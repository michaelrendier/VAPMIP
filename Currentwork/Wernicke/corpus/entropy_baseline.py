"""entropy_baseline.py (2026-11-21): closed-class share and word-level entropy on the standard testing corpus.
Run from Currentwork/Wernicke/ with VAPMIP/.venv/bin/python corpus/entropy_baseline.py. Reads extractor/extract_v0.py (closed-class tables) and corpus/texts/.
A baseline for the orbweaver: bits per word under unigram and bigram models, last 10% of each work held out. Crude tokenizer, add-0.1 smoothing, no tuning."""
import re, sys, glob, math, collections, importlib.util, os
# load the closed-class tables from extract_v0 without running it as a script
src = open('extractor/extract_v0.py', encoding='utf-8').read()
names = ['DET','PREP','ADV_CLOSED','PRON','BE','WH','COORD','MODAL']
ns = {}
for nme in names:
    m = re.search(r'^(%s)\s*=\s*(set\(.*?\)|\{.*?\}|frozenset\(.*?\))\s*$' % nme, src, re.M | re.S)
    if m:
        try: ns[nme] = set(eval(m.group(2), {}, {})); 
        except Exception as e: pass
closed = set().union(*ns.values()) if ns else set()
print('tables found:', {k: len(v) for k, v in ns.items()}, 'union', len(closed))
toks = []
for f in sorted(glob.glob('corpus/texts/*.txt')):
    t = open(f, encoding='utf-8', errors='ignore').read().lower()
    toks.append(re.findall(r"[a-z]+(?:'[a-z]+)?", t))
alltoks = [w for ts in toks for w in ts]
N = len(alltoks); cnt = collections.Counter(alltoks)
cl = sum(c for w, c in cnt.items() if w in closed)
print('tokens', N, 'types', len(cnt), 'closed-class table size', len(closed), 'closed share of tokens %.1f%%' % (100*cl/N), 'closed types present', sum(1 for w in cnt if w in closed))
# coverage
cum = 0
for k, (w, c) in enumerate(cnt.most_common(), 1):
    cum += c
    for t in (0.5, 0.8, 0.9, 0.95):
        pass
    if k in (10, 50, 100, 200, 500, 1000, 5000): print(' top %5d types cover %.1f%%' % (k, 100*cum/N))
# next-word distribution after 'in'
for head in ('in', 'of', 'the'):
    nxt = collections.Counter()
    for ts in toks:
        for a, b in zip(ts, ts[1:]):
            if a == head: nxt[b] += 1
    tot = sum(nxt.values()); H = -sum(c/tot*math.log2(c/tot) for c in nxt.values())
    top = nxt.most_common(10); cov10 = sum(c for _, c in top)/tot
    clshare = sum(c for w, c in nxt.items() if w in closed)/tot
    print("after %r: n=%d distinct=%d entropy=%.2f bits, top10 cover %.1f%%, next is closed-class %.1f%%; top: %s" % (head, tot, len(nxt), H, 100*cov10, 100*clshare, [w for w, _ in top]))
# bits per word, unigram vs bigram, held-out: last 10% of each work (add-k smoothing with unigram back-off)
train = [ts[:int(.9*len(ts))] for ts in toks]; test = [ts[int(.9*len(ts)):] for ts in toks]
uni = collections.Counter(w for ts in train for w in ts); V = len(uni) + 1; Ntr = sum(uni.values())
bi = collections.Counter(); ctx = collections.Counter()
for ts in train:
    for a, b in zip(ts, ts[1:]): bi[(a, b)] += 1; ctx[a] += 1
def pu(w): return (uni.get(w, 0) + 0.1) / (Ntr + 0.1*(V+1))
def pb(a, b, lam=0.7):
    c = ctx.get(a, 0)
    pbi = bi.get((a, b), 0)/c if c else 0.0
    return lam*pbi + (1-lam)*pu(b)
bu = bb = n = 0
bu_closed = bb_closed = nc = 0; bu_open = bb_open = no = 0
for ts in test:
    for a, b in zip(ts, ts[1:]):
        x = -math.log2(pu(b)); y = -math.log2(pb(a, b)); bu += x; bb += y; n += 1
        if b in closed: bu_closed += x; bb_closed += y; nc += 1
        else: bu_open += x; bb_open += y; no += 1
print('held-out %d words: unigram %.2f bits/word, bigram %.2f bits/word' % (n, bu/n, bb/n))
print('  closed-class targets (%d): unigram %.2f, bigram %.2f | open-class targets (%d): unigram %.2f, bigram %.2f' % (nc, bu_closed/nc, bb_closed/nc, no, bu_open/no, bb_open/no))
chars = sum(len(w)+1 for ts in test for w in ts[1:]); print('  = %.2f bits/char (bigram, incl. one space per word)' % (bb/chars))
