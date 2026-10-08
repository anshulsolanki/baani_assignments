#include "mastermind.h"

#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

void
rudp_init(struct rudp_session *r, int udp_fd)
{
  memset(r, 0, sizeof(*r));
  r->udp_fd = udp_fd;
  r->next_send_msg_id = 1;
  r->next_deliver_msg_id = 1;
}

void
rudp_set_peer(struct rudp_session *r, const char *ip, int port)
{
  memset(&r->peer_addr, 0, sizeof(r->peer_addr));
  r->peer_addr.sin_family = AF_INET;
  r->peer_addr.sin_port = htons((uint16_t)port);
  inet_pton(AF_INET, ip, &r->peer_addr.sin_addr);
  r->has_peer = 1;
  r->last_recv_ms = get_current_ms();
  r->last_ping_ms = r->last_recv_ms;
}

void
rudp_reset(struct rudp_session *r)
{
  int fd = r->udp_fd;
  memset(r, 0, sizeof(*r));
  r->udp_fd = fd;
  r->next_send_msg_id = 1;
  r->next_deliver_msg_id = 1;
}

/* Pack struct chunk_pkt fields into a portable 20-byte buffer (Doubt Doc Q27) */
void
pack_chunk(const struct chunk_pkt *pkt, char buf[MM_CHUNK_PKT_SIZE])
{
  memset(buf, 0, MM_CHUNK_PKT_SIZE);
  uint32_t net_magic = htonl(pkt->magic);
  uint16_t net_type = htons((uint16_t)pkt->type);
  uint16_t net_msg_id = htons((uint16_t)pkt->msg_id);
  uint16_t net_seq = htons((uint16_t)pkt->seq_num);
  uint16_t net_total = htons((uint16_t)pkt->total_chunks);
  uint16_t net_len = htons((uint16_t)pkt->data_len);

  memcpy(buf + 0, &net_magic, 4);
  memcpy(buf + 4, &net_type, 2);
  memcpy(buf + 6, &net_msg_id, 2);
  memcpy(buf + 8, &net_seq, 2);
  memcpy(buf + 10, &net_total, 2);
  memcpy(buf + 12, &net_len, 2);
  memcpy(buf + 16, pkt->data, MM_CHUNK_DATA_SIZE);
}

/* Unpack a 20-byte buffer back into struct chunk_pkt */
int
unpack_chunk(const char *buf, int len, struct chunk_pkt *pkt)
{
  if (len != MM_CHUNK_PKT_SIZE) {
    return -1;
  }

  uint32_t net_magic = 0;
  uint16_t net_type = 0;
  uint16_t net_msg_id = 0;
  uint16_t net_seq = 0;
  uint16_t net_total = 0;
  uint16_t net_len = 0;

  memcpy(&net_magic, buf + 0, 4);
  memcpy(&net_type, buf + 4, 2);
  memcpy(&net_msg_id, buf + 6, 2);
  memcpy(&net_seq, buf + 8, 2);
  memcpy(&net_total, buf + 10, 2);
  memcpy(&net_len, buf + 12, 2);

  pkt->magic = ntohl(net_magic);
  pkt->type = (int)ntohs(net_type);
  pkt->msg_id = (int)ntohs(net_msg_id);
  pkt->seq_num = (int)ntohs(net_seq);
  pkt->total_chunks = (int)ntohs(net_total);
  pkt->data_len = (int)ntohs(net_len);
  memcpy(pkt->data, buf + 16, MM_CHUNK_DATA_SIZE);

  if (pkt->magic != MM_MAGIC) {
    return -1;
  }
  return 0;
}

/* Send a control packet (ACK, PING, PONG, FIN) over UDP */
static void
send_control_packet(struct rudp_session *r, const struct sockaddr_in *dst,
                    int type, int msg_id, int seq_num, int total_chunks)
{
  struct chunk_pkt pkt;
  memset(&pkt, 0, sizeof(pkt));
  pkt.magic = MM_MAGIC;
  pkt.type = type;
  pkt.msg_id = msg_id;
  pkt.seq_num = seq_num;
  pkt.total_chunks = total_chunks;
  pkt.data_len = 0;

  char raw_buf[MM_CHUNK_PKT_SIZE];
  pack_chunk(&pkt, raw_buf);
  sendto(r->udp_fd, raw_buf, MM_CHUNK_PKT_SIZE, 0,
         (const struct sockaddr *)dst, sizeof(*dst));
}

/* Find a free slot in sent_list[] to store an outgoing chunk */
static struct sent_chunk *
get_free_sent_slot(struct rudp_session *r)
{
  for (int i = 0; i < 128; i++) {
    if (!r->sent_list[i].active || r->sent_list[i].acked) {
      return &r->sent_list[i];
    }
  }
  return &r->sent_list[0];
}

