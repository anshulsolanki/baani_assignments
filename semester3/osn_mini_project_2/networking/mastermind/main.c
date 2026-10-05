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

  uint64_t last_broadcast_ms = 0;
  uint64_t last_lobby_render_ms = 0;

  discovery_send_broadcast(disc_fd, MM_DISCOVERY_PORT, my_game_port, my_name);
  last_broadcast_ms = now_ms();
  discovery_render_lobby(peers);
  last_lobby_render_ms = last_broadcast_ms;

  for (;;) {
    struct pollfd pfds[2];
    pfds[0].fd = STDIN_FILENO;
    pfds[0].events = POLLIN;
    pfds[1].fd = disc_fd;
    pfds[1].events = POLLIN;

    int ready = poll(pfds, 2, 200);
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

    if (updated || (now - last_lobby_render_ms >= 1000)) {
      discovery_render_lobby(peers);
      last_lobby_render_ms = now;
    }

    if (pfds[0].revents & POLLIN) {
      char line[128];
      if (fgets(line, sizeof(line), stdin) == nullptr) {
        break;
      }
      trim_newline(line);
      if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
        break;
      }
      discovery_render_lobby(peers);
    }
  }

  close(disc_fd);
  close(listen_fd);
  return 0;
}
