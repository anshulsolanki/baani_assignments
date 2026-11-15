# CS3.301 Operating Systems and Networks — Course Project
## Complete Concept Walkthrough, Code Pointers & TA Viva Guide for Baani

---

## 1. Plain-English Walkthrough ("What & Why Before How")

### What Are We Building and Why?
Imagine five laptops in a hostel room sharing the work of running users' programs. Instead of asking friends on WhatsApp to run a program, we built a **Distributed Compute Cluster** in C with three programs communicating over UDP and TCP sockets:
1. **`./scheduler` (Central Brain):** Holds the job queue (up to 1024 jobs), tracks which worker machines are alive and how many free cores/RAM/GPUs they have, decides which worker runs which job using a 10-step scheduling pass, and relays live output and `[Event]` updates back to users.
2. **`./worker` (Muscle / Laptop Node):** Discovers the scheduler via UDP broadcast, advertises its hardware capacity (clamped to real CPU cores and RAM), forks each assigned job inside an isolated `/tmp/osn_job_<JobID>` sandbox with `nobody` privileges and OS resource limits (`setrlimit`), watches the job's memory/CPU/output/checkpoints every 500ms, and sends heartbeats every 2 seconds.
3. **`./client` (User Shell):** Discovers the scheduler via UDP broadcast, logs the user in, lets them run commands (`nodes`, `submit`, `status`, `logs`, `logs -f`, `cancel`, `migrate`, `crons`, `cancel-cron`), and prints asynchronous `[Event]` notifications even while idle at the `client> ` prompt.

---

## 2. "What to Show the TA" — Exact File & Function Pointers

