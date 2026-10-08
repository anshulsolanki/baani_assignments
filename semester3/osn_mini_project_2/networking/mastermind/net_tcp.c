#include "mastermind.h"

#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

void
tcp_init(struct tcp_session *s)
{
  s->fd = -1;
  s->buf_len = 0;
  memset(s->buf, 0, sizeof(s->buf));
}

void
tcp_close(struct tcp_session *s)
{
  if (s->fd >= 0) {
    close(s->fd);
    s->fd = -1;
  }
  s->buf_len = 0;
}

int
tcp_connect_to_peer(const char *ip, int port)
{
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0) {
    return -1;
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_port = htons((uint16_t)port);
  if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {
    close(fd);
    return -1;
  }

  if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    close(fd);
    return -1;
  }

  return fd;
}

int
tcp_send_line(struct tcp_session *s, const char *line)
{
  if (s == NULL || s->fd < 0 || line == NULL) {
    return -1;
  }

  char out_buf[512];
  int len = snprintf(out_buf, sizeof(out_buf), "%s\n", line);
  if (len < 0 || len >= (int)sizeof(out_buf)) {
    return -1;
  }

  int total_sent = 0;
  while (total_sent < len) {
    ssize_t n = send(s->fd, out_buf + total_sent,
                     (size_t)(len - total_sent), 0);
    if (n < 0) {
      if (errno == EINTR) {
        continue;
      }
      return -1;
    }
    if (n == 0) {
      return -1;
    }
    total_sent += (int)n;
  }

  char log_msg[300];
  snprintf(log_msg, sizeof(log_msg), "TCP sent: %s", line);
  write_log(log_msg);
  return 0;
}

/* Check if s->buf already contains a newline-terminated message */
static int
pop_line_from_buffer(struct tcp_session *s, char *out_line, int max_len)
{
  for (int i = 0; i < s->buf_len; i++) {
    if (s->buf[i] == '\n') {
      int copy_len = i;
      if (copy_len > 0 && s->buf[copy_len - 1] == '\r') {
        copy_len--;
      }
      if (copy_len >= max_len) {
        copy_len = max_len - 1;
      }

      memcpy(out_line, s->buf, (size_t)copy_len);
      out_line[copy_len] = '\0';

      int remaining = s->buf_len - (i + 1);
      if (remaining > 0) {
        memmove(s->buf, s->buf + i + 1, (size_t)remaining);
      }
      s->buf_len = remaining;

      char log_msg[300];
      snprintf(log_msg, sizeof(log_msg), "TCP received: %s", out_line);
      write_log(log_msg);
      return 1;
    }
  }
  return 0;
}

int
tcp_read_line(struct tcp_session *s, int do_recv, char *out_line, int max_len)
{
  if (s == NULL || s->fd < 0) {
    return -1;
  }

  if (pop_line_from_buffer(s, out_line, max_len)) {
    return 1;
  }

  if (!do_recv) {
    return 0;
  }

  if (s->buf_len >= (int)sizeof(s->buf) - 1) {
    s->buf_len = 0;
  }

  ssize_t n = recv(s->fd, s->buf + s->buf_len,
                   sizeof(s->buf) - (size_t)s->buf_len - 1, 0);
  if (n < 0) {
    if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
      return 0;
    }
    return -1;
  }
  if (n == 0) {
    /* Peer closed the TCP socket */
    return -1;
  }

  s->buf_len += (int)n;
  if (pop_line_from_buffer(s, out_line, max_len)) {
    return 1;
  }
  return 0;
}
