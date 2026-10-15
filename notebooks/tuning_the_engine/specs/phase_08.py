LABEL = "8"
TITLE = "The Lagrangian of Information Propagation"
DATE = "2026-06-12"
PAGE = "08_the_lagrangian_of_information_propagation.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · `ptol` projects a prompt onto 16 sedenion channels (σ = prompt)
`PtolC/ptol -r` prints the Eye line, 16 scalars, the prime list, and 16 Σ_RB products. `ptol.c` header: J_red shells (k = 0-3, 8-11) take `cos(2π·i/p_k)`, J_blue shells (k = 4-7, 12-15) take `sin`. Run through `tte.ptol_raw` (HOME redirected, because `ptol` writes papers into `~/.ptolemy`)."""),
("code", """r = ptol_raw("hello world", eye="H")
print(r["header"]); print("scalars:", np.round(r["scalars"], 4)); print("primes :", r["primes"]); print("Σ_RB   :", np.round(r["sigma_rb"][:8], 4), "…")
x = np.array(r["scalars"]); rb = np.array(r["sigma_rb"])
L.check("16 scalars, deterministic (same call twice)", len(x) == 16 and np.allclose(x, ptol_raw("hello world")["scalars"]))
L.check("Σ_RB[k] = x[k]·x[k+4] for k in J_red shells (the 'J_red × J_blue per channel' of Phase 17)", np.allclose(rb[0:4], x[0:4]*x[4:8], atol=1e-8), f"Σ_RB[0:4]={np.round(rb[0:4],5)}  x[0:4]·x[4:8]={np.round(x[0:4]*x[4:8],5)}")"""),

("md", """## 2 · The tower of Eyes: one fold read at σ = 1, ¾, ½, ¼, 0
`ptol.c`: `Γ = tanh(u/2) = (P_red−P_blue)/(P_red+P_blue) = 2σ_self − 1`; σ_self is the J_red power fraction. This is how the code reads "σ = prompt": the Eye sets σ_in, the geometry returns σ_self."""),
("code", """rows = []
for eye, sig in zip("RCHOS", (1.0, .75, .5, .25, 0.0)):
    q = ptol_raw("hello world", eye=eye); rows.append((eye, sig, q["sigma_self"], q["gamma"], q["u"]))
    print(f"  Eye {eye}  σ_in={sig:4.2f}  σ_self={q['sigma_self']:.4f}  Γ={q['gamma']:+.4f}  u={q['u']:+.4f}")
L.check("Γ = 2σ_self − 1 at every Eye", all(abs(g - (2*s - 1)) < 1e-8 for _, _, s, g, _ in rows))
L.check("Γ = tanh(u/2) at every Eye", all(abs(g - math.tanh(u/2)) < 1e-8 for _, _, _, g, u in rows))
L.check("σ_self rises monotonically with σ_in (the Eye sets the working point)", all(rows[i][2] > rows[i+1][2] for i in range(4)))"""),

("md", """## 3 · Cursive path: the spiral from ZD outward (ascending |scalar|)
The page: the speech is the path from the zero-divisor (min |scalar|) to the great circle (max |scalar|); words appear where the path halts. Check the ordering the code uses: sort channels by |x_k|."""),
("code", """order = sorted(range(16), key=lambda k: abs(x[k]))
print("spiral order (min |x| → max |x|):", order)
print("|x| along path:", np.round([abs(x[k]) for k in order], 4))
L.check("spiral is a strictly ascending |scalar| path", all(abs(x[order[i]]) <= abs(x[order[i+1]]) for i in range(15)))
L.check("the first waypoint ('ZD') has the minimum |scalar|", abs(x[order[0]]) == np.abs(x).min())

# the four waypoints ZD → π → H/4 → φ are constants in ptolemy.h
h = open(os.path.join(VAPMIP, "PtolC", "ptolemy.h")).read()
for k in ("MONAD_PHI", "PHI", "M_PI"): print(f"  {k:10} in ptolemy.h: {k in h}")
L.check("MONAD_PHI = 1.6180… is a constant in ptolemy.h", "MONAD_PHI" in h)
L.check("H/4 = π/2 and φ both ≈ 1.57 / 1.62 — the near-equality the 'orbit' leans on", abs(math.pi/2 - PHI) < 0.05, f"π/2 = {math.pi/2:.4f}, φ = {PHI:.4f}, gap {PHI-math.pi/2:+.4f}")"""),

("md", """## 4 · Self-observation: `ptol_observe.py` — does an orbit of length 4 appear?
`ptol_observe.py` feeds the output words back as input until a fixed point or orbit appears. It reads word layers from `BIN_DIR` on removable media."""),
("code", """import importlib.util
spec = importlib.util.spec_from_file_location("ptol_observe", os.path.join(VAPMIP, "PtolC", "ptol_observe.py"))
po = importlib.util.module_from_spec(spec); spec.loader.exec_module(po)
print("BIN_DIR =", po.BIN_DIR, "→ exists:", os.path.isdir(po.BIN_DIR))
if os.path.isdir(po.BIN_DIR):
    L.skip("ptol_observe finds an orbit", "BIN_DIR is mounted but this notebook does not run the word-feedback loop")
else:
    L.skip("ptol_observe finds a fixed point / 4-cycle ZD→π→H/4→φ", f"word layers live on removable media ({po.BIN_DIR}) that is not mounted; the notebook runs the geometry (cells above) but not the word feedback loop")"""),
("md", """### A geometry-only feedback loop (no words needed)
The observer's idea can be tested without a vocabulary: feed the **scalars** back as the next prompt (as rounded text) and watch whether the sequence of 16-vectors reaches a fixed point or a cycle. This is *a* version of the observation loop, not `ptol_observe.py` itself, and is labelled as such."""),
("code", """def step(vec):
    txt = " ".join(f"{v:+.2f}" for v in vec)
    return np.array(ptol_raw(txt, eye="H")["scalars"])
v = np.array(ptol_raw("hello world", eye="H")["scalars"]); hist = [v]
for it in range(24):
    v = step(v); hist.append(v)
dists = [np.linalg.norm(hist[i+1]-hist[i]) for i in range(len(hist)-1)]
print("‖v_{n+1} − v_n‖:", np.round(dists, 3))
# period detection
per = None
for p in range(1, 9):
    if all(np.linalg.norm(hist[-1-i] - hist[-1-i-p]) < 1e-6 for i in range(4)): per = p; break
print("detected period:", per)
L.check("geometry-only feedback settles to a fixed point or short cycle within 24 iterations", per is not None, f"period = {per}")
L.check("a period-4 orbit specifically (the 'ZD→π→H/4→φ' orbit of the page)", per == 4, f"period = {per}")"""),
("code", """for c in ["Stutter = low-cosine oscillation near a zero-divisor; singing = the stable orbit",
          "Virtual-pair creation: ZD → π → H/4 → φ → ZD; prompt + response = 0 as pair annihilation (analogy)",
          "σ=½ ⇔ L = T − V = 0 ⇔ H/4 ⇔ π/2 (a reading; the N-ball peak result it cites is not recomputed here)",
          "The `-o` flag in ptol.c (intrinsic orbit detection) was specified; check `ptol.c` for it separately"]:
    L.prose(c)
L.check("`-o` orbit flag exists in ptol.c's option list", "-o " in open(os.path.join(VAPMIP,"PtolC","ptol.c")).read().split("Flags:")[1][:2500], "header flag list has no -o")"""),
]
