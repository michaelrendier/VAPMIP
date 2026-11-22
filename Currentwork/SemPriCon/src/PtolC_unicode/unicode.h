/*
 * PtolC/unicode.h — Unicode helpers for the C Monad (SemPriCon upgrade, 2026-10-18).
 *
 * The 2026-05 build addressed and tokenised BYTES: ASCII letters only, every other byte a separator or a zero digit.
 * This build addresses and tokenises CODE POINTS (UTF-8 in, UTF-8 out).  The character classes come from unicode_tables.h,
 * generated from Python's unicodedata (version in UNICODE_DATA_VERSION), so behaviour does not depend on the C library's locale.
 * Input is expected in NFC; the ingest step is responsible for normalising (the monad does not normalise).
 */
#ifndef UNICODE_H
#define UNICODE_H
#include <stdint.h>

/* Decode one code point at *s and advance *s.  An invalid byte yields U+FFFD and consumes one byte. */
uint32_t u8_next(const char **s);
/* Encode cp as UTF-8 into out (no terminator); returns the byte count, 1..4. */
int      u8_put(uint32_t cp, char *out);
/* Number of code points in a UTF-8 string. */
int      u8_len(const char *s);

int      u_is_word(uint32_t cp);        /* General_Category L* or M* */
int      u_is_han(uint32_t cp);         /* CJK ideograph blocks: one token per character */
int      u_is_latin(uint32_t cp);       /* Latin-script letter */
int      u_is_vowel(uint32_t cp);       /* lower-case Latin vowel (accented included) */
uint32_t u_lower(uint32_t cp);          /* simple lower-case mapping */
int      u_is_sentence_end(uint32_t cp);/* . ! ? \n and the CJK / fullwidth / ellipsis equivalents */

#endif
