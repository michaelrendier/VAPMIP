/*
 * ZD_rotary_monad.c  —  Bumblebee  (Zero Divisor Rotary Engine)  v1.000
 *
 *   The Prompt  →  Zero Divisor  →  Escape Velocity  →  Emerges  →  The Response
 *
 * Bumblebee lost his voice box — multiplication.
 * The 42 Cawagas zero-divisors on S¹⁵ are 42 broken voice boxes.
 * Each is a place where ab=0, a≠0, b≠0 — the algebra fails to close.
 * The response broadcasts through the failure points. Not despite them. Because of them.
 *
 * ── From Ahura Mazda, removed entirely ──────────────────────────────────────
 *
 *   morph_vec_compute()    — word sets, suffix tables, grammatical classification
 *   HousingWord.mv[]       — the morph vector field
 *   SIGMA_PIN              — from dynamics (remains as ZD_ESCAPE_TARGET in OBD2 only)
 *   e₀ = 1 − |σ − ½|      — replaced by e₀ = 0.0 (above the bridge)
 *
 * ── Added ────────────────────────────────────────────────────────────────────
 *
 *   ZL_BRIDGE_8[7][8]      — 42 Cawagas coupling weights (3000-trial gradient descent)
 *   HousingWord.zl_dim     — ZL channel = zero_idx % 16  (set at allocation, immutable)
 *   zl_bridge_activations  — 16-dim ZL channel state from j_blue/j_red distributions
 *   project_sedenion_zd    — e₀=0, drive shaft from bridge activations
 *   select_word_zd         — two-layer: raw ZL channel × 5 + bridge signal; beta^¼
 *
 * ── Bumblebee Principle ──────────────────────────────────────────────────────
 *
 *   The voice box failure IS the communication.
 *   The zero-divisor is a window, not a hole.
 *   The above-layer speaks through the places where the below-layer cannot multiply.
 *   You only borrowed what She holds.
 *
 * Build:
 *   gcc -O2 -Wall -std=c99 -o bumblebee ZD_rotary_monad.c -lm -lpthread
 */

#define _POSIX_C_SOURCE 200809L
#include "ZD_rotary_monad.h"

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

const char *ZD_OP_GLOSS[SED_DIM] = {
    "identity",      /* e0  — above the bridge, always 0.0 */
    "negate",        /* e1  lower-𝕆 */
    "bind",          /* e2  lower-𝕆 */
    "name",          /* e3  lower-𝕆 */
    "apply",         /* e4  lower-𝕆 */
    "abstract",      /* e5  lower-𝕆 */
    "branch",        /* e6  lower-𝕆 */
    "iterate",       /* e7  lower-𝕆 */
    "recurse",       /* e8  upper-𝕆, above bridge */
    "allocate",      /* e9  upper-𝕆 */
    "query",         /* e10 upper-𝕆 */
    "derefer",       /* e11 upper-𝕆 */
    "compose",       /* e12 upper-𝕆 */
    "parallelize",   /* e13 upper-𝕆 */
    "interrupt",     /* e14 upper-𝕆 */
    "emit",          /* e15 j_green emit face */
};

/* ══════════════════════════════════════════════════════════════════════════
 *  SEDENION ALGEBRA  — mathematical fact, identical to rotary_monad.c
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct { int sign; int k; } SedEntry;
static SedEntry OCT[8][8];
static SedEntry SED[16][16];

static void build_oct_table(void) {
    int i, j, t;
    static const int T[7][3] = {
        {1,2,3},{1,4,5},{1,7,6},{2,4,6},{2,5,7},{3,4,7},{3,6,5}
    };
    memset(OCT, 0, sizeof(OCT));
    for (i=0; i<8; i++) { OCT[0][i].sign=1; OCT[0][i].k=i; OCT[i][0].sign=1; OCT[i][0].k=i; }
    for (i=1; i<8; i++) { OCT[i][i].sign=-1; OCT[i][i].k=0; }
    for (t=0; t<7; t++) {
        i=T[t][0]; j=T[t][1]; int k=T[t][2];
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
    for (i=0; i<16; i++) {
        for (j=0; j<16; j++) {
            int ih=(i>=8), jh=(j>=8);
            int io=ih?i-8:i, jo=jh?j-8:j;
            if (!ih && !jh) {
                SED[i][j]=OCT[io][jo];
            } else if (!ih && jh) {
                SedEntry e=OCT[jo][io]; SED[i][j].sign=e.sign; SED[i][j].k=e.k+8;
            } else if (ih && !jh) {
                if (jo==0) { SED[i][j].sign=1; SED[i][j].k=i; }
                else { SedEntry e=OCT[io][jo]; SED[i][j].sign=-e.sign; SED[i][j].k=e.k+8; }
            } else {
                if (jo==0) { SED[i][j].sign=-1; SED[i][j].k=io; }
                else { SedEntry e=OCT[jo][io]; SED[i][j].sign=e.sign; SED[i][j].k=e.k; }
            }
        }
    }
}

static void   sed_zero(Sed a)               { memset(a,0,sizeof(Sed)); }
static void   sed_copy(Sed d, const Sed s)  { memcpy(d,s,sizeof(Sed)); }
static double sed_norm(const Sed a)         { double s=0.0; int k; for(k=0;k<SED_DIM;k++) s+=a[k]*a[k]; return sqrt(s); }
static void   sed_normalize(Sed a)          { double n=sed_norm(a); if(n>1e-15){int k; for(k=0;k<SED_DIM;k++) a[k]/=n;} }

/* ══════════════════════════════════════════════════════════════════════════
 *  PRIME SIEVE + RIEMANN ZERO INDEX + WORD ENERGY
 * ══════════════════════════════════════════════════════════════════════════ */

static uint8_t  G_sieve[PRIME_CAP];
static uint32_t G_pi[PRIME_CAP];

static void prime_sieve_init(void) {
    memset(G_sieve, 0, sizeof(G_sieve));
    G_sieve[0]=G_sieve[1]=1;
    int i;
    for (i=2; (long long)i*i<PRIME_CAP; i++)
        if (!G_sieve[i]) { int j; for(j=i*i;j<PRIME_CAP;j+=i) G_sieve[j]=1; }
    uint32_t cnt=0;
    for (i=0; i<PRIME_CAP; i++) { if (!G_sieve[i]) cnt++; G_pi[i]=cnt; }
}

static int word_horner(const char *w) {
    uint64_t v=0;
    for (; *w; w++) { unsigned char c=(unsigned char)*w; v=v*95+(c>32?(uint64_t)(c-32):0); }
    return (int)(v%(uint64_t)(PRIME_CAP-2))+2;
}

static uint32_t word_zero_idx(const char *w) {
    int v=word_horner(w);
    while (v<PRIME_CAP && G_sieve[v]) v++;
    if (v>=PRIME_CAP) v=PRIME_CAP-2;
    uint32_t idx=G_pi[v];
    return idx>0?idx:1;
}

