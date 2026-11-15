#include "tempest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Check that the city argument has at least one letter or digit */
static int
has_alnum_char(const char *s)
{
  for (int i = 0; s[i] != '\0'; i++) {
    char c = s[i];
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
        (c >= '0' && c <= '9')) {
      return 1;
    }
  }
  return 0;
}

int
main(int argc, char *argv[])
{
  if (argc < 2) {
    printf("Usage: tempest <city_name> [--raw]\n");
    return 1;
  }

  int raw_mode = 0;
  const char *city = argv[1];

  if (argc == 3) {
    if (strcmp(argv[2], "--raw") == 0) {
      raw_mode = 1;
    } else {
      printf("tempest: too many arguments\n");
      return 1;
    }
  } else if (argc > 3) {
    printf("tempest: too many arguments\n");
    return 1;
  }

  if (!has_alnum_char(city)) {
    printf("tempest: invalid location\n");
    return 1;
  }

  char *encoded_city = url_encode(city);
  if (encoded_city == NULL) {
    return 1;
  }

  int result = fetch_weather(city, encoded_city, raw_mode);
  free(encoded_city);
  return result;
}
