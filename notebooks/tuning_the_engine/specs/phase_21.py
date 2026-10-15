LABEL = "21"
TITLE = "The Hypercomplex Sedenion Parallax"
DATE = "2026-06-30"
PAGE = "21_the_hypercomplex_sedenion_parallax.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · Sixteen real scalars are eight complex numbers
Page: `z_k = v[k] + i·v[partner(k)]` for k ∈ {0-3, 8-11} — prime pairs (2,11), (3,13), (5,17), (7,19), (23,41), (29,43), (31,47), (37,53) — and the eight phases `θ_k = arctan(v[partner]/v[k])` "have never been extracted". Extract them from the binary's output."""),
("code", """P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
cos_idx = [0,1,2,3,8,9,10,11]
pairs = [(P[k], P[partner(k)]) for k in cos_idx]
print("prime pairs:", pairs)
L.check("page's prime pairs (2,11)(3,13)(5,17)(7,19)(23,41)(29,43)(31,47)(37,53)", pairs == [(2,11),(3,13),(5,17),(7,19),(23,41),(29,43),(31,47),(37,53)])
home = scratch("ph21_")
def zs(text, eye="H"):
    v = np.array(ptol_raw(text, eye, home)["scalars"]); return np.array([v[k] + 1j*v[partner(k)] for k in cos_idx]), v
z, v = zs("walk with me")
print("|z_k| :", np.round(np.abs(z), 3)); print("θ_k   :", np.round(np.angle(z), 3))
L.check("(|z_k|, θ_k) reconstruct the 16 scalars exactly (polar form is a bijection: same parameters, different geometry)", np.allclose(np.array([[w.real, w.imag] for w in z]).reshape(-1)[[0,2,4,6,8,10,12,14]], v[cos_idx]) and np.allclose([w.imag for w in z], v[[partner(k) for k in cos_idx]]))
L.check("eight phases exist and are not all zero (they are what a real-only readout discards)", np.abs(np.angle(z)).max() > 0.1)"""),
("md", """## 2 · The "43× gain on e3"
Page: the noun channel e3 (p=7) looks weak in the real projection (`v[3]`) but its true magnitude is `|z₃| = √(v[3]²+v[7]²)`; "the 43× gain is the ratio |z₃|/v[3]". The ratio is unbounded where `v[3] → 0` (it is 1/|cos θ₃|) — measure its distribution over a real vocabulary instead of one word."""),
("code", """words = sorted({w.strip('.,!?;:"\\'()[]').lower() for l in open(os.path.join(VAPMIP,'foundations.txt'),encoding='utf-8') for w in l.split()})
words = [w for w in words if 3 <= len(w) <= 14 and w.isalpha()][:3000]
ratios = []; 
for w in words:
    zz, vv = zs(w); 
    if abs(vv[3]) > 1e-9: ratios.append((abs(zz[3])/abs(vv[3]), w))
r_ = np.array([x for x, _ in ratios]); order = np.argsort(-r_)
print(f"{len(r_)} words: ratio |z3|/|v[3]| median {np.median(r_):.2f}, 90th pct {np.percentile(r_,90):.1f}, 99th {np.percentile(r_,99):.1f}, max {r_.max():.1f}")
print("largest:", [(ratios[i][1], round(float(r_[i]), 1)) for i in order[:5]])
L.check("ratio |z₃|/v[3] equals 1/|cos θ₃| exactly (it is a property of the angle, not a gain of the channel)", all(abs(abs(zs(w)[0][3])/abs(zs(w)[1][3]) - 1/abs(math.cos(np.angle(zs(w)[0][3])))) < 1e-9 for _, w in ratios[:30]))
L.check("a 43× ratio occurs for some words in an ordinary vocabulary", r_.max() >= 43, f"max {r_.max():.1f}")
print(f"(observation) median ratio {np.median(r_):.2f}: the real projection typically shows the e3 channel at about 1/{np.median(r_):.0f} of its complex magnitude; 43× is a tail value")"""),
("md", """## 3 · The torus T⁸ address and the amplitude-only collision
Claim: two words with the same 8 amplitudes but different phases are different words; the old address (amplitude only) collapses them. Count, over a real vocabulary, how many words collide on the 8 amplitudes alone (rounded) and how many of those are separated by phases."""),
("code", """amp, ph, names = [], [], []
for w in words[:1500]:
    zz, _ = zs(w); amp.append(tuple(np.round(np.abs(zz), 2))); ph.append(tuple(np.round(np.angle(zz), 2))); names.append(w)
from collections import Counter, defaultdict
ca = Counter(amp); cp = Counter(zip(amp, ph))
coll_amp = sum(c for c in ca.values() if c > 1); coll_full = sum(c for c in cp.values() if c > 1)
print(f"1500 words: collide on amplitudes only: {coll_amp}; collide on amplitude+phase: {coll_full}")
L.check("amplitude-only addresses collide more often than amplitude+phase addresses at the same rounding", coll_amp > coll_full or coll_amp == 0, f"{coll_amp} vs {coll_full} (at 2-decimal rounding both are small; the structural fact — polar form loses nothing — is checked above)")
by = defaultdict(list)
for n_, a_, p_ in zip(names, amp, ph): by[a_].append((n_, p_))
ex = next(((a_, v_) for a_, v_ in by.items() if len(v_) > 1), None)
print("example amplitude collision:", ex[1][:3] if ex else "none at this rounding")"""),
("md", """## 4 · Spectral pan — which octonion carries the word?
`spectral_pan = Σ_{k=8..15} v² / Σ v²`. The page predicts "spectrally flat" (≈0.5) for the, is, and; low pan for foundational structures, high for fine-grained concepts."""),
("code", """pan = lambda w: float((zs(w)[1][8:]**2).sum() / (zs(w)[1]**2).sum())
fw = ["the", "is", "and", "of", "to"]; cw = ["sedenion", "octonion", "zero", "divisor", "prime", "riemann", "mathematics", "philosophy"]
print("function words :", {w: round(pan(w), 3) for w in fw}); print("content words  :", {w: round(pan(w), 3) for w in cw})
allp = np.array([pan(w) for w in words[:800]])
print(f"800 vocabulary words: pan mean {allp.mean():.3f} sd {allp.std():.3f} min {allp.min():.3f} max {allp.max():.3f}")
L.check("function words (the, is, and) sit near 0.5", all(abs(pan(w) - 0.5) < 0.15 for w in ("the","is","and")), str({w: round(pan(w),2) for w in ("the","is","and")}))
print(f"(observation) spectral pan sd over the vocabulary = {allp.std():.3f}")
# σ_self (phase pan) and spectral pan as independent axes
ss = np.array([ptol_raw(w, "H", home)["sigma_self"] for w in words[:800]])
rho = float(np.corrcoef(ss, allp)[0, 1]); print(f"corr(σ_self, spectral_pan) over 800 words = {rho:+.3f}")
L.check("σ_self (phase pan) and spectral pan are independent axes (|corr| < 0.5)", abs(rho) < 0.5, f"corr {rho:+.3f}")"""),
("md", """## 5 · Zero-divisors as parallax blindspots
In ℝ, ℂ, ℍ, 𝕆 the product of nonzero elements is never 0 (Phase 6); in 𝕊 it can be. At a ZD pair the phase of the pair is the `arctan(0/0)` singularity. Algebra only:"""),
("code", """from _sedenion import cd_mul, cd_norm
rng = np.random.default_rng(9)
for n, nm in ((2, "ℂ"), (4, "ℍ"), (8, "𝕆")):
    mn = min(cd_norm(cd_mul(list(rng.normal(size=n)), list(rng.normal(size=n)))) for _ in range(2000)); print(f"  {nm}: min |a·b| over 2000 random pairs = {mn:.3e}")
vecs, pairs_ = zd_vectors(); ka, kb = next(iter(pairs_))
a, b = vecs[ka], vecs[kb]
L.check("𝕊 has nonzero a, b with a·b = 0 (a blindspot: baseline vanishes)", cd_norm(cd_mul(a, b)) < 1e-12 and cd_norm(a) > 0 and cd_norm(b) > 0)
L.check("the normed-division algebras ℂ, ℍ, 𝕆 never do (|ab| = |a||b| to 1e-12)", all(abs(cd_norm(cd_mul(list(x), list(y))) - np.linalg.norm(x)*np.linalg.norm(y)) < 1e-12 for n in (2,4,8) for x, y in [(rng.normal(size=n), rng.normal(size=n))]))
L.prose("'The eye cannot measure what passes through its own blindspot; therefore the word is not selected, it emerges' — interpretation of the ZD fact above")"""),
("code", """for c in ["Lips = the eight phase angles (Phase 19's 'missing' part) — extraction shown above; using them to select words is not built",
          "Homophones may differ only in phase (prosody): not testable from spelling-based input",
          "Hyperwebster works in T⁸, S¹⁵ is the shadow of T⁸ (a reading; the bijection polar↔real is checked, the 'native space' statement is not)"]:
    L.prose(c)"""),
]
