#!/usr/bin/env python3
"""19D_rotary_boxkite_monad.py — wiring FourthAgePapers/ScalarContextPropagation's
own claim into a real, running monad, not just a paper claim and a set of
isolated test scripts.

Cody, 2026-09-21: "lets wire everything together as the paper claims into the
full structure with the sentence constructor in a new monad. start with
rotary_rerun_boxkite_monad.py code... i want that scalar used to track actual
contextual fits from monad3_c.bin... i want the context boxkite behind each
word actually used and tested to work, before updating ptol.c for testing.
the Mind's Eye is where the context operations should happen...context isn't
just gathered, or assumed, it's also created."

Starts from `rotary_rerun_boxkite_monad.py` — same Eye/Hands/BoxKite reuse
discipline, not reinvented, not a third Eye/Hands pair. What's actually new:

  1. `Monad3CStore` — a real, live reader for `monad3_c.bin`'s WordNet
     section (the C-native packed format §7/§9/§13 of the paper actually
     test against — NOT the separate Python-pickle `monad3.bin` the older
     monad's `self.store` reads). Honest finding made while building this:
     those two files have drifted (`monad3.bin` mtime 2026-09-03,
     `monad3_c.bin` mtime 2026-09-12) — not reconciled here, flagged, not
     silently papered over.
  2. `wordnet_boxkite.gamma_radial()` / `recover_gamma_radial()` — promoted
     out of notebook 05's own cell into real shipped code this same pass
     (it only ever existed inline in the notebook before this), checked
     against the paper's own recorded value (`windspeed("tree") =
     -0.151155`) before anything here was built on top of it.
  3. `NineteenDContext` / `NineteenDMindsEye.create_context()` — genuine
     context CREATION, not a passive gather: given a set of leaves, pulls
     each one's real, CURRENT 19-vector from `monad3_c.bin`, and honestly
     records which leaves were RECALLED from that live store versus freshly
     CREATED via a direct WordNet lookup when the store doesn't have them
     yet. That recalled-vs-created split is the same distinction Cody's own
     memory-curation practice makes explicit when working around a limited
     context window — applied here to the Mind's Eye instead of left
     implicit.
  4. The two real stub hooks already sitting in `engine/grammar/generate.py`
     — `Leaf.gamma` ("register scale (stub)", hardcoded 0.4) and `Ring.code`
     ("box-kite context hash (stub 0)") — filled with the real, live
     `gamma_radial` and `context_code` values this pass computes, not left
     at their defaults.

`ptol.c` is explicitly NOT touched by this pass. Python only, this file,
tested for real against the live store before anything moves to C.
"""
from __future__ import annotations

import mmap
import os
import struct
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from rotary_rerun_monad import (
    BoxKite, BoxKiteUnavailable, MindsEye, PapersHands,
    Ledger, Relation, Status, Fault,
)
import wordnet_boxkite as wb
from sentence_context import resolve_word_synset

import sys
sys.path.insert(0, os.path.dirname(__file__))
from engine.grammar.generate import (                      # noqa: E402
    ParseSpec, Leaf, Ring, Sentence, Slot,
    structure_phase, fill_phase, linearize, check,
)


# ═══════════════════════════════════════════════════════════════════════════
#  Monad3CStore — a real, live reader for monad3_c.bin's WordNet section
# ═══════════════════════════════════════════════════════════════════════════

_BK_STRUCT = struct.Struct('<32sB3xI19hf')      # BoxKiteEntry, 82 bytes — must
                                                 # match monad_combine.py's own
_HDR_STRUCT = struct.Struct('<8s6I16d13Q')
NREL = len(wb.RELATION_METHODS)                 # 19


