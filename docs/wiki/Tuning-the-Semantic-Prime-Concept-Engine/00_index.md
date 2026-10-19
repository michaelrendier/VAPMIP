# TUNING THE SEMANTIC PRIME CONCEPT ENGINE — WIKI INDEX

The functional reference for **SemPriCon**: the semantic prime-concept hashing engine, starting from the original golden-ratio address code and updated as it changes.

> **Protocol (Cody, 2026-10-18).**
> 1. **Functionality, not provenance.** Each page says what a part does *now*, how to run it, and how to check it. It is not a log. Pages are edited **in place**; git preserves the history, and nothing is archived by hand.
> 2. **Only the semantic prime-concept hash.** Other exploratory methodologies live in [Tuning the Engine](../Tuning-the-Engine/00_index.md). This wiki starts from the original code (`PtolC/monad.c` at `eb28ce8`, documented as it ran in `SemPriCon/paper/The_Golden_Ratio_Monad.pdf`) and follows the code from there.
> 3. **A repass on this index is part of every update**: add or change the page, then re-check that every row below is current.
> 4. **The code is authoritative.** If a page and the code disagree, the page is wrong; fix the page.
> 5. **Fitting is allowed here and only here** (see [05](05_the_baseline.md)): English and the other languages are fitted to The Baseline. It stays forbidden in all mathematics work.

Working directory: `VAPMIP/SemPriCon/`. Test bed: Chinese (Traditional) and English (US, UK) now, each in its own single-language store; Swahili, Finnish, Indonesian and Quechua are on hold.

| Page | Part | What it specifies |
|---|---|---|
| [01_the_address.md](01_the_address.md) | address | word → slot and energy: the original ASCII code, and the Unicode code |
| [02_the_tokenizer.md](02_the_tokenizer.md) | tokenizer | text → tokens: Unicode letters, Han characters, sentence ends, the filter |
| [03_the_slots_and_collisions.md](03_the_slots_and_collisions.md) | slots | N = 25 000, placement, occupancy, which collisions are errors and which are the point |
| [04_learn_and_speak.md](04_learn_and_speak.md) | engine | learning weights and speaking, as they run now; state version 5 |
| [05_the_baseline.md](05_the_baseline.md) | The Baseline | the Chinese reference, what is frozen, the fitting rules, Fresh Start |
| [06_the_calibration_set.md](06_the_calibration_set.md) | calibration | the frozen 1 024-word testing-and-debugging set (English + Chinese; 512 simple, 512 deeper synonyms) |
| [07_data_and_tools.md](07_data_and_tools.md) | data | corpora, licences, closed doors, and every tool with its command |
| [08_verification.md](08_verification.md) | tests | what is verified against the compiled binary, how to re-run it, what is weak |
| [09_the_test_bins.md](09_the_test_bins.md) | test bins | `test_chinese_v1.0.bin` and `test_english_v1.0.bin`: one alphabet each, how they were built, versioning |

*9 pages.*
