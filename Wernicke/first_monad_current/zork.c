/*
 * PtolC/zork.c — Infocom-style sentence parser for the monad REPL.
 *
 * Verb table mirrors zork_parser.py exactly.
 * Same 16 operators, same grammar, same direction shortcuts.
 */

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>

#include "zork.h"

/* ── Operator names ──────────────────────────────────────────────────────── */

static const char *OP_NAMES[ZORK_OP_COUNT] = {
    "identity", "negate",      "bind",        "name",
    "apply",    "abstract",    "branch",       "iterate",
    "recurse",  "allocate",    "query",        "dereference",
    "compose",  "parallelize", "interrupt",    "emit",
};

const char *zork_op_name(int k)
{
    if (k < 0 || k >= ZORK_OP_COUNT) return "?";
    return OP_NAMES[k];
}

/* ── Verb table ───────────────────────────────────────────────────────────── */

typedef struct { const char *verb; int op; } VerbEntry;

static const VerbEntry VERBS[] = {
    /* e0 identity */
    {"look",0},{"examine",0},{"x",0},{"l",0},{"what",0},{"describe",0},
    {"inspect",0},{"read",0},{"check",0},{"glance",0},{"observe",0},
    {"study",0},{"survey",0},{"scan",0},
    /* e1 negate */
    {"drop",1},{"remove",1},{"throw",1},{"discard",1},{"toss",1},
    {"destroy",1},{"break",1},{"smash",1},{"kill",1},{"attack",1},
    {"hit",1},{"strike",1},{"fight",1},{"negate",1},
    /* e2 bind */
    {"put",2},{"place",2},{"set",2},{"attach",2},{"connect",2},
    {"bind",2},{"tie",2},{"fasten",2},{"insert",2},{"load",2},
    {"fill",2},{"combine",2},{"merge",2},{"link",2},{"join",2},
    /* e3 name */
    {"call",3},{"name",3},{"label",3},{"title",3},{"define",3},
    {"say",3},{"tell",3},{"speak",3},{"shout",3},{"whisper",3},
    {"answer",3},{"reply",3},{"yell",3},
    /* e4 apply */
    {"use",4},{"press",4},{"push",4},{"activate",4},{"apply",4},
    {"turn",4},{"pull",4},{"flip",4},{"switch",4},{"touch",4},
    {"feel",4},{"rub",4},{"wave",4},{"operate",4},
    /* e5 abstract */
    {"take",5},{"get",5},{"pick",5},{"lift",5},{"grab",5},
    {"hold",5},{"carry",5},{"collect",5},{"gather",5},{"obtain",5},
    {"acquire",5},{"steal",5},{"snatch",5},
    /* e6 branch */
    {"go",6},{"move",6},{"walk",6},{"run",6},{"travel",6},
    {"enter",6},{"exit",6},{"leave",6},{"climb",6},{"jump",6},
    {"fly",6},{"swim",6},{"crawl",6},{"proceed",6},{"head",6},
    /* e7 iterate */
    {"count",7},{"list",7},{"search",7},{"find",7},{"seek",7},
    {"iterate",7},{"enumerate",7},{"repeat",7},{"try",7},
    {"attempt",7},{"explore",7},
    /* e8 recurse */
    {"open",8},{"unlock",8},{"solve",8},{"crack",8},{"decode",8},
    {"decipher",8},{"unwrap",8},{"unzip",8},{"recurse",8},
    {"dig",8},{"cut",8},
    /* e9 allocate */
    {"make",9},{"create",9},{"build",9},{"forge",9},{"construct",9},
    {"craft",9},{"write",9},{"draw",9},{"compose",9},{"allocate",9},
    {"new",9},{"spawn",9},{"generate",9},
    /* e10 query */
    {"ask",10},{"question",10},{"wonder",10},{"think",10},{"query",10},
    {"why",10},{"how",10},{"ponder",10},{"consider",10},
    {"contemplate",10},{"guess",10},{"know",10},{"understand",10},
    /* e11 dereference */
    {"follow",11},{"point",11},{"refer",11},{"track",11},{"trace",11},
    {"pursue",11},{"it",11},{"them",11},{"that",11},{"this",11},
    {"dereference",11},
    /* e12 compose */
    {"record",12},{"note",12},{"document",12},{"transcribe",12},
    {"copy",12},{"print",12},{"log",12},{"save",12},{"capture",12},
    /* e13 parallelize */
    {"together",13},{"simultaneously",13},{"also",13},
    {"parallelize",13},{"multi",13},{"both",13},{"dual",13},
    {"split",13},{"fork",13},
    /* e14 interrupt */
    {"stop",14},{"quit",14},{"pause",14},{"cancel",14},{"abort",14},
    {"halt",14},{"interrupt",14},{"end",14},{"finish",14},
    {"done",14},{"wait",14},
    /* e15 emit */
    {"show",15},{"display",15},{"output",15},{"reveal",15},{"emit",15},
    {"present",15},{"give",15},{"offer",15},{"share",15},{"send",15},
    {"pass",15},
    /* sentinel */
    {NULL, -1}
};

