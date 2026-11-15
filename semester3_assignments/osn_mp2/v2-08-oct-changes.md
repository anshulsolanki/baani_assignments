# CS3.301 OSN Mini Project 2 — Summary of Changes (v2 — 08 Oct)

This document details all code and documentation updates made in response to your 5 feedback points, including a full requirement check against the official assignment specification (`https://cs3301.pages.dev/assignments/02`) and the official CS3.301 TA Doubt Document (`https://hackmd.io/@m26-osn/S1qenn-tzg`), plus the complete guide on how `mastermind` is built for 2 laptops and how to run and test it across 2 laptops.

---

## 1. Strictly Written in C Only

* **Removed** the Python test script (`semester3/osn_mp2/test_mp2.py`).
* Every file in the project (`networking/tempest/*.c`, `networking/mastermind/*.c`, and `xv6/kernel/*.c`) is **100% pure C**.

---

## 2. Rewritten in Basic, Straightforward 2nd-Year Undergraduate C

All files in `networking/tempest/` and `networking/mastermind/` have been rewritten so they use simple, step-by-step C that a 2nd-year undergraduate student learning from Beej's Guide to Network Programming would naturally write:

* **Removed all "fancy" / compact / professional C constructs:**
  1. **No `nullptr`:** Replaced all C23 `nullptr` keywords with standard `NULL`.
  2. **No variadic `va_list` / `va_start` logger:** `networking/mastermind/log.c` now uses the **exact** `gettimeofday()` + `strftime()` code snippet and variable names (`tv`, `tm_info`, `buffer`) provided in the assignment handout.
  3. **No `__attribute__((packed))` compiler extensions:** Instead of compiler-packed structs, `discovery.c` (`pack_discovery_packet` / `unpack_discovery_packet`) and `net_rudp.c` (`pack_chunk` / `unpack_chunk`) explicitly copy fields into fixed-size byte buffers (`char buf[38]` and `unsigned char buf[20]`) using `memcpy`, `htonl`/`ntohl`, and `htons`/`ntohs`. This also directly follows **TA Tatva (`[TA]`)'s recommendation in Question 27 of the official TA Doubt Doc**.
  4. **Simple character-by-character TCP line reader:** Replaced the buffered ring-reader in `net_tcp.c` with a straightforward `while` loop calling `recv(fd, &c, 1, 0)` one character at a time until `'\n'` is read (`tcp_recv_line()`).
  5. **No `getenv()` test hooks:** Removed all `getenv()` environment-variable overrides from `discovery.c` and `main.c`.
  6. **Simple `for` loops and clear variable names:** Used plain `for` loops, `strcmp`, `strncmp`, `strstr`, `sscanf`, and `snprintf` throughout `url.c`, `http.c`, `game.c`, `discovery.c`, `net_tcp.c`, `net_rudp.c`, and `main.c`.

---

## 3. Verification of Every Requirement & Official TA Doubt Doc Clarifications

Every requirement from the live assignment page (`https://cs3301.pages.dev/assignments/02`) and all **27 questions in the Official CS3.301 TA Doubt Doc** (`https://hackmd.io/@m26-osn/S1qenn-tzg`) has been verified:

