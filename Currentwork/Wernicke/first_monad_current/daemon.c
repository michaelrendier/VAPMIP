/*
 * PtolC/daemon.c — Ptolemy daemon mode.
 *
 * The monad is loaded once and kept resident (165 MB is negligible).
 * Connections are handled sequentially — the monad is not thread-safe
 * and does not need to be; query latency is sub-millisecond.
 *
 * Systemd socket activation: if $LISTEN_FDS >= 1 the kernel has already
 * bound the socket and passed it as fd 3.  We skip bind()/listen() and
 * use fd 3 directly.  No libsystemd dependency.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <time.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include "ptolemy.h"
#include "monad.h"
#include "monad3c.h"
#include "state.h"
#include "log.h"
#include "daemon.h"
#include "search.h"
#include "sensor.h"
#include "code.h"

/* ── Signal handling ──────────────────────────────────────────────────────── */

static volatile int g_quit = 0;

static void handle_sig(int sig)
{
    (void)sig;
    g_quit = 1;
}

/* ── monad3_c.bin ownership — the writer pen sidecar ──────────────────────
 *
 * harness.py takes flock(LOCK_EX) on ~/.ptolemy/monad3_c.writer while a
 * Monad is attached, and writes "<owner>:<pid>" to the ".owner" sidecar:
 * owner "daemon" (the harness / this daemon) or "ptolemy" (a bare Monad or
 * the ptol binary self-persisting an exact copy). The daemon checks that
 * sidecar before ANY write to the combined store — if a LIVE "ptolemy:<pid>"
 * holds the pen, the daemon stands down and lets that process persist;
 * "daemon:*", a stale pid, or no sidecar → the daemon writes.
 */
static char g_owner_sidecar[600] = "";
static char g_observe_fifo[600]  = "";   /* named pipe: fire-and-forget ingest */
static char g_observe_spool[600] = "";   /* local fallback when the pipe is gone */

/* ── input-size repack timer — a leaky integrator with a natural knee ─────
 *
 * Not a wall-clock interval. Every ingested prose line CHARGES an
 * accumulator by its byte length; idle time BLEEDS it with time constant
 * REPACK_TAU. Under a steady input rate r the accumulator follows the RC
 * charge curve toward the asymptote r·TAU — fast (near-exponential) at
 * first, then bending into saturation. The repack FIRES at the knee of
 * that curve, one time constant in: accum ≥ K·(1 − 1/e). K itself scales
 * with the store being repacked (a proxy: the resident checkpoint's size),
 * so a bigger store tolerates more drift before a fold pays for itself.
 *
 * A burst of turns compounds and trips the knee quickly; the same bytes
 * dribbled over hours bleed away and never do — the fold happens when the
 * field has absorbed a coherent batch, not on a timer. REPACK_MAX_AGE is a
 * hard guarantee floor so a barely-used session still folds in eventually;
 * SIGTERM always folds on the way out.
 */
#define REPACK_KNEE      0.6321205588285577   /* 1 − 1/e  — one time constant  */
#define REPACK_RATIO     0.05                 /* K as a fraction of store size */
#define REPACK_K_MIN     (64UL   * 1024)      /* 64 KiB  — floor for tiny bins */
#define REPACK_K_MAX     (8UL    * 1024 * 1024)
#define REPACK_TAU_DEF   1800.0               /* s — bleed time constant       */
#define REPACK_MAX_AGE   21600                /* s — 6 h hard fallback         */

static double  g_accum        = 0.0;   /* charge (bytes-ish), bled over time  */
static time_t  g_accum_ts     = 0;     /* last time g_accum was updated       */
static time_t  g_last_repack  = 0;
static size_t  g_repack_K     = REPACK_K_MIN;
static double  g_repack_tau   = REPACK_TAU_DEF;
static int     g_had_input    = 0;     /* something charged since last fold   */
static char    g_ckpt_path[600] = ""; /* what the daemon can persist today    */
static char    g_repack_cmd[512] = ""; /* full-rebuild command (new vocab)    */
static char    g_monad3c_path[600] = ""; /* the packed store ptol.c reads     */
static long    g_monad3c_pending  = 0;   /* live words the packed table lacks */

/* enough never-before-seen words to make a full CSR rebuild worth it */
#define MONAD3C_REBUILD_AT 2000

static int monad3c_write_permitted(void);   /* defined just below */

static void repack_charge(size_t n)
{
    time_t now = time(NULL);
    if (g_accum_ts && now > g_accum_ts)          /* bleed the gap first */
        g_accum *= exp(-difftime(now, g_accum_ts) / g_repack_tau);
    g_accum   += (double)n;
    g_accum_ts = now;
    g_had_input = 1;
}

static void spawn_detached(const char *cmd)
{
    pid_t p = fork();
    if (p == 0) {
        setsid();
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        _exit(127);
    }
    /* parent: SIGCHLD is SIG_IGN (set in daemon_serve) so no zombie */
}

