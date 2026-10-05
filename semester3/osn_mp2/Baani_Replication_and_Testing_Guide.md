# CS3.301 Operating Systems and Networks — Mini Project 2
## Complete Step-by-Step Replication, Testing, and Viva Guide for Baani

**Reference Repository (GitHub):** [`https://github.com/anshulsolanki/baani_assignments`](https://github.com/anshulsolanki/baani_assignments)  
**Working Project Folder:** `semester3/osn_mini_project_2/`  
**Reference & Test Suite Folder:** `semester3/osn_mp2/`

---

## 1. Overview & Golden Rules Before You Start

This guide gives you the exact **20-checkpoint sequence** that has already been implemented, tested, and committed one-by-one in `https://github.com/anshulsolanki/baani_assignments`. You can inspect each commit on GitHub (or locally via `git show <commit_hash>`) and replicate it step-by-step in your own private IIIT repository (`code.iiit.ac.in/osn/...`).

### Critical Assignment Rules to Keep in Mind
1. **Push Every Commit Within 24 Hours:**
   * Do **not** make all 20 commits in 10 minutes and push them in one big batch.
   * Spread your work naturally across days/sessions, and run `git push` after every checkpoint (or every couple of checkpoints) so the server push timestamps match your commit timestamps.
2. **Use Branches for `xv6` (`alarms` and `cow`) as Recommended by the Spec:**
   * The assignment handout specifically advises working on separate branches (`alarms` and `cow`) in `xv6` and then rebasing them together (`git rebase`). Section 3 below shows the exact branch and rebase commands to run so your git history matches the course git guide (`https://cs3301.pages.dev/resources/git`).
3. **Never Modify the Provided `Makefile`s in `networking/`:**
   * `networking/Makefile`, `networking/tempest/Makefile`, and `networking/mastermind/Makefile` already use `SRCS = $(wildcard *.c)` and `-std=c23 -D_POSIX_C_SOURCE=200809L -D_XOPEN_SOURCE=700 -Wall -Wextra -Werror -Wno-unused-parameter -g`.
   * Leave those three `Makefile`s untouched.
4. **Never Test `mastermind` on IIIT-H Campus Wi-Fi / LAN:**
   * Always use your **personal mobile hotspot** (or an isolated local Docker bridge network) when testing `mastermind`'s UDP broadcast discovery.

---

## 2. Environment Setup (Apple Silicon M5 Pro MacBook + Ubuntu 24.04 Docker)

### 2.1 Setting Up Your Ubuntu 24.04 ARM64 Container (For `xv6` & Linux `gcc` Verification)
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

### 2.2 Testing 2-Player `mastermind` on One MacBook vs. Two Laptops
* **On One MacBook (Using Two Docker Containers on the Same Bridge Network):**
  Open **two** terminal windows on your Mac and start two separate containers (`docker run -it --rm -v "/path/to/your/iiit-repo:/workspace" -w /workspace osn-mp2 bash`). Container 1 gets IP `172.17.0.2` and Container 2 gets IP `172.17.0.3` on the Docker bridge subnet, so their UDP broadcasts discover each other automatically!
* **On One MacBook (Using Two Native macOS Terminal Tabs Offline/Loopback):**
  You can also run two instances in two terminal tabs using `MM_BROADCAST_IP=127.0.0.1 ./mastermind`.
* **With a Friend's Laptop (Real 2-Laptop Test):**
  Connect both laptops to your **personal mobile hotspot** (never IIIT Wi-Fi) and run `./mastermind` (and `./mastermind --cost-cutting --log`) natively.

---

## 3. The 20 Incremental Checkpoints — Exact Replication Guide

You can view the exact diff of any checkpoint in the reference repo at any time using:
```bash
git show <commit_hash>
```

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
* **Reference Commit:** `c83e821` (`git show c83e821`)
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
* **Reference Commit:** `357f1c1` (`git show 357f1c1`)
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
* **Reference Commit:** `e17896e` (`git show e17896e`)
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
* **TA Viva Point:** *How do you prevent an alarm handler from being re-entered if the handler itself takes longer than `ticks`?*  
  We set `p->alarm_active = 1` before jumping to `p->alarm_handler`, and we only decrement `p->alarm_ticks_left` when `p->alarm_active == 0`. `p->alarm_active` stays `1` until the handler calls `sigreturn()`.

---

### Phase 2: `xv6` — Copy-on-Write (CoW) Fork [50 Marks]

> **Git Branch Workflow (Recommended by Spec):**
> Switch back to `main` and create a `cow` branch (or continue on `main` if you prefer a single linear branch, then rebase at Checkpoint 8):
> ```bash
> git checkout main
> git checkout -b cow
> ```

---

#### Checkpoint 4: Add Physical Page Reference Counting in `kalloc`
* **Reference Commit:** `cb3cdfa` (`git show cb3cdfa`)
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
* **Reference Commit:** `d39eb65` (`git show d39eb65`)
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
* **TA Viva Point:** *Why do we also clear `PTE_W` and set `PTE_COW` in `*pte` (the parent's PTE)?*  
  If the parent writes to the page before the child does, the parent must also trigger a store page fault and allocate its own private copy; otherwise the parent's write would silently modify the child's memory!

---

#### Checkpoint 6: Handle CoW Store Page Faults in `usertrap`
* **Reference Commit:** `51dfcc1` (`git show 51dfcc1`)
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
* **TA Viva Point:** *How does your CoW fault handler coexist with lazy `sbrk()` allocation (`vmfault`)?*  
  A CoW page is **already mapped** (`PTE_V` and `PTE_COW` are set) and faults only on a write (`r_scause() == 15`). A lazy `sbrk()` page is **unmapped** (`PTE_V == 0`). By checking `cowfault()` first on `r_scause() == 15`, mapped CoW pages are duplicated, while unmapped lazy `sbrk()` pages return `-1` from `cowfault()` and fall through to `vmfault()`.

---

#### Checkpoint 7: Handle CoW Pages in `copyout`
* **Reference Commit:** `23e83af` (`git show 23e83af`)
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
* **TA Viva Point:** *Why doesn't `copyout()` trigger a hardware page fault automatically?*  
  Because `copyout()` runs in supervisor mode using `kernel_pagetable` (where all physical RAM is direct-mapped RW) and walks the user page table in software via `walkaddr()`. Therefore, `copyout()` must explicitly check `PTE_COW` and call `cowfault()`.

---

#### Checkpoint 8: Rebase `cow` and `alarms` Branches and Format Code
* **Reference Commit:** `2e86cf4` (`git show 2e86cf4`)
* **Suggested Commit Message:** `xv6: rebase cow and alarms branches and format code`
* **Files Modified:**
  * `xv6/kernel/riscv.h` (and any formatting via `make fmt`)
* **What to Run (if you used separate `alarms` and `cow` branches):**
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

---

#### Checkpoint 9: Parse CLI Arguments and Implement URL Encoding
* **Reference Commit:** `2733028` (`git show 2733028`)
* **Suggested Commit Message:** `tempest: parse CLI arguments and implement URL encoding`
* **Files Created:**
  1. `networking/tempest/tempest.h`
  2. `networking/tempest/url.c`
  3. `networking/tempest/main.c`
* **What Is Implemented:**
  * `url_encode()` in `url.c` leaves RFC 3986 unreserved characters (`A-Z`, `a-z`, `0-9`, `-`, `_`, `.`, `~`) intact and converts all other bytes (including spaces) to `%XX` uppercase hex.
  * `main.c` parses `<city_name>` and optional trailing `--raw`. If more than 1 argument (other than a trailing `--raw`) is passed, it prints `tempest: too many arguments` and exits with `1`.
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

#### Checkpoint 10: Implement TCP Connection and HTTP GET Request with Timeout
* **Reference Commit:** `ade2cfa` (`git show ade2cfa`)
* **Suggested Commit Message:** `tempest: implement TCP connection and HTTP GET request with timeout`
* **Files Created / Modified:**
  1. `networking/tempest/tempest.h`
  2. `networking/tempest/http.c`
  3. `networking/tempest/main.c`
* **What Is Implemented:**
  * `http_connect()`: resolves `wttr.is:80` via `getaddrinfo()`, creates a `SOCK_STREAM` socket, sets a **10-second timeout** (`SO_RCVTIMEO` and `SO_SNDTIMEO`) via `setsockopt()`, and connects.
  * `send_all()`: loops until all bytes of the HTTP/1.1 request (`GET /<encoded_city>?0T HTTP/1.1\r\nHost: wttr.is\r\nUser-Agent: curl/8.0\r\nConnection: close\r\n\r\n`) are sent, handling short writes.
  * `recv_all()`: dynamically grows a buffer and reads in a loop until `recv()` returns `0` (EOF).
* **How to Test:**
  ```bash
  cd networking/tempest && make
  ```
* **Commit Command:**
  ```bash
  make -C networking/tempest clean
  git add networking/tempest/tempest.h networking/tempest/http.c networking/tempest/main.c
  git commit -m "tempest: implement TCP connection and HTTP GET request with timeout"
  ```

---

#### Checkpoint 11: Parse HTTP Status Line, Headers, and Chunked Body
* **Reference Commit:** `7c3cf32` (`git show 7c3cf32`)
* **Suggested Commit Message:** `tempest: parse HTTP status line, headers, and chunked body`
* **Files Modified:**
  * `networking/tempest/http.c`
* **What Is Implemented:**
  * Finds `\r\n\r\n` to separate the HTTP status line + headers from the body.
  * Extracts the HTTP status code from `HTTP/1.1 <status> ...`.
  * Decodes `Transfer-Encoding: chunked` bodies (`decode_chunked()`) if the header is present.
  * Detects invalid locations (`status_code == 404` or body containing `"Unknown location"` / `"not found"`) and prints `tempest: invalid location`.
  * In `--raw` mode, prints each line of the outgoing HTTP request prefixed with `> ` and each line of the incoming HTTP headers prefixed with `< `, followed by the weather report body.
* **How to Test:**
  ```bash
  cd networking/tempest && make
  ./tempest Hyderabad
  ./tempest "New York"
  ./tempest Rotterdam --raw
  ./tempest InvalidCityXYZ987
  ./tempest a b
  ```
* **Commit Command:**
  ```bash
  make -C networking/tempest clean
  git add networking/tempest/http.c
  git commit -m "tempest: parse HTTP status line, headers, and chunked body"
  ```

---

### Phase 4: `networking/mastermind` — Peer-to-Peer LAN Game [40 Marks]

---

#### Checkpoint 12: Define Protocol Constants, Structs, and Logging Utility
* **Reference Commit:** `c15dfad` (`git show c15dfad`)
* **Suggested Commit Message:** `mastermind: define protocol constants, structs, and logging utility`
* **Files Created:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/log.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Defines the 4-byte protocol magic `MM_MAGIC` (`0x4D4D4E44` = `"MMND"`), discovery constants (2s broadcast, 5s expiry), RUDP constants (`MM_CHUNK_DATA_SIZE = 4`, 0.1s retransmit), message verbs (`CHALLENGE`, `ACCEPT`, `REJECT`, `READY`, `GUESS`, `FEEDBACK`, `GAMEOVER`, `DISCONNECT`), and structs.
  * Implements `log_event()` in `log.c` using the exact `gettimeofday()` + `strftime()` microsecond timestamp format from the assignment specification, appending to `log.txt` when `--log` is passed.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/log.c networking/mastermind/main.c
  git commit -m "mastermind: define protocol constants, structs, and logging utility"
  ```

---

#### Checkpoint 13: Implement UDP Broadcast Player Discovery and Peer Expiry
* **Reference Commit:** `a6e78f0` (`git show a6e78f0`)
* **Suggested Commit Message:** `mastermind: implement UDP broadcast player discovery and peer expiry`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/discovery.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Creates a UDP socket with `SO_BROADCAST`, `SO_REUSEADDR`, and `SO_REUSEPORT` bound to port `33301`.
  * Broadcasts `struct discovery_pkt` (`magic`, `listen_port`, `name`) every **2 seconds**.
  * On receiving a broadcast, checks `ntohl(pkt.magic) == MM_MAGIC`, extracts the sender's IP from `recvfrom()`'s `struct sockaddr_in` (never from the payload), updates or inserts the peer in `peers[]`, and removes any peer whose `now - last_seen_ms >= 5000` (5 seconds).
  * Renders the `Players Online:` table (`ID`, `Name`, `IP Addr`, `Port`, `Last Seen`).
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/discovery.c networking/mastermind/main.c
  git commit -m "mastermind: implement UDP broadcast player discovery and peer expiry"
  ```

---

#### Checkpoint 14: Implement Challenge Handshake and Persistent TCP Session
* **Reference Commit:** `5906e3e` (`git show 5906e3e`)
* **Suggested Commit Message:** `mastermind: implement challenge handshake and persistent TCP session`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/net_tcp.c`
  3. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Implements `tcp_connect_peer()`, `tcp_send_msg()`, and buffered newline-delimited `tcp_recv_line()` in `net_tcp.c`.
  * Handles `challenge <ID>` in the lobby: connects to peer `<ID>`'s advertised TCP port and sends `CHALLENGE <my_name>\n`.
  * Prompts the target player to accept (`yes` $\rightarrow$ sends `ACCEPT\n`) or decline (`no` $\rightarrow$ sends `REJECT\n` and returns both players to the discovery lobby).
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/net_tcp.c networking/mastermind/main.c
  git commit -m "mastermind: implement challenge handshake and persistent TCP session"
  ```

---

#### Checkpoint 15: Implement Sequence Validation, Feedback Rules, and ANSI Board
* **Reference Commit:** `a5dcd8e` (`git show a5dcd8e`)
* **Suggested Commit Message:** `mastermind: implement sequence validation, feedback rules, and ANSI board`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/game.c`
* **What Is Implemented:**
  * `game_validate_sequence()`: verifies string length is `5` and every character is `'0'..'9'`.
  * `game_validate_feedback()`: verifies string length is `5` and every character is `'x'`, `'o'`, or `'-'`.
  * `game_compute_expected_feedback()`: two-pass Mastermind feedback algorithm (exact matches `'x'` first, then misplaced matches `'o'`, else `'-'`).
  * `game_render_board()`: renders the 12-attempt board with `* * * * *` masking the secret sequence on the Codebreaker's screen and ANSI color coding (`x` Green `\033[32m`, `o` Yellow `\033[33m`, `-` Red `\033[31m`).
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/game.c
  git commit -m "mastermind: implement sequence validation, feedback rules, and ANSI board"
  ```

---

#### Checkpoint 16: Handle Game Completion and TCP Disconnection Recovery
* **Reference Commit:** `251c226` (`git show 251c226`)
* **Suggested Commit Message:** `mastermind: handle game completion and TCP disconnection recovery`
* **Files Modified:**
  * `networking/mastermind/main.c`
* **What Is Implemented:**
  * Connects the full Mastermind $\leftrightarrow$ Codebreaker turn loop (`READY`, `GUESS <seq>`, `FEEDBACK <fb>`, `GAMEOVER <master_seq>`).
  * Keeps the `master sequence` local to the Mastermind during gameplay and only reveals it in `GAMEOVER <master_seq>` when the Codebreaker gets `xxxxx` or exhausts all 12 attempts.
  * Detects peer TCP disconnection (`tcp_recv_line()` returning `-1` on `recv() == 0` EOF) and prints `<Player_name> disconnected. Press enter to go home.` before returning to the discovery lobby on Enter.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/main.c
  git commit -m "mastermind: handle game completion and TCP disconnection recovery"
  ```

---

#### Checkpoint 17: Implement Chunked UDP State Transfer for Cost-Cutting Mode
* **Reference Commit:** `67a4c50` (`git show 67a4c50`)
* **Suggested Commit Message:** `mastermind: implement chunked UDP state transfer for cost-cutting mode`
* **Files Created / Modified:**
  1. `networking/mastermind/mastermind.h`
  2. `networking/mastermind/net_rudp.c`
* **What Is Implemented:**
  * Splits outgoing messages into fixed 4-byte payload chunks (`struct rudp_pkt` with `magic`, `type`, `msg_id`, `seq_num`, `total_chunks`, `data_len`, `data[4]`).
  * Sends all chunks of a message immediately in a pipeline without waiting for ACKs.
  * Buffers incoming chunks by `seq_num` in `struct rudp_rx_msg` so out-of-order chunks are reassembled in exact `0 .. total_chunks - 1` order once `received_count == total_chunks`.
* **Commit Command:**
  ```bash
  make -C networking/mastermind && make -C networking/mastermind clean
  git add networking/mastermind/mastermind.h networking/mastermind/net_rudp.c
  git commit -m "mastermind: implement chunked UDP state transfer for cost-cutting mode"
  ```

---

#### Checkpoint 18: Add Per-Chunk ACK, 0.1s Retransmission, and UDP Disconnect Detection
* **Reference Commit:** `30d0be0` (`git show 30d0be0`)
* **Suggested Commit Message:** `mastermind: add per-chunk ACK, 0.1s retransmission, and UDP disconnect detection`
* **Files Modified:**
  1. `networking/mastermind/net_rudp.c`
  2. `networking/mastermind/main.c`
* **What Is Implemented:**
  * Receiver sends an `RUDP_PKT_ACK` for every received data chunk `(msg_id, seq_num, total_chunks)`.
  * Sender's `rudp_tick()` checks unacknowledged chunks in the `poll()` loop and retransmits any chunk whose `now - last_sent_ms >= 100` ms (`0.1 s`).
  * Detects UDP peer disconnection via `RUDP_PKT_FIN`, chunk retry exhaustion, or 5-second `RUDP_PKT_PING`/`RUDP_PKT_PONG` heartbeat timeout, displaying `<Player_name> disconnected. Press enter to go home.`
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
* **Reference Commit:** `bd06a9f` (`git show bd06a9f`)
* **Suggested Commit Message:** `docs: document networking and xv6 implementation details in readme`
* **Files Modified:**
  * `readme.md` (and `ai-usage.md` if applicable)
* **What Is Implemented:**
  * Fills in every section of the provided `readme.md` template:
    * `tempest` design, changed defaults (`none`), assumptions, known bugs (`none known`).
    * `mastermind` design, 4-byte magic (`0x4D4D4E44`), broadcast payload layout, message verbs, `--cost-cutting` chunk struct & ACK/retransmit scheme, TCP & UDP disconnection detection.
    * `xv6` Copy-on-Write reference counts/locking, `PTE_COW` bit, write fault duplication, and `sigalarm`/`sigreturn` `struct proc` fields & re-entrancy prevention.
* **Commit Command:**
  ```bash
  git add readme.md
  git commit -m "docs: document networking and xv6 implementation details in readme"
  ```

---

#### Checkpoint 20: Final Build and Test Verification Across `networking` and `xv6`
* **Reference Commit:** `b481dcd` (`git show b481dcd`)
* **Suggested Commit Message:** `chore: final build and test verification across networking and xv6`
* **How to Run Full Verification Before Final Submission:**
  1. **Networking Build & Clean Test:**
     ```bash
     cd networking
     make clean && make all
     ```
  2. **Automated Verification Suite (`test_mp2.py` — keep outside your IIIT repo):**
     ```bash
     python3 /path/to/semester3/osn_mp2/test_mp2.py
     ```
  3. **`xv6` Automated Test Runner (Inside Ubuntu Docker Container):**
     ```bash
     cd xv6
     ./test-xv6.py cowtest
     ./test-xv6.py alarmtest
     ./test-xv6.py -q usertests
     ```

---

## 4. Quick Cheat-Sheet of TA Viva Questions & Answers

### Part 1: Networking (`tempest` & `mastermind`)
1. **Why do we use `send_all()` and `recv_all()` loops instead of a single `send()` or `recv()` call?**
   * TCP is a byte-stream protocol without message boundaries. A single `send()` can write fewer bytes than requested if the kernel send buffer is nearly full (short write), and an HTTP response or game message may arrive fragmented across multiple TCP segments requiring multiple `recv()` calls.
2. **How does `tempest` know when the HTTP/1.1 response is complete?**
   * We send `Connection: close` in the HTTP request headers. Per RFC 9112 § 9.3, the server closes the TCP connection after transmitting the full response body, causing `recv()` to return `0` (EOF).
3. **Why is the sender's IP address extracted from `recvfrom()`'s `struct sockaddr_in` rather than placed inside the UDP broadcast payload?**
   * A machine may have multiple network interfaces (`lo`, `eth0`, `wlan0`, `docker0`) and does not necessarily know which interface's IP address routes to a given peer prior to sending a broadcast to `255.255.255.255`. The IP header's source address populated by the kernel in `recvfrom()` is guaranteed to be the sender's routable interface address on that subnet.
4. **In `--cost-cutting` mode, what happens if Chunk 2 arrives before Chunk 0, or if Chunk 1 is dropped?**
   * Every chunk header carries `msg_id`, `seq_num`, and `total_chunks`. When Chunk 2 arrives first, the receiver immediately sends an `RUDP_PKT_ACK` for `seq_num = 2` and stores its 4 bytes at `slot->chunk_data[2]`. When Chunk 1 is dropped, the sender does not receive an ACK for `seq_num = 1` within `0.1 s` (`100 ms`), so `rudp_tick()` retransmits only Chunk 1. Once `slot->received_count == slot->total_chunks`, the receiver concatenates `chunk_data[0 .. total_chunks - 1]` in order.

### Part 2: `xv6` (`cow` & `alarms`)
1. **Which PTE bit did you use for Copy-on-Write and why?**
   * Bit 8 (`#define PTE_COW (1L << 8)` in `kernel/riscv.h`). In the RISC-V Sv39 page table entry format, bits 8 and 9 are the `RSW` (Reserved for Supervisor Software) bits, which the hardware MMU ignores and leaves for the OS kernel to use.
2. **Why do we need `pageref.lock` in `kalloc.c`?**
   * In `xv6` (which runs with `CPUS = 3` in QEMU), multiple processes on different CPU cores can share physical pages via `fork()` and simultaneously increment (`krefinc` in `uvmcopy`) or decrement (`kfree` on `cowfault` or `exit`) the same page's reference count. Without a spinlock, concurrent updates to `pageref.count[]` would race and either leak pages or free a page still in use by another process.
3. **Why must `copyout()` also check `PTE_COW`?**
   * System calls like `read()`, `pipe()`, and `wait()` copy data from the kernel to user memory using `copyout()`. Because `copyout()` translates user virtual addresses in software (`walkaddr()`) and writes through the kernel's direct-mapped physical address, the RISC-V MMU does not raise a user-mode store page fault. If `copyout()` did not check `PTE_COW` and call `cowfault()`, it would either fail (since `PTE_W == 0`) or overwrite shared memory.
4. **Why does `sys_sigreturn()` return `p->trapframe->a0`?**
   * In `kernel/syscall.c`, `syscall()` stores the return value of every `sys_*` function into `p->trapframe->a0`. After `sys_sigreturn()` copies `*(p->alarm_tf)` back into `*(p->trapframe)`, returning `p->trapframe->a0` ensures that `p->trapframe->a0` retains its original pre-interrupt value (`alarmtest` `test3`).
