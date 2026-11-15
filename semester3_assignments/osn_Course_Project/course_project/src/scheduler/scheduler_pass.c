#include "scheduler.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Track already-logged (skipped_job, favored_job) quota pairs to avoid log spam */
#define MAX_QUOTA_LOG_PAIRS 256
static struct {
    int skipped_id;
    int favored_id;
} quota_logged_pairs[MAX_QUOTA_LOG_PAIRS];
static int num_quota_logged = 0;

static int was_quota_pair_logged(int skipped_id, int favored_id) {
    for (int i = 0; i < num_quota_logged; i++) {
        if (quota_logged_pairs[i].skipped_id == skipped_id &&
            quota_logged_pairs[i].favored_id == favored_id) {
            return 1;
        }
    }
    if (num_quota_logged < MAX_QUOTA_LOG_PAIRS) {
        quota_logged_pairs[num_quota_logged].skipped_id = skipped_id;
        quota_logged_pairs[num_quota_logged].favored_id = favored_id;
        num_quota_logged++;
    }
    return 0;
}

static int total_non_dead_cluster_cores(const struct scheduler_ctx *ctx) {
    int total = 0;
    for (int i = 0; i < MAX_WORKERS; i++) {
        const struct worker_node *w = &ctx->workers[i];
        if (w->used && w->state != WORKER_DEAD) {
            total += w->total_cores;
        }
    }
    return total;
}

static int user_held_cores(const struct scheduler_ctx *ctx, const char *user) {
    int held = 0;
    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        const struct job_entry *j = &ctx->jobs[i];
        if (j->used && j->state == JOB_RUNNING && strcmp(j->user, user) == 0) {
            held += j->cores;
        }
    }
    return held;
}

static int is_user_over_quota(const struct scheduler_ctx *ctx, const char *user) {
    int cluster_cores = total_non_dead_cluster_cores(ctx);
    if (cluster_cores <= 0) {
        return 0;
    }
    /* Strictly more than 50% of non-dead cluster cores */
    return (user_held_cores(ctx, user) * 2) > cluster_cores;
}

/*
 * Section 4D & 13: Full 4-level worker comparison tiebreaker.
 * Returns 1 if candidate `a` is strictly better than `b` for job `j`.
 * Tiebreaker order: idle > cached binary > lowest CPU% > fewest running jobs.
 */
static int is_better_worker(const struct worker_node *a,
                            const struct worker_node *b,
                            const struct job_entry *j,
                            char *reason_buf, size_t reason_len) {
    int a_idle = (a->running_jobs == 0) ? 1 : 0;
    int b_idle = (b->running_jobs == 0) ? 1 : 0;
    if (a_idle != b_idle) {
        if (a_idle && reason_buf != NULL) {
            snprintf(reason_buf, reason_len, "idle vs busy");
        }
        return a_idle > b_idle;
    }

    if (j->is_local_file && j->sha1_hash[0] != '\0') {
        int a_cached = worker_has_hash(a, j->sha1_hash);
        int b_cached = worker_has_hash(b, j->sha1_hash);
        if (a_cached != b_cached) {
            if (a_cached && reason_buf != NULL) {
                snprintf(reason_buf, reason_len,
                         "binary cached vs not cached, both %s",
                         a_idle ? "idle" : "busy");
            }
            return a_cached > b_cached;
        }
    }

    if (a->cpu_load_pct != b->cpu_load_pct) {
        if (a->cpu_load_pct < b->cpu_load_pct && reason_buf != NULL) {
            snprintf(reason_buf, reason_len, "CPU %d%% vs %d%%",
                     a->cpu_load_pct, b->cpu_load_pct);
        }
        return a->cpu_load_pct < b->cpu_load_pct;
    }

    if (a->running_jobs != b->running_jobs) {
        if (a->running_jobs < b->running_jobs && reason_buf != NULL) {
            snprintf(reason_buf, reason_len, "fewer running jobs: %d vs %d",
                     a->running_jobs, b->running_jobs);
        }
        return a->running_jobs < b->running_jobs;
    }

    return a->id < b->id;
}

static int worker_fits_job(const struct worker_node *w, const struct job_entry *j) {
    if (!w->used || w->state != WORKER_ALIVE || w->sock_fd < 0) {
        return 0;
    }
    if (w->free_cores < j->cores || w->free_ram_mb < j->ram_mb || w->free_gpu < j->gpu) {
        return 0;
    }
    return 1;
}

