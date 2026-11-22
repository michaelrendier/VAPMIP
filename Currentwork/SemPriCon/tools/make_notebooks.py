#!/usr/bin/env python3
"""make_notebooks.py — writes notebooks/0N_*.ipynb from the cell lists below.  Execute with:  python -m nbconvert --to notebook --execute --inplace notebooks/*.ipynb"""
import os, nbformat as nbf
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "notebooks")
def md(s): return nbf.v4.new_markdown_cell(s.strip("\n"))
def code(s): return nbf.v4.new_code_cell(s.strip("\n"))
SETUP = '''import os, sys, json, math, collections, re, hashlib
import numpy as np
sys.path.insert(0, os.path.abspath("../tools"))
import ptol_bin, monad_py as mp
ROOT  = os.path.abspath("..")
STORE = os.path.join(ROOT, "dirty", "monad_wordnet_v4_20260519.bin")
CBIN  = os.path.join(ROOT, "build", "PtolC_eb28ce8", "ptolemy")
SPACES = "[\\u200b\\u2009\\u2008\\u2007\\u2006\\u2005\\u2004\\u2003]"   # the eight Fermat separators'''
NB = {}

NB["01_the_store"] = [
md("""# 01 — The store: what `monad_wordnet_v4_20260519.bin` contained
**Scope.** This notebook only *reads* the PTOL state file that the May-2026 C monad (`PtolC/` at commit `eb28ce8`, v1.215) loaded when it produced the
screenshot reply `holcussamestuffseemy`. Nothing is modified, tuned or sanitised. Reader: `tools/ptol_bin.py`, a copy of the layout in `state.c: state_load`.

| section | bytes | meaning |
|---|---|---|
| header | 36 (v4) | `"PTOL"`, version, N, vocab_size, A_size, word_count, threshold f64, affect f32 |
| β | 8·N | depth per zero slot (f64) |
| age | 4·N | steps since last activation (i32) |
| vocab | variable | per *occupied slot*: `idx u32, wlen u16, E f64, home u8, gen u8, prose_seen u8, word` |
| A | 16·A_size | `i u32, j u32, w f64`, always `i < j` |"""),
code(SETUP),
code('''d = ptol_bin.load(STORE)
print({k: d[k] for k in ("version","N","vocab_size","A_size","word_count","threshold","affect")})
print("file bytes", d["bytes_total"], " consumed by the reader", d["bytes_consumed"], " -> every byte accounted for:", d["bytes_total"]==d["bytes_consumed"])
print("sha256", hashlib.sha256(open(STORE,"rb").read()).hexdigest())'''),
md("""The header matches the three numbers printed on the screenshot (`vocab=24485  A=6825748  wc=121914388`), so this is the file that was loaded."""),
md("""## What a "vocabulary" entry is
The store has **one word per occupied slot** (25 000 slots), not one per word it has met. Which word a slot displays is decided in `monad_learn_ex`:
`if (!present || E > vocab[idx].E) replace` — the arrival with the highest `E` wins. (Notebook 02 shows `E` is a function of spelling alone.)"""),
code('''V = d["vocab"]; words = [v[1] for v in V]
print("occupied slots", len(V), "of", d["N"])
print("word length distribution of the displayed words:", sorted(collections.Counter(len(w) for w in words).items()))
print("non-ASCII words:", sum(1 for w in words if not w.isascii()))'''),
md("""## Scripts: is there any multilingual content?"""),
code('''A = json.load(open(os.path.join(ROOT,"dirty","monad_wordnet_v4_20260519.assessment.json")))
print(json.dumps(A["scripts"], ensure_ascii=False, indent=1)[:600])'''),
md("""All 24 485 displayed words are ASCII. Notebook 03 shows why none could have been anything else: `tok_split` uses `isalpha()` in the C locale, so a non-ASCII
byte is a *separator*, never part of a word."""),
md("## Field health (the project's own `eval_checkpoint.py` measures)"),
code('''print(json.dumps({k: A[k] for k in ("field","eval_checkpoint")}, indent=1))'''),
md("""`eval_checkpoint.py` verdict rule: CONVERGED = pollution < 1 % and entropy and Gini in band; PASS = pollution < 20 %. Here: pollution 5.04 %, entropy 88.68 % of max
(natural band 85–92), Gini 0.7564 (natural band 0.60–0.80). → **PASS, not CONVERGED.**

## Token sanitiser (2026-10-17 ruleset) — same tool that wrote the `*.POISON.md` notes"""),
code('''for k, n in list(A["sanitiser"]["tiers"].items())[:10]:
    print(f"{k:34} {n:6}  {A['sanitiser']['samples'][k][:8]}")
print("quarantined:", A["sanitiser"]["quarantined"], f"({A['sanitiser']['quarantined_pct']} %)")'''),
md("""`B:candidate_evidence_pending` is "not found in WordNet" — 75 % of the displayed words. Most of those are *slot winners that are not words*
(`azv`, `xxa`, `uxp`, …): see notebook 06, item 2."""),
md("## Where the screenshot's words and the prompt's words sit"),
code('''for w, hit in A["probes"].items(): print(f"{w:13}", hit if hit else "— not displayed by any slot")'''),
md("""`tree`, `water`, `name`, `is` are **not** displayed anywhere, because the slot each of them addresses to is held by a different word:"""),
code('''for w in ["tree","water","name","is","ptolemy","philadelphos"]:
    i, E = mp.word_coords(w); print(f"{w:13} -> z#{i:<6} E={E:.4f}   slot displays: {dict(zip((v[0] for v in V),(v[1] for v in V))).get(i)!r}")'''),
]

