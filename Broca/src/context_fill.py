#!/usr/bin/env python3
"""context_fill.py — every word, every time, learned again for the first time.

THE FORMAL DEFINITION OF THE LIST

"it, us, we, me, at, and, why" is not one class. Classified by WHERE THE
REFERENT IS relative to the context, it is four, and the boundary is decidable
rather than stylistic:

    PATHWAY    the referent is ALREADY IN the context      it, us, we, me
               resolution is a lookup; nothing is added

    SIGNPOST   the referent is a RELATION between two       at, and, of
               things already present
               binds; introduces no third thing

    PAYLOAD    the referent is NEW and supplied HERE        content words
               appends to what is known

    DEMAND     the referent is ABSENT and REQUIRED          why, who, what
               opens a slot that must be filled later

DEMAND is the one that breaks the frequency story. `why` is short and common
like `it`, but it does not resolve against the context — it declares that
something is missing. That is not a claim, it is an INTENTION: a declaration
of what must survive until it can be satisfied. Every other word on the list
reads the context; `why` writes an obligation into it.

LEARNED AGAIN FOR THE FIRST TIME

Not incremental accumulation, and not memoisation. Every occurrence is
processed at FULL strength, from scratch, as though the word had never been
seen. The word is not what is learned — the word is the index. What is learned
is THIS OCCURRENCE'S CONTEXT, and that has never been seen before even when
the word has.

So repetition does not decay the effort. What decays is the NOVELTY, because
each fresh reading overlaps more with what is already held. Full effort,
diminishing return, and the two are independent.

THE EVENT HORIZON

Novelty falls asymptotically and never reaches zero. There is no occurrence
after which a word is "known" — you approach the limit and never cross it,
which is what makes it a horizon rather than a finish line. Measured below:
the curve flattens, and the residual stays strictly positive.

If novelty ever hit exactly zero, learning would have to stop, and the loop
that makes speech self-referential would open. It does not, so it does not.

THE BASIS, AND WHY ORDER IS NOT OPTIONAL

Boehm-Jacopini (1966), the structured program theorem: any computable function
is expressible with

    SEQUENCE      one thing after another
    SELECTION     if / then / else
    ITERATION     while

Three, not seven. Boolean and bitwise are VALUES, not control. range_check is
selection. And SEQUENCE is one of the three, which is the formal statement of
"the order definitely matters" — order is not a property of the program, it is
a constructor of it. Two programs with the same statements in a different
order are different programs, the way two sentences with the same words in a
different order are different sentences.

python3 first. Port to PtolC/ only once a result is significant.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Set, Tuple

_ROOT = '/home/rendier/Projects/ThePlace'
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

__all__ = ['WordClass', 'classify', 'Reading', 'ContextFill', 'Basis']


# ═══════════════════════════════════════════════════════════════════════════
#  THE FOUR CLASSES — by referent location, not by frequency
# ═══════════════════════════════════════════════════════════════════════════

class WordClass(Enum):
    PATHWAY  = 'pathway'    # referent already in context      — reads
    SIGNPOST = 'signpost'   # relation between two present     — binds
    PAYLOAD  = 'payload'    # new referent supplied here       — appends
    DEMAND   = 'demand'     # referent absent, required later  — obliges

    @property
    def touches_long_path(self) -> bool:
        """Only PAYLOAD adds to identity. The others read, bind, or oblige."""
        return self is WordClass.PAYLOAD

    @property
    def declares_intention(self) -> bool:
        """Only DEMAND opens a slot that must survive until satisfied."""
        return self is WordClass.DEMAND


# Closed-class inventories. These are STIPULATED, which is honest: the class
# boundary is defined by referent location, and these are the English words
# that sit on each side of it. A different language needs a different table
# and the same four classes.
_PATHWAY = frozenset("""
    it its this that these those he she they them him her us we me you i
    here there then now one
""".split())

_SIGNPOST = frozenset("""
    at and or of to in on by for with from as but nor so yet
    into onto over under between through during before after
