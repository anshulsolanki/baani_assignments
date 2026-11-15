#include "worker.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <unistd.h>

static void append_tokens(char *buf, char **args, int *argc_out, int max_args) {
    char *p = buf;
    while (*p != '\0' && *argc_out < max_args - 1) {
        while (*p == ' ' || *p == '\t') {
            p++;
        }
        if (*p == '\0') {
            break;
        }
        if (*p == '"' || *p == '\'') {
            char q = *p++;
            args[(*argc_out)++] = p;
            while (*p != '\0' && *p != q) {
                p++;
            }
            if (*p == q) {
                *p++ = '\0';
            }
        } else {
            args[(*argc_out)++] = p;
            while (*p != '\0' && *p != ' ' && *p != '\t') {
                p++;
            }
            if (*p != '\0') {
                *p++ = '\0';
            }
        }
    }
    args[*argc_out] = NULL;
}

/*
 * Copy src to dst with explicit file permissions.
 */
static int copy_file_With_mode(const char *src, const char *dst, mode_t mode) {
    FILE *in = fopen(src, "rb");
    if (in == NULL) {
        return -1;
    }
    int out_fd = open(dst, O_CREAT | O_TRUNC | O_WRONLY, mode);
    if (out_fd < 0) {
        fclose(in);
        return -1;
    }

    char buf[8192];
    size_t n = 0;
    while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
        if (write(out_fd, buf, n) < 0) {
            close(out_fd);
            fclose(in);
            return -1;
        }
    }

    fchmod(out_fd, mode);
    close(out_fd);
    fclose(in);
    return 0;
}

void cleanup_job_directory(const char *job_dir) {
    if (job_dir == NULL || strncmp(job_dir, "/tmp/osn_job_", 13) != 0) {
        return;
    }

    char ckpt_dir[MAX_PATH_STR];
    snprintf(ckpt_dir, sizeof(ckpt_dir), "%s/checkpoint", job_dir);

    DIR *cd = opendir(ckpt_dir);
    if (cd != NULL) {
        struct dirent *de;
        while ((de = readdir(cd)) != NULL) {
            if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0) {
                continue;
            }
            char fpath[MAX_PATH_STR * 2];
            snprintf(fpath, sizeof(fpath), "%s/%s", ckpt_dir, de->d_name);
            unlink(fpath);
        }
        closedir(cd);
        rmdir(ckpt_dir);
    }

    DIR *d = opendir(job_dir);
    if (d != NULL) {
        struct dirent *de;
        while ((de = readdir(d)) != NULL) {
            if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0) {
                continue;
            }
            char fpath[MAX_PATH_STR * 2];
            snprintf(fpath, sizeof(fpath), "%s/%s", job_dir, de->d_name);
            unlink(fpath);
        }
        closedir(d);
    }
    rmdir(job_dir);
}

void kill_all_active_jobs(struct worker_ctx *wctx) {
    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        struct active_job *aj = &wctx->jobs[i];
        if (!aj->used) {
            continue;
        }
        if (aj->pid > 0) {
            kill(-aj->pid, SIGKILL);
            kill(aj->pid, SIGKILL);
            int status = 0;
            waitpid(aj->pid, &status, 0);
        }
        if (aj->log_read_fd >= 0) {
            close(aj->log_read_fd);
        }
        cleanup_job_directory(aj->job_dir);
        aj->used = 0;
    }
    wctx->free_cores = wctx->total_cores;
    wctx->free_ram_mb = wctx->total_ram_mb;
    wctx->free_gpu = wctx->total_gpu;
}

/*
 * Section 5A & 5B: Isolate and limit a job in /tmp/osn_job_<JobID> and launch via fork() + execvp().
 */
