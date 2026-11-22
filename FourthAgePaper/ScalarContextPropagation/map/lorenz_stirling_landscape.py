"""lorenz_stirling_landscape.py (2026-11-21): the Scalar Boxkite context points classified by the author's Lorenz-Stirling basin code.
Code: Currentwork/SemPriCon/orbweaver/LorenzStirling.py (identical to PtolemyDesktop/Archimedes/Maths/LorenzStirling.py): Newton-style
Stirling V=10 iteration (basin boundaries, 8 basins, extinction on escape) + Lorenz trajectory seeded from the capture point.
Point of a word sense: Z = (1 + gamma_radial) + i * (number of non-zero relations): Wernicke on the real axis, Broca on the imaginary axis
(the Scale engine's Broca-Wernicke Rings convention). Run from VAPMIP/ with .venv/bin/python."""
import gzip, os, sys, collections, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'Currentwork', 'SemPriCon', 'orbweaver'))
from LorenzStirling import LorenzStirling
ls = LorenzStirling()
rows = []
with gzip.open(os.path.join(HERE, 'scalar_context_map.tsv.gz'), 'rt', encoding='utf-8') as f:
    h = f.readline().rstrip('\n').split('\t')
    for line in f: rows.append(dict(zip(h, line.rstrip('\n').split('\t'))))
cache = {}
def classify(gamma, broca):
    k = (round(gamma, 6), broca)
    if k not in cache:
        r = ls.stirling.iterate(complex(1 + gamma, broca))
        cache[k] = (0 if r.extinct else r.basin_id, r.iterations, abs(r.z_final))
    return cache[k]
cls = {}
for r in rows:
    if r['gamma_radial'] == '': continue
    c = int(r['class'])
    if c in cls: continue
    broca = sum(1 for x in r['vec19'].split(',') if x != '0')
    cls[c] = (float(r['gamma_radial']), broca)
tally = collections.Counter(); syn = collections.Counter()
popu = collections.Counter(int(r['class']) for r in rows if r['gamma_radial'] != '')
for c, (g, b) in cls.items():
    bid = classify(g, b)[0]; tally[bid] += 1
print('distinct (gamma, broca) points classified:', len(cache))
print('classes by Lorenz-Stirling basin (0 = extinct):', dict(sorted(tally.items())))
by_lemma = collections.defaultdict(set)
for r in rows:
    if r['gamma_radial'] == '': continue
    g = float(r['gamma_radial']); b = sum(1 for x in r['vec19'].split(',') if x != '0')
    by_lemma[r['lemma']].add(classify(g, b)[0])
multi_rows = {l: v for l, v in by_lemma.items() if len(v) >= 2}
print('lemmas with senses in >= 2 Lorenz-Stirling basins:', len(multi_rows), 'of', len(by_lemma))
# basin map over the region the points occupy
xs = np.linspace(0.0, 1.0, 200); ys = np.linspace(0.0, 8.0, 240)
grid = np.zeros((len(ys), len(xs)), int)
for i, y in enumerate(ys):
    for j, x in enumerate(xs):
        r = ls.stirling.iterate(complex(x, y)); grid[i, j] = 0 if r.extinct else r.basin_id
print('basin map over [0,1]x[0,8]: share of grid by basin', {int(k): round(float((grid == k).mean()), 3) for k in np.unique(grid)})
fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(grid, origin='lower', extent=(0, 1, 0, 8), aspect='auto', cmap='tab10', interpolation='nearest', alpha=.55)
pts = np.array([(1 + g, b) for g, b in cls.values()])
ax.scatter(pts[:, 0], pts[:, 1], s=5, c='k', alpha=.5)
ax.set_xlabel('Wernicke: 1 + gamma_radial'); ax.set_ylabel('Broca: non-zero relations')
ax.set_title('Lorenz-Stirling basins (Stirling V=10) over the context plane, with the 1,276 classes')
fig.colorbar(im, ax=ax, label='basin id (0 = extinction)'); fig.savefig(os.path.join(HERE, 'lorenz_stirling_basins.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
json.dump({'points': len(cache), 'class_tally': {str(k): v for k, v in sorted(tally.items())}, 'lemmas_multi_basin': len(multi_rows), 'lemmas': len(by_lemma),
           'grid_share': {str(int(k)): float((grid == k).mean()) for k in np.unique(grid)}, 'examples': {w: sorted(multi_rows[w]) for w in ['bank', 'run', 'light', 'head', 'city', 'state'] if w in multi_rows}},
          open(os.path.join(HERE, 'lorenz_stirling.json'), 'w'), indent=1)
print({w: sorted(by_lemma[w]) for w in ['bank', 'run', 'light', 'head', 'city', 'state', 'tree'] if w in by_lemma})
