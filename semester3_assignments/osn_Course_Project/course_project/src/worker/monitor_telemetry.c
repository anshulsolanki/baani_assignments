#include "worker.h"
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#ifdef __APPLE__
#include <libproc.h>
#endif

static void read_process_telemetry(pid_t pid, int *out_rss_mb,
                                   int *out_faults, double *out_cpu_sec) {
    *out_rss_mb = 0;
    *out_faults = 0;
    *out_cpu_sec = 0.0;

#ifdef __APPLE__
    struct proc_taskinfo ti;
    int ret = proc_pidinfo(pid, PROC_PIDTASKINFO, 0, &ti, sizeof(ti));
    if (ret == (int)sizeof(ti)) {
        *out_rss_mb = (int)((ti.pti_resident_size + (1024ULL * 1024ULL - 1)) /
                            (1024ULL * 1024ULL));
        *out_faults = (int)ti.pti_faults;
        *out_cpu_sec = (double)(ti.pti_total_user + ti.pti_total_system) / 1e9;
    }
#else
    char path[128];
    snprintf(path, sizeof(path), "/proc/%d/statm", (int)pid);
    FILE *fm = fopen(path, "r");
    if (fm != NULL) {
        unsigned long size_pages = 0, resident_pages = 0;
        if (fscanf(fm, "%lu %lu", &size_pages, &resident_pages) == 2) {
            long page_sz = sysconf(_SC_PAGESIZE);
            if (page_sz <= 0) {
                page_sz = 4096;
            }
            unsigned long long bytes = (unsigned long long)resident_pages *
                                       (unsigned long long)page_sz;
            *out_rss_mb = (int)((bytes + (1024ULL * 1024ULL - 1)) / (1024ULL * 1024ULL));
        }
        fclose(fm);
    }

    snprintf(path, sizeof(path), "/proc/%d/stat", (int)pid);
    FILE *fs = fopen(path, "r");
    if (fs != NULL) {
        char line[1024];
        if (fgets(line, sizeof(line), fs) != NULL) {
            char *rparen = strrchr(line, ')');
            if (rparen != NULL && rparen[1] == ' ') {
                char state_ch = 0;
                unsigned long minflt = 0, cminflt = 0, majflt = 0, cmajflt = 0;
                unsigned long utime = 0, stime = 0;
                int matched = sscanf(rparen + 2,
                                     "%c %*d %*d %*d %*d %*d %*u %lu %lu %lu %lu %lu %lu",
                                     &state_ch, &minflt, &cminflt, &majflt, &cmajflt,
                                     &utime, &stime);
                if (matched == 7) {
                    *out_faults = (int)(minflt + majflt);
                    long clk = sysconf(_SC_CLK_TCK);
                    if (clk <= 0) {
                        clk = 100;
                    }
                    *out_cpu_sec = (double)(utime + stime) / (double)clk;
                }
            }
        }
        fclose(fs);
    }
#endif
}

static void drain_job_output(struct worker_ctx *wctx, struct active_job *aj) {
    if (aj->log_read_fd < 0) {
        return;
    }

    uint8_t buf[sizeof(struct msg_job_output_hdr) + 4096];
    char *text_ptr = (char *)(buf + sizeof(struct msg_job_output_hdr));

    ssize_t n = 0;
    while ((n = read(aj->log_read_fd, text_ptr, 4096)) > 0) {
        struct msg_job_output_hdr hdr;
        hdr.job_id = aj->job_id;
        hdr.text_len = (int32_t)n;
        memcpy(buf, &hdr, sizeof(hdr));
        send_packet(wctx->sock_fd, MSG_WORKER_JOB_OUTPUT,
                    buf, (int32_t)sizeof(hdr) + (int32_t)n);
    }
}

/*
 * Section 5E: Crash diagnosis turning waitpid() status or worker kill_reason into plain words.
 */
