#include "tempest.h"

#include <errno.h>
#include <netdb.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

/* Return current time in milliseconds using gettimeofday */
static long
get_time_ms(void)
{
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return (long)tv.tv_sec * 1000L + (long)(tv.tv_usec / 1000L);
}

/* Set socket send and receive timeouts based on remaining time */
static void
set_socket_timeout(int sockfd, long remaining_ms)
{
  if (remaining_ms < 1) {
    remaining_ms = 1;
  }
  struct timeval tv;
  tv.tv_sec = remaining_ms / 1000L;
  tv.tv_usec = (remaining_ms % 1000L) * 1000L;
  setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
  setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
}

/* Connect to wttr.is:80 using getaddrinfo */
static int
connect_to_server(long start_ms)
{
  struct addrinfo hints;
  struct addrinfo *res = NULL;
  struct addrinfo *p = NULL;

  memset(&hints, 0, sizeof(hints));
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  if (getaddrinfo(TEMPEST_HOST, TEMPEST_PORT, &hints, &res) != 0) {
    return -1;
  }

  int sockfd = -1;
  for (p = res; p != NULL; p = p->ai_next) {
    long elapsed = get_time_ms() - start_ms;
    if (elapsed >= TEMPEST_TIMEOUT_MS) {
      break;
    }

    sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
    if (sockfd < 0) {
      continue;
    }

    set_socket_timeout(sockfd, TEMPEST_TIMEOUT_MS - elapsed);

    if (connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
      break;
    }

    close(sockfd);
    sockfd = -1;
  }

  freeaddrinfo(res);
  return sockfd;
}

