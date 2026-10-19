#include "mastermind.h"
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

// starting a rudp session, rudp is relaible udp. using supplied fd
void rudp_init(struct rudp_session *r, int udp_fd) {
  memset(r, 0, sizeof(*r)); // initializing th session struct to 0
  r->udp_fd = udp_fd;       // our sockets fd
  r->next_send_msg_id = 1; // id counter to keep track of whcih msg after which,
                           // so we dont loose any
  r->next_deliver_msg_id = 1;
}

// net address details of player we are playing with
void rudp_set_peer(struct rudp_session *r, const char *ip, int port) {
  memset(&r->peer_addr, 0, sizeof(r->peer_addr)); // clearin gout old values
  r->peer_addr.sin_family = AF_INET;              // IPv4
  r->peer_addr.sin_port =
      htons((uint16_t)port); // their port, conertedto network byte order
  inet_pton(
      AF_INET, ip,
      &r->peer_addr.sin_addr); // converts the readable ip into binary form
                               // required by the socket adrres struct
  r->has_peer = 1;                    // marking perr as configured
  r->last_recv_ms = get_current_ms(); // timestamp, last received a msg
  r->last_ping_ms =
      r->last_recv_ms; // timestamp, last sent a msg (for disconnecting and
                       // removing from online table)
}

// resets the session but zaves the scoket
void rudp_reset(struct rudp_session *r) {
  int fd = r->udp_fd;       // saving socket fd
  memset(r, 0, sizeof(*r)); // clearing session; rest same as rudp_init
  r->udp_fd = fd;
  r->next_send_msg_id = 1;
  r->next_deliver_msg_id = 1;
}

// converting the packet into bytes to send; different computers have diff byte
// orders and padding so converting to network byte order
void pack_chunk(const struct chunk_pkt *pkt, char buf[MM_CHUNK_PKT_SIZE]) {
  memset(buf, 0, MM_CHUNK_PKT_SIZE);      // clering the buffer
  uint32_t net_magic = htonl(pkt->magic); // magic number; msg is in our
                                          // protocol
  uint16_t net_type = htons((uint16_t)pkt->type); // packet type, eg ack, ping
  uint16_t net_msg_id = htons((uint16_t)pkt->msg_id); // which chunk
  uint16_t net_seq = htons((uint16_t)pkt->seq_num);   // chunk position
  uint16_t net_total =
      htons((uint16_t)pkt->total_chunks); // how many chunks to complete msg
  uint16_t net_len = htons((uint16_t)pkt->data_len); // total data being sent

  // coping into the buffer
  memcpy(buf + 0, &net_magic, 4);
  memcpy(buf + 4, &net_type, 2);
  memcpy(buf + 6, &net_msg_id, 2);
  memcpy(buf + 8, &net_seq, 2);
  memcpy(buf + 10, &net_total, 2);
  memcpy(buf + 12, &net_len, 2);
  memcpy(
      buf + 16, pkt->data /*arr of data*/,
      MM_CHUNK_DATA_SIZE /*capacity of payload area*/); // not a field so no
                                                        // need to convert this
}

// recieves the bytes and reconstructs the packet
int unpack_chunk(const char *buf, int len, struct chunk_pkt *pkt) {
  if (len != MM_CHUNK_PKT_SIZE) // invalid packet
  {
    return -1;
  }

  // initializing vars
  uint32_t net_magic = 0;
  uint16_t net_type = 0;
  uint16_t net_msg_id = 0;
  uint16_t net_seq = 0;
  uint16_t net_total = 0;
  uint16_t net_len = 0;

  // extracting the netwrok bytes
  memcpy(&net_magic, buf + 0, 4);
  memcpy(&net_type, buf + 4, 2);
  memcpy(&net_msg_id, buf + 6, 2);
  memcpy(&net_seq, buf + 8, 2);
  memcpy(&net_total, buf + 10, 2);
  memcpy(&net_len, buf + 12, 2);

  // converting back to normal from network byte order and putting into
  // chunk_pkt struct
  pkt->magic = ntohl(net_magic);
  pkt->type = (int)ntohs(net_type);
  pkt->msg_id = (int)ntohs(net_msg_id);
  pkt->seq_num = (int)ntohs(net_seq);
  pkt->total_chunks = (int)ntohs(net_total);
  pkt->data_len = (int)ntohs(net_len);

  memcpy(pkt->data, buf + 16,
         MM_CHUNK_DATA_SIZE); // getting the actual data in payload

  if (pkt->magic != MM_MAGIC) // if magic number doesnt match invalid packet,
                              // not from our protocol
  {
    return -1;
  }
  return 0;
}

