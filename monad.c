/*
 * monad.c — Ptolemy sedenion learning engine  (C canonical, v1.218)
 *
 * Self-contained. Deps: libc, libm, pthreads, POSIX sockets.
 * No transformers. No autoregression. No LLMs.
 *
 * Build:   gcc -O2 -Wall -std=c99 -o ptolemy-monad monad.c -lm -lpthread
 * Install: pkexec install -m 755 ptolemy-monad /usr/local/bin/ptolemy-monad
 *
 * CLI:
 *   ptolemy-monad --teach                  (read stdin, learn forever)
 *   ptolemy-monad --learn-file PATH        (ingest .txt file)
 *   ptolemy-monad --url URL               (fetch HTTP URL and ingest)
 *   ptolemy-monad --generate SEED [N]     (generate N words from seed)
 *   ptolemy-monad --query WORD            (print sedenion for word)
 *   ptolemy-monad --report                (Hamiltonian report)
 *   ptolemy-monad --load-bin PATH         (load .ptol state)
 *   ptolemy-monad --save-bin PATH         (save .ptol state)
 *   ptolemy-monad --daemon PORT           (TCP teaching server, port default 7297)
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <signal.h>
#include <ctype.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* ── Constants ──────────────────────────────────────────────────────────── */
#define PTOL_VERSION      "1.219"
#define SED_DIM           16
#define OMEGA_ZS          0.56714    /* Lambert W(1); BAO spectral gap */
#define GAP               0.000707   /* Yang-Mills mass gap; semantic vacuum */
#define D_STAR            0.24600    /* Fermat proximity threshold */
#define SIGMA_CRIT        0.5        /* critical line σ = ½ */
#define PHI               1.6180339887498949
#define SQRT2             1.4142135623730951

/* Vocabulary limits */
#define VOCAB_MAX         (1 << 17)   /* 131072 words */
#define VOCAB_HT_SZ       (1 << 18)   /* hash table slots (> VOCAB_MAX) */
#define WORD_LEN          52          /* max word length + null */
#define N_NBRS            24          /* A-matrix neighbours per word */
#define WINDOW_SZ         16          /* sliding context window */
#define RECENT_SZ         8           /* no-repeat buffer */
#define CHUNK_WORDS       64          /* words per learning chunk */

/* Binary format */
#define PTOL_MAGIC        0x4C544F50u /* "PTOL" little-endian */
#define PTOL_BIN_VER      3

/* ── Operator glosses — plain-English sedenion dimension labels ────────── */
static const char *OP_GLOSS[SED_DIM] = {
    "self",         /* e0  identity */
    "negation",     /* e1  negate */
    "binding",      /* e2  bind */
    "the Indexor",  /* e3  name */
    "action",       /* e4  apply */
    "quality",      /* e5  abstract */
    "decision",     /* e6  branch */
    "sequence",     /* e7  iterate */
    "depth",        /* e8  recurse */
    "allocation",   /* e9  allocate */
    "inquiry",      /* e10 query */
    "reference",    /* e11 dereference */
    "composition",  /* e12 compose */
    "parallel",     /* e13 parallelize */
    "signal",       /* e14 interrupt */
    "voice",        /* e15 emit */
};

/* ── Auto-save path and background thread ──────────────────────────────── */
static char     G_bin_path[4096] = "";   /* path for auto-save; set in main() */
static pthread_t G_bg_tid;
static int       G_bg_started = 0;

/* ── Riemann zeros (first 20) ────────────────────────────────────────────── */
static const double RIEMANN_ZEROS[20] = {
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
};

/* ── Sedenion types ──────────────────────────────────────────────────────── */
typedef double Sed[SED_DIM];

typedef struct { int sign; int k; } SedEntry;

static SedEntry OCT[8][8];  /* 8×8 octonion table (Fano plane) */
static SedEntry SED[16][16]; /* 16×16 sedenion table (Cayley-Dickson) */

/* ══════════════════════════════════════════════════════════════════════════
 *  SEDENION ALGEBRA
 * ══════════════════════════════════════════════════════════════════════════ */

static void build_oct_table(void) {
    int i, j;
    /* Identity row/col */
    for (i = 0; i < 8; i++) {
        OCT[0][i].sign = 1; OCT[0][i].k = i;
        OCT[i][0].sign = 1; OCT[i][0].k = i;
    }
    /* e_i * e_i = -e_0 */
    for (i = 1; i < 8; i++) { OCT[i][i].sign = -1; OCT[i][i].k = 0; }

    /* Fano plane triples — EXACT match of Python _build_oct_table() */
    static const int T[7][3] = {
        {1,2,3},{1,4,5},{1,7,6},{2,4,6},{2,5,7},{3,4,7},{3,6,5}
    };
    int t;
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
    /* Cayley-Dickson doubling — EXACT match of Python _build_sed_table() */
    int i, j;
    for (i = 0; i < 16; i++) {
        for (j = 0; j < 16; j++) {
            int ih = (i >= 8), jh = (j >= 8);
            int io = ih ? i - 8 : i;
            int jo = jh ? j - 8 : j;
            if (!ih && !jh) {
                SED[i][j] = OCT[io][jo];
            } else if (!ih && jh) {
                SedEntry e = OCT[jo][io];
                SED[i][j].sign = e.sign;
                SED[i][j].k    = e.k + 8;
            } else if (ih && !jh) {
                if (jo == 0) {
                    SED[i][j].sign = 1; SED[i][j].k = i;
                } else {
                    SedEntry e = OCT[io][jo];
                    SED[i][j].sign = -e.sign;
                    SED[i][j].k    =  e.k + 8;
                }
            } else { /* ih && jh */
                if (jo == 0) {
                    SED[i][j].sign = -1; SED[i][j].k = io;
                } else {
                    SedEntry e = OCT[jo][io];
                    SED[i][j].sign = e.sign;
                    SED[i][j].k    = e.k;
                }
            }
        }
    }
}

