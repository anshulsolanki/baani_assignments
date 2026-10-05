#include "mastermind.h"

#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

void
tcp_session_init(struct tcp_session *s)
{
  s->fd = -1;
  s->rx_len = 0;
  memset(s->rx_buf, 0, sizeof(s->rx_buf));
}

void
tcp_session_close(struct tcp_session *s)
{
  if (s->fd >= 0) {
    close(s->fd);
    s->fd = -1;
  }
  s->rx_len = 0;
}

int
tcp_connect_peer(const char *ip, uint16_t port)
{
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0) {
    return -1;
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_port = htons(port);
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
tcp_send_msg(struct tcp_session *s, const char *msg)
{
  if (s == nullptr || s->fd < 0 || msg == nullptr) {
    return -1;
  }

  char line[512];
  int len = snprintf(line, sizeof(line), "%s\n", msg);
  if (len < 0 || (size_t)len >= sizeof(line)) {
    return -1;
  }

  size_t total = 0;
  while (total < (size_t)len) {
    ssize_t n = send(s->fd, line + total, (size_t)len - total, 0);
    if (n < 0) {
      if (errno == EINTR) {
        continue;
      }
      return -1;
    }
    if (n == 0) {
      return -1;
    }
    total += (size_t)n;
  }

  log_event("TCP_TX fd=%d msg=\"%s\"", s->fd, msg);
  return 0;
}

static bool
extract_buffered_line(struct tcp_session *s, char *out_line, size_t max_len)
{
  for (size_t i = 0; i < s->rx_len; i++) {
    if (s->rx_buf[i] == '\n') {
      size_t copy_len = i;
      if (copy_len > 0 && s->rx_buf[copy_len - 1] == '\r') {
        copy_len--;
      }
      if (copy_len >= max_len) {
        copy_len = max_len - 1;
      }
      memcpy(out_line, s->rx_buf, copy_len);
      out_line[copy_len] = '\0';

      size_t consumed = i + 1;
      memmove(s->rx_buf, s->rx_buf + consumed, s->rx_len - consumed);
      s->rx_len -= consumed;

      log_event("TCP_RX fd=%d msg=\"%s\"", s->fd, out_line);
      return true;
    }
  }
  return false;
}

int
tcp_recv_line(struct tcp_session *s, bool do_read, char *out_line,
              size_t max_len)
{
  if (s == nullptr || s->fd < 0) {
    return -1;
  }

  /* First check if a full line is already buffered from an earlier recv() */
  if (extract_buffered_line(s, out_line, max_len)) {
    return 1;
  }

  if (!do_read) {
    return 0;
  }

  if (s->rx_len >= sizeof(s->rx_buf) - 1) {
    s->rx_len = 0;
  }

  ssize_t n = recv(s->fd, s->rx_buf + s->rx_len,
                   sizeof(s->rx_buf) - s->rx_len - 1, 0);
  if (n < 0) {
    if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
      return 0;
    }
    return -1;
  }
  if (n == 0) {
    /* Peer closed TCP connection (EOF) */
    return -1;
  }

  s->rx_len += (size_t)n;
  if (extract_buffered_line(s, out_line, max_len)) {
    return 1;
  }
  return 0;
}
