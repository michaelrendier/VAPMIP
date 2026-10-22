# 17 · v3.0 — the word list and the two Universal Native Space bins

**Job.** Record the v3.0 word list, the two UNS bins built from it, why Chinese is the baseline, and the first side-by-side survey of M3 and M4. Flat mechanisms (M1, M2) are not used. Nothing is assigned or aligned yet; the assignment of English words to Chinese idea slots is the next discussion.

## Why Chinese is the baseline (Cody's stated rationale, 2026-10-21)
A) it is **ideographic**: a character is an idea, not a spelling (an ideographic system keeps *couch* and *chair* from being two versions of one idea); B) it is **alive and spoken well today** (not dead, not recently dead, not dying like Navajo and Comanche); C) it has existed for **over five millennia**; D) it is believed to be **one of the most efficient partitionings of idea space** in language form. It is taken as the bare minimum of ideas space. Hieroglyphs would have been chosen were the language not dead; Demotic put one character at the start of a word to carry its tone, which became the invisible tone / tense / conjugation marks the orbweaver will carry ([10](10_design_notes.md)). A, B, C are Cody's statements; D is his assumption and is **not measured here**.

## The word list (`SemPriCon/calibration/calibration_v3_en_zh.tsv`, read-only, sha256 `d130d2b43e2fe0fbf65dbaad193bf6ed8451c3cfe49ed93b2169e96b716ed1f1`)
Built by `tools/calibration_v3.py` (a modified copy of `calibration_v1.py`; v1 is frozen and untouched) from `tools/en_word_freq.py`, `tools/zh_char_freq.py`, WordNet, CC-CEDICT and the Han alphabet. The calibration protocol of [06](06_the_calibration_set.md): 512 concepts × 2 (S simple, L deeper), direct English and Chinese analogues, every surface word once, ≤ 15 % per lexicographer class, Traditional characters. **Change from v1:** every Chinese word is a **single character** in the engine's Han alphabet (M2/M4 map single characters only). The Open Multilingual WordNet has only 135 synsets with two single-character Mandarin lemmas, so Chinese candidates come from CC-CEDICT: S's character lists the English S word as a whole gloss (among its first four definitions), L is any other single character glossed by a lemma of the synset. Result: 1 024 rows, nouns 586, verbs 408, adjectives 30; 1 024 distinct English words and 1 024 distinct characters. **Known noise** (kept, as in v1): WordNet and CEDICT senses are imperfect and many characters are polysemous, so some pairs are near rather than direct (*beat* 勝, *mountain* 陵). Corrections go to a new version.

## The bins (`SemPriCon/clean/`, state v6, read-only, `tools/v3_build.py`)
`test_english_v3.0.bin` (sha256 `5fecfabee487cc793812f09a9390cc4e912f033d75e983158d3c13d5d20a2888`) from M3 (`uns_mech.en_uns`, the eb28ce8 float seed); `test_chinese_v3.0.bin` (sha256 `f2de1e456fff18c86d8ac6fe6e3acb00da3360cef677fc5a0f073952547cc3bd`) from M4 (`uns_mech.zh_uns`). Each is ground state → one pass over its half of the list → frozen, using the monad's own learning step (β ← β + E²·α·|sin γ|·π/2, label = highest-E arrival). Deliberate differences from the engine's ingest: the address is the UNS mechanism; γ is the **exact zero** of the slot for both languages; the engine's token filter is **not** applied (it would have rejected 8 English words: cry, fly, pharynx, scratch, strength, stretch, stylish, yr); a list of single words has no sentences, so no A edges. Checked: every stored slot and E equals the address recomputed from the mechanism; `ptol_bin.write_state` was verified byte-identical against two C-written v6 files. `data/v3_map.tsv` holds every row's slot, γ, E, turn, radius and state for both bins. PDF: `SpaceClaude/SemPriCon_v3.0_word_list_map.pdf`.

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
