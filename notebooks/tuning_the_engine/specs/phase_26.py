LABEL = "26"
TITLE = "The Degeneracy Audit: Five Dead Statistics"
DATE = "2026-08-08"
PAGE = "26_the_degeneracy_audit_five_dead_statistics.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """> *What does this quantity actually vary over?* — every failure on the page is a statistic used to discriminate between things it is **constant** on.

The scripts behind the page live in `ContextPlease/claude/scratchpad/2026-08-08_*`. This notebook re-derives each result from `engines/_sedenion.cd_mul` and the repo data, in-notebook, and compares with the page's numbers."""),
("md", """## 26.1 · det(L_q) = N(q)² — and does it hold up the tower?
Page: `det(L_q) = N(q)²` and `spec(L_q) = {±i,±i}` for every unit pure-imaginary q; "det = N^k at *every* level of the Cayley–Dickson tower, so T32/T64 would also change nothing". The first two are for the 4×4 quaternion block; the last is a claim about the full 16×16 / 32×32 left-multiplication matrix. Test both."""),
("code", """from _sedenion import cd_mul, e
def Lmat(a):
    n = len(a); return np.array([cd_mul(list(a), list(e(j, n))) for j in range(n)]).T
rng = np.random.default_rng(5)
# quaternion block
rat = []
for _ in range(100):
    q = rng.normal(size=4); rat.append(np.linalg.det(Lmat(q))/(q@q)**2)
L.check("n=4: det L(q) / N(q)² = 1.000000 across random q", np.allclose(rat, 1))
sp_all = []
for _ in range(100):
    v = rng.normal(size=3); v /= np.linalg.norm(v); q = np.array([0, *v])
    sp_all.append(np.sort(np.linalg.eigvals(Lmat(q)).imag))
L.check("n=4: spec(L_q) = {±i, ±i} identical for every unit pure-imaginary q", np.allclose(sp_all, [-1, -1, 1, 1], atol=1e-9))
# the tower: is det(L_a) a function of the norm alone at n = 8, 16, 32 ?
print(f"{'n':>3} {'det(L_a)/N^(n/2) over 300 random a':>40}")
spread = {}
for n in (4, 8, 16, 32):
    r = []
    for _ in range(300 if n < 32 else 60):
        a = rng.normal(size=n); N2 = a @ a
        r.append(np.linalg.det(Lmat(a))/N2**(n/2))
    r = np.array(r); spread[n] = (r.min(), r.max())
    print(f"{n:3d}   min {r.min():10.6f}   max {r.max():10.6f}   spread {r.max()-r.min():.2e}")
L.check("n = 8 (octonion): det L_a = N(a)^(n/2) exactly (composition algebra)", spread[8][1]-spread[8][0] < 1e-9 and abs(spread[8][0]-1) < 1e-9)
L.check("n = 16 (sedenion): det L_a = N(a)^(n/2) — 'det = N^k at EVERY level' (page §26.1)", spread[16][1]-spread[16][0] < 1e-6, f"ratio ranges {spread[16][0]:.4f} … {spread[16][1]:.4f}: the full-matrix determinant is NOT a function of the norm alone at n=16")
L.check("n = 32: same claim", spread[32][1]-spread[32][0] < 1e-6, f"ratio ranges {spread[32][0]:.3e} … {spread[32][1]:.3e}")"""),
("md", """**Correction recorded:** the quaternion 4×4 block statistic (what Phase 22's landmarks used) is norm-degenerate — that part of §26.1 is exact. But *"det = N^k at every level"* is true only while the algebra is a composition algebra (n ≤ 8). At n = 16 the full-matrix determinant of L_a is **not** a function of the norm; it carries angular information (and vanishes on the zero-divisors, Phase 17). So the "T32/T64 would also change nothing" extension needs the per-block qualifier: per 4-block, yes; whole-matrix, no. The §26.1 conclusion about the *landmark signature* (built from 4×4 block determinants) stands."""),

