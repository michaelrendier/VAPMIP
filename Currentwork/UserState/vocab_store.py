#!/usr/bin/env python3
"""vocab_store.py -- the user's VOCABULARY AS USAGE: a store Cody (and, later, the Monad) can add to.

Cody, 2026-11-24: nuance is which senses of a word go together, when; "run" and "set" have hundreds of uses; how many of them a speaker commands
(and which they leave out) shows the depth of their reading; an education is stored in a vocabulary; the kitchen register differs from the coding register;
synsets must be addable on the fly and gain usage over time.

What it keeps, per lemma:  per SENSE (a WordNet synset name, or a custom synset `usr:<lemma>:<k>` the user adds): how many times it was used, the lemmas it
co-occurred with (the nuance: which senses go with which company), and the registers it was used in (kitchen, coding, chat ...).
Disambiguation = rank prior + gloss/example overlap with the sentence + THIS USER'S OWN co-occurrence history for that sense + register match.
A custom synset carries relations the user names (hypernyms ...), so it gets a real 19-vector and a `gamma_radial` like any WordNet synset (wordnet_boxkite).

Everything is additive counts (order of observation does not matter); JSON on disk.
"""
import collections, json, math, os, re, sys, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..'))
import wordnet_boxkite as W
from nltk.corpus import wordnet as wn, stopwords, brown
from nltk.stem import WordNetLemmatizer
STOP = set(stopwords.words('english')) | {"don't", "it's", "i'm", "that's", "you're", "i've", "can't", "didn't", "isn't", "doesn't", "won't"}
LEM = WordNetLemmatizer()
TOK = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
WNPOS = {'n': wn.NOUN, 'v': wn.VERB, 'a': wn.ADJ, 'r': wn.ADV}
_RANK = None
def brown_rank():
    """lemma -> frequency rank in the Brown corpus (1 = most common): the 'common words' reference for rarity and for absence."""
    global _RANK
    if _RANK is None:
        c = collections.Counter(w.lower() for w in brown.words() if w.isalpha())
        _RANK = {w: i + 1 for i, (w, _) in enumerate(c.most_common())}
    return _RANK

_BC = None
def brown_counts():
    """lemma -> Brown count and the total: the general-English prior the user's own usage is mixed into."""
    global _BC
    if _BC is None:
        c = collections.Counter(w.lower() for w in brown.words() if w.isalpha()); _BC = (c, sum(c.values()))
    return _BC

def sentences(text): return [s.strip() for s in re.split(r'(?<=[.?!])\s+|\.\.\.+|\n+', text) if len(s.strip()) > 2]
def content_lemmas(sent):
    out = []
    for w in TOK.findall(sent):
        lw = w.lower()
        if lw in STOP or len(lw) < 3 or any(c.isdigit() for c in lw): continue      # numbers are not words (numeric.py): no digit token is ever a lemma
        out.append(lw)
    return out