static void diagnose_job_exit(const struct active_job *aj, int status,
                              struct msg_job_done *done) {
    done->exit_code = 0;
    done->term_signal = 0;

    if (aj->kill_reason == KILL_CANCEL) {
        done->outcome = OUTCOME_CANCELLED;
        snprintf(done->diagnosis, sizeof(done->diagnosis), "Cancelled by user.");
        return;
    }
    if (aj->kill_reason == KILL_PREEMPT) {
        done->outcome = OUTCOME_PREEMPTED;
        snprintf(done->diagnosis, sizeof(done->diagnosis),
                 "Preempted for higher-priority job.");
        return;
    }
    if (aj->kill_reason == KILL_MIGRATE) {
        done->outcome = OUTCOME_MIGRATED;
        snprintf(done->diagnosis, sizeof(done->diagnosis),
                 "Migrated to another worker.");
        return;
    }
    if (aj->kill_reason == KILL_TIMEOUT) {
        done->outcome = OUTCOME_FAILED;
        snprintf(done->diagnosis, sizeof(done->diagnosis),
                 "Wall-clock timeout exceeded (%ds limit).", aj->time_limit_sec);
        return;
    }
    if (aj->kill_reason == KILL_MEMORY) {
        done->outcome = OUTCOME_FAILED;
        snprintf(done->diagnosis, sizeof(done->diagnosis),
                 "Memory limit exceeded (%dMB limit).", aj->ram_mb);
        return;
    }

    if (WIFSIGNALED(status)) {
        int sig = WTERMSIG(status);
        done->term_signal = sig;
        done->outcome = OUTCOME_FAILED;

        if (sig == SIGXCPU) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Wall-clock timeout exceeded (%ds limit).", aj->time_limit_sec);
        } else if (sig == SIGABRT) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d (SIGABRT - Aborted).", sig);
        } else if (sig == SIGBUS) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d (SIGBUS - Bus Error).", sig);
        } else if (sig == SIGILL) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d (SIGILL - Illegal Instruction).", sig);
        } else if (sig == SIGKILL) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d (SIGKILL - Killed).", sig);
        } else if (sig == SIGTERM) {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d (SIGTERM - Terminated).", sig);
        } else {
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Terminated by signal %d.", sig);
        }
        return;
    }

    if (WIFEXITED(status)) {
        int code = WEXITSTATUS(status);
        done->exit_code = code;
        if (code == 0) {
            done->outcome = OUTCOME_COMPLETED;
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Exited with code 0.");
        } else if (code == 127) {
            done->outcome = OUTCOME_FAILED;
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Exited with code 127 (command not found).");
        } else if (code == 126) {
            done->outcome = OUTCOME_FAILED;
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Exited with code 126 (cannot execute / privilege drop failed).");
        } else {
            done->outcome = OUTCOME_FAILED;
            snprintf(done->diagnosis, sizeof(done->diagnosis),
                     "Exited with code %d.", code);
        }
        return;
    }

    done->outcome = OUTCOME_FAILED;
    snprintf(done->diagnosis, sizeof(done->diagnosis), "Terminated abnormally.");
}

void stop_active_job(struct worker_ctx *wctx, int job_id, int stop_reason) {
    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        struct active_job *aj = &wctx->jobs[i];
        if (!aj->used || aj->job_id != job_id) {
            continue;
        }

        if (stop_reason == STOP_CANCEL) {
            aj->kill_reason = KILL_CANCEL;
            kill(-aj->pid, SIGKILL);
            kill(aj->pid, SIGKILL);
            log_line("[WORKER %d] Killing Job %d (cancelled)", wctx->worker_id, job_id);
        } else if (stop_reason == STOP_PREEMPT) {
            aj->kill_reason = KILL_PREEMPT;
            kill(-aj->pid, SIGKILL);
            kill(aj->pid, SIGKILL);
            log_line("[WORKER %d] Killing Job %d (preempted)", wctx->worker_id, job_id);
        } else if (stop_reason == STOP_MIGRATE) {
            /* Section 14: Send SIGTERM first so job can save one last checkpoint, then SIGKILL after 2s */
            aj->kill_reason = KILL_MIGRATE;
            aj->migrate_sigterm_time = time(NULL);
            kill(-aj->pid, SIGTERM);
            kill(aj->pid, SIGTERM);
            log_line("[WORKER %d] Sent SIGTERM to Job %d for live migration", wctx->worker_id, job_id);
        }
        return;
    }
}

