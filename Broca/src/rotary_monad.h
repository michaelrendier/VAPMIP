/*
 * rotary_monad.h  —  Ahura Mazda
 * Wankel rotary semantic engine.  Public API header.
 *
 * Include this in callers.  Implementation: rotary_monad.c
 *
 *   3 = 1 + 15i
 *
 *   The Worker (rotor):    j_blue, j_red, j_green  — three scalar pressures
 *   The Work   (sedenion): e₀ + e₁…e₇ + e₈…e₁₄ + e₁₅ — produced at coupling only
 *
 *   The Sedenion is The Work, not The Worker.
 *
 * Build:
 *   gcc -O2 -Wall -std=c99 -o ahura-mazda rotary_monad.c -lm -lpthread
 *
 * Install:
 *   pkexec install -m 755 ahura-mazda /usr/local/bin/ahura-mazda
 *
 * CLI:
 *   ahura-mazda                          REPL (stdin is tty)
 *   ahura-mazda prompt text here         immediate response, then REPL
 *   ahura-mazda --speak PROMPT [N]       produce N words from prompt (default 12)
 *   ahura-mazda --intake PROMPT          trace one full port cycle step-by-step
 *   ahura-mazda --learn-file PATH        ingest .txt into housing
 *   ahura-mazda --teach                  ingest from stdin (no response)
 *   ahura-mazda --query WORD             housing entry: β, E, morph vector, neighbours
 *   ahura-mazda --report                 OBD2 diagnostic report
 *   ahura-mazda --obd2                   live OBD2 stream after speak
 *   ahura-mazda --words N                words per REPL response (default 12)
 *   ahura-mazda --load-bin PATH          load .rx8 state file
 *   ahura-mazda --save-bin PATH          save .rx8 state file
 *   ahura-mazda --daemon [PORT]          TCP teaching server (default 7297)
 *
 * State:  ~/.ptolemy/ahura.rx8  (auto-loaded, auto-saved every 60 s)
 *
 * Dropped from monad.c (not applicable to rotary engine):
 *   --generate     cam_encode sedenion generation — replaced by Wankel --speak
 *   --url          HTTP fetch — rotor runs on ingested text, not live HTTP streams
 */

#ifndef ROTARY_MONAD_H
#define ROTARY_MONAD_H

#include <stdint.h>
#include <stdio.h>

/* ── Build metadata ─────────────────────────────────────────────────────── */
#define AHURA_VERSION   "1.000"
#define AHURA_ENGINE    "Ahura Mazda — Wankel Rotary Semantic Engine"

/* ── Sedenion and field constants ────────────────────────────────────────── */
#define SED_DIM         16
#define SIGMA_PIN       0.5          /* eccentric shaft — ξ(s)=ξ(1-s), never computed */
#define GAP             0.000707     /* apex seal floor  — semantic vacuum / Yang-Mills gap */
#define BEARING_TOL     0.04         /* σ drift tolerance before R0004 bearing fault */
#define SEAL_FLOOR      0.03         /* face pressure minimum before apex seal fault */
#define D_STAR          0.24600      /* zero-divisor proximity threshold */
#define PHI             1.6180339887498949
#define SQRT2           1.4142135623730951

/* ── Port geometry ───────────────────────────────────────────────────────── */
/* Six ports at 60° intervals.  Rotor advances exactly PORT_STEP per rotate(). */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#define PORT_STEP       (M_PI / 3.0)
/* Port index 0-5 = round(theta/PORT_STEP) % 6 */
#define PORT_IDX_INTAKE     0   /* θ=0       field renewal */
#define PORT_IDX_TRANSFER   1   /* θ=π/3     begin bracket mixing */
#define PORT_IDX_LEADING    2   /* θ=2π/3    leading spark */
#define PORT_IDX_TRAILING   3   /* θ=π       trailing spark + unconditional coupling */
#define PORT_IDX_EXHAUST    4   /* θ=4π/3    word crystallised */
#define PORT_IDX_SCAVENGE   5   /* θ=5π/3    gentle field decay */

/* ── OBD2 PID codes ──────────────────────────────────────────────────────── */
#define OBD2_ROTOR_ANGLE        0x2301
#define OBD2_J_BLUE             0x2302
#define OBD2_J_RED              0x2303
#define OBD2_J_GREEN            0x2304
#define OBD2_SIGMA_LIVE         0x2305
#define OBD2_BRACKET_MAG        0x2306
#define OBD2_APEX_SEAL_HEALTH   0x2307
#define OBD2_COUPLING_EFF       0x2308
#define OBD2_HOUSING_N          0x2309
#define OBD2_COUPLING_EVENTS    0x230A
#define OBD2_TOTAL_STEPS        0x230B
#define OBD2_LAST_WORD          0x230C
#define OBD2_DRIVE_SHAFT_DOM    0x230D

