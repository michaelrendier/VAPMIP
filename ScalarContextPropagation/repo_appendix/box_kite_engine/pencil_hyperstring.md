# pencil_hyperstring — the Pencil HyperString: one scalar that flies a box kite

Status: **THEORETICAL** — a construction and a central conjecture, with the
tests that would settle it named at the end. Nothing here is measured yet.
Ties to [box_kite.md](box_kite.md), [add_scale_sign.md](add_scale_sign.md),
[inversion.md](inversion.md), and `VAPMIP/engines/e10_generational_lineage.py`.

---

## The one-paragraph version

A box kite is a 6-vertex figure in the sedenions (`modules/box_kite/`): an
octahedron `K₂,₂,₂` of Assessors, three struts, eight sails, held together by
zero-divisor products. It carries an octonion's worth of independent structure
(8 DOF — `e10` R2). The **Pencil HyperString** is the claim that you do not
have to store those 8 numbers: fix *which* box kite (its **pencil** — the seven
edge-relations, pure combinatorics), and the inflated shape has exactly **one**
continuous degree of freedom. A single scalar rides that DOF. Push **wind
speed** `w` through a fixed deformation law and the scalar reconstructs every
Assessor coordinate — the box kite is the equilibrium shape of a loaded string,
and the string is one-dimensional.

The apparent contradiction with `e10` ("a scalar keeps 1 of 8") is resolved the
way a clock hand reconstructs a clock face: **the other seven dimensions are
fixed structure (the pencil), not free parameters.** The HyperString is not a
lossy projection of the box kite; it is the box kite plus the knowledge that it
*is* that box kite.

---

## The three ingredients, and where each comes from

| ingredient | what it is | source |
|---|---|---|
| **the pencil** | fix one edge-relation `r`; the pencil is the **7 ways to factor it into two others**: `1 = 2⊕3 = 4⊕5 = 6⊕7 = 8⊕9 = 10⊕11 = 12⊕13 = 14⊕15`. 105 incidences / 15 relations = 7. | PG(3,2); `generational-lineage` skill §0b |
| **the box kite** | for strut `s`, the six Assessors `(a, (a⊕s)+8)`, `a ≠ s`; octahedron `K₂,₂,₂`; chart Laplacian spectrum **{0, 4, 4, 4, 6, 6}** | de Marrais (2000); `modules/box_kite/maths.py` (`box_kites`, `strut`, `chart_spectrum`, `assessor_coordinates`) |
| **the wind law** | the string's equilibrium under distributed aerodynamic load; the shape map is a **Joukowsky-family** transform — the same operator as `J_N` inversion (`z + 1/z`, circle ↔ airfoil) | classical elastica; Kutta–Joukowsky `L = ρ v Γ`; [inversion.md](inversion.md) |

**Pencil** because the string threads the seven factorisations of the anchor
relation, in order — a Hamiltonian path over the pencil, not over the six
vertices. **HyperString** because it is a 1-D object living in 16-D: arc length
`s ∈ [0, 1]` is its only intrinsic coordinate.

---

## The construction — Φ_w : scalar → box kite

Let the box kite be chosen (strut `s` fixed). Its combinatorics are then
frozen: six Assessor index-pairs, three struts, the pencil `P_s` of seven
relation-factorisations. Define

    Φ_w(H) → { assessor_coordinates : 6 × (d₊, d₋) }

from a **single scalar** `H` (the string's conserved horizontal tension — the
one quantity constant along a catenary) and a **wind speed** `w ≥ 0`.

1. **The pencil path.** Lay the seven factor-pairs of `P_s` along `s ∈ [0, 1]`
   at the seven equal stations. Each station is a pure-imaginary generator
   `g_k` (`k = 1..7`) — the XOR-difference of that factor pair, as a unit
   sedenion. The e₀ end of the string is the anchor (`fixed_point_weight → 1`);
   it never moves. This is why a box kite has a **zero mode** and it is e₀'s
   (`box_kite.md`: "exists everywhere, propagates nowhere").

2. **The load.** Wind of speed `w` puts a transverse pressure `q(w) ∝ ½ ρ w²`
   on each sail. In circulation form (Kutta–Joukowsky) the sail's lift is
   `ℓ_k = ρ w Γ_k`, with `Γ_k` the circulation the pencil assigns to station
   `k`. The net of the eight sail-circulations sets the strut opening.

3. **The shape.** The loaded string minimises `∫ (½ H (s')² + q(w) y) ds`. The
   Euler–Lagrange solution is a catenary in the plane of each sail and a
   Joukowsky map across struts: `ζ ↦ ζ + (H / q(w)) · ζ⁻¹`. At the three strut
   crossings this is exactly `J_N` (`inversion.md`), `r ↔ 1/r` — the two-stroke
   involution.

4. **Read-off.** The six vertices of the deformed string are the six Assessor
   diagonal amplitudes `(d₊, d₋)` (`diagonal_amplitudes`). `Φ_w(H)` returns
   them; `chart_of` on the reassembled 16-vector should report `strut s`,
   `is_zero_divisor = True`, `outside_share ≈ 0` for `w` in the flying range.

