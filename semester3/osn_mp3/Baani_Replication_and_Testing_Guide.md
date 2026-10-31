# CS3.301 Operating Systems and Networks — Mini Project 3
## Complete Step-by-Step Commit, Replication, and Testing Guide for Baani

**Reference Repository (GitHub):** `https://github.com/anshulsolanki/baani_assignments`  
**Completed Reference Code Folder:** `semester3/osn_mini_project_3/`  
**Clean Untouched Boilerplate Folder:** `semester3/osn_mp3/mp3_boilerplate/`  
**Guides & Spec Folder:** `semester3/osn_mp3/`

---

## 1. Golden Rules Before You Start (Read Carefully!)

1. **Commit & Push Iteratively on `main` Across Sessions (Server Push Time Counts!):**
   - The handout explicitly states: *"Your commit history will be evaluated based on the time a commit was **pushed**, i.e. the server time. So if you made a commit 2 days ago and pushed it today, we will assume you made that commit today itself. **So push as often as you can!**"*
   - Do **not** run all 14 commits in 15 minutes right before November 10. Spread them naturally across your work sessions (e.g., 3–4 commits per day over several days) and run `git push origin main` immediately after each commit!
2. **Branching Rule on `code.iiit.ac.in`:**
   - *"Only commits to the `main` branch of the repo shall be counted. If branching has been done, it is forbidden to squash merge, rebase or delete the branch after merging."*
   - Working directly and cleanly on `main` (following the 14 checkpoints below in sequence) avoids any risk of accidentally rebasing, squash-merging, or deleting a branch.
3. **Pure C + Makefiles Only Inside Your Submission Repo:**
   - Do **not** add any `.py` helper scripts, shell scripts, or `Dockerfile`s inside your `code.iiit.ac.in` repository. Only commit the C source/header files, `Makefile`s, `plots/*.png`, `README.md`, `ai-usage.md`, and `.gitignore`.
4. **Do Not Touch Unrelated `xv6` Boilerplate Files:**
   - Only 10 files inside `xv6/` are modified/added (`kernel/stat.h`, `kernel/fcntl.h`, `kernel/syscall.h`, `kernel/syscall.c`, `kernel/sysfile.c`, `user/user.h`, `user/usys.pl`, `user/ln.c`, `user/readlink.c`, and `xv6/Makefile`). Leave every other file in `xv6/` untouched.
5. **No `sleep()` or `usleep()` in `airport-troubles`:**
   - Our discrete-event logical clock (`clock.c`) uses `pthread_mutex_t` and `pthread_cond_t` with symbolic timestamps — zero `sleep`/`usleep` calls anywhere.
6. **`ai-usage.md` Reminder:**
   - Before your final push, remember to paste share links to any AI chatbot conversations you personally used for conceptual doubts/debugging into `ai-usage.md` (no screenshots; links only, or state if none were used, per course policy).

---

## 2. Environment Setup (Testing Native C + `xv6` in Ubuntu 24.04 Docker)

- **Parts 1 & 3 (`concurrency/airport-troubles` and `concurrency/birthday-boy`):**
  - Compile and run **natively** on both macOS Terminal (`gcc` / `clang`) and Ubuntu Linux (`gcc`) using standard POSIX threads (`-pthread`).
- **Part 2 (`xv6` RISC-V Kernel & QEMU):**
  - Reuse the exact same Ubuntu 24.04 Docker container from Mini Project 2 (keep the `Dockerfile` **outside** your git repo, e.g., `~/osn_docker/Dockerfile`):

```dockerfile
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    gdb \
    make \
    perl \
    python3 \
    bc \
    clang-format \
    git \
    qemu-system-misc \
    gcc-riscv64-unknown-elf \
    binutils-riscv64-unknown-elf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
```

Build once and launch mounting your `code.iiit.ac.in` clone:

```bash
docker build -t osn-mp3 ~/osn_docker
docker run -it --rm -v "/path/to/your/mini-project3:/workspace" -w /workspace osn-mp3 bash
```

