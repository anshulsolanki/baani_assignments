# Distributed Compute Cluster (CS3.301 Course Project)

A distributed compute cluster written in C over plain UDP/TCP sockets consisting of three programs:
- **`./scheduler`**: Central cluster server holding the bounded job queue (`1024` max), worker table, cron templates, and client sessions, driving the canonical 10-step scheduling pass.
- **`./worker`**: Compute node advertising hardware-clamped resources (`-cores`, `-ram`, `-gpu`), isolating and limiting jobs in `/tmp/osn_job_<JobID>`, capturing live output and telemetry (`proc_pidinfo` on macOS, `/proc` on Linux), managing an LRU executable cache (`cache/`), and watching job checkpoints (`$OSN_CHECKPOINT_DIR/state`).
- **`./client`**: Interactive user CLI supporting UDP discovery, login, asynchronous `[Event]` notifications, and cluster commands (`nodes`, `submit`, `status`, `logs`, `logs -f`, `cancel`, `migrate`, `crons`, `cancel-cron`).

---

## 1. Repository Layout

```text
course_project/
├── Makefile                        # Builds ./scheduler, ./worker, ./client, and tests/
├── README.md                       # Build, run, architecture, design choices & assumptions
├── src/
│   ├── shared/
│   │   ├── cluster_protocol.h      # Wire message types, constants, and packet structs
│   │   ├── net_utils.h             # Declarations for framing, UDP discovery, logging, SHA-1
│   │   ├── log_utils.c             # Central log_line() with [HH:MM:SS] 24-hour timestamps
│   │   ├── net_utils.c             # TCP send/recv framing and UDP discovery broadcast/reply
│   │   └── sha1.c                  # Self-contained SHA-1 implementation for binary hashing
│   ├── scheduler/
│   │   ├── scheduler.h             # Job, Worker, ClientSession, CronTemplate structs
│   │   ├── main.c                  # CLI parser, UDP+TCP setup, 1s select() event loop
│   │   ├── worker_registry.c       # Worker registration, heartbeats (ALIVE/SUSPECTED/DEAD), rescue
│   │   ├── job_manager.c           # Job records, 64 KB log tail buffer, dependencies/groups, crons
│   │   ├── scheduler_pass.c        # Canonical 10-step scheduling pass (FIFO/PRIORITY, aging, quota, cache)
│   │   └── client_handler.c        # Client login and command handlers
│   ├── worker/
│   │   ├── worker.h                # ActiveJob, PendingCkpt, WorkerContext structs
│   │   ├── main.c                  # CLI parser, sysconf/sysctl clamping, UDP discovery, select() loop
│   │   ├── sandbox_exec.c          # /tmp/osn_job_<id>, nobody privilege drop, rlimits, fork+execvp
│   │   ├── monitor_telemetry.c     # 500ms output.log tailing, live RSS/CPU telemetry, crash diagnosis
│   │   └── cache_ckpt.c            # SHA-1 cache/ manager with LRU eviction & checkpoint polling
│   └── client/
│       ├── client.h                # ClientContext struct & prototypes
│       ├── main.c                  # CLI parser, UDP discovery + fallback, login, select() loop
│       └── commands.c              # Command parser (nodes, submit, status, logs, cancel, migrate, crons)
└── tests/                          # Test programs for resource limits, signals, and checkpoints
    ├── Makefile
    ├── hello_job.c
    ├── sleeper_job.c
    ├── cpu_burner.c
    ├── mem_hog.c
    ├── crash_segv.c
    ├── crash_fpe.c
    └── counter_ckpt.c
```

---

## 2. How to Build and Run

### Build Everything
```bash
make all
```
This compiles `./scheduler`, `./worker`, `./client` in the root directory and the test programs in `tests/`. To clean all build artifacts:
```bash
make clean
```

### Start the Scheduler (Section 2A)
```bash
./scheduler <port> <FIFO|PRIORITY> [-discovery-port <port>]
# Example:
./scheduler 8080 PRIORITY
```

