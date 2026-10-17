# 02 — Content Words versus Pathway Words (M-SPLIT)

**Claim under specification:** the NOUN, VERB and ADVERB the Zork Sentence Parser
handles are selected by *context encoded in the vocabulary*. The connecting words
("pathway words") are selected by a *different mechanism*: the relation between
two units of text. This document defines the split precisely enough to test.

---

## 1. Definitions

**Content word.** A word whose selection is driven by topic. Its meaning is
carried in the vocabulary store: `vec[19]` and Γ_rad of the sense chosen. Classes
in scope: NOUN, VERB, ADVERB. (Adjectives are not named in the request; this
spec places them with NOUN modifiers and flags the placement as [PARAM: `adj_class`]
to be settled by the author — see §6.)

**Pathway word.** A word whose job is to relate units rather than to name things.
Classes: coordinating and subordinating conjunctions, discourse connectives
("however", "therefore", "for example"), sequencing adverbials ("first", "then"),
prepositions used as relation labels, pronouns used as references, and
auxiliaries/copulas required by the clause pattern.

**Boundary case.** Some words are both: "because" is a pathway word (relation:
Cause) but is also in WordNet; "then" is an adverb in WordNet but functions as a
sequence connective. The spec resolves this by **function in the plan**, not by
dictionary class: a word is a pathway word if and only if it is chosen to realise
`relation_to_prev` of a plan unit (or a clause-internal relation: prepositions as
relation labels per `zork.h` `PREP → relation label`).

## 2. Evidence that the split already exists in the code [CODE]

| Where | Evidence |
|---|---|
| `PtolC/zork.h` | Separate roles: `VERB → operator`, `NOUN → word in monad vocab`, `PREP → relation label`, `IT → last-mentioned noun`. PREP and IT are not vocabulary lookups. |
| `ptol.c` `console_speak` | Content words come from `get_monad_words` / the 16-shell firing. The sentence creator receives `WORDS` (content lemmas) and an `ACT`; connectives are not in `WORDS`. |
| `sails.py` `SPEECH_ACTS` | `why` carries `"advcl": "because"` — a connective attached by the **act**, not by the vocabulary. |
| `engine/grammar/shadow.py` | `OBL = {obl, advmod, advcl, ...}` and `XC = {xcomp, ccomp}` — dependency labels that are relation-level, separate from the lemmas they dominate. |

## 3. The two mechanisms

### 3.1 Vocabulary mechanism (content words)

- **Input:** topic (context state `C[L]`, ring position `(r₁, r₂)`), slot required
  (`SPOCA` slot and part of speech), register band.
- **Operation:** rank candidate lemmas of the right POS by closeness of their
  `vec[19]` (and Γ_rad band) to the topic; select by the traversal rule in
  `03_smith_chart_topic_land.md`.
- **Existing code:** `generate.py` `_rank`, `_resonant_pick`, `fill_phase`, with
  `_band_ok` enforcing register. [CODE]
- **Guarantee:** every content word returned has `in_store = true`
  (test `GEN-03`).

### 3.2 Pathway mechanism (connectives)

- **Input:** `relation_to_prev` of the unit (RST relation, `07_rst_connectives.md`),
  register band, and optionally the speech act.
- **Operation:** look up the admissible connective set for the relation, filtered
  by register; choose by a deterministic rule (first in the register-ordered list,
  rotated by `step` to avoid repetition — [PARAM: `rotation`]).
- **Guarantee:** the chosen connective is a member of the relation's admissible
  set (test `RST-01`); the set is disjoint from the vocabulary mechanism's output
  in the sense of §4.

## 4. Disjointness requirement

**SPL-R1.** The vocabulary mechanism must never emit a word that is in the
connective inventory *as a content word of the plan*. If a topic word equals a
connective ("then" as a topic) the plan unit must mark it `quoted` and the
realiser must not reuse it as a connective in the same unit.

**SPL-R2.** The pathway mechanism must never read `vec[19]`. (Its inputs are
relation labels, not topic.) This is what makes the two mechanisms independent and
therefore separately testable.

**SPL-R3.** A word's membership in the connective inventory is a *table*, not a
computation. The table is a versioned data file (`schemas/connective_inventory`
described in `07_*` §5) so it can be extended without code change.

## 5. Inventory (seed) [HYP — to be extended]

The seed lists below are starting points drawn from standard English discourse
usage, not from a measured corpus. They are meant to be *extended by test*, not
trusted.

| Class | Seed members |
|---|---|
| Coordinating conjunction | and, but, or, nor, so, yet, for |
| Subordinating conjunction | because, although, while, if, unless, since, when, after, before, until, whereas |
| Additive connective | also, moreover, furthermore, in addition |
| Contrastive connective | however, but, yet, nevertheless, in contrast, on the other hand |
| Causal / resultative | therefore, thus, consequently, as a result, hence |
| Exemplifying | for example, for instance, such as |
| Sequencing | first, second, then, next, finally, afterward |
| Concessive | although, even though, despite, nonetheless |
| Summarising | in summary, overall, in short |
| Reference (pronominal) | it, they, this, that, these, those |
| Relation-label prepositions | in, on, at, of, to, from, with, by, for, about |

## 6. Open questions for the author

| ID | Question | Why it matters |
|---|---|---|
| SPL-Q1 | Where do adjectives sit? The request names NOUN, VERB, ADVERB only. | Decides whether adjectives are chosen by topic (vocabulary mechanism) or are a third class. |
| SPL-Q2 | Do auxiliaries and copulas count as pathway words? | They are required by clause pattern, not chosen by topic or relation. Proposed: a third table, "structural words", chosen by the clause pattern from `frames.py`. |
| SPL-Q3 | Are pronouns pathway words (referential links) or content words? | Proposed: pathway, chosen by Centering (`06_*`), since the choice is *pronoun vs full noun phrase*, a coherence decision. |

## 7. Tests

| ID | Checks |
|---|---|
| `SPL-01` | Every token of every calibration response is classified exactly once into content / pathway / structural by the function-in-plan rule; no token is unclassified. |
| `SPL-02` | The pathway mechanism's code path performs no read of `vec[19]` (static check or instrumented lookup counter = 0). |
| `SPL-03` | Disjointness (SPL-R1): no plan unit's `content_words` intersects its `connective` unless marked `quoted`. |
| `SPL-04` | Inventory file validates against its schema and has no duplicate (relation, connective, register) rows. |
| `SPL-05` | Swapping the topic (holding relation fixed) changes content words and leaves the connective set unchanged; swapping the relation (holding topic fixed) does the opposite. This is the behavioural test of independence. |

## 8. C-port notes

The connective inventory is a small static table (hundreds of entries); store it
as a sorted array keyed by `(relation_id, register_id, rotation_index)` so the
choice is O(1) with no allocation.
