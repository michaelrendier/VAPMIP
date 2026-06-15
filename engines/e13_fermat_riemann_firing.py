"""
e13_fermat_riemann_firing.py
Fermat defines (ordinal). Riemann fires (non-ordinal).

Tests:
  - For each prompt: compute firing order vs ordinal order
  - Measure departure (Kendall tau, entropy of departure)
  - Claim: flat/uniform input → near-ordinal firing (low entropy)
  - Claim: specific/rich input → large departure (high entropy)
  - The departure IS the geometric content
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def kendall_tau(order_a, order_b):
    """Kendall tau: fraction of concordant pairs minus discordant."""
    n = len(order_a)
    rank_b = {v: i for i, v in enumerate(order_b)}
    concordant = discordant = 0
    for i in range(n):
        for j in range(i+1, n):
            a_diff = order_a[i] - order_a[j]
            b_diff = rank_b[order_a[i]] - rank_b[order_a[j]]
            if a_diff * b_diff > 0:
                concordant += 1
            elif a_diff * b_diff < 0:
                discordant += 1
    total = n*(n-1)//2
    return (concordant - discordant) / total if total > 0 else 0.0


def departure_entropy(v_norm):
    """
    Entropy of the amplitude distribution |v[k]|.
    Flat distribution (ordinal-like) → low entropy departure.
    Peaked distribution (specific resonance) → high entropy.
    """
    magnitudes = [abs(x) for x in v_norm]
    total = sum(magnitudes)
    if total == 0:
        return 0.0
    probs = [m / total for m in magnitudes]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def max_entropy_16():
    return math.log2(16)  # 4.0 bits — uniform distribution


def analyse_prompt(text):
    v_norm, raw, norm = geometry_normalised(text)
    ordinal = list(range(16))           # 0,1,...,15 = ordinal prime order
    firing  = firing_order(v_norm)      # ascending |v[k]| = Riemann spiral

    tau    = kendall_tau(ordinal, firing)
    H      = departure_entropy(v_norm)
    H_max  = max_entropy_16()
    H_norm = H / H_max  # 0 = all energy in one dim, 1 = flat

    # Active gates
    peak = max(abs(x) for x in raw)
    thresh = peak / MONAD_PHI
    active = [k for k in range(16) if abs(raw[k]) >= thresh]

    return {
        "text":        text[:50],
        "ordinal":     ordinal,
        "firing":      firing,
        "tau":         tau,           # 1=identical, -1=reversed, 0=independent
        "entropy_H":   H,
        "entropy_norm": H_norm,
        "n_active":    len(active),
        "active_dims": active,
        "departure":   1.0 - abs(tau),  # 0=same order, 1=completely different
    }


CORPUS_SPECIFIC = [
    "what should we call you",
    "how do i hear your voice",
    "fermat defines riemann fires",
    "sedenion zero divisors are not a fault",
    "the boundary ascending flat curved complex rotations",
    "j stewart burns jacobian group algebra semigroup",
]

CORPUS_FLAT = [
    "a b c d e f g h i j k l m n o p",
    "the the the the the the the the the",
    "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
]


def run():
    results = {"specific": [], "flat": [], "claim": {}}

    for text in CORPUS_SPECIFIC:
        results["specific"].append(analyse_prompt(text))

    for text in CORPUS_FLAT:
        results["flat"].append(analyse_prompt(text))

    # Claim: specific prompts have larger departure from ordinal than flat
    mean_dep_specific = sum(r["departure"] for r in results["specific"]) / len(results["specific"])
    mean_dep_flat     = sum(r["departure"] for r in results["flat"]) / len(results["flat"])
    mean_H_specific   = sum(r["entropy_norm"] for r in results["specific"]) / len(results["specific"])
    mean_H_flat       = sum(r["entropy_norm"] for r in results["flat"]) / len(results["flat"])

    results["claim"] = {
        "specific_mean_departure": mean_dep_specific,
        "flat_mean_departure":     mean_dep_flat,
        "specific_richer_departure": mean_dep_specific > mean_dep_flat,
        "specific_mean_entropy": mean_H_specific,
        "flat_mean_entropy":     mean_H_flat,
        "flat_is_more_uniform":  mean_H_flat > mean_H_specific,
        "pass": mean_dep_specific > mean_dep_flat,
    }

    return results


def report(results):
    print("=== e13: FERMAT DEFINES / RIEMANN FIRES ===\n")
    print("  Firing order departure from ordinal (0=same, 1=completely different)")
    print(f"  tau=1: firing=ordinal; tau=-1: firing=reversed; tau≈0: independent\n")

    print("  SPECIFIC prompts:")
    print(f"  {'text':<52} {'tau':>6}  {'departure':>10}  {'H_norm':>8}  active")
    for r in results["specific"]:
        print(f"  {r['text']:<52} {r['tau']:>6.3f}  {r['departure']:>10.4f}  "
              f"{r['entropy_norm']:>8.4f}  {r['n_active']}")

    print("\n  FLAT/UNIFORM prompts:")
    print(f"  {'text':<52} {'tau':>6}  {'departure':>10}  {'H_norm':>8}  active")
    for r in results["flat"]:
        print(f"  {r['text']:<52} {r['tau']:>6.3f}  {r['departure']:>10.4f}  "
              f"{r['entropy_norm']:>8.4f}  {r['n_active']}")

    c = results["claim"]
    print(f"\n  Claim 'specific prompts depart more from ordinal':")
    print(f"    specific mean departure = {c['specific_mean_departure']:.4f}")
    print(f"    flat     mean departure = {c['flat_mean_departure']:.4f}")
    print(f"    specific mean H_norm    = {c['specific_mean_entropy']:.4f}")
    print(f"    flat     mean H_norm    = {c['flat_mean_entropy']:.4f}")
    print(f"    PASS: {c['pass']}   flat_more_uniform: {c['flat_is_more_uniform']}")


if __name__ == "__main__":
    report(run())