NB["02_the_address"] = [
md("""# 02 — The address: `monad_word_coords` and `generate_zeros`
C source: `monad.c` lines 146–190 (commit `eb28ce8`). Port: `tools/monad_py.py: word_coords, generate_zeros`. Ported **as-is**, defects included.

```c
uint64_t v = 0;
for (p = surface; *p; p++) { ci = (c >= 32 && c < 127) ? c - 32 + 1 : 0;  v = v * 95ULL + ci; }
if (v > 0) v--;
double seed = fmod((double)v * MONAD_PHI, 1.0);
*idx = (int)(seed * N);               *E = D_STAR + seed * (OMEGA_ZS - D_STAR);
```"""),
code(SETUP),
md("## Step by step for `holcus`"),
code('''s = "holcus"; v = 0
for c in s.encode():
    ci = c-32+1; v = v*95 + ci; print(f"  {chr(c)}  digit {ci:3d}  v = {v}")
v -= 1
x = float(v) * mp.PHI
print("v-1 =", v, "  (double)v*phi =", repr(x), "  fmod ->", repr(math.fmod(x,1.0)))
print("word_coords ->", mp.word_coords(s), "   d* + seed*(Omega-d*) with seed =", math.fmod(x,1.0))'''),
md("## The port reproduces the store exactly\nEvery one of the 24 485 displayed words, re-addressed from its spelling, lands on the slot and energy the store holds."),
code('''m = mp.Monad.from_bin(STORE)
bad = sum(1 for i,v in m.vocab.items() if mp.word_coords(v["word"])[0]!=i or abs(mp.word_coords(v["word"])[1]-v["E"])>1e-12)
print("mismatches:", bad, "of", len(m.vocab))'''),
md("""## Defect 1 — the seed loses its fractional bits as words get longer
`(double)v * φ` is a 53-bit float. Once the product exceeds 2⁵² the spacing between doubles is ≥ 1, so `fmod(x, 1.0)` is **exactly 0**. Before that the number
of usable fractional bits shrinks by one per factor of two. Result: the number of *distinct* slots a word length can reach falls from thousands to one."""),
code('''from nltk.corpus import wordnet as wn
lem = sorted({l.lower() for s in wn.all_synsets() for l in s.lemma_names() if l.isalpha() and l.isascii()})
by = collections.defaultdict(list)
for w in lem:
    if mp.token_accept(w): by[len(w)].append(w)
rows = []
for n in range(2,16):
    ws = by[n]; ids = [mp.word_coords(w)[0] for w in ws]
    rows.append((n, len(ws), len(set(ids)), sum(1 for i in ids if i==0)))
print("len  lemmas  distinct-slots  at-slot-0")
for r in rows: print(f"{r[0]:3d} {r[1]:7d} {r[2]:14d} {r[3]:10d}")'''),
code('''import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6,3.4))
ax.semilogy([r[0] for r in rows], [r[2] for r in rows], "o-"); ax.set_xlabel("word length (letters)"); ax.set_ylabel("distinct slots reached")
ax.axhline(25000, ls=":", c="grey"); ax.set_title("monad_word_coords: address resolution by word length"); fig.tight_layout()
fig.savefig(os.path.join(ROOT,"figures","address_resolution_by_length.png"), dpi=160); print("saved")'''),
md("""Every word of 8 letters or more addresses to **z#0 with E = d\\*** (11 117 of 11 117 eight-letter lemmas, 10 913 of 10 913 nine-letter, …). That includes `philadelphos`.
The 2026-05-17 baseline assessment reports `philadelphos` as its "deepest word, zero #0"; this is the arithmetic that put it there.
A second, smaller effect: for lengths 6 and 7 the seed is quantised (6 letters: 5 271 distinct seeds; 7 letters: 64)."""),
code('''for w in ["philadelphos","ptolemy","holcus","seemy","carre"]:
    print(f"{w:13} -> {mp.word_coords(w)}")
print("slot 0 on the store displays:", m.vocab[0]["word"])'''),
md("""## Defect 2 — `uint64` wraps at ~10 letters
`95¹⁰ ≈ 6·10¹⁹ > 2⁶⁴`. In C the accumulator wraps silently; the port masks to 64 bits to match. This is moot in practice because defect 1 has already zeroed the seed for such words,
but it is a second reason a long word's address cannot be trusted.

## What a non-ASCII word does
Every byte outside 32..126 contributes digit **0**, so a non-ASCII string (UTF-8 bytes) is a run of zero digits:"""),
code('''for w in ["tree","arbre","baum","木","δένδρο","شجرة","ağaç"]:
    print(f"{w!r:10} bytes={list(w.encode())[:8]}  word_coords={mp.word_coords(w)}")'''),
md("""`木` → three bytes, all digit 0 → `v = 0` → z#0. Any word made only of non-ASCII bytes lands on z#0 with E = d\\*; mixed words (`ağaç`) lose the non-ASCII letters.
In the C engine this path is never reached from text (the tokenizer discards those bytes first — notebook 03), only from a direct call.

## The zeros themselves
`generate_zeros` tabulates the first 20 and *computes* the rest with Newton's method on the Riemann–von Mangoldt count (`N(t) = n`). They are approximations, not tabulated zeros."""),
code('''import mpmath
print("  n     true zero    monad z[n-1]     error")
for n in [21, 100, 1000, 5000, 25000]:
    z = float(mpmath.zetazero(n).imag); print(f"{n:6d} {z:12.4f} {m.zeros[n-1]:14.4f} {abs(z-m.zeros[n-1]):9.4f}")'''),
]

