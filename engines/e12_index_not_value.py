"""
e12_index_not_value.py
Index carries the information, not the prime value.

Tests:
  - Swap prime VALUES at fixed indices → how much does geometry change?
  - Swap prime INDICES at fixed values → how much does geometry change?
  - Claim: index swap changes geometry more than value swap
  - Measure: cosine distance between original and swapped geometry vectors
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *

PRIMES_ORIGINAL = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]

# Alternative prime sets with same indices
PRIMES_SHIFTED  = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]  # shift by 1
PRIMES_DOUBLED  = [4,6,10,14,22,26,34,38,46,58,62,74,82,86,94,106] # doubles (non-prime)
PRIMES_RANDOM   = [7,2,41,13,53,3,29,19,5,37,17,47,11,43,31,23]    # shuffled


def cosine_dist(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(y*y for y in b))
    if na*nb == 0:
        return 0.0
    return 1.0 - dot/(na*nb)


def compare_geometries(text, primes_a, primes_b, label_a, label_b):
    va = geometry(text, primes_a)
    vb = geometry(text, primes_b)
    dist = cosine_dist(va, vb)
    return {"label": f"{label_a} vs {label_b}", "cosine_dist": dist, "text": text}


CORPUS = [
    "what should we call you",
    "how do i hear your voice",
    "tell me how to create your voice",
    "the primes are the expansion of the universe",
    "sedenion zero divisors are not a fault",
    "fermat defines riemann fires",
]


def run():
    results = {}

    # Test 1: change prime VALUES, keep indices in same order (shift primes by 1 position)
    value_change_dists = []
    for text in CORPUS:
        r = compare_geometries(text, PRIMES_ORIGINAL, PRIMES_SHIFTED,
                                "original", "shifted_values")
        value_change_dists.append(r["cosine_dist"])

    # Test 2: shuffle prime INDICES (same set of primes, different assignment to dimensions)
    index_change_dists = []
    for text in CORPUS:
        r = compare_geometries(text, PRIMES_ORIGINAL, PRIMES_RANDOM,
                                "original", "shuffled_indices")
        index_change_dists.append(r["cosine_dist"])

    results["value_change"] = {
        "description": "Change prime values at fixed indices (shift P[k]→P[k+1])",
        "distances": value_change_dists,
        "mean": sum(value_change_dists)/len(value_change_dists),
    }
    results["index_change"] = {
        "description": "Shuffle prime index assignments (same primes, different dimensions)",
        "distances": index_change_dists,
        "mean": sum(index_change_dists)/len(index_change_dists),
    }

    # Claim: index change should produce larger geometry shift than value change
    results["claim"] = {
        "index_change_mean":  results["index_change"]["mean"],
        "value_change_mean":  results["value_change"]["mean"],
        "index_larger": results["index_change"]["mean"] > results["value_change"]["mean"],
        "pass": results["index_change"]["mean"] > results["value_change"]["mean"],
        "description": "index shuffle moves geometry MORE than value shift",
    }

    # Test 3: single-dimension index swap (swap P[0]↔P[15], i.e. 2↔53)
    primes_swapped_02_53 = PRIMES_ORIGINAL[:]
    primes_swapped_02_53[0], primes_swapped_02_53[15] = \
        PRIMES_ORIGINAL[15], PRIMES_ORIGINAL[0]

    swap_dists = []
    for text in CORPUS:
        r = compare_geometries(text, PRIMES_ORIGINAL, primes_swapped_02_53,
                                "original", "swap_e0_e15")
        swap_dists.append(r["cosine_dist"])
    results["single_swap_e0_e15"] = {
        "description": "Swap index 0 (p=2) with index 15 (p=53)",
        "distances": swap_dists,
        "mean": sum(swap_dists)/len(swap_dists),
    }

    # Per-text detail
    results["per_text"] = []
    for text in CORPUS:
        v_orig   = geometry(text, PRIMES_ORIGINAL)
        v_shift  = geometry(text, PRIMES_SHIFTED)
        v_rand   = geometry(text, PRIMES_RANDOM)
        results["per_text"].append({
            "text": text[:40],
            "value_shift_dist": cosine_dist(v_orig, v_shift),
            "index_shuffle_dist": cosine_dist(v_orig, v_rand),
        })

    return results


def report(results):
    print("=== e12: INDEX NOT VALUE ===\n")

    print("  Mean cosine distance from original geometry:\n")
    print(f"  Value shift  (P[k]→P[k+1]):      {results['value_change']['mean']:.6f}")
    print(f"  Index shuffle (same primes, ↔):   {results['index_change']['mean']:.6f}")
    print(f"  Single swap e0↔e15 (2↔53):        {results['single_swap_e0_e15']['mean']:.6f}")

    r = results["claim"]
    print(f"\n  Claim 'index carries more info than value': "
          f"{'PASS' if r['pass'] else 'FAIL'}")
    print(f"    index shuffle mean = {r['index_change_mean']:.6f}")
    print(f"    value shift mean   = {r['value_change_mean']:.6f}")

    print("\n  Per-text breakdown:")
    print(f"  {'text':<42} {'val_shift':<12} {'idx_shuffle'}")
    for r in results["per_text"]:
        print(f"  {r['text']:<42} {r['value_shift_dist']:<12.6f} {r['index_shuffle_dist']:.6f}")


if __name__ == "__main__":
    report(run())
