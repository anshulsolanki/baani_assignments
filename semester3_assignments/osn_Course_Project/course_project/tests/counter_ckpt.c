#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static volatile sig_atomic_t g_term = 0;

static void on_sigterm(int sig) {
    (void)sig;
    g_term = 1;
}

static void save_checkpoint(const char *ckpt_dir, int step) {
    if (ckpt_dir == NULL || ckpt_dir[0] == '\0') {
        return;
    }
    char tmp_path[512], state_path[512];
    snprintf(tmp_path, sizeof(tmp_path), "%s/state.tmp", ckpt_dir);
    snprintf(state_path, sizeof(state_path), "%s/state", ckpt_dir);

    FILE *fp = fopen(tmp_path, "w");
    if (fp != NULL) {
        fprintf(fp, "%d\n", step);
        fclose(fp);
        rename(tmp_path, state_path);
    }
}

int main(void) {
    signal(SIGTERM, on_sigterm);

    const char *ckpt_dir = getenv("OSN_CHECKPOINT_DIR");
    int step = 1;

    if (ckpt_dir != NULL && ckpt_dir[0] != '\0') {
        char state_path[512];
        snprintf(state_path, sizeof(state_path), "%s/state", ckpt_dir);
        FILE *fp = fopen(state_path, "r");
        if (fp != NULL) {
            if (fscanf(fp, "%d", &step) == 1) {
                printf("Resumed from checkpoint at step %d\n", step);
                fflush(stdout);
            }
            fclose(fp);
        }
    }

    for (; step <= 20; step++) {
        printf("step %d\n", step);
        fflush(stdout);
        save_checkpoint(ckpt_dir, step + 1);
        if (g_term) {
            save_checkpoint(ckpt_dir, step + 1);
            return 0;
        }
        sleep(1);
        if (g_term) {
            save_checkpoint(ckpt_dir, step + 1);
            return 0;
        }
    }

    return 0;
}
