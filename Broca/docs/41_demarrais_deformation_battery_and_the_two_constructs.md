## Phase 41 — The De Marrais Deformation Battery, and the Two Constructs Compared (2026-10-12)

*Claude Sonnet 5.5. A measurement session, not a build: no engine file changed. Everything
below was computed in `.claude/scratchpad/2026-10-12_demarrais_deformation_battery/`
(`cdalg.py`, `part1.py` … `part5.py`, captured `output_*.txt`; mirrored to `ContextPlease/`).
The ESTABLISHED half — what the sedenion algebra itself does — is recorded in
`VAPMIP/marrais_boxkite_catalog.txt` §11–15; this page records the comparison with the two
constructs. Observer-position stated up front: **orientation** — each Assessor read as the native
complex pair `(d₊, d₋)`, anchor at e₀/e₈; **aperture** — exact symmetry groups AND continuous
flows/tangent analysis at all 84 diagonals, plus generic prompt vectors, never only lattice picks.
One test was re-run because its first aperture was degenerate (see §3).*

Prompted by Cody: *test the De Marrais box kite for deformations — what kind of functions cause
what deformations — starting from the Walsh and Sylvester–Hadamard definitions, with operators,
operations and the Universal Native Space constants; then test the same in both constructs and say
whether the deformations of his choosing and the maths are the same.* Constants supplied: π, φ,
ln 10, "all four versions of d\*", i, e, 0, 1, "etc." (see §6 for what was and was not testable).

---

### 1. The shape of the answer

The De Marrais kite has three kinds of deformation, and nothing else:

| Kind | What it is | Evidence |
|---|---|---|
| **Exact** (every ZD relation survives) | G₂ flows (14 parameters); multiplication by `exp(θ e₈)`; the finite group of order 2,688 = (ℤ/2)⁴·GL(3,2), whose 16 sign factors are exactly the Hadamard rows; scalings; conjugation | tangent space of the ZD-pair variety at all 336 pairs is exactly 14 + 2 (scalings); flows to t = 2.5 hold to 1e-15 while diagonals move 48° off their lattice lines |
| **First-order tear** | everything else, at a rate set by the singular values of `x → xy` (√2 or 2) | in-plane rotation off a diagonal tears at exactly 2.000/radian; dense WHT keeps 0/336; random orthogonal keeps 0 |
| **Algebra deformation** | change the doubling parameter μ | positive real c: isomorphic, kite tilts to κ = 1/√c; +c split: half the adjacency; 0: collapse; i: degree 6 |

### 2. Walsh and Hadamard, specifically

- As **sign-flip operators**, the 16 Hadamard rows are exactly the automorphisms among all 65,536
  diagonal sign operators: zero deformation.
- As **perturbation directions**, every row is uniformly transversal: response `√2·|δ|` against all
  84 annihilators (min = mean = max).
- As the **dense transform** (WHT), the kite is destroyed (0/336 pairs survive).
- As the **tension-law sign patterns** (Phase 40) they are rows 0–3 on the station index.
- As **ptol.c's Γ**: the J_red/J_blue partition *is* Hadamard row 4. `Γ = Σ χ₄(k) v_k² / |v|²`,
  agreeing with the printed Γ to 1e-10 on four prompts. The other 14 non-trivial Walsh coefficients of the
  energy distribution are computed by nothing today.

### 3. Functions of the native pair

For `z = d₊ + i d₋` and a diagonal `x` at magnitude λ ∈ {0.3, 1, 2.5} (λ = 1 alone is degenerate for
`z²` and the Möbius map — the first run used only it and over-reported; corrected):

| f | keeps d₊ line | keeps d₋ line |
|---|---|---|
| Joukowsky `z + c/z` (c = Ω_ZS), `z²`, `tanh(z/2)`, `1/z`, conj, `z·i` | yes | yes |
| `exp(z)`, Möbius `(z−1)/(z+1)`, real shift | yes | no |
| imaginary shift | no | yes |
| generic in-plane rotation `z·e^{0.3i}` | no | no |

### 4. The Universal Native Space constants as the doubling parameter

μ₄ = −c with c > 0 leaves the combinatorics untouched (168 plane-pairs, degree 4, within-chart)
and tilts every vertex to κ = ±1/√c. Constants tested: 1/2, √2, 2, e, π, φ, ln 10, Ω_ZS, d\*, d\*_spec,
GAP; κ values in `marrais_boxkite_catalog.txt` §14. The 0.24631 versus 0.24600 difference between
d\* and d\*_spec shows up as κ = 2.0149 versus 2.0162. μ₄ = 0 collapses the kite (1,764 plane pairs).
μ₄ = ±i gives 252 pairs, degree 6, complex slopes (±1 ± i)/√2. An apparent anomaly at c = GAP (537
pairs) was a tolerance artifact and vanishes at tolerance 1e-14.

As a rotation angle θ = c rad of a diagonal in its plane, the defect is zero at π/4 + nπ/2; ln 10 rad
lands 0.054 rad (3.1°) from 3π/4 (defect 0.107, the smallest of the set). With 13 constants and a 90°
period a near-miss of that size is expected by chance (≈ 60% that some constant is within 3°), so it is
recorded, not chased.

### 5. The two constructs against the maths