NB["03_learn"] = [
md("""# 03 — Learning: `tok_split`, `token_accept`, `monad_learn_ex`, the A-matrix
C source: `tokenizer.c`; `filter.c`; `monad.c` lines 252–550 (`monad_a_add`, `dirac_pole`, `monad_learn_ex`). Port: `tools/monad_py.py`.
Checked against the compiled binary: same text → both write a state file → the files are compared (`tools/verify_learn_against_c.py`)."""),
code(SETUP),
md("""## Tokeniser
`isalpha(c) || c == '\\''` on an `unsigned char`, C locale: **ASCII letters and apostrophe only**; everything else (digits, punctuation, every byte ≥ 128) ends a word.
Lower-cased; a token must be ≥ 2 characters and must not start with an apostrophe."""),
code('''for s in ["The tree is a plant.", "arbre 木 baum δένδρο", "don't 'quoted' x ab", "ağaç dört"]:
    print(f"{s!r:28} -> {mp.tok_split(s)}")'''),
md("## `token_accept` (prose rules)"),
code('''tests = ["tree","a","qgt","bcdfg","xxxxxxxxxxxxxxxxxxxxxxxxx","deadbeef","ban'","aeiou","schzr","strengths","qwrtypsdfghjkl"]
for t in tests: print(f"{t:28} accepted={mp.token_accept(t)}")'''),
md("Among the 24 485 words the store displays, how many would today's prose filter reject? (They were admitted by the earlier, pre-vowel-fix filter or by the WordNet path.)"),
code('''m = mp.Monad.from_bin(STORE)
rej = [v["word"] for v in m.vocab.values() if not mp.token_accept(v["word"])]
print(len(rej), "of", len(m.vocab), rej[:20])'''),
md("""## Learning one sentence, shown
For each accepted token: address → `β += E²·α·|sin γ|·π/2` (cap 7.552) → the slot displays the highest-`E` arrival. Then every pair within 12 accepted tokens gets
`w = Eᵢ·Eⱼ·couple / ((|γᵢ−γⱼ| + gap)·d)` where `d` is the text distance, `couple = 2` if both zeros share the Dirac pole sign (else 1), `gap = 0.000707`."""),
code('''g = mp.Monad()
text = "The tree is a plant. Water is a liquid that the tree drinks."
g.learn(text)
print("accepted tokens -> slot, E, beta")
for w in mp.tok_split(text):
    if mp.token_accept(w):
        i, E = mp.word_coords(w); print(f"  {w:8} z#{i:<6} E={E:.4f} gamma={g.zeros[i]:10.3f} beta={g.beta[i]:.6f}  slot displays {g.vocab[i]['word']!r}")
A = g._A_dict(); print(len(A), "edges; strongest:")
for (i,j),w in sorted(A.items(), key=lambda kv:-kv[1])[:6]: print(f"  {g.vocab[i]['word']}({i}) <-> {g.vocab[j]['word']}({j})  w={w:.4e}   key=(i<<15)|j={(i<<15)|j}")'''),
md("""`A` is stored once per unordered pair with `i < j`; the key packs both indices into 30 bits, which is only possible while `N < 2¹⁵ = 32 768` (N = 25 000 here)."""),
md("## Verification against the compiled C binary (three texts, ground state each time)"),
code('''import verify_learn_against_c as v
for t in ["The tree is a plant. Water is a liquid that the tree drinks. Arbre means tree in French.",
          "I am Ptolemy. I am named after Ptolemy the Second, Philadelphos, who commissioned the Septuagint.",
          "Holcus is a genus of grasses; velvet grass, Yorkshire fog. Qgt xz bcdfg aeiou 12345 http://x.y/z tree tree tree."]:
    print(v.compare(t))'''),
md("`vocab_equal`, `edge_keys_equal` true and both error columns 0.0: the port is exact on this path."),
]

