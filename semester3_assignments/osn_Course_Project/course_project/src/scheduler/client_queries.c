#include "scheduler.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void handle_client_nodes(struct scheduler_ctx *ctx, struct client_session *cs) {
    char buf[8192];
    int off = 0;
    off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                    "--- Cluster Status ---\n"
                    "%-6s %-10s %-19s %-21s %-16s %s\n",
                    "ID", "Status", "Cores (Free/Total)",
                    "RAM (Free/Total)", "GPU (Free/Total)", "Jobs");

    int any = 0;
    for (int i = 0; i < MAX_WORKERS; i++) {
        struct worker_node *w = &ctx->workers[i];
        if (!w->used) {
            continue;
        }
        any = 1;
        char cores_s[32], ram_s[32], gpu_s[32];
        snprintf(cores_s, sizeof(cores_s), "%d / %d", w->free_cores, w->total_cores);
        snprintf(ram_s, sizeof(ram_s), "%d / %d", w->free_ram_mb, w->total_ram_mb);
        snprintf(gpu_s, sizeof(gpu_s), "%d / %d", w->free_gpu, w->total_gpu);

        off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                        "%-6d %-10s %-19s %-21s %-16s %d\n",
                        w->id, worker_state_str(w->state),
                        cores_s, ram_s, gpu_s, w->running_jobs);
    }
    if (!any) {
        off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                        "(no workers registered)\n");
    }
    off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                    "----------------------");
    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, buf);
}

void handle_client_status(struct scheduler_ctx *ctx, struct client_session *cs,
                          const struct packet_header *hdr) {
    int32_t job_id = 0;
    if (hdr->length != sizeof(job_id) || recv_all(cs->sock_fd, &job_id, sizeof(job_id)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }

    struct job_entry *j = find_job_by_id(ctx, job_id);
    if (j == NULL) {
        char err[128];
        snprintf(err, sizeof(err), "[Client] Error: Job %d not found.", job_id);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }

    char out[1024];
    int off = 0;
    off += snprintf(out + off, sizeof(out) - (size_t)off,
                    "[Job %d] Status: %s\n"
                    "[Job %d] User: %s\n",
                    j->id, job_state_str(j->state),
                    j->id, j->user);

    if (j->state == JOB_RUNNING) {
        off += snprintf(out + off, sizeof(out) - (size_t)off,
                        "  - Current RAM: %dMB / %dMB Limit\n"
                        "  - Page Faults: %d\n"
                        "  - CPU Time: %.1fs\n"
                        "[Job %d] Assigned to: Worker %d",
                        j->current_ram_mb, j->ram_mb,
                        j->page_faults,
                        j->cpu_time_sec,
                        j->id, j->worker_id);
    } else {
        if (j->worker_id > 0) {
            off += snprintf(out + off, sizeof(out) - (size_t)off,
                            "[Job %d] Assigned to: Worker %d",
                            j->id, j->worker_id);
        } else {
            off += snprintf(out + off, sizeof(out) - (size_t)off,
                            "[Job %d] Assigned to: None", j->id);
        }
        if (j->peak_ram_mb > 0 || j->state == JOB_COMPLETED || j->state == JOB_FAILED) {
            off += snprintf(out + off, sizeof(out) - (size_t)off,
                            "\n  - Peak RAM: %dMB / %dMB Limit\n"
                            "  - Page Faults: %d\n"
                            "  - CPU Time: %.1fs",
                            j->peak_ram_mb, j->ram_mb,
                            j->page_faults, j->cpu_time_sec);
        }
        if (j->diagnosis[0] != '\0') {
            off += snprintf(out + off, sizeof(out) - (size_t)off,
                            "\n  - Reason: %s", j->diagnosis);
        }
    }

    if (j->ckpt_count > 0) {
        long age = (long)(time(NULL) - j->ckpt_time);
        if (age < 0) {
            age = 0;
        }
        off += snprintf(out + off, sizeof(out) - (size_t)off,
                        "\n  - Latest Checkpoint: #%d (%d bytes, age %lds)",
                        j->ckpt_count, (int)j->ckpt_len, age);
    }

    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, out);
}

