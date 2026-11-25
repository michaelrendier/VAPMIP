#!/usr/bin/env python3
"""vocab_tests.py -- tests of the usage store (vocab_store.py).  Expectations were written BEFORE running:

  V1  additive store: save/load is exact; with senses given (gold) the counts do not depend on the order of observation.
  V2  on-the-fly synset: a user-added sense ('86' = remove an item from the menu) wins in its own register and context, loses in another ('page 86'),
      gains usage counts, and has a real 19-vector and gamma_radial.
  V3  disambiguation on SemCor (gold senses): rank-first baseline ~0.65; gloss overlap alone is NOT expected to beat it; a store that has seen
      other text with confirmed senses (the user's usage) IS expected to beat the baseline.  Reported either way.
  V4  vocabulary depth orders registers: nps_chat (casual) < goemotions (Reddit) < Cody's chat < the ScalarContextPropagation paper, on mean log polysemy and
      rare-word rate; textstat grade as the outside reference.  Ordinal ground truth only (source), so this is a screening test, not a calibration.
Writes out/VOCAB_TESTS_REPORT.md.  Seeded."""
import collections, json, math, os, random, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H)
from vocab_store import UsageStore, content_lemmas, sentences, brown_rank
import wordnet_boxkite as W
from user_state import BC
from nltk.corpus import wordnet as wn
REP = []
def say(*a):
    s = '\n'.join(str(x) for x in a); print(s, flush=True); REP.append(s)
random.seed(5)

def v1():
    say('## V1  additive store, exact round trip', '')
    t = ['the chef will run the kitchen tonight', 'run a mile before the service', 'set the table and set the clock']
    g = {'run': 'run.v.01', 'set': 'set.v.01'}
    a = UsageStore(); [a.observe(x, 'kitchen', gold=g) for x in t]
    b = UsageStore(); [b.observe(x, 'kitchen', gold=g) for x in reversed(t)]
    p = '/tmp/claude-1000/vstore.json'; a.save(p); c = UsageStore.load(p)
    same_order = a.lemmas == b.lemmas; same_disk = a.lemmas == c.lemmas and a.custom == c.custom
    say(f'order-independent with gold senses: **{same_order}**   ·   disk round trip exact: **{same_disk}**   ·   {a.n_obs} observations, {len(a.lemmas)} lemmas', '')
    return same_order and same_disk

def v2():
    say('## V2  a synset added on the fly', '')
    s = UsageStore()
    sid = s.add_synset('86', 'remove an item from the menu because the kitchen has run out of it', 'v', relations={'hypernyms': ['remove.v.01'], 'also_sees': ['out.r.01']},
                       register='kitchen', examples=['we are out of salmon so eighty six the salmon'])
    v = s.vector_of(sid); g = W.gamma_radial(v)
    k = s.disambiguate('86', content_lemmas('86 the salmon chef we are out'), 'kitchen')[0]
    o = s.disambiguate('86', content_lemmas('turn to page 86 of the book'), 'coding')[0]
    for _ in range(3): s.observe('86 the salmon, chef, we are out', 'kitchen')
    used = s.lemmas['86']['senses'].get(sid, {}).get('n', 0)
    say(f'sense id {sid}; 19-vector nonzero at {[W.RELATION_METHODS[i] for i, x in enumerate(v) if x]}; gamma_radial {g:+.3f}', f'kitchen context chooses: `{k}`   ·   "page 86" in coding context chooses: `{o}`   ·   usage count after 3 kitchen sentences: {used}', '')
    ok = k == sid and o != sid and used == 3 and g is not None
    say(f'**{"PASS" if ok else "FAIL"}**', ''); return ok

