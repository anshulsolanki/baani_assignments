# CS3.301 Operating Systems and Networks — Mini Project 2
## Complete Project Specification, Boilerplate Analysis & Checkpoint Execution Plan

**Course:** CS3.301 Operating Systems and Networks (IIIT Hyderabad, Monsoon 2026)  
**Official Assignment Page:** [https://cs3301.pages.dev/assignments/02](https://cs3301.pages.dev/assignments/02)  
**Released:** September 16, 2026  
**Final Deadline:** **October 15, 2026 at 11:59 PM** (No extensions)  
**Doubt Document Cutoff:** **October 10, 2026 at 11:59 PM**

---

## 1. Overview & General Rules

Build a weather client (`tempest`) and a networked Mastermind game (`mastermind`) over raw POSIX sockets, and implement copy-on-write `fork()` and process alarms (`sigalarm` / `sigreturn`) in the `xv6` kernel.

**This is an individual assignment** divided into two major parts:
1. **Part 1: Networking in C using Raw POSIX Sockets** (`networking/` — **55 marks** header / **60 marks** sum of sub-parts)
2. **Part 2: xv6 Operating System Kernel Modifications** (`xv6/` — **90 marks**)

### Repository Structure & What Is Already in `mp2_boilerplate`
Work must be done exclusively inside the allocated private repository under the `osn` organization on `code.iiit.ac.in`:
```text
mini-project2/
├── networking/
│   ├── Makefile                # Provided: runs $(MAKE) -C tempest and $(MAKE) -C mastermind
│   ├── tempest/
│   │   └── Makefile            # Provided: compiles $(wildcard *.c) -> networking/tempest/tempest
│   └── mastermind/
│       └── Makefile            # Provided: compiles $(wildcard *.c) -> networking/mastermind/mastermind
├── xv6/
│   ├── user/                   # Provided: cowtest.c, alarmtest.c, usertests.c, user.h, usys.pl
│   ├── kernel/                 # Provided: riscv64 kernel with lazy sbrk (vmfault) & alarm syscall stubs
│   ├── Makefile                # Provided: builds kernel & fs.img (already includes _cowtest & _alarmtest)
│   └── test-xv6.py             # Provided: automated test runner for cowtest, alarmtest, usertests
├── ai-usage.md                 # Provided: empty file for chat links
└── readme.md                   # Provided: structured template with HTML comment prompts to fill in
```

### Critical Findings from Inspecting `mp2_boilerplate`
1. **Do NOT Modify the Networking `Makefile`s:**
   * `networking/Makefile`, `networking/tempest/Makefile`, and `networking/mastermind/Makefile` are already configured with the exact C23 compiler flags and `SRCS = $(wildcard *.c)`.
   * Any `.c` files you create inside `networking/tempest/` and `networking/mastermind/` will automatically be compiled into `networking/tempest/tempest` and `networking/mastermind/mastermind` when you run `make all` in `networking/`.
   * Avoid using `<math.h>` functions so you don't even need to edit `LDLIBS` in the provided `Makefile`s.
2. **What Is Already Wired Up in `mp2_boilerplate/xv6` (Crucial for TA Review!):**
   * **Syscall numbers and stubs for `sigalarm` and `sigreturn` are ALREADY present** in `kernel/syscall.h` (`SYS_sigalarm = 23`, `SYS_sigreturn = 24`), `kernel/syscall.c`, `user/user.h`, `user/usys.pl`, and `kernel/sysproc.c` (which has `TODO(mini-project 2)` stubs for `sys_sigalarm` and `sys_sigreturn`). You do **not** need to touch `syscall.h`, `syscall.c`, `user.h`, or `usys.pl`!
   * **Lazy page allocation (`vmfault`) is ALREADY implemented** in this version of `xv6` (`kernel/vm.c` lines 458–491 and `kernel/trap.c` lines 71–74). Your Copy-on-Write (CoW) page fault handler **must coexist cleanly with `vmfault()`** so lazy `sbrk()` allocation continues to pass `usertests`.
   * **Kernel Naming Conventions in This Boilerplate:** This `xv6` codebase uses `printk()` (not `printf()`) and `kexit()`, `kfork()`, `kwait()`, `kkill()`, `kexec()` inside `kernel/`. It also includes a `.clang-format` file and a `make fmt` target in `xv6/Makefile`.
3. **Structured `readme.md` Template:**
   * `mp2_boilerplate/readme.md` already has exact section headers and HTML comments (`<!-- ... -->`) specifying what to write for each subsection. Fill in that exact file rather than replacing its structure.

---

## 2. Answering Baani's Technical & Environment Questions

### Q1: Apple Silicon (M5 Pro) MacBook — Docker (Ubuntu ARM64) vs. Distrobox vs. GitHub Codespaces?
* **Recommendation:** **Docker with an Ubuntu 24.04 LTS ARM64 container** (using Docker Desktop or **OrbStack**, which is lighter and faster on Apple Silicon) is the **best primary choice**, paired with native macOS terminal testing for 2-laptop Wi-Fi hotspot tests.
* **Why Ubuntu 24.04 ARM64 in Docker is best:**
  1. **Zero CPU Emulation Overhead:** Ubuntu ARM64 runs natively on Apple Silicon M5 Pro cores at full speed, while still providing genuine Linux `gcc` (GCC 13/14 with full `-std=c23` support), Linux glibc headers, `qemu-system-riscv64` ($\ge 7.2$), and `gcc-riscv64-unknown-elf`.
  2. **Identical to TA Grading Environment:** TAs grade on Linux. Code compiled with Apple Clang on macOS can accidentally rely on BSD/Darwin header behavior or fail on Linux `-D_POSIX_C_SOURCE=200809L`.
  3. **How to Test 2-Player UDP Broadcast Inside Docker on One MacBook:**
     * By default, Docker creates a bridge subnet (e.g., `172.17.0.0/16` with broadcast `172.17.255.255` or `255.255.255.255`).
     * If you start **two separate containers** mounting your project folder (`docker run -it --rm -v "$PWD":/work -w /work osn-mp2 bash` in two terminal tabs), Container 1 gets IP `172.17.0.2` and Container 2 gets IP `172.17.0.3`. They can discover each other via UDP broadcast and play `mastermind` over both TCP and `--cost-cutting` UDP on a single laptop!
  4. **Important Caveat for 2-Laptop Hotspot Testing on Mac:**
     * Docker Desktop on macOS runs inside a Linux VM behind NAT, so UDP broadcast packets from a *friend's physical laptop* on your mobile hotspot won't cross into a macOS Docker container cleanly.
     * **Solution:** Because our networking code will use standard POSIX `poll()` (which works on **both** Linux and macOS, unlike Linux-only `epoll`), your exact same C code will compile and run **both** inside your Ubuntu Docker container **and** natively on macOS when testing with a friend's laptop over a mobile hotspot.

#### Quick Docker Setup (`Dockerfile` for local use — do NOT commit to repo):
```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    build-essential gcc gdb make perl python3 bc \
    clang-format git curl netcat-openbsd iproute2 iputils-ping \
    qemu-system-misc gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf
WORKDIR /workspace
```

---

### Q2: Key Corrections & Clarifications on Baani's Notes (`osn_mp2_planning_and_requirements.md`)
1. **Is Chunked Encoding Needed in `tempest`?**
   * When sending `GET /<city>?0T HTTP/1.1` with `Connection: close`, `wttr.is` normally replies with a `Content-Length` header and closes the connection after sending the body.
   * However, because the Networking references explicitly list **RFC 7230 §§ 3.1–3.3 (HTTP message syntax and chunked encoding)**, we should include a clean ~25-line decoder for `Transfer-Encoding: chunked` alongside `Content-Length` / read-until-EOF. That way, whether `wttr.is` or a TA test script sends `Content-Length` or `Transfer-Encoding: chunked`, `tempest` handles both effortlessly.
2. **Mastermind Broadcast Interval (2 Seconds vs. 5 Seconds):**
   * In your notes, you wrote *"every 5 secs if not refreshed, remove from player table. Each player broadcasts every 5 secs."*
   * **Correction:** The spec and `mp2_boilerplate/readme.md` (line 69) state:
     * **Broadcast frequency:** Every **2 seconds**
     * **Player expiry timeout:** Every **5 seconds**
     * *(If you broadcast only every 5s and expire at 5s, a 1ms network delay would delete online players from the table! Always broadcast every 2s and expire after 5s.)*
3. **How to Demarcate TCP Message Boundaries in `mastermind` (`\n` Framing):**
   * You noted: *"TCP send byte stream, how to demarkate the start and end of a msg?? (using `\n`?)"*
   * **Yes!** Because TCP is a byte stream (`1 send() != 1 recv()`), newline-delimited (`\n`) text framing with a per-connection receive buffer is the cleanest, most debuggable design. Each message is a single line `VERB [payload]\n`, buffered until `\n` is seen.

---

## 3. Authenticity & Anti-AI-Detection Strategy (TA Evaluation & Git Hygiene)

To ensure the project is 100% authentic, transparent, and passes both git-history inspection and the live TA viva:

1. **Incremental Git History (Never Push Big Drops):**
   * Follow the **20-Checkpoint Commit Plan** in Section 6 below.
   * Each checkpoint is a small, self-contained step (30–120 lines of code) that compiles and can be tested immediately.
   * **Push every commit within 24 hours** of making it.
2. **Write & Re-Type Each Checkpoint Yourself:**
   * Rather than copy-pasting whole files, build one checkpoint at a time, compile it, test it, and make sure you can explain every variable, struct field, and condition in your own words.
3. **Keep Code Idiomatic & Simple:**
   * Use straightforward C data structures (fixed-size arrays for the player table and 12×5 board, clear helper functions, standard `poll()` loop).
   * In `xv6`, always follow existing `xv6` conventions (`printk`, `acquire`/`release`, `PGROUNDDOWN`, `PTE2PA`, `PA2PTE`) and run `make fmt` before committing.

---

## 4. Detailed Technical Specification: Part 1 — Networking (`networking/`) [55 Marks]

### General Networking Rules
* **Compiler Flags (already in `tempest/Makefile` and `mastermind/Makefile`):**
  ```bash
  gcc -std=c23 -D_POSIX_C_SOURCE=200809L -D_XOPEN_SOURCE=700 \
      -Wall -Wextra -Werror -Wno-unused-parameter -g
  ```
* **Allowed API:** `socket`, `bind`, `listen`, `accept`, `connect`, `send`, `sendto`, `recv`, `recvfrom`, `setsockopt`, `getsockopt`, `getaddrinfo`, `shutdown`, `close`, and `poll`, `select`, or `epoll`.
* **Banned:** `libcurl`, `libevent`, `libuv`, `ZeroMQ`, `ENet`, or shelling out to `curl`/`wget`/`nc`.
* **Testing Warning:** **Never** test on IIIT-H WiFi or LAN. Always use a personal mobile hotspot (or isolated local Docker bridge network).

---

### Part A: `tempest` — HTTP/1.1 Weather Client [15 Marks]

#### Modular File Layout (`networking/tempest/`):
```text
networking/tempest/
├── Makefile        # Provided (do not modify)
├── tempest.h       # Constants, structs, and function prototypes
├── url.c           # URL percent-encoding for <city_name>
├── http.c          # DNS lookup, TCP connect with 10s timeout, send_all, recv_response, header/body/chunk parsing
└── main.c          # CLI argument parsing (<city> and optional trailing --raw) and output printing
```

#### Requirements & Exact Behavior:
1. **CLI Syntax:**
   * `$ ./tempest <city_name>` or `$ ./tempest <city_name> --raw`
   * The `--raw` flag, if present, **must** appear after `<city_name>`.
   * If more than one argument (besides a trailing `--raw`) is provided, print `tempest: too many arguments` and exit.
2. **URL Encoding (`url.c`):**
   * Convert spaces and non-unreserved characters in `<city_name>` to `%XX` hex format (e.g., `"New York"` $\rightarrow$ `"New%20York"`). Unreserved characters (`A-Z`, `a-z`, `0-9`, `-`, `_`, `.`, `~`) remain unchanged.
3. **HTTP/1.1 Request Format (`http.c`):**
   ```http
   GET /<url_encoded_city>?0T HTTP/1.1\r\n
   Host: wttr.is\r\n
   User-Agent: curl/8.0\r\n
   Connection: close\r\n
   \r\n
   ```
   *(Note: `User-Agent: curl/...` ensures `wttr.is` returns compact plain-text ASCII art rather than an HTML page, and `Connection: close` tells the server to close the TCP connection once the response is complete per RFC 9112 § 9.3.)*
4. **10-Second Timeout & Short Read/Write Handling:**
   * Enforce a **10-second timeout** across the request lifecycle (using `setsockopt` with `SO_RCVTIMEO`/`SO_SNDTIMEO` and/or `poll()` timeout tracking elapsed time).
   * Implement `send_all(fd, buf, len)` in a `while` loop to handle short writes.
   * Implement `recv_all(fd, ...)` in a `while` loop until `recv()` returns `0` (EOF) to handle short reads and TCP stream fragmentation.
5. **Response Parsing & Invalid Location Detection:**
   * Locate `\r\n\r\n` to split the HTTP status line + headers from the body.
   * Parse the status code from `HTTP/1.1 <status> ...`.
   * Detect invalid locations: if HTTP status is `404` (or non-200) or the body starts with `"Unknown location"` / contains the `wttr.is` invalid location message, print:
     ```text
     tempest: invalid location
     ```
   * If `Transfer-Encoding: chunked` is present in the headers, decode the chunked body (`<hex_len>\r\n<chunk_data>\r\n...0\r\n\r\n`).
6. **Output Modes:**
   * **Normal mode:** Print only the decoded response body.
   * **`--raw` mode:** Print each line of the outgoing HTTP request prefixed with `> `, then each line of the received HTTP response headers (including the blank line) prefixed with `< `, followed by the response body.

---

### Part B: `mastermind` — P2P LAN Game over TCP & Reliable UDP [40 Marks]

#### Modular File Layout (`networking/mastermind/`):
```text
networking/mastermind/
├── Makefile        # Provided (do not modify)
├── mastermind.h    # Protocol verbs, magic constant, structs (peer, chunk, game_state), prototypes
├── log.c           # --log implementation with gettimeofday() + strftime() appending to log.txt
├── discovery.c     # UDP broadcast sender/receiver (2s interval, 4-byte magic, 5s peer expiry table)
├── net_tcp.c       # Normal mode persistent TCP session, \n message framing, disconnect detection
├── net_rudp.c      # --cost-cutting mode: fixed-size struct chunks, seq_num, per-chunk ACK, 0.1s retransmit
├── game.c          # Input validation, feedback calculation/validation, 12x5 board state, ANSI rendering
└── main.c          # Startup prompt, non-blocking poll() event loop multiplexing stdin + UDP + TCP/RUDP
```

#### Complete Specification of Sub-Components:
1. **Player Discovery (`discovery.c`) [8 Marks]:**
   * **4-Byte Magic Identifier:** e.g., `0x4D4D4E44` (`"MMND"` in ASCII — 4 bytes). Every UDP broadcast packet begins with these 4 bytes; ignore any packet that does not match.
   * **Broadcast Payload Layout:**
     ```c
     struct discovery_pkt {
         uint32_t magic;       // htonl(0x4D4D4E44)
         uint16_t listen_port; // htons(my_listen_port)
         char name[32];        // null-terminated player name
     };
     ```
     *(Never put the sender's IP in the payload; extract it from `recvfrom()`'s `struct sockaddr_in src_addr.sin_addr` via `inet_ntop()`.)*
   * **Timers:** Send broadcast every **2 seconds** to `255.255.255.255` (or subnet broadcast) on a fixed discovery UDP port (with `SO_BROADCAST` and `SO_REUSEADDR`/`SO_REUSEPORT` enabled). Remove any peer from the `Players Online` table if `now - peer.last_seen > 5.0` seconds.
2. **Starting the Game & Lobby (`main.c`, `discovery.c`) [2 Marks]:**
   * Prompt for player name on startup, bind an ephemeral/available listening port for game sessions, and enter the `poll()` loop displaying:
     ```text
     Players Online:
     ID       Name         IP Addr     Port    Last Seen
     1    Tatva           10.2.35.123  8080    2 s. ago
     2    ristiavdaatnso  10.2.35.125  8000    1 s. ago
     ____________________________________________________
     > 
     ```
   * Command `challenge <ID>` connects to Peer `<ID>`'s `IP:Port` and sends `CHALLENGE <my_name>\n`.
   * Target player sees the challenge prompt and types `yes` (sends `ACCEPT\n`, starts game) or `no` (sends `REJECT\n`, both return to discovery lobby).
3. **Gameplay & Validation (`game.c`) [15 Marks]:**
   * **Initiator (`Feena`) = Mastermind**; **Acceptor (`Tatva`) = Codebreaker**.
   * **Sequence Validation:** Both the 5-digit `master sequence` and every 5-digit `attempt` must be validated: `strlen(s) == 5` and all 5 characters in `'0'..'9'`.
   * **Feedback Validation:** Must be `strlen(fb) == 5` and every character in `{'x', 'o', '-'}`:
     * `x` = right digit, right position (colored **Green** `\033[32m` on Codebreaker's board)
     * `o` = right digit, wrong position (colored **Yellow** `\033[33m` on Codebreaker's board)
     * `-` = digit not present (colored **Red** `\033[31m` on Codebreaker's board)
   * **Secret Protection:** Never send `master sequence` over the network during gameplay! Only send it in the final `GAMEOVER <master_seq>\n` message when the game ends (after attempt 12 or when all 5 digits are `xxxxx`).
4. **Failure Management (Disconnection Detection):**
   * If the peer closes their program or disconnects mid-game, print:
     ```text
     <Player_name> disconnected. Press enter to go home.
     ```
   * **TCP Detection:** `recv()` returns `0` (EOF) or `-1` with fatal error, or `poll()` reports `POLLHUP | POLLERR`.
   * **UDP (`--cost-cutting`) Detection:** Either a `DISCONNECT` control packet when closing, periodic `PING`/`PONG` heartbeat timeout (e.g., 5 seconds without any packet), or exceeding maximum chunk retransmission retries (e.g., 30 retries = 3.0 seconds of unacknowledged chunks).
5. **Cost Cutting Mode (`--cost-cutting` in `net_rudp.c`) [15 Marks]:**
   * Replaces TCP with UDP for all game state transfers.
   * **Chunk Struct:**
     ```c
     #define CHUNK_DATA_SIZE 4
     struct rudp_pkt {
         uint32_t magic;        // Packet identifier
         uint8_t  type;         // PKT_DATA (1), PKT_ACK (2), PKT_PING (3), PKT_PONG (4), PKT_FIN (5)
         uint16_t msg_id;       // Message number
         uint16_t seq_num;      // Chunk sequence number (0 .. total_chunks - 1)
         uint16_t total_chunks; // Total number of chunks in this message
         uint16_t data_len;     // Valid bytes in data[]
         char     data[CHUNK_DATA_SIZE];
     };
     ```
     *(Using a small fixed `CHUNK_DATA_SIZE`, e.g., 4 bytes, ensures even short messages like `"GUESS 12345\n"` split into multiple chunks so chunk reordering, aggregation, and per-chunk ACKs are genuinely exercised!)*
   * **Pipelined Send & 0.1s Retransmission:**
     * Sender transmits all chunks `0 .. total_chunks - 1` immediately without waiting for ACKs.
     * Receiver sends a `PKT_ACK` referencing `(msg_id, seq_num)` for every received chunk, buffers chunks by `seq_num`, and delivers the reassembled text once all `total_chunks` have arrived.
     * Sender's `poll()` loop checks unacknowledged chunks every ~10–20 ms; any chunk whose `now - last_sent >= 0.1s` (100 ms) is retransmitted.
6. **Logging (`--log` in `log.c`) [5 Marks]:**
   * When `--log` is passed, append every sent/received event to `log.txt` using the exact `gettimeofday` + `strftime` snippet from the specification.

---

## 5. Detailed Technical Specification: Part 2 — xv6 Kernel (`xv6/`) [90 Marks]

### Part A: Copy-on-Write (CoW) Fork [50 Marks]

#### Exact Files Modified in `mp2_boilerplate/xv6`:
1. `kernel/riscv.h`:
   * Define the CoW software bit in the PTE (bits 8 and 9 are reserved for supervisor software in RISC-V Sv39):
     ```c
     #define PTE_COW (1L << 8)
     ```
2. `kernel/defs.h`:
   * Declare reference-count helper functions in `kalloc.c` (e.g., `void krefinc(void *pa);` or `int cowalloc(pagetable_t pagetable, uint64 va);`).
3. `kernel/kalloc.c` **[10 Marks — Reference Counting]**:
   * Maintain a reference count array for all physical pages from `KERNBASE` to `PHYSTOP`:
     ```c
     struct {
       struct spinlock lock;
       int count[(PHYSTOP - KERNBASE) / PGSIZE];
     } pageref;
     ```
   * In `kinit()`: initialize `pageref.lock` before calling `freerange()`.
   * In `freerange()`: set initial ref count so `kfree()` during boot frees each page properly.
   * In `kalloc()`: when a page `r` is allocated, set its ref count to `1`.
   * Add `krefinc(void *pa)`: acquire `pageref.lock`, increment `pageref.count[(PGROUNDDOWN((uint64)pa) - KERNBASE) / PGSIZE]`, release lock.
   * In `kfree(void *pa)`: acquire `pageref.lock`, decrement ref count; if ref count `> 0`, release lock and return immediately without freeing! Only when ref count reaches `0` do you `memset(pa, 1, PGSIZE)` and push `pa` onto `kmem.freelist`.
4. `kernel/vm.c` **[15 Marks — `uvmcopy` & 10 Marks — `copyout`]**:
   * **In `uvmcopy(pagetable_t old, pagetable_t new, uint64 sz)`:**
     * Instead of calling `kalloc()` and `memmove()`, inspect `flags = PTE_FLAGS(*pte)`.
     * If `flags & PTE_W`: clear `PTE_W` and set `PTE_COW` in both `*pte` (parent's PTE) and `flags` (child's PTE):
       ```c
       if (flags & PTE_W) {
         flags = (flags & ~PTE_W) | PTE_COW;
         *pte = (*pte & ~PTE_W) | PTE_COW;
       }
       ```
     * Map the existing physical page `pa` into `new` with `mappages(new, i, PGSIZE, pa, flags)`.
     * Call `krefinc((void *)pa)` to increment the reference count.
   * **CoW Fault Resolution Helper (used by both `usertrap` and `copyout`):**
     * Write a clean helper `int cowfault(pagetable_t pagetable, uint64 va)` (or integrate with `vmfault`):
       * Check `va < MAXVA`, look up `pte = walk(pagetable, va, 0)`.
       * Verify `pte != 0`, `(*pte & PTE_V)`, `(*pte & PTE_U)`, and `(*pte & PTE_COW)`.
       * Allocate new page `char *mem = kalloc()`. If `mem == 0`, return `-1` (out of memory).
       * Copy `memmove(mem, (char *)PTE2PA(*pte), PGSIZE)`.
       * Update `*pte = PA2PTE(mem) | ((PTE_FLAGS(*pte) & ~PTE_COW) | PTE_W)`.
       * Call `kfree((void *)old_pa)` to decrement the old physical page's reference count.
   * **In `copyout()`:**
     * At lines 362–365 of `kernel/vm.c`, right before checking `if ((*pte & PTE_W) == 0)`, check if `(*pte & PTE_COW) != 0`. If so, trigger CoW page duplication so `pa0` and `pte` point to the newly allocated writable page!
5. `kernel/trap.c` **[15 Marks — `usertrap` Page Fault Handling]**:
   * At lines 71–74 of `kernel/trap.c`, when `r_scause() == 15` (store/AMO page fault), check if the fault address `r_stval()` is a mapped CoW page (`cowfault(p->pagetable, r_stval()) == 0`), while still preserving the existing `vmfault()` call for lazy `sbrk` pages! If out of memory on a CoW fault, `setkilled(p)`.

---

### Part B: Process Alarms (`sigalarm` & `sigreturn`) [40 Marks]

#### Exact Files Modified in `mp2_boilerplate/xv6`:
1. `kernel/proc.h` **[10 Marks — Process State]**:
   * Add alarm fields to `struct proc`:
     ```c
     int alarm_ticks;                // Alarm period in ticks (0 if disabled)
     uint64 alarm_handler;           // User virtual address of handler function
     int alarm_ticks_left;           // Ticks remaining until next alarm call
     int alarm_active;               // 1 if currently executing inside handler, 0 otherwise
     struct trapframe *alarm_tf;     // Saved trapframe from before handler started
     ```
2. `kernel/proc.c` **[Part of 10 Marks — Initialization & Cleanup]**:
   * In `allocproc()`: allocate `p->alarm_tf = (struct trapframe *)kalloc()` (or use an embedded `struct trapframe alarm_tf` inside `struct proc` to avoid extra `kalloc` failure paths), and initialize `alarm_ticks = 0`, `alarm_handler = 0`, `alarm_ticks_left = 0`, `alarm_active = 0`.
   * In `freeproc()`: reset all alarm fields to `0` (and `kfree(p->alarm_tf)` if dynamically allocated).
3. `kernel/sysproc.c` **[15 Marks — `sys_sigalarm` & `sys_sigreturn`]**:
   * Fill in the existing `TODO(mini-project 2)` stubs at lines 117–130 of `kernel/sysproc.c`:
     * **`sys_sigalarm(void)`:**
       * Fetch `int ticks` (`argint(0, &ticks)`) and `uint64 handler` (`argaddr(1, &handler)`).
       * If `ticks < 0`, return `-1`.
       * Set `p->alarm_ticks = ticks`, `p->alarm_handler = handler`, `p->alarm_ticks_left = ticks`, and return `0`.
     * **`sys_sigreturn(void)`:**
       * Restore `*(p->trapframe) = *(p->alarm_tf)` (if `p->alarm_active` or unconditionally when called by handler).
       * Clear `p->alarm_active = 0`.
       * **Crucial (`test3` in `alarmtest.c`):** Return `p->trapframe->a0`! Why? Because `syscall()` in `kernel/syscall.c` executes `p->trapframe->a0 = syscalls[num]();`. Returning `p->trapframe->a0` ensures `a0` is written back with its original pre-interrupt value.
4. `kernel/trap.c` **[15 Marks — Timer Interrupt in `usertrap`]**:
   * In `usertrap()`, inside the `if (which_dev == 2)` block (timer interrupt from user space):
     * Check `if (p->alarm_ticks > 0 && p->alarm_active == 0)`:
       * Decrement `p->alarm_ticks_left--` (or increment elapsed ticks).
       * When `p->alarm_ticks_left == 0`:
         * Reset `p->alarm_ticks_left = p->alarm_ticks` (for periodic execution).
         * Set `p->alarm_active = 1` (prevents re-entrant calls tested by `test2`).
         * Save `*(p->alarm_tf) = *(p->trapframe)`.
         * Redirect user PC: `p->trapframe->epc = p->alarm_handler`.

---

## 6. Step-by-Step Checkpoint & Git Commit Plan (For Authentic Execution & TA Review)

Below is the exact **20-checkpoint sequence** designed so Baani can build, test, commit, and push the project step by step, with full clarity on **what changed**, **why**, **how to test it**, and **what TAs ask in the viva**.

---

### Phase 1: `xv6` — Alarms Branch (`git checkout -b alarms`)
*(We start with Alarms or CoW on separate branches as recommended by the handout.)*

| Checkpoint | Suggested Commit Message | Files Modified | What Is Implemented & Why | How to Test at This Stage | TA Viva / Review Focus |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **CP 1** | `xv6: add alarm state fields to struct proc` | `xv6/kernel/proc.h`, `xv6/kernel/proc.c` | Add `alarm_ticks`, `alarm_handler`, `alarm_ticks_left`, `alarm_active`, and `alarm_tf` to `struct proc`. Initialize them in `allocproc()` and reset them in `freeproc()`. | `cd xv6 && make kernel/kernel` (verifies clean compilation). | Why do we need `alarm_tf` separate from `p->trapframe`? *(Because the alarm handler runs in user space and may make syscalls like `write`/`printf` that overwrite `p->trapframe`!)* |
| **CP 2** | `xv6: implement sys_sigalarm and sys_sigreturn syscalls` | `xv6/kernel/sysproc.c` | Replace the `-1` stubs in `sys_sigalarm` and `sys_sigreturn`. `sys_sigalarm` validates `ticks >= 0` and stores the alarm config. `sys_sigreturn` restores `*(p->trapframe) = *(p->alarm_tf)`, sets `alarm_active = 0`, and returns `p->trapframe->a0`. | `cd xv6 && make kernel/kernel` | Why does `sys_sigreturn` return `p->trapframe->a0` instead of `0`? *(Because `syscall()` assigns the return value of `sys_sigreturn()` into `p->trapframe->a0`. Returning `0` would clobber user register `a0`, failing `alarmtest` `test3`!)* |
| **CP 3** | `xv6: invoke alarm handler on timer interrupts in usertrap` | `xv6/kernel/trap.c` | In `usertrap()`, when `which_dev == 2`, check `p->alarm_ticks > 0 && !p->alarm_active`. Decrement `alarm_ticks_left`; when `0`, reset counter, save trapframe to `alarm_tf`, set `alarm_active = 1`, and set `p->trapframe->epc = p->alarm_handler`. | Run `./test-xv6.py alarmtest` and `./test-xv6.py -q usertests`. All `test0`, `test1`, `test2`, `test3` must pass! | Why check `p->alarm_ticks > 0` instead of `p->alarm_handler != 0`? *(Because address `0x0` is a valid user code address in `xv6`!)* |

---

### Phase 2: `xv6` — Copy-on-Write Fork Branch (`git checkout main && git checkout -b cow`)

| Checkpoint | Suggested Commit Message | Files Modified | What Is Implemented & Why | How to Test at This Stage | TA Viva / Review Focus |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **CP 4** | `xv6: add physical page reference counting in kalloc` | `xv6/kernel/riscv.h`, `xv6/kernel/defs.h`, `xv6/kernel/kalloc.c` | Define `PTE_COW (1L << 8)` in `riscv.h`. Add `pageref` array + spinlock in `kalloc.c`, `krefinc()`, `krefget()`, and update `kalloc()`/`kfree()` so pages are only freed when ref count hits `0`. | Run `./test-xv6.py -q usertests` to verify normal memory allocation/freeing still works with ref counting. | Why is a spinlock needed around `pageref`? *(Multiple CPUs/harts can `fork()` or `kfree()` shared pages concurrently.)* |
| **CP 5** | `xv6: share parent physical pages as CoW in uvmcopy` | `xv6/kernel/vm.c` | Modify `uvmcopy()` to stop calling `kalloc()`. Clear `PTE_W` and set `PTE_COW` on writable PTEs in both parent and child, map the same `pa`, and call `krefinc((void *)pa)`. | Compile `make kernel/kernel` (will fault on boot until CP 6 handles CoW write faults). | Why must we clear `PTE_W` in the **parent** PTE as well as the child PTE? *(If the parent writes to the page first, the parent must also trigger a page fault so it doesn't corrupt the child's memory!)* |
| **CP 6** | `xv6: handle CoW store page faults in usertrap` | `xv6/kernel/vm.c`, `xv6/kernel/trap.c`, `xv6/kernel/defs.h` | Implement `cowfault(pagetable, va)` to allocate a new page, copy old page data, update PTE with `PTE_W` & clear `PTE_COW`, and `kfree` old page. Call it on store page faults (`r_scause() == 15`) in `usertrap()`. | Boot `make qemu` and run `cowtest` (`simple` and `three` tests will pass!). | How do you distinguish a CoW fault from a write to a read-only code page or lazy `sbrk` page? *(CoW pages are already mapped (`PTE_V`) and have `PTE_COW` set; read-only code pages lack `PTE_COW`; lazy `sbrk` pages have `PTE_V == 0`.)* |
| **CP 7** | `xv6: handle CoW pages in copyout` | `xv6/kernel/vm.c` | In `copyout()`, before rejecting non-`PTE_W` pages, check if `*pte & PTE_COW` is set and invoke `cowfault()` so kernel-to-user writes (`read()`, `pipe()`, `wait()`) duplicate CoW pages properly. | Run `./test-xv6.py cowtest` (`simple`, `three`, `file` all pass!) and `./test-xv6.py -q usertests`. | Why doesn't `copyout()` trigger a hardware page fault automatically? *(Because `copyout()` walks the user page table in software and writes directly via the kernel's direct-mapped physical address!)* |
| **CP 8** | `xv6: rebase cow and alarms branches and format code` | `xv6/*` | Rebase `alarms` and `cow` onto your main branch (`git rebase`), run `make fmt`, and verify both `./test-xv6.py cowtest`, `./test-xv6.py alarmtest`, and `./test-xv6.py -q usertests` pass together. | Run all 3 `test-xv6.py` suites back-to-back. | How do CoW page faults and timer interrupts coexist in `usertrap`? *(Timer interrupts have `which_dev == 2`, whereas store page faults have `r_scause() == 15`.)* |

---

### Phase 3: `networking/tempest` — HTTP/1.1 Weather Client

| Checkpoint | Suggested Commit Message | Files Modified | What Is Implemented & Why | How to Test at This Stage | TA Viva / Review Focus |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **CP 9** | `tempest: parse CLI arguments and implement URL encoding` | `networking/tempest/tempest.h`, `networking/tempest/url.c`, `networking/tempest/main.c` | Parse `<city_name>` and optional trailing `--raw`. Print `tempest: too many arguments` on extra args. Implement RFC 3986 percent-encoding for `<city_name>`. | Compile with `make` in `networking/tempest`; test `./tempest a b` $\rightarrow$ `tempest: too many arguments`. | Why must spaces in `"New York"` be encoded as `%20`? *(HTTP request targets cannot contain raw spaces; a space would prematurely end the request-target field in `GET /New York?0T HTTP/1.1`.)* |
| **CP 10** | `tempest: implement TCP connection and HTTP GET request with timeout` | `networking/tempest/http.c`, `networking/tempest/tempest.h` | Resolve `wttr.is:80` via `getaddrinfo()`, open TCP socket, configure 10s timeout (`SO_RCVTIMEO`/`SO_SNDTIMEO`), format HTTP/1.1 GET request with `Connection: close`, and send via `send_all()` loop. | Run `./tempest Hyderabad` and verify bytes are received from `wttr.is`. | How does `send_all()` handle short writes? *(It loops while `total_sent < len`, advancing the buffer pointer by `n` bytes returned by each `send()` call.)* |
| **CP 11** | `tempest: parse HTTP status line, headers, and chunked body` | `networking/tempest/http.c`, `networking/tempest/main.c` | Read full response in a loop until EOF, split headers/body at `\r\n\r\n`, decode `Transfer-Encoding: chunked` if present, detect invalid locations (`tempest: invalid location`), and implement `--raw` vs. normal output. | Test `./tempest Hyderabad`, `./tempest "New York"`, `./tempest Rotterdam --raw`, and `./tempest InvalidCityXYZ123`. | What do `Host`, `Connection: close`, `Content-Length`, and `\r\n\r\n` do in HTTP/1.1? |

---

### Phase 4: `networking/mastermind` — Peer-to-Peer LAN Game

| Checkpoint | Suggested Commit Message | Files Modified | What Is Implemented & Why | How to Test at This Stage | TA Viva / Review Focus |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **CP 12** | `mastermind: define protocol constants, structs, and logging utility` | `networking/mastermind/mastermind.h`, `networking/mastermind/log.c` | Define 4-byte magic (`0x4D4D4E44`), message verbs, peer table struct, board state struct, and implement `--log` appending microsecond-timestamped entries to `log.txt`. | Compile with `make` in `networking/mastermind`. | How does `gettimeofday` + `strftime` format microsecond timestamps? |
| **CP 13** | `mastermind: implement UDP broadcast player discovery and peer expiry` | `networking/mastermind/discovery.c`, `networking/mastermind/main.c` | Setup UDP broadcast socket (`SO_BROADCAST`), broadcast `magic + port + name` every 2s, receive peer broadcasts (extracting IP from `recvfrom` source address), expire peers after 5s, and render `Players Online:` table. | Run 2 instances on mobile hotspot (or 2 Docker containers) and watch them appear and expire after 5s when one exits. | Why is the sender's IP taken from `recvfrom()`'s `sockaddr_in` instead of the packet payload? *(A host may have multiple interfaces or spoofed payload data; the IP header's source address is the actual routable LAN address.)* |
| **CP 14** | `mastermind: implement challenge handshake and persistent TCP session` | `networking/mastermind/net_tcp.c`, `networking/mastermind/main.c` | Handle `challenge <ID>` command, open TCP connection to peer's listening port, prompt peer with `yes`/`no`, return to lobby on `no`, or transition to gameplay on `yes`. | Challenge peer `1`, test rejecting (`no`) and accepting (`yes`). | How does `poll()` let the program listen for UDP broadcasts, incoming TCP challenges, and `stdin` commands at the same time without threads? |
| **CP 15** | `mastermind: implement sequence validation, feedback rules, and ANSI board` | `networking/mastermind/game.c` | Validate 5-digit sequences (`0-9`) and 5-char feedback (`x`, `o`, `-`), render the 12-row board with `*****` mask for Codebreaker and ANSI colors (`x` green, `o` yellow, `-` red). | Play turns between Mastermind and Codebreaker; test invalid inputs (e.g., `1234`, `12a45`, `xxz--`). | Why is the `master sequence` kept only on the Mastermind's side until the game ends? |
| **CP 16** | `mastermind: handle game completion and TCP disconnection recovery` | `networking/mastermind/game.c`, `networking/mastermind/net_tcp.c`, `networking/mastermind/main.c` | Detect win (`xxxxx`) or 12 exhausted attempts, send `master sequence` to Codebreaker, close TCP socket, wait for Enter to return to lobby. Detect peer disconnect (`recv == 0`) and show `<Player_name> disconnected. Press enter to go home.` | Play a full game to win/loss, and test `Ctrl+C` mid-game on either player. | How does TCP notify the other end when a process crashes or closes its socket? *(The OS kernel sends a TCP `FIN` or `RST` segment, causing `poll()` to mark the fd readable and `recv()` to return `0` or `-1`.)* |
| **CP 17** | `mastermind: implement chunked UDP state transfer for cost-cutting mode` | `networking/mastermind/net_rudp.c`, `networking/mastermind/mastermind.h` | Implement `--cost-cutting` mode: split outgoing messages into fixed-size `struct rudp_pkt` chunks with `seq_num` and `total_chunks`, transmit without waiting, reorder and reassemble on receiver. | Run `./mastermind --cost-cutting` and verify messages are split into chunks and reassembled in order. | How does the receiver know all chunks of a message have arrived if chunks arrive out of order? *(Each chunk carries `total_chunks` and `seq_num`; the receiver tracks a bitmask/array of received `seq_num`s until `received_count == total_chunks`.)* |
| **CP 18** | `mastermind: add per-chunk ACK, 0.1s retransmission, and UDP disconnect detection` | `networking/mastermind/net_rudp.c`, `networking/mastermind/main.c` | Send `PKT_ACK` per chunk, retransmit any un-ACKed chunk after `0.1s` (100 ms) in the `poll()` loop, and detect UDP peer disconnection via heartbeat/retry timeout. | Test `./mastermind --cost-cutting --log` and inspect `log.txt` to see chunk sends, ACKs, and reassembly. | Why must the sender NOT wait for an ACK before sending the next chunk? *(Stop-and-wait wastes bandwidth; pipelining sends all chunks immediately and only retransmits specific un-ACKed chunks after 0.1s.)* |

---

### Phase 5: Final Documentation & End-to-End Verification

| Checkpoint | Suggested Commit Message | Files Modified | What Is Implemented & Why |
| :---: | :--- | :--- | :--- |
| **CP 19** | `docs: document networking and xv6 implementation details in readme` | `readme.md`, `ai-usage.md` | Fill out every section of `mp2_boilerplate/readme.md` (Tempest design, Mastermind 4-byte magic, message verbs, RUDP chunk struct, TCP & UDP disconnect detection, xv6 CoW locking & PTE bit, xv6 Alarm struct fields & `sigreturn` state) and add any chat links to `ai-usage.md`. |
| **CP 20** | `chore: final build and test verification across networking and xv6` | Any minor cleanups | Verify `cd networking && make clean && make all` compiles with zero warnings/errors, and `cd xv6 && ./test-xv6.py cowtest && ./test-xv6.py alarmtest && ./test-xv6.py -q usertests` passes 100%. |
