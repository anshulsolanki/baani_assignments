# CS3.301 Operating Systems and Networks — Mini Project 3
## Complete Concept Walkthrough, Code Pointers & TA Viva Guide for Baani

---

## 1. Plain-English Walkthrough of Every Part

### Part 1: Airport Troubles (`concurrency/airport-troubles/` — 80 Marks)
- **What Problem We Are Solving:**
  Every person in Gotham Intergalactic Airport (`Student`, `Immigration officer 1`, `Baggage handler 1`, `Baggage handler 2`) runs as a real OS thread (`pthread_t`), sharing limited resources (3 passport scanners, 1 hall with an officer lockout rule, and a baggage belt of capacity 2). Actions take **symbolic** time (`2` units for `scans passport`, `1` unit for everything else), and calling `sleep()` / `usleep()` is penalized.
- **How Our Discrete-Event Logical Clock Works (`clock.c`):**
  1. Instead of sleeping in wall-clock seconds, a thread performing an action of duration `d` picks a free index `slot` in `sim->slot_used[]`, sets `sim->wake_time[slot] = current_time + d`, and sleeps on `pthread_cond_wait(&sim->cv, &sim->lock)` inside `wait_until_time()`.
  2. Any thread waiting for a condition (e.g., waiting for a free scanner or waiting for `!officer_in_hall`) sleeps inside `sim_wait_condition()`, which records `seen_version = sim->state_version` and increments `sim->checked_count`.
  3. **Quiescence Invariant:** When `timed_count + checked_count == active_threads` (and `finishing_phase_count == 0`), **every single live thread** in the process has either scheduled a future wakeup or already verified against the latest `state_version` that it cannot start any action at `current_time`. Only then does `try_advance_clock()` scan `sim->wake_time[]` with a simple `for` loop and jump `sim->current_time` directly to the smallest `wake_time`!
  4. **Two-Phase Tick (`finishing_phase_count`):** At the new timestamp `t`, all actions **finishing** at `t` run **Phase 1** first (`free_scanners++`, `unscanned_in_hall--`, `officer_in_hall = 0`, `belt_slots_used--`) before calling `sim_complete_action()`. Waiting threads stay blocked until `finishing_phase_count == 0` (**Phase 2**), guaranteeing freed scanners or belt slots at `t` are immediately available at `t`.

---

### Part 2: Symbolic Links in `xv6` (`xv6/` — 60 Marks)
- **Hard Link vs. Symbolic Link (Soft Link):**
  - A **hard link** (`link()`) adds a new directory entry (`name -> inum`) pointing directly to the **same existing inode** and increments `ip->nlink++`. If you `unlink` the original name, the file still exists (`nlink >= 1`). Hard links cannot point to nonexistent files.
  - A **symbolic link** (`symlink(target, path)`) allocates a **brand-new inode** of type `T_SYMLINK` (`4`) and stores the **string path** `target` inside that inode's data blocks. If the target file is later deleted, the symlink becomes a *dangling symlink* and opening it fails.
- **How `sys_symlink` Works (`kernel/sysfile.c`):**
  - Wraps filesystem changes in `begin_op()` / `end_op()` (crash-safe logging).
  - Calls `create(path, T_SYMLINK, 0, 0)` which allocates a locked `T_SYMLINK` inode (or returns `0` if `path` already exists).
  - Writes `strlen(target)` bytes into the inode at offset `0` via `writei(ip, 0, (uint64)target, 0, len)`, then calls `iunlockput(ip)` and `end_op()`.
- **How `sys_open` & `create` Work (`kernel/sysfile.c`):**
  - Note in `kernel/fcntl.h`: `0x800` was already taken by `O_APPEND`, so we defined `#define O_NOFOLLOW 0x1000`.
  - Why did we also update 1 line in `create()`? Because in `symlinktest.c` (`createsymlink()`), the shell/test runs `open("/testsymlink/l", O_WRONLY | O_CREATE | O_APPEND)` where `l` is an **existing symlink** pointing to `t`! In stock xv6, `create()` failed whenever an existing inode wasn't `T_FILE` or `T_DEVICE`. Allowing `create(path, T_FILE, 0, 0)` to return a locked `T_SYMLINK` inode lets `sys_open()` follow `l -> t` (or reject if `O_NOFOLLOW` was also set) without overwriting `l`!
  - Inside `sys_open()`, a `for (depth = 0; ; depth++)` loop checks if `ip->type == T_SYMLINK && !(omode & O_NOFOLLOW)`. If so, it checks `depth < 10`, reads `ip->size` bytes into `path` with `readi()`, null-terminates `path`, calls `iunlockput(ip)`, and repeats until reaching a non-symlink inode (or failing at `depth >= 10` on cycles).

