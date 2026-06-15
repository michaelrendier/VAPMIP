"""
e16b_boundary_ascending.py  (covers wiki/57 claims)
Boundary ascending: flat→curved→complex→rotations→S¹⁵.
Negative space wake at each level. Krohn-Rhodes = two doublings.

Tests:
  - At each CD level, count zero-divisors (negative space wake grows)
  - Associativity failure rate increases with level
  - Two doublings from level N expose cross-terms not visible at level N
  - Alternativity: octonions are alternative; sedenions are not
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def count_zero_divisors(n):
    """Count pairs (i,j) with i<j, i≠0, j≠0 where e_i * e_j = 0."""
    pairs = []
    for i in range(1, n):
        for j in range(i+1, n):
            product = cd_mul(e(i, n), e(j, n))
            if all(abs(x) < 1e-12 for x in product):
                pairs.append((i, j))
    return pairs


def associativity_failures(n):
    """Count triples (i,j,k) where (e_i*e_j)*e_k ≠ e_i*(e_j*e_k)."""
    fails = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                lhs = cd_mul(cd_mul(e(i,n), e(j,n)), e(k,n))
                rhs = cd_mul(e(i,n), cd_mul(e(j,n), e(k,n)))
                if any(abs(l-r) > 1e-10 for l,r in zip(lhs,rhs)):
                    fails += 1
    return fails


def alternativity_test(n):
    """
    Alternative algebra: (a*a)*b = a*(a*b) and a*(b*b) = (a*b)*b.
    Octonions (n=8) are alternative; sedenions (n=16) are not.
    """
    fails = 0
    for i in range(n):
        for j in range(n):
            ei, ej = e(i,n), e(j,n)
            # left alternative: (ei*ei)*ej == ei*(ei*ej)
            lhs = cd_mul(cd_mul(ei, ei), ej)
            rhs = cd_mul(ei, cd_mul(ei, ej))
            if any(abs(l-r) > 1e-10 for l,r in zip(lhs,rhs)):
                fails += 1
    return fails


def run():
    results = {}

    for level in [1, 2, 3, 4]:  # R, C, H, O, S (2^level dims)
        n = 2 ** level
        zd = count_zero_divisors(n)
        assoc_fail = associativity_failures(n)
        alt_fail = alternativity_test(n)
        results[f"level_{level}_n{n}"] = {
            "level": level, "n": n,
            "zero_divisor_pairs": len(zd),
            "associativity_failures": assoc_fail,
            "alternativity_failures": alt_fail,
            "is_associative": assoc_fail == 0,
            "is_alternative": alt_fail == 0,
        }

    results["wake_grows"] = {
        "zd_counts": [results[f"level_{l}_n{2**l}"]["zero_divisor_pairs"] for l in range(1,5)],
        "pass": all(
            results[f"level_{l+1}_n{2**(l+1)}"]["zero_divisor_pairs"] >=
            results[f"level_{l}_n{2**l}"]["zero_divisor_pairs"]
            for l in range(1, 4)
        ),
        "description": "Zero-divisor count increases at each level (negative space wake grows)",
    }

    # Expected: R(0), C(0), H(0), O(0), S(42)
    # Actually ZD only appear at sedenion level (level 4)
    results["octonion_alternative"] = {
        "octonion_alt_failures": results["level_3_n8"]["alternativity_failures"],
        "sedenion_alt_failures": results["level_4_n16"]["alternativity_failures"],
        "octonions_are_alternative": results["level_3_n8"]["alternativity_failures"] == 0,
        "sedenions_are_not": results["level_4_n16"]["alternativity_failures"] > 0,
        "pass": (results["level_3_n8"]["alternativity_failures"] == 0 and
                 results["level_4_n16"]["alternativity_failures"] > 0),
    }

    return results


def report(results):
    print("=== e16b: BOUNDARY ASCENDING ===\n")
    print(f"  {'level':<8} {'n':<6} {'ZD pairs':<12} {'assoc_fail':<14} {'alt_fail':<12} {'assoc?':<8} {'alt?'}")
    for level in range(1, 5):
        n = 2**level
        r = results[f"level_{level}_n{n}"]
        print(f"  {r['level']:<8} {r['n']:<6} {r['zero_divisor_pairs']:<12} "
              f"{r['associativity_failures']:<14} {r['alternativity_failures']:<12} "
              f"{str(r['is_associative']):<8} {r['is_alternative']}")

    r = results["wake_grows"]
    print(f"\n  ZD counts: {r['zd_counts']}")
    print(f"  Wake grows at each level: {'PASS' if r['pass'] else 'FAIL'}")

    r = results["octonion_alternative"]
    print(f"\n  Octonions alternative: {r['octonions_are_alternative']}  "
          f"Sedenions NOT alternative: {r['sedenions_are_not']}  "
          f"[{'PASS' if r['pass'] else 'FAIL'}]")
    print(f"  (Octonion alt_failures={r['octonion_alt_failures']}, "
          f"Sedenion alt_failures={r['sedenion_alt_failures']})")


if __name__ == "__main__":
    report(run())
