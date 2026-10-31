# Operating Systems and Networks — Mini Project 3 Specification

- **Released:** October 14, 2026
- **Due:** November 10, 2026 (11:59 PM)
- **Doubt Doc Cutoff:** November 7, 2026 (11:59 PM)
- **Subtitle:** *Concurrency, distributed shortest paths and symlinks in xv6*
- **Total Marks:** **170 Marks**
  - **Part 1 — Concurrency: Airport Troubles:** 80 Marks (`concurrency/airport-troubles/`)
  - **Part 2 — xv6: Symbolic Links (`symlink`, `open`, `ln`, `readlink`):** 60 Marks (`xv6/`)
  - **Part 3 — Concurrency & Distributed Shortest Paths: Birthday Boy (Parallel Bellman-Ford + Performance Analysis):** 30 Marks (`concurrency/birthday-boy/` + `README.md`)

---

## 0. Repository Structure & Submission Rules

```text
mini-project3/
├── concurrency/
│   ├── airport-troubles/
│   └── birthday-boy/
├── xv6/
│   ├── user/
│   ├── kernel/
│   ├── Makefile
│   └── ...
├── ai-usage.md
└── README.md
```

- **Makefiles:** The Makefiles for `airport-troubles` and `birthday-boy` are not provided in the boilerplate; we must write them ourselves. The `xv6/` boilerplate is provided.
- **Git & Commit Policy:**
  - Commit iteratively and coherently on the `main` branch as you go.
  - Commit history is evaluated based on **push time** (server time).
  - If branching is used, it is **forbidden to squash merge, rebase, or delete the branch** after merging.
  - Each commit message must clearly describe the specific functionality implemented in that commit.
- **`README.md`:** Must contain build instructions, run instructions, design assumptions made, known bugs, and the **Performance Analysis report & plots** for Part 3 (Birthday Boy).
- **Modularity & I/O Format:** Code must be modular (not monolithic). Inputs and outputs must strictly match the specified format for the autograder.

---

## Part 1: Airport Troubles [80 Marks]
**Directory:** `concurrency/airport-troubles/`

### 1.1 Problem Overview
Simulate the arrivals area of Gotham Intergalactic Airport after Spaceship GB-420 lands. **Every person in the airport must be modelled as a thread** (`pthread_t`).

There are three types of actors (threads):
1. **Students** (any number of students, each has ID `i` from input and has **1 bag**):
   - Enter the immigration hall (`enters`)
   - Scan their passport at one of the **3 passport scanners** (`scans passport`, takes **2 time units**; each scanner serves 1 student at a time)
   - Wait to be approved by the immigration officer, then receive a stamp (`receives stamp`, takes **1 time unit**)
   - Leave the immigration hall (`leaves hall`, takes **1 time unit**)
   - Collect their own bag from the baggage belt (`collects bag`, takes **1 time unit**) and exit the airport.
2. **The Immigration Officer** (only **1 officer**, always has ID `1`, can visit the hall multiple times as specified in input):
   - Enters the hall (`enters`, allowed when arrived & ready)
   - Waits until every student currently in the hall has scanned their passport, then approves everyone in the hall at once as one batch (`approves`, takes **1 time unit**)
   - Leaves the hall immediately after approving (`leaves`, takes **1 time unit**).
3. **Baggage Handlers** (exactly **2 handlers**, with IDs `1` and `2`, NOT in input — spawned automatically by the simulation):
   - Load bags from the spaceship onto the baggage belt (`loads bag for Student <i>`, takes **1 time unit**).
   - The belt holds **at most 2 bags** at a time.
   - If the belt has space, a ready bag (whose owner has received a stamp) is loaded immediately; otherwise the handler blocks until a spot on the belt is freed up.

---

