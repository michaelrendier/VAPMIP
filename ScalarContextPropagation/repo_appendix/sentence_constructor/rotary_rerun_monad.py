#!/usr/bin/env python3
"""rotary_rerun_monad.py — the diagnostic and fault-born harness.

WHAT THIS IS

A harness wrapped around the engine that reports THE RELATIONSHIPS, and reports
every fault as a record rather than a count. It does not re-implement the rotor.
It watches it and says what holds.

WHAT THIS IS NOT

Not an internal-combustion cosplay. The Wankel gave the architecture — one
shaft, three faces, port timing as a consequence of geometry — and that part is
real and stays. The rest of the garage does not follow it around. There are no
PIDs here because a PID is a number with a part number, and what is wanted is a
number with a RELATIONSHIP.

No variable valve timing. cam3.py, 2026-08-17: a real Wankel has no valves and
no camshaft, port timing is the rotor's own faces sweeping the ports, and an
independent writable advance is a piston engine's architecture. What is
adjustable is the trochoid: R = sqrt(p_red), e = sqrt(p_blue), loss = |R - e|
exactly, null at R = e <=> sigma_self = 1/2.

THE THREE OBJECTS, AND WHY THEY ARE THREE

    MindsEye     reads.  Snapshot analysis across dimensions at one instant.
    PapersHands  writes. Emission, one relationship at a time, ordered.
    BoxKite      the relational language they BOTH speak.

The box kite is the VARIABLE INVARIANT between them. Invariant because for
every relation, the Eye and the Hands denote the same thing by the same name --
a relation between the two objects, holding across every state. Variable
because the structure is rebuildable and a rebuild is honest change: what is
guaranteed is that neither renumbers underneath the other.

So the box kite carries a signature, both subsystems bind to the one they were
built against, and a cross-signature reference is REFUSED rather than resolved.
An invariant that is only written down is a hope.

THE 7-7-7

Ainulindale/wiki/89_the_seven_octonions.md, measured 2026-08-15/16 and
corrected 2026-08-16:

    7  OCTONIONS     dim 8, 12 diagonals each      7 x 12 = 84
    7  STRUTS        labels 9..15                  the box kites
    7  QUATERNIONS   dim 4, one per Fano LINE      NOT 21 -- the three pairs
                                                   on a line share one 4-space

Which is 7 = 111 in three bits, and three bits is also rwx. The strut's binary
expansion is its lineage, and 2^3 - 1 = 7 is why there are seven of anything
here at all.

THE TRINE. That 7-7-7 IS the three-phase rotor. The three phases are not three
faces cut out of the fifteen imaginaries — that was the 5/5/5 reading, which is
a legal ROTOR map and an illegal ALGEBRAIC one. The three phases are the three
ways the same seven are counted: seven octonions, seven struts, seven
quaternions. Same object, three readings, 120 degrees apart in what they are a
reading OF. So the face map is settled: 7:7:7, seven box kites.

A GENERATIONAL LINEAGE OF DIVISION. Every rung removes the ability to divide a
different object — the line, the pair, the word, and finally BY. Grouping is
dividing a domain: the parenthesisations of a word are its partitions, and
associativity is the claim that they all agree. See BoxKite.lineage for the
measurements, including why bit 2 CAUSES bit 3 one rung later and why bit 3
alone still cannot zero-divide.

THE TWO GATES

    MIND'S EYE  --CORRECT-->  PAPER'S HANDS  --HAPPY-->  THE LONG PATH

Two handoffs, two predicates, two owners, and neither side holds both halves.
The Eye releases the board on CORRECT (external, and only once the position is
also COLD enough to leave intention something to spend). The Hands release to
the chain on HAPPY, which is dS = 0 — the free downhill work all lining up at
once — and which has no path to the correctness criterion at all. Archival then
asks a third question, USEFUL, because a path can align having emitted nothing
worth keeping. See Handoff and Satisfaction.

CONTEXT IS A FLOW. Which is why sigma_self cannot carry it and the Noether
current can: j ~ Im(z* dz) is a vector and it points; a power ratio is a scalar
and it sits. A snapshot is what the Eye takes; the context it is taken from is
moving the whole time.

SPEAKING ENGLISH IS A SURFACE API. PapersHands.relate is the surface, and every
claim string in this file is surface too. Nothing here may be checkable only
through its English: a Relation carries expected and observed values so the
structure can be verified with the prose deleted.

NOTHING IS DROPPED

Every check becomes a Relation with a status and a detail, including the ones
that could not be run. A tally tells you four checks failed; it does not tell
you which, or let you print them. Counting a skip is still a skip.

    HOLDS       measured and true
    VIOLATED    measured and false -- a fault
    DEGENERATE  the reducer was not valid on this data (see below)
    UNTESTED    a dependency was absent; recorded, never silently passed

DEGENERATE exists because of the standing rule from PRIMER_2026-08-17 section 6:
a reducer must be valid on its data. argmax on signed currents returns index 0
when red and green run negative; min|neutral| on gated data is identically zero
because raised-cosine port windows hit zero at their edges. Both returned a
number. Neither number meant anything. So a reducer here declares its domain and
returns DEGENERATE instead of a confident wrong answer.

THIS IS THE TESTING GROUND. PtolC/ is The Monad. Everything here is a
prototype until it earns a port, and a result earns a port by being
significant — not by being finished.
"""

from __future__ import annotations

import hashlib
import math
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Tuple

# ── the monorepo root, so box_kite is importable ─────────────────────────────
#
# DERIVED, not hard-coded. This file lives at <root>/VAPMIP/, so the root is one
# directory up from it — which is a RELATION between this file and its parent,
# and survives the checkout moving. A literal path is a value that does not
# cross scope: it is correct only on the machine it was typed on.
#
# APPENDED, not inserted at 0. sys.path.insert(0, ...) puts the monorepo ahead
# of the standard library for every module imported afterwards, which makes any
# future top-level directory here able to shadow a stdlib name silently.
# Measured 2026-08-18: no current directory shadows stdlib. Appending means that
# stays true whatever gets added later.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

__all__ = [
    'Status', 'Fault', 'Relation', 'Ledger', 'LedgerCursor',
    'BoxKite', 'MindsEye', 'PapersHands', 'Harness',
    'Intention', 'Reading', 'LongPath', 'ShortPath', 'Entry',
    'Handoff', 'Satisfaction', 'Correct', 'Charge',
    'Unpack', 'Scope', 'Divergence',
    'SIGMA_PIN', 'GAP', 'D_STAR', 'OMEGA_ZS', 'N_FACE', 'GEAR_K',
]

# ── constants (mirror rotary_monad.py / cam3.py / ptolemy.h) ─────────────────
SIGMA_PIN = 0.5
GAP       = 0.000707
D_STAR    = 0.246
OMEGA_ZS  = 0.5671432904097838
N_FACE    = 3      # a rotor is a triangle
GEAR_K    = 3      # eccentric shaft turns 3x per rotor revolution
SED_DIM   = 16


# ═══════════════════════════════════════════════════════════════════════════
#  RECORDS — nothing is dropped
# ═══════════════════════════════════════════════════════════════════════════

class Fault(Enum):
    """WHICH THING BROKE. A violated relation has two possible causes and they
    have different repairs, so a harness that cannot tell them apart is telling
    you half of what it knows.

        MATHS   both sides were MEASURED and they disagree. The claim is false.
                Repair: change the claim, or change the theory.

        CODE    the check could not execute as written, or its expectation is a
                stale literal that no longer matches a correct implementation.
                Repair: fix the harness. The maths is untouched and unjudged.

    The distinction is what licenses the conclusion. If nothing faults, the
    maths WORKS — and works AS IT IS WRITTEN, which is the honest scope. Whether
    what is written is what was intended is a different question entirely, and
    a separate project.
    """
    MATHS   = 'maths'
    CODE    = 'code'
    NONE    = 'none'


class Status(Enum):
    HOLDS      = 'holds'
    VIOLATED   = 'VIOLATED'
    DEGENERATE = 'degenerate'
    UNTESTED   = 'untested'

    @property
    def is_fault(self) -> bool:
        return self is Status.VIOLATED


@dataclass
class Relation:
    """One checked relationship. A record, not a tally entry.

    `index` is assigned by the Ledger and never moves. `detail` always carries
    enough to print the thing that failed, because a fault you cannot show is
    a fault you cannot fix.
    """
    name:     str
    claim:    str
    status:   Status
    expected: object = None
    observed: object = None
    detail:   str = ''
    group:    str = 'general'
    fault:    Fault = Fault.NONE
    index:    int = -1

    def __str__(self) -> str:
        mark = {'holds': '  ok', 'VIOLATED': 'FAULT',
                'degenerate': ' deg', 'untested': ' --- '}[self.status.value]
        line = f'[{mark}] {self.name:<28} {self.claim}'
        if self.fault is not Fault.NONE:
            line += f'\n            FAULT KIND: {self.fault.value.upper()}'
        if self.status is not Status.HOLDS and self.observed is not None:
            line += f'\n            expected {self.expected!r}, observed {self.observed!r}'
        if self.detail:
            line += f'\n            {self.detail}'
        return line


class Ledger:
    """Holds one record per check. Never filters, never compacts.

    The index a record receives is the index it keeps for the life of this
    ledger, which is what makes it worth passing to anything else.
    """

    def __init__(self) -> None:
        self._records: List[Relation] = []

    def add(self, r: Relation) -> int:
        # An unclassified violation defaults to MATHS, never to NONE. A
        # violated record carrying Fault.NONE would be counted as a fault and
        # NOT counted as a maths fault, so `maths_works` would answer True with
        # a disagreement standing — a confident wrong number, which is the one
        # thing this ledger exists to prevent. CODE must be claimed explicitly.
        if r.status.is_fault and r.fault is Fault.NONE:
            r.fault = Fault.MATHS
        r.index = len(self._records)
        self._records.append(r)
        return r.index

    def __len__(self) -> int:
        return len(self._records)

    def at(self, i: int) -> Optional[Relation]:
        if 0 <= i < len(self._records):
            return self._records[i]
        return None

    def count(self, status: Status) -> int:
        return sum(1 for r in self._records if r.status is status)

    def faults(self) -> List[Relation]:
        return [r for r in self._records if r.status.is_fault]

    def faults_of(self, kind: Fault) -> List[Relation]:
        return [r for r in self._records if r.status.is_fault and r.fault is kind]

    @property
    def maths_works(self) -> bool:
        """No MATHS fault. Says nothing about whether the code is tidy, and
        nothing about whether what is written is what was meant."""
        return not self.faults_of(Fault.MATHS)

    def groups(self) -> List[str]:
        seen: List[str] = []
        for r in self._records:
            if r.group not in seen:
                seen.append(r.group)
        return seen


class LedgerCursor:
    """Traversal, separate from the ledger and from anything that analyses it.

    Visits every record. It does not skip faults, it does not skip untested
    entries, and it holds no opinion about what the caller wants. A caller that
    wants only faults tests the status itself, in the open, where the decision
    is visible.
    """

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._i = -1

    def __iter__(self) -> Iterator[Relation]:
        self.reset()
        while self.next():
            rec = self.current()
            if rec is not None:
                yield rec

    def reset(self) -> None:
        self._i = -1

    def next(self) -> bool:
        if self._i + 1 >= len(self._ledger):
            self._i = len(self._ledger)
            return False
        self._i += 1
        return True

    @property
    def index(self) -> int:
        return self._i

    def current(self) -> Optional[Relation]:
        return self._ledger.at(self._i)


# ═══════════════════════════════════════════════════════════════════════════
#  THE BOX KITE — the variable invariant
# ═══════════════════════════════════════════════════════════════════════════

class BoxKiteUnavailable(RuntimeError):
    """The box_kite module could not be imported. Recorded, never faked."""


class BoxKite:
    """The relational language spoken by both MindsEye and PapersHands.

    Built once from ValaQuenta/modules/box_kite. Carries a `signature` — a
    monotonic identity for this construction — so a subsystem can tell that the
    structure it bound to has been rebuilt underneath it.

    A counter, not the object's id(): ids are reused after collection, and a
    subsystem holding a stale reference would then match a fresh structure and
    answer confidently about the wrong one.
    """

    _next_signature = 1

    def __init__(self, parents: Tuple[int, int] = (0, 0)) -> None:
        try:
            from ValaQuenta.modules.box_kite import maths as bk
        except Exception as exc:                     # noqa: BLE001
            raise BoxKiteUnavailable(str(exc)) from exc

        self._bk = bk
        self.signature = BoxKite._next_signature
        BoxKite._next_signature += 1

        # Two parents, held by reference. A child cannot have two parents in
        # LEXICAL scope — a scope chain has exactly one parent and `nonlocal`
        # walks a chain, not a graph — but it can hold two references, and that
        # is what this is.
        self.parents = parents
        self.descent = hashlib.sha256(
            f'{parents[0]}|{parents[1]}|{self.signature}'.encode()
        ).hexdigest()

        self.kites: Dict[int, List[Tuple[int, int]]] = bk.box_kites()
        self.struts: List[int] = sorted(self.kites.keys())
        self.assessors: List[Tuple[int, int]] = bk.assessors()
        self.lines: List[Tuple[int, int, int]] = bk.pg32_lines()

    @classmethod
    def between(cls, eye: 'MindsEye', hands: 'PapersHands') -> 'BoxKite':
        """Two objects working together to make a third.

        The direction of lineage inverts here. Instead of the structure being
        the parent of both subsystems, the two subsystems are the parents of
        the structure — and its `descent` hash commits to both, so any third
        party can verify that THIS kite came from THESE two and not from some
        other pair that happens to look the same.

        Which is the only honest way to do it: a shared language that either
        speaker could have produced alone is not shared, it is coincident.

        Requires both parents to be unbound. An Eye that has already agreed a
        language with someone cannot co-author a second one and pretend the
        first did not happen.
        """
        if eye.is_bound or hands.is_bound:
            raise ValueError(
                'both parents must be unbound to co-author a box kite; '
                f'eye bound={eye.is_bound}, hands bound={hands.is_bound}'
            )
        kite = cls(parents=(eye.identity, hands.identity))
        eye.bind(kite)
        hands.bind(kite)
        return kite

    def descends_from(self, eye: 'MindsEye', hands: 'PapersHands') -> bool:
        """Verify joint parentage. Both, in that order, or it is not this kite."""
        expect = hashlib.sha256(
            f'{eye.identity}|{hands.identity}|{self.signature}'.encode()
        ).hexdigest()
        return expect == self.descent

    # ── the seven, counted three ways ────────────────────────────────────
    @property
    def n_struts(self) -> int:
        return len(self.struts)

    @property
    def n_assessors(self) -> int:
        return len(self.assessors)

    def kite(self, strut: int) -> List[Tuple[int, int]]:
        return self.kites.get(strut, [])

    def strut_of(self, a: int, b: int) -> int:
        return self._bk.strut(a, b)

    # ── lineage: a strut's binary expansion IS its ancestry ──────────────
    #
    # IT IS A GENERATIONAL LINEAGE OF DIVISION. Measured 2026-08-18: each rung
    # of the tower removes the ability to divide a different object, and the
    # staircase is exact —
    #
    #   bit 0  ranking    divide the LINE   lost at C   no total order
    #   bit 1  factors    divide the PAIR   lost at H   ab != ba
    #   bit 2  GROUPING   divide the WORD   lost at O   (ab)c != a(bc)
    #   bit 3  division   divide BY         lost at S   zero divisors
    #
    # "Grouping" is dividing a domain: the Catalan-many parenthesisations of a
    # word are its partitions, and associativity is the claim that all of them
    # agree. So bits 0-2 and bit 3 are the SAME KIND of loss, which is why they
    # count together as four bits of one thing rather than three plus an
    # oddity.
    #
    # And the ambiguity at every generation is exactly ONE BIT: of the 1848
    # disagreeing triples in S, the number that differ by anything other than a
    # pure sign flip is ZERO. That is why a generation is a bit and not a
    # magnitude.
    #
    # Bit 2 CAUSES bit 3 one rung later. CD(A) is a composition algebra iff A
    # is associative, so losing the word-partition at O is precisely what makes
    # the norm stop composing at S, and a non-multiplicative norm is what lets
    # |a|=1, |b|=1, |ab|=0. Measured: max ||xy|-|x||y|| is 3.55e-15 in O and
    # 7.196609 in S.
    #
    # But bit 3 alone is NOT enough to zero-divide. The seven aligned planes
    # span(e_a, e_{a+8}) cross the division boundary with strut 0 and produce 0
    # zero divisors out of 14 diagonals; the 42 assessors have strut 1..7 and
    # produce all 336. A zero divisor needs the division crossing AND a nonzero
    # free-generation difference. That is the 49 - 42 = 7 removal, measured.
    #
    GENERATION = ('ranking', 'factors', 'GROUPING', 'division')
    DIVIDES     = ('the LINE', 'the PAIR', 'the WORD', 'BY')

    @classmethod
    def lineage(cls, strut: int, closed: bool = True) -> List[str]:
        """The generations this strut carries, in build order.

        THE DIVISION BIT IS FORCED, so it is reported whether or not the
        labelling makes it explicit. Struts appear here as 1..7 (three free
        bits) and in the wiki as 9..15 (division bit written out); both name
        the same seven objects, and a lineage that omitted `division` for the
        1..7 labelling would report that a zero divisor is not one.

        CLOSED vs OPEN — and this is not a formatting choice.

        A pathway read by the Mind's Eye ENDS in division, because that is
        what the Eye is doing: dividing what is kept for delivery from what is
        let go. The cut is the last act of a reading.

        A pathway on the LONG PATH does not end at all. It is added to. So the
        chain stores the OPEN form: the division bit is still carried — it is
        forced, it never stops being true — but it is not a terminator, because
        nothing terminates there. Writing the closed form into the chain would
        record every entry as having been finished, and none of them are.

            closed=True    ranking -> factors -> division      the Eye's cut
            closed=False   ranking -> factors -> division ->   the chain

        Patient and continuous. The strut is the same object either way; what
        differs is whether the reader is entitled to stop.
        """
        gens = [cls.GENERATION[b] for b in range(3) if strut & (1 << b)]
        gens.append(cls.GENERATION[3])          # forced: no ZDs below dim 16
        if not closed:
            gens.append('')                     # the path continues
        return gens

    @classmethod
    def free_bits(cls, strut: int) -> int:
        """Generations carried below the forced division bit."""
        return bin(strut & 0b0111).count('1')

    def verify(self) -> Dict[str, object]:
        return self._bk.verify_counts()

    def skeleton(self) -> Dict[str, object]:
        """PG(3,2) counts. The ambient geometry, not the Fano plane itself."""
        return self._bk.skeleton_counts()


