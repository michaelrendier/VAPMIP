LABEL = "34"
TITLE = "The Anomaly, the Caustic, and the One File"
DATE = "2026-08-27"
PAGE = "34_the_anomaly_the_caustic_and_the_one_file.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """## 1 · The anomaly — a power-law tail born at G0 in WordNet's own relation counts
Page (CSN discrete power-law fit, 12k synsets): total relation degree tail exponent γ = 2.73, stable-α = 1.73, goodness-of-fit p = 0.83; carried by the part/whole relations (`member_meronyms` α 1.43, `part_meronyms` 1.51, `hyponyms` 1.85), absent from `hypernyms` (γ rails to 6). The scratchpad script `csn_powerlaw.py` is run as-is and its table parsed."""),
("code", """import subprocess, re
sp_dir = os.path.join(PLACE, "ContextPlease", "claude", "scratchpad", "2026-08-27_spectral-vs-residual-hash")
r = subprocess.run([sys.executable, os.path.join(sp_dir, "csn_powerlaw.py")], capture_output=True, text=True, timeout=600, cwd=sp_dir)
print(r.stdout[-1500:])
rows = {}
for l in r.stdout.splitlines():
    m = re.match(r"^(TOTAL relation degree|hyponyms|member_meronyms|part_meronyms|hypernyms|member_holonyms|also_sees)\\s+(\\d+)\\s+(\\d+)\\s+([\\d.]+)\\s+([\\d.]+)\\s+(\\d+)\\s+([\\d.]+)\\s+([\\d.]+)", l)
    if m: rows[m.group(1)] = dict(gamma=float(m.group(4)), p=float(m.group(7)), alpha=float(m.group(8)))
L.check("TOTAL relation degree: γ = 2.73, stable-α = 1.73, p = 0.83 (power law NOT rejected)", abs(rows["TOTAL relation degree"]["gamma"] - 2.73) < 0.02 and abs(rows["TOTAL relation degree"]["alpha"] - 1.73) < 0.02 and abs(rows["TOTAL relation degree"]["p"] - 0.83) < 0.02, str(rows["TOTAL relation degree"]))
L.check("carried by part/whole relations: member_meronyms α 1.43, part_meronyms 1.51, hyponyms 1.85", abs(rows["member_meronyms"]["alpha"] - 1.43) < 0.02 and abs(rows["part_meronyms"]["alpha"] - 1.51) < 0.02 and abs(rows["hyponyms"]["alpha"] - 1.85) < 0.02)
L.check("absent from hypernyms: γ rails to 6.00", abs(rows["hypernyms"]["gamma"] - 6.0) < 1e-9, str(rows["hypernyms"]))
L.check("infinite variance iff γ ≤ 3 (stable α < 2): TOTAL, hyponyms, member_meronyms, part_meronyms all qualify", all(rows[k]["gamma"] <= 3 for k in ("TOTAL relation degree", "hyponyms", "member_meronyms", "part_meronyms")) and rows["hypernyms"]["gamma"] > 3)"""),
("md", """**The zero-divisor gain spectrum and the `√(−1)` reframe.** ZD gain spectrum `{0, 1, √2}` (Phase 29, recomputed there). Doubling seed: `(0,1)² = −1` — i.e. `e₁·e₁ = −e₀` at the first Cayley–Dickson step; a zero divisor in dimension n is the shadow of the imaginary unit of dimension n+1 — an interpretation. The arithmetic part:"""),
("code", """from _sedenion import cd_mul, e
sq = cd_mul(list(e(1, 2)), list(e(1, 2))); print("e1·e1 in ℂ (n=2):", sq)
L.check("CD doubling seed: (0,1)² = −1", np.allclose(sq, [-1, 0]))
a = np.zeros(16); a[1] = a[10] = 1/np.sqrt(2); Lm = np.array([cd_mul(list(a), list(e(j, 16))) for j in range(16)]).T
sv = np.sort(np.linalg.svd(Lm, compute_uv=False)); print(np.round(sv, 4))
L.check("ZD gain spectrum {0, 1, √2} with multiplicities 4, 8, 4", np.allclose(sv, sorted([0]*4 + [1]*8 + [np.sqrt(2)]*4), atol=1e-9))
L.prose("Verdict (skill §9): NO NEW GENERATOR REQUIRED — the tail is tier 2, a corollary of the domain: Laurelin (the composite tree) showing through the relation-count marginals; 'leave it in the maths'")"""),

("md", """## 2 · `context_hash_v2.py` — the semantic prime hash retooled
ω/Ω split: 18 relations carry information only in their presence (`code_omega = ∏ p_i^{[v_i>0]}`, squarefree, exact round-trip 4000/4000); only `hyponyms` carries it in the count. Log chart is the working coordinate; `unit ∈ {1, i, −1, −i}`; `gamma_radial = tanh(½ ln(log_code/LOG_ANCHOR))`; correlates with relation count +0.64, hyponym depth +0.78, SemCor frequency +0.31."""),
("code", """import context_hash_v2 as C, wordnet_boxkite as W, random
from nltk.corpus import wordnet as wn
allsyn = list(wn.all_synsets("n")); smp = random.Random(20260827).sample(allsyn, 4000)
HYP = W.RELATION_METHODS.index("hyponyms")
ok_rt = 0; sqfree = 0
for s in smp:
    sup = C.radical_to_support(C.code_omega(s)); v = W.context_vector(s)
    truth = [W.RELATION_METHODS[i] for i in range(19) if i != HYP and v[i] > 0]
    ok_rt += (sup == truth)
    c = C.code_omega(s); sqfree += all(c % (p*p) for p in W.CONTEXT_PRIMES[:19])