| Section / Topic | File & Function to Show | Key Implementation Detail |
| :--- | :--- | :--- |
| **2A & 4A: Scheduler `select()` Loop** | `src/scheduler/main.c` $\rightarrow$ `main()` | Single-threaded `select()` multiplexing `udp_disc_fd`, `tcp_listen_fd`, `workers[]`, and `clients[]` with a 1s periodic tick (`cron_tick`, `check_worker_heartbeats`, `check_job_dependencies`, `schedule_jobs`). |
| **2B: Hardware Clamping** | `src/worker/main.c` $\rightarrow$ `get_hardware_limits()` | Uses `sysconf(_SC_NPROCESSORS_ONLN)` for cores and `sysctlbyname("hw.memsize")` (macOS) / `sysconf(_SC_PHYS_PAGES) * sysconf(_SC_PAGESIZE)` (Linux) for RAM. |
| **2C: UDP Discovery** | `src/shared/net_utils.c` $\rightarrow$ `discover_scheduler_udp()` & `handle_udp_discovery_request()` | Broadcasts `"DISCOVER_SCHEDULER"` to `255.255.255.255:9999` up to 3 times (`2s` `select()` timeout each); scheduler replies `"SCHEDULER_TCP_PORT <port>"`. |
| **3: Client Login, Queries & Async Events** | `src/client/main.c`, `src/client/commands.c`, `src/scheduler/client_queries.c` | Validates `1..31` chars of `[A-Za-z0-9_.-]`; `select()` watches `STDIN_FILENO` and `sock_fd` simultaneously so `MSG_SCHED_EVENT` prints immediately; `client_queries.c` serves `nodes`, `status`, `logs`, `cancel`, `migrate`, and `crons`. |
| **4B: Canonical 10-Step Scheduling Pass** | `src/scheduler/scheduler_pass.c` $\rightarrow$ `schedule_jobs()` | Implements aging (`eff_prio = base_prio - wait_sec / 10`), `FIFO` vs `PRIORITY` sorting, `hold_for_job_id` check, `>50%` quota check, resource match, 4-level tiebreaker, and `FIFO` head-of-line stop vs `PRIORITY` continue. |
| **4C: Heartbeats & 3-Attempt Rescue** | `src/scheduler/worker_registry.c` $\rightarrow$ `check_worker_heartbeats()` & `mark_worker_dead_and_rescue()` | `ALIVE -> SUSPECTED` at `>= 3s` silence, back to `ALIVE` on heartbeat, `-> DEAD` at `>= 6s` silence; moves `RUNNING -> LOST -> QUEUED` up to 3 attempts, then `FAILED_PERMANENT`. |
| **4D & 13: 4-Level Worker Tiebreaker** | `src/scheduler/scheduler_pass.c` $\rightarrow$ `is_better_worker()` | Exact order: `idle (0 running jobs) > cached binary (SHA-1) > lowest CPU load % > fewest running jobs`. |
| **5A: Sandbox, Privilege Drop & Limits** | `src/worker/sandbox_exec.c` $\rightarrow$ `launch_job_process()` | Creates `/tmp/osn_job_<id>`, `chown` to `nobody`, `fork()`, `setpgid(0,0)`, `chdir()`, `dup2()` to `output.log`, `setgid()` then `setuid()`, `setrlimit()` (`CPU`, `AS`, `FSIZE`, `NPROC`), and `execvp()`. |
| **5D & 5E: Live Telemetry & Crash Diagnosis** | `src/worker/monitor_telemetry.c` $\rightarrow$ `read_process_telemetry()`, `diagnose_job_exit()`, `poll_active_jobs()` | Reads RSS/faults/CPU via `proc_pidinfo(PROC_PIDTASKINFO)` on macOS and `/proc/<pid>/stat[m]` on Linux; enforces macOS RSS cap and wall-clock deadline; translates exit codes (`127`) and signals (`SIGSEGV`, `SIGFPE`). |
| **6: Streaming Logs (`logs -f`)** | `src/scheduler/job_manager.c` $\rightarrow$ `append_job_log()` & `src/client/main.c` | Keeps 64 KB sliding tail buffer per job; forwards live chunks to `follow_job_id` subscribers; `Ctrl+C` sends `MSG_CLIENT_LOGS_UNSUB` without exiting client. |
| **7: Timestamped Logging** | `src/shared/log_utils.c` $\rightarrow$ `log_line()` | Formats `[HH:MM:SS]` via `localtime_r()` + `strftime()` and flushes stdout. |
| **8: Dependencies & Groups** | `src/scheduler/client_handler.c` $\rightarrow$ `resolve_dependencies()` & `src/scheduler/job_manager.c` $\rightarrow$ `check_job_dependencies()` | Resolves `g<id>` at submit time; promotes `WAITING -> QUEUED` when all deps complete; cascades `WAITING -> CANCELLED` in a `do { ... } while (changed)` loop when any dep fails. |
| **9: Graceful Draining** | `src/worker/main.c` $\rightarrow$ `initiate_worker_drain()` | Triggered identically by `"drain"` on worker `stdin` or `SIGINT` (`Ctrl+C`); sets `WORKER_DRAINING`, finishes active jobs, and exits cleanly. |
| **10: Preemptible Jobs** | `src/scheduler/scheduler_pass.c` $\rightarrow$ `try_preempt_for_job()` | Picks victims on an `ALIVE` worker with `preemptible && base_prio > 1` sorted by lowest priority (`3` before `2`) then newest `submit_time` first; sets `hold_for_job_id` and does not consume an attempt. |
| **11: Fair-Share User Quotas** | `src/scheduler/scheduler_pass.c` $\rightarrow$ `is_user_over_quota()` | Checks `user_held_cores(user) * 2 > total_non_dead_cluster_cores()`; skips job if another non-over-quota user has a `QUEUED` job. |
| **12: Recurring (Cron) Jobs** | `src/scheduler/job_manager.c` $\rightarrow$ `cron_tick()` | Fires first copy immediately at submit time and subsequent copies every `every_sec` seconds; `cancel-cron` sets `active = 0`. |
| **13: SHA-1 Caching & LRU Eviction** | `src/shared/sha1.c` & `src/worker/cache_ckpt.c` $\rightarrow$ `cache_evict_lru()` | Content-addressed `<cache_dir>/<name>-<sha1>`; `utimes()` updates mtime on launch; evicts oldest-mtime file when total exceeds `OSN_CACHE_SIZE_MB` (never evicting newly stored or active hashes). |
| **14: Checkpoints & Live Migration** | `src/worker/cache_ckpt.c` $\rightarrow$ `check_job_checkpoint_file()` & `src/worker/monitor_telemetry.c` $\rightarrow$ `stop_active_job()` | Polls `$OSN_CHECKPOINT_DIR/state` every 500ms; `migrate` sends `SIGTERM` $\rightarrow$ waits 2s $\rightarrow$ `SIGKILL`, reads final state once more after `waitpid`, requeues without attempt penalty, and sets `avoid_worker_id`. |

