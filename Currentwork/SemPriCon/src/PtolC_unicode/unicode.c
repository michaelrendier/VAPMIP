/*
 * PtolC/unicode.c — see unicode.h.
 */
#include <stddef.h>
#include "unicode.h"
#include "unicode_tables.h"

uint32_t u8_next(const char **s)
{
    const unsigned char *p = (const unsigned char *)*s;
    uint32_t c = p[0];
    if (c < 0x80)                         { *s += 1; return c; }
    if (c >= 0xC2 && c <= 0xDF && (p[1] & 0xC0) == 0x80)
                                          { *s += 2; return ((c & 0x1F) << 6) | (p[1] & 0x3F); }
    if (c >= 0xE0 && c <= 0xEF && (p[1] & 0xC0) == 0x80 && (p[2] & 0xC0) == 0x80) {
        uint32_t cp = ((c & 0x0F) << 12) | ((p[1] & 0x3F) << 6) | (p[2] & 0x3F);
        if (cp >= 0x800 && !(cp >= 0xD800 && cp <= 0xDFFF)) { *s += 3; return cp; }
    }
    if (c >= 0xF0 && c <= 0xF4 && (p[1] & 0xC0) == 0x80 && (p[2] & 0xC0) == 0x80 && (p[3] & 0xC0) == 0x80) {
        uint32_t cp = ((c & 0x07) << 18) | ((p[1] & 0x3F) << 12) | ((p[2] & 0x3F) << 6) | (p[3] & 0x3F);
        if (cp >= 0x10000 && cp <= 0x10FFFF) { *s += 4; return cp; }
    }
    *s += 1;
    return 0xFFFD;
}

int u8_put(uint32_t cp, char *out)
{
    if (cp < 0x80)    { out[0] = (char)cp; return 1; }
    if (cp < 0x800)   { out[0] = (char)(0xC0 | (cp >> 6)); out[1] = (char)(0x80 | (cp & 0x3F)); return 2; }
    if (cp < 0x10000) { out[0] = (char)(0xE0 | (cp >> 12)); out[1] = (char)(0x80 | ((cp >> 6) & 0x3F)); out[2] = (char)(0x80 | (cp & 0x3F)); return 3; }
    out[0] = (char)(0xF0 | (cp >> 18)); out[1] = (char)(0x80 | ((cp >> 12) & 0x3F));
    out[2] = (char)(0x80 | ((cp >> 6) & 0x3F)); out[3] = (char)(0x80 | (cp & 0x3F));
    return 4;
}

int u8_len(const char *s)
{
    int n = 0;
    while (*s) { u8_next(&s); n++; }
    return n;
}

static int in_ranges(const uint32_t (*r)[2], int n, uint32_t cp)
{
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (cp < r[mid][0]) hi = mid - 1;
        else if (cp > r[mid][1]) lo = mid + 1;
        else return 1;
    }
    return 0;
}

int u_is_word(uint32_t cp)  { return in_ranges(U_WORD,  U_WORD_N,  cp); }
int u_is_han(uint32_t cp)   { return in_ranges(U_HAN,   U_HAN_N,   cp); }
int u_is_latin(uint32_t cp) { return in_ranges(U_LATIN, U_LATIN_N, cp); }

int u_is_vowel(uint32_t cp)
{
    int lo = 0, hi = U_VOWEL_N - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (cp < U_VOWEL[mid]) hi = mid - 1;
        else if (cp > U_VOWEL[mid]) lo = mid + 1;
        else return 1;
    }
    return 0;
}

uint32_t u_lower(uint32_t cp)
{
    int lo = 0, hi = U_LOWER_N - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (cp < U_LOWER[mid][0]) hi = mid - 1;
        else if (cp > U_LOWER[mid][0]) lo = mid + 1;
        else return U_LOWER[mid][1];
    }
    return cp;
}

int u_is_sentence_end(uint32_t cp)
{
    switch (cp) {
        case '.': case '!': case '?': case '\n':
        case 0x2026:                 /* …  */
        case 0x203C: case 0x2047: case 0x2048: case 0x2049:   /* ‼ ⁇ ⁈ ⁉ */
        case 0x3002:                 /* 。 */
        case 0xFF01: case 0xFF1F: case 0xFF0E:                /* ！ ？ ． */
            return 1;
        default: return 0;
    }
}
