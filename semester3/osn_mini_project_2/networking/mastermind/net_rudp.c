#include "mastermind.h"

#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

void
rudp_session_init(struct rudp_session *r, int udp_fd)
{
  memset(r, 0, sizeof(*r));
  r->udp_fd = udp_fd;
  r->next_tx_msg_id = 1;
  r->next_rx_deliver_id = 1;
}

void
rudp_session_set_peer(struct rudp_session *r, const char *ip, uint16_t port)
{
  memset(&r->peer_addr, 0, sizeof(r->peer_addr));
  r->peer_addr.sin_family = AF_INET;
  r->peer_addr.sin_port = htons(port);
  inet_pton(AF_INET, ip, &r->peer_addr.sin_addr);
  r->peer_known = true;
  r->last_rx_ms = now_ms();
  r->last_ping_ms = r->last_rx_ms;
}

void
rudp_session_reset(struct rudp_session *r)
{
  int fd = r->udp_fd;
  memset(r, 0, sizeof(*r));
  r->udp_fd = fd;
  r->next_tx_msg_id = 1;
  r->next_rx_deliver_id = 1;
}

static struct rudp_tx_chunk *
alloc_tx_slot(struct rudp_session *r)
{
  /* Prefer a completely unused or already-acknowledged slot */
  for (size_t i = 0; i < MM_RUDP_WINDOW_SLOTS; i++) {
    if (!r->tx_window[i].in_use || r->tx_window[i].acked) {
      return &r->tx_window[i];
    }
  }
  return &r->tx_window[0];
}

/* Split msg into fixed-size struct rudp_pkt chunks and transmit all chunks
 * immediately without waiting for ACKs (pipelined transmission). */
int
rudp_send_msg(struct rudp_session *r, const char *msg)
{
  if (r == nullptr || r->udp_fd < 0 || !r->peer_known || msg == nullptr) {
    return -1;
  }

  size_t len = strlen(msg);
  uint16_t total_chunks =
      (uint16_t)((len + MM_CHUNK_DATA_SIZE - 1) / MM_CHUNK_DATA_SIZE);
  if (total_chunks == 0) {
    total_chunks = 1;
  }
  if (total_chunks > MM_MAX_CHUNKS) {
    return -1;
  }

  uint16_t msg_id = r->next_tx_msg_id++;
  uint64_t now = now_ms();

  log_event("RUDP_MSG_SPLIT msg_id=%u total_chunks=%u msg=\"%s\"",
            (unsigned)msg_id, (unsigned)total_chunks, msg);

  for (uint16_t seq = 0; seq < total_chunks; seq++) {
    size_t offset = (size_t)seq * MM_CHUNK_DATA_SIZE;
    size_t rem = (offset < len) ? (len - offset) : 0;
    uint16_t dlen =
        (uint16_t)(rem > MM_CHUNK_DATA_SIZE ? MM_CHUNK_DATA_SIZE : rem);

    struct rudp_tx_chunk *slot = alloc_tx_slot(r);
    memset(slot, 0, sizeof(*slot));
    slot->in_use = true;
    slot->acked = false;
    slot->last_sent_ms = now;
    slot->retries = 0;

    slot->pkt.magic = htonl(MM_MAGIC);
    slot->pkt.type = RUDP_PKT_DATA;
    slot->pkt.msg_id = htons(msg_id);
    slot->pkt.seq_num = htons(seq);
    slot->pkt.total_chunks = htons(total_chunks);
    slot->pkt.data_len = htons(dlen);
    if (dlen > 0) {
      memcpy(slot->pkt.data, msg + offset, dlen);
    }

    sendto(r->udp_fd, &slot->pkt, sizeof(slot->pkt), 0,
           (struct sockaddr *)&r->peer_addr, sizeof(r->peer_addr));

    log_event("RUDP_CHUNK_TX msg_id=%u seq=%u/%u len=%u data=\"%.*s\"",
              (unsigned)msg_id, (unsigned)seq, (unsigned)total_chunks,
              (unsigned)dlen, (int)dlen, slot->pkt.data);
  }

  return 0;
}

