/*
 * wntest.c — proof that wordnet-dev's C API reproduces wordnet_boxkite.py's
 * context_vector exactly, for a real word. Build: gcc -O2 -o wntest wntest.c
 * -lwordnet   Run: WNSEARCHDIR=/usr/share/wordnet ./wntest bank
 *
 * Checked 2026-08-25: bank's first noun sense counts HYPERPTR=1, HYPOPTR=2
 * from read_synset()'s own ptrtyp[] array — exactly Python's
 * {'hypernyms': 1, 'hyponyms': 2} for bank.n.01. Groundwork for a future
 * pure-C port of the WordNet-relational composter, not the port itself.
 */
#include <stdio.h>
#include <string.h>
#include "wn.h"

int main(int argc, char **argv) {
    const char *word = argc > 1 ? argv[1] : "bank";
    if (wninit() != 0) { fprintf(stderr, "wninit failed\n"); return 1; }
    printf("wnrelease: %s\n", wnrelease);

    IndexPtr idx = index_lookup((char*)word, NOUN);
    if (!idx) { printf("no noun index for '%s'\n", word); return 1; }
    printf("word=%s off_cnt=%d sense_cnt=%d\n", idx->wd, idx->off_cnt, idx->sense_cnt);

    long first_offset = idx->offset[0];
    SynsetPtr syn = read_synset(NOUN, first_offset, (char*)word);
    if (!syn) { printf("read_synset failed\n"); return 1; }
    printf("gloss: %s\n", syn->defn);
    printf("ptrcount: %d\n", syn->ptrcount);
    int counts[MAXPTR+1]; memset(counts, 0, sizeof(counts));
    for (int i = 0; i < syn->ptrcount; i++) {
        int t = syn->ptrtyp[i];
        if (t >= 0 && t <= MAXPTR) counts[t]++;
        printf("  [%d] type=%d(%s) ppos=%d pfrm=%d pto=%d\n",
               i, t, (t>=0 && t<=LASTTYPE) ? ptrtyp[t] : "?",
               syn->ppos[i], syn->pfrm[i], syn->pto[i]);
    }
    printf("HYPERPTR(%d)=%d  HYPOPTR(%d)=%d  ISMEMBERPTR(%d)=%d  HASPARTPTR(%d)=%d\n",
           HYPERPTR, counts[HYPERPTR], HYPOPTR, counts[HYPOPTR],
           ISMEMBERPTR, counts[ISMEMBERPTR], HASPARTPTR, counts[HASPARTPTR]);
    free_synset(syn);
    free_index(idx);
    return 0;
}
