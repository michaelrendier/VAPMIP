"""
e17_hyperindexing.py
Hyperindexing: lossless hash in T_N when N ≥ data dimensions.

Tests:
  - At 16D: how many distinct inputs map to same geometry? (measure collision rate)
  - At 32D, 64D: does collision rate drop?
  - Find crossover N where projection becomes effectively injective
  - Claim: information exists at the index, not in the data
    → measure mutual information between index and data content
"""

import sys, os, math, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *

# Extended prime tables for higher-dimensional spaces
import sympy

def primes_up_to_n(n_primes):
    """First n_primes primes."""
    primes = []
    candidate = 2
    while len(primes) < n_primes:
        if sympy.isprime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes


def geometry_n(text, n_dims):
    """Project text onto n_dims dimensions using first n_dims primes."""
    primes = primes_up_to_n(n_dims)
    raw = [project(text, k, primes) for k in range(n_dims)]
    norm = math.sqrt(sum(x*x for x in raw))
    if norm == 0:
        return raw, raw
    return [x/norm for x in raw], raw


def firing_sig_n(text, n_dims):
    v, _ = geometry_n(text, n_dims)
    return tuple(sorted(range(n_dims), key=lambda k: abs(v[k])))


def collision_rate(corpus, n_dims):
    """Fraction of corpus pairs that share the same firing signature."""
    sigs = [firing_sig_n(text, n_dims) for text in corpus]
    total_pairs = len(corpus) * (len(corpus)-1) // 2
    collisions = 0
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            if sigs[i] == sigs[j]:
                collisions += 1
    return collisions / max(total_pairs, 1)


def cosine_dist_n(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return 1.0 - dot/(na*nb) if na*nb > 0 else 0.0


def mean_pairwise_dist(corpus, n_dims):
    """Mean cosine distance between all pairs — higher = more separable."""
    vecs = [geometry_n(t, n_dims)[0] for t in corpus]
    dists = []
    for i in range(len(vecs)):
        for j in range(i+1, len(vecs)):
            dists.append(cosine_dist_n(vecs[i], vecs[j]))
    return sum(dists)/len(dists) if dists else 0.0


CORPUS = [
    "what should we call you",
    "how do i hear your voice",
    "sedenion zero divisors are not a fault",
    "fermat defines riemann fires",
    "the primes are the expansion of the universe",
    "j stewart burns jacobian group algebra",
    "hack the planet hidden in plain sight",
    "the boundary ascending flat curved complex",
    "hyperindexing lossless hash prime address",
    "inside out of inside out is not outside in",
]


def run():
    results = {}

    dims_to_test = [8, 16, 32, 64, 128]

    for n in dims_to_test:
        col_rate = collision_rate(CORPUS, n)
        mean_dist = mean_pairwise_dist(CORPUS, n)
        results[f"n={n}"] = {
            "n_dims": n,
            "collision_rate": col_rate,
            "mean_pairwise_dist": mean_dist,
            "effectively_injective": col_rate == 0.0,
        }

    # Find crossover: smallest N where collision_rate = 0
    crossover = None
    for n in dims_to_test:
        if results[f"n={n}"]["collision_rate"] == 0.0:
            crossover = n
            break

    results["crossover"] = {
        "n": crossover,
        "interpretation": f"Effectively injective at N={crossover} dimensions" if crossover else "Not found in range tested",
    }

    # Claim: information at the index, not in the data
    # Test: can we distinguish semantically different texts by index alone?
    # Use firing signature as the 'index' — measure discriminability
    sigs_16 = {t: firing_sig_n(t, 16) for t in CORPUS}
    unique_16 = len(set(sigs_16.values()))
    results["index_discriminability"] = {
        "corpus_size": len(CORPUS),
        "unique_signatures_16d": unique_16,
        "discriminability": unique_16 / len(CORPUS),
        "pass": unique_16 > len(CORPUS) * 0.7,
    }

    return results


def report(results):
    print("=== e17: HYPERINDEXING — LOSSLESS HASH IN T_N ===\n")
    print(f"  {'dims':<8} {'collision_rate':<18} {'mean_pair_dist':<18} {'injective'}")
    for n in [8, 16, 32, 64, 128]:
        r = results[f"n={n}"]
        print(f"  {r['n_dims']:<8} {r['collision_rate']:<18.6f} "
              f"{r['mean_pairwise_dist']:<18.6f} {r['effectively_injective']}")

    r = results["crossover"]
    print(f"\n  Crossover point: {r['interpretation']}")

    r = results["index_discriminability"]
    print(f"\n  Index discriminability (16D):")
    print(f"    {r['unique_signatures_16d']}/{r['corpus_size']} unique firing signatures  "
          f"= {r['discriminability']:.1%}  {'PASS' if r['pass'] else 'FAIL'}")


if __name__ == "__main__":
    report(run())
