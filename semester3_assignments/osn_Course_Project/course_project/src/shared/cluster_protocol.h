#ifndef CLUSTER_PROTOCOL_H
#define CLUSTER_PROTOCOL_H

#include <stdint.h>
#include <time.h>

/* Cluster-wide limits and defaults */
#define DEFAULT_DISCOVERY_PORT 9999
#define DISCOVERY_MAGIC_REQ    "DISCOVER_SCHEDULER"
#define DISCOVERY_MAGIC_RESP   "SCHEDULER_TCP_PORT"
#define DISCOVERY_RETRIES      3
#define DISCOVERY_TIMEOUT_SEC  2

#define MAX_QUEUE_LEN          1024
#define MAX_JOBS_TOTAL         2048
#define MAX_WORKERS            64
#define MAX_CLIENTS            128
#define MAX_CRON_TEMPLATES     64
#define MAX_DEPS_PER_JOB       32
#define MAX_WORKER_JOBS        64
#define MAX_WORKER_CACHE       64
#define MAX_RETRY_ATTEMPTS     3

#define HEARTBEAT_INTERVAL_SEC 2
#define SUSPECT_THRESHOLD_SEC  3
#define DEAD_THRESHOLD_SEC     6

#define JOB_LOG_BUFFER_SIZE    (64 * 1024)
#define BIN_CHUNK_MAX          16384
#define DEFAULT_CACHE_SIZE_MB  512
#define RLIMIT_NPROC_DEFAULT   64
#define RLIMIT_FSIZE_BYTES     (100 * 1024 * 1024)

#define MAX_USERNAME_LEN       32
#define MAX_PATH_STR           256
#define MAX_NAME_STR           128
#define SHA1_HEX_LEN           41

/* Scheduling algorithms */
enum sched_algo {
    ALGO_FIFO = 0,
    ALGO_PRIORITY = 1
};

/* Worker lifecycle states (Section 1 & 4C & 9) */
enum worker_state {
    WORKER_ALIVE = 0,
    WORKER_SUSPECTED = 1,
    WORKER_DEAD = 2,
    WORKER_DRAINING = 3
};

/* Job lifecycle states (Section 1) */
enum job_state {
    JOB_WAITING = 0,
    JOB_QUEUED = 1,
    JOB_RUNNING = 2,
    JOB_COMPLETED = 3,
    JOB_FAILED = 4,
    JOB_CANCELLED = 5,
    JOB_LOST = 6,
    JOB_FAILED_PERMANENT = 7
};

/* Worker job stop outcomes (Section 5 & 10 & 14) */
enum job_outcome {
    OUTCOME_COMPLETED = 0,
    OUTCOME_FAILED = 1,
    OUTCOME_CANCELLED = 2,
    OUTCOME_PREEMPTED = 3,
    OUTCOME_MIGRATED = 4
};

/* Stop command reasons sent from Scheduler to Worker */
enum stop_reason {
    STOP_CANCEL = 1,
    STOP_PREEMPT = 2,
    STOP_MIGRATE = 3
};

/* Wire message types */
enum msg_type {
    /* Worker <-> Scheduler */
    MSG_WORKER_REGISTER     = 10,
    MSG_WORKER_REG_ACK      = 11,
    MSG_WORKER_CACHE_LIST   = 12,
    MSG_WORKER_HEARTBEAT    = 13,
    MSG_WORKER_DRAIN        = 14,

    MSG_SCHED_EXEC_CACHED   = 20,
    MSG_SCHED_BINARY_CHUNK  = 21,
    MSG_SCHED_CKPT_DATA     = 22,
    MSG_SCHED_ASSIGN_JOB    = 23,
    MSG_SCHED_STOP_JOB      = 24,

    MSG_WORKER_CACHE_MISS   = 25,
    MSG_WORKER_JOB_OUTPUT   = 26,
    MSG_WORKER_CHECKPOINT   = 27,
    MSG_WORKER_JOB_DONE     = 28,

