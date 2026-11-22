"""
zd_approach_directions.py
==========================
Directions of approach to a sedenion zero-divisor: does every direction
give the same output? Answer, computed exactly (not approximated): no --
and CORRECTED on 2026-07-10 after testing the full known population
(336 pairs, not just 5): there are exactly TWO sub-classes, not one
universal pattern, split 3:1.

Origin: this is the open, untested item from 2026-07-07 ('lost CD-tower
operators (ordering, commutativity, associativity, alternativity) may be
recoverable, encoded geometrically, depending on which direction a
zero-divisor locus is approached from') -- picked back up and actually
computed here.

THE SETUP

cd_mul is exactly bilinear, so for a known zero-divisor pair (a, b) with
a*b = 0, the behaviour along any approach path a(t) = a + t*v,
b(t) = b + t*w is exact, no limit required:

    a(t) * b(t) = a*b + t*(a*w + v*b) + t^2*(v*w)
                = t * D(v, w) + O(t^2)      [since a*b = 0]

D(v, w) = a*w + v*b is the exact first-order (directional-derivative) term.
D depends on the direction (v, w) -- the question is HOW.

FIRST PASS (2026-07-10, morning) -- 5 hand-picked pairs only:

    All 5 gave the SAME split: 4/256 flat, 244/256 at |D|=sqrt(2) (using
    normalised (e_i+e_j)/sqrt(2) vectors), 8/256 at |D|=2.0. This was
    reported as a universal, established result. It was not -- see below.

CORRECTED, FULL RESULT (2026-07-10, later same day) -- ALL 336 known
composite zero-divisor pairs, via CayleyDickson.find_composite_zero_divisors()
(TuringStack/udeo_poc.py), unnormalised (a[i]=1, a[j]=+-1, norm=sqrt(2)):

    NOT one universal pattern. Exactly TWO sub-classes, split 3:1:
        252/336 pairs (75%): 6/256 flat directions, nonzero |D| in
            {2.0: 244 directions, 2.828 (2*sqrt2): 6 directions}
        84/336 pairs (25%):  4/256 flat directions, nonzero |D| in
            {2.0: 244 directions, 2.828 (2*sqrt2): 8 directions}

    (The magnitude values 2.0/2.828 here vs sqrt(2)/2.0 in the first pass
    are the same finding at a different normalisation -- find_composite_
    zero_divisors() returns norm-sqrt(2) vectors, not unit vectors; every
    value scales by sqrt(2). The real correction is the flat-count split:
    4 vs 6, not always 4.)

    All 5 of the original hand-picked pairs happened to land in the 84/336
    (25%) minority class -- a small-sample bias caught only by testing the
    complete population, the same lesson Method 6 in ValaQuenta's
    udeo_crypto engine produced independently the same day.

WHAT THIS MEANS (stated at the confidence level the numbers support)

Confirmed, ESTABLISHED: a sedenion zero-divisor is not a uniform sink, and
the local approach-direction structure is not one universal shape either --
it is exactly TWO discrete shapes (244 directions at the common magnitude in
both; 4 or 6 flat; 8 or 6 at the larger magnitude, in a fixed 3:1 population
ratio). This is real, exact bilinear algebra verified to floating-point
precision on the complete known population, not a statistical tendency and
not (this time) an unverified generalisation from a handful of examples.

OPEN, NOT YET ANSWERED: what distinguishes the 75% class from the 25% class
structurally (which pairs land in which, and why the 3:1 ratio), and
whether either flat-direction set is where 'the lost CD-tower operators' (the
missing ordering/commutativity/associativity/alternativity structure) are
recoverable, as speculated on 2026-07-07. This file establishes the
structure exists and is exact; it does not yet connect the flat directions
to any specific recovered operator. That is the next step, not this one.

Author:  Claude, at Cody's direction -- 2026-07-10
Version: 0.200 -- corrected: full 336-pair population, not 5 hand-picked pairs
"""

import math
from typing import Dict, List, Any, Tuple

import numpy as np


def cd_conj(x: np.ndarray) -> np.ndarray:
    c = x.copy()
    c[1:] = -c[1:]
    return c

def cd_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = len(a)
    if n == 1:
        return np.array([a[0] * b[0]])
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = cd_mul(a1, b1) - cd_mul(cd_conj(b2), a2)
    c2 = cd_mul(b2, a1) + cd_mul(a2, cd_conj(b1))
    return np.concatenate([c1, c2])

def e_k(k: int, dim: int = 16) -> np.ndarray:
    v = np.zeros(dim)
    v[k] = 1.0
    return v

def _pair(i: int, j: int) -> np.ndarray:
    return (e_k(i) + e_k(j)) / math.sqrt(2)

# The 5 known zero-divisor pairs (from modules/singularity_null/maths.py,
# also verified in udeo_poc.py). All satisfy a*b = 0 exactly.
KNOWN_ZD_PAIRS = [
    ('(e1+e10)/sqrt2', '(e5+e14)/sqrt2', _pair(1, 10), _pair(5, 14)),
    ('(e1+e10)/sqrt2', '(e7+e12)/sqrt2', _pair(1, 10), _pair(7, 12)),
    ('(e1+e11)/sqrt2', '(e4+e14)/sqrt2', _pair(1, 11), _pair(4, 14)),
    ('(e1+e14)/sqrt2', '(e2+e13)/sqrt2', _pair(1, 14), _pair(2, 13)),
    ('(e1+e12)/sqrt2', '(e2+e15)/sqrt2', _pair(1, 12), _pair(2, 15)),
]


