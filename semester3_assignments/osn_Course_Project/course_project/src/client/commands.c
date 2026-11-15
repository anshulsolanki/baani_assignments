#include "client.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Section 3: A valid username is 1 to 31 characters drawn from
 * letters, digits, '_', '-', and '.'.
 */
int is_valid_username(const char *name) {
    if (name == NULL) {
        return 0;
    }
    size_t len = strlen(name);
    if (len < 1 || len >= MAX_USERNAME_LEN) {
        return 0;
    }
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)name[i];
        if (!isalnum(c) && c != '_' && c != '-' && c != '.') {
            return 0;
        }
    }
    return 1;
}

static int parse_and_send_submit(struct client_ctx *cctx, int argc, char **argv) {
    if (argc < 2) {
        printf("[Client] Usage: submit <binary> -cores <num> -ram <MB> -time <sec> -prio <1-3> "
               "[-gpu <num>] [-depends-on <list>] [-group <id>] [-preemptible] [-every <sec>]\n");
        return 0;
    }

    struct msg_submit_req req;
    memset(&req, 0, sizeof(req));
    snprintf(req.binary, sizeof(req.binary), "%s", argv[1]);
    req.cores = -1;
    req.ram_mb = -1;
    req.time_sec = -1;
    req.prio = -1;
    req.gpu = 0;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-cores") == 0 && i + 1 < argc) {
            req.cores = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-ram") == 0 && i + 1 < argc) {
            req.ram_mb = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-time") == 0 && i + 1 < argc) {
            req.time_sec = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-prio") == 0 && i + 1 < argc) {
            req.prio = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-gpu") == 0 && i + 1 < argc) {
            req.gpu = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-group") == 0 && i + 1 < argc) {
            req.group_id = atoi(argv[++i]);
            if (req.group_id <= 0) {
                printf("[Client] Error: -group requires a positive integer.\n");
                return 0;
            }
        } else if (strcmp(argv[i], "-depends-on") == 0 && i + 1 < argc) {
            snprintf(req.depends_on, sizeof(req.depends_on), "%s", argv[++i]);
        } else if (strcmp(argv[i], "-preemptible") == 0) {
            req.preemptible = 1;
        } else if (strcmp(argv[i], "-every") == 0 && i + 1 < argc) {
            req.every_sec = atoi(argv[++i]);
            if (req.every_sec <= 0) {
                printf("[Client] Error: -every requires a positive interval in seconds.\n");
                return 0;
            }
        } else {
            printf("[Client] Error: unknown or incomplete submit flag '%s'.\n", argv[i]);
            return 0;
        }
    }

    if (req.cores <= 0 || req.ram_mb <= 0 || req.time_sec <= 0 ||
        req.prio < 1 || req.prio > 3) {
        printf("[Client] Error: missing or invalid required flags (-cores, -ram, -time, -prio <1-3>).\n");
        return 0;
    }

    if (send_packet(cctx->sock_fd, MSG_CLIENT_SUBMIT_REQ, &req, sizeof(req)) < 0) {
        return -1;
    }
    cctx->waiting_for_reply = 1;
    return 0;
}

/*
 * Parse a single command line entered at the client> prompt.
 * Returns 1 if the user requested exit, -1 on socket failure, 0 otherwise.
 */
int execute_client_command(struct client_ctx *cctx, const char *line) {
    char copy[1024];
    snprintf(copy, sizeof(copy), "%s", line);

    char *argv[64];
    int argc = 0;
    char *saveptr = NULL;
    char *tok = strtok_r(copy, " \t\r\n", &saveptr);
    while (tok != NULL && argc < 63) {
        argv[argc++] = tok;
        tok = strtok_r(NULL, " \t\r\n", &saveptr);
    }
    if (argc == 0) {
        return 0;
    }

    if (strcmp(argv[0], "exit") == 0 || strcmp(argv[0], "quit") == 0) {
        return 1;
    }

    if (strcmp(argv[0], "nodes") == 0) {
        if (send_packet(cctx->sock_fd, MSG_CLIENT_NODES_REQ, NULL, 0) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    if (strcmp(argv[0], "submit") == 0) {
        return parse_and_send_submit(cctx, argc, argv);
    }

    if (strcmp(argv[0], "status") == 0) {
        if (argc < 2) {
            printf("[Client] Usage: status <job_id>\n");
            return 0;
        }
        int32_t job_id = atoi(argv[1]);
        if (send_packet(cctx->sock_fd, MSG_CLIENT_STATUS_REQ, &job_id, sizeof(job_id)) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    if (strcmp(argv[0], "logs") == 0) {
        if (argc < 2) {
            printf("[Client] Usage: logs <job_id> [-f]\n");
            return 0;
        }
        struct msg_logs_req lreq;
        lreq.job_id = atoi(argv[1]);
        lreq.follow = (argc >= 3 && strcmp(argv[2], "-f") == 0) ? 1 : 0;
        if (send_packet(cctx->sock_fd, MSG_CLIENT_LOGS_REQ, &lreq, sizeof(lreq)) < 0) {
            return -1;
        }
        cctx->waiting_for_logs = 1;
        cctx->in_follow_mode = lreq.follow;
        return 0;
    }

    if (strcmp(argv[0], "cancel") == 0) {
        if (argc < 2) {
            printf("[Client] Usage: cancel <job_id>\n");
            return 0;
        }
        int32_t job_id = atoi(argv[1]);
        if (send_packet(cctx->sock_fd, MSG_CLIENT_CANCEL_REQ, &job_id, sizeof(job_id)) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    printf("[Client] Unknown command '%s'. Available: nodes, submit, status, logs, cancel, migrate, crons, cancel-cron\n",
           argv[0]);
    return 0;
}
