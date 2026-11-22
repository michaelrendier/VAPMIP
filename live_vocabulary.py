#!/usr/bin/env python3
"""
live_vocabulary.py -- the Monad's own vocabulary, improvable on the fly.

Cody, 2026-11-21: Ptolemy must be able to improve his own vocabulary, the way a
reader does: hear or read a sentence, learn what a word relates to, remember
WHEN it was learned, HOW it was refined, and WHEN it became a different word.
No outside machinery (no Princeton grinder) is needed: the WordNet context
vector of a sense is DERIVED from relation edges, and edges can be added.

What this file is
-----------------
  * a sense store layered over WordNet 3.0 (NLTK) and the context bin:
        sense id  'wn:<pos><offset>'            a WordNet sense (base counts read
                                                from NLTK, exact)
                  'live:<word>.<pos>.<k>'       a sense the Monad learned itself
  * a relation-edge log: each edge is (sense, relation, target sense) with its
    source sentence, a support count and timestamps. The 19-vector of a sense is
    compress_count(base count + added edges) per relation, exactly as
    wordnet_boxkite.context_vector defines it. Reciprocal relations are kept
    consistent (hypernym <-> hyponym, instance, member/substance/part holonym <->
    meronym: measured exact on all of WordNet 3.0, bench/dim19.txt); symmetric
    ones (attributes, also_sees, verb_groups, similar_tos) are written both ways.
  * an append-only JSONL journal. Replaying it over the same base rebuilds the
    same state (deterministic), so the journal IS the vocabulary's memory:
        created   first time a word/sense exists          (when, from what sentence)
        edge      a relation edge added                    (vector before / after)
        support   the same edge heard again                (refinement; no vector change)
        seen      an unknown token met, no evidence yet    (first/last time, count)
        split     one sense divided into two               (when it became a different word)
  * hear(text): a deterministic reader (Hearst 1992 style patterns: "X is a kind
    of Y", "Y such as X", "X is part of Y", ...) that turns sentences into edges.
    Limits are stated, not hidden: single-token noun heads, English patterns only.
  * dirty_frames(): the touched senses as sedenion-shaped frames (<= 16 senses, an
    anchor e0, a spanning tree of <= 15 relation edges), the same shape as
    CombinedMonad.dirty_chunks, so the sedenion window can persist a frame at a time.
  * repack_monad3c(): writes the changed senses into a COPY of monad3_c.bin (the
    C-native store ptol mmaps), adding new words to the word table. The source
    file is never modified.

Honest boundaries
-----------------
  * one entry per word in the bin: a changed sense that is not the bin's own entry
    is written as the row  'word#<pos>:<offset-or-liveid>'.
  * a new word has no phonetic entry and no English co-occurrence row here; those
    stores learn through monad_english_io.hear and the phonetic builder.
  * sense choice for an EXISTING word in a pattern is "first WordNet sense of the
    needed part of speech" (recorded in the event as resolution='first-pos-sense').
    Disambiguation by context is the orbweaver's job, not this file's.
"""
from __future__ import annotations

import datetime
import json
import math
import os
import re
import struct
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import wordnet_boxkite as _WB

RELATIONS: List[str] = list(_WB.RELATION_METHODS)
_REL_IDX = {r: i for i, r in enumerate(RELATIONS)}

# Exact reciprocals (measured: equal edge-endpoint totals on all of WordNet 3.0).
INVERSE: Dict[str, str] = {
    'hypernyms': 'hyponyms', 'hyponyms': 'hypernyms',
    'instance_hypernyms': 'instance_hyponyms', 'instance_hyponyms': 'instance_hypernyms',
    'member_holonyms': 'member_meronyms', 'member_meronyms': 'member_holonyms',
    'substance_holonyms': 'substance_meronyms', 'substance_meronyms': 'substance_holonyms',
    'part_holonyms': 'part_meronyms', 'part_meronyms': 'part_holonyms',
    # symmetric (even endpoint totals in WordNet 3.0; written both ways):
    'attributes': 'attributes', 'also_sees': 'also_sees',
    'verb_groups': 'verb_groups', 'similar_tos': 'similar_tos',
}
# no stored inverse among the 19: entailments, causes, topic/region/usage domains.

