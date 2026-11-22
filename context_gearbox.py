#!/usr/bin/env python3
"""
context_gearbox.py -- the Cyclic Context Gearbox: lossless, FIFO, odometer-style compaction of context over time.

Cody, 2026-11-21. The .clauderc files are a block and tackle: a gearbox of time and of freshness. Context 1 cycles into
context 2, and so on; each wheel holds the same information at a different compactness. This is that mechanism as an
engine object, used twice:

    DATA SELF   how Ptolemy knows what is happening to him (inputs, his own sayings, sensor faults, vocabulary changes)
    USER SELF   how the user responds to that (reactions, corrections, tone, acceptance): the user's side, in the same
                language (the cyclic context buffer for the user's input, as the Librarian is a data representation)

Odometer. Gear 0 holds raw events. When gear 0 holds more than `cap` records, its OLDEST `ratio` records are compacted into ONE
record of gear 1 (FIFO); when gear 1 overflows, its oldest `ratio` records compact into one record of gear 2; and so on. A
compacted record carries (a) a DIGEST (a short readable summary: counts, terms, tone, time span: the shortcut), (b) the whole
block, zlib-compressed (LOSSLESS), (c) a hash of the block. `reconstruct(record)` expands it back, recursively, to the original
raw events, so the first event of every train of thought is always returnable ("reconstructable from first principles").
The ledger (append-only JSONL, optional) holds the raw events; replaying it rebuilds the same gears (deterministic).

Tunable: `gears=[(cap, ratio), ...]` per box. A gear shift is a change of compactness, not a deletion. Nothing is renormalised and
nothing is discarded; "rescale" only changes how much detail is held at hand.

`SelfContexts` pairs the two boxes. Events carry a global sequence number; a user event may `responds_to` a Ptolemy event, so
`reaction_to(seq)` returns how the user reacted, and `thread(seq)` returns the whole train of thought from its first event, whatever
gear it now sits in. `shortcuts()` yields canonical environment-variable lines (CTX_DATA_G1=..., CTX_USER_G2=...) for the
.clauderc style of pulling a context block by name.
"""
from __future__ import annotations

import base64
import collections
import datetime
import hashlib
import json
import re
import zlib
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

_STOP = set("the a an of in on at for with by from and or but not to is are was were be it its this that i you he she we they".split())


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')


def _digest(events: List[dict], n_terms: int = 6) -> Dict[str, Any]:
    """The readable shortcut of a block: size, time span, kinds, most frequent terms, mean tone if the events carry one."""
    terms: collections.Counter = collections.Counter()
    kinds: collections.Counter = collections.Counter()
    tone = collections.defaultdict(float)
    nt = 0
    for e in events:
        kinds[e.get('kind', '?')] += 1
        for k in ('text', 'sentence', 'note'):
            v = e.get('payload', {}).get(k) if isinstance(e.get('payload'), dict) else None
            if isinstance(v, str):
                terms.update(w for w in re.findall(r"[a-z]{3,}", v.lower()) if w not in _STOP)
        tv = e.get('payload', {}).get('tone') if isinstance(e.get('payload'), dict) else None
        if isinstance(tv, dict):
            nt += 1
            for a, x in tv.items():
                tone[a] += float(x)
    return {'n': len(events), 'seq': [events[0]['seq'], events[-1]['seq']], 't': [events[0]['t'], events[-1]['t']],
            'kinds': dict(kinds), 'terms': [w for w, _ in terms.most_common(n_terms)],
            'tone': {a: round(x / nt, 3) for a, x in tone.items()} if nt else {}}


