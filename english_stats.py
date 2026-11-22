#!/usr/bin/env python3
"""
english_stats.py -- actual English usage, as ONE data object: a poll of the current values.

Cody, 2026-11-21: "it's about time to get to English statistics. Actual usage. They don't have to be live, just available when the
pathways are running." Two requirements: (1) a single data class, a poll of the current values; granularities defined by the assumed
educational response desire. (2) phonetics left out: this is "what number did they end up at" under the Scalar Context Propagation
hash, and nothing about sound.

WHAT IT HOLDS (EnglishStats, a dataclass)
    word counts           unigram, ordered-pair (bigram) counts, and the count of each context     (frequency: what the
                          A-matrix cannot hold, because it merges by max: bench of 2026-11-21, learning_curve.txt)
    context-class counts  the same, keyed by the word's Scalar Boxkite context class (the final number the hash lands on for the
                          word's first WordNet sense): class-to-class pairs, and which words sit in each class
    levels                the educational response desire as a vocabulary rank cut: child / general / college / specialist
THE PREDICTION  P(w | prev) is a three-part mixture, each part a probability distribution over the vocabulary:
    P = a*P_word(w|prev)  +  b*P_class(class(w)|class(prev)) * P(w|class(w))  +  c*P_unigram(w)
    A word beyond the chosen level's rank cut loses the word-pair part (it is spoken from its class only): that is the granularity.
    `granularity` 'word' | 'class' | 'basin' says how coarse the class part is (exact class: 1,276; density basin: 15; attractor: 171).
THE POLL  `poll()` returns plain values (tokens, vocabulary, classes seen, level sizes, the top words): the single object a pathway
    reads. `level_for(text)` infers the level from how rare the user's own words are (the assumed educational response desire).
Needs NLTK WordNet only to find the first sense of a word; the class numbers come from map/scalar_context_map.tsv.gz.
"""
from __future__ import annotations

import collections
import gzip
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(_HERE, 'FourthAgePaper', 'ScalarContextPropagation', 'map', 'scalar_context_map.tsv.gz')


class ContextHash:
    """word -> where the Scalar Boxkite context hash puts its first sense: class, density basin, attractor basin, gamma, address."""

    def __init__(self, map_path: str = DEFAULT_MAP, use_nltk: bool = True):
        self.by_synset: Dict[str, Tuple[int, int, int, Optional[float], int]] = {}
        with gzip.open(map_path, 'rt', encoding='utf-8') as f:
            h = f.readline().rstrip('\n').split('\t')
            ix = {k: i for i, k in enumerate(h)}
            for line in f:
                c = line.rstrip('\n').split('\t')
                s = c[ix['synset']]
                if s not in self.by_synset:
                    g = c[ix['gamma_radial']]
                    self.by_synset[s] = (int(c[ix['class']]), int(c[ix['density_basin']]), int(c[ix['attractor_basin']]),
                                         None if g == '' else float(g), int(c[ix['context_addr']]))
        self._wn = None
        if use_nltk:
            from nltk.corpus import wordnet as wn
            self._wn = wn
        self._cache: Dict[str, Optional[tuple]] = {}

    def of(self, word: str) -> Optional[Dict[str, Any]]:
        w = word.lower()
        if w not in self._cache:
            v = None
            if self._wn is not None:
                ss = self._wn.synsets(w)
                if ss and ss[0].name() in self.by_synset:
                    v = self.by_synset[ss[0].name()]
            self._cache[w] = v
        v = self._cache[w]
        if v is None:
            return None
        return {'class': v[0], 'density_basin': v[1], 'attractor_basin': v[2], 'gamma': v[3], 'addr': v[4]}


LEVELS = ('child', 'general', 'college', 'specialist')
_TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")


