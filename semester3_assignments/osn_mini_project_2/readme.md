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
- `tempest.h`: Constants (`wttr.is`, port `80`, 10-second timeout `TEMPEST_TIMEOUT_MS = 10000`) and function declarations.
- `url.c`: Implements URL percent-encoding (`url_encode()`) so multi-word city names or special characters (such as `"New York"` $\rightarrow$ `"New%20York"`) can be safely placed in the HTTP request path.
- `http.c`: Starts a 10-second running timer (`get_time_ms()`) before `connect()`, resolves `wttr.is:80` using `getaddrinfo()`, connects a TCP socket, sends the HTTP/1.1 `GET /<city>?0T HTTP/1.1` request using a `send_all()` loop to handle short writes, and reads the full response until EOF using `poll()` with the remaining timeout to handle short reads. It splits headers from the body at `\r\n\r\n`, parses the HTTP status code from the status line, and checks for invalid locations (`status_code != 200`, `"Unknown location"`, `"location not found"`, or unexpected IP geolocation coordinate fallback). When `--raw` is given, it prints the outgoing HTTP request lines (prefixed with `> `), the incoming response header lines (prefixed with `< `), and the body, exiting with status `1` if the location was invalid.
- `main.c`: Validates CLI arguments (`<city>` and optional trailing `--raw`), printing `tempest: too many arguments` when extra arguments are supplied.

#### Changed defaults

none

#### Assumptions

- `wttr.is` is queried over HTTP/1.1 on port `80` with `User-Agent: curl/8.0` and `Connection: close` (RFC 9112 Section 9.3).
- City names with spaces must be enclosed in quotes on the command line (e.g. `./tempest "New York"`).
- When `--raw` is specified, it takes precedence over printing `tempest: invalid location` (prints the raw HTTP request and response and exits with status `1` on invalid locations).

#### Known bugs

none known

### mastermind

```bash
mastermind [--cost-cutting] [--log]
```

#### Design

