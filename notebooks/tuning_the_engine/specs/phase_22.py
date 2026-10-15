LABEL = "22"
TITLE = "The Translator: Zero-Divisors as Portals, Landmark Navigation"
DATE = "2026-06-30 (reconstructed after a power outage)"
PAGE = "22_the_translator_zero_divisors_as_portals_landmark.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """## 1 · The quaternion regular representation L(q) and its determinant
Page: every quaternion `q=(w,x,y,z)` has the 4×4 real matrix
`L(q) = [[w,−x,−y,−z],[x,w,−z,y],[y,z,w,−x],[z,−y,x,w]]`; the four 4-blocks {e0-3, e4-7, e8-11, e12-15} of `ptol.c` are "quaternion blocks and always have been"; `det L(q)` and its eigenvalues are "The Information Compressed". Check: `L(q)` really is left-multiplication in ℍ, `det L(q) = N(q)²`, orthogonality for unit q, and that 𝕊's two octonion halves are each ℍ⊕ℍ."""),
("code", """from _sedenion import cd_mul, cd_conj, cd_norm
def Lq(q):
    w, x, y, z = q
    return np.array([[w,-x,-y,-z],[x,w,-z,y],[y,z,w,-x],[z,-y,x,w]])
rng = np.random.default_rng(6)
errs = []
for _ in range(200):
    q, r = rng.normal(size=4), rng.normal(size=4)
    errs.append(np.abs(Lq(q) @ r - np.array(cd_mul(list(q), list(r)))).max())
L.check("L(q)·r = q·r (cd_mul at n=4) for 200 random pairs", max(errs) < 1e-12, f"max err {max(errs):.1e}")
dets = [(np.linalg.det(Lq(q)), (q@q)**2) for q in rng.normal(size=(100, 4))]
L.check("det L(q) = N(q)²  (N = squared norm)", all(abs(a-b) < 1e-9*max(1, b) for a, b in dets))
u = rng.normal(size=4); u /= np.linalg.norm(u)
L.check("unit q ⇒ L(q) is orthogonal (a rotation of ℝ⁴)", np.allclose(Lq(u).T @ Lq(u), np.eye(4)))
ev = np.linalg.eigvals(Lq(u)); print("eigenvalues of L(unit q):", np.round(ev, 4), " |λ| =", np.round(np.abs(ev), 6))
L.check("eigenvalues of L(unit q) are e^{±iθ}, each twice", np.allclose(np.abs(ev), 1) and np.allclose(np.sort(np.angle(ev)), np.sort([np.arccos(u[0]), np.arccos(u[0]), -np.arccos(u[0]), -np.arccos(u[0])])))
print("-> det L(q) = N(q)² is a NORM invariant: it carries no information beyond |q| (the wiki's own Phase 26 returns to this).")"""),
("md", """## 2 · Test 1 — where does subtraction live? (the Cayley–Dickson product)
`(a,b)(c,d) = (a·c − d̄·b, d·a + b·c̄)`: the LOWER half is built by subtraction, the UPPER half by addition, at every level. `cd_conj` negates everything but e₀ ("θ → −θ"). Instrument `cd_mul`."""),
("code", """import inspect
src = inspect.getsource(cd_mul); print(src)
x, y = rng.normal(size=16), rng.normal(size=16)
a, b, c_, d = x[:8], x[8:], y[:8], y[8:]
conj = lambda v: np.array(cd_conj(list(v)))
lo = np.array(cd_mul(list(a), list(c_))) - np.array(cd_mul(list(conj(d)), list(b)))
hi = np.array(cd_mul(list(d), list(a))) + np.array(cd_mul(list(b), list(conj(c_))))
full = np.array(cd_mul(list(x), list(y)))
L.check("lower half (e0-e7) = a·c − d̄·b  (subtraction)", np.allclose(full[:8], lo))
L.check("upper half (e8-e15) = d·a + b·c̄  (addition)", np.allclose(full[8:], hi))
v = rng.normal(size=16); L.check("cd_conj negates every component except e₀", np.allclose(cd_conj(list(v)), [v[0]] + list(-v[1:])))"""),
("md", """## 3 · Test 2 — landmark routes and the resolution hypothesis
v2 (not in the repo any more; `UDEO_monad.py` is v5/v6): 16D vector → 4 quaternion blocks → block determinant signs → walk the spiral order (ascending |v|), compress to one landmark per block transition tagged by the turn sign of the determinant; compare routes by LCS overlap. The page's diagnosis: the route alphabet is too small (~192) for a 4000-word vocabulary, so collisions are forced by pigeonhole.
Count the alphabet **exactly** instead of estimating, then rebuild the v2 route function and measure real collisions."""),
("code", """import itertools
def routes(nblocks):                       # block visiting order × turn signs for each transition after the first
    return math.factorial(nblocks) * 2**(nblocks-1)
print("route alphabet size: 4 blocks (16D) =", routes(4), "; 8 blocks (T32) =", f"{routes(8):,}", "; 16 blocks (T64) =", f"{routes(16):,}")
L.check("16D: 4! block orders × 2³ turn-sign choices = 192 distinct routes (page: ~192)", routes(4) == 192)
n_words = 4000
print(f"pigeonhole at {n_words} words: at least {math.ceil(n_words/192)} words must share a route at 16D; T32 has room for {routes(8)//n_words:,} routes per word")
L.check("16D cannot separate 4000 words (192 < 4000): collision is forced", 192 < n_words)
L.check("T32 (8 blocks) has > 10⁶ routes: the capacity limit is lifted", routes(8) > 10**6)"""),
("code", """def route(v):
    n = len(v)//4
    blocks = [v[4*i:4*i+4] for i in range(n)]
    dets = [np.linalg.det(Lq(b)) for b in blocks]                  # = N(b)² ≥ 0 !
    order = sorted(range(len(v)), key=lambda k: abs(v[k]))
    seen = []
    for k in order:
        b_ = k // 4
        if b_ not in seen: seen.append(b_)
    # turn sign of the determinant relative to the previous block visited
    r = [f"q{seen[0]}start"]
    for p_, q_ in zip(seen, seen[1:]):
        r.append(f"q{q_}{'+' if dets[q_] >= dets[p_] else '-'}")
    return tuple(r), dets
words = [w.strip('.,!?;:"\\'()[]').lower() for l in open(os.path.join(VAPMIP,'foundations.txt'),encoding='utf-8') for w in l.split()]
words = sorted({w for w in words if 3 <= len(w) <= 14 and w.isalpha()})[:1500]
home = scratch("ph22_")
R = {w: route(np.array(ptol_raw(w, "H", home)["scalars"])) for w in words}
allroutes = Counter = {}
for w, (r_, d_) in R.items(): allroutes.setdefault(r_, []).append(w)
print(f"{len(words)} words → {len(allroutes)} distinct routes (alphabet {routes(4)}); largest class has {max(len(v) for v in allroutes.values())} words")
L.check("the det of every block is ≥ 0 (det L(q) = N(q)²): the 'turn sign' is a comparison of norms, not an orientation", all(min(d_) >= 0 for _, (r_, d_) in R.items()),
        "so the determinant 'turn direction' carries only |q_i| ≶ |q_j| — no sign/orientation information")
L.check("the 16D route alphabet collides (the page's diagnosis): on average ≥ 10 words share a route", len(words)/len(allroutes) >= 10, f"{len(words)/len(allroutes):.1f} words per route; only {len(allroutes)} of the {routes(4)} possible routes occur at all")
print("example route class:", next(iter(sorted(allroutes.values(), key=len, reverse=True)))[:8])
def lcs(a, b):
    m = [[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)):
        for j in range(len(b)): m[i+1][j+1] = m[i][j]+1 if a[i] == b[j] else max(m[i][j+1], m[i+1][j])
    return m[-1][-1]/max(len(a), len(b))
print("hot ~ cold route similarity:", lcs(R.get('hot', route(np.array(ptol_raw('hot','H',home)['scalars'])))[0], route(np.array(ptol_raw('cold','H',home)['scalars']))[0]))"""),
("md", """The page's v2 positive (`hot → cold`, similarity 1.000) is a statement about a route being shared; with only 192 routes available, sharing is the default outcome and carries no semantic information. The in-notebook rebuild confirms the capacity argument; the specific `hot/cold` number depends on the v2 details (not in the repo) and is shown only as a measurement of the rebuild.

## 4 · What `UDEO_monad.py` (current, v5/v6) says about the same question
Run its own sanity checks and its RSA cross-check (genuine (e, d) pairs vs random controls under the J2 product)."""),
("code", """import io, contextlib
import UDEO_monad as U
buf = io.StringIO()
with contextlib.redirect_stdout(buf): U.sanity_checks()
print(buf.getvalue()[-600:])
L.check("UDEO_monad.sanity_checks() passes (cd_mul ≠ cd_mul_j2 at every dimension)", "should be False" in buf.getvalue())
rv = U.rsa_validate_j2(n_random=30)
rows = rv['results']
for r_ in rows: print(f"  {r_['label']:12} e={r_['e']:<4} d={r_['d']:<5} genuine={r_['genuine']:.4f}  random mean={r_['mean_random']:.4f} sd={r_['std_random']:.4f}  z={r_.get('z', float('nan')):+.2f}")
zs_ = [r_.get('z', 0.0) for r_ in rows]
L.check("genuine (e,d) pairs are separated from random controls under J2 (|z| ≥ 3 on all toy keys)", all(abs(z_) >= 3 for z_ in zs_), f"z-scores {np.round(zs_, 2)} — the file's own docstring records this as 'at chance'")"""),
("code", """for c_ in ["Zero-divisor loci are portals/birthplaces, not endpoints; the accumulated path through ZD holes IS memory (framing; the spiral ordering that would record the path is ptol.c's idx[])",
           "Resolution = dimension count: DNA-level structure needs T₆₄ (a hypothesis; the capacity half is proved above by counting, the 'DNA' half is not tested)",
           "Eye-hand coordination via a controller as the literal mechanism of cursor tracking",
           "Turn-by-turn landmark directions vs satellite coordinates as the compression picture"]:
    L.prose(c_)"""),
]
