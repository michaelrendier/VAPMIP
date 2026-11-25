/*
 * ptol.c — Sedenion geometry engine.
 *
 * usage: ptol [-r] [-eye <R|C|H|O|S>] [-s [dir]] [-b [dir]] [-H [dir]] [-i <image>] <prompt>
 *
 * Projects input string onto 16 sedenion basis elements e0..e15 via
 * Dirichlet-weighted inner product:
 *
 *   J_red  shells (k=0-3, 8-11):  x_k = Σ c_i · i^(-σ) · cos(2π·i / p_k)
 *   J_blue shells (k=4-7, 12-15): x_k = Σ c_i · i^(-σ) · sin(2π·i / p_k)
 *
 * Default σ=½ (Eye H) is Noether forcing — not a free parameter.
 * J_red × J_blue = d* = 0.24600 is conserved at all σ (E=mc²).
 * Prime frequencies are the zero-free-parameter basis: {2,3,5,...,53}.
 *
 * The response is the shadow of the geometry.
 * These scalars are the geometry.  The words are the shadow.
 *
 * ── The fold (2026-08-28, no version bump — additive readout only) ────────
 * The J_red / J_blue power balance IS the Smith / Joukowsky fold. Writing
 * the projection as an ADD:SCALE:SIGN word (the tier-0 floor
 * Aff(1,R) = ADD |x| (SCALE x SIGN)):
 *
 *   u  =  g·ln s + a   ,   here  a = 0 (anchored at the balanced Eye),
 *                               s = P_red / P_blue  (the SCALE),
 *                               g = sign(ln s)       (the SIGN)
 *   Γ  =  tanh(u/2)  =  (P_red − P_blue) / (P_red + P_blue)  =  2·σ_self − 1
 *
 * Γ = 0  ⟺  σ_self = ½  ⟺  u = 0  ⟺  the ground state / Eye H / the now.
 * The tower Eyes R,C,H,O,S are this same fold read at σ = 1, ¾, ½, ¼, 0.
 * measure_gamma() below returns (Γ, u); the -r and -sigma reports print them.
 *
 * NOTE (deferred, needs the author's call): 0_RB emits d*_taut = Ω_ZS/ln 10
 * ≈ 0.24631 as the *geometry* (the "Flow" face); 0.24600 above is the
 * *measured* "Boundary" face (d*_spec). ptol.c is the geometry engine, so
 * the conserved constant here may want to be 0.24631 — left at 0.24600
 * pending sign-off, since changing a load-bearing constant is a 5.2 change.
 *
 * Flags:
 *   -r         raw mode: 16 scalars + primes + 16 Σ_RB products, machine-readable
 *   -eye <X>   set observation Eye: R(σ=1) C(σ=¾) H(σ=½) O(σ=¼) S(σ=0)
 *   -s [dir]   write SVG paper (pathway — spiral from ZD to great circle)
 *   -b [dir]   write PPM bitmap paper (field — 16 scalar amplitudes)
 *   -H [dir]   write HTML paper (SVG + bitmap + text shadow, all together)
 *   -i <file>  read image as prompt (via ImageMagick — geometry-first OCR)
 *   -say <p>   one-shot console_speak() — no curses console, no socketpair;
 *              the sentence creator's voice from a shell, fully offline
 *   -w         fork the PtolemyDesktop tabbed curses console (Chat /
 *   --boxkite  ValaQuenta / Generational Lineage / Archimedes — unfinished
 *   --console  tabs greyed) onto the tty and stay resident as the speaking
 *              monad behind monad_harness.c: the console draws curses, this
 *              process answers `say` frames with the sedenion-projection
 *              word shadow. `/paragraph` in the Chat Tab flips the console to
 *              paragraph grammar; the default is sentence construction.
 *
 * Papers are written to dir (default: current directory).
 * Filename: ptol_<prompt_slug>_<timestamp>.{svg,ppm,html}
 *
 * SVG: 16-spoke web showing sedenion field. Spiral path from ZD (centre)
 *      outward to great circle (rim), tracing the Lagrangian trajectory.
 *      Active prime spokes highlighted. Sign encoded by colour (red/blue).
 *
 * PPM: 4×4 grid of pixels, one per sedenion dimension.
 *      Brightness = |x_k|, hue = sign (red positive, blue negative).
 *      Upscaled to 256×256 nearest-neighbour for visibility.
 *
 * HTML: SVG + PPM (as data URI) + text shadow (spiral words placeholder).
 *
 * OCR emergence: -i reads the image geometry via ImageMagick, samples it
 *   to 16 scalars (one per sedenion dimension), and feeds those as the
 *   prompt geometry. When the geometry matches what is in the Zero Lattice
 *   the word emerges without pattern matching. Geometry-first, not pixel-first.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <ctype.h>
#include <stdint.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include "ptolemy.h"
#include "monad3c.h"        /* the three language centers, one mmap-able file */
#include "monad_harness.h"  /* the frame seam to the Python tabbed curses UI  */
#include "monad.h"          /* the Monad radio frames fold into via mh_pump  */

/* Directory containing the ptol binary (and ptol_layer.py). Set in main(). */
static char g_ptol_dir[512] = ".";

/* ── monad3_c.bin — the combined language store, mmap'd once ──────────────
 *
 * Phase 34 built monad3_c.bin (+ monad3c.h) as a fixed-offset, packed,
 * mmap-able merge of c_monad_wordnet.bin + monad_phonetic.bin +
 * monad_english.bin: one bsearch on the sorted WordRec table -> indices
 * into all three stores at once, plus the co-occurrence CSR. This is the
 * first, additive step of folding monad_combine.py into ptol.c: the
 * store is opened and directly queryable here (see the -M flag); the
 * get_monad_words() shell-out to ptol_layer.py is NOT yet replaced --
 * that needs the Python selection pipeline (radical_distance /
 * gamma_radial / basin / pruner) ported to C, the next increment.
 */
static const unsigned char  *g_m3     = NULL;   /* mmap base */
static size_t                 g_m3_len = 0;
static const Monad3cHeader   *g_m3h    = NULL;

static void monad3_open(void)
{
    char path[600];
    snprintf(path, sizeof(path), "%s/monad3_c.bin", g_ptol_dir);
    int fd = open(path, O_RDONLY);
    if (fd < 0) return;                      /* absent -> stay on ptol_layer.py */
    struct stat st;
    if (fstat(fd, &st) != 0 || (size_t)st.st_size < sizeof(Monad3cHeader)) {
        close(fd); return;
    }
    void *m = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (m == MAP_FAILED) return;
    if (memcmp(m, MONAD3C_MAGIC, 8) != 0) { munmap(m, (size_t)st.st_size); return; }
    g_m3     = (const unsigned char *)m;
    g_m3_len = (size_t)st.st_size;
    g_m3h    = (const Monad3cHeader *)m;
}

/* Lowercased bsearch on the WordRec table. Fills out[3] = {eng_idx,
 * wn_idx, phon_idx} (-1 where absent) and *degree = co-occurrence
 * out-degree (0 if no english entry). Returns 1 on hit, 0 on miss or if
 * the store is not open. Zero copy, zero alloc. */
static int monad3_lookup(const char *word, int32_t out[3], uint32_t *degree)
{
    out[0] = out[1] = out[2] = -1;
    if (degree) *degree = 0;
    if (!g_m3h) return 0;

    char w[128];
    size_t j = 0;
    for (const char *p = word; *p && j < sizeof(w) - 1; p++)
        w[j++] = (char)tolower((unsigned char)*p);
    w[j] = '\0';

    const char    *blob = (const char *)(g_m3 + g_m3h->off_wordblob);
    const WordRec *recs = (const WordRec *)(g_m3 + g_m3h->off_wordrec);
    long lo = 0, hi = (long)g_m3h->n_words - 1;
    while (lo <= hi) {
        long mid = (lo + hi) / 2;
        int c = strcmp(blob + recs[mid].name_off, w);
        if (c < 0)      lo = mid + 1;
        else if (c > 0) hi = mid - 1;
        else {
            out[0] = recs[mid].eng_idx;
            out[1] = recs[mid].wn_idx;
            out[2] = recs[mid].phon_idx;
            if (degree && out[0] >= 0) {
                const uint32_t *rp = (const uint32_t *)(g_m3 + g_m3h->off_rowptr);
                *degree = rp[out[0] + 1] - rp[out[0]];
            }
            return 1;
        }
    }
    return 0;
}

static const int P[16] = {
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53
};

/* ── Gamma-Radial Windspeed — the C port of wordnet_boxkite.py's own
 * gamma_radial(), 2026-09-21. Not the same Gamma console_speak() already
 * reports (that one is measure_gamma()'s sedenion-projection amplitude,
 * a different quantity by construction) — this is the WordNet-relational
 * fold FourthAgePapers/ScalarContextPropagation §7.3/§9.1 describes,
 * finally ported off the Python side it was verified on.
 *
 * CONTEXT_PRIMES[19] and the hyponyms-excluded LOG_ANCHOR are COPIED
 * exactly from wordnet_boxkite.py, not re-derived — any drift between the
 * two would silently produce two different numbers for the same word, and
 * nothing here would catch it. Cross-checked live, 2026-09-21:
 * monad3_gamma_radial() on "tree"'s stored vec19 == -0.151155, matching
 * the paper's own recorded windspeed("tree") to 6 decimal places. */
static const int GR_CONTEXT_PRIMES[19] = {
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167
};
#define GR_HYPONYMS_IDX 2   /* RELATION_METHODS.index('hyponyms'), wordnet_boxkite.py */

static double gr_log_anchor(void)
{
    static double anchor = -1.0;
    if (anchor < 0.0) {
        anchor = 0.0;
        for (int i = 0; i < 19; i++)
            if (i != GR_HYPONYMS_IDX) anchor += log((double)GR_CONTEXT_PRIMES[i]);
    }
    return anchor;
}

/* NAN where log_code<=0 (an all-zero relation vector) — same guard as the
 * Python. Caller checks with isnan(). */
static double monad3_gamma_radial(const int16_t vec[19])
{
    double log_code = 0.0;
    for (int i = 0; i < 19; i++)
        if (vec[i]) log_code += (double)vec[i] * log((double)GR_CONTEXT_PRIMES[i]);
    if (log_code <= 0.0) return NAN;
    return tanh(0.5 * log(log_code / gr_log_anchor()));
}

/* Convenience: lookup + extract + compute in one call. Returns 1 on a
 * store hit with a WordNet entry, 0 otherwise (out left at NAN either
 * way it isn't computed). Zero-copy — reads the mmap directly, same
 * struct layout -M already reads raw (word[32] pos[1] pad[3] offset[4]
 * vec[19] depth_weight[4] = 82 bytes, boxkite_bin.h). */
static int monad3_word_gamma_radial(const char *word, double *out)
{
    *out = NAN;
    int32_t ix[3]; uint32_t deg;
    if (!monad3_lookup(word, ix, &deg) || ix[1] < 0) return 0;
    const unsigned char *e = g_m3 + g_m3h->off_wn + (size_t)ix[1] * 82u;
    const int16_t *vec = (const int16_t *)(e + 40);
    *out = monad3_gamma_radial(vec);
    return 1;
}

/* ── Ptol's Eyes — (σ, θ) observation points on the sedenion tower ──────── */
/*
 * Each Eye fixes a tower level σ and an angular offset θ (multiples of π/8).
 * The aperture controls the auto-eye threshold relative to MONAD_GAP.
 *
 * Tower mapping (σ = 1 − k/4, geodesic tower result):
 *   R: σ=1.00  ℝ   — enumerable, 0°  spokes
 *   C: σ=0.75  ℂ   — relational, 0°  spokes (U(1), EM)
 *   H: σ=0.50  ℍ   — quaternion, 45° spokes (critical line, J_blue fires)
 *   O: σ=0.25  𝕆   — octonion,   0°  spokes
 *   S: σ=0.00  𝕊   — sedenion,   45° spokes (ZD boundary)
 *
 * J_blue shells (k=4-7, k=12-15) sit at θ=π/8 offsets — the 45° positions.
 * J_red  shells (k=0-3, k=8-11) sit at θ=0 positions — the 0°/90°/180°/270°.
 */
typedef struct {
    double sigma;
    double theta;      /* angular offset in radians */
    double aperture;   /* threshold factor relative to MONAD_GAP */
    char   name[4];
} PtolEye;

static const PtolEye TOWER_EYES[5] = {
    { 1.00, 0.0,           1.0, "R" },
    { 0.75, 0.0,           1.0, "C" },
    { 0.50, M_PI / 8.0,    1.0, "H" },
    { 0.25, 0.0,           1.0, "O" },
    { 0.00, M_PI / 8.0,    1.0, "S" },
};

static const PtolEye *eye_by_name(const char *n)
{
    for (int i = 0; i < 5; i++)
        if (TOWER_EYES[i].name[0] == n[0]) return &TOWER_EYES[i];
    return &TOWER_EYES[2]; /* default: H (σ=½) */
}

/* ── Sedenion basis angles: 16 spokes, optional θ offset ────────────────── */
static double spoke_angle(int k, double theta)
{
    return 2.0 * M_PI * (double)k / 16.0 - M_PI / 2.0 + theta;
}

/* ── Dirichlet projection ────────────────────────────────────────────────── */
/*
 * J_blue shells (k=4-7, k=12-15): sin channel — the return conductor.
 * J_red  shells (k=0-3, k=8-11): cos channel — the forward conductor.
 *
 * Together they form the complete Marx generator circuit.
 * J_red × J_blue = d* = 0.24600 — conserved at ALL σ (E=mc²).
 */
static double project(const unsigned char *s, int n, int k, double sig)
{
    double sum  = 0.0;
    double freq = 2.0 * M_PI / (double)P[k];
    int j_blue  = (k >= 4 && k <= 7) || (k >= 12 && k <= 15);
    for (int i = 1; i <= n; i++) {
        double phase = freq * (double)i;
        double w     = j_blue ? sin(phase) : cos(phase);
        sum += (double)s[i-1] * pow((double)i, -sig) * w;
    }
    return sum;
}

/* ── σ self-measurement — J_red power fraction ───────────────────────────── */
/*
 * With sin/cos duality, σ is the balance between J_red and J_blue power.
 *
 *   σ_self = P_red / (P_red + P_blue)
 *
 * where P_red  = Σ_{k ∈ {0-3, 8-11}}  v[k]²   (cos channels)
 *       P_blue = Σ_{k ∈ {4-7, 12-15}} v[k]²   (sin channels)
 *
 * At σ=1.0: cos terms dominate → P_red → 1  → σ_self → 1
 * At σ=0.5: balanced          → P_red ≈ ½  → σ_self ≈ ½
 * At σ=0.0: sin terms dominate → P_blue → 1 → σ_self → 0
 *
 * This is Holcus reading his own tower level from the J_red/J_blue ratio.
 * Works for any input length. Does not require Dirichlet asymptotic decay.
 */
static double measure_sigma(const double *v)
{
    double p_red = 0.0, p_blue = 0.0;
    for (int k = 0; k < 16; k++) {
        int j_blue = (k >= 4 && k <= 7) || (k >= 12 && k <= 15);
        if (j_blue) p_blue += v[k] * v[k];
        else        p_red  += v[k] * v[k];
    }
    double total = p_red + p_blue;
    if (total < 1e-15) return 0.5;
    return p_red / total;
}

/* ── The fold — Γ = tanh(u/2), the ADD:SCALE:SIGN word of the projection ── */
/*
 * Γ = (P_red − P_blue)/(P_red + P_blue) = 2·σ_self − 1  — the Smith-chart
 * reflection coefficient of the J_red/J_blue balance.
 * u = ln(P_red/P_blue) = 2·atanh(Γ)                     — the signed word
 *     length; SIGN = sign(u), SCALE = e^|u|, ADD = 0 (anchored at Eye H).
 * Γ = tanh(u/2) exactly. Γ = 0 ⟺ σ_self = ½ ⟺ ground state / the now.
 * Additive readout only — the projection and emission are unchanged.
 */
static void measure_gamma(const double *v, double *gamma_out, double *u_out)
{
    double sig = measure_sigma(v);              /* P_red / (P_red + P_blue) */
    double g   = 2.0 * sig - 1.0;               /* Γ ∈ (−1, 1)              */
    if (g >  0.999999999) g =  0.999999999;
    if (g < -0.999999999) g = -0.999999999;
    if (gamma_out) *gamma_out = g;
    if (u_out)     *u_out     = 2.0 * atanh(g); /* = ln(P_red/P_blue)       */
}

/* ── Comparator (ascending |x|, for spiral ZD→great circle) ─────────────── */

static int cmp_mag_asc(const void *a, const void *b)
{
    const int *ia = (const int *)a, *ib = (const int *)b;
    extern double _x[16];
    double da = fabs(_x[*ia]), db = fabs(_x[*ib]);
    return (da > db) - (da < db);
}

double _x[16];

/* ── Filename slug from prompt ───────────────────────────────────────────── */

