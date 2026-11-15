#include "worker.h"
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

void init_worker_cache(struct worker_ctx *wctx) {
    const char *env_dir = getenv("OSN_CACHE_DIR");
    if (env_dir != NULL && env_dir[0] != '\0') {
        snprintf(wctx->cache_dir, sizeof(wctx->cache_dir), "%s", env_dir);
    } else {
        snprintf(wctx->cache_dir, sizeof(wctx->cache_dir), "cache");
    }

    mkdir(wctx->cache_dir, 0755);

    double mb = (double)DEFAULT_CACHE_SIZE_MB;
    const char *env_mb = getenv("OSN_CACHE_SIZE_MB");
    if (env_mb != NULL && env_mb[0] != '\0') {
        double parsed = atof(env_mb);
        if (parsed > 0.0) {
            mb = parsed;
        }
    }
    wctx->cache_limit_bytes = (int64_t)(mb * 1024.0 * 1024.0);
}

/*
 * Extract the 40-char SHA-1 suffix from a cached filename "<name>-<40hex>".
 */
static int extract_hash_from_filename(const char *fname, char out_hash[SHA1_HEX_LEN]) {
    const char *dash = strrchr(fname, '-');
    if (dash == NULL || strlen(dash + 1) != 40) {
        return -1;
    }
    snprintf(out_hash, SHA1_HEX_LEN, "%s", dash + 1);
    return 0;
}

int cache_lookup_by_hash(const struct worker_ctx *wctx, const char *hash,
                         char *out_path, size_t out_len) {
    if (hash == NULL || hash[0] == '\0') {
        return -1;
    }

    DIR *d = opendir(wctx->cache_dir);
    if (d == NULL) {
        return -1;
    }

    struct dirent *de;
    while ((de = readdir(d)) != NULL) {
        if (de->d_name[0] == '.') {
            continue;
        }
        char file_hash[SHA1_HEX_LEN];
        if (extract_hash_from_filename(de->d_name, file_hash) == 0 &&
            strcmp(file_hash, hash) == 0) {
            snprintf(out_path, out_len, "%s/%s", wctx->cache_dir, de->d_name);
            closedir(d);
            return 0;
        }
    }

    closedir(d);
    return -1;
}

int cache_hash_in_use(const struct worker_ctx *wctx, const char *hash) {
    if (hash == NULL || hash[0] == '\0') {
        return 0;
    }
    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        if (wctx->jobs[i].used && strcmp(wctx->jobs[i].sha1_hash, hash) == 0) {
            return 1;
        }
    }
    return 0;
}

/*
 * Section 13: Evict Least Recently Used (oldest mtime) cached programs until total size
 * fits within OSN_CACHE_SIZE_MB. Never evict `keep_hash` (just stored) or any binary
 * currently used by a running job.
 */
void cache_evict_lru(struct worker_ctx *wctx, const char *keep_hash) {
    while (1) {
        DIR *d = opendir(wctx->cache_dir);
        if (d == NULL) {
            return;
        }

        int64_t total_bytes = 0;
        char victim_path[MAX_PATH_STR * 2] = "";
        char victim_hash[SHA1_HEX_LEN] = "";
        int64_t victim_size = 0;
        double oldest_ts = 0.0;
        int has_victim = 0;

        struct dirent *de;
        while ((de = readdir(d)) != NULL) {
            if (de->d_name[0] == '.') {
                continue;
            }
            char fhash[SHA1_HEX_LEN];
            if (extract_hash_from_filename(de->d_name, fhash) < 0) {
                continue;
            }

            char full_path[MAX_PATH_STR * 2];
            snprintf(full_path, sizeof(full_path), "%s/%s", wctx->cache_dir, de->d_name);

            struct stat st;
            if (stat(full_path, &st) != 0) {
                continue;
            }
            total_bytes += (int64_t)st.st_size;

            if (keep_hash != NULL && strcmp(fhash, keep_hash) == 0) {
                continue;
            }
            if (cache_hash_in_use(wctx, fhash)) {
                continue;
            }

#ifdef __APPLE__
            double ts = (double)st.st_mtimespec.tv_sec +
                        (double)st.st_mtimespec.tv_nsec / 1e9;
#else
            double ts = (double)st.st_mtim.tv_sec +
                        (double)st.st_mtim.tv_nsec / 1e9;
#endif
            if (!has_victim || ts < oldest_ts) {
                has_victim = 1;
                oldest_ts = ts;
                snprintf(victim_path, sizeof(victim_path), "%s", full_path);
                snprintf(victim_hash, sizeof(victim_hash), "%s", fhash);
                victim_size = (int64_t)st.st_size;
            }
        }
        closedir(d);

        if (total_bytes <= wctx->cache_limit_bytes || !has_victim) {
            break;
        }

        unlink(victim_path);
        log_line("[WORKER %d] LRU cache evicted %.8s... (%lld bytes)",
                 wctx->worker_id, victim_hash, (long long)victim_size);
    }
}

