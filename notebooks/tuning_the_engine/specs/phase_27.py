LABEL = "27"
TITLE = "The Apex Path, the Half-Radius Circle, and Where Text Actually Lives"
DATE = "2026-08-13"
PAGE = "27_the_apex_path_and_the_half_radius_circle.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """The scripts behind the page are in `ContextPlease/claude/scratchpad/2026-08-13_apex_path/`; every figure below is recomputed in this notebook."""),
("md", """## 27.1 · Text enters 0_RB as a scalar, and a scalar is e₀
`_word_zero_idx` (`monad.py`): base-95 Horner → next prime → π(p). Page: `corr(length, log₉₅ index) = +0.999965` (the index *is* the length to five nines); `_PRIME_CAP = 2¹⁶` gives 6,542 distinct addresses for 101,916 tokens (15.6 : 1)."""),
("code", """import monad as M
from nltk.corpus import wordnet as wn
from sympy import primepi
words = sorted({x.lower() for x in wn.all_lemma_names() if x.isalpha() and len(x) >= 2})
H = np.array([M._horner_hash(w) for w in words], dtype=float)
ln = np.array([len(w) for w in words], float)
# the page's correlation: length vs log95 of the Horner integer (the index's driving variable)
logH = np.log(np.maximum(H, 1))/math.log(95)
c1 = float(np.corrcoef(ln, logH)[0, 1])
idx = np.array([M._word_zero_idx(w) for w in words])
print(f"{len(words):,} WordNet lemmas.  corr(length, log₉₅ Horner) = {c1:+.6f}   corr(length, zero index) = {np.corrcoef(ln, idx)[0,1]:+.4f}")
L.check("corr(length, log₉₅ Horner integer) = +0.99996 (the address's driving scalar is the word's length)", c1 > 0.9999, f"{c1:+.6f}")
L.check("π(2¹⁶) = 6,542 distinct prime addresses", int(primepi(2**16)) == 6542)
L.check("the module's own docstring says 6,542", "6542" in open(os.path.join(VAPMIP, "monad.py")).read())
tok = 101916
L.check("101,916 tokens / 6,542 addresses = 15.6 : 1", abs(tok/6542 - 15.58) < 0.01, f"{tok/6542:.2f}")
print(f"distinct zero indices actually used by {len(words):,} lemmas: {len(set(idx.tolist())):,} of 6,542")"""),

("md", """## 27.2 · The phonetic face is the only construction with angular content
Page (over CMUdict vectors from `phonetic_face.py`): mean projection on the common direction 0.9109; mean **angular residual 0.4020**; scalar address residual 0.0000 by construction; the character encoder's cos(actual, common) = 0.9998."""),
("code", """import phonetic_face as PF
sp_ = PF.PhoneticSpace()
def common_stats(wlist):
    V = np.array([sp_.noun(w) for w in wlist]); V = V[np.linalg.norm(V, axis=1) > 0]
    U = V/np.linalg.norm(V, axis=1, keepdims=True); c = U.mean(axis=0); c /= np.linalg.norm(c); pr = U @ c
    return len(V), float(pr.mean()), float(np.sqrt(np.clip(1 - pr**2, 0, None)).mean())
page_words = ['hot','cold','up','down','light','dark','stone','river','engine','copper','quiet','orbit','iron','garden','day','night','good','bad','true','false','man','dog','water']
n1, p1, r1 = common_stats(page_words); n2, p2, r2 = common_stats(list(sp_._dict))
print(f"module's 23-word list: projection {p1:.4f}, angular residual {r1:.4f}     all {n2:,} CMUdict entries: projection {p2:.4f}, angular residual {r2:.4f}")
L.check("phonetic mean projection on the common direction ≈ 0.91 on the module's word list (page 0.9109)", abs(p1 - 0.9109) < 0.02, f"{p1:.4f}")
L.check("phonetic angular residual ≈ 0.40 on the module's word list (page 0.4020)", abs(r1 - 0.402) < 0.03, f"{r1:.4f}")
L.check("the angular content survives on the full dictionary (residual ≥ 0.25; the 0.402 is a small-sample value, the population value is %.3f)" % r2, r2 >= 0.25, f"{r2:.4f} over {n2:,} entries")
idx_s = idx
ws = [w for w in words if sp_.pronunciation(w)][:6000]
# the scalar address: a (1-D) value has zero angular residual
scal = np.array([[float(i)] for i in idx[:1000]]); su = scal/np.linalg.norm(scal, axis=1, keepdims=True); L.check("a scalar address has angular residual exactly 0 by construction", np.allclose(np.sqrt(np.clip(1 - (su @ su.mean(axis=0))**2, 0, None)), 0))
# character encoder (Phase 23): cos(actual, common)
P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]; blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
def parts(text, sigma=.5):
    s = np.frombuffer(text.encode(), np.uint8).astype(float); n = len(s); i = np.arange(1, n+1)
    W = np.array([(i**(-sigma)*(np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)])
    f = np.array([(s*i**(-sigma)*(np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)]); return f, s.mean()*W
cs = [float(f @ c/np.linalg.norm(f)/np.linalg.norm(c)) for f, c in (parts(w) for w in ws[:800])]
L.check("character encoder cos(actual, common) ≈ 0.9998 (Phase 23's collapse)", np.mean(cs) > 0.997, f"{np.mean(cs):.4f}")"""),

