#include "mastermind.h"

#include <arpa/inet.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* Bind a listening TCP socket (or UDP socket in --cost-cutting mode) on an
 * available port and return the port number via *out_port. */
static int
create_game_socket(int cost_cutting, int *out_port)
{
  int type = cost_cutting ? SOCK_DGRAM : SOCK_STREAM;
  int fd = socket(AF_INET, type, 0);
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

  if (!cost_cutting) {
    if (listen(fd, 5) < 0) {
      close(fd);
      return -1;
    }
  }

  socklen_t len = sizeof(addr);
  if (getsockname(fd, (struct sockaddr *)&addr, &len) < 0) {
    close(fd);
    return -1;
  }

  *out_port = (int)ntohs(addr.sin_port);
  return fd;
}

static void
strip_newline(char *s)
{
  int len = (int)strlen(s);
  while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
    s[len - 1] = '\0';
    len--;
  }
}

static int
send_game_msg(int cost_cutting, struct tcp_session *tcp,
              struct rudp_session *rudp, const char *msg)
{
  if (cost_cutting) {
    return rudp_send_message(rudp, msg);
  }
  return tcp_send_line(tcp, msg);
}

static void
close_game_session(int cost_cutting, struct tcp_session *tcp,
                   struct rudp_session *rudp)
{
  if (cost_cutting) {
    rudp_reset(rudp);
  } else {
    tcp_close(tcp);
  }
}

static void
handle_game_message(const char *msg, int cost_cutting, int *phase,
                    struct board_state *board, struct tcp_session *tcp,
                    struct rudp_session *rudp, char opponent_name[MM_NAME_LEN],
                    struct peer_entry peers[MM_MAX_PEERS])
{
  /* Incoming CHALLENGE <name> */
  if (strncmp(msg, "CHALLENGE ", 10) == 0) {
    if (*phase == PHASE_LOBBY || *phase == PHASE_ASK_CHALLENGE_ACCEPT) {
      strncpy(opponent_name, msg + 10, MM_NAME_LEN - 1);
      opponent_name[MM_NAME_LEN - 1] = '\0';
      *phase = PHASE_ASK_CHALLENGE_ACCEPT;
      printf("\nChallenge from %s! Type 'yes' to accept or 'no' to reject: ",
             opponent_name);
      fflush(stdout);
    }
    return;
  }

  /* Response to our challenge: ACCEPT or REJECT */
  if (*phase == PHASE_WAIT_CHALLENGE_REPLY) {
    if (strcmp(msg, "ACCEPT") == 0) {
      init_board(board, ROLE_MASTERMIND);
      *phase = PHASE_MASTER_SET_SECRET;
      print_board(board);
      printf("Enter 5-digit master sequence: ");
      fflush(stdout);
    } else if (strcmp(msg, "REJECT") == 0) {
      close_game_session(cost_cutting, tcp, rudp);
      *phase = PHASE_LOBBY;
      print_online_players(peers);
    }
    return;
  }

  /* Mastermind has set the secret sequence: READY */
  if (*phase == PHASE_WAIT_MASTER_SECRET && strcmp(msg, "READY") == 0) {
    *phase = PHASE_BREAKER_GUESS;
    print_board(board);
    printf("Enter 5-digit attempt: ");
    fflush(stdout);
    return;
  }

  /* Codebreaker sent an attempt: GUESS <5digits> */
  if (*phase == PHASE_WAIT_BREAKER_GUESS && strncmp(msg, "GUESS ", 6) == 0) {
    const char *guess = msg + 6;
    if (board->num_attempts < MM_MAX_ATTEMPTS && is_valid_sequence(guess)) {
      int idx = board->num_attempts;
      strcpy(board->guesses[idx], guess);
      board->has_feedback[idx] = 0;
      board->num_attempts++;
      *phase = PHASE_MASTER_FEEDBACK;

      char expected[MM_SEQ_LEN + 1];
      calculate_feedback(board->master_seq, guess, expected);
      print_board(board);
      printf("Enter feedback for %s (expected %s): ", guess, expected);
      fflush(stdout);
    }
    return;
  }

  /* Mastermind sent feedback: FEEDBACK <5chars> */
  if (*phase == PHASE_WAIT_MASTER_FEEDBACK &&
      strncmp(msg, "FEEDBACK ", 9) == 0) {
    const char *fb = msg + 9;
    if (board->num_attempts > 0 && is_valid_feedback(fb)) {
      int idx = board->num_attempts - 1;
      strcpy(board->feedbacks[idx], fb);
      board->has_feedback[idx] = 1;

      if (strcmp(fb, "xxxxx") != 0 && board->num_attempts < MM_MAX_ATTEMPTS) {
        *phase = PHASE_BREAKER_GUESS;
        print_board(board);
        printf("Enter 5-digit attempt: ");
        fflush(stdout);
      } else {
        print_board(board);
      }
    }
    return;
  }

