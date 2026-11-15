#include "net_utils.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/*
 * Central logging function required by Section 7.
 * Prefixes every log line with a 24-hour [HH:MM:SS] timestamp.
 */
void log_line(const char *fmt, ...) {
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);

    char time_buf[16];
    strftime(time_buf, sizeof(time_buf), "[%H:%M:%S]", &tm_info);

    char msg_buf[2048];
    va_list args;
    va_start(args, fmt);
    vsnprintf(msg_buf, sizeof(msg_buf), fmt, args);
    va_end(args);

    printf("%s %s\n", time_buf, msg_buf);
    fflush(stdout);
}

const char *job_state_str(int state) {
    switch (state) {
        case JOB_WAITING:          return "WAITING";
        case JOB_QUEUED:           return "QUEUED";
        case JOB_RUNNING:          return "RUNNING";
        case JOB_COMPLETED:        return "COMPLETED";
        case JOB_FAILED:           return "FAILED";
        case JOB_CANCELLED:        return "CANCELLED";
        case JOB_LOST:             return "LOST";
        case JOB_FAILED_PERMANENT: return "FAILED_PERMANENT";
        default:                   return "UNKNOWN";
    }
}

const char *worker_state_str(int state) {
    switch (state) {
        case WORKER_ALIVE:     return "ALIVE";
        case WORKER_SUSPECTED: return "SUSPECTED";
        case WORKER_DEAD:      return "DEAD";
        case WORKER_DRAINING:  return "DRAINING";
        default:               return "UNKNOWN";
    }
}

const char *path_basename_ptr(const char *path) {
    if (path == NULL) {
        return "";
    }
    const char *slash = strrchr(path, '/');
    return (slash != NULL) ? (slash + 1) : path;
}