void poll_active_jobs(struct worker_ctx *wctx) {
    time_t now = time(NULL);

    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        struct active_job *aj = &wctx->jobs[i];
        if (!aj->used) {
            continue;
        }

        /* 1. Stream any new output from output.log (Section 5B & 6) */
        drain_job_output(wctx, aj);

        /* 2. Check if $OSN_CHECKPOINT_DIR/state changed (Section 14) */
        check_job_checkpoint_file(wctx, aj);

        /* 3. Read live RSS, page faults, and CPU time (Section 5D) */
        int rss_mb = 0, faults = 0;
        double cpu_sec = 0.0;
        read_process_telemetry(aj->pid, &rss_mb, &faults, &cpu_sec);
        if (rss_mb > 0 || faults > 0 || cpu_sec > 0.0) {
            aj->current_ram_mb = rss_mb;
            if (rss_mb > aj->peak_ram_mb) {
                aj->peak_ram_mb = rss_mb;
            }
            aj->page_faults = faults;
            aj->cpu_time_sec = cpu_sec;
        }

        /* 4. Enforce memory limit, wall-clock timeout, or 2s migration SIGKILL escalation */
        if (aj->kill_reason == KILL_MIGRATE && aj->migrate_sigterm_time > 0) {
            if (now - aj->migrate_sigterm_time >= 2) {
                kill(-aj->pid, SIGKILL);
                kill(aj->pid, SIGKILL);
            }
        } else if (aj->kill_reason == KILL_NONE) {
            if (aj->current_ram_mb > aj->ram_mb) {
                aj->kill_reason = KILL_MEMORY;
                kill(-aj->pid, SIGKILL);
                kill(aj->pid, SIGKILL);
                log_line("[WORKER %d] Job %d exceeded RAM limit (%dMB > %dMB), sending SIGKILL",
                         wctx->worker_id, aj->job_id, aj->current_ram_mb, aj->ram_mb);
            } else if (now - aj->start_time >= aj->time_limit_sec) {
                aj->kill_reason = KILL_TIMEOUT;
                kill(-aj->pid, SIGKILL);
                kill(aj->pid, SIGKILL);
                log_line("[WORKER %d] Job %d exceeded wall-clock timeout (%ds), sending SIGKILL",
                         wctx->worker_id, aj->job_id, aj->time_limit_sec);
            }
        }

        /* 5. Reap exited child process without blocking */
        int status = 0;
        pid_t wpid = waitpid(aj->pid, &status, WNOHANG);
        if (wpid == aj->pid) {
            kill(-aj->pid, SIGKILL);

            /* Drain remainder of output.log and read final checkpoint state ONE more time */
            drain_job_output(wctx, aj);
            check_job_checkpoint_file(wctx, aj);

            struct msg_job_done done;
            memset(&done, 0, sizeof(done));
            done.job_id = aj->job_id;
            done.peak_ram_mb = aj->peak_ram_mb;
            done.page_faults = aj->page_faults;
            done.cpu_time_sec = aj->cpu_time_sec;
            diagnose_job_exit(aj, status, &done);

            if (done.outcome == OUTCOME_FAILED) {
                log_line("[ERROR] Job %d Failed. Diagnosis: %s",
                         aj->job_id, done.diagnosis);
            } else if (done.outcome == OUTCOME_COMPLETED) {
                log_line("[WORKER %d] Job %d COMPLETED.", wctx->worker_id, aj->job_id);
            }

            send_packet(wctx->sock_fd, MSG_WORKER_JOB_DONE, &done, sizeof(done));

            if (aj->log_read_fd >= 0) {
                close(aj->log_read_fd);
                aj->log_read_fd = -1;
            }
            cleanup_job_directory(aj->job_dir);

            wctx->free_cores += aj->cores;
            wctx->free_ram_mb += aj->ram_mb;
            wctx->free_gpu += aj->gpu;
            aj->used = 0;
        }
    }
}

int count_worker_active_jobs(const struct worker_ctx *wctx) {
    int count = 0;
    for (int i = 0; i < MAX_WORKER_JOBS; i++) {
        if (wctx->jobs[i].used) {
            count++;
        }
    }
    return count;
}

int compute_worker_cpu_load_pct(int total_cores) {
    double load[1] = { 0.0 };
    if (getloadavg(load, 1) < 0 || total_cores <= 0) {
        return 0;
    }
    int pct = (int)((load[0] / (double)total_cores) * 100.0);
    if (pct < 0) {
        pct = 0;
    }
    if (pct > 100) {
        pct = 100;
    }
    return pct;
}

void send_worker_heartbeat(struct worker_ctx *wctx) {
    struct msg_worker_heartbeat hb;
    memset(&hb, 0, sizeof(hb));
    hb.worker_id = wctx->worker_id;
    hb.cpu_load_pct = compute_worker_cpu_load_pct(wctx->total_cores);
    hb.free_cores = wctx->free_cores;
    hb.free_ram_mb = wctx->free_ram_mb;
    hb.free_gpu = wctx->free_gpu;

    int count = 0;
    for (int i = 0; i < MAX_WORKER_JOBS && count < MAX_WORKER_JOBS; i++) {
        const struct active_job *aj = &wctx->jobs[i];
        if (!aj->used) {
            continue;
        }
        hb.jobs[count].job_id = aj->job_id;
        hb.jobs[count].current_ram_mb = aj->current_ram_mb;
        hb.jobs[count].peak_ram_mb = aj->peak_ram_mb;
        hb.jobs[count].page_faults = aj->page_faults;
        hb.jobs[count].cpu_time_sec = aj->cpu_time_sec;
        count++;
    }
    hb.active_jobs = count;

    send_packet(wctx->sock_fd, MSG_WORKER_HEARTBEAT, &hb, sizeof(hb));
}
