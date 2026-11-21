"""horner_vs_arithmetic.py (2026-11-20): is arithmetic coding (3Blue1Brown, 'This algorithm changed how I think about compression') useful in the hyperindexing system?
The Horner address of a word is the exact base-B interval index: v = v*B + digit.  In Vsauce's Hyperwebster (Banach-Tarski video) every word sits in the volume of its first letter, and removing that letter gives back
the whole book: the word tree is self-similar, each child an equal 1/B slice.  Arithmetic coding is the SAME tree with UNEQUAL slices (width = probability).  So the question is how many characters fit in the fixed 256-bit
address (8 x uint32; standing spec, not questioned here) under equal slices (Horner, B = 27 or 95) against model-weighted slices.
PROTOCOL (registered before running): train a static order-k character model on 10 of the 11 Wernicke corpus texts, test on the held-out 11th (Flatland); alphabet = 26 letters + space + end mark;
prediction P1: order-3 bits/char < 3.2 (Horner base 27 = 4.755, base 95 = 6.570); P2: more than 70 characters fit in 256 bits at order 3 (Horner: 53 / 38); P3: exact arithmetic intervals keep lexicographic order when the end mark sorts first.
Run: ../SedenionSpectralRelativity/.venv/bin/python horner_vs_arithmetic.py"""
import os, re, math, random, collections
from fractions import Fraction as Fr
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Wernicke", "corpus", "texts"); HELD = "abbott_flatland_1884.txt"
def clean(s):
    s = re.sub(r"[^a-z ]+", " ", s.lower()); return re.sub(r" +", " ", s).strip()
txt = {f: clean(open(os.path.join(T, f), errors="ignore").read()) for f in sorted(os.listdir(T)) if f.endswith(".txt")}
train = [v for k, v in txt.items() if k != HELD]; test = txt[HELD]
ALPHA = "$ abcdefghijklmnopqrstuvwxyz"; IDX = {c: i for i, c in enumerate(ALPHA)}; M = len(ALPHA)          # '$' = end mark, FIRST so order is lexicographic
out = [f"corpus: {len(train)} train texts, {sum(map(len,train)):,} chars; held out {HELD}, {len(test):,} chars"]
def fit(k):
    cnt = collections.defaultdict(lambda: [0] * M)
    for s in train:
        ctx = "^" * k
        for ch in s: cnt[ctx[-k:] if k else ""][IDX[ch]] += 1; ctx += ch
    return cnt
def prob(cnt, ctx, ch, k):                                   # KT (Dirichlet 1/2) over the 28 symbols, the model that never assigns zero
    c = cnt.get(ctx[-k:] if k else "", None); n = sum(c) if c else 0
    return ((c[IDX[ch]] if c else 0) + .5) / (n + M / 2)
models = {k: fit(k) for k in (0, 1, 2, 3, 4)}
words = [w for w in test.split()]
out.append(f"\nbits per character on the held-out text (spaces included; uniform: base 27 = {math.log2(27):.3f}, base 95 = {math.log2(95):.3f}):")
bpc = {}
for k, cnt in models.items():
    bits = 0.0; ctx = "^" * k
    for ch in test: bits += -math.log2(prob(cnt, ctx, ch, k)); ctx += ch
    bpc[k] = bits / len(test); out.append(f"   order {k}: {bpc[k]:.3f} bits/char   table cells {len(cnt)*M:,}")
k = 3; cnt = models[k]
def phrase_bits(s):
    b = 0.0; ctx = "^" * k
    for ch in s + "$": b += -math.log2(prob(cnt, ctx, ch, k)); ctx += ch
    return b
out.append("\nhow many characters fit in a 256-bit address (windows of the held-out text, phrase + end mark, order 3):")
for N in (30, 38, 53, 70, 90, 110, 130):
    ws = [test[i:i + N] for i in range(0, len(test) - N, 37)]; ok = sum(phrase_bits(w) <= 256 for w in ws) / len(ws)
    out.append(f"   {N:>3} chars: {100*ok:5.1f}% of {len(ws):,} windows fit   (Horner base 27 fits {int(256/math.log2(27))}, base 95 fits {int(256//math.log2(95))})")
# lexicographic order of exact arithmetic intervals (P3)
def interval(w):
    lo, width, ctx = Fr(0), Fr(1), "^" * k
    for ch in w + "$":
        c = cnt.get(ctx[-k:], [0] * M); tot = 2 * sum(c) + M; i = IDX[ch]
        lo += width * Fr(sum(2 * x + 1 for x in c[:i]), tot); width *= Fr(2 * c[i] + 1, tot); ctx += ch
    return lo, width
sample = sorted(set(random.Random(7).sample(words, 4000)))[:1500]; iv = [interval(w) for w in sample]
mono = all(iv[i][0] < iv[i + 1][0] for i in range(len(iv) - 1)); disj = all(iv[i][0] + iv[i][1] <= iv[i + 1][0] for i in range(len(iv) - 1))
out.append(f"\nlexicographic order kept by the exact intervals: {mono}; intervals pairwise disjoint (injective): {disj}  ({len(sample)} sorted distinct words)")
wb = [-math.log2(Fr(*(lambda lw: (lw[1].numerator, lw[1].denominator))(interval(w)))) for w in sample[:600]]
out.append(f"single words (mean over 600 distinct): arithmetic {sum(wb)/len(wb):.1f} bits vs Horner base 27 {sum(math.log2(27)*(len(w)+0) for w in sample[:600])/600:.1f} bits (letters only)")
out.append("\nPREDICTIONS: P1 order-3 < 3.2 bits/char: " + ("HELD" if bpc[3] < 3.2 else "FAILED") + f" ({bpc[3]:.3f}); P3: " + ("HELD" if mono and disj else "FAILED"))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "horner_vs_arithmetic.txt"), "w").write("\n".join(out) + "\n"); print("\n".join(out))
