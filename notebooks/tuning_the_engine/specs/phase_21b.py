LABEL = "21b"
TITLE = "Correction: cos is the Observer, sin is the Content Frame"
DATE = "2026-06-30 (addendum to Phase 21)"
PAGE = "21b_correction_cos_is_the_observer_sin_is_the_content.md"
BYLINE = "correction by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · The frame inversion is an exact change of variables
Phase 21: `z_k = cos_k + i·sin_k`, `θ_k = arctan(sin/cos)`. Phase 21b: `z'_k = sin_k + i·cos_k`, `θ'_k = arctan(cos/sin)`. Then `θ'_k = π/2 − θ_k` and `z' = i·conj(z)`. Check on real projections, and check that the Mind's Eye (σ_self < ½) is the sin-dominant, "content-frame" side."""),
("code", """P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
cos_idx = [0,1,2,3,8,9,10,11]
home = scratch("ph21b_")
def pair_vals(text, eye="H"):
    v = np.array(ptol_raw(text, eye, home)["scalars"]); return np.array([v[k] for k in cos_idx]), np.array([v[partner(k)] for k in cos_idx]), v
c, s_, v = pair_vals("walk with me")
z_old, z_new = c + 1j*s_, s_ + 1j*c
th_old, th_new = np.angle(z_old), np.angle(z_new)
print("θ (observer frame):", np.round(th_old, 3)); print("θ' (content frame):", np.round(th_new, 3))
L.check("z' = i·conj(z)  (the inversion is a reflection + quarter turn, nothing lost)", np.allclose(z_new, 1j*np.conj(z_old)))
L.check("|z'| = |z|  (amplitudes unchanged)", np.allclose(np.abs(z_new), np.abs(z_old)))
L.check("θ' = π/2 − θ  (mod 2π)", np.allclose(np.exp(1j*th_new), np.exp(1j*(np.pi/2 - th_old))))"""),
("md", """## 2 · Which frame dominates where? σ < ½, = ½, > ½
Page: σ<½ ⇒ sin>cos ⇒ content frame (Mind's Eye); σ=½ ⇒ neither ⇒ conservation; σ>½ ⇒ cos>sin ⇒ observer frame (Paper's Hands). With σ_self = P_cos/(P_cos+P_sin) this is a restatement — verify on 200 sentences at Eye H and its conjugate, and look for prompts that sit at σ_self ≈ ½ to examine the "θ = π/4 for balanced dimensions" claim."""),
("code", """sents = [l.strip() for l in open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8") if 15 <= len(l.strip()) <= 120][:200]
res = []
for s0 in sents:
    for eye in "RCHOS":
        r = ptol_raw(s0, eye, home); res.append((s0, eye, r["sigma_self"], np.array(r["scalars"])))
frame_ok = all((r[2] < .5) == (np.sum(r[3][[k for k in range(16) if blue(k)]]**2) > np.sum(r[3][[k for k in range(16) if not blue(k)]]**2)) for r in res)
L.check("σ_self < ½ ⇔ sin power > cos power (content frame dominates), for 1000 (sentence, Eye) readings", frame_ok)
near = [r for r in res if abs(r[2] - 0.5) < 0.02]
print(f"readings with σ_self within 0.02 of ½: {len(near)} of {len(res)}")
L.check("balanced readings (σ_self ≈ ½) exist in this corpus to test the 'θ = π/4' claim", len(near) >= 5, f"{len(near)}")
if near:
    th = np.concatenate([np.arctan2(np.array([r[3][partner(k)] for k in cos_idx]), np.array([r[3][k] for k in cos_idx])) for r in near])
    print(f"phase angles θ_k at balanced readings: mean |θ| = {np.abs(th).mean():.3f} rad, sd {th.std():.3f}; π/4 = {math.pi/4:.3f}")
    L.check("at σ_self ≈ ½ every dimension sits at |θ_k| = π/4 (page: 'for balanced dimensions arctan(1)')", np.all(np.abs(np.abs(th) - math.pi/4) < 0.05), f"|θ| ranges {np.abs(th).min():.2f} … {np.abs(th).max():.2f}: total power is balanced, individual pairs are not")"""),
("md", """## 3 · The Wick-rotation flag is the same flip
Phase 1: `-W` uses `cos(γ/2 − π/2) = +sin(γ/2)`, `-h` uses `cos(γ/2)`. Frame flip = a quarter-turn shift in the argument."""),
("code", """g = np.linspace(0, 40, 4001)
L.check("cos(γ/2 − π/2) = sin(γ/2) for all γ (the -W gate is the observer→content flip)", np.allclose(np.cos(g/2 - np.pi/2), np.sin(g/2)))
L.check("cos² + sin² = 1 at every γ (no frame is lost)", np.allclose(np.cos(g/2)**2 + np.sin(g/2)**2, 1))"""),
("md", """## 4 · Bell's inequality — what the exact numbers are
The page says Bell's "hidden angle" is the observer/content parallax θ_k and that the CHSH violation is the angle being nonzero. The standard facts are exact and cheap to verify: every deterministic local hidden-variable strategy has CHSH S ≤ 2 (enumerate all 16), while the singlet gives 2√2 at the standard angles."""),
("code", """import itertools
best = 0
for a0, a1, b0, b1 in itertools.product([1, -1], repeat=4):            # all 16 deterministic LHV strategies
    S = a0*b0 + a0*b1 + a1*b0 - a1*b1; best = max(best, abs(S))
print("max |S| over all 16 deterministic local strategies:", best)
E = lambda x, y: -math.cos(x - y)                                        # singlet correlation
a0, a1, b0, b1 = 0, math.pi/2, math.pi/4, -math.pi/4
S_q = E(a0, b0) + E(a0, b1) + E(a1, b0) - E(a1, b1)
print(f"quantum singlet CHSH S = {S_q:.6f}   (2√2 = {2*math.sqrt(2):.6f})")
L.check("local hidden variables: |S| ≤ 2 (exhaustive over the 16 deterministic strategies)", best == 2)
L.check("singlet at the standard angles: |S| = 2√2", abs(abs(S_q) - 2*math.sqrt(2)) < 1e-12)
L.prose("'The hidden variable is θ_k = arctan(cos_k/sin_k), the parallax angle between frames' — an identification; no sedenion construction here reproduces the CHSH value 2√2")
L.prose("'Entanglement IS σ=½' — interpretation")"""),
("code", """for c_ in ["'Cosine is the observer; the observer is imaginary to the content' (framing; the inversion itself is an exact change of variables, checked above)",
           "Corrected sedenion address space: z_k = sin + i·cos — a relabelling of the same 16 reals",
           "Mind's Eye = content frame (updateable), Paper's Hands = observer frame (non-updateable): the σ-side assignment is checked; 'updateable' is an architecture statement"]:
    L.prose(c_)"""),
]
