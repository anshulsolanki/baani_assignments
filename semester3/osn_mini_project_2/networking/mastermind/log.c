#include "mastermind.h"

#include <stdio.h>
#include <sys/time.h>
#include <time.h>

static int g_log_enabled = 0;

void
init_logging(int enabled)
{
  g_log_enabled = enabled;
}

long
get_current_ms(void)
{
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return (long)tv.tv_sec * 1000L + (long)(tv.tv_usec / 1000L);
}

void
write_log(const char *message)
{
  if (!g_log_enabled) {
    return;
  }

  FILE *log_file = fopen("log.txt", "a");
  if (log_file == NULL) {
    return;
  }

  // Inside your logging function
  char time_buffer[30];
  struct timeval tv;
  time_t curtime;

  gettimeofday(&tv, NULL);
  curtime = tv.tv_sec;

  // Format the time part
  strftime(time_buffer, 30, "%Y-%m-%d %H:%M:%S", localtime(&curtime));

  // Add microseconds and print to the log file
  fprintf(log_file, "[%s.%06ld] [LOG] %s\n", time_buffer, (long)tv.tv_usec,
          message);

  fclose(log_file);
}
