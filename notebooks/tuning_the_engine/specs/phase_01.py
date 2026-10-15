LABEL = "1"
TITLE = "The Foundation — Prime Directive, Rotations, Instrumentation"
DATE = "2026-05-31"
PAGE = "01_foundation_the_engine.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · The constants everything else leans on
`OMEGA_ZS = W(1)` is the Lambert fixed point (`W·e^W = 1`, equivalently `x = e^{-x}`); `d* = Ω/ln 10`; `GAP = 1/(1000√2)`.
The page calls Ω "what the engine selects, not a choice". First check: it really is the fixed point."""),
("code", """from scipy.special import lambertw
w1 = float(lambertw(1).real)
L.check("Ω_ZS = W(1) = fixed point of x = e^(-x)", abs(w1-OMEGA_ZS) < 1e-15 and abs(math.exp(-OMEGA_ZS)-OMEGA_ZS) < 1e-15, f"W(1) = {w1:.15f}")
L.check("d* = Ω/ln10 = 0.24631", abs(D_STAR-0.24631) < 1e-5, f"d* = {D_STAR:.6f}")
L.check("GAP = Ω − 0.246·ln10 to <1e-3 (the page's 0.000707 is the coincidence-grade closeness, not an identity)",
        abs((OMEGA_ZS-0.246*LN10)-GAP) < 1e-3, f"Ω − 0.246·ln10 = {OMEGA_ZS-0.246*LN10:.6f}  vs GAP = {GAP:.6f}")
print(f"Ω = {OMEGA_ZS:.12f}   d* = {D_STAR:.6f}   GAP = {GAP:.9f}")"""),

("md", """## 2 · External validation 1 — "Gnarl IS the discrete RedBlue Hamiltonian; fixed point at α=3 is y≈0.5671"
The page (and `engines/e02_gnarl_validator.py`) state the fixed-point condition `y + tan(3y) = 0 ⇒ y ≈ 0.5671`.
Test the statement itself before testing the engine: is `y = Ω` a root of that equation, and where are the real roots?"""),
("code", """from scipy.optimize import brentq
f = lambda y: y + math.tan(3*y)
print(f"f(Ω) = Ω + tan(3Ω) = {f(OMEGA_ZS):+.4f}   (a fixed point needs 0)")
# Gnarl: x' = x − h·sin(y+tan(αy)),  y' = y + h·sin(x+tan(αx)).  Equilibrium needs sin(y+tan αy)=0 and sin(x+tan αx)=0,
# i.e. y+tan(αy) = kπ for integer k.  Enumerate the roots on (0, π/(2α)) branches.
alpha = 3.0
roots = []
for k in range(-4, 5):
    g = lambda y, k=k: y + math.tan(alpha*y) - k*math.pi
    # tan has poles at (m+1/2)π/α: bracket between poles
    for m in range(0, 6):
        a, b = (m-0.5)*math.pi/alpha + 1e-6, (m+0.5)*math.pi/alpha - 1e-6
        if a > 0 and g(a)*g(b) < 0:
            roots.append((k, brentq(g, a, b)))
print("real roots y>0 of  y + tan(3y) = kπ  (k, y):")
for k, y in roots[:12]: print(f"   k={k:+d}  y={y:.5f}")
near = min(roots, key=lambda r: abs(r[1]-OMEGA_ZS))
L.check("y=Ω solves y+tan(3y)=0 (the page / e02 docstring statement)", abs(f(OMEGA_ZS)) < 1e-6,
        f"f(Ω) = {f(OMEGA_ZS):+.4f}; nearest root to Ω is y={near[1]:.5f} (k={near[0]}), not Ω")"""),
("code", """import e02_gnarl_validator as e02
import random
random.seed(1)
res = e02.verify_fixed_point(n_starts=40, verbose=False)
print(f"e02.verify_fixed_point: mean |r−Ω| = {res['mean_dist']:.4f}, converged within {e02.CONVERGENCE_THRESHOLD}: {res['pct_converged']*100:.0f}%")
# what does the orbit actually do?
for x0, y0 in [(0.3, 0.2), (0.5, 0.5), (-0.4, 0.7)]:
    x, y, r = e02.gnarl_iterate(x0, y0)
    print(f"   start ({x0:+.1f},{y0:+.1f}) -> ({x:+.4f},{y:+.4f})  |z|={r:.4f}")
L.check("Gnarl orbits converge to |z| ≈ Ω from random starts (e02)", res['pct_converged'] > 0.5,
        f"{res['pct_converged']*100:.0f}% within 0.05; mean distance {res['mean_dist']:.3f}")"""),
("md", """**Result recorded, not smoothed over:** the stated fixed-point equation is not satisfied by Ω, and the engine's own validator does not converge to it.
That is a chase-it item for Phase 1's *external validation 1* (code or maths? — the Gnarl family may hit Ω through a different reading, e.g. the mean of the orbit, or a different α/h). It is logged here as FAIL and left in the code."""),