`mastermind` is split into seven files under `networking/mastermind/`:
- `mastermind.h`: Defines the 4-byte protocol magic (`MM_MAGIC`), discovery and RUDP constants, `struct chunk_pkt`, `struct peer_entry`, `struct board_state`, and function declarations.
- `log.c`: Implements microsecond-timestamped logging (`write_log()`) appending to `log.txt` when `--log` is enabled using `gettimeofday()` and `strftime()`.
- `discovery.c`: Manages the UDP broadcast socket (`SO_BROADCAST`, port `33301`), packs the 4-byte magic, 2-byte listening port, and 32-byte player name into a 38-byte buffer (`pack_discovery_packet()`), broadcasts every 2 seconds to `255.255.255.255`, extracts the sender's IP from `recvfrom()`'s source address, removes peers not refreshed for 5 seconds, and prints the `Players Online` table.
- `net_tcp.c`: Manages the persistent TCP game connection in normal mode, sending and receiving newline-delimited (`\n`) messages with a receive buffer (`tcp_read_line()`) to handle TCP byte-stream framing and short reads.
- `net_rudp.c`: Implements reliable UDP state transfer for `--cost-cutting` mode. Messages are divided into fixed-size 4-byte chunks (`struct chunk_pkt`), packed into a 20-byte buffer (`pack_chunk()` / `unpack_chunk()`) before `sendto()`, sent immediately without waiting for ACKs, acknowledged per chunk (`PKT_TYPE_ACK`), retransmitted every `0.1 s` (`100 ms`) if unacknowledged, and reordered/reassembled by `seq_num` once all `total_chunks` arrive.
- `game.c`: Validates 5-digit sequences (`0-9`) and 5-character feedback strings (`x`, `o`, `-`), computes expected feedback, and renders the 12-row board (`print_board()`) with ANSI colors (`x` green, `o` yellow, `-` red on the Codebreaker's board) while keeping the `master sequence` hidden (`*****`) on the Codebreaker's board until the game ends.
- `main.c`: Runs a single-threaded `poll()` loop multiplexing `stdin`, the UDP discovery socket, and the TCP/UDP game session socket.

#### Discovery

- **4-byte magic:** `0x4D4D4E44` (`"MMND"` in ASCII), stored in network byte order (`htonl(MM_MAGIC)`). Any UDP packet that does not start with these 4 bytes or is not `38` bytes long (`MM_DISC_PKT_SIZE`) is ignored.
- **Broadcast payload layout (`38` bytes packed via `pack_discovery_packet`):**
  - Bytes `0..3`: `uint32_t magic` = `htonl(0x4D4D4E44)`
  - Bytes `4..5`: `uint16_t port` = `htons(my_game_port)`
  - Bytes `6..37`: `char name[32]` = null-terminated player name
- The sender's IP address is not included in the payload; it is read from `recvfrom()`'s `struct sockaddr_in` using `inet_ntop()`.

#### Message verbs

All game session messages are formatted as `<VERB>[ <payload>]`:
- `CHALLENGE <challenger_name>`: Sent by the challenger (Mastermind) when typing `challenge <ID>`.
- `ACCEPT`: Sent by the challenged player (Codebreaker) when typing `yes`.
- `REJECT`: Sent by the challenged player when typing `no`; both players return to the discovery lobby.
- `READY`: Sent by the Mastermind after locally entering and validating the 5-digit `master sequence`.
- `GUESS <5_digits>`: Sent by the Codebreaker on each turn with their validated 5-digit attempt (`0-9`).
- `FEEDBACK <5_chars>`: Sent by the Mastermind with the validated 5-character feedback (`x`, `o`, `-`).
- `GAMEOVER <master_seq>`: Sent by the Mastermind at the end of the game (when `xxxxx` is reached or after 12 attempts) so the Codebreaker can display the `master sequence` on their board.

#### Reliable transfer over UDP (`--cost-cutting`)

- **Chunk struct (`struct chunk_pkt` in `mastermind.h`) and 20-byte wire buffer (`pack_chunk` / `unpack_chunk`):**
  - Bytes `0..3`: `magic` (`htonl(0x4D4D4E44)`)
  - Bytes `4..5`: `type` (`PKT_TYPE_DATA=1`, `PKT_TYPE_ACK=2`, `PKT_TYPE_PING=3`, `PKT_TYPE_PONG=4`, `PKT_TYPE_FIN=5`)
  - Bytes `6..7`: `msg_id` (message number in network byte order)
  - Bytes `8..9`: `seq_num` (chunk index `0 .. total_chunks - 1` in network byte order)
  - Bytes `10..11`: `total_chunks` (total chunks in the message in network byte order)
  - Bytes `12..13`: `data_len` (number of valid bytes in `data[]`)
  - Bytes `14..15`: unused/zero bytes
  - Bytes `16..19`: `char data[4]` (`MM_CHUNK_DATA_SIZE = 4` bytes of text)
- **Sequence numbering & total chunk count:** A text message of length $L$ is split into $\lceil L / 4 \rceil$ chunks with `seq_num` from `0` to `total_chunks - 1`.
- **Pipelined send, per-chunk ACK, and 0.1 s retransmission:** `rudp_send_message()` sends all chunks of a message immediately without waiting for ACKs. For every `PKT_TYPE_DATA` chunk received, `rudp_handle_incoming()` sends a `PKT_TYPE_ACK` referencing `(msg_id, seq_num)` and stores the chunk at index `seq_num`. Once `received_count == total_chunks`, the chunks are concatenated in `seq_num` order (`0 .. total_chunks - 1`). Every 25 ms in the `poll()` loop, `rudp_check_timers()` checks all unacknowledged chunks and retransmits any chunk where `now - last_sent_ms >= 100` ms (`0.1 s`).

#### Disconnection handling

- **TCP:** Detected when `poll()` reports activity on `tcp.fd` and `recv()` returns `0` (EOF when the peer closes the connection) or `-1` on error. The TCP socket is closed and `<Player_name> disconnected. Press enter to go home.` is printed.
- **UDP:** Detected in `--cost-cutting` mode when: (1) a `PKT_TYPE_FIN` packet is received on peer exit, (2) a chunk exceeds 35 retransmission attempts without receiving an ACK, or (3) no UDP packet (including periodic `PKT_TYPE_PING` / `PKT_TYPE_PONG` heartbeats sent every 1.5 seconds) is received from the peer for 5 seconds (`MM_UDP_TIMEOUT_MS`). When detected, `<Player_name> disconnected. Press enter to go home.` is printed.

#### Changed defaults

none

#### Assumptions

- Discovery broadcasts are sent on UDP port `33301` (`MM_DISCOVERY_PORT`) to `255.255.255.255` every 2 seconds, and peers expire after 5 seconds without a broadcast.
- Testing is performed between two laptops connected to the same personal mobile hotspot.

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

- **Reference counts & locking (`kernel/kalloc.c`):** Physical page reference counts are stored in `pageref.count[(PHYSTOP - KERNBASE) / PGSIZE]`, indexed by `PA2IDX(pa) = ((uint64)pa - KERNBASE) / PGSIZE` and protected by `struct spinlock pageref.lock`. `kalloc()` sets a newly allocated page's reference count to `1`, `krefinc(pa)` increments the count when `uvmcopy()` shares a page, and `kfree(pa)` decrements the count under `pageref.lock`, only freeing the physical page into `kmem.freelist` when the count reaches `0`.
- **CoW PTE bit (`kernel/riscv.h`):** Bit 8 of the RISC-V Sv39 PTE (one of the supervisor software RSW bits) is defined as `#define PTE_COW (1L << 8)`. In `uvmcopy()`, writable user pages have `PTE_W` cleared and `PTE_COW` set in both the parent's and child's PTEs, mapping the same physical page.
- **Write fault duplication (`kernel/vm.c`, `kernel/trap.c`):** When user space writes to a CoW page, the CPU raises a store page fault (`r_scause() == 15`). `usertrap()` calls `cowfault(p->pagetable, r_stval())`. If the page's reference count is `1` (`krefcnt(pa) == 1`), `cowfault()` restores `PTE_W` and clears `PTE_COW` in-place; otherwise it allocates a new page with `kalloc()`, copies the 4096 bytes with `memmove()`, updates the PTE to point to the new page with `PTE_W` set and `PTE_COW` cleared, and calls `kfree()` on the old physical page. `copyout()` also checks `*pte & PTE_COW` and calls `cowfault()` before writing to user memory.

### Alarms

- **`struct proc` fields (`kernel/proc.h`, `kernel/proc.c`):** Added `int alarm_ticks` (alarm period in ticks), `uint64 alarm_handler` (user virtual address of the handler), `int alarm_ticks_left` (ticks remaining until next call), `int alarm_active` (`1` while the handler is currently running), and `struct trapframe *alarm_tf` (allocated in `allocproc()` and freed in `freeproc()` to save the interrupted trapframe).
- **State restored by `sigreturn` (`kernel/sysproc.c`):** When the handler calls `sigreturn()`, `sys_sigreturn()` restores `*(p->trapframe) = *(p->alarm_tf)`, sets `p->alarm_active = 0`, and returns `p->trapframe->a0` so register `a0` and all other saved user registers and `epc` are restored.
- **Preventing handler re-entry (`kernel/trap.c`):** On a timer interrupt (`which_dev == 2`) in `usertrap()`, the kernel only decrements `p->alarm_ticks_left` and triggers the alarm when `p->alarm_ticks > 0 && p->alarm_active == 0`. Setting `p->alarm_active = 1` before jumping to `p->alarm_handler` prevents re-entrant calls until `sigreturn()` resets `p->alarm_active = 0`.

### Assumptions

- If `cowfault()` cannot allocate a new physical page (`kalloc() == 0`), it returns `-1` and `usertrap()` terminates the process via `setkilled(p)`.

### Known bugs

none known
