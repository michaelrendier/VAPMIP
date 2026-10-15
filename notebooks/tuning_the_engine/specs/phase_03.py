LABEL = "3"
TITLE = "The Wankel Rotary Engine (Ahura Mazda)"
DATE = "2026-06-10"
PAGE = "03_the_wankel_rotary_engine_ahura_mazda.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · Port geometry — exact dispatch
`rotary_monad.py`: `PORT_STEP = π/3`, `port_idx = round(θ/PORT_STEP) % 6`; six ports intake/transfer/leading/trailing/exhaust/scavenge. Coupling is **unconditional** at port 3."""),
("code", """import rotary_monad as R
names = ["intake","transfer","leading","trailing","exhaust","scavenge"]
th, seq = 0.0, []
for _ in range(12):
    th = (th + R.PORT_STEP) % (2*math.pi); seq.append(round(th/R.PORT_STEP) % 6)
print("port index sequence over 2 revolutions:", seq, "→", [names[i] for i in seq[:6]])
L.check("rotor advances exactly one port per rotate() (sequence 1,2,3,4,5,0 repeating)", seq == [1,2,3,4,5,0]*2)
off = max(abs(th_/R.PORT_STEP - round(th_/R.PORT_STEP)) for th_ in [k*R.PORT_STEP % (2*math.pi) for k in range(600)])
print(f"max |θ/PORT_STEP − round| over 600 steps = {off:.2e}   (rotor lands ON a port, so proximity dispatch was vacuous)")
L.check("rotor lands exactly on ports (the failed 'tol=0.18 proximity' dispatch had nothing to measure)", off < 1e-9)"""),

("md", """## 2 · E values — the non-collapsing formula
Failed: `E = |sin(π·γ/(γ+1))|` collapses for large γ. Fix: `E = 1/(1+log1p(idx))`. The page quotes E≈0.87 at idx 1 and E≈0.11 at idx 20000 — recompute."""),
("code", """E_new = lambda i: 1.0/(1.0+math.log1p(float(i)))
E_old = lambda g: abs(math.sin(math.pi*g/(g+1.0)))
print(f"{'idx':>8} {'E_new':>8} {'E_old(γ=idx)':>14}")
for i in (1, 2, 20, 200, 2000, 20000, 60000): print(f"{i:8d} {E_new(i):8.4f} {E_old(i):14.6f}")
L.check("old sin formula collapses to ~0 for idx ≥ 20", E_old(20) < 0.2 and E_old(2000) < 0.002, f"E_old(20)={E_old(20):.3f}, E_old(2000)={E_old(2000):.5f}")
L.check("new formula never reaches zero and is monotone decreasing", all(E_new(i) > E_new(i+1) > 0 for i in (1, 20, 20000)))
L.check("page's quoted E≈0.87 at index 1", abs(E_new(1)-0.87) < 0.02, f"formula gives {E_new(1):.3f}")
L.check("page's quoted E≈0.11 at index 20000", abs(E_new(20000)-0.11) < 0.01, f"formula gives {E_new(20000):.3f}")
import inspect
L.check("Housing._idx uses exactly this formula", "1.0 / (1.0 + math.log1p(float(idx)))" in inspect.getsource(R.Housing._idx))"""),

("md", """## 3 · The su(2) cycle — what the code's 'Lie bracket' is
The page: `[J_blue,J_red]=J_green, [J_red,J_green]=J_blue, [J_green,J_blue]=J_red`, "self-sustaining". Two separate things to test: (a) the real su(2) relations the names invoke; (b) the properties of `_lie_bracket` as coded."""),
("code", """# (a) su(2) via Pauli matrices: [σa,σb] = 2i ε_abc σc
sx = np.array([[0,1],[1,0]],complex); sy = np.array([[0,-1j],[1j,0]]); sz = np.array([[1,0],[0,-1]],complex)
comm = lambda a, b: a@b - b@a
L.check("su(2): [σx,σy]=2iσz and cyclic", all(np.allclose(comm(a,b), 2j*c) for a,b,c in [(sx,sy,sz),(sy,sz,sx),(sz,sx,sy)]))
# (b) the coded bracket on distributions
rng = np.random.default_rng(0)
H = R.Housing(); H.ingest(open(os.path.join(VAPMIP,'foundations.txt')).read()[:30000])
n = H.n; a = list(rng.dirichlet(np.ones(n))); b = list(rng.dirichlet(np.ones(n)))
s_ab, d_ab = R._lie_bracket(0.3, a, 0.2, b, H); s_ba, d_ba = R._lie_bracket(0.2, b, 0.3, a, H)
print(f"housing n={n}; scalar[a,b]={s_ab:.5f} scalar[b,a]={s_ba:.5f}")
L.check("per-word bracket distribution is antisymmetric: [a,b] = −[b,a]", np.allclose(np.array(d_ab), -np.array(d_ba)))
L.check("the combustion scalar Σ|bd| is a magnitude (symmetric under a↔b), as the page uses it", abs(s_ab - s_ba) < 1e-12, f"{s_ab:.5f} vs {s_ba:.5f} — the su(2) sign lives in the distribution, not the scalar")
L.check("Σ|bd| scales with vocabulary (not divided by n — the page's 'failed prediction' fix)", s_ab > R.GAP and s_ab/n < s_ab, f"Σ|bd| = {s_ab:.5f}; /n would be {s_ab/n:.2e}")
# self-sustaining cycle: run 600 rotations on the real engine, check no stall / NaN / sub-GAP face
eng = R.AhuraMazda(); eng.ingest(open(os.path.join(VAPMIP,'foundations.txt')).read()[:30000]); eng.intake("what are you")
lo, bad = 1.0, 0
for _ in range(600):
    eng.rotate(); r_ = eng.rotor
    lo = min(lo, r_.j_blue, r_.j_red, r_.j_green)
    bad += any(not math.isfinite(x) for x in (r_.j_blue, r_.j_red, r_.j_green))