### 1.2 Constraints [10 Marks for Satisfying Each — 80 Marks Total]
1. **Hall Lockout During Officer Visit:** While the officer is in the hall, **no one may enter** and **students may not leave**.
2. **Officer Batch Approval Rule:** The officer must wait until **every student currently in the hall has scanned their passport** (including those waiting for a scanner). She then approves everyone in the hall as **one batch** (counts as 1 action taking 1 time unit).
3. **Stamp Prerequisite & Empty Hall Case:** A student can receive a stamp **only after being approved**. The officer leaves right after approving, without waiting for the stamps to be issued. If there is no one to approve in the hall, she still approves an empty batch and leaves.
4. **Leaving Hall Prerequisite:** Students cannot leave the hall until they have received a stamp.
   - *Note:* You can assume every student eventually receives a stamp, so no student is left waiting in the hall after the officer's last visit.
5. **Baggage Loading Prerequisite:** A handler cannot load a bag until its owner has **received a stamp**. Any handler (`1` or `2`) may load any ready bag, in any order. If the belt is full (capacity = 2), a handler waits with her bag until a student collects one.
6. **Bag Collection Prerequisite:** A student can collect **only their own bag**, and **only after leaving the hall**. If their bag is not on the belt yet, they wait until a handler loads it. After collecting it, they leave the airport.
7. **Exact Once Guarantee:** Every bag whose owner receives a stamp is loaded and collected **exactly once**. No other bag is loaded.
8. **Symbolic Action Durations (Discrete Event / Logical Clock Simulation — NO `usleep`/`sleep`!):**
   - Every action takes **1 time unit**, except `scans passport`, which takes **2 time units**.
   - **CRITICAL:** *"The action times are just symbolic. Your aim is to run a simulation of the actions, which means you need not actually wait for 2 seconds for scanning a passport. Any calls to `usleep` or similar that we we find in your code will be considered **suboptimal solutions** and **may be penalized**."*

---

### 1.3 Input & Output Format
- **Input Format:**
  - First line: Single integer `N` (number of arrival events).
  - Next `N` lines: `<time> <actor> <id>`
    - `<actor>` is either `Student` or `Immigration officer`.
    - `Baggage handler` is NOT part of the input since their action times depend on stamp receipt times.
    - Lines with the same timestamp must be processed in the order in which they are given.
- **Output Format:**
  - `<time> <actor> <id> <action>`
  - Actor actions:
    - Students: `enters`, `scans passport`, `receives stamp`, `leaves hall`, `collects bag`
    - Officer (`Immigration officer 1`): `enters`, `approves`, `leaves`
    - Handlers (`Baggage handler 1` or `2`): `loads bag for Student <i>`

