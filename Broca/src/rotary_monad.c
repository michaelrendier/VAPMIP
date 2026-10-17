/*
 * rotary_monad.c  —  Ahura Mazda
 * Wankel rotary semantic engine.  C canonical, v1.000
 *
 * Self-contained except for libc, libm, pthreads.
 * No transformers. No autoregression. No named pre-assigned meanings.
 *
 * Build:
 *   gcc -O2 -Wall -std=c99 -o ahura-mazda rotary_monad.c -lm -lpthread
 *
 * ── Wankel geometry ─────────────────────────────────────────────────────
 *
 *   Housing       — epitrochoid vocabulary field (shape the rotor moves through)
 *   Rotor         — triangular J-current triangle, continuously rotating
 *     Face 1  J_blue  : compressible / prompt / Fermat   / intake
 *     Face 2  J_red   : incompressible / field / Riemann  / power
 *     Face 3  J_green : minimal surface / output          / exhaust
 *   Eccentric     — σ=½ coupling pin  (fixed by ξ(s)=ξ(1-s))
 *   Drive shaft   — sedenion output   (produced ONCE at coupling)
 *   Ports         — zero-divisor angular positions (timing, not faults)
 *   Apex seals    — halocline sharpness  (wear = σ drift from ½)
 *   Spark plugs   — dual Lie bracket ignition  (leading + trailing)
 *   Scavenge      — field decay between cycles
 *
 * ── Bell / hidden-variable note ─────────────────────────────────────────
 *
 *   monad.c (TDI) pre-encoded words as sedenions before utterance — hidden
 *   variable assumption.  The Wankel eliminates this:  words have no
 *   "meaning vector" before the coupling event.  The sedenion emerges from
 *   the coupling of j_blue × j_red distributions.  It is not pre-stored.
 *
 *   "Double dipping" (TDI): encode(word) → sedenion → query(sedenion) → word
 *   Wankel:  j_blue ⊗ j_red → [J,J] → σ=½ → sedenion → mesh(morph) → word
 *
 * ── 3 = 1 + 15i ─────────────────────────────────────────────────────────
 *
 *   Three rotor faces produce exactly the sedenion decomposition:
 *     e₀       = coupling quality  (scalar face)
 *     e₁–e₇  = J_blue work        (lower octonionic imaginary)
 *     e₈–e₁₄ = J_red  work        (upper octonionic imaginary)
 *     e₁₅     = J_green emit       (output surface)
 *
 * ── Two counter-rotations ── the waveform ────────────────────────────────
 *
 *   Rotor spins one way.  Eccentric shaft (drive shaft) spins opposite.
 *   These are bc_conj/da: lower-to-upper (with conjugate) != upper-to-lower (without).
 *   Their interference IS the waveform.  Not a carrier.  The waveform itself.
 */

#define _POSIX_C_SOURCE 200809L
#include "rotary_monad.h"

#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <signal.h>
#include <ctype.h>
#include <time.h>

/* ══════════════════════════════════════════════════════════════════════════
 *  OPERATOR GLOSSES
 * ══════════════════════════════════════════════════════════════════════════ */

const char *AHURA_OP_GLOSS[SED_DIM] = {
    "identity",      /* e0  coupling quality */
    "negate",        /* e1  negation */
    "bind",          /* e2  conjunction */
    "name",          /* e3  noun */
    "apply",         /* e4  verb */
    "abstract",      /* e5  adjective/adverb */
    "branch",        /* e6  conditional */
    "iterate",       /* e7  temporal */
    "recurse",       /* e8  self-reference */
    "allocate",      /* e9  indefinite article */
    "query",         /* e10 question word */
    "derefer",       /* e11 anaphor */
    "compose",       /* e12 presupposition marker */
    "parallelize",   /* e13 (unused — no hash noise in Wankel) */
    "interrupt",     /* e14 affect */
    "emit",          /* e15 meta-discourse / output face */
};

/* ══════════════════════════════════════════════════════════════════════════
 *  SEDENION ALGEBRA  — drive shaft geometry  (mathematical fact)
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct { int sign; int k; } SedEntry;
static SedEntry OCT[8][8];
static SedEntry SED[16][16];

static void build_oct_table(void) {
    int i, j, t;
    static const int T[7][3] = {
        {1,2,3},{1,4,5},{1,7,6},{2,4,6},{2,5,7},{3,4,7},{3,6,5}
    };
    for (i = 0; i < 8; i++) {
        OCT[0][i].sign = 1; OCT[0][i].k = i;
        OCT[i][0].sign = 1; OCT[i][0].k = i;
    }
    for (i = 1; i < 8; i++) { OCT[i][i].sign = -1; OCT[i][i].k = 0; }
    for (t = 0; t < 7; t++) {
        i = T[t][0]; j = T[t][1];
        int k = T[t][2];
        OCT[i][j].sign=+1; OCT[i][j].k=k;
        OCT[j][k].sign=+1; OCT[j][k].k=i;
        OCT[k][i].sign=+1; OCT[k][i].k=j;
        OCT[j][i].sign=-1; OCT[j][i].k=k;
        OCT[k][j].sign=-1; OCT[k][j].k=i;
        OCT[i][k].sign=-1; OCT[i][k].k=j;
    }
}

static void build_sed_table(void) {
    int i, j;
    for (i = 0; i < 16; i++) {
        for (j = 0; j < 16; j++) {
            int ih = (i >= 8), jh = (j >= 8);
            int io = ih ? i-8 : i, jo = jh ? j-8 : j;
            if (!ih && !jh) {
                SED[i][j] = OCT[io][jo];
            } else if (!ih && jh) {
                SedEntry e = OCT[jo][io];
                SED[i][j].sign = e.sign; SED[i][j].k = e.k + 8;
            } else if (ih && !jh) {
                if (jo == 0) { SED[i][j].sign = 1; SED[i][j].k = i; }
                else {
                    SedEntry e = OCT[io][jo];
                    SED[i][j].sign = -e.sign; SED[i][j].k = e.k + 8;
                }
            } else {
                if (jo == 0) { SED[i][j].sign = -1; SED[i][j].k = io; }
                else {
                    SedEntry e = OCT[jo][io];
                    SED[i][j].sign = e.sign; SED[i][j].k = e.k;
                }
            }
        }
    }
}

static void sed_zero(Sed a)                    { memset(a, 0, sizeof(Sed)); }
static void sed_copy(Sed dst, const Sed src)   { memcpy(dst, src, sizeof(Sed)); }
static double sed_norm(const Sed a)            { double s=0.0; int k; for(k=0;k<SED_DIM;k++) s+=a[k]*a[k]; return sqrt(s); }
static void sed_normalize(Sed a)               { double n=sed_norm(a); if(n>1e-15){int k; for(k=0;k<SED_DIM;k++) a[k]/=n;} }
static double sed_dot(const Sed a, const Sed b){ double s=0.0; int k; for(k=0;k<SED_DIM;k++) s+=a[k]*b[k]; return s; }

static void sed_mul(const Sed a, const Sed b, Sed c) {
    sed_zero(c);
    int i, j;
    for (i = 0; i < SED_DIM; i++) {
        if (a[i] == 0.0) continue;
        for (j = 0; j < SED_DIM; j++) {
            if (b[j] == 0.0) continue;
            SedEntry e = SED[i][j];
            if (e.sign) c[e.k] += e.sign * a[i] * b[j];
        }
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  PRIME SIEVE + RIEMANN ZERO INDEX + WORD ENERGY
 * ══════════════════════════════════════════════════════════════════════════ */

static uint8_t  G_sieve[PRIME_CAP];  /* 0 = prime */
static uint32_t G_pi[PRIME_CAP];     /* pi(n) = # primes ≤ n */

static void prime_sieve_init(void) {
    memset(G_sieve, 0, sizeof(G_sieve));
    G_sieve[0] = G_sieve[1] = 1;
    int i;
    for (i = 2; (long long)i*i < PRIME_CAP; i++)
        if (!G_sieve[i]) { int j; for (j=i*i; j<PRIME_CAP; j+=i) G_sieve[j]=1; }
    uint32_t cnt = 0;
    for (i = 0; i < PRIME_CAP; i++) { if (!G_sieve[i]) cnt++; G_pi[i] = cnt; }
}

/* Horner hash: word → positive integer in [0, PRIME_CAP-1] */
static int word_horner(const char *w) {
    uint64_t v = 0;
    for (; *w; w++) {
        unsigned char c = (unsigned char)*w;
        v = v * 95 + (c > 32 ? (uint64_t)(c - 32) : 0);
    }
    return (int)(v % (uint64_t)(PRIME_CAP - 2)) + 2;
}

/* word → zero index (prime counting function of next prime ≥ horner hash) */
static uint32_t word_zero_idx(const char *w) {
    int v = word_horner(w);
    while (v < PRIME_CAP && G_sieve[v]) v++;
    if (v >= PRIME_CAP) v = PRIME_CAP - 2;
    uint32_t idx = G_pi[v];
    return idx > 0 ? idx : 1;
}