("md", """## 26.2 · The wall is alternativity, not associativity — the bracketing test
Left-division `b ≈ a⁻¹·(a·b)`, `a⁻¹ = ā/N(a)`. Page: ℍ 1.4×10⁻¹⁶; 𝕆 1.6×10⁻¹⁶ (while associator 1.10 and bracketing disagreement 113.9 %); 𝕊 0.52 (bracketing 131.5 %); T32 0.74."""),
("code", """def mul(x, y): return np.array(cd_mul(list(x), list(y)))
def conj(x): return np.concatenate([[x[0]], -x[1:]])
inv = lambda x: conj(x)/(x@x)
rng = np.random.default_rng(7)
rows = {}
for dim, nm in ((4, "quaternion"), (8, "octonion"), (16, "sedenion"), (32, "T32")):
    errs, asso, brk = [], [], []
    for _ in range(400 if dim < 32 else 100):
        a, b, d = (rng.normal(size=dim) for _ in range(3))
        errs.append(np.linalg.norm(mul(inv(a), mul(a, b)) - b)/np.linalg.norm(b))
        asso.append(np.linalg.norm(mul(mul(a, b), d) - mul(a, mul(b, d)))/(np.linalg.norm(a)*np.linalg.norm(b)*np.linalg.norm(d)))
        Lh, Rh = mul(mul(a, b), d), mul(a, mul(b, d)); brk.append(np.linalg.norm(Lh-Rh)/max(np.linalg.norm(Lh), 1e-30))
    rows[nm] = (np.median(errs), np.median(asso), np.median(brk)); print(f"  {nm:11} division error {rows[nm][0]:.2e}   associator {rows[nm][1]:.2e}   bracketing disagreement {rows[nm][2]*100:7.1f} %")
L.check("quaternion division exact (~1e-16)", rows["quaternion"][0] < 1e-13)
L.check("octonion division exact to machine precision although NOT associative", rows["octonion"][0] < 1e-13 and rows["octonion"][1] > 0.5)
L.check("sedenion division error ≈ 0.52 (page)", abs(rows["sedenion"][0] - 0.52) < 0.06, f"{rows['sedenion'][0]:.3f}")
L.check("T32 division error ≈ 0.74 (page)", abs(rows["T32"][0] - 0.74) < 0.08, f"{rows['T32'][0]:.3f}")
L.check("octonion bracketing disagreement ≈ 114 % and sedenion ≈ 131 % (page)", abs(rows["octonion"][2] - 1.139) < 0.15 and abs(rows["sedenion"][2] - 1.315) < 0.15, f"{rows['octonion'][2]*100:.1f} % / {rows['sedenion'][2]*100:.1f} %")
# alternativity is exactly what rescues division: (a⁻¹)(ab) = b  in any alternative algebra
alt = {}
for dim in (8, 16):
    alt[dim] = np.median([np.linalg.norm(mul(mul(a, a), b) - mul(a, mul(a, b)))/(np.linalg.norm(a)**2*np.linalg.norm(b)) for a, b in [(rng.normal(size=dim), rng.normal(size=dim)) for _ in range(200)]])
L.check("alternativity (aa)b = a(ab) holds for 𝕆 and fails for 𝕊 — the property division needs", alt[8] < 1e-12 and alt[16] > 0.1, f"defect: 𝕆 {alt[8]:.1e}, 𝕊 {alt[16]:.3f}")"""),
("md", """**Engineering rule on the page:** aggregate addresses additively (mean of 16-vectors), never by multiplying sedenions. Demonstrate the order dependence that motivates it."""),
("code", """vs = [rng.normal(size=16) for _ in range(6)]
def prod_left(vs):
    r = vs[0]
    for v in vs[1:]: r = mul(r, v)
    return r
def prod_right(vs):
    r = vs[-1]
    for v in reversed(vs[:-1]): r = mul(v, r)
    return r
pl, pr = prod_left(vs), prod_right(vs)
ml = np.mean(vs, axis=0); mr = np.mean(vs[::-1], axis=0)
print(f"product, left vs right bracketing: relative difference {np.linalg.norm(pl-pr)/np.linalg.norm(pl):.3f}")
L.check("multiplicative aggregation depends on the bracketing (left ≠ right)", np.linalg.norm(pl-pr)/np.linalg.norm(pl) > 0.1)
L.check("additive aggregation (mean) is order- and bracket-independent", np.allclose(ml, mr))"""),

