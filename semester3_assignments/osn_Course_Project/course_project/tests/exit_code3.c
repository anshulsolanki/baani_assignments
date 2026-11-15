#include <stdio.h>

/*
 * Section 5E test: exits with non-zero status code 3 to verify
 * "Exited with code 3." diagnosis.
 */
int main(void) {
    printf("Exiting intentionally with status code 3\n");
    return 3;
}
