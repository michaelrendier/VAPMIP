# SpecTools — the specification toolset

**File naming for bins, speakers (TestMonad), assessments and mappings: `NAMING_CONVENTION.md` (this folder).**

Start here. Everything we use to create the SemPriCon bins, measure them, and place words on the critical line, with a pointer to where it lives and how to run it. Nothing in this folder is a result to be trusted blindly: each entry says how to regenerate it and what it was checked against.

Setup: `python3 -m venv .venv && .venv/bin/pip install numpy mpmath scipy reportlab` (run from `SemPriCon/`; the venv is gitignored). Rules: bins are read-only; HOME at a throwaway directory when running the engine; never touch `~/.ptolemy/monad_wordnet.bin`.

## 1 · The zeros of ζ (exact)
| item | what | check |
|---|---|---|
| `zeros/zeros_exact.py` | finds the first N zeros ρ_k = ½ + iγ_k: Hardy-function scan, `mpmath.siegelz` refinement, 8 processes, checkpointed. `python3 SpecTools/zeros/zeros_exact.py 25000` (about 1–2 h; safe to stop and re-run) | 21 indices against `mpmath.zetazero` to 1e-10; min gap asserted |
| `zeros/zeros_exact_25000.tsv` | the table: `k  γ_k`, 18 digits | sha256 `0a51f4fc…2ee1` |
| `zeros/zeros_exact_300.tsv` | the first 300, a quick copy | |
The engine's own `generate_zeros` is a smooth Newton approximation, off by up to 1.94 against this table. Used by M2 (`tools/zh_half_line.py`).

## 2 · The four mechanisms (wiki 12–16)
| mechanism | code | page |
|---|---|---|
| M1 English → ½ line (eb28ce8 as it ran) | `tools/monad_py.py` (port, 8/8 replies identical to the compiled binary), `src/PtolC_eb28ce8/` | wiki 13 |
| M2 Chinese → ½ line, single characters | `tools/zh_half_line.py --selftest`, `tools/zh_structure.py` | wiki 14 |
| M3 English in UNS (π/2 equator) | `tools/uns_mech.py --selftest` | wiki 15 |
| M4 Chinese in UNS | `tools/uns_mech.py --selftest` | wiki 16 |
Wiki = `../docs/wiki/Tuning-the-Semantic-Prime-Concept-Engine/`. Requirements, faults and open decisions: `SemPriCon_requ_conf.md`.

## 3 · Bin creation, by version (the number is in the file name)
| version | what | recipe |
|---|---|---|
| v1.0 | `test_chinese_v1.0.bin`, `test_english_v1.0.bin` | `bin_creation/build_v1.0_zh_en_bins.md`; archive `clean/archive/v1.0/` |
| v2.0 | `test_finnish_v2.0.bin`, `test_indonesian_v2.0.bin` | `bin_creation/build_v2.0_fi_id_bins.md` |
| v2.0 | the four zh/en word-list bins (`test_{chinese,english,chinese_english,english_chinese}_v2.bin`) | `bin_creation/build_v2.0_zh_en_wordlist_bins.sh` (copy of `tools/exp_v2_run.sh`) |
| v3.0 | `test_english_v3.bin`, `test_chinese_v3.bin` (UNS mechanisms M3 and M4 over the v3.0 word list), `test_chinese_english_v3.bin` (English words assigned to the Chinese slots); speaking test `tools/v3_speak.py` | `tools/v3_build.py` (needs `calibration/calibration_v3_en_zh.tsv`); v2.0 archived in `dirty/v2.0/`, gitignored; assessments in `clean/archive/v2.0/` |
Common pieces: `tools/ptol_bin.py` (state-file reader/writer), `tools/gen_alphabet.py`, `tools/ingest_corpora.py`, `tools/vocab_build.py`, `tools/text_build.py`, `tools/exp_v2_filter.py`, `tools/exp_v2_list.py`, `src/PtolC_unicode/` (+ `src/unicode_upgrade.patch`).

## 4 · The 1024-word list and the calibration sets
| item | where |
|---|---|
| the word list as mapped in the four v2.0 bins (updated in place) | wiki `1024.md`; source rows `experiment_v2/list.tsv` |
| frozen calibration set v1 (1 024 EN+ZH), pinned | `calibration/calibration_v1_en_zh.tsv`, `calibration/FROZEN.sha256` |
| calibration v2 (EN+ZH+FI+ID, candidate) | `calibration/calibration_v2_en_zh_fi_id.tsv`; builders `tools/calibration_v1.py`, `calibration_v2.py`, `calibration_build.py` |
| v3.0 list (1 024 rows, single Chinese characters, frozen) | `calibration/calibration_v3_en_zh.tsv`, `calibration/FROZEN_v3.sha256`; builder `tools/calibration_v3.py` with `tools/en_word_freq.py`, `tools/zh_char_freq.py` (system python3 + pyarrow); PDF of the list and its map `tools/v3_pdf.py`, wiki 17 |
| six-language set (on hold) | `calibration/on_hold/` |

## 5 · Assessments and probes
`tools/assess_bin.py` (structure, census), `tools/assess_prose.py` (language-adaptive prose-word assessment), `tools/exp_v2_assess.py`, `tools/en1_dict_pdf.py` (one-row-per-slot dictionary PDF of a bin), `tools/verify_against_c.py` / `verify_learn_against_c.py` / `verify_unicode_against_c.py` (port vs compiled engine), `tools/zh_census.py`, `tools/unicode_address_measure.py`. Results: `clean/archive/v1.0/assessment/`, `clean/archive/v2.0/assessment/`.

## 6 · Orbweaver pathway
`orbweaver/LorenzStirling.py` (byte-identical copy, provenance in `orbweaver/PROVENANCE.md`): the basin classifier for the sentence constructor. Not wired in yet.

## 7 · Protocols
dPrint in new code (`tools/dprint.py`). Fresh Start: the version number rises only then; old files are archived, never edited; assessments are committed before any bin is gitignored.
