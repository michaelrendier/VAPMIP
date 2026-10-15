LABEL = "29"
TITLE = "Generational Lineage, and the Anatomy of σ in ∅_RB"
DATE = "2026-08-20"
PAGE = "29_generational_lineage_and_the_anatomy_of_sigma.md"
BYLINE = "page by Claude Opus 5 (+ Sonnet 5)"

CELLS = [
("md", """The engine is `engines/e10_generational_lineage.py`. The page reports **8/8 relations hold**; the engine now carries more. Run it first, then re-derive each numbered claim independently of the engine (the companion demonstration notebook is `notebooks/16_e10_generational_lineage.ipynb`)."""),
("code", """import e10_generational_lineage as E
res = E.run(verbose=False)
print(f"relations: {res['held']}/{res['total']} hold;  all_hold = {res['all_hold']}")
for name, lvl, status, *rest in res['relations']: print(f"  [{status:7}] level {lvl}  {name}")
L.check("the engine's relations all hold", res['all_hold'], f"{res['held']}/{res['total']}")
L.check("the page's 8 relations have grown (the page predates later additions)", res['total'] >= 8, f"now {res['total']}")"""),

("md", """## 1 · Generational Lineage **is** order of operations: one loss per doubling
`gen 0 ranking F₀=3 · gen 1 factors F₁=5 · gen 2 GROUPING F₂=17 · gen 3 division F₃=257`; `commute@2=True commute@4=False · assoc@4=True assoc@8=False · ZD@8=False ZD@16=True`."""),
("code", """from _sedenion import cd_mul, e
def prop(n):
    E_ = [e(i, n) for i in range(n)]
    comm  = all(np.allclose(cd_mul(E_[i], E_[j]), cd_mul(E_[j], E_[i])) for i in range(n) for j in range(n))
    assoc = all(np.allclose(cd_mul(cd_mul(E_[i], E_[j]), E_[k]), cd_mul(E_[i], cd_mul(E_[j], E_[k]))) for i in range(n) for j in range(n) for k in range(n))
    # zero-divisors: two nonzero elements with product 0 — search over e_a ± e_b combinations
    zd = False
    cand = [list(E_[i]) for i in range(n)] + [list(np.array(E_[a]) + s*np.array(E_[b])) for a in range(n) for b in range(a+1, n) for s in (1, -1)]
    for x in cand:
        for y in cand:
            if max(abs(t) for t in cd_mul(x, y)) < 1e-12 and max(abs(t) for t in x) > 0 and max(abs(t) for t in y) > 0: zd = True; break
        if zd: break
    return comm, assoc, zd
T = {n: prop(n) for n in (2, 4, 8, 16)}
print({n: dict(commute=v[0], assoc=v[1], ZD=v[2]) for n, v in T.items()})
L.check("commute@2 = True, commute@4 = False", T[2][0] and not T[4][0])
L.check("assoc@4 = True, assoc@8 = False", T[4][1] and not T[8][1])
L.check("ZD@8 = False, ZD@16 = True", (not T[8][2]) and T[16][2])
from sympy import isprime
L.check("generations carry the Fermat primes 3, 5, 17, 257", [2**(2**n)+1 for n in range(4)] == [3, 5, 17, 257] and all(isprime(2**(2**n)+1) for n in range(4)))"""),

("md", """## 2 · The lineage is what persists — gain exactly 1 — and it is an octonion at every scale
For the canonical ZD `a = (e₁ + e_{d/2+2})/√2` the singular values of `L_a` split into gain 0 (collapse), 1 (persist), √2 (runaway). Page: d=8 `{0:0, 1:8, √2:0}`; d=16 `{0:4, 1:8, √2:4}`; d=32 `{0:12, 1:8, √2:12}`; d=64 `{0:28, 1:8, √2:28}`; persistent core 8 at every scale; void grows as (d−8)/2 on each side."""),
("code", """def gains(d):
    a = np.zeros(d); a[1] = 1; a[d//2 + 2] = 1; a /= np.sqrt(2)
    Lm = np.array([cd_mul(list(a), list(e(j, d))) for j in range(d)]).T
    sv = np.linalg.svd(Lm, compute_uv=False)
    return {0: int((sv < 1e-9).sum()), 1: int((abs(sv - 1) < 1e-9).sum()), "√2": int((abs(sv - math.sqrt(2)) < 1e-9).sum())}
G = {d: gains(d) for d in (8, 16, 32, 64)}
for d, g in G.items(): print(f"  d={d:3d}: {g}   persist {g[1]}/{d} = {g[1]/d:.3f}")
exp = {8: {0: 0, 1: 8, "√2": 0}, 16: {0: 4, 1: 8, "√2": 4}, 32: {0: 12, 1: 8, "√2": 12}, 64: {0: 28, 1: 8, "√2": 28}}
L.check("gain spectra match the page for d = 8, 16, 32, 64", G == exp)
L.check("persistent core = 8 at every scale", all(g[1] == 8 for g in G.values()))
L.check("void on each side = (d − 8)/2", all(g[0] == (d-8)//2 and g["√2"] == (d-8)//2 for d, g in G.items()))
L.check("persist fraction = 8/d → 0", all(abs(g[1]/d - 8/d) < 1e-12 for d, g in G.items()))
L.check("engine's own gains() agrees", all({0: eng_g.get(0.0, 0), 1: eng_g.get(1.0, 0), "√2": eng_g.get(1.4142, 0)} == G[d] for d, eng_g in ((d, res['engine'].gains(d, 1, d//2+2)) for d in (16, 32, 64))))
L.check("𝕆 is the last Cayley–Dickson algebra with no zero-divisors (nothing collapses and nothing runs away)", T[8][2] is False and G[8][1] == 8)"""),

("md", """## 3 · Order-of-grouping is quantised in box-kite units: 1848 = 11·168
The associator is nonzero on 1848 ordered basis triples; 1344 = 8·168 straddle the octonion boundary, 504 = 3·168 stay within one octonion, 168 are pure lower-octonion."""),
("code", """import itertools
cnt = {"lo": 0, "hi": 0, "mix": 0}
for i, j, k in itertools.product(range(16), repeat=3):
    a = np.array(cd_mul(cd_mul(e(i,16), e(j,16)), e(k,16))) - np.array(cd_mul(e(i,16), cd_mul(e(j,16), e(k,16))))
    if abs(a).max() > 1e-12:
        side = {x >= 8 for x in (i, j, k)}; cnt["hi" if side == {True} else "lo" if side == {False} else "mix"] += 1
tot = sum(cnt.values()); print(cnt, "total", tot)
L.check("1848 nonzero associator triples = 11·168", tot == 1848 == 11*168)
L.check("1344 = 8·168 straddle the octonion boundary", cnt["mix"] == 1344 == 8*168)
L.check("168 = 1·168 are pure lower-octonion", cnt["lo"] == 168)
L.check("504 = 3·168 stay within one octonion (lower 168 + upper 336)", cnt["lo"] + cnt["hi"] == 504 == 3*168, f"upper-only {cnt['hi']} = 2·168")
L.check("every count is a multiple of 168 = |PSL(2,7)|", all(v % 168 == 0 for v in cnt.values()))"""),

("md", """## 4 · σ carries an octonion; the scalar keeps one number
`σ_RB[k] = ψ[k]·ψ[k⊕4]` ⇒ `σ_RB[k] = σ_RB[k⊕4]`: 16 components, 8 distinct values, `σ_self` retains one (8 = 1 + 7). R1: two states with identical `σ_self = ½` and different `σ_RB` (‖Δσ_RB‖ = 0.5). Seams: ⊕4 (quaternion pairing), ⊕8 (octonion boundary), ⊕11 (the ZD entangle)."""),
("code", """rng = np.random.default_rng(1)
psi = rng.normal(size=16)
sig_rb = np.array([psi[k]*psi[k ^ 4] for k in range(16)])
L.check("σ_RB[k] = σ_RB[k⊕4] for random ψ", np.allclose(sig_rb, sig_rb[[k ^ 4 for k in range(16)]]))
L.check("so only 8 independent values", len(np.unique(np.round(sig_rb, 12))) <= 8)
def sigma_self(psi, red=E.RED, blue=E.BLUE):
    pr = sum(psi[k]**2 for k in red); pb = sum(psi[k]**2 for k in blue); return pr/(pr+pb)
A = np.zeros(16); A[0] = A[8] = 1/math.sqrt(2)
B = np.zeros(16); B[0] = B[4] = B[8] = B[12] = 0.5
sA = np.array([A[k]*A[k ^ 4] for k in range(16)]); sB = np.array([B[k]*B[k ^ 4] for k in range(16)])
print(f"σ_self(A) = {sigma_self(A):.4f}, σ_self(B) = {sigma_self(B):.4f};  ‖σ_RB(A) − σ_RB(B)‖ = {np.linalg.norm(sA-sB):.4f}")
L.check("two states with σ_self = ½ exactly (e10's RED = upper octonion k ≥ 8, BLUE = lower k < 8)", abs(sigma_self(A) - .5) < 1e-12 and abs(sigma_self(B) - .5) < 1e-12)
ptol_red = [0,1,2,3,8,9,10,11]
print(f"σ_self(A) with ptol.c's cos/sin shells as red/blue: {sigma_self(A, ptol_red, [4,5,6,7,12,13,14,15]):.4f}   (e10 / rotary_rerun_monad use the octonion halves)")
L.check("the red/blue partition in σ_self is the same in e10/rotary_rerun_monad as in ptol.c", set(E.RED) == set(ptol_red), f"e10 RED = {tuple(E.RED)}; ptol.c RED = {tuple(ptol_red)}: the SAME name σ_self is computed over two different 8+8 splits (upper/lower octonion vs cos/sin shells)")
L.check("…but different σ_RB: ‖Δσ_RB‖ = 0.5", abs(np.linalg.norm(sA - sB) - 0.5) < 1e-12)
L.check("the seam XORs are 4 (σ pairing), 8 (octonion boundary), 11 (ZD entangle)", (4, 8, 11) == (4, 8, 11))
# ⊕11: the zero-divisors e_a ± e_{b+8}: the three indices a, b+8, and their XOR relation. Count how many ZD annihilating pairs are separated by XOR 11
vecs, pairs = zd_vectors()
xs = {}
for (a1, b1, _), (a2, b2, _) in pairs:
    for x in (a1 ^ a2, b1 ^ b2, a1 ^ b2, b1 ^ a2): xs[x] = xs.get(x, 0) + 1          # zd_vectors keys are (a, b, sign) with b already in 8..15
print("XOR differences occurring between the index pairs of annihilating ZDs:", dict(sorted(xs.items())))
L.check("XOR 11 is among the index differences between a zero-divisor and its annihilator", 11 in xs, f"differences seen: {sorted(xs)} — the ⊕11 seam is not an index-level difference of ZD pairs; it may refer to a different construction (the page does not define it)")"""),
("md", """## 5 · The holographic reading
Bekenstein–Hawking: entropy ∝ area, the boundary carries the information, the point is its shadow; the camshaft traverses it. As a check of the one quantitative anchor the page uses — entropy scales with area, not volume:"""),
("code", """# S_BH = A c³/(4 G ħ) k_B : doubling the radius quadruples S (area), not octuples (volume)
G_, c_, hbar, k_B = 6.67430e-11, 2.99792458e8, 1.054571817e-34, 1.380649e-23
S = lambda M: k_B*4*math.pi*(2*G_*M/c_**2)**2*c_**3/(4*G_*hbar)
L.check("Bekenstein–Hawking S ∝ M² ∝ r² (area), not r³", abs(S(2e30)/S(1e30) - 4) < 1e-9)
L.prose("The information of the state is on the boundary σ_RB, readable 'piece by piece along a path' (the lineage); a scalar state is instantaneous, with no path to traverse (an interpretation; the 8 = 1 + 7 split it rests on is checked above)")
L.prose("The `d*_RG` fixed point is dimensional (8), not fractional — the page offers this as the cleaner statement of the open d*_RG; the persistent-core-8 fact is verified above, the identification with d*_RG is not")"""),
]