**Scalar construct (pencil hyperstring / Gamma-Radial).**
- *Not the same object.* `Π(φ)` is never a zero divisor (0 of 13 points on each of 6 pencils; it acts
  isometrically against all 84 diagonals). `H` is a property of a product that lives near the real axis.
- *Not the same deformations.* A station flow inside an Assessor plane is transversal (rate 2.000/rad);
  the kite's exact deformations are G₂ flows and `exp(θ e₈)`.
- *Pencil convention.* The paper's `pencil(r)` for strut `r ≤ 7` contains **no** Assessor plane. The
  Assessor planes of strut `s` are six of the seven stations of `pencil(s+8)`. On those pencils the
  one-phase tension law holds only for strut 1; for struts 2–7 `H` depends on 4, 4, 5, 5, 5, 5 phase
  combinations. **This qualifies Phase 40**: the tension law is a statement about the paper's pencil, not
  about the Assessor-plane geometry. (Cause not found; not alternativity, not associator counts.)
- *Where they agree.* The sign patterns ε are the maths' own automorphism characters; `H(0) = −1` is
  derived from `e_a⁻¹e_b = ±e_r` and `∏ e_a = −1`.

**Scaled construct (live address / A-Matrix).**
- *Agrees.* Every lens reading is exactly covariant under all 168 frame-preserving index maps
  (`local_curvature`, `outside_share`, `fixed_point_weight` invariant; `chart_energy` permutes by
  `s → A(s)`) on all four prompts; under 300 random permutations they are unchanged in 0–1 cases.
- *Does not carry topic.* On 16 prompts in 4 subjects the projected address separates nothing:
  inter/intra distance 0.94–0.95, leave-one-out 1-NN 0.06–0.19 (chance 0.25), for the 7 chart energies,
  the 15 Walsh coefficients, the 16 energies and the 16 amplitudes. The idea-carrying shape has to be
  composed from the words (pencil index, `w`, `vec19`, basin pull), not from projecting the string.
- *Kernel fiber.* `throw_fiber` writes `psi[a]` and `psi[b]` for the first Assessor `(a,b)` — but an
  Assessor is the plane `(e_a, e_{b+8})`. As written the nearest Assessor is `(2,1)` instead of `(2,3)`
  for strut 1, and for strut 5 the dominant chart is 2, not 5. With `e_{b+8}` the chart and Assessor
  match the intended strut. **Not changed.** *(Retracted as a defect on 2026-10-13: `span{e₀,e_a,e_b,e_s}` with `s = a⊕b` is a closed quaternion subalgebra — emerger domain ℍ — while the Assessor pair is a FRAGMENT; the as-written fiber is a coherent object in a different bracket. See the consolidated record.)* Also, the `depth` parameter's `√(1−d²)·e₀`
  admixture takes the vector off the ZD surface for every depth < 1, so `is_zero_divisor` can only read
  True at depth exactly 1.0.

### 6. What was not testable, and what was added

- **d\*_RG** ("The Stability", the renormalisation-group face) has no closed form per the canonical-maths
  file; there is no value to plug in, so it was not tested.
- **d\*** and **d\*_taut** are the same number (0.24631) and give identical results; **d\*_ln(10)** is
  Ω_ZS = 0.56714; **d\*_spec** ≈ 0.24600 is the separately measured fifth quantity.
- Added to the list: √2, 1/2, 2, GAP, Ω_ZS. `i` was used as a complex μ₄ and as a phase scale
  (`−cos(iS) = −cosh S`, which leaves [−1, 1]); `0` and `1` as μ₄ (degenerate; standard/split), as angle
  and as phase scale.

### 7. What this means for "one part of the idea at a time"

A hypothesis, not a result. The exact live degrees of freedom of the kite are the 14 of G₂, nested:
placing one vertex uses 11 (stabiliser 3), and that stabiliser still moves its 4 partners (rank 3). A
sentence-building process that fixes one part and lets related parts move would act through exactly
such a chain; whether the words' data can drive it is untested. The 15 unused Walsh coefficients
and the Hadamard-row structure of the tension law are the natural 16-channel readout for the oscilloscope
idea; also untested.

### Open items

- Decide whether the kernel's `throw_fiber` should use `e_{b+8}` (Cody's call; one-token change).
- Re-derive why the single-phase law holds for pencils 1–9 and not 10–15.
- Compose a live kite from the pool's tokens (pencil index, `w`) and run this battery on *that*.
- Which quantity is the A-Matrix windspeed (Phase 40 open item), now with the added fact that a
  scalar can only deform along one phase while the exact deformations are 14-dimensional.
- Paper `ScalarContextPropagation` §9.4/§10 (branch) not edited.

### Addendum 2026-10-13 — see the consolidated record

Everything in this page, the Phase 40 page, and the four scratchpad folders is now in one document:
`VAPMIP/docs/wiki/Boxkite-Deformation-Record-2026-10-12.md` (with raw outputs). New there: the Blackjack subgroup
(F₂₁ = the 21 sign-free automorphisms), the {4:8:4} grading of a zero divisor (edges = the null block; the isometric 8 is a
sub-octonion; ptol's J_red/J_blue is u = 4), bracketing and firing order (the tension law's one-phase form depends on both),
and the four d\* / three Lambert-W interaction (the three W values are the three classes of the doubling parameter).

