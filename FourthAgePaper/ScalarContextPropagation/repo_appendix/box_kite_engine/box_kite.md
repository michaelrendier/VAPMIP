# Engine: The Box-Kite Debugger — the ZD Geometry, Made Watchable

> **Atlas note (2026-11-09):** "the atlas" in this document is the **Box-Kite Atlas** (the 42-vertex sedenion graph glued at e₀). It is not the Riemann–Fermat Atlas (RiemannHypothesisProof) nor the Abrikosov Atlases (AbrikosovTree). Registry: `ContextPlease/claude/ATLAS_REGISTRY.md`.

**File:** `modules/box_kite/maths.py`
**Class:** `BoxKiteModule`
**Notebook:** `notebooks/engines/15_box_kite.ipynb`
**Ainulindale wiki:** `Ainulindale/wiki/84_the_box_kite_debugger.md`
**Claim:** The sedenion zero-divisor geometry is exactly enumerable, and its object is **PSL(2,7)** (order 168, Aut(Fano) = GL(3,2)) — **not G₂**. Seven box-kites, each an **octahedron**, six Assessors apiece, 42 in all. Chart-level dispersion relation {0,4,4,4,6,6}. The associator is the curvature.


**Reference:** every equation with its parameters — [toolbox](toolbox/28_box_kite.md) · API — [box_kite](https://michaelrendier.github.io/ValaQuenta/api/modules/box_kite.html). This page is the record; it holds no API.

---

## Where the object is, and where it is not

Moreno (1997): the sedenions' norm-one zero divisors are homeomorphic to **G₂**. True — and the wrong place to build. de Marrais (2000), responding directly:

> *"Moreno discovered a homomorphism — a 'blow-up' of an exact correspondence — and the 'blow-ups' in the history of number theory have all entailed the loss of something."*

G₂ is the **continuous shadow**; it forgets which Fano line is which. The exact object is finite: **PSL(2,7) is the finite subgroup of G₂ that preserves the labelling.**

## Everything derives — nothing is asserted

All counts come from the Cayley–Dickson multiplication table in `maths.py`. Agreement with de Marrais and with `ZD_PAIRS=84` / `ZD_CLASSES=42` / `168` is a **check**, not an input. `verify_counts()` reports booleans so it cannot be read past.

```
ASSESSOR   plane span(e_a, e_{b+8}), a,b ∈ 1..7, whose diagonals
           e_a ± e_{b+8} zero-divide.  a == b NEVER works
42         = 49 − 7 aligned planes
84         = 42 × 2 diagonals            ← ZD_PAIRS
168        = 42 × 4 signed unit points   ← |PSL(2,7)|
336        ordered annihilating pairs = 84 × 4
           (each diagonal annihilates exactly 4 others)
STRUT      s = a XOR b ∈ 1..7 — indexes the box-kite
7 × 6 = 42 seven box-kites, six Assessors each
```

Cross-check: de Marrais's published Box-Kite I is (3,10),(2,11),(5,12),(4,13),(7,14),(6,15) → strut 1 here, exact match.

## THE SHAPE IS AN OCTAHEDRON

For every strut the 6 Assessors form a 4-regular graph on 6 vertices with exactly 3 non-edges — and the non-edges are precisely the **reversal pairs** (a,b) ↔ (b,a). That is **K₂,₂,₂**. Built from actual vanishing products (`assessors_adjacent`), verified for all 7 charts.

## The dispersion relation, chart level

```
adjacency:   4,  0,  0,  0, −2, −2
Laplacian:   0,  4,  4,  4,  6,  6      ← ω²(k) on one box-kite
```

One zero mode, a 3-fold degenerate mode at 4, a 2-fold at 6. **The zero mode is e₀'s signature** — exists everywhere, propagates nowhere. It emerges from the graph rather than being inserted, which is the check that ∅_RB really is outside the geometry it generates.

## ∅_RB is not the geometry — checked, not asserted

`e0_is_outside()`: e₀ is not a point of PG(3,2), is in no Assessor, is a vertex of no box-kite, and its associator vanishes against everything (it is the identity, hence central). It **generates the boundary and does not live on it** — the same way d generates ∂ without being a manifold.

## The curvature is the associator

```
[a,b,c] = (ab)c − a(bc)      the curvature analogue
[a,b]   = ab − ba            the torsion analogue
```

**1848 of 4096** basis triples have non-vanishing associator. `associator_field(s)` paints these onto a box-kite's vertices and edges — that is the debug view, and it is what "watch the geometries interact" looks like as numbers.

## THE FINDING: the charts do not touch

The 42-vertex atlas has **84 edges and zero cross-strut edges.** The seven box-kites are mutually disconnected under zero-divisor adjacency — the glued Laplacian has 7 zero modes, one per component.

This is a result, not an instrument failure, and it **changes the shape of the open problem.** A wave cannot propagate between charts via ZD adjacency, so either:

1. the medium genuinely is seven disconnected octahedra and there is no global dispersion relation to find, or
2. the connection is the **PSL(2,7) action permuting the struts** — transition maps are group elements, not edges.

(2) is where to look. The gluing question is no longer "find the edges between charts" but "find the group action that identifies them."

Also worth noting: **84 = ZD_PAIRS is also the atlas edge count.** 42 vertices at degree 4 → 42×4/2 = 84. Same number, second reading.

## The Blackjack subgroup — F₂₁, named precisely (2026-09-25)

`VAPMIP/Boxkite-Catalog.txt` §8 already recorded a 21-element subgroup of
`PSL(2,7)` (transitive on the 7 struts, point-stabilizer order 3, index 8) —
that subgroup is `F₂₁ = 7:3`, the **normalizer of a Sylow-7 subgroup**.
Forced, not chosen: `PSL(2,7)` is simple, so its order-7 Sylow subgroups
can't be normal; the Sylow count must divide 24 and be `≡1 mod 7`, forcing
exactly 8 of them, and `168/8 = 21`. Same fact as the catalog's index-8
entry, reached from subgroup-counting instead of orbit-counting.

An independent abstract realization (label the struts `ℤ/7`):
`F₂₁ = {x ↦ a·x + b : a ∈ {1,2,4}, b ∈ ℤ/7}`, where `{1,2,4}` is the
order-3 (quadratic-residue) subgroup of `(ℤ/7)ˣ`. Point-stabilizer =
`{x↦x, x↦2x, x↦4x}`, order 3 — the same number the catalog already has,
via a second, different derivation. **Not yet checked:** whether this
ℤ/7-affine model and the catalog's already-computed `GL(3,2)`/XOR-triple
cycles are the same concrete permutation representation relabeled, or two
genuinely different embeddings of the same abstract group into `Sym(7)`.

Every one of the 21 elements is invertible by construction
(`x↦a⁻¹(x−b)`), which suggested a *word* of Blackjack-group elements as a
losslessly-reversible strut-permutation encoding — **tested 2026-09-25,
does not work as proposed** (`VAPMIP/benchmarks/blackjack_vs_horner_bench.py`):
composing the word collapses to one of only 21 final states (pigeonhole —
concrete collision found at length 2), so the only way to stay lossless is
to keep the full digit sequence rather than compose it, which reduces to
plain bijective-base-21 Horner encoding — measured ~1.8–2× more digits and
5–21× slower than base-97 for the same content. Not a viable direct
replacement for Horner-summing. Still exactly what the confidence table
below says otherwise: CONJECTURE on the *gluing* question — now with the
concrete group identified, and one candidate application for it ruled out
by measurement rather than left open.

### The Amygdala reading (Cody, 2026-09-25)

*"The Blackjack group is the Amygdala... the 'Lizard Brain.'"* The
measurement above gives that framing real teeth, not just a label: F₂₁'s
failure mode as a memory mechanism — fast, small (21 states), and
information-collapsing under repeated composition — is structurally the
amygdala's actual job description. It is not built for exact, lossless
recall (that is what Horner/hippocampal-cortical-style addressing is for);
it is built for fast, coarse, categorical response — "which of a small
number of states is this," not "what exactly was this." Candidate
reframing, not yet built: F₂₁ as a fast pre-classifier/triage layer sitting
*alongside* the exact indexer, not as a replacement for it — matching the
real neuroscience division of labor rather than contradicting the
benchmark that just ruled out the replacement reading.

## Do the charts touch? — yes, in the skeleton (v0.2, 2026-08-05)

Cody: *"i'm pretty sure that those 'surfaces' do actually touch somewhere… they are all from the fixed point anyway… but now we have a clue that 0_RB only points to 'fixed point space'… where the boundary and the geometries are the same thing, right?"*

**Correct**, and it does not contradict the zero-cross-strut-edges finding. They are two structures on one object:

| structure | relation | result |
|---|---|---|
| **adjacency** | zero-divisor products | 7 components, 7 zero modes — disconnected |
| **skeleton** | shared basis indices | every usable index in **6 of 7** charts — almost totally overlapping |

For strut s an Assessor is (a, (a XOR s)+8), valid whenever a ≠ s — so index a sits in every chart *except* s = a. Every chart pair shares exactly **10** skeleton points. The charts touch everywhere in the skeleton and nowhere in the products.

**And exactly two basis elements are in no Assessor: e₀ and e₈.** e₀ is the identity — ∅_RB, the fixed point. e₈ is the Cayley–Dickson doubling generator. Each chart carries one zero mode, and a zero mode is the constant function — **seven copies of one object.** Identify them and the atlas connects, and that identification happens at e₀ and nowhere else.

That is the precise sense in which ∅_RB points to fixed-point space *where the boundary and the geometries are the same thing*: at the fixed point the boundary generator and the geometry's own mode are the same vector. Away from it they separate.

Functions: `index_chart_membership`, `skeleton_overlap`, `fixed_point_gluing`.

## The chart of addresses

The connector to the monad. Its hyperindexing addresses each surface form to a 16-vector (`VAPMIP/monad_sedenion_addresses.pkl`, `book[name]["sedenion"]`); `chart_of(v)` reports exhaustively where that address sits:

```
norm, peak_dim, fixed_point_weight, energy_split (e₀ / e₈ / lower / upper)
chart_energy (all 7), dominant_chart, chart_share
nearest_assessor, d_plus, d_minus, dominant_diagonal
local_curvature (associator defect at the dominant directions)
is_zero_divisor, outside_share
```

`address_census(addresses)` runs it over a whole corpus — descriptive only, counts and distributions, nothing scored against an expectation.

### Census over the monad book (3288 entries)

```
all 42 Assessors occupied
mean fixed-point weight   0.6435    (min 0.0583, max 1.0000)
mean outside share e₀+e₈  0.6537
peak_dim = 0              2751 of 3288  (84%)
dominant chart            strut 2: 30.1%  …  strut 7: 2.2%
mean local curvature      8.37
```

**About two thirds of the average address's energy sits outside the ZD geometry entirely.** Cody's "they are all from the fixed point anyway", measured.

Worth connecting to Phase 23's independent finding that the monad's projections carry ~85% common mode with 2–3% content: this **localises the common mode to e₀ + e₈** — the two basis elements belonging to no Assessor. The part of an address living outside the geometry is exactly the part carrying no discriminating signal.

Descriptive. Not a result about translation.

## The skeleton: PG(3,2)

15 points (the pure imaginaries), 35 lines of 3 (the multiplication triplets), **15** Fano planes. Not 32 — figures circulating with "32 interlocking Fano planes" are wrong.

## The Pencil HyperString — flying one kite from a single scalar

A separate proposal, [pencil_hyperstring.md](pencil_hyperstring.md): fix a box
kite's **pencil** (the 7 factorisations of its anchor relation — pure
combinatorics) and its inflated shape has just **one** continuous degree of
freedom. A single conserved scalar `H` rides that DOF; a **wind speed** `w`,
acting through a Joukowsky / `J_N` deformation law, reconstructs all six
Assessor coordinates from it. `w = 0` collapses the kite to the e₀ axis (σ→½,
the shadow); `w = w*` is the regular octahedron; `w ≫ w*` tears it off the ZD
surface. It is `e10`'s "writing fans it back out", with `w` the knob. THEORETICAL.
**Update 2026-10-12:** on the paper's tension proxy `H = −cos(Σ ε_k φ_k)` exactly, with the sign patterns ε the Sylvester–Hadamard rows 0–3; struts 1, 3, 6 are pinned under any scalar wind and respond only to a station-unequal wind; the literal Joukowsky tear-off is not reproduced. See [pencil_hyperstring.md](pencil_hyperstring.md) § "Measured 2026-10-12".