// sends the control packets used to manage communication, acks and all
static void send_control_packet(struct rudp_session *r,
                                const struct sockaddr_in *dst, int type,
                                int msg_id, int seq_num, int total_chunks) {
  struct chunk_pkt pkt;
  memset(&pkt, 0, sizeof(pkt)); // initializng chunk
  pkt.magic = MM_MAGIC;
  pkt.type = type;
  pkt.msg_id = msg_id;
  pkt.seq_num = seq_num;
  pkt.total_chunks = total_chunks;
  pkt.data_len = 0;

  char raw_buf[MM_CHUNK_PKT_SIZE];
  pack_chunk(&pkt, raw_buf); // converting into netwrok bine=ary order
  sendto(r->udp_fd /*udp socket*/, raw_buf, MM_CHUNK_PKT_SIZE, 0,
         (const struct sockaddr *)dst /*destination address*/, sizeof(*dst));
}

// tracking sent chunks and if they were acked by sent list; it's arr which
// tells slot active, inactive, cked, retries etc
static struct sent_chunk *
get_free_sent_slot(struct rudp_session *r) { // we have sent list with 128 slots
  for (int i = 0; i < 128; i++)              // iterating throught the sent list
  {
    if (!r->sent_list[i].active ||
        r->sent_list[i].acked) // inactive slot, or already acked, then getting
                               // it's address to reuse
    {
      return &r->sent_list[i];
    }
  }
  return &r->sent_list[0]; // no slot available then 1st slot fallback; might
                           // get overwritten CAREFUL
}

// breaking message into chunks and sending
int rudp_send_message(struct rudp_session *r, const char *msg) {
  if (r == NULL /*no session pointer*/ || r->udp_fd < 0 /*no valid scket*/ ||
      !r->has_peer /*no destination peer*/ || msg == NULL /*no msg*/) {
    return -1;
  }

  int len = (int)strlen(msg);
  int total_chunks = (len + MM_CHUNK_DATA_SIZE - 1) /
                     MM_CHUNK_DATA_SIZE; // dividing into chunks; rounding up
  if (total_chunks <= 0)                 // no negative chunks
  {
    total_chunks = 1;
  }
  if (total_chunks > MM_MAX_CHUNKS) // too big msg, rejected
  {
    return -1;
  }

  int msg_id = r->next_send_msg_id; // id to identify the chunks containing
                                    // parts of this msg
  r->next_send_msg_id++;
  long now = get_current_ms(); // curretn time

  for (int seq = 0; seq < total_chunks; seq++) // sending chunks one by one
  {
    int offset = seq * MM_CHUNK_DATA_SIZE; // start of the chunk
    int chunk_len = len - offset;
    if (chunk_len < 0) {
      chunk_len = 0;
    }
    if (chunk_len > MM_CHUNK_DATA_SIZE) {
      chunk_len = MM_CHUNK_DATA_SIZE;
    }

    struct sent_chunk *slot =
        get_free_sent_slot(r);      // finding free/reusable slot
    memset(slot, 0, sizeof(*slot)); // intializing th eslot
    slot->active = 1;
    slot->acked = 0;
    slot->last_sent_ms = now;
    slot->retries = 0;
    // packet details
    slot->pkt.magic = MM_MAGIC;
    slot->pkt.type = PKT_TYPE_DATA;
    slot->pkt.msg_id = msg_id;
    slot->pkt.seq_num = seq;
    slot->pkt.total_chunks = total_chunks;
    slot->pkt.data_len = chunk_len;
    if (chunk_len > 0) {
      memcpy(slot->pkt.data, msg + offset,
             (size_t)chunk_len); // copying msg into packet
    }

    char raw_buf[MM_CHUNK_PKT_SIZE];
    pack_chunk(&slot->pkt, raw_buf); // converting to network byte order
    sendto(r->udp_fd, raw_buf, MM_CHUNK_PKT_SIZE, 0,
           (struct sockaddr *)&r->peer_addr,
           sizeof(r->peer_addr)); // sending packet

    char log_msg[160]; // logging msg
    snprintf(log_msg, sizeof(log_msg), "UDP sent chunk %d/%d of msg %d", seq,
             total_chunks, msg_id);
    write_log(log_msg);
  }
  return 0;
}