/* Break message into fixed-size 4-byte chunks and send all immediately */
int
rudp_send_message(struct rudp_session *r, const char *msg)
{
  if (r == NULL || r->udp_fd < 0 || !r->has_peer || msg == NULL) {
    return -1;
  }

  int len = (int)strlen(msg);
  int total_chunks = (len + MM_CHUNK_DATA_SIZE - 1) / MM_CHUNK_DATA_SIZE;
  if (total_chunks <= 0) {
    total_chunks = 1;
  }
  if (total_chunks > MM_MAX_CHUNKS) {
    return -1;
  }

  int msg_id = r->next_send_msg_id;
  r->next_send_msg_id++;
  long now = get_current_ms();

  for (int seq = 0; seq < total_chunks; seq++) {
    int offset = seq * MM_CHUNK_DATA_SIZE;
    int chunk_len = len - offset;
    if (chunk_len < 0) {
      chunk_len = 0;
    }
    if (chunk_len > MM_CHUNK_DATA_SIZE) {
      chunk_len = MM_CHUNK_DATA_SIZE;
    }

    struct sent_chunk *slot = get_free_sent_slot(r);
    memset(slot, 0, sizeof(*slot));
    slot->active = 1;
    slot->acked = 0;
    slot->last_sent_ms = now;
    slot->retries = 0;

    slot->pkt.magic = MM_MAGIC;
    slot->pkt.type = PKT_TYPE_DATA;
    slot->pkt.msg_id = msg_id;
    slot->pkt.seq_num = seq;
    slot->pkt.total_chunks = total_chunks;
    slot->pkt.data_len = chunk_len;
    if (chunk_len > 0) {
      memcpy(slot->pkt.data, msg + offset, (size_t)chunk_len);
    }

    char raw_buf[MM_CHUNK_PKT_SIZE];
    pack_chunk(&slot->pkt, raw_buf);
    sendto(r->udp_fd, raw_buf, MM_CHUNK_PKT_SIZE, 0,
           (struct sockaddr *)&r->peer_addr, sizeof(r->peer_addr));

    char log_msg[160];
    snprintf(log_msg, sizeof(log_msg),
             "UDP sent chunk %d/%d of msg %d", seq, total_chunks, msg_id);
    write_log(log_msg);
  }

  return 0;
}

/* Find or initialize a reassembly buffer for msg_id */
static struct recv_msg_buf *
get_recv_slot(struct rudp_session *r, int msg_id, int total_chunks)
{
  for (int i = 0; i < 16; i++) {
    if (r->recv_list[i].active && r->recv_list[i].msg_id == msg_id) {
      return &r->recv_list[i];
    }
  }

  int idx = msg_id % 16;
  struct recv_msg_buf *slot = &r->recv_list[idx];
  memset(slot, 0, sizeof(*slot));
  slot->active = 1;
  slot->delivered = 0;
  slot->msg_id = msg_id;
  slot->total_chunks = total_chunks;
  return slot;
}

/* If the next expected message has all its chunks, reassemble and return it */
int
rudp_get_ready_message(struct rudp_session *r, char *out_msg, int max_len)
{
  if (r == NULL) {
    return 0;
  }

  for (int i = 0; i < 16; i++) {
    struct recv_msg_buf *slot = &r->recv_list[i];
    if (slot->active && !slot->delivered &&
        slot->msg_id == r->next_deliver_msg_id &&
        slot->received_count == slot->total_chunks) {
      slot->delivered = 1;
      r->next_deliver_msg_id++;

      int pos = 0;
      for (int c = 0; c < slot->total_chunks; c++) {
        int clen = slot->chunk_len[c];
        if (pos + clen >= max_len) {
          clen = max_len - 1 - pos;
        }
        if (clen > 0) {
          memcpy(out_msg + pos, slot->chunk_data[c], (size_t)clen);
          pos += clen;
        }
      }
      out_msg[pos] = '\0';

      char log_msg[300];
      snprintf(log_msg, sizeof(log_msg), "UDP reassembled msg %d: %s",
               slot->msg_id, out_msg);
      write_log(log_msg);
      return 1;
    }
  }
  return 0;
}

