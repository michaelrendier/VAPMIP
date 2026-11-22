/*
 * PtolC/tokenizer.c — Text tokeniser for the C Monad.
 */

#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include "tokenizer.h"
#include "unicode.h"
#include "alphabet.h"
#include "dprint.h"

static void tok_push(char ***out, int *cap, int *count, const char *buf, int blen)
{
    char *t = malloc(blen + 1);
    memcpy(t, buf, blen); t[blen] = '\0';
    if (*count >= *cap) { *cap *= 2; *out = realloc(*out, *cap * sizeof(char *)); }
    (*out)[(*count)++] = t;
}

/* Unicode tokeniser: a word is a maximal run of letters and combining marks (General_Category L*, M*) and apostrophes,
 * lower-cased code point by code point.  Every Han character is a token by itself (there is no word segmenter).
 * A token must have at least two code points (a Han character is one) and must not start with an apostrophe.
 * Invalid UTF-8 bytes are separators.  U+2019 is read as the apostrophe. */
char **tok_split(const char *text, int *count)
{
    int   cap  = 512;
    char **out = malloc(cap * sizeof(char *));
    *count = 0;
    if (!out || !text) return out;

    int   tlen = strlen(text);
    char *buf  = malloc(tlen * 2 + 8);
    if (!buf) return out;
    int blen = 0, ncp = 0;
#if defined(HAN_RUN)
    int buf_han = 0;
#endif
    const char *p = text;

    for (;;) {
        uint32_t cp = *p ? u8_next(&p) : 0;                 /* 0: end of text, flush */
#if defined(ALPHABET_TABLE)
        /* Table build: a letter is any character of the language's alphabet (U+2019 counts as the apostrophe where the alphabet has one). */
        int word_char = cp && alpha_rank(u_lower(cp == 0x2019 ? '\'' : cp)) > 0;
#elif defined(ALPHABET_ASCII95)
        /* English build: the alphabet is ASCII.  A letter is [A-Za-z] or an apostrophe; every other code point separates words. */
        int word_char = cp && ((cp < 128 && isalpha((int)cp)) || cp == '\'');
#else
        int word_char = cp && (u_is_word(cp) || cp == '\'' || cp == 0x2019);
#endif

#if defined(HAN_RUN)
        /* HAN_RUN: a run of Han characters is ONE token (a word); the corpus is segmented into words before it reaches the engine
         * (tools/exp_v2.py, longest match over the word list).  A Han word of one character is a word; a Latin word still needs two. */
        if (word_char && u_is_han(cp)) {
            if (ncp > 0 && !buf_han) {
                if (ncp >= 2 && buf[0] != '\'') tok_push(&out, &cap, count, buf, blen);
                blen = 0; ncp = 0;
            }
            blen += u8_put(cp, buf + blen); ncp++; buf_han = 1;
            DPRINT_I("tok.han_run_len", ncp);
        } else if (word_char) {
            if (ncp > 0 && buf_han) {
                tok_push(&out, &cap, count, buf, blen);
                DPRINT_S("tok.push_han", buf); DPRINT_I("tok.count", *count);
                blen = 0; ncp = 0; buf_han = 0;
            }
            if (cp == 0x2019) cp = '\'';
            blen += u8_put(u_lower(cp), buf + blen);
            ncp++;
        } else if (ncp > 0) {
            if ((buf_han || ncp >= 2) && buf[0] != '\'') {
                tok_push(&out, &cap, count, buf, blen);
                DPRINT_I("tok.count", *count);
            }
            blen = 0; ncp = 0; buf_han = 0;
        }
#else
        if (word_char && u_is_han(cp)) {
            if (ncp >= 2 && buf[0] != '\'') tok_push(&out, &cap, count, buf, blen);
            blen = 0; ncp = 0;
            char one[4]; int n = u8_put(cp, one);
            tok_push(&out, &cap, count, one, n);
        } else if (word_char) {
            if (cp == 0x2019) cp = '\'';
            blen += u8_put(u_lower(cp), buf + blen);
            ncp++;
        } else if (ncp > 0) {
            if (ncp >= 2 && buf[0] != '\'') tok_push(&out, &cap, count, buf, blen);
            blen = 0; ncp = 0;
        }
#endif
        if (!cp) break;
    }

    free(buf);
    return out;
}

void tok_free(char **tokens, int count)
{
    if (!tokens) return;
    for (int i = 0; i < count; i++) free(tokens[i]);
    free(tokens);
}
