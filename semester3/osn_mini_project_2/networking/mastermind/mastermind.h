#ifndef MASTERMIND_H
#define MASTERMIND_H

#include <netinet/in.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* 4-byte protocol magic ("MMND") */
#define MM_MAGIC              0x4D4D4E44U

/* Discovery configuration */
#define MM_DISCOVERY_PORT     33301
#define MM_BROADCAST_INT_MS   2000
#define MM_PEER_EXPIRY_MS     5000
#define MM_MAX_PEERS          32
#define MM_MAX_NAME_LEN       32

/* Game configuration */
#define MM_SEQ_LEN            5
#define MM_MAX_ATTEMPTS       12

/* Reliable UDP (--cost-cutting) configuration */
#define MM_CHUNK_DATA_SIZE    4
#define MM_MAX_CHUNKS         64
#define MM_RETRANSMIT_MS      100
#define MM_RUDP_PING_MS       1500
#define MM_RUDP_TIMEOUT_MS    5000

/* Message verbs for game session (newline-delimited over TCP or reassembled RUDP) */
#define VERB_CHALLENGE        "CHALLENGE"
#define VERB_ACCEPT           "ACCEPT"
#define VERB_REJECT           "REJECT"
#define VERB_READY            "READY"
#define VERB_GUESS            "GUESS"
#define VERB_FEEDBACK         "FEEDBACK"
#define VERB_GAMEOVER         "GAMEOVER"
#define VERB_DISCONNECT       "DISCONNECT"

/* UDP broadcast discovery payload (sender IP comes from packet source, not payload) */
struct discovery_pkt {
  uint32_t magic;                  /* htonl(MM_MAGIC) */
  uint16_t listen_port;            /* htons(game_listen_port) */
  char name[MM_MAX_NAME_LEN];      /* Null-terminated player name */
};

/* Reliable UDP packet types (--cost-cutting) */
enum rudp_pkt_type {
  RUDP_PKT_DATA = 1,
  RUDP_PKT_ACK  = 2,
  RUDP_PKT_PING = 3,
  RUDP_PKT_PONG = 4,
  RUDP_PKT_FIN  = 5
};

/* Fixed-size chunk packet for --cost-cutting mode */
struct rudp_pkt {
  uint32_t magic;                  /* htonl(MM_MAGIC) */
  uint8_t type;                    /* enum rudp_pkt_type */
  uint8_t reserved;
  uint16_t msg_id;                 /* htons(message ID) */
  uint16_t seq_num;                /* htons(0 .. total_chunks - 1) */
  uint16_t total_chunks;           /* htons(total chunks in message) */
  uint16_t data_len;               /* htons(valid bytes in data[]) */
  char data[MM_CHUNK_DATA_SIZE];   /* Chunk payload bytes */
};

/* Online peer entry in discovery table */
struct peer_entry {
  bool active;
  int id;
  char name[MM_MAX_NAME_LEN];
  char ip[INET_ADDRSTRLEN];
  uint16_t port;
  uint64_t last_seen_ms;
};

/* Player role during a game */
enum player_role {
  ROLE_NONE = 0,
  ROLE_MASTERMIND,
  ROLE_CODEBREAKER
};

/* Application state machine */
enum app_phase {
  PHASE_LOBBY = 0,
  PHASE_WAIT_CHALLENGE_RESP,
  PHASE_PROMPT_CHALLENGE_REQ,
  PHASE_MASTER_ENTER_SECRET,
  PHASE_WAIT_MASTER_READY,
  PHASE_BREAKER_ENTER_GUESS,
  PHASE_WAIT_BREAKER_GUESS,
  PHASE_MASTER_ENTER_FEEDBACK,
  PHASE_WAIT_MASTER_FEEDBACK,
  PHASE_GAME_OVER,
  PHASE_PEER_DISCONNECTED
};

/* 12x5 Mastermind board state */
struct board_state {
  enum player_role role;
  char master_seq[MM_SEQ_LEN + 1];
  bool master_seq_known;
  int num_attempts;
  char guesses[MM_MAX_ATTEMPTS][MM_SEQ_LEN + 1];
  char feedbacks[MM_MAX_ATTEMPTS][MM_SEQ_LEN + 1];
  bool feedback_ready[MM_MAX_ATTEMPTS];
  bool breaker_won;
};

/* Logging & time helpers (log.c) */
void log_init(bool enabled);
void log_event(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
uint64_t now_ms(void);

/* Discovery helpers (discovery.c) */
int discovery_init_socket(uint16_t discovery_port);
int discovery_send_broadcast(int udp_fd, uint16_t discovery_port,
                             uint16_t my_game_port, const char *my_name);
bool discovery_handle_packet(int udp_fd, uint16_t my_game_port,
                             const char *my_name,
                             struct peer_entry peers[MM_MAX_PEERS],
                             int *next_peer_id);
bool discovery_expire_peers(struct peer_entry peers[MM_MAX_PEERS]);
const struct peer_entry *discovery_find_peer(
    const struct peer_entry peers[MM_MAX_PEERS], int id);
void discovery_render_lobby(const struct peer_entry peers[MM_MAX_PEERS]);

/* Persistent TCP session state and helpers (net_tcp.c) */
struct tcp_session {
  int fd;
  char rx_buf[1024];
  size_t rx_len;
};

void tcp_session_init(struct tcp_session *s);
void tcp_session_close(struct tcp_session *s);
int tcp_connect_peer(const char *ip, uint16_t port);
int tcp_send_msg(struct tcp_session *s, const char *msg);
/* Returns 1 if a complete line was extracted into out_line, 0 if more bytes
 * are needed, or -1 on EOF / disconnection. */
int tcp_recv_line(struct tcp_session *s, bool do_read, char *out_line,
                  size_t max_len);

/* Game logic & ANSI board rendering (game.c) */
void game_init_board(struct board_state *b, enum player_role role);
bool game_validate_sequence(const char *seq);
bool game_validate_feedback(const char *fb);
void game_compute_expected_feedback(const char *master_seq, const char *guess,
                                    char out_fb[MM_SEQ_LEN + 1]);
void game_render_board(const struct board_state *b, const char *opponent_name,
                       const char *status_line);

#endif /* MASTERMIND_H */
