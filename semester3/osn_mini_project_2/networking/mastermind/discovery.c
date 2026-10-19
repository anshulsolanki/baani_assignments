#include "mastermind.h"
#include <arpa/inet.h> //converts ip addresses and nums to network formats
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

// info to broadcast
static void pack_discovery_packet(int my_game_port, const char *my_name,
                                  char buf[MM_DISC_PKT_SIZE]) {
  memset(buf, 0, MM_DISC_PKT_SIZE);
  uint32_t net_magic =
      htonl /*converts 32 bit unsigned int to network byte order */ (
          MM_MAGIC); // 4 unsigned bytes, the magic number
  uint16_t net_port = htons /*16 bit unsigned int ot netwrok byte order*/ (
      (uint16_t)my_game_port); // our game portt

  memcpy(buf, &net_magic, 4); // copying into buffer
  memcpy(buf + 4, &net_port, 2);
  strncpy(buf + 6, my_name, MM_NAME_LEN - 1);
  buf[MM_DISC_PKT_SIZE - 1] = '\0';
}

// broadcasted info we received
static int unpack_discovery_packet(const char *buf, int len, int *out_port,
                                   char out_name[MM_NAME_LEN]) {
  if (len != MM_DISC_PKT_SIZE) // invlaid packet
  {
    return -1;
  }

  uint32_t net_magic = 0;
  uint16_t net_port = 0;
  memcpy(&net_magic, buf, 4);
  memcpy(&net_port, buf + 4, 2);

  if (ntohl(net_magic) != MM_MAGIC) // if magic numbers don't match
  {
    return -1;
  }

  *out_port =
      (int)ntohs(net_port); // converting net_pot back from netwrok byte ordera
                            // and storing it into var whose address this is
  memcpy(out_name, buf + 6, MM_NAME_LEN); // getting name
  out_name[MM_NAME_LEN - 1] = '\0';       // making the name null terminated
  return 0;
}

// creating udp socket and recives datagrams
int create_discovery_socket(int port) {
  int fd = socket(AF_INET /*IPv4*/, SOCK_DGRAM /*udp socet*/,
                  0 /*os selects protocol*/);
  if (fd < 0) {
    return -1;
  }

  int opt = 1;
  setsockopt(fd, SOL_SOCKET, SO_BROADCAST /*setting*/,
             &opt /*setting enabled or disabled?*/,
             sizeof(opt)); // send broadcast packets
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt,
             sizeof(opt)); // allows addresses to be reused

  struct sockaddr_in addr; // stores adress and port
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;                // IPv4
  addr.sin_addr.s_addr = htonl(INADDR_ANY); // all local IPv4 interfaces
  addr.sin_port = htons((uint16_t)port);    // port

  if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) <
      0) // assigning local address and port to socket
  {
    close(fd);
    return -1;
  }

  return fd;
}

// broadcasting info
int send_discovery_broadcast(int udp_fd, int discovery_port, int my_game_port,
                             const char *my_name) {
  char pkt_buf[MM_DISC_PKT_SIZE];
  pack_discovery_packet(my_game_port, my_name,
                        pkt_buf); // the packet that needes to be braodcasted

  struct sockaddr_in
      bcast_addr; // holds IPv4 destination address and port number
  memset(&bcast_addr, 0, sizeof(bcast_addr));
  bcast_addr.sin_family = AF_INET;                       // IPv4
  bcast_addr.sin_port = htons((uint16_t)discovery_port); // port
  bcast_addr.sin_addr.s_addr = htonl(INADDR_BROADCAST);  // IPv4 broadcast
                                                        // address

  ssize_t sent =
      sendto(udp_fd /*udp scoket to use*/, pkt_buf /*message*/,
             MM_DISC_PKT_SIZE, 0 /*flags*/,
             (struct sockaddr *)&bcast_addr /*destination address and prot*/,
             sizeof(bcast_addr));
  if (sent != MM_DISC_PKT_SIZE) {
    return -1;
  }

  char log_msg[128];
  snprintf(log_msg /*string to print into*/, sizeof(log_msg),
           "Sent UDP broadcast: name=%s port=%d", my_name,
           my_game_port); // fiexed size printing
  write_log(log_msg);     // logging
  return 0;
}

