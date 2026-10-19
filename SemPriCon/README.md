# SemPriCon — the golden-ratio monad, as it was

Work directory for the white paper on the simplest engine in the lineage: the May-2026 C monad (`PtolC/` at commit `eb28ce8`, v1.215) that answered "what is your name" with `holcus same stuff seemy`. SemPriCon = Semantic Prime Concept; the prime-concept hash itself is **not** in the baseline documented here.

| path | what |
|---|---|
| `src/PtolC_eb28ce8/` | the source at commit `eb28ce8`, unmodified (`git archive`); the authority for everything else here |
| `dirty/` | the store that was loaded (`monad_wordnet_v4_20260519.bin`, gitignored) + its `POISON.md` notice, `ASSESSMENT.md`, `assessment.json` |
| `tools/ptol_bin.py` | read-only reader of the PTOL state file (layout of `state.c`) |
| `tools/assess_bin.py` | the assessment (eval_checkpoint classifier + sanitiser + script census) |
| `tools/monad_py.py` | line-for-line Python port of the C functions, bugs included (`# AS-IS:`) |
| `tools/verify_against_c.py`, `tools/verify_learn_against_c.py` | port vs the compiled binary: replies byte-identical (8/8), learned state exact |
| `notebooks/01…06` | executed notebooks: store, address, learn, speak, the name, shortcomings |
| `paper/The_Golden_Ratio_Monad.{md,pdf}` | the white paper (arXiv-ready draft). Built from `paper/template.md` by `make_paper.py`: every number from `evidence.py` (fresh runs), every C listing cut verbatim from `src/`. `python3 paper/make_paper.py --check` fails if the committed text differs from a fresh run; `paper/build_pdf.sh` makes the PDF (pandoc + LuaLaTeX) |
| `tools/make_notebooks.py` | writes `notebooks/` (execute with nbconvert) |
| `figures/` | figures made by the notebooks |
| `src/PtolC_unicode/`, `src/unicode_upgrade.patch` | the Unicode build of the C monad (a copy of the 2026-05 source plus the patch) |
| `calibration/` | the frozen 1 024-word calibration set, English + Chinese (`calibration_v1_en_zh.tsv`, pinned by `FROZEN.sha256`); the six-language set is in `on_hold/` |
| `corpora/` | fetch scripts, manifest, licences, closed doors (data gitignored) |
| **wiki** | `../docs/wiki/Tuning-the-Semantic-Prime-Concept-Engine/` — the functional reference for everything here, updated in place |

Rebuild the reference binary: `cp -r src/PtolC_eb28ce8 build/ && make -C build/PtolC_eb28ce8`. Reproduce the reply:
`HOME=$PWD/scratch_home PTOLEMY_HOME=$PWD/scratch_home/.ptolemy build/PtolC_eb28ce8/ptolemy -c dirty/monad_wordnet_v4_20260519.bin -W "what is your name" -n`

Rules in force: the store is read-only; `monad3_c.bin` and everything `ptol.c` uses are untouched; the code at `eb28ce8` is authoritative over any comment or wiki about it.