def directional_derivative_matrix(a: np.ndarray, b: np.ndarray, dim: int = 16) -> np.ndarray:
    """
    D[i,j] = |D(e_i, e_j)| = |a . e_j + e_i . b|, the exact magnitude of
    the first-order term of (a+t*e_i)*(b+t*e_j) as t -> 0, for every pair
    of basis approach directions.
    """
    D = np.zeros((dim, dim))
    for i in range(dim):
        v = e_k(i, dim)
        for j in range(dim):
            w = e_k(j, dim)
            term = cd_mul(a, w) + cd_mul(v, b)
            D[i, j] = float(np.linalg.norm(term))
    return D


def analyze_zd_pair(label_a: str, label_b: str, a: np.ndarray, b: np.ndarray) -> Dict[str, Any]:
    prod_norm = float(np.linalg.norm(cd_mul(a, b)))
    assert prod_norm < 1e-10, f"{label_a} x {label_b} is not a zero-divisor pair (|a.b|={prod_norm})"

    D = directional_derivative_matrix(a, b)
    flat = np.argwhere(D < 1e-10)
    nonzero_vals = D[D >= 1e-10]
    unique_vals, counts = np.unique(np.round(nonzero_vals, 4), return_counts=True)

    return {
        'a': label_a, 'b': label_b,
        'product_norm': prod_norm,
        'n_flat_directions': int(len(flat)),
        'flat_direction_indices': flat.tolist(),
        'nonzero_magnitude_distribution': dict(zip(unique_vals.tolist(), counts.tolist())),
        'D_matrix': D,
    }


def run_all() -> List[Dict[str, Any]]:
    """Run the exact directional-derivative analysis on all 5 known ZD pairs."""
    results = []
    print("=" * 78)
    print("  ZERO-DIVISOR APPROACH DIRECTIONS — exact directional-derivative structure")
    print("=" * 78)
    for label_a, label_b, a, b in KNOWN_ZD_PAIRS:
        r = analyze_zd_pair(label_a, label_b, a, b)
        results.append(r)
        print()
        print(f"  {label_a} x {label_b}   (|a.b| = {r['product_norm']:.2e})")
        print(f"    flat directions (D=0, degenerate approach): {r['n_flat_directions']}/256"
              f"  at {r['flat_direction_indices']}")
        print(f"    nonzero |D| distribution: {r['nonzero_magnitude_distribution']}")

    all_splits = [(r['n_flat_directions'], r['nonzero_magnitude_distribution']) for r in results]
    consistent = all(s == all_splits[0] for s in all_splits)
    print()
    print(f"  Split consistent across these 5 hand-picked pairs: {consistent}")
    print("  WARNING: these 5 pairs are not representative of the full population --")
    print("  see run_full_population() for the corrected, complete result.")
    print("=" * 78)
    return results


def run_full_population(max_pairs: int = None) -> Dict[str, Any]:
    """
    Run the exact directional-derivative analysis on the COMPLETE known
    population of composite zero-divisor pairs (336, via
    CayleyDickson.find_composite_zero_divisors() in TuringStack/udeo_poc.py),
    not just the 5 hand-picked ones run_all() uses. This is what corrected
    the original 'universal 4/244/8' claim into the real 3:1 two-class split.

    Requires TuringStack/udeo_poc.py to be importable (sys.path adjusted
    below to find it relative to a standard ThePlace checkout).
    """
    import sys
    import os
    turingstack_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'TuringStack')
    sys.path.insert(0, turingstack_path)
    from udeo_poc import CayleyDickson

    s16 = CayleyDickson(16, 'real')
    pairs = s16.find_composite_zero_divisors()

    patterns: Dict[Tuple[int, Tuple], int] = {}
    for a_list, b_list in pairs:
        a = np.array(a_list)
        b = np.array(b_list)
        assert float(np.linalg.norm(cd_mul(a, b))) < 1e-9
        D = directional_derivative_matrix(a, b)
        n_flat = int(np.sum(D < 1e-10))
        nonzero = D[D >= 1e-10]
        vals, counts = np.unique(np.round(nonzero, 4), return_counts=True)
        key = (n_flat, tuple(zip(vals.tolist(), counts.tolist())))
        patterns[key] = patterns.get(key, 0) + 1

    print("=" * 78)
    print(f"  FULL POPULATION: {len(pairs)} known composite zero-divisor pairs")
    print("=" * 78)
    for key, count in sorted(patterns.items(), key=lambda x: -x[1]):
        n_flat, dist = key
        pct = 100.0 * count / len(pairs)
        print(f"  {count}/{len(pairs)} pairs ({pct:.1f}%): {n_flat} flat directions, "
              f"nonzero |D| distribution = {dict(dist)}")
    print()
    print(f"  Distinct patterns: {len(patterns)} (NOT 1 -- the 5-pair sample in run_all() "
          f"missed this)")
    print("=" * 78)
    return {'n_pairs': len(pairs), 'patterns': patterns}


if __name__ == "__main__":
    run_all()
    print()
    run_full_population()
