# 11 — Metrics and Benchmarks

Defines every metric used by `test_matrix.json`, the latency/memory protocol, and
the result-log format. A metric ID is `MET-*`. Tests cite metrics by ID.

---

## 1. Conventions

- All scores are computed on a stated **split** of a stated **set version**.
- A score without its parameters (`ring_norm`, `anchor_policy`, `τ` ladder, `β`,
  cutoff, budgets, `entity_id`, `include_hyponyms`) is not comparable and must not
  be reported.
- "exact" tests are boolean; any failure is reported with the failing item ids.

## 2. Numeric accuracy

**MET-ERR** — maximum relative error `max |a − b| / max(|b|, ε)`, ε = 1e-300.
Pass criteria are stated per test (e.g. 1e-12 for exact decay, 1e-9 for fold
round-trips — the tolerance already used in `modules/scale`).

## 3. Smith-chart locator metrics

**MET-IND (ring independence).** For a candidate pair over the calibration set,
compute (a) Spearman rank correlation ρ between `r₁` and `r₂`, and (b) `R²` of the
best linear fit `r₂ ≈ a·r₁ + b`.
Verdict: **DEGENERATE** if `|ρ| > 0.9` or `R² > 0.99` (the J_red/J_blue case had
`R² = 1` exactly); **WEAK** if `0.7 < |ρ| ≤ 0.9`; **INDEPENDENT** otherwise.
[PARAM thresholds.] Reported with a scatter summary (10×10 occupancy grid).

**MET-SAT (saturation).** Fraction of calibration units with `|Γ| > 0.95`.
Verdict **SATURATED** above 0.25 [PARAM]; this is the signature of the raw-count
pair in `modules/scale`.

**MET-SEP (separation ratio).** With subject labels:
`SEP = mean inter-subject Γ-distance / mean intra-subject Γ-distance`, where the
distance is `|Γᵢ − Γⱼ|`. `SEP > 1` means subjects separate; report also the
per-subject-pair matrix.

**MET-KNN (nearest-neighbour accuracy).** Leave-one-out k-NN (k = 1, 3, 5) subject
classification using Γ position (or cell). Report chance level (1/8 for T1).

**MET-PUR (cell purity).** For each non-empty cell, the fraction of its items
sharing the majority subject; report the item-weighted mean and the number of
singleton cells.

**MET-COV (topic-class coverage).** Wording-independent comparison of a generated
text `G` against a reference `R`:
- `K(T)` = set of classes of the in-store content words of `T`, where a class is
  the pair `(lexname, hypernym ancestor at depth d)`, d = 3 [PARAM].
- `COV = |K(G) ∩ K(R)| / |K(R)|` (recall of reference topic-classes).
- `PREC = |K(G) ∩ K(R)| / |K(G)|`.
- **Budget efficiency** `EFF = COV / n_content_words(G)`.
Reported with `d` and the store coverage of `R` (`CAL-07`), since classes that the
store cannot represent cannot be recovered.

## 4. Segmentation metrics

Let a text have `N` units, a reference segmentation `ref` and a hypothesis `hyp`
(each a list of 0/1 boundary indicators over the `N−1` gaps).

**MET-PK (Beeferman et al., 1999).** Slide a window of width `k` (default: half the
mean reference segment length, rounded) over the text. Count windows in which `ref`
and `hyp` disagree on whether the two ends lie in the same segment. `Pk` =
disagreements / windows. Lower is better.

**MET-WD (Pevzner & Hearst, 2002).** Same window; count windows in which the
**number of boundaries** inside the window differs between `ref` and `hyp`.
`WD` = such windows / (N − k). Lower is better.

**MET-BF1.** Boundary precision, recall and F1 with tolerance `t ∈ {0,1,2}` units:
a hypothesised boundary is correct if within `t` of an unmatched reference
boundary.

Report all three; no single one is sufficient (Pk is known to favour hypotheses
with few boundaries).

## 5. Discourse metrics

**MET-DIST.** A discrete distribution (e.g. Centering transition fractions).

**MET-TV (total variation distance).** `½ Σᵢ |pᵢ − qᵢ|` between two discrete
distributions. 0 = identical, 1 = disjoint.

**MET-ACC.** Accuracy of a classification against gold labels.
**MET-DEF (default rate).** Fraction of decisions in which the rule table fell to
its declared default. Always reported next to MET-ACC.

**MET-RATE.** Fraction of items satisfying a stated predicate.

## 6. Latency and memory protocol

All latency claims in this project are **[UNMEASURED]** until a log exists. This is
the protocol that produces one.

**MET-LAT (latency).**
1. Fix the machine (§7) and record `lscpu`, `/proc/meminfo` summary, kernel, Python
   version, nltk version, git commit of the tested tree.