static void
send_control_pkt(struct rudp_session *r, const struct sockaddr_in *dst,
                 uint8_t type, uint16_t msg_id, uint16_t seq_num,
                 uint16_t total_chunks)
{
  struct rudp_pkt pkt;
  memset(&pkt, 0, sizeof(pkt));
  pkt.magic = htonl(MM_MAGIC);
  pkt.type = type;
  pkt.msg_id = htons(msg_id);
  pkt.seq_num = htons(seq_num);
  pkt.total_chunks = htons(total_chunks);
  pkt.data_len = htons(0);

  sendto(r->udp_fd, &pkt, sizeof(pkt), 0, (const struct sockaddr *)dst,
         sizeof(*dst));
}

static struct rudp_rx_msg *
find_or_alloc_rx_slot(struct rudp_session *r, uint16_t msg_id,
                      uint16_t total_chunks)
{
  for (size_t i = 0; i < 16; i++) {
    if (r->rx_slots[i].active && r->rx_slots[i].msg_id == msg_id) {
      return &r->rx_slots[i];
    }
  }
  size_t idx = msg_id % 16;
  struct rudp_rx_msg *slot = &r->rx_slots[idx];
  memset(slot, 0, sizeof(*slot));
  slot->active = true;
  slot->delivered = false;
  slot->msg_id = msg_id;
  slot->total_chunks = total_chunks;
  return slot;
}

int
rudp_pop_ready_msg(struct rudp_session *r, char *out_msg, size_t max_len)
{
  if (r == nullptr) {
    return 0;
  }

  for (size_t i = 0; i < 16; i++) {
    struct rudp_rx_msg *slot = &r->rx_slots[i];
    if (slot->active && !slot->delivered &&
        slot->msg_id == r->next_rx_deliver_id &&
        slot->received_count == slot->total_chunks) {
      slot->delivered = true;
      r->next_rx_deliver_id++;

      size_t pos = 0;
      for (uint16_t c = 0; c < slot->total_chunks; c++) {
        uint16_t clen = slot->chunk_len[c];
        if (pos + clen >= max_len) {
          clen = (uint16_t)(max_len - 1 - pos);
        }
        if (clen > 0) {
          memcpy(out_msg + pos, slot->chunk_data[c], clen);
          pos += clen;
        }
      }
      out_msg[pos] = '\0';
      log_event("RUDP_MSG_REASSEMBLED msg_id=%u msg=\"%s\"",
                (unsigned)slot->msg_id, out_msg);
      return 1;
    }
  }
  return 0;
}