---

### Part 3: Birthday Boy — Parallel Bellman-Ford (`concurrency/birthday-boy/` — 30 Marks)
- **How We Avoid Data Races Without Slow Per-Edge Locks (`solver.c`):**
  - If two threads relax edges `(u1 -> w)` and `(u2 -> w)` into the **same destination vertex `w`** simultaneously, writing `dist[w]` directly causes a **read-write / write-write data race**, while locking a mutex on every edge relaxation destroys parallelism!
  - Instead:
    1. In `solve_bellman_ford()`, we expand the `E` undirected edges into `2E` directed edges (`u -> v` and `v -> u`) and sort them by destination vertex `dst` using standard C `qsort()` (`compare_edges_by_dst()`).
    2. We divide `[0, V)` across the `T` threads (`v_start = (t * V) / T`, `v_end = ((t + 1) * V) / T`) along with their contiguous slice of incoming edges `[edge_start, edge_end)`, so **no two threads share any destination vertex `v`**.
    3. We keep two distance arrays (`dist_curr` and `dist_next`). In each of the `V - 1` iterations:
       - **Phase 1:** Every thread reads `dist_curr[u]` (read-only!) and writes only to its own slice `dist_next[v]` (`v` in `[v_start, v_end)`).
       - `barrier_wait(&solver->barrier)` waits for all `T` threads.
       - **Phase 2:** Every thread copies `dist_curr[v] = dist_next[v]` for its own slice `[v_start, v_end)`.
       - `barrier_wait(&solver->barrier)` before starting the next iteration.

---

## 2. "What to Show the TA" — Quick File & Line Pointers

### Part 1 (`concurrency/airport-troubles/`)
- **Where each person's thread is spawned:** `main.c` lines `130–160` (`pthread_create` for 2 handlers, 1 officer, and `num_students` students while holding `sim.lock`).
- **How symbolic time jumps without `usleep`:** `clock.c` -> `try_advance_clock()` (lines `10–47`), checking `timed_count + checked_count == active_threads` and scanning `sim->wake_time[]` to jump `sim->current_time = min_time`.
- **Same-timestamp input order rule:** `clock.c` -> `sim_wait_arrival_turn()` (lines `156–177`).
- **Constraint 1 (No enter/leave while officer in hall):**
  - Student entry check: `actors.c` line `20` (`while (sim->officer_in_hall)`).
  - Student exit check: `actors.c` line `63` (`while (sim->officer_in_hall)`).
  - Officer waits for mid-exit students & locks hall until `leaves` finishes: `actors.c` lines `115–120` and `146`.
- **Constraint 2 & 3 (Batch approval after all hall students scan, even empty hall):** `actors.c` lines `127–140` (`while (sim->unscanned_in_hall > 0)` then batch loop setting `approved = 1` for `in_hall` students).
- **Constraint 5, 6, 7 (Belt capacity 2, stamped bags only, collect own bag after leaving hall):** `actors.c` -> `handler_thread()` (lines `161–196`) and `student_thread()` step 5 (lines `78–90`).

### Part 2 (`xv6/`)
- **`T_SYMLINK` & `O_NOFOLLOW`:** `kernel/stat.h` line `4` (`T_SYMLINK 4`) and `kernel/fcntl.h` line `7` (`O_NOFOLLOW 0x1000`).
- **`sys_symlink()` implementation:** `kernel/sysfile.c` lines `306–334`.
- **Why `O_CREATE | O_APPEND` works on an existing symlink:** `kernel/sysfile.c` line `260` in `create()` + `sys_open()` loop lines `352–393`.
- **Cycle protection (max depth 10):** `kernel/sysfile.c` line `381` (`if (depth >= 10 || target_len >= MAXPATH)`).
- **`ln -s` and `readlink`:** `user/ln.c` lines `8–14` and `user/readlink.c` lines `19–35` (`open(argv[1], O_RDONLY | O_NOFOLLOW)` + `st.type != T_SYMLINK`).

