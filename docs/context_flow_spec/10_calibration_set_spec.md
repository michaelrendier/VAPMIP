# 10 — The Standard Calibration Set (CAL)

**Purpose:** one fixed, versioned set of prompts and reference responses that
every model and every method in this spec is calibrated and debugged against.
Reference responses are produced by a transformer (Claude, model ID
`claude-sonnet-5-5`) because that is the available source of fluent reference
text — see §2 for what that does and does not license.

---

## 1. What this set is for

| Use | How the set serves it |
|---|---|
| Calibrate | Tune `[PARAM]`s (τ, β, cutoffs, budgets) on the **dev** split only. |
| Debug | Failing items localise a defect to a mechanism (each item is tagged with the mechanism it stresses). |
| Benchmark | Report metrics on the **test** split, which is never used for tuning. |
| Regress | Deterministic components must reproduce stored outputs bit-for-bit. |

## 2. The bias caveat (read before using any score)

Reference responses are one transformer's output. A metric that rewards matching
its **wording** measures similarity to that model's style, not quality. Therefore:

1. **Gold labels are structural**, authored at generation time, and independent of
   surface wording: topic boundaries, per-sentence focus entity, per-unit RST
   relation, subject area, speech act (§5).
2. **Comparisons against the reference text use wording-independent measures**:
   topic-class coverage (`MET-COV`), transition distribution (`MET-TV`), segment
   structure (`MET-PK`/`MET-WD`). Lexical overlap measures (BLEU, ROUGE, exact
   match) are **not** used as pass/fail criteria.
3. Every item records `authored_by`, so a later set from a different author or a
   human can be added as a second reference and the *agreement between references*
   measured (`CAL-06`).
4. The set cannot establish that a response is *true*. It establishes structure and
   coverage only. Item `notes` flag content the author is unsure of.

## 3. Subject areas

Eight general areas plus one in-domain tier. General areas are chosen to give
distinct vocabulary regions in WordNet while avoiding specialised jargon the store
may lack.

| ID | Area | Notes |
|---|---|---|
| S1 | Cooking and food | concrete nouns, process verbs |
| S2 | Weather and earth | physical processes, causes |
| S3 | History | events, agents, sequence |
| S4 | Biology | taxonomy (deep hypernym chains), processes |
| S5 | Machines and engineering | artefacts, parts (meronymy), how-things-work |
| S6 | Mathematics | abstract nouns, definitions |
| S7 | Language and linguistics | metalinguistic vocabulary |
| S8 | Music and the arts | mixed concrete/abstract |
| **S9** | In-domain (Ptolemy terms: sedenion, zero divisor, box-kite, Smith chart, etc.) | tests out-of-store behaviour and the author's own terminology; kept in a **separate tier** |

## 4. Prompt types

| ID | Type | Example shape | Stresses |
|---|---|---|---|
| P1 | Definition | "What is X?" | `define_X`, R-ELAB |
| P2 | Procedure | "How does X work / how do you X?" | `how`, R-SEQ |
| P3 | Reason | "Why does X happen?" | `why`, R-CAUS/R-RES |
| P4 | Who / where | "Who did X?" / "Where is X?" | `who_Xs`, `where` |
| P5 | Yes / no | "Is X a kind of Y?" | `yesno`, R-EVID |
| P6 | Comparison | "How is X different from Y?" | two topic points, R-CONT |
| P7 | Multi-topic | one prompt, two unrelated asks | segmentation |
| P8 | Single word | "bridge" | locator refusal / minimal context |
| P9 | Ambiguous word | "bank", "bat", "bass" | sense handling (Q6) |
| P10 | Out-of-vocabulary | a word absent from the store | `BPE-*`, refusal |
| P11 | Follow-up with pronoun | turn 2: "What does it eat?" | Centering, `IT` |
| P12 | Degenerate | empty, whitespace, punctuation only, very long | refusals (CN-12) |

## 5. Tiers and quantities

Targets for the first release, v1.0 of the set. Quantities are [PARAM] and may be
raised, never lowered, once frozen.

| Tier | Content | Items | Response length | Gold labels carried |
|---|---|---|---|---|
| **T1 core** | S1–S8 × P1–P6 | 48 | 1 paragraph (4–6 sentences) | subject, act, focus per sentence, relation per adjacent pair |
| **T2 stress** | P7–P10, P12 over S1–S8 (choose 2–3 areas each) | 24 | varies | subject(s), refusal expectation |
| **T3 segmentation** | long responses built to contain deliberate topic shifts | 16 | 3–5 paragraphs, 2–4 topics | **segment boundaries**, topic per segment, relation across boundary |
| **T4 multi-turn** | P11 conversations of 3–5 turns | 10 conversations | 1–3 sentences per turn | referent chain, focus per turn, transitions |
| **T5 in-domain** | S9 × P1–P6 | 12 | 1 paragraph | as T1; separate reporting |
| **T6 synonym-swap pairs** | T3 items re-written with synonym substitution | 8 pairs | as T3 | same boundaries as source (by construction) |