/* Receive one UDP packet, send ACK if DATA, and reassemble when complete */
int
rudp_handle_incoming(struct rudp_session *r, char *out_msg, int max_len)
{
  if (r == NULL || r->udp_fd < 0) {
    return -1;
  }

  char raw_buf[MM_CHUNK_PKT_SIZE];
  struct sockaddr_in src_addr;
  socklen_t addr_len = sizeof(src_addr);

  ssize_t n = recvfrom(r->udp_fd, raw_buf, sizeof(raw_buf), 0,
                       (struct sockaddr *)&src_addr, &addr_len);
  if (n != MM_CHUNK_PKT_SIZE) {
    return 0;
  }

  struct chunk_pkt pkt;
  if (unpack_chunk(raw_buf, (int)n, &pkt) < 0) {
    return 0;
  }

  if (!r->has_peer) {
    r->peer_addr = src_addr;
    r->has_peer = 1;
  }
  r->last_recv_ms = get_current_ms();

  if (pkt.type == PKT_TYPE_DATA) {
    if (pkt.total_chunks <= 0 || pkt.total_chunks > MM_MAX_CHUNKS ||
        pkt.seq_num < 0 || pkt.seq_num >= pkt.total_chunks ||
        pkt.data_len < 0 || pkt.data_len > MM_CHUNK_DATA_SIZE) {
      return 0;
    }

    /* Send ACK referencing the chunk's sequence number */
    send_control_packet(r, &src_addr, PKT_TYPE_ACK, pkt.msg_id, pkt.seq_num,
                        pkt.total_chunks);

    char log_msg[160];
    snprintf(log_msg, sizeof(log_msg),
             "UDP received chunk %d/%d of msg %d (sent ACK)", pkt.seq_num,
             pkt.total_chunks, pkt.msg_id);
    write_log(log_msg);

    struct recv_msg_buf *slot =
        get_recv_slot(r, pkt.msg_id, pkt.total_chunks);
    if (!slot->got_chunk[pkt.seq_num]) {
      slot->got_chunk[pkt.seq_num] = 1;
      slot->chunk_len[pkt.seq_num] = pkt.data_len;
      if (pkt.data_len > 0) {
        memcpy(slot->chunk_data[pkt.seq_num], pkt.data, (size_t)pkt.data_len);
      }
      slot->received_count++;
    }

    return rudp_get_ready_message(r, out_msg, max_len);
  } else if (pkt.type == PKT_TYPE_ACK) {
    char log_msg[160];
    snprintf(log_msg, sizeof(log_msg), "UDP received ACK for chunk %d of msg %d",
             pkt.seq_num, pkt.msg_id);
    write_log(log_msg);

    for (int i = 0; i < 128; i++) {
      if (r->sent_list[i].active &&
          r->sent_list[i].pkt.msg_id == pkt.msg_id &&
          r->sent_list[i].pkt.seq_num == pkt.seq_num) {
        r->sent_list[i].acked = 1;
      }
    }
  } else if (pkt.type == PKT_TYPE_PING) {
    send_control_packet(r, &src_addr, PKT_TYPE_PONG, 0, 0, 0);
  } else if (pkt.type == PKT_TYPE_FIN) {
    write_log("UDP received disconnect packet from peer");
    return -1;
  }

  return 0;
}

/* Retransmit unacknowledged chunks after 0.1s (100 ms) and check peer timeout */
int
rudp_check_timers(struct rudp_session *r)
{
  if (r == NULL || !r->has_peer || r->udp_fd < 0) {
    return 0;
  }

  long now = get_current_ms();

  for (int i = 0; i < 128; i++) {
    struct sent_chunk *slot = &r->sent_list[i];
    if (slot->active && !slot->acked &&
        (now - slot->last_sent_ms) >= MM_RETRANSMIT_MS) {
      slot->retries++;
      if (slot->retries > 35) {
        write_log("UDP peer disconnected (max chunk retries exceeded)");
        return -1;
      }
      slot->last_sent_ms = now;

      char raw_buf[MM_CHUNK_PKT_SIZE];
      pack_chunk(&slot->pkt, raw_buf);
      sendto(r->udp_fd, raw_buf, MM_CHUNK_PKT_SIZE, 0,
             (struct sockaddr *)&r->peer_addr, sizeof(r->peer_addr));

      char log_msg[160];
      snprintf(log_msg, sizeof(log_msg),
               "UDP retransmitted chunk %d of msg %d (retry %d)",
               slot->pkt.seq_num, slot->pkt.msg_id, slot->retries);
      write_log(log_msg);
    }
  }

  if (now - r->last_ping_ms >= MM_PING_MS) {
    send_control_packet(r, &r->peer_addr, PKT_TYPE_PING, 0, 0, 0);
    r->last_ping_ms = now;
  }

  if (now - r->last_recv_ms >= MM_UDP_TIMEOUT_MS) {
    write_log("UDP peer disconnected (heartbeat timeout)");
    return -1;
  }

  return 0;
}

void
rudp_send_disconnect(struct rudp_session *r)
{
  if (r != NULL && r->has_peer && r->udp_fd >= 0) {
    send_control_packet(r, &r->peer_addr, PKT_TYPE_FIN, 0, 0, 0);
  }
}
