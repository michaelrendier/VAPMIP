# The notebook-form plan — transcribed from `~/Desktop/thelist.png`, filled out

Transcribed verbatim from the screenshot, then each item annotated against
the actual notebooks (all 5 read in full this session, cell by cell,
including recorded outputs — not summarized from filenames).

**Decision (Cody, 2026-09-19): two artifacts, not one.** `README.md`
stays "cliff notes" — wide-scoped, shallow, pointing at all the code and
at the paper, not going deep. Abstract, §1, §2 stay exactly as they are.
The **paper** is a separate thing, built from the jupyter notebooks
written for each section, one section at a time — from §3 onward the
code is center stage, going incrementally deeper section by section,
guided (not duplicated) by the wide README. Convention **B** from
`cs-paper-code-conventions` applies to the *paper*, not to `README.md`.

---

## 1. How to run this
> requirements.txt, venv, notebooks/, which sibling repos (VAPMIP,
> ValaQuenta) have to be checked out alongside this one for the imports to
> resolve (currently hardcoded home-relative paths — a real portability
> wrinkle, flag or fix here).

**Not a notebook — setup prose.** Confirmed the wrinkle is real: every one
of the 5 notebooks' first code cell does
`sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/VAPMIP"))` (or
`.../ValaQuenta/modules/box_kite`) — hardcoded to this machine's home
directory, not relative to the repo. Existing §2.3 of `README.md` already
states the install steps; it does not yet flag this path issue. Carry
forward, and either (a) state it as an honest limitation (matches the
paper's own provenance-label ethos) or (b) fix it with a repo-relative
`sys.path` resolution before publishing. Recommend (a) now, (b) before
submission.

## 2. The problem
> no multidimensional, inspectable per-word context in a transformer
> (keep, short, motivation only — no equations).

**Not a notebook.** Current `README.md` §1 already satisfies this exactly
— prose only, already zero equations. Carries forward unchanged.

## 3. "The primes are the words"
> token → address (notebook 01): the actual Horner/next_prime/π code, the
> 6543-vs-6542 off-by-one *and the code that found it*, the U+200B
> collision bug *and the code that reproduces it*.

**`notebooks/01_semantic_prime_hashing.ipynb` — 14 cells, checked in full,
with recorded outputs.** Everything the outline names is actually in
there:
- `monad._horner_hash` / `monad._next_prime` / `monad._word_zero_idx`,
  run live against `VAPMIP/monad.py` (cells 1–3), worked example table for
  6 real words with real `H`/`next_prime`/`idx`/`gamma` numbers.
- determinism check (cell 5): pass.
- live 347,119-word vocabulary distribution (cells 7–8): 109,403 words/s,
  buckets `[1, 6543]`, `6543/6542` distinct buckets used — the self-
  contradictory count is preserved verbatim as found, not smoothed over.
- U+200B / `'v!'` collision (cells 9–10): reproduced live —
  `horner(U+200B) == horner('v!') == 8171`, both `idx=1026`.
- the 6543-vs-6542 anomaly (cells 11–13): chased to a **MATHS/METHOD, not
  CODE** verdict — `π(65537)=6543` because 65537 is itself prime, and 91
  real live-vocabulary words land in bucket 6543 (`apocope`,
  `contemplating`, `discipline`, among some non-word tokens worth an
  honest aside — see draft).

**Two things adjacent to this bug, not inside the notebook, flagged for
your call (see clarifying questions):**
- The historic foothold itself — wiki-16's tree/árbol/木, water/eau/
  aqua/wasser, all-σ=½ cross-*natural*-language claim — and the honest
  blind re-run against the unaltered mechanism today
  (`repo_appendix/semantic_prime_hash/001_original_2026-05-27_word_zero_idx.py`):
  **none** of those groups share an `idx` under the live code.
- `VAPMIP/prime_hash.py` (2026-08-18, never wired into the live pipeline)
  names the U+200B bug precisely as a tier-0/tier-1 category error and
  designs — but does not ship — a fix (`split_tiers()`).

## 4. Why primes at all — the domain, grounded
> notebook 02: the sieve and un-sieve code, 313/49999 derived from
> p²≤N/2p≤N directly in code, not asserted.

**`notebooks/02_the_313_sieve_and_49999_unsieve.ipynb` — 10 cells,
checked.** Matches exactly: `GenerationalLineage/engine/lineage.py::un_sieve`
gives both boundaries; cells 3 and 5 *independently* re-derive them by
direct arithmetic (`max(p for p in primes if p*p<=N)` = 313,
`max(p for p in primes if 2*p<=N)` = 49999) rather than trusting
`un_sieve()` alone — both agree. `D == reverse(A)` exact; entropy gap
≈7.19 bits. One extra thread (zeta-ordered birth narrowing the gap ~15%)
is referenced from `RiemannHypothesisProof/ADDENDUM...md`, not reproduced
here — a real "at scale" test still to run, not this notebook's job.

**Corrected, Cody (2026-09-19): section 4 is ONLY the 313 sieve finding
— nothing else.** `VAPMIP/lineage_hash.py`/`monad_identity.py` (the
65-prime-pool, frequency-order, Fermat-generation machinery flagged in
the previous draft) are **superfluous here** — not notebook-wrapped, and
not what Cody actually built the "65 primes are letters" realization on.
Corrected history: 313 answers a question asked plainly — "what is the
last prime to see any new factors come down in the sieve" (= the highest
prime factor ever required to build any composite in the domain) — and
that number is what resolved an open ambiguity (primes as *words* vs.
primes as *letters*) into a decision: the first 65 primes are letters,
which sets up an orderly, mostly-collision-independent spelling hash —
leading directly into §5. My own earlier inference — that 313 was chosen
to *also* satisfy `lineage_hash.py`'s Fermat-generation-window framing —
was **wrong**; Cody: "313 was not ever in the planning." Drop that
connection entirely.

