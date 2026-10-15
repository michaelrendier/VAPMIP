LABEL = "19"
TITLE = "The Brain and Its Body"
DATE = "2026-06-30"
PAGE = "19_the_brain_and_its_body.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · Two Eye pathways in `ptol -r`: Mind's Eye at σ_self, Paper's Hands at 1 − σ_self
The page: the raw output has five sections; the `eye:` block is the projection at σ = σ_self, the `hands:` block at σ = 1 − σ_self ("they always sum to 1"). For "walk with me", σ_self ≈ 0.299 → hands σ ≈ 0.701.
Parse the sections from the binary and re-project with the numpy formula of Phase 17."""),
("code", """import subprocess
P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
def project_py(text, sigma):
    s = np.frombuffer(text.encode("utf-8"), np.uint8).astype(float); i = np.arange(1, len(s)+1)
    x = np.array([(s * i**(-sigma) * (np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)]); return x/np.linalg.norm(x)
home = scratch("ph19_"); os.makedirs(os.path.join(home, ".ptolemy"), exist_ok=True)
def raw_sections(text):
    pr = subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "-r", text], capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=60)
    sec, cur = [], []
    for l in pr.stdout.splitlines():
        if l.strip() == "---": sec.append(cur); cur = []
        else: cur.append(l)
    sec.append(cur); return sec