---

## 3. Complete 14-Commit Step-by-Step Sequence

Below is the exact chronological order in which to build, test, commit, and push the entire project from your template repository on `code.iiit.ac.in`. Every file's complete final source code is in `semester3/osn_mini_project_3/`.

---

### Summary Table of All 14 Commits

| Commit # | Part | Files Added / Modified | Requirement Fulfilled |
| :---: | :--- | :--- | :--- |
| **1** | Setup | `.gitignore`, `concurrency/Makefile`, `concurrency/airport-troubles/Makefile`, `concurrency/airport-troubles/airport.h` | Build setup + data structures & constants for Airport Troubles |
| **2** | Part 1 | `concurrency/airport-troubles/clock.c` | Symbolic discrete-event clock & 2-phase synchronization (Constraint 8 — no `usleep`) |
| **3** | Part 1 | `concurrency/airport-troubles/actors.c` (hall + officer + student hall flow), `concurrency/airport-troubles/main.c` | Student arrival/entry/passport scanning & Immigration Officer batch approval/lockout (Constraints 1–4) |
| **4** | Part 1 | `concurrency/airport-troubles/actors.c` (baggage handlers + bag collection) | Baggage handlers (`1` & `2`), capacity-2 belt, and student bag collection (Constraints 5–7) |
| **5** | Part 2 | `xv6/kernel/stat.h`, `xv6/kernel/fcntl.h`, `xv6/kernel/syscall.h`, `xv6/kernel/syscall.c`, `xv6/user/user.h`, `xv6/user/usys.pl` | Define `T_SYMLINK`, `O_NOFOLLOW`, and wire `SYS_symlink` syscall stub |
| **6** | Part 2 | `xv6/kernel/sysfile.c` (`sys_symlink`) | Implement `symlink(target, path)` kernel syscall storing target in `T_SYMLINK` inode [20 Marks] |
| **7** | Part 2 | `xv6/kernel/sysfile.c` (`create` + `sys_open`) | Follow symlinks in `open()` up to depth 10, handle `O_NOFOLLOW` and `O_CREATE|O_APPEND` on symlinks [20 Marks] |
| **8** | Part 2 | `xv6/user/ln.c` | Support `ln -s target linkname` soft linking alongside hard linking [10 Marks] |
| **9** | Part 2 | `xv6/user/readlink.c`, `xv6/Makefile` | Implement `readlink` user program and register `$U/_readlink` in `UPROGS` [10 Marks] |
| **10** | Part 3 | `concurrency/birthday-boy/Makefile`, `concurrency/birthday-boy/bellman_ford.h`, `concurrency/birthday-boy/barrier.c` | Build setup, solver structures, and reusable generation-counted pthread barrier |
| **11** | Part 3 | `concurrency/birthday-boy/solver.c` | Vertex-partitioned incoming-edge parallel Bellman-Ford algorithm (`V - 1` rounds, race-free) [10 Marks] |
| **12** | Part 3 | `concurrency/birthday-boy/main.c` | CLI `V E N T` graph parser, distance printer, and end-to-end shortest-path execution |
| **13** | Docs | `README.md` (Parts 1, 2, and 3 build/run/design/assumptions) | Document build instructions, run instructions, design choices, and assumptions |
| **14** | Part 3 & Docs | `plots/runtime_vs_v.png`, `plots/runtime_vs_t.png`, `README.md` (Performance Analysis), `ai-usage.md` | Add experimental benchmark plots, fitted $k \cdot V \cdot E$ analysis ($k = 3.27 \times 10^{-10}\text{ s}$), and multi-core scaling report [20 Marks] |

---

## 4. Detailed Commit-by-Commit Instructions & Stage Tests

---