("md", """## 26.3 · ⚠ RETRACTION — the module signal is lexical, not semantic
Data: `monad_sedenion_addresses.pkl` (3,288 entries of `skills.*` symbols, 16-D addresses). Two-arm shuffled null grouped by parent module (≥4 members), then a 1:1 character-trigram–matched null and a partial correlation."""),
("code", """import pickle
from collections import Counter, defaultdict
from itertools import combinations
book = pickle.load(open(os.path.join(VAPMIP, "monad_sedenion_addresses.pkl"), "rb"))["book"]
names, vecs = [], []
for nm, ent in book.items():
    v = ent.get("sedenion") if isinstance(ent, dict) else ent
    if v is not None and len(v) == 16: names.append(nm); vecs.append(np.asarray(v, float))
V0 = np.array(vecs); print(len(names), "addresses")
L.check("3,288 addresses in the book (page)", len(names) == 3288, f"{len(names)}")
groups = defaultdict(list)
for i, nm in enumerate(names):
    parts = nm.split(".")
    if len(parts) >= 2: groups[".".join(parts[:2])].append(i)
groups = {g: ix for g, ix in groups.items() if len(ix) >= 4}
L.check("92 parent modules with ≥ 4 members (page)", len(groups) == 92, f"{len(groups)}")
def cos_stats(M, rng=None):
    M = M/np.clip(np.linalg.norm(M, axis=1, keepdims=True), 1e-12, None); idx = np.arange(len(M)) if rng is None else rng.permutation(len(M)); within = []
    for g, ix in groups.items():
        jx = idx[ix]; S = M[jx] @ M[jx].T; within.append(S[np.triu_indices(len(jx), 1)].mean())
    return float(np.mean(within))
arms = {"raw 16D": V0.copy(), "e₀ projected out": np.where(np.arange(16) == 0, 0, V0), "e₀+e₈ out": np.where((np.arange(16) == 0) | (np.arange(16) == 8), 0, V0)}
zres = {}
for arm, M in arms.items():
    w = cos_stats(M); nulls = [cos_stats(M, np.random.default_rng(s)) for s in range(200)]
    zres[arm] = (w, np.mean(nulls), np.std(nulls), (w-np.mean(nulls))/np.std(nulls)); print(f"{arm:18} within {w:.4f} | null {np.mean(nulls):.4f} ± {np.std(nulls):.4f} → z = {zres[arm][3]:+.2f}")
L.check("shuffled null: raw z ≈ +29 (page +28.99)", abs(zres["raw 16D"][3] - 29) < 4, f"z = {zres['raw 16D'][3]:+.2f}")
L.check("e₀ projected out roughly doubles the effect (z ≈ +31; gap 0.142 → 0.289)", zres["e₀ projected out"][3] > 25 and (zres["e₀ projected out"][0]-zres["e₀ projected out"][1]) > 1.7*(zres["raw 16D"][0]-zres["raw 16D"][1]), f"gap raw {zres['raw 16D'][0]-zres['raw 16D'][1]:.3f} → {zres['e₀ projected out'][0]-zres['e₀ projected out'][1]:.3f}")
L.check("e₈ carries ≈ 1 %: projecting it out as well changes within-module cos by ~0.003", abs(zres["e₀+e₈ out"][0] - zres["e₀ projected out"][0]) < 0.01, f"{zres['e₀ projected out'][0]:.4f} → {zres['e₀+e₈ out'][0]:.4f}")"""),
("code", """# the lexical-matched null
Vn = V0.copy(); Vn[:, 0] = 0.0; Vn /= np.clip(np.linalg.norm(Vn, axis=1, keepdims=True), 1e-12, None)
N = len(names)
def tri(s): s = f"  {s}  "; return Counter(s[i:i+3] for i in range(len(s)-2))
TRI = [tri(n) for n in names]; MOD = [".".join(n.split(".")[:2]) for n in names]
def tsim(a, b): return sum((a & b).values())/math.sqrt(sum(a.values())*sum(b.values()))
rng = np.random.default_rng(3)
same = []
for g, ix in groups.items():
    ps = list(combinations(ix, 2))
    if len(ps) > 400: ps = [ps[k] for k in rng.choice(len(ps), 400, replace=False)]
    same += ps
P = 150_000; I, J = rng.integers(0, N, P), rng.integers(0, N, P); m = np.array([MOD[i] != MOD[j] and i != j for i, j in zip(I, J)]); I, J = I[m], J[m]
lexD = np.array([tsim(TRI[i], TRI[j]) for i, j in zip(I, J)]); addrD = (Vn[I]*Vn[J]).sum(1); o = np.argsort(lexD); lexD, addrD = lexD[o], addrD[o]
lexS = np.array([tsim(TRI[i], TRI[j]) for i, j in same]); addrS = np.array([float(Vn[i] @ Vn[j]) for i, j in same])
mi = np.clip(np.searchsorted(lexD, lexS), 0, len(lexD)-1); ok = np.abs(lexD[mi]-lexS) <= 0.02
a_, b_ = addrS[ok].mean(), addrD[mi[ok]].mean(); diff = addrS[ok]-addrD[mi[ok]]; se = diff.std()/math.sqrt(len(diff))
print(f"{len(same):,} same-module pairs; matched {ok.sum():,};  lexical sim same {lexS[ok].mean():.4f} vs matched cross {lexD[mi[ok]].mean():.4f}")
print(f"address cos: same {a_:.4f} vs matched cross {b_:.4f}   gap {a_-b_:+.4f} ± {se:.4f}   t = {(a_-b_)/se:+.1f}")
allL = np.concatenate([lexS, lexD]); allA = np.concatenate([addrS, addrD]); allS = np.concatenate([np.ones(len(lexS)), np.zeros(len(lexD))])
X = np.column_stack([np.ones(len(allL)), allL]); rA = allA - X @ np.linalg.lstsq(X, allA, rcond=None)[0]; rS = allS - X @ np.linalg.lstsq(X, allS, rcond=None)[0]
cLA, cSA, pc = np.corrcoef(allL, allA)[0, 1], np.corrcoef(allS, allA)[0, 1], np.corrcoef(rS, rA)[0, 1]
print(f"corr(lexical, address) {cLA:+.4f}   corr(same-module, address) {cSA:+.4f}   partial corr(same-module, address | lexical) {pc:+.4f}")
L.check("lexical similarity matched between arms (|Δ| < 0.01)", abs(lexS[ok].mean() - lexD[mi[ok]].mean()) < 0.01)
L.check("the module effect SURVIVES lexical matching (gap > 3 SE)", (a_-b_)/se > 3, f"gap {a_-b_:+.4f}, t = {(a_-b_)/se:+.1f} — NEGATIVE: the retraction is reproduced")
L.check("corr(lexical, address) ≈ +0.32 — the address is a function of the name", abs(cLA - 0.32) < 0.06, f"{cLA:+.3f}")
L.check("partial corr(same-module, address | lexical) ≈ −0.057 (module effect vanishes and slightly inverts)", pc < 0.02, f"{pc:+.4f}")"""),

