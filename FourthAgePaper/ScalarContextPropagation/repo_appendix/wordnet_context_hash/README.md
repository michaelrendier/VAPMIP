# wordnet_context_hash — the shipped Python addressing scheme, in full

Copied from `VAPMIP/`, 2026-09-21.

- **`wordnet_boxkite.py`** — the actual shipped scheme: `spelling_code`
  (§5.2), `context_code`/`CONTEXT_PRIMES` (§7), `LETTER_PRIMES`,
  `next_prime`. Every notebook in `notebooks/` imports this file
  directly rather than restating it.
- **`monad_combine.py`** — builds `monad3_c.bin` from the three source
  stores (`eng:`, `wn:`, `phon:`) — the union-of-vocabularies step (§6.2).
- **`monad.py`** — the original word→prime address, unaltered since
  commit `204c75d`, 2026-05-27 (§3.1). The very first mechanism this
  whole project ran.
- **`monad_english_io.py`** — home of `basin()`, the A-matrix basin
  drift this paper renames the **A-Matrix Basin Windspeed** and
  explicitly does not use (§9.1, §11).
- **`prime_hash.py`** — names the U+200B collision correctly as an
  aperture/category error and proposes `split_tiers()`; designed, not
  yet wired into `monad.py` (§3.3).
- **`context_pruner.py`**, **`context_hash_v2.py`** — related
  addressing utilities from the same lineage, referenced in passing
  elsewhere in this project; included here for completeness.
- **`monad_bin_SPEC.md`** — the live `monad3_c.bin` format spec
  (renamed from `SPEC.md` on copy to avoid a filename collision with
  this directory's other README).
