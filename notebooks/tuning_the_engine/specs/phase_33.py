LABEL = "33"
TITLE = "Folded-In Context, and the Geometry That Does No Work"
DATE = "2026-08-25"
PAGE = "33_folded_in_context_and_the_geometry_that_does_no_work.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """## 1 · `0_RB` / `0_BR` — grounded, not guessed
`0_RB = J_red + J_blue`; `Σ_RB[k] = ψ[k]·ψ[k⊕4]` is involution-paired (16 slots, 8 independent values); `0_BR` appears once, in a bookkeeping identity that failed: `J_red + 0_BR − 0_RB = J_blue` misses by `(0_BR − 2·J_blue)`."""),
("code", """import sympy as sp
Jr, Jb, X = sp.symbols("J_red J_blue X")
RB = Jr + Jb
miss = sp.simplify((Jr + X - RB) - Jb)
print("J_red + 0_BR − 0_RB − J_blue =", miss)
L.check("the failed identity misses by exactly (0_BR − 2·J_blue)", sp.simplify(miss - (X - 2*Jb)) == 0)
L.check("0_RB vs 0_BR read as a sum or product in either order: zero degrees of freedom (commutativity of + and ×)", sp.simplify((Jr + Jb) - (Jb + Jr)) == 0 and sp.simplify(Jr*Jb - Jb*Jr) == 0)
rng = np.random.default_rng(1); psi = rng.normal(size=16); srb = np.array([psi[k]*psi[k ^ 4] for k in range(16)])
L.check("Σ_RB[k] == Σ_RB[k⊕4] exactly (real multiplication commutes) — 16 slots, 8 independent values", np.array_equal(srb, srb[[k ^ 4 for k in range(16)]]) and len(set(np.round(srb, 14))) <= 8)
import monad as M
for _ in range(3):
    s = "".join(chr(int(c)) for c in rng.integers(97, 123, 30)); psi_c = np.array(M.cam_encode(s)); 
    pr = float((psi_c[8:]**2).sum()); pb = float((psi_c[:8]**2).sum())
    L.check(f"J_red + J_blue = 1.0000000000 for cam_encode('{s[:10]}…') (a unit vector split into non-overlapping halves — geometry, not content)", abs(pr + pb - 1) < 1e-12, f"{pr + pb:.12f}")"""),

("md", """## 2 · The geometry does no work — five collapses, one fact
Table on the page; the third row: `[J_red,J_blue]` and `[J_blue,J_red]` report the same *scalar* in `_lie_bracket` (`rotary_monad.py:394`) because it sums `abs()`, erasing the sign flip the underlying distribution carries — "a reducer choice, not new physics". Test on the live function."""),
("code", """import rotary_monad as R
H = R.Housing(); H.ingest(open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read()[:30000]); n = H.n
a = list(rng.dirichlet(np.ones(n))); b = list(rng.dirichlet(np.ones(n)))
s_ab, d_ab = R._lie_bracket(0.3, a, 0.2, b, H); s_ba, d_ba = R._lie_bracket(0.2, b, 0.3, a, H)
L.check("[J_red,J_blue] and [J_blue,J_red] give the same SCALAR", abs(s_ab - s_ba) < 1e-12, f"{s_ab:.6f} vs {s_ba:.6f}")
L.check("…while the underlying distributions carry the sign flip (d_ab = −d_ba)", np.allclose(d_ab, -np.array(d_ba)))
import inspect
L.check("the cause is the abs() in the reducer (`sum(abs(x) for x in bd)`)", "abs(x) for x in bd" in inspect.getsource(R._lie_bracket))
L.prose("`0_RB`/`0_BR` as a sixth ring pair for the Scale module: 'geometries don't carry independent degrees of freedom, and testing for one is the wrong question' — the correction; the five collapses above are the evidence")"""),

("md", """## 3 · The Scale is a correlator — bumpy at hypercomplex scale
Page: a locally-square fold is exact for any single fold at any point; what breaks is stitching many folds once the content is hypercomplex. The measured cause on record: the failure of norm multiplicativity jumps from `3.55e-15` (octonions) to `7.196609` (sedenions)."""),
("code", """from _sedenion import cd_mul
def maxdev(dim, trials=20000, seed=0):
    r = np.random.default_rng(seed); worst = 0.0
    for _ in range(trials):
        x, y = r.normal(size=dim), r.normal(size=dim); p = np.array(cd_mul(list(x), list(y)))
        worst = max(worst, abs(np.linalg.norm(p) - np.linalg.norm(x)*np.linalg.norm(y)))
    return worst
