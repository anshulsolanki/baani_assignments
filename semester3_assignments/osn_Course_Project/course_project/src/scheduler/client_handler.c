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
static int add_unique_dep(int *out_deps, int *out_count, int jid,
                          char *err_buf, size_t err_len) {
    for (int i = 0; i < *out_count; i++) {
        if (out_deps[i] == jid) {
            return 0;
        }
    }
    if (*out_count >= MAX_DEPS_PER_JOB) {
        snprintf(err_buf, err_len,
                 "[Client] Error: too many dependencies (max %d).", MAX_DEPS_PER_JOB);
        return -1;
    }
    out_deps[(*out_count)++] = jid;
    return 0;
}

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
                    if (add_unique_dep(out_deps, out_count, ctx->jobs[i].id,
                                       err_buf, err_len) < 0) {
                        return -1;
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
            if (add_unique_dep(out_deps, out_count, djid, err_buf, err_len) < 0) {
                return -1;
            }
        }

        tok = strtok_r(NULL, ",", &saveptr);
    }

    return 0;
}

static void handle_client_submit(struct scheduler_ctx *ctx, struct client_session *cs,
                                 const struct packet_header *hdr) {
    struct msg_submit_req req;
    if (hdr->length != sizeof(req) || recv_all(cs->sock_fd, &req, sizeof(req)) < 0) {
        handle_client_disconnect(ctx, cs);
        return;
    }

    if (req.cores <= 0 || req.ram_mb <= 0 || req.time_sec <= 0 ||
        req.prio < 1 || req.prio > 3 || req.gpu < 0) {
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                         "[Client] Error: invalid submit resource/priority flags.");
        return;
    }

    /* Section 12: Recurring (Cron) job template registration */
    if (req.every_sec > 0) {
        if (req.depends_on[0] != '\0') {
            send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                             "[Client] Error: cannot combine -every with -depends-on.");
            return;
        }
        if (ctx->next_cron_id > MAX_CRON_TEMPLATES) {
            send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                             "[Client] Error: maximum cron templates reached.");
            return;
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
        return;
    }

    int deps[MAX_DEPS_PER_JOB];
    int num_deps = 0;
    char err_msg[256] = "";
    if (resolve_dependencies(ctx, req.depends_on, deps, &num_deps,
                             err_msg, sizeof(err_msg)) < 0) {
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY, err_msg);
        return;
    }

    int enters_queue_now = (num_deps == 0) ? 1 : 0;
    if (num_deps > 0) {
        int all_done = 1;
        for (int d = 0; d < num_deps; d++) {
            struct job_entry *dep = find_job_by_id(ctx, deps[d]);
            if (dep == NULL || dep->state != JOB_COMPLETED) {
                all_done = 0;
                break;
            }
        }
        if (all_done) {
            enters_queue_now = 1;
        }
    }

    /* Section 4A: Bounded job queue (1024 QUEUED entries max) */
    if (enters_queue_now && count_queued_jobs(ctx) >= MAX_QUEUE_LEN) {
        log_line("[SCHEDULER] Rejecting submit from %s: QUEUE_FULL", cs->username);
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                         "[Client] QUEUE_FULL: The job queue is full (1024 entries).");
        return;
    }

    struct job_entry *j = create_job_record(ctx, cs->username, &req,
                                            deps, num_deps, 0, 0);
    if (j == NULL) {
        send_text_packet(cs->sock_fd, MSG_SCHED_REPLY,
                         "[Client] QUEUE_FULL: Maximum job records reached.");
        return;
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
}

void handle_client_message(struct scheduler_ctx *ctx, struct client_session *cs,
                           const struct packet_header *hdr) {
    switch (hdr->type) {
        case MSG_CLIENT_NODES_REQ:
            handle_client_nodes(ctx, cs);
            break;
        case MSG_CLIENT_SUBMIT_REQ:
            handle_client_submit(ctx, cs, hdr);
            break;
        case MSG_CLIENT_STATUS_REQ:
            handle_client_status(ctx, cs, hdr);
            break;
        case MSG_CLIENT_LOGS_REQ:
            handle_client_logs(ctx, cs, hdr);
            break;
        case MSG_CLIENT_LOGS_UNSUB:
            handle_client_logs_unsub(cs, hdr);
            break;
        case MSG_CLIENT_CANCEL_REQ:
            handle_client_cancel(ctx, cs, hdr);
            break;
        case MSG_CLIENT_MIGRATE_REQ:
            handle_client_migrate(ctx, cs, hdr);
            break;
        case MSG_CLIENT_CRONS_REQ:
            handle_client_crons(ctx, cs);
            break;
        case MSG_CLIENT_CANCEL_CRON:
            handle_client_cancel_cron(ctx, cs, hdr);
            break;
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