/* ── Direction shortcuts (e6 branch) ─────────────────────────────────────── */

typedef struct { const char *abbr; const char *full; } DirEntry;
static const DirEntry DIRS[] = {
    {"n","north"},{"s","south"},{"e","east"},{"w","west"},
    {"u","up"},{"d","down"},{"ne","northeast"},{"nw","northwest"},
    {"se","southeast"},{"sw","southwest"},
    {"north","north"},{"south","south"},{"east","east"},{"west","west"},
    {"up","up"},{"down","down"},{"in","in"},{"out","out"},
    {NULL,NULL}
};

/* ── Prepositions ─────────────────────────────────────────────────────────── */

static const char *PREPS[] = {
    "in","into","inside","on","onto","upon","under","beneath",
    "behind","through","from","off","about","with","to","at",
    "over","across","against","around","near","beside",NULL
};

/* ── Articles ─────────────────────────────────────────────────────────────── */

static const char *ARTICLES[] = {"the","a","an","some","any",NULL};

/* ── Pronoun table ─────────────────────────────────────────────────────────── */

static const char *PRONOUNS[] = {"it","them","that","this","those","these",NULL};

/* ── Module state ─────────────────────────────────────────────────────────── */

static char g_last_noun[ZORK_NOUN_MAX] = {0};

void zork_reset_context(void) { g_last_noun[0] = '\0'; }

/* ── Helpers ──────────────────────────────────────────────────────────────── */

static void str_lower(char *s)
{
    for (; *s; s++) *s = (char)tolower((unsigned char)*s);
}

static int is_article(const char *w)
{
    for (int i = 0; ARTICLES[i]; i++)
        if (strcmp(w, ARTICLES[i]) == 0) return 1;
    return 0;
}

static int is_prep(const char *w)
{
    for (int i = 0; PREPS[i]; i++)
        if (strcmp(w, PREPS[i]) == 0) return 1;
    return 0;
}

static int is_pronoun(const char *w)
{
    for (int i = 0; PRONOUNS[i]; i++)
        if (strcmp(w, PRONOUNS[i]) == 0) return 1;
    return 0;
}

static int lookup_verb(const char *v)
{
    for (int i = 0; VERBS[i].verb; i++)
        if (strcmp(v, VERBS[i].verb) == 0) return VERBS[i].op;
    return -1;
}

static const char *lookup_dir(const char *v)
{
    for (int i = 0; DIRS[i].abbr; i++)
        if (strcmp(v, DIRS[i].abbr) == 0) return DIRS[i].full;
    return NULL;
}

/* ── Simple tokeniser — writes into caller-provided array ─────────────────── */

#define MAX_TOKS 64
static int tokenise(const char *input, char toks[][128], int cap)
{
    int n = 0;
    const char *p = input;
    while (*p && n < cap) {
        while (*p && (isspace((unsigned char)*p) || *p == ',' ||
                      *p == ';' || *p == '.' || *p == '!')) p++;
        if (!*p) break;
        int i = 0;
        while (*p && !isspace((unsigned char)*p) && *p != ',' &&
               *p != ';' && *p != '.' && *p != '!' && i < 127)
            toks[n][i++] = *p++;
        toks[n][i] = '\0';
        if (i > 0) { str_lower(toks[n]); n++; }
    }
    return n;
}

/* ── Main parse ───────────────────────────────────────────────────────────── */

