#include "worker.h"
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <unistd.h>

#ifdef __APPLE__
#include <sys/sysctl.h>
#endif

static volatile sig_atomic_t g_worker_sigint = 0;

static void worker_sigint_handler(int sig) {
    (void)sig;
    g_worker_sigint = 1;
}

static void get_hardware_limits(int *out_cores, int *out_ram_mb) {
    long nprocs = sysconf(_SC_NPROCESSORS_ONLN);
    if (nprocs <= 0) {
        nprocs = 1;
    }
    *out_cores = (int)nprocs;

    uint64_t mem_bytes = 0;
#ifdef __APPLE__
    size_t len = sizeof(mem_bytes);
    if (sysctlbyname("hw.memsize", &mem_bytes, &len, NULL, 0) != 0) {
        mem_bytes = 4096ULL * 1024ULL * 1024ULL;
    }
#else
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGESIZE);
    if (pages > 0 && page_size > 0) {
        mem_bytes = (uint64_t)pages * (uint64_t)page_size;
    } else {
        mem_bytes = 4096ULL * 1024ULL * 1024ULL;
    }
#endif
    *out_ram_mb = (int)(mem_bytes / (1024ULL * 1024ULL));
}

static void initiate_worker_drain(struct worker_ctx *wctx) {
    if (wctx->is_draining) {
        return;
    }
    wctx->is_draining = 1;
    wctx->drain_announced = 1;
    log_line("[WORKER %d] Draining initiated locally.", wctx->worker_id);
    if (wctx->sock_fd >= 0) {
        send_packet(wctx->sock_fd, MSG_WORKER_DRAIN, NULL, 0);
    }
}

static int connect_and_register_worker(struct worker_ctx *wctx) {
    char target_ip[64] = "";
    int target_port = 0;

    log_line("[WORKER] Looking for scheduler via UDP discovery (port %d)...",
             wctx->discovery_port);
    if (discover_scheduler_udp(wctx->discovery_port, target_ip,
                               sizeof(target_ip), &target_port) == 0) {
        log_line("[WORKER] Scheduler found at %s:%d.", target_ip, target_port);
    } else if (wctx->has_fallback) {
        snprintf(target_ip, sizeof(target_ip), "%s", wctx->fallback_ip);
        target_port = wctx->fallback_port;
        log_line("[WORKER] No discovery reply, using fallback %s:%d.",
                 target_ip, target_port);
    } else {
        log_line("[WORKER] Error: UDP discovery failed and no fallback address provided.");
        return -1;
    }

    log_line("[WORKER] Connecting to scheduler at %s:%d...", target_ip, target_port);
    int fd = connect_tcp(target_ip, target_port);
    if (fd < 0) {
        log_line("[WORKER] Error: failed to connect to scheduler at %s:%d.",
                 target_ip, target_port);
        return -1;
    }

    struct msg_worker_register reg;
    reg.cores = wctx->total_cores;
    reg.ram_mb = wctx->total_ram_mb;
    reg.gpu = wctx->total_gpu;

    if (send_packet(fd, MSG_WORKER_REGISTER, &reg, sizeof(reg)) < 0) {
        close(fd);
        return -1;
    }

    struct packet_header hdr;
    struct msg_worker_reg_ack ack;
    if (recv_header(fd, &hdr) < 0 ||
        hdr.type != MSG_WORKER_REG_ACK ||
        hdr.length != sizeof(ack) ||
        recv_all(fd, &ack, sizeof(ack)) < 0) {
        close(fd);
        return -1;
    }

    wctx->sock_fd = fd;
    wctx->worker_id = ack.worker_id;
    wctx->free_cores = wctx->total_cores;
    wctx->free_ram_mb = wctx->total_ram_mb;
    wctx->free_gpu = wctx->total_gpu;

    log_line("[WORKER %d] Registered successfully. ID: %d. Capacity: %d Cores, %dMB RAM, %d GPU.",
             wctx->worker_id, wctx->worker_id,
             wctx->total_cores, wctx->total_ram_mb, wctx->total_gpu);
    log_line("[WORKER %d] Heartbeat active. Waiting for jobs...", wctx->worker_id);

    /* Section 13: Scan cache/ folder and report existing cached hashes to scheduler */
    send_worker_cache_list(wctx);
    return 0;
}

