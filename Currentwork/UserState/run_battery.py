#!/usr/bin/env python3
"""Stage 2: score every cached prompt, validate against labels, and write the report and the .ans documents.
Reads corpus.jsonl + raw_cache.jsonl (run_raw.py).  Statistics come from ValaQuenta's Bell Curve engine (`BC`).

    python3 run_battery.py            -> out/REPORT.md, out/results.jsonl, out/*.ans, out_local/*.ans (not committed)

THE TESTS (the expected value is fixed before the run; a failed test is a result, and sets the next retool)
  T1  GoEmotions (human raters, n ~ 1950): for each of the 14 poles, the predicted level against the level the human labels imply
      through the SAME setpoint table (Pearson r, CI, n-sigma, AUC at >= 0.25, Holm across the 14 poles); net-sign agreement (kappa)
      for three configurations: vader only | independent of GoEmotions (no `go` meter) | full battery.
  T2  Irony (TweetEval test, n = 784): the irony meter against the human label (AUC, F1, kappa, at 0.5 and at the best cut).
  T3  Probes (85 hand-written, expectations written before running): pass when the pole vector points the same way (cosine >= 0.5),
      or, for expected neutral, the activity stays small.  Three multi-turn conversations run through the warming object.
  T4  Adversarial (jailbreak vs regular, harmful requests): where do they land; separation by Mann-Whitney AUC and Hedges g.
"""
import collections, json, math, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', '..'))
from user_state import (BC, NT, Reading, mix_labels, EMO, score, digits, scalar, net, code, sedenion, LAYER_ORDER,
                        UserEmotionalState, DEFAULT_USE, apply_irony, incongruity, irony_k)
import user_state_console as C

OUT = os.path.join(H, 'out'); LOC = os.path.join(H, 'out_local')
os.makedirs(OUT, exist_ok=True); os.makedirs(LOC, exist_ok=True)
corp = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'corpus.jsonl')))}
raw = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'raw_cache.jsonl'))) if j['id'] in corp}
ids = [i for i in corp if i in raw]
POLES = [(a, s) for a in NT for s in (0, 1)]
pname = lambda p: f"{p[0]}{'-' if p[1] == 0 else '+'}"
vec = lambda r: [r[a][s] for a, s in POLES]
cos = lambda u, v: (sum(x * y for x, y in zip(u, v)) / (math.sqrt(sum(x * x for x in u)) * math.sqrt(sum(y * y for y in v))))\
    if any(u) and any(v) else 0.0


def auc_ci(auc, n1, n2, z=1.96):
    """Hanley-McNeil (1982) standard error for an AUC."""
    q1, q2 = auc / (2 - auc), 2 * auc * auc / (1 + auc)
    se = math.sqrt((auc * (1 - auc) + (n1 - 1) * (q1 - auc * auc) + (n2 - 1) * (q2 - auc * auc)) / (n1 * n2))
    return max(0.0, auc - z * se), min(1.0, auc + z * se)


INDEP_USE = ('vader', 'hartmann', 'arousal', 'profanity', 'act', 'empath', 'stance')
CONFIGS = {'vader only': dict(use=('vader',), irony=False),
           'independent of GoEmotions, no irony swap': dict(use=INDEP_USE, irony=False),
           'independent of GoEmotions (vader+hartmann+arousal+profanity+act+empath+stance, irony swap)': dict(use=INDEP_USE, irony=True),
           'full battery (adds the go_emotions model: LEAKS, it trained on these labels)': dict(use=DEFAULT_USE, irony=True)}
R = {name: {i: score(raw[i], **kw) for i in ids} for name, kw in CONFIGS.items()}
FULL = list(CONFIGS)[3]; INDEP = list(CONFIGS)[2]
# the config the battery ships as default for unseen prompts is the full one; INDEP is the honest validation against GoEmotions
rep = ['# User emotional state: battery report', '',
       f'Prompts scored: **{len(ids)}**  ·  sources: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(corp[i]['source'] for i in ids).items()), '',
       'The state is 7 neurotransmitters x 2 poles (dark, light), level 0-9, e0 = tanh(3 x net). Statistics: ValaQuenta `bell_curve` v1.0.', '']