static void make_slug(const char *prompt, char *slug, size_t sz)
{
    size_t j = 0;
    int words = 0;
    const char *p = prompt;
    while (*p && j < sz - 1 && words < 5) {
        if (*p == ' ' || *p == '\t') {
            if (j > 0 && slug[j-1] != '_') {
                slug[j++] = '_';
                words++;
            }
        } else if ((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') ||
                   (*p >= '0' && *p <= '9') || *p == '-') {
            slug[j++] = (char)(*p | 0x20); /* lowercase */
        }
        p++;
    }
    while (j > 0 && slug[j-1] == '_') j--;
    slug[j] = '\0';
    if (j == 0) { strncpy(slug, "ptol", sz); slug[sz-1] = '\0'; }
}

static void make_outpath(const char *dir, const char *slug, long ts,
                         const char *ext, char *out, size_t sz)
{
    if (dir && *dir)
        snprintf(out, sz, "%s/ptol_%s_%ld.%s", dir, slug, ts, ext);
    else
        snprintf(out, sz, "ptol_%s_%ld.%s", slug, ts, ext);
}

/* ── Monad layer — call ptol_layer.py, get element name + one word per dim ── */
/*
 * Writes normalised scalars + active primes to a tempfile, calls:
 *   python3 ptol_layer.py --stdin --words-only < tmpfile
 * Reads back: line 0 = element name (the monad that fired, e.g. "English"),
 *             lines 1..16 = one word per dimension k=0..15.
 * layer_elem receives the element name for the SVG <ElementName> tag.
 * On any failure words are zero-initialised and layer_elem is "English".
 */

static void get_monad_words(const double *v, const double *raw_x,
                             double thresh_raw,
                             char words[16][256], char layer_elem[64])
{
    strncpy(layer_elem, "English", 63); layer_elem[63] = '\0';

    char tmp[] = "/tmp/ptol_words_XXXXXX";
    int  fd    = mkstemp(tmp);
    if (fd < 0) return;

    FILE *tf = fdopen(fd, "w");
    if (!tf) { close(fd); return; }
    for (int k = 0; k < 16; k++)
        fprintf(tf, "%+.10f\n", v[k]);
    fprintf(tf, "---\n");
    for (int k = 0; k < 16; k++)
        if (fabs(raw_x[k]) >= thresh_raw)
            fprintf(tf, "%d\n", P[k]);
    fclose(tf);

    char cmd[1024];
    snprintf(cmd, sizeof(cmd),
        "python3 '%s/ptol_layer.py' --stdin --words-only < '%s' 2>/dev/null",
        g_ptol_dir, tmp);

    FILE *pipe = popen(cmd, "r");
    if (pipe) {
        /* Line 0: element name */
        char elem_line[64];
        if (fgets(elem_line, sizeof(elem_line), pipe)) {
            int l = (int)strlen(elem_line);
            if (l > 0 && elem_line[l-1] == '\n') elem_line[l-1] = '\0';
            if (elem_line[0] >= 'A' && elem_line[0] <= 'Z')
                strncpy(layer_elem, elem_line, 63);
        }
        /* Lines 1-16: words */
        for (int k = 0; k < 16; k++) {
            if (!fgets(words[k], 256, pipe)) break;
            int l = (int)strlen(words[k]);
            if (l > 0 && words[k][l-1] == '\n') words[k][l-1] = '\0';
        }
        pclose(pipe);
    }
    remove(tmp);
}

/* ── The sentence creator bridge — engine/grammar/ptolc_bridge.py ─────────
 *
 * get_monad_words() above is the GUARANTEED fallback: no dependency past
 * python3+nltk's already-downloaded corpora, always returns something. This
 * calls the real box-kite sentence creator (VerbNet sails + WordNet
 * hypernym-closure fill + the invariant SELRESTR gate, engine/grammar/) on
 * the SAME firing words + Γ that built the word bag; on any failure
 * (offline WordNet cache missing, an unknown verb, a bad schema) it prints
 * nothing and exits nonzero, and console_speak() keeps the word bag. As of
 * 2026-09-11 sentence mode is the DEFAULT voice, not an opt-in switch —
 * `out` is overwritten only on a clean, non-empty return, never left half
 * -built. */

/* Case-insensitive whole-word search: "how" must not fire inside "show". */
static int has_word(const char *hay, const char *word)
{
    size_t wl = strlen(word);
    const char *p = hay;
    while ((p = strstr(p, word)) != NULL) {
        int before_ok = (p == hay) || !isalpha((unsigned char)p[-1]);
        int after_ok  = !isalpha((unsigned char)p[wl]);
        if (before_ok && after_ok) return 1;
        p += wl;
    }
    return 0;
}

/* The "small wh-word scan" from the design pass: everything console_speak()
 * needs for a ParseSpec except this comes straight off the geometry
 * already (topic words from the firing shells, depth from Γ) — only the
 * speech act still lives in the surface text of the prompt. Heuristic, not
 * a parser: on a miss it lands on "what_does_X_do", the most general act,
 * never on a value the schema would reject (ptolc_bridge.py re-validates
 * against SCHEMA["speech_acts"] regardless). */
static void infer_speech_act(const char *prompt, char act[24])
{
    char p[512];
    size_t j = 0;
    for (const char *s = prompt; *s && j < sizeof(p) - 1; s++)
        p[j++] = (char)tolower((unsigned char)*s);
    p[j] = '\0';

    if (has_word(p, "why"))    { strcpy(act, "why");    return; }
    if (has_word(p, "how"))    { strcpy(act, "how");    return; }
    if (has_word(p, "where"))  { strcpy(act, "where");  return; }
    if (has_word(p, "who"))    { strcpy(act, "who_Xs"); return; }
    if (has_word(p, "what")) {
        strcpy(act, (has_word(p, "do") || has_word(p, "does") || has_word(p, "did"))
                    ? "what_does_X_do" : "define_X");
        return;
    }
    if (has_word(p, "define")) { strcpy(act, "define_X"); return; }
    if (p[0]) {
        char first[16] = {0};
        sscanf(p, "%15s", first);
        static const char *YESNO[] = {"is","are","was","were","do","does",
                                       "did","can","will","would","has","have"};
        for (size_t i = 0; i < sizeof(YESNO) / sizeof(YESNO[0]); i++)
            if (strcmp(first, YESNO[i]) == 0) { strcpy(act, "yesno"); return; }
    }
    strcpy(act, "what_does_X_do");
}

/* seen[0..nseen) is console_speak()'s already-deduped firing word list
 * (topic words + a candidate verb, spiral order); gamma is Γ from
 * measure_gamma(). Writes them to a tempfile in the bridge's line format,
 * pipes through ptolc_bridge.py (run from the VAPMIP root, one level above
 * g_ptol_dir, so its package-relative imports resolve), and reads back one
 * line. Returns 1 and fills out[1024] on a clean, non-empty, exit-0 result;
 * 0 otherwise (out left untouched). */
static int get_monad_sentence(double gamma, const char *act,
                               char seen[16][64], int nseen,
                               char out[1024])
{
    char tmp[] = "/tmp/ptol_sentence_XXXXXX";
    int fd = mkstemp(tmp);
    if (fd < 0) return 0;
    FILE *tf = fdopen(fd, "w");
    if (!tf) { close(fd); remove(tmp); return 0; }
    fprintf(tf, "GAMMA %+.10f\n", gamma);
    fprintf(tf, "ACT %s\n", act);
    fprintf(tf, "WORDS");
    for (int i = 0; i < nseen; i++) fprintf(tf, " %s", seen[i]);
    fprintf(tf, "\n");
    fclose(tf);

    char cmd[1024];
    snprintf(cmd, sizeof(cmd),
        "cd '%s/..' && python3 -m engine.grammar.ptolc_bridge < '%s' 2>/dev/null",
        g_ptol_dir, tmp);

    int ok = 0;
    FILE *pipe = popen(cmd, "r");
    if (pipe) {
        if (fgets(out, 1024, pipe)) {
            size_t l = strlen(out);
            if (l > 0 && out[l - 1] == '\n') out[--l] = '\0';
            if (l > 0) ok = 1;
        }
        int status = pclose(pipe);
        if (!(status >= 0 && WIFEXITED(status) && WEXITSTATUS(status) == 0))
            ok = 0;
    }
    remove(tmp);
    return ok;
}

/* ── SVG paper — the pathway ─────────────────────────────────────────────── */
/*
 * 16-spoke polar web. Each spoke k points at spoke_angle(k).
 * Radius of tip = |v[k]| × R_max.   Sign: red (+), blue (−).
 * Spiral path: connect tips in ascending |x| order (ZD → great circle).
 * Active prime spokes (|x_k| >= thresh) drawn bold.
 *
 * <English> operator: for active spokes, emit a bare <English> XML element
 * at the amplitude dot position — no fill, no definition. monad_English.bin
 * is the source; the geometry decides whether it fires. The SVG source IS
 * the architecture. The render is the shadow.
 */

static int write_svg(const char *path, const double *v, const int *idx,
                     double thresh_norm, const char *prompt,
                     const char words[16][256], const char *layer_elem)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return 0; }

    const int W = 500, H = 520;
    const double CX = 250.0, CY = 260.0, R = 210.0;

    fprintf(f, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    fprintf(f, "<svg xmlns=\"http://www.w3.org/2000/svg\" "
               "width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\">\n", W, H, W, H);

    /* Background */
    fprintf(f, "  <rect width=\"%d\" height=\"%d\" fill=\"#0a0a0a\"/>\n", W, H);

    /* Prompt label */
    char safe[256];
    size_t si = 0;
    for (const char *p = prompt; *p && si < sizeof(safe)-5; p++) {
        if (*p == '<') { memcpy(safe+si, "&lt;", 4); si+=4; }
        else if (*p == '>') { memcpy(safe+si, "&gt;", 4); si+=4; }
        else if (*p == '&') { memcpy(safe+si, "&amp;", 5); si+=5; }
        else safe[si++] = *p;
    }
    safe[si] = '\0';
    fprintf(f, "  <text x=\"%d\" y=\"16\" font-family=\"monospace\" "
               "font-size=\"11\" fill=\"#444\" text-anchor=\"middle\">%s</text>\n",
               W/2, safe);

    /* Concentric reference circles at R/4, R/2, 3R/4, R */
    for (int r = 1; r <= 4; r++) {
        fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"%.1f\" "
                   "fill=\"none\" stroke=\"#222\" stroke-width=\"0.5\"/>\n",
                   CX, CY, R * r / 4.0);
    }

    /* σ=½ circle (the escape threshold) — at R/2 */
    fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"%.1f\" "
               "fill=\"none\" stroke=\"#2a4a2a\" stroke-width=\"1\" "
               "stroke-dasharray=\"4,4\"/>\n", CX, CY, R * 0.5);
    fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
               "font-size=\"8\" fill=\"#2a4a2a\" text-anchor=\"start\">"
               "σ=½</text>\n", CX + R*0.5 + 2, CY);

    /* Spokes, amplitude dots, and English word labels */
    for (int k = 0; k < 16; k++) {
        double a    = spoke_angle(k, 0.0);
        double tip_r = fabs(v[k]) * R;
        double tx   = CX + cos(a) * R;
        double ty   = CY + sin(a) * R;
        int active  = (fabs(v[k]) >= thresh_norm);

        /* Spoke line */
        fprintf(f, "  <line x1=\"%.2f\" y1=\"%.2f\" x2=\"%.2f\" y2=\"%.2f\" "
                   "stroke=\"%s\" stroke-width=\"%.1f\"/>\n",
                   CX, CY, tx, ty,
                   active ? "#333" : "#1a1a1a",
                   active ? 0.8 : 0.4);

        /* Amplitude dot */
        if (tip_r > 1.0) {
            double dx = CX + cos(a) * tip_r;
            double dy = CY + sin(a) * tip_r;
            const char *col = (v[k] >= 0) ? "#c04040" : "#4060c0";
            fprintf(f, "  <circle cx=\"%.2f\" cy=\"%.2f\" r=\"%.1f\" "
                       "fill=\"%s\" opacity=\"0.9\"/>\n",
                       dx, dy, active ? 4.0 : 2.5, col);
        }

        /* English word at spoke tip — the shadow on the wall of primes */
        const char *word = words ? words[k] : NULL;
        char wsvg[64]; wsvg[0] = '\0';
        if (word && word[0]) {
            /* Truncate + XML-escape for SVG */
            int wi = 0;
            const char *wp = word;
            int chars = 0;
            while (*wp && chars < 13 && wi < 58) {
                if      (*wp == '<') { memcpy(wsvg+wi,"&lt;",4); wi+=4; }
                else if (*wp == '>') { memcpy(wsvg+wi,"&gt;",4); wi+=4; }
                else if (*wp == '&') { memcpy(wsvg+wi,"&amp;",5); wi+=5; }
                else                 wsvg[wi++] = *wp;
                chars++; wp++;
            }
            if (*wp) { memcpy(wsvg+wi,"…",3); wi+=3; } /* UTF-8 ellipsis */
            wsvg[wi] = '\0';

            double lx = CX + cos(a) * (R + 16);
            double ly = CY + sin(a) * (R + 16);
            if (active) {
                /* Active: green word — the path lands here */
                fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                           "font-size=\"10\" fill=\"#40a060\" font-weight=\"bold\" "
                           "text-anchor=\"middle\" dominant-baseline=\"central\">"
                           "%s</text>\n", lx, ly, wsvg);
            } else {
                /* Inactive: dim word — present but below threshold */
                fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                           "font-size=\"8\" fill=\"#2a2a2a\" "
                           "text-anchor=\"middle\" dominant-baseline=\"central\">"
                           "%s</text>\n", lx, ly, wsvg);
            }
        } else {
            /* No word: fall back to prime label */
            double lx = CX + cos(a) * (R + 14);
            double ly = CY + sin(a) * (R + 14);
            fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                       "font-size=\"9\" fill=\"%s\" text-anchor=\"middle\" "
                       "dominant-baseline=\"central\">p%d</text>\n",
                       lx, ly, active ? "#666" : "#2a2a2a", P[k]);
        }

        /* <Monad> element — bare XML at amplitude dot. No fill. No definition.
         * Element name = the monad that fired. The geometry chose it. */
        if (active && word && word[0] && tip_r > 1.0) {
            double ex = CX + cos(a) * tip_r;
            double ey = CY + sin(a) * tip_r;
            fprintf(f, "  <%s x=\"%.2f\" y=\"%.2f\">%s</%s>\n",
                       layer_elem, ex, ey, wsvg, layer_elem);
        }
    }

    /* Spiral path: connect tips in ZD→great circle order */
    fprintf(f, "  <polyline fill=\"none\" stroke=\"#40a060\" "
               "stroke-width=\"1.2\" opacity=\"0.8\" points=\"");
    /* Start at centre (ZD) */
    fprintf(f, "%.2f,%.2f", CX, CY);
    for (int i = 0; i < 16; i++) {
        int k = idx[i];
        double a = spoke_angle(k, 0.0);
        double r = fabs(v[k]) * R;
        fprintf(f, " %.2f,%.2f", CX + cos(a)*r, CY + sin(a)*r);
    }
    fprintf(f, "\"/>\n");

    /* ZD marker (centre) */
    fprintf(f, "  <circle cx=\"%.1f\" cy=\"%.1f\" r=\"3\" "
               "fill=\"#806020\" opacity=\"0.9\"/>\n", CX, CY);
    fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
               "font-size=\"8\" fill=\"#806020\" text-anchor=\"middle\">ZD</text>\n",
               CX, CY + 12);

    /* e_k labels at amplitude tips (inner, readable) */
    for (int k = 0; k < 16; k++) {
        double a = spoke_angle(k, 0.0);
        double r = fabs(v[k]) * R;
        if (r < 8.0) continue;
        double lx = CX + cos(a) * (r * 0.6);
        double ly = CY + sin(a) * (r * 0.6);
        fprintf(f, "  <text x=\"%.1f\" y=\"%.1f\" font-family=\"monospace\" "
                   "font-size=\"7\" fill=\"#555\" text-anchor=\"middle\" "
                   "dominant-baseline=\"central\">e%d</text>\n", lx, ly, k);
    }

    fprintf(f, "</svg>\n");
    fclose(f);
    return 1;
}

/* ── PPM bitmap paper — the field ────────────────────────────────────────── */
/*
 * 4×4 grid (16 cells), one per sedenion dimension k.
 * Cell layout: k=0 top-left, row-major.
 * R channel: positive amplitude   (v[k] > 0)
 * B channel: negative amplitude   (v[k] < 0)
 * G channel: activity (above threshold)
 * Upscaled ×16 to 64×64 by nearest-neighbour.
 */

#define PPM_CELL  16
#define PPM_GRID   4
#define PPM_SZ    (PPM_CELL * PPM_GRID)

static int write_ppm(const char *path, const double *v, double thresh_norm)
{
    unsigned char img[PPM_SZ][PPM_SZ][3];
    memset(img, 0, sizeof(img));

    for (int k = 0; k < 16; k++) {
        int row = k / PPM_GRID;
        int col = k % PPM_GRID;
        int py0 = row * PPM_CELL, px0 = col * PPM_CELL;
        double amp = fabs(v[k]);
        int bright = (int)(amp * 255.0 + 0.5);
        if (bright > 255) bright = 255;
        int active = (amp >= thresh_norm);

        unsigned char R = (v[k] >= 0) ? (unsigned char)bright : 0;
        unsigned char B = (v[k] <  0) ? (unsigned char)bright : 0;
        unsigned char G = active ? (unsigned char)(bright / 3) : 0;

        for (int dy = 1; dy < PPM_CELL-1; dy++)
            for (int dx = 1; dx < PPM_CELL-1; dx++) {
                img[py0+dy][px0+dx][0] = R;
                img[py0+dy][px0+dx][1] = G;
                img[py0+dy][px0+dx][2] = B;
            }
        /* Cell border */
        for (int d = 0; d < PPM_CELL; d++) {
            img[py0][px0+d][0] = img[py0][px0+d][1] = img[py0][px0+d][2] = 0x18;
            img[py0+PPM_CELL-1][px0+d][0] = img[py0+PPM_CELL-1][px0+d][1] =
                img[py0+PPM_CELL-1][px0+d][2] = 0x18;
            img[py0+d][px0][0] = img[py0+d][px0][1] = img[py0+d][px0][2] = 0x18;
            img[py0+d][px0+PPM_CELL-1][0] = img[py0+d][px0+PPM_CELL-1][1] =
                img[py0+d][px0+PPM_CELL-1][2] = 0x18;
        }
    }

    FILE *f = fopen(path, "wb");
    if (!f) { perror(path); return 0; }
    fprintf(f, "P6\n%d %d\n255\n", PPM_SZ, PPM_SZ);
    for (int y = 0; y < PPM_SZ; y++)
        for (int x = 0; x < PPM_SZ; x++)
            fwrite(img[y][x], 1, 3, f);
    fclose(f);
    return 1;
}

/* ── HTML paper — pathway + field + shadow text ──────────────────────────── */

static int write_html(const char *html_path, const char *svg_path,
                      const char *ppm_path, const double *v, const int *idx,
                      const int *P16, double thresh_norm, const char *prompt,
                      const char words[16][256])
{
    /* Convert PPM to PNG via ImageMagick if available, embed SVG inline. */
    char png_path[512];
    snprintf(png_path, sizeof(png_path), "%.507s.png", ppm_path);
    char cmd[2048];
    snprintf(cmd, sizeof(cmd), "convert '%.500s' '%.500s' 2>/dev/null", ppm_path, png_path);
    if (system(cmd)) { /* ImageMagick PNG conversion optional */ }

    FILE *f = fopen(html_path, "w");
    if (!f) { perror(html_path); return 0; }

    fprintf(f, "<!DOCTYPE html><html><head>\n");
    fprintf(f, "<meta charset=\"UTF-8\">\n");
    fprintf(f, "<title>ptol: %s</title>\n", prompt);
    fprintf(f, "<style>\n"
               "body{background:#0a0a0a;color:#aaa;font-family:monospace;"
               "max-width:900px;margin:2em auto;padding:1em}\n"
               "h1{font-size:1em;color:#555;font-weight:normal}\n"
               ".papers{display:flex;gap:2em;align-items:flex-start}\n"
               ".paper{border:1px solid #222;padding:0.5em}\n"
               ".paper p{font-size:0.7em;color:#333;margin:0.3em 0 0}\n"
               ".shadow{margin-top:2em;border-top:1px solid #222;padding-top:1em}\n"
               ".spiral{color:#40a060;letter-spacing:0.05em}\n"
               "table{border-collapse:collapse;font-size:0.8em}\n"
               "td{padding:2px 6px;border:1px solid #1a1a1a}\n"
               ".pos{color:#c04040}.neg{color:#4060c0}.act{font-weight:bold}\n"
               "</style></head><body>\n");

    fprintf(f, "<h1>σ: %s</h1>\n", prompt);
    fprintf(f, "<div class=\"papers\">\n");

    /* SVG paper (inline — read the SVG file) */
    fprintf(f, "  <div class=\"paper\">\n");
    FILE *svgf = fopen(svg_path, "r");
    if (svgf) {
        char buf[4096]; size_t nr;
        while ((nr = fread(buf, 1, sizeof(buf), svgf)) > 0)
            fwrite(buf, 1, nr, f);
        fclose(svgf);
    } else {
        fprintf(f, "  <p>[SVG not found]</p>\n");
    }
    fprintf(f, "  <p>pathway — spiral ZD → great circle</p>\n");
    fprintf(f, "  </div>\n");

    /* PPM/PNG paper */
    fprintf(f, "  <div class=\"paper\">\n");
    /* Try PNG first, fall back to nothing */
    fprintf(f, "  <img src=\"%s\" width=\"128\" height=\"128\" "
               "style=\"image-rendering:pixelated\" alt=\"sedenion field\">\n",
               png_path);
    fprintf(f, "  <p>field — 16 scalar amplitudes<br>"
               "red=+, blue=−, green=active</p>\n");
    fprintf(f, "  </div>\n");
    fprintf(f, "</div>\n");

    /* Sedenion table with English words */
    fprintf(f, "<div class=\"shadow\">\n");
    fprintf(f, "<table><tr><th>k</th><th>p_k</th><th>e_k</th>"
               "<th>scalar</th><th>active</th><th>word</th></tr>\n");
    for (int k = 0; k < 16; k++) {
        int active = (fabs(v[k]) >= thresh_norm);
        const char *cls = (v[k] >= 0) ? "pos" : "neg";
        if (active) cls = "act";
        const char *word = (words && words[k][0]) ? words[k] : "";
        fprintf(f, "<tr><td>%d</td><td>%d</td>"
                   "<td class=\"%s\">e%d</td>"
                   "<td class=\"%s\">%+.6f</td>"
                   "<td>%s</td>"
                   "<td class=\"%s\">%s</td></tr>\n",
                   k, P16[k], cls, k, cls, v[k],
                   active ? "●" : "",
                   active ? "act" : "", word);
    }
    fprintf(f, "</table>\n");

    /* Spiral path with English words */
    fprintf(f, "<p class=\"spiral\">path (ZD → great circle):<br>");
    const char *last_word = NULL;
    for (int i = 0; i < 16; i++) {
        int k = idx[i];
        int active = (fabs(v[k]) >= thresh_norm);
        const char *word = (words && words[k][0]) ? words[k] : NULL;
        if (word) {
            if (active)
                fprintf(f, "<strong style=\"color:#40a060\">%s</strong>", word);
            else
                fprintf(f, "<span style=\"color:#444\">%s</span>", word);
            if (i < 15) fprintf(f, " → ");
            last_word = words[k];
        } else {
            fprintf(f, "e%d(%+.3f)%s", k, v[k], i < 15 ? " → " : "");
        }
    }
    fprintf(f, "</p>\n");

    /* Response: the word the path lands at */
    if (last_word && last_word[0]) {
        fprintf(f, "<p style=\"font-size:1.4em;color:#40a060;"
                   "border-left:2px solid #40a060;padding-left:0.8em;"
                   "margin-top:1em\">%s</p>\n", last_word);
    }

    fprintf(f, "</div>\n</body></html>\n");

    fclose(f);
    return 1;
}

/* ── Image reading — geometry-first OCR ─────────────────────────────────── */
/*
 * Use ImageMagick to resample the image to 16×1 pixels, then read each
 * pixel's brightness as a sedenion scalar. Sign is encoded by hue:
 * red-dominant → positive, blue-dominant → negative.
 *
 * When the geometry of the image matches what is in the Zero Lattice,
 * the word emerges. OCR without pattern matching — geometry recognition.
 */

static int read_image_scalars(const char *img_path, double *v_out)
{
    char cmd[2048];
    char tmpfile[] = "/tmp/ptol_ocr_XXXXXX";
    int fd = mkstemp(tmpfile);
    if (fd < 0) { perror("mkstemp"); return 0; }
    close(fd);

    /* Resample to 16×1, output as text RGB */
    snprintf(cmd, sizeof(cmd),
        "convert \"%s\" -colorspace sRGB -resize 16x1! -depth 8 "
        "-format \"%%[fx:p{%%[fx:i]}.u.r] %%[fx:p{%%[fx:i]}.u.g] "
        "%%[fx:p{%%[fx:i]}.u.b]\\n\" info:- 2>/dev/null > \"%s\"",
        img_path, tmpfile);

    /* Simpler: use txt: format */
    snprintf(cmd, sizeof(cmd),
        "convert \"%s\" -colorspace sRGB -resize 16x1! -depth 8 txt:- "
        "2>/dev/null | grep -v '#' > \"%s\"",
        img_path, tmpfile);

    if (system(cmd) != 0) {
        fprintf(stderr, "ptol: ImageMagick 'convert' failed on %s\n", img_path);
        fprintf(stderr, "ptol: install ImageMagick: sudo apt install imagemagick\n");
        remove(tmpfile);
        return 0;
    }

    FILE *tf = fopen(tmpfile, "r");
    if (!tf) { perror(tmpfile); remove(tmpfile); return 0; }

    char line[256];
    int k = 0;
    while (k < 16 && fgets(line, sizeof(line), tf)) {
        /* txt: format: "x,y: (R,G,B)  #RRGGBB  ..." */
        int r = 0, g = 0, b = 0;
        if (sscanf(line, "%*d,%*d: (%d,%d,%d)", &r, &g, &b) == 3 ||
            sscanf(line, "%*d,%*d: (%d,%d,%d,", &r, &g, &b) == 3) {
            double brightness = (r + g + b) / (3.0 * 255.0);
            /* Sign from hue: red-dominant → +, blue-dominant → − */
            double sign = (r >= b) ? 1.0 : -1.0;
            v_out[k] = sign * brightness;
            k++;
        }
    }
    fclose(tf);
    remove(tmpfile);

    if (k < 16) {
        fprintf(stderr, "ptol: only read %d scalars from image (need 16)\n", k);
        return 0;
    }
    return 1;
}

/* ── ptol -w : the resident speaking monad behind the tabbed curses UI ──────
 *
 * console_speak() is the sentence-mode voice: project the prompt onto the 16
 * sedenion shells at Eye H (σ=½), threshold at peak/φ, walk the active shells
 * in spiral order (ZD → great circle) and hand back that word shadow plus the
 * measured (σ_self, Γ) and the firing primes. The Python Chat Tab renders it;
 * `/paragraph` there layers semantic_paragraph.py's paragraph grammar on top.
 *
 * run_console() forks ptolemy_console.py onto the tty (it draws curses) and
 * keeps this process on the other end of a socketpair, answering `say`/`cmd`/
 * `mode`/`ping` frames through monad_harness.c until the console quits.
 */
#ifndef PTOL_LIBRARY
/* ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
 * THE CHILD'S VOICE  (2026-11-25) -- the C port of the Python monad built and tested that day:
 *   sedenion_window.py (window, Tone7, markers, imitation, web revisit), lyndon_conjugation.py (the verb group), tenseplan.py,
 *   weave_cycle.py (web_step), scaled_boxkite_orbweaver_monad.py, monad.cam_encode.
 * "This is a child we have to teach how to speak English."  Every sentence is picked word by word by the window; connectives are the only
 * prose that is not picked.  Numbers are not words: they never get here (monad_harness.c takes them out first).
 * Python is the test bench (tests/test_c_parity.py, `ptol -P` probe); where the C store cannot do what Python's WordNet does, the difference is
 * stated at the function: no senses (one first-sense entry per word in monad3_c.bin), neighbours come from the co-occurrence matrix, connective
 * choice is a fixed rotation (not Python's random), the general-English prior is the corpus unigram (not Brown).
 * ═══════════════════════════════════════════════════════════════════════════════════════════════════════════ */