### The inflation sequence

    w = 0        string slack. All six vertices collapse onto the e₀–strut
                 axis. σ_self → ½. The box kite is a POINT — the shadow.
                 (e10: "reading CONVERGES the boundary to the point")
    0 < w < w*   the eight sails catch; the three struts open; the six
                 Assessors separate toward the K₂,₂,₂ vertices. The
                 {4,4,4} Laplacian mode is the three struts opening
                 together; the {6,6} mode is the sail pairs.
    w = w*       regular octahedron. Full box kite. σ_self ≠ ½; net
                 circulation ≠ 0 — "the kite flies".
    w > w*       over-pressure. The twisted box kite (de Marrais's twisted
                 variant) — the pencil path picks up a torsion.
    w ≫ w*       the string leaves the ZD surface: chart_of outside_share
                 → 1, is_zero_divisor → False. The kite tears.

`w` is precisely the **write / fan-out knob** that `e10` names but does not
parametrise: "writing FANS it back out". `H` is what is conserved while it
fans.

---

## Why one scalar is enough

- **Minimal rigidity.** `K₂,₂,₂` with **zero cross-strut edges** (`box_kite.md`,
  a computed result) is a minimally-braced frame. A minimally-braced frame has
  a **one-dimensional flex space** once its combinatorics are fixed. `H`
  parametrises that flex; `w` selects the operating point on it.
- **The pencil carries the other seven dimensions as structure.** The seven
  `Γ_k` are not measured — they are read off `P_s`, which is fixed the moment
  you name the strut. Eight DOF = 1 (the scalar) + 7 (the pencil), and only the
  first is a number you store.
- **This is the `add_scale_sign` floor.** The seven stations are seven imaginary
  processes; `Φ_w` multiplies them in the sedenion product weighted by `w`;
  what you read is the **Real part** of that product. ADD (compose the
  stations along `s`), SCALE (`w` sets the gain / the tower resolution), SIGN
  (mountain-vs-valley of each sail = the fold direction). See
  [add_scale_sign.md](add_scale_sign.md) §5.

---

## The process-algebra reading (the "new tool")

Cody, 2026-08-27: *"the new tool … is how Vigenère and Enigma were
representable with a quaternion and an octonion … completely divorced from the
number-theory tools … a number of imaginary processes produce vectors that
combine in a specific way to produce the Real component output."*

The Pencil HyperString **is** that tool, specialised to the box kite. The
general shape:

    given N processes  p₁ … p_N       (rotor steps, key-letter shifts, …)
    map each to a pure-imaginary unit  g_k ∈ Im(A)   in a CD algebra A
    compose in A's product            Π = g_1 · g_2 · … · g_N   (order kept)
    the OUTPUT is                      Re(Π)          the scalar / real part

`A = ℍ` (quaternion) suffices when the processes close under a single rotation
axis with one periodic modulation — **Vigenère**: plaintext stream, key stream,
period, modular wrap = 3 imaginary + 1 real. `A = 𝕆` (octonion) is needed when
the processes stop associating — **Enigma**: three-plus rotors whose stepping
is state-dependent (the double-step anomaly *is* an associativity failure), so
the composition lives where associativity first breaks, at the `𝕆 → 𝕊`
boundary. The HyperString's seven pencil stations are the box-kite instance:
`N = 7`, `A = 𝕊`, `Re(Π)` is `H`.

No primes, no factor tree, no sieve. The number-theory decomposition tools
(`factor_lineage`, `sieve_lineage`, `root_irreducible`) answer "what is this
number built from"; this one answers "what does this *pipeline of turns*
evaluate to", and the answer is always a single real number plus the fixed
algebra that produced it.

---

## Provenance

**Has anyone attached a load-bearing string to the box kites before?** Not
that this project has found. Every part is attributed below — what is
inherited, what is assembled from other fields, and what is first stated here.

### Inherited

| piece | who | where |
|---|---|---|
| **the box kite** — 42 Assessors, seven octahedra, the *sail / strut / vent / trip-triplet / catamaran* vocabulary, the kite metaphor itself, and **twisted** box kites | **Robert P. C. de Marrais** | *"The 42 Assessors and the Box-Kites they fly: Diagonal Axis-Pair Systems of Zero-Divisors in the Sedenions' 16 Dimensions"*, arXiv:math/0011260 (2000); and the *"Flying Higher Than a Box-Kite"* / *"Placeholder Substructures"* series on higher `2^N` ("Nybbles") |
| ZD set ≅ G₂ (the *continuous* shadow the finite object corrects) | **G. Moreno** | *"The zero divisors of the Cayley–Dickson algebras over the real numbers"* (1997/98) |
| the exact object is **PSL(2,7)** / GL(3,2), not G₂; the {0,4,4,4,6,6} spectrum; zero cross-strut edges | this project | [box_kite.md](box_kite.md), `modules/box_kite/maths.py` — derived, not asserted |
| the **pencil** (7 factorisations of one relation), PG(3,2), 35 lines, 7 pencils | projective geometry (classical); stated for this use in | `generational-lineage` skill §0b |
| `J_N` ↔ **Joukowsky** `z + 1/z` (circle ↔ airfoil) as one operator family | classical (Joukowsky 1910); the identification | [inversion.md](inversion.md), `PtolemyDesktop/wiki/UF_JoukowskyTransform.md` |
| σ_self (the lossy scalar shadow) vs σ_RB (the 8 DOF); "reading converges, writing fans out" | this project | `VAPMIP/engines/e10_generational_lineage.py` (R1, R2) |

