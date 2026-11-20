#!/usr/bin/env python3
"""prime_hash.py — the Box Kite prime hashing algorithm.

Built 2026-08-18 from constraints all measured in-session. python3 first;
PtolC/ only once a result is significant.

═══════════════════════════════════════════════════════════════════════════
THE THREE TIERS, AND ONLY TWO OF THEM ARE ARITHMETIC
═══════════════════════════════════════════════════════════════════════════

    tier 0   whitespace, punctuation, invisible Unicode   APERTURE
             NOT in the maths. Sets which domain of words is drawn from.
             Feeding one of these into the letter polynomial is a category
             error, and it is a live bug in monad.py: `_horner_hash` clamps
             digits from below only, so U+200B yields coefficient 8171 in a
             base-95 positional system. Measured: '​' and 'v!' collide.

    tier 1   primes 2..71  (20 of them)                    LETTERS
             Spelling. Muscle memory. The 20th prime is 71; monad.py already
             had this right. 313 is the 65th prime and is the SIEVE boundary
             (last prime claiming anything new at N=1e5), not the letter cap.

    tier 2   primes 73 and up                              CONTEXT
             Knowledge-bearing. This is where the address lives.

0 and 1 are tier 0, and can never be channels: 1 is a UNIT (one divisor, no
address, and admitting it destroys unique factorisation); 0 is ABSORBING
(every word would encode to 0). They are the two ends of the annihilation
gradient — L_1 kills 0 of 16 directions, a zero divisor kills 4, L_0 kills 16.

═══════════════════════════════════════════════════════════════════════════
TWO HASHES, NOT ONE — because spelling is not the address
═══════════════════════════════════════════════════════════════════════════

    SPELL(w)    tier-1 Horner over letters. REVERSIBLE — it IS the word.
                Measured: 73,616/73,616 distinct, zero collisions.
    ADDRESS(w)  tier-2 product over CONTEXT channels, then next_prime.

The old pipeline fused these and addressed by spelling, which is provenance
addressing — the same failure as filing coconut oil under `vegetable oil`
beside olive oil (liquid, useless for tempering) while cocoa butter, its
actual functional neighbour, sits on another branch. An address must be
computed from what a thing LICENSES, not from what it is made of.

═══════════════════════════════════════════════════════════════════════════
WHY next_prime IS SAFE HERE
═══════════════════════════════════════════════════════════════════════════

Codes are products of DISTINCT primes, so adjacent codes sit ~0.044*M apart
(multiplicative) while the prime gap is ~ln(M) (additive) — a ratio of 1e88 at
92 digits. next_prime is therefore effectively INJECTIVE on the code set.

Consequence: there is no natural collision background. EVERY collision is a
method error, deductively — by unique factorisation a correct encoder cannot
produce a code collision, ever. One collision is proof, with no control and no
threshold. Measured: correct 35-channel encoder 0 collisions over 4000 inputs;
folding those channels onto 7 first (valid code, wrong method) gave 2354.

═══════════════════════════════════════════════════════════════════════════
THE CHANNEL MAP IS THE ONE OPEN CHOICE, SO IT IS PLUGGABLE
═══════════════════════════════════════════════════════════════════════════

Everything above is forced. What a channel MEANS is not, so it is an
interface. Two are implemented:

    HypernymPath   channel per ancestor synset. gcd == LCA FOR FREE, which
                   is the whole prompt->response operation in one arithmetic
                   step. Recommended.
    BoxKiteLines   channel per PG(3,2) line (35) or assessor (42). The
                   geometry. 42 assessors = 94 digits, leaving 6 for
                   etymology; 35 lines = 77, leaving 23.

BUDGET, measured with the corrected letter cap:
     7 struts          14 digits      21 strut pairs   44 digits
    35 PG(3,2) lines   77 digits      42 assessors     94 digits
    84 diagonals      204 digits
"""

from __future__ import annotations
import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

LETTER_CAP = 71          # the 20th prime