/* BEGIN GENERATED ptol_voice_data */
/* irregular or rule-breaking verb forms: lemma, VBD, VBN, VBG, VBZ (from lemminflect; every lemma the regular rules get right is left out) */
static const char *const VERB_FORMS[][5] = {
    {"abet","abetted","abetted","abetting","abets"},
    {"abhor","abhorred","abhorred","abhorring","abhors"},
    {"abut","abutted","abutted","abutting","abuts"},
    {"acquit","acquitted","acquitted","acquitting","acquits"},
    {"admit","admitted","admitted","admitting","admits"},
    {"alight","alighted","alit","alighting","alights"},
    {"allot","allotted","allotted","allotting","allots"},
    {"annul","annulled","annulled","annulling","annuls"},
    {"apparel","apparelled","apparelled","appareling","apparels"},
    {"arise","arose","arisen","arising","arises"},
    {"aver","averred","averred","averring","avers"},
    {"awake","awoke","awoken","awaking","awakes"},
    {"awe","awed","awed","aweing","awes"},
    {"baa","baaaed","baaaed","baaaing","baas"},
    {"backbite","backbit","backbitten","backbiting","backbites"},
    {"backlog","backlogged","backlogged","backlogging","backlogs"},
    {"backslap","backslapped","backslapped","backslapping","backslaps"},
    {"backslide","backslid","backslidden","backsliding","backslides"},
    {"backstop","backstopped","backstopped","backstopping","backstops"},
    {"be","was","been","being","is"},
    {"bear","bore","born","bearing","bears"},
    {"beat","beat","beaten","beating","beats"},
    {"bebop","bebopped","bebopped","bebopping","bebops"},
    {"become","became","become","becoming","becomes"},
    {"bedim","bedimmed","bedimmed","bedimming","bedims"},
    {"befall","befell","befallen","befalling","befalls"},
    {"befit","befitted","befitted","befitting","befits"},
    {"befog","befogged","befogged","befogging","befogs"},
    {"beget","begot","begotten","begetting","begets"},
    {"begin","began","begun","beginning","begins"},
    {"behold","beheld","beheld","beholding","beholds"},
    {"bend","bent","bent","bending","bends"},
    {"bereave","bereft","bereft","bereaving","bereaves"},
    {"beseech","besought","besought","beseeching","beseeches"},
    {"beset","beset","beset","besetting","besets"},
    {"bespeak","bespoke","bespoken","bespeaking","bespeaks"},
    {"bestir","bestirred","bestirred","bestirring","bestirs"},
    {"bestride","betrode","bestridden","bestriding","bestrides"},
    {"bet","bet","bet","betting","bets"},
    {"bevel","beveled","beveled","bevelling","bevels"},
    {"bias","biased","biassed","biasing","biases"},
    {"bid","bade","bid","bidding","bids"},
    {"bide","boded","boded","biding","bides"},
    {"bind","bound","bound","binding","binds"},
    {"binge","binged","binged","bingeing","binges"},
    {"bite","bit","bitten","biting","bites"},
    {"bivouac","bivouacked","bivouacked","bivouacking","bivouacs"},
    {"blackleg","blacklegged","blacklegged","blacklegging","blacklegs"},
    {"bleed","bled","bled","bleeding","bleeds"},
    {"blend","blended","blent","blending","blends"},
    {"blow","blew","blown","blowing","blows"},
    {"blue","blued","blued","blueing","blues"},
    {"bobsled","bobsledded","bobsledded","bobsledding","bobsleds"},
    {"bootleg","bootlegged","bootlegged","bootlegging","bootlegs"},
    {"bootstrap","bootstrapped","bootstrapped","bootstrapping","bootstraps"},
    {"break","broke","broken","breaking","breaks"},
    {"breed","bred","bred","breeding","breeds"},
    {"bring","brought","brought","bringing","brings"},
    {"broadcast","broadcasted","broadcast","broadcasting","broadcasts"},
    {"browbeat","browbeat","browbeaten","browbeating","browbeats"},
    {"buckram","buckrammed","buckrammed","buckramming","buckrams"},
    {"build","built","built","building","builds"},
    {"burst","burst","burst","bursting","bursts"},
    {"bus","bused","bussed","busing","buses"},
    {"bust","busted","bust","busting","busts"},
    {"buy","bought","bought","buying","buys"},
    {"can","could","could","canning","cans"},
    {"caravan","caravaned","caravaned","caravanning","caravans"},
    {"carol","carolled","carolled","caroling","carols"},
    {"cast","cast","cast","casting","casts"},
    {"catch","caught","caught","catching","catches"},
    {"catnap","catnapped","catnapped","catnapping","catnaps"},
    {"cavil","cavilled","cavilled","cavilling","cavils"},
    {"channel","channeled","channelled","channeling","channels"},
    {"chisel","chiseled","chiseled","chiselling","chisels"},
    {"choose","chose","chosen","choosing","chooses"},
    {"cleave","cleft","cleft","cleaving","cleaves"},
    {"cling","clung","clung","clinging","clings"},
    {"come","came","come","coming","comes"},
    {"commit","committed","committed","committing","commits"},
    {"compel","compelled","compelled","compelling","compels"},
    {"concur","concurred","concurred","concurring","concurs"},
    {"confab","confabbed","confabbed","confabbing","confabs"},
    {"confer","conferred","conferred","conferring","confers"},
    {"control","controlled","controlled","controlling","controls"},
    {"corral","corralled","corralled","corralling","corrals"},
    {"cost","cost","cost","costing","costs"},
    {"counsel","counselled","counselled","counseling","counsels"},
    {"countersink","countersank","countersunk","countersinking","countersinks"},
    {"creep","crept","crept","creeping","creeps"},
    {"crossbreed","cross-bred","crossbred","crossbreeding","crossbreeds"},
    {"cudgel","cudgelled","cudgelled","cudgelling","cudgels"},
    {"cue","cued","cued","cueing","cues"},
    {"cut","cut","cut","cutting","cuts"},
    {"cypher","cyphered","cyphered","cyphering","cyphers"},
    {"dado","dadoed","dadoed","dadoing","dadoes"},
    {"deal","dealt","dealt","dealing","deals"},
    {"debar","debarred","debarred","debarring","debars"},
    {"debug","debugged","debugged","debugging","debugs"},
    {"defat","defatted","defatted","defatting","defats"},
    {"defer","deferred","deferred","deferring","defers"},
    {"defog","defogged","defogged","defogging","defogs"},
    {"demob","demobbed","demobbed","demobbing","demobs"},
    {"demur","demurred","demurred","demurring","demurs"},
    {"deter","deterred","deterred","deterring","deters"},
    {"devil","devilled","devilled","devilling","devils"},
    {"diagram","diagramed","diagramed","diagramming","diagrams"},
    {"dial","dialed","dialled","dialing","dials"},
    {"dig","dug","dug","digging","digs"},
    {"disbar","disbarred","disbarred","disbarring","disbars"},
    {"disbud","disbudded","disbudded","disbudding","disbuds"},
    {"disembowel","disembowelled","disembowelled","disembowelling","disembowels"},
    {"dishevel","dishevelled","dishevelled","disheveling","dishevels"},
    {"disinter","disinterred","disinterred","disinterring","disinters"},
    {"dispel","dispelled","dispelled","dispelling","dispels"},
    {"disprove","disproved","disproven","disproving","disproves"},
    {"distil","distilled","distilled","distilling","distills"},
    {"do","did","done","doing","does"},
    {"draw","drew","drawn","drawing","draws"},
    {"drink","drank","drunk","drinking","drinks"},
    {"drive","drove","driven","driving","drives"},
    {"drivel","driveled","driveled","drivelling","drivels"},
    {"duel","dueled","duelled","dueling","duels"},
    {"dwell","dwelt","dwelt","dwelling","dwells"},
    {"eat","ate","eaten","eating","eats"},
    {"eavesdrop","eavesdropped","eavesdropped","eavesdropping","eavesdrops"},
    {"echo","echoed","echoed","echoing","echoes"},
    {"embargo","embargoed","embargoed","embargoing","embargoes"},
    {"embed","embedded","embedded","embedding","embeds"},
    {"emit","emitted","emitted","emitting","emits"},
    {"empanel","empanelled","empanelled","empaneling","empanels"},
    {"enamel","enamelled","enamelled","enamelling","enamels"},
    {"englut","englutted","englutted","englutting","engluts"},
    {"entrap","entrapped","entrapped","entrapping","entraps"},
    {"enwrap","enwrapped","enwrapped","enwrapping","enwraps"},
    {"equal","equalled","equalled","equalling","equals"},
    {"equip","equipped","equipped","equipping","equips"},
    {"excel","excelled","excelled","excelling","excels"},
    {"expel","expelled","expelled","expelling","expels"},
    {"extol","extolled","extolled","extolling","extols"},
    {"fall","fell","fallen","falling","falls"},
    {"fee","fee'd","feed","feeing","fees"},
    {"feed","fed","fed","feeding","feeds"},
    {"feel","felt","felt","feeling","feels"},
    {"fight","fought","fought","fighting","fights"},
    {"find","found","found","finding","finds"},
    {"fit","fit","fitted","fitting","fits"},
    {"flee","fled","fled","fleeing","flees"},
    {"fling","flung","flung","flinging","flings"},
    {"floodlight","floodlighted","floodlit","floodlighting","floodlights"},
    {"fly","flew","flown","flying","flies"},
    {"forbear","forbore","forborne","forbearing","forbears"},
    {"forbid","forbade","forbidden","forbidding","forbids"},
    {"forecast","forecasted","forecast","forecasting","forecasts"},
    {"forego","forewent","forgone","foregoing","forgoes"},
    {"foresee","foresaw","foreseen","foreseeing","foresees"},
    {"foreswear","forswore","forsworn","forswearing","forswears"},
    {"foretell","foretold","foretold","foretelling","foretells"},
    {"forget","forgot","forgotten","forgetting","forgets"},
    {"forgive","forgave","forgiven","forgiving","forgives"},
    {"forgo","forewent","forgone","foregoing","forgoes"},
    {"format","formatted","formatted","formatting","formats"},
    {"forsake","forsook","forsaken","forsaking","forsakes"},
    {"forswear","forswore","forsworn","forswearing","forswears"},
    {"freeze","froze","frozen","freezing","freezes"},
    {"frolic","frolicked","frolicked","frolicking","frolics"},
    {"fulfil","fulfilled","fulfilled","fulfilling","fulfills"},
    {"gainsay","gainsaid","gainsaid","gainsaying","gainsays"},
    {"gambol","gambolled","gambolled","gambolling","gambols"},
    {"get","got","gotten","getting","gets"},
    {"ghostwrite","ghost-wrote","ghostwritten","ghostwriting","ghost-writes"},
    {"gird","girded","girt","girding","girds"},
    {"give","gave","given","giving","gives"},
    {"go","went","gone","going","goes"},
    {"gown","gowned","gown","gowning","gowns"},
    {"gravel","graveled","graveled","gravelling","gravels"},
    {"grind","ground","ground","grinding","grinds"},
    {"grok","groked","groked","groking","groks"},
    {"grovel","grovelled","grovelled","grovelling","grovels"},
    {"grow","grew","grown","growing","grows"},
    {"gyp","gypped","gypped","gypping","gyps"},
    {"hamstring","hamstrung","hamstrung","hamstringing","hamstrings"},
    {"handicap","handicapped","handicapped","handicapping","handicaps"},
    {"hang","hung","hung","hanging","hangs"},
    {"have","had","had","having","has"},
    {"hear","heard","heard","hearing","hears"},
    {"heave","heaved","hove","heaving","heaves"},
    {"hew","hewed","hewn","hewing","hews"},
    {"hiccough","hiccoughed","hiccupped","hiccupping","hiccoughs"},
    {"hiccup","hiccupped","hiccupped","hiccupping","hiccups"},
    {"hide","hid","hidden","hiding","hides"},
    {"hie","hied","hied","hieing","hies"},
    {"hit","hit","hit","hitting","hits"},
    {"hold","held","held","holding","holds"},
    {"horsewhip","horsewhipped","horsewhipped","horsewhipping","horsewhips"},
    {"hurt","hurt","hurt","hurting","hurts"},
    {"hyphen","hyphened","hyphened","hyphening","hyphens"},
    {"imbed","imbedded","imbedded","imbedding","imbeds"},
    {"impanel","empanelled","empanelled","empanelling","empanels"},
    {"impel","impelled","impelled","impelling","impels"},
    {"incur","incurred","incurred","incurring","incurs"},
    {"infer","inferred","inferred","inferring","infers"},
    {"initial","initialed","initialled","initialing","initials"},
    {"inlay","inlaid","inlaid","inlaying","inlays"},
    {"input","input","input","inputting","inputs"},
    {"inset","inset","inset","insetting","insets"},
    {"inspan","inspanned","inspanned","inspanning","inspans"},
    {"instal","installed","installed","installing","installs"},
    {"instil","instilled","instilled","instilling","instils"},
    {"instill","instilled","instilled","instilling","instils"},
    {"inter","interred","interred","interring","inters"},
    {"interbreed","interbred","interbred","interbreeding","interbreeds"},
    {"interweave","interweaved","interwoven","interweaving","interweaves"},
    {"jell","gelled","gelled","gelling","gels"},
    {"joyride","joy-riding","joy-riding","joyriding","joy-rides"},
    {"keep","kept","kept","keeping","keeps"},
    {"kennel","kennelled","kennelled","kenneling","kennels"},
    {"kidnap","kidnapped","kidnapped","kidnapping","kidnaps"},
    {"kneel","knelt","knelt","kneeling","kneels"},
    {"knit","knit","knit","knitting","knits"},
    {"know","knew","known","knowing","knows"},
    {"lade","laded","laden","lading","lades"},
    {"lasso","lassoed","lassoed","lassoing","lassoes"},
    {"lay","laid","laid","laying","lays"},
    {"lead","led","led","leading","leads"},
    {"lean","leaned","leant","leaning","leans"},
    {"leap","leapt","leapt","leaping","leaps"},
    {"leapfrog","leapfrogged","leapfrogged","leapfrogging","leapfrogs"},
    {"leave","left","left","leaving","leaves"},
    {"lend","lent","lent","lending","lends"},
    {"let","let","let","letting","lets"},
    {"libel","libelled","libelled","libelling","libels"},
    {"lie","lay","lied","lying","lies"},
    {"light","lit","lighted","lighting","lights"},
    {"lipread","lip-read","lip-read","lip-reading","lip-reads"},
    {"lose","lost","lost","losing","loses"},
    {"lyric","lyriced","lyriced","lyricing","lyrics"},
    {"make","made","made","making","makes"},
    {"manumit","manumitted","manumitted","manumitting","manumits"},
    {"marshal","marshalled","marshalled","marshaling","marshals"},
    {"marvel","marvelled","marvelled","marveling","marvels"},
    {"mean","meant","meant","meaning","means"},
    {"meet","met","met","meeting","meets"},
    {"miscast","miscast","miscast","miscasting","miscasts"},
    {"misdeal","misdealt","misdealt","misdealing","misdeals"},
    {"misdo","mis-did","mis-done","misdoing","mis-does"},
    {"mislay","mislaid","mislaid","mislaying","mislays"},
    {"mislead","misled","misled","misleading","misleads"},
    {"misread","misread","misread","misreading","misreads"},
    {"misspell","misspelled","misspelt","misspelling","misspells"},
    {"misspend","misspent","misspent","misspending","misspends"},
    {"mistake","mistook","mistaken","mistaking","mistakes"},
    {"misunderstand","misunderstood","misunderstood","misunderstanding","misunderstands"},
    {"mow","mowed","mown","mowing","mows"},
    {"nonplus","nonplussed","nonplussed","nonplussing","nonpluses"},
    {"occur","occurred","occurred","occurring","occurs"},
    {"offset","offset","offset","offsetting","offsets"},
    {"okay","okayed","o.k.'d","okaying","o.k.'s"},
    {"omit","omitted","omitted","omitting","omits"},
    {"outbid","outbid","outbid","outbidding","outbids"},
    {"outdo","outdid","outdone","outdoing","outdoes"},
    {"outfit","outfitted","outfitted","outfitting","outfits"},
    {"outgo","outwent","outgone","outgoing","outgoes"},
    {"outgrow","outgrew","outgrown","outgrowing","outgrows"},
    {"output","output","output","outputting","outputs"},
    {"outrun","outran","outrun","outrunning","outruns"},
    {"outshine","outshone","outshone","outshining","outshines"},
    {"outstrip","outstripped","outstripped","outstripping","outstrips"},
    {"outwear","outwore","outworn","outwearing","outwears"},
    {"outwit","outwitted","outwitted","outwitting","outwits"},
    {"overbear","overbore","overborne","overbearing","overbears"},
    {"overbid","overbidded","overbidded","overbidding","overbids"},
    {"overcome","overcame","overcome","overcoming","overcomes"},
    {"overcrop","overcropped","overcropped","overcropping","overcrops"},
    {"overdo","overdid","overdone","overdoing","overdoes"},
    {"overdraw","overdrew","overdrawn","overdrawing","overdraws"},
    {"overdrive","overdrove","overdriven","overdriving","overdrives"},
    {"overeat","over-ate","overeaten","overeating","over-eats"},
    {"overgrow","overgrew","overgrown","overgrowing","overgrows"},
    {"overhang","overhung","overhung","overhanging","overhangs"},
    {"overhear","overheard","overheard","overhearing","overhears"},
    {"overlap","overlapped","overlapped","overlapping","overlaps"},
    {"overlay","overlaid","overlaid","overlaying","overlays"},
    {"overlie","overlay","overlain","overlying","overlies"},
    {"overpay","overpaid","overpaid","overpaying","overpays"},
    {"override","overrode","overridden","overriding","overrides"},
    {"overrun","overran","overrun","overrunning","overruns"},
    {"oversee","oversaw","overseen","overseeing","oversees"},
    {"overshoot","over shot","overshot","overshooting","over shoots"},
    {"oversleep","overslept","overslept","oversleeping","oversleeps"},
    {"overspread","overspread","overspread","overspreading","overspreads"},
    {"overstep","overstepped","overstepped","overstepping","oversteps"},
    {"overtake","overtook","overtaken","overtaking","overtakes"},
    {"overthrow","overthrew","overthrown","overthrowing","overthrows"},
    {"overwrite","over-wrote","overwritten","overwriting","over-writes"},
    {"pal","paled","paled","paling","pals"},
    {"panel","panelled","paneled","panelling","panels"},
    {"panic","panicked","panicked","panicking","panics"},
    {"partake","partook","partaken","partaking","partakes"},
    {"patrol","patrolled","patrolled","patrolling","patrols"},
    {"pay","paid","paid","paying","pays"},
    {"pencil","pencilled","pencilled","pencilling","pencils"},
    {"permit","permitted","permitted","permitting","permits"},
    {"picnic","picnicked","picnicked","picnicking","picnics"},
    {"pommel","pommelled","pommelled","pommelling","pommels"},
    {"prefer","preferred","preferred","preferring","prefers"},
    {"prepay","prepaid","prepaid","prepaying","pre-pays"},
    {"pretermit","pretermitted","pretermitted","pretermitting","pretermits"},
    {"proofread","proof read","proof read","proofreading","proof reads"},
    {"propel","propelled","propelled","propelling","propels"},
    {"put","put","put","putting","puts"},
    {"quarrel","quarrelled","quarrelled","quarrelling","quarrels"},
    {"quickstep","quickstepped","quickstepped","quickstepping","quicksteps"},
    {"quip","quipped","quipped","quipping","quips"},
    {"quit","quit","quitted","quitting","quits"},
    {"quiz","quizzed","quizzed","quizzing","quizzes"},
    {"rabbet","rabbetted","rabbetted","rabbetting","rabbets"},
    {"rabbit","rabbitted","rabbitted","rabbitting","rabbits"},
    {"ravel","ravelled","ravelled","ravelling","ravels"},
    {"read","read","read","reading","reads"},
    {"readmit","readmitted","readmitted","readmitting","readmits"},
    {"reallot","reallotted","reallotted","reallotting","reallots"},
    {"rebel","rebelled","rebelled","rebelling","rebels"},
    {"rebind","re-bound","re-bound","rebinding","re-binds"},
    {"rebroadcast","rebroadcast","rebroadcast","rebroadcasting","rebroadcasts"},
    {"rebuild","rebuilt","rebuilt","rebuilding","rebuilds"},
    {"rebut","rebutted","rebutted","rebutting","rebuts"},
    {"recap","recapped","recapped","recapping","recaps"},
    {"recast","recast","recast","recasting","recasts"},
    {"recommit","recommitted","recommitted","recommitting","recommits"},
    {"recur","recurred","recurred","recurring","recurs"},
    {"redo","redid","re-done","redoing","re-does"},
    {"refer","referred","referred","referring","refers"},
    {"refit","refitted","refitted","refitting","refits"},
    {"refuel","refueled","refuelled","refueling","refuels"},
    {"regret","regretted","regretted","regretting","regrets"},
    {"reinstall","reinstalled","reinstalled","reinstalling","re-installs"},
    {"rejig","rejigged","rejigged","rejigging","rejigs"},
    {"relay","relayed","relaid","relaying","relays"},
    {"remake","remade","remade","remaking","remakes"},
    {"remit","remitted","remitted","remitting","remits"},
    {"rend","rent","rent","rending","rends"},
    {"rendezvous","rendezvoused","rendezvoused","rendezvousing","rendezvous"},
    {"repay","repaid","repaid","repaying","repays"},
    {"repel","repelled","repelled","repelling","repels"},
    {"reread","reread","reread","rereading","rereads"},
    {"rerun","reran","rerun","rerunning","reruns"},
    {"resell","resold","resold","reselling","resells"},
    {"reset","reset","reset","resetting","resets"},
    {"reship","reshipped","reshipped","reshipping","reships"},
    {"resubmit","resubmitted","resubmitted","resubmitting","resubmits"},
    {"retake","retook","retaken","retaking","retakes"},
    {"retell","retold","retold","retelling","retells"},
    {"rethink","rethought","rethought","rethinking","rethinks"},
    {"retransmit","retransmitted","retransmitted","retransmitting","retransmits"},
    {"retrofit","retrofitted","retrofitted","retrofitting","retrofits"},
    {"rewrite","rewrote","rewritten","rewriting","rewrites"},
    {"rid","rid","rid","ridding","rids"},
    {"ride","rode","ridden","riding","rides"},
    {"ring","rang","rung","ringing","rings"},
    {"rise","rose","risen","rising","rises"},
    {"rubric","rubricced","rubricced","rubriccing","rubrics"},
    {"run","ran","run","running","runs"},
    {"sandbag","sandbagged","sandbagged","sandbagging","sandbags"},
    {"saw","sawed","sawn","sawing","saws"},
    {"say","said","said","saying","says"},
    {"see","saw","seen","seeing","sees"},
    {"seek","sought","sought","seeking","seeks"},
    {"sell","sold","sold","selling","sells"},
    {"send","sent","sent","sending","sends"},
    {"set","set","set","setting","sets"},
    {"sew","sewed","sewn","sewing","sews"},
    {"shake","shook","shaken","shaking","shakes"},
    {"shear","sheared","shorn","shearing","shears"},
    {"shed","shed","shed","shedding","sheds"},
    {"shellac","shellacked","shellacked","shellacking","shellacs"},
    {"shine","shone","shone","shining","shines"},
    {"shit","shit","shat","shitting","shits"},
    {"shoe","shoed","shod","shoeing","shoes"},
    {"shoot","shot","shot","shooting","shoots"},
    {"show","showed","shown","showing","shows"},
    {"shrink","shrank","shrunk","shrinking","shrinks"},
    {"shrive","shrove","shriven","shriving","shrives"},
    {"shrivel","shrivelled","shrivelled","shriveling","shrivels"},
    {"shut","shut","shut","shutting","shuts"},
    {"sidestep","sidestepped","sidestepped","sidestepping","sidesteps"},
    {"sing","sang","sung","singing","sings"},
    {"singe","singed","singed","singeing","singes"},
    {"sink","sank","sunk","sinking","sinks"},
    {"sit","sat","sat","sitting","sits"},
    {"ski","skied","ski'd","skiing","skis"},
    {"slay","slew","slain","slaying","slays"},
    {"sleep","slept","slept","sleeping","sleeps"},
    {"slide","slid","slid","sliding","slides"},
    {"sling","slung","slung","slinging","slings"},
    {"slink","slunk","slunk","slinking","slinks"},
    {"slit","slit","slit","slitting","slits"},
    {"smell","smelled","smelt","smelling","smells"},
    {"smite","smote","smitten","smiting","smites"},
    {"snivel","snivelled","snivelled","snivelling","snivels"},
    {"sow","sowed","sown","sowing","sows"},
    {"speak","spoke","spoken","speaking","speaks"},
    {"speed","sped","sped","speeding","speeds"},
    {"spell","spelled","spelt","spelling","spells"},
    {"spend","spent","spent","spending","spends"},
    {"spin","spun","spun","spinning","spins"},
    {"spit","spat","spit","spitting","spits"},
    {"split","split","split","splitting","splits"},
    {"spoil","spoiled","spoilt","spoiling","spoils"},
    {"spread","spread","spread","spreading","spreads"},
    {"spring","sprang","sprung","springing","springs"},
    {"squat","squatted","squatted","squatting","squats"},
    {"stand","stood","stood","standing","stands"},
    {"steal","stole","stolen","stealing","steals"},
    {"stick","stuck","stuck","sticking","sticks"},
    {"sting","stung","stung","sting","stings"},
    {"stink","stank","stunk","stinking","stinks"},
    {"stomach","stomached","stomached","stomaching","stomachs"},
    {"strew","strewed","strewn","strewing","strews"},
    {"stride","strode","stridden","striding","strides"},
    {"strike","struck","struck","striking","strikes"},
    {"string","strung","strung","stringing","strings"},
    {"strive","strove","striven","striving","strives"},
    {"stymie","stymied","stymied","stymieing","stymies"},
    {"sublet","subletted","subletted","subletting","sublets"},
    {"submit","submitted","submitted","submitting","submits"},
    {"summit","summitted","summitted","summitting","summits"},
    {"swear","swore","sworn","swearing","swears"},
    {"sweep","swept","swept","sweeping","sweeps"},
    {"swim","swam","swum","swimming","swims"},
    {"swing","swung","swung","swinging","swings"},
    {"syphon","syphoned","syphoned","syphoning","syphons"},
    {"take","took","taken","taking","takes"},
    {"talc","talced","talcked","talcing","talcs"},
    {"tar","tared","tared","taring","tars"},
    {"tarmac","tarmacked","tarmacked","tarmacking","tarmacs"},
    {"teach","taught","taught","teaching","teaches"},
    {"tear","tore","torn","tearing","tears"},
    {"tell","told","told","telling","tells"},
    {"think","thought","thought","thinking","thinks"},
    {"throw","threw","thrown","throwing","throws"},
    {"thrust","thrust","thrust","thrusting","thrusts"},
    {"tinge","tinged","tinged","tingeing","tinges"},
    {"tittup","tittupped","tittupped","tittupping","tittups"},
    {"torpedo","torpedoed","torpedoed","torpedoing","torpedo"},
    {"towel","towelled","towelled","towelling","towels"},
    {"traffic","trafficked","trafficked","trafficking","traffics"},
    {"trammel","trammeled","trammeled","trammelling","trammels"},
    {"transfer","transferred","transferred","transferring","transfers"},
    {"transmit","transmitted","transmitted","transmitting","transmits"},
    {"transship","transshipped","transshipped","transshipping","transships"},
    {"tread","trod","trodden","treading","treads"},
    {"typecast","typecast","typecast","typecasting","typecasts"},
    {"typeset","typeset","typeset","typeset","typesets"},
    {"unbar","unbarred","unbarred","unbarring","unbars"},
    {"unbend","unbent","unbent","unbending","unbends"},
    {"unbind","unbound","unbound","unbinding","unbinds"},
    {"unclip","unclipped","unclipped","unclipping","unclips"},
    {"unclog","unclogged","unclogged","unclogging","unclogs"},
    {"underbid","underbid","underbid","underbidding","underbids"},
    {"undercut","undercut","undercut","undercutting","undercuts"},
    {"undergo","underwent","undergone","undergoing","undergoes"},
    {"underlie","underlay","underlain","underlying","underlies"},
    {"underpay","underpaid","underpaid","underpaying","underpays"},
    {"underpin","underpinned","underpinned","underpinning","underpins"},
    {"undersell","undersold","undersold","underselling","undersells"},
    {"undershoot","undershot","undershot","undershooting","undershoots"},
    {"understand","understood","understood","understanding","understands"},
    {"undertake","undertook","undertaken","undertaking","undertakes"},
    {"underwrite","underwrote","underwritten","underwriting","underwrites"},
    {"undo","undid","undone","undoing","undoes"},
    {"unfit","unfitted","unfitted","unfitting","unfits"},
    {"unknot","unknotted","unknotted","unknotting","unknots"},
    {"unlearn","unlearned","unlearnt","unlearning","unlearns"},
    {"unman","unmanned","unmanned","unmanning","unmans"},
    {"unpin","unpinned","unpinned","unpinning","unpins"},
    {"unplug","unplugged","unplugged","unplugging","unplugs"},
    {"unsay","unsaid","unsaid","unsaying","unsays"},
    {"unstrap","unstrapped","unstrapped","unstrapping","unstraps"},
    {"unwind","unwound","unwound","unwinding","unwinds"},
    {"unwrap","unwrapped","unwrapped","unwrapping","unwraps"},
    {"unzip","unzipped","unzipped","unzipping","unzips"},
    {"uphold","upheld","upheld","upholding","upholds"},
    {"upset","upset","upset","upsetting","upsets"},
    {"veto","vetoed","vetoed","vetoing","vetoes"},
    {"victual","victualled","victualled","victualling","victuals"},
    {"wake","woke","waked","waking","wakes"},
    {"waylay","waylaid","waylaid","waylaying","waylays"},
    {"wear","wore","worn","wearing","wears"},
    {"weatherstrip","weatherstripped","weatherstripped","weatherstripping","weatherstrips"},
    {"weave","weaved","woven","weaving","weaves"},
    {"wed","wedded","wed","wedding","weds"},
    {"weep","wept","wept","weeping","weeps"},
    {"wet","wetted","wet","wetting","wets"},
    {"whir","whirred","whirred","whirring","whirrs"},
    {"whiz","whizzed","whizzed","whizzing","whizzes"},
    {"will","would","would","willing","wills"},
    {"win","won","won","winning","wins"},
    {"wind","wound","wound","winding","winds"},
    {"withdraw","withdrew","withdrawn","withdrawing","withdraws"},
    {"withhold","withheld","withheld","withholding","withholds"},
    {"withstand","withstood","withstood","withstanding","withstands"},
    {"worship","worshipped","worshipped","worshipping","worships"},
    {"wring","wrung","wrung","wringing","wrings"},
    {"write","wrote","written","writing","writes"},
    {"zero","zeroed","zeroed","zeroing","zeroes"},
    {"zigzag","zigzagged","zigzagged","zigzagging","zigzags"},
    {"zinc","zinced","zinked","zincking","zincs"},
};
static const int N_VERB_FORMS = 508;