("md", """## 3 · External validation 4 — Hermite H₁₆ zeros calibrate the 16 timing lobes
`np.polynomial.hermite.hermroots([0]*16+[1])` gives the 16 real zeros; `e_k = zero_k²`."""),
("code", """import e03_hermite_cam as e03
z = np.polynomial.hermite.hermroots([0]*16 + [1])
print("H16 zeros (16):", np.round(z, 4))
L.check("H16 has exactly 16 real zeros, symmetric about 0", len(z)==16 and np.allclose(np.sort(z), -np.sort(z)[::-1]), f"{len(z)} zeros")
sq = np.sort(z**2)
L.check("squares give 8 distinct heights, each doubled (partner(k)=15−k, as vagcom.CamProfile assumes)", len(np.unique(np.round(sq, 10)))==8)
r = e03.run(verbose=False)
et = np.array(r['e_targets']); print("e03 e_targets[:4] =", np.round(et[:4], 4), " (max-normalised so the largest = Ω)")
L.check("e03 targets scale the largest lobe to Ω", abs(et.max()-OMEGA_ZS) < 1e-9, f"max = {et.max():.6f}")
print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ('zeros', 'e_targets')})"""),

("md", """## 4 · External validation 5 — Triangle Inequality Average as a similarity
`engines/e04_tia_similarity.py`: the same TIA as the page, over the prime-hash address of each word."""),
("code", """import e04_tia_similarity as e04
r4 = e04.run(verbose=False)
rel = [x['tia'] for x in r4['results'] if x['relation']=='RELATED']
dis = [x['tia'] for x in r4['results'] if x['relation']=='DISTANT']
for x in r4['results']: print(f"  {x['w1']:>10} ~ {x['w2']:<11} {x['relation']:8} tia={x['tia']:.6f}")
print(f"mean RELATED {np.mean(rel):.6f}   mean DISTANT {np.mean(dis):.6f}   spread {np.mean(rel)-np.mean(dis):+.2e}")
L.check("TIA(related) > TIA(distant) on average", np.mean(rel) > np.mean(dis), f"Δ = {np.mean(rel)-np.mean(dis):+.2e}")
L.check("separation is practically useful (Δ > 1e-3)", (np.mean(rel)-np.mean(dis)) > 1e-3, "all values sit at ≈0.477; the signal is 4+ orders below the level")"""),

("md", """## 5 · The four rotations and the Euler gate
`-h`: `cos(γ/2 + affect·π/2)`; `-W`: `cos(γ/2 − π/2) = +sin(γ/2)`; `-O`: `|sin(γ/2)·cos(γ/2)|`; conservation `sin²+cos² = 1` and the 8-fold sum `Σ cos(γ/2 + kπ/4) = 0`.
γ are real Riemann-zero ordinates, computed here with `mpmath.zetazero`."""),
("code", """import mpmath as mp
gam = [float(mp.zetazero(n).imag) for n in range(1, 9)]
print("γ₁..γ₈ =", np.round(gam, 4))
gate_h = lambda g, affect=0.0: math.cos(g/2 + affect*math.pi/2)
gate_W = lambda g: math.cos(g/2 - math.pi/2)
gate_O = lambda g: abs(math.sin(g/2)*math.cos(g/2))
print(f"{'γ':>9} {'-h':>8} {'-W':>8} {'-O':>8}   sin²+cos²")
for g in gam: print(f"{g:9.4f} {gate_h(g):8.4f} {gate_W(g):8.4f} {gate_O(g):8.4f}   {math.sin(g/2)**2+math.cos(g/2)**2:.15f}")
L.check("-W gate equals +sin(γ/2) (the crest) for every zero", all(abs(gate_W(g)-math.sin(g/2)) < 1e-12 for g in gam))
L.check("affect=1 reproduces −sin(γ/2) (the trough = the Phase-3 'sin correction' bug)", all(abs(gate_h(g, 1.0)+math.sin(g/2)) < 1e-12 for g in gam))
L.check("-O = |sin γ|/2", all(abs(gate_O(g)-abs(math.sin(g))/2) < 1e-12 for g in gam))
s8 = [sum(math.cos(g/2 + k*math.pi/4) for k in range(8)) for g in gam]
L.check("8D conservation: Σ_k cos(γ/2+kπ/4) = 0 (page: −1.73e-11)", max(abs(x) for x in s8) < 1e-12, f"max |Σ| = {max(abs(x) for x in s8):.2e}")"""),

