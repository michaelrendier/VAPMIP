LABEL = "23"
TITLE = "The Addressing Bug, the Common Mode, and the Third Face"
DATE = "2026-07-28"
PAGE = "23_the_addressing_bug_the_common_mode_and_the_third.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """## 1 · The addressing bug: `fmod((double)v·φ, 1.0)` past 2⁵³
The old `monad_word_coords` computed a base-95 Horner integer `v`, then `seed = fmod((double)v·φ, 1.0)`. A double has a 53-bit mantissa: `95⁸ = 6.6×10¹⁵` fits under `2⁵³ = 9.0×10¹⁵`, `95⁹` does not. Past 2⁵³ the low bits — the only bits `fmod(·,1)` depends on — are gone. The fix is Knuth multiplicative hashing in exact integer arithmetic. `VAPMIP/monad_addressing.py` holds both versions; run them over the real WordNet lemma list."""),
("code", """L.check("95⁸ < 2⁵³ < 95⁹ (the page's arithmetic)", 95**8 < 2**53 < 95**9, f"95⁸ = {95**8:.3e}, 2⁵³ = {2**53:.3e}, 95⁹ = {95**9:.3e}")
import monad_addressing as A
from nltk.corpus import wordnet as wn
words = sorted({x.lower() for x in wn.all_lemma_names() if x.isalpha() and len(x) >= 2})
print(f"{len(words):,} unique alphabetic WordNet lemmas (the page measured 101,916 tokens of the WordNet build)")
res = {}
for nm, f in (("old", A.old_coords), ("new", A.new_coords)):
    idx = [f(w)[0] for w in words]; seeds = [f(w)[1] for w in words]
    res[nm] = (A.chi_square_uniform(idx, A.N_ZEROS), A.ks_uniform(seeds), A.collision_profile(words, f))
    c, k, p = res[nm]
    print(f"{nm}: χ²={c['chi2']:,.1f} (z={c['z']:+,.1f})   KS D={k['D']:.4f} (crit {k['critical_95']:.4f})   max pile-up {p['max_pileup']:,}   at idx 0: {p['at_idx0']:,}   occupied {p['occupied']:,} (expected {p['expected_occupied']:,.0f})")
L.check("old: χ² enormous, KS 'NOT UNIFORM'", res['old'][0]['z'] > 1000 and res['old'][1]['D'] > res['old'][1]['critical_95'])
L.check("new: χ² ≈ df=99 (|z| < 3), KS uniform", abs(res['new'][0]['z']) < 3 and res['new'][1]['D'] < res['new'][1]['critical_95'])
L.check("new: occupancy within 2 % of the balls-in-bins expectation", abs(res['new'][2]['ratio_to_expected'] - 1) < 0.02, f"ratio {res['new'][2]['ratio_to_expected']:.4f}")
L.check("old: a large fraction of all words piled onto idx 0 (the page: 62,961 of 101,916 = 62 %)", res['old'][2]['at_idx0']/len(words) > 0.4, f"{res['old'][2]['at_idx0']:,} of {len(words):,} = {res['old'][2]['at_idx0']/len(words)*100:.0f} %")"""),
("code", """# survival by word length under the old hash: seed collapses to exactly 0.0 for len ≥ 8
lb_old = A.length_bias(words, A.old_coords)
print(f"{'len':>4} {'n':>7} {'frac seed==0 (old)':>20}")
for Ln in (5, 6, 7, 8, 9, 10, 12): 
    r = lb_old.get(Ln); 
    if r: print(f"{Ln:4d} {r['n']:7d} {r['frac_exactly_zero']:20.3f}")
L.check("old hash: every word of ≥ 9 letters has seed exactly 0.0", all(lb_old[Ln]['frac_exactly_zero'] > 0.99 for Ln in lb_old if Ln >= 9))
L.check("old hash: 6-letter words are mostly fine, 8+ are all dead (matches the page's survival table)", lb_old[6]['frac_exactly_zero'] < 0.5 and lb_old[8]['frac_exactly_zero'] > 0.95)
lb_new = A.length_bias(words, A.new_coords)
L.check("new hash: mean seed ≈ ½ at every length with ≥ 200 words", all(abs(r['mean_seed'] - 0.5) < 0.08 for r in lb_new.values() if r['n'] >= 200), "max deviation %.3f" % max(abs(r['mean_seed']-0.5) for r in lb_new.values() if r['n'] >= 200))
# the identity used to justify the fix: frac(v·φ) == frac(v/φ) because φ = 1 + 1/φ
import random; random.seed(1)
vs = [random.randrange(1, 10**6) for _ in range(1000)]
L.check("frac(v·φ) = frac(v/φ) for integer v (φ = 1 + 1/φ)", all(abs(((v*MONAD_PHI) % 1) - ((v/MONAD_PHI) % 1)) < 1e-6 for v in vs) if (MONAD_PHI := (1+5**.5)/2) else False)
L.check("round(2⁶⁴/φ) = 0x9E3779B97F4A7C15 (Knuth's constant)", round(2**64/((1+5**.5)/2)) in (0x9E3779B97F4A7C15, 0x9E3779B97F4A7C15 + 0) or abs(round(2**64/((1+5**.5)/2)) - 0x9E3779B97F4A7C15) < 2**12, "double precision gives the leading 53 bits; the constant is exact as used")"""),
("md", """### The STILL-OPEN capacity claim: 101,916 tokens into 25,000 zeros ≈ 4:1
Pigeonhole: with N = 25,000 slots, n tokens occupy `N(1−(1−1/N)ⁿ)` of them in expectation."""),
("code", """for n in (13752, 24551, 77477, 101916):
    exp = 25000*(1-(1-1/25000)**n); print(f"  {n:7,d} tokens → expected occupied slots {exp:8,.0f}  ({n/25000:.2f} tokens per slot)")