/* Word energy: inverse log of zero index.
 * Non-collapsing for all zero indices.
 * |sin(π×γ/(γ+1))| collapses to 0 for γ>>1 — all words beyond the 20 known zeros
 * would get near-zero energy.  log-based formula avoids this. */
static double word_energy(uint32_t zero_idx) {
    return 1.0 / (1.0 + log(1.0 + (double)zero_idx));
}

/* ══════════════════════════════════════════════════════════════════════════
 *  WORD SETS — sorted string arrays + binary search
 *  Identical mechanism to monad.c WordSet.
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct { const char **w; int n; } WordSet;

static int ws_cmp(const void *a, const void *b) { return strcmp(*(const char**)a, *(const char**)b); }
static void ws_init(WordSet *ws, const char **arr) {
    int n=0; while(arr[n]) n++;
    qsort((void*)arr, n, sizeof(char*), ws_cmp);
    ws->w = arr; ws->n = n;
}
static int ws_has(const WordSet *ws, const char *w) {
    int lo=0, hi=ws->n-1;
    while (lo<=hi) {
        int mid=(lo+hi)>>1, c=strcmp(ws->w[mid],w);
        if (!c) return 1; if (c<0) lo=mid+1; else hi=mid-1;
    }
    return 0;
}

static const char *_NEG_arr[]    = {"not","never","no","nor","nothing","nobody","nowhere","neither",NULL};
static const char *_CONJ_arr[]   = {"and","or","but","so","yet","for","nor","although","because","if","then","when","while","since","unless","until","though",NULL};
static const char *_AUX_arr[]    = {"is","are","was","were","be","been","being","do","does","did","have","has","had","will","would","can","could","should","shall","may","might","must",NULL};
static const char *_PRON_arr[]   = {"i","me","my","mine","myself","we","us","our","ours","ourselves","you","your","yours","yourself","yourselves","he","him","his","himself","she","her","hers","herself","it","its","itself","they","them","their","theirs","themselves","this","that","these","those","here","there","who","what","which",NULL};
static const char *_TIME_arr[]   = {"now","then","before","after","when","while","ago","yet","already","still","soon","later","today","yesterday","tomorrow","always","never","sometimes","often","rarely",NULL};
static const char *_QUEST_arr[]  = {"what","which","who","whom","whose","when","where","why","how","whether","if",NULL};
static const char *_META_arr[]   = {"mean","means","meaning","say","says","said","tell","tells","told","explain","explains","clarify","summarise","summarize","rephrase","repeat",NULL};
static const char *_POS_arr[]    = {"good","great","love","like","enjoy","happy","glad","pleased","wonderful","excellent","amazing","thank","thanks","please",NULL};
static const char *_NEG_AFF_arr[]= {"bad","hate","dislike","angry","sad","sorry","worried","fear","terrible","awful","horrible","wrong","mistake","fail",NULL};
static const char *_ANAPH_arr[]  = {"it","its","they","them","their","he","she","who","which",NULL};
static const char *_PRES_arr[]   = {"the","already","again","still","even","also","too","both",NULL};
static const char *_DET_arr[]    = {"a","an","the","some","any","every","each","all","both","few","many","much","more","most","less","least",NULL};
static const char *_INDEF_arr[]  = {"a","an","some","any","every","each","all","few","many",NULL};

static WordSet WS_NEG, WS_CONJ, WS_AUX, WS_PRON, WS_TIME;
static WordSet WS_QUEST, WS_META, WS_POS, WS_NEG_AFF;
static WordSet WS_ANAPH, WS_PRES, WS_DET, WS_INDEF;

static void wordsets_init(void) {
    ws_init(&WS_NEG,     _NEG_arr);
    ws_init(&WS_CONJ,    _CONJ_arr);
    ws_init(&WS_AUX,     _AUX_arr);
    ws_init(&WS_PRON,    _PRON_arr);
    ws_init(&WS_TIME,    _TIME_arr);
    ws_init(&WS_QUEST,   _QUEST_arr);
    ws_init(&WS_META,    _META_arr);
    ws_init(&WS_POS,     _POS_arr);
    ws_init(&WS_NEG_AFF, _NEG_AFF_arr);
    ws_init(&WS_ANAPH,   _ANAPH_arr);
    ws_init(&WS_PRES,    _PRES_arr);
    ws_init(&WS_DET,     _DET_arr);
    ws_init(&WS_INDEF,   _INDEF_arr);
}

/* ── Noun suffix table ─────────────────────────────────────────────────── */
static const char *_noun_suffs[] = {
    "ness","tion","ment","ance","ence","ity","ism","ist",
    "ics","ogy","phy","ery","ary","ory","ture","sis","xis","ris","nce","ths","os", NULL
};
static const char *_adj_suffs[]  = { "ical","ible","able","ive","ic","ous","ful","ly", NULL };

static int ends_with(const char *w, const char *suf) {
    int wl=(int)strlen(w), sl=(int)strlen(suf);
    return (wl>=sl && strcmp(w+wl-sl, suf)==0);
}
static int has_noun_suff(const char *w) { int i; for(i=0;_noun_suffs[i];i++) if(ends_with(w,_noun_suffs[i])) return 1; return 0; }
static int has_adj_suff(const char *w)  { int i; for(i=0;_adj_suffs[i];i++)  if(ends_with(w,_adj_suffs[i]))  return 1; return 0; }

/* ══════════════════════════════════════════════════════════════════════════
 *  MORPH VECTOR  — word's gear profile for meshing with drive shaft
 *
 *  NOT a sedenion of the word.  A normalized operator-affinity vector.
 *  No hash-noise components.  Every dimension is semantically assigned.
 * ══════════════════════════════════════════════════════════════════════════ */