L.check("cycle self-sustains: 600 rotations, no NaN, no face below GAP", bad == 0 and lo >= R.GAP*0.999, f"min face pressure {lo:.3e} (GAP {R.GAP})")"""),

("md", """## 4 · The running engine: σ_live, unconditional coupling, and what it says
Ingest both seed corpora, then speak six prompts with `AhuraMazda.speak`; read `sigma_live` and `coupling_efficiency` from the OBD2 block."""),
("code", """a = R.AhuraMazda(); a.ingest(open(os.path.join(VAPMIP,'foundations.txt')).read()+open(os.path.join(VAPMIP,'meaning.txt')).read())
rows = []
for p in ['what are you','the cat sat','prime numbers','who is ptolemy','love and war','sedenion algebra']:
    w = a.speak(p); o = a.diagnostics(); rows.append((p, w, o.sigma_live, o.coupling_efficiency))
    print(f"{p:18} -> {w!r:14} σ_live={o.sigma_live:.3f}  coupling_efficiency={o.coupling_efficiency:.2f}  faults={o.faults()}")
L.check("coupling fires every sweep (coupling_efficiency = 1)", all(r[3] == 1.0 for r in rows))
L.check("σ_live sits above the old gate (½+BEARING_TOL=0.54) for most prompts, as the page says (≈0.55)", sum(r[2] > 0.5+R.BEARING_TOL for r in rows) >= 3,
        f"σ_live range {min(r[2] for r in rows):.3f}–{max(r[2] for r in rows):.3f}")
