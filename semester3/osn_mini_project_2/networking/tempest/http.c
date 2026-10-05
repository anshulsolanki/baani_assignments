#include "tempest.h"

#include <errno.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

int
http_connect(const char *host, const char *port)
{
  struct addrinfo hints;
  struct addrinfo *res = nullptr;

  memset(&hints, 0, sizeof(hints));
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;

  int err = getaddrinfo(host, port, &hints, &res);
  if (err != 0) {
    return -1;
  }

  int sockfd = -1;
  for (struct addrinfo *p = res; p != nullptr; p = p->ai_next) {
    sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
    if (sockfd < 0) {
      continue;
    }

    struct timeval tv;
    tv.tv_sec = TEMPEST_TIMEOUT_SEC;
    tv.tv_usec = 0;
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    if (connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
      break;
    }

    close(sockfd);
    sockfd = -1;
  }

  freeaddrinfo(res);
  return sockfd;
}

int
send_all(int sockfd, const char *buf, size_t len)
{
  size_t total_sent = 0;
  while (total_sent < len) {
    ssize_t n = send(sockfd, buf + total_sent, len - total_sent, 0);
    if (n < 0) {
      if (errno == EINTR) {
        continue;
      }
      return -1;
    }
    if (n == 0) {
      return -1;
    }
    total_sent += (size_t)n;
  }
  return 0;
}

char *
recv_all(int sockfd, size_t *out_len)
{
  size_t cap = 4096;
  size_t len = 0;
  char *buf = malloc(cap);
  if (buf == nullptr) {
    return nullptr;
  }

  for (;;) {
    if (len + 2048 + 1 > cap) {
      cap *= 2;
      char *new_buf = realloc(buf, cap);
      if (new_buf == nullptr) {
        free(buf);
        return nullptr;
      }
      buf = new_buf;
    }

    ssize_t n = recv(sockfd, buf + len, cap - len - 1, 0);
    if (n < 0) {
      if (errno == EINTR) {
        continue;
      }
      free(buf);
      return nullptr;
    }
    if (n == 0) {
      break;
    }
    len += (size_t)n;
  }

  buf[len] = '\0';
  if (out_len != nullptr) {
    *out_len = len;
  }
  return buf;
}

int
fetch_weather(const char *encoded_city, bool raw_mode)
{
  const char *host = getenv("TEMPEST_HOST");
  if (host == nullptr || host[0] == '\0') {
    host = TEMPEST_HOST;
  }
  const char *port = getenv("TEMPEST_PORT");
  if (port == nullptr || port[0] == '\0') {
    port = TEMPEST_PORT;
  }

  int sockfd = http_connect(host, port);
  if (sockfd < 0) {
    fprintf(stderr, "tempest: failed to connect to %s:%s\n", host, port);
    return 1;
  }

  char req[1024];
  int req_len = snprintf(req, sizeof(req),
                         "GET /%s?0T HTTP/1.1\r\n"
                         "Host: %s\r\n"
                         "User-Agent: %s\r\n"
                         "Connection: close\r\n"
                         "\r\n",
                         encoded_city, TEMPEST_HOST, TEMPEST_USER_AGENT);
  if (req_len < 0 || (size_t)req_len >= sizeof(req)) {
    close(sockfd);
    return 1;
  }

  if (send_all(sockfd, req, (size_t)req_len) < 0) {
    close(sockfd);
    fprintf(stderr, "tempest: failed to send HTTP request\n");
    return 1;
  }

  size_t resp_len = 0;
  char *resp = recv_all(sockfd, &resp_len);
  close(sockfd);

  if (resp == nullptr) {
    fprintf(stderr, "tempest: failed to receive HTTP response\n");
    return 1;
  }

  (void)raw_mode;
  free(resp);
  return 0;
}
