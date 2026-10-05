#include "mastermind.h"

#include <arpa/inet.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static int
bind_ephemeral_tcp_or_udp(bool use_udp, uint16_t *out_port)
{
  int fd = socket(AF_INET, use_udp ? SOCK_DGRAM : SOCK_STREAM, 0);
  if (fd < 0) {
    return -1;
  }

  int opt = 1;
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  addr.sin_port = htons(0);

  if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    close(fd);
    return -1;
  }

  if (!use_udp && listen(fd, 8) < 0) {
    close(fd);
    return -1;
  }

  socklen_t len = sizeof(addr);
  if (getsockname(fd, (struct sockaddr *)&addr, &len) < 0) {
    close(fd);
    return -1;
  }

  *out_port = ntohs(addr.sin_port);
  return fd;
}

static void
trim_newline(char *s)
{
  size_t len = strlen(s);
  while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
    s[--len] = '\0';
  }
}

static int
session_send(bool cost_cutting, struct tcp_session *tcp,
             struct rudp_session *rudp, const char *msg)
{
  if (cost_cutting) {
    return rudp_send_msg(rudp, msg);
  }
  return tcp_send_msg(tcp, msg);
}

static void
session_close_or_reset(bool cost_cutting, struct tcp_session *tcp,
                       struct rudp_session *rudp)
{
  if (cost_cutting) {
    rudp_session_reset(rudp);
  } else {
    tcp_session_close(tcp);
  }
}

