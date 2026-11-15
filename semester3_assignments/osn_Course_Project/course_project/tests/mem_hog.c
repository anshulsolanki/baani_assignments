#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    size_t step_mb = 16;
    size_t total_mb = 0;
    while (1) {
        size_t bytes = step_mb * 1024 * 1024;
        char *p = malloc(bytes);
        if (p == NULL) {
            fprintf(stderr, "malloc failed at %zu MB\n", total_mb);
            return 2;
        }
        memset(p, 0xAA, bytes);
        total_mb += step_mb;
        printf("Allocated %zu MB\n", total_mb);
        fflush(stdout);
        usleep(200000);
    }
    return 0;
}
