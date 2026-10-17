# 03 — The Smith-Chart Topic Locator (M-SMITH)

**The author's idea, specified.** On the Smith-chart side of The Scale engine, two
relationships about a text can be compared Smith-chart style. The resulting point
shows *where in "topic land" the prompt lives* — where the information is located.
The system then proceeds **around that specific ring** to scale context up. It
does **not** try to use every appropriate known word; it passes on a full,
adequate response that takes advantage of vocabulary-ingested knowledge.

---

## 1. Building blocks that already exist [CODE]

| Need | Existing identifier | Where |
|---|---|---|
| Fold Z → Γ | `mobius_fold(Z, Z0) = (Z−Z0)/(Z+Z0)` | `ValaQuenta/modules/scale/maths.py` |
| Unfold | `unfold_is_arctanh_exp`, `Z = Z₀·(1+Γ)/(1−Γ)` | same |
| Any two relationships → point | `custom_ring_chart(obj, ring1_fn, ring2_fn, Z0, …)` | same |
| Many objects → points + integer cells | `custom_ring_chart_series(...)` → `readings`, `cells` keyed by `(round(r1), round(r2))` | same |
| Local scale factor | `scale_factor(Z, Z0) = |2Z₀/(Z+Z₀)²|` | same |
| Anchor-independent invariant | `cross_ratio(z1,z2,z3,z4)` | same |
| Locally square cells | `verify_locally_square` | same |
| Master identity | Γ = tanh(½·ln(Z/Z₀)) | `fold_is_log_tanh` |
| Continuous / discrete charts | `charts(s)` | `GenerationalLineage/engine/toolsets/scale.py` |

The cells returned by `custom_ring_chart_series` — `(round(r₁), round(r₂))` buckets
— are the candidate **regions of topic land** ("windows of order").

## 2. Lessons already on the record (must be re-checked here) [CODE]

From `ValaQuenta/wiki/scale.md` §8, tested 2026-08-25:

1. **Degenerate pairs exist.** `J_red` against `J_blue` satisfies
   `J_red + J_blue = 1` to ten decimal places: one degree of freedom, not two.
   *Any* candidate pair here must pass an independence test before it is called
   a pair (`SM-02`).
2. **Unbounded axes saturate.** Raw count `n` against `compress_count(n)` drove
   `|Γ|` from 0.79 (n=1) to 0.98 (n=1000): the unbounded axis dominated.
   Candidate axes must be bounded or compressed (`SM-03`).
3. **Well-conditioned pairs are bounded naturally.** Inertia ∈ [0,1] against
   entropy ∈ [0,4] gave Γ spread 0.10–0.79 with no saturation.
4. The fold is **holomorphic**: cells are locally square for *any* pair, so
   squareness says nothing about whether the pair means anything.

## 3. Definition of the locator

Given a text unit `u` (a prompt, a sentence, a paragraph):

```
r₁ = ring1_fn(u)          # relationship 1 (see §4)
r₂ = ring2_fn(u)          # relationship 2
Z  = r₁ + i·r₂
Γ  = (Z − Z₀)/(Z + Z₀)    # Z₀ = anchor (see §5)
position(u) = (Γ, |Γ|, arg Γ, cell = (round r₁, round r₂))
```

**Interpretation [HYP]:** `|Γ|` is the distance of the unit from the anchor
(how far from the "typical" point of topic land); `arg Γ` is *which way* it lies;
`cell` is the discrete region. Units about the same subject should share or
neighbour cells; units about different subjects should separate.

## 4. Candidate ring pairs [HYP — each to be tested, none assumed]

Notation: `W(u)` is the set of in-store content tokens of `u`; `lexname(w)` is the
WordNet lexicographer category of the chosen sense (≈45 categories, e.g.
`noun.artifact`, `verb.motion`); `d(w)` is `min_depth` of the sense in the
hypernym hierarchy.