---

## 3. Top 20 Likely TA Viva Questions & Model Answers

**Q1. Why did you choose a single-threaded `select()` loop in the scheduler instead of spawning a thread per connection?**  
> **Answer:** In the scheduler, every client command (`nodes`, `status`, `submit`, `cancel`), worker heartbeat, and scheduling pass mutates the same shared job queue and worker table. With a single-threaded `select()` loop and length-prefixed non-blocking packets, there are zero mutex deadlocks or data races, `nodes` and `status` are answered on the very next `select()` wakeup without ever waiting behind locks, and the 1-second timer tick drives aging, heartbeats, and cron jobs deterministically.

**Q2. How does your TCP wire protocol handle partial reads or writes when sending a 30 MB binary over TCP?**  
> **Answer:** Every message on the wire starts with an 8-byte `struct packet_header { int32_t type; int32_t length; }`. In `src/shared/net_utils.c`, `send_all()` and `recv_all()` loop over `send()` and `recv()` until all `length` bytes have been transferred (retrying on `EINTR`), and binaries are streamed in 16 KB `MSG_SCHED_BINARY_CHUNK` packets so memory usage stays small and bounded.

**Q3. Why must the worker call `setgid()` BEFORE `setuid()` when dropping privileges to `nobody`?**  
> **Answer:** Only `root` (`euid == 0`) has permission to change its group ID via `setgid()` and supplementary groups via `setgroups()`. If you called `setuid(nobody_uid)` first, the process would immediately lose root privileges, and the subsequent `setgid(nobody_gid)` call would fail with `EPERM` (`Operation not permitted`), leaving the job running with root's group privileges!

**Q4. Why must `chown()` on `/tmp/osn_job_<JobID>` happen before dropping privileges?**  
> **Answer:** `mkdir()` creates `/tmp/osn_job_<JobID>` owned by `root` (when worker runs under `sudo`). Unprivileged user `nobody` cannot `chown` a root-owned directory or write files (like `checkpoint/state.tmp`) inside a root-owned directory unless `root` first `chown`s `/tmp/osn_job_<JobID>` and `/tmp/osn_job_<JobID>/checkpoint` to `nobody`.

**Q5. Why isn't `RLIMIT_CPU` alone enough to enforce `-time <sec>`?**  
> **Answer:** `RLIMIT_CPU` only measures time the process spends actively executing on a CPU core. If a job calls `sleep(1000)` or blocks on I/O, it consumes almost `0.0s` of CPU time and `RLIMIT_CPU` never fires! That's why our worker also records millisecond `aj->start_ms` (`gettimeofday()`) and checks `now_ms - aj->start_ms >= aj->time_limit_sec * 1000` (after checking `waitpid(WNOHANG)` so an already-finished job isn't falsely timed out), killing overdue jobs with `SIGKILL` and reporting `"Wall-clock timeout exceeded"`.

**Q6. Why does macOS require special handling for the `-ram <MB>` limit compared to Linux?**  
> **Answer:** On Linux, the kernel enforces `setrlimit(RLIMIT_AS, ...)` so `malloc()`/`mmap()` returns `NULL` once virtual address space exceeds `-ram`. On macOS, the XNU kernel ignores `RLIMIT_AS`. Therefore, in `poll_active_jobs()`, our worker calls `proc_pidinfo(pid, PROC_PIDTASKINFO, ...)` every 500ms to read `pti_resident_size` (RSS), and if `rss_mb > aj->ram_mb`, immediately kills the job with `SIGKILL` and reports `"Memory limit exceeded"`.

