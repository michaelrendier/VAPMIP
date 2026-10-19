/*
 * PtolC/alphabet.h — the per-language alphabet of the table build (-DALPHABET_TABLE).
 * ALPHABET_HEADER names a generated header (tools/gen_alphabet.py) that defines ALPHA[ALPHA_N], the sorted code points of the language's writing.
 * alpha_rank(cp) is the character's digit: its 1-based position in ALPHA, or 0 when it is not in the alphabet.
 */
#ifndef ALPHABET_H
#define ALPHABET_H
#ifdef ALPHABET_TABLE
#include <stdint.h>
#include ALPHABET_HEADER
static inline int alpha_rank(uint32_t cp)
{
    int lo = 0, hi = ALPHA_N - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (cp < ALPHA[mid]) hi = mid - 1;
        else if (cp > ALPHA[mid]) lo = mid + 1;
        else return mid + 1;
    }
    return 0;
}
#endif
#endif
