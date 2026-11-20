#!/usr/bin/env python3
"""
monad_english_io.py -- read()/write() for the language-center store.

`monad_english.bin` is a pickle (protocol 4), ~36 MB, 164,283 words, whose
core is a sparse co-occurrence A-matrix:  A[i] = {j: weight in (0,1]}  --
"from word i, the pull toward word j".  THIS IS THE NEWTON-BASIN FIELD:
the roots are words, A is the dynamics, a seed iterated through A converges
to a word; a topic-scoped A (monad_physics.bin, ...) is a sub-basin.

The learning lives HERE, in the speech -- not in the fold geometry or the
prime hash. The monad deepens these edges as it runs (browsing, research):
the merge rule is max(existing, new), NEVER renormalise (repeats deepen
context). This module is that read/write path, plus the basin accessor the
constructor needs.

Pickle dict schema (v1.218):
  version str | n int | vocab {word:idx} | words [word] | beta [float]
  E [float] | A [ {j:w} ] | age [int] | fire_count [int] | stratum [int]
  psi_prev [16 float] | word_count int | correction_mask {}
"""
from __future__ import annotations

import os
import pickle
import tempfile
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
WORKING = os.path.join(_HERE, 'PtolC', 'monad_english.bin')
_ARCHIVE_DIR = '/home/rendier/Projects/ThePlace/PTorrent/bin_archive/clean'
ARCHIVE = os.path.join(_ARCHIVE_DIR, 'monad_english.bin')


def topic_path(topic: Optional[str]) -> Optional[str]:
    """Map a topic name to its scoped A-matrix bin -- the SETTING, a
    narrowed Newton basin (monad_physics.bin, monad_mathematics.bin, ...).
    None / 'english' -> the full store. Unknown topic -> None (full store)."""
    if not topic or topic.lower() == 'english':
        return None
    p = os.path.join(_ARCHIVE_DIR, f'monad_{topic.lower()}.bin')
    return p if os.path.exists(p) else None

_ARRAY_KEYS = ('beta', 'E', 'A', 'age', 'fire_count', 'stratum')

# Function words + tokens that co-occur with everything or carry no
# lexical content -- excluded from the basin BEFORE resolution (IDF alone
# rewards their rarity when they're single letters / acronyms).
STOPWORDS = frozenset("""
a an the this that these those and or but nor for so yet of to in on at by
with from as into onto upon over under out off up down about after before
is are was were be been being am do does did have has had having will would
shall should can could may might must not no yes it its it's they them their
he she his her him we us our you your i me my mine ours yours theirs one ones
which who whom whose what where when why how there here then than too very
just also only even still ever never always some any all each every both few
many much more most other another such same own way thing things get got
""".split())

# The monad hears everything it says -- its own utterances deepen the
# co-occurrence field (hear() below). To stop it driving itself into
# feedback on its own output, content that has already looped back through
# the monad this many times stops being heard.
ECHO_CAP = 5


def _tokens(text: str):
    out = []
    for raw in str(text).split():
        w = raw.strip('.,;:!?"\'()[]{}<>-—–‘’“”').lower()
        if w:
            out.append(w)
    return out


