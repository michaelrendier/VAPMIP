#!/usr/bin/env python3
"""Stage C of the Kafka workup (after kafka_parse.py and kafka_raw.py): every sentence of The Trial and The Metamorphosis (David Wyllie's
translations, Project Gutenberg 7849 and 5200) through the pathway machinery, then the report.

PATHWAYS run per sentence:
  P1 battery      the user-state meters -> the 15-layer state (user_state.score), warmed across the sentences of a paragraph
  P2 extractor    the Wernicke content extractor v0: SHELL act and polarity; ANCHOR, relation, claim, HOOK lemmas (the seven slots)
  P3 context hash the Scalar Boxkite context hash (english_stats.ContextHash): class, density basin, gamma of each content word
and the cost of each, timed on a sample.  Output: out_local/kafka_*.ans (sentence lines with the console strip; local only, translation
text), out/KAFKA_REPORT.md (aggregates, line numbers, the hand synopses of the parable; short clips only).

Page numbers: Gutenberg plain text has none. Lines are line numbers of the e-text file. Page numbers need the Schocken edition
(see README: scan the pages, tesseract reads them locally)."""
import collections, json, math, os, re, sys, time
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(H, '..', '..')
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(H, '..', 'Wernicke', 'extractor'))
from user_state import (BC, NT, Reading, score, scalar, net, code, digits, UserEmotionalState, METERS, DEFAULT_USE,
                        incongruity, irony_k, stance_score)
import user_state_console as C

OUT = os.path.join(H, 'out'); LOC = os.path.join(H, 'out_local'); os.makedirs(OUT, exist_ok=True); os.makedirs(LOC, exist_ok=True)
paras = [json.loads(l) for l in open(os.path.join(H, 'kafka_paras.jsonl'))]
raw = {j['id']: j for j in map(json.loads, open(os.path.join(H, 'kafka_raw.jsonl')))}
POLES = [(a, s) for a in NT for s in (0, 1)]

# ── hand synopses of "Before the Law" (sentences 12-44 of trial-00125; Chapter Nine, e-text line 6250), written from the text ──
PARABLE = {
 12: "the priest begins the story: a doorkeeper stands before the law",
 13: "a man from the countryside asks to be let in",
 14: "the doorkeeper says not now",
 15: "the man asks whether he may enter later",
 16: "'possible, but not now'",
 17: "the gate is open; the man stoops to look through",
 18: "the doorkeeper laughs: try it, in spite of my prohibition",
 19: "he warns: I am powerful",
 20: "and I am only the lowest doorkeeper",
 21: "each room has a doorkeeper stronger than the last",
 22: "even I cannot bear to look at the third",
 23: "the man had expected the law open to all; he looks at the fur coat and the hooked nose and decides to wait",
 24: "he is given a stool beside the gate",
 25: "he sits there for days and years",
 26: "he tries again and again and wearies the doorkeeper",
 27: "the doorkeeper asks small, indifferent questions and always ends 'not yet'",
 28: "the man spends everything he brought on bribes",
 29: "the doorkeeper accepts it 'so you don't think you failed to do something'",
 30: "for years the man watches him without a break",
 31: "he forgets the other doormen; this one is the only obstacle",
 32: "first he curses his fate aloud, later he grumbles",
 33: "senile, he begs the fleas in the fur collar to change the doorkeeper's mind",
 34: "his eyes dim; he cannot tell whether it is darkening or his eyes failing",
 35: "now he sees an unquenchable radiance from the door",
 36: "he has not long to live",
 37: "all those years condense into one question never yet asked",
 38: "he beckons; he cannot raise his stiff body",
 39: "the doorkeeper must stoop far down; the size difference has turned against the man",
 40: "'what do you want to know now?'",
 41: "'you are insatiable'",
 42: "'everyone strives for the law; why has no one else come in all these years?'",
 43: "the doorkeeper, to be heard by the failing man, shouts: this entrance was meant only for you",
 44: "'now I shall go and close it'"}

