/*
 * PtolC/main.c — ptolemy command-line binary.
 *
 * Primary flags:
 *   -l <file|url|->   learn from file, URL (via curl), or stdin
 *   -h <prompt>       hear → speak
 *   -s                status  (or speak math if verbose >= 1)
 *   -q <word>         lookup a single word
 *   -V                version
 *
 * Verbosity modifier (stackable, combinable with primary flags):
 *   -v  / --verbose   level 1: show mathematics (β, J^μ, A edges)
 *   -lv / -hv / -sv   primary + level 1 verbose
 *   -vv               level 2: + ANSI colour (hear=cyan, speak=green, learn=yellow)
 *   -vvv              level 3: full pipeline — for -h shows learn+hear+speak
 *
 * Other flags:
 *   -c <path>         checkpoint path (overrides env/auto-search)
 *   -n                no-save: do not write checkpoint after -l
 *
 * Checkpoint search order:
 *   1. -c flag
 *   2. $PTOLEMY_CHECKPOINT env var
 *   3. ./monad_wordnet.bin
 *   4. ../Callimachus/data/monad_wordnet.bin
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>

#include "ptolemy.h"
#include "monad.h"
#include "checkpoint.h"

/* g_color and g_self_ref are defined in monad.c — set here by main() */

#define PTOLEMY_VERSION "1.0.0"

/* ── Arg parsing ──────────────────────────────────────────────────────────── */

typedef struct {
    char primary;   /* 'l','h','s','q','c','n','V', 0=none */
    int  v;         /* verbose count (number of 'v' chars) */
} Arg;

static Arg parse_arg(const char *a)
{
    Arg r = {0, 0};
    if (!a || a[0] != '-') return r;
    if (a[1] == '-') {
        if (strcmp(a+2, "verbose") == 0) r.v = 1;
        return r;
    }
    for (const char *p = a + 1; *p; p++) {
        switch (*p) {
            case 'v': r.v++; break;
            case 'l': case 'h': case 's': case 'q':
            case 'c': case 'n': case 'V': case 'i':
                r.primary = *p; break;
            default: break;
        }
    }
    return r;
}

/* ── I/O helpers ──────────────────────────────────────────────────────────── */

static char *read_file(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "[ptolemy] cannot open %s: %s\n", path, strerror(errno));
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    rewind(f);
    char *buf = malloc(sz + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t got = fread(buf, 1, sz, f);
    buf[got] = '\0';
    fclose(f);
    return buf;
}

static char *read_stdin(void)
{
    size_t cap = 65536, len = 0;
    char  *buf = malloc(cap);
    int    c;
    while ((c = fgetc(stdin)) != EOF) {
        if (len + 2 >= cap) { cap *= 2; buf = realloc(buf, cap); }
        buf[len++] = (char)c;
    }
    buf[len] = '\0';
    return buf;
}

static char *read_url(const char *url)
{
    for (const char *p = url; *p; p++) {
        if (*p == '\'') {
            fprintf(stderr, "[ptolemy] URL contains single quote — refused\n");
            return NULL;
        }
    }
    char cmd[4096];
    snprintf(cmd, sizeof(cmd), "curl -sf '%s'", url);
    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "[ptolemy] curl failed for %s\n", url);
        return NULL;
    }
    size_t cap = 131072, len = 0;
    char  *buf = malloc(cap);
    int    c;
    while ((c = fgetc(pipe)) != EOF) {
        if (len + 2 >= cap) { cap *= 2; buf = realloc(buf, cap); }
        buf[len++] = (char)c;
    }
    buf[len] = '\0';
    pclose(pipe);
    return buf;
}

static const char *find_checkpoint(const char *flag_path)
{
    static char found[4096];
    const char *env_path = getenv("PTOLEMY_CHECKPOINT");
    const char *cands[4] = {
        flag_path,
        env_path,
        "monad_wordnet.bin",
        "../Callimachus/data/monad_wordnet.bin",
    };
    for (int i = 0; i < 4; i++) {
        if (!cands[i] || !cands[i][0]) continue;
        FILE *t = fopen(cands[i], "rb");
        if (t) {
            fclose(t);
            strncpy(found, cands[i], sizeof(found) - 1);
            found[sizeof(found) - 1] = '\0';
            return found;
        }
    }
    return NULL;
}