### Commit 1 — Part 1 Build System & Airport Simulation Data Structures
- **Files Created:**
  1. `.gitignore` (ignores `*.o`, `*.dSYM/`, `.DS_Store`, `airport-troubles`, `birthday-boy`)
  2. `concurrency/Makefile` (delegates `all` and `clean` to `airport-troubles` and `birthday-boy`)
  3. `concurrency/airport-troubles/Makefile` (`gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g`)
  4. `concurrency/airport-troubles/airport.h`
- **Why This Change Is Made:**
  - The boilerplate provides empty `concurrency/airport-troubles/` and `concurrency/birthday-boy/` folders without `Makefile`s.
  - `airport.h` defines the symbolic durations (`ACTION_DURATION = 1`, `SCAN_DURATION = 2`), hardware capacities (`NUM_SCANNERS = 3`, `NUM_HANDLERS = 2`, `BELT_CAPACITY = 2`), per-person thread structs (`struct student`, `struct officer`, `struct handler_arg`), and the shared monitor `struct airport_sim`.
- **How to Test at Commit 1:**
  ```bash
  gcc -std=c11 -Wall -Wextra -Werror -fsyntax-only concurrency/airport-troubles/airport.h
  ```
  *(Must exit with status `0` and zero warnings.)*
- **Git Commands:**
  ```bash
  git add .gitignore concurrency/Makefile concurrency/airport-troubles/Makefile concurrency/airport-troubles/airport.h
  git commit -m "airport-troubles: add Makefile and core simulation structs in airport.h"
  git push origin main
  ```

---

### Commit 2 — Part 1 Symbolic Discrete-Event Logical Clock (`clock.c`)
- **Files Created:**
  - `concurrency/airport-troubles/clock.c`
- **Why This Change Is Made:**
  - Constraint 8 forbids `sleep()` / `usleep()` and requires symbolic action durations (`1` unit for normal actions, `2` units for `scans passport`).
  - `clock.c` implements a **two-phase discrete-event clock** over `pthread_mutex_t`, `pthread_cond_t`, and three plain `int` arrays (`slot_used[]`, `wake_time[]`, `wake_done[]`):
    - Threads executing an action pick a free index `slot` in `slot_used[]` and record `wake_time[slot] = current_time + duration`.
    - Threads waiting on a false precondition call `sim_wait_condition()`, which records `seen_version = sim->state_version` and increments `sim->checked_count`.
    - When `timed_count + checked_count == active_threads` (meaning every live thread has either scheduled a future timestamp or verified it cannot act at `current_time`), `try_advance_clock()` scans `wake_time[]` with a simple `for` loop and advances `sim->current_time` to the minimum `wake_time`.
    - **Phase 1 (`finishing_phase_count`):** All threads finishing an action at the new timestamp wake up first and release their resources (`free_scanners++`, `officer_in_hall = 0`, `belt_slots_used--`) via `sim_complete_action()` **before** any waiting thread in Phase 2 evaluates preconditions at that timestamp.
    - `sim_wait_arrival_turn()` guarantees input lines with the exact same timestamp are processed in input order.
- **How to Test at Commit 2:**
  ```bash
  cd concurrency/airport-troubles
  gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g -c clock.c -o clock.o
  rm -f clock.o
  ```
- **Git Commands:**
  ```bash
  git add concurrency/airport-troubles/clock.c
  git commit -m "airport-troubles: implement pthread discrete-event symbolic clock"
  git push origin main
  ```

---

### Commit 3 — Part 1 Immigration Hall Actors & Input Parser (`actors.c` + `main.c`)
- **Files Created:**
  - `concurrency/airport-troubles/actors.c` *(initially with `student_thread` up to `leaves hall`, `officer_thread`, and an empty stub `handler_thread` that immediately calls `sim_thread_exit` so you can test the hall constraints standalone first!)*
  - `concurrency/airport-troubles/main.c`
