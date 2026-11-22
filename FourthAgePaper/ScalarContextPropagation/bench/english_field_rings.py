"""english_field_rings.py (2026-11-22): candidate two-ring sets taken from the English field (monad3_c.bin) and tried in the Scale engine (ValaQuenta/modules/scale). Run from VAPMIP/ with ValaQuenta/.venv/bin/python; output: english_field_rings.txt."""
import sys, struct, numpy as np, math
sys.path.insert(0, '.'); sys.path.insert(0, '..')
import live_vocabulary as LV
from ValaQuenta.modules.scale import custom_ring_chart, two_ring_point, cross_ratio, mobius_fold, verify_cross_ratio_is_scale_blind
st = LV.read_c_store('PtolC/monad3_c.bin'); d = st['data']; o = st['offs']; n = st['n_eng']
beta = np.frombuffer(d, '<f8', n, o['beta']); E = np.frombuffer(d, '<f8', n, o['E'])
age = np.frombuffer(d, '<i4', n, o['age']); fire = np.frombuffer(d, '<i4', n, o['fire']); strat = np.frombuffer(d, '<i4', n, o['strat'])
rp = np.frombuffer(d, '<u4', n + 1, o['rowptr']); deg = np.diff(rp.astype(np.int64))
print('english words', n)
print('E   min %.5f max %.5f mean %.4f | beta min %.4g max %.4g mean %.4f | fire max %d | degree max %d median %d' % (E.min(), E.max(), E.mean(), beta.min(), beta.max(), beta.mean(), fire.max(), deg.max(), np.median(deg)))
print('share beta==0: %.3f  share beta at cap(7.552): %.3f' % ((beta == 0).mean(), (beta >= 7.55).mean()))
D_STAR, A_PI = 0.24600, 0.56714
seed = (E - D_STAR) / (A_PI - D_STAR); N = 25000
slot = np.floor(seed * N); frac = seed * N - slot
print('seed range %.4f..%.4f' % (seed.min(), seed.max()))
def study(name, r1, r2, mask=None):
    r1 = np.asarray(r1, float); r2 = np.asarray(r2, float)
    if mask is not None: r1, r2 = r1[mask], r2[mask]
    c = np.corrcoef(r1, r2)[0, 1] if r1.std() > 0 and r2.std() > 0 else float('nan')
    s = r1 + r2
    Z0 = complex(np.median(r1), np.median(r2)) if np.median(r1) > 0 else complex(1, 1)
    Z0 = complex(abs(Z0.real) or 1.0, abs(Z0.imag) or 1.0)
    pts = r1 + 1j * r2
    G = (pts - Z0) / (pts + Z0)
    sv = np.linalg.svd(np.stack([r1 - r1.mean(), r2 - r2.mean()], 1), compute_uv=False)
    print('%-44s corr %+.3f | sum range %.3g (std %.3g) | |Gamma| mean %.3f p5 %.3f p95 %.3f | sv ratio %.3f' % (name, c, np.ptp(s), s.std(), np.abs(G).mean(), np.percentile(np.abs(G), 5), np.percentile(np.abs(G), 95), sv[1] / sv[0]))
m = beta > 0
study('E (continuous address) vs beta (learned)', E, beta, m)
study('seed fraction in slot vs slot/N (one number split)', frac, slot / N)
study('beta vs A-degree', beta, deg, m)
study('E vs log2(1+fire)', E, np.log2(1 + fire), fire > 0)
study('beta vs E^2 (J = beta E^2 seed)', beta, E ** 2, m)
# the structural identity: J_pos*J_neg = e^-E ? (NoetherWiles NR4) as a test on the stored numbers: are beta*E^2 and e^-E related?
J = beta * E ** 2
print('J = beta*E^2: mean %.4f  max %.4f ; corr(J, exp(-E)) %.3f' % (J[m].mean(), J.max(), np.corrcoef(J[m], np.exp(-E[m]))[0, 1]))
print('cross-ratio is scale blind (Scale engine control):', verify_cross_ratio_is_scale_blind()['holds'])
print('--- usage rings (directed co-occurrence): production = out-degree, comprehension = in-degree ---')
col = np.frombuffer(d, '<u4', int(rp[-1]), o['col']); indeg = np.bincount(col, minlength=n)
ok = (deg > 0) & (indeg > 0)
lo, li = np.log(deg[ok]), np.log(indeg[ok])
print('words with both: %d of %d | corr(log out, log in) %.3f | std(log out - log in) %.3f | std(log out + log in) %.3f' % (ok.sum(), n, np.corrcoef(lo, li)[0, 1], (lo - li).std(), (lo + li).std()))
print('product out*in: median %.1f, IQR %.1f..%.1f (a Cassini product-constant would make this a spike)' % (np.median(deg[ok] * indeg[ok]), *np.percentile(deg[ok] * indeg[ok], [25, 75])))
study('log out-degree vs log in-degree (rescaled rings)', lo, li)
study('log beta vs log E (rescaled rings)', np.log(beta[m]), np.log(E[m]))