| Pair | ring₁ | ring₂ | Why proposed | Known risk |
|---|---|---|---|---|
| **RP-A** | specificity: mean `d(w)` over `W(u)` | breadth: Shannon entropy of the `lexname` distribution over `W(u)` | Chunk up/down (depth) against spread of subject matter | Both may rise with text length → correlated |
| **RP-B** | mean Γ_rad(w) over `W(u)` | dispersion: standard deviation of Γ_rad(w) | Uses the existing relational scalar; mean/spread is the natural 2-parameter summary | Spread undefined for |W|=1 |
| **RP-C** | relation richness: mean `Σ vec[i]` | relation evenness: entropy of the normalised `vec` summed over `W(u)` | Directly uses the 19D vector; richness vs balance | Evenness may be dominated by hypernyms slot |
| **RP-D** | log-compressed token-frequency rank (mean) | `lexname` entropy | Rarity of vocabulary against breadth | Needs a frequency table; `eng` store has `fire` counts [CODE: `monad3c.h`] — unverified as frequency |
| **RP-E** | noun share of `W(u)` | verb share of `W(u)` | Object-talk vs process-talk | Likely one degree of freedom (shares sum ≤ 1) → expected degenerate; included as a **negative control** |

`RP-E` is deliberately included because it is expected to fail `SM-02`; it proves
the independence test can actually fail.

## 5. The anchor Z₀

Z₀ is **not** free. Options [PARAM `anchor_policy`]:

| Policy | Z₀ | Property |
|---|---|---|
| `AP-1` | (1 + 1i) after normalising each ring to its calibration-set median = 1 | simple; Γ = 0 at the median unit |
| `AP-2` | the calibration-set mean point | Γ = 0 at the average prompt |
| `AP-3` | the point of a designated neutral prompt | explicit, reproducible |

**Anchor-sensitivity guarantee:** because the cross-ratio of any four points is
invariant under every Möbius map [LIT; verified in code, `verify_cross_ratio_is_scale_blind`],
topic-land *relationships among four units* must not depend on the anchor. Test
`SM-06` checks this on real ring data; if it fails the implementation, not the
mathematics, is wrong.

## 6. Normalisation (must be fixed before comparing pairs)

Ring values must be non-negative real numbers so Z lies in the right half-plane
and Z + Z₀ ≠ 0 [the fold's pole is at Z = −Z₀]. Each ring is mapped through
`x ↦ x / median_calibration(x)` or a log-compress; the choice is [PARAM
`ring_norm`] and recorded in every result log.

## 7. The ring and the traversal

### 7.1 What "ring" means here

Two definitions are possible and the spec carries both as variants, since only
experiment can say which is useful:

| Variant | Ring = | Moving "around" it means |
|---|---|---|
| **RING-Γ** | the circle `|Γ| = |Γ(prompt)|` (constant distance from anchor) | varying `arg Γ` at fixed distance |
| **RING-R1** | the level set `r₁ = r₁(prompt)` (the constant-ring₁ circle of the Smith chart) | varying `r₂` at fixed `r₁` |
| **RING-R2** | the level set `r₂ = r₂(prompt)` | varying `r₁` at fixed `r₂` |

On a Smith chart, constant-resistance and constant-reactance loci are both
circles through the point `Γ = 1`; constant-`|Γ|` circles are centred on the origin.
RING-R1/RING-R2 are therefore the chart's *native* two families (this is the
"two-ring" instrument of `modules/scale`). RING-Γ is the constant-mismatch
circle.

### 7.2 Vocabulary side: a precomputed position index

For each vocabulary entry `w` (a sense) the ring values `(r₁(w), r₂(w))` are
computed **offline** over the single-word unit, giving `Γ(w)`. An index sorted by
`(|Γ|, arg Γ)` (or by `r₁`, `r₂` for the level-set variants) lets the traversal
find nearby words without scanning the vocabulary. [HYP: an O(log V + k) lookup
with k = words returned; unmeasured — `PERF-02`.]

> A single word is a degenerate unit for ring functions that need `|W| ≥ 2`
> (RP-B spread, RP-A/RP-D entropy). For vocabulary entries the pair must be
> defined on a single sense (e.g. depth and relation-slot entropy of its own
> `vec`). The pair used for *units* and the pair used for *entries* must be the
> same functions evaluated on different supports; this requirement is checked by
> `SM-13`.

### 7.3 Traversal algorithm (deterministic)

