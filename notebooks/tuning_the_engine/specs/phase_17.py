LABEL = "17"
TITLE = "The Marx Generator Complete: J_blue, PtolEye, Σ_RB, The Operator"
DATE = "2026-06-26"
PAGE = "17_the_marx_generator_complete_j_blue_ptoleye_rb_the.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · The projection, re-implemented from the page and compared with the binary
Page/`ptol.c project()`: `x_k = Σᵢ s[i−1]·i^(−σ)·w(2πi/P_k)` with `w = sin` on J_blue shells (k = 4–7, 12–15) and `cos` elsewhere; `P = {2,3,5,…,53}`; the vector is then normalised. Re-implement it in numpy (from the page text, not the C) and compare with `ptol -r` for several prompts and all five Eyes."""),
("code", """P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
def project_py(text, sigma):
    s = np.frombuffer(text.encode("utf-8"), np.uint8).astype(float); i = np.arange(1, len(s)+1)
    x = np.array([(s * i**(-sigma) * (np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)])
    return x/np.linalg.norm(x), x
home = scratch("ph17_")
prompts = ["hello world", "the void named itself at sigma equals half", "zero divisor", "a", "Ptolemaious Holcaios Philadelphos"]
eyes = dict(R=1.0, C=.75, H=.5, O=.25, S=0.0)
worst = 0.0
for p in prompts:
    for eye, sg in eyes.items():
        v, _ = project_py(p, sg); r = ptol_raw(p, eye=eye, home=home)
        worst = max(worst, np.abs(v - np.array(r["scalars"])).max())
print(f"max |numpy projection − ptol -r| over {len(prompts)*5} (prompt, Eye) cases = {worst:.2e}")
L.check("the page's projection formula reproduces ptol -r to print precision (1e-9)", worst < 1e-9, f"worst {worst:.2e}")"""),
("md", """## 2 · σ_self is the J_red power fraction; Γ and the Eyes"""),
("code", """def sigma_self(v): 
    pr = sum(v[k]**2 for k in range(16) if not blue(k)); pb = sum(v[k]**2 for k in range(16) if blue(k)); return pr/(pr+pb)
rows = []
for p in prompts:
    for eye, sg in eyes.items():
        v, _ = project_py(p, sg); r = ptol_raw(p, eye=eye, home=home); rows.append((p, eye, sigma_self(v), r["sigma_self"]))
L.check("σ_self = P_red/(P_red+P_blue) matches the binary's reported σ_self", max(abs(a-b) for *_, a, b in rows) < 1e-8)
for p in prompts[:2]: print(f"  {p[:30]:30}", {e: round(s, 3) for q, e, s, _ in rows if q == p})
print("(observation, not a page claim) σ_self ordering across the Eyes per prompt:", {p[:12]: [round(sv[2],3) for sv in [r_ for r_ in rows if r_[0]==p]] for p in prompts})"""),
("md", """## 3 · Σ_RB — "conserved at all σ: sum(s_rb)/total_power = d* = 0.24600"
The page and the C comment claim the J_red×J_blue cross-product, summed over the 16 channels and divided by total power, is the constant d*. Compute it across prompts and Eyes."""),
("code", """partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
tab = []
for p in prompts:
    for eye, sg in eyes.items():
        v, _ = project_py(p, sg); srb = np.array([v[k]*v[partner(k)] for k in range(16)])
        tab.append((p, eye, srb.sum()/np.sum(v**2)))
vals = np.array([t[2] for t in tab])
print(f"Σ_RB/|v|² over {len(vals)} cases: min {vals.min():+.4f}  max {vals.max():+.4f}  mean {vals.mean():+.4f}   (d* = 0.24600)")
r = ptol_raw("hello world", eye="H", home=home)
L.check("Σ_RB from the binary equals v[k]·v[partner(k)]", np.allclose(r["sigma_rb"], [r["scalars"][k]*r["scalars"][partner(k)] for k in range(16)], atol=1e-8))
L.check("Σ_RB/total power = d* = 0.246 for every prompt and Eye (the 'conservation')", np.all(np.abs(vals - 0.246) < 1e-3), f"range {vals.min():+.3f} … {vals.max():+.3f}")
L.check("Σ_RB/total power is the same at all five Eyes for a given prompt (invariant in σ)", all(np.ptp([t[2] for t in tab if t[0] == p]) < 1e-3 for p in prompts), "per-prompt spread across Eyes: " + str([round(float(np.ptp([t[2] for t in tab if t[0]==p])), 3) for p in prompts]))"""),
("md", """## 4 · PtolEye — the five observation points
`TOWER_EYES = {R:1.00, C:0.75, H:0.50 (θ=π/8), O:0.25, S:0.00 (θ=π/8)}`; π/8 is "the arctan(d*) half-angle = 13.82°/2". Check the number and the table in the source."""),
("code", """src = open(os.path.join(VAPMIP, "PtolC", "ptol.c")).read()
import re
tab_src = re.search(r"TOWER_EYES\\[5\\]\\s*=\\s*\\{(.*?)\\};", src, re.S)
print(tab_src.group(0)[:600] if tab_src else "TOWER_EYES table not found")
L.check("TOWER_EYES table (5 Eyes) is in ptol.c", tab_src is not None)
ang = math.degrees(math.atan(0.246)); half = ang/2
print(f"arctan(d*) = {ang:.3f}°;  half = {half:.3f}°;  π/8 = {math.degrees(math.pi/8):.3f}°")
L.check("arctan(d*) = 13.82° (page)", abs(ang - 13.82) < 0.01, f"{ang:.3f}°")
L.check("page: 'π/8 (= the arctan(d*) half-angle = 13.82°/2)'", abs(math.degrees(math.pi/8) - half) < 0.02, f"π/8 = {math.degrees(math.pi/8):.3f}°, but ½·arctan(d*) = {half:.3f}°. The two are different angles; either the π/8 is not derived from d* or the parenthesis is mis-stated")"""),
("md", """## 5 · The Operator L_a — spectrum, determinant, the ZD collapse
`L_a`: 16×16 left-multiplication matrix of the sedenion a. Claims: for a non-ZD unit `a = cosθ·e₀ + sinθ·v̂`: det = 1, Tr = 16·Re(a), eigenvalues e^{±iθ}×8. For the ZD `a=(e₁+e₁₀)/√2`: det = 0, singular values [0×4, 1×8, √2×4], eigenvalue sectors λ=0 (×4), ±i (×8), ±i√2 (×4). Compute from `cd_mul`."""),
("code", """from _sedenion import cd_mul, e
def L_mat(a): return np.array([cd_mul(list(a), list(e(j, 16))) for j in range(16)]).T      # column j = a·e_j
def R_mat(a): return np.array([cd_mul(list(e(j, 16)), list(a)) for j in range(16)]).T
rng = np.random.default_rng(8)
th = 0.7; vhat = np.zeros(16); vhat[3] = 1.0           # pure imaginary unit direction e3 (non-ZD, norm 1)
a = np.zeros(16); a[0] = math.cos(th); a += math.sin(th)*vhat
La = L_mat(a); ev = np.linalg.eigvals(La)
print(f"unit a = cos θ e0 + sin θ e3, θ={th}:  det={np.linalg.det(La):.6f}  Tr={np.trace(La):.6f}  (16·cosθ = {16*math.cos(th):.6f})")
L.check("non-ZD unit a: det(L_a) = 1", abs(np.linalg.det(La) - 1) < 1e-9)
L.check("Tr(L_a) = 16·Re(a)", abs(np.trace(La) - 16*math.cos(th)) < 1e-9)
ph = np.sort(np.angle(ev)); print("eigenvalue phases:", np.round(np.unique(np.round(ph, 6)), 4), "  |λ| range", np.round([abs(ev).min(), abs(ev).max()], 6))
L.check("eigenvalues are e^{±iθ} each with multiplicity 8", abs(abs(ev).max()-1) < 1e-9 and abs(abs(ev).min()-1) < 1e-9 and np.sum(np.abs(np.angle(ev) - th) < 1e-6) == 8 and np.sum(np.abs(np.angle(ev) + th) < 1e-6) == 8)"""),
("code", """# generic unit sedenion (not along a single imaginary unit): does the clean spectrum survive?
g = rng.normal(size=16); g /= np.linalg.norm(g)
Lg = L_mat(g); evg = np.linalg.eigvals(Lg)
print(f"generic unit sedenion: det = {np.linalg.det(Lg):.6f}, Tr = {np.trace(Lg):.6f} (16·Re = {16*g[0]:.6f}), |λ| in [{abs(evg).min():.4f}, {abs(evg).max():.4f}]")
L.check("Tr(L_a) = 16·Re(a) for ANY sedenion (page: 'ALWAYS')", abs(np.trace(Lg) - 16*g[0]) < 1e-9)
L.check("det(L_a) = 1 for a generic unit sedenion (page: 'volume preserved, not a collapse')", abs(np.linalg.det(Lg) - 1) < 1e-6, f"det = {np.linalg.det(Lg):.6f}")
# the ZD element
z = np.zeros(16); z[1] = z[10] = 1/math.sqrt(2)
Lz, Rz = L_mat(z), R_mat(z)
sv = np.sort(np.linalg.svd(Lz, compute_uv=False)); evz = np.linalg.eigvals(Lz)
print("ZD a=(e1+e10)/√2: det =", f"{np.linalg.det(Lz):.2e}", " singular values (rounded):", np.round(sv, 4))
L.check("ZD: det(L_a) = 0", abs(np.linalg.det(Lz)) < 1e-9)
L.check("ZD singular values = [0×4, 1×8, √2×4]", np.allclose(sv, sorted([0]*4 + [1]*8 + [math.sqrt(2)]*4), atol=1e-8), f"got {np.round(sv, 4)}")
mod = np.round(np.abs(evz), 6); print("ZD eigenvalue moduli (count):", {float(m): int((mod == m).sum()) for m in np.unique(mod)})
L.check("ZD eigenvalue sectors: λ=0 ×4, |λ|=1 ×8, |λ|=√2 ×4", sorted(np.round(np.abs(evz), 4)) == sorted([0]*4 + [1]*8 + [round(math.sqrt(2), 4)]*4), f"moduli {dict(zip(*np.unique(mod, return_counts=True)))}")
S = (Lz + Rz)/2; A = (Lz - Rz)/2
modS = np.round(np.abs(np.linalg.eigvals(S)), 4)
print("(L+R)/2 eigenvalue moduli (value: count):", dict(zip(*np.unique(modS, return_counts=True))), f"   ‖(L+R)/2‖_F = {np.linalg.norm(S):.4f}   ‖(L−R)/2‖_F = {np.linalg.norm(A):.4f}")
L.check("page: at the ZD only the commutator (L−R)/2 survives (the symmetric part vanishes)", np.linalg.norm(S) < 1e-9, f"‖sym‖={np.linalg.norm(S):.4f}, ‖antisym‖={np.linalg.norm(A):.4f}")
L.check("page: Σ_RB=(L_a+R_a)/2 has all eigenvalues → 0 at the ZD", np.allclose(np.linalg.eigvals(S), 0, atol=1e-6), f"max |λ| = {np.abs(np.linalg.eigvals(S)).max():.4f}")"""),
("code", """for c in ["'Three algebraic losses at the ZD crossing = three gauge forces; gravity is the null space (not quantised: no eigenvalue)' — interpretation of the spectrum; the spectrum itself is computed above",
          "The √2 in the ZD spectrum is the √2 in GAP = 1/(1000√2): the numerical coincidence is real (√2 appears); the identification is a reading",
          "Hamiltonian H = L_a as the Legendre projection of L_(I|O): Everett (tangent bundle, all paths) vs Copenhagen (cotangent, one path)",
          "VAPMIP rename (SMMIP → Virtual Action Potential Monad Information Propagation)"]:
    L.prose(c)"""),
]