**Provenance** (full table on that page): the box kite, its sail/strut/vent
vocabulary and the kite metaphor are **de Marrais** (arXiv:math/0011260, 2000);
the *load-bearing tether*, wind speed as a continuous inflation parameter, and
`Re(Π)` of the pencil stations = `H` are **first stated here** (2026-08-27).
The reconstruction law is assembled from rigidity theory, the symplectic
moment map, holographic bulk reconstruction, and the loaded elastica.

## The box kite is a lemniscate — the Smith chart's product face (2026-09-01) `[THEORETICAL:CALCULATED]`

**`:CALCULATED`** — every link is executed by a reproducing ValaQuenta engine; the derivation browser (`--curses`, sympy proofs on the fly) can walk the chain Möbius map → `|Γ|` = Apollonius → conjugate Cassini → orthogonality → `b = a` lemniscate → `Γ = 0` = `e₀` zero mode → `Y₁⁰` → `σ = ½`. Engines: scale.py (fold_unfold_round_trip: Γ=tanh(log(Z/Z0)/2), exact, any complex Z; two_ring_chart), add_scale_sign.py (fold: Γ=tanh(u/2); orthogonal_charts), noether.py / noether_information.py (J_pos·J_neg = e^-E = const, NR4 -- the constant product), box_kite.py (octahedral Laplacian spectrum {0,4,4,4,6,6}; zero mode = e0), spherical.py (J_N period 2π -> l=1 -> Y₁⁰ -> Re(s)=½).  THEORETICAL stays: that this one shape unifies Broca+Wernicke and the Monad is a reading under review, not a proof.