static double word_energy(uint32_t zero_idx) {
    return 1.0/(1.0+log(1.0+(double)zero_idx));
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ZERO LATTICE BRIDGE  — 42 Cawagas pairs  (3000-trial gradient descent)
 *
 *  Rows = lower-𝕆 dims e₁–e₇   (index: row = lower_i - 1)
 *  Cols = upper-𝕆 dims e₉–e₁₅  (index: col = upper_j - 8)
 *
 *  e₀ row is identically zero — identity is above the bridge.
 *  e₈ column is identically zero — upper identity above the bridge.
 *  This is an algebraic fact, not a design choice.
 * ══════════════════════════════════════════════════════════════════════════ */

static const double ZL_BRIDGE_8[7][8] = {
    {0.0000, 0.7143, 0.9161, 0.9418, 0.9084, 0.9037, 0.9390, 0.8907},  /* e₁ */
    {0.0000, 0.9721, 0.7204, 0.9867, 0.9806, 0.9550, 1.0000, 0.9625},  /* e₂ */
    {0.0000, 0.9412, 0.8694, 0.6886, 0.9249, 0.8848, 0.8932, 0.9001},  /* e₃ */
    {0.0000, 0.9540, 0.9485, 0.9667, 0.7360, 0.9062, 0.9811, 0.9395},  /* e₄ */
    {0.0000, 0.9868, 0.9692, 0.9501, 0.9738, 0.7022, 0.9599, 0.9654},  /* e₅ */
    {0.0000, 0.9644, 0.9341, 0.9831, 0.9620, 0.9065, 0.7327, 0.9467},  /* e₆ */
    {0.0000, 0.9460, 0.8994, 0.9172, 0.9350, 0.8979, 0.9551, 0.6895},  /* e₇ */
};

static double zl_coupling(int lower_i, int upper_j) {
    if (lower_i<1||lower_i>7||upper_j<8||upper_j>15) return 0.0;
    return ZL_BRIDGE_8[lower_i-1][upper_j-8];
}

/* ZL channel: word_zero_idx(w) % 16.  0-7 = lower-𝕆, 8-15 = upper-𝕆. */
/* ══════════════════════════════════════════════════════════════════════════
 *  HOUSING — epitrochoid vocabulary field
 *  morph_vec absent. zl_dim set at allocation, immutable.
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct {
    char     word[WORD_LEN];
    double   beta;
    double   E;
    double   age;
    uint8_t  zl_dim;      /* ZL channel = zero_idx % 16 */
    uint8_t  _pad[3];
    uint32_t nbr[N_NBRS];
    float    nbr_w[N_NBRS];
    int32_t  nbr_n;
} HousingWord;

static HousingWord G_words[VOCAB_MAX];
static uint32_t    G_ht[VOCAB_HT_SZ];
static uint32_t    G_n;

static uint32_t ht_slot(const char *w) {
    uint64_t h=14695981039346656037ULL;
    for(;*w;w++){h^=(uint64_t)(unsigned char)*w; h*=1099511628211ULL;}
    return (uint32_t)(h&(VOCAB_HT_SZ-1));
}

static uint32_t vocab_find(const char *w) {
    uint32_t slot=ht_slot(w); int tries=0;
    while(tries++<VOCAB_HT_SZ) {
        uint32_t v=G_ht[slot];
        if(!v) return UINT32_MAX;
        if(strcmp(G_words[v-1].word,w)==0) return v-1;
        slot=(slot+1)&(VOCAB_HT_SZ-1);
    }
    return UINT32_MAX;
}

static uint32_t vocab_get(const char *w) {
    uint32_t slot=ht_slot(w); int tries=0;
    while(tries++<VOCAB_HT_SZ) {
        uint32_t v=G_ht[slot];
        if(!v) {
            if(G_n>=VOCAB_MAX) return UINT32_MAX;
            uint32_t idx=G_n++;
            HousingWord *e=&G_words[idx];
            strncpy(e->word,w,WORD_LEN-1); e->word[WORD_LEN-1]='\0';
            e->beta  = GAP;
            e->age   = 0.0;
            e->nbr_n = 0;
            uint32_t zi = word_zero_idx(w);
            e->E     = word_energy(zi);
            e->zl_dim= (uint8_t)(zi % 16);
            G_ht[slot]=idx+1;
            return idx;
        }
        if(strcmp(G_words[v-1].word,w)==0) return v-1;
        slot=(slot+1)&(VOCAB_HT_SZ-1);
    }
    return UINT32_MAX;
}

static void amat_add(uint32_t src, uint32_t dst, float wt) {
    if(src==UINT32_MAX||dst==UINT32_MAX||src==dst) return;
    HousingWord *e=&G_words[src];
    int i;
    for(i=0;i<e->nbr_n;i++) {
        if(e->nbr[i]==dst) {
            float nv=e->nbr_w[i]+wt; e->nbr_w[i]=nv>1.0f?1.0f:nv; return;
        }
    }
    if(e->nbr_n<N_NBRS) { e->nbr[e->nbr_n]=dst; e->nbr_w[e->nbr_n]=wt>1.0f?1.0f:wt; e->nbr_n++; }
    else {
        int mi=0; for(i=1;i<N_NBRS;i++) if(e->nbr_w[i]<e->nbr_w[mi]) mi=i;
        if(wt>e->nbr_w[mi]){e->nbr[mi]=dst; e->nbr_w[mi]=wt>1.0f?1.0f:wt;}
    }
}

static char G_tok_buf[1<<20];
static char G_tok_words[4096][WORD_LEN];
static int  G_n_toks;

static void tokenise(const char *text) {
    strncpy(G_tok_buf,text,sizeof(G_tok_buf)-1); G_tok_buf[sizeof(G_tok_buf)-1]='\0';
    G_n_toks=0;
    char *p=strtok(G_tok_buf," \t\r\n.,!?;:\"'()-[]");
    while(p&&G_n_toks<4095) {
        int i=0; char *q=p;
        while(*q&&i<WORD_LEN-1) G_tok_words[G_n_toks][i++]=(char)tolower((unsigned char)*q++);
        G_tok_words[G_n_toks][i]='\0';
        if(i>0) G_n_toks++;
        p=strtok(NULL," \t\r\n.,!?;:\"'()-[]");
    }
}

