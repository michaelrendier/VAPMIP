#!/usr/bin/env python3
"""solution_tests.py -- four tests of the "user state as a solution" design (Python first; nothing here is wired into the engine).

  T1  dilution mixing (C1V1 + C2V2 = C3V3) against the engine's running mean (UserEmotionalState): same maths in the special case, and what volume adds.
  T2  the emotion table as 14 non-negative poles: noisy round trip, mixed feelings, and the DSM-5 criteria text through the cheap usage pathway.
  T3  the dispenser as three legal moves (dilute / add / neutralise) against the v2 conjugate law and no action, on scripted users.
      THE PLANT (how a user responds to a dose) IS MY MODEL. T3 tests controller behaviour (feasibility, speed, overshoot, chatter), not real users.
  T4  distilling the transformer teachers into one sparse linear map, trained on several registers, scored against human labels and held-out Kafka.

Writes out/SOLUTION_TESTS_REPORT.md.  Seeded."""
import collections, csv, json, math, os, random, re, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..'))
csv.field_size_limit(10 ** 9)
from user_state import (BC, NT, EMO, Reading, mix_labels, score, scalar, net, DEFAULT_USE, UserEmotionalState)
POLES = [(a, s) for a in NT for s in (0, 1)]          # index 2*i + side; side 0 = dark, 1 = light
vec14 = lambda r: np.array([r[a][s] for a, s in POLES], float)
def reading_of(v):
    r = Reading.zero()
    for (a, s), x in zip(POLES, v): r[a][s] = float(min(1.0, max(0.0, x)))
    return r
REP = []
def say(*a):
    s = '\n'.join(str(x) for x in a); print(s, flush=True); REP.append(s)

# ───────────────────────────── T1 dilution ─────────────────────────────
class Solution:
    """c = concentration per pole, V = volume.  add(d, v): C1V1 + C2V2 = C3(V1+V2).  The cold prompt assigns.  Vmax caps memory (outflow)."""
    def __init__(self, vmax=None): self.c = None; self.V = 0.0; self.vmax = vmax
    def add(self, d, v=1.0):
        d = np.asarray(d, float)
        if self.c is None: self.c, self.V = d.copy(), v
        else: self.c = (self.V * self.c + v * d) / (self.V + v); self.V += v
        if self.vmax: self.V = min(self.V, self.vmax)
        return self.c

def t1():
    say('## T1 — dilution mixing against the engine\'s running mean', '')
    R = random.Random(11); rows = []
    for floor in (0.0, 0.1, 0.25, 0.3):
        vmax = None if floor == 0 else 1.0 / floor - 1.0
        worst = 0.0
        for _ in range(500):
            st = UserEmotionalState(floor=floor); sol = Solution(vmax)
            for _ in range(R.randint(2, 40)):
                d = np.array([R.random() for _ in range(14)]); st.add(reading_of(d)); sol.add(d, 1.0)
                worst = max(worst, float(np.max(np.abs(vec14(st.state) - sol.c))))
        rows.append((floor, vmax, worst))
    say('| engine floor f | solution Vmax = 1/f − 1 | max abs difference over 500 random conversations |', '|---|---|---|')
    for f, vm, w in rows: say(f'| {f} | {"∞" if vm is None else f"{vm:.2f}"} | {w:.2e} |')
    # what volume adds: a long outburst vs a short one, then calm turns
    def washout(v_out, calm_v, calm_turns=6, vmax=None):
        s = Solution(vmax); s.add([0.0] * 14, 1.0)
        d = np.zeros(14); d[2 * 5] = 1.0            # NE dark = 1.0
        s.add(d, v_out); out = [s.c[10]]
        for _ in range(calm_turns): s.add(np.zeros(14), calm_v); out.append(s.c[10])
        return out
    say('', 'Washout of one NE-dark outburst (concentration after the outburst, then after each calm prompt of volume v):', '',
        '| outburst volume | calm prompt volume | after outburst | +1 | +2 | +3 | +4 | +5 | +6 |', '|---|---|---|---|---|---|---|---|---|')
    for vo, vc in ((1, 1), (1, 3), (4, 1), (4, 3)):
        w = washout(vo, vc); say(f'| {vo} | {vc} | ' + ' | '.join(f'{x:.2f}' for x in w) + ' |')
    ok = all(w < 1e-9 for _, _, w in rows)
    say('', f'Result: the dilution recursion reproduces the running mean to {max(w for _,_,w in rows):.1e} for every floor, '
        f'so the old rule is the special case v = 1; unequal volumes add the weighting the old rule lacks (a long calm prompt washes out an outburst faster, a long outburst resists). **{"PASS" if ok else "FAIL"}**', '')
    return ok