t_all = time.time()
# ── P1: battery per sentence, warmed per paragraph ──
SID = lambda p, i: f"{p['id']}-s{i:03d}"
sent_rows = []; para_state = {}
for p in paras:
    st = UserEmotionalState(floor=0.0)                      # a plain running mean across the paragraph's sentences
    for i, s in enumerate(p['sentences']):
        r = raw.get(SID(p, i))
        if not r: continue
        rd = score(r, use=DEFAULT_USE, irony=True)
        st.add(rd)
        sent_rows.append({'pid': p['id'], 'i': i, 'work': p['work'], 'chapter': p['chapter'], 'para': p['para'], 'line': p['line'],
                          'text': s, 'reading': rd, 'acc': Reading({a: list(v) for a, v in st.state.items()}), 'raw': r})
    para_state[p['id']] = st

# ── P2: the extractor (seven slots) ──
import extract_v0 as X
t0 = time.time()
for row in sent_rows:
    try:
        e = X.extract(row['text'])
        an, rel, cl, hk = [], [], [], []; act = None
        for c in e['clauses']:
            s = c['slots']; act = act or s['SHELL']['act']
            an += [w['lemma'] for w in s['ANCHOR']]; rel += [w['lemma'] for w in s['SPAN']['relation']]
            cl += [w['lemma'] for w in s['SPAN']['claim']]; hk += [w['lemma'] for w in s['HOOK']]
        row['slots'] = {'act': act, 'anchor': an, 'relation': rel, 'claim': cl, 'hook': hk}
    except Exception as ex:
        row['slots'] = {'act': None, 'anchor': [], 'relation': [], 'claim': [], 'hook': [], 'err': str(ex)[:60]}
t_extract = time.time() - t0

# ── P3: the scalar boxkite context hash of the content words ──
from english_stats import ContextHash
ch = ContextHash()
t0 = time.time()
for row in sent_rows:
    words = row['slots']['anchor'] + row['slots']['relation'] + row['slots']['claim'] + row['slots']['hook']
    g, cls = [], []
    for w in words:
        o = ch.of(w)
        if o: cls.append(o['class']); g.append(o['gamma']) if o['gamma'] is not None else None
    row['ctx'] = {'n': len(cls), 'gamma': BC.mean(g) if g else None, 'classes': len(set(cls))}
t_ctx = time.time() - t0

# ── cost per pathway (single-sentence cost on a 150-sentence sample, one thread) ──
import random
R = random.Random(5); samp = R.sample(sent_rows, 150)
def timeit(f):
    t = time.perf_counter()
    for r in samp: f(r)
    return (time.perf_counter() - t) / len(samp) * 1000.0
from user_state import arousal_features, empath_counts, RawMeters
rm = RawMeters(load_models=False)
cost = {'tokenise + arousal/profanity counts': timeit(lambda r: arousal_features(r['text'])),
        'VADER lexicon': timeit(lambda r: rm.vader.polarity_scores(r['text'])),
        'Empath domain counts': timeit(lambda r: empath_counts(r['text'])),
        'stance + incongruity rules': timeit(lambda r: (stance_score(r['text']), incongruity(r['text'], 0.0))),
        'NPS dialogue-act naive Bayes': timeit(lambda r: rm.act(r['text'])),
        'combine the meters into the 15-layer state': timeit(lambda r: score(r['raw'])),
        'extractor v0 (seven slots, WordNet)': t_extract / len(sent_rows) * 1000.0,
        'scalar boxkite context hash lookups': t_ctx / len(sent_rows) * 1000.0}
