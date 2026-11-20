/*
 * boxkite_bin.h — the shared shape of a box-kite context snapshot.
 *
 * One BoxKiteEntry per WordNet synset (first-sense-per-word convention,
 * same as sentence_context.py's resolve_word_synset stub). The SAME 19
 * dimensions, same order, as wordnet_boxkite.py's RELATION_METHODS —
 * verified 2026-08-25 against the real C WordNet library (wntest.c):
 * bank's first noun sense gives HYPERPTR=1, HYPOPTR=2 here, exactly
 * matching Python's {'hypernyms':1,'hyponyms':2} for bank.n.01.
 *
 * c_monad_wordnet.bin  = C_MONAD_WORDNET_MAGIC header + N_ENTRIES structs,
 * written by dump_boxkite_bin.c, read by boxkite_lookup.c or the future
 * pure-C monad. wordnet_boxkite.py's export_pickle() writes the SAME
 * fields (as a list of dicts) to a .pkl on the Python side — two
 * different serializations of one schema, not two different schemas.
 *
 * depth_weight is the ONE adjustable knob this file defines: a per-entry
 * scalar (default 1.0) that scales the whole relation vector wherever it
 * is CONSUMED (sentence-root summing, nearest-neighbor distance) — how
 * strongly this entry's context counts, not a multi-hop graph-depth
 * traversal. That distinction is deliberate, not an oversight: literal
 * multi-hop (grandparent-hypernym-level) counting is real future work,
 * not built here. set_depth_weight()/get_depth_weight() below are the
 * "proper functions" — they mutate ONE entry in place (fixed record size
 * makes an in-place fseek+fwrite exact, no full-file rewrite needed) and
 * have a byte-identical counterpart in wordnet_boxkite.py.
 */

#ifndef BOXKITE_BIN_H
#define BOXKITE_BIN_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

#define BOXKITE_MAGIC     "BXKT"
#define BOXKITE_VERSION   1
#define N_RELATIONS       19
#define BOXKITE_WORD_LEN  32

/* Same order as wordnet_boxkite.py's RELATION_METHODS — index i here IS
 * index i there. Kept as a comment, not a duplicated string table, so
 * there is exactly one place (wordnet_boxkite.py) that names them. */
/*
 *  0 hypernyms          1 instance_hypernyms   2 hyponyms
 *  3 instance_hyponyms  4 member_holonyms      5 substance_holonyms
 *  6 part_holonyms      7 member_meronyms      8 substance_meronyms
 *  9 part_meronyms     10 attributes           11 entailments
 * 12 causes            13 also_sees            14 verb_groups
 * 15 similar_tos       16 topic_domains        17 region_domains
 * 18 usage_domains
 */

#pragma pack(push, 1)

typedef struct {
    char     magic[4];       /* "BXKT" */
    uint32_t version;        /* BOXKITE_VERSION */
    uint32_t n_entries;
    uint32_t entry_size;     /* sizeof(BoxKiteEntry) — a self-describing file */
} BoxKiteHeader;

typedef struct {
    char     word[BOXKITE_WORD_LEN];  /* first lemma, NUL-terminated */
    uint8_t  pos;                     /* 1=NOUN 2=VERB 3=ADJ 4=ADV (wn.h values) */
    uint8_t  _pad[3];
    uint32_t synset_offset;           /* WordNet's own offset — the stable id */
    int16_t  vector[N_RELATIONS];     /* compress_count()-ed relation exponents */
    float    depth_weight;            /* the one adjustable knob — default 1.0 */
} BoxKiteEntry;

#pragma pack(pop)

/* ── the shared functions — same names/shapes, both sides ──────────────── */

/* Read the header + all entries from `path`. Returns entry count (>=0) or
 * -1 on error; *out is malloc'd, caller frees. */
static inline int boxkite_load(const char *path, BoxKiteEntry **out) {
    FILE *f = fopen(path, "rb");
    if (!f) return -1;
    BoxKiteHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1
        || memcmp(hdr.magic, BOXKITE_MAGIC, 4) != 0
        || hdr.entry_size != sizeof(BoxKiteEntry)) {
        fclose(f);
        return -1;
    }
    BoxKiteEntry *entries = (BoxKiteEntry *)malloc((size_t)hdr.n_entries * sizeof(BoxKiteEntry));
    if (!entries) { fclose(f); return -1; }
    size_t got = fread(entries, sizeof(BoxKiteEntry), hdr.n_entries, f);
    fclose(f);
    if (got != hdr.n_entries) { free(entries); return -1; }
    *out = entries;
    return (int)hdr.n_entries;
}

/* Linear lookup by word (case-sensitive, first match). Returns index or -1.
 * Linear is fine here: this is a lookup/diagnostic helper, not the hot
 * path of a future monad — that would sort/hash, not built here. */
static inline int boxkite_find(const BoxKiteEntry *entries, int n, const char *word) {
    for (int i = 0; i < n; i++)
        if (strncmp(entries[i].word, word, BOXKITE_WORD_LEN) == 0)
            return i;
    return -1;
}

/* Mutate ONE entry's depth_weight, in place, on disk — an fseek to the
 * exact record offset (header + index*entry_size) and a single fwrite of
 * that one field. Does not touch the rest of the file. Returns 0 on
 * success. */
static inline int boxkite_set_depth_weight(const char *path, int index, float weight) {
    FILE *f = fopen(path, "r+b");
    if (!f) return -1;
    long off = (long)sizeof(BoxKiteHeader)
             + (long)index * (long)sizeof(BoxKiteEntry)
             + (long)offsetof(BoxKiteEntry, depth_weight);
    if (fseek(f, off, SEEK_SET) != 0) { fclose(f); return -1; }
    size_t wrote = fwrite(&weight, sizeof(weight), 1, f);
    fclose(f);
    return wrote == 1 ? 0 : -1;
}

static inline float boxkite_get_depth_weight(const BoxKiteEntry *entries, int index) {
    return entries[index].depth_weight;
}

#endif /* BOXKITE_BIN_H */
