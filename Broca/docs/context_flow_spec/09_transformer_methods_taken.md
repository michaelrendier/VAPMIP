# 09 — Transformer Methodology Taken, Weights Excluded

**Constraint (hard):** no transformer is run. Heavy-token transformers are a wall on
laptop-class hardware. What is taken is the *handling of context, topics, subject
matter and ideas* — as arithmetic that can be written down, inspected, and run
without trained tensors.

This document records each borrowed idea, what it is in the transformer, what the
weight-free version is here, and how it is tested.

---

## 0. Background: the four named families [LIT]

| | BERT (2018) | RoBERTa (2019) | T5 (2019) | GPT line |
|---|---|---|---|---|
| Layout | encoder only | encoder only | encoder + decoder | decoder only |
| Sees | both directions | both directions | encoder: all; decoder: causal | left context only |
| Trained to | fill masked words; next-sentence | fill masked words (dynamic masking) | reconstruct dropped spans (text-to-text) | predict next token |
| Output | per-token vectors | per-token vectors | text | text |

Consequence for this project: **reading** (deconstruction) corresponds to the
encoder behaviour — everything in view at once; **writing** (construction)
corresponds to the decoder behaviour — ordered emission; T5 is the case where both
are one object with an explicit seam. These are correspondences used to organise
the design (`01_*` §1), not claims that the architecture is copied.

## 1. M-ATT — attention as weighted lookup

**In the transformer [LIT]:** for query `q` and context items with keys `kᵢ` and
values `vᵢ`, the output is `Σ softmax(q·kᵢ/√d)ᵢ · vᵢ` — a soft dictionary lookup.
Cost is quadratic in context length.

**Here [HYP]:** context items are the in-store words of the context window; the
"key" is the item's `vec19` (or a transform of it); the "query" is the current
need (a candidate word, or the unit's decayed state `ĉ`). Weights are explicit:

```
w_i = softmax_i( −β · dist(q, k_i) )        β > 0   [PARAM: sharpness]
output = Σ w_i · v_i
```

`dist` is one of the similarity candidates from `04_*` §5. No parameters are
learned; `β` is swept.

**Properties that must hold (checkable):**
- `Σ wᵢ = 1`, `wᵢ ≥ 0` (`ATT-01`).
- Permutation invariance of the output over context order (`ATT-02`).
- `wᵢ` is non-increasing in `dist` (`ATT-03`).
- As `β → 0` the output tends to the plain average; as `β → ∞` to the nearest item
  (`ATT-06`).

**Cost:** n² pairs of 19-dim distance for a window of n words. [UNMEASURED]; the
scaling is tested in `ATT-04` and `PERF-05`, and the window size is bounded by the
decay ladder (older context is summarised, not attended to).

**Relationship to M-DECAY:** the decayed state is attention with a *fixed* weight
profile (`λ^age`); M-ATT is attention with a *content-dependent* profile. Both are
supplied so the calibration set can say whether content-dependence earns its cost
(`ATT-05`).

## 2. M-POS — positional encoding

**In the transformer [LIT]:** position `pos` is encoded as a vector of sines and
cosines at geometrically spaced frequencies:
`PE(pos, 2i) = sin(pos / 10000^(2i/d))`, `PE(pos, 2i+1) = cos(pos / 10000^(2i/d))`.
It gives order information to an otherwise order-blind operation.

**Here [CODE + HYP]:** `ptol.c` `project()` already uses a sin/cos pair per shell at
frequency `2π/p_k` with `p_k` the first 16 primes (J_blue = sin shells, J_red = cos
shells). The structural similarity is real; the frequency spacing differs
(geometric in the transformer, prime here). This is **a similarity to test, not an
equivalence**.

**Question:** which frequency bank gives a better *position code* for the context
window — one in which distinct positions are well separated and a given offset has
a consistent signature?

**Tests:**
- `POS-01` — minimum pairwise distance between position codes over positions
  0..n−1, for the geometric bank vs the prime bank at equal dimension.
- `POS-02` — aliasing length: the smallest `n` at which two positions have
  near-identical codes (prime frequencies are incommensurate; geometric ones are
  not necessarily).
- `POS-03` — offset consistency: for a fixed offset `δ`, the distance
  `‖PE(p) − PE(p+δ)‖` as a function of `p` (a good code has low variance).

Decision rule: if the prime bank is not worse on all three, prefer it (it is already
in the engine). If it is worse, record by how much.

## 3. M-BPE — subword merges

**In the transformer [LIT]:** byte-pair encoding repeatedly merges the most frequent
adjacent symbol pair to build a vocabulary of subwords. Deterministic.

**Here [HYP]:** purpose is the **out-of-vocabulary** case (`oov` in the reading
record). A prompt word not in the store is split into the longest in-store subwords
so some context can still be read. Merge table built from the store's own word list
(offline, deterministic).

**Guarantees:** `decode(encode(w)) == w` for every string (`BPE-01`, round trip);
encoding is deterministic (`BPE-02`); an OOV word either yields ≥ 1 in-store
subword or an explicit `NO_IN_STORE_SUBWORD` refusal (`BPE-03`).

**Caution:** subword vectors are not word vectors. The spec marks subword-derived
context as `provenance = "subword"` and the locator may down-weight it [PARAM].

## 4. M-RES — residual (identity-preserving) update

**In the transformer [LIT]:** each layer *adds* its output to the running vector
rather than replacing it (`x ← x + f(x)`), so the original signal is never lost.

**Here:** the decay update `C ← λC + v` is exactly this shape — the old state is
kept (scaled) and the new input is added. The test is that the update never
overwrites: `DEC-01`/`DEC-02` already cover it. Recorded here so the correspondence
is explicit.

## 5. M-MASK — masking / forbidden dependencies

**In the transformer [LIT]:** the causal mask forbids attending to future tokens;
this is what lets a decoder be trained and run left to right.

**Here:** (a) during construction the planner may not read units it has not yet
planned (no forward reference); (b) the dependency DAG of plan operations must be
acyclic. The second is the same check `pathway_decompose` already makes
(`ValueError` on cycle or missing name [CODE: `modules/scale`]).

**Tests:** `MASK-01` a unit's plan never depends on a later unit; `MASK-02` the
plan DAG is acyclic on every calibration prompt.

## 6. Ideas deliberately **not** taken

| Idea | Why not |
|---|---|
| Learned embeddings | Replaced by the precomputed `vec19` / Γ_rad. |
| Multi-head attention with learned projections | No learning; one explicit similarity per experiment. |
| Layer stacking with learned feed-forward blocks | Depth is provided by the granularity ladder, not by learned layers. |
| Next-token probability over a vocabulary | Replaced by ring traversal and a clause-pattern realiser; no probability distribution is claimed. |
| Pre-training on large corpora | The vocabulary store is the pre-computation. |

## 7. Tests

| ID | Checks |
|---|---|
| `ATT-01` | Weights are a probability distribution |
| `ATT-02` | Output invariant under reordering of context |
| `ATT-03` | Monotone in distance |
| `ATT-04` | Empirical cost vs window size n (fit exponent) |
| `ATT-05` | Content-dependent weighting vs fixed decay weighting vs plain average, on topic-class coverage of the generated response |
| `ATT-06` | Limits β→0 and β→∞ |
| `POS-01..03` | Position-code comparison (§2) |
| `BPE-01..03` | Round trip, determinism, refusal (§3) |
| `MASK-01..02` | No forward reference; acyclic plan DAG (§5) |
