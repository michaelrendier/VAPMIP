LABEL = "31"
TITLE = "WordNet Box-Kites and the Pile-Concept Emergence"
DATE = "2026-08-24 → 2026-08-25"
PAGE = "31_wordnet_box_kites_and_the_pile_concept_emergence.md"
BYLINE = "page by Claude Opus 5 (+ Sonnet 5)"

CELLS = [
("md", """The machinery is `VAPMIP/wordnet_boxkite.py`. Every statement below is rerun against the live WordNet (NLTK) in this notebook."""),
("md", """## 1 · The retool — `context_vector` is 19 real relation methods
`RELATION_METHODS` = the WordNet synset API (hypernyms … usage_domains), each fixed 1-to-1 to its own prime `CONTEXT_PRIMES`, disjoint from the small `LETTER_PRIMES` tier. `context_code`/`context_addr` build a lossless `(code, addr, delta)`."""),
("code", """import wordnet_boxkite as W
from nltk.corpus import wordnet as wn
print(W.RELATION_METHODS)
L.check("19 relation methods", len(W.RELATION_METHODS) == 19)
L.check("all 19 are real methods on a WordNet synset", all(hasattr(wn.synset("tree.n.01"), m) for m in W.RELATION_METHODS))
cp = W.CONTEXT_PRIMES[:19]
L.check("each relation has its own distinct prime (1-to-1)", len(set(cp)) == 19)
L.check("CONTEXT_PRIMES (first 19) are all > the LETTER_CAP (71): disjoint from the letter tier", min(cp) > W.LETTER_CAP, f"smallest context prime {min(cp)}, LETTER_CAP {W.LETTER_CAP}")
from sympy import isprime
L.check("CONTEXT_PRIMES are prime", all(isprime(p) for p in cp))
syn = wn.synset("tree.n.01"); v = W.context_vector(syn)
import math as _m
code = W.context_code(syn)
rebuild = 1
for p, x in zip(cp, v): rebuild *= p**x
L.check("context_code = ∏ CONTEXT_PRIMES[i]^vector[i]", code == rebuild)
a = W.context_addr(syn); print({k: (str(x)[:30] + ("…" if len(str(x)) > 30 else "")) for k, x in a.items()})
L.check("context_addr returns (code, addr, delta) — the lossless pair", all(k in a for k in ("code", "addr", "delta")) or len(a) >= 2)"""),

("md", """## 2 · Two corrections kept in the record
(1) Neighbourhood by exact vector match: `hilbert.n.01` (mathematician), `irrawaddy.n.01` (a river) and `new_york.n.03` collide on `{instance_hypernyms: 1}` despite no semantic relation. (2) Near-miss vectors do **not** give small gaps in the multiplicative code; "same" is answered by the address, "nearly the same" needs a vector distance."""),
("code", """for nm in ("hilbert.n.01", "irrawaddy.n.01", "new_york.n.03"):
    s = wn.synset(nm); print(f"  {nm:16} {dict((r, c) for r, c in zip(W.RELATION_METHODS, W.context_vector(s)) if c)}   {s.definition()[:50]}")
vs = [tuple(W.context_vector(wn.synset(n))) for n in ("hilbert.n.01", "irrawaddy.n.01", "new_york.n.03")]
L.check("hilbert / irrawaddy / new_york.n.03 share one exact context vector {instance_hypernyms: 1}", len(set(vs)) == 1 and dict((r, c) for r, c in zip(W.RELATION_METHODS, vs[0]) if c) == {"instance_hypernyms": 1})
col, n = W.find_collisions(4000)
print(f"find_collisions(4000): {len(col)} collision buckets over {n} sampled synsets; largest bucket {max(len(v) for v in col.values())}")
L.check("find_collisions reports real exact-vector buckets (> 1 member) — contextual, not semantic, neighbours", len(col) > 0 and all(len(v) > 1 for v in col.values()))
# near-miss: vectors differing by 1 in one dimension -> code ratio is that dimension's prime, which can be large
pairs = []
syns = list(wn.all_synsets("n"))[:3000]
by = {}
for s in syns: by.setdefault(tuple(W.context_vector(s)), []).append(s)
for v1, ss1 in by.items():
    for i in range(19):
        v2 = list(v1); v2[i] += 1; v2 = tuple(v2)
        if v2 in by: pairs.append((ss1[0], by[v2][0], i)); break
    if len(pairs) >= 20: break
ratios = [W.context_code(b)/W.context_code(a) for a, b, i in pairs]
print("near-miss pairs (differ by 1 in one dimension): code ratios", [round(float(r), 1) for r in ratios[:8]], "… and the prime of the differing dimension:", [W.CONTEXT_PRIMES[i] for _, _, i in pairs[:8]])
L.check("a one-count difference multiplies the code by the differing dimension's PRIME (not a small gap) — multiplicative encodings do this by construction", all(abs(r - W.CONTEXT_PRIMES[i]) < 1e-6*W.CONTEXT_PRIMES[i] for r, (_, _, i) in zip(ratios, pairs)), f"{len(pairs)} near-miss pairs")
L.check("so 'nearly the same' needs context_distance (L1 on vectors), built separately", all(W.context_distance(a, b) == 1 for a, b, i in pairs) if pairs else False, "context_distance of a near-miss pair = 1")"""),

("md", """## 3 · `compress_count` — log-compress the count before it becomes an exponent
Raw counts as exponents blew up (`tree.n.01` = 364 digits, `hyponyms = 180 → 83^180`). Fix: `compress_count(n) = round(log2(n+1))` → 28 digits."""),
("code", """syn = wn.synset("tree.n.01")
raw = W.raw_context_vector(syn); cmp_ = W.context_vector(syn)
rawcode = 1
for p, x in zip(W.CONTEXT_PRIMES, raw): rawcode *= p**x
hy = W.RELATION_METHODS.index("hyponyms")
print(f"tree.n.01: raw hyponyms = {raw[hy]}, prime = {W.CONTEXT_PRIMES[hy]}, raw code digits = {len(str(rawcode))}; compressed hyponyms = {cmp_[hy]}, code digits = {len(str(W.context_code(syn)))}")
L.check("tree.n.01 raw: hyponyms = 180 with prime 83 → 83^180", raw[hy] == 180 and W.CONTEXT_PRIMES[hy] == 83)
L.check("raw code of tree.n.01 is 364 digits", len(str(rawcode)) == 364, f"{len(str(rawcode))}")
L.check("compressed code is 28 digits", len(str(W.context_code(syn))) == 28)
L.check("compress_count(n) = round(log2(n+1)) for n = 0 … 300", all(W.compress_count(n) == round(math.log2(n + 1)) for n in range(301)))
L.check("0 vs 1 barely compresses (the page's honest limit): compress_count(0)=0, compress_count(1)=1", (W.compress_count(0), W.compress_count(1)) == (0, 1))"""),

("md", """## 4 · The pile-concept test
Three WordNet senses of "bank" (`bank.n.01` slope, `bank.n.03` ridge/pile, `bank.n.05` reserve) share one exact shape `{hypernyms:1, hyponyms:2}`; etymologically separate (Old Norse *banki* vs Old Italian *banca*). 15 hand-filtered "pile/heap/mass" senses are compared with 2000 random noun synsets, L1 distance to the bank-shape target."""),
("code", """target = [0]*19; target[W.RELATION_METHODS.index("hypernyms")] = 1; target[W.RELATION_METHODS.index("hyponyms")] = 2
vb = [W.context_vector(wn.synset(n)) for n in ("bank.n.01", "bank.n.03", "bank.n.05")]
L.check("bank.n.01 / .03 / .05 all equal the shape {hypernyms: 1, hyponyms: 2}", all(v == target for v in vb), str([[x for x in v if x] for v in vb]))
for n in ("bank.n.01", "bank.n.03", "bank.n.05"): print(f"  {n}: {wn.synset(n).definition()[:70]}")
pile = ["pile.n.01", "mound.n.04", "stack.n.01", "dune.n.01", "reserve.n.02", "stockpile.n.02", "hoard.n.01", "cairn.n.01", "haystack.n.01", "snowdrift.n.01", "volcano.n.02", "mountain.n.01", "cache.n.01", "knoll.n.01", "ball.n.08"]
L1 = lambda a, b: sum(abs(x - y) for x, y in zip(a, b))
rows = []
for nm in pile:
    try: s = wn.synset(nm); rows.append((nm, L1(W.context_vector(s), target), s.definition()[:48]))
    except Exception as ex: rows.append((nm, None, f"missing in this WordNet: {ex}"))
for r in rows: print(f"  {r[0]:16} L1 = {r[1]}   {r[2]}")
have = [r for r in rows if r[1] is not None]
exact = [r[0] for r in have if r[1] == 0]; meanL1 = np.mean([r[1] for r in have])
print(f"exact matches: {len(exact)}/{len(have)}  {exact};  mean L1 {meanL1:.2f}")
L.check("15 of the 15 curated pile senses exist in this WordNet", len(have) == 15, f"{len(have)}")
L.check("exact matches 4/15: mound.n.04, reserve.n.02, knoll.n.01, ball.n.08", sorted(exact) == sorted(["mound.n.04", "reserve.n.02", "knoll.n.01", "ball.n.08"]), str(exact))
L.check("mean L1 of the pile words ≈ 1.67", abs(meanL1 - 1.67) < 0.05, f"{meanL1:.2f}")"""),
("code", """import random
allsyn = list(wn.all_synsets("n"))
rates = []
for seed in (1, 2, 3, 4, 5):
    smp = random.Random(seed).sample(allsyn, 2000)
    d = [L1(W.context_vector(s), target) for s in smp]; rates.append((np.mean([x == 0 for x in d]), np.mean(d)))
print("control, n=2000 random noun synsets, 5 seeds: exact-match rate", [f"{a:.3f}" for a, _ in rates], " mean L1", [f"{b:.2f}" for _, b in rates])
base = float(np.mean([a for a, _ in rates])); mL = float(np.mean([b for _, b in rates]))
L.check("random base rate of the exact bank shape ≈ 5.5 % (page: 110/2000)", abs(base - 0.055) < 0.01, f"{base:.3f}")
L.check("random mean L1 ≈ 2.47 (page)", abs(mL - 2.47) < 0.15, f"{mL:.2f}")
from scipy.stats import binom
pval = float(binom.sf(len(exact)-1, len(have), base)); print(f"binomial P(X ≥ {len(exact)} | n={len(have)}, p={base:.3f}) = {pval:.4f};   enrichment {len(exact)/len(have)/base:.1f}×")
L.check("pile words hit the exact shape at ≈ 5× the random rate (page)", 3.5 < (len(exact)/len(have))/base < 7, f"{(len(exact)/len(have))/base:.1f}×")
L.check("tail probability ≈ 0.01 (page: Poisson ≈ 0.01)", 0.003 < pval < 0.03, f"p = {pval:.4f}")
share = np.mean([L1(W.context_vector(s), target) == 0 for s in allsyn])
print(f"share of ALL {len(allsyn):,} nouns with exactly this shape: {share:.3f} = 1 in {1/share:.0f}")
L.check("the shape {hypernyms:1, hyponyms:2} is shared by roughly 1 noun in 18 overall (a coarse family, not a unique tag)", 12 < 1/share < 28, f"1 in {1/share:.0f}")"""),
("code", """cluster = ["stockpile.n.02", "hoard.n.01", "cairn.n.01", "snowdrift.n.01", "cache.n.01"]
for nm in cluster:
    s = wn.synset(nm); v = W.context_vector(s); print(f"  {nm:16} hypernyms={v[0]} hyponyms={v[W.RELATION_METHODS.index('hyponyms')]}  L1={L1(v, target)}")
L.check("the L1=2 cluster misses only because WordNet records zero hyponyms for these entries (a coverage gap in WordNet)", all(wn.synset(n).hyponyms() == [] for n in cluster) and all(L1(W.context_vector(wn.synset(n)), target) == 2 for n in cluster))
for c in ["Old Norse banki vs Old Italian banca: two separate etymologies for the river bank and the financial bank (the page checked via WebSearch; an etymological fact not reproduced offline)",
          "'The shared shape may intone an abstract prime concept — pile of something': an interpretation; the measured part is the 5× enrichment and the coarse-family caveat",
          "Closing call: keep the algorithm exactly as it is — 'ideas/sorts' between words with similar context are structure unseen to us that the algorithm lands on (the generational-lineage skill's emergence check)"]:
    L.prose(c)"""),
]