**Restructured, Cody (2026-09-21): §4 split into 5 subsections.** 4.1
introduces the Two Trees Engine (names only, no wider-scope claim); 4.2
defines Laurelin as the factors domain, with the Fermat/Riemann
distinction stated as reported fact ("Fermat defines the primes by
extinction of every possible factor; Zeta only describes their order of
arrival") — no claim about 313 itself, that correction above still
stands; 4.3 defines Telperion as *this paper's* Riemann prime-zeta-zero
tree (the ≤313 letters that address via π(p)→γ, §3), explicitly not the
same-named zero-divisor tree used elsewhere in the project (§9–§11); 4.4
is the original 313 derivation; 4.5 is the composite/factoral-primes
closing content, unchanged. PDF not regenerated yet — holding per Cody's
instruction until editing is finished.

**Terminology, now precisely defined and verified exactly (not
approximately) against `_spf_gpf_tables(100_000)`:** Cody's correction —
"factoral primes are the ones that contribute to Laurelin. composite
primes are telperion factors... the factors exist in telperion alone."
Checked directly over every composite `≤10⁵`: `max(spf) == 313` with no
exception, and all 65 primes `≤313` get used as an `spf` — Telperion's
alphabet is exactly, completely, and only those 65 (**composite
primes**). 5,068 primes, exactly the range `(313, 49999]`, appear as a
`gpf` and **never once** as an `spf` — Telperion is permanently blind to
them; only Laurelin ever accounts for them (**factoral primes**). This
is what actually grounds "the first 65 primes are letters": not merely
"last prime with new striking work" but the complete, closed,
exhaustively-verified set of every possible smallest-factor identity in
the domain.

49999 (Laurelin's/birth boundary) gets one honest sentence, not
developed — informational color for number theorists/physicists, per
Cody's instruction, not load-bearing for this paper.

## 5. Spelling → prime
> notebook 03: LETTER_PRIMES (20, ≤71) with the code that builds it, naive
> product scheme's code + its collision, then spelling_code/spell_decode
> and the round-trip numbers.

**`notebooks/03_phonetic_prime_hashing.ipynb` — 12 cells, checked.**
Matches exactly: naive 26-letters-one-prime-each product scheme (cell 2),
its anagram-blindness demonstrated directly (`cat`==`act`,
`listen`==`silent`, cell 4), then `wordnet_boxkite.py::spelling_code`
(20-prime Gödel-positional tier, `LETTER_PRIMES ≤ 71`) fixing it (cells
6–8), then measured on a live 30,000-word sample (cell 10): exact
recovery %, split `≤20` vs `>20` letters (the tier-wraparound lossy case).
Draft: `draft_section_05.md` — scoped exactly to the ordering/anagram
issue per Cody's instruction, real numbers from the notebook's own
recorded cell outputs (710/1914801911 collisions; 95.290% overall,
96.745% on ≤20-letter words). One open flag carried into the draft: §4's
65-prime pool vs §5's shipped 20-prime tier don't match in size — asked
Cody whether 65 is meant to become the tier eventually or is a separate
fact about the domain.

## 6. How `monad3_c.bin` learns WordNet
> **(new)**: dump_boxkite_bin.c + boxkite_bin.h's packed struct,
> wordnet_boxkite.py's Python-side twin, the cross-language verification.

**Re-scoped and finalized, Cody (2026-09-20): "pigeon-holed to WordNet
only."** Section 6 = strictly how `monad3_c.bin` was built to carry the
19D WordNet relationships — `dump_boxkite_bin.c`/`boxkite_bin.h`/
`wntest.c` (build + cross-check) and `monad_combine.py`'s
`read_boxkite_c`/`CombinedMonad`/`write_c` (folding it into the combined
file, confirmed union of english/wordnet/phonetic vocab). Explicitly
**excluded**: bootstrap/bulk ingest (`ingest.c`, `build_monad_bin.py
merge`), the filesystem-ingestion/`.bin`-poisoning experiments, and the
vocabulary-update law's formulas (`monad_learn_ex` in C /
`Crank.learn` in Python — two *different* laws, not twins) — mentioned
only as "the store keeps growing," one line, no code. `phon:` checked
directly and confirmed to have **no WordNet wiring** (built from
`nltk.corpus.cmudict` alone) — one-line mention only. Draft:
`draft_section_06.md`.

**Notebook 06 should be a C-kernel notebook (Cling/Clang-style), not
Python** — per Cody: "the Monad and the Monad Harness [are] strictly C
these days," Python monads are for testing/CS-paper enumeration only.
This section's real mechanism (`dump_boxkite_bin.c` etc.) is native C;
the companion notebook should run it directly rather than restate it in
Python. Saved to [[project-ptolemy-monad]] and [[project-oblique-gear]]
(the `Crank`/TDI/Wankel naming history, tangential but real, kept out of
this section per scope).

**Notebook 06.5 built (2026-09-20)** —
`notebooks/06.5_monad3c_update_mechanism.ipynb`, real C-kernel notebook
(`jupyter-c-kernel`, project's own established convention —
`VAPMIP/notebooks/c/install_c_kernel.sh`), every cell actually compiled
+ run with `gcc`, not asserted. Covers the update mechanism itself
(`monad_learn_ex`'s β law / `prose_seen` ladder / A-matrix coupling,
real constants from `ptolemy.h`) and only what the daemon *sends* to
trigger it, not daemon internals — per Cody's instruction. Two real
anomalies found by running it, both flagged in `draft_section_06.md`
§6.5: `MONAD_BETA_SAT=7.552` vs. `SPEC.md`'s stated `(0,1]`; and the
`prose_seen` ladder's order-dependent asymmetry (WordNet→prose reaches
"verified", prose→WordNet does not). Source `.c` files archived in
`repo_appendix/monad3c_update/`.