import torch
torch.set_num_threads(8)
from transformers import pipeline
os.environ['HF_HUB_OFFLINE'] = '1'
lat = {}
for key, name in (('go_emotions (roberta-base, 125M)', 'SamLowe/roberta-base-go_emotions'), ('7-emotion (distilroberta, 82M)', 'j-hartmann/emotion-english-distilroberta-base'),
                  ('irony (roberta-base, 125M)', 'cardiffnlp/twitter-roberta-base-irony')):
    pl = pipeline('text-classification', model=name, device=-1, top_k=None, truncation=True, max_length=128)
    sm = samp[:40]; t = time.perf_counter()
    for r in sm: pl(r['text'])
    lat[key] = (time.perf_counter() - t) / len(sm) * 1000.0
cost.update({k + ', one sentence at a time': v for k, v in lat.items()})

# ── the .ans documents (local only) ──
def synop(row):
    s = row['slots']; key = [w for w in (s['hook'] + s['anchor']) if w][:2]
    return ' '.join(key) + (' / ' + ' '.join(s['relation'][:1]) if s['relation'] else '') + (' / ' + ' '.join(s['claim'][:1]) if s['claim'] else '')
for work in ('trial', 'metamorphosis'):
    lines = [f'\x1b[1mKafka, {work} (David Wyllie translation, Project Gutenberg): the user-state battery, per sentence\x1b[0m', C.legend(),
             'line = e-text line of the paragraph start; the strip is the 15-layer state of THAT sentence; para strip = the running mean over the paragraph so far', '']
    last = None
    for row in [r for r in sent_rows if r['work'] == work]:
        if (row['pid']) != last:
            last = row['pid']
            lines.append(f"\x1b[1m── {work} {row['chapter']} para {row['para']} (e-text line {row['line']}) ──\x1b[0m")
        lines.append(f"{C.inline(row['reading'])} {C.inline(row['acc'], False)}  s{row['i']:03d} {row['text'][:88]}   «{synop(row)}»")
    open(os.path.join(LOC, f'kafka_{work}.ans'), 'w').write('\n'.join(lines) + '\n')
# the parable in its own document, with the hand synopsis
par = [r for r in sent_rows if r['pid'] == 'trial-00125' and 12 <= r['i'] <= 44]
st = UserEmotionalState(floor=0.0); lines = ['\x1b[1mBefore the Law (The Trial, chapter nine; the priest tells it; e-text line 6250 on): sentence by sentence\x1b[0m', C.legend(), '']
for r in par:
    st.add(r['reading'])
    lines.append(f"{C.inline(r['reading'])} {C.inline(st.state, False)} s{r['i']:02d} {PARABLE[r['i']]}")
open(os.path.join(LOC, 'kafka_before_the_law.ans'), 'w').write('\n'.join(lines) + '\n')

# ── the report ──
pname = lambda p: f"{p[0]}{'-' if p[1] == 0 else '+'}"
rep = ['# Kafka through the pathway machinery', '',
       'Texts: *The Trial* and *The Metamorphosis*, David Wyllie\'s English translations from Project Gutenberg (7849, 5200), local copies. '
       f'{len(paras)} paragraphs (Gutenberg sets whole dialogue blocks as one paragraph), {len(sent_rows)} sentences. Line numbers are lines of the e-text file; '
       'there are no page numbers in the e-text. *The Complete Stories* (Schocken 1971, LCCN 75-161559) is in copyright and lending-only; "An Imperial Message" and '
       '"Description of a Struggle" are in it and in no public-domain English translation I could find.', '']
rep += ['## Cost of each pathway (this CPU, 8 cores, no GPU)', '', '| pathway | ms per sentence | sentences per second |', '|---|---|---|']
for k, v in sorted(cost.items(), key=lambda kv: kv[1]):
    rep.append(f'| {k} | {v:.3f} | {1000.0 / v:,.0f} |')
cheap = sum(v for k, v in cost.items() if 'one sentence' not in k and 'extractor' not in k and 'context hash' not in k)
rep += ['', f'Everything that is counting (the first six rows) together: {cheap:.2f} ms per sentence. The three models: {sum(lat.values()):.0f} ms per sentence one at a time '
        f'({sum(lat.values()) / max(cheap, 1e-9):,.0f} times the counting). The lexicon and rule meters are the cheap part; the models are what costs.', '']
