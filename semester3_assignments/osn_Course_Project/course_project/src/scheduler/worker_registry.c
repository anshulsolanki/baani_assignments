#include "scheduler.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct worker_node *find_worker_by_fd(struct scheduler_ctx *ctx, int fd) {
    for (int i = 0; i < MAX_WORKERS; i++) {
        if (ctx->workers[i].used && ctx->workers[i].sock_fd == fd) {
            return &ctx->workers[i];
        }
    }
    return NULL;
}

struct worker_node *find_worker_by_id(struct scheduler_ctx *ctx, int worker_id) {
    for (int i = 0; i < MAX_WORKERS; i++) {
        if (ctx->workers[i].used && ctx->workers[i].id == worker_id) {
            return &ctx->workers[i];
        }
    }
    return NULL;
}

int worker_has_hash(const struct worker_node *w, const char *hash) {
    if (w == NULL || hash == NULL || hash[0] == '\0') {
        return 0;
    }
    for (int i = 0; i < w->num_cached; i++) {
        if (strcmp(w->cached_hashes[i], hash) == 0) {
            return 1;
        }
    }
    return 0;
}

void worker_add_hash(struct worker_node *w, const char *hash) {
    if (w == NULL || hash == NULL || hash[0] == '\0') {
        return;
    }
    if (worker_has_hash(w, hash)) {
        return;
    }
    if (w->num_cached < MAX_WORKER_CACHE) {
        snprintf(w->cached_hashes[w->num_cached], SHA1_HEX_LEN, "%s", hash);
        w->num_cached++;
    }
}

void worker_remove_hash(struct worker_node *w, const char *hash) {
    if (w == NULL || hash == NULL) {
        return;
    }
    for (int i = 0; i < w->num_cached; i++) {
        if (strcmp(w->cached_hashes[i], hash) == 0) {
            for (int k = i; k + 1 < w->num_cached; k++) {
                memcpy(w->cached_hashes[k], w->cached_hashes[k + 1], SHA1_HEX_LEN);
            }
            w->num_cached--;
            return;
        }
    }
}

static void release_preempt_holds_for(struct scheduler_ctx *ctx, int prio1_job_id) {
    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        if (ctx->jobs[i].used && ctx->jobs[i].hold_for_job_id == prio1_job_id) {
            ctx->jobs[i].hold_for_job_id = 0;
        }
    }
}

static void mark_worker_dead_and_rescue(struct scheduler_ctx *ctx,
                                        struct worker_node *w,
                                        const char *reason) {
    if (w->sock_fd >= 0) {
        close(w->sock_fd);
        w->sock_fd = -1;
    }
    w->state = WORKER_DEAD;
    w->free_cores = 0;
    w->free_ram_mb = 0;
    w->free_gpu = 0;
    w->running_jobs = 0;

    log_line("[SCHEDULER] Worker %d -> DEAD (%s)", w->id, reason);

    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        struct job_entry *j = &ctx->jobs[i];
        if (!j->used || j->state != JOB_RUNNING || j->worker_id != w->id) {
            continue;
        }

        notify_user_event(ctx, j->user, "[Event] WARNING: Worker %d DEAD.", w->id);

        j->state = JOB_LOST;
        j->preempt_pending = 0;
        j->migrate_pending = 0;

        if (j->attempts >= MAX_RETRY_ATTEMPTS) {
            j->state = JOB_FAILED_PERMANENT;
            snprintf(j->diagnosis, sizeof(j->diagnosis),
                     "Exceeded retry limit (%d attempts) after Worker %d died.",
                     MAX_RETRY_ATTEMPTS, w->id);
            log_line("[SCHEDULER] Job %d RUNNING -> LOST -> FAILED_PERMANENT", j->id);
            notify_user_event(ctx, j->user,
                              "[Event] Job %d FAILED_PERMANENT (exceeded %d attempts).",
                              j->id, MAX_RETRY_ATTEMPTS);
            notify_job_followers_eof(ctx, j->id);
            release_preempt_holds_for(ctx, j->id);
        } else {
            j->state = JOB_QUEUED;
            j->worker_id = 0;
            j->queued_since = time(NULL);
            log_line("[SCHEDULER] Job %d RUNNING -> LOST -> QUEUED", j->id);
            notify_user_event(ctx, j->user,
                              "[Event] Job %d (attempt %d) moved back to QUEUED.",
                              j->id, j->attempts);
        }
    }

    check_job_dependencies(ctx);
    schedule_jobs(ctx);
}