| Component & Requirement | Official Spec / TA Doubt Doc Reference | Verification in Code |
| :--- | :--- | :--- |
| **`tempest`: CLI Arguments** | `./tempest <city_name> [--raw]`; if `> 1` city arg (excluding `--raw`), print `tempest: too many arguments` and exit `1`. | Verified in `networking/tempest/main.c`. |
| **`tempest`: URL Encoding** | Percent-encode spaces (`%20`) and special characters before building the HTTP `GET /<city>?0T` path. | Verified in `networking/tempest/url.c` (`url_encode()`). |
| **`tempest`: 10-Second Application Timeout** | **TA Doubt Doc Q3, Q5, Q13, Q15:** Timeout must be 10 seconds total at the application level starting **before `connect()`**, using `poll()` with the remaining time reduced after each read (`remaining = 10000 - (get_time_ms() - start_ms)`). Print `tempest: connection timed out` on expiry. | Verified in `networking/tempest/http.c` (`get_time_ms()`, `recv_all_with_timeout()`). |
| **`tempest`: Content-Length / Body Handling** | **TA Doubt Doc Q9:** TA Gautam (`[GB]`) confirmed `wttr.is` does not use chunked transfer encoding and handling normal response bodies suffices. | Verified in `networking/tempest/http.c` (removed unnecessary `decode_chunked()`). |
| **`tempest`: `--raw` Precedence** | **TA Doubt Doc Q12, Q16, Q17, Q23:** `--raw` prints outgoing request lines with `> `, incoming response header lines with `< `, then a blank line and the body. If both `--raw` and an invalid location are given, `--raw` output takes precedence and exits with `1`. | Verified in `networking/tempest/http.c` (`print_prefixed_lines()`, `fetch_weather()`). |
| **`tempest`: Invalid Location Detection** | **TA Doubt Doc Q6, Q7:** Print `tempest: invalid location` and exit with `1`. | Verified in `networking/tempest/http.c` (`check_invalid_location()`). |
| **`mastermind`: UDP Broadcast Discovery** | **TA Doubt Doc Q1:** Broadcast every **2 seconds** to `255.255.255.255` (`INADDR_BROADCAST`) on UDP port `33301` with a 4-byte protocol magic (`0x4D4D4E44`), TCP/RUDP port, and player name. Extract sender IP from `recvfrom()`'s `struct sockaddr_in`. Expire peers after **5 seconds**. | Verified in `networking/mastermind/discovery.c`. |
| **`mastermind`: Challenge & Persistent TCP** | `challenge <ID>` connects via TCP, sends `CHALLENGE <name>`, target prompts `Accept? (yes/no):`. Challenger = Codebreaker, Challenged = Mastermind. Single persistent TCP connection for the entire game. | Verified in `networking/mastermind/net_tcp.c` and `main.c`. |
| **`mastermind`: 12-Row Board & ANSI Colors** | **TA Doubt Doc Q10:** TA Tatva (`[TA]`) confirmed the board should match the assignment handout format with all 12 rounds shown (`*****  *****` for remaining rounds), `*****` hidden on top for Codebreaker until game over, and ANSI colors (`x` Green, `o` Yellow, `-` Red). | Verified in `networking/mastermind/game.c` (`print_board()`). |
| **`mastermind`: Master Sequence Privacy** | Secret 5-digit sequence (`0-9`, repeats allowed) stays strictly on the Mastermind's machine during gameplay and is only sent in `GAMEOVER <seq>` after win (`xxxxx`) or 12 failed attempts. | Verified in `networking/mastermind/main.c`. |
| **`mastermind`: Disconnection Handling** | Detect mid-game disconnect in both TCP (`recv() == 0`) and UDP (`PKT_FIN`, retry exhaustion, or 5s heartbeat timeout) and print `<Player_name> disconnected. Press enter to go home.` | Verified in `networking/mastermind/main.c` and `net_rudp.c`. |
| **`mastermind`: `--cost-cutting` Mode** | **TA Doubt Doc Q27:** Pack chunk struct fields into a byte buffer (`20` bytes total, `4` data bytes per chunk), pipeline all chunks without waiting, send per-chunk `PKT_ACK`, retransmit unACKed chunks after **0.1 seconds** (`100 ms`), and reassemble out-of-order chunks by `seq_num`. | Verified in `networking/mastermind/net_rudp.c`. |
| **`mastermind`: `--log` Flag** | Log network/protocol events to `log.txt` with microsecond timestamps using `gettimeofday()` + `strftime()`. | Verified in `networking/mastermind/log.c`. |
| **`xv6`: Process Alarms (`sigalarm` / `sigreturn`)** | Save/restore full trapframe (`p->alarm_tf`), prevent re-entrancy (`p->alarm_active`), preserve `a0` across `sigreturn()`. Pass `alarmtest` (`test0`–`test3`) and `usertests`. | Verified in `xv6/kernel/{proc.h,proc.c,sysproc.c,trap.c}`. |
| **`xv6`: Copy-on-Write (`cow`) Fork** | Share parent physical pages read-only with `PTE_COW` (`1L << 8`), reference-count physical pages in `kalloc.c`, copy on store page fault (`r_scause() == 15`) and in `copyout()`. Pass `cowtest` and `usertests`. | Verified in `xv6/kernel/{riscv.h,defs.h,kalloc.c,vm.c,trap.c}`. |

---

## 4. In `tempest`: Weather Differences vs. Google & Non-Existent Location Fix

