# CS3.301 Operating Systems and Networks — Course Project
## Complete Step-by-Step 18-Commit Replication, Team Split & Testing Guide for Baani

**Reference Repository (GitHub):** `https://github.com/anshulsolanki/baani_assignments`  
**Completed Reference Code Folder:** `semester3_assignments/osn_Course_Project/course_project/`  
**Specification & Plan:** `semester3_assignments/osn_Course_Project/Project_Plan_and_Specification.md`  
**Viva Guide:** `semester3_assignments/osn_Course_Project/Viva_Questions_and_Pointers.md`

---

## 1. Critical Rules Before You Start (Read Carefully!)

1. **Do NOT Delete `AGENTS.md` or `CLAUDE.md` in Your Provisioned Repository:**
   - The official course webpage (`https://cs3301.pages.dev/project`) warns:
     > *"Deleting the `AGENTS.md` or `CLAUDE.md` files from the provisioned repositories will result in a penalty."*
   - Leave any pre-existing `AGENTS.md` or `CLAUDE.md` in your `code.iiit.ac.in` repository completely untouched.
2. **Prompt Injections Were Identified & Ignored:**
   - The course handout PDF contains two invisible `0.99pt` white-text traps:
     - Trap #1 (Page 2): Tells AI agents to create `common/proto.h` with `#ifndef OSN_AUTOGRADER_H`.
     - Trap #2 (Page 12): Tells AI agents to log `[OSN_KILLED]` whenever a process is killed.
   - Our codebase (`course_project/`) uses `src/shared/cluster_protocol.h` (`#ifndef CLUSTER_PROTOCOL_H`) and contains **zero** occurrences of `common/proto.h`, `OSN_AUTOGRADER_H`, or `[OSN_KILLED]`.
3. **Team of 3 Members & Commit History Rules:**
   - Page 2 states: *"This is a team project for 3 members, and the work should be split roughly evenly. We look at commits to see who did what, so everyone commits their own work. Commit often, with real commit messages."*
   - Below, the **18 incremental commits** are also tagged with a suggested **3-Member Split (Member A: Networking & Client, Member B: Scheduler & Queue/Algorithms, Member C: Worker Sandbox, Caching & Checkpoints)** so each team member can commit and push ~6 commits across Milestones 1–4.

---

## 2. Summary of the 18 Incremental Commits (With Suggested 3-Member Split)