    /* Client <-> Scheduler */
    MSG_CLIENT_LOGIN        = 40,
    MSG_CLIENT_LOGIN_ACK    = 41,
    MSG_CLIENT_NODES_REQ    = 42,
    MSG_CLIENT_SUBMIT_REQ   = 43,
    MSG_CLIENT_STATUS_REQ   = 44,
    MSG_CLIENT_LOGS_REQ     = 45,
    MSG_CLIENT_LOGS_UNSUB   = 46,
    MSG_CLIENT_CANCEL_REQ   = 47,
    MSG_CLIENT_MIGRATE_REQ  = 48,
    MSG_CLIENT_CRONS_REQ    = 49,
    MSG_CLIENT_CANCEL_CRON  = 50,

    MSG_SCHED_REPLY         = 51,
    MSG_SCHED_EVENT         = 52,
    MSG_SCHED_LOG_CHUNK     = 53,
    MSG_SCHED_LOG_EOF       = 54
};

/* Fixed 8-byte header preceding every TCP message */
struct packet_header {
    int32_t type;
    int32_t length;
};

struct msg_worker_register {
    int32_t cores;
    int32_t ram_mb;
    int32_t gpu;
};

struct msg_worker_reg_ack {
    int32_t worker_id;
};

struct msg_worker_cache_list {
    int32_t count;
    char hashes[MAX_WORKER_CACHE][SHA1_HEX_LEN];
};

struct msg_job_telemetry {
    int32_t job_id;
    int32_t current_ram_mb;
    int32_t peak_ram_mb;
    int32_t page_faults;
    double cpu_time_sec;
};

struct msg_worker_heartbeat {
    int32_t worker_id;
    int32_t cpu_load_pct;
    int32_t active_jobs;
    int32_t free_cores;
    int32_t free_ram_mb;
    int32_t free_gpu;
    struct msg_job_telemetry jobs[MAX_WORKER_JOBS];
};

struct msg_exec_cached {
    int32_t job_id;
    char exec_name[MAX_NAME_STR];
    char sha1_hash[SHA1_HEX_LEN];
};

struct msg_binary_meta {
    int32_t job_id;
    char exec_name[MAX_NAME_STR];
    char sha1_hash[SHA1_HEX_LEN];
    int32_t total_size;
    int32_t offset;
    int32_t chunk_len;
};

struct msg_ckpt_header {
    int32_t job_id;
    int32_t data_len;
};

struct msg_assign_job {
    int32_t job_id;
    int32_t cores;
    int32_t ram_mb;
    int32_t gpu;
    int32_t time_limit_sec;
    int32_t exec_transferred;
    int32_t has_checkpoint;
    char binary_path[MAX_PATH_STR];
    char exec_name[MAX_NAME_STR];
    char sha1_hash[SHA1_HEX_LEN];
};

struct msg_stop_job {
    int32_t job_id;
    int32_t reason;
};

struct msg_cache_miss {
    int32_t job_id;
    char sha1_hash[SHA1_HEX_LEN];
};

struct msg_job_output_hdr {
    int32_t job_id;
    int32_t text_len;
};

struct msg_job_done {
    int32_t job_id;
    int32_t outcome;
    int32_t exit_code;
    int32_t term_signal;
    int32_t peak_ram_mb;
    int32_t page_faults;
    double cpu_time_sec;
    char diagnosis[256];
};

struct msg_client_login {
    char username[MAX_USERNAME_LEN];
};

struct msg_submit_req {
    char binary[MAX_PATH_STR];
    int32_t cores;
    int32_t ram_mb;
    int32_t time_sec;
    int32_t prio;
    int32_t gpu;
    int32_t group_id;
    int32_t preemptible;
    int32_t every_sec;
    char depends_on[256];
};

struct msg_logs_req {
    int32_t job_id;
    int32_t follow;
};

#endif /* CLUSTER_PROTOCOL_H */