### 4.1 Why `wttr.is` Weather Differs from Google Weather
* The assignment strictly requires querying **only** `http://wttr.is/<city>?0T` over plain HTTP on port 80 (`tempest` is not allowed to query Google or HTTPS APIs).
* `wttr.is` is a custom server hosted by the course staff, and its backend weather data feed differs from live Google Weather.
* You can verify that `./tempest <city>` matches `curl -s "http://wttr.is/<city>?0T"` character-for-character.

### 4.2 Why Non-Existent Locations Were Showing Weather & How It Was Fixed
1. **What was wrong in our earlier code:**
   * Previously, our code only checked `if (status_code == 404 || status_code == 400)`.
   * However, when `wttr.is` fails to look up invalid cities such as `notarealcity`, `invalidcity`, `iiith`, `xyzabc123`, or `qwertyuiop`, the `wttr.is` server actually returns **`HTTP/1.1 500 Internal Server Error`** (or falls back to raw latitude/longitude coordinates like `Weather report: 21.997400,79.001100`)!
   * Because our old code only checked `404` and `400`, it did not flag `500` responses or coordinate fallbacks as invalid locations.
2. **How `check_invalid_location()` in `networking/tempest/http.c` works now:**
   * Flags **any** HTTP response where `status_code != 200` (catching `500`, `502`, `404`, `400`, etc.).
   * Flags any response body containing `"Unknown location"`, `"location not found"`, `"not found"`, `"Sorry"`, or `"ERROR"`.
   * Flags any response body that does not start with `"Weather report:"`.
   * Flags any input that has no alphanumeric characters (`A-Z`, `a-z`, `0-9`).
   * Flags any response where `wttr.is` fell back to raw GPS coordinates (`Weather report: <lat>,<lon>`).
3. **Official TA Clarification (Doubt Doc Q7) to Keep in Mind:**
   * In the official CS3.301 Doubt Doc (`https://hackmd.io/@m26-osn/S1qenn-tzg`), a student asked about `wttr.is` returning `200 OK` on certain made-up strings (like `noSuchCity`) where `wttr.is`'s own database fuzzy-matches a real place:
     > **Q7:** *"The server `wttr.is` in some cases does not detect that a city does not exist, for eg. I tried `noSuchCity` and it gave the weather report with `200 OK`, so how then should we detect invalid locations? Based on servers response not being 200?"*  
     > **TA Advait (`[AD]`) Answer:** *"Use the HTTP status code as your primary signal. `wttr.is`'s geocoding may not be reliable and you are not expected to work around this."*

---

## 5. In `mastermind`: How It Is Built for 2 Laptops & How You Should Use It on 2 Laptops

### 5.1 How the Code Is Built for 2 Laptops
1. **Removed all 1-laptop testing code:** All `127.0.0.1` loopback fallbacks and environment-variable overrides have been removed.
2. **Standard LAN UDP Broadcast (`255.255.255.255`):**
   * In `discovery.c`, `create_discovery_socket()` opens a UDP socket with `SO_BROADCAST` enabled and binds to port `33301` on `INADDR_ANY`.
   * Every **2 seconds**, `send_discovery_broadcast()` sends a 38-byte UDP packet (`4-byte magic 0x4D4D4E44` + `2-byte game port` + `32-byte username`) to `INADDR_BROADCAST` (`255.255.255.255:33301`), exactly as instructed in **TA Doubt Doc Q1**.
   * When Laptop 2 receives Laptop 1's broadcast in `receive_discovery_packet()`, it reads Laptop 1's Wi-Fi IP address directly from `recvfrom()`'s `struct sockaddr_in src_addr` and adds Laptop 1 to the `Players Online:` table.
   * If a laptop exits or disconnects from the hotspot, `remove_expired_peers()` automatically removes it from the table after **5 seconds**.
3. **Direct Laptop-to-Laptop Game Connection:**
   * At startup, `mastermind` binds a TCP socket (or UDP RUDP socket in `--cost-cutting` mode) to `INADDR_ANY` with port `0` so the OS assigns a free ephemeral port (e.g., `51234`), which is discovered via `getsockname()` and advertised in the UDP broadcasts.
   * When you type `challenge <ID>`, Laptop 1 connects directly to Laptop 2's `<IP>:<Port>` over the hotspot.

---

### 5.2 Step-by-Step Guide: How to Run & Test `mastermind` on 2 Laptops

