# Re-check log (moved from the README on 2026-11-21)

Dated notes, newest first, kept as written. Symbols in the text of the paper follow `@RCCM_SYMBOLS` (α fine-structure; A_π = W(1); Ω_ζΣ = d*).

**2026-09-28 — re-checked against GenerationalLineage 1.0.0; Facebook added to
author contact.** `GenerationalLineage` shipped its first public release
(v1.0.0) the day after this paper's own consistency pass, including a fix
unrelated to anything this paper cites: `engine.maths` dropped its dependency
on a sibling repository's `udeo_poc.CayleyDickson` (replaced with GL's own
`engine.lineage.cd_mul_gf2`), which only affects GL's own EXTENDED layer, not
`lineage.py` or `cs_benchmark.py`. Re-run live against the released code,
today: `import lineage; lineage.un_sieve(100_000)` (§4.4) still reproduces
`313`, `49999`, and `7.193551572213686` bit-for-bit; the `cs_benchmark.descend`
import and call in §8 (`from GenerationalLineage.engine.toolsets.cs_benchmark
import descend`) still runs exactly as shown. Nothing in this paper needed a
correction. Author contact block (top and §12) gained a Facebook link,
`facebook.com/rendier`, alongside the existing GitHub and ORCID entries.

**2026-09-27 — consistency pass.** Every piece of code this paper
names or shows a Listing for was checked directly against the live
source it claims to be (not the `repo_appendix` snapshot, not memory):
`VAPMIP/monad.py`, `VAPMIP/wordnet_boxkite.py`, `VAPMIP/monad_combine.py`,
`VAPMIP/PtolC/{boxkite_bin.h, dump_boxkite_bin.c, ptol.c, monad.c,
ptolemy.h}`, `ValaQuenta/modules/box_kite/maths.py`,
`GenerationalLineage/engine/lineage.py`. One real discrepancy found and
fixed: §6.1/§13.2's `BoxKiteEntry` C struct was missing the live
header's explicit `uint8_t _pad[3]` field and used literal `32`/`19`
where the real header uses `#define BOXKITE_WORD_LEN`/`#define
N_RELATIONS` — both sections now match `PtolC/boxkite_bin.h` exactly.
Everything else checked exact on first pass, including re-running
`GenerationalLineage/engine/lineage.py::un_sieve(100_000)` live rather
than trusting the recorded numbers: `313`, `49999`, and the birth/death
entropy gap (`7.193551572213686`, stated in the paper to two decimals
as `+7.19`) all reproduce bit-for-bit.