Total first release: **48 + 24 + 16 + 10 conversations + 12 + 8 pairs**.

## 6. Item schema

JSON Lines, one item per line, validated against
`schemas/calibration_item.schema.json`.

```json
{
  "id": "CAL-T1-S4-P1-001",
  "version": "1.0",
  "tier": "T1",
  "split": "dev",
  "subject_area": "S4",
  "prompt_type": "P1",
  "turns": [
    {"role": "user", "text": "What is photosynthesis?"}
  ],
  "response": {
    "text": "…full reference response…",
    "units": [
      {
        "unit_id": "u1",
        "level": "L1",
        "text": "…sentence…",
        "speech_act": "define_X",
        "focus_entity": "photosynthesis",
        "relation_to_prev": null,
        "connective": null,
        "topic_id": "t1"
      }
    ],
    "boundaries": [],
    "topics": [{"topic_id": "t1", "label": "photosynthesis"}]
  },
  "expect": {
    "refusal": null,
    "min_in_store_fraction": null
  },
  "authored_by": "claude-sonnet-5-5",
  "authored_date": "2026-10-12",
  "notes": ""
}
```

Field rules:

- `split` ∈ {`dev`, `test`}. Assign by a fixed hash of `id` (no manual choice): first
  hex digit of `sha256(id)` in `0–9a–b` ⇒ dev (≈ 69 %), else test (≈ 31 %).
- `units[*].level` is the level of the unit; T1 uses sentence units (L1).
- `boundaries` is a list of unit indices at which a new topic segment begins
  (empty for single-topic items).
- `relation_to_prev` ∈ the RST list of `07_*` §2 or null.
- `expect.refusal` is null for ordinary items and a refusal code
  (`EMPTY_INPUT`, `NO_IN_STORE_TOKENS`, `SINGLE_TOKEN_UNDEFINED`, …) for items whose
  correct behaviour is to refuse (P8, P10 where nothing is in store, P12).
- Multi-turn (T4) items have several `turns`, each user turn with its own response
  record.

## 7. Authoring protocol

1. **Generate in a clean session** with only this document and the schema in
   context (so the set is not shaped by the implementation under test).
2. **Write labels at the same time as text**, not afterwards: the author states, for
   each unit, focus entity, act and relation *as written*.
3. **Validate** with `verify_spec.py --calibration <dir>` (schema, split rule,
   unique ids, boundaries in range, relation names valid, no empty units).
4. **Second pass for label consistency** (`CAL-03`): re-derive focus entities with
   the deconstruction path (once built) and list disagreements for the author to
   adjudicate; adjudication is recorded, not silent.
5. **Author spot-check:** the project author reads a sample (≥ 10 %) and records
   corrections in `notes` with the date.
6. **Freeze:** compute `sha256` for every file; write `MANIFEST.sha256`; set the
   version.

## 8. Directory layout (to be created by the authoring session)

```
calibration/
    MANIFEST.sha256
    CHANGELOG.md
    T1_core.jsonl
    T2_stress.jsonl
    T3_segmentation.jsonl
    T4_multiturn.jsonl
    T5_indomain.jsonl
    T6_synonym_pairs.jsonl
    gold_transitions.json      # constructed Centering cases (CEN-03)
    gold_connectives.json      # relation/connective pairs (RST-01/02)
```

## 9. Freezing and hygiene

- A frozen item is **never edited in place.** A correction creates a new version of
  the item (`version` bumped, old line kept with `"superseded_by"`), and the set
  version increments with a changelog entry.
- The **test split is never read by tuning code.** Every tuning run logs the split
  it read; `CAL-04` fails if a tuning log references a test item.
- A method's score is only comparable to another's if both used the same set
  version, split, and parameters. Result logs record all three.

## 10. Tests of the set itself

| ID | Checks |
|---|---|
| `CAL-01` | Every file validates against its schema |
| `CAL-02` | Checksums match `MANIFEST.sha256` |
| `CAL-03` | Label consistency: derived focus entities agree with authored ones above a stated threshold; disagreements listed |
| `CAL-04` | Split hygiene: no tuning log reads a `test` item |
| `CAL-05` | Coverage: every (subject area × prompt type) cell of T1 is populated; every RST relation appears ≥ 3 times across T1/T3; every Centering transition appears ≥ 3 times across T4/gold |
| `CAL-06` | Second-reference agreement (when a second author exists): agreement of boundaries and focus entities between references |
| `CAL-07` | Store coverage report: fraction of content words per subject area that are in `monad3_c.bin` (so low scores can be attributed to vocabulary gaps and not to method failure) |

## 11. Why a coverage report matters

Low scores on an item can come from three sources: the **method** is wrong, the
**vocabulary store lacks the words**, or the **label is wrong**. `CAL-07` separates
the second from the first, `CAL-03` the third. Every failure analysis starts by
ruling these out.