""".split())

_DEMAND = frozenset("""
    why who what when where how which whom whose whether
""".split())


def classify(word: str) -> WordClass:
    """Decidable, by table for the closed classes and by default for the rest.

    DEMAND is tested before PATHWAY because several demand words are formally
    ambiguous in English ("that" is a pathway, "what" a demand) and the
    obligation reading dominates when both are available.
    """
    w = word.lower().strip(".,;:!?'\"()[]")
    if w in _DEMAND:
        return WordClass.DEMAND
    if w in _PATHWAY:
        return WordClass.PATHWAY
    if w in _SIGNPOST:
        return WordClass.SIGNPOST
    return WordClass.PAYLOAD


# ═══════════════════════════════════════════════════════════════════════════
#  THE FILL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Reading:
    """One occurrence, read from scratch. Never merged with a previous one."""
    word:        str
    wclass:      WordClass
    occurrence:  int              # how many times this word has been READ
    context:     Tuple[str, ...]  # what surrounded it THIS time
    kites:       Tuple[int, ...]  # which box kites this reading lit
    novelty:     float            # fraction of this reading never seen before
    obligation:  Optional[str] = None   # DEMAND opens a slot

    def __str__(self) -> str:
        ob = f'  opens[{self.obligation}]' if self.obligation else ''
        return (f'{self.word:<12} {self.wclass.value:<9} #{self.occurrence:<4} '
                f'novelty {self.novelty:.6f}  kites {list(self.kites)}{ob}')


class ContextFill:
    """Reads every occurrence at full strength and measures what was new.

    The word is the index; the CONTEXT is the content. Two occurrences of the
    same word in different surroundings are two different events, and the
    second is not a repeat of the first — it is a first reading of something
    that happens to share a label.
    """

    N_KITES = 7
    PRIMES  = (2, 3, 5, 7, 11, 13, 17)     # one per box kite

    def __init__(self) -> None:
        self.seen_pairs: Set[Tuple[str, str]] = set()   # (word, context term)
        self.counts: Dict[str, int] = {}
        self.readings: List[Reading] = []
        self.obligations: List[Tuple[str, int]] = []     # (slot, reading index)
        self.kite_history: Dict[str, List[Tuple[int, ...]]] = {}
        self.coherence_of: Dict[str, float] = {}
        self.alpha_of: Dict[str, float] = {}

    @staticmethod
    def _coherence(prior: Sequence[Tuple[int, ...]],
                   now: Tuple[int, ...]) -> float:
        """How completely this reading's geometries agree with its history.

        The resultant of the kite indicator vectors, in [0, 1]. 1.0 means every
        reading of this word has lit exactly the same channels — full downhill,
        nothing opposing. 0 means they scatter and no direction is free.
        """
        if not prior:
            return 1.0                       # nothing to disagree with yet
        acc = [0.0] * ContextFill.N_KITES
        for ks in list(prior) + [now]:
            for k in ks:
                acc[k - 1] += 1.0
        total = sum(acc)
        if total == 0.0:
            return 0.0
        # concentration: how much mass sits in the channels this reading lit
        here = sum(acc[k - 1] for k in now)
        return here / total

    # ── the box kite lookup ──────────────────────────────────────────────
    def _kites_for(self, word: str, context: Sequence[str]) -> Tuple[int, ...]:
        """Which relational channels this reading lights.

        Deterministic in (word, context) so the same reading in the same
        surroundings always lights the same kites — the structure is fixed,
        only what passes through it varies.
        """
        h = 0
        for tok in (word,) + tuple(context):
            for ch in tok:
                h = (h * 131 + ord(ch)) & 0xFFFFFFFF
        return tuple(k for k in range(1, self.N_KITES + 1) if (h >> k) & 1) or (1,)

    def intention_code(self, kites: Sequence[int]) -> int:
        """The squarefree prime product — the Intention encoding, reused."""
        code = 1
        for k in kites:
            p = self.PRIMES[k - 1]
            if code % p:
                code *= p
        return code

    # ── the fill itself ──────────────────────────────────────────────────
    def fill(self, word: str, context: Sequence[str]) -> Reading:
        """Learn this occurrence AGAIN FOR THE FIRST TIME.

        Full effort every call. Nothing is skipped because the word was seen;
        what is measured is how much of THIS reading is new.
        """
        w = word.lower().strip(".,;:!?'\"()[]")
        wc = classify(w)
        self.counts[w] = self.counts.get(w, 0) + 1

        ctx = tuple(c.lower().strip(".,;:!?'\"()[]") for c in context)
        kites = self._kites_for(w, ctx)

        # NOVELTY HAS TWO COMPONENTS, AND ONLY ONE OF THEM SATURATES.
        #
        #   contextual   fresh (word, context-term) pairs. This CAN reach zero:
        #                a finite corpus exhausts its surroundings.
        #
        #   historical   the event's share of the chain it attaches to, 1/n.
        #                This can NEVER reach zero, because the nth event is
        #                always one of n and the chain head is always new.
        #
        # The horizon is the second one. Two occurrences in identical company
        # are still not the same event, because they attach at different points
        # of the history — which is what "learned again for the first time"
        # means operationally rather than poetically.
        #
        #     novelty = c + (1 - c) / n**alpha
        #
        # First reading: c=1, novelty 1. Thereafter it falls toward n^-alpha
        # and stays strictly positive for any alpha > 0. Since sum 1/n
        # diverges, TOTAL learning is unbounded while per-event novelty
        # vanishes: you never stop learning, and each lesson matters less.
        # Same harmonic structure as sum 1/p over the primes.
        #
        # THE DEPTH OF THE ASYMPTOTE IS THE COHERENCE — alpha.
        #
        # How fast the groove deepens is set by how completely the geometries
        # agree. A word whose readings light the SAME box kites every time is
        # running full downhill: every channel pulls the same way, the work is
        # free, and it grooves quickly. A word whose readings scatter across
        # kites is fighting itself, and it never becomes automatic however
        # often it is repeated.
        #
        # Which is MUSCLE MEMORY, exactly. A movement aligned with the body's
        # mechanics becomes automatic in a few hundred repetitions; a movement
        # that fights them stays effortful after thousands. Same curve, and
        # the exponent is the alignment.
        pairs = {(w, c) for c in ctx if c}
        fresh = pairs - self.seen_pairs
        c = (len(fresh) / len(pairs)) if pairs else 0.0

        prior = self.kite_history.setdefault(w, [])
        coh = self._coherence(prior, kites)
        prior.append(kites)

        alpha = 0.25 + 1.5 * coh          # depth of the groove
        n = self.counts[w]
        novelty = c + (1.0 - c) / (n ** alpha)
        self.alpha_of[w] = alpha
        self.coherence_of[w] = coh
        self.seen_pairs |= pairs

        r = Reading(word=w, wclass=wc, occurrence=self.counts[w],
                    context=ctx, kites=kites, novelty=novelty)

        if wc.declares_intention:
            r.obligation = f'{w}?'
            self.obligations.append((r.obligation, len(self.readings)))

        self.readings.append(r)
        return r

    # ── the horizon ──────────────────────────────────────────────────────
    def novelty_curve(self, word: str) -> List[float]:
        return [r.novelty for r in self.readings if r.word == word]

    def horizon_report(self, word: str) -> str:
        curve = self.novelty_curve(word)
        if not curve:
            return f'{word}: never read'
        out = [f'{word!r} read {len(curve)} times — novelty per occurrence']
        step = max(1, len(curve) // 12)
        for i in range(0, len(curve), step):
            bar = '#' * int(curve[i] * 40)
            out.append(f'   #{i+1:<5} {curve[i]:.6f}  {bar}')
        tail = [c for c in curve[len(curve)//2:]]
        out.append(f'   mean novelty, second half: {sum(tail)/len(tail):.9f}')
        out.append(f'   strictly positive throughout: {all(c > 0 for c in curve)}')
        out.append(f'   coherence {self.coherence_of.get(word, 0):.4f}'
                   f'  ->  groove depth alpha = {self.alpha_of.get(word, 0):.4f}')
        return '\n'.join(out)

    def unfilled(self) -> List[str]:
        """Slots opened by DEMAND and never satisfied."""
        return [slot for (slot, _) in self.obligations]


# ═══════════════════════════════════════════════════════════════════════════
#  THE BASIS — three constructors, and SEQUENCE is one of them
# ═══════════════════════════════════════════════════════════════════════════

class Basis:
    """Boehm-Jacopini: sequence, selection, iteration. That is the whole set.

    Recorded here so the claim is checkable rather than asserted: boolean and
    bitwise are VALUES and do not construct control flow; range_check is
    selection wearing a different name.
    """

    CONSTRUCTS = ('sequence', 'selection', 'iteration')
    NOT_CONSTRUCTS = {
        'boolean':     'a value type, not control flow',
        'bitwise':     'a value operation, not control flow',
        'range_check': 'selection, renamed',
        'finally':     'sequence with an unconditional tail',
    }

    @staticmethod
    def order_matters(a: Sequence[str], b: Sequence[str]) -> bool:
        """Same statements, different order — a different program.

        This is what makes SEQUENCE a constructor rather than a formatting
        choice: the set of statements does not determine the program.
        """
        return sorted(a) == sorted(b) and list(a) != list(b)


def main(argv: List[str]) -> int:
    cf = ContextFill()

    print('=' * 70)
    print('THE LIST, FORMALLY DEFINED — by where the referent is')
    print('=' * 70)
    for w in ('it', 'us', 'we', 'me', 'at', 'and', 'why'):
        c = classify(w)
        print(f'  {w:<6} {c.value:<9} long-path={str(c.touches_long_path):<5} '
              f'intention={c.declares_intention}')

    print()
    print('=' * 70)
    print('THE EVENT HORIZON — full effort every time, diminishing novelty')
    print('=' * 70)
    corpus = [
        'the rotor turns and the shaft turns with it',
        'the shaft turns and the rotor follows it',
        'why does the rotor turn at all',
        'the rotor turns because the shaft turns',
        'and the shaft turns and the rotor turns and it holds',
        'why the shaft turns is what the rotor knows',
        'the rotor and the shaft turn together at last',
        'it turns and it holds and the shaft is true',
    ] * 12

    for line in corpus:
        toks = line.split()
        for i, t in enumerate(toks):
            ctx = toks[max(0, i - 3):i] + toks[i + 1:i + 4]
            cf.fill(t, ctx)

    for w in ('turns', 'the', 'rotor'):
        print(cf.horizon_report(w)); print()

    print('MUSCLE MEMORY — groove depth is the coherence, not the count')
    print(f'  {"word":<10} {"reads":>6} {"coherence":>10} {"alpha":>7} {"final novelty":>14}')
    for w in sorted(cf.counts, key=lambda x: -cf.counts[x])[:10]:
        curve = cf.novelty_curve(w)
        print(f'  {w:<10} {cf.counts[w]:>6} {cf.coherence_of[w]:>10.4f} '
              f'{cf.alpha_of[w]:>7.4f} {curve[-1]:>14.9f}')

    print()
    print('DEMAND opens slots that are not claims:')
    print(f'  {len(cf.unfilled())} obligations opened by "why"')
    print('  a claim is satisfied by what is present; an obligation is not')

    print()
    print('=' * 70)
    print('THE BASIS')
    print('=' * 70)
    print(f'  constructs: {Basis.CONSTRUCTS}')
    for k, v in Basis.NOT_CONSTRUCTS.items():
        print(f'    {k:<12} {v}')
    a = ['read', 'decide', 'write']
    b = ['write', 'read', 'decide']
    print(f'\n  same statements, different order -> different program: '
          f'{Basis.order_matters(a, b)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
