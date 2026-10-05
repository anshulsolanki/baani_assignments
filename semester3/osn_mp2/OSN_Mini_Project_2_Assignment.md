# CS3.301 Operating Systems and Networks — Mini Project 2 (Baani's Assignment)

**Course:** CS3.301 Operating Systems and Networks (IIIT Hyderabad)  
**Official Assignment Page:** [https://cs3301.pages.dev/assignments/02](https://cs3301.pages.dev/assignments/02)  
**Released:** September 16, 2026  
**Final Deadline:** **October 15, 2026 at 11:59 PM** (No extensions)  
**Doubt Document Cutoff:** **October 10, 2026 at 11:59 PM**

---

## 1. Screenshot Ordering & Continuity Verification

All **17 WhatsApp screenshots** in `/Users/solankianshul/Downloads/osn_mp2` were inspected and stitched together. The timestamps in the filenames (`11.01.41` to `12.00.36`) are in **exact top-to-bottom sequential order** of the assignment specification page, with zero missing sections between screenshots:

| Order | Screenshot File | Section Covered | Continuity / How It Connects to the Next Screenshot |
| :---: | :--- | :--- | :--- |
| **1** | [WhatsApp Image 2026-09-28 at 11.01.41.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.01.41.jpeg) | **Overview & Before You Start**: Deadlines, Submission rules, Git commit policy | Ends with `"You can refer to the resource on git for more details."` right before repository structure. |
| **2** | [WhatsApp Image 2026-09-28 at 11.01.59.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.01.59.jpeg) | **Repository Structure, AI Usage & Grading** | Starts with `"Your repository has the following structure:"` (`mini-project2/`), ends with **Grading**. |
| **3** | [WhatsApp Image 2026-09-28 at 11.04.03.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.04.03.jpeg) | **Networking [55]**: General Requirements, GCC flags, Allowed/Banned APIs, References (part 1) | Ends at the 3rd bullet of **References** (`Beej's Guide to Network Programming`). |
| **4** | [WhatsApp Image 2026-09-28 at 11.19.41.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.19.41.jpeg) | **Networking References (part 2) & Important Notice** | Continues **References** (`RFC 7230`, `RFC 3550`, `Shivang Srivastava's article`) and adds the **IIIT-H Network Warning**. |
| **5** | [WhatsApp Image 2026-09-28 at 11.22.25.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.22.25.jpeg) | **Part A: `tempest` [15]**: Problem statement, `wttr.is` endpoint, `curl` example, Requirements 1–2 | Ends with Requirement 2 (`Example: $ tempest Hyderabad`). |
| **6** | [WhatsApp Image 2026-09-28 at 11.27.02.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.27.02.jpeg) | **Part A: `tempest` [15]**: Requirements 3–8 & `--raw` example | Continues directly with Requirement 3 (`tempest: too many arguments`) through Requirement 8 (`--raw` output example). |
| **7** | [WhatsApp Image 2026-09-28 at 11.32.45.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.32.45.jpeg) | **Part A Conclusion & Part B: `mastermind` [40] Intro + Rules 1–6** | Finishes `tempest` (Req 10 & RFC 9112 notes), starts **Part B: mastermind [40]** and **Rules** (up to white peg `o`). |
| **8** | [WhatsApp Image 2026-09-28 at 11.33.04.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.33.04.jpeg) | **Part B: `mastermind`**: Rules 6–8, References, Feena's (mastermind) board view | Continues Rule 6 (`-` peg), Rules 7–8, game references, and shows Feena's terminal view. |
| **9** | [WhatsApp Image 2026-09-28 at 11.33.42.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.33.42.jpeg) | **Part B: `mastermind`**: Tatva's (codebreaker) board view, general notes, **Player discovery [8 marks]** intro | Directly follows Feena's view with Tatva's view, 5 general bullets, and the intro paragraph of **Player discovery**. |
| **10** | [WhatsApp Image 2026-09-28 at 11.34.30.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.34.30.jpeg) | **Player discovery Requirements 1–4 & Starting the game [2 marks]** | Lists the 4 requirements for UDP broadcast discovery, then shows the `Players Online:` table and 5-second expiry rule. |
| **11** | [WhatsApp Image 2026-09-28 at 11.35.25.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.35.25.jpeg) | **Challenging a Player & Gameplay [15 marks]** | Continues with `challenge <ID>`, `yes`/`no` handshake, role assignment, input validation, and turn flow. |
| **12** | [WhatsApp Image 2026-09-28 at 11.36.19.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.36.19.jpeg) | **Gameplay Colors/Requirements, Ending the game & Failure Management (part 1)** | Continues with ANSI colors (`o` yellow, `x` green, `-` red), Ending the game, and starts **Failure Management**. |
| **13** | [WhatsApp Image 2026-09-28 at 11.36.33.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.36.33.jpeg) | **Failure Management (part 2) & Cost Cutting [15 marks]** | Starts with `<Player_name> disconnected. Press enter to go home.` and covers the `--cost-cutting` reliable-UDP specification. |
| **14** | [WhatsApp Image 2026-09-28 at 11.36.49.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.36.49.jpeg) | **Logging [5 marks]** | Covers the `--log` flag, `log.txt`, and the C snippet using `gettimeofday()` + `strftime()`. Finishes the Networking section. |
| **15** | [WhatsApp Image 2026-09-28 at 11.37.08.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.37.08.jpeg) | **xv6 [90]**: Intro & **Copy-on-write fork [50]** (Overview + Approach bullets 1–3) | Starts the **xv6 [90]** section, CoW fork problem statement, `kalloc`/`kfree` [10], `uvmcopy` [15], and `usertrap` [15] intro. |
| **16** | [WhatsApp Image 2026-09-28 at 11.59.08.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2011.59.08.jpeg) | **Copy-on-write fork** (`usertrap` sub-bullets + `copyout` [10]) & **Alarms [40]** (Intro, Syscalls, Req 1–2) | Finishes CoW fork approach (`copyout`), starts **Alarms [40]**, `sigalarm`/`sigreturn` prototypes, and first 2 requirements. |
| **17** | [WhatsApp Image 2026-09-28 at 12.00.36.jpeg](file:///Users/solankianshul/Downloads/osn_mp2/WhatsApp%20Image%202026-09-28%20at%2012.00.36.jpeg) | **Alarms [40]**: Remaining Requirements & Approach | Completes the remaining 6 requirements and 3 **Approach** milestones (`proc.h`/`allocproc.c` [10], syscalls [15], `usertrap` [15]). |

---

## 2. Mapping Your Daughter's Reference Document to the Assignment

Below is how every link and reference from your daughter's shared document connects back to the screenshots and assignment tasks:

| Reference in Document | Actual Link / Resource | Screenshot(s) | Where & Why It Is Used in the Assignment |
| :--- | :--- | :---: | :--- |
| `https://cs3301.pages.dev/resources/git` | [CS3.301 Git Resource Guide](https://cs3301.pages.dev/resources/git) | **#1** (`11.01.41`) | **Submission Rules**: Explains how to make atomic, descriptive commits (e.g., `tempest: parse HTTP status line and headers`), push within 24 hours of each commit, and rebase branches (needed when combining xv6 CoW fork and Alarms branches). |
| `Beej’s Guide to Network Programming` | [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) | **#3** (`11.04.03`) | **Networking (General)**: Primary reference for programming raw POSIX sockets in C (`socket`, `bind`, `listen`, `accept`, `connect`, `send`, `recv`, `sendto`, `recvfrom`, `setsockopt`, `getaddrinfo`, `poll`/`select`). |
| `RFC 7230 sections 3.1 to 3.3, for HTTP message syntax and chunked encoding` | [RFC 7230 §§ 3.1–3.3](https://www.rfc-editor.org/rfc/rfc7230#section-3.1) | **#4** (`11.19.41`) | **Part A (`tempest`)**: Explains HTTP/1.1 request/response start-lines, header fields (`\r\n` CRLF delimiters), message body length, and `Transfer-Encoding: chunked`. |
| `RFC 3550 section 6.4.1, for the interarrival jitter formula` | [RFC 3550 § 6.4.1](https://www.rfc-editor.org/rfc/rfc3550#section-6.4.1) | **#4** (`11.19.41`) | **Networking General References**: Listed under the Networking references section for packet timing/jitter concepts. |
| `Shivang Srivastava’s article on how to write an HTTP request from scratch` | [From TCP to HTTP: Understanding the Magic Behind Your Web Requests](https://shv-ng.medium.com/from-tcp-to-http-understanding-the-magic-behind-your-web-requests-b9bae1a8debb) | **#4** (`11.19.41`) | **Part A (`tempest`)**: Step-by-step tutorial on opening a TCP socket and manually formatting/sending a raw HTTP GET request over it. |
| `https://www.rfc-editor.org/info/rfc9112/#section-9.3` | [RFC 9112 § 9.3 (Connection Tear-down)](https://www.rfc-editor.org/rfc/rfc9112.html#section-9.3) | **#5** (`11.22.25`) | **Part A (`tempest`) Requirement 1**: `tempest` does not need persistent connections; this section explains how to cleanly close/tear down an HTTP/1.1 connection (e.g., `Connection: close`). |
| `https://www.rfc-editor.org/info/rfc9112/#section-2` & `#section-3` | [RFC 9112 § 2 (Message)](https://www.rfc-editor.org/rfc/rfc9112.html#section-2) & [§ 3 (Request Line)](https://www.rfc-editor.org/rfc/rfc9112.html#section-3) | **#7** (`11.32.45`) | **Part A (`tempest`) Notes**: Defines the exact wire format of an HTTP/1.1 message and request line (`GET /<city_name>?0T HTTP/1.1\r\nHost: wttr.is\r\n...`). |
| `Here is a link to a video of the rules for further understanding...` | [How to Play Mastermind (YouTube)](https://www.youtube.com/watch?v=wsYPsrzCKiA) | **#8** (`11.33.04`) | **Part B (`mastermind`) Rules**: Visual explanation of the classic Mastermind board game mechanics (adapted here to a 12×5 board with digits `0–9`, `x` for exact match, `o` for wrong-position match, `-` for miss, and duplicate digits allowed). |
| `Here is a better illustrated gameplay example.` | [Illustrated Gameplay Link](https://www.youtube.com/watch?v=dQw4w9WgXcQ) | **#8** (`11.33.04`) | **Part B (`mastermind`) Rules**: Linked in the assignment handout right below the first video (note: the course staff put a playful Rickroll link here, so rely on the written rules in Screenshots #7–#9!). |
| `Link to the wikipedia page for the pen and paper version of the game.` | [Bulls and Cows (Wikipedia)](https://en.wikipedia.org/wiki/Bulls_and_cows) | **#8** (`11.33.04`) | **Part B (`mastermind`) Rules**: Explains the pen-and-paper number-guessing variant of Mastermind. |
| `https://cs3301.pages.dev/assignments/02#player-discovery-8-marks` | [Assignment 2 — Player Discovery Section](https://cs3301.pages.dev/assignments/02#player-discovery-8-marks) | **#9 & #10** (`11.33.42`, `11.34.30`) | **Part B (`mastermind`) Player Discovery**: Direct anchor link to the 8-mark UDP broadcast discovery specification (also the URL for the entire Mini Project 2 page). |
| `https://en.wikipedia.org/wiki/Broadcast_address` | [Broadcast Address (Wikipedia)](https://en.wikipedia.org/wiki/Broadcast_address) | **#9** (`11.33.42`) | **Part B (`mastermind`) Player Discovery**: Explains IPv4 subnet/broadcast addresses (used with `setsockopt(..., SO_BROADCAST, ...)` so players on the same LAN can discover each other via UDP). |

---

## 3. What Exactly Is the Assignment & What Needs to Be Done?

This is an **individual assignment** divided into two major parts:
1. **Part 1: Networking in C using Raw POSIX Sockets** (`networking/` — **55 marks** header, **60 marks** sum of sub-components)
2. **Part 2: xv6 Operating System Kernel Modifications** (`xv6/` — **90 marks**)

### Repository Structure & Mandatory Rules
You must work only inside your allocated private repository under the `osn` organization on `code.iiit.ac.in`:
```text
mini-project2/
├── networking/
│   ├── tempest/
│   ├── mastermind/
├── xv6/
│   ├── user/
│   ├── kernel/
│   ├── Makefile
│   └── ...
├── ai-usage.md
└── readme.md
```

* **Git Commit Policy (Strict):**
  * Commit iteratively and coherently as you build each feature.
  * **Push after every single commit (within 24 hours of each commit).**
  * Use clear, feature-specific commit messages (e.g., `tempest: parse HTTP status line and headers`).
  * Large bulk commits right before the deadline or vague commit messages will be penalized.
* **AI Usage Policy (Strict):**
  * **NO AI agents** are allowed to generate code or the report.
  * AI chatbots may be used *only* for understanding concepts and debugging errors.
  * Every prompt used must be documented in `ai-usage.md` as **chat links only** (no screenshots).
* **Grading:** Code implementation + in-person evaluation (viva) with a TA.
* **Documentation (`readme.md`):** Must contain build instructions, run instructions, all design/protocol assumptions made, disconnection detection mechanisms (for both TCP and UDP), custom communication verbs/error names/payloads, magic packet value, and known bugs.

---

## 4. Detailed Task Breakdown: Part 1 — Networking (`networking/`)

### General Networking Constraints
* **Modularity:** Break code into multiple `.c` and `.h` files by functionality (monolithic code will be penalized).
* **Build System:** Running `make all` at the top level of `networking/` must build and output both `tempest` and `mastermind` binaries right inside `networking/`.
* **Compiler Flags:**
  ```bash
  gcc -std=c23 \
    -D_POSIX_C_SOURCE=200809L \
    -D_XOPEN_SOURCE=700 \
    -Wall -Wextra -Werror \
    -Wno-unused-parameter \
    your_file.c
  ```
  *(Only `-lm` may be linked. No other external libraries.)*
* **Allowed API:** Raw POSIX sockets only: `socket`, `bind`, `listen`, `accept`, `connect`, `send`, `sendto`, `recv`, `recvfrom`, `setsockopt`, `getsockopt`, `getaddrinfo`, `shutdown`, `close`, and `poll`, `select`, or `epoll`.
* **Banned (0 marks if used):** `libcurl`, `libevent`, `libuv`, `ZeroMQ`, `ENet`, or shelling out to `curl`, `wget`, `nc`.
* **CRITICAL NETWORK WARNING:** **Never test `mastermind` (especially UDP broadcast discovery) on IIIT-H WiFi or LAN.** Always test using a personal mobile hotspot.

---

### Task 1A: `tempest` — Raw Socket HTTP/1.1 Weather Client [15 Marks]
Build a command-line HTTP/1.1 client `tempest` that fetches current weather reports from `http://wttr.is/<city_name>?0T`.

#### What Needs to Be Implemented:
1. **Command-Line Parsing:**
   * Usage: `$ tempest <city_name>` or `$ tempest <city_name> --raw` (Note: `--raw` must appear *after* the city argument).
   * If more than one location argument is given, print: `tempest: too many arguments`.
   * URL-encode `<city_name>` if it contains spaces or special characters (e.g., `New York` $\rightarrow$ `New%20York`, passed as `"New York"` on CLI).
2. **DNS Resolution & TCP Connection:**
   * Resolve `wttr.is` (port `80`) using `getaddrinfo()` and open a TCP `socket()` + `connect()`.
3. **10-Second Request Timeout:**
   * Enforce a 10-second timeout on the request (using `setsockopt` with `SO_RCVTIMEO`/`SO_SNDTIMEO` or `poll()`/`select()`). Terminate the request if it exceeds 10 seconds (document in `readme.md` if customized).
4. **Construct & Send Raw HTTP/1.1 GET Request:**
   * Send a valid HTTP/1.1 request to `GET /<url_encoded_city>?0T HTTP/1.1\r\nHost: wttr.is\r\nUser-Agent: curl/8.0\r\nConnection: close\r\n\r\n` (note: `wttr.is` formats output as plain text when `User-Agent` resembles `curl` or `?0T` is used; test the exact headers against `wttr.is`).
   * Handle **short writes** (loop `send()` until all bytes of the request are transmitted).
   * Persistent connections are not required (`Connection: close` per RFC 9112 § 9.3).
5. **Receive & Parse HTTP/1.1 Response:**
   * Handle **short reads** (loop `recv()` until the server closes the connection or full `Content-Length` / chunked body is read).
   * Separate HTTP response headers from the response body (split at `\r\n\r\n`).
   * Check for invalid locations (e.g., HTTP 404 or error body from `wttr.is`) and print: `tempest: invalid location`.
6. **Output Formatting (`default` vs. `--raw`):**
   * **Default (`$ tempest Hyderabad`):** Print **only** the weather report body (do NOT print HTTP headers):
     ```text
     $ tempest Hyderabad

     Weather report: Hyderabad

                     Overcast
            .--.     +22(25) °C
         .-(    ).   ↙ 4 km/h
        (___.__)__)  10 km
                     0.0 mm
     ```
   * **Raw Mode (`$ tempest Rotterdam --raw`):** Print the outgoing HTTP request lines prefixed with `> `, followed by the exact HTTP response headers prefixed with `< `, and then the response body (matching Screenshot #6):
     ```text
     $ tempest Rotterdam --raw
     > <YOUR HTTP REQUEST HERE>
     > ...
     > ...
     > ...
     < HTTP/1.1 200 OK
     < Access-Control-Allow-Origin: *
     < Cache-Control: public, max-age=600
     < Content-Type: text/plain; charset=utf-8
     < Date: Sun, 13 Sep 2026 10:36:33 GMT
     < Content-Length: 173
     <
     Weather report: Rotterdam

        _`/"".-.     Light rain shower
         ,\_(   ).   19 °C
          /(___(__)  → 14 km/h
            ‘ ‘ ‘ ‘  10 km
           ‘ ‘ ‘ ‘   0.9 mm
     ```
   * *(Note: Requirement #9 is skipped in the handout numbering — it jumps from 8 to 10.)* Requirement 10: Be prepared to explain every HTTP request and response header field used during your TA evaluation.

---

### Task 1B: `mastermind` — P2P LAN Game over TCP & Reliable UDP [40–45 Marks]
Build a peer-to-peer terminal game where two players on the same LAN discover each other via UDP broadcast and play a 12-attempt, 5-digit Mastermind game. Both players run the **exact same executable** (`mastermind`). Use non-blocking sockets / I/O multiplexing (`poll`, `select`, or `epoll`) rather than threads.

#### Subtask 1: Startup & UDP Broadcast Player Discovery [8 + 2 = 10 Marks]
1. **Startup Prompt & Listener:**
   * Ask the user to enter their player name.
   * Bind and start listening for incoming game connections on a chosen port.
2. **UDP Broadcast Discovery:**
   * Create a UDP socket enabled for broadcast (`SO_BROADCAST`).
   * Every **2 seconds**, broadcast a discovery packet to the LAN broadcast address.
   * **Packet Payload Requirements:**
     * **4-byte Magic Identifier:** To identify packets belonging to your `mastermind` program and ignore foreign network traffic (document the 4-byte magic value in `readme.md`).
     * **Player Name** and **Listening Port Number**.
     * **Do NOT include the player's IP address in the payload** — the receiver must extract the sender's IP address from the UDP packet's source address (`recvfrom` `src_addr`).
3. **Live Lobby UI (`Players Online`):**
   * Continuously display and refresh the discovered peers table whenever a broadcast packet arrives:
     ```text
     Players Online:
     ID       Name         IP Addr     Port    Last Seen
     1    Tatva           10.2.35.123  8080    2 s. ago
     2    ristiavdaatnso  10.2.35.125  8000    1 s. ago
     ____________________________________________________
     > 
     ```
   * **5-Second Expiry:** Remove any player from the list if no broadcast packet has been received from them for **5 seconds**.

#### Subtask 2: Challenging a Player & Establishing the Session [Part of Starting/Gameplay]
* Typing `challenge <ID>` (e.g., `> challenge 1`) sends a connection/challenge request to that player's `IP:Port` (e.g., `10.2.35.123:8080`).
* The challenged player is prompted to accept (`yes`) or reject (`no`):
  * `no` $\rightarrow$ both return to UDP discovery lobby.
  * `yes` $\rightarrow$ starts the game over a **persistent bi-directional TCP socket** (or UDP in `--cost-cutting` mode).
* **Role Assignment:**
  * **Challenger (Initiator, e.g., Feena)** = **Mastermind** (sets the secret 5-digit sequence and gives feedback).
  * **Acceptor (Challenged, e.g., Tatva)** = **Codebreaker** (has 12 attempts to guess the sequence).

#### Subtask 3: Gameplay Mechanics & Terminal Rendering [15 Marks]
1. **Setting the Master Sequence (Mastermind):**
   * Prompt Mastermind (Feena) to enter the 5-digit `master sequence`.
   * **Validation:** Must be **exactly 5 characters**, and **all 5 characters must be digits (`0–9`)**. (Duplicate digits are allowed.)
   * **Security Rule:** Do **NOT** send the `master sequence` over the network to the Codebreaker until the game has ended!
2. **Turn Loop (Up to 12 Attempts):**
   * **Codebreaker's Guess:** Codebreaker enters a 5-digit attempt (must also be validated: length 5, all digits `0–9`) and presses Enter to send it over the socket.
   * **Mastermind's Feedback:** Mastermind receives the attempt, assigns a 5-character feedback string, and presses Enter to send it back.
   * **Feedback Rules & Validation:**
     * Validate that feedback is **exactly 5 characters** containing only `x`, `o`, or `-`:
       * `x` (red peg in classic rules, **colored GREEN** in terminal): digit is in the master sequence and in the **correct position**.
       * `o` (white peg in classic rules, **colored YELLOW** in terminal): digit is in the master sequence but in the **wrong position**.
       * `-` (no peg, **colored RED** in terminal): digit is **not present** in the master sequence (or already accounted for).
     * Feedback is given **out of order** (e.g., `xo---` does not reveal which specific position matched).
     * Duplicate digits are scored per occurrence.
3. **Board Rendering & ANSI Colors:**
   * Re-render the 12-row board after every attempt and feedback update.
   * On the Codebreaker's board, color the feedback characters using ANSI escape sequences:
     * `x` = **Green**
     * `o` = **Yellow**
     * `-` = **Red**
   * Both players see the exact same 12 rows of guesses and feedback, except below the `-----` divider on row 13 (Mastermind sees the secret `master sequence`, while Codebreaker sees `*****` until the game ends):
     * **Feena's (Mastermind) View:**
       ```text
       12345  -----
       65731  xo---
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       -----
       67676
       ```
     * **Tatva's (Codebreaker) View:**
       ```text
       12345  -----
       65731  xo---
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       *****  *****
       -----
       *****
       ```
4. **Ending the Game:**
   * Triggered when: (1) Codebreaker guesses all 5 digits correctly in $\le 12$ attempts, OR (2) Codebreaker exhausts all 12 attempts.
   * Mastermind's program sends the `master sequence` to Codebreaker's program and closes the game socket.
   * Codebreaker's board reveals the `master sequence` at the bottom.
   * Pressing `Enter` returns both players to the UDP discovery homepage.

#### Subtask 4: Failure Management (Disconnection Detection)
* If either player closes their application or disconnects mid-game (in **both** normal TCP mode and `--cost-cutting` UDP mode), the other player's program must detect it and display:
  ```text
  <Player_name> disconnected. Press enter to go home.
  ```
* Pressing `Enter` returns the remaining player to the UDP discovery homepage.
* Document how disconnection detection works for both TCP (e.g., `recv` returning `0` / `POLLHUP`) and UDP (e.g., heartbeat/keepalive or unacknowledged retries) in `readme.md`.

#### Subtask 5: Cost Cutting Mode (`--cost-cutting`) — Reliable UDP [15 Marks]
When `mastermind` is launched with `--cost-cutting`, **all game state transfers between players must use UDP instead of TCP**, with custom reliability layered on top:
1. **Chunking & Reordering:**
   * Divide outgoing text/state messages into **fixed-size chunks** sent inside a C `struct`.
   * Include the **sequence number** of the chunk and the **total number of chunks**.
   * The receiver buffers incoming chunks, **reorders them by sequence number**, aggregates them once all chunks arrive, and processes/displays the complete message.
2. **Non-Blocking Per-Chunk ACK & 0.1s Retransmission:**
   * The receiver sends an **ACK** referencing the sequence number for every chunk received.
   * The sender **must NOT wait** for an ACK before sending subsequent chunks (pipelined/sliding transmission).
   * If any chunk is not acknowledged within **0.1 seconds (100 ms)**, the sender must **retransmit** that specific chunk.

#### Subtask 6: Event Logging (`--log`) [5 Marks]
When launched with `--log`, append every network/game event sent or received to `log.txt` (do not overwrite) using the exact microsecond timestamp format given in Screenshot #14:
```c
#include <stdio.h>
#include <sys/time.h>
#include <time.h>

// Inside your logging function
char time_buffer[30];
struct timeval tv;
time_t curtime;

gettimeofday(&tv, NULL);
curtime = tv.tv_sec;

// Format the time part
strftime(time_buffer, 30, "%Y-%m-%d %H:%M:%S", localtime(&curtime));

// Add microseconds and print to the log file
fprintf(log_file, "[%s.%06ld] [LOG] Your message here\n", time_buffer, tv.tv_usec);
```

---

## 5. Detailed Task Breakdown: Part 2 — xv6 Kernel (`xv6/`) [90 Marks]

> **Git Workflow Recommendation from Handout:**  
> Because both **Copy-on-Write Fork** and **Alarms** modify `kernel/trap.c` (`usertrap`), develop them on **two separate git branches** and `git rebase` them when finished so all CoW commits are grouped together and all Alarm commits are grouped together.

---

### Task 2A: Copy-on-Write (CoW) Fork [50 Marks]
Instead of duplicating every physical page in `uvmcopy()` during `fork()`, map both parent and child virtual pages to the **same physical pages** marked read-only + CoW, and allocate/copy a physical page only when either process attempts to write to it.

* **Verification Target:** Both `cowtest` and `usertests -q` must pass in xv6.

#### Step-by-Step Implementation Plan (Graded Milestones):
1. **Physical Page Reference Counting (`kernel/kalloc.c`) [10 Marks]:**
   * Maintain a reference count array (protected by a spinlock) indexed by physical page number (`pa / PGSIZE`).
   * Set ref count to `1` when `kalloc()` allocates a page.
   * Create helper functions to increment ref count (when sharing a page in `uvmcopy`) and decrement ref count in `kfree()`.
   * Only free the physical page back to the freelist in `kfree()` when its reference count drops to `0`.
2. **Share Pages in `uvmcopy()` (`kernel/vm.c`) [15 Marks]:**
   * Do not allocate new physical memory in `uvmcopy()`.
   * For any writable page (`PTE_W`), clear `PTE_W` and set a software-reserved PTE bit (e.g., `PTE_COW = (1L << 8)` in RISC-V Sv39, which reserves bits 8 and 9 for supervisor software) in **both** the parent's and child's PTEs.
   * Map the child's virtual address to the parent's physical address using `mappages()` and increment the physical page's reference count.
3. **Handle CoW Page Faults in `usertrap()` (`kernel/trap.c`) [15 Marks]:**
   * Detect store page faults (`r_scause() == 15` on RISC-V).
   * Check the faulting virtual address (`r_stval()`): verify it is within user address space, mapped, and marked with `PTE_COW` (do NOT duplicate genuinely read-only pages like code/text segments — kill the process on invalid faults).
   * Allocate a new physical page with `kalloc()`, copy the 4096 bytes from the old physical page, decrement the old page's reference count via `kfree()`, and update the faulting process's PTE to point to the new physical page with `PTE_W` restored and `PTE_COW` cleared. (Optimization: if ref count is already `1`, you can simply restore `PTE_W` and clear `PTE_COW` without allocating/copying, or allocate/copy and let `kfree` free the old ref.)
   * If `kalloc()` runs out of memory (`0`), kill the process (`setkilled(p)`).
4. **Handle CoW Pages in `copyout()` (`kernel/vm.c`) [10 Marks]:**
   * When the kernel copies data to user space via `copyout()`, software page table walks bypass hardware page faults.
   * Check if the destination user PTE has `PTE_COW` set; if so, perform the same CoW page allocation, copy, reference count decrement, and PTE update before writing to the page.

---

### Task 2B: Process Alarms (`sigalarm` & `sigreturn`) [40 Marks]
Allow user processes to register a periodic user-space callback function (`handler`) that the kernel invokes every `n` CPU ticks consumed by that process.

* **System Call Signatures:**
  ```c
  int sigalarm(int ticks, void (*handler)());
  int sigreturn(void);
  ```
* **Verification Target:** Both `alarmtest` and `usertests -q` must pass in xv6.

#### Requirements Checklist:
* `sigalarm(n, fn)` registers `fn` to run every `n` ticks of CPU time. Calling `sigalarm(0, 0)` cancels any pending alarm.
* `sigalarm` returns `0` on success and non-zero on error.
* Note that `0x0` (null pointer) is a valid code address in xv6 (`0` is where user text starts), so only check if a timer is active (`ticks > 0`), not whether `handler != 0`.
* When the alarm fires, the user handler executes in user mode and finishes by calling `sigreturn()`.
* `sigreturn()` must restore the exact interrupted register state so the user program resumes at the exact instruction where it was interrupted, completely undisturbed, and `sigreturn` must return the return value (i.e., `trapframe->a0` restored to its pre-interrupt value).
* The alarm is **periodic**: reset the tick counter each time the alarm fires.
* **No Re-entrancy:** If an alarm handler is currently executing and has not yet called `sigreturn()`, the kernel must **not** invoke the handler again until `sigreturn()` completes.

#### Step-by-Step Implementation Plan (Graded Milestones):
1. **Process State Fields (`kernel/proc.h` & `kernel/proc.c` / `allocproc`) [10 Marks]:**
   * Add fields to `struct proc` in `kernel/proc.h`:
     * Alarm interval (`alarm_ticks` / `n`)
     * Handler function pointer (`alarm_handler`)
     * Elapsed ticks counter since last alarm (`ticks_passed`)
     * Flag indicating whether the process is currently inside an alarm handler (`in_alarm_handler`)
     * Saved copy of the interrupted user trapframe (`struct trapframe *alarm_tf` or inline struct) so registers aren't corrupted by the handler.
   * Initialize these fields in `allocproc()` and clean them up in `freeproc()`.
2. **Implement `sigalarm` and `sigreturn` Syscalls [15 Marks]:**
   * Register syscall numbers in `kernel/syscall.h`, `kernel/syscall.c`, `user/user.h`, and `user/usys.pl`.
   * `sys_sigalarm()`: Read `ticks` and `handler` arguments (`argint`, `argaddr`). If `ticks < 0`, return `-1`. Store `alarm_ticks = ticks`, `alarm_handler = handler`, reset `ticks_passed = 0`, and return `0`.
   * `sys_sigreturn()`: Restore `p->trapframe` from the saved `alarm_tf`, clear `in_alarm_handler = 0`, and return the restored `p->trapframe->a0` so user space sees the original `a0` register untouched.
3. **Timer Interrupt Handling in `usertrap()` (`kernel/trap.c`) [15 Marks]:**
   * In `usertrap()`, when a timer interrupt occurs (`which_dev == 2`):
     * Check if the current process has an active alarm (`p->alarm_ticks > 0`) and is **not** already in the handler (`!p->in_alarm_handler`).
     * Increment `p->ticks_passed`.
     * When `p->ticks_passed >= p->alarm_ticks`:
       * Reset `p->ticks_passed = 0`.
       * Set `p->in_alarm_handler = 1`.
       * Save the current `*p->trapframe` into `p->alarm_tf`.
       * Redirect execution to the user handler by setting `p->trapframe->epc = p->alarm_handler`.

---

## 6. Master Execution Checklist for Baani

- [ ] **Setup & Git Hygiene**
  - [ ] Clone the private template repo from `code.iiit.ac.in` under `osn`.
  - [ ] Remember to commit after every small milestone and `git push` within 24 hours of each commit.
  - [ ] Keep `ai-usage.md` updated with chat links if any AI chatbot is used for concept explanations or debugging.
- [ ] **Part 1A: `networking/tempest/` (15 Marks)**
  - [ ] Implement CLI argument parsing (`<city_name>`, optional trailing `--raw`, `tempest: too many arguments`).
  - [ ] Implement URL encoding for city names.
  - [ ] Implement DNS lookup (`getaddrinfo`), TCP connect, and 10s socket timeout.
  - [ ] Implement HTTP/1.1 request formatting, short-write handling, and short-read response loop.
  - [ ] Strip headers in normal mode, print `> ` / `< ` headers in `--raw` mode, and print `tempest: invalid location` on bad city names.
- [ ] **Part 1B: `networking/mastermind/` (40–45 Marks)**
  - [ ] Switch to personal mobile hotspot before testing any UDP broadcast code!
  - [ ] Implement UDP broadcast discovery (every 2s, 4-byte magic header, name + port payload, source IP extraction, 5s timeout removal).
  - [ ] Implement `Players Online` table UI and `challenge <ID>` + `yes`/`no` handshake.
  - [ ] Implement 5-digit sequence validation, 5-char feedback validation (`x`, `o`, `-`), ANSI color output, and 12-turn board rendering.
  - [ ] Implement end-of-game secret sequence reveal and return-to-lobby flow.
  - [ ] Implement disconnect detection (`<Player_name> disconnected. Press enter to go home.`) for both TCP and UDP.
  - [ ] Implement `--cost-cutting` mode (UDP fixed-size chunk `struct` with `seq_num` & `total_chunks`, receiver reordering, per-chunk ACK, non-blocking 0.1s retransmission timer).
  - [ ] Implement `--log` mode appending microsecond-timestamped events to `log.txt`.
  - [ ] Verify top-level `make all` in `networking/` compiles both `tempest` and `mastermind` cleanly with all C23 warning flags.
- [ ] **Part 2A: `xv6/` Copy-on-Write Fork (50 Marks — Branch 1)**
  - [ ] Implement physical page reference counting in `kalloc.c`.
  - [ ] Modify `uvmcopy()` in `vm.c` to map shared pages read-only with `PTE_COW`.
  - [ ] Handle store page faults (`scause == 15`) on `PTE_COW` pages in `usertrap()` (`trap.c`).
  - [ ] Handle `PTE_COW` pages in `copyout()` (`vm.c`).
  - [ ] Run `cowtest` and `usertests -q`.
- [ ] **Part 2B: `xv6/` Alarms (40 Marks — Branch 2)**
  - [ ] Add alarm fields and saved trapframe to `struct proc` (`proc.h`, `proc.c`).
  - [ ] Wire up and implement `sigalarm` and `sigreturn` system calls.
  - [ ] Update timer interrupt handling in `usertrap()` (`trap.c`) with non-reentrant handler invocation.
  - [ ] Run `alarmtest` and `usertests -q`.
  - [ ] Rebase the two xv6 branches cleanly so CoW commits and Alarm commits are grouped logically.
- [ ] **Final Documentation (`readme.md` & `ai-usage.md`)**
  - [ ] Document build/run instructions, custom protocol headers/verbs/payloads, 4-byte magic value, timeout values, TCP & UDP disconnect detection methods, assumptions, and known bugs in `readme.md`.
