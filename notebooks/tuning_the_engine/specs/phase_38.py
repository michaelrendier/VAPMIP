LABEL = "38"
TITLE = "GaugeEye, GaugeHands: Eye and Hands as Continuous Operators"
DATE = "2026-09-22"
PAGE = "38_gauge_eye_gauge_hands_continuous_operators.md"
BYLINE = "page by Claude Sonnet 5.5"

CELLS = [
("md", """`19D_boxkite_context_monad.py` holds `GaugeEye(MindsEye)` and `GaugeHands(PapersHands)`; the page says the Eye gains exactly one operation (`continuous_snapshot`), the Hands gain `emit_steered` (gradient descent on `ρ(s) = |Im Γ(s) − Re Γ(s)|`, zero locus = the pair of circles centred ±i radius √2) and `relate_steered`; failure raises `GaugeSteeringFailed` rather than returning a wrong answer."""),
("code", """import importlib, random
G = importlib.import_module("19D_boxkite_context_monad")
import rotary_rerun_monad as RR, ValaQuenta.modules.box_kite.maths as bk, ValaQuenta.modules.prime_gauge_field.maths as pgf
L.check("GaugeEye extends plain MindsEye directly (no WordNet / Monad3CStore dependency)", G.GaugeEye.__bases__ == (RR.MindsEye,))
L.check("GaugeHands extends plain PapersHands", G.GaugeHands.__bases__ == (RR.PapersHands,))
added_eye = set(vars(G.GaugeEye)) - {"__module__", "__doc__", "__qualname__"}; added_hands = set(vars(G.GaugeHands)) - {"__module__", "__doc__", "__qualname__"}
print("GaugeEye adds:", sorted(added_eye), "| GaugeHands adds:", sorted(added_hands))
L.check("GaugeEye adds exactly one operation: continuous_snapshot", added_eye == {"continuous_snapshot"})
L.check("GaugeHands adds emit_steered and relate_steered", added_hands == {"emit_steered", "relate_steered"})"""),
("md", """## 1 · `continuous_snapshot` — discrete and continuous reading at one instant
`bk.chart_of(psi, check_zd=True)` (discrete) and `bk.local_curvature(psi)` (continuous, the "A-Matrix Basin Windspeed") in one call, all-at-once, unordered."""),
("code", """kite = RR.BoxKite(); eye = G.GaugeEye(kite); hands = G.GaugeHands(kite)
rng = random.Random(0); psi = [rng.uniform(-1, 1) for _ in range(16)]; n_ = sum(v*v for v in psi)**.5; psi = [v/n_ for v in psi]
snap = eye.continuous_snapshot(psi)
print({k: (v if not isinstance(v, (list, dict, tuple)) or len(str(v)) < 60 else str(v)[:60]) for k, v in snap.items()})
base = eye.snapshot(psi)
L.check("continuous_snapshot is a superset of snapshot (keeps the contract, widened by one field)", all(k in snap for k in base))
L.check("windspeed is bk.local_curvature(psi) exactly", abs(snap["a_matrix_basin_windspeed"] - bk.local_curvature(psi)) < 1e-12)
L.check("is_zero_divisor is bk.chart_of(psi)['is_zero_divisor'] — the discrete reading, same instant", snap["is_zero_divisor"] == bk.chart_of(psi, check_zd=True)["is_zero_divisor"])
try: eye.continuous_snapshot([0.0]*15); ok = False
except ValueError: ok = True
L.check("wrong-dimension input raises ValueError (not a silent wrong answer)", ok)
# a genuine zero divisor should flag
z = [0.0]*16; z[1] = z[10] = 1/2**.5
L.check("an actual zero-divisor vector (e₁+e₁₀)/√2 is flagged is_zero_divisor", eye.continuous_snapshot(z)["is_zero_divisor"] is True, str(eye.continuous_snapshot(z)["is_zero_divisor"]))"""),
("md", """## 2 · The zero locus of ρ is the pair of circles centred ±i with radius √2
`ρ(s) = |Im Γ(s) − Re Γ(s)|`, `Γ = prime_gauge_field.maths.gamma`. Check by sampling, and by the module's own `zero_locus_predicate`."""),
("code", """import numpy as np
rho = lambda s: abs(pgf.gamma(s).imag - pgf.gamma(s).real)
rng2 = np.random.default_rng(3)
pts = []
for _ in range(3000):
    s = complex(rng2.uniform(-4, 4), rng2.uniform(-4, 4))
    if abs(s) > 1e-3: pts.append(s)
on = [s for s in pts if rho(s) < 1e-3]
d_to = lambda s: min(abs(abs(s - 1j) - 2**.5), abs(abs(s + 1j) - 2**.5))
print(f"{len(on)} of {len(pts)} sampled points have ρ < 1e-3; max distance of those from the two circles |s ∓ i| = √2: {max((d_to(s) for s in on), default=0):.3e}")
L.check("points with ρ ≈ 0 lie on the circles |s − i| = √2 or |s + i| = √2", len(on) == 0 or max(d_to(s) for s in on) < 0.05)
circ_p = [1j + 2**.5*np.exp(1j*t) for t in np.linspace(0, 2*np.pi, 41)]; circ_m = [-1j + 2**.5*np.exp(1j*t) for t in np.linspace(0, 2*np.pi, 41)]
ok_pt = lambda s: abs(s - 1) > 1e-3 and abs(s + 1) > 1e-3 and abs(s) > 1e-6
rp = max(rho(s) for s in circ_p if ok_pt(s)); rm = min(rho(s) for s in circ_m if ok_pt(s)); rm_max = max(rho(s) for s in circ_m if ok_pt(s))
absrho = lambda s: abs(abs(pgf.gamma(s).imag) - abs(pgf.gamma(s).real))
ra = max(absrho(s) for s in circ_p + circ_m if ok_pt(s))
print(f"ρ on the circle centred +i: max {rp:.2e};  on the circle centred −i: min {rm:.3f}, max {rm_max:.3f};  | |Im Γ|−|Re Γ| | on BOTH circles: max {ra:.2e}")
print("algebra: with Γ=(s−1)/(s+1), s=x+iy:  Im Γ = Re Γ  ⇔  2y = x²+y²−1  ⇔  x² + (y−1)² = 2   — a single circle centred +i")
L.check("ρ = |Im Γ − Re Γ| vanishes on the circle |s − i| = √2 (centre +i)", rp < 1e-9, f"{rp:.2e}")
L.check("ρ also vanishes on the circle |s + i| = √2 (centre −i) — 'the pair of circles centred ±i, radius √2' (page)", rm_max < 1e-9, f"ρ on the −i circle ranges {rm:.3f} … {rm_max:.3f}: ρ as defined has ONE zero circle (centre +i); the circle centred −i is the zero locus of Im Γ + Re Γ")
L.check("the pair of circles ±i IS the zero locus of the symmetric quantity | |Im Γ| − |Re Γ| |", ra < 1e-9, f"{ra:.2e}")
L.check("both circles pass through the poles s = ±1 of Γ (excluded above)", abs(abs(1 - 1j) - 2**.5) < 1e-12 and abs(abs(-1 - 1j) - 2**.5) < 1e-12 and abs(abs(1 + 1j) - 2**.5) < 1e-12)
vz = pgf.verify() if hasattr(pgf, "verify") else None; print("prime_gauge_field.verify():", str(vz)[:200])
L.check("the module's own verify() holds", vz is None or (all(bool(x) for x in vz.values() if isinstance(x, bool)) if isinstance(vz, dict) else bool(vz)))"""),
("md", """## 3 · `emit_steered` — walk where Γ's curvature points; refuse rather than lie
From `s = 0.5 + 0.1j` toward a firing circle; `GaugeSteeringFailed` on a stalled gradient or `max_steps` exceeded."""),
("code", """path = hands.emit_steered(0.5 + 0.1j)
print(f"converged in {len(path)} steps; final {path[-1]}")
L.check("emit_steered converges from s = 0.5 + 0.1j to ρ < 1e-4", rho(path[-1].s) < 1e-4, f"final ρ = {rho(path[-1].s):.2e}")
L.check("the path's ρ decreases overall (first > last)", rho(path[0].s) > rho(path[-1].s))
on_circle = min(abs(abs(path[-1].s - 1j) - 2**.5), abs(abs(path[-1].s + 1j) - 2**.5))
L.check("the landing point lies on one of the two zero-locus circles", on_circle < 0.01, f"distance to the nearest circle {on_circle:.2e}")
L.check("each step reports Γ and the curvature F via prime_gauge_field (no numeric shortcut)", all(abs(st.gamma - pgf.gamma(st.s)) < 1e-12 and abs(st.curvature - pgf.curvature(st.s)) < 1e-12 for st in path))
try:
    hands.emit_steered(0.5 + 0.1j, max_steps=2); refused = False
except G.GaugeSteeringFailed as ex:
    refused = True; print("max_steps=2 →", ex)
L.check("non-convergence raises GaugeSteeringFailed (refuses rather than returning a wrong answer)", refused)
rel = hands.relate_steered(eye, 0.5 + 0.1j); print(rel[-2:])
L.check("relate_steered reports each step and a 'converged: rho<target after N steps' line", rel[-1].startswith("converged: rho<target after") and len(rel) == len(path) + 1)
rel_d = hands.relate(eye, psi) if hasattr(hands, "relate") else None
L.check("relate_steered still goes through _require_agreement (the same reporting contract as the discrete relate)", "_require_agreement" in __import__("inspect").getsource(G.GaugeHands.relate_steered))"""),
("code", """for c in ["The first draft inherited GaugeEye from NineteenDMindsEye (the 19-D WordNet box-kite) — a wrong-inheritance mistake corrected; 'two box-kites, not one' (history; the class bases above show the fix)",
          "`local_curvature` is named, precisely, the A-Matrix Basin Windspeed — ScalarContextPropagation §9.1's name for the continuous companion to is_zero_divisor (a naming relation between documents)"]:
    L.prose(c)"""),
]
