#!/usr/bin/env python3
"""
001_original_2026-05-27_word_zero_idx.py

The original "primes are the words" semantic prime hash — P1 only
(the address; P2, the Z(t) Newton zero-value solver, is a separate,
optional refinement not needed to produce the address itself).

Extracted verbatim from VAPMIP/monad.py as it stood at commit 204c75d
("2026-05-27: buoyancy scoring, NS constants, J_ambient calibration"),
the commit that introduced this mechanism. Confirmed byte-identical to
the version still in VAPMIP/monad.py today, 2026-09 — this piece has
never been altered since it was first written.

    git -C VAPMIP log --follow --oneline -S "_word_zero_idx" -- monad.py
    git -C VAPMIP show 204c75d:monad.py

This file adds only the cross-language test block at the bottom
(run 2026-09-19, against the live, unaltered mechanism) — not present
in the original commit, added here to show what a blind re-run of the
original hypothesis actually produces.
"""
from typing import List

# ── P1: Prime hash — word → prime address → Riemann zero index ────────────────
#
# Design:
#   Each word gets an E-value derived from its position on the critical line,
#   not from its registration order.  The path:
#     word → Horner base-95 int → next prime p in [2, _PRIME_CAP]
#          → π(p) = zero index → γ[zero_idx] via Z(t) Newton (not needed here)
#
#   _PRIME_CAP = 2^16 → 6542 distinct prime addresses.
#   [2026-09-19 note: this undercounts by one — 65537 is itself prime, so
#    the true range is [1, 6543]. Left as originally written; see the
#    paper's own §3 for where this was caught.]

_PRIME_CAP = 1 << 16          # 65536 — primes searched in [2, 65537]

# Build sieve of Eratosthenes (runs once at import)
_cap = _PRIME_CAP + 2
_sv  = bytearray([1]) * _cap
_sv[0] = _sv[1] = 0
for _i in range(2, int(_cap ** 0.5) + 1):
    if _sv[_i]:
        _sv[_i * _i :: _i] = bytearray(len(_sv[_i * _i :: _i]))

# Precompute π(k) — count of primes ≤ k, for k in [0, _PRIME_CAP]
_prime_pi_table: List[int] = [0] * _cap
_cnt = 0
for _k in range(_cap):
    if _sv[_k]:
        _cnt += 1
    _prime_pi_table[_k] = _cnt
del _i, _k, _cnt, _cap


def _next_prime(v: int) -> int:
    """
    Smallest prime p ≥ (v mod _PRIME_CAP), clamped to [2, 65537].

    :param v: Non-negative integer.
    :returns: A prime in [2, 65537].
    :rtype: int
    """
    v = max(2, int(v) % (_PRIME_CAP + 1))
    while v <= _PRIME_CAP + 1:
        if _sv[min(v, _PRIME_CAP + 1)] or v > _PRIME_CAP:
            return v
        v += 1
    return 65537   # largest prime ≤ 65537


def _horner_hash(w: str, base: int = 95, offset: int = 32) -> int:
    """
    Horner base-95 hash of word string. Returns a non-negative integer.
    ord range [32, 126] (printable ASCII) → coefficients in [0, 94].

    :param w: Word string (already cleaned/lowercased).
    :param base: Polynomial base (95 = printable ASCII range).
    :param offset: ord offset.
    :returns: Non-negative integer.
    :rtype: int
    """
    v = 0
    for ch in w:
        v = v * base + max(0, ord(ch) - offset)
    return abs(v)


def _word_zero_idx(w: str) -> int:
    """
    P1 prime hash: word → Horner int → next prime p → π(p) = zero index.

    :param w: Cleaned word string.
    :returns: Zero index in [1, 6542].
    :rtype: int
    """
    v = _horner_hash(w)
    p = _next_prime(v)
    idx = _prime_pi_table[min(p, _PRIME_CAP + 1)]
    return max(1, idx)


# ── 2026-09-19 re-run: the original cross-language hypothesis, tested ────────
if __name__ == "__main__":
    print("=== tree ===")
    for lang, w in [("en", "tree"), ("es", "árbol"), ("zh", "树")]:
        print(f"  {lang}  {w!r:10s}  idx={_word_zero_idx(w)}")

    print("=== water ===")
    for lang, w in [("en", "water"), ("fr", "eau"), ("ja", "水")]:
        print(f"  {lang}  {w!r:10s}  idx={_word_zero_idx(w)}")

    print("=== water/eau/aqua/wasser (Ainulindale wiki-16's own cited example) ===")
    for w in ["water", "eau", "aqua", "wasser"]:
        print(f"  {w!r:10s}  idx={_word_zero_idx(w)}")

    print()
    print("None of the above groups share an idx under this mechanism, run blind,")
    print("today — including wiki-16's own example words. This is the honest,")
    print("reproducible shape of the 'semantic neighborhood' finding: the address")
    print("space places every word somewhere (mechanically true by construction),")
    print("but does not, on its own, place cross-language synonyms at the same")
    print("address. See the paper's §3 for what that does and does not mean.")
