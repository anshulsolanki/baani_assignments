#define _DARWIN_C_SOURCE
#include "mastermind.h"

#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int
discovery_init_socket(uint16_t discovery_port)
{
  int fd = socket(AF_INET, SOCK_DGRAM, 0);
  if (fd < 0) {
    return -1;
  }

  int opt = 1;
  setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#ifdef SO_REUSEPORT
  setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
#endif

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  addr.sin_port = htons(discovery_port);

  if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    close(fd);
    return -1;
  }

  return fd;
}

int
discovery_send_broadcast(int udp_fd, uint16_t discovery_port,
                         uint16_t my_game_port, const char *my_name)
{
  struct discovery_pkt pkt;
  memset(&pkt, 0, sizeof(pkt));
  pkt.magic = htonl(MM_MAGIC);
  pkt.listen_port = htons(my_game_port);
  snprintf(pkt.name, sizeof(pkt.name), "%s", my_name);

  const char *bcast_ip = getenv("MM_BROADCAST_IP");
  if (bcast_ip == nullptr || bcast_ip[0] == '\0') {
    bcast_ip = "255.255.255.255";
  }

  struct sockaddr_in dst;
  memset(&dst, 0, sizeof(dst));
  dst.sin_family = AF_INET;
  dst.sin_port = htons(discovery_port);
  if (inet_pton(AF_INET, bcast_ip, &dst.sin_addr) <= 0) {
    dst.sin_addr.s_addr = htonl(INADDR_BROADCAST);
  }

  ssize_t n = sendto(udp_fd, &pkt, sizeof(pkt), 0, (struct sockaddr *)&dst,
                     sizeof(dst));
  if (n < 0) {
    /* Fallback to loopback so two local instances on a single offline machine
     * can still discover each other if 255.255.255.255 is unreachable. */
    inet_pton(AF_INET, "127.0.0.1", &dst.sin_addr);
    n = sendto(udp_fd, &pkt, sizeof(pkt), 0, (struct sockaddr *)&dst,
               sizeof(dst));
  }

  if (n == (ssize_t)sizeof(pkt)) {
    log_event("DISCOVERY_TX magic=0x%08X port=%u name=\"%s\"", MM_MAGIC,
              (unsigned)my_game_port, my_name);
    return 0;
  }
  return -1;
}

bool
discovery_handle_packet(int udp_fd, uint16_t my_game_port, const char *my_name,
                        struct peer_entry peers[MM_MAX_PEERS],
                        int *next_peer_id)
{
  struct discovery_pkt pkt;
  struct sockaddr_in src_addr;
  socklen_t addr_len = sizeof(src_addr);

  ssize_t n = recvfrom(udp_fd, &pkt, sizeof(pkt), 0,
                       (struct sockaddr *)&src_addr, &addr_len);
  if (n != (ssize_t)sizeof(pkt)) {
    return false;
  }

  /* Verify 4-byte magic identifier */
  if (ntohl(pkt.magic) != MM_MAGIC) {
    return false;
  }

  uint16_t peer_port = ntohs(pkt.listen_port);
  pkt.name[MM_MAX_NAME_LEN - 1] = '\0';

  /* Extract sender's IP from packet source (never from payload) */
  char src_ip[INET_ADDRSTRLEN];
  if (inet_ntop(AF_INET, &src_addr.sin_addr, src_ip, sizeof(src_ip)) ==
      nullptr) {
    return false;
  }

  /* Ignore our own broadcast packets */
  if (peer_port == my_game_port && strcmp(pkt.name, my_name) == 0) {
    return false;
  }

  uint64_t now = now_ms();
  log_event("DISCOVERY_RX src_ip=%s port=%u name=\"%s\"", src_ip,
            (unsigned)peer_port, pkt.name);

  /* Update existing peer entry if already present */
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].port == peer_port &&
        strcmp(peers[i].ip, src_ip) == 0) {
      bool changed = (strcmp(peers[i].name, pkt.name) != 0);
      snprintf(peers[i].name, sizeof(peers[i].name), "%s", pkt.name);
      peers[i].last_seen_ms = now;
      return changed;
    }
  }

  /* Add new peer entry */
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (!peers[i].active) {
      peers[i].active = true;
      peers[i].id = (*next_peer_id)++;
      snprintf(peers[i].name, sizeof(peers[i].name), "%s", pkt.name);
      snprintf(peers[i].ip, sizeof(peers[i].ip), "%s", src_ip);
      peers[i].port = peer_port;
      peers[i].last_seen_ms = now;
      log_event("PEER_ADDED id=%d name=\"%s\" ip=%s port=%u", peers[i].id,
                peers[i].name, peers[i].ip, (unsigned)peers[i].port);
      return true;
    }
  }

  return false;
}

bool
discovery_expire_peers(struct peer_entry peers[MM_MAX_PEERS])
{
  uint64_t now = now_ms();
  bool removed = false;

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && (now - peers[i].last_seen_ms) >= MM_PEER_EXPIRY_MS) {
      log_event("PEER_EXPIRED id=%d name=\"%s\" ip=%s port=%u", peers[i].id,
                peers[i].name, peers[i].ip, (unsigned)peers[i].port);
      peers[i].active = false;
      removed = true;
    }
  }
  return removed;
}

const struct peer_entry *
discovery_find_peer(const struct peer_entry peers[MM_MAX_PEERS], int id)
{
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].id == id) {
      return &peers[i];
    }
  }
  return nullptr;
}

void
discovery_render_lobby(const struct peer_entry peers[MM_MAX_PEERS])
{
  uint64_t now = now_ms();
  printf("\033[2J\033[H");
  printf("Players Online:\n");
  printf("%-6s %-16s %-15s %-7s %s\n", "ID", "Name", "IP Addr", "Port",
         "Last Seen");

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active) {
      unsigned long elapsed_sec =
          (unsigned long)((now - peers[i].last_seen_ms) / 1000ULL);
      printf("%-6d %-16s %-15s %-7u %lu s. ago\n", peers[i].id, peers[i].name,
             peers[i].ip, (unsigned)peers[i].port, elapsed_sec);
    }
  }
  printf("____________________________________________________\n");
  printf("> ");
  fflush(stdout);
}