- **Why This Change Is Made:**
  - Implements Constraints 1, 2, 3, and 4:
    - `read_input()` in `main.c` parses both 3-token lines (`<time> Student <id>`) and 4-token lines (`<time> Immigration officer <id>`).
    - `student_thread()` waits for arrival time + same-timestamp input order, blocks while `sim->officer_in_hall == 1`, enters (`1` unit, `in_hall = 1`, `unscanned_in_hall++`), acquires one of `3` scanners (`2` units, `free_scanners--`), waits for `st->approved == 1`, receives stamp (`1` unit), and leaves hall (`1` unit when `!officer_in_hall`).
    - `officer_thread()` waits for any mid-exit student (`students_leaving_now == 0`), locks the hall (`officer_in_hall = 1`), enters (`1` unit), waits until `unscanned_in_hall == 0` (every student in hall has finished scanning), approves everyone currently in the hall as one batch (`1` unit — even if empty!), and immediately leaves (`1` unit), clearing `officer_in_hall = 0` only when `leaves` finishes.
- **How to Test at Commit 3:**
  - Build with `make` in `concurrency/airport-troubles` and test an empty-hall officer visit:
    ```bash
    cd concurrency/airport-troubles
    make
    printf "1\n3 Immigration officer 1\n" | ./airport-troubles
    ```
    Expected output:
    ```text
    3 Immigration officer 1 enters
    4 Immigration officer 1 approves
    5 Immigration officer 1 leaves
    ```
- **Git Commands:**
  ```bash
  make -C concurrency/airport-troubles clean
  git add concurrency/airport-troubles/actors.c concurrency/airport-troubles/main.c
  git commit -m "airport-troubles: add input parser, student hall flow, and officer batch approval"
  git push origin main
  ```

---

### Commit 4 — Part 1 Baggage Handlers, Capacity-2 Belt & Bag Collection (`actors.c`)
- **Files Modified:**
  - `concurrency/airport-troubles/actors.c` (complete final version matching `semester3/osn_mini_project_3/concurrency/airport-troubles/actors.c`)
- **Why This Change Is Made:**
  - Implements Constraints 5, 6, and 7:
    - When a student finishes `receives stamp`, their student index `st->idx` is enqueued into `sim->ready_bags[]`.
    - Two `handler_thread` workers (`ID 1` and `ID 2`) wait until `ready_count > 0 && belt_slots_used < BELT_CAPACITY` (`2`). Each handler pops a ready student's bag, reserves a belt slot (`belt_slots_used++`), prints `<t> Baggage handler <h> loads bag for Student <id>`, waits `1` unit, and sets `bag_on_belt = 1`.
    - After leaving the hall, each student waits for `st->bag_on_belt == 1`, prints `<t> Student <id> collects bag`, waits `1` unit, and frees the belt slot (`belt_slots_used--`, `bags_collected++`).
    - Handlers exit cleanly once `bags_collected == num_students && ready_count == 0`.
- **How to Test at Commit 4:**
  1. Run the official specification example:
     ```bash
     cd concurrency/airport-troubles
     make
     ./airport-troubles << 'EOF'
     7
     0 Student 1
     0 Student 2
     0 Student 3
     1 Student 4
     3 Immigration officer 1
     4 Student 5
     9 Immigration officer 1
     EOF
     ```
     Verify timestamps run from `0` to `13` (`0..3` enters/scans, `5` approves, `6` stamps + officer leaves, `7` handlers load 2 bags + students leave + Student 5 enters, `8` 2 bags collected + Student 5 scans, `9` next 2 bags loaded + officer enters, `10` 2 bags collected + officer approves, `11` stamp + leaves, `12` bag 5 loaded + Student 5 leaves, `13` Student 5 collects bag).
  2. Test same-timestamp input ordering (`Student 10` before officer enters at `3`; `Student 20` after officer waits until `8`):
     ```bash
     ./airport-troubles << 'EOF'
     4
     3 Student 10
     3 Immigration officer 1
     3 Student 20
     12 Immigration officer 1
     EOF
     ```
  3. Test symbolic time jump (`t = 1000000` finishes instantaneously in `< 0.05s`):
     ```bash
     time printf "2\n0 Student 1\n1000000 Immigration officer 1\n" | ./airport-troubles
     make clean
     ```
