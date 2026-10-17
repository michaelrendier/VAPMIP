#!/usr/bin/env python3
"""lineage_hash.py — generational lineage prime hashing, three faces.

Built 2026-08-18. python3 first; PtolC/ only on a significant result.

═══════════════════════════════════════════════════════════════════════════
THE THREE FACES OF LANGUAGE  (not the engine's 7:7:7 trine — a different 3)
═══════════════════════════════════════════════════════════════════════════

    LETTERS   are spelling         are MUSCLE MEMORY
    WORDS     are CONTEXT-BEARING INTENTION, and their ORDER MATTERS
    PATHWAYS  are how ideas and concepts are built

Speaking is not a fourth face. It is the TRAVERSAL ORDER of the third.

═══════════════════════════════════════════════════════════════════════════
THE ONE DESIGN DECISION THAT ORGANISES EVERYTHING: COMMUTATIVITY
═══════════════════════════════════════════════════════════════════════════

Each face gets the encoding its own algebra demands, and the discriminator is
whether order carries information:

    face 1-2  LETTERS, WORDS    ORDER MATTERS      -> POSITIONAL encoding
                                                      (Horner: bijective,
                                                       order-preserving, compact)
    face 3    PATHWAYS          order does NOT     -> MULTIPLICATIVE encoding
                                                      (prime product: commutative,
                                                       set-like, gcd == LCA)

This is not a convenience. Commutativity is lost at generation 1 of the
Cayley-Dickson tower (`ab != ba`), and the faces sit on opposite sides of that
loss. A word is a sequence and 'dog' != 'god'. A set of ideas is a set, and
{animal, mammal} == {mammal, animal}. Encoding either one the other way
destroys exactly the information that face exists to carry.

═══════════════════════════════════════════════════════════════════════════
THE GENERATIONAL LADDER IS FERMAT
═══════════════════════════════════════════════════════════════════════════

    F_n = 2^(2^n) + 1  IS the Cayley-Dickson doubling index, by construction.

    F_0 = 3      generation 0   ranking   (C)   order as RANKING lost
    F_1 = 5      generation 1   factors   (H)   ab != ba
    F_2 = 17     generation 2   GROUPING  (O)   (ab)c != a(bc)
    F_3 = 257    generation 3   division  (S)   zero divisors
    F_4 = 65537  generation 4   dim 32          -- outside the letter cap

    3 x 5 x 17 x 257 = 65535 = 2^16 - 1        <- the sedenion dimension.

A letter's prime CARRIES its generation: read it off by which Fermat band the
prime falls in. Same mechanism as a strut's binary expansion, different ladder.

The cap at 313 is not arbitrary and not the alphabet size: any cap in
[257, 65537) admits exactly the four generations the box kite has. pi(313)=65
is a POOL, not a letter count.

    nonempty subsets of {3,5,17,257}  = 15 = PG(3,2) points   (verified)
    those containing 257 (forced)     =  8 = 2^3
    minus the one with no free bits   =  7 = THE STRUTS

═══════════════════════════════════════════════════════════════════════════
THE JOIN: LETTERS DETERMINE THE STRUT
═══════════════════════════════════════════════════════════════════════════

A word's letters each carry a generation. OR their generation bits together
and you get the word's LINEAGE — which generations it crosses — and that is
its STRUT. So face 1 hands face 3 its box kite without anything being
assigned by hand.

Letters are mapped to primes in ENGLISH FREQUENCY ORDER, so the commonest
letters take the lowest primes and therefore the earliest generations. The
most frequent letters are the most ancestral, which makes generation a
measured property of usage rather than a label.
"""

from __future__ import annotations
import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# ── the ladder ───────────────────────────────────────────────────────────
FERMAT = [3, 5, 17, 257]                 # F_0..F_3 — the four generations
GENERATION = ('ranking', 'factors', 'GROUPING', 'division')
LETTER_CAP = 313                         # admits exactly F_0..F_3