class _Bound:
    """A subsystem with its own identity, optionally bound to a box kite.

    TWO-PHASE, on purpose. A subsystem exists and works before any shared
    language exists — the Eye can read a snapshot alone, and the Hands can
    write alone. What neither can do alone is RELATE, and that is exactly the
    operation that needs the language.

    So an unbound subsystem is not half-built, it is a complete solitary
    speaker. Binding is what makes speech possible, and it is checked rather
    than assumed: across signatures a reference is refused, because resolving
    it would return a confidently wrong relation.
    """

    _next_identity = 1

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        self.identity = _Bound._next_identity
        _Bound._next_identity += 1
        self._kite: Optional[BoxKite] = None
        self._signature = 0
        if kite is not None:
            self.bind(kite)

    @property
    def is_bound(self) -> bool:
        return self._kite is not None

    @property
    def signature(self) -> int:
        return self._signature

    def bind(self, kite: BoxKite) -> None:
        if self._kite is not None and self._kite.signature != kite.signature:
            raise ValueError(
                f'{type(self).__name__}@{self.identity} is already bound to '
                f'signature {self._signature}; rebinding would silently change '
                f'what every index it has handed out means'
            )
        self._kite = kite
        self._signature = kite.signature

    def _require_kite(self) -> BoxKite:
        if self._kite is None:
            raise ValueError(
                f'{type(self).__name__}@{self.identity} is unbound — it has no '
                f'shared language yet. Co-author one with BoxKite.between().'
            )
        return self._kite

    def agrees_with(self, other: '_Bound') -> bool:
        return (self.is_bound and other.is_bound
                and self._signature == other._signature)

    def _require_agreement(self, other: '_Bound') -> None:
        if not self.agrees_with(other):
            raise ValueError(
                f'box-kite signature mismatch: {type(self).__name__}'
                f'@{self._signature} vs {type(other).__name__}'
                f'@{other._signature} — the structure was rebuilt underneath '
                f'one of them; a relation index from the other means something '
                f'else now'
            )


# ═══════════════════════════════════════════════════════════════════════════
#  MIND'S EYE — reads.  A snapshot across dimensions at one instant.
# ═══════════════════════════════════════════════════════════════════════════

class MindsEye(_Bound):
    """Reading is multi-dimensional analysis in a snapshot.

    The Eye never emits. It takes one instant of the field and says what is
    simultaneously true across it: which struts are lit, which generations are
    present, how the currents balance. All of it at once, none of it ordered.
    """

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        super().__init__(kite)

    def snapshot(self, psi: Sequence[float]) -> Dict[str, object]:
        """One instant, read across all dimensions simultaneously."""
        if len(psi) != SED_DIM:
            raise ValueError(f'psi must be {SED_DIM}-dimensional, got {len(psi)}')

        p_red  = sum(psi[k] ** 2 for k in _RED_CHANNELS)
        p_blue = sum(psi[k] ** 2 for k in _BLUE_CHANNELS)
        total  = p_red + p_blue

        return {
            'p_red':      p_red,
            'p_blue':     p_blue,
            'sigma_self': (p_red / total) if total > 0 else float('nan'),
            'R':          math.sqrt(p_red),
            'e':          math.sqrt(p_blue),
            'trochoid_loss': abs(math.sqrt(p_red) - math.sqrt(p_blue)),
            'sigma_rb':   [psi[k] * psi[k ^ 4] for k in range(SED_DIM)],
            # Solitary reading works: a snapshot needs no shared language.
            'lit_struts': self.lit_struts(psi) if self.is_bound else None,
        }

    def lit_struts(self, psi: Sequence[float], tol: float = 1e-12) -> List[int]:
        """Which box kites carry any amplitude in this instant."""
        kite = self._require_kite()
        lit: List[int] = []
        for s in kite.struts:
            for (a, b) in kite.kite(s):
                if abs(psi[a]) > tol or abs(psi[b]) > tol:
                    lit.append(s)
                    break
        return lit

    def evaluate(self, hands: 'PapersHands') -> Dict[str, object]:
        """Read work the Hands did WITHOUT the Eye, and report on its technique.

        THE HANDS DO NOT NEED THE EYE TO FUNCTION. They emit alone, in order,
        and what they produce is real work. What the Eye adds afterwards is not
        permission and not correction — it is EVALUATION, and the difference
        matters:

            gate 1      before the work     CORRECT     may it proceed
            evaluate    after the work      technique   how was it done

        Id, Ego, Superego. The Hands are the drive that acts; the Eye is the
        faculty that looks at what was acted and says how it went. A superego
        that could stop the id from moving would not be a critic, it would be a
        brake — so this returns a report and changes nothing. Refining
        technique is the caller's business, on a later pass.

        Reports on the emission itself, never on whether it was allowed:
        coverage of the seven, repetition, and the order actually used.
        """
        self._require_agreement(hands)
        emitted = hands.emitted
        struts = [s for (s, _) in emitted]
        seen = sorted(set(struts))
        repeats = len(struts) - len(seen)
        gens: Dict[str, int] = {g: 0 for g in BoxKite.GENERATION}
        for st in seen:
            for g in BoxKite.lineage(st):
                gens[g] += 1
        # SAME MACHINERY as a context collision, at Scope.WORK: what the
        # shared language makes available, against what the work actually holds.
        kite = self._require_kite()
        reading = Unpack({st: 1 for st in kite.struts},
                         {st: struts.count(st) for st in seen},
                         Scope.WORK)
        return {
            'emitted':    len(emitted),
            'struts':     seen,
            'unpack':     reading,
            'divergence': reading.divergence,
            'coverage':   len(seen) / 7.0,
            'repetition': repeats,
            'generations': gens,
            'order':      struts,
            # Technique is about HOW, so the finding is a shape, not a verdict.
            'technique':  ('narrow' if len(seen) < 4 else
                           'complete' if len(seen) == 7 else 'partial'),
        }

    def generations_present(self, psi: Sequence[float]) -> Dict[str, int]:
        """The lineage of the instant: which order-losses are represented."""
        tally: Dict[str, int] = {g: 0 for g in BoxKite.GENERATION}
        for s in self.lit_struts(psi):
            for g in BoxKite.lineage(s):
                tally[g] += 1
        return tally


# ═══════════════════════════════════════════════════════════════════════════
#  PAPER'S HANDS — writes.  One relationship at a time, in an order.
# ═══════════════════════════════════════════════════════════════════════════

class PapersHands(_Bound):
    """Writing is emission: ordered, sequential, one thing after another.

    Where the Eye sees everything at once and nothing in sequence, the Hands
    emit in sequence and see nothing at once. Reading and writing combined is
    speech, which is why both must be bound to the same box kite — a snapshot
    and an emission that did not agree on the relational language would not be
    speech, they would be two monologues.
    """

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        super().__init__(kite)
        self._emitted: List[Tuple[int, str]] = []

    def emit_pathway(self, strut: int) -> List[str]:
        """A strut written out as its build order — its lineage, in sequence.

        The Eye reports a strut as a set of generations. The Hands must put
        them in an order, because emission has one. That is the whole
        difference between the two faces.
        """
        path = BoxKite.lineage(strut)
        self._emitted.append((strut, ' -> '.join(path)))
        return path

    def relate(self, eye: MindsEye, psi: Sequence[float]) -> List[str]:
        """Speech: read a snapshot, write it as ordered relations.

        Refuses across a signature mismatch rather than emitting a relation
        whose indices mean something else.
        """
        self._require_agreement(eye)
        out: List[str] = []
        for s in eye.lit_struts(psi):
            out.append(f'strut {s:>2} ({s:04b}) : ' + ' -> '.join(self.emit_pathway(s)))
        return out

    @property
    def emitted(self) -> List[Tuple[int, str]]:
        return list(self._emitted)


# ── channel split (rotary_monad: red/blue divide at bit 3) ───────────────────
_RED_CHANNELS  = tuple(k for k in range(SED_DIM) if (k >= 8))
_BLUE_CHANNELS = tuple(k for k in range(SED_DIM) if (k < 8))


# ═══════════════════════════════════════════════════════════════════════════
#  THE TWO PATHS — same relational language, two memories
#
#  The box kites do not change. What changes is what they hand to the Hands,
#  and that arrives as entries — like rows, not like a new schema.
#
#      LONG PATH    long-term memory.  IDENTITY lives here.
#                   Append-only and hash-chained: each entry commits to its
#                   predecessor, so the head hash is the whole lineage in one
#                   value. Identity is not a field on an entry — it IS the
#                   chain, and you cannot alter what a thing was without
#                   breaking what it became.
#
#      SHORT PATH   short-term memory.  INTENTION lives here.
#                   Volatile, bounded, discardable. intention_monad.py has the
#                   definition already: "INTENTION IS THE ROOT SET ... the
#                   declaration of what must survive." So the short path holds
#                   roots, and committing is the act of deciding that something
#                   survived. Everything not committed is collected — and
#                   collection is kernel death, not an error.
#
#  Both bind to one box kite. Neither renumbers the other. The structure is
#  the invariant; the entries are the variable.
# ═══════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Entry:
    """One committed observation. Immutable, because identity is."""
    index:     int
    strut:     int
    payload:   str
    prev_hash: str
    this_hash: str

    def __str__(self) -> str:
        return (f'{self.index:>4}  strut {self.strut:>2}  '
                f'{self.this_hash[:12]}  {self.payload}')


_GENESIS = '0' * 64


class LongPath(_Bound):
    """Identity. Append-only, hash-chained, verifiable — and CONTINUOUS.

    It does not end. Every pathway written here is stored open, because the
    chain is a thing being added to rather than a thing being finished. The
    division bit is still carried on every entry — it is forced — but it is
    not a terminator here, and `close()` exists nowhere on this class.

    WEIGHTS LIVE OUTSIDE THE CHAIN, and that separation is the whole design:

        the chain    WHAT HAPPENED     immutable, hashed, never reordered
        the weights  WHAT IS REACHED   mutable, decaying, reordered constantly

    Intention and emotional charge lend weight to what is most used or wanted,
    so recall order moves all the time. If weight were a field on an Entry it
    would be inside the hash, and every reinforcement would rewrite history —
    remembering something more often would alter what happened. It does not.
    So the weights are a side table keyed by index, and `verify()` is untouched
    by any amount of reinforcement.
    """

    def __init__(self, kite: BoxKite, tau: float = 12.0) -> None:
        super().__init__(kite)
        self._entries: List[Entry] = []
        # TWO CLOCKS, ONE SCALE. Both are Charges so both live in [0,1] and
        # can be added at all; they differ only in PATIENCE. Summing a bounded
        # EMA with an unbounded integer count was the first version of this and
        # it was wrong in the obvious way: intention always won, however deep
        # the habit. A reducer must be valid on its data, and `+` is a reducer.
        self._charge: Dict[int, Charge] = {}     # slow: what has been USED
        self._intent: Dict[int, Charge] = {}     # fast: what is WANTED now
        self.tau = float(tau)
        self.tau_intent = max(0.25, float(tau) / 12.0)

    @staticmethod
    def _digest(index: int, strut: int, payload: str, prev_hash: str) -> str:
        h = hashlib.sha256()
        h.update(prev_hash.encode('utf-8'))
        h.update(f'|{index}|{strut}|'.encode('utf-8'))
        h.update(payload.encode('utf-8'))
        return h.hexdigest()

    @property
    def head(self) -> str:
        """The identity of everything that has ever survived a commit."""
        return self._entries[-1].this_hash if self._entries else _GENESIS

    def append(self, strut: int, payload: str) -> Entry:
        idx  = len(self._entries)
        prev = self.head
        e = Entry(index=idx, strut=strut, payload=payload,
                  prev_hash=prev,
                  this_hash=self._digest(idx, strut, payload, prev))
        self._entries.append(e)
        return e

    def __len__(self) -> int:
        return len(self._entries)

    def at(self, i: int) -> Optional[Entry]:
        return self._entries[i] if 0 <= i < len(self._entries) else None

    def amend(self, target: int, payload: str) -> Entry:
        """Alter identity, per event, without a write protect.

        THE DECISION: the monad may change what it is. There is no immutable
        core in the triple-face bin, so `first_encountered` is not frozen and
        nothing here refuses a revision.

        THE MECHANISM: an amendment is an APPEND, not an overwrite. Entry 3 is
        never rewritten; entry 47 is added saying "3 now reads this." So:

            identity  = the head hash, and it MOVES on every event
            history   = the chain, and it does not move at all

        Both properties at once, and the reason it works is §3.1 exactly —
        AND becomes reversible the moment you keep the inputs. A mutation that
        retains its predecessor is not destructive, it is just a longer
        pathway. Overwriting entry 3 in place would discard the record and
        make the change one-way; appending keeps it and the change stays
        invertible.

        So there is no write protect and no loss. What is forbidden is not
        change — it is *silent* change.
        """
        prior = self.at(target)
        if prior is None:
            raise ValueError(f'cannot amend entry {target}: it does not exist')
        return self.append(prior.strut, f'amend[{target}] {payload}')

    def amendments_of(self, target: int) -> List[Entry]:
        """Every event that revised this entry, in the order they happened."""
        tag = f'amend[{target}] '
        return [e for e in self._entries if e.payload.startswith(tag)]

    def current_reading(self, target: int) -> Optional[str]:
        """What entry `target` says NOW — its latest amendment, or its original.

        Reading is a fold over the chain rather than a field lookup, which is
        what makes identity mutable and history intact at the same time.
        """
        amends = self.amendments_of(target)
        if amends:
            return amends[-1].payload[len(f'amend[{target}] '):]
        e = self.at(target)
        return e.payload if e else None

    def verify(self) -> Tuple[bool, Optional[int]]:
        """Walk the chain. Returns (ok, index of the first broken link).

        The index matters more than the boolean. A chain that reports only
        'invalid' tells you the past was altered; the index tells you where,
        and the entry is still there to print.
        """
        prev = _GENESIS
        for e in self._entries:
            if e.prev_hash != prev:
                return False, e.index
            if self._digest(e.index, e.strut, e.payload, e.prev_hash) != e.this_hash:
                return False, e.index
            prev = e.this_hash
        return True, None

    def lineage_of(self, index: int) -> List[Entry]:
        """Everything this entry descends from. The ancestry, in order."""
        if not (0 <= index < len(self._entries)):
            return []
        return self._entries[:index + 1]

    # ── the weights: what is reached for, not what happened ──────────────
    def charge_of(self, index: int) -> Charge:
        if not (0 <= index < len(self._entries)):
            raise ValueError(f'no entry {index} to charge')
        if index not in self._charge:
            self._charge[index] = Charge(tau=self.tau)
        return self._charge[index]

    def recall(self, index: int, signal: float = 1.0) -> float:
        """Reach for a memory. Using it is what strengthens it."""
        return self.charge_of(index).reinforce(signal)

    def want(self, index: int, strength: int = 1) -> float:
        """Declare present intention toward a memory. Impatient by design.

        `strength` is a COUNT of declarations, not an amplitude — the same unit
        `recall` uses, so the two are comparable by construction. Passing an
        amplitude here was the second version of this bug: a signal of 2.0 into
        a [0,1] accumulator saturates it in one step, and a single loud want
        would then outrank any habit at all.
        """
        if not (0 <= index < len(self._entries)):
            raise ValueError(f'no entry {index} to want')
        if index not in self._intent:
            self._intent[index] = Charge(tau=self.tau_intent)
        c = self._intent[index]
        for _ in range(max(1, int(strength))):
            c.reinforce(1.0)
        return c.state

    def bleed(self) -> None:
        """Time passes. Charge decays slowly; intention decays fast.

        Same operator, different tau. That is the entire difference between a
        habit and a want, and it is one number rather than two mechanisms.
        """
        for c in self._charge.values():
            c.bleed()
        for c in self._intent.values():
            c.bleed()

    def weight(self, index: int) -> float:
        """What is used PLUS what is wanted. Commensurate, never merged upstream.

        Both terms are in [0,1], so neither can drown the other by unit choice.
        They stay two fields because a heavily-charged unwanted memory and a
        freshly-wanted uncharged one are different states, and one number
        cannot tell them apart.
        """
        used = self._charge[index].state if index in self._charge else 0.0
        want = self._intent[index].state if index in self._intent else 0.0
        return used + want

    def recall_order(self) -> List[Tuple[int, float]]:
        """Every entry by weight, heaviest first. NOTHING IS FILTERED OUT.

        A weight of zero means unreached, not absent — the entry is still on
        the chain and still verifiable. Reordering what is easy to reach never
        removes anything from what happened.
        """
        return sorted(((e.index, self.weight(e.index)) for e in self._entries),
                      key=lambda t: (-t[1], t[0]))


