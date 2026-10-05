#include "tempest.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int
main(int argc, char *argv[])
{
  if (argc < 2) {
    fprintf(stderr, "Usage: %s <city_name> [--raw]\n", argv[0]);
    return 1;
  }

  bool raw_mode = false;
  const char *city = argv[1];

  if (argc == 3) {
    if (strcmp(argv[2], "--raw") == 0) {
      raw_mode = true;
    } else {
      printf("tempest: too many arguments\n");
      return 1;
    }
  } else if (argc > 3) {
    printf("tempest: too many arguments\n");
    return 1;
  }

  /* Disallow --raw as the city name when a second argument is missing/present */
  char *encoded_city = url_encode(city);
  if (encoded_city == nullptr) {
    fprintf(stderr, "tempest: memory allocation failed\n");
    return 1;
  }

  (void)raw_mode;
  free(encoded_city);
  return 0;
}