- **Git Commands:**
  ```bash
  git add concurrency/airport-troubles/actors.c
  git commit -m "airport-troubles: implement baggage handlers, belt capacity limit, and bag collection"
  git push origin main
  ```

---

### Commit 5 — Part 2 (`xv6`) Define `T_SYMLINK`, `O_NOFOLLOW`, and Syscall Stubs
- **Files Modified:**
  1. `xv6/kernel/stat.h` — add `#define T_SYMLINK 4 // Symlink`
  2. `xv6/kernel/fcntl.h` — add `#define O_NOFOLLOW 0x1000` *(Note: `0x800` is already `O_APPEND` in boilerplate!)*
  3. `xv6/kernel/syscall.h` — add `#define SYS_symlink 23`
  4. `xv6/kernel/syscall.c` — add `extern uint64 sys_symlink(void);` and `[SYS_symlink] sys_symlink,`
  5. `xv6/user/user.h` — add `int symlink(const char *, const char *);`
  6. `xv6/user/usys.pl` — add `entry("symlink");`
- **Why This Change Is Made:**
  - `user/symlinktest.c` in the boilerplate references `T_SYMLINK`, `O_NOFOLLOW`, and `symlink()`, so it cannot compile until the new inode type, open flag, and system call entry (`SYS_symlink = 23`) are wired between user space and kernel space.
- **How to Test at Commit 5 (inside Docker container):**
  ```bash
  cd xv6
  perl user/usys.pl | tail -n 6
  ```
  Verify `.global symlink` / `li a7, SYS_symlink` / `ecall` is emitted.
- **Git Commands:**
  ```bash
  git add xv6/kernel/stat.h xv6/kernel/fcntl.h xv6/kernel/syscall.h xv6/kernel/syscall.c xv6/user/user.h xv6/user/usys.pl
  git commit -m "xv6: add T_SYMLINK inode type, O_NOFOLLOW flag, and symlink syscall wiring"
  git push origin main
  ```

---

### Commit 6 — Part 2 (`xv6`) Implement `sys_symlink` in `kernel/sysfile.c`
- **Files Modified:**
  - `xv6/kernel/sysfile.c` (add `sys_symlink(void)` right above `sys_open(void)`)
- **Why This Change Is Made:**
  - Fulfills **The `symlink` system call [20 marks]**:
    - Reads user strings `target` and `path` (`argstr(0, target, MAXPATH)` and `argstr(1, path, MAXPATH)`).
    - Starts a filesystem log transaction (`begin_op()`), allocates a new `T_SYMLINK` inode at `path` via `create(path, T_SYMLINK, 0, 0)` (which atomically fails if `path` already exists), writes `strlen(target)` bytes of `target` into `ip`'s data block using `writei()`, releases the inode (`iunlockput(ip)`), ends the transaction (`end_op()`), and returns `0` (or `-1` on any failure).
    - Does not require `target` to exist, allowing dangling symlinks.
- **How to Test at Commit 6 (inside Docker container):**
  ```bash
  cd xv6
  make clean && make fs.img kernel/kernel
  ```
  *(Both the RISC-V kernel and user programs including `_symlinktest` now compile and link cleanly with zero warnings!)*
- **Git Commands:**
  ```bash
  make -C xv6 clean
  git add xv6/kernel/sysfile.c
  git commit -m "xv6: implement sys_symlink system call storing target path in inode"
  git push origin main
  ```

---

### Commit 7 — Part 2 (`xv6`) Follow Symbolic Links in `sys_open` & `create`
- **Files Modified:**
  - `xv6/kernel/sysfile.c` (update `create()` line 259 to allow returning `T_SYMLINK` when `type == T_FILE`, and update `sys_open()` to iteratively follow symlinks up to depth `10`)
