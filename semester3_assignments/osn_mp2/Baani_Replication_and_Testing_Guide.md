# CS3.301 Operating Systems and Networks — Mini Project 2
## Complete Step-by-Step Replication, 2-Laptop Testing, and Viva Guide for Baani

**Reference Repository (GitHub):** [`https://github.com/anshulsolanki/baani_assignments`](https://github.com/anshulsolanki/baani_assignments)  
**Working Project Folder:** `semester3/osn_mini_project_2/`  
**Reference Documentation Folder:** `semester3/osn_mp2/`

---

## 1. Overview & Golden Rules Before You Start

This guide gives you the exact **20-checkpoint sequence** written in clean, basic 2nd-year undergraduate C (no fancy compiler tricks, no Python scripts, no compact/obscure helper functions). Every requirement from the official assignment specification (`https://cs3301.pages.dev/assignments/02`) and the official CS3.301 TA Doubt Document (`https://hackmd.io/@m26-osn/S1qenn-tzg`) has been verified.

### Critical Assignment Rules to Keep in Mind
1. **Strictly C Code Only:**
   * Every file in the repository is pure C (`xv6` kernel C and `networking` C). Do not add any `.py` or shell scripts to your repository.
2. **Push Every Commit Within 24 Hours:**
   * Do **not** make all 20 commits in 10 minutes and push them in one big batch.
   * Spread your work naturally across sessions, and run `git push` after every checkpoint (or every couple of checkpoints) so the server push timestamps match your commit timestamps.
3. **Use Branches for `xv6` (`alarms` and `cow`) as Recommended by the Spec:**
   * The assignment handout specifically advises working on separate branches (`alarms` and `cow`) in `xv6` and then rebasing them together (`git rebase`). Section 3 below shows the exact branch and rebase commands to run so your git history matches the course git guide (`https://cs3301.pages.dev/resources/git`).
4. **Never Modify the Provided `Makefile`s in `networking/`:**
   * `networking/Makefile`, `networking/tempest/Makefile`, and `networking/mastermind/Makefile` already use `SRCS = $(wildcard *.c)` and `-std=c23 -D_POSIX_C_SOURCE=200809L -D_XOPEN_SOURCE=700 -Wall -Wextra -Werror -Wno-unused-parameter -g`.
   * Leave those three `Makefile`s untouched.
5. **Always Test `mastermind` on 2 Laptops Connected to a Personal Mobile Hotspot:**
   * Never run `mastermind` on IIIT-H campus Wi-Fi / LAN (campus networks drop UDP broadcasts and have many other students running on the same port).
   * Connect **Laptop 1 (your laptop)** and **Laptop 2 (a friend's laptop / TA's laptop)** to the **same personal mobile hotspot** to test and play `mastermind`.

---

## 2. Environment Setup & How to Test on 2 Laptops

### 2.1 Setting Up Ubuntu 24.04 on Your MacBook (For `xv6` & Linux `gcc` Verification)
Create a `Dockerfile` **outside** your git repository (e.g., in `~/osn_docker/Dockerfile` — never commit the `Dockerfile` into your assignment repo):

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
    curl \
    netcat-openbsd \
    iproute2 \
    iputils-ping \
    qemu-system-misc \
    gcc-riscv64-unknown-elf \
    binutils-riscv64-unknown-elf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
```

Build and run the container mounting your IIIT assignment repo:
```bash
# Build once:
docker build -t osn-mp2 ~/osn_docker

# Start an interactive shell mounting your assignment folder:
docker run -it --rm -v "/path/to/your/iiit-repo:/workspace" -w /workspace osn-mp2 bash
```

### 2.2 Step-by-Step Guide: Testing `mastermind` on 2 Laptops (Exactly How the TA Will Test)

During the evaluation, the TA will test `mastermind` across **2 laptops** connected to the same local network (mobile hotspot). Here is the exact procedure to practice and use on 2 laptops:

#### Step 1: Connect Both Laptops to Your Phone's Personal Hotspot
1. Turn on **Personal Hotspot** on your phone.
   * *(Important for iPhone Hotspot: Make sure "Maximize Compatibility" is toggled ON if needed, and neither laptop has a VPN turned on.)*
2. Connect **Laptop 1** (your laptop) and **Laptop 2** (your friend's laptop) to that same phone hotspot.
3. Verify both laptops are on the same subnet:
   * On macOS: `ipconfig getifaddr en0` (e.g., `172.20.10.2` and `172.20.10.3`)
   * On Linux: `hostname -I`
   * *(Note: If running inside Docker on one of the laptops on Linux, pass `--network host` to `docker run` so the container shares the laptop's Wi-Fi interface. On macOS, run `./mastermind` directly in the native macOS Terminal (`cd networking/mastermind && make && ./mastermind`) so it uses your MacBook's real Wi-Fi card `en0` directly!)*

#### Step 2: Compile and Launch `mastermind` on Both Laptops
* **On Laptop 1:**
  ```bash
  cd networking/mastermind
  make
  ./mastermind --log
  ```
  When prompted:
  ```text
  Enter your username: Feena
  ```
* **On Laptop 2:**
  ```bash
  cd networking/mastermind
  make
  ./mastermind --log
  ```
  When prompted:
  ```text
  Enter your username: Tatva
  ```

#### Step 3: Verify Player Discovery (`refresh` & 5-Second Expiry)
1. Wait 2 seconds, then type `refresh` on Laptop 1:
   ```text
   > refresh
   Players Online:
   ID   Name             IP Addr          Port    Last Seen
   0    Tatva            172.20.10.3      49152   1s ago
   ```
2. Type `refresh` on Laptop 2:
   ```text
   > refresh
   Players Online:
   ID   Name             IP Addr          Port    Last Seen
   0    Feena            172.20.10.2      51234   0s ago
   ```
3. **Test Peer Expiry (5 seconds):** Press `Ctrl+C` on Laptop 2 to stop `Tatva`, wait 5 seconds, and type `refresh` on Laptop 1 — `Tatva` will disappear (`No other players found.`). Restart `./mastermind --log` on Laptop 2.

#### Step 4: Test Challenge Reject & Accept Flow
1. On Laptop 1 (`Feena`), challenge player `0` (`Tatva`):
   ```text
   > challenge 0
   Waiting for Tatva to respond...
   ```
2. On Laptop 2 (`Tatva`), you will immediately see:
   ```text
   Feena (172.20.10.2) has challenged you. Accept? (yes/no):
   ```
   * First type `no` to verify rejection: Laptop 1 prints `Tatva rejected your challenge.` and both return to the lobby.
   * Now type `challenge 0` again on Laptop 1, and type `yes` on Laptop 2.

#### Step 5: Play a Full Game (Laptop 2 = Mastermind, Laptop 1 = Codebreaker)
1. **Laptop 2 (`Tatva` — Mastermind)** is prompted to set the 5-digit secret sequence:
   * First test invalid input: type `12a45` or `123` $\rightarrow$ it prints `Invalid sequence. Please enter exactly 5 digits (0-9).`
   * Now enter a valid 5-digit sequence, e.g. `67676`.
2. **Laptop 1 (`Feena` — Codebreaker)** sees the 12-row board with `*****  *****` on top and is prompted for Attempt 1:
   * Enter a guess, e.g. `12345`.
3. **Laptop 2 (`Tatva` — Mastermind)** sees `Feena guessed: 12345` and `(Expected feedback: -----)` and is prompted:
   ```text
   Enter feedback for 12345 (x=exact, o=misplaced, -=wrong):
   ```
   * Enter `-----`.
4. Both laptops immediately re-render the colored 12-row board!
5. Next, on Laptop 1 (`Feena`), guess `67676`. On Laptop 2 (`Tatva`), enter `xxxxx`.
6. Both laptops display the final board with the top row `*****` replaced by `67676` on the Codebreaker's screen and print:
   * Laptop 1: `Congratulations! You broke the code in 2 attempts! Press enter to go home.`
   * Laptop 2: `Feena broke your code in 2 attempts! Press enter to go home.`

#### Step 6: Test Mid-Game Disconnection
1. Start another game between Laptop 1 and Laptop 2.
2. In the middle of the game, press `Ctrl+C` (or type `exit`) on Laptop 2.
3. Laptop 1 immediately prints:
   ```text
   Tatva disconnected. Press enter to go home.
   ```
   Pressing Enter returns Laptop 1 cleanly to the lobby.

#### Step 7: Test Cost-Cutting Mode (`--cost-cutting`) on Both Laptops
1. Start both laptops with `--cost-cutting --log`:
   ```bash
   ./mastermind --cost-cutting --log
   ```
2. Repeat the challenge, gameplay, and mid-game disconnect tests. Check `log.txt` afterwards to see every 4-byte UDP chunk (`CHUNK_SENT`, `CHUNK_RECV`, `ACK_SENT`, `ACK_RECV`, `MSG_REASSEMBLED`) logged with microsecond timestamps!

---

## 3. Explanation of `tempest` & `wttr.is` Behavior (Official TA Clarifications)

You noticed two things when testing `tempest`:
1. **Why does the weather shown by `wttr.is` differ from Google Weather?**
   * The assignment strictly requires querying **only** `http://wttr.is/<city>?0T` over plain HTTP on port 80 (`tempest` is not allowed to query Google or HTTPS APIs).
   * `wttr.is` is a custom server hosted by the course staff (running an older snapshot/upstream instance of `wttr.in` behind ` Caddy`). Its weather values come from `wttr.is`'s own backend data source, so the temperature/wind numbers will naturally differ from live Google Weather. You can verify that `./tempest <city>` matches `curl -s "http://wttr.is/<city>?0T"` character-for-character.
2. **Why did some non-existent location names show a weather report instead of `tempest: invalid location`?**
   * There were **two causes**, one in our code (which is now **fixed**) and one on the `wttr.is` server itself (which the TAs explicitly documented in **Question 7 of the Official TA Doubt Doc**):
     1. **What we fixed in `http.c`:** Previously, our code only checked `if (status_code == 404 || status_code == 400)`. However, when `wttr.is` fails to look up cities like `notarealcity`, `invalidcity`, `iiith`, or `xyzabc123`, the server actually returns **`HTTP/1.1 500 Internal Server Error`** or **`HTTP/1.1 502 Bad Gateway`** or falls back to IP coordinates (`Weather report: 21.997400,79.001100`). Because our old code only checked `404` and `400`, it didn't flag `500`!
     2. **How `http.c` works now:** `check_invalid_location()` in `http.c` now flags **any** response where `status_code != 200`, **any** response containing error text (`"Unknown location"`, `"not found"`, `"Sorry"`, `"ERROR"`), **any** response that doesn't start with `"Weather report:"`, **any** input without letters/digits, and **any** response where `wttr.is` fell back to raw GPS coordinates (`Weather report: 21.997400,79.001100`).
     3. **Official TA Clarification (Doubt Doc Q7):** In the official CS3.301 Doubt Doc (`https://hackmd.io/@m26-osn/S1qenn-tzg`), a student asked:
        > **Q7:** *"The server `wttr.is` in some cases does not detect that a city does not exist, for eg. I tried `noSuchCity` and it gave the weather report with `200 OK`, so how then should we detect invalid locations? Based on server's response not being 200?"*  
        > **TA Advait (`[AD]`) Answer:** *"Use the HTTP status code as your primary signal. `wttr.is`'s geocoding may not be reliable and you are not expected to work around this."*
   * With our updated `check_invalid_location()` in `http.c`:
     * `./tempest notarealcity` $\rightarrow$ `tempest: invalid location`
     * `./tempest invalidcity` $\rightarrow$ `tempest: invalid location`
     * `./tempest iiith` $\rightarrow$ `tempest: invalid location`
     * `./tempest xyzabc123` $\rightarrow$ `tempest: invalid location`
     * `./tempest qwertyuiop` $\rightarrow$ `tempest: invalid location`

---

## 4. The 20 Incremental Checkpoints — Exact Replication Guide

Below is the complete step-by-step walkthrough of all **20 checkpoints**, what files are created/modified, how to test at each stage, and the key concepts to know for your TA viva.

---

### Phase 1: `xv6` — Process Alarms (`sigalarm` & `sigreturn`) [40 Marks]

> **Git Branch Workflow (Recommended by Spec):**
> In your IIIT repo, create and switch to an `alarms` branch before starting Checkpoint 1:
> ```bash
> git checkout -b alarms
> ```

---

#### Checkpoint 1: Add Alarm State Fields to `struct proc`
* **Suggested Commit Message:** `xv6: add alarm state fields to struct proc`
* **Files Modified:**
  1. `xv6/kernel/proc.h`
  2. `xv6/kernel/proc.c`
* **What to Change:**
  1. In `xv6/kernel/proc.h`, at the bottom of `struct proc`, add:
     ```c
     // Process alarm state (sigalarm / sigreturn)
     int alarm_ticks;             // Alarm interval in ticks (0 if disabled)
     uint64 alarm_handler;        // User virtual address of alarm handler
     int alarm_ticks_left;        // Ticks remaining until next handler invocation
     int alarm_active;            // Non-zero while executing inside alarm handler
     struct trapframe *alarm_tf;  // Saved trapframe prior to handler execution
     ```
  2. In `xv6/kernel/proc.c` inside `allocproc()`, right after allocating `p->trapframe`, allocate `p->alarm_tf` and zero-initialize the alarm fields:
     ```c
     // Allocate a page to save the trapframe during sigalarm handler execution.
     if ((p->alarm_tf = (struct trapframe *)kalloc()) == 0) {
       freeproc(p);
       release(&p->lock);
       return 0;
     }

     // Initialize alarm state.
     p->alarm_ticks = 0;
     p->alarm_handler = 0;
     p->alarm_ticks_left = 0;
     p->alarm_active = 0;
     ```
  3. In `xv6/kernel/proc.c` inside `freeproc()`, free `p->alarm_tf` and reset all alarm fields:
     ```c
     if (p->alarm_tf)
       kfree((void *)p->alarm_tf);
     p->alarm_tf = 0;
     p->alarm_ticks = 0;
     p->alarm_handler = 0;
     p->alarm_ticks_left = 0;
     p->alarm_active = 0;
     ```
* **How to Test:**
  ```bash
  cd xv6 && make kernel/kernel
  ```
* **Commit Command:**
  ```bash
  git add xv6/kernel/proc.h xv6/kernel/proc.c
  git commit -m "xv6: add alarm state fields to struct proc"
  ```
* **TA Viva Point:** *Why do we need `p->alarm_tf` separate from `p->trapframe`?*  
  Because the user-space alarm handler runs in user mode and makes system calls (`printf`, `write`, `sigreturn`). Every system call traps into the kernel and overwrites `p->trapframe`. Saving a copy in `p->alarm_tf` before entering the handler allows `sigreturn()` to restore the exact pre-interrupt CPU registers.

---

#### Checkpoint 2: Implement `sys_sigalarm` and `sys_sigreturn` Syscalls
* **Suggested Commit Message:** `xv6: implement sys_sigalarm and sys_sigreturn syscalls`
* **Files Modified:**
  * `xv6/kernel/sysproc.c`
* **What to Change:**
  *(Note: In your boilerplate, `SYS_sigalarm` and `SYS_sigreturn` are already wired in `syscall.h`, `syscall.c`, `user.h`, and `usys.pl`. You only need to fill in the stubs at the bottom of `xv6/kernel/sysproc.c`!)*
  ```c
  uint64
  sys_sigalarm(void)
  {
    int ticks;
    uint64 handler;
    struct proc *p = myproc();

    argint(0, &ticks);
    argaddr(1, &handler);

    if (ticks < 0)
      return -1;

    p->alarm_ticks = ticks;
    p->alarm_handler = handler;
    p->alarm_ticks_left = ticks;

    return 0;
  }

  uint64
  sys_sigreturn(void)
  {
    struct proc *p = myproc();

    if (p->alarm_active) {
      *(p->trapframe) = *(p->alarm_tf);
      p->alarm_active = 0;
    }

    return p->trapframe->a0;
  }
  ```
* **How to Test:**
  ```bash
  cd xv6 && make kernel/kernel
  ```
* **Commit Command:**
  ```bash
  git add xv6/kernel/sysproc.c
  git commit -m "xv6: implement sys_sigalarm and sys_sigreturn syscalls"
  ```
* **TA Viva Point:** *Why must `sys_sigreturn()` return `p->trapframe->a0` instead of `0`?*  
  In `xv6/kernel/syscall.c`, `syscall()` executes `p->trapframe->a0 = syscalls[num]();`. If `sys_sigreturn()` returned `0`, `syscall()` would overwrite the restored `p->trapframe->a0` with `0`, corrupting register `a0` of the interrupted user code and failing `test3` in `alarmtest.c`!

---

#### Checkpoint 3: Invoke Alarm Handler on Timer Interrupts in `usertrap`
* **Suggested Commit Message:** `xv6: invoke alarm handler on timer interrupts in usertrap`
* **Files Modified:**
  * `xv6/kernel/trap.c`
* **What to Change:**
  In `usertrap()` in `xv6/kernel/trap.c`, update the `if (which_dev == 2)` timer interrupt block:
  ```c
  // give up the CPU if this is a timer interrupt.
  if (which_dev == 2) {
    if (p->alarm_ticks > 0 && p->alarm_active == 0) {
      p->alarm_ticks_left--;
      if (p->alarm_ticks_left <= 0) {
        p->alarm_ticks_left = p->alarm_ticks;
        p->alarm_active = 1;
        *(p->alarm_tf) = *(p->trapframe);
        p->trapframe->epc = p->alarm_handler;
      }
    }
    yield();
  }
  ```
* **How to Test (in Docker / Linux):**
  ```bash
  cd xv6
  ./test-xv6.py alarmtest
  ./test-xv6.py -q usertests
  ```
  Expected output: `test0 passed`, `test1 passed`, `test2 passed`, `test3 passed`.
* **Commit Command:**
  ```bash
  git add xv6/kernel/trap.c
  git commit -m "xv6: invoke alarm handler on timer interrupts in usertrap"
  ```

---

### Phase 2: `xv6` — Copy-on-Write (CoW) Fork [50 Marks]

> **Git Branch Workflow (Recommended by Spec):**
> Switch back to `main` and create a `cow` branch:
> ```bash
> git checkout main
> git checkout -b cow
> ```

---

#### Checkpoint 4: Add Physical Page Reference Counting in `kalloc`
* **Suggested Commit Message:** `xv6: add physical page reference counting in kalloc`
* **Files Modified:**
  1. `xv6/kernel/riscv.h`
  2. `xv6/kernel/defs.h`
  3. `xv6/kernel/kalloc.c`
* **What to Change:**
  1. In `xv6/kernel/riscv.h`, define the Copy-on-Write bit using supervisor software bit 8:
     ```c
     #define PTE_COW (1L << 8) // copy-on-write page (RSW bit 8)
     ```
  2. In `xv6/kernel/defs.h`, under `// kalloc.c`, add:
     ```c
     void            krefinc(void *);
     ```
  3. In `xv6/kernel/kalloc.c`, add the `pageref` structure and reference-counting logic:
     ```c
     #define PA2IDX(pa) (((uint64)(pa) - KERNBASE) / PGSIZE)

     struct {
       struct spinlock lock;
       int count[(PHYSTOP - KERNBASE) / PGSIZE];
     } pageref;
     ```
     * In `kinit()`: call `initlock(&pageref.lock, "pageref");` before `freerange()`.
     * In `freerange()`: set `pageref.count[PA2IDX(p)] = 1;` under `pageref.lock` before calling `kfree(p)`.
     * Implement `krefinc(void *pa)`: acquire `pageref.lock`, increment `pageref.count[PA2IDX(pa)]`, release `pageref.lock`.
     * In `kfree(void *pa)`: acquire `pageref.lock`, decrement `pageref.count[PA2IDX(pa)]`; if the new count is `> 0`, release `pageref.lock` and `return` immediately without freeing! Only when the count reaches `0` do we `memset(pa, 1, PGSIZE)` and add `pa` to `kmem.freelist`.
     * In `kalloc()`: when `r != 0`, set `pageref.count[PA2IDX(r)] = 1` under `pageref.lock`.
* **How to Test:**
  ```bash
  cd xv6 && ./test-xv6.py -q usertests
  ```
* **Commit Command:**
  ```bash
  git add xv6/kernel/riscv.h xv6/kernel/defs.h xv6/kernel/kalloc.c
  git commit -m "xv6: add physical page reference counting in kalloc"
  ```

---

#### Checkpoint 5: Share Parent Physical Pages as CoW in `uvmcopy`
* **Suggested Commit Message:** `xv6: share parent physical pages as CoW in uvmcopy`
* **Files Modified:**
  * `xv6/kernel/vm.c`
* **What to Change:**
  In `uvmcopy()` in `xv6/kernel/vm.c`, remove `kalloc()` and `memmove()`. Instead, clear `PTE_W` and set `PTE_COW` on writable pages in both parent and child, map the same physical page `pa`, and increment its reference count with `krefinc((void *)pa)`:
  ```c
  int
  uvmcopy(pagetable_t old, pagetable_t new, uint64 sz)
  {
    pte_t *pte;
    uint64 pa, i;
    uint flags;

    for (i = 0; i < sz; i += PGSIZE) {
      if ((pte = walk(old, i, 0)) == 0)
        continue; // page table entry hasn't been allocated
      if ((*pte & PTE_V) == 0)
        continue; // physical page hasn't been allocated
      pa = PTE2PA(*pte);
      if (*pte & PTE_W) {
        *pte = (*pte & ~PTE_W) | PTE_COW;
      }
      flags = PTE_FLAGS(*pte);
      if (mappages(new, i, PGSIZE, pa, flags) != 0) {
        goto err;
      }
      krefinc((void *)pa);
    }
    return 0;

  err:
    uvmunmap(new, 0, i / PGSIZE, 1);
    return -1;
  }
  ```
* **Commit Command:**
  ```bash
  git add xv6/kernel/vm.c
  git commit -m "xv6: share parent physical pages as CoW in uvmcopy"
  ```

---

#### Checkpoint 6: Handle CoW Store Page Faults in `usertrap`
* **Suggested Commit Message:** `xv6: handle CoW store page faults in usertrap`
* **Files Modified:**
  1. `xv6/kernel/defs.h`
  2. `xv6/kernel/vm.c`
  3. `xv6/kernel/trap.c`
* **What to Change:**
  1. Declare `int cowfault(pagetable_t, uint64);` under `// vm.c` in `xv6/kernel/defs.h`.
  2. Implement `cowfault()` at the bottom of `xv6/kernel/vm.c`:
     ```c
     int
     cowfault(pagetable_t pagetable, uint64 va)
     {
       pte_t *pte;
       uint64 pa;
       uint flags;
       char *mem;

       if (va >= MAXVA)
         return -1;

       pte = walk(pagetable, va, 0);
       if (pte == 0)
         return -1;
       if ((*pte & PTE_V) == 0 || (*pte & PTE_U) == 0 || (*pte & PTE_COW) == 0)
         return -1;

       pa = PTE2PA(*pte);
       flags = (PTE_FLAGS(*pte) & ~PTE_COW) | PTE_W;

       if ((mem = kalloc()) == 0)
         return -1;

       memmove(mem, (char *)pa, PGSIZE);
       *pte = PA2PTE(mem) | flags;
       kfree((void *)pa);

       return 0;
     }
     ```
  3. In `usertrap()` in `xv6/kernel/trap.c`, check `cowfault()` on store page faults (`r_scause() == 15`) right before the existing `vmfault()` check:
     ```c
     } else if ((which_dev = devintr()) != 0) {
       // ok
     } else if (r_scause() == 15 && cowfault(p->pagetable, r_stval()) == 0) {
       // page fault on copy-on-write page
     } else if ((r_scause() == 15 || r_scause() == 13) &&
                vmfault(p->pagetable, p->sz, r_stval(),
                        (r_scause() == 13) ? 1 : 0) != 0) {
       // page fault on lazily-allocated page
     } else {
     ```
* **Commit Command:**
  ```bash
  git add xv6/kernel/defs.h xv6/kernel/vm.c xv6/kernel/trap.c
  git commit -m "xv6: handle CoW store page faults in usertrap"
  ```

---

#### Checkpoint 7: Handle CoW Pages in `copyout`
* **Suggested Commit Message:** `xv6: handle CoW pages in copyout`
* **Files Modified:**
  * `xv6/kernel/vm.c`
* **What to Change:**
  In `copyout()` in `xv6/kernel/vm.c`, right after `pte = walk(pagetable, va0, 0);`, check if `*pte & PTE_COW` is set and resolve the CoW fault before checking `*pte & PTE_W`:
  ```c
    pte = walk(pagetable, va0, 0);
    if (*pte & PTE_COW) {
      if (cowfault(pagetable, va0) < 0)
        return -1;
      pa0 = walkaddr(pagetable, va0);
    }
    // forbid copyout over read-only user text pages.
    if ((*pte & PTE_W) == 0)
      return -1;
  ```
* **How to Test (in Docker / Linux):**
  ```bash
  cd xv6
  ./test-xv6.py cowtest
  ./test-xv6.py -q usertests
  ```
  Expected output: `simple: ok`, `simple: ok`, `three: ok` (×3), `file: ok`, `ALL COW TESTS PASSED`.
* **Commit Command:**
  ```bash
  git add xv6/kernel/vm.c
  git commit -m "xv6: handle CoW pages in copyout"
  ```

---

#### Checkpoint 8: Rebase `cow` and `alarms` Branches and Format Code
* **Suggested Commit Message:** `xv6: rebase cow and alarms branches and format code`
* **Files Modified:**
  * `xv6/kernel/riscv.h` (and any formatting via `make fmt`)
* **What to Run:**
  ```bash
  # Rebase cow onto alarms, then fast-forward main:
  git checkout cow
  git rebase alarms
  git checkout main
  git merge --ff-only cow

  # Format code according to xv6/.clang-format:
  cd xv6 && make fmt
  ```
* **How to Test:**
  ```bash
  cd xv6
  ./test-xv6.py cowtest
  ./test-xv6.py alarmtest
  ./test-xv6.py -q usertests
  ```
* **Commit Command:**
  ```bash
  git add xv6/
  git commit -m "xv6: rebase cow and alarms branches and format code"
  ```

---

### Phase 3: `networking/tempest` — HTTP/1.1 Weather Client [15 Marks]

All `tempest` code is written in simple, straightforward 2nd-year C (`tempest.h`, `url.c`, `http.c`, `main.c`).

---

#### Checkpoint 9: Parse CLI Arguments and Implement URL Encoding
* **Suggested Commit Message:** `tempest: parse CLI arguments and implement URL encoding`
* **Files Created:**
  1. `networking/tempest/tempest.h`
  2. `networking/tempest/url.c`
  3. `networking/tempest/main.c`
* **What Is Implemented:**
  * `is_safe_char()` and `url_encode()` in `url.c`: simple `for` loop that copies alphanumeric characters and `-`, `_`, `.`, `~` directly and formats all other characters (such as spaces) as `%02X`.
  * `main.c`: checks `argc == 2` (`./tempest <city>`) or `argc == 3` with `strcmp(argv[2], "--raw") == 0`. If more arguments are passed, prints `tempest: too many arguments` and returns `1`.
* **How to Test:**
  ```bash
  cd networking/tempest && make
  ./tempest a b
  # Output: tempest: too many arguments
  ```
* **Commit Command:**
  ```bash
  make -C networking/tempest clean
  git add networking/tempest/tempest.h networking/tempest/url.c networking/tempest/main.c
  git commit -m "tempest: parse CLI arguments and implement URL encoding"
  ```

---

#### Checkpoint 10: Implement TCP Connection and HTTP GET Request with 10-Second Timeout
* **Suggested Commit Message:** `tempest: implement TCP connection and HTTP GET request with timeout`
* **Files Created / Modified:**
  1. `networking/tempest/tempest.h`
  2. `networking/tempest/http.c`
  3. `networking/tempest/main.c`
* **What Is Implemented:**
  * `get_time_ms()` using `gettimeofday()` to track the overall 10-second (`10000 ms`) application-level deadline starting **before** `connect()` (per TA Doubt Doc Q3, Q5, Q13, Q15).
  * `connect_to_server()` resolves `wttr.is:80` using `getaddrinfo()` and connects a TCP socket (`SOCK_STREAM`).
  * `send_all()` loops over `send()` until the full HTTP/1.1 request (`GET /<city>?0T HTTP/1.1\r\nHost: wttr.is\r\nUser-Agent: curl/8.0.0\r\nAccept: */*\r\nConnection: close\r\n\r\n`) is written.
  * `recv_all_with_timeout()` uses `poll()` with `remaining = 10000 - (get_time_ms() - start_ms)` before every `recv()` call until EOF (`recv() == 0`). If the 10-second budget expires, it prints `tempest: connection timed out` and exits with `1`.
* **Commit Command:**
  ```bash
  make -C networking/tempest clean
  git add networking/tempest/tempest.h networking/tempest/http.c networking/tempest/main.c
  git commit -m "tempest: implement TCP connection and HTTP GET request with timeout"
  ```

---

#### Checkpoint 11: Parse HTTP Status Line, Headers, Invalid Locations, and `--raw` Mode
* **Suggested Commit Message:** `tempest: parse HTTP status line, headers, and raw output`
* **Files Modified:**
  * `networking/tempest/http.c`
* **What Is Implemented:**
  * Finds `\r\n\r\n` with `strstr()` to split HTTP headers from the body and parses `status_code` from `HTTP/1.1 <status>` with `sscanf()`.
  * `check_invalid_location()`: checks if `status_code != 200` (catching `404`, `400`, `500`, `502`, etc.), checks if the body contains `"Unknown location"`, `"location not found"`, `"not found"`, `"Sorry"`, or `"ERROR"`, checks that the body starts with `"Weather report:"`, and checks that `wttr.is` did not fall back to raw latitude/longitude coordinates (`Weather report: 21.997400,79.001100`).
  * Implements `--raw` mode with `print_prefixed_lines()` (`> ` for request lines, `< ` for response headers, followed by the body). Per TA Doubt Doc Q12 & Q23, `--raw` takes precedence over `tempest: invalid location` and still exits with code `1` if the location is invalid.
* **How to Test:**
  ```bash
  cd networking/tempest && make
  ./tempest Hyderabad
  ./tempest "New York"
  ./tempest Rotterdam --raw
  ./tempest notarealcity
  ./tempest iiith
  ./tempest a b
  ```
* **Commit Command:**
  ```bash
  make -C networking/tempest clean
  git add networking/tempest/http.c
  git commit -m "tempest: parse HTTP status line, headers, and raw output"
  ```

---

### Phase 4: `networking/mastermind` — Peer-to-Peer LAN Game [40 Marks]

All `mastermind` code is written in basic, clear 2nd-year C (`mastermind.h`, `log.c`, `discovery.c`, `game.c`, `net_tcp.c`, `net_rudp.c`, `main.c`) and built specifically for 2 laptops on a LAN/hotspot.

---

#### Checkpoint 12: Define Protocol Constants, Structs, and Logging Utility
* **Suggested Commit Message:** `mastermind: define protocol constants, structs, and logging utility`
* **Files Created:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/log.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Defines `MAGIC_NUMBER` (`0x4D4D4E44`), discovery timing constants (`2000 ms` broadcast, `5000 ms` expiry), RUDP constants (`CHUNK_DATA_SIZE = 4`, `100 ms` retransmit), and basic structs (`struct peer_info`, `struct game_state`, `struct rudp_chunk`, `struct rudp_state`).
  * Implements `write_log()` in `log.c` using the exact `gettimeofday()` + `strftime()` code snippet from the assignment handout, writing to `log.txt` when `--log` is enabled.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/log.c networking/mastermind/main.c
  git commit -m "mastermind: define protocol constants, structs, and logging utility"
  ```

---

#### Checkpoint 13: Implement UDP Broadcast Player Discovery and Peer Expiry
* **Suggested Commit Message:** `mastermind: implement UDP broadcast player discovery and peer expiry`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/discovery.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * `discovery_init()` creates a UDP socket bound to port `33301` with `SO_BROADCAST` and `SO_REUSEADDR`.
  * `pack_discovery_packet()` and `unpack_discovery_packet()` explicitly pack/unpack the 38-byte broadcast buffer (`magic` in network byte order, `listen_port` in network byte order, and `name[32]`) using `memcpy`, `htonl`/`ntohl`, and `htons`/`ntohs`.
  * `discovery_send_broadcast()` broadcasts to `INADDR_BROADCAST` (`255.255.255.255`) every **2 seconds**.
  * `discovery_receive()` verifies `magic == MAGIC_NUMBER`, reads the sender's IP from `recvfrom()`'s `struct sockaddr_in`, ignores self-broadcasts, and updates `peers[]`.
  * `discovery_remove_expired()` removes peers not seen for **5 seconds** (`5000 ms`).
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/discovery.c networking/mastermind/main.c
  git commit -m "mastermind: implement UDP broadcast player discovery and peer expiry"
  ```

---

#### Checkpoint 14: Implement Challenge Handshake and Persistent TCP Session
* **Suggested Commit Message:** `mastermind: implement challenge handshake and persistent TCP session`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/net_tcp.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Implements `tcp_create_listen_socket()`, `tcp_connect_to_peer()`, `tcp_send_line()`, and simple character-by-character `tcp_recv_line()` in `net_tcp.c`.
  * Handles `challenge <ID>` in the lobby: connects to peer `<ID>`'s advertised port and sends `CHALLENGE <my_name>\n`.
  * Prompts the target player to accept (`yes` $\rightarrow$ `ACCEPT\n`) or decline (`no` $\rightarrow$ `REJECT\n`).
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/net_tcp.c networking/mastermind/main.c
  git commit -m "mastermind: implement challenge handshake and persistent TCP session"
  ```

---

#### Checkpoint 15: Implement Sequence Validation, Feedback Rules, and 12-Row ANSI Board
* **Suggested Commit Message:** `mastermind: implement sequence validation, feedback rules, and ANSI board`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/game.c`
* **What Is Implemented:**
  * `is_valid_sequence()`: checks length is `5` and characters are `'0'..'9'`.
  * `is_valid_feedback()`: checks length is `5` and characters are `'x'`, `'o'`, or `'-'`.
  * `calculate_feedback()`: two-pass Mastermind algorithm (exact matches `'x'` first, then misplaced matches `'o'`, else `'-'`).
  * `print_board()`: prints the exact 12-row board format from the assignment writeup (and TA Doubt Doc Q10), with `*****  *****` at the top, guesses on the left, colored feedback on the right (`x` green, `o` yellow, `-` red), and `*****  *****` for remaining rounds.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/game.c
  git commit -m "mastermind: implement sequence validation, feedback rules, and ANSI board"
  ```

---

#### Checkpoint 16: Handle Game Completion and TCP Disconnection Recovery
* **Suggested Commit Message:** `mastermind: handle game completion and TCP disconnection recovery`
* **Files Modified:**
  * `networking/mastermind/main.c`
* **What Is Implemented:**
  * Connects the full Mastermind $\leftrightarrow$ Codebreaker turn loop (`READY`, `GUESS <seq>`, `FEEDBACK <fb>`, `GAMEOVER <master_seq>`).
  * Keeps the `master sequence` local to the Mastermind during gameplay and only reveals it in `GAMEOVER <master_seq>` when the Codebreaker gets `xxxxx` or exhausts all 12 attempts.
  * Detects peer TCP disconnection (`tcp_recv_line()` returning `-1` on `recv() == 0` EOF) and prints `<Player_name> disconnected. Press enter to go home.`
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/main.c
  git commit -m "mastermind: handle game completion and TCP disconnection recovery"
  ```

---

#### Checkpoint 17: Implement Chunked UDP State Transfer for Cost-Cutting Mode
* **Suggested Commit Message:** `mastermind: implement chunked UDP state transfer for cost-cutting mode`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/net_rudp.c`
* **What Is Implemented:**
  * `pack_chunk()` and `unpack_chunk()` explicitly pack/unpack the 20-byte UDP chunk buffer (`magic`, `type`, `msg_id`, `seq_num`, `total_chunks`, `data_len`, `data[4]`) using `memcpy`, `htonl`/`ntohl`, and `htons`/`ntohs` (per TA Doubt Doc Q27).
  * `rudp_send_message()` splits outgoing messages into 4-byte chunks and sends all chunks immediately without waiting for ACKs.
  * Buffers incoming chunks by `seq_num` so out-of-order chunks are reassembled in exact `0 .. total_chunks - 1` order once all chunks arrive.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/net_rudp.c
  git commit -m "mastermind: implement chunked UDP state transfer for cost-cutting mode"
  ```

---

#### Checkpoint 18: Add Per-Chunk ACK, 0.1s Retransmission, and UDP Disconnect Detection
* **Suggested Commit Message:** `mastermind: add per-chunk ACK, 0.1s retransmission, and UDP disconnect detection`
* **Files Modified:**
  1. `networking/mastermind/net_rudp.c`
  2. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Receiver sends a `PKT_ACK` for every received data chunk `(msg_id, seq_num, total_chunks)`.
  * `rudp_check_timers()` checks unacknowledged chunks in the `poll()` loop and retransmits any chunk whose `now - last_sent_ms >= 100` ms (`0.1 s`).
  * Detects UDP peer disconnection via `PKT_FIN`, chunk retry exhaustion (`> 50` retries), or 5-second `PKT_PING`/`PKT_PONG` heartbeat timeout, displaying `<Player_name> disconnected. Press enter to go home.`
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/net_rudp.c networking/mastermind/main.c
  git commit -m "mastermind: add per-chunk ACK, 0.1s retransmission, and UDP disconnect detection"
  ```

---

### Phase 5: Documentation & Final Verification

---

#### Checkpoint 19: Document Networking and `xv6` Implementation Details in `readme.md`
* **Suggested Commit Message:** `docs: document networking and xv6 implementation details in readme`
* **Files Modified:**
  * `readme.md`
* **What Is Implemented:**
  * Fills in every section of the provided `readme.md` template matching the exact struct and function names in our code.
* **Commit Command:**
  ```bash
  git add readme.md
  git commit -m "docs: document networking and xv6 implementation details in readme"
  ```

---

#### Checkpoint 20: Final Build and Test Verification Across `networking` and `xv6`
* **Suggested Commit Message:** `chore: final build and test verification across networking and xv6`
* **How to Run Full Verification Before Final Submission:**
  1. **Networking Build & Clean Test:**
     ```bash
     cd networking
     make clean && make all
     ```
  2. **Test `tempest` CLI Cases:**
     ```bash
     cd networking/tempest
     ./tempest Hyderabad
     ./tempest "New York"
     ./tempest Rotterdam --raw
     ./tempest notarealcity
     ./tempest a b
     ```
  3. **Test `mastermind` on 2 Laptops over Mobile Hotspot:**
     * Follow Section 2.2 above for both standard TCP mode (`./mastermind --log`) and cost-cutting UDP mode (`./mastermind --cost-cutting --log`).
  4. **`xv6` Automated Test Runner (Inside Ubuntu Docker Container):**
     ```bash
     cd xv6
     ./test-xv6.py cowtest
     ./test-xv6.py alarmtest
     ./test-xv6.py -q usertests
     ```
  5. **Clean All Compiled Binaries Before Pushing:**
     ```bash
     make -C networking clean
     make -C xv6 clean
     git status
     ```

---

## 5. Quick Cheat-Sheet of TA Viva Questions & Answers

### Part 1: Networking (`tempest` & `mastermind`)
1. **Why do we use `send_all()` and `recv_all_with_timeout()` loops instead of a single `send()` or `recv()` call?**
   * TCP is a byte-stream protocol without message boundaries. A single `send()` can write fewer bytes than requested if the kernel send buffer is nearly full, and an HTTP response may arrive across multiple TCP packets requiring multiple `recv()` calls until `recv()` returns `0` (EOF).
2. **How did you implement the 10-second timeout in `tempest`?**
   * Before calling `connect()`, we record `start_ms = get_time_ms()`. In `recv_all_with_timeout()`, before every `recv()` call, we compute `remaining = 10000 - (get_time_ms() - start_ms)` and pass `remaining` to `poll()`. If `remaining <= 0` or `poll()` returns `0`, we print `tempest: connection timed out` and exit with `1`.
3. **Why did you pack structs into a byte buffer (`pack_discovery_packet` and `pack_chunk`) instead of passing `struct` pointers directly to `sendto()`?**
   * C compilers may insert padding bytes between struct fields depending on alignment rules, and multi-byte integers (`uint32_t`, `uint16_t`) must be converted to network byte order (`htonl`, `htons`). Packing fields explicitly into a fixed-size `unsigned char buf[]` guarantees an exact wire format across machines (TA Doubt Doc Q27).
4. **Why is the sender's IP address extracted from `recvfrom()`'s `struct sockaddr_in` rather than placed inside the UDP broadcast payload?**
   * A laptop may have multiple network interfaces (`lo`, `en0`, `wlan0`, `docker0`). When `recvfrom()` receives a UDP broadcast packet on the hotspot subnet, the kernel fills `sender_addr.sin_addr` with the sender's actual routable IP address on that Wi-Fi network.
5. **In `--cost-cutting` mode, what happens if Chunk 2 arrives before Chunk 0, or if Chunk 1 is dropped?**
   * Every 20-byte chunk packet carries `msg_id`, `seq_num`, and `total_chunks`. When Chunk 2 arrives first, the receiver immediately sends a `PKT_ACK` for `seq_num = 2` and copies its 4 bytes into `rx_data[2]`. When Chunk 1 is dropped, the sender does not receive an ACK for `seq_num = 1` within `0.1 s` (`100 ms`), so `rudp_check_timers()` retransmits only Chunk 1. Once `rx_received_count == rx_total_chunks`, the receiver joins `rx_data[0 .. rx_total_chunks - 1]` in order.

### Part 2: `xv6` (`cow` & `alarms`)
1. **Which PTE bit did you use for Copy-on-Write and why?**
   * Bit 8 (`#define PTE_COW (1L << 8)` in `kernel/riscv.h`). In the RISC-V Sv39 page table entry format, bits 8 and 9 are the `RSW` (Reserved for Supervisor Software) bits, which the hardware MMU ignores and leaves for the OS kernel to use.
2. **Why do we need `pageref.lock` in `kalloc.c`?**
   * In `xv6` (which runs with `CPUS = 3` in QEMU), multiple processes on different CPU cores can share physical pages via `fork()` and simultaneously increment (`krefinc` in `uvmcopy`) or decrement (`kfree` on `cowfault` or `exit`) the same page's reference count. Without a spinlock, concurrent updates to `pageref.count[]` would race.
3. **Why must `copyout()` also check `PTE_COW`?**
   * System calls like `read()`, `pipe()`, and `wait()` copy data from the kernel to user memory using `copyout()`. Because `copyout()` translates user virtual addresses in software (`walkaddr()`) and writes through the kernel's direct-mapped physical address, the RISC-V MMU does not raise a user-mode store page fault. Therefore, `copyout()` must explicitly check `PTE_COW` and call `cowfault()`.
4. **Why does `sys_sigreturn()` return `p->trapframe->a0`?**
   * In `kernel/syscall.c`, `syscall()` stores the return value of every `sys_*` function into `p->trapframe->a0`. After `sys_sigreturn()` copies `*(p->alarm_tf)` back into `*(p->trapframe)`, returning `p->trapframe->a0` ensures that `p->trapframe->a0` retains its original pre-interrupt value (`alarmtest` `test3`).
