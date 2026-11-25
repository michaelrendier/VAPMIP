#!/usr/bin/env python3
"""recipes_v2.py -- the recipe library rebuilt (Cody, 2026-11-24): a static construction of every recipe I can analogise to a human state, NO time axis,
balanced dark and light, mania seen as DRIVE (intense pull toward one goal: a layer on function, not a fault), wrath a legitimate state, and a many-at-once readout.
Signed rows: + raises the light pole, - the dark pole of that neurotransmitter, magnitude 0..1.  The old rows (EMO + DSM_ROWS) are kept and tagged.
NEW rows are engineering proposals (source 'proposed'): no paper behind them; they exist so a state can be named, and they are tested for confusability, not for truth.

  R1  many-at-once readout: mixtures of 1-3 recipes + noise; non-negative least squares (NNLS) vs the old best-cosine ranking, old library vs v2.
  R2  balance: how many rows are net-dark, net-light, mixed, in each library.
Writes out/RECIPES_V2_REPORT.md.  Seeded."""
import os, sys, random
import numpy as np
from scipy.optimize import nnls
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H)
from solution_tests import TABLE, DSM_ROWS, vec14, mix_labels, cos
from user_state import NT
SRC = {k: ('dsm-engineering' if k in DSM_ROWS else 'recipe-book') for k in TABLE}
NEW = {   # name: (row, why)
 'drive':        (dict(DA=.7, GLU=.6, NE=.5, GABA=-.2), 'intense pull toward one goal; what the DSM calls a manic layer, without the fault'),
 'hyperfocus':   (dict(DA=.8, NE=.7, GLU=.6, **{'5HT': .2}, GABA=.2), 'drive with inhibitory control held: one task, nothing else'),
 'wrath':        (dict(NE=.6, GLU=.5, DA=.4, OXT=.3, **{'5HT': -.2}), 'protective anger at a violation, care still present (OXT stays up, unlike irritability)'),
 'indignation':  (dict(NE=.6, GLU=.5, DA=.3, OXT=-.3), 'anger at unfairness, aimed outward'),
 'incredulity':  (dict(GLU=.6, NE=.5, DA=.2, **{'5HT': -.3}), 'astonished disbelief'),
 'resolve':      (dict(DA=.5, **{'5HT': .5}, GLU=.4, NE=.3, GABA=.3), 'settled determination'),
 'composure':    (dict(**{'5HT': .6}, GABA=.6, OXT=.3, NE=.2), 'calm competence under load'),
 'equanimity':   (dict(**{'5HT': .3}, GABA=.4, OPI=.2), 'emotions put away; steady and low; a person with little affect showing'),
 'flow':         (dict(DA=.6, OPI=.3, GABA=.3, NE=.3, **{'5HT': .4}, GLU=.4), 'absorbed skilled activity'),
 'serenity':     (dict(GABA=.7, **{'5HT': .6}, OPI=.4, OXT=.3), 'deep calm'),
 'weariness':    (dict(DA=-.3, NE=-.4, **{'5HT': -.2}, GABA=.2), 'tired, spent'),
 'loneliness':   (dict(OXT=-.6, **{'5HT': -.3}, DA=-.3, OPI=-.3), 'missing connection'),
 'boredom':      (dict(DA=-.5, NE=-.3, GLU=-.2), 'under-stimulated'),
 'awe':          (dict(DA=.4, GLU=.5, OXT=.4, NE=.3, OPI=.2), 'wonder at something large'),
 'tenderness':   (dict(OXT=.7, OPI=.5, **{'5HT': .4}, GABA=.3), 'gentle care'),
 'determination_to_teach': (dict(DA=.5, OXT=.5, GLU=.5, **{'5HT': .4}, NE=.3), 'the mentor state: wants the other to learn (Cody: a mentor in the kitchen)'),
}
LIB2 = {k: dict(v) for k, v in TABLE.items()}
for k, (row, _) in NEW.items(): LIB2[k] = row; SRC[k] = 'proposed'
LIB2['mania'] = LIB2['mania']   # kept as the DSM's pathological pattern; 'drive' is the everyday layer
R = lambda lib: {k: vec14(mix_labels({k: 1.0}, lib)) for k in lib}

