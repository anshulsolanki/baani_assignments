#include "mastermind.h"

#include <stdarg.h>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>

static bool g_log_enabled = false;

void
log_init(bool enabled)
{
  g_log_enabled = enabled;
}

uint64_t
now_ms(void)
{
  struct timeval tv;
  gettimeofday(&tv, nullptr);
  return (uint64_t)tv.tv_sec * 1000ULL + (uint64_t)(tv.tv_usec / 1000);
}

void
log_event(const char *fmt, ...)
{
  if (!g_log_enabled) {
    return;
  }

  FILE *fp = fopen("log.txt", "a");
  if (fp == nullptr) {
    return;
  }

  struct timeval tv;
  gettimeofday(&tv, nullptr);

  char buf[64];
  strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&tv.tv_sec));
  fprintf(fp, "[%s.%06ld] ", buf, (long)tv.tv_usec);

  va_list ap;
  va_start(ap, fmt);
  vfprintf(fp, fmt, ap);
  va_end(ap);

  fprintf(fp, "\n");
  fclose(fp);
}
