"""dim19.py (2026-11-21): structure of the 19 relation dimensions: per-relation counts, reciprocity, lemma-level relations the 19 omit, effective dimension (SVD), trio collapses, F21 facts. Run from VAPMIP/ with .venv/bin/python."""
import sys, math, collections, itertools
sys.path.insert(0, '.')
import numpy as np, wordnet_boxkite as W
from nltk.corpus import wordnet as wn
names = W.RELATION_METHODS
raw = []; comp = []
for s in wn.all_synsets():
    raw.append([len(getattr(s, m)()) for m in names]); comp.append(W.context_vector(s))
R = np.array(raw, float); C = np.array(comp, float)
print('per relation: synsets with >=1 target, total edge endpoints')
for i, n in enumerate(names): print('  %-20s %6d %7d' % (n, int((R[:, i] > 0).sum()), int(R[:, i].sum())))
# reciprocity (edge endpoints should match between inverse pairs)
for a, b in [('hypernyms','hyponyms'),('instance_hypernyms','instance_hyponyms'),('member_holonyms','member_meronyms'),('substance_holonyms','substance_meronyms'),('part_holonyms','part_meronyms')]:
    print('reciprocal', a, int(R[:, names.index(a)].sum()), b, int(R[:, names.index(b)].sum()))
# lemma-level relations the 19 omit
lem = collections.Counter()
for s in wn.all_synsets():
    for l in s.lemmas():
        if l.antonyms(): lem['antonyms'] += 1
        if l.derivationally_related_forms(): lem['derivationally_related_forms'] += 1
        if l.pertainyms(): lem['pertainyms'] += 1
print('lemma-level relations not among the 19 (lemmas with >=1):', dict(lem))
# effective dimension
for label, M in (('raw counts', R), ('compressed (code vector)', C)):
    Xc = M - M.mean(0); sv = np.linalg.svd(Xc, compute_uv=False); ev = sv**2/ (sv**2).sum()
    cum = np.cumsum(ev)
    print(label, 'rank', int(np.linalg.matrix_rank(M)), 'comps for 90/99/99.9%%: %d %d %d' % tuple(int(np.searchsorted(cum, t))+1 for t in (.9, .99, .999)))
    print('   top variances', [round(float(x), 3) for x in ev[:8]])
# triple collapses on the compressed vectors (sum of the three kinds)
idx = lambda n: names.index(n)
def collapse(M, groups):
    cols = []; used = set()
    for g in groups:
        cols.append(sum(M[:, idx(n)] for n in g)); used |= set(g)
    rest = [M[:, idx(n)] for n in names if n not in used]
    return np.stack(cols + rest, 1)
distinct = lambda M: len({tuple(r) for r in M.astype(int)})
print('distinct vectors, 19 dims (compressed):', distinct(C))
G_h = ['member_holonyms','substance_holonyms','part_holonyms']; G_m = ['member_meronyms','substance_meronyms','part_meronyms']; G_d = ['topic_domains','region_domains','usage_domains']
for label, gs in (('holonym trio', [G_h]), ('meronym trio', [G_m]), ('domain trio', [G_d]), ('holonym+meronym trios (17 dims)->', [G_h, G_m]), ('all three trios', [G_h, G_m, G_d])):
    M = collapse(R, gs); print('collapse', label, '-> dims', M.shape[1], 'distinct raw-count vectors', distinct(M), 'distinct after log compress', distinct(np.round(np.log2(M+1))))
# F21 facts
F = {(a, b) for a in (1, 2, 4) for b in range(7)}
print('F21 size', len(F), 'scale part a in', sorted({a for a, _ in F}), 'quadratic residues mod 7', sorted({x*x % 7 for x in range(1, 7)}), '2^3 mod 7 =', pow(2, 3, 7))
# orbits of x->2x on Z7
print('orbits of x->2x on Z/7:', [sorted({(x*2**k) % 7 for k in range(3)}) for x in range(7)][:7])
