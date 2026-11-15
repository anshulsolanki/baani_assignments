#include "scheduler.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct client_session *find_client_by_fd(struct scheduler_ctx *ctx, int fd) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (ctx->clients[i].used && ctx->clients[i].sock_fd == fd) {
            return &ctx->clients[i];
        }
    }
    return NULL;
}

void handle_client_disconnect(struct scheduler_ctx *ctx, struct client_session *cs) {
    (void)ctx;
    if (cs->sock_fd >= 0) {
        close(cs->sock_fd);
        cs->sock_fd = -1;
    }
    cs->used = 0;
    cs->logged_in = 0;
    cs->follow_job_id = 0;
}

void handle_initial_connection_packet(struct scheduler_ctx *ctx, int fd) {
    struct packet_header hdr;
    if (recv_header(fd, &hdr) < 0) {
        close(fd);
        return;
    }

    if (hdr.type == MSG_WORKER_REGISTER && hdr.length == sizeof(struct msg_worker_register)) {
        struct msg_worker_register reg;
        if (recv_all(fd, &reg, sizeof(reg)) < 0) {
            close(fd);
            return;
        }

        struct worker_node *slot = NULL;
        for (int i = 0; i < MAX_WORKERS; i++) {
            if (!ctx->workers[i].used) {
                slot = &ctx->workers[i];
                break;
            }
        }
        if (slot == NULL) {
            close(fd);
            return;
        }

        memset(slot, 0, sizeof(*slot));
        slot->used = 1;
        slot->id = ctx->next_worker_id++;
        slot->sock_fd = fd;
        slot->state = WORKER_ALIVE;
        slot->last_heartbeat = time(NULL);
        slot->total_cores = reg.cores;
        slot->free_cores = reg.cores;
        slot->total_ram_mb = reg.ram_mb;
        slot->free_ram_mb = reg.ram_mb;
        slot->total_gpu = reg.gpu;
        slot->free_gpu = reg.gpu;

        struct msg_worker_reg_ack ack;
        ack.worker_id = slot->id;
        send_packet(fd, MSG_WORKER_REG_ACK, &ack, sizeof(ack));

        log_line("[SCHEDULER] Worker %d connected. Cores: %d, RAM: %dMB, GPU: %d",
                 slot->id, slot->total_cores, slot->total_ram_mb, slot->total_gpu);
        schedule_jobs(ctx);
        return;
    }

    if (hdr.type == MSG_CLIENT_LOGIN && hdr.length == sizeof(struct msg_client_login)) {
        struct msg_client_login login;
        if (recv_all(fd, &login, sizeof(login)) < 0) {
            close(fd);
            return;
        }
        login.username[MAX_USERNAME_LEN - 1] = '\0';

        struct client_session *cs = NULL;
        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (!ctx->clients[i].used) {
                cs = &ctx->clients[i];
                break;
            }
        }
        if (cs == NULL) {
            close(fd);
            return;
        }

        memset(cs, 0, sizeof(*cs));
        cs->used = 1;
        cs->sock_fd = fd;
        cs->logged_in = 1;
        cs->follow_job_id = 0;
        snprintf(cs->username, sizeof(cs->username), "%s", login.username);

        send_text_packet(fd, MSG_CLIENT_LOGIN_ACK, "OK");
        log_line("[SCHEDULER] Client '%s' connected.", cs->username);
        return;
    }

    close(fd);
}

/*
 * Parse -depends-on list such as "1,2,g3" at submit time (Section 8).
 * Expands group references g<id> into the job IDs currently in group <id>.
 * Rejects unknown job IDs or empty/unknown group IDs.
 */