class Monad3CStore:
    """Reads `monad3_c.bin` directly, mmap'd — the same loader notebook 05's
    verified cell uses, ported here so it's real, reusable code instead of a
    one-off notebook cell. Builds a word -> 19-vector dict once, up front
    (146,743 words in ~0.4s per the notebook's own measured run — cheap
    enough to just do, not worth lazy-loading)."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.path.join(
            os.path.dirname(__file__), 'PtolC', 'monad3_c.bin')
        self.mtime: Optional[float] = None
        self._vectors: Dict[str, List[int]] = {}
        self.load_time_s: float = 0.0
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        self.mtime = os.path.getmtime(self.path)
        t0 = time.time()
        with open(self.path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            vals = _HDR_STRUCT.unpack_from(mm, 0)
            n_words = vals[2]
            off = vals[23:]
            o_blob, o_rec, o_wn = off[0], off[1], off[10]
            rec = struct.Struct('<iiii')

            def name(o: int) -> str:
                e = mm.find(b'\x00', o_blob + o)
                return mm[o_blob + o:e].decode('utf-8', 'replace')

            for i in range(n_words):
                noff, ei, wi, pi = rec.unpack_from(mm, o_rec + i * 16)
                if wi < 0:
                    continue
                w = name(noff)
                entry = _BK_STRUCT.unpack_from(mm, o_wn + wi * _BK_STRUCT.size)
                v = list(entry[3:3 + NREL])
                if any(v):
                    self._vectors[w] = v
            mm.close()
        self.load_time_s = time.time() - t0

    def __len__(self) -> int:
        return len(self._vectors)

    def __contains__(self, word: str) -> bool:
        return word in self._vectors

    def vector_for(self, word: str) -> Optional[List[int]]:
        return self._vectors.get(word)

    def words(self):
        return self._vectors.keys()

    def freshness_days(self) -> Optional[float]:
        if self.mtime is None:
            return None
        return (time.time() - self.mtime) / 86400.0


# ═══════════════════════════════════════════════════════════════════════════
#  NineteenDContext — the thing the Mind's Eye actually CREATES, not just reads
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class NineteenDContext:
    leaves: List[str]
    vectors: Dict[str, List[int]] = field(default_factory=dict)
    sources: Dict[str, str] = field(default_factory=dict)    # 'recalled'|'created'|'unknown'
    root_vector: List[int] = field(default_factory=lambda: [0] * NREL)
    gamma_by_leaf: Dict[str, Optional[float]] = field(default_factory=dict)
    root_gamma: Optional[float] = None

    def contextual_fit(self, word: str) -> Optional[float]:
        """1.0 = the candidate's own gamma_radial sits exactly on this
        context's root gamma; 0.0 = maximally far (gamma_radial's own range
        is (-1,1), so max separation is 2). None if either side has no
        defined gamma (an all-zero-relation word, or a word not resolvable
        at all)."""
        if self.root_gamma is None:
            return None
        v = self.vectors.get(word)
        if v is None:
            v, _src = _resolve_vector(word, None)
            if v is None:
                return None
        g = wb.gamma_radial(v)
        if g is None:
            return None
        return max(0.0, 1.0 - abs(g - self.root_gamma) / 2.0)

    def summary(self) -> str:
        recalled = sum(1 for s in self.sources.values() if s == 'recalled')
        created = sum(1 for s in self.sources.values() if s == 'created')
        unknown = sum(1 for s in self.sources.values() if s == 'unknown')
        return (f"{len(self.leaves)} leaves: {recalled} recalled (live store), "
                f"{created} created (fresh WordNet lookup), {unknown} unresolved  "
                f"root_gamma={self.root_gamma}")


def _resolve_vector(word: str, store: Optional[Monad3CStore]
                     ) -> Tuple[Optional[List[int]], str]:
    """RECALLED: already in the live store. CREATED: not in the store, but a
    real WordNet synset exists for it — a fresh reading, not a stored memory,
    same distinction Cody's own context-window workarounds make. UNKNOWN:
    neither — no synset resolves at all."""
    if store is not None:
        v = store.vector_for(word)
        if v is not None:
            return v, 'recalled'
    syn = resolve_word_synset(word)
    if syn is not None:
        return wb.context_vector(syn), 'created'
    return None, 'unknown'


# ═══════════════════════════════════════════════════════════════════════════
#  NineteenDMindsEye — MindsEye, extended with real context CREATION
# ═══════════════════════════════════════════════════════════════════════════

class NineteenDMindsEye(MindsEye):
    """Everything MindsEye already does (snapshot, lit_struts, evaluate,
    generations_present) is untouched — this only ADDS the operation that
    was missing: creating a working context from raw leaves, rather than
    only ever reading a snapshot of one that already existed."""

    def __init__(self, store: Monad3CStore, kite: Optional[BoxKite] = None) -> None:
        super().__init__(kite)
        self.store = store

    def create_context(self, leaves: List[str]) -> NineteenDContext:
        ctx = NineteenDContext(leaves=list(leaves))
        root = [0] * NREL
        for leaf in leaves:
            v, src = _resolve_vector(leaf, self.store)
            ctx.sources[leaf] = src
            if v is None:
                ctx.gamma_by_leaf[leaf] = None
                continue
            ctx.vectors[leaf] = v
            ctx.gamma_by_leaf[leaf] = wb.gamma_radial(v)
            root = [a + b for a, b in zip(root, v)]           # the composter,
        ctx.root_vector = root                                 # Phase 32/31
        ctx.root_gamma = wb.gamma_radial(root)
        return ctx


# ═══════════════════════════════════════════════════════════════════════════
#  RotaryBoxKite19D — the monad itself
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Encounter19D:
    text: str
    surface: str
    context: NineteenDContext
    ring_code: int
    slot_gammas: Dict[str, float]
    verdict: str
    licensed: bool


class RotaryBoxKite19D:
    """One Monad. Eye/Hands/BoxKite reused exactly as
    `rotary_rerun_boxkite_monad.py` established — no third pair, no extra
    thread layer. What this class adds is wiring the real Gamma-Radial
    Windspeed into the real sentence constructor's own stub hooks."""

    def __init__(self, store_path: Optional[str] = None) -> None:
        self.store = Monad3CStore(store_path)
        try:
            self._eye_obj = NineteenDMindsEye(self.store)
            self._hands_obj = PapersHands()
            self.box_kite: Optional[BoxKite] = BoxKite.between(
                self._eye_obj, self._hands_obj)
            self._kite_error: Optional[str] = None
        except BoxKiteUnavailable as exc:
            self._eye_obj = NineteenDMindsEye(self.store)
            self._hands_obj = PapersHands()
            self.box_kite = None
            self._kite_error = str(exc)

    def process_input(self, spec: ParseSpec, depth: str = 'surface') -> Encounter19D:
        leaves = list(spec.topic_lemmas)
        if spec.subject_hint:
            leaves = [spec.subject_hint] + leaves
        ctx = self._eye_obj.create_context(leaves)

        # ── patch the real windspeed into ParseSpec.topic_gamma before the
        # real pipeline runs — this is the actual fill of the stub the
        # subject-hint Leaf gets built with (generate.py:262).
        if ctx.root_gamma is not None:
            spec = ParseSpec(speech_act=spec.speech_act, verb=spec.verb,
                             subject_hint=spec.subject_hint,
                             focus_hint=spec.focus_hint,
                             topic_gamma=ctx.root_gamma,
                             topic_lemmas=spec.topic_lemmas)

        sent = structure_phase(spec, depth)
        sent = fill_phase(sent, spec, depth)

        # ── patch every filled Leaf's stub gamma with its real contextual
        # fit against this turn's created context, and the Ring's stub
        # code with the real context_code of the ring's own anchor verb.
        slot_gammas: Dict[str, float] = {}
        for ring in [sent.main] + list(sent.subs):
            anchor_syn = resolve_word_synset(ring.anchor)
            if anchor_syn is not None:
                ring.code = wb.context_code(anchor_syn) % (1 << 31)  # fits a real int field
            for slot in ring.slots:
                if isinstance(slot.filler, Leaf):
                    fit = ctx.contextual_fit(slot.filler.lemma)
                    if fit is not None:
                        slot.filler.gamma = fit
                        slot_gammas[slot.filler.lemma] = fit

        surface = linearize(sent)
        verdict = check(sent)
        return Encounter19D(
            text=spec.verb, surface=surface, context=ctx,
            ring_code=sent.main.code, slot_gammas=slot_gammas,
            verdict=verdict['verdict'], licensed=verdict['licensed'])


