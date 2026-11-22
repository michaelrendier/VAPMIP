# Broca: the scalar and scaled boxkite

*Entry page, rewritten 2026-11-21. Branch `boxkite`. Everything under `Currentwork/Broca/` is a copy; the originals stay in the VAPMIP root and in `docs/`. The names Broca and Wernicke are a division of labour, not neuroscience.*

**What is here.** The structure side of the sentence constructor: the context kite, its struts and relations, the Mind's-Eye kite in motion (De Marrais G2 deformations), context flow, and the morphology/conjugation `repass()` still to come. It constrains and orders; it may extinguish a candidate but does not outvote the semantic web (`Currentwork/Wernicke/`).

**Two kites, never mixed.**

| kite | is | file |
|---|---|---|
| scalar boxkite | discrete and static: 7 ordered pairs, pencil, string, flashlight, the tension law. One word. | `src/19D_rotary_boxkite_monad.py` |
| scaled boxkite (Mind's-Eye) | the kite in motion; windspeed must deform it; basin attractors extinguish response possibilities. A sentence. | `src/scaled_mind_eye_boxkite_kernel_monad.py` |

Never insert static functionality into the scaled kite; never move the scalar kite.

**Read first, in this order**
1. `docs/Scaled-Kite-English-Thought-Center-Context.md`: the design record (sections 0–24; the corrections A–F of 2026-10-13 are §8).
2. `docs/Boxkite-Relational-Atlas.md`: the relational atlas.
3. `docs/context_flow_spec/`: the 95-test specification for context flow (nothing implemented).
4. `docs/Kings-Maille-Box-Kite-Rings-As-Sentences.md`, `docs/Boxkite-Deformation-Record-2026-10-12.md` (a dated record).
5. `docs/40_…`, `docs/41_…`: copies of two pages of the Tuning-the-Engine chronology (a historical record; not edited).

| dir | what |
|---|---|
| `src/` | `19D_*`, `rotary_*`, `ZD_rotary_*`, `VQ_rotary_monad.py`, `scaled_mind_eye_boxkite_kernel_monad.py`, `zd_approach_directions.py`, `sentence_context.py`, `context_fill.py`, `context_pruner.py`, `lyndon_conjugation.py` (stub), `phonetic_face.py`, and the C kite sources (`rotary_rerun.c`, `boxkite_bin.h`, `dump_boxkite_bin.c`, `monad3c.h`) |
| `catalogs/` | `Boxkite-Catalog.txt`, `marrais_boxkite_catalog.txt`, `SedenionOperators.txt` (the de Marrais catalogues) |
| `docs/` | the pages above |

Run Python files from the VAPMIP root, or with `PYTHONPATH=../..`. Licence: Proprietary, all rights reserved (`../../LICENSE`).
