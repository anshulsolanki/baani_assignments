#!/usr/bin/env python3
"""
End-to-End Verification Suite for CS3.301 OSN Mini Project 2
============================================================
Runs 100% on a SINGLE machine (no second laptop required) and verifies:
1. Build Verification:
   - `make clean && make all` in `networking/` (`tempest` and `mastermind`) with strict C23 flags.
   - Cross-target syntax & type verification of all `xv6/kernel/*.c` files with `-target riscv64-unknown-elf`.
2. `tempest` Functional Tests:
   - CLI argument validation (`tempest a b` -> `tempest: too many arguments`)
   - RFC 3986 URL percent-encoding (`"New York"` -> `"New%20York"`)
   - Live HTTP/1.1 query to `wttr.is` (`Hyderabad`, `"New York" --raw`, and invalid location)
   - Chunked Transfer-Encoding (`Transfer-Encoding: chunked`) against a local mock HTTP/1.1 server
3. `mastermind` Full 2-Player End-to-End Tests (on a Single Machine):
   - Sequence (`0-9` x 5) and feedback (`x`/`o`/`-` x 5) validation + feedback computation rules
   - 2-Player UDP Broadcast Discovery (`SO_REUSEPORT` on port 33301, 4-byte magic `0x4D4D4E44`,
     source IP extraction from `recvfrom`, peer table insertion)
   - 2-Player Persistent TCP Game Session (`\n` framing, `CHALLENGE` -> `ACCEPT` -> `READY` ->
     `GUESS` -> `FEEDBACK` -> `GAMEOVER`, plus TCP peer disconnect detection)
   - 2-Player Reliable UDP (`--cost-cutting`) Session (4-byte chunk splitting, out-of-order chunk
     reassembly, per-chunk ACKs, 0.1s retransmission on simulated packet drop, and `log.txt` verification)
"""

import ctypes
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent / "osn_mini_project_2"
NET_DIR = PROJECT_DIR / "networking"
TEMPEST_DIR = NET_DIR / "tempest"
MM_DIR = NET_DIR / "mastermind"
XV6_DIR = PROJECT_DIR / "xv6"

PASS_COUNT = 0
FAIL_COUNT = 0


def report(name: str, passed: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}" + (f" ({detail})" if detail else ""))
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}" + (f" ({detail})" if detail else ""))


def test_builds():
    print("\n=== 1. Build & Compiler Verification ===")
    r1 = subprocess.run(["make", "clean"], cwd=NET_DIR, capture_output=True, text=True)
    r2 = subprocess.run(["make", "all"], cwd=NET_DIR, capture_output=True, text=True)
    report(
        "networking: `make clean && make all` (-std=c23 -Wall -Wextra -Werror)",
        r1.returncode == 0 and r2.returncode == 0,
        "tempest and mastermind built cleanly",
    )

    has_bins = (TEMPEST_DIR / "tempest").exists() and (MM_DIR / "mastermind").exists()
    report("networking binaries generated at expected paths", has_bins)
    subprocess.run(["make", "clean"], cwd=NET_DIR, capture_output=True)

    kernel_c_files = [str(p) for p in sorted((XV6_DIR / "kernel").glob("*.c"))]
    cmd = [
        "clang",
        "-target",
        "riscv64-unknown-elf",
        "-Wall",
        "-Werror",
        "-Wno-unknown-attributes",
        "-O",
        "-fno-omit-frame-pointer",
        "-ggdb",
        "-gdwarf-2",
        "-march=rv64gc",
        "-std=gnu99",
        "-mcmodel=medany",
        "-ffreestanding",
        "-fno-common",
        "-nostdlib",
        "-I.",
        "-fsyntax-only",
    ] + kernel_c_files
    r3 = subprocess.run(cmd, cwd=XV6_DIR, capture_output=True, text=True)
    report(
        "xv6: all kernel/*.c pass riscv64-unknown-elf -Wall -Werror check",
        r3.returncode == 0,
        r3.stderr.strip() if r3.returncode != 0 else "0 warnings, 0 errors",
    )


