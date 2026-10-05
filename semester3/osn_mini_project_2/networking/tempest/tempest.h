#ifndef TEMPEST_H
#define TEMPEST_H

#include <stdbool.h>
#include <stddef.h>

#define TEMPEST_HOST        "wttr.is"
#define TEMPEST_PORT        "80"
#define TEMPEST_TIMEOUT_SEC 10

/* Encode a city name into RFC 3986 percent-encoded form.
 * Returns a newly allocated string (caller must free), or NULL on failure.
 */
char *url_encode(const char *str);

#endif /* TEMPEST_H */