static int resolve_dependencies(struct scheduler_ctx *ctx, const char *dep_str,
                                int *out_deps, int *out_count,
                                char *err_buf, size_t err_len) {
    *out_count = 0;
    if (dep_str == NULL || dep_str[0] == '\0') {
        return 0;
    }

    char copy[256];
    snprintf(copy, sizeof(copy), "%s", dep_str);

    char *saveptr = NULL;
    char *tok = strtok_r(copy, ",", &saveptr);
    while (tok != NULL) {
        while (*tok == ' ') {
            tok++;
        }
        if (*tok == '\0') {
            tok = strtok_r(NULL, ",", &saveptr);
            continue;
        }

        if (tok[0] == 'g' || tok[0] == 'G') {
            int gid = atoi(tok + 1);
            if (gid <= 0) {
                snprintf(err_buf, err_len,
                         "[Client] Error: invalid group dependency '%s'.", tok);
                return -1;
            }
            int matched = 0;
            for (int i = 0; i < MAX_JOBS_TOTAL; i++) {
                if (ctx->jobs[i].used && ctx->jobs[i].group_id == gid) {
                    if (*out_count < MAX_DEPS_PER_JOB) {
                        out_deps[(*out_count)++] = ctx->jobs[i].id;
                    }
                    matched++;
                }
            }
            if (matched == 0) {
                snprintf(err_buf, err_len,
                         "[Client] Error: group 'g%d' does not exist at submit time.", gid);
                return -1;
            }
        } else {
            for (size_t k = 0; tok[k] != '\0'; k++) {
                if (!isdigit((unsigned char)tok[k])) {
                    snprintf(err_buf, err_len,
                             "[Client] Error: invalid dependency token '%s'.", tok);
                    return -1;
                }
            }
            int djid = atoi(tok);
            struct job_entry *dj = find_job_by_id(ctx, djid);
            if (dj == NULL) {
                snprintf(err_buf, err_len,
                         "[Client] Error: dependency Job %d does not exist.", djid);
                return -1;
            }
            if (*out_count < MAX_DEPS_PER_JOB) {
                out_deps[(*out_count)++] = djid;
            }
        }

        tok = strtok_r(NULL, ",", &saveptr);
    }

    return 0;
}