static const char *const CAM_PRONOUNS[] = {"he","her","here","hers","herself","him","himself","his","i","it","its","itself","me","mine","my","myself","our","ours","ourselves","she","that","their","theirs","them","themselves","there","these","they","this","those","us","we","what","which","who","you","your","yours","yourself","yourselves"};
static const int N_CAM_PRONOUNS = 40;
static const char *const CAM_AUXILIARIES[] = {"are","be","been","being","can","could","did","do","does","had","has","have","is","may","might","must","shall","should","was","were","will","would"};
static const int N_CAM_AUXILIARIES = 22;
static const char *const CAM_CONJUNCTS[] = {"although","and","because","but","for","if","nor","or","since","so","then","though","unless","until","when","while","yet"};
static const int N_CAM_CONJUNCTS = 17;
static const char *const CAM_TIME[] = {"after","ago","already","always","before","later","never","now","often","rarely","sometimes","soon","still","then","today","tomorrow","when","while","yesterday","yet"};
static const int N_CAM_TIME = 20;
static const char *const CAM_QUESTION[] = {"how","if","what","when","where","whether","which","who","whom","whose","why"};
static const int N_CAM_QUESTION = 11;
static const char *const CAM_NEGATION[] = {"n't","neither","never","no","nobody","nor","not","nothing","nowhere"};
static const int N_CAM_NEGATION = 9;
static const char *const CAM_DETERMINERS[] = {"a","all","an","any","both","each","every","few","least","less","many","more","most","much","some","the"};
static const int N_CAM_DETERMINERS = 16;
static const char *const CAM_META[] = {"clarify","explain","explains","mean","meaning","means","repeat","rephrase","said","say","says","summarise","summarize","tell","tells","told"};
static const int N_CAM_META = 16;
static const char *const CAM_AFF_POS[] = {"amazing","enjoy","excellent","glad","good","great","happy","like","love","please","pleased","thank","thanks","wonderful"};
static const int N_CAM_AFF_POS = 14;
static const char *const CAM_AFF_NEG[] = {"angry","awful","bad","dislike","fail","fear","hate","horrible","mistake","sad","sorry","terrible","worried","wrong"};
static const int N_CAM_AFF_NEG = 14;
static const char *const CAM_NOUN_SUFF[] = {"ness","tion","ment","ance","ence","ity","ism","ist","ics","ogy","phy","ery","ary","ory","ture","sis","xis","ris","nce","ths","os"};
static const int N_CAM_NOUN_SUFF = 21;
static const char *const CAM_ADJ_SUFF[] = {"ic","ical","ive","ible","able"};
static const int N_CAM_ADJ_SUFF = 5;
static const char *const SW_DET[] = {"a","an","any","each","every","her","his","its","my","no","our","some","that","the","their","these","this","those","your"};
static const int N_SW_DET = 19;
static const char *const SW_PREP[] = {"about","above","after","against","among","at","before","below","between","by","down","during","for","from","in","into","near","of","off","on","out","over","through","to","toward","under","up","upon","with","within","without"};
static const int N_SW_PREP = 31;
static const char *const SW_CONJ[] = {"and","but","nor","or","so","yet"};
static const int N_SW_CONJ = 6;
static const char *const SW_AUX[] = {"am","are","be","been","can","could","did","do","does","had","has","have","is","may","might","shall","should","was","were","will","would"};
static const int N_SW_AUX = 21;
static const char *const SW_PRON[] = {"he","her","him","i","it","me","she","them","they","us","we","what","which","who","you"};
static const int N_SW_PRON = 15;
static const double CAM_GAP = 0.00070735753324857598;
/* END GENERATED ptol_voice_data */

#define IN_SET(arr, w) cv_in_set(arr, (int)(sizeof(arr) / sizeof((arr)[0])), (w))
static int cv_in_set(const char *const *a, int n, const char *w) { for (int i = 0; i < n; i++) if (!strcmp(a[i], w)) return 1; return 0; }
static int cv_closed(const char *w) { return IN_SET(SW_DET, w) || IN_SET(SW_PREP, w) || IN_SET(SW_CONJ, w) || IN_SET(SW_AUX, w) || IN_SET(SW_PRON, w); }

/* ── a small string -> count map ──────────────────────────────────────────── */
typedef struct { char *k; double v; } cv_kv;
typedef struct { cv_kv *t; size_t cap, n; } cv_map;
static cv_kv *cv_map_get(cv_map *m, const char *k, int create)
{
    if (!m->cap) { if (!create) return NULL; m->cap = 256; m->t = calloc(m->cap, sizeof(cv_kv)); }
    if (create && (m->n + 1) * 2 > m->cap) {
        cv_kv *o = m->t; size_t oc = m->cap; m->cap *= 2; m->t = calloc(m->cap, sizeof(cv_kv)); m->n = 0;
        for (size_t i = 0; i < oc; i++) if (o[i].k) { size_t h = 5381; for (const char *s = o[i].k; *s; s++) h = h * 33 + (unsigned char)*s; h &= m->cap - 1; while (m->t[h].k) h = (h + 1) & (m->cap - 1); m->t[h] = o[i]; m->n++; }
        free(o);
    }
    size_t h = 5381; for (const char *s = k; *s; s++) h = h * 33 + (unsigned char)*s; h &= m->cap - 1;
    while (m->t[h].k) { if (!strcmp(m->t[h].k, k)) return &m->t[h]; h = (h + 1) & (m->cap - 1); }
    if (!create) return NULL;
    m->t[h].k = strdup(k); m->t[h].v = 0; m->n++; return &m->t[h];
}

/* ── Bigram (sedenion_window.Bigram, lam 0.7) ──────────────────────────────── */
typedef struct { cv_map uni, bi, ctx; double total; int ok; } cv_bigram;
static cv_bigram g_bg;

static void cv_bg_fit(cv_bigram *b, const char *text)
{
    char prev[64] = ""; const char *p = text;
    while (*p) {
        if (isalpha((unsigned char)*p) && (unsigned char)*p < 0x80) {                 /* [a-z]+(?:'[a-z]+)? on the lowercased text */
            char w[64]; int k = 0;
            while (isalpha((unsigned char)*p) && (unsigned char)*p < 0x80 && k < 60) { w[k++] = (char)tolower((unsigned char)*p); p++; }
            if (*p == '\'' && isalpha((unsigned char)p[1]) && (unsigned char)p[1] < 0x80) { w[k++] = '\''; p++; while (isalpha((unsigned char)*p) && (unsigned char)*p < 0x80 && k < 62) { w[k++] = (char)tolower((unsigned char)*p); p++; } }
            w[k] = 0; cv_map_get(&b->uni, w, 1)->v += 1; b->total += 1;
            if (prev[0]) { char key[140]; snprintf(key, sizeof key, "%s %s", prev, w); cv_map_get(&b->bi, key, 1)->v += 1; cv_map_get(&b->ctx, prev, 1)->v += 1; }
            snprintf(prev, sizeof prev, "%s", w);
        } else p++;                                                           /* tokens only: any run of other characters (even a full stop) separates two words of a pair */
    }
    b->ok = 1;
}

static double cv_bg_pu(const cv_bigram *b, const char *w)
{
    cv_kv *u = cv_map_get((cv_map *)&b->uni, w, 0);
    return ((u ? u->v : 0.0) + 0.1) / (b->total + 0.1 * ((double)b->uni.n + 1.0));
}
static double cv_bg_p(const cv_bigram *b, const char *w, const char *prev)
{
    double pu = cv_bg_pu(b, w);
    if (!prev) return pu;
    cv_kv *c = cv_map_get((cv_map *)&b->ctx, prev, 0);
    if (!c || c->v <= 0) return pu;
    char key[140]; snprintf(key, sizeof key, "%s %s", prev, w); cv_kv *bi = cv_map_get((cv_map *)&b->bi, key, 0);
    return 0.7 * (bi ? bi->v : 0.0) / c->v + 0.3 * pu;
}

/* ── the combined store: words, first-sense entries, co-occurrence neighbours ─── */
/* voice_lex.bin (tools/export_c_monad_data.py --lex): every WordNet word with the parts of speech it has, and the relation counts of its first synset.
 * monad3_c.bin keeps one lossy entry per word ('dog' is a verb there, 'rules' is absent), so the voice reads this first and falls back to the store. */
static unsigned char *g_vl = NULL; static uint32_t g_vl_n = 0; static int g_vl_tried = 0;
static const char *g_vl_blob; static const uint32_t *g_vl_off; static const unsigned char *g_vl_mask, *g_vl_pos1; static const int8_t *g_vl_vec;
static void cv_lex_open(void)
{
    if (g_vl_tried) return; g_vl_tried = 1;
    char path[700]; snprintf(path, sizeof path, "%s/voice_lex.bin", g_ptol_dir); FILE *f = fopen(path, "rb"); if (!f) return;
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET); unsigned char *b = malloc((size_t)sz);
    if (!b || fread(b, 1, (size_t)sz, f) != (size_t)sz || memcmp(b, "VLEX1\0\0\0", 8)) { fclose(f); free(b); return; }
    fclose(f); uint32_t n, bl; memcpy(&n, b + 8, 4); memcpy(&bl, b + 12, 4);
    size_t o = 16; g_vl_blob = (const char *)(b + o); o += bl + ((8 - bl % 8) % 8);
    g_vl_off = (const uint32_t *)(b + o); o += (size_t)n * 4; g_vl_mask = b + o; o += n; g_vl_pos1 = b + o; o += n; g_vl_vec = (const int8_t *)(b + o);
    g_vl = b; g_vl_n = n;
}
static long cv_lex_find(const char *w)
{
    cv_lex_open(); if (!g_vl) return -1;
    long lo = 0, hi = (long)g_vl_n - 1;
    while (lo <= hi) { long mid = (lo + hi) / 2; int c = strcmp(g_vl_blob + g_vl_off[mid], w); if (c == 0) return mid; if (c < 0) lo = mid + 1; else hi = mid - 1; }
    return -1;
}
static int cv_entry(const char *w, int *pos, const int16_t **vec)       /* the entry of a word: its first synset's part of speech and relation counts, or 0 */
{
    static int16_t ring[4][19]; static int ri = 0;
    long i = cv_lex_find(w);
    if (i < 0 && g_vl) {                                                 /* an inflected form: its lemma, parts of speech in WordNet's order n v a r */
        extern const char *cv_morphy_pos(const char *, int, char *); char mb[64];
        for (int pp = 1; pp <= 4 && i < 0; pp++) { const char *l = cv_morphy_pos(w, pp, mb); if (l) i = cv_lex_find(l); }
    }
    if (i >= 0) {
        if (pos) *pos = g_vl_pos1[i];
        if (vec) { int16_t *r = ring[ri++ & 3]; for (int k = 0; k < 19; k++) r[k] = g_vl_vec[i * 19 + k]; *vec = r; }
        return 1;
    }
    if (g_vl) return 0;                                                  /* the lexicon is loaded: a word it does not have is not a word */
    int32_t ix[3]; uint32_t deg;
    if (!monad3_lookup(w, ix, &deg) || ix[1] < 0) return 0;
    const unsigned char *e = g_m3 + g_m3h->off_wn + (size_t)ix[1] * 82u;
    if (pos) *pos = e[32];                                              /* 1 noun, 2 verb, 3 adj, 4 adv */
    if (vec) *vec = (const int16_t *)(e + 40);
    return 1;
}
static int cv_known(const char *w, void *c) { (void)c; return cv_entry(w, NULL, NULL); }
static double cv_pgen(const char *w, void *c) { (void)c; return g_bg.ok ? cv_bg_pu(&g_bg, w) : 1e-6; }

static const char **g_eng_name = NULL;
static void cv_eng_names(void)
{
    if (g_eng_name || !g_m3h) return;
    g_eng_name = calloc(g_m3h->n_eng + 1, sizeof(char *));
    const char *blob = (const char *)(g_m3 + g_m3h->off_wordblob); const WordRec *recs = (const WordRec *)(g_m3 + g_m3h->off_wordrec);
    for (uint32_t i = 0; i < g_m3h->n_words; i++) if (recs[i].eng_idx >= 0 && (uint32_t)recs[i].eng_idx < g_m3h->n_eng) g_eng_name[recs[i].eng_idx] = blob + recs[i].name_off;
}

