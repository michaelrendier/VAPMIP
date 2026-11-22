/*
 * PtolC/zork.h — Infocom-style sentence parser for the monad REPL.
 *
 * Verb-first lookup maps natural language to sedenion operator (e₀–e₁₅).
 * Mirrors zork_parser.py exactly — same verb table, same grammar templates.
 *
 * VERB  → sedenion operator
 * NOUN  → word in monad vocab
 * PREP  → relation label
 * IT    → last-mentioned noun (e₁₁ dereference)
 *
 * Slash commands (/generate, /status, /health, /verb) bypass the monad
 * and route to built-in REPL handlers.
 */

#ifndef ZORK_H
#define ZORK_H

#define ZORK_OP_COUNT   16
#define ZORK_NOUN_MAX   256
#define ZORK_PROMPT_MAX 512

typedef struct {
    int  op;                     /* sedenion operator 0–15, -1 if unknown */
    char op_name[32];
    char verb[64];
    char noun[ZORK_NOUN_MAX];    /* first noun phrase */
    char noun2[ZORK_NOUN_MAX];   /* second noun (ditransitive) */
    char prep[32];               /* preposition or empty */
    char prompt[ZORK_PROMPT_MAX];/* monad_speak() prompt */
    int  ok;                     /* 1 = parsed, 0 = unknown verb */
    char error[128];

    /* Slash command fields */
    int  is_slash;               /* 1 if input was /cmd ... */
    char slash_cmd[64];          /* command name after '/' */
    char slash_args[ZORK_PROMPT_MAX]; /* rest of line after /cmd */
} ZorkResult;

/* Parse a natural language sentence.
 * Returns ZorkResult; caller does not free anything. */
ZorkResult zork_parse(const char *input);

/* Name of sedenion operator k (0–15). */
const char *zork_op_name(int k);

/* State: last noun seen (for pronoun resolution across calls). */
void  zork_reset_context(void);

#endif /* ZORK_H */