_POS_CODE = {'n': 1, 'v': 2, 'a': 3, 's': 3, 'r': 4}
_CODE_POS = {1: 'n', 2: 'v', 3: 'a', 4: 'r'}
LIVE_OFFSET_BASE = 0xF0000000          # synset_offset of a learned sense in the bin: base + k

_STOP = set("the a an of in on at for with by from about into is are was were be been being and or but not no "
            "to it its this that these those his her their our your my as if so than then there here which who "
            "whom whose what when where why how can could may might will would shall should do does did has have "
            "had also very just only more most such other some any each every all both either neither one two "
            "three i you he she we they them us me him".split())


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')


def compress(count: int) -> int:
    return _WB.compress_count(count)


def _decompress(v: int) -> int:
    """Approximate inverse of compress_count, used only when NLTK cannot give the real count."""
    return max(0, int(round(2 ** v)) - 1)


# ── the reader's patterns (Hearst 1992 style); NP = optional article + one token ──
_W = r"([a-z][a-z-]*[a-z]|[a-z])"
_ART = r"(?:(?:an?|the)\s+)?"
_PATTERNS: List[Tuple[str, str, bool]] = [
    # (regex, relation of group1, flip)  relation is read as: group1 --relation--> group2
    (_ART + _W + r"\s+(?:is|are)\s+" + r"(?:an?\s+)?(?:kind|type|sort|form|species|class|variety)\s+of\s+" + _ART + _W, 'hypernyms', False),
    (_ART + _W + r"\s+(?:is|are)\s+an?\s+" + _W + r"$", 'hypernyms', False),
    (_ART + _W + r"\s+(?:is|are)\s+(?:a\s+)?part\s+of\s+" + _ART + _W, 'part_holonyms', False),
    (_ART + _W + r"\s+(?:is|are)\s+(?:a\s+)?member\s+of\s+" + _ART + _W, 'member_holonyms', False),
    (_ART + _W + r"\s+(?:is|are)\s+made\s+(?:of|from)\s+" + _ART + _W, 'substance_meronyms', False),
    (_ART + _W + r"\s+(?:has|have|contains?)\s+an?\s+" + _W, 'part_meronyms', False),
    (_ART + _W + r"\s+(?:causes?|leads?\s+to)\s+" + _ART + _W, 'causes', False),
    (_ART + _W + r"\s+(?:is|are)\s+similar\s+to\s+" + _ART + _W, 'similar_tos', False),
]
_SUCH_AS = re.compile(_ART + _W + r",?\s+such\s+as\s+(.+)$")
_LIST_SPLIT = re.compile(r"\s*(?:,|\band\b|\bor\b)\s*")


class Sense:
    """One sense: identity, base counts, added edges, history pointers."""
    __slots__ = ('id', 'word', 'pos', 'source', 'offset', 'base_raw', 'added', 'support',
                 'created', 'depth_weight', 'events')

    def __init__(self, sid: str, word: str, pos: str, source: str, offset: int,
                 base_raw: Optional[List[int]] = None, created: str = ''):
        self.id = sid
        self.word = word
        self.pos = pos
        self.source = source                     # 'wordnet' | 'live'
        self.offset = offset
        self.base_raw = list(base_raw) if base_raw else [0] * len(RELATIONS)
        self.added: Dict[str, List[str]] = {r: [] for r in RELATIONS}   # relation -> target sense ids
        self.support: Dict[Tuple[str, str], int] = {}                    # (relation, target) -> times heard
        self.created = created
        self.depth_weight = 1.0
        self.events: List[int] = []              # journal sequence numbers touching this sense

    def raw(self) -> List[int]:
        return [self.base_raw[i] + len(self.added[r]) for i, r in enumerate(RELATIONS)]

    def vector(self) -> List[int]:
        return [compress(c) for c in self.raw()]

    def touched(self) -> bool:
        return any(self.added[r] for r in RELATIONS)


