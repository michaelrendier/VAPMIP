# 04 — Carry-Over as Decay (M-DECAY)

**Purpose:** carry topic from one unit to the next at several granularities, with
properties that can be **proved by arithmetic** and therefore tested exactly.

---

## 1. The integrator

For each level `L ∈ {L0, …, L4}` the context state holds a vector `C[L] ∈ ℝ¹⁹`
and a scalar mass `m[L]`.

Define the per-step retention

```
λ_L = exp(−1 / τ_L)          τ_L > 0        [PARAM: time constant, in units of that level's steps]
```

On each new unit `x` at level `L` with word vector `v(x) ∈ ℝ¹⁹`:

```
C[L] ← λ_L · C[L] + v(x)
m[L] ← λ_L · m[L] + 1
```

The **normalised context** is `ĉ[L] = C[L] / m[L]` (undefined while `m[L] = 0`).

This is a linear, time-invariant, first-order filter (a leaky integrator). The
normalisation by mass makes `ĉ` an exponentially weighted *average* of the inputs,
independent of how many have arrived.

## 2. Closed forms (these are the guarantees)

Let an impulse `v` arrive at step 0 into an empty state and nothing after.

```
C(n) = λⁿ · v            (exact)
m(n) = λⁿ
ĉ(n) = v                 (the average of one input never changes)
```

For inputs `v₀, v₁, …, v_n` at steps 0..n:

```
C(n) = Σₖ λ^(n−k) · v_k
```

Half-life in steps: `n½ = τ · ln 2`.

**G-DEC-1 (exact decay).** `C(n) = λⁿ v` to floating-point rounding. Test
`DEC-01`, tolerance 1e-12 relative for n ≤ 10⁴.
**G-DEC-2 (superposition).** The state for `a·v + b·w` equals `a·C(v) + b·C(w)`.
Test `DEC-02`.
**G-DEC-3 (half-life).** The weight of an impulse after `⌈τ·ln 2⌉` steps is within
the rounding of `½`. Test `DEC-03`.
**G-DEC-4 (level ordering).** For `τ_L < τ_(L+1)` and the same input stream, the
higher-level state decays more slowly. Test `DEC-04`.
**G-DEC-5 (determinism).** Same stream ⇒ bit-identical state (CN-31). Test `DEC-09`.

## 3. Multi-granularity ladder

The author's plan includes several granularity models, which the spec treats as
the same filter at different `τ`:

| Level | Updated by | Default τ [PARAM] | Meaning |
|---|---|---|---|
| L0 | every word | 3 words | immediate lexical neighbourhood |
| L1 | every sentence | 4 sentences | local discourse |
| L2 | every paragraph | 4 paragraphs | topic segment |
| L3 | every response | whole response | document topic |
| L4 | every turn | many turns | session topic |

Defaults are not results. The only structural requirement is the strict ordering
`τ(L0) < τ(L1) < τ(L2) < τ(L3) < τ(L4)` (CN-41). A geometric ladder
`τ_(L+1) = ρ·τ_L` is one choice [PARAM ρ]; it echoes the project's scale
structure but is a choice, not a derivation.

**Feeding rule.** The word vector `v` enters L0 directly. What enters L(L+1) is the
*normalised* state of level L at the moment a unit of level L+1 closes:
`v_(L+1) = ĉ[L]`. This makes each level an average of averages and prevents a
long sentence from outweighing a short one.

## 4. Boundary events

From `01_context_needs.md` §6.3: `boundary(L, β)` multiplies `C[l]` and `m[l]` by
`β` for every `l ≤ L`.

| Event | L | β [PARAM] | Effect |
|---|---|---|---|
| sentence end | L1 | 1.0 (no change to L1; close the unit into L2 feed) | — |
| topic-shift boundary (from `05_*`) | L2 | small (0 = hard reset) | paragraph state forgets the old topic; L3, L4 keep it |
| new response | L3 | 0 | document state cleared; L4 keeps session |
| explicit reset | L4 | 0 | everything cleared |

Because `boundary` multiplies numerator and denominator by the same `β`, `ĉ` is
unchanged immediately after a boundary and the *next* input then dominates
proportionally to `β`. **G-DEC-6 (boundary algebra).** After `boundary(L, β)` with
`β → 0`, the next input fully determines `ĉ[l]` for `l ≤ L`; with `β = 1` the state
is unchanged. Test `DEC-05`.

## 5. Using the state

The decayed state is a *query* for the vocabulary mechanism and the locator:

- **Topic similarity** of a candidate word `w`: `sim(ĉ[L], vec(w))` using the
  similarity function chosen by experiment (`SM-04`; options: cosine on `vec19`,
  cosine on `ln(1+vec19)`, Γ_rad difference, Jaccard on non-zero slots).
- **Locator input:** the ring values of the *unit* may be computed from the
  decayed state instead of the raw unit, giving a context-aware point (variant
  `ctx-locator`, compared in `SM-04`).
- **Boundary detector input:** disagreement between short-`τ` and long-`τ` states
  is a candidate topic-shift signal (`TT-06`).

## 6. Numerical safety

- `λ_L ∈ (0, 1)` for finite `τ_L`; the filter cannot grow.
- **Underflow:** after about `745·τ` steps of silence `λⁿ` underflows to 0 in
  float64. Behaviour at zero must be defined: `m = 0 ⇒ ĉ` undefined ⇒ the state
  reports `EMPTY` (a refusal value), not a division by zero. Test `DEC-08`.
- **Long runs:** 10⁶ updates with bounded input must not produce NaN or ∞
  (`DEC-08`).
- **Scale of inputs:** `vec19` entries are small non-negative integers
  (log-compressed counts [CODE]); no overflow risk. If a future vector is
  unbounded, compress it first (the lesson from `compress_count` and `modules/scale`).

## 7. Tests

| ID | Checks | Metric |
|---|---|---|
| `DEC-01` | Impulse response equals `λⁿ v` | MET-ERR |
| `DEC-02` | Superposition | MET-ERR |
| `DEC-03` | Half-life | MET-ERR |
| `DEC-04` | Level ordering of decay rates | exact |
| `DEC-05` | Boundary algebra for β ∈ {0, ½, 1} | MET-ERR |
| `DEC-06` | Normalisation: `ĉ` independent of input count for constant input | MET-ERR |
| `DEC-07` | Feeding rule: higher level receives `ĉ` of lower level | exact |
| `DEC-08` | Underflow / long run / empty state behaviour | exact |
| `DEC-09` | Bit-identical determinism across runs | exact |
| `DEC-10` | Probe-topic recall: a topic planted at sentence k is detectable at k+n as a function of τ (empirical curve vs analytic curve) | MET-ERR |
| `DEC-11` | Latency of a single update at each level | MET-LAT |

## 8. What this does **not** claim

- It does not claim that exponential forgetting is the *right* memory shape for
  language; only that it is exact, cheap and testable. Alternatives (power-law
  decay, a mixture of exponentials) are listed as `DEC-ALT` follow-ups and enter
  through the same test harness.
- It does not claim the default `τ` values are good. They are placeholders for a
  sweep on the calibration set (`MET-SWEEP`).

## 9. C-port notes

State per level is 19 floats plus one mass: 20 × 5 levels × 8 bytes = 800 bytes.
Update is 19 multiply-adds. `λ_L` is precomputed per level. No allocation.
