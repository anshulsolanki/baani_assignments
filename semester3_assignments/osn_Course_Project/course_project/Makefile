CC = gcc
CFLAGS = -std=c11 -D_DEFAULT_SOURCE -D_BSD_SOURCE -Wall -Wextra -Werror -pthread -O2 -g -Isrc/shared -Isrc/scheduler -Isrc/worker -Isrc/client
LDFLAGS = -pthread

SHARED_SRCS = src/shared/log_utils.c src/shared/net_utils.c src/shared/sha1.c
SCHED_SRCS = src/scheduler/main.c src/scheduler/worker_registry.c src/scheduler/job_manager.c src/scheduler/scheduler_pass.c src/scheduler/client_handler.c
WORKER_SRCS = src/worker/main.c src/worker/sandbox_exec.c src/worker/monitor_telemetry.c src/worker/cache_ckpt.c
CLIENT_SRCS = src/client/main.c src/client/commands.c

all: scheduler worker client test_bins

scheduler: $(SHARED_SRCS) $(SCHED_SRCS)
	$(CC) $(CFLAGS) -o scheduler $(SHARED_SRCS) $(SCHED_SRCS) $(LDFLAGS)

worker: $(SHARED_SRCS) $(WORKER_SRCS)
	$(CC) $(CFLAGS) -o worker $(SHARED_SRCS) $(WORKER_SRCS) $(LDFLAGS)

client: $(SHARED_SRCS) $(CLIENT_SRCS)
	$(CC) $(CFLAGS) -o client $(SHARED_SRCS) $(CLIENT_SRCS) $(LDFLAGS)

test_bins:
	$(MAKE) -C tests all

clean:
	rm -f ./scheduler ./worker ./client *.o src/shared/*.o src/scheduler/*.o src/worker/*.o src/client/*.o
	rm -rf *.dSYM cache
	$(MAKE) -C tests clean

.PHONY: all test_bins clean
