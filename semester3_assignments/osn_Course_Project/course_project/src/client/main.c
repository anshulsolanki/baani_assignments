#include "client.h"
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <unistd.h>

static volatile sig_atomic_t g_client_sigint = 0;

static void client_sigint_handler(int sig) {
    (void)sig;
    g_client_sigint = 1;
}

static int connect_and_login_client(struct client_ctx *cctx, int is_reconnect) {
    char target_ip[64] = "";
    int target_port = 0;

    if (discover_scheduler_udp(cctx->discovery_port, target_ip,
                               sizeof(target_ip), &target_port) != 0) {
        if (cctx->has_fallback) {
            snprintf(target_ip, sizeof(target_ip), "%s", cctx->fallback_ip);
            target_port = cctx->fallback_port;
            printf("No discovery reply, using fallback %s:%d.\n",
                   target_ip, target_port);
            fflush(stdout);
        } else {
            fprintf(stderr, "[Client] Error: UDP discovery failed and no fallback IP:port provided.\n");
            return -1;
        }
    }

    int fd = connect_tcp(target_ip, target_port);
    if (fd < 0) {
        fprintf(stderr, "[Client] Error: failed to connect to Scheduler at %s:%d.\n",
                target_ip, target_port);
        return -1;
    }

    cctx->sock_fd = fd;
    if (!is_reconnect) {
        printf("[Client] Connected to Scheduler.\n");
        fflush(stdout);
    }

    while (!is_valid_username(cctx->username)) {
        printf("Username: ");
        fflush(stdout);
        char line[128];
        if (fgets(line, sizeof(line), stdin) == NULL) {
            close(fd);
            return -1;
        }
        char *nl = strpbrk(line, "\r\n");
        if (nl != NULL) {
            *nl = '\0';
        }
        if (is_valid_username(line)) {
            snprintf(cctx->username, sizeof(cctx->username), "%s", line);
        } else {
            printf("[Client] Invalid username (must be 1..31 chars of letters, digits, '_', '-', '.').\n");
            fflush(stdout);
        }
    }

    struct msg_client_login login;
    memset(&login, 0, sizeof(login));
    snprintf(login.username, sizeof(login.username), "%s", cctx->username);
    if (send_packet(fd, MSG_CLIENT_LOGIN, &login, sizeof(login)) < 0) {
        close(fd);
        return -1;
    }

    struct packet_header hdr;
    if (recv_header(fd, &hdr) < 0 || hdr.type != MSG_CLIENT_LOGIN_ACK) {
        close(fd);
        return -1;
    }
    if (hdr.length > 0) {
        char ack_buf[128];
        recv_all(fd, ack_buf, (size_t)hdr.length);
    }

    if (!is_reconnect) {
        printf("Logged in as %s.\n", cctx->username);
        fflush(stdout);
    }
    return 0;
}

