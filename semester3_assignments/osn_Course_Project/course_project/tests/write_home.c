#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Section 5A privilege-drop test: attempts to create a file outside the job
 * sandbox (/etc/osn_forbidden_test). Under sudo -> nobody, fopen() fails with
 * Permission denied (EACCES) and exits with non-zero code 1.
 */
int main(void) {
    const char *target = "/etc/osn_forbidden_test";
    FILE *fp = fopen(target, "w");
    if (fp == NULL) {
        fprintf(stderr, "Write blocked (%s): %s\n", target, strerror(errno));
        return 1;
    }
    fprintf(fp, "unexpected write\n");
    fclose(fp);
    return 0;
}
