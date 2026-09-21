## Phase 37 — The Composter Monad: Eye/Hands Reused, Not Reinvented (2026-09-21)

*Claude Sonnet 5. Written to document `rotary_rerun_boxkite_monad.py` in its
current, real form — last touched 2026-08-31 (`fb5fc1e`), cited directly by
the `ScalarContextPropagation` paper's §11 as the live `BoxKite` object. This
page runs the file for real and reports what it actually does and actually
measures, closing the loop Phase 36 left open at its item 3
("full-response rendering ... via `rotary_rerun_boxkite_monad` — still where
we are, on purpose").*

---

### Where it belongs, and the one thing it deliberately does not do

`RotaryBoxKiteMonad` is one Monad holding both faces already built in
`rotary_rerun_monad.py` — `MindsEye` (internal visual space: reads, snapshot,
all-at-once, never emits, never renders, never touches anything external)
and `PapersHands` (ordered emission — and per this file's own design note,
rendering and external interaction belong here too, not on a separate output
object). It does not build a third Eye/Hands pair, and does not spin up a
second thread pair alongside the real ones — the file's own header quotes
the exact instruction this was built against: *"we don't need whole lots of
separate layers ... all doing work together if the monad does literally all
the work."* `BoxKite.between(self._eye_obj, self._hands_obj)` is built once,
in `__init__`, from those same two objects — not a metaphor, the literal
signed instance the `ScalarContextPropagation` paper's §11 quotes as *"the
relational language spoken by both MindsEye and PapersHands."*

### The composter, validated against existing code before this file existed

`sentence_context.py`'s `root_vector` (per-word `context_vector`s,
componentwise-summed into one sentence root) is the same operation as
`rotary_rerun_monad.py`'s `Reading.summed_with()`, run at 19 WordNet-relation
dimensions instead of 7 box-kite-strut dimensions. "Composter" names the
operation correctly — individual leaf identity genuinely merges into one
substrate, confirmed independently by the word-salad order-independence test
in Phase 32 — and it is the codebase's own precise term (`summed`, alongside
`shared` = gcd/min and `combined` = lcm/max, the last one not yet built).

### The v5.1 pipeline, one entry point

`process_input(text)`, in order:

1. **Composite** — `build_sentence_context(text)` folds the sentence's words
   into one root vector; `infer_direction(root_vector)` picks a grammatical
   frame (`classify`, `enumerate`, `decompose`, ... 13 total).
2. **Look inward** — `cam_encode(text)` → `MindsEye.snapshot()`. Internal
   only, exactly as designed; nothing external is touched here.
3. **Word selection**, PACE-style — the v5.1 constructor (radical distance +
   gamma_radial fold + conjugate scale + co-occurrence basin) is tried first;
   `nearest_synsets` over a neighborhood corpus is the guaranteed fallback if
   the constructor path raises or returns nothing. Never a hard failure.
4. **Schema prune** — `context_pruner.embed16`/`prune` collapses
   perspective-redundant candidates, holding a redundancy margin (never below
   3 while there are 3 to keep).
5. **Mind's Eye recursive repass** — `MindsEyeRepass` walks a 16-word frame /
   15-edge tree, one step per word, recording coverage.
6. **Assemble** — `assemble_sentence(direction, words_out)`, a real,
   honestly-scoped template layer (13 templates, `{0}`-style slot filling,
   pads by repeating the last candidate rather than crashing on an
   under-filled template). Named in-file as exactly what it is, not oversold
   as an NLG system.
7. **Look outward** — `PapersHands.relate()` (the real pathway emission) plus
   `harness.present()` — rendering lives here, on this face, not on a
   separate object, per the same design note §1 above quotes.
8. **Self-ingest** — the Monad hears its own output (`monad_english_io.hear`,
   `echo=0`) while it is still in Hands.

### Run, live, this session (`.venv/bin/python3 rotary_rerun_boxkite_monad.py`)

```
BoxKite signature 1  7 struts, 42 assessors

=== input: 'the volcano formed a mountain of cinder and ash' ===
  response: 'it is made of beetle and mixture.'
  lit_struts_in / out / shared: [1..7] / [1..7] / [1..7]

=== input: 'she deposited her savings in the reserve account' ===
  response: 'it is made of detail and pica.'
  lit_struts_in / out / shared: [1..7] / [1..7] / [1..7]

=== input: 'the engine contains sixteen distinct operators' ===
  response: 'it is made of gearing and category.'
  lit_struts_in / out / shared: [1..7] / [1..7] / [1..7]

real   (input <-> its own response) strut overlap: [7, 7, 7]  mean=7.00
control(input <-> another response) strut overlap: [7, 7, 7]  mean=7.00

real    sigma_self delta: [0.0609, 0.2436, 0.0778]  mean=0.1274
control sigma_self delta: [0.0329, 0.1827, 0.1058]  mean=0.1071

[  ok] crossref.strut_overlap   real >= control  (n=3, direction only)
[FAULT] crossref.sigma_delta    real < control   observed 0.1274 vs 0.1071 (n=3)

2 relations   1 hold   1 FAULT   0 untested
```

Reported exactly, not softened. Two honest findings, both already anticipated
by the file's own comments rather than discovered fresh here:

- **`crossref.strut_overlap` "holds" with zero discriminating power.** Every
  run, real or control, lights all 7 struts on both sides — the file's own
  in-source note (`# ... which had zero discriminating power above`) already
  flags this before the coarser test is even run. A pass here is not
  evidence of anything; it was already known to be uninformative at this
  small `n` and this coarse a metric.
- **`crossref.sigma_delta` genuinely FAULTs.** The finer sigma_self-delta
  measurement — does a response sit closer to its own input than to a
  random other response, in the continuous field, not just the binary strut
  set — does not hold on this `n=3` sample (`0.1274` vs `0.1071`, real
  worse than control). Recorded as `MATHS` fault, not hidden, not re-run
  until it passed. `n=3` is explicitly too small to claim significance
  either way; this is a direction, and today the direction is wrong.

### What this confirms and what it leaves open

Confirms: the Eye/Hands reuse discipline holds end to end with no crash, no
silent fallback-without-record, and the box kite really does bind
(`signature 1, 7 struts, 42 assessors`) to the same two objects every run.
The sentence output is legible English, template-thin exactly as documented
(`'it is made of beetle and mixture.'` is a real run, not a cherry-picked
bad one) — Phase 36's item 3 ("full-response rendering ... via
`rotary_rerun_boxkite_monad`") is live, just not yet linguistically rich.

Leaves open, named rather than fixed here: the channel-split discrepancy the
file's own comment already flags (`rotary_rerun_monad.py` splits red/blue at
`k>=8`; `rotary_rerun.c` splits at `k in {4-7,12-15}` — two different
partitions computing `sigma_self` two different ways across the Python and C
sides); the `crossref.sigma_delta` FAULT itself, which needs a larger `n`
before it means anything either way; and `constructor`-vs-`nearest_synsets`
selector tracking — this run's stdout does not print which path each
sentence actually took, so a future pass should log `selector` per
`Encounter` rather than only carrying it in the dataclass.

### Where the `ScalarContextPropagation` paper picks this up

§11 ("The sentence constructor") cites this exact file and this exact
`BoxKite.between(eye, hands)` call as the real, live, signed instance behind
the quote it uses — named there as future work, explicitly not fed by that
paper's own windspeed yet. Nothing in this page changes that scoping; it
exists so the citation points at something checked, not assumed.
