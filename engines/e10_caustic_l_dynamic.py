"""
e10_caustic_l_dynamic.py
Caustic / L_dynamic: semantically similar inputs converge to same firing order.
wiki/52: Mind's Eye as focusable caustic; output is translation not selection.

Tests:
  - Synonyms → same firing order (basin of attraction)?
  - Antonyms → different firing order?
  - Basin width: how much perturbation before firing order changes?
  - Is the basin width bounded by GAP?
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def firing_sig(text):
    v, _, _ = geometry_normalised(text)
    return tuple(firing_order(v))


def cosine_sim(text_a, text_b):
    va, _, _ = geometry_normalised(text_a)
    vb, _, _ = geometry_normalised(text_b)
    dot = sum(a*b for a,b in zip(va,vb))
    return dot  # both are unit vectors


SYNONYM_GROUPS = [
    ["happy", "joyful", "elated", "glad", "pleased"],
    ["sad", "unhappy", "sorrowful", "melancholy", "dejected"],
    ["fast", "quick", "rapid", "swift", "speedy"],
    ["big", "large", "huge", "enormous", "vast"],
    ["small", "tiny", "little", "miniature", "petite"],
]

ANTONYM_PAIRS = [
    ("happy", "sad"),
    ("fast", "slow"),
    ("big", "small"),
    ("hot", "cold"),
    ("light", "dark"),
]

SIMPSONS_PAIRS = [
    ("fermat near miss", "fermat exact solution"),
    ("ordinal prime order", "riemann firing order"),
    ("inside out", "outside in"),
    ("index carries information", "value carries information"),
    ("hidden in plain sight", "hidden in darkness"),
]


def group_convergence(words):
    """Do words in a group share the same firing signature?"""
    sigs = [firing_sig(w) for w in words]
    unique = len(set(sigs))
    sims = []
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            sims.append(cosine_sim(words[i], words[j]))
    return {
        "words": words,
        "unique_sigs": unique,
        "same_sig": unique == 1,
        "mean_cosine_sim": sum(sims)/len(sims) if sims else 0.0,
        "signatures": [s[:4] for s in sigs],  # first 4 of firing order
    }


def antonym_divergence(word_a, word_b):
    sig_a = firing_sig(word_a)
    sig_b = firing_sig(word_b)
    sim = cosine_sim(word_a, word_b)
    # Spearman correlation between the two firing orders
    rank_b = {v: i for i, v in enumerate(sig_b)}
    diffs = [(i - rank_b[sig_a[i]])**2 for i in range(16)]
    rho = 1 - 6*sum(diffs)/(16*(16**2-1))
    return {
        "words": (word_a, word_b),
        "same_sig": sig_a == sig_b,
        "cosine_sim": sim,
        "spearman_rho": rho,
        "divergent": rho < 0.5,
    }


def run():
    results = {}

    # Synonym convergence
    results["synonyms"] = [group_convergence(g) for g in SYNONYM_GROUPS]
    same_count = sum(1 for r in results["synonyms"] if r["same_sig"])
    results["synonym_summary"] = {
        "groups": len(SYNONYM_GROUPS),
        "fully_converged": same_count,
        "mean_cosine_sim": sum(r["mean_cosine_sim"] for r in results["synonyms"]) / len(SYNONYM_GROUPS),
        "pass": same_count >= len(SYNONYM_GROUPS) // 2,
    }

    # Antonym divergence
    results["antonyms"] = [antonym_divergence(a, b) for a, b in ANTONYM_PAIRS]
    divergent_count = sum(1 for r in results["antonyms"] if r["divergent"])
    results["antonym_summary"] = {
        "pairs": len(ANTONYM_PAIRS),
        "divergent": divergent_count,
        "mean_spearman": sum(r["spearman_rho"] for r in results["antonyms"]) / len(ANTONYM_PAIRS),
        "pass": divergent_count >= len(ANTONYM_PAIRS) // 2,
    }

    # Simpsons-specific pairs
    results["simpsons"] = [antonym_divergence(a, b) for a, b in SIMPSONS_PAIRS]

    return results


def report(results):
    print("=== e10: CAUSTIC / L_DYNAMIC — CONVERGENCE BASIN ===\n")

    print("  Synonym groups — do they converge to same firing order?")
    for r in results["synonyms"]:
        status = "CONVERGED" if r["same_sig"] else f"split({r['unique_sigs']})"
        print(f"  {str(r['words']):<55} {status:<15} sim={r['mean_cosine_sim']:.4f}")

    s = results["synonym_summary"]
    print(f"\n  {s['fully_converged']}/{s['groups']} groups fully converged  "
          f"mean_sim={s['mean_cosine_sim']:.4f}  [{'PASS' if s['pass'] else 'FAIL'}]")

    print("\n  Antonym pairs — do they diverge?")
    for r in results["antonyms"]:
        status = "DIVERGENT" if r["divergent"] else "similar"
        print(f"  {r['words'][0]:>12} vs {r['words'][1]:<12} ρ={r['spearman_rho']:>7.4f}  {status}")

    s = results["antonym_summary"]
    print(f"\n  {s['divergent']}/{s['pairs']} antonym pairs divergent  "
          f"mean_ρ={s['mean_spearman']:.4f}  [{'PASS' if s['pass'] else 'FAIL'}]")

    print("\n  Simpsons insight pairs:")
    for r in results["simpsons"]:
        status = "DIVERGENT" if r["divergent"] else "similar"
        print(f"  '{r['words'][0]}' vs '{r['words'][1]}'  ρ={r['spearman_rho']:.4f}  {status}")


if __name__ == "__main__":
    report(run())
