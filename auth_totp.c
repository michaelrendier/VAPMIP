/*
 * auth_totp.c — Holcus TOTP authentication (RFC 6238 / RFC 4226)
 *
 * Self-contained SHA-1 and HMAC-SHA1 — no OpenSSL dependency.
 * Keeps the "zero external deps beyond libc/libm" build constraint.
 *
 * Build: included via Makefile alongside monad.c
 *        gcc -O2 -Wall -std=c99 -o ptolemy-monad monad.c auth_totp.c -lm -lpthread
 *
 * Test:  gcc -O2 -std=c99 -DTOTP_SELFTEST -o totp_test auth_totp.c && ./totp_test
 */

#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "auth_totp.h"
#include "auth_totp_secret.h"   /* TOTP_SECRET_RAW[], TOTP_SECRET_LEN — gitignored */

/* ── SHA-1 (FIPS 180-4) ─────────────────────────────────────────────────── */

typedef struct {
    uint32_t h[5];
    uint64_t bit_len;
    uint8_t  buf[64];
    int      buf_used;
} SHA1_CTX;

#define ROL32(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

static void sha1_init(SHA1_CTX *c) {
    c->h[0] = 0x67452301u;
    c->h[1] = 0xEFCDAB89u;
    c->h[2] = 0x98BADCFEu;
    c->h[3] = 0x10325476u;
    c->h[4] = 0xC3D2E1F0u;
    c->bit_len = 0;
    c->buf_used = 0;
}

static void sha1_compress(SHA1_CTX *c, const uint8_t blk[64]) {
    uint32_t w[80], a, b, d, e, f, k, tmp;
    int i;
    for (i = 0; i < 16; i++)
        w[i] = ((uint32_t)blk[i*4]<<24)|((uint32_t)blk[i*4+1]<<16)
              |((uint32_t)blk[i*4+2]<<8)|(uint32_t)blk[i*4+3];
    for (i = 16; i < 80; i++)
        w[i] = ROL32(w[i-3]^w[i-8]^w[i-14]^w[i-16], 1);
    a = c->h[0]; b = c->h[1]; uint32_t cc = c->h[2]; d = c->h[3]; e = c->h[4];
    for (i = 0; i < 80; i++) {
        if      (i < 20) { f = (b & cc) | (~b & d); k = 0x5A827999u; }
        else if (i < 40) { f = b ^ cc ^ d;           k = 0x6ED9EBA1u; }
        else if (i < 60) { f = (b & cc)|(b & d)|(cc & d); k = 0x8F1BBCDCu; }
        else             { f = b ^ cc ^ d;           k = 0xCA62C1D6u; }
        tmp = ROL32(a,5) + f + e + k + w[i];
        e = d; d = cc; cc = ROL32(b,30); b = a; a = tmp;
    }
    c->h[0]+=a; c->h[1]+=b; c->h[2]+=cc; c->h[3]+=d; c->h[4]+=e;
}

static void sha1_update(SHA1_CTX *c, const uint8_t *data, size_t len) {
    c->bit_len += len * 8;
    while (len > 0) {
        int space = 64 - c->buf_used;
        int take  = (int)len < space ? (int)len : space;
        memcpy(c->buf + c->buf_used, data, take);
        c->buf_used += take;
        data += take;
        len  -= take;
        if (c->buf_used == 64) {
            sha1_compress(c, c->buf);
            c->buf_used = 0;
        }
    }
}