def v3():
    say('## V3  disambiguation on SemCor (gold senses)', '')
    from nltk.corpus import semcor
    from nltk.tree import Tree
    files = semcor.fileids()[:60]; items = []
    for f in files:
        for sent in semcor.tagged_sents(f, tag='sem'):
            toks = []
            for ch in sent:
                if isinstance(ch, Tree) and hasattr(ch.label(), 'synset'):
                    lab = ch.label(); toks.append((lab.name().lower(), lab.synset().name()))
            if len(toks) >= 4: items.append([(l, s) for l, s in toks])
    random.shuffle(items); tr, te = items[:4000], items[4000:4800]
    say(f'{len(items)} usable SemCor sentences; train (confirmed senses) {len(tr)}, test {len(te)}', '')
    def evalu(store, mode):
        ok = n = 0
        for sent in te:
            lems = [l for l, _ in sent]
            for i, (l, gold) in enumerate(sent):
                ss = store.senses_of(l)
                if len(ss) < 2: continue
                if mode == 'first': pred = ss[0][0] if ss[0][2] >= 0 else ss[0][0]
                else: pred = store.disambiguate(l, lems[:i] + lems[i + 1:], None, w=MODE_W[mode])[0]
                ok += pred == gold; n += 1
        return ok / n, n
    MODE_W = {'gloss only': (0.0, 1.0, 0, 0, 0), 'prior+gloss': (1.0, 1.0, 0, 0, 0), 'prior+gloss+usage': (1.0, 1.0, 0.5, 1.0, 0.8)}
    empty = UsageStore(); res = {}
    res['rank-first baseline'] = evalu(empty, 'first'); res['gloss overlap only'] = evalu(empty, 'gloss only'); res['rank prior + gloss'] = evalu(empty, 'prior+gloss')
    st = UsageStore()
    for sent in tr:
        for i, (l, gold) in enumerate(sent):
            st.observe(' '.join(x for x, _ in sent), None, gold={l: gold}) if False else None
    # confirmed-sense training: per sentence, observe all tokens with their gold sense
    st = UsageStore()
    for sent in tr:
        lems = [l for l, _ in sent]
        for i, (l, gold) in enumerate(sent):
            e = st.lemmas.setdefault(l, {'n': 0, 'senses': {}}); e['n'] += 1; st.n_obs += 1
            h = e['senses'].setdefault(gold, {'n': 0, 'ctx': {}, 'reg': {}}); h['n'] += 1
            for c in lems[:i] + lems[i + 1:]: h['ctx'][c] = h['ctx'].get(c, 0) + 1
    res['rank prior + gloss + this store\'s usage'] = evalu(st, 'prior+gloss+usage')
    say('| method | accuracy | ambiguous tokens |', '|---|---|---|')
    for k, (a, n) in res.items(): say(f'| {k} | {a:.3f} | {n} |')
    base = res['rank-first baseline'][0]; best = res['rank prior + gloss + this store\'s usage'][0]
    say('', f'usage store minus rank-first baseline: {best - base:+.3f}', ''); return best > base

def v4():
    say('## V4  vocabulary depth by register', '')
    import textstat
    rk = brown_rank(); rows = [json.loads(l) for l in open(os.path.join(H, 'corpus.jsonl'))]
    src = {k: [r['text'] for r in rows if r['source'] == k] for k in ('nps_chat', 'goemotions', 'proj_chat', 'proj_novel')}
    paper = open(os.path.join(H, '..', '..', 'FourthAgePaper', 'ScalarContextPropagation', '19_Dimensional_Scalar_WordNet_Context_Propagation_v4.0.md')).read()
    src['ScalarContext paper'] = [p for p in paper.split('\n\n') if len(p.split()) >= 25 and not p.lstrip().startswith(('```', '|', '    '))]
    def feats(t):
        ls = content_lemmas(t)
        if len(ls) < 5: return None
        return (np.mean([math.log(max(1, len(wn.synsets(l)))) for l in ls]), np.mean([rk.get(l, 10 ** 6) > 5000 for l in ls]), np.mean([len(l) for l in ls]))
    say('| register | texts | mean log polysemy [95% CI] | rare-word rate [95% CI] | word length | FK grade |', '|---|---|---|---|---|---|')
    mp = {}
    for k, t in src.items():
        t = random.sample(t, min(400, len(t))); F = [f for f in map(feats, t) if f]
        a = [f[0] for f in F]; b = [f[1] for f in F]; c = [f[2] for f in F]
        ca = BC.bootstrap_ci(a, n_boot=1000)['ci']; cb = BC.bootstrap_ci(b, n_boot=1000)['ci']
        fk = np.mean([textstat.flesch_kincaid_grade(x) for x in t]); mp[k] = (np.mean(a), np.mean(b))
        say(f'| {k} | {len(F)} | {np.mean(a):.3f} [{ca[0]:.3f}, {ca[1]:.3f}] | {np.mean(b):.3f} [{cb[0]:.3f}, {cb[1]:.3f}] | {np.mean(c):.2f} | {fk:.1f} |')
    order = ['nps_chat', 'goemotions', 'proj_chat', 'ScalarContext paper']
    mono_p = all(mp[order[i]][0] <= mp[order[i + 1]][0] for i in range(3)); mono_r = all(mp[order[i]][1] <= mp[order[i + 1]][1] for i in range(3))
    say('', f'ordering nps_chat < goemotions < proj_chat < paper holds on polysemy: **{mono_p}**, on rare-word rate: **{mono_r}**', ''); return mono_p, mono_r

