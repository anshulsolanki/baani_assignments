#include "tempest.h"

#include <ctype.h>
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

/* Case-insensitive substring search within a bounded buffer. */
static bool
header_contains_ci(const char *headers, size_t headers_len, const char *needle)
{
  size_t nlen = strlen(needle);
  if (nlen == 0 || headers_len < nlen) {
    return false;
  }

  for (size_t i = 0; i <= headers_len - nlen; i++) {
    bool match = true;
    for (size_t j = 0; j < nlen; j++) {
      if (tolower((unsigned char)headers[i + j]) !=
          tolower((unsigned char)needle[j])) {
        match = false;
        break;
      }
    }
    if (match) {
      return true;
    }
  }
  return false;
}

/* Decode RFC 7230 / RFC 9112 section 7.1 chunked transfer-coding. */
static char *
decode_chunked(const char *body, size_t body_len, size_t *decoded_len)
{
  char *out = malloc(body_len + 1);
  if (out == nullptr) {
    return nullptr;
  }

  size_t pos = 0;
  size_t out_pos = 0;

  while (pos < body_len) {
    /* Find the end of the chunk-size line */
    const char *line_end = strstr(body + pos, "\r\n");
    if (line_end == nullptr) {
      break;
    }

    char *endptr = nullptr;
    unsigned long chunk_sz = strtoul(body + pos, &endptr, 16);
    if (endptr == body + pos) {
      break;
    }

    pos = (size_t)(line_end - body) + 2;
    if (chunk_sz == 0) {
      break;
    }

    if (pos + chunk_sz > body_len) {
      chunk_sz = body_len - pos;
    }

    memcpy(out + out_pos, body + pos, chunk_sz);
    out_pos += chunk_sz;
    pos += chunk_sz;

    /* Skip trailing CRLF after chunk-data */
    if (pos + 2 <= body_len && body[pos] == '\r' && body[pos + 1] == '\n') {
      pos += 2;
    }
  }

  out[out_pos] = '\0';
  if (decoded_len != nullptr) {
    *decoded_len = out_pos;
  }
  return out;
}

static void
print_prefixed_lines(const char *prefix, const char *text, size_t len)
{
  size_t start = 0;
  while (start < len) {
    size_t end = start;
    while (end < len && text[end] != '\n') {
      end++;
    }

    size_t line_len = end - start;
    if (line_len > 0 && text[start + line_len - 1] == '\r') {
      line_len--;
    }

    printf("%s%.*s\n", prefix, (int)line_len, text + start);
    start = (end < len) ? end + 1 : len;
  }
}

static bool
is_invalid_location(int status_code, const char *body, size_t body_len)
{
  if (status_code == 404 || status_code == 400) {
    return true;
  }
  if (header_contains_ci(body, body_len, "Unknown location") ||
      header_contains_ci(body, body_len, "not found") ||
      header_contains_ci(body, body_len, "unable to find any matching weather")) {
    return true;
  }
  return false;
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

  if (resp == nullptr || resp_len == 0) {
    free(resp);
    fprintf(stderr, "tempest: empty or failed HTTP response\n");
    return 1;
  }

  /* Split headers and body at \r\n\r\n */
  char *sep = strstr(resp, "\r\n\r\n");
  if (sep == nullptr) {
    free(resp);
    fprintf(stderr, "tempest: malformed HTTP response\n");
    return 1;
  }

  size_t headers_with_blank_len = (size_t)(sep - resp) + 4;
  const char *raw_body = sep + 4;
  size_t raw_body_len = resp_len - headers_with_blank_len;

  /* Parse HTTP status code from status line: HTTP/1.x <code> <reason> */
  int status_code = 0;
  const char *sp = strchr(resp, ' ');
  if (sp != nullptr && sp < sep) {
    status_code = atoi(sp + 1);
  }

  /* Decode chunked body if Transfer-Encoding: chunked is present */
  char *decoded_body = nullptr;
  const char *body_ptr = raw_body;
  size_t body_len = raw_body_len;

  if (header_contains_ci(resp, headers_with_blank_len,
                         "Transfer-Encoding: chunked")) {
    decoded_body = decode_chunked(raw_body, raw_body_len, &body_len);
    if (decoded_body != nullptr) {
      body_ptr = decoded_body;
    }
  }

  if (is_invalid_location(status_code, body_ptr, body_len)) {
    printf("tempest: invalid location\n");
    free(decoded_body);
    free(resp);
    return 1;
  }

  if (raw_mode) {
    print_prefixed_lines("> ", req, (size_t)req_len);
    print_prefixed_lines("< ", resp, headers_with_blank_len);
  }

  fwrite(body_ptr, 1, body_len, stdout);
  if (body_len > 0 && body_ptr[body_len - 1] != '\n') {
    putchar('\n');
  }

  free(decoded_body);
  free(resp);
  return 0;
}