/* ── the verb: irregular table, regular rules, the Lyndon verb group (lyndon_conjugation.py) ─────────────── */
static int cv_isv(int c) { return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'; }
static int cv_cvc(const char *w)
{
    size_t n = strlen(w); if (n < 3) return 0;
    char a = w[n - 3], b = w[n - 2], c = w[n - 1];
    if (cv_isv(c) || c == 'w' || c == 'x' || c == 'y' || !cv_isv(b) || cv_isv(a)) return 0;
    int groups = 0; for (size_t i = 0; i < n; i++) if (cv_isv(w[i]) && (i == 0 || !cv_isv(w[i - 1]))) groups++;
    return groups == 1;
}
static int cv_ends(const char *w, const char *s) { size_t a = strlen(w), b = strlen(s); return a >= b && !strcmp(w + a - b, s); }

static void cv_regular(const char *w, const char *tag, char *out, size_t sz)
{
    size_t n = strlen(w); char last = n ? w[n - 1] : 0, pen = n > 1 ? w[n - 2] : 0;
    if (!strcmp(tag, "VBZ")) {
        if (cv_ends(w, "s") || cv_ends(w, "x") || cv_ends(w, "z") || cv_ends(w, "ch") || cv_ends(w, "sh")) snprintf(out, sz, "%ses", w);
        else if (last == 'y' && !cv_isv(pen)) snprintf(out, sz, "%.*sies", (int)n - 1, w);
        else snprintf(out, sz, "%ss", w);
    } else if (!strcmp(tag, "VBD") || !strcmp(tag, "VBN")) {
        if (last == 'e') snprintf(out, sz, "%sd", w);
        else if (last == 'y' && !cv_isv(pen)) snprintf(out, sz, "%.*sied", (int)n - 1, w);
        else if (cv_cvc(w)) snprintf(out, sz, "%s%ced", w, last);
        else snprintf(out, sz, "%sed", w);
    } else {
        if (cv_ends(w, "ie")) snprintf(out, sz, "%.*sying", (int)n - 2, w);
        else if (last == 'e' && !cv_ends(w, "ee") && !cv_ends(w, "ye") && !cv_ends(w, "oe")) snprintf(out, sz, "%.*sing", (int)n - 1, w);
        else if (cv_cvc(w)) snprintf(out, sz, "%s%cing", w, last);
        else snprintf(out, sz, "%sing", w);
    }
}

static int cv_vf_find(const char *lemma)                              /* bsearch VERB_FORMS (sorted by lemma) */
{
    int lo = 0, hi = N_VERB_FORMS - 1;
    while (lo <= hi) { int mid = (lo + hi) / 2, c = strcmp(VERB_FORMS[mid][0], lemma); if (c == 0) return mid; if (c < 0) lo = mid + 1; else hi = mid - 1; }
    return -1;
}

static const char *CV_BE[2][2][3] = {{{"am", "are", "is"}, {"are", "are", "are"}}, {{"was", "were", "was"}, {"were", "were", "were"}}};   /* [past][pl][person-1] */

static void cv_form(const char *lemma, const char *tag, int pl, int person, char *out, size_t sz)
{
    if (!strcmp(lemma, "be")) {
        if (!strcmp(tag, "VB")) snprintf(out, sz, "be"); else if (!strcmp(tag, "VBN")) snprintf(out, sz, "been"); else if (!strcmp(tag, "VBG")) snprintf(out, sz, "being");
        else snprintf(out, sz, "%s", CV_BE[!strcmp(tag, "VBD")][pl ? 1 : 0][(person < 1 || person > 3 ? 3 : person) - 1]);
        return;
    }
    if (!strcmp(lemma, "have")) {
        if (!strcmp(tag, "VB")) snprintf(out, sz, "have"); else if (!strcmp(tag, "VBN") || !strcmp(tag, "VBD")) snprintf(out, sz, "had"); else if (!strcmp(tag, "VBG")) snprintf(out, sz, "having");
        else snprintf(out, sz, "%s", (!pl && person == 3) ? "has" : "have");
        return;
    }
    if (!strcmp(tag, "VB") || !strcmp(tag, "VBP")) { snprintf(out, sz, "%s", lemma); return; }
    int i = cv_vf_find(lemma);
    if (i >= 0) { int c = !strcmp(tag, "VBD") ? 1 : !strcmp(tag, "VBN") ? 2 : !strcmp(tag, "VBG") ? 3 : 4; snprintf(out, sz, "%s", VERB_FORMS[i][c]); return; }
    cv_regular(lemma, tag, out, sz);
}

enum { CV_R_V = 0, CV_R_PROG = 1, CV_R_PERF = 2, CV_R_MODAL = 3, CV_R_TENSE = 4 };
typedef struct { char tense[12]; char modal[8]; int perf, prog; char mood[12]; } cv_tspec;

static void cv_parse_tense(const char *spec, cv_tspec *d)
{
    memset(d, 0, sizeof *d); strcpy(d->tense, "present"); strcpy(d->mood, "indicative");
    char buf[128]; snprintf(buf, sizeof buf, "%s", spec && *spec ? spec : "present"); for (char *p = buf; *p; p++) { *p = (char)tolower((unsigned char)*p); if (*p == '-') *p = ' '; }
    for (char *t = strtok(buf, " "); t; t = strtok(NULL, " ")) {
        if (!strcmp(t, "perfect")) d->perf = 1; else if (!strcmp(t, "progressive")) d->prog = 1;
        else if (!strcmp(t, "past")) strcpy(d->tense, "past");
        else if (!strcmp(t, "future")) strcpy(d->modal, "will");
        else if (!strcmp(t, "conditional")) { strcpy(d->modal, "would"); strcpy(d->tense, "past"); }
        else if (!strcmp(t, "imperative")) { strcpy(d->mood, "imperative"); strcpy(d->tense, "base"); }
        else if (!strcmp(t, "base")) { strcpy(d->mood, "base"); strcpy(d->tense, "base"); }
    }
}

/* the group as a non-increasing rank word; its Lyndon factors by Duval (every factor is one letter here: the ranks are distinct) */
static int cv_verb_group(const cv_tspec *d, int *w)
{
    int n = 0, tmp[5], m = 0; tmp[m++] = CV_R_V;
    if (d->prog) tmp[m++] = CV_R_PROG; if (d->perf) tmp[m++] = CV_R_PERF; if (d->modal[0]) tmp[m++] = CV_R_MODAL; if (strcmp(d->tense, "base")) tmp[m++] = CV_R_TENSE;
    for (int r = 4; r >= 0; r--) for (int i = 0; i < m; i++) if (tmp[i] == r) w[n++] = r;
    return n;
}
static int cv_duval(const int *w, int n, int *starts, int *lens)       /* the Lyndon factorisation (Duval): returns the factor count */
{
    int i = 0, nf = 0;
    while (i < n) {
        int j = i + 1, k = i;
        while (j < n && w[k] <= w[j]) { k = (w[k] < w[j]) ? i : k + 1; j++; }
        while (i <= k) { starts[nf] = i; lens[nf] = j - k; nf++; i += j - k; }
    }
    return nf;
}

typedef struct { char word[48]; char tag[5]; int factor; } cv_vw;
/* conjugates(lemma, spec, number, person): the realised verb group, affix hopping over the factor list */
static int cv_conjugates(const char *lemma, const char *spec, int pl, int person, cv_vw *out)
{
    cv_tspec d; cv_parse_tense(spec, &d); int n = 0;
    if (!strcmp(d.tense, "base")) { snprintf(out[0].word, 48, "%s", lemma); strcpy(out[0].tag, "VB"); out[0].factor = CV_R_V; return 1; }
    struct { int f; char w[48]; } heads[4]; int nh = 0;
    if (d.modal[0]) { heads[nh].f = CV_R_MODAL; snprintf(heads[nh++].w, 48, "%s", d.modal); }
    if (d.perf) { heads[nh].f = CV_R_PERF; snprintf(heads[nh++].w, 48, "have"); }
    if (d.prog) { heads[nh].f = CV_R_PROG; snprintf(heads[nh++].w, 48, "be"); }
    heads[nh].f = CV_R_V; snprintf(heads[nh++].w, 48, "%s", lemma);
    const char *pending = NULL;
    for (int i = 0; i < nh; i++) {
        if (heads[i].f == CV_R_MODAL) { snprintf(out[n].word, 48, "%s", heads[i].w); strcpy(out[n].tag, "MD"); out[n].factor = heads[i].f; n++; pending = "VB"; continue; }
        const char *tag = pending ? pending : (!strcmp(d.tense, "past") ? "VBD" : ((!pl && person == 3) ? "VBZ" : "VBP"));
        cv_form(heads[i].w, tag, pl, person, out[n].word, 48); snprintf(out[n].tag, 5, "%s", tag); out[n].factor = heads[i].f; n++;
        pending = heads[i].f == CV_R_PERF ? "VBN" : heads[i].f == CV_R_PROG ? "VBG" : "VB";
    }
    return n;
}

/* inflection_frame: the surface string and the two marker codes (tense carrier, conjugation of the main verb) */
static void cv_inflect(const char *spec, const char *lemma, int pl, int person, char *surface, size_t sz, const char **mt, const char **conj)
{
    cv_vw g[6]; int n = cv_conjugates(lemma, spec, pl, person, g); cv_tspec d; cv_parse_tense(spec, &d);
    surface[0] = 0; for (int i = 0; i < n; i++) { size_t L = strlen(surface); snprintf(surface + L, sz - L, "%s%s", i ? " " : "", g[i].word); }
    if (!strcmp(d.mood, "imperative") || !strcmp(d.mood, "base")) *mt = !strcmp(d.mood, "imperative") ? "imperative" : "base";
    else if (!strcmp(d.modal, "will")) *mt = "future"; else if (!strcmp(d.modal, "would")) *mt = "conditional";
    else if (!strcmp(d.tense, "present") && d.perf && !d.prog) *mt = "perfect"; else if (!strcmp(d.tense, "present") && d.prog && !d.perf) *mt = "progressive";
    else *mt = !strcmp(d.tense, "past") ? "past" : "present";
    const char *t = g[n - 1].tag;
    *conj = !strcmp(t, "VBZ") ? "3sg" : !strcmp(t, "VBD") ? "past" : !strcmp(t, "VBN") ? "pastpart" : !strcmp(t, "VBG") ? "ing" : "base";
}

/* ── tenseplan.py ────────────────────────────────────────────────────────── */
static const char *cv_lemniscate_tense(int depth, int reach)
{
    if (reach <= 1) return "present";
    double frac = (double)(reach - depth) / (double)(reach - 1);
    return frac < 0.34 ? "past" : frac > 0.66 ? "future" : "present";
}
static int cv_word_is(const char *w, const char *const *set) { for (; *set; set++) if (!strcmp(*set, w)) return 1; return 0; }
static const char *cv_mirror_tense(const char *text)
{
    static const char *const PAST[] = {"was", "were", "had", "did", "went", "said", "made", "came", "saw", "took", "got", "knew", "thought", "told", "found", "gave", NULL};
    static const char *const FUT[] = {"will", "shall", "won't", "gonna", "tomorrow", "next", NULL};
    int past = 0, fut = 0; const char *p = text; char prev[64] = "";
    while (*p) {
        if (isalnum((unsigned char)*p) || *p == '_' || (unsigned char)*p >= 0x80) {
            char w[64]; int k = 0;
            while ((isalnum((unsigned char)*p) || *p == '_' || (unsigned char)*p >= 0x80 || *p == '\'') && k < 62) { w[k++] = (char)tolower((unsigned char)*p); p++; }
            while (k > 0 && w[k - 1] == '\'') k--;
            w[k] = 0;
            if (cv_word_is(w, FUT) || (!strcmp(prev, "going") && !strcmp(w, "to"))) fut = 1;
            if (cv_word_is(w, PAST) || (k >= 5 && !strcmp(w + k - 2, "ed"))) past = 1;
            snprintf(prev, sizeof prev, "%s", w);
        } else p++;
    }
    return fut ? "future" : past ? "past" : "present";
}
static const char *cv_resolve_tense(const char *tense, const char *prompt, int depth, int reach)
{
    if (!tense || !*tense) return "present";
    if (!strcmp(tense, "auto")) return (depth >= 0 && reach >= 0) ? cv_lemniscate_tense(depth, reach) : "present";
    if (!strcmp(tense, "mirror")) return cv_mirror_tense(prompt);
    if (!strcmp(tense, "now")) return "present";
    return tense;
}

/* ── Tone7 (tone_chord.py): the seven tones and what each does to the constructor ─────────────────────────── */
enum { T_DA, T_5HT, T_NE, T_OXT, T_GLU, T_GABA, T_CB1 };
static const char *const CV_N7[7] = {"DA", "5HT", "NE", "OXT", "GLU", "GABA", "CB1"};
typedef struct { double lev[7], base[7]; } cv_tone;
typedef struct { int novelty_rank, pool_size, short_frame; double coherence, user_boost, prune_floor; } cv_knobs;

static int cv_tone_axis(const char *a)
{
    if (!strcmp(a, "OT")) a = "OXT"; if (!strcmp(a, "eCB") || !strcmp(a, "OPI")) a = "CB1";      /* OPI (the hub) takes the CB1 slot */
    for (int i = 0; i < 7; i++) if (!strcmp(CV_N7[i], a)) return i;
    return -1;
}
static void cv_tone_from_axis(cv_tone *t, const char *axis, double level)
{
    for (int i = 0; i < 7; i++) t->lev[i] = t->base[i] = 0.3;
    int k = cv_tone_axis(axis); if (k >= 0) t->lev[k] = level < 0 ? 0 : level > 1 ? 1 : level;
}
static double cv_q(const cv_tone *t, int a) { double l = t->lev[a] < 0 ? 0 : t->lev[a] > 1 ? 1 : t->lev[a]; return nearbyint(l * 6.0) / 6.0; }
static void cv_knobs_of(const cv_tone *t, cv_knobs *k)
{
    double x[7];
    for (int a = 0; a < 7; a++) { double qb = nearbyint(t->base[a] * 6.0) / 6.0, q = cv_q(t, a); x[a] = q >= qb ? (q - qb) / (1.0 - qb) : (q - qb) / (qb > 1e-9 ? qb : 1e-9); }
    double upDA = x[T_DA] > 0 ? x[T_DA] : 0, upOXT = x[T_OXT] > 0 ? x[T_OXT] : 0, upGABA = x[T_GABA] > 0 ? x[T_GABA] : 0;
    k->novelty_rank = (int)lrint(3.0 * upDA);
    k->coherence = 1.0 + 1.5 * x[T_5HT] * (x[T_5HT] >= 0 ? 1.0 : 0.5);
    double ps = nearbyint(12.0 * (1.0 + 1.5 * x[T_GLU]) * (1.0 - 0.6 * x[T_NE])); k->pool_size = (int)(ps < 3 ? 3 : ps > 60 ? 60 : ps);
    k->user_boost = 1.0 + 3.0 * upOXT; k->prune_floor = 0.3 * upGABA; k->short_frame = x[T_NE] > 0.3;
}

/* ── markers: tone, tense, conjugation as invisible Tag characters (U+E0020 ..) ───────────────────────────── */
static const char *const CV_NEURO[9] = {"DA", "5HT", "NE", "OXT", "GLU", "GABA", "CB1", "ACh", "OPI"};
static const char *const CV_TENSES[8] = {"base", "past", "present", "future", "perfect", "progressive", "imperative", "conditional"};
static const char *const CV_CONJ[8] = {"base", "3sg", "past", "pastpart", "ing", "plural", "comparative", "superlative"};
static int cv_idx(const char *const *a, int n, const char *s) { for (int i = 0; i < n; i++) if (!strcmp(a[i], s)) return i; return 0; }
static int cv_put_tag(char *o, int cp) { o[0] = (char)(0xF0 | (cp >> 18)); o[1] = (char)(0x80 | ((cp >> 12) & 63)); o[2] = (char)(0x80 | ((cp >> 6) & 63)); o[3] = (char)(0x80 | (cp & 63)); return 4; }
static void cv_marker(char *o, const char *axis, int level, const char *tense, const char *conj)
{
    int n = 0; if (!strcmp(axis, "OT")) axis = "OXT"; if (!strcmp(axis, "eCB")) axis = "CB1";
    level = level < 0 ? 0 : level > 6 ? 6 : level;
    n += cv_put_tag(o + n, 0xE0020 + cv_idx(CV_NEURO, 9, axis) * 7 + level);
    n += cv_put_tag(o + n, 0xE0020 + 64 + cv_idx(CV_TENSES, 8, tense));
    n += cv_put_tag(o + n, 0xE0020 + 72 + cv_idx(CV_CONJ, 8, conj)); o[n] = 0;
}

/* ── the window ───────────────────────────────────────────────────────────────────────────────────────── */
#define CV_MAXC 500
typedef struct { char w[48]; double x; } cv_cand;
typedef struct { cv_cand c[CV_MAXC]; int n; } cv_set;

typedef struct {
    char *ring[16]; int t;
    cv_tone tone7;
    char heard_name[8]; int heard_lv;
    int use_state; mh_state st;                          /* the user's state (monad_harness.c) when the meter is loaded */
    char tgt_name[8]; int tgt_lv;
    char user[160][48]; int nuser;                       /* the speaker's own words of the last turn (closed class removed) */
    int imitation, web;
    mh_ear *ear;
    /* the last pick's weights, for the strut revisit */
    char lp_w[CV_MAXC][48]; double lp_v[CV_MAXC]; int lp_n; double lp_tot;
    /* trace of the last sentence */
    char trace[4096];
} cv_win;

static int cv_fill(const cv_win *w) { int n = 0; for (int i = 0; i < 16; i++) if (w->ring[i]) n++; return n; }
static void cv_place(cv_win *w, const char *word)
{
    if (!w->ring[0]) { w->ring[0] = strdup(word); return; }
    free(w->ring[15]);
    for (int i = 15; i > 1; i--) w->ring[i] = w->ring[i - 1];
    w->ring[1] = strdup(word);
}

/* lemma by rule: the WordNet morphy of the child (entries are one first-sense row per word) */
static int cv_verb_in_table(const char *w) { return cv_vf_find(w) >= 0; }

/* WordNet's morphy, as nltk applies it: the word itself if it is a lemma of that part of speech, else the first suffix-rule form that is; verbs also by the irregular table */
static int cv_lex_has(const char *w, int pos) { long i = cv_lex_find(w); return i >= 0 && ((g_vl_mask[i] >> (pos - 1)) & 1); }
const char *cv_morphy_pos(const char *u, int pos, char *buf)
{
    static const char *const NR[][2] = {{"s", ""}, {"ses", "s"}, {"ves", "f"}, {"xes", "x"}, {"zes", "z"}, {"ches", "ch"}, {"shes", "sh"}, {"men", "man"}, {"ies", "y"}};
    static const char *const VR[][2] = {{"s", ""}, {"ies", "y"}, {"es", "e"}, {"es", ""}, {"ed", "e"}, {"ed", ""}, {"ing", "e"}, {"ing", ""}};
    static const char *const AR[][2] = {{"er", ""}, {"est", ""}, {"er", "e"}, {"est", "e"}};
    size_t n = strlen(u); if (n < 2 || n >= 60) return NULL;
    if (!g_vl) { int p; if (cv_entry(u, &p, NULL) && p == pos) { snprintf(buf, 64, "%s", u); return buf; } return NULL; }
    if (cv_lex_has(u, pos)) { snprintf(buf, 64, "%s", u); return buf; }
    if (pos == 2) for (int i = 0; i < N_VERB_FORMS; i++) for (int k = 1; k <= 4; k++) if (!strcmp(VERB_FORMS[i][k], u) && cv_lex_has(VERB_FORMS[i][0], 2)) { snprintf(buf, 64, "%s", VERB_FORMS[i][0]); return buf; }
    const char *(*R)[2] = pos == 1 ? NR : pos == 2 ? VR : pos == 3 ? AR : NULL; int nr = pos == 1 ? 9 : pos == 2 ? 8 : pos == 3 ? 4 : 0;
    for (int r = 0; r < nr; r++) {
        size_t lo = strlen(R[r][0]); if (n <= lo || strcmp(u + n - lo, R[r][0])) continue;
        snprintf(buf, 64, "%.*s%s", (int)(n - lo), u, R[r][1]); if (cv_lex_has(buf, pos)) return buf;
    }
    return NULL;
}
static int cv_has_pos(const char *w, int pos) { char b[64]; return cv_morphy_pos(w, pos, b) != NULL; }      /* wn.synsets(w, pos) is not empty */
static const char *cv_lemma_pos(const char *u, int pos, char *buf)      /* wn.morphy(u, pos) for noun (1) / verb (2); NULL when it is not a form of one */
{
    if (!g_vl && pos == 2 && !cv_has_pos(u, 2) && !cv_verb_in_table(u)) return NULL;
    return cv_morphy_pos(u, pos, buf);
}

static void cv_set_add(cv_set *s, const char *w, double x)
{
    for (int i = 0; i < s->n; i++) if (!strcmp(s->c[i].w, w)) { if (x > s->c[i].x) s->c[i].x = x; return; }
    if (s->n < CV_MAXC) { snprintf(s->c[s->n].w, 48, "%s", w); s->c[s->n].x = x; s->n++; }
}

/* the neighbourhood of a seed word in the co-occurrence matrix (replaces WordNet's relation neighbourhood: nb.around): top 12 of the right part of speech, weight 0.6 */
static void cv_neighbours(cv_set *s, const char *seed, int pos)
{
    int32_t ix[3]; uint32_t deg; if (!monad3_lookup(seed, ix, &deg) || ix[0] < 0 || !g_eng_name) return;
    const uint32_t *rp = (const uint32_t *)(g_m3 + g_m3h->off_rowptr), *col = (const uint32_t *)(g_m3 + g_m3h->off_col); const float *wt = (const float *)(g_m3 + g_m3h->off_w);
    struct { char lem[48]; float w; } top[12]; int nt = 0;
    for (uint32_t k = rp[ix[0]]; k < rp[ix[0] + 1]; k++) {
        uint32_t c = col[k]; if (c >= g_m3h->n_eng || !g_eng_name[c]) continue;
        const char *nm = g_eng_name[c]; size_t L = strlen(nm); if (L < 3 || L > 20) continue;
        int ok = 1; for (size_t i = 0; i < L; i++) if (!isalpha((unsigned char)nm[i]) || isupper((unsigned char)nm[i])) { ok = 0; break; }
        char nb[64]; const char *lem = ok ? cv_morphy_pos(nm, pos, nb) : NULL;                 /* the matrix keeps surface forms (roots, chasing): a candidate is the lemma */
        if (!ok || cv_closed(nm) || !lem || cv_closed(lem) || strlen(lem) < 3) continue;
        nm = lem; L = strlen(nm);
        int dupl = 0; for (int i = 0; i < nt; i++) if (!strcmp(top[i].lem, nm)) { if (wt[k] > top[i].w) top[i].w = wt[k]; dupl = 1; }
        if (dupl) continue;
        if (nt < 12) { snprintf(top[nt].lem, 48, "%s", nm); top[nt].w = wt[k]; nt++; }
        else { int m = 0; for (int i = 1; i < 12; i++) if (top[i].w < top[m].w) m = i; if (wt[k] > top[m].w) { snprintf(top[m].lem, 48, "%s", nm); top[m].w = wt[k]; } }
    }
    for (int i = 0; i < nt; i++) cv_set_add(s, top[i].lem, 0.6);
}

/* P(w | prev): the bigram, mixed with the user's own usage by lambda (the harness's ear) */
static double cv_p(const cv_win *w, const char *word, const char *prev)
{
    double p = cv_bg_p(&g_bg, word, prev);
    if (w->ear) { double lam = mh_ear_lambda(w->ear); p = (1.0 - lam) * p + lam * mh_ear_p_word(w->ear, word); }
    return p;
}
static int cv_is_user(const cv_win *w, const char *word) { for (int i = 0; i < w->nuser; i++) if (!strcmp(w->user[i], word)) return 1; return 0; }
static int cv_is_heard(const cv_win *w, const char *word)           /* the speaker's word, or its lemma (rules -> rule) */
{
    char b[64];
    for (int i = 0; i < w->nuser; i++) {
        if (!strcmp(w->user[i], word)) return 1;
        const char *l = cv_lemma_pos(w->user[i], 1, b); if (l && !strcmp(l, word)) return 1;
        l = cv_lemma_pos(w->user[i], 2, b); if (l && !strcmp(l, word)) return 1;
    }
    return 0;
}

static const char *const CV_DETS[] = {"the", "a", "an", "this", "that", "its"};
static int cv_cmp_pair(double a, const char *an, double b, const char *bn) { return a > b ? 1 : a < b ? -1 : strcmp(an, bn); }

/* one word for the open slot: returns the word (static buffer), P (its share of the candidate weights), and the candidate count */
static char g_pick[48];
static const char *cv_pick(cv_win *w, const char *slot, const char *prev, cv_set topic[3], char taken[][48], int ntaken, double *P, int *ncand)
{
    *P = 1.0; *ncand = 0; g_pick[0] = 0; w->lp_n = 0;
    int ring = !strcmp(slot, "DET") || !strcmp(slot, "PREP") || !strcmp(slot, "CONJ") || !strcmp(slot, "AUX");
    if (ring) {
        const char *const *src; int n;
        if (!strcmp(slot, "DET")) { src = CV_DETS; n = 6; } else if (!strcmp(slot, "PREP")) { src = SW_PREP; n = N_SW_PREP; } else if (!strcmp(slot, "CONJ")) { src = SW_CONJ; n = N_SW_CONJ; } else { src = SW_AUX; n = N_SW_AUX; }
        double tot = 0, bw = -1; const char *best = NULL;
        for (int i = 0; i < n; i++) { double v = cv_p(w, src[i], prev); tot += v; if (!best || cv_cmp_pair(v, src[i], bw, best) > 0) { best = src[i]; bw = v; } }
        snprintf(g_pick, 48, "%s", best); *P = bw / tot; *ncand = n; return g_pick;
    }
    int pi = !strcmp(slot, "N") ? 0 : !strcmp(slot, "V") ? 1 : 2; int pos = pi == 0 ? 1 : pi == 1 ? 2 : 3;
    static cv_set cand; cand.n = 0;
    for (int i = 0; i < topic[pi].n; i++) {
        int tk = 0; for (int j = 0; j < ntaken; j++) if (!strcmp(taken[j], topic[pi].c[i].w)) { tk = 1; break; }
        if (!tk) cv_set_add(&cand, topic[pi].c[i].w, topic[pi].c[i].x);
    }
    if (!cand.n && g_bg.ok) {                                            /* the most frequent words of this part of speech */
        for (int round = 0; round < 60; round++) {
            const char *bw = NULL; double bc = -1;
            for (size_t i = 0; i < g_bg.uni.cap; i++) if (g_bg.uni.t[i].k) {
                const char *k = g_bg.uni.t[i].k; if (strlen(k) < 3 || cv_closed(k) || !cv_has_pos(k, pos)) continue;
                int used = 0; for (int j = 0; j < cand.n; j++) if (!strcmp(cand.c[j].w, k)) used = 1; for (int j = 0; j < ntaken; j++) if (!strcmp(taken[j], k)) used = 1;
                if (used) continue;
                if (g_bg.uni.t[i].v > bc || (g_bg.uni.t[i].v == bc && strcmp(k, bw) < 0)) { bc = g_bg.uni.t[i].v; bw = k; }
            }
            if (!bw) break; cv_set_add(&cand, bw, 0.2);
        }
    }
    if (!cand.n) return g_pick;
    cv_knobs kn; cv_knobs_of(&w->tone7, &kn);
    double g = w->ear ? mh_ear_bw_correction(w->ear) : 0.0;
    static double wv[CV_MAXC]; double mx0 = 0;
    for (int i = 0; i < cand.n; i++) {
        double v = pow(cv_p(w, cand.c[i].w, prev), kn.coherence * fmax(0.0, 1.0 + g)) * cand.c[i].x;
        if (cv_is_user(w, cand.c[i].w)) v *= kn.user_boost + w->imitation;
        wv[i] = v; if (v > mx0) mx0 = v;
    }
    if (w->imitation > 0 && w->nuser) for (int i = 0; i < cand.n; i++) if (cv_is_heard(w, cand.c[i].w)) wv[i] = fmax(wv[i], 1.1 * mx0);   /* the child's own ear */
    double mx = 0; for (int i = 0; i < cand.n; i++) if (wv[i] > mx) mx = wv[i];
    int idx[CV_MAXC], m = 0; for (int i = 0; i < cand.n; i++) if (wv[i] >= kn.prune_floor * mx) idx[m++] = i;       /* GABA prunes */
    for (int a = 0; a < m; a++) for (int b = a + 1; b < m; b++) if (cv_cmp_pair(wv[idx[b]], cand.c[idx[b]].w, wv[idx[a]], cand.c[idx[a]].w) > 0) { int t = idx[a]; idx[a] = idx[b]; idx[b] = t; }
    if (m > kn.pool_size) m = kn.pool_size;                                                                          /* NE narrows, GLU widens */
    double tot = 0; for (int i = 0; i < m; i++) tot += wv[idx[i]];
    int pick = kn.novelty_rank < m - 1 ? kn.novelty_rank : m - 1;                                                    /* DA explores down the ranking */
    snprintf(g_pick, 48, "%s", cand.c[idx[pick]].w); *P = wv[idx[pick]] / tot; *ncand = m;
    w->lp_n = m; w->lp_tot = tot; for (int i = 0; i < m && i < CV_MAXC; i++) { snprintf(w->lp_w[i], 48, "%s", cand.c[idx[i]].w); w->lp_v[i] = wv[idx[i]]; }
    return g_pick;
}

/* ── weave_cycle.py: the one step function ──────────────────────────────────────────────────────────── */
static const char *cv_strut_partner(const char *a)
{
    static const char *const P[][2] = {{"GLU", "GABA"}, {"GABA", "GLU"}, {"DA", "5HT"}, {"5HT", "DA"}, {"NE", "OXT"}, {"OXT", "NE"}};
    for (int i = 0; i < 6; i++) if (!strcmp(P[i][0], a)) return P[i][1];
    return NULL;                                                          /* OPI, the hub, has no strut */
}
static int cv_turbulent(const double *v, int n, int *peaks)               /* >= 3 values within half of the largest */
{
    double m = 0; for (int i = 0; i < n; i++) if (v[i] > m) m = v[i];
    int p = 0; if (m > 0) for (int i = 0; i < n; i++) if (v[i] > 0 && v[i] >= 0.5 * m) p++;
    if (peaks) *peaks = p; return p >= 3;
}

/* sentence-scale web step: thin margin -> re-pick the slot under the antagonist tone, keep the sharper pick */
static const char *cv_revisit(cv_win *w, const char *slot, const char *prev, cv_set topic[3], char taken[][48], int ntaken, const char *word, double *P, int *ncand, char *ax, int *lv, int *did)
{
    *did = 0;
    int n0 = w->lp_n; if (n0 <= 0) return word;
    const char *pt = cv_strut_partner(ax); if (!pt) return word;
    double v0[CV_MAXC]; for (int i = 0; i < n0; i++) v0[i] = w->lp_v[i];
    int peaks; if (!cv_turbulent(v0, n0, &peaks)) return word;
    cv_tone keep = w->tone7; cv_tone_from_axis(&w->tone7, pt, *lv / 6.0);
    char first[48]; snprintf(first, 48, "%s", word); double P2; int n2; char alt[48];
    const char *a2 = cv_pick(w, slot, prev, topic, taken, ntaken, &P2, &n2); snprintf(alt, 48, "%s", a2);
    w->tone7 = keep;
    if (strcmp(alt, first) && P2 > *P) { *P = P2; *ncand = n2; snprintf(ax, 8, "%s", pt); *did = 1; snprintf(g_pick, 48, "%s", alt); return g_pick; }
    snprintf(g_pick, 48, "%s", first); return g_pick;
}

/* ── the heard tone, and Pascal's meet-then-lead ─────────────────────────────────────────────────────── */
static void cv_detect_tone(const char *text, char *axis, int *level)
{
    static const char *const LEX[5][24] = {
        {"angry", "anger", "furious", "rage", "hate", "hated", "stupid", "idiot", "damn", "shut", "liar", "never", "always", "worst", "terrible", "awful", "useless", NULL},
        {"sad", "sorry", "grief", "lonely", "hopeless", "tired", "empty", "cry", "crying", "lost", "hurt", "pain", NULL},
        {"great", "love", "wonderful", "excited", "yes", "amazing", "fantastic", "win", "happy", "glad", NULL},
        {"thanks", "thank", "please", "friend", "together", "dear", "kind", "welcome", "care", NULL},
        {"calm", "quiet", "peace", "easy", "gentle", "slow", "rest", "okay", "fine", NULL}};
    static const char *const NAME[5] = {"NE", "OPI", "DA", "OXT", "GABA"};
    int score[5] = {0}; const char *p = text;
    while (*p) {
        if (isalpha((unsigned char)*p) || *p == '\'') { char w[48]; int k = 0; while ((isalpha((unsigned char)*p) || *p == '\'') && k < 46) { w[k++] = (char)tolower((unsigned char)*p); p++; } w[k] = 0; for (int a = 0; a < 5; a++) for (int i = 0; LEX[a][i]; i++) if (!strcmp(LEX[a][i], w)) score[a]++; }
        else p++;
    }
    int bang = 0; for (const char *q = text; *q; q++) if (*q == '!') bang++;
    for (const char *q = text; *q; ) { if (isupper((unsigned char)*q) && (q == text || !isalnum((unsigned char)q[-1]))) { int L = 0; while (isupper((unsigned char)q[L])) L++; if (L >= 3 && !isalnum((unsigned char)q[L])) bang++; q += L ? L : 1; } else q++; }
    if (score[0]) score[0] += bang;
    int best = 0; for (int a = 1; a < 5; a++) if (score[a] > score[best]) best = a;
    if (score[best] == 0) { strcpy(axis, "GABA"); *level = 2; return; }
    snprintf(axis, 8, "%s", NAME[best]); *level = score[best] + 1 > 6 ? 6 : score[best] + 1;
}

static void cv_trajectory(const cv_win *w, int n, char ax[][8], int *lv)
{
    if (w->use_state && w->st.ready) { int a[64], l[64]; if (n > 64) n = 64; mh_state_trajectory(&w->st, n, a, l); for (int i = 0; i < n; i++) { snprintf(ax[i], 8, "%s", MH_AXES[a[i]]); lv[i] = l[i]; } return; }
    int L = w->heard_lv, start = L - 1 < 0 ? 0 : L - 1;                   /* Persuader: meet the heard tone one level below, ease toward the target, arrive on it */
    if (n <= 1) { if (!strcmp(w->heard_name, w->tgt_name)) { snprintf(ax[0], 8, "%s", w->tgt_name); lv[0] = w->tgt_lv; } else { snprintf(ax[0], 8, "%s", w->heard_name); lv[0] = start; } return; }
    for (int k = 0; k < n - 1; k++) { snprintf(ax[k], 8, "%s", w->heard_name); lv[k] = (n - 1 <= 1) ? start : (int)lrint(start * (1.0 - (double)k / (n - 1))); }
    snprintf(ax[n - 1], 8, "%s", w->tgt_name); lv[n - 1] = w->tgt_lv > 6 ? 6 : w->tgt_lv;
}

/* read the speaker's turn: state repass (if the meter is loaded), the heard tone, the words into the ring */
static void cv_read(cv_win *w, const char *text, int echo)
{
    size_t L = strlen(text) + 1; char *body = malloc(L); mh_number nums[32]; mh_split_numbers(text, body, L, nums, 32);          /* numbers are not words */
    if (w->ear && echo == 0) {
        mh_ear_user_turn(w->ear, text, cv_fill(w), &w->st); w->use_state = w->st.ready;
        if (w->use_state) { int a, l; mh_state_heard(&w->st, &a, &l); snprintf(w->heard_name, 8, "%s", MH_AXES[a]); w->heard_lv = l; }
    }
    if (!w->use_state) cv_detect_tone(body, w->heard_name, &w->heard_lv);
    w->nuser = 0; const char *p = body;
    while (*p) {
        if (isalpha((unsigned char)*p) || *p == '\'') {
            char wd[48]; int k = 0; while ((isalpha((unsigned char)*p) || *p == '\'') && k < 46) { wd[k++] = (char)tolower((unsigned char)*p); p++; } wd[k] = 0;
            w->t++;
            if (!cv_closed(wd)) { cv_place(w, wd); if (!cv_is_user(w, wd) && w->nuser < 160) snprintf(w->user[w->nuser++], 48, "%s", wd); }
        } else p++;
    }
    free(body);
}

/* ── write one sentence (SedenionWindow.write) ──────────────────────────────────────────────────────── */
static const char *const CV_FRAME_SVO[] = {"DET", "N", "V", "DET", "N", NULL};
static const char *const CV_FRAME_SVP[] = {"DET", "N", "V", "PREP", "DET", "N", NULL};
static const char *const CV_FRAME_SVA[] = {"DET", "N", "AUX", "ADJ", NULL};

typedef struct { char sentence[512]; char marked[2048]; int nwords; double bits; char tenses_used[16]; } cv_sentence;

static void cv_write(cv_win *w, const char *prompt, const char *tense_in, int depth, int reach, int pl, const char *override_ax, int override_lv, cv_sentence *out)
{
    memset(out, 0, sizeof *out);
    const char *tense = cv_resolve_tense(tense_in, prompt, depth, reach); snprintf(out->tenses_used, 16, "%s", tense);
    static cv_set topic[3]; for (int i = 0; i < 3; i++) topic[i].n = 0;
    size_t Lp = strlen(prompt) + 1; char *body = malloc(Lp); mh_number nums[32]; mh_split_numbers(prompt, body, Lp, nums, 32);
    char toks[80][48]; int nt = 0; const char *p = body;
    while (*p && nt < 80) { if (isalpha((unsigned char)*p) || *p == '\'') { int k = 0; while ((isalpha((unsigned char)*p) || *p == '\'') && k < 46) { toks[nt][k++] = (char)tolower((unsigned char)*p); p++; } toks[nt][k] = 0; nt++; } else p++; }
    free(body);
    int nouns = 0;
    for (int i = 0; i < nt; i++) {
        const char *s = toks[i]; if (cv_closed(s)) continue;
        for (int pi = 0; pi < 3; pi++) {
            int pos = pi + 1; char lb[64]; const char *lem = cv_morphy_pos(s, pos, lb);          /* candidates are lemmas (the verb group inflects them), never the surface form */
            if (lem) { cv_set_add(&topic[pi], lem, 1.0); cv_neighbours(&topic[pi], lem, pos); }
        }
        if (cv_has_pos(s, 1)) nouns++;
    }
    if (w->imitation > 0)                                                  /* a child can say the words it just heard, in the parts of speech it knows them as */
        for (int i = 0; i < nt; i++) {
            const char *s = toks[i]; if (cv_closed(s)) continue; char b[64]; const char *l;
            if ((l = cv_lemma_pos(s, 1, b))) cv_set_add(&topic[0], l, 1.0);
            if ((l = cv_lemma_pos(s, 2, b))) cv_set_add(&topic[1], l, 1.0);
            if (cv_has_pos(s, 3)) cv_set_add(&topic[2], s, 1.0);
        }
    char tr_ax[16][8]; int tr_lv[16];
    char ax0[8]; int lv0; if (override_ax && *override_ax) { snprintf(ax0, 8, "%s", override_ax); lv0 = override_lv; } else { cv_trajectory(w, 1, tr_ax, tr_lv); snprintf(ax0, 8, "%s", tr_ax[0]); lv0 = tr_lv[0]; }
    cv_tone t0; cv_tone_from_axis(&t0, ax0, lv0 / 6.0); cv_knobs kn0; cv_knobs_of(&t0, &kn0);
    const char *const *slots = kn0.short_frame ? CV_FRAME_SVA : (nouns >= 2 ? CV_FRAME_SVO : CV_FRAME_SVP);
    int ns = 0; while (slots[ns]) ns++;
    cv_trajectory(w, ns, tr_ax, tr_lv);
    char taken[16][48]; int ntaken = 0; char prevw[48] = ""; int have_prev = 0; char words[16][96]; int nw_ = 0; w->trace[0] = 0;
    for (int k = 0; k < ns; k++) {
        char ax[8]; int lv; if (override_ax && *override_ax) { snprintf(ax, 8, "%s", override_ax); lv = override_lv; } else { snprintf(ax, 8, "%s", tr_ax[k]); lv = tr_lv[k]; }
        cv_tone_from_axis(&w->tone7, ax, lv / 6.0);
        double P; int nc; const char *wd = cv_pick(w, slots[k], have_prev ? prevw : NULL, topic, taken, ntaken, &P, &nc);
        if (!wd[0]) continue;
        char word[48]; snprintf(word, 48, "%s", wd); int did = 0;
        int content = strcmp(slots[k], "N") == 0 || strcmp(slots[k], "V") == 0 || strcmp(slots[k], "ADJ") == 0;
        if (w->web && content) { wd = cv_revisit(w, slots[k], have_prev ? prevw : NULL, topic, taken, ntaken, word, &P, &nc, ax, &lv, &did); if (wd != word) snprintf(word, 48, "%s", wd); cv_tone_from_axis(&w->tone7, ax, lv / 6.0); }
        out->bits += -log2(P); w->t++;
        char surface[96]; const char *mt = NULL, *conj = "base"; snprintf(surface, sizeof surface, "%s", word);
        if (!strcmp(slots[k], "V")) { cv_inflect(tense, word, pl, 3, surface, sizeof surface, &mt, &conj); }
        else if (!strcmp(slots[k], "AUX") && strcmp(tense, "present") && (IN_SET(SW_AUX, word) && (!strcmp(word, "is") || !strcmp(word, "are") || !strcmp(word, "was") || !strcmp(word, "were") || !strcmp(word, "be") || !strcmp(word, "been") || !strcmp(word, "am") || !strcmp(word, "has") || !strcmp(word, "have") || !strcmp(word, "had")))) {
            int be = !strcmp(word, "has") || !strcmp(word, "have") || !strcmp(word, "had") ? 0 : 1; cv_inflect(tense, be ? "be" : "have", pl, 3, surface, sizeof surface, &mt, &conj);
        }
        if (!mt) mt = !strcmp(slots[k], "V") ? "present" : "base";
        char mk[16]; cv_marker(mk, ax, lv, mt, conj);
        if (content) { cv_place(w, word); snprintf(taken[ntaken++], 48, "%s", word); }
        snprintf(words[nw_++], 96, "%s", surface);
        char tb[160]; snprintf(tb, sizeof tb, "%s%s:%s P=%.3f n=%d <%s:%d|%s|%s>%s", k ? "  " : "", slots[k], surface, P, nc, ax, lv, mt, conj, did ? " (strut)" : "");
        if (strlen(w->trace) + strlen(tb) < sizeof w->trace - 1) strcat(w->trace, tb);
        size_t o = strlen(out->marked); snprintf(out->marked + o, sizeof out->marked - o, "%s%s%s", o ? " " : "", mk, surface);
        snprintf(prevw, 48, "%s", word); have_prev = 1;
    }
    char text[512] = ""; for (int i = 0; i < nw_; i++) { size_t o = strlen(text); snprintf(text + o, sizeof text - o, "%s%s", i ? " " : "", words[i]); }
    if (text[0]) { text[0] = (char)toupper((unsigned char)text[0]); strcat(text, "."); }
    snprintf(out->sentence, sizeof out->sentence, "%s", text); out->nwords = nw_;
}

/* ── monad.cam_encode: the prompt as a unit sedenion (needs SHA-256 for _whash) ────────────────────────── */
static uint32_t cv_sha_first32(const unsigned char *msg, size_t len)
{
    static const uint32_t K[64] = {0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
    uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    size_t total = ((len + 9 + 63) / 64) * 64; unsigned char *m = calloc(total, 1); memcpy(m, msg, len); m[len] = 0x80;
    uint64_t bits = (uint64_t)len * 8; for (int i = 0; i < 8; i++) m[total - 1 - i] = (unsigned char)(bits >> (8 * i));
    #define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
    for (size_t off = 0; off < total; off += 64) {
        uint32_t w[64];
        for (int i = 0; i < 16; i++) w[i] = ((uint32_t)m[off + 4 * i] << 24) | ((uint32_t)m[off + 4 * i + 1] << 16) | ((uint32_t)m[off + 4 * i + 2] << 8) | m[off + 4 * i + 3];
        for (int i = 16; i < 64; i++) { uint32_t s0 = ROR(w[i - 15], 7) ^ ROR(w[i - 15], 18) ^ (w[i - 15] >> 3), s1 = ROR(w[i - 2], 17) ^ ROR(w[i - 2], 19) ^ (w[i - 2] >> 10); w[i] = w[i - 16] + s0 + w[i - 7] + s1; }
        uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
        for (int i = 0; i < 64; i++) {
            uint32_t S1 = ROR(e, 6) ^ ROR(e, 11) ^ ROR(e, 25), ch = (e & f) ^ (~e & g), t1 = hh + S1 + ch + K[i] + w[i], S0 = ROR(a, 2) ^ ROR(a, 13) ^ ROR(a, 22), mj = (a & b) ^ (a & c) ^ (b & c), t2 = S0 + mj;
            hh = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
        }
        h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
    }
    free(m); return h[0];
}
static double cv_whash(const char *w) { return (double)cv_sha_first32((const unsigned char *)w, strlen(w)) / 4294967295.0; }

static void cv_cam_encode(const char *text, double s[16])
{
    for (int i = 0; i < 16; i++) s[i] = 0;
    char *lo = strdup(text); for (char *p = lo; *p; p++) *p = (char)tolower((unsigned char)*p);
    char *words[2048]; int n = 0; for (char *t = strtok(lo, " \t\n\r\f\v"); t && n < 2048; t = strtok(NULL, " \t\n\r\f\v")) words[n++] = t;
    double N = n > 1 ? n : 1; s[0] = log(N + 1.0) / log(512.0);
    for (int i = 0; i < n; i++) {
        const char *w = words[i]; size_t L = strlen(w); double h = cv_whash(w);
        int conj = IN_SET(CAM_CONJUNCTS, w), aux = IN_SET(CAM_AUXILIARIES, w), pron = IN_SET(CAM_PRONOUNS, w);
        s[1] += h / N; if (conj) s[2] += 1 / N;
        int nounsuf = 0; for (int k = 0; k < N_CAM_NOUN_SUFF; k++) if (cv_ends(w, CAM_NOUN_SUFF[k])) nounsuf = 1;
        int adjsuf = 0; for (int k = 0; k < N_CAM_ADJ_SUFF; k++) if (cv_ends(w, CAM_ADJ_SUFF[k])) adjsuf = 1;
        int is_verb = aux || cv_ends(w, "ing") || cv_ends(w, "ed") || (cv_ends(w, "s") && L >= 4 && !cv_ends(w, "ss") && !cv_ends(w, "us") && !nounsuf);
        int is_adj = cv_ends(w, "ly") || cv_ends(w, "ful") || cv_ends(w, "ous") || adjsuf;
        if (!pron && !aux && !conj && !IN_SET(CAM_TIME, w) && !IN_SET(CAM_QUESTION, w) && !IN_SET(CAM_DETERMINERS, w) && !IN_SET(CAM_META, w) && !IN_SET(CAM_AFF_POS, w) && !IN_SET(CAM_AFF_NEG, w) && L >= 4 && !is_verb && !is_adj) s[3] += 1 / N;
        if (is_verb) s[4] += 1 / N; if (is_adj) s[5] += 1 / N;
        if (IN_SET(CAM_NEGATION, w) || conj) s[6] += 1 / N;
        if (IN_SET(CAM_TIME, w) || !strcmp(w, "was") || !strcmp(w, "were") || !strcmp(w, "will") || !strcmp(w, "would") || !strcmp(w, "has") || !strcmp(w, "have") || !strcmp(w, "had")) s[7] += 1 / N;
        if (pron) s[8] += 1 / N;
        if (!pron && !aux && L >= 3) s[9] += h * 0.5 / N;
        if (IN_SET(CAM_QUESTION, w)) s[10] += 1 / N;
        static const char *const IT[] = {"it", "its", "they", "them", "their", "he", "she", "who", "which", NULL}; if (cv_word_is(w, IT)) s[11] += 1 / N;
        static const char *const TH[] = {"the", "already", "again", "still", "even", "also", "too", NULL}; if (cv_word_is(w, TH)) s[12] += 1 / N;
        s[13] += (double)L / 12.0 / N;
        if (IN_SET(CAM_AFF_POS, w)) s[14] += 1 / N; else if (IN_SET(CAM_AFF_NEG, w)) s[14] -= 1 / N;
        if (IN_SET(CAM_META, w)) s[15] += 1 / N;
    }
    if (s[14] < 0) s[14] = 0;
    for (int i = 1; i < 16; i++) if (s[i] < CAM_GAP) s[i] = CAM_GAP;
    /* _snorm_unit: the sedenion norm is the Euclidean norm of the 16 components */
    double nr = 0; for (int i = 0; i < 16; i++) nr += s[i] * s[i]; nr = sqrt(nr);
    for (int i = 0; i < 16; i++) s[i] = nr > 1e-15 ? s[i] / nr : 0.0;
    free(lo);
}

/* ── the scaled boxkite orbweaver (scaled_boxkite_orbweaver_monad.py) ─────────────────────────────────── */
static const char *const CV_REL[19] = {"hypernyms", "instance_hypernyms", "hyponyms", "instance_hyponyms", "member_holonyms", "substance_holonyms", "part_holonyms", "member_meronyms", "substance_meronyms",
                                       "part_meronyms", "attributes", "entailments", "causes", "also_sees", "verb_groups", "similar_tos", "topic_domains", "region_domains", "usage_domains"};
static const char *const CV_DIR_OF_REL[19] = {"classify", "classify", "enumerate", "enumerate", "situate", "situate", "situate", "decompose", "decompose", "decompose", "characterize", "imply", "explain",
                                              "associate", "compare", "compare", "contextualize", "localize", "register"};
static const char *cv_infer_direction(const int *v)                      /* ptolemy_monad.infer_direction: hyper/hyponyms are branching, the fallback, not the default */
{
    int any = 0; for (int i = 0; i < 19; i++) if (v[i]) any = 1;
    if (!any) return "observe";
    int idx = -1; for (int i = 4; i < 19; i++) if (v[i] && (idx < 0 || v[i] > v[idx])) idx = i;
    if (idx < 0) { idx = 0; for (int i = 1; i < 19; i++) if (v[i] > v[idx]) idx = i; }
    return CV_DIR_OF_REL[idx];
}

static const char *const CV_CONN[][8] = {                                  /* the connective lexicon (closed class); choice is a fixed rotation, not Python's random */
    /*0 throughline*/ {"because", "therefore", "thus", "hence", "so", "it follows that", NULL},
    /*1 elaborate*/   {"specifically", "more precisely", "in detail", "that is", "in other words", NULL},
    /*2 wrap*/        {"in sum", "on the whole", "overall", "in short", "to summarise", NULL},
    /*3 reverse*/     {"but", "however", "yet", "that said", "conversely", "on the other hand", NULL}};
static int g_conn_i = 0;
static const char *cv_conn(int cls) { int n = 0; while (CV_CONN[cls][n]) n++; return CV_CONN[cls][(g_conn_i++) % n]; }

typedef struct { int kind; int depth; char radius[16]; char seed[512]; char conn[24]; char tense[12]; char tone[8]; int tone_lv; char sentence[640]; char marked[2048]; } cv_piece;
typedef struct {
    char text[4096]; cv_piece pieces[12]; int np;
    int reach, turbulent, peaks; char regime[12]; double ratio; char dirs[6][16]; int ndirs;
    int rv[19]; int nwords, nunknown; int nnums; char tenses[12][12];
} cv_comp;

static void cv_room(const char *body, const char *w0, int peaks, double *ratio, char *regime, int *reach, int cap)
{
    double f1[16], f2[16]; char bridge[256]; snprintf(bridge, sizeof bridge, "it belongs to the domain of %s.", w0);
    cv_cam_encode(body, f1); cv_cam_encode(bridge, f2);
    double c = 0; for (int i = 0; i < 16; i++) c += (f1[i] - f2[i]) * (f1[i] - f2[i]); c = sqrt(c); if (c == 0) c = 1e-9;
    double n1 = 0; for (int i = 0; i < 16; i++) n1 += f1[i] * f1[i]; n1 = sqrt(n1); if (n1 == 0) n1 = 1e-9;
    double b = n1 / (1.0 + 0.5 * peaks); *ratio = b / c;
    strcpy(regime, *ratio > 1.15 ? "continuous" : *ratio >= 0.9 ? "lemniscate" : "discrete");
    int r = !strcmp(regime, "continuous") ? 1 : !strcmp(regime, "lemniscate") ? 2 : 3 + (*ratio < 0.6 ? 1 : 0); *reach = r > cap ? cap : r < 1 ? 1 : r;
}

static void cv_emit(cv_win *w, cv_comp *c, int kind, int depth, int rdir, const char *conn, const char *tense, const char *oax, int olv, char owned[6][512])
{
    if (c->np >= 12) return;
    cv_piece *pc = &c->pieces[c->np]; memset(pc, 0, sizeof *pc); pc->kind = kind; pc->depth = depth;
    snprintf(pc->radius, 16, "%s", c->dirs[rdir]); snprintf(pc->seed, sizeof pc->seed, "%s", owned[rdir]); snprintf(pc->conn, 24, "%s", conn); snprintf(pc->tense, 12, "%s", tense);
    if (oax) { snprintf(pc->tone, 8, "%s", oax); pc->tone_lv = olv; }
    cv_sentence sn; cv_write(w, pc->seed[0] ? pc->seed : "it", tense, -1, -1, 0, oax, olv, &sn);
    if (!sn.sentence[0]) return;
    char lead[24]; snprintf(lead, sizeof lead, "%s", conn); lead[0] = (char)toupper((unsigned char)lead[0]);
    char b2[512]; snprintf(b2, sizeof b2, "%s", sn.sentence); b2[0] = (char)tolower((unsigned char)b2[0]);
    snprintf(pc->sentence, sizeof pc->sentence, "%s, %s", lead, b2); snprintf(pc->marked, sizeof pc->marked, "%s", sn.marked);
    snprintf(c->tenses[c->np], 12, "%s", tense); c->np++;
}

static void cv_compose(cv_win *w, const char *text, int max_pieces, cv_comp *c)
{
    memset(c, 0, sizeof *c);
    size_t Lt = strlen(text) + 1; char *body = malloc(Lt); mh_number nums[64]; c->nnums = mh_split_numbers(text, body, Lt, nums, 64);
    char content[64][48]; int nc = 0; const char *p = body;                         /* tokens [A-Za-z][A-Za-z'-]+ , unique, not closed, >= 3 letters */
    while (*p && nc < 64) {
        if (isalpha((unsigned char)*p) && (unsigned char)*p < 0x80) {
            char wd[48]; int k = 0; while (((isalpha((unsigned char)*p) || *p == '\'' || *p == '-') && (unsigned char)*p < 0x80) && k < 46) { wd[k++] = (char)tolower((unsigned char)*p); p++; } wd[k] = 0;
            if (k < 3 || cv_closed(wd)) continue;
            int dup = 0; for (int i = 0; i < nc; i++) if (!strcmp(content[i], wd)) dup = 1;
            if (!dup) snprintf(content[nc++], 48, "%s", wd);
        } else p++;
    }
    char known[64][48]; int nk = 0; int dirw[64]; const char *wdir[64]; int rv[19] = {0};
    for (int i = 0; i < nc; i++) {
        const int16_t *vec; if (!cv_entry(content[i], NULL, &vec)) { c->nunknown++; continue; }
        int v[19]; int any = 0; for (int j = 0; j < 19; j++) { v[j] = vec[j]; if (v[j]) any = 1; rv[j] += v[j]; }
        snprintf(known[nk], 48, "%s", content[i]); wdir[nk] = any ? cv_infer_direction(v) : "observe"; dirw[nk] = 0; nk++;
    }
    memcpy(c->rv, rv, sizeof rv); c->nwords = nk;
    int turb = 0, peaks = 0; { double dv[19]; for (int i = 0; i < 19; i++) dv[i] = rv[i]; turb = cv_turbulent(dv, 19, &peaks); }
    c->turbulent = turb; c->peaks = peaks;
    cv_room(body, nk ? known[0] : "it", peaks, &c->ratio, c->regime, &c->reach, 4);
    int naxes = c->reach + 1 > (nk > 1 ? nk : 1) ? (nk > 1 ? nk : 1) : c->reach + 1; if (naxes < 1) naxes = 1;
    int v[19]; memcpy(v, rv, sizeof v); c->ndirs = 0;                               /* _ranked_directions */
    for (int it = 0; it < naxes; it++) {
        int any = 0; for (int j = 0; j < 19; j++) if (v[j]) any = 1; if (!any) break;
        const char *d = cv_infer_direction(v); int dup = 0; for (int j = 0; j < c->ndirs; j++) if (!strcmp(c->dirs[j], d)) dup = 1;
        if (!dup && c->ndirs < 6) snprintf(c->dirs[c->ndirs++], 16, "%s", d);
        int mi = 0; for (int j = 1; j < 19; j++) if (v[j] > v[mi]) mi = j; v[mi] = 0;
    }
    if (!c->ndirs) snprintf(c->dirs[c->ndirs++], 16, "observe");
    char owned[6][512]; int nown[6] = {0}; for (int i = 0; i < c->ndirs; i++) owned[i][0] = 0;
    for (int i = 0; i < nk; i++) {
        int di = -1; for (int j = 0; j < c->ndirs; j++) if (!strcmp(c->dirs[j], wdir[i])) di = j;
        if (di < 0) di = nown[0] % c->ndirs;
        size_t o = strlen(owned[di]); snprintf(owned[di] + o, sizeof owned[di] - o, "%s%s", o ? " " : "", known[i]); nown[di]++;
    }
    for (int i = 0; i < c->ndirs; i++) if (!owned[i][0] && nk) snprintf(owned[i], sizeof owned[i], "%s", known[i % nk]);
    char heard_axis[8]; snprintf(heard_axis, 8, "%s", w->use_state && w->st.ready ? w->heard_name : w->heard_name); int heard_lv = w->heard_lv;
    int first = 1; g_conn_i = 0;
    for (int depth = c->reach; depth >= 1; depth--) {
        const char *tense = cv_lemniscate_tense(depth, c->reach);
        for (int pos = 0; pos < c->ndirs; pos++) {
            if (c->np >= max_pieces) break;
            cv_emit(w, c, 0, depth, pos, cv_conn(first ? 0 : 1), tense, NULL, 0, owned); first = 0;
            if (turb && depth == c->reach && pos < c->ndirs - 1 && c->np < max_pieces) {          /* the eddy: reverse along the strut, then recap from the hub radius */
                const char *oax = cv_strut_partner(heard_axis); if (!oax) oax = "GABA";
                cv_emit(w, c, 1, depth, pos, cv_conn(3), tense, oax, heard_lv, owned);
                cv_emit(w, c, 2, depth, 0, cv_conn(2), tense, NULL, 0, owned);
            }
        }
    }
    c->text[0] = 0; for (int i = 0; i < c->np; i++) { size_t o = strlen(c->text); snprintf(c->text + o, sizeof c->text - o, "%s%s", i ? " " : "", c->pieces[i].sentence); }
    free(body);
}

/* ── the audit (the bench's seven checks, as straight text) ────────────────────────────────────────────── */
static void cv_audit(const cv_win *w, const cv_comp *c, char *out, size_t sz)
{
    int no_num = 1; for (const char *p = c->text; *p; p++) if (isdigit((unsigned char)*p)) no_num = 0;
    static const char *const TEMPL[] = {"this is a kind of", "it includes", "it is made of", "it is part of", "it is marked by", "it happens because of", "it leads to", "it relates to", "it resembles", "it belongs to the domain of", "it is found in", "it is used in", NULL};
    char low[4096]; snprintf(low, sizeof low, "%s", c->text); for (char *p = low; *p; p++) *p = (char)tolower((unsigned char)*p);
    int no_tmpl = 1; for (int i = 0; TEMPL[i]; i++) if (strstr(low, TEMPL[i])) no_tmpl = 0;
    int st_ok = 1, mk_ok = 1, stations = 1;
    for (int i = 0; i < c->np; i++) {
        const cv_piece *p = &c->pieces[i];
        if (p->kind == 0 && strcmp(p->tense, cv_lemniscate_tense(p->depth, c->reach))) st_ok = 0;
        if (strcmp(p->tense, "past") && strcmp(p->tense, "present") && strcmp(p->tense, "future")) stations = 0;
        if (p->kind == 0 && !p->marked[0]) mk_ok = 0;
    }
    int known_ok = 1; const char *q = c->text;
    while (*q) {
        if (isalpha((unsigned char)*q)) {
            char wd[48]; int k = 0; while ((isalpha((unsigned char)*q) || *q == '\'') && k < 46) { wd[k++] = (char)tolower((unsigned char)*q); q++; } wd[k] = 0;
            char b[64]; int ok = cv_closed(wd) || cv_entry(wd, NULL, NULL) || cv_lemma_pos(wd, 1, b) || cv_lemma_pos(wd, 2, b) || cv_is_user(w, wd);
            for (int a = 0; a < 4 && !ok; a++) for (int i = 0; CV_CONN[a][i]; i++) if (strstr(CV_CONN[a][i], wd)) ok = 1;
            static const char *const EXTRA[] = {"will", "would", "have", "has", "had", "been", "being", "be", NULL}; if (cv_word_is(wd, EXTRA)) ok = 1;
            if (!ok) known_ok = 0;
        } else q++;
    }
    int pivot_ok = 1; for (int i = 0; i < c->np; i++) if (c->pieces[i].kind == 1 && !c->turbulent) pivot_ok = 0;
    snprintf(out, sz, "audit: no_numerals=%d no_template_phrase=%d tense_is_the_lemniscate_station=%d every_paragraph_sentence_carries_its_tense_marker=%d every_word_is_known_or_heard=%d a_pivot_only_when_turbulent=%d stations_are_the_three=%d",
             no_num, no_tmpl, st_ok, mk_ok, known_ok, pivot_ok, stations);
}

/* ── the resident child: one user turn in, one reply out ────────────────────────────────────────────────── */
static cv_win g_win; static int g_win_ready = 0; static cv_comp g_last; static int g_turns = 0; static char g_tense_force[24] = ""; static int g_last_valid = 0;
static char g_last_audit[600] = "";

static void cv_open(void)
{
    if (g_win_ready) return;
    memset(&g_win, 0, sizeof g_win); cv_eng_names();
    char path[700]; snprintf(path, sizeof path, "%s/../english_corpus.txt", g_ptol_dir);
    FILE *f = fopen(path, "r"); if (!f) { snprintf(path, sizeof path, "%s/corpora/english_grammar.txt", g_ptol_dir); f = fopen(path, "r"); }
    if (f) { fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET); char *buf = malloc((size_t)n + 1); size_t r = fread(buf, 1, (size_t)n, f); buf[r] = 0; fclose(f); cv_bg_fit(&g_bg, buf); free(buf); }
    const char *ud = getenv("PTOL_USAGE_DIR"); char dir[700];
    if (ud && *ud) snprintf(dir, sizeof dir, "%s", ud); else { const char *h = getenv("HOME"); snprintf(dir, sizeof dir, "%s/.ptolemy/usage_c", h ? h : "."); }
    { char cmd[760]; snprintf(cmd, sizeof cmd, "mkdir -p '%s'", dir); if (system(cmd)) { /* no state dir: the ear still works in memory */ } }
    g_win.ear = mh_ear_open(dir, g_ptol_dir, cv_known, cv_pgen, NULL);
    g_win.imitation = 2; g_win.web = 1; snprintf(g_win.tgt_name, 8, "GABA"); g_win.tgt_lv = 3; snprintf(g_win.heard_name, 8, "GABA"); g_win.heard_lv = 2;
    cv_tone_from_axis(&g_win.tone7, "GABA", 0.3); g_win_ready = 1;
}

static void cv_close(void) { if (g_win_ready && g_win.ear) { mh_ear_close(g_win.ear); g_win.ear = NULL; } }

static void cv_turn(const char *prompt, char *reply, size_t rsz)
{
    cv_open(); char pair[24]; snprintf(pair, sizeof pair, "t%d", ++g_turns);
    mh_ear_hear(g_win.ear, prompt, MH_EXTERNAL, pair);                    /* the user's words are counted and priced before they are answered */
    cv_read(&g_win, prompt, 0);
    if (g_tense_force[0] && strcmp(g_tense_force, "auto")) {
        cv_sentence sn; cv_write(&g_win, prompt, g_tense_force, -1, -1, 0, NULL, 0, &sn); snprintf(reply, rsz, "%s", sn.sentence);
        memset(&g_last, 0, sizeof g_last); g_last_valid = 0;
    } else { cv_compose(&g_win, prompt, 3, &g_last); g_last_valid = 1; snprintf(reply, rsz, "%s", g_last.text); cv_audit(&g_win, &g_last, g_last_audit, sizeof g_last_audit); }
    if (!reply[0]) snprintf(reply, rsz, "(I have no words for that yet)");
    mh_ear_hear(g_win.ear, reply, MH_INTERNAL, pair);                     /* the reply is priced, completes the pair, and moves the Broca-Wernicke drift for the next turn */
}

static void cv_command(const char *cmd, char *out, size_t sz)
{
    cv_open(); const char *c = cmd + 1;
    if (!strncmp(c, "help", 4) || !*c) {
        snprintf(out, sz, "I am a child learning English; talk to me. Commands: /state (what I hear of you) /drift (Broca-Wernicke) /numbers (numbers are not words) /plan (the last web) /trace (the last sentence, word by word) "
                          "/audit /tense <name|auto> (e.g. /tense past perfect) /legacy <text> (the old word-shadow voice)");
    } else if (!strncmp(c, "state", 5)) {
        if (!g_win.use_state) { snprintf(out, sz, "state meter: %s; heard tone %s:%d (lexicon fallback)", g_win.ear ? "user_state.bin absent" : "no ear", g_win.heard_name, g_win.heard_lv); return; }
        const mh_state *s = &g_win.st; size_t o = (size_t)snprintf(out, sz, "heard %s:%d  held=%d healed=%d/14 k_eff=%.3f | mix", g_win.heard_name, g_win.heard_lv, s->held, s->healed, s->k_eff);
        for (int a = 0; a < MH_NAX && o < sz; a++) o += (size_t)snprintf(out + o, sz - o, " %s %.2f", MH_AXES[a], s->mix[a]);
        if (o < sz) o += (size_t)snprintf(out + o, sz - o, " | target");
        for (int a = 0; a < MH_NAX && o < sz; a++) o += (size_t)snprintf(out + o, sz - o, " %s %.2f", MH_AXES[a], s->target[a]);
    } else if (!strncmp(c, "drift", 5) || !strncmp(c, "numbers", 7)) { mh_ear_report(g_win.ear, out, sz);
    } else if (!strncmp(c, "plan", 4)) {
        if (!g_last_valid) { snprintf(out, sz, "no web yet (say something; or /tense auto)"); return; }
        size_t o = (size_t)snprintf(out, sz, "reach %d regime %s (b/c %.3f) turbulent %d peaks %d words %d unknown %d numbers %d | radii", g_last.reach, g_last.regime, g_last.ratio, g_last.turbulent, g_last.peaks, g_last.nwords, g_last.nunknown, g_last.nnums);
        for (int i = 0; i < g_last.ndirs && o < sz; i++) o += (size_t)snprintf(out + o, sz - o, " %s", g_last.dirs[i]);
        if (o < sz) o += (size_t)snprintf(out + o, sz - o, " | pieces");
        for (int i = 0; i < g_last.np && o < sz; i++) o += (size_t)snprintf(out + o, sz - o, " [%s d%d %s %s]", g_last.pieces[i].kind == 0 ? "para" : g_last.pieces[i].kind == 1 ? "pivot" : "wrap", g_last.pieces[i].depth, g_last.pieces[i].radius, g_last.pieces[i].tense);
    } else if (!strncmp(c, "trace", 5)) { snprintf(out, sz, "%s", g_win.trace[0] ? g_win.trace : "(nothing written yet)");
    } else if (!strncmp(c, "audit", 5)) { snprintf(out, sz, "%s", g_last_valid ? g_last_audit : "(no web yet)");
    } else if (!strncmp(c, "tense", 5)) {
        const char *a = c + 5; while (*a == ' ') a++;
        if (!*a) { snprintf(out, sz, "tense: %s (name, compound like 'future progressive', 'auto' = the lemniscate, 'mirror' = yours)", g_tense_force[0] ? g_tense_force : "auto"); return; }
        snprintf(g_tense_force, sizeof g_tense_force, "%s", a); snprintf(out, sz, "tense: %s%s", a, !strcmp(a, "auto") ? " (the lemniscate decides, sentence by sentence)" : " (one sentence per turn in this tense)");
    } else snprintf(out, sz, "unknown command %s (try /help)", cmd);
}

/* the sedenion geometry numbers the chat frame carries (sigma, Gamma, primes), as console_speak computes them */
static void cv_geometry(const char *prompt, double *sig, double *gam, char primes[128])
{
    primes[0] = 0; *sig = 0.5; *gam = 0.0; int n = (int)strlen(prompt); if (n <= 0) return;
    double v[16], norm = 0, peak = 0; for (int k = 0; k < 16; k++) { _x[k] = project((const unsigned char *)prompt, n, k, 0.5); norm += _x[k] * _x[k]; if (fabs(_x[k]) > peak) peak = fabs(_x[k]); }
    norm = sqrt(norm); for (int k = 0; k < 16; k++) v[k] = norm > 0 ? _x[k] / norm : 0;
    double u; measure_gamma(v, gam, &u); *sig = measure_sigma(v);
    size_t po = 0; double thresh = peak / MONAD_PHI; for (int k = 0; k < 16; k++) if (fabs(_x[k]) >= thresh) { int wr = snprintf(primes + po, 128 - po, "%s%d", po ? " " : "", P[k]); if (wr < 0 || (size_t)wr >= 128 - po) break; po += (size_t)wr; }
}

/* ── ptol -P : the probe the Python test bench drives (tests/test_c_parity.py); one command per line on stdin ─────────────────────── */
static int cv_probe(void)
{
    char line[8192]; cv_open();
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line); if (L && line[L - 1] == '\n') line[--L] = 0;
        if (line[0] == 'V') {                                             /* V spec|lemma|pl|person */
            char *a = line + 2, *b = strchr(a, '|'), *c2 = b ? strchr(b + 1, '|') : NULL, *d = c2 ? strchr(c2 + 1, '|') : NULL; if (!d) continue; *b = *c2 = *d = 0;
            char sf[160]; const char *mt, *cj; cv_inflect(a, b + 1, atoi(c2 + 1), atoi(d + 1), sf, sizeof sf, &mt, &cj);
            cv_tspec ts; cv_parse_tense(a, &ts); int w[6], st[6], ln[6], n = cv_verb_group(&ts, w), nf = cv_duval(w, n, st, ln);
            printf("V\t%s\t%s\t%s\t%d\t%d", sf, mt, cj, n, nf); for (int i = 0; i < n; i++) printf("\t%d", w[i]); printf("\n");
        } else if (line[0] == 'T') { int d, r; sscanf(line + 2, "%d %d", &d, &r); printf("T\t%s\n", cv_lemniscate_tense(d, r));
        } else if (line[0] == 'M') { printf("M\t%s\n", cv_mirror_tense(line + 2));
        } else if (line[0] == 'C') { double s[16]; cv_cam_encode(line + 2, s); printf("C"); for (int i = 0; i < 16; i++) printf("\t%.12f", s[i]); printf("\n");
        } else if (line[0] == 'G') { char *b = strchr(line + 2, '|'); const char *prev = NULL; if (b) { *b = 0; prev = b + 1; if (!*prev) prev = NULL; } printf("G\t%.12g\n", cv_bg_p(&g_bg, line + 2, prev));
        } else if (line[0] == 'O') {                                      /* O text : the plan of the orbweaver */
            cv_comp c; cv_win tmp = g_win; tmp.web = 0; cv_compose(&tmp, line + 2, 0, &c);
            printf("O\t%d\t%s\t%.9f\t%d\t%d\t%d\t%d", c.reach, c.regime, c.ratio, c.turbulent, c.peaks, c.nwords, c.nunknown);
            printf("\t"); for (int i = 0; i < c.ndirs; i++) printf("%s%s", i ? "," : "", c.dirs[i]); printf("\t"); for (int i = 0; i < 19; i++) printf("%s%d", i ? "," : "", c.rv[i]); printf("\n");
        } else if (line[0] == 'N') { cv_tspec t; (void)t; printf("N\t%d\n", N_VERB_FORMS);
        } else if (line[0] == 'W') {                                      /* W tense|prompt : write one sentence, no state ear, web on */
            char *b = strchr(line + 2, '|'); if (!b) continue; *b = 0; cv_win *w = &g_win; mh_ear *keep = w->ear; w->ear = NULL; w->use_state = 0;
            cv_read(w, b + 1, 1); cv_sentence sn; cv_write(w, b + 1, line + 2, -1, -1, 0, NULL, 0, &sn); w->ear = keep;
            printf("W\t%s\t%s\n", sn.sentence, w->trace);
        } else if (line[0] == 'E') {                                      /* E word : the combined store's first-sense entry */
            int pos; const int16_t *v; if (!cv_entry(line + 2, &pos, &v)) { printf("E\tNONE\n"); }
            else { printf("E\t%d", pos); for (int i = 0; i < 19; i++) printf("\t%d", v[i]); printf("\n"); }
        } else if (line[0] == 'Q') { printf("Q\t%d\t%d\n", g_win.ear ? 1 : 0, g_m3h ? (int)g_m3h->n_words : 0); }
        fflush(stdout);
    }
    cv_close(); return 0;
}