@dataclass
class MonadEnglish:
    version: str
    vocab: Dict[str, int]
    words: List[str]
    beta: List[float]
    E: List[float]
    A: List[Dict[int, float]]           # sparse co-occurrence adjacency
    age: List[int]
    fire_count: List[int]
    stratum: List[int]
    psi_prev: List[float]
    word_count: int
    correction_mask: Dict
    path: Optional[str] = None
    _extra: Dict = field(default_factory=dict)   # any future keys, preserved
    dirty: bool = False
    _indeg: Optional[List[int]] = None           # lazy: co-occurrence in-degree
    _touched: Optional[set] = None               # word idxs mutated since load

    # ---- lookups ----
    def idx(self, word: str) -> Optional[int]:
        return self.vocab.get(word.lower().strip())

    def indegree(self) -> List[int]:
        """How many words point AT each word -- the co-occurrence document
        frequency. Built once (O(edges)); reset to None after big deepen
        batches if you want it recomputed."""
        if self._indeg is None:
            deg = [0] * len(self.words)
            for nbrs in self.A:
                for j in nbrs:
                    deg[j] += 1
            self._indeg = deg
        return self._indeg

    def idf(self, word: str) -> float:
        """log(N / (1 + in-degree)) -- high for rare words, ~0 for words
        that co-occur with everything ('the', 'and', 'you')."""
        i = self.idx(word)
        if i is None:
            return 0.0
        import math as _m
        return _m.log(len(self.words) / (1.0 + self.indegree()[i]))

    def neighbors(self, word: str, k: Optional[int] = None
                  ) -> List[Tuple[str, float]]:
        """A word's co-occurrence basin, strongest pull first."""
        i = self.idx(word)
        if i is None:
            return []
        pairs = sorted(((self.words[j], w) for j, w in self.A[i].items()),
                       key=lambda t: -t[1])
        return pairs[:k] if k else pairs

    def basin(self, seeds: Sequence[str], k: Optional[int] = None,
              idf: bool = True, min_pull: float = 0.25) -> Dict[str, float]:
        """The candidate pool as one Newton basin: over all seed words,
        pull(j) = max_i A[i][j]  (max, matching the deepen rule -- not a
        sum, which would just reward hub words).

        idf=True multiplies each pull by idf(word) so the function-word
        flood ('the', 'and', 'you') is crushed and content words surface;
        min_pull drops single-noise-occurrence edges first. The returned
        score is pull*idf when idf=True, else raw pull."""
        pull: Dict[int, float] = {}
        for s in seeds:
            i = self.idx(s)
            if i is None:
                continue
            for j, w in self.A[i].items():
                if w >= min_pull and w > pull.get(j, 0.0):
                    pull[j] = w
        if idf:
            deg = self.indegree()
            n = len(self.words)
            import math as _m
            scored = ((self.words[j], w * _m.log(n / (1.0 + deg[j])))
                      for j, w in pull.items())
        else:
            scored = ((self.words[j], w) for j, w in pull.items())
        out = sorted(scored, key=lambda t: -t[1])
        return dict(out[:k] if k else out)

    # ---- mutation: the monad learning as it goes ----
    def _ensure(self, word: str) -> int:
        w = word.lower().strip()
        i = self.vocab.get(w)
        if i is not None:
            return i
        i = len(self.words)
        self.vocab[w] = i
        self.words.append(w)
        self.beta.append(0.0)
        self.E.append(0.0)
        self.A.append({})
        self.age.append(0)
        self.fire_count.append(0)
        self.stratum.append(0)
        self.dirty = True
        return i

    def deepen(self, src: str, tgt: str, weight: float = 1.0) -> None:
        """max(existing, new) -- repeats DEEPEN context, never renormalise."""
        i, j = self._ensure(src), self._ensure(tgt)
        if weight > self.A[i].get(j, 0.0):
            self.A[i][j] = weight
        self.fire_count[i] += 1
        self.age[i] = int(time.time())
        self.dirty = True
        if self._touched is None:
            self._touched = set()
        self._touched.add(i)
        self._touched.add(j)

    def deepen_many(self, src: str, targets: Sequence[Tuple[str, float]]) -> None:
        for tgt, w in targets:
            self.deepen(src, tgt, w)

    # ---- serialisation ----
    def to_dict(self) -> Dict:
        d = dict(self._extra)
        d.update(
            version=self.version, n=len(self.words), vocab=self.vocab,
            words=self.words, beta=self.beta, E=self.E, A=self.A, age=self.age,
            fire_count=self.fire_count, stratum=self.stratum,
            psi_prev=self.psi_prev, word_count=self.word_count,
            correction_mask=self.correction_mask,
        )
        return d


def hear(me: MonadEnglish, text: str, echo: int = 0, window: int = 5,
         base: float = 1.0, cap: int = ECHO_CAP) -> Tuple[int, int]:
    """The monad's UNIVERSAL INTAKE: everything it says, sees, hears, or
    reads deepens the co-occurrence field. It is a participant in its own
    education -- not passively trained. Unknown words are ADDED, not
    dropped.

    `echo` = how many times this content has ALREADY looped back through
    the monad. Anything from outside (a user turn, a fetched page, a
    research result) is echo 0 and is never capped. The monad's own
    output, fed back, increments `echo` each pass; at `echo >= cap` this
    is a NO-OP so it cannot drive itself into feedback on what it just
    said.

    Co-occurrence: within a sliding window, weight decays with distance
    (adjacent = base, `window` apart -> 0), merged by max (repeats deepen
    context, never renormalise). Returns (edges_deepened, new_words)."""
    if echo >= cap:
        return (0, 0)
    toks = _tokens(text)
    before = len(me.words)
    n = 0
    for i in range(len(toks)):
        for d in range(1, window + 1):
            j = i + d
            if j >= len(toks):
                break
            w = base * (1.0 - (d - 1) / window)
            me.deepen(toks[i], toks[j], w)
            me.deepen(toks[j], toks[i], w)
            n += 2
    return (n, len(me.words) - before)