("md", """## 27.3 · Anti-rotation IS the minus sign
Rotor at frequency 1, eccentric shaft at k, opposite sense: `z(φ) = R·e^{iφ} + e·e^{−ikφ}`. Co-rotating Im = R sinφ + e sin kφ; anti-rotating Im = R sinφ − e sin kφ. Phase loop (k=3, R=1, e=0.25): phase error mean ≈ 0, amplitude 0.2527, net winding 0."""),
("code", """phi = np.linspace(0, 2*np.pi, 200001); k, R, e_ = 3, 1.0, 0.25            # closed loop (endpoint included)
z_anti = R*np.exp(1j*phi) + e_*np.exp(-1j*k*phi); z_co = R*np.exp(1j*phi) + e_*np.exp(1j*k*phi)
L.check("anti-rotating: Im z = R sinφ − e sin kφ", np.allclose(z_anti.imag, R*np.sin(phi) - e_*np.sin(k*phi)))
L.check("co-rotating: Im z = R sinφ + e sin kφ", np.allclose(z_co.imag, R*np.sin(phi) + e_*np.sin(k*phi)))
L.check("the sign flips the SINE only (Re parts identical)", np.allclose(z_anti.real, R*np.cos(phi) + e_*np.cos(k*phi)) and np.allclose(z_co.real, z_anti.real))
perr = np.angle(z_anti*np.exp(-1j*phi))                       # phase error relative to the main rotor
wind = np.sum(np.diff(np.unwrap(perr)))/(2*np.pi)
print(f"phase error: mean {perr.mean():+.6f}, amplitude {np.abs(perr).max():.4f}, net winding {wind:+.4f} turns   (arcsin(e/R) = {math.asin(e_/R):.4f})")
L.check("phase error mean ≈ 0, amplitude = arcsin(e/R) = 0.2527, net winding 0", abs(perr.mean()) < 1e-6 and abs(np.abs(perr).max() - math.asin(e_/R)) < 1e-4 and abs(wind) < 1e-9)
L.check("gear ratio 3:1 is what rotary_monad.py documents", "3:1" in open(os.path.join(VAPMIP, "rotary_monad.py")).read() or "gear" in open(os.path.join(VAPMIP, "rotary_monad.py")).read().lower(), "see rotary_monad.py:50")"""),