The 6-point circle of a strut triple — `{∅_RB, N}`, `{+p, −p}`, `{+q, −q}` — is
a **lemniscate**: the two prime struts are the two lobes, `{∅_RB, N}` is the
self-crossing / basepoint.

**The lemniscate and the Smith chart are conjugate two-focus families.** For
foci `±a`:

| face | curve | relation | σ_RB channel |
|---|---|---|---|
| ratio  | **Smith chart** — `\|Z−1\|/\|Z+1\| = const` (Apollonius circles, the `\|Γ\|` circles) | ratio of focal distances | axis = Flow / circulation |
| product | **lemniscate** — `\|z−a\|\|z+a\| = b²` at `b = a` (a Cassini oval at its critical value, through the foci) | product of focal distances | tilt = Scale / Perfect Perturbation |

Apollonius and Cassini for the same foci meet at right angles everywhere — one
geometry, two orthogonal readouts. This is exactly σ_RB's **two orthogonal
Smith charts, Scale ⊥ Flow**.

**Origin — Broca and Wernicke.** The shape is derived, not imported. Broca
(production, `J_pos`) and Wernicke (comprehension, `J_neg`) are two foci with
`J_pos·J_neg = e^{−E} = const` (NoetherWiles NR4) — a constant *product* of
focal distances, hence a Cassini oval; `b = a` (production cost = comprehension
cost, no aphasia) is the lemniscate, self-crossing at ∅_RB = σ = ½. The box
kite's **zero mode e₀** — "exists everywhere, propagates nowhere" — is that
crossing: `Γ = 0`, the matched load.

