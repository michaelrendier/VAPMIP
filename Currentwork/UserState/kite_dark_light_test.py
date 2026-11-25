"""kite_dark_light_test.py -- does the box-kite sign structure fit the 7-NT x dark/light poles?  (2026-11-25)
Structure (ValaQuenta box_kite, all 7 kites identical): 6 vertices = 6 NTs in 3 antagonist pairs (the non-edges, never annihilate); each vertex has 2 diagonals (+/-) = dark/light poles;
each of the 12 edges annihilates exactly 2 of its 4 pole pairs (both same-sign or both opposite-sign); every one of the 8 faces has gauge-invariant Z2 holonomy -1 (frustrated).
Data: 3,655 corpus prompts, calibrated 14-pole dose. Raw: all 12 NT pairs have same-pole correlation > opposite-pole (one global dark/light factor): all 8 faces holonomy +1 (uniform; 1/64 of sign patterns).
After regressing out the dark-group and light-group means: 3 parallel / 9 crossed edges, face holonomies mixed [1,-1,1,1,1,-1,1,1]; bootstrap 0/300 all -1, 60/300 all +1, 240/300 mixed.
Reading: the kite structure is available (a Z2 gauge field on the edges) but the text meters show only the global valence factor, not a kite-specific flux.  Run with the VAPMIP .venv from this directory."""
import sys, os, json, itertools, random, numpy as np
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), '..', '..'))
from prompt_to_state import PromptToState, NT
P = PromptToState(); random.seed(11)
rows = [json.loads(l) for l in open('corpus.jsonl')]; txt = []
for src in sorted({r['source'] for r in rows}):
    t = [r['text'] for r in rows if r['source'] == src and len(r['text']) > 8]; random.shuffle(t); txt += t[:700]
D = np.array([P.dose1(t)[0] for t in txt]); print('prompts', len(txt), 'poles', D.shape)
C = np.corrcoef(D.T); idx = lambda a, s: 2 * NT.index(a) + (1 if s > 0 else 0)      # even = dark (-), odd = light (+)
axes = [('GLU', 'GABA'), ('DA', '5HT'), ('NE', 'OXT')]; verts = [v for ax in axes for v in ax]; ax_of = {v: i for i, ax in enumerate(axes) for v in ax}
edges = [(a, b) for a, b in itertools.combinations(verts, 2) if ax_of[a] != ax_of[b]]; assert len(edges) == 12
def etype(a, b): return 1 if (C[idx(a, -1), idx(b, -1)] + C[idx(a, 1), idx(b, 1)]) > (C[idx(a, -1), idx(b, 1)] + C[idx(a, 1), idx(b, -1)]) else -1
T = {frozenset(e): etype(*e) for e in edges}
faces = [(x, y, z) for x in axes[0] for y in axes[1] for z in axes[2]]
hol = {f: T[frozenset((f[0], f[1]))] * T[frozenset((f[1], f[2]))] * T[frozenset((f[0], f[2]))] for f in faces}
for f, h in hol.items(): print(f, h)
print('edge types (+1 same-pole pairs correlate more):', {tuple(sorted(k)): v for k, v in T.items()})
obs = len(set(hol.values())) == 1
# null: all 2^12 edge-sign assignments
cnt = 0; tot = 0
for bits in itertools.product((1, -1), repeat=12):
    t = {frozenset(e): b for e, b in zip(edges, bits)}; hs = {t[frozenset((f[0], f[1]))] * t[frozenset((f[1], f[2]))] * t[frozenset((f[0], f[2]))] for f in faces}; tot += 1; cnt += (len(hs) == 1)
print('all 8 faces same holonomy (observed):', obs, '| fraction of all 4096 sign patterns with that property:', cnt / tot)
# bootstrap stability of the observed edge types
rng = np.random.default_rng(1); agree = []
for _ in range(300):
    ii = rng.integers(0, len(D), len(D)); Cb = np.corrcoef(D[ii].T)
    tb = {frozenset(e): (1 if (Cb[idx(e[0], -1), idx(e[1], -1)] + Cb[idx(e[0], 1), idx(e[1], 1)]) > (Cb[idx(e[0], -1), idx(e[1], 1)] + Cb[idx(e[0], 1), idx(e[1], -1)]) else -1) for e in edges}
    hb = {tb[frozenset((f[0], f[1]))] * tb[frozenset((f[1], f[2]))] * tb[frozenset((f[0], f[2]))] for f in faces}; agree.append(len(hb) == 1)
print('bootstrap: share of resamples with all faces same holonomy:', np.mean(agree))
# magnitude of the cross-polarity effect per edge
for e in edges: print(e, 'same-pole', round(C[idx(e[0], -1), idx(e[1], -1)] + C[idx(e[0], 1), idx(e[1], 1)], 3), 'opp-pole', round(C[idx(e[0], -1), idx(e[1], 1)] + C[idx(e[0], 1), idx(e[1], -1)], 3))
# --- remove the global dark/light factor (net valence = mean light - mean dark) and the overall arousal (mean of all), then repeat
Z = (D - D.mean(0)) / (D.std(0) + 1e-9); dark = Z[:, 0::2].mean(1); light = Z[:, 1::2].mean(1)
R = Z.copy()
for g in (dark, light):
    for j in range(14): R[:, j] -= np.polyfit(g, R[:, j], 1)[0] * g          # regress out the group means
C2 = np.corrcoef(R.T)
def types(Cm): return {frozenset(e): (1 if (Cm[idx(e[0], -1), idx(e[1], -1)] + Cm[idx(e[0], 1), idx(e[1], 1)]) > (Cm[idx(e[0], -1), idx(e[1], 1)] + Cm[idx(e[0], 1), idx(e[1], -1)]) else -1) for e in edges}
T2 = types(C2); hol2 = [T2[frozenset((f[0], f[1]))] * T2[frozenset((f[1], f[2]))] * T2[frozenset((f[0], f[2]))] for f in faces]
print('AFTER removing the dark-group and light-group means: edge types', sum(v == 1 for v in T2.values()), 'parallel /', sum(v == -1 for v in T2.values()), 'crossed; face holonomies', hol2)
agree = {'-1': 0, '+1': 0, 'mixed': 0}
for _ in range(300):
    ii = rng.integers(0, len(R), len(R)); tb = types(np.corrcoef(R[ii].T)); hb = [tb[frozenset((f[0], f[1]))] * tb[frozenset((f[1], f[2]))] * tb[frozenset((f[0], f[2]))] for f in faces]
    agree['-1' if all(h == -1 for h in hb) else '+1' if all(h == 1 for h in hb) else 'mixed'] += 1
print('bootstrap of the residual (300): all faces -1 / all +1 / mixed:', agree)
