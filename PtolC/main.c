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
#include <pwd.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "ptolemy.h"
#include "monad.h"
#include "state.h"
#include "ingest.h"
#include "daemon.h"
#include "log.h"
#include "zork.h"

/* g_color and g_self_ref are defined in monad.c — set here by main() */

/* ── fermat_clean — strip Fermat spaces for stdout ───────────────────────── *
 * Replaces all Fermat space sequences (E2 80 {8A..83}) with plain ' '.
 * Returns malloc'd string.  Caller frees.  Original kept for Wernicke loop.  */
static char *fermat_clean(const char *s)
{
    size_t len = strlen(s);
    char *out  = malloc(len + 1);
    size_t r = 0, w = 0;
    const unsigned char *p = (const unsigned char *)s;
    static const unsigned char thirds[] = {
        0x8A, 0x89, 0x88, 0x87, 0x86, 0x85, 0x84, 0x83
    };
    while (r < len) {
        if (p[r] == 0xE2 && r + 2 < len && p[r+1] == 0x80) {
            int is_fermat = 0;
            for (int k = 0; k < 8; k++)
                if (p[r+2] == thirds[k]) { is_fermat = 1; break; }
            if (is_fermat) {
                out[w++] = ' ';
                r += 3;
                continue;
            }
        }
        out[w++] = (char)p[r++];
    }
    out[w] = '\0';
    return out;
}

#define PTOLEMY_VERSION "2.2.0"

/* ── Checkpoint evaluator ─────────────────────────────────────────────────── */

static void run_eval(const char *ckpt_path)
{
    /* Locate eval_checkpoint.py: SMMIP_REPO env → default path → skip */
    char script[4096] = {0};
    const char *smmip = getenv("SMMIP_REPO");
    if (smmip && smmip[0]) {
        snprintf(script, sizeof(script), "%s/tools/eval_checkpoint.py", smmip);
    } else {
        const char *home = getenv("HOME");
        if (home && home[0])
            snprintf(script, sizeof(script),
                     "%s/Projects/Ptol/SMMIP/tools/eval_checkpoint.py", home);
    }
    if (!script[0]) return;

    FILE *t = fopen(script, "r");
    if (!t) return;
    fclose(t);

    /* Write JSON assessment alongside checkpoint */
    char json_out[4096];
    snprintf(json_out, sizeof(json_out), "%s.assessment.json", ckpt_path);

    char cmd[8192];
    snprintf(cmd, sizeof(cmd),
             "python3 '%s' '%s' --out '%s'", script, ckpt_path, json_out);

    fprintf(stderr, "\n[eval] running checkpoint assessment...\n");
    int rc = system(cmd);
    if (rc == 0)
        fprintf(stderr, "[eval] assessment written → %s\n", json_out);
    else if (rc > 0)
        fprintf(stderr, "[eval] verdict: WARN/FAIL (exit %d) — see %s\n", rc, json_out);
}

/* ── Ptolemy home directory ───────────────────────────────────────────────── */

static char g_ptolemy_dir[4096] = {0};

static void init_ptolemy_dir(void)
{
    const char *override = getenv("PTOLEMY_HOME");
    if (override && override[0]) {
        snprintf(g_ptolemy_dir, sizeof(g_ptolemy_dir), "%s", override);
        return;
    }
    const char *home = getenv("HOME");
    if (!home || !home[0]) {
        struct passwd *pw = getpwuid(getuid());
        if (pw && pw->pw_dir) home = pw->pw_dir;
    }
    if (home && home[0])
        snprintf(g_ptolemy_dir, sizeof(g_ptolemy_dir), "%s/.ptolemy", home);
    else
        snprintf(g_ptolemy_dir, sizeof(g_ptolemy_dir), ".ptolemy");

    /* create ~/.ptolemy/ if it does not exist */
    mkdir(g_ptolemy_dir, 0700);
}

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
            case 'l': case 'L': case 'h': case 's': case 'w':
            case 'c': case 'n': case 'V': case 'i': case 'r':
            case 'I': case 'q': case 'd': case 'D': case 'C':
            case 'F': case 'S': case 'W': case 'e': case 'O': case 'J':
                r.primary = *p; break;
            default: break;
        }
    }
    return r;
}