if __name__ == '__main__':
    monad = RotaryBoxKite19D()
    print(f"Monad3CStore: {len(monad.store):,} words, loaded in "
          f"{monad.store.load_time_s:.2f}s, file is "
          f"{monad.store.freshness_days():.1f} days old "
          f"(mtime {time.ctime(monad.store.mtime) if monad.store.mtime else '?'})")
    if monad.box_kite is None:
        print(f"[BoxKite UNAVAILABLE] {monad._kite_error}")
    else:
        print(f"BoxKite signature {monad.box_kite.signature}  "
              f"{monad.box_kite.n_struts} struts, {monad.box_kite.n_assessors} assessors")

    cases = [
        ParseSpec('what_does_X_do', 'converge', subject_hint='the series',
                  topic_lemmas=['series', 'limit', 'sum', 'value']),
        ParseSpec('define_X', 'be', subject_hint='a tree',
                  topic_lemmas=['tree', 'plant', 'wood', 'root']),
        ParseSpec('how', 'run', subject_hint='the engine',
                  topic_lemmas=['engine', 'machine', 'system']),
    ]
    for spec in cases:
        print(f"\n=== {spec.speech_act}  verb={spec.verb}  subject={spec.subject_hint!r} ===")
        enc = monad.process_input(spec)
        print(f"  {enc.context.summary()}")
        print(f"  ring_code={enc.ring_code}")
        print(f"  slot gammas (real contextual fit, not the 0.4 stub): {enc.slot_gammas}")
        print(f"  surface: {enc.surface}")
        print(f"  verdict: {enc.verdict}  licensed={enc.licensed}")