NB["04_speak"] = [
md("""# 04 — Speaking: `monad_speak` / `monad_speak_wick`, stage by stage
C source: `monad.c` lines 560–1045. Port: `Monad.speak`, `Monad.speak_wick`, `near_canonical`, `fermat_space`.
`-W` = `monad_speak_wick` = `monad_speak` with `affect` forced to −1, so the emission gate is `cos(γ/2 − π/2) = sin(γ/2) > 0`."""),
code(SETUP),
md("## Run the screenshot prompt and expose every stage"),
code('''m = mp.Monad.from_bin(STORE); tr = {}
out = m.speak_wick("what is your name", 50, tr)
print(repr(out)); print(re.split(SPACES, out))'''),
md("""### Stage 1 — hear
Each token is addressed (`monad_wm_get`). A word the store already displays keeps its stored `E`; any other word is computed, and flagged `[new]` in the C trace."""),
code('''for w, idx, E, known in tr["hear"]:
    print(f"{w:6} z#{idx:<6} gamma={m.zeros[idx]:10.3f}  E={E:.4f}  beta={m.beta[idx]:.3f}  known={known}   slot displays {m.vocab.get(idx,{}).get('word')!r}")'''),
md("""### Stage 2 — seed, spread, two A-passes
`J[idx] += β·E²·exp(−λ·age)`; each seeded zero then leaks `J·exp(−|Δn|)` to ±3 neighbours; then every A edge is crossed twice from the *pre-propagation* field `J0`
(`i→j` weighted by `β[j]`, then `j→i` weighted by `β[i]`), edge weight clamped to `1/gap`."""),
code('''print("lag_ratio", tr["lag_ratio"], " sum_V", f'{tr["sum_V"]:.4e}', " sum_T", f'{tr["sum_T"]:.4f}', " -> actual_max", tr["actual_max"])
print("J_max", f'{tr["J_max"]:.3f}', " J_floor (1% of J_max)", f'{tr["J_floor"]:.3f}')'''),
md("""### Stage 3 — length from a Lagrangian ratio
`actual_max = 4 + int(max_tokens · ΣT/(ΣT+ΣV))`, `ΣV = Σ β·E²` over every occupied slot (≈ 5.7·10³ here), `ΣT = Σ E²` over the query's slots (< 1).
The ratio is ≈ 10⁻⁴, so `actual_max = 4` for any short prompt on this store."""),
md("### Stage 4 — Fermat pointer and the golden-angle step"),
code('''print("pointer z#", tr["pointer"], " gamma", round(m.zeros[tr["pointer"]],3), "(median gamma of the query's zeros, nearest zero)")
print("golden step = round(N/phi^2) =", tr["golden_step"])'''),
md("### Stage 5 — first word (\"demotic\") and the walk"),
code('''print("target_E = (sumV/(sumV+sumT))*Omega =", tr["target_E"], "  chosen slot", tr["demotic"], "word", m.vocab[tr["demotic"]]["word"], "E", m.vocab[tr["demotic"]]["E"])
for e in tr["emitted"]: print(e)'''),
md("""`('walk', slot, stored word, displayed word, J, separator)`. `near_canonical` may replace the stored word by a neighbour within ±50 slots (`same`, `stuff` here were the slots' own words).
The separator is `U+200B … U+2003` chosen by `J/J_max` in eight bands — the "Fermat space". The sequence `holcus​same​stuff​seemy` carries zero-width spaces: the screenshot shows no spaces for that reason."""),
md("## Equivalence with the compiled binary (8 prompts, byte for byte)"),
code('''import verify_against_c as vc
ok = 0
for p in ["what is your name","can you hear what i am typing","who are you","what is a tree","good morning","the cat sat on the mat","how do you do","tell me about water"]:
    c = vc.c_reply(p); mm = mp.Monad.from_bin(STORE); py = mm.speak_wick(p, 50); ok += (c == py)
    print("MATCH" if c == py else "DIFF ", repr(p), "->", re.split(SPACES, c))
print(ok, "/ 8 identical")'''),
]

