# Currentwork — what is being worked on now

Moved here 2026-11-21 (restructure). Everything in these three directories is live; history is in Git.

| directory | what | read first |
|---|---|---|
| `Broca/` | scalar and scaled boxkite (branch `boxkite`): the structure side | `Broca/README.md` |
| `Wernicke/` | the semantic orbweaver (branch `orbweaver`): the meaning side | `Wernicke/README.md` |
| `SemPriCon/` | the prime-concept baseline (Chinese first), battery v3 | `SemPriCon/README.md`; wiki `../docs/wiki/Tuning-the-Semantic-Prime-Concept-Engine/` |

## Old path → new path
`VAPMIP/Broca/` → `VAPMIP/Currentwork/Broca/` · `VAPMIP/Wernicke/` → `VAPMIP/Currentwork/Wernicke/` · `VAPMIP/SemPriCon/` → `VAPMIP/Currentwork/SemPriCon/`.
Pages that record history (the Tuning-the-Engine wiki and its copies, `notebooks/tuning_the_engine/`, dated entries in `CHANGELOG.md` and `TODO.md`) still use the old paths; read them through this map.

## Running things after the move
* Python files in `Broca/` and `Wernicke/` import their siblings from the VAPMIP root: run from `VAPMIP/`, or set `PYTHONPATH=../..` when running from inside a tree.
* SemPriCon runs in `Currentwork/SemPriCon/.venv` (`.venv/bin/python …` from `Currentwork/SemPriCon/`). Five paths that reached outside the tree were lengthened by one `..` (`tools/assess_bin.py`, `tools/wb_pull.py`, `tools/zh_wiki.py`, `tools/exp_v2_wiki.py`, `Wernicke/sanitize/sanitize_v0.py`).
* Checked after the move: `mappings/UNS/uns_mech.py --selftest`, `clean/TestMonad_english_v3.py`, `Wernicke/extractor/extract_v0.py`, and the VAPMIP tests (36 passed).
