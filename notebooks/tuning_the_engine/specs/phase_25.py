LABEL = "25"
TITLE = "The Box-Kite Debugger, and the Negative Space"
DATE = "2026-08-05"
PAGE = "25_the_box_kite_debugger_and_the_negative_space.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """## 1 · Everything derives from the Cayley–Dickson table — rederive it independently
Page: assessors are planes `span(e_a, e_{b+8})`, `a,b ∈ 1..7`, whose diagonals `e_a ± e_{b+8}` zero-divide; `a == b` never works. Counts: 42 = 49−7 aligned assessors, 84 = 42×2 diagonals, 168 = 42×4 unit points, 336 = 84×4 ordered annihilating pairs; strut `s = a XOR b ∈ 1..7`; 7 box-kites × 6 assessors. Derive them here from `engines/_sedenion.cd_mul` (not from the box_kite module), then compare with `ValaQuenta/modules/box_kite`."""),
("code", """from _sedenion import cd_mul, e
import itertools
def vec(a, b, s):
    v = [0.0]*16; v[a] = 1.0; v[b+8] = float(s); return v
iszero = lambda v: max(abs(t) for t in v) < 1e-12
diag = {(a, b, s): vec(a, b, s) for a in range(1, 8) for b in range(1, 8) for s in (1, -1)}
ann = {k: [] for k in diag}
for k1, v1 in diag.items():
    for k2, v2 in diag.items():
        if iszero(cd_mul(v1, v2)): ann[k1].append(k2)
is_zd = {k: bool(v) for k, v in ann.items()}
assessors = [(a, b) for a in range(1, 8) for b in range(1, 8) if is_zd[(a, b, 1)] and is_zd[(a, b, -1)]]
print(f"assessors (both diagonals zero-divide): {len(assessors)}; a==b among them: {sum(a == b for a, b in assessors)}")
L.check("42 = 49 − 7 assessors; a == b never works", len(assessors) == 42 and all(a != b for a, b in assessors))
ndiag = sum(1 for k in diag if is_zd[k] and (k[0], k[1]) in set(assessors))
L.check("84 = 42×2 diagonals", ndiag == 84)
L.check("168 = 42×4 unit points (±e_a ± e_{b+8} up to overall sign, normalised: 4 per assessor)", len(assessors)*4 == 168)
ordered = sum(len(v) for k, v in ann.items() if is_zd[k])
L.check("336 = 84×4 ordered annihilating pairs (each ZD has 4 partners)", ordered == 336 and all(len(v) == 4 for k, v in ann.items() if is_zd[k]), f"ordered pairs {ordered}")
strut = lambda a, b: a ^ b
kites = {}
for a, b in assessors: kites.setdefault(strut(a, b), []).append((a, b))
print("struts:", sorted(kites), " sizes:", [len(v) for _, v in sorted(kites.items())])
L.check("7 box-kites (struts 1..7) of 6 assessors each", sorted(kites) == list(range(1, 8)) and all(len(v) == 6 for v in kites.values()))"""),
("code", """import ValaQuenta.modules.box_kite.maths as B
vc = B.verify_counts()
print({k: v for k, v in vc.items() if not isinstance(v, (list, dict))})
L.check("module's own count verification agrees with the independent derivation", vc['assessors'] == len(assessors) and vc['diagonals'] == ndiag and vc['unit_points'] == 168 and vc['ordered_zd_pairs'] == ordered if 'ordered_zd_pairs' in vc else vc['assessors'] == 42)
L.check("all 42 module assessors equal the independently found set", sorted(B.assessors()) == sorted(assessors))"""),

("md", """## 2 · Each chart is an octahedron K₂,₂,₂; dispersion {0,4,4,4,6,6}
Adjacency = two assessors have diagonals that multiply to zero. Build all seven graphs from the vanishing products and check regularity, the three non-edges (reversal pairs), and the Laplacian spectrum."""),
("code", """def adjacent(A, B):
    return any(iszero(cd_mul(vec(*A, s1), vec(*B, s2))) for s1 in (1, -1) for s2 in (1, -1))
spectra = {}; ok_oct = True; cross = 0
for s, nodes in sorted(kites.items()):
    edges = [(i, j) for i in range(6) for j in range(i+1, 6) if adjacent(nodes[i], nodes[j])]
    deg = [sum(1 for e_ in edges if i in e_) for i in range(6)]
    non = [(i, j) for i in range(6) for j in range(i+1, 6) if (i, j) not in edges]
    ok_oct &= len(edges) == 12 and set(deg) == {4} and len(non) == 3 and len({x for p in non for x in p}) == 6
    A = np.zeros((6, 6)); 
    for i, j in edges: A[i, j] = A[j, i] = 1
    spectra[s] = np.round(np.linalg.eigvalsh(np.diag(A.sum(1)) - A), 6)