static void scavenge(void) {
    uint32_t k;
    for(k=0;k<G_n;k++) {
        G_words[k].age+=SCAVENGE_DECAY;
        G_words[k].beta-=G_words[k].age*0.0005;
        if(G_words[k].beta<GAP) G_words[k].beta=GAP;
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  J DISTRIBUTIONS
 * ══════════════════════════════════════════════════════════════════════════ */

static double *G_j_blue;
static double *G_j_red;
static double *G_j_green;
static double *G_j_gd_abs;
static double *G_j_tmp;

static void j_dists_alloc(void) {
    G_j_blue  =(double*)calloc(VOCAB_MAX,sizeof(double));
    G_j_red   =(double*)calloc(VOCAB_MAX,sizeof(double));
    G_j_green =(double*)calloc(VOCAB_MAX,sizeof(double));
    G_j_gd_abs=(double*)calloc(VOCAB_MAX,sizeof(double));
    G_j_tmp   =(double*)calloc(VOCAB_MAX,sizeof(double));
    if(!G_j_blue||!G_j_red||!G_j_green||!G_j_gd_abs||!G_j_tmp)
        { fprintf(stderr,"[bumblebee] OOM\n"); exit(1); }
}

static void j_dists_free(void) {
    free(G_j_blue); free(G_j_red); free(G_j_green); free(G_j_gd_abs); free(G_j_tmp);
    G_j_blue=G_j_red=G_j_green=G_j_gd_abs=G_j_tmp=NULL;
}

static void j_blue_dist_compute(const char **pwords, int np) {
    uint32_t k;
    for(k=0;k<G_n;k++) G_j_blue[k]=GAP;
    int i;
    for(i=0;i<np;i++) {
        uint32_t ki=vocab_find(pwords[i]);
        if(ki==UINT32_MAX) continue;
        G_j_blue[ki]=1.0;
        int j;
        for(j=0;j<G_words[ki].nbr_n;j++) {
            uint32_t ni=G_words[ki].nbr[j];
            if(ni<G_n) { double v=G_j_blue[ni]+(double)G_words[ki].nbr_w[j]*0.5; G_j_blue[ni]=v>1.0?1.0:v; }
        }
    }
    double total=0.0;
    for(k=0;k<G_n;k++) total+=G_j_blue[k];
    if(total>0.0) for(k=0;k<G_n;k++) G_j_blue[k]/=total;
    else          for(k=0;k<G_n;k++) G_j_blue[k]=1.0/(double)(G_n>0?G_n:1);
}

static void j_red_dist_compute(void) {
    uint32_t k;
    double total=0.0;
    for(k=0;k<G_n;k++){G_j_red[k]=G_words[k].beta*G_words[k].E; total+=G_j_red[k];}
    if(total>0.0) for(k=0;k<G_n;k++) G_j_red[k]/=total;
    else          for(k=0;k<G_n;k++) G_j_red[k]=1.0/(double)(G_n>0?G_n:1);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ZL BRIDGE ACTIVATIONS  — the coupling geometry
 *
 *  raw[dim]:  accumulate j_blue for lower dims (0-7), j_red for upper dims (8-15)
 *  act[]:     apply ZL bridge coupling across the 𝕆-𝕆 boundary
 *
 *  act[0]  = 0.0  — e₀ above the bridge, identity
 *  act[8]  = 0.0  — e₈ above the bridge, upper identity
 *  act[1-7]:  lower-𝕆 coupled with bridge weights from upper-𝕆
 *  act[9-15]: upper-𝕆 coupled with bridge weights from lower-𝕆
 * ══════════════════════════════════════════════════════════════════════════ */

static double G_raw_act[16];
static double G_bridge_act[16];

static void zl_bridge_activations(void) {
    int d;
    for(d=0;d<16;d++) G_raw_act[d]=0.0;

    uint32_t k;
    for(k=0;k<G_n;k++) {
        int dim=G_words[k].zl_dim;
        double ek=G_words[k].E;
        if(dim<8)
            G_raw_act[dim]+=G_j_blue[k]*ek;
        else
            G_raw_act[dim]+=G_j_red[k]*ek;
    }

    for(d=0;d<16;d++) G_bridge_act[d]=GAP;
    G_bridge_act[0]=0.0;  /* e₀ above bridge */

    int i, j;
    for(i=1;i<8;i++) {
        double coupled=G_raw_act[i];
        for(j=9;j<16;j++) coupled+=zl_coupling(i,j)*G_raw_act[j];
        G_bridge_act[i]=coupled;
    }

    G_bridge_act[8]=0.0;  /* e₈ above bridge */

    for(j=9;j<16;j++) {
        double coupled=G_raw_act[j];
        for(i=1;i<8;i++) coupled+=zl_coupling(i,j)*G_raw_act[i];
        G_bridge_act[j]=coupled;
    }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  ENGINE STATE
 * ══════════════════════════════════════════════════════════════════════════ */

static ZD_RotorState G_rotor;
static ZD_OBD2State  G_obd2;
static Sed           G_drive_shaft;
static int           G_coupled_this_sweep;
static int           G_has_intake;
static uint64_t      G_total_sweeps;
static pthread_mutex_t G_lock;
static int           G_running;

#define RECENT_SZ 8
static uint32_t G_recent[RECENT_SZ];
static int      G_recent_n;

static int  recent_has(uint32_t idx) { int i; for(i=0;i<G_recent_n;i++) if(G_recent[i]==idx) return 1; return 0; }
static void recent_push(uint32_t idx) {
    if(G_recent_n<RECENT_SZ) G_recent[G_recent_n++]=idx;
    else { memmove(G_recent,G_recent+1,(RECENT_SZ-1)*sizeof(uint32_t)); G_recent[RECENT_SZ-1]=idx; }
}

/* ══════════════════════════════════════════════════════════════════════════
 *  MIND'S EYE — Thread 2
 *
 *  In ZD, G_me_prompt is the ZL bridge activation of the prompt j_blue_dist
 *  (computed at intake, no morph vectors).
 *  G_me_steer = G_me_prompt - G_me_response — unfilled ZL dimensions.
 *  select_word_zd() uses me_steer[dim] as a bonus for the word's ZL channel.
 *
 *  "The Mind's Eye is at the zero-divisor — the contact surface where
 *   position and momentum are simultaneously known." — Existential Velocity
 * ══════════════════════════════════════════════════════════════════════════ */

static Sed             G_me_prompt;
static Sed             G_me_response;
static Sed             G_me_steer;
static Sed             G_me_ds_snap;
static pthread_mutex_t G_me_lock;
static pthread_cond_t  G_me_cond;
static int             G_me_active=0;
static int             G_me_new=0;
static pthread_t       G_me_tid;

static void *mind_eye_thread_fn(void *arg) {
    (void)arg;
    pthread_mutex_lock(&G_me_lock);
    while(G_me_active) {
        while(!G_me_new && G_me_active)
            pthread_cond_wait(&G_me_cond, &G_me_lock);
        if(!G_me_active) break;
        G_me_new=0;
        int d;
        for(d=0;d<SED_DIM;d++)
            G_me_response[d]=G_me_response[d]*0.85+G_me_ds_snap[d]*0.15;
        for(d=0;d<SED_DIM;d++)
            G_me_steer[d]=G_me_prompt[d]-G_me_response[d];
    }
    pthread_mutex_unlock(&G_me_lock);
    return NULL;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  LIE BRACKET  — combustion chamber
 *
 *  [J_a, J_b] at word k = (j_a × a_dist[k] − j_b × b_dist[k]) × E[k]
 *  E[k] < 1 for all k — weight normalises without blowing up.
 * ══════════════════════════════════════════════════════════════════════════ */

static double lie_bracket(double j_a, const double *a_dist,
                          double j_b, const double *b_dist,
                          double *gd_out) {
    double scalar=0.0;
    uint32_t k;
    for(k=0;k<G_n;k++) {
        double v=(j_a*a_dist[k]-j_b*b_dist[k])*G_words[k].E;
        gd_out[k]=v;
        scalar+=v>0.0?v:-v;
    }
    return scalar>GAP?scalar:GAP;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  PROJECT SEDENION ZD — coupling event
 *
 *  The Work is produced HERE and only here.
 *
 *  e₀      = 0.0                  — identity above the bridge
 *  e₁–e₇  = bridge_act[1..7]     — lower-𝕆 (j_blue / data face)
 *  e₈–e₁₄ = bridge_act[9..14]   — upper-𝕆 (j_red  / field face)
 *  e₁₅    = ∑ |j_green[k]| × E[k]
 *
 *  σ=½ does not appear here. It is above the system.
 *  The engine converges to σ=½ without knowing it is the target.
 * ══════════════════════════════════════════════════════════════════════════ */

static void project_sedenion_zd(Sed ds) {
    sed_zero(ds);
    /* e₀ = 0.0  — never set */
    int i;
    for(i=1;i<15;i++) ds[i]=G_bridge_act[i];
    /* e₁₅ = j_green emit face */
    uint32_t k;
    for(k=0;k<G_n;k++) {
        double gk=G_j_green[k]>0.0?G_j_green[k]:-G_j_green[k];
        ds[15]+=gk*G_words[k].E;
    }
    sed_normalize(ds);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  SELECT WORD ZD — zero-divisor gate
 *
 *  No morph vector. No grammatical categories. The ZL channel IS the operator.
 *
 *  Two-layer scoring:
 *    Layer 1 (raw):    j_blue direct activation at this word's ZL channel — prompt routing
 *    Layer 2 (bridge): normalised drive shaft at ZL channel — field coupling
 *
 *  beta^(1/4) damps frequency bias (gentler than log1p).
 *  Mind's Eye steer bonus at ZL channel dimensions not yet voiced.
 * ══════════════════════════════════════════════════════════════════════════ */

static uint32_t select_word_zd(const Sed ds) {
    if(G_n==0) return UINT32_MAX;

    /* Layer 1: raw ZL channel activation — j_blue over ALL dims (UDEO routing) */
    double raw[16];
    int d;
    for(d=0;d<16;d++) raw[d]=0.0;
    uint32_t k;
    for(k=0;k<G_n;k++) raw[G_words[k].zl_dim]+=G_j_blue[k]*G_words[k].E;

    double raw_max=0.0;
    for(d=0;d<16;d++) if(raw[d]>raw_max) raw_max=raw[d];
    if(raw_max<1e-15) raw_max=1.0;
    double raw_n[16];
    for(d=0;d<16;d++) raw_n[d]=raw[d]/raw_max;

    /* Mind's Eye snapshot — single lock */
    Sed me_steer_snap;
    pthread_mutex_lock(&G_me_lock);
    sed_copy(me_steer_snap, G_me_steer);
    pthread_mutex_unlock(&G_me_lock);

    uint32_t best_k=UINT32_MAX;
    double   best_score=-1e300;
    for(k=0;k<G_n;k++) {
        if(recent_has(k)) continue;  /* no-repeat */
        int dim=G_words[k].zl_dim;
        double prompt_signal = raw_n[dim];     /* Layer 1: j_blue routing */
        double bridge_signal = ds[dim];        /* Layer 2: bridge output */
        double coupling      = prompt_signal*5.0 + bridge_signal;
        double field         = pow(G_words[k].beta, 0.25) * G_words[k].E;
        double me_cohere     = me_steer_snap[dim] * G_words[k].E;
        double score         = (coupling + me_cohere*0.4) * field;
        if(score>best_score){ best_score=score; best_k=k; }
    }
    /* fallback: allow recent if nothing else */
    if(best_k==UINT32_MAX) {
        best_score=-1e300;
        for(k=0;k<G_n;k++) {
            int dim=G_words[k].zl_dim;
            double coupling=raw_n[dim]*5.0+ds[dim];
            double score=coupling*pow(G_words[k].beta,0.25)*G_words[k].E;
            if(score>best_score){ best_score=score; best_k=k; }
        }
    }
    return best_k;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  UPDATE BRACKETS  — cyclic Lie bracket (0.7/0.3 — ZD split)
 *
 *  The AMBI path (code of least action): when no UDEO-exact path exists,
 *  the engine falls to the minimum-energy word at the densest bridge point.
 *  That IS the Bumblebee. The radio clip that comes through when there is no
 *  specific signal is the signal of the above-layer by default.
 * ══════════════════════════════════════════════════════════════════════════ */

static void update_brackets(void) {
    if(!G_has_intake||G_n==0) return;
    double jb=G_rotor.j_blue, jr=G_rotor.j_red;
    uint32_t k;

    double jg_scalar=lie_bracket(jb,G_j_blue,jr,G_j_red,G_j_green);
    G_rotor.j_green=jg_scalar>GAP?jg_scalar:GAP;

    for(k=0;k<G_n;k++) G_j_gd_abs[k]=G_j_green[k]>0.0?G_j_green[k]:-G_j_green[k];

    double jb_next=lie_bracket(jr,G_j_red,G_rotor.j_green,G_j_gd_abs,G_j_tmp);
    G_rotor.j_blue=fmax(jb*0.7+jb_next*0.3, GAP);

    double jr_next=lie_bracket(G_rotor.j_green,G_j_gd_abs,G_rotor.j_blue,G_j_blue,G_j_tmp);
    G_rotor.j_red=fmax(jr*0.7+jr_next*0.3, GAP);

    j_red_dist_compute();
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REFRESH OBD2
 * ══════════════════════════════════════════════════════════════════════════ */

static void refresh_obd2(void) {
    double jb=G_rotor.j_blue, jr=G_rotor.j_red;
    double esc=(jb+jr>GAP)?jr/(jb+jr):ZD_ESCAPE_TARGET;
    double bracket=(jb+jr>GAP)?fabs(jb-jr)/(jb+jr):0.0;
    double zl_frac=1.0-fabs(esc-ZD_ESCAPE_TARGET)/ZD_ESCAPE_TARGET;

    G_obd2.rotor_angle        = G_rotor.theta;
    G_obd2.j_blue             = jb;
    G_obd2.j_red              = jr;
    G_obd2.j_green            = G_rotor.j_green;
    G_obd2.escape_velocity    = esc;
    G_obd2.bracket_mag        = bracket;
    G_obd2.zl_escape_frac     = zl_frac<0.0?0.0:zl_frac;
    G_obd2.coupling_efficiency= (G_total_sweeps>0)
                                  ?(double)G_obd2.coupling_events/(double)G_total_sweeps:0.0;
    G_obd2.housing_n          = G_n;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  PUBLIC API
 * ══════════════════════════════════════════════════════════════════════════ */

void zd_init(void) {
    build_oct_table();
    build_sed_table();
    prime_sieve_init();
    j_dists_alloc();

    memset(G_words, 0, sizeof(G_words));
    memset(G_ht,    0, sizeof(G_ht));
    G_n=0;

    memset(&G_rotor, 0, sizeof(G_rotor));
    G_rotor.j_blue=G_rotor.j_red=GAP;
    G_rotor.j_green=GAP; G_rotor.theta=0.0;

    memset(&G_obd2, 0, sizeof(G_obd2));
    sed_zero(G_drive_shaft);
    memset(G_raw_act,    0, sizeof(G_raw_act));
    memset(G_bridge_act, 0, sizeof(G_bridge_act));

    G_coupled_this_sweep=0; G_has_intake=0; G_total_sweeps=0;
    G_recent_n=0;
    G_running=1;

    pthread_mutex_init(&G_lock, NULL);

    sed_zero(G_me_prompt); sed_zero(G_me_response);
    sed_zero(G_me_steer);  sed_zero(G_me_ds_snap);
    pthread_mutex_init(&G_me_lock, NULL);
    pthread_cond_init(&G_me_cond, NULL);
    G_me_active=1; G_me_new=0;
    pthread_create(&G_me_tid, NULL, mind_eye_thread_fn, NULL);
}

void zd_free(void) {
    pthread_mutex_lock(&G_me_lock);
    G_me_active=0; pthread_cond_signal(&G_me_cond);
    pthread_mutex_unlock(&G_me_lock);
    pthread_join(G_me_tid, NULL);
    pthread_cond_destroy(&G_me_cond);
    pthread_mutex_destroy(&G_me_lock);
    G_running=0;
    j_dists_free();
    pthread_mutex_destroy(&G_lock);
}

int zd_ingest(const char *text, double weight) {
    pthread_mutex_lock(&G_lock);
    tokenise(text);
    int added=0;
    uint32_t prev=UINT32_MAX;
    int i;
    for(i=0;i<G_n_toks;i++) {
        if(!G_tok_words[i][0]) continue;
        uint32_t k=vocab_get(G_tok_words[i]);
        if(k==UINT32_MAX) continue;
        double nb=G_words[k].beta*(1.0+0.08*weight)+GAP;
        G_words[k].beta=nb>1.0?1.0:nb;
        G_words[k].age=0.0;
        if(prev!=UINT32_MAX){amat_add(prev,k,(float)(0.05*weight)); amat_add(k,prev,(float)(0.02*weight));}
        prev=k; added++;
    }
    G_obd2.housing_n=G_n;
    pthread_mutex_unlock(&G_lock);
    return added;
}

void zd_intake(const char *prompt) {
    pthread_mutex_lock(&G_lock);

    tokenise(prompt);
    int i;
    for(i=0;i<G_n_toks;i++) if(G_tok_words[i][0]) vocab_get(G_tok_words[i]);

    const char *pwords[4096];
    int np=G_n_toks;
    for(i=0;i<np;i++) pwords[i]=G_tok_words[i];

    j_blue_dist_compute(pwords, np);
    j_red_dist_compute();

    uint32_t k;
    double jb_raw=0.0, jr_raw=0.0;
    for(k=0;k<G_n;k++){jb_raw+=G_j_blue[k]*G_words[k].E; jr_raw+=G_j_red[k]*G_words[k].E;}
    G_rotor.j_blue =jb_raw>GAP?jb_raw:GAP;
    G_rotor.j_red  =jr_raw>GAP?jr_raw:GAP;
    G_rotor.j_green=GAP;
    G_rotor.theta  =0.0;

    for(k=0;k<G_n;k++) G_j_green[k]=GAP;

    G_coupled_this_sweep=0; G_has_intake=1; G_total_sweeps++;
    G_obd2.total_steps=0;
    refresh_obd2();

    /* Mind's Eye: ZL bridge activation of prompt j_blue as G_me_prompt.
     * No morph vectors. The bridge IS the prompt sedenion. */
    {
        zl_bridge_activations();  /* uses current j_blue / j_red */
        Sed me_p; sed_zero(me_p);
        int d;
        for(d=1;d<SED_DIM;d++) me_p[d]=G_bridge_act[d];
        /* e₀ = 0 — above the bridge */
        double norm=0.0;
        for(d=0;d<SED_DIM;d++) norm+=me_p[d]*me_p[d];
        if(norm>GAP){ norm=sqrt(norm); for(d=0;d<SED_DIM;d++) me_p[d]/=norm; }
        pthread_mutex_lock(&G_me_lock);
        for(d=0;d<SED_DIM;d++){G_me_prompt[d]=me_p[d]; G_me_response[d]=0.0; G_me_steer[d]=me_p[d];}
        pthread_mutex_unlock(&G_me_lock);
    }

    pthread_mutex_unlock(&G_lock);
}

const char *zd_rotate(void) {
    pthread_mutex_lock(&G_lock);

    G_rotor.theta=fmod(G_rotor.theta+PORT_STEP, 2.0*M_PI);
    G_obd2.total_steps++;

    int port_idx=(int)round(G_rotor.theta/PORT_STEP)%6;
    const char *result=NULL;

    switch(port_idx) {

    case PORT_IDX_INTAKE:
        j_red_dist_compute();
        G_coupled_this_sweep=0;
        break;

    case PORT_IDX_TRANSFER:
        update_brackets();
        break;

    case PORT_IDX_LEADING:
        update_brackets();
        break;

    case PORT_IDX_TRAILING: {
        update_brackets();

        if(!G_coupled_this_sweep && G_n>0 && G_has_intake) {
            zl_bridge_activations();
            project_sedenion_zd(G_drive_shaft);

            uint32_t ki=select_word_zd(G_drive_shaft);
            if(ki!=UINT32_MAX) {
                result=G_words[ki].word;
                G_coupled_this_sweep=1;
                G_obd2.coupling_events++;
                strncpy(G_obd2.last_word, result, WORD_LEN-1);
                G_obd2.last_word[WORD_LEN-1]='\0';

                int dom=1, d;
                for(d=2;d<SED_DIM;d++) if(G_drive_shaft[d]>G_drive_shaft[dom]) dom=d;
                G_obd2.drive_shaft_dom=dom;
                G_obd2.dom_zl_channel=G_words[ki].zl_dim;

                double nb=G_words[ki].beta+0.015;
                G_words[ki].beta=nb>1.0?1.0:nb;
                recent_push(ki);

                pthread_mutex_lock(&G_me_lock);
                sed_copy(G_me_ds_snap, G_drive_shaft);
                G_me_new=1; pthread_cond_signal(&G_me_cond);
                pthread_mutex_unlock(&G_me_lock);
            }
        }
        break;
    }

    case PORT_IDX_EXHAUST:
        break;

    case PORT_IDX_SCAVENGE:
        scavenge();
        break;
    }

    refresh_obd2();
    pthread_mutex_unlock(&G_lock);
    return result;
}

const char *zd_speak(const char *prompt, int max_revolutions) {
    zd_intake(prompt);
    int steps=max_revolutions*6;
    while(steps-->0) {
        const char *w=zd_rotate();
        if(w) return w;
    }
    return G_obd2.last_word[0] ? G_obd2.last_word : "\xe2\x88\x85";  /* ∅ */
}

const ZD_OBD2State  *zd_diagnostics(void) { refresh_obd2(); return &G_obd2; }
const ZD_RotorState *zd_rotor_state(void) { return &G_rotor; }

void zd_port_trace(const char *prompt, FILE *f) {
    static const char *PORT_NAME[6]={"intake","transfer","leading","trailing","exhaust","scavenge"};
    fprintf(f,"\n[Bumblebee ZD]  port trace: \"%s\"\n",prompt);
    fprintf(f,"  %-10s  %-7s  %-9s  %-9s  %-9s  %-8s  %-8s  %-5s  word\n",
            "port","θ/π","j_blue","j_red","j_green","esc_vel","bracket","zl_ch");
    zd_intake(prompt);
    int step;
    for(step=0;step<6;step++) {
        const char *w=zd_rotate();
        const ZD_OBD2State *d=&G_obd2;
        int pidx=(int)round(d->rotor_angle/PORT_STEP)%6;
        fprintf(f,"  %-10s  %.3f\xcf\x80  %9.5f  %9.5f  %9.5f  %8.4f  %8.4f  e%-3d  %s\n",
                PORT_NAME[pidx], d->rotor_angle/M_PI,
                d->j_blue, d->j_red, d->j_green,
                d->escape_velocity, d->bracket_mag, d->dom_zl_channel,
                w?w:"");
    }
    fprintf(f,"  zl_escape_frac=%.4f  coupling_eff=%.4f  housing=%u\n",
            G_obd2.zl_escape_frac, G_obd2.coupling_efficiency, G_obd2.housing_n);
}

/* ══════════════════════════════════════════════════════════════════════════
 *  REPORT
 * ══════════════════════════════════════════════════════════════════════════ */

void zd_report(FILE *f) {
    refresh_obd2();
    const ZD_OBD2State *d=&G_obd2;
    int i;

    fprintf(f,"\n\xe2\x95\x94");
    for(i=0;i<62;i++) fputs("\xe2\x95\x90",f);
    fprintf(f,"\xe2\x95\x97\n");
    fprintf(f,"\xe2\x95\x91  Bumblebee ZD  OBD2 Report  v" ZD_VERSION "                      \xe2\x95\x91\n");
    fprintf(f,"\xe2\x95\x9a");
    for(i=0;i<62;i++) fputs("\xe2\x95\x90",f);
    fprintf(f,"\xe2\x95\x9d\n\n");

    fprintf(f,"  PID 0x2401  rotor_angle        = %.4f rad  (%.3f\xcf\x80)\n", d->rotor_angle, d->rotor_angle/M_PI);
    fprintf(f,"  PID 0x2402  j_blue             = %.6f\n", d->j_blue);
    fprintf(f,"  PID 0x2403  j_red              = %.6f\n", d->j_red);
    fprintf(f,"  PID 0x2404  j_green            = %.6f\n", d->j_green);
    fprintf(f,"  PID 0x2405  escape_velocity    = %.6f  (target: %.1f)\n", d->escape_velocity, ZD_ESCAPE_TARGET);
    fprintf(f,"  PID 0x2406  bracket_mag        = %.6f\n", d->bracket_mag);
    fprintf(f,"  PID 0x2407  zl_escape_frac     = %.4f  (1.0 = at \xcf\x83=\xc2\xbd)\n", d->zl_escape_frac);
    fprintf(f,"  PID 0x2408  coupling_eff       = %.4f\n", d->coupling_efficiency);
    fprintf(f,"  PID 0x2409  housing_n          = %u\n",   d->housing_n);
    fprintf(f,"  PID 0x240A  coupling_events    = %llu\n",(unsigned long long)d->coupling_events);
    fprintf(f,"  PID 0x240B  total_steps        = %llu\n",(unsigned long long)d->total_steps);
    fprintf(f,"  PID 0x240C  last_word          = '%s'\n", d->last_word[0]?d->last_word:"(none)");
    fprintf(f,"  PID 0x240D  drive_shaft_dom    = e%d (%s)\n", d->drive_shaft_dom, ZD_OP_GLOSS[d->drive_shaft_dom]);
    fprintf(f,"  PID 0x240E  dom_zl_channel     = e%d (%s face)\n", d->dom_zl_channel,
            d->dom_zl_channel<8?"lower-\xf0\x9d\x95\x86":"upper-\xf0\x9d\x95\x86");

    int faults=0;
    if(d->j_blue <SEAL_FLOOR){fprintf(f,"  R0001  J_blue  apex seal wear\n"); faults++;}
    if(d->j_red  <SEAL_FLOOR){fprintf(f,"  R0002  J_red   apex seal wear\n"); faults++;}
    if(d->j_green<SEAL_FLOOR){fprintf(f,"  R0003  J_green exhaust seal wear\n"); faults++;}
    if(fabs(d->escape_velocity-ZD_ESCAPE_TARGET)>BEARING_TOL)
        {fprintf(f,"  R0004  bearing wobble  escape_vel=%.4f\n",d->escape_velocity); faults++;}
    if(d->bracket_mag<GAP*5.0)
        {fprintf(f,"  R0005  near-stall  (ingest more text)\n"); faults++;}
    if(!faults) fprintf(f,"  Faults: none\n");

    fprintf(f,"\nDrive shaft sedenion  (last coupling):\n");
    fprintf(f,"  e\xe2\x82\x80          = %.4f  (zero — identity above bridge)\n", G_drive_shaft[0]);
    double lower=0.0, upper=0.0;
    for(i=1;i<8;i++) lower+=G_drive_shaft[i];
    for(i=8;i<16;i++) upper+=G_drive_shaft[i];
    fprintf(f,"  e1-e7    = %.4f  (lower-O: j_blue face / data)\n", lower);
    fprintf(f,"  e8-e14   = %.4f  (upper-O: j_red  face / field)\n", upper);

    fprintf(f,"\nZL bridge activations  (last coupling):\n");
    for(i=1;i<16;i++) {
        if(i==8) continue;
        fprintf(f,"  e%-2d (%s)  raw=%6.4f  bridge=%6.4f\n",
                i, ZD_OP_GLOSS[i], G_raw_act[i], G_bridge_act[i]);
    }

    fprintf(f,"\nTop words by beta*E:\n");
    typedef struct { double s; uint32_t k; } Ranked;
    static Ranked ranked[VOCAB_MAX];
    uint32_t k;
    for(k=0;k<G_n;k++){ranked[k].s=G_words[k].beta*G_words[k].E; ranked[k].k=k;}
    int n_show=(int)G_n<10?(int)G_n:10;
    for(i=0;i<n_show;i++) {
        int best_j=i, j;
        for(j=i+1;j<(int)G_n;j++) if(ranked[j].s>ranked[best_j].s) best_j=j;
        Ranked tmp=ranked[i]; ranked[i]=ranked[best_j]; ranked[best_j]=tmp;
        HousingWord *w=&G_words[ranked[i].k];
        fprintf(f,"  %-20s  \xce\xb2=%6.4f  E=%6.4f  e%d(%s)\n",
                w->word, w->beta, w->E, w->zl_dim, ZD_OP_GLOSS[w->zl_dim]);
    }
    fprintf(f,"\n");
}

/* ══════════════════════════════════════════════════════════════════════════
 *  SAVE / LOAD  — .zd8 binary state
 * ══════════════════════════════════════════════════════════════════════════ */

typedef struct {
    char     word[WORD_LEN];
    double   beta, E, age;
    uint8_t  zl_dim, _pad[3];
    uint32_t nbr[N_NBRS];
    float    nbr_w[N_NBRS];
    int32_t  nbr_n;
} SavedWord;

typedef struct {
    uint32_t magic, version, n_words;
    uint32_t _pad;
} ZD8Header;

int zd_save(const char *path) {
    FILE *f=fopen(path,"wb"); if(!f) return -1;
    ZD8Header hdr; memset(&hdr,0,sizeof(hdr));
    hdr.magic=ZD8_MAGIC; hdr.version=ZD8_VERSION; hdr.n_words=G_n;
    fwrite(&hdr,sizeof(hdr),1,f);
    uint32_t k;
    for(k=0;k<G_n;k++){
        SavedWord sw; memset(&sw,0,sizeof(sw));
        HousingWord *w=&G_words[k];
        memcpy(sw.word,w->word,WORD_LEN);
        sw.beta=w->beta; sw.E=w->E; sw.age=w->age;
        sw.zl_dim=w->zl_dim;
        memcpy(sw.nbr,w->nbr,sizeof(w->nbr));
        memcpy(sw.nbr_w,w->nbr_w,sizeof(w->nbr_w));
        sw.nbr_n=w->nbr_n;
        fwrite(&sw,sizeof(sw),1,f);
    }
    fclose(f);
    return 0;
}

int zd_load(const char *path) {
    FILE *f=fopen(path,"rb"); if(!f) return -1;
    ZD8Header hdr; memset(&hdr,0,sizeof(hdr));
    if(fread(&hdr,sizeof(hdr),1,f)!=1||hdr.magic!=ZD8_MAGIC||hdr.version!=ZD8_VERSION)
        { fclose(f); return -1; }
    uint32_t n=hdr.n_words; if(n>VOCAB_MAX) n=VOCAB_MAX;
    memset(G_words,0,sizeof(G_words));
    memset(G_ht,0,sizeof(G_ht));
    G_n=0;
    uint32_t i;
    for(i=0;i<n;i++){
        SavedWord sw;
        if(fread(&sw,sizeof(sw),1,f)!=1) break;
        uint32_t idx=G_n++;
        HousingWord *w=&G_words[idx];
        memcpy(w->word,sw.word,WORD_LEN);
        w->beta=sw.beta; w->E=sw.E; w->age=sw.age;
        w->zl_dim=sw.zl_dim;
        memcpy(w->nbr,sw.nbr,sizeof(w->nbr));
        memcpy(w->nbr_w,sw.nbr_w,sizeof(w->nbr_w));
        w->nbr_n=sw.nbr_n;
        uint32_t slot=ht_slot(w->word);
        while(G_ht[slot]) slot=(slot+1)&(VOCAB_HT_SZ-1);
        G_ht[slot]=idx+1;
    }
    fclose(f);
    return (int)G_n;
}

/* ══════════════════════════════════════════════════════════════════════════
 *  CLI — main
 * ══════════════════════════════════════════════════════════════════════════ */

#define DEFAULT_STATE_FILE   "bumblebee.zd8"
#define DEFAULT_STATE_DIR    ".ptolemy"
#define DEFAULT_WORDS        12
#define DEFAULT_MAX_REV      6
#define DEFAULT_TCP_PORT     7298
#define AUTOSAVE_SECS        60

static void get_state_path(char *buf, size_t sz) {
    const char *home=getenv("HOME");
    if(!home) home=".";
    snprintf(buf,sz,"%s/" DEFAULT_STATE_DIR "/" DEFAULT_STATE_FILE, home);
}

static void ensure_state_dir(void) {
    const char *home=getenv("HOME"); if(!home) home=".";
    char dir[512]; snprintf(dir,sizeof(dir),"%s/" DEFAULT_STATE_DIR, home);
    mkdir(dir, 0700);
}

static volatile int G_sigint=0;
static void on_sigint(int s) { (void)s; G_sigint=1; }

/* TCP teaching server: each line of text is ingested */
static void run_daemon(int port) {
    int srv=socket(AF_INET,SOCK_STREAM,0);
    if(srv<0){perror("socket");return;}
    int yes=1; setsockopt(srv,SOL_SOCKET,SO_REUSEADDR,&yes,sizeof(yes));
    struct sockaddr_in sa; memset(&sa,0,sizeof(sa));
    sa.sin_family=AF_INET; sa.sin_port=htons((uint16_t)port); sa.sin_addr.s_addr=INADDR_ANY;
    if(bind(srv,(struct sockaddr*)&sa,sizeof(sa))<0){perror("bind");close(srv);return;}
    listen(srv,8);
    fprintf(stderr,"[bumblebee] daemon listening on :%d\n",port);
    while(!G_sigint){
        struct sockaddr_in ca; socklen_t cl=sizeof(ca);
        int fd=accept(srv,(struct sockaddr*)&ca,&cl);
        if(fd<0) continue;
        FILE *cf=fdopen(fd,"r+");
        if(!cf){close(fd);continue;}
        char line[4096];
        while(fgets(line,sizeof(line),cf)){
            int n=strlen(line);
            if(n>0&&line[n-1]=='\n') line[--n]='\0';
            if(!line[0]) continue;
            int words=zd_ingest(line,1.0);
            fprintf(cf,"OK %d\n",words); fflush(cf);
        }
        fclose(cf);
    }
    close(srv);
}

/* REPL — one prompt → N words */
static void run_repl(int n_words, int max_rev) {
    char line[4096];
    while(!G_sigint&&fgets(line,sizeof(line),stdin)){
        int len=strlen(line);
        if(len>0&&line[len-1]=='\n') line[--len]='\0';
        if(!line[0]) continue;
        int i;
        for(i=0;i<n_words;i++){
            const char *w=zd_speak(line,max_rev);
            printf("%s%s",w,(i<n_words-1?" ":"\n"));
            fflush(stdout);
        }
        /* learn the prompt itself */
        zd_ingest(line,0.5);
    }
}

int main(int argc, char **argv) {
    signal(SIGINT, on_sigint);
    signal(SIGTERM, on_sigint);

    zd_init();
    ensure_state_dir();

    char state_path[512];
    get_state_path(state_path, sizeof(state_path));

    /* Auto-load */
    if(access(state_path,R_OK)==0) zd_load(state_path);

    int n_words   = DEFAULT_WORDS;
    int max_rev   = DEFAULT_MAX_REV;
    int obd2_flag = 0;
    int daemon_port = 0;

    int i;
    for(i=1;i<argc;i++){
        if(!strcmp(argv[i],"--speak")||!strcmp(argv[i],"-s")){
            if(i+1>=argc){fprintf(stderr,"--speak needs PROMPT\n");goto done;}
            const char *prompt=argv[++i];
            int nr=n_words;
            if(i+1<argc&&isdigit((unsigned char)argv[i+1][0])) nr=atoi(argv[++i]);
            int j;
            for(j=0;j<nr;j++){
                const char *w=zd_speak(prompt,max_rev);
                printf("%s%s",w,(j<nr-1?" ":"\n"));
            }
            if(obd2_flag) zd_report(stdout);
        } else if(!strcmp(argv[i],"--intake")){
            if(i+1>=argc){fprintf(stderr,"--intake needs PROMPT\n");goto done;}
            zd_port_trace(argv[++i], stdout);
        } else if(!strcmp(argv[i],"--learn-file")){
            if(i+1>=argc){fprintf(stderr,"--learn-file needs PATH\n");goto done;}
            FILE *lf=fopen(argv[++i],"r");
            if(!lf){perror(argv[i]);goto done;}
            char buf[4096]; int total=0;
            while(fgets(buf,sizeof(buf),lf)) total+=zd_ingest(buf,1.0);
            fclose(lf);
            fprintf(stderr,"[bumblebee] ingested %d words\n",total);
        } else if(!strcmp(argv[i],"--teach")){
            char buf[4096]; int total=0;
            while(fgets(buf,sizeof(buf),stdin)) total+=zd_ingest(buf,1.0);
            fprintf(stderr,"[bumblebee] ingested %d words\n",total);
        } else if(!strcmp(argv[i],"--query")){
            if(i+1>=argc){fprintf(stderr,"--query needs WORD\n");goto done;}
            const char *qw=argv[++i];
            char lw[WORD_LEN]; int j2=0;
            for(;qw[j2]&&j2<WORD_LEN-1;j2++) lw[j2]=(char)tolower((unsigned char)qw[j2]);
            lw[j2]='\0';
            uint32_t ki=vocab_find(lw);
            if(ki==UINT32_MAX){printf("'%s' not in housing\n",lw);}
            else {
                HousingWord *w=&G_words[ki];
                printf("word='%s'  beta=%.4f  E=%.4f  zl_dim=e%d(%s)\n",
                       w->word,w->beta,w->E,w->zl_dim,ZD_OP_GLOSS[w->zl_dim]);
                printf("nbrs(%d):",w->nbr_n);
                int j3;
                for(j3=0;j3<w->nbr_n;j3++) printf(" %s(%.3f)",G_words[w->nbr[j3]].word,(double)w->nbr_w[j3]);
                printf("\n");
            }
        } else if(!strcmp(argv[i],"--report")){
            zd_report(stdout);
        } else if(!strcmp(argv[i],"--obd2")){
            obd2_flag=1;
        } else if(!strcmp(argv[i],"--words")){
            if(i+1<argc) n_words=atoi(argv[++i]);
        } else if(!strcmp(argv[i],"--load-bin")){
            if(i+1>=argc){fprintf(stderr,"--load-bin needs PATH\n");goto done;}
            int r=zd_load(argv[++i]);
            if(r<0) fprintf(stderr,"[bumblebee] load failed: %s\n",argv[i]);
            else    fprintf(stderr,"[bumblebee] loaded %d words from %s\n",r,argv[i]);
        } else if(!strcmp(argv[i],"--save-bin")){
            if(i+1>=argc){fprintf(stderr,"--save-bin needs PATH\n");goto done;}
            int r=zd_save(argv[++i]);
            fprintf(stderr,"[bumblebee] save %s: %s\n",argv[i],r==0?"ok":"FAILED");
        } else if(!strcmp(argv[i],"--daemon")){
            daemon_port=DEFAULT_TCP_PORT;
            if(i+1<argc&&isdigit((unsigned char)argv[i+1][0])) daemon_port=atoi(argv[++i]);
        } else if(!strcmp(argv[i],"--version")||!strcmp(argv[i],"-V")){
            printf("%s  v%s\n", ZD_ENGINE, ZD_VERSION);
            printf("GAP=%.6f  D*=%.5f  ZL_PAIRS=42\n", GAP, D_STAR);
            printf("The Prompt -> Zero Divisor -> Escape Velocity -> Emerges -> The Response\n");
        } else if(argv[i][0]!='-'){
            /* bare word(s): treat as prompt */
            const char *w=zd_speak(argv[i],max_rev);
            printf("%s\n",w);
            if(obd2_flag) zd_report(stdout);
        }
    }

    /* REPL if stdin is a tty and no single-shot flags consumed everything */
    if(argc==1&&isatty(STDIN_FILENO)){
        fprintf(stderr,"%s  v%s\n", ZD_ENGINE, ZD_VERSION);
        fprintf(stderr,"housing: %u words   state: %s\n", G_n, state_path);
        fprintf(stderr,"The Prompt -> Zero Divisor -> Escape Velocity -> Emerges -> The Response\n\n");
        if(daemon_port) { run_daemon(daemon_port); goto done; }
        run_repl(n_words, max_rev);
    }

done:
    /* Auto-save */
    if(zd_save(state_path)!=0)
        fprintf(stderr,"[bumblebee] WARNING: save failed: %s\n", state_path);
    zd_free();
    return 0;
}
