# Wernicke: the semantic orbweaver

*Entry page, rewritten 2026-11-21. Branch `orbweaver`. Except where stated, files under `Wernicke/` are copies; the originals stay in the VAPMIP root and in `docs/`. The names Broca and Wernicke are a division of labour, not neuroscience.*

**What is here.** The semantic side of the sentence constructor: which words, chosen because of their relation to the prompt. Open vocabulary, graded weights, learned from usage. **No box kite here** (the kites are in `Broca/`). The orbweaver's silks are the roles a sentence decomposes into: `ANCHOR SPAN SCAFFOLD ELABORATE HOOK WRAP SHELL`.

**State.** Built: the standard testing corpus, the content extractor v0, the sanitiser and bin builder, the monitor. Not built: the S and G scorers, the orbweaver as a voice that plays a reply. The orbweaver monads exist (`src/boxkite_orbweaver_monad.py`, Phase 35) and have been benched, not yet played.

**Read first, in this order**
1. `docs/semantic_orbweaver_notes.md`: the live notes (status block at the top).
2. `corpus/README.md`: the standard testing corpus every orbweaver function is tested against.
3. `extractor/README.md`: the extractor v0, its tests and its known failures.
4. `sanitize/README.md`: the token-level sanitiser for the granular bins.
5. `docs/35_…`, `docs/42_…`, `docs/43_…`: copies of three pages of the Tuning-the-Engine chronology (a historical record; not edited).

| dir | what |
|---|---|
| `src/` | `boxkite_orbweaver_monad.py` (Phase 35 orbweaver), `wordnet_boxkite.py` (WordNet relation hash), `context_hash_v2.py`, `prime_hash.py`, `lineage_hash.py`, `monad_addressing.py`, `monad_english_io.py`, `semantic_paragraph.py`, `zork_parser.py`, `speak.py`, `sem_hash.py`, `eval_checkpoint.py`, `math_isolate.py`, `grammar/` |
| `extractor/` | the content extractor v0 (original work, not a copy) |
| `sanitize/` | the sanitiser and `build_bins.py` (original work) |
| `corpus/` | the standard testing corpus: 11 public-domain works, 134 sampled sentences, 24 chat prompts, model-provided reference answers (unreviewed) |
| `first_monad_current/` | the C sources of today's `ptolemy` (`make ptolemy`; reproduces the May reply on `checkpoints/clean/monad_wordnet_v4_20260519.bin` in a scratch `$HOME/.ptolemy/`) |
| `first_monad_history/` | `monad.c`, `monad.h`, `ptolemy.h` exactly as committed at `fb7ba29` (v1.0) and `eb28ce8` (v1.215, the screenshot engine) |
| `sibling/` | `semantic_engine.py`, `hyperwebster.py` from the deprecated SemanticWordEngine (May 2026) |

The May bins (`checkpoints/clean/`) are historical and read-only; never write to them. Run Python files from the VAPMIP root, or with `PYTHONPATH=..`. Licence: Proprietary, all rights reserved (`../LICENSE`).