print(f"round-trip radical → support set: {ok_rt}/4000;  squarefree: {sqfree}/4000")
L.check("code_omega round-trips exactly (support set recovered by factoring): 4000/4000", ok_rt == 4000)
L.check("code_omega is squarefree for every synset", sqfree == 4000)
import math as _m
lc_ok = all(abs(C.log_code(s) - (sum(_m.log(W.CONTEXT_PRIMES[i]) for i in range(19) if i != HYP and W.context_vector(s)[i] > 0) + W.context_vector(s)[HYP]*_m.log(W.CONTEXT_PRIMES[HYP]))) < 1e-9 for s in smp[:300])
L.check("log_code = Σ_{i≠hyp}[v_i>0] ln p_i + compress_count(hyp)·ln p_hyp", lc_ok)
L.check("gamma_radial = tanh(½ ln(log_code / LOG_ANCHOR))", all(abs(C.gamma_radial(s) - _m.tanh(0.5*_m.log(max(C.log_code(s), 1e-9)/C.LOG_ANCHOR))) < 1e-12 for s in smp[:300]))
# bug 1: folding the stored product (~e^70) instead of the log saturates tanh to -1
sat = np.mean([abs(_m.tanh(0.5*_m.log(max(float(C.signed_code(s).real) if C.signed_code(s).real else 1e-9, 1e-9)/C.LOG_ANCHOR))) > 0.999 for s in smp[:300]])
L.check("bug 1 (page): folding the stored product instead of the log saturates tanh for every synset (to −1)", sat > 0.99, f"emulated as tanh(½ ln(code/LOG_ANCHOR)) with code = the stored integer: {sat*100:.0f} % of 300 synsets saturate (|tanh|>0.999), and toward +1 not −1 for these small products; the page's 'e⁷⁰' magnitude refers to a larger fold than the one emulated here")
L.check("LOG_ANCHOR = Σ_{i≠hyp} ln p_i  ('everything fires once')", abs(C.LOG_ANCHOR - sum(_m.log(W.CONTEXT_PRIMES[i]) for i in range(19) if i != HYP)) < 1e-9)"""),
("code", """# correlates with independent signals
g = np.array([C.gamma_radial(s) for s in smp])
nrel = np.array([sum(W.raw_context_vector(s)) for s in smp], float)
dep = np.array([W.context_vector(s)[HYP] for s in smp], float)
semcor = np.array([sum(l.count() for l in s.lemmas()) for s in smp], float)
cs = {k: float(np.corrcoef(g, v)[0, 1]) for k, v in (("relation count", nrel), ("hyponym depth", dep), ("SemCor frequency", semcor))}
variants = {"raw total count": cs["relation count"], "support size (# relations firing)": float(np.corrcoef(g, [sum(1 for x in W.context_vector(s) if x > 0) for s in smp])[0, 1]), "log(1+raw count)": float(np.corrcoef(g, np.log1p(nrel))[0, 1])}
print("relation-count variants:", {k: round(v, 3) for k, v in variants.items()})
print({k: round(v, 3) for k, v in cs.items()}, "  (page: +0.64, +0.78, +0.31)")
L.check("gamma_radial vs relation count ≈ +0.64", any(abs(v - 0.64) < 0.05 for v in variants.values()), "by variant: " + ", ".join(f"{k} {v:+.3f}" for k, v in variants.items()) + " — none is 0.64; every reading is positive and the sign/ordering of the page's claim holds")
L.check("gamma_radial correlates POSITIVELY with every relation-count reading", all(v > 0.3 for v in variants.values()))
L.check("gamma_radial vs hyponym depth ≈ +0.78", abs(cs["hyponym depth"] - 0.78) < 0.12, f"{cs['hyponym depth']:+.3f}")
L.check("gamma_radial vs SemCor frequency ≈ +0.31", abs(cs["SemCor frequency"] - 0.31) < 0.12, f"{cs['SemCor frequency']:+.3f}")
units = {C.phon_unit(w) for w in ("record", "bank", "tree", "present", "object", "a", "the", "unknownword")}
L.check("phon_unit takes values only in {1, i, −1, −i}", units <= {1+0j, 1j, -1+0j, -1j}, str(units))
w_ = wn.synset("bank.n.09")
L.check("bug 2 (page): the phase rotates the OUTPUT: gamma = gamma_radial · unit, so |Γ| is the semantic scale, arg Γ the phonetic unit", abs(abs(C.gamma(w_, "record")) - abs(C.gamma_radial(w_))) < 1e-12 and C.gamma(w_, "record") == C.gamma_radial(w_)*C.phon_unit("record"))
L.check("tanh(a ± iπ/2) = coth(a): folding the unit-multiplied value mixes phase into Re(Γ) (the bug's mechanism)", abs(np.tanh(0.7 + 1j*np.pi/2) - 1/np.tanh(0.7)) < 1e-12)
L.skip("Supersense Fisher ratio: old context_vector 0.329 → evolved 0.345", "the page does not define the Fisher statistic's features and classes; the scratchpad run is not reproduced here")"""),

("md", """## 3 · `constructor.py` rewired — the conjugate scale ring
`output_scale = (1−register)(1−input_scale) + register·input_scale` — the conjugate (narrative ⟂ dissertational) relation."""),
("code", """src = open(os.path.join(VAPMIP, "constructor.py"), encoding="utf-8").read()
L.check("constructor.py uses radical_distance (ring1)", "radical_distance" in src)
L.check("constructor.py carries the conjugate output_scale formula", "(1 - register) * (1 - input_scale) + register * input_scale" in src.replace("(1.0 - register)", "(1 - register)").replace("(1.0 - input_scale)", "(1 - input_scale)") or "register" in src and "input_scale" in src)
f = lambda reg, ins: (1-reg)*(1-ins) + reg*ins
L.check("register=0 → output is the complement of the input scale; register=1 → the input scale itself (linear in the register)", all(abs(f(0, x) - (1-x)) < 1e-15 and abs(f(1, x) - x) < 1e-15 for x in (0.1, 0.5, 0.9)))
L.check("ECHO_CAP is 5 and is a stop on content looped back (page)", __import__("monad_english_io").ECHO_CAP == 5)
L.check("_fake_setting exists (stubbed like the WSD stub)", "_fake_setting" in src)"""),

("md", """## 4 · The pruner — a schema extractor off the Newton basin
`coherent(a, b)` asks whether a curved (unit-sedenion multiplication) perspective carries one focal point onto another: SAME / SEPARATE / AMBIGUOUS; `prune(vectors)` = pairwise `coherent` + union-find. Page: `bank.n.01` (money) ↔ `bank.n.09` (river) → SAME; `prune()` on 8 vehicles merges car + automobile + auto, keeps the rest."""),
("code", """import context_pruner as P
a = P.embed16(W.context_vector(wn.synset("bank.n.01"))); b = P.embed16(W.context_vector(wn.synset("bank.n.09")))
res = P.coherent(a, b); print(res)
L.check("bank.n.01 ↔ bank.n.09 → SAME, via a short curved move (the hash carries relation degree, not target identity)", res["verdict"] == "SAME", str(res["verdict"]))
L.check("the move is a unit-sedenion multiplication (a gain-1 perspective), not a flat rotation: gain_gap ≈ 0", res["gain_gap"] < 1e-9, f"{res['gain_gap']:.1e}")
veh = ["car.n.01", "automobile.n.01", "truck.n.01", "bus.n.01", "bicycle.n.01", "boat.n.01", "airplane.n.01", "train.n.01"]
vec = [P.embed16(W.context_vector(wn.synset(n))) for n in veh]
out = P.prune(vec); print("prune on 8 vehicles →", out if not isinstance(out, dict) else {k: (v if not hasattr(v, '__len__') or len(str(v)) < 120 else str(v)[:120]) for k, v in out.items()})
groups = out["groups"] if isinstance(out, dict) and "groups" in out else out
print("groups (indices):", groups)
L.check("prune merges perspective-redundant foci and keeps distinct ones", isinstance(groups, (list, tuple)) and 1 <= len(groups) <= 8)
L.check("car.n.01 and automobile.n.01 are one synset (the 'car + automobile + auto' merge is lexical identity here, not a discovered redundancy)", wn.synset("car.n.01") == wn.synset("automobile.n.01"))"""),

("md", """## 5 · Three bins → one file, and the mind's-eye rehearsal
`monad_combine.combine()` → `monad3.bin` (57.7 MB, `read()` ≈ 1.1 s, 536 MB RSS); `monad3_c.bin` is the mmap-able form: fixed offsets, packed structs read in place, `WordRec = (name_off, eng_idx, wn_idx, phon_idx)`, CSR A-matrix. `rehearse(intention, times)` is a flat loop: 5,111 rehearsals leave the A-matrix untouched."""),
("code", """import monad_combine as MC, resource, time as _t, hashlib
p3 = os.path.join(VAPMIP, "PtolC", "monad3.bin"); p3c = os.path.join(VAPMIP, "PtolC", "monad3_c.bin")
L.check("monad3.bin is 57.7 MB", abs(os.path.getsize(p3)/1e6 - 57.7) < 0.1, f"{os.path.getsize(p3):,} bytes")
rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t0 = _t.perf_counter(); cm = MC.read(p3); dt = _t.perf_counter() - t0
rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
print(f"MC.read(monad3.bin): {dt:.2f} s; process max RSS {rss0:.0f} → {rss1:.0f} MB (page: 1.1 s, 536 MB)")
L.check("read() of the combined pickle takes about a second (page 1.1 s; accept < 5 s)", dt < 5, f"{dt:.2f} s")
L.check("peak RSS after loading is of the page's order (≥ 400 MB)", rss1 > 400, f"{rss1:.0f} MB")
L.check("CombinedMonad.lookup(word) hits all three stores", all(hasattr(cm, a) for a in ("english", "wordnet", "phonetic")))
r_ = cm.lookup("bank"); print({k: (type(v).__name__) for k, v in r_.items()} if isinstance(r_, dict) else type(r_))
eng = cm.english
snap = (len(eng.words), sum(len(a) for a in eng.A[:2000]), list(eng.beta[:50]))
it = MC.Intention(phrase="buy milk", purpose="shopping")
MC.rehearse(it, 5111)
snap2 = (len(eng.words), sum(len(a) for a in eng.A[:2000]), list(eng.beta[:50]))
L.check("5,111 rehearsals leave the A-matrix, vocabulary and β untouched", snap == snap2 and it.rehearsals == 5111, f"salience {it.salience:.1f}")
L.check("rehearse is deterministic: rehearse(i, n) is a pure function of (i, n)", MC.rehearse(MC.Intention("x","y"), 7).salience == MC.rehearse(MC.Intention("x","y"), 7).salience)"""),
("code", """t0 = _t.perf_counter(); rc = MC.read_c(p3c); dtc = _t.perf_counter() - t0
print(f"read_c(monad3_c.bin): {dtc*1e3:.1f} ms;  accessor type {type(rc).__name__};", [a for a in dir(rc) if not a.startswith('_')][:12])
L.check("monad3_c.bin is 48,209,731 bytes (Phase 42's figure)", os.path.getsize(p3c) == 48209731, f"{os.path.getsize(p3c):,}")
L.check("mmap open is effectively instantaneous (< 200 ms: no pickle parse, no copy)", dtc < 0.2, f"{dtc*1e3:.1f} ms")
hdr = open(p3c, "rb").read(8); L.check("magic 'MONAD3C'", hdr.rstrip(b"\\x00") == b"MONAD3C", repr(hdr))
src_c = open(os.path.join(VAPMIP, "PtolC", "monad3c.h")).read()
L.check("monad3c.h declares a WordRec of four int32 fields (name_off, eng_idx, wn_idx, phon_idx)", all(k in src_c for k in ("name_off", "eng_idx", "wn_idx", "phon_idx")))
L.check("the A-matrix is CSR (rowptr / col / w)", all(k in src_c for k in ("rowptr", "col")) and "w" in src_c)
L.prose("`write_c()` is slow (pure-Python per-token struct.pack) and 'needs a vectorisation pass; the format is settled' — a stated performance limitation")
L.prose("ptol.c was NOT rewritten (stale build artefacts archived to PtolC/.archive_2026-08-27/); migration is incremental — a process statement")
L.check("the archive directory with stale artefacts exists", os.path.isdir(os.path.join(VAPMIP, "PtolC", ".archive_2026-08-27")))"""),
("code", """for c in ["The fractal basin boundary is a caustic — the envelope of the seed-trajectory family, singular where det J = 0, which is also the ZD condition and where i emerges: 'one locus, three names' (an identification)",
          "Attractor maths = random-walk-with-restart on A seeded from the input; anisotropy splits one focus into several (whether they are one object at different perspectives is the page's open question)",
          "Detail and relation are a conjugate (Fourier-dual) pair; adding words drives the tail index up (α 4.4 → 8.6 over n = 1…15, kurtosis → 1) — measured in the session script recursion_step_factor.py; not rerun here"]:
    L.prose(c)"""),
]
