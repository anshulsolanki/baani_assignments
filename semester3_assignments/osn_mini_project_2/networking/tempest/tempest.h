#ifndef TEMPEST_H
#define TEMPEST_H

#include <stddef.h>

#define TEMPEST_HOST        "wttr.is"
#define TEMPEST_PORT        "80"
#define TEMPEST_TIMEOUT_MS  10000

/* Convert city name into URL-encoded string (caller frees returned pointer) */
char *url_encode(const char *city);

/* Send HTTP/1.1 GET request to wttr.is and print the weather output */
int fetch_weather(const char *city, const char *encoded_city, int raw_mode);

#endif
