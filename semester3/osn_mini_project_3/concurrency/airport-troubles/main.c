#include "airport.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct raw_line {
    int time;
    int is_officer;
    int id;
};

/*
 * Parse N arrival events from stdin.
 * Each line has format: <time> Student <id>  OR  <time> Immigration officer <id>
 */
static int read_input(int *out_n, struct raw_line **out_lines,
                      int *out_students, int *out_visits) {
    int n = 0;
    if (scanf("%d", &n) != 1 || n < 0) {
        return -1;
    }

    struct raw_line *lines = NULL;
    if (n > 0) {
        lines = calloc(n, sizeof(struct raw_line));
        if (lines == NULL) {
            return -1;
        }
    }

    int student_count = 0;
    int visit_count = 0;

    for (int i = 0; i < n; i++) {
        int t = 0;
        int id = 0;
        char word1[64];
        char word2[64];

        if (scanf("%d %63s", &t, word1) != 2) {
            free(lines);
            return -1;
        }

        if (strcmp(word1, "Student") == 0) {
            if (scanf("%d", &id) != 1) {
                free(lines);
                return -1;
            }
            lines[i].time = t;
            lines[i].is_officer = 0;
            lines[i].id = id;
            student_count++;
        } else if (strcmp(word1, "Immigration") == 0) {
            if (scanf("%63s %d", word2, &id) != 2 || strcmp(word2, "officer") != 0) {
                free(lines);
                return -1;
            }
            lines[i].time = t;
            lines[i].is_officer = 1;
            lines[i].id = id;
            visit_count++;
        } else {
            free(lines);
            return -1;
        }
    }

    *out_n = n;
    *out_lines = lines;
    *out_students = student_count;
    *out_visits = visit_count;
    return 0;
}

int main(void) {
    int n = 0;
    int num_students = 0;
    int num_visits = 0;
    struct raw_line *lines = NULL;

    if (read_input(&n, &lines, &num_students, &num_visits) < 0) {
        fprintf(stderr, "Error: invalid input format\n");
        return 1;
    }

    struct airport_sim sim;
    sim_init(&sim, n, num_students, num_visits);

    struct officer off;
    off.id = 1;
    off.num_visits = num_visits;
    off.visit_times = num_visits > 0 ? calloc(num_visits, sizeof(int)) : NULL;
    off.visit_event_indices = num_visits > 0 ? calloc(num_visits, sizeof(int)) : NULL;
    off.sim = &sim;

    int s_idx = 0;
    int v_idx = 0;
    for (int i = 0; i < n; i++) {
        sim.events[i].time = lines[i].time;
        sim.events[i].is_officer = lines[i].is_officer;
        sim.events[i].processed = 0;

        if (lines[i].is_officer) {
            sim.events[i].visit_index = v_idx;
            off.id = lines[i].id;
            off.visit_times[v_idx] = lines[i].time;
            off.visit_event_indices[v_idx] = i;
            v_idx++;
        } else {
            sim.events[i].visit_index = -1;
            sim.students[s_idx].idx = s_idx;
            sim.students[s_idx].id = lines[i].id;
            sim.students[s_idx].arrival_time = lines[i].time;
            sim.students[s_idx].arrival_event_idx = i;
            sim.students[s_idx].in_hall = 0;
            sim.students[s_idx].approved = 0;
            sim.students[s_idx].bag_on_belt = 0;
            sim.students[s_idx].sim = &sim;
            s_idx++;
        }
    }
    free(lines);

    struct handler_arg handlers[NUM_HANDLERS];

    /*
     * Hold sim.lock while spawning every person's thread so active_threads is
     * completely initialized before any thread begins executing.
     */
    pthread_mutex_lock(&sim.lock);
    sim.active_threads = num_students + (num_visits > 0 ? 1 : 0) + NUM_HANDLERS;

    for (int h = 0; h < NUM_HANDLERS; h++) {
        handlers[h].id = h + 1;
        handlers[h].sim = &sim;
        if (pthread_create(&handlers[h].thread, NULL, handler_thread, &handlers[h]) != 0) {
            perror("pthread_create handler");
            pthread_mutex_unlock(&sim.lock);
            return 1;
        }
    }

    if (num_visits > 0) {
        if (pthread_create(&off.thread, NULL, officer_thread, &off) != 0) {
            perror("pthread_create officer");
            pthread_mutex_unlock(&sim.lock);
            return 1;
        }
    }

    for (int i = 0; i < num_students; i++) {
        if (pthread_create(&sim.students[i].thread, NULL, student_thread, &sim.students[i]) != 0) {
            perror("pthread_create student");
            pthread_mutex_unlock(&sim.lock);
            return 1;
        }
    }

    pthread_mutex_unlock(&sim.lock);

    /* Wait for all actor threads to finish */
    for (int i = 0; i < num_students; i++) {
        pthread_join(sim.students[i].thread, NULL);
    }
    if (num_visits > 0) {
        pthread_join(off.thread, NULL);
    }
    for (int h = 0; h < NUM_HANDLERS; h++) {
        pthread_join(handlers[h].thread, NULL);
    }

    free(off.visit_times);
    free(off.visit_event_indices);
    sim_destroy(&sim);
    return 0;
}
