#include "net_utils.h"
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

int send_all(int fd, const void *buf, size_t len) {
    const uint8_t *ptr = (const uint8_t *)buf;
    size_t sent = 0;

    while (sent < len) {
        ssize_t n = send(fd, ptr + sent, len - sent, 0);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        if (n == 0) {
            return -1;
        }
        sent += (size_t)n;
    }
    return 0;
}

int recv_all(int fd, void *buf, size_t len) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t got = 0;

    while (got < len) {
        ssize_t n = recv(fd, ptr + got, len - got, 0);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        if (n == 0) {
            return -1;
        }
        got += (size_t)n;
    }
    return 0;
}

int send_packet(int fd, int32_t type, const void *payload, int32_t length) {
    struct packet_header hdr;
    hdr.type = type;
    hdr.length = length;

    if (send_all(fd, &hdr, sizeof(hdr)) < 0) {
        return -1;
    }
    if (length > 0 && payload != NULL) {
        if (send_all(fd, payload, (size_t)length) < 0) {
            return -1;
        }
    }
    return 0;
}

int send_text_packet(int fd, int32_t type, const char *text) {
    int32_t len = (text != NULL) ? (int32_t)(strlen(text) + 1) : 0;
    return send_packet(fd, type, text, len);
}

int recv_header(int fd, struct packet_header *hdr) {
    return recv_all(fd, hdr, sizeof(*hdr));
}

int create_tcp_server(int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#ifdef SO_REUSEPORT
    setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
#endif

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    if (listen(fd, 64) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

int connect_tcp(const char *ip, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {
        close(fd);
        return -1;
    }

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

int create_udp_discovery_server(int discovery_port) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#ifdef SO_REUSEPORT
    setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
#endif

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)discovery_port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

void handle_udp_discovery_request(int udp_fd, int scheduler_tcp_port) {
    char buf[256];
    struct sockaddr_in cli_addr;
    socklen_t cli_len = sizeof(cli_addr);

    ssize_t n = recvfrom(udp_fd, buf, sizeof(buf) - 1, 0,
                         (struct sockaddr *)&cli_addr, &cli_len);
    if (n <= 0) {
        return;
    }
    buf[n] = '\0';

    if (strncmp(buf, DISCOVERY_MAGIC_REQ, strlen(DISCOVERY_MAGIC_REQ)) == 0) {
        char reply[128];
        int len = snprintf(reply, sizeof(reply), "%s %d",
                           DISCOVERY_MAGIC_RESP, scheduler_tcp_port);
        sendto(udp_fd, reply, (size_t)len, 0,
               (struct sockaddr *)&cli_addr, cli_len);
    }
}

int discover_scheduler_udp(int discovery_port, char *out_ip, size_t ip_len, int *out_port) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        return -1;
    }

    int broadcast = 1;
    setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));

    struct sockaddr_in bcast_addr;
    memset(&bcast_addr, 0, sizeof(bcast_addr));
    bcast_addr.sin_family = AF_INET;
    bcast_addr.sin_port = htons((uint16_t)discovery_port);
    bcast_addr.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    struct sockaddr_in lo_addr;
    memset(&lo_addr, 0, sizeof(lo_addr));
    lo_addr.sin_family = AF_INET;
    lo_addr.sin_port = htons((uint16_t)discovery_port);
    lo_addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    const char *req = DISCOVERY_MAGIC_REQ;
    size_t req_len = strlen(req);

    for (int attempt = 0; attempt < DISCOVERY_RETRIES; attempt++) {
        ssize_t s1 = sendto(fd, req, req_len, 0,
                            (struct sockaddr *)&bcast_addr, sizeof(bcast_addr));
        if (s1 < 0) {
            /* If broadcast interface is offline, also try loopback */
            sendto(fd, req, req_len, 0,
                   (struct sockaddr *)&lo_addr, sizeof(lo_addr));
        }

        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(fd, &rfds);
        struct timeval tv;
        tv.tv_sec = DISCOVERY_TIMEOUT_SEC;
        tv.tv_usec = 0;

        int ready = select(fd + 1, &rfds, NULL, NULL, &tv);
        if (ready > 0 && FD_ISSET(fd, &rfds)) {
            char buf[256];
            struct sockaddr_in from;
            socklen_t from_len = sizeof(from);
            ssize_t n = recvfrom(fd, buf, sizeof(buf) - 1, 0,
                                 (struct sockaddr *)&from, &from_len);
            if (n > 0) {
                buf[n] = '\0';
                size_t prefix_len = strlen(DISCOVERY_MAGIC_RESP);
                if (strncmp(buf, DISCOVERY_MAGIC_RESP, prefix_len) == 0) {
                    int port = atoi(buf + prefix_len);
                    if (port > 0) {
                        inet_ntop(AF_INET, &from.sin_addr, out_ip, (socklen_t)ip_len);
                        if (strcmp(out_ip, "0.0.0.0") == 0) {
                            snprintf(out_ip, ip_len, "127.0.0.1");
                        }
                        *out_port = port;
                        close(fd);
                        return 0;
                    }
                }
            }
        }
    }

    close(fd);
    return -1;
}