void handle_client_message(struct scheduler_ctx *ctx, struct client_session *cs,
                           const struct packet_header *hdr) {
    switch (hdr->type) {
        case MSG_CLIENT_NODES_REQ: {
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
            break;
        }

        case MSG_CLIENT_SUBMIT_REQ: {
            struct msg_submit_req req;
            if (hdr->length != sizeof(req) || recv_all(cs->sock_fd, &req, sizeof(req)) < 0) {
                handle_client_disconnect(ctx, cs);
                return;
            }

            if (req.cores <= 0 || req.ram_mb <= 0 || req.time_sec <= 0 ||
                req.prio < 1 || req.prio > 3 || req.gpu < 0) {
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                 "[Client] Error: invalid submit resource/priority flags.");
                break;
            }

            /* Section 12: Recurring (Cron) job template registration */
            if (req.every_sec > 0) {
                if (req.depends_on[0] != '\0') {
                    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                     "[Client] Error: cannot combine -every with -depends-on.");
                    break;
                }
                if (ctx->next_cron_id > MAX_CRON_TEMPLATES) {
                    send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                     "[Client] Error: maximum cron templates reached.");
                    break;
                }

                int tid = ctx->next_cron_id++;
                struct cron_template *t = &ctx->crons[tid - 1];
                memset(t, 0, sizeof(*t));
                t->used = 1;
                t->id = tid;
                t->active = 1;
                snprintf(t->user, sizeof(t->user), "%s", cs->username);
                snprintf(t->binary, sizeof(t->binary), "%s", req.binary);
                snprintf(t->job_args, sizeof(t->job_args), "%s", req.job_args);
                t->cores = req.cores;
                t->ram_mb = req.ram_mb;
                t->gpu = req.gpu;
                t->time_sec = req.time_sec;
                t->prio = req.prio;
                t->group_id = req.group_id;
                t->preemptible = req.preemptible;
                t->every_sec = req.every_sec;
                t->runs = 0;
                t->next_due = time(NULL);

                log_line("[SCHEDULER] Cron template %d SUBMITTED by %s (every %ds)",
                         t->id, cs->username, t->every_sec);

                char reply[256];
                snprintf(reply, sizeof(reply),
                         "[Client] Cron template registered (every %ds).\n"
                         "[Client] Template ID assigned: %d",
                         t->every_sec, t->id);
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);

                /* First copy goes in immediately */
                cron_tick(ctx);
                schedule_jobs(ctx);
                break;
            }

            /* Section 4A: Bounded job queue (1024 entries max) */
            if (count_queued_jobs(ctx) >= MAX_QUEUE_LEN) {
                log_line("[SCHEDULER] Rejecting submit from %s: QUEUE_FULL", cs->username);
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                 "[Client] QUEUE_FULL: The job queue is full (1024 entries).");
                break;
            }

            int deps[MAX_DEPS_PER_JOB];
            int num_deps = 0;
            char err_msg[256] = "";
            if (resolve_dependencies(ctx, req.depends_on, deps, &num_deps,
                                     err_msg, sizeof(err_msg)) < 0) {
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err_msg);
                break;
            }

            struct job_entry *j = create_job_record(ctx, cs->username, &req,
                                                    deps, num_deps, 0, 0);
            if (j == NULL) {
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                 "[Client] QUEUE_FULL: Maximum job records reached.");
                break;
            }

            log_line("[SCHEDULER] Job %d SUBMITTED by %s", j->id, cs->username);

            char reply[512];
            if (num_deps > 0) {
                snprintf(reply, sizeof(reply),
                         "[Client] Job submitted (WAITING on %s).\n"
                         "[Client] Job ID assigned: %d",
                         req.depends_on, j->id);
            } else {
                snprintf(reply, sizeof(reply),
                         "[Client] Job submitted.\n"
                         "[Client] Job ID assigned: %d",
                         j->id);
            }
            send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);

            check_job_dependencies(ctx);
            schedule_jobs(ctx);
            break;
        }

        case MSG_CLIENT_STATUS_REQ: {
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
                break;
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
            break;
        }

        case MSG_CLIENT_LOGS_REQ: {
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
                break;
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
            break;
        }

        case MSG_CLIENT_LOGS_UNSUB: {
            if (hdr->length > 0) {
                char dummy[64];
                recv_all(cs->sock_fd, dummy, (size_t)hdr->length);
            }
            cs->follow_job_id = 0;
            break;
        }

        case MSG_CLIENT_CANCEL_REQ: {
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
                break;
            }

            if (j->state == JOB_COMPLETED || j->state == JOB_FAILED ||
                j->state == JOB_CANCELLED || j->state == JOB_FAILED_PERMANENT) {
                char err[128];
                snprintf(err, sizeof(err),
                         "[Client] Error: Job %d is already %s.",
                         j->id, job_state_str(j->state));
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
                break;
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
            break;
        }

        case MSG_CLIENT_MIGRATE_REQ: {
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
                break;
            }
            if (j->state != JOB_RUNNING) {
                char err[128];
                snprintf(err, sizeof(err),
                         "[Client] Error: Job %d is not RUNNING (current state: %s).",
                         j->id, job_state_str(j->state));
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
                break;
            }

            struct worker_node *w = find_worker_by_id(ctx, j->worker_id);
            if (w == NULL || w->sock_fd < 0) {
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                                 "[Client] Error: Worker running the job is unreachable.");
                break;
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
            break;
        }

        case MSG_CLIENT_CRONS_REQ: {
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
            break;
        }

        case MSG_CLIENT_CANCEL_CRON: {
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
                break;
            }
            struct cron_template *t = &ctx->crons[tid - 1];
            if (!t->active) {
                char err[128];
                snprintf(err, sizeof(err),
                         "[Client] Error: Cron template %d is already cancelled.", tid);
                send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err);
                break;
            }
            t->active = 0;
            log_line("[SCHEDULER] Cron %d cancelled by %s", tid, cs->username);
            char reply[128];
            snprintf(reply, sizeof(reply),
                     "[Client] Cron template %d cancelled (future runs stopped).", tid);
            send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, reply);
            break;
        }

        default: {
            if (hdr->length > 0) {
                char *skip = malloc((size_t)hdr->length);
                if (skip != NULL) {
                    recv_all(cs->sock_fd, skip, (size_t)hdr->length);
                    free(skip);
                }
            }
            break;
        }
    }
}
