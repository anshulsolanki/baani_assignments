#include "scheduler.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct job_entry *find_job_by_id(struct scheduler_ctx *ctx, int job_id) {
    if (job_id <= 0 || job_id > MAX_JOBS_TOTAL) {
        return NULL;
    }
    struct job_entry *j = &ctx->jobs[job_id - 1];
    return j->used ? j : NULL;
}

int count_queued_jobs(const struct scheduler_ctx *ctx) {
    int count = 0;
    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        if (ctx->jobs[i].used &&
            (ctx->jobs[i].state == JOB_QUEUED || ctx->jobs[i].state == JOB_WAITING)) {
            count++;
        }
    }
    return count;
}

void notify_user_event(struct scheduler_ctx *ctx, const char *username,
                       const char *fmt, ...) {
    if (username == NULL || username[0] == '\0') {
        return;
    }

    char buf[1024];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buf, sizeof(buf), fmt, args);
    va_end(args);

    for (int i = 0; i < MAX_CLIENTS; i++) {
        struct client_session *cs = &ctx->clients[i];
        if (cs->used && cs->logged_in && cs->sock_fd >= 0 &&
            strcmp(cs->username, username) == 0) {
            send_text_packet(cs->sock_fd, MSG_SCHED_EVENT, buf);
        }
    }
}

void append_job_log(struct scheduler_ctx *ctx, struct job_entry *j,
                    const char *data, int len) {
    if (j == NULL || data == NULL || len <= 0) {
        return;
    }

    if (j->log_buf == NULL) {
        j->log_buf = calloc(1, JOB_LOG_BUFFER_SIZE + 1);
        if (j->log_buf == NULL) {
            return;
        }
        j->log_len = 0;
    }

    /* Section 6: Keep at least the last 64 KB of output in memory */
    if (len >= JOB_LOG_BUFFER_SIZE) {
        memcpy(j->log_buf, data + (len - JOB_LOG_BUFFER_SIZE), JOB_LOG_BUFFER_SIZE);
        j->log_len = JOB_LOG_BUFFER_SIZE;
    } else if (j->log_len + len > JOB_LOG_BUFFER_SIZE) {
        int drop = (j->log_len + len) - JOB_LOG_BUFFER_SIZE;
        memmove(j->log_buf, j->log_buf + drop, (size_t)(j->log_len - drop));
        j->log_len -= drop;
        memcpy(j->log_buf + j->log_len, data, (size_t)len);
        j->log_len += len;
    } else {
        memcpy(j->log_buf + j->log_len, data, (size_t)len);
        j->log_len += len;
    }
    j->log_buf[j->log_len] = '\0';

    /* Stream chunk live to any client following this job (logs <id> -f) */
    for (int i = 0; i < MAX_CLIENTS; i++) {
        struct client_session *cs = &ctx->clients[i];
        if (cs->used && cs->sock_fd >= 0 && cs->follow_job_id == j->id) {
            send_packet(cs->sock_fd, MSG_SCHED_LOG_CHUNK, data, len);
        }
    }
}

void notify_job_followers_eof(struct scheduler_ctx *ctx, int job_id) {
    char footer[128];
    snprintf(footer, sizeof(footer), "-- Job %d finished --", job_id);

    for (int i = 0; i < MAX_CLIENTS; i++) {
        struct client_session *cs = &ctx->clients[i];
        if (cs->used && cs->sock_fd >= 0 && cs->follow_job_id == job_id) {
            cs->follow_job_id = 0;
            send_text_packet(cs->sock_fd, MSG_SCHED_LOG_EOF, footer);
        }
    }
}

/*
 * Section 8: Check WAITING jobs.
 * - If all dependencies are COMPLETED -> move WAITING to QUEUED.
 * - If any dependency is FAILED, FAILED_PERMANENT, or CANCELLED -> move WAITING to CANCELLED
 *   and cascade down the dependency chain.
 */