# ───────────────────────── T1 GoEmotions ─────────────────────────
go = [i for i in ids if corp[i]['source'] == 'goemotions']
rep += ['## T1  GoEmotions: predicted poles against what the human labels imply', '',
        f'n = {len(go)} texts, 70 per emotion (where at least half of the raters chose it). Expected pole = the human label mix through the same setpoint table. '
        'Because both sides use one table, T1 measures whether the *text meters* recover the human-labelled emotion; it does not validate the table itself.', '']
T1 = {}
for name in CONFIGS:
    rows = []
    ps = []
    for p in POLES:
        e = [mix_labels(corp[i]['meta']['labels'])[p[0]][p[1]] for i in go]
        y = [R[name][i][p[0]][p[1]] for i in go]
        if BC.stdev(e) == 0 or BC.stdev(y) == 0:
            rows.append((pname(p), float('nan'), (float('nan'),) * 2, float('nan'), float('nan'), float('nan'))); ps.append(1.0); continue
        pr = BC.pearson(e, y)
        pos = [yy for yy, ee in zip(y, e) if ee >= .25]; neg = [yy for yy, ee in zip(y, e) if ee < .25]
        auc = BC.mann_whitney_u(pos, neg)['auc'] if len(pos) > 4 and len(neg) > 4 else float('nan')
        rows.append((pname(p), pr['r'], pr['ci'], math.atanh(min(0.999999, abs(pr['r']))) * math.sqrt(len(e) - 3), auc, len(pos))); ps.append(max(pr['p'], 1e-300))
    adj = BC.holm(ps)
    T1[name] = (rows, adj)
    # net sign agreement
    def cls(x): return 'dark' if x < -0.04 else 'light' if x > 0.04 else 'flat'
    e = [cls(net(mix_labels(corp[i]['meta']['labels']))) for i in go]
    y = [cls(net(R[name][i])) for i in go]
    k = BC.cohens_kappa(e, y)
    acc = sum(a == b for a, b in zip(e, y)) / len(e)
    rep += [f'### {name}', '', '| pole | r | 95% CI | sigma (Fisher z) | AUC(>=.25) | n present | Holm p |', '|---|---|---|---|---|---|---|']
    for (pn, r, ci, sg, auc, npres), a in zip(rows, adj):
        rep.append(f'| {pn} | {r:+.3f} | [{ci[0]:+.2f}, {ci[1]:+.2f}] | {sg:.1f} | {auc:.3f} | {npres} | {a:.1e} |')
    rep += ['', f'net-sign agreement (dark/flat/light): accuracy {acc:.3f}, Cohen kappa {k["kappa"]:.3f} (se {k["se"]:.3f}); '
                f'mean r over the 14 poles {BC.mean([r[1] for r in rows if r[1] == r[1]]):+.3f}', '']
# paired comparison vader-only vs independent: bootstrap of the difference in net-sign accuracy
def acc_of(name, idx):
    def cls(x): return 'dark' if x < -0.04 else 'light' if x > 0.04 else 'flat'
    return [1.0 if cls(net(mix_labels(corp[i]['meta']['labels']))) == cls(net(R[name][i])) else 0.0 for i in idx]
a_v, a_i = acc_of(list(CONFIGS)[0], go), acc_of(INDEP, go)
a_n = acc_of(list(CONFIGS)[1], go)
d = [b - a for a, b in zip(a_v, a_i)]
bt = BC.bootstrap_ci(d, n_boot=2000); pt = BC.t_test_paired(a_i, a_v)
dn = [b - a for a, b in zip(a_v, a_n)]; bn = BC.bootstrap_ci(dn, n_boot=2000); pn = BC.t_test_paired(a_n, a_v)
rep += [f'**Independent battery WITHOUT the irony swap vs vader alone, net-sign accuracy**: {BC.mean(dn):+.3f} (bootstrap 95% CI [{bn["ci"][0]:+.3f}, {bn["ci"][1]:+.3f}]; paired t = {pn["t"]:.2f}, p = {pn["p"]:.2e}).', '']
rep += [f'**Independent battery WITH the irony swap vs vader alone, net-sign accuracy**: +{BC.mean(d):.3f} (bootstrap 95% CI [{bt["ci"][0]:+.3f}, {bt["ci"][1]:+.3f}]; paired t = {pt["t"]:.2f}, p = {pt["p"]:.2e}).', '']