/* ── prompt -> response scale pairs — substrate for a scaling engine ─────
 *
 * A prompt (external) and the response it drew (internal) carry the same
 * pair_id. When both halves have been seen the daemon has a sample:
 * (prompt_bytes -> response_bytes). It keeps a small ring of pending
 * external halves, matches the internal half against it, appends the
 * completed sample to ~/.ptolemy/pairs.jsonl (append-only, offline-fit),
 * and keeps a running ratio for STATUS. The scaling engine itself is a
 * separate, offline thing that reads pairs.jsonl — this is just the tap.
 */
#define PAIR_RING 64

struct pair_slot { char id[64]; size_t ext; time_t t; };
static struct pair_slot g_pair_ring[PAIR_RING];
static int    g_pair_head    = 0;
static long   g_pair_n       = 0;      /* completed samples */
static double g_pair_ratio_s = 0.0;    /* sum of resp/prompt ratios */
static size_t g_pair_last_e  = 0, g_pair_last_i = 0;
static char   g_pairs_path[600] = "";

static void pair_record(const char *cls, const char *id, size_t nbytes)
{
    if (strcmp(cls, "external") == 0) {          /* stash the prompt half */
        struct pair_slot *slot = &g_pair_ring[g_pair_head];
        snprintf(slot->id, sizeof(slot->id), "%s", id);
        slot->ext = nbytes;
        slot->t   = time(NULL);
        g_pair_head = (g_pair_head + 1) % PAIR_RING;
        return;
    }
    if (strcmp(cls, "internal") != 0) return;

    for (int k = 0; k < PAIR_RING; k++) {        /* match the response half */
        if (g_pair_ring[k].id[0] && strcmp(g_pair_ring[k].id, id) == 0) {
            size_t e = g_pair_ring[k].ext, i = nbytes;
            g_pair_ring[k].id[0] = '\0';
            g_pair_n++;
            if (e > 0) g_pair_ratio_s += (double)i / (double)e;
            g_pair_last_e = e; g_pair_last_i = i;
            if (g_pairs_path[0]) {
                FILE *pf = fopen(g_pairs_path, "a");
                if (pf) {
                    fprintf(pf,
                        "{\"t\":%lld,\"id\":\"%s\",\"prompt_bytes\":%zu,"
                        "\"response_bytes\":%zu,\"ratio\":%.4f}\n",
                        (long long)time(NULL), id, e, i,
                        e ? (double)i / (double)e : 0.0);
                    fclose(pf);
                }
            }
            plog(PLOG_INFO, "daemon pair %s: %zu -> %zu B (ratio %.2f)",
                 id, e, i, e ? (double)i / (double)e : 0.0);
            return;
        }
    }
}

/* ── the in-place fold — no serializer, just a range check + pwrite ──────
 *
 * The packed monad3_c.bin ptol.c reads is a fixed-offset mmap: β f64[nE],
 * age/fire i32[nE], and an A-matrix CSR (rowptr/col/w). Every word the live
 * daemon knows that ALSO has a row in that table is "in range": its current
 * β, age and every already-present edge weight are written straight into
 * the mapping (MAP_SHARED + msync). No parse, no rebuild, no Python. Values
 * are already clamped to [0,1] by monad_learn, so nothing can overflow.
 *
 * "Out of range" = a live word the packed table has never seen (new vocab)
 * or a brand-new edge — those need the CSR grown, which only the full
 * rebuild (g_repack_cmd) can do. They are counted; when enough pile up the
 * rebuild is spawned and the counter clears.
 */
