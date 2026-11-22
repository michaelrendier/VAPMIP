"""learning_curve.py (2026-11-21): does the existing co-occurrence field (A-matrix) learn to predict English as it is taught? Run from VAPMIP/ with .venv/bin/python; output learning_curve.txt (rounds 1-3)."""
import sys, glob, math, re, collections, time
sys.path.insert(0, '.')
import monad_english_io as M
files = sorted(glob.glob('Currentwork/Wernicke/corpus/texts/*.txt'))
toks_by = []
for f in files:
    t = open(f, encoding='utf-8', errors='ignore').read().lower()
    toks_by.append(re.findall(r"[a-z]+(?:'[a-z]+)?", t))
# fixed held-out: last 5% of each work (up to 4000 tokens each); training chunks: the first 95% of each work, fed in 6 rounds
held = []; train = []
for ts in toks_by:
    cut = int(len(ts) * .95); held.append(ts[cut:cut + 3000]); train.append(ts[:min(cut, 60000)])
me = M.MonadEnglish(version='t', vocab={}, words=[], beta=[], E=[], A=[], age=[], fire_count=[], stratum=[], psi_prev=[0.0]*16, word_count=0, correction_mask={})
def evaluate(me):
    V = len(me.words); hit1 = hit10 = n = 0; bits = 0.0; seen = 0
    for ts in held:
        for a, b in zip(ts, ts[1:]):
            i, j = me.idx(a), me.idx(b); n += 1
            if i is None or j is None: bits += math.log2(V + 1 + 1); continue
            row = me.A[i]; tot = sum(row.values()) + 0.01 * (V + 1)
            p = (row.get(j, 0.0) + 0.01) / tot; bits += -math.log2(p); seen += 1
            if row:
                top = sorted(row, key=lambda k: -row[k])[:10]
                hit1 += (top[0] == j); hit10 += (j in top)
    return {'vocab': V, 'edges': sum(len(r) for r in me.A), 'bits_per_word': round(bits / n, 2), 'top1': round(hit1 / n, 3), 'top10': round(hit10 / n, 3), 'in_vocab': round(seen / n, 3)}
print('held-out tokens', sum(len(h) for h in held))
rounds = 4
for r in range(rounds):
    t = time.time()
    for ts in train:
        a = int(len(ts) * r / rounds); b = int(len(ts) * (r + 1) / rounds)
        M.hear(me, ' '.join(ts[a:b]))
    ws = [w for row in me.A for w in row.values()]
    top1w = sum(1 for w in ws if w >= 0.999) / max(1, len(ws))
    print('round', r + 1, evaluate(me), 'share of edges with weight 1.0: %.3f' % top1w, '(%.0fs)' % (time.time() - t))
# does frequency show? compare weight of a very frequent pair with a rare pair
i, j = me.idx('of'), me.idx('the'); k = me.idx('abbot')
print("weight A[of][the]=", me.A[i].get(j), " fire_count[of]=", me.fire_count[i], " | an adjacent pair seen once: weights near", sorted(set(round(w, 2) for w in list(me.A[k].values())[:5])))
