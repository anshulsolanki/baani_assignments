#ifndef NET_UTILS_H
#define NET_UTILS_H

#include "cluster_protocol.h"
#include <stddef.h>
#include <stdint.h>

/* Central timestamped logger (Section 7) */
void log_line(const char *fmt, ...);

/* State name helpers */
const char *job_state_str(int state);
const char *worker_state_str(int state);

/* TCP framing helpers */
int send_all(int fd, const void *buf, size_t len);
int recv_all(int fd, void *buf, size_t len);
int send_packet(int fd, int32_t type, const void *payload, int32_t length);
int send_text_packet(int fd, int32_t type, const char *text);
int recv_header(int fd, struct packet_header *hdr);

/* Socket setup and UDP discovery (Section 2C) */
int create_tcp_server(int port);
int connect_tcp(const char *ip, int port);
int create_udp_discovery_server(int discovery_port);
void handle_udp_discovery_request(int udp_fd, int scheduler_tcp_port);
int discover_scheduler_udp(int discovery_port, char *out_ip, size_t ip_len, int *out_port);

/* SHA-1 hashing (Section 13) */
void sha1_bytes(const uint8_t *data, size_t len, char out_hex[41]);
int sha1_file(const char *path, char out_hex[41], int32_t *out_size);
const char *path_basename_ptr(const char *path);

#endif /* NET_UTILS_H */