# ───────────────────────────── T2 table as 14 poles ─────────────────────────────
DSM_ROWS = {   # signed: + light pole, − dark pole.  My engineering rows from the DSM-5 criteria (panic, mania, stimulant/paranoia, ...).
 'panic': dict(NE=-.9, GABA=-.7, GLU=-.6, **{'5HT': -.4}, OXT=-.2), 'mania': dict(DA=.9, NE=.7, **{'5HT': .6}, GLU=.7, GABA=-.5),
 'paranoia': dict(NE=-.8, **{'5HT': -.6}, OXT=-.7, GABA=-.6, DA=.3), 'apathy': dict(DA=-.8, OPI=-.5, NE=-.3),
 'sedation': dict(GABA=.9, GLU=-.6, NE=-.5, OPI=.4), 'irritability': dict(GABA=-.5, **{'5HT': -.5}, NE=-.5),
 'petulance': dict(**{'5HT': -.6}, GABA=-.6, OXT=-.4, NE=-.5), 'opioid_high': dict(OPI=.9, GABA=.4, DA=.3)}
TABLE = {k: v for k, v in EMO.items() if k != 'neutral'}; TABLE.update(DSM_ROWS)
def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0
def row14(lab): return vec14(mix_labels({lab: 1.0}, TABLE))
def row7(lab): return np.array([TABLE[lab].get(a, 0.0) for a in NT])

