#!/usr/bin/env python3
"""The cheapest pathway: usage statistics only.  A word + bigram count model (tf-idf, ridge) trained on the human-labelled GoEmotions
texts (all of them EXCEPT the 1,954 held-out test texts of the battery), predicting the 14 pole levels directly.  At run time it is a
sparse dot product.  Compared on the same held-out texts with VADER alone, the meter battery without the GoEmotions-trained model
(independent) and the full battery (leaks).  Then applied to Kafka.
Writes out/USAGE_MODEL_REPORT.md.  Model kept local (usage_model.joblib, gitignored)."""
import csv, collections, json, math, os, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..'))
csv.field_size_limit(10 ** 9)
from user_state import BC, NT, Reading, mix_labels, score, net, scalar, DEFAULT_USE
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
import joblib
RAW = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/UserStateCorpora')
POLES = [(a, s) for a in NT for s in (0, 1)]
corp = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'corpus.jsonl')))}
raw = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'raw_cache.jsonl')))}
test = [i for i in corp if corp[i]['source'] == 'goemotions']
test_texts = {corp[i]['text'] for i in test}
agg = {}
for k in (1, 2, 3):
    with open(f'{RAW}/goemotions_{k}.csv', newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f); labs = rd.fieldnames[9:]
        for row in rd:
            if row['example_very_unclear'] == 'True': continue
            a = agg.setdefault(row['id'], {'text': row['text'], 'n': 0, 'sum': collections.Counter()})
            a['n'] += 1
            for l in labs:
                if row[l] == '1': a['sum'][l] += 1
train = [a for a in agg.values() if ' '.join(a['text'].split())[:600] not in test_texts]
Xt = [a['text'] for a in train]
Y = np.array([[mix_labels({l: c / a['n'] for l, c in a['sum'].items()})[p[0]][p[1]] for p in POLES] for a in train])
print('train texts', len(train), 'test texts', len(test), flush=True)
t = time.time()
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True, lowercase=True, token_pattern=r"(?u)\b\w[\w']*\b|[!?]")
X = vec.fit_transform(Xt); mdl = Ridge(alpha=1.5).fit(X, Y); fit_s = time.time() - t
joblib.dump((vec, mdl), os.path.join(H, 'usage_model.joblib'))
print('fit', round(fit_s, 1), 's, features', X.shape[1], flush=True)

def reading_of(v):
    r = Reading.zero()
    for (a, s), x in zip(POLES, v): r[a][s] = float(min(1.0, max(0.0, x)))
    return r
Xe = vec.transform([corp[i]['text'] for i in test]); pred = mdl.predict(Xe)
R = {'usage model (word+bigram counts, ridge)': {i: reading_of(p) for i, p in zip(test, pred)},
     'VADER only': {i: score(raw[i], use=('vader',), irony=False) for i in test},
     'battery without GoEmotions-trained meter (independent)': {i: score(raw[i], use=('vader', 'hartmann', 'arousal', 'profanity', 'act', 'empath', 'stance'), irony=False) for i in test},
     'full battery (leaks)': {i: score(raw[i], use=DEFAULT_USE, irony=True) for i in test}}
cls = lambda x: 'dark' if x < -0.04 else 'light' if x > 0.04 else 'flat'
exp = {i: mix_labels(corp[i]['meta']['labels']) for i in test}
rep = ['# The usage-statistics pathway (word + bigram counts) against the meter battery', '',
       f'Trained on {len(train):,} human-labelled GoEmotions texts (the {len(test):,} test texts of the battery excluded); {X.shape[1]:,} word and bigram features; fit {fit_s:.1f} s. '
       'Target: the 14 pole levels implied by the human labels through the setpoint table. Test: the same 1,954 held-out texts as T1.', '',
       '| pathway | mean r over 14 poles | net-sign accuracy | kappa | cost per text |', '|---|---|---|---|---|']
cost = {'usage model (word+bigram counts, ridge)': None, 'VADER only': '0.26 ms', 'battery without GoEmotions-trained meter (independent)': '~1.0 ms counting + 86 ms (7-emotion model)',
        'full battery (leaks)': '~1.96 ms counting + 364 ms (three models)'}