class LiveVocabulary:
    def __init__(self, journal_path: Optional[str] = None, clock: Callable[[], str] = _now,
                 base_bin: Optional[str] = None, use_nltk: bool = True):
        self.clock = clock
        self.journal_path = journal_path
        self.senses: Dict[str, Sense] = {}
        self.by_word: Dict[str, List[str]] = {}
        self.unknown: Dict[str, Dict[str, Any]] = {}     # word -> {'first','last','count'}
        self.journal: List[dict] = []
        self._wn = None
        if use_nltk:
            from nltk.corpus import wordnet as wn
            self._wn = wn
        self._live_k = 0
        self.base_bin = base_bin
        self._replaying = False
        if journal_path and os.path.exists(journal_path):
            self.replay(journal_path)

    # ── journal ─────────────────────────────────────────────────────────
    def _emit(self, kind: str, **fields) -> dict:
        ev = {'seq': len(self.journal), 't': self.clock(), 'kind': kind}
        ev.update(fields)
        self.journal.append(ev)
        if self.journal_path and not self._replaying:
            with open(self.journal_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(ev, ensure_ascii=False, sort_keys=True) + '\n')
        return ev

    def replay(self, path: str) -> int:
        """Rebuild state from a journal file. Deterministic: same base + same journal -> same state."""
        self._replaying = True
        n = 0
        try:
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    ev = json.loads(line)
                    self._apply(ev)
                    n += 1
        finally:
            self._replaying = False
        return n

    def _apply(self, ev: dict) -> None:
        """Re-execute one journal event (without re-writing it)."""
        k = ev['kind']
        saved = self.clock
        self.clock = lambda t=ev['t']: t
        try:
            if k == 'created':
                self._ensure_sense(ev['sense'], ev['word'], ev['pos'], ev['source'], ev.get('offset'),
                                   evidence=ev.get('evidence', ''), resolution=ev.get('resolution', ''))
            elif k in ('edge', 'support'):
                self.add_edge(ev['sense'], ev['relation'], ev['target'], source=ev.get('source', ''),
                              _from_replay=True)
            elif k == 'seen':
                self.unknown[ev['word']] = {'first': ev['t'], 'last': ev['t'], 'count': ev.get('count', 1)}
                self._emit('seen', word=ev['word'], count=ev.get('count', 1))
            elif k == 'split':
                self.split_sense(ev['sense'], ev['moved'], _from_replay=True)
        finally:
            self.clock = saved

    # ── senses ──────────────────────────────────────────────────────────
    def _wn_base_raw(self, synset) -> List[int]:
        return [len(getattr(synset, m)()) for m in RELATIONS]

    def _wn_sense(self, synset) -> Sense:
        sid = 'wn:%s%08d' % (synset.pos(), synset.offset())
        if sid in self.senses:
            return self.senses[sid]
        lemma = synset.lemma_names()[0].lower()
        s = Sense(sid, lemma, synset.pos(), 'wordnet', synset.offset(), self._wn_base_raw(synset), self.clock())
        self.senses[sid] = s
        self.by_word.setdefault(lemma, []).append(sid)
        return s

    def _ensure_sense(self, sid: str, word: str, pos: str, source: str, offset: Optional[int],
                      evidence: str = '', resolution: str = '') -> Sense:
        if sid in self.senses:
            return self.senses[sid]
        if sid.startswith('wn:'):
            ss = self._wn.synset_from_pos_and_offset(sid[3], int(sid[4:]))
            s = self._wn_sense(ss)
        else:
            s = Sense(sid, word, pos, 'live', offset if offset is not None else LIVE_OFFSET_BASE + self._live_k,
                      None, self.clock())
            self._live_k = max(self._live_k, int(sid.rsplit('.', 1)[-1]))
            self.senses[sid] = s
            self.by_word.setdefault(word, []).append(sid)
            self.unknown.pop(word, None)
        ev = self._emit('created', sense=sid, word=s.word, pos=s.pos, source=s.source, offset=s.offset,
                        evidence=evidence, resolution=resolution)
        s.events.append(ev['seq'])
        return s

    def resolve(self, word: str, pos: str, evidence: str = '', create: bool = True) -> Optional[Sense]:
        """The sense a pattern slot refers to. Existing live sense of that pos first, else the first WordNet
        sense of that pos (resolution='first-pos-sense'), else a new live sense (a word the Monad learns)."""
        word = word.lower()
        for sid in self.by_word.get(word, []):
            if self.senses[sid].pos == pos:
                return self.senses[sid]
        if self._wn is not None:
            wpos = 'a' if pos == 'a' else pos
            ss = self._wn.synsets(word, wpos)
            if ss:
                s = self._wn_sense(ss[0])
                ev = self._emit('created', sense=s.id, word=word, pos=s.pos, source='wordnet', offset=s.offset,
                                evidence=evidence, resolution='first-pos-sense')
                s.events.append(ev['seq'])
                return s
        if not create:
            return None
        self._live_k += 1
        sid = 'live:%s.%s.%02d' % (word, pos, sum(1 for x in self.by_word.get(word, []) if x.startswith('live:')) + 1)
        s = Sense(sid, word, pos, 'live', LIVE_OFFSET_BASE + self._live_k, None, self.clock())
        self.senses[sid] = s
        self.by_word.setdefault(word, []).append(sid)
        ev = self._emit('created', sense=sid, word=word, pos=pos, source='live', offset=s.offset,
                        evidence=evidence, resolution='new-word')
        s.events.append(ev['seq'])
        self.unknown.pop(word, None)
        return s

    # ── edges ───────────────────────────────────────────────────────────
    def add_edge(self, sid: str, relation: str, target: str, source: str = '', _from_replay: bool = False
                 ) -> Dict[str, Any]:
        """Add (or re-support) the edge sid --relation--> target, and its reciprocal. Returns what changed."""
        if relation not in _REL_IDX:
            raise KeyError(relation)
        s = self.senses[sid] if sid in self.senses else self._ensure_sense(sid, '', '', '', None)
        t = self.senses[target] if target in self.senses else self._ensure_sense(target, '', '', '', None)
        out = {'sense': sid, 'relation': relation, 'target': target, 'new': False}
        key = (relation, target)
        if target in s.added[relation]:
            s.support[key] = s.support.get(key, 1) + 1
            ev = self._emit('support', sense=sid, relation=relation, target=target, source=source,
                            support=s.support[key])
            s.events.append(ev['seq'])
            return out
        before = s.vector()
        s.added[relation].append(target)
        s.support[key] = 1
        inv = INVERSE.get(relation)
        before_t = t.vector()
        if inv is not None and sid not in t.added[inv] and not (inv == relation and sid == target):
            t.added[inv].append(sid)
            t.support[(inv, sid)] = 1
        ev = self._emit('edge', sense=sid, relation=relation, target=target, source=source,
                        vec_before=before, vec_after=s.vector(),
                        target_vec_before=before_t, target_vec_after=t.vector())
        s.events.append(ev['seq'])
        t.events.append(ev['seq'])
        out['new'] = True
        out['vec_before'] = before
        out['vec_after'] = s.vector()
        return out

    # ── hearing ─────────────────────────────────────────────────────────
    def note_unknown(self, word: str) -> None:
        word = self.lemma(word, 'n')
        if self._wn is not None and self._wn.synsets(word):
            return
        if word in self.by_word:
            return
        u = self.unknown.get(word)
        if u is None:
            self.unknown[word] = {'first': self.clock(), 'last': self.clock(), 'count': 1}
            self._emit('seen', word=word, count=1)
        else:
            u['count'] += 1
            u['last'] = self.clock()

    def hear(self, text: str, source: str = 'heard') -> List[dict]:
        """Read text; return the edge/support events produced. Sentences that match no pattern teach nothing
        about relations but unknown tokens in them are noted as 'seen'."""
        results: List[dict] = []
        for sent in re.split(r"[.!?;\n]+", text.lower()):
            sent = re.sub(r"\s+", " ", sent.strip(" ,:\"'()"))
            if not sent:
                continue
            for w in re.findall(r"[a-z][a-z-]{2,}", sent):
                if w not in _STOP:
                    self.note_unknown(w)
            m = _SUCH_AS.search(sent)
            if m:
                hyper = m.group(1)
                items = [x for x in (_LIST_SPLIT.split(m.group(2)) if m.group(2) else []) if x]
                for it in items:
                    it = re.sub(r"^(?:an?|the)\s+", "", it.strip())
                    if re.fullmatch(r"[a-z][a-z-]*", it):
                        results.append(self._learn(it, 'hypernyms', hyper, sent, source, ('n', 'n')))
                continue
            for rx, rel, _ in _PATTERNS:
                m = re.fullmatch(rx, sent)
                if not m:
                    continue
                a, b = m.group(1), m.group(2)
                if a in _STOP or b in _STOP:
                    break
                pos = ('v', 'v') if rel == 'causes' else ('a', 'a') if rel == 'similar_tos' else ('n', 'n')
                results.append(self._learn(a, rel, b, sent, source, pos))
                break
        return results

    def lemma(self, word: str, pos: str) -> str:
        """Base form: WordNet morphy when it knows the word, else a conservative plural/3rd-person strip
        (-ies -> -y; -ses/-xes/-ches/-shes -> drop -es; -s -> drop, but not -ss/-us/-is)."""
        if self._wn is not None:
            m = self._wn.morphy(word, 'a' if pos == 'a' else pos)
            if m:
                return m
        if pos in ('n', 'v') and len(word) > 3:
            if word.endswith('ies'):
                return word[:-3] + 'y'
            if re.search(r'(ses|xes|ches|shes)$', word):
                return word[:-2]
            if word.endswith('s') and not re.search(r'(ss|us|is)$', word):
                return word[:-1]
        return word

    def _learn(self, a: str, rel: str, b: str, sentence: str, source: str, pos: Tuple[str, str]) -> dict:
        a, b = self.lemma(a, pos[0]), self.lemma(b, pos[1])
        if a in _STOP or b in _STOP or len(a) < 3 or len(b) < 3 or a == b:
            return {'sense': None, 'relation': rel, 'target': None, 'new': False, 'skipped': 'function word or too short',
                    'sentence': sentence, 'words': (a, b)}
        if rel == 'causes':
            # WordNet's `causes` relation links VERB senses only; noun causation ("smoking causes cancer") has no
            # place among the 19 relations, so it is skipped rather than forced.
            if any(self.resolve(x, 'v', create=False) is None for x in (a, b)):
                return {'sense': None, 'relation': rel, 'target': None, 'new': False, 'skipped': 'not verb-verb',
                        'sentence': sentence, 'words': (a, b)}
        sa = self.resolve(a, pos[0], evidence=sentence)
        sb = self.resolve(b, pos[1], evidence=sentence)
        r = self.add_edge(sa.id, rel, sb.id, source=source or sentence)
        r['sentence'] = sentence
        r['words'] = (a, b)
        return r

    # ── becoming a different word ───────────────────────────────────────
    def propose_splits(self, word: str, threshold: float = 0.15) -> List[dict]:
        """For a word whose senses accumulated hypernym targets that are far apart in the WordNet taxonomy
        (path similarity below the threshold), propose which edges belong to different senses."""
        out = []
        for sid in self.by_word.get(word.lower(), []):
            s = self.senses[sid]
            tg = s.added['hypernyms']
            if len(tg) < 2 or self._wn is None:
                continue
            groups: List[List[str]] = []
            for t in tg:
                ts = self._synset_of(t)
                placed = False
                for g in groups:
                    gs = self._synset_of(g[0])
                    sim = (ts.path_similarity(gs) if ts and gs else None)
                    if sim is not None and sim >= threshold:
                        g.append(t)
                        placed = True
                        break
                if not placed:
                    groups.append([t])
            if len(groups) > 1:
                out.append({'sense': sid, 'groups': groups})
        return out

    def _synset_of(self, sid: str):
        if sid.startswith('wn:') and self._wn is not None:
            return self._wn.synset_from_pos_and_offset(sid[3], int(sid[4:]))
        s = self.senses.get(sid)
        if s is not None and s.added['hypernyms']:
            return self._synset_of(s.added['hypernyms'][0])
        return None

    def split_sense(self, sid: str, moved: Dict[str, List[str]], _from_replay: bool = False) -> str:
        """Divide sense `sid`: the edges in `moved` ({relation: [targets]}) leave it and become a new live sense of
        the same word and part of speech. The base (WordNet) counts stay with the original. Journaled as 'split'."""
        s = self.senses[sid]
        self._live_k += 1
        n = sum(1 for x in self.by_word.get(s.word, []) if x.startswith('live:')) + 1
        nid = 'live:%s.%s.%02d' % (s.word, s.pos, n)
        ns = Sense(nid, s.word, s.pos, 'live', LIVE_OFFSET_BASE + self._live_k, None, self.clock())
        self.senses[nid] = ns
        self.by_word.setdefault(s.word, []).append(nid)
        for rel, tgts in moved.items():
            for t in tgts:
                if t in s.added[rel]:
                    s.added[rel].remove(t)
                    ns.added[rel].append(t)
                    ns.support[(rel, t)] = s.support.pop((rel, t), 1)
                    tt = self.senses[t]
                    inv = INVERSE.get(rel)
                    if inv and sid in tt.added[inv]:
                        tt.added[inv][tt.added[inv].index(sid)] = nid
        ev = self._emit('split', sense=sid, new_sense=nid, word=s.word, moved=moved)
        s.events.append(ev['seq'])
        ns.events.append(ev['seq'])
        return nid

    # ── queries ─────────────────────────────────────────────────────────
    def history(self, word_or_sense: str) -> List[dict]:
        ids = [word_or_sense] if word_or_sense in self.senses else self.by_word.get(word_or_sense.lower(), [])
        seqs = {q for i in ids for q in self.senses[i].events}
        w = word_or_sense.lower()
        seqs |= {e['seq'] for e in self.journal if e['kind'] == 'seen' and e.get('word') == w}
        return [self.journal[q] for q in sorted(seqs)]

    def lookup(self, word: str) -> List[dict]:
        return [{'sense': i, 'pos': self.senses[i].pos, 'source': self.senses[i].source,
                 'vector': self.senses[i].vector(), 'gamma_radial': _WB.gamma_radial(self.senses[i].vector()),
                 'created': self.senses[i].created, 'edges_added': sum(len(v) for v in self.senses[i].added.values())}
                for i in self.by_word.get(word.lower(), [])]

    def touched_senses(self) -> List[Sense]:
        return [s for s in self.senses.values() if s.touched() or s.source == 'live']

    # ── the sedenion window ─────────────────────────────────────────────
    def dirty_frames(self, cap: int = 16) -> List[dict]:
        """The touched senses as sedenion-shaped frames. A frame is one local context: node[0] = e0 (the anchor:
        the sense with most edges in its connected component), up to cap-1 = 15 other nodes, and a spanning tree of
        <= 15 relation edges from the edge log. A component larger than one frame yields several frames that share
        its anchor."""
        touched = {s.id: s for s in self.touched_senses()}
        adj: Dict[str, List[Tuple[str, str]]] = {i: [] for i in touched}
        for i, s in touched.items():
            for rel, tg in s.added.items():
                for t_ in tg:
                    if t_ in touched and t_ != i:
                        adj[i].append((t_, rel)); adj[t_].append((i, rel))
        seen_c: set = set()
        frames: List[dict] = []
        for start in sorted(touched, key=lambda i: (-len(adj[i]), i)):
            if start in seen_c:
                continue
            comp, stack = [], [start]
            seen_c.add(start)
            while stack:
                x = stack.pop()
                comp.append(x)
                for y, _ in adj[x]:
                    if y not in seen_c:
                        seen_c.add(y); stack.append(y)
            anchor = max(comp, key=lambda i: (len(adj[i]), i))
            order, parent, q = [anchor], {anchor: None}, [anchor]
            while q:                                   # BFS from the anchor: parent edge of each node
                x = q.pop(0)
                for y, rel in sorted(adj[x]):
                    if y not in parent:
                        parent[y] = (x, rel); order.append(y); q.append(y)
            rest = order[1:]
            chunks = [rest[k:k + cap - 1] for k in range(0, len(rest), cap - 1)] or [[]]
            for ch in chunks:
                nodes = [anchor] + ch
                nset = set(nodes)
                tree = []
                for n in ch:
                    px, rel = parent[n]
                    if px in nset:
                        tree.append((px, rel, n))
                    else:                              # parent fell in an earlier frame: join to the anchor if linked
                        link = next(((anchor, r_, n) for y, r_ in adj[n] if y == anchor), None)
                        if link:
                            tree.append(link)
                frames.append({'e0': anchor, 'nodes': nodes, 'edges': tree,
                               'unreached': [n for n in ch if n not in {e[2] for e in tree}]})
        return frames

    # ── the bin ─────────────────────────────────────────────────────────
    def bin_rows(self) -> Dict[str, dict]:
        """The rows to write into monad3_c.bin: key -> {'pos','offset','vec19','depth_weight'}."""
        rows: Dict[str, dict] = {}
        for s in self.touched_senses():
            key = s.word
            own = None
            if self.base_bin and os.path.exists(self.base_bin):
                own = _base_entry_offsets(self.base_bin).get(s.word)
            if s.source == 'wordnet' and own is not None and own != s.offset:
                key = '%s#%s:%d' % (s.word, s.pos, s.offset)
            elif s.source == 'live' and s.word in rows:
                key = '%s#%s:%d' % (s.word, s.pos, s.offset)
            rows[key[:31]] = {'pos': _POS_CODE[s.pos], 'offset': s.offset, 'vec19': s.vector(),
                              'depth_weight': s.depth_weight}
        return rows


