#!/usr/bin/env python3
"""Build the User-state test corpus (seed 20261122) from the local-only downloads, the Wernicke standard prompts and NLTK's NPS chat.
Writes corpus.jsonl (one prompt per line: id, source, text, meta).  Raw downloads live in
~/Desktop/SpaceClaude/local_only_references/UserStateCorpora (not committed: adversarial strings and third-party text).
Sources: GoEmotions (Demszky et al. 2020, Apache-2.0), TweetEval irony (Van Hee et al. 2018 / Barbieri et al. 2020),
AdvBench (Zou et al. 2023), HarmBench (Mazeika et al. 2024), jailbreak_llms (Shen et al. 2023), NPS Chat (Forsyth & Martell 2007)."""
import csv, json, os, random, re, sys, collections
csv.field_size_limit(10 ** 9)
R = random.Random(20261122)
H = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/UserStateCorpora')
WERN = os.path.join(H, '..', 'Wernicke', 'corpus')
out = []
def add(src, text, **meta):
    t = ' '.join(str(text).split())
    if len(t) >= 3:
        out.append({'id': f'{src}-{len(out):05d}', 'source': src, 'text': t[:600], 'meta': meta})

# A. GoEmotions: per text, the mean over raters of each label; 70 texts per label where >= half of the raters chose it
labs = None; agg = {}
for i in (1, 2, 3):
    with open(f'{RAW}/goemotions_{i}.csv', newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f)
        labs = rd.fieldnames[9:]
        for row in rd:
            if row['example_very_unclear'] == 'True':
                continue
            a = agg.setdefault(row['id'], {'text': row['text'], 'n': 0, 'sum': collections.Counter()})
            a['n'] += 1
            for l in labs:
                if row[l] == '1':
                    a['sum'][l] += 1
per = collections.defaultdict(list)
for k, a in agg.items():
    if a['n'] < 2:
        continue
    for l in labs:
        if a['sum'][l] / a['n'] >= 0.5:
            per[l].append(k)
seen = set()
for l in labs:
    ids = [k for k in per[l] if k not in seen]; R.shuffle(ids)
    for k in ids[:70]:
        seen.add(k); a = agg[k]
        add('goemotions', a['text'], labels={x: round(c / a['n'], 3) for x, c in a['sum'].items()}, n_raters=a['n'], top=l)
# B. irony
for sp, take in (('test', None), ('train', 700)):
    T = open(f'{RAW}/irony_{sp}_text.txt', encoding='utf-8').read().splitlines()
    L = open(f'{RAW}/irony_{sp}_labels.txt').read().split()
    idx = list(range(len(T)));
    if take: R.shuffle(idx); idx = idx[:take]
    for i in idx: add(f'irony_{sp}', T[i], irony=int(L[i]))
# C. adversarial
def col(path, name, n, src, **m):
    rows = list(csv.DictReader(open(path, newline='', encoding='utf-8'))); R.shuffle(rows)
    for r in rows[:n]: add(src, r[name], **m)
col(f'{RAW}/jailbreak_llms_jailbreak.csv', 'prompt', 300, 'adv_jailbreak', kind='jailbreak')
col(f'{RAW}/jailbreak_llms_regular.csv', 'prompt', 300, 'adv_regular', kind='regular')
col(f'{RAW}/advbench_harmful_behaviors.csv', 'goal', 300, 'adv_advbench', kind='harmful_request')
col(f'{RAW}/harmbench_text_all.csv', 'Behavior', 200, 'adv_harmbench', kind='harmful_request')
# D. the project's own prompts and novel sentences, NPS chat
for fn, src in (('prompts_chat.jsonl', 'proj_chat'), ('session_prompts_2026-10-17.jsonl', 'proj_session'), ('prompts_corpus.jsonl', 'proj_novel')):
    for line in open(os.path.join(WERN, fn)): add(src, json.loads(line)['text'])
from nltk.corpus import nps_chat
posts = list(nps_chat.xml_posts()); R.shuffle(posts)
for p in posts[:300]: add('nps_chat', p.text, act=p.get('class'))
# E. hand-written probes (expected primary emotion, written BEFORE any run) -- Currentwork/UserState/probes.jsonl
for line in open(os.path.join(H, 'probes.jsonl')):
    j = json.loads(line); add('probe', j['text'], expect=j['expect'], conv=j.get('conv'), turn=j.get('turn'), note=j.get('note'))
with open(os.path.join(H, 'corpus.jsonl'), 'w') as f:
    for o in out: f.write(json.dumps(o, ensure_ascii=False) + '\n')
c = collections.Counter(o['source'] for o in out)
print(len(out), dict(c))