Original (superseded) research, kept for the source-file references it
still gets right:
- `VAPMIP/PtolC/boxkite_bin.h` — the packed `BoxKiteEntry` struct (19
  `int16_t` relation exponents + `depth_weight`), documented as the same
  schema as `wordnet_boxkite.py`'s Python side, "two different
  serializations of one schema, not two different schemas."
- `VAPMIP/PtolC/dump_boxkite_bin.c` — builds `c_monad_wordnet.bin` by
  reading WordNet's own `index.noun/verb/adj/adv` files directly (not a
  library iterator — `getindex()` is fuzzy search, not enumeration, per
  the file's own corrected comment) and calling the real C WordNet
  library (`index_lookup`, `read_synset`) per word, first sense only.
  `compress_count` is ported verbatim from the Python file.
- `VAPMIP/PtolC/wntest.c` — the actual cross-check, 2026-08-25: `bank`'s
  first noun sense gives `HYPERPTR=1, HYPOPTR=2` from the real C library,
  exactly matching Python's `{'hypernyms':1,'hyponyms':2}` for
  `bank.n.01`.

**⚠ Important clarification, in case it reads the other way:** "cross-
language" here means **C implementation vs. Python implementation of the
same schema**, verified to agree — nothing to do with the natural-
language (English/French/Chinese) claim in item 3. Flagging this
explicitly since the two easily get conflated under one word.

## 7. Context → prime, and the combined address
> notebook 05: RELATION_METHODS, compress_count, context_code, the gamma
> fold, then next_prime(spelling_code × context_code) — the actual
> deliverable, verified.

