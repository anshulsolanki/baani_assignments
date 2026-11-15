#include "airport.h"
#include <stdio.h>

/*
 * Student thread lifecycle:
 * enters (1) -> scans passport (2) -> receives stamp (1) -> leaves hall (1) -> collects bag (1)
 */
void *student_thread(void *arg) {
    struct student *st = (struct student *)arg;
    struct airport_sim *sim = st->sim;

    pthread_mutex_lock(&sim->lock);

    /* 1. Wait until arrival timestamp and same-timestamp input order */
    sim_wait_arrival_time(sim, st->arrival_time);
    sim_wait_arrival_turn(sim, st->arrival_event_idx);
    sim_mark_arrival_processed(sim, st->arrival_event_idx);

    /* Wait if immigration officer is currently in the hall */
    while (sim->officer_in_hall) {
        sim_wait_condition(sim);
    }

    /* Action: enters (duration 1) */
    st->in_hall = 1;
    sim->students_in_hall++;
    sim->unscanned_in_hall++;
    printf("%d Student %d enters\n", sim->current_time, st->id);
    fflush(stdout);
    sim_wait_action(sim, ACTION_DURATION);
    sim_complete_action(sim);

    /* 2. Wait for one of the 3 passport scanners */
    while (sim->free_scanners == 0) {
        sim_wait_condition(sim);
    }

    /* Action: scans passport (duration 2) */
    sim->free_scanners--;
    printf("%d Student %d scans passport\n", sim->current_time, st->id);
    fflush(stdout);
    sim_wait_action(sim, SCAN_DURATION);
    sim->free_scanners++;
    sim->unscanned_in_hall--;
    sim_complete_action(sim);

    /* 3. Wait until approved by the immigration officer */
    while (!st->approved) {
        sim_wait_condition(sim);
    }

    /* Action: receives stamp (duration 1) */
    printf("%d Student %d receives stamp\n", sim->current_time, st->id);
    fflush(stdout);
    sim_wait_action(sim, ACTION_DURATION);
    /* Bag is now ready to be loaded onto the belt */
    sim->ready_bags[sim->ready_tail] = st->idx;
    sim->ready_tail++;
    sim->ready_count++;
    sim_complete_action(sim);

    /* 4. Leave the immigration hall (cannot leave while officer is in hall) */
    while (sim->officer_in_hall) {
        sim_wait_condition(sim);
    }

    /* Action: leaves hall (duration 1) */
    sim->students_leaving_now++;
    printf("%d Student %d leaves hall\n", sim->current_time, st->id);
    fflush(stdout);
    sim_wait_action(sim, ACTION_DURATION);
    st->in_hall = 0;
    sim->students_leaving_now--;
    sim->students_in_hall--;
    sim_complete_action(sim);

    /* 5. Wait until own bag has been loaded onto the baggage belt */
    while (!st->bag_on_belt) {
        sim_wait_condition(sim);
    }

    /* Action: collects bag (duration 1) */
    printf("%d Student %d collects bag\n", sim->current_time, st->id);
    fflush(stdout);
    sim_wait_action(sim, ACTION_DURATION);
    st->bag_on_belt = 0;
    sim->belt_slots_used--;
    sim->bags_collected++;
    sim_complete_action(sim);

    sim_thread_exit(sim);
    pthread_mutex_unlock(&sim->lock);
    return NULL;
}

/*
 * Immigration Officer 1 thread lifecycle across all scheduled visits:
 * enters (1) -> waits for all hall students to scan -> approves (1) -> leaves (1)
 */
void *officer_thread(void *arg) {
    struct officer *off = (struct officer *)arg;
    struct airport_sim *sim = off->sim;

    pthread_mutex_lock(&sim->lock);

    for (int v = 0; v < off->num_visits; v++) {
        sim->officer_current_visit = v;
        sim_notify_change(sim);

        sim_wait_arrival_time(sim, off->visit_times[v]);
        sim_wait_arrival_turn(sim, off->visit_event_indices[v]);
        sim_mark_arrival_processed(sim, off->visit_event_indices[v]);

        /* Wait if any student is mid-exit from the hall */
        while (sim->students_leaving_now > 0) {
            sim_wait_condition(sim);
        }

        /* Action: enters (duration 1) */
        sim->officer_in_hall = 1;
        printf("%d Immigration officer %d enters\n", sim->current_time, off->id);
        fflush(stdout);
        sim_wait_action(sim, ACTION_DURATION);
        sim_complete_action(sim);

        /* Wait until every student currently in the hall has scanned passport */
        while (sim->unscanned_in_hall > 0) {
            sim_wait_condition(sim);
        }

        /* Action: approves all unapproved students in the hall as one batch (duration 1) */
        printf("%d Immigration officer %d approves\n", sim->current_time, off->id);
        fflush(stdout);
        sim_wait_action(sim, ACTION_DURATION);
        for (int i = 0; i < sim->num_students; i++) {
            if (sim->students[i].in_hall && !sim->students[i].approved) {
                sim->students[i].approved = 1;
            }
        }
        sim_complete_action(sim);

        /* Action: leaves immediately after approving (duration 1) */
        printf("%d Immigration officer %d leaves\n", sim->current_time, off->id);
        fflush(stdout);
        sim_wait_action(sim, ACTION_DURATION);
        sim->officer_in_hall = 0;
        sim->officer_current_visit = v + 1;
        sim_complete_action(sim);
    }

    sim_thread_exit(sim);
    pthread_mutex_unlock(&sim->lock);
    return NULL;
}

/*
 * Baggage Handler thread lifecycle (Handlers 1 and 2):
 * Waits for a stamped student's bag and free space on the belt (capacity 2),
 * then loads the bag onto the belt (duration 1).
 */
void *handler_thread(void *arg) {
    struct handler_arg *handler = (struct handler_arg *)arg;
    struct airport_sim *sim = handler->sim;

    pthread_mutex_lock(&sim->lock);

    while (1) {
        while ((sim->ready_count == 0 || sim->belt_slots_used >= BELT_CAPACITY) &&
               sim->bags_collected < sim->num_students) {
            sim_wait_condition(sim);
        }

        if (sim->bags_collected >= sim->num_students && sim->ready_count == 0) {
            break;
        }

        if (sim->ready_count > 0 && sim->belt_slots_used < BELT_CAPACITY) {
            int student_idx = sim->ready_bags[sim->ready_head];
            sim->ready_head++;
            sim->ready_count--;
            sim->belt_slots_used++;

            printf("%d Baggage handler %d loads bag for Student %d\n",
                   sim->current_time, handler->id, sim->students[student_idx].id);
            fflush(stdout);

            sim_wait_action(sim, ACTION_DURATION);
            sim->students[student_idx].bag_on_belt = 1;
            sim_complete_action(sim);
        }
    }

    sim_thread_exit(sim);
    pthread_mutex_unlock(&sim->lock);
    return NULL;
}
