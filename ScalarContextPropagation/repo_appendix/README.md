# repo_appendix — full code index

Everything this paper's mechanism touches, copied in, so this directory
is self-contained rather than a set of promises about other repos.
§13 (Code appendix) is the *curated* path through this; this README is
the *complete* index — every subdirectory, what it is, and which
section of the paper it backs.

## One deliberate exclusion: the Two Trees engine

The Two Trees engine (`GenerationalLineage/engine/lineage.py`,
`VAPMIP/engines/e06_two_trees.py`, and its own Full-Engine-Protocol
notebook, `VAPMIP/notebooks/16_e10_generational_lineage.ipynb`) is
**not** copied here, on purpose. §4 uses it as an *explainer* — it names
and demonstrates the 313/49999 boundary this paper's letter alphabet is
built on — not as something this paper builds or ships. The engine
itself, its notebooks, and its wiki live in `ValaQuenta` and `VAPMIP`
and stay there; this paper only ever reads its output. Every other
mechanism this paper's prose touches, including things mentioned only
once or in passing, is copied below.

## Subdirectories

- **`semantic_prime_hash/`** — §3. The original word→prime address
  mechanism and its Fibonacci-collision fix.
- **`c_monad_core/`** — §3, §6, §9.6, §13. The live C monad in full:
  `ptol.c` (the current touchpoint, `-M`), `monad.c` (the update law
  §6.5 extracts from), `wntest.c` (the C/Python cross-check), the two
  headers (`ptolemy.h`, `boxkite_bin.h`), and `dump_boxkite_bin.c` (the
  WordNet→C build step).
- **`wordnet_context_hash/`** — §5, §6, §7. `wordnet_boxkite.py`
  (`spelling_code`, `context_code`, the whole shipped scheme),
  `monad_combine.py` (the `monad3_c.bin` build), `monad.py` (the
  original address, unaltered since 2026-05-27), `monad_english_io.py`
  (home of `basin()`, the A-Matrix Basin Windspeed), `prime_hash.py`
  (the unshipped `split_tiers()` fix for the U+200B bug, §3.3),
  `context_pruner.py`/`context_hash_v2.py` (related addressing
  utilities referenced in passing), and the live `monad_bin` spec.
- **`box_kite_engine/`** — §9, §11, §13.5. `ValaQuenta/modules/box_kite/`
  in full (`maths.py`, `tools.py` — `pencil()`, `box_kites()`,
  `assessors()`, `chart_of()`), plus the three wiki pages this paper's
  §9 checks its own work against: `box_kite.md` (the established
  object), `pencil_hyperstring.md` (the `Φ_w` conjecture §9 tests),
  `inversion.md` (the `J_N` definition §9.5 distinguishes `J_2` from).
- **`j2_involution/`** — §9.5. Every J_2-adjacent calculation,
  application, and design specification this project has: the engine
  (`e09_j2_involution.py`), the two design-spec wiki pages
  (`51_j2_involution_riemann_fermat.md`,
  `60_heart_j2_involution.md`), and two notebooks that apply it
  (`14_heart_j2_involution.ipynb`, a general application;
  `method2_j2_involution_t256.ipynb`, a cryptographic one). This
  project's wider framework is UFT-adjacent territory this paper's own
  prose keeps deliberately obfuscated (§9.5 states only the exact,
  checkable maths) — that is a desk-rejection decision about *this
  paper*, not a restriction on the code itself, which is included here
  in full per the author's own instruction.
- **`sentence_constructor/`** — §11. The live, running sentence
  constructor this paper's windspeed doesn't feed yet:
  `rotary_rerun_boxkite_monad.py` (the real `BoxKite` object,
  `BoxKite.between(eye, hands)`), `rotary_rerun_monad.py` (the wider
  monad it's built in), and `grammar/` — the whole real sentence
  creator (VerbNet sails, WordNet hypernym-closure fill, the SELRESTR
  gate, and `rotary_bridge.py`, the install point confirmed live
  2026-09-11).
- **`reference_docs/`** — background cited in passing throughout:
  `Boxkite-Catalog.txt` (§11's full inventory), the reference-machine
  spec (§2.4, §8), the A-matrix wind/lift gate this paper's windspeed
  work checks against (§9), the historic wiki-16 semantic-prime
  foothold (§3.4), and the Native-Space coordinate-frame primer §9.3's
  first correction is grounded in.
- **`monad3c_update/`**, **`boxkite_exploration/`**,
  **`windspeed_reconstruction/`** — already-documented, see their own
  READMEs (`windspeed_reconstruction/README.md`) or §13.1/§6.5.
- **`methodology/`** — the two Claude Code skills this paper's own
  working process produced and cites (`observer-position`,
  `cs-paper-code-conventions`) — process, not results, kept for anyone
  reproducing how this paper was actually built.

## Licensing, stated plainly (the author's own words)

The Scalar Boxkite Context Propagator — everything in this paper and
this directory — is **GNU/GPL**. Free to use, study, modify, and
redistribute, research or commercial, under that license.

The Monad itself (the live system this code feeds into, beyond what
this paper describes) is **license-restricted**: researchers, students,
hobbyists, and anyone without deep pockets can use and study it freely;
commercial use is limited and priced to the depth of the pockets asking.

`0_RB` and the dynamic actual-path-of-the-photon Lagrangian are the
author's personal intellectual property — real, not absent from this
work, obfuscated in this paper's prose by a desk-rejection judgment call
about what a first CS preprint should say, not by a decision to
withhold them from people equipped to use them properly. Using that
single equation, that Lagrangian, and the wider framework together
inside the Monad is the author's personal IP. Ptolemy itself is not for
sale, full stop, unless P.O.E. gets a green light.
