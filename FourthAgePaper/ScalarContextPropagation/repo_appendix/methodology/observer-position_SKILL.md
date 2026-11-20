---
name: observer-position
description: >
  Methodology for tracking your own vantage point inside hypergeometric /
  algebraic maths that has no camera and no screen — sedenion space, Native
  Space, box-kite structure, any n-dimensional object you can only reason
  about symbolically. Combines nes-viewport's bounded-window discipline with
  scad-spatial's two camera-angle parameters (angle of viewing = breadth/FOV,
  angle of orientation = which direction you're pointed), applied abstractly
  rather than rendered. Load before any computation on a hyperdimensional
  object — before picking a coordinate system, before choosing which/how-many
  of the object's components to hold in view at once, whenever a result looks
  "flat," discrete-when-it-shouldn't-be, rigid, or otherwise suspicious;
  whenever switching between a native/intrinsic coordinate system and a
  Cartesian/extrinsic one; whenever comparing "the whole structure" against
  "one slice of it" and getting different answers.
---

# Observer Position — the vantage point has no camera

`nes-viewport` tracks a 2D window on a bigger map. `scad-spatial` tracks a 3D
camera — pose, frustum, angle of view — on a bigger scene, and can render
what it sees. This skill is the same discipline one level more abstract: the
"space" is an algebraic or hyperdimensional structure with no screen to draw
on, and the two things a camera would give you — **how wide you're looking**
and **which way you're pointed** — still have to be tracked explicitly, or
the maths quietly hands you an artifact of the vantage point instead of a
fact about the object.

Built 2026-09-20, directly from two real mistakes made in the same session,
both caught only after the fact. Kept here as the worked examples because
they're real, not illustrative.

## 1. The two observer parameters

| | `nes-viewport` | `scad-spatial` | this skill |
|---|---|---|---|
| bounded frame | viewport `vw×vh` on content `cw×ch` | frustum on scene bbox | **angle of viewing** — how much of the structure is in frame: one point, one slice, the whole atlas; sampled continuously or at discrete positions |
| pointing | (n/a — 2D, no angle) | pose: eye/target/up | **angle of orientation** — which coordinate system, which fixed point/anchor, which basis the observation is taken relative to |
| proof the whole content passes through | sweep test (§4, that skill) | canonical poses + one orbit | sweep the same computation across multiple orientations/apertures and check the finding survives |

Both parameters are independent, and a wrong answer can come from either one
alone — check them separately, don't conflate "this looks wrong" with "pick
a different everything."

## 2. Angle of orientation — which frame is this maths actually native to

The mistake, real, this session: running Maxwell-counting rigidity analysis
(bar-and-joint, ordinary 3D Cartesian, rigid-body motions subtracted the
Euclidean way) on a box-kite reconstruction question. The arithmetic was
correct — `dim(flex) = 9`, exactly, verifiable — and completely beside the
point, because the object doesn't live in Cartesian 3-space. This project's
own standing rule says so outright: *"Native Space... radial complex
spherical polar coordinate space in which all SMIP mathematics natively
reside. Flat Cartesian coordinates are a projection out of Native Space and
are never used internally."* Running the analysis in the wrong frame didn't
give a blurry answer — it gave a **confidently wrong** one, because Cartesian
rigidity theory is a real, self-consistent theory; it's just a theory of the
wrong object.

**Check before computing:** what frame is this object's own maths native to?
Sedenion / Native Space work is radial-complex-spherical-polar
(`r,θ,φ,ψ,σ`), not Cartesian, unless a result is being handed to a human as
final output. Complex-paired quantities (an Assessor's `(d₊,d₋)`, `σ_RB`'s
XOR-4 partners) are natively **one complex number**, not two independent
reals — the pairing itself is orientation information, and flattening it to
a bare 2-tuple throws that away before the maths even starts.

## 3. Angle of viewing — how much is in frame, and at what resolution