_CACHE: Dict[str, MonadEnglish] = {}


def read(path: Optional[str] = None, use_cache: bool = True) -> MonadEnglish:
    """Load the language-center store. Tries the working copy, falls back
    to the clean archive. Resident-cached (the file is ~300 MB in RAM;
    keeping all three monad bins open is fine per design)."""
    if path is None:
        path = WORKING if os.path.exists(WORKING) else ARCHIVE
    path = os.path.abspath(path)
    if use_cache and path in _CACHE:
        return _CACHE[path]

    with open(path, 'rb') as f:
        d = pickle.load(f)
    known = {'version', 'n', 'vocab', 'words', 'beta', 'E', 'A', 'age',
             'fire_count', 'stratum', 'psi_prev', 'word_count',
             'correction_mask'}
    me = MonadEnglish(
        version=d.get('version', 'unknown'),
        vocab=d['vocab'], words=d['words'], beta=d['beta'], E=d['E'],
        A=d['A'], age=d['age'],
        fire_count=d.get('fire_count', [0] * len(d['words'])),
        stratum=d.get('stratum', [0] * len(d['words'])),
        psi_prev=d.get('psi_prev', [0.0] * 16),
        word_count=d.get('word_count', 0),
        correction_mask=d.get('correction_mask', {}),
        path=path,
        _extra={k: v for k, v in d.items() if k not in known},
    )
    if use_cache:
        _CACHE[path] = me
    return me


def write(me: MonadEnglish, path: Optional[str] = None, backup: bool = True
          ) -> str:
    """Atomically persist (temp file + rename, so a crash mid-write can't
    corrupt the 36 MB store). Keeps one .bak of the previous version."""
    path = os.path.abspath(path or me.path or WORKING)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if backup and os.path.exists(path):
        os.replace(path, path + '.bak')
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as f:
            pickle.dump(me.to_dict(), f, protocol=4)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    me.path = path
    me.dirty = False
    return path


# ==========================================================================
if __name__ == '__main__':
    import sys

    src = ARCHIVE
    print(f"read({src}) ...")
    t = time.time()
    me = read(src, use_cache=False)
    print(f"  {time.time()-t:.2f}s  version={me.version}  "
          f"words={len(me.words):,}  edges={sum(len(a) for a in me.A):,}")

    # round-trip
    scratch = ('/home/rendier/Projects/ThePlace/ContextPlease/claude/scratchpad/'
               '2026-08-27_spectral-vs-residual-hash/_me_roundtrip.bin')
    write(me, scratch, backup=False)
    me2 = read(scratch, use_cache=False)
    ok = (me2.words == me.words and me2.vocab == me.vocab
          and me2.A == me.A and me2.beta == me.beta and me2.E == me.E
          and me2.psi_prev == me.psi_prev)
    print(f"round-trip identical: {ok}   "
          f"({os.path.getsize(scratch)/1e6:.1f} MB)")
    os.unlink(scratch)

    # basin demo -- the constructor's pool
    for probe in ('kitchen', 'physics', 'grammar'):
        nb = me.neighbors(probe, k=8)
        print(f"\n  neighbors({probe!r}): "
              + ", ".join(f"{w}:{v:.2f}" for w, v in nb))
    b = me.basin(['cook', 'kitchen', 'recipe'], k=12)
    print("\n  basin(['cook','kitchen','recipe']):",
          ", ".join(f"{w}:{v:.2f}" for w, v in list(b.items())))

    # deepen demo -- learning as it goes
    me.deepen('cook', 'sous-vide', 0.9)
    me.deepen('cook', 'mise-en-place', 0.95)
    j = me.idx('sous-vide')
    print(f"\n  after deepen: 'sous-vide' idx={j}  "
          f"A[cook][sous-vide]={me.A[me.idx('cook')].get(j)}  dirty={me.dirty}")

    # hear() + echo cap
    utt = "the sommelier decanted the wine before the tasting"
    print("\n  hear() at each echo depth (cap =", ECHO_CAP, "):")
    for e in range(ECHO_CAP + 2):
        edges, new = hear(me, utt, echo=e)
        print(f"    echo={e}: deepened {edges} edges, {new} new words"
              + ("   <- feedback broken" if edges == 0 else ""))
    print("  external input (user/web/research) is always echo=0, never capped")