static void
process_session_message(const char *msg, bool cost_cutting,
                        enum app_phase *phase, struct board_state *board,
                        struct tcp_session *tcp, struct rudp_session *rudp,
                        char opponent_name[MM_MAX_NAME_LEN],
                        const struct peer_entry peers[MM_MAX_PEERS])
{
  if (*phase == PHASE_LOBBY && cost_cutting &&
      strncmp(msg, VERB_CHALLENGE " ", strlen(VERB_CHALLENGE) + 1) == 0) {
    snprintf(opponent_name, MM_MAX_NAME_LEN, "%s",
             msg + strlen(VERB_CHALLENGE) + 1);
    *phase = PHASE_PROMPT_CHALLENGE_REQ;
    printf("\n%s has challenged you! Accept challenge? (yes/no): ",
           opponent_name);
    fflush(stdout);
    return;
  }

  if (*phase == PHASE_PROMPT_CHALLENGE_REQ &&
      strncmp(msg, VERB_CHALLENGE " ", strlen(VERB_CHALLENGE) + 1) == 0) {
    printf("\n%s has challenged you! Accept challenge? (yes/no): ",
           opponent_name);
    fflush(stdout);
    return;
  }

  if (*phase == PHASE_WAIT_CHALLENGE_RESP) {
    if (strcmp(msg, VERB_ACCEPT) == 0) {
      game_init_board(board, ROLE_MASTERMIND);
      *phase = PHASE_MASTER_ENTER_SECRET;
      game_render_board(board, opponent_name,
                        "Enter 5-digit master sequence (0-9): ");
    } else if (strcmp(msg, VERB_REJECT) == 0) {
      session_close_or_reset(cost_cutting, tcp, rudp);
      *phase = PHASE_LOBBY;
      discovery_render_lobby(peers);
      printf("%s declined your challenge.\n> ", opponent_name);
      fflush(stdout);
    }
    return;
  }

  if (*phase == PHASE_WAIT_MASTER_READY && strcmp(msg, VERB_READY) == 0) {
    *phase = PHASE_BREAKER_ENTER_GUESS;
    game_render_board(board, opponent_name,
                      "Your turn! Enter 5-digit guess (0-9): ");
    return;
  }

  if (*phase == PHASE_WAIT_BREAKER_GUESS &&
      strncmp(msg, VERB_GUESS " ", strlen(VERB_GUESS) + 1) == 0) {
    const char *guess = msg + strlen(VERB_GUESS) + 1;
    if (board->num_attempts < MM_MAX_ATTEMPTS &&
        game_validate_sequence(guess)) {
      int idx = board->num_attempts;
      snprintf(board->guesses[idx], sizeof(board->guesses[idx]), "%s", guess);
      board->feedback_ready[idx] = false;
      board->num_attempts++;
      *phase = PHASE_MASTER_ENTER_FEEDBACK;

      char exp_fb[MM_SEQ_LEN + 1];
      game_compute_expected_feedback(board->master_seq, guess, exp_fb);
      char prompt[160];
      snprintf(prompt, sizeof(prompt),
               "Codebreaker guessed %s. Enter 5-char feedback [x/o/-] "
               "(expected %s): ",
               guess, exp_fb);
      game_render_board(board, opponent_name, prompt);
    }
    return;
  }

  if (*phase == PHASE_WAIT_MASTER_FEEDBACK &&
      strncmp(msg, VERB_FEEDBACK " ", strlen(VERB_FEEDBACK) + 1) == 0) {
    const char *fb = msg + strlen(VERB_FEEDBACK) + 1;
    if (board->num_attempts > 0 && game_validate_feedback(fb)) {
      int idx = board->num_attempts - 1;
      snprintf(board->feedbacks[idx], sizeof(board->feedbacks[idx]), "%s", fb);
      board->feedback_ready[idx] = true;

      if (strcmp(fb, "xxxxx") == 0) {
        board->breaker_won = true;
      } else if (board->num_attempts < MM_MAX_ATTEMPTS) {
        *phase = PHASE_BREAKER_ENTER_GUESS;
        game_render_board(board, opponent_name,
                          "Your turn! Enter 5-digit guess (0-9): ");
      }
    }
    return;
  }

  if (strncmp(msg, VERB_GAMEOVER " ", strlen(VERB_GAMEOVER) + 1) == 0) {
    const char *secret = msg + strlen(VERB_GAMEOVER) + 1;
    if (game_validate_sequence(secret)) {
      snprintf(board->master_seq, sizeof(board->master_seq), "%s", secret);
      board->master_seq_known = true;
    }
    if (board->num_attempts > 0 &&
        strcmp(board->feedbacks[board->num_attempts - 1], "xxxxx") == 0) {
      board->breaker_won = true;
    }
    session_close_or_reset(cost_cutting, tcp, rudp);
    *phase = PHASE_GAME_OVER;
    char status[160];
    if (board->breaker_won) {
      snprintf(status, sizeof(status),
               "You cracked the code (%s) in %d attempts! Press Enter to "
               "return to lobby.",
               board->master_seq, board->num_attempts);
    } else {
      snprintf(status, sizeof(status),
               "Out of attempts! Master sequence was %s. Press Enter to "
               "return to lobby.",
               board->master_seq);
    }
    game_render_board(board, opponent_name, status);
    return;
  }

  if (strcmp(msg, VERB_DISCONNECT) == 0) {
    session_close_or_reset(cost_cutting, tcp, rudp);
    *phase = PHASE_PEER_DISCONNECTED;
    printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
    fflush(stdout);
  }
}