L.check("101,916 tokens into 25,000 zeros ≈ 4:1 (page)", abs(101916/25000 - 4.08) < 0.01)
L.prose("`E = D_STAR + seed·(Ω−D_STAR)` with a uniform seed makes E a frequency-blind tiebreaker; seating policy should key on frequency/β — the page records it as open and unchanged")
L.prose("Old .bin files 'silently mislead' under the new binary (state stores (word, idx) with old addresses) — a stated behaviour of the C binary; needs a stored old/new state pair to test")"""),

("md", """## 2 · The common mode: `project(text,k,σ) = c̄·W(n,k,σ) + D(content)`
Writing each character code as `c_i = c̄ + d_i`, the Dirichlet projection splits exactly into a part that depends only on the length and channel (`W`) and a content part. Page: content is 2–3 % of the signal, `cos(actual, common) = +0.9998`, and for `zzz` the content term is exactly 0."""),
("code", """P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
blue = lambda k: 4 <= k <= 7 or 12 <= k <= 15
def parts(text, sigma=0.5):
    s = np.frombuffer(text.encode(), np.uint8).astype(float); n = len(s); i = np.arange(1, n+1)
    W = np.array([(i**(-sigma) * (np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)])
    cbar = s.mean(); common = cbar*W
    full = np.array([(s * i**(-sigma) * (np.sin if blue(k) else np.cos)(2*np.pi*i/P[k])).sum() for k in range(16)])
    return full, common, full - common
f, c, d = parts("listen")
L.check("project = c̄·W + D(content) exactly (residual is D by construction)", np.allclose(f, c + d))
ws = [w for w in words if 4 <= len(w) <= 10][:3000:3]
cs, shares = [], []
for w in ws:
    f, c, d = parts(w); cs.append(float(f @ c/np.linalg.norm(f)/np.linalg.norm(c))); shares.append(np.linalg.norm(d)/np.linalg.norm(f))
print(f"{len(ws)} words: cos(actual, common) mean {np.mean(cs):.4f} (min {np.min(cs):.4f});  content share |D|/|v| median {np.median(shares)*100:.1f} %, 90th pct {np.percentile(shares,90)*100:.1f} %")
L.check("cos(actual, common) ≈ +0.9998 (page)", np.mean(cs) > 0.997, f"mean {np.mean(cs):.4f}")
L.check("content is a few percent of the signal (page: 2–3 %)", np.median(shares) < 0.08, f"median {np.median(shares)*100:.1f} %")
f, c, d = parts("zzz"); L.check("'zzz': content term exactly 0.0 (all characters equal the mean)", np.abs(d).max() < 1e-12, f"max |D| = {np.abs(d).max():.1e}")"""),
("code", """# cosine as a length detector: group |cos| by |len(a) − len(b)| over same-prompt-set pairs
home = scratch("ph23_")
ws2 = [w for w in words if 4 <= len(w) <= 12][:4000:10]
vec = {w: np.array(ptol_raw(w, "H", home)["scalars"]) for w in ws2[:300]}
import itertools
from collections import defaultdict
g = defaultdict(list)
for a, b in itertools.combinations(list(vec), 2):
    g[abs(len(a)-len(b))].append(abs(float(vec[a] @ vec[b])))
for dl in sorted(g): print(f"  |Δlen|={dl}: mean |cos| = {np.mean(g[dl]):.3f}  (n={len(g[dl])})")
means = [np.mean(g[k]) for k in sorted(g) if len(g[k]) >= 20]
L.check("mean |cos| falls monotonically as |Δlen| grows (cosine is a length detector)", all(a >= b - 0.01 for a, b in zip(means, means[1:])), f"{np.round(means, 3)}")
v_listen, v_silent = np.array(ptol_raw("listen","H",home)["scalars"]), np.array(ptol_raw("silent","H",home)["scalars"])
L.check("listen/silent cos ≈ 0.9997 (word order barely registers)", float(v_listen @ v_silent) > 0.999, f"{float(v_listen @ v_silent):.5f}")
hot, cat = np.array(ptol_raw("hot","H",home)["scalars"]), np.array(ptol_raw("cat","H",home)["scalars"])
L.check("same-length inputs give near-identical normalised state (max|v_hot − v_cat| ≈ 0.018)", abs(np.abs(hot-cat).max() - 0.018) < 0.02, f"{np.abs(hot-cat).max():.4f}")"""),
("md", """### Σ_RB redundancy and the d* claim, re-measured
Page: `s_rb[k] == s_rb[partner(k)]` identically (partner is an involution, product commutative) so only 8 of 16 entries are independent; and `J_red×J_blue = d* = 0.24600 conserved at all σ` is false — re-measured at [−0.0729, +0.1230]."""),
("code", """partner = lambda k: k+4 if (k < 4 or 8 <= k < 12) else k-4
r = ptol_raw("hello world", "H", home)
srb = np.array(r["sigma_rb"])
L.check("partner is an involution on the 16 channels", all(partner(partner(k)) == k for k in range(16)))
L.check("s_rb[k] == s_rb[partner(k)] for all 16 (so 8 independent entries)", all(abs(srb[k] - srb[partner(k)]) < 1e-9 for k in range(16)))
vals = []
for w in ws2[:200]:
    rr = ptol_raw(w, "H", home); v = np.array(rr["scalars"]); vals += [v[k]*v[partner(k)] for k in range(8)]
vals = np.array(vals); print(f"J_red×J_blue per channel over 200 words: min {vals.min():+.4f}, max {vals.max():+.4f}  (page: [−0.0729, +0.1230])")
L.check("J_red×J_blue = d* = 0.246 on every channel (the ptol.c header claim; the page retracts it)", np.all(np.abs(vals - 0.246) < 0.01), f"measured range [{vals.min():+.4f}, {vals.max():+.4f}] on 200 words; the page's re-measure was [−0.0729, +0.1230] on its own set")
L.check("ptol.c still carries the false statement in its header (page: 'still uncorrected')", "J_red × J_blue = d* = 0.24600" in open(os.path.join(VAPMIP, "PtolC", "ptol.c")).read(), "lines 13 / 280 of PtolC/ptol.c")"""),

("md", """## 3 · The third face: phonetic features over CMUdict (`phonetic_face.py`)
16 articulatory features; a word's vector is the **mean** over its phonemes, so length is designed out. Run the module's own diagnostics."""),
("code", """import phonetic_face as PF
sp = PF.PhoneticSpace()
print("CMUdict entries:", len(sp._dict))
L.check("CMUdict has 123,455 pronunciations (page)", len(sp._dict) == 123455, f"{len(sp._dict):,}")
mp_ = {(r['a'], r['b']): r['cos'] for r in PF.minimal_pairs_check(sp)}
for k, v in mp_.items(): print(f"  {k[0]:>6}/{k[1]:<6} cos = {v:+.4f}")
L.check("eight/ate (homophones, spelled differently): cos = +1.0000", abs(mp_[('eight','ate')] - 1.0) < 1e-9)
L.check("though/tough (spelled alike, sound different): cos ≈ +0.7591", abs(mp_[('though','tough')] - 0.7591) < 0.01, f"{mp_[('though','tough')]:.4f}")
L.check("the phonetic face ranks the spelled-alike pair BELOW the one-phoneme minimal pairs (it hears, it doesn't read)", mp_[('though','tough')] < min(mp_[('cat','bat')], mp_[('pin','bin')]))
page_words = ['hot','cold','up','down','light','dark','stone','river','engine','copper','quiet','orbit','iron','garden','day','night','good','bad','true','false','man','dog','water']
lb = PF.verify_no_length_bias(sp, page_words)
print("module's own 23-word list — spread of mean |cos| across phoneme-count groups:", round(lb['spread'], 6))
L.check("no length bias on the module's own word list: spread 0.0398 (page)", abs(lb['spread'] - 0.0398) < 0.001, f"{lb['spread']:.6f}")
rows = lb['by_phoneme_len_diff']; ms = [r['mean_abs_cos'] for r in rows.values() if r['n'] >= 3]
L.check("…and the trend is non-monotonic (the character encoder fell monotonically 0.994 → 0.868)", not all(a >= b for a, b in zip(ms, ms[1:])), str(np.round(ms, 3)))
big = [w for w in words if sp.pronunciation(w)][:400:2]
lb2 = PF.verify_no_length_bias(sp, big)
ms2 = [r['mean_abs_cos'] for r in lb2['by_phoneme_len_diff'].values() if r['n'] >= 3]
print(f"same test on {len(big)} alphabetical WordNet lemmas: spread {lb2['spread']:.4f}; groups {np.round(ms2, 3)}")
L.check("the small spread survives a 200-word alphabetical sample (spread < 0.06)", lb2['spread'] < 0.06, f"spread {lb2['spread']:.4f} (the 23-word list in the module is short; a bigger sample shows more variation — the face is not length-flat on every sample)")"""),
("code", """# etymology carries: ablaut pairs vs unrelated controls
from itertools import combinations
cos = lambda a, b: PF.cosine(sp.noun(a), sp.noun(b))
fam = [('drank','drunk'),('sing','sang'),('tooth','teeth'),('foot','feet'),('goose','geese'),('man','men'),('swim','swam'),('begin','began'),('ring','rang'),('sit','sat')]
ctrl = [('sing','desk'),('tooth','river'),('drank','mountain'),('foot','lamp'),('man','stone'),('swim','paper'),('begin','window'),('ring','table'),('sit','cloud'),('goose','chair')]
fm = np.mean([cos(a, b) for a, b in fam if sp.pronunciation(a) and sp.pronunciation(b)]); cm = np.mean([cos(a, b) for a, b in ctrl])
print(f"family mean {fm:.3f}   unrelated mean {cm:.3f}   (page: 0.958 vs 0.820)")
for a, b in fam[:4]: print(f"  {a}/{b}: {cos(a,b):.4f}")
L.check("families score above unrelated controls", fm > cm, f"{fm:.3f} vs {cm:.3f}")
L.check("the page's honest limit: sing/desk (unrelated) outscores foot/feet (a family)", cos('sing','desk') > cos('foot','feet'), f"sing/desk {cos('sing','desk'):.4f} vs foot/feet {cos('foot','feet'):.4f}")"""),
("md", """## 4 · The four negative translator constructions and the `hot → cold` artifact
`translator_discocat`, `translator_vsa`, `translator_monad.py`, `lio_monad.py` all failed the same way (common mode). The repo holds each as a module with its own tests; run what is cheap, and check the artifact directly: does `cold` rank near the top for `hot` in a plain length-controlled comparison?"""),
("code", """import glob
mods = {"translator_discocat": os.path.join(PLACE, "ValaQuenta", "modules", "translator_discocat"), "translator_vsa": os.path.join(PLACE, "ValaQuenta", "modules", "translator_vsa"),
        "translator_monad.py": os.path.join(VAPMIP, "translator_monad.py"), "lio_monad.py": os.path.join(VAPMIP, "lio_monad.py"), "phonetic_face.py": os.path.join(VAPMIP, "phonetic_face.py"), "discocat_corpus.py": os.path.join(VAPMIP, "discocat_corpus.py")}
for k, v in mods.items(): print(f"  {k:22} exists: {os.path.exists(v)}")
L.check("all four translator constructions + the phonetic face are present in the repos", all(os.path.exists(v) for v in mods.values()))
# the artifact: rank of 'cold' among 12 candidate words for 'hot' under the character-based vectors
cands = ["cold","told","word","gold","fold","ice","hat","hit","cat","dog","sun","warm"]
vh = np.array(ptol_raw("hot", "H", home)["scalars"])
rk = sorted(cands, key=lambda w: -float(vh @ np.array(ptol_raw(w, "H", home)["scalars"])))
print("candidates ranked by cosine to 'hot' (character-based ptol vectors):", rk)
L.check("'cold' is NOT the top antonym hit: its rank is driven by length, not meaning", rk[0] != "cold", f"top = {rk[0]!r}; 'cold' ranks {rk.index('cold')+1} of {len(rk)}")"""),
("code", """for c_ in ["New-device bring-up notes (proot Ubuntu aarch64: storage mount cannot hold the exec bit; Python 3.14 is PEP-668) — environment facts, not reproducible here",
           "`philadelphos` at z#0 with β=7.552 was an overflow artefact: the Phase-1 'deepest word' narrative should be read with that in mind (the page says so; the old .bin it came from is not re-run here)",
           "`prime_path` is not a path: |z_k| grows monotonically with prime size so ptol's spiral idx[] mostly sorts the primes (a claim about 1–3 inversions; checked below in Phase 26/27 notebooks where relevant)",
           "Kaiser–Squires inversion does not transfer (irreducibly 2D; s_rb pairs different primes)",
           "monad.h:9 'bijective base-95 Horner' is a hash, not a bijection (wraps at uint64): a documentation fact, true by inspection of the arithmetic above"]:
    L.prose(c_)"""),
]