**Drafted (2026-09-20): `draft_section_07.md`.** Scoped per Cody: "this is
The WordNet section... the code here is just the 'reading' mechanism of
`monad3_c.bin`'s WordNet relationships... as they will be used directly
in the boxkite section later" — so §7 stops at `gamma_radial`/
`context_code`, explicitly not developing the pencil/box-kite consumption
(that's §9/§10 now). One flag found reconciling real recorded notebook
output against the current prose README: the notebook's own cell 9 run
says **286/286** exact combined round trips; `README.md` §7 currently
states "300/300" — stale, needs reconciling.

**Resolved (2026-09-21):** `README.md`'s three "300/300" mentions
(§7, §9 notebook table, G1 gate) corrected to **286/286** to match the
notebook's own recorded run, which is authoritative. §7's `Flag` note
removed from `draft_section_07.md` now that the two agree.

**`notebooks/05_wordnet_19d_contextual_hash.ipynb` — 13 cells, checked.**
This is the paper's actual shipped result. `context_vector`→`context_code`
exact factor-back on real data; the `gamma_radial` tanh/atanh fold
(rel. err ~1e-16, 0 collisions on a 20k sample); confirms
`LETTER_PRIMES`/`CONTEXT_PRIMES` are disjoint by construction (boundary at
prime 71); then the combined `next_prime(spelling_code × context_code)`:
**300/300 exact full round trip** (spelling + full 19D context, recovered
from one prime), plus one fully worked example end to end.

## 8. Cost, measured
> (keep — energy_bench.py, concrete flop counts, this is exactly
> Fast-Inverse-Square-Root-flavored content).

**Drafted (2026-09-20): `draft_section_08.md`.** Scoped narrowly per
Cody: not "backprop is wrong" (it remains the right tool for OCR/CNN-
class problems) but "backprop is a hard wall for training on a laptop,"
a compute-accessibility claim, not a correctness one. Cites the
established gradient-descent/curvature-blindness critique (Newton's
method, natural gradient, saddle-point literature) properly, then the
real historical precedent with *zero* cost function at all — the
Zork/Infocom static-lexicon sentence parser, this project's actual
design ancestor. States plainly that §3–§7's own shipped mechanism
already *is* a forward-propagation machine, cited as such rather than
re-argued from zero-divisor eigenvalue theory (that material — the
`L_a` `{0,±i,±i√2}` split, `J_red`/`J_blue`, the Mind's Eye "Zero
Divisor Reframe" STM promotion gate — is real but VAPMIP/Ainulindalë-
scoped, explicitly kept out per this paper's own "no 0_RB" rule; saved
instead to [[project-minds-eye-papers-hands]]). Anchor kept minimal:
just `e₀` on the Real numberline, already established in §3.2.
**No notebook — and the outline's own parenthetical says keep it that
way.** `engine/energy_bench.py` + `bench/energy_results.txt` already exist
as a standalone script + results file, referenced (not notebook-wrapped)
in current README §12. Read literally, item 8 is asking to keep this as
prose-plus-script, not to build a 6th notebook — flagged in the questions
below so I don't build one you didn't ask for.

## 9. The Pencil — its own section (Cody, 2026-09-19)

**Not folded into the box-kite section.** The Pencil is a separate tool
from the box kite — it's the *theoretical* object, and it's what a
windspeed requires to mean anything at all: without the pencil's
hyperdimensionality, there is nothing for the collapse to collapse. This
section's job is narrow and load-bearing, not exhaustive: demonstrate
just enough of the pencil's hyperdimensional structure to anchor the box
kite so a windspeed actually works — **not** the fuller pathway/portal
exploration from the Boxkite Catalog (that belongs to §11, out of scope
here). Source: `notebooks/04...ipynb` cells 4–7 (`pencil()`, built and
verified this session, 7 factorisations per strut) — the minimal slice,
not the whole notebook.

**The pipeline, Cody's own words (2026-09-20), the spine §9 has to
show:** `windspeed > deformations > static-strut-relationships >
wordnet context relationships > result`. Precisely, with each link
labeled by what's actually built vs. what's target/`THEORETICAL`:

**Windspeed, finalized (Cody, 2026-09-20) — one paper, one windspeed:**
tested two real candidates side by side (script + results below) and the
assignment is now locked:

- **`windspeed_B` = `gamma_radial`, recovered via spelling-division —
  THIS is "the windspeed" for `ScalarContextPropagation`, full stop.**
  Exact, deterministic, needs nothing but the word's text and its stored
  `(full_addr, delta)` — no corpus, no state, no history. That's why it's
  the context-propagation windspeed: it's the one that can genuinely be
  *propagated* (forward, tape-free) rather than requiring a live store.
- **`windspeed_A` = A-matrix basin drift, RENAMED "the Newton basin locus
  contextual flow"** — Cody: "an early tool to determine output... it
  gets to be the constructor windspeed for when we adjust the Mind's
  Eye (different later engineering project)." **Explicitly reassigned
  out of this paper** — belongs to the sentence-constructor/Mind's-Eye
  thread, not here. Do not use it in §9's pipeline; do not call it
  "windspeed" without the "Newton basin locus contextual flow" qualifier
  if it ever needs mentioning as a forward-pointer.

1. **Phonetic prime (spelling), `ESTABLISHED`** — a word's letters,
   preserving order, multiplied into prime-power composites (§5's
   `spelling_code`), "context-less" — recoverable from the literal text
   alone, no WordNet involved.
2. **`w` = `gamma_radial`, `ESTABLISHED`** — recovered exactly via
   `full_code = full_addr − delta`, `spelling = spelling_code(word)`
   (from text alone), `context_code_recovered = full_code ÷ spelling`
   (exact — disjoint prime tiers), then the §7.3 fold. Verified live,
   2026-09-20, not just designed (`/tmp/windspeed_test/test.py` —
   recovery assertions pass, `windspeed_B("tree") = −0.151155`).
3. **`w` applied as a deformation to the pencil-anchored box kite,
   `THEORETICAL`** — `Φ_w(H)`, per `pencil_hyperstring.md`; at a
   *constant* `w` the deformable kites settle to one fixed shape, not a
   moving one. **Partially probed, 2026-09-20** (spectral proxy, not
   the full sail-mechanics geometry — that stays unbuilt, confirmed):
   weighted-Laplacian test on all 7 struts, eigenvectors labeled
   `strut`(`{4,4,4}`)/`sail`(`{6,6}`) per `pencil_hyperstring.md`'s own
   mode mapping. Finding: whether a mode is wind-blind depends on the
   **strut**, not the windspeed (`A` and `B` are blind at identical
   modes on every strut) — strut 4 fully invariant, struts 1/6/7
   partially, struts 2/3/5 fully open. Real result, still a proxy — the
   actual sail-pressure→strut-angle mechanics per Cody's own model
   (sails deform in a constant way, fixing two struts' relationship at
   the crossing) is not what this measures.
4. **Static strut relationships (the fixed crossing points),
   `THEORETICAL`, but now precisely characterizable** — a strut's
   crossing is the fixed point of the order-2 (`J_2`-type) `r↔1/r`
   radial fold at that station, *not* the full order-4 `J_N` (see the
   2026-09-20 J_N-vs-J_2 discussion) — a clean, unique fixed point is
   exactly why a fixed `w` can pin a crossing at all.
5. **WordNet context relationships, `ESTABLISHED`** — §7's
   `context_code`/`gamma_radial`, read off the settled shape.
6. **Result** — a real generated reply; `SpaceClaude/OMFG.png` (§11) is
   the literal first instance of step 6 actually happening.

The missing-middle target, now precisely locatable: step 2 above (the
recovery) is done and verified. Step 3 (`Φ_w`, the actual deformation
law) is the one real open piece — everything before and after it is
either `ESTABLISHED` or newly verified. State
this plainly in §9 as the target, correctly labeled `THEORETICAL`, not
implied to already work.

**§9 drafted (2026-09-20): `draft_section_09.md`.** Written after the full
windspeed-testing arc (§9.1 final assignment), the Native-Space/aperture
corrections (§9.3, now also the `observer-position` skill), the `H`
conservation result (§9.4, real but partial — struts 1/3/6 only, `{1,3,6}`'s
structural reason left honestly open for §11), and the `J_2`-not-`J_N`
crossing proof (§9.5). §9.6 states plainly that the windspeed recovery is
verified in Python but not yet ported to `ptol.c` — the live C touchpoint
today is still just `-M`'s byte-exact struct read (§6). §7 repassed to
match: its closing now states `gamma_radial` *is* §9's windspeed, the same
number, not an analogous one. Checked drafted §3–§8 for stale references
to the corrected framing (`J_N`, `{4,4,4}`, Cartesian) — none found; only
§9 touches this material, so no other section needed changes.

## 10. The Box Kite — de Marrais briefly, the retooling at length

Two very different amounts of space, on purpose. **De Marrais's box
kite** (42 Assessors, 7 octahedra, `{0,4,4,4,6,6}` spectrum) gets just
enough room for a reader to recognize the general shape — established,
cited, not this paper's contribution (`notebooks/04...ipynb` cells 1–3,
`verify_counts()`). Most of the section is **Cody's own retooling of the
box kite as a collapsible graphing utility** — a hyper-relationship
snapshot object that the pencil's windspeed can inflate/collapse, which
is the actual engineering move this paper is making with de Marrais's
established structure. This is where §5/§6 of the current prose
`README.md` (the anchor-and-string reading, §3.2 there) gets rebuilt from
notebook cells instead of restated as prose.