_BASE_CACHE: Dict[str, Dict[str, int]] = {}


def _base_entry_offsets(path: str) -> Dict[str, int]:
    if path not in _BASE_CACHE:
        _BASE_CACHE[path] = {k: v['offset'] for k, v in read_c_store(path)['wn'].items()}
    return _BASE_CACHE[path]


# ── monad3_c.bin: read and repack ──────────────────────────────────────────
_HDR = struct.Struct('<8s6I16d13Q')
_BK = struct.Struct('<32sB3xI19hf')


def read_c_store(path: str) -> dict:
    """Parse the C-native store into its parts (names, record table, wordnet table, raw sections)."""
    with open(path, 'rb') as f:
        data = f.read()
    v = _HDR.unpack_from(data, 0)
    magic, ver, n_words, n_eng, n_wn, n_phon, nnz = v[:7]
    psi = v[7:23]
    (o_blob, o_rec, o_beta, o_E, o_age, o_fire, o_strat, o_rowptr, o_col, o_w, o_wn, o_phix, o_phblob) = v[23:]
    assert magic.rstrip(b'\x00') == b'MONAD3C'
    names = data[o_blob:o_rec].rstrip(b'\x00').split(b'\x00') if n_words else []
    # the blob is padded to 8 bytes after the last NUL; split on NUL and drop the padding tail
    names = [x.decode('utf-8') for x in data[o_blob:o_blob + (o_rec - o_blob)].split(b'\x00')[:n_words]]
    rec = [struct.unpack_from('<iiii', data, o_rec + i * 16) for i in range(n_words)]
    wn = {}
    for i in range(n_wn):
        e = _BK.unpack_from(data, o_wn + i * _BK.size)
        wn[e[0].rstrip(b'\x00').decode('utf-8')] = {'pos': e[1], 'offset': e[2], 'vec19': list(e[3:22]),
                                                      'depth_weight': e[22]}
    return {'data': data, 'header': v, 'names': names, 'rec': rec, 'wn': wn, 'n_words': n_words,
            'n_eng': n_eng, 'n_wn': n_wn, 'n_phon': n_phon, 'nnz': nnz, 'psi': psi,
            'offs': dict(blob=o_blob, rec=o_rec, beta=o_beta, E=o_E, age=o_age, fire=o_fire, strat=o_strat,
                         rowptr=o_rowptr, col=o_col, w=o_w, wn=o_wn, phix=o_phix, phblob=o_phblob)}


