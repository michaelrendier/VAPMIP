# Context Flow — Specification (index)

**Spec version:** 0.1 · **Written:** 2026-10-12 · **Status:** DESIGN — nothing in this
directory is implemented yet. Every test in `test_matrix.json` starts at
`UNIMPLEMENTED`.

This directory is the single specification for **Context Flow**: how the
Ptolemy Monad carries topic, subject matter and "ideas" from a prompt, through
the vocabulary-ingested knowledge it already holds, into a full response —
without learned weights, without a GPU, without the internet, and inside a
millisecond-scale latency budget on a laptop.

It is written so that every claim can later be **tested and benchmarked**. Each
method has an ID, each test has an ID, each metric has an ID, and the machine-
readable `test_matrix.json` ties them together. `verify_spec.py` checks that the
documents and the matrix agree with each other.

---

## 0. Evidence labels used throughout

Every statement in this spec carries (explicitly or by section header) one of:

| Label | Meaning |
|---|---|
| **[CODE]** | Read from a file in this repository on 2026-10-12. The file and identifier are named. |
| **[LIT]** | Published method, described from the author's knowledge of the literature. Not re-verified here. Citations are by author/year so they can be checked. |
| **[HYP]** | A design hypothesis. The test that would confirm or refute it is named. |
| **[UNMEASURED]** | A quantity (latency, memory, accuracy) that has not been measured. No number is claimed. |
| **[PARAM]** | A free parameter. The default is a starting value, not a result. |

If a sentence has no label and is not obviously definitional, treat it as [HYP].

## 1. Hard constraints (these bound every design choice)

1. **No transformer weights.** No learned parameter tensors, no gradient
   descent, no pre-trained model in the response path. Transformer *methodology*
   (attention as weighted lookup, positional encoding, subword merges, residual
   addition, masking) may be taken — see `09_transformer_methods_taken.md`.
2. **Laptop, offline, CPU.** Reference machine in
   `VAPMIP/docs/SYSTEM_SPECS_ThinkPad_X1_Carbon_6th.md`. A GPU is planned but
   must not be *necessary*. [See `11_metrics_and_benchmarks.md` §7 for a hardware
   discrepancy between two repo documents that the benchmark protocol resolves.]
3. **Millisecond response.** Target is per-component and end-to-end latency in
   milliseconds. The target value itself is a [PARAM]; see `PERF-*` tests.
4. **Guarantee-based.** Where a method can give a hard guarantee (exact decay,
   deterministic ring traversal, bounded word budget) the spec states it and the
   test checks it. Where it cannot, the spec names the explicit fallback and the
   test checks that the fallback fires — never a confident approximation. (Same
   rule `ptolc_bridge.py` already follows: print nothing, exit nonzero, keep the
   word-bag.)
5. **Vocabulary-ingested knowledge only (for now).** Knowledge ingested later
   through the hyperindexer is out of scope; the interfaces leave a named slot
   for it (`01_context_needs.md`, CN-90s) but nothing here depends on it.
6. **Two mechanisms, not one.** Content words (NOUN, VERB, ADVERB) come from
   context encoded in the vocabulary. Connecting ("pathway") words come from a
   separate mechanism selected by relation between units. See
   `02_content_vs_pathway_words.md`.

## 2. Document map

| File | Contents | Method IDs | Test prefix |
|---|---|---|---|
| `01_context_needs.md` | What context must exist, at which granularity, in which interface | CN-* | — |
| `02_content_vs_pathway_words.md` | The two-mechanism split; inventories; boundary between them | M-SPLIT | SPL-* |
| `03_smith_chart_topic_land.md` | Two-relationship Smith-chart locator; ring traversal; stopping rules | M-SMITH | SM-* |
| `04_carry_over_decay.md` | Multi-granularity leaky integrators; exactness guarantees | M-DECAY | DEC-* |
| `05_topic_shift_texttiling.md` | Splitting text by topic shift; 19D variant; multi-timescale detector | M-TILE | TT-* |
| `06_centering.md` | Centering Theory: focus tracking, transitions, pronominalisation | M-CENTER | CEN-* |
| `07_rst_connectives.md` | Rhetorical Structure; relation → connective selection | M-RST | RST-* |
| `08_generation_pipeline.md` | Reiter & Dale pipeline mapped onto existing artifacts | M-PIPE | GEN-* |
| `09_transformer_methods_taken.md` | Methodology borrowed from transformers, weights excluded | M-ATT, M-POS, M-BPE, M-RES, M-MASK | ATT-*, POS-*, BPE-* |
| `10_calibration_set_spec.md` | Standard prompt/response set: schema, tiers, labels, freezing | CAL | CAL-* |
| `11_metrics_and_benchmarks.md` | Metric definitions, latency protocol, result-log format | MET-* | PERF-* |
| `test_matrix.json` | Machine-readable index of every test | — | all |
| `12_test_matrix.md` | Human-readable rendering of `test_matrix.json` (generated) | — | all |
| `schemas/*.json` | JSON Schemas for calibration items and result logs | — | — |
| `verify_spec.py` | Consistency check for this directory | — | — |

## 3. How to use this spec

**To implement a method:** read its file top to bottom. The *Interface* section
gives the function signatures to implement; the *Guarantees* section says what
must be exactly true; the *Tests* section lists the IDs that must pass.

**To run a benchmark:** pick tests from `test_matrix.json` by `area` or `tier`,
run them against the calibration set (`10_calibration_set_spec.md`), and write a
result log in the format of `schemas/result_log.schema.json`. Never edit a
previous log; add a new one.

**To add a method:** add its document, give it an `M-` ID, add its tests to
`test_matrix.json`, add the test prefix to the table above, then run
`python3 verify_spec.py`. The verifier fails if a test cites a missing document,
a missing metric, or a duplicate ID.

**To change the spec:** bump the version in this file, record the change in §6,
and never silently edit a frozen calibration item (see `10_*` §9).

## 4. Order of work (recommended, not binding)

1. `CAL` — the calibration set has to exist before anything can be calibrated.
2. `DEC` — decay is exact arithmetic; it can be fully verified with no data.
3. `SM-02` — the ring-independence test decides whether the Smith-chart locator
   is viable *at all* (the J_red/J_blue pair in `modules/scale` turned out to be
   one degree of freedom, not two). If every candidate pair is degenerate, the
   locator needs a different pair before `03_*` goes any further.
4. `TT`, `CEN`, `RST` — each is independently testable against gold labels.
5. `GEN` — end-to-end, once the pieces exist.
6. `PERF` — measured throughout, reported at the end.

## 5. Design-to-C policy

Per standing practice: **design and test in python3; move to `ptol.c` only after
the design is accomplished.** Each method document therefore ends with a
*C-port notes* section listing what the C side would need (data layout, no-alloc
paths) — as notes only. Nothing here changes `ptol.c`.

## 6. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-12 | First complete draft. Written from a read of `ptol.c`, `modules/scale`, `modules/prime_gauge_field`, `engine/grammar/*`, `wordnet_boxkite.py`, `PtolC/zork.h`. |

## 7. Provenance

The design questions behind this spec came from a working session on
2026-10-12 ("Context Flow" in the scaled-boxkite context monad model). The four
older methods (generation pipeline, Centering, RST, TextTiling) were proposed as
non-transformer, non-learned methods for "larger text object construction". The
Smith-chart locator is the project author's own idea: compare two relationships
Smith-chart style to place a prompt in "topic land", then traverse a ring to
scale context up instead of using every appropriate word.
