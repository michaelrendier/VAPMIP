## Phase 39 — Running a Boxkite: Hub, Fiber, UFT Dial (2026-09-24)

*Claude Sonnet 5. Documents `scaled_mind_eye_boxkite_kernel_monad.py`, built
against Cody's own derivation, same session: "how do i use 0_RB + L_(I|O) +
UFT... to 'run a boxkite'." Reuse discipline unbroken again — `GaugeEye`,
`GaugeHands`, `GaugeStep`, `GaugeSteeringFailed` imported from Phase 38's
file, `BoxKite`/`MindsEye`/`PapersHands`/`SED_DIM` from `rotary_rerun_monad.py`.
This file adds exactly one new thing: the hub-anchored fiber-sequence loop
those pieces were missing.*

---

### The three pieces, in the roles derived for them

- **`0_RB` = the HUB.** `e_0`/`e_8`, the one fixed point shared by all seven
  otherwise-disconnected box-kite charts (`bk.fixed_point_gluing`,
  `bk.e0_is_outside` — both ESTABLISHED, checked not asserted: `e_0` is not
  a `PG(3,2)` point, is in no Assessor, its associator always vanishes).
  `bk.fixed_point_weight(psi)` — `psi[0]²/|psi|²` — is the **structural
  constant** itself: computed identically regardless of which chart or
  which reading is in use.
- **`L_(I|O)` = the FIBER.** One throw from the hub out to a specific chart
  (one strut, one grammatical/semantic role) and back. `throw_fiber()`
  builds `psi` fresh from `HUB_PSI` on every call — there is no path back to
  construct, because the throw never left a residue at the previous landing
  point. That *is* "return to the hub between fibers," structurally
  enforced, not merely asserted.
- **UFT = the DIAL.** `GaugeEye.continuous_snapshot()` already reads both
  readings off one landed instant: `is_zero_divisor` (discrete) and
  `a_matrix_basin_windspeed` (continuous). Deliberately **not** `h_rb_hat`'s
  σ-facet table (`sigma_to_theory`, σ=0/½/1/2/real-only) — `sigma_self` here
  is the box-kite's own native quantity, a different σ than `h_rb_hat`'s
  `Re(s)` coupling exponent (see `Ainulindale/wiki/123_sigma_rb_mass_gap_
  calibration.md`, "THREE SIGMAS — do not conflate them"). Feeding one into
  the other's facet classifier would be exactly the conflation that page
  exists to prevent.

### Verification, not assertion

`fixed_point_weight` read `0.640000` at every one of the seven struts in the
first live run, no exceptions — the literal, numeric demonstration that the
hub-distance measure is identical across every otherwise-disconnected
chart, confirmed by running it, not by definition alone. One genuine,
freshly-observed correlation surfaced the same run and was flagged as open,
not folded in as confirmed: the continuous windspeed reading split cleanly
between struts carrying `BoxKite.lineage`'s GROUPING bit (struts 4–7,
windspeed `+12`) and those without it (struts 1–3, windspeed `0`) — checked
only at one depth, one Assessor choice; not chased further this pass.

### The Aule channel — Systems Analysis Harness, propagated

Per Cody's ruling the same session ("Aule is the Root of Systems Analysis
Harness... propagate from there into the new monad we just built"):
`_aule_channel()`, a defensively-imported, no-op-if-absent wrapper around
`PtolemyDesktop/Aule/aule.py`'s real `stream_event()`. Channel name
`"mind_eye_boxkite"`. `hub_report()` publishes `hub_confirmed`;
`throw_fiber()` publishes `fiber_thrown` per crossing. Verified live, not
just wired: 8 real events (1 hub + 7 fibers) landed in Aulë's own
`aule.log` on a direct test run; a second run with `_stream_event` forced
to `None` confirmed the kernel still runs cleanly with Aule absent. This is
the reference instance of the repeated-channel pattern — the next monad
copies `_aule_channel`'s shape and swaps the channel name, not re-derives
the wiring.

### Status

Built, self-tested (`__main__`: hub report, one fiber per strut 1..7,
structural-constant check). No `ptol.c` changes. `monad_harness.c`'s own
`mh_pump`/`mh_ingest_support` were made real the same session (a separate,
C-layer thread — "the beginning of the PtolemyDesktop Event Handler for the
monad," the general bus function deliberately deferred) but are not wired
into this Python kernel; that remains open.
