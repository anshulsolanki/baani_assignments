#include <signal.h>
#include <stdio.h>

int main(void) {
    printf("About to trigger SIGFPE...\n");
    fflush(stdout);
    raise(SIGFPE);
    return 0;
}