void send_worker_cache_list(struct worker_ctx *wctx) {
    struct msg_worker_cache_list cl;
    memset(&cl, 0, sizeof(cl));

    DIR *d = opendir(wctx->cache_dir);
    if (d != NULL) {
        struct dirent *de;
        while ((de = readdir(d)) != NULL && cl.count < MAX_WORKER_CACHE) {
            if (de->d_name[0] == '.') {
                continue;
            }
            char fhash[SHA1_HEX_LEN];
            if (extract_hash_from_filename(de->d_name, fhash) == 0) {
                snprintf(cl.hashes[cl.count], SHA1_HEX_LEN, "%s", fhash);
                cl.count++;
            }
        }
        closedir(d);
    }

    send_packet(wctx->sock_fd, MSG_WORKER_CACHE_LIST, &cl, sizeof(cl));
}

void handle_binary_chunk(struct worker_ctx *wctx, const struct packet_header *hdr) {
    if (hdr->length < (int32_t)sizeof(struct msg_binary_meta)) {
        return;
    }

    struct msg_binary_meta meta;
    if (recv_all(wctx->sock_fd, &meta, sizeof(meta)) < 0) {
        return;
    }

    int32_t data_len = hdr->length - (int32_t)sizeof(meta);
    uint8_t *buf = malloc((size_t)(data_len > 0 ? data_len : 1));
    if (buf == NULL) {
        return;
    }
    if (data_len > 0 && recv_all(wctx->sock_fd, buf, (size_t)data_len) < 0) {
        free(buf);
        return;
    }

    if (meta.offset == 0) {
        if (wctx->bin_rx.fp != NULL) {
            fclose(wctx->bin_rx.fp);
            wctx->bin_rx.fp = NULL;
        }
        wctx->bin_rx.active = 1;
        wctx->bin_rx.job_id = meta.job_id;
        snprintf(wctx->bin_rx.exec_name, sizeof(wctx->bin_rx.exec_name), "%s", meta.exec_name);
        snprintf(wctx->bin_rx.sha1_hash, sizeof(wctx->bin_rx.sha1_hash), "%s", meta.sha1_hash);
        snprintf(wctx->bin_rx.tmp_path, sizeof(wctx->bin_rx.tmp_path),
                 "%s/.tmp_%d_%s", wctx->cache_dir, (int)getpid(), meta.sha1_hash);
        wctx->bin_rx.fp = fopen(wctx->bin_rx.tmp_path, "wb");
        wctx->bin_rx.total_size = meta.total_size;
        wctx->bin_rx.received = 0;
    }

    if (wctx->bin_rx.active && wctx->bin_rx.fp != NULL && data_len > 0) {
        fwrite(buf, 1, (size_t)data_len, wctx->bin_rx.fp);
        wctx->bin_rx.received += data_len;
    }
    free(buf);

    if (wctx->bin_rx.active && wctx->bin_rx.received >= wctx->bin_rx.total_size) {
        if (wctx->bin_rx.fp != NULL) {
            fclose(wctx->bin_rx.fp);
            wctx->bin_rx.fp = NULL;
        }

        char verify_hash[SHA1_HEX_LEN];
        int32_t verify_sz = 0;
        if (sha1_file(wctx->bin_rx.tmp_path, verify_hash, &verify_sz) == 0 &&
            strcmp(verify_hash, wctx->bin_rx.sha1_hash) == 0) {
            char final_path[MAX_PATH_STR * 2];
            snprintf(final_path, sizeof(final_path), "%s/%s-%s",
                     wctx->cache_dir, wctx->bin_rx.exec_name, wctx->bin_rx.sha1_hash);
            chmod(wctx->bin_rx.tmp_path, 0755);
            rename(wctx->bin_rx.tmp_path, final_path);

            cache_evict_lru(wctx, wctx->bin_rx.sha1_hash);
            send_worker_cache_list(wctx);
        } else {
            unlink(wctx->bin_rx.tmp_path);
        }
        wctx->bin_rx.active = 0;
    }
}