NB["05_the_name"] = [
md("""# 05 — "What is your name?": what the engine did, with the open items closed
Questions left open by the 2026-10-17 trace: (1) why is `holcus` first for every prompt, (2) why does its slot clear `J_floor`, (3) was the identity text learned into this store."""),
code(SETUP),
code('''m = mp.Monad.from_bin(STORE); H = mp.word_coords("holcus")[0]
print("holcus ->", mp.word_coords("holcus"), " seed =", (mp.word_coords("holcus")[1]-mp.D_STAR)/(mp.OMEGA_ZS-mp.D_STAR), "= 8074/8192 =", 8074/8192)'''),
md("""## (2) Why the slot clears `J_floor`: it is a hub
The slot has 18 268 A-neighbours (the median slot has 150) and is the 5th best-connected slot of 25 000. It shares an edge with all four query slots, so it receives
weight in the A-passes whatever the prompt."""),
code('''deg = np.bincount(np.concatenate([m.Ai, m.Aj]), minlength=25000)
print("degree of holcus slot", deg[H], " rank", int((deg>deg[H]).sum())+1, " median degree", int(np.median(deg)), " top-5 degrees", np.sort(deg)[::-1][:5])
q = [a[0] for a in m.hear_raw("what is your name")]
print("direct edges to the query slots:", [(int(i),int(j),round(float(w),4)) for i,j,w in zip(m.Ai,m.Aj,m.Aw) if (i==H and j in q) or (j==H and i in q)])'''),
md("""## The slot is the slot of the word *in*
Which words address to z#24639? Every WordNet lemma and every function word is tested; two do. The slot's displayed word is whichever has the higher `E`."""),
code('''from nltk.corpus import wordnet as wn
lem = sorted({l.lower() for s in wn.all_synsets() for l in s.lemma_names() if l.isalpha() and l.isascii()})
cand = sorted({(mp.word_coords(w)[1], w) for w in lem + ["in","of","the","and","to","a","is"] if mp.token_accept(w) and mp.word_coords(w)[0]==H}, reverse=True)
for E, w in cand: print(f"{w:8} E = {E!r}")
print("E difference:", cand[0][0]-cand[1][0])'''),
md("""`holcus` beats `in` by about 1·10⁻⁶ in `E` and takes the label; `in` is one of the most frequent words in English, so its slot is a hub. The five best-connected slots are all slots of function words:"""),
code('''order = np.argsort(-deg)[:8]
fw = ["the","and","of","to","in","a","is","that","it","for","as","with","was","by","on","at","be"]
for i in order:
    print(f"z#{int(i):<6} degree {int(deg[i]):6d}  displayed {m.vocab.get(int(i),{}).get('word')!r:10}  function words addressing here: {[w for w in fw if mp.word_coords(w)[0]==int(i)]}")'''),
md("""## (1) Why it is first: the selector, not the prompt
The first word is the slot, among those with `J > J_floor` and an open gate, whose stored `E` is closest to `target_E = (ΣV/(ΣV+ΣT))·Ω`. Because `ΣT ≪ ΣV`, `target_E ≈ Ω = 0.5671`
for any short prompt. `holcus` has `E = 0.5625`, the closest available.

First word over many prompts (random 1–6 word prompts drawn from the store's own words, fresh state each time):"""),
code('''import random; random.seed(7)
W = [v["word"] for v in m.vocab.values() if mp.token_accept(v["word"])]
first = collections.Counter(); lens = collections.Counter()
for t in range(150):
    q = " ".join(random.sample(W, random.randint(1,6)))
    mm = mp.Monad.from_bin(STORE) if t == 0 else mm
    mm.age = [0]*25000; mm.affect = 0.0; mm.last_pointer = 0
    ws = re.split(SPACES, mm.speak_wick(q, 50)); first[ws[0]] += 1; lens[len(ws)] += 1
print(first.most_common(6)); print("reply lengths:", dict(lens))'''),
md("""`holcus` is first in 92 of 150 random prompts and in all 8 of the standard prompts. Others (`yack`, …) win when `holcus`'s gate or `J` fails for that prompt, or when another slot's `E`
is nearer `target_E`. Reply length is 4 in 140 of 150; shorter replies occur when fewer than 3 walk candidates pass the gates.

## (3) Was the identity text learned into this store?
`PTOLEMY_IDENTITY` (`monad.c` lines 97–139) is learned only with `-i`. Parse it out of the C source, learn it from ground state, and ask whether each of its edges exists in the store with at least that weight."""),
code('''src = open(os.path.join(ROOT,"src","PtolC_eb28ce8","monad.c")).read()
body = src.split("static const char *PTOLEMY_IDENTITY =")[1].split(";\\n")[0]
ident = "".join(re.findall(r'"((?:[^"\\\\]|\\\\.)*)"', body)).encode().decode("unicode_escape")
print(len(ident), "chars:", ident[:120], "...")
g = mp.Monad(); g.learn(ident); IA = g._A_dict()
store = {(int(i),int(j)): float(w) for i,j,w in zip(m.Ai,m.Aj,m.Aw)}
present = [k for k in IA if k in store]; geq = [k for k in present if store[k] >= IA[k]*(1-1e-9)]
print("identity edges:", len(IA), " present in the store:", len(present), " with weight >= identity's own contribution:", len(geq))'''),
md("""If the store had been built without `-i`, only chance overlap would appear. Edge density of the store is 6 825 748 / (25 000·24 999/2) = 2.18 %, so about 14 of the 646 would be expected by chance; all 646 are present."""),
code('''rare = [k for k in IA if IA[k] > 0 and k not in store]
print("identity edges absent from the store:", len(rare))
for w in ["ptolemy","philadelphos","septuagint","noether","riemann","prime","zero","holcus"]:
    i,E = mp.word_coords(w); print(f"{w:13} z#{i:<6} slot displays {m.vocab.get(i,{}).get('word')!r}  degree {int(deg[i])}")'''),
md("""## What this establishes and what it does not
- The reply is produced entirely by the stages in notebook 04; the port reproduces it exactly.
- `holcus` first = the label of the slot where the word *in* lives (a 1·10⁻⁶ difference in `E` between the two words that address there) + that slot being a hub + the selector's `E`-nearest rule + an `E` close to Ω. None of those four reads the prompt.
- The identity text was learned into this store: all 646 edges it would create are present, each at least as heavy as the identity's own contribution (chance expectation at the store's edge density is ≈ 14).
- Words 2–4 come from the golden-angle walk from the pointer through slots with `J > J_floor`; their `J` comes from the A-matrix learned from text.
- Whether this *is* self-understanding is not a code question; the code shows the mechanism that produced the sequence."""),
]