static long monad3c_fold_inplace(Monad *m)
{
    if (!g_monad3c_path[0]) return -1;
    int fd = open(g_monad3c_path, O_RDWR);
    if (fd < 0) return -1;
    struct stat st;
    if (fstat(fd, &st) != 0 || (size_t)st.st_size < sizeof(Monad3cHeader)) {
        close(fd); return -1;
    }
    unsigned char *map = mmap(NULL, (size_t)st.st_size,
                              PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (map == MAP_FAILED) return -1;
    if (memcmp(map, MONAD3C_MAGIC, 8) != 0) {
        munmap(map, (size_t)st.st_size); return -1;
    }

    const Monad3cHeader *h   = (const Monad3cHeader *)map;
    const char    *blob      = (const char *)(map + h->off_wordblob);
    const WordRec *recs       = (const WordRec *)(map + h->off_wordrec);
    double        *beta       = (double *)(map + h->off_beta);
    int32_t       *age        = (int32_t *)(map + h->off_age);
    int32_t       *fire       = (int32_t *)(map + h->off_fire);
    const uint32_t*rowptr     = (const uint32_t *)(map + h->off_rowptr);
    const uint32_t*col        = (const uint32_t *)(map + h->off_col);
    float         *wv         = (float *)(map + h->off_w);

    uint32_t *eng2row = calloc(h->n_eng, sizeof(uint32_t));
    int      *eng2zi  = malloc((size_t)h->n_eng * sizeof(int));
    if (!eng2row || !eng2zi) {
        free(eng2row); free(eng2zi);
        munmap(map, (size_t)st.st_size); return -1;
    }
    for (uint32_t r = 0; r < h->n_words; r++) {
        int32_t ei = recs[r].eng_idx;
        if (ei >= 0 && (uint32_t)ei < h->n_eng) eng2row[ei] = r;
    }

    long folded = 0;
    for (uint32_t ei = 0; ei < h->n_eng; ei++) {   /* β / age / fire */
        const char *word = blob + recs[eng2row[ei]].name_off;
        int zi; double E;
        if (!monad_wm_get(m, word, &zi, &E)) { eng2zi[ei] = -1; continue; }
        eng2zi[ei] = zi;
        double lb = m->beta[zi];
        if (beta[ei] != lb) { beta[ei] = lb; folded++; }
        age[ei]  = m->age[zi];
        fire[ei] += 1;
    }
    for (uint32_t ei = 0; ei < h->n_eng; ei++) {   /* existing edges */
        int zi = eng2zi[ei];
        if (zi < 0) continue;
        for (uint32_t p = rowptr[ei]; p < rowptr[ei + 1]; p++) {
            if (col[p] >= h->n_eng) continue;
            int zj = eng2zi[col[p]];
            if (zj < 0) continue;
            double lw = monad_a_get(m, zi, zj);
            if (lw <= 0.0) continue;
            float f = (float)(lw > 1.0 ? 1.0 : lw);
            if (wv[p] != f) { wv[p] = f; folded++; }
        }
    }

    long oor = (long)m->wm_size - (long)h->n_eng;   /* live words the table lacks */
    g_monad3c_pending = oor > 0 ? oor : 0;

    free(eng2row); free(eng2zi);
    msync(map, (size_t)st.st_size, MS_ASYNC);
    munmap(map, (size_t)st.st_size);
    return folded;
}

static void maybe_repack(Monad *m, time_t now)
{
    if (!g_had_input) {
        if (now - g_last_repack >= REPACK_MAX_AGE) g_last_repack = now;
        return;
    }
    if (g_accum_ts && now > g_accum_ts) {        /* bleed since last touch */
        g_accum   *= exp(-difftime(now, g_accum_ts) / g_repack_tau);
        g_accum_ts = now;
    }
    int knee = g_accum >= (double)g_repack_K * REPACK_KNEE;
    int aged = (now - g_last_repack) >= REPACK_MAX_AGE;
    if (!knee && !aged) return;

    if (!monad3c_write_permitted()) {
        plog(PLOG_INFO, "daemon: repack due (accum=%.0f K=%zu %s) — a bare "
             "Monad holds the pen, deferring", g_accum, g_repack_K,
             knee ? "knee" : "max-age");
        return;    /* try again next idle sweep */
    }
    plog(PLOG_INFO, "daemon: repack firing — accum=%.0f / K=%zu (%s)",
         g_accum, g_repack_K, knee ? "asymptote knee" : "max-age fallback");

    long folded = monad3c_fold_inplace(m);       /* the range check + pwrite */
    if (folded >= 0)
        plog(PLOG_INFO, "daemon: in-place fold — %ld values written, "
             "%ld new words pending a full rebuild", folded, g_monad3c_pending);
    else if (g_ckpt_path[0])
        state_save(m, g_ckpt_path, 0.0);          /* no packed store → checkpoint */

    if (g_monad3c_pending >= MONAD3C_REBUILD_AT && g_repack_cmd[0]) {
        plog(PLOG_INFO, "daemon: %ld new words — spawning full CSR rebuild",
             g_monad3c_pending);
        spawn_detached(g_repack_cmd);
        g_monad3c_pending = 0;
    }
    g_accum      = 0.0;                           /* the reset */
    g_had_input  = 0;
    g_last_repack = now;
}

static int monad3c_write_permitted(void)
{
    if (!g_owner_sidecar[0]) return 1;              /* not wired → permit */
    FILE *f = fopen(g_owner_sidecar, "r");
    if (!f) return 1;                               /* nobody claims the pen */
    char owner[64] = {0};
    int  pid = 0;
    int  got = fscanf(f, "%63[^:]:%d", owner, &pid);
    fclose(f);
    if (got != 2) return 1;
    if (strcmp(owner, "ptolemy") != 0) return 1;    /* harness/daemon holds it */
    if (pid > 0 && kill(pid, 0) != 0) return 1;     /* stale — holder is gone */
    return 0;                                       /* a live bare Monad owns it */
}

/* ── conversational ingest — the concurrent FIFO drain ───────────────────
 *
 * The two Claude Code hooks (UserPromptSubmit, Stop) sanitise their turn to
 * prose and fire it at g_observe_fifo, then return — no wait. Because the
 * gaps between a prompt landing, the model thinking, and the reply arriving
 * are all very different lengths, ingestion must not sit on any of them:
 * the daemon poll()s the pipe alongside the query socket and drains it in
 * slices between accept()s. If the pipe is gone (its drive unmounted) the
 * hook appends to g_observe_spool on local storage instead; the daemon
 * drains that on startup and whenever it is idle.
 *
 * Wire framing matches the socket OBSERVE verb:
 *     <class> [pair_id]\n   external | internal | document, optional pair id
 *     <prose line>\n        ... learned at the class weight
 *     .\n                   end of turn — fires pair_record for a pair id
 * The parse state (weight, class, pair id, byte count) is carried in an
 * ObsState across poll wakes and spool lines. Weight is a single scalar
 * here (β and edges together); harness.INGEST_POLICY's orthogonal
 * (w_sem, w_ctx) vector needs a two-weight learn in monad.c and is applied
 * on the Python in-process path meanwhile.
 */
typedef struct { float w; char cls[16]; char pair[64]; size_t bytes; } ObsState;

static void observe_ingest_line(Monad *m, char *ln, ObsState *st)
{
    if (strcmp(ln, ".") == 0) {                     /* end of turn */
        if (st->pair[0] && (strcmp(st->cls, "external") == 0 ||
                            strcmp(st->cls, "internal") == 0))
            pair_record(st->cls, st->pair, st->bytes);
        st->w = 0.0f; st->cls[0] = '\0'; st->pair[0] = '\0'; st->bytes = 0;
        return;
    }
    /* a class header line: "<class>" or "<class> <pair_id>" */
    char c[16] = {0}, p[64] = {0};
    int got = sscanf(ln, "%15s %63s", c, p);
    if (got >= 1) {
        float w = 0.0f;
        if      (strcmp(c, "external") == 0) w = 1.5f;
        else if (strcmp(c, "internal") == 0) w = 0.9f;
        else if (strcmp(c, "document") == 0) w = 1.0f;
        if (w > 0.0f) {
            st->w = w; st->bytes = 0;
            snprintf(st->cls, sizeof(st->cls), "%s", c);
            snprintf(st->pair, sizeof(st->pair), "%s", got >= 2 ? p : "");
            return;
        }
    }
    if (st->w > 0.0f && ln[0]) {                    /* a prose line */
        size_t k = strlen(ln);
        monad_learn(m, ln, st->w);
        repack_charge(k);
        st->bytes += k;
    }
}

static void drain_spool(Monad *m)
{
    if (!g_observe_spool[0]) return;
    FILE *f = fopen(g_observe_spool, "r");
    if (!f) return;
    char ln[4096];
    ObsState st = {0};
    long n = 0;
    while (fgets(ln, sizeof(ln), f)) {
        size_t k = strlen(ln);
        while (k > 0 && (ln[k-1] == '\n' || ln[k-1] == '\r')) ln[--k] = '\0';
        observe_ingest_line(m, ln, &st);
        n++;
    }
    fclose(f);
    if (n > 0) {
        FILE *t = fopen(g_observe_spool, "w");   /* truncate what we consumed */
        if (t) fclose(t);
        plog(PLOG_INFO, "daemon: drained %ld spooled ingest lines", n);
    }
}

/* ── Socket path resolution ───────────────────────────────────────────────── */

const char *daemon_sock_path(const char *flag_path, const char *ptolemy_dir)
{
    static char resolved[4096];

    if (flag_path && flag_path[0]) {
        snprintf(resolved, sizeof(resolved), "%s", flag_path);
        return resolved;
    }
    const char *env = getenv("PTOLEMY_SOCKET");
    if (env && env[0]) {
        snprintf(resolved, sizeof(resolved), "%s", env);
        return resolved;
    }
    if (ptolemy_dir && ptolemy_dir[0])
        snprintf(resolved, sizeof(resolved), "%s/ptolemy.sock", ptolemy_dir);
    else
        snprintf(resolved, sizeof(resolved), ".ptolemy.sock");
    return resolved;
}

/* ── PID file ─────────────────────────────────────────────────────────────── */

static void pid_write(const char *pid_path)
{
    FILE *f = fopen(pid_path, "w");
    if (!f) return;
    fprintf(f, "%d\n", (int)getpid());
    fclose(f);
}

static void pid_remove(const char *pid_path)
{
    if (pid_path) unlink(pid_path);
}

/* ── Client handler ───────────────────────────────────────────────────────── */

static void handle_client(Monad *m, int fd, int verbose)
{
    /* Wrap fd in FILE* for line-oriented I/O */
    FILE *in  = fdopen(dup(fd), "r");
    FILE *out = fdopen(dup(fd), "w");
    if (!in || !out) {
        if (in)  fclose(in);
        if (out) fclose(out);
        return;
    }

    char line[4096];
    while (fgets(line, sizeof(line), in)) {
        /* strip trailing \r\n */
        size_t l = strlen(line);
        while (l > 0 && (line[l-1] == '\n' || line[l-1] == '\r'))
            line[--l] = '\0';

        if (strncmp(line, "HEAR ", 5) == 0) {
            const char *query = line + 5;
            plog(PLOG_INFO, "daemon HEAR: %s", query);
            char *resp = monad_speak(m, query, 50, verbose);
            fprintf(out, "%s\n.\n", resp);
            fflush(out);
            free(resp);
            if (monad3c_write_permitted())
                monad_self_flush(m);
            else
                plog(PLOG_INFO, "daemon: monad3_c.bin held by a bare Monad "
                                "— skipping self-flush");

        } else if (strncmp(line, "OBSERVE ", 8) == 0) {
            /* OBSERVE <class> [pair_id]\n  <prose line>\n ... \n .\n
             *
             * Passive ingest — the daemon as observer on the live
             * conversation and on committed documentation. <class>:
             *   external  a user prompt (the human, full weight)
             *   internal  the assistant's final prose (down-weighted)
             *   document  committed wiki / README / paper prose off a
             *             git post-commit hook (neutral weight)
             * See harness.INGEST_POLICY. Reads prose lines until a lone
             * '.', learns each into the field. The monad3_c.bin ownership
             * check gates the FLUSH, not this in-RAM update.
             *
             * [pair_id], present on external/internal only, links a prompt
             * to the response it drew — the daemon records the
             * (prompt_bytes -> response_bytes) sample for a downstream
             * response-scaling engine (see pair_record / ~/.ptolemy/pairs.jsonl).
             *
             * MATHEMATICAL SANITIZATION: the sender (harness.strip_to_prose)
             * has already dropped notation-dense lines. The WORDS for the
             * maths are expected to arrive as prose from the calculator —
             * the derivation engine's narration, ~/.clauderc_canonical_maths
             * (as 'document'), the unit-management vocabulary — not from raw
             * glyphs. The daemon just learns what it is given.
             *
             * NOTE: monad_learn() applies one weight to both the beta-field
             * and the co-occurrence edges. The orthogonal (w_sem, w_ctx)
             * split needs a two-weight learn in monad.c; until then w_sem
             * stands in for both. The Python in-process path does the full
             * split. */
            char cls[32] = {0}, pair_id[64] = {0};
            sscanf(line + 8, "%31s %63s", cls, pair_id);
            float w_sem = 0.0f;
            if      (strcmp(cls, "external") == 0) w_sem = 1.5f;
            else if (strcmp(cls, "internal") == 0) w_sem = 0.9f;
            else if (strcmp(cls, "document") == 0) w_sem = 1.0f;
            if (w_sem == 0.0f) {
                fprintf(out, "ERR OBSERVE class must be external|internal|document\n.\n");
                fflush(out);
                continue;
            }
            size_t total = 0;
            int lines = 0;
            char pl[4096];
            while (fgets(pl, sizeof(pl), in)) {
                size_t pn = strlen(pl);
                while (pn > 0 && (pl[pn-1] == '\n' || pl[pn-1] == '\r'))
                    pl[--pn] = '\0';
                if (strcmp(pl, ".") == 0) break;
                if (pn == 0) continue;
                monad_learn(m, pl, w_sem);
                repack_charge(pn);   /* charge the input-size repack timer */
                total += pn;
                lines++;
            }
            plog(PLOG_INFO, "daemon OBSERVE %s%s%s: %d lines, %zu chars",
                 cls, pair_id[0] ? " " : "", pair_id, lines, total);
            if (pair_id[0] && strcmp(cls, "document") != 0)
                pair_record(cls, pair_id, total);
            fprintf(out, "OK %zu\n.\n", total);
            fflush(out);
            maybe_repack(m, time(NULL));   /* a big turn can trip the knee now */

        } else if (strcmp(line, "STATUS") == 0) {
            monad_status(m, out);
            {   /* repack timer — where we are on the charge curve */
                time_t now = time(NULL);
                double a = g_accum;
                if (g_accum_ts && now > g_accum_ts)
                    a *= exp(-difftime(now, g_accum_ts) / g_repack_tau);
                double urg = g_repack_K ? 1.0 - exp(-a / (double)g_repack_K) : 0.0;
                fprintf(out,
                    "repack: accum=%.0f K=%zu urgency=%.3f knee=%.3f "
                    "since=%llds tau=%.0fs pending=%ld\n",
                    a, g_repack_K, urg, REPACK_KNEE,
                    (long long)(now - g_last_repack), g_repack_tau,
                    g_monad3c_pending);
                fprintf(out,
                    "pairs: n=%ld mean_ratio=%.3f last=%zu->%zu\n",
                    g_pair_n, g_pair_n ? g_pair_ratio_s / (double)g_pair_n : 0.0,
                    g_pair_last_e, g_pair_last_i);
            }
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "HEALTH") == 0) {
            monad_health(m, out);
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "QUIT") == 0) {
            fprintf(out, "OK\n.\n");
            fflush(out);
            break;

        } else if (strncmp(line, "SEARCH ", 7) == 0) {
            /* SEARCH <query>  — context search: arXiv + Wikipedia */
            const char *query = line + 7;
            plog(PLOG_INFO, "daemon SEARCH: %s", query);
            PtolSearchResult results[PTOL_SEARCH_MAX];
            double zeros[8];
            int nz = 0;
            int n = ptol_search_context(query, results, PTOL_SEARCH_MAX,
                                        zeros, &nz);
            for (int i = 0; i < n; i++) {
                fprintf(out, "[%s] %s\n%s\n",
                        results[i].source == PTOL_SEARCH_ARXIV ? "arxiv" : "wiki",
                        results[i].title, results[i].summary);
                /* Feed title+summary into field */
                char combined[1024];
                snprintf(combined, sizeof(combined), "%s %s",
                         results[i].title, results[i].summary);
                monad_learn(m, combined, 1.0f);
            }
            if (nz > 0) {
                fprintf(out, "[lmfdb] zeros:");
                for (int i = 0; i < nz; i++)
                    fprintf(out, " %.4f", zeros[i]);
                fprintf(out, "\n");
            }
            fprintf(out, ".\n");
            fflush(out);

        } else if (strcmp(line, "SENSOR_READ") == 0) {
            /* SENSOR_READ  — read 8 sensor channels from live_state.json */
            plog(PLOG_INFO, "daemon SENSOR_READ");
            float ch[8];
            sensor_read(ch, NULL);
            sensor_print(ch, out);
            /* Feed dominant channel name into field */
            int top = 0;
            for (int i = 1; i < 8; i++)
                if (ch[i] > ch[top]) top = i;
            static const char *CH_NAMES[8] = {
                "identity","negate","bind","name",
                "apply","abstract","branch","iterate"};
            monad_learn(m, CH_NAMES[top], 0);
            fprintf(out, ".\n");
            fflush(out);

        } else if (strncmp(line, "CODE_READ ", 10) == 0) {
            /* CODE_READ <path>  — profile a source file */
            const char *path = line + 10;
            plog(PLOG_INFO, "daemon CODE_READ: %s", path);
            CodeProfile prof;
            if (code_read_file(path, &prof)) {
                code_profile_print(&prof, out);
                /* Feed file into field via monad_learn on first 256 chars */
                FILE *src = fopen(path, "r");
                if (src) {
                    char snippet[256];
                    size_t got = fread(snippet, 1, 255, src);
                    fclose(src);
                    snippet[got] = '\0';
                    monad_learn(m, snippet, 1.0f);
                }
            } else {
                fprintf(out, "ERR cannot read %s\n", path);
            }
            fprintf(out, ".\n");
            fflush(out);

        } else if (l > 0) {
            fprintf(out, "ERR unknown command\n.\n");
            fflush(out);
        }
    }

    fclose(in);
    fclose(out);
}