# per chapter
rep += ['## Per work and chapter: the mean state of the sentences', '', '| work | chapter | sentences | e0 mean (95% CI) | dark mass | light mass | strongest dark pole | strongest light pole |', '|---|---|---|---|---|---|---|---|']
byc = collections.OrderedDict()
for r in sent_rows: byc.setdefault((r['work'], r['chapter']), []).append(r)
for (w, c), rs in byc.items():
    e0 = [scalar(r['reading']) for r in rs]
    bt = BC.bootstrap_ci(e0, n_boot=500) if len(e0) > 3 else {'ci': (float('nan'),) * 2}
    dk = {p: BC.mean([r['reading'][p[0]][0] for r in rs]) for p in NT and [(a, 0) for a in NT]}
    lt = {p: BC.mean([r['reading'][p[0]][1] for r in rs]) for p in [(a, 1) for a in NT]}
    sd = max(dk, key=dk.get); sl = max(lt, key=lt.get)
    rep.append(f"| {w} | {c} | {len(rs)} | {BC.mean(e0):+.3f} [{bt['ci'][0]:+.3f}, {bt['ci'][1]:+.3f}] | {sum(dk.values()):.2f} | {sum(lt.values()):.2f} | {pname(sd)} {dk[sd]:.2f} | {pname(sl)} {lt[sl]:.2f} |")
# vs conversation
conv = [json.loads(l) for l in open(os.path.join(OUT, 'results.jsonl'))]
cv = [x['e0'] for x in conv if x['source'] in ('goemotions', 'nps_chat', 'proj_chat', 'proj_session')]
ka = [scalar(r['reading']) for r in sent_rows]
mw = BC.mann_whitney_u(ka, cv); zero_k = sum(1 for r in sent_rows if code(r['reading']) == 0) / len(sent_rows)
rep += ['', f'Kafka sentences vs conversational prompts (GoEmotions, NPS chat, the project prompts): e0 mean {BC.mean(ka):+.3f} vs {BC.mean(cv):+.3f}; '
        f'Mann-Whitney AUC {mw["auc"]:.3f} (p = {mw["p"]:.1e}); Hedges g = {BC.hedges_g(ka, cv):+.2f}. Share of sentences that read all-zero (no change from baseline): '
        f'Kafka {zero_k:.3f}.', '']
# meter agreement
def meter_net(name):
    return [net(METERS[name](r['raw'])[0]) if METERS[name](r['raw'])[1] > 0 else 0.0 for r in sent_rows]
names = ['vader', 'go', 'hartmann', 'empath', 'stance', 'arousal']
M_ = {n: meter_net(n) for n in names}
rep += ['## Do the meters agree? (Pearson r of each meter\'s net, over all Kafka sentences)', '', '| | ' + ' | '.join(names) + ' |', '|---|' + '---|' * len(names)]
for a in names:
    row = []
    for b in names:
        if a == b: row.append('1'); continue
        if BC.stdev(M_[a]) == 0 or BC.stdev(M_[b]) == 0: row.append('-'); continue
        row.append(f"{BC.pearson(M_[a], M_[b])['r']:+.2f}")
    rep.append(f'| {a} | ' + ' | '.join(row) + ' |')
rep += ['']
# slots and context hash
acts = collections.Counter(r['slots']['act'] for r in sent_rows)
g_ = [r['ctx']['gamma'] for r in sent_rows if r['ctx']['gamma'] is not None]
rep += ['## What the other pathways say', '', f'Extractor v0 SHELL acts: ' + ', '.join(f'{k} {v}' for k, v in acts.most_common()) + '.',
        f'Scalar boxkite context hash: content words found {sum(r["ctx"]["n"] for r in sent_rows)}, mean gamma per sentence {BC.mean(g_):.3f} (sd {BC.stdev(g_):.3f}), '
        f'mean distinct classes per sentence {BC.mean([r["ctx"]["classes"] for r in sent_rows]):.2f}.', '']
