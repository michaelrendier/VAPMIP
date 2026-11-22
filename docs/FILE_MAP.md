# File map of the VAPMIP root (2026-11-21)

The Python modules stay at the repository root on purpose: the console (`PtolemyDesktop/ptolemy_console.py`) and the harness find the monads by the pattern `VAPMIP/*monad*.py`, and the modules import each other by flat name. Moving them is a code change (see the last section). This page is the map instead.

## Layout
| directory | holds |
|---|---|
| `Currentwork/` | `Broca/`, `Wernicke/`, `SemPriCon/` (live work) |
| `docs/` | the wiki, specs, notes, `Repository_Reference.md`, this file |
| `paper/`, `FourthAgePaper/ScalarContextPropagation/` | the two papers |
| `outreach/` | letters and emails; `outreach/archive/` the PDFs they attached |
| `records/` | audits, job lists, loose notes |
| `archive/` | superseded and source-only files |
| `PtolC/`, `monad_bin/` | the compiled monad and the bin format |
| `engines/`, `engine/`, `tools/`, `tests/`, `benchmarks/`, `notebooks/` | engines `e01…e17`, grammar, tools, tests, benchmarks, notebooks (`notebooks/tuning_the_engine/` is a record) |
| `checkpoints/`, `datasets/`, `corpus/`, `code-corpora/` | stores and data (referenced by path from notebooks and tools) |
| `face/`, `skills/`, `RingCircle/`, `HyperindexCompression/`, `gallery/`, `image_gallery/`, `holcus_paths*` | face, the monad's skill modules (not Claude skills), the ring-circle table, the compression notes, images and traces |

## Python modules at the root, by kind
* **Core:** `monad.py` (and `monad.c`, `monad.h` family), `harness.py`, `prime_hash.py`, `wordnet_boxkite.py`, `live_vocabulary.py`, `monad_addressing.py`, `monad_combine.py`, `monad_english_io.py`, `monad_bus.py`, `monad_browse.py`, `monad_identity.py`, `ptol_state.py`, `add_scale_sign.py`, `lineage_hash.py`, `context_hash_v2.py`, `semantic_paragraph.py`, `sentence_context.py`, `context_fill.py`, `context_pruner.py`, `zork_parser.py`, `speak.py`, `constructor.py`.
* **The current tools:** `19D_rotary_boxkite_monad.py` (scalar boxkite), `scaled_mind_eye_boxkite_kernel_monad.py` (scaled boxkite), `boxkite_orbweaver_monad.py` (orbweaver).
* **Other monads** (24 in all, discovered by `*monad*.py`): `19D_boxkite_context_monad.py`, `rotary_monad.py`, `rotary_rerun_monad.py`, `rotary_rerun_boxkite_monad.py`, `ZD_rotary_monad.py`, `VQ_rotary_monad.py`, `RF_monad.py`, `UDEO_monad.py`, `lio_monad.py`, `intention_monad.py`, `translator_monad.py`, `ptolemy_monad.py`, `walkwithme_monad.py`, `monad_harness_diagnostic.py`, `monad.py`.
* **`lshs*.py`** (the Laplacian/SDR/voice family): `lshs.py`, `lshs_captain.py`, `lshs_holcus_voice.py`, `lshs_laplacian.py`, `lshs_portrait.py`, `lshs_read.py`, `lshs_sdr.py`, `lshs_speak.py`.
* **Holcus window and traces:** `holcus_from_above.py`, `holcus_window.py`, `rotary_boxkite_window.py`, `layer_spectrograph.py`, `listen.py`, `phonon.py`.
* **Experiments and visuals:** `defect_field.py`, `demo.py`, `euler_prime_spiral.py`, `hypernumeric.py`, `sieve_clock.py`, `superformula_svg.py`, `vagcom.py`, `zd_approach_directions.py`, `lyndon_conjugation.py`, `phonetic_face.py`, `discocat_corpus.py`, `generational_lineage_engine.py`, `burn.py`.
* **Hardware and authentication:** `cad.py`, `cam3.py`, `fritzing.py`, `pendant.py`, `auth_totp.c/.h`.
* **Text and data at the root:** the corpora (`*_corpus.txt`, `war-corpus.txt`, `prime_dictionary.txt`, `corpus_list.json`), `foundations.txt`, `meaning.txt` (source corpora, ingested by `burn.py` and `monad.py`; not documentation), the catalogs (`Boxkite-Catalog.txt`, `marrais_boxkite_catalog.txt`, `SedenionOperators.txt`), `monad_sentences.json`, `monad_sedenion_addresses.pkl`.

## What it would take to move the Python modules
1. Change the console's discovery pattern and the harness's import path to the new folders; 2. give every module a package-relative or `sys.path`-based import for its siblings; 3. repoint `corpus_list.json`, `burn.py` and the notebooks' data paths (the notebooks under `notebooks/tuning_the_engine/` are a record and must not be edited, which pins their data files where they are). Until then the root stays flat and this page is the index.