// finding or initializing slot in recieve buffer for recieving chunks of a msg
static struct recv_msg_buf *
get_recv_slot(struct rudp_session *r, int msg_id,
              int total_chunks) { // we have recieving list with 16 slots
  for (int i = 0; i < 16;
       i++) // iterating list to find place where relevant chunk is present
  {
    if (r->recv_list[i].active &&
        r->recv_list[i].msg_id == msg_id) // active lot, and already a slot
                                          // colecting chunks of this msg_id
    {
      return &r->recv_list[i]; // return the address
    }
  }
  // no address found
  int idx = msg_id % 16; // choosing random slot; might get overwritten CAREFUL
  struct recv_msg_buf *slot =
      &r->recv_list[idx];         // getting the address of the slot
  memset(slot, 0, sizeof(*slot)); // reseting this selcted slot
  slot->active = 1;
  slot->delivered = 0;
  slot->msg_id = msg_id;
  slot->total_chunks = total_chunks;
  return slot;
}

// did we recieve all chunks?
int rudp_get_ready_message(struct rudp_session *r, char *out_msg, int max_len) {
  if (r == NULL) // session pointer invlaid
  {
    return 0;
  }

  for (int i = 0; i < 16; i++) // iterating through receive list
  {
    struct recv_msg_buf *slot = &r->recv_list[i];
    if (slot->active && !slot->delivered /*msg not delivered to caller yet*/ &&
        slot->msg_id == r->next_deliver_msg_id /*correct msg*/ &&
        slot->received_count ==
            slot->total_chunks /*all chunks of msg received*/) {
      slot->delivered = 1; // msg delivered
      r->next_deliver_msg_id++;

      int pos = 0; // where next chunk should be copied in output msg
      for (int c = 0; c < slot->total_chunks; c++) // visiting all chunks
      {
        int clen = slot->chunk_len[c]; // no. of useful bytes in each chunk
        if (pos + clen >=
            max_len) // output buffer shouldnt overflow; adjusting clen
        {
          clen = max_len - 1 - pos;
        }
        if (clen > 0) // copying chunks into output
        {
          memcpy(out_msg + pos, slot->chunk_data[c], (size_t)clen);
          pos += clen;
        }
      }
      out_msg[pos] = '\0';

      char log_msg[300]; // logging
      snprintf(log_msg, sizeof(log_msg), "UDP reassembled msg %d: %s",
               slot->msg_id, out_msg);
      write_log(log_msg);
      return 1;
    }
  }
  return 0;
}

// recieving the udp packets, acking them and reassembling
int rudp_handle_incoming(struct rudp_session *r, char *out_msg, int max_len) {
  if (r == NULL || r->udp_fd < 0) // invalid session or socket
  {
    return -1;
  }
  // initializing for incoming packet
  char raw_buf[MM_CHUNK_PKT_SIZE];
  struct sockaddr_in src_addr;
  socklen_t addr_len = sizeof(src_addr);

  ssize_t n = recvfrom(r->udp_fd, raw_buf, sizeof(raw_buf), 0,
                       (struct sockaddr *)&src_addr, &addr_len);
  if (n != MM_CHUNK_PKT_SIZE) // recieved packet no the size it should be
  {
    return 0;
  }

  struct chunk_pkt pkt;
  if (unpack_chunk(raw_buf, (int)n, &pkt) <
      0) // unpacking the packet we recieved from netwrok byte to normal
  {
    return 0;
  }

  if (!r->has_peer) // if no peer yet, setting the sender as peer
  {
    r->peer_addr = src_addr;
    r->has_peer = 1;
  }
  r->last_recv_ms = get_current_ms(); // updating current recieve time

  if (pkt.type == PKT_TYPE_DATA) // handling datapacket
  {
    if (pkt.total_chunks <= 0 || pkt.total_chunks > MM_MAX_CHUNKS ||
        pkt.seq_num < 0 || pkt.seq_num >= pkt.total_chunks ||
        pkt.data_len < 0 ||
        pkt.data_len > MM_CHUNK_DATA_SIZE) // checking to be valid
    {
      return 0;
    }

    // sending ack to sender for this chunk
    send_control_packet(r, &src_addr, PKT_TYPE_ACK, pkt.msg_id, pkt.seq_num,
                        pkt.total_chunks);

    char log_msg[160]; // logging the chunk
    snprintf(log_msg, sizeof(log_msg),
             "UDP received chunk %d/%d of msg %d (sent ACK)", pkt.seq_num,
             pkt.total_chunks, pkt.msg_id);
    write_log(log_msg);

    struct recv_msg_buf *slot = get_recv_slot(
        r, pkt.msg_id,
        pkt.total_chunks); // getting slot in recv_list, one where we r
                           // collecting chunks of this msg_id, or new one if
                           // none cuch exist
    if (!slot->got_chunk
             [pkt.seq_num] /*arr to track which chunks were recieved */) {
      slot->got_chunk[pkt.seq_num] = 1; // marking as recieved
      slot->chunk_len[pkt.seq_num] =
          pkt.data_len; // whats the payload of the chunk
      if (pkt.data_len > 0) {
        memcpy(slot->chunk_data[pkt.seq_num], pkt.data,
               (size_t)pkt.data_len); // copying the payload into desired spot
      }
      slot->received_count++;
    }
    return rudp_get_ready_message(
        r, out_msg, max_len); // finding completed msgs in recv buffer, if it's
                              // next explected one sending to out msg
  } else if (pkt.type == PKT_TYPE_ACK) // if ack
  {
    char log_msg[160]; // logging the ack
    snprintf(log_msg, sizeof(log_msg),
             "UDP received ACK for chunk %d of msg %d", pkt.seq_num,
             pkt.msg_id);
    write_log(log_msg);

    for (int i = 0; i < 128; i++) // finding matching outgoing chunk in
    {
      if (r->sent_list[i].active /*active*/ &&
          r->sent_list[i].pkt.msg_id == pkt.msg_id /*msg id is acks*/ &&
          r->sent_list[i].pkt.seq_num == pkt.seq_num /*seq no. also amtches*/) {
        r->sent_list[i].acked =
            1; // update the fact thta the chunk has been acked
      }
    }
  } else if (pkt.type ==
             PKT_TYPE_PING) // ping message: checking if player is responsive
  {
    send_control_packet(r, &src_addr, PKT_TYPE_PONG, 0, 0,
                        0);            // sending pong in response
  } else if (pkt.type == PKT_TYPE_FIN) // fin, to disconnect
  {
    write_log("UDP received disconnect packet from peer"); // logging
    return -1;
  }
  return 0;
}