static void sed_zero(Sed a) {
    memset(a, 0, sizeof(Sed));
}
static void sed_copy(Sed dst, const Sed src) {
    memcpy(dst, src, sizeof(Sed));
}
static double sed_norm(const Sed a) {
    double s = 0.0;
    int k;
    for (k = 0; k < SED_DIM; k++) s += a[k]*a[k];
    return sqrt(s);
}
static void sed_scale(Sed a, double f) {
    int k;
    for (k = 0; k < SED_DIM; k++) a[k] *= f;
}
static void sed_normalize(Sed a) {
    double n = sed_norm(a);
    if (n > 1e-15) sed_scale(a, 1.0/n);
}
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
static void sed_add(Sed a, const Sed b) {
    int k;
    for (k = 0; k < SED_DIM; k++) a[k] += b[k];
}
static double sed_dot(const Sed a, const Sed b) {
    double s = 0.0;
    int k;
    for (k = 0; k < SED_DIM; k++) s += a[k]*b[k];
    return s;
}
static void sed_basis(int k, Sed out) {
    sed_zero(out);
    if (k >= 0 && k < SED_DIM) out[k] = 1.0;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  WORD HASH (FNV-1a → [0,1])  Replaces Python SHA-256 _whash()
 * ══════════════════════════════════════════════════════════════════════════ */
static double word_hash(const char *w) {
    uint64_t h = 14695981039346656037ULL;
    for (; *w; w++) {
        h ^= (uint64_t)(unsigned char)*w;
        h *= 1099511628211ULL;
    }
    /* Mix high/low halves for better distribution */
    h ^= h >> 33;
    h *= 0xff51afd7ed558ccdULL;
    h ^= h >> 33;
    return (double)(h & 0x7FFFFFFFFFFFFFFFULL) / (double)0x7FFFFFFFFFFFFFFFULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  CAM_ENCODE — Linguistic prompt → unit sedenion
 *  Ported exactly from Python cam_encode() in monad.py
 * ══════════════════════════════════════════════════════════════════════════ */

/* Word set membership via sorted string arrays + binary search */
typedef struct { const char **w; int n; } WordSet;

#define DEF_SET(name, ...) \
    static const char *_##name##_arr[] = { __VA_ARGS__, NULL }; \
    static int _##name##_n = -1; \
    static WordSet WS_##name

static int ws_cmp(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}
static void ws_init(WordSet *ws, const char **arr) {
    int n = 0;
    while (arr[n]) n++;
    /* sort for binary search */
    qsort((void*)arr, n, sizeof(char*), ws_cmp);
    ws->w = arr; ws->n = n;
}
static int ws_has(const WordSet *ws, const char *w) {
    int lo = 0, hi = ws->n - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >> 1;
        int c = strcmp(ws->w[mid], w);
        if (c == 0) return 1;
        if (c < 0) lo = mid + 1; else hi = mid - 1;
    }
    return 0;
}

/* Pronouns */
static const char *_PRONOUNS_arr[] = {
    "i","me","my","mine","myself","we","us","our","ours","ourselves",
    "you","your","yours","yourself","yourselves",
    "he","him","his","himself","she","her","hers","herself",
    "it","its","itself","they","them","their","theirs","themselves",
    "this","that","these","those","here","there","who","what","which", NULL
};
static WordSet WS_PRONOUNS;

/* Auxiliaries */
static const char *_AUX_arr[] = {
    "is","are","was","were","be","been","being",
    "do","does","did","have","has","had",
    "will","would","can","could","should","shall","may","might","must", NULL
};
static WordSet WS_AUX;

/* Conjunctions */
static const char *_CONJ_arr[] = {
    "and","or","but","so","yet","for","nor",
    "although","because","if","then","when","while",
    "since","unless","until","though", NULL
};
static WordSet WS_CONJ;

/* Time words */
static const char *_TIME_arr[] = {
    "now","then","before","after","when","while","ago","yet",
    "already","still","soon","later","today","yesterday","tomorrow",
    "always","never","sometimes","often","rarely","was","were",
    "will","would","has","have","had", NULL
};
static WordSet WS_TIME;

/* Question words */
static const char *_QUEST_arr[] = {
    "what","which","who","whom","whose","when","where","why","how","whether","if", NULL
};
static WordSet WS_QUEST;

/* Negation */
static const char *_NEG_arr[] = {
    "not","never","no","nor","nothing","nobody","nowhere","neither", NULL
};
static WordSet WS_NEG;

/* Determiners */
static const char *_DET_arr[] = {
    "a","an","the","some","any","every","each","all","both",
    "few","many","much","more","most","less","least", NULL
};
static WordSet WS_DET;

/* Meta-discourse */
static const char *_META_arr[] = {
    "mean","means","meaning","say","says","said","tell","tells","told",
    "explain","explains","clarify","summarise","summarize","rephrase","repeat", NULL
};
static WordSet WS_META;

/* Positive affect */
static const char *_POS_arr[] = {
    "good","great","love","like","enjoy","happy","glad","pleased",
    "wonderful","excellent","amazing","thank","thanks","please", NULL
};
static WordSet WS_POS;

/* Negative affect */
static const char *_NEG_AFF_arr[] = {
    "bad","hate","dislike","angry","sad","sorry","worried","fear",
    "terrible","awful","horrible","wrong","mistake","fail", NULL
};
static WordSet WS_NEG_AFF;

/* Anaphor resolvers (s[11]) */
static const char *_ANAPH_arr[] = {
    "it","its","they","them","their","he","she","who","which", NULL
};
static WordSet WS_ANAPH;

/* Presupposition markers (s[12]) */
static const char *_PRES_arr[] = {
    "the","already","again","still","even","also","too", NULL
};
static WordSet WS_PRES;

static void cam_wordsets_init(void) {
    ws_init(&WS_PRONOUNS, _PRONOUNS_arr);
    ws_init(&WS_AUX,      _AUX_arr);
    ws_init(&WS_CONJ,     _CONJ_arr);
    ws_init(&WS_TIME,     _TIME_arr);
    ws_init(&WS_QUEST,    _QUEST_arr);
    ws_init(&WS_NEG,      _NEG_arr);
    ws_init(&WS_DET,      _DET_arr);
    ws_init(&WS_META,     _META_arr);
    ws_init(&WS_POS,      _POS_arr);
    ws_init(&WS_NEG_AFF,  _NEG_AFF_arr);
    ws_init(&WS_ANAPH,    _ANAPH_arr);
    ws_init(&WS_PRES,     _PRES_arr);
}

/* cam_encode: text → unit sedenion.
 * Exact port of Python cam_encode(). */
static void cam_encode(const char *text, Sed out) {
    /* tokenize into lowercase words */
    static char buf[1 << 20];  /* 1MB work buffer */
    strncpy(buf, text, sizeof(buf)-1); buf[sizeof(buf)-1] = '\0';

    static char *tokens[65536];
    static char lwords[65536][WORD_LEN];
    int n = 0;

    char *p = strtok(buf, " \t\r\n");
    while (p && n < 65535) {
        int i = 0;
        while (*p && i < WORD_LEN-1) {
            lwords[n][i++] = (char)tolower((unsigned char)*p++);
        }
        lwords[n][i] = '\0';
        tokens[n] = lwords[n];
        n++;
        p = strtok(NULL, " \t\r\n");
    }
    if (n == 0) n = 1;

    sed_zero(out);
    /* s[0] = log(n+1) / log(512) */
    out[0] = log((double)(n+1)) / log(512.0);

    int t;
    for (t = 0; t < n; t++) {
        const char *w = tokens[t];
        int wlen = (int)strlen(w);
        double h = word_hash(w);
        double inv_n = 1.0 / (double)n;

        /* s[1]: word hash sum */
        out[1] += h * inv_n;

        /* s[2]: conjunctions */
        if (ws_has(&WS_CONJ, w)) out[2] += inv_n;

        /* s[3]: content words (not stop-class, len >= 4) */
        if (!ws_has(&WS_PRONOUNS, w) && !ws_has(&WS_AUX, w)
         && !ws_has(&WS_CONJ, w) && !ws_has(&WS_TIME, w)
         && !ws_has(&WS_QUEST, w) && !ws_has(&WS_DET, w)
         && !ws_has(&WS_META, w) && !ws_has(&WS_POS, w)
         && !ws_has(&WS_NEG_AFF, w) && wlen >= 4)
            out[3] += inv_n;

        /* s[4]: auxiliaries and verb morphology (-ing, -ed) */
        if (ws_has(&WS_AUX, w)
         || (wlen > 3 && strcmp(w+wlen-3,"ing")==0)
         || (wlen > 2 && strcmp(w+wlen-2,"ed")==0))
            out[4] += inv_n;

        /* s[5]: adverbs/adjectives (-ly, -ful, -ous) */
        if ((wlen > 2 && strcmp(w+wlen-2,"ly")==0)
         || (wlen > 3 && strcmp(w+wlen-3,"ful")==0)
         || (wlen > 3 && strcmp(w+wlen-3,"ous")==0))
            out[5] += inv_n;

        /* s[6]: negation or conjunctions */
        if (ws_has(&WS_NEG, w) || ws_has(&WS_CONJ, w)) out[6] += inv_n;

        /* s[7]: temporal markers */
        if (ws_has(&WS_TIME, w)) out[7] += inv_n;

        /* s[8]: pronouns */
        if (ws_has(&WS_PRONOUNS, w)) out[8] += inv_n;

        /* s[9]: word hash * 0.5 (non-pronoun, non-aux, len >= 3) */
        if (!ws_has(&WS_PRONOUNS, w) && !ws_has(&WS_AUX, w) && wlen >= 3)
            out[9] += h * 0.5 * inv_n;

        /* s[10]: question words */
        if (ws_has(&WS_QUEST, w)) out[10] += inv_n;

        /* s[11]: specific anaphor pronouns */
        if (ws_has(&WS_ANAPH, w)) out[11] += inv_n;

        /* s[12]: presupposition markers */
        if (ws_has(&WS_PRES, w)) out[12] += inv_n;

        /* s[13]: average word length / 12 */
        out[13] += (double)wlen / 12.0 * inv_n;

        /* s[14]: positive/negative affect */
        if (ws_has(&WS_POS, w))     out[14] += inv_n;
        else if (ws_has(&WS_NEG_AFF, w)) out[14] -= inv_n;

        /* s[15]: meta-discourse */
        if (ws_has(&WS_META, w)) out[15] += inv_n;
    }

    /* s[14]: floor at 0 */
    if (out[14] < 0.0) out[14] = 0.0;

    /* All dims except s[0]: floor at GAP */
    int k;
    for (k = 1; k < SED_DIM; k++)
        if (out[k] < GAP) out[k] = GAP;

    sed_normalize(out);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  VOCABULARY — open-addressed hash table
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct {
    char   word[WORD_LEN];
    double beta;           /* scalar field amplitude */
    double E;              /* Riemann energy */
    double age;            /* recency (0=fresh, grows with time) */
    /* A-matrix: top N_NBRS co-occurrence neighbours */
    uint32_t nbr[N_NBRS];
    float    nbr_w[N_NBRS];
    int      nbr_n;        /* actual count */
} Word;

static Word     *G_words;           /* word array */
static uint32_t  G_n;               /* vocab size */
static uint32_t  G_ht[VOCAB_HT_SZ]; /* hash table: word str → index+1 */

static uint32_t ht_slot(const char *w) {
    uint64_t h = 14695981039346656037ULL;
    for (; *w; w++) {
        h ^= (uint64_t)(unsigned char)*w;
        h *= 1099511628211ULL;
    }
    return (uint32_t)(h & (VOCAB_HT_SZ - 1));
}

/* Find word index, or UINT32_MAX if not found */
static uint32_t vocab_find(const char *w) {
    uint32_t slot = ht_slot(w);
    int tries = 0;
    while (tries < VOCAB_HT_SZ) {
        uint32_t v = G_ht[slot];
        if (v == 0) return UINT32_MAX;          /* empty slot */
        if (strcmp(G_words[v-1].word, w) == 0)
            return v - 1;
        slot = (slot + 1) & (VOCAB_HT_SZ - 1);
        tries++;
    }
    return UINT32_MAX;
}

/* Find or allocate word entry */
static uint32_t vocab_get(const char *w) {
    uint32_t slot = ht_slot(w);
    int tries = 0;
    while (tries < VOCAB_HT_SZ) {
        uint32_t v = G_ht[slot];
        if (v == 0) {
            /* allocate */
            if (G_n >= VOCAB_MAX) return UINT32_MAX;  /* full */
            uint32_t idx = G_n++;
            Word *e = &G_words[idx];
            strncpy(e->word, w, WORD_LEN-1);
            e->word[WORD_LEN-1] = '\0';
            e->beta  = GAP;
            e->age   = 0.0;
            e->nbr_n = 0;
            /* Riemann energy: |sin(π*(idx+1)*φ / (γ+1))| */
            int zi = (int)(idx % 20);
            double gamma = RIEMANN_ZEROS[zi];
            e->E = fabs(sin(M_PI * (idx+1) * PHI / (gamma + 1.0)));
            G_ht[slot] = idx + 1;
            return idx;
        }
        if (strcmp(G_words[v-1].word, w) == 0) return v - 1;
        slot = (slot + 1) & (VOCAB_HT_SZ - 1);
        tries++;
    }
    return UINT32_MAX;
}

/* Add or reinforce A-matrix edge src→dst */
static void amat_add(uint32_t src, uint32_t dst, float weight) {
    if (src == UINT32_MAX || dst == UINT32_MAX || src == dst) return;
    Word *w = &G_words[src];
    /* Search existing */
    int i;
    for (i = 0; i < w->nbr_n; i++) {
        if (w->nbr[i] == dst) {
            float nv = w->nbr_w[i] + weight;
            w->nbr_w[i] = nv > 1.0f ? 1.0f : nv;
            return;
        }
    }
    /* Add new slot */
    if (w->nbr_n < N_NBRS) {
        w->nbr[w->nbr_n]   = dst;
        w->nbr_w[w->nbr_n] = weight > 1.0f ? 1.0f : weight;
        w->nbr_n++;
        return;
    }
    /* Evict weakest */
    int min_i = 0;
    for (i = 1; i < N_NBRS; i++)
        if (w->nbr_w[i] < w->nbr_w[min_i]) min_i = i;
    if (weight > w->nbr_w[min_i]) {
        w->nbr[min_i]   = dst;
        w->nbr_w[min_i] = weight > 1.0f ? 1.0f : weight;
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ENGINE STATE (global singleton)
 * ══════════════════════════════════════════════════════════════════════════ */

static struct {
    /* Context window (ring buffer) */
    uint32_t window[WINDOW_SZ];
    int      win_head, win_n;

    /* Prompt sedenion */
    Sed      prompt_sed;
    double   prompt_psi[SED_DIM];
    int      has_prompt;

    /* Field state */
    double   psi_prev[SED_DIM];    /* previous window psi (for turbo) */
    double   bao_mean;
    double   field_health;

    /* Adaptive thresholds */
    double   redundancy_min, redundancy_max;
    double   novelty_min;
    double   noise_max;
    int      chunk_min_words;

    /* No-repeat buffer */
    uint32_t recent[RECENT_SZ];
    int      recent_n;

    /* Stats */
    uint64_t words_learned;
    uint64_t chunks_ingested;
    uint64_t words_emitted;
    int      dtc_p0087;            /* BAO fault count */
    int      segfaults;

    /* Threading */
    pthread_mutex_t lock;
    int      running;

    /* Emission threshold (adaptive) */
    double   emission_threshold;
} G;

/* ══════════════════════════════════════════════════════════════════════════
 *  J_MU — Dual Noether current
 * ══════════════════════════════════════════════════════════════════════════ */

/* Allocate J arrays — caller frees */
static double *jmu_alloc(void) {
    return (double *)calloc(G_n, sizeof(double));
}

static void j_mu(const double *window_psi, const double *prompt_psi,
                 double *J_pos, double *J_neg) {
    uint32_t k;
    for (k = 0; k < G_n; k++) {
        Word *w  = &G_words[k];
        double b = w->beta;
        double e2= w->E * w->E;
        double decay = exp(-w->age * 0.001);
        double base  = b * e2 * decay;
        J_pos[k] = base * window_psi[k % SED_DIM];
        J_neg[k] = base * prompt_psi[k % SED_DIM];
    }
}

static void a_propagate(double *J) {
    /* Single A-matrix hop: spread J through adjacency */
    static double J2[VOCAB_MAX];
    memcpy(J2, J, G_n * sizeof(double));
    uint32_t src;
    for (src = 0; src < G_n; src++) {
        if (J[src] < GAP) continue;
        Word *w = &G_words[src];
        int i;
        for (i = 0; i < w->nbr_n; i++) {
            uint32_t dst = w->nbr[i];
            if (dst < G_n)
                J2[dst] += J[src] * (double)w->nbr_w[i] * 0.5;
        }
    }
    memcpy(J, J2, G_n * sizeof(double));
}

/* ── DIM_ROLE (firing order) — exact match of Python Crank._DIM_ROLE ──── */
static const int DIM_ROLE[SED_DIM] = {
    /* e0  e1  e2  e3  e4  e5  e6  e7  e8  e9 e10 e11 e12 e13 e14 e15 */
       8,  8,  4,  0,  1,  2,  3,  5,  5,  5,  6,  6,  6,  7,  7,  7
};

typedef struct { double score; uint32_t idx; } Candidate;

static int cand_cmp(const void *a, const void *b) {
    const Candidate *ca = (const Candidate *)a;
    const Candidate *cb = (const Candidate *)b;
    /* Descending score */
    if (ca->score > cb->score) return -1;
    if (ca->score < cb->score) return +1;
    return 0;
}

/* sigma_candidates: score by σ = ½ proximity, sorted by DIM_ROLE then -score */
static int sigma_candidates(const double *J_pos, const double *J_neg,
                             Candidate *out, int max_out) {
    if (G_n == 0) return 0;

    /* Adaptive emission threshold */
    double max_jp = 0.0;
    uint32_t k;
    for (k = 0; k < G_n; k++)
        if (J_pos[k] > max_jp) max_jp = J_pos[k];
    double thr = max_jp * (G.emission_threshold / OMEGA_ZS) * 0.01;

    int n = 0;
    for (k = 0; k < G_n && n < max_out; k++) {
        double jp = J_pos[k], jn = J_neg[k];
        double total = jp + jn;
        if (total < thr || total < 1e-15) continue;
        double sigma = jp / total;
        double score = jp * (1.0 - fabs(sigma - 0.5) * 2.0);
        out[n].score = score;
        out[n].idx   = k;
        n++;
    }
    /* Sort by descending score */
    qsort(out, n, sizeof(Candidate), cand_cmp);
    return n;
}

/* Power steering: sedenion attention O(n) not O(n²) */
static void power_steering(double *J_pos, const double *window_psi,
                            const double *prompt_psi) {
    double T[SED_DIM], exp_T[SED_DIM], Z = 0.0;
    double T_max = -1e100;
    int k;
    for (k = 0; k < SED_DIM; k++) {
        T[k] = window_psi[k] * prompt_psi[k];
        if (T[k] > T_max) T_max = T[k];
    }
    for (k = 0; k < SED_DIM; k++) {
        exp_T[k] = exp((T[k] - T_max) / 4.0);
        Z += exp_T[k];
    }
    if (Z < 1e-15) Z = 1.0;
    double attn[SED_DIM];
    for (k = 0; k < SED_DIM; k++) attn[k] = exp_T[k] / Z;

    uint32_t i;
    for (i = 0; i < G_n; i++)
        J_pos[i] *= (1.0 + attn[i % SED_DIM]);
}

/* Fermat scan: check for zero-divisor proximity */
typedef struct { int i; int j; double prox; int is_zd; } FermatHit;

static int fermat_scan(const Sed ws, FermatHit *hits, int max_hits) {
    Sed sn; sed_copy(sn, ws); sed_normalize(sn);
    int n = 0;
    int i, j;
    for (i = 1; i < SED_DIM && n < max_hits; i++) {
        for (j = i+1; j < SED_DIM && n < max_hits; j++) {
            Sed probe; sed_zero(probe);
            probe[i] = 1.0 / SQRT2;
            probe[j] = 1.0 / SQRT2;
            Sed prod; sed_mul(sn, probe, prod);
            double pn   = sed_norm(prod);
            double prox = 1.0 - pn;
            if (prox > D_STAR) {
                hits[n].i     = i;
                hits[n].j     = j;
                hits[n].prox  = prox;
                hits[n].is_zd = pn < 1e-10;
                n++;
            }
        }
    }
    return n;
}

/* Window management */
static void window_push(uint32_t idx) {
    G.window[G.win_head % WINDOW_SZ] = idx;
    G.win_head++;
    if (G.win_n < WINDOW_SZ) G.win_n++;
}

static void window_sed(Sed out) {
    if (G.win_n == 0) { sed_basis(0, out); return; }
    /* Build text string from window words */
    static char wbuf[WORD_LEN * WINDOW_SZ + 64];
    wbuf[0] = '\0';
    int i;
    for (i = 0; i < G.win_n; i++) {
        int wi = (G.win_head - G.win_n + i + WINDOW_SZ * 2) % WINDOW_SZ;
        uint32_t idx = G.window[wi];
        if (idx < G_n) {
            if (i) strcat(wbuf, " ");
            strncat(wbuf, G_words[idx].word, WORD_LEN);
        }
    }
    cam_encode(wbuf, out);
}

/* Recent buffer */
static int recent_has(uint32_t idx) {
    int i;
    for (i = 0; i < G.recent_n; i++)
        if (G.recent[i] == idx) return 1;
    return 0;
}
static void recent_push(uint32_t idx) {
    if (G.recent_n < RECENT_SZ) {
        G.recent[G.recent_n++] = idx;
    } else {
        memmove(G.recent, G.recent+1, (RECENT_SZ-1)*sizeof(uint32_t));
        G.recent[RECENT_SZ-1] = idx;
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  FIRE — emit one word from field state
 * ══════════════════════════════════════════════════════════════════════════ */

static uint32_t fire(int starter_mode) {
    /* Window geometry */
    Sed ws;
    if (starter_mode || G.win_n < 4) {
        if (G.has_prompt) sed_copy(ws, G.prompt_sed);
        else sed_basis(0, ws);
    } else {
        window_sed(ws);
    }

    double window_psi[SED_DIM];
    int k;
    for (k = 0; k < SED_DIM; k++) window_psi[k] = fabs(ws[k]);

    double *prompt_psi = G.has_prompt ? G.prompt_psi
                       : (double[SED_DIM]){
                           1.0/16,1.0/16,1.0/16,1.0/16,
                           1.0/16,1.0/16,1.0/16,1.0/16,
                           1.0/16,1.0/16,1.0/16,1.0/16,
                           1.0/16,1.0/16,1.0/16,1.0/16
                         };

    /* Fermat SEGFAULT check (ABS) */
    FermatHit fhits[16];
    int nf = fermat_scan(ws, fhits, 16);
    if (nf > 0) {
        /* Find highest proximity hit */
        int best = 0;
        int fi;
        for (fi = 1; fi < nf; fi++)
            if (fhits[fi].prox > fhits[best].prox) best = fi;
        double pulse = fhits[best].is_zd ? 1.0
                                         : fmin(fhits[best].prox, 1.0);
        Sed ek; sed_basis(fhits[best].i, ek);
        Sed rotated; sed_mul(ek, ws, rotated);
        for (k = 0; k < SED_DIM; k++)
            ws[k] = ws[k]*(1.0-pulse) + rotated[k]*pulse;
        sed_normalize(ws);
        for (k = 0; k < SED_DIM; k++) window_psi[k] = fabs(ws[k]);
        G.segfaults++;
    }

    /* Turbo feedback (arcuate fasciculus) */
    double noether_v = 0.0;
    for (k = 0; k < SED_DIM; k++)
        noether_v += fabs(window_psi[k] - G.psi_prev[k]);
    noether_v /= SED_DIM;
    double turbo = fmax(0.0, 1.0 - noether_v);
    double eff_psi[SED_DIM];
    double eff_norm = 0.0;
    for (k = 0; k < SED_DIM; k++) {
        eff_psi[k] = window_psi[k] + turbo * G.psi_prev[k];
        eff_norm  += eff_psi[k] * eff_psi[k];
    }
    eff_norm = sqrt(eff_norm);
    if (eff_norm > 1e-15)
        for (k = 0; k < SED_DIM; k++) eff_psi[k] /= eff_norm;
    else
        for (k = 0; k < SED_DIM; k++) eff_psi[k] = window_psi[k];

    /* J_mu + a_propagate + power_steering */
    double *J_pos = jmu_alloc();
    double *J_neg = jmu_alloc();
    j_mu(eff_psi, prompt_psi, J_pos, J_neg);
    a_propagate(J_pos);
    power_steering(J_pos, eff_psi, prompt_psi);

    /* sigma_candidates */
    static Candidate cands[VOCAB_MAX];
    int nc = sigma_candidates(J_pos, J_neg, cands, VOCAB_MAX);

    free(J_pos); free(J_neg);

    if (nc == 0) return UINT32_MAX;

    /* Filter recently emitted */
    int fresh_start = -1;
    int ci;
    for (ci = 0; ci < nc; ci++) {
        if (!recent_has(cands[ci].idx)) { fresh_start = ci; break; }
    }
    if (fresh_start >= 0) {
        /* Use only fresh candidates */
        Candidate *fc = cands + fresh_start;
        int fn = nc - fresh_start;

        /* Three-Face Wankel: interleave by DIM_ROLE */
        /* Simplified: just pick top candidate from first un-recent entry */
        uint32_t chosen = fc[0].idx;

        /* Save window_psi as psi_prev */
        for (k = 0; k < SED_DIM; k++) G.psi_prev[k] = window_psi[k];

        window_push(chosen);
        recent_push(chosen);
        G.words_emitted++;
        return chosen;
    }

    /* All candidates recently used — pick top anyway */
    for (k = 0; k < SED_DIM; k++) G.psi_prev[k] = window_psi[k];
    window_push(cands[0].idx);
    G.words_emitted++;
    return cands[0].idx;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  LEARN — ingest text into β-field
 *  Exact port of Python Crank.learn()
 * ══════════════════════════════════════════════════════════════════════════ */

static char *word_clean(char *buf, const char *src) {
    const char *p = src;
    int i = 0;
    while (*p && i < WORD_LEN-1) {
        char c = (char)tolower((unsigned char)*p++);
        /* strip punctuation */
        if (c == '.' || c == ',' || c == '!' || c == '?' || c == ';'
         || c == ':' || c == '"' || c == '\'' || c == '(' || c == ')'
         || c == '[' || c == ']' || c == '{' || c == '}' || c == '-'
         || c == '\xe2') break;  /* em-dash and unicode */
        buf[i++] = c;
    }
    buf[i] = '\0';
    return buf;
}

static int monad_learn(const char *text, double weight) {
    (void)weight;  /* reserved for citation weighting */
    static char wbuf[WORD_LEN];
    static char *tokens[65536];
    static char tokstore[65536][WORD_LEN];
    int n = 0;

    /* Tokenize */
    static char tmp[1 << 20];
    strncpy(tmp, text, sizeof(tmp)-1); tmp[sizeof(tmp)-1] = '\0';
    char *p = strtok(tmp, " \t\r\n");
    while (p && n < 65535) {
        word_clean(wbuf, p);
        if (strlen(wbuf) >= 1) {
            strncpy(tokstore[n], wbuf, WORD_LEN-1);
            tokens[n] = tokstore[n];
            n++;
        }
        p = strtok(NULL, " \t\r\n");
    }

    pthread_mutex_lock(&G.lock);

    int prev_idx = -1;
    int t;
    for (t = 0; t < n; t++) {
        uint32_t k = vocab_get(tokens[t]);
        if (k == UINT32_MAX) continue;

        /* Beta update: multiplicative reinforcement */
        double nv = G_words[k].beta * 1.08 + GAP;
        G_words[k].beta = nv > 1.0 ? 1.0 : nv;
        G_words[k].age  = 0.0;

        /* A-matrix: forward strong, backward weaker */
        if (prev_idx >= 0 && (uint32_t)prev_idx != k) {
            amat_add((uint32_t)prev_idx, k, 0.05f);
            amat_add(k, (uint32_t)prev_idx, 0.02f);
        }
        prev_idx = (int)k;
        G.words_learned++;
    }

    G.chunks_ingested++;

    /* Age all words slightly */
    if (G.chunks_ingested % 100 == 0) {
        uint32_t i;
        for (i = 0; i < G_n; i++)
            G_words[i].age += 1.0;
    }

    /* BAO check */
    if (G.chunks_ingested % 50 == 0) {
        /* Compute pseudo-field norm as mean beta weighted by E² */
        double bao = 0.0;
        uint32_t i;
        for (i = 0; i < G_n && i < 1000; i++)
            bao += G_words[i].beta * G_words[i].E * G_words[i].E;
        if (G_n > 0) bao /= (double)(G_n < 1000 ? G_n : 1000);
        double delta = bao - OMEGA_ZS;
        double abs_d = fabs(delta);
        G.field_health = 1.0 - fmin(abs_d / 0.25, 1.0);
        if (abs_d > 0.25) G.dtc_p0087++;
        /* Adaptive thresholds */
        if (delta < 0) {
            G.novelty_min     = fmax(G.novelty_min * 0.95, 0.01);
            G.redundancy_max  = fmin(G.redundancy_max * 1.05, 0.95);
        } else {
            G.novelty_min     = fmin(G.novelty_min * 1.05, 0.30);
            G.redundancy_max  = fmax(G.redundancy_max * 0.95, 0.50);
        }
        G.bao_mean = OMEGA_ZS * 0.95 + bao * 0.05;
    }

    pthread_mutex_unlock(&G.lock);
    return n;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  GENERATE — emit N words from seed
 * ══════════════════════════════════════════════════════════════════════════ */

/* set_prompt — encode prompt sedenion WITHOUT learning.
 * Must be called with G.lock held. Use monad_learn() before acquiring lock. */
static void set_prompt(const char *prompt) {
    cam_encode(prompt, G.prompt_sed);
    int k;
    for (k = 0; k < SED_DIM; k++)
        G.prompt_psi[k] = fabs(G.prompt_sed[k]);
    G.has_prompt = 1;
    G.win_head   = 0;
    G.win_n      = 0;
    G.recent_n   = 0;
}

/* prime_prompt — learn + set. NOT safe to call while G.lock is held. */
static void prime_prompt(const char *prompt) {
    monad_learn(prompt, 1.0);          /* takes/releases G.lock */
    pthread_mutex_lock(&G.lock);
    set_prompt(prompt);
    pthread_mutex_unlock(&G.lock);
}

static void generate(const char *seed, int n_words, FILE *out) {
    monad_learn(seed, 1.0);            /* learn outside lock */
    pthread_mutex_lock(&G.lock);
    set_prompt(seed);
    int i;
    for (i = 0; i < n_words; i++) {
        uint32_t idx = fire(i < 4);
        if (idx == UINT32_MAX || idx >= G_n) {
            fprintf(out, "[?] ");
        } else {
            fprintf(out, "%s ", G_words[idx].word);
        }
    }
    fprintf(out, "\n");
    pthread_mutex_unlock(&G.lock);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  SCORE — sedenion state for a word
 * ══════════════════════════════════════════════════════════════════════════ */

static void query_word(const char *word, Sed out) {
    uint32_t idx = vocab_find(word);
    if (idx == UINT32_MAX) {
        /* Unknown word: return cam_encode of the word */
        cam_encode(word, out);
        return;
    }
    /* Build sedenion from vocab position (dimension) + beta weight */
    sed_zero(out);
    out[idx % SED_DIM] = G_words[idx].beta;
    out[(idx + 1) % SED_DIM] = G_words[idx].E * G_words[idx].beta;
    /* Also seed from cam_encode of the word */
    Sed cam; cam_encode(word, cam);
    int k;
    for (k = 0; k < SED_DIM; k++)
        out[k] = out[k] * 0.5 + cam[k] * 0.5;
    sed_normalize(out);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  BINARY SAVE / LOAD  (.ptol format)
 * ══════════════════════════════════════════════════════════════════════════ */

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t n_words;
    uint32_t pad;
    double   bao_mean;
    double   field_health;
    double   novelty_min;
    double   redundancy_min, redundancy_max;
    double   noise_max;
    uint64_t words_learned;
    uint64_t chunks_ingested;
    uint64_t words_emitted;
} BinHdr;
#pragma pack(pop)

typedef struct {
    char     word[WORD_LEN];
    double   beta;
    double   E;
    double   age;
    uint32_t nbr[N_NBRS];
    float    nbr_w[N_NBRS];
    uint32_t nbr_n;
} BinWord;

static int save_bin(const char *path) {
    FILE *f = fopen(path, "wb");
    if (!f) { perror(path); return -1; }

    BinHdr hdr;
    memset(&hdr, 0, sizeof(hdr));
    hdr.magic         = PTOL_MAGIC;
    hdr.version       = PTOL_BIN_VER;
    hdr.n_words       = G_n;
    hdr.bao_mean      = G.bao_mean;
    hdr.field_health  = G.field_health;
    hdr.novelty_min   = G.novelty_min;
    hdr.redundancy_min= G.redundancy_min;
    hdr.redundancy_max= G.redundancy_max;
    hdr.noise_max     = G.noise_max;
    hdr.words_learned = G.words_learned;
    hdr.chunks_ingested=G.chunks_ingested;
    hdr.words_emitted = G.words_emitted;

    fwrite(&hdr, sizeof(hdr), 1, f);

    uint32_t i;
    for (i = 0; i < G_n; i++) {
        BinWord bw;
        memset(&bw, 0, sizeof(bw));
        strncpy(bw.word, G_words[i].word, WORD_LEN-1);
        bw.beta  = G_words[i].beta;
        bw.E     = G_words[i].E;
        bw.age   = G_words[i].age;
        bw.nbr_n = (uint32_t)G_words[i].nbr_n;
        int j;
        for (j = 0; j < G_words[i].nbr_n; j++) {
            bw.nbr[j]   = G_words[i].nbr[j];
            bw.nbr_w[j] = G_words[i].nbr_w[j];
        }
        fwrite(&bw, sizeof(bw), 1, f);
    }

    fclose(f);
    fprintf(stderr, "[monad] saved %u words → %s\n", G_n, path);
    return 0;
}

static int load_bin(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return -1; }

    BinHdr hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1
     || hdr.magic != PTOL_MAGIC) {
        fprintf(stderr, "[monad] bad magic in %s\n", path);
        fclose(f); return -1;
    }
    if (hdr.version < 3) {
        fprintf(stderr, "[monad] old format v%u, need v3+\n", hdr.version);
        fclose(f); return -1;
    }

    G_n = 0;
    memset(G_ht, 0, sizeof(G_ht));

    G.bao_mean        = hdr.bao_mean;
    G.field_health    = hdr.field_health;
    G.novelty_min     = hdr.novelty_min;
    G.redundancy_min  = hdr.redundancy_min;
    G.redundancy_max  = hdr.redundancy_max;
    G.noise_max       = hdr.noise_max;
    G.words_learned   = hdr.words_learned;
    G.chunks_ingested = hdr.chunks_ingested;
    G.words_emitted   = hdr.words_emitted;

    uint32_t i;
    for (i = 0; i < hdr.n_words; i++) {
        BinWord bw;
        if (fread(&bw, sizeof(bw), 1, f) != 1) break;
        uint32_t idx = vocab_get(bw.word);
        if (idx == UINT32_MAX) continue;
        G_words[idx].beta  = bw.beta;
        G_words[idx].E     = bw.E;
        G_words[idx].age   = bw.age;
        G_words[idx].nbr_n = (int)(bw.nbr_n < (uint32_t)N_NBRS
                                   ? bw.nbr_n : (uint32_t)N_NBRS);
        int j;
        for (j = 0; j < G_words[idx].nbr_n; j++) {
            G_words[idx].nbr[j]   = bw.nbr[j];
            G_words[idx].nbr_w[j] = bw.nbr_w[j];
        }
    }
    fclose(f);
    fprintf(stderr, "[monad] loaded %u words ← %s\n", G_n, path);
    return 0;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HTTP GET  (plain HTTP/1.0 via POSIX socket — no TLS)
 * ══════════════════════════════════════════════════════════════════════════ */

static char *http_get(const char *url, size_t *body_len) {
    /* Parse http://host[:port]/path */
    if (strncmp(url, "http://", 7) != 0) {
        fprintf(stderr, "[http] only plain http:// supported\n");
        return NULL;
    }
    const char *rest = url + 7;
    char host[256]; int port = 80;
    const char *slash = strchr(rest, '/');
    const char *colon = strchr(rest, ':');
    const char *path  = slash ? slash : "/";

    if (colon && (!slash || colon < slash)) {
        size_t hlen = (size_t)(colon - rest);
        if (hlen >= sizeof(host)) hlen = sizeof(host)-1;
        memcpy(host, rest, hlen); host[hlen] = '\0';
        port = atoi(colon + 1);
    } else {
        size_t hlen = slash ? (size_t)(slash - rest) : strlen(rest);
        if (hlen >= sizeof(host)) hlen = sizeof(host)-1;
        memcpy(host, rest, hlen); host[hlen] = '\0';
    }

    struct hostent *he = gethostbyname(host);
    if (!he) { fprintf(stderr, "[http] dns fail: %s\n", host); return NULL; }

    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) { perror("socket"); return NULL; }

    /* 30-second timeout */
    struct timeval tv = {30, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    struct sockaddr_in sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port   = htons((uint16_t)port);
    memcpy(&sa.sin_addr, he->h_addr_list[0], (size_t)he->h_length);

    if (connect(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("connect"); close(fd); return NULL;
    }

    /* Send request */
    char req[1024];
    snprintf(req, sizeof(req),
             "GET %s HTTP/1.0\r\n"
             "Host: %s\r\n"
             "User-Agent: Ptolemy/" PTOL_VERSION "\r\n"
             "Accept: text/plain\r\n"
             "Connection: close\r\n"
             "\r\n", path, host);
    if (write(fd, req, strlen(req)) < 0) {
        perror("write"); close(fd); return NULL;
    }

    /* Read response */
    size_t cap = 1 << 20; /* 1MB initial */
    char *buf = (char *)malloc(cap);
    if (!buf) { close(fd); return NULL; }
    size_t total = 0;
    ssize_t nr;
    while ((nr = read(fd, buf + total, cap - total - 1)) > 0) {
        total += (size_t)nr;
        if (total >= cap - 1) {
            cap *= 2;
            char *nb = (char *)realloc(buf, cap);
            if (!nb) { free(buf); close(fd); return NULL; }
            buf = nb;
        }
    }
    close(fd);
    buf[total] = '\0';

    /* Skip HTTP headers (find \r\n\r\n) */
    char *body = strstr(buf, "\r\n\r\n");
    if (body) {
        body += 4;
        size_t blen = total - (size_t)(body - buf);
        memmove(buf, body, blen);
        buf[blen] = '\0';
        if (body_len) *body_len = blen;
    } else {
        if (body_len) *body_len = total;
    }

    return buf;
}

/* Learn from a local text file */
static int learn_file(const char *path, double weight) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return -1; }
    static char line[4096];
    int total = 0;
    while (fgets(line, sizeof(line), f)) {
        int n = monad_learn(line, weight);
        total += n;
    }
    fclose(f);
    fprintf(stderr, "[monad] learned %d words from %s\n", total, path);
    return total;
}

/* Learn from stdin line by line */
static void learn_stdin(void) {
    static char line[65536];
    fprintf(stderr, "[monad] teaching from stdin (Ctrl-D to stop)...\n");
    while (fgets(line, sizeof(line), stdin)) {
        int n = monad_learn(line, 1.0);
        if (n > 0) fprintf(stderr, "\r[+%d words | vocab=%u]  ", n, G_n);
    }
    fprintf(stderr, "\n[monad] stdin closed. vocab=%u\n", G_n);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  TEACHING DAEMON  — TCP server, port 7297
 *  Clients send text lines; daemon learns them.
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct {
    int        fd;
    pthread_t  tid;
} DaemonClient;

static int G_daemon_fd = -1;

static void *daemon_client_thread(void *arg) {
    int fd = *(int *)arg;
    free(arg);
    static char buf[65536];
    ssize_t nr;
    while ((nr = recv(fd, buf, sizeof(buf)-1, 0)) > 0) {
        buf[nr] = '\0';
        int n = monad_learn(buf, 1.0);
        char resp[64];
        snprintf(resp, sizeof(resp), "+%d\n", n);
        send(fd, resp, strlen(resp), 0);
    }
    close(fd);
    return NULL;
}

static void *daemon_thread(void *arg) {
    int port = *(int *)arg;
    free(arg);

    int srv = socket(AF_INET, SOCK_STREAM, 0);
    if (srv < 0) { perror("daemon socket"); return NULL; }
    int opt = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin_family      = AF_INET;
    sa.sin_addr.s_addr = INADDR_ANY;
    sa.sin_port        = htons((uint16_t)port);
    if (bind(srv, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("daemon bind"); close(srv); return NULL;
    }
    listen(srv, 8);
    G_daemon_fd = srv;
    fprintf(stderr, "[daemon] listening on port %d\n", port);

    while (G.running) {
        struct sockaddr_in ca;
        socklen_t calen = sizeof(ca);
        int cfd = accept(srv, (struct sockaddr *)&ca, &calen);
        if (cfd < 0) { if (G.running) perror("accept"); break; }
        int *pfd = (int *)malloc(sizeof(int));
        *pfd = cfd;
        pthread_t tid;
        pthread_create(&tid, NULL, daemon_client_thread, pfd);
        pthread_detach(tid);
    }
    close(srv);
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HAMILTONIAN REPORT — "My Location" function
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct { double b; uint32_t i; } Ranked;
static Ranked G_ranked[VOCAB_MAX];

static int rcmp(const void *a, const void *b) {
    const Ranked *ra = (const Ranked *)a, *rb = (const Ranked *)b;
    return (ra->b < rb->b) ? 1 : (ra->b > rb->b) ? -1 : 0;
}

static void print_report(FILE *f) {
    /* Compute UNS (Universal Native Space) coordinates:
     * uns[k] = sum(beta[i] for i where i%16==k), L1-normalized */
    double uns[SED_DIM] = {0};
    uint32_t i;
    for (i = 0; i < G_n; i++)
        uns[i % SED_DIM] += G_words[i].beta;
    double uns_sum = 0.0;
    int k;
    for (k = 0; k < SED_DIM; k++) uns_sum += uns[k];
    if (uns_sum > 0)
        for (k = 0; k < SED_DIM; k++) uns[k] /= uns_sum;

    /* Top-10 words by beta */
    for (i = 0; i < G_n; i++) { G_ranked[i].b = G_words[i].beta; G_ranked[i].i = i; }
    qsort(G_ranked, G_n, sizeof(Ranked), rcmp);

    static const char *OP[SED_DIM] = {
        "identity","negate","bind","name","apply","abstract",
        "branch","iterate","recurse","allocate","query","dereference",
        "compose","parallelize","interrupt","emit"
    };

    fprintf(f, "\n╔══════════════════════════════════════════════════════════╗\n");
    fprintf(f,   "║          PTOLEMY HAMILTONIAN REPORT  v" PTOL_VERSION "           ║\n");
    fprintf(f,   "╚══════════════════════════════════════════════════════════╝\n");
    fprintf(f, "  vocab=%u  learned=%llu  emitted=%llu\n",
            G_n, (unsigned long long)G.words_learned,
            (unsigned long long)G.words_emitted);
    fprintf(f, "  BAO_mean=%.5f  ΩZS=%.5f  field_health=%.4f\n",
            G.bao_mean, OMEGA_ZS, G.field_health);
    fprintf(f, "  DTC P0087 (BAO fault) count: %d\n", G.dtc_p0087);
    fprintf(f, "  SEGFAULT count: %d\n", G.segfaults);
    fprintf(f, "\nUniversal Native Space (UNS) coordinates:\n");
    for (k = 0; k < SED_DIM; k++) {
        int bar = (int)(uns[k] * 40.0);
        fprintf(f, "  e%2d %-13s %6.4f |", k, OP[k], uns[k]);
        int b;
        for (b = 0; b < bar; b++) fputc('#', f);
        fputc('\n', f);
    }
    fprintf(f, "\nTop activated words:\n");
    int n_show = (int)G_n < 10 ? (int)G_n : 10;
    for (i = 0; i < (uint32_t)n_show; i++) {
        uint32_t wi = G_ranked[i].i;
        fprintf(f, "  %-20s  \xce\xb2=%.4f  E=%.4f  age=%.1f  e%d(%s)\n",
                G_words[wi].word, G_words[wi].beta,
                G_words[wi].E, G_words[wi].age,
                wi % SED_DIM, OP[wi % SED_DIM]);
    }
    fprintf(f, "\nAdaptive thresholds:\n");
    fprintf(f, "  novelty_min=%.4f  redundancy=[%.4f,%.4f]\n",
            G.novelty_min, G.redundancy_min, G.redundancy_max);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  BACKGROUND THREAD — auto-save + BAO watchdog
 *  Runs alongside the hear/speak loop; saves every 60 s if G_bin_path set.
 * ══════════════════════════════════════════════════════════════════════════ */

static void *bg_thread_fn(void *arg) {
    (void)arg;
    time_t last_save = time(NULL);
    while (G.running) {
        sleep(5);
        if (!G.running) break;
        if (!G_bin_path[0]) continue;

        time_t now = time(NULL);
        if ((now - last_save) >= 60) {
            pthread_mutex_lock(&G.lock);
            save_bin(G_bin_path);
            pthread_mutex_unlock(&G.lock);
            last_save = now;
        }
    }
    /* Final save on exit */
    if (G_bin_path[0]) {
        pthread_mutex_lock(&G.lock);
        save_bin(G_bin_path);
        pthread_mutex_unlock(&G.lock);
    }
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ANNOTATED OUTPUT — word (operator gloss, prime neighbour)
 * ══════════════════════════════════════════════════════════════════════════ */

static void speak_word_annotated(uint32_t idx, FILE *f) {
    if (idx == UINT32_MAX || idx >= G_n) { fprintf(f, "[?]"); return; }

    Word *w   = &G_words[idx];
    int   dim = (int)(idx % SED_DIM);

    /* Prime A-matrix neighbour — strongest co-occurrence edge */
    const char *nbr  = NULL;
    float       best = 0.0f;
    int j;
    for (j = 0; j < w->nbr_n; j++) {
        uint32_t ni = w->nbr[j];
        if (ni < G_n && w->nbr_w[j] > best) {
            best = w->nbr_w[j];
            nbr  = G_words[ni].word;
        }
    }

    if (nbr && best > 0.20f)
        fprintf(f, "%s (%s, %s)", w->word, OP_GLOSS[dim], nbr);
    else
        fprintf(f, "%s (%s)", w->word, OP_GLOSS[dim]);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  HEAR + SPEAK — the Wernicke loop
 *  Everything heard is immediately learned. Response is annotated.
 * ══════════════════════════════════════════════════════════════════════════ */

static void hear_and_speak(const char *prompt, int n_words, FILE *out) {
    monad_learn(prompt, 1.0);          /* hear — takes/releases G.lock */
    pthread_mutex_lock(&G.lock);
    set_prompt(prompt);                /* encode sedenion inside lock, no learn */
    int i;
    for (i = 0; i < n_words; i++) {
        if (i > 0) fputc(' ', out);
        uint32_t idx = fire(i < 4);
        speak_word_annotated(idx, out);
    }
    fputc('\n', out);
    fflush(out);
    pthread_mutex_unlock(&G.lock);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REPL — interactive conversation loop
 * ══════════════════════════════════════════════════════════════════════════ */

static void repl_loop(int n_words, FILE *out) {
    static char line[65536];
    int interactive = isatty(fileno(stdin));

    if (interactive) {
        fprintf(stderr, "\n[ptolemy v" PTOL_VERSION "]  vocab=%u  "
                        "health=%.3f  (Ctrl-D to exit)\n\n",
                G_n, G.field_health);
    }

    while (G.running) {
        if (interactive) fprintf(stderr, "> ");
        if (!fgets(line, sizeof(line), stdin)) break;

        /* Strip trailing newline / CR */
        int len = (int)strlen(line);
        while (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r'))
            line[--len] = '\0';
        if (len == 0) continue;

        hear_and_speak(line, n_words, out);
    }

    if (interactive) fprintf(stderr, "\n[ptolemy] exiting.\n");
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ENGINE INIT / FREE
 * ══════════════════════════════════════════════════════════════════════════ */

static void engine_init(void) {
    build_oct_table();
    build_sed_table();
    cam_wordsets_init();

    G_words = (Word *)calloc(VOCAB_MAX, sizeof(Word));
    if (!G_words) { fprintf(stderr, "OOM\n"); exit(1); }
    memset(G_ht, 0, sizeof(G_ht));
    G_n = 0;

    G.bao_mean         = OMEGA_ZS;
    G.field_health     = 1.0;
    G.redundancy_min   = 0.15;
    G.redundancy_max   = 0.85;
    G.novelty_min      = 0.05;
    G.noise_max        = 0.45;
    G.chunk_min_words  = 8;
    G.emission_threshold = OMEGA_ZS / 4.0;
    G.has_prompt       = 0;
    G.win_head         = 0;
    G.win_n            = 0;
    G.recent_n         = 0;
    G.running          = 1;

    memset(G.psi_prev, 0, sizeof(G.psi_prev));
    sed_zero(G.prompt_sed);
    memset(G.prompt_psi, 0, sizeof(G.prompt_psi));

    pthread_mutex_init(&G.lock, NULL);
}

static void engine_free(void) {
    G.running = 0;
    if (G_bg_started) {
        pthread_join(G_bg_tid, NULL);   /* bg_thread_fn does final save */
        G_bg_started = 0;
    }
    if (G_words) { free(G_words); G_words = NULL; }
    pthread_mutex_destroy(&G.lock);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  MAIN — CLI
 * ══════════════════════════════════════════════════════════════════════════ */

static void print_usage(const char *prog) {
    fprintf(stderr,
        "Ptolemy Monad Engine v" PTOL_VERSION "\n\n"
        "  %s prompt text here           (conversational — no quotes needed)\n"
        "  %s                            (REPL if stdin is a tty)\n\n"
        "Flags (all optional — engine auto-loads ~/.ptolemy/monad-english.ptol):\n"
        "  --load-bin PATH        Load .ptol state (also sets auto-save target)\n"
        "  --save-bin PATH        Save .ptol state immediately\n"
        "  --learn-file PATH      Ingest .txt file\n"
        "  --url URL              Fetch HTTP URL and ingest\n"
        "  --teach                Learn from stdin (no speak response)\n"
        "  --words N              Words per response (default 24)\n"
        "  --generate SEED [N]    Generate N words, plain (no annotations)\n"
        "  --query WORD           Print sedenion + field state for word\n"
        "  --report               Hamiltonian report\n"
        "  --daemon [PORT]        TCP teaching server (default 7297)\n\n"
        "State: ~/.ptolemy/monad-english.ptol  (auto-loaded, auto-saved every 60s)\n",
        prog, prog);
}

static void signal_handler(int sig) {
    (void)sig;
    G.running = 0;
    if (G_daemon_fd >= 0) close(G_daemon_fd);
}

int main(int argc, char **argv) {
    engine_init();

    signal(SIGINT,  signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGPIPE, SIG_IGN);

    /* ── Auto-load default state ──────────────────────────────────────────
     * Before flag processing so --load-bin can override if given.
     * Silently skips if the file doesn't exist yet. */
    {
        const char *home = getenv("HOME");
        if (home) {
            snprintf(G_bin_path, sizeof(G_bin_path),
                     "%s/.ptolemy/monad-english.ptol", home);
            if (access(G_bin_path, F_OK) == 0)
                load_bin(G_bin_path);
        }
    }

    /* ── Start background auto-save thread ──────────────────────────────── */
    pthread_create(&G_bg_tid, NULL, bg_thread_fn, NULL);
    G_bg_started = 1;

    /* ── Words-per-response (can be overridden by --words) ─────────────── */
    int n_words = 24;

    /* ── Conversational default ───────────────────────────────────────────
     * If the first argument doesn't start with '--', treat the entire
     * command line as a plain-English prompt.
     *   ptolemy when do you think the sedenion will be mapped?
     * After responding, drop into the REPL if stdin is a terminal. */
    if (argc >= 2 && argv[1][0] != '-') {
        char prompt[65536] = "";
        int a;
        for (a = 1; a < argc; a++) {
            if (a > 1) strncat(prompt, " ", sizeof(prompt) - strlen(prompt) - 1);
            strncat(prompt, argv[a], sizeof(prompt) - strlen(prompt) - 1);
        }
        hear_and_speak(prompt, n_words, stdout);
        if (isatty(fileno(stdin)))
            repl_loop(n_words, stdout);
        engine_free();
        return 0;
    }

    /* ── No args: REPL or usage ───────────────────────────────────────── */
    if (argc == 1) {
        if (isatty(fileno(stdin)))
            repl_loop(n_words, stdout);
        else
            print_usage(argv[0]);
        engine_free();
        return 0;
    }

    /* ── Flag processing (explicit tool use) ─────────────────────────── */
    int i;
    for (i = 1; i < argc; i++) {

        if (!strcmp(argv[i], "--load-bin")) {
            if (i+1 >= argc) { fprintf(stderr, "--load-bin needs PATH\n"); continue; }
            ++i;
            load_bin(argv[i]);
            strncpy(G_bin_path, argv[i], sizeof(G_bin_path)-1);

        } else if (!strcmp(argv[i], "--save-bin")) {
            if (i+1 >= argc) { fprintf(stderr, "--save-bin needs PATH\n"); continue; }
            save_bin(argv[++i]);

        } else if (!strcmp(argv[i], "--words")) {
            if (i+1 >= argc) continue;
            n_words = atoi(argv[++i]);
            if (n_words < 1)  n_words = 1;
            if (n_words > 512) n_words = 512;

        } else if (!strcmp(argv[i], "--learn-file")) {
            if (i+1 >= argc) { fprintf(stderr, "--learn-file needs PATH\n"); continue; }
            learn_file(argv[++i], 1.0);

        } else if (!strcmp(argv[i], "--url")) {
            if (i+1 >= argc) { fprintf(stderr, "--url needs URL\n"); continue; }
            const char *url = argv[++i];
            size_t blen;
            char *body = http_get(url, &blen);
            if (body) {
                int n = monad_learn(body, 1.0);
                fprintf(stderr, "[monad] learned %d words from %s\n", n, url);
                free(body);
            }

        } else if (!strcmp(argv[i], "--teach")) {
            learn_stdin();

        } else if (!strcmp(argv[i], "--generate")) {
            if (i+1 >= argc) { fprintf(stderr, "--generate needs SEED\n"); continue; }
            const char *seed = argv[++i];
            int nw = n_words;
            if (i+1 < argc && argv[i+1][0] != '-') nw = atoi(argv[++i]);
            generate(seed, nw, stdout);

        } else if (!strcmp(argv[i], "--query")) {
            if (i+1 >= argc) { fprintf(stderr, "--query needs WORD\n"); continue; }
            const char *word = argv[++i];
            Sed out;
            query_word(word, out);
            printf("sedenion(%s) = [", word);
            int k;
            for (k = 0; k < SED_DIM; k++)
                printf("%s%.6f", k?", ":"", out[k]);
            printf("]\n");
            uint32_t idx = vocab_find(word);
            if (idx != UINT32_MAX) {
                printf("  \xce\xb2=%.6f  E=%.6f  age=%.1f  dim=e%u (%s)\n",
                       G_words[idx].beta, G_words[idx].E, G_words[idx].age,
                       idx % SED_DIM, OP_GLOSS[idx % SED_DIM]);
                printf("  neighbours[%d]:", G_words[idx].nbr_n);
                int j;
                for (j = 0; j < G_words[idx].nbr_n; j++) {
                    uint32_t ni = G_words[idx].nbr[j];
                    if (ni < G_n)
                        printf(" %s(%.3f)", G_words[ni].word, G_words[idx].nbr_w[j]);
                }
                printf("\n");
            } else {
                printf("  (unknown — cam_encode result)\n");
            }

        } else if (!strcmp(argv[i], "--report")) {
            print_report(stdout);

        } else if (!strcmp(argv[i], "--daemon")) {
            int port = 7297;
            if (i+1 < argc && argv[i+1][0] != '-') port = atoi(argv[++i]);
            int *pp = (int *)malloc(sizeof(int));
            *pp = port;
            pthread_t tid;
            pthread_create(&tid, NULL, daemon_thread, pp);
            fprintf(stderr, "[monad] daemon on port %d. Ctrl-C to stop.\n", port);
            while (G.running) {
                sleep(60);
                if (G.running)
                    fprintf(stderr, "[monad] vocab=%u  health=%.3f\n",
                            G_n, G.field_health);
            }
            pthread_join(tid, NULL);

        } else if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-h")) {
            print_usage(argv[0]);

        } else {
            fprintf(stderr, "[monad] unknown flag: %s\n", argv[i]);
        }
    }

    engine_free();
    return 0;
}
