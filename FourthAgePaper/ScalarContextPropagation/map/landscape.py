"""landscape.py (2026-11-21): the Scalar Boxkite context landscape, 2D and 3D, and the multi-location words.
Run from VAPMIP/ with .venv/bin/python FourthAgePaper/ScalarContextPropagation/map/landscape.py
Reads scalar_context_map.tsv.gz (scalar_context_map.py). Axes: Wernicke = 1 + gamma_radial (continuous), Broca = number of non-zero
relations among the 19 (discrete). The 3D view uses the spatial-simulation 3D overview function on the 19-D class vectors."""
import gzip, os, sys, collections, math, json
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser('~/.claude/skills/spatial-simulation/assets'))
import overview3d as O3
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
with gzip.open(os.path.join(HERE, 'scalar_context_map.tsv.gz'), 'rt', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        r = dict(zip(hdr, line.rstrip('\n').split('\t'))); rows.append(r)
cls = {}
for r in rows:
    c = int(r['class'])
    if c not in cls:
        v = [int(x) for x in r['vec19'].split(',')]
        cls[c] = {'vec': v, 'gamma': None if r['gamma_radial'] == '' else float(r['gamma_radial']), 'attr': int(r['attractor_basin']), 'n': 0}
syn_seen = set()
for r in rows:
    if r['synset'] not in syn_seen: syn_seen.add(r['synset']); cls[int(r['class'])]['n'] += 1
C = sorted(cls)
pal = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#bcbd22']
def col(a): return pal[a - 1] if a <= 8 else '#888888'
# ---- 2D
fig, ax = plt.subplots(figsize=(10, 7))
for c in C:
    d = cls[c]
    if d['gamma'] is None: continue
    ax.scatter(1 + d['gamma'], sum(1 for x in d['vec'] if x) + (np.random.RandomState(c).rand() - .5) * 0.5, s=8 + 28 * math.log10(1 + d['n']), c=col(d['attr']), alpha=.65, edgecolors='none')
ax.set_xlabel('Wernicke (continuous): 1 + gamma_radial'); ax.set_ylabel('Broca (discrete): number of non-zero relations (jittered)')
ax.set_title('Scalar Boxkite context landscape, WordNet 3.0: 1,276 classes (size = log synsets, colour = attractor basin)')
ax.annotate('largest class: hypernyms=1 (45,441 synsets)', (0.098, 1.0), xytext=(0.32, 0.55), arrowprops=dict(arrowstyle='->'), fontsize=9)
ax.text(0.62, 1.55, 'blue: attractor basin 1 (970 classes, 88% of synsets)\norange: basin 2 (adjective satellites)\ngrey: the small hub basins', fontsize=9, va='bottom')
ax.set_ylim(0.3, 7.5)
fig.savefig(os.path.join(HERE, 'landscape_2d.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
# ---- 3D via the overview function
X = np.array([cls[c]['vec'] for c in C], float)
ov = O3.overview(X, mode='static')
P = ov['P']
fig = plt.figure(figsize=(10, 8)); ax = fig.add_subplot(111, projection='3d')
sizes = [6 + 26 * math.log10(1 + cls[c]['n']) for c in C]
ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=sizes, c=[col(cls[c]['attr']) for c in C], alpha=.7, edgecolors='none')
ax.view_init(elev=ov['camera']['elevation_deg'], azim=ov['camera']['azimuth_deg'])
names = ['hyp', 'ihyp', 'hypo', 'ihypo', 'mholo', 'sholo', 'pholo', 'mmero', 'smero', 'pmero', 'attr', 'entail', 'cause', 'also', 'vgrp', 'sim', 'topic', 'region', 'usage']
def load(a): return ', '.join('%s %+.2f' % (names[i], a[i]) for i in np.argsort(-np.abs(a))[:3])
def short(a): return ' / '.join(names[i] for i in np.argsort(-np.abs(a))[:2])
ax.set_xlabel('1: ' + short(ov['axes'][:, 0]), labelpad=8); ax.set_ylabel('2: ' + short(ov['axes'][:, 1]), labelpad=8); ax.set_zlabel('3: ' + short(ov['axes'][:, 2]), labelpad=8)
fig.suptitle('Context landscape in 3D (overview function): %.0f%% of the variance of the 19 dims shown; clipped %d of %d classes\nloadings: ' % (100 * ov['explained_total'], int(ov['clipped'].sum()), len(C)) + ' | '.join(load(ov['axes'][:, i]) for i in range(3)), fontsize=9, y=0.98)
fig.savefig(os.path.join(HERE, 'landscape_3d.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
# ---- words with several contexts
bylem = collections.defaultdict(list)
for r in rows:
    g = None if r['gamma_radial'] == '' else float(r['gamma_radial'])
    bylem[r['lemma']].append((r['synset'], int(r['class']), g, int(r['attractor_basin']), sum(1 for x in r['vec19'].split(',') if x != '0')))
multi = {l: v for l, v in bylem.items() if len(v) >= 2}
ncls = collections.Counter(len({x[1] for x in v}) for v in multi.values())
nb = collections.Counter(len({x[3] for x in v}) for v in multi.values())
def gspread(v):
    gs = [x[2] for x in v if x[2] is not None]; return (max(gs) - min(gs)) if len(gs) > 1 else 0.0
spread = sorted(((gspread(v), l) for l, v in multi.items()), reverse=True)
stats = {'lemmas': len(bylem), 'lemmas_with_2plus_senses': len(multi), 'lemmas_in_2plus_classes': sum(c for k, c in ncls.items() if k >= 2),
         'lemmas_in_2plus_attractor_basins': sum(c for k, c in nb.items() if k >= 2), 'max_classes_one_lemma': max(ncls), 'widest_gamma_spread': spread[:12]}
json.dump(stats, open(os.path.join(HERE, 'polysemy.json'), 'w'), indent=1)
fig, ax = plt.subplots(figsize=(10, 6.5))
rs = np.random.RandomState(5)
for i, w in enumerate(['run', 'light', 'bank', 'head']):
    v = [x for x in bylem[w] if x[2] is not None]
    xs = [1 + x[2] + rs.randn() * 0.004 for x in v]; ys = [x[4] + rs.randn() * 0.05 for x in v]
    ax.scatter(xs, ys, c=pal[i], s=60, label='%s (%d senses)' % (w, len(bylem[w])), alpha=.7, edgecolors='k', linewidths=.3)
ax.set_xlabel('Wernicke: 1 + gamma_radial'); ax.set_ylabel('Broca: non-zero relations'); ax.legend(fontsize=10)
ax.set_title('One word, several contexts: the senses of four words occupy different places in the landscape')
fig.savefig(os.path.join(HERE, 'landscape_words.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
print(json.dumps({k: stats[k] for k in stats if k != 'widest_gamma_spread'}), '\nloadings:', [load(ov['axes'][:, i]) for i in range(3)], 'explained', [round(x, 3) for x in ov['explained']])
print('widest gamma spread:', [(w, round(s, 3)) for s, w in spread[:8]])
