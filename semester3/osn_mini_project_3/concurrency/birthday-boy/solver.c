#include "bellman_ford.h"
#include <stdio.h>
#include <stdlib.h>

/*
 * Compare two directed edges by destination vertex `dst` so qsort() groups
 * all incoming edges for the same destination vertex together.
 */
static int compare_edges_by_dst(const void *a, const void *b) {
    const struct directed_edge *ea = (const struct directed_edge *)a;
    const struct directed_edge *eb = (const struct directed_edge *)b;
    return ea->dst - eb->dst;
}

/*
 * Worker routine: executes V - 1 Bellman-Ford relaxation rounds in parallel.
 * Each thread only updates its own slice of destination vertices [v_start, v_end),
 * avoiding any data races on dist_next[].
 */
static void *bf_worker_thread(void *arg) {
    struct worker_task *task = (struct worker_task *)arg;
    struct bf_solver *solver = task->solver;
    const struct directed_edge *edges = solver->edges;
    int *dist_curr = solver->dist_curr;
    int *dist_next = solver->dist_next;
    int iterations = solver->num_vertices - 1;

    for (int iter = 0; iter < iterations; iter++) {
        /* Relax all edges entering this thread's assigned vertices */
        for (int e = task->edge_start; e < task->edge_end; e++) {
            int u = edges[e].src;
            int v = edges[e].dst;
            if (dist_curr[u] != BF_INF && dist_curr[u] + 1 < dist_next[v]) {
                dist_next[v] = dist_curr[u] + 1;
            }
        }

        barrier_wait(&solver->barrier);

        /* Copy updated distances into dist_curr for the next round */
        for (int v = task->v_start; v < task->v_end; v++) {
            dist_curr[v] = dist_next[v];
        }

        barrier_wait(&solver->barrier);
    }

    return NULL;
}

int solve_bellman_ford(int num_vertices, int num_edges, int source,
                       int num_threads, const struct raw_edge *raw_edges,
                       int *out_distances) {
    if (num_vertices <= 0 || num_threads <= 0) {
        return -1;
    }

    int total_dir = 2 * num_edges;
    struct directed_edge *edges = NULL;
    if (total_dir > 0) {
        edges = malloc(total_dir * sizeof(struct directed_edge));
        if (edges == NULL) {
            return -1;
        }
    }

    /* Expand each undirected edge {u, v} into u -> v and v -> u */
    for (int i = 0; i < num_edges; i++) {
        edges[2 * i].src = raw_edges[i].u;
        edges[2 * i].dst = raw_edges[i].v;
        edges[2 * i + 1].src = raw_edges[i].v;
        edges[2 * i + 1].dst = raw_edges[i].u;
    }

    if (total_dir > 0) {
        qsort(edges, total_dir, sizeof(struct directed_edge), compare_edges_by_dst);
    }

    struct bf_solver solver;
    solver.num_vertices = num_vertices;
    solver.num_directed_edges = total_dir;
    solver.source = source;
    solver.num_threads = num_threads;
    solver.edges = edges;
    solver.dist_curr = malloc(num_vertices * sizeof(int));
    solver.dist_next = malloc(num_vertices * sizeof(int));

    struct worker_task *tasks = calloc(num_threads, sizeof(struct worker_task));
    if (solver.dist_curr == NULL || solver.dist_next == NULL || tasks == NULL) {
        free(edges);
        free(solver.dist_curr);
        free(solver.dist_next);
        free(tasks);
        return -1;
    }

    for (int v = 0; v < num_vertices; v++) {
        solver.dist_curr[v] = BF_INF;
        solver.dist_next[v] = BF_INF;
    }
    solver.dist_curr[source] = 0;
    solver.dist_next[source] = 0;

    /* Divide vertices [0, V) and their incoming edges across T threads */
    int cur_edge = 0;
    for (int t = 0; t < num_threads; t++) {
        tasks[t].thread_id = t;
        tasks[t].v_start = (t * num_vertices) / num_threads;
        tasks[t].v_end = ((t + 1) * num_vertices) / num_threads;

        tasks[t].edge_start = cur_edge;
        while (cur_edge < total_dir && edges[cur_edge].dst < tasks[t].v_end) {
            cur_edge++;
        }
        tasks[t].edge_end = cur_edge;
        tasks[t].solver = &solver;
    }

    barrier_init(&solver.barrier, num_threads);

    for (int t = 0; t < num_threads; t++) {
        if (pthread_create(&tasks[t].thread, NULL, bf_worker_thread, &tasks[t]) != 0) {
            perror("pthread_create");
            return -1;
        }
    }

    for (int t = 0; t < num_threads; t++) {
        pthread_join(tasks[t].thread, NULL);
    }

    for (int v = 0; v < num_vertices; v++) {
        out_distances[v] = (solver.dist_curr[v] == BF_INF) ? -1 : solver.dist_curr[v];
    }

    barrier_destroy(&solver.barrier);
    free(tasks);
    free(solver.dist_curr);
    free(solver.dist_next);
    free(edges);
    return 0;
}
