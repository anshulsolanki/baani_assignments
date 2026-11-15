#include <stdio.h>
#include <unistd.h>

int main(void) {
    for (int i = 1; i <= 30; i++) {
        printf("sleeper tick %d\n", i);
        fflush(stdout);
        sleep(1);
    }
    return 0;
}