("md", """## 26.4 · The Hyperwebster incompatibility — a lossless address cannot be a semantic neighbourhood
Wall 1: a bijection strings ↔ indices preserves length (ratio exactly 1.0000). Wall 2: the index metric measures spelling (`cat/car` 2 apart, `cat/feline` ~10¹⁵)."""),
("code", """from math import log2
for k, nm in ((26, "a–z"), (256, "bytes")):
    for n in (3, 10, 1024):
        idx_bits, data_bits = log2(k**n), n*log2(k)
        if n == 1024: print(f"  {nm:5} length {n}: index {idx_bits:9.1f} bits, data {data_bits:9.1f} bits, ratio {idx_bits/data_bits:.4f}")
        L.check(f"{nm}, length {n}: index bits / data bits = 1.0000 (counting argument)", abs(idx_bits/data_bits - 1) < 1e-12) if n == 1024 else None
def lex_index(s, k=26, off=ord('a')):
    idx = sum(k**i for i in range(1, len(s)))
    for ch in s: idx = idx*k + (ord(ch)-off)
    return idx
d = lambda a, b: abs(lex_index(a) - lex_index(b))
for a, b in (("cat","cats"), ("cat","car"), ("cat","dog"), ("big","large"), ("cat","feline"), ("hot","cold")): print(f"  {a:>4}/{b:<7} index distance {d(a,b):>22,d}")
L.check("cat/car (unrelated) are 2 apart; cat/dog 1,027; cat/feline 3,817,157,994,289,027; big/large 5,646,664,168,650", (d("cat","car"), d("cat","dog"), d("cat","feline"), d("big","large")) == (2, 1027, 3817157994289027, 5646664168650))
L.check("the index metric ranks an UNRELATED pair (cat/car) as vastly closer than a SYNONYM pair (cat/feline)", d("cat","car") * 10**12 < d("cat","feline"))
L.prose("Theorem: a lossless canonical address cannot be a semantic neighbourhood (lossless ⇒ injective ⇒ cat and feline far apart; semantic ⇒ synonyms close ⇒ lossy). A short argument; no code reproduces a proof — the two numbers above are its instances")"""),

