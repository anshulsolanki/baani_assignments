#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "cluster_protocol.h"
#include "net_utils.h"
#include <stdint.h>
#include <time.h>

struct job_entry {
    int used;
    int id;
    char user[MAX_USERNAME_LEN];
    char binary[MAX_PATH_STR];
    char job_args[MAX_PATH_STR];
    char exec_name[MAX_NAME_STR];
    char sha1_hash[SHA1_HEX_LEN];
    int32_t binary_size;
    int is_local_file;

    int cores;
    int ram_mb;
    int gpu;
    int time_sec;
    int base_prio;
    int eff_prio;

    time_t submit_time;
    time_t queued_since;

    int state;
    int worker_id;
    int attempts;

    int group_id;
    int deps[MAX_DEPS_PER_JOB];
    int num_deps;

    int preemptible;
    int preempt_pending;
    int hold_for_job_id;

    int cron_id;
    int cron_run_no;

    int migrate_pending;
    int avoid_worker_id;

    uint8_t *ckpt_data;
    int32_t ckpt_len;
    int ckpt_count;
    time_t ckpt_time;

    int current_ram_mb;
    int peak_ram_mb;
    int page_faults;
    double cpu_time_sec;
    char diagnosis[256];

    char *log_buf;
    int log_len;
};

struct worker_node {
    int used;
    int id;
    int sock_fd;
    int state;
    time_t last_heartbeat;

    int total_cores;
    int free_cores;
    int total_ram_mb;
    int free_ram_mb;
    int total_gpu;
    int free_gpu;

    int cpu_load_pct;
    int running_jobs;

    int num_cached;
    char cached_hashes[MAX_WORKER_CACHE][SHA1_HEX_LEN];
};

struct client_session {
    int used;
    int sock_fd;
    char username[MAX_USERNAME_LEN];
    int logged_in;
    int follow_job_id;
};

struct cron_template {
    int used;
    int id;
    int active;
    char user[MAX_USERNAME_LEN];
    char binary[MAX_PATH_STR];
    char job_args[MAX_PATH_STR];
    int cores;
    int ram_mb;
    int gpu;
    int time_sec;
    int prio;
    int group_id;
    int preemptible;
    int every_sec;
    int runs;
    time_t next_due;
};

struct scheduler_ctx {
    int tcp_port;
    int discovery_port;
    int algo;
    int tcp_listen_fd;
    int udp_disc_fd;

    int next_worker_id;
    int next_job_id;
    int next_cron_id;

    struct worker_node workers[MAX_WORKERS];
    struct client_session clients[MAX_CLIENTS];
    struct job_entry jobs[MAX_JOBS_TOTAL];
    struct cron_template crons[MAX_CRON_TEMPLATES];
};

/* worker_registry.c */
struct worker_node *find_worker_by_fd(struct scheduler_ctx *ctx, int fd);
struct worker_node *find_worker_by_id(struct scheduler_ctx *ctx, int worker_id);
int worker_has_hash(const struct worker_node *w, const char *hash);
void worker_add_hash(struct worker_node *w, const char *hash);
void worker_remove_hash(struct worker_node *w, const char *hash);
void handle_worker_message(struct scheduler_ctx *ctx, struct worker_node *w,
                           const struct packet_header *hdr);
void handle_worker_disconnect(struct scheduler_ctx *ctx, struct worker_node *w);
void check_worker_heartbeats(struct scheduler_ctx *ctx);

/* job_manager.c */
struct job_entry *find_job_by_id(struct scheduler_ctx *ctx, int job_id);
int count_queued_jobs(const struct scheduler_ctx *ctx);
void append_job_log(struct scheduler_ctx *ctx, struct job_entry *j,
                    const char *data, int len);
void notify_job_followers_eof(struct scheduler_ctx *ctx, int job_id);
void notify_user_event(struct scheduler_ctx *ctx, const char *username,
                       const char *fmt, ...);
void check_job_dependencies(struct scheduler_ctx *ctx);
void cron_tick(struct scheduler_ctx *ctx);
struct job_entry *create_job_record(struct scheduler_ctx *ctx,
                                    const char *username,
                                    const struct msg_submit_req *req,
                                    const int *deps, int num_deps,
                                    int cron_id, int cron_run_no);

/* scheduler_pass.c */
void schedule_jobs(struct scheduler_ctx *ctx);
int dispatch_job_to_worker(struct scheduler_ctx *ctx, struct job_entry *j,
                           struct worker_node *w);

/* client_handler.c */
struct client_session *find_client_by_fd(struct scheduler_ctx *ctx, int fd);
void handle_client_message(struct scheduler_ctx *ctx, struct client_session *cs,
                           const struct packet_header *hdr);
void handle_client_disconnect(struct scheduler_ctx *ctx, struct client_session *cs);
void handle_initial_connection_packet(struct scheduler_ctx *ctx, int fd);

#endif /* SCHEDULER_H */
