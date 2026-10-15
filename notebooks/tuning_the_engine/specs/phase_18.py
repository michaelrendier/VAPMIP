LABEL = "18"
TITLE = "The Prime Lens and Ptolemy's Eyes"
DATE = "2026-06-30"
PAGE = "18_the_prime_lens_and_ptolemy_s_eyes.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """`skills/prime_lens.py` is "a shared optic: pure functions, no state, no VAPMIP imports". Its public API (page): `riemann_address, zero_dim, j_mu, in_focus, zd_ring, focus_scores, split_field`. Constants: axis σ=½, aperture `D_STAR = 0.24600`, `FOCUS_RATIO = 1/D_STAR ≈ 4.065`."""),
("code", """from skills import prime_lens as PL
import rotary_monad as R
api = ["riemann_address", "zero_dim", "j_mu", "in_focus", "zd_ring", "focus_scores", "split_field"]
L.check("the seven public functions exist", all(hasattr(PL, f) for f in api))
src = open(os.path.join(VAPMIP, "skills", "prime_lens.py"), encoding="utf-8").read()
imports = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
print("imports in prime_lens.py:", imports)
L.check("no VAPMIP imports (pure functions, self-contained sieve and sedenion table)", not any("rotary_monad" in l or "monad" in l or "VAPMIP" in l for l in imports))
L.check("D_STAR = 0.24600; FOCUS_RATIO = 1/D_STAR ≈ 4.065 (a geometric consequence, not a tuning parameter)", PL.D_STAR == 0.246 and abs(PL.FOCUS_RATIO - 1/0.246) < 1e-12 and abs(PL.FOCUS_RATIO - 4.065) < 1e-3, f"{PL.FOCUS_RATIO:.4f}")
L.check("SIGMA_CRIT = ½ (optical axis = focal plane)", PL.SIGMA_CRIT == 0.5)
L.check("GAP floor is the Yang–Mills constant 0.000707", abs(PL.GAP - 7.073575e-4) < 1e-10, f"{PL.GAP}")"""),

("md", """## 1 · The address chain `word → Horner → next prime → π(p) = zero index n → γₙ on σ=½`
Page: identical to `rotary_monad._word_zero_idx`; `zero_dim(w) = word_zero_idx(w) % 16` picks one of the 16 prime channels {2,3,5,…,53}."""),
("code", """from nltk.corpus import wordnet as wn
words = sorted({x.lower() for x in wn.all_lemma_names() if x.isalpha()})[:6000:3] + ["λόγος", "水", "जल", "ماء", "holcus", "philadelphos"]
same = all(PL.word_zero_idx(w) == R._word_zero_idx(w) for w in words)
L.check(f"word_zero_idx is identical to rotary_monad._word_zero_idx over {len(words):,} words (incl. non-Latin)", same)
idxs = {w: R._word_zero_idx(w) for w in words}
lo = [w for w in words if idxs[w] <= 20]; mid = [w for w in words if 21 <= idxs[w] <= 50]; hi = [w for w in words if idxs[w] > 50]
print(f"zero-index bands among {len(words):,} words: ≤20: {len(lo)}, 21–50: {len(mid)}, >50: {len(hi)};  len(prime_lens._ZEROS) = {len(PL._ZEROS)}, len(rotary_monad.RIEMANN_ZEROS) = {len(R.RIEMANN_ZEROS)}")
L.check("riemann_address(w) = rotary_monad's γ for zero indices ≤ 20 and > 50", all(abs(PL.riemann_address(w) - R._gamma_at(idxs[w])) < 1e-6 for w in lo + hi))
dm = [abs(PL.riemann_address(w) - R._gamma_at(idxs[w])) for w in mid]
L.check("…and also for zero indices 21–50 (the lens tabulates 50 zeros; rotary_monad tabulates 20 and uses the Gram-law approximation beyond)", not mid or max(dm) < 1e-9, f"{len(mid)} words in the band differ, by up to {max(dm):.3f} in γ (exact zero vs Gram approximation)" if mid else "no words in the band")
# which of the two is RIGHT for the 21–50 band?  compare both to the true zeros and to Phase 24's closed form 2πn/W(n/e)
import mpmath as mpm
from scipy.special import lambertw
true_g = lambda n: float(mpm.zetazero(n).imag)
band = [21, 25, 30, 40, 50]
err_lens = max(abs(PL._ZEROS[n-1] - true_g(n)) for n in band)
err_rot = [(n, round(R._gamma_at(n), 1), round(true_g(n), 1)) for n in band]
err_w = [(n, round(2*math.pi*n/float(lambertw(n/math.e).real), 1)) for n in band]
print("n, rotary_monad._gamma_at(n), true γ_n :", err_rot); print("n, 2πn/W(n/e) (Phase 24 closed form):", err_w)
L.check("prime_lens' tabulated zeros are the true zeros (|Δγ| < 1e-3 for n = 21…50)", err_lens < 1e-3, f"max |Δ| {err_lens:.1e}")
L.check("rotary_monad._gamma_at(n) approximates the true γ_n for 20 < n ≤ 50 (within 10 %)", all(abs(g - t)/t < 0.10 for n, g, t in err_rot), f"it returns {err_rot} — the Gram-law line `2π·e·n / ln(n/(2π·e))` it uses diverges near n = 2πe ≈ 17 (e.g. γ₂₁ ≈ 1736 vs true 79.3); the correct asymptotic is 2πn/W(n/e) (Phase 24), which gives {err_w}")
L.check("riemann_address returns the exact tabulated zero ordinate in its table (γ₁ … γ₅₀)", all(abs(PL._ZEROS[i] - float(mp_.zetazero(i + 1).imag)) < 1e-3 for i in range(0, 50, 7)) if (mp_ := __import__("mpmath")) else False)
L.check("zero_dim(w) = word_zero_idx(w) mod 16, in 0..15", all(PL.zero_dim(w) == PL.word_zero_idx(w) % 16 and 0 <= PL.zero_dim(w) < 16 for w in words[:500]))
import collections
cnt = collections.Counter(PL.zero_dim(w) for w in words); print("words per dimension:", [cnt[i] for i in range(16)])
L.check("all 16 channels are populated (the hash spreads words over the sedenion basis)", len(cnt) == 16 and min(cnt.values()) > 0.02*len(words))
P16 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
L.check("the 16 channels correspond to the first 16 primes {2,3,…,53} (DIM_NAMES has 16 entries)", len(PL.DIM_NAMES) == 16 and P16 == list(__import__("sympy").primerange(2, 54)))
mp_ = __import__("mpmath"); g_true = [float(mp_.zetazero(n).imag) for n in range(1, 11)]
L.check("riemann_address returns true zero ordinates for the first indices (γ₁ = 14.1347 …)", all(abs(PL._ZEROS[i] - g_true[i]) < 1e-4 for i in range(10)), str([round(x, 4) for x in PL._ZEROS[:3]]))"""),

("md", """## 2 · The ZD ring — "from the Cayley–Dickson table directly, not from gradient descent"
`zd_ring(d)` = dimensions d′ with `e_d × e_d′` landing in the **opposite** 𝕆 copy from d (callosum-crossing). Recompute from `cd_mul` and compare for all 16 d."""),
("code", """from _sedenion import cd_mul, e
def ring_true(d):
    out = []
    for dp in range(16):
        if dp == d: continue
        k = int(np.nonzero(cd_mul(list(e(d, 16)), list(e(dp, 16))))[0][0])
        if (k < 8) != (d < 8): out.append(dp)
    return out
