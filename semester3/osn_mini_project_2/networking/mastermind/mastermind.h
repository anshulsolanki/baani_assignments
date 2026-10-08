#ifndef MASTERMIND_H
#define MASTERMIND_H

#include <netinet/in.h>
#include <stddef.h>
#include <stdint.h>

/* 4-byte magic identifier ("MMND" = 0x4D4D4E44) */
#define MM_MAGIC              0x4D4D4E44U

/* Discovery settings */
#define MM_DISCOVERY_PORT     33301
#define MM_BROADCAST_MS       2000
#define MM_EXPIRY_MS          5000
#define MM_MAX_PEERS          32
#define MM_NAME_LEN           32
#define MM_DISC_PKT_SIZE      38

/* Game settings */
#define MM_SEQ_LEN            5
#define MM_MAX_ATTEMPTS       12

/* Cost-cutting (Reliable UDP) settings */
#define MM_CHUNK_DATA_SIZE    4
#define MM_CHUNK_PKT_SIZE     20
#define MM_MAX_CHUNKS         64
#define MM_RETRANSMIT_MS      100
#define MM_PING_MS            1500
#define MM_UDP_TIMEOUT_MS     5000

/* Packet types for --cost-cutting UDP state transfer */
#define PKT_TYPE_DATA         1
#define PKT_TYPE_ACK          2
#define PKT_TYPE_PING         3
#define PKT_TYPE_PONG         4
#define PKT_TYPE_FIN          5

/* Player roles */
#define ROLE_NONE             0
#define ROLE_MASTERMIND       1
#define ROLE_CODEBREAKER      2

/* Game phases */
#define PHASE_LOBBY                 0
#define PHASE_WAIT_CHALLENGE_REPLY  1
#define PHASE_ASK_CHALLENGE_ACCEPT  2
#define PHASE_MASTER_SET_SECRET     3
#define PHASE_WAIT_MASTER_SECRET    4
#define PHASE_BREAKER_GUESS         5
#define PHASE_WAIT_BREAKER_GUESS    6
#define PHASE_MASTER_FEEDBACK       7
#define PHASE_WAIT_MASTER_FEEDBACK  8
#define PHASE_GAME_OVER             9
#define PHASE_DISCONNECTED          10

/* Entry in the online players table */
struct peer_entry {
  int active;
  int id;
  char name[MM_NAME_LEN];
  char ip[INET_ADDRSTRLEN];
  int port;
  long last_seen_ms;
};

/* Board state for the 12-round Mastermind game */
struct board_state {
  int role;
  char master_seq[MM_SEQ_LEN + 1];
  int show_master_seq;
  int num_attempts;
  char guesses[MM_MAX_ATTEMPTS][MM_SEQ_LEN + 1];
  char feedbacks[MM_MAX_ATTEMPTS][MM_SEQ_LEN + 1];
  int has_feedback[MM_MAX_ATTEMPTS];
};

/* Persistent TCP session state */
struct tcp_session {
  int fd;
  char buf[1024];
  int buf_len;
};

/* Struct representing a single fixed-size chunk in --cost-cutting mode.
 * Before sending over UDP, fields are packed into a 20-byte buffer. */
struct chunk_pkt {
  uint32_t magic;
  int type;
  int msg_id;
  int seq_num;
  int total_chunks;
  int data_len;
  char data[MM_CHUNK_DATA_SIZE];
};

/* Outgoing chunk waiting for ACK in --cost-cutting mode */
struct sent_chunk {
  int active;
  int acked;
  long last_sent_ms;
  int retries;
  struct chunk_pkt pkt;
};

/* Incoming message being reassembled from chunks in --cost-cutting mode */
struct recv_msg_buf {
  int active;
  int delivered;
  int msg_id;
  int total_chunks;
  int received_count;
  int got_chunk[MM_MAX_CHUNKS];
  int chunk_len[MM_MAX_CHUNKS];
  char chunk_data[MM_MAX_CHUNKS][MM_CHUNK_DATA_SIZE];
};

/* Reliable UDP state for --cost-cutting mode */
struct rudp_session {
  int udp_fd;
  int has_peer;
  struct sockaddr_in peer_addr;
  int next_send_msg_id;
  int next_deliver_msg_id;
  long last_recv_ms;
  long last_ping_ms;
  struct sent_chunk sent_list[128];
  struct recv_msg_buf recv_list[16];
};

/* log.c */
void init_logging(int enabled);
void write_log(const char *message);
long get_current_ms(void);

/* discovery.c */
int create_discovery_socket(int port);
int send_discovery_broadcast(int udp_fd, int discovery_port, int my_game_port,
                             const char *my_name);
int receive_discovery_packet(int udp_fd, int my_game_port, const char *my_name,
                             struct peer_entry peers[MM_MAX_PEERS],
                             int *next_id);
int remove_expired_peers(struct peer_entry peers[MM_MAX_PEERS]);
struct peer_entry *find_peer_by_id(struct peer_entry peers[MM_MAX_PEERS],
                                   int id);
void print_online_players(struct peer_entry peers[MM_MAX_PEERS]);

/* game.c */
void init_board(struct board_state *b, int role);
int is_valid_sequence(const char *s);
int is_valid_feedback(const char *s);
void calculate_feedback(const char *master_seq, const char *guess,
                        char out_fb[MM_SEQ_LEN + 1]);
void print_board(const struct board_state *b);

/* net_tcp.c */
void tcp_init(struct tcp_session *s);
void tcp_close(struct tcp_session *s);
int tcp_connect_to_peer(const char *ip, int port);
int tcp_send_line(struct tcp_session *s, const char *line);
int tcp_read_line(struct tcp_session *s, int do_recv, char *out_line,
                  int max_len);

/* net_rudp.c */
void rudp_init(struct rudp_session *r, int udp_fd);
void rudp_set_peer(struct rudp_session *r, const char *ip, int port);
void rudp_reset(struct rudp_session *r);
void pack_chunk(const struct chunk_pkt *pkt, char buf[MM_CHUNK_PKT_SIZE]);
int unpack_chunk(const char *buf, int len, struct chunk_pkt *pkt);
int rudp_send_message(struct rudp_session *r, const char *msg);
int rudp_handle_incoming(struct rudp_session *r, char *out_msg, int max_len);
int rudp_get_ready_message(struct rudp_session *r, char *out_msg, int max_len);
int rudp_check_timers(struct rudp_session *r);
void rudp_send_disconnect(struct rudp_session *r);

#endif