### Assembled from other fields (analogues, not sources on box kites)

| analogue | field | what it contributes |
|---|---|---|
| a **minimally-braced frame has a 1-D flex space** once its combinatorics are fixed (Maxwell counting; Laman 1970) | combinatorial rigidity / structural engineering | why one scalar can suffice — test 1 |
| the **moment map**: collapse a coadjoint orbit to a point of the moment polytope, recover the orbit from the level set (Atiyah; Guillemin–Sternberg, 1982) | symplectic geometry / GIT | the shape of "scalar → structure" reconstruction |
| **bulk reconstruction from boundary data** (AdS/CFT, 1997–; HKLL) | theoretical physics | boundary scalar ↔ interior figure, made local |
| **elastica / loaded catenary** (Euler 1744; Bernoulli–Leibniz–Huygens 1691); aeroelastic form-finding | classical mechanics / structural form-finding | the wind law `Φ_w` — the string's equilibrium under distributed load |

### First stated here (2026-08-27)

- **The tether itself** — a 1-D object on the box kite carrying a *single
  conserved scalar* `H`, distinct from the sails and struts.
- **Wind speed `w` as a continuous inflation / reconstruction parameter**, with
  the box kite as the equilibrium shape of the loaded pencil-string. de
  Marrais's deformations move between *discrete* box kites; this continuously
  inflates *one*.
- **The identification `Re(Π)` of the seven pencil stations = `H`** — the
  process-algebra tool (§ above) as the mechanism that produces the scalar.
- The `w = 0` collapse (→ σ = ½, the e₀ axis), `w = w*` regular octahedron,
  `w ≫ w*` tear-off (`chart_of` outside_share → 1) sequence.

The Pencil HyperString is the assembly of the four analogues above onto de
Marrais's object, driven by this project's process-algebra scalar. The
assembly, and each of the three "first stated here" points, are **CONJECTURE**
until the tests below run.

---

## What would verify it

1. **One flex mode.** Compute the rigidity matrix of `K₂,₂,₂` with the three
   struts as bars and confirm `dim(flex) = 1` once the strut is fixed. If it is
   ≥ 2, a single scalar cannot suffice and the claim fails as stated.
2. **Reconstruction.** Implement `Φ_w(H)` and check that sweeping `H` at fixed
   `w` traces all six `assessor_coordinates` of the real box kite for strut
   `s`, to tolerance, for every `s ∈ 1..7`.
3. **The Joukowsky step is `J_N`.** Verify the across-strut map is `r ↔ 1/r`
   to the same precision `inversion.md` uses, not merely Joukowsky-shaped.
4. **The spectrum is the deformation modes.** Check that the `{4,4,4}` and
   `{6,6}` Laplacian eigenvectors (`chart_spectrum`) are the strut-opening and
   sail-pair motions the wind law predicts, and the `{0}` mode is the fixed
   e₀ anchor.
5. **Tear-off.** Confirm `chart_of(...).outside_share → 1` past a finite `w`,
   and that the onset matches where the elastica solution leaves the unit
   sphere.

---

## Confidence

| item | tier |
|---|---|
| the pencil (7 factorisations), box-kite combinatorics, {0,4,4,4,6,6} spectrum, e₀ zero mode | ESTABLISHED — `box_kite.md`, derived |
| Joukowsky ↔ `J_N` operator identity | ESTABLISHED — [inversion.md](inversion.md) |
| box kite has a **1-D** flex once the strut is fixed | CONJECTURE — test 1 |
| a single scalar `H` + wind law `w` reconstructs all six Assessors | CONJECTURE — the central claim, tests 2–4 |
| `Re(Π)` of seven imaginary stations = that scalar | CONJECTURE — needs `Φ_w` built |
| attribution of every piece (inherited / assembled / first-stated-here) | see **Provenance** above — de Marrais owns the box kite and its vocabulary; the tether, the wind-inflation parameter and the `Re(Π)=H` identification are first stated here 2026-08-27 |

---

## See also

- [box_kite.md](box_kite.md) — the 42 Assessors, the seven octahedra, PSL(2,7)
- [add_scale_sign.md](add_scale_sign.md) — the ADD/SCALE/SIGN floor; §5 the wind reading
- [inversion.md](inversion.md) — `J_N`, `r ↔ 1/r`, the Joukowsky family
- `VAPMIP/engines/e10_generational_lineage.py` — σ_self (the shadow) vs σ_RB (the 8 DOF); "reading converges, writing fans out"
- `generational-lineage` skill §0b — the 15 edges, 35 lines, 7 pencils