static int send_binary_to_worker(struct worker_node *w, const struct job_entry *j) {
    FILE *fp = fopen(j->binary, "rb");
    if (fp == NULL) {
        return -1;
    }

    uint8_t *payload = malloc(sizeof(struct msg_binary_meta) + BIN_CHUNK_MAX);
    if (payload == NULL) {
        fclose(fp);
        return -1;
    }

    int32_t offset = 0;
    size_t n = 0;
    while ((n = fread(payload + sizeof(struct msg_binary_meta), 1, BIN_CHUNK_MAX, fp)) > 0) {
        struct msg_binary_meta meta;
        memset(&meta, 0, sizeof(meta));
        meta.job_id = j->id;
        snprintf(meta.exec_name, sizeof(meta.exec_name), "%s", j->exec_name);
        snprintf(meta.sha1_hash, sizeof(meta.sha1_hash), "%s", j->sha1_hash);
        meta.total_size = j->binary_size;
        meta.offset = offset;
        meta.chunk_len = (int32_t)n;

        memcpy(payload, &meta, sizeof(meta));
        int32_t pkt_len = (int32_t)sizeof(meta) + (int32_t)n;
        if (send_packet(w->sock_fd, MSG_SCHED_BINARY_CHUNK, payload, pkt_len) < 0) {
            free(payload);
            fclose(fp);
            return -1;
        }
        offset += (int32_t)n;
    }

    free(payload);
    fclose(fp);
    return 0;
}

int dispatch_job_to_worker(struct scheduler_ctx *ctx, struct job_entry *j,
                           struct worker_node *w) {
    /* Refresh hash/size in case binary on disk was modified between runs */
    if (sha1_file(j->binary, j->sha1_hash, &j->binary_size) == 0) {
        j->is_local_file = 1;
    } else {
        j->is_local_file = 0;
    }

    /* Step 1 after worker chosen: Send saved checkpoint first if job has one (Section 14) */
    int has_ckpt = (j->ckpt_data != NULL && j->ckpt_len > 0) ? 1 : 0;
    if (has_ckpt) {
        int32_t pkt_len = (int32_t)sizeof(struct msg_ckpt_header) + j->ckpt_len;
        uint8_t *buf = malloc((size_t)pkt_len);
        if (buf != NULL) {
            struct msg_ckpt_header ch;
            ch.job_id = j->id;
            ch.data_len = j->ckpt_len;
            memcpy(buf, &ch, sizeof(ch));
            memcpy(buf + sizeof(ch), j->ckpt_data, (size_t)j->ckpt_len);
            send_packet(w->sock_fd, MSG_SCHED_CKPT_DATA, buf, pkt_len);
            free(buf);
        }
    }

    /* Step 2 after worker chosen: Send binary or short EXEC_CACHED message (Section 13) */
    int exec_transferred = 0;
    if (j->is_local_file && j->sha1_hash[0] != '\0') {
        if (worker_has_hash(w, j->sha1_hash)) {
            struct msg_exec_cached ec;
            memset(&ec, 0, sizeof(ec));
            ec.job_id = j->id;
            snprintf(ec.exec_name, sizeof(ec.exec_name), "%s", j->exec_name);
            snprintf(ec.sha1_hash, sizeof(ec.sha1_hash), "%s", j->sha1_hash);
            send_packet(w->sock_fd, MSG_SCHED_EXEC_CACHED, &ec, sizeof(ec));
            exec_transferred = 1;
            log_line("[SCHEDULER] Job %d: %s already cached (sha1 %.8s...) on Worker %d, not sending",
                     j->id, j->binary, j->sha1_hash, w->id);
        } else if (send_binary_to_worker(w, j) == 0) {
            worker_add_hash(w, j->sha1_hash);
            exec_transferred = 1;
            log_line("[SCHEDULER] Job %d: sent %s (%d bytes, sha1 %.8s...) -> Worker %d",
                     j->id, j->binary, (int)j->binary_size, j->sha1_hash, w->id);
        }
    }

    /* Step 3: Send ASSIGN_JOB */
    struct msg_assign_job assign;
    memset(&assign, 0, sizeof(assign));
    assign.job_id = j->id;
    assign.cores = j->cores;
    assign.ram_mb = j->ram_mb;
    assign.gpu = j->gpu;
    assign.time_limit_sec = j->time_sec;
    assign.exec_transferred = exec_transferred;
    assign.has_checkpoint = has_ckpt;
    snprintf(assign.binary_path, sizeof(assign.binary_path), "%s", j->binary);
    snprintf(assign.exec_name, sizeof(assign.exec_name), "%s", j->exec_name);
    snprintf(assign.sha1_hash, sizeof(assign.sha1_hash), "%s", j->sha1_hash);

    if (send_packet(w->sock_fd, MSG_SCHED_ASSIGN_JOB, &assign, sizeof(assign)) < 0) {
        return -1;
    }

    j->state = JOB_RUNNING;
    j->worker_id = w->id;
    j->attempts++;
    j->avoid_worker_id = 0;

    w->free_cores -= j->cores;
    w->free_ram_mb -= j->ram_mb;
    w->free_gpu -= j->gpu;
    w->running_jobs++;

    /* Release any preempted victims that were held waiting for this priority-1 job to start */
    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        if (ctx->jobs[i].used && ctx->jobs[i].hold_for_job_id == j->id) {
            ctx->jobs[i].hold_for_job_id = 0;
        }
    }

    if (j->attempts > 1) {
        notify_user_event(ctx, j->user,
                          "[Event] Job %d (attempt %d) RUNNING on Worker %d.",
                          j->id, j->attempts, w->id);
    } else {
        notify_user_event(ctx, j->user,
                          "[Event] Job %d RUNNING on Worker %d.",
                          j->id, w->id);
    }

    return 0;
}

