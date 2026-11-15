#include <signal.h>
#include <stdio.h>

int main(void) {
    printf("About to trigger SIGSEGV...\n");
    fflush(stdout);
    raise(SIGSEGV);
    return 0;
}