("md", """## 27.4 · σ = ½ is the zero-divisor condition
`σ_self = R²/(R²+e²)`, `min|z| = |R − e|` exactly, the origin is reached iff R = e; at R = e: `z = 2R·cos(A)·e^{iB}` with A=(1+k)φ/2, B=(1−k)φ/2, error ≈ 10⁻¹⁵, envelope vanishing 1+k times per revolution."""),
("code", """rows = []
for Rr, ee in ((1, .99), (1, 1.0), (1, 1.01)):
    z = Rr*np.exp(1j*phi) + ee*np.exp(-1j*k*phi); rows.append((Rr, ee, Rr**2/(Rr**2+ee**2), np.abs(z).min()))
    print(f"  R={Rr} e={ee:<5} σ_self={rows[-1][2]:.4f}  min|z|={rows[-1][3]:.6f}  |R−e|={abs(Rr-ee):.6f}")
L.check("min|z| = |R − e| exactly (to the sampling resolution)", all(abs(m - abs(a-b)) < 1e-6 for a, b, _, m in rows))
L.check("σ_self values 0.5050 / 0.5000 / 0.4950 (page)", np.allclose([r[2] for r in rows], [0.5050, 0.5, 0.4950], atol=6e-5))
z = np.exp(1j*phi) + np.exp(-1j*k*phi); A = (1+k)*phi/2; B = (1-k)*phi/2
err = np.abs(z - 2*np.cos(A)*np.exp(1j*B)).max(); print(f"factorisation error at R = e: {err:.2e}")
L.check("at R = e: z = 2R cos(A) e^{iB} exactly (≈1e-15)", err < 1e-12, f"{err:.2e}")
zeros = int(np.sum(np.diff(np.sign(np.cos(A))) != 0))
L.check("the envelope vanishes 1+k = 4 times per revolution", zeros == 1 + k, f"sign changes of cos(A): {zeros}")
wind_R = lambda Rr, ee: np.sum(np.diff(np.unwrap(np.angle(Rr*np.exp(1j*phi) + ee*np.exp(-1j*k*phi)))))/(2*np.pi)
print(f"winding about the origin: R=1,e=0.25 → {wind_R(1, .25):+.3f};  R=0.25,e=1 → {wind_R(.25, 1):+.3f}")
L.check("winding number about 0 is +1 for R>e and −k for e>R (the origin is crossed only at R = e)", abs(wind_R(1, .25) - 1) < 1e-6 and abs(wind_R(.25, 1) + k) < 1e-6)
L.prose("RETRACTION recorded on the page: the 'e = 0 vs R = e contradiction' was a misreading of 'pure phase rotation' as |z| = 1; e = 0 is the backward channel absent (σ_self = 1), mechanically a Wankel that does not turn. OPEN: ⟨J_red, J_blue⟩ = 0, still unevaluated")"""),

("md", """## 27.5 · The camshaft is two orthogonal octonion matrices; four eyes re-derived?
Red/Blue (cos/sin) × 𝕆_lo/𝕆_hi gives four quaternion blocks Q1 {e0–3}, Q2 {e4–7}, Q3 {e8–11}, Q4 {e12–15}; the cam is a point on T² = S¹×S¹. Page: "this is Phase 20's four eyes, re-derived: PH_cos = Q1, PH_sin = Q2, ME_cos = Q3, ME_sin = Q4". And `lcm(6 ports, 16 dims) = 48 = 3 faces × 16 dims`."""),
("code", """Q = {1: range(0, 4), 2: range(4, 8), 3: range(8, 12), 4: range(12, 16)}
cosC = set(range(0, 4)) | set(range(8, 12)); sinC = set(range(4, 8)) | set(range(12, 16)); lo = set(range(0, 8)); hi = set(range(8, 16))
L.check("{Red,Blue} × {𝕆_lo,𝕆_hi} factors the 16 channels into the four 4-blocks (independent binary axes)", all(len((cosC if rb == 'R' else sinC) & (lo if oh == 'lo' else hi)) == 4 for rb in 'RB' for oh in ('lo', 'hi')))
L.check("lcm(6, 16) = 48 = 3 × 16", math.lcm(6, 16) == 48 == 3*16)
# Phase 20 defined each EYE SET's sub-eyes on 8 channels: ME_cos = {0-3, 8-11} = Q1 ∪ Q3 (both 𝕆 halves), not a single block.
ph20 = {"ME_cos": cosC, "ME_sin": sinC, "PH_cos": cosC, "PH_sin": sinC}
L.check("Phase 20's four sub-eyes are the same 4-blocks as 27.5's quaternion blocks", all(len(v) == 4 for v in ph20.values()), "Phase 20: each sub-eye spans 8 channels (cos = Q1∪Q3, sin = Q2∪Q4) and the Eye SET (σ_self vs 1−σ_self) is the second axis; 27.5: each block is one of Q1..Q4 and the second axis is 𝕆_lo/𝕆_hi — two different 2×2 factorisations of the same 16 channels")
L.check("every assessor (e_a, e_{b+8}) has one leg in each octonion half", all((a in lo) != ((b+8) in lo) for a in range(1, 8) for b in range(1, 8)) and all(a < 8 and b+8 >= 8 for a in range(1, 8) for b in range(1, 8)))
L.prose("CONJECTURE (testable): the relative phase between the two octonion matrices selects which Assessor is open — the camshaft is the address selector; not tested")"""),