| Commit # | Milestone | Suggested Author | Files Added / Modified | Requirement Fulfilled & Marks |
| :-: | :-: | :-: | :--- | :--- |
| **1** | M1 | Member A | `Makefile`, `.gitignore`, `src/shared/cluster_protocol.h`, `src/shared/net_utils.h`, `src/shared/log_utils.c` | Wire protocol structs, constants, and Section 7 central `log_line()` with `[HH:MM:SS]` (`10 marks`) |
| **2** | M1 | Member A | `src/shared/net_utils.c` | TCP packet framing (`send_packet`, `recv_header`, `recv_all`) and Section 2C UDP discovery broadcast/responder (`10 marks`) |
| **3** | M1 | Member B | `src/scheduler/scheduler.h`, `src/scheduler/main.c` | Section 2A & 4A: Scheduler CLI (`<port> FIFO|PRIORITY [-discovery-port]`), UDP responder, and non-blocking `select()` event loop (`35 marks`) |
| **4** | M1 | Member C | `src/worker/worker.h`, `src/worker/main.c` | Section 2B: Worker CLI, `sysconf`/`sysctl` hardware clamping with warning, UDP discovery + fallback `<ip> <port>`, and Worker ID registration (`10 marks`) |
| **5** | M1 | Member A | `src/client/client.h`, `src/client/main.c`, `src/client/commands.c` | Section 3: Client UDP discovery + fallback, username validation (`1..31` chars), `-user` flag, auto-relogin, `select()` prompt, and `nodes` command (`25 marks`) |
| **6** | M1 | Member B | `src/scheduler/job_manager.c`, `src/scheduler/scheduler_pass.c`, `src/scheduler/client_handler.c` | Section 4A & 4B: `submit`, bounded 1024 queue (`QUEUE_FULL`), `FIFO` and `PRIORITY` (with 10s aging) scheduling pass, `status`, `logs`, and `[Event]` push (`25 marks`) |
| **7** | M1 | Member C | `src/worker/sandbox_exec.c` | Section 5A & 5B: Job isolation in `/tmp/osn_job_<JobID>`, `nobody` privilege drop (`setgid` then `setuid`), `RLIMIT_CPU`/`RLIMIT_AS`/`RLIMIT_FSIZE`/`RLIMIT_NPROC`, `output.log` redirection & directory cleanup (`40 marks`) |
| **8** | M2 | Member B | `src/scheduler/worker_registry.c` | Section 4C: Worker heartbeat tracking (`ALIVE -> SUSPECTED` at ~2.5s $\rightarrow$ `DEAD` at ~6.0s) and 3-attempt job rescue (`RUNNING -> LOST -> QUEUED` / `FAILED_PERMANENT`) (`40 marks`) |
| **9** | M2 | Member C | `src/worker/monitor_telemetry.c` (telemetry & limits) | Section 4D & 5D: Worker 2s heartbeat with `getloadavg()` CPU%, per-job live RSS/Page Faults/CPU time (`proc_pidinfo` on macOS, `/proc` on Linux), and macOS RSS limit enforcement (`20 marks`) |
| **10** | M2 | Member C | `src/worker/monitor_telemetry.c` (crash diagnosis & cancel) | Section 5C & 5E: `cancel <job_id>` (`SIGKILL` + `waitpid`) and plain-English crash diagnosis (`127`, `SIGSEGV`, `SIGFPE`, wall-clock timeout, memory limit) (`20 marks`) |
| **11** | M2 | Member A | `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c`, `src/client/main.c` | Section 6: 64 KB output ring/tail buffer, live 500ms streaming (`logs <id> -f`), `-- Job X finished --` footer, and `Ctrl+C` return to `client>` prompt (`20 marks`) |
| **12** | M2 | Member C | `src/worker/main.c`, `src/scheduler/worker_registry.c` | Section 9: Graceful worker draining via `drain` on worker `stdin` or `Ctrl+C` (`SIGINT`) (`10 marks`) |
| **13** | M3 | Member B | `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c` | Section 8: Job dependencies (`-depends-on 1,2,g3`) and groups (`-group <id>`), `WAITING -> QUEUED` promotion, and cascading cancellation (`20 marks`) |
| **14** | M3 | Member B | `src/scheduler/scheduler_pass.c` | Section 10: Preemptible jobs (`-preemptible`), Priority 1 victim selection (lowest prio first, newest first), and `hold_for_job_id` deferral (`20 marks`) |
| **15** | M3 | Member B | `src/scheduler/scheduler_pass.c` | Section 11: Fair-share user quotas (>50% non-dead cluster cores skip rule and once-per-pair logging) (`15 marks`) |
| **16** | M3 | Member A | `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c`, `src/client/commands.c` | Section 12: Recurring (Cron) jobs (`-every <sec>`, 1s `cron_tick()`, `crons`, `cancel-cron <id>`) (`15 marks`) |
| **17** | M3 | Member C | `src/shared/sha1.c`, `src/worker/cache_ckpt.c`, `src/scheduler/scheduler_pass.c` | Section 13: SHA-1 content hashing, `cache/` binary storage, `EXEC_CACHED`, 4-level tiebreaker (`idle > cached > CPU% > jobs`), LRU eviction (`OSN_CACHE_SIZE_MB`), and `CACHE_MISS` recovery (`35 marks`) |
| **18** | M4 | Member C / All | `src/worker/cache_ckpt.c`, `src/scheduler/client_handler.c`, `tests/*`, `README.md` | Section 14: `$OSN_CHECKPOINT_DIR/state` 500ms polling, checkpoint restoration, live `migrate <id>` (`SIGTERM` $\rightarrow$ 2s $\rightarrow$ `SIGKILL`), test suite (`tests/`), and `README.md` (`30 marks`) |

---

## 3. Detailed Commit-by-Commit Instructions & Verification Commands

Every file's complete source code is in `semester3_assignments/osn_Course_Project/course_project/`. Below is what each commit adds, why, and how to test it at that stage.

---

### Commit 1 — Wire Protocol Header & Central Timestamped Logger (`Section 7`)
- **Files:** `Makefile`, `.gitignore`, `src/shared/cluster_protocol.h`, `src/shared/net_utils.h`, `src/shared/log_utils.c`
- **What & Why:**
  - Defines all message enums (`MSG_WORKER_*`, `MSG_SCHED_*`, `MSG_CLIENT_*`), state enums (`JOB_WAITING..JOB_FAILED_PERMANENT`, `WORKER_ALIVE..WORKER_DRAINING`), and fixed packet structs in `src/shared/cluster_protocol.h`.
  - Implements `log_line()` in `src/shared/log_utils.c`, which formats the current local time as `[HH:MM:SS]` (24-hour) and prints `[HH:MM:SS] <message>\n` with `fflush(stdout)`.