**Q7. Why did you call `setpgid(0, 0)` in the child process and `kill(-aj->pid, SIGKILL)` in the worker?**  
> **Answer:** If a job is a shell script or spawns child processes, killing only the top-level PID (`kill(aj->pid, SIGKILL)`) would leave its grandchildren alive as orphan processes still burning CPU/RAM! Calling `setpgid(0, 0)` puts the job in its own process group with PGID equal to `aj->pid`, so `kill(-aj->pid, SIGKILL)` kills the entire process tree at once.

**Q8. Why does `getrusage(RUSAGE_CHILDREN)` not work for live telemetry in `status <job_id>`?**  
> **Answer:** `getrusage(RUSAGE_CHILDREN)` only reports resource usage of child processes that have **already terminated and been waited on**. For a currently `RUNNING` job, we must query the OS directly for that specific live PID using `proc_pidinfo(pid, PROC_PIDTASKINFO, ...)` on macOS and `/proc/<pid>/stat` + `/proc/<pid>/statm` on Linux.

**Q9. Explain the difference between `FIFO` and `PRIORITY` when the first job in the queue needs 8 cores and the only free worker has 4 cores.**  
> **Answer:** Under `FIFO`, the scheduling pass **stops immediately** (`break;`) at step 8 because `FIFO` enforces strict submission order — a smaller 2-core job behind the 8-core job must wait. Under `PRIORITY`, the scheduler skips the 8-core job (after attempting preemption if it has effective priority 1) and **continues** (`continue;`) to try the next queued job.

**Q10. How does priority aging prevent starvation in `PRIORITY` mode?**  
> **Answer:** Whenever a job enters `QUEUED`, we record `queued_since`. At the start of every scheduling pass, we compute `boost = (now - queued_since) / 10` and `eff_prio = max(1, base_prio - boost)`. So a Priority 3 job becomes Priority 2 after 10 seconds in the queue and Priority 1 after 20 seconds, guaranteeing it eventually reaches the highest priority.

**Q11. What happens when a job is preempted vs. when its worker dies (`DEAD`)?**  
> **Answer:**
> - When a worker goes `DEAD` (3 missed heartbeats / 6s), its jobs go `RUNNING -> LOST -> QUEUED` and **consume an attempt**; if a job fails 3 attempts (`attempts >= 3`), it transitions to `FAILED_PERMANENT`.
> - When a job is **preempted** (or **migrated**), it is not a fault, so we decrement `j->attempts--` when moving it back to `QUEUED` so no retry attempt is used! Furthermore, a preempted job sets `hold_for_job_id = prio1_job->id` so it cannot grab back the freed cores until the Priority 1 job has started.

**Q12. In Section 10 (Preemption), if a worker is running three preemptible jobs — Job A (prio 2, submitted at t=5), Job B (prio 3, submitted at t=2), and Job C (prio 3, submitted at t=8) — in what order are victims killed?**  
> **Answer:** Victims are chosen **lowest priority first (highest priority number `3` before `2`), and among equals, most recently submitted first**. So **Job C** (prio 3, t=8) is killed first, then **Job B** (prio 3, t=2), and only if more resources are still needed, **Job A** (prio 2, t=5). We stop adding victims as soon as the freed cores/RAM/GPUs are enough for the Priority 1 job.

**Q13. In Section 11 (Fair-Share Quotas), if a cluster has 8 non-dead cores and User A is running a 4-core job (50%), is User A's next queued job skipped?**  
> **Answer:** **No!** The specification explicitly states: *"If a user holds **more than 50%** of the cluster's total cores ... Exactly 50% is **not** over quota."* We check `user_held_cores(user) * 2 > total_non_dead_cluster_cores()`, which is `4 * 2 > 8` (`8 > 8`, false). Only when User A holds 5 or more cores out of 8 (`> 50%`) AND another user who is not over quota has a `QUEUED` job do we skip User A's job.

**Q14. Why must group dependencies (`-depends-on g3`) be resolved at submit time rather than dynamically during scheduling?**  
> **Answer:** Because Section 8 specifies: *"The scheduler resolves `g3` **at submit time** into the set of job IDs in group 3 at that moment. Jobs that join group 3 later have no effect on this dependency."* And if group 3 has no jobs at submit time, the submission is immediately rejected.