// retrnsmitting the unacked chunks and checking timeout for perr
int rudp_check_timers(struct rudp_session *r) {
  if (r == NULL || !r->has_peer ||
      r->udp_fd < 0) // invalid session, or no peer or no valid socket
  {
    return 0;
  }

  long now = get_current_ms(); // current time

  for (int i = 0; i < 128; i++) // checking sent buffer
  {
    struct sent_chunk *slot = &r->sent_list[i];
    if (slot->active && !slot->acked &&
        (now - slot->last_sent_ms) >=
            MM_RETRANSMIT_MS) // some chunk which hasnt been acked past time
                              // needs retransmitting
    {
      slot->retries++;
      if (slot->retries > 35) // error, disconnection based on retry limit
      {
        write_log(
            "UDP peer disconnected (max chunk retries exceeded)"); // loggigng
        return -1;
      }
      slot->last_sent_ms = now; // updating time

      char raw_buf[MM_CHUNK_PKT_SIZE];
      pack_chunk(&slot->pkt, raw_buf);
      sendto(r->udp_fd, raw_buf, MM_CHUNK_PKT_SIZE, 0,
             (struct sockaddr *)&r->peer_addr,
             sizeof(r->peer_addr)); // repacking, resending chunk

      char log_msg[160]; // logging
      snprintf(log_msg, sizeof(log_msg),
               "UDP retransmitted chunk %d of msg %d (retry %d)",
               slot->pkt.seq_num, slot->pkt.msg_id, slot->retries);
      write_log(log_msg);
    }
  }

  if (now - r->last_ping_ms >=
      MM_PING_MS) // periodic pings to check if sill connected
  {
    send_control_packet(r, &r->peer_addr, PKT_TYPE_PING, 0, 0, 0);
    r->last_ping_ms = now; // updating time
  }

  if (now - r->last_recv_ms >= MM_UDP_TIMEOUT_MS) // ping due, pong not recived
  {
    write_log("UDP peer disconnected (heartbeat timeout)"); // logging
                                                            // disconnect
    return -1;
  }
  return 0;
}

// sending fin to disconnect
void rudp_send_disconnect(struct rudp_session *r) {
  if (r != NULL && r->has_peer &&
      r->udp_fd >= 0) // valid session, valid peer and valid socket
  {
    send_control_packet(r, &r->peer_addr, PKT_TYPE_FIN, 0, 0, 0); // sending fin
  }
}