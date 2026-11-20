## 9. The Pencil — the Gamma-Radial Windspeed, and what it takes to run the box kite today

Scoped deliberately narrow, per the paper's own rule: only what's necessary
to run the box-kite mechanism as the current monad actually uses it. The
fuller exploration this pencil work opened up — recorded in full in
`VAPMIP/Boxkite-Catalog.txt` — is real, substantial, and explicitly **not**
developed here; it closes the paper as "in development," §11.

### 9.1 The Gamma-Radial Windspeed, finalized

Two real candidate windspeeds were tested side by side this pass (weighted-
operator probe, all 7 struts) before this section could be written
honestly, and it's worth naming both now, precisely, so neither is ever
confused for the other again: the **Gamma-Radial Windspeed** and the
**A-Matrix Basin Windspeed**.

**`gamma_radial`, recovered from a word's own stored address, is the
windspeed for this paper — the Gamma-Radial Windspeed** — exact,
deterministic, needs nothing but the word's text and its `(full_addr,
delta)`:

```python
full_code = full_addr - delta                          # exact, §7
spelling  = spelling_code(word)                         # from the text alone
context_code_recovered = full_code // spelling          # exact integer division —
                                                          #   disjoint prime tiers, §7.4
windspeed = gamma_radial(context_code_recovered)         # the real-valued fold, §7.3
```
Live, runnable:
`repo_appendix/windspeed_reconstruction/01_windspeed_recovery.py` (§13.4).

Verified live against a real word: `windspeed("tree") = −0.151155`.

The other real candidate — the **A-Matrix Basin Windspeed** (A-matrix
basin drift) — is **not** this paper's windspeed. It needs a live,
mutating, corpus-dependent store, which is exactly wrong for a claim
about forward propagation from an address alone. It has a real, separate
home: the windspeed for sentence *construction* — a different, later
engineering pass (the Mind's Eye, VAPMIP's short-term-memory subsystem —
introduced properly in §11), out of scope here. Two names, two genuinely
different jobs; kept apart on purpose.

### 9.2 The pencil, attached

`pencil(s)` — 7 factorisations of one relation, `ValaQuenta/modules/
box_kite/maths.py`, built and verified this project. For strut 1:

```python
>>> bk.pencil(1)
[(2,3), (4,5), (6,7), (8,9), (10,11), (12,13), (14,15)]
```
Live, runnable: `ValaQuenta/modules/box_kite/maths.py::pencil` — no
notebook wraps this call directly; ValaQuenta is this project's root
authoritative engine repo, called here exactly as shown.

Each station is a pair of PG(3,2) points XORing to the anchor. This is the
minimal slice needed here — just enough that a windspeed has something to
act on. The fuller pathway/portal structure over the pencil is Catalog
material, §11.

### 9.3 What the deformation actually does — corrected twice, now honest

Two real mistakes, corrected in the record rather than quietly fixed,
because both changed the answer:

**Wrong coordinate frame.** An initial check of `pencil_hyperstring.md`'s
"one flex mode" claim used ordinary Cartesian 3D rigidity theory (Maxwell
counting: `dim(flex) = 3·6 − 6 − 3 = 9`, exact, matching an earlier,
independent notebook finding). That arithmetic is correct and irrelevant —
this project's own standing rule is that sedenion/box-kite maths is native
to **radial complex spherical polar coordinates**, never Cartesian
internally. Confirmed once corrected: pairing an Assessor's `(d₊,d₋)` as
one native complex number (the same move already verified elsewhere in this
project's σ_RB work) is the right representation, not two independent
Cartesian reals.

**Wrong aperture.** A second check used bare Cayley–Dickson basis vectors
(`e₂`, `e₄`, ...) as pencil-station generators — exactly as
`pencil_hyperstring.md` literally specifies ("a unit sedenion"). Checked
directly: every one of the 256 possible basis-vector products is *exactly*
`±1` times another basis vector (zero exceptions) — a closed, quantized
lattice. `H = Re(Π)` landing on `{−1,0,1}` under this representation,
found originally in notebook 04, was therefore never evidence that the box
kite's own structure is discrete. It's what multiplying quantized lattice
points together always does. Opening the aperture — the same generator
varying continuously along its own great circle instead of a discrete pick
— gives smooth, exact variation: `Re(Π) = −cos(φ)`, verified.

Both corrections came from the same discipline, now written up as its own
skill (`observer-position`) precisely so this doesn't get re-discovered the
hard way a third time: track *which coordinate frame* (orientation) and
*how much of the structure, at what resolution* (aperture) a result was
taken from before trusting it.

### 9.4 `H`, conserved — a Noether current, a real and partial result

Every quantity this paper calls "conserved" — this one included — is a
**Noether current** in the precise sense Emmy Noether's 1918 theorem
establishes: a continuous symmetry of the motion is what holds the
quantity fixed along it, not a coincidence found by scanning candidates
until one happened to stay flat. Stated explicitly here, once, because
it is true of every conservation claim in this paper and should not be
read as a looser, informal use of the word.

Once the aperture is opened, `H` is not merely continuous — it is **exactly
conserved**, a genuine Noether current, along one specific, non-arbitrary
path: each pencil station's phase advancing at a rate proportional to its
own position in the pencil (`φ_k ∝ (k+1)/7`), moving through all seven
stations *in pencil order*. Checked against three other joint-motion rules
(uniform rate, reversed order, random per-station rates) — none of them
conserve `H`; only the pencil's own order does, i.e. only that specific
rate law is the symmetry `H`'s conservation is attached to. Not a trivial
fact about any coordinated motion — a specific one.

Checked across all 7 struts, and here the honest result is a real, partial
one, not a closed law: **`H` conserves exactly, as a Noether current, on
struts 1, 3, and 6, and drifts on struts 2, 4, 5, and 7** — confirmed
against two different generator conventions (which endpoint of each
station pair is taken "first"), so it's a fact about the strut, not an
artifact of that choice. *Why* those three specifically is open — checked
and ruled out that they form a closed Fano-plane line — the Fano plane
is the smallest possible projective geometry, 7 points and 7 lines,
3 points per line, the same small structure the 7 struts themselves are
already indexed by — checked directly (`1⊕3=2`, not `6`) and ruled out
as the explanation. Kept honest as an unresolved structural question for
the Catalog, §11, not forced to a premature answer here.

### 9.5 The crossing, precisely — `J_2`, not `J_N`

One more correction worth keeping, because it's now exact rather than
descriptive. The Joukowsky map used at a strut crossing, `ζ ↦ ζ + c·ζ⁻¹`
(`c = H/q(w)`), is **not itself an involution** — `f(f(ζ)) ≠ ζ`, checked
directly. It is the 2-to-1 projection of a genuine order-2 symmetry
underneath it, `ζ ↔ c/ζ` (not simply `ζ ↔ 1/ζ` unless `c=1` — verified the
general form exactly: `f(ζ)=f(c/ζ)`, and `c/(c/ζ)=ζ`, both exact). That
symmetry is `J_2`, the same order-2 fold already established elsewhere in
this project (the Red/Blue swap, the `(I|O)` two-stroke engine) — **not**
`J_N`, the separate order-4 map this project also has on record. The
crossing itself is the fixed point of that `J_2` fold, `ζ = √c` — which is
exactly why a fixed windspeed can pin a crossing at all: an order-2
involution has one clean fixed point; a bare continuous deformation with no
such symmetry would not.

### 9.6 What runs today, in the current monad

Honest status, not aspirational, updated since the recovery was first
written up: the windspeed recovery (§9.1) **is now ported into `ptol.c`**
(`monad3_gamma_radial()`, 2026-09-21), checked against this paper's own
recorded value before anything was built on it —
`windspeed("tree") = -0.151155` in both Python and C, to 6 decimal
places. `monad3_lookup()` mmaps `monad3_c.bin` and reads a word's real
19-dimensional relation vector straight out of the packed store by raw
pointer arithmetic (`-M`, byte-exact against `boxkite_bin.h`, §6); `-M`
and `-say` now also print that word's real, live Gamma-Radial Windspeed
alongside it — `ptol -M tree` and `ptol -say "the engine runs"` are both
real, scriptable, offline-testable entry points today, not a plan.

What is still exactly where it was: the **windspeed-driven deformation**
this section derives — `Φ_w`, the pencil/strut-angle geometry actually
moving in response to the windspeed — remains Python-verified
`THEORETICAL:CALCULATED` in neither language; §9.3–§9.4 measure a
spectral proxy for it, not the mechanics, and that hasn't changed. And
one further honest boundary, drawn on purpose rather than blurred: the
new C computation is wired into `-M`/`-say`, both offline/scriptable, but
**not yet into `-w`'s live interactive console** — `console_speak()` now
computes the report, but `mh_send_chat`'s wire protocol to the curses UI
is untouched this pass, since that is the one recently-verified live
interactive path and extending it needs its own tested pass, not a
same-sitting add-on. Stated plainly rather than implied otherwise: the
*recovery* is real, checked, and in C now; the *deformation* is not; the
*live console display* of the recovery is computed but not yet visible
to someone actually sitting at `-w`.

### What this section is not

Not the full sail-pressure-to-strut-angle mechanics the author's own
model describes (unbuilt — the spectral checks above are a proxy, not
that geometry). Not the fuller pathway/portal exploration, the Blackjack
(21-member) subgroup connecting all 7 hyper-boxkite structures, or the
`{1,3,6}` question's resolution — all Catalog material, named and
pointed at, §11, not developed here.