def _merge_digests(ds: List[Dict[str, Any]], n_terms: int = 6) -> Dict[str, Any]:
    terms: collections.Counter = collections.Counter()
    kinds: collections.Counter = collections.Counter()
    tone = collections.defaultdict(float)
    nt = 0
    n = 0
    for d in ds:
        n += d['n']
        kinds.update(d['kinds'])
        for i, w in enumerate(d['terms']):
            terms[w] += len(d['terms']) - i
        if d['tone']:
            nt += d['n']
            for a, x in d['tone'].items():
                tone[a] += x * d['n']
    return {'n': n, 'seq': [ds[0]['seq'][0], ds[-1]['seq'][1]], 't': [ds[0]['t'][0], ds[-1]['t'][1]], 'kinds': dict(kinds),
            'terms': [w for w, _ in terms.most_common(n_terms)],
            'tone': {a: round(x / nt, 3) for a, x in tone.items()} if nt else {}}


def _pack(items: List[dict], level: int) -> Tuple[str, str]:
    raw = json.dumps(items, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return base64.b64encode(zlib.compress(raw, level)).decode('ascii'), hashlib.sha256(raw).hexdigest()


def _unpack(blob: str, digest: str) -> List[dict]:
    raw = zlib.decompress(base64.b64decode(blob))
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('compacted block does not match its hash')
    return json.loads(raw.decode('utf-8'))


class Gearbox:
    """One odometer. gears = [(cap, ratio), ...]: gear i holds at most cap_i records; when it overflows, its oldest ratio_i
    records become one record of gear i+1. The last gear is the archive (never compacted further)."""

    def __init__(self, name: str, gears: Optional[List[Tuple[int, int]]] = None, ledger: Optional[str] = None,
                 clock: Callable[[], str] = _now):
        self.name = name
        self.spec = list(gears or [(32, 8), (16, 8), (16, 8)])
        self.gears: List[List[dict]] = [[] for _ in range(len(self.spec) + 1)]
        self.ledger = ledger
        self.clock = clock
        self.n_raw = 0
        self.raw_bytes = 0

    # ── intake ──────────────────────────────────────────────────────────
    def push(self, event: dict, _replay: bool = False) -> dict:
        """Add a raw event (a dict with at least seq, t, kind, payload). Triggers the odometer carries."""
        self.gears[0].append(event)
        self.n_raw += 1
        self.raw_bytes += len(json.dumps(event, sort_keys=True, ensure_ascii=False).encode('utf-8'))
        if self.ledger and not _replay:
            with open(self.ledger, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + '\n')
        self._carry()
        return event

    def _carry(self) -> None:
        for i, (cap, ratio) in enumerate(self.spec):
            while len(self.gears[i]) > cap:
                block = self.gears[i][:ratio]
                del self.gears[i][:ratio]
                self.gears[i + 1].append(self._compact(block, i + 1))

    def _compact(self, block: List[dict], level: int) -> dict:
        if level == 1:
            digest = _digest(block)
        else:
            digest = _merge_digests([b['digest'] for b in block])
        blob, h = _pack(block, 6 if level == 1 else 9)
        return {'gear': level, 'digest': digest, 'blob': blob, 'hash': h, 'span': digest['seq']}

    def replay(self, path: str) -> int:
        n = 0
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.push(json.loads(line), _replay=True)
                    n += 1
        return n

    # ── reading back ────────────────────────────────────────────────────
    def reconstruct(self, record: dict) -> List[dict]:
        """The original raw events inside a record (a raw event returns itself)."""
        if 'blob' not in record:
            return [record]
        out: List[dict] = []
        for item in _unpack(record['blob'], record['hash']):
            out.extend(self.reconstruct(item))
        return out

    def all_events(self) -> List[dict]:
        out: List[dict] = []
        for g in self.gears:
            for r in g:
                out.extend(self.reconstruct(r))
        return sorted(out, key=lambda e: e['seq'])

    def find(self, seq: int) -> Optional[dict]:
        """The raw event with this sequence number, wherever it now sits."""
        for g in self.gears:
            for r in g:
                if 'blob' not in r:
                    if r['seq'] == seq:
                        return r
                elif r['span'][0] <= seq <= r['span'][1]:
                    for e in self.reconstruct(r):
                        if e['seq'] == seq:
                            return e
        return None

    def sizes(self) -> Dict[str, Any]:
        stored = [sum(len(json.dumps(r, sort_keys=True, ensure_ascii=False).encode('utf-8')) for r in g) for g in self.gears]
        return {'records': [len(g) for g in self.gears], 'stored_bytes': stored, 'total_stored': sum(stored),
                'raw_bytes': self.raw_bytes, 'raw_events': self.n_raw,
                'ratio': (self.raw_bytes / sum(stored)) if sum(stored) else 1.0}

    def digests(self) -> List[List[Dict[str, Any]]]:
        return [[r['digest'] for r in g if 'digest' in r] for g in self.gears]

    def shortcuts(self, prefix: str = 'CTX') -> Dict[str, str]:
        """Canonical shortcut variables: one line per gear, the newest digest of that gear (gear 0: the last raw events)."""
        out: Dict[str, str] = {}
        for i, g in enumerate(self.gears):
            if not g:
                continue
            if i == 0:
                d = _digest(g[-min(len(g), 8):])
            else:
                d = _merge_digests([r['digest'] for r in g])
            out['%s_%s_G%d' % (prefix, self.name.upper(), i)] = '%d events seq %d-%d | %s%s' % (
                d['n'], d['seq'][0], d['seq'][1], ' '.join(d['terms']),
                (' | tone ' + ' '.join('%s=%.2f' % kv for kv in d['tone'].items())) if d['tone'] else '')
        return out


class SelfContexts:
    """The pair: DATA SELF (what happens to Ptolemy) and USER SELF (how the user responds), one global sequence."""

    def __init__(self, gears=None, ledger_dir: Optional[str] = None, clock: Callable[[], str] = _now):
        import os
        self.clock = clock
        self.seq = 0
        self.data = Gearbox('data', gears, ledger=os.path.join(ledger_dir, 'data.jsonl') if ledger_dir else None, clock=clock)
        self.user = Gearbox('user', gears, ledger=os.path.join(ledger_dir, 'user.jsonl') if ledger_dir else None, clock=clock)
        self._thread: Dict[int, int] = {}
        self._responses: Dict[int, List[int]] = collections.defaultdict(list)

    def _event(self, kind: str, who: str, responds_to: Optional[int], payload: dict) -> dict:
        self.seq += 1
        thread = self._thread.get(responds_to, responds_to) if responds_to is not None else self.seq
        self._thread[self.seq] = thread
        ev = {'seq': self.seq, 't': self.clock(), 'kind': kind, 'who': who, 'thread': thread, 'payload': payload}
        if responds_to is not None:
            ev['responds_to'] = responds_to
            self._responses[responds_to].append(self.seq)
        return ev

    def ptolemy(self, kind: str, responds_to: Optional[int] = None, **payload) -> int:
        """Record something that happened to / was done by Ptolemy (DATA SELF). Returns the sequence number."""
        return self.data.push(self._event(kind, 'ptolemy', responds_to, payload))['seq']

    def user_says(self, kind: str, responds_to: Optional[int] = None, **payload) -> int:
        """Record the user's input or reaction (USER SELF); responds_to = the Ptolemy event it answers."""
        return self.user.push(self._event(kind, 'user', responds_to, payload))['seq']

    def reaction_to(self, seq: int) -> List[dict]:
        """How the user reacted to Ptolemy's event `seq` (raw events, whatever gear they now sit in)."""
        return [e for s in self._responses.get(seq, []) for e in [self.user.find(s) or self.data.find(s)] if e]

    def thread(self, seq: int) -> List[dict]:
        """The whole train of thought containing `seq`, from its first event, in order, across both boxes."""
        t = self._thread.get(seq)
        evs = [e for e in self.data.all_events() + self.user.all_events() if e.get('thread') == t]
        return sorted(evs, key=lambda e: e['seq'])

    def shortcuts(self) -> Dict[str, str]:
        d = dict(self.data.shortcuts()); d.update(self.user.shortcuts()); return d

    def export_lines(self) -> List[str]:
        return ["export %s=%s" % (k, json.dumps(v)) for k, v in sorted(self.shortcuts().items())]