dO, dS = maxdev(8, 5000), maxdev(16, 5000)
print(f"max | |xy| − |x||y| |  over random normal pairs:  octonion {dO:.2e}    sedenion {dS:.4f}")
L.check("octonions: norm is multiplicative to ~1e-14 (page: 3.55e-15)", dO < 1e-12, f"{dO:.2e}")
L.check("sedenions: norm fails to compose by an O(1) amount (page: 7.196609 on its sample)", dS > 1.0, f"{dS:.4f} on 5000 random N(0,1) pairs; the page's number depends on its sample and is not reproduced digit-for-digit")
vecs, pairs = zd_vectors(); (ka, kb) = next(iter(pairs))
x, y = np.array(vecs[ka])/np.sqrt(2), np.array(vecs[kb])/np.sqrt(2)
L.check("a unit ZD pair has |x|=|y|=1 and |xy|=0: the norm does not compose (the cause the harness comment names)", abs(np.linalg.norm(x) - 1) < 1e-12 and np.linalg.norm(np.array(cd_mul(list(x), list(y)))) < 1e-12)
import ValaQuenta.modules.box_kite.maths as B
col = B.associator_census(); print(col)
L.check("seven octahedral chart-bubbles glue only at e₀ and e₈ (box-kite finding, Phase 25)", B.fixed_point_gluing()['orphan_count'] == 2 and str(B.fixed_point_gluing()['indices_in_no_assessor']) == '[0, 8]')"""),

("md", """## 4 · σ_RB IS a scale reading — `σ_RB[k] = (r_k²/2)·sin(2θ_k)`
Pair the XOR-4 partners as real/imaginary parts of one complex number `Z_k = ψ[k] + iψ[k⊕4]`; page: max error 3.6×10⁻¹⁵ over 2000 trials, all 16 k; all 8 pairs stay inside RED or inside BLUE (XOR 4 flips bit 2, never bit 3)."""),
("code", """errs = []
for _ in range(2000):
    psi = rng.normal(size=16)
    for k in range(16):
        Z = complex(psi[k], psi[k ^ 4]); r2, th = abs(Z)**2, np.angle(Z)
        errs.append(abs(psi[k]*psi[k ^ 4] - (r2/2)*math.sin(2*th)))
print(f"2000 trials × 16 k: max error {max(errs):.2e}")
L.check("σ_RB[k] = (r²/2) sin(2θ) to floating-point exactness (page: 3.6e-15)", max(errs) < 1e-12, f"{max(errs):.2e}")
r_, th_ = 1.7, math.pi/4
L.check("maximal at θ = 45° (ψ[k] = ψ[k⊕4]) and zero when the pair sits on an axis", abs(math.sin(2*th_) - 1) < 1e-15 and abs(0.5*r_**2*math.sin(0)) < 1e-15)
L.check("scale-squared, not scale-invariant: σ_RB grows with r²", abs((2*r_)**2/2*math.sin(2*th_) - 4*(r_**2/2*math.sin(2*th_))) < 1e-12)
red = set(range(8, 16)); blue = set(range(8))
pairs8 = {frozenset((k, k ^ 4)) for k in range(16)}
L.check("the 8 XOR-4 pairs stay entirely inside RED or BLUE (4 + 4), never straddling bit 3", len(pairs8) == 8 and all(p <= red or p <= blue for p in pairs8) and sum(p <= red for p in pairs8) == 4 and sum(p <= blue for p in pairs8) == 4)
from ValaQuenta.modules.scale import maths as SM
print([n for n in dir(SM) if "polar" in n.lower()])
pd = getattr(SM, "polar_decompose", None)
L.check("the Scale module's own polar_decompose exists (so no new tool was needed)", pd is not None)
if pd is not None:
    z = complex(0.6, 0.8); out = pd(z); print("polar_decompose(0.6+0.8i) =", out)
    rr, tt = (out["r"], out["theta"]) if isinstance(out, dict) else (out[0], out[1])
    L.check("polar_decompose returns r = |Z| and θ = arg Z", abs(rr - 1) < 1e-12 and abs(tt - math.atan2(0.8, 0.6)) < 1e-12)"""),

("md", """## 5 · Folded-in context: three faces planned, none merged (PLANNING)
What exists on disk for each face:"""),
("code", """bp = os.path.join(VAPMIP, "PtolC", "c_monad_wordnet.bin"); hdr = open(bp, "rb").read(16)
import struct
magic, ver, nent, esz = struct.unpack("<4sIII", hdr)
print(f"c_monad_wordnet.bin: magic {magic}, version {ver}, entries {nent:,}, entry_size {esz}; file {os.path.getsize(bp):,} bytes")
L.check("wordnet face: c_monad_wordnet.bin is a BXKT file with 154,725 entries", magic == b"BXKT" and nent == 154725, f"{nent:,}")
L.check("file size = header (16) + entries × entry_size", os.path.getsize(bp) == 16 + nent*esz, f"{16 + nent*esz:,} vs {os.path.getsize(bp):,}")
pk = os.path.join(VAPMIP, "monad_boxkite_wordnet.pkl")
L.check("the companion pickle monad_boxkite_wordnet.pkl exists in the repo", os.path.exists(pk), "not found at VAPMIP/ (the page lists it; it may be a local/generated artefact)")
from nltk.corpus.reader.wordnet import WordNetCorpusReader as WR
nrules = sum(len(v) for v in WR.MORPHOLOGICAL_SUBSTITUTIONS.values())
L.check("phonetic/morphology face: NLTK's MORPHOLOGICAL_SUBSTITUTIONS has 25 regular suffix rules (n/v/a/r/s)", nrules == 25, f"{nrules}")
L.check("…plus the .exc exception lists shipped at /usr/share/wordnet/{noun,verb,adj,adv}.exc", all(os.path.exists(f"/usr/share/wordnet/{p}.exc") for p in ("noun", "verb", "adj", "adv")))
L.check("relational face: raw source text present as VAPMIP/english_corpus.txt", os.path.exists(os.path.join(VAPMIP, "english_corpus.txt")))
L.check("relational face: monad_english.bin is NOT built in this round (page: 'not built this round')", not os.path.exists(os.path.join(VAPMIP, "monad_english.bin")), "absent, as the page says")
L.prose("None of the three faces is merged; 'one structure to poll, not the historical two-file split' is a plan recorded before building")"""),
]
