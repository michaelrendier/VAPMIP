"""
e09_j2_involution.py
J₂ involution: swaps R↔B sub-algebras of the sedenion.

Tests:
  - J₂² = identity on all 16 basis elements
  - J₂ is an automorphism: J₂(a*b) = J₂(a)*J₂(b)?
  - Sedenion multiplication table: verify known zero-divisor pairs
  - R+B = full sedenion; R-B = the involution axis
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


# Known Cawagas zero-divisor pairs (ea, eb) where ea*eb = 0
# Partial list — 42 pairs total on S^15
KNOWN_ZD_PAIRS = [
    (1, 10), (2, 11), (3, 8), (4, 13), (5, 12), (6, 15), (7, 14),
    (1, 14), (2, 13), (3, 12), (4, 11), (5, 10), (6, 9),  (7, 8),
]


def run():
    results = {}

    # ── J₂² = identity ───────────────────────────────────────────────────────
    results["j2_involution"] = {
        "pass": j2_is_involution(16),
        "description": "J₂(J₂(v)) == v for all basis elements"
    }

    # ── J₂ as automorphism: J₂(a*b) = J₂(a)*J₂(b) ──────────────────────────
    failures = []
    for i in range(16):
        for j in range(16):
            ei, ej = e(i), e(j)
            lhs = j2_swap(cd_mul(ei, ej))
            rhs = cd_mul(j2_swap(ei), j2_swap(ej))
            if lhs != rhs:
                failures.append((i, j))
    results["j2_automorphism"] = {
        "pass": len(failures) == 0,
        "failures": failures[:10],
        "n_failures": len(failures),
        "description": "J₂(a*b) == J₂(a)*J₂(b) for all basis pairs"
    }

    # ── Zero-divisor verification ─────────────────────────────────────────────
    zd_results = []
    for a, b in KNOWN_ZD_PAIRS:
        ea, eb = e(a), e(b)
        product = cd_mul(ea, eb)
        is_zero = all(abs(x) < 1e-12 for x in product)
        zd_results.append({
            "pair": (a, b),
            "product_is_zero": is_zero,
            "product": product,
        })

    results["zero_divisors"] = {
        "pairs_tested": len(KNOWN_ZD_PAIRS),
        "pairs_confirmed": sum(1 for r in zd_results if r["product_is_zero"]),
        "failures": [r for r in zd_results if not r["product_is_zero"]],
        "pass": all(r["product_is_zero"] for r in zd_results),
    }

    # ── Find ALL zero-divisor pairs ───────────────────────────────────────────
    all_zd = []
    for i in range(1, 16):
        for j in range(i+1, 16):
            product = cd_mul(e(i), e(j))
            if all(abs(x) < 1e-12 for x in product):
                all_zd.append((i, j))
    results["all_zero_divisors"] = {
        "count": len(all_zd),
        "expected_cawagas": 42,
        "pass": len(all_zd) == 42,
        "pairs": all_zd,
    }

    # ── J₂ and zero-divisors: does J₂ map ZD pairs to ZD pairs? ──────────────
    zd_preserved = []
    for a, b in all_zd:
        ja = j2_swap(e(a))
        jb = j2_swap(e(b))
        product = cd_mul(ja, jb)
        is_zero = all(abs(x) < 1e-12 for x in product)
        zd_preserved.append(is_zero)
    results["j2_preserves_zd"] = {
        "pass": all(zd_preserved),
        "count_preserved": sum(zd_preserved),
        "total": len(all_zd),
    }

    # ── Sedenion associativity failure ────────────────────────────────────────
    # Find (ei*(ej*ek)) ≠ ((ei*ej)*ek)
    assoc_failures = 0
    for i in range(16):
        for j in range(16):
            for k in range(16):
                lhs = cd_mul(e(i), cd_mul(e(j), e(k)))
                rhs = cd_mul(cd_mul(e(i), e(j)), e(k))
                if any(abs(l-r) > 1e-12 for l, r in zip(lhs, rhs)):
                    assoc_failures += 1
    results["non_associativity"] = {
        "associativity_failures": assoc_failures,
        "total_triples": 16**3,
        "pass": assoc_failures > 0,  # we EXPECT failures — pass = non-assoc confirmed
        "description": "sedenion IS non-associative (failures > 0 = expected)"
    }

    return results


def report(results):
    print("=== e09: J₂ INVOLUTION ===\n")

    r = results["j2_involution"]
    print(f"  J₂² = identity:          {'PASS' if r['pass'] else 'FAIL'}")

    r = results["j2_automorphism"]
    print(f"  J₂ automorphism:         {'PASS' if r['pass'] else 'FAIL'}  ({r['n_failures']} failures)")
    if r["failures"]:
        print(f"    first failure pairs: {r['failures'][:5]}")

    r = results["zero_divisors"]
    print(f"  Known ZD pairs verified: {'PASS' if r['pass'] else 'FAIL'}  "
          f"({r['pairs_confirmed']}/{r['pairs_tested']})")

    r = results["all_zero_divisors"]
    print(f"  Total ZD pairs found:    {'PASS' if r['pass'] else 'FAIL'}  "
          f"found={r['count']}  expected={r['expected_cawagas']}")

    r = results["j2_preserves_zd"]
    print(f"  J₂ maps ZD→ZD:           {'PASS' if r['pass'] else 'FAIL'}  "
          f"({r['count_preserved']}/{r['total']})")

    r = results["non_associativity"]
    print(f"  Non-associativity:       {'CONFIRMED' if r['pass'] else 'UNEXPECTED'}  "
          f"({r['associativity_failures']}/{r['total_triples']} triples fail assoc)")


if __name__ == "__main__":
    report(run())
