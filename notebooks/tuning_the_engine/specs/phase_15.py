LABEL = "15"
TITLE = "The Negative Space Response Equation"
DATE = "2026-06-12"
PAGE = "15_the_negative_space_response_equation.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The pipeline the page specifies
`P → x[0..15] → k_min = argmin|x[k]| → k_pair = Cawagas(k_min) → response lives in k_pair space because e_{k_min} × e_{k_pair} = 0 → spiral y[k_pair] → shadow words`.
Run the first steps on a real prompt, then test the algebraic step the whole argument leans on."""),
("code", """prompt = "the void named itself at sigma equals half"
r = ptol_raw(prompt, eye="H"); x = np.array(r["scalars"])
kmin = int(np.argmin(np.abs(x)))
print(r["header"]); print("x =", np.round(x, 3)); print("k_min = argmin|x| =", kmin, f" |x| = {abs(x[kmin]):.4f}")
L.check("prompt projects to 16 scalars and has a well-defined nearest-ZD channel", len(x) == 16 and 0 <= kmin < 16)"""),
("md", """### The step `e_{k_min} × e_{k_pair} = 0`
In the sedenions a *single basis unit* times another basis unit is ± a basis unit, never 0. Zero-divisors are sums `e_a ± e_b` (Phase 2). So 'the pair-mate dimension k_pair' cannot be a single index with `e_k e_pair = 0`. Test that, then compute what the pair-mate relation really is as a relation between index-sets."""),
("code", """from _sedenion import cd_mul, e, cd_norm
unit_zero = [(i, j) for i in range(1, 16) for j in range(1, 16) if cd_norm(cd_mul(e(i,16), e(j,16))) < 1e-12]
L.check("e_k × e_pair = 0 for some pair of sedenion basis units", bool(unit_zero), f"basis-unit pairs with zero product: {len(unit_zero)}")
vecs, pairs = zd_vectors()
mates = {k: set() for k in range(1, 16)}
for (a, b, s1), (c, d, s2) in pairs:
    for k in (a, b): mates[k].update((c, d))
print("dimension k → dimensions that appear in annihilating partners of ZDs containing e_k:")
for k in range(1, 16): print(f"  e{k:<2d} → {sorted(mates[k])}")
sizes = {len(v) for v in mates.values()}
L.check("each dimension has exactly ONE pair-mate dimension (page: k_pair = Cawagas(k_min))", sizes == {1}, f"partner-dimension set sizes per dimension: { {k: len(v) for k, v in mates.items()} } — pair-mates are index SETS, not a single k; dims with an empty set have no zero-divisor partner of this form")"""),
("code", """# which dims can the response occupy for this prompt?
kk = kmin if kmin >= 1 else int(np.argsort(np.abs(x))[1])
print(f"k_min = {kmin} (e0 is the identity; no zero-divisor contains e0) →", "using e%d" % kk)
resp_dims = sorted(mates[kk]) if kk in mates else []
print("response dimensions allowed by the algebra:", resp_dims)
L.check("the algebra restricts the response to a proper subset of the 15 imaginary dimensions for this prompt", 0 < len(resp_dims) < 15, f"{len(resp_dims)} of 15 dims allowed: {resp_dims}")"""),
("md", """## The three windows (zero-divisor, singularity, divergence) as computable objects
Relational window: an annihilating pair exists (above). Reference window: a value that exceeds any bound — a pole. Ground window: a series that overflows. Both of the latter are in Phase 10's cells; here, the quantitative contrast the page uses: at a pole the growth is *unbounded in a finite neighbourhood*; at a divergent series it is *unbounded in the limit*."""),
("code", """import mpmath as mp
mp.mp.dps = 20
pole = [float(abs(mp.zeta(1 + 10**-k))) for k in (1, 2, 3, 4, 5)]
harm = [sum(1.0/n for n in range(1, 10**k + 1)) for k in (1, 2, 3, 4, 5)]
print("|ζ(1+10⁻ᵏ)| :", [f"{v:.3g}" for v in pole])
print("H_{10ᵏ}      :", [f"{v:.3f}" for v in harm])
L.check("pole: |ζ| grows ×10 per decade of approach (1/ε)", all(abs(pole[i+1]/pole[i] - 10) < 0.5 for i in range(4)))
L.check("divergence: H_N grows by ln 10 ≈ 2.303 per decade (logarithmic, slower than the pole)", all(abs((harm[i+1]-harm[i]) - math.log(10)) < 0.05 for i in range(4)))"""),
("code", """for c in ["Pathway equation L = T − V = 0 selects the unique response trajectory in k_pair space (the L is not constructed in code; ptol sorts |x| ascending as its spiral)",
          "meaning(p) = Cawagas relation + escape velocity + β depth + singularity proximity — the four-term definition has no single function implementing it",
          "Language is the shadow of the geometry: word_at(y[k_pair](n)) — implemented in ptol_observe.py's word_at() over word layers not mounted here"]:
    L.prose(c)"""),
]