/*
 * Section 10: Preemption for a Priority 1 job when no worker currently has enough free resources.
 * Picks an ALIVE worker where killing preemptible jobs (prio > 1) frees enough resources.
 * Victims are ordered: lowest priority (highest number) first, then newest submission first.
 */
static void try_preempt_for_job(struct scheduler_ctx *ctx, struct job_entry *prio1_job) {
    /* Do not issue duplicate preemptions if victims are already being stopped for this job */
    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        if (ctx->jobs[i].used &&
            (ctx->jobs[i].hold_for_job_id == prio1_job->id ||
             (ctx->jobs[i].preempt_pending && ctx->jobs[i].hold_for_job_id == prio1_job->id))) {
            return;
        }
    }

    for (int wi = 0; wi < MAX_WORKERS; wi++) {
        struct worker_node *w = &ctx->workers[wi];
        if (!w->used || w->state != WORKER_ALIVE || w->sock_fd < 0) {
            continue;
        }
        if (w->total_cores < prio1_job->cores ||
            w->total_ram_mb < prio1_job->ram_mb ||
            w->total_gpu < prio1_job->gpu) {
            continue;
        }

        struct job_entry *cands[MAX_WORKER_JOBS];
        int ncand = 0;
        for (int ji = 0; ji < MAX_JOBS_TOTAL; ji++) {
            struct job_entry *v = &ctx->jobs[ji];
            if (v->used && v->state == JOB_RUNNING && v->worker_id == w->id &&
                v->preemptible && v->base_prio > 1 && !v->preempt_pending && !v->migrate_pending) {
                if (ncand < MAX_WORKER_JOBS) {
                    cands[ncand++] = v;
                }
            }
        }

        /* Sort candidates: highest priority number (lowest priority) first, then newest submit first */
        for (int a = 0; a < ncand; a++) {
            for (int b = a + 1; b < ncand; b++) {
                int swap = 0;
                if (cands[b]->base_prio > cands[a]->base_prio) {
                    swap = 1;
                } else if (cands[b]->base_prio == cands[a]->base_prio) {
                    if (cands[b]->submit_time > cands[a]->submit_time ||
                        (cands[b]->submit_time == cands[a]->submit_time &&
                         cands[b]->id > cands[a]->id)) {
                        swap = 1;
                    }
                }
                if (swap) {
                    struct job_entry *tmp = cands[a];
                    cands[a] = cands[b];
                    cands[b] = tmp;
                }
            }
        }

        int fc = w->free_cores;
        int fr = w->free_ram_mb;
        int fg = w->free_gpu;
        int nvictims = 0;

        for (int c = 0; c < ncand; c++) {
            fc += cands[c]->cores;
            fr += cands[c]->ram_mb;
            fg += cands[c]->gpu;
            nvictims++;
            if (fc >= prio1_job->cores && fr >= prio1_job->ram_mb && fg >= prio1_job->gpu) {
                break;
            }
        }

        if (fc >= prio1_job->cores && fr >= prio1_job->ram_mb && fg >= prio1_job->gpu) {
            for (int c = 0; c < nvictims; c++) {
                struct job_entry *v = cands[c];
                v->preempt_pending = 1;
                v->hold_for_job_id = prio1_job->id;

                struct msg_stop_job stop_cmd;
                stop_cmd.job_id = v->id;
                stop_cmd.reason = STOP_PREEMPT;
                send_packet(w->sock_fd, MSG_SCHED_STOP_JOB, &stop_cmd, sizeof(stop_cmd));

                log_line("[SCHEDULER] Preempting Job %d (prio %d) on Worker %d to make room for Priority 1 Job %d",
                         v->id, v->base_prio, w->id, prio1_job->id);
            }
            return;
        }
    }
}

/*
 * Canonical 10-step Scheduling Pass (Page 18: Order of Scheduling Decisions).
 */
