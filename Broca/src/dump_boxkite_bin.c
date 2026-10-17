/*
 * dump_boxkite_bin.c — builds c_monad_wordnet.bin: one BoxKiteEntry per
 * WordNet synset, first-sense-per-word, same 19-dim relation vector as
 * wordnet_boxkite.py's context_vector (verified against it — see
 * wntest.c / boxkite_bin.h). A real box-kite SNAPSHOT dataset: fread the
 * file, you have the array, no live WordNet C calls needed at runtime.
 *
 * Build:  gcc -O2 -o dump_boxkite_bin dump_boxkite_bin.c -lwordnet
 * Run:    WNSEARCHDIR=/usr/share/wordnet ./dump_boxkite_bin c_monad_wordnet.bin
 *
 * Enumeration note, corrected after checking wn.h rather than assuming:
 * getindex() is a FUZZY SEARCH for one word (hyphen/underscore variants),
 * not a sequential-scan iterator — there is no library call to "give me
 * the next index entry." index.noun/verb/adj/adv are plain text files,
 * alphabetically one headword per line, so this reads those directly
 * (first whitespace-delimited token per line = the word) and calls the
 * documented index_lookup() (exact match) for each — first sense only.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "wn.h"
#include "boxkite_bin.h"

/* Mirrors wordnet_boxkite.py's RELATION_METHODS, same order, same count
 * (19) — index i here is index i there. */
static const int REL_PTRTYPE[N_RELATIONS] = {
    HYPERPTR, INSTANCE, HYPOPTR, INSTANCES,
    ISMEMBERPTR, ISSTUFFPTR, ISPARTPTR,
    HASMEMBERPTR, HASSTUFFPTR, HASPARTPTR,
    ATTRIBUTE, ENTAILPTR, CAUSETO, SEEALSOPTR, VERBGROUP, SIMPTR,
    CLASSIF_CATEGORY, CLASSIF_REGIONAL, CLASSIF_USAGE,
};

/* compress_count(n) = round(log2(n+1)) — wordnet_boxkite.py's own
 * function, ported verbatim (same formula, same reasoning: the COUNT is
 * compressed before becoming an exponent, not "the exponent gets
 * logged" — see that file's compress_count() docstring). */
static int16_t compress_count(int n) {
    if (n < 0) n = 0;
    double v = log2((double)n + 1.0);
    return (int16_t)(v < 0 ? (int)(v - 0.5) : (int)(v + 0.5));
}

/* Tally one synset's raw pointer-type counts, then compress_count() each
 * of the 19 tracked types into `out`. Only counts SYNSET-level pointers
 * (pfrm==0 && pto==0) — a word-specific (lexical) pointer like a
 * particular DERIVATION link is not a relation of the synset as a whole,
 * and NLTK's synset-level accessors don't count those either. */
static void synset_context_vector(SynsetPtr syn, int16_t out[N_RELATIONS]) {
    int raw[MAXPTR + 1];
    memset(raw, 0, sizeof(raw));
    for (int i = 0; i < syn->ptrcount; i++) {
        if (syn->pfrm[i] != 0 || syn->pto[i] != 0) continue;  /* lexical, skip */
        int t = syn->ptrtyp[i];
        if (t >= 0 && t <= MAXPTR) raw[t]++;
    }
    for (int r = 0; r < N_RELATIONS; r++)
        out[r] = compress_count(raw[REL_PTRTYPE[r]]);
}

static const char *index_filename(int pos) {
    switch (pos) {
        case NOUN: return "/usr/share/wordnet/index.noun";
        case VERB: return "/usr/share/wordnet/index.verb";
        case ADJ:  return "/usr/share/wordnet/index.adj";
        case ADV:  return "/usr/share/wordnet/index.adv";
        default:   return NULL;
    }
}

static int dump_pos(FILE *out, int pos, int *count) {
    const char *fname = index_filename(pos);
    FILE *idxf = fname ? fopen(fname, "r") : NULL;
    if (!idxf) { fprintf(stderr, "  can't open %s\n", fname ? fname : "?"); return 0; }

    char line[LINEBUF];
    int wcount = 0;
    while (fgets(line, sizeof(line), idxf)) {
        if (line[0] == ' ') continue;   /* license header lines start with a space */
        char word[BOXKITE_WORD_LEN];
        if (sscanf(line, "%31s", word) != 1) continue;

        IndexPtr idx = index_lookup(word, pos);
        if (!idx) continue;
        long first_offset = idx->offset[0];
        SynsetPtr syn = read_synset(pos, first_offset, word);
        if (syn) {
            BoxKiteEntry e;
            memset(&e, 0, sizeof(e));
            strncpy(e.word, word, BOXKITE_WORD_LEN - 1);
            e.pos = (uint8_t)pos;
            e.synset_offset = (uint32_t)first_offset;
            synset_context_vector(syn, e.vector);
            e.depth_weight = 1.0f;
            fwrite(&e, sizeof(e), 1, out);
            wcount++;
            free_synset(syn);
        }
        free_index(idx);
    }
    fclose(idxf);
    *count += wcount;
    return wcount;
}

int main(int argc, char **argv) {
    const char *out_path = argc > 1 ? argv[1] : "c_monad_wordnet.bin";

    if (wninit() != 0) { fprintf(stderr, "wninit failed — set WNSEARCHDIR\n"); return 1; }

    FILE *tmp = tmpfile();
    if (!tmp) { perror("tmpfile"); return 1; }

    int total = 0;
    fprintf(stderr, "[dump_boxkite_bin] nouns...\n");
    dump_pos(tmp, NOUN, &total);
    fprintf(stderr, "[dump_boxkite_bin] verbs...\n");
    dump_pos(tmp, VERB, &total);
    fprintf(stderr, "[dump_boxkite_bin] adjectives...\n");
    dump_pos(tmp, ADJ, &total);
    fprintf(stderr, "[dump_boxkite_bin] adverbs...\n");
    dump_pos(tmp, ADV, &total);

    FILE *out = fopen(out_path, "wb");
    if (!out) { perror("fopen out"); return 1; }
    BoxKiteHeader hdr;
    memcpy(hdr.magic, BOXKITE_MAGIC, 4);
    hdr.version = BOXKITE_VERSION;
    hdr.n_entries = (uint32_t)total;
    hdr.entry_size = (uint32_t)sizeof(BoxKiteEntry);
    fwrite(&hdr, sizeof(hdr), 1, out);

    rewind(tmp);
    char buf[65536];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), tmp)) > 0)
        fwrite(buf, 1, n, out);
    fclose(tmp);
    fclose(out);

    fprintf(stderr, "[dump_boxkite_bin] %d entries -> %s (%zu bytes)\n",
           total, out_path, sizeof(hdr) + (size_t)total * sizeof(BoxKiteEntry));
    return 0;
}