("md", """## 26.5 · The common mode is e₀, not e₀ + e₈
Page: mean `fixed_point_weight` (e₀ alone) 0.6435; mean `outside_share` (e₀+e₈) 0.6537; difference 0.0102. Recompute over the book addresses with the same functions from the box-kite module."""),
("code", """import ValaQuenta.modules.box_kite.maths as B
fp = np.array([B.fixed_point_weight(list(v)) for v in V0]); es = [B.energy_split(list(v)) for v in V0]
print("energy_split keys:", list(es[0]))
w0 = V0**2/np.sum(V0**2, axis=1, keepdims=True)
e0, e8 = w0[:, 0].mean(), w0[:, 8].mean()
print(f"mean fixed_point_weight (module) {fp.mean():.4f};  recomputed power share: e₀ {e0:.4f}, e₈ {e8:.4f}, e₀+e₈ {e0+e8:.4f}")
L.check("e₈ carries about 1 % of the energy", e8 < 0.03, f"e₈ share {e8:.4f}")
L.check("e₀ carries the fixed-point weight (≈ 0.64)", abs(e0 - 0.6435) < 0.03 or abs(fp.mean() - 0.6435) < 0.03, f"e₀ {e0:.4f}; module fixed_point_weight {fp.mean():.4f}")"""),