## 11. Future Paths for Research (new — the Boxkite Catalog, scoped out)

**Explicitly out of scope for this paper's claims — a forward pointer,
not a result.** Cody's box kite + pencil, working together (not de
Marrais's box kite alone), produced a much larger catalog of findings
this session — recorded in `VAPMIP/Boxkite-Catalog.txt` — that belong
here, named but not developed: the anchor to the Real axis, the sedenion
zero-divisor portals, the fuller pathway enumeration through the pencil,
and the 21-member subgroup that connects every strut while preserving
zero-divisor structure — **renamed, from now on, the "Blackjack
subgroup"** (21 elements; `2026-08-13_apex_path/psl27_strut_action.py`,
verified 2026-09-17). Findings above and below the sedenion zero-divisor
locus plane are real and were "incredible," in Cody's words, but **this
paper propagates only the 19D WordNet relational data** — the sentence
parser/constructor's move into the box kite, and the fuller "speaking
English" program the Boxkite Catalog opens up, are a separate, later
paper. This section exists so that future work has a named place to
start from, not so this paper's scope creeps to match it.

**Two descriptions, named (2026-09-25): "Collapsible Context" (Method 1)
and "Collapsible System Monitor" (Method 2) — and they are `J_red`/`J_blue`,
checked against the Halocline table (`02b_the_halocline_j_blue_j_red_h_hat_
rb.md`), not asserted by analogy.** Method 1's first step (word → γ) is
discrete-to-discrete, injective, conserved — `J_red` (incompressible,
Noether-conserved, "what IS"). Method 2's first step (state → scalar) is a
genuine `ℝ¹⁵ → ℝ` collapse, lossy by construction — `J_blue` (compressible,
zero-divisor-bearing, "what CANNOT BE"). Load-bearing distinction: what a
live system perceives first (the alert/scalar, Method 2's collapsed output)
is never what caused it (the 15-dimensional state, which existed first and
drove the collapse) — the perceived order and the causal order run opposite
for Method 2 specifically (not Method 1, where they coincide). Causality
always wins regardless of which one announces itself first to an observer;
same discipline as this project's forward-propagating-maths rule — never
reconstruct backward from what was perceived, the generative direction is
fixed independent of arrival order.

**Correction, tested 2026-09-25 (`repo_appendix/windspeed_reconstruction/
08_rate_conservation_all_struts.py`, already-built code, run for real —
not new maths): `H = Re(Π)` conservation is NOT universal across the
box-kite.** It holds exactly (spread `~1e-16`, machine precision) on struts
**1, 3, 6** under the correct pencil-ordered rate law — and genuinely fails
(spread `0.4`–`1.8`) on struts **2, 4, 5, 7**, same rate law. A uniform-rate
control conserves on none of the seven. So "Method 1 = `J_red`, conserved"
overstated it: conservation is real but **conditional on which strut**, not
a blanket property of the method. Which three struts hold, and why `1,3,6`
specifically — no obvious parity or XOR pattern found at a glance — is a
genuine open question this run surfaces, not one it answers. The `J_red`
identification stands for those three struts; it does not stand as stated
for the other four, and the paper should say exactly that, not round up.

**3) The dual scalar box-kite structure — de Marrais's and Cody's, both
present, one object not two (2026-09-25).** Per §10 above: de Marrais's
box-kite is the static skeleton (42 Assessors, 7 octahedra, established,
unchanging); Cody's retooling is that same skeleton read as "a collapsible
graphing utility... the pencil's windspeed can inflate/collapse" — already
named, in §10, as this paper's actual engineering move, before Method 1 or
Method 2 existed. Reframes both new methods precisely: Method 1 and Method
2 are not two different box-kites, they are **the same de Marrais skeleton
under the same Cody collapse/inflate operator, driven by two different
scalars** — `γ` (content) for Method 1, the system-monitor anchor for
Method 2. One static geometry, one dynamic operator, two signals. (Grounded
against §10's own wording, not asserted fresh — flag for correction if a
different pairing was meant; the source message trailed off before
specifying one.)

