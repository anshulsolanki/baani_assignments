#include "mastermind.h"
#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

// creating a tcp session; unused an dclean
void tcp_init(struct tcp_session *s) {
  s->fd = -1;     // no socket currently open
  s->buf_len = 0; // buffer length currently 0
  memset(s->buf, 0, sizeof(s->buf));
}

// closing a tcp session
void tcp_close(struct tcp_session *s) {
  if (s->fd >= 0) // if socket exists, closing it
  {
    close(s->fd);
    s->fd = -1;
  }
  s->buf_len = 0;
}

// establishing tcp connection to be able to play the game
int tcp_connect_to_peer(const char *ip, int port) {
  int fd = socket(AF_INET /*IPv4*/, SOCK_STREAM /*tcp*/, 0);
  if (fd < 0) {
    return -1;
  }

  struct sockaddr_in addr; // address of player u wanna connect with
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;             // IPv4
  addr.sin_port = htons((uint16_t)port); // the gaem port
  if (inet_pton /*binary ip address to readble form*/ (AF_INET, ip,
                                                       &addr.sin_addr) <= 0) {
    close(fd);
    return -1;
  }
  if (connect(fd /*socket*/,
              (struct sockaddr *)&addr /*address where u wanna connect*/,
              sizeof(addr)) < 0) // connecting
  {
    close(fd);
    return -1;
  }
  return fd;
}

// sends the message through our connection
int tcp_send_line(struct tcp_session *s, const char *line) {
  if (s == NULL /*no session*/ || s->fd < 0 /*no valid socket*/ ||
      line == NULL /*no message*/) {
    return -1;
  }

  char out_buf[512];
  int len = snprintf(
      out_buf, sizeof(out_buf), "%s\n",
      line); // adding newline at end of our messgage casue thats the boundary
  if (len < 0 || len >= (int)sizeof(out_buf)) {
    return -1;
  }

  int total_sent = 0;
  while (total_sent < len) // some part might not have gotten sent
  {
    ssize_t n = send(s->fd /*socket*/,
                     out_buf + total_sent /*where to start from in buffer*/,
                     (size_t)(len - total_sent), 0 /*no flags*/);
    if (n < 0) {
      if (errno == EINTR) // error due to interrupt?
      {
        continue;
      }
      return -1;
    }
    if (n == 0) // nothing sent, mihgt go into infinite loop
    {
      return -1;
    }
    total_sent += (int)n;
  }

  char log_msg[300]; // loggign
  snprintf(log_msg, sizeof(log_msg), "TCP sent: %s", line);
  write_log(log_msg);
  return 0;
}

// extracting message from buffer, we only need guess and score can leave
// evrything else behind
static int pop_line_from_buffer(struct tcp_session *s, char *out_line,
                                int max_len) {
  for (int i = 0; i < s->buf_len; i++) {
    if (s->buf[i] == '\n') //\n helps indentify complete message
    {
      int copy_len = i; // position of the newline
      if (copy_len > 0 &&
          s->buf[copy_len - 1] == '\r') //\r just before the newline, so not
                                        //including this in our message
      {
        copy_len--;
      }
      if (copy_len >= max_len) {
        copy_len = max_len - 1;
      }

      memcpy(out_line, s->buf, (size_t)copy_len); // copying into out_line
      out_line[copy_len] = '\0';

      int remaining =
          s->buf_len - (i + 1 /*message and newline*/); // remianing bytes?
      if (remaining > 0) {
        memmove(s->buf, s->buf + i + 1,
                (size_t)remaining); // moving to beginning of the buffer
      }
      s->buf_len = remaining;

      char log_msg[300]; // logging
      snprintf(log_msg, sizeof(log_msg), "TCP received: %s", out_line);
      write_log(log_msg);
      return 1;
    }
  }
  return 0;
}

// receiver for tcp messages
int tcp_read_line(struct tcp_session *s, int do_recv, char *out_line,
                  int max_len) {
  if (s == NULL /*session not defined*/ || s->fd < 0 /*socket not defined*/) {
    return -1;
  }
  if (pop_line_from_buffer(s, out_line,
                           max_len)) // message boundaries not conserved;
                                     // searching for message in buffer
  {
    return 1;
  }
  if (!do_recv) // allowed to call recv?
  {
    return 0;
  }

  if (s->buf_len >=
      (int)sizeof(s->buf) - 1) // if budffer almost full, reseting recorded
                               // length to make more space
  {
    s->buf_len = 0;
  }

  ssize_t n = recv(s->fd /*socket*/,
                   s->buf + s->buf_len /*start writing from,no overwrite*/,
                   sizeof(s->buf) - (size_t)s->buf_len - 1, 0 /*no flags*/);
  if (n < 0) {
    if (errno == EINTR /*signal interupt*/ || errno == EAGAIN /*waitng*/ ||
        errno == EWOULDBLOCK /*blocked*/) {
      return 0;
    }
    return -1;
  }
  if (n == 0) // closed connection detected
  {
    return -1;
  }

  s->buf_len += (int)n;
  if (pop_line_from_buffer(
          s, out_line, max_len)) // looking for message in newly recieved data
  {
    return 1;
  }
  return 0;
}