/* ── English re-anchor ────────────────────────────────────────────────────── *
 * After every filesystem ingest, re-learn the English grammar corpus.
 * This re-applies the gauge constraint: function words and connective
 * structure are re-anchored so domain-specific A-edges don't crowd out
 * the English backbone.
 *
 * Search order:
 *   1. {PTOLEMY_HOME}/english_grammar.txt   (deployed / installed)
 *   2. ./corpora/english_grammar.txt        (running from source tree)
 *   3. /proc/self/exe/../corpora/...        (binary-relative)             */
static void reanchor_english(Monad *m, int verbose)
{
    char paths[3][4096];
    snprintf(paths[0], sizeof(paths[0]), "%s/english_grammar.txt", g_ptolemy_dir);
    snprintf(paths[1], sizeof(paths[1]), "corpora/english_grammar.txt");

    /* binary-relative path via /proc/self/exe */
    paths[2][0] = '\0';
    char exebuf[4096];
    ssize_t exelen = readlink("/proc/self/exe", exebuf, sizeof(exebuf) - 1);
    if (exelen > 0) {
        exebuf[exelen] = '\0';
        char *slash = strrchr(exebuf, '/');
        if (slash) {
            *slash = '\0';
            snprintf(paths[2], sizeof(paths[2]),
                     "%s/corpora/english_grammar.txt", exebuf);
        }
    }

    for (int k = 0; k < 3; k++) {
        if (!paths[k][0]) continue;
        if (access(paths[k], R_OK) != 0) continue;
        char *text = NULL;
        FILE *f = fopen(paths[k], "rb");
        if (f) {
            fseek(f, 0, SEEK_END); long sz = ftell(f); rewind(f);
            text = malloc(sz + 1);
            if (text) { size_t got = fread(text, 1, sz, f); text[got] = '\0'; }
            fclose(f);
        }
        if (!text) continue;
        fprintf(stderr, "[ptolemy] re-anchor English grammar (%zu bytes)\n",
                strlen(text));
        monad_learn(m, text, verbose);
        free(text);
        return;
    }
    fprintf(stderr, "[ptolemy] warning: english_grammar.txt not found — "
            "run 'make grammar' to install\n");
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
    static char home_monad[4096];
    static char home_ckpt[4096];

    if (g_ptolemy_dir[0]) {
        snprintf(home_monad, sizeof(home_monad),
                 "%s/monad.bin", g_ptolemy_dir);
        snprintf(home_ckpt, sizeof(home_ckpt),
                 "%s/monad_wordnet.bin", g_ptolemy_dir);
    }

    const char *env_path = getenv("PTOLEMY_CHECKPOINT");
    const char *cands[]  = {
        flag_path,
        env_path,
        home_monad[0] ? home_monad : NULL,   /* active education state */
        home_ckpt[0]  ? home_ckpt  : NULL,   /* fallback: wordnet state */
        "monad_wordnet.bin",
        NULL
    };
    for (int i = 0; i < (int)(sizeof(cands)/sizeof(cands[0])) - 1; i++) {
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
    printf("ptolemy %s — RedBlue Geometries Engine\n", PTOLEMY_VERSION);
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
        "ptolemy %s — RedBlue Geometries Engine\n\n"
        "  -l <file|url|->  learn from file, URL, or stdin\n"
        "  -I <path>        ingest directory or file (Native Space whitelist)\n"
        "  -h <prompt>      hear → Noether response  (real J: β×E²)\n"
        "  -W <prompt>      hear → Wick-rotated response  (imaginary J: β×E²×sin(E/2))\n"
        "  -D <query>       send query to running daemon\n"
        "  -d               start daemon (keeps monad resident in memory)\n"
        "  -s               status  (or spontaneous speak if verbose)\n"
        "  -F               field health report\n"
        "  -w <word>        lookup: zero, σ, E, β, home/gen stratum\n"
        "  -i / --identity  learn Ptolemy's identity text (run once)\n"
        "  -r               interactive REPL: hear → speak → hear loop\n"
        "  -V               version\n\n"
        "Verbosity (stackable, combinable):\n"
        "  -v / --verbose   level 1: β deepening, J^μ propagation, A edges\n"
        "  -vv              level 2: level 1 + ANSI colour\n"
        "  -vvv             level 3: full pipeline + self-referential loop\n"
        "                   (verbose output is fed back through learn())\n"
        "  -lv  -hv  -sv    combined primary + verbose\n\n"
        "Other:\n"
        "  -c <path>        checkpoint path\n"
        "  -S <path>        socket path for daemon (default: ~/.ptolemy/ptolemy.sock)\n"
        "  -n               no-save after -l\n"
        "  -q / --quiet     suppress terminal output\n\n"
        "Checkpoint: -c → $PTOLEMY_CHECKPOINT → ~/.ptolemy/monad_wordnet.bin"
        " → ./monad_wordnet.bin\n",
        PTOLEMY_VERSION);
}

