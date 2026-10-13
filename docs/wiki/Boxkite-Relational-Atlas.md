# The Sedenion Box-Kite as Relations — from nothing to a strut

**Written 2026-10-13** (Claude Sonnet 5.5, with Cody). Everything marked **[MEASURED]** was computed from the multiplication
table by a script in `.claude/scratchpad/2026-10-13_portals_inventory_moving_kite/` (genealogy.py, genealogy2.py, g2decomp.py,
portals.py, invariants.py, spinor_braid.py, lambert3.py; captured outputs beside them) or in
`2026-10-12_demarrais_deformation_battery/`. **[LIT]** = standard mathematics stated from the literature, not re-verified here.
**[HYP]** = a reading, with the test that would settle it.

**The question this page answers (Cody):** what is every part of de Marrais's sedenion box-kite made of, down to its smallest
components — which are *relations*, not numbers — and what are the named groupings (spinors, fibres, braids, twistors, indices …)
composites **of**, all the way to the Assessors and struts?

**The short answer.** There are only a handful of primitive relations (§1). Everything else — the 15 imaginary units, the 35 quaternion
triples, the 15 sub-algebras, the Fano plane, the Assessors, the struts, the edges, the zero divisors — is a composite of them, and
the whole box-kite is fixed by **one choice** (a pivot point `e₈` and the plane `P` that does not contain it) plus **one cocycle** (the
Cayley–Dickson sign table). Numbers (42, 84, 168, 336, 2,688) appear only as *counts of consequences*.

---

## 1. The primitive relations (the smallest components)

| # | relation | what it relates | definition | how it was checked |
|---|---|---|---|---|
| R0 | **zero / neutral** | one thing | the index `0` is neutral for XOR; `e₀` is the multiplicative identity and the real axis. "Zero value, not no value": it is a *present* element that every other element acts through and none acts on. | `e₀` is in no Assessor; fixed by every derivation (below) |
| R1 | **sign** | one thing (an orientation) | a choice in `{+1, −1}` (the group `ℤ/2`); also the conjugation `e₀ ↦ e₀`, `eₖ ↦ −eₖ (k>0)` | `e_k² = −1` for every `k>0` |
| R2 | **bit / doubling** | a thing and its new half | one Cayley–Dickson step adjoins one binary coordinate; four steps give the 4-bit index word | `ℝ→ℂ→ℍ→𝕆→𝕊` = 1,2,4,8,16 components |
| R3 | **collinearity (XOR)** | three things | `i ⊕ j = k` — "`k` is the third point on the line through `i` and `j`". The *only* structural relation on the index set. | all basis products land on `e_{i⊕j}` (max extra mass `0.0`) |
| R4 | **handedness** `α(i,j)` | an ordered pair | the sign in `e_i e_j = α(i,j) e_{i⊕j}` — a 2-cochain `{±1}`-valued on `ℤ/2⁴` (the Cayley–Dickson cocycle) | the whole multiplication table is `α` |
| R5 | **commutator sign** `β(i,j)` | a pair | `β(i,j) = α(i,j)/α(j,i)`: `−1` for distinct nonzero `i, j`, `+1` if either is `0` or `i = j` | **[MEASURED]** both statements, all 256 pairs |
| R6 | **associator sign** `φ(i,j,k)` | a triple | `(e_i e_j)e_k = φ · e_i(e_j e_k)`; **`φ = ∂α`**, the coboundary of the handedness | **[MEASURED]** 0 violations over all 4096 triples |
| R7 | **annihilation** | two elements | `xy = 0`: the signed basis products cancel in pairs. Needs R3 (index coincidence) and R4 (sign) together. | §3 |

R0–R4 are *given* by the Cayley–Dickson construction; R5, R6 are *derived* from R4 (a commutator and an associator are what a cocycle
looks like when you ask whether it commutes or associates); R7 is the first relation that **needs two others at once** — which is why
it appears late (§5).

**Not primitive, and worth saying so:** a *number*. 1,848 (nonzero associators), 168 (`|PSL(2,7)|`), 42 Assessors are all counts of
how often a relation holds, not inputs to anything.

## 2. The genealogy, bottom-up (each level is a composite of the one before)

