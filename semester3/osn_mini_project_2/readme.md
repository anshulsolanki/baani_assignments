# Mini Project 2

Mini-project 2 from CS3.301 Operating Systems and Networks, Monsoon 2026

## networking

### Build

```bash
cd networking
make all      # builds tempest/tempest and mastermind/mastermind
make clean
```

### tempest

```bash
tempest <city>
tempest <city> --raw
```

#### Design

`tempest` is split into four files under `networking/tempest/`:
- `tempest.h`: Constants (`wttr.is`, port `80`, 10-second socket timeout) and function declarations.
- `url.c`: Implements RFC 3986 percent-encoding (`url_encode()`) so multi-word city names or special characters (such as `"New York"` $\rightarrow$ `"New%20York"`) can be safely placed in the HTTP request target.
- `http.c`: Resolves `wttr.is:80` using `getaddrinfo()`, connects a TCP socket with a 10-second timeout (`SO_RCVTIMEO` and `SO_SNDTIMEO`), sends the HTTP/1.1 `GET /<city>?0T HTTP/1.1` request using a `send_all()` loop to handle short writes, and reads the full response until EOF in `recv_all()` (since `Connection: close` is sent in the request headers). It splits the status line and headers from the body at `\r\n\r\n`, decodes `Transfer-Encoding: chunked` if present (`decode_chunked()`), and detects invalid locations (`is_invalid_location()`) by checking if the HTTP status code is `404`/`400` or if the response body contains `"Unknown location"` / `"not found"`, printing `tempest: invalid location`.
- `main.c`: Validates CLI arguments (`<city>` and optional trailing `--raw`), printing `tempest: too many arguments` when extra arguments are supplied.

#### Changed defaults

none

#### Assumptions

- `wttr.is` is queried over plain HTTP/1.1 on port `80` with `User-Agent: curl/8.0` so the server returns the compact plain-text ASCII weather report (`?0T`).
- If `--raw` is supplied, it must be the last argument after `<city>`.

#### Known bugs

none known

### mastermind

```bash
mastermind [--cost-cutting] [--log]
```

#### Design

`mastermind` is split into seven files under `networking/mastermind/`:
- `mastermind.h`: Defines the 4-byte protocol magic (`MM_MAGIC`), discovery & RUDP packet structs, message verb constants, game board state, and module prototypes.
- `log.c`: Implements microsecond-timestamped logging (`gettimeofday()` + `strftime()`) to `log.txt` when `--log` is enabled, plus `now_ms()` for protocol timers.
- `discovery.c`: Manages the UDP broadcast socket (`SO_BROADCAST`, port `33301`), transmits discovery broadcasts every 2 seconds, validates incoming broadcast packets against the 4-byte magic, extracts the sender's IP from `recvfrom()`'s source address, expires peers unseen for 5 seconds, and renders the `Players Online` lobby table.
- `net_tcp.c`: Manages the persistent TCP game connection in normal mode, sending and receiving newline-delimited (`\n`) messages with a per-connection receive buffer (`tcp_recv_line()`) to handle TCP byte-stream framing and short reads.
- `net_rudp.c`: Implements reliable UDP message transfer for `--cost-cutting` mode, splitting messages into fixed-size `struct rudp_pkt` chunks (`MM_CHUNK_DATA_SIZE = 4` bytes), sending all chunks immediately without waiting for ACKs, sending per-chunk `RUDP_PKT_ACK` packets on receipt, retransmitting unacknowledged chunks every `0.1 s` (`100 ms`), reassembling out-of-order chunks by `seq_num`, and monitoring UDP peer liveness via periodic `PING`/`PONG` and `FIN` packets.
- `game.c`: Validates 5-digit sequences (`0-9`) and 5-character feedback strings (`x`, `o`, `-`), computes expected feedback according to the Mastermind rules, and renders the 12-row board with ANSI colors (`x` green, `o` yellow, `-` red) while keeping the `master sequence` masked (`* * * * *`) on the Codebreaker's screen until the game ends.
- `main.c`: Runs a non-blocking `poll()` event loop multiplexing `stdin`, the UDP discovery socket, and the active TCP/UDP game session socket.

#### Discovery

