# 17 · v3.0 — the word list and the two Universal Native Space bins

**Job.** Record the v3.0 word list, the two UNS bins built from it, why Chinese is the baseline, and the first side-by-side survey of M3 and M4. Flat mechanisms (M1, M2) are not used. Nothing is assigned or aligned yet; the assignment of English words to Chinese idea slots is the next discussion.

## Why Chinese is the baseline (Cody's stated rationale, 2026-10-21)
A) it is **ideographic**: a character is an idea, not a spelling (an ideographic system keeps *couch* and *chair* from being two versions of one idea); B) it is **alive and spoken well today** (not dead, not recently dead, not dying like Navajo and Comanche); C) it has existed for **over five millennia**; D) it is believed to be **one of the most efficient partitionings of idea space** in language form. It is taken as the bare minimum of ideas space. Hieroglyphs would have been chosen were the language not dead; Demotic put one character at the start of a word to carry its tone, which became the invisible tone / tense / conjugation marks the orbweaver will carry ([10](10_design_notes.md)). A, B, C are Cody's statements; D is his assumption and is **not measured here**.

## The word list (`SemPriCon/calibration/calibration_v3_en_zh.tsv`, read-only, sha256 `d130d2b43e2fe0fbf65dbaad193bf6ed8451c3cfe49ed93b2169e96b716ed1f1`)
Built by `tools/calibration_v3.py` (a modified copy of `calibration_v1.py`; v1 is frozen and untouched) from `tools/en_word_freq.py`, `tools/zh_char_freq.py`, WordNet, CC-CEDICT and the Han alphabet. The calibration protocol of [06](06_the_calibration_set.md): 512 concepts × 2 (S simple, L deeper), direct English and Chinese analogues, every surface word once, ≤ 15 % per lexicographer class, Traditional characters. **Change from v1:** every Chinese word is a **single character** in the engine's Han alphabet (M2/M4 map single characters only). The Open Multilingual WordNet has only 135 synsets with two single-character Mandarin lemmas, so Chinese candidates come from CC-CEDICT: S's character lists the English S word as a whole gloss (among its first four definitions), L is any other single character glossed by a lemma of the synset. Result: 1 024 rows, nouns 586, verbs 408, adjectives 30; 1 024 distinct English words and 1 024 distinct characters. **Known noise** (kept, as in v1): WordNet and CEDICT senses are imperfect and many characters are polysemous, so some pairs are near rather than direct (*beat* 勝, *mountain* 陵). Corrections go to a new version.

## The bins (`SemPriCon/clean/`, state v6, read-only, `tools/v3_build.py`)
`test_english_v3.0.bin` (sha256 `5fecfabee487cc793812f09a9390cc4e912f033d75e983158d3c13d5d20a2888`) from M3 (`uns_mech.en_uns`, the eb28ce8 float seed); `test_chinese_v3.0.bin` (sha256 `f2de1e456fff18c86d8ac6fe6e3acb00da3360cef677fc5a0f073952547cc3bd`) from M4 (`uns_mech.zh_uns`). Each is ground state → one pass over its half of the list → frozen, using the monad's own learning step (β ← β + E²·α·|sin γ|·π/2, label = highest-E arrival). Deliberate differences from the engine's ingest: the address is the UNS mechanism; γ is the **exact zero** of the slot for both languages; the engine's token filter is **not** applied (it would have rejected 8 English words: cry, fly, pharynx, scratch, strength, stretch, stylish, yr); a list of single words has no sentences, so no A edges. Checked: every stored slot and E equals the address recomputed from the mechanism; `ptol_bin.write_state` was verified byte-identical against two C-written v6 files. `data/v3_map.tsv` holds every row's slot, γ, E, turn, radius and state for both bins. PDF: `SpaceClaude/SemPriCon/SemPriCon_v3.0_word_list_map.pdf`.

## M3 and M4 side by side (on trial)
| | English, M3 | Chinese, M4 |
|---|---|---|
| input | the spelling | one character, by dictionary position |
| turn | frac(v/φ), v = base-95 Horner count | (i + ½)/97 518, i = dictionary index (radical, strokes, key, code point) |
| θ, φ, slot | π/2, 2π·turn, ⌊25 000·turn⌋ | the same |
| r | E/d*_taut, E from the same turn: radius = azimuth (one coordinate) | E/d*_taut, E from the key component: independent (two coordinates) |
| neighbours | no meaning | shared radical / structure |
| precision | float, 53 bits | exact integers |

