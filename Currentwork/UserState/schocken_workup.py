#!/usr/bin/env python3
"""Schocken workup (after schocken_parse.py and schocken_raw.py): every paragraph of Kafka's Complete Stories (Schocken 1971, Muir et al.;
Cody's PDF) through the battery and the usage model.  Per paragraph: e-book page, line on page, one-line synopsis, e0, the 15-cell strip.
Synopses: HAND (my words, schocken_synopses.json) for the three works Cody named; AUTO (first words of the paragraph) elsewhere, labelled.
Outputs:  out/SCHOCKEN_REPORT.md  numbers + hand synopses only (no book text);  out_local/schocken_*.ans  strips with book text (LOCAL ONLY)."""
import json, os, re, sys, time, collections
import numpy as np, joblib
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..'))
from user_state import BC, NT, Reading, score, scalar, net, code, digits, UserEmotionalState, DEFAULT_USE
import user_state_console as C
POLES = [(a, s) for a in NT for s in (0, 1)]
OUT = os.path.join(H, 'out'); LOC = os.path.join(H, 'out_local')
paras = [json.loads(l) for l in open(os.path.join(H, 'schocken_paras.jsonl'))]
_old = {p['id']: p for p in map(json.loads, open(os.path.join(H, 'schocken_paras_v0.jsonl')))}      # raw cache is keyed by the v0 paragraph ids
_byid = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'schocken_raw.jsonl')))}
raw_by_text = {}
for pid, p in _old.items():
    for i, s in enumerate(p['sentences']):
        j = _byid.get(f'{pid}-s{i:03d}')
        if j: raw_by_text[s] = j
class _Raw(dict):
    pass
vec, mdl = joblib.load(os.path.join(H, 'usage_model.joblib'))
HAND = json.load(open(os.path.join(H, 'schocken_synopses.json'))) if os.path.exists(os.path.join(H, 'schocken_synopses.json')) else {}
def reading_of(v):
    r = Reading.zero()
    for (a, s), x in zip(POLES, v): r[a][s] = float(min(1.0, max(0.0, x)))
    return r
def mean_reading(rs):
    out = Reading.zero(); n = len(rs)
    for r in rs:
        for a in NT:
            for s in (0, 1): out[a][s] += r[a][s] / n
    return out
rows = []
for p in paras:
    ss = [(i, s) for i, s in enumerate(p['sentences']) if s in raw_by_text]
    if not ss: continue
    bat = [score(raw_by_text[s], use=DEFAULT_USE, irony=True) for i, s in ss]
    use = [reading_of(v) for v in mdl.predict(vec.transform([s for _, s in ss]))]
    pb, pu = mean_reading(bat), mean_reading(use)
    key = f"{p['work']}|{p['para']}"
    syn = HAND.get(key); kind = 'hand'
    if not syn:
        kind = 'auto'; syn = ' '.join(p['text'].split()[:14]) + ('…' if len(p['text'].split()) > 14 else '')
    rows.append({'p': p, 'bat': pb, 'use': pu, 'e0b': scalar(pb), 'e0u': scalar(pu), 'syn': syn, 'kind': kind, 'sent_bat': bat, 'sent_use': use})
print(len(rows), 'paragraphs scored')
by = collections.OrderedDict()
for r in rows: by.setdefault(r['p']['work'], []).append(r)
NAMED = ['Before the Law', 'An Imperial Message', 'Description of a Struggle']
rep = ['# Schocken *Complete Stories* — paragraph workup (e-book pages)', '',
       f'{len(rows):,} paragraphs, {sum(len(r["p"]["sentences"]) for r in rows):,} sentences, {len(by)} works. Source: Cody\'s PDF (Schocken 1971, a.b.e-book v3.0, 555 pp.); '
       'page = the e-book\'s "Page N" footer (not the print page), line = non-blank line on that page. The book is in copyright: this report holds numbers and my own synopses only; '
       'the strips with book text are in `out_local/` (gitignored). e0b = battery, e0u = usage model (counts only). Synopsis kind: hand (mine) / auto (first words, mechanical).', '',
       '## Per work', '', '| work | paragraphs | e0 battery | e0 usage | first third → last third (battery) |', '|---|---|---|---|---|']
for w, rs in by.items():
    b = [r['e0b'] for r in rs]; u = [r['e0u'] for r in rs]; n = len(b)
    th = f'{BC.mean(b[:max(1, n // 3)]):+.3f} → {BC.mean(b[-max(1, n // 3):]):+.3f}' if n >= 3 else '—'
    rep.append(f'| {w} | {n} | {BC.mean(b):+.3f} | {BC.mean(u):+.3f} | {th} |')
allb = [r['e0b'] for r in rows]; allu = [r['e0u'] for r in rows]
pr = BC.pearson(allb, allu)
rep += ['', f'Paragraph e0, usage model against battery over the whole book: r = {pr["r"]:+.3f} (95% CI [{pr["ci"][0]:+.3f}, {pr["ci"][1]:+.3f}]); mean battery {BC.mean(allb):+.3f}, usage {BC.mean(allu):+.3f}.', '']
for w in NAMED:
    if w not in by: continue
    rep += [f'## {w}', '', '| # | page | line | synopsis | kind | e0 bat | e0 use | code |', '|---|---|---|---|---|---|---|---|']
    for r in by[w][:400]:
        p = r['p']; rep.append(f"| {p['para']} | {p['page']} | {p['line']} | {r['syn']} | {r['kind']} | {r['e0b']:+.2f} | {r['e0u']:+.2f} | {code(r['bat'])} |")
    rep.append('')
    if w in ('Before the Law', 'An Imperial Message'):
        rep += [f'### {w}: sentence by sentence (the work is one paragraph)', '', '| s | synopsis (mine) | e0 bat | e0 use | strip digits |', '|---|---|---|---|---|']
        for r in by[w]:
            for i, (sb, su) in enumerate(zip(r['sent_bat'], r['sent_use'])):
                d = digits(sb); dig = ''.join(str(d[l]) if l[1] != 'cursor' else '|' for l in C.LAYER_ORDER)
                rep.append(f"| {i} | {HAND.get(f'{w}|1|s{i}', '')} | {scalar(sb):+.2f} | {scalar(su):+.2f} | `{dig}` |")
        rep.append('')
open(os.path.join(OUT, 'SCHOCKEN_REPORT.md'), 'w').write('\n'.join(rep) + '\n')
# local .ans: one strip per paragraph (battery), plus sentence strips for the three named works
os.makedirs(LOC, exist_ok=True)
def ansdoc(ws, fname, sentences):
    L = ['\x1b[1mSchocken Complete Stories — user-state console model (battery)\x1b[0m', C.legend(), '']
    for w in ws:
        L.append(f'\x1b[1m── {w} ──\x1b[0m')
        st = UserEmotionalState(floor=0.15)
        for r in by[w]:
            p = r['p']; st.add(r['bat'])
            L.append(f"p{p['page']:>3} l{p['line']:>2}  {C.inline(r['bat'])}  acc {C.inline(st.state, with_scalar=False)}  [{r['kind']}] {r['syn']}")
            if sentences:
                for k, (s, sr) in enumerate(zip(p['sentences'], r['sent_bat'])): L.append(f"          {C.inline(sr)}  {HAND.get(f'{w}|{p['para']}|s{k}') or ' '.join(s.split())[:100]}")
        L.append('')
    open(os.path.join(LOC, fname), 'w').write('\n'.join(L) + '\n')
ansdoc([w for w in NAMED if w in by], 'schocken_three_works.ans', True)
ansdoc(list(by), 'schocken_all.ans', False)
print('\n'.join(rep[:30]))