The second mistake, same session, different parameter: representing
"generators" as bare basis vectors (`e_2`, `e_4`, ...) — single quantized
lattice points — then multiplying them and reporting the result's apparent
discreteness as a finding about the object. It wasn't: any product of two
Cayley–Dickson basis vectors is *exactly* `±1` times another basis vector,
always, checked directly (256/256, zero exceptions) — an artifact of the
aperture being pinned to 16 discrete points, not a property of the
underlying continuous structure. Opening the aperture — letting the same
generator vary continuously along its own great circle instead of picking
one of two lattice endpoints — immediately produced smooth, non-quantized
variation (`Re(Π) = −cos(φ)`, exactly, verified). The object was never
discrete. The camera was stopped down to a pinhole and the pinhole's own
sampling grid got reported as the subject.

**Check before computing:** is the current representation sampling the
object at a fixed set of points (basis vectors, canonical poses, integer
indices) when the question is about *continuous* structure? A narrow /
discrete aperture is not wrong — it's often exactly right, cheap, and
sufficient — but its own resolution limit must not be mistaken for a
property of what it's looking at. If a result comes back suspiciously
clean/quantized/rigid, open the aperture (continuous parametrization, a
generic rather than lattice-aligned point) before trusting the cleanliness.

## 4. Worked object: the box kite as seven poses of one hyperobject

Directly analogous to `scad-spatial`'s canonical-pose table (front/top/iso…)
— the seven struts are seven *poses*, not seven separate objects:

| pose | orientation | aperture | what it shows | what it can't show |
|---|---|---|---|---|
| one-strut close-up | anchored at that strut's own fixed point | narrow (one octahedron, 6 vertices) | full local detail — the `{4:8:4}` block structure, exact | nothing about the other 6 struts; looks disconnected (it's a real fact: zero cross-strut edges under adjacency) |
| atlas / wide | anchored at `e₀`/`e₈` (the only points in no Assessor — where all seven charts actually glue) | wide (all 7 struts at once) | that it's one object — "seven copies of one object," identified at the fixed point | per-strut local detail; at this aperture every strut looks the same (that's not a bug, it's what "the same object, different pose" means) |
| portal / transition | oriented along a specific `PSL(2,7)` group element (the Blackjack subgroup) | narrow (two ZD points + the connecting element) | that the connection is a discrete jump, not a path — confirmed twice independently (linear interpolation leaves the locus immediately; a proper single-gear rotation is on-locus only at `t=0,1`) | anything about what's "between" the two points, because there is no between |
| continuous-native | oriented along one generator's own great circle, aperture opened past the lattice | continuous | genuine smooth variation, exact conservation laws along specific paths (verified: `H` flat to full precision along the pencil-ordered rate, drifting under every other tested rate) | — this is usually the pose that resolves whether an earlier "discrete" finding was real or an aperture artifact |

None of these four poses is *the* correct one. They're different, equally
real, equally partial views of one hyperdimensional object — the same way
`scad-spatial` insists no single canonical pose is "the" view of a 4D
polytope. The failure mode isn't picking one; it's forgetting which one is
currently active and comparing findings taken from different poses as if
they were the same measurement.

## 5. The protocol

Before running a computation on a hyperdimensional / Native-Space object,
state both parameters out loud, the way a camera pose gets stated before a
render:

1. **Orientation** — which frame (native radial-complex-polar vs Cartesian;
   which fixed point/anchor; complex-paired or flattened-real).
2. **Aperture** — how much is in frame (one point / one slice / the whole
   structure) and at what resolution (continuous / a specific discrete
   lattice / random sample).
3. If a result looks suspiciously clean, rigid, or discrete: **change one
   parameter at a time** and recheck — orientation first (is this Native
   Space or an accidental Cartesian projection?), then aperture (is this
   continuous or accidentally pinned to a lattice?). Changing both at once
   loses the diagnosis.
4. **Sweep before trusting a single pose** — the equivalent of `nes-viewport`
   §4's move-to-top/move-to-bottom test and `scad-spatial`'s canonical-poses-
   plus-orbit: take the same finding from more than one orientation/aperture
   and confirm it survives. A finding that only holds at one specific pose is
   a fact about the pose, not (yet) a fact about the object.

## See also

- `nes-viewport` — the 2D bounded-window model this generalises.
- `scad-spatial` — the 3D camera model this generalises; §3's rotate/slice/
  project/encode table is the same "n dimensions, one vantage point" problem
  at the perceptual-rendering end rather than the algebraic end.