int main(int argc, char **argv) {
    signal(SIGPIPE, SIG_IGN);

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = client_sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);

    struct client_ctx cctx;
    memset(&cctx, 0, sizeof(cctx));
    cctx.sock_fd = -1;
    cctx.discovery_port = DEFAULT_DISCOVERY_PORT;

    for (int i = 1; i < argc; i++) {
        const char *f = (argv[i][0] == '-' && argv[i][1] == '-' && argv[i][2] != '\0')
                            ? (argv[i] + 1)
                            : argv[i];
        if (strcmp(f, "-user") == 0 && i + 1 < argc) {
            const char *u = argv[++i];
            if (is_valid_username(u)) {
                snprintf(cctx.username, sizeof(cctx.username), "%s", u);
            } else {
                fprintf(stderr, "[Client] Warning: invalid -user '%s', will prompt interactively.\n", u);
            }
        } else if (strcmp(f, "-discovery-port") == 0 && i + 1 < argc) {
            cctx.discovery_port = atoi(argv[++i]);
        } else if (!cctx.has_fallback && argv[i][0] != '-' &&
                   i + 1 < argc && argv[i + 1][0] != '-') {
            cctx.has_fallback = 1;
            snprintf(cctx.fallback_ip, sizeof(cctx.fallback_ip), "%s", argv[i]);
            cctx.fallback_port = atoi(argv[++i]);
        } else {
            fprintf(stderr,
                    "Usage: %s [<scheduler_ip> <scheduler_port>] [-user <username>] [-discovery-port <port>]\n",
                    argv[0]);
            return 1;
        }
    }

    if (connect_and_login_client(&cctx, 0) < 0) {
        return 1;
    }

    int stdin_eof = 0;

    while (1) {
        if (g_client_sigint) {
            g_client_sigint = 0;
            if (cctx.in_follow_mode) {
                /* Section 3 & 6: Ctrl+C during logs -f returns to prompt without exiting client */
                send_packet(cctx.sock_fd, MSG_CLIENT_LOGS_UNSUB, NULL, 0);
                cctx.in_follow_mode = 0;
                cctx.waiting_for_logs = 0;
                cctx.last_log_char = '\0';
                cctx.prompt_shown = 0;
                printf("\n");
                fflush(stdout);
            } else {
                printf("\n");
                break;
            }
        }

        if (!cctx.waiting_for_reply && !cctx.waiting_for_logs &&
            !cctx.in_follow_mode && !stdin_eof && !cctx.prompt_shown) {
            printf("client> ");
            fflush(stdout);
            cctx.prompt_shown = 1;
        }

        if (stdin_eof && !cctx.waiting_for_reply && !cctx.waiting_for_logs && !cctx.in_follow_mode) {
            break;
        }

        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(cctx.sock_fd, &rfds);
        int max_fd = cctx.sock_fd;

        if (!stdin_eof && !cctx.waiting_for_reply && !cctx.waiting_for_logs && !cctx.in_follow_mode) {
            FD_SET(STDIN_FILENO, &rfds);
            if (STDIN_FILENO > max_fd) {
                max_fd = STDIN_FILENO;
            }
        }

        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 200000;

        int ready = select(max_fd + 1, &rfds, NULL, NULL, &tv);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            break;
        }

        if (ready > 0 && FD_ISSET(cctx.sock_fd, &rfds)) {
            struct packet_header hdr;
            if (recv_header(cctx.sock_fd, &hdr) < 0) {
                close(cctx.sock_fd);
                cctx.sock_fd = -1;
                if (stdin_eof) {
                    break;
                }
                /* Reconnect and auto-login without prompting (Section 3) */
                if (connect_and_login_client(&cctx, 1) < 0) {
                    break;
                }
                cctx.waiting_for_reply = 0;
                cctx.waiting_for_logs = 0;
                cctx.in_follow_mode = 0;
                cctx.last_log_char = '\0';
                cctx.prompt_shown = 0;
                continue;
            }

            char *payload = NULL;
            if (hdr.length > 0) {
                payload = malloc((size_t)hdr.length + 1);
                if (payload == NULL || recv_all(cctx.sock_fd, payload, (size_t)hdr.length) < 0) {
                    free(payload);
                    break;
                }
                payload[hdr.length] = '\0';
            }

            if (hdr.type == MSG_SCHED_EVENT) {
                if (cctx.prompt_shown) {
                    printf("\n");
                    cctx.prompt_shown = 0;
                }
                if (payload != NULL) {
                    printf("%s\n", payload);
                    fflush(stdout);
                }
            } else if (hdr.type == MSG_SCHED_REPLY) {
                if (payload != NULL) {
                    printf("%s\n", payload);
                    fflush(stdout);
                }
                cctx.waiting_for_reply = 0;
                cctx.prompt_shown = 0;
            } else if (hdr.type == MSG_SCHED_LOG_CHUNK) {
                if (payload != NULL && hdr.length > 0) {
                    fwrite(payload, 1, (size_t)hdr.length, stdout);
                    fflush(stdout);
                    cctx.last_log_char = payload[hdr.length - 1];
                }
            } else if (hdr.type == MSG_SCHED_LOG_EOF) {
                if (cctx.last_log_char != '\0' && cctx.last_log_char != '\n') {
                    printf("\n");
                    fflush(stdout);
                }
                if (payload != NULL && payload[0] != '\0') {
                    printf("%s\n", payload);
                    fflush(stdout);
                }
                cctx.last_log_char = '\0';
                cctx.waiting_for_logs = 0;
                cctx.in_follow_mode = 0;
                cctx.prompt_shown = 0;
            }

            free(payload);
        }

        if (ready > 0 && !stdin_eof && !cctx.waiting_for_reply &&
            !cctx.waiting_for_logs && !cctx.in_follow_mode &&
            FD_ISSET(STDIN_FILENO, &rfds)) {
            char line[1024];
            if (fgets(line, sizeof(line), stdin) == NULL) {
                stdin_eof = 1;
            } else {
                cctx.prompt_shown = 0;
                int rc = execute_client_command(&cctx, line);
                if (rc != 0) {
                    break;
                }
            }
        }
    }

    if (cctx.sock_fd >= 0) {
        close(cctx.sock_fd);
    }
    return 0;
}