void handle_checkpoint_data(struct worker_ctx *wctx, const struct packet_header *hdr) {
    if (hdr->length < (int32_t)sizeof(struct msg_ckpt_header)) {
        return;
    }

    struct msg_ckpt_header ch;
    if (recv_all(wctx->sock_fd, &ch, sizeof(ch)) < 0) {
        return;
    }

    int32_t dlen = hdr->length - (int32_t)sizeof(ch);
    uint8_t *data = malloc((size_t)(dlen > 0 ? dlen : 1));
    if (data == NULL) {
        return;
    }
    if (dlen > 0 && recv_all(wctx->sock_fd, data, (size_t)dlen) < 0) {
        free(data);
        return;
    }

    free(wctx->pending_ckpt.data);
    wctx->pending_ckpt.valid = 1;
    wctx->pending_ckpt.job_id = ch.job_id;
    wctx->pending_ckpt.data = data;
    wctx->pending_ckpt.len = dlen;
}

/*
 * Section 14: Poll $OSN_CHECKPOINT_DIR/state every ~500ms using stat() timestamps.
 * When changed, read the file and send MSG_WORKER_CHECKPOINT to the scheduler.
 */
void check_job_checkpoint_file(struct worker_ctx *wctx, struct active_job *aj) {
    char state_path[MAX_PATH_STR * 2];
    snprintf(state_path, sizeof(state_path), "%s/state", aj->ckpt_dir);

    struct stat st;
    if (stat(state_path, &st) != 0 || st.st_size <= 0) {
        return;
    }

#ifdef __APPLE__
    uint64_t sig = ((uint64_t)st.st_mtimespec.tv_sec << 32) ^
                   (uint64_t)st.st_mtimespec.tv_nsec ^
                   (uint64_t)st.st_size ^ (uint64_t)st.st_ino;
#else
    uint64_t sig = ((uint64_t)st.st_mtim.tv_sec << 32) ^
                   (uint64_t)st.st_mtim.tv_nsec ^
                   (uint64_t)st.st_size ^ (uint64_t)st.st_ino;
#endif

    if (sig == aj->last_ckpt_sig) {
        return;
    }

    FILE *fp = fopen(state_path, "rb");
    if (fp == NULL) {
        return;
    }

    int32_t dlen = (int32_t)st.st_size;
    int32_t pkt_len = (int32_t)sizeof(struct msg_ckpt_header) + dlen;
    uint8_t *buf = malloc((size_t)pkt_len);
    if (buf == NULL) {
        fclose(fp);
        return;
    }

    struct msg_ckpt_header ch;
    ch.job_id = aj->job_id;
    ch.data_len = dlen;
    memcpy(buf, &ch, sizeof(ch));

    size_t n = fread(buf + sizeof(ch), 1, (size_t)dlen, fp);
    fclose(fp);

    (void)n;
    free(buf);
}