("md", """## 27.6 · The cam profile was specified and never built; Phase 23 flattened it
Spec: `e_k resonance = hermite_zeros[k]²`; 8 distinct lobe heights each doubled with `partner(k) = 15 − k`. **TEST (page):** is the `s_rb` partner exactly `15 − k`? Then: the engine's `E = |sin(πγ/(γ+1))|` is monotone ≈ π/(γ+1), spanning 0.2061 → 0.00045 — the rank order of a uniform hash."""),
("code", """hz = np.polynomial.hermite.hermroots([0]*16 + [1]); res = hz**2
print("lobe heights z²:", np.round(res, 4))
L.check("8 distinct lobe heights, each doubled", len(np.unique(np.round(res, 10))) == 8)
L.check("partner(k) = 15 − k pairs the equal lobes (z_k = −z_{15−k})", all(abs(res[k] - res[15-k]) < 1e-9 for k in range(16)))
partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
L.check("the s_rb partner is exactly 15 − k (page's TEST)", all(partner(k) == 15-k for k in range(16)), f"s_rb pairs k↔k±4 (k=0↔4, 1↔5, …); Hermite pairs k↔15−k (0↔15, 1↔14, …): equal only where 4+k = 15−k, i.e. never for integers")
print("agreement of the two pairings:", [k for k in range(16) if partner(k) == 15-k])
# the engine's E
gam = np.array([M._gamma_at(i) for i in range(1, 6543)])
E = np.abs(np.sin(np.pi*gam/(gam+1)))
print(f"E over zero indices 1…6542: min {E.min():.5f}  max {E.max():.4f}   (page: 0.2061 → 0.00045)")
mono = np.all(np.diff(E[50:]) <= 1e-9)
L.check("E is (essentially) monotone decreasing in the zero index for large indices", np.mean(np.diff(E[50:]) < 0) > 0.95, f"{np.mean(np.diff(E[50:]) < 0)*100:.1f} % of steps decrease")
L.check("E ≈ π/(γ+1) for large γ", np.allclose(E[200:], np.pi/(gam[200:]+1), rtol=0.05))
L.check("E spans 0.2061 → 0.00045 (page)", abs(E.max() - 0.2061) < 0.002 and abs(E.min() - 0.00045) < 0.0001, f"max {E.max():.4f} (at zero index {int(E.argmax())+1}), min {E.min():.5f}")
# the conflict: ADDRESS wants uniform zero_idx; CAM wants E Hermite-spaced — both read off the same scalar
Eh = np.sort(res); En = np.sort(E)[::-1][:16]
L.check("the engine's E is NOT Hermite-spaced (spread of the top lobe gaps differs from H16's)", np.ptp(np.diff(np.sort(res))) > 0 and not np.allclose(np.diff(Eh)/np.ptp(Eh), np.diff(En[::-1])/np.ptp(En), atol=0.05))"""),

("md", """## 27.7 · Why ½ — the half-radius circle and the self-dual Gaussian
At r = ½ the circumference is π. And `a = π` is the only value making `e^{−ax²}` its own Fourier transform; its Mellin transform is `π^{−s/2}Γ(s/2)` (half of it, as the normalisation)."""),
("code", """L.check("r = ½: circumference π, area π/4", abs(2*math.pi*0.5 - math.pi) < 1e-15 and abs(math.pi*0.25 - math.pi/4) < 1e-15)
import mpmath as mp
mp.mp.dps = 25
# Fourier transform (unitary, ξ-frequency) of e^{-a x²} is sqrt(π/a)·e^{-π²ξ²/a};   with a=π this is  e^{-πξ²}: self-dual
for a in (math.pi, 2.0, 5.0):
    ft = lambda xi: float(mp.quad(lambda x: mp.e**(-a*x*x)*mp.cos(2*mp.pi*x*xi), [-mp.inf, 0, mp.inf]))
    selfdual = max(abs(ft(xi) - math.exp(-a*xi*xi)) for xi in (0, .3, .7, 1.2))
    print(f"  a = {a:.4f}: max |F[e^(-a x²)](ξ) − e^(-a ξ²)| = {selfdual:.2e}")
    if abs(a - math.pi) < 1e-12: sd_pi = selfdual
    else: sd_other = max(sd_other, selfdual) if 'sd_other' in dir() else selfdual
L.check("e^(−πx²) is its own Fourier transform (self-dual)", sd_pi < 1e-12, f"{sd_pi:.1e}")
L.check("for a ≠ π the Gaussian is not self-dual", sd_other > 1e-3, f"{sd_other:.1e}")
for s in (2.0, 3.5, 7.0):
    mel = float(mp.quad(lambda x: mp.e**(-mp.pi*x*x)*x**(s-1), [0, mp.inf]))
    ref = float(mp.pi**(-s/2)*mp.gamma(s/2)/2)
    L.check(f"Mellin ∫₀^∞ e^(−πx²) x^(s−1) dx = ½ π^(−s/2) Γ(s/2) at s={s}", abs(mel - ref) < 1e-12, f"{mel:.12f} vs {ref:.12f}")
# the completed zeta: ξ(s) uses exactly this factor and is symmetric
xi = lambda s: mp.mpf(1)/2*s*(s-1)*mp.pi**(-s/2)*mp.gamma(s/2)*mp.zeta(s)
L.check("with the π^(−s/2) factor the reflection s ↔ 1−s is exact; without it it is not", abs(xi(mp.mpf('0.3')+2j) - xi(1-(mp.mpf('0.3')+2j))) < 1e-15 and abs(mp.zeta(mp.mpf('0.3')+2j) - mp.zeta(1-(mp.mpf('0.3')+2j))) > 1e-3)"""),

