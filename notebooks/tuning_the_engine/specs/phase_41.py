LABEL = "41"
TITLE = "The De Marrais Deformation Battery, and the Two Constructs Compared"
DATE = "2026-10-12"
PAGE = "41_demarrais_deformation_battery_and_the_two_constructs.md"
BYLINE = "page by Claude Sonnet 5.5"

CELLS = [
("md", """The page's numbers were computed by the scripts in `ContextPlease/claude/scratchpad/2026-10-12_demarrais_deformation_battery/` (`cdalg.py`, `part1.py … part5.py`). Here the five scripts are **re-run** (in parallel, into memory) and their outputs parsed against the page; where a number can be re-derived independently in a few lines it is, from `engines/_sedenion.cd_mul`."""),
("code", """import subprocess, re, time as _t
sd = os.path.join(PLACE, "ContextPlease", "claude", "scratchpad", "2026-10-12_demarrais_deformation_battery")
t0 = _t.time()
procs = {p: subprocess.Popen([sys.executable, os.path.join(sd, p + ".py")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=sd) for p in ("part1", "part2", "part3", "part4", "part5")}
OUT = {p: pr.communicate(timeout=800)[0] for p, pr in procs.items()}
print({p: len(o.splitlines()) for p, o in OUT.items()}, f"  wall {_t.time()-t0:.0f} s")
L.check("all five scripts ran to completion with output", all(len(o.splitlines()) > 15 for o in OUT.values()) and not any("Traceback" in o for o in OUT.values()))"""),

("md", """## 1 · The shape of the answer: three kinds of deformation
Exact (G₂ flows, 14 parameters; `exp(θ e₈)`; the finite group of order 2,688 = (ℤ/2)⁴·GL(3,2) whose 16 sign factors are the Hadamard rows) · first-order tear (everything else, rate set by the singular values √2 or 2) · algebra deformation (the doubling parameter μ)."""),
("code", """p1 = OUT["part1"]; print(p1[:1100])
L.check("baseline: 42 assessors, 84 diagonals, 336 ordered ZD pairs, each diagonal killed by 4 partners", "'assessors': 42, 'diagonals': 84, 'ordered_zd_pairs': 336" in p1 and "'kills_per_diagonal': [4]" in p1)
L.check("DM-01: all 16 Hadamard-row sign flips are automorphisms (error 0)", "all 16 Hadamard-row sign flips are automorphisms: max error 0.00e+00" in p1)
L.check("DM-02: of 65,536 diagonal sign operators exactly 16 are automorphisms (the characters)", "of 65536 diagonal sign operators, automorphisms: 16" in p1)
L.check("DM-03: 168 frame-preserving GL(4,2) maps lift, each in 16 sign ways → monomial Aut of order 2,688", "A that lift to an automorphism: 168" in p1 and "monomial Aut order 2688" in p1)
L.check("DM-04: dim Der(sedenions) = 14 (the dimension of G₂)", "dimension of Der(sedenions) = 14" in p1)
L.check("DM-04: the Der-orbit through each diagonal has tangent dimension 11, stabiliser 3", "tangent dim of the Der-orbit through each diagonal: [np.int64(11)] ; stabiliser dims [np.int64(3)]" in p1)
L.check("DM-04: no nonzero derivation keeps all 84 diagonal lines invariant", "derivations that keep ALL 84 diagonal lines invariant: 0" in p1)
L.check("DM-06: every Walsh row is uniformly transversal: response √2 against all 84 annihilators (min = mean = max)", len(re.findall(r"u=\\s*\\d+\\s+1\\.4142\\s+1\\.4142\\s+1\\.4142", p1)) == 16, "16 rows × (min, mean, max) = 1.4142")"""),
("code", """# independent re-derivation of the group order and the Hadamard-character count
from _sedenion import cd_mul, e
sign_tab = {}
for i in range(16):
    for j in range(16):
        pr_ = cd_mul(list(e(i, 16)), list(e(j, 16))); k = int(np.nonzero(pr_)[0][0]); sign_tab[(i, j)] = (k, int(round(pr_[k])))
assert all(k == i ^ j for (i, j), (k, s) in sign_tab.items())
count = 0
import itertools
# a diagonal sign operator s (s_0=1) is an automorphism iff s_i s_j = s_{i xor j}  — a character of (Z/2)^4
for bits in itertools.product((1, -1), repeat=15):
    s_ = (1,) + bits
    if all(s_[i]*s_[j] == s_[i ^ j] for i in range(16) for j in range(16)): count += 1
L.check("independent: exactly 16 diagonal sign operators are automorphisms (= the 16 characters of (ℤ/2)⁴ = the 16 Hadamard rows)", count == 16, f"{count} (searched the 2¹⁵ operators with s₀ = +1)")
L.check("(ℤ/2)⁴ · GL(3,2) = 16 · 168 = 2,688", 16*168 == 2688)
H4 = np.array([[(-1)**bin(i & j).count("1") for j in range(16)] for i in range(16)])
chars = {tuple(r) for r in H4}
L.check("those 16 characters are the rows of the 16×16 Sylvester–Hadamard matrix", count == len(chars) == 16)"""),

("md", """## 2 · Walsh and Hadamard, specifically — and the dense transform destroys the kite
Page: as sign-flip operators the Hadamard rows are automorphisms (zero deformation); as perturbation directions uniformly transversal (√2·|δ|); as the **dense transform (WHT)** the kite is destroyed (0/336 survive); and ptol.c's Γ is a Walsh coefficient: the J_red/J_blue partition *is* Hadamard row 4."""),
("code", """vecs, pairs = zd_vectors()
pr_list = list(pairs)
def dense(v):
    return list(H4 @ np.array(v)/4.0)
surv = sum(1 for (ka, kb) in pr_list if max(abs(t) for t in cd_mul(dense(vecs[ka]), dense(vecs[kb]))) < 1e-12)
print(f"WHT/4 applied to both factors: {surv}/{len(pr_list)} ordered ZD pairs still annihilate")
L.check("dense WHT keeps 0/336 ZD relations (independent recomputation)", surv == 0 and len(pr_list) == 336)
p2 = OUT["part2"]
m = re.search(r"WHT \\(dense Hadamard transform / 4\\)\\s+([\\d.]+)", p2); L.check("DM-10 script: WHT row keeps 0.000", m and float(m.group(1)) == 0.0)
m = re.search(r"random orthogonal 16x16 \\(10 draws\\), best fraction preserved: ([\\d.]+)", p2); L.check("random orthogonal maps keep 0", m and float(m.group(1)) == 0.0)
def first_val(prefix):
    for l in p2.splitlines():
        if l.strip().startswith(prefix):
            m = re.search(r"\\s(\\d\\.\\d{3})\\s+(\\d\\.\\d{3})\\s+(\\d\\.\\d{3})\\s+(\\d\\.\\d{3})\\s*$", l); return [float(x) for x in m.groups()] if m else None
for pre in ("identity", "scale x2.5", "conjugation", "swap halves", "rotate every (k,k+8) pair by 0.3"):
    fv = first_val(pre); L.check(f"DM-10 operator '{pre}…' keeps T(x)T(y) = 0 on all 336 pairs (first column 1.000)", fv is not None and fv[0] == 1.0, str(fv))
fv = first_val("swap halves"); L.check("…but the half-swap does NOT keep the mixed products T(x)·y and x·T(y) (columns 3–4 are 0.000): it is an automorphism-like relabelling, not a deformation of the kite", fv is not None and fv[1] == 0.0 and fv[2] == 0.0, str(fv))
# Γ is the Walsh coefficient chi_4 (the J_red/J_blue partition)
p3 = OUT["part3"]
diffs = [float(x) for x in re.findall(r"\\|diff\\|=([\\d.e+-]+)", p3)]
L.check("SC-01: ptol.c's printed Γ equals Σ χ₄(k) v_k²/|v|² on four prompts (|diff| ~ 1e-10)", len(diffs) == 4 and max(diffs) < 1e-9, f"|diff| = {diffs}")
chi4 = lambda k: -1 if (k >> 2) & 1 else 1
home = scratch("ph41_")
for prompt in ("neutron generation", "the cat sat on the mat"):
    r = ptol_raw(prompt, eye="H", home=home); v = np.array(r["scalars"])
    w4 = sum(chi4(k)*v[k]**2 for k in range(16))/np.sum(v**2)
    L.check(f"independent: Γ('{prompt}') from ptol -r equals the χ₄ Walsh coefficient of v² … (sign: Γ = P_red − P_blue with red = cos shells k∈{{0-3, 8-11}})", abs(r["gamma"] - w4) < 1e-8, f"Γ = {r['gamma']:+.6f}; χ₄-coefficient (bit 2 of k) = {w4:+.6f}")
L.check("the cos/sin shell partition {0-3, 8-11} | {4-7, 12-15} is exactly the sign of bit 2 of k (Hadamard row 4)", all((chi4(k) == 1) == (k in (0,1,2,3,8,9,10,11)) for k in range(16)))"""),
("md", """## 3 · The tear — first-order, transversal, exactly 2 per radian
Rotating a diagonal in its plane off the zero-divisor line: the defect `min_y ‖x(θ) y‖` grows at exactly 2.000 per radian."""),
("code", """a, b = 1, 10    # plane (e_1, e_10)
xq = lambda th: [0.0]*1 + [math.cos(th)] + [0.0]*8 + [math.sin(th)] + [0.0]*5
# all 84 diagonals as candidate annihilators
diags = [np.array(v) for v in vecs.values()]
def defect(th):
    x = np.array([0.0]*16); x[a] = math.cos(th); x[b] = math.sin(th)
    return min(np.linalg.norm(cd_mul(list(x), list(y))) for y in diags)
th0 = math.pi/4
rates = [(d, defect(th0 + d)/abs(d)) for d in (1e-4, 1e-3, 1e-2)]
print("defect/δ at θ = π/4 + δ:", [(d, round(r_, 4)) for d, r_ in rates])
L.check("the defect at the zero-divisor angle π/4 is 0 and grows linearly with slope exactly 2.000/rad", defect(th0) < 1e-12 and all(abs(r_ - 2.0) < 0.02 for d, r_ in rates), str(rates))
L.check("script CS-03: the station flow is TRANSVERSAL: rate 2.0000 per radian", len(re.findall(r"rate 2\\.0000 per radian", OUT["part3"])) >= 2)
L.check("DM-11 (script): defect is 0 at θ = 0.7854 and √2 at θ = 0 and θ = π/2", "theta=0.7854  min_y ||x y|| = 0.00000" in OUT["part2"] and "theta=0.0000  min_y ||x y|| = 1.41421" in OUT["part2"] and "theta=1.5708  min_y ||x y|| = 1.41421" in OUT["part2"])"""),

("md", """## 4 · Exact deformations: flows of derivations keep every relation (G₂)
Flow all 84 diagonals along `exp(tD)`, `D` a random derivation: `‖x(t)y(t)‖ ≤ 1e-14` over 336 relations while diagonals move up to 45°; a random orthogonal generator does not."""),
("code", """p4 = OUT["part4"]; print(p4[:900])
rows = re.findall(r"^\\s*([\\d.]+)\\s+([\\d.e+-]+)\\s+([\\d.]+)\\s+True", p4, re.M)
L.check("DM-20: flowing the whole set along a derivation keeps ‖xy‖ ≤ 1e-14 for t up to 2.5", len(rows) == 4 and all(float(r_[1]) < 1e-13 for r_ in rows), str([(r_[0], r_[1], r_[2]) for r_ in rows]))
L.check("…while the diagonals move off their lattice lines by up to ≈45°", max(float(r_[2]) for r_ in rows) > 40)
L.check("DM-21 control: a RANDOM orthogonal generator does not keep the relations (‖xy‖ ≈ 0.02–0.15)", re.search(r"t=0\\.05\\s+max \\|\\|x\\(t\\) y\\(t\\)\\|\\| = 0\\.0\\d+", p4) is not None)
L.check("DM-22: the orbit of all 84 diagonals under Der has rank 14 of 14 (stabiliser dimension 0); each chart's 12 diagonals also 14 of 14", "all 84 diagonals together: orbit rank 14 of 14  (stabiliser dimension 0)" in p4 and len(re.findall(r"orbit rank under Der = 14 of 14", p4)) == 7)
L.check("DM-23: the stabiliser of one diagonal has dim 3, moves 4 partners (rank 3)", "stabiliser of one diagonal: dim 3" in p4 and "[3]" in p4)
# independent: Der(sedenions) dimension 14 via the linear system  D(xy) = D(x)y + xD(y)
n = 16; idx = lambda i, j: i*n + j
rows_ = []
for i in range(n):
    for j in range(n):
        k, s = sign_tab[(i, j)]
        for m_ in range(n):
            row = np.zeros(n*n)
            row[idx(m_, k)] += s            # coefficient of e_m in D(e_i e_j) = s * D(e_k)  -> D[m,k]
            for r in range(n):              # D(e_i) e_j + e_i D(e_j)
                kr, sr = sign_tab[(r, j)]
                if kr == m_: row[idx(r, i)] -= sr      # D[r,i] * (e_r e_j)_m
                kr2, sr2 = sign_tab[(i, r)]
                if kr2 == m_: row[idx(r, j)] -= sr2    # D[r,j] * (e_i e_r)_m
            rows_.append(row)
A = np.array(rows_); sv = np.linalg.svd(A, compute_uv=False)
nullity = int((sv < 1e-9).sum()) + max(0, n*n - len(sv)) if A.shape[0] >= A.shape[1] else n*n - int((sv > 1e-9).sum())
print("dimension of the derivation algebra Der(𝕊) (independent null-space computation):", nullity)
L.check("independent: dim Der(sedenions) = 14 = dim G₂", nullity == 14, f"{nullity}")"""),

("md", """## 5 · Functions of the native pair `z = d₊ + i d₋` at a diagonal
Page: Joukowsky `z + c/z` (c = Ω_ZS), `z²`, `tanh(z/2)`, `1/z`, conj, `z·i` keep both lines; `exp(z)`, Möbius `(z−1)/(z+1)`, real shift keep d₊ only; imaginary shift keeps d₋ only; generic in-plane rotation `z·e^{0.3i}` keeps neither. λ = 1 alone is degenerate for `z²` and the Möbius map — first run over-reported; corrected with λ ∈ {0.3, 1, 2.5}."""),
("code", """p5 = OUT["part5"]; print(p5[:1700])
def cells(label):
    m = re.search(rf"{label}\\s+((?:\\d+/\\d+)\\s*\\|\\s*(?:\\d+/\\d+)(?:\\s+(?:\\d+/\\d+)\\s*\\|\\s*(?:\\d+/\\d+))*)", p5)
    return re.findall(r"(\\d+)/(\\d+)\\s*\\|\\s*(\\d+)/(\\d+)", m.group(1)) if m else None
both = ["Joukowsky z\\\\+c/z, c=Omega_ZS", r"z\\^2", r"tanh\\(z/2\\)", "rotate z by pi/2", "conj", r"1/z"]
for lbl in both:
    c = cells(lbl); L.check(f"keeps BOTH the d₊ and d₋ line at every λ: {lbl.replace(chr(92), '')}", c is not None and all(a_ == b_ and c_ == d_ and a_ == c_ for a_, b_, c_, d_ in c) or (c is not None and all(int(a_) == int(b_) and int(c_) == int(d_) for a_, b_, c_, d_ in c)), str(c))
c = cells(r"exp\\(z\\)"); L.check("exp(z) keeps the d₊ line, loses the d₋ line", c is not None and all(a_ == b_ and int(c_) == 0 for a_, b_, c_, d_ in c), str(c))
c = cells(r"z \\+ 0\\.3 \\(shift, real\\)"); L.check("real shift keeps d₊, loses d₋", c is not None and all(a_ == b_ and int(c_) == 0 for a_, b_, c_, d_ in c), str(c))
c = cells(r"z \\+ 0\\.3 i \\(shift, imag\\)"); L.check("imaginary shift loses d₊, keeps d₋", c is not None and all(int(a_) == 0 and c_ == d_ for a_, b_, c_, d_ in c), str(c))
c = cells(r"z \\* e\\^\\{0\\.3 i\\}"); L.check("generic in-plane rotation z·e^{0.3i} keeps neither line", c is not None and all(int(a_) == 0 and int(c_) == 0 for a_, b_, c_, d_ in c), str(c))
mo = re.search(r"Moebius \\(z-1\\)/\\(z\\+1\\)\\s+(.*)", p5).group(1)
L.check("Möbius (z−1)/(z+1): keeps d₊ and loses d₋ at λ = 0.3, 2.5; at λ = 1 it is degenerate (0/0 | 14/14) — the page's correction", "14/14 | 0/14" in mo and "0/0 | 14/14" in mo, mo.strip())"""),

("md", """## 6 · The Universal Native Space constants as the doubling parameter
Deform the top doubling `μ₄ = −c`: `c > 0` leaves the combinatorics untouched (168 plane-pairs, degree 4, within-chart) and tilts every vertex to `κ = ±1/√c`; `μ₄ = 0` collapses the kite (1,764 plane pairs); `μ₄ = ±i` gives 252 pairs, degree 6, complex slopes `(±1 ± i)/√2`; an apparent anomaly at `c = GAP` (537 pairs) was a tolerance artefact."""),
("code", """p2 = OUT["part2"]
def dm13(c, sign):
    m = re.search(rf"^   {re.escape(c)}\\s+{sign}\\s+(\\d+)\\s+(\\d+)\\s+\\[([\\d, ]+)\\]\\s+(\\d+)\\s+\\[(.*)\\]\\s*$", p2, re.M)
    return m.groups() if m else None
std = dm13("1", "-1"); print("c=1, μ₄=−1 (standard):", std)
L.check("μ₄ = −1 reproduces the standard algebra: 168 pairs, 42 planes, degree 4, within-chart 168", std[:2] == ("168", "42") and std[2] == "4" and std[3] == "168")
for c_name, c_val in (("1/2", 0.5), ("sqrt2", math.sqrt(2)), ("2", 2.0), ("e", math.e), ("pi", math.pi), ("ln10", LN10), ("Omega_ZS=d*_ln10", OMEGA_ZS), ("d*=d*_taut", D_STAR), ("d*_spec", 0.24600)):
    g = dm13(c_name, "-1")
    if g is None: L.check(f"c = {c_name.replace(chr(92), '')}: row present", False); continue
    ks = [abs(float(x)) for x in re.findall(r"-?[\\d.]+", g[4])]
    L.check(f"c = {c_name.replace(chr(92), '')} (μ₄=−c): 168 pairs, degree 4 — combinatorics untouched; κ = 1/√c = {1/math.sqrt(c_val):.4f}", g[0] == "168" and g[2] == "4" and any(abs(k - 1/math.sqrt(c_val)) < 6e-4 for k in ks), f"table κ = {ks}, 1/√c = {1/math.sqrt(c_val):.4f}")
dn, ds = dm13("d*=d*_taut", "-1"), dm13("d*_spec", "-1")
print("κ(d*) vs κ(d*_spec):", dn[4], ds[4])
L.check("the 0.24631 vs 0.24600 difference between d* and d*_spec shows up as κ = 2.0149 vs 2.0162 (page)", "2.0149" in dn[4] and "2.0162" in ds[4])
L.check("independent: 1/√0.24631 = 2.0149 and 1/√0.24600 = 2.0162", abs(1/math.sqrt(D_STAR) - 2.0149) < 1e-3 and abs(1/math.sqrt(0.246) - 2.0162) < 1e-3, f"{1/math.sqrt(D_STAR):.4f}, {1/math.sqrt(0.246):.4f}")
z0 = re.search(r"^   0\\s+\\+1\\s+(\\d+)", p2, re.M).group(1)
L.check("μ₄ = 0 collapses the kite: 1,764 plane pairs", z0 == "1764", z0)
L.check("μ₄ = ±i: 252 pairs, degree 6, complex slopes (±1±i)/√2", len(re.findall(r"^   i\\s+[+-]1\\s+252\\s+42\\s+\\[6\\]", p2, re.M)) == 2 and "0.7071-0.7071j" in p2)
L.check("c = GAP row: 168 pairs at the working tolerance; the 537-pair anomaly appears only in DM-14 (all four levels deformed) and is the page's tolerance artefact", dm13("GAP", "-1")[0] == "168" and "GAP                pairs=537" in p2, "a tolerance of 1e-14 removes it (page); not re-run at that tolerance here")
L.prose("A near-miss: with θ = c rad as an in-plane rotation, the defect vanishes at π/4 + nπ/2; ln 10 rad lands 3.1° from 3π/4 (defect 0.107, smallest of the set); with 13 constants and a 90° period ≈ 60 % chance that some constant is within 3° — 'recorded, not chased'")
a_ = math.log(10) % (math.pi/2); L.check("ln 10 rad is within 0.06 rad of 3π/4 mod π/2 (a near-miss, as the page says)", abs(math.log(10) - 3*math.pi/4) < 0.06, f"ln 10 − 3π/4 = {math.log(10) - 3*math.pi/4:+.4f} rad = {math.degrees(math.log(10) - 3*math.pi/4):+.2f}°")"""),

("md", """## 7 · The two constructs against the maths
**Scalar construct** (pencil hyperstring / Gamma-Radial): the paper's pencil for strut r ≤ 7 contains **no** Assessor plane; `Π(φ)` is never a zero divisor. **Scaled construct** (live address): every lens reading is exactly covariant under all 168 frame-preserving index maps; the projected address does not carry topic; the kernel's `throw_fiber` writes `psi[a], psi[b]` rather than `psi[a], psi[b+8]`."""),
("code", """L.check("CS-01: stations of pencil(r) that are Assessor planes: r = 1..8 → 0 of 7; r = 9..15 → 6 of 7", re.search(r"r=1\\.\\.8\\s*:\\s*0 of 7", p3) is not None and re.search(r"r=9\\.\\.15[^:]*:\\s*6 of 7", p3) is not None)
L.check("CS-02: Π(φ) is a zero divisor at 0 of 13 points on every pencil tested (6 pencils); smallest relative norm against the 84 diagonals = 1.0000", p3.count("zero divisor at 0 of 13 points") == 6 and p3.count("= 1.0000") >= 6)
L.check("SC-02: all four lens readings are covariant over all 168 automorphic maps (4 prompts)", len(re.findall(r"local_curvature invariant 168, outside_share 168, fixed_point_weight 168, chart_energy permutes by s->A\\(s\\): 168", p3)) == 4)
ctrl = re.findall(r"curvature AND outside_share both unchanged in (\\d+) / 300", p3)
L.check("…while random index permutations (controls) leave the readings unchanged in 0–1 of 300 cases", all(int(x) <= 1 for x in ctrl) and len(ctrl) >= 2, str(ctrl))
sc4 = re.findall(r"^   (7 chart energies.*?|15 Walsh coefficients.*?|16 raw energies.*?|16 raw \\|v_k\\|)\\s+([\\d.]+)\\s+([\\d.]+)\\s*$", p5, re.M)
print("SC-04:", sc4)
L.check("SC-04: on 16 prompts in 4 subjects the projected address separates nothing: inter/intra ≈ 0.94–0.95, 1-NN 0.06–0.19 (chance 0.25)", len(sc4) == 4 and all(0.93 < float(r_[1]) < 0.96 for r_ in sc4) and all(float(r_[2]) <= 0.19 for r_ in sc4), str(sc4))
sc3 = p3[p3.index("SC-03"):]
L.check("SC-03: as written (e_a + e_b) the nearest Assessor for strut 1 is (2,1), not (2,3); with e_{b+8} it is (2,3)", "as written e_a+e_b     dominant chart=1 (intended 1)  nearest assessor=(2, 1)" in sc3 and "Assessor e_a+e_(b+8)   dominant chart=1 (intended 1)  nearest assessor=(2, 3)" in sc3)
L.check("SC-03: strut 5 as written has dominant chart 2, not 5; with e_{b+8} the nearest Assessor is (1,4)", "dominant chart=2 (intended 5)  nearest assessor=(1, 2)" in sc3 and "nearest assessor=(1, 4)" in sc3)
L.check("SC-03: is_zero_divisor reads True only at depth exactly 1.0 (with the Assessor plane)", "depth 1.0  Assessor e_a+e_(b+8)   dominant chart=1 (intended 1)  nearest assessor=(2, 3)  is_zero_divisor=True" in sc3 and "depth 0.6  Assessor e_a+e_(b+8)   dominant chart=1 (intended 1)  nearest assessor=(2, 3)  is_zero_divisor=False" in sc3)
import scaled_mind_eye_boxkite_kernel_monad as K, inspect
ks = inspect.getsource(K.MindEyeBoxKiteKernel.throw_fiber)
L.check("the kernel's throw_fiber STILL writes psi[a], psi[b] (page: 'Not changed'; retracted as a defect 2026-10-13: span{e₀,e_a,e_b,e_s} is a closed quaternion subalgebra, a coherent object in a different domain)", "psi[a] = depth / math.sqrt(2.0)" in ks and "psi[b] = depth / math.sqrt(2.0)" in ks and "b + 8" not in ks and "psi[b+8]" not in ks)
import ValaQuenta.modules.box_kite.maths as BK
L.check("{e₀, e_a, e_b, e_{a⊕b}} is closed under multiplication (a quaternion subalgebra ℍ) for a, b ≤ 7 — the page's reading of the as-written fiber", all(abs(np.array(cd_mul(list(e(i, 16)), list(e(j, 16)))) - 0).argmax() in (0, 1, 2, 3, 4, 5, 6, 7) for i in (1, 2) for j in (1, 2, 3)) and sign_tab[(1, 2)][0] == 3 and sign_tab[(2, 4)][0] == 6)"""),
("code", """for c in ["§7 'one part of the idea at a time' is a HYPOTHESIS, not a result: a sentence-building process that fixes one part and lets related parts move would act through a chain of G₂ stabilisers (11 to place one vertex, stabiliser 3 moving its 4 partners with rank 3); whether the words' data can drive it is untested",
          "The 15 unused Walsh coefficients and the Hadamard-row structure of the tension law are the natural 16-channel readout for the oscilloscope idea — untested",
          "d*_RG ('The Stability', the renormalisation-group face) has no closed form, so it could not be tested; d* and d*_taut are the same number 0.24631; d*_ln(10) is Ω_ZS; d*_spec ≈ 0.24600 is the separately measured fifth quantity",
          "OPEN: decide whether throw_fiber should use e_{b+8} (one-token change, Cody's call); re-derive why the single-phase law holds for pencils 1–9 and not 10–15; compose a live kite from the pool's tokens and run this battery on that",
          "Addendum 2026-10-13: everything here is consolidated in docs/wiki/Boxkite-Deformation-Record-2026-10-12.md (Blackjack subgroup F₂₁, the {4:8:4} grading, bracketing and firing order, the four d* / three Lambert-W interaction)"]:
    L.prose(c)
L.check("the consolidated record exists: docs/wiki/Boxkite-Deformation-Record-2026-10-12.md", os.path.exists(os.path.join(VAPMIP, "docs", "wiki", "Boxkite-Deformation-Record-2026-10-12.md")))"""),
]
