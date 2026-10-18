# ASSESSMENT: monad_wordnet_v4_20260519.bin (2026-10-18)

Companion to `monad_wordnet_v4_20260519.POISON.md`. Machine-readable: `monad_wordnet_v4_20260519.assessment.json`. Reproduce: `python3 tools/assess_bin.py dirty/monad_wordnet_v4_20260519.bin out.json` (needs NLTK WordNet; use `PtolemyDesktop/.venv`).

## 1. Identity of the file
| field | value |
|---|---|
| sha256 | `66f70c70dcd8d860fa4af01833cf5c6e4c376194c510b5be156fe0c6064faf31` |
| size | 110,040,527 bytes, all consumed by the reader (`tools/ptol_bin.py`, layout of `state.c: state_load`) |
| format | PTOL v4: magic, version, N, vocab_size, A_size, word_count, threshold f64, affect f32; β f64[N]; age i32[N]; vocab (idx u32, wlen u16, E f64, home u8, gen u8, prose_seen u8, word); A (i u32, j u32, w f64) |
| N | 25,000 slots (zeros) |
| vocabulary | 24,485 occupied slots |
| A-edges | 6,825,748 (edge density 2.18 %) |
| word_count | 121,914,388 |
| threshold, affect | 3.776, −1.0 |
| corpus (per `checkpoints/clean/PRIMER_from_dot_ptolemy.md`) | WordNet 3.1 + Gutenberg English corpus, `teach_english.sh` overnight run, "post-vowelfix", engine v1.218 |

## 2. Field
| measure | value | project band |
|---|---|---|
| occupied zeros | 25,000 of 25,000 | |
| entropy | 12.9558 / 14.6096 bits = 88.68 % | 85–92 % natural |
| Gini | 0.7564 | 0.60–0.80 natural |
| β at the cap (7.552) | 1,826 of 24,485 occupied slots (7.5 %) | |
| strata | home = gen = 1 (ℂ, text) for all 24,485 | |
| prose_seen | 3: 13,594 · 1: 10,538 · 2: 158 · 0: 195 | |

## 3. Vocabulary
* displayed-word lengths: 2: 200 · 3: 2,518 · 4: 6,875 · 5: 12,545 · 6: 2,330 · 7: 17 · 8+: 0 (word length ≥ 8 addresses to slot 0).
* scripts: ASCII 24,485; non-ASCII 0.
* `eval_checkpoint` classes: 1,233 polluted (5.04 %): consonant-only 993, consonant-cluster-3 654, no-vowel 344, hex-string 268.
* sanitiser: quarantined 1,008 (4.12 %); admitted tiers A 4,563 (in WordNet), B 18,409 (candidate, no WordNet synset), C 450 (proper noun), F 55 (function word).
* the whole of this store is a table of *slot winners*: see `POISON.md`, "Structure that makes the vocabulary unrepresentative".

## 4. The words of the screenshot reply and prompt, as the store holds them
| word | slot | E | β | displayed by its slot |
|---|---|---|---|---|
| holcus | 24639 | 0.5625 | 7.552 | holcus |
| same | 1859 | 0.2699 | 7.552 | same |
| stuff | 18482 | 0.4834 | 7.552 | stuff |
| seemy | 0 | 0.2460 | 7.552 | seemy |
| what | 16194 | 0.4540 | 7.552 | what |
| your | 18893 | 0.4887 | 7.552 | your |
| is | 1894 | 0.2703 | — | nanti |
| name | 15471 | 0.4447 | — | emite |
| tree | 3109 | 0.2859 | — | typhon |
| water | 9361 | 0.3663 | — | defrg |
| ptolemy | 10156 | 0.3765 | — | sift |
| philadelphos | 0 | 0.2460 | — | seemy |

`holcus` and the word `in` both address to slot 24639; `holcus` has the higher E by 1.18·10⁻⁶ and is displayed. That slot has 18,268 A-neighbours (5th best connected of 25,000; median 150).

## 5. Verdict
**DIRTY, PASS.** Verdict rule (`tools/eval_checkpoint.py`): pollution 5.04 % < 20 % (PASS), ≥ 1 % (not CONVERGED); entropy and Gini in their natural bands. No multilingual content. Reproduced to the byte by the source at commit `eb28ce8` (build in `build/`, port in `tools/monad_py.py`; `tools/verify_against_c.py` 8/8 identical replies; `tools/verify_learn_against_c.py` exact).
