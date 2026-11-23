#!/usr/bin/env python3
"""Schocken parse: split Kafka's Complete Stories (Schocken 1971, a.b.e-book v3.0 PDF, Cody's copy at ~/Desktop/SpaceClaude/downloads/kafka.pdf)
into paragraphs with work, e-book page (the 'Page N' footer ends page N), line-on-page, and sentences.  Copyrighted: output is LOCAL ONLY (gitignored)."""
import json, os, re
from nltk.tokenize import sent_tokenize
H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/Kafka/schocken/complete_stories_layout.txt')
L = open(SRC, encoding='utf-8').read().split('\n')
foot = re.compile(r'^\s*Page (\d+)\s*$')
# page of each line = number of the next footer at or after it
page = [0] * len(L); nxt = None
for i in range(len(L) - 1, -1, -1):
    m = foot.match(L[i])
    if m: nxt = int(m.group(1))
    page[i] = nxt or 0
# titles from the contents list (lines 120-~330), '*' stripped
toc = []
for l in L[118:420]:
    if l.startswith('* Published'): break
    t = l.strip().rstrip('*').strip()
    if not t or foot.match(l) or t in ('Contents', 'Foreword by John Updike', 'Two Introductory Parables', 'The Longer Stories', 'The Shorter Stories'): continue
    toc.append(t)
    m = re.match(r'^(.*?)\s*\[(.*?)\]\s*$', t)
    if m: toc += [m.group(1).strip(), m.group(2).strip()]
    if ':' in t: toc.append(t.split(':')[0].strip())
toc += ['The Trees', 'Fellowship']
tset = set(toc)
body0 = next(i for i, l in enumerate(L) if l.strip() == 'TWO INTRODUCTORY PARABLES')
BACK = {'POSTSCRIPT', 'BIBLIOGRAPHY', 'EDITORS AND TRANSLATORS', 'ON THE MATERIAL INCLUDED IN THIS VOLUME', 'CHRONOLOGY', 'SELECTED WRITINGS ON KAFKA'}
SKIP = {'TWO INTRODUCTORY PARABLES', 'THE LONGER STORIES', 'THE SHORTER STORIES'}
back = False
work = 'front'; out = []; para = []; first = None; line_on_page = {}; cnt = 0; pn_in_work = 0
def flush():
    global para, first, pn_in_work
    if para:
        text = ' '.join(x.strip() for x in para).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 3:
            pn_in_work += 1
            out.append({'id': f'cs-{len(out):05d}', 'work': work, 'para': pn_in_work, 'page': page[first[0]], 'line': first[1], 'text': text})
    para, first = [], None
lp = 0; curpage = None
for i in range(body0, len(L)):
    l = L[i]
    if page[i] != curpage: curpage = page[i]; lp = 0
    if foot.match(l): flush(); continue
    s = l.strip()
    if not s: flush(); continue
    lp += 1
    if s in SKIP: flush(); continue
    if not back and not l.startswith(' ') and s in tset and s != work:
        flush(); work = s; pn_in_work = 0; back = s in BACK; continue
    if re.match(r'^\s*(Translated by|Notes?\b)', s): flush(); continue
    if l.startswith('     ') and para and len(l) - len(l.lstrip()) >= 5 and l.rstrip()[-1:] in '.:!?"”' and False: pass
    indent = len(l) - len(l.lstrip())
    if indent >= 5 and para and not para[-1].rstrip().endswith(('-', ',')) and indent < 20 and para[-1].rstrip()[-1:] in '.!?"”:;':
        flush()
    if first is None: first = (i, lp)
    para.append(l)
flush()
# merge pieces that start lowercase (paragraph broken by a page footer) into the previous paragraph of the same work
m = []
for p in out:
    if m and m[-1]['work'] == p['work'] and p['text'][:1].islower() and not m[-1]['text'].rstrip().endswith(('.', '!', '?', '"', '”')):
        m[-1]['text'] += ' ' + p['text']
    else: m.append(p)
out = m
for k, p in enumerate(out): p['id'] = f'cs-{k:05d}'; p['sentences'] = [s for s in sent_tokenize(p['text']) if s.strip()]
with open(os.path.join(H, 'schocken_paras.jsonl'), 'w') as f:
    for p in out: f.write(json.dumps(p, ensure_ascii=False) + '\n')
import collections
c = collections.Counter(p['work'] for p in out)
print(len(out), 'paragraphs', sum(len(p['sentences']) for p in out), 'sentences,', len(c), 'works')
for w, n in list(c.items())[:70]: print(f'  {n:4d} {w}')