/* ── Housing / vocabulary limits ─────────────────────────────────────────── */
#define VOCAB_MAX       65536
#define VOCAB_HT_SZ     (1 << 17)   /* 131072 hash table slots */
#define WORD_LEN        52
#define N_NBRS          16           /* A-matrix neighbours per word */
#define PRIME_CAP       65537        /* sieve bound */
#define WINDOW_SZ       16           /* context ring buffer — for annotation */
#define SCAVENGE_DECAY  0.003        /* beta decay per scavenge port */

/* ── Binary state format ─────────────────────────────────────────────────── */
#define RX8_MAGIC       0x3858520Au  /* "RX8\n" little-endian */
#define RX8_VERSION     1

/* ── Types ───────────────────────────────────────────────────────────────── */

/* Drive shaft sedenion — the Work.  Produced ONCE at coupling.  Never input. */
typedef double Sed[SED_DIM];

/*
 * RotorState — the Worker.
 * j_blue, j_red, j_green are scalar pressures, NOT sedenions.
 * The sedenion does not appear here.
 */
typedef struct {
    double j_blue;   /* face 1: compressible / prompt / Fermat / intake */
    double j_red;    /* face 2: incompressible / field / Riemann / power */
    double j_green;  /* face 3: minimal surface / output / exhaust */
    double theta;    /* rotor angle [0, 2π) */
} RotorState;

/* OBD2State — live VAG-COM stream.  All values are continuous gradients. */
typedef struct {
    double   rotor_angle;         /* PID 0x2301  θ  [0, 2π) */
    double   j_blue;              /* PID 0x2302  face 1 pressure */
    double   j_red;               /* PID 0x2303  face 2 pressure */
    double   j_green;             /* PID 0x2304  face 3 pressure */
    double   sigma_live;          /* PID 0x2305  eccentric shaft alignment */
    double   bracket_mag;         /* PID 0x2306  [J_blue,J_red] combustion */
    double   apex_seal_health;    /* PID 0x2307  1 − |σ−½|/BEARING_TOL */
    double   coupling_efficiency; /* PID 0x2308  coupled / total sweeps */
    uint32_t housing_n;           /* PID 0x2309  vocabulary size */
    uint64_t coupling_events;     /* PID 0x230A  successful couplings */
    uint64_t total_steps;         /* PID 0x230B  rotor steps taken */
    char     last_word[WORD_LEN]; /* PID 0x230C  last emitted word */
    int      drive_shaft_dom;     /* PID 0x230D  dominant e-dim on drive shaft */
} OBD2State;

/* ── Sedenion component map (drive shaft channels) ───────────────────────── */
/*
 *   e₀      = coupling quality  (1 − |σ_live − ½|)
 *   e₁–e₇  = J_blue face work  (lower imaginary: grammar / content)
 *   e₈–e₁₄ = J_red  face work  (upper imaginary: context / memory)
 *   e₁₅    = J_green emit face (output surface)
 */

/* ── Operator glosses ─────────────────────────────────────────────────────── */
extern const char *AHURA_OP_GLOSS[SED_DIM];

/* ── Public API ────────────────────────────────────────────────────────────
 *
 * Typical usage:
 *   ahura_init();
 *   ahura_ingest(text, 1.0);            // build housing from corpus
 *   const char *w = ahura_speak(prompt, 4);  // Wankel cycle → one word
 *   const OBD2State *d = ahura_diagnostics();
 *   ahura_save(path);
 *   ahura_free();
 */
void             ahura_init(void);
void             ahura_free(void);

int              ahura_ingest(const char *text, double weight);

/* Low-level Wankel cycle: call intake() once, then rotate() until non-NULL */
void             ahura_intake(const char *prompt);
const char      *ahura_rotate(void);

/* High-level: intake + rotate up to max_revolutions × 6 steps → one word */
const char      *ahura_speak(const char *prompt, int max_revolutions);

const OBD2State *ahura_diagnostics(void);
const RotorState *ahura_rotor_state(void);

/* Formatted diagnostic report to FILE (stdout/stderr/file) */
void             ahura_report(FILE *f);

/* Port-cycle trace: intake prompt, then step through all 6 ports with OBD2 */
void             ahura_port_trace(const char *prompt, FILE *f);

int              ahura_load(const char *path);
int              ahura_save(const char *path);

#endif /* ROTARY_MONAD_H */