("md", """## 26.6 · The sedenion is exactly one cache line — and the throughput table
16 × fp32 = 64 bytes (one line); 16 × fp64 = 128 bytes (two). Page table (i7-8550U): numpy untiled 326 ms / 1.65 GFLOP/s, C/AVX2 1 thread 177 ms / 3.03, 8 threads 33 ms / 16.19, iGPU 18.5 ms / 29.09, RAM ceiling 8.1 ms / 66, for 2²⁰ products at 512 FLOP each. Re-run the CPU rows with the scratchpad's `sedmul.c` (compiled here) and a numpy table product."""),
("code", """import subprocess, re, time as _t
L.check("16 × fp32 = 64 bytes = one cache line; 16 × fp64 = 128 bytes = two", 16*4 == 64 and 16*8 == 128)
d = scratch("sedbench_"); exe = os.path.join(d, "sedmul")
src = os.path.join(PLACE, "ContextPlease", "claude", "scratchpad", "2026-08-08_sedenion_igpu_benchmark", "sedmul.c")
cc = subprocess.run(["gcc", "-O3", "-mavx2", "-mfma", "-fopenmp", "-o", exe, src], capture_output=True, text=True)
L.check("scratchpad sedmul.c compiles (-O3 -mavx2 -mfma -fopenmp)", cc.returncode == 0, cc.stderr[-200:])
res = {}
if cc.returncode == 0:
    for t in (1, 8):
        o = subprocess.run([exe, str(t)], capture_output=True, text=True).stdout.strip(); print(" ", o)
        m = re.search(r"([\\d.]+) ms\\s+([\\d.]+) GFLOP/s", o); res[t] = (float(m.group(1)), float(m.group(2)))
L.check("C/AVX2 1 thread ≈ 3 GFLOP/s (page 3.03)", 1.5 < res.get(1, (0, 0))[1] < 8, f"{res.get(1)} ms, GFLOP/s")
L.check("C/AVX2 8 threads: ≈ 16 GFLOP/s (page 16.19)", 8 < res.get(8, (0, 0))[1] < 40, f"{res.get(8)} ms, GFLOP/s")
L.check("8 threads is 4–6× the single thread (memory-bound scaling)", 3 < res[8][1]/res[1][1] < 7, f"{res[8][1]/res[1][1]:.1f}×")
L.skip("iGPU UHD 620 zero-copy: 18.5 ms / 29.09 GFLOP/s", "pyopencl is not installed in this venv (the page's run used intel-opencl-icd); rows above are CPU-only")
print("arithmetic intensity:", 512/(3*16*4), "FLOP/byte (3 arrays × 16 fp32 × 4 B) →", f"{512/(3*16*4):.2f}")
L.check("arithmetic intensity ≈ 2.7 FLOP/byte", abs(512/(3*16*4) - 2.67) < 0.01)"""),
("code", """# numpy untiled: sign-table form z[k] = Σ s·x[i]·y[j]
import time
rows_ = []
for i in range(16):
    for j in range(16):
        ei, ej = np.zeros(16), np.zeros(16); ei[i] = 1; ej[j] = 1; p = np.array(cd_mul(list(ei), list(ej))); k = int(np.nonzero(p)[0][0]); rows_.append((i, j, k, p[k]))
TAB = np.array(rows_)
Nn = 1 << 16
X = np.random.rand(16, Nn).astype(np.float32); Y = np.random.rand(16, Nn).astype(np.float32)
def numpy_mul(X, Y):
    Z = np.zeros_like(X)
    for i, j, k, s in rows_: Z[int(k)] += np.float32(s)*X[int(i)]*Y[int(j)]
    return Z
t0 = time.perf_counter(); Z = numpy_mul(X, Y); t1 = time.perf_counter()
gf = 512*Nn/(t1-t0)/1e9
print(f"numpy sign-table product, {Nn:,} sedenions: {1e3*(t1-t0):.1f} ms → {gf:.2f} GFLOP/s (page: 1.65)")
chk = np.array(cd_mul(list(X[:, 5].astype(float)), list(Y[:, 5].astype(float))))
L.check("the sign-table product equals cd_mul on a spot check", np.allclose(Z[:, 5], chk, atol=1e-4))
L.check("numpy untiled throughput is of the page's order (0.3–5 GFLOP/s)", 0.3 < gf < 5, f"{gf:.2f}")"""),

