#ifndef AIRPORT_H
#define AIRPORT_H

#include <pthread.h>

#define NUM_SCANNERS 3
#define NUM_HANDLERS 2
#define BELT_CAPACITY 2

#define ACTION_DURATION 1
#define SCAN_DURATION 2

struct airport_sim;

/* Per-arrival record to enforce input-order tie-breaking on equal timestamps */
struct arrival_event {
    int time;
    int is_officer;
    int visit_index;
    int processed;
};

/* State for one student thread */
struct student {
    int idx;
    int id;
    int arrival_time;
    int arrival_event_idx;

    int in_hall;
    int approved;
    int bag_on_belt;

    pthread_t thread;
    struct airport_sim *sim;
};

/* State for the single Immigration Officer 1 thread */
struct officer {
    int id;
    int num_visits;
    int *visit_times;
    int *visit_event_indices;

    pthread_t thread;
    struct airport_sim *sim;
};

/* Argument for each Baggage Handler thread (ID 1 and ID 2) */
struct handler_arg {
    int id;
    pthread_t thread;
    struct airport_sim *sim;
};

/* Shared airport simulation state and logical clock */
struct airport_sim {
    pthread_mutex_t lock;
    pthread_cond_t cv;

    /* Logical clock fields (no sleep/usleep used) */
    int current_time;
    int max_threads;
    int active_threads;
    int timed_count;
    int finishing_phase_count;
    int checked_count;
    int state_version;

    /* Simple arrays tracking threads waiting for a future timestamp */
    int *slot_used;
    int *wake_time;
    int *wake_done;

    /* Input arrival ordering */
    int num_events;
    struct arrival_event *events;

    /* Immigration hall state */
    int num_students;
    struct student *students;
    int free_scanners;
    int students_in_hall;
    int unscanned_in_hall;
    int students_leaving_now;
    int officer_in_hall;
    int officer_current_visit;
    int num_officer_visits;

    /* Baggage area state */
    int *ready_bags;
    int ready_head;
    int ready_tail;
    int ready_count;
    int belt_slots_used;
    int bags_collected;
};

/* Logical clock and synchronization helpers (clock.c) */
void sim_init(struct airport_sim *sim, int num_events, int num_students, int num_visits);
void sim_destroy(struct airport_sim *sim);
void sim_notify_change(struct airport_sim *sim);
void sim_wait_condition(struct airport_sim *sim);
void sim_wait_arrival_time(struct airport_sim *sim, int target_time);
void sim_wait_arrival_turn(struct airport_sim *sim, int event_idx);
void sim_mark_arrival_processed(struct airport_sim *sim, int event_idx);
void sim_wait_action(struct airport_sim *sim, int duration);
void sim_complete_action(struct airport_sim *sim);
void sim_thread_exit(struct airport_sim *sim);

/* Actor thread entry points (actors.c) */
void *student_thread(void *arg);
void *officer_thread(void *arg);
void *handler_thread(void *arg);

#endif
