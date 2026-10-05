#include "tempest.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static bool
is_unreserved(unsigned char c)
{
  return isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~';
}

char *
url_encode(const char *str)
{
  if (str == nullptr) {
    return nullptr;
  }

  size_t len = strlen(str);
  /* Worst case: every character expands to %XX (3 bytes) + null terminator */
  char *encoded = malloc(len * 3 + 1);
  if (encoded == nullptr) {
    return nullptr;
  }

  size_t j = 0;
  for (size_t i = 0; i < len; i++) {
    unsigned char c = (unsigned char)str[i];
    if (is_unreserved(c)) {
      encoded[j++] = (char)c;
    } else {
      snprintf(&encoded[j], 4, "%%%02X", c);
      j += 3;
    }
  }
  encoded[j] = '\0';

  return encoded;
}