**Method 2 (BUILT — first pass, 2026-09-25) — collapsing a 15-channel
system monitor into a single scalar that reconstructs the pencil-attached
box-kite location. "The box-kite grabbing the anchor side."** Real code,
run against live system data, not just named:
`PtolemyDesktop/Aule/system_boxkite.py`. Two real bugs caught and fixed by
running it — counters fed in raw instead of as rates (windspeed read as
frozen for hours against real activity), and process/thread-count
reference scales saturated regardless of load. One real degeneracy found
and left open, not smoothed over: the first-pass `e₀ := RMS(15 imaginary
channels)` formula makes `fixed_point_weight` **algebraically constant at
exactly 1/16** for any nonzero input (`e0²=Σxᵢ²/15 ⟹ e0²/(e0²+Σxᵢ²)=1/16`
identically) — not a live signal under this formula, a genuine open item
for whichever formula replaces it. Method 1 (this
paper's actual content) runs content → scalar → pencil: a word/token is
the input, the box-kite is built forward from it. Method 2 runs the
opposite direction: a live system-monitoring vector (15 channels — CPU,
memory, disk I/O, network I/O, process/thread counts, load×3, context
switches — one per imaginary sedenion component, `e₁..e₁₅`) is embedded
as a 16-vector with a derived real/anchor component (`e₀`, `fixed_point_
weight(ψ) = ψ[0]²/|ψ|²`, never an independently-measured 16th channel —
its kernel is provably all-imaginary, `Null-Space-of-the-Zero-Divisor`).
The anchor's continuous companion (`local_curvature(ψ)`, the already-
named "A-Matrix Basin Windspeed," `box_kite.maths`) is watched for a
*collapse* — a jump between windspeed regimes, the same kind already
observed once, unprompted, between struts 1–3 and 4–7 in this repo's own
work. At a collapse, `nearest_assessor(ψ)`/`chart_projection(ψ)` reads
off the discrete point `r ∈ 1..15` the state has landed nearest to, and
`pencil(r)` returns that point's exact 7-pair bundle — sent onward as the
coordinate a live "PtolKernel" needs to look at the same location in its
own internal box-kite.