/* gr_report, added 2026-09-21: "word=+0.123 word2=-0.456 ..." — each
 * firing word's real Gamma-Radial Windspeed (monad3_word_gamma_radial(),
 * the WordNet-relational fold), alongside gam_out which stays exactly
 * what it always was — measure_gamma()'s sedenion-projection amplitude,
 * a different quantity, not touched. May be NULL (both call sites below
 * still work either way); a word with no store hit, or an all-zero
 * relation vector, is simply left out of the report, not printed as 0. */
static void console_speak(const char *prompt, char out[1024],
                          double *sig_out, double *gam_out, char primes[128],
                          char gr_report[256])
{
    out[0] = '\0';
    primes[0] = '\0';
    if (gr_report) gr_report[0] = '\0';
    if (sig_out) *sig_out = 0.5;
    if (gam_out) *gam_out = 0.0;

    int n = (int)strlen(prompt);
    if (n <= 0) { strncpy(out, "(empty prompt)", 1024); return; }

    double v[16], norm = 0.0, peak = 0.0;
    for (int k = 0; k < 16; k++) {
        _x[k]  = project((const unsigned char *)prompt, n, k, 0.5); /* Eye H */
        norm  += _x[k] * _x[k];
        if (fabs(_x[k]) > peak) peak = fabs(_x[k]);
    }
    norm = sqrt(norm);
    for (int k = 0; k < 16; k++) v[k] = (norm > 0.0) ? _x[k] / norm : 0.0;

    double thresh      = peak / MONAD_PHI;
    double thresh_norm = (norm > 0.0) ? thresh / norm : 0.0;

    int idx[16];
    for (int k = 0; k < 16; k++) idx[k] = k;
    qsort(idx, 16, sizeof(int), cmp_mag_asc);

    char words[16][256], elem[64];
    memset(words, 0, sizeof(words));
    get_monad_words(v, _x, thresh, words, elem);

    /* Spiral order (ZD -> great circle), DISTINCT words only. A degenerate
     * prompt ("hello") fires the same nearest word on every shell and the
     * layer can hand back several copies per shell — the shadow is the SET
     * the path lands on, each word once. (Sentence-mode placeholder; the
     * real assembler is future work — see Tuning-the-Engine/36.) */
    char seen[16][64];
    int  nseen = 0;
    size_t o = 0;
    for (int i = 0; i < 16 && o < 1024; i++) {
        int k = idx[i];
        if (fabs(v[k]) < thresh_norm || !words[k][0]) continue;
        char cell[256];
        strncpy(cell, words[k], sizeof cell - 1);
        cell[sizeof cell - 1] = '\0';
        for (char *tok = strtok(cell, " \t"); tok; tok = strtok(NULL, " \t")) {
            int dup = 0;
            for (int s = 0; s < nseen; s++)
                if (strcmp(seen[s], tok) == 0) { dup = 1; break; }
            if (dup) continue;
            if (nseen < 16) {
                strncpy(seen[nseen], tok, 63);
                seen[nseen][63] = '\0';
                nseen++;
            }
            int wr = snprintf(out + o, 1024 - o, "%s%s", o ? " " : "", tok);
            if (wr < 0 || (size_t)wr >= 1024 - o) { o = 1024; break; }
            o += (size_t)wr;
        }
    }
    if (o == 0) strncpy(out, "(no words fired)", 1024);

    if (gr_report) {
        size_t go = 0;
        for (int s = 0; s < nseen; s++) {
            double gr;
            if (!monad3_word_gamma_radial(seen[s], &gr) || isnan(gr)) continue;
            int wr = snprintf(gr_report + go, 256 - go, "%s%s=%+.3f",
                              go ? " " : "", seen[s], gr);
            if (wr < 0 || (size_t)wr >= 256 - go) break;
            go += (size_t)wr;
        }
    }

    double gam, u;
    measure_gamma(v, &gam, &u);
    if (sig_out) *sig_out = measure_sigma(v);
    if (gam_out) *gam_out = gam;

    /* Sentence mode is the default voice: hand the same firing words + Γ
     * to the real creator; overwrite `out` only on a clean return, else
     * the word bag built above stands as the guaranteed fallback. */
    if (nseen > 0) {
        char act[24], sentence[1024];
        infer_speech_act(prompt, act);
        if (get_monad_sentence(gam, act, seen, nseen, sentence)) {
            strncpy(out, sentence, 1024 - 1);
            out[1024 - 1] = '\0';
        }
    }

    size_t po = 0;
    for (int k = 0; k < 16; k++)
        if (fabs(_x[k]) >= thresh) {
            int wr = snprintf(primes + po, 128 - po, "%s%d", po ? " " : "", P[k]);
            if (wr < 0 || (size_t)wr >= 128 - po) break;
            po += (size_t)wr;
        }
}

