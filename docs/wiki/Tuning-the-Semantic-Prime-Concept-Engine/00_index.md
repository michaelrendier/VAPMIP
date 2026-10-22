# TUNING THE SEMANTIC PRIME CONCEPT ENGINE — WIKI INDEX

The functional reference for **SemPriCon**: the semantic prime-concept hashing engine, starting from the original golden-ratio address code and updated as it changes.

> **Protocol (Cody, 2026-10-18).**
> 1. **Functionality, not provenance.** Each page says what a part does *now*, how to run it, and how to check it. It is not a log. Pages are edited **in place**; git preserves the history, and nothing is archived by hand.
> 2. **Only the semantic prime-concept hash.** Other exploratory methodologies live in [Tuning the Engine](../Tuning-the-Engine/00_index.md). This wiki starts from the original code (`PtolC/monad.c` at `eb28ce8`, documented as it ran in `SemPriCon/paper/The_Golden_Ratio_Monad.pdf`) and follows the code from there.
> 3. **A repass on this index is part of every update**: add or change the page, then re-check that every row below is current.
> 4. **The code is authoritative.** If a page and the code disagree, the page is wrong; fix the page.
> 5. **Fitting is allowed here and only here** (see [05](05_the_baseline.md)): English and the other languages are fitted to The Baseline. It stays forbidden in all mathematics work.

Working directory: `VAPMIP/SemPriCon/`. Test bed: Chinese (Traditional), English (US, UK), Finnish and Indonesian, each in its own single-language store; Swahili and Quechua are on hold.

| Page | Part | What it specifies |
|---|---|---|
| [01_the_address.md](01_the_address.md) | address | word → slot and energy: the original ASCII code, and the Unicode code |
| [02_the_tokenizer.md](02_the_tokenizer.md) | tokenizer | text → tokens: Unicode letters, Han characters, sentence ends, the filter |
| [03_the_slots_and_collisions.md](03_the_slots_and_collisions.md) | slots | N = 25 000, placement, occupancy, which collisions are errors and which are the point |
| [04_learn_and_speak.md](04_learn_and_speak.md) | engine | learning weights and speaking, as they run now; state version 6 |
| [05_the_baseline.md](05_the_baseline.md) | The Baseline | the Chinese reference, what is frozen, the fitting rules, Fresh Start |
| [06_the_calibration_set.md](06_the_calibration_set.md) | calibration | the frozen 1 024-word testing-and-debugging set (English + Chinese; 512 simple, 512 deeper synonyms) |
| [07_data_and_tools.md](07_data_and_tools.md) | data | corpora, licences, closed doors, and every tool with its command |
| [08_verification.md](08_verification.md) | tests | what is verified against the compiled binary, how to re-run it, what is weak |
| [09_the_test_bins.md](09_the_test_bins.md) | test bins | `test_{chinese,english,finnish,indonesian}_v2.0.bin`: one alphabet each, how they were built, versioning |
| [10_design_notes.md](10_design_notes.md) | design notes | decided-but-unbuilt ideas, e.g. the invisible tone / tense / conjugation prefix |
| [11_baseline_mapping_zh_en.md](11_baseline_mapping_zh_en.md) | workbench | LIVE SNAPSHOT: the four zh/en word-list bins, where every list word landed, pair offsets, second-pass effects, order effect, fault rows; pull a block with `tools/wb_pull.py` |
| [12_four_mechanisms.md](12_four_mechanisms.md) | mechanisms | the four address mechanisms (M1 English ½ line, M2 Chinese ½ line, M3 English in UNS, M4 Chinese in UNS), why English and Chinese differ, shared constants, order of work |
| [13_M1_english_to_half_line.md](13_M1_english_to_half_line.md) | M1 | the machinery behind `holcus·same·stuff·seemy` as it ran (eb28ce8), and what it measurably is |
| [14_M2_chinese_to_half_line.md](14_M2_chinese_to_half_line.md) | M2 | single Chinese character → dictionary position → exact zero; E from the golden-ratio hash of the key component; self-test and held-out probes |
| [15_M3_english_in_uns.md](15_M3_english_in_uns.md) | M3 | M1 as golden-angle rotations on the π/2 equatorial great circle of UNS; byte-identical replies |
| [16_M4_chinese_in_uns.md](16_M4_chinese_in_uns.md) | M4 | M2 as an azimuth turn on the equator with the key component as radius |
| [17_v3_word_list_and_uns_bins.md](17_v3_word_list_and_uns_bins.md) | v3.0 | the v3.0 word list (single Chinese characters), why Chinese is the baseline, the two UNS bins, M3 and M4 side by side, first survey |
| [1024.md](1024.md) | word list | the English row headers, their Chinese words and the slot of each in every bin; updated in place |

*18 pages* (and, outside the wiki: `../../../SemPriCon/SemPriCon_requ_conf.md`, the required-configurations list, and `../../../SemPriCon/SpecTools/README.md`, the specification toolset: exact zeros, bin-creation recipes by version, word lists, probes).