@dataclass
class EnglishStats:
    unigram: collections.Counter = field(default_factory=collections.Counter)
    bigram: collections.Counter = field(default_factory=collections.Counter)
    ctx: collections.Counter = field(default_factory=collections.Counter)
    class_uni: collections.Counter = field(default_factory=collections.Counter)
    class_bi: collections.Counter = field(default_factory=collections.Counter)
    class_ctx: collections.Counter = field(default_factory=collections.Counter)
    word_in_class: collections.Counter = field(default_factory=collections.Counter)
    n_tokens: int = 0
    level_cut: Dict[str, int] = field(default_factory=lambda: {'child': 1000, 'general': 5000, 'college': 20000, 'specialist': 0})
    rank_levels: Tuple[int, int, int] = (300, 2000, 8000)      # median frequency rank of the user's words: child < general < college < specialist
    mix: Tuple[float, float, float] = (0.6, 0.3, 0.1)
    granularity: str = 'class'
    chash: Optional[ContextHash] = field(default=None, repr=False)
    _rank: Optional[Dict[str, int]] = field(default=None, repr=False)

    # ── learning ───────────────────────────────────────────────────────
    def _cls(self, w: str) -> int:
        if self.chash is None:
            return 0
        o = self.chash.of(w)
        if o is None:
            return 0
        return {'class': o['class'], 'basin': o['density_basin'], 'word': 0}.get(self.granularity, o['class'])

    def observe(self, text: str) -> int:
        """Count the usage in `text` (frequency, ordered pairs, classes). Returns tokens counted."""
        toks = _TOK.findall(text.lower())
        self.unigram.update(toks)
        prevc = None
        for i, w in enumerate(toks):
            c = self._cls(w)
            self.class_uni[c] += 1
            self.word_in_class[(c, w)] += 1
            if i:
                self.bigram[(toks[i - 1], w)] += 1
                self.ctx[toks[i - 1]] += 1
                self.class_bi[(prevc, c)] += 1
                self.class_ctx[prevc] += 1
            prevc = c
        self.n_tokens += len(toks)
        self._rank = None
        return len(toks)

    # ── the prediction ─────────────────────────────────────────────────
    def rank(self, w: str) -> int:
        if self._rank is None:
            self._rank = {x: i + 1 for i, (x, _) in enumerate(self.unigram.most_common())}
        return self._rank.get(w, 10 ** 9)

    def p(self, w: str, prev: Optional[str], level: Optional[str] = None) -> float:
        V = len(self.unigram) + 1
        pu = (self.unigram.get(w, 0) + 0.1) / (self.n_tokens + 0.1 * V)
        a, b, c = self.mix
        pw = 0.0
        if prev is not None and self.ctx.get(prev):
            cut = self.level_cut.get(level, 0) if level else 0
            if not (cut and self.rank(w) > cut):                      # beyond the level's rank cut: no word-pair evidence
                pw = self.bigram.get((prev, w), 0) / self.ctx[prev]
            else:
                a, b = 0.0, a + b
        pc = 0.0
        if prev is not None and self.chash is not None:
            cp, cw = self._cls(prev), self._cls(w)
            if self.class_ctx.get(cp) and self.class_uni.get(cw):
                pc = (self.class_bi.get((cp, cw), 0) / self.class_ctx[cp]) * (self.word_in_class.get((cw, w), 0) / self.class_uni[cw])
        if self.chash is None:
            a, b, c = a + b * 0.0, 0.0, c + b                           # no hash: word pairs and unigram only
        return a * pw + b * pc + c * pu

    def bits(self, text: str, level: Optional[str] = None) -> Tuple[float, int]:
        toks = _TOK.findall(text.lower())
        tot = 0.0
        for i in range(1, len(toks)):
            tot += -math.log2(max(self.p(toks[i], toks[i - 1], level), 1e-12))
        return tot, max(0, len(toks) - 1)

    # ── the educational response desire ─────────────────────────────────
    def level_for(self, text: str) -> str:
        """The level the user's own vocabulary suggests: the median frequency rank of their content words."""
        ranks = sorted(self.rank(w) for w in _TOK.findall(text.lower()) if len(w) > 3)
        if not ranks:
            return 'general'
        med = ranks[len(ranks) // 2]
        c1, c2, c3 = self.rank_levels
        if med < c1: return 'child'
        if med < c2: return 'general'
        if med < c3: return 'college'
        return 'specialist'

    def frequent(self, wn, pos: str, n: int) -> List[str]:
        """The n most frequent words that have a WordNet sense of part of speech `pos` (candidate pools when a prompt gives none)."""
        out = []
        for w, _ in self.unigram.most_common():
            if len(w) < 3:
                continue
            if wn.synsets(w, pos):
                out.append(w)
                if len(out) >= n:
                    break
        return out

    def vocabulary_at(self, level: str) -> List[str]:
        cut = self.level_cut.get(level, 0)
        ws = [w for w, _ in self.unigram.most_common()]
        return ws[:cut] if cut else ws

    # ── the poll ───────────────────────────────────────────────────────
    def poll(self) -> Dict[str, Any]:
        """The current values, as plain data."""
        return {'tokens': self.n_tokens, 'vocabulary': len(self.unigram), 'pairs': len(self.bigram),
                'classes_seen': len([c for c in self.class_uni if c]), 'granularity': self.granularity, 'mix': self.mix,
                'levels': {k: (min(v, len(self.unigram)) if v else len(self.unigram)) for k, v in self.level_cut.items()},
                'top_words': [w for w, _ in self.unigram.most_common(10)],
                'top_class_share': (self.class_uni.most_common(1)[0][1] / max(1, self.n_tokens)) if self.class_uni else 0.0}
