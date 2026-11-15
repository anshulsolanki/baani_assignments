#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

/*
 * Section 5A fork-bomb guard test (RLIMIT_NPROC): attempts to fork 128 child
 * processes and verifies fork() hits EAGAIN under the worker's process limit.
 */
int main(void) {
    int spawned = 0;
    for (int i = 0; i < 128; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            fprintf(stderr, "fork() blocked after %d children: %s\n",
                    spawned, strerror(errno));
            while (wait(NULL) > 0) {
            }
            return 2;
        }
        if (pid == 0) {
            sleep(2);
            _exit(0);
        }
        spawned++;
    }

    while (wait(NULL) > 0) {
    }
    printf("Spawned all %d children without hitting RLIMIT_NPROC\n", spawned);
    return 0;
}