if __name__ == '__main__' and 'v4b' not in sys.argv:
    r = {'v1': v1(), 'v2': v2()}; r['v3'] = v3(); r['v4'] = v4()
    open(os.path.join(H, 'out', 'VOCAB_TESTS_REPORT.md'), 'w').write('# Vocabulary store tests (V1-V4)\n\n' + '\n'.join(REP) + '\n')
    print(r)

# ───────── V4b: retooled after V4 failed (tiny samples; mean polysemy falls with rarity, so it cannot be the depth metric) ─────────
def sense_count(sid, lemma):
    try:
        s = wn.synset(sid)
        for l in s.lemmas():
            if l.name().lower() == lemma: return l.count()
        return min((l.count() for l in s.lemmas()), default=0)
    except Exception: return 0
def v4b():
    """Depth = which senses of the HIGHLY POLYSEMOUS common words a speaker commands, not the average polysemy.  Chunks of ~40 words so every register has n.
       tail   = share of tokens, among lemmas with >= 8 senses, that the (history-free) reader puts on a non-first sense
       famil  = mean log(1 + SemCor count of the chosen sense) over those tokens (lower = rarer, deeper sense)
       Expected order (Cody's claim): nps_chat < goemotions < Cody's chat < paper, lower famil going up."""
    say('## V4b  sense-tail depth (retooled)', '')
    rk = brown_rank(); rows = [json.loads(l) for l in open(os.path.join(H, 'corpus.jsonl'))]; st = UsageStore()
    def chunks(texts, size=40):
        words = ' '.join(texts).split(); return [' '.join(words[i:i + size]) for i in range(0, len(words) - size, size)]
    src = {'nps_chat': chunks([r['text'] for r in rows if r['source'] == 'nps_chat']), 'goemotions': chunks([r['text'] for r in rows if r['source'] == 'goemotions'][:1500])}
    src['Cody (dark-prompt.md)'] = chunks([open(os.path.join(H, 'dark-prompt.md')).read()])
    paper = open(os.path.join(H, '..', '..', 'FourthAgePaper', 'ScalarContextPropagation', '19_Dimensional_Scalar_WordNet_Context_Propagation_v4.0.md')).read()
    src['ScalarContext paper'] = chunks([p for p in paper.split('\n\n') if not p.lstrip().startswith(('```', '|', '    ', '#'))])
    kaf = [json.loads(l)['text'] for l in open(os.path.join(H, 'kafka_paras.jsonl'))]; src['Kafka (Wyllie)'] = chunks(kaf)
    def feats(t):
        ls = content_lemmas(t); tail = []; fam = []; poly = []
        for i, l in enumerate(ls):
            ss = st.senses_of(l)
            if len(ss) < 8: continue
            sid = st.disambiguate(l, ls[:i] + ls[i + 1:])[0]; tail.append(sid != ss[0][0]); fam.append(math.log(1 + sense_count(sid, l))); poly.append(math.log(len(ss)))
        if len(tail) < 4: return None
        return np.mean(tail), np.mean(fam), np.mean(poly), np.mean([len(l) for l in ls])
    say('| register | chunks | non-first-sense share [95% CI] | sense familiarity (log count) [95% CI] | log polysemy of the words used | word length |', '|---|---|---|---|---|---|')
    M = {}
    for k, t in src.items():
        t = random.sample(t, min(150, len(t))); F = [f for f in map(feats, t) if f]
        if len(F) < 5: say(f'| {k} | {len(F)} | too few | | | |'); continue
        a = [f[0] for f in F]; b = [f[1] for f in F]; ca = BC.bootstrap_ci(a, n_boot=1000)['ci']; cb = BC.bootstrap_ci(b, n_boot=1000)['ci']
        M[k] = (np.mean(a), np.mean(b)); say(f'| {k} | {len(F)} | {np.mean(a):.3f} [{ca[0]:.3f}, {ca[1]:.3f}] | {np.mean(b):.3f} [{cb[0]:.3f}, {cb[1]:.3f}] | {np.mean([f[2] for f in F]):.2f} | {np.mean([f[3] for f in F]):.2f} |')
    o = [k for k in ('nps_chat', 'goemotions', 'Cody (dark-prompt.md)', 'ScalarContext paper') if k in M]
    mt = all(M[o[i]][0] <= M[o[i + 1]][0] for i in range(len(o) - 1)); mf = all(M[o[i]][1] >= M[o[i + 1]][1] for i in range(len(o) - 1))
    say('', f'ordering holds on non-first-sense share: **{mt}**; on sense familiarity falling: **{mf}**', ''); return mt, mf

if __name__ == '__main__' and 'v4b' in sys.argv:
    r = v4b(); open(os.path.join(H, 'out', 'VOCAB_TESTS_REPORT.md'), 'a').write('\n'.join(REP) + '\n'); print(r)
