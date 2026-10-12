# 05 — Splitting Text by Topic Shift (M-TILE)

**Purpose:** find where one topic ends and the next begins, so (a) deconstruction
can segment an input, (b) the paragraph-level (L2) state can be reset at the right
moment, and (c) construction can be checked for topic coherence.

---

## 1. TextTiling (Hearst, 1997) [LIT]

Lexical-cohesion segmentation, no training:

1. Cut the token stream into fixed-length **pseudo-sentences** of `w` tokens.
2. Group `k` pseudo-sentences into a **block**.
3. At each **gap** between pseudo-sentences compute the similarity of the block
   on the left to the block on the right (word-count cosine = *block comparison*;
   or *vocabulary introduction*: count of new words).
4. **Smooth** the similarity sequence.
5. At each local minimum compute a **depth score**:
   `depth(g) = (peak_left − sim(g)) + (peak_right − sim(g))`
   where `peak_left`, `peak_right` are the nearest local maxima on either side.
6. Place a **boundary** at gaps where `depth(g) > cutoff`,
   with `cutoff = mean(depth) − σ(depth)/2` (liberal) or `mean − σ` (conservative).
7. Snap boundaries to the nearest real paragraph break.

## 2. The NLTK implementation [CODE, checked 2026-10-12]

`nltk.tokenize.TextTilingTokenizer(w=20, k=10, similarity_method='block_comparison',
stopwords=None, smoothing_method=[0], smoothing_width=2, smoothing_rounds=1,
cutoff_policy=1, demo_mode=False)`. In the installed source (nltk 3.10.3):
`BLOCK_COMPARISON`, `VOCABULARY_INTRODUCTION`; `LC, HC = 0, 1`; with `cutoff_policy
== LC` the cutoff is `avg − stdev`, otherwise `avg − stdev/2.0` (so the default
`cutoff_policy=1` is the liberal rule). It **raises `ValueError`** ("No paragraph
breaks were found (text too short perhaps?)") when the input contains no paragraph
breaks. Input must therefore be paragraph-delimited text.

> The error behaviour is a feature for this project: it is an explicit refusal.
> The spec requires the variants below to keep that property (`TT-05`).

## 3. Why the baseline is weak for this project [HYP]

Block comparison uses **literal word overlap**. Two passages about the same topic
in different words (synonyms, hypernyms, related terms) look unrelated. The
vocabulary store already knows relational structure (`vec[19]`, hypernym
hierarchy), so a similarity that uses it should place boundaries by *meaning*.

## 4. Variants specified

| ID | Name | Unit | Block similarity | Notes |
|---|---|---|---|---|
| **TT-0** | NLTK baseline | token pseudo-sentences | word-count cosine | reference; unmodified `TextTilingTokenizer` |
| **TT-1** | Sentence units | real sentences | word-count cosine | removes the arbitrary `w`; tests whether pseudo-sentences matter |
| **TT-2** | Relational block similarity | sentences | cosine of summed `vec19` of in-store content words, optionally `ln(1+·)` first | the 19D variant |
| **TT-3** | Lexname-histogram similarity | sentences | cosine of `lexname` histograms | coarser, robust to sense error |
| **TT-4** | Multi-timescale mismatch | sentences | `1 − cos(ĉ[short τ], ĉ[long τ])` from `04_*` | no blocks; shift = short and long memories disagree |
| **TT-5** | Combined | sentences | weighted mean of TT-2 and TT-4 | weights [PARAM] |

All variants share steps 4–6 (smoothing, depth score, cutoff) so differences are
attributable to the similarity alone. The cutoff policy is a [PARAM] swept in
`TT-07`.

### 4.1 TT-4 in detail [HYP]

Maintain two decayed averages of the sentence vectors with `τ_short < τ_long`
(`04_*`). Let `a_t = ĉ_short(t)`, `b_t = ĉ_long(t)`. Define
`d_t = 1 − cos(a_t, b_t)`. A topic shift appears as a rise in `d_t` (the recent
past has moved away from the longer past). A boundary is a local maximum of `d_t`
exceeding a cutoff. This needs no block size and is O(19) per sentence; it is the
cheapest candidate and the one most compatible with streaming.

### 4.2 Refusals (CN-12)

All variants must return an explicit refusal when: fewer than `2·k` sentences
(blocks variants) or fewer than 3 sentences (TT-4); no in-store tokens; or all
similarities equal (zero variance ⇒ depth scores undefined).

## 5. Segment output

```
Segmentation:
    variant_id, params
    boundaries   sorted list of sentence indices where a new segment begins
    depth        list of depth (or d_t) values per gap
    cutoff       value used
    refusal      null | "TOO_SHORT" | "NO_IN_STORE_TOKENS" | "ZERO_VARIANCE"
```

## 6. Metrics (defined in `11_metrics_and_benchmarks.md`)

- **Pk** (Beeferman, Berger & Lafferty, 1999) — probability that two units `k`
  apart are wrongly judged to be in the same / different segments; `k` is half the
  mean true segment length. Lower is better.
- **WindowDiff** (Pevzner & Hearst, 2002) — fraction of sliding windows in which the
  number of hypothesised boundaries differs from the reference count. Lower is
  better. Penalises near-misses less harshly than exact-match scoring.
- **Boundary P/R/F1 with tolerance ±t units** — t ∈ {0, 1, 2}.

Reference values are from gold boundaries in the calibration set
(`10_calibration_set_spec.md` §5).

## 7. Tests

| ID | Checks | Metric |
|---|---|---|
| `TT-01` | TT-0 baseline on the gold-boundary items | MET-PK, MET-WD, MET-BF1 |
| `TT-02` | TT-2 against TT-0 on the same items | same |
| `TT-03` | **Synonym-swap robustness**: replace content words in a gold item by synonyms; word-overlap variants should degrade, relational variants should not [HYP] | change in MET-WD |
| `TT-04` | No-boundary text yields zero (or minimal) boundaries | count |
| `TT-05` | Refusals fire for too-short, no-token and zero-variance inputs | exact |
| `TT-06` | TT-4 vs TT-0/TT-2 | MET-PK, MET-WD |
| `TT-07` | Cutoff-policy sweep (liberal / conservative / fixed percentile) | MET-WD, MET-BF1 |
| `TT-08` | Streaming equivalence: TT-4 online gives the same boundaries as TT-4 batch | exact |
| `TT-09` | Segment-size sensitivity: very short and very long true segments | MET-WD |
| `TT-10` | Latency per sentence for TT-2, TT-4 | MET-LAT |

## 8. Use inside the system

- **Deconstruction:** segment a long input, then run the locator on each segment
  (a multi-topic prompt gets one topic-land point per segment).
- **State:** a detected boundary triggers `boundary(L2, β)` (`04_*` §4).
- **Construction check:** run the segmenter on the *generated* response and compare
  to the plan's intended segments (`GEN-05`).

## 9. C-port notes

TT-4 is the C-friendly candidate (two 19-float states, one cosine per sentence).
TT-2 needs per-block vector sums (rolling add/subtract, no re-scan). The smoothing
and depth-score steps are O(number of gaps).