void handle_worker_disconnect(struct scheduler_ctx *ctx, struct worker_node *w) {
    (void)ctx;
    if (w->sock_fd >= 0) {
        close(w->sock_fd);
        w->sock_fd = -1;
    }

    /* Section 9: A drained worker with 0 active jobs exits gracefully */
    if (w->state == WORKER_DRAINING && w->running_jobs == 0) {
        log_line("[SCHEDULER] Worker %d drain complete and disconnected.", w->id);
        w->used = 0;
        return;
    }

    /*
     * Leave w->state as ALIVE/SUSPECTED with sock_fd = -1 so check_worker_heartbeats
     * transitions ALIVE -> SUSPECTED (~2s) -> DEAD (~6s) via the 4C state machine.
     */
}

void check_worker_heartbeats(struct scheduler_ctx *ctx) {
    time_t now = time(NULL);

    for (int i = 0; i < MAX_WORKERS; i++) {
        struct worker_node *w = &ctx->workers[i];
        if (!w->used || w->state == WORKER_DEAD) {
            continue;
        }

        long silence = (long)(now - w->last_heartbeat);
        if (silence >= DEAD_THRESHOLD_SEC) {
            mark_worker_dead_and_rescue(ctx, w, "3 missed heartbeats");
        } else if (w->state == WORKER_ALIVE && silence >= SUSPECT_THRESHOLD_SEC) {
            w->state = WORKER_SUSPECTED;
            log_line("[SCHEDULER] Worker %d ALIVE -> SUSPECTED (missed heartbeat)", w->id);
            for (int k = 0; k < MAX_JOBS_TOTAL; k++) {
                struct job_entry *j = &ctx->jobs[k];
                if (j->used && j->state == JOB_RUNNING && j->worker_id == w->id) {
                    notify_user_event(ctx, j->user,
                                      "[Event] WARNING: Worker %d SUSPECTED (missed heartbeat).",
                                      w->id);
                }
            }
        }
    }
}