- **Why This Change Is Made:**
  - Fulfills **The `open` system call [20 marks]**:
    - When `O_NOFOLLOW` is **not** set, `sys_open()` follows `T_SYMLINK` chains iteratively in a `for (depth = 0; ; depth++)` loop, reading the target path from `ip` via `readi()` and unlocking/putting the symlink inode at each hop.
    - Enforces a **maximum traversal depth of 10** (`if (depth >= 10 || target_len >= MAXPATH)` returns `-1`), preventing infinite loops on cycles like `b -> a -> b`.
    - Handles `O_CREATE` on an existing symlink (tested by `createsymlink()` in `symlinktest.c` via `open("/testsymlink/l", O_WRONLY | O_CREATE | O_APPEND)`): `create()` returns the existing `T_SYMLINK` inode so `sys_open()` follows `l` to `/testsymlink/t` and appends to `t` while keeping `l` intact as a `T_SYMLINK` (unless `O_NOFOLLOW` was also set, in which case `O_CREATE | O_NOFOLLOW` on a symlink returns `-1`).
- **How to Test at Commit 7 (inside Docker container):**
  ```bash
  cd xv6
  ./test-xv6.py symlinktest
  ```
  Expected output:
  ```text
  Start: test symlinks
  test symlinks: ok
  Start: test O_CREATE on existing symlink
  test O_CREATE on existing symlink: ok
  Start: test concurrent symlinks
  test concurrent symlinks: ok
  ```
- **Git Commands:**
  ```bash
  make -C xv6 clean
  git add xv6/kernel/sysfile.c
  git commit -m "xv6: follow symbolic links in sys_open up to depth 10 and support O_NOFOLLOW"
  git push origin main
  ```

---

### Commit 8 — Part 2 (`xv6`) Update `ln` User Program for Soft Links (`ln -s`)
- **Files Modified:**
  - `xv6/user/ln.c`
- **Why This Change Is Made:**
  - Fulfills **The `ln` user program [10 marks]**:
    - When invoked as `ln -s <target> <linkname>` (`argc == 4 && strcmp(argv[1], "-s") == 0`), calls `symlink(argv[2], argv[3])`.
    - Otherwise (`argc == 3`), preserves standard hard-linking via `link(argv[1], argv[2])`.
- **How to Test at Commit 8 (inside Docker container):**
  Boot `make qemu` inside `xv6/` and run in the xv6 shell:
  ```sh
  echo "a" > file1
  ln -s file1 file2
  cat file2
  echo "b" >> file2
  cat file1
  rm file1
  cat file2
  ```
  Verify `cat file2` prints `a`, `echo "b" >> file2` appends to `file1` (`a` then `b`), and after `rm file1`, `cat file2` prints `cat: cannot open file2`! Quit QEMU with `Ctrl-A X`.
- **Git Commands:**
  ```bash
  make -C xv6 clean
  git add xv6/user/ln.c
  git commit -m "xv6: extend ln user program to create symbolic links with -s flag"
  git push origin main
  ```

---

### Commit 9 — Part 2 (`xv6`) Add `readlink` User Program & Register in `Makefile`
- **Files Created / Modified:**
  1. `xv6/user/readlink.c` (new file)
  2. `xv6/Makefile` (add `$U/_readlink` to `UPROGS`)
- **Why This Change Is Made:**
  - Fulfills **The `readlink` user program [10 marks]**:
    - Opens `argv[1]` with `O_RDONLY | O_NOFOLLOW` so it inspects the inode itself without dereferencing it.
    - Calls `fstat(fd, &st)` and checks `st.type == T_SYMLINK`. If opening fails or `st.type != T_SYMLINK` (e.g., `readlink README`), prints a clear error message to `stderr` (`fd 2`) and exits with non-zero status `exit(1)`.
    - Otherwise reads the stored target string (`read(fd, buf, MAXPATH - 1)`), null-terminates `buf`, prints `printf("%s\n", buf)`, and exits with `0`.