int main(int argc, char **argv) {
    signal(SIGPIPE, SIG_IGN);

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = worker_sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);

    struct worker_ctx *wctx = calloc(1, sizeof(struct worker_ctx));
    if (wctx == NULL) {
        perror("calloc worker_ctx");
        return 1;
    }
    wctx->sock_fd = -1;
    wctx->discovery_port = DEFAULT_DISCOVERY_PORT;

    int arg_idx = 1;
    if (argc >= 3 && argv[1][0] != '-' && argv[2][0] != '-') {
        wctx->has_fallback = 1;
        snprintf(wctx->fallback_ip, sizeof(wctx->fallback_ip), "%s", argv[1]);
        wctx->fallback_port = atoi(argv[2]);
        arg_idx = 3;
    }

    int req_cores = -1;
    int req_ram_mb = -1;
    int req_gpu = 0;

    for (int i = arg_idx; i < argc; i++) {
        if (strcmp(argv[i], "-cores") == 0 && i + 1 < argc) {
            req_cores = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-ram") == 0 && i + 1 < argc) {
            req_ram_mb = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-gpu") == 0 && i + 1 < argc) {
            req_gpu = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-discovery-port") == 0 && i + 1 < argc) {
            wctx->discovery_port = atoi(argv[++i]);
        } else {
            fprintf(stderr,
                    "Usage: %s [<scheduler_ip> <scheduler_port>] -cores <num> -ram <MB> [-gpu <num>] [-discovery-port <port>]\n",
                    argv[0]);
            free(wctx);
            return 1;
        }
    }

    if (req_cores <= 0 || req_ram_mb <= 0 || req_gpu < 0) {
        fprintf(stderr, "Error: -cores <num> and -ram <MB> are required positive integers.\n");
        free(wctx);
        return 1;
    }

    int hw_cores = 1, hw_ram_mb = 1024;
    get_hardware_limits(&hw_cores, &hw_ram_mb);

    if (req_cores > hw_cores) {
        log_line("[WORKER] Warning: clamping requested cores (%d) to hardware limit (%d).",
                 req_cores, hw_cores);
        req_cores = hw_cores;
    }
    if (req_ram_mb > hw_ram_mb) {
        log_line("[WORKER] Warning: clamping requested RAM (%dMB) to hardware limit (%dMB).",
                 req_ram_mb, hw_ram_mb);
        req_ram_mb = hw_ram_mb;
    }

    wctx->total_cores = req_cores;
    wctx->total_ram_mb = req_ram_mb;
    wctx->total_gpu = req_gpu;
    wctx->is_root = (geteuid() == 0) ? 1 : 0;

    if (!wctx->is_root) {
        log_line("[WORKER] Warning: worker not running as root (sudo). Jobs will run without privilege-dropping to 'nobody'.");
    }

    init_worker_cache(wctx);

    if (connect_and_register_worker(wctx) < 0) {
        free(wctx);
        return 1;
    }

    int stdin_open = 1;
    time_t last_hb = time(NULL);

    while (1) {
        if (g_worker_sigint) {
            g_worker_sigint = 0;
            initiate_worker_drain(wctx);
        }

        poll_active_jobs(wctx);

        if (wctx->is_draining && count_worker_active_jobs(wctx) == 0) {
            log_line("[WORKER %d] Drain complete (0 active jobs). Exiting gracefully.",
                     wctx->worker_id);
            close(wctx->sock_fd);
            break;
        }

        time_t now = time(NULL);
        if (now - last_hb >= HEARTBEAT_INTERVAL_SEC) {
            last_hb = now;
            send_worker_heartbeat(wctx);
        }

        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(wctx->sock_fd, &rfds);
        int max_fd = wctx->sock_fd;

        if (stdin_open) {
            FD_SET(STDIN_FILENO, &rfds);
            if (STDIN_FILENO > max_fd) {
                max_fd = STDIN_FILENO;
            }
        }

        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 300000; /* ~300ms poll interval for 500ms output/checkpoint watching */

        int ready = select(max_fd + 1, &rfds, NULL, NULL, &tv);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            break;
        }

        if (ready > 0) {
            if (stdin_open && FD_ISSET(STDIN_FILENO, &rfds)) {
                char line[128];
                if (fgets(line, sizeof(line), stdin) == NULL) {
                    stdin_open = 0;
                } else {
                    char *nl = strchr(line, '\n');
                    if (nl != NULL) {
                        *nl = '\0';
                    }
                    if (strcmp(line, "drain") == 0) {
                        initiate_worker_drain(wctx);
                    }
                }
            }

            if (FD_ISSET(wctx->sock_fd, &rfds)) {
                struct packet_header hdr;
                if (recv_header(wctx->sock_fd, &hdr) < 0) {
                    /* Section 2B: On connection loss, kill running jobs and re-register */
                    close(wctx->sock_fd);
                    wctx->sock_fd = -1;
                    kill_all_active_jobs(wctx);
                    if (wctx->is_draining) {
                        break;
                    }
                    log_line("[WORKER] Lost connection to scheduler. Attempting to reconnect...");
                    if (connect_and_register_worker(wctx) < 0) {
                        break;
                    }
                    last_hb = time(NULL);
                    continue;
                }

                switch (hdr.type) {
                    case MSG_SCHED_EXEC_CACHED: {
                        struct msg_exec_cached ec;
                        if (hdr.length == sizeof(ec)) {
                            recv_all(wctx->sock_fd, &ec, sizeof(ec));
                        }
                        break;
                    }
                    case MSG_SCHED_BINARY_CHUNK:
                        handle_binary_chunk(wctx, &hdr);
                        break;
                    case MSG_SCHED_CKPT_DATA:
                        handle_checkpoint_data(wctx, &hdr);
                        break;
                    case MSG_SCHED_ASSIGN_JOB: {
                        struct msg_assign_job assign;
                        if (hdr.length == sizeof(assign) &&
                            recv_all(wctx->sock_fd, &assign, sizeof(assign)) == 0) {
                            launch_job_process(wctx, &assign);
                        }
                        break;
                    }
                    case MSG_SCHED_STOP_JOB: {
                        struct msg_stop_job stop_cmd;
                        if (hdr.length == sizeof(stop_cmd) &&
                            recv_all(wctx->sock_fd, &stop_cmd, sizeof(stop_cmd)) == 0) {
                            stop_active_job(wctx, stop_cmd.job_id, stop_cmd.reason);
                        }
                        break;
                    }
                    default: {
                        if (hdr.length > 0) {
                            char *skip = malloc((size_t)hdr.length);
                            if (skip != NULL) {
                                recv_all(wctx->sock_fd, skip, (size_t)hdr.length);
                                free(skip);
                            }
                        }
                        break;
                    }
                }
            }
        }
    }

    kill_all_active_jobs(wctx);
    free(wctx->pending_ckpt.data);
    free(wctx);
    return 0;
}