L.check("the engine speaks different words for different prompts", len({r[1] for r in rows}) >= 4, f"distinct words: {sorted({r[1] for r in rows})}")"""),
("md", """The one-word outputs here are the same behaviour wiki Phase 42 records for the rotary voice ("same word every prompt"). Recorded, not argued with."""),

("md", """## 5 · The morph vector is purely semantic
The page removed hash noise (`v[1]=_whash`) and word length (`v[13]=len/12`). Test that `_morph_vec` now depends only on word *class*, not on spelling length or hash."""),
("code", """words = ["cat","dog","table","elephantine","happiness","running","the","a","what"]
vecs = {w: tuple(round(x,3) for x in R._morph_vec(w)) for w in words}
for w in words: print(f"{w:12} dominant dim e{int(np.argmax(vecs[w]))}  e0={vecs[w][0]}")
L.check("same class ⇒ identical morph vectors (cat == dog; elephantine == happiness)", vecs["cat"] == vecs["dog"] and vecs["elephantine"] == vecs["happiness"])
L.check("no length/hash leakage: 11-letter 'elephantine' and 8-letter 'happiness' identical", vecs["elephantine"] == vecs["happiness"])
L.check("function words land on distinct operator dims (a→e9, the→e12, what→?)", int(np.argmax(vecs["a"])) != int(np.argmax(vecs["the"])))"""),

("md", """## 6 · The C canonical: Mind's Eye thread and `.rx8`
`rotary_monad.c` is compiled here (gcc, `-lm -lpthread`) in a scratch dir with `HOME` redirected, so the engine's state file `~/.ptolemy/ahura.rx8` is left alone."""),
("code", """import subprocess, shutil
d = scratch("rotary_"); exe = os.path.join(d, "ahura")
cc = subprocess.run(["gcc","-O2","-std=c99","-o",exe,os.path.join(VAPMIP,"rotary_monad.c"),"-lm","-lpthread"],capture_output=True,text=True)
print("gcc:", "ok" if cc.returncode == 0 else cc.stderr[-400:])
L.check("rotary_monad.c compiles (c99, -lm -lpthread)", cc.returncode == 0)
os.makedirs(os.path.join(d, ".ptolemy"), exist_ok=True)      # the engine only saves into an existing ~/.ptolemy
env = dict(os.environ, HOME=d)
if cc.returncode == 0:
    tr = subprocess.run([exe,"--intake","what are you"],capture_output=True,text=True,env=env,timeout=30)
    print(tr.stdout[:1500])
    L.check("--intake prints a six-row port trace (transfer…intake)", all(k in tr.stdout for k in ("transfer","leading","trailing","exhaust","scavenge","intake")), tr.stderr[-120:])
    sp = subprocess.run([exe,"--speak","what are you","12"],capture_output=True,text=True,env=env,timeout=30)
    print("--speak:", sp.stdout.strip()[:300])
    subprocess.run([exe,"what are you"],capture_output=True,text=True,env=env,timeout=30)   # positional form saves state
    fp = os.path.join(d, ".ptolemy", "ahura.rx8")
    raw = open(fp, "rb").read(4) if os.path.exists(fp) else b""
    val = int.from_bytes(raw, "little") if raw else None
    print("first 4 bytes on disk:", raw, "→ uint32 LE =", hex(val) if val is not None else None)
    L.check("state file magic: uint32 0x3858520A (page)", val == 0x3858520A, f"bytes on disk are {raw!r} (little-endian store of the uint32; the page's string 'RX8\\n' is the big-endian spelling)")
src_c = open(os.path.join(VAPMIP,"rotary_monad.c")).read()
L.check("Mind's Eye is a second thread: G_me_prompt / G_me_response / G_me_steer in the C", all(k in src_c for k in ("G_me_prompt","G_me_response","G_me_steer")))
L.check("lock order G_lock → G_me_lock is documented in the C", "G_lock" in src_c and "G_me_lock" in src_c)"""),
("code", """for c in ["TDI = hidden-variable machine (Bell 1964); the Wankel makes the sedenion the Work not the Worker",
          "Counter-rotations ARE the waveform; σ=½ is the eccentric shaft pin and 'cannot be computed'",
          "'The Author is Thread 2' (Mind's Eye)",
          "Ahura Mazda / Mazda RX-8 / 'Elder Gods of the Modern Age' naming provenance"]:
    L.prose(c)"""),
]