// recieving info
int receive_discovery_packet(int udp_fd, int my_game_port, const char *my_name,
                             struct peer_entry peers[MM_MAX_PEERS],
                             int *next_id) {
  char pkt_buf[MM_DISC_PKT_SIZE];
  struct sockaddr_in src_addr;           // to stroe senders address info
  socklen_t addr_len = sizeof(src_addr); // size of address struct

  ssize_t n =
      recvfrom(udp_fd /*our listening sockett*/,
               pkt_buf /*where to write incoming bytes*/, sizeof(pkt_buf), 0,
               (struct sockaddr *)&src_addr /*info about sender*/, &addr_len);
  if (n != MM_DISC_PKT_SIZE) {
    return 0;
  }

  int peer_port = 0;           // other players game port
  char peer_name[MM_NAME_LEN]; // other payers name
  if (unpack_discovery_packet(pkt_buf, (int)n, &peer_port, peer_name) < 0) {
    return 0;
  }

  char src_ip[INET_ADDRSTRLEN]; // need sender's ip address to be able to send
                                // them info
  if (inet_ntop(AF_INET, &src_addr.sin_addr, src_ip, sizeof(src_ip)) ==
      NULL) // converts the binary IPv4 info in src_addr to readable txt
  {
    return 0;
  }

  if (peer_port == my_game_port &&
      strcmp(peer_name, my_name) == 0) // ignoring packets sent by us
  {
    return 0;
  }

  long now = get_current_ms(); // curent time
  char log_msg[160];           // logging
  snprintf(log_msg, sizeof(log_msg), "Received UDP broadcast from %s (%s:%d)",
           peer_name, src_ip, peer_port);
  write_log(log_msg);

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].port == peer_port &&
        strcmp(peers[i].ip, src_ip) ==
            0) // refreshering if is existing player in table
    {
      strncpy(peers[i].name, peer_name, MM_NAME_LEN - 1);
      peers[i].name[MM_NAME_LEN - 1] = '\0';
      peers[i].last_seen_ms = now;
      return 0; // peer already exists, no need to clear terminal screen
    }
  }

  for (int i = 0; i < MM_MAX_PEERS; i++) // if new player, adding to table
  {
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

int remove_expired_peers(
    struct peer_entry peers[MM_MAX_PEERS]) // removing players that have been
                                           // dormant for someitme
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
find_peer_by_id(struct peer_entry peers[MM_MAX_PEERS],
                int id) // returning entry of player with this id
{
  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active && peers[i].id == id) {
      return &peers[i];
    }
  }
  return NULL;
}

void print_online_players(
    struct peer_entry peers[MM_MAX_PEERS]) // curretn online players list
{
  long now = get_current_ms();
  printf("\033[2J\033[H"); //\033[2J clears the terminal screen, \033[H moves
                           //the cursor to the top-left corner
  printf("Players Online:\n");
  printf("ID       Name         IP Addr     Port    Last Seen\n");

  for (int i = 0; i < MM_MAX_PEERS; i++) {
    if (peers[i].active) // only display active players
    {
      long secs = (now - peers[i].last_seen_ms) / 1000L; // calculating last
                                                         // seen
      if (secs < 0) // time cant be negative
      {
        secs = 0;
      }
      printf("%-4d %-15s %-12s %-7d %ld s. ago\n", peers[i].id, peers[i].name,
             peers[i].ip, peers[i].port, secs); //- to left align
    }
  }
  printf("____________________________________________________\n");
  printf("> ");
  fflush(stdout);
}