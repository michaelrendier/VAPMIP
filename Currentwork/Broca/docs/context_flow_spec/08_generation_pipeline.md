# 08 — The Generation Pipeline (M-PIPE)

**Purpose:** fix the *order of decisions* in constructing a text object larger than
a sentence, and map each decision onto an artifact that exists or must be built.
This document is the integration point: it is where the other methods plug in.

---

## 1. The reference architecture (Reiter & Dale, 2000) [LIT]

*Building Natural Language Generation Systems* divides generation into six tasks in
three stages:

| Stage | Task | Question it answers |
|---|---|---|
| **Document planner** | Content determination | What information goes in? |
| | Document structuring | In what order, with what relations? |
| **Microplanner** | Lexicalisation | Which words express each concept? |
| | Referring-expression generation | Name it, describe it, or pronoun? |
| | Aggregation | Which simple units merge into one sentence? |
| **Surface realiser** | Linguistic realisation | Grammar, agreement, inflection |
| | Structure realisation | Paragraphs, layout, punctuation |

## 2. Mapping onto this project

| Task | Method in this spec | Existing artifact [CODE] | Status |
|---|---|---|---|
| Content determination | Smith-chart locator + ring traversal (`03_*`) | none; `console_speak` takes the 16-shell firing words instead | **to build** |
| Document structuring | RST relation selection (`07_*`) + topic segmentation (`05_*`) | none | **to build** |
| Lexicalisation | Vocabulary mechanism (`02_*` §3.1) | `generate.py` `_rank`, `_resonant_pick`, `fill_phase`, `_band_ok` | **exists** |
| Referring expressions | Centering (`06_*`) | `zork.h` `IT → last noun` (single slot) | **partial** |
| Aggregation | `07_*` §6 | none | **to build** |
| Linguistic realisation | clause pattern + inflection | `generate.py` `structure_phase`, `linearize`, `_third_person`; `shadow.check` | **exists** |
| Structure realisation | paragraphing | none; `/paragraph` mode in the Chat Tab (`semantic_paragraph.py`) is the nearest [CODE: `ptol.c` comments] | **partial** |

The design observation: the *microplanner's lexicalisation and the realiser already
exist*. What is missing is everything **above** the sentence — which is exactly the
scope of this spec.

## 3. Pipeline definition

```
build_text(prompt_reading, context_state, config) -> TextObject
    1. PLAN
       a. locate:  P = locator(prompt_reading)                      # 03
       b. segment: topic segments of the input, if multi-topic       # 05
       c. for each segment s:
              words_s = traverse(P_s, ring, budget, stop_rules)      # 03
              units_s = split words_s into units of ≤ N_content words (by POS slots)
       d. structure: assign relation_to_prev to each unit            # 07 §4
       e. focus:    assign focus_entity per unit, intended transition # 06 §4
    2. MICROPLAN
       a. lexicalise:   ParseSpec per unit (verb, topic_lemmas, act) # existing
       b. referring:    pronoun or full NP per mention               # 06
       c. aggregate:    merge eligible adjacent units                # 07 §6
       d. connectives:  choose per relation, register, rotation      # 07 §3
    3. REALISE
       a. build_response(ParseSpec, depth) per unit                  # existing
       b. linearize + join with connectives + paragraphing
    4. VERIFY (cheap, deterministic)
       a. every content word in store                                 # GEN-03
       b. each sentence passes shadow.check ('prime')                 # GEN-04
       c. realised Centering transitions == intended                  # CEN-06
       d. word count ≤ budget                                         # SM-09
    5. UPDATE STATE: feed the response's units into the decay ladder  # 04
```

### 3.1 Guarantees

