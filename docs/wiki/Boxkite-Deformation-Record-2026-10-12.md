# Boxkite Deformation Record — 2026-10-12 / 13

**One document, everything.** This page records every experiment run in the 2026-10-12/13 session on how
box kites deform: the four scratchpad experiments, the De Marrais deformation battery (parts 1–7), the
follow-ups on the Blackjack subgroup, the {4:8:4} grading and bracketing/firing order, the comparison of
Cody's two constructs with the maths, and a log of every statement that was corrected along the way.
Raw captured output of every script is appended verbatim (Appendix). The ESTABLISHED (algebra-only) facts are
mirrored in `VAPMIP/marrais_boxkite_catalog.txt` §11–18; the project-side results in `VAPMIP/Boxkite-Catalog.txt`
§15–17; the narrative phases are `Tuning-the-Engine/40_*` and `41_*`.

*Claude Sonnet 5.5, working with Cody. Nothing in any engine file was changed. Everything here is a measurement
or a computation; interpretations are labelled.*

---

## 0. How to read this

**Evidence labels.** **[MEASURED]** — computed by a script in the scratchpad, output captured below.
**[DERIVED]** — follows by algebra from measured facts, step shown. **[HYP]** — a hypothesis; the test that would settle
it is named. **[LIT]** — from the published literature, not re-verified here. **[CORRECTED]** — an earlier statement in
this session that was wrong or incomplete; see §11.

**Observer-position (stated before computing, per the project skill).** *Orientation:* every Assessor is read as the
native complex pair `(d₊, d₋)` = `((v_a + v_{b+8})/√2, (v_a − v_{b+8})/√2)`, anchored at e₀/e₈ (the only indices in no
Assessor); the 16-vector is storage. *Aperture:* exact finite groups **and** continuous flows/tangent analysis at all 84
diagonals; generic prompt vectors and random phase vectors, never only lattice picks; one test (the function-of-pair table)
was re-run at three magnitudes because its first aperture (unit magnitude) was degenerate.

**Algebra implementation.** A stand-alone Cayley–Dickson product with a parameter μ at each doubling level,
`(a,b)(c,d) = (ac + μ d*b, da + bc*)`, μ = −1 at every level = the standard sedenions. It reproduces
`ValaQuenta.modules.box_kite.maths.multiply` on all 256 basis pairs and 50 random vector pairs (0 mismatches).

## 1. Artefact index

| Folder (under `.claude/scratchpad/`, mirrored to `ContextPlease/claude/scratchpad/`) | Script → output | What it computed |
|---|---|---|
| `2026-10-12_windspeed_deformation_proxy/` | `test.py` → `output.txt` | The paper's tension proxy `H = Re(Π)`: baseline swing per strut, per-station response, non-uniform wind, gusts, and the exact fit `H = −cos(Σεφ)` |
| | `test2.py` → `output2.txt` | Are the ε the Sylvester–Hadamard rows (and for which pencils); anchoring (128 subsets); continuous/semi-continuous/discrete regimes |
| `2026-10-12_pencil_tearoff_test/` | `test.py` → `output.txt` | The conjectured "w ≫ w\* tears the kite off the ZD surface" under the literal Joukowsky law |
| `2026-10-12_projected_address_lens/` | `probe.py` → `output.txt` | ptol.c's projected prompt address read through `chart_of` |
| `2026-10-12_demarrais_deformation_battery/` | `cdalg.py` | the parametrised Cayley–Dickson algebra |
| | `part1.py` → `output_part1.txt` | baseline, characters, all 65,536 sign operators, monomial automorphism group, derivations, ZD-pair tangent space, annihilators, Walsh probes |
| | `part2.py` → `output_part2.txt`, `part2b.py` → `output_part2b.txt` | operator battery on the 336 pairs; in-plane rotation; μ-scan with the UNS constants; multiplication by exp(θe_t); constants as angle and as phase scale; GAP tolerance check |
| | `part3.py` → `output_part3.txt` | scalar and scaled constructs against the maths (its CS-04 table is superseded by part 5) |
| | `part4.py` → `output_part4.txt` | G₂ flows of the whole kite |
| | `part5.py` → `output_part5.txt` | function-of-pair table at three magnitudes; topic separation of the live readings |
| | `part6.py`/`part6b.py`/`part6c.py` → `output_part6a/b/c.txt` | Blackjack subgroup; {4:8:4} blocks and edges; bracketing and firing order; the kernel fiber as a bracket |
| | `part7.py` → `output_part7.txt` | pencil convention, gradient ranks, alternativity/associator negatives, the mechanism of the law |
| | `zdscan.py`, `part8.py` → `output_part8.txt` | the 4 d\* faces and the 3 Lambert-W values as the doubling parameter μ₄ (the only constants needed for ln(10) in UNS) |

## 2. The tension law on the paper's pencil proxy  [MEASURED]

The proxy (ScalarContextPropagation paper §9.3–9.4): each of the seven stations of `pencil(r)` is a continuous point
`cos φ·e_a + sin φ·e_b` (`a ⊕ b = r`); `Π` is their left-associated ordered product; `H = Re(Π)` plays the string tension. Stations
are pencil factorisations, **not** Assessor vertices.

- **Exact law:** `H = −cos(Σ_k ε_k φ_k)` to ≤ 8e-16 over 200 random φ-vectors per strut (pencils 1–9).
- **Mechanism [DERIVED in part]:** each station factor is exactly `e_a · exp(η_k e_r φ_k)` with `e_a⁻¹ e_b = η_k e_r` (checked for
  every pencil r = 1..15), and the product of the bare `e_a` is exactly `−e₀` for every r, so `H(φ=0) = −1`. The remaining sign factor
  in ε is bracketing-dependent (§9) and not derived.
- **ε patterns** (left bracketing, natural order): struts 1,3,6 `++--++-`; 2,7 `+--++--`; 4 `+++++++`; 5 `+-+-+-+` — rows 2, 3, 0, 1 of the Sylvester–Hadamard
  matrix on the station index `j = k−1`.
- **Noether path** `φ_k = t·(π/2)·(k+1)/7`: swing of H — struts 1,3,6: 0 (pinned); 4: 2.0000 (−1→+1→−1); 2,7: 1.2225; 5: 0.3765. Signed rate sums `S_s`: 0; 2π; −4π/7; 2π/7.
  This answers the paper's §9.4/§10 open question "why struts {1,3,6}" *within the proxy*: their signed rate sum cancels exactly.
- **Station response:** `|∂H/∂φ_k|` is identical for all seven stations of a strut (0.782 for 2,7; 0.434 for 5; 0 for 1,3,4,6 at t=½) — the response is collective.
- **Entry modes:** any scalar wind (position, rate, gust) moves only the one signed phase; strut 1 stays at exactly 0 swing under gusts. A station-unequal wind
  (`r_k = (k+1)/7·(1+d·u_k)`) reaches the rigid struts: mean swing 0.0032 / 0.0287 / 0.1874 at d = 0.05 / 0.15 / 0.4.
- **Anchoring** (hold a subset of stations fixed): 128 subsets → 7 distinct groupings of the 7 struts; {1,3,6} stay rigid under 8 of 128.
- **Regimes:** φ ∈ {0, π/2} → H ∈ {−1, 0, 1} (the "quantised lattice", an aperture effect); φ on a π/8 grid → 9 values; real φ fills [−1, 1].
- **Scope:** pencils 1–9 satisfy the one-phase law **for the left bracketing**; see §9 for how this changes with bracketing and §10 for the pencil-convention caveat.

## 3. The tear-off test  [MEASURED]

Page claim (`pencil_hyperstring.md`, CONJECTURE, test 5): `w ≫ w\*` ⇒ `outside_share → 1`, `is_zero_divisor → False`. `Φ_w` is unbuilt, so the literal
reading was tested: Joukowsky `z → z + c/z`, `c = H/q(w)`, `q = ½ρw²`, on each vertex `z = d₊ + i d₋`, reassembled exactly.
(A) `c → 0` as `w → ∞`: the map tends to the **identity** (shift 2.5 at w=1, 0.025 at w=10, 2.5e-6 at w=1000) and blows up as `w → 0` — opposite to the stated
inflation sequence. (B) A real zero divisor stays a zero divisor with `outside_share = 0` for w from 0.01 to 1000 (Joukowsky preserves the axes where the diagonals sit).
(C) The six-vertex sum of diagonals is a zero divisor for 0 of 4096 sign choices on strut 1. Structural: indices e₀, e₈ belong to no Assessor, so no map inside Assessor planes can move
energy onto them. **Verdict:** not reproduced by the literal formula; not refuted for the real `Φ_w` (station generators, circulations, reassembly under-specified).

## 4. The projected address through the box-kite lens  [MEASURED]

`ptol -r` gives a plain 16-real vector (Dirichlet projection; `ptol.c` never multiplies sedenions). Through `chart_of`: four prompts are never zero divisors,
`outside_share` 1–8%, chart shares 0.12–0.17 (nearly flat), `local_curvature` 12.0 for three of four. So the address is a generic vector: zero divisors are avoided automatically,
and the ZD surface is a thin subset it never touches.

## 5. The De Marrais deformation battery (the algebra alone)  [MEASURED]

### 5.1 Baseline
42 Assessors, 84 diagonals, 336 ordered ZD pairs, exactly 4 partners per diagonal, 7 octahedra.

### 5.2 What deforms nothing
- The 16 Sylvester–Hadamard (Walsh) sign vectors are automorphisms (error 0.0). Of all 65,536 diagonal sign operators on the 16 components **exactly 16** are automorphisms — these.
- Monomial automorphisms `e_i → η_i e_{A i}` need `A ∈ GL(4,2)` (20,160); exactly **168** lift, each in 16 sign ways: group of order **2,688 = 16 × 168**; all 168 fix e₈ and map the 42 Assessor planes onto themselves; element orders 1×1, 2×21, 3×56, 4×42, 7×48 (PSL(2,7)).
- Multiplication by `exp(θ e₈)`, on either side (both factors, or one), keeps all 336 pairs for every θ tried; no other basis unit does (14%/29%). Conjugation and the sign of e₀ or e₈ alone also keep every pair.

### 5.3 The continuous exact deformations
- `dim Der(sedenions) = 14` (g₂). The tangent space of the ZD-pair variety at every one of the 336 pairs has dimension **16 = 14 (derivation orbit) + 2 (scalings)** — nothing else is ZD-preserving to first order.
- Der-orbit through one diagonal: 11 (stabiliser 3, which still moves its 4 partners, rank 3); through the 12 diagonals of a chart: 14; through all 84: 14 (stabiliser 0).
- No derivation keeps all 84 diagonal lines invariant: every continuous exact deformation moves the kite off its lattice. Flows `exp(tD)` for t up to 2.5 keep all 336 relations to 1e-15 while diagonals move up to 48°; a random orthogonal generator gives defect 0.023 (t=0.05) and 0.148 (t=0.3).

### 5.4 First-order response (what tears, how fast)
- Annihilator of each of the 84 diagonals: dimension 4; the other singular values of `x → xy` are √2 (×8) and 2 (×4) — **this is the {4:8:4} grading** (§8).
- Every Hadamard row, as a perturbation of x, gives the same response √2·|δ| against all 84 y.
- In-plane rotation off a diagonal: defect `2|sin(θ − π/4)|`, zero at θ = π/4 + nπ/2, tear rate exactly 2.000 per radian.
- Dense Walsh–Hadamard transform: 0/336 pairs survive; Gray-code and bit-reversal index maps: 29%, 24%; random orthogonal 16×16: 0.
- Functions of the native pair `z = d₊ + i d₋` (three magnitudes; magnitude 1 alone is degenerate for `z²` and Möbius): Joukowsky (real c), `z²`, `tanh(z/2)`, `1/z`, conjugation, rotation by π/2 keep both diagonal lines; `exp(z)`, Möbius with real z₀, and a real shift keep only d₊; an imaginary shift keeps only d₋; a generic in-plane rotation keeps neither.

### 5.5 Deforming the algebra (μ): the constants necessary for ln(10) in Universal Native Space
Plane pairs still containing a zero-divisor pair are *solved for* (null space + rank-1 condition), not assumed at 45°. Per Cody (2026-10-13) the main text uses only
the **four d\*** and the **three Lambert-W values** (and ln 10 itself); every other constant that was tried is in Appendix B and §13. Full interaction in §6.
- Standard sedenions (μ₄ = −1): 168 ordered plane pairs, degree 4, all within chart, κ = ±1.
- **Any μ₄ = −c with c > 0** has the same combinatorics (isomorphic algebra) and tilts every vertex to κ = 1/√c; **μ₄ = +c > 0** (split) keeps half the adjacency (84 pairs, degree 2); **μ₄ = 0** collapses the kite to the all-to-all degenerate structure (1,764 pairs, degree 42).

| value entering as μ₄ | role | result | κ |
|---|---|---|---|
| ln 10 = 2.302585 (as −ln 10) | the quantity being built | standard class, tilted | 0.6590 |
| **d\*** (Boundary) 0.24631 (as −d\*) | equatorial plane | standard class, tilted | 2.0149 |
| **d\*_taut** (Flow) = W(1)/ln 10 = 0.246307201473 | radial unit | **identical to d\*** | 2.0149 |
| **d\*_ln(10)** (Translator) = W(1) = 0.5671432904 | metric bridge | standard class, tilted | 1.3279 |
| **d\*_RG** (Stability) — dimension 8 | centre; persistent octonion | no real-valued μ; as −8 it is just κ = 1/√8 = 0.3536 (arithmetic, not evidence); target value 0.24631 repeats d\* | — |
| **W(0) = 0** | vacuum fixed point | **μ₄ = 0: degenerate** (1,764 pairs, every plane with every plane) | — |
| **W(1) = +0.5671 = Ω_ZS** | entropy ceiling | **μ₄ > 0: split** (84 pairs, degree 2) | 1.3279 |
| **W(−1/e) = −1** | branch collapse | **μ₄ = −1: exactly the standard sedenions** (168 pairs, degree 4) | 1.0000 |

Also measured: **constants as a rotation angle** θ = c rad in an Assessor plane (defect zero at π/4 + nπ/2; ln 10 rad is 0.054 rad = 3.1° from 3π/4, defect 0.107 — expected by chance among 13 constants, recorded not chased);
and **as a phase scale in the tension law** `H = −cos(c·S_s)` (struts 1,3,6 read −1 for every constant; strut 4 reads −cos 2πc; 2,7 read −cos 4πc/7; 5 reads −cos 2πc/7). See Appendix B for the full constant list.

## 6. The four d\*, the three Lambert-W values, and their interaction  [MEASURED + HYP]