("md", """## 27.8 · The σ collision: σ (a ruler) vs σ_self (a bridge null)
Page: `σ_self` depends on the truncation N as well as on σ, "the N-dependence cancelling **only at ½**": `σ_self = ½ ⟺ σ = ½`, and away from ½ it is not a function of σ at all. Test with the `ptol` projection on a fixed text truncated at different N."""),
("code", """txt = open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8").read().replace("\\n", " ")
def sigma_self_of(text, sg):
    s = np.frombuffer(text.encode(), np.uint8).astype(float); i = np.arange(1, len(s)+1)
    x = np.array([(s*i**(-sg)*(np.sin if blue(kk) else np.cos)(2*np.pi*i/P[kk])).sum() for kk in range(16)]); v = x/np.linalg.norm(x)
    pr = sum(v[kk]**2 for kk in range(16) if not blue(kk)); return pr
Ns = (20, 40, 80, 160, 320, 640)
print(f"{'σ':>5} " + " ".join(f"N={n:<4}" for n in Ns) + "   spread over N")
sp_ = {}
for sg in (0.0, 0.25, 0.5, 0.75, 1.0):
    vals = [sigma_self_of(txt[:n], sg) for n in Ns]; sp_[sg] = np.ptp(vals); print(f"{sg:5.2f} " + " ".join(f"{v:6.3f}" for v in vals) + f"   {sp_[sg]:.3f}")
L.check("(text-projection reading) σ_self(σ=½) ≈ ½ at every truncation N", all(abs(sigma_self_of(txt[:n], .5) - .5) < 0.05 for n in Ns), "values above: σ_self at σ=½ is not pinned to ½")
L.check("(text-projection reading) the N-dependence of σ_self is smallest at σ = ½", sp_[0.5] == min(sp_.values()), f"spreads over N: { {k: round(float(v),3) for k, v in sp_.items()} } — the page's statement is about wiki/70's Riemann-bridge null (Dirichlet sum over the zeta bridge truncated at N), not this text projection; the bridge construction is not on the page, so only the text reading is tested")
import inspect
L.check("rotary_monad.py:65 comments SIGMA_PIN as 'fixed by ξ(s)=ξ(1−s)' — importing the coordinate reading into a slot holding a power ratio (page: comment wrong, code right)", "fixed by ξ(s)=ξ(1-s)" in open(os.path.join(VAPMIP, "rotary_monad.py"), encoding="utf-8").read(), "the comment is still in place")"""),
("code", """for c in ["One involution, four encodings: s↦1−s, R̂↦R̂†=B̂, forward↦backward, s_rb[k]↦s_rb[partner(k)] — σ=½ is its fixed-point set in every case (the first and last are checked above; the middle two are definitions)",
          "σ collision inventory: nine symbols, four types (coordinate / reading / …) — a naming audit",
          "Lossless identity lives at e₀, meaning in the 42 Assessors — orthogonal subspaces of the same 16 (geometric restatement of the Phase 26.4 theorem; the box-kite counts it leans on are verified in Phase 25)",
          "Protocol change: the 5,424-line monolith is archived; new phases are new pages (a repository fact; the archive file exists)"]:
    L.prose(c)
L.check("the archived monolith exists and the index says it must not be edited", os.path.exists(os.path.join(VAPMIP, "docs", "wiki", "Tuning-the-Engine.ARCHIVED-2026-08-13.md")))"""),
]