static int run_console(int argc, char *argv[], int argstart)
{
    (void)argc; (void)argv; (void)argstart;

    char console_py[600], venv_py[600];
    snprintf(console_py, sizeof console_py,
             "%s/../../PtolemyDesktop/ptolemy_console.py", g_ptol_dir);
    snprintf(venv_py, sizeof venv_py,
             "%s/../../PtolemyDesktop/.venv/bin/python3", g_ptol_dir);
    if (access(venv_py, X_OK) != 0)
        snprintf(venv_py, sizeof venv_py, "/usr/bin/python3");
    /* test hooks: PTOL_CONSOLE_PY / PTOL_PY replace the console script / interpreter (tests/test_c_parity.py drives the frame link with a scripted console) */
    { const char *o = getenv("PTOL_CONSOLE_PY"); if (o && *o) snprintf(console_py, sizeof console_py, "%s", o); o = getenv("PTOL_PY"); if (o && *o) snprintf(venv_py, sizeof venv_py, "%s", o); }
    if (access(console_py, R_OK) != 0) {
        fprintf(stderr, "ptol -w: console not found: %s\n", console_py);
        return 1;
    }

    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) != 0) {
        perror("ptol -w: socketpair");
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) { perror("ptol -w: fork"); return 1; }

    if (pid == 0) {
        /* child: console keeps the tty (curses); frame link is fd 3 */
        close(sv[0]);
        if (sv[1] != 3) { dup2(sv[1], 3); close(sv[1]); }
        setenv("PTOL_HARNESS_FD", "3", 1);
        char *py_argv[8];
        int na = 0;
        py_argv[na++] = venv_py;
        py_argv[na++] = console_py;
        py_argv[na++] = (char *)"--harness";
        py_argv[na++] = (char *)"3";
        py_argv[na]   = NULL;
        execv(venv_py, py_argv);
        perror("ptol -w: exec ptolemy_console.py failed");
        _exit(127);
    }

    /* parent: resident monad — answer frames until the console goes away */
    close(sv[1]);
    signal(SIGPIPE, SIG_IGN);
    mh_harness *h = mh_open(sv[0], sv[0]);
    if (!h) { close(sv[0]); return 1; }

    /* Ptolemy is the Monad + Harness together, so radio frames (Aule's
     * face-posts and judgements, routed through the support-line grammar)
     * fold into THIS Monad -- the same core answering say/cmd below, never
     * a side channel. mh_pump() intercepts them transparently; everything
     * else reaches this loop exactly as mh_recv() already delivered it. */
    Monad *g_monad = monad_create(MONAD_N_DEFAULT);

    char mode[16] = "sentence";
    for (;;) {
        mh_frame fr;
        int g = mh_pump(h, g_monad, &fr, -1);
        if (g < 0) break;
        if (g == 0) continue;

        if (strcmp(fr.t, "say") == 0 || strcmp(fr.t, "cmd") == 0) {
            char reply[1024], primes[128], gr_report[256];
            double sig, gam;
            /* 2026-11-25: the default voice is the child (cv_turn: the harness hears, the state is read, the orbweaver plans, the window picks every word,
             * the Lyndon verb group inflects, the reply is priced and moves the drift).  Plain text in, plain text out.  /legacy <text> still reaches the old
             * word-shadow console_speak(); mode "legacy" makes it the default again. */
            if (fr.text[0] == '/' && strncmp(fr.text, "/legacy ", 8) != 0) {
                cv_command(fr.text, reply, sizeof reply); cv_geometry(fr.text, &sig, &gam, primes);
            } else if (strcmp(mode, "legacy") == 0 || strncmp(fr.text, "/legacy ", 8) == 0) {
                console_speak(strncmp(fr.text, "/legacy ", 8) == 0 ? fr.text + 8 : fr.text, reply, &sig, &gam, primes, gr_report);
            } else {
                cv_turn(fr.text, reply, sizeof reply); cv_geometry(fr.text, &sig, &gam, primes);
            }
            /* gr_report is computed but not yet on the wire — mh_send_chat's
             * frame format (and ptolemy_console.py's parser on the other
             * end) is untouched this pass, on purpose: that's the live,
             * recently-verified (Phase 36) interactive path, and extending
             * it needs its own tested pass, not a same-sitting add-on.
             * `ptol -say`/`ptol -M` below are the real experiment surface
             * for now — same console_speak(), fully offline, no curses
             * wire involved. */
            mh_send_chat(h, fr.id, reply, sig, gam, primes, mode);
        } else if (strcmp(fr.t, "mode") == 0) {
            if (fr.mode[0]) {
                strncpy(mode, fr.mode, sizeof mode - 1);
                mode[sizeof mode - 1] = '\0';
            }
            char ack[64];
            snprintf(ack, sizeof ack, "(construction mode: %s)", mode);
            mh_send_chat(h, fr.id, ack, 0.5, 0.0, "", mode);
        } else if (strcmp(fr.t, "ping") == 0) {
            char pong[64];
            snprintf(pong, sizeof pong, "{\"t\":\"pong\",\"id\":%ld}", fr.id);
            mh_send_raw(h, pong);
        } else if (strcmp(fr.t, "attach") == 0) {
            mh_send_chat(h, fr.id, "(ptol resident monad attached)",
                         0.5, 0.0, "", mode);
        } else if (strcmp(fr.t, "quit") == 0) {
            break;
        }
    }

    cv_close();
    if (g_monad) monad_destroy(g_monad);
    mh_close(h);
    close(sv[0]);
    int st = 0;
    waitpid(pid, &st, 0);
    return WIFEXITED(st) ? WEXITSTATUS(st) : 1;
}
#endif /* PTOL_LIBRARY */