static void print_version(void)
{
    printf("ptolemy %s — H_hat_RB Field Engine\n", PTOLEMY_VERSION);
    printf("  Riemann zeros   N=%d\n", MONAD_N_DEFAULT);
    printf("  σ = ½           Noether forcing: J(σ,E)=0 iff σ=½\n");
    printf("  β_sat = %.3f    L_ground = %.3f\n", MONAD_BETA_SAT, MONAD_L_GROUND);
    printf("  φ = %.16f\n", MONAD_PHI);
    printf("  D* = %.5f       Ω_ζΣ = %.5f\n", MONAD_D_STAR, MONAD_OMEGA_ZS);
    printf("  Self-referential: -vvv pipes verbose → learn()\n");
    printf("  Identity:         --identity / -i  (run once after corpus)\n");
    printf("  CLAUDE-SMMNIP-00729-56714-24600\n");
}

static void print_usage(void)
{
    fprintf(stderr,
        "ptolemy %s — H_hat_RB Field Engine\n\n"
        "  -l <file|url|->  learn from file, URL, or stdin\n"
        "  -h <prompt>      hear → Noether response\n"
        "  -s               status  (or spontaneous speak if verbose)\n"
        "  -q <word>        lookup: zero, σ, E, β\n"
        "  -i / --identity  learn Ptolemy's identity text (run once)\n"
        "  -V               version\n\n"
        "Verbosity (stackable, combinable):\n"
        "  -v / --verbose   level 1: β deepening, J^μ propagation, A edges\n"
        "  -vv              level 2: level 1 + ANSI colour\n"
        "  -vvv             level 3: full pipeline + self-referential loop\n"
        "                   (verbose output is fed back through learn())\n"
        "  -lv  -hv  -sv    combined primary + verbose\n\n"
        "Other:\n"
        "  -c <path>        checkpoint path\n"
        "  -n               no-save after -l\n\n"
        "Checkpoint: -c → $PTOLEMY_CHECKPOINT → ./monad_wordnet.bin"
        " → ../Callimachus/data/monad_wordnet.bin\n",
        PTOLEMY_VERSION);
}

/* ── Main ─────────────────────────────────────────────────────────────────── */