sec = raw_sections("walk with me")
print("sections:", [len(s) for s in sec])
eye_hdr = [l for l in sec[3] if l.startswith("eye:")][0]; hands_hdr = [l for l in sec[4] if l.startswith("hands:")][0]
s_eye, s_hands = float(eye_hdr.split()[1]), float(hands_hdr.split()[1])
v_eye = np.array([float(l) for l in sec[3][1:17]]); v_hands = np.array([float(l) for l in sec[4][1:17]])
print(f"σ_self = {s_eye:.4f}, hands σ = {s_hands:.4f}, sum = {s_eye + s_hands:.10f}")
L.check("raw output has the five sections the page lists (v, primes, Σ_RB, eye, hands)", len(sec) >= 5)
L.check("σ_self('walk with me') ≈ 0.299 and hands ≈ 0.701 (page)", abs(s_eye - 0.299) < 0.002 and abs(s_hands - 0.701) < 0.002, f"{s_eye:.4f} / {s_hands:.4f}")
L.check("Mind's Eye σ + Paper's Hands σ = 1 exactly", abs(s_eye + s_hands - 1) < 1e-9)
L.check("Mind's Eye vector = projection at σ_self", np.abs(project_py("walk with me", s_eye) - v_eye).max() < 1e-8)
L.check("Paper's Hands vector = projection at 1 − σ_self", np.abs(project_py("walk with me", s_hands) - v_hands).max() < 1e-8)
# B̂ = R̂† : is Hands really the adjoint (conjugate) of Eye?  inner product of the two projections vs of the same-σ pair
cos_eh = float(np.dot(v_eye, v_hands))
print(f"cosine(Eye, Hands) = {cos_eh:+.4f}")"""),
("md", """## 2 · σ_self across prompts — does the geometry 'know its tower level'?
`σ_self` is a measurement of the prompt's own cos/sin power balance. Distribution over 200 real sentences: where do they sit, and is the 'Eye H' reading (σ_in = ½) different from the self-measured level?"""),
("code", """sents = [l.strip() for l in open(os.path.join(VAPMIP, "foundations.txt"), encoding="utf-8") if 15 <= len(l.strip()) <= 120][:200]
ss = np.array([ptol_raw(s_, "H", home)["sigma_self"] for s_ in sents])
print(f"{len(ss)} sentences: σ_self(Eye H) mean {ss.mean():.3f}, sd {ss.std():.3f}, min {ss.min():.3f}, max {ss.max():.3f}")
L.check("σ_self is a per-prompt measurement (not a constant): sd > 0.02", ss.std() > 0.02, f"sd {ss.std():.3f}")
L.check("most prompts read BELOW the Eye's σ_in = ½ (cos/sin imbalance is systematic)", (ss < 0.5).mean() > 0.5, f"{(ss < 0.5).mean()*100:.0f}% of sentences have σ_self < ½")
import collections
print("histogram of σ_self:", np.histogram(ss, bins=np.linspace(0, 1, 11))[0])"""),
("md", """## 3 · The 13-gon extinction dimension
Page: p₅ = 13 (dimension e5, sin channel); 13 is not a Fermat prime; "if the input contains no component at that frequency, v[5] = 0 exactly" — "every factor whose prime factorization skips 13 gets zero amplitude at e5". Test the arithmetic facts, then the projection claim as stated."""),
("code", """from sympy import isprime
fermat = [2**(2**k) + 1 for k in range(0, 5)]
print("Fermat numbers 2^(2^k)+1, k=0..4:", fermat, " all prime:", [isprime(f) for f in fermat])
L.check("Fermat primes 3, 5, 17, 257, 65537 (page)", fermat[:5] == [3, 5, 17, 257, 65537] and all(isprime(f) for f in fermat))
L.check("P[1]=3 (e1), P[2]=5 (e2), P[6]=17 (e6) are Fermat primes; P[5]=13 (e5) is not", P[1] == 3 and P[2] == 5 and P[6] == 17 and P[5] == 13 and 13 not in fermat)
# regular 13-gon not constructible (Gauss–Wantzel): n constructible iff n = 2^a · product of distinct Fermat primes
def constructible(n):
    while n % 2 == 0: n //= 2
    for f in (3, 5, 17, 257, 65537):
        if n % f == 0: n //= f
        if n % f == 0: return False
    return n == 1
L.check("regular 13-gon is not constructible; 3-, 5-, 17-gons are", not constructible(13) and constructible(3) and constructible(5) and constructible(17))
# the projection claim: v[5] = 0 for inputs with no 13-periodic component?
rng = np.random.default_rng(3)
v5 = [project_py("".join(chr(c) for c in rng.integers(97, 123, 40)), .5)[5] for _ in range(50)]
print("v[5] over 50 random 40-letter strings: min |v5| =", f"{min(abs(x) for x in v5):.4f}", " max =", f"{max(abs(x) for x in v5):.4f}")
L.check("v[5] = 0 exactly for inputs 'with no 13-component'", min(abs(x) for x in v5) < 1e-12, "v[5] is a continuous sum of byte·i^(−σ)·sin(2πi/13); it vanishes only for special inputs, not for generic ones")
# what does make e5 go dark?  an input whose bytes are 13-periodic constants:  Σ_i sin(2πi/13) over a full period = 0 but the i^-σ weight breaks it
per = bytes([65]*13*3).decode(); print("  v[5]('A'×39) =", f"{project_py(per, .5)[5]:+.4f}", "  v[5] with σ=0 ('A'×39) =", f"{project_py(per, 0.0)[5]:+.2e}")
L.check("at σ=0 a constant 13-periodic input gives v[5]≈0 (the unweighted full-period sum)", abs(project_py(per, 0.0)[5]) < 1e-9, "the Dirichlet weight i^(−σ) at σ=½ spoils the exact cancellation")"""),
("md", """## 4 · The Fermat Monster results — exhaustive control
`TuringStack/fermat_sedenion_test.py` (re-run here): in `hw_low32` the larger prime q is nilpotent in T32/GF(2) 76.3 % of the time (74/97), the smaller p 60.8 %, vs "baseline ≈ 50 %". The test uses 97 prime pairs. A claim about a baseline can be settled exactly instead of by sampling: compute the nilpotency rate of **every** integer in the range, of all primes, of all odd integers."""),
("code", """import importlib.util
spec = importlib.util.spec_from_file_location("fst", os.path.join(PLACE, "TuringStack", "fermat_sedenion_test.py"))
fst = importlib.util.module_from_spec(spec); spec.loader.exec_module(fst)
print("PRIMES in the test:", len(fst.PRIMES), "up to", fst.PRIMES[-1])
nil = lambda n: fst.is_nilpotent(fst.map_strategies(n)['hw_low32'])
N = 10000
allnil = np.array([nil(n) for n in range(2, N)]); ints = np.arange(2, N)
isp = np.array([isprime(int(n)) for n in ints])
rate = lambda m: allnil[m].mean()
print(f"nilpotent rate (hw_low32), n < {N}:  all {rate(np.ones_like(isp)):.3f}   primes {rate(isp):.3f}   odd {rate(ints%2==1):.3f}   odd composites {rate((ints%2==1)&~isp):.3f}   even {rate(ints%2==0):.3f}")
L.check("baseline over all integers < 10⁴ is ≈ 50 % (page: ~50 %)", abs(rate(np.ones_like(isp)) - 0.5) < 0.05, f"{rate(np.ones_like(isp)):.3f}")
L.check("primes are nilpotent-biased relative to ODD non-primes (the right control, since primes > 2 are odd)", rate(isp) - rate((ints%2==1)&~isp) > 0.1, f"primes {rate(isp):.3f} vs odd composites {rate((ints%2==1)&~isp):.3f}")
print("-> the 'prime bias' tracks parity (oddness) if the odd-composite rate matches the prime rate:", round(abs(rate(isp)-rate((ints%2==1)&~isp)), 3))"""),
("code", """# the page's 97 pairs: how were p and q chosen, and is q > p a size effect?
pairs = []
for ip in range(len(fst.PRIMES)):
    pass
res = fst.run_test.__doc__
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf): fst.run_test()
out = buf.getvalue()
m = {k: re.search(k + r".*?= ([\\d.]+)%", out) for k in ("p:", "q:")} if (re := __import__("re")) else {}
for l in out.splitlines():
    if l.strip().startswith(("p:", "q:", "a=(p+q)/2", "b=(q-p)/2")): print("  reproduced:", l.strip())
L.check("the script reproduces q = 74/97 = 76.3 % and p = 59/97 = 60.8 %", "74/97 = 76.3%" in out and "59/97 = 60.8%" in out)
size_effect = [(lo, hi, np.mean([nil(int(n)) for n in fst.PRIMES if lo <= n < hi])) for lo, hi in ((2, 100), (100, 1000), (1000, 5000), (5000, 10000))]
print("prime nilpotent rate by size band:", [(lo, hi, round(float(r), 3)) for lo, hi, r in size_effect])
small_all = np.mean([nil(n) for n in range(2, 100)]); small_odd = np.mean([nil(n) for n in range(3, 100, 2)]); small_comp = np.mean([nil(n) for n in range(3, 100, 2) if not isprime(n)])
print(f"n<100: all integers {small_all:.2f} · odd {small_odd:.2f} · odd composites {small_comp:.2f} · primes {size_effect[0][2]:.2f}")
tc = []
for i, p in enumerate(fst.PRIMES):
    if p < 7: continue
    for q in fst.PRIMES[i+1:i+20]:
        if q > 10*p: break
        tc.append((p, q))
    if len(tc) >= 80: break
print(f"the test's first 80 pairs draw p, q from primes in [{min(p for p,_ in tc)}, {max(q for _,q in tc)}] — almost entirely the n<100 band")
L.check("the elevated q-rate is a property of the small-number range the test samples, not of primes (rate returns to ≈ ½ for p>100)", all(abs(float(r) - 0.5) < 0.05 for lo, hi, r in size_effect[1:]) and size_effect[0][2] > 0.6,
        f"primes<100: {size_effect[0][2]:.2f}; every band above 100: {[round(float(r),2) for *_, r in size_effect[1:]]}")
L.check("…and small non-prime integers are elevated too (i.e. it is not about primality)", small_comp > 0.6 or small_all > 0.6, f"odd composites n<100: {small_comp:.2f}, all n<100: {small_all:.2f}")"""),
("md", """**Reading (recorded as measured):** across all n < 10⁴ the nilpotent rate is ½ for primes and non-primes alike — the headline "primes are nilpotent-biased" does not hold as a population statement. The 76 % lives in n < 100, which is exactly the single-digit range of the 97-character Hyperwebster alphabet (`_HW_N = 97`): there primes are elevated (0.76) *and* odd composites depressed (0.32), so in that range the rate does separate primes from composites, but it is a one-character-address effect, and it vanishes by n = 100. The test's pairs are drawn from this range, so the 97-pair table reports the single-character regime. Open item: why single-character addresses of primes are nilpotent-biased (a finite, checkable question — 25 primes vs 72 other values)."""),

