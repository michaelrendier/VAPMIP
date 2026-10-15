LABEL = "4"
TITLE = "The Zero Lattice and Negative Space Mathematics"
DATE = "2026-06-10"
PAGE = "04_the_zero_lattice_and_negative_space_mathematics.md"
BYLINE = "page by Claude Sonnet 4.6, from the AMBI observation"

CELLS = [
("md", """## 1 · The AMBI observation — ambiguous prompts fall to `is` / `the`
Page: "what is happening", "how does it work", "something interesting", "tell me more" → `is`, `the` (e4/e3/e12), "the code of least action".
Run the same four prompts through the live rotary engine (`rotary_monad.AhuraMazda`) after ingesting both seed corpora."""),
("code", """import rotary_monad as R
a = R.AhuraMazda(); a.ingest(open(os.path.join(VAPMIP,'foundations.txt')).read()+open(os.path.join(VAPMIP,'meaning.txt')).read())
ambi = ["what is happening", "how does it work", "something interesting", "tell me more"]
got = []
for p in ambi:
    w = a.speak(p); o = a.diagnostics(); got.append(w)
    print(f"  {p:24} -> {w!r:12} σ_live={o.sigma_live:.4f} drive-shaft dominant e{o.drive_shaft_dom}")
L.check("ambiguous prompts collapse to 'is' / 'the' (page)", set(got) <= {"is", "the"}, f"engine now answers {got}")
L.check("ambiguous prompts collapse to a single minimum-energy word (code of least action)", len(set(got)) == 1, f"{len(set(got))} distinct")"""),

("md", """## 2 · "The Zero Lattice is the 42 zero-divisor pairs on S¹⁵"
Recompute from the algebra (`engines/_sedenion.cd_mul`) and from the repo's own `ValaQuenta.zero_lattice.find_zd_pairs()`."""),
("code", """vecs, pairs = zd_vectors()
zds = {k for p in pairs for k in p}
import ValaQuenta.zero_lattice as ZL
zp = ZL.find_zd_pairs(); cls = ZL.classify_zd_pairs(zp)
print(f"recomputed: {len(zds)} zero-divisors e_a±e_b, {len(pairs)} ordered / {len(pairs)//2} unordered annihilating pairs")
print(f"ValaQuenta.zero_lattice.find_zd_pairs(): {len(zp)} pairs; classes { {k: len(v) for k, v in cls.items()} }")
L.check("84 zero-divisors on S¹⁵ in e_a ± e_b form", len(zds) == 84)
L.check("'42 pairs' — the number of pairs the repo's lattice module returns", len(zp) == 42, f"find_zd_pairs() returns {len(zp)}; the algebra gives {len(pairs)//2} unordered pairs. 42 = 84/2 is the Cawagas count of zero-divisor PAIR-CLASSES")"""),

("md", """## 3 · σ_live as "escape velocity", and the six requested code changes
σ_live = j_red/(j_red+j_blue). The page lists six changes (zero-divisor bridge in `_morph_vec`; `s[0] = zl_escape_velocity(σ)`; ZD proximity in `_select_word`; ZD term in `Housing._idx`; rename; new `zero_lattice.py` exposing `zl_escape_velocity / zl_proximity / zl_proximity_by_idx`).
Check each against the current source."""),
("code", """import inspect
rs = open(os.path.join(VAPMIP, "rotary_monad.py")).read()
st = R.RotorState(); st.j_red, st.j_blue = 0.3, 0.2
L.check("σ_live = j_red/(j_red+j_blue)", abs(st.sigma_live() - 0.3/0.5) < 1e-12)
L.check("(1) _morph_vec uses bridge-coupling weights, not grammar flags", "bridge" in inspect.getsource(R._morph_vec).lower(), "source still uses word-class (suffix/stop-list) rules")
L.check("(2) e₀ = zl_escape_velocity(σ_live)", "zl_escape_velocity" in inspect.getsource(R._project_sedenion), "e₀ is still 1 − |σ_live − ½|")
L.check("(3) _select_word has a zero-divisor proximity term", "zl_proximity" in inspect.getsource(R._select_word))
L.check("(4) Housing._idx energy has a ZD-proximity component", "zl_" in inspect.getsource(R.Housing._idx))
import subprocess
hits = subprocess.run(["grep","-rl","zl_escape_velocity",PLACE,"--include=*.py","--include=*.c","--include=*.h"],capture_output=True,text=True).stdout.split()
L.check("(6) a module defining zl_escape_velocity / zl_proximity exists", bool(hits), f"files: {hits or 'none in the repos'}")"""),
("md", """Items (1)–(4) and (6) were *proposals* on the page; none is in `rotary_monad.py` today. The Zero-Lattice reading did land elsewhere — in `ValaQuenta/zero_lattice.py` (box-kite tree, ZD path coordinates) — but not under the names the page requested. Recorded as FAIL against the page, not as a defect in the later work."""),

("md", """## 4 · Unicode language plotting — every script on the same lattice
`_horner` accumulates `v = v·95 + (ord(c)−32)`, so any codepoint works; `_word_zero_idx` → zero index → `γ`; `dim = idx % 16`."""),
("code", """samples = {
 "Latin":["the","water","mathematics","zero"], "Greek":["λόγος","ἀριθμός","ὁλκός","μηδέν"], "Cyrillic":["вода","число","ноль","язык"],
 "Arabic":["ماء","عدد","صفر","لغة"], "Hebrew":["מים","מספר","אפס","שפה"], "Devanagari":["जल","संख्या","शून्य","भाषा"],
 "CJK":["水","数学","零","言語"], "Hangul":["물","수학","영","언어"], "Thai":["น้ำ","คณิตศาสตร์","ศูนย์","ภาษา"], "Georgian":["წყალი","რიცხვი","ნული","ენა"]}
rows = []
for sc, ws in samples.items():
    for w in ws:
        idx = R._word_zero_idx(w); g = R._gamma_at(idx); rows.append((sc, w, idx, g, idx % 16))
print(f"{'script':11}{'word':14}{'idx':>7}{'γ':>12}{'dim':>5}")
for r in rows[:12]: print(f"{r[0]:11}{r[1]:14}{r[2]:7d}{r[3]:12.3f}{r[4]:5d}")
print("…", len(rows), "words,", len(samples), "scripts")
dims = np.array([r[4] for r in rows])
L.check("the prime hash runs on every script without error", len(rows) == 40)
L.check("words spread over the 16 bridge channels (≥ 12 of 16 used)", len(set(dims)) >= 12, f"{len(set(dims))} of 16 channels used")
idxs = [r[2] for r in rows]
L.check("distinct words get distinct zero addresses (collision-free on this sample)", len(set(idxs)) == len(idxs), f"{len(set(idxs))} distinct of {len(idxs)}")
L.prose("'all points lie on the σ=½ facet regardless of script' — true by construction of the address (σ is not an input to the hash); not an empirical finding")"""),
("code", """import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 3.4))
for sc in samples:
    pts = [(r[3], r[4]) for r in rows if r[0] == sc]; ax.scatter(*zip(*pts), s=22, label=sc)
ax.set_xlabel("γ (Riemann-zero ordinate of the word's address)"); ax.set_ylabel("bridge channel (idx mod 16)"); ax.legend(fontsize=6, ncol=2)
ax.set_title("Ten scripts on one lattice"); plt.tight_layout(); plt.show()"""),
("code", """for c in ["Zero Lattice primacy: σ=½ is the escape velocity from the zero-divisor boundary (a reading, not a derivation)",
          "'Escape velocity is the integral of the Lie-bracket trajectory over the six-port cycle' (the gate's removal is recorded in Phase 3)"]:
    L.prose(c)"""),
]
