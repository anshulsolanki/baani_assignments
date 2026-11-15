#ifndef CLIENT_H
#define CLIENT_H

#include "cluster_protocol.h"
#include "net_utils.h"

struct client_ctx {
    int sock_fd;
    int discovery_port;
    int has_fallback;
    char fallback_ip[64];
    int fallback_port;

    char username[MAX_USERNAME_LEN];
    int waiting_for_reply;
    int waiting_for_logs;
    int in_follow_mode;
    int prompt_shown;
    char last_log_char;
};

int is_valid_username(const char *name);
int execute_client_command(struct client_ctx *cctx, const char *line);

#endif /* CLIENT_H */