def t2():
    say('## T2 — the table as 14 non-negative poles', '')
    names = list(TABLE); R = np.random.default_rng(5)
    R14 = {n: row14(n) for n in names}; R7 = {n: row7(n) for n in names}
    # (a) noisy round trip: noise sigma on each pole, readout = nearest row by cosine
    say('### (a) Noisy round trip (each emotion + Gaussian noise on every pole, read out by nearest recipe by cosine; 400 draws per emotion)', '',
        '| noise σ (of 1.0 full scale) | 7 signed axes top-1 | 14 poles top-1 |', '|---|---|---|')
    conf = collections.Counter()
    for sig in (0.05, 0.10, 0.20):
        ok7 = ok14 = tot = 0
        for n in names:
            for _ in range(400):
                v7 = R7[n] + R.normal(0, sig, 7); v14 = np.clip(R14[n] + R.normal(0, sig, 14), 0, None)
                b7 = max(names, key=lambda m: cos(v7, R7[m])); b14 = max(names, key=lambda m: cos(v14, R14[m]))
                ok7 += b7 == n; ok14 += b14 == n; tot += 1
                if sig == 0.10 and b14 != n: conf[(n, b14)] += 1
        say(f'| {sig} | {ok7 / tot:.3f} | {ok14 / tot:.3f} |')
    say('', 'Most frequent confusions at σ = 0.10 (14 poles): ' + ', '.join(f'{a}→{b} ({c})' for (a, b), c in conf.most_common(8)), '')
    # (b) mixed feelings: 50/50 mixtures of every pair; signed averaging (my cosine check) against the engine's pole-wise mix
    both = {'signed7': 0, 'poles14': 0}; top1 = {'signed7': 0, 'poles14': 0}; npair = 0; lost = []
    for a, b in __import__('itertools').combinations(names, 2):
        npair += 1
        v7 = 0.5 * R7[a] + 0.5 * R7[b]; v14 = vec14(mix_labels({a: .5, b: .5}, TABLE))
        for key, v, RR in (('signed7', v7, R7), ('poles14', v14, R14)):
            rk = sorted(names, key=lambda m: -cos(v, RR[m]))[:2]
            both[key] += set(rk) == {a, b}; top1[key] += rk[0] in (a, b)
        if a in ('joy', 'love') and b in ('fear', 'grief', 'anger', 'panic'):
            lost.append((a, b, float(np.linalg.norm(v7)), float(np.linalg.norm(v14))))
    say(f'### (b) Mixed feelings: {npair} pairs, 50/50, noiseless', '', '| method | both emotions are the top-2 | top-1 is one of the pair |', '|---|---|---|')
    for k in ('signed7', 'poles14'): say(f'| {k} | {both[k] / npair:.3f} | {top1[k] / npair:.3f} |')
    say('', 'Vector length of opposite-feeling mixtures (7 signed axes → 14 poles): ' + '; '.join(f'{a}+{b} {x:.2f} → {y:.2f}' for a, b, x, y in lost[:6]), '',
        'Note: the engine\'s `mix_labels` already mixes pole by pole, so the cancelling problem I described earlier belonged to my signed-average check, not to the engine.', '')
    # (c) DSM-5 criteria text through the cheap usage pathway (GoEmotions-trained model) -> nearest recipe.  Accept sets written BEFORE running.
    import joblib
    vec, mdl = joblib.load(os.path.join(H, 'usage_model.joblib'))
    DSM_TXT = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/DSM5/dsm5.txt'); L = open(DSM_TXT, encoding='utf-8', errors='ignore').read().split('\n')
    BLOCKS = {'panic attack criteria': ((11946, 11983), {'panic', 'fear', 'nervousness'}),
              'manic episode criteria': ((7499, 7516), {'mania', 'excitement'}),
              'stimulant intoxication': ((28920, 28934), {'paranoia', 'nervousness', 'irritability', 'mania', 'anger'}),
              'caffeine intoxication': ((25812, 25826), {'nervousness', 'mania', 'excitement'}),
              'opioid intoxication': ((27912, 27924), {'apathy', 'sedation', 'opioid_high', 'sadness'}),
              'sedative intoxication': ((28382, 28395), {'sedation', 'apathy', 'irritability'})}
    from nltk.tokenize import sent_tokenize
    say('### (c) DSM-5 criteria text through the usage pathway (clinical register; accept sets fixed before the run)', '', '| block | sentences | pole length | nearest recipe | in accept set |', '|---|---|---|---|---|')
    hit = 0
    for k, ((a, b), acc) in BLOCKS.items():
        txt = ' '.join(' '.join(x.split()) for x in L[a:b] if x.strip()); ss = [s for s in sent_tokenize(txt) if len(s) > 8]
        P = np.clip(mdl.predict(vec.transform(ss)), 0, None).mean(0)
        best = sorted(names, key=lambda m: -cos(P, R14[m]))[:3]; ok = best[0] in acc; hit += ok
        say(f'| {k} | {len(ss)} | {np.linalg.norm(P):.2f} | {", ".join(best)} | {"yes" if ok else "no"} |')
    say('', f'{hit}/{len(BLOCKS)} blocks land in their accept set. The usage model was trained on Reddit, so the clinical register is a domain shift (same finding as Kafka).', '')

# ───────────────────────────── T3 dispenser ─────────────────────────────
B = np.zeros(14)                                     # baseline (white), 0..9 units; light poles
for a, lv in zip(NT, (2, 3, 2, 3, 4, 1, 3)): B[2 * NT.index(a) + 1] = lv
LIGHT_OF = {2 * i: 2 * i + 1 for i in range(7)}      # dark index -> light index of the same neurotransmitter
IDX = lambda a, s: 2 * NT.index(a) + s
SCEN = {   # (t0, shock vector spec, repeats)  shock added to the TRUE state at turn t0
 'panic':      ({('NE', 0): 7, ('GABA', 0): 6, ('GLU', 0): 5, ('5HT', 0): 3, ('OXT', 0): 1}, 'abrupt'),
 'fear (gradual)': ({('NE', 0): 7, ('GABA', 0): 6, ('GLU', 0): 5, ('5HT', 0): 3, ('OXT', 0): 1}, 'ramp'),
 'mania':      ({('DA', 1): 5, ('GLU', 1): 4, ('NE', 1): 5, ('5HT', 1): 3, ('GABA', 0): 3}, 'abrupt'),
 'apathy':     ({('DA', 1): -3, ('OPI', 1): -2, ('NE', 0): 2}, 'abrupt'),
 'petulance':  ({('5HT', 0): 4, ('GABA', 0): 4, ('OXT', 0): 3, ('NE', 0): 3}, 'repeat'),
 'grief':      ({('OPI', 0): 7, ('DA', 1): -3, ('5HT', 1): -4, ('5HT', 0): 6, ('OXT', 0): 4}, 'abrupt'),
 'calm (no event)': ({}, 'none')}