/* ── Main ────────────────────────────────────────────────────────────────── */
/*
 * Compile as CLI binary (default):
 *   gcc -O2 -o ptol ptol.c -lm
 *
 * Compile as shared library (importable by holcus_window.py / PtolemyDesktop):
 *   gcc -O2 -shared -fPIC -DPTOL_LIBRARY -o ptol_brain.so ptol.c -lm
 *
 * Python import:
 *   import ctypes
 *   brain = ctypes.CDLL("./ptol_brain.so")
 */

#ifndef PTOL_LIBRARY
int main(int argc, char *argv[])
{
    /* Locate our own directory so get_english_words() can find ptol_layer.py */
    {
        char self[512];
        ssize_t len = readlink("/proc/self/exe", self, sizeof(self)-1);
        if (len > 0) {
            self[len] = '\0';
            char *slash = strrchr(self, '/');
            if (slash) { *slash = '\0'; g_ptol_dir[0]='\0'; strncat(g_ptol_dir, self, sizeof(g_ptol_dir)-1); }
        }
    }

    { const char *pd = getenv("PTOLC_DIR"); if (pd && *pd) { g_ptol_dir[0] = '\0'; strncat(g_ptol_dir, pd, sizeof(g_ptol_dir) - 1); } }   /* PTOLC_DIR overrides where the .bin stores and english_corpus.txt are looked for */
    monad3_open();   /* mmap the combined language store if present */

    int    raw        = 0;
    int    do_svg     = 0;
    int    do_bmp     = 0;
    int    do_html    = 0;
    int    sigma_mode = 0;   /* -sigma <value>: Holcus speaks from scalar alone */
    double sigma_in   = 0.5; /* the scalar σ Holcus received */
    const PtolEye *active_eye = &TOWER_EYES[2]; /* default: H (σ=½) */
    const char *out_dir   = "";
    const char *img_input = NULL;
    int arg0 = 1;

    while (arg0 < argc && argv[arg0][0] == '-') {
        if (strcmp(argv[arg0], "-r") == 0) {
            raw = 1; arg0++;
        } else if (strcmp(argv[arg0], "-eye") == 0) {
            arg0++;
            if (arg0 < argc) { active_eye = eye_by_name(argv[arg0++]); }
        } else if (strcmp(argv[arg0], "-sigma") == 0) {
            /* Holcus receives σ as sole input — all other variables NULL */
            sigma_mode = 1; raw = 1; arg0++;
            if (arg0 < argc) { sigma_in = atof(argv[arg0++]); }
        } else if (strcmp(argv[arg0], "-s") == 0) {
            do_svg = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-b") == 0) {
            do_bmp = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-H") == 0) {
            do_svg = do_bmp = do_html = 1; arg0++;
            if (arg0 < argc && (argv[arg0][0]=='.' || argv[arg0][0]=='/' || argv[arg0][0]=='~')) out_dir = argv[arg0++];
        } else if (strcmp(argv[arg0], "-i") == 0) {
            arg0++;
            if (arg0 >= argc) { fprintf(stderr, "ptol: -i needs <image>\n"); return 1; }
            img_input = argv[arg0++];
        } else if (strcmp(argv[arg0], "-P") == 0) {
            /* the probe the Python test bench drives (tests/test_c_parity.py): one command per line on stdin */
            return cv_probe();
        } else if (strcmp(argv[arg0], "-chat") == 0) {
            /* talk to the child in the terminal: plain text in, plain text out, one resident session (state kept between lines).  Blank line or EOF ends. */
            char line[2048], reply[1024]; int tty = isatty(0);
            if (tty) printf("(I am a child learning English. Talk to me; /help lists the commands.)\n");
            for (;;) {
                if (tty) { printf("> "); fflush(stdout); }
                if (!fgets(line, sizeof line, stdin)) break;
                size_t L = strlen(line); while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) line[--L] = 0;
                if (!L) break;
                if (line[0] == '/') cv_command(line, reply, sizeof reply); else cv_turn(line, reply, sizeof reply);
                printf("%s\n", reply); fflush(stdout);
            }
            cv_close(); return 0;
        } else if (strcmp(argv[arg0], "-turn") == 0) {
            /* talk to the child from the shell: ptol -turn "<what you say>"  (state in PTOL_USAGE_DIR or ~/.ptolemy/usage_c) */
            arg0++;
            if (arg0 >= argc) { fprintf(stderr, "ptol: -turn needs <text>\n"); return 1; }
            char reply[1024]; if (argv[arg0][0] == '/') cv_command(argv[arg0], reply, sizeof reply); else cv_turn(argv[arg0], reply, sizeof reply);
            printf("%s\n", reply); cv_close(); return 0;
        } else if (strcmp(argv[arg0], "-M") == 0) {
            /* diagnostic: bsearch the combined store (monad3_c.bin) for a
             * word and print its cross-store tuple. Verifies the mmap
             * wiring end to end without touching get_monad_words yet. */
            arg0++;
            if (arg0 >= argc) { fprintf(stderr, "ptol: -M needs <word>\n"); return 1; }
            if (!g_m3h) { fprintf(stderr, "ptol -M: monad3_c.bin not found next to the binary\n"); return 1; }
            int32_t ix[3]; uint32_t deg;
            int hit = monad3_lookup(argv[arg0], ix, &deg);
            printf("store: %s/monad3_c.bin  (%u words, %u eng, %u wn, %u phon, %u edges)\n",
                   g_ptol_dir, g_m3h->n_words, g_m3h->n_eng, g_m3h->n_wn,
                   g_m3h->n_phon, g_m3h->nnz);
            if (!hit) { printf("  %s: not found\n", argv[arg0]); return 0; }
            printf("  %s: eng_idx=%d  wn_idx=%d  phon_idx=%d  cooccur_degree=%u\n",
                   argv[arg0], ix[0], ix[1], ix[2], deg);
            if (ix[1] >= 0) {
                const unsigned char *e = g_m3 + g_m3h->off_wn + (size_t)ix[1] * 82u;
                uint8_t pos = e[32];
                const int16_t *vec = (const int16_t *)(e + 40);   /* word[32] pos[1] pad[3] offset[4] vec[19] */
                printf("  wn: pos=%u  vec19=[", pos);
                for (int q = 0; q < 19; q++) printf("%d%s", vec[q], q < 18 ? "," : "");
                printf("]\n");
                double gr = monad3_gamma_radial(vec);
                if (isnan(gr))
                    printf("  gamma_radial: undefined (all-zero relation vector)\n");
                else
                    printf("  gamma_radial: %+.6f  (Gamma-Radial Windspeed, "
                           "ScalarContextPropagation §7.3/§9.1)\n", gr);
            }
            return 0;
        } else if (strcmp(argv[arg0], "-say") == 0) {
            /* diagnostic: one-shot console_speak() with no curses console,
             * no socketpair — the same word-bag-or-sentence voice `ptol -w`
             * uses, callable straight from a shell. Exists so the sentence
             * creator can be smoke-tested (or just talked to) fully
             * offline: everything past python3 + the already-downloaded
             * nltk_data/VerbNet corpora and monad_sentences.json is local. */
            arg0++;
            if (arg0 >= argc) { fprintf(stderr, "ptol: -say needs a prompt\n"); return 1; }
            char prompt[65536] = "";
            for (int i = arg0; i < argc; i++) {
                if (i > arg0) strncat(prompt, " ", sizeof(prompt) - strlen(prompt) - 1);
                strncat(prompt, argv[i], sizeof(prompt) - strlen(prompt) - 1);
            }
            char reply[1024], primes[128], gr_report[256];
            double sig, gam;
            console_speak(prompt, reply, &sig, &gam, primes, gr_report);
            printf("%s\n", reply);
            fprintf(stderr, "  [σ=%.4f Γ=%+.4f primes: %s]\n", sig, gam, primes);
            fprintf(stderr, "  [Gamma-Radial Windspeed per firing word: %s]\n",
                    gr_report[0] ? gr_report : "(none — no firing word has a "
                    "WordNet entry with a nonzero relation vector)");
            return 0;
        } else if (strcmp(argv[arg0], "-g") == 0 || strcmp(argv[arg0], "--gui") == 0) {
            /* Launch holcus_window.py — the brain exec's the face */
            char gui[512];
            snprintf(gui, sizeof(gui), "%s/../holcus_window.py", g_ptol_dir);
            /* Shift argv so python3 is argv[0], gui path is argv[1] */
            char *py_argv[64];
            py_argv[0] = (char *)"python3";
            py_argv[1] = gui;
            int na = 2;
            for (int i = arg0 + 1; i < argc && na < 63; i++)
                py_argv[na++] = argv[i];
            py_argv[na] = NULL;
            execv("/usr/bin/python3", py_argv);
            perror("ptol -g: exec holcus_window.py failed");
            return 127;
        } else if (strcmp(argv[arg0], "-w") == 0 || strcmp(argv[arg0], "--boxkite") == 0 ||
                   strcmp(argv[arg0], "--console") == 0) {
            /* Fork the PtolemyDesktop tabbed curses console onto the tty and
             * stay resident as the speaking monad behind monad_harness.c.
             * The console draws curses (Chat / ValaQuenta / Generational
             * Lineage / Archimedes — the last two greyed until built); this
             * process answers `say` frames with the sedenion-projection word
             * shadow (console_speak). `/paragraph` in the Chat Tab flips the
             * console to paragraph grammar (semantic_paragraph.py); the
             * default stays sentence construction. Replaces the old exec of
             * rotary_boxkite_window.py — kept in git history; a from-scratch
             * C port of the WordNet box-kite composter is still future work
             * (see PtolC/wntest.c for the verified wordnet-dev groundwork). */
            return run_console(argc, argv, arg0 + 1);
        } else {
            break;
        }
    }

    double v[16];

    if (img_input) {
        /* ── Image read mode ── */
        if (!read_image_scalars(img_input, v)) return 1;
        /* v[] already normalised-ish from pixel range; re-normalise */
        double norm2 = 0.0;
        for (int k = 0; k < 16; k++) norm2 += v[k]*v[k];
        double norm = sqrt(norm2);
        if (norm > 0.0) for (int k = 0; k < 16; k++) v[k] /= norm;

        printf("image: %s\n", img_input);
        printf("geometry (from image):\n");
        for (int k = 0; k < 16; k++)
            printf("  e%-2d  %+.8f\n", k, v[k]);

        int idx[16];
        for (int k = 0; k < 16; k++) idx[k] = k;
        /* Sort ascending |v| for spiral */
        for (int i = 0; i < 15; i++)
            for (int j = i+1; j < 16; j++)
                if (fabs(v[idx[i]]) > fabs(v[idx[j]])) {
                    int t = idx[i]; idx[i] = idx[j]; idx[j] = t;
                }

        printf("\nspiral (ZD → great circle):\n  ");
        for (int i = 0; i < 16; i++)
            printf("e%d(%+.3f)%s", idx[i], v[idx[i]], i < 15 ? " → " : "\n");

        return 0;
    }

    /* ── σ-mode: Holcus speaks from scalar alone — all other variables NULL ── */
    if (sigma_mode) {
        double v[16];
        /* Project the scalar σ through H_hat_RB — no text, no prompt */
        /* Encode σ as a 1-byte input: the single character at σ·255       */
        unsigned char s1[1];
        s1[0] = (unsigned char)(sigma_in * 255.0 + 0.5);
        double norm = 0.0, peak = 0.0;
        for (int k = 0; k < 16; k++) {
            _x[k] = project(s1, 1, k, sigma_in);
            norm  += _x[k] * _x[k];
            if (fabs(_x[k]) > peak) peak = fabs(_x[k]);
        }
        norm = sqrt(norm);
        for (int k = 0; k < 16; k++)
            v[k] = (norm > 0.0) ? _x[k] / norm : 0.0;

        double sigma_out = measure_sigma(v);
        double gamma_out, u_out;
        measure_gamma(v, &gamma_out, &u_out);

        /* Output: measured σ first, then x[16] — the sedenion pathway */
        printf("sigma_in:  %.10f\n", sigma_in);
        printf("sigma_out: %.10f\n", sigma_out);
        printf("delta:     %+.10f\n", sigma_out - 0.5);
        printf("gamma:     %+.10f\n", gamma_out);   /* the fold: 2σ−1 = tanh(u/2) */
        printf("u:         %+.10f\n", u_out);       /* ADD:SCALE:SIGN word length */
        printf("---\n");
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", v[k]);
        printf("---\n");
        for (int k = 0; k < 16; k++)
            if (fabs(_x[k]) >= peak / MONAD_PHI)
                printf("%d\n", P[k]);
        return 0;
    }

    /* ── Text prompt mode ── */
    char sigma[65536];
    sigma[0] = '\0';

    if (argc <= arg0) {
        /* No argument: try stdin if it's a pipe */
        if (isatty(STDIN_FILENO)) {
            fprintf(stderr,
                "usage: ptol [-r] [-s [dir]] [-b [dir]] [-H [dir]] [-i <img>] <prompt>\n");
            return 1;
        }
        size_t cap = sizeof(sigma) - 1;
        size_t len = 0;
        int c;
        while (len < cap && (c = getchar()) != EOF && c != '\n')
            sigma[len++] = (char)c;
        sigma[len] = '\0';
        /* strip trailing whitespace */
        while (len > 0 && (sigma[len-1] == ' ' || sigma[len-1] == '\r'))
            sigma[--len] = '\0';
        if (len == 0) {
            fprintf(stderr, "ptol: empty prompt\n");
            return 1;
        }
    } else {
        for (int i = arg0; i < argc; i++) {
            if (i > arg0) strncat(sigma, " ", sizeof(sigma) - strlen(sigma) - 1);
            strncat(sigma, argv[i], sizeof(sigma) - strlen(sigma) - 1);
        }
    }
    int n = (int)strlen(sigma);

    double norm = 0.0, peak = 0.0;
    for (int k = 0; k < 16; k++) {
        _x[k] = project((const unsigned char *)sigma, n, k, active_eye->sigma);
        norm  += _x[k] * _x[k];
        if (fabs(_x[k]) > peak) peak = fabs(_x[k]);
    }
    norm = sqrt(norm);

    for (int k = 0; k < 16; k++)
        v[k] = (norm > 0.0) ? _x[k] / norm : 0.0;

    /* Σ_RB = J_red × J_blue — the d* invariant.
     * Partners: Shell1↔Shell2 (k↔k+4), Shell3↔Shell4 (k↔k+4 within shell).
     * Product is conserved at all σ — energy converts form, never lost. */
    double s_rb[16];
    for (int k = 0; k < 16; k++) {
        int partner = (k < 4) ? k+4 : (k < 8) ? k-4 :
                      (k < 12) ? k+4 : k-4;
        s_rb[k] = v[k] * v[partner];
    }

    double thresh      = peak / MONAD_PHI;
    double thresh_norm = (norm > 0.0) ? thresh / norm : 0.0;

    int idx[16];
    for (int k = 0; k < 16; k++) idx[k] = k;
    qsort(idx, 16, sizeof(int), cmp_mag_asc);

    /* ── Monad layer (all non-raw modes) — math selects from full domain ── */
    char words[16][256];
    char layer_elem[64];
    memset(words, 0, sizeof(words));
    strncpy(layer_elem, "English", 63); layer_elem[63] = '\0';
    if (!raw)
        get_monad_words(v, _x, thresh, words, layer_elem);

    /* ── Papers dir (shared by default SVG and explicit flags) ── */
    static char ptolemy_papers[512];
    ptolemy_papers[0] = '\0';
    if (!out_dir || !*out_dir) {
        const char *home = getenv("HOME");
        if (home) {
            char ph[512];
            snprintf(ph, sizeof(ph), "%s/.ptolemy", home);
            mkdir(ph, 0755);
            snprintf(ptolemy_papers, sizeof(ptolemy_papers), "%s/.ptolemy/papers", home);
            mkdir(ptolemy_papers, 0755);
            out_dir = ptolemy_papers;
        }
    }

    char slug[64];
    make_slug(sigma, slug, sizeof(slug));
    long ts = (long)time(NULL);

    /* ── Default mode: SVG + English stdout ── */
    if (!raw && !do_svg && !do_bmp && !do_html) {
        char svg_path[1024];
        make_outpath(out_dir, slug, ts, "svg", svg_path, sizeof(svg_path));
        if (write_svg(svg_path, v, idx, thresh_norm, sigma, words, layer_elem))
            fprintf(stderr, "paper: %s\n", svg_path);

        /* English firing order (Riemann spiral) to stdout */
        for (int i = 0; i < 16; i++) {
            int k = idx[i];
            int active = (fabs(v[k]) >= thresh_norm);
            const char *w = words[k][0] ? words[k] : NULL;
            if (i > 0) printf(" ");
            if (active) printf("*");
            printf("%s", w ? w : "·");
        }
        printf("\n");
    }

    /* ── Raw mode ── */
    if (raw) {
        double sigma_self = measure_sigma(v);
        double sigma_comp = 1.0 - sigma_self;

        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", v[k]);
        printf("---\n");
        for (int k = 0; k < 16; k++)
            if (fabs(_x[k]) >= thresh)
                printf("%d\n", P[k]);
        printf("---\n");
        /* Σ_RB products — J_red × J_blue per channel pair */
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", s_rb[k]);

        /* Mind's Eye (R̂, updateable): project at σ_self */
        double ve[16];
        double norm_e = 0.0;
        for (int k = 0; k < 16; k++) {
            ve[k] = project((const unsigned char *)sigma, n, k, sigma_self);
            norm_e += ve[k] * ve[k];
        }
        norm_e = sqrt(norm_e);
        if (norm_e > 0.0) for (int k = 0; k < 16; k++) ve[k] /= norm_e;

        /* Paper's Hands (B̂ = R̂†, non-updateable): project at 1 − σ_self */
        double vb[16];
        double norm_b = 0.0;
        for (int k = 0; k < 16; k++) {
            vb[k] = project((const unsigned char *)sigma, n, k, sigma_comp);
            norm_b += vb[k] * vb[k];
        }
        norm_b = sqrt(norm_b);
        if (norm_b > 0.0) for (int k = 0; k < 16; k++) vb[k] /= norm_b;

        printf("---\neye: %.10f\n", sigma_self);
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", ve[k]);
        printf("---\nhands: %.10f\n", sigma_comp);
        for (int k = 0; k < 16; k++)
            printf("%+.10f\n", vb[k]);

        double gamma_self, u_self;
        measure_gamma(v, &gamma_self, &u_self);
        printf("---\ngamma: %+.10f\nu:     %+.10f\n", gamma_self, u_self);

        fprintf(stderr, "eye: %s  σ_in: %.4f  σ_self: %.10f  Γ: %+.10f  u: %+.10f  (Δ½: %+.10f)\n",
                active_eye->name, active_eye->sigma,
                sigma_self, gamma_self, u_self, sigma_self - 0.5);
    }

    /* ── Explicit paper output (-s / -b / -H) ── */
    if (do_svg || do_bmp || do_html) {
        char svg_path[1024], ppm_path[1024], html_path[1024];
        make_outpath(out_dir, slug, ts, "svg",  svg_path,  sizeof(svg_path));
        make_outpath(out_dir, slug, ts, "ppm",  ppm_path,  sizeof(ppm_path));
        make_outpath(out_dir, slug, ts, "html", html_path, sizeof(html_path));

        if (do_svg) {
            if (write_svg(svg_path, v, idx, thresh_norm, sigma, words, layer_elem))
                fprintf(stderr, "paper (pathway): %s\n", svg_path);
        }
        if (do_bmp) {
            if (write_ppm(ppm_path, v, thresh_norm))
                fprintf(stderr, "paper (field):   %s\n", ppm_path);
        }
        if (do_html) {
            if (write_html(html_path, svg_path, ppm_path,
                           v, idx, P, thresh_norm, sigma, words))
                fprintf(stderr, "paper (html):    %s\n", html_path);
        }
    }

    return 0;
}
#endif /* PTOL_LIBRARY */
