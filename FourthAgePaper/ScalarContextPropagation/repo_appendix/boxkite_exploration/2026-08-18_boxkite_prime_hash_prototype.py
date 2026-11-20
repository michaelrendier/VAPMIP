#!/usr/bin/env python3
"""boxkite_prime_hash.py — the Box Kite Context as the prime hashing algorithm.

PROTOTYPE. python3 first; PtolC/ only once this is significant.

THE TWO TIERS, SPLIT AT THE 20TH PRIME

    primes <=  71    LETTERS   spelling, muscle memory. 20 of them.
    primes >   71    CONTEXT   knowledge-bearing. everything above.

CORRECTED 2026-08-18. This file previously capped the letters at 313, which
fused two unrelated facts: 313 is the last prime to claim anything NEW at
N = 1e5 (the sieve's productive/redundant boundary, sqrt(1e5) = 316.23), and it
is the 65TH prime — not the 21st. The letter count is ~20, and monad.py already
says so: PRIMES and RIEMANN_ZEROS both have 20 entries, ending at 71.

The letter arithmetic, measured:

    26  modern English
    23  classical Latin (J split from I in 1524, U/V likewise, W is a digraph)
    20  with H, I, J collapsing toward Y

0 AND 1 CANNOT BE ADDED. 1 is a unit — exactly one divisor, so no address at
all — and admitting it destroys unique factorisation, which is the only thing
holding this encoding up. 0 is absorbing: 0 * anything = 0, so every word would
encode to the same value. Neither is prime, and for two different reasons.

THE ENCODING

A word's box kite context is a vector of exponents over the 42 assessors.
Measured with the corrected cap: 42 assessors give a 94-digit squarefree code,
where at cap 313 they gave 112 and did not fit. The letter-cap error was
costing the encoding its entire assessor layer. 35 PG(3,2) lines now cost 77,
and 44 channels fit under 100.

    code  = prod over lines of p_i ^ e_i      unique by FTA, factors back
    addr  = next_prime(code)                  the single prime output
    delta = addr - code                       the clarifier

COLLISIONS ARE FORCED AND THEY ARE NOT FAULTS

next_prime is a rounding operator and it quantizes at the prime gap: at 92
digits the mean gap is ln(10^92) ~ 212, so roughly 212 distinct contexts share
each output prime. That cannot be engineered away and it should not be.

    a collision is a DISCUSSION, not a fault.

Two words landing on one address have arrived at the same neighbourhood by
different routes, and `delta` recovers which route each took. So the response
to a collision is `unpack()` — "I'm going to need you to unpack that" — which
returns what each context actually says and where they part company. The pair
(addr, delta) is reversible; addr alone is not. Toffoli, not a hash: the
one-wayness was never in the arithmetic, only in discarding the operand.
"""

from __future__ import annotations
import math
from typing import Dict, List, Sequence, Tuple

LETTER_CAP = 71        # the 20th prime; see the two-tiers note above


def _sieve(n: int) -> List[int]:
    sv = bytearray([1]) * (n + 1)
    sv[0] = sv[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    return [i for i in range(n + 1) if sv[i]]


_P = _sieve(20000)
LETTER_PRIMES: List[int] = [p for p in _P if p <= LETTER_CAP]
CONTEXT_PRIMES: List[int] = [p for p in _P if p > LETTER_CAP]


def _is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin for the range we work in."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
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


class BoxKiteAddress:
    """One knowledge-bearing word, addressed by its whole box kite context.

    `lines` is the exponent vector over the 35 lines of PG(3,2). Zero means the
    word does not touch that line; a positive exponent is how strongly it does,
    exactly as Intention encodes magnitude.
    """

    __slots__ = ('surface', 'lines', 'code', 'addr', 'delta')

    N_LINES = 42       # the assessors — they fit now

    def __init__(self, surface: str, lines: Sequence[int]) -> None:
        if len(lines) != self.N_LINES:
            raise ValueError(f'need {self.N_LINES} line exponents, got {len(lines)}')
        if any(e < 0 for e in lines):
            raise ValueError('a negative exponent is a commitment against a line, '
                             'which is a different object')
        self.surface = surface
        self.lines = tuple(int(e) for e in lines)
        self.code = 1
        for p, e in zip(CONTEXT_PRIMES, self.lines):
            if e:
                self.code *= p ** e
        self.addr = next_prime(self.code)
        self.delta = self.addr - self.code

    # ── reversibility: the record was kept, so nothing is one-way ────────
    def recovered_code(self) -> int:
        """addr - delta. The operand was retained, so this is exact."""
        return self.addr - self.delta

    def factored(self) -> Dict[int, int]:
        """The code back into its lines. FTA guarantees this is unique."""
        out: Dict[int, int] = {}
        c = self.recovered_code()
        for i, p in enumerate(CONTEXT_PRIMES[:self.N_LINES]):
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
        return (f'BoxKiteAddress({self.surface!r}, {self.digits()} digits, '
                f'delta={self.delta})')


def collides(a: BoxKiteAddress, b: BoxKiteAddress) -> bool:
    return a.addr == b.addr and a.code != b.code


def unpack(a: BoxKiteAddress, b: BoxKiteAddress) -> Dict[str, object]:
    """"I'm going to need you to unpack that for me."

    A collision is not a fault and not an ambiguity — it is two contexts that
    arrived at one neighbourhood by different routes, and both routes are still
    fully recoverable. This returns the discussion: what each one holds, what
    they hold in common, and where they part.

    gcd is componentwise MIN — the shared minimum context, which is what the
    two of them can actually talk about. The symmetric difference is the
    disagreement, and it is the interesting half.
    """
    fa, fb = a.factored(), b.factored()
    shared = {i: min(fa[i], fb[i]) for i in set(fa) & set(fb)}
    only_a = {i: fa[i] for i in set(fa) - set(shared)}
    only_b = {i: fb[i] for i in set(fb) - set(shared)}
    return {
        'same_address':  a.addr == b.addr,
        'same_context':  a.code == b.code,
        'shared_lines':  shared,
        'only_first':    only_a,
        'only_second':   only_b,
        'separation':    abs(a.code - b.code),
        'resolved_by':   ('identical context' if a.code == b.code else
                          f'delta: {a.delta} vs {b.delta}'),
    }
