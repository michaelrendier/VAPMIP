# 07 — Rhetorical Structure and Connective Selection (M-RST)

**Purpose:** give a larger text object a *structure*, and choose the connecting
words from the *relation* between units — the second mechanism of
`02_content_vs_pathway_words.md`.

---

## 1. The theory (Mann & Thompson, 1988) [LIT]

A text is a tree. Leaves are text units (clauses/sentences). Internal nodes join
units by a **rhetorical relation**. Most relations are **nucleus–satellite**: the
nucleus carries the main point; the satellite supports it (evidence, background,
elaboration…). Some are **multinuclear** (sequence, contrast, list). A relation is
usually signalled in the surface text by a **discourse connective** ("because",
"however", "for example") or by structure alone.

## 2. Relation inventory used by this spec [HYP — a deliberately small set]

The full RST set has ~25–30 relations. The calibration set starts with 12, chosen
because each has a clear connective signal and a clear relation to a speech act.

| ID | Relation | Type | Gloss |
|---|---|---|---|
| R-ELAB | Elaboration | N–S | satellite adds detail to nucleus |
| R-EXAM | Example | N–S | satellite instantiates the nucleus |
| R-CAUS | Cause | N–S | satellite is the reason for the nucleus (or reverse: R-RES, Result) |
| R-RES | Result | N–S | satellite is the consequence |
| R-EVID | Evidence | N–S | satellite supports belief in the nucleus |
| R-BACK | Background | N–S | satellite supplies context to understand the nucleus |
| R-CONC | Concession | N–S | satellite grants a point against the nucleus |
| R-COND | Condition | N–S | nucleus holds if the satellite holds |
| R-CONT | Contrast | multinuclear | two units differ on a salient dimension |
| R-SEQ | Sequence | multinuclear | units in temporal / procedural order |
| R-LIST | List / Joint | multinuclear | units on equal footing |
| R-SUM | Summary | N–S | satellite restates the nucleus compactly |

`relation_to_prev` in a plan unit (`01_*` §4) takes a value from this list or null.

## 3. Relation → connective table (the pathway mechanism's data)

Seed entries [HYP]. Columns: the register bands from `REGISTER_BANDS`
(narrative / surface / technical / thesis) restrict which connectives are allowed.

| Relation | narrative | surface | technical | thesis |
|---|---|---|---|---|
| R-ELAB | and | also; in addition | furthermore; moreover | moreover |
| R-EXAM | for example | for instance; such as | for instance | for example |
| R-CAUS | because | since; because | since | given that |
| R-RES | so | therefore | consequently; thus | consequently; hence |
| R-EVID | after all | as shown by | as evidenced by | this is evidenced by |
| R-BACK | (none) | in this context | in this setting | in this setting |
| R-CONC | but | although | although; even though | notwithstanding |
| R-COND | if | if; when | provided that | provided that |
| R-CONT | but | however | in contrast; however | by contrast |
| R-SEQ | then | first … then; next | subsequently | subsequently |
| R-LIST | and | also | likewise | likewise |
| R-SUM | so | in short | in summary | in summary |

Rule: an empty cell means *no connective is required*; the relation may be
signalled by structure alone, and the planner may emit null (`RST-04`).

The table is data (a versioned file), not code (SPL-R3). It is a seed, expected to
be extended by the tests below.

## 4. Selecting the relation (the hard part) [HYP]

The vocabulary mechanism gives *what* to say; something must decide *how this unit
relates to the last one*. Candidate signals, each testable:

| Signal | Source | Suggests |
|---|---|---|
| Speech act of the unit | `SPEECH_ACTS` | `why` → R-CAUS/R-EVID; `how` → R-SEQ; `define_X` → R-ELAB/R-EXAM; `yesno` → R-EVID/R-ELAB |
| Topic closeness of unit to previous | cosine of `ĉ` vectors (`04_*`) | very high → R-ELAB/R-EXAM; moderate → R-CONT/R-LIST; low → new segment (`05_*`) |
| Focus transition | Centering (`06_*`) | CONTINUE → R-ELAB/R-SEQ; SMOOTH-SHIFT → R-LIST/R-CONT; ROUGH-SHIFT → R-BACK |
| Polarity / antonymy | `Lemma.antonyms()` between key words (WordNet) | antonym pair across units → R-CONT/R-CONC |
| Causal lexicon | `Synset.causes()`, `entailments()` slots of `vec19` (slots 11, 12) | non-zero ⇒ R-CAUS/R-RES candidate |
| Plan position | step index | first unit → null; last → R-SUM candidate |

The relation selector is a deterministic rule table over these signals. It does
not learn. Its accuracy is measured against gold relations (`RST-02`). Where no
signal fires it returns **R-ELAB as the default** only if the default is declared
and counted separately (the default rate is a reported metric, so a high default
rate cannot hide inside accuracy).

## 5. Data files

`connective_inventory.json` (to be created with the implementation):

```json
{
  "version": "0.1",
  "rows": [
    {"relation": "R-CAUS", "register": "surface", "connective": "since", "position": "front"},
    {"relation": "R-CONT", "register": "surface", "connective": "however", "position": "front"}
  ]
}
```

`position` ∈ {front, mid, back}; the realiser uses it for clause attachment.
Uniqueness key: `(relation, register, connective)`.

## 6. Aggregation (Reiter & Dale microplanning) [LIT]

Aggregation merges adjacent simple units into one sentence using a connective
(for example two R-LIST units sharing a subject become one clause with "and").
Spec rules [HYP]:

- Aggregate adjacent units only if they share `focus_entity` (so Centering is
  preserved) and the relation is in {R-LIST, R-ELAB, R-SEQ, R-CAUS}.
- Never aggregate across a segment boundary (`05_*`).
- Cap the merged length at a clause budget [PARAM].

## 7. Tests

| ID | Checks | Metric |
|---|---|---|
| `RST-01` | Chosen connective ∈ admissible set for (relation, register) | exact |
| `RST-02` | **Relation recovery**: remove the connective from a gold pair, predict the relation from signals; accuracy against gold, with default-rate reported | MET-ACC, MET-DEF |
| `RST-03` | Speech-act prior: relation distribution per speech act in the reference set vs the rule table's priors | MET-TV |
| `RST-04` | Structure-only cells: planner emits null where the table is empty | exact |
| `RST-05` | Aggregation preserves Centering transition (no ROUGH-SHIFT introduced) | exact |
| `RST-06` | Rotation: repeated relation across a response does not repeat the same connective consecutively when alternatives exist | exact |
| `RST-07` | Inventory file validates and has unique keys | exact |
| `RST-08` | Register consistency: no technical-band connective in a narrative-band unit | exact |

## 8. Known weak points

- Inter-annotator agreement on RST relations in the literature is modest; the
  small inventory is chosen to limit that, but the gold relations are one
  annotator's (the calibration set author's) judgement. Report it as such.
- Many relations are signalled without a connective in real prose; the table's
  empty cells model that, but the *rate* in real text is not claimed here.
- Relation selection from shallow signals will be wrong often; the measure that
  matters for generation is whether the *connective chosen is admissible*
  (`RST-01`), which holds even when the relation guess is poor.

## 9. C-port notes

The table becomes a dense array indexed `[relation][register][rotation]` of
offsets into a string blob. The signal rules are a short chain of integer
comparisons.
