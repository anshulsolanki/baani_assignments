#include "bellman_ford.h"
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int num_vertices = 0;
    int num_edges = 0;
    int source = 0;
    int num_threads = 0;

    if (scanf("%d %d %d %d", &num_vertices, &num_edges, &source, &num_threads) != 4) {
        fprintf(stderr, "Error: expected V E N T\n");
        return 1;
    }

    if (num_vertices <= 0 || num_edges < 0 ||
        source < 0 || source >= num_vertices || num_threads <= 0) {
        fprintf(stderr, "Error: invalid graph parameters\n");
        return 1;
    }

    struct raw_edge *raw_edges = NULL;
    if (num_edges > 0) {
        raw_edges = malloc(num_edges * sizeof(struct raw_edge));
        if (raw_edges == NULL) {
            perror("malloc");
            return 1;
        }
    }

    for (int i = 0; i < num_edges; i++) {
        int s = 0;
        int d = 0;
        if (scanf("%d %d", &s, &d) != 2 ||
            s < 0 || s >= num_vertices || d < 0 || d >= num_vertices) {
            fprintf(stderr, "Error: invalid edge at line %d\n", i + 2);
            free(raw_edges);
            return 1;
        }
        raw_edges[i].u = s;
        raw_edges[i].v = d;
    }

    int *distances = malloc(num_vertices * sizeof(int));
    if (distances == NULL) {
        perror("malloc");
        free(raw_edges);
        return 1;
    }

    if (solve_bellman_ford(num_vertices, num_edges, source, num_threads,
                           raw_edges, distances) < 0) {
        fprintf(stderr, "Error: Bellman-Ford solver failed\n");
        free(distances);
        free(raw_edges);
        return 1;
    }

    for (int v = 0; v < num_vertices; v++) {
        if (v > 0) {
            putchar(' ');
        }
        printf("%d", distances[v]);
    }
    putchar('\n');
    fflush(stdout);

    free(distances);
    free(raw_edges);
    return 0;
}
