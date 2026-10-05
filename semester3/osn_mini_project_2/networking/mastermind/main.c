#include "mastermind.h"

#include <arpa/inet.h>
#include <poll.h>
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
            (unsigned)my_game_port, cost_cutting ? "UDP" : "TCP");

  struct peer_entry peers[MM_MAX_PEERS];
  memset(peers, 0, sizeof(peers));
  int next_peer_id = 1;

  enum app_phase phase = PHASE_LOBBY;
  struct tcp_session tcp;
  tcp_session_init(&tcp);
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
    if (!cost_cutting && tcp.fd >= 0) {
      session_idx = (int)nfds;
      pfds[nfds].fd = tcp.fd;
      pfds[nfds].events = POLLIN;
      pfds[nfds].revents = 0;
      nfds++;
    }

    int ready = poll(pfds, nfds, 200);
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
    if (listen_idx >= 0 && (pfds[listen_idx].revents & POLLIN)) {
      struct sockaddr_in cli_addr;
      socklen_t cli_len = sizeof(cli_addr);
      int cfd = accept(listen_fd, (struct sockaddr *)&cli_addr, &cli_len);
      if (cfd >= 0) {
        tcp_session_init(&tcp);
        tcp.fd = cfd;
        phase = PHASE_PROMPT_CHALLENGE_REQ;
      }
    }

    /* Handle incoming TCP session messages */
    if (session_idx >= 0 &&
        (pfds[session_idx].revents & (POLLIN | POLLHUP | POLLERR))) {
      char msg[256];
      int rc = tcp_recv_line(&tcp, true, msg, sizeof(msg));
      while (rc == 1) {
        if (phase == PHASE_PROMPT_CHALLENGE_REQ &&
            strncmp(msg, VERB_CHALLENGE " ", strlen(VERB_CHALLENGE) + 1) == 0) {
          snprintf(opponent_name, sizeof(opponent_name), "%s",
                   msg + strlen(VERB_CHALLENGE) + 1);
          printf("\n%s has challenged you! Accept challenge? (yes/no): ",
                 opponent_name);
          fflush(stdout);
        } else if (phase == PHASE_WAIT_CHALLENGE_RESP) {
          if (strcmp(msg, VERB_ACCEPT) == 0) {
            printf("%s accepted the challenge!\n", opponent_name);
            phase = PHASE_MASTER_ENTER_SECRET;
          } else if (strcmp(msg, VERB_REJECT) == 0) {
            printf("%s rejected the challenge.\n", opponent_name);
            tcp_session_close(&tcp);
            phase = PHASE_LOBBY;
            discovery_render_lobby(peers);
          }
        }
        rc = tcp_recv_line(&tcp, false, msg, sizeof(msg));
      }

      if (rc < 0) {
        tcp_session_close(&tcp);
        phase = PHASE_LOBBY;
        discovery_render_lobby(peers);
      }
    }

    /* Handle user stdin input */
    if (pfds[0].revents & POLLIN) {
      char line[128];
      if (fgets(line, sizeof(line), stdin) == nullptr) {
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
              tcp_send_msg(&tcp, out);
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
          tcp_send_msg(&tcp, VERB_ACCEPT);
          phase = PHASE_WAIT_MASTER_READY;
        } else if (strcmp(line, "no") == 0) {
          tcp_send_msg(&tcp, VERB_REJECT);
          tcp_session_close(&tcp);
          phase = PHASE_LOBBY;
          discovery_render_lobby(peers);
        } else {
          printf("Please type 'yes' or 'no': ");
          fflush(stdout);
        }
      }
    }
  }

  tcp_session_close(&tcp);
  close(disc_fd);
  close(listen_fd);
  return 0;
}
