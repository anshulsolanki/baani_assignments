#include "scheduler.h"
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#define MAX_PENDING_CONNS 64

static void print_usage(const char *prog) {
    fprintf(stderr, "Usage: %s <port> <FIFO|PRIORITY> [-discovery-port <port>]\n", prog);
}

int main(int argc, char **argv) {
    signal(SIGPIPE, SIG_IGN);

    if (argc < 3) {
        print_usage(argv[0]);
        return 1;
    }

    int tcp_port = atoi(argv[1]);
    if (tcp_port <= 0 || tcp_port > 65535) {
        fprintf(stderr, "Invalid TCP port: %s\n", argv[1]);
        return 1;
    }

    int algo = -1;
    if (strcmp(argv[2], "FIFO") == 0) {
        algo = ALGO_FIFO;
    } else if (strcmp(argv[2], "PRIORITY") == 0) {
        algo = ALGO_PRIORITY;
    } else {
        fprintf(stderr, "Invalid scheduling algorithm '%s' (expected FIFO or PRIORITY)\n", argv[2]);
        return 1;
    }

    int discovery_port = DEFAULT_DISCOVERY_PORT;
    for (int i = 3; i < argc; i++) {
        if (strcmp(argv[i], "-discovery-port") == 0 && i + 1 < argc) {
            discovery_port = atoi(argv[++i]);
        } else {
            print_usage(argv[0]);
            return 1;
        }
    }

    struct scheduler_ctx *ctx = calloc(1, sizeof(struct scheduler_ctx));
    if (ctx == NULL) {
        perror("calloc scheduler_ctx");
        return 1;
    }

    ctx->tcp_port = tcp_port;
    ctx->discovery_port = discovery_port;
    ctx->algo = algo;
    ctx->next_worker_id = 1001;
    ctx->next_job_id = 1;
    ctx->next_cron_id = 1;

    ctx->tcp_listen_fd = create_tcp_server(tcp_port);
    if (ctx->tcp_listen_fd < 0) {
        perror("create_tcp_server");
        free(ctx);
        return 1;
    }

    ctx->udp_disc_fd = create_udp_discovery_server(discovery_port);
    if (ctx->udp_disc_fd < 0) {
        perror("create_udp_discovery_server");
        close(ctx->tcp_listen_fd);
        free(ctx);
        return 1;
    }

    log_line("[SCHEDULER] Started on port %d. Algorithm: %s",
             tcp_port, (algo == ALGO_FIFO) ? "FIFO" : "PRIORITY");
    log_line("[SCHEDULER] Discovery responder listening on UDP port %d.",
             discovery_port);
    log_line("[SCHEDULER] Listening for incoming connections...");

    int pending_fds[MAX_PENDING_CONNS];
    for (int i = 0; i < MAX_PENDING_CONNS; i++) {
        pending_fds[i] = -1;
    }

    time_t last_tick = time(NULL);

    while (1) {
        fd_set rfds;
        FD_ZERO(&rfds);

        FD_SET(ctx->tcp_listen_fd, &rfds);
        FD_SET(ctx->udp_disc_fd, &rfds);
        int max_fd = (ctx->tcp_listen_fd > ctx->udp_disc_fd)
                         ? ctx->tcp_listen_fd
                         : ctx->udp_disc_fd;

        for (int i = 0; i < MAX_PENDING_CONNS; i++) {
            if (pending_fds[i] >= 0) {
                FD_SET(pending_fds[i], &rfds);
                if (pending_fds[i] > max_fd) {
                    max_fd = pending_fds[i];
                }
            }
        }

        for (int i = 0; i < MAX_WORKERS; i++) {
            if (ctx->workers[i].used && ctx->workers[i].sock_fd >= 0) {
                int fd = ctx->workers[i].sock_fd;
                FD_SET(fd, &rfds);
                if (fd > max_fd) {
                    max_fd = fd;
                }
            }
        }

        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (ctx->clients[i].used && ctx->clients[i].sock_fd >= 0) {
                int fd = ctx->clients[i].sock_fd;
                FD_SET(fd, &rfds);
                if (fd > max_fd) {
                    max_fd = fd;
                }
            }
        }

        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 250000; /* 250ms poll for responsive 1s ticks */

        int ready = select(max_fd + 1, &rfds, NULL, NULL, &tv);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("select");
            break;
        }

        if (ready > 0) {
            /* 1. UDP discovery request */
            if (FD_ISSET(ctx->udp_disc_fd, &rfds)) {
                handle_udp_discovery_request(ctx->udp_disc_fd, ctx->tcp_port);
            }

            /* 2. New TCP connection */
            if (FD_ISSET(ctx->tcp_listen_fd, &rfds)) {
                struct sockaddr_in cli_addr;
                socklen_t cli_len = sizeof(cli_addr);
                int new_fd = accept(ctx->tcp_listen_fd,
                                    (struct sockaddr *)&cli_addr, &cli_len);
                if (new_fd >= 0) {
                    int placed = 0;
                    for (int i = 0; i < MAX_PENDING_CONNS; i++) {
                        if (pending_fds[i] < 0) {
                            pending_fds[i] = new_fd;
                            placed = 1;
                            break;
                        }
                    }
                    if (!placed) {
                        close(new_fd);
                    }
                }
            }

            /* 3. Unclassified connections sending first packet (REGISTER or LOGIN) */
            for (int i = 0; i < MAX_PENDING_CONNS; i++) {
                int fd = pending_fds[i];
                if (fd >= 0 && FD_ISSET(fd, &rfds)) {
                    pending_fds[i] = -1;
                    handle_initial_connection_packet(ctx, fd);
                }
            }

            /* 4. Connected workers */
            for (int i = 0; i < MAX_WORKERS; i++) {
                struct worker_node *w = &ctx->workers[i];
                if (w->used && w->sock_fd >= 0 && FD_ISSET(w->sock_fd, &rfds)) {
                    struct packet_header hdr;
                    if (recv_header(w->sock_fd, &hdr) < 0) {
                        handle_worker_disconnect(ctx, w);
                    } else {
                        handle_worker_message(ctx, w, &hdr);
                    }
                }
            }

            /* 5. Connected clients */
            for (int i = 0; i < MAX_CLIENTS; i++) {
                struct client_session *cs = &ctx->clients[i];
                if (cs->used && cs->sock_fd >= 0 && FD_ISSET(cs->sock_fd, &rfds)) {
                    struct packet_header hdr;
                    if (recv_header(cs->sock_fd, &hdr) < 0) {
                        handle_client_disconnect(ctx, cs);
                    } else {
                        handle_client_message(ctx, cs, &hdr);
                    }
                }
            }
        }

        /* Periodic 1-second tick for cron, heartbeats, dependencies, and scheduling */
        time_t now = time(NULL);
        if (now > last_tick) {
            last_tick = now;
            cron_tick(ctx);
            check_worker_heartbeats(ctx);
            check_job_dependencies(ctx);
            schedule_jobs(ctx);
        }
    }

    close(ctx->udp_disc_fd);
    close(ctx->tcp_listen_fd);
    free(ctx);
    return 0;
}