**Terminology, corrected before this got written down wrong:** the
16-vector itself is exactly a **sedenion** — no hedge needed, that's what
a 16-component Cayley–Dickson element is. "Functor" is not the right word
for the collapse step, and shouldn't go in the paper as one: a functor is
a structure-preserving map between two *categories*, preserving
composition of morphisms — no such categorical structure (objects *and*
morphisms on both sides) has been set up here. What's actually happening
is a **projection/collapse** (`ψ → r`, lossy, many-to-one — many different
system states can land on the same point) composed with a **deterministic
lookup** (`r → pencil(r)`, exact, lossless, the same `r` always returns
the same 7 pairs). Say precisely what reconstructs and what doesn't:
`pencil(r)` reconstructs the *canonical structure at the point the state
collapsed to* — not the original 15 raw channel readings, which the
collapse genuinely and irreversibly discards. Overclaiming "reconstructs
the multidimensional information" would not survive the same scrutiny
this paper already applies to its own Method 1 claims.

### Aulë Face report specification — "system boxkite"

Aulë's reports for this method are two shapes, both real, both drawn
directly from the running code, not designed on paper first.

**Channel map** (the 15 imaginary components, `e₁..e₁₅`, `PtolemyDesktop/
Aule/system_boxkite.py::CHANNELS`):

| index | channel | note |
|---|---|---|
| 1 | `cpu_percent` | instantaneous |
| 2 | `mem_used_percent` | instantaneous |
| 3 | `mem_available_percent` | instantaneous |
| 4 | `swap_used_percent` | instantaneous |
| 5 | `disk_read_bps` | rate — delta'd against previous sample, not the raw counter |
| 6 | `disk_write_bps` | rate |
| 7 | `disk_iops` | rate |
| 8 | `net_recv_bps` | rate — **excluded from every Assessor** (`e₈` is the CD doubling generator, box_kite.md); invisible to `chart_energy`/`nearest_assessor` though it still counts toward `norm()` and `local_curvature`'s candidate pool |
| 9 | `net_sent_bps` | rate |
| 10 | `process_count` | instantaneous |
| 11 | `thread_count` | instantaneous |
| 12–14 | `load1`/`load5`/`load15` | normalized by core count |
| 15 | `ctx_switches_per_sec` | rate |

`e₀`: derived, never measured — see the RMS degeneracy above.

**Live State Report** (poll interface, `get_live_state()` — instant,
never triggers new sampling; the watcher thread updates it continuously,
default 1s interval):

    {
      "timestamp": <float, unix time>,
      "raw":       {<channel name>: <rate-converted value>, ... 15 entries},
      "vector":    [e0, e1, ..., e15]   # 16 floats
    }