### Part 3 (`concurrency/birthday-boy/` & `README.md`)
- **Reusable generation-counted barrier:** `barrier.c` lines `16–36` (`my_gen = b->generation`).
- **Sorting edges by destination vertex (`qsort`) & vertex slicing:** `solver.c` -> `compare_edges_by_dst()` (lines `9–13`) and `solve_bellman_ford()` (lines `56–105`).
- **Race-free parallel Bellman-Ford inner loop:** `solver.c` -> `bf_worker_thread()` (lines `19–47`).
- **Fitted constant $k$ and benchmark plots:** `README.md` (`k = 3.27e-10` seconds, `plots/runtime_vs_v.png`, `plots/runtime_vs_t.png`).

---

## 3. Top 20 Likely TA Viva Questions & Model Answers

### Part 1: Airport Troubles Viva Questions

**Q1. How did you avoid using `sleep()` or `usleep()` while still running every person as a real `pthread_t`?**  
> **Answer:** We built a discrete-event logical clock in `clock.c` using one mutex (`sim->lock`), one condition variable (`sim->cv`), and simple `int` arrays (`slot_used[]`, `wake_time[]`, `wake_done[]`). When a thread starts an action of symbolic duration `d`, it reserves a slot with `wake_time[slot] = current_time + d` and blocks on `pthread_cond_wait`. Waiting threads increment `checked_count` after checking the current `state_version`. Once `timed_count + checked_count == active_threads`, we know no thread can start any more actions at `current_time`, so `try_advance_clock()` scans `wake_time[]` with a `for` loop and immediately jumps `current_time` to the minimum `wake_time`. Even a timestamp gap of `1,000,000` finishes in milliseconds.

**Q2. What would go wrong if `try_advance_clock()` jumped `current_time` before every awake thread checked its condition?**  
> **Answer:** A thread that just became eligible at `current_time` (for example, Students 1–4 becoming eligible to `receives stamp` at `t = 6` right after the officer finishes `approves`) might not have been scheduled by the OS yet. Jumping `current_time` to `7` prematurely would delay their stamp to `t = 7` or violate constraints. Tracking `state_version` and `checked_count` guarantees every active non-timed thread has inspected the latest state at `current_time` before the clock can advance.

**Q3. Why do you have `finishing_phase_count` (two-phase wakeup) at each timestamp?**  
> **Answer:** At timestamp `t`, multiple actions might finish at `t` while other threads want to start actions at `t`. For example, at `t = 3` in the example, Students 1–3 finish `scans passport` (freeing the 3 scanners) and Student 4 wants to start `scans passport` at `t = 3`. `finishing_phase_count` forces all threads finishing at `t` to increment `free_scanners` / release resources first before Phase 2 threads evaluate `free_scanners > 0`.

**Q4. How do you ensure `3 Student 10` before `3 Immigration officer 1` enters at `t = 3`, while `3 Student 20` after `3 Immigration officer 1` waits until the officer leaves?**  
> **Answer:** `sim_wait_arrival_turn()` in `clock.c` checks all earlier input events `j < event_idx` with the same arrival timestamp `my_time` and waits until `events[j].processed == 1`. So `Student 10` runs first (`!officer_in_hall`, enters hall), then `Officer 1` runs (`officer_in_hall = 1`, enters hall), and then `Student 20` marks its arrival processed, sees `officer_in_hall == 1`, and waits until the officer finishes `leaves`.

**Q5. When exactly does `officer_in_hall` become `0` — when the officer starts `leaves` or when `leaves` finishes?**  
> **Answer:** When `leaves` **finishes** (`t + 1`), after `sim_wait_action(sim, ACTION_DURATION)`! In the official example, the officer prints `6 Immigration officer 1 leaves` (`6 -> 7`), and waiting Student 5 enters at `7 Student 5 enters`, proving the hall remains locked during the 1 time unit the officer is leaving.

**Q6. What happens in your code if the TA changes the number of scanners from `3` to `5` or belt capacity from `2` to `4`?**  
> **Answer:** You only change `#define NUM_SCANNERS 5` or `#define BELT_CAPACITY 4` at the top of `airport.h` and recompile with `make` — no magic numbers are hardcoded in `actors.c` or `clock.c`.

**Q7. How do your baggage handlers know when to exit instead of waiting forever on `pthread_cond_wait`?**  
> **Answer:** Each time a student finishes `collects bag`, `sim->bags_collected` is incremented. In `handler_thread()`, the wait condition loops only while `sim->bags_collected < sim->num_students`; once `bags_collected == num_students` and `ready_count == 0`, both handlers break out, call `sim_thread_exit()`, and terminate cleanly.