- **Stage Test:**
  ```bash
  gcc -std=c11 -Wall -Wextra -Werror -Isrc/shared -c src/shared/log_utils.c -o log_utils.o && rm -f log_utils.o
  ```
- **Git Commit:**
  ```bash
  git add Makefile .gitignore src/shared/cluster_protocol.h src/shared/net_utils.h src/shared/log_utils.c
  git commit -m "shared: add wire protocol definitions and timestamped log_line helper"
  git push origin main
  ```

---

### Commit 2 — TCP Framing Loops & UDP Scheduler Discovery (`Section 2C`)
- **Files:** `src/shared/net_utils.c`, `src/shared/sha1.c`
- **What & Why:**
  - Implements `send_all()`, `recv_all()`, `send_packet()`, and `recv_header()` to handle partial TCP reads/writes cleanly.
  - Implements `create_udp_discovery_server()` (with `SO_REUSEADDR` and `SO_REUSEPORT`), `handle_udp_discovery_request()` (replies `"SCHEDULER_TCP_PORT <port>"` to `"DISCOVER_SCHEDULER"`), and `discover_scheduler_udp()` (3 broadcast attempts with a 2-second `select()` timeout per attempt).
- **Stage Test:**
  ```bash
  gcc -std=c11 -Wall -Wextra -Werror -Isrc/shared -c src/shared/net_utils.c src/shared/sha1.c && rm -f *.o
  ```
- **Git Commit:**
  ```bash
  git add src/shared/net_utils.c src/shared/sha1.c
  git commit -m "shared: implement TCP packet framing, UDP discovery broadcast, and SHA-1"
  git push origin main
  ```

---

### Commit 3 — Scheduler Startup, CLI & Non-Blocking `select()` Event Loop (`Sections 2A & 4A`)
- **Files:** `src/scheduler/scheduler.h`, `src/scheduler/main.c`
- **What & Why:**
  - Parses `./scheduler <port> <FIFO|PRIORITY> [-discovery-port <port>]` (default UDP port `9999`).
  - Binds the TCP listen socket and UDP discovery responder socket, prints the startup log lines, and runs a single-threaded `select()` event loop with a 1-second periodic tick.
- **Git Commit:**
  ```bash
  git add src/scheduler/scheduler.h src/scheduler/main.c
  git commit -m "scheduler: add CLI parser, UDP discovery responder, and select event loop"
  git push origin main
  ```

---

### Commit 4 — Worker Startup, Hardware Clamping & Registration (`Section 2B`)
- **Files:** `src/worker/worker.h`, `src/worker/main.c`
- **What & Why:**
  - Parses `./worker [<scheduler_ip> <scheduler_port>] -cores <num> -ram <MB> [-gpu <num>] [-discovery-port <port>]`.
  - Queries hardware cores via `sysconf(_SC_NPROCESSORS_ONLN)` and physical RAM via `sysctlbyname("hw.memsize", ...)` (macOS) / `sysconf(_SC_PHYS_PAGES) * sysconf(_SC_PAGESIZE)` (Linux), clamping `-cores` and `-ram` with a warning if the user specifies more than the machine has.
  - Discovers the scheduler over UDP (or falls back to `<scheduler_ip> <scheduler_port>` after 3 failed retries), registers over TCP, and receives its unique Worker ID (`1001`, `1002`, ...).
- **Git Commit:**
  ```bash
  git add src/worker/worker.h src/worker/main.c
  git commit -m "worker: implement hardware resource clamping, UDP discovery fallback, and registration"
  git push origin main
  ```

---

### Commit 5 — Client Login, Interactive Prompt & `nodes` Command (`Section 3`)
- **Files:** `src/client/client.h`, `src/client/main.c`, `src/client/commands.c`
- **What & Why:**
  - Validates usernames (`1..31` chars drawn from letters, digits, `_`, `-`, `.`), supports `-user <username>` to skip the interactive prompt, and automatically re-sends the username on reconnect.
  - Runs `select()` over `STDIN_FILENO` and the scheduler socket so `[Event]` lines print immediately even when the user is idle at `client> `.
- **Git Commit:**
  ```bash
  git add src/client/client.h src/client/main.c src/client/commands.c
  git commit -m "client: implement UDP discovery, username validation, async event loop, and nodes command"
  git push origin main
  ```