```
traverse(prompt_point P, ring_variant, budget N, stop_rules):
    candidates = vocabulary entries on or within ε of the ring through P
    order = sort candidates by angular distance from P, alternating sides
            (θ₀, θ₀+δ, θ₀−δ, θ₀+2δ, θ₀−2δ, …); ties broken by lemma, ascending
    selected = []
    for w in order:
        if w violates register band or POS need: continue
        selected.append(w)
        if any stop rule fires: break
    return selected, reason_for_stopping
```

The order is a total order, so the result is **deterministic** (guarantee `SM-08`).

### 7.4 Stop rules (explicit — "adequate", not "everything")

| Rule | Fires when | [PARAM] |
|---|---|---|
| **S-BUDGET** | `len(selected) == N` | `N` per level (words per unit) |
| **S-ARC** | cumulative angular travel ≥ Δθ_max | Δθ_max |
| **S-SATURATE** | the last `k` selected words added no new `lexname` | `k` |
| **S-EMPTY** | no more candidates on the ring | — |

The return value includes `reason_for_stopping` ∈ {BUDGET, ARC, SATURATE, EMPTY}.
**Guarantee:** the loop terminates in at most `|candidates|` steps and never
returns more than `N` words (`SM-09`).

### 7.5 Scaling the context up

"Scale up" is the same traversal run at the next granularity: the
paragraph-level point (computed from the *union* of unit words) defines a ring;
traversing it yields the topic words for the paragraph plan. The relation between
levels is therefore a re-evaluation of the same locator on a bigger unit, not a
different algorithm. [HYP; tested by `SM-10` coverage-vs-budget at L1/L2/L3.]

## 8. Output of the locator

```
LocatorResult:
    pair_id         one of RP-A..RP-E (or a user pair id)
    ring_norm, anchor_policy
    r1, r2, Z, gamma (complex), abs_gamma, arg_gamma, scale_factor
    cell            (int, int)
    refusal         null | "EMPTY_INPUT" | "NO_IN_STORE_TOKENS" | "SINGLE_TOKEN_UNDEFINED"
```

**Refusal rule (CN-12):** if the chosen ring functions are undefined for the
input (e.g. spread on one token), the locator returns a refusal, never a
fabricated number (`SM-12`).

## 9. Tests

| ID | Checks | Metric |
|---|---|---|
| `SM-01` | Fold/unfold round-trip on real ring data, max error | MET-ERR |
| `SM-02` | **Ring independence** for each pair RP-A..RP-E | MET-IND |
| `SM-03` | Saturation: `|Γ|` distribution over the calibration set is not piled against 1 | MET-SAT |
| `SM-04` | Topic separation ratio (inter-subject vs intra-subject Γ distance) | MET-SEP |
| `SM-05` | Leave-one-out k-NN subject classification from Γ position | MET-KNN |
| `SM-06` | Anchor invariance of cross-ratios across anchor policies | MET-ERR |
| `SM-07` | Cell purity (fraction of a cell's items sharing the majority subject) | MET-PUR |
| `SM-08` | Traversal determinism: same input ⇒ identical output list | exact |
| `SM-09` | Stop rules honoured: ≤ N words, termination, reason reported | exact |
| `SM-10` | Topic-class coverage versus word budget | MET-COV |
| `SM-11` | Locally-square check on real data (should hold; sanity of the code) | MET-ERR |
| `SM-12` | Refusals fire for empty, OOV-only and single-token inputs | exact |
| `SM-13` | Unit-pair and entry-pair are the same functions on different supports | exact |
| `SM-14` | Variant comparison RING-Γ vs RING-R1 vs RING-R2 on SM-10 | MET-COV |

## 10. Decision rule

If **no** candidate pair passes `SM-02` and `SM-04`, the Smith-chart locator is
not viable *with these relationships*, and the next step is to propose new
relationships — not to relax the thresholds. The negative result is a data point
(chase-every-anomaly rule), recorded in the result log with the failing pair.

## 11. C-port notes

Per-entry `(r₁, r₂, Γ)` is a fixed 3×float record parallel to the `WordRec`
table; the sorted position index is a `uint32` permutation array. Traversal needs
no allocation beyond the output buffer of size `N`.