int
rudp_recv_packet(struct rudp_session *r, char *out_msg, size_t max_len)
{
  if (r == nullptr || r->udp_fd < 0) {
    return -1;
  }

  struct rudp_pkt pkt;
  struct sockaddr_in src_addr;
  socklen_t addr_len = sizeof(src_addr);

  ssize_t n = recvfrom(r->udp_fd, &pkt, sizeof(pkt), 0,
                       (struct sockaddr *)&src_addr, &addr_len);
  if (n != (ssize_t)sizeof(pkt)) {
    return 0;
  }

  if (ntohl(pkt.magic) != MM_MAGIC) {
    return 0;
  }

  if (!r->peer_known) {
    r->peer_addr = src_addr;
    r->peer_known = true;
  }
  r->last_rx_ms = now_ms();

  uint16_t msg_id = ntohs(pkt.msg_id);
  uint16_t seq = ntohs(pkt.seq_num);
  uint16_t total = ntohs(pkt.total_chunks);
  uint16_t dlen = ntohs(pkt.data_len);

  if (pkt.type == RUDP_PKT_DATA) {
    if (total == 0 || total > MM_MAX_CHUNKS || seq >= total ||
        dlen > MM_CHUNK_DATA_SIZE) {
      return 0;
    }

    log_event("RUDP_CHUNK_RX msg_id=%u seq=%u/%u len=%u data=\"%.*s\"",
              (unsigned)msg_id, (unsigned)seq, (unsigned)total, (unsigned)dlen,
              (int)dlen, pkt.data);

    /* Immediately send per-chunk ACK */
    send_control_pkt(r, &src_addr, RUDP_PKT_ACK, msg_id, seq, total);
    log_event("RUDP_ACK_TX msg_id=%u seq=%u/%u", (unsigned)msg_id,
              (unsigned)seq, (unsigned)total);

    struct rudp_rx_msg *slot = find_or_alloc_rx_slot(r, msg_id, total);
    if (!slot->chunk_received[seq]) {
      slot->chunk_received[seq] = true;
      slot->chunk_len[seq] = dlen;
      if (dlen > 0) {
        memcpy(slot->chunk_data[seq], pkt.data, dlen);
      }
      slot->received_count++;
    }

    return rudp_pop_ready_msg(r, out_msg, max_len);
  } else if (pkt.type == RUDP_PKT_ACK) {
    log_event("RUDP_ACK_RX msg_id=%u seq=%u/%u", (unsigned)msg_id,
              (unsigned)seq, (unsigned)total);
    for (size_t i = 0; i < MM_RUDP_WINDOW_SLOTS; i++) {
      if (r->tx_window[i].in_use &&
          ntohs(r->tx_window[i].pkt.msg_id) == msg_id &&
          ntohs(r->tx_window[i].pkt.seq_num) == seq) {
        r->tx_window[i].acked = true;
      }
    }
  } else if (pkt.type == RUDP_PKT_PING) {
    send_control_pkt(r, &src_addr, RUDP_PKT_PONG, 0, 0, 0);
  } else if (pkt.type == RUDP_PKT_PONG) {
    /* Liveness already updated via r->last_rx_ms */
  } else if (pkt.type == RUDP_PKT_FIN) {
    log_event("RUDP_FIN_RX peer disconnected");
    return -1;
  }

  return 0;
}

int
rudp_tick(struct rudp_session *r)
{
  if (r == nullptr || !r->peer_known || r->udp_fd < 0) {
    return 0;
  }

  uint64_t now = now_ms();

  /* Retransmit any unacknowledged chunk after 0.1s (100 ms) */
  for (size_t i = 0; i < MM_RUDP_WINDOW_SLOTS; i++) {
    struct rudp_tx_chunk *slot = &r->tx_window[i];
    if (slot->in_use && !slot->acked &&
        (now - slot->last_sent_ms) >= MM_RETRANSMIT_MS) {
      slot->retries++;
      if (slot->retries > 35) {
        log_event("RUDP_TIMEOUT max retries exceeded on msg_id=%u seq=%u",
                  (unsigned)ntohs(slot->pkt.msg_id),
                  (unsigned)ntohs(slot->pkt.seq_num));
        return -1;
      }
      slot->last_sent_ms = now;
      sendto(r->udp_fd, &slot->pkt, sizeof(slot->pkt), 0,
             (struct sockaddr *)&r->peer_addr, sizeof(r->peer_addr));
      log_event("RUDP_CHUNK_RETX msg_id=%u seq=%u retry=%d",
                (unsigned)ntohs(slot->pkt.msg_id),
                (unsigned)ntohs(slot->pkt.seq_num), slot->retries);
    }
  }

  /* Send periodic UDP heartbeat PING to detect silent peer disconnection */
  if (now - r->last_ping_ms >= MM_RUDP_PING_MS) {
    send_control_pkt(r, &r->peer_addr, RUDP_PKT_PING, 0, 0, 0);
    r->last_ping_ms = now;
  }

  if (now - r->last_rx_ms >= MM_RUDP_TIMEOUT_MS) {
    log_event("RUDP_TIMEOUT no packets from peer for %llu ms",
              (unsigned long long)(now - r->last_rx_ms));
    return -1;
  }

  return 0;
}

void
rudp_send_fin(struct rudp_session *r)
{
  if (r != nullptr && r->peer_known && r->udp_fd >= 0) {
    send_control_pkt(r, &r->peer_addr, RUDP_PKT_FIN, 0, 0, 0);
    log_event("RUDP_FIN_TX");
  }
}