ZorkResult zork_parse(const char *input)
{
    ZorkResult r;
    memset(&r, 0, sizeof(r));
    r.op = -1;

    if (!input || !input[0]) {
        snprintf(r.error, sizeof(r.error), "I beg your pardon?");
        return r;
    }

    /* ── Slash command ────────────────────────────────────────────────── */
    if (input[0] == '/') {
        r.is_slash = 1;
        const char *p = input + 1;
        int ci = 0;
        while (*p && !isspace((unsigned char)*p) && ci < 63)
            r.slash_cmd[ci++] = *p++;
        r.slash_cmd[ci] = '\0';
        while (*p && isspace((unsigned char)*p)) p++;
        strncpy(r.slash_args, p, sizeof(r.slash_args) - 1);
        r.ok = 1;
        return r;
    }

    /* ── Tokenise ─────────────────────────────────────────────────────── */
    char toks[MAX_TOKS][128];
    int  ntok = tokenise(input, toks, MAX_TOKS);
    if (ntok == 0) {
        snprintf(r.error, sizeof(r.error), "I beg your pardon?");
        return r;
    }

    /* ── Direction shorthand ──────────────────────────────────────────── */
    const char *dir = lookup_dir(toks[0]);
    if (dir) {
        r.op = 6;
        strncpy(r.op_name, OP_NAMES[6], sizeof(r.op_name) - 1);
        strncpy(r.verb,    toks[0],     sizeof(r.verb) - 1);
        strncpy(r.noun,    dir,         sizeof(r.noun) - 1);
        snprintf(r.prompt, sizeof(r.prompt), "branch %s", dir);
        if (g_last_noun[0] == '\0') strncpy(g_last_noun, dir, ZORK_NOUN_MAX-1);
        r.ok = 1;
        return r;
    }

    /* ── Verb lookup ──────────────────────────────────────────────────── */
    int op = lookup_verb(toks[0]);

    /* 6-letter prefix expansion (Infocom rule) */
    if (op < 0 && strlen(toks[0]) >= 4) {
        for (int i = 0; VERBS[i].verb; i++) {
            size_t tl = strlen(toks[0]);
            size_t cmp = tl < 6 ? tl : 6;
            if (strncmp(toks[0], VERBS[i].verb, cmp) == 0 ||
                strncmp(VERBS[i].verb, toks[0], cmp) == 0) {
                op = VERBS[i].op;
                strncpy(toks[0], VERBS[i].verb, 127);
                break;
            }
        }
    }

    if (op < 0) {
        snprintf(r.error, sizeof(r.error),
            "I don't know '%s'. Try: look, take, put, go, use, open, say, find, make, ask",
            toks[0]);
        r.ok = 0;
        return r;
    }

    r.op = op;
    strncpy(r.op_name, OP_NAMES[op], sizeof(r.op_name) - 1);
    strncpy(r.verb,    toks[0],      sizeof(r.verb) - 1);

    /* ── Build noun list (skip articles, resolve pronouns) ───────────── */
    /* Collect non-verb tokens, skipping articles */
    char rest[MAX_TOKS][128];
    int  nrest = 0;
    for (int i = 1; i < ntok && nrest < MAX_TOKS; i++) {
        if (is_article(toks[i])) continue;
        if (is_pronoun(toks[i]) && g_last_noun[0]) {
            strncpy(rest[nrest++], g_last_noun, 127);
        } else {
            strncpy(rest[nrest], toks[i], 127);
            nrest++;
        }
    }

    /* ── Find preposition in middle ───────────────────────────────────── */
    int prep_pos = -1;
    for (int i = 1; i < nrest; i++) {
        if (is_prep(rest[i])) { prep_pos = i; break; }
    }

    if (prep_pos > 0) {
        strncpy(r.prep, rest[prep_pos], sizeof(r.prep) - 1);
        /* noun 1: tokens before prep */
        char buf[ZORK_NOUN_MAX] = {0};
        for (int i = 0; i < prep_pos; i++) {
            if (i) strncat(buf, " ", ZORK_NOUN_MAX - strlen(buf) - 1);
            strncat(buf, rest[i], ZORK_NOUN_MAX - strlen(buf) - 1);
        }
        strncpy(r.noun, buf, ZORK_NOUN_MAX - 1);
        /* noun 2: tokens after prep */
        buf[0] = '\0';
        for (int i = prep_pos + 1; i < nrest; i++) {
            if (i > prep_pos + 1) strncat(buf, " ", ZORK_NOUN_MAX - strlen(buf) - 1);
            strncat(buf, rest[i], ZORK_NOUN_MAX - strlen(buf) - 1);
        }
        strncpy(r.noun2, buf, ZORK_NOUN_MAX - 1);
    } else {
        /* all rest is one noun */
        char buf[ZORK_NOUN_MAX] = {0};
        for (int i = 0; i < nrest; i++) {
            if (i) strncat(buf, " ", ZORK_NOUN_MAX - strlen(buf) - 1);
            strncat(buf, rest[i], ZORK_NOUN_MAX - strlen(buf) - 1);
        }
        strncpy(r.noun, buf, ZORK_NOUN_MAX - 1);
    }

    /* Update last noun */
    if (r.noun[0])
        strncpy(g_last_noun, r.noun, ZORK_NOUN_MAX - 1);

    /* ── Build monad prompt ───────────────────────────────────────────── *
     * op_name + noun [prep noun2]                                        */
    char prompt[ZORK_PROMPT_MAX] = {0};
    strncat(prompt, OP_NAMES[op], ZORK_PROMPT_MAX - strlen(prompt) - 1);
    if (r.noun[0]) {
        strncat(prompt, " ", ZORK_PROMPT_MAX - strlen(prompt) - 1);
        strncat(prompt, r.noun, ZORK_PROMPT_MAX - strlen(prompt) - 1);
    }
    if (r.prep[0] && r.noun2[0]) {
        strncat(prompt, " ", ZORK_PROMPT_MAX - strlen(prompt) - 1);
        strncat(prompt, r.prep, ZORK_PROMPT_MAX - strlen(prompt) - 1);
        strncat(prompt, " ", ZORK_PROMPT_MAX - strlen(prompt) - 1);
        strncat(prompt, r.noun2, ZORK_PROMPT_MAX - strlen(prompt) - 1);
    }
    strncpy(r.prompt, prompt, ZORK_PROMPT_MAX - 1);

    r.ok = 1;
    return r;
}
