/* monad3c.h -- the three language centers as ONE mmap-able file.
 * Low hardware bandwidth: mmap() it, cast, read structs in place.
 * No parse, no copy, no alloc on load. One bsearch on the word table
 * gives indices into all three stores at once.
 *
 *   [ Header ][ word blob ][ WordRec[n_words] ]
 *   [ eng: beta f64[nE] E f64[nE] age i32[nE] fire i32[nE] strat i32[nE] ]
 *   [ eng A-matrix CSR: rowptr u32[nE+1]  col u32[nnz]  w f32[nnz] ]
 *   [ wn: BoxKiteEntry[nW]  (82 bytes each, see boxkite_bin.h) ]
 *   [ phon: ix u64[nP+1]  blob (len-prefixed ARPAbet tokens) ]
 *
 * All sections 8-byte aligned; every offset is bytes from file start.
 */
#ifndef MONAD3C_H
#define MONAD3C_H
#include <stdint.h>
#define MONAD3C_MAGIC "MONAD3C\0"
typedef struct {
    char     magic[8];
    uint32_t version;         /* 1 */
    uint32_t n_words;         /* unified word table rows */
    uint32_t n_eng, n_wn, n_phon, nnz;
    double   psi_prev[16];
    uint64_t off_wordblob, off_wordrec;
    uint64_t off_beta, off_E, off_age, off_fire, off_stratum;
    uint64_t off_rowptr, off_col, off_w;
    uint64_t off_wn, off_phon_ix, off_phon_blob;
} Monad3cHeader;
typedef struct {           /* sorted by name -- bsearch on the blob */
    uint32_t name_off;     /* NUL-terminated UTF-8 in the word blob   */
    int32_t  eng_idx;      /* -1 if absent */
    int32_t  wn_idx;
    int32_t  phon_idx;
} WordRec;
#endif