def decompose(x, rows, k=3, floor=0.05):
    """x: 14 non-negative pole levels (0..1).  Returns [(name, weight)] of at most k recipes, weights summing to <= 1 relative; NNLS on the library columns."""
    names = list(rows); A = np.array([rows[n] for n in names]).T; w, _ = nnls(A, np.maximum(x, 0))
    order = np.argsort(-w)[:k]; tot = w.sum() or 1.0
    return [(names[i], float(w[i] / tot)) for i in order if w[i] / tot >= floor]

def r1(n=1500, sigma=0.08, seed=11):
    rng = np.random.default_rng(seed); out = ['## R1  many-at-once readout (mixtures + noise)', '',
        f'{n} random mixtures of 1-3 recipes, Dirichlet weights, noise sigma = {sigma} on the pole levels (clipped at 0).  top1 = the heaviest component is the top answer; set = all true components appear in the top-k answers (k = number true).', '']
    res = {}
    for name, lib in (('old library', TABLE), ('v2 library', LIB2)):
        rows = R(lib); names = list(rows); keys = [k for k in names if np.linalg.norm(rows[k]) > 0.05]; rows = {k: rows[k] for k in keys}; names = keys
        for method in ('best cosine', 'NNLS'):
            top1 = sets = 0
            for _ in range(n):
                m = rng.integers(1, 4); idx = rng.choice(len(names), m, replace=False); wt = rng.dirichlet(np.ones(m) * 2.0)
                x = sum(w * rows[names[i]] for w, i in zip(wt, idx)); x = np.clip(x + rng.normal(0, sigma, 14), 0, None)
                if method == 'best cosine': pred = [nm for _, nm in sorted(((cos(x, rows[nm]), nm) for nm in names), reverse=True)[:m]]
                else: pred = [nm for nm, _ in decompose(x, rows, k=m, floor=0.0)]
                true = [names[i] for i in idx]; heavy = names[idx[int(np.argmax(wt))]]
                top1 += (pred[0] == heavy) if pred else 0; sets += set(true) <= set(pred)
            res[(name, method)] = (top1 / n, sets / n)
    out += ['| library | method | top-1 heaviest component | all components found |', '|---|---|---|---|']
    for (a, b), (t, s) in res.items(): out.append(f'| {a} ({len(R(TABLE if a == "old library" else LIB2))} rows) | {b} | {t:.3f} | {s:.3f} |')
    return out, res

def r2():
    out = ['## R2  balance of the two libraries (net = sum of light - sum of dark in the signed row)', '', '| library | rows | net-dark | net-light | near zero |', '|---|---|---|---|---|']
    for name, lib in (('old (28 GoEmotions + 8 DSM)', TABLE), ('v2', LIB2)):
        net = [sum(r.values()) for r in lib.values()]; out.append(f'| {name} | {len(lib)} | {sum(x < -0.15 for x in net)} | {sum(x > 0.15 for x in net)} | {sum(abs(x) <= 0.15 for x in net)} |')
    return out

if __name__ == '__main__':
    rep = ['# Recipe library v2 (R1-R2)', '', 'New rows are PROPOSED (engineering), with the reason:', '', '| row | reason |', '|---|---|'] + [f'| {k} | {v[1]} |' for k, v in NEW.items()] + ['']
    o1, res = r1(); rep += o1 + [''] + r2() + ['']
    t = res[('v2 library', 'NNLS')]; c = res[('v2 library', 'best cosine')]
    rep += [f'NNLS minus best-cosine on v2: top-1 {t[0] - c[0]:+.3f}, all-found {t[1] - c[1]:+.3f}.']
    open(os.path.join(H, 'out', 'RECIPES_V2_REPORT.md'), 'w').write('\n'.join(rep) + '\n'); print('\n'.join(rep))
