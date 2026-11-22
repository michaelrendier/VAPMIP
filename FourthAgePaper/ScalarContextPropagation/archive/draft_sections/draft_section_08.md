## 8. Cost, measured — and why there was no cost function to measure against

### 8.1 The claim, scoped honestly

This is not "backpropagation is wrong." Backprop remains, right now, the
best tool available for a large class of problems — OCR, CNNs generally,
anything where a labeled dataset and a differentiable architecture
already exist and the compute to train it is available. The claim here
is narrower and practical: **backprop is a hard wall for training a
neural network on a laptop**, and that wall is what keeps AI design out
of the hands of people doing hobby work at home — not a wall of
correctness, a wall of compute. Millions of cost-function evaluations,
a stored computational graph, a backward pass through it — that is
real, unavoidable work, and it does not fit in an evening on consumer
hardware. The engineering goal of this whole project was to make that
wall optional, not to declare it wrong.

### 8.2 What a scalar cost function can't see

A trained network's cost function reduces the entire state of the
system, at every step, to one number — how far from the target. That
scalar has no field structure: it cannot express *which direction* is
degenerate versus which direction actually carries information, only
*how far* the current guess is from a fixed target. Gradient descent
then has to rediscover the local shape of the loss surface step by
step, from that one number and its immediate slope, which is exactly
why ill-conditioning and saddle points are real, well-documented
failure modes of first-order methods (Newton's method, natural gradient,
and Hessian-aware saddle-escape methods are the established fixes —
all of them use curvature/eigenstructure the plain gradient never
looks at). None of that is new here; it's the standard critique,
cited as such.

### 8.3 The actual design: intent and desire, forward only

The mechanism this paper documents does not evaluate a cost function at
any step. A word's address is computed once, directly (§3–§5); its
19-dimensional WordNet relational signature is read once, directly
(§7); nothing is compared against a target and adjusted backward. Two
things carry forward instead — **intent** (what the code/maths
*function* actually does at this step) and **desire** (the code/maths
*jurisdiction* it's allowed to act within) — the same two terms this
project's own Lagrangian framing already uses elsewhere, given here
their plain engineering translation. Forward propagation, in this
sense, is not a metaphor layered on top of the box-kite mechanism —
**the scalar box-kite context propagation described in §3–§7 of this
paper already is one**, end to end, and is cited here as exactly that:
a working instance, not an argument that one could work.

### 8.4 A real precedent with no cost function at all

The design origin for this predates any of this project's own maths:
the classic Infocom/Zork-style text-adventure **sentence parser** — a
static readout against hardcoded lexicographical data (verb tables,
noun tables, fixed grammar rules), zero training, zero cost function,
zero gradient of any kind. It answers a question directly by table
lookup, every time, deterministically. What this project adds to that
model is not a cost function — it's replacing Zork's *flat* hardcoded
tables with a *relationally rich* one (the 19D WordNet vector, the
box-kite structure it can be read against), while keeping the same
zero-training, zero-backward-pass shape the parser always had.

### 8.5 The anchor, kept minimal on purpose

The only zero-divisor structure this section needs is the anchor: a
fixed point on the Real numberline (`e₀`, already established as the
box kite's anchor in §3.2) that the box-kite's own zero-divisor
structure turns around, hyperdimensionally, while the anchor itself
stays fixed. Nothing about *why* that structure is stable, or what its
eigenvalue decomposition looks like at a zero divisor, is needed
here — that's real, and it's VAPMIP/Ainulindalë territory (the Mind's
Eye's own "Zero Divisor Reframe," where a thought-pathway only gets
promoted to long-term memory once it's checked both mathematically
correct *and* contextually sane — a real, separate design principle,
not developed in this paper). What's worth saying plainly: any 2D/3D
rendering of that structure on a screen is a flattened shadow of
something hyperdimensional and never actually static — the same
caution this project already keeps on record as Flattening Syndrome.

### 8.6 Cost, measured

The comparison that *is* this paper's to make — what the already-shipped
mechanism (§3–§7) actually costs, measured, on real hardware:

```
read path:        ~600 flop/token (one sedenion-scale product + one
                   sparse A-matrix row)
ingest fold:       1.8 × 10⁵ words/s, ≈38 µJ/word @ 7W (reference
                   machine, single core)
native floor:      ≈115 ns, <1 µJ/word
```
Live, runnable: `engine/energy_bench.py` — no notebook wraps this one,
it's a standalone benchmark script, run directly against the hardware
it reports on.

against the standard forward-FLOP identity for a dense transformer
(`2·N_params` multiply-accumulates/token, ~1 J/token at 70B params,
10⁻¹¹ J/flop datacentre-effective) — **10⁴–10⁶× cheaper per query**, and
the gap is structural, not an optimisation: the addressed structure
regenerates its answer from a fixed ruler; the materialised field is
re-swept in full every time because the answer lives in the weights.

The numbers above are the ThinkPad X1 Carbon's (i7-8550U,
`VAPMIP/docs/SYSTEM_SPECS_ThinkPad_X1_Carbon_6th.md`, snapshot
2026-07-31), correctly attributed in `engine/energy_bench.py`'s own
header — see §2.4 for the two-machine note this figure draws on.

**Back Propagation = Bad = Hard = Inefficient = Work = Hard Boundary.
Forward Propagation = Good = Easy = Free = Less Work** — the author's
own framing, kept as a direct quote. The "15 year old laptop" line
alongside it is a deliberate rhetorical placeholder, not a literal
hardware-age claim (neither the X1 Carbon nor the EliteBook is
actually 15 years old) — the point it's making is real regardless:
whatever the exact machine or its exact age, it's a dinosaur next to a
current top-of-line laptop, and it still runs this fine. The measured
numbers above are what actually back the claim; the "15" is the
easy-to-grasp version of it, not a spec.