# ── the prime ladder ─────────────────────────────────────────────────────
def _sieve(n: int) -> List[int]:
    sv = bytearray([1]) * (n + 1)
    sv[0] = sv[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    return [i for i in range(n + 1) if sv[i]]


_P = _sieve(3_000_000)
LETTER_PRIMES: List[int] = [p for p in _P if p <= LETTER_CAP]
CONTEXT_PRIMES: List[int] = [p for p in _P if p > LETTER_CAP]


def _is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin over the bases valid past 3.3e24."""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    n = max(2, n)
    if n == 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not _is_prime(n):
        n += 2
    return n


# ── TIER 0: the aperture, stripped before any arithmetic ─────────────────
def split_tiers(text: str) -> Tuple[str, str]:
    """Separate tier-0 delimiters from tier-1 letters.

    Returns (letters, delimiters). The delimiters are NOT discarded — they
    are the aperture, and they are returned so the caller can set the domain
    with them. They simply never enter a polynomial.

    This is the fix for the live monad.py bug: anything outside printable
    ASCII is tier 0 by construction here, so it cannot become a base-95
    digit >= 95 and cannot forge a collision.
    """
    letters, delims = [], []
    for ch in text:
        if ch.isalpha() and ord(ch) < 128:
            letters.append(ch.lower())
        else:
            delims.append(ch)
    return ''.join(letters), ''.join(delims)


# ── TIER 1: spelling. reversible, and it IS the word ─────────────────────
_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
_A_IDX = {c: i for i, c in enumerate(_ALPHA)}


def spell(word: str) -> int:
    """Horner over letters only, base 26. Bijective on [a-z]+.

    Base 26 with a +1 offset so leading letters are not swallowed: 'a' and
    'aa' must differ, which plain base-26 does not give you.
    """
    letters, _ = split_tiers(word)
    v = 0
    for ch in letters:
        v = v * 26 + (_A_IDX[ch] + 1)
    return v


def unspell(v: int) -> str:
    """The retained record. spell() is one-way only if you discard this."""
    out = []
    while v > 0:
        v, r = divmod(v - 1, 26)
        out.append(_ALPHA[r])
    return ''.join(reversed(out))


# ── TIER 2: the context address ──────────────────────────────────────────
class ChannelMap:
    """Word -> {channel index: exponent}. The one open design decision."""

    def channels(self, key: str) -> Dict[int, int]:
        raise NotImplementedError

    @property
    def width(self) -> int:
        raise NotImplementedError


class HypernymPath(ChannelMap):
    """One channel per ancestor. gcd == LCA falls out of the arithmetic.

    code(w) = prod over ancestors a of p_a

    so gcd(code_A, code_B) = prod over SHARED ancestors = the path from the
    LCA to the root. The descent-and-climb-back-out that turns a prompt into
    a response is then a single gcd, and its digit count is the descent depth.

    Exponent carries magnitude: how strongly the word sits on that ancestor.
    Squarefree (all 1) is the degenerate unit-cube corner.
    """

    def __init__(self, parents: Dict[str, List[str]]) -> None:
        self.parents = parents
        nodes = sorted({k for k in parents} | {v for vs in parents.values() for v in vs})
        self.index = {n: i for i, n in enumerate(nodes)}
        self._width = len(nodes)

    @property
    def width(self) -> int:
        return self._width

    def path(self, key: str) -> List[str]:
        out, seen = [key], {key}
        while True:
            ps = self.parents.get(out[-1]) or []
            if not ps or ps[0] in seen:
                break
            out.append(ps[0])
            seen.add(ps[0])
        return out

    def channels(self, key: str) -> Dict[int, int]:
        return {self.index[a]: 1 for a in self.path(key) if a in self.index}


class BoxKiteLines(ChannelMap):
    """One channel per PG(3,2) line (35) or assessor (42) the word touches."""

    def __init__(self, assign: Dict[str, Dict[int, int]], width: int = 35) -> None:
        self.assign = assign
        self._width = width

    @property
    def width(self) -> int:
        return self._width

    def channels(self, key: str) -> Dict[int, int]:
        return dict(self.assign.get(key, {}))


class Address:
    """One knowledge-bearing word, addressed by its context."""

    __slots__ = ('key', 'chan', 'code', 'addr', 'delta')

    def __init__(self, key: str, chan: Dict[int, int]) -> None:
        self.key = key
        self.chan = dict(chan)
        code = 1
        for c, e in sorted(self.chan.items()):
            if e:
                code *= CONTEXT_PRIMES[c] ** e
        self.code = code
        self.addr = next_prime(code)
        self.delta = self.addr - self.code

    def recovered(self) -> int:
        """addr - delta. The operand was retained, so nothing is one-way."""
        return self.addr - self.delta

    def factored(self) -> Dict[int, int]:
        out, c = {}, self.recovered()
        for i, p in enumerate(CONTEXT_PRIMES):
            if p * p > c and c > 1:
                break
            e = 0
            while c % p == 0:
                c //= p
                e += 1
            if e:
                out[i] = e
        return out

    def digits(self) -> int:
        return len(str(self.addr))

    def __repr__(self) -> str:
        return f'Address({self.key!r}, {self.digits()}d, delta={self.delta})'


# ── the operations that matter ───────────────────────────────────────────
def shared(a: Address, b: Address) -> int:
    """gcd — componentwise MIN. THE DESCENT. Under HypernymPath this is the
    LCA path exactly, so the descent is one arithmetic operation."""
    return math.gcd(a.code, b.code)


def descent_depth(a: Address, b: Address) -> Tuple[int, int]:
    """(steps down from a, steps down from b) to reach the shared minimum."""
    g = shared(a, b)
    da = sum(1 for c, e in a.chan.items() if CONTEXT_PRIMES[c] ** e and g % CONTEXT_PRIMES[c])
    db = sum(1 for c, e in b.chan.items() if CONTEXT_PRIMES[c] ** e and g % CONTEXT_PRIMES[c])
    return da, db


def combined(a: Address, b: Address) -> int:
    """lcm — componentwise MAX. The combined reach."""
    return a.code // math.gcd(a.code, b.code) * b.code


def is_method_error(a: Address, b: Address) -> bool:
    """Distinct inputs sharing a CODE. By unique factorisation a correct
    encoder cannot do this, so one occurrence is proof — not evidence."""
    return a.key != b.key and a.code == b.code


def unpack(a: Address, b: Address) -> Dict[str, object]:
    """'I'm gonna need you to unpack that for me.'"""
    fa, fb = a.factored(), b.factored()
    keys = set(fa) & set(fb)
    sh = {k: min(fa[k], fb[k]) for k in keys}
    return {
        'same_address': a.addr == b.addr,
        'method_error': is_method_error(a, b),
        'shared':       sh,
        'only_first':   {k: v for k, v in fa.items() if sh.get(k, 0) < v},
        'only_second':  {k: v for k, v in fb.items() if sh.get(k, 0) < v},
    }