- **4-byte magic:** `0x4D4D4E44` (`"MMND"` in ASCII), stored in network byte order (`htonl(MM_MAGIC)`). Any UDP broadcast packet that does not start with these 4 bytes or does not match `sizeof(struct discovery_pkt)` is ignored.
- **Broadcast payload layout (`struct discovery_pkt`):**
  - `uint32_t magic`: `htonl(0x4D4D4E44)` (4 bytes)
  - `uint16_t listen_port`: `htons(my_game_port)` (2 bytes)
  - `char name[32]`: Null-terminated player name (32 bytes)
- The sender's IPv4 address is never included in the broadcast payload; it is extracted from the `struct sockaddr_in` populated by `recvfrom()` via `inet_ntop()`.

#### Message verbs

All session messages (defined in `mastermind.h`) are formatted as `<VERB>[ <payload>]`:
- `CHALLENGE <challenger_name>`: Sent by the initiator (Mastermind) when running `challenge <ID>` to invite peer `<ID>` to a game.
- `ACCEPT`: Sent by the challenged player (Codebreaker) when typing `yes` to accept the challenge.
- `REJECT`: Sent by the challenged player when typing `no` to decline the challenge; both players return to the discovery lobby.
- `READY`: Sent by the Mastermind after locally entering and validating the 5-digit secret `master sequence` (the sequence itself is not sent).
- `GUESS <5_digits>`: Sent by the Codebreaker on each turn with their validated 5-digit attempt (`0-9`).
- `FEEDBACK <5_chars>`: Sent by the Mastermind after validating the 5-character feedback (`x`, `o`, `-`) for the current attempt.
- `GAMEOVER <master_seq>`: Sent by the Mastermind immediately after the final `FEEDBACK` when the Codebreaker guesses `xxxxx` or exhausts all 12 attempts, revealing the secret sequence so the Codebreaker can display it before returning to the lobby.
- `DISCONNECT`: Sent if a player cleanly exits mid-session.

#### Reliable transfer over UDP (`--cost-cutting`)

- **Chunk struct (`struct rudp_pkt` in `mastermind.h`):**
  - `uint32_t magic`: `htonl(0x4D4D4E44)`
  - `uint8_t type`: `RUDP_PKT_DATA (1)`, `RUDP_PKT_ACK (2)`, `RUDP_PKT_PING (3)`, `RUDP_PKT_PONG (4)`, or `RUDP_PKT_FIN (5)`
  - `uint8_t reserved`: Padding byte
  - `uint16_t msg_id`: Monotonically increasing message identifier (`htons`)
  - `uint16_t seq_num`: 0-indexed chunk sequence number `0 .. total_chunks - 1` (`htons`)
  - `uint16_t total_chunks`: Total number of chunks in `msg_id` (`htons`)
  - `uint16_t data_len`: Number of valid payload bytes in `data[]` (`htons`)
  - `char data[4]`: Fixed 4-byte chunk payload (`MM_CHUNK_DATA_SIZE = 4`)
- **Sequence numbering & total chunk count:** Each outgoing message of length $L$ is split into $\lceil L / 4 \rceil$ chunks numbered `seq_num = 0` through `total_chunks - 1`. Every chunk header carries both `seq_num` and `total_chunks`.
- **Pipelined send, per-chunk ACK, and 0.1 s retransmission:** `rudp_send_msg()` transmits all chunks of a message back-to-back without waiting for ACKs. For every `RUDP_PKT_DATA` chunk received, `rudp_recv_packet()` immediately replies with an `RUDP_PKT_ACK` carrying `(msg_id, seq_num, total_chunks)` and stores the chunk payload at index `seq_num` in the reassembly slot. Even if chunks arrive out of order, once `received_count == total_chunks`, the message is reassembled in `0 .. total_chunks - 1` order and delivered to the game state machine. Meanwhile, `rudp_tick()` runs every 25 ms in the `poll()` loop and retransmits any unacknowledged chunk whose elapsed time since `last_sent_ms` is $\ge 100\text{ ms}$ (`0.1 s`).

#### Disconnection handling

- **TCP:** Detected when `poll()` reports `POLLIN | POLLHUP | POLLERR` and `recv()` returns `0` (EOF from TCP `FIN`) or `-1` (`ECONNRESET`), or when `VERB_DISCONNECT` is received. The active TCP socket is closed and `<Player_name> disconnected. Press enter to go home.` is displayed.
- **UDP:** Detected in `--cost-cutting` mode via three mechanisms: (1) receiving an explicit `RUDP_PKT_FIN` packet on peer exit, (2) exceeding the chunk retransmission retry limit when a peer stops acknowledging chunks, or (3) a 5-second inactivity timeout (`MM_RUDP_TIMEOUT_MS`) monitored by periodic `RUDP_PKT_PING` / `RUDP_PKT_PONG` heartbeats sent every 1.5 seconds. Upon detection, `<Player_name> disconnected. Press enter to go home.` is displayed.