def _pad8(buf: bytearray) -> None:
    while len(buf) % 8:
        buf.append(0)


def repack_monad3c(src: str, dst: str, rows: Dict[str, dict]) -> dict:
    """Write `dst` = `src` with the WordNet table updated/extended by `rows` (key -> pos/offset/vec19/depth_weight).
    New keys join the unified word table. Everything else (English field, A-matrix, phonetic) is copied byte for
    byte. `src` is never modified."""
    assert os.path.abspath(src) != os.path.abspath(dst), 'refusing to overwrite the source store'
    st = read_c_store(src)
    data, o = st['data'], st['offs']
    wn = dict(st['wn'])
    new_keys = [k for k in rows if k not in wn]
    wn.update(rows)
    old_rec = {st['names'][i]: st['rec'][i] for i in range(st['n_words'])}
    names = sorted(set(st['names']) | set(rows))
    wn_keys = sorted(wn)
    wn_pos = {k: i for i, k in enumerate(wn_keys)}

    def section(start, end):
        return data[start:end]

    sizes = dict(beta=st['n_eng'] * 8, E=st['n_eng'] * 8, age=st['n_eng'] * 4, fire=st['n_eng'] * 4,
                 strat=st['n_eng'] * 4, rowptr=(st['n_eng'] + 1) * 4, col=st['nnz'] * 4, w=st['nnz'] * 4)
    keep = {k: section(o[k], o[k] + sizes[k]) for k in sizes}
    phix = section(o['phix'], o['phblob'])
    phblob = section(o['phblob'], len(data))

    out = bytearray(b'\x00' * (_HDR.size + (8 - _HDR.size % 8) % 8))
    _pad8(out)
    off_blob = len(out)
    enc = [n.encode('utf-8') for n in names]
    name_off, acc = [], 0
    for b in enc:
        name_off.append(acc)
        acc += len(b) + 1
    out += b'\x00'.join(enc) + b'\x00'
    _pad8(out)
    off_rec = len(out)
    for i, nm in enumerate(names):
        e, p = (old_rec[nm][1], old_rec[nm][3]) if nm in old_rec else (-1, -1)     # rec = (name_off, eng, wn, phon)
        out += struct.pack('<iiii', name_off[i], e, wn_pos.get(nm, -1), p)
    offs = {}
    for k in ('beta', 'E', 'age', 'fire', 'strat', 'rowptr', 'col', 'w'):
        _pad8(out)
        offs[k] = len(out)
        out += keep[k]
    _pad8(out)
    off_wn = len(out)
    for k in wn_keys:
        r = wn[k]
        out += _BK.pack(k.encode('utf-8')[:31], r['pos'], r['offset'], *r['vec19'], r['depth_weight'])
    _pad8(out)
    off_phix = len(out)
    out += phix
    _pad8(out)
    off_phblob = len(out)
    out += phblob
    hdr = _HDR.pack(b'MONAD3C\x00', st['header'][1], len(names), st['n_eng'], len(wn_keys), st['n_phon'], st['nnz'],
                    *st['psi'], off_blob, off_rec, offs['beta'], offs['E'], offs['age'], offs['fire'], offs['strat'],
                    offs['rowptr'], offs['col'], offs['w'], off_wn, off_phix, off_phblob)
    out[:len(hdr)] = hdr
    with open(dst, 'wb') as f:
        f.write(out)
    return {'dst': dst, 'words_before': st['n_words'], 'words_after': len(names), 'wn_before': st['n_wn'],
            'wn_after': len(wn_keys), 'new_keys': new_keys, 'replaced': [k for k in rows if k in st['wn']]}