/* ── Server ───────────────────────────────────────────────────────────────── */

int daemon_serve(Monad *m, const char *sock_path, const char *ckpt_path,
                 const char *pid_path, int verbose)
{
    int server_fd = -1;

    /* Check for systemd socket activation ($LISTEN_FDS set by systemd) */
    const char *listen_fds_str = getenv("LISTEN_FDS");
    if (listen_fds_str && atoi(listen_fds_str) >= 1) {
        server_fd = 3;   /* SD_LISTEN_FDS_START */
        plog(PLOG_INFO, "daemon using systemd-activated socket (fd %d)", server_fd);
    } else {
        /* Create and bind our own socket */
        server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_fd < 0) {
            plog(PLOG_ERROR, "daemon socket(): %s", strerror(errno));
            return -1;
        }

        struct sockaddr_un addr;
        memset(&addr, 0, sizeof(addr));
        addr.sun_family = AF_UNIX;
        strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

        unlink(sock_path);   /* remove stale socket if present */

        if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
            plog(PLOG_ERROR, "daemon bind(%s): %s", sock_path, strerror(errno));
            close(server_fd);
            return -1;
        }
        chmod(sock_path, 0600);

        if (listen(server_fd, 16) < 0) {
            plog(PLOG_ERROR, "daemon listen(): %s", strerror(errno));
            close(server_fd);
            return -1;
        }
        plog(PLOG_INFO, "daemon listening on %s", sock_path);
    }

    /* PID file */
    if (pid_path) pid_write(pid_path);

    /* Resolve the monad3_c.bin ownership sidecar: alongside the checkpoint
     * if we have one, else ~/.ptolemy/. Used by monad3c_write_permitted()
     * before every write to the combined store. */
    {
        char dir[512] = "";
        if (ckpt_path && ckpt_path[0]) {
            snprintf(dir, sizeof(dir), "%s", ckpt_path);
            char *slash = strrchr(dir, '/');
            if (slash) *slash = '\0';
            else dir[0] = '\0';
        }
        if (!dir[0]) {
            const char *home = getenv("HOME");
            snprintf(dir, sizeof(dir), "%s/.ptolemy", home ? home : ".");
        }
        snprintf(g_owner_sidecar, sizeof(g_owner_sidecar),
                 "%s/monad3_c.writer.owner", dir);
        plog(PLOG_INFO, "daemon: monad3_c ownership sidecar = %s", g_owner_sidecar);

        /* prompt->response scale samples — append-only, next to the store */
        snprintf(g_pairs_path, sizeof(g_pairs_path), "%s/pairs.jsonl", dir);

        /* the packed store ptol.c reads — folded in place at the knee.
         * $PTOL_MONAD3C wins (the canonical file lives next to the ptol
         * binary in PtolC/, not in ~/.ptolemy); else look beside the
         * checkpoint. Absent → the fold is skipped and the daemon falls
         * back to state_save. */
        {
            const char *m3 = getenv("PTOL_MONAD3C");
            if (m3 && m3[0])
                snprintf(g_monad3c_path, sizeof(g_monad3c_path), "%s", m3);
            else
                snprintf(g_monad3c_path, sizeof(g_monad3c_path),
                         "%s/monad3_c.bin", dir);
        }
        plog(PLOG_INFO, "daemon: in-place fold target = %s", g_monad3c_path);

        /* The conversational-ingest pipe lives next to the SOCKET, NOT next
         * to the (possibly external-drive) checkpoint — the spool must stay
         * reachable when the store's drive is unmounted. sock_path is bounded
         * by sun_path (<108 bytes), so sdir[128] is provably ample. */
        {
            char sdir[128];
            const char *home = getenv("HOME");
            if (sock_path && sock_path[0])
                snprintf(sdir, sizeof(sdir), "%s", sock_path);
            else
                snprintf(sdir, sizeof(sdir), "%s/.ptolemy/x", home ? home : ".");
            char *s2 = strrchr(sdir, '/');
            if (s2) *s2 = '\0'; else snprintf(sdir, sizeof(sdir), ".");
            snprintf(g_observe_fifo,  sizeof(g_observe_fifo),  "%s/monad.observe.fifo", sdir);
            snprintf(g_observe_spool, sizeof(g_observe_spool), "%s/observe.spool", sdir);
        }
        plog(PLOG_INFO, "daemon: observe pipe = %s", g_observe_fifo);
    }

    /* ── input-size repack timer setup ──────────────────────────────────
     * K scales with the store the fold rewrites — proxy: the checkpoint's
     * current size. TAU and the external fold command are env-overridable
     * so they can be tuned without a rebuild. */
    {
        g_ckpt_path[0] = '\0';
        if (ckpt_path && ckpt_path[0])
            snprintf(g_ckpt_path, sizeof(g_ckpt_path), "%s", ckpt_path);

        size_t store_bytes = 0;
        struct stat cst;
        if (g_ckpt_path[0] && stat(g_ckpt_path, &cst) == 0)
            store_bytes = (size_t)cst.st_size;

        double k = REPACK_RATIO * (double)store_bytes;
        if (k < (double)REPACK_K_MIN) k = (double)REPACK_K_MIN;
        if (k > (double)REPACK_K_MAX) k = (double)REPACK_K_MAX;
        g_repack_K = (size_t)k;

        const char *tau_s = getenv("PTOL_REPACK_TAU");
        if (tau_s && *tau_s) {
            double t = atof(tau_s);
            if (t >= 1.0) g_repack_tau = t;
        }
        const char *cmd_s = getenv("PTOL_REPACK_CMD");
        if (cmd_s && *cmd_s)
            snprintf(g_repack_cmd, sizeof(g_repack_cmd), "%s", cmd_s);

        g_last_repack = time(NULL);
        g_accum_ts    = g_last_repack;
        plog(PLOG_INFO, "daemon: repack timer — K=%zu B (store≈%zu B), "
             "tau=%.0fs, knee=%.0f%%, cmd=%s", g_repack_K, store_bytes,
             g_repack_tau, REPACK_KNEE * 100.0,
             g_repack_cmd[0] ? g_repack_cmd : "(checkpoint only)");
    }

    /* Signal handlers */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sig;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT,  &sa, NULL);
    signal(SIGCHLD, SIG_IGN);   /* reap detached repack folds automatically */

    /* Open the conversational-ingest pipe. O_RDONLY|O_NONBLOCK never blocks
     * even with no writer; a held write end keeps the reader from seeing
     * EOF as hooks come and go. Pipe failure is non-fatal — queries and the
     * spool drain still work. */
    int fifo_fd = -1, fifo_hold = -1;
    if (g_observe_fifo[0]) {
        if (mkfifo(g_observe_fifo, 0600) != 0 && errno != EEXIST)
            plog(PLOG_WARN, "daemon: mkfifo(%s): %s", g_observe_fifo, strerror(errno));
        fifo_fd   = open(g_observe_fifo, O_RDONLY | O_NONBLOCK);
        fifo_hold = open(g_observe_fifo, O_WRONLY | O_NONBLOCK);
        if (fifo_fd < 0)
            plog(PLOG_WARN, "daemon: open observe pipe: %s", strerror(errno));
    }
    drain_spool(m);   /* anything the hooks spooled while we were down */

    /* Serve loop — poll the query socket AND the ingest pipe. Ingest is
     * drained in slices between accept()s so a long turn never stalls a
     * STATUS / HEAR query, and idle gaps are spent draining the spool. */
    ObsState obs_st   = {0};               /* carried FIFO parse state */
    char   obs_buf[8192];
    size_t obs_len    = 0;
    int    idle_ticks = 0;

    while (!g_quit) {
        struct pollfd fds[2];
        fds[0].fd = server_fd; fds[0].events = POLLIN; fds[0].revents = 0;
        nfds_t nfds = 1;
        if (fifo_fd >= 0) {
            fds[1].fd = fifo_fd; fds[1].events = POLLIN; fds[1].revents = 0;
            nfds = 2;
        }

        int pr = poll(fds, nfds, 250);
        if (pr < 0) {
            if (errno == EINTR) continue;   /* signal — re-check g_quit */
            plog(PLOG_WARN, "daemon poll(): %s", strerror(errno));
            break;
        }
        if (pr == 0) {                       /* idle — use the gap */
            if (++idle_ticks >= 8) {
                drain_spool(m);
                maybe_repack(m, time(NULL));   /* check the asymptote knee */
                idle_ticks = 0;
            }
            continue;
        }

        if (fifo_fd >= 0 && (fds[1].revents & POLLIN)) {
            ssize_t nr = read(fifo_fd, obs_buf + obs_len,
                              sizeof(obs_buf) - 1 - obs_len);
            if (nr > 0) {
                obs_len += (size_t)nr;
                obs_buf[obs_len] = '\0';
                char *start = obs_buf, *nl;
                while ((nl = strchr(start, '\n')) != NULL) {
                    *nl = '\0';
                    observe_ingest_line(m, start, &obs_st);
                    start = nl + 1;
                }
                obs_len = strlen(start);
                memmove(obs_buf, start, obs_len + 1);
                if (obs_len == sizeof(obs_buf) - 1) {   /* overlong line — flush */
                    observe_ingest_line(m, obs_buf, &obs_st);
                    obs_len = 0; obs_buf[0] = '\0';
                }
            }
        }

        if (fds[0].revents & POLLIN) {
            int client = accept(server_fd, NULL, NULL);
            if (client < 0) {
                if (errno == EINTR) continue;
                if (!g_quit)
                    plog(PLOG_WARN, "daemon accept(): %s", strerror(errno));
                break;
            }
            handle_client(m, client, verbose);
            close(client);
        }
    }

    if (fifo_fd   >= 0) close(fifo_fd);
    if (fifo_hold >= 0) close(fifo_hold);
    if (g_observe_fifo[0]) unlink(g_observe_fifo);

    plog(PLOG_INFO, "daemon shutting down");

    if (monad3c_write_permitted()) {
        if (g_had_input) {
            long folded = monad3c_fold_inplace(m);   /* fold the tail in place */
            if (folded >= 0)
                plog(PLOG_INFO, "daemon shutdown fold — %ld values, %ld pending",
                     folded, g_monad3c_pending);
            if ((folded < 0 || g_monad3c_pending >= MONAD3C_REBUILD_AT)
                && g_repack_cmd[0])
                spawn_detached(g_repack_cmd);
        }
        if (ckpt_path) {
            plog(PLOG_INFO, "daemon saving checkpoint %s (accum was %.0f)",
                 ckpt_path, g_accum);
            state_save(m, ckpt_path, 0.0);
        }
    } else {
        plog(PLOG_WARN, "daemon: monad3_c.bin held by a bare Monad "
                        "— NOT persisting on shutdown");
    }

    close(server_fd);
    if (listen_fds_str == NULL) unlink(sock_path);
    pid_remove(pid_path);
    return 0;
}