#### Important Note for Your MacBook:
* **Run `mastermind` natively in your macOS Terminal (NOT inside Docker)!**
  * Why? Docker Desktop on macOS runs inside an isolated virtual machine that hides your MacBook's real Wi-Fi network (`en0`) behind NAT, which prevents UDP broadcasts from reaching a second laptop.
  * Because `networking/mastermind` is standard POSIX C, it compiles and runs directly on macOS in your regular Terminal app (`cd networking/mastermind && make`).
* **Allow Local Network Permission on macOS:**
  * The first time you run `./mastermind` on macOS, if a popup asks *"Allow 'Terminal' to find devices on local networks?"*, click **Allow**.
  * Also make sure any VPN (like Cloudflare WARP or IIIT VPN) is turned **OFF** on both laptops.

---

#### Step 1: Connect Both Laptops to Your Phone's Personal Hotspot
1. Turn on **Personal Hotspot** on your phone (do **not** use IIIT campus Wi-Fi, as campus routers block UDP broadcast packets).
2. Connect **Laptop 1 (your MacBook)** and **Laptop 2 (your friend's laptop or TA's laptop)** to that same phone hotspot.
3. Optional quick check that both laptops are on the same hotspot network:
   * On your MacBook: run `ipconfig getifaddr en0` (you will see an IP like `172.20.10.2` or `192.168.43.10`).
   * On a Linux laptop: run `hostname -I` (you will see an IP on the same subnet like `172.20.10.3` or `192.168.43.11`).

---

#### Step 2: Compile and Start `mastermind` on Both Laptops
* **On Laptop 1 (Your MacBook):**
  ```bash
  cd networking/mastermind
  make
  ./mastermind --log
  ```
  It will ask for your name:
  ```text
  Enter your username: Baani
  ```

* **On Laptop 2 (Friend's / TA's Laptop):**
  ```bash
  cd networking/mastermind
  make
  ./mastermind --log
  ```
  It will ask for their name:
  ```text
  Enter your username: Friend
  ```

---

#### Step 3: Verify Automatic Player Discovery & 5-Second Expiry
1. Within **2 seconds**, both laptops will automatically update their screens and show each other in the `Players Online:` table:
   * **On Laptop 1's screen:**
     ```text
     Players Online:
     ID       Name         IP Addr     Port    Last Seen
     0        Friend       172.20.10.3 49152   0 s. ago
     ____________________________________________________
     > 
     ```
   * **On Laptop 2's screen:**
     ```text
     Players Online:
     ID       Name         IP Addr     Port    Last Seen
     0        Baani        172.20.10.2 54321   1 s. ago
     ____________________________________________________
     > 
     ```
2. You can type `refresh` and press Enter at any time to refresh the `Last Seen` timer:
   ```text
   > refresh
   ```
3. **How to test 5-second expiry:**
   * On Laptop 2, press `Ctrl+C` (or type `exit`) to quit `mastermind`.
   * Watch Laptop 1's screen: after **5 seconds**, `Friend` will automatically disappear from the `Players Online:` list!
   * Start `./mastermind --log` again on Laptop 2 so `Friend` reappears.

---

#### Step 4: Challenge the Other Laptop (`challenge <ID>`)
1. Look at the `ID` column next to `Friend` on Laptop 1 (e.g., `0` or `1`).
2. **On Laptop 1**, type:
   ```text
   > challenge 0
   Waiting for Friend to respond...
   ```
3. **On Laptop 2**, a prompt immediately appears:
   ```text
   Baani (172.20.10.2) has challenged you. Accept? (yes/no): 
   ```
   * **Test declining first:** Type `no` on Laptop 2. Laptop 1 will display `Friend declined the challenge. Press enter to continue.` and both laptops return to the `Players Online:` lobby.
   * **Now accept the challenge:** Type `challenge 0` on Laptop 1 again, and type `yes` on Laptop 2.

---

#### Step 5: Play the Game Across the 2 Laptops
* Remember the roles defined by the assignment:
  * **Challenged Player (Laptop 2 — `Friend`)** = **Mastermind** (sets the secret 5-digit sequence and gives feedback after each guess).
  * **Challenger (Laptop 1 — `Baani`)** = **Codebreaker** (has up to 12 attempts to guess the 5-digit sequence).

