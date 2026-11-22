# 06 — Centering Theory (M-CENTER)

**Purpose:** track what a passage is *about* from sentence to sentence, choose the
subject of the next sentence, and decide when to use a pronoun. Centering is a
model of **local coherence**; it has no learned parameters.

---

## 1. The theory (Grosz, Joshi & Weinstein, 1983/1995) [LIT]

For each utterance `Uₙ`:

- **Forward-looking centers** `Cf(Uₙ)`: the entities mentioned in `Uₙ`, **ranked**
  by grammatical role (commonly subject > object > other).
- **Preferred center** `Cp(Uₙ)`: the top-ranked element of `Cf(Uₙ)`.
- **Backward-looking center** `Cb(Uₙ)`: the highest-ranked element of `Cf(Uₙ₋₁)`
  that is realised in `Uₙ`. (Undefined for the first utterance.)

**Transitions** between `Uₙ₋₁` and `Uₙ`:

|  | `Cb(Uₙ) = Cp(Uₙ)` | `Cb(Uₙ) ≠ Cp(Uₙ)` |
|---|---|---|
| `Cb(Uₙ) = Cb(Uₙ₋₁)` (or Cb(Uₙ₋₁) undefined) | **CONTINUE** | **RETAIN** |
| `Cb(Uₙ) ≠ Cb(Uₙ₋₁)` | **SMOOTH-SHIFT** | **ROUGH-SHIFT** |

**Rules.**
- *Rule 1:* if any element of `Cf(Uₙ)` is realised as a pronoun, `Cb(Uₙ)` is.
- *Rule 2 (preference):* CONTINUE > RETAIN > SMOOTH-SHIFT > ROUGH-SHIFT.

Interpretation: coherent text mostly continues or smoothly shifts focus; rough
shifts are costly for the reader.

## 2. Mapping onto what exists [CODE]

| Centering notion | Existing source |
|---|---|
| Entities and their roles | `engine/grammar/shadow.py` `spoca` slots: `S`, `P`, `O_d`, `O_i`, `C_s`, `C_o`, `A` (from UD deprels `SUBJ`, `DOBJ`, `IOBJ`, `OBL`, `XC`) |
| Role ranking | Define: `S > O_d > O_i > C > A` [PARAM: `role_rank`] |
| Parser-level entities | `PtolC/zork.h`: `noun` (first NP), `noun2` (second) |
| Pronoun resolution | `zork.h`: `IT → last-mentioned noun`; `g_last_noun` (single slot) |
| Pronoun realisation | not yet in the sentence creator |

**Observation [CODE]:** the existing `IT` mechanism is exactly a one-element
`Cb`. Centering generalises it to a ranked list and adds the transition logic.

## 3. Entity identity

Centering needs to know when two mentions are the same entity. In this system:

- **Same lemma** ⇒ same entity (baseline `E-1`).
- **Same synset** ⇒ same entity (`E-2`; catches synonyms).
- **Same hypernym within depth h** ⇒ same entity-class (`E-3`; too coarse for
  Cb, listed for completeness).
- **Pronoun ⇒ entity** by the most recent compatible `Cb`/`Cf` element
  (number and animacy from the lemma's sense; `E-4`).

The identity function is a [PARAM `entity_id`] recorded in each result log.

## 4. Construction use

At plan time, for each unit after the first:

1. **Choose the unit's focus** `focus_entity`:
   prefer continuing `Cb` (CONTINUE); else keep a previously ranked `Cf` entity
   (RETAIN or SMOOTH-SHIFT); otherwise start a new one (ROUGH-SHIFT) and mark the
   relation so a connective can announce it (`07_*`).
2. **Place the focus in the subject slot** when the clause pattern allows, so that
   `Cb = Cp` (CONTINUE rather than RETAIN).
3. **Pronominalise** the focus when it equals `Cb` and no other `Cf` element of
   compatible number/animacy competes (avoids ambiguity). This implements
   Rule 1.

**Guarantee (G-CEN-1).** The planner returns, for every unit, the transition type
it intends; the *realised* transition recomputed from the surface text by the
deconstruction path must equal the intended one (self-consistency; test
`CEN-03`/`CEN-06`).

## 5. Deconstruction use

Run `shadow.reduce` per sentence, collect `spoca`, rank entities, compute `Cb` and
the transition. Output a transition string for the passage, e.g.
`— CONT CONT SMOOTH CONT ROUGH`. Reference responses in the calibration set carry
gold transitions (`10_*` §5).

## 6. Measures

| Measure | Definition |
|---|---|
| Transition distribution | Fractions of CONTINUE / RETAIN / SMOOTH / ROUGH over a response |
| Coherence score (simple) | `(#CONT + 0.5·#RETAIN + 0.25·#SMOOTH) / #transitions` [PARAM weights] |
| Distribution distance | Total-variation distance between generated and reference distributions: `½ Σ |pᵢ − qᵢ|` |
| Rule-1 violations | Count of pronoun uses where `Cb` is not a pronoun (or vice versa) |

## 7. Tests

| ID | Checks | Metric |
|---|---|---|
| `CEN-01` | `Cf` ranking from parse matches hand-built gold on a set of 30 sentences | exact |
| `CEN-02` | `Cb` determination on two-sentence gold pairs | exact |
| `CEN-03` | Transition classification on a table of 20 constructed cases covering all four transitions and the undefined-first case | exact |
| `CEN-04` | Rule 1 detection on constructed pronoun cases | exact |
| `CEN-05` | Descriptive: transition distribution of the reference responses by subject area and response length | MET-DIST |
| `CEN-06` | Generated vs reference transition distribution | MET-TV |
| `CEN-07` | `IT` dereference equals `g_last_noun` behaviour on single-noun inputs (regression: the generalisation must not break the existing parser) | exact |
| `CEN-08` | Entity-identity variants E-1..E-4 compared on `CEN-02` | accuracy |
| `CEN-09` | Pronominalisation does not create ambiguity: no pronoun with two compatible antecedents in `Cf` | exact |

## 8. Known weak points [LIT/HYP]

- The role ranking (subject > object) is a language-specific heuristic; passives
  and fronted constructions can invert it. The parser's UD relations include
  `nsubj:pass`; the spec treats it as `S` for ranking unless `CEN-08` shows
  otherwise.
- Real prose has many non-pronominal re-mentions; the theory underspecifies
  definite descriptions. E-1 vs E-2 tests how much that matters here.
- Centering is *local*: it says nothing about topic across paragraphs. That is the
  job of `05_*` and the decayed state (`04_*`).

## 9. C-port notes

`Cf` is a short array (≤ 8 entities) of lemma indices; `Cb` is one index; the
transition is a 2-bit code. Entity identity via the `WordRec` index is O(1).