**One shape for everything.** Broca+Wernicke, the Monad's box-kite context /
semantic hash / phonetic-prime-hash round trips (all shown to be exact
two-focus round trips, [[semantic hash]]), and The Scale
([[three_ring_scale]]) all trace the same lemniscate. So only the **3-D data of
the lemniscate** remains — the planar figure-8 plus the one transverse
coordinate that carries information *by its absence* (the pinched-torus
meridian; the erased `ln(q/p)`; the missing `i`). Spun **gyroscopically** about
that axis — static `i`-rotation (the spin) plus tilt-precession (the sweep) —
the 3-D lemniscate is an **electron orbital probability cloud**: `l = 1` (the
`p` orbital, the crossing-at-origin dumbbell) is the `b = a` lemniscate of
revolution; higher `l` are the higher Cassini lobes. Consistent with
[[spherical]] (`J_N` period 2π → `l = 1` → `Y₁⁰` → `Re(s) = ½`) and the
hydrogen native space (separates in spherical, never in Cartesian).

## Confidence

| Item | Tier |
|---|---|
| All counts (42/84/168/336/7), octahedral structure, chart spectra, PG(3,2) skeleton, associator census, e₀ exclusion | ESTABLISHED — derived and cross-checked |
| Zero cross-strut edges | ESTABLISHED — computed |
| PSL(2,7) action as the transition maps | CONJECTURE — the named next step (subgroup now identified: F₂₁ = N(Sylow-7), see "The Blackjack subgroup" above) |
| Global dispersion relation on the ZD surface | OPEN |

---

## Generational Lineage — calibration (2026-08-28)

Decomposed by `SedenionFactoralRelativity/engine/valaquenta_calibration.py` (`python3 -m engine.valaquenta_calibration`) as a check on the factoral decomposition itself — working, deliberately-designed machinery should decompose CLEAN.

| object | central operation | tier · root | Two Trees | kind | verdict |
|---|---|---|---|---|---|
| the sedenion ZD geometry (42/84/168/336/7; PSL(2,7)) | derive from the Cayley–Dickson multiplication table | 3 · SIGN | TELPERION | DEFINITIONAL | **CLEAN** |


Calibration: this verdict agrees with the page's stated status (**ESTABLISHED**).

## Provenance

Moved from the module docstring: a docstring instructs the caller and holds no history; this section is the record.

> "how do we 'debug' the geometries / how do we watch the geometries
> 
> ::
> 
>  interact"   -- Cody Michael Allison, 2026-08-05