#### Changed defaults

none

#### Assumptions

- Discovery uses UDP port `33301` (`MM_DISCOVERY_PORT`) and broadcasts to `255.255.255.255` (overridable via `MM_BROADCAST_IP` for custom subnet broadcast testing).
- Each player binds an ephemeral port (`htons(0)`) for their TCP/RUDP game session and advertises that port in their discovery broadcast payload.

#### Known bugs

none known

## xv6

### Build

```bash
cd xv6
make qemu     # boot xv6; Ctrl-A X to quit
make clean
```

### Run

```bash
# in the xv6 shell
cowtest
alarmtest
usertests -q

# or from outside
./test-xv6.py cowtest
./test-xv6.py alarmtest
./test-xv6.py -q usertests
```

### Copy-on-write fork

- **Reference counts & locking (`kernel/kalloc.c`):** Physical page reference counts are stored in `pageref.count[(PHYSTOP - KERNBASE) / PGSIZE]`, indexed by `PA2IDX(pa) = ((uint64)pa - KERNBASE) / PGSIZE` and protected by `struct spinlock pageref.lock`. `kalloc()` initializes a newly allocated page's reference count to `1`, `krefinc(pa)` increments the count when a page is shared in `uvmcopy()`, and `kfree(pa)` decrements the count under `pageref.lock`, only returning the page to `kmem.freelist` when its reference count reaches `0`.
- **CoW PTE bit (`kernel/riscv.h`):** Bit 8 of the RISC-V Sv39 PTE (one of the supervisor software RSW bits) is defined as `#define PTE_COW (1L << 8)`. In `uvmcopy()`, writable user pages have `PTE_W` cleared and `PTE_COW` set in both the parent's and child's PTEs, and both page tables map the same physical address.
- **Write fault duplication (`kernel/vm.c`, `kernel/trap.c`):** When user space attempts to write to a CoW page, the CPU raises a store page fault (`r_scause() == 15`). `usertrap()` calls `cowfault(p->pagetable, r_stval())` before falling back to lazy-allocation `vmfault()`. `cowfault()` verifies that the faulting virtual address is `< MAXVA` and mapped with `PTE_V | PTE_U | PTE_COW`, allocates a new page with `kalloc()`, copies the 4096-byte page contents via `memmove()`, updates the PTE to point to the new physical page with `PTE_W` restored and `PTE_COW` cleared, and calls `kfree()` on the old physical address to decrement its reference count. `copyout()` also checks `*pte & PTE_COW` and calls `cowfault()` before writing from the kernel to user memory.

### Alarms

- **`struct proc` fields (`kernel/proc.h`, `kernel/proc.c`):** Added `int alarm_ticks` (alarm interval in ticks), `uint64 alarm_handler` (user virtual address of the handler function), `int alarm_ticks_left` (ticks remaining until next invocation), `int alarm_active` (non-zero while executing inside the alarm handler), and `struct trapframe *alarm_tf` (allocated in `allocproc()` and freed in `freeproc()` to hold a copy of the interrupted user trapframe).
- **State restored by `sigreturn` (`kernel/sysproc.c`):** When the user handler finishes and calls `sigreturn()`, `sys_sigreturn()` copies the saved trapframe back into the active trapframe (`*(p->trapframe) = *(p->alarm_tf)`), clears `p->alarm_active = 0`, and returns `p->trapframe->a0` so that `syscall()` restores the original value of register `a0` along with all other user registers and `epc`.
- **Preventing handler re-entry (`kernel/trap.c`):** In `usertrap()`, when a timer interrupt occurs (`which_dev == 2`), the kernel only decrements `p->alarm_ticks_left` and invokes the handler if `p->alarm_ticks > 0 && p->alarm_active == 0`. Before redirecting `p->trapframe->epc = p->alarm_handler`, the kernel sets `p->alarm_active = 1`, which prevents another alarm handler invocation until the running handler calls `sigreturn()`.

### Assumptions

- If `cowfault()` fails to allocate a physical page due to memory exhaustion (`kalloc() == 0`), `cowfault()` returns `-1` and `usertrap()` marks the faulting process as killed (`setkilled(p)`).

### Known bugs

none known