/* ── /generate — spawn Python image generator ────────────────────────────── */

static void do_generate(Monad *m, const char *prompt,
                        const char *ckpt, int verbose)
{
    (void)m; (void)verbose;

    /* Locate generate_image.py.
     * Search order:
     *   1. {bindir}/tools/generate_image.py      (installed beside binary)
     *   2. {bindir}/../tools/generate_image.py   (running from PtolC/ subdir)
     *   3. tools/generate_image.py               (CWD fallback)              */
    char script[4096] = {0};
    char exebuf[4096] = {0};
    ssize_t exelen = readlink("/proc/self/exe", exebuf, sizeof(exebuf) - 1);
    if (exelen > 0) {
        exebuf[exelen] = '\0';
        char *slash = strrchr(exebuf, '/');
        if (slash) {
            *slash = '\0';
            /* 1. bindir/tools/ */
            char candidate[4096];
            snprintf(candidate, sizeof(candidate),
                     "%s/tools/generate_image.py", exebuf);
            if (access(candidate, R_OK) == 0) {
                strncpy(script, candidate, sizeof(script) - 1);
            } else {
                /* 2. bindir/../tools/ */
                snprintf(candidate, sizeof(candidate),
                         "%s/../tools/generate_image.py", exebuf);
                if (access(candidate, R_OK) == 0)
                    strncpy(script, candidate, sizeof(script) - 1);
            }
        }
    }
    if (!script[0])
        strncpy(script, "tools/generate_image.py", sizeof(script) - 1);

    /* Check the script exists */
    if (access(script, R_OK) != 0) {
        fprintf(stderr,
            "[generate] tools/generate_image.py not found\n"
            "           searched beside binary and in parent tools/\n");
        return;
    }

    /* Build command — sanitise prompt by stripping single-quotes */
    char safe_prompt[1024] = {0};
    int si = 0;
    for (const char *p = prompt; *p && si < 1023; p++)
        if (*p != '\'') safe_prompt[si++] = *p;
    safe_prompt[si] = '\0';

    char bin_arg[4096] = {0};
    if (ckpt && ckpt[0])
        snprintf(bin_arg, sizeof(bin_arg), " --bin '%s'", ckpt);

    char cmd[8192];
    snprintf(cmd, sizeof(cmd),
             "python3 '%s'%s '%s'",
             script, bin_arg, safe_prompt);

    fprintf(stderr, "[generate] rendering field portrait…\n");
    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "[generate] popen failed: %s\n", strerror(errno));
        return;
    }
    char path[4096] = {0};
    if (fgets(path, sizeof(path), pipe)) {
        size_t plen = strlen(path);
        while (plen > 0 && (path[plen-1] == '\n' || path[plen-1] == '\r'))
            path[--plen] = '\0';
    }
    int rc = pclose(pipe);
    if (rc == 0 && path[0]) {
        printf("[generate] → %s\n", path);
        fflush(stdout);
        /* Try to open with system image viewer (best-effort) */
        char view_cmd[4096];
        snprintf(view_cmd, sizeof(view_cmd),
                 "xdg-open '%s' 2>/dev/null &", path);
        system(view_cmd);
    } else {
        fprintf(stderr, "[generate] failed (exit %d)\n", rc);
    }
}

/* ── Main ─────────────────────────────────────────────────────────────────── */