**Collapse Report** (Aulë event, channel `"system_boxkite"`, type
`"collapse"`, fired when `|z_score| >= 3.0` against a 30-sample rolling
window of `local_curvature` — first-pass threshold, not tuned against
real incident data, OPEN the same way the windspeed-regime finding it's
built on is OPEN):

    {
      "point":              <int, 1..15 — nearest discrete point>,
      "pencil":             [[a, b], ... 7 pairs] | null,
      "windspeed":          <float — local_curvature reading that triggered this>,
      "z_score":            <float>,
      "fixed_point_weight": <float — currently always 0.0625, see degeneracy above>,
      "nearest_assessor":   [a, b]
    }

Status: **BUILT, first pass, self-tested against live data** — not a
conversation-stage design anymore, unlike the Blackjack subgroup entry
above it. Two bugs fixed, one degeneracy found and left honestly open;
next real step is a replacement `e₀` formula and a validated (not
first-guess) collapse threshold, not a rewrite of what's here.

**Closing image (Cody, 2026-09-20): `SpaceClaude/OMFG.png` goes at the
very end of §11**, the paper's last real content before §12. Real
screenshot, not staged — the first run of the box-kite context monad
(`RotaryBoxKiteMonad`), asked a deliberate trick prompt with no prior
turn to refer to: `"what were we talking about?"`. Real reply: `"it
includes conversation, confuse, and yak."` — a genuinely decompositional
answer to an unanswerable question (three words directly on-topic for
"what is a conversation," including an honest thread of confusion, not a
refusal or a hallucinated fabricated topic). Caption should say plainly
what it is: the real first output of this machinery, kept exactly as it
happened, including the "confuse" — not cleaned up to look more
impressive than the actual first result was.

## 12. Provenance, attribution, licensing, citations
> everything currently scattered as inline subsections, moved here as one
> section.

**Not a notebook — an editing/consolidation task** on material that
already exists scattered across current `README.md` §0 (labels), §2.2
(disambiguation), the provenance column of §8's table, §15 (licensing),
and References. No new research needed, just relocation into one closing
section.

---

## Production plan — how to build the notebook-form paper without redoing work

The real *Annotated Transformer* is a single `jupytext`-paired script (a
`.py` with `# %%` cell markers, kept in sync with the `.ipynb` it
executes to) rendered to a static page. Our situation differs in one way
that matters: we already have **5 independently-written, independently-
verified notebooks**, not one linear draft. The plan respects that —
copies verified cells in, does not re-derive them:

1. **One master notebook**, `PAPER.ipynb`, cell order = the 12 items
   above, built incrementally, one section's notebook at a time — not
   all at once. Items 3–5, 7, 9, 10 pull from the existing notebooks'
   cells, copied in verbatim (markdown cells become the paper's prose,
   code cells stay real and runnable) — not paraphrased, not re-typed as
   formulas; §9/§10 pull only the relevant slice of notebook 04 (pencil
   cells 4–7; established box-kite cells 1–3 plus the retooling write-up),
   not the whole notebook. Items 1, 2, 8, 11, 12 are prose (§11
   deliberately a forward pointer, not code-backed, since it's out of
   scope for this paper).
2. Pair it with `jupytext` to a `.py` (percent format) so the paper has a
   diffable plain-text source, same mechanism `nlp.seas.harvard.edu`
   uses — confirmed directly this session, not assumed.
3. Item 6 needs a **new** notebook 06 written first (§6 above — the
   `dump_boxkite_bin.c`/`boxkite_bin.h`/`wntest.c` material has never been
   notebook-wrapped), then folded into the master the same way as the
   other five.
4. Item 8 stays a script + results file, referenced by path — per its own
   "(keep...)" wording, not converted.
5. Before publishing, **re-run the whole master notebook top to bottom in
   one kernel** — the individual notebooks were each verified separately;
   a single coherent execution is the actual reproducibility bar this
   project already holds itself to elsewhere (G4's determinism gate,
   G7's clean-checkout gate).
6. Render `PAPER.ipynb` → `README.md` (or a page) via `nbconvert`, the way
   this project already treats notebooks as "the executable form of every
   result in this paper" (current README §2.3) — just now literally, cell
   for cell, instead of paraphrased into prose above them.

This does not throw away the current prose `README.md`; it's a genuinely
different artifact (convention A/software-paper-adjacent vs. convention
B/literate). Whether both should exist, or the notebook form replaces the
prose form, is one of the questions below.
