#include "airport.h"
#include <stdio.h>
#include <stdlib.h>

/*
 * Advance symbolic time to the earliest pending wake_time once every active
 * thread is either waiting on a future timestamp or has verified it cannot
 * start any action at current_time.
 */
static void try_advance_clock(struct airport_sim *sim) {
    if (sim->finishing_phase_count > 0) {
        return;
    }
    if (sim->timed_count + sim->checked_count < sim->active_threads) {
        return;
    }
    if (sim->timed_count == 0) {
        return;
    }

    /* Find the smallest wake_time across all active timer slots */
    int min_time = -1;
    for (int i = 0; i < sim->max_threads; i++) {
        if (sim->slot_used[i] && !sim->wake_done[i]) {
            if (min_time == -1 || sim->wake_time[i] < min_time) {
                min_time = sim->wake_time[i];
            }
        }
    }

    if (min_time == -1) {
        return;
    }

    sim->current_time = min_time;

    /* Mark all threads whose wake_time equals min_time as ready to wake */
    for (int i = 0; i < sim->max_threads; i++) {
        if (sim->slot_used[i] && !sim->wake_done[i] && sim->wake_time[i] == min_time) {
            sim->wake_done[i] = 1;
            sim->timed_count--;
            sim->finishing_phase_count++;
        }
    }

    sim->state_version++;
    sim->checked_count = 0;
    pthread_cond_broadcast(&sim->cv);
}

void sim_init(struct airport_sim *sim, int num_events, int num_students, int num_visits) {
    pthread_mutex_init(&sim->lock, NULL);
    pthread_cond_init(&sim->cv, NULL);

    sim->current_time = 0;
    sim->max_threads = num_students + NUM_HANDLERS + 2;
    sim->active_threads = 0;
    sim->timed_count = 0;
    sim->finishing_phase_count = 0;
    sim->checked_count = 0;
    sim->state_version = 1;

    sim->slot_used = calloc(sim->max_threads, sizeof(int));
    sim->wake_time = calloc(sim->max_threads, sizeof(int));
    sim->wake_done = calloc(sim->max_threads, sizeof(int));

    sim->num_events = num_events;
    sim->events = NULL;
    if (num_events > 0) {
        sim->events = calloc(num_events, sizeof(struct arrival_event));
    }

    sim->num_students = num_students;
    sim->students = NULL;
    if (num_students > 0) {
        sim->students = calloc(num_students, sizeof(struct student));
    }

    sim->free_scanners = NUM_SCANNERS;
    sim->students_in_hall = 0;
    sim->unscanned_in_hall = 0;
    sim->students_leaving_now = 0;
    sim->officer_in_hall = 0;
    sim->officer_current_visit = 0;
    sim->num_officer_visits = num_visits;

    sim->ready_bags = NULL;
    if (num_students > 0) {
        sim->ready_bags = calloc(num_students, sizeof(int));
    }
    sim->ready_head = 0;
    sim->ready_tail = 0;
    sim->ready_count = 0;
    sim->belt_slots_used = 0;
    sim->bags_collected = 0;
}

void sim_destroy(struct airport_sim *sim) {
    free(sim->slot_used);
    free(sim->wake_time);
    free(sim->wake_done);
    free(sim->events);
    free(sim->students);
    free(sim->ready_bags);
    pthread_cond_destroy(&sim->cv);
    pthread_mutex_destroy(&sim->lock);
}

void sim_notify_change(struct airport_sim *sim) {
    sim->state_version++;
    sim->checked_count = 0;
    pthread_cond_broadcast(&sim->cv);
}

/*
 * Wait until shared airport state changes (after all completions at
 * the current timestamp have finished). Must be called with sim->lock held.
 */
void sim_wait_condition(struct airport_sim *sim) {
    if (sim->finishing_phase_count > 0) {
        while (sim->finishing_phase_count > 0) {
            pthread_cond_wait(&sim->cv, &sim->lock);
        }
        return;
    }

    int seen_version = sim->state_version;
    sim->checked_count++;
    try_advance_clock(sim);

    while (sim->state_version == seen_version || sim->finishing_phase_count > 0) {
        pthread_cond_wait(&sim->cv, &sim->lock);
    }
}

/* Reserve a free slot in the timer arrays and wait until wake_t */
static void wait_until_time(struct airport_sim *sim, int wake_t, int notify_first) {
    int slot = 0;
    while (slot < sim->max_threads && sim->slot_used[slot]) {
        slot++;
    }

    sim->slot_used[slot] = 1;
    sim->wake_time[slot] = wake_t;
    sim->wake_done[slot] = 0;
    sim->timed_count++;

    if (notify_first) {
        sim_notify_change(sim);
    }
    try_advance_clock(sim);

    while (!sim->wake_done[slot]) {
        pthread_cond_wait(&sim->cv, &sim->lock);
    }

    sim->slot_used[slot] = 0;
}

/*
 * Wait until symbolic clock reaches target_time (for scheduled arrivals).
 */
void sim_wait_arrival_time(struct airport_sim *sim, int target_time) {
    if (sim->current_time >= target_time) {
        return;
    }
    wait_until_time(sim, target_time, 0);
    sim_complete_action(sim);
}

/*
 * Ensure lines with the exact same timestamp are processed in input order.
 */
void sim_wait_arrival_turn(struct airport_sim *sim, int event_idx) {
    int my_time = sim->events[event_idx].time;

    while (1) {
        int blocked_by_earlier = 0;
        for (int j = 0; j < event_idx; j++) {
            if (sim->events[j].time == my_time && !sim->events[j].processed) {
                /* If officer is still busy in an earlier visit, don't stall */
                if (sim->events[j].is_officer &&
                    sim->officer_current_visit < sim->events[j].visit_index) {
                    continue;
                }
                blocked_by_earlier = 1;
                break;
            }
        }
        if (!blocked_by_earlier) {
            break;
        }
        sim_wait_condition(sim);
    }
}

void sim_mark_arrival_processed(struct airport_sim *sim, int event_idx) {
    if (!sim->events[event_idx].processed) {
        sim->events[event_idx].processed = 1;
        sim_notify_change(sim);
    }
}

/*
 * Wait in symbolic time for `duration` units. Upon return, caller updates
 * any completion state before calling sim_complete_action.
 */
void sim_wait_action(struct airport_sim *sim, int duration) {
    int target_time = sim->current_time + duration;
    wait_until_time(sim, target_time, 1);
}

void sim_complete_action(struct airport_sim *sim) {
    sim->finishing_phase_count--;
    sim->state_version++;
    sim->checked_count = 0;
    pthread_cond_broadcast(&sim->cv);
    try_advance_clock(sim);
}

void sim_thread_exit(struct airport_sim *sim) {
    sim->active_threads--;
    sim_notify_change(sim);
    try_advance_clock(sim);
}