void schedule_jobs(struct scheduler_ctx *ctx) {
    time_t now = time(NULL);

    /* Step 1 & 2: Collect QUEUED jobs only and apply 10s aging for PRIORITY mode */
    struct job_entry *queued[MAX_JOBS_TOTAL];
    int qcount = 0;

    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        struct job_entry *j = &ctx->jobs[i];
        if (!j->used || j->state != JOB_QUEUED) {
            continue;
        }

        if (ctx->algo == ALGO_PRIORITY) {
            long wait_sec = (long)(now - j->queued_since);
            if (wait_sec < 0) {
                wait_sec = 0;
            }
            int boost = (int)(wait_sec / 10);
            j->eff_prio = j->base_prio - boost;
            if (j->eff_prio < 1) {
                j->eff_prio = 1;
            }
        } else {
            j->eff_prio = j->base_prio;
        }

        /* Refresh local file hash check before worker matching so cached tiebreaker is accurate */
        if (sha1_file(j->binary, j->sha1_hash, &j->binary_size) == 0) {
            j->is_local_file = 1;
        }

        queued[qcount++] = j;
    }

    if (qcount == 0) {
        return;
    }

    /* Step 3: Sort QUEUED jobs (FIFO: submission order; PRIORITY: eff_prio, then older first) */
    for (int a = 0; a < qcount; a++) {
        for (int b = a + 1; b < qcount; b++) {
            int swap = 0;
            if (ctx->algo == ALGO_FIFO) {
                if (queued[b]->id < queued[a]->id) {
                    swap = 1;
                }
            } else {
                if (queued[b]->eff_prio < queued[a]->eff_prio) {
                    swap = 1;
                } else if (queued[b]->eff_prio == queued[a]->eff_prio) {
                    if (queued[b]->submit_time < queued[a]->submit_time ||
                        (queued[b]->submit_time == queued[a]->submit_time &&
                         queued[b]->id < queued[a]->id)) {
                        swap = 1;
                    }
                }
            }
            if (swap) {
                struct job_entry *tmp = queued[a];
                queued[a] = queued[b];
                queued[b] = tmp;
            }
        }
    }

    /* Iterate through sorted QUEUED jobs */
    for (int i = 0; i < qcount; i++) {
        struct job_entry *j = queued[i];

        /* Step 4: Preempted-job hold check (Section 10) */
        if (j->hold_for_job_id > 0) {
            struct job_entry *holder = find_job_by_id(ctx, j->hold_for_job_id);
            if (holder != NULL &&
                (holder->state == JOB_QUEUED || holder->state == JOB_WAITING)) {
                continue;
            }
            j->hold_for_job_id = 0;
        }

        (void)is_user_over_quota;
        (void)was_quota_pair_logged;

        /* Step 6 & 7: Resource match + Choose one worker using 4-level tiebreaker */
        struct worker_node *best_w = NULL;
        struct worker_node *runner_up = NULL;
        char win_reason[128] = "";

        for (int wi = 0; wi < MAX_WORKERS; wi++) {
            struct worker_node *w = &ctx->workers[wi];
            if (!worker_fits_job(w, j)) {
                continue;
            }
            if (j->avoid_worker_id > 0 && w->id == j->avoid_worker_id) {
                continue;
            }
            if (best_w == NULL) {
                best_w = w;
            } else {
                char tmp_reason[128] = "";
                if (is_better_worker(w, best_w, j, tmp_reason, sizeof(tmp_reason))) {
                    runner_up = best_w;
                    best_w = w;
                    snprintf(win_reason, sizeof(win_reason), "%s", tmp_reason);
                } else if (runner_up == NULL) {
                    runner_up = w;
                    is_better_worker(best_w, w, j, win_reason, sizeof(win_reason));
                }
            }
        }

        /* Section 14 fallback: if only avoid_worker_id fits, allow it */
        if (best_w == NULL && j->avoid_worker_id > 0) {
            struct worker_node *aw = find_worker_by_id(ctx, j->avoid_worker_id);
            if (aw != NULL && worker_fits_job(aw, j)) {
                best_w = aw;
            }
        }

        if (best_w != NULL) {
            if (runner_up != NULL && win_reason[0] != '\0') {
                log_line("[SCHEDULER] Job %d -> Worker %d (chosen over %d: %s)",
                         j->id, best_w->id, runner_up->id, win_reason);
            } else {
                log_line("[SCHEDULER] Job %d -> Worker %d", j->id, best_w->id);
            }
            dispatch_job_to_worker(ctx, j, best_w);
        } else {
            /* Step 8: No match -> Priority 1 job tries preemption, then FIFO stops or PRIORITY continues */
            if (j->eff_prio == 1) {
                try_preempt_for_job(ctx, j);
            }
            if (ctx->algo == ALGO_FIFO) {
                break;
            }
        }
    }
}
