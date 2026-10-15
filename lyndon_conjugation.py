"""
lyndon_conjugation.py -- STUB. Lyndon factorisation as the part of the equation that will handle conjugations and tenses.

STATUS (2026-10-14): the Lyndon core below is real and checked (`verify()`). The two hooks that
would make it a conjugation/tense mechanism, `conjugates()` and `inflection_frame()`, are STUBS
that raise NotImplementedError: the design is not settled, and this file does not guess it.
Nothing imports this file yet; it is not woven into the equation, the harness, or any Monad.

Why Lyndon words (from the Collatz work, FourthAgePapers/CollatzShift, and Cody's reading of it): a Lyndon
word is a word strictly smaller than all of its proper rotations. The Chen-Fox-Lyndon theorem: every word
factors UNIQUELY as a concatenation of Lyndon words in non-increasing order. Lyndon words are the
"primes" of words; the factorisation is the word-level fundamental theorem of arithmetic, the same
kind of object as the project's word-primes and sentence constructor.

One naming caution, kept explicit: in combinatorics on words, two words are CONJUGATE when one is a
rotation of the other (uv ~ vu). That is the necklace / cyclic-class sense. Whether it is the same
thing as grammatical conjugation (verb forms) is a question for the design, not something this stub
assumes. `conjugates()` below is written for the combinatorial sense only, and its stub status
refers to the grammatical sense.

What the real core provides (all stdlib, exact):
    duval(word)            the Lyndon factorisation (Duval's algorithm, one linear pass)
    is_lyndon(word)        the definition, tested directly
    least_rotation(word)   the canonical necklace representative
    primitive_root(word)   the smallest u with word = u^k, and k
    necklace_class(word)   all distinct rotations (the combinatorial conjugacy class)
    verify()               exhaustive check of the theorem over short words
"""
from __future__ import annotations

from itertools import product
from typing import List, Sequence, Tuple


def is_lyndon(w: Sequence) -> bool:
    """True when ``w`` is non-empty and strictly smaller than every proper rotation."""
    n = len(w)
    return n > 0 and all(tuple(w) < tuple(w[i:]) + tuple(w[:i]) for i in range(1, n))


def duval(w: Sequence) -> List[Tuple]:
    """The Lyndon factorisation of ``w``: Lyndon words ``l1 >= l2 >= ... >= lk`` with ``w = l1 l2 ... lk``."""
    w = tuple(w)
    n, i, out = len(w), 0, []
    while i < n:
        j, k = i + 1, i
        while j < n and w[k] <= w[j]:
            k = i if w[k] < w[j] else k + 1
            j += 1
        while i <= k:
            out.append(w[i:i + j - k])
            i += j - k
    return out


def least_rotation(w: Sequence) -> Tuple:
    """The least rotation of ``w`` (the canonical necklace representative)."""
    w = tuple(w)
    return min(w[i:] + w[:i] for i in range(len(w))) if w else w


def primitive_root(w: Sequence) -> Tuple[Tuple, int]:
    """``(u, k)`` with ``w = u^k`` and ``u`` the shortest such word."""
    w = tuple(w)
    n = len(w)
    for d in range(1, n + 1):
        if n % d == 0 and w[:d] * (n // d) == w:
            return w[:d], n // d
    return w, 1


def necklace_class(w: Sequence) -> List[Tuple]:
    """The distinct rotations of ``w``: its class under conjugation in the combinatorial sense (uv ~ vu)."""
    w = tuple(w)
    return sorted({w[i:] + w[:i] for i in range(len(w))}) if w else [w]


def conjugates(word: Sequence) -> List[Tuple]:
    """STUB. Intended: the grammatical conjugation mechanism. Not designed; not built.

    :raises NotImplementedError: always. For the combinatorial sense use :func:`necklace_class`.
    """
    raise NotImplementedError("grammatical conjugation via Lyndon factors is not designed yet (stub)")


def inflection_frame(word: Sequence) -> dict:
    """STUB. Intended: the tense/inflection layer, woven into the equation. Not designed; not built.

    :raises NotImplementedError: always.
    """
    raise NotImplementedError("tense/inflection via Lyndon factors is not designed yet (stub)")


def verify(max_len: int = 10, alphabet: Sequence = "ab") -> dict:
    """Exhaustive check of Chen-Fox-Lyndon over every word of length <= ``max_len`` on ``alphabet``.

    Checks, for each word: the factors concatenate to the word, each factor is Lyndon, the factors
    are non-increasing, and the number of Lyndon words of each length equals (1/n) sum mu(d) k^(n/d).
    """
    def mu(n):
        r, m, p = 1, n, 2
        while p * p <= m:
            if m % p == 0:
                m //= p
                if m % p == 0:
                    return 0
                r = -r
            p += 1
        return -r if m > 1 else r
    k = len(alphabet)
    words = bad = 0
    count = {}
    for n in range(1, max_len + 1):
        for w in product(alphabet, repeat=n):
            words += 1
            f = duval(w)
            ok = (tuple(x for l in f for x in l) == w and all(is_lyndon(l) for l in f)
                  and all(f[i] >= f[i + 1] for i in range(len(f) - 1)))
            bad += not ok
            count[n] = count.get(n, 0) + is_lyndon(w)
    formula = {n: sum(mu(d) * k ** (n // d) for d in range(1, n + 1) if n % d == 0) // n for n in range(1, max_len + 1)}
    return {"words_checked": words, "failures": bad, "lyndon_counts": count, "counts_match_formula": count == formula}


if __name__ == "__main__":
    print(verify())
    for s in ("banana", "abracadabra", "the cat sat on the mat".split()):
        print(s if isinstance(s, str) else " ".join(s), "->", ["".join(x) if isinstance(s, str) else " ".join(x) for x in duval(s)])
    for fn in (conjugates, inflection_frame):
        try:
            fn("walk")
        except NotImplementedError as e:
            print(fn.__name__, "->", "NotImplementedError:", e)
