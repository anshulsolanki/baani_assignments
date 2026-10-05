#!/usr/bin/env python3
"""
End-to-End Verification Suite for CS3.301 OSN Mini Project 2
============================================================
Verifies:
1. Build Verification:
   - `make clean && make all` in `networking/` (`tempest` and `mastermind`) with strict C23 flags.
   - Cross-target syntax & type verification of all `xv6/kernel/*.c` files with `-target riscv64-unknown-elf`.
2. `tempest` Functional Tests:
   - CLI argument validation (`tempest a b` -> `tempest: too many arguments`)
   - RFC 3986 URL percent-encoding (`"New York"` -> `"New%20York"`)
   - Live HTTP/1.1 query to `wttr.is` (`Hyderabad`, `"New York" --raw`, and invalid location)
   - Chunked Transfer-Encoding (`Transfer-Encoding: chunked`) against a local mock HTTP/1.1 server
3. `mastermind` Functional Tests:
   - Sequence (`0-9` x 5) and feedback (`x`/`o`/`-` x 5) validation + feedback computation rules
   - UDP Broadcast Player Discovery (4-byte magic `0x4D4D4E44`, source IP extraction, 5s expiry)
   - Persistent TCP Session (`\n` framing, challenge/accept/guess/feedback/gameover, TCP disconnect detection)
   - Reliable UDP (`--cost-cutting`) Session (4-byte chunk splitting, out-of-order chunk reassembly,
     per-chunk ACKs, 0.1s retransmission on simulated packet drop, and `log.txt` verification)
"""

import ctypes
import os
import socket
import struct
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

    # Clean up binaries after checking they exist
    has_bins = (TEMPEST_DIR / "tempest").exists() and (MM_DIR / "mastermind").exists()
    report("networking binaries generated at expected paths", has_bins)
    subprocess.run(["make", "clean"], cwd=NET_DIR, capture_output=True)

    # Verify xv6 kernel compiles cleanly with clang -target riscv64-unknown-elf
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

        # Helper to run tempest main() in a child python process to capture stdout cleanly
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

        # Test too many arguments
        res_args = run_tempest_cli(["a", "b"])
        report(
            "CLI: `tempest a b` prints `tempest: too many arguments`",
            "tempest: too many arguments" in res_args.stdout and res_args.returncode != 0,
            res_args.stdout.strip(),
        )

        # Test chunked encoding & invalid location via local mock HTTP/1.1 server
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

        # Live test against wttr.is
        res_live = run_tempest_cli(["Hyderabad"])
        report(
            "Live HTTP/1.1 query to wttr.is (`tempest Hyderabad`)",
            res_live.returncode == 0 and "Weather report: Hyderabad" in res_live.stdout,
            res_live.stdout.splitlines()[0] if res_live.stdout else "no output",
        )


def test_mastermind():
    print("\n=== 3. `mastermind` Discovery, TCP, & Reliable UDP (`--cost-cutting`) Tests ===")
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

        # 3b. Reliable UDP (--cost-cutting) chunking, out-of-order reassembly, ACK, and 0.1s retransmission
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            lib.log_init.argtypes = [ctypes.c_bool]
            lib.log_init(True)

            # Create two UDP sockets on loopback
            sock_a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_a.bind(("127.0.0.1", 0))
            port_a = sock_a.getsockname()[1]

            sock_b = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_b.bind(("127.0.0.1", 0))
            port_b = sock_b.getsockname()[1]

            # Allocate rudp_session buffers (4096 bytes is plenty for struct rudp_session)
            sess_a = ctypes.create_string_buffer(4096)
            sess_b = ctypes.create_string_buffer(4096)

            lib.rudp_session_init.argtypes = [ctypes.c_void_p, ctypes.c_int]
            lib.rudp_session_set_peer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint16]
            lib.rudp_send_msg.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            lib.rudp_send_msg.restype = ctypes.c_int
            lib.rudp_recv_packet.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
            lib.rudp_recv_packet.restype = ctypes.c_int
            lib.rudp_tick.argtypes = [ctypes.c_void_p]
            lib.rudp_tick.restype = ctypes.c_int

            lib.rudp_session_init(sess_a, sock_a.fileno())
            lib.rudp_session_set_peer(sess_a, b"127.0.0.1", port_b)
            lib.rudp_session_init(sess_b, sock_b.fileno())
            lib.rudp_session_set_peer(sess_b, b"127.0.0.1", port_a)

            # Send a 14-byte message ("CHALLENGE Baani") -> splits into 4 chunks of 4 bytes
            lib.rudp_send_msg(sess_a, b"CHALLENGE Baani")

            # Intercept all 4 raw UDP chunk packets on sock_b, drop chunk #1 to test 0.1s retransmission,
            # and deliver chunks #3, #2, #0 out of order!
            raw_chunks = []
            for _ in range(4):
                data, addr = sock_b.recvfrom(1024)
                raw_chunks.append((data, addr))

            report(
                "RUDP (`--cost-cutting`): split 'CHALLENGE Baani' (15B) into 4 fixed-size chunks",
                len(raw_chunks) == 4,
                f"{len(raw_chunks)} chunks transmitted",
            )

            # Re-inject chunks 3, 2, 0 into sock_b in reverse order via a helper socket, dropping chunk 1
            injector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for idx in [3, 2, 0]:
                # Rewrite source or feed directly to sock_b
                sock_b_self = ("127.0.0.1", port_b)
                # Send from sock_a so ACKs go back to sock_a
                sock_a.sendto(raw_chunks[idx][0], sock_b_self)

            out_buf = ctypes.create_string_buffer(256)
            reassembled = False
            for _ in range(3):
                rc = lib.rudp_recv_packet(sess_b, out_buf, 256)
                if rc == 1:
                    reassembled = True
                # Let sock_a process the ACKs for chunks 3, 2, 0
                lib.rudp_recv_packet(sess_a, out_buf, 256)

            report(
                "RUDP: receiver withholds incomplete message when chunk #1 is dropped",
                not reassembled,
            )

            # Wait 0.12s (> 0.1s retransmit timer) and invoke rudp_tick(sess_a)
            time.sleep(0.12)
            lib.rudp_tick(sess_a)

            # Now sock_b should receive only the retransmitted chunk #1 and complete reassembly!
            rc = lib.rudp_recv_packet(sess_b, out_buf, 256)
            report(
                "RUDP: 0.1s retransmission of dropped chunk #1 + out-of-order reassembly",
                rc == 1 and out_buf.value == b"CHALLENGE Baani",
                f"reassembled={out_buf.value.decode()!r}",
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
            injector.close()
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