int main(int argc, char *argv[])
{
    if (argc < 2) { print_usage(); return 1; }

    /* ── Pre-scan: verbose level, checkpoint path, no-save ─────────────── */
    int         verbose   = 0;
    const char *ckpt_flag = NULL;
    int         no_save   = 0;

    for (int i = 1; i < argc; i++) {
        if (!argv[i] || argv[i][0] != '-') continue;
        if (strcmp(argv[i], "--verbose") == 0) {
            if (verbose < 1) verbose = 1;
            continue;
        }
        Arg a = parse_arg(argv[i]);
        if (a.v > verbose) verbose = a.v;
        if (a.primary == 'c' && i + 1 < argc) ckpt_flag = argv[++i];
        if (a.primary == 'n') no_save = 1;
    }

    /* ── Colour and self-referential mode ──────────────────────────────── */
    g_color    = (verbose >= 2) && isatty(fileno(stderr)) && isatty(fileno(stdout));
    g_self_ref = (verbose >= 3);

    /* ── Load monad ─────────────────────────────────────────────────────── */
    const char *ckpt_path = find_checkpoint(ckpt_flag);
    Monad *m = monad_create(MONAD_N_DEFAULT);
    monad_ground_init(m);

    if (ckpt_path) {
        checkpoint_load(m, ckpt_path);
    } else {
        fprintf(stderr,
            "[ptolemy] no checkpoint found — ground state  σ=0\n"
            "          run: python3 Callimachus/wordnet_init.py\n"
            "          then: python3 Callimachus/checkpoint_export.py\n");
    }

    /* ── Process arguments in order ─────────────────────────────────────── */
    int learned = 0;

    for (int i = 1; i < argc; i++) {
        if (!argv[i] || argv[i][0] != '-') continue;
        if (strcmp(argv[i], "--verbose") == 0) continue;

        Arg a = parse_arg(argv[i]);

        /* -V : version */
        if (a.primary == 'V') {
            print_version();
            continue;
        }

        /* -c / -n : handled in pre-scan */
        if (a.primary == 'c') { i++; continue; }
        if (a.primary == 'n') continue;

        /* -i / --identity : learn Ptolemy's identity ────────────────── */
        if (a.primary == 'i' ||
            (argv[i][0]=='-' && argv[i][1]=='-' && strcmp(argv[i]+2,"identity")==0)) {
            monad_learn_identity(m);
            monad_self_flush(m);
            learned = 1;
            continue;
        }

        /* -l : learn ─────────────────────────────────────────────────── */
        if (a.primary == 'l' && i + 1 < argc) {
            const char *src  = argv[++i];
            char       *text = NULL;

            if (strcmp(src, "-") == 0) {
                text = read_stdin();
            } else if (strncmp(src, "http://",  7) == 0 ||
                       strncmp(src, "https://", 8) == 0) {
                fprintf(stderr, "[ptolemy] fetching %s ...\n", src);
                text = read_url(src);
            } else {
                text = read_file(src);
            }

            if (text) {
                int lv = (verbose >= 1) ? verbose : a.v;
                fprintf(stderr, "[ptolemy] learning %s  (%zu bytes)\n",
                        src, strlen(text));
                monad_learn(m, text, lv);
                monad_self_flush(m);
                free(text);
                learned = 1;
                if (lv == 0) monad_status(m, stderr);
            }
            continue;
        }

        /* -h : hear → speak ──────────────────────────────────────────── */
        if (a.primary == 'h' && i + 1 < argc) {
            const char *query = argv[++i];
            int hv = (verbose >= 1) ? verbose : a.v;

            if (hv == 0) {
                char  qcopy[4096];
                char *tok;
                strncpy(qcopy, query, sizeof(qcopy) - 1);
                tok = strtok(qcopy, " \t\r\n");
                while (tok) {
                    monad_lookup(m, tok, stderr);
                    tok = strtok(NULL, " \t\r\n");
                }
            }

            char *response = monad_speak(m, query, 50, hv);
            printf("%s\n", response);
            free(response);
            monad_self_flush(m);
            if (g_self_ref) learned = 1;  /* save after self-ref cycle */
            continue;
        }

        /* -s : status / verbose speak ────────────────────────────────── */
        if (a.primary == 's') {
            int sv = (verbose >= 1) ? verbose : a.v;
            if (sv >= 1) {
                char *response = monad_speak(m, "", 50, sv);
                printf("%s\n", response);
                free(response);
                monad_self_flush(m);
                if (g_self_ref) learned = 1;
            }
            monad_status(m, stdout);
            continue;
        }

        /* -q : word lookup ───────────────────────────────────────────── */
        if (a.primary == 'q' && i + 1 < argc) {
            monad_lookup(m, argv[++i], stdout);
            continue;
        }

        /* Bare -v / -vv / -vvv with no primary: spontaneous speak */
        if (a.primary == 0 && a.v > 0) {
            int bv = a.v > verbose ? a.v : verbose;
            char *response = monad_speak(m, "", 50, bv);
            printf("%s\n", response);
            free(response);
            monad_self_flush(m);
            if (g_self_ref) learned = 1;
            continue;
        }

        if (a.primary != 0)
            fprintf(stderr, "[ptolemy] flag -%c: missing argument\n", a.primary);
    }

    /* ── Save if learned ─────────────────────────────────────────────────── */
    if (learned && !no_save) {
        const char *save = ckpt_path ? ckpt_path : "monad_wordnet.bin";
        checkpoint_save(m, save, 0.0);
    }

    monad_destroy(m);
    return 0;
}