**G-PIPE-1 (bounded).** Output content-word count ≤ the configured budget.
**G-PIPE-2 (in-store).** Every content word is a store entry (CN-03).
**G-PIPE-3 (fallback).** If any stage returns a refusal, the pipeline returns the
*previous guaranteed output* — the word bag of `console_speak` — and reports which
stage refused (`GEN-02`). No stage may substitute a guess for a refusal.
**G-PIPE-4 (determinism).** Same prompt, same initial state, same config ⇒
identical text (CN-31). Rotation uses the step counter, never a random source.
**G-PIPE-5 (verification is not optional).** Stage 4 failing is a reported defect
of the plan, not silently repaired.

## 4. Interface to the existing creator

The creator's input is `ParseSpec(speech_act, verb, topic_lemmas)` plus a depth
band (`band_of(|Γ|)`). A plan unit maps to one `ParseSpec`:

| Plan unit field | ParseSpec / call |
|---|---|
| `speech_act` | `speech_act` |
| `content_words` (the VERB among them) | `verb`; remaining → `topic_lemmas` |
| `register` | depth band argument (`narrative`/`surface`/`technical`/`thesis`) |

When no content word is a known VerbNet lemma the existing bridge falls back to a
per-act default verb (`_DEFAULT_VERB`). The spec keeps that behaviour and makes it
visible: `verb_source ∈ {from_words, default_for_act}` in the result log.

## 5. Alternation variant (open question Q3)

`M-PIPE-ALT`: instead of planning the whole text first, alternate
plan-one-unit / realise-one-unit, feeding each realised unit back through
deconstruction (`reduce`) so the next unit is planned from the *actual* surface
state. This is closer to the Mind's-Eye / Paper's-Hands loop and matches the
observation in `PtolemyDesktop/README.md` that the kernel re-hears what it says
(the Wernicke feedback path). It costs more per unit and gives the planner ground
truth about what was said. Tested against the plan-first pipeline in `GEN-06`; the
choice between them is deferred to the data.

## 6. Failure taxonomy (so failures are classified, not just counted)

| Code | Stage | Meaning |
|---|---|---|
| F-LOC | plan | locator refused (empty / no in-store tokens / undefined ring) |
| F-RING | plan | traversal returned no candidates (S-EMPTY at step 0) |
| F-REL | plan | relation selector hit the default for > threshold of units |
| F-VERB | microplan | no verb from words; default-for-act used |
| F-FRAME | realise | `shadow.check` = `composite` (verb does not license the pattern) |
| F-BUDGET | verify | over budget |
| F-FOCUS | verify | realised transition ≠ intended |
| F-BRIDGE | realise | creator subprocess failed; word-bag fallback used |

Each result record in a benchmark log carries a list of failure codes.

## 7. Tests

| ID | Checks | Metric |
|---|---|---|
| `GEN-01` | End-to-end: every calibration prompt → text within budget, no crash | exact |
| `GEN-02` | Fallback honoured: force each stage to refuse; the word-bag output is returned and the failing stage reported | exact |
| `GEN-03` | All content words are store entries | exact |
| `GEN-04` | Sentence-level `shadow.check` verdict is `prime` for each unit (rate reported, not required to be 100%) | MET-RATE |
| `GEN-05` | Re-segmenting the generated text recovers the plan's segments | MET-PK, MET-WD |
| `GEN-06` | Plan-first vs alternation variant | MET-COV, MET-TV, MET-LAT |
| `GEN-07` | Determinism: two runs bit-identical | exact |
| `GEN-08` | Failure codes: each F-code is reachable by a constructed input (no dead codes) | exact |
| `GEN-09` | Topic-class coverage of the response against the reference (the wording-independent comparison) | MET-COV |
| `GEN-10` | Register: response register band matches the requested band | MET-RATE |

## 8. C-port notes

Plan and microplan operate on small fixed arrays (≤ 32 units, ≤ 16 content words
per unit). Verification is a single pass. The `popen` boundary to Python is the
current obstacle to millisecond latency (see `11_*` §6); the port order that
removes it is: (1) locator and traversal, (2) decay ladder, (3) connective table,
(4) Centering, (5) the sentence creator itself.