int
main(int argc, char *argv[])
{
  bool cost_cutting = false;
  bool log_enabled = false;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "--cost-cutting") == 0) {
      cost_cutting = true;
    } else if (strcmp(argv[i], "--log") == 0) {
      log_enabled = true;
    } else {
      fprintf(stderr, "Usage: %s [--cost-cutting] [--log]\n", argv[0]);
      return 1;
    }
  }

  signal(SIGPIPE, SIG_IGN);
  log_init(log_enabled);

  char my_name[MM_MAX_NAME_LEN];
  printf("Enter your player name: ");
  fflush(stdout);
  if (fgets(my_name, sizeof(my_name), stdin) == nullptr) {
    return 0;
  }
  trim_newline(my_name);
  if (my_name[0] == '\0') {
    snprintf(my_name, sizeof(my_name), "Player");
  }

  uint16_t my_game_port = 0;
  int listen_fd = bind_ephemeral_tcp_or_udp(cost_cutting, &my_game_port);
  if (listen_fd < 0) {
    perror("bind game socket");
    return 1;
  }

  int disc_fd = discovery_init_socket(MM_DISCOVERY_PORT);
  if (disc_fd < 0) {
    perror("bind discovery socket");
    close(listen_fd);
    return 1;
  }

  log_event("STARTUP name=\"%s\" game_port=%u mode=%s", my_name,
            (unsigned)my_game_port,
            cost_cutting ? "UDP(--cost-cutting)" : "TCP");

  struct peer_entry peers[MM_MAX_PEERS];
  memset(peers, 0, sizeof(peers));
  int next_peer_id = 1;

  enum app_phase phase = PHASE_LOBBY;
  struct tcp_session tcp;
  tcp_session_init(&tcp);
  struct rudp_session rudp;
  rudp_session_init(&rudp, listen_fd);
  struct board_state board;
  game_init_board(&board, ROLE_NONE);
  char opponent_name[MM_MAX_NAME_LEN] = {0};

  uint64_t last_broadcast_ms = 0;
  uint64_t last_lobby_render_ms = 0;

  discovery_send_broadcast(disc_fd, MM_DISCOVERY_PORT, my_game_port, my_name);
  last_broadcast_ms = now_ms();
  discovery_render_lobby(peers);
  last_lobby_render_ms = last_broadcast_ms;

  for (;;) {
    struct pollfd pfds[4];
    nfds_t nfds = 0;

    pfds[nfds].fd = STDIN_FILENO;
    pfds[nfds].events = POLLIN;
    pfds[nfds].revents = 0;
    nfds++;

    pfds[nfds].fd = disc_fd;
    pfds[nfds].events = POLLIN;
    pfds[nfds].revents = 0;
    nfds++;

    int listen_idx = -1;
    if (!cost_cutting && phase == PHASE_LOBBY) {
      listen_idx = (int)nfds;
      pfds[nfds].fd = listen_fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    }

    int session_idx = -1;
    if (cost_cutting) {
      session_idx = (int)nfds;
      pfds[nfds].fd = listen_fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    } else if (tcp.fd >= 0) {
      session_idx = (int)nfds;
      pfds[nfds].fd = tcp.fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    }

    /* Poll every 25 ms in --cost-cutting mode so 0.1s (100 ms) chunk
     * retransmissions fire accurately. */
    int timeout_ms = cost_cutting ? 25 : 200;
    int ready = poll(pfds, nfds, timeout_ms);
    if (ready < 0) {
      continue;
    }

    uint64_t now = now_ms();
    if (now - last_broadcast_ms >= MM_BROADCAST_INT_MS) {
      discovery_send_broadcast(disc_fd, MM_DISCOVERY_PORT, my_game_port,
                               my_name);
      last_broadcast_ms = now;
    }

    bool updated = discovery_expire_peers(peers);
    if (pfds[1].revents & POLLIN) {
      if (discovery_handle_packet(disc_fd, my_game_port, my_name, peers,
                                  &next_peer_id)) {
        updated = true;
      }
    }

    if (phase == PHASE_LOBBY &&
        (updated || (now - last_lobby_render_ms >= 1000))) {
      discovery_render_lobby(peers);
      last_lobby_render_ms = now;
    }

    /* Handle incoming TCP challenge connection */
    if (!cost_cutting && listen_idx >= 0 &&
        (pfds[listen_idx].revents & POLLIN)) {
      struct sockaddr_in cli_addr;
      socklen_t cli_len = sizeof(cli_addr);
      int cfd = accept(listen_fd, (struct sockaddr *)&cli_addr, &cli_len);
      if (cfd >= 0) {
        tcp_session_init(&tcp);
        tcp.fd = cfd;
        phase = PHASE_PROMPT_CHALLENGE_REQ;
      }
    }

    /* Handle incoming session traffic (TCP or RUDP --cost-cutting) */
    if (session_idx >= 0 &&
        (pfds[session_idx].revents & (POLLIN | POLLHUP | POLLERR))) {
      if (cost_cutting) {
        char msg[256];
        int rc = rudp_recv_packet(&rudp, msg, sizeof(msg));
        if (rc == 1) {
          process_session_message(msg, cost_cutting, &phase, &board, &tcp,
                                  &rudp, opponent_name, peers);
        } else if (rc < 0 && phase != PHASE_GAME_OVER &&
                   phase != PHASE_LOBBY) {
          rudp_session_reset(&rudp);
          phase = PHASE_PEER_DISCONNECTED;
          printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
          fflush(stdout);
        }
      } else {
        char msg[256];
        int rc = tcp_recv_line(&tcp, true, msg, sizeof(msg));
        while (rc == 1) {
          if (phase == PHASE_PROMPT_CHALLENGE_REQ &&
              strncmp(msg, VERB_CHALLENGE " ", strlen(VERB_CHALLENGE) + 1) ==
                  0) {
            snprintf(opponent_name, sizeof(opponent_name), "%s",
                     msg + strlen(VERB_CHALLENGE) + 1);
          }
          process_session_message(msg, cost_cutting, &phase, &board, &tcp,
                                  &rudp, opponent_name, peers);
          if (tcp.fd < 0) {
            break;
          }
          rc = tcp_recv_line(&tcp, false, msg, sizeof(msg));
        }

        if (rc < 0 && phase != PHASE_GAME_OVER && phase != PHASE_LOBBY) {
          tcp_session_close(&tcp);
          phase = PHASE_PEER_DISCONNECTED;
          printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
          fflush(stdout);
        }
      }
    }

    /* Check RUDP 0.1s retransmission timers and UDP peer liveness */
    if (cost_cutting && rudp.peer_known && phase != PHASE_LOBBY &&
        phase != PHASE_GAME_OVER && phase != PHASE_PEER_DISCONNECTED) {
      if (rudp_tick(&rudp) < 0) {
        rudp_session_reset(&rudp);
        phase = PHASE_PEER_DISCONNECTED;
        printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
        fflush(stdout);
      }
    }

    /* Handle user stdin input */
    if (pfds[0].revents & POLLIN) {
      char line[128];
      if (fgets(line, sizeof(line), stdin) == nullptr) {
        if (cost_cutting && rudp.peer_known) {
          rudp_send_fin(&rudp);
        }
        break;
      }
      trim_newline(line);

      if (phase == PHASE_LOBBY) {
        if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
          break;
        }
        if (strncmp(line, "challenge ", 10) == 0) {
          int target_id = atoi(line + 10);
          const struct peer_entry *p = discovery_find_peer(peers, target_id);
          if (p == nullptr) {
            printf("Invalid player ID: %d\n> ", target_id);
            fflush(stdout);
          } else if (cost_cutting) {
            rudp_session_reset(&rudp);
            rudp_session_set_peer(&rudp, p->ip, p->port);
            snprintf(opponent_name, sizeof(opponent_name), "%s", p->name);
            char out[128];
            snprintf(out, sizeof(out), "%s %s", VERB_CHALLENGE, my_name);
            session_send(cost_cutting, &tcp, &rudp, out);
            phase = PHASE_WAIT_CHALLENGE_RESP;
            printf("Waiting for %s to respond to challenge...\n",
                   opponent_name);
            fflush(stdout);
          } else {
            int cfd = tcp_connect_peer(p->ip, p->port);
            if (cfd < 0) {
              printf("Failed to connect to %s.\n> ", p->name);
              fflush(stdout);
            } else {
              tcp_session_init(&tcp);
              tcp.fd = cfd;
              snprintf(opponent_name, sizeof(opponent_name), "%s", p->name);
              char out[128];
              snprintf(out, sizeof(out), "%s %s", VERB_CHALLENGE, my_name);
              session_send(cost_cutting, &tcp, &rudp, out);
              phase = PHASE_WAIT_CHALLENGE_RESP;
              printf("Waiting for %s to respond to challenge...\n",
                     opponent_name);
              fflush(stdout);
            }
          }
        } else {
          discovery_render_lobby(peers);
        }
      } else if (phase == PHASE_PROMPT_CHALLENGE_REQ) {
        if (strcmp(line, "yes") == 0) {
          session_send(cost_cutting, &tcp, &rudp, VERB_ACCEPT);
          game_init_board(&board, ROLE_CODEBREAKER);
          phase = PHASE_WAIT_MASTER_READY;
          game_render_board(&board, opponent_name,
                            "Waiting for Mastermind to set the secret "
                            "sequence...\n");
        } else if (strcmp(line, "no") == 0) {
          session_send(cost_cutting, &tcp, &rudp, VERB_REJECT);
          if (!cost_cutting) {
            tcp_session_close(&tcp);
          } else {
            rudp_session_reset(&rudp);
          }
          phase = PHASE_LOBBY;
          discovery_render_lobby(peers);
        } else {
          printf("Please type 'yes' or 'no': ");
          fflush(stdout);
        }
      } else if (phase == PHASE_MASTER_ENTER_SECRET) {
        if (!game_validate_sequence(line)) {
          game_render_board(&board, opponent_name,
                            "Invalid sequence! Enter exactly 5 digits (0-9): ");
        } else {
          snprintf(board.master_seq, sizeof(board.master_seq), "%s", line);
          board.master_seq_known = true;
          session_send(cost_cutting, &tcp, &rudp, VERB_READY);
          phase = PHASE_WAIT_BREAKER_GUESS;
          game_render_board(&board, opponent_name,
                            "Waiting for Codebreaker's guess...\n");
        }
      } else if (phase == PHASE_BREAKER_ENTER_GUESS) {
        if (!game_validate_sequence(line)) {
          game_render_board(&board, opponent_name,
                            "Invalid guess! Enter exactly 5 digits (0-9): ");
        } else {
          int idx = board.num_attempts;
          snprintf(board.guesses[idx], sizeof(board.guesses[idx]), "%s", line);
          board.feedback_ready[idx] = false;
          board.num_attempts++;

          char out[64];
          snprintf(out, sizeof(out), "%s %s", VERB_GUESS, line);
          session_send(cost_cutting, &tcp, &rudp, out);
          phase = PHASE_WAIT_MASTER_FEEDBACK;
          game_render_board(&board, opponent_name,
                            "Waiting for Mastermind's feedback...\n");
        }
      } else if (phase == PHASE_MASTER_ENTER_FEEDBACK) {
        int idx = board.num_attempts - 1;
        char exp_fb[MM_SEQ_LEN + 1];
        game_compute_expected_feedback(board.master_seq, board.guesses[idx],
                                       exp_fb);

        if (!game_validate_feedback(line) || strcmp(line, exp_fb) != 0) {
          char prompt[160];
          snprintf(prompt, sizeof(prompt),
                   "Invalid feedback! Must be 5 chars [x/o/-] matching rules "
                   "(%s): ",
                   exp_fb);
          game_render_board(&board, opponent_name, prompt);
        } else {
          snprintf(board.feedbacks[idx], sizeof(board.feedbacks[idx]), "%s",
                   line);
          board.feedback_ready[idx] = true;

          char out[64];
          snprintf(out, sizeof(out), "%s %s", VERB_FEEDBACK, line);
          session_send(cost_cutting, &tcp, &rudp, out);

          bool won = (strcmp(line, "xxxxx") == 0);
          bool done = won || (board.num_attempts >= MM_MAX_ATTEMPTS);

          if (done) {
            board.breaker_won = won;
            snprintf(out, sizeof(out), "%s %s", VERB_GAMEOVER,
                     board.master_seq);
            session_send(cost_cutting, &tcp, &rudp, out);
            if (!cost_cutting) {
              tcp_session_close(&tcp);
            }
            phase = PHASE_GAME_OVER;

            char status[160];
            if (won) {
              snprintf(status, sizeof(status),
                       "Codebreaker cracked your sequence in %d attempts! "
                       "Press Enter to return to lobby.",
                       board.num_attempts);
            } else {
              snprintf(status, sizeof(status),
                       "Codebreaker exhausted all 12 attempts! You win! Press "
                       "Enter to return to lobby.");
            }
            game_render_board(&board, opponent_name, status);
          } else {
            phase = PHASE_WAIT_BREAKER_GUESS;
            game_render_board(&board, opponent_name,
                              "Waiting for Codebreaker's next guess...\n");
          }
        }
      } else if (phase == PHASE_GAME_OVER || phase == PHASE_PEER_DISCONNECTED) {
        session_close_or_reset(cost_cutting, &tcp, &rudp);
        phase = PHASE_LOBBY;
        discovery_render_lobby(peers);
      }
    }
  }

  if (cost_cutting && rudp.peer_known) {
    rudp_send_fin(&rudp);
  }
  tcp_session_close(&tcp);
  close(disc_fd);
  close(listen_fd);
  return 0;
}