| level | structure | composite of | relation used | count **[MEASURED]** |
|---|---|---|---|---|
| 0 | nothing / `e₀` | — | R0 | 1 |
| 1 | the 4-bit **index group** `ℤ/2⁴` | four doublings | R2 | 16 elements |
| 2 | the 15 **imaginary units** = points of `PG(3,2)` | nonzero indices | R3 | 15 |
| 3 | **lines** (quaternion triples) `{i, j, i⊕j}` | two points + their XOR | R3 | 35; all 35 span closed 4-dim subalgebras with composition (≅ ℍ) |
| 4 | **planes** (7 points + 0) = kernels of the 15 **characters** `χ_u` | lines + R3 closure | R3 + duality | 15 hyperplanes ↔ 15 `u` |
| 5 | **sub-octonions** | planes with the right `φ` | R3 + R4 + R6 | **8 of the 15 hyperplanes** have composition, alternativity and every independent triple nonassociative (octonions); **7 do not** (composition fails, not alternative, nonassociative in only 72/168 triples) |
| 6 | the **antiflag** `(e₈, P)` | one point + one plane not containing it | a *choice* | 15 × 8 = 120 antiflags; stabiliser in `GL(4,2) ≅ A₈` (order 20,160) has order **168** |
| 7 | the **oriented Fano plane** `P` | `P = {1…7}` + the signs `α` on its 7 lines | R3 + R4 | the octonion multiplication table (one of 480) |
| 8 | the **shadow** `x ↦ x+8` | `e₈` pairs each lower point with an upper one | R2 | 7 shadow points + the pivot `e₈` |
| 9 | the **Assessor** `(a, b)` | an *ordered pair of distinct points of `P`*, read as the plane `span(e_a, e_{b+8})` | shadow + off-diagonal | `7 × 6 = 42` (the 49 cells of `P×P` minus the 7 diagonal ones `(a,a)`, which are normed planes with no zero divisor) |
| 10 | the **strut label** `s = a ⊕ b` | the third point of the line through `a, b` | R3 | 7 values (the points of `P`) |
| 11 | the **diagonal** `e_a ± e_{b+8}` | an Assessor + a sign | R1 | 84 |
| 12 | the **edge** | two Assessors, same `s`, on different lines through `s` | R3 (necessary: `a⊕b⊕c⊕d = 0`) + R4 (selects 2 of 4 sign choices) + R7 | 84 edges (12 per kite); predicate "same `s`, not the reversal" = measured adjacency exactly (168 ordered plane pairs) |
| 13 | the **face** (triangle) | three mutually adjacent Assessors, one from each antipodal pair | R7 on three | 8 per kite, 56 total; **all 8 carry sign-holonomy −1** (§3) |
| 14 | the **axis** ("strut" in de Marrais's sense) | an antipodal pair = a line of `P` through `s` | R3 | 3 per kite, 21 total |
| 15 | the **kite** (chart `s`) | the plane `P` with the point `s` removed; 3 axes as antipodal pairs | levels 9–14 | 7 |
| 16 | the **zero divisor** | a diagonal; its annihilator `N(y)` | R7 | 168 primitive unit ZDs (= 42 × 4), 336 ordered ZD pairs |

**The whole kite from one choice and one cocycle.** Choose the antiflag `(e₈, P)` (which doubling bit is the last one). The cocycle `α`
supplies every sign. From those two inputs, and no numbers, levels 7–16 follow.

## 3. The box-kite, factored

**Chart `s` is the Fano plane with the point `s` removed.** Its six vertices are the six other points of `P` (Assessor `(a, a⊕s)`);
its three antipodal pairs `(a, a⊕s) ↔ (a⊕s, a)` are the three lines of `P` through `s`. Two vertices are adjacent exactly when they lie
on *different* lines through `s`. [MEASURED: `kite_s` = the six points other than `s`, grouped by the three lines through `s`, for all 7 `s`.]

**Symmetry.** The stabiliser of `s` in `GL(3,2)` has order 24 and acts faithfully on the six vertices as `S₃` on the three axes with a
kernel of order 4 — the rotation group of the octahedron. The full monomial automorphism group (signs included) has order
`16 × 168 = 2,688`: the 16 Hadamard sign characters times the 168.

**Why an "edge" is a *relation* and not an object.** The *vertices* are the zero divisors (two per Assessor). An *edge* is the
vanishing of a **two-factor product** `xy = 0` between zero divisors of two Assessors. (The phrase "binary" is avoided here to keep it
apart from binary notation: an edge is a two-factor product relation.) Because it has only two factors, no grouping ever enters it —
which is the first structural difference from the seven-factor ordered product of the scalar construct (paper §9.7–§9.8).

**The sign gauge (new).** On each edge the annihilating sign choices satisfy `σ_u σ_v = c_uv` with `c_uv` a fixed sign. Around every one of
the 8 faces of a kite the product of the three `c` is **−1**: the Z₂ field on the octahedron is *frustrated* on every face, so no choice of
one diagonal per vertex satisfies all 12 edges (the best satisfies 8). The edges are relations whose signs cannot be globally
consistent — a Z₂ flux of −1 through every triangle. **[MEASURED]**; its relation to De Marrais's "sails" and "vents" is **[HYP]** (my first
test required all three diagonals to annihilate each other pairwise and found 0 of 8 faces, which is this frustration seen from the other side).