void handle_client_logs(struct scheduler_ctx *ctx, struct client_session *cs,
                        const struct packet_header *hdr) {
    struct msg_logs_req lreq;
    if (hdr->length != sizeof(lreq) || recv_all(cs->sock_fd, &lreq, sizeof(lreq)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }

    struct job_entry *j = find_job_by_id(ctx, lreq.job_id);
    if (j == NULL) {
        char err[128];
        snprintf(err, sizeof(err), "[Client] Error: Job %d not found.", lreq.job_id);
        send_text_packet(cs->sock_fd, MSG_SCHED_LOG_EOF, err);
        return;
    }

    if (j->log_buf != NULL && j->log_len > 0) {
        send_packet(cs->sock_fd, MSG_SCHED_LOG_CHUNK, j->log_buf, j->log_len);
    }

    if (lreq.follow) {
        log_line("[SCHEDULER] Client '%s' following Job %d logs",
                 cs->username, j->id);
        if (j->state == JOB_COMPLETED || j->state == JOB_FAILED ||
            j->state == JOB_CANCELLED || j->state == JOB_FAILED_PERMANENT) {
            char footer[128];
            snprintf(footer, sizeof(footer), "-- Job %d finished --", j->id);
            send_text_packet(cs->sock_fd, MSG_SCHED_LOG_EOF, footer);
        } else {
            cs->follow_job_id = j->id;
        }
    } else {
        send_text_packet(cs->sock_fd, MSG_SCHED_LOG_EOF, "");
    }
}

void handle_client_logs_unsub(struct client_session *cs,
                              const struct packet_header *hdr) {
    if (hdr->length > 0) {
        char dummy[64];
        recv_all(cs->sock_fd, dummy, (size_t)hdr->length);
    }
    cs->follow_job_id = 0;
}

void handle_client_cancel(struct scheduler_ctx *ctx, struct client_session *cs,
                          const struct packet_header *hdr) {
    int32_t job_id = 0;
    if (hdr->length != sizeof(job_id) || recv_all(cs->sock_fd, &job_id, sizeof(job_id)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }

    struct job_entry *j = find_job_by_id(ctx, job_id);
    if (j == NULL) {
        char err[128];
        snprintf(err, sizeof(err), "[Client] Error: Job %d not found.", job_id);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }

    if (j->state == JOB_COMPLETED || j->state == JOB_FAILED ||
        j->state == JOB_CANCELLED || j->state == JOB_FAILED_PERMANENT) {
        char err[128];
        snprintf(err, sizeof(err),
                 "[Client] Error: Job %d is already %s.",
                 j->id, job_state_str(j->state));
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }

    int prev_state = j->state;
    if (prev_state == JOB_RUNNING) {
        struct worker_node *w = find_worker_by_id(ctx, j->worker_id);
        if (w != NULL) {
            if (w->sock_fd >= 0) {
                struct msg_stop_job stop_cmd;
                stop_cmd.job_id = j->id;
                stop_cmd.reason = STOP_CANCEL;
                send_packet(w->sock_fd, MSG_SCHED_STOP_JOB, &stop_cmd, sizeof(stop_cmd));
            }
            w->free_cores += j->cores;
            w->free_ram_mb += j->ram_mb;
            w->free_gpu += j->gpu;
            if (w->running_jobs > 0) {
                w->running_jobs--;
            }
        }
        log_line("[SCHEDULER] Job %d RUNNING -> CANCELLED (kill sent, requested by %s)",
                 j->id, cs->username);
    } else {
        log_line("[SCHEDULER] Job %d %s -> CANCELLED (requested by %s)",
                 j->id, job_state_str(prev_state), cs->username);
    }

    j->state = JOB_CANCELLED;
    j->preempt_pending = 0;
    j->migrate_pending = 0;
    j->current_ram_mb = 0;
    snprintf(j->diagnosis, sizeof(j->diagnosis),
             "Cancelled by %s", cs->username);

    for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
        if (ctx->jobs[i].used && ctx->jobs[i].hold_for_job_id == j->id) {
            ctx->jobs[i].hold_for_job_id = 0;
        }
    }

    notify_user_event(ctx, j->user,
                      "[Event] Job %d %s -> CANCELLED (requested by %s).",
                      j->id, job_state_str(prev_state), cs->username);
    notify_job_followers_eof(ctx, j->id);

    char reply[128];
    snprintf(reply, sizeof(reply), "[Client] Job %d cancelled.", j->id);
    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);

    check_job_dependencies(ctx);
    schedule_jobs(ctx);
}

