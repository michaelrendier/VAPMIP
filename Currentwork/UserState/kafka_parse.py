#!/usr/bin/env python3
"""Stage A of the Kafka workup: split the Project Gutenberg e-texts (David Wyllie's translations of The Trial, Gutenberg 7849, and
The Metamorphosis, 5200) into paragraphs and sentences, recording work, chapter, paragraph number and the line number in the e-text
file where each paragraph starts.  Gutenberg plain text carries no page numbers; page numbers need the Schocken edition (see README).
The texts are local only (~/Desktop/SpaceClaude/local_only_references/Kafka/); kafka_paras.jsonl is local only (gitignored)."""
import json, os, re, sys
import nltk
H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/Kafka')
WORKS = [('trial', 'trial_7849.txt', re.compile(r'^Chapter (One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)$')),
         ('metamorphosis', 'metamorphosis_5200.txt', re.compile(r'^(I|II|III)$'))]
out = []
for work, fn, chap_re in WORKS:
    lines = open(os.path.join(SRC, fn), encoding='utf-8-sig').read().split('\n')
    start = next(i for i, l in enumerate(lines) if 'START OF THE PROJECT GUTENBERG' in l) + 1
    end = next(i for i, l in enumerate(lines) if 'END OF THE PROJECT GUTENBERG' in l)
    chapter = 'front'; para = []; first = None; pn = 0
    def flush():
        global para, first, pn
        if para:
            text = ' '.join(x.strip() for x in para).strip()
            if len(text) > 2 and not chap_re.match(text):
                pn += 1
                out.append({'id': f'{work}-{len(out):05d}', 'work': work, 'chapter': chapter, 'para': pn, 'line': first, 'text': text})
        para, first = [], None
    for i in range(start, end):
        l = lines[i]
        if chap_re.match(l.strip()):
            flush(); chapter = l.strip(); pn = 0; continue
        if not l.strip():
            flush(); continue
        if first is None: first = i + 1
        para.append(l)
    flush()
# sentence split
tok = nltk.data.load('tokenizers/punkt_tab/english.pickle') if False else None
from nltk.tokenize import sent_tokenize
n_s = 0
for p in out:
    p['sentences'] = [s for s in sent_tokenize(p['text']) if s.strip()]
    n_s += len(p['sentences'])
with open(os.path.join(H, 'kafka_paras.jsonl'), 'w') as f:
    for p in out: f.write(json.dumps(p, ensure_ascii=False) + '\n')
import collections
c = collections.Counter((p['work'], p['chapter']) for p in out)
print(len(out), 'paragraphs,', n_s, 'sentences'); print(dict(c))