void handle_worker_message(struct scheduler_ctx *ctx, struct worker_node *w,
                           const struct packet_header *hdr) {
    switch (hdr->type) {
        case MSG_WORKER_CACHE_LIST: {
            struct msg_worker_cache_list cl;
            if (hdr->length != sizeof(cl) || recv_all(w->sock_fd, &cl, sizeof(cl)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            w->num_cached = 0;
            for (int i = 0; i < cl.count && i < MAX_WORKER_CACHE; i++) {
                worker_add_hash(w, cl.hashes[i]);
            }
            break;
        }

        case MSG_WORKER_HEARTBEAT: {
            struct msg_worker_heartbeat hb;
            if (hdr->length != sizeof(hb) || recv_all(w->sock_fd, &hb, sizeof(hb)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            w->last_heartbeat = time(NULL);
            w->cpu_load_pct = hb.cpu_load_pct;
            if (w->state == WORKER_SUSPECTED) {
                w->state = WORKER_ALIVE;
                log_line("[SCHEDULER] Worker %d SUSPECTED -> ALIVE (heartbeat received)", w->id);
            }
            for (int i = 0; i < hb.active_jobs && i < MAX_WORKER_JOBS; i++) {
                struct job_entry *j = find_job_by_id(ctx, hb.jobs[i].job_id);
                if (j != NULL && j->state == JOB_RUNNING) {
                    j->current_ram_mb = hb.jobs[i].current_ram_mb;
                    if (hb.jobs[i].peak_ram_mb > j->peak_ram_mb) {
                        j->peak_ram_mb = hb.jobs[i].peak_ram_mb;
                    }
                    j->page_faults = hb.jobs[i].page_faults;
                    j->cpu_time_sec = hb.jobs[i].cpu_time_sec;
                }
            }
            schedule_jobs(ctx);
            break;
        }

        case MSG_WORKER_DRAIN: {
            if (hdr->length > 0) {
                char dummy[64];
                recv_all(w->sock_fd, dummy, (size_t)hdr->length);
            }
            if (w->state != WORKER_DRAINING) {
                w->state = WORKER_DRAINING;
                log_line("[SCHEDULER] Worker %d -> DRAINING", w->id);
            }
            break;
        }

        case MSG_WORKER_CACHE_MISS: {
            struct msg_cache_miss cm;
            if (hdr->length != sizeof(cm) || recv_all(w->sock_fd, &cm, sizeof(cm)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            log_line("[SCHEDULER] Worker %d reported CACHE_MISS for Job %d (sha1 %.8s...); resending binary",
                     w->id, cm.job_id, cm.sha1_hash);
            worker_remove_hash(w, cm.sha1_hash);
            struct job_entry *j = find_job_by_id(ctx, cm.job_id);
            if (j != NULL && j->state == JOB_RUNNING && j->worker_id == w->id) {
                if (j->attempts > 0) {
                    j->attempts--; /* Cache miss does not count as a failed attempt */
                }
                w->free_cores += j->cores;
                w->free_ram_mb += j->ram_mb;
                w->free_gpu += j->gpu;
                if (w->running_jobs > 0) {
                    w->running_jobs--;
                }
                dispatch_job_to_worker(ctx, j, w);
            }
            break;
        }

        case MSG_WORKER_JOB_OUTPUT: {
            if (hdr->length < (int32_t)sizeof(struct msg_job_output_hdr)) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            struct msg_job_output_hdr oh;
            if (recv_all(w->sock_fd, &oh, sizeof(oh)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            int32_t text_len = hdr->length - (int32_t)sizeof(oh);
            char *buf = malloc((size_t)text_len + 1);
            if (buf == NULL) {
                return;
            }
            if (text_len > 0 && recv_all(w->sock_fd, buf, (size_t)text_len) < 0) {
                free(buf);
                handle_worker_disconnect(ctx, w);
                return;
            }
            buf[text_len] = '\0';
            struct job_entry *j = find_job_by_id(ctx, oh.job_id);
            if (j != NULL) {
                append_job_log(ctx, j, buf, text_len);
            }
            free(buf);
            break;
        }

        case MSG_WORKER_CHECKPOINT: {
            if (hdr->length < (int32_t)sizeof(struct msg_ckpt_header)) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            struct msg_ckpt_header ch;
            if (recv_all(w->sock_fd, &ch, sizeof(ch)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            int32_t dlen = hdr->length - (int32_t)sizeof(ch);
            uint8_t *data = malloc((size_t)(dlen > 0 ? dlen : 1));
            if (data == NULL) {
                return;
            }
            if (dlen > 0 && recv_all(w->sock_fd, data, (size_t)dlen) < 0) {
                free(data);
                handle_worker_disconnect(ctx, w);
                return;
            }
            struct job_entry *j = find_job_by_id(ctx, ch.job_id);
            if (j != NULL) {
                free(j->ckpt_data);
                j->ckpt_data = data;
                j->ckpt_len = dlen;
                j->ckpt_count++;
                j->ckpt_time = time(NULL);
                log_line("[SCHEDULER] Job %d saved checkpoint #%d (%d bytes)",
                         j->id, j->ckpt_count, (int)dlen);
            } else {
                free(data);
            }
            break;
        }

        case MSG_WORKER_JOB_DONE: {
            struct msg_job_done done;
            if (hdr->length != sizeof(done) || recv_all(w->sock_fd, &done, sizeof(done)) < 0) {
                handle_worker_disconnect(ctx, w);
                return;
            }
            struct job_entry *j = find_job_by_id(ctx, done.job_id);
            if (j == NULL || j->state != JOB_RUNNING || j->worker_id != w->id) {
                break;
            }

            w->free_cores += j->cores;
            w->free_ram_mb += j->ram_mb;
            w->free_gpu += j->gpu;
            if (w->running_jobs > 0) {
                w->running_jobs--;
            }

            j->current_ram_mb = 0;
            if (done.peak_ram_mb > j->peak_ram_mb) {
                j->peak_ram_mb = done.peak_ram_mb;
            }
            j->page_faults = done.page_faults;
            j->cpu_time_sec = done.cpu_time_sec;

            if (done.outcome == OUTCOME_COMPLETED && !j->preempt_pending && !j->migrate_pending) {
                j->state = JOB_COMPLETED;
                snprintf(j->diagnosis, sizeof(j->diagnosis), "Completed (exit code 0)");
                log_line("[SCHEDULER] Job %d RUNNING -> COMPLETED on Worker %d", j->id, w->id);
                notify_user_event(ctx, j->user, "[Event] Job %d COMPLETED successfully.", j->id);
                notify_job_followers_eof(ctx, j->id);
            } else if (done.outcome == OUTCOME_PREEMPTED || j->preempt_pending) {
                j->state = JOB_QUEUED;
                j->worker_id = 0;
                j->queued_since = time(NULL);
                j->preempt_pending = 0;
                if (j->attempts > 0) {
                    j->attempts--;
                }
                log_line("[SCHEDULER] Job %d RUNNING -> QUEUED (preempted on Worker %d)", j->id, w->id);
                notify_user_event(ctx, j->user,
                                  "[Event] Job %d preempted on Worker %d and moved back to QUEUED.",
                                  j->id, w->id);
            } else if (done.outcome == OUTCOME_MIGRATED || j->migrate_pending) {
                j->state = JOB_QUEUED;
                j->queued_since = time(NULL);
                j->migrate_pending = 0;
                j->avoid_worker_id = w->id;
                j->worker_id = 0;
                if (j->attempts > 0) {
                    j->attempts--;
                }
                log_line("[SCHEDULER] Job %d RUNNING -> QUEUED (migrated off Worker %d, checkpoint #%d)",
                         j->id, w->id, j->ckpt_count);
                if (j->ckpt_count > 0) {
                    notify_user_event(ctx, j->user,
                                      "[Event] Job %d stopped on Worker %d and moved back to QUEUED; it resumes from checkpoint #%d.",
                                      j->id, w->id, j->ckpt_count);
                } else {
                    notify_user_event(ctx, j->user,
                                      "[Event] Job %d stopped on Worker %d and moved back to QUEUED.",
                                      j->id, w->id);
                }
            } else if (done.outcome == OUTCOME_CANCELLED) {
                j->state = JOB_CANCELLED;
                snprintf(j->diagnosis, sizeof(j->diagnosis), "%s", done.diagnosis);
                notify_job_followers_eof(ctx, j->id);
                release_preempt_holds_for(ctx, j->id);
            } else {
                j->state = JOB_FAILED;
                snprintf(j->diagnosis, sizeof(j->diagnosis), "%s", done.diagnosis);
                log_line("[SCHEDULER] Job %d RUNNING -> FAILED on Worker %d. Reason: %s",
                         j->id, w->id, j->diagnosis);
                notify_user_event(ctx, j->user,
                                  "[Event] Job %d FAILED. Reason: %s",
                                  j->id, j->diagnosis);
                notify_job_followers_eof(ctx, j->id);
                release_preempt_holds_for(ctx, j->id);
            }

            check_job_dependencies(ctx);
            schedule_jobs(ctx);
            break;
        }

        default: {
            if (hdr->length > 0) {
                char *skip = malloc((size_t)hdr->length);
                if (skip != NULL) {
                    recv_all(w->sock_fd, skip, (size_t)hdr->length);
                    free(skip);
                }
            }
            break;
        }
    }
}
