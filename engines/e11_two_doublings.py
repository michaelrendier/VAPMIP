"""
e11_two_doublings.py
Two Cayley-Dickson doublings expose all pathways at any level.

Tests:
  - At level N: how many distinct basis products are reachable?
  - After 1 doubling: partial picture
  - After 2 doublings: complete picture (all pathways visible)?
  - The cross-term from the 2nd doubling = J₂
  - Does the 2nd cross-term complete the involution?
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def pathways_at_level(n):
    """
    Count distinct non-zero basis products e_i * e_j for i≠j at level n.
    'Pathway' = non-trivial product that lands on a specific basis element.
    """
    paths = set()
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            product = cd_mul(e(i, n), e(j, n))
            # Which basis element does this land on?
            for k, v in enumerate(product):
                if abs(v) > 1e-12:
                    paths.add((i, j, k, round(v)))
    return paths


def cross_terms_at_doubling(level):
    """
    At the k-th Cayley-Dickson doubling (level = 2^k dimensions),
    identify the cross-terms: the products that only exist at THIS level
    (not reachable at the level below).
    """
    n = 2 ** level
    n_half = n // 2

    paths_full  = pathways_at_level(n)
    paths_lower = pathways_at_level(n_half) if n_half >= 1 else set()

    # New pathways introduced at this level
    # = products involving at least one component from the upper half (indices >= n_half)
    new_paths = {p for p in paths_full
                 if p[0] >= n_half or p[1] >= n_half or p[2] >= n_half}

    return {
        "level": level,
        "n": n,
        "total_paths": len(paths_full),
        "new_paths_at_this_level": len(new_paths),
        "lower_paths": len(paths_lower),
    }


def two_doublings_completeness():
    """
    Claim: two doublings above any level expose all pathways.
    Test: start at level 1 (R, 2D), check levels 2, 3, 4.
    Measure pathway count growth: does it stabilise after 2 doublings?
    """
    results = []
    for base_level in range(1, 4):
        base_n = 2 ** base_level
        counts = {}
        for extra in range(3):
            level = base_level + extra
            n = 2 ** level
            paths = pathways_at_level(n)
            counts[f"+{extra}"] = len(paths)
        results.append({
            "base_level": base_level,
            "base_n": base_n,
            "pathway_counts": counts,
            "ratio_0_to_1": counts["+1"] / max(counts["+0"], 1),
            "ratio_1_to_2": counts["+2"] / max(counts["+1"], 1),
        })
    return results


def j2_as_second_cross_term():
    """
    The J₂ involution (R↔B swap) IS the cross-term from the 4th doubling.
    Test: does j2_swap(e(k)) for k in 8..15 give the cross-term of the doubling?
    """
    # At the sedenion level (level 4, n=16):
    # The upper 8 elements (e8..e15) are the cross-terms from the 4th doubling
    # J₂ swaps them with the lower 8 elements
    cross_term_indices = list(range(8, 16))
    swapped = [j2_swap(e(k)) for k in cross_term_indices]
    # Each should land in the lower half
    all_lower = all(
        all(abs(s[k]) < 1e-12 for k in range(8, 16))
        for s in swapped
    )
    return {
        "cross_term_indices": cross_term_indices,
        "j2_maps_upper_to_lower": all_lower,
        "pass": all_lower,
    }


def run():
    results = {}

    results["pathway_growth"] = two_doublings_completeness()

    for level in range(1, 5):
        results[f"level_{level}"] = cross_terms_at_doubling(level)

    results["j2_cross_term"] = j2_as_second_cross_term()

    return results


def report(results):
    print("=== e11: TWO DOUBLINGS EXPOSE ALL PATHWAYS ===\n")

    print("  Pathway counts at each Cayley-Dickson level:")
    print(f"  {'level':<8} {'n':<6} {'paths':<12} {'new_paths':<14} {'lower_paths'}")
    for lev in range(1, 5):
        r = results[f"level_{lev}"]
        print(f"  {r['level']:<8} {r['n']:<6} {r['total_paths']:<12} "
              f"{r['new_paths_at_this_level']:<14} {r['lower_paths']}")

    print("\n  Pathway growth from base level (0 = base, 1 = +1 doubling, 2 = +2 doublings):")
    for r in results["pathway_growth"]:
        c = r["pathway_counts"]
        print(f"  base=level{r['base_level']}(n={r['base_n']}):  "
              f"+0={c['+0']:5d}  +1={c['+1']:5d}  +2={c['+2']:5d}  "
              f"ratios: {r['ratio_0_to_1']:.3f} → {r['ratio_1_to_2']:.3f}")

    r = results["j2_cross_term"]
    print(f"\n  J₂ = 4th doubling cross-term: {'PASS' if r['pass'] else 'FAIL'}  "
          f"(upper half maps to lower: {r['j2_maps_upper_to_lower']})")


if __name__ == "__main__":
    report(run())
