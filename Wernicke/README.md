# Wernicke: the semantic orbweaver tree

Branch: `orbweaver`. The semantic side of the sentence constructor: which words, chosen because of their relation to the prompt. Open vocabulary, graded weights, learned from usage. **No box kite here.** (Wernicke's area: meaning and word selection. An analogy used as a division of labour, not neuroscience.)

Copies only; the originals stay where they are in VAPMIP. Run Python files from the VAPMIP root, or with `PYTHONPATH=..` (they import their siblings).

| dir | what |
|---|---|
| `src/` | `boxkite_orbweaver_monad.py` (Phase 35 orbweaver), `wordnet_boxkite.py` (WordNet relation hash, H3), `context_hash_v2.py`, `prime_hash.py`, `lineage_hash.py`, `monad_addressing.py`, `monad_english_io.py`, `semantic_paragraph.py`, `zork_parser.py`, `speak.py`, `sem_hash.py`, `eval_checkpoint.py` |
| `first_monad_current/` | the C sources of today's `ptolemy` (`make ptolemy`; reads PTOL v4 bins; reproduces the May reply on `checkpoints/clean/monad_wordnet_v4_20260519.bin` in a scratch `$HOME/.ptolemy/`) |
| `first_monad_history/` | `monad.c`, `monad.h`, `ptolemy.h` exactly as committed at `fb7ba29` (v1.0, 2026-05-15) and `eb28ce8` (v1.215, 2026-05-18, the screenshot engine) |
| `sibling/` | `semantic_engine.py`, `hyperwebster.py` from the deprecated SemanticWordEngine (golden-ratio hash, May 2026) |
| `docs/` | `semantic_orbweaver_notes.md` (live notes), Tuning the Engine 35, 42, 43 |

The May bins (`checkpoints/clean/`) are historical and read-only. Never write to them.
