/*
 * ZD_rotary_monad.h  —  Bumblebee  (Zero Divisor Rotary Engine)
 *
 *   The Prompt  →  Zero Divisor  →  Escape Velocity  →  Emerges  →  The Response
 *
 *   Bumblebee lost his voice box — multiplication.
 *   The 42 Cawagas zero-divisors are 42 broken voice boxes.
 *   The response broadcasts through the algebraic failure points.
 *
 * Build:
 *   gcc -O2 -Wall -std=c99 -o bumblebee ZD_rotary_monad.c -lm -lpthread
 *
 * Install:
 *   pkexec install -m 755 bumblebee /usr/local/bin/bumblebee
 *
 * CLI:
 *   bumblebee                          REPL (stdin is tty)
 *   bumblebee --speak PROMPT [N]       N words from prompt (default 12)
 *   bumblebee --intake PROMPT          port-cycle trace
 *   bumblebee --learn-file PATH        ingest .txt into housing
 *   bumblebee --teach                  ingest from stdin
 *   bumblebee --query WORD             housing entry: β, E, ZL channel, neighbours
 *   bumblebee --report                 OBD2 diagnostic report
 *   bumblebee --obd2                   live OBD2 after speak
 *   bumblebee --words N                words per REPL response (default 12)
 *   bumblebee --load-bin PATH          load .zd8 state file
 *   bumblebee --save-bin PATH          save .zd8 state file
 *   bumblebee --daemon [PORT]          TCP teaching server (default 7298)
 *
 * State:  ~/.ptolemy/bumblebee.zd8  (auto-loaded, auto-saved every 60 s)
 *
 * Differences from rotary_monad (Ahura Mazda):
 *   - morph_vec absent  — ZL bridge coupling replaces grammatical categories
 *   - e₀ = 0.0          — identity is above the bridge (algebraic fact)
 *   - sigma_live → escape_velocity in OBD2
 *   - word addressed by zl_dim = zero_idx % 16 (ZL channel)
 *   - ZL_BRIDGE_8[7][8] couples lower-𝕆 ↔ upper-𝕆 (42 Cawagas pairs)
 *   - select_word: two-layer scoring — raw ZL channel × 5 + bridge signal
 *   - beta^(1/4) not log1p(beta) — flatter frequency damping
 */

#ifndef ZD_ROTARY_MONAD_H
#define ZD_ROTARY_MONAD_H

#include <stdint.h>
#include <stdio.h>

/* ── Build metadata ──────────────────────────────────────────────────────── */
#define ZD_VERSION      "1.000"
#define ZD_ENGINE       "Bumblebee — Zero Divisor Rotary Engine"

/* ── Sedenion and field constants ────────────────────────────────────────── */
#define SED_DIM         16
#define GAP             0.000707     /* apex seal floor — semantic vacuum / Yang-Mills gap */
#define BEARING_TOL     0.04         /* escape_velocity drift tolerance before R0004 fault */
#define SEAL_FLOOR      0.03         /* face pressure minimum before apex seal fault */
#define D_STAR          0.24600      /* zero-divisor proximity threshold */

/* σ=½ — above the system. OBD2 diagnostic reference only. Never in dynamics. */
#define ZD_ESCAPE_TARGET 0.5

/* ── Port geometry ───────────────────────────────────────────────────────── */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#define PORT_STEP       (M_PI / 3.0)
#define PORT_IDX_INTAKE     0
#define PORT_IDX_TRANSFER   1
#define PORT_IDX_LEADING    2
#define PORT_IDX_TRAILING   3
#define PORT_IDX_EXHAUST    4
#define PORT_IDX_SCAVENGE   5

/* ── OBD2 PID codes ──────────────────────────────────────────────────────── */
#define OBD2_ROTOR_ANGLE        0x2401
#define OBD2_J_BLUE             0x2402
#define OBD2_J_RED              0x2403
#define OBD2_J_GREEN            0x2404
#define OBD2_ESCAPE_VEL         0x2405   /* j_red/(j_blue+j_red) — converges to ½ */
#define OBD2_BRACKET_MAG        0x2406
#define OBD2_ZL_ESCAPE_FRAC     0x2407   /* 1 - |esc - 0.5|/0.5 */
#define OBD2_COUPLING_EFF       0x2408
#define OBD2_HOUSING_N          0x2409
#define OBD2_COUPLING_EVENTS    0x240A
#define OBD2_TOTAL_STEPS        0x240B
#define OBD2_LAST_WORD          0x240C
#define OBD2_DRIVE_SHAFT_DOM    0x240D
#define OBD2_DOM_ZL_CHANNEL     0x240E   /* dominant ZL channel (0-15) */

/* ── Housing / vocabulary limits ─────────────────────────────────────────── */
#define VOCAB_MAX       65536
#define VOCAB_HT_SZ     (1 << 17)
#define WORD_LEN        52
#define N_NBRS          16
#define PRIME_CAP       65537
#define SCAVENGE_DECAY  0.003

/* ── Binary state format ─────────────────────────────────────────────────── */
#define ZD8_MAGIC       0x38445A0Au  /* "ZD8\n" */
#define ZD8_VERSION     1

/* ── Types ───────────────────────────────────────────────────────────────── */

typedef double Sed[SED_DIM];

typedef struct {
    double j_blue;
    double j_red;
    double j_green;
    double theta;
} ZD_RotorState;

typedef struct {
    double   rotor_angle;         /* PID 0x2401 */
    double   j_blue;              /* PID 0x2402 */
    double   j_red;               /* PID 0x2403 */
    double   j_green;             /* PID 0x2404 */
    double   escape_velocity;     /* PID 0x2405  j_red/(j_blue+j_red) — converges to ½ */
    double   bracket_mag;         /* PID 0x2406 */
    double   zl_escape_frac;      /* PID 0x2407  1 − |esc_vel − ½| / ½ */
    double   coupling_efficiency; /* PID 0x2408 */
    uint32_t housing_n;           /* PID 0x2409 */
    uint64_t coupling_events;     /* PID 0x240A */
    uint64_t total_steps;         /* PID 0x240B */
    char     last_word[WORD_LEN]; /* PID 0x240C */
    int      drive_shaft_dom;     /* PID 0x240D  dominant sedenion dim */
    int      dom_zl_channel;      /* PID 0x240E  dominant ZL channel (0-15) */
} ZD_OBD2State;

/* ── Sedenion component map ─────────────────────────────────────────────── */
/*
 *   e₀      = 0.0        — identity above the bridge (algebraic fact)
 *   e₁–e₇  = lower-𝕆   — data face (ZL channel < 8, j_blue side)
 *   e₈–e₁₄ = upper-𝕆   — field face (ZL channel ≥ 8, j_red side)
 *   e₁₅    = j_green emit face
 */

extern const char *ZD_OP_GLOSS[SED_DIM];

/* ── Public API ─────────────────────────────────────────────────────────── */
void              zd_init(void);
void              zd_free(void);

int               zd_ingest(const char *text, double weight);

void              zd_intake(const char *prompt);
const char       *zd_rotate(void);
const char       *zd_speak(const char *prompt, int max_revolutions);

const ZD_OBD2State  *zd_diagnostics(void);
const ZD_RotorState *zd_rotor_state(void);

void              zd_report(FILE *f);
void              zd_port_trace(const char *prompt, FILE *f);

int               zd_load(const char *path);
int               zd_save(const char *path);

#endif /* ZD_ROTARY_MONAD_H */