NB["06_shortcomings"] = [
md("""# 06 — Shortcomings, measured
Each item: what the code does, one measurement, one consequence. Nothing is fixed here; this is the list the next version is engineered against."""),
code(SETUP),
code('''m = mp.Monad.from_bin(STORE)
from nltk.corpus import wordnet as wn
lem = sorted({l.lower() for s in wn.all_synsets() for l in s.lemma_names() if l.isalpha() and l.isascii()})
lem = [w for w in lem if mp.token_accept(w)]
print(len(lem), "WordNet single-token ASCII lemmas pass the prose filter")'''),
md("## 1. Address resolution collapses with word length\nSee notebook 02. 8+ letters → slot 0."),
code('''print("lemmas at slot 0:", sum(1 for w in lem if mp.word_coords(w)[0]==0), "of", len(lem))
print("distinct slots reached by all lemmas:", len({mp.word_coords(w)[0] for w in lem}), "of 25000")'''),
md("## 2. The displayed word is the highest-`E` arrival in the slot, so most displayed words are not words anyone meant"),
code('''by = collections.defaultdict(list)
for w in lem: by[mp.word_coords(w)[0]].append(w)
inbin = sum(1 for w in lem if w in m.wm)
print("WordNet lemmas that are their slot's displayed word:", inbin, "of", len(lem), f"({100*inbin/len(lem):.1f} %)")
print("mean lemmas per occupied slot (excluding slot 0):", round(np.mean([len(v) for i,v in by.items() if i]),2))'''),
md("""Consequence: `is`→`nanti`, `name`→`emite`, `tree`→`typhon`, `water`→`defrg`. The *weights* (β, A) live on the slot and are shared by every word that addresses there; only the label is arbitrary.

## 3. The zeros are approximations
Notebook 02: error up to 1.8 at n = 21, 0.28 at n = 25 000.

## 4. Fixed reply length
`actual_max = 4 + int(50·ΣT/(ΣT+ΣV))` with ΣV ≈ 5.7·10³ → 4 for short prompts."""),
code('''beta = np.array(m.beta); E = np.array([m.vocab[i]["E"] if i in m.vocab else 0 for i in range(25000)])
print("sum_V (all occupied slots):", float(np.sum(np.where(E>0, beta*E*E, 0))))'''),
md("## 5. β saturates\nβ is capped at 7.552 and most occupied slots reach the cap, so β no longer discriminates between slots."),
code('''occ = np.array(sorted(m.vocab))
print("slots at the cap:", int((beta[occ] >= 7.55).sum()), "of", len(occ), f"({100*(beta[occ]>=7.55).mean():.1f} %)")'''),
md("""## 6. The tokenizer discards every non-ASCII byte
Greek, Chinese, Arabic, Hebrew, Coptic, accented Latin letters all become separators. `ağaç` → `a`, `a` (both dropped, 1 char). A multilingual test through this engine must use ASCII orthography.

## 7. Documentation and code disagree (one case)
The comment before the demotic selection says "first output word chosen from first 200 qualifying walk candidates"; the code scans all N slots. The code is what ran.

## 8. The word map is not persisted
`state_save` writes vocab entries only, so after a reload `monad_wm_get` knows only the displayed words; every other word is `[new]` and its `E` is recomputed. Same slot, same `E` (the
address is deterministic), so the reply is unchanged — but the `[new]` flag in the trace is not evidence about whether the word was ever seen.

## 9. Open: the separator
The screenshot reply has no visible spaces (zero-width separators) while the same binary on a pipe prints a visible U+2003 em space in one prompt of the standard eight. Which band appears depends on `J/J_max`.
Whether a tty changes anything was not tested."""),
md("""## 10. `prose_seen` belongs to the slot, not to the displayed word
`monad_learn_ex` sets `prose_seen` (0 none, 1 prose, 2 WordNet text, 3 both) on the *slot* each time any word addresses there. A slot flagged 3 ("verified common") may display a word that was never in WordNet, because a different word that shares the slot was."""),
code('''ps = collections.Counter(v["ps"] for v in m.vocab.values())
print("prose_seen over occupied slots:", dict(ps))
flag3_not_wn = [v["word"] for v in m.vocab.values() if v["ps"]==3 and not wn.synsets(v["word"])]
print(len(flag3_not_wn), "slots flagged 3 display a word with no WordNet synset, e.g.", flag3_not_wn[:12])'''),
]

import sys
for name, cells in NB.items():
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    nb = nbf.v4.new_notebook(); nb.cells = cells
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbf.write(nb, os.path.join(OUT, name + ".ipynb")); print("wrote", name)
