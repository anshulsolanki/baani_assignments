#ifndef WORKER_H
#define WORKER_H

#include "cluster_protocol.h"
#include "net_utils.h"
#include <stdio.h>
#include <sys/types.h>
#include <time.h>

enum internal_kill_reason {
    KILL_NONE = 0,
    KILL_TIMEOUT = 1,
    KILL_MEMORY = 2,
    KILL_CANCEL = 3,
    KILL_PREEMPT = 4,
    KILL_MIGRATE = 5
};

struct active_job {
    int used;
    int job_id;
    pid_t pid;
    int cores;
    int ram_mb;
    int gpu;
    int time_limit_sec;
    int64_t start_ms;

    int log_read_fd;
    char job_dir[MAX_PATH_STR];
    char ckpt_dir[MAX_PATH_STR];
    char sha1_hash[SHA1_HEX_LEN];

    uint64_t last_ckpt_sig;

    int current_ram_mb;
    int peak_ram_mb;
    int page_faults;
    double cpu_time_sec;

    int kill_reason;
    int64_t migrate_sigterm_ms;
};

struct pending_ckpt {
    int valid;
    int job_id;
    uint8_t *data;
    int32_t len;
};

struct binary_transfer_state {
    int active;
    int job_id;
    char exec_name[MAX_NAME_STR];
    char sha1_hash[SHA1_HEX_LEN];
    char tmp_path[MAX_PATH_STR];
    FILE *fp;
    int32_t total_size;
    int32_t received;
};

struct worker_ctx {
    int worker_id;
    int sock_fd;
    int discovery_port;
    int has_fallback;
    char fallback_ip[64];
    int fallback_port;

    int total_cores;
    int free_cores;
    int total_ram_mb;
    int free_ram_mb;
    int total_gpu;
    int free_gpu;

    int is_root;
    int is_draining;
    int drain_announced;

    char cache_dir[MAX_PATH_STR];
    int64_t cache_limit_bytes;

    struct active_job jobs[MAX_WORKER_JOBS];
    struct pending_ckpt pending_ckpt;
    struct binary_transfer_state bin_rx;
};

/* sandbox_exec.c */
int launch_job_process(struct worker_ctx *wctx, const struct msg_assign_job *assign);
void cleanup_job_directory(const char *job_dir);
void kill_all_active_jobs(struct worker_ctx *wctx);

/* monitor_telemetry.c */
void poll_active_jobs(struct worker_ctx *wctx);
void stop_active_job(struct worker_ctx *wctx, int job_id, int stop_reason);
int count_worker_active_jobs(const struct worker_ctx *wctx);
int compute_worker_cpu_load_pct(int total_cores);
void send_worker_heartbeat(struct worker_ctx *wctx);

/* cache_ckpt.c */
void init_worker_cache(struct worker_ctx *wctx);
int cache_lookup_by_hash(const struct worker_ctx *wctx, const char *hash,
                         char *out_path, size_t out_len);
int cache_hash_in_use(const struct worker_ctx *wctx, const char *hash);
void cache_evict_lru(struct worker_ctx *wctx, const char *keep_hash);
void send_worker_cache_list(struct worker_ctx *wctx);
void handle_binary_chunk(struct worker_ctx *wctx, const struct packet_header *hdr);
void handle_checkpoint_data(struct worker_ctx *wctx, const struct packet_header *hdr);
void check_job_checkpoint_file(struct worker_ctx *wctx, struct active_job *aj);

#endif /* WORKER_H */