/* ── Client ───────────────────────────────────────────────────────────────── */

static int client_connect(const char *sock_path)
{
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        fprintf(stderr, "[ptolemy] socket(): %s\n", strerror(errno));
        return -1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "[ptolemy] cannot connect to daemon at %s: %s\n",
                sock_path, strerror(errno));
        close(fd);
        return -1;
    }
    return fd;
}

/* Read lines from fd until ".\n" sentinel, printing each to stdout. */
static void client_read_response(int fd)
{
    FILE *f = fdopen(dup(fd), "r");
    if (!f) return;
    char line[4096];
    while (fgets(line, sizeof(line), f)) {
        if (strcmp(line, ".\n") == 0) break;
        fputs(line, stdout);
    }
    fclose(f);
}

int daemon_query(const char *query, const char *sock_path)
{
    int fd = client_connect(sock_path);
    if (fd < 0) return -1;

    dprintf(fd, "HEAR %s\n", query);
    client_read_response(fd);
    dprintf(fd, "QUIT\n");
    close(fd);
    return 0;
}

int daemon_command(const char *cmd, const char *sock_path)
{
    int fd = client_connect(sock_path);
    if (fd < 0) return -1;

    dprintf(fd, "%s\n", cmd);
    client_read_response(fd);
    dprintf(fd, "QUIT\n");
    close(fd);
    return 0;
}