**The four d\*** (the chart of *radial complex spherical ln(10)*: centre, equatorial plane, radial ruler, scale bridge — four shadows of one point, 0.24631; `Ainulindale/wiki/17`, `.clauderc_canonical_maths`, `FourthAgePapers/DStarRG`):
`d\*` = 0.24631 (Boundary) · `d\*_RG` = dimension 8, numeric OPEN (Stability) · `d\*_taut` = Ω_ZS/ln 10 = 0.246307201473 (Flow) · `d\*_ln(10)` = d\*·ln 10 = Ω_ZS = 0.5671432904 (Translator).
Environment variables: `D_STAR_BOUNDARY`, `D_STAR_RG`, `D_STAR_TAUT`, `D_STAR_LN10` in `~/.clauderc`.

**The three Lambert-W values** (`Ainulindale/AgeThird/Third_Age_CS_Draft_v2.md` §2.2 and Appendix D): `W(0) = 0` (vacuum fixed point), `W(1) = Ω_ZS = 0.5671432904097838` (entropy ceiling; the fixed point of x → e^{−x}), `W(−1/e) = −1` (branch collapse; the zero-divisor crossing). Verified numerically (mpmath): W(1)e^{W(1)} = 1; W₀(−1/e) = W₋₁(−1/e) = −1.
*Caveat:* the emerger, `bao_mass_gap` and the Navier–Stokes wiki 106 speak of "three **rotor faces** of Ω_ZS = W(1)" (a Wankel trine: intake/power/exhaust, all carrying the same number 0.56714). That is the same *count* (3) read as three faces of one value; the two readings are kept apart here — **please confirm which is canonical for the fixed-point machinery.**

