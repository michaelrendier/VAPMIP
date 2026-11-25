#!/usr/bin/env python3
"""window16.py -- a 16-word cyclic context window with 15 edges, updatable and addable-to.

  slots     16 = the sedenion basis e0..e15.  Word number k goes into slot k mod 16 and OVERWRITES the oldest word (a cyclic buffer: nothing shifts, so a word keeps its slot).
  edges     15 = the links between consecutive arrivals (the oldest and the newest are not joined).  Each edge is labelled by the XOR of its two slot numbers (1..15):
            the sedenion product index, e_i e_j = ± e_(i xor j), the same labelling the box kite / PG(3,2) uses.  Read in arrival order the labels run
            through the ruler pattern 1,3,1,7,1,3,1,15,1,3,1,7,1,3,1 rotated by the phase (k mod 16).
  evidence  per edge, what WordNet says about the two senses: a named relation among the 19 if one holds directly, else the lowest common hypernym and path similarity.
  scalar    the window as a 16-vector of gamma_radial (the paper's windspeed), slot order: a point in 16 dimensions you can compare, subtract and extend.
  growth    senses come from `UsageStore`: add_synset() mid-stream and the next word that matches it uses it; every push also adds usage counts (the store learns).
"""
import os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H)
import wordnet_boxkite as W
from nltk.corpus import wordnet as wn
from vocab_store import UsageStore, content_lemmas

class Window16:
    def __init__(self, store=None, register=None):
        self.store = store or UsageStore(); self.register = register; self.k = 0
        self.slot = [None] * 16        # each: dict(word, sense, n=arrival number)

    def push(self, word):
        """Add one word.  The sense is chosen against the other words now in the window."""
        lem = word.lower(); ctx = [s['word'] for s in self.slot if s]
        sid, _ = self.store.disambiguate(lem, ctx, self.register)
        i = self.k % 16; self.slot[i] = dict(word=lem, sense=sid, n=self.k); self.k += 1
        if sid:
            e = self.store.lemmas.setdefault(lem, {'n': 0, 'senses': {}}); e['n'] += 1; self.store.n_obs += 1
            h = e['senses'].setdefault(sid, {'n': 0, 'ctx': {}, 'reg': {}}); h['n'] += 1
            for c in ctx: h['ctx'][c] = h['ctx'].get(c, 0) + 1
            if self.register: h['reg'][self.register] = h['reg'].get(self.register, 0) + 1
        return i

    def push_text(self, text):
        for w in content_lemmas(text): self.push(w)

    def order(self):
        """Slots in arrival order, oldest first (only the filled ones)."""
        return sorted((s for s in self.slot if s), key=lambda s: s['n'])

    def _syn(self, sid):
        try: return None if sid is None or sid.startswith('usr:') else wn.synset(sid)
        except Exception: return None

    def edges(self):
        """The (up to) 15 edges between consecutive arrivals: slot pair, XOR label, relation evidence."""
        o = self.order(); out = []
        for a, b in zip(o, o[1:]):
            ia, ib = a['n'] % 16, b['n'] % 16; sa, sb = self._syn(a['sense']), self._syn(b['sense']); rel = None; lch = None; sim = None
            if sa and sb:
                for m in W.RELATION_METHODS:
                    try:
                        if sb in getattr(sa, m)(): rel = m; break
                    except Exception: pass
                if sa == sb: rel = 'same synset'
                try:
                    c = sa.lowest_common_hypernyms(sb); lch = c[0].name() if c else None; sim = sa.path_similarity(sb)
                except Exception: pass
            elif (a['sense'] or '').startswith('usr:') or (b['sense'] or '').startswith('usr:'): rel = 'user-defined sense'
            out.append(dict(a=a['word'], b=b['word'], slots=(ia, ib), label=ia ^ ib, relation=rel, common_hypernym=lch, path_similarity=None if sim is None else round(sim, 3)))
        return out

    def vector(self):
        """16-vector of gamma_radial by slot (0 where empty or undefined)."""
        v = np.zeros(16)
        for i, s in enumerate(self.slot):
            if s and s['sense']:
                g = W.gamma_radial(self.store.vector_of(s['sense'])); v[i] = 0.0 if g is None else g
        return v