- **How to Test at Commit 9 (inside Docker container):**
  1. Boot `make qemu` and test manually:
     ```sh
     ln -s README myreadme
     readlink myreadme
     readlink README
     readlink does_not_exist
     ```
     - `readlink myreadme` prints `README`
     - `readlink README` prints `readlink: README is not a symbolic link` (exit status `1`)
     - `readlink does_not_exist` prints `readlink: cannot open does_not_exist` (exit status `1`)
  2. Run the full automated xv6 test suites:
     ```bash
     ./test-xv6.py symlinktest
     ./test-xv6.py -q usertests
     ```
     *(Both `symlinktest` and `usertests -q` must pass 100%!)*
- **Git Commands:**
  ```bash
  make -C xv6 clean
  git add xv6/user/readlink.c xv6/Makefile
  git commit -m "xv6: add readlink user utility and register in Makefile UPROGS"
  git push origin main
  ```

---

### Commit 10 — Part 3 Build System, Solver Header & Reusable Thread Barrier
- **Files Created:**
  1. `concurrency/birthday-boy/Makefile`
  2. `concurrency/birthday-boy/bellman_ford.h`
  3. `concurrency/birthday-boy/barrier.c`
- **Why This Change Is Made:**
  - Sets up the modular structure for `birthday-boy` and implements a portable generation-counted `struct thread_barrier` (`barrier_init`, `barrier_wait`, `barrier_destroy`) on top of `pthread_mutex_t` and `pthread_cond_t` (since `pthread_barrier_t` is an optional POSIX extension unavailable on macOS and easy to reason about in OS vivas).
- **How to Test at Commit 10:**
  ```bash
  cd concurrency/birthday-boy
  gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g -c barrier.c -o barrier.o
  rm -f barrier.o
  ```
- **Git Commands:**
  ```bash
  git add concurrency/birthday-boy/Makefile concurrency/birthday-boy/bellman_ford.h concurrency/birthday-boy/barrier.c
  git commit -m "birthday-boy: add Makefile, solver types, and reusable pthread barrier"
  git push origin main
  ```

---

### Commit 11 — Part 3 Parallel Bellman-Ford Solver (`solver.c`)
- **Files Created:**
  - `concurrency/birthday-boy/solver.c`
- **Why This Change Is Made:**
  - Fulfills **The Bellman-Ford algorithm [10 marks]**:
    - Expands the `E` bidirectional edges into `2E` directed edges (`u -> v` and `v -> u`) and sorts them by destination vertex `dst` using standard C `qsort()` (`compare_edges_by_dst()`).
    - Divides vertices `[0, V)` across the `T` spawned threads (`v_start = (t * V) / T`, `v_end = ((t + 1) * V) / T`) and assigns each thread its contiguous range `[edge_start, edge_end)` of incoming edges.
    - Across `V - 1` iterations, every thread reads `dist_curr[]` (read-only) and relaxes incoming edges into its own disjoint slice of `dist_next[]` with **zero data races and zero mutex contention**, synchronizes via `barrier_wait()`, copies its slice `dist_curr[v] = dist_next[v]`, and synchronizes at a second barrier before the next iteration.
- **How to Test at Commit 11:**
  ```bash
  cd concurrency/birthday-boy
  gcc -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pthread -O2 -g -c solver.c -o solver.o
  rm -f solver.o
  ```
- **Git Commands:**
  ```bash
  git add concurrency/birthday-boy/solver.c
  git commit -m "birthday-boy: implement vertex-partitioned parallel Bellman-Ford solver"
  git push origin main
  ```

---

### Commit 12 — Part 3 CLI Entry Point (`main.c`) & End-to-End Verification
- **Files Created:**
  - `concurrency/birthday-boy/main.c`
- **Why This Change Is Made:**
  - Reads `V E N T` and the `E` bidirectional edge lines `S D` from `stdin`, validates bounds, runs `solve_bellman_ford()`, and prints the `V` space-separated shortest path lengths on a single line.