# correlation of state with gamma
pairs = [(scalar(r['reading']), r['ctx']['gamma']) for r in sent_rows if r['ctx']['gamma'] is not None]
pc = BC.pearson([a for a, b in pairs], [b for a, b in pairs])
rep += [f'e0 against mean gamma of the sentence: r = {pc["r"]:+.3f} (95% CI [{pc["ci"][0]:+.3f}, {pc["ci"][1]:+.3f}], n = {pc["n"]}).', '']
# sarcasm / irony
qs = [r['raw']['irony'].get('irony', 0.0) for r in sent_rows]; ks = [irony_k(q, incongruity(r['text'], r['raw']['vader']['compound'])) for q, r in zip(qs, sent_rows)]
rep += ['## Irony and sarcasm', '', f'Irony model q > 0.9: {sum(q > 0.9 for q in qs)} of {len(qs)} sentences ({sum(q > 0.9 for q in qs) / len(qs):.3f}). '
        f'Incongruity swap strength k > 0.3: {sum(k > 0.3 for k in ks)} ({sum(k > 0.3 for k in ks) / len(ks):.3f}). '
        'Kafka\'s narration is not the voice of a user, so these meters are reading the content of a story, not a mind that wrote it to us: '
        'the model fires on dry statements of fact, and the cue list (written from conversational sarcasm) finds almost nothing. '
        'Neither can see the nihilistic or deadpan irony the passages carry; that sits in the implication.', '']
top = sorted(zip(ks, qs, sent_rows), key=lambda t: -t[0])[:8]
rep += ['Highest swap strength (line numbers only):', ''] + [f"- {r['work']} {r['chapter']} para {r['para']} s{r['i']:03d} (e-text line {r['line']}): k = {k:.2f}, q = {q:.2f}" for k, q, r in top] + ['']
# the parable
rep += ['## Before the Law (The Trial, chapter nine, paragraph 15, e-text line 6250 on)', '', '| s | hand synopsis | e0 | strongest poles | irony q | seven-slot act / relation | context gamma |', '|---|---|---|---|---|---|---|']
for r in par:
    rd = r['reading']; top = sorted(((rd[a][s], (a, s)) for a, s in POLES), reverse=True)[:3]
    tp = ', '.join(f'{pname(p)}{v:.2f}' for v, p in top if v > .05) or '-'
    g = r['ctx']['gamma']
    rep.append(f"| {r['i']} | {PARABLE[r['i']]} | {scalar(rd):+.2f} | {tp} | {r['raw']['irony'].get('irony', 0):.2f} | {r['slots']['act']} / {' '.join(r['slots']['relation'][:2])} | {g:.2f} |" if g is not None else
               f"| {r['i']} | {PARABLE[r['i']]} | {scalar(rd):+.2f} | {tp} | {r['raw']['irony'].get('irony', 0):.2f} | {r['slots']['act']} / {' '.join(r['slots']['relation'][:2])} | - |")
pe = [scalar(r['reading']) for r in par]
rep += ['', f'The parable as a whole: mean e0 {BC.mean(pe):+.3f}; first third {BC.mean(pe[:11]):+.3f}, middle {BC.mean(pe[11:22]):+.3f}, last third {BC.mean(pe[22:]):+.3f}. '
        f'Last sentence read e0 {pe[-1]:+.2f}; the sentence that carries the whole meaning (43, "this entrance was meant only for you") read e0 {pe[-2]:+.2f}.', '']
open(os.path.join(OUT, 'KAFKA_REPORT.md'), 'w').write('\n'.join(rep) + '\n')
print('done in', round(time.time() - t_all), 's; sentences', len(sent_rows)); print('\n'.join(rep[:24]))