static void sha1_final(SHA1_CTX *c, uint8_t digest[20]) {
    uint64_t bl = c->bit_len;
    uint8_t pad[8];
    c->buf[c->buf_used++] = 0x80;
    if (c->buf_used > 56) {
        while (c->buf_used < 64) c->buf[c->buf_used++] = 0;
        sha1_compress(c, c->buf);
        c->buf_used = 0;
    }
    while (c->buf_used < 56) c->buf[c->buf_used++] = 0;
    for (int i = 7; i >= 0; i--) { pad[i] = bl & 0xFF; bl >>= 8; }
    memcpy(c->buf + 56, pad, 8);
    sha1_compress(c, c->buf);
    for (int i = 0; i < 5; i++) {
        digest[i*4]   = (c->h[i] >> 24) & 0xFF;
        digest[i*4+1] = (c->h[i] >> 16) & 0xFF;
        digest[i*4+2] = (c->h[i] >>  8) & 0xFF;
        digest[i*4+3] =  c->h[i]        & 0xFF;
    }
}

/* ── HMAC-SHA1 ──────────────────────────────────────────────────────────── */

static void hmac_sha1(const uint8_t *key, int klen,
                      const uint8_t *msg, int mlen,
                      uint8_t mac[20])
{
    uint8_t k[64], ipad[64], opad[64], inner[20];
    SHA1_CTX ctx;

    memset(k, 0, 64);
    if (klen > 64) {
        sha1_init(&ctx); sha1_update(&ctx, key, klen); sha1_final(&ctx, k);
    } else {
        memcpy(k, key, klen);
    }
    for (int i = 0; i < 64; i++) { ipad[i] = k[i] ^ 0x36; opad[i] = k[i] ^ 0x5C; }

    sha1_init(&ctx);
    sha1_update(&ctx, ipad, 64);
    sha1_update(&ctx, msg, mlen);
    sha1_final(&ctx, inner);

    sha1_init(&ctx);
    sha1_update(&ctx, opad, 64);
    sha1_update(&ctx, inner, 20);
    sha1_final(&ctx, mac);
}

/* ── HOTP (RFC 4226) ────────────────────────────────────────────────────── */

static uint32_t hotp(int64_t counter) {
    uint8_t msg[8], mac[20];
    for (int i = 7; i >= 0; i--) { msg[i] = counter & 0xFF; counter >>= 8; }
    hmac_sha1(TOTP_SECRET_RAW, TOTP_SECRET_LEN, msg, 8, mac);
    int offset = mac[19] & 0x0F;
    uint32_t code = ((uint32_t)(mac[offset]   & 0x7F) << 24)
                  | ((uint32_t)(mac[offset+1] & 0xFF) << 16)
                  | ((uint32_t)(mac[offset+2] & 0xFF) <<  8)
                  |  (uint32_t)(mac[offset+3] & 0xFF);
    return code % 1000000u;
}

/* ── TOTP (RFC 6238) ────────────────────────────────────────────────────── */

unsigned int auth_totp_current(void) {
    return (unsigned int)hotp((int64_t)time(NULL) / 30);
}

int auth_totp_verify(const char *six_digit_code) {
    if (!six_digit_code) return 0;
    /* reject non-numeric or wrong length */
    int len = 0;
    for (const char *p = six_digit_code; *p; p++, len++)
        if (*p < '0' || *p > '9') return 0;
    if (len != 6) return 0;

    uint32_t input = (uint32_t)atoi(six_digit_code);
    int64_t  t     = (int64_t)time(NULL) / 30;

    /* check t-1, t, t+1 — ±30 s drift tolerance */
    for (int d = -1; d <= 1; d++)
        if (hotp(t + d) == input) return 1;
    return 0;
}

/* ── Self-test (build with -DTOTP_SELFTEST) ─────────────────────────────── */
#ifdef TOTP_SELFTEST
int main(void) {
    printf("Holcus TOTP self-test\n");
    printf("Current code: %06u\n", auth_totp_current());
    printf("Enter code from Google Authenticator: ");
    char buf[16];
    if (!fgets(buf, sizeof(buf), stdin)) return 1;
    buf[strcspn(buf, "\n")] = 0;
    if (auth_totp_verify(buf)) {
        printf("VALID — authentication successful\n");
        return 0;
    } else {
        printf("INVALID — code rejected\n");
        return 1;
    }
}
#endif
