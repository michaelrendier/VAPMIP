LABEL = "30"
TITLE = "Wind, Lift, and the Monad's Original Gate"
DATE = "2026-08-23"
PAGE = "30_wind_lift_and_the_monads_original_gate.md"
BYLINE = "page by Claude Opus 5 (+ Sonnet 5)"

CELLS = [
("md", """The page's engine is `engine/lineage.py` (then `SedenionFactoralRelativity/`, now the **GenerationalLineage** repo, v1.0.0). Run its own self-check, then re-derive each section independently. Sections the page itself labels design specification (§9, §10 for N>3, §11) are `PROSE`."""),
("code", """sys.path.insert(0, os.path.join(PLACE, "GenerationalLineage"))
from engine import lineage as GL
r = GL.run(verbose=False)
print({k: (v if not isinstance(v, (list, dict)) else f"<{type(v).__name__} {len(v)}>") for k, v in r.items()})
held = r.get("held", r.get("n_hold")); tot = r.get("total", r.get("n_total"))
L.check("GenerationalLineage lineage.run(): every self-checked relation holds (page: 40/40 at PW12)", r.get("all_hold", held == tot), f"{held}/{tot} now (the page's 40 has grown)")"""),

("md", """## 1 · PW10 — the two-ring chart (Smith/Möbius fold) and its four invariants
`Γ = (Z − Z₀)/(Z + Z₀)`. Invariants claimed: fixed point, boundary, conformal orthogonality, the inversion π-rotation — for *any* ring pair and any (including complex) anchor, checked against Ω(n) and φ(n)/n."""),
("code", """G = lambda Z, Z0: (Z - Z0)/(Z + Z0)
rng = np.random.default_rng(2)
Z0s = [1.0, 2.5+0j, 0.3+0.9j, -1.2+0.4j]
ok_fp = all(abs(G(Z0, Z0)) < 1e-15 for Z0 in Z0s)
L.check("fixed point: Γ(Z₀) = 0 for real and complex anchors", ok_fp)
L.check("boundary: |Γ| = 1 on the imaginary axis for a real positive anchor (reactive loads sit on the unit circle)", all(abs(abs(G(1j*y, 2.0)) - 1) < 1e-12 for y in rng.normal(size=50)))
L.check("inversion = π-rotation: Γ(Z₀²/Z) = −Γ(Z)", all(abs(G(Z0**2/Z, Z0) + G(Z, Z0)) < 1e-12 for Z0 in Z0s for Z in rng.normal(size=5)+1j*rng.normal(size=5)))
def angle_between(f, z, dz1, dz2, h=1e-6):
    d1 = (f(z + h*dz1) - f(z))/h; d2 = (f(z + h*dz2) - f(z))/h
    return np.angle(d2/d1) - np.angle(dz2/dz1)
L.check("conformal: Γ preserves angles (orthogonal grid lines map to orthogonal circles)", all(abs((angle_between(lambda z: G(z, Z0), 0.7+0.5j, 1, 1j) + np.pi) % (2*np.pi) - np.pi) < 1e-3 for Z0 in Z0s))
L.check("the module's ring_chart_gamma agrees with the Möbius form", all(abs(GL.ring_chart_gamma(Z, Z0) - G(Z, Z0)) < 1e-12 for Z0 in Z0s for Z in (0.3+0.2j, 1.4-0.7j)))
# applied to arithmetic: ring pair (Ω(n), φ(n)/n) — unrelated to impedance
from sympy import totient, primefactors, factorint
Om = lambda n: sum(factorint(n).values())
vals = [G(complex(Om(n)), complex(float(totient(n))/n)) for n in range(2, 60)]
L.check("fold applied to (Ω(n), φ(n)/n) stays finite and |Γ| ≤ 1 for positive real ring values", all(abs(v) <= 1 + 1e-12 for v in vals))"""),

("md", """## 2 · PW11 / PW12 — the crystal (period from repeat-autocorrelation) and the join (permutation order)
Recover a hidden Vigenère key length blind for k = 5, 7, 11, 13; composite periods ambiguous against their divisors (a real Kasiski limitation). `permutation_order_via_stems` = lcm of cycle lengths, 400/400 random permutations."""),
("code", """import random, inspect
word = [7, 4, 17, 2, 19, 8]                        # the control's fixed, internally non-repeating motif (engine/lineage.py PW11)
def control(true_k, rng):
    key = [(3*i + 1) % 26 for i in range(true_k)]; plain = []
    for _ in range(40):
        plain += [rng.randrange(26) for _ in range(rng.randint(5, 15))] + word
    return GL.vigenere_cipher(plain, key, alphabet=26)
def recovered(true_k, rng):
    return GL.infer_period_by_stem_vote(GL.repeat_distances(control(true_k, rng), n=4), max_period=20)["best_period"]
rng0 = random.Random(20260823); first = {k: recovered(k, rng0) for k in (5, 7, 11, 13)}
print("the engine's own seed (20260823):", first)
L.check("the page's control: exact recovery of the hidden key length for k = 5, 7, 11, 13", first == {5: 5, 7: 7, 11: 11, 13: 13}, str(first))
rate = {k: np.mean([recovered(k, random.Random(1000 + s)) == k for s in range(40)]) for k in (5, 7, 11, 13)}
print("recovery rate over 40 other seeds per prime period:", {k: f"{v:.0%}" for k, v in rate.items()})
L.check("…and robustly: ≥ 90 % recovery over 40 fresh seeds for every prime period", all(v >= 0.9 for v in rate.values()), str({k: round(float(v), 2) for k, v in rate.items()}))
"""),
("code", """random.seed(5)
comp = {}
for k in (6, 10, 12):
    outs = []
    for _ in range(5):
        o = GL.infer_period_by_stem_vote(GL.repeat_distances(control(k, random.Random(50 + _)), n=4), max_period=20); outs.append(o.get("best_period"))
    comp[k] = outs
print("composite periods → inferred:", comp)
L.check("composite periods are genuinely ambiguous against their divisors (the page's honest limit): inferred period is sometimes a proper divisor", any(any(v is not None and v != k and k % v == 0 for v in vs) for k, vs in comp.items()), str(comp))
# the join: permutation order = lcm of cycle lengths
from sympy.combinatorics import Permutation
random.seed(3); bad = 0
for _ in range(400):
    n = random.randrange(3, 14); perm = list(range(n)); random.shuffle(perm)
    lcm_cycles = math.lcm(*[len(c) for c in Permutation(perm).full_cyclic_form]) if n else 1
    bad += GL.permutation_order_via_stems(perm) != lcm_cycles
L.check("permutation order via stems agrees with lcm(cycle lengths) for 400/400 random permutations", bad == 0, f"{400-bad}/400")"""),

("md", """## 3 · Tension is shape, not mass — and the corpus has no mass to find
Page: `|v|² = 1.0000` exactly for all 3,288 addresses in `monad_sedenion_addresses.pkl`."""),
("code", """import pickle
book = pickle.load(open(os.path.join(VAPMIP, "monad_sedenion_addresses.pkl"), "rb"))["book"]
V = np.array([ent["sedenion"] for ent in book.values() if len(ent["sedenion"]) == 16])
print(V.shape, "  |v|² range:", float((V**2).sum(1).min()), float((V**2).sum(1).max()))
L.check("3,288 addresses", len(V) == 3288)
L.check("|v|² = 1.0000 for every address (unit-normalised upstream: no absolute scale survives)", np.allclose((V**2).sum(1), 1.0, atol=1e-4), f"|v|² ∈ [{(V**2).sum(1).min():.6f}, {(V**2).sum(1).max():.6f}]")"""),

("md", """## 4 · The Hamiltonian split — inertia + kinetic — and the redundant GAP diagnostic
Raw (unnormalised) terms mirroring `H_RB = Γ^a·D_a + Γ_ij·β`: `inertia = v[0]²`, `kinetic = local_curvature(v)` (associator defect at dominant directions). Page: inertia mean 0.6435, min 0.0583, max 1.0; kinetic mean 8.3735, min 0, max 12; corr = −0.1751. And the entropy-ceiling diagnostic: `GAP = H_ceiling − H`, `H_ceiling = H_binary(tension) + tension·log₂15`, GAP = 0 on a uniform synthetic control, corr(tension, GAP) = 0.9498."""),
("code", """import ValaQuenta.modules.box_kite.maths as B
inertia = V[:, 0]**2
kin = np.array([B.local_curvature(list(v)) for v in V])
cr = float(np.corrcoef(inertia, kin)[0, 1])
print(f"inertia: mean {inertia.mean():.4f} min {inertia.min():.4f} max {inertia.max():.4f}")
print(f"kinetic: mean {kin.mean():.4f} min {kin.min():.4f} max {kin.max():.4f}      corr(inertia, kinetic) = {cr:+.4f}")
L.check("inertia mean 0.6435, min 0.0583, max 1.0000", abs(inertia.mean() - 0.6435) < 5e-4 and abs(inertia.min() - 0.0583) < 5e-4 and abs(inertia.max() - 1) < 1e-4)
L.check("kinetic mean 8.3735, min 0, max 12", abs(kin.mean() - 8.3735) < 0.01 and kin.min() == 0 and abs(kin.max() - 12) < 1e-6, f"{kin.mean():.4f}, {kin.min()}, {kin.max()}")
L.check("corr(inertia, kinetic) = −0.1751 (weakly anti-correlated: two channels, not one)", abs(cr + 0.1751) < 0.01, f"{cr:+.4f}")
def Hb(p): return 0.0 if p <= 0 or p >= 1 else -(p*math.log2(p) + (1-p)*math.log2(1-p))
P = V**2; t = 1 - P[:, 0]
H = -(np.where(P > 0, P*np.log2(np.where(P > 0, P, 1)), 0)).sum(1)
ceil = np.array([Hb(x) + x*math.log2(15) for x in t]); GAP_ = ceil - H
unif = np.zeros(16); unif[0] = .6; unif[1:] = .4/15
tu = 1 - unif[0]; Hu = -(unif*np.log2(unif)).sum(); gu = Hb(tu) + tu*math.log2(15) - Hu
print(f"uniform control (e₀ = 0.6, the other 15 equal): GAP = {gu:.2e};  corpus corr(tension, GAP) = {np.corrcoef(t, GAP_)[0,1]:.4f}")
L.check("GAP = 0 exactly on a synthetic uniform control", abs(gu) < 1e-12)
L.check("GAP ≥ 0 on every corpus address (it is a ceiling)", GAP_.min() > -1e-9, f"min {GAP_.min():.2e}")
L.check("corr(tension, GAP) ≈ 0.9498 on the real corpus (the diagnostic is nearly redundant with tension)", abs(np.corrcoef(t, GAP_)[0, 1] - 0.9498) < 0.03, f"{np.corrcoef(t, GAP_)[0,1]:.4f}")"""),

("md", """## 5 · The wind is the commutator
`[e₀, ·] = 0` against all 16 basis directions; all 210 ordered pairs of distinct imaginary directions have a nonzero commutator."""),
("code", """from _sedenion import cd_mul, e
comm = lambda i, j: np.array(cd_mul(e(i,16), e(j,16))) - np.array(cd_mul(e(j,16), e(i,16)))
L.check("e₀'s commutator vanishes against all 16 basis directions", all(np.abs(comm(0, j)).max() < 1e-12 for j in range(16)))
nz = sum(1 for i in range(1, 16) for j in range(1, 16) if i != j and np.abs(comm(i, j)).max() > 1e-12)
L.check("all 210 ordered pairs i≠j among the 15 imaginary directions have a nonzero commutator", nz == 210, f"{nz}")
L.check("(i,i) pairs commute trivially, so the 15 diagonal pairs are the only calm ones among the imaginaries", all(np.abs(comm(i, i)).max() < 1e-12 for i in range(1, 16)))
L.check("the associator, by contrast, vanishes on e₀ identically (single point of total calm for curvature too)", all(np.abs(np.array(cd_mul(cd_mul(e(0,16), e(j,16)), e(k,16))) - np.array(cd_mul(e(0,16), cd_mul(e(j,16), e(k,16))))).max() < 1e-12 for j in range(16) for k in range(16)))"""),

("md", """## 6 · Deformation is real, but the wind has to be elastic
Weighted graph Laplacian on a box-kite octahedron, edge weight = local torsion; the page's finding: using the box-kite's *own* diagonals gives the same deformed spectrum on struts 1, 2, 3 (rigid), a source from real asymmetric addresses gives different spectra (elastic). The exact edge-weight definition is not on the page; here is the cleanest reading — weight = ‖[d_A, d_B]‖ of the first diagonals of the two Assessors."""),
("code", """def vec(a, b, s):
    v = [0.0]*16; v[a] = 1.0; v[b+8] = float(s); return np.array(v)
Bmod = B
ass = Bmod.assessors(); kites = {}
for a, b in ass: kites.setdefault(a ^ b, []).append((a, b))
def lap_spectrum(strut, weight):
    nodes = kites[strut]; W = np.zeros((6, 6))
    for i in range(6):
        for j in range(i+1, 6):
            if Bmod.assessors_adjacent(nodes[i], nodes[j]): W[i, j] = W[j, i] = weight(nodes[i], nodes[j])
    return np.round(np.linalg.eigvalsh(np.diag(W.sum(1)) - W), 4)
cnorm = lambda A, Bq: float(np.linalg.norm(np.array(cd_mul(list(vec(*A, 1)), list(vec(*Bq, 1)))) - np.array(cd_mul(list(vec(*Bq, 1)), list(vec(*A, 1))))))
bare = [np.round(np.linalg.eigvalsh(np.diag(np.ones(6)*4) - np.array([[1.0 if Bmod.assessors_adjacent(kites[s][i], kites[s][j]) and i != j else 0 for j in range(6)] for i in range(6)])), 4) for s in (1, 2, 3)]
sp_struct = [lap_spectrum(s, cnorm) for s in (1, 2, 3)]
print("bare spectrum (strut 1):", bare[0]); 
for s, sp_ in zip((1, 2, 3), sp_struct): print(f"structural-wind spectrum, strut {s}:", sp_)
L.check("bare octahedron spectrum {0,4,4,4,6,6}", np.allclose(bare[0], [0, 4, 4, 4, 6, 6]))
L.check("structural wind (the kite's own diagonals): identical deformed spectra on struts 1, 2, 3 (rigid)", all(np.allclose(sp_struct[0], x) for x in sp_struct[1:]))
nz0 = int(np.sum(np.abs(sp_struct[0]) < 1e-9)); print("zero modes under the structural wind:", nz0)
rng = np.random.default_rng(4); addr = V[rng.choice(len(V), 3, replace=False)]
def elastic(addr_v):
    def w(A, Bq):          # wind from a REAL address: energy of the address on each Assessor's plane
        return float(addr_v[A[0]]**2 + addr_v[A[1]+8]**2 + addr_v[Bq[0]]**2 + addr_v[Bq[1]+8]**2)
    return w
sp_el = [lap_spectrum(1, elastic(v)) for v in addr]
for v_, sp_ in zip(range(3), sp_el): print(f"address-sourced spectrum {v_}:", sp_)
L.check("address-sourced wind gives different deformed spectra for different addresses (elastic)", not (np.allclose(sp_el[0], sp_el[1]) and np.allclose(sp_el[1], sp_el[2])))
L.prose("The page's mode-collapse detail (two zero modes instead of one; the 3-fold/2-fold split merging into one 4-fold) depends on the exact torsion weighting used in the session; the reading above reproduces rigid-vs-elastic, not the mode-collapse detail")"""),

("md", """## 7 · Lift — Kutta–Joukowski on the box-kite
`Lift = wind × circulation`; circulation = signed sum of torsion around a closed 4-cycle; all 105 four-cycles across the 7 struts: 53 positive, 31 negative, 21 zero, values at ±4, ±8, ±16, 0. The signing convention ("canonically signed by the algebra itself") is not on the page and is not in the repo; the combinatorial claims are checkable."""),
("code", """import itertools
tot = 0; contains_pair = 0; per = []
for s, nodes in sorted(kites.items()):
    adj = {(i, j) for i in range(6) for j in range(6) if i != j and Bmod.assessors_adjacent(nodes[i], nodes[j])}
    cyc = set()
    for q in itertools.permutations(range(6), 4):
        if all((q[i], q[(i+1) % 4]) in adj for i in range(4)):
            cyc.add((frozenset(q), frozenset(frozenset((q[i], q[(i+1) % 4])) for i in range(4))))
    nonadj = {frozenset((i, j)) for i in range(6) for j in range(i+1, 6) if (i, j) not in adj}
    per.append(len(cyc)); tot += len(cyc)
    contains_pair += sum(1 for vs, es in cyc if any(p <= vs for p in nonadj))
print("4-cycles per octahedron:", per, "total", tot, "; containing a full reversal pair:", contains_pair)
L.check("15 four-cycles per octahedron, 105 over the seven", per == [15]*7 and tot == 105)
L.check("every 4-cycle of an octahedron contains a full reversal (antipodal) pair — the pigeonhole the page found universal", contains_pair == tot)
L.skip("lift split 53 positive / 31 negative / 21 zero, values at ±4, ±8, ±16, 0", "the torsion sign convention for circulation is not specified on the page nor implemented in the repos (the Phase-40 tension law is the later, written-down version)")"""),

("md", """## 8 · Paper's Hands — read from `ptol.c`, not inferred"""),
("code", """src = open(os.path.join(VAPMIP, "PtolC", "ptol.c")).read()
import re as _re
L.check("ptol.c has the Mind's Eye line: ve[k] = project(…, k, sigma_self)  (cast spelling differs from the page's quote)", _re.search(r"ve\[k\]\s*=\s*project\([^;]*,\s*sigma_self\)", src) is not None)
L.check("ptol.c has the Paper's Hands line: vb[k] = project(…, k, sigma_comp) with σ_comp = 1 − σ_self", _re.search(r"vb\[k\]\s*=\s*project\([^;]*,\s*sigma_comp\)", src) is not None and "double sigma_comp = 1.0 - sigma_self" in src)
L.check("the code's own comment marks Hands non-updateable and Eye updateable", "non-updateable" in src and "updateable" in src)"""),

("md", """## 10 · Multiple anchors, one summed path (PW3)
`spiral_address(p·q) = spiral_address(p) + spiral_address(q)`, exact; three anchors (97, 41, 227) sum to `spiral_address(97·41·227)` to 1e-12; generalises to N anchors."""),
("code", """sa = GL.spiral_address
def add(*ns):
    parts = [sa(n) for n in ns]; keys = ("log_radius", "angle")
    return {k: sum(p[k] for p in parts) for k in keys}
one = sa(97*41*227); three = add(97, 41, 227)
print({k: (one[k], three[k]) for k in ("log_radius", "angle")})
L.check("three anchors (97, 41, 227): summed == spiral_address(97·41·227) to 1e-12", abs(one["log_radius"] - three["log_radius"]) < 1e-12 and abs(one["angle"] - three["angle"]) < 1e-9, f"Δlog_radius {abs(one['log_radius']-three['log_radius']):.1e}, Δangle {abs(one['angle']-three['angle']):.1e}")
ns = [3, 5, 7, 11, 13, 17, 19, 23]
L.check("N = 8 anchors: still additive", abs(sa(math.prod(ns))["log_radius"] - add(*ns)["log_radius"]) < 1e-9)"""),
("code", """for c in ["§9 Zero-lift loops carry grammar/definitional boundaries; nonzero-lift loops the relational, usage-driven layer — a design specification (the page says so), consistent with langue/parole and competence/performance",
          "§10 'three simultaneous Lagrangian terms, the actual path is their sum' for content/intent/desire — specification; only the log-additivity is checked",
          "§11 24D Leech-lattice ambient container, 0_ZD as the 16D shadow, and 'the Monad's original gate is the sign of Lift, derived not trained' (≈ Mixture-of-Experts with a derived gate) — roadmap/grounding, explicitly not computed",
          "Lift-sign as a hand-off trigger Eye→Hands: 'a strong, testable hypothesis, not yet confirmed against address-modulated wind' (page's own scope note)"]:
    L.prose(c)"""),
]