**What is established about their interaction** (all measured above or in the cited files):
1. **The Translator face IS a Lambert value:** `d\*_ln(10) = d\*·ln 10 = W(1)` — one of the four d\* coincides with one of the three W exactly.
2. **The three W values are the three classes of the Cayley–Dickson doubling parameter.** Entered as μ₄: W(0) = 0 → degenerate; W(1) > 0 → split; W(−1/e) = −1 → the standard (division-type) sedenions. One W value in each isomorphism class (μ = 0, μ > 0, μ < 0) — and the roles in the Third Age draft match: "before the first distinction, every prime equal weight" ↔ every plane pairs with every plane; "the zero-divisor crossing" ↔ the standard algebra where the octahedral kite first exists.
3. **The four d\* all live in the standard class** (they enter as negative μ₄) and differ only in tilt: Boundary and Flow coincide (κ = 2.0149), the Translator is κ = 1.3279, and the RG face as dimension 8 is κ = 1/√8. So **four faces give three distinct tilts** (two if the RG face's numeric target is used) — a count of 4 reducing to 3.
4. **The RG face's "8" is the isometric block of {4:8:4}:** the DStarRG "persistent core" is the gain-exactly-1 directions and contains e₀ and e₈ ("the two indices in no zero-divisor plane"); in §8 the gain-1 "now" block of every zero divisor is an 8-dimensional coordinate sub-octonion containing e₀ and e₈, with the 4 + 4 the past/future (void) blocks. The RG face is the 8.
5. The emerger's firing clock combines them: 4 d\* faces : 3 Lambert-W faces, `lcm(4,3) = 12` steps, entry bracket = ⌊12u⌋ mod 5 [THEORETICAL, `emerger.md`].

**Not established (do not read as a result):** an explicit rule by which the four and the three combine into "3 = 4 in the fixed-point lineage". Items 2–3 are the closest measured structure (3 classes, 3 distinct tilts from 4 faces); whether that is what is meant is **[HYP]** and for Cody to say.

## 7. The Blackjack subgroup  [MEASURED + DERIVED]

The 168 frame-preserving index maps (PSL(2,7)) act on the 7 struts as GL(3,2) on the Fano points. As **unsigned permutation matrices** (no sign correction), exactly **21** of them keep all 336 ZD pairs;
they form a closed subgroup with element orders 1×1, 3×14, 7×6 — the Frobenius group F₂₁ = 7:3 — and are **transitive on the 7 struts**. They are exactly the 21 maps that are automorphisms with **all signs +1** (pure relabelling): the
two sets are identical. The other 147 need a sign lift. De Marrais's papers [LIT: arXiv:math/0011260 and follow-ups] tie PSL(2,7) of order 168 to the primitive unit zero divisors; a literature search found no 21-element subgroup or the name
"Blackjack" there, so the **name is this project's**; the subgroup (normalizer of a Sylow-7 subgroup) and its sign-free-automorphism characterisation are algebra, computed here.

## 8. {4:8:4} in the kite  [MEASURED + DERIVED]

For a norm-one zero divisor `a`, `L_a` has singular values {0 ×4, 1 ×8, √2 ×4} (`three_ring_scale.md` §4). The battery reproduces it exactly from the multiplication table (for the diagonals of norm √2: 0 ×4, √2 ×8, 2 ×4).
- **The 4 (past, gain 0) is the vertex's edges:** the 4 edge-partners of a vertex y are exactly its annihilator — rank 4, norm 1.0 inside the null block. Left and right annihilators coincide.
- **The 4 (future, gain √2)** is spanned by the *other-sign* diagonals of the same four neighbour planes (the partner that does **not** annihilate y). **The opposite vertex** (the reversal plane) lies entirely in the 8-block.
- **The 8 (now, gain 1)** is the *coordinate* subspace on the indices `{i : χ_u(i) = +1}` — a sub-octonion — where the Hadamard character `u` is the **unique nonzero u ∈ 𝔽₂³ orthogonal to both a and b** (the polar point of the Fano line `{a, b, a⊕b}`); verified for all 84 diagonals, 12 per u, u ∈ 1..7 only (u ≥ 8 never arises). The past and future 4-blocks both live on the complementary 8 indices (each carries half of each, 50/50) and are separated by the d₊/d₋ sign of the neighbour planes.
- **ptol.c's J_red/J_blue is one of these:** J_red = `{0–3, 8–11}` = u = 4 (the ZDs on the quaternion line {1,2,3}); Γ = Σ χ₄(k)v_k²/|v|² agrees with the printed Γ to 1e-10 on four prompts. There are seven equivalent choices (u = 1..7), permuted transitively by the 168.
- The emerger's fixed index assignment `{4..7} / {1,2,3,8..11} / {12..15}` is right about the 8-block (plus e₀) but not about the 4|4 split: for a given diagonal, both `{4..7}` and `{12..15}` carry half null and half gain-√2.

## 9. Bracketing and firing order  [MEASURED]

132 bracketings (Catalan(6)) of the 7-factor pencil product, and 300 random firing orders (permutations of the stations, left bracketing):

| pencil r | bracketings with the one-phase law | rank histogram over the 132 | distinct sign patterns among rank-1 |
|---|---|---|---|
| 1, 2, 4 | **132 / 132** | all rank 1 | 7 (only 3 are ± Hadamard rows) |
| 8 | 132 / 132 | all rank 1 | 14 (none Hadamard rows) |
| 9 (strut 1's Assessor pencil) | 52 / 132 | {1:52, 4:56, 6:21, 7:3} | 3 |
| 10 | 0 / 132 | {4:34, 5:52, 6:31, 7:15} | — |
| 12 | 0 / 132 | {5:116, 6:12, 7:4} | — |
| 15 | 10 / 132 | {1:10, 4:22, 5:82, 6:12, 7:6} | 2 |

Firing order (left bracketing): r=1 — all 300 permutations rank 1 (10 patterns); r=9 — 11/300; r=10 — 9/300. **So "H depends on one signed phase" is a property of the triple (pencil, bracketing, firing order), not of the pencil
alone, and "ε = Hadamard rows" is a property of the left-bracketed natural order.** This supports the hypothesis that deformations (and edges) differ under different bracketings.

## 10. The constructs against the maths

**Scalar construct (pencil hyperstring / Gamma-Radial).** [MEASURED]
- *Pencil convention:* the pencils the paper uses for strut `r ≤ 7` contain **no** Assessor plane (0 of 7); the six Assessor planes of strut `s` are stations of `pencil(s+8)` (index XOR = s+8), plus the plane `{e_s, e₈}`. §9 shows the law's validity there depends on the bracketing.
- `Π(φ)` is never a zero divisor (0 of 13 points on each of six pencils; |Πd|/(|Π||d|) ≥ 1.0000 against all 84 diagonals): it is not a point of the ZD kite. A station flow in an Assessor plane tears at exactly 2.000/rad. Where it agrees: the ε are the maths' own automorphism characters (for the left bracketing); `H(0) = −1` is derived.

**Scaled construct (live address / A-Matrix).** [MEASURED]
- ptol.c's Γ *is* the χ₄ Walsh coefficient (§8). All lens readings (`local_curvature`, `outside_share`, `fixed_point_weight`, `chart_energy` permuting by `s → A(s)`) are exactly covariant under all 168 frame-preserving maps, on four prompts; under 300 random permutations they are unchanged in 0–1 cases.
- The projected address carries no topic: 16 prompts, 4 subjects — inter/intra distance 0.94–0.95, leave-one-out 1-NN 0.06–0.19 (chance 0.25) for the 7 chart energies, the 15 Walsh coefficients, the 16 energies and the 16 amplitudes.
- **Kernel fiber `throw_fiber`: [CORRECTED] not necessarily a defect.** It writes `psi[a], psi[b]` for the first Assessor `(a,b)`, i.e. energy on `e_a, e_b` (two lower-octonion indices). In the Assessor convention that is the wrong plane. But `span{e₀, e_a, e_b, e_s}` with `s = a⊕b` is closed under products — a **quaternion subalgebra** (the strut's own Fano line), `emerger.domain_of({a,b,s}) = ℍ`, while the Assessor pair `{a, b+8}` is a FRAGMENT. So the fiber is a coherent object in a *different bracket* (ℍ domain, no zero divisors) — plausibly a new bracketing, as Cody suggested. The `depth` parameter's `√(1−d²)e₀` admixture takes any Assessor-plane version off the ZD surface for every depth < 1.
- **Answer to "is e_b always in the upper octonion?":** in an Assessor `(a,b)` the plane is `span(e_a, e_{b+8})`: `a ∈ 1..7` is lower-octonion, `b+8 ∈ 9..15` is upper-octonion, always — every Assessor plane straddles the `{8:8}` boundary. The label `b` is the lower-octonion name of the upper element.

## 11. Corrections log

| # | Said earlier | Corrected to | Where found |
|---|---|---|---|
| 1 | Tension law shown for "the seven struts" | Holds for the paper's `pencil(r≤7)` (no Assessor planes) and only for the left bracketing; Assessor pencils depend on bracketing (§9) | part 6b/7 |
| 2 | Function-of-pair table: Möbius, `z²` keep both lines | An artifact of unit magnitude; at λ = 0.3, 2.5 Möbius tears the d₋ line (part 5) | part 5 |
| 3 | c = GAP all-levels gives 537 plane pairs | Tolerance artifact; 252 (= standard) at tol 1e-14 | part 2b |
| 4 | "d\*_RG has no value" | Dimension 8 (confirmed), numeric open with target 0.24631 (wiki 17, DStarRG); I had read only the canonical file | d\* hunt |
| 5 | Kernel fiber "possible defect" | A different bracket (quaternion line) — retracted as a defect | part 6b |
| 6 | "ε are Hadamard rows" | Only for left bracketing, natural order; 4 of 7 patterns per pencil are not Hadamard rows | part 6b |
| 7 | "Blackjack: preserves zero-divisor annihilation" (catalog) | True *as unsigned permutations*; all 168 preserve it with sign lifts; the 21 = the sign-free automorphisms | part 6/6c |
| 8 | Constants reported as a list of names (d\*, d\*_taut, d\*_ln(10), Ω_ZS …) | Names are not values: d\* and d\*_taut are one number (0.24631); d\*_ln(10) and Ω_ZS = W(1) are one number (0.56714). Distinct values: 0.24631, 0.56714, plus the open RG face. The main text now carries only the 4 d\* and 3 Lambert-W values | 2026-10-13 |
| 9 | d\*_spec (0.24600) listed as "the fifth value" among the faces | Quarantined as a disputed prior-model addition (Cody); it appears only in §13 and Appendix B | 2026-10-13 |

## 12. Open questions

1. Why is the one-phase law bracketing- and order-dependent for the Assessor pencils (and not for pencils ≤ 8)? Not alternativity (`e_r(e_r e_a) = −e_a` holds for all r, a), not simple associator counts.
2. Does a bracketing/firing-order that makes the Assessor pencil single-phase correspond to a named `{…}` bracket of the emerger? (Run the emerger's five brackets × the legal firing orders against §8.)
3. Which quantity is "the A-Matrix windspeed"? A scalar per read deforms only along one phase; the exact deformations are 14-dimensional.
4. Is the sign-free (F₂₁) structure what the A-Matrix "static grammar" maps onto (non-deformable skeleton)? Untested.
5. The 14 unread Walsh coefficients of the live address as the 16-channel oscilloscope readout; compose the live kite from the pool's tokens (pencil index, `w`, `vec19`, basin pull) and re-run this battery on it.
6. d\*_RG numerics (open) and the disputed fifth d\*_spec — see `~/.clauderc` and memory `reference_four_dstar_values`.

## 13. Future work — values kept, disambiguated from the 4 d\* and 3 Lambert-W

Nothing here is discarded; none of it is one of the four d\* or three W. Each is labelled with where it comes from.

| Value | Where it appears | Disambiguation |
|---|---|---|
| **d\*_spec ≈ 0.24600** | `~/.clauderc` `GAP`/legacy `D_STAR`; `ptol.c` comment; Ainulindale README Key Constants; PTorrent | The Berry–Keating spectral gap "observed in SPARC". **Disputed fifth value** — Cody believes a prior model added it; kept because `GAP = |d\*_spec·ln 10 − Ω_ZS| ≈ 7.07e-4 ≈ 1/(1000√2)` (the mass-gap analogue) is built on it. Env var `D_STAR_SPEC`. |
| 0.24682 | `smnnip_*_patched.py`; May-2026 primers; `SMNNIP_TODO.txt` | An early RG-flow estimate of d\*_RG, superseded. Env var `D_STAR_RG_SUPERSEDED`. |
| d\*_ℝ = 0.24600, d\*_ln10 = 0.56644, d\*_S "OPEN (Σ CD strata sum)" | `Third_Age_CS_Draft_v2.md` §2.3 | An *older* four-value set (July 2026): d\*_ℝ ↔ the Boundary taken as 0.24600; d\*_ln10 computed from it (0.56644, not Ω); d\*_S ↔ the open RG-type face. Superseded by the canonical four faces. |
| d\*_spec, d\*_taut, d\*_RG, d·ln 10 as "four branches of the natural logarithm in 𝕊" | a Gemini-era text in `corpus_repos.txt` | A different four (it uses d\*_spec in place of the Boundary). Historical. |
| W "rotor faces 1, 2, 3" (all = 0.56714) | Navier–Stokes wiki 106; `bao_mass_gap`; emerger | The *three-faces-of-one-value* reading of "three Lambert-W"; see §6 caveat. |
| W₋₁(−1/e) = −1 (the second real branch) | computed in `part8.py` | Equals the principal W₀(−1/e) = −1 at the branch point; no separate value. |
| GAP, 1/(1000√2), V(16) ≈ 0.2353, n\* ≈ 5.257 | canonical constants | Derived/related quantities, not faces. |
| π, e, φ, √2, 1/2, 2, i, 0, 1 as μ₄ / angle / phase scale | Appendix B | Test inputs tried at Cody's request; not part of the ln(10) machinery. |

## 14. Reproduce

```
cd .claude/scratchpad/2026-10-12_demarrais_deformation_battery
python3 -u part1.py   # ~4 min    python3 -u part2.py   # ~3 min    python3 -u part2b.py
python3 -u part3.py   python3 -u part4.py   python3 -u part5.py   python3 -u part6.py   python3 -u part6b.py   python3 -u part6c.py   python3 -u part7.py
```
Python 3.12, numpy, scipy (part 4). Do not run with `-I` from another directory (the package imports need the ThePlace root on the path, which `cdalg.py` adds).

---

# Appendix A — verbatim captured output

### windspeed_deformation_proxy: test.py

```
1. BASELINE  H(t) along the Noether path, every strut  (tension swing = max-min)
   strut  swing(H)   H(0)     H(1)     |Im Pi|(t=0.5)
   1      0.000000  -1.00000  -1.00000  0.00000
   2      1.222521  -1.00000  +0.22252  0.78183
   3      0.000000  -1.00000  -1.00000  0.00000
   4      2.000000  -1.00000  -1.00000  0.00000
   5      0.376510  -1.00000  -0.62349  0.43388
   6      0.000000  -1.00000  -1.00000  0.00000
   7      1.222521  -1.00000  +0.22252  0.78183

2. RESPONSE OF EACH STATION  |dH/dphi_k| at t=0.5 on the Noether path (central difference)
   strut | st1    st2    st3    st4    st5    st6    st7  
   1     | 0.000  0.000  0.000  0.000  0.000  0.000  0.000
   2     | 0.782  0.782  0.782  0.782  0.782  0.782  0.782
   3     | 0.000  0.000  0.000  0.000  0.000  0.000  0.000
   4     | 0.000  0.000  0.000  0.000  0.000  0.000  0.000
   5     | 0.434  0.434  0.434  0.434  0.434  0.434  0.434
   6     | 0.000  0.000  0.000  0.000  0.000  0.000  0.000
   7     | 0.782  0.782  0.782  0.782  0.782  0.782  0.782

3. NON-UNIFORM WIND  rates r_k = (k+1)/7 * (1 + d*u_k), u_k random in [-1,1], 60 draws/strut
   mean tension swing of H over t in [0,1]; d=0 is the Noether path
   strut | d=0      d=0.05   d=0.15   d=0.4  
   1     | 0.0000   0.0032   0.0287   0.1874 
   2     | 1.2225   1.2346   1.2537   1.2652 
   3     | 0.0000   0.0032   0.0287   0.1874 
   4     | 2.0000   1.9989   1.9907   1.9810 
   5     | 0.3765   0.3892   0.4242   0.5599 
   6     | 0.0000   0.0032   0.0287   0.1874 
   7     | 1.2225   1.2346   1.2537   1.2652 

4. SCALAR WIND, TIME-VARYING  (gusts): t(tau) = tau + 0.2*sin(2*pi*tau)/(2*pi)  vs steady t=tau
   strut 1: max|H_gust(tau) - H_steady(tau)| = 0.0000   range gust=[-1.0000,-1.0000] steady=[-1.0000,-1.0000]
   strut 2: max|H_gust(tau) - H_steady(tau)| = 0.0536   range gust=[-1.0000,0.2225] steady=[-1.0000,0.2225]

5. IS H A FUNCTION OF ONE SIGNED PHASE?  fit H = -cos(sum_k eps_k*phi_k), best of 128 sign patterns,
   200 random phi vectors per strut; also the signed rate sum on the Noether path
   strut 1: max|H + cos(sum eps*phi)| = 4.44e-16   eps=++--++-   signed Noether rate sum = +0.00000 rad
   strut 2: max|H + cos(sum eps*phi)| = 3.89e-16   eps=+--++--   signed Noether rate sum = -1.79520 rad
   strut 3: max|H + cos(sum eps*phi)| = 4.44e-16   eps=++--++-   signed Noether rate sum = +0.00000 rad
   strut 4: max|H + cos(sum eps*phi)| = 7.63e-16   eps=+++++++   signed Noether rate sum = +6.28319 rad
   strut 5: max|H + cos(sum eps*phi)| = 3.33e-16   eps=+-+-+-+   signed Noether rate sum = +0.89760 rad
   strut 6: max|H + cos(sum eps*phi)| = 4.44e-16   eps=++--++-   signed Noether rate sum = +0.00000 rad
   strut 7: max|H + cos(sum eps*phi)| = 3.89e-16   eps=+--++--   signed Noether rate sum = -1.79520 rad
```

### windspeed_deformation_proxy: test2.py

```
A. eps pattern per pencil r (r<=7 are the box-kite struts) vs Hadamard rows (columns j=0..6)
   r=1  err=4.4e-16 eps=++--++-  = +/- Hadamard row [2]
   r=2  err=3.3e-16 eps=+--++--  = +/- Hadamard row [3]
   r=3  err=4.4e-16 eps=++--++-  = +/- Hadamard row [2]
   r=4  err=4.4e-16 eps=+++++++  = +/- Hadamard row [0]
   r=5  err=3.3e-16 eps=+-+-+-+  = +/- Hadamard row [1]
   r=6  err=4.4e-16 eps=++--++-  = +/- Hadamard row [2]
   r=7  err=3.3e-16 eps=+--++--  = +/- Hadamard row [3]
   r=8  err=4.4e-16 eps=+++--++  = +/- Hadamard row NONE
   r=9  err=3.3e-16 eps=+-++-+-  = +/- Hadamard row NONE
   r=10 err=1.3e+00 eps=++-+--+  = +/- Hadamard row NONE
   r=11 err=1.4e+00 eps=+------  = +/- Hadamard row NONE
   r=12 err=1.3e+00 eps=+--+--+  = +/- Hadamard row NONE
   r=13 err=1.3e+00 eps=+-+--++  = +/- Hadamard row NONE
   r=14 err=1.5e+00 eps=+--+-++  = +/- Hadamard row [7]
   r=15 err=1.4e+00 eps=+--+++-  = +/- Hadamard row NONE

B. anchoring: 128 different subsets of stations held fixed -> 7 different groupings of the 7 struts
   {1,3,6} stay rigid under 8 of 128 anchor subsets; rigid-set sizes seen: [0, 1, 2, 3, 7]
   grouping ((1, 3, 6), (2, 7), (4,), (5,))  <- 73 anchor subsets, e.g. anchored stations [1]
   grouping ((1, 3, 5, 6), (2, 4, 7))  <- 12 anchor subsets, e.g. anchored stations [1, 4, 5]
   grouping ((1, 2, 3, 6, 7), (4, 5))  <- 12 anchor subsets, e.g. anchored stations [2, 4, 6]
   grouping ((1, 3, 4, 6), (2, 5, 7))  <- 12 anchor subsets, e.g. anchored stations [3, 4, 7]
   grouping ((1, 2, 3, 4, 5, 6, 7),)  <- 11 anchor subsets, e.g. anchored stations [1, 2, 4, 5, 6]

C. regimes of the SAME law H = -cos(sum eps*phi), strut 1:
   discrete  phi in {0,pi/2}            : H values seen = [-1.0, 0.0, 1.0]
   semi-cont phi on grid {0,pi/8,...,pi/2}: 9 distinct H values, from -1.000 to 1.000
   continuous phi real                   : H fills [-1, 1]
```

### pencil_tearoff_test

```
A. Joukowsky as written, one vertex z = 0.7+0.4j  (|z|^2 = 0.650)
          w     c=H/q(w)         |z'-z| note
       0.01        20000        24806.9 
        0.1          200        248.069 
          1            2        2.48069 
          2          0.5       0.620174 
          3      0.22222       0.275633 
         10         0.02      0.0248069 
        100       0.0002    0.000248069 
       1000        2e-06    2.48069e-06 
      10000        2e-08    2.48069e-08 

B. single zero divisor = diagonal of Assessor (2, 3) in strut 1
   start (d+ diagonal): is_ZD=True outside=0
     w=0.01    is_ZD=True  outside_share=0  norm=2e+04
     w=0.3     is_ZD=True  outside_share=0  norm=23.22
     w=1       is_ZD=True  outside_share=0  norm=3
     w=3       is_ZD=True  outside_share=0  norm=1.222
     w=30      is_ZD=True  outside_share=0  norm=1.002
     w=1000    is_ZD=True  outside_share=0  norm=1
   start (d- diagonal): is_ZD=True outside=0
     w=0.01    is_ZD=True  outside_share=0  norm=2e+04
     w=0.3     is_ZD=True  outside_share=0  norm=21.22
     w=1       is_ZD=True  outside_share=0  norm=1
     w=3       is_ZD=True  outside_share=0  norm=0.7778
     w=30      is_ZD=True  outside_share=0  norm=0.9978
     w=1000    is_ZD=True  outside_share=0  norm=1
   control: a MIXED vector in the same plane (both diagonals occupied)
   start: is_ZD=False outside=0

C. six-vertex kite vector in strut 1: sum of one diagonal per Assessor,
   all 4^6 = 4096 diagonal/sign choices; which are zero divisors at w=baseline?
   baseline zero-divisor kite vectors found: 0 of 4096
   e0/e8 are never populated by any assessor-plane map (indices 0 and 8 belong to no Assessor),
   so outside_share = 0 for every candidate and for every deformation of it, by construction.
```

### projected_address_lens

```
neutron generation           ZD=False outside=0.011 dom_chart=1 share=0.17 curv=12.0 shares=[0.17, 0.17, 0.16, 0.13, 0.12, 0.13, 0.13]
pressurized water reactor    ZD=False outside=0.037 dom_chart=2 share=0.17 curv=12.0 shares=[0.16, 0.17, 0.17, 0.14, 0.13, 0.12, 0.12]
the cat sat on the mat       ZD=False outside=0.029 dom_chart=2 share=0.17 curv=12.0 shares=[0.17, 0.17, 0.16, 0.13, 0.13, 0.12, 0.12]
neutron                      ZD=False outside=0.075 dom_chart=4 share=0.15 curv=4.0 shares=[0.15, 0.14, 0.14, 0.15, 0.14, 0.14, 0.14]
```

### demarrais_deformation_battery: output_part1.txt

```
DM-00 baseline: {'assessors': 42, 'diagonals': 84, 'ordered_zd_pairs': 336, 'kills_per_diagonal': [4], 'diagonals_with_a_partner': 84}
DM-01 all 16 Hadamard-row sign flips are automorphisms: max error 0.00e+00
DM-02 of 65536 diagonal sign operators, automorphisms: 16 (expected 16 = the characters)
DM-03 |GL(4,2)|=20160 ; A that lift to an automorphism: 168 ; each lifts in 16 sign ways -> monomial Aut order 2688
      of those, preserving the set of 42 Assessor planes: 168  (x16 characters = 2688)
      frame-preserving AND fixing e8: 168
DM-04 dimension of Der(sedenions) = 14  (g2 would be 14)
      tangent dim of the Der-orbit through each diagonal: [np.int64(11)] ; stabiliser dims [np.int64(3)]
      derivations that keep ALL 84 diagonal lines invariant: 0  (0 => every continuous exact deformation moves the kite off its lattice)
DM-05 tangent space (all directions preserving xy=0 to 1st order) of the pair, per ordered ZD pair: dims [np.int64(16)] ; of which derivation (G2) directions: [np.int64(14)]
      => on the unit spheres: variety dim >= [np.int64(14)] ; scaling x,y accounts for 2
DM-06 dim of {x : x y = 0} for each of the 84 diagonals y: [4] ; nonzero singular values of x->xy: [(np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(1.4142), np.float64(2.0), np.float64(2.0), np.float64(2.0), np.float64(2.0))]
      Walsh-row perturbations of x: response ||R_y chi_u||/||chi_u||  (min / mean / max over the 84 y):
        u= 0  1.4142  1.4142  1.4142
        u= 1  1.4142  1.4142  1.4142
        u= 2  1.4142  1.4142  1.4142
        u= 3  1.4142  1.4142  1.4142
        u= 4  1.4142  1.4142  1.4142
        u= 5  1.4142  1.4142  1.4142
        u= 6  1.4142  1.4142  1.4142
        u= 7  1.4142  1.4142  1.4142
        u= 8  1.4142  1.4142  1.4142
        u= 9  1.4142  1.4142  1.4142
        u=10  1.4142  1.4142  1.4142
        u=11  1.4142  1.4142  1.4142
        u=12  1.4142  1.4142  1.4142
        u=13  1.4142  1.4142  1.4142
        u=14  1.4142  1.4142  1.4142
        u=15  1.4142  1.4142  1.4142
```

### demarrais_deformation_battery: output_part2.txt

```
pairs 336

DM-10  operators on the 336 ordered ZD pairs (x,y), xy=0.   fraction with the stated product still zero
   operator T                                 T(x)T(y)   T(x) y   x T(y)   T(y)T(x)
   identity                                      1.000    1.000    1.000      1.000
   scale x2.5                                    1.000    1.000    1.000      1.000
   conjugation (e_k -> -e_k, k>0)                1.000    1.000    1.000      1.000
   WHT (dense Hadamard transform / 4)            0.000    0.000    0.000      0.000
   Gray-code index map (unsigned)                0.286    0.000    0.000      0.286
   bit-reversal index map (unsigned)             0.238    0.167    0.167      0.238
   swap halves e_i <-> e_{i+8}                   1.000    0.000    0.000      1.000
   rotate every (k,k+8) pair by 0.3 rad          1.000    1.000    1.000      1.000
   rotate every (k,k+8) pair by pi/4             1.000    1.000    1.000      1.000
   character chi_1 (Hadamard row 1)              1.000    0.429    0.429      1.000
   character chi_4 (Hadamard row 4)              1.000    0.429    0.429      1.000
   character chi_5 (Hadamard row 5)              1.000    0.429    0.429      1.000
   character chi_9 (Hadamard row 9)              1.000    0.571    0.571      1.000
   character chi_15 (Hadamard row 15)            1.000    0.571    0.571      1.000
   XOR-translate index by 1 (unsigned)           0.429    0.143    0.143      0.429
   XOR-translate index by 3 (unsigned)           0.429    0.143    0.143      0.429
   XOR-translate index by 8 (unsigned)           1.000    0.000    0.000      1.000
   flip sign of e_0 only                         1.000    1.000    1.000      1.000
   flip sign of e_3 only                         0.714    0.857    0.857      0.714
   flip sign of e_8 only                         1.000    1.000    1.000      1.000
   flip sign of e_11 only                        0.714    0.857    0.857      0.714
   left-multiply by e_1                          0.429    0.286    0.286      0.429
   left-multiply by e_5                          0.429    0.286    0.286      0.429
   left-multiply by e_8                          1.000    1.000    1.000      1.000
   random orthogonal 16x16 (10 draws), best fraction preserved: 0.000

DM-11  ZD defect of x(theta)=cos e_a + sin e_{b+8} against its best partner diagonal (standard algebra):
   theta=0.0000  min_y ||x y|| = 1.41421
   theta=0.1000  min_y ||x y|| = 1.26596
   theta=0.5000  min_y ||x y|| = 0.56308
   theta=0.7754  min_y ||x y|| = 0.02000
   theta=0.7854  min_y ||x y|| = 0.00000
   theta=0.7954  min_y ||x y|| = 0.02000
   theta=1.0000  min_y ||x y|| = 0.42592
   theta=1.5708  min_y ||x y|| = 1.41421

DM-12  standard sedenions:  {'capable_ordered_plane_pairs': 168, 'planes_with_a_partner': 42, 'degree_set': [4], 'within_chart': 168, 'nullity_hist': {2: 168}, 'kappa_x': [1.0, -1.0]}

DM-13  deform ONLY the sedenion doubling  mu4 = +/- c   (mu1..3 = -1).  c from the UNS list
   c                   sign  pairs    planes    degrees        within-chart kappa_x (ZD slope in plane)
   0                     +1  1764     42        [42]           252          []
   1                     -1  168      42        [4]            168          [1.0, -1.0]
   1                     +1  84       42        [2]            84           [1.0, -1.0]
   1/2                   -1  168      42        [4]            168          [1.4142, -1.4142]
   1/2                   +1  84       42        [2]            84           [1.4142, -1.4142]
   sqrt2                 -1  168      42        [4]            168          [0.8409, -0.8409]
   sqrt2                 +1  84       42        [2]            84           [0.8409, -0.8409]
   2                     -1  168      42        [4]            168          [0.7071, -0.7071]
   2                     +1  84       42        [2]            84           [0.7071, -0.7071]
   e                     -1  168      42        [4]            168          [0.6065, -0.6065]
   e                     +1  84       42        [2]            84           [0.6065, -0.6065]
   pi                    -1  168      42        [4]            168          [0.5642, -0.5642]
   pi                    +1  84       42        [2]            84           [0.5642, -0.5642]
   phi                   -1  168      42        [4]            168          [0.7862, -0.7862]
   phi                   +1  84       42        [2]            84           [-0.7862, 0.7862]
   ln10                  -1  168      42        [4]            168          [0.659, -0.659]
   ln10                  +1  84       42        [2]            84           [-0.659, 0.659]
   Omega_ZS=d*_ln10      -1  168      42        [4]            168          [1.3279, -1.3279]
   Omega_ZS=d*_ln10      +1  84       42        [2]            84           [1.3279, -1.3279]
   d*=d*_taut            -1  168      42        [4]            168          [2.0149, -2.0149]
   d*=d*_taut            +1  84       42        [2]            84           [2.0149, -2.0149]
   d*_spec               -1  168      42        [4]            168          [2.0162, -2.0162]
   d*_spec               +1  84       42        [2]            84           [2.0162, -2.0162]
   GAP                   -1  168      42        [4]            168          [-37.606, 37.606]
   GAP                   +1  84       42        [2]            84           [-37.606, 37.606]
   i                     -1  252      42        [6]            252          [(-0.7071-0.7071j), (0.7071+0.7071j), (0.7071-0.7071j), (-0.7071+0.7071j)]
   i                     +1  252      42        [6]            252          [(-0.7071+0.7071j), (0.7071-0.7071j), (-0.7071-0.7071j), (0.7071+0.7071j)]

DM-14  deform ALL four doubling levels together  mu_k = -c   (k=1..4)
   0                  pairs=1764  planes=42  degrees=[42] within=252 kappa=[0.0, 'family']
   1                  pairs=168   planes=42  degrees=[4] within=168 kappa=[1.0, -1.0]
   1/2                pairs=168   planes=42  degrees=[4] within=168 kappa=[0.7071, -0.7071, 1.0]
   sqrt2              pairs=168   planes=42  degrees=[4] within=168 kappa=[0.5946, -0.5946, 0.7071]
   2                  pairs=168   planes=42  degrees=[4] within=168 kappa=[0.3536, -0.3536, 0.5]
   e                  pairs=168   planes=42  degrees=[4] within=168 kappa=[0.2231, -0.2231, 0.3679]
   pi                 pairs=168   planes=42  degrees=[4] within=168 kappa=[-0.1796, 0.1796, 0.3183]
   phi                pairs=168   planes=42  degrees=[4] within=168 kappa=[0.4859, -0.4859, 0.618]
   ln10               pairs=168   planes=42  degrees=[4] within=168 kappa=[0.2862, -0.2862, 0.4343]
   Omega_ZS=d*_ln10   pairs=168   planes=42  degrees=[4] within=168 kappa=[0.7531, -0.7531, 1.0]
   d*=d*_taut         pairs=168   planes=42  degrees=[4] within=168 kappa=[0.4963, -0.4963, 1.0]
   d*_spec            pairs=168   planes=42  degrees=[4] within=168 kappa=[0.496, -0.496, 1.0]
   GAP                pairs=537   planes=42  degrees=[4, 14, 15, 20, 27] within=171 kappa=[0.0, 0.0266, -0.0266]
   i                  pairs=252   planes=42  degrees=[6] within=252 kappa=[(-0.7071-0.7071j), (0.7071+0.7071j), (0.7071-0.7071j)]

DM-15  deform ONE lower level (others standard)
   mu1=+0.0  pairs=1344  planes=42  degrees=[4, 36, 38] within=240
   mu1=+1.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu1=+2.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu1=-2.0  pairs=168   planes=42  degrees=[4] within=168
   mu2=+0.0  pairs=1344  planes=42  degrees=[4, 36, 38] within=240
   mu2=+1.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu2=+2.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu2=-2.0  pairs=168   planes=42  degrees=[4] within=168
   mu3=+0.0  pairs=1344  planes=42  degrees=[4, 36, 38] within=240
   mu3=+1.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu3=+2.0  pairs=120   planes=42  degrees=[2, 4] within=120
   mu3=-2.0  pairs=168   planes=42  degrees=[4] within=168
```

### demarrais_deformation_battery: output_part2b.txt

```
(i) GAP at all four levels, plane pairs with a null direction (before the rank-1 test), by tolerance:
    tol=1e-09 : 618  [standard algebra: 252]
    tol=1e-12 : 282  [standard algebra: 252]
    tol=1e-14 : 252  [standard algebra: 252]

(ii) multiplication by u=cos(th)+sin(th) e_t  -- fraction of the 336 ZD pairs kept (th=0.3 and th=1.1)
    t   R_u both  R_u x-only  R_u y-only |  L_u both  L_u x-only  L_u y-only
    1   0.143      0.286       0.286    |  0.143      0.286       0.286   
    2   0.143      0.286       0.286    |  0.143      0.286       0.286   
    3   0.143      0.286       0.286    |  0.143      0.286       0.286   
    4   0.143      0.286       0.286    |  0.143      0.286       0.286   
    5   0.143      0.286       0.286    |  0.143      0.286       0.286   
    6   0.143      0.286       0.286    |  0.143      0.286       0.286   
    7   0.143      0.286       0.286    |  0.143      0.286       0.286   
    8   1.000      1.000       1.000    |  1.000      1.000       1.000   
    9   0.143      0.286       0.286    |  0.143      0.286       0.286   
   10   0.143      0.286       0.286    |  0.143      0.286       0.286   
   11   0.143      0.286       0.286    |  0.143      0.286       0.286   
   12   0.143      0.286       0.286    |  0.143      0.286       0.286   
   13   0.143      0.286       0.286    |  0.143      0.286       0.286   
   14   0.143      0.286       0.286    |  0.143      0.286       0.286   
   15   0.143      0.286       0.286    |  0.143      0.286       0.286   

(iii) constants as the rotation angle theta (radians) of a diagonal inside its own plane; defect = min_y ||x(theta) y||  (analytic: 2|sin(theta - pi/4)|)
    0         theta=0.00000  defect=1.41421   analytic=1.41421
    1         theta=1.00000  defect=0.42592   analytic=0.42592
    1/2       theta=0.50000  defect=0.56308   analytic=0.56308
    sqrt2     theta=1.41421  defect=1.17637   analytic=1.17637
    2         theta=2.00000  defect=0.69742   analytic=1.87446
    e         theta=2.71828  defect=0.70845   analytic=1.87032
    pi        theta=3.14159  defect=1.41421   analytic=1.41421
    phi       theta=1.61803  defect=1.34586   analytic=1.47942
    ln10      theta=2.30259  defect=0.10717   analytic=1.99713
    Omega_ZS  theta=0.56714  defect=0.43305   analytic=0.43305
    d*        theta=0.24631  defect=1.02671   analytic=1.02671
    d*_spec   theta=0.24600  defect=1.02724   analytic=1.02724
    GAP       theta=0.00071  defect=1.41321   analytic=1.41321

(iv) tension at the end of the Noether path if every phase is scaled by c:  H = -cos(c * S_s)   (S: strut 1,3,6 = 0 ; 4 = 2pi ; 2,7 = -4pi/7 ; 5 = 2pi/7)
    c         1,3,6      4          2,7        5        
    0         -1.00000   -1.00000   -1.00000   -1.00000 
    1         -1.00000   -1.00000   +0.22252   -0.62349 
    1/2       -1.00000   +1.00000   -0.62349   -0.90097 
    sqrt2     -1.00000   +0.85822   +0.82375   -0.29686 
    2         -1.00000   -1.00000   +0.90097   +0.22252 
    e         -1.00000   +0.19797   -0.16668   +0.76377 
    pi        -1.00000   -0.62968   -0.80005   +0.94870 
    phi       -1.00000   +0.73737   +0.97207   -0.11818 
    ln10      -1.00000   +0.32442   +0.54702   +0.47591 
    Omega_ZS  -1.00000   +0.91232   -0.52496   -0.87320 
    d*        -1.00000   -0.02320   -0.90383   -0.97566 
    d*_spec   -1.00000   -0.02513   -0.90406   -0.97572 
    GAP       -1.00000   -0.99999   -1.00000   -1.00000 
    i(imag)   -1         -cosh(6.283)  -cosh(1.795)  -cosh(0.898)   (phase scale i: -cos(i S) = -cosh(S): leaves [-1,1])
```

### demarrais_deformation_battery: output_part3.txt (its CS-04 table is superseded by part 5)

```
=== SCALAR CONSTRUCT (pencil hyperstring proxy) vs the maths ===

CS-01  are the stations Assessor planes?  (De Marrais Assessor planes of strut s have index XOR s+8)
   stations of pencil(r) that are Assessor planes:  r=1..8: 0 of 7 ; r=9..15 (= strut s+8): 6 of 7 (+ the plane {s,e8})
   => the paper's pencil(strut r<=7) never sits in the Assessor planes; pencil(s+8) does, and its H depends on 4-5 phase combinations for s=2..7 (rank 1 only for s=1)

CS-02  is the product Pi(phi) ever a zero divisor?  (chart_of exact test; 12 phase vectors + the Noether path per pencil)
   pencil( 1): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000
   pencil( 4): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000
   pencil( 9): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000
   pencil(10): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000
   pencil(12): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000
   pencil(15): zero divisor at 0 of 13 points ; smallest ||Pi d||/(|Pi||d|) against the 84 diagonals = 1.0000

CS-03  the construct's deformation at an Assessor-plane station:  rotate d+ -> d-  (phi: pi/4 -> pi/4+delta)
   first-order tear rate of a diagonal x(phi) against its best partner (DM-11):  |d||x y|/d phi| at pi/4
   delta=0.0001 : defect 0.000200  -> rate 2.0000 per radian   (exactly 2: the station flow is TRANSVERSAL to the zero-divisor set)
   delta=0.001 : defect 0.002000  -> rate 2.0000 per radian   (exactly 2: the station flow is TRANSVERSAL to the zero-divisor set)

CS-04  functions of the pair z = d+ + i d-  applied to a diagonal x:  does the image stay a zero divisor (annihilate one of the 84 diagonals)?
   f                                            x = d+ diagonal (z real)     x = d- diagonal (z imaginary)
   identity                                     14/14 stay zero divisors     14/14 stay zero divisors    
   scale by 2.5                                 14/14 stay zero divisors     14/14 stay zero divisors    
   Joukowsky z + c/z, c=Omega_ZS                14/14 stay zero divisors     14/14 stay zero divisors    
   Joukowsky z + c/z, c=0.3                     14/14 stay zero divisors     14/14 stay zero divisors    
   Moebius (z-z0)/(z+z0), z0=1 (Smith fold)     14/14 stay zero divisors     14/14 stay zero divisors    
   exp(z)                                       14/14 stay zero divisors     0/14 stay zero divisors     
   z^2                                          14/14 stay zero divisors     14/14 stay zero divisors    
   tanh(z/2)                                    14/14 stay zero divisors     14/14 stay zero divisors    
   rotate z by 0.3 rad (in-plane)               0/14 stay zero divisors      0/14 stay zero divisors     
   rotate z by pi/2 (swap d+ -> d-)             14/14 stay zero divisors     14/14 stay zero divisors    
   complex conjugate (d- -> -d-)                14/14 stay zero divisors     14/14 stay zero divisors    
   1/z (inversion)                              14/14 stay zero divisors     14/14 stay zero divisors    

=== SCALED CONSTRUCT (live address) vs the maths ===

SC-01  ptol.c's Gamma = a Walsh coefficient of the energy distribution?   chi_4(k) = (-1)^(bit2 of k)  == the J_red/J_blue partition
   neutron generation           Gamma(ptol)=-0.8763784555   W_4=sum chi_4 v^2/|v|^2=-0.8763784555   |diff|=2.1e-11   other W_u: [-0.032, 0.032, 0.001, -0.011, -0.093, 0.065]
   pressurized water reactor    Gamma(ptol)=-0.8613638337   W_4=sum chi_4 v^2/|v|^2=-0.8613638336   |diff|=5.5e-11   other W_u: [-0.015, -0.161, 0.043, 0.053, 0.238, 0.002]
   the cat sat on the mat       Gamma(ptol)=-0.8828607305   W_4=sum chi_4 v^2/|v|^2=-0.8828607304   |diff|=5.8e-11   other W_u: [-0.016, -0.089, 0.0, 0.034, 0.124, 0.057]
   neutron                      Gamma(ptol)=-0.0886422526   W_4=sum chi_4 v^2/|v|^2=-0.0886422526   |diff|=5.0e-11   other W_u: [-0.087, -0.157, -0.046, -0.039, -0.007, 0.027]

SC-02  covariance of the lens readings under the maths' symmetry group  (apply the signed monomial automorphism T to the address)
   frame-preserving index maps found (fixing e8): 168  (expected 168 = |GL(3,2)|; signs lift in 16 ways each)
   neutron generation           over 168 automorphic maps: local_curvature invariant 168, outside_share 168, fixed_point_weight 168, chart_energy permutes by s->A(s): 168
   pressurized water reactor    over 168 automorphic maps: local_curvature invariant 168, outside_share 168, fixed_point_weight 168, chart_energy permutes by s->A(s): 168
   the cat sat on the mat       over 168 automorphic maps: local_curvature invariant 168, outside_share 168, fixed_point_weight 168, chart_energy permutes by s->A(s): 168
   neutron                      over 168 automorphic maps: local_curvature invariant 168, outside_share 168, fixed_point_weight 168, chart_energy permutes by s->A(s): 168
   control: 300 RANDOM index permutations of the 16 slots (not automorphisms):
   neutron generation           curvature AND outside_share both unchanged in 0 / 300
   pressurized water reactor    curvature AND outside_share both unchanged in 1 / 300

SC-03  the kernel's fiber (scaled_mind_eye_boxkite_kernel_monad.throw_fiber):  psi = sqrt(1-d^2) e0 + d/sqrt2 (e_a + e_b), (a,b)=first Assessor of the strut
   as written (indices a and b directly)  vs  the Assessor plane (a, b+8)
   strut 1 depth 0.6  as written e_a+e_b     dominant chart=1 (intended 1)  nearest assessor=(2, 1)  is_zero_divisor=False
   strut 1 depth 0.6  Assessor e_a+e_(b+8)   dominant chart=1 (intended 1)  nearest assessor=(2, 3)  is_zero_divisor=False
   strut 1 depth 1.0  as written e_a+e_b     dominant chart=1 (intended 1)  nearest assessor=(2, 1)  is_zero_divisor=False
   strut 1 depth 1.0  Assessor e_a+e_(b+8)   dominant chart=1 (intended 1)  nearest assessor=(2, 3)  is_zero_divisor=True
   strut 2 depth 0.6  as written e_a+e_b     dominant chart=2 (intended 2)  nearest assessor=(1, 2)  is_zero_divisor=False
   strut 2 depth 0.6  Assessor e_a+e_(b+8)   dominant chart=2 (intended 2)  nearest assessor=(1, 3)  is_zero_divisor=False
   strut 2 depth 1.0  as written e_a+e_b     dominant chart=2 (intended 2)  nearest assessor=(1, 2)  is_zero_divisor=False
   strut 2 depth 1.0  Assessor e_a+e_(b+8)   dominant chart=2 (intended 2)  nearest assessor=(1, 3)  is_zero_divisor=True
   strut 5 depth 0.6  as written e_a+e_b     dominant chart=2 (intended 5)  nearest assessor=(1, 2)  is_zero_divisor=False
   strut 5 depth 0.6  Assessor e_a+e_(b+8)   dominant chart=2 (intended 5)  nearest assessor=(1, 4)  is_zero_divisor=False
   strut 5 depth 1.0  as written e_a+e_b     dominant chart=2 (intended 5)  nearest assessor=(1, 2)  is_zero_divisor=False
   strut 5 depth 1.0  Assessor e_a+e_(b+8)   dominant chart=2 (intended 5)  nearest assessor=(1, 4)  is_zero_divisor=True
```

### demarrais_deformation_battery: output_part4.txt

```
dim Der = 14
ZD relations (ordered diagonal pairs): 336

DM-20  flow the WHOLE set of 84 diagonals along exp(tD), D a random derivation (unit norm):
   t      max ||x(t) y(t)|| over the 336 relations   max angular distance of a diagonal from its lattice line (deg)   still unit norm?
   0.05   1.58e-16                                    0.96                                             True
   0.30   1.90e-16                                    5.79                                             True
   1.00   4.37e-16                                   19.28                                             True
   2.50   1.08e-15                                   48.06                                             True

DM-21  control: flow along a RANDOM orthogonal generator (not a derivation), same t:
   t=0.05  max ||x(t) y(t)|| = 0.023
   t=0.30  max ||x(t) y(t)|| = 0.148

DM-22  dimension of the family of exactly-deformed kites:
   chart 1: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 2: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 3: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 4: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 5: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 6: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   chart 7: 12 diagonals (6 vertices x 2): orbit rank under Der = 14 of 14
   all 84 diagonals together: orbit rank 14 of 14  (stabiliser dimension 0)

DM-23  Der sub-structure: which derivations fix a given vertex (stabiliser) and do they fix its partners?
   stabiliser of one diagonal: dim 3
   it has 4 partners; derivations fixing x also fix how many of them (rank of their action on the partners): [3]
```

### demarrais_deformation_battery: output_part5.txt

```
CS-04b  same test, magnitudes lam in {0.3, 1.0, 2.5}: fraction of (plane, diagonal) cases still zero divisors, d+ line / d- line
   f                              lam=0.3 (d+ | d-)        lam=1.0 (d+ | d-)        lam=2.5 (d+ | d-)       
   Joukowsky z+c/z, c=Omega_ZS    14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   Moebius (z-1)/(z+1)            14/14 | 0/14             0/0 | 14/14              14/14 | 0/14            
   exp(z)                         14/14 | 0/14             14/14 | 0/14             14/14 | 0/14            
   z^2                            14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   tanh(z/2)                      14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   rotate z by pi/2               14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   conj                           14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   1/z                            14/14 | 14/14            14/14 | 14/14            14/14 | 14/14           
   z * e^{0.3 i}                  0/14 | 0/14              0/14 | 0/14              0/14 | 0/14             
   z + 0.3 (shift, real)          14/14 | 0/14             14/14 | 0/14             14/14 | 0/14            
   z + 0.3 i (shift, imag)        0/14 | 14/14             0/14 | 14/14             0/14 | 14/14            

SC-04  which live reading of the address carries topic?  16 prompts, 4 subjects (chance 1-NN = 0.25)
   feature of the projected address   inter/intra dist   leave-one-out 1-NN
   7 chart energies (box-kite lens)   0.946              0.188
   15 Walsh coefficients of v^2 (chi_1..15) 0.941              0.062
   16 raw energies v_k^2              0.941              0.062
   16 raw |v_k|                       0.949              0.125
```

### demarrais_deformation_battery: output_part6a.txt

```
ordered ZD pairs 336
(a) frame-preserving index maps: 168
    element orders in the 168: {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}  (PSL(2,7): 1x1, 2x21, 3x56, 4x42, 7x48)
    unsigned permutation matrices (no sign lift) that keep ALL 336 pairs: 21 of 168
    their element orders: {1: 1, 3: 14, 7: 6}
    closed under composition (a subgroup)? True
    orbit of strut 1 under it: [1, 2, 3, 4, 5, 6, 7]  -> transitive on the 7 struts? True

(b) {4:8:4}: eigen-blocks of R_y^T R_y for each of the 84 diagonals y (x -> x y)
    eigenvalues of R^T R: [np.float64(0.0), np.float64(2.0), np.float64(4.0)] dims: {'null (gain 0)': 4, 'gain |y|': 8, 'gain sqrt2|y|': 4}
    index weight of each block (diag of projector, indices 0..15):
      null        [0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5]
      gain 1      [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
      gain sqrt2  [0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5]
    the 4 edge-partners x (x y = 0): [(4, 5, -1), (5, 4, 1), (6, 7, 1), (7, 6, -1)]
    they span rank 4; fraction of each lying in the null block: [1.0, 1.0, 1.0, 1.0]
    where the 84 diagonals sit relative to y=(2,3,+): (norm in null / gain1 / gain-sqrt2)
      (0.500 0.707 0.500) x48  e.g. (1, 4, 1) 
      (0.707 0.000 0.707) x16  e.g. (4, 6, 1) 
      (0.000 1.000 0.000) x12  e.g. (1, 2, 1) y itself
      (0.000 0.000 1.000) x4   e.g. (4, 5, 1) 
      (1.000 0.000 0.000) x4   e.g. (4, 5, -1) 
    chart 1 assessors: [(2, 3), (3, 2), (4, 5), (5, 4), (6, 7), (7, 6)]  y=(2,3): opposite vertex is the reversal (3,2)
      reversal (3, 2, 1) : null 0.000, gain1 1.000, gain-sqrt2 0.000
      reversal (3, 2, -1) : null 0.000, gain1 1.000, gain-sqrt2 0.000
    left-annihilator {x : y x = 0} dim 4 ; principal-angle overlap with the right-annihilator: 1.000
    gain-sqrt2 block vs left-annihilator overlap: 0.000
    overlap of the emerger's fixed index sets with the real blocks of this diagonal (tr(P_idx P_block)/dim):
      {4..7}         null 0.50  gain1 0.00  gain-sqrt2 0.50
      {1,2,3,8..11}  null 0.00  gain1 0.88  gain-sqrt2 0.00
      {12..15}       null 0.50  gain1 0.00  gain-sqrt2 0.50
```

### demarrais_deformation_battery: output_part6b.txt

```
(a2) index maps A that are AUTOMORPHISMS with all signs +1 (pure relabelling): 21 of 168

(b2) for each of the 84 diagonals: the character u such that  gain-1 block = coordinate subspace {i : chi_u(i)=+1}
   u = (4,) : 12 diagonals, e.g. [(1, 2, 1), (1, 2, -1), (1, 3, 1)]
   u = (2,) : 12 diagonals, e.g. [(1, 4, 1), (1, 4, -1), (1, 5, 1)]
   u = (6,) : 12 diagonals, e.g. [(1, 6, 1), (1, 6, -1), (1, 7, 1)]
   u = (1,) : 12 diagonals, e.g. [(2, 4, 1), (2, 4, -1), (2, 6, 1)]
   u = (5,) : 12 diagonals, e.g. [(2, 5, 1), (2, 5, -1), (2, 7, 1)]
   u = (3,) : 12 diagonals, e.g. [(3, 4, 1), (3, 4, -1), (3, 7, 1)]
   u = (7,) : 12 diagonals, e.g. [(3, 5, 1), (3, 5, -1), (3, 6, 1)]
   by strut of the plane (a XOR b) -> u :
      strut 1 -> u [(2,), (4,), (6,)]
      strut 2 -> u [(1,), (4,), (5,)]
      strut 3 -> u [(3,), (4,), (7,)]
      strut 4 -> u [(1,), (2,), (3,)]
      strut 5 -> u [(2,), (5,), (7,)]
      strut 6 -> u [(1,), (6,), (7,)]
      strut 7 -> u [(3,), (5,), (6,)]

(c) 132 bracketings of 7 factors (Catalan(6) = 132)
   pencil r : bracketings giving rank 1 (single-phase law) / total 132 ; distinct sign patterns among them
   r= 1 : rank1 132/132 ; rank histogram {1: 132} ; patterns 7
   r= 2 : rank1 132/132 ; rank histogram {1: 132} ; patterns 7
   r= 4 : rank1 132/132 ; rank histogram {1: 132} ; patterns 7
   r= 8 : rank1 132/132 ; rank histogram {1: 132} ; patterns 14
   r= 9 : rank1  52/132 ; rank histogram {1: 52, 4: 56, 6: 21, 7: 3} ; patterns 3
   r=10 : rank1   0/132 ; rank histogram {4: 34, 5: 52, 6: 31, 7: 15} ; patterns 0
   r=12 : rank1   0/132 ; rank histogram {5: 116, 6: 12, 7: 4} ; patterns 0
   r=15 : rank1  10/132 ; rank histogram {1: 10, 4: 22, 5: 82, 6: 12, 7: 6} ; patterns 2
      r= 1 patterns that are +/- Hadamard rows: 3 of 7 ; non-Hadamard e.g. ['+-++-+-', '++-+++-', '+++----']
      r= 2 patterns that are +/- Hadamard rows: 3 of 7 ; non-Hadamard e.g. ['+---+--', '+----++', '+-++-+-']
      r= 4 patterns that are +/- Hadamard rows: 3 of 7 ; non-Hadamard e.g. ['+----++', '+++-+++', '+++----']
      r= 8 patterns that are +/- Hadamard rows: 0 of 14 ; non-Hadamard e.g. ['+-+++-+', '+-----+', '++-----']
      r= 9 patterns that are +/- Hadamard rows: 2 of 3 ; non-Hadamard e.g. ['+-++-+-']
      r=10 patterns that are +/- Hadamard rows: 0 of 0 ; non-Hadamard e.g. []
      r=12 patterns that are +/- Hadamard rows: 0 of 0 ; non-Hadamard e.g. []
      r=15 patterns that are +/- Hadamard rows: 1 of 2 ; non-Hadamard e.g. ['++-+--+']

   firing order (permuting the 7 stations, left-bracketed product), 300 random permutations per pencil:
   r= 1 : rank histogram {1: 300} ; rank-1 orders 300/300 ; sign patterns 10 distinct
   r= 9 : rank histogram {1: 11, 4: 71, 5: 129, 6: 51, 7: 38} ; rank-1 orders 11/300 ; sign patterns 3 distinct
   r=10 : rank histogram {1: 9, 4: 73, 5: 129, 6: 53, 7: 36} ; rank-1 orders 9/300 ; sign patterns 3 distinct

(d) kernel fiber as written: support {e0, e_a, e_b}; strut s = a XOR b -> the Fano line {a, b, s}
   strut 1 : (a,b)=(2,3), s=1 : span{e0,e_a,e_b,e_s} closed under products (a quaternion subalgebra)? True ; span{e0,e_a,e_{b+8}} closed? False
   strut 2 : (a,b)=(1,3), s=2 : span{e0,e_a,e_b,e_s} closed under products (a quaternion subalgebra)? True ; span{e0,e_a,e_{b+8}} closed? False
   strut 5 : (a,b)=(1,4), s=5 : span{e0,e_a,e_b,e_s} closed under products (a quaternion subalgebra)? True ; span{e0,e_a,e_{b+8}} closed? False
   emerger.domain_of({a,b,s}) strut 1 = H ; domain_of({a, b+8}) = FRAGMENT
   emerger.domain_of({a,b,s}) strut 2 = H ; domain_of({a, b+8}) = FRAGMENT
   emerger.domain_of({a,b,s}) strut 5 = H ; domain_of({a, b+8}) = FRAGMENT
```

### demarrais_deformation_battery: output_part6c.txt

```
(i) pure-relabelling automorphisms == unsigned maps keeping all 336 ZD pairs ?  sizes 21, 21 ; identical sets: True
(ii) rule 'u = the unique nonzero u in F2^3 with u.a = u.b = 0' reproduces the 8-block for all 84 diagonals: failures = 0 ; diagonals per u: {4: 12, 2: 12, 6: 12, 1: 12, 5: 12, 3: 12, 7: 12}
(iii) u=4 : 8-block indices [0, 1, 2, 3, 8, 9, 10, 11] closed under XOR (a subalgebra): True
(iii) u=2 : 8-block indices [0, 1, 4, 5, 8, 9, 12, 13] closed under XOR (a subalgebra): True
(iii) u=1 : 8-block indices [0, 2, 4, 6, 8, 10, 12, 14] closed under XOR (a subalgebra): True
(iv) characters u in 1..15 that arise as a diagonal's {4:8:4} split: [1, 2, 3, 4, 5, 6, 7] ; never: [8, 9, 10, 11, 12, 13, 14, 15]
```

### demarrais_deformation_battery: output_part7.txt

```
(a) Assessor planes of each strut have index XOR s+8; pencil(r) stations that are Assessor planes:
   strut 1: XOR set [9] ; pencil(9) = [(1, 8), (2, 11), (3, 10), (4, 13), (5, 12), (6, 15), (7, 14)]
   strut 2: XOR set [10] ; pencil(10) = [(1, 11), (2, 8), (3, 9), (4, 14), (5, 15), (6, 12), (7, 13)]
   strut 3: XOR set [11] ; pencil(11) = [(1, 10), (2, 9), (3, 8), (4, 15), (5, 14), (6, 13), (7, 12)]
   strut 4: XOR set [12] ; pencil(12) = [(1, 13), (2, 14), (3, 15), (4, 8), (5, 9), (6, 10), (7, 11)]
   strut 5: XOR set [13] ; pencil(13) = [(1, 12), (2, 15), (3, 14), (4, 9), (5, 8), (6, 11), (7, 10)]
   strut 6: XOR set [14] ; pencil(14) = [(1, 15), (2, 12), (3, 13), (4, 10), (5, 11), (6, 8), (7, 9)]
   strut 7: XOR set [15] ; pencil(15) = [(1, 14), (2, 13), (3, 12), (4, 11), (5, 10), (6, 9), (7, 8)]
   pencil( 1): 0 of 7 stations are Assessor planes
   pencil( 2): 0 of 7 stations are Assessor planes
   pencil( 3): 0 of 7 stations are Assessor planes
   pencil( 4): 0 of 7 stations are Assessor planes
   pencil( 5): 0 of 7 stations are Assessor planes
   pencil( 6): 0 of 7 stations are Assessor planes
   pencil( 7): 0 of 7 stations are Assessor planes
   pencil( 8): 0 of 7 stations are Assessor planes
   pencil( 9): 6 of 7 stations are Assessor planes
   pencil(10): 6 of 7 stations are Assessor planes
   pencil(11): 6 of 7 stations are Assessor planes
   pencil(12): 6 of 7 stations are Assessor planes
   pencil(13): 6 of 7 stations are Assessor planes
   pencil(14): 6 of 7 stations are Assessor planes
   pencil(15): 6 of 7 stations are Assessor planes

(b) rank of the gradient set of H(phi) over 60 random points (left bracketing, natural station order):
   r= 1  singular values [15.886, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 2  singular values [14.652, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 3  singular values [14.726, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 4  singular values [14.614, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 5  singular values [15.713, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 6  singular values [14.353, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 7  singular values [15.119, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 8  singular values [15.436, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r= 9  singular values [14.329, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] -> rank 1
   r=10  singular values [8.984, 7.623, 4.407, 3.729, 0.0, 0.0, 0.0] -> rank 4
   r=11  singular values [9.901, 8.065, 4.846, 3.992, 0.0, 0.0, 0.0] -> rank 4
   r=12  singular values [13.885, 5.733, 5.174, 5.062, 4.092, 0.0, 0.0] -> rank 5
   r=13  singular values [6.152, 5.316, 5.095, 4.394, 3.73, 0.0, 0.0] -> rank 5
   r=14  singular values [10.559, 8.186, 5.196, 4.39, 3.316, 0.0, 0.0] -> rank 5
   r=15  singular values [7.649, 6.784, 5.51, 5.261, 3.494, 0.0, 0.0] -> rank 5

(c) negative results: is it alternativity or associator counts?
   e_r(e_r e_a) = -e_a fails for 0 (r,a) pairs
   pencil  1: nonzero [e_ak,e_al,e_r] in 18/21 ; [e_ak,e_r,e_al] in 15/21 ; rank 1
   pencil  8: nonzero [e_ak,e_al,e_r] in 21/21 ; [e_ak,e_r,e_al] in 21/21 ; rank 1
   pencil  9: nonzero [e_ak,e_al,e_r] in  9/21 ; [e_ak,e_r,e_al] in 21/21 ; rank 1
   pencil 10: nonzero [e_ak,e_al,e_r] in  9/21 ; [e_ak,e_r,e_al] in 21/21 ; rank 4
   pencil 15: nonzero [e_ak,e_al,e_r] in  9/21 ; [e_ak,e_r,e_al] in 21/21 ; rank 5

(d) mechanism: each station = e_a * exp(eta e_r phi) with e_a^-1 e_b = eta e_r ; product of the bare e_a (phi=0):
   r= 1 : all stations +/- e_r: True   eta=--+-++-  prod(e_a) = -1 e_0
   r= 2 : all stations +/- e_r: True   eta=+----++  prod(e_a) = -1 e_0
   r= 3 : all stations +/- e_r: True   eta=--+-++-  prod(e_a) = -1 e_0
   r= 4 : all stations +/- e_r: True   eta=+++----  prod(e_a) = -1 e_0
   r= 5 : all stations +/- e_r: True   eta=-+--+-+  prod(e_a) = -1 e_0
   r= 6 : all stations +/- e_r: True   eta=--+-++-  prod(e_a) = -1 e_0
   r= 7 : all stations +/- e_r: True   eta=+----++  prod(e_a) = -1 e_0
   r= 8 : all stations +/- e_r: True   eta=+++++++  prod(e_a) = -1 e_0
   r= 9 : all stations +/- e_r: True   eta=-+-+--+  prod(e_a) = -1 e_0
   r=10 : all stations +/- e_r: True   eta=--+++--  prod(e_a) = -1 e_0
   r=11 : all stations +/- e_r: True   eta=+--+-+-  prod(e_a) = -1 e_0
   r=12 : all stations +/- e_r: True   eta=----+++  prod(e_a) = -1 e_0
   r=13 : all stations +/- e_r: True   eta=+-+---+  prod(e_a) = -1 e_0
   r=14 : all stations +/- e_r: True   eta=++--+--  prod(e_a) = -1 e_0
   r=15 : all stations +/- e_r: True   eta=-++--+-  prod(e_a) = -1 e_0
```

### demarrais_deformation_battery: output_part8.txt

```
Lambert W values (mpmath):  W(0) = 0.0000000000000000   W(1) = 0.5671432904097838   W(-1/e) principal = -1.0000000000000000   W_-1(-1/e) = -1.0000000000000000
   W(1)*exp(W(1)) = 1.0000000000000000 (the fixed point of x -> exp(-x): 0.5671432904097838)
   d*_taut = W(1)/ln10 = 0.246307201473 ; d*_ln10 = d* x ln10 = 0.5671432904097838 = W(1): True

THE THREE LAMBERT-W VALUES as the doubling parameter mu4 (mu1..3 = -1):
   mu4 = W(0) = 0                                 pairs=1764  degree=[42]   within-chart=252  kappa=[]
   mu4 = W(1) = +0.5671 (as the value itself)     pairs=84    degree=[2]    within-chart=84   kappa=[1.3279, -1.3279]
   mu4 = -W(1) = -0.5671                          pairs=168   degree=[4]    within-chart=168  kappa=[1.3279, -1.3279]
   mu4 = W(-1/e) = -1                             pairs=168   degree=[4]    within-chart=168  kappa=[1.0, -1.0]

THE FOUR d* FACES as mu4 = -d  (tilt of the standard kite):
   d*  (Boundary) = 0.24631                       pairs=168   degree=[4]    within-chart=168  kappa=[2.0149, -2.0149]
   d*_taut (Flow) = W(1)/ln10                     pairs=168   degree=[4]    within-chart=168  kappa=[2.0149, -2.0149]
   d*_ln(10) (Translator) = W(1)                  pairs=168   degree=[4]    within-chart=168  kappa=[1.3279, -1.3279]
   d*_RG (Stability): dimension 8 as -8           pairs=168   degree=[4]    within-chart=168  kappa=[0.3536, -0.3536]
   d*_RG target value 0.24631 (same as d*)        pairs=168   degree=[4]    within-chart=168  kappa=[2.0149, -2.0149]
   ln(10)  (the thing being built)                pairs=168   degree=[4]    within-chart=168  kappa=[0.659, -0.659]

THE 4 x 3 TABLE: mu4 = -(d*_face x W_value) is NOT used (no defined interaction); see record §6 for what is and is not established.
```

# Appendix B — other constants tried (not necessary for ln(10) in UNS)

Tried at Cody's request ("pi, phi, ln(10) (all four versions of d*), i, e, etc.", "0, 1"). Entered as μ₄ = −c (the standard class, tilted to κ = 1/√c; entering as +c gives the split class, 84 pairs, degree 2, same |κ|).
Raw scan in Appendix A (`output_part2.txt`, DM-13/14/15):

| c | κ = 1/√c | tilt arctan κ |
|---|---|---|
| 1/2 | 1.4142 | 54.74° |\n| sqrt 2 | 0.8409 | 40.06° |\n| 2 | 0.7071 | 35.26° |\n| e | 0.6065 | 31.24° |\n| pi | 0.5642 | 29.43° |\n| phi (golden ratio) | 0.7862 | 38.17° |\n| d*_spec 0.24600 (disputed fifth) | 2.0162 | 63.62° |\n| GAP 7.0736e-4 | 37.6060 | 88.48° |

- **0 and 1:** μ₄ = 0 → degenerate (1,764 pairs, degree 42) = W(0); μ₄ = −1 → the standard kite (κ = 1), μ₄ = +1 → split (84 pairs) = the W(−1/e) = −1 entry and its sign flip. As an angle, 0 and 1 rad give defects 1.4142 and 0.4259; as a phase scale, 0 gives H = −1 for every strut and 1 is the baseline.
- **i:** μ₄ = ±i → 252 pairs, degree 6, complex slopes κ = (±1 ± i)/√2; as a phase scale, −cos(iS) = −cosh(S), leaving [−1, 1] (struts 1,3,6 stay at −1).
- **e, π, φ, √2 as angles / phase scales:** see `output_part2b.txt` (iii), (iv).
- **GAP in all four levels:** an apparent 537-pair row was a numerical-threshold artifact (μ³ = 3.5e-10 < 1e-9); at tolerance 1e-14 it is 252 = the standard count.


---

# Addendum 2026-10-13 — genealogy, portals, G₂ decomposition, moving-kite invariants, Lambert-W, the paper update

**What this addendum adds** (second pass of the session; everything is in `.claude/scratchpad/2026-10-13_portals_inventory_moving_kite/`, outputs in Appendix C):

1. **The factorisation** of the box-kite into relations, from nothing to a strut — written up as its own page, `Boxkite-Relational-Atlas.md`. Headline [MEASURED]: an Assessor is an *ordered pair of distinct
   points of the Fano plane* `P` (`7 × 6 = 42`), the strut label `s = a⊕b` is the third point of their line, chart `s` is the plane with the point `s` removed (its three antipodal pairs are the three lines through `s`),
   edges are pairs on different lines through `s`, and the whole structure comes from one choice (the antiflag `(e₈, P)`) and one cocycle (the Cayley–Dickson signs).
2. **Sub-algebra census (corrects genealogy.py's first pass):** 35 quaternion lines; of the 15 order-8 subgroups, **8 are octonions and 7 are not** (not alternative, composition fails).
3. **The sign gauge:** every face of every kite carries sign-holonomy −1 (all 8 frustrated); the best diagonal assignment satisfies 8 of 12 edges.
4. **Portals:** all 84 diagonals lie on one continuous `G₂`-orbit (83 of 83 reached, residual ≤ 1e-12); the struts are not separate. Inside a zero divisor: a 3-sphere of partners with the four lattice neighbours as an orthonormal frame.
5. **`G₂` decomposition:** `ℝ¹⁶ = ℝe₀ ⊕ ℝe₈ ⊕ 7 ⊕ 7`; fixed subspace `span(e₀, e₈)` = the `{2:14}` pointer.
6. **Definition-level checks:** the octonions are a Clifford module under left multiplication and the sedenions are not (the failure is the non-alternativity); both hexagon identities hold for `(φ, β)` — the table is an algebra in a braided monoidal category; the 35 lines of `PG(3,2)` ↔ the 35 points of the Klein quadric.
7. **Moving-kite readings:** invariants (norm, `e₀`/`e₈` weights, lower/upper split, singular spectra of `L_v`, `R_v`, associator norm) versus frame-relative readings (chart energies, `local_curvature`, every Walsh coefficient including ptol's `Γ`, the `σ_RB` tilt).
8. **The three Lambert-W values** reproduced to 40 digits with three methods; `W(−1/e)` is a double root.
9. **The scalar/scaled split is now explicit.** The pencil / string / flashlight / `Φ(w)` / tension-law machinery (§§2–3, §9–10 of this record) belongs to the **seven ordered pairs — a discrete, static object, the scalar context box kite**. It was wrongly extended to the scaled Mind's-Eye kite in Phase 40 §7; that is corrected there. The scaled kite has to move as de Marrais's kite moves (§§5.3 and 6 above and the atlas §6–§8).
11. **Lambert W as a fixed-point multiplier and its UNS values** (`2026-10-13_lambert_dynamics_uns/`, output in Appendix C): four tests → three values (W₀ and W₋₁ meet at the double root); `W(1)` in UNS is `d*_taut`, `W(−1/e)` in UNS is `−log₁₀ e`; `−W(λ)` is the fixed-point multiplier of `e^{−λx}` (flip at `λ = e`, no further cascade), `−W(−λ)` that of `e^{λx}` (fold at `λ = 1/e`); the double root is a Whitney fold and the cardioid cusp is the same multiplier `+1`. Atlas §10.
10. **The paper** (`ScalarContextPropagation` v4.0 and its README, branch `scalar-context-propagation`) gained §9.7 (the seven ordered pairs laid out: 3 axes + pivot + 3 shadows, the station as `e_a·exp(η e_r φ)`, the one-signed-phase law, Listing 9.7 + transcript, bracketing and firing order) and §9.8 (how they differ from de Marrais's chart) and new appendix scripts 12–13; edited in a git worktree, **uncommitted**.

### Corrections log, continued

| # | Said earlier | Corrected to | Where found |
|---|---|---|---|
| 10 | Phase 40 §7: string machinery applied to the *scaled* Mind's-Eye kite | The pencil / string is the discrete scalar object; the scaled kite is a different object (the moving `G₂` kite). Scope note added to Phase 40. | Cody, 2026-10-13 |
| 11 | genealogy.py: "order 8: 50 subgroups", 0 octonions | The census included 35 order-4 spans; correct: 15 order-8, **8 octonions + 7 non-alternative** | genealogy2.py |
| 12 | genealogy.py: "faces whose three vertices can all mutually annihilate: 0" read as a finding | It is the sign frustration (all 8 faces have holonomy −1), measured directly in genealogy2.py | genealogy2.py |
| 13 | lambert3.py first run: Newton at `W(−1/e)` printed no ratios | scipy returns `nan` at the branch point, which broke my root; with the exact root −1 the error ratio tends to ½ (double root) | lambert3.py |

# Appendix C — verbatim captured output, 2026-10-13 scripts

### ../2026-10-13_lambert_dynamics_uns/output_lambert_uns.txt

```
1. THE FOUR TESTS (principal branch W0 at x = 0, 1, -1/e ; the second real branch W-1 at x = -1/e)
   W0(0)       = 0.0
   W0(1)       = 0.5671432904097838729999687
   W0(-1/e)    = -0.99999999999999999999758
   W-1(-1/e)   = -1.00000000000000000000242
   distinct values (to 15 digits): 3 ; counted with multiplicity (the branch point is a double root): 4
   numerical splitting of the double root: W0(-1/e) - W-1(-1/e) = 4.8399e-21  (evaluating at a 40-digit -1/e, error ~1e-41, splits the pair by ~ sqrt(2 e x error): the square-root sensitivity IS the double root)

2. THE VALUES IN UNIVERSAL NATIVE SPACE (UNS = decimal-log metric ds = d.log10(p): divide a natural-log quantity by ln 10)
   ln 10 = 2.302585092994045684 ; 1/ln 10 = log10(e) = 0.43429448190325182765 ; d*_taut = W(1)/ln 10 = 0.24630720147342257805
   value       natural scale              UNS (value / ln 10)        in units of d*_taut       
   W0(0)       0.0                        0.0                        0.0                       
   W0(1)       0.567143290409783873       0.24630720147342257805     2.302585092994045684      
   W0(-1/e)    -1.0                       -0.43429448190325182765    -4.0599706140053868953    
   W-1(-1/e)   -1.0                       -0.43429448190325182765    -4.0599706140053868953    
   sum of the four tests: -1.432856709590216127 = Omega - 2 ; UNS: -0.62228176233308107725 = d*_taut - 2/ln10 : -0.62228176233308107725 ; in d*_taut units: -5.8173561350167281067
   W(1) in UNS IS d*_taut (the Flow);  W(-1/e) in UNS is -log10(e) = -0.4342944819...;  W(1) = ln10 x d*_taut (the Translator)
   1/d*_taut = ln10/Omega = 4.0599706140053868953

3. W AS THE FIXED-POINT MULTIPLIER.  f_lam(x) = exp(-lam x): fixed point x* = W(lam)/lam ; multiplier f'(x*) = -lam x* = -W(lam)
   lam      W(lam)        multiplier -W(lam)   numerical f'(x*)   behaviour of the iteration (last values)
   0.0000   0.00000000    -0.00000000          -0.00000000        attracting fixed point
   1.0000   0.56714329    -0.56714329          -0.56714329        attracting fixed point
   2.0000   0.85260550    -0.85260550          -0.85260550        attracting fixed point
   2.6639   0.98992420    -0.98992420          -0.98992420        attracting fixed point
   2.7183   1.00000000    -1.00000000          -1.00000000        period 2
   3.0000   1.04990889    -1.04990889          -1.04990889        period 2
   4.0000   1.20216787    -1.20216787          -1.20216787        period 2
   8.0000   1.60581200    -1.60581200          -1.60581200        period 2
   NOTE: past lam = e the orbit settles on a period-2 cycle and stays there (tested to lam = 8): exp(-lam x) is DECREASING, so its second iterate is increasing and the real map cannot be chaotic; no cascade, no crisis in the technical sense on the real line.
   multiplier = -1 (FLIP: period doubling) at W(lam) = 1  <=>  lam = e ;  multiplier = 0 at lam = 0 (superstable) ; the idle point is lam = 1 : multiplier -Omega
   GROWTH family g_lam(x) = exp(lam x): fixed points are solutions of exp(lam x) = x, i.e. x = -W(-lam)/lam ; multiplier = -W(-lam)
      lam = 0.300000 : number of real fixed points = 2
      lam = 0.367879 : number of real fixed points = 0   (tangent: the double root; fixed point x = e, multiplier +1)
      lam = 0.400000 : number of real fixed points = 0
   (at lam = 1/e: W(-1/e) = -1 and the multiplier -W = +1: the FOLD / saddle-node; tetration's critical base e^{1/e})

4. THE FOLD IS A PROJECTION.  The curve (w, x = w e^w) is smooth and single-valued in w; dx/dw = e^w (1+w) vanishes at w = -1.  Number of real w with w e^w = x:
      x = +2.000000 : 1 real preimage(s)
      x = +0.500000 : 1 real preimage(s)
      x = +0.000000 : 1 real preimage(s)
      x = -0.100000 : 2 real preimage(s)
      x = -0.367879 : 2 real preimage(s)   <- the branch point (exactly ONE preimage, a double root; the float -1/e sits a hair above the true value, so the grid sees 2)
      x = -0.400000 : 0 real preimage(s)
   (Whitney: the generic singularity of a projection of a smooth curve/surface is a fold; the two-valuedness of W is the shadow of a smooth curve with a vertical tangent)

5. THE CARDIOID CUSP IS THE SAME MULTIPLIER +1.  Boundary of the main cardioid: c(mu) = mu/2 - mu^2/4 for the fixed-point multiplier mu = e^{i t} of z -> z^2 + c
   dc/dmu = 1/2 - mu/2 vanishes on the unit circle only at mu = 1 : c(1) = 0.2500 ; at c = 1/4 the fixed point z = 1/2 has multiplier 2z = 1.0000 (the saddle-node)
   |dc/dt| along the boundary near t = 0 (speed of the boundary point; 0 = cusp): [0.0998, 0.05, 0.0, 0.05, 0.0998]
   So the cardioid is the unit circle |mu| = 1 seen through a map with a critical point at mu = 1: a circle, flattened.
```

### output_lambert3.txt

```
1. mpmath (50 digits)
   W(0)     = 0.0   check w e^w - x = 0.0
   W(1)     = 0.5671432904097838729999686622103555497538   check w e^w - x = -1.34e-51
   W(-1/e)  = -1.0   check w e^w - x = 0.0
   W_{-1}(-1/e) = -1.0  (the second real branch meets the principal branch at the branch point)

2. scipy.special.lambertw (double precision)
   W(0)     = 0.0000000000000000
   W(1)     = 0.5671432904097838
   W(-1/e)  = nan

3. Newton on f(w) = w e^w - x from several starts: iterations to 1e-15 and the observed order
   W(0)     start +0.3 :   5 iterations ; error ratios e(n+1)/e(n) = [0.065, 0.004, 0.0]
   W(0)     start -0.5 :   7 iterations ; error ratios e(n+1)/e(n) = [0.333, 0.143, 0.023, 0.001]
   W(0)     start +1.0 :   7 iterations ; error ratios e(n+1)/e(n) = [0.333, 0.143, 0.023, 0.001]
   W(1)     start +0.3 :   5 iterations ; error ratios e(n+1)/e(n) = [0.056, 0.003, 0.0]
   W(1)     start +1.0 :   5 iterations ; error ratios e(n+1)/e(n) = [0.088, 0.008, 0.0]
   W(1)     start +2.0 :   7 iterations ; error ratios e(n+1)/e(n) = [0.416, 0.222, 0.058, 0.004]
   W(-1/e)  start -0.5 : 200 iterations ; error ratios e(n+1)/e(n) = [0.545, 0.525, 0.513, 0.507]
   W(-1/e)  start -0.8 : 200 iterations ; error ratios e(n+1)/e(n) = [0.517, 0.509, 0.505, 0.502]
   W(-1/e)  start -2.0 : 200 iterations ; error ratios e(n+1)/e(n) = [0.45, 0.478, 0.49, 0.495]
   W(-1/e)  start -0.2 : 200 iterations ; error ratios e(n+1)/e(n) = [0.572, 0.544, 0.524, 0.513]
   (a ratio ->0.5 means a DOUBLE root: linear convergence; ratios shrinking fast mean a simple root: quadratic)

4. local structure f'(w) = e^w (1+w) at each root, and the fixed-point multiplier of x -> e^{-x}
   W(0)     root +0.0000000000 : f'(root) = 1.0000000000 
   W(1)     root +0.5671432904 : f'(root) = 2.7632228344 
   W(-1/e)  root -1.0000000000 : f'(root) = 0.0000000000   <- DOUBLE root (branch point)
   x -> exp(-x) at Omega: multiplier = -exp(-Omega) = -0.5671432904 = -Omega: True   (|.|<1: attracting, alternating)
   fixed-point iteration x -> exp(-x) from 0.5 reaches Omega to 1e-12 in 44 steps (rate 0.5671 per step, predicted 0.5671)

5. relations to the four d*
   d*_taut = W(1)/ln10 = 0.246307201473423 ; d*_ln10 = d*_taut * ln10 = 0.5671432904097838 = W(1) : True
   Omega = exp(-Omega) = 0.5671432904097838 ; Omega = -ln(Omega) = 0.5671432904097840
   note: scipy.special.lambertw(-1/e) returned nan in double precision (the float -1/e sits on/just past the branch point); mpmath at 50 digits returns exactly -1.
```

### output_genealogy.txt (first pass — superseded by genealogy2)

```
LEVEL 1  index group  Z2^4 = F2^4 under XOR  (16 elements; 15 nonzero)
LEVEL 2  sign cocycle alpha(i,j) in {+-1}:  e_i e_j = alpha(i,j) e_{i xor j}   [twisted group algebra R^alpha[Z2^4]]
   every basis product is +-1 times a single basis element: True (max extra mass 0.0e+00)
   commutator sign beta(i,j) = alpha(i,j)alpha(j,i): -1 for distinct nonzero i,j: True ; +1 when i=0, j=0 or i=j: True
   (the 'braiding' data; beta is NOT a bicharacter on Z2^4: beta(i^j,k) vs beta(i,k)beta(j,k) for independent i,j,k: 2520 violations)
LEVEL 3  associator sign phi(i,j,k) = (e_i e_j) e_k / e_i (e_j e_k) in {+-1}: values seen [-1, 1] ; phi=-1 in 1848 of 4096 triples (catalog: 1848 nonzero associators)
   nonassociative (phi=-1) among DEPENDENT triples (k in span{i,j}): 0 of 931 ; among INDEPENDENT triples: 1848 of 2730

LEVEL 4  subalgebras = subgroups of Z2^4:
   order 2 (C):  15 subgroups {0,i}
   order 4 (H): 35 subgroups = the 35 lines of PG(3,2); composition (norm-multiplicative) holds in all: True
   order 8: 50 subgroups = the 15 hyperplanes ker chi_u (+0); octonion-like (composition AND every independent triple nonassociative): 0 of 50
      [0, 1, 2, 3]                       composition=True  all-independent-triples-nonassociative=False
      [0, 1, 2, 3, 4, 5, 6, 7]           composition=True  all-independent-triples-nonassociative=False
      [0, 1, 2, 3, 8, 9, 10, 11]         composition=True  all-independent-triples-nonassociative=False
      [0, 1, 2, 3, 12, 13, 14, 15]       composition=False  all-independent-triples-nonassociative=False
      [0, 1, 4, 5]                       composition=True  all-independent-triples-nonassociative=False
      [0, 1, 4, 5, 8, 9, 12, 13]         composition=True  all-independent-triples-nonassociative=False
      [0, 1, 4, 5, 10, 11, 14, 15]       composition=False  all-independent-triples-nonassociative=False
      [0, 1, 6, 7]                       composition=True  all-independent-triples-nonassociative=False
      [0, 1, 6, 7, 8, 9, 14, 15]         composition=True  all-independent-triples-nonassociative=False
      [0, 1, 6, 7, 10, 11, 12, 13]       composition=False  all-independent-triples-nonassociative=False
      [0, 1, 8, 9]                       composition=True  all-independent-triples-nonassociative=False
      [0, 1, 10, 11]                     composition=True  all-independent-triples-nonassociative=False
      [0, 1, 12, 13]                     composition=True  all-independent-triples-nonassociative=False
      [0, 1, 14, 15]                     composition=True  all-independent-triples-nonassociative=False
      [0, 2, 4, 6]                       composition=True  all-independent-triples-nonassociative=False
      [0, 2, 4, 6, 8, 10, 12, 14]        composition=True  all-independent-triples-nonassociative=False
      [0, 2, 4, 6, 9, 11, 13, 15]        composition=False  all-independent-triples-nonassociative=False
      [0, 2, 5, 7]                       composition=True  all-independent-triples-nonassociative=False
      [0, 2, 5, 7, 8, 10, 13, 15]        composition=True  all-independent-triples-nonassociative=False
      [0, 2, 5, 7, 9, 11, 12, 14]        composition=False  all-independent-triples-nonassociative=False
      [0, 2, 8, 10]                      composition=True  all-independent-triples-nonassociative=False
      [0, 2, 9, 11]                      composition=True  all-independent-triples-nonassociative=False
      [0, 2, 12, 14]                     composition=True  all-independent-triples-nonassociative=False
      [0, 2, 13, 15]                     composition=True  all-independent-triples-nonassociative=False
      [0, 3, 4, 7]                       composition=True  all-independent-triples-nonassociative=False
      [0, 3, 4, 7, 8, 11, 12, 15]        composition=True  all-independent-triples-nonassociative=False
      [0, 3, 4, 7, 9, 10, 13, 14]        composition=False  all-independent-triples-nonassociative=False
      [0, 3, 5, 6]                       composition=True  all-independent-triples-nonassociative=False
      [0, 3, 5, 6, 8, 11, 13, 14]        composition=True  all-independent-triples-nonassociative=False
      [0, 3, 5, 6, 9, 10, 12, 15]        composition=False  all-independent-triples-nonassociative=False
      [0, 3, 8, 11]                      composition=True  all-independent-triples-nonassociative=False
      [0, 3, 9, 10]                      composition=True  all-independent-triples-nonassociative=False
      [0, 3, 12, 15]                     composition=True  all-independent-triples-nonassociative=False
      [0, 3, 13, 14]                     composition=True  all-independent-triples-nonassociative=False
      [0, 4, 8, 12]                      composition=True  all-independent-triples-nonassociative=False
      [0, 4, 9, 13]                      composition=True  all-independent-triples-nonassociative=False
      [0, 4, 10, 14]                     composition=True  all-independent-triples-nonassociative=False
      [0, 4, 11, 15]                     composition=True  all-independent-triples-nonassociative=False
      [0, 5, 8, 13]                      composition=True  all-independent-triples-nonassociative=False
      [0, 5, 9, 12]                      composition=True  all-independent-triples-nonassociative=False
      [0, 5, 10, 15]                     composition=True  all-independent-triples-nonassociative=False
      [0, 5, 11, 14]                     composition=True  all-independent-triples-nonassociative=False
      [0, 6, 8, 14]                      composition=True  all-independent-triples-nonassociative=False
      [0, 6, 9, 15]                      composition=True  all-independent-triples-nonassociative=False
      [0, 6, 10, 12]                     composition=True  all-independent-triples-nonassociative=False
      [0, 6, 11, 13]                     composition=True  all-independent-triples-nonassociative=False
      [0, 7, 8, 15]                      composition=True  all-independent-triples-nonassociative=False
      [0, 7, 9, 14]                      composition=True  all-independent-triples-nonassociative=False
      [0, 7, 10, 13]                     composition=True  all-independent-triples-nonassociative=False
      [0, 7, 11, 12]                     composition=True  all-independent-triples-nonassociative=False
   order 16: the sedenions; composition fails (zero divisors): worst |xy|-|x||y| on random pairs = 3.639

LEVEL 5  projective geometry PG(3,2):  15 points, 35 lines, 15 planes (=hyperplanes), each point on 7 lines
   |GL(4,2)| = 20160 (= A8). Antiflag (point 8, plane P={1..7}): 15 x 8 = 120 antiflags -> stabiliser order 20160/120 = 168 (= |PSL(2,7)|)
   Klein correspondence count: lines of PG(3,2) = 35 = points of the Klein quadric Q+(5,2) (q^2+1)(q^2+q+1) = 35

LEVEL 6  Assessors from the antiflag (point e8, plane P = {1..7}):
   each Assessor plane span(e_a, e_{b+8}) lies on a unique PG line {a, b+8, (a^b)+8}: 42 Assessors on 21 distinct lines, [2] Assessors per line
      1 point of P, 2 outside                       not through e8   21 lines   <- the Assessor lines
      1 point of P, 2 outside                       through e8        7 lines
      in P                                          not through e8    7 lines
   struts (chart label) s = a xor b  = a point of the lower plane P:  chart s holds the Assessors (a, a^s), a not in {0,s}:  6 each, 7 charts, 42 total
   EDGE RULE: Assessors (a,b),(c,d) are joined by a vanishing product iff  a^b = c^d (same strut)  and (c,d) != (b,a) (not the reversal): predicate == measured adjacency: True (168 ordered pairs)
   the necessary identity: basis products of x=e_a+-e_{b+8}, y=e_c+-e_{d+8} cancel in pairs only if  a^c = b^d  (and  a^d = b^c),  i.e.  a^b^c^d = 0;  the signs alpha then pick which 2 of the 4 sign choices annihilate: [2] sign choices per adjacent plane pair

LEVEL 7  one box-kite (chart 1): vertices, edges, faces
   vertices 6, edges 12, triangular faces 8, non-edges (the 3 'struts' in De Marrais's sense = axes joining opposite vertices): [((2, 3), (3, 2)), ((4, 5), (5, 4)), ((6, 7), (7, 6))]
   faces whose three vertices can carry diagonals that ALL mutually annihilate (both orders): 0 ; faces where they cannot: 8
   faces carrying a one-direction cycle x1 x2 = x2 x3 = x3 x1 = 0: 0
```

### output_genealogy2.txt

```
A. proper accounting of the 4096 ordered index triples
   rank<=2 (dependent) triples: 1576 ; of those nonassociative: 0
   rank-3 (independent) ordered triples: 2520 (= 15*14*12); nonassociative: 1848

B. the 15 order-8 subgroups (hyperplanes ker chi_u, plus the 0): subalgebra type
   u= 1 [0, 2, 4, 6, 8, 10, 12, 14]        composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 2 [0, 1, 4, 5, 8, 9, 12, 13]         composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 3 [0, 3, 4, 7, 8, 11, 12, 15]        composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 4 [0, 1, 2, 3, 8, 9, 10, 11]         composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 5 [0, 2, 5, 7, 8, 10, 13, 15]        composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 6 [0, 1, 6, 7, 8, 9, 14, 15]         composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 7 [0, 3, 5, 6, 8, 11, 13, 14]        composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 8 [0, 1, 2, 3, 4, 5, 6, 7]           composition=True  alternative=True  nonassoc 168/168  -> OCTONION (composition, alternative, nonassociative)
   u= 9 [0, 2, 4, 6, 9, 11, 13, 15]        composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=10 [0, 1, 4, 5, 10, 11, 14, 15]       composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=11 [0, 3, 4, 7, 9, 10, 13, 14]        composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=12 [0, 1, 2, 3, 12, 13, 14, 15]       composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=13 [0, 2, 5, 7, 9, 11, 12, 14]        composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=14 [0, 1, 6, 7, 10, 11, 12, 13]       composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   u=15 [0, 3, 5, 6, 9, 10, 12, 15]        composition=False alternative=False nonassoc  72/168  -> composition-failing, NOT alternative
   counts: {'composition-failing, NOT alternative': 7, 'OCTONION (composition, alternative, nonassociative)': 8}

C. the oriented Fano plane P (lower octonion): e_a e_b = alpha(a,b) e_{a^b} on its 7 lines
   lines of P: [(1, 2, 3), (1, 4, 5), (1, 6, 7), (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 5, 6)]
   orientation signs alpha(a,b) for (a<b) on each line:  {(1, 2, 3): 1, (1, 4, 5): 1, (1, 6, 7): -1, (2, 4, 6): 1, (2, 5, 7): 1, (3, 4, 7): 1, (3, 5, 6): -1}

D. Assessor = ordered pair (a,b) of DISTINCT points of P ; strut s = third point of the line ; kite_s = the 6 other points
   ordered pairs of distinct points of P: 42 = 7*6 = 42 = number of Assessors: True
   the 7x7 grid P x P has 49 cells; the diagonal (a,a) is the CD pair (e_a, e_{a+8}) which has no zero divisors (normed C-like plane) -> 49 - 7 = 42
   kite_s's 6 vertices are exactly the 6 points of P other than s, grouped by the 3 lines through s: True
   octahedron edges = pairs of vertices on DIFFERENT lines through s: 12 edges, each vertex adjacent to the 4 vertices on the other two lines; the 3 non-edges = the 3 lines through s (reversal pairs)
   |GL(3,2)| = 168 ; stabiliser of strut 1 has order 24 ; its action on the 6 vertices is faithful with image of order 24
   the induced permutation group on the 3 axes (lines through s) has order 6
   (order 24 acting faithfully, with S3 on the 3 axes and kernel of order 4 = the rotation group S4 of the octahedron/cube)

E. the SIGN GAUGE on the octahedron (a Z2 field on the edges)
   for each ordered adjacent pair: annihilating (sigma_u, sigma_v) combos have sigma_u*sigma_v in: [(-1,), (1,)]
   edge constraint sigma_u sigma_v = c_uv : constant c on each edge (single value): True ; c=+1 on 12, c=-1 on 12 of 24 ordered pairs
   triangle (face) products of c around the 8 faces: [-1, -1, -1, -1, -1, -1, -1, -1]  -> +1 (consistent) faces 0, -1 (frustrated) faces 8
   best sign assignment of the 6 diagonals satisfies 8 of 12 edge constraints (12 = a consistent gauge, <12 = frustrated)

F. why zero divisors begin at the sedenions: the doubling step as projective geometry P_{n+1} = P_n + pivot + shadow(P_n)
   level 3 (dim  8): lower index group has  3 nonzero points, 1 lines through each point; cross pairs (a,b), a!=b:   6 ; diagonals  12 ; ordered annihilating diagonal pairs: 0
   level 4 (dim 16): lower index group has  7 nonzero points, 3 lines through each point; cross pairs (a,b), a!=b:  42 ; diagonals  84 ; ordered annihilating diagonal pairs: 336
   level 5 (dim 32): lower index group has 15 nonzero points, 7 lines through each point; cross pairs (a,b), a!=b: 210 ; diagonals 420 ; ordered annihilating diagonal pairs: 3696
```

### output_g2decomp.txt

```
derivations found: 14 ; max |D + D^T| (skew-symmetry) = 4.996003610813204e-16
FIXED subspace of all 14 derivations: dim 2 ; spanned by indices [0, 8]
Casimir (-sum D^2) eigenvalues with multiplicities: {np.float64(-0.0): 2, np.float64(1.0): 14}
max |off-diagonal block| (lower<->upper) of the derivations: 1.9e-16, 3.6e-16  -> halves preserved: True
derivation matrices touching e0 or e8 at all: 2.2e-16
commutant of the 14 derivations (matrices commuting with all): dim 8
intertwiners from the lower 7 to the upper 7: dim 1
the 14 derivations restricted to the lower 7 span a space of dimension 14 (so0(7) would be 21; g2 is 14)
```

### output_portals.txt

```
1. REACHABILITY: from the diagonal (2, 3, 1) can a continuous G2 flow (which preserves EVERY zero-divisor relation) carry it onto each of the other 83 diagonals?
   OTHER CHART              reachable 72 of 72
   same plane               reachable  1 of  1
   same chart, reversal     reachable  2 of  2
   same chart, neighbour    reachable  8 of  8
   residual of the best attempts: max over reachable = 1.0e-12 ; min over unreachable = none

2. THE PATH from (2, 3, 1) (chart 1) to (1, 2, 1) (chart 3)
   d1 = (2, 3, 1) is annihilated by its neighbour (4,5,-)  : |d1 y0| = 0.0e+00
   tau   |x(tau) y(tau)|   angle(x, nearest lattice diagonal) deg   dominant chart (share)   smallest singular value of L_x   straight-line |x y_min|
   0.00  0.0e+00            0.00                              1 (0.17)                 4.0e-17                       0.000
   0.25  4.2e-14           28.42                              3 (0.17)                 1.4e-14                       0.215
   0.50  8.2e-14           40.63                              2 (0.16)                 3.0e-14                       0.366
   0.75  2.0e-13           28.42                              1 (0.17)                 5.0e-14                       0.215
   1.00  1.6e-13            0.00                              3 (0.17)                 6.1e-14                       0.000

3. INSIDE a zero divisor y = (2,3,+): the annihilator N(y) = {x : x y = 0}
   dim N(y) = 4 ; every nonzero element of N(y) is itself a zero divisor (x y = 0, x != 0)
   the 4 lattice neighbours of y inside N(y): Gram matrix (cosines) =
[[1. 0. 0. 0.]
 [0. 1. 0. 0.]
 [0. 0. 1. 0.]
 [0. 0. 0. 1.]]
   a great-circle arc from neighbour 1 to neighbour 2 stays in N(y) (arc point annihilates y): |w y| = 0.0e+00
   products inside N(y): |x1 x2|/(|x1||x2|) range 1.006..1.378 ; fraction of the product that stays in N(y): 0.000..0.000  (1.0 = N(y) is closed under multiplication)
   stabiliser of y has dim 3 and acts on the 4 neighbours with rank 3 (it rotates them inside N(y) = S^3, fixing y)
```

### output_invariants.txt

```
MAX CHANGE of each reading when the address is moved by a continuous G2 deformation g = exp(0.7 D)   (3 vectors: random + 2 prompts)
   reading                                      max change   invariant under the moving kite?
   norm                                         0.000e+00    YES
   e0 weight (fixed_point_weight)               2.776e-17    YES
   e8 weight                                    3.469e-17    YES
   outside_share (e0+e8)                        6.939e-18    YES
   lower / upper energy split                   2.220e-16    YES
   chart_energy[1] (7 chart energies)           3.449e-02    no
   chart_energy[4]                              2.278e-02    no
   local_curvature (top-3 basis triples)        1.200e+01    no
   Walsh W_4 (= ptol Gamma)                     2.790e-01    no
   Walsh W_9                                    2.140e-01    no
   sigma_RB  sum tilt                           8.907e-01    no
   sigma_RB  sum axis                           0.000e+00    YES
   sing. values of L_v, smallest                2.220e-16    YES
   sing. values of L_v, largest                 2.220e-16    YES
   sing. values of R_v, smallest                0.000e+00    YES
   associator norm K(v)                         9.663e-13    YES

SAME readings under the FINITE group (168 frame-preserving index maps; sign-blind readings):  all chart/lattice readings permute covariantly (part 3 SC-02); the moving-kite invariants above need no relabelling at all.

sigma_RB frame: tilt = Re sum_k psi[k] conj psi[k^4], psi[k] = x[k] + i x[k^8]; the pairing k <-> k^4 is the red/blue pairing (Hadamard character chi_4), the pairing k <-> k^8 is the Cayley-Dickson doubling pair.
   ptol: neutron generation           sum tilt +0.507920  sum axis +0.00e+00  (axis sum is identically 0)
   ptol: the cat sat on the mat       sum tilt +0.518650  sum axis +0.00e+00  (axis sum is identically 0)
```

### output_spinor_braid.txt

```
(1) SPINOR / Clifford-module test:  max | L_a L_a + |a|^2 I |  over random imaginary a
    a in the lower octonion's imaginaries (indices 1..7):   3.55e-15   -> Clifford module Cl(0,7) on R^8 = the octonion spinor: True
    a in the 7 imaginaries {1,2,3,8,9,10,11} (another sub-octonion): 9.58e+00
    a in a NON-alternative hyperplane {2,4,6,9,11,13,15}: 1.66e+01
    a in ALL 15 sedenion imaginaries:                        1.60e+01   -> the sedenions are NOT a Clifford module under their own left multiplication: True
    norm of the failure for one random a, x: |a(ax) + |a|^2 x| = 30.211

(2) BRAID: sign-valued associator phi(i,j,k) and braiding beta(i,j) = alpha(i,j)/alpha(j,i) on Z2^4
    hexagon 1:  phi(j,k,i) beta(i,j^k) phi(i,j,k) = beta(i,k) phi(j,i,k) beta(i,j)   violations over all 4096 (i,j,k): 0
    hexagon 2:  phi(k,i,j) beta(i^j,k) phi(i,j,k) = beta(i,k) phi(i,k,j) beta(j,k)   violations over all 4096 (i,j,k): 0
    phi = coboundary of alpha:  phi(i,j,k) = alpha(i,j) alpha(i^j,k) alpha(j,k) alpha(i,j^k): violations 0
    (if the hexagons hold, the multiplication table is an algebra in a braided monoidal category of Z2^4-graded spaces: braiding = commutator sign, associator = nonassociativity sign, both generated by the single cocycle alpha)
    beta is not a bicharacter (2520 violations, genealogy.py), so this braiding is NOT the trivial/symmetric one: it is carried by the associator phi.
```
