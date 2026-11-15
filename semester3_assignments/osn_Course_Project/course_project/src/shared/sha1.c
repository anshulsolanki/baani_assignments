#include "net_utils.h"
#include <stdio.h>
#include <string.h>

struct sha1_ctx {
    uint32_t state[5];
    uint64_t count;
    uint8_t buffer[64];
};

static uint32_t rol32(uint32_t val, int bits) {
    return (val << bits) | (val >> (32 - bits));
}

static void sha1_transform(uint32_t state[5], const uint8_t block[64]) {
    uint32_t w[80];
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i * 4 + 0] << 24) |
               ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) |
               ((uint32_t)block[i * 4 + 3]);
    }
    for (int i = 16; i < 80; i++) {
        w[i] = rol32(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
    }

    uint32_t a = state[0];
    uint32_t b = state[1];
    uint32_t c = state[2];
    uint32_t d = state[3];
    uint32_t e = state[4];

    for (int i = 0; i < 80; i++) {
        uint32_t f = 0;
        uint32_t k = 0;
        if (i < 20) {
            f = (b & c) | ((~b) & d);
            k = 0x5A827999;
        } else if (i < 40) {
            f = b ^ c ^ d;
            k = 0x6ED9EBA1;
        } else if (i < 60) {
            f = (b & c) | (b & d) | (c & d);
            k = 0x8F1BBCDC;
        } else {
            f = b ^ c ^ d;
            k = 0xCA62C1D6;
        }
        uint32_t temp = rol32(a, 5) + f + e + k + w[i];
        e = d;
        d = c;
        c = rol32(b, 30);
        b = a;
        a = temp;
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
}

static void sha1_init(struct sha1_ctx *ctx) {
    ctx->state[0] = 0x67452301;
    ctx->state[1] = 0xEFCDAB89;
    ctx->state[2] = 0x98BADCFE;
    ctx->state[3] = 0x10325476;
    ctx->state[4] = 0xC3D2E1F0;
    ctx->count = 0;
}

static void sha1_update(struct sha1_ctx *ctx, const uint8_t *data, size_t len) {
    size_t idx = (size_t)(ctx->count & 63);
    ctx->count += len;

    size_t i = 0;
    if (idx > 0) {
        size_t take = 64 - idx;
        if (len < take) {
            memcpy(ctx->buffer + idx, data, len);
            return;
        }
        memcpy(ctx->buffer + idx, data, take);
        sha1_transform(ctx->state, ctx->buffer);
        i += take;
    }

    for (; i + 64 <= len; i += 64) {
        sha1_transform(ctx->state, data + i);
    }

    if (i < len) {
        memcpy(ctx->buffer, data + i, len - i);
    }
}

static void sha1_final(struct sha1_ctx *ctx, char out_hex[41]) {
    uint64_t total_bits = ctx->count * 8;
    uint8_t pad = 0x80;
    sha1_update(ctx, &pad, 1);

    pad = 0x00;
    while ((ctx->count & 63) != 56) {
        sha1_update(ctx, &pad, 1);
    }

    uint8_t len_bytes[8];
    for (int i = 0; i < 8; i++) {
        len_bytes[7 - i] = (uint8_t)(total_bits >> (i * 8));
    }
    sha1_update(ctx, len_bytes, 8);

    for (int i = 0; i < 5; i++) {
        snprintf(out_hex + (i * 8), 9, "%08x", ctx->state[i]);
    }
    out_hex[40] = '\0';
}

void sha1_bytes(const uint8_t *data, size_t len, char out_hex[41]) {
    struct sha1_ctx ctx;
    sha1_init(&ctx);
    sha1_update(&ctx, data, len);
    sha1_final(&ctx, out_hex);
}

int sha1_file(const char *path, char out_hex[41], int32_t *out_size) {
    FILE *fp = fopen(path, "rb");
    if (fp == NULL) {
        return -1;
    }

    struct sha1_ctx ctx;
    sha1_init(&ctx);

    uint8_t buf[8192];
    int32_t total = 0;
    size_t n = 0;
    while ((n = fread(buf, 1, sizeof(buf), fp)) > 0) {
        sha1_update(&ctx, buf, n);
        total += (int32_t)n;
    }
    fclose(fp);

    sha1_final(&ctx, out_hex);
    if (out_size != NULL) {
        *out_size = total;
    }
    return 0;
}
