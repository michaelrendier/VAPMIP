# Tuning the Engine — one notebook per phase

Companion notebooks for the VAPMIP wiki log `docs/wiki/Tuning-the-Engine/` (Phases 1–42, plus the addenda 02b and 21b).
Each `phase_NN.ipynb` **runs the machinery its wiki page describes** — against the live repo, not against numbers copied from the page —
and records, claim by claim, what reproduces.

## What a notebook is

| Block | Purpose |
|---|---|
| header | phase, date, byline, link to the wiki page |
| cells | the claims of the page, each re-computed (own re-derivation where the page gives a formula; the repo's engine/binary/script where it names one) |
| **Ledger** (last cell) | every claim as `PASS` / `FAIL` / `PROSE` / `SKIP` with the measured detail |

* **PASS** — reproduced against the live repo.
* **FAIL** — did *not* reproduce. This is a result, kept in the output (the wiki's own rule: failures stay in the code). It means the page, the code, or the data has moved, or the page's claim is wrong; the detail line says which and by how much.
* **PROSE** — stated on the page with no executable counterpart (interpretation, values, history). Never counted as a pass.
* **SKIP** — has an executable counterpart that cannot run here (e.g. the battery-energy rows need the laptop unplugged; the iGPU row needs `pyopencl`).

`FINDINGS.md` is the roll-up: a table of all notebooks and every FAIL with its detail. Regenerate it with `python3 ledger_summary.py`.

## Running

```
PtolemyDesktop/.venv/bin/python VAPMIP/notebooks/tuning_the_engine/build_notebooks.py          # all phases
PtolemyDesktop/.venv/bin/python VAPMIP/notebooks/tuning_the_engine/build_notebooks.py 03 17 42 # some phases
python3 VAPMIP/notebooks/tuning_the_engine/ledger_summary.py                                   # rewrite FINDINGS.md
```

* The notebooks are **generated** from `specs/phase_NN.py` (title, date, page, a list of markdown/code cells) by `build_notebooks.py`, which executes them in the `ptolemy-venv` kernel kept beside it (`.jupyter_path/kernels/ptolemy-venv`, `PYTHONHASHSEED=0`). Edit the spec, rebuild — do not hand-edit the `.ipynb`.
* The venv kernel matters: the system `python3` carries a `~/.local` numpy that shadows the apt one (ABI mismatch with nltk/pandas).
* `tte.py` is the shared helper (`from tte import *`): paths, the constants (`OMEGA_ZS`, `D_STAR`, `GAP`, …), `Ledger`, `scratch()`, `ptol_raw()` (runs `PtolC/ptol -r` with `HOME` redirected) and `zd_vectors()` (the 84 sedenion zero-divisors recomputed from `engines/_sedenion.cd_mul`).
* A few notebooks are slow because they re-run real programs: 24 (~1 min), 34 (~1 min), 41 (~3 min, five scratchpad scripts), 42 (~1.5 min, the whole 24-module benchmark).

## Side-effect discipline

Notebooks must not change the user's state. `ptol` is always run with `HOME` redirected to a scratch directory (it writes papers into `~/.ptolemy`); `ptolemy -r -n` never saves; C binaries are compiled into scratch directories; the Aulë stream is captured instead of written; `PtolC/*.bin` and `~/.ptolemy/monad*.bin` are checksummed before and after in Phase 42. Note that `ptolemy-monad.service` (the resident conversational/document ingest) folds text into `PtolC/monad3_c.bin` **by design**, so that one file's modification time can change while any notebook runs; Phase 42 says so in its ledger rather than claiming "unchanged".

## Conventions

* Maths is written in Unicode; code uses the repo's own identifiers.
* Where the page quotes a number, the notebook recomputes it; where the page quotes a sentence that the repo no longer produces (the engine moved on), the check fails and the detail says what the code does now.
* Hash-order determinism: the kernel runs with `PYTHONHASHSEED=0`; Phase 32 shows that `ptolemy_monad.process_input` is *not* deterministic across hash seeds (set-iteration order), which also explains the changed wording of its replies in Phase 42.