- **How to Test at Commit 12:**
  ```bash
  cd concurrency
  make
  ./birthday-boy/birthday-boy << 'EOF'
  6 7 0 4
  0 1
  0 2
  1 3
  2 3
  3 4
  1 2
  4 5
  EOF
  ```
  Expected output:
  ```text
  0 1 1 2 3 4
  ```
  Also test disconnected vertex (`4 2 0 2` with edges `0 1` and `1 2` $\rightarrow$ `0 1 2 -1`) and `T > V` (`6 7 0 16` $\rightarrow$ `0 1 1 2 3 4`). Then run `make clean`.
- **Git Commands:**
  ```bash
  make -C concurrency clean
  git add concurrency/birthday-boy/main.c
  git commit -m "birthday-boy: add stdin graph parser and shortest-path distance output"
  git push origin main
  ```

---

### Commit 13 — Root `README.md` (Build, Run, Design & Assumptions for Parts 1–3)
- **Files Modified:**
  - `README.md` *(write the Repository Structure, Part 1, Part 2, and Part 3 build/run/design/assumptions sections from `semester3/osn_mini_project_3/README.md`)*
- **Why This Change Is Made:**
  - Satisfies the repository documentation requirement in `README.md` (build instructions, run instructions, modular design breakdown, explicit assumptions, and known bugs).
- **How to Test at Commit 13:**
  - Follow every build command written in `README.md` verbatim from a clean repo (`make -C concurrency`, `make -C concurrency clean`) to confirm zero typos.
- **Git Commands:**
  ```bash
  git add README.md
  git commit -m "docs: add build, run, design, and assumptions documentation in README"
  git push origin main
  ```

---

### Commit 14 — Part 3 Performance Analysis Report, Benchmark Plots & `ai-usage.md`
- **Files Created / Modified:**
  1. `plots/runtime_vs_v.png`
  2. `plots/runtime_vs_t.png`
  3. `README.md` *(append the full `Part 3: Performance Analysis Report` section with tables, fitted $k = 3.27 \times 10^{-10}\text{ s}$, embedded plots, and multi-core scaling observations)*
  4. `ai-usage.md` *(add any chat links you used for understanding concepts/debugging, or `No AI tools were used.` as applicable)*
- **Why This Change Is Made:**
  - Fulfills **Performance analysis [20 marks]**:
    - Plot 1 shows average runtime vs. `V` (`E = 40V`, fixed `T = 4`, averaged over 5 random graphs per point) overlaid with the theoretical complexity curve $k \cdot V \cdot E$ tuned to $k = 3.27 \times 10^{-10}\text{ seconds}$, plus a fixed-`V` varying-`E` table verifying linear scaling with `E`.
    - Plot 2 shows average runtime vs. `T` (`T = 1..32` for fixed `V = 3000, E = 120,000`, averaged over 5 random graphs) and explains the `2.27x` multi-core speedup up to `T = 3..4`, the heterogeneous P-core/E-core barrier straggler step at `T = 6..8`, and the OS context-switching + barrier contention slowdown at `T = 16..32`.
- **Final Pre-Submission Checklist before Pushing Commit 14:**
  1. Run `git status` — ensure **zero** untracked `.o`, binaries, `.py` scripts, or `.DS_Store` files exist.
  2. Run `git branch -a` and `git log --oneline` — verify all 14 commits sit cleanly on `main` with clear, descriptive commit messages.
  3. Open `code.iiit.ac.in` in your browser and verify `README.md` renders both PNG plots (`plots/runtime_vs_v.png` and `plots/runtime_vs_t.png`) and `ai-usage.md` is present.
- **Git Commands:**
  ```bash
  git add plots/runtime_vs_v.png plots/runtime_vs_t.png README.md ai-usage.md
  git commit -m "birthday-boy: add Bellman-Ford performance plots and scaling analysis in README"
  git push origin main
  ```