/* Handle short writes by looping until all bytes are sent */
static int
send_all(int sockfd, const char *buf, int len, long start_ms)
{
  int total_sent = 0;
  while (total_sent < len) {
    long elapsed = get_time_ms() - start_ms;
    if (elapsed >= TEMPEST_TIMEOUT_MS) {
      return -1;
    }
    set_socket_timeout(sockfd, TEMPEST_TIMEOUT_MS - elapsed);

    ssize_t n = send(sockfd, buf + total_sent, (size_t)(len - total_sent), 0);
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
  return 0;
}

/* Print each line of a block of text with a prefix like "> " or "< " */
static void
print_with_prefix(const char *prefix, const char *text, int len)
{
  int i = 0;
  while (i < len) {
    int line_start = i;
    while (i < len && text[i] != '\n') {
      i++;
    }
    int line_len = i - line_start;
    if (line_len > 0 && text[line_start + line_len - 1] == '\r') {
      line_len--;
    }
    printf("%s%.*s\n", prefix, line_len, text + line_start);
    if (i < len && text[i] == '\n') {
      i++;
    }
  }
}

/* Check if the response indicates an invalid location */
static int
check_invalid_location(const char *city, int status_code, const char *body)
{
  /* Primary signal (per TA Doubt Doc Q7): non-200 HTTP status code */
  if (status_code != 200) {
    return 1;
  }

  if (body == NULL || body[0] == '\0') {
    return 1;
  }

  if (strstr(body, "Unknown location") != NULL ||
      strstr(body, "location not found") != NULL ||
      strstr(body, "unable to find any matching weather") != NULL) {
    return 1;
  }

  /* Valid wttr.is ?0T output always begins with "Weather report:" */
  if (strncmp(body, "Weather report:", 15) != 0) {
    return 1;
  }

  /* If user did not search for GPS coordinates (no comma in input), but
   * wttr.is fell back to IP geolocation coordinates (e.g. "21.99,79.00"),
   * flag it as an invalid location. */
  if (strchr(city, ',') == NULL) {
    const char *first_newline = strchr(body, '\n');
    if (first_newline != NULL) {
      for (const char *p = body + 15; p < first_newline; p++) {
        if (*p == ',') {
          return 1;
        }
      }
    }
  }

  return 0;
}

int
fetch_weather(const char *city, const char *encoded_city, int raw_mode)
{
  /* Start the 10-second timer before connect() as required (Doubt Doc Q5/Q15) */
  long start_ms = get_time_ms();

  int sockfd = connect_to_server(start_ms);
  if (sockfd < 0) {
    fprintf(stderr, "tempest: connection failed or timed out\n");
    return 1;
  }

  /* Build HTTP/1.1 GET request with Connection: close (RFC 9112 Section 9.3) */
  char request[1024];
  int req_len = snprintf(request, sizeof(request),
                         "GET /%s?0T HTTP/1.1\r\n"
                         "Host: %s\r\n"
                         "User-Agent: curl/8.0\r\n"
                         "Connection: close\r\n"
                         "\r\n",
                         encoded_city, TEMPEST_HOST);
  if (req_len < 0 || req_len >= (int)sizeof(request)) {
    close(sockfd);
    return 1;
  }

  if (send_all(sockfd, request, req_len, start_ms) < 0) {
    close(sockfd);
    fprintf(stderr, "tempest: failed to send request\n");
    return 1;
  }

  /* Read full HTTP response using poll() to enforce running 10s timeout */
  int capacity = 8192;
  int total_read = 0;
  char *response = (char *)malloc((size_t)capacity);
  if (response == NULL) {
    close(sockfd);
    return 1;
  }

  while (1) {
    long elapsed = get_time_ms() - start_ms;
    long remaining = TEMPEST_TIMEOUT_MS - elapsed;
    if (remaining <= 0) {
      free(response);
      close(sockfd);
      fprintf(stderr, "tempest: request timed out\n");
      return 1;
    }

    struct pollfd pfd;
    pfd.fd = sockfd;
    pfd.events = POLLIN;
    pfd.revents = 0;

    int ret = poll(&pfd, 1, (int)remaining);
    if (ret == 0) {
      free(response);
      close(sockfd);
      fprintf(stderr, "tempest: request timed out\n");
      return 1;
    }
    if (ret < 0) {
      if (errno == EINTR) {
        continue;
      }
      free(response);
      close(sockfd);
      return 1;
    }

    if (total_read + 2048 >= capacity) {
      capacity *= 2;
      char *new_buf = (char *)realloc(response, (size_t)capacity);
      if (new_buf == NULL) {
        free(response);
        close(sockfd);
        return 1;
      }
      response = new_buf;
    }

    ssize_t n = recv(sockfd, response + total_read,
                     (size_t)(capacity - total_read - 1), 0);
    if (n < 0) {
      if (errno == EINTR) {
        continue;
      }
      free(response);
      close(sockfd);
      return 1;
    }
    if (n == 0) {
      /* Server closed connection (EOF) */
      break;
    }
    total_read += (int)n;
  }

  close(sockfd);
  response[total_read] = '\0';

  if (total_read == 0) {
    free(response);
    return 1;
  }

  /* Find the "\r\n\r\n" boundary between HTTP headers and body */
  char *header_end = strstr(response, "\r\n\r\n");
  if (header_end == NULL) {
    free(response);
    return 1;
  }

  int header_bytes = (int)(header_end - response) + 4;
  char *body = header_end + 4;
  int body_len = total_read - header_bytes;

  /* Parse HTTP status code from "HTTP/1.1 <code> ..." */
  int status_code = 0;
  sscanf(response, "HTTP/%*s %d", &status_code);

  int is_invalid = check_invalid_location(city, status_code, body);

  /* Per Doubt Doc Q12 & Q23: --raw takes precedence even for invalid locations,
   * printing the raw HTTP request and response and exiting with non-zero status */
  if (raw_mode) {
    print_with_prefix("> ", request, req_len);
    print_with_prefix("< ", response, header_bytes);
    fwrite(body, 1, (size_t)body_len, stdout);
    if (body_len > 0 && body[body_len - 1] != '\n') {
      printf("\n");
    }
    free(response);
    return is_invalid ? 1 : 0;
  }

  if (is_invalid) {
    printf("tempest: invalid location\n");
    free(response);
    return 1;
  }

  /* Normal mode: print only the HTTP response body */
  fwrite(body, 1, (size_t)body_len, stdout);
  if (body_len > 0 && body[body_len - 1] != '\n') {
    printf("\n");
  }

  free(response);
  return 0;
}