  /* Game ended: GAMEOVER <master_seq> */
  if (strncmp(msg, "GAMEOVER ", 9) == 0) {
    const char *secret = msg + 9;
    if (is_valid_sequence(secret)) {
      strcpy(board->master_seq, secret);
      board->show_master_seq = 1;
    }
    close_game_session(cost_cutting, tcp, rudp);
    *phase = PHASE_GAME_OVER;
    print_board(board);
    printf("Game over! Press Enter to return to homepage.\n");
    fflush(stdout);
    return;
  }
}

int
main(int argc, char *argv[])
{
  int cost_cutting = 0;
  int log_enabled = 0;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "--cost-cutting") == 0) {
      cost_cutting = 1;
    } else if (strcmp(argv[i], "--log") == 0) {
      log_enabled = 1;
    } else {
      printf("Usage: %s [--cost-cutting] [--log]\n", argv[0]);
      return 1;
    }
  }

  signal(SIGPIPE, SIG_IGN);
  init_logging(log_enabled);

  char my_name[MM_NAME_LEN];
  printf("Enter your name: ");
  fflush(stdout);
  if (fgets(my_name, sizeof(my_name), stdin) == NULL) {
    return 0;
  }
  strip_newline(my_name);
  if (my_name[0] == '\0') {
    strcpy(my_name, "Player");
  }

  int my_game_port = 0;
  int game_listen_fd = create_game_socket(cost_cutting, &my_game_port);
  if (game_listen_fd < 0) {
    perror("create_game_socket");
    return 1;
  }

  int disc_fd = create_discovery_socket(MM_DISCOVERY_PORT);
  if (disc_fd < 0) {
    perror("create_discovery_socket");
    close(game_listen_fd);
    return 1;
  }

  char start_log[128];
  snprintf(start_log, sizeof(start_log),
           "Started mastermind as %s on port %d", my_name, my_game_port);
  write_log(start_log);

  struct peer_entry peers[MM_MAX_PEERS];
  memset(peers, 0, sizeof(peers));
  int next_peer_id = 1;

  int phase = PHASE_LOBBY;
  struct tcp_session tcp;
  tcp_init(&tcp);
  struct rudp_session rudp;
  rudp_init(&rudp, game_listen_fd);
  struct board_state board;
  init_board(&board, ROLE_NONE);
  char opponent_name[MM_NAME_LEN] = "";

  long last_bcast_ms = get_current_ms();
  send_discovery_broadcast(disc_fd, MM_DISCOVERY_PORT, my_game_port, my_name);
  print_online_players(peers);

  while (1) {
    struct pollfd pfds[4];
    int nfds = 0;

    /* 0: Standard input */
    pfds[nfds].fd = STDIN_FILENO;
    pfds[nfds].events = POLLIN;
    pfds[nfds].revents = 0;
    nfds++;

    /* 1: UDP broadcast discovery socket */
    pfds[nfds].fd = disc_fd;
    pfds[nfds].events = POLLIN;
    pfds[nfds].revents = 0;
    nfds++;

    /* 2: Listening TCP socket (when in lobby and not in --cost-cutting mode) */
    int listen_idx = -1;
    if (!cost_cutting && phase == PHASE_LOBBY) {
      listen_idx = nfds;
      pfds[nfds].fd = game_listen_fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    }

    /* 3: Active game session socket (TCP or UDP --cost-cutting) */
    int session_idx = -1;
    if (cost_cutting) {
      session_idx = nfds;
      pfds[nfds].fd = game_listen_fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    } else if (tcp.fd >= 0) {
      session_idx = nfds;
      pfds[nfds].fd = tcp.fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    }

    int timeout_ms = cost_cutting ? 25 : 200;
    int ready = poll(pfds, (nfds_t)nfds, timeout_ms);
    if (ready < 0) {
      continue;
    }

    long now = get_current_ms();

    /* Broadcast our presence every 2 seconds */
    if (now - last_bcast_ms >= MM_BROADCAST_MS) {
      send_discovery_broadcast(disc_fd, MM_DISCOVERY_PORT, my_game_port,
                               my_name);
      last_bcast_ms = now;
    }

    /* Expire peers not seen for 5 seconds and process incoming broadcasts */
    int list_changed = remove_expired_peers(peers);
    if (pfds[1].revents & POLLIN) {
      if (receive_discovery_packet(disc_fd, my_game_port, my_name, peers,
                                   &next_peer_id)) {
        list_changed = 1;
      }
    }

    /* Clear and reprint the discovery list whenever a broadcast arrives or expires */
    if (phase == PHASE_LOBBY && list_changed) {
      print_online_players(peers);
    }

    /* Accept incoming TCP connection for a challenge */
    if (!cost_cutting && listen_idx >= 0 &&
        (pfds[listen_idx].revents & POLLIN)) {
      struct sockaddr_in cli_addr;
      socklen_t cli_len = sizeof(cli_addr);
      int cfd = accept(game_listen_fd, (struct sockaddr *)&cli_addr, &cli_len);
      if (cfd >= 0) {
        tcp_init(&tcp);
        tcp.fd = cfd;
        phase = PHASE_ASK_CHALLENGE_ACCEPT;
      }
    }

    /* Read incoming game messages over TCP or Reliable UDP */
    if (session_idx >= 0 &&
        (pfds[session_idx].revents & (POLLIN | POLLHUP | POLLERR))) {
      if (cost_cutting) {
        char msg[256];
        int rc = rudp_handle_incoming(&rudp, msg, sizeof(msg));
        while (rc == 1) {
          handle_game_message(msg, cost_cutting, &phase, &board, &tcp, &rudp,
                              opponent_name, peers);
          if (!rudp.has_peer) {
            break;
          }
          rc = rudp_get_ready_message(&rudp, msg, sizeof(msg));
        }
        if (rc < 0 && phase != PHASE_LOBBY && phase != PHASE_GAME_OVER) {
          rudp_reset(&rudp);
          phase = PHASE_DISCONNECTED;
          printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
          fflush(stdout);
        }
      } else {
        char msg[256];
        int rc = tcp_read_line(&tcp, 1, msg, sizeof(msg));
        while (rc == 1) {
          handle_game_message(msg, cost_cutting, &phase, &board, &tcp, &rudp,
                              opponent_name, peers);
          if (tcp.fd < 0) {
            break;
          }
          rc = tcp_read_line(&tcp, 0, msg, sizeof(msg));
        }
        if (rc < 0 && phase != PHASE_LOBBY && phase != PHASE_GAME_OVER) {
          tcp_close(&tcp);
          phase = PHASE_DISCONNECTED;
          printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
          fflush(stdout);
        }
      }
    }

    /* Check 0.1s chunk retransmission timer and peer timeout in --cost-cutting mode */
    if (cost_cutting && rudp.has_peer && phase != PHASE_LOBBY &&
        phase != PHASE_GAME_OVER && phase != PHASE_DISCONNECTED) {
      if (rudp_check_timers(&rudp) < 0) {
        rudp_reset(&rudp);
        phase = PHASE_DISCONNECTED;
        printf("\n%s disconnected. Press enter to go home.\n", opponent_name);
        fflush(stdout);
      }
    }

    /* Handle keyboard input from player */
    if (pfds[0].revents & POLLIN) {
      char line[128];
      if (fgets(line, sizeof(line), stdin) == NULL) {
        if (cost_cutting && rudp.has_peer) {
          rudp_send_disconnect(&rudp);
        }
        break;
      }
      strip_newline(line);

      if (phase == PHASE_LOBBY) {
        if (strncmp(line, "challenge ", 10) == 0) {
          int id = atoi(line + 10);
          struct peer_entry *p = find_peer_by_id(peers, id);
          if (p == NULL) {
            printf("Player ID %d not found.\n> ", id);
            fflush(stdout);
          } else {
            strncpy(opponent_name, p->name, MM_NAME_LEN - 1);
            opponent_name[MM_NAME_LEN - 1] = '\0';

            char req_msg[64];
            snprintf(req_msg, sizeof(req_msg), "CHALLENGE %s", my_name);

            if (cost_cutting) {
              rudp_reset(&rudp);
              rudp_set_peer(&rudp, p->ip, p->port);
              send_game_msg(cost_cutting, &tcp, &rudp, req_msg);
              phase = PHASE_WAIT_CHALLENGE_REPLY;
              printf("Challenge sent to %s. Waiting for response...\n",
                     opponent_name);
              fflush(stdout);
            } else {
              int cfd = tcp_connect_to_peer(p->ip, p->port);
              if (cfd < 0) {
                printf("Could not connect to %s.\n> ", opponent_name);
                fflush(stdout);
              } else {
                tcp_init(&tcp);
                tcp.fd = cfd;
                send_game_msg(cost_cutting, &tcp, &rudp, req_msg);
                phase = PHASE_WAIT_CHALLENGE_REPLY;
                printf("Challenge sent to %s. Waiting for response...\n",
                       opponent_name);
                fflush(stdout);
              }
            }
          }
        } else {
          print_online_players(peers);
        }
      } else if (phase == PHASE_ASK_CHALLENGE_ACCEPT) {
        if (strcmp(line, "yes") == 0) {
          send_game_msg(cost_cutting, &tcp, &rudp, "ACCEPT");
          init_board(&board, ROLE_CODEBREAKER);
          phase = PHASE_WAIT_MASTER_SECRET;
          print_board(&board);
          printf("Waiting for %s to set the master sequence...\n",
                 opponent_name);
          fflush(stdout);
        } else if (strcmp(line, "no") == 0) {
          send_game_msg(cost_cutting, &tcp, &rudp, "REJECT");
          close_game_session(cost_cutting, &tcp, &rudp);
          phase = PHASE_LOBBY;
          print_online_players(peers);
        } else {
          printf("Please type 'yes' or 'no': ");
          fflush(stdout);
        }
      } else if (phase == PHASE_MASTER_SET_SECRET) {
        if (!is_valid_sequence(line)) {
          printf("Invalid sequence! Enter 5 digits (0-9): ");
          fflush(stdout);
        } else {
          strcpy(board.master_seq, line);
          board.show_master_seq = 1;
          send_game_msg(cost_cutting, &tcp, &rudp, "READY");
          phase = PHASE_WAIT_BREAKER_GUESS;
          print_board(&board);
          printf("Waiting for %s's attempt...\n", opponent_name);
          fflush(stdout);
        }
      } else if (phase == PHASE_BREAKER_GUESS) {
        if (!is_valid_sequence(line)) {
          printf("Invalid sequence! Enter 5 digits (0-9): ");
          fflush(stdout);
        } else {
          int idx = board.num_attempts;
          strcpy(board.guesses[idx], line);
          board.has_feedback[idx] = 0;
          board.num_attempts++;

          char out_msg[32];
          snprintf(out_msg, sizeof(out_msg), "GUESS %s", line);
          send_game_msg(cost_cutting, &tcp, &rudp, out_msg);
          phase = PHASE_WAIT_MASTER_FEEDBACK;
          print_board(&board);
          printf("Waiting for %s's feedback...\n", opponent_name);
          fflush(stdout);
        }
      } else if (phase == PHASE_MASTER_FEEDBACK) {
        int idx = board.num_attempts - 1;
        char expected[MM_SEQ_LEN + 1];
        calculate_feedback(board.master_seq, board.guesses[idx], expected);

        if (!is_valid_feedback(line)) {
          printf("Invalid feedback! Use 5 chars from {x, o, -} (expected %s): ",
                 expected);
          fflush(stdout);
        } else {
          strcpy(board.feedbacks[idx], line);
          board.has_feedback[idx] = 1;

          char fb_msg[32];
          snprintf(fb_msg, sizeof(fb_msg), "FEEDBACK %s", line);
          send_game_msg(cost_cutting, &tcp, &rudp, fb_msg);

          if (strcmp(line, "xxxxx") == 0 ||
              board.num_attempts >= MM_MAX_ATTEMPTS) {
            char end_msg[32];
            snprintf(end_msg, sizeof(end_msg), "GAMEOVER %s", board.master_seq);
            send_game_msg(cost_cutting, &tcp, &rudp, end_msg);
            if (!cost_cutting) {
              tcp_close(&tcp);
            }
            phase = PHASE_GAME_OVER;
            print_board(&board);
            printf("Game over! Press Enter to return to homepage.\n");
            fflush(stdout);
          } else {
            phase = PHASE_WAIT_BREAKER_GUESS;
            print_board(&board);
            printf("Waiting for %s's next attempt...\n", opponent_name);
            fflush(stdout);
          }
        }
      } else if (phase == PHASE_GAME_OVER || phase == PHASE_DISCONNECTED) {
        close_game_session(cost_cutting, &tcp, &rudp);
        phase = PHASE_LOBBY;
        print_online_players(peers);
      }
    }
  }

  tcp_close(&tcp);
  close(game_listen_fd);
  close(disc_fd);
  return 0;
}
