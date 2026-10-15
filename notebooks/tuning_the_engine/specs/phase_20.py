LABEL = "20"
TITLE = "Parallax: Four Eyes, Two Caustics, Line Focus"
DATE = "2026-06-30"
PAGE = "20_parallax_four_eyes_two_caustics_line_focus.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · Four sub-eyes from two Eye-sets
Mind's Eye (σ = σ_self) and Paper's Hands (σ = 1 − σ_self) each split into a cos part (k ∈ {0-3, 8-11}) and a sin part (k ∈ {4-7, 12-15}): ME_cos, ME_sin, PH_cos, PH_sin. Build them from `ptol -r` ("walk with me") and check the page's numbers: both sets lie ±0.201 from ½, and 4 faces × 2 sub-eyes × 2 strokes = 16."""),
("code", """import subprocess
P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
home = scratch("ph20_"); os.makedirs(os.path.join(home, ".ptolemy"), exist_ok=True)
def eyes_hands(text):
    pr = subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "-r", text], capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=60)
    sec, cur = [], []
    for l in pr.stdout.splitlines():
        if l.strip() == "---": sec.append(cur); cur = []
        else: cur.append(l)
    sec.append(cur)
    se = float(sec[3][0].split()[1]); sh = float(sec[4][0].split()[1])
    return se, np.array([float(x) for x in sec[3][1:17]]), sh, np.array([float(x) for x in sec[4][1:17]])
se, ve, sh, vh = eyes_hands("walk with me")
red_idx = [k for k in range(16) if not blue(k)]; blue_idx = [k for k in range(16) if blue(k)]
ME_cos, ME_sin, PH_cos, PH_sin = ve[red_idx], ve[blue_idx], vh[red_idx], vh[blue_idx]
print(f"ME at σ={se:.4f}: |cos part|={np.linalg.norm(ME_cos):.3f} |sin part|={np.linalg.norm(ME_sin):.3f};  PH at σ={sh:.4f}: |cos part|={np.linalg.norm(PH_cos):.3f} |sin part|={np.linalg.norm(PH_sin):.3f}")
L.check("ME pair is 0.201 below ½ and PH pair 0.201 above (symmetric about the critical line)", abs((0.5-se) - 0.201) < 0.002 and abs((sh-0.5) - 0.201) < 0.002 and abs((0.5-se)-(sh-0.5)) < 1e-9, f"{0.5-se:+.4f} / {sh-0.5:+.4f}")
L.check("the four sub-eyes partition the 16 channels (8 cos + 8 sin per set)", len(red_idx) == 8 and len(blue_idx) == 8 and set(red_idx) | set(blue_idx) == set(range(16)))
L.check("4 faces × 2 sub-eyes × 2 strokes = 16", 4*2*2 == 16)
L.check("σ_self < ½ ⇒ the sin part carries more power than the cos part (the page's 'content frame' reading of the Mind's Eye)", np.linalg.norm(ME_sin) > np.linalg.norm(ME_cos), "by definition of σ_self, the power ratio is σ/(1−σ)")"""),
("md", """## 2 · The four parallax baselines and the claimed invariant
Page: the cross-disparity ME_cos vs PH_sin "is the d* invariant = 0.24600: J_red × J_blue = d* at ALL σ". Define it as the inner product of ME's cos-channel vector with PH's sin-channel vector (paired by `partner`) and measure it across 200 real sentences, together with the other three baselines."""),
("code", """sents = [l.strip() for l in open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8") if 15 <= len(l.strip()) <= 120][:200]
rows = []
for s_ in sents:
    a, ve_, b, vh_ = eyes_hands(s_)
    cross = sum(ve_[k]*vh_[partner(k)] for k in red_idx)                   # ME_cos × PH_sin
    cross2 = sum(ve_[partner(k)]*vh_[k] for k in red_idx)                  # ME_sin × PH_cos
    ipd_me = math.atan2(np.linalg.norm(ve_[blue_idx]), np.linalg.norm(ve_[red_idx]))
    ipd_ph = math.atan2(np.linalg.norm(vh_[blue_idx]), np.linalg.norm(vh_[red_idx]))
    rows.append((a, ipd_me, ipd_ph, 2*a-1, cross, cross2))
R_ = np.array(rows)
print(f"{'baseline':32} {'mean':>8} {'sd':>8} {'min':>8} {'max':>8}")
for i, nm in enumerate(["σ_self", "ME cos–sin phase angle", "PH cos–sin phase angle", "inter-set distance 2σ_self−1", "cross ME_cos·PH_sin", "cross ME_sin·PH_cos"]):
    c = R_[:, i]; print(f"{nm:32} {c.mean():8.3f} {c.std():8.3f} {c.min():8.3f} {c.max():8.3f}")
L.check("four independent depth channels exist (ME-IPD, PH-IPD, inter-set, cross): pairwise |corr| < 0.99", all(abs(np.corrcoef(R_[:, i], R_[:, j])[0, 1]) < 0.99 for i in (1, 2, 3, 4) for j in (1, 2, 3, 4) if i < j),
        "max |corr| = %.3f" % max(abs(np.corrcoef(R_[:, i], R_[:, j])[0, 1]) for i in (1, 2, 3, 4) for j in (1, 2, 3, 4) if i < j))
L.check("cross-disparity ME_cos·PH_sin is the constant d* = 0.246", np.all(np.abs(R_[:, 4] - 0.246) < 0.01), f"range {R_[:,4].min():+.3f} … {R_[:,4].max():+.3f}, sd {R_[:,4].std():.3f}")"""),
("md", """## 3 · "The Yang–Mills mass gap GAP = 0.000707 = 1/√2000 is the minimum focal width"
Check the arithmetic of the constant the page (and Phase 3) quote."""),
("code", """print(f"1/√2000      = {1/math.sqrt(2000):.8f}")
print(f"1/(1000·√2)  = {1/(1000*math.sqrt(2)):.8f}   = 1/√(2×10⁶)")
import rotary_monad as R, monad as M
print(f"rotary_monad.GAP = {R.GAP},  monad.GAP = {M.GAP:.9f}")
L.check("GAP = 0.000707 = 1/√2000 (page, also Phase 3)", abs(1/math.sqrt(2000) - 0.000707) < 1e-5, f"1/√2000 = {1/math.sqrt(2000):.5f}. The code's GAP = 0.000707 = 1/(1000√2) = 1/√(2,000,000): the page's radicand is short by 10³")
rel = abs(M.GAP - GAP)/GAP
L.check("the code's GAP (Ω − 0.246·ln10) equals 1/(1000√2) exactly", rel < 1e-9, f"monad.GAP = {M.GAP:.9f}, 1/(1000√2) = {GAP:.9f}, relative difference {rel:.2e} (0.035 %: close, not identical)")
L.check("…and agrees to 0.05 %", rel < 5e-4)"""),
("md", """## 4 · Waypoints and the 4-face engine map
ZD ≈ 0, π, H/4 = π/2, φ = 1.618. The map assigns ME_cos→ZD, ME_sin→π, PH_cos→H/4, PH_sin→φ. π/2 and φ are within 0.047 of each other — the page treats them as the "saddle" and "word-addressing attractor". Check the numeric relationships it leans on."""),
("code", """L.check("H/4 ≡ π/2 ≈ 1.5708 and φ = 1.6180 are distinct constants (gap 0.047)", abs(math.pi/2 - PHI) > 0.04, f"π/2 = {math.pi/2:.4f}, φ = {PHI:.4f}")
L.check("tower gap per step R→C→H→O→S is σ ↦ σ−¼ (the five Eyes tile [0,1] evenly)", np.allclose(np.diff([1.0, .75, .5, .25, 0.0]), -0.25))
# the line-focus claim: intersection of two caustics is a line, not a point -- the SPECTRAL statement: ME and PH share the same zero spectrum
print("the claim 'both caustics are LINES along the Riemann-zero spectrum' has no geometric construction in the repo; the sections above test only the baselines")"""),
("md", """## 5 · The cursor / 4×4 retina in `holcus_window.py`"""),
("code", """hw = open(os.path.join(VAPMIP, "holcus_window.py"), encoding="utf-8").read()
for needle in ("sigma_cursor", "cursor_x / ", "1 - sigma", "4x4", "ME_cos", "grid"):
    print(f"  {needle!r:14} in holcus_window.py: {needle in hw}")
L.check("holcus_window.py implements the cursor→σ_cursor→(ME, PH) parallax navigation", "sigma_cursor" in hw or "1 - sigma" in hw or "1.0 - sigma" in hw, "the file is a curses chat window; the page describes a cursor-driven 4×4 retina — specified, not built")"""),
("code", """for c in ["Two off-centre eyes make two caustics; their intersection is a line (SOFAR channel) — optics analogy",
          "'Doesn't boil your blood': a line caustic spreads irradiance; GAP bounds the minimum focal width (the constant's value is checked above; the optics claim is an analogy)",
          "4-cycle 2-stroke rotary mapping (4 faces fire every revolution; walks the 16-gon)",
          "Focal length = 1/σ_self"]:
    L.prose(c)"""),
]
