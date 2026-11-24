#!/usr/bin/env python3
"""read_context.py -- read a text the way ScalarContextPropagation (v4.0) reads a word, and lift it to a sentence and a whole text.  NO training, NO model.

THE MECHANISM (all from VAPMIP/wordnet_boxkite.py, the shipped functions; paper §5-§9):
  word -> synset (WordNet sense)
       -> 19 relation counts   (`context_vector`: hypernyms, hyponyms, meronyms ... usage_domains; each count log2-compressed)
       -> one integer address  (`context_code` = prod CONTEXT_PRIMES[i]^v[i]; exactly recoverable)
       -> one real             (`gamma_radial` = tanh(0.5 ln(log_code / LOG_ANCHOR)); the paper's Gamma-Radial Windspeed; ~ -1 sparse/specific, ~ 0 rich)
WHAT IS ADDED HERE (mine, NOT in the paper; the paper gives the word-level scalar, and says the sentence constructor does not yet use it):
  sentence field  = the SUM of its content words' 19-vectors (additive, like the solution model); its gamma is `gamma_radial(sum)`.
  semantic field  = the lexicographer file of the sense (noun.feeling, noun.communication, verb.emotion, ...): which part of the world the word is about.
  recurrence      = the same lemma/synset returning across the text (the structure behind "keep", "again", "N times").
  emotion anchors = the hypernym closure of a word's senses reaches an anchor synset (anger.n.01, fear.n.01 ...) -> that emotion's recipe row (TABLE in solution_tests.py).
Known limits: sense = rank-ordered WordNet senses (no disambiguation yet); closed-class words are skipped; irony, aim ("stupid" aimed at whom) and negation are invisible here.

    .venv/bin/python Currentwork/UserState/read_context.py FILE.md [--sentences]
"""
import collections, math, os, re, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(H, '..', '..'); sys.path.insert(0, V); sys.path.insert(0, H)
import wordnet_boxkite as W
from nltk.corpus import wordnet as wn, stopwords
from nltk.stem import WordNetLemmatizer
STOP = set(stopwords.words('english')) | {"i'm", "don't", "it's", "i'd", "that's", "you're", "i've", "can't", "didn't", "isn't", "doesn't", "won't", "don", "re", "ve", "ll"}
LEM = WordNetLemmatizer()
TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")

# emotion name (a GoEmotions label, = a row of the recipe table) -> anchor synsets in WordNet's own tree
ANCHORS = {'anger': ['anger.n.01', 'angriness.n.01'], 'annoyance': ['annoyance.n.01', 'irritation.n.01'], 'disgust': ['disgust.n.01'], 'fear': ['fear.n.01'],
           'nervousness': ['nervousness.n.01', 'anxiety.n.02'], 'sadness': ['sadness.n.01'], 'grief': ['grief.n.01'], 'disappointment': ['disappointment.n.01'],
           'remorse': ['remorse.n.01', 'guilt.n.01'], 'embarrassment': ['embarrassment.n.01'], 'joy': ['joy.n.01', 'happiness.n.01'], 'amusement': ['amusement.n.01'],
           'love': ['love.n.01', 'love.n.02'], 'caring': ['caring.n.01', 'care.n.01'], 'gratitude': ['gratitude.n.01'], 'admiration': ['admiration.n.01'],
           'pride': ['pride.n.01'], 'optimism': ['optimism.n.01', 'hope.n.01'], 'relief': ['relief.n.01'], 'excitement': ['excitement.n.01'],
           'curiosity': ['curiosity.n.01'], 'surprise': ['surprise.n.01'], 'confusion': ['confusion.n.01', 'perplexity.n.01'], 'desire': ['desire.n.01'],
           'approval': ['approval.n.01'], 'disapproval': ['disapproval.n.01'], 'realization': ['realization.n.01']}
ANCH = {}
for emo, names in ANCHORS.items():
    for n in names:
        try: ANCH.setdefault(wn.synset(n), emo)
        except Exception: pass
EMO_LEX = {'noun.feeling', 'noun.motive', 'verb.emotion', 'adj.all'}   # adj.all is every adjective: only used with an anchor hit below

def content_senses(word, k=3):
    """Lemmatise, take up to k rank-ordered senses over noun/verb/adj/adv."""
    out = []
    for pos in ('n', 'v', 'a', 'r'):
        lem = LEM.lemmatize(word.lower(), pos)
        ss = wn.synsets(lem, pos if pos != 'a' else wn.ADJ)
        if ss: out.append((lem, ss[:k]))
    return out

def emotion_hits(word):
    """{emotion: weight}.  A sense's hypernym closure containing an anchor is a hit, weight 1/(1+rank).  Adjectives and verbs go through their derivationally related nouns (angry -> anger)."""
    hits = collections.Counter()
    for pos in ('n', 'v', 'a'):
        lem = LEM.lemmatize(word.lower(), pos)
        for rank, s in enumerate(wn.synsets(lem, pos if pos != 'a' else wn.ADJ)[:4]):
            cands = [s]
            for l in s.lemmas():
                cands += [d.synset() for d in l.derivationally_related_forms() if d.synset().pos() == 'n']
            for c in cands:
                if c.pos() != 'n': continue
                for h in set(c.closure(lambda x: x.hypernyms())) | {c}:
                    if h in ANCH: hits[ANCH[h]] += 1.0 / (1 + rank); break
    return hits

def read_sentence(sent):
    words = [w for w in TOK.findall(sent) if w.lower() not in STOP and len(w) > 2]
    rec = []; field = np.zeros(19)
    for w in words:
        cs = content_senses(w, 1)
        if not cs: continue
        lem, ss = cs[0]; s = ss[0]; v = W.context_vector(s); field += v
        rec.append(dict(word=w, lemma=lem, synset=s.name(), lex=s.lexname(), v=v, gamma=W.gamma_radial(v), polysemy=len(wn.synsets(lem)), emo=dict(emotion_hits(w))))
    return rec, field

def read_text(text):
    sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+|\.\.\.+', text) if len(s.strip()) > 3]
    return [(s,) + read_sentence(s) for s in sents]

if __name__ == '__main__':
    text = open(sys.argv[1]).read().strip(); R = read_text(text)
    lex = collections.Counter(); lem = collections.Counter(); emo = collections.Counter(); gam = []
    for s, rec, f in R:
        for r in rec:
            lex[r['lex']] += 1; lem[r['lemma']] += 1; gam.append(r['gamma'] if r['gamma'] is not None else 0.0)
            for e, w in r['emo'].items(): emo[e] += w
    print(f'{len(R)} sentences, {sum(len(r) for _, r, _ in R)} content words with a sense')
    print('SEMANTIC FIELDS:', ', '.join(f'{k} {v}' for k, v in lex.most_common(12)))
    print('RECURRENCE (lemma x count):', ', '.join(f'{k} {v}' for k, v in lem.most_common(25)))
    print('EMOTION ANCHORS reached (weighted):', ', '.join(f'{k} {v:.1f}' for k, v in emo.most_common(14)))
    g = np.array(gam); print(f'gamma_radial per word: mean {g.mean():+.2f}, sd {g.std():.2f}; sparse (< -0.8) {int((g < -0.8).sum())}, rich (> -0.3) {int((g > -0.3).sum())}')