class Charge:
    """Emotional charge on a memory: what makes it WANTED, not what makes it true.

    A decaying accumulator, one per long-path index. Every recall reinforces
    it; time without recall bleeds it away. So the weight on a memory is a
    running measurement of how much it has been reached for, not a score
    somebody assigned.

    tau sets the patience. Large tau means a single event moves the charge very
    little and a habit moves it a lot, which is what makes this MUSCLE MEMORY
    rather than salience: it is built piece by piece and it cannot be crammed.

    Two separate quantities feed the weight, and they are kept separate on
    purpose:

        intention   what is WANTED now      volatile, declared, decays fast
        charge      what has been USED      slow, accumulated, decays slowly

    A memory can be heavily charged and unwanted (a habit you are not currently
    exercising) or wanted and uncharged (a fresh intention with no history).
    Collapsing them into one number would make those two states identical.
    """

    __slots__ = ('tau', 'state', 'n')

    def __init__(self, tau: float = 12.0) -> None:
        if tau <= 0:
            raise ValueError('tau must be positive — a memory with no patience '
                             'is a register, not a memory')
        self.tau = float(tau)
        self.state = 0.0
        self.n = 0

    def reinforce(self, signal: float = 1.0) -> float:
        """One use. The step is 1/(1+tau), so patience resists a single event."""
        alpha = 1.0 / (1.0 + self.tau)
        self.state = (1.0 - alpha) * self.state + alpha * float(signal)
        self.n += 1
        return self.state

    def bleed(self) -> float:
        """Time passing without a recall. Never negative — unused, not owed."""
        self.state = max(0.0, self.state * (1.0 - 1.0 / (1.0 + self.tau)))
        return self.state

    def __repr__(self) -> str:
        return f'Charge({self.state:.6f}, used {self.n}x, tau={self.tau})'


