#!/usr/bin/env python3
"""
monad_addressing.py — fix and verify the monad's word->zero addressing.

THE BUG (found 2026-07-28, monad.c:170 monad_word_coords)

    uint64_t v = 0;
    for (...) v = v * 95ULL + ci;              /* base-95 Horner   */
    double seed = fmod((double)v * MONAD_PHI, 1.0);

`(double)v` has a 53-bit mantissa. 95^8 = 6.63e15 fits under 2^53 = 9.01e15;
95^9 = 6.30e17 does not. Past 2^53 the low-order bits — the ONLY bits
fmod(.,1.0) depends on — are gone, so seed collapses to exactly 0.0.

Consequence, measured on the WordNet build:

    len   in corpus   seated   survival
      6      11547      4836    41.88%
      7      14044        47     0.33%
      8      15013         0     0.00%
      9+     ~60000        0     0.00%

Every word of 8+ characters lands at idx 0 with E = D_STAR = 0.246, the
MINIMUM possible E, so it then loses monad.c:464's `E > vocab[idx].E`
contest to whatever already holds slot 0. ~60,000 of 101,916 unique corpus
tokens are unaddressable. 'philadelphos' sits at z#0 with E=0.2460 because
its address OVERFLOWED to zero, not because the field selected it.

THE FIX — Fibonacci/Knuth multiplicative hashing, exact in integer arithmetic

    uint64_t h = v * 0x9E3779B97F4A7C15ULL;    /* round(2^64 / phi), wraps */
    double seed = (double)h / 18446744073709551616.0;   /* h / 2^64 */

The multiply is done in uint64 where wraparound is defined and exact. The
double conversion happens ONLY at the end, on a value already confined to
[0, 2^64), and we need just ~15 bits of it to select 1 of N zeros — well
inside a double's 53. Same golden-ratio equidistribution the original was
reaching for, without ever asking a double to hold the low bits of a big
integer.

WHAT THIS DOES NOT FIX — stated so it is not mistaken for a capacity fix.
This is a HASH, not a bijection, and it was always many-to-one: 101,916
unique tokens into N=25,000 zeros collide ~4:1 by pigeonhole no matter how
good the hash is. The fix removes the LENGTH BIAS (long words no longer all
collapse to one slot); it does not raise the ceiling. Expect seated vocab to
rise toward N, not toward 101,916.

PRIME DIRECTIVE #1: the constant is round(2^64/phi), derived, not tuned.
Nothing here is fitted to make a distribution look better.
PRIME DIRECTIVE #2: old_coords() is kept and run side by side. Its failure
is the baseline every table below is measured against.

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import math
import re
import sys
from collections import Counter
from typing import Dict, List, Sequence, Tuple

U64 = (1 << 64) - 1
TWO64 = float(1 << 64)

# round(2^64 / phi) — Knuth's multiplicative-hash constant. Derived, not chosen.
PHI_64 = 0x9E3779B97F4A7C15

MONAD_PHI = 1.618033988749895
D_STAR = 0.246
OMEGA_ZS = 0.5671432904097838
N_ZEROS = 25000


def _horner95(surface: str) -> int:
    """base-95 Horner accumulation in uint64, exactly as monad.c does it."""
    v = 0
    for ch in surface:
        c = ord(ch)
        ci = (c - 32 + 1) if 32 <= c < 127 else 0
        v = (v * 95 + ci) & U64
    return v - 1 if v > 0 else 0


def old_coords(surface: str, N: int = N_ZEROS) -> Tuple[int, float, float]:
    """monad.c as it stands. Kept as the baseline (Prime Directive #2)."""
    v = _horner95(surface)
    seed = math.fmod(float(v) * MONAD_PHI, 1.0)
    if seed < 0.0:
        seed += 1.0
    idx = min(int(seed * N), N - 1)
    return idx, seed, D_STAR + seed * (OMEGA_ZS - D_STAR)


def new_coords(surface: str, N: int = N_ZEROS) -> Tuple[int, float, float]:
    """The proposed replacement. Integer multiply; double only at the end."""
    v = _horner95(surface)
    h = (v * PHI_64) & U64
    seed = h / TWO64
    idx = min(int(seed * N), N - 1)
    return idx, seed, D_STAR + seed * (OMEGA_ZS - D_STAR)


# ── uniformity tests ─────────────────────────────────────────────────────────

def chi_square_uniform(idxs: Sequence[int], N: int, bins: int = 100) -> Dict[str, float]:
    """
    Chi-square goodness-of-fit against uniform over [0,N).

    Reports the statistic and its z-score under the chi-square's own normal
    approximation (df large). No pass/fail threshold is hard-coded — the
    number is reported and interpreted in the output, not silently gated.
    """
    counts = Counter(i * bins // N for i in idxs)
    exp = len(idxs) / bins
    chi2 = sum((counts.get(b, 0) - exp) ** 2 / exp for b in range(bins))
    df = bins - 1
    z = (chi2 - df) / math.sqrt(2 * df)
    return {'chi2': chi2, 'df': df, 'z': z, 'bins': bins}


def ks_uniform(seeds: Sequence[float]) -> Dict[str, float]:
    """Kolmogorov-Smirnov distance of seeds from U[0,1)."""
    s = sorted(seeds)
    n = len(s)
    d = max(max(abs((i + 1) / n - x), abs(x - i / n)) for i, x in enumerate(s))
    return {'D': d, 'n': n, 'critical_95': 1.36 / math.sqrt(n)}


def length_bias(words: Sequence[str], coords) -> Dict[int, Dict[str, float]]:
    """Mean seed per word length. A working hash shows ~0.5 at every length."""
    by_len: Dict[int, List[float]] = {}
    for w in words:
        by_len.setdefault(len(w), []).append(coords(w)[1])
    return {L: {'n': len(v), 'mean_seed': sum(v) / len(v),
                'frac_exactly_zero': sum(1 for x in v if x == 0.0) / len(v)}
            for L, v in sorted(by_len.items())}


def collision_profile(words: Sequence[str], coords, N: int = N_ZEROS) -> Dict[str, object]:
    """
    Occupancy vs the balls-in-bins expectation.

    For n balls in N bins the expected number of occupied bins is
    N*(1 - (1-1/N)^n). A good hash lands near it; a broken one lands far
    below because everything piles into a few slots.
    """
    n = len(words)
    occ = Counter(coords(w)[0] for w in words)
    expected = N * (1.0 - (1.0 - 1.0 / N) ** n)
    return {'tokens': n, 'zeros': N, 'occupied': len(occ),
            'expected_occupied': expected,
            'ratio_to_expected': len(occ) / expected,
            'max_pileup': max(occ.values()),
            'at_idx0': occ.get(0, 0)}


def load_corpus_words(path: str, limit: int = None) -> List[str]:
    seen, out = set(), []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            for t in re.findall(r"[a-z']+", line.lower()):
                if len(t) >= 2 and t not in seen:
                    seen.add(t)
                    out.append(t)
                    if limit and len(out) >= limit:
                        return out
    return out


def _main(argv: List[str]) -> int:
    path = argv[1] if len(argv) > 1 else '/root/wordnet_dump.txt'
    print("monad_addressing.py — verify the fix BEFORE touching monad.c")
    print("=" * 74)
    try:
        words = load_corpus_words(path)
    except FileNotFoundError:
        print(f"no corpus at {path} — regenerate with PtolC/tools/dump_wordnet.py")
        return 2
    print(f"\ncorpus: {len(words)} unique tokens (len>=2), N={N_ZEROS} zeros")

    for label, fn in (("OLD (monad.c today)", old_coords), ("NEW (fibonacci)", new_coords)):
        idxs = [fn(w)[0] for w in words]
        seeds = [fn(w)[1] for w in words]
        chi = chi_square_uniform(idxs, N_ZEROS)
        ks = ks_uniform(seeds)
        col = collision_profile(words, fn)
        print(f"\n── {label} ──")
        print(f"   chi2={chi['chi2']:.1f} df={chi['df']} z={chi['z']:+.1f}"
              f"   (z near 0 = uniform)")
        print(f"   KS  D={ks['D']:.6f}  critical_95={ks['critical_95']:.6f}"
              f"   {'UNIFORM' if ks['D'] < ks['critical_95'] else 'NOT UNIFORM'}")
        print(f"   occupied zeros {col['occupied']} / expected {col['expected_occupied']:.0f}"
              f"  (ratio {col['ratio_to_expected']:.4f})")
        print(f"   max pile-up on one zero = {col['max_pileup']}   at idx0 = {col['at_idx0']}")
        print(f"   seeds exactly 0.0: {sum(1 for s in seeds if s == 0.0)}")

    print("\n── length bias (mean seed should be ~0.5 at EVERY length) ──")
    lo, ln = length_bias(words, old_coords), length_bias(words, new_coords)
    print(f"   {'len':>4} {'n':>7} {'OLD mean':>10} {'OLD zero%':>10} "
          f"{'NEW mean':>10} {'NEW zero%':>10}")
    for L in sorted(ln):
        if L > 14:
            continue
        o, n_ = lo[L], ln[L]
        print(f"   {L:>4} {n_['n']:>7} {o['mean_seed']:>10.6f} "
              f"{100*o['frac_exactly_zero']:>9.2f}% {n_['mean_seed']:>10.6f} "
              f"{100*n_['frac_exactly_zero']:>9.2f}%")

    print("\n── sanity: known words under the new addressing ──")
    for w in ['hot', 'cold', 'absolute', 'wonderful', 'philadelphos', 'extraordinary']:
        oi, os_, oe = old_coords(w)
        ni, ns, ne = new_coords(w)
        print(f"   {w:<14} old idx={oi:<6} E={oe:.6f}   ->   new idx={ni:<6} E={ne:.6f}")
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