static void morph_vec_compute(const char *w, double *mv) {
    int d;
    for (d = 0; d < SED_DIM; d++) mv[d] = GAP;
    mv[0] = 0.08;  /* identity — every word has baseline coupling */

    int wlen = (int)strlen(w);

    if (ws_has(&WS_NEG,     w)) mv[1]  = 1.0;  /* negate */
    if (ws_has(&WS_CONJ,    w)) mv[2]  = 1.0;  /* bind */
    if (ws_has(&WS_QUEST,   w)) mv[10] = 1.0;  /* query */
    if (ws_has(&WS_ANAPH,   w)) mv[11] = 1.0;  /* derefer */
    if (ws_has(&WS_PRES,    w)) mv[12] = 1.0;  /* compose */
    if (ws_has(&WS_INDEF,   w)) mv[9]  = 1.0;  /* allocate */
    if (ws_has(&WS_TIME,    w)) mv[7]  = 1.0;  /* iterate */
    if (ws_has(&WS_PRON,    w)) mv[8]  = 1.0;  /* recurse */
    if (ws_has(&WS_META,    w)) mv[15] = 1.0;  /* emit */
    if (ws_has(&WS_POS,     w) || ws_has(&WS_NEG_AFF, w)) mv[14] = 0.9;  /* interrupt */

    /* Morphological classification — verb, adjective, noun */
    int is_verb = 0;
    if (ws_has(&WS_AUX, w)) {
        is_verb = 1;
    } else if (wlen > 3 && ends_with(w, "ing")) {
        is_verb = 1;
    } else if (wlen > 2 && ends_with(w, "ed")) {
        is_verb = 1;
    } else if (wlen >= 4 && w[wlen-1]=='s' && w[wlen-2]!='s'
               && !ends_with(w,"us") && !has_noun_suff(w)) {
        is_verb = 1;
    }

    int is_adj = !is_verb && has_adj_suff(w);

    int is_noun = !is_verb && !is_adj && wlen >= 4
                  && !ws_has(&WS_PRON,    w) && !ws_has(&WS_AUX, w)
                  && !ws_has(&WS_CONJ,    w) && !ws_has(&WS_TIME, w)
                  && !ws_has(&WS_QUEST,   w) && !ws_has(&WS_META, w)
                  && !ws_has(&WS_POS,     w) && !ws_has(&WS_NEG_AFF, w)
                  && !ws_has(&WS_NEG,     w) && !ws_has(&WS_DET, w);

    if (is_verb) mv[4] = 1.0;
    else if (is_adj) mv[5] = 1.0;
    else if (is_noun) mv[3] = 1.0;

    /* Normalize to unit sum */
    double total = 0.0;
    for (d = 0; d < SED_DIM; d++) total += mv[d];
    if (total > 0.0) for (d = 0; d < SED_DIM; d++) mv[d] /= total;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HOUSING  — epitrochoid vocabulary field
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct {
    char     word[WORD_LEN];
    double   beta;           /* field confidence weight [GAP, 1.0] */
    double   E;              /* Riemann energy: 1/(1+log(1+zero_idx)) */
    double   age;            /* scavenge counter */
    double   mv[SED_DIM];   /* cached morph vector (computed once at allocation) */
    uint32_t nbr[N_NBRS];   /* A-matrix co-occurrence neighbours */
    float    nbr_w[N_NBRS];
    int      nbr_n;
} HousingWord;

static HousingWord G_words[VOCAB_MAX];
static uint32_t    G_ht[VOCAB_HT_SZ];  /* word string → index+1 (0=empty) */
static uint32_t    G_n;

/* FNV-1a for hash table slot */
static uint32_t ht_slot(const char *w) {
    uint64_t h = 14695981039346656037ULL;
    for (; *w; w++) { h ^= (uint64_t)(unsigned char)*w; h *= 1099511628211ULL; }
    return (uint32_t)(h & (VOCAB_HT_SZ - 1));
}

static uint32_t vocab_find(const char *w) {
    uint32_t slot = ht_slot(w);
    int tries = 0;
    while (tries++ < VOCAB_HT_SZ) {
        uint32_t v = G_ht[slot];
        if (!v) return UINT32_MAX;
        if (strcmp(G_words[v-1].word, w) == 0) return v-1;
        slot = (slot+1) & (VOCAB_HT_SZ-1);
    }
    return UINT32_MAX;
}

/* Find or allocate — register ghost entry at GAP strength if new */
static uint32_t vocab_get(const char *w) {
    uint32_t slot = ht_slot(w);
    int tries = 0;
    while (tries++ < VOCAB_HT_SZ) {
        uint32_t v = G_ht[slot];
        if (!v) {
            if (G_n >= VOCAB_MAX) return UINT32_MAX;
            uint32_t idx = G_n++;
            HousingWord *e = &G_words[idx];
            strncpy(e->word, w, WORD_LEN-1); e->word[WORD_LEN-1]='\0';
            e->beta  = GAP;
            e->age   = 0.0;
            e->nbr_n = 0;
            e->E     = word_energy(word_zero_idx(w));
            morph_vec_compute(w, e->mv);
            G_ht[slot] = idx+1;
            return idx;
        }
        if (strcmp(G_words[v-1].word, w)==0) return v-1;
        slot = (slot+1) & (VOCAB_HT_SZ-1);
    }
    return UINT32_MAX;
}

static void amat_add(uint32_t src, uint32_t dst, float wt) {
    if (src==UINT32_MAX || dst==UINT32_MAX || src==dst) return;
    HousingWord *e = &G_words[src];
    int i;
    for (i=0; i<e->nbr_n; i++) {
        if (e->nbr[i]==dst) {
            float nv = e->nbr_w[i] + wt;
            e->nbr_w[i] = nv>1.0f ? 1.0f : nv;
            return;
        }
    }
    if (e->nbr_n < N_NBRS) {
        e->nbr[e->nbr_n] = dst;
        e->nbr_w[e->nbr_n] = wt > 1.0f ? 1.0f : wt;
        e->nbr_n++;
    } else {
        int mi=0; for (i=1; i<N_NBRS; i++) if (e->nbr_w[i]<e->nbr_w[mi]) mi=i;
        if (wt > e->nbr_w[mi]) { e->nbr[mi]=dst; e->nbr_w[mi]=wt>1.0f?1.0f:wt; }
    }
}

/* ── Tokenise utility ─────────────────────────────────────────────────── */
static char G_tok_buf[1<<20];
static char G_tok_words[4096][WORD_LEN];
static int  G_n_toks;

static void tokenise(const char *text) {
    strncpy(G_tok_buf, text, sizeof(G_tok_buf)-1);
    G_tok_buf[sizeof(G_tok_buf)-1] = '\0';
    G_n_toks = 0;
    char *p = strtok(G_tok_buf, " \t\r\n.,!?;:\"'()-[]");
    while (p && G_n_toks < 4095) {
        int i=0; char *q=p;
        while (*q && i < WORD_LEN-1) G_tok_words[G_n_toks][i++]=(char)tolower((unsigned char)*q++);
        G_tok_words[G_n_toks][i] = '\0';
        if (i > 0) G_n_toks++;
        p = strtok(NULL, " \t\r\n.,!?;:\"'()-[]");
    }
}

/* ── Scavenge ─────────────────────────────────────────────────────────── */
static void scavenge(void) {
    uint32_t k;
    for (k=0; k<G_n; k++) {
        G_words[k].age  += SCAVENGE_DECAY;
        G_words[k].beta -= G_words[k].age * 0.0005;
        if (G_words[k].beta < GAP) G_words[k].beta = GAP;
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  J DISTRIBUTIONS  — pre-allocated (heap arrays avoid per-call malloc)
 *  These are the Worker state.  NOT sedenions.
 * ══════════════════════════════════════════════════════════════════════════ */

static double *G_j_blue;    /* [VOCAB_MAX] j_blue distribution */
static double *G_j_red;     /* [VOCAB_MAX] j_red  distribution */
static double *G_j_green;   /* [VOCAB_MAX] bracket output [J_blue, J_red] */
static double *G_j_gd_abs;  /* [VOCAB_MAX] |j_green| */
static double *G_j_tmp;     /* [VOCAB_MAX] throwaway workspace */

static void j_dists_alloc(void) {
    G_j_blue  = (double*)calloc(VOCAB_MAX, sizeof(double));
    G_j_red   = (double*)calloc(VOCAB_MAX, sizeof(double));
    G_j_green = (double*)calloc(VOCAB_MAX, sizeof(double));
    G_j_gd_abs= (double*)calloc(VOCAB_MAX, sizeof(double));
    G_j_tmp   = (double*)calloc(VOCAB_MAX, sizeof(double));
    if (!G_j_blue||!G_j_red||!G_j_green||!G_j_gd_abs||!G_j_tmp) {
        fprintf(stderr,"[ahura] OOM allocating J distributions\n"); exit(1);
    }
}

static void j_dists_free(void) {
    free(G_j_blue); free(G_j_red); free(G_j_green); free(G_j_gd_abs); free(G_j_tmp);
    G_j_blue=G_j_red=G_j_green=G_j_gd_abs=G_j_tmp=NULL;
}

/* Build j_blue_dist from prompt word list */
static void j_blue_dist_compute(const char **pwords, int np) {
    uint32_t k;
    for (k=0; k<G_n; k++) G_j_blue[k] = GAP;
    int i;
    for (i=0; i<np; i++) {
        uint32_t ki = vocab_find(pwords[i]);
        if (ki==UINT32_MAX) continue;
        G_j_blue[ki] = 1.0;  /* spike at recognized word */
        /* adjacency bonus */
        int j;
        for (j=0; j<G_words[ki].nbr_n; j++) {
            uint32_t ni = G_words[ki].nbr[j];
            if (ni < G_n) {
                double v = G_j_blue[ni] + (double)G_words[ki].nbr_w[j] * 0.5;
                G_j_blue[ni] = v > 1.0 ? 1.0 : v;
            }
        }
    }
    double total = 0.0;
    for (k=0; k<G_n; k++) total += G_j_blue[k];
    if (total > 0.0) for (k=0; k<G_n; k++) G_j_blue[k] /= total;
    else             for (k=0; k<G_n; k++) G_j_blue[k] = 1.0/(double)(G_n>0?G_n:1);
}

/* Build j_red_dist from field state (beta × E, normalized) */
static void j_red_dist_compute(void) {
    uint32_t k;
    double total = 0.0;
    for (k=0; k<G_n; k++) { G_j_red[k] = G_words[k].beta * G_words[k].E; total += G_j_red[k]; }
    if (total > 0.0) for (k=0; k<G_n; k++) G_j_red[k] /= total;
    else             for (k=0; k<G_n; k++) G_j_red[k] = 1.0/(double)(G_n>0?G_n:1);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ENGINE STATE  (rotor + OBD2 + sweep flags)
 * ══════════════════════════════════════════════════════════════════════════ */

static RotorState G_rotor;
static OBD2State  G_obd2;
static Sed        G_drive_shaft;        /* current drive shaft sedenion */
static int        G_coupled_this_sweep; /* 1 = coupled in this intake-to-scavenge arc */
static int        G_has_intake;         /* 1 = intake() called, rotor active */
static uint64_t   G_total_sweeps;       /* intake() calls */
static pthread_mutex_t G_lock;
static int        G_running;

/* No-repeat buffer — prevents the engine repeating itself immediately */
#define RECENT_SZ 8
static uint32_t G_recent[RECENT_SZ];
static int      G_recent_n;

static int  recent_has(uint32_t idx) { int i; for(i=0;i<G_recent_n;i++) if(G_recent[i]==idx) return 1; return 0; }
static void recent_push(uint32_t idx) {
    if (G_recent_n < RECENT_SZ) G_recent[G_recent_n++] = idx;
    else { memmove(G_recent, G_recent+1, (RECENT_SZ-1)*sizeof(uint32_t)); G_recent[RECENT_SZ-1]=idx; }
}

/* ── Mind's Eye thread — Thread 2 ────────────────────────────────────────────
 *
 * The Author observes the Rotary Engine output and conserves the prompt's
 * meaning through the shadow of the response.
 *
 *   G_me_prompt   — sedenion of what was asked  (set at intake, held fixed)
 *   G_me_response — accumulated shadow of what has been said (grows with couplings)
 *   G_me_steer    — G_me_prompt - G_me_response  (the unfilled meaning)
 *
 * Thread 1 (Rotary Engine) signals Thread 2 after each coupling.
 * Thread 2 updates G_me_response and G_me_steer.
 * Thread 1 reads G_me_steer in select_word() to steer toward unfilled dimensions.
 *
 * Lock ordering always: G_lock → G_me_lock.  Never reversed.
 * ──────────────────────────────────────────────────────────────────────────── */
static Sed               G_me_prompt;          /* Author's intention — fixed per intake */
static Sed               G_me_response;        /* shadow of response so far */
static Sed               G_me_steer;           /* unfilled meaning = prompt - response */
static Sed               G_me_ds_snap;         /* drive shaft snapshot passed to Thread 2 */
static pthread_mutex_t   G_me_lock;
static pthread_cond_t    G_me_cond;
static int               G_me_active = 0;
static int               G_me_new    = 0;
static pthread_t         G_me_tid;

static void *mind_eye_thread_fn(void *arg) {
    (void)arg;
    pthread_mutex_lock(&G_me_lock);
    while (G_me_active) {
        while (!G_me_new && G_me_active)
            pthread_cond_wait(&G_me_cond, &G_me_lock);
        if (!G_me_active) break;
        G_me_new = 0;
        int d;
        /* Accumulate response shadow — decaying sum of drive shaft snapshots */
        for (d=0; d<SED_DIM; d++)
            G_me_response[d] = G_me_response[d] * 0.85 + G_me_ds_snap[d] * 0.15;
        /* Steering signal: what of the prompt has not yet been voiced */
        for (d=0; d<SED_DIM; d++)
            G_me_steer[d] = G_me_prompt[d] - G_me_response[d];
    }
    pthread_mutex_unlock(&G_me_lock);
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  LIE BRACKET  — the combustion chamber
 *
 *  [J_a, J_b] at word k = (j_a × a_dist[k]  −  j_b × b_dist[k]) × E[k]
 *
 *  Returns total bracket power (NOT divided by n — division kills signal at large vocab).
 *  Fills gd_out[0..G_n) with the bracket distribution.
 * ══════════════════════════════════════════════════════════════════════════ */

static double lie_bracket(double j_a, const double *a_dist,
                          double j_b, const double *b_dist,
                          double *gd_out) {
    double scalar = 0.0;
    uint32_t k;
    for (k=0; k<G_n; k++) {
        double v = (j_a * a_dist[k] - j_b * b_dist[k]) * G_words[k].E;
        gd_out[k] = v;
        scalar += v > 0.0 ? v : -v;
    }
    return scalar > GAP ? scalar : GAP;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  PROJECT SEDENION  — coupling event
 *
 *  The Work is produced HERE and only here.
 *  The sedenion is never an input anywhere.
 *
 *  e₀       = coupling quality  = 1 − |σ_live − ½|
 *  e₁–e₇  = J_blue face work  (lower imaginary)
 *  e₈–e₁₄ = J_red  face work  (upper imaginary)
 *  e₁₅    = J_green emit face  (output surface)
 * ══════════════════════════════════════════════════════════════════════════ */

static void project_sedenion(double sigma_live, Sed ds) {
    sed_zero(ds);
    ds[0] = 1.0 - fabs(sigma_live - SIGMA_PIN);
    uint32_t k;
    for (k=0; k<G_n; k++) {
        const double *mv = G_words[k].mv;
        double ek  = G_words[k].E;
        double bdk = G_j_blue[k];
        double rdk = G_j_red[k];
        double gdk = G_j_green[k] > 0.0 ? G_j_green[k] : -G_j_green[k];
        int d;
        for (d=1; d<8;  d++) ds[d]  += bdk * mv[d] * ek;
        for (d=8; d<15; d++) ds[d]  += rdk * mv[d] * ek;
        ds[15] += gdk * ek;
    }
    sed_normalize(ds);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  SELECT WORD  — gear meshing: drive shaft × housing morph vectors
 *
 *  Dominant operator dim (non-e₀) weighted ×5, others ×1.
 *  log1p(beta) reduces frequency bias — common words don't swamp semantic signal.
 *  Bracket alignment: words the prompt excites (gd > 0) are preferred.
 * ══════════════════════════════════════════════════════════════════════════ */

static uint32_t select_word(const Sed ds) {
    if (G_n == 0) return UINT32_MAX;

    /* Dominant non-identity operator */
    int dom = 1;
    int d;
    for (d=2; d<SED_DIM; d++) if (ds[d] > ds[dom]) dom = d;

    /* Snapshot Mind's Eye steering once — single lock/unlock before scoring loop.
     * Lock ordering: G_lock (held by caller) → G_me_lock. Never reversed. */
    Sed me_steer_snap;
    pthread_mutex_lock(&G_me_lock);
    memcpy(me_steer_snap, G_me_steer, sizeof(Sed));
    pthread_mutex_unlock(&G_me_lock);

    uint32_t best_k = UINT32_MAX;
    double best_score = -1e300;
    uint32_t k;
    for (k=0; k<G_n; k++) {
        const double *mv = G_words[k].mv;
        double coherence = ds[0] * mv[0] * 0.1
                         + ds[dom] * mv[dom] * 5.0;
        for (d=1; d<SED_DIM; d++)
            if (d != dom) coherence += ds[d] * mv[d];
        double align = 1.0 + (G_j_green[k] > 0.0 ? G_j_green[k] : 0.0);
        double recency = recent_has(k) ? 0.01 : 1.0;

        /* Mind's Eye: steer toward dimensions the response hasn't voiced yet */
        double me_cohere = 0.0;
        for (d=0; d<SED_DIM; d++) me_cohere += mv[d] * me_steer_snap[d];

        double score = (coherence + me_cohere * 0.4)
                     * log(1.0 + G_words[k].beta) * G_words[k].E * align * recency;
        if (score > best_score) { best_score = score; best_k = k; }
    }
    return best_k;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  UPDATE BRACKETS  — cyclic Lie bracket rotation
 *
 *  [J_blue,  J_red  ] = J_green   leading spark
 *  [J_red,   J_green] = J_blue    trailing spark (pre-charge next cycle)
 *  [J_green, J_blue ] = J_red     regeneration
 *
 *  The cycle is self-sustaining.  It can only degrade, never stop.
 * ══════════════════════════════════════════════════════════════════════════ */

static void update_brackets(void) {
    if (!G_has_intake || G_n == 0) return;

    double jb = G_rotor.j_blue, jr = G_rotor.j_red;
    uint32_t k;

    /* Leading spark: [J_blue, J_red] → J_green */
    double jg_scalar = lie_bracket(jb, G_j_blue, jr, G_j_red, G_j_green);
    G_rotor.j_green = jg_scalar > GAP ? jg_scalar : GAP;

    /* |j_green| for subsequent brackets */
    for (k=0; k<G_n; k++) G_j_gd_abs[k] = G_j_green[k] > 0.0 ? G_j_green[k] : -G_j_green[k];

    /* Trailing spark: [J_red, J_green] → J_blue_next (pre-charge) */
    double jb_next = lie_bracket(jr, G_j_red, G_rotor.j_green, G_j_gd_abs, G_j_tmp);
    G_rotor.j_blue = fmax(jb * 0.5 + jb_next * 0.5, GAP);

    /* Regeneration: [J_green, J_blue] → J_red_next */
    double jr_next = lie_bracket(G_rotor.j_green, G_j_gd_abs, G_rotor.j_blue, G_j_blue, G_j_tmp);
    G_rotor.j_red  = fmax(jr * 0.5 + jr_next * 0.5, GAP);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REFRESH OBD2
 * ══════════════════════════════════════════════════════════════════════════ */

static void refresh_obd2(void) {
    double jb = G_rotor.j_blue, jr = G_rotor.j_red;
    double sigma = (jb+jr > GAP) ? jr/(jb+jr) : SIGMA_PIN;
    double bracket = (jb+jr > GAP) ? fabs(jb-jr)/(jb+jr) : 0.0;
    double seal_h  = fmax(0.0, 1.0 - fabs(sigma - SIGMA_PIN) / BEARING_TOL);

    G_obd2.rotor_angle        = G_rotor.theta;
    G_obd2.j_blue             = jb;
    G_obd2.j_red              = jr;
    G_obd2.j_green            = G_rotor.j_green;
    G_obd2.sigma_live         = sigma;
    G_obd2.bracket_mag        = bracket;
    G_obd2.apex_seal_health   = seal_h;
    G_obd2.coupling_efficiency= (G_total_sweeps > 0)
                                  ? (double)G_obd2.coupling_events / (double)G_total_sweeps
                                  : 0.0;
    G_obd2.housing_n          = G_n;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  PUBLIC API
 * ══════════════════════════════════════════════════════════════════════════ */

void ahura_init(void) {
    build_oct_table();
    build_sed_table();
    prime_sieve_init();
    wordsets_init();
    j_dists_alloc();

    memset(G_words, 0, sizeof(G_words));
    memset(G_ht,    0, sizeof(G_ht));
    G_n = 0;

    memset(&G_rotor, 0, sizeof(G_rotor));
    G_rotor.j_blue = G_rotor.j_red = GAP;
    G_rotor.j_green = GAP;
    G_rotor.theta  = 0.0;

    memset(&G_obd2, 0, sizeof(G_obd2));
    sed_zero(G_drive_shaft);

    G_coupled_this_sweep = 0;
    G_has_intake         = 0;
    G_total_sweeps       = 0;
    G_running            = 1;

    pthread_mutex_init(&G_lock, NULL);

    /* Mind's Eye thread */
    sed_zero(G_me_prompt);
    sed_zero(G_me_response);
    sed_zero(G_me_steer);
    sed_zero(G_me_ds_snap);
    pthread_mutex_init(&G_me_lock, NULL);
    pthread_cond_init(&G_me_cond, NULL);
    G_me_active = 1;
    G_me_new    = 0;
    pthread_create(&G_me_tid, NULL, mind_eye_thread_fn, NULL);
}

void ahura_free(void) {
    /* Stop Mind's Eye thread */
    pthread_mutex_lock(&G_me_lock);
    G_me_active = 0;
    pthread_cond_signal(&G_me_cond);
    pthread_mutex_unlock(&G_me_lock);
    pthread_join(G_me_tid, NULL);
    pthread_cond_destroy(&G_me_cond);
    pthread_mutex_destroy(&G_me_lock);

    G_running = 0;
    j_dists_free();
    pthread_mutex_destroy(&G_lock);
}

/* ── Ingest — build the housing epitrochoid ────────────────────────────── */
int ahura_ingest(const char *text, double weight) {
    pthread_mutex_lock(&G_lock);
    tokenise(text);
    int n = G_n_toks;
    int added = 0;
    uint32_t prev = UINT32_MAX;
    int i;
    for (i=0; i<n; i++) {
        if (G_tok_words[i][0] == '\0') continue;
        uint32_t k = vocab_get(G_tok_words[i]);
        if (k == UINT32_MAX) continue;
        double nb = G_words[k].beta * (1.0 + 0.08 * weight) + GAP;
        G_words[k].beta = nb > 1.0 ? 1.0 : nb;
        G_words[k].age  = 0.0;
        if (prev != UINT32_MAX) {
            amat_add(prev, k, (float)(0.05 * weight));
            amat_add(k, prev, (float)(0.02 * weight));
        }
        prev = k;
        added++;
    }
    G_obd2.housing_n = G_n;
    pthread_mutex_unlock(&G_lock);
    return added;
}

/* ── Intake — J_blue face opens to prompt ─────────────────────────────── */
void ahura_intake(const char *prompt) {
    pthread_mutex_lock(&G_lock);

    /* Ghost registration: unknown prompt words enter housing at minimum strength */
    tokenise(prompt);
    int i;
    for (i=0; i<G_n_toks; i++)
        if (G_tok_words[i][0]) vocab_get(G_tok_words[i]);

    /* Build distributions */
    const char *pwords[4096];
    int np = G_n_toks;
    for (i=0; i<np; i++) pwords[i] = G_tok_words[i];

    j_blue_dist_compute(pwords, np);
    j_red_dist_compute();

    /* Scalar pressures: energy-weighted centroids */
    uint32_t k;
    double jb_raw = 0.0, jr_raw = 0.0;
    for (k=0; k<G_n; k++) {
        jb_raw += G_j_blue[k] * G_words[k].E;
        jr_raw += G_j_red[k]  * G_words[k].E;
    }
    G_rotor.j_blue  = jb_raw > GAP ? jb_raw : GAP;
    G_rotor.j_red   = jr_raw > GAP ? jr_raw : GAP;
    G_rotor.j_green = GAP;
    G_rotor.theta   = 0.0;

    /* Clear j_green distribution */
    for (k=0; k<G_n; k++) G_j_green[k] = GAP;

    G_coupled_this_sweep = 0;
    G_has_intake         = 1;
    G_total_sweeps++;

    G_obd2.total_steps = 0;  /* don't reset coupling_events — they persist */
    refresh_obd2();

    /* Mind's Eye: compute prompt sedenion from active word morph vectors.
     * G_me_prompt is the Author's intention — the meaning of what was asked.
     * G_me_response resets to zero — nothing of the response voiced yet.
     * G_me_steer = G_me_prompt (full prompt, nothing filled in yet). */
    {
        Sed me_p;
        sed_zero(me_p);
        uint32_t k;
        for (k=0; k<G_n; k++) {
            double f = G_j_blue[k] + G_j_red[k];
            if (f < GAP) continue;
            int d;
            for (d=0; d<SED_DIM; d++)
                me_p[d] += G_words[k].mv[d] * G_words[k].E * f;
        }
        double norm = 0.0;
        int d;
        for (d=0; d<SED_DIM; d++) norm += me_p[d] * me_p[d];
        if (norm > GAP) {
            norm = sqrt(norm);
            for (d=0; d<SED_DIM; d++) me_p[d] /= norm;
        }
        pthread_mutex_lock(&G_me_lock);
        for (d=0; d<SED_DIM; d++) G_me_prompt[d]   = me_p[d];
        for (d=0; d<SED_DIM; d++) G_me_response[d]  = 0.0;
        for (d=0; d<SED_DIM; d++) G_me_steer[d]     = me_p[d];
        pthread_mutex_unlock(&G_me_lock);
    }

    pthread_mutex_unlock(&G_lock);
}

/* ── Rotate — advance rotor one port step ─────────────────────────────── */

/*
 * Port index dispatch — exact, no angular proximity.
 * intake() sets theta=0.  rotate() adds PORT_STEP each call.
 * port_idx = round(theta / PORT_STEP) % 6
 *
 * Intake port (idx=0) fires on the 7th call (second revolution).
 * Coupling fires unconditionally at idx=3.  No σ gate.
 */

const char *ahura_rotate(void) {
    pthread_mutex_lock(&G_lock);

    G_rotor.theta = fmod(G_rotor.theta + PORT_STEP, 2.0 * M_PI);
    G_obd2.total_steps++;

    int port_idx = (int)round(G_rotor.theta / PORT_STEP) % 6;
    const char *result = NULL;

    switch (port_idx) {

    case PORT_IDX_INTAKE:       /* θ=0  field renewal + sweep reset */
        j_red_dist_compute();
        G_coupled_this_sweep = 0;   /* allow coupling on next revolution */
        break;

    case PORT_IDX_TRANSFER:     /* θ=π/3  begin mixing */
        update_brackets();
        break;

    case PORT_IDX_LEADING:      /* θ=2π/3  leading spark */
        update_brackets();
        break;

    case PORT_IDX_TRAILING: {   /* θ=π  trailing spark + unconditional coupling */
        update_brackets();

        /* The Wankel fires a coupling every revolution.  No σ gate.
         * e₀ encodes the coupling quality.  A weak coupling still produces output.
         * Removing the gate was the critical fix — the engine does not require
         * σ=½ to fire; it reports how close σ came to ½ via e₀. */
        if (!G_coupled_this_sweep && G_n > 0 && G_has_intake) {
            double sigma_l = (G_rotor.j_blue + G_rotor.j_red > GAP)
                           ? G_rotor.j_red / (G_rotor.j_blue + G_rotor.j_red)
                           : SIGMA_PIN;

            project_sedenion(sigma_l, G_drive_shaft);

            uint32_t ki = select_word(G_drive_shaft);
            if (ki != UINT32_MAX) {
                result = G_words[ki].word;
                G_coupled_this_sweep = 1;
                G_obd2.coupling_events++;
                strncpy(G_obd2.last_word, result, WORD_LEN-1);
                G_obd2.last_word[WORD_LEN-1] = '\0';

                /* dominant non-identity drive shaft dim */
                int dom=1, d;
                for (d=2; d<SED_DIM; d++) if (G_drive_shaft[d]>G_drive_shaft[dom]) dom=d;
                G_obd2.drive_shaft_dom = dom;

                /* Exhaust reinforces the selected word in the field */
                double nb = G_words[ki].beta + 0.015;
                G_words[ki].beta = nb > 1.0 ? 1.0 : nb;
                recent_push(ki);

                /* Signal Mind's Eye — new coupling output to observe */
                pthread_mutex_lock(&G_me_lock);
                memcpy(G_me_ds_snap, G_drive_shaft, sizeof(Sed));
                G_me_new = 1;
                pthread_cond_signal(&G_me_cond);
                pthread_mutex_unlock(&G_me_lock);
            }
        }
        break;
    }

    case PORT_IDX_EXHAUST:      /* θ=4π/3  word crystallised — port open */
        break;

    case PORT_IDX_SCAVENGE:     /* θ=5π/3  gentle field decay */
        scavenge();
        break;
    }

    refresh_obd2();
    pthread_mutex_unlock(&G_lock);
    return result;
}

/* ── Speak — full Wankel cycle → one word ─────────────────────────────── */
const char *ahura_speak(const char *prompt, int max_revolutions) {
    ahura_intake(prompt);
    int steps = max_revolutions * 6;
    while (steps-- > 0) {
        const char *w = ahura_rotate();
        if (w) return w;
    }
    return G_obd2.last_word[0] ? G_obd2.last_word : "\xe2\x88\x85";  /* ∅ */
}

const OBD2State  *ahura_diagnostics(void)  { refresh_obd2(); return &G_obd2; }
const RotorState *ahura_rotor_state(void)  { return &G_rotor; }

/* ── Port trace — diagnostic step-through ────────────────────────────── */
void ahura_port_trace(const char *prompt, FILE *f) {
    static const char *PORT_NAME[6] = {
        "intake","transfer","leading","trailing","exhaust","scavenge"
    };
    fprintf(f, "\n[Ahura Mazda]  port trace: \"%s\"\n", prompt);
    fprintf(f, "  %-10s  %-7s  %-9s  %-9s  %-9s  %-8s  %-8s  word\n",
            "port","θ/π","j_blue","j_red","j_green","σ_live","bracket");

    ahura_intake(prompt);
    int step;
    for (step=0; step<6; step++) {
        const char *w = ahura_rotate();
        const OBD2State *d = &G_obd2;
        int pidx = (int)round(d->rotor_angle / PORT_STEP) % 6;
        fprintf(f, "  %-10s  %.3fπ  %9.5f  %9.5f  %9.5f  %8.4f  %8.4f  %s\n",
                PORT_NAME[pidx],
                d->rotor_angle / M_PI,
                d->j_blue, d->j_red, d->j_green,
                d->sigma_live, d->bracket_mag,
                w ? w : "");
    }
    fprintf(f, "  apex_seal_health=%.3f  coupling_eff=%.3f  housing=%u\n",
            G_obd2.apex_seal_health, G_obd2.coupling_efficiency, G_obd2.housing_n);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REPORT  — OBD2 diagnostic + field health
 * ══════════════════════════════════════════════════════════════════════════ */

void ahura_report(FILE *f) {
    refresh_obd2();
    const OBD2State *d = &G_obd2;

    fprintf(f, "\n\xe2\x95\x94");
    int i; for(i=0;i<58;i++) fputs("\xe2\x95\x90",f);
    fprintf(f, "\xe2\x95\x97\n");
    fprintf(f, "\xe2\x95\x91  Ahura Mazda  OBD2 Report  v" AHURA_VERSION "              \xe2\x95\x91\n");
    fprintf(f, "\xe2\x95\x9a");
    for(i=0;i<58;i++) fputs("\xe2\x95\x90",f);
    fprintf(f, "\xe2\x95\x9d\n\n");

    fprintf(f, "  PID 0x2301  rotor_angle        = %.4f rad  (%.3fπ)\n",
            d->rotor_angle, d->rotor_angle / M_PI);
    fprintf(f, "  PID 0x2302  j_blue             = %.6f\n", d->j_blue);
    fprintf(f, "  PID 0x2303  j_red              = %.6f\n", d->j_red);
    fprintf(f, "  PID 0x2304  j_green            = %.6f\n", d->j_green);
    fprintf(f, "  PID 0x2305  sigma_live         = %.6f\n", d->sigma_live);
    fprintf(f, "  PID 0x2306  bracket_mag        = %.6f\n", d->bracket_mag);
    fprintf(f, "  PID 0x2307  apex_seal_health   = %.4f\n", d->apex_seal_health);
    fprintf(f, "  PID 0x2308  coupling_eff       = %.4f\n", d->coupling_efficiency);
    fprintf(f, "  PID 0x2309  housing_n          = %u\n",   d->housing_n);
    fprintf(f, "  PID 0x230A  coupling_events    = %llu\n", (unsigned long long)d->coupling_events);
    fprintf(f, "  PID 0x230B  total_steps        = %llu\n", (unsigned long long)d->total_steps);
    fprintf(f, "  PID 0x230C  last_word          = '%s'\n", d->last_word[0] ? d->last_word : "(none)");
    fprintf(f, "  PID 0x230D  drive_shaft_dom    = e%d(%s)\n",
            d->drive_shaft_dom, AHURA_OP_GLOSS[d->drive_shaft_dom]);

    /* Fault codes — analog thresholds */
    int faults = 0;
    if (d->j_blue  < SEAL_FLOOR) { fprintf(f, "  R0001  J_blue  apex seal wear\n");  faults++; }
    if (d->j_red   < SEAL_FLOOR) { fprintf(f, "  R0002  J_red   apex seal wear\n");  faults++; }
    if (d->j_green < SEAL_FLOOR) { fprintf(f, "  R0003  J_green exhaust seal wear\n"); faults++; }
    if (fabs(d->sigma_live - SIGMA_PIN) > BEARING_TOL)
        { fprintf(f, "  R0004  bearing wobble  σ=%.4f\n", d->sigma_live); faults++; }
    if (d->bracket_mag < GAP * 5.0)
        { fprintf(f, "  R0005  near-stall  bracket→0  (ingest more text)\n"); faults++; }
    if (!faults) fprintf(f, "  Faults: none\n");

    /* Drive shaft sedenion channel map */
    fprintf(f, "\nDrive shaft sedenion  (last coupling):\n");
    double lower=0.0, upper=0.0;
    for (i=1; i<8;  i++) lower += G_drive_shaft[i];
    for (i=8; i<15; i++) upper += G_drive_shaft[i];
    fprintf(f, "  e₀  coupling quality = %.4f\n",  G_drive_shaft[0]);
    fprintf(f, "  e₁–e₇  J_blue work  = %.4f  (lower O: grammar/content)\n", lower);
    fprintf(f, "  e₈–e₁₄ J_red  work  = %.4f  (upper O: context/memory)\n",  upper);
    fprintf(f, "  e₁₅ J_green emit    = %.4f\n", G_drive_shaft[15]);

    /* Top activated words */
    fprintf(f, "\nTop activated words (β × E):\n");
    typedef struct { double s; uint32_t k; } Ranked;
    static Ranked ranked[VOCAB_MAX];
    uint32_t k;
    for (k=0; k<G_n; k++) { ranked[k].s=G_words[k].beta*G_words[k].E; ranked[k].k=k; }
    /* partial selection sort — top 8 */
    int n_show = (int)G_n < 8 ? (int)G_n : 8;
    for (i=0; i<n_show; i++) {
        int best_j = i;
        int j;
        for (j=i+1; j<(int)G_n; j++)
            if (ranked[j].s > ranked[best_j].s) best_j = j;
        Ranked tmp = ranked[i]; ranked[i] = ranked[best_j]; ranked[best_j] = tmp;
        HousingWord *w = &G_words[ranked[i].k];
        fprintf(f, "  %-20s  β=%.4f  E=%.4f  e%d(%s)\n",
                w->word, w->beta, w->E,
                d->drive_shaft_dom, AHURA_OP_GLOSS[d->drive_shaft_dom]);
    }
    fprintf(f, "\n");
}

/* ══════════════════════════════════════════════════════════════════════════
 *  BINARY STATE  (.rx8 format)
 *
 *  Magic (4) + Version (4) + vocab_n (4) + coupling_events (8) +
 *  total_steps (8) + last_word (WORD_LEN) +
 *  For each word: word (WORD_LEN) + beta (8) + E (8) + age (8) +
 *                 nbr_n (4) + nbr_idx (N_NBRS×4) + nbr_w (N_NBRS×4)
 *
 *  The morph vector is recomputed from the word string on load.
 * ══════════════════════════════════════════════════════════════════════════ */

int ahura_save(const char *path) {
    FILE *fp = fopen(path, "wb");
    if (!fp) { fprintf(stderr,"[ahura] save failed: %s\n", path); return 0; }

    uint32_t magic   = RX8_MAGIC;
    uint32_t version = RX8_VERSION;
    uint32_t vocab_n = G_n;
    uint64_t coup    = G_obd2.coupling_events;
    uint64_t steps   = G_obd2.total_steps;

    fwrite(&magic,   4, 1, fp);
    fwrite(&version, 4, 1, fp);
    fwrite(&vocab_n, 4, 1, fp);
    fwrite(&coup,    8, 1, fp);
    fwrite(&steps,   8, 1, fp);
    fwrite(G_obd2.last_word, WORD_LEN, 1, fp);

    uint32_t k;
    for (k=0; k<G_n; k++) {
        HousingWord *w = &G_words[k];
        fwrite(w->word, WORD_LEN, 1, fp);
        fwrite(&w->beta, 8, 1, fp);
        fwrite(&w->E,    8, 1, fp);
        fwrite(&w->age,  8, 1, fp);
        int32_t nbr_n = w->nbr_n;
        fwrite(&nbr_n, 4, 1, fp);
        fwrite(w->nbr,   N_NBRS * 4, 1, fp);
        fwrite(w->nbr_w, N_NBRS * 4, 1, fp);
    }

    fclose(fp);
    fprintf(stderr, "[ahura] saved %u words → %s\n", G_n, path);
    return 1;
}

int ahura_load(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return 0;

    uint32_t magic, version, vocab_n;
    uint64_t coup, steps;
    if (fread(&magic,   4, 1, fp) < 1) { fclose(fp); return 0; }
    if (magic != RX8_MAGIC) {
        fprintf(stderr,"[ahura] wrong magic in %s (got 0x%X, want 0x%X)\n",
                path, magic, RX8_MAGIC);
        fclose(fp); return 0;
    }
    if (fread(&version, 4, 1, fp) < 1) { fclose(fp); return 0; }
    if (fread(&vocab_n, 4, 1, fp) < 1) { fclose(fp); return 0; }
    if (fread(&coup,    8, 1, fp) < 1) { fclose(fp); return 0; }
    if (fread(&steps,   8, 1, fp) < 1) { fclose(fp); return 0; }
    if (fread(G_obd2.last_word, WORD_LEN, 1, fp) < 1) { fclose(fp); return 0; }

    G_obd2.coupling_events = coup;
    G_obd2.total_steps     = steps;

    /* Reset vocab */
    memset(G_words, 0, sizeof(G_words));
    memset(G_ht,    0, sizeof(G_ht));
    G_n = 0;

    uint32_t i;
    for (i=0; i<vocab_n && i<VOCAB_MAX; i++) {
        HousingWord tmp;
        memset(&tmp, 0, sizeof(tmp));
        if (fread(tmp.word,  WORD_LEN, 1, fp) < 1) break;
        if (fread(&tmp.beta, 8, 1, fp) < 1) break;
        if (fread(&tmp.E,    8, 1, fp) < 1) break;
        if (fread(&tmp.age,  8, 1, fp) < 1) break;
        int32_t nbr_n;
        if (fread(&nbr_n, 4, 1, fp) < 1) break;
        if (fread(tmp.nbr,   N_NBRS * 4, 1, fp) < 1) break;
        if (fread(tmp.nbr_w, N_NBRS * 4, 1, fp) < 1) break;
        tmp.nbr_n = nbr_n;

        uint32_t idx = vocab_get(tmp.word);
        if (idx == UINT32_MAX) break;
        G_words[idx].beta  = tmp.beta;
        G_words[idx].E     = tmp.E;
        G_words[idx].age   = tmp.age;
        G_words[idx].nbr_n = tmp.nbr_n < N_NBRS ? tmp.nbr_n : N_NBRS;
        memcpy(G_words[idx].nbr,   tmp.nbr,   sizeof(tmp.nbr));
        memcpy(G_words[idx].nbr_w, tmp.nbr_w, sizeof(tmp.nbr_w));
        /* mv is recomputed by vocab_get — no need to restore */
    }

    fclose(fp);
    fprintf(stderr, "[ahura] loaded %u words from %s\n", G_n, path);
    return 1;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  LEARN FROM FILE
 * ══════════════════════════════════════════════════════════════════════════ */

static int learn_file(const char *path, double weight) {
    FILE *fp = fopen(path, "r");
    if (!fp) { fprintf(stderr,"[ahura] cannot open: %s\n", path); return 0; }
    static char line[65536];
    int total = 0;
    while (fgets(line, sizeof(line), fp)) {
        int n = ahura_ingest(line, weight);
        if (n > 0) { total += n; fprintf(stderr,"\r  [+%d | vocab=%u]  ", total, G_n); }
    }
    fprintf(stderr,"\n  learned %d words from %s  (vocab=%u)\n", total, path, G_n);
    fclose(fp);
    return total;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ANNOTATED SPEAK  — word (operator gloss, best neighbour)
 * ══════════════════════════════════════════════════════════════════════════ */

static void speak_word_annotated(const char *word, FILE *f) {
    if (!word || !word[0]) { fprintf(f, "\xe2\x88\x85"); return; }

    uint32_t idx = vocab_find(word);
    int tty = isatty(fileno(f));
    const char *DIM = tty ? "\033[2;90m" : "";
    const char *RST = tty ? "\033[0m"    : "";
    int dom = G_obd2.drive_shaft_dom;

    if (idx == UINT32_MAX) {
        fprintf(f, "%s %s(%s)%s", word, DIM, AHURA_OP_GLOSS[dom], RST);
        return;
    }
    HousingWord *w = &G_words[idx];
    const char *nbr = NULL;
    float best = 0.0f;
    int j;
    for (j=0; j<w->nbr_n; j++) {
        uint32_t ni = w->nbr[j];
        if (ni < G_n && w->nbr_w[j] > best) { best = w->nbr_w[j]; nbr = G_words[ni].word; }
    }
    if (nbr && best > 0.20f)
        fprintf(f, "%s %s(%s, %s)%s", word, DIM, AHURA_OP_GLOSS[dom], nbr, RST);
    else
        fprintf(f, "%s %s(%s)%s",     word, DIM, AHURA_OP_GLOSS[dom],      RST);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HEAR + SPEAK  — ingest prompt, spin the Wankel, emit n_words
 * ══════════════════════════════════════════════════════════════════════════ */

/*
 * Information conservation:  public_key(prompt) + private_key(response) = 0
 *
 * The 0 is not the empty set — it is the zero-divisor geometry encoding the
 * exchange.  Three source weights preserve asymmetry:
 *
 *   corpus ingestion  1.0   world knowledge, background field
 *   Author prompt     2.0   current intention, privileged input
 *   engine self-voice 0.5   what was said, heard back — closes the cycle
 *
 * Holcus hears everything he says.  Memory is emergent.  Context is deterministic.
 * Each input is needed only once — the geometry encodes the exchange permanently.
 */
static void hear_and_speak(const char *prompt, int n_words, FILE *out) {
    ahura_ingest(prompt, 2.0);   /* Author voice — privileged */
    ahura_intake(prompt);

    int produced = 0;
    int max_steps = n_words * 12;  /* 2 revolutions per word budget */
    while (produced < n_words && max_steps-- > 0) {
        const char *w = ahura_rotate();
        if (w) {
            if (produced > 0) fputc(' ', out);
            speak_word_annotated(w, out);
            ahura_ingest(w, 0.5);   /* engine hears its own voice */
            produced++;
        }
    }
    if (!produced) fprintf(out, "\xe2\x88\x85");
    fputc('\n', out);
    fflush(out);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REPL  — interactive conversation loop
 * ══════════════════════════════════════════════════════════════════════════ */

static void repl_loop(int n_words, FILE *out) {
    static char line[65536];
    int interactive = isatty(fileno(stdin));

    if (interactive)
        fprintf(stderr, "\n[Ahura Mazda v" AHURA_VERSION "]  vocab=%u"
                        "  (Ctrl-D to exit)\n\n", G_n);

    while (G_running) {
        if (interactive) fprintf(stderr, "> ");
        if (!fgets(line, sizeof(line), stdin)) break;
        int len = (int)strlen(line);
        while (len > 0 && (line[len-1]=='\n'||line[len-1]=='\r')) line[--len]='\0';
        if (!len) continue;
        hear_and_speak(line, n_words, out);
    }
    if (interactive) fprintf(stderr, "\n[ahura] exiting.\n");
}

/* ══════════════════════════════════════════════════════════════════════════
 *  BACKGROUND THREAD  — auto-save + watchdog
 * ══════════════════════════════════════════════════════════════════════════ */

static char      G_bin_path[4096] = "";
static pthread_t G_bg_tid;
static int       G_bg_started = 0;

static void *bg_thread_fn(void *arg) {
    (void)arg;
    time_t last_save = time(NULL);
    while (G_running) {
        sleep(5);
        if (!G_running) break;
        if (!G_bin_path[0]) continue;
        time_t now = time(NULL);
        if ((now - last_save) >= 60) {
            pthread_mutex_lock(&G_lock);
            ahura_save(G_bin_path);
            pthread_mutex_unlock(&G_lock);
            last_save = now;
        }
    }
    if (G_bin_path[0]) {
        pthread_mutex_lock(&G_lock);
        ahura_save(G_bin_path);
        pthread_mutex_unlock(&G_lock);
    }
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  TEACHING DAEMON  — TCP server, same port as monad (7297)
 *  Clients send text lines; daemon ingests them.
 * ══════════════════════════════════════════════════════════════════════════ */

static int G_daemon_fd = -1;

static void *daemon_client_thread(void *arg) {
    int fd = *(int*)arg; free(arg);
    static char buf[65536];
    ssize_t nr;
    while ((nr = recv(fd, buf, sizeof(buf)-1, 0)) > 0) {
        buf[nr] = '\0';
        int n = ahura_ingest(buf, 1.0);
        char resp[64];
        snprintf(resp, sizeof(resp), "+%d\n", n);
        send(fd, resp, strlen(resp), 0);
    }
    close(fd);
    return NULL;
}

static void *daemon_thread(void *arg) {
    int port = *(int*)arg; free(arg);
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    if (srv < 0) { perror("socket"); return NULL; }
    int opt = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    struct sockaddr_in sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin_family      = AF_INET;
    sa.sin_addr.s_addr = INADDR_ANY;
    sa.sin_port        = htons((uint16_t)port);
    if (bind(srv, (struct sockaddr*)&sa, sizeof(sa)) < 0) {
        perror("bind"); close(srv); return NULL;
    }
    listen(srv, 8);
    G_daemon_fd = srv;
    fprintf(stderr, "[daemon] listening on port %d\n", port);
    while (G_running) {
        struct sockaddr_in ca; socklen_t cal = sizeof(ca);
        int cfd = accept(srv, (struct sockaddr*)&ca, &cal);
        if (cfd < 0) { if (G_running) perror("accept"); break; }
        int *pfd = (int*)malloc(sizeof(int)); *pfd = cfd;
        pthread_t tid;
        pthread_create(&tid, NULL, daemon_client_thread, pfd);
        pthread_detach(tid);
    }
    close(srv);
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  MAIN  — CLI
 * ══════════════════════════════════════════════════════════════════════════ */

static void print_usage(const char *prog) {
    fprintf(stderr,
        "Ahura Mazda  —  Wankel Rotary Semantic Engine  v" AHURA_VERSION "\n"
        "3 = 1 + 15i  |  The Sedenion is The Work, not The Worker.\n\n"
        "  %s prompt text here         (speak immediately, then REPL if tty)\n"
        "  %s                          (REPL)\n\n"
        "  --speak PROMPT [N]          Wankel cycle: produce N words (default 12)\n"
        "  --intake PROMPT             Trace one full 6-port cycle step-by-step\n"
        "  --words N                   Words per REPL response (default 12)\n"
        "  --learn-file PATH           Ingest .txt file into housing\n"
        "  --teach                     Ingest from stdin (no response)\n"
        "  --query WORD                Housing entry: β, E, morph vector, neighbours\n"
        "  --report                    OBD2 diagnostic + drive shaft report\n"
        "  --obd2                      OBD2 after last speak (same as --report)\n"
        "  --load-bin PATH             Load .rx8 state file\n"
        "  --save-bin PATH             Save .rx8 state file\n"
        "  --daemon [PORT]             TCP teaching server (default 7297)\n\n"
        "State:  ~/.ptolemy/ahura.rx8  (auto-loaded and auto-saved every 60 s)\n"
        "\nDropped from monad.c (not applicable to rotary engine):\n"
        "  --generate  cam_encode sedenion generation  → use --speak\n"
        "  --url       HTTP fetch  → pipe wget/curl output to --teach via stdin\n",
        prog, prog);
}

static void signal_handler(int sig) {
    (void)sig;
    G_running = 0;
    if (G_daemon_fd >= 0) close(G_daemon_fd);
}

int main(int argc, char **argv) {
    ahura_init();

    signal(SIGINT,  signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGPIPE, SIG_IGN);

    /* Auto-load default state */
    {
        const char *home = getenv("HOME");
        if (home) {
            snprintf(G_bin_path, sizeof(G_bin_path), "%s/.ptolemy/ahura.rx8", home);
            if (access(G_bin_path, F_OK) == 0)
                ahura_load(G_bin_path);
        }
    }

    /* Start background auto-save thread */
    pthread_create(&G_bg_tid, NULL, bg_thread_fn, NULL);
    G_bg_started = 1;

    int n_words = 12;

    /* Conversational default — first arg not a flag */
    if (argc >= 2 && argv[1][0] != '-') {
        char prompt[65536] = "";
        int a;
        for (a=1; a<argc; a++) {
            if (a>1) strncat(prompt, " ", sizeof(prompt)-strlen(prompt)-1);
            strncat(prompt, argv[a], sizeof(prompt)-strlen(prompt)-1);
        }
        hear_and_speak(prompt, n_words, stdout);
        if (isatty(fileno(stdin))) repl_loop(n_words, stdout);
        G_running = 0;
        if (G_bg_started) { pthread_join(G_bg_tid, NULL); G_bg_started=0; }
        ahura_free();
        return 0;
    }

    /* No args: REPL or usage */
    if (argc == 1) {
        if (isatty(fileno(stdin))) repl_loop(n_words, stdout);
        else print_usage(argv[0]);
        G_running = 0;
        if (G_bg_started) { pthread_join(G_bg_tid, NULL); G_bg_started=0; }
        ahura_free();
        return 0;
    }

    /* Flag processing */
    int i;
    for (i=1; i<argc; i++) {

        if (!strcmp(argv[i], "--load-bin")) {
            if (i+1 >= argc) { fprintf(stderr,"--load-bin needs PATH\n"); continue; }
            ahura_load(argv[++i]);
            strncpy(G_bin_path, argv[i], sizeof(G_bin_path)-1);

        } else if (!strcmp(argv[i], "--save-bin")) {
            if (i+1 >= argc) { fprintf(stderr,"--save-bin needs PATH\n"); continue; }
            ahura_save(argv[++i]);

        } else if (!strcmp(argv[i], "--words")) {
            if (i+1 >= argc) continue;
            n_words = atoi(argv[++i]);
            if (n_words < 1) n_words = 1;
            if (n_words > 256) n_words = 256;

        } else if (!strcmp(argv[i], "--learn-file")) {
            if (i+1 >= argc) { fprintf(stderr,"--learn-file needs PATH\n"); continue; }
            learn_file(argv[++i], 1.0);

        } else if (!strcmp(argv[i], "--teach")) {
            static char line[65536];
            fprintf(stderr,"[ahura] teaching from stdin (Ctrl-D to stop)...\n");
            while (fgets(line, sizeof(line), stdin)) {
                int n = ahura_ingest(line, 1.0);
                if (n > 0) fprintf(stderr,"\r[+%d | vocab=%u]  ", n, G_n);
            }
            fprintf(stderr,"\n[ahura] stdin closed. vocab=%u\n", G_n);

        } else if (!strcmp(argv[i], "--speak")) {
            if (i+1 >= argc) { fprintf(stderr,"--speak needs PROMPT\n"); continue; }
            char prompt[65536];
            strncpy(prompt, argv[++i], sizeof(prompt)-1);
            int nw = n_words;
            if (i+1 < argc && argv[i+1][0] != '-') nw = atoi(argv[++i]);
            hear_and_speak(prompt, nw, stdout);

        } else if (!strcmp(argv[i], "--intake")) {
            if (i+1 >= argc) { fprintf(stderr,"--intake needs PROMPT\n"); continue; }
            ahura_port_trace(argv[++i], stdout);

        } else if (!strcmp(argv[i], "--query")) {
            if (i+1 >= argc) { fprintf(stderr,"--query needs WORD\n"); continue; }
            const char *qw = argv[++i];
            uint32_t idx = vocab_find(qw);
            if (idx == UINT32_MAX) {
                printf("'%s' not in housing\n", qw);
            } else {
                HousingWord *w = &G_words[idx];
                printf("housing('%s'):\n", qw);
                printf("  β=%.6f  E=%.6f  age=%.1f  zero_idx=%u\n",
                       w->beta, w->E, w->age, word_zero_idx(qw));
                printf("  morph vector:\n");
                int d;
                for (d=0; d<SED_DIM; d++)
                    if (w->mv[d] > GAP * 2)
                        printf("    e%2d %-14s  %.4f\n", d, AHURA_OP_GLOSS[d], w->mv[d]);
                printf("  neighbours[%d]:", w->nbr_n);
                int j;
                for (j=0; j<w->nbr_n; j++) {
                    uint32_t ni = w->nbr[j];
                    if (ni < G_n) printf(" %s(%.3f)", G_words[ni].word, w->nbr_w[j]);
                }
                printf("\n");
            }

        } else if (!strcmp(argv[i], "--report") || !strcmp(argv[i], "--obd2")) {
            /* Run a speak cycle to populate OBD2 if field is loaded */
            if (G_n > 0 && G_obd2.last_word[0] == '\0') {
                const char *seed = G_words[0].word;
                ahura_speak(seed, 4);
            }
            ahura_report(stdout);

        } else if (!strcmp(argv[i], "--daemon")) {
            int port = 7297;
            if (i+1 < argc && argv[i+1][0] != '-') port = atoi(argv[++i]);
            int *pp = (int*)malloc(sizeof(int)); *pp = port;
            pthread_t tid;
            pthread_create(&tid, NULL, daemon_thread, pp);
            fprintf(stderr,"[ahura] daemon on port %d. Ctrl-C to stop.\n", port);
            while (G_running) {
                sleep(60);
                if (G_running)
                    fprintf(stderr,"[ahura] vocab=%u  coupling_events=%llu\n",
                            G_n, (unsigned long long)G_obd2.coupling_events);
            }
            pthread_join(tid, NULL);

        } else if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-h")) {
            print_usage(argv[0]);

        } else {
            fprintf(stderr,"[ahura] unknown flag: %s\n", argv[i]);
        }
    }

    G_running = 0;
    if (G_bg_started) { pthread_join(G_bg_tid, NULL); G_bg_started=0; }
    ahura_free();
    return 0;
}