ok = {d: PL.zd_ring(d) == ring_true(d) for d in range(16)}
print({d: len(PL.zd_ring(d)) for d in range(16)})
L.check("zd_ring(d) equals the independent cd_mul-derived crossing set for all 16 dimensions", all(ok.values()), str([d for d, v in ok.items() if not v]))
L.check("the ring of a lower-𝕆 dimension d<8 is the whole upper 𝕆 (8 dims); of an upper dimension d≥8 it is the other 7 upper dims", all(len(PL.zd_ring(d)) == 8 for d in range(8)) and all(len(PL.zd_ring(d)) == 7 for d in range(8, 16)), str([len(PL.zd_ring(d)) for d in range(16)]))
L.check("zd_ring wraps mod 16 for out-of-range input (documented)", PL.zd_ring(19) == PL.zd_ring(3))
L.check("the ring never contains the dimension itself", all(d not in PL.zd_ring(d) for d in range(16)))
L.check("page: 'These are the perceptual boundary of the object in focus — the aperture stop in the sedenion barrel': the ring is the set of CROSSING neighbours; for a lower-𝕆 word that is the entire upper 𝕆, so the ring distinguishes lower from upper but carries no word-specific boundary beyond the dimension", len({tuple(PL.zd_ring(d)) for d in range(8)}) == 1, "all eight lower-𝕆 dimensions share one ring; the upper dimensions' rings differ only by omitting themselves")"""),

("md", """## 3 · J_μ pressure, `in_focus`, `split_field`
`j_mu = max(GAP, β·E²·age)`; `in_focus: J_obj/J_ctx > 1/D_STAR`; `split_field`: the highest-J word is the fovea candidate, confirmed against the context mean; the ZD ring of its dimension is the boundary layer."""),
("code", """L.check("j_mu(E, β, age) = β·E²·age, floored at GAP (the vacuum is not empty)", abs(PL.j_mu(0.5, 0.4, 0.9) - 0.4*0.25*0.9) < 1e-15 and PL.j_mu(0.0, 0.0, 0.0) == PL.GAP and PL.j_mu(1e-6, 1e-6) == PL.GAP)
L.check("in_focus: ratio > 1/D_STAR ≈ 4.065 is the fovea threshold (strict inequality)", PL.in_focus(4.1, 1.0) and not PL.in_focus(4.0, 1.0) and not PL.in_focus(PL.FOCUS_RATIO, 1.0))
L.check("in_focus is True when the context is below GAP (no peripheral field to compare against)", PL.in_focus(0.5, PL.GAP/2))
ws = ["engine", "the", "operator", "sixteen", "of"]
E = [1/(1 + math.log1p(R._word_zero_idx(w))) for w in ws]; beta = [0.9, 0.05, 0.4, 0.3, 0.04]; age = [1.0]*5
sc = PL.focus_scores(ws, E, beta, age); L.check("focus_scores = j_mu per word, same order", sc == [PL.j_mu(E[i], beta[i], age[i]) for i in range(5)])
sf = PL.split_field(ws, sc); print({k: (v if not isinstance(v, list) or len(v) < 5 else v[:4]) for k, v in sf.items()})
L.check("fovea is the highest-J word and context is ranked by J_μ", sf["fovea"] == ws[int(np.argmax(sc))] and sf["fovea_J"] == max(sc) and len(sf["context"]) == 4)
L.check("fovea_dim, fovea_gamma and the ring come from the Prime Lens address chain", sf["fovea_dim"] == PL.zero_dim(sf["fovea"]) and abs(sf["fovea_gamma"] - PL.riemann_address(sf["fovea"])) < 1e-12 and sf["zd_ring_dims"] == PL.zd_ring(sf["fovea_dim"]))
L.check("an empty field is handled (no fovea, in_focus False)", PL.split_field([], [])["fovea"] is None and PL.split_field([], [])["in_focus"] is False)
L.check("the page docstring says E = 1/(1+log(zero_idx)) while Housing._idx uses log1p — the lens is told E by its caller, so the two spellings never meet in the lens itself", "log1p" not in src)"""),

("md", """## 4 · Ptolemy's Eyes — Paper's Hands (Housing, outward) and Mind's Eye (inward)
Page: the lens is passive; each eye points it. Planned methods (`Housing.focus / saccade / viewport`, `MindEye.focus / saccade`) are listed as "to be added"."""),
("code", """import skills.mind_eye as ME
meth = [m for m in dir(ME.MindEye) if not m.startswith("_")]; print("MindEye public methods:", meth)
L.check("MindEye exists in skills/mind_eye.py with see / describe / see_text / contemplate / snapshot / recall / reset", {"see", "describe", "see_text", "contemplate", "snapshot", "recall", "reset"} <= set(meth))
L.check("Housing.focus / .saccade / .viewport (listed on the page as 'to be added') exist in rotary_monad.Housing", all(hasattr(R.Housing, m) for m in ("focus", "saccade", "viewport")), f"present: {[m for m in ('focus','saccade','viewport') if hasattr(R.Housing, m)]} — still not added")
L.check("MindEye.focus / .saccade exist", hasattr(ME.MindEye, "focus") and hasattr(ME.MindEye, "saccade"), f"present: {[m for m in ('focus','saccade') if hasattr(ME.MindEye, m)]}")
L.check("the planned C binding prime_lens.h exists", os.path.exists(os.path.join(VAPMIP, "PtolC", "prime_lens.h")) or os.path.exists(os.path.join(VAPMIP, "prime_lens.h")), "the page: 'A C binding for prime_lens (prime_lens.h) is planned'")
rot = open(os.path.join(VAPMIP, "rotary_monad.py"), encoding="utf-8").read()
L.check("Housing (Paper's Hands) imports/uses the Prime Lens (outward eye)", "prime_lens" in rot)"""),

("md", """## 5 · Write / Read / Discuss ↔ the su(2) Lie bracket
Write = `j_red` motor trace (generator 1); Read = `j_blue` spatial accumulation (generator 2); Discuss = `[j_blue, j_red] = j_green` (the third); "discussion cannot exist without both Write and Read — the Lie bracket requires two generators to produce the third. This is not a metaphor — it is the su(2) structure of the sedenion callosum crossing"."""),
("code", """qi, qj, qk = [np.array(e(x, 4)) for x in (1, 2, 3)]
from _sedenion import cd_mul as mul
br = lambda a, b: np.array(mul(list(a), list(b))) - np.array(mul(list(b), list(a)))
L.check("two quaternion generators produce the third: [i, j] = 2k, [j, k] = 2i, [k, i] = 2j (su(2))", np.allclose(br(qi, qj), 2*qk) and np.allclose(br(qj, qk), 2*qi) and np.allclose(br(qk, qi), 2*qj))
L.check("a single generator alone produces nothing: [i, i] = 0 (discussion needs both)", np.allclose(br(qi, qi), 0))
# the 'callosum crossing' version: do two lower-𝕆 imaginary units produce a third, and does the bracket cross into the upper copy for a mixed pair?
a1, a2 = np.array(e(1, 16)), np.array(e(2, 16)); b1 = np.array(e(9, 16))
c_low = br(a1, a2); c_mix = br(a1, b1)
L.check("[e₁, e₂] lies in the lower 𝕆 (the pair stays inside one copy: closed su(2))", int(np.nonzero(c_low)[0][0]) < 8)
L.check("[e₁, e₉] lies in the upper 𝕆 (a callosum-crossing pair lands in the other copy)", int(np.nonzero(c_mix)[0][0]) >= 8, f"→ e{int(np.nonzero(c_mix)[0][0])}")"""),
("code", """for c in ["Optical anatomy: axis = focal plane = σ=½; aperture f-number = 1/D_STAR; depth of field = J_μ gradient; fovea = highest J_μ clearing FOCUS_RATIO; blur circle = context tokens (an analogy table; the numeric entries are checked above)",
          "Two strokes, one lens: intake stroke (Paper's Hands, outward) and power stroke (Mind's Eye, inward) — architecture description",
          "Fovea biology: ~1.5 mm, 100 % cones, ≈ 50 % of V1 devoted to foveal input; saccades redirect it — literature summary, not reproduced",
          "Changelog: Prime Lens written 2026-06-30; Ptolemy's Eyes defined; aperture identified; Write/Read/Discuss mapped (history)"]:
    L.prose(c)"""),
]