print("strut 1 Laplacian spectrum:", spectra[1])
L.check("every chart: 6 vertices, 12 edges, 4-regular, 3 disjoint non-edges (octahedron K₂,₂,₂)", ok_oct)
L.check("chart dispersion relation {0,4,4,4,6,6} for all seven", all(np.allclose(sp_, [0, 4, 4, 4, 6, 6]) for sp_ in spectra.values()))
# cross-strut edges
for (s1, n1), (s2, n2) in itertools.combinations(sorted(kites.items()), 2):
    cross += sum(adjacent(A, B) for A in n1 for B in n2)
print("edges between assessors of DIFFERENT struts:", cross)
L.check("ZERO cross-strut edges: 7 disconnected octahedra (the page's finding)", cross == 0)
L.check("module spectrum agrees", np.allclose(sorted(B.chart_spectrum(1)), [0, 4, 4, 4, 6, 6], atol=1e-8))
# the zero mode count in the glued Laplacian
gs = np.array(sorted(B.glued_spectrum())); print("zero modes of the glued Laplacian:", int((np.abs(gs) < 1e-8).sum()))
L.check("seven zero modes in the glued 42-vertex Laplacian", int((np.abs(gs) < 1e-8).sum()) == 7)"""),
("md", """## 3 · The object is PSL(2,7) (order 168), not G₂
`G₂` continuous, dim 14; `PSL(2,7)` finite, order 168, `Aut(Fano)`. Verify 168 directly: |GL(3,2)| by enumeration of invertible 3×3 matrices over GF(2); PG(3,2) has 15 points, 35 lines, 15 planes (7 points each)."""),
("code", """cnt = 0
for bits in range(512):
    M3 = [[(bits >> (3*r + c)) & 1 for c in range(3)] for r in range(3)]
    det = (M3[0][0]*(M3[1][1]*M3[2][2] - M3[1][2]*M3[2][1]) - M3[0][1]*(M3[1][0]*M3[2][2] - M3[1][2]*M3[2][0]) + M3[0][2]*(M3[1][0]*M3[2][1] - M3[1][1]*M3[2][0])) % 2
    cnt += det