class UsageStore:
    def __init__(self):
        self.lemmas = {}      # lemma -> {'n': int, 'senses': {sid: {'n': int, 'ctx': {lemma: int}, 'reg': {name: int}}}}
        self.custom = {}      # sid -> {lemma, pos, gloss, examples, relations, register, created, vec}
        self.n_obs = 0; self.n_sent = 0

    # ───────── adding vocabulary ─────────
    def add_synset(self, lemma, gloss, pos='n', relations=None, register=None, examples=()):
        """Add a sense on the fly.  relations = {'hypernyms': [synset-name or lemma, ...], ...}: names from W.RELATION_METHODS; counts become the 19-vector."""
        lemma = lemma.lower(); k = 1 + sum(1 for s in self.custom.values() if s['lemma'] == lemma); sid = f'usr:{lemma}:{k}'
        rel = {m: list(t) for m, t in (relations or {}).items() if m in W.RELATION_METHODS}
        vec = [W.compress_count(len(rel.get(m, []))) for m in W.RELATION_METHODS]
        self.custom[sid] = dict(lemma=lemma, pos=pos, gloss=gloss, examples=list(examples), relations=rel, register=register, created=time.time(), vec=vec)
        self.lemmas.setdefault(lemma, {'n': 0, 'senses': {}}); return sid

    def senses_of(self, lemma):
        """[(sid, gloss tokens, rank)]: custom senses first (the user's own meaning wins ties), then WordNet in its own order."""
        out = [(sid, set(content_lemmas(c['gloss'] + ' ' + ' '.join(c['examples']))), -1) for sid, c in self.custom.items() if c['lemma'] == lemma]
        seen = set()
        for pos in ('n', 'v', 'a', 'r'):
            for s in wn.synsets(LEM.lemmatize(lemma, pos), WNPOS[pos]):
                if s.name() in seen: continue
                seen.add(s.name()); g = set(content_lemmas(s.definition() + ' ' + ' '.join(s.examples()))); out.append((s.name(), g, len(seen) - 1))
        return out

    def vector_of(self, sid):
        if sid in self.custom: return self.custom[sid]['vec']
        return W.context_vector(wn.synset(sid))

    # ───────── reading ─────────
    def disambiguate(self, lemma, ctx, register=None, w=(1.0, 1.0, 0.5, 1.0, 0.8)):
        """Score every sense: rank prior, gloss overlap, this user's co-occurrence for the sense, the sense's own register history, custom bonus.  Returns (sid, scores)."""
        ss = self.senses_of(lemma)
        if not ss: return None, {}
        hist = self.lemmas.get(lemma, {}).get('senses', {}); ctx = set(ctx) - {lemma}; sc = {}
        tot = sum(h['n'] for h in hist.values()) or 1
        for sid, g, rank in ss:
            h = hist.get(sid, {'n': 0, 'ctx': {}, 'reg': {}})
            prior = 0.5 if rank < 0 else 1.0 / (1 + rank)        # a custom sense must earn its place by context or register
            gl = len(g & ctx) / (1 + math.sqrt(len(g)))
            us = sum(h['ctx'].get(c, 0) for c in ctx) / (1.0 + h['n']) if h['n'] else 0.0
            fam = h['n'] / tot
            reg = (h['reg'].get(register, 0) / (1.0 + h['n'])) if (register and h['n']) else 0.0
            cust = 1.0 if (sid in self.custom and (register is None or self.custom[sid]['register'] in (None, register))) and (len(g & ctx) or reg) else 0.0
            sc[sid] = w[0] * prior + w[1] * gl + w[2] * us + w[3] * reg + w[4] * cust + 0.3 * fam
        return max(sc, key=sc.get), sc

    def observe(self, text, register=None, gold=None):
        """Read a text: per sentence, disambiguate each content lemma, then add the counts.  gold = {lemma: sid} confirms a sense (the user said which one)."""
        for sent in sentences(text):
            ls = content_lemmas(sent); self.n_sent += 1
            for i, lem in enumerate(ls):
                ctx = ls[:i] + ls[i + 1:]
                sid = (gold or {}).get(lem) or self.disambiguate(lem, ctx, register)[0]
                if not sid: continue
                e = self.lemmas.setdefault(lem, {'n': 0, 'senses': {}}); e['n'] += 1; self.n_obs += 1
                h = e['senses'].setdefault(sid, {'n': 0, 'ctx': {}, 'reg': {}}); h['n'] += 1
                for c in ctx: h['ctx'][c] = h['ctx'].get(c, 0) + 1
                if register: h['reg'][register] = h['reg'].get(register, 0) + 1

    # ───────── usage as probability (2026-11-25) ─────────
    def confidence(self, K: float = 200.0) -> float:
        """How much of the mix is this user's own usage: lambda = N/(N+K), N = tokens counted. 0 on a cold store, 1 as it grows."""
        return self.n_obs / (self.n_obs + K)

    def p_word(self, lemma: str, K: float = 200.0) -> float:
        """P(lemma) = lambda * (user count + 0.5)/(N + 0.5 V_user) + (1 - lambda) * Brown(lemma): the usage field as the probability, backed off to general English
        while the store is young. Never 0 (Brown smoothing). Compression reading: -log2 p_word is the bits this word costs a reader who knows this user."""
        bc, bt = brown_counts(); lam = self.confidence(K); lem = lemma.lower()
        pb = (bc.get(lem, 0) + 0.5) / (bt + 0.5 * len(bc))
        n = self.lemmas.get(lem, {}).get('n', 0); V = max(1, len(self.lemmas))
        pu = (n + 0.5) / (self.n_obs + 0.5 * V)
        return lam * pu + (1.0 - lam) * pb

    # ───────── depth, and what is NOT used ─────────
    def profile(self):
        """Vocabulary depth from usage: polysemy of the words commanded, rarity, breadth of senses actually used, word length."""
        rk = brown_rank(); tok = poly = rare = ln = 0; breadth = []
        for lem, e in self.lemmas.items():
            n = e['n']
            if not n: continue
            p = max(1, len(wn.synsets(lem))); tok += n; poly += n * math.log(p); rare += n * (rk.get(lem, 10 ** 6) > 5000); ln += n * len(lem)
            if n >= 3: breadth.append(len(e['senses']))
        return dict(tokens=tok, lemmas=sum(1 for e in self.lemmas.values() if e['n']), mean_log_polysemy=poly / max(tok, 1), rare_rate=rare / max(tok, 1),
                    mean_word_len=ln / max(tok, 1), mean_senses_used=(sum(breadth) / len(breadth)) if breadth else 0.0, custom_synsets=len(self.custom))

    def absent(self, reference_lemmas, top=20):
        """The words the reference register commands that this user has not used (the words NOT chosen)."""
        return [l for l in reference_lemmas if self.lemmas.get(l, {}).get('n', 0) == 0][:top]

    # ───────── disk ─────────
    def save(self, path): json.dump(dict(lemmas=self.lemmas, custom=self.custom, n_obs=self.n_obs, n_sent=self.n_sent), open(path, 'w'))
    @classmethod
    def load(cls, path):
        j = json.load(open(path)); s = cls(); s.lemmas, s.custom, s.n_obs, s.n_sent = j['lemmas'], j['custom'], j['n_obs'], j['n_sent']; return s