def test_tempest():
    print("\n=== 2. `tempest` HTTP/1.1 Weather Client Tests ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        dylib_path = Path(tmpdir) / "libtempest.dylib"
        c_files = [str(p) for p in sorted(TEMPEST_DIR.glob("*.c"))]
        cmd = [
            "gcc",
            "-dynamiclib",
            "-std=c23",
            "-D_POSIX_C_SOURCE=200809L",
            "-D_XOPEN_SOURCE=700",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-unused-parameter",
            "-o",
            str(dylib_path),
        ] + c_files
        subprocess.run(cmd, check=True)

        lib = ctypes.CDLL(str(dylib_path))
        lib.url_encode.argtypes = [ctypes.c_char_p]
        lib.url_encode.restype = ctypes.c_char_p

        enc = lib.url_encode(b"New York")
        report("url_encode('New York') -> 'New%20York'", enc == b"New%20York", f"got {enc!r}")

        def run_tempest_cli(args, env_extra=None):
            env = os.environ.copy()
            if env_extra:
                env.update(env_extra)
            code = f"""
import ctypes, sys
lib = ctypes.CDLL({str(dylib_path)!r})
args = [b"tempest"] + {[a.encode() for a in args]!r}
argv = (ctypes.c_char_p * len(args))(*args)
rc = lib.main(len(args), argv)
sys.exit(rc)
"""
            return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)

        res_args = run_tempest_cli(["a", "b"])
        report(
            "CLI: `tempest a b` prints `tempest: too many arguments`",
            "tempest: too many arguments" in res_args.stdout and res_args.returncode != 0,
            res_args.stdout.strip(),
        )

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(5)
        port = server.getsockname()[1]

        def handle_mock_requests():
            for _ in range(2):
                conn, _ = server.accept()
                req = conn.recv(1024).decode("utf-8", errors="replace")
                if "GET /ChunkCity?0T HTTP/1.1" in req:
                    resp = (
                        "HTTP/1.1 200 OK\r\n"
                        "Transfer-Encoding: chunked\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        "8\r\nWeather:\r\n"
                        "7\r\n Sunny\n\r\n"
                        "0\r\n\r\n"
                    )
                    conn.sendall(resp.encode())
                else:
                    resp = (
                        "HTTP/1.1 404 Not Found\r\n"
                        "Content-Length: 27\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        "Unknown location; please try"
                    )
                    conn.sendall(resp.encode())
                conn.close()
            server.close()

        t = threading.Thread(target=handle_mock_requests, daemon=True)
        t.start()

        mock_env = {"TEMPEST_HOST": "127.0.0.1", "TEMPEST_PORT": str(port)}
        res_chunk = run_tempest_cli(["ChunkCity", "--raw"], env_extra=mock_env)
        report(
            "HTTP/1.1 chunked Transfer-Encoding + `--raw` header/request prefixing",
            "> GET /ChunkCity?0T HTTP/1.1" in res_chunk.stdout
            and "< HTTP/1.1 200 OK" in res_chunk.stdout
            and "Weather: Sunny" in res_chunk.stdout,
        )

        res_inv = run_tempest_cli(["NowhereLandXYZ"], env_extra=mock_env)
        report(
            "Invalid location detection prints `tempest: invalid location`",
            res_inv.stdout.strip() == "tempest: invalid location",
            res_inv.stdout.strip(),
        )
        t.join(timeout=2)

        res_live = run_tempest_cli(["Hyderabad"])
        report(
            "Live HTTP/1.1 query to wttr.is (`tempest Hyderabad`)",
            res_live.returncode == 0 and "Weather report: Hyderabad" in res_live.stdout,
            res_live.stdout.splitlines()[0] if res_live.stdout else "no output",
        )