void handle_client_migrate(struct scheduler_ctx *ctx, struct client_session *cs,
                           const struct packet_header *hdr) {
    int32_t job_id = 0;
    if (hdr->length != sizeof(job_id) || recv_all(cs->sock_fd, &job_id, sizeof(job_id)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }

    struct job_entry *j = find_job_by_id(ctx, job_id);
    if (j == NULL) {
        char err[128];
        snprintf(err, sizeof(err), "[Client] Error: Job %d does not exist.", job_id);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }
    if (j->state != JOB_RUNNING) {
        char err[128];
        snprintf(err, sizeof(err),
                 "[Client] Error: Job %d is not RUNNING (current state: %s).",
                 j->id, job_state_str(j->state));
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }

    struct worker_node *w = find_worker_by_id(ctx, j->worker_id);
    if (w == NULL || w->sock_fd < 0) {
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                         "[Client] Error: Worker running the job is unreachable.");
        return;
    }

    j->migrate_pending = 1;
    struct msg_stop_job stop_cmd;
    stop_cmd.job_id = j->id;
    stop_cmd.reason = STOP_MIGRATE;
    send_packet(w->sock_fd, MSG_SCHED_STOP_JOB, &stop_cmd, sizeof(stop_cmd));

    log_line("[SCHEDULER] Migrating Job %d off Worker %d (requested by %s)",
             j->id, w->id, cs->username);

    char reply[256];
    if (j->ckpt_count > 0) {
        snprintf(reply, sizeof(reply),
                 "[Client] Migrating Job %d off Worker %d. It will resume from checkpoint #%d.",
                 j->id, w->id, j->ckpt_count);
    } else {
        snprintf(reply, sizeof(reply),
                 "[Client] Migrating Job %d off Worker %d.",
                 j->id, w->id);
    }
    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);
}

void handle_client_crons(struct scheduler_ctx *ctx, struct client_session *cs) {
    char buf[4096];
    int off = 0;
    off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                    "--- Cron Templates ---\n"
                    "%-4s %-10s %-6s %-10s %-12s %s\n",
                    "ID", "Interval", "Runs", "Status", "User", "Command");
    int any = 0;
    for (int i = 0; i < MAX_CRON_TEMPLATES; i++) {
        struct cron_template *t = &ctx->crons[i];
        if (!t->used) {
            continue;
        }
        any = 1;
        char iv_s[24];
        snprintf(iv_s, sizeof(iv_s), "%ds", t->every_sec);
        off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                        "%-4d %-10s %-6d %-10s %-12s %s%s%s\n",
                        t->id, iv_s, t->runs,
                        t->active ? "ACTIVE" : "CANCELLED",
                        t->user, t->binary,
                        t->job_args[0] ? " " : "", t->job_args);
    }
    if (!any) {
        off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                        "(no cron templates)\n");
    }
    off += snprintf(buf + off, sizeof(buf) - (size_t)off,
                    "----------------------");
    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, buf);
}

void handle_client_cancel_cron(struct scheduler_ctx *ctx, struct client_session *cs,
                               const struct packet_header *hdr) {
    int32_t tid = 0;
    if (hdr->length != sizeof(tid) || recv_all(cs->sock_fd, &tid, sizeof(tid)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }
    if (tid <= 0 || tid > MAX_CRON_TEMPLATES || !ctx->crons[tid - 1].used) {
        char err[128];
        snprintf(err, sizeof(err),
                 "[Client] Error: Cron template %d does not exist.", tid);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }
    struct cron_template *t = &ctx->crons[tid - 1];
    if (!t->active) {
        char err[128];
        snprintf(err, sizeof(err),
                 "[Client] Error: Cron template %d is already cancelled.", tid);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
        return;
    }
    t->active = 0;
    log_line("[SCHEDULER] Cron %d cancelled by %s", tid, cs->username);
    char reply[128];
    snprintf(reply, sizeof(reply),
             "[Client] Cron template %d cancelled (future runs stopped).", tid);
    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);
}