("md", """## 6 · Gravity is a push — neutral-buoyancy selection and the IQM calibration
Pull (old): `score = jp·σ-proximity`. Push (new): `buoy = 1/(1+|jp − J_ambient|·ln10)`. `J_ambient` is initialised at the interquartile mean of `jp = β·E²`.
`monad.Engine` carries `_J_ambient`; here the *rule* is exercised on a synthetic field, then the engine's own initial `_J_ambient` is read."""),
("code", """rng = np.random.default_rng(7)
jp = rng.lognormal(mean=-6, sigma=1.8, size=5000)          # heavy-tailed β·E² field
p25, p75 = np.percentile(jp, [25, 75])
iqm = jp[(jp >= p25) & (jp <= p75)].mean()
print(f"median {np.median(jp):.3e}   mean {jp.mean():.3e}   IQM {iqm:.3e}   max {jp.max():.3e}")
buoy = 1.0/(1.0 + np.abs(jp - iqm)*LN10)
pull_pick, push_pick = int(np.argmax(jp)), int(np.argmax(buoy))
print(f"pull picks jp={jp[pull_pick]:.3e} (the heaviest);  push picks jp={jp[push_pick]:.3e} (≈ J_ambient)")
L.check("pull selects the max-J word", jp[pull_pick] == jp.max())
L.check("push selects a word at neutral buoyancy (|jp−IQM| minimal)", abs(jp[push_pick]-iqm) == np.abs(jp-iqm).min())
L.check("IQM sits inside the content zone P25..P75, away from the stop-word tail", p25 <= iqm <= p75 and iqm < jp.mean())
from monad import Engine
e = Engine(); print("cold-start Engine._J_ambient =", e._J_ambient, "(= GAP; calibrated to the field on load)")
import monad as _m
L.check("Engine cold-starts _J_ambient at its GAP (= Ω − 0.246·ln10)", e._J_ambient == _m.GAP,
        f"monad.GAP = {_m.GAP:.12f} vs 1/(1000√2) = {GAP:.12f}  (differ by {abs(_m.GAP-GAP):.1e}: the 'exact' form in engines/_sedenion.py is the rounded one)")"""),

("md", """## 7 · The speaking engine itself — `monad.Engine` (v1.218), identity probe, instrumentation
Load the two seed corpora (`foundations.txt`, `meaning.txt`) into the live engine, then ask the questions the page asks:
does the identity probe speak `SELF_EQUATION`? does the OBD2 layer implement the DTC/PID tables of the page?"""),
("code", """from monad import Engine, SensorArray, SELF_EQUATION
e = Engine()
for fn in ("foundations.txt", "meaning.txt"):
    print(fn, e.load(open(os.path.join(VAPMIP, fn)).read()))
p = e.identity_probe()
print("SELF_EQUATION :", SELF_EQUATION)
print("probe response:", " ".join(p['words'][:12]))
print("equation_hits :", p['equation_hits'], " at_native_depth:", p['at_native_depth'])
L.check("identity_probe reaches native depth (≥2 SELF_EQUATION words) on the two seed corpora", p['at_native_depth'],
        f"hits = {p['equation_hits']}; the 2026-05-27 event used the long-run field, which is not in this repo state")"""),
("code", """s = SensorArray(e)
print("PIDs implemented in code:", [hex(k) for k in SensorArray._PID_NAMES])
page_src = page("01")
import re
page_dtcs = sorted(set(re.findall(r"P0\\d{3}", page_src)))
code_dtcs = sorted(set(re.findall(r"P0\\d{3}", open(os.path.join(VAPMIP, "monad.py")).read())))
print("DTCs named on the page:", page_dtcs)
print("DTCs coded in monad.py :", code_dtcs)
print("fault_scan() now:", s.fault_scan())
print("ready_check()   :", {k: v for k, v in s.ready_check().items()})
only_page, only_code = sorted(set(page_dtcs)-set(code_dtcs)), sorted(set(code_dtcs)-set(page_dtcs))
L.check("page DTC table == code DTC table", not only_page and not only_code,
        f"on page only: {only_page}; in code only: {only_code}")
L.check("readiness monitor count: page lists 8, code lists the same", len(s.ready_check()) == 8, f"{len(s.ready_check())} monitors (code added THREE_FACE, ANAPHOR, ONE_WIRE)")
print(s.torque_csv().splitlines()[0:6])"""),
("md", """**Reading:** the instrumentation layer exists and runs (PID reads, fault scan, readiness), but the DTC set and monitor count have moved on from the page — the page documents v2.0.0 of an earlier design, the code is `Engine.version == "v1.218"` with a different DTC table.
Phase 1's narrative claims (the engine analogy, Wernicke/Broca, RH = no aphasias) have no executable counterpart and are recorded as PROSE."""),
("code", """for c in ["Diesel/TDI ⇄ monad component mapping (camshaft=sedenion, crankshaft=H_hat_RB, ECU=monad)",
          "Wernicke/Broca = J_neg/J_pos; RH = 'no aphasias'",
          "DTC codes as a Gödelian constructive consistency demonstration",
          "'holcus' as the deepest word / Ptolemaious Holcaios Philadelphos"]:
    L.prose(c)"""),
]