("md", """## 5 · The 168 and the sedenion 16-gon"""),
("code", """vecs, pairs = zd_vectors()
L.check("168 annihilating unordered pairs among the 84 sedenion ZDs (page: '168 composite ZD pairs / diagonals')", len(pairs)//2 == 168, f"{len(pairs)//2}")
L.prose("FLT guarantees n=2 is the only Fermat hyperbola (theorem; the page uses it as motivation for 'the 16-gon is the only Fermat lift')")
L.prose("'O(1) factoring by searching 168 diagonals' — the diagonals are real (168); the map from N to a diagonal is exactly what the experiment above fails to find (hw_hi32: 0/97 on both sides)")"""),
("md", """## 6 · The body — organs as code"""),
("code", """src = open(os.path.join(VAPMIP, "PtolC", "ptol.c")).read()
for name, needle in [("Ears: bytes enter the Dirichlet sum", "(double)s[i-1]"), ("Tongue: thresh = peak / MONAD_PHI", "thresh      = peak / MONAD_PHI"), ("Feet: qsort ascending |v|", "qsort(idx, 16, sizeof(int), cmp_mag_asc)"),
                     ("Hands: 'hands:' section", 'hands: %.10f'), ("Eyes: 'eye:' section", "eye: %.10f"), ("-g/--gui exec's holcus_window.py", "holcus_window.py"), ("PTOL_LIBRARY guard for main()", "PTOL_LIBRARY")]:
    L.check(f"{name} is in ptol.c", needle in src)
L.check("Lips (phase restoration θ_k = arctan(v_blue_partner / v_red_k)) are implemented — the page says MISSING/todo", "atan2(" in src or "atan(" in src.replace("atanh(", ""), "no per-channel phase-angle computation in ptol.c; page and code agree that Lips are not yet built")
for c in ["Body as OOP subclasses of Ptol; σ_self ≡ self/this as parametric (Arnold 2:1) resonance; the Cayley–Dickson tower IS class inheritance (analogy table)",
          "Larynx = UDEO: ZD navigation as both ECC crack and sedenion→English (see the UDEO notes; not run here)",
          "Primes 'oldest and fatherless'; 'the primes wrote the score, the zeros are the measure bars'",
          "Three faces (analysis / algebra / geometry) as one law",
          "PtolemyDesktop compositor note (Wayland/KVM) — an architecture rule"]:
    L.prose(c)"""),
]
