/* wn_c_test.c — C against the native WordNet 3.0 library (wordnet-dev: wn.h, libwordnet).
 * Looks up the noun "tree": the number of senses and the first gloss, and the hypernym pointer count of sense 1.
 * Build:  cc -o wn_c_test wn_c_test.c -lwordnet
 * Needs WNHOME or /usr/share/wordnet (the dict files).  This is WordNet 3.0 only; NLTK, VerbNet, SemCor,
 * FrameNet are reachable from C through nltk_embed_test.c (embedded Python), not through a C API. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wn.h>

int main(void) {
    if (wninit() != 0) { fprintf(stderr, "wninit failed: is /usr/share/wordnet present?\n"); return 1; }
    char word[] = "tree";
    int senses = in_wn(word, NOUN);
    if (!(senses & (1u << NOUN))) { fprintf(stderr, "no noun entry\n"); return 1; }
    char *res = findtheinfo(word, NOUN, HYPERPTR, 1);
    printf("tree (noun), first sense, hypernym chain:\n%s", res ? res : "(none)\n");
    SynsetPtr s = findtheinfo_ds(word, NOUN, HYPERPTR, 1);
    if (s) { printf("gloss of the first sense: %s\n", s->defn); free_syns(s); }
    return 0;
}