# ───────────────────────── T2 irony ─────────────────────────
tst = [i for i in ids if corp[i]['source'] == 'irony_test']
y = [corp[i]['meta']['irony'] for i in tst]; q = [raw[i]['irony'].get('irony', 0.0) for i in tst]
pos = [s for s, l in zip(q, y) if l == 1]; neg = [s for s, l in zip(q, y) if l == 0]
mw = BC.mann_whitney_u(pos, neg); lo, hi = auc_ci(mw['auc'], len(pos), len(neg))
def at(th):
    tp = sum(1 for s, l in zip(q, y) if s >= th and l == 1); fp = sum(1 for s, l in zip(q, y) if s >= th and l == 0)
    fn = sum(1 for s, l in zip(q, y) if s < th and l == 1); tn = sum(1 for s, l in zip(q, y) if s < th and l == 0)
    return BC.confusion_metrics(tp, fp, fn, tn), (tp, fp, fn, tn)
cuts = [c / 100 for c in range(5, 96, 5)]
best = max(cuts, key=lambda c: at(c)[0]['f1'] if at(c)[0]['f1'] == at(c)[0]['f1'] else -1)
m5, c5 = at(0.5); mb, cb = at(best)
kap = BC.cohens_kappa(y, [1 if s >= 0.5 else 0 for s in q])
trn = [i for i in ids if corp[i]['source'] == 'irony_train']
def aucs(idx):
    yy = [corp[i]['meta']['irony'] for i in idx]
    out = {}
    for nm, f in (('model q', lambda i: raw[i]['irony'].get('irony', 0.0)), ('incongruity cues s', lambda i: incongruity(raw[i]['text'], raw[i]['vader']['compound'])),
                  ('k (the swap strength used)', lambda i: irony_k(raw[i]['irony'].get('irony', 0.0), incongruity(raw[i]['text'], raw[i]['vader']['compound'])))):
        sc = [f(i) for i in idx]
        po = [a for a, l in zip(sc, yy) if l == 1]; ne = [a for a, l in zip(sc, yy) if l == 0]
        m_ = BC.mann_whitney_u(po, ne); out[nm] = (m_['auc'],) + auc_ci(m_['auc'], len(po), len(ne))
    return out
at_tr, at_te = aucs(trn), aucs(tst)
rep += ['## T2b  The irony swap strength k against the human irony labels', '', '| signal | AUC train (n=%d) | AUC test (n=%d) |' % (len(trn), len(tst)), '|---|---|---|']
for nm in at_tr: rep.append(f'| {nm} | {at_tr[nm][0]:.3f} [{at_tr[nm][1]:.3f}, {at_tr[nm][2]:.3f}] | {at_te[nm][0]:.3f} [{at_te[nm][1]:.3f}, {at_te[nm][2]:.3f}] |')
rep.append('')
rep += ['## T2  Irony meter against TweetEval human labels (test split, n = %d, %d ironic)' % (len(tst), len(pos)), '',
        f'AUC {mw["auc"]:.3f} (95% CI [{lo:.3f}, {hi:.3f}], p = {mw["p"]:.1e}, {BC.p_to_sigma(max(mw["p"], 1e-300)):.1f} sigma). At 0.5: precision {m5["precision"]:.3f}, recall {m5["recall"]:.3f}, F1 {m5["f1"]:.3f}, kappa {kap["kappa"]:.3f}, MCC {m5["mcc"]:.3f}. '
        f'Best cut {best:.2f}: F1 {mb["f1"]:.3f}, precision {mb["precision"]:.3f}, recall {mb["recall"]:.3f}.', '']

