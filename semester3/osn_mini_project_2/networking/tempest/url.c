#include "tempest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Check if character is safe to keep unencoded in a URL */
static int
is_safe_url_char(char c)
{
  if (c >= 'a' && c <= 'z') {
    return 1;
  }
  if (c >= 'A' && c <= 'Z') {
    return 1;
  }
  if (c >= '0' && c <= '9') {
    return 1;
  }
  if (c == '-' || c == '_' || c == '.' || c == '~') {
    return 1;
  }
  return 0;
}

char *
url_encode(const char *city)
{
  if (city == NULL) {
    return NULL;
  }

  int len = (int)strlen(city);
  /* Each character takes at most 3 bytes (%XX) plus 1 byte for '\0' */
  char *encoded = (char *)malloc((size_t)(len * 3 + 1));
  if (encoded == NULL) {
    return NULL;
  }

  int j = 0;
  for (int i = 0; i < len; i++) {
    unsigned char c = (unsigned char)city[i];
    if (is_safe_url_char((char)c)) {
      encoded[j] = (char)c;
      j++;
    } else {
      sprintf(&encoded[j], "%%%02X", c);
      j += 3;
    }
  }
  encoded[j] = '\0';

  return encoded;
}
