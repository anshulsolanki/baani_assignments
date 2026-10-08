#include "mastermind.h"

#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* Pack 4-byte magic, 2-byte port, and 32-byte player name into a 38-byte buffer */
static void
pack_discovery_packet(int my_game_port, const char *my_name,
                      char buf[MM_DISC_PKT_SIZE])
{
  memset(buf, 0, MM_DISC_PKT_SIZE);
  uint32_t net_magic = htonl(MM_MAGIC);
  uint16_t net_port = htons((uint16_t)my_game_port);

  memcpy(buf, &net_magic, 4);
  memcpy(buf + 4, &net_port, 2);
  strncpy(buf + 6, my_name, MM_NAME_LEN - 1);
  buf[MM_DISC_PKT_SIZE - 1] = '\0';
}

/* Unpack 38-byte discovery buffer and check the 4-byte magic identifier */
static int
unpack_discovery_packet(const char *buf, int len, int *out_port,
                        char out_name[MM_NAME_LEN])
{
  if (len != MM_DISC_PKT_SIZE) {
    return -1;
  }

  uint32_t net_magic = 0;
  uint16_t net_port = 0;
  memcpy(&net_magic, buf, 4);
  memcpy(&net_port, buf + 4, 2);

  if (ntohl(net_magic) != MM_MAGIC) {
    return -1;
  }

  *out_port = (int)ntohs(net_port);
  memcpy(out_name, buf + 6, MM_NAME_LEN);
  out_name[MM_NAME_LEN - 1] = '\0';
  return 0;
}

int
create_discovery_socket(int port)
{
  int fd = socket(AF_INET, SOCK_DGRAM, 0);
  if (fd < 0) {
    return -1;
  }

  int opt = 1;
  setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  addr.sin_port = htons((uint16_t)port);

  if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    close(fd);
    return -1;
  }

  return fd;
}

int
send_discovery_broadcast(int udp_fd, int discovery_port, int my_game_port,
                         const char *my_name)
{
  char pkt_buf[MM_DISC_PKT_SIZE];
  pack_discovery_packet(my_game_port, my_name, pkt_buf);

  struct sockaddr_in bcast_addr;
  memset(&bcast_addr, 0, sizeof(bcast_addr));
  bcast_addr.sin_family = AF_INET;
  bcast_addr.sin_port = htons((uint16_t)discovery_port);
  bcast_addr.sin_addr.s_addr = htonl(INADDR_BROADCAST);

  ssize_t sent = sendto(udp_fd, pkt_buf, MM_DISC_PKT_SIZE, 0,
                        (struct sockaddr *)&bcast_addr, sizeof(bcast_addr));
  if (sent != MM_DISC_PKT_SIZE) {
    return -1;
  }

  char log_msg[128];
  snprintf(log_msg, sizeof(log_msg), "Sent UDP broadcast: name=%s port=%d",
           my_name, my_game_port);
  write_log(log_msg);
  return 0;
}

int
receive_discovery_packet(int udp_fd, int my_game_port, const char *my_name,
                         struct peer_entry peers[MM_MAX_PEERS], int *next_id)
{
  char pkt_buf[MM_DISC_PKT_SIZE];
  struct sockaddr_in src_addr;
  socklen_t addr_len = sizeof(src_addr);

  ssize_t n = recvfrom(udp_fd, pkt_buf, sizeof(pkt_buf), 0,
                       (struct sockaddr *)&src_addr, &addr_len);
  if (n != MM_DISC_PKT_SIZE) {
    return 0;
  }

  int peer_port = 0;
  char peer_name[MM_NAME_LEN];
  if (unpack_discovery_packet(pkt_buf, (int)n, &peer_port, peer_name) < 0) {
    return 0;
  }

  /* Get sender's IP address from the UDP packet header (not payload) */
  char src_ip[INET_ADDRSTRLEN];
  if (inet_ntop(AF_INET, &src_addr.sin_addr, src_ip, sizeof(src_ip)) == NULL) {
    return 0;
  }

  /* Ignore broadcast packets sent by our own instance */
  if (peer_port == my_game_port && strcmp(peer_name, my_name) == 0) {
    return 0;
  }

  long now = get_current_ms();
  char log_msg[160];
  snprintf(log_msg, sizeof(log_msg),
           "Received UDP broadcast from %s (%s:%d)", peer_name, src_ip,
           peer_port);
  write_log(log_msg);

  /* Refresh existing player if already in the table */
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].port == peer_port &&
        strcmp(peers[i].ip, src_ip) == 0) {
      strncpy(peers[i].name, peer_name, MM_NAME_LEN - 1);
      peers[i].name[MM_NAME_LEN - 1] = '\0';
      peers[i].last_seen_ms = now;
      return 1;
    }
  }

  /* Otherwise add as a new player entry */
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (!peers[i].active) {
      peers[i].active = 1;
      peers[i].id = *next_id;
      (*next_id)++;
      strncpy(peers[i].name, peer_name, MM_NAME_LEN - 1);
      peers[i].name[MM_NAME_LEN - 1] = '\0';
      strncpy(peers[i].ip, src_ip, INET_ADDRSTRLEN - 1);
      peers[i].ip[INET_ADDRSTRLEN - 1] = '\0';
      peers[i].port = peer_port;
      peers[i].last_seen_ms = now;
      return 1;
    }
  }

  return 0;
}

int
remove_expired_peers(struct peer_entry peers[MM_MAX_PEERS])
{
  long now = get_current_ms();
  int changed = 0;

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && (now - peers[i].last_seen_ms) >= MM_EXPIRY_MS) {
      char log_msg[128];
      snprintf(log_msg, sizeof(log_msg), "Removed expired player %s (%s:%d)",
               peers[i].name, peers[i].ip, peers[i].port);
      write_log(log_msg);
      peers[i].active = 0;
      changed = 1;
    }
  }
  return changed;
}

struct peer_entry *
find_peer_by_id(struct peer_entry peers[MM_MAX_PEERS], int id)
{
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].id == id) {
      return &peers[i];
    }
  }
  return NULL;
}

void
print_online_players(struct peer_entry peers[MM_MAX_PEERS])
{
  long now = get_current_ms();
  printf("\033[2J\033[H");
  printf("Players Online:\n");
  printf("ID       Name         IP Addr     Port    Last Seen\n");

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active) {
      long secs = (now - peers[i].last_seen_ms) / 1000L;
      if (secs < 0) {
        secs = 0;
      }
      printf("%-4d %-15s %-12s %-7d %ld s. ago\n", peers[i].id, peers[i].name,
             peers[i].ip, peers[i].port, secs);
    }
  }

  printf("____________________________________________________\n");
  printf("> ");
  fflush(stdout);
}