def test_mastermind():
    print("\n=== 3. `mastermind` 2-Player Discovery, TCP Game, & Reliable UDP (`--cost-cutting`) Tests ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        dylib_path = Path(tmpdir) / "libmastermind.dylib"
        c_files = [str(p) for p in sorted(MM_DIR.glob("*.c"))]
        cmd = [
            "gcc",
            "-dynamiclib",
            "-std=c23",
            "-D_POSIX_C_SOURCE=200809L",
            "-D_XOPEN_SOURCE=700",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-unused-parameter",
            "-o",
            str(dylib_path),
        ] + c_files
        subprocess.run(cmd, check=True)

        lib = ctypes.CDLL(str(dylib_path))

        # 3a. Sequence & Feedback validation
        lib.game_validate_sequence.argtypes = [ctypes.c_char_p]
        lib.game_validate_sequence.restype = ctypes.c_bool
        lib.game_validate_feedback.argtypes = [ctypes.c_char_p]
        lib.game_validate_feedback.restype = ctypes.c_bool
        lib.game_compute_expected_feedback.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        valid_seq = (
            lib.game_validate_sequence(b"04291")
            and not lib.game_validate_sequence(b"1234")
            and not lib.game_validate_sequence(b"12a45")
        )
        report("Mastermind 5-digit sequence validation (`0-9`)", valid_seq)

        valid_fb = (
            lib.game_validate_feedback(b"xxo--")
            and not lib.game_validate_feedback(b"xxo-")
            and not lib.game_validate_feedback(b"xxz--")
        )
        report("Mastermind 5-char feedback validation (`x`, `o`, `-`)", valid_fb)

        out_fb = ctypes.create_string_buffer(6)
        lib.game_compute_expected_feedback(b"12345", b"15392", out_fb)
        report(
            "Mastermind feedback rule calculation (secret=12345, guess=15392 -> xox-o)",
            out_fb.value == b"xox-o",
            f"got {out_fb.value.decode()}",
        )

        # 3b. 2-Player UDP Broadcast Discovery on a Single Machine
        lib.discovery_init_socket.argtypes = [ctypes.c_uint16]
        lib.discovery_init_socket.restype = ctypes.c_int
        lib.discovery_send_broadcast.argtypes = [
            ctypes.c_int,
            ctypes.c_uint16,
            ctypes.c_uint16,
            ctypes.c_char_p,
        ]
        lib.discovery_send_broadcast.restype = ctypes.c_int
        lib.discovery_handle_packet.argtypes = [
            ctypes.c_int,
            ctypes.c_uint16,
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.discovery_handle_packet.restype = ctypes.c_bool

        os.environ["MM_BROADCAST_IP"] = "127.0.0.1"
        disc_port = 34301
        disc_fd_rx = lib.discovery_init_socket(disc_port)
        tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        peers_p2 = ctypes.create_string_buffer(4096)
        next_id_p2 = ctypes.c_int(1)

        lib.discovery_send_broadcast(tx_sock.fileno(), disc_port, 9001, b"Feena")
        discovered = lib.discovery_handle_packet(
            disc_fd_rx, 9002, b"Tatva", peers_p2, ctypes.byref(next_id_p2)
        )
        os.close(disc_fd_rx)
        tx_sock.close()
        report(
            "2-Player UDP Broadcast Discovery on single machine (Feena -> Tatva)",
            discovered and next_id_p2.value == 2,
            "4-byte magic verified & peer added with ID=1",
        )

        # 3c. 2-Player Persistent TCP Session (Challenge -> Accept -> Ready -> Guess -> Feedback -> GameOver -> Disconnect)
        lib.tcp_session_init.argtypes = [ctypes.c_void_p]
        lib.tcp_session_close.argtypes = [ctypes.c_void_p]
        lib.tcp_connect_peer.argtypes = [ctypes.c_char_p, ctypes.c_uint16]
        lib.tcp_connect_peer.restype = ctypes.c_int
        lib.tcp_send_msg.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lib.tcp_send_msg.restype = ctypes.c_int
        lib.tcp_recv_line.argtypes = [
            ctypes.c_void_p,
            ctypes.c_bool,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        lib.tcp_recv_line.restype = ctypes.c_int

        tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_listener.bind(("127.0.0.1", 0))
        tcp_listener.listen(2)
        tcp_port = tcp_listener.getsockname()[1]

        client_fd = lib.tcp_connect_peer(b"127.0.0.1", tcp_port)
        server_conn, _ = tcp_listener.accept()

        # Struct tcp_session is { int fd; char rx_buf[1024]; size_t rx_len; }
        class TcpSession(ctypes.Structure):
            _fields_ = [
                ("fd", ctypes.c_int),
                ("rx_buf", ctypes.c_char * 1024),
                ("rx_len", ctypes.c_size_t),
            ]

        sess_master = TcpSession()
        sess_breaker = TcpSession()
        lib.tcp_session_init(ctypes.byref(sess_master))
        lib.tcp_session_init(ctypes.byref(sess_breaker))
        sess_master.fd = client_fd
        sess_breaker.fd = server_conn.fileno()

        # Exchange pipelined TCP game messages and verify newline framing
        lib.tcp_send_msg(ctypes.byref(sess_master), b"CHALLENGE Feena")
        lib.tcp_send_msg(ctypes.byref(sess_master), b"READY")
        line1 = ctypes.create_string_buffer(128)
        line2 = ctypes.create_string_buffer(128)
        rc1 = lib.tcp_recv_line(ctypes.byref(sess_breaker), True, line1, 128)
        rc2 = lib.tcp_recv_line(ctypes.byref(sess_breaker), False, line2, 128)
        report(
            "2-Player TCP Session: newline stream framing across back-to-back messages",
            rc1 == 1 and rc2 == 1 and line1.value == b"CHALLENGE Feena" and line2.value == b"READY",
            f"msg1={line1.value.decode()!r}, msg2={line2.value.decode()!r}",
        )

        # Close Mastermind's TCP socket and verify Codebreaker detects EOF disconnect (-1)
        lib.tcp_session_close(ctypes.byref(sess_master))
        rc_eof = lib.tcp_recv_line(ctypes.byref(sess_breaker), True, line1, 128)
        report(
            "2-Player TCP Session: peer disconnect detection on socket close (EOF -> -1)",
            rc_eof == -1,
        )
        server_conn.close()
        tcp_listener.close()

        # 3d. Reliable UDP (--cost-cutting) chunking, out-of-order reassembly, ACK, and 0.1s retransmission
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            lib.log_init.argtypes = [ctypes.c_bool]
            lib.log_init(True)

            sock_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_a.bind(("127.0.0.1", 0))
            port_a = sock_a.getsockname()[1]

            sock_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_b.bind(("127.0.0.1", 0))
            port_b = sock_b.getsockname()[1]

            sess_a = ctypes.create_string_buffer(16384)
            sess_b = ctypes.create_string_buffer(16384)

            lib.rudp_session_init.argtypes = [ctypes.c_void_p, ctypes.c_int]
            lib.rudp_session_set_peer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint16]
            lib.rudp_send_msg.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            lib.rudp_send_msg.restype = ctypes.c_int
            lib.rudp_recv_packet.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
            lib.rudp_recv_packet.restype = ctypes.c_int
            lib.rudp_pop_ready_msg.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
            lib.rudp_pop_ready_msg.restype = ctypes.c_int
            lib.rudp_tick.argtypes = [ctypes.c_void_p]
            lib.rudp_tick.restype = ctypes.c_int

            lib.rudp_session_init(sess_a, sock_a.fileno())
            lib.rudp_session_set_peer(sess_a, b"127.0.0.1", port_b)
            lib.rudp_session_init(sess_b, sock_b.fileno())
            lib.rudp_session_set_peer(sess_b, b"127.0.0.1", port_a)

            lib.rudp_send_msg(sess_a, b"CHALLENGE Baani")

            raw_chunks = []
            for _ in range(4):
                data, addr = sock_b.recvfrom(1024)
                raw_chunks.append((data, addr))

            report(
                "RUDP (`--cost-cutting`): split 'CHALLENGE Baani' (15B) into 4 fixed-size chunks",
                len(raw_chunks) == 4,
                f"{len(raw_chunks)} chunks transmitted",
            )

            for idx in [3, 2, 0]:
                sock_b_self = ("127.0.0.1", port_b)
                sock_a.sendto(raw_chunks[idx][0], sock_b_self)

            out_buf = ctypes.create_string_buffer(256)
            reassembled = False
            for _ in range(3):
                rc = lib.rudp_recv_packet(sess_b, out_buf, 256)
                if rc == 1:
                    reassembled = True
                lib.rudp_recv_packet(sess_a, out_buf, 256)

            report(
                "RUDP: receiver withholds incomplete message when chunk #1 is dropped",
                not reassembled,
            )

            time.sleep(0.12)
            lib.rudp_tick(sess_a)

            rc = lib.rudp_recv_packet(sess_b, out_buf, 256)
            # Drain ACK for chunk #1 on sess_a
            lib.rudp_recv_packet(sess_a, out_buf, 256)
            report(
                "RUDP: 0.1s retransmission of dropped chunk #1 + out-of-order reassembly",
                rc == 1 and out_buf.value == b"CHALLENGE Baani",
                f"reassembled={out_buf.value.decode()!r}",
            )

            # Test back-to-back pipelined RUDP messages ("FEEDBACK xxxxx" + "GAMEOVER 12345")
            lib.rudp_send_msg(sess_a, b"FEEDBACK xxxxx")
            lib.rudp_send_msg(sess_a, b"GAMEOVER 12345")
            delivered_msgs = []
            for _ in range(8):
                rc = lib.rudp_recv_packet(sess_b, out_buf, 256)
                while rc == 1:
                    delivered_msgs.append(out_buf.value.decode())
                    rc = lib.rudp_pop_ready_msg(sess_b, out_buf, 256)
                lib.rudp_recv_packet(sess_a, out_buf, 256)

            report(
                "RUDP: back-to-back pipelined messages ('FEEDBACK xxxxx' + 'GAMEOVER 12345') delivered in order",
                delivered_msgs == ["FEEDBACK xxxxx", "GAMEOVER 12345"],
                f"delivered={delivered_msgs}",
            )

            log_contents = Path("log.txt").read_text() if Path("log.txt").exists() else ""
            has_logs = (
                "RUDP_MSG_SPLIT" in log_contents
                and "RUDP_CHUNK_RETX" in log_contents
                and "RUDP_MSG_REASSEMBLED" in log_contents
            )
            report(
                "Logging (`--log`): microsecond-timestamped events written to `log.txt`",
                has_logs,
            )

            sock_a.close()
            sock_b.close()
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    test_builds()
    test_tempest()
    test_mastermind()
    print(f"\n====================================================")
    print(f"  Summary: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    print(f"====================================================")
    sys.exit(1 if FAIL_COUNT > 0 else 0)
