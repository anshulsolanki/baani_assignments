#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("Hello from Distributed Compute Cluster job (PID %d)!\n", (int)getpid());
    fflush(stdout);
    return 0;
}
