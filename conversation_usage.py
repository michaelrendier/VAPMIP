#!/usr/bin/env python3
"""
conversation_usage.py -- the daemon's usage channel: what is said in the conversation becomes usage, senses and drift.   (Cody, 2026-11-25: "the daemon is go")

Harness.observe(text, cls, pair_id) is the one entry every user prompt and every assistant reply passes through (the same entry that drops the turn on the daemon FIFO).
It now also calls ConversationUsage.hear(), in-process and never raising:

    external  (the human)   -> UsageStore.observe   per-sense usage counts, co-occurrence, register: the user's own vocabulary as usage
                               LiveVocabulary.hear   "X is a kind of Y" -> new senses / edges in the append-only journal
                               comprehension cost (Wernicke) of the turn, remembered under pair_id
    internal  (assistant)   -> production cost (Broca) of the reply; the pair completes BWDrift.update -> channel `bw_correction`
    document / web          -> not the user's voice: no usage counts (the same rule EnglishStats keeps), journal hear only for documents.

Costs are bits = -log2 UsageStore.p_word (the user's usage mixed into general English; lambda = N/(N+200)): the probabilities of the compression reading.
State lives in PTOL_USAGE_DIR (default ~/.ptolemy/usage): usage.json (the store), vocab.jsonl (the sense journal, replayable), drift.jsonl (one line per turn pair).
PTOL_USAGE=0 switches it off.  The C daemon (PtolC/daemon.c) is untouched.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from typing import Any, Dict, Optional

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(H, 'Currentwork', 'UserState'))

TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")


class ConversationUsage:
    def __init__(self, directory: Optional[str] = None, use_nltk: bool = True):
        import bw_drift
        from vocab_store import UsageStore
        import live_vocabulary
        self.dir = directory or os.environ.get('PTOL_USAGE_DIR') or os.path.join(os.path.expanduser('~'), '.ptolemy', 'usage')
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, 'usage.json')
        self.store = UsageStore.load(self.path) if os.path.exists(self.path) else UsageStore()
        self.vocab = live_vocabulary.LiveVocabulary(journal_path=os.path.join(self.dir, 'vocab.jsonl'), use_nltk=use_nltk)
        self.drift = bw_drift.BWDrift(); self.pending: Dict[str, float] = {}; self.last: Optional[Dict[str, Any]] = None
        self.channels: Dict[str, Any] = {'bw_correction': 0.0}

    def bits_per_word(self, text: str) -> float:
        ws = [w.lower() for w in TOK.findall(text)]
        return sum(-math.log2(self.store.p_word(w)) for w in ws) / len(ws) if ws else 0.0

    def _save(self) -> None:
        tmp = self.path + '.tmp'; self.store.save(tmp); os.replace(tmp, self.path)

    def hear(self, prose: str, cls: str = 'external', pair_id: Optional[str] = None, register: Optional[str] = None) -> Optional[Dict[str, Any]]:
        out = None
        if cls == 'external':
            bits = self.bits_per_word(prose)                     # priced BEFORE it is counted: surprise against what the store knew
            self.store.observe(prose, register=register); self.vocab.hear(prose, source='external'); self._save()
            if pair_id: self.pending[pair_id] = bits
        elif cls == 'internal':
            bits = self.bits_per_word(prose)
            w = self.pending.pop(pair_id, None) if pair_id else None
            if w is not None and bits > 0 and w > 0:
                out = self.drift.update(w, bits); self.channels['bw_correction'] = out['bw_correction']; self.last = out
                with open(os.path.join(self.dir, 'drift.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps(out) + '\n')
        elif cls == 'document':
            self.vocab.hear(prose, source='document')
        return out
