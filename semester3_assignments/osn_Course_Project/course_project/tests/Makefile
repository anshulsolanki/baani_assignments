CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -Werror -O2

BINS = hello_job sleeper_job cpu_burner mem_hog crash_segv crash_fpe exit_code3 write_home fork_bomb counter_ckpt

all: $(BINS)

hello_job: hello_job.c
	$(CC) $(CFLAGS) -o hello_job hello_job.c

sleeper_job: sleeper_job.c
	$(CC) $(CFLAGS) -o sleeper_job sleeper_job.c

cpu_burner: cpu_burner.c
	$(CC) $(CFLAGS) -o cpu_burner cpu_burner.c

mem_hog: mem_hog.c
	$(CC) $(CFLAGS) -o mem_hog mem_hog.c

crash_segv: crash_segv.c
	$(CC) $(CFLAGS) -o crash_segv crash_segv.c

crash_fpe: crash_fpe.c
	$(CC) $(CFLAGS) -o crash_fpe crash_fpe.c

exit_code3: exit_code3.c
	$(CC) $(CFLAGS) -o exit_code3 exit_code3.c

write_home: write_home.c
	$(CC) $(CFLAGS) -o write_home write_home.c

fork_bomb: fork_bomb.c
	$(CC) $(CFLAGS) -o fork_bomb fork_bomb.c

counter_ckpt: counter_ckpt.c
	$(CC) $(CFLAGS) -o counter_ckpt counter_ckpt.c

clean:
	rm -f $(BINS) *.o
	rm -rf *.dSYM

.PHONY: all clean