**What is inside a zero divisor.** For `y = (2,3,+)`: the annihilator `N(y) = {x : xy = 0}` is 4-dimensional; every nonzero element of it is a
zero divisor; the four lattice neighbours are an *orthonormal basis* of `N(y)` (Gram matrix = identity); a great-circle arc between two of them
stays in `N(y)` (all points annihilate `y`) — so **an edge is a 3-sphere's worth of partners, four of which are lattice points**. `N(y)` is **not** closed
under multiplication and not norm-multiplicative (products leave it, ratio 1.006–1.378) — it is a subspace, not a subalgebra. The {4:8:4}
grading of `x ↦ xy` is exactly: 4 = this null block (the edges), 8 = an isometric sub-octonion on `{i : χ_u(i) = +1}` with `u` the polar point of the Fano line
`{a, b, s}`, 4 = the other-sign diagonals of the same four neighbour planes.

**The fibre lies in the NOW block (added 2026-10-13).** For all 14 Assessors tested (both diagonals, d = 0.3/0.6/1.0) the throw vector
supported on `{0, a, b, s=a⊕b}` has ratio `|ψy|/(|ψ||y|) = 1.0000`, i.e. it lies in the isometric 8-block of its Assessor. Reason: `χ_u(s) = χ_u(a)χ_u(b) = +1`,
so the quaternion line of `{a,b,s}` sits inside `ker χ_u` = the NOW octonion. This is why the earlier kernel "defect" is a different bracketing, not a defect.
(`scratchpad/2026-10-13_portals_inventory_moving_kite/fibre_now_block.py`.)

## 4. The named groupings — mathematical definitions, and what each is composed from