---

### Part 2: `xv6` Symbolic Links Viva Questions

**Q8. Why did you define `O_NOFOLLOW` as `0x1000` instead of `0x800`?**  
> **Answer:** In our boilerplate's `kernel/fcntl.h`, `0x800` is already defined as `O_APPEND`! Using `0x800` would make `O_APPEND` and `O_NOFOLLOW` collide (which would immediately break `createsymlink()` in `symlinktest.c` where `O_WRONLY | O_CREATE | O_APPEND` is passed!). Using the next unused bit `0x1000` avoids any flag collision.

**Q9. Walk through what happens when `echo "hi" >> link` (`open("link", O_WRONLY | O_CREATE | O_APPEND)`) runs on an existing symlink `link -> target`.**  
> **Answer:**
> 1. In `sys_open()`, `depth = 0`: because `omode & O_CREATE` is set, it calls `create("link", T_FILE, 0, 0)`.
> 2. In `create()`, `dirlookup` finds `"link"` (`ip->type == T_SYMLINK`), unlocks `dp`, locks `ip`, and returns `ip` (because we added `ip->type == T_SYMLINK` to line 260 of `create()`).
> 3. Back in `sys_open()`, since `O_NOFOLLOW` is not set, it reads `"target"` from `ip` via `readi()`, unlocks/puts `"link"`, and loops to `depth = 1` with `path = "target"`.
> 4. At `depth = 1`, `create("target", T_FILE, 0, 0)` returns the locked `T_FILE` inode of `"target"` (or creates it if missing).
> 5. `f->off` is set to `ip->size` (`O_APPEND`), `"hi"` is appended to `"target"`, and `"link"` remains untouched as a `T_SYMLINK`!

**Q10. What happens if someone calls `symlink("a", "b")` and `"b"` already exists?**  
> **Answer:** `sys_symlink()` calls `create(path, T_SYMLINK, 0, 0)`. In `create()`, `dirlookup` finds `"b"`, checks `if (type == T_FILE && ...)` which is **false** because `type` is `T_SYMLINK`, unlocks and puts `ip`, and returns `0`. `sys_symlink()` calls `end_op()` and returns `-1`.

**Q11. Why must `sys_symlink` call `begin_op()` and `end_op()`?**  
> **Answer:** xv6 uses a write-ahead crash-recovery log (`kernel/log.c`). Allocating an inode (`ialloc`), updating its metadata (`iupdate`), adding a directory entry (`dirlink`), and writing the target path (`writei`) modify multiple disk blocks; wrapping them in `begin_op()` / `end_op()` makes the symlink creation atomic with respect to crashes.

**Q12. In `sys_open()`, why is it critical to call `iunlockput(ip)` on each symlink inode before looking up the next target path?**  
> **Answer:** Two reasons: (1) **Deadlock prevention** — if a symlink points to itself (`a -> a`), holding `a`'s sleeplock (`ilock`) while trying to `ilock(a)` again on the next iteration would immediately self-deadlock! (2) **Inode cache leak prevention** — `namei`/`create` increments the in-memory inode reference count `ip->ref`, so failing to `iput(ip)` would leak `NINODE` (`50`) cache entries.

**Q13. What happens when `rm symlink_name` (`unlink`) is executed on a symlink?**  
> **Answer:** Because `sys_unlink()` uses `nameiparent()` + `dirlookup()` directly and does **not** follow symlinks, `unlink` deletes the symlink directory entry and frees the `T_SYMLINK` inode without touching the target file — matching standard UNIX `rm` behavior!

**Q14. How does `readlink` distinguish a regular file from a symbolic link?**  
> **Answer:** `user/readlink.c` opens the path with `O_RDONLY | O_NOFOLLOW` so `sys_open` returns a file descriptor to the inode itself without following it. It then calls `fstat(fd, &st)` and checks `if (st.type != T_SYMLINK)`. If someone runs `readlink README.md` on a regular file (`T_FILE`), it prints an error to `stderr` and exits with status `1`.

---

### Part 3: Birthday Boy (Parallel Bellman-Ford & Analysis) Viva Questions