def _sieve(n: int) -> List[int]:
    sv = bytearray([1]) * (n + 1)
    sv[0] = sv[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    return [i for i in range(n + 1) if sv[i]]


_P = _sieve(3_000_000)
LETTER_POOL: List[int] = [p for p in _P if p <= LETTER_CAP]        # 65
CONTEXT_PRIMES: List[int] = [p for p in _P if p > LETTER_CAP]


def generation(p: int) -> int:
    """Which Fermat band this prime falls in. The lineage, read off the value."""
    for n, f in enumerate(FERMAT):
        if p <= f:
            return n
    return len(FERMAT)          # beyond the letter tier


# ═══════════════════════════════════════════════════════════════════════
#  FACE 1 — LETTERS.  spelling, muscle memory.
# ═══════════════════════════════════════════════════════════════════════
# English frequency order: commonest letters take the lowest primes, so the
# most-used letters are the most ancestral. Generation becomes a measured
# property of usage rather than an assigned label.
FREQ_ORDER = 'etaoinshrdlcumwfgypbvkjxqz'
LETTER_PRIME: Dict[str, int] = {c: LETTER_POOL[i] for i, c in enumerate(FREQ_ORDER)}
PRIME_LETTER: Dict[int, str] = {v: k for k, v in LETTER_PRIME.items()}


def letter_generation(c: str) -> int:
    return generation(LETTER_PRIME[c])


def split_tiers(text: str) -> Tuple[str, str]:
    """TIER 0 out first. Whitespace, punctuation and invisible Unicode are the
    APERTURE — they select the domain and never enter a polynomial.

    This closes the live monad.py fault: `_horner_hash` clamps digits from
    below only, so U+200B becomes coefficient 8171 in a base-95 positional
    system and distinct strings collide. Here a non-letter cannot become a
    digit at all.
    """
    letters, delims = [], []
    for ch in text:
        if ch.isalpha() and ord(ch) < 128:
            letters.append(ch.lower())
        else:
            delims.append(ch)
    return ''.join(letters), ''.join(delims)


# ═══════════════════════════════════════════════════════════════════════
#  FACE 2 — WORDS.  composites, and ORDER MATTERS.
# ═══════════════════════════════════════════════════════════════════════
class Word:
    """A composite of letters. Positional, because 'dog' != 'god'.

    THREE THINGS COME OUT OF THE LETTERS, and only the first is the spelling:

        spell    Horner base-27 over letter indices. BIJECTIVE and ordered.
                 This IS the word — it is the retained record, and spelling is
                 one-way only if you discard `unspell`.
        lineage  the ORDERED sequence of letter generations. A path, not a set.
        strut    the OR of the generation bits. WHICH generations this word
                 crosses -> which box kite it belongs to. Handed to face 3.
    """

    __slots__ = ('surface', 'letters', 'delims', 'spell', 'lineage', 'strut')

    def __init__(self, surface: str) -> None:
        self.surface = surface
        self.letters, self.delims = split_tiers(surface)
        if not self.letters:
            raise ValueError(f'{surface!r} has no tier-1 content — it is pure aperture')

        v = 0
        for ch in self.letters:
            v = v * 27 + (FREQ_ORDER.index(ch) + 1)
        self.spell = v

        self.lineage = tuple(letter_generation(c) for c in self.letters)

        bits = 0
        for g in self.lineage:
            bits |= (1 << g)
        self.strut = bits

    @staticmethod
    def unspell(v: int) -> str:
        out = []
        while v > 0:
            v, r = divmod(v - 1, 27)
            out.append(FREQ_ORDER[r])
        return ''.join(reversed(out))

    @property
    def generations(self) -> List[str]:
        """Which generations this word crosses, in build order."""
        return [GENERATION[b] for b in range(4) if self.strut & (1 << b)]

    @property
    def box_kite(self) -> Optional[int]:
        """The strut with the division bit forced, 1..7. None if it never
        reaches the division generation — such a word has no zero divisors
        and therefore no box kite to live in."""
        if not (self.strut & 0b1000):
            return None
        free = self.strut & 0b0111
        return free if free else None

    def __repr__(self) -> str:
        return (f'Word({self.surface!r} spell={self.spell} '
                f'strut={self.strut:04b} kite={self.box_kite})')


# ═══════════════════════════════════════════════════════════════════════
#  FACE 3 — PATHWAYS.  ideas, built as products.  order does NOT matter.
# ═══════════════════════════════════════════════════════════════════════
def _is_prime(n: int) -> bool:
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
    if n % 2 == 0:
        n += 1 if n > 2 else 0
    while not _is_prime(n):
        n += 2
    return n


class Pathway:
    """A set of ideas a word reaches. Commutative, so a PRODUCT.

    code  = prod over channels of p_c ^ e_c     unique by FTA, factors back
    addr  = next_prime(code)                    the single prime output

    next_prime is safe because codes are products of distinct primes and sit
    ~0.044*M apart multiplicatively while the prime gap is ~ln(M) additively —
    a ratio of 1e88 at 92 digits. It is injective on the code set in practice,
    so there is NO natural collision background: every code collision is a
    method error, deductively, by unique factorisation.
    """

    __slots__ = ('key', 'chan', 'code', 'addr', 'delta')

    def __init__(self, key: str, chan: Dict[int, int]) -> None:
        self.key = key
        self.chan = {c: e for c, e in chan.items() if e}
        code = 1
        for c, e in sorted(self.chan.items()):
            code *= CONTEXT_PRIMES[c] ** e
        self.code = code
        self.addr = next_prime(code)
        self.delta = self.addr - self.code

    def recovered(self) -> int:
        return self.addr - self.delta

    def digits(self) -> int:
        return len(str(self.addr))

    def __repr__(self) -> str:
        return f'Pathway({self.key!r}, {self.digits()}d, delta={self.delta})'


def descend(a: Pathway, b: Pathway) -> int:
    """gcd — componentwise MIN. THE DESCENT, and under an ancestor-channel map
    this IS the lowest common ancestor. The LCA is divided out, never searched."""
    return math.gcd(a.code, b.code)


def climb(shared_code: int, target: Pathway) -> int:
    """...and work your way back out. What the target adds beyond the shared."""
    return target.code // shared_code


def method_error(a: Pathway, b: Pathway) -> bool:
    """Distinct keys on one code. A correct encoder cannot do this — ever."""
    return a.key != b.key and a.code == b.code


# ═══════════════════════════════════════════════════════════════════════
#  THE THREE FACES, JOINED
# ═══════════════════════════════════════════════════════════════════════
class Lineage:
    """One utterance-level object carrying all three faces.

    The faces are NOT summed into one scalar. They are kept as three fields
    because they are three different algebras, and a single number would have
    to pick one and destroy the others. What joins them is that FACE 1
    DETERMINES THE STRUT AND THE STRUT SELECTS FACE 3's BOX KITE — a
    structural hand-off, not an arithmetic merge.
    """

    __slots__ = ('word', 'pathway')

    def __init__(self, surface: str, channels: Optional[Dict[int, int]] = None) -> None:
        self.word = Word(surface)
        self.pathway = Pathway(surface, channels or {}) if channels else None

    @property
    def strut(self) -> int:
        return self.word.strut

    def report(self) -> Dict[str, object]:
        return {
            'surface':     self.word.surface,
            'letters':     self.word.letters,
            'aperture':    self.word.delims,
            'spell':       self.word.spell,
            'reversible':  Word.unspell(self.word.spell) == self.word.letters,
            'lineage':     self.word.lineage,
            'generations': self.word.generations,
            'strut':       f'{self.word.strut:04b}',
            'box_kite':    self.word.box_kite,
            'addr':        self.pathway.addr if self.pathway else None,
            'digits':      self.pathway.digits() if self.pathway else None,
        }
