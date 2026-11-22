"""newton_stirling.py (2026-11-21): Newton basins of the degree-9 Stirling polynomial S10 (the UF om.ufm V=10 polynomial in
Currentwork/SemPriCon/orbweaver/LorenzStirling.py), as the wiki describes them (Newton's method; one basin per root), and the Scalar
Boxkite context points classified by them. The shipped LorenzStirling.py does NOT do this: it iterates z -> log|S10(1/z + p1)| and labels
the final |z| (int(|z|*7)%8+1); on its own default map every point is 'extinct' (bail 4.0) or one basin (bail >= 40).
Point of a word sense: Z = (1 + gamma_radial) + i * (non-zero relations): Wernicke real axis, Broca imaginary axis.
Run from VAPMIP/ with .venv/bin/python."""
import gzip, os, json, collections
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
coef = np.array([15, -45, -270, 182, 1687, 1395, -1576, -2684, -1008, 0]) / 7680.0       # z^9 ... z^0
roots_all = np.roots(coef)
roots = []
for r in sorted(roots_all, key=lambda r: (r.real, r.imag)):
    if not any(abs(r - q) < 1e-3 for q in roots): roots.append(r)       # S10 has a DOUBLE root at -1: 9 roots, 8 distinct basins
roots = np.array(roots)
dcoef = np.polyder(coef)
def newton(z, iters=80):
    z = np.asarray(z, complex)
    for _ in range(iters):
        d = np.polyval(dcoef, z)
        step = np.where(np.abs(d) > 1e-14, np.polyval(coef, z) / d, 0)
        z = z - step
    return z
def basin_of(z):
    zf = newton(z)
    dist = np.abs(zf[..., None] - roots)
    b = dist.argmin(-1) + 1
    ok = (dist.min(-1) < 1e-3)
    return np.where(ok, b, 0)
# Newton converges only linearly at the double root (-1), so the convergence test there is loose:

print('roots of S10:', [complex(round(r.real, 4), round(r.imag, 4)) for r in roots])
rows = []
with gzip.open(os.path.join(HERE, 'scalar_context_map.tsv.gz'), 'rt', encoding='utf-8') as f:
    h = f.readline().rstrip('\n').split('\t')
    for line in f: rows.append(dict(zip(h, line.rstrip('\n').split('\t'))))
pts = {}
for r in rows:
    if r['gamma_radial'] == '': continue
    pts[(r['gamma_radial'], r['vec19'])] = complex(1 + float(r['gamma_radial']), sum(1 for x in r['vec19'].split(',') if x != '0'))
keys = list(pts); zs = np.array([pts[k] for k in keys]); bs = basin_of(zs)
bymap = dict(zip(keys, bs))
cnt = collections.Counter(int(b) for b in bs)
print('classes classified:', len(keys), 'by Newton-Stirling basin (0 = did not converge):', dict(sorted(cnt.items())))
by_lemma = collections.defaultdict(set); lem_n = collections.Counter()
for r in rows:
    if r['gamma_radial'] == '': continue
    by_lemma[r['lemma']].add(int(bymap[(r['gamma_radial'], r['vec19'])]))
multi = {l: v for l, v in by_lemma.items() if len(v) >= 2}
print('lemmas', len(by_lemma), 'with senses in >=2 Newton-Stirling basins:', len(multi), ' max basins one lemma:', max(len(v) for v in by_lemma.values()))
print({w: sorted(by_lemma[w]) for w in ['bank', 'run', 'light', 'head', 'city', 'state', 'tree', 'set'] if w in by_lemma})
# basin map over the plane the points occupy, plus the roots
xs = np.linspace(0, 1.0, 300); ys = np.linspace(0, 8.0, 360)
G = basin_of(xs[None, :] + 1j * ys[:, None])
print('plane share by basin:', {int(k): round(float((G == k).mean()), 3) for k in np.unique(G)})
fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(G, origin='lower', extent=(0, 1, 0, 8), aspect='auto', cmap='tab10', interpolation='nearest', alpha=.6)
P = np.array([[z.real, z.imag] for z in zs]); ax.scatter(P[:, 0], P[:, 1], s=5, c='k', alpha=.5)
ax.set_xlabel('Wernicke: 1 + gamma_radial'); ax.set_ylabel('Broca: non-zero relations')
ax.set_title('Newton basins of the degree-9 Stirling polynomial over the context plane (1,276 classes)'); fig.colorbar(im, ax=ax, label='root basin (0 = no convergence)')
fig.savefig(os.path.join(HERE, 'newton_stirling_basins.png'), dpi=130, bbox_inches='tight'); plt.close(fig)
# whole plane picture of the polynomial's basins, for reference
xs2 = np.linspace(-4, 4, 500); G2 = basin_of(xs2[None, :] + 1j * xs2[:, None])
fig, ax = plt.subplots(figsize=(7, 7)); ax.imshow(G2, origin='lower', extent=(-4, 4, -4, 4), cmap='tab10', interpolation='nearest')
ax.scatter(roots.real, roots.imag, c='k', s=25); ax.set_title('Newton basins of S10 (degree 9), roots marked'); fig.savefig(os.path.join(HERE, 'newton_stirling_plane.png'), dpi=110, bbox_inches='tight')
json.dump({'roots': [[float(r.real), float(r.imag)] for r in roots], 'class_counts': {str(k): v for k, v in sorted(cnt.items())}, 'lemmas': len(by_lemma),
           'lemmas_multi_basin': len(multi), 'plane_share': {str(int(k)): float((G == k).mean()) for k in np.unique(G)}}, open(os.path.join(HERE, 'newton_stirling.json'), 'w'), indent=1)
