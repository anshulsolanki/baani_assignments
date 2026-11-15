#include <stdio.h>

int main(void) {
    printf("Starting CPU burner loop...\n");
    fflush(stdout);
    volatile unsigned long x = 0;
    while (1) {
        x++;
    }
    return 0;
}