2. **Warm-up:** discard the first 50 calls of each component.
3. **Sample:** at least 1,000 timed calls per component per condition, using a
   monotonic clock (`time.perf_counter_ns` in Python; `clock_gettime(CLOCK_MONOTONIC)`
   in C).
4. Report **p50, p95, p99, max** and the number of samples. Mean alone is never
   reported.
5. Conditions, reported separately (never pooled):
   - **cold:** first call after process start (includes store mmap/open, NLTK
     import);
   - **warm in-process:** repeated calls in one process;
   - **subprocess:** the path `ptol.c` uses today — `popen("python3 … --stdin …")`
     per call.
6. **Components timed independently:** store lookup; Γ_rad of a word; locator;
   traversal; one decay update per level; connective choice; Centering step;
   TextTiling variant per sentence; full `build_text`; end-to-end `console_speak`.

**Why the subprocess condition is mandatory.** `ptol.c` `get_monad_words()` and
`get_monad_sentence()` each start a fresh `python3` process per call [CODE]. Process
start-up and NLTK import are likely to dominate the arithmetic of any context method
specified here. If the subprocess condition dominates, the latency budget is decided
by *where the code runs*, not by the method. `PERF-02` isolates this.

**MET-MEM.** Resident set size (`ru_maxrss` / `/proc/self/status` VmRSS) after
warm-up, and the growth over 10⁵ calls (must be flat; `PERF-03`).

**MET-SWEEP.** For each [PARAM] under calibration: the grid of values tried, the
score at each on the **dev** split, the chosen value, and the **test** score at the
chosen value (reported once).

## 7. Reference hardware

Two repository documents disagree about the laptop:

| Source | CPU |
|---|---|
| `VAPMIP/docs/SYSTEM_SPECS_ThinkPad_X1_Carbon_6th.md` (snapshot 2026-07-31) | Intel Core i7-8550U @ 1.80 GHz, 4 cores / 8 threads |
| `VAPMIP/PtolC/README.md` benchmark table | Intel Core i7-6600U @ 2.60 GHz, 4 logical cores, 8 GB RAM |

They cannot both describe the same machine. The protocol therefore **does not
assume either**: every result log captures `lscpu` at run time (§6 step 1), and the
log's `machine` block is authoritative. Which document is stale is for the author to
settle; this spec flags it so older benchmark numbers are not compared against new
ones without checking.

## 8. Result-log format

Each benchmark run writes one JSON file validated against
`schemas/result_log.schema.json`:

```json
{
  "log_version": "1.0",
  "run_id": "2026-10-12T14-30-00Z_DEC-01",
  "spec_version": "0.1",
  "calibration_set_version": "1.0",
  "split": "dev",
  "git_commit": "…",
  "machine": {"cpu": "…", "cores": 0, "ram_mb": 0, "kernel": "…", "python": "…", "nltk": "…"},
  "parameters": {"tau": [3, 12, 48, 192, 768], "ring_norm": "median", "anchor_policy": "AP-2"},
  "tests": [
    {
      "test_id": "DEC-01",
      "status": "PASS",
      "metric": "MET-ERR",
      "value": 2.2e-16,
      "threshold": 1e-12,
      "n_items": 0,
      "failing_items": [],
      "notes": ""
    }
  ]
}
```

`status` ∈ {`PASS`, `FAIL`, `ERROR`, `SKIP`, `UNIMPLEMENTED`}. A test that errors is
`ERROR`, never `FAIL` and never silently dropped. Logs are append-only; a rerun
writes a new file.

## 9. Pass / fail philosophy

- **Exact tests** (boolean) must pass; failure is a defect.
- **Metric tests** carry a threshold in `test_matrix.json`. At v0.1 almost all
  thresholds are `null` — the first benchmark run *establishes a baseline*; the
  baseline is then written into the matrix as the regression threshold with its
  provenance (run id).
- A result that is legal but surprising is a **data point to chase**, recorded in
  the log `notes` with the run id, not discarded and not called negative.

## 10. Test list (performance)

| ID | Checks | Metric |
|---|---|---|
| `PERF-01` | Component latencies (warm, in-process) | MET-LAT |
| `PERF-02` | Subprocess versus in-process, same component | MET-LAT |
| `PERF-03` | Memory growth over 10⁵ calls is flat | MET-MEM |
| `PERF-04` | Cold start | MET-LAT |
| `PERF-05` | Scaling with context window size n ∈ {10, 50, 200, 1000} words; fit exponent | MET-LAT |
| `PERF-06` | End-to-end `build_text` latency by response length | MET-LAT |
| `PERF-07` | Python vs C implementation of a ported component (after porting) | MET-LAT |