#### Example Walkthrough (Understanding the Timestamps!)
Input:
```text
7
0 Student 1
0 Student 2
0 Student 3
1 Student 4
3 Immigration officer 1
4 Student 5
9 Immigration officer 1
```
Output trace analysis:
- `t=0`: Students 1, 2, 3 arrive and enter hall (`0 Student 1 enters`, `0 Student 2 enters`, `0 Student 3 enters`). Entering takes 1 time unit (`0 -> 1`) or starts scanning at `t=1`? Wait: look closely at the example output!
  - `0 Student 1 enters`
  - `1 Student 1 scans passport` (started at `t=0` after entering, or entering takes 1 time unit so at `t=1` scanning begins, or `scans passport` is printed when it *starts* or when it *completes*? Look at Student 4:
    - `1 Student 4 enters`
    - Since all 3 scanners are busy with Students 1, 2, 3 from `t=1` to `t=3` (or `t=0` to `t=2` + 1), when does Student 4 scan?
    - Look at the example output:
      - `0 Student 1 enters`, `0 Student 2 enters`, `0 Student 3 enters`
      - `1 Student 1 scans passport`, `1 Student 2 scans passport`, `1 Student 3 scans passport`
      - `1 Student 4 enters`
      - `3 Student 4 scans passport`
      - `3 Immigration officer 1 enters`
      - `5 Immigration officer 1 approves`
      - `6 Student 1 receives stamp`, `6 Student 2 receives stamp`, `6 Student 3 receives stamp`, `6 Student 4 receives stamp`
      - `6 Immigration officer 1 leaves`
      - `7 Baggage handler 1 loads bag for Student 1`, `7 Student 1 leaves hall`, `7 Baggage handler 2 loads bag for Student 2`, `7 Student 2 leaves hall`, `7 Student 3 leaves hall`, `7 Student 4 leaves hall`, `7 Student 5 enters`
      - `8 Student 1 collects bag`, `8 Student 2 collects bag`, `8 Student 5 scans passport`
      - `9 Baggage handler 1 loads bag for Student 3`, `9 Baggage handler 2 loads bag for Student 4`, `9 Immigration officer 1 enters`
      - `10 Student 3 collects bag`, `10 Student 4 collects bag`, `10 Immigration officer 1 approves`
      - `11 Student 5 receives stamp`, `11 Immigration officer 1 leaves`
      - `12 Baggage handler 1 loads bag for Student 5`, `12 Student 5 leaves hall`
      - `13 Student 5 collects bag`
  - Look how crystal-clear the timing rules are from this example! Every action's timestamp is the time when that action **completes** (or occurs after its duration):
    - Student 1 arrives at `0`, `enters` at `0` (or enters immediately upon arrival if officer not in hall, taking 1 time unit before next action? Wait: `0 Student 1 enters` -> +1 time unit (`enters` duration = 1) -> at `t=1`, `1 Student 1 scans passport`! And scanning takes 2 time units (`1 + 2 = 3`), so the scanner becomes free at `t=3`! Then Student 4, who entered at `t=1` (+1 = ready at `t=2`, waiting for scanner), gets a free scanner at `t=3` and prints `3 Student 4 scans passport`, which takes 2 time units (`3 + 2 = 5`)!
    - Meanwhile, `Immigration officer 1` arrives at `3` and prints `3 Immigration officer 1 enters`. She waits until Student 4 finishes scanning at `t=5`, and then at `t=5` prints `5 Immigration officer 1 approves` (duration = 1, finishes at `t=6`)!
    - At `t=6`, Officer prints `6 Immigration officer 1 leaves` (duration = 1, finishes at `t=7`, so Student 5 who arrived at `t=4` can finally enter at `t=7`!), AND at `t=6` Students 1–4 print `6 Student i receives stamp` (duration = 1, finishes at `t=7`)!
    - At `t=7`, Students 1–4 print `7 Student i leaves hall` (duration = 1, finishes at `t=8`) AND Handlers 1 & 2 print `7 Baggage handler 1 loads bag for Student 1` & `2` (duration = 1, finishes at `t=8`)!
    - At `t=8`, Students 1 & 2 print `8 Student 1 collects bag` (duration = 1, freeing belt slots at `t=9`!).
    - At `t=9`, Handlers 1 & 2 load bags for Students 3 & 4 (`9 Baggage handler ...`), taking 1 time unit (`9 + 1 = 10`), so at `t=10` Students 3 & 4 print `10 Student 3 collects bag`!
  - Every action prints its message when the action **starts**, and then occupies the actor/resource for its **duration** (1 time unit for everything except `scans passport` which occupies the student & scanner for **2 time units**)! That matches every single timestamp in the example from `t=0` to `t=13` with 100% mathematical precision!

---

## Part 2: Symbolic Links in xv6 [60 Marks]
**Directory:** `xv6/`

### 2.1 Overview
Implement symbolic links (soft links) to files in xv6 (symlinks to directories or devices are not required).
- Must pass `usertests -q` and `symlinktest`.
- Userspace programs (`ln` and `readlink`) will be manually tested.

### 2.2 Sub-Requirements
1. **New Inode Type (`kernel/stat.h`) & Syscall Wiring:**
   - Add `#define T_SYMLINK 4` in `kernel/stat.h`.
   - Add `O_NOFOLLOW` flag (e.g., `#define O_NOFOLLOW 0x800`) in `kernel/fcntl.h`.
2. **The `symlink` System Call [20 Marks]:**
   - Prototype: `int symlink(char *target, char *path)`
   - Creates a new inode of type `T_SYMLINK` at `path` storing the `target` string in the inode's data block(s) (within a logging transaction `begin_op()` / `end_op()`).
   - Dangling symlinks are allowed (`target` need not exist).
   - Returns `0` on success, `-1` on failure.
3. **The `open` System Call [20 Marks]:**
   - Modify `sys_open` in `kernel/sysfile.c` to follow symlinks when `O_NOFOLLOW` is **not** set.
   - Notice `createsymlink()` in `symlinktest.c`! Even if `O_CREATE` is passed (`open("/testsymlink/l", O_WRONLY | O_CREATE | O_APPEND)` where `l` is an existing symlink to `t`), `open` must follow the existing symlink `l` to `t` rather than overwriting `l` or failing!
   - If a symlink points to another symlink, follow recursively up to a **maximum depth of 10**; if still a symlink after 10 hops (cycle like `a -> b -> a`), fail and return `-1`.
   - If the target of a symlink does not exist, `open` fails and returns `-1` (unless created appropriately, wait: `symlinktest.c` line 105 checks that opening a symlink to a nonexistent file with `O_RDWR` fails).
4. **The `ln` User Program [10 Marks]:**
   - Modify `user/ln.c` so that `ln -s target linkname` calls `symlink(target, linkname)`, while `ln target linkname` continues to create a hard link via `link(target, linkname)`.
   - The `-s` flag, if present, will always be passed as `argv[1]`.
5. **The `readlink` User Program [10 Marks]:**
   - Create `user/readlink.c` and add `$U/_readlink` to `UPROGS` in `xv6/Makefile`.
   - Takes the path of a symlink (`readlink <path>`), opens it with `O_RDONLY | O_NOFOLLOW`, verifies via `fstat` that `st.type == T_SYMLINK`, reads the target string from the inode, and prints it.
   - If the path does not exist or is not a symlink (`st.type != T_SYMLINK`), print an error message and exit with a non-zero status (`exit(1)`).

---

## Part 3: Birthday Boy [30 Marks]
**Directory:** `concurrency/birthday-boy/` + Performance Analysis in root `README.md`

### 3.1 The Parallel Bellman-Ford Algorithm [10 Marks]
- Model the campus as an undirected (bidirectional), unweighted/unit-weight (or edge-list) graph with `V` vertices and `E` edges.
  - Look at the input format and example in Screenshot 10 & 11:
    - First line: `V E N T` (number of vertices `V`, number of edges `E`, source node `N`, number of threads `T` to spawn).
    - Next `E` lines: `S D` (two zero-indexed vertex IDs representing a bidirectional edge of weight 1).
    - Example Input:
      ```text
      6 7 0 4
      0 1
      0 2
      1 3
      2 3
      3 4
      1 2
      4 5
      ```
    - Example Output:
      ```text
      0 1 1 2 3 4
      ```
- Parallelize the **Bellman-Ford shortest-path algorithm** using `T` threads (`pthread_t` + barrier/synchronization across the `V - 1` relaxation iterations) to find the shortest path length from source node `N` to every vertex `0 .. V-1`.

### 3.2 Performance Analysis [20 Marks]
In the root `README.md`, include a performance analysis report with:
1. **Plot 1 (Runtime vs. `V` for fixed cores + complexity curve $k \cdot V \cdot E$):**
   - Runtime on the y-axis and `V` on the x-axis for a fixed number of cores/threads, averaged over several graphs with the same `V` and `E` but different edge sets.
   - On the same plot, overlay the theoretical complexity curve $k V E$, tuning constant $k$ to fit the experimental curve, and state the value of $k$.
2. **Plot 2 (Runtime vs. `T` for fixed `V` and `E`):**
   - Runtime on the y-axis and thread count `T` on the x-axis (with `V` and `E` fixed), averaged over different edge sets.
3. **Observations & Analysis:**
   - Explain why the plots look the way they do (e.g., speedup saturation, thread creation and barrier synchronization overhead when `T` exceeds physical cores or when `E` per thread is small, cache contention / false sharing).
