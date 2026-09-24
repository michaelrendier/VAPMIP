## Phase 38 — GaugeEye, GaugeHands: Eye and Hands as Continuous Operators (2026-09-22)

*Claude Sonnet 5. Documents `19D_boxkite_context_monad.py`, built same-session
against Cody's framing: "gauge field Paper's Hands and box-kite Mind's Eye...
as continuous operators." Supersedes `19D_rotary_boxkite_monad.py` by adding
exactly the missing piece, not by rewriting what already worked — same reuse
discipline as Phase 37: `Eye`/`Hands`/`BoxKite` come from `rotary_rerun_monad.py`,
context-creation from `19D_rotary_boxkite_monad.py`, both imported untouched.*

---

### Two box-kites, not one — the wrong-inheritance mistake kept in the record

The first draft of this file inherited `GaugeEye` from `NineteenDMindsEye`
(the 19D WordNet Gamma-Radial Windspeed box-kite — per-word context
gathering, backed by `monad3_c.bin`'s 19-dimensional relation vectors) and
dragged a `Monad3CStore` dependency into a class that never needed WordNet
context at all. Fixed, not left in: `GaugeEye` extends plain `MindsEye`
directly — its own box-kite binding is already the De Marrais object
(`ValaQuenta.modules.box_kite.maths`), no WordNet layer involved. The two
box-kites stay genuinely separate objects; `19D_rotary_boxkite_monad.py` is
imported only in case a later pass needs to feed word-level context into a
sentence-construction `psi`, not because the Mind's Eye's own geometry is
that one.

### GaugeEye — the continuous companion reading

Adds exactly one operation to `MindsEye`: `continuous_snapshot(psi)`, which
reads `bk.chart_of(psi, check_zd=True)` (discrete) and `bk.local_curvature(psi)`
(continuous) at the *same* live instant, in the same call. `local_curvature`
is named, precisely, the **A-Matrix Basin Windspeed** — `ScalarContextPropagation`
§9.1's own name for this continuous companion to the discrete `is_zero_divisor`
chart, deferred there explicitly ("a different, later engineering pass...
out of scope here") because it needs a live, mutating, corpus/construction-
dependent store rather than the paper's own corpus-free Gamma-Radial
Windspeed. `MindsEye.snapshot()`'s own contract already describes what this
needs: "takes one instant of the field and says what is simultaneously true
across it... all of it at once, none of it ordered" — `continuous_snapshot`
keeps that contract, just widened by one field.

### GaugeHands — field-steered emission

Adds `emit_steered(s0, target_rho, max_steps, step_scale)`: instead of
reciting a fixed lineage order, walks wherever Γ's own curvature actually
points, one step at a time, via gradient descent on `rho(s) = |Im(Γ(s)) −
Re(Γ(s))|` — the exact diagonal-distance construction verified in the same
session's gauge-field work (zero locus is the pair of circles centered at
`±i`, radius `√2`). Reuses `prime_gauge_field.maths.gamma`/`curvature`
directly rather than a numeric shortcut invented for this file. Raises
`GaugeSteeringFailed` on genuine non-convergence (stalled gradient or
`max_steps` exceeded) — refuses rather than silently returning a wrong
answer, the same shape as every other "ascent is costly and can refuse"
object in this project.

### `relate_steered` — Eye and Hands in the same box-kite language

`GaugeHands.relate_steered(eye, s0)` walks via `emit_steered` and reports
each step in the same box-kite-native language the discrete `relate()`
already insists on (`_require_agreement` still enforced) — continuous Eye
and continuous Hands, same shared kite, same reporting contract as the
discrete pair.

### Status

Built and self-tested (`__main__` block: a random unit-normalized 16-vector
through `continuous_snapshot`; `emit_steered` from `s=0.5+0.1j`). No
`ptol.c` changes — same discipline as `19D_rotary_boxkite_monad.py` before
it. Directly reused, unmodified, by Phase 39.