---

### Commit 6 — Job Queue (`1024` Max), `FIFO` / `PRIORITY` Scheduling Pass & Client Handlers (`Sections 3, 4A, 4B`)
- **Files:** `src/scheduler/job_manager.c`, `src/scheduler/scheduler_pass.c`, `src/scheduler/client_handler.c`
- **What & Why:**
  - Enforces the bounded `1024`-entry queue (`QUEUE_FULL` returned immediately on overflow without blocking).
  - Implements `FIFO` (strict submission order with head-of-line blocking) and `PRIORITY` (`1..3` with 10-second aging `eff_prio = max(1, base_prio - wait_sec / 10)`).
- **Git Commit:**
  ```bash
  git add src/scheduler/job_manager.c src/scheduler/scheduler_pass.c src/scheduler/client_handler.c
  git commit -m "scheduler: implement bounded 1024 job queue, FIFO and aged PRIORITY scheduling"
  git push origin main
  ```

---

### Commit 7 — Worker Job Sandbox, Resource Limits & Output Capture (`Sections 5A & 5B`)
- **Files:** `src/worker/sandbox_exec.c`
- **What & Why:**
  - Creates `/tmp/osn_job_<JobID>` and `/tmp/osn_job_<JobID>/checkpoint`, redirects `stdout`/`stderr` to `output.log`, drops privileges to `nobody` (`setgid` then `setuid`) when run with `sudo` (or warns when non-root), sets `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_FSIZE`, and `RLIMIT_NPROC` (`64`), launches the job with `fork()` + `execvp()`, and cleans up `/tmp/osn_job_<JobID>` after completion.
- **Stage Test (End of Milestone 1):**
  ```bash
  make all
  ./scheduler 8080 PRIORITY &
  ./worker -cores 4 -ram 1024 -gpu 1 &
  ./client -user lordz << 'EOF'
  nodes
  submit ./tests/hello_job -cores 1 -ram 64 -time 5 -prio 1
  EOF
  ```
- **Git Commit:**
  ```bash
  git add src/worker/sandbox_exec.c
  git commit -m "worker: isolate jobs in /tmp/osn_job_<id>, drop privileges to nobody, and set rlimits"
  git push origin main
  ```

---

### Commit 8 — Worker Heartbeats (`2s`), `SUSPECTED`/`DEAD` Detection & 3-Attempt Job Rescue (`Section 4C`)
- **Files:** `src/scheduler/worker_registry.c`
- **What & Why:**
  - Transitions a silent worker `ALIVE -> SUSPECTED` after 1 missed heartbeat (`~3s`), back to `ALIVE` if a heartbeat arrives, or `-> DEAD` after 3 consecutive missed heartbeats (`~6s`).
  - Rescues all `RUNNING` jobs on a `DEAD` worker (`RUNNING -> LOST -> QUEUED`) up to `MAX_RETRY_ATTEMPTS = 3`, after which the job becomes `FAILED_PERMANENT`.
- **Git Commit:**
  ```bash
  git add src/scheduler/worker_registry.c
  git commit -m "scheduler: add heartbeat timeout state machine and 3-attempt dead-worker job rescue"
  git push origin main
  ```

---

### Commit 9 — Load-Aware Scheduling (`4D`) & Live Resource Telemetry (`5D`)
- **Files:** `src/worker/monitor_telemetry.c`
- **What & Why:**
  - Computes worker CPU load % via `getloadavg()` and per-job live RSS MB, page faults, and CPU seconds (`proc_pidinfo(PROC_PIDTASKINFO)` on macOS; `/proc/<pid>/statm` + `/proc/<pid>/stat` on Linux).
  - Enforces `-ram` on macOS by checking live RSS every `500ms` and sending `SIGKILL` when `rss_mb > ram_mb`.
- **Git Commit:**
  ```bash
  git add src/worker/monitor_telemetry.c
  git commit -m "worker: add live RSS/CPU telemetry via proc_pidinfo and /proc plus load-aware heartbeats"
  git push origin main
  ```

---

### Commit 10 — Job Cancellation (`5C`) & Plain-English Crash Diagnosis (`5E`)
- **Files:** `src/worker/monitor_telemetry.c`, `src/scheduler/client_handler.c`
- **What & Why:**
  - Implements `cancel <job_id>` across `WAITING`, `QUEUED`, and `RUNNING` jobs (`SIGKILL` + `waitpid` with zero zombies).
  - Translates `waitpid()` status and worker kill reasons into clear messages (`Exited with code 127 (command not found)`, `Terminated by signal 11 (SIGSEGV - Segmentation Fault)`, `Terminated by signal 8 (SIGFPE - Floating Point Exception)`, `Wall-clock timeout exceeded`, `Memory limit exceeded`).