## First survey (1 024 rows; computed, not tuned)
| | English bin | Chinese bin |
|---|---|---|
| occupied slots | 732 | 996 |
| most words in one slot | 210 | 3 |
| outranked words (label belongs to a higher E) | 292 | 28 |
| words at slot 0 | 210 (208 words have 8 or more letters) | 1 |
| S/L of a concept: median ring distance (turns), against unrelated pairs | 0.236 vs 0.228 | 0.182 vs 0.266 |
| S/L within 0.01 turn, against unrelated pairs (of 512) | 39 vs 27 | 67 vs 20 |

English against Chinese on the same row: same slot in **0** of 1 024 rows; median ring distance 0.241 against 0.256 for unrelated rows (uniform expectation of the mean 0.250). The mechanisms place a concept independently. English **piles 210 words onto slot 0**: the M1 defect (float seed exhausted at 8 letters) carries through M3 on purpose, as the record of what the original mechanism does. A shared Chinese slot is a radical; a shared English slot is a coincidence of spelling.

Limits: one list, one run; S/L distances show weak structure for Chinese only; "match" is not yet defined; no assignment has been made. Reproduce: `tools/calibration_v3.py`, `tools/v3_build.py`, `tools/v3_pdf.py <out.pdf>`.

## The assignment experiment: `test_chinese_english_v3.0.bin` (2026-10-21)
Pass 1 puts the 1 024 Chinese characters at their M4 addresses. Pass 2 **assigns each English word to the slot of its Chinese partner** (same row of the list): the slot, the azimuth, the idea, is taken from the Chinese; the English word keeps its own M3 energy E, its own radius on the equator. Not a hash of English onto primes. Built by `tools/v3_build.py` (`build_assigned`); sha256 in `clean/MANIFEST.tsv`. Result: 996 occupied slots, 2 048 words, **1 052 outranked** (the engine keeps one label per slot, the highest E): **611 slots are labelled by the Chinese character, 385 by the English word**, so 639 of the 1 024 English words are not reachable by a lookup. Choice not yet tested: the English word taking the partner's E instead of its own (then the first arrival, the Chinese character, would keep every label).

**Speaking** (`tools/v3_speak.py`: the Unicode port of the speaking mechanism with the UNS mechanisms as the address of unheard words; reference = the compiled eb28ce8 binary on the May-2026 store, which answers "what is your name" with `holcus​same​stuff​seemy`). All three v3.0 bins answer **nothing** (empty reply), with the engine's own zeros and with the exact zeros:
- *what*, *is*, *your* are not in any bin; *name* is known to the English bin (slot 15 471) and the assigned bin (slot 1 890, the slot of 名).
- English bin: *name*'s zero has cos(γ/2 − π/2) < 0, so the walk's phase filter rejects it.
- Assigned bin: *name* passes the phase filter but its β is 1.9·10⁻⁴ (one learning hit), so its signal J = β·E² = 3.8·10⁻⁵ is under the floor `GAP` = 7.1·10⁻⁴; nothing speaks. The May-2026 store has millions of hits, so its β is large.
- There are no A edges (a list has no sentences) and the spectral spread is ±3 slots, so there is nothing to walk to except heard words: a bin built from a word list can only echo.
- Echoes: "name family food work" → English bin `food`; "valley mountain family name" → English bin `watchful​valley` (*mountain*, eight letters, sits on slot 0 beside *watchful*); Chinese characters as the prompt (名 家 食 事) → Chinese bin and assigned bin `事 家`.

**Assessments** (`clean/assessment/`, three bins): English 732 slots, 100 % prose words, 0.41 % pollution (eval_checkpoint). Chinese 996 slots: prose 99.6 %, but eval_checkpoint and the sanitiser class every single character as garbage (100 %): they were built for alphabetic words. Assigned bin: the language-adaptive grader assumes one language and votes Indonesian (prose 4.5 %, non-prose 93.8 %), applying alphabetic rules to Han characters; the sanitiser gives 62 % garbage for the same reason. **These are assessor limits on single-character and mixed-script bins, kept as data and not repaired.**