int main(int argc, char *argv[])
{
    if (argc < 2) { print_usage(); return 1; }

    init_ptolemy_dir();

    /* ── Pre-scan: verbose level, checkpoint path, no-save, quiet ───────── */
    int         verbose    = 0;
    const char *ckpt_flag  = NULL;
    const char *sock_flag  = NULL;
    int         no_save    = 0;
    int         quiet      = 0;

    for (int i = 1; i < argc; i++) {
        if (!argv[i] || argv[i][0] != '-') continue;
        if (strcmp(argv[i], "--verbose") == 0) {
            if (verbose < 1) verbose = 1;
            continue;
        }
        if (strcmp(argv[i], "--quiet") == 0) { quiet = 1; continue; }
        Arg a = parse_arg(argv[i]);
        if (a.v > verbose) verbose = a.v;
        if (a.primary == 'c' && i + 1 < argc) ckpt_flag = argv[++i];
        if (a.primary == 'C' && i + 1 < argc) ckpt_flag = argv[++i]; /* -C: alt config/checkpoint */
        if (a.primary == 'S' && i + 1 < argc) sock_flag  = argv[++i];
        if (a.primary == 'n') no_save = 1;
        if (a.primary == 'q') quiet = 1;
    }

    /* ── Colour and self-referential mode ──────────────────────────────── */
    g_color    = (verbose >= 2) && isatty(fileno(stderr)) && isatty(fileno(stdout));
    g_self_ref = (verbose >= 3);

    /* ── Logging ────────────────────────────────────────────────────────── */
    plog_init(g_ptolemy_dir, quiet);

    /* ── Load monad ─────────────────────────────────────────────────────── */
    const char *ckpt_path = find_checkpoint(ckpt_flag);
    Monad *m = monad_create(MONAD_N_DEFAULT);
    monad_ground_init(m);

    if (ckpt_path) {
        state_load(m, ckpt_path);
    } else {
        if (!quiet)
            fprintf(stderr,
                "[ptolemy] no checkpoint found — ground state  σ=0\n"
                "          place monad_wordnet.bin in ~/.ptolemy/\n");
    }

    /* ── Process arguments in order ─────────────────────────────────────── */
    int learned = 0;
    int did_ingest = 0;

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

        /* -l : learn  /  -L : learn as WordNet (canonical English) ───── */
        if ((a.primary == 'l' || a.primary == 'L') && i + 1 < argc) {
            const char *src  = argv[++i];
            char       *text = NULL;

            if (strcmp(src, "-") == 0) {
                text = read_stdin();
            } else if (strncmp(src, "http://",  7) == 0 ||
                       strncmp(src, "https://", 8) == 0) {
                fprintf(stderr, "[ptolemy] fetching %s ...\n", src);
                text = read_url(src);
            } else {
                if (access(src, R_OK) == 0) {
                    text = read_file(src);
                } else {
                    /* not a readable file — treat argument as literal text */
                    text = strdup(src);
                }
            }

            if (text) {
                int lv = (verbose >= 1) ? verbose : a.v;
                NSFiletype lft = (a.primary == 'L') ? NS_FT_WORDNET : NS_FT_PROSE;
                fprintf(stderr, "[ptolemy] learning (%zu bytes)%s\n",
                        strlen(text),
                        lft == NS_FT_WORDNET ? " [wordnet]" : "");
                monad_learn_ex(m, text, lv, lft);
                monad_self_flush(m);
                free(text);
                learned = 1;
                if (lv == 0) monad_status(m, stderr);
            }
            continue;
        }

        /* -I : filesystem ingest (Native Space whitelist) ───────────────── */
        if (a.primary == 'I' && i + 1 < argc) {
            const char *root = argv[++i];
            int iv = (verbose >= 1) ? verbose : a.v;
            const char *save_to = ckpt_path ? ckpt_path
                                : (g_ptolemy_dir[0] ? g_ptolemy_dir : NULL);
            /* Build the save path string if we have a dir but no ckpt_flag */
            static char ingest_ckpt[4096];
            if (!ckpt_path && g_ptolemy_dir[0]) {
                snprintf(ingest_ckpt, sizeof(ingest_ckpt),
                         "%s/monad.bin", g_ptolemy_dir);  /* active_state, not checkpoint */
                save_to = ingest_ckpt;
            }
            int n = ingest_path(m, root, iv, save_to);
            if (n > 0) {
                learned = 1; did_ingest = 1;
                reanchor_english(m, 0);   /* re-apply gauge constraint */
                monad_status(m, stderr);
            }
            continue;
        }

        /* -d : start daemon ──────────────────────────────────────────── */
        if (a.primary == 'd') {
            static char d_save[4096], d_pid[4096];
            const char *sp = daemon_sock_path(sock_flag, g_ptolemy_dir);
            const char *save_ckpt = NULL;
            const char *pid_p     = NULL;
            if (!no_save) {
                if (ckpt_path) {
                    save_ckpt = ckpt_path;
                } else if (g_ptolemy_dir[0]) {
                    snprintf(d_save, sizeof(d_save),
                             "%s/monad_wordnet.bin", g_ptolemy_dir);
                    save_ckpt = d_save;
                } else {
                    save_ckpt = "monad_wordnet.bin";
                }
            }
            if (g_ptolemy_dir[0]) {
                snprintf(d_pid, sizeof(d_pid),
                         "%s/ptolemy.pid", g_ptolemy_dir);
                pid_p = d_pid;
            }
            daemon_serve(m, sp, save_ckpt, pid_p, verbose);
            monad_destroy(m);
            plog_close();
            return 0;
        }

        /* -D : query daemon ──────────────────────────────────────────── */
        if (a.primary == 'D' && i + 1 < argc) {
            const char *query = argv[++i];
            const char *sp    = daemon_sock_path(sock_flag, g_ptolemy_dir);
            int rc = daemon_query(query, sp);
            monad_destroy(m);
            plog_close();
            return rc == 0 ? 0 : 1;
        }

        /* -F : field health ──────────────────────────────────────────── */
        if (a.primary == 'F') {
            monad_health(m, stdout);
            continue;
        }

        /* -S : socket path (handled in pre-scan, skip here) ─────────── */
        if (a.primary == 'S') { i++; continue; }

        /* -e : set affect (e7 octonion field) ────────────────────────── *
         * Usage: -e neutral | -e irritated | -e angry | -e passive | -e <float>
         * Sets the system's emotional state absolutely (not relative).   */
        if (a.primary == 'e' && i + 1 < argc) {
            const char *level = argv[++i];
            float af;
            if      (strcmp(level, "angry")     == 0) af =  1.0f;
            else if (strcmp(level, "irritated") == 0) af =  0.7f;
            else if (strcmp(level, "tense")     == 0) af =  0.3f;
            else if (strcmp(level, "neutral")   == 0) af =  0.0f;
            else if (strcmp(level, "calm")      == 0) af = -0.3f;
            else if (strcmp(level, "passive")   == 0) af = -0.7f;
            else af = (float)atof(level);
            if (af >  1.0f) af =  1.0f;
            if (af < -1.0f) af = -1.0f;
            m->affect = af;
            if (!quiet)
                fprintf(stderr, "[affect e7]  %.2f  (%s)\n", af, level);
            continue;
        }

        /* -W : hear → Wick-rotated speak (π/2 phase rotation) ─────────── */
        if (a.primary == 'W' && i + 1 < argc) {
            const char *query = argv[++i];
            int wv = (verbose >= 1) ? verbose : a.v;
            char *response = monad_speak_wick(m, query, 50, wv);
            char *clean    = fermat_clean(response);
            printf("%s\n", clean); free(clean);
            monad_hear_fermat(m, response, wv);
            free(response);
            learned = 1;
            continue;
        }

        /* -O : hear → octonion speak (8-face, 4-cycle 2-stroke) ────────── */
        if (a.primary == 'O' && i + 1 < argc) {
            const char *query = argv[++i];
            int ov = (verbose >= 1) ? verbose : a.v;
            char *response = monad_speak_oct(m, query, 50, ov);
            char *clean    = fermat_clean(response);
            printf("%s\n", clean); free(clean);
            monad_hear_fermat(m, response, ov);
            free(response);
            learned = 1;
            continue;
        }

        /* -J : hear → J-direct speak (raw charge field, no face routing) ── */
        if (a.primary == 'J' && i + 1 < argc) {
            const char *query = argv[++i];
            int jv = (verbose >= 1) ? verbose : a.v;
            char *response = monad_speak_charge(m, query, 20, jv);
            char *clean    = fermat_clean(response);
            printf("%s\n", clean); free(clean);
            monad_hear_fermat(m, response, jv);
            free(response);
            learned = 1;
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

            float af_before = m->affect;
            char *response = monad_speak(m, query, 50, hv);
            char *clean    = fermat_clean(response);
            printf("%s\n", clean); free(clean);
            monad_hear_fermat(m, response, hv);
            free(response);
            monad_self_flush(m);
            learned = 1;
            if (m->affect != af_before) learned = 1;
            continue;
        }

        /* -r : interactive REPL — Zork-parsed hear → speak → hear_fermat loop.
         * Input is parsed by zork_parse() first:
         *   /generate <prompt>  → render field portrait image
         *   /status             → monad_status()
         *   /health             → monad_health()
         *   /vocab <word>       → monad_lookup()
         *   /help               → show commands
         *   /reset              → reset Zork pronoun context
         *   Known verb sentence → verb→operator→prompt → monad_speak()
         *   Plain text          → monad_speak() directly (pass-through)
         * Ctrl-D or blank line exits. */
        if (a.primary == 'r') {
            char linebuf[4096];
            int  repl_v = (verbose >= 1) ? verbose : 0;
            zork_reset_context();
            if (!quiet) {
                fprintf(stderr, "[ptolemy] interactive  (blank line or Ctrl-D to quit)\n");
                fprintf(stderr, "          Zork sentence parser active — verb-governed input\n");
                fprintf(stderr, "          /generate <prompt>  /status  /health  /vocab <w>  /help\n");
                if (ckpt_path)
                    fprintf(stderr, "          loaded: %s\n", ckpt_path);
                if (!no_save)
                    fprintf(stderr, "          session will save on exit  (use -n to suppress)\n");
                fprintf(stderr, "\n");
            }
            for (;;) {
                printf(">>> ");
                fflush(stdout);
                if (!fgets(linebuf, sizeof(linebuf), stdin)) break;
                size_t llen = strlen(linebuf);
                while (llen > 0 && (linebuf[llen-1] == '\n' || linebuf[llen-1] == '\r'))
                    linebuf[--llen] = '\0';
                if (!linebuf[0]) break;

                /* ── Zork parse ──────────────────────────────────────────── */
                ZorkResult zp = zork_parse(linebuf);

                /* ── Slash commands ──────────────────────────────────────── */
                if (zp.is_slash) {
                    if (strcmp(zp.slash_cmd, "generate") == 0) {
                        do_generate(m, zp.slash_args, ckpt_path, repl_v);
                    } else if (strcmp(zp.slash_cmd, "status") == 0 ||
                               strcmp(zp.slash_cmd, "s") == 0) {
                        monad_status(m, stdout);
                    } else if (strcmp(zp.slash_cmd, "health") == 0 ||
                               strcmp(zp.slash_cmd, "F") == 0) {
                        monad_health(m, stdout);
                    } else if ((strcmp(zp.slash_cmd, "vocab") == 0 ||
                                strcmp(zp.slash_cmd, "w") == 0) &&
                               zp.slash_args[0]) {
                        monad_lookup(m, zp.slash_args, stdout);
                    } else if (strcmp(zp.slash_cmd, "reset") == 0) {
                        zork_reset_context();
                        fprintf(stderr, "[zork] pronoun context reset\n");
                    } else if (strcmp(zp.slash_cmd, "help") == 0 ||
                               strcmp(zp.slash_cmd, "?") == 0) {
                        printf(
                            "Slash commands:\n"
                            "  /generate <prompt>  render field portrait image\n"
                            "  /status             field status\n"
                            "  /health             field health report\n"
                            "  /vocab <word>       look up a word's zero address\n"
                            "  /reset              reset pronoun context\n"
                            "  /help               this message\n"
                            "\nVerb-governed input (Zork sentence parser):\n"
                            "  take lamp           → e5 abstract lamp\n"
                            "  put lamp in box     → e2 bind lamp in box\n"
                            "  go north  /  n      → e6 branch north\n"
                            "  ask about primes    → e10 query primes\n"
                            "  make new field      → e9 allocate new field\n"
                            "  examine it          → e0 identity <last noun>\n"
                            "\nPlain text passes through to monad directly.\n"
                        );
                        fflush(stdout);
                    } else {
                        fprintf(stderr,
                            "[repl] unknown command: /%s  (try /help)\n",
                            zp.slash_cmd);
                    }
                    continue;
                }

                /* ── Zork-parsed input or plain pass-through ─────────────── */
                const char *query;
                if (zp.ok && zp.prompt[0]) {
                    if (repl_v == 0)
                        fprintf(stderr,
                            "[zork] e%d/%s  \"%s\"\n",
                            zp.op, zp.op_name, zp.prompt);
                    query = zp.prompt;
                } else {
                    if (!zp.ok && zp.error[0])
                        fprintf(stderr, "[zork] %s\n", zp.error);
                    query = linebuf;
                }

                float af_before = m->affect;
                char *response  = monad_speak(m, query, 50, repl_v);
                printf("%s\n", response);
                fflush(stdout);

                /* Wernicke loop: response exhaust compresses next hear() */
                monad_hear_fermat(m, response, repl_v);
                free(response);
                monad_self_flush(m);
                if (g_self_ref)            learned = 1;
                if (m->affect != af_before) learned = 1;
            }
            if (!quiet) fprintf(stderr, "\n[ptolemy] session ended\n");
            continue;
        }

        /* -s : status / verbose speak ────────────────────────────────── */
        if (a.primary == 's') {
            int sv = (verbose >= 1) ? verbose : a.v;
            if (sv >= 1) {
                char *response = monad_speak(m, "", 50, sv);
                char *clean    = fermat_clean(response);
                printf("%s\n", clean); free(clean);
                monad_hear_fermat(m, response, sv);
                free(response);
                monad_self_flush(m);
                learned = 1;
            }
            monad_status(m, stdout);
            continue;
        }

        /* -w : word lookup ───────────────────────────────────────────── */
        if (a.primary == 'w' && i + 1 < argc) {
            monad_lookup(m, argv[++i], stdout);
            continue;
        }

        /* -q : quiet (handled in pre-scan, skip here) ────────────────── */
        if (a.primary == 'q') continue;

        /* Bare -v / -vv / -vvv with no primary: spontaneous speak */
        if (a.primary == 0 && a.v > 0) {
            int bv = a.v > verbose ? a.v : verbose;
            char *response = monad_speak(m, "", 50, bv);
            char *clean    = fermat_clean(response);
            printf("%s\n", clean); free(clean);
            monad_hear_fermat(m, response, bv);
            free(response);
            monad_self_flush(m);
            learned = 1;
            continue;
        }

        if (a.primary != 0)
            fprintf(stderr, "[ptolemy] flag -%c: missing argument\n", a.primary);
    }

    /* ── Save if learned ─────────────────────────────────────────────────── */
    if (learned && !no_save) {
        static char default_save[4096];
        const char *save;
        if (ckpt_path) {
            save = ckpt_path;
        } else if (g_ptolemy_dir[0]) {
            snprintf(default_save, sizeof(default_save),
                     "%s/monad_wordnet.bin", g_ptolemy_dir);
            save = default_save;
        } else {
            save = "monad_wordnet.bin";
        }
        /* Refuse to overwrite monad_wordnet.bin in non-ingest sessions.
         * Use -l to ingest or -c <other.bin> to save a separate checkpoint. */
        const char *base = strrchr(save, '/');
        if (!base) base = save; else base++;
        if (strcmp(base, "monad_wordnet.bin") == 0 && !did_ingest) {
            if (!quiet)
                fprintf(stderr, "[ptolemy] protected: %s — use -l to ingest"
                                " or -c <path> for a session checkpoint\n", save);
        } else {
            state_save(m, save, 0.0);
            if (did_ingest && !quiet)
                run_eval(save);
        }
    }

    monad_destroy(m);
    plog_close();
    return 0;
}