**Q15. Why didn't you just split the raw edge list `0..E-1` across threads and write directly into one shared `dist[]` array?**  
> **Answer:** Two reasons:
> 1. **Data race:** Two threads relaxing `(u1 -> w)` and `(u2 -> w)` simultaneously would race on reading and writing `dist[w]` (undefined behavior in C, and one thread could overwrite a smaller distance with a larger one).
> 2. **Asynchronous cascading vs synchronous rounds:** Reading and writing the same `dist[]` array within an iteration mixes round `k` and round `k+1` values non-deterministically.
> Grouping directed edges by destination `dst` so each thread exclusively owns `[v_start, v_end)` in `dist_next[]` while reading `dist_curr[]` eliminates **100% of locks and data races** inside the relaxation loop!

**Q16. Why does your `barrier_wait()` in `barrier.c` need a `generation` counter instead of just checking `while (b->waiting_count < b->total_threads)`?**  
> **Answer:** Because the barrier is **reused** `2 * (V - 1)` times in a tight loop! If the last arriving thread reset `waiting_count = 0` and broadcast, waking threads checking `waiting_count < total_threads` would get stuck forever (or a fast thread could re-enter the next barrier round before slow threads exited the previous one). Capturing `int my_gen = b->generation;` on entry and waiting `while (b->generation == my_gen)` makes every barrier phase completely isolated.

**Q17. Why didn't you stop Bellman-Ford early as soon as no distance changed in an iteration?**  
> **Answer:** On random connected graphs with `V = 3000, E = 120,000`, the diameter is only `~4–5` hops! With early termination, the loop would stop after ~5 rounds instead of `V - 1 = 2999` rounds, reducing complexity from $\Theta(VE)$ to $O(E \cdot \text{diameter})$ and masking the theoretical $O(VE)$ Bellman-Ford scaling required in the performance analysis plot ($k \cdot V \cdot E$). Running all `V - 1` iterations faithfully measures parallel Bellman-Ford's $\Theta(VE)$ work. *(If the TA asks how to add early exit live: add a shared `any_changed` flag set if any thread updates `dist_next[v]`, checked after the second barrier!)*

**Q18. How did you find the constant $k$ for the theoretical curve $k \cdot V \cdot E$ in Plot 1?**  
> **Answer:** Each data point gave an experimental runtime $t_i$ at $(V_i, E_i)$. Minimizing squared error $\sum_i (t_i - k (V_i E_i))^2$ gives the closed-form least-squares fit $k = \frac{\sum_i t_i (V_i E_i)}{\sum_i (V_i E_i)^2} = 3.27 \times 10^{-10}\text{ seconds}$ per $(V \cdot E)$ unit.

**Q19. Why is the experimental runtime slightly above $k \cdot V \cdot E$ for small `V` (`500–1500`), and right on top of $k \cdot V \cdot E$ for large `V` (`2500–4000`)?**  
> **Answer:** Because real runtime has lower-order overheads: $T(V, E) = c_{\text{spawn}} + c_{\text{barrier}} \cdot 2(V - 1) + k V E$. At `V = 500`, edge relaxation only takes `~3.3 ms`, so thread spawning and `998` barrier synchronizations (`~4 ms`) are a noticeable fraction. By `V = 3000–4000`, the quadratic $k V E$ term (`118–209 ms`) dominates completely.

**Q20. Explain the shape of Plot 2 (Runtime vs. `T`): why does runtime drop from `T = 1` to `T = 3..4`, step up at `T = 6..8`, and become slower than `T = 1` at `T = 32`?**  
> **Answer:**
> 1. **`T = 1 -> 3, 4` (`313 ms -> 138 ms`, `2.27x` speedup):** Work per thread drops as `2E / T` across the 4 high-frequency Performance cores; speedup is `< 4x` due to Amdahl's Law (sequential setup + `5,998` barriers + shared memory-bus bandwidth on random `dist_curr[u]` reads).
> 2. **`T = 4 -> 6, 8` (`142 ms -> 185 ms`):** Our 8-core CPU has 4 Performance cores + 4 slower Efficiency cores. Because every iteration hits two global barriers (`5,998` barriers total), all fast P-core threads must wait for the slowest E-core thread in every single round!
> 3. **`T = 16 -> 32` (`209 ms -> 375 ms`):** Now `T` exceeds physical cores (`T > 8`). Threads preempt each other mid-iteration, and reaching `5,998` barriers forces tens of thousands of kernel context switches (`pthread_cond_wait` / `futex` / `ulock` wakeups) and mutex contention on `barrier->lock`, costing more time than single-threaded execution!
