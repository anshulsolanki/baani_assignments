#ifndef BELLMAN_FORD_H
#define BELLMAN_FORD_H

#include <pthread.h>

#define BF_INF 1000000000

struct raw_edge {
    int u;
    int v;
};

struct directed_edge {
    int src;
    int dst;
};

/* Reusable thread barrier built with pthread mutex and condition variable */
struct thread_barrier {
    pthread_mutex_t lock;
    pthread_cond_t cv;
    int total_threads;
    int waiting_count;
    int generation;
};

/* Shared Parallel Bellman-Ford solver context */
struct bf_solver {
    int num_vertices;
    int num_directed_edges;
    int source;
    int num_threads;

    struct directed_edge *edges;
    int *dist_curr;
    int *dist_next;

    struct thread_barrier barrier;
};

/* Exclusive vertex and incoming-edge partition assigned to one thread */
struct worker_task {
    int thread_id;
    int v_start;
    int v_end;
    int edge_start;
    int edge_end;
    pthread_t thread;
    struct bf_solver *solver;
};

/* Barrier functions (barrier.c) */
void barrier_init(struct thread_barrier *b, int total_threads);
void barrier_wait(struct thread_barrier *b);
void barrier_destroy(struct thread_barrier *b);

/* Parallel Bellman-Ford solver (solver.c) */
int solve_bellman_ford(int num_vertices, int num_edges, int source,
                       int num_threads, const struct raw_edge *raw_edges,
                       int *out_distances);

#endif
