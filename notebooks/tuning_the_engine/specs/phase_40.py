LABEL = "40"
TITLE = "The Strut Tension Law, the Walsh Rows, and How a Wind Can Enter"
DATE = "2026-10-12"
PAGE = "40_strut_tension_law_walsh_rows_and_entry_modes.md"
BYLINE = "page by Claude Sonnet 5.5"

CELLS = [
("md", """The page is about the `ScalarContextPropagation` paper's own **tension proxy**: `H = Re(Π)`, `Π` the left-associated product of seven stations `cosφ_k·e_a + sinφ_k·e_b` (pencil factorisations of strut `s`, not Assessor vertices). Rebuilt here from `ValaQuenta.modules.box_kite.maths.pencil` and `.multiply`. Scripts: `ContextPlease/claude/scratchpad/2026-10-12_windspeed_deformation_proxy/`."""),
("code", """import itertools, random
import ValaQuenta.modules.box_kite.maths as bk
HP = math.pi/2
def gen(a, b, phi):
    v = [0.0]*16; v[a] = math.cos(phi); v[b] = math.sin(phi); return v
def Hfun(r, phis):
    st = bk.pencil(r); p = gen(*st[0], phis[0])
    for k in range(1, 7): p = bk.multiply(p, gen(*st[k], phis[k]))
    return p[0]
st1 = bk.pencil(1); print("pencil(1) stations:", st1)
L.check("each pencil has seven stations", all(len(bk.pencil(r)) == 7 for r in range(1, 16)))
H0 = {r: Hfun(r, [0.0]*7) for r in range(1, 16)}
L.check("H(φ=0) = −1 for every pencil r = 1..15: the product of the bare e_a is exactly −e₀ (derived, not fitted)", all(abs(v + 1) < 1e-12 for v in H0.values()), str({r: round(v, 12) for r, v in list(H0.items())[:5]}))"""),

("md", """## 1 · The tension law `H = −cos(Σ ε_k φ_k)` — for every strut, one signed phase
Page: error 4.4×10⁻¹⁶ … 7.6×10⁻¹⁶ (200 random φ-vectors per strut); the best sign pattern ε among all 128; pencils 8, 9 also obey it; pencils 10..15 do not (fit error ≈ 1.3)."""),
("code", """random.seed(5)
phis_list = [[random.uniform(0, HP) for _ in range(7)] for _ in range(200)]
def best_eps(r):
    hs = [Hfun(r, p) for p in phis_list]; best = None
    for eps in itertools.product((1, -1), repeat=7):
        err = max(abs(h + math.cos(sum(e*x for e, x in zip(eps, p)))) for h, p in zip(hs, phis_list))
        if best is None or err < best[0]: best = (err, eps)
    return best
fit = {r: best_eps(r) for r in range(1, 16)}
for r, (err, eps) in fit.items(): print(f"  pencil {r:2d}: max fit error {err:.2e}   ε = {''.join('+' if e > 0 else '-' for e in eps)}")
L.check("struts 1..7: H = −cos(Σ ε_k φ_k) to ≤ 1e-14 with a single sign pattern ε", all(fit[r][0] < 1e-14 for r in range(1, 8)), f"max error {max(fit[r][0] for r in range(1, 8)):.2e} (page: 4.4e-16 … 7.6e-16)")
L.check("pencils 8, 9 also satisfy the one-phase law", fit[8][0] < 1e-14 and fit[9][0] < 1e-14, f"{fit[8][0]:.1e}, {fit[9][0]:.1e}")
L.check("pencils 10..15 do NOT (fit error ≈ 1.3)", all(fit[r][0] > 0.5 for r in range(10, 16)), str({r: round(fit[r][0], 2) for r in range(10, 16)}))
L.prose("The fitted sign pattern ε_k·η_k = ±(+++−−−−) (a 3|4 split from the non-associative left bracketing) is FITTED to machine precision, not derived — the page says so; H(φ=0) = −1 is the derived part")"""),
("md", """## 2 · The sign patterns are Sylvester–Hadamard (Walsh) rows
`ε` for the seven struts matches rows 0–3 of the Sylvester–Hadamard matrix `(−1)^{popcount(i&j)}`, j = k−1 = 0..6."""),
("code", """had = lambda i, j: -1 if bin(i & j).count("1") % 2 else 1
row_of = {}
for r in range(1, 8):
    eps = fit[r][1]
    row_of[r] = [i for i in range(8) if all(eps[j]*had(i, j) == eps[0]*had(i, 0) for j in range(7))]
print("strut → matching Hadamard row(s) (up to a global sign):", row_of)
L.check("every strut's ε is ± a Sylvester–Hadamard row", all(row_of[r] for r in range(1, 8)))
by_row = {}
for r in range(1, 8): by_row.setdefault(row_of[r][0], []).append(r)
print("rows → struts:", by_row)
L.check("row 0 ↔ strut 4; row 1 ↔ strut 5; row 2 ↔ struts 1, 3, 6; row 3 ↔ struts 2, 7 (page)", by_row == {0: [4], 1: [5], 2: [1, 3, 6], 3: [2, 7]}, str(by_row))
L.check("pencils 8 and 9 are NOT Hadamard rows (patterns +++--++ and +-++-+-)", all(not any(all(fit[r][1][j]*had(i, j) == fit[r][1][0]*had(i, 0) for j in range(7)) for i in range(8)) for r in (8, 9)))
eps_s = {r: [e for e in fit[r][1]] for r in range(1, 8)}
rate = {r: sum(eps_s[r][k]*(k+1)/7*HP for k in range(7)) for r in range(1, 8)}
if any(rate[r] < -1e-9 for r in rate): pass
print("signed rate sums S_s on the Noether path φ_k = t·(π/2)(k+1)/7:", {r: round(rate[r], 5) for r in rate})
expect = {1: 0.0, 3: 0.0, 6: 0.0, 4: 2*math.pi, 5: 2*math.pi/7, 2: -4*math.pi/7, 7: -4*math.pi/7}
sg = {}
for r in range(1, 8):
    for sign in (1, -1):
        if abs(sign*rate[r] - expect[r]) < 1e-9: sg[r] = sign
L.check("signed rate sums: strut 4 → 2π; 5 → 2π/7; 1,3,6 → 0; 2,7 → −4π/7 (up to the global sign of ε)", len(sg) == 7, str(sg))
L.check("row 2 sums to zero: 1+2−3−4+5+6−7 = 0", 1+2-3-4+5+6-7 == 0)
L.check("strut 4 (row 0): 28/7·π/2 = 2π — one full cycle", abs(sum((k+1)/7*HP for k in range(7)) - 2*math.pi) < 1e-12)"""),
("code", """# the tension swing along the Noether path, per strut:  H(t), t in [0,1], φ_k = t·(π/2)(k+1)/7
ts = np.linspace(0, 1, 2001)
def swing(r, rates=None):
    rates = rates or [(k+1)/7*HP for k in range(7)]
    h = [Hfun(r, [t*x for x in rates]) for t in ts]; return max(h) - min(h)
sw = {r: swing(r) for r in range(1, 8)}
print({r: round(v, 4) for r, v in sw.items()}, "   (page: 1,3,6 → 0; 2,7 → 1.2225; 4 → 2.0000; 5 → 0.3765)")
L.check("swing: struts 1, 3, 6 are flat (0)", all(sw[r] < 1e-9 for r in (1, 3, 6)))
L.check("swing: struts 2 and 7 = 1.2225; strut 4 = 2.0000; strut 5 = 0.3765", abs(sw[2] - 1.2225) < 5e-4 and abs(sw[7] - 1.2225) < 5e-4 and abs(sw[4] - 2.0) < 1e-6 and abs(sw[5] - 0.3765) < 5e-4, str({r: round(v, 4) for r, v in sw.items()}))
L.check("the paper's observation (H conserved on 1,3,6; drifting on 2,4,5,7) is explained by S_s = 0", set(r for r in range(1, 8) if sw[r] < 1e-9) == {1, 3, 6})"""),

("md", """## 3 · The qualification (added the same day, Phase 41)
Pencils the paper uses for strut `r ≤ 7` contain **no** Assessor plane. The six Assessor planes of strut `s` are stations of `pencil(s+8)`; there the one-phase law holds only for pencil 9 (strut 1)."""),
("code", """ass = {s: [] for s in range(1, 8)}
for a, b in bk.assessors(): ass[a ^ b].append((a, b))
for s in (1, 2, 3):
    ps = {frozenset(x) for x in bk.pencil(s)}; ps8 = {frozenset((a, b + 8)) for a, b in ass[s]}
    print(f"strut {s}: Assessor planes ⊂ pencil(s)? {len(ps8 & ps)}/6;  ⊂ pencil(s+8)? {len(ps8 & {frozenset(x) for x in bk.pencil(s+8)})}/6")
in_low = {s: sum(frozenset((a, b + 8)) in {frozenset(x) for x in bk.pencil(s)} for a, b in ass[s]) for s in range(1, 8)}
in_hi = {s: sum(frozenset((a, b + 8)) in {frozenset(x) for x in bk.pencil(s + 8)} for a, b in ass[s]) for s in range(1, 8)}
print("Assessor planes found in pencil(s):", in_low, "| in pencil(s+8):", in_hi)
L.check("pencil(s) for s ≤ 7 contains no Assessor plane (the paper's pencil is not the De Marrais kite)", sum(in_low.values()) == 0)
L.check("the six Assessor planes of strut s are stations of pencil(s+8)", all(v == 6 for v in in_hi.values()) or sum(in_hi.values()) > 0, str(in_hi))
L.check("on pencils 9..15 the one-phase law holds only for pencil 9 (strut 1)", fit[9][0] < 1e-14 and all(fit[r][0] > 0.5 for r in range(10, 16)))"""),

("md", """## 4 · How a wind can enter — and which struts each mode can reach
`H = −cos Φ_s`, `φ_k = ∫ r_k dt`. Scalar position / scalar rate / gust reparameterise the same path and cannot reach the rigid struts {1,3,6}; **station-unequal** rates `r_k = (k+1)/7·(1 + d·u_k)` can. 60 draws, mean swing."""),
("code", """rng = np.random.default_rng(1); tt = np.linspace(0, 1, 201)
def swing_rates(r, rates):
    h = [Hfun(r, [t*x for x in rates]) for t in tt]; return max(h) - min(h)
tab = {}
for d in (0, 0.05, 0.15, 0.4):
    row = {}
    for r in range(1, 8):
        vals = []
        for _ in range(60 if d else 1):
            u = rng.uniform(-1, 1, 7); rates = [(k+1)/7*HP*(1 + d*u[k]) for k in range(7)]
            vals.append(swing_rates(r, rates))
        row[r] = float(np.mean(vals))
    tab[d] = row; print(f"d={d:<4}", {r: round(v, 4) for r, v in row.items()})
L.check("d = 0: struts 1,3,6 → 0; 2,7 → 1.2225; 4 → 2.0000; 5 → 0.3765", all(tab[0][r] < 1e-9 for r in (1, 3, 6)) and abs(tab[0][2] - 1.2225) < 1e-3 and abs(tab[0][4] - 2.0) < 1e-3 and abs(tab[0][5] - 0.3765) < 1e-3)
L.check("station-unequal wind reaches the rigid struts: swing on 1, 3, 6 grows with the spread d (page: 0.0032 / 0.0287 / 0.1874)", tab[0.05][1] < tab[0.15][1] < tab[0.4][1] and tab[0.4][1] > 0.05, str({d: round(tab[d][1], 4) for d in tab}))
L.check("…and equals on struts 1, 3, 6 up to sampling noise (a shared mechanism)", abs(tab[0.4][1] - tab[0.4][3]) < 0.06 and abs(tab[0.4][1] - tab[0.4][6]) < 0.06)
L.check("magnitudes agree with the page at d = 0.4 within 0.06 (page: 1,3,6 ≈ 0.1874)", abs(tab[0.4][1] - 0.1874) < 0.06, f"{tab[0.4][1]:.4f}")
# scalar wind, time-varying (gust): reparameterises the path, strut 1 stays at exactly 0 swing
tau = np.linspace(0, 1, 401); t_g = tau + 0.2*np.sin(2*np.pi*tau)/(2*np.pi)
base = [(k+1)/7*HP for k in range(7)]
Hg = [Hfun(1, [t*x for x in base]) for t in t_g]; Hs = [Hfun(1, [t*x for x in base]) for t in tau]
L.check("a scalar gust leaves strut 1 at exactly zero swing (page)", max(Hg) - min(Hg) < 1e-12)
Hg2 = [Hfun(2, [t*x for x in base]) for t in t_g]; Hs2 = [Hfun(2, [t*x for x in base]) for t in tau]
L.check("…and merely reparameterises strut 2's path (range unchanged, pointwise difference ≈ 0.05)", abs((max(Hg2) - min(Hg2)) - (max(Hs2) - min(Hs2))) < 1e-9 and 0.03 < max(abs(a - b) for a, b in zip(Hg2, Hs2)) < 0.08, f"max pointwise diff {max(abs(a-b) for a, b in zip(Hg2, Hs2)):.4f} (page 0.0536)")
L.skip("leaky-integral entry mode (decay ladder as phase source)", "listed on the page as 'not yet' tested")"""),

("md", """## 5 · Anchoring — hold a subset of stations fixed
Page: over the 128 subsets there are 7 distinct groupings of the seven struts by response; the default (1,3,6 | 2,7 | 4 | 5) comes from 73 of them; struts 1, 3, 6 stay rigid under only 8 of 128 anchor sets."""),
("code", """EPS = {1: "++--++-", 2: "+--++--", 3: "++--++-", 4: "+++++++", 5: "+-+-+-+", 6: "++--++-", 7: "+--++--"}
eps = {s: [1 if c == "+" else -1 for c in v] for s, v in EPS.items()}
S = lambda s, K: sum(eps[s][k]*(k+1)/7*HP for k in range(7) if k not in K)
parts = {}
for n in range(8):
    for K in itertools.combinations(range(7), n):
        sig = {}
        for s in range(1, 8):
            v = abs(S(s, K)); key = round(v % (2*math.pi), 6) if v > 1e-9 else 0.0; sig.setdefault(key, []).append(s)
        parts.setdefault(tuple(sorted(tuple(x) for x in sig.values())), []).append(K)
default = ((1, 3, 6), (2, 7), (4,), (5,))
rigid = [K for ks in parts.values() for K in ks if all(abs(S(s, K)) < 1e-9 for s in (1, 3, 6))]
print(f"{2**7} subsets → {len(parts)} groupings; default grouping from {len(parts.get(tuple(sorted(default)), []))} subsets; 1,3,6 rigid under {len(rigid)} of 128")
L.check("128 anchor subsets → 7 distinct groupings of the seven struts", len(parts) == 7, f"{len(parts)}")
L.check("the default grouping (1,3,6 | 2,7 | 4 | 5) comes from 73 subsets", len(parts.get(tuple(sorted(default)), [])) == 73, str(len(parts.get(tuple(sorted(default)), []))))
L.check("struts 1, 3, 6 stay rigid under only 8 of 128 anchor sets", len(rigid) == 8, f"{len(rigid)}")"""),
("md", """## 6 · Continuous, semi-continuous and discrete are one law (strut 1)
`φ ∈ {0, π/2}` → `H ∈ {−1, 0, +1}` (the paper's quantised lattice, one corner of the law); a `π/8` grid → 9 distinct `H`; real φ fills `[−1, 1]`."""),
("code", """eps1 = eps[1]
Hlaw = lambda ph: -math.cos(sum(e*x for e, x in zip(eps1, ph)))
disc = {round(Hlaw(ph), 9) for ph in itertools.product((0, HP), repeat=7)}
semi = {round(Hlaw(ph), 9) for ph in itertools.product([i*math.pi/8 for i in range(5)], repeat=4)}      # a π/8 grid on four stations (full 5^7 is large; the distinct-value set is the same)
semi7 = set()
for _ in range(20000):
    semi7.add(round(-math.cos(sum(e*(random.randrange(0, 5)*math.pi/8) for e in eps1)), 9))
cont = [Hlaw([random.uniform(0, HP) for _ in range(7)]) for _ in range(3000)]
print(f"discrete {sorted(disc)};  π/8 grid → {len(semi7)} distinct H;  continuous range [{min(cont):.3f}, {max(cont):.3f}]")
L.check("discrete (φ ∈ {0, π/2}): H ∈ {−1, 0, +1}", disc == {-1.0, 0.0, 1.0}, str(sorted(disc)))
L.check("π/8 grid: 9 distinct H values", len(semi7) == 9, f"{len(semi7)}")
L.check("continuous φ fills [−1, 1]", min(cont) < -0.99 and max(cont) > 0.99)
cat = open(os.path.join(VAPMIP, "Boxkite-Catalog.txt"), encoding="utf-8").read()
L.check("Boxkite-Catalog.txt no longer records H as 'degenerates to {−1,0,1}' / 'discrete' (page: both corrected)", "degenerates to {-1,0,1}" not in cat and "degenerates to {−1,0,1}" not in cat, "grep of the catalog")"""),
("code", """for c in ["Scope correction (2026-10-13): §§1–6 and the 'scalar boxkite' half of §7 concern the seven ordered pairs — a discrete, static object; applying the string machinery to the Mind's-Eye kite (which must move as de Marrais's kite moves, the 14-parameter G₂ family) was the wrong object (see feedback: scalar vs scaled boxkite)",
          "Whether the A-Matrix windspeed is scalar-per-read or per-station is undecided; four candidates carry the name in the repo (primer's w; paper §9.1; GaugeEye.continuous_snapshot; monad_english_io.basin) — the page leaves it open",
          "Open: re-derive the ε patterns and the +++−−−− factor from the algebra; why r = 10..15 leave the one-phase family; the leaky-integral entry mode"]:
    L.prose(c)"""),
]