**Q15. What is the exact 4-level worker selection tiebreaker order when multiple `ALIVE` workers fit a job?**  
> **Answer:**
> 1. **Idle over busy** (`0` running jobs beats `> 0` running jobs).
> 2. **Binary already cached** (SHA-1 hash present in `w->cached_hashes[]` beats not cached, compared within the idle group and within the busy group).
> 3. **Lowest CPU load %** (`w->cpu_load_pct` from `getloadavg()`).
> 4. **Fewest running jobs** (`w->running_jobs`).

**Q16. Why does an idle worker without the cached binary beat a busy worker that already has the binary cached?**  
> **Answer:** Because starting the job on an idle machine gives it uncontended CPU/memory immediately, which matters more than saving a one-time network file transfer. Caching only breaks ties *within* the idle group or *within* the busy group.

**Q17. How does LRU cache eviction in Section 13 know which binary was used least recently, and which files are protected from eviction?**  
> **Answer:** Whenever a job launches from a cached binary `<cache_dir>/<name>-<sha1>`, the worker calls `utimes(cached_path, NULL)` to update the file's modification timestamp to `now`. When storing a new binary pushes total folder size above `OSN_CACHE_SIZE_MB`, `cache_evict_lru()` scans `<cache_dir>/`, skips the newly stored hash (`keep_hash`) and any hash currently used by a `RUNNING` job (`cache_hash_in_use()`), and deletes the file with the oldest timestamp until total size is within the limit, then sends `MSG_WORKER_CACHE_LIST` to update the scheduler.

**Q18. What happens if someone manually deletes a cached file from a worker's `cache/` folder while the scheduler thinks the worker still has it?**  
> **Answer:** When the worker receives `MSG_SCHED_ASSIGN_JOB` with `exec_transferred == 1`, it looks up `assign->sha1_hash` in `cache/`. Seeing the file is missing, the worker sends `MSG_WORKER_CACHE_MISS` back to the scheduler instead of starting the job. The scheduler removes that hash from `w->cached_hashes[]`, decrements `j->attempts--` so no retry attempt is charged, and immediately streams the full binary followed by `MSG_SCHED_ASSIGN_JOB`.

**Q19. Why should a checkpointing job write to `state.tmp` and `rename()` it to `state` instead of writing directly to `state`?**  
> **Answer:** The worker polls `$OSN_CHECKPOINT_DIR/state` every 500ms asynchronously, and a worker or job can also be killed mid-write. Writing directly to `state` with `fopen("state", "w")` truncates the file to 0 bytes first, risking the worker reading a half-written or empty checkpoint! On POSIX filesystems, `rename("state.tmp", "state")` is **atomic**, so `state` always contains either the complete previous checkpoint or the complete new checkpoint.

**Q20. Walk through the exact sequence of events when a user runs `migrate <job_id>` (Section 14).**  
> **Answer:**
> 1. Scheduler verifies the job is `RUNNING`, marks `j->migrate_pending = 1`, and sends `MSG_SCHED_STOP_JOB` (`STOP_MIGRATE`) to its current worker (`Worker 1001`).
> 2. Worker 1001 sends `SIGTERM` to the job's process group so the job can catch `SIGTERM` and write one final checkpoint, and starts a 2-second escalation timer (sending `SIGKILL` after 2s if still alive).
> 3. As soon as `waitpid()` reaps the job, Worker 1001 checks `$OSN_CHECKPOINT_DIR/state` **one final time**, sends `MSG_WORKER_CHECKPOINT` to the scheduler so the last save isn't lost, and sends `MSG_WORKER_JOB_DONE` (`OUTCOME_MIGRATED`).
> 4. Scheduler moves the job back to `QUEUED` **without using a retry attempt**, sets `j->avoid_worker_id = 1001`, and on the next scheduling pass picks another qualifying worker (`Worker 1002`), sending `MSG_SCHED_CKPT_DATA` first, then the binary/`EXEC_CACHED`, then `MSG_SCHED_ASSIGN_JOB`.
> 5. Worker 1002 writes the checkpoint bytes into `/tmp/osn_job_<id>/checkpoint/state` before `fork()`/`execvp()`, and the job reads `$OSN_CHECKPOINT_DIR/state` on startup to continue from where it left off!