(The words are from Cody's list. Each is given its **mathematical** definition [LIT], then *where it arises in the sedenion/box-kite* and what it is
composed from, with what was measured. The project's own uses are in the repo; this page uses the mathematical ones.)

**Index.** An element of the group `ℤ/2⁴` (a 4-bit word). *Composed from:* the four doublings (R2). The sedenion basis is `{e_i}` indexed by it.

**Cocycle / coboundary.** A function on tuples of group elements whose "boundary" vanishes (cocycle) or which is itself a boundary (coboundary).
*Here:* `α` is a 2-cochain; `φ = ∂α` is its coboundary (the associator); `β = α/αᵀ` is its antisymmetrisation (the commutator).
*Composed from:* R4. **[MEASURED]** `φ = ∂α` with 0 violations.

**Character (Walsh function / Sylvester–Hadamard row).** A homomorphism `χ_u : ℤ/2⁴ → {±1}`, `χ_u(i) = (−1)^{popcount(u&i)}`.
*Here:* the 16 characters are exactly the diagonal sign operators that are algebra automorphisms (16 of 65,536); the 15 non-trivial ones ↔ the 15 hyperplanes ↔ the 15
sub-algebras of §2; `u ∈ 1…7` are the polar points of the {4:8:4} gradings. *Composed from:* R1 + R3 (duality). ptol.c's `J_red / J_blue` partition is `χ₄`.

**Spinor.** An element of a representation space of `Spin(n)` (the double cover of `SO(n)`) that is not a representation of `SO(n)`. The octonions
`ℝ⁸` are the real 8-dimensional spinor representation of `Spin(7)` (and a half-spinor of `Spin(8)`, which triality relates to the vector representation);
`G₂ ⊂ Spin(7)` is the stabiliser of a unit spinor, so `ℝ⁸ = 1 ⊕ 7` under `G₂`. The real 16-dimensional spin representation of `Spin(9)` is `𝕆 ⊕ 𝕆`.
*Here:* the left multiplications `L_a` by imaginary `a` satisfy `L_a² = −|a|²` on the lower octonion (error 3.6e-15), which is exactly what makes `ℝ⁸` a Clifford module `Cl₀,₇`
(the spinor); on the full sedenions `L_a² + |a|² ≠ 0` (error up to 16, failure for one random `a, x` = 30.2) — **the sedenions are not a Clifford/spinor module under their own
product**, and that failure *is* the non-alternativity that creates the zero divisors. *Composed from:* a Clifford module needs R6 trivial enough (alternativity). **[MEASURED]** the Clifford
test; **[LIT]** the representation theory.

**Fibre.** For a map `f : X → Y`, the fibre over `y` is `f⁻¹(y)`; a fibre bundle is a map that is locally a product. *Here, four fibres:* (i) the **annihilator**
`N(y)` is the fibre of `x ↦ xy` over `0` (4-dimensional) — a 3-sphere of partners; (ii) the **orbit map** `G₂ → G₂·y` has fibre `SU(2)` = the stabiliser of `y` (dimension 3),
which acts on `N(y)` (rank 3 on the four neighbours); (iii) the octonionic **Hopf fibration** `S⁷ → S¹⁵ → S⁸` of the Cayley–Dickson pair `(a,b)`, whose base coordinate `|a|² − |b|²` is the
`{8:8}` quantity (**[LIT]**, not re-verified); (iv) the kernel's hub→chart "fibre" is a path in the base of the first of these. *Composed from:* R7 for (i), the continuous layer (§6) for (ii).

**Braid.** The braid group `B_n` is the fundamental group of the space of `n` unordered points in the plane; `B₂ ≅ ℤ`. Algebraically a **braiding** on a monoidal category is a family of
isomorphisms `c_{X,Y} : X⊗Y → Y⊗X` obeying the two **hexagon** identities together with the associator. *Here:* on the category of `ℤ/2⁴`-graded spaces, the commutator sign `β` is a
braiding and the associator sign `φ` its associator. **[MEASURED]** both hexagon identities hold with **0 violations over all 4096 triples**, and `φ = ∂α` — so the sedenion multiplication table is an algebra
in a braided monoidal category whose braiding is the commutator sign and whose associator is the nonassociativity sign, both generated by the single cocycle `α` (the structure Albuquerque–Majid
found for the octonions **[LIT]**; here verified for the sedenions). `β` is **not** a bicharacter (2,520 violations) — the braiding is carried by the associator, not trivial. *Composed from:* R4 alone.

**Twistor.** A point of twistor space: `ℂ⁴` (or `ℂP³`), a pair of spinors `(ω^A, π_{A'})`, with the *Penrose correspondence* `lines of ℂP³ ↔ points of (complexified, compactified) Minkowski space = the Klein
quadric in ℂP⁵`; the symmetry group is `SL(4,ℂ)`, double cover of `SO(6,ℂ)`. *Here, the finite analogue over `F₂` exists exactly:* the 15 imaginary units are the 15 points of `PG(3,2) = P³(F₂)`;
its **35 lines** are in bijection with the **35 points of the Klein quadric `Q⁺(5,2)`** (`(q²+1)(q²+q+1) = 35`); the group `GL(4,2) ≅ A₈` (order 20,160) is the `F₂` twistor/conformal group; and **the 168 is
the stabiliser of an antiflag** (point `e₈`, plane `P`) — 20,160 / 120. **[MEASURED]** the counts and the stabiliser order; **[LIT]** the correspondence. This is a *finite geometric analogue*, not a
claim that the sedenion is a twistor space. *Composed from:* R3 only.

**Pencil (project term, with a standard meaning).** In projective geometry a **pencil** is the set of lines through a point (here 7 lines through a point of `PG(3,2)`); the paper's "seven ordered pairs" are one pencil
listed in a fixed order. *Composed from:* R3. *Relation to the kite:* §7.

## 5. Why zero divisors begin at the sedenions (the recursive building step)

The index set grows by the doubling `P_{n+1} = P_n ⊔ {pivot} ⊔ shadow(P_n)` (1 → 3 → 7 → 15 points). A cross pair `(a, b+h)` with `a ≠ b` is a candidate zero divisor; for it to have a **partner**
you need a second cross pair `(c, d+h)` with `a⊕b = c⊕d` — i.e. **two different lines through the same point `s` of the lower space**. **[MEASURED]**

| doubling | lower space | lines through a point | cross pairs | annihilating ordered diagonal pairs |
|---|---|---|---|---|
| quaternion → octonion (8-dim) | 3 points | **1** | 6 | **0** |
| octonion → sedenion (16-dim) | 7 points | **3** | 42 | **336** |
| sedenion → 32-dim | 15 points | 7 | 210 | 3,696 |

The Fano plane is the smallest projective space in which a point lies on two distinct lines *and* the sign cocycle can cancel — so the box-kite is the **first** place the recursion produces R7. Each further doubling repeats the
same step with a bigger lower space.

## 6. The continuous layer (the exact deformations)

- **G₂ and the components.** The 14 derivations preserve the lower and upper halves, are skew-symmetric, and have a **common fixed subspace of dimension 2 = `span(e₀, e₈)`**; their Casimir has eigenvalue `0` (×2) and `1` (×14), the commutant has dimension 8, and the intertwiners
  between the lower 7 and the upper 7 have dimension 1. So `ℝ¹⁶ = ℝe₀ ⊕ ℝe₈ ⊕ 7 ⊕ 7` under `G₂` — the two sevens carrying *one* representation, complexified by `e₈`. The fixed complex line `{e₀, e₈}` is the `{2:14}` pointer `z = x₀ + i x₈` and the "persistent indices in no zero-divisor plane" of the `d*_RG` construction. **[MEASURED]**
- **Portals.** From the diagonal `(2,3,+)`, a continuous `G₂` flow reaches **every one of the other 83 diagonals** (72/72 in other charts, 8/8 neighbours, 2/2 reversal, 1/1 same plane; residual ≤ 1e-12): all 84 diagonals lie on a single `G₂`-orbit. Along such a flow every zero-divisor relation holds to ~1e-13 and `L_x` keeps a zero smallest singular value (it *stays* a zero divisor), while the straight line between the same endpoints leaves the zero-divisor set (smallest singular value 0.215–0.366). In between the vertex sits up to 40.6° from the nearest lattice diagonal and its "dominant chart" is noise (shares 0.16–0.17). **[MEASURED]** So the seven "struts" (charts) are seven lattice positions on **one connected family**, not seven separate structures; the earlier finding that interpolating *index permutations* jumps (catalog §9) is a statement about permutation interpolation, not about the zero-divisor variety.
- **What survives the motion.** Under `g = exp(0.7 D)`: unchanged — norm, `e₀` weight, `e₈` weight, `e₀+e₈` ("outside") share, lower/upper split, `Σ axis` of `σ_RB`, the singular values of `L_v` and `R_v`, and the associator norm `K(v) = Σ_{ij}|[v,e_i,e_j]|²`; changed — the seven chart energies, `local_curvature` (by 12.0), the Walsh coefficients including `ptol`'s `Γ = W₄` (by 0.28), and the `σ_RB` tilt (by 0.89). **[MEASURED]** The first group are *invariants of the kite*; the second are *readings relative to a frame* (here the fixed frame `u = 4`, `⊕8` of the question space `σ_RB`).

## 7. The seven ordered pairs against this atlas (the scalar construct)

`pencil(s)` = the 7 lines of `PG(3,2)` through the point `s` = **3 axes** (the lines of `P` through `s` = the kite's antipodal pairs) + **1 pivot** `(8, s+8)` + **3 shadows** (the axes shifted by 8). None is an Assessor
(an Assessor is a cross pair *between* a point and the shadow of a *different* point). The Assessors of chart `s` are six of the seven stations of `pencil(s+8)`, plus the plane `{s, 8}`. Details, the tension law
`H = −cos(Σ ε_k φ_k)` and its bracketing/firing-order dependence: `ScalarContextPropagation` paper §9.7–§9.8 and `Boxkite-Deformation-Record-2026-10-12.md`.

## 8. What the moving (scaled) kite needs, and which implemented functions need a new home

The scaled Mind's-Eye kite cannot be the seven ordered pairs (a discrete, static object); it has to be carried by `G₂` the way de Marrais's kite moves. Triage of what exists (read from the files):

| function / file | depends on | survives the moving kite? | disposition |
|---|---|---|---|
| `box_kite.maths`: `multiply`, `associator`, `diagonals`, `is_assessor`, `assessors`, `box_kites`, `strut` | the table / the lattice frame | yes — algebra-native; the lattice is the *reference frame* | keep; becomes the frame the flow is measured against |
| `chart_projection`, `chart_of` chart energies, `nearest_assessor`, `dominant_chart`, `lit_struts` | lattice labels | no — labels meaningless between lattice points (shares flat, dominant chart flickers) | keep as **frame-relative** readings; stop treating them as identity |
| `local_curvature` (top-3 coordinate triples) | coordinates | no | replace by the basis-independent associator norm `K(v)`; keep the old as a frame reading |
| `fixed_point_weight`, `outside_share`, `energy_split` | `e₀`, `e₈`, halves | **yes** (all `G₂`-invariant) | keep; promote to the kite's invariants |
| new: singular spectrum of `L_v`, `R_v` | the product only | **yes** | add; distance-to-zero-divisor and the {4:8:4} grading, no labels |
| `PapersHands.emit_pathway` / `relate` (lineage order over chart indices) | chart labels | no | shelve for the static scalar kite; re-home as ring-walks on the moving kite |
| `throw_fiber` / `run_boxkite` (strut-indexed throws) | the 7 discrete struts | no | shelve the strut-indexed form; re-home as a *path in the orbit*; the as-written `psi[a], psi[b]` is a different bracket (an ℍ-line), not a defect |
| `GaugeEye.continuous_snapshot` (`a_matrix_basin_windspeed = local_curvature`) | coordinates | no | reading relative to a frame; pair with `K(v)` |
| `GaugeHands.emit_steered`, `prime_gauge_field` (`Γ(s)`, curvature) | the complex `s`-plane | independent of the kite | keep — a Scale-engine object, not a kite function |
| `emerger` brackets `{1:15},{2:14},{8:8},{4:4:4:4},{4:8:4}` | index sets | partly — `{2:14}` is `Fix(G₂)`; `{1:15}`,`{8:8}` are `G₂`-stable (`e₀`, halves); `{4:4:4:4}`,`{4:8:4}` are frame-relative | re-express `{4:8:4}` per zero divisor by its polar character `u` |
| `ptol.c`: `project`, `measure_sigma`, `measure_gamma`, `σ_RB` | the fixed question frame (`u = 4`, `⊕8`) | it *is* the fixed frame | keep unchanged — "fixed question space"; `Γ` is `W₄`, the other 14 Walsh coefficients are the unread channels |
| `monad3_gamma_radial`, `basin()`, WordNet 19D, `compress_count` | the scalar-context side | independent | stays with the scalar context box kite |
| pencil / string / flashlight / `Φ(w)` / Joukowsky / the tension law `H` | the 7 ordered pairs | no — discrete, static | **shelve from the scaled kite**; remains the scalar context box kite's machinery |
| my Context Flow spec's locator/ring-traversal and any use of `lit_struts` as "sub-subjects" | chart labels | no | re-base on the kite's invariants and the topic words, not on chart labels |

## 9. Open items

1. Make the "3 = 4" statement (four `d*` faces, three Lambert-W values) explicit — `Boxkite-Deformation-Record` §6 lists what is measured (the three `W` values are the three isomorphism classes of the doubling parameter; four `d*` faces give three tilts).
2. Which Lambert-W triple is canonical: `{W(0)=0, W(1)=Ω_ZS, W(−1/e)=−1}` (Third Age draft §2.2, reproduced to 40 digits in `output_lambert3.txt`; `W(−1/e)=−1` is a *double root* — Newton converges linearly, error ratio → ½, and `scipy` returns `nan` there) or three "rotor faces" of `W(1)`.
3. Relate the frustrated sign gauge on the faces to de Marrais's sails, vents, trefoils and zigzag.
4. Build the moving kite: a `G₂` element as the live state, readings = the invariants of §6 plus the frame-relative Walsh channels; compose it from the pool's tokens, not from projecting the string (the projected address carries no topic — 16 prompts, 4 subjects).
5. The pencil bracketing question on the Assessor-plane pencils (`s+8`): which bracketing/order makes them single-phase, and does it correspond to one of the emerger's five brackets.

## 10. Lambert W as a fixed-point object (added 2026-10-13, after Cody's note)

Scripts and output: `.claude/scratchpad/2026-10-13_lambert_dynamics_uns/` (`lambert_uns.py`, `output_lambert_uns.txt`).

- **Four tests, three values.** `W₀(0) = 0`, `W₀(1) = Ω_ZS = 0.56714329040978387299996866…`, `W₀(−1/e) = −1`, `W₋₁(−1/e) = −1`. The last two are the *same point* reached on the two sheets: three distinct values, four counted with
  multiplicity (the branch point is a double root). Numerically the pair splits by ~5e-21 when evaluated at a 40-digit `−1/e` — the square-root sensitivity of a double root. **[MEASURED]** The four `d*` faces have the same pattern:
  four faces, three distinct numbers, because the Boundary and the Flow are both `0.24631`. Each 4-set has exactly one doubled member.
- **In Universal Native Space** (decimal-log metric: divide a natural-log quantity by `ln 10`): `W(0) → 0`; **`W(1) → 0.246307201473… = d*_taut`** (the Flow); `W(−1/e) → −log₁₀(e) = −0.434294481903…` (twice, for the double root).
  In units of `d*_taut`: `0`, `ln 10`, `−1/d*_taut = −4.0599706…`. The sum of the four tests is `Ω − 2` → `d*_taut − 2/ln 10 = −0.62228…` in UNS (arithmetic; no meaning claimed). **[MEASURED]**
- **W is the (negated) multiplier of the exponential map's fixed point.** For `f_λ(x) = e^{−λx}`: fixed point `x* = W(λ)/λ`, multiplier `f′(x*) = −W(λ)` (checked numerically at 8 values of `λ`).
  `λ = 0`: multiplier 0 (superstable) — `W(0)`. `λ = 1`: multiplier `−Ω` (attracting; the idle point) — `W(1)`. `W(λ) = 1` at `λ = e`: multiplier `−1`, a **flip**; past it the orbit settles on a period-2 cycle (tested to `λ = 8`) and stays — `e^{−λx}` is decreasing, so its second iterate is increasing and the real map cannot be chaotic. For the growth map `e^{λx}` the fixed points are `x = −W(−λ)/λ`: two for `λ < 1/e`, one (double, `x = e`, multiplier `+1`) at `λ = 1/e`, none above: `W(−1/e) = −1` is the **fold (saddle-node)**. **[MEASURED]**
- **The double root is a projection artifact, exactly.** The curve `(w, x = w eʷ)` is smooth and single-valued; `dx/dw = eʷ(1+w) = 0` at `w = −1`. Projecting onto `x` folds it: 1 preimage for `x > 0`, 2 for `−1/e < x < 0`, 1 (double) at `x = −1/e`, 0 below. The two-valuedness of `W` is the shadow of a smooth curve with a vertical tangent — a Whitney fold. Locally it is `w ↦ w²`, the same normal form as the double cover branched at the ramified primes (`RAMIFICATION = DETACHMENT` in the canonical maths). **[MEASURED + LIT]**
- **The cardioid cusp is the same multiplier `+1`.** The main cardioid is the image of the unit circle `|μ| = 1` under `μ ↦ c(μ) = μ/2 − μ²/4` (μ = the multiplier of the fixed point of `z² + c`); `dc/dμ = ½ − μ/2` vanishes on the circle only at `μ = 1`, where `c = 1/4` and the fixed point `z = ½` has multiplier `2z = 1` — the saddle-node of `z² + c`. The cusp is where the circle's image stops being an immersion. **[MEASURED]**
- **Vocabulary, kept honest.** *Catastrophe* (Thom) = a singularity of a gradient map; the fold is the simplest elementary catastrophe, so `W(−1/e)` (a double root) is a catastrophe in the technical sense, and so is a caustic (Arnold). *Crisis* (Grebogi–Ott–Yorke) means a sudden change of a **chaotic attractor**; the real exponential family has none (above). Windows of order in a chaotic regime are born at folds — multiplier `+1`, the same condition as `W(−1/e)` and the cardioid cusp (the logistic map's period-3 window opens at a tangent bifurcation) **[LIT]**. Which of `d*` and `W` is the "catastrophe" end and which the "crisis" end is not decided by this vocabulary; it is Cody's to assign.

