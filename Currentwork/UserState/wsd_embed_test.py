#!/usr/bin/env python3
"""wsd_embed_test.py -- disambiguation, both ways (Cody 2026-11-24: 'do both').
  (1) sentence-embedding: all-MiniLM-L6-v2 (local copy): cos(sentence embedding, embedding of '<lemma>: <gloss>') per candidate sense
  (2) usage-learned: the vocab_store co-occurrence memory trained on confirmed senses from DISJOINT SemCor sentences (as in V3)
  (3) both + rank prior, weights fitted on a validation slice (never on the test slice)
SemCor gold; same 800 test sentences and ambiguous tokens as V3.  Expectation written first: embedding alone beats gloss-overlap (0.464) and approaches/exceeds the
rank-first baseline (0.518 here); the combination beats either alone.  Writes out/WSD_EMBED_REPORT.md.  Seeded."""
import collections, json, math, os, random, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H)
os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TOKENIZERS_PARALLELISM'] = 'false'
from vocab_store import UsageStore
from nltk.corpus import wordnet as wn, semcor
from nltk.tree import Tree
from user_state import BC
random.seed(5)
from sentence_transformers import SentenceTransformer
M = SentenceTransformer(os.path.expanduser('~/Desktop/SpaceClaude/local_only_references/models/all-MiniLM-L6-v2'), device='cpu')
items = []
for f in semcor.fileids()[:60]:
    for sent in semcor.tagged_sents(f, tag='sem'):
        toks = [(ch.label().name().lower(), ch.label().synset().name()) for ch in sent if isinstance(ch, Tree) and hasattr(ch.label(), 'synset')]
        if len(toks) >= 4: items.append((' '.join(w for w in sent.leaves() if isinstance(w, str)) if hasattr(sent, 'leaves') else '', toks))
random.shuffle(items); tr, te, va = items[:4000], items[4000:4800], items[4800:5099]
def surface(sent):  # SemCor leaves are lists of words; rebuild a readable sentence
    return ' '.join(w for w in (sent if isinstance(sent, list) else sent.leaves()))
# need surface text: re-read the same sentences keyed by position is awkward; rebuild from lemma tokens (content words) instead: context = the content lemmas joined
def ctx_text(toks): return ' '.join(l.replace('_', ' ') for l, _ in toks)
st = UsageStore(); cache = {}
def gloss_vec(sid, lemma):
    k = (sid, lemma)
    if k not in cache:
        s = wn.synset(sid); cache[k] = M.encode(f'{lemma.replace("_", " ")}: {s.definition()}', normalize_embeddings=True)
    return cache[k]
def build_features(data):
    rows = []
    for toks, in ((t,) for _, t in data):
        e = M.encode(ctx_text(toks), normalize_embeddings=True); lems = [l for l, _ in toks]
        for i, (l, gold) in enumerate(toks):
            ss = st.senses_of(l)
            if len(ss) < 2: continue
            ctx = lems[:i] + lems[i + 1:]; _, sc = st.disambiguate(l, ctx, None, w=(0, 0, 0.5, 1.0, 0))      # usage part only (needs the trained store)
            for rank, (sid, g, r) in enumerate(ss):
                if sid.startswith('usr:'): continue
                rows.append((id(toks), i, sid, gold, 1.0 / (1 + r), float(e @ gloss_vec(sid, l)), sc.get(sid, 0.0)))
    return rows
# train the usage memory on confirmed senses (disjoint)
for _, toks in tr:
    lems = [l for l, _ in toks]
    for i, (l, gold) in enumerate(toks):
        e = st.lemmas.setdefault(l, {'n': 0, 'senses': {}}); e['n'] += 1; st.n_obs += 1
        h = e['senses'].setdefault(gold, {'n': 0, 'ctx': {}, 'reg': {}}); h['n'] += 1
        for c in lems[:i] + lems[i + 1:]: h['ctx'][c] = h['ctx'].get(c, 0) + 1
print('features: validation', flush=True); Fv = build_features(va); print('features: test', flush=True); Ft = build_features(te)
def acc(F, w):
    by = collections.defaultdict(list)
    for r in F: by[(r[0], r[1])].append(r)
    ok = 0
    for k, c in by.items():
        best = max(c, key=lambda r: w[0] * r[4] + w[1] * r[5] + w[2] * r[6]); ok += best[2] == best[3]
    return ok / len(by), len(by)
grid = [(a, b, c) for a in (0, .5, 1, 2) for b in (0, .5, 1, 2, 4) for c in (0, .5, 1, 2)]
fit = max((g for g in grid if any(g)), key=lambda g: acc(Fv, g)[0])
rows = [('rank prior only (first sense)', (1, 0, 0)), ('embedding only', (0, 1, 0)), ('usage memory only', (0, 0, 1)), ('rank + embedding', (1, 1, 0)), ('rank + usage', (1, 0, 1)), (f'all three, weights fitted on validation {fit}', fit)]
out = ['# Disambiguation, both ways (SemCor gold senses)', '', f'train (confirmed senses for the usage memory) {len(tr)} sentences, validation {len(va)}, test {len(te)}. Embedding = all-MiniLM-L6-v2, context = the sentence\'s tagged content lemmas, sense = "<lemma>: <WordNet gloss>".', '', '| method | test accuracy | ambiguous tokens |', '|---|---|---|']
res = {}
for n, w in rows:
    a, k = acc(Ft, w); res[n] = a; out.append(f'| {n} | {a:.3f} | {k} |')
open(os.path.join(H, 'out', 'WSD_EMBED_REPORT.md'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
