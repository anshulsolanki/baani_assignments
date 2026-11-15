#include "bellman_ford.h"

void barrier_init(struct thread_barrier *b, int total_threads) {
    pthread_mutex_init(&b->lock, NULL);
    pthread_cond_init(&b->cv, NULL);
    b->total_threads = total_threads;
    b->waiting_count = 0;
    b->generation = 0;
}

/*
 * Block calling thread until all `total_threads` arrive at the barrier.
 * Uses a generation counter so threads waking up cannot interfere with
 * the next barrier round.
 */
void barrier_wait(struct thread_barrier *b) {
    if (b->total_threads <= 1) {
        return;
    }

    pthread_mutex_lock(&b->lock);
    int my_gen = b->generation;
    b->waiting_count++;

    if (b->waiting_count == b->total_threads) {
        b->waiting_count = 0;
        b->generation++;
        pthread_cond_broadcast(&b->cv);
    } else {
        while (b->generation == my_gen) {
            pthread_cond_wait(&b->cv, &b->lock);
        }
    }

    pthread_mutex_unlock(&b->lock);
}

void barrier_destroy(struct thread_barrier *b) {
    pthread_cond_destroy(&b->cv);
    pthread_mutex_destroy(&b->lock);
}