int launch_job_process(struct worker_ctx *wctx, const struct msg_assign_job *assign) {
    struct active_job *slot = NULL;
    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        if (!wctx->jobs[i].used) {
            slot = &wctx->jobs[i];
            break;
        }
    }
    if (slot == NULL) {
        return -1;
    }

    char cached_path[MAX_PATH_STR] = "";
    if (assign->exec_transferred) {
        if (cache_lookup_by_hash(wctx, assign->sha1_hash, cached_path, sizeof(cached_path)) < 0) {
            /* Cached file disappeared from disk -> report CACHE_MISS (Section 13) */
            log_line("[WORKER %d] CACHE_MISS for Job %d (sha1 %.8s...)",
                     wctx->worker_id, assign->job_id, assign->sha1_hash);
            struct msg_cache_miss cm;
            memset(&cm, 0, sizeof(cm));
            cm.job_id = assign->job_id;
            snprintf(cm.sha1_hash, sizeof(cm.sha1_hash), "%s", assign->sha1_hash);
            send_packet(wctx->sock_fd, MSG_WORKER_CACHE_MISS, &cm, sizeof(cm));
            return 0;
        }
        /* Mark cached binary as used now for LRU eviction (Section 13) */
        utimes(cached_path, NULL);
    }

    memset(slot, 0, sizeof(*slot));
    slot->job_id = assign->job_id;
    slot->cores = assign->cores;
    slot->ram_mb = assign->ram_mb;
    slot->gpu = assign->gpu;
    slot->time_limit_sec = assign->time_limit_sec;
    snprintf(slot->sha1_hash, sizeof(slot->sha1_hash), "%s", assign->sha1_hash);

    snprintf(slot->job_dir, sizeof(slot->job_dir), "/tmp/osn_job_%d", assign->job_id);
    snprintf(slot->ckpt_dir, sizeof(slot->ckpt_dir), "%s/checkpoint", slot->job_dir);

    cleanup_job_directory(slot->job_dir);
    mkdir(slot->job_dir, 0755);
    mkdir(slot->ckpt_dir, 0755);

    /* Restore saved checkpoint if provided for this job (Section 14) */
    if (assign->has_checkpoint && wctx->pending_ckpt.valid &&
        wctx->pending_ckpt.job_id == assign->job_id &&
        wctx->pending_ckpt.data != NULL && wctx->pending_ckpt.len > 0) {
        char state_path[MAX_PATH_STR * 2];
        snprintf(state_path, sizeof(state_path), "%s/state", slot->ckpt_dir);
        FILE *cf = fopen(state_path, "wb");
        if (cf != NULL) {
            fwrite(wctx->pending_ckpt.data, 1, (size_t)wctx->pending_ckpt.len, cf);
            fclose(cf);
        }
        struct stat st;
        if (stat(state_path, &st) == 0) {
#ifdef __APPLE__
            slot->last_ckpt_sig = ((uint64_t)st.st_mtimespec.tv_sec << 32) ^
                                  (uint64_t)st.st_mtimespec.tv_nsec ^
                                  (uint64_t)st.st_size ^ (uint64_t)st.st_ino;
#else
            slot->last_ckpt_sig = ((uint64_t)st.st_mtim.tv_sec << 32) ^
                                  (uint64_t)st.st_mtim.tv_nsec ^
                                  (uint64_t)st.st_size ^ (uint64_t)st.st_ino;
#endif
        }
    }
    if (wctx->pending_ckpt.valid && wctx->pending_ckpt.job_id == assign->job_id) {
        free(wctx->pending_ckpt.data);
        wctx->pending_ckpt.data = NULL;
        wctx->pending_ckpt.len = 0;
        wctx->pending_ckpt.valid = 0;
    }

    char local_exec_path[MAX_PATH_STR * 2] = "";
    if (assign->exec_transferred) {
        snprintf(local_exec_path, sizeof(local_exec_path), "%s/%s",
                 slot->job_dir, assign->exec_name[0] ? assign->exec_name : "job_exec");
        copy_file_With_mode(cached_path, local_exec_path, 0755);
    }

    char log_path[MAX_PATH_STR * 2];
    snprintf(log_path, sizeof(log_path), "%s/output.log", slot->job_dir);
    int out_fd = open(log_path, O_CREAT | O_TRUNC | O_WRONLY, 0644);
    if (out_fd < 0) {
        cleanup_job_directory(slot->job_dir);
        return -1;
    }

    uid_t nobody_uid = 0;
    gid_t nobody_gid = 0;
    int drop_privs = 0;
    if (wctx->is_root) {
        struct passwd *pw = getpwnam("nobody");
        if (pw != NULL) {
            nobody_uid = pw->pw_uid;
            nobody_gid = pw->pw_gid;
            drop_privs = 1;
            chown(slot->job_dir, nobody_uid, nobody_gid);
            chown(slot->ckpt_dir, nobody_uid, nobody_gid);
            chown(log_path, nobody_uid, nobody_gid);
            if (local_exec_path[0] != '\0') {
                chown(local_exec_path, nobody_uid, nobody_gid);
            }
            char state_path[MAX_PATH_STR * 2];
            snprintf(state_path, sizeof(state_path), "%s/state", slot->ckpt_dir);
            chown(state_path, nobody_uid, nobody_gid);
        }
    }

    slot->log_read_fd = open(log_path, O_RDONLY | O_NONBLOCK);

    log_line("[WORKER %d] Job %d ASSIGNED, forking...", wctx->worker_id, assign->job_id);

    pid_t pid = fork();
    if (pid < 0) {
        close(out_fd);
        if (slot->log_read_fd >= 0) {
            close(slot->log_read_fd);
        }
        cleanup_job_directory(slot->job_dir);
        return -1;
    }

    if (pid == 0) {
        /* Child process: setup sandbox, limits, output redirection, and execvp */
        setpgid(0, 0);
        signal(SIGINT, SIG_DFL);
        signal(SIGTERM, SIG_DFL);
        signal(SIGPIPE, SIG_DFL);

        /* 1. Give it its own working directory */
        if (chdir(slot->job_dir) != 0) {
            _exit(126);
        }

        setenv("OSN_CHECKPOINT_DIR", slot->ckpt_dir, 1);

        /* Redirect stdout and stderr to output.log (Section 5B) */
        dup2(out_fd, STDOUT_FILENO);
        dup2(out_fd, STDERR_FILENO);

        for (int fd = 3; fd < 1024; fd++) {
            close(fd);
        }

        /* 2. Drop privileges to 'nobody' if started with sudo (setgid first, then setuid) */
        if (wctx->is_root) {
            if (!drop_privs) {
                _exit(126);
            }
            setgroups(0, NULL);
            if (setgid(nobody_gid) != 0 || setuid(nobody_uid) != 0) {
                _exit(126);
            }
        }

        /* 3. Limit CPU time */
        struct rlimit rl_cpu;
        rl_cpu.rlim_cur = (rlim_t)assign->time_limit_sec;
        rl_cpu.rlim_max = (rlim_t)assign->time_limit_sec;
        setrlimit(RLIMIT_CPU, &rl_cpu);

        /* 4. Limit virtual memory (RLIMIT_AS) */
        struct rlimit rl_mem;
        rl_mem.rlim_cur = (rlim_t)assign->ram_mb * 1024ULL * 1024ULL;
        rl_mem.rlim_max = (rlim_t)assign->ram_mb * 1024ULL * 1024ULL;
        setrlimit(RLIMIT_AS, &rl_mem);

        /* Limit output file size */
        struct rlimit rl_fsz;
        rl_fsz.rlim_cur = RLIMIT_FSIZE_BYTES;
        rl_fsz.rlim_max = RLIMIT_FSIZE_BYTES;
        setrlimit(RLIMIT_FSIZE, &rl_fsz);

        /* 5. Guard against fork bombs (RLIMIT_NPROC) */
        struct rlimit rl_nproc;
        if (wctx->is_root) {
            rl_nproc.rlim_cur = RLIMIT_NPROC_DEFAULT;
            rl_nproc.rlim_max = RLIMIT_NPROC_DEFAULT;
            setrlimit(RLIMIT_NPROC, &rl_nproc);
        }

        char *args[64];
        int argc_job = 0;
        char prog[MAX_NAME_STR + 4];
        char cmd_copy[MAX_PATH_STR];
        char args_copy[MAX_PATH_STR];

        if (assign->exec_transferred) {
            snprintf(prog, sizeof(prog), "./%s",
                     assign->exec_name[0] ? assign->exec_name : "job_exec");
            args[argc_job++] = prog;
            args[argc_job] = NULL;
        } else {
            snprintf(cmd_copy, sizeof(cmd_copy), "%s", assign->binary_path);
            append_tokens(cmd_copy, args, &argc_job, 64);
        }

        if (assign->job_args[0] != '\0') {
            snprintf(args_copy, sizeof(args_copy), "%s", assign->job_args);
            append_tokens(args_copy, args, &argc_job, 64);
        }

        if (argc_job > 0) {
            execvp(args[0], args);
        }

        _exit(127);
    }

    close(out_fd);
    slot->used = 1;
    slot->pid = pid;
    slot->start_time = time(NULL);
    slot->kill_reason = KILL_NONE;

    wctx->free_cores -= assign->cores;
    wctx->free_ram_mb -= assign->ram_mb;
    wctx->free_gpu -= assign->gpu;

    return 0;
}