### Start One or More Workers (Section 2B)
```bash
sudo ./worker [<scheduler_ip> <scheduler_port>] -cores <num> -ram <MB> [-gpu <num>] [-discovery-port <port>]
# Example (auto-discovers scheduler via UDP port 9999):
sudo ./worker -cores 4 -ram 2048 -gpu 1
```
- If run without `sudo`, the worker prints a clear warning and skips privilege-dropping (`chown`/`setgid`/`setuid` to `nobody`) so local development works without root.
- When running multiple workers on the same machine, give each worker its own cache directory via `OSN_CACHE_DIR` (and optional cache cap via `OSN_CACHE_SIZE_MB`):
  ```bash
  OSN_CACHE_DIR=cache_w1 OSN_CACHE_SIZE_MB=512 sudo -E ./worker -cores 4 -ram 2048 -gpu 1
  OSN_CACHE_DIR=cache_w2 OSN_CACHE_SIZE_MB=512 sudo -E ./worker -cores 4 -ram 2048 -gpu 0
  ```

### Start the Client (Section 3)
```bash
./client [<scheduler_ip> <scheduler_port>] [-user <username>] [-discovery-port <port>]
# Example:
./client -user lordz
```

### Supported Client Commands
- `nodes` — Lists every worker (`ID`, `Status`, `Cores (Free/Total)`, `RAM (Free/Total)`, `GPU (Free/Total)`, `Jobs`).
- `submit <binary> -cores <c> -ram <MB> -time <sec> -prio <1-3> [-gpu <g>] [-depends-on 1,2,g3] [-group <id>] [-preemptible] [-every <sec>]` — Submits a job or recurring cron template.
- `status <job_id>` — Displays job state, owner, assigned worker, live/peak RAM, page faults, CPU time, failure reason, and latest checkpoint (`#n, size, age`).
- `logs <job_id>` — Prints up to the last 64 KB of output captured from the job.
- `logs <job_id> -f` — Streams live output as the job runs until completion (`-- Job <id> finished --`) or `Ctrl+C` (which returns to `client> ` without exiting).
- `cancel <job_id>` — Cancels a `WAITING`, `QUEUED`, or `RUNNING` job.
- `migrate <job_id>` — Migrates a `RUNNING` job off its current worker (`SIGTERM` $\rightarrow$ 2s grace $\rightarrow$ `SIGKILL`), saving its latest checkpoint and resuming on another worker.
- `crons` / `cancel-cron <template_id>` — Lists recurring cron templates or stops future runs of a template.

---

## 3. Design Choices & Assumptions

1. **Single-Threaded `select()` Event Loop Concurrency Model (Section 4A):**
   - The scheduler uses a non-blocking single-threaded `select()` loop over the UDP discovery socket, TCP listen socket, worker sockets, and client sockets with a periodic 1-second tick (`cron_tick()`, `check_worker_heartbeats()`, `check_job_dependencies()`, `schedule_jobs()`).
   - This eliminates lock contention and guarantees `nodes` and `status` queries never wait behind scheduling passes.
2. **Length-Prefixed Binary Wire Protocol:**
   - Every TCP packet starts with an 8-byte `struct packet_header` (`int32_t type`, `int32_t length`), handled by `send_all()` / `recv_all()` loops to cope with partial TCP transfers.
3. **Cross-Platform Resource Telemetry & Limits (macOS + Linux):**
   - Hardware clamping uses `sysconf(_SC_NPROCESSORS_ONLN)` for cores and `sysctlbyname("hw.memsize", ...)` (macOS) / `sysconf(_SC_PHYS_PAGES) * sysconf(_SC_PAGESIZE)` (Linux) for physical RAM.
   - Live per-job RSS, page faults, and CPU time are read via `proc_pidinfo(pid, PROC_PIDTASKINFO, ...)` on macOS and `/proc/<pid>/statm` + `/proc/<pid>/stat` on Linux. Because macOS ignores `RLIMIT_AS`, the worker's 500ms loop also enforces `-ram` by checking live RSS and sending `SIGKILL` when exceeded.
4. **Self-Contained SHA-1 Executable Caching & LRU Eviction (Section 13):**
   - `src/shared/sha1.c` implements standard FIPS 180-1 SHA-1 in pure C so the project builds on both macOS and Linux with zero external library dependencies.
   - Cached binaries are stored as `<cache_dir>/<name>-<sha1>` and touched with `utimes()` on each job launch; when total cache size exceeds `OSN_CACHE_SIZE_MB` (default `512` MB), the oldest-mtime unused files are evicted first.

---

## 4. Known Bugs / Limitations
- None known. All 14 sections (`2` through `14`) and 4 milestones have been verified end-to-end.
