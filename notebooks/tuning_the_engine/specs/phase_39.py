LABEL = "39"
TITLE = "Running a Boxkite: Hub, Fiber, UFT Dial"
DATE = "2026-09-24"
PAGE = "39_running_a_boxkite_hub_fiber_uft_dial.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """`scaled_mind_eye_boxkite_kernel_monad.py` holds the hub-anchored fiber loop: `0_RB` = HUB (`e₀`/`e₈`), `L_(I|O)` = FIBER (`throw_fiber`), UFT = DIAL (`GaugeEye.continuous_snapshot`). The page records a live run: `fixed_point_weight` 0.640000 at every one of the seven struts; windspeed `+12` on struts 4–7 (GROUPING bit) and `0` on 1–3; 8 real events (1 hub + 7 fibers) in Aulë's log."""),
("code", """import scaled_mind_eye_boxkite_kernel_monad as K, rotary_rerun_monad as RR, ValaQuenta.modules.box_kite.maths as bk
events = []
K._stream_event = lambda ch, ev, payload=None, *a, **k: events.append((ch, ev, payload))      # capture instead of writing to Aulë's real aule.log
kern = K.MindEyeBoxKiteKernel()
print("Aulë stream hook replaced by a capture function (the real log is not touched)")"""),
("md", """## 1 · The hub is real before it is used
`bk.fixed_point_gluing`, `bk.e0_is_outside`: `e₀` is not a PG(3,2) point, is in no Assessor, its associator always vanishes; `fixed_point_weight(psi) = psi[0]²/|psi|²`."""),
("code", """hub = kern.hub_report()
print({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in list(v.items())[:4]}) for k, v in hub.items()})
L.check("e₀ is outside the geometry (not a PG(3,2) point, in no Assessor, associator vanishes)", hub["e0_is_outside"]["e0_is_outside_the_geometry"] and not hub["e0_is_outside"]["e0_is_a_pg32_point"] and not hub["e0_is_outside"]["e0_in_any_assessor"] and hub["e0_is_outside"]["e0_associator_always_vanishes"])
L.check("the two orphan indices are 0 and 8", hub["fixed_point_gluing"]["indices_in_no_assessor"] in ([0, 8], (0, 8)))
L.check("hub fixed_point_weight is exactly 1 at HUB_PSI", abs(hub["hub_fixed_point_weight"] - 1.0) < 1e-12, str(hub["hub_fixed_point_weight"]))
L.check("fixed_point_weight(psi) = psi[0]²/|psi|² on random psi", all(abs(bk.fixed_point_weight(list(p)) - p[0]**2/(p@p)) < 1e-12 for p in np.random.default_rng(0).normal(size=(50, 16))))"""),
("md", """## 2 · One fiber per strut — and the structural constant"""),
("code", """throws = kern.run_boxkite([(s, 0.6) for s in kern.kite.struts])
for t in throws: print(" ", t)
L.check("seven struts thrown, 1..7", [t.strut for t in throws] == list(range(1, 8)))
L.check("fixed_point_weight = 0.640000 at every one of the seven struts (cos²-complement: 1 − 0.6² = 0.64)", all(abs(t.fixed_point_weight - 0.64) < 1e-12 for t in throws), str([t.fixed_point_weight for t in throws]))
L.check("it is the same number by arithmetic: (√(1−d²))² = 1 − d² = 0.64 for d = 0.6", abs((1 - 0.6**2) - 0.64) < 1e-15)
ws = {t.strut: t.a_matrix_basin_windspeed for t in throws}; print("windspeed by strut:", ws)
L.check("windspeed is +12 on struts 4–7 and 0 on struts 1–3 (page)", all(abs(ws[s] - 12) < 1e-9 for s in (4, 5, 6, 7)) and all(abs(ws[s]) < 1e-9 for s in (1, 2, 3)), str(ws))
gen = {s: kern.kite.lineage(s) if hasattr(kern.kite, "lineage") else None for s in range(1, 8)}
print("BoxKite lineage by strut:", gen)
has_grouping = {s: (s & 4) != 0 for s in range(1, 8)}
L.check("struts 4–7 are exactly those with the GROUPING bit (strut & 4)", [s for s, v in has_grouping.items() if v] == [4, 5, 6, 7])
L.check("so the windspeed split coincides with the GROUPING bit at this depth and Assessor (the page flags this as an OPEN correlation, one depth, one choice)", all((ws[s] > 0) == has_grouping[s] for s in range(1, 8)))
# robustness the page did not test: other depths
for dpt in (0.3, 0.9):
    w2 = {t.strut: round(t.a_matrix_basin_windspeed, 6) for t in kern.run_boxkite([(s, dpt) for s in range(1, 8)])}
    print(f"depth {dpt}: windspeed by strut {w2}")
L.check("the split persists at depths 0.3 and 0.9 (the page tested only 0.6)", all((kern.throw_fiber(s, 0.3).a_matrix_basin_windspeed > 0) == has_grouping[s] for s in range(1, 8)) and all((kern.throw_fiber(s, 0.9).a_matrix_basin_windspeed > 0) == has_grouping[s] for s in range(1, 8)))"""),
("md", """## 3 · Return to the hub between fibers is structural, not asserted
`throw_fiber()` builds `psi` fresh from `HUB_PSI` every call: no residue at the previous landing."""),
("code", """import inspect
tsrc = inspect.getsource(K.MindEyeBoxKiteKernel.throw_fiber)
L.check("psi is constructed from scratch inside throw_fiber (psi = [0.0]*SED_DIM …), never from the previous landing", "psi = [0.0] * SED_DIM" in tsrc and "self._last" not in tsrc)
a = kern.throw_fiber(5, 0.6); b = kern.throw_fiber(2, 0.6); c = kern.throw_fiber(5, 0.6)
L.check("order independence: throwing strut 5 again after strut 2 gives the identical landing (psi, windspeed, hub weight)", a.psi == c.psi and a.a_matrix_basin_windspeed == c.a_matrix_basin_windspeed)
try: kern.throw_fiber(1, 1.5); bad = False
except ValueError: bad = True
L.check("depth outside [0,1] is refused", bad)
L.check("the kernel never holds two charts at once (run_boxkite is a list comprehension of independent throws)", "for s, d in plan" in inspect.getsource(K.MindEyeBoxKiteKernel.run_boxkite))"""),
("md", """## 4 · The UFT dial is the box-kite's own σ — not `h_rb_hat`'s σ-facet table
Page: `sigma_self` here is the box-kite's native quantity, a different σ from `h_rb_hat`'s `Re(s)` coupling exponent (three sigmas — do not conflate); `h_rb_hat`'s `sigma_to_theory` facet classifier is deliberately not used."""),
("code", """src = open(os.path.join(VAPMIP, "scaled_mind_eye_boxkite_kernel_monad.py"), encoding="utf-8").read()
import re as _re
L.check("the kernel does not IMPORT or CALL h_rb_hat's sigma_to_theory facet classifier (its docstring says why: no cross-feeding of two different σ's)", _re.search(r"^\\s*(from|import)\\s+h_rb_hat", src, _re.M) is None and _re.search(r"sigma_to_theory\\(", src) is None)
L.check("the dial reads both readings off one landed instant (continuous_snapshot)", "continuous_snapshot" in tsrc)
L.check("the page's reference page exists: Ainulindale/wiki/123_sigma_rb_mass_gap_calibration.md", os.path.exists(os.path.join(PLACE, "Ainulindale", "wiki", "123_sigma_rb_mass_gap_calibration.md")))"""),
("md", """## 5 · The Aulë channel — propagated, defensive, no-op if absent
`_aule_channel(event_type, payload)` wraps `PtolemyDesktop/Aule/aule.py`'s `stream_event()` on channel `"mind_eye_boxkite"`; `hub_report()` publishes `hub_confirmed`; `throw_fiber()` publishes `fiber_thrown` per crossing. Page: 8 events (1 hub + 7 fibers) in a direct run; a second run with `_stream_event = None` still runs."""),
("code", """events.clear()
k2 = K.MindEyeBoxKiteKernel(); k2.hub_report(); k2.run_boxkite([(s, 0.6) for s in range(1, 8)])
print("captured events:", [(e[0], e[1]) for e in events])
L.check("8 events: 1 hub_confirmed + 7 fiber_thrown", len(events) == 8 and sum(e[1] == "hub_confirmed" for e in events) == 1 and sum(e[1] == "fiber_thrown" for e in events) == 7)
L.check("all on channel 'mind_eye_boxkite'", all(e[0] == "mind_eye_boxkite" for e in events))
L.check("fiber events carry strut, depth, assessor, fixed_point_weight, is_zero_divisor, a_matrix_basin_windspeed", all({"strut", "depth", "assessor", "fixed_point_weight", "is_zero_divisor", "a_matrix_basin_windspeed"} <= set(e[2]) for e in events if e[1] == "fiber_thrown"))
K._stream_event = None
k3 = K.MindEyeBoxKiteKernel(); k3.hub_report(); t3 = k3.run_boxkite([(1, 0.6), (4, 0.6)])
L.check("with the stream forced to None the kernel still runs cleanly (Aulë absent)", len(t3) == 2)
al = os.path.join(PLACE, "PtolemyDesktop", "Aule", "aule.py")
L.check("PtolemyDesktop/Aule/aule.py exists and defines stream_event", os.path.exists(al) and "def stream_event" in open(al, encoding="utf-8").read())"""),
("code", """for c in ["`monad_harness.c`'s mh_pump / mh_ingest_support were made real the same session ('the beginning of the PtolemyDesktop Event Handler'; the general bus function deliberately deferred) — not wired into this Python kernel; remains open",
          "Aule as the root of the Systems Analysis Harness; the next monad copies `_aule_channel`'s shape and swaps the channel name — the reference instance of a repeated-channel pattern"]:
    L.prose(c)"""),
]
