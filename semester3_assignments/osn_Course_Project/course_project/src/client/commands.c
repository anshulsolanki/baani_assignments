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

static const char *norm_flag(const char *arg) {
    if (arg[0] == '-' && arg[1] == '-' && arg[2] != '\0') {
        return arg + 1;
    }
    return arg;
}

static int tokenize_command_line(char *buf, char **argv, int max_args) {
    int argc = 0;
    char *p = buf;
    while (*p != '\0' && argc < max_args - 1) {
        while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') {
            p++;
        }
        if (*p == '\0') {
            break;
        }
        if (*p == '"' || *p == '\'') {
            char q = *p++;
            argv[argc++] = p;
            while (*p != '\0' && *p != q) {
                p++;
            }
            if (*p == q) {
                *p++ = '\0';
            }
        } else {
            argv[argc++] = p;
            while (*p != '\0' && *p != ' ' && *p != '\t' && *p != '\r' && *p != '\n') {
                p++;
            }
            if (*p != '\0') {
                *p++ = '\0';
            }
        }
    }
    argv[argc] = NULL;
    return argc;
}

static void append_job_arg(char *dst, size_t dst_sz, const char *arg) {
    size_t cur = strlen(dst);
    int has_space = (strchr(arg, ' ') != NULL || strchr(arg, '\t') != NULL);
    snprintf(dst + cur, dst_sz - cur, "%s%s%s%s",
             (cur > 0) ? " " : "",
             has_space ? "\"" : "",
             arg,
             has_space ? "\"" : "");
}

static int parse_and_send_submit(struct client_ctx *cctx, int argc, char **argv) {
    if (argc < 2) {
        printf("[Client] Usage: submit <binary> -cores <num> -ram <MB> -time <sec> -prio <1-3> "
               "[-gpu <num>] [-depends-on <list>] [-group <id>] [-preemptible] [-every <sec>]\n");
        return 0;
    }

    struct msg_submit_req req;
    memset(&req, 0, sizeof(req));

    /* Support quoted command with arguments such as "./counter 30" */
    const char *sp = strpbrk(argv[1], " \t");
    if (sp != NULL) {
        size_t bin_len = (size_t)(sp - argv[1]);
        if (bin_len >= sizeof(req.binary)) {
            bin_len = sizeof(req.binary) - 1;
        }
        memcpy(req.binary, argv[1], bin_len);
        req.binary[bin_len] = '\0';
        while (*sp == ' ' || *sp == '\t') {
            sp++;
        }
        if (*sp != '\0') {
            snprintf(req.job_args, sizeof(req.job_args), "%s", sp);
        }
    } else {
        snprintf(req.binary, sizeof(req.binary), "%s", argv[1]);
    }

    req.cores = -1;
    req.ram_mb = -1;
    req.time_sec = -1;
    req.prio = -1;
    req.gpu = 0;

    int seen_flag = 0;
    for (int i = 2; i < argc; i++) {
        if (!seen_flag && argv[i][0] != '-') {
            append_job_arg(req.job_args, sizeof(req.job_args), argv[i]);
            continue;
        }
        seen_flag = 1;
        const char *f = norm_flag(argv[i]);
        if (strcmp(f, "-cores") == 0 && i + 1 < argc) {
            req.cores = atoi(argv[++i]);
        } else if (strcmp(f, "-ram") == 0 && i + 1 < argc) {
            req.ram_mb = atoi(argv[++i]);
        } else if (strcmp(f, "-time") == 0 && i + 1 < argc) {
            req.time_sec = atoi(argv[++i]);
        } else if (strcmp(f, "-prio") == 0 && i + 1 < argc) {
            req.prio = atoi(argv[++i]);
        } else if (strcmp(f, "-gpu") == 0 && i + 1 < argc) {
            req.gpu = atoi(argv[++i]);
        } else if (strcmp(f, "-group") == 0 && i + 1 < argc) {
            req.group_id = atoi(argv[++i]);
            if (req.group_id <= 0) {
                printf("[Client] Error: -group requires a positive integer.\n");
                return 0;
            }
        } else if (strcmp(f, "-depends-on") == 0 && i + 1 < argc) {
            snprintf(req.depends_on, sizeof(req.depends_on), "%s", argv[++i]);
        } else if (strcmp(f, "-preemptible") == 0) {
            req.preemptible = 1;
        } else if (strcmp(f, "-every") == 0 && i + 1 < argc) {
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
    int argc = tokenize_command_line(copy, argv, 64);
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
        lreq.follow = (argc >= 3 && strcmp(norm_flag(argv[2]), "-f") == 0) ? 1 : 0;
        if (send_packet(cctx->sock_fd, MSG_CLIENT_LOGS_REQ, &lreq, sizeof(lreq)) < 0) {
            return -1;
        }
        cctx->last_log_char = '\0';
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

    if (strcmp(argv[0], "migrate") == 0) {
        if (argc < 2) {
            printf("[Client] Usage: migrate <job_id>\n");
            return 0;
        }
        int32_t job_id = atoi(argv[1]);
        if (send_packet(cctx->sock_fd, MSG_CLIENT_MIGRATE_REQ, &job_id, sizeof(job_id)) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    if (strcmp(argv[0], "crons") == 0) {
        if (send_packet(cctx->sock_fd, MSG_CLIENT_CRONS_REQ, NULL, 0) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    if (strcmp(argv[0], "cancel-cron") == 0) {
        if (argc < 2) {
            printf("[Client] Usage: cancel-cron <template_id>\n");
            return 0;
        }
        int32_t tid = atoi(argv[1]);
        if (send_packet(cctx->sock_fd, MSG_CLIENT_CANCEL_CRON, &tid, sizeof(tid)) < 0) {
            return -1;
        }
        cctx->waiting_for_reply = 1;
        return 0;
    }

    printf("[Client] Unknown command '%s'. Available: nodes, submit, status, logs, cancel, migrate, crons, cancel-cron\n",
           argv[0]);
    return 0;
}