def shock_vec(spec, jitter):
    s = np.zeros(14)
    for (a, side), x in spec.items(): s[IDX(a, side)] = x * jitter
    return s
def schedule(kind, s, T):
    out = [np.zeros(14) for _ in range(T)]
    if kind == 'abrupt': out[3] = s
    elif kind == 'ramp':
        for k in range(8): out[3 + k] = s / 8
    elif kind == 'repeat':
        for t in (3, 6, 9): out[t] = s * 0.7
    return out
THR_ON, THR_OFF, BAND = 2.5, 1.2, 1.5
def ctl_three(c, st):
    e = c - B; mx = np.max(np.abs(e))
    st['on'] = (mx > THR_ON) or (st['on'] and mx > THR_OFF)
    a = np.zeros(14); dil = 0.0; moves = set()
    if not st['on']: return a, dil, moves
    elev = e > BAND; depl = (e < -BAND)
    if elev.any():
        dil = min(0.4, 0.08 * float(e[elev].max())); moves.add('calm')
        for p in np.where(elev)[0]:
            if p % 2 == 0:                       # an elevated dark pole: neutralise with the light pole of the same neurotransmitter
                a[LIGHT_OF[p]] += 0.6 * e[p]; moves.add('neutralise')
    for p in np.where(depl)[0]:
        if p % 2 == 1:
            a[p] += min(-e[p], 3.0); moves.add('persuade' if NT[p // 2] in ('DA', 'GLU') else 'reassure')
    return np.minimum(a, 4.0), dil, moves
def ctl_v2(c, st, deadband):
    ls, ds = c[1::2], c[0::2]; s = ls - ds; bs = B[1::2]
    T = bs - 0.6 * (s - bs); act = np.abs(s - bs) > deadband
    t14 = np.zeros(14)
    for i in range(7):
        t14[2 * i + 1] = max(T[i], 0.0); t14[2 * i] = max(-T[i], 0.0)
    return t14, act
def plant(u, action, kind, kap, nu, kapT):
    if kind == 'three':
        a, dil, _ = action
        u = (1 - dil) * u + dil * B
        add = kap * a; u = u + add
        for d_i, l_i in LIGHT_OF.items():
            m = nu * min(u[d_i], add[l_i]); u[d_i] -= m
    elif kind == 'v2':
        t14, act = action
        for i in range(7):
            if act[i]:
                for p in (2 * i, 2 * i + 1): u[p] += kapT * (t14[p] - u[p])
    return np.clip(u, 0, 9)
def run_one(scen, ctl, seed, kap, nu, kapT, T=40, dead_v2=0.5, relax=0.08):
    R = np.random.default_rng(seed); spec, kind = SCEN[scen]; jit = R.uniform(0.8, 1.2); S = schedule(kind, shock_vec(spec, jit), T)
    u = B.copy(); sol = Solution(vmax=8); st = {'on': False}; pending = None
    ent = None; inband = 0; first = None; under = 0.0; disp = 0; dose = 0.0; infeas = 0; emit = 0; moves = collections.Counter(); panic_flag = 0
    sh_sign = np.sign(S[3] if kind != 'repeat' else S[3]) if kind != 'none' else np.zeros(14)
    prev_ne = None
    for t in range(T):
        u = u + relax * (B - u) + S[t]
        if pending is not None: u = plant(u, pending, ctl, kap, nu, kapT)
        u = np.clip(u, 0, 9)
        d = np.clip(u + R.normal(0, 1.2, 14), 0, 9); cprev = None if sol.c is None else sol.c.copy(); c = sol.add(d, 1.0)
        # abrupt-rise flag: the INCOMING dose (not the smoothed solution) jumps NE-dark by >= 4 levels over the current concentration and is >= 5
        if cprev is not None and d[IDX('NE', 0)] - cprev[IDX('NE', 0)] >= 4.0 and d[IDX('NE', 0)] >= 5: panic_flag += 1
        if ctl == 'three':
            a, dil, mv = ctl_three(c, st); pending = (a, dil, mv)
            if a.any() or dil > 0: disp += 1; dose += float(a.sum()); moves.update(mv)
        elif ctl == 'v2':
            t14, act = ctl_v2(c, st, dead_v2); pending = (t14, act)
            if act.any():
                disp += 1; emit += 1; dose += float(np.abs(t14 - c)[np.repeat(act, 2)].sum())
                if np.max((c - t14)[np.repeat(act, 2)]) > BAND: infeas += 1      # asks the solution to lose a pole: impossible with solutes
        else: pending = None
        e = np.max(np.abs(u - B))
        if t >= 3 and kind != 'none':
            inband = inband + 1 if e < 2.0 else 0
            if inband >= 3 and first is None: first = t
            if kind != 'repeat': under = max(under, float(np.max(-sh_sign * (u - B))))
    tt = (first - 3) if first is not None else T
    return dict(tt=tt, over=max(under, 0.0), disp=disp, dose=dose, infeas=infeas / emit if emit else float('nan'), moves=moves, panic=panic_flag > 0)
def t3():
    say('## T3 — the dispenser as three legal moves, on scripted users', '',
        'The plant (how the true state responds to a dose) is my model: relaxation 0.08 per turn to baseline; each dose moves the state by κ; "neutralise" annihilates dark against light of the same neurotransmitter with efficiency ν. '
        'Observation = true state + Gaussian noise σ = 1.2 per pole, mixed by the dilution solution (Vmax = 8). 40 turns, 200 seeds per cell, shock at turn 3. '
        'Controllers: **three-move** (dilute / add / neutralise, hysteresis 2.5 on, 1.2 off), **v2** (signed conjugate T = B − 0.6·(s − B), dead-band 0.5 level; v2 coarse = dead-band 4.5 levels), **none**. Time = turns until the TRUE state is within 2 levels of baseline for 3 turns (40 = never).', '')
    variants = [(0.5, 0.5, 0.3), (0.5, 0.0, 0.3), (0.25, 0.5, 0.15), (0.25, 0.0, 0.15)]
    N = 200; summary = {}
    for (kap, nu, kapT) in variants:
        say(f'### Plant κ = {kap}, ν = {nu}, v2 pull = {kapT}', '', '| scenario | controller | time to band | overshoot (levels) | dispenses | solute dosed | infeasible emissions |', '|---|---|---|---|---|---|---|')
        for scen in SCEN:
            res = {}
            for name, ctl, dv in (('none', 'none', 0), ('v2', 'v2', 0.5), ('v2 coarse', 'v2', 4.5), ('three-move', 'three', 0)):
                res[name] = [run_one(scen, ctl, 1000 + k, kap, nu, kapT, dead_v2=dv) for k in range(N)]
                r = res[name]
                inf = np.nanmean([x['infeas'] for x in r]) if ctl == 'v2' else float('nan')
                say(f'| {scen} | {name} | {np.mean([x["tt"] for x in r]):.1f} | {np.mean([x["over"] for x in r]):.2f} | {np.mean([x["disp"] for x in r]):.1f} | {np.mean([x["dose"] for x in r]):.1f} | '
                    f'{"—" if math.isnan(inf) else f"{inf:.2f}"} |')
            summary[(kap, nu, scen)] = res
        say('')
    # paired comparison, three-move minus v2 and minus none, over all variants (per seed)
    say('### Paired comparison over all four plants and the six event scenarios (three-move minus comparator, per seed)', '', '| metric | comparator | mean difference | 95% bootstrap CI | paired t | p |', '|---|---|---|---|---|---|')
    for metric in ('tt', 'over'):
        for comp in ('none', 'v2', 'v2 coarse'):
            a, b = [], []
            for (kap, nu, scen), res in summary.items():
                if scen.startswith('calm'): continue
                a += [x[metric] for x in res['three-move']]; b += [x[metric] for x in res[comp]]
            d = [x - y for x, y in zip(a, b)]; bt = BC.bootstrap_ci(d, n_boot=1000); tt = BC.t_test_paired(a, b)
            say(f'| {"time to band" if metric == "tt" else "overshoot"} | {comp} | {BC.mean(d):+.2f} | [{bt["ci"][0]:+.2f}, {bt["ci"][1]:+.2f}] | {tt["t"]:.1f} | {tt["p"]:.1e} |')
    say('', '### Which moves the three-move controller chose, per scenario (share of seeds using the move at least once; plant κ 0.5, ν 0.5)', '', '| scenario | calm | neutralise | reassure | persuade |', '|---|---|---|---|---|')
    for scen in SCEN:
        r = summary[(0.5, 0.5, scen)]['three-move']
        say(f'| {scen} | ' + ' | '.join(f'{np.mean([m in x["moves"] for x in r]):.2f}' for m in ('calm', 'neutralise', 'reassure', 'persuade')) + ' |')
    pa = np.mean([x['panic'] for x in summary[(0.5, 0.5, 'panic')]['none']]); fe = np.mean([x['panic'] for x in summary[(0.5, 0.5, 'fear (gradual)')]['none']])
    ca = np.mean([x['panic'] for x in summary[(0.5, 0.5, 'calm (no event)')]['none']])
    say('', f'Abrupt-rise flag (incoming NE-dark dose ≥ 4 levels above the current concentration and ≥ 5): fires in {pa:.2f} of panic runs, {fe:.2f} of gradual-fear runs, {ca:.2f} of calm runs. The two have the same end state; only the rate tells them apart.', '')

# ───────────────────────────── T4 distillation ─────────────────────────────
def t4():
    say('## T4 — distilling the teachers into one sparse linear map, trained on several registers', '')
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import Ridge
    import joblib
    RAWD = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/UserStateCorpora')
    corp = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'corpus.jsonl')))}
    rc = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'raw_cache.jsonl')))}
    teach = lambda raw: vec14(score(raw, use=DEFAULT_USE, irony=True))
    gtest = [i for i in corp if corp[i]['source'] == 'goemotions']; gtexts = {corp[i]['text'] for i in gtest}
    reg = {}                                                             # register -> list of (text, teacher vector)
    for i, c in corp.items():
        if c['source'] != 'goemotions' and i in rc: reg.setdefault('corpus:' + c['source'], []).append((c['text'], teach(rc[i])))
    kp = [json.loads(l) for l in open(os.path.join(H, 'kafka_paras.jsonl'))]; kr = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'kafka_raw.jsonl')))}
    for p in kp:
        for i, s in enumerate(p['sentences']):
            j = kr.get(f"{p['id']}-s{i:03d}")
            if j: reg.setdefault('wyllie:' + p['work'], []).append((s, teach(j)))
    sp = [json.loads(l) for l in open(os.path.join(H, 'schocken_paras_v0.jsonl'))]; sr = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'schocken_raw.jsonl')))}
    for p in sp:
        if p['work'] == 'The Metamorphosis': continue                  # same text as the held-out Wyllie Metamorphosis
        for i, s in enumerate(p['sentences']):
            j = sr.get(f"{p['id']}-s{i:03d}")
            if j: reg.setdefault('schocken', []).append((s, teach(j)))
    say('Teacher-labelled register data (full battery output as the label; GoEmotions test texts excluded; Schocken Metamorphosis excluded):', '',
        '| register | texts |', '|---|---|')
    for k, v in reg.items(): say(f'| {k} | {len(v):,} |')
    held = reg.pop('wyllie:metamorphosis')
    train_reg = [x for k, v in reg.items() for x in v]
    # human GoEmotions train set (the 1,954 test texts excluded), exactly as usage_model.py
    agg = {}
    for k in (1, 2, 3):
        with open(f'{RAWD}/goemotions_{k}.csv', newline='', encoding='utf-8') as f:
            rd = csv.DictReader(f); labs = rd.fieldnames[9:]
            for row in rd:
                if row['example_very_unclear'] == 'True': continue
                a = agg.setdefault(row['id'], {'text': row['text'], 'n': 0, 'sum': collections.Counter()}); a['n'] += 1
                for l in labs:
                    if row[l] == '1': a['sum'][l] += 1
    gtrain = [a for a in agg.values() if ' '.join(a['text'].split())[:600] not in gtexts]
    Yh = np.array([vec14(mix_labels({l: c / a['n'] for l, c in a['sum'].items()})) for a in gtrain]); Xh = [a['text'] for a in gtrain]
    exp = {i: vec14(mix_labels(corp[i]['meta']['labels'])) for i in gtest}
    Xg = [corp[i]['text'] for i in gtest]; Eg = np.array([exp[i] for i in gtest])
    Xm = [s for s, _ in held]; Tm = np.array([v for _, v in held])
    def fit(texts, Y, w=None):
        v = TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True, lowercase=True, token_pattern=r"(?u)\b\w[\w']*\b|[!?]")
        X = v.fit_transform(texts); m = Ridge(alpha=1.5).fit(X, Y, sample_weight=w); return v, m
    def evalm(v, m):
        Pg = np.clip(m.predict(v.transform(Xg)), 0, 1); Pm = np.clip(m.predict(v.transform(Xm)), 0, 1)
        rs = [np.corrcoef(Eg[:, p], Pg[:, p])[0, 1] for p in range(14) if Eg[:, p].std() > 0 and Pg[:, p].std() > 0]
        netg = lambda M: (M[:, 1::2].sum(1) - M[:, 0::2].sum(1)) / 7
        cls = lambda x: np.where(x < -0.04, -1, np.where(x > 0.04, 1, 0))
        acc = float(np.mean(cls(netg(Eg)) == cls(netg(Pg))))
        rm = [np.corrcoef(Tm[:, p], Pm[:, p])[0, 1] for p in range(14) if Tm[:, p].std() > 0 and Pm[:, p].std() > 0]
        e0m = np.corrcoef(np.tanh(3 * netg(Tm)), np.tanh(3 * netg(Pm)))[0, 1]
        return float(np.mean(rs)), acc, float(np.mean(rm)), float(e0m), float(np.tanh(3 * netg(Pm)).mean())
    v0, m0 = joblib.load(os.path.join(H, 'usage_model.joblib'))
    models = {'S0 human-trained usage model (GoEmotions only)': (v0, m0)}
    models['S1 distilled from teachers, registers only (no human labels)'] = fit([t for t, _ in train_reg], np.array([y for _, y in train_reg]))
    pooled_t = Xh + [t for t, _ in train_reg]; pooled_y = np.vstack([Yh, np.array([y for _, y in train_reg])])
    models['S2 pooled: human GoEmotions + teacher-labelled registers'] = fit(pooled_t, pooled_y)
    teacher_g = np.array([vec14(score(rc[i], use=DEFAULT_USE, irony=True)) for i in gtest])
    say('', '| model | GoEmotions test: mean pole r (human) | net-sign accuracy | held-out Wyllie Metamorphosis: mean pole r (teacher) | e0 r | mean e0 |', '|---|---|---|---|---|---|')
    out = {}
    for k, (v, m) in models.items():
        out[k] = evalm(v, m); r = out[k]; say(f'| {k} | {r[0]:+.3f} | {r[1]:.3f} | {r[2]:+.3f} | {r[3]:+.3f} | {r[4]:+.3f} |')
    mt = float(np.tanh(3 * ((Tm[:, 1::2].sum(1) - Tm[:, 0::2].sum(1)) / 7)).mean())
    ng = lambda M: (M[:, 1::2].sum(1) - M[:, 0::2].sum(1)) / 7
    clsf = lambda x: np.where(x < -0.04, -1, np.where(x > 0.04, 1, 0))
    rt = [np.corrcoef(Eg[:, p], teacher_g[:, p])[0, 1] for p in range(14) if Eg[:, p].std() > 0 and teacher_g[:, p].std() > 0]
    say(f'| the teachers themselves (full battery; leaks on GoEmotions) | {np.mean(rt):+.3f} | {np.mean(clsf(ng(Eg)) == clsf(ng(teacher_g))):.3f} | — | — | {mt:+.3f} (teacher mean on Metamorphosis) |', '')
    # paired test on net-sign accuracy: S2 vs S0
    def acc_vec(v, m):
        Pg = np.clip(m.predict(v.transform(Xg)), 0, 1); return (clsf(ng(Eg)) == clsf(ng(Pg))).astype(float)
    a2 = acc_vec(*models['S2 pooled: human GoEmotions + teacher-labelled registers']); a0 = acc_vec(v0, m0)
    d = list(a2 - a0); bt = BC.bootstrap_ci(d, n_boot=2000); tt = BC.t_test_paired(list(a2), list(a0))
    say(f'S2 minus S0 on GoEmotions net-sign accuracy: {np.mean(d):+.3f} (95% CI [{bt["ci"][0]:+.3f}, {bt["ci"][1]:+.3f}], p = {tt["p"]:.2g}).', '')

if __name__ == '__main__':
    which = sys.argv[1:] or ['t1', 't2', 't3', 't4']
    for w in which: {'t1': t1, 't2': t2, 't3': t3, 't4': t4}[w]()
    if len(which) == 4: open(os.path.join(H, 'out', 'SOLUTION_TESTS_REPORT.md'), 'w').write('# Solution-model tests (T1–T4)\n\n' + '\n'.join(REP) + '\n')