("md", """## 26.7 · RSA — enumerating the standard's constraints is a dead end by construction
| probe | page |
|---|---|
| last-digit / last-two-digit filter | 1.000× |
| wheel sieve, all primes ≤ 10⁶ | 24.6× |
| FIPS 186-5 separation \\|p−q\\| > 2⁹²⁴ | excludes 3.155×10⁻³⁰ |
| GNFS vs naive | 10³⁰⁵ → 10³⁵ |
| Coppersmith threshold | half of p's bits: ~154 of 308 digits for RSA-2048 |"""),
("code", """# (a) last-digit filter: for composite N and any prime p coprime to 10, a q-residue with p·q ≡ N (mod m) always exists -> no reduction
from sympy import primerange
Nn_ = 1000003*1000033
for m in (10, 100):
    pr = [p for p in primerange(7, 2000) if math.gcd(p, m) == 1]
    passing = [p for p in pr if any((p*q) % m == Nn_ % m for q in range(m))]
    print(f"  mod {m}: fraction of primes p passing the 'last digits are consistent with N' filter: {len(passing)/len(pr):.4f}")
    L.check(f"last-{'digit' if m == 10 else 'two-digit'} filter removes nothing (1.000×)", len(passing) == len(pr))
# (b) wheel sieve by all primes ≤ 10^6 : density ∏(1−1/p)  ->  Mertens: e^{-γ}/ln B
dens = 1.0
for p in primerange(2, 10**6 + 1): dens *= (1 - 1/p)
print(f"  ∏_(p ≤ 10⁶)(1−1/p) = {dens:.6f}  → speed-up {1/dens:.2f}×   (Mertens e^γ ln 10⁶ = {math.exp(0.5772156649)*math.log(1e6):.2f})")
L.check("wheel sieve with all primes ≤ 10⁶ gives 24.6× (page)", abs(1/dens - 24.6) < 0.15, f"{1/dens:.2f}×")
# (c) FIPS separation: |p−q| ≤ 2^924 among random 1024-bit primes ≈ 2·2^924 / 2^1023
frac = 2.0**(924 + 1 - 1023)
print(f"  excluded fraction ≈ 2^−98 = {frac:.4e}")
L.check("FIPS 186-5 separation excludes 3.155×10⁻³⁰ of the space (page)", abs(frac/3.155e-30 - 1) < 1e-3, f"{frac:.4e}")
# (d) GNFS vs naive in decimal orders
ln_n = 2048*math.log(2); gnfs_bits = 1.923*ln_n**(1/3)*math.log(ln_n)**(2/3)/math.log(2)
print(f"  naive primes ≤ √N ≈ 10^{1014.53*math.log10(2):.1f};  GNFS heuristic ≈ 2^{gnfs_bits:.1f} = 10^{gnfs_bits*math.log10(2):.1f}")
L.check("naive 10³⁰⁵ → GNFS 10³⁵ (orders of magnitude within ±1.5)", abs(1014.53*math.log10(2) - 305) < 1 and abs(gnfs_bits*math.log10(2) - 35) < 1.5)
L.check("Coppersmith: half of p's bits ≈ 154 of 308 decimal digits for RSA-2048", abs(308/2 - 154) < 1e-9 and abs(1024*math.log10(2) - 308.25) < 0.01, f"1024-bit p has {1024*math.log10(2):.2f} decimal digits")
L.prose("'There is no equation in p alone: N gives one equation in two unknowns; every derived constraint inherits that' — an argument; the digit-window/Hensel branching of ×10 per digit is described, not recomputed here")"""),
("code", """for c in ["Superseded diagnosis: 'insufficient resolution' (Phase 22) → 'degenerate statistic' — checked above per 4-block; the whole-matrix extension fails at n ≥ 16 (the correction)",
          "Build the 16-D address from the co-occurrence graph A (monad_english.bin, ~1.9M edges), not from the index (design direction; no per-word addresses exist — the page's BLOCKED item)",
          "Tower-climbing forfeits cache alignment (T32/fp32 = 2 lines, T64 = 4) — arithmetic; a performance reading",
          "BLOCKED: vocabulary run — no per-word 16-D addresses exist (primer §14 step 4)"]:
    L.prose(c)"""),
]
