/*
 * PtolC/code.c — Source file cognition: lower-𝕆 operator dim mapping.
 *
 * Reads C or Python source files and counts keyword occurrences that
 * proxy for the lower-𝕆 sedenion operator labels (e₀..e₇):
 *
 *   e₀  identity  — total lines (complexity norm)
 *   e₁  negate    — return / break / continue / raise / assert
 *   e₂  bind      — #include / import / from … import
 *   e₃  name      — = assignment / := walrus / var declarations
 *   e₄  apply     — function calls: identifier followed by '('
 *   e₅  abstract  — function/class/struct/typedef/def/class definitions
 *   e₆  branch    — if / else / switch / case / match / elif
 *   e₇  iterate   — for / while / do / comprehension [ for
 *
 * No external parser. Token counting via line-scan. Fast and dependency-free.
 *
 * Dominant operator (highest count, excluding e₀) is the structural
 * fingerprint of the file. A function-heavy file hits e₅ (abstract);
 * a control-flow heavy file hits e₆/e₇.
 *
 * e₅(abstract) → e₁₂(compose): the strongest sedenion zero-divisor coupling
 * channel. Abstract-heavy files push hardest through the cognitive half.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#include "code.h"
#include "log.h"

/* ── Keyword tables ───────────────────────────────────────────────────────── */

/* e₁ negate */
static const char *_KW_NEGATE[] = {
    "return", "break", "continue", "raise", "assert", "goto", "throw", NULL
};

/* e₂ bind (whole-word or directive) */
static const char *_KW_BIND[] = {
    "#include", "import", NULL
};

/* e₅ abstract (function/class/type definitions) */
static const char *_KW_ABSTRACT[] = {
    "def ", "class ", "struct ", "typedef ", "fn ", "func ", NULL
};

/* e₆ branch */
static const char *_KW_BRANCH[] = {
    "if ", "if(", "else", "elif ", "switch ", "switch(",
    "case ", "match ", NULL
};

/* e₇ iterate */
static const char *_KW_ITERATE[] = {
    "for ", "for(", "while ", "while(", "do {", "do{",
    " for ", "[for ", NULL
};

/* ── Helpers ──────────────────────────────────────────────────────────────── */

static int kw_match(const char *line, const char *kw)
{
    return strstr(line, kw) != NULL;
}

/* Count occurrences of '(' preceded by an identifier char — proxy for calls */
static int count_calls(const char *line)
{
    int n = 0;
    for (const char *p = line; *p; p++) {
        if (*p == '(' && p > line &&
            (isalnum((unsigned char)p[-1]) || p[-1] == '_'))
            n++;
    }
    return n;
}

/* Count '=' that are assignments (not ==, !=, <=, >=, :=) */
static int count_assignments(const char *line)
{
    int n = 0;
    for (const char *p = line + 1; *p; p++) {
        if (*p == '=' &&
            p[-1] != '=' && p[-1] != '!' && p[-1] != '<' &&
            p[-1] != '>' && p[-1] != ':' &&
            (*(p+1) != '='))
            n++;
    }
    return n;
}

/* ── Core file reader ─────────────────────────────────────────────────────── */

int code_read_file(const char *path, CodeProfile *profile)
{
    if (!path || !profile) return 0;

    memset(profile, 0, sizeof(*profile));
    strncpy(profile->path, path, sizeof(profile->path) - 1);

    FILE *f = fopen(path, "r");
    if (!f) {
        plog(PLOG_WARN, "code_read: cannot open %s", path);
        return 0;
    }

    char line[4096];
    while (fgets(line, sizeof(line), f)) {
        profile->counts[CODE_DIM_IDENTITY]++;   /* e₀: line count */

        /* Strip leading whitespace for keyword matching */
        const char *trimmed = line;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++;

        /* e₁ negate */
        for (int i = 0; _KW_NEGATE[i]; i++)
            if (kw_match(trimmed, _KW_NEGATE[i]))
                profile->counts[CODE_DIM_NEGATE]++;

        /* e₂ bind */
        for (int i = 0; _KW_BIND[i]; i++)
            if (kw_match(trimmed, _KW_BIND[i]))
                profile->counts[CODE_DIM_BIND]++;

        /* e₃ name */
        profile->counts[CODE_DIM_NAME] += count_assignments(trimmed);

        /* e₄ apply */
        profile->counts[CODE_DIM_APPLY] += count_calls(trimmed);

        /* e₅ abstract */
        for (int i = 0; _KW_ABSTRACT[i]; i++)
            if (kw_match(trimmed, _KW_ABSTRACT[i]))
                profile->counts[CODE_DIM_ABSTRACT]++;

        /* e₆ branch */
        for (int i = 0; _KW_BRANCH[i]; i++)
            if (kw_match(trimmed, _KW_BRANCH[i]))
                profile->counts[CODE_DIM_BRANCH]++;

        /* e₇ iterate */
        for (int i = 0; _KW_ITERATE[i]; i++)
            if (kw_match(trimmed, _KW_ITERATE[i]))
                profile->counts[CODE_DIM_ITERATE]++;
    }

    fclose(f);

    /* Determine dominant operator (e₁..e₇, excluding e₀ identity) */
    profile->dominant_dim = 1;
    for (int i = 2; i < 8; i++) {
        if (profile->counts[i] > profile->counts[profile->dominant_dim])
            profile->dominant_dim = i;
    }

    return 1;
}

/* ── Normalise to unit vector ─────────────────────────────────────────────── */

void code_profile_to_vec(const CodeProfile *profile, float *vec8)
{
    /* e₀ = clamped complexity; e₁..e₇ = count ratios */
    int lines = profile->counts[CODE_DIM_IDENTITY];
    vec8[0] = (lines > 0) ? fminf((float)lines / 500.0f, 1.0f) : 0.0f;
    float total = 0.0f;
    for (int i = 1; i < 8; i++) {
        vec8[i] = (lines > 0) ? (float)profile->counts[i] / (float)lines : 0.0f;
        total  += vec8[i] * vec8[i];
    }
    /* Normalise e₁..e₇ to unit sphere (preserve e₀) */
    float norm = sqrtf(total);
    if (norm > 0.0f)
        for (int i = 1; i < 8; i++)
            vec8[i] /= norm;
}

/* ── Print ────────────────────────────────────────────────────────────────── */

static const char *_DIM_NAME[8] = {
    "identity", "negate", "bind", "name",
    "apply", "abstract", "branch", "iterate"
};

void code_profile_print(const CodeProfile *profile, FILE *out)
{
    fprintf(out, "code_profile: %s\n", profile->path);
    for (int i = 0; i < 8; i++) {
        fprintf(out, "  e%d %-10s %d%s\n",
                i, _DIM_NAME[i], profile->counts[i],
                (i == profile->dominant_dim) ? "  ← dominant" : "");
    }
    fprintf(out, "  dominant_op: %s\n", _DIM_NAME[profile->dominant_dim]);
}