void check_job_dependencies(struct scheduler_ctx *ctx) {
    int changed = 0;
    do {
        changed = 0;
        for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
            struct job_entry *j = &ctx->jobs[i];
            if (!j->used || j->state != JOB_WAITING) {
                continue;
            }

            int all_completed = 1;
            int failed_dep_id = 0;

            for (int d = 0; d < j->num_deps; d++) {
                struct job_entry *dep = find_job_by_id(ctx, j->deps[d]);
                if (dep == NULL) {
                    failed_dep_id = j->deps[d];
                    break;
                }
                if (dep->state == JOB_FAILED ||
                    dep->state == JOB_FAILED_PERMANENT ||
                    dep->state == JOB_CANCELLED) {
                    failed_dep_id = dep->id;
                    break;
                }
                if (dep->state != JOB_COMPLETED) {
                    all_completed = 0;
                }
            }

            if (failed_dep_id > 0) {
                j->state = JOB_CANCELLED;
                snprintf(j->diagnosis, sizeof(j->diagnosis),
                         "Cancelled because dependency Job %d failed/cancelled.",
                         failed_dep_id);
                log_line("[SCHEDULER] Job %d WAITING -> CANCELLED (dependency Job %d failed)",
                         j->id, failed_dep_id);
                notify_user_event(ctx, j->user,
                                  "[Event] Job %d CANCELLED (dependency Job %d failed).",
                                  j->id, failed_dep_id);
                notify_job_followers_eof(ctx, j->id);
                changed = 1;
            } else if (all_completed) {
                j->state = JOB_QUEUED;
                j->queued_since = time(NULL);
                log_line("[SCHEDULER] Job %d WAITING -> QUEUED (dependencies satisfied)", j->id);
                notify_user_event(ctx, j->user,
                                  "[Event] Job %d moved from WAITING to QUEUED (dependency satisfied).",
                                  j->id);
                changed = 1;
            }
        }
    } while (changed);
}

struct job_entry *create_job_record(struct scheduler_ctx *ctx,
                                    const char *username,
                                    const struct msg_submit_req *req,
                                    const int *deps, int num_deps,
                                    int cron_id, int cron_run_no) {
    if (ctx->next_job_id > MAX_JOBS_TOTAL) {
        return NULL;
    }

    int jid = ctx->next_job_id++;
    struct job_entry *j = &ctx->jobs[jid - 1];
    memset(j, 0, sizeof(*j));

    j->used = 1;
    j->id = jid;
    snprintf(j->user, sizeof(j->user), "%s", username);
    snprintf(j->binary, sizeof(j->binary), "%s", req->binary);
    snprintf(j->exec_name, sizeof(j->exec_name), "%s", path_basename_ptr(req->binary));

    if (sha1_file(req->binary, j->sha1_hash, &j->binary_size) == 0) {
        j->is_local_file = 1;
    } else {
        j->is_local_file = 0;
        j->sha1_hash[0] = '\0';
        j->binary_size = 0;
    }

    j->cores = req->cores;
    j->ram_mb = req->ram_mb;
    j->gpu = req->gpu;
    j->time_sec = req->time_sec;
    j->base_prio = req->prio;
    j->eff_prio = req->prio;
    j->group_id = req->group_id;
    j->preemptible = req->preemptible;
    j->cron_id = cron_id;
    j->cron_run_no = cron_run_no;

    time_t now = time(NULL);
    j->submit_time = now;
    j->queued_since = now;

    j->num_deps = num_deps;
    for (int i = 0; i < num_deps && i < MAX_DEPS_PER_JOB; i++) {
        j->deps[i] = deps[i];
    }

    if (num_deps > 0) {
        j->state = JOB_WAITING;
    } else {
        j->state = JOB_QUEUED;
    }

    return j;
}

/*
 * Section 12: 1-second timer firing recurring (cron) job templates.
 */
void cron_tick(struct scheduler_ctx *ctx) {
    time_t now = time(NULL);

    for (int i = 0; i < MAX_CRON_TEMPLATES; i++) {
        struct cron_template *t = &ctx->crons[i];
        if (!t->used || !t->active || now < t->next_due) {
            continue;
        }

        if (count_queued_jobs(ctx) >= MAX_QUEUE_LEN) {
            t->next_due = now + t->every_sec;
            continue;
        }

        struct msg_submit_req req;
        memset(&req, 0, sizeof(req));
        snprintf(req.binary, sizeof(req.binary), "%s", t->binary);
        req.cores = t->cores;
        req.ram_mb = t->ram_mb;
        req.gpu = t->gpu;
        req.time_sec = t->time_sec;
        req.prio = t->prio;
        req.group_id = t->group_id;
        req.preemptible = t->preemptible;

        t->runs++;
        t->next_due = now + t->every_sec;

        struct job_entry *j = create_job_record(ctx, t->user, &req, NULL, 0, t->id, t->runs);
        if (j != NULL) {
            log_line("[SCHEDULER] Cron %d injected Job %d (run #%d) for user %s",
                     t->id, j->id, t->runs, t->user);
            notify_user_event(ctx, t->user,
                              "[Event] Cron %d injected Job %d (run #%d).",
                              t->id, j->id, t->runs);
        }
    }
}