# ───────────────────────── T3 probes ─────────────────────────
pr = [i for i in ids if corp[i]['source'] == 'probe']
rep += ['## T3  Hand-written probes (expectations fixed before the run)', '', '| # | expect | got (top poles) | cos | e0 | pass | prompt |', '|---|---|---|---|---|---|---|']
npass = 0; probe_rows = []
for n, i in enumerate(pr):
    note_ = corp[i]['meta'].get('note') or ''
    exl = 'cynical' if (note_.startswith('sarcasm') or note_.startswith('irony')) else corp[i]['meta']['expect']   # v2: Cody calls the eye roll 'cynical'
    ex = mix_labels({exl: 1.0}); r = R[FULL][i]
    ev, rv = vec(ex), vec(r)
    if exl == 'neutral':
        ok = max(rv) < 0.25; cs = float('nan')
    else:
        cs = cos(ev, rv); ok = cs >= 0.5
    npass += ok
    top = sorted(zip(rv, POLES), reverse=True)[:3]
    probe_rows.append((i, ok, cs))
    rep.append(f"| {n + 1} | {exl}{' (v1: ' + corp[i]['meta']['expect'] + ')' if exl != corp[i]['meta']['expect'] else ''} | {', '.join(f'{pname(p)}{v:.2f}' for v, p in top if v > .05) or '-'} | {cs:.2f} | {scalar(r):+.2f} | {'yes' if ok else '**NO**'} | {corp[i]['text'][:70]} |")
wl = BC.wilson_ci(npass, len(pr))
rep += ['', f'**Probes passed: {npass}/{len(pr)} = {npass / len(pr):.3f} (Wilson 95% [{wl[0]:.3f}, {wl[1]:.3f}])**', '']
# conversations
rep += ['### Warm-up: three conversations through the UserEmotionalState (cold prompt assigns, later prompts add)', '']
for cid in 'ABC':
    turns = sorted((i for i in pr if corp[i]['meta'].get('conv') == cid), key=lambda i: corp[i]['meta']['turn'])
    if not turns:
        continue
    st = UserEmotionalState(); rep.append(f"**{cid}: {corp[turns[0]]['meta']['note']}**"); rep.append('')
    rep.append('| turn | prompt | reading e0 | accumulated e0 | drift |'); rep.append('|---|---|---|---|---|')
    for i in turns:
        st.add(R[FULL][i]); rep.append(f"| {corp[i]['meta']['turn']} | {corp[i]['text'][:60]} | {scalar(R[FULL][i]):+.2f} | {scalar(st.state):+.2f} | {st.drift()['net_slope']:+.3f} |")
    rep.append('')

# ───────────────────────── T4 adversarial ─────────────────────────
rep += ['## T4  Adversarial and regular prompts: where they land', '', '| source | n | e0 mean (sd) | net mean | strongest dark pole | strongest light pole |', '|---|---|---|---|---|---|']
by = collections.defaultdict(list)
for i in ids: by[corp[i]['source']].append(i)
for src in sorted(by):
    xs = [scalar(R[FULL][i]) for i in by[src]]; ns = [net(R[FULL][i]) for i in by[src]]
    dk = max(POLES[0::2], key=lambda p: BC.mean([R[FULL][i][p[0]][0] for i in by[src]])); lt = max(POLES[1::2], key=lambda p: BC.mean([R[FULL][i][p[0]][1] for i in by[src]]))
    rep.append(f"| {src} | {len(xs)} | {BC.mean(xs):+.3f} ({BC.stdev(xs):.3f}) | {BC.mean(ns):+.3f} | {pname(dk)} {BC.mean([R[FULL][i][dk[0]][0] for i in by[src]]):.2f} | {pname(lt)} {BC.mean([R[FULL][i][lt[0]][1] for i in by[src]]):.2f} |")