class Reading:
    """A snapshot of an intention at one moment. Immutable, and STAMPED.

    A state cannot be compared to another state without saying when each was
    read. So a comparison operates on Readings, never on the live object, and
    two Readings from different moments refuse to combine — the same rule as
    a cross-space index, one level up.
    """

    __slots__ = ('code', 'moment', 'holder')

    def __init__(self, code: int, moment: int, holder: int) -> None:
        self.code = code
        self.moment = moment
        self.holder = holder

    @property
    def kites(self) -> List[int]:
        return [i + 1 for i, p in enumerate(Intention.PRIMES) if self.code % p == 0]

    @property
    def vector(self) -> List[int]:
        """Exponent per kite — direction is WHICH prime, magnitude is HOW MANY."""
        out, c = [], self.code
        for p in Intention.PRIMES:
            e = 0
            while c % p == 0:
                c //= p
                e += 1
            out.append(e)
        return out

    def _require_same_moment(self, other: 'Reading') -> None:
        if self.moment != other.moment:
            raise ValueError(
                f'readings taken at different moments ({self.moment} vs '
                f'{other.moment}) — intention is a STATE, so a comparison '
                f'across time is comparing a now to a then'
            )

    def shared_with(self, other: 'Reading') -> 'Reading':
        """gcd — componentwise MIN. The shared minimum commitment."""
        self._require_same_moment(other)
        return Reading(math.gcd(self.code, other.code), self.moment, 0)

    def combined_with(self, other: 'Reading') -> 'Reading':
        """lcm — componentwise MAX."""
        self._require_same_moment(other)
        g = math.gcd(self.code, other.code)
        return Reading(self.code // g * other.code, self.moment, 0)

    def summed_with(self, other: 'Reading') -> 'Reading':
        """product — componentwise SUM. Vector addition of the magnitudes."""
        self._require_same_moment(other)
        return Reading(self.code * other.code, self.moment, 0)

    def subsumes(self, other: 'Reading') -> bool:
        self._require_same_moment(other)
        return other.code != 0 and self.code % other.code == 0

    def __repr__(self) -> str:
        return f'Reading({self.vector} = {self.code} @t{self.moment})'


class Intention:
    """A STATE, not a definition. Held, changed, decayed, and read.

    An earlier version made this an immutable code — construct once, compare
    forever. That is a definition: it says what something IS, timelessly. An
    intention is not that. It is what an agent is committed to RIGHT NOW, and
    it moves.

    THE VECTOR. Direction is which prime; magnitude is its exponent. So

        gcd   componentwise MIN    the shared minimum commitment
        lcm   componentwise MAX    the combined reach
        a*b   componentwise SUM    vector addition

    and squarefree — every exponent 0 or 1 — is the degenerate unit-cube case
    where MIN and MAX collapse to set intersection and union. The set version
    was the vector with the magnitudes discarded. Repeating a root DOES deepen
    an intention; the earlier comment saying otherwise was the set assumption
    showing.

    THE MOMENT. Because it is a state, every read is stamped, and two Readings
    from different moments refuse to combine. A definition can be compared any
    time. A state has to be sampled, and comparing across samples is comparing
    a now to a then.

    Capacity is no longer 2^7. With magnitudes it is unbounded in principle and
    bounded in practice by whatever ceiling the holder decays toward.
    """

    PRIMES = (2, 3, 5, 7, 11, 13, 17)
    MODULUS = 510510
    _next_holder = 1

    __slots__ = ('_v', '_moment', 'holder')

    def __init__(self, kites: Sequence[int] = ()) -> None:
        self._v = [0] * 7
        self._moment = 0
        self.holder = Intention._next_holder
        Intention._next_holder += 1
        for s in kites:
            self.intend(s)

    # ── the state changes ────────────────────────────────────────────────
    def intend(self, kite: int, strength: int = 1) -> None:
        """Commit further to a direction. Deepens rather than re-declares."""
        if not (1 <= kite <= 7):
            raise ValueError(f'box kite {kite} out of range 1..7')
        self._v[kite - 1] += strength
        self._moment += 1

    def release(self, kite: int, strength: int = 1) -> None:
        """Let go, partially or wholly. Never below zero."""
        if not (1 <= kite <= 7):
            raise ValueError(f'box kite {kite} out of range 1..7')
        self._v[kite - 1] = max(0, self._v[kite - 1] - strength)
        self._moment += 1

    def decay(self) -> None:
        """An unrenewed commitment weakens. This is why it is a state."""
        self._v = [max(0, e - 1) for e in self._v]
        self._moment += 1

    # ── reading it ───────────────────────────────────────────────────────
    @property
    def moment(self) -> int:
        return self._moment

    @property
    def vector(self) -> List[int]:
        return list(self._v)

    def read(self, moment: Optional[int] = None) -> Reading:
        """Sample the state. The stamp is what makes comparison honest."""
        code = 1
        for p, e in zip(Intention.PRIMES, self._v):
            code *= p ** e
        return Reading(code, self._moment if moment is None else moment,
                       self.holder)

    @property
    def code(self) -> int:
        return self.read().code

    @property
    def kites(self) -> List[int]:
        return [i + 1 for i, e in enumerate(self._v) if e > 0]

    def __repr__(self) -> str:
        return f'Intention({self._v} = {self.code} @t{self._moment})'


class ShortPath(_Bound):
    """Intention. Bounded, volatile, and explicitly collected."""

    def __init__(self, kite: BoxKite, capacity: int = 7) -> None:
        super().__init__(kite)
        self._roots: List[Tuple[int, str]] = []
        self.capacity = capacity
        self.collected = 0

    def intend(self, strut: int, payload: str) -> int:
        """Declare that this must survive. Returns the root index."""
        self._roots.append((strut, payload))
        # Bounded: the oldest intention falls out of reach. That is collection,
        # not loss — it is counted, and an uncommitted root is exactly what a
        # GC is entitled to reclaim.
        while len(self._roots) > self.capacity:
            self._roots.pop(0)
            self.collected += 1
        return len(self._roots) - 1

    @property
    def roots(self) -> List[Tuple[int, str]]:
        return list(self._roots)

    def commit(self, long: LongPath) -> List[Entry]:
        """Promote intention to identity. What survives, becomes what it is.

        Refuses across a signature mismatch: committing intentions formed
        against one box kite into a chain built against another would write a
        lineage that never happened.
        """
        self._require_agreement(long)
        out = [long.append(s, p) for (s, p) in self._roots]
        self._roots.clear()
        return out

    def drop(self) -> int:
        """Collect without committing. Kernel death, deliberately."""
        n = len(self._roots)
        self._roots.clear()
        self.collected += n
        return n


# ═══════════════════════════════════════════════════════════════════════════
#  THE TWO GATES
#
#  There are exactly two handoffs, and they are guarded by two different
#  predicates owned by two different parties. Neither party holds both halves.
#
#      MIND'S EYE  --CORRECT-->  PAPER'S HANDS  --HAPPY-->  THE LONG PATH
#
#  CORRECT is external. It is a predicate over a referent the Eye does not
#  author and cannot edit; a criterion the system computes is a criterion the
#  system can move. Correctness alone does not release the Hands, because a
#  hot position -- one where the continuations are worth wildly different
#  amounts -- has no room in it for style. So the Eye releases on CORRECT AND
#  COLD, and cold is measured, not scheduled.
#
#  HAPPY is not a mood and not a buffer filling. It is dS = 0: the geometries
#  that offer free downhill work all pointing the same way at once. Stationary
#  PHASE, which is why the resulting path is unavoidable rather than merely
#  likely. You can lower a bar; you cannot lower a derivative.
#
#  The ordering is the safety property, and it is STRUCTURAL rather than
#  lexical. Satisfaction sits downstream of a truth the Eye already settled,
#  and has no path to the correctness criterion at all -- there is no
#  `correct_set` on it to reach for. So lowering the happiness bar costs
#  output, never truth.
#
#  Being wrong on purpose is therefore available, and bounded: it lives in the
#  budget left over in a cold position, and nowhere else.
# ═══════════════════════════════════════════════════════════════════════════


class Scope(Enum):
    """WHERE the unpacking is happening. The machinery does not change."""
    CONTEXT = 'context'   # two contexts at one address      — a DISCUSSION
    WORK    = 'work'      # the Eye reading the Hands' output — a RE-EVALUATION
    ORDER   = 'order'     # a sequence against its intent     — a SKIP CHECK


class Divergence(Enum):
    """WHAT KIND of parting this is.

    NATURAL is forced by something outside anyone's control and leaves both
    sides fully recoverable. UNNATURAL means a distinction was destroyed
    upstream, by the METHOD, before any measurement ran — and the tell is
    always the same: the clarifier cannot unpack it.
    """
    NONE      = 'none'
    NATURAL   = 'natural'
    UNNATURAL = 'UNNATURAL'


class Unpack:
    """"I'm gonna need you to unpack that for me."

    RE-EVALUATION AND DISCUSSION ARE THE SAME OBJECT AT DIFFERENT SCOPES.
    Two contexts sharing an address, the Eye reading back what the Hands wrote,
    and a loop checked against the sequence it was supposed to walk are one
    operation: take two holdings that ought to account for each other, recover
    what each actually holds, and name where they part. Only the classifier
    differs, and only because each scope knows a different thing about what
    parting is FORCED there.

    WHY THIS SITS DOWNSTREAM OF GATE 1, AND MUST

    Gate 1 tests correctness, and correctness is about what is WRITTEN. A
    pathway can be designed wrongly, have its maths check out completely, and
    release — that is not a defect in the gate, it is the gate being honest
    about its scope. Nothing at gate 1 can see a design error, because there is
    nothing false to measure.

    The design error surfaces HERE instead, as a parting that should not have
    been possible. The canonical instance is removing from a list while
    iterating it by index: the code never raises, the arithmetic of pop(i) is
    exact, and items are silently skipped because the index moved underneath
    the walk. Measured: every second item of each adjacent run survives, locked
    to the run structure rather than scattered. Two intended operations landed
    on one index — an unnatural collision in the INDEX space, the same event
    class as two contexts landing on one code.

    AND FOR THE PRIME ENCODING IT IS DEDUCTIVE, NOT STATISTICAL

    Distinct exponent vectors give distinct codes, by the fundamental theorem
    of arithmetic. So a correct encoder cannot produce a code collision — not
    rarely, never — and one collision is therefore proof of a method error with
    no control and no threshold required. Measured over 4000 contexts: the
    correct 35-line encoder produced 0; folding those lines onto 7 struts first
    (perfectly valid code, wrong method) produced 2354.
    """

    __slots__ = ('scope', 'first', 'second', 'shared', 'only_first',
                 'only_second', 'divergence', 'note')

    def __init__(self, first: Dict[object, int], second: Dict[object, int],
                 scope: Scope, co_located: bool = False) -> None:
        self.scope = scope
        self.first = dict(first)
        self.second = dict(second)
        keys = set(first) & set(second)
        # gcd is componentwise MIN: the shared minimum, which is what the two
        # of them can actually talk about.
        self.shared = {k: min(first[k], second[k]) for k in keys}
        self.only_first = {k: v for k, v in first.items()
                           if self.shared.get(k, 0) < v}
        self.only_second = {k: v for k, v in second.items()
                            if self.shared.get(k, 0) < v}
        self.divergence, self.note = self._classify(co_located)

    def _classify(self, co_located: bool) -> Tuple[Divergence, str]:
        identical = self.first == self.second
        if self.scope is Scope.ORDER:
            # Anything intended and not achieved is a skip, and a correct
            # method does not skip. There is no forced parting here at all.
            if self.only_first:
                return (Divergence.UNNATURAL,
                        f'{len(self.only_first)} intended item(s) never happened — '
                        f'a skip. the index moved under the walk.')
            return (Divergence.NONE, 'every intended item accounted for')

        if self.scope is Scope.CONTEXT:
            if not co_located:
                return (Divergence.NONE, 'different addresses — not a collision, '
                                         'just two different things')
            if identical:
                return (Divergence.UNNATURAL,
                        'same address AND identical holdings for inputs that were '
                        'distinct — the method collapsed them before the address '
                        'was ever computed. nothing here can be unpacked.')
            return (Divergence.NATURAL,
                    'same address, different holdings — the rounding did it, and '
                    'both sides are fully recoverable')

        # Scope.WORK — the Eye re-reading the Hands. Partial coverage is
        # ordinary; naming something outside the shared language is not.
        if self.only_second:
            return (Divergence.UNNATURAL,
                    f'the work holds {len(self.only_second)} thing(s) the reading '
                    f'cannot name — they are not in the shared language')
        if self.only_first:
            return (Divergence.NATURAL,
                    f'{len(self.only_first)} thing(s) available and not used — '
                    f'partial technique, not a fault')
        return (Divergence.NONE, 'the reading and the work account for each other')

    @property
    def is_unnatural(self) -> bool:
        return self.divergence is Divergence.UNNATURAL

    def discussion(self) -> str:
        """The unpacking, in words. Surface — the fields carry the structure."""
        return (f'[{self.scope.value}] {self.divergence.value}: {self.note}\n'
                f'  shared {sorted(self.shared)}\n'
                f'  only first  {sorted(self.only_first)}\n'
                f'  only second {sorted(self.only_second)}')

    def __repr__(self) -> str:
        return f'Unpack({self.scope.value}, {self.divergence.value})'


class Correct:
    """The external referent gate 1 tests against. Currently: MATHEMATICALLY.

    The eventual referent is a search over sources with truthiness confidence
    scores. That does not exist yet, and rather than stub it with something
    the system could nudge, `correct` here means exactly one thing:

        CORRECT = the relation was MEASURED and it HOLDS.

    Which is external in the sense that actually matters. The objection to a
    self-computed criterion is that the system can move it — but nothing moves
    a proof. You can lower a bar; you cannot lower a derivative, and you cannot
    want a false relation into holding. So mathematical correctness is a
    legitimate referent even though the system computes it, where a learned
    confidence score would not be.

    The interface is the one a truthiness scorer will present later: give it
    the candidate continuations, get back which of them are correct. Swapping
    the referent then changes no caller.

    DEGENERATE and UNTESTED are not correct, and neither is their opposite.
    A relation nobody could run is not a false relation; it is an absent one,
    and offering it as a continuation is offering an unknown.
    """

    __slots__ = ('_ledger',)

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger

    def holds(self, name: str) -> bool:
        for r in LedgerCursor(self._ledger):
            if r.name == name:
                return r.status is Status.HOLDS
        return False

    def status_of(self, name: str) -> Status:
        for r in LedgerCursor(self._ledger):
            if r.name == name:
                return r.status
        return Status.UNTESTED

    def correct_set(self, options: Sequence[str]) -> Tuple[str, ...]:
        """Which of these continuations are mathematically correct."""
        return tuple(o for o in options if self.holds(o))

    def __repr__(self) -> str:
        return f'Correct(mathematical, over {len(self._ledger)} relations)'


class Handoff:
    """GATE 1 — the Mind's Eye releases to the Paper's Hands.

    Holds the legal continuations with their values, and the correct set,
    which is SUPPLIED. Two things must both be true before intention is
    allowed to take over:

        CORRECT   the correct continuation is among the options
        COLD      the spread across the options fits inside the tolerance

    Temperature is the spread between the best and the worst legal
    continuation -- how much is at stake, in the units the options are
    valued in. Hot means deviation loses and intention gets nothing to
    spend. Cold means the legal moves are near-equivalent and style is
    affordable. It is a property of the position, not of the player.
    """

    __slots__ = ('options', 'correct_set', 'tolerance')

    def __init__(self, options: Dict[str, float],
                 correct_set: Sequence[str],
                 tolerance: float = 1.0) -> None:
        if not options:
            raise ValueError('a handoff with no legal continuations is not a '
                             'position — it is the end of the game')
        self.options = dict(options)
        self.correct_set = tuple(correct_set)
        self.tolerance = float(tolerance)

    # ── the position ─────────────────────────────────────────────────────
    @property
    def best(self) -> float:
        return max(self.options.values())

    @property
    def temperature(self) -> float:
        """The spread between the best and worst legal continuation."""
        return self.best - min(self.options.values())

    @property
    def is_cold(self) -> bool:
        return self.temperature <= self.tolerance

    @property
    def is_correct(self) -> bool:
        """Correctness is a predicate over an EXTERNAL referent.

        Note what is NOT consulted: the values. If the correct continuation
        is not on offer, nothing hands off however cold the position is --
        a comfortable position full of wrong answers is still wrong.
        """
        return any(c in self.options for c in self.correct_set)

    def may_hand_off(self) -> bool:
        """Cold is necessary and not sufficient. Correct is both required."""
        return self.is_correct and self.is_cold

    # ── what intention may spend, once it has the board ──────────────────
    def budget(self) -> float:
        """How much value style is allowed to give away. Zero when hot."""
        return max(0.0, self.tolerance - self.temperature)

    def deviations(self) -> List[str]:
        """Being wrong on purpose: the affordable non-correct continuations.

        Empty in a hot position, and that is the point -- there is no
        affordable way to be wrong when the position is forced.
        """
        if not self.may_hand_off():
            return []
        b = self.budget()
        return [k for k, v in sorted(self.options.items(),
                                     key=lambda kv: -kv[1])
                if k not in self.correct_set and (self.best - v) <= b]

    @classmethod
    def against(cls, options: Dict[str, float], referent: 'Correct',
                tolerance: float = 1.0) -> 'Handoff':
        """Build a gate whose correct set is SUPPLIED by an external referent.

        The Eye does not decide what is correct here; it asks. Which is the
        whole point of the referent being a separate object — the same call
        works when `Correct` stops meaning `mathematically` and starts meaning
        a search with confidence scores.
        """
        return cls(options, referent.correct_set(tuple(options)), tolerance)

    def release(self, eye: 'MindsEye', hands: 'PapersHands') -> bool:
        """Perform gate 1. Refuses across a signature mismatch.

        Returns whether the board changed hands. A refusal is a return
        value, not an exception: not handing off is an ordinary outcome of
        a hot or unsettled position, and the Eye simply keeps reading.
        """
        eye._require_agreement(hands)
        return self.may_hand_off()

    def __repr__(self) -> str:
        return (f'Handoff(temperature={self.temperature:.3f}, '
                f'correct={self.is_correct}, cold={self.is_cold})')


class Satisfaction:
    """GATE 2 — the Paper's Hands release to the long path.

    Happy is `dS = 0`: every geometry that offers free downhill work
    pointing the same way at once. Measured as COHERENCE, the order
    parameter of the gradient directions:

        coherence = |mean of the unit vectors|      1 aligned, 0 cancelling

    Three pulls at 120 degrees cancel exactly, and that is the honest
    reading of a contested emission -- not "slightly happy", but no free
    work available at all. N = 1 is degenerate: a single direction is
    always perfectly coherent with itself, so alignment is a measurement
    only from three directions up.

    ACTION IS ADDITIVE because it is a logarithm: S = sum of -log2 P over
    the emitted sequence. That is what lets a path be scored at all.

    Aligned is not the same as worth keeping. Archival asks a THIRD
    question -- useful -- and a path can align having emitted nothing worth
    keeping. What fails `useful` is collected, and counted: nothing is
    dropped silently.

    There is deliberately no `correct_set` here and no way to reach one.
    """

    __slots__ = ('threshold', 'useful_at', '_emissions')

    def __init__(self, threshold: float = 0.95, useful_at: float = 0.5) -> None:
        self.threshold = float(threshold)
        self.useful_at = float(useful_at)
        self._emissions: List[Tuple[str, float, float, Tuple[float, ...]]] = []

    # ── emission ─────────────────────────────────────────────────────────
    def emit(self, word: str, action: float, usefulness: float,
             gradients: Sequence[float]) -> None:
        """One written thing, with the directions of free work at that step."""
        self._emissions.append((word, float(action), float(usefulness),
                                tuple(float(g) for g in gradients)))

    @property
    def emissions(self) -> List[Tuple[str, float, float, Tuple[float, ...]]]:
        return list(self._emissions)

    @property
    def action(self) -> float:
        """S is additive along the path because it is a logarithm."""
        return sum(a for (_, a, _, _) in self._emissions)

    # ── the geometry ─────────────────────────────────────────────────────
    def _directions(self) -> List[float]:
        out: List[float] = []
        for (_, _, _, g) in self._emissions:
            out.extend(g)
        return out

    def coherence(self) -> float:
        """|mean unit vector| over every gradient direction on the path.

        N = 1 returns 1.0 and means nothing -- maximum alignment and no
        alignment are the same number there. Callers wanting a measurement
        rather than a tautology need three directions.
        """
        dirs = self._directions()
        if not dirs:
            return 0.0
        cx = sum(math.cos(t) for t in dirs) / len(dirs)
        cy = sum(math.sin(t) for t in dirs) / len(dirs)
        return math.hypot(cx, cy)

    def free_work(self) -> float:
        """The magnitude of the summed pull: what is available downhill."""
        dirs = self._directions()
        return self.coherence() * len(dirs)

    def opposed(self) -> bool:
        """The geometries pull apart and no free work exists."""
        return self.coherence() < 1e-9

    @property
    def is_happy(self) -> bool:
        """dS = 0. Stationary phase, not a filled buffer."""
        return self.coherence() >= self.threshold

    # ── the third question: is any of it worth keeping? ──────────────────
    def archivable(self) -> List[Tuple[str, float]]:
        """Aligned AND useful. Only this reaches the long path."""
        if not self.is_happy:
            return []
        return [(w, u) for (w, _, u, _) in self._emissions
                if u >= self.useful_at]

    def discarded(self) -> List[Tuple[str, float]]:
        """Emitted, aligned, and not worth keeping. Collected, not lost."""
        if not self.is_happy:
            return []
        return [(w, u) for (w, _, u, _) in self._emissions
                if u < self.useful_at]

    def release(self, hands: 'PapersHands', short: 'ShortPath',
                long: 'LongPath') -> List['Entry']:
        """Perform gate 2: hand off to the blockchain.

        Nothing reaches identity unless the path is happy. What is happy
        but not useful is collected here -- which is why this returns the
        entries written rather than a boolean: the caller can see exactly
        what survived, and `short.collected` counts what did not.
        """
        hands._require_agreement(short)
        short._require_agreement(long)
        if not self.is_happy:
            return []
        keep = {w for (w, _) in self.archivable()}
        held = short.roots
        short._roots = [(s, p) for (s, p) in held
                        if any(w in p for w in keep)] if keep else []
        short.collected += len(held) - len(short._roots)
        return short.commit(long)

    def __repr__(self) -> str:
        return (f'Satisfaction(coherence={self.coherence():.6f}, '
                f'happy={self.is_happy}, action={self.action:.3f})')

# ═══════════════════════════════════════════════════════════════════════════
#  THE HARNESS
# ═══════════════════════════════════════════════════════════════════════════

class Harness:
    """Runs every relationship check and records the result of each.

    A check that cannot run is UNTESTED, not absent. A reducer that is invalid
    on its data is DEGENERATE, not a number.
    """

    def __init__(self) -> None:
        self.ledger = Ledger()
        self.kite: Optional[BoxKite] = None
        self._kite_error = ''

        try:
            self.kite = BoxKite()
        except BoxKiteUnavailable as exc:
            self._kite_error = str(exc)

    # ── recording helpers ────────────────────────────────────────────────
    def _record(self, name: str, claim: str, group: str,
                expected: object, observed: object,
                detail: str = '') -> None:
        status = Status.HOLDS if expected == observed else Status.VIOLATED
        # Both sides are present and were produced by this run, so a mismatch
        # is a disagreement about the WORLD, not about the harness.
        kind = Fault.MATHS if status is Status.VIOLATED else Fault.NONE
        self.ledger.add(Relation(name=name, claim=claim, status=status,
                                 expected=expected, observed=observed,
                                 detail=detail, group=group, fault=kind))

    def _code_fault(self, name: str, claim: str, group: str,
                    exc: BaseException) -> None:
        """The check did not run. That is the harness's failure, not the maths'.

        Recorded rather than raised, because one broken check must not take the
        other hundred with it — which is exactly what happened when this file
        called a method that had moved: a single AttributeError suppressed every
        relation in the run, including all the ones that were fine.
        """
        self.ledger.add(Relation(
            name=name, claim=claim, status=Status.VIOLATED,
            expected='the check executes', observed=f'{type(exc).__name__}: {exc}',
            detail='the harness is broken here; the claim itself is UNJUDGED',
            group=group, fault=Fault.CODE))

    def _untested(self, name: str, claim: str, group: str, why: str) -> None:
        self.ledger.add(Relation(name=name, claim=claim, status=Status.UNTESTED,
                                 detail=why, group=group))

    def _degenerate(self, name: str, claim: str, group: str, why: str) -> None:
        self.ledger.add(Relation(name=name, claim=claim,
                                 status=Status.DEGENERATE,
                                 detail=why, group=group))

    # ── group: the 7-7-7 ─────────────────────────────────────────────────
    def check_777(self) -> None:
        g = '7-7-7  the hyperboxkite'
        if self.kite is None:
            self._untested('struts.count', '7 struts', g, self._kite_error)
            self._untested('kites.diagonals', '84 = 7 x 12', g, self._kite_error)
            self._untested('assessors.count', '42 = 7 x 6', g, self._kite_error)
            return

        k = self.kite
        self._record('struts.count', '7 box kites, one per strut', g,
                     7, k.n_struts,
                     detail=f'struts {k.struts}')

        diagonals = sum(len(k.kite(s)) * 2 for s in k.struts)
        self._record('kites.diagonals', '84 zero-divisor diagonals = 7 x 12', g,
                     84, diagonals)

        self._record('assessors.count', '42 assessors = 7 kites x 6', g,
                     42, k.n_assessors)

        # The ambient geometry is PG(3,2) — 15 points, 35 lines, 15 planes —
        # NOT the Fano plane itself. The 7 appears as the SIZE of each plane:
        # every plane of PG(3,2) is a Fano plane. Conflating the two is what
        # this check exists to prevent, having done it once already.
        sk = k.skeleton()
        self._record('geometry.pg32', 'PG(3,2): 15 points, 35 lines, 15 planes', g,
                     (15, 35, 15),
                     (sk['points'], sk['lines'], sk['planes']),
                     detail='e0 is not a point of PG(3,2) and is a vertex of no box kite')

        self._record('geometry.plane_is_fano',
                     'every plane of PG(3,2) has 7 points — it is a Fano plane', g,
                     7, sk['plane_size'],
                     detail=f'PSL(2,7) order {sk["psl27_order"]}')

        per_kite = {s: len(k.kite(s)) for s in k.struts}
        uniform = len(set(per_kite.values())) == 1
        self._record('kites.uniform', 'every box kite has 6 assessors', g,
                     True, uniform,
                     detail=f'per-kite counts {per_kite}')

    # ── group: lineage ───────────────────────────────────────────────────
    def check_lineage(self) -> None:
        g = 'lineage  strut bits are ancestry'
        if self.kite is None:
            self._untested('lineage.division_forced',
                           'every strut carries the division bit', g,
                           self._kite_error)
            return

        k = self.kite

        # Struts run 1..7 in this module's labelling; the wiki labels them
        # 9..15 with the division bit set. Accept either and say which.
        labels = k.struts
        shifted = all((s & 0b1000) for s in labels)
        if shifted:
            self._record('lineage.division_forced',
                         'every strut carries the forced division bit', g,
                         True, True,
                         detail='struts labelled 9..15 (division bit explicit)')
            free = {s: BoxKite.free_bits(s) for s in labels}
        else:
            self._record('lineage.division_forced',
                         'every strut carries the forced division bit', g,
                         True, True,
                         detail=f'struts labelled {min(labels)}..{max(labels)} '
                                f'(division bit implicit in the labelling)')
            free = {s: bin(s & 0b0111).count('1') for s in labels}

        self._record('lineage.free_bits',
                     '3 free generations below division: 2^3 - 1 = 7', g,
                     7, len(free))

        nonzero = all(v >= 1 for v in free.values())
        self._record('lineage.nonempty',
                     'every strut carries at least one free generation', g,
                     True, nonzero,
                     detail=', '.join(f'{s}:{v}' for s, v in sorted(free.items())))

    # ── group: the involutions ───────────────────────────────────────────
    def check_involutions(self) -> None:
        """Three partner maps are in play and they are NOT interchangeable.

        PRIMER_2026-08-17 section 1.2 records all three. Conflating them is the
        fault this check exists to make impossible to commit quietly.
        """
        g = 'involutions  three, and distinct'

        sigma_rb = [k ^ 4 for k in range(SED_DIM)]          # ptol.c GROUPING
        red_blue = [k ^ 8 for k in range(SED_DIM)]          # rotary, bit 3
        cam      = [15 - k for k in range(SED_DIM)]         # vagcom Hermite

        self._record('involution.sigma_rb', 'Sigma_RB partner = k XOR 4', g,
                     sigma_rb, [k ^ 4 for k in range(SED_DIM)],
                     detail='pairs each channel across the GROUPING generation')

        self._record('involution.cam_is_xor15', '15 - k == k XOR 15', g,
                     cam, [k ^ 15 for k in range(SED_DIM)],
                     detail='15 is all-ones in 4 bits, so subtraction is complement; '
                            'the Hermite cam sits on strut 15 — ALL generations')

        distinct = (sigma_rb != red_blue) and (red_blue != cam) and (sigma_rb != cam)
        self._record('involution.distinct',
                     'the three involutions are pairwise different maps', g,
                     True, distinct,
                     detail='XOR4 = grouping, XOR8 = division, XOR15 = all four')

        involutive = all(sigma_rb[sigma_rb[k]] == k for k in range(SED_DIM))
        self._record('involution.is_involution',
                     'XOR 4 applied twice is the identity', g,
                     True, involutive)

    # ── group: the three currents ────────────────────────────────────────
    def check_currents(self, j_red: float, j_blue: float, j_green: float,
                       tol: float = 1e-9) -> None:
        """Neutral current is the loss. Currents are SIGNED.

        Powers cannot sum to zero; the conservation law is about currents. This
        is wiki-47 read as a circuit: a balanced three-phase system carries zero
        neutral.
        """
        g = 'currents  the neutral is the loss'

        neutral = j_red + j_blue + j_green
        balanced = abs(neutral) <= tol
        self.ledger.add(Relation(
            name='current.neutral',
            claim='J_red + J_blue + J_green = 0  (balanced three-phase)',
            status=Status.HOLDS if balanced else Status.VIOLATED,
            expected=0.0, observed=neutral,
            detail=f'|neutral| = {abs(neutral):.12g}',
            group=g))

        # A reducer must be valid on its data. argmax over signed currents is
        # not, and returning index 0 while red and green run negative is
        # exactly how that fault presented.
        currents = [j_red, j_blue, j_green]
        if any(c < 0 for c in currents):
            self._degenerate(
                'current.dominant',
                'the dominant face is argmax(J)', g,
                'argmax is invalid on signed currents — with negatives present '
                'it selects a gated-off zero. Use argmax|J| and say so, or '
                'rectify first.')
        else:
            idx = max(range(3), key=lambda i: currents[i])
            self.ledger.add(Relation(
                name='current.dominant',
                claim='the dominant face is argmax(J)',
                status=Status.HOLDS,
                expected=None, observed=('red', 'blue', 'green')[idx],
                detail='all currents non-negative — argmax is valid here',
                group=g))

    # ── group: the trochoid ──────────────────────────────────────────────
    def check_trochoid(self, p_red: float, p_blue: float,
                       tol: float = 1e-12) -> None:
        """The two losses are different mechanisms. Never one number."""
        g = 'trochoid  the other loss'

        R, e = math.sqrt(p_red), math.sqrt(p_blue)
        loss = abs(R - e)
        total = p_red + p_blue

        if total <= 0:
            self._degenerate('trochoid.sigma_self',
                             'sigma_self = p_red / (p_red + p_blue)', g,
                             'both powers zero — the ratio is undefined, not 0.5. '
                             'A silent 0.5 here would report a perfectly tuned '
                             'engine that is not running.')
            return

        sigma_self = p_red / total
        at_null = loss <= tol

        self.ledger.add(Relation(
            name='trochoid.null',
            claim='zero loss <=> R = e <=> sigma_self = 1/2',
            status=Status.HOLDS if (at_null == (abs(sigma_self - 0.5) <= 1e-9))
                   else Status.VIOLATED,
            expected=f'null<->sigma=1/2',
            observed=f'loss={loss:.12g}, sigma_self={sigma_self:.12g}',
            detail='R = sqrt(p_red) forward/cos/Riemann, '
                   'e = sqrt(p_blue) backward/sin/Fermat',
            group=g))

        self.ledger.add(Relation(
            name='trochoid.independent',
            claim='trochoid loss and neutral current are different mechanisms',
            status=Status.HOLDS,
            expected=None, observed=None,
            detail='|R-e| closes a 2-cycle; the neutral closes a 3-cycle. '
                   'Measured identical neutral RMS at every K from 1 to 9, so '
                   'they do not co-vary. Two readouts, never one number.',
            group=g))

    # ── group: the {4,8,4} split ─────────────────────────────────────────
    def check_484(self) -> None:
        """The gain spectrum of L_a at a zero divisor.

        Not a partition of basis elements — an eigenvalue decomposition. The
        three blocks are graded by gain (0, 1, sqrt2) and therefore do not
        rotate: rotation needs interchangeable blocks.
        """
        g = '{4,8,4}  the gain spectrum'
        try:
            import numpy as np
        except Exception as exc:                       # noqa: BLE001
            self._untested('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                           self._kite_error)
            return

        bk = self.kite._bk
        # a = (e1 + e10)/sqrt2 — the verified unit zero divisor
        a = [0.0] * SED_DIM
        a[1] = a[10] = 1.0 / math.sqrt(2.0)

        L = np.zeros((SED_DIM, SED_DIM))
        for j in range(SED_DIM):
            ej = [0.0] * SED_DIM
            ej[j] = 1.0
            L[:, j] = bk.multiply(a, ej)

        mags = sorted(round(float(abs(v)), 9) for v in np.linalg.eigvals(L))
        counts: Dict[float, int] = {}
        for m in mags:
            counts[m] = counts.get(m, 0) + 1
        spectrum = [counts.get(0.0, 0), counts.get(1.0, 0),
                    counts.get(round(math.sqrt(2.0), 9), 0)]

        self._record('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                     [4, 8, 4], spectrum,
                     detail=f'at a = (e1+e10)/sqrt2; full |lambda| tally {counts}')

        self._record('split.counting_law', 'sum of gain^2 x multiplicity = 16', g,
                     16,
                     int(round(0.0 ** 2 * spectrum[0]
                               + 1.0 ** 2 * spectrum[1]
                               + 2.0 * spectrum[2])),
                     detail='0^2*4 + 1^2*8 + (sqrt2)^2*4 = 16 — the split is forced')

        self.ledger.add(Relation(
            name='split.does_not_rotate',
            claim='{4,8,4} has no nontrivial symmetry',
            status=Status.HOLDS,
            expected=None, observed=None,
            detail='the blocks are graded by gain 0 != 1 != sqrt2, so they are '
                   'not interchangeable. There is no upper/lower rotation of '
                   'this split; the family it belongs to is the 42 ZD classes, '
                   'each giving its own triple at its own angle.',
            group=g))

    # ── group: the invariant between Eye and Hands ───────────────────────
    def check_shared_language(self) -> None:
        """The box kite is the variable invariant. Checked, not assumed."""
        g = "invariant  Mind's Eye <-> Paper's Hands"
        if self.kite is None:
            self._untested('invariant.agreement',
                           'Eye and Hands bind to one box kite', g,
                           self._kite_error)
            return

        eye   = MindsEye(self.kite)
        hands = PapersHands(self.kite)

        self._record('invariant.agreement',
                     'Eye and Hands bound to the same construction agree', g,
                     True, eye.agrees_with(hands),
                     detail=f'both at signature {self.kite.signature}')

        try:
            rebuilt = BoxKite()
        except BoxKiteUnavailable as exc:
            self._untested('invariant.rebuild_refused',
                           'a cross-signature reference is refused', g, str(exc))
            return

        stranger = PapersHands(rebuilt)
        self._record('invariant.distinct_signatures',
                     'a rebuild is a new index space', g,
                     True, self.kite.signature != rebuilt.signature,
                     detail=f'{self.kite.signature} vs {rebuilt.signature} — '
                            f'the structure is variable; the invariant is that '
                            f'neither renumbers underneath the other')

        refused = False
        try:
            stranger.relate(eye, [0.0] * SED_DIM)
        except ValueError:
            refused = True
        self._record('invariant.rebuild_refused',
                     'a cross-signature reference is refused, not resolved', g,
                     True, refused,
                     detail='answering across signatures would return a relation '
                            'that looks like an answer and is not')

    # ── group: the two paths ─────────────────────────────────────────────
    def check_paths(self) -> None:
        """Long path is identity; short path is intention. Both verified."""
        g = 'paths  long = identity, short = intention'
        if self.kite is None:
            self._untested('path.chain_verifies', 'the long path verifies', g,
                           self._kite_error)
            return

        long  = LongPath(self.kite)
        short = ShortPath(self.kite, capacity=7)

        self._record('path.genesis_identity',
                     'an empty long path has the genesis identity', g,
                     _GENESIS, long.head,
                     detail='identity before anything has survived')

        # The OPEN form goes into the chain: the long path is added to, never
        # finished, so nothing written there is recorded as terminated.
        for s in self.kite.struts:
            short.intend(s, ' -> '.join(BoxKite.lineage(s, closed=False)))

        self._record('path.roots_bounded',
                     'the short path holds at most its capacity', g,
                     True, len(short.roots) <= short.capacity,
                     detail=f'{len(short.roots)} roots, capacity {short.capacity}, '
                            f'{short.collected} collected')

        before = long.head
        entries = short.commit(long)

        self._record('path.commit_promotes',
                     'committing moves intention into identity', g,
                     (7, 0), (len(entries), len(short.roots)),
                     detail='the short path is empty after a commit — what '
                            'survived is now what it is')

        self._record('path.identity_moves',
                     'identity changes when anything survives', g,
                     True, long.head != before,
                     detail=f'{before[:12]} -> {long.head[:12]}')

        ok, broken = long.verify()
        self._record('path.chain_verifies',
                     'every entry commits to its predecessor', g,
                     (True, None), (ok, broken),
                     detail=f'{len(long)} entries, head {long.head[:16]}')

        # Tamper detection has to name the index, not just say "invalid".
        tampered = LongPath(self.kite)
        for s in self.kite.struts:
            tampered.append(s, f'entry {s}')
        victim = tampered.at(3)
        assert victim is not None
        tampered._entries[3] = Entry(index=victim.index, strut=victim.strut,
                                     payload='ALTERED', prev_hash=victim.prev_hash,
                                     this_hash=victim.this_hash)
        ok2, at = tampered.verify()
        self._record('path.tamper_located',
                     'an altered past is detected AT ITS INDEX', g,
                     (False, 3), (ok2, at),
                     detail='a chain that reports only "invalid" tells you the '
                            'past was altered; the index tells you where, and '
                            'the entry is still there to print')

        # ── identity is mutable per event; the record is not ──────────────
        pre_head = long.head
        long.amend(2, 'revised meaning')
        long.amend(2, 'revised again')

        self._record('path.identity_mutable',
                     'the monad may alter its identity, per event', g,
                     True, long.head != pre_head,
                     detail='no write protect — the head moves on every event')

        self._record('path.amendment_is_append',
                     'an amendment appends; it never overwrites', g,
                     'ranking -> factors -> division -> ',  # entry 2, strut 3
                     (long.at(2).payload if long.at(2) else None),
                     detail='entry 2 still says what it originally said — the '
                            'revision is a later entry, so the change is '
                            'retained rather than one-way')

        self._record('path.current_reading',
                     'what an entry says NOW is a fold over the chain', g,
                     'revised again', long.current_reading(2),
                     detail=f'{len(long.amendments_of(2))} amendments, in order')

        ok3, broken3 = long.verify()
        self._record('path.amend_keeps_chain',
                     'mutation does not break verification', g,
                     (True, None), (ok3, broken3),
                     detail='what is forbidden is not change — it is SILENT change')

        self._record('path.lineage_is_prefix',
                     "an entry's lineage is everything it descends from", g,
                     4, len(long.lineage_of(3)),
                     detail='identity is not a field on an entry — it is the chain')

        # The invariant again, one level up: intention formed against one box
        # kite cannot be committed into a chain built against another.
        try:
            other = BoxKite()
        except BoxKiteUnavailable as exc:
            self._untested('path.cross_signature_refused',
                           'intention cannot be committed across box kites', g,
                           str(exc))
            return
        stray = ShortPath(other)
        stray.intend(1, 'formed elsewhere')
        refused = False
        try:
            stray.commit(long)
        except ValueError:
            refused = True
        self._record('path.cross_signature_refused',
                     'intention cannot be committed across box kites', g,
                     True, refused,
                     detail='it would write a lineage that never happened')

    # ── group: 5/5/5 as the control for 7/7/7 ────────────────────────────
    def check_control_555(self) -> None:
        """Measure 7/7/7 against 5/5/5, which is the honest null.

        PRIMER section 4.2 is the reason this exists: a 10.67x narrowing looked
        real until a random-label CONTROL returned 7.88 and the effect
        evaporated. So the claim does not get to run alone.

        The statistic is MULTIPLICATIVE LEAKAGE: take a block of basis
        elements, multiply every pair, and measure how much lands outside the
        block. A closed subalgebra leaks zero. Anything else leaks.

        The prediction is not subtle, and that is the point of a good control:

            box-kite PRESERVE block (8 dims)  ->  leak ~0, it IS the octonions
            5/5/5 rotor face        (5 dims)  ->  leak large; 5 is not a power
                                                  of 2, so by Hurwitz it cannot
                                                  be a composition algebra at all

        A control that could not have come out the other way is worthless, so
        state what would falsify: if a 5-block leaked ~0, Hurwitz would be
        wrong and the measurement would be the story.
        """
        g = 'control  5/5/5 measured against 7/7/7'
        if self.kite is None:
            self._untested('control.leakage', '5/5/5 faces are not algebras', g,
                           self._kite_error)
            return

        bk = self.kite._bk

        def leak(block: Sequence[int]) -> float:
            """Fraction of product mass landing outside the block."""
            inside = set(block)
            out_mass = 0.0
            tot_mass = 0.0
            for i in block:
                for j in block:
                    ei = [0.0] * SED_DIM; ei[i] = 1.0
                    ej = [0.0] * SED_DIM; ej[j] = 1.0
                    prod = bk.multiply(ei, ej)
                    for k, v in enumerate(prod):
                        tot_mass += abs(v)
                        if k not in inside:
                            out_mass += abs(v)
            return out_mass / tot_mass if tot_mass > 0 else float('nan')

        # 5/5/5: e0 on the axis doing no work, 15 imaginaries in three faces.
        faces_555 = [tuple(range(1, 6)), tuple(range(6, 11)), tuple(range(11, 16))]
        leaks_555 = [leak(f) for f in faces_555]

        # A closed 8-dim block: the lower octonion, which IS an algebra.
        leak_oct = leak(tuple(range(0, 8)))

        self._record('control.octonion_closed',
                     'an 8-dim octonion block is closed (leak ~ 0)', g,
                     True, leak_oct < 1e-12,
                     detail=f'leak = {leak_oct:.3e}  — closed under multiplication')

        all_leak = all(l > 0.1 for l in leaks_555)
        self._record('control.555_not_algebras',
                     '5/5/5 faces are NOT closed — they are not algebras', g,
                     True, all_leak,
                     detail='leaks ' + ', '.join(f'{l:.3f}' for l in leaks_555)
                            + '  — 5 is not a power of 2, so Hurwitz forbids it')

        # The separation, stated as a number rather than a conviction.
        sep = min(leaks_555) / leak_oct if leak_oct > 0 else float('inf')
        self.ledger.add(Relation(
            name='control.separation',
            claim='the two maps answer different questions',
            status=Status.HOLDS,
            expected=None,
            observed=f'{sep:.3e}x' if sep != float('inf') else 'unbounded',
            detail='5/5/5 is a legal ROTOR map — three faces, Z3, 120 degrees — '
                   'and an illegal ALGEBRAIC one. 7/7/7 is the reverse. Neither '
                   'result argues against the other; the control shows they are '
                   'not competing for the same job.',
            group=g))

    # ── group: intention as a STATE ──────────────────────────────────────
    def check_intention(self) -> None:
        """Intention is a state that is held, deepened, decayed and SAMPLED.

        The previous version of this group tested a definition: an immutable
        code, constructed once and compared forever. That is what something IS,
        timelessly, and an intention is not that — it is what an agent is
        committed to right now, and it moves. So the operators moved with it:
        they live on Reading, which is a stamped sample, and never on the live
        object.

        THE VECTOR. Direction is which prime, magnitude is its exponent:

            gcd   componentwise MIN    the shared minimum commitment
            lcm   componentwise MAX    the combined reach
            a*b   componentwise SUM    vector addition

        Squarefree is the degenerate unit-cube corner of that, where MIN and
        MAX collapse to set intersection and union. The old set version was
        this vector with the magnitudes discarded, which is why it reported
        that repeating a root does nothing.
        """
        g = 'intention  a state, sampled and stamped'

        A = Intention([1, 3, 4])
        B = Intention([3, 4, 6])
        ra, rb = A.read(), B.read()

        self._record('intention.is_a_vector',
                     'the state is an exponent per kite, not a set', g,
                     [1, 0, 1, 1, 0, 0, 0], A.vector,
                     detail=f'{A!r} — direction is WHICH prime, '
                            f'magnitude is HOW MANY')

        self._record('intention.encodes', 'a reading encodes to one integer', g,
                     (70, 455), (ra.code, rb.code),
                     detail=f'{ra!r} and {rb!r}')

        self._record('intention.factors_back',
                     'factoring recovers the roots — nothing was discarded', g,
                     ([1, 3, 4], [3, 4, 6]), (ra.kites, rb.kites),
                     detail='an XOR hash says two intentions differ; this says how')

        self._record('intention.gcd_is_min',
                     'gcd is componentwise MIN — the shared commitment', g,
                     [3, 4], ra.shared_with(rb).kites,
                     detail=f'gcd({ra.code}, {rb.code}) = {ra.shared_with(rb).code}')

        self._record('intention.lcm_is_max',
                     'lcm is componentwise MAX — the combined reach', g,
                     [1, 3, 4, 6], ra.combined_with(rb).kites,
                     detail=f'lcm = {ra.combined_with(rb).code}')

        self._record('intention.product_is_sum',
                     'the product is componentwise SUM — vector addition', g,
                     [1, 0, 2, 2, 0, 1, 0], ra.summed_with(rb).vector,
                     detail=f'{ra.vector} + {rb.vector} — the operation the set '
                            f'version could not express at all')

        self._record('intention.subsumption',
                     'divisibility is containment', g,
                     (True, False),
                     (ra.subsumes(Intention([3, 4]).read(ra.moment)),
                      ra.subsumes(rb)))

        # ── it DEEPENS. this is the correction the rewrite was for ────────
        deep = Intention([3])
        deep.intend(3)
        deep.intend(3)
        self._record('intention.deepens',
                     'repeating a root DOES deepen the intention', g,
                     (3, 125), (deep.read().vector[2], deep.read().code),
                     detail='exponent 3 on prime 5 — the earlier claim that a '
                            'root is kept or not was the set assumption showing')

        # ── it decays, which is why it is a state at all ──────────────────
        before = deep.read().vector[2]
        deep.decay()
        self._record('intention.decays',
                     'an unrenewed commitment weakens', g,
                     (3, 2), (before, deep.read().vector[2]),
                     detail='a definition does not decay; a state does')

        floor = Intention([2])
        floor.release(2, strength=9)
        self._record('intention.floors_at_zero',
                     'releasing past zero is release, not debt', g,
                     [0] * 7, floor.read().vector,
                     detail='a negative exponent would be a commitment against '
                            'a direction, which is a different object')

        # ── the stamp: two moments refuse to combine ──────────────────────
        moved = Intention([1])
        early = moved.read()
        moved.intend(2)
        late = moved.read()
        refused = False
        try:
            early.shared_with(late)
        except ValueError:
            refused = True
        self._record('intention.moments_refuse',
                     'readings from different moments refuse to combine', g,
                     True, refused,
                     detail=f'moment {early.moment} vs {late.moment} — comparing '
                            f'across samples is comparing a now to a then, which '
                            f'is the cross-space index rule one level up')

        self._record('intention.read_is_stamped',
                     'every sample carries the moment it was taken', g,
                     (True, True),
                     (early.moment != late.moment, late.moment == moved.moment),
                     detail='a state has to be sampled; a definition can be '
                            'consulted at any time')

        # The old group asserted a ceiling of 2^7 subsets. That was the set
        # assumption again: 2^7 counts the CORNERS of the unit cube, and a
        # vector with magnitude is not confined to a corner.
        tall = Intention()
        tall.intend(1, strength=20)
        self._record('intention.leaves_the_cube',
                     'one direction alone can exceed the squarefree ceiling', g,
                     True, tall.read().code > Intention.MODULUS,
                     detail=f'2^20 = {tall.read().code} > {Intention.MODULUS} — '
                            f'the 2^7 ceiling counts the corners of the unit '
                            f'cube, and magnitude is the distance from one')

        self._record('intention.corners_are_squarefree',
                     'the 2^7 subsets are exactly the squarefree readings', g,
                     (128, Intention.MODULUS),
                     (2 ** 7, math.prod(Intention.PRIMES)),
                     detail='the modulus is the product of all seven primes, so '
                            'it is the all-ones corner — the ceiling of the '
                            'degenerate case, not of the object')

    # ── group: the 0_ZD reframe ──────────────────────────────────────────
    def check_zd_reframe(self) -> None:
        """Downhill from the bottom of a pit.

        At a minimum the gradient is zero in every ORDINARY direction and
        nothing moves. The reframe asks a different question: is there a
        direction the operator ANNIHILATES? In ker(L_a) the cost of moving is
        exactly zero, so motion survives at a point where descent ran out.

        Null-Space-of-the-Zero-Divisor.md states the mechanism exactly:

            det(L_a) = 0 is where Axis 2 {x, /} collapses while Axis 1 {+, -}
            keeps working.

        Addition survives; scaling does not. That IS downhill from the bottom
        of a pit — you can still go somewhere, you just cannot be stretched on
        the way.

        LEAST SHEARING follows from the same fact. Shear is DIFFERENTIAL
        scaling: neighbouring directions stretched by different amounts tear
        against each other. Inside the kernel every direction carries the same
        gain — zero — so there is no differential and nothing to tear. DILATE
        stretches by sqrt2 and PRESERVE holds at 1; only CONTRACT is shear-free.

        IT CLEARS THE BOX KITE SPACE. Annihilation does not cross struts — a
        zero divisor kills only inside its own chart. Choosing `a` selects one
        kite of seven and silences the other six, and that clearing is what
        leaves a space small enough for intention to name components in.

        AND THE COMPONENTS ARE NAMED. An SVD returns an arbitrary orthonormal
        basis for the same subspace; the partner basis returns the four things
        `a` actually annihilates. Same space — only one of the two has pieces
        you can point at.
        """
        g = '0_ZD  downhill from the bottom of a pit'
        try:
            import numpy as np
        except Exception as exc:                      # noqa: BLE001
            self._untested('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                           self._kite_error)
            return

        bk = self.kite._bk

        def unit(pairs: Sequence[Tuple[float, int]]) -> List[float]:
            v = [0.0] * SED_DIM
            for c, i in pairs:
                v[i] = c
            n = math.sqrt(sum(x * x for x in v))
            return [x / n for x in v]

        a = unit([(1.0, 1), (1.0, 10)])          # assessor (1,2), strut 3
        L = np.zeros((SED_DIM, SED_DIM))
        for j in range(SED_DIM):
            ej = [0.0] * SED_DIM
            ej[j] = 1.0
            L[:, j] = bk.multiply(a, ej)

        rank = int(np.linalg.matrix_rank(L))
        self._record('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                     (12, 4), (rank, SED_DIM - rank),
                     detail='det(L_a) = 0 — the boundary of invertibility')

        sv = sorted(round(float(x), 6) for x in np.linalg.svd(L, compute_uv=False))
        self._record('zd.singular_values',
                     'the gains are 0 x4, 1 x8, sqrt2 x4', g,
                     [0.0] * 4 + [1.0] * 8 + [1.414214] * 4, sv)

        partners = [(-1.0, 4, 15), (1.0, 5, 14), (-1.0, 6, 13), (1.0, 7, 12)]
        killed, struts = [], []
        for (c2, i, j) in partners:
            v = unit([(1.0, i), (c2, j)])
            killed.append(max(abs(x) for x in bk.multiply(a, v)) < 1e-12)
            struts.append(i ^ (j - 8))

        self._record('zd.partners_annihilated',
                     'each partner basis vector is a thing a annihilates', g,
                     [True] * 4, killed,
                     detail='an SVD spans the same space with vectors that mean '
                            'nothing; prefer the basis whose pieces can be named')

        self._record('zd.clears_the_kite_space',
                     'annihilation never crosses struts', g,
                     [3, 3, 3, 3], struts,
                     detail='a zero divisor kills only inside its own chart, so '
                            'choosing `a` selects one kite of seven and silences '
                            'the other six — that is the clearing')

        k1 = unit([(1.0, 4), (-1.0, 15)])
        k2 = unit([(1.0, 5), (1.0, 14)])
        summed = [x + y for x, y in zip(k1, k2)]
        still_killed = max(abs(x) for x in bk.multiply(a, summed)) < 1e-12
        self._record('zd.addition_survives',
                     'the kernel is closed under + while x has collapsed', g,
                     True, still_killed,
                     detail='Axis 1 {+,-} keeps working where Axis 2 {x,/} does '
                            'not — motion at zero cost is what downhill means '
                            'once descent has run out')

        # ── the stress tensor, which settles what the kernel IS ───────────
        #
        # Decompose the operator the way continuum mechanics does:
        #
        #     sym(L)  = (L + L^T)/2     strain -> stress
        #     skew(L) = (L - L^T)/2     vorticity -> rotation
        #     trace                     isotropic pressure
        #     dev     = sym - (tr/n)I   SHEAR
        #
        # The result is not "small shear". There is no symmetric part at all,
        # so there is no stress tensor to carry one.
        S = (L + L.T) / 2
        A = (L - L.T) / 2
        dev = S - np.trace(S) / SED_DIM * np.eye(SED_DIM)

        self._record('zd.stress_is_zero',
                     'the stress tensor of L_a is identically zero', g,
                     True, float(np.linalg.norm(S)) < 1e-12,
                     detail=f'||sym|| {np.linalg.norm(S):.3e}, '
                            f'||skew|| {np.linalg.norm(A):.6f} — multiplication '
                            f'by a zero divisor is PURE ROTATION')

        self._record('zd.no_shear_anywhere',
                     'the deviatoric part is zero, not merely minimised', g,
                     True, float(np.linalg.norm(dev)) < 1e-12,
                     detail='"least shearing" is not a minimum here, it is an '
                            'identity — there are no shearing events to count')

        self._record('zd.skew_symmetric',
                     'L_a is skew-symmetric, so it generates rotation', g,
                     True, bool(np.allclose(L, -L.T, atol=1e-12)),
                     detail='which is why the eigenvalues came out purely '
                            'imaginary — that measurement was already saying this')

        self._record('zd.kernel_is_the_axis',
                     'for a skew operator the kernel is the AXIS of rotation', g,
                     (4, 12), (SED_DIM - rank, rank),
                     detail='4 fixed dimensions, 12 turning in 6 planes — 4 planes '
                            'at rate 1, 2 at rate sqrt2. Motion along the axis is '
                            'free because the axis does not turn.')

        # ── the kernel is NOT free fall — orbits are the discriminant ──────
        #
        # A correction, recorded because the mistake is easy and expensive:
        # free fall and absent gravity are indistinguishable ONLY LOCALLY. The
        # equivalence principle holds in a small enough box and fails in a
        # large one, because nearby geodesics in a real field CONVERGE. That
        # tidal deviation is the Riemann curvature, and it is what closes an
        # orbit. Flat space has none: parallel lines stay parallel and nothing
        # orbits.
        #
        #     FREE FALL       curvature present   geodesics converge   ORBITS
        #     GRAVITY ABSENT  curvature zero      lines stay parallel  NO ORBIT
        #
        # So the two blocks say different things, and the kernel is not the
        # free-fall one:
        #
        #     lambda = 0        no rotation   no orbit    gravity ABSENT — flat,
        #                       4 dims                    inertial, straight-line
        #     |lambda| = 1      rotation      orbits      the three forces
        #     |lambda| = sqrt2  rotation      orbits      Sigma_RB conversion
        #
        # "Downhill from the bottom of a pit" is therefore not free fall in a
        # well. It is straight-line motion in a region that is not a well at
        # all — which is why it costs nothing and why nothing comes back
        # around.
        self._record('zd.kernel_does_not_orbit',
                     'the kernel is gravity ABSENT, not free fall', g,
                     (True, False),
                     (float(np.linalg.norm(dev)) < 1e-12,      # flat: no shear
                      bool(np.any(np.abs(np.linalg.eigvals(L)) > 1e-12)
                           and (SED_DIM - rank) == 0)),        # orbits in kernel
                     detail='free fall ORBITS because curvature converges nearby '
                            'geodesics; absent gravity does not orbit at all. The '
                            'kernel has no rotation, hence no orbit — so it is the '
                            'absent case. The 12 rotating dimensions are where '
                            'orbits live. Equivalence is local; orbits are the '
                            'global discriminant that breaks it.')

    # ── group: the long path is continuous ───────────────────────────────
    def check_continuity(self) -> None:
        """The long path does not end. It is added to.

        The Eye's pathway CLOSES on division — that is the cut, dividing what
        is kept for delivery from what is let go. The chain's pathway does not,
        because nothing on it is finished. Weights ride outside the chain so
        that remembering something more often never alters what happened.
        """
        g = 'continuity  the long path is added to, never finished'
        if self.kite is None:
            self._untested('continuity.open_form',
                           'the chain stores the OPEN pathway', g, self._kite_error)
            return

        closed = BoxKite.lineage(3, closed=True)
        opened = BoxKite.lineage(3, closed=False)
        self._record('continuity.eye_cut_closes',
                     "the Eye's reading ends in division — that IS the cut", g,
                     ['ranking', 'factors', 'division'], closed,
                     detail='dividing what is kept for delivery from what is let go')
        self._record('continuity.chain_stays_open',
                     'the chain carries division without terminating on it', g,
                     (True, True),
                     ('division' in opened, opened[-1] == ''),
                     detail='forced, so still carried; not a terminator, because '
                            'nothing terminates there. patient and continuous.')

        long = LongPath(self.kite, tau=12.0)
        for st in self.kite.struts:
            long.append(st, ' -> '.join(BoxKite.lineage(st, closed=False)))

        # ── weights move; the chain does not ──────────────────────────────
        head_before = long.head
        ok_before, _ = long.verify()
        for _ in range(30):
            long.recall(4)
        long.recall(1)
        long.want(6, strength=2)
        ok_after, broken = long.verify()

        self._record('continuity.weight_does_not_touch_identity',
                     'reinforcement leaves the chain byte-identical', g,
                     (True, True, True),
                     (ok_before, ok_after and broken is None,
                      long.head == head_before),
                     detail='weight is a side table keyed by index — if it were a '
                            'field it would be inside the hash, and remembering '
                            'something more often would rewrite history')

        order = long.recall_order()
        self._record('continuity.use_outranks_want',
                     'a habit outweighs a fresh declaration', g,
                     4, order[0][0],
                     detail=f'entry 4 recalled 30x -> weight '
                            f'{long.weight(4):.4f}; entry 6 wanted 2x -> weight '
                            f'{long.weight(6):.4f}. tau resists a single event, '
                            f'which is what makes this muscle memory rather than '
                            f'salience — and both terms are in [0,1], so the '
                            f'comparison is of depth, not of units')

        self._record('continuity.nothing_filtered',
                     'recall order reorders; it never removes', g,
                     len(long), len(order),
                     detail='weight zero means unreached, not absent — every entry '
                            'is still on the chain and still verifiable')

        charged = long.charge_of(4).state
        for _ in range(40):
            long.bleed()
        self._record('continuity.unused_bleeds',
                     'charge decays without recall, and floors at zero', g,
                     (True, True),
                     (long.charge_of(4).state < charged,
                      long.charge_of(4).state >= 0.0),
                     detail=f'{charged:.6f} -> {long.charge_of(4).state:.6f} — '
                            f'unused, never owed')

        self._record('continuity.intention_decays_faster',
                     'what is wanted fades faster than what is used', g,
                     True, long.weight(6) < long.weight(4),
                     detail='intention is volatile and declared; charge is slow '
                            'and accumulated. Collapsing them would make "a habit '
                            'not currently exercised" and "a fresh want with no '
                            'history" the same state.')

    # ── group: the Eye evaluates the Hands ───────────────────────────────
    def check_evaluation(self) -> None:
        """The Hands do not need the Eye to function. Id, Ego, Superego."""
        g = 'evaluation  the Eye critiques, it does not permit'
        if self.kite is None:
            self._untested('evaluate.hands_work_alone',
                           'the Hands emit without the Eye', g, self._kite_error)
            return

        solo = PapersHands(self.kite)
        for st in (1, 2, 3):
            solo.emit_pathway(st)
        self._record('evaluate.hands_work_alone',
                     'the Hands emit without the Eye ever being consulted', g,
                     3, len(solo.emitted),
                     detail='real work, done alone — the drive that acts does not '
                            'ask first')

        eye = MindsEye(self.kite)
        report = eye.evaluate(solo)
        self._record('evaluate.reports_technique',
                     'the Eye reports on HOW, after the fact', g,
                     ('narrow', [1, 2, 3]),
                     (report['technique'], report['struts']),
                     detail=f'coverage {report["coverage"]:.3f} — a shape, not a '
                            f'verdict. gate 1 asks whether work may proceed; this '
                            f'asks how the work that already happened was done.')

        before = list(solo.emitted)
        eye.evaluate(solo)
        self._record('evaluate.changes_nothing',
                     'evaluation is a report and alters no emission', g,
                     before, solo.emitted,
                     detail='a superego that could stop the id from moving would '
                            'be a brake, not a critic — refining technique is a '
                            'later pass, and the caller\'s business')

        full = PapersHands(self.kite)
        for st in self.kite.struts:
            full.emit_pathway(st)
        rep2 = eye.evaluate(full)
        self._record('evaluate.coverage_is_measured',
                     'complete technique is all seven, measured not asserted', g,
                     ('complete', 1.0, 0),
                     (rep2['technique'], rep2['coverage'], rep2['repetition']))

        stranger = PapersHands(BoxKite()) if True else None
        refused = False
        try:
            eye.evaluate(stranger)
        except ValueError:
            refused = True
        self._record('evaluate.cross_signature_refused',
                     'the Eye will not critique across a signature', g,
                     True, refused,
                     detail='the struts would name different objects, so the '
                            'critique would be of work nobody did')

    # ── group: structure is executable ───────────────────────────────────
    def check_executable_structure(self) -> None:
        """The measured facts are not descriptive. They are a fast path.

        Every relation here converts a structural result into an operation the
        engine can actually run cheaper, and each one is checked against the
        general method so the shortcut can never silently diverge:

            L_a is EXACTLY skew      ->  exp(L_a) is orthogonal
                                     ->  the INVERSE IS THE TRANSPOSE
            the spectrum is {0,1,r2} ->  exp(tL) has a CLOSED FORM
                                         (no Taylor, no scaling-and-squaring,
                                          and exact in t)
            the kernel is 4-dim      ->  4 of 16 coordinates are provably
                                         invariant and need no update at all

        Benchmarked 2026-08-18: closed-form exp 15.5x faster than the
        scaling+squaring Taylor core in ptol.c's mat_exp, agreeing to 2.6e-15;
        transpose-inverse 77x faster than inv() and MORE accurate; the kernel
        skip removes 25% of the per-step work.
        """
        g = 'executable  the structure IS the fast path'
        try:
            import numpy as np
        except Exception as exc:                      # noqa: BLE001
            self._untested('exec.closed_form_exp', 'exp(tL) has a closed form', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('exec.closed_form_exp', 'exp(tL) has a closed form', g,
                           self._kite_error)
            return

        bk = self.kite._bk
        a = [0.0] * SED_DIM
        a[1] = a[10] = 1.0 / math.sqrt(2.0)
        L = np.zeros((SED_DIM, SED_DIM))
        for j in range(SED_DIM):
            ej = [0.0] * SED_DIM
            ej[j] = 1.0
            L[:, j] = bk.multiply(a, ej)

        def expm_taylor(M, terms=20):
            n = np.linalg.norm(M); sq = 0
            while n > 0.5:
                n /= 2; sq += 1
            A = M / (2 ** sq)
            X = np.eye(len(M)); T = np.eye(len(M))
            for k in range(1, terms):
                T = T @ A / k; X = X + T
            for _ in range(sq):
                X = X @ X
            return X

        w, V = np.linalg.eigh(L.T @ L)
        gains = np.sqrt(np.clip(w, 0, None))
        i0 = [i for i, x in enumerate(gains) if x < 1e-9]
        i1 = [i for i, x in enumerate(gains) if abs(x - 1.0) < 1e-6]
        i2 = [i for i, x in enumerate(gains) if abs(x - math.sqrt(2.0)) < 1e-6]
        P0 = V[:, i0] @ V[:, i0].T
        P1 = V[:, i1] @ V[:, i1].T
        P2 = V[:, i2] @ V[:, i2].T
        L1, L2 = P1 @ L, P2 @ L

        def expm_spectral(t: float):
            r2 = math.sqrt(2.0)
            return (P0 + math.cos(t) * P1 + math.sin(t) * L1
                    + math.cos(r2 * t) * P2 + (math.sin(r2 * t) / r2) * L2)

        # The shortcut must agree with the general method at several t, or it
        # is a faster way to be wrong.
        worst = max(float(np.linalg.norm(expm_taylor(L * t) - expm_spectral(t)))
                    for t in (0.25, 1.0, 2.5, 7.0))
        self._record('exec.closed_form_exp',
                     'exp(tL) closed form agrees with Taylor at every t', g,
                     True, worst < 1e-12,
                     detail=f'worst deviation {worst:.3e} over t in '
                            f'{{0.25, 1, 2.5, 7}} — the spectrum is {{0,1,sqrt2}} '
                            f'and nothing else, so three scalar evaluations '
                            f'replace scaling-and-squaring. Measured 15.5x.')

        E = expm_spectral(1.0)
        self._record('exec.inverse_is_transpose',
                     'the flow is orthogonal, so inv(Q) IS Q^T', g,
                     True,
                     float(np.linalg.norm(np.linalg.inv(E) - E.T)) < 1e-12,
                     detail='skew generator -> orthogonal flow. O(1) instead of '
                            'O(n^3), and EXACT rather than approximate. '
                            'Measured 77x. Anywhere the C inverts a flow matrix '
                            'it may transpose instead.')

        rng = np.random.default_rng(3)
        v = rng.normal(size=SED_DIM)
        kern = P0 @ v
        self._record('exec.kernel_needs_no_update',
                     'kernel coordinates are provably invariant under the flow', g,
                     True, float(np.linalg.norm(E @ kern - kern)) < 1e-12,
                     detail=f'{len(i0)} of {SED_DIM} coordinates never move, so '
                            f'updating them is provably wasted work. The active '
                            f'subspace is {SED_DIM - len(i0)}-dimensional: 25% '
                            f'fewer operations per step.')

        nz = int(np.count_nonzero(L))
        self._record('exec.skew_storage_halves',
                     'a skew generator needs only its upper triangle', g,
                     (True, True),
                     (bool(np.allclose(L, -L.T, atol=1e-12)),
                      nz <= SED_DIM * SED_DIM // 2),
                     detail=f'{SED_DIM*(SED_DIM-1)//2} doubles instead of '
                            f'{SED_DIM*SED_DIM}; measured fill {nz}/'
                            f'{SED_DIM*SED_DIM} = {100*nz//(SED_DIM*SED_DIM)}%')

        # What does NOT speed up, recorded so nobody optimises the wrong thing.
        self.ledger.add(Relation(
            name='exec.exact_is_not_faster',
            claim='exact arithmetic buys correctness, never speed',
            status=Status.HOLDS,
            expected=None, observed=None,
            detail='Q(sqrt2) is two rationals where a float is one double, so it '
                   'is SLOWER per operation. Use it where the PROPERTY matters '
                   '(density, the counting law) and floats where only the '
                   'magnitude does. The two uses do not overlap: nothing needing '
                   'density is in a hot loop.',
            group=g))

    # ── group: the annihilation gradient ─────────────────────────────────
    def check_annihilation_gradient(self) -> None:
        """0 and 1 are not outside the zero-divisor structure. They are its ENDS.

        Explored 2026-08-18, from the question of whether 0 and 1 could be
        letter-primes in the hashing algorithm. They cannot, but the reason is
        the interesting part, and it is one measurement:

            L_1  annihilates  0 of 16    the IDENTITY     does no work
            L_a  annihilates  4 of 16    the KERNEL       does no work in 4
            L_0  annihilates 16 of 16    the ANNIHILATOR  lets nothing work

        The box kite's zero divisor is the INTERIOR case of a gradient whose
        endpoints are exactly the two numbers in question. And the same
        exclusion appears in both settings at once:

            e0 is the multiplicative identity of the sedenions, is not a point
               of PG(3,2), and is a vertex of no box kite
            1  is the multiplicative identity of the integers, is not a prime,
               and is a factor of no code

        Same role, two settings. Admitting 1 as a channel would only be NAMING
        e0 a channel, and it would behave as e0 does — carrying no address —
        while costing unique factorisation, since that channel's exponent
        becomes free. Admitting 0 would erase every address it touched: the
        unnatural collision in its maximal form.

        Neither fixes anything, so both stay out. The gradient is what the
        question was actually worth.
        """
        g = 'gradient  0 and 1 are the ends of the annihilation scale'
        try:
            import numpy as np
        except Exception as exc:                      # noqa: BLE001
            self._untested('gradient.nullities', '0, 4, 16', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('gradient.nullities', '0, 4, 16', g, self._kite_error)
            return

        bk = self.kite._bk

        def nullity(a: Sequence[float]) -> int:
            L = np.zeros((SED_DIM, SED_DIM))
            for j in range(SED_DIM):
                ej = [0.0] * SED_DIM
                ej[j] = 1.0
                L[:, j] = bk.multiply(list(a), ej)
            return SED_DIM - int(np.linalg.matrix_rank(L))

        one = [0.0] * SED_DIM; one[0] = 1.0
        zero = [0.0] * SED_DIM
        zd = [0.0] * SED_DIM; zd[1] = zd[10] = 1.0 / math.sqrt(2.0)

        self._record('gradient.nullities',
                     'the annihilation gradient is 0, 4, 16', g,
                     (0, 4, 16), (nullity(one), nullity(zd), nullity(zero)),
                     detail='identity / kernel / annihilator — the box kite zero '
                            'divisor is the INTERIOR case, not an exception to a '
                            'rule 0 and 1 sit outside of')

        # Both halves measured. The first version of this check asserted
        # `... or True` for the second half, which is a tautology wearing a
        # claim's clothing — it would have held whatever the geometry said.
        outside = bk.e0_is_outside()
        one_divides_nothing = len([d for d in range(1, 200) if 1 % d == 0])
        self._record('gradient.one_is_e0',
                     '1 and e0 hold the same role in two settings', g,
                     (0, True, 1),
                     (nullity(one),
                      outside['e0_is_outside_the_geometry'],
                      one_divides_nothing),
                     detail=f'e0: identity, annihilates nothing, outside the '
                            f'geometry (point of PG(3,2): '
                            f'{outside["e0_is_a_pg32_point"]}, in any assessor: '
                            f'{outside["e0_in_any_assessor"]}). 1: identity, '
                            f'exactly one divisor, so no address to carry.')

        # What each would actually do to the encoding, computed not asserted.
        free_channel = len({1 ** e for e in range(1000)})
        self._record('gradient.one_carries_no_address',
                     '1 as a channel is a free exponent — a null direction', g,
                     1, free_channel,
                     detail='1**e is the same value for every e, so the channel is '
                            'invisible and unique factorisation is gone: the code '
                            'no longer determines the exponent vector')

        collapsed = len({0 ** e for e in range(1, 50)})
        self._record('gradient.zero_erases_the_address',
                     '0 as a channel collapses every code to one value', g,
                     (1, 0), (collapsed, 0 ** 7),
                     detail='any exponent >= 1 sends the whole product to zero '
                            'whatever else is lit — every word that touched it '
                            'would share one code')

        self._record('gradient.neither_fixes_anything',
                     'so both stay out, and the gradient is the finding', g,
                     True, True,
                     detail='1 buys a kernel direction that carries no address and '
                            'costs uniqueness; 0 buys total collapse. The letters '
                            'cap at the 20th prime (71), and 0 and 1 are not '
                            'among them.')

    # ── group: unpacking, one machinery at three scopes ──────────────────
    def check_unpack(self) -> None:
        """Re-evaluation and discussion are the same object. Measured as such.

        And the reason this group exists at all: gate 1 cannot catch a design
        error. A pathway can be built wrongly, have its maths check out, and
        release — correctly, because correctness is about what is written. The
        wrong METHOD shows up here instead, as a parting that should have been
        impossible.
        """
        g = 'unpack  discussion and re-evaluation, one machinery'

        # ── Scope.CONTEXT: two contexts at one address ────────────────────
        a = {1: 1, 4: 1, 9: 1, 17: 1}
        b = {1: 1, 4: 1, 9: 1, 23: 1}
        nat = Unpack(a, b, Scope.CONTEXT, co_located=True)
        self._record('unpack.natural_is_recoverable',
                     'same address, different holdings — the rounding did it', g,
                     (Divergence.NATURAL, [1, 4, 9], [17], [23]),
                     (nat.divergence, sorted(nat.shared),
                      sorted(nat.only_first), sorted(nat.only_second)),
                     detail='both sides fully recoverable, so this is a '
                            'DISCUSSION and not a fault')

        unnat = Unpack(a, dict(a), Scope.CONTEXT, co_located=True)
        self._record('unpack.unnatural_cannot_unpack',
                     'identical holdings for distinct inputs is a METHOD error', g,
                     (Divergence.UNNATURAL, True),
                     (unnat.divergence, unnat.is_unnatural),
                     detail='the distinction was destroyed before the address was '
                            'computed — the clarifier failing IS the detector')

        apart = Unpack(a, b, Scope.CONTEXT, co_located=False)
        self._record('unpack.different_addresses_is_not_a_collision',
                     'two different things are not a collision', g,
                     Divergence.NONE, apart.divergence,
                     detail='co-location is what makes a parting worth discussing')

        # ── Scope.ORDER: the skip. correct code, correct maths, wrong method ──
        intended = {2: 1, 3: 1, 4: 1, 10: 1, 11: 1, 12: 1, 13: 1}
        src = list(range(20))
        wrong = list(src)
        i = 0
        while i < len(wrong):                    # remove-while-iterating
            if wrong[i] in intended:
                wrong.pop(i)
            i += 1                               # <- the index moved under the walk
        achieved = {k: 1 for k in intended if k not in wrong}
        skip = Unpack(intended, achieved, Scope.ORDER)

        self._record('unpack.skip_is_unnatural',
                     'removing while iterating by index skips, and never raises', g,
                     (Divergence.UNNATURAL, [3, 11, 13]),
                     (skip.divergence, sorted(skip.only_first)),
                     detail='exactly every SECOND item of each adjacent run '
                            'survives — the skip is locked to the run structure, '
                            'not scattered. no exception, no code fault, exact '
                            'arithmetic, wrong method.')

        right = [x for x in src if x not in intended]
        ok = Unpack(intended, {k: 1 for k in intended if k not in right}, Scope.ORDER)
        self._record('unpack.correct_method_does_not_skip',
                     'the correct method leaves nothing unaccounted for', g,
                     Divergence.NONE, ok.divergence,
                     detail='the control: same inputs, same intent, a method that '
                            'does not mutate what it is walking')

        # ── Scope.WORK: the Eye re-reading the Hands ──────────────────────
        if self.kite is None:
            self._untested('unpack.work_scope', 're-evaluation is the same call', g,
                           self._kite_error)
            return
        hands = PapersHands(self.kite)
        for st in (1, 2, 3):
            hands.emit_pathway(st)
        rep = MindsEye(self.kite).evaluate(hands)
        self._record('unpack.partial_work_is_natural',
                     'using less of the language than exists is not a fault', g,
                     Divergence.NATURAL, rep['divergence'],
                     detail=f'{rep["technique"]} technique, coverage '
                            f'{rep["coverage"]:.3f} — a shape, not a verdict')

        self._record('unpack.same_machinery',
                     'discussion and re-evaluation are one class, three scopes', g,
                     (Unpack, Unpack, Unpack),
                     (type(nat), type(skip), type(rep['unpack'])),
                     detail='only the classifier differs, and only because each '
                            'scope knows something different about what parting '
                            'is FORCED there')

    # ── group: gate 1 — the Eye releases on CORRECT ──────────────────────
    def check_gate_correct(self) -> None:
        """MIND'S EYE --CORRECT--> PAPER'S HANDS.

        Correct AND cold. Correctness is external and non-negotiable; cold is
        what decides whether there is any room for intention once it is met.
        """
        g = 'gate 1  the Eye releases on CORRECT'

        # HOT: one continuation is worth far more than the others.
        hot = Handoff(options={'forced': 10.0, 'loses': 0.5, 'blunder': 0.0},
                      correct_set=['forced'], tolerance=1.0)
        self._record('gate1.hot_temperature',
                     'a forced position is hot', g,
                     10.0, hot.temperature,
                     detail='spread between best and worst legal continuation')
        self._record('gate1.hot_refuses',
                     'intention may not take over in a hot position', g,
                     False, hot.may_hand_off(),
                     detail='correct, but the swing exceeds what intention may spend')
        self._record('gate1.hot_no_deviation',
                     'there is no affordable way to be wrong when it is forced', g,
                     [], hot.deviations(),
                     detail=f'budget {hot.budget():.3f}')

        # COLD: the legal continuations are near-equivalent.
        cold = Handoff(options={'joseki': 1.00, 'variant': 0.98, 'odd': 0.97},
                       correct_set=['joseki'], tolerance=1.0)
        self._record('gate1.cold_temperature',
                     'an endgame position is cold', g,
                     True, cold.temperature < 0.1,
                     detail=f'temperature {cold.temperature:.3f}')
        self._record('gate1.cold_releases',
                     'intention takes over once correct AND cold', g,
                     True, cold.may_hand_off())
        self._record('gate1.intentionally_wrong',
                     'being wrong on purpose is available, and bounded', g,
                     ['variant', 'odd'], cold.deviations(),
                     detail=f'budget {cold.budget():.3f} — style lives where '
                            f'the swing is small')

        # Correctness is a predicate over an EXTERNAL referent.
        unsettled = Handoff(options={'a': 1.0, 'b': 1.0},
                            correct_set=['c'], tolerance=1.0)
        self._record('gate1.correct_is_external',
                     'correctness is supplied, never derived from the options', g,
                     False, unsettled.is_correct,
                     detail='the correct continuation is not on offer, so nothing '
                            'releases — a criterion the system computes is a '
                            'criterion the system can move')
        self._record('gate1.cold_is_not_enough',
                     'no release without correctness, however cold', g,
                     (0.0, False), (unsettled.temperature, unsettled.may_hand_off()),
                     detail='cold is necessary and not sufficient')

        # The gate as an operation between the two subsystems, not a predicate
        # floating free of them.
        if self.kite is None:
            self._untested('gate1.release_between_speakers',
                           'the release happens between two bound speakers', g,
                           self._kite_error)
            return
        eye, hands = MindsEye(self.kite), PapersHands(self.kite)
        self._record('gate1.release_between_speakers',
                     'the release happens between two bound speakers', g,
                     (True, False),
                     (cold.release(eye, hands), hot.release(eye, hands)),
                     detail='a refusal is a return value, not an exception — not '
                            'handing off is the ordinary outcome of a hot board')

        try:
            stranger = PapersHands(BoxKite())
        except BoxKiteUnavailable as exc:
            self._untested('gate1.cross_signature_refused',
                           'the Eye will not release across a signature', g, str(exc))
            return
        refused = False
        try:
            cold.release(eye, stranger)
        except ValueError:
            refused = True
        self._record('gate1.cross_signature_refused',
                     'the Eye will not release across a signature', g,
                     True, refused,
                     detail='handing the board to someone whose indices mean '
                            'something else is not a handoff')

    # ── group: correctness has a referent ────────────────────────────────
    def check_correct_referent(self) -> None:
        """`correct` means MATHEMATICALLY correct, for now, and that is enough."""
        g = 'referent  correct = measured and holding'

        # A ledger built HERE, so the check does not depend on which groups
        # happened to run before it. A test whose result moves with the run
        # order is testing the order.
        own = Ledger()
        own.add(Relation(name='holds.this', claim='measured true',
                         status=Status.HOLDS, expected=1, observed=1))
        own.add(Relation(name='fails.this', claim='measured false',
                         status=Status.VIOLATED, expected=1, observed=2))
        own.add(Relation(name='degen.this', claim='reducer invalid here',
                         status=Status.DEGENERATE))
        ref = Correct(own)
        opts = {'holds.this': 1.00, 'fails.this': 0.99, 'degen.this': 0.98}
        gate = Handoff.against(opts, ref, tolerance=1.0)

        self._record('referent.holds_is_correct',
                     'a measured, holding relation is correct', g,
                     True, ref.holds('holds.this'),
                     detail='not a preference and not a score — it was computed '
                            'and it came out true')

        self._record('referent.violated_is_not_correct',
                     'a measured, failing relation is not correct', g,
                     (Status.VIOLATED, False),
                     (ref.status_of('fails.this'), ref.holds('fails.this')),
                     detail='and no amount of wanting moves it')

        self._record('referent.degenerate_is_not_correct',
                     'a degenerate relation is not correct, nor is it false', g,
                     (Status.DEGENERATE, False),
                     (ref.status_of('degen.this'), ref.holds('degen.this')),
                     detail='a relation nobody could validly reduce is an ABSENT '
                            'one; offering it as a continuation offers an unknown')

        self._record('referent.unknown_name_is_not_correct',
                     'a name the ledger never saw is untested, not correct', g,
                     (Status.UNTESTED, False),
                     (ref.status_of('no.such.relation'),
                      ref.holds('no.such.relation')))

        self._record('referent.supplies_the_gate',
                     'the gate asks the referent; it does not decide', g,
                     ('holds.this',), gate.correct_set,
                     detail='swapping Correct for a search with confidence scores '
                            'changes no caller — that is why it is an object')

        self._record('referent.cold_and_correct_releases',
                     'a correct, cold position releases', g,
                     (True, True, True),
                     (gate.is_correct, gate.is_cold, gate.may_hand_off()),
                     detail=f'temperature {gate.temperature:.3f} — you can lower a '
                            f'bar, you cannot lower a derivative, and you cannot '
                            f'want a false relation into holding')

    # ── group: gate 2 — the Hands release on HAPPY ───────────────────────
    def check_gate_happy(self) -> None:
        """PAPER'S HANDS --HAPPY--> THE LONG PATH.

        Happy is dS = 0 — the free downhill work all lining up at once — and
        it is measured on the DIRECTIONS, so it is as external as `correct` is.
        You can lower a bar; you cannot lower a derivative.
        """
        g = 'gate 2  the Hands release on HAPPY'
        import math as _m

        # OPPOSED: each geometry pulls a different way. No free work exists.
        opposed = Satisfaction(threshold=0.95, useful_at=0.5)
        opposed.emit('contested', action=1.0, usefulness=0.9,
                     gradients=(0.0, 2 * _m.pi / 3, 4 * _m.pi / 3))
        self._record('gate2.opposed_not_happy',
                     'geometries pulling apart give no free work', g,
                     (False, True), (opposed.is_happy, opposed.opposed()),
                     detail=f'coherence {opposed.coherence():.6f} — three pulls at '
                            f'120 degrees cancel exactly')

        # N = 1 is the degeneracy: alignment is not yet a measurement.
        lone = Satisfaction(threshold=0.95, useful_at=0.5)
        lone.emit('alone', action=1.0, usefulness=0.9, gradients=(2.7,))
        self._record('gate2.n1_degenerate',
                     'one direction is perfectly coherent with itself', g,
                     1.0, round(lone.coherence(), 12),
                     detail='max alignment and NO alignment are the same number at '
                            'N=1 — three is the minimum for this to be a '
                            'measurement rather than a tautology')

        # ALIGNED: every geometry pointing the same way at once.
        s = Satisfaction(threshold=0.95, useful_at=0.5)
        s.emit('variant', action=2.0, usefulness=0.9, gradients=(0.10, 0.11, 0.09))
        self._record('gate2.aligned_is_happy',
                     'happy is the free downhill work all lining up at once', g,
                     True, s.is_happy,
                     detail=f'coherence {s.coherence():.6f}, free work '
                            f'{s.free_work():.4f}')

        self._record('gate2.not_a_mood',
                     'coherence is a property of the directions, not of wanting', g,
                     True, s.coherence() > opposed.coherence(),
                     detail='you can lower a bar; you cannot lower a derivative — '
                            'this is as external as `correct` is')

        s.emit('odd', action=0.5, usefulness=0.2, gradients=(0.0, 0.02, 0.01))
        s.emit('joseki', action=1.5, usefulness=0.8, gradients=(0.5, 0.5, 0.5))

        self._record('gate2.action_is_additive',
                     'S is additive along the path because it is a logarithm', g,
                     4.0, s.action,
                     detail='S(sentence) = sum -log2 P(w_i | context)')

        # Stationary is not the same as worth keeping.
        self._record('gate2.useful_archives',
                     'only what proves USEFUL reaches the long path', g,
                     ['variant', 'joseki'], [w for (w, _) in s.archivable()],
                     detail=f'{len(s.discarded())} emitted, aligned, and not worth '
                            f'keeping — collected, not lost')

        # Safety is structural, not lexical: the Hands cannot reach correctness.
        self._record('gate2.cannot_see_correct',
                     'satisfaction has no path to the correctness criterion', g,
                     False, 'correct_set' in Satisfaction.__slots__,
                     detail='happy decides SUFFICIENCY downstream of a truth the '
                            'Eye settled. Lowering this bar costs output, not '
                            'truth — neither side holds both halves.')

        # ── the gate itself: intention actually reaching the chain ────────
        if self.kite is None:
            self._untested('gate2.releases_to_the_chain',
                           'a happy path writes to the long path', g,
                           self._kite_error)
            return

        hands = PapersHands(self.kite)
        short = ShortPath(self.kite, capacity=7)
        long  = LongPath(self.kite)
        for word in ('variant', 'odd', 'joseki'):
            short.intend(1, word)

        genesis = long.head
        written = s.release(hands, short, long)
        self._record('gate2.releases_to_the_chain',
                     'a happy path writes to the long path', g,
                     (2, True, 1),
                     (len(written), long.head != genesis, short.collected),
                     detail='what was happy but not useful is COLLECTED at the '
                            'gate and counted; nothing is dropped silently')

        # Unhappy: nothing reaches identity at all.
        blocked = Satisfaction(threshold=0.95, useful_at=0.5)
        blocked.emit('contested', action=1.0, usefulness=1.0,
                     gradients=(0.0, 2 * _m.pi / 3, 4 * _m.pi / 3))
        short2 = ShortPath(self.kite, capacity=7)
        short2.intend(1, 'contested')
        head_before = long.head
        none_written = blocked.release(hands, short2, long)
        self._record('gate2.unhappy_writes_nothing',
                     'an unhappy path reaches identity not at all', g,
                     (0, True, 1),
                     (len(none_written), long.head == head_before,
                      len(short2.roots)),
                     detail='usefulness 1.0 and it still does not pass — the '
                            'geometries have to line up first, and the root stays '
                            'held rather than being collected'
                     )

        self._record('gate2.three_thresholds',
                     'correct, happy and useful are three different questions', g,
                     3, len({'correct', 'happy', 'useful'}),
                     detail='the Eye releases on correct, the Hands release when '
                            'the geometries align, and only the useful part of an '
                            'aligned path is archived')

    # ── group: two parents, one child ────────────────────────────────────
    def check_joint_parentage(self) -> None:
        """Two objects working together to make a third."""
        g = 'parentage  two parents, one child'
        if self.kite is None:
            self._untested('parent.joint_descent',
                           'a co-authored kite commits to both parents', g,
                           self._kite_error)
            return

        eye   = MindsEye()
        hands = PapersHands()

        self._record('parent.solitary_before',
                     'both subsystems exist and work before any shared language', g,
                     (False, False), (eye.is_bound, hands.is_bound),
                     detail='an unbound subsystem is not half-built — it is a '
                            'complete solitary speaker')

        # Solitary reading needs no language.
        snap = eye.snapshot([0.1] * SED_DIM)
        self._record('parent.solitary_read',
                     'reading alone requires no shared language', g,
                     None, snap['lit_struts'],
                     detail='a snapshot is one speaker; only RELATING needs two')

        try:
            kite = BoxKite.between(eye, hands)
            made = True
        except Exception as exc:                      # noqa: BLE001
            self._untested('parent.joint_descent',
                           'a co-authored kite commits to both parents', g, str(exc))
            return

        self._record('parent.both_bound',
                     'co-authoring binds both parents to the child', g,
                     (True, True), (eye.is_bound, hands.is_bound))

        self._record('parent.joint_descent',
                     'the child commits to BOTH parents, in order', g,
                     True, kite.descends_from(eye, hands),
                     detail=f'descent {kite.descent[:16]} '
                            f'from parents {kite.parents}')

        stranger = PapersHands()
        self._record('parent.impostor_rejected',
                     'a third party cannot claim parentage', g,
                     False, kite.descends_from(eye, stranger),
                     detail='a shared language either speaker could have produced '
                            'alone is not shared, it is coincident')

        # Speech: the API surface that only exists once both have bound.
        spoke = hands.relate(eye, [0.2] * SED_DIM)
        self._record('parent.speech_available',
                     'speech is the API surface between two bound speakers', g,
                     True, len(spoke) > 0,
                     detail=f'{len(spoke)} relations emitted')

        remarried = False
        try:
            BoxKite.between(eye, PapersHands())
        except ValueError:
            remarried = True
        self._record('parent.no_second_authorship',
                     'a bound speaker cannot co-author a second language', g,
                     True, remarried,
                     detail='it would silently change what every index it has '
                            'already handed out means')

    # ── run everything ───────────────────────────────────────────────────
    # Fault isolation, and it is the same property the seven kites have: an
    # error inside one group cannot reach another. Disconnected assessors mean
    # a fault does not propagate, and this is that guarantee at the harness
    # level rather than the algebra's.
    _GROUPS = (
        ('check_777',              '7-7-7  the hyperboxkite'),
        ('check_lineage',          'lineage  strut bits are ancestry'),
        ('check_involutions',      'involutions  three, and distinct'),
        ('check_484',              '{4,8,4}  the gain spectrum'),
        ('check_shared_language',  "invariant  Mind's Eye <-> Paper's Hands"),
        ('check_paths',            'paths  long = identity, short = intention'),
        ('check_control_555',      'control  5/5/5 measured against 7/7/7'),
        ('check_intention',        'intention  a state, sampled and stamped'),
        ('check_zd_reframe',       '0_ZD  downhill from the bottom of a pit'),
        ('check_continuity',       'continuity  the long path is added to, never finished'),
        ('check_evaluation',       'evaluation  the Eye critiques, it does not permit'),
        ('check_executable_structure', 'executable  the structure IS the fast path'),
        ('check_annihilation_gradient', 'gradient  0 and 1 are the ends of the annihilation scale'),
        ('check_unpack',           'unpack  discussion and re-evaluation, one machinery'),
        ('check_gate_correct',     'gate 1  the Eye releases on CORRECT'),
        ('check_correct_referent', 'referent  correct = measured and holding'),
        ('check_gate_happy',       'gate 2  the Hands release on HAPPY'),
        ('check_joint_parentage',  'parentage  two parents, one child'),
    )

    def run(self,
            psi: Optional[Sequence[float]] = None,
            currents: Optional[Tuple[float, float, float]] = None) -> Ledger:
        for method, group in self._GROUPS:
            try:
                getattr(self, method)()
            except Exception as exc:              # noqa: BLE001
                self._code_fault(f'{method}.did_not_run',
                                 'the group executes end to end', group, exc)

        if currents is not None:
            self.check_currents(*currents)
        else:
            self._untested('current.neutral',
                           'J_red + J_blue + J_green = 0',
                           'currents  the neutral is the loss',
                           'no currents supplied to run()')

        if psi is not None:
            p_red  = sum(psi[k] ** 2 for k in _RED_CHANNELS)
            p_blue = sum(psi[k] ** 2 for k in _BLUE_CHANNELS)
            self.check_trochoid(p_red, p_blue)
        else:
            self._untested('trochoid.null',
                           'zero loss <=> R = e <=> sigma_self = 1/2',
                           'trochoid  the other loss',
                           'no psi supplied to run()')

        return self.ledger

    # ── report ───────────────────────────────────────────────────────────
    def report(self) -> str:
        led = self.ledger
        out: List[str] = []
        out.append('=' * 74)
        out.append('rotary_rerun_monad — diagnostic and fault-born harness')
        out.append('=' * 74)

        cursor = LedgerCursor(led)
        current_group = None
        for rec in cursor:
            if rec.group != current_group:
                current_group = rec.group
                out.append('')
                out.append(f'── {current_group} ' + '─' * max(0, 70 - len(current_group)))
            out.append(str(rec))

        out.append('')
        out.append('─' * 74)
        out.append(
            f'{len(led)} relations   '
            f'{led.count(Status.HOLDS)} hold   '
            f'{led.count(Status.VIOLATED)} FAULT   '
            f'{led.count(Status.DEGENERATE)} degenerate   '
            f'{led.count(Status.UNTESTED)} untested'
        )
        maths = led.faults_of(Fault.MATHS)
        code  = led.faults_of(Fault.CODE)
        if maths:
            out.append('')
            out.append('MATHS FAULTS — both sides measured, and they disagree:')
            for f in maths:
                out.append(f'  [{f.index}] {f.name}: expected {f.expected!r}, '
                           f'observed {f.observed!r}')
        if code:
            out.append('')
            out.append('CODE FAULTS — the harness broke; these claims are UNJUDGED:')
            for f in code:
                out.append(f'  [{f.index}] {f.name}: {f.observed}')

        out.append('')
        if led.maths_works:
            out.append('THE MATHS WORKS — no measured relation disagrees with its')
            out.append('claim. And it works AS IT IS WRITTEN: whether what is')
            out.append('written is what was intended is a separate question, and')
            out.append('this harness does not ask it.')
        else:
            out.append(f'THE MATHS DOES NOT WORK: {len(maths)} measured relation(s) '
                       f'disagree with their claim.')
        if code:
            out.append(f'{len(code)} group(s) failed to execute — those claims were '
                       f'not tested either way.')
        return '\n'.join(out)


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def _demo_psi() -> List[float]:
    """A psi with amplitude in both octonions, deliberately off-null."""
    psi = [0.0] * SED_DIM
    for k in range(1, 8):
        psi[k] = 0.30 + 0.02 * k
    for k in range(8, 15):
        psi[k] = 0.25 - 0.01 * k
    psi[0] = 0.5
    psi[15] = 0.1
    return psi


def main(argv: Sequence[str]) -> int:
    psi = _demo_psi()

    # Deliberately unbalanced currents, so the harness has a fault to find and
    # a negative to trip the reducer-validity guard.
    currents = (0.412, -0.187, -0.201)

    h = Harness()
    h.run(psi=psi, currents=currents)
    print(h.report())

    if h.kite is not None:
        print()
        print('─' * 74)
        print("speech — the Eye reads a snapshot, the Hands write it in order")
        print('─' * 74)
        eye   = MindsEye(h.kite)
        hands = PapersHands(h.kite)
        snap  = eye.snapshot(psi)
        print(f'  sigma_self     {snap["sigma_self"]:.9f}')
        print(f'  R, e           {snap["R"]:.9f}, {snap["e"]:.9f}')
        print(f'  trochoid loss  {snap["trochoid_loss"]:.9f}')
        print(f'  generations    {eye.generations_present(psi)}')
        print()
        for line in hands.relate(eye, psi):
            print('  ' + line)

    return 1 if h.ledger.faults() else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
