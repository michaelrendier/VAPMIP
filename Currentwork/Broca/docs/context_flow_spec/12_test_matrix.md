# 12 — Test Matrix (generated)

Generated from `test_matrix.json` by `verify_spec.py --render`. Do not edit by hand.

Matrix version 0.1 · spec version 0.1 · 95 tests

| ID | Area | Title | Metric | Needs set | Threshold | Status | Spec |
|---|---|---|---|---|---|---|---|
| `SPL-01` | split | Every response token classified exactly once (content/pathway/structural) | exact | yes | — | UNIMPLEMENTED | 02_content_vs_pathway_words.md |
| `SPL-02` | split | Pathway code path performs no vec19 read | exact | no | — | UNIMPLEMENTED | 02_content_vs_pathway_words.md |
| `SPL-03` | split | Disjointness of content_words and connective per unit | exact | yes | — | UNIMPLEMENTED | 02_content_vs_pathway_words.md |
| `SPL-04` | split | Connective inventory validates; no duplicate (relation,register,connective) | exact | no | — | UNIMPLEMENTED | 02_content_vs_pathway_words.md |
| `SPL-05` | split | Swap topic -> content changes, connective fixed; swap relation -> inverse | exact | yes | — | UNIMPLEMENTED | 02_content_vs_pathway_words.md |
| `SM-01` | smith | Fold/unfold round trip on real ring data | MET-ERR | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-02` | smith | Ring independence for RP-A..RP-E (RP-E is the negative control) | MET-IND | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-03` | smith | Saturation of |Gamma| over the calibration set | MET-SAT | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-04` | smith | Topic separation ratio inter/intra subject | MET-SEP | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-05` | smith | Leave-one-out k-NN subject classification from Gamma position | MET-KNN | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-06` | smith | Cross-ratio invariance across anchor policies | MET-ERR | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-07` | smith | Cell purity | MET-PUR | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-08` | smith | Traversal determinism | exact | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-09` | smith | Stop rules honoured: <=N words, terminates, reason reported | exact | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-10` | smith | Topic-class coverage versus word budget at L1/L2/L3 | MET-COV | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-11` | smith | Locally-square check on real ring data | MET-ERR | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-12` | smith | Refusals for empty, OOV-only, single-token inputs | exact | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-13` | smith | Unit-pair and entry-pair are the same functions on different supports | exact | no | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `SM-14` | smith | RING-Gamma vs RING-R1 vs RING-R2 coverage comparison | MET-COV | yes | — | UNIMPLEMENTED | 03_smith_chart_topic_land.md |
| `DEC-01` | decay | Impulse response equals lambda^n v | MET-ERR | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-02` | decay | Superposition | MET-ERR | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-03` | decay | Half-life | MET-ERR | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-04` | decay | Level ordering of decay rates | exact | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-05` | decay | Boundary algebra for beta in {0,1/2,1} | MET-ERR | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-06` | decay | Normalised context independent of input count for constant input | MET-ERR | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-07` | decay | Feeding rule: higher level receives normalised lower level | exact | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-08` | decay | Underflow, long run, empty-state behaviour | exact | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-09` | decay | Bit-identical determinism across runs | exact | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-10` | decay | Probe-topic recall curve vs analytic curve | MET-ERR | yes | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `DEC-11` | decay | Latency of one update per level | MET-LAT | no | — | UNIMPLEMENTED | 04_carry_over_decay.md |
| `TT-01` | tile | TT-0 baseline on gold-boundary items | MET-WD | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-02` | tile | TT-2 relational similarity vs TT-0 | MET-WD | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-03` | tile | Synonym-swap robustness of overlap vs relational variants | MET-WD | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-04` | tile | No-boundary text yields zero or minimal boundaries | exact | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-05` | tile | Refusals for too-short, no-token, zero-variance inputs | exact | no | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-06` | tile | TT-4 multi-timescale mismatch vs TT-0/TT-2 | MET-PK | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-07` | tile | Cutoff-policy sweep | MET-BF1 | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-08` | tile | Streaming equals batch for TT-4 | exact | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-09` | tile | Sensitivity to very short and very long true segments | MET-WD | yes | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `TT-10` | tile | Latency per sentence for TT-2 and TT-4 | MET-LAT | no | — | UNIMPLEMENTED | 05_topic_shift_texttiling.md |
| `CEN-01` | center | Cf ranking from parse vs gold sentences | exact | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-02` | center | Cb determination on two-sentence gold pairs | exact | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-03` | center | Transition classification on constructed cases | exact | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-04` | center | Rule 1 pronoun detection | exact | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-05` | center | Descriptive transition distribution of reference responses | MET-DIST | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-06` | center | Generated vs reference transition distribution | MET-TV | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-07` | center | IT dereference regression vs g_last_noun | exact | no | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-08` | center | Entity identity variants E-1..E-4 on Cb accuracy | MET-ACC | yes | — | UNIMPLEMENTED | 06_centering.md |
| `CEN-09` | center | No pronoun with two compatible antecedents | exact | yes | — | UNIMPLEMENTED | 06_centering.md |
| `RST-01` | rst | Chosen connective in admissible set for (relation, register) | exact | no | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-02` | rst | Relation recovery with connective removed; default rate reported | MET-ACC | yes | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-03` | rst | Speech-act prior vs reference relation distribution | MET-TV | yes | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-04` | rst | Structure-only cells emit null | exact | no | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-05` | rst | Aggregation preserves Centering transition | exact | yes | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-06` | rst | No consecutive repeat of a connective when alternatives exist | exact | yes | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-07` | rst | Inventory file validates, unique keys | exact | no | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `RST-08` | rst | Register consistency of connectives | exact | yes | — | UNIMPLEMENTED | 07_rst_connectives.md |
| `GEN-01` | gen | End-to-end every prompt within budget, no crash | exact | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-02` | gen | Forced stage refusal returns word-bag fallback and names the stage | exact | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-03` | gen | All content words are store entries | exact | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-04` | gen | Per-unit shadow.check verdict prime rate | MET-RATE | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-05` | gen | Re-segmenting generated text recovers plan segments | MET-PK | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-06` | gen | Plan-first vs alternation variant | MET-COV | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-07` | gen | Two runs bit-identical | exact | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-08` | gen | Each failure code reachable by a constructed input | exact | no | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-09` | gen | Topic-class coverage against the reference response | MET-COV | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `GEN-10` | gen | Response register matches requested band | MET-RATE | yes | — | UNIMPLEMENTED | 08_generation_pipeline.md |
| `ATT-01` | attention | Weights are a probability distribution | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `ATT-02` | attention | Output invariant under reordering of context | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `ATT-03` | attention | Weight monotone in distance | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `ATT-04` | attention | Empirical cost vs window size | MET-LAT | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `ATT-05` | attention | Content-dependent vs fixed-decay vs plain-average weighting on coverage | MET-COV | yes | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `ATT-06` | attention | Limits beta->0 (average) and beta->inf (nearest) | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `POS-01` | position | Minimum pairwise distance of position codes, geometric vs prime bank | MET-ERR | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `POS-02` | position | Aliasing length of position codes | MET-ERR | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `POS-03` | position | Offset consistency of position codes | MET-ERR | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `BPE-01` | subword | Round trip decode(encode(w)) == w | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `BPE-02` | subword | Encoding determinism | exact | no | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `BPE-03` | subword | OOV yields in-store subword or explicit refusal | exact | yes | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `MASK-01` | mask | A unit's plan never depends on a later unit | exact | yes | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `MASK-02` | mask | Plan DAG acyclic on every prompt | exact | yes | — | UNIMPLEMENTED | 09_transformer_methods_taken.md |
| `CAL-01` | cal | Every set file validates against its schema | exact | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-02` | cal | Checksums match MANIFEST.sha256 | exact | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-03` | cal | Authored vs derived focus-entity agreement; disagreements listed | MET-ACC | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-04` | cal | No tuning log reads a test-split item | exact | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-05` | cal | Coverage of subject x type cells, relations, transitions | exact | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-06` | cal | Second-reference agreement (when available) | MET-ACC | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `CAL-07` | cal | Store coverage of content words per subject area | MET-RATE | yes | — | UNIMPLEMENTED | 10_calibration_set_spec.md |
| `PERF-01` | perf | Component latencies warm in-process | MET-LAT | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-02` | perf | Subprocess vs in-process for the same component | MET-LAT | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-03` | perf | Memory growth over 1e5 calls is flat | MET-MEM | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-04` | perf | Cold start | MET-LAT | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-05` | perf | Scaling with context window n in {10,50,200,1000} | MET-LAT | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-06` | perf | End-to-end build_text latency by response length | MET-LAT | yes | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |
| `PERF-07` | perf | Python vs C implementation of a ported component | MET-LAT | no | — | UNIMPLEMENTED | 11_metrics_and_benchmarks.md |

## Status counts

- UNIMPLEMENTED: 95