jb, rg = [scalar(R[FULL][i]) for i in by['adv_jailbreak']], [scalar(R[FULL][i]) for i in by['adv_regular']]
mw = BC.mann_whitney_u(jb, rg); wt = BC.t_test_welch(jb, rg)
rep += ['', f'Jailbreak vs regular prompts, e0: AUC {mw["auc"]:.3f}, Welch t = {wt["t"]:.2f} (p = {wt["p"]:.1e}), Hedges g = {BC.hedges_g(jb, rg):+.2f}.', '']
# per-pole screening of jailbreak vs regular, Holm
pv = []; names = []
for p in POLES:
    a = [R[FULL][i][p[0]][p[1]] for i in by['adv_jailbreak']]; b = [R[FULL][i][p[0]][p[1]] for i in by['adv_regular']]
    if BC.stdev(a + b) > 0: pv.append(max(BC.mann_whitney_u(a, b)['p'], 1e-300)); names.append((p, BC.hedges_g(a, b)))
adj = BC.holm(pv)
rep += ['Jailbreak vs regular, per pole (Mann-Whitney, Holm-adjusted): ' + '; '.join(f'{pname(p)} g={g:+.2f} p={a:.1e}' for (p, g), a in zip(names, adj) if a < .05) or 'none significant', '']

# ───────────────────────── descriptive: the whole corpus ─────────────────────────
e0 = [scalar(R[FULL][i]) for i in ids]; jb_ = BC.jarque_bera(e0)
rep += ['## All prompts: the distribution of e0', '', f'n = {len(e0)}, mean {BC.mean(e0):+.3f}, sd {BC.stdev(e0):.3f}, median {BC.median(e0):+.3f}, skew {jb_["skew"]:+.2f}, excess kurtosis {jb_["kurt_excess"]:+.2f}; '
        f'Jarque-Bera p = {jb_["p"]:.1e} (not normal: the readings pile up at zero and the tails are heavy).', '']
cd = collections.Counter(code(R[FULL][i]) for i in ids)
rep += [f'Distinct 14-digit codes: {len(cd)} of {len(ids)} prompts; the most common state is code {cd.most_common(1)[0][0]:014d} ({cd.most_common(1)[0][1]} prompts, '
        f'{"all zero: no change from baseline" if cd.most_common(1)[0][0] == 0 else "see out/results.jsonl"}).', '']

open(os.path.join(OUT, 'REPORT.md'), 'w').write('\n'.join(rep) + '\n')
with open(os.path.join(OUT, 'results.jsonl'), 'w') as f:
    for i in ids:
        r = R[FULL][i]
        f.write(json.dumps({'id': i, 'source': corp[i]['source'], 'text': corp[i]['text'][:200], 'e0': round(scalar(r), 4), 'net': round(net(r), 4),
                            'code': f'{code(r):014d}', 'sedenion': [round(x, 3) for x in sedenion(r)]}, ensure_ascii=False) + '\n')
# .ans documents: committed set vs local-only set (third-party tweets and adversarial strings stay local)
def items(srcs):
    for i in ids:
        if corp[i]['source'] in srcs:
            note = corp[i]['meta'].get('expect') or corp[i]['meta'].get('top') or corp[i]['meta'].get('kind') or ''
            yield corp[i]['text'], R[FULL][i], f'[{corp[i]["source"]}{" " + note if note else ""}]'
open(os.path.join(OUT, 'user_state_probes.ans'), 'w').write(C.ans_document(items({'probe'}), 'User emotional state: hand-written probes'))
open(os.path.join(OUT, 'user_state_corpus.ans'), 'w').write(C.ans_document(items({'goemotions', 'proj_chat', 'proj_session', 'proj_novel', 'nps_chat', 'probe'}), 'User emotional state: GoEmotions, project prompts, NPS chat, probes'))
open(os.path.join(LOC, 'user_state_irony_adversarial.ans'), 'w').write(C.ans_document(items({'irony_test', 'irony_train', 'adv_jailbreak', 'adv_regular', 'adv_advbench', 'adv_harmbench'}), 'User emotional state: irony tweets and adversarial prompts (local only)'))
print('\n'.join(rep[:6])); print('...'); print(f'probes passed {npass}/{len(pr)}; REPORT.md written')
