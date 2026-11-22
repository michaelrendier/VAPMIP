"""wordnet_basins.py (2026-11-21): gamma_radial over every WordNet 3.0 synset (NLTK, 117,659); exact neighbourhoods (identical 19-vectors) and density basins of gamma. Run from VAPMIP/ with .venv/bin/python."""
"""WordNet 3.0: gamma_radial over every synset; neighbourhoods (exact 19-vector classes) and density basins."""
import sys, math, json, collections
sys.path.insert(0, '.')
import wordnet_boxkite as W
from nltk.corpus import wordnet as wn
rows = []
for s in wn.all_synsets():
    v = tuple(W.context_vector(s)); g = W.gamma_radial(list(v))
    rows.append((s.name(), s.pos(), v, g, s.min_depth()))
N = len(rows); none = [r for r in rows if r[3] is None]
print('synsets', N, 'no relations (gamma undefined)', len(none))
by = collections.Counter(r[1] for r in rows); print('pos', dict(by))
# exact neighbourhoods: identical 19-vector
cls = collections.defaultdict(list)
for r in rows: cls[r[2]].append(r)
print('distinct 19-vectors', len(cls), 'largest class sizes', sorted((len(v) for v in cls.values()), reverse=True)[:10])
sizes = sorted((len(v) for v in cls.values()), reverse=True); cum = 0
for k in (1, 5, 10, 50, 100, 500, 1000):
    print(' top', k, 'classes hold %.1f%% of synsets' % (100*sum(sizes[:k])/N))
names = W.RELATION_METHODS
def desc(v): return ', '.join('%s=%d' % (names[i][:12], e) for i, e in enumerate(v) if e) or '(none)'
print('--- ten biggest exact neighbourhoods')
for v, members in sorted(cls.items(), key=lambda kv: -len(kv[1]))[:10]:
    g = W.gamma_radial(list(v))
    print(len(members), 'gamma=%s' % (None if g is None else round(g, 4)), desc(v), '| pos', dict(collections.Counter(m[1] for m in members)), '| e.g.', [m[0] for m in members[:3]])
# gamma density: histogram, smoothed, local maxima (basins) and minima (ridges)
gs = sorted(r[3] for r in rows if r[3] is not None)
B = 200; lo, hi = -1.0, 1.0; h = [0]*B
for g in gs: h[min(B-1, int((g-lo)/(hi-lo)*B))] += 1
sm = [sum(h[max(0,i-2):i+3])/len(h[max(0,i-2):i+3]) for i in range(B)]
peaks = [i for i in range(1, B-1) if sm[i] > sm[i-1] and sm[i] >= sm[i+1] and sm[i] > 0.01*max(sm)]
print('--- gamma range', round(gs[0], 4), round(gs[-1], 4), 'median', round(gs[len(gs)//2], 4))
mins = [i for i in range(1, B-1) if sm[i] < sm[i-1] and sm[i] <= sm[i+1]]
print('density peaks (bin centre gamma, smoothed count):', [(round(lo+(i+.5)*(hi-lo)/B, 3), round(sm[i])) for i in peaks])
print('density valleys:', [(round(lo+(i+.5)*(hi-lo)/B, 3), round(sm[i])) for i in mins if sm[i] < 0.5*max(sm)][:20])
# basin = between consecutive valleys; report population, pos mix, depth, examples
edges = [lo] + [lo+(i+.5)*(hi-lo)/B for i in mins if sm[i] < 0.6*max(sm)] + [hi]
print('--- basins (between valleys)')
for a, b in zip(edges, edges[1:]):
    mem = [r for r in rows if r[3] is not None and a <= r[3] < b]
    if not mem: continue
    c = collections.Counter(r[1] for r in mem); avgd = sum(r[4] for r in mem)/len(mem)
    topvec = collections.Counter(r[2] for r in mem).most_common(1)[0]
    print('[%.3f, %.3f) n=%d (%.1f%%) pos %s mean_depth %.1f | commonest vector: %s (x%d) | e.g. %s' % (a, b, len(mem), 100*len(mem)/N, dict(c), avgd, desc(topvec[0]), topvec[1], [m[0] for m in mem[:3]]))
pass