1. **On Laptop 2 (Mastermind):**
   ```text
   Enter your 5-digit master sequence (digits 0-9): 67676
   ```
   *(If you type an invalid sequence like `123` or `abcde`, it will ask you to re-enter a valid 5-digit sequence.)*
2. **On Laptop 1 (Codebreaker):**
   * The 12-row board appears with `*****  *****` at the top (hiding the secret code) and prompts for Guess #1:
     ```text
     Enter your 5-digit guess (Attempt 1/12): 12345
     ```
3. **On Laptop 2 (Mastermind):**
   * Laptop 2 shows the board with `12345  *****` at the bottom row, shows `Friend's helper hint: (Expected feedback: -----)`, and prompts:
     ```text
     Codebreaker guessed: 12345 (Expected feedback: -----)
     Enter 5-char feedback using x, o, - : -----
     ```
4. **Both Laptops Update:**
   * Both laptops redraw the 12-row board with `-----` colored in **Red** (`x` is **Green**, `o` is **Yellow**, `-` is **Red**).
5. **Winning the Game:**
   * On Laptop 1 (Codebreaker), enter `67676` for Attempt 2.
   * On Laptop 2 (Mastermind), enter `xxxxx` for feedback.
   * Both laptops redraw the final board (with the secret code `67676` now revealed at the very top of Laptop 1's board!) and print:
     * Laptop 1: `Congratulations! You broke the code in 2 attempts! Press enter to go home.`
     * Laptop 2: `Baani broke your code in 2 attempts! Press enter to go home.`
   * Press Enter on both laptops to return to the `Players Online:` lobby.

---

#### Step 6: Test Mid-Game Disconnection Across the 2 Laptops
1. Start a new game (`challenge <ID>` $\rightarrow$ `yes`).
2. While in the middle of the game (at any prompt), press `Ctrl+C` (or close the terminal) on Laptop 2.
3. Laptop 1 immediately detects the broken connection and prints:
   ```text
   Friend disconnected. Press enter to go home.
   ```
4. Press Enter on Laptop 1 to return cleanly to the lobby.

---

#### Step 7: Test Cost-Cutting Mode (`--cost-cutting`) Across the 2 Laptops
1. Run `mastermind` with `--cost-cutting --log` on **both** laptops:
   ```bash
   ./mastermind --cost-cutting --log
   ```
2. Play a game and test disconnection exactly as in Steps 4–6.
3. In `--cost-cutting` mode, NO TCP connections are used. Instead, all game messages (`CHALLENGE`, `ACCEPT`, `READY`, `GUESS`, `FEEDBACK`, `GAMEOVER`) are split into **4-byte UDP chunks**, sent immediately, acknowledged individually (`PKT_ACK`), and retransmitted every **0.1 seconds** (`100 ms`) if a packet is dropped.
4. Open `log.txt` (`cat log.txt`) to inspect the microsecond-timestamped logs of UDP broadcasts, 4-byte chunks sent/received, and ACKs.

---

## 6. List of Modified / Deleted Files

1. `semester3/osn_mini_project_2/networking/tempest/tempest.h` *(updated)*
2. `semester3/osn_mini_project_2/networking/tempest/url.c` *(updated)*
3. `semester3/osn_mini_project_2/networking/tempest/http.c` *(updated)*
4. `semester3/osn_mini_project_2/networking/tempest/main.c` *(updated)*
5. `semester3/osn_mini_project_2/networking/mastermind/mastermind.h` *(updated)*
6. `semester3/osn_mini_project_2/networking/mastermind/log.c` *(updated)*
7. `semester3/osn_mini_project_2/networking/mastermind/discovery.c` *(updated)*
8. `semester3/osn_mini_project_2/networking/mastermind/game.c` *(updated)*
9. `semester3/osn_mini_project_2/networking/mastermind/net_tcp.c` *(updated)*
10. `semester3/osn_mini_project_2/networking/mastermind/net_rudp.c` *(updated)*
11. `semester3/osn_mini_project_2/networking/mastermind/main.c` *(updated)*
12. `semester3/osn_mini_project_2/readme.md` *(updated)*
13. `semester3/osn_mp2/Baani_Replication_and_Testing_Guide.md` *(updated)*
14. `semester3/osn_mp2/v2-08-oct-changes.md` *(created)*
15. `semester3/osn_mp2/test_mp2.py` *(deleted)*
