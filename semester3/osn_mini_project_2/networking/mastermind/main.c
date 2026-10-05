#include "mastermind.h"

#include <stdio.h>
#include <string.h>

int
main(int argc, char *argv[])
{
  bool cost_cutting = false;
  bool log_enabled = false;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "--cost-cutting") == 0) {
      cost_cutting = true;
    } else if (strcmp(argv[i], "--log") == 0) {
      log_enabled = true;
    } else {
      fprintf(stderr, "Usage: %s [--cost-cutting] [--log]\n", argv[0]);
      return 1;
    }
  }

  log_init(log_enabled);
  log_event("STARTUP mode=%s", cost_cutting ? "UDP(--cost-cutting)" : "TCP");
  return 0;
}