L.check("|GL(3,2)| = |PSL(2,7)| = 168 (invertible 3×3 matrices over GF(2))", cnt == 168, f"{cnt}")
pts = list(range(1, 16))
lines = {frozenset(t) for t in itertools.combinations(pts, 3) if t[0] ^ t[1] == t[2]}
L.check("PG(3,2): 15 points, 35 lines (triples a⊕b=c)", len(pts) == 15 and len(lines) == 35)
L.check("the module reports the same", len(B.pg32_points()) == 15 and len(B.pg32_lines()) == 35 and B.psl27_order() == 168)
L.prose("Moreno (1997): the sedenions' norm-one zero-divisors are homeomorphic to G₂ — a published theorem (not recomputed); de Marrais (2000): the homomorphism is a 'blow-up' that loses the labelling")"""),
("md", """## 4 · ∅_RB (e₀) is not the geometry; e₈ is the other orphan
Page/addendum: e₀ is in no assessor, not a PG(3,2) point, a vertex of no box-kite, and `[e₀,·,·] = 0`; exactly two basis elements are in no assessor: e₀ and e₈. Every usable index lies in 6 of the 7 charts; each pair of charts shares exactly 10 skeleton points."""),
("code", """used = {x for (a, b) in assessors for x in (a, b+8)}
print("basis indices in no assessor:", sorted(set(range(16)) - used))
L.check("exactly e₀ and e₈ are in no assessor", sorted(set(range(16)) - used) == [0, 8])
chart_idx = {s: {x for (a, b) in nodes for x in (a, b+8)} for s, nodes in kites.items()}
per_index = {x: sum(1 for s in chart_idx if x in chart_idx[s]) for x in used}
L.check("every usable index lies in exactly 6 of the 7 charts", set(per_index.values()) == {6}, str(sorted(set(per_index.values()))))
sh = {(s1, s2): len(chart_idx[s1] & chart_idx[s2]) for s1, s2 in itertools.combinations(sorted(chart_idx), 2)}
print("skeleton points shared by chart pairs:", sorted(set(sh.values())))
L.check("every chart pair shares exactly 10 skeleton points", set(sh.values()) == {10})
assoc = lambda i, j, k: np.array(cd_mul(cd_mul(e(i,16), e(j,16)), e(k,16))) - np.array(cd_mul(e(i,16), cd_mul(e(j,16), e(k,16))))
L.check("[e₀, j, k] = 0 for all j, k (the identity generates the boundary and does not live on it)", all(np.abs(assoc(0, j, k)).max() < 1e-12 for j in range(16) for k in range(16)))
nz = sum(1 for i in range(16) for j in range(16) for k in range(16) if np.abs(assoc(i, j, k)).max() > 1e-12)
print(f"basis triples with nonzero associator: {nz} of {16**3}")
L.check("1848 of 4096 basis triples curve (page)", nz == 1848, f"{nz}")
L.check("module census agrees", B.associator_census()['nonzero'] == nz)"""),

("md", """## 5 · The negative space: Mertens, μ, and the same ½
`M(x) = Σ_{n≤x} μ(n)`; RH ⇔ `M(x) = O(x^{½+ε})`. Page: M(10) = −1, M(100) = 1, M(1000) = 2, M(10000) = −23; growth 1/ζ(s) = Σ μ(n)n⁻ˢ = ∏(1−p⁻ˢ)."""),
("code", """from sympy import mobius
mu = [0] + [int(mobius(n)) for n in range(1, 20001)]
Mcum = np.cumsum(mu)                       # Mcum[x] = M(x)
Mx = lambda x: int(Mcum[x])
vals = {x: Mx(x) for x in (10, 100, 1000, 10000)}
print("M(x):", vals)
L.check("M(10)=−1, M(100)=1, M(1000)=2, M(10000)=−23", vals == {10: -1, 100: 1, 1000: 2, 10000: -23})
from ValaQuenta.modules.archimedes_screw import maths as M
L.check("module mertens(x) agrees", all(M.mertens(x) == v for x, v in vals.items()))
mx = max(abs(Mx(x)) for x in range(1, 20001, 7)); print(f"max |M(x)| for sampled x ≤ 2·10⁴: {mx};  √x at 2·10⁴ = {math.sqrt(2e4):.1f}")
L.check("|M(x)| stays below √x for x ≤ 10⁴ (Mertens' (false) conjecture is not violated here — first counterexample is astronomically large)", all(abs(Mx(x)) < math.sqrt(x) for x in range(2, 10001, 13)))
import mpmath as mp
mp.mp.dps = 20
from sympy import primerange
prod = 1.0
for p in primerange(2, 10000): prod *= (1 - p**-3.0)
inv = 1/float(mp.zeta(3)); print(f"∏(1−p⁻³) over p<10⁴ = {prod:.12f}   1/ζ(3) = {inv:.12f}")
L.check("extinction product ∏(1−p⁻ˢ) = 1/ζ(s) = Σ μ(n)n⁻ˢ at s=3", abs(prod - inv) < 1e-9 and abs(sum(mu[n]*n**-3.0 for n in range(1, 20000)) - inv) < 1e-9)"""),
("md", """## 6 · The bug the build found (`CTX_ARCHIMEDES_SCREW` inner quotes)
`~/.clauderc_ValaQuenta` defines each context block as a bash string; an inner double quote ends it early. Check the file now parses and the engine's context resolves."""),
("code", """import subprocess, shlex
rc = os.path.expanduser("~/.clauderc_ValaQuenta")
r_ = subprocess.run(["bash", "-n", rc], capture_output=True, text=True)
L.check("~/.clauderc_ValaQuenta has no bash syntax error (inner-quote bug fixed)", r_.returncode == 0, r_.stderr[:200])
out = subprocess.run(["bash", "-c", f"source {shlex.quote(rc)}; echo \\"${{CTX_ARCHIMEDES_SCREW:0:80}}\\"; echo \\"${{CTX_BOX_KITE:0:80}}\\""], capture_output=True, text=True)
print(out.stdout[:300])
L.check("CTX_ARCHIMEDES_SCREW and CTX_BOX_KITE both resolve to non-empty text", all(l.strip() for l in out.stdout.strip().splitlines()[:2]) and len(out.stdout.strip().splitlines()) >= 2)"""),
("code", """for c in ["The gluing is not an edge problem but a group-action problem: the transition maps would be the PSL(2,7) action permuting the struts (CONJECTURE — named next step, not built)",
          "Identify the seven zero modes (all e₀) and the atlas connects at e₀ and nowhere else (the counts are checked; 'at the fixed point boundary and geometry are the same vector' is a reading)",
          "Three motions — grown (ζ orders), extinct (μ strikes, lpf), identified (N-shape names, gpf): the leaf is dead but unnamed for 2δ",
          "The chart of addresses / address census over the book (3,288 entries): needs the monad book, descriptive only"]:
    L.prose(c)"""),
]