t = time.perf_counter()
for _ in range(3): mdl.predict(vec.transform([corp[i]['text'] for i in test[:300]]))
ms_usage = (time.perf_counter() - t) / (3 * 300) * 1000
cost['usage model (word+bigram counts, ridge)'] = f'{ms_usage:.3f} ms (batch of 300)'
res = {}
for name, rr in R.items():
    rs = []
    for p in POLES:
        e = [exp[i][p[0]][p[1]] for i in test]; y = [rr[i][p[0]][p[1]] for i in test]
        if BC.stdev(e) > 0 and BC.stdev(y) > 0: rs.append(BC.pearson(e, y)['r'])
    ex = [cls(net(exp[i])) for i in test]; pr = [cls(net(rr[i])) for i in test]
    k = BC.cohens_kappa(ex, pr); acc = sum(a == b for a, b in zip(ex, pr)) / len(ex)
    res[name] = (BC.mean(rs), acc, k['kappa'], len(rs))
    rep.append(f'| {name} | {BC.mean(rs):+.3f} ({len(rs)} poles) | {acc:.3f} | {k["kappa"]:.3f} | {cost[name]} |')
# paired difference usage vs independent on net-sign accuracy
def accv(name): return [1.0 if cls(net(exp[i])) == cls(net(R[name][i])) else 0.0 for i in test]
a_u, a_i, a_v = accv('usage model (word+bigram counts, ridge)'), accv('battery without GoEmotions-trained meter (independent)'), accv('VADER only')
for lab, a_b in (('independent battery', a_i), ('VADER', a_v)):
    d = [x - y for x, y in zip(a_u, a_b)]; b = BC.bootstrap_ci(d, n_boot=2000); tt = BC.t_test_paired(a_u, a_b)
    rep.append('')
    rep.append(f'Usage model minus {lab}, net-sign accuracy: {BC.mean(d):+.3f} (bootstrap 95% CI [{b["ci"][0]:+.3f}, {b["ci"][1]:+.3f}], paired t = {tt["t"]:.2f}, p = {tt["p"]:.1e}).')
# Kafka
paras = [json.loads(l) for l in open(os.path.join(H, 'kafka_paras.jsonl'))]
kraw = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'kafka_raw.jsonl')))}
rows = [(f"{p['id']}-s{i:03d}", s, p) for p in paras for i, s in enumerate(p['sentences'])]
Xk = vec.transform([s for _, s, _ in rows]); pk = mdl.predict(Xk)
ku = [scalar(reading_of(v)) for v in pk]
kb = [scalar(score(kraw[i], use=DEFAULT_USE, irony=True)) for i, _, _ in rows]
pr_ = BC.pearson(ku, kb)
rep += ['', '## On Kafka (4,627 sentences)', '', f'Per-sentence e0, usage model against the full battery: r = {pr_["r"]:+.3f} (95% CI [{pr_["ci"][0]:+.3f}, {pr_["ci"][1]:+.3f}]). '
        f'Mean e0: usage model {BC.mean(ku):+.3f}, battery {BC.mean(kb):+.3f}.', '']
par = [(k, v) for k, v in zip(rows, ku) if k[2]['id'] == 'trial-00125' and 12 <= int(k[0].split('-s')[1]) <= 44]
pu = [v for _, v in par]
rep += [f'Before the Law: mean e0 {BC.mean(pu):+.3f}; thirds {BC.mean(pu[:11]):+.3f}, {BC.mean(pu[11:22]):+.3f}, {BC.mean(pu[22:]):+.3f}; last sentence ("now I\'ll go and close it") {pu[-1]:+.2f}; '
        f'sentence 43 ("this entrance was meant only for you") {pu[-2]:+.2f}.', '']
# highest-weight words for a few poles
fn = np.array(vec.get_feature_names_out())
rep += ['## What the usage model learned (largest weights)', '']
for p in [('NE', 0), ('OXT', 1), ('DA', 1), ('5HT', 0), ('GABA', 0), ('OPI', 1)]:
    j = POLES.index(p); top = np.argsort(-mdl.coef_[j])[:10]
    rep.append(f"- {p[0]}{'-' if p[1] == 0 else '+'}: " + ', '.join(fn[top]))
open(os.path.join(H, 'out', 'USAGE_MODEL_REPORT.md'), 'w').write('\n'.join(rep) + '\n')
print('\n'.join(rep))
