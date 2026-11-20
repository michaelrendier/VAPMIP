# c_monad_core — the live C monad, in full

Copied from `VAPMIP/PtolC/`, 2026-09-21. This paper's §3, §6, §9.6, and
§13 all excerpt small pieces of these files; the full files are here so
nothing is taken on trust.

- **`ptol.c`** — the current live touchpoint. `-M` mmaps `monad3_c.bin`
  and reads a word's stored 19-vector by raw pointer arithmetic
  (§9.6, §13.3). This is the actual running monad, not a stand-in.
- **`monad.c`** — the real update law: `monad_learn_ex`'s β-deepening,
  the `prose_seen` ladder, the A-matrix 2D inverse-distance coupling.
  §6.5's C-kernel notebook extracts its cells directly from this file.
- **`wntest.c`** — the C-vs-Python cross-check for
  `dump_boxkite_bin.c`'s WordNet relation counts, verified 2026-08-25
  (§6.1).
- **`ptolemy.h`** — real constants, including `MONAD_BETA_SAT = 7.552`,
  the live value that corrected `monad_bin/SPEC.md`'s stale `(0,1]`
  claim (§6.5).
- **`boxkite_bin.h`** — the packed `BoxKiteEntry` record, byte-identical
  on both the C and Python sides of the build (§6.1, §13.2).
- **`dump_boxkite_bin.c`** — builds `c_monad_wordnet.bin` from the real
  WordNet C library, not a reimplementation (§6.1, §13.2).