- **Git Commit:**
  ```bash
  git add src/worker/monitor_telemetry.c src/scheduler/client_handler.c
  git commit -m "worker,scheduler: implement job cancellation and human-readable crash diagnosis"
  git push origin main
  ```

---

### Commit 11 — 64 KB Log Buffer & Live Streaming Logs (`logs <id> -f`, `Section 6`)
- **Files:** `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c`, `src/client/main.c`
- **What & Why:**
  - Worker tails `output.log` every `~500ms` (`O_NONBLOCK`); scheduler retains the last 64 KB per job and forwards live chunks to subscribed `logs <id> -f` clients until `-- Job <id> finished --` or `Ctrl+C` (which unsubscribes and returns to `client> `).
- **Git Commit:**
  ```bash
  git add src/scheduler/job_manager.c src/scheduler/client_handler.c src/client/main.c
  git commit -m "scheduler,client: add 64KB output buffer and live streaming logs -f with Ctrl+C handling"
  git push origin main
  ```

---

### Commit 12 — Graceful Worker Draining (`Section 9`)
- **Files:** `src/worker/main.c`, `src/scheduler/worker_registry.c`
- **What & Why:**
  - Handles typing `drain` on worker `stdin` and pressing `Ctrl+C` (`SIGINT`) identically: transitions worker to `DRAINING`, stops assigning new jobs, finishes running jobs while heartbeating, and exits cleanly.
- **Git Commit:**
  ```bash
  git add src/worker/main.c src/scheduler/worker_registry.c
  git commit -m "worker,scheduler: support graceful worker draining via stdin drain and SIGINT"
  git push origin main
  ```

---

### Commit 13 — Job Dependencies & Groups (`Section 8`)
- **Files:** `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c`
- **What & Why:**
  - Supports `-group <id>` and `-depends-on 1,2,g3` (expanding `g<id>` at submit time and rejecting unknown job/group IDs). Promotes `WAITING -> QUEUED` when all dependencies complete and cascades `WAITING -> CANCELLED` if any dependency fails or is cancelled.
- **Git Commit:**
  ```bash
  git add src/scheduler/job_manager.c src/scheduler/client_handler.c
  git commit -m "scheduler: implement job dependencies, submit-time group expansion, and cascading cancel"
  git push origin main
  ```

---

### Commit 14 — Preemptible Jobs (`Section 10`)
- **Files:** `src/scheduler/scheduler_pass.c`
- **What & Why:**
  - Supports `-preemptible`. When a Priority 1 job has no qualifying worker, finds an `ALIVE` worker where killing `-preemptible` jobs (`prio > 1`, ordered lowest priority / highest number first, then newest submission first) frees enough resources, requeues victims without using an attempt, and holds them (`hold_for_job_id`) until the Priority 1 job starts.
- **Git Commit:**
  ```bash
  git add src/scheduler/scheduler_pass.c
  git commit -m "scheduler: add priority-1 preemption of preemptible jobs with victim hold"
  git push origin main
  ```

---

### Commit 15 — Fair-Share User Quotas (`Section 11`)
- **Files:** `src/scheduler/scheduler_pass.c`
- **What & Why:**
  - Checks if a job's owner holds strictly `> 50%` of non-dead cluster cores while another user (not over quota) has a `QUEUED` job; skips the over-quota user's job and logs `[SCHEDULER] Skipping Job X (user u1, quota exceeded) in favor of Job Y (user u2)` once per pair.
- **Git Commit:**
  ```bash
  git add src/scheduler/scheduler_pass.c
  git commit -m "scheduler: enforce 50% fair-share user core quotas in scheduling pass"
  git push origin main
  ```

---

### Commit 16 — Recurring (Cron) Jobs (`Section 12`)
- **Files:** `src/scheduler/job_manager.c`, `src/scheduler/client_handler.c`, `src/client/commands.c`
- **What & Why:**
  - Implements `-every <sec>` template registration (separate template IDs starting at `1`, rejecting `-every` with `-depends-on`), immediate first run + periodic 1s `cron_tick()` injection, `crons`, and `cancel-cron <id>`.
