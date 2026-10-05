#ifndef TEMPEST_H
#define TEMPEST_H

#include <stdbool.h>
#include <stddef.h>
#include <sys/types.h>

#define TEMPEST_HOST        "wttr.is"
#define TEMPEST_PORT        "80"
#define TEMPEST_TIMEOUT_SEC 10
#define TEMPEST_USER_AGENT  "curl/8.0"

/* Encode a city name into RFC 3986 percent-encoded form.
 * Returns a newly allocated string (caller must free), or NULL on failure.
 */
char *url_encode(const char *str);

/* Establish a TCP connection to host:port with a 10s socket timeout.
 * Returns a connected socket descriptor, or -1 on error.
 */
int http_connect(const char *host, const char *port);

/* Send the entire buffer over sockfd, handling short writes.
 * Returns 0 on success, -1 on error.
 */
int send_all(int sockfd, const char *buf, size_t len);

/* Read the full HTTP response from sockfd until EOF.
 * Returns a newly allocated null-terminated buffer, setting *out_len,
 * or NULL on error.
 */
char *recv_all(int sockfd, size_t *out_len);

/* Execute the weather query for encoded_city and print output.
 * Returns 0 on success, 1 on failure.
 */
int fetch_weather(const char *encoded_city, bool raw_mode);

#endif /* TEMPEST_H */