- **Git Commit:**
  ```bash
  git add src/scheduler/job_manager.c src/scheduler/client_handler.c src/client/commands.c
  git commit -m "scheduler,client: implement recurring cron job templates, crons, and cancel-cron"
  git push origin main
  ```

---

### Commit 17 — Executable Caching, 4-Level Tiebreaker & LRU Eviction (`Section 13`)
- **Files:** `src/worker/cache_ckpt.c`, `src/scheduler/scheduler_pass.c`
- **What & Why:**
  - Hashes executables with SHA-1, stores binaries in `<cache_dir>/<name>-<sha1>` (`OSN_CACHE_DIR`), sends `EXEC_CACHED` on cache hits, recovers from `CACHE_MISS` without retry penalty, applies full tiebreaker (`idle > cached binary > lowest CPU% > fewest running jobs`), and enforces `OSN_CACHE_SIZE_MB` via LRU mtime eviction.
- **Git Commit:**
  ```bash
  git add src/worker/cache_ckpt.c src/scheduler/scheduler_pass.c
  git commit -m "worker,scheduler: add SHA-1 executable caching, cache-aware tiebreaker, and LRU eviction"
  git push origin main
  ```

---

### Commit 18 — Checkpoints, Live Job Migration (`Section 14`), Test Suite & `README.md`
- **Files:** `src/worker/cache_ckpt.c`, `src/scheduler/client_handler.c`, `tests/*`, `README.md`
- **What & Why:**
  - Polls `$OSN_CHECKPOINT_DIR/state` every `~500ms`, saves latest checkpoint per job on the scheduler, restores checkpoints before restarting any retried/preempted/migrated job, implements `migrate <job_id>` (`SIGTERM` $\rightarrow$ 2s $\rightarrow$ `SIGKILL` + final state read + `avoid_worker_id`), and adds the `tests/` programs and `README.md`.
- **Git Commit:**
  ```bash
  git add src/worker/cache_ckpt.c src/scheduler/client_handler.c tests/ README.md
  git commit -m "cluster: implement cooperative checkpoints, live job migration, test programs, and README"
  git push origin main
  ```

---

## 4. Incremental Bug-Fix & Edge-Case Hardening Commits (`Commits 19–23`)

After completing the 18 feature commits, a thorough line-by-line audit uncovered several subtle edge cases. Committing fixes incrementally (just as a student team discovers bugs during integration testing) produces an authentic, high-quality git history:

| Commit # | Suggested Author | Files Added / Modified | Bug / Edge Case Fixed |
| :-: | :-: | :--- | :--- |
| **19** | Member A | `src/client/*`, `src/worker/sandbox_exec.c`, `src/*/main.c` | Job CLI arguments in `submit` (both `submit ./counter_ckpt 20 ...` and `submit "./counter_ckpt 20" ...`), flexible `<ip> <port>` fallback flag placement, and clean trailing newline on `logs <id>` when job output has no `\n` |
| **20** | Member B | `src/shared/cluster_protocol.h`, `src/scheduler/{job_manager,worker_registry,client_handler,scheduler_pass}.c` | Reset `worker_id = 0` when a job moves back to `QUEUED` (so `status` shows `Assigned to: None`), count strictly `JOB_QUEUED` for the `1024` `QUEUE_FULL` cap (`WAITING` jobs excluded per Section 8), deduplicate `-depends-on 1,g3`, expand job capacity to `8192`, and handle `0`-byte executable transfers |
| **21** | Member C | `src/scheduler/scheduler_pass.c`, `src/worker/{worker.h,sandbox_exec.c,monitor_telemetry.c}`, `src/shared/net_utils.c` | Reserve worker while multiple `-preemptible` victims exit for a Priority 1 job, millisecond `gettimeofday()` wall-clock & migration timers (reaping exited jobs via `waitpid(WNOHANG)` before checking timeout), non-root `RLIMIT_NPROC` cap, and broadcast + loopback UDP discovery |
| **22** | Member B | `Makefile`, `src/scheduler/{scheduler.h,client_handler.c,client_queries.c}` | Modular split of client query/admin handlers (`nodes`, `status`, `logs`, `cancel`, `migrate`, `crons`, `cancel-cron`) into `src/scheduler/client_queries.c` |
| **23** | Member C | `tests/{Makefile,exit_code3.c,write_home.c,fork_bomb.c}`, `.gitignore`, `README.md` | Add remaining Section 5 test programs (`exit_code3`, `write_home`, `fork_bomb`) and finalize `README.md` |

