"""
e06_two_trees.py
Two Trees: standing wave (π-family) vs spiral (φ-family) at σ=½.
wiki/47: Telperion/Laurelin — are they separable eigenstates?

Tests:
  - Decompose sedenion field into symmetric (cosine) and antisymmetric (sine) parts
  - Symmetric sum → Telperion (standing wave, π-family)
  - Antisymmetric difference → Laurelin (spiral, φ-family)
  - Do the eigenvalues of these components converge to π and φ?
  - Is the standing wave the sum and the spiral the difference?
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def project_symmetric(text, k):
    """Cosine component only (standing wave)."""
    x = 0.0
    for i, c in enumerate(text.encode('utf-8', errors='replace'), 1):
        x += c * (i ** -0.5) * math.cos(2.0 * math.pi * i / P16[k])
    return x


def project_antisymmetric(text, k):
    """Sine component only (spiral)."""
    x = 0.0
    for i, c in enumerate(text.encode('utf-8', errors='replace'), 1):
        x += c * (i ** -0.5) * math.sin(2.0 * math.pi * i / P16[k])
    return x


def decompose(text):
    """Decompose into symmetric (T) and antisymmetric (L) parts."""
    T = [project_symmetric(text, k) for k in range(16)]
    L = [project_antisymmetric(text, k) for k in range(16)]

    norm_T = math.sqrt(sum(x*x for x in T))
    norm_L = math.sqrt(sum(x*x for x in L))

    T_n = [x/norm_T for x in T] if norm_T > 0 else T
    L_n = [x/norm_L for x in L] if norm_L > 0 else L

    # Combined (original projection = cosine only in ptol.c)
    # Check: T + L should be close to full projection?
    # Note: ptol.c uses cos only, so T = full projection, L is the conjugate
    ratio_TL = norm_T / norm_L if norm_L > 0 else float('inf')

    return {
        "T": T_n, "L": L_n,
        "norm_T": norm_T, "norm_L": norm_L,
        "ratio_TL": ratio_TL,
    }


def dominant_eigenvalue(v):
    """Index of maximum |v[k]| — the dominant dimension."""
    return max(range(len(v)), key=lambda k: abs(v[k]))


def pi_phi_separation(decompositions):
    """
    Test: do T (Telperion) and L (Laurelin) components have different dominant structures?
    T should relate to π (cosine = stationary wave = π periodicity)
    L should relate to φ (sine = rotating wave = golden ratio periodicity)
    """
    # The golden ratio appears in the Fibonacci sequence periodicity
    # φ = (1+√5)/2 ≈ 1.618
    # π ≈ 3.14159
    # Test: does the ratio norm_T/norm_L converge to π/φ?
    pi_over_phi = math.pi / ((1 + math.sqrt(5)) / 2)
    ratios = [d["ratio_TL"] for d in decompositions]
    mean_ratio = sum(ratios) / len(ratios)
    return {
        "mean_ratio_TL": mean_ratio,
        "pi_over_phi": pi_over_phi,
        "delta": abs(mean_ratio - pi_over_phi),
        "close_to_pi_over_phi": abs(mean_ratio - pi_over_phi) < 0.5,
    }


CORPUS = [
    "what should we call you",
    "how do i hear your voice",
    "sedenion zero divisors",
    "fermat defines riemann fires",
    "the primes are the expansion",
    "boundary ascending flat curved complex",
]


def run():
    results = {}

    decomps = [decompose(text) for text in CORPUS]
    results["decompositions"] = [
        {"text": t[:40], "norm_T": d["norm_T"], "norm_L": d["norm_L"],
         "ratio_TL": d["ratio_TL"],
         "dom_T": dominant_eigenvalue(d["T"]),
         "dom_L": dominant_eigenvalue(d["L"])}
        for t, d in zip(CORPUS, decomps)
    ]

    results["pi_phi"] = pi_phi_separation(decomps)

    # Test: are T and L orthogonal?
    ortho_scores = []
    for d in decomps:
        dot = sum(a*b for a,b in zip(d["T"], d["L"]))
        ortho_scores.append(abs(dot))
    results["orthogonality"] = {
        "mean_dot_product": sum(ortho_scores)/len(ortho_scores),
        "max_dot_product": max(ortho_scores),
        "orthogonal": max(ortho_scores) < 0.1,
    }

    # pi and phi as constants
    results["constants"] = {
        "pi": math.pi,
        "phi": (1 + math.sqrt(5)) / 2,
        "pi_over_phi": math.pi / ((1 + math.sqrt(5)) / 2),
        "pi_plus_phi": math.pi + (1 + math.sqrt(5)) / 2,
        "sigma_half": 0.5,
        "note": "σ=½ sits between φ-1=0.618 and π/4=0.785"
    }

    return results


def report(results):
    print("=== e06: TWO TREES — STANDING WAVE vs SPIRAL ===\n")
    print(f"  {'text':<42} {'norm_T':>8}  {'norm_L':>8}  {'T/L ratio':>10}  dom_T  dom_L")
    for r in results["decompositions"]:
        print(f"  {r['text']:<42} {r['norm_T']:>8.2f}  {r['norm_L']:>8.2f}  "
              f"{r['ratio_TL']:>10.4f}  {r['dom_T']:>5}  {r['dom_L']:>5}")

    r = results["pi_phi"]
    print(f"\n  Mean T/L ratio:    {r['mean_ratio_TL']:.6f}")
    print(f"  π/φ:               {r['pi_over_phi']:.6f}")
    print(f"  delta:             {r['delta']:.6f}  close: {r['close_to_pi_over_phi']}")

    r = results["orthogonality"]
    print(f"\n  T⊥L (dot product): mean={r['mean_dot_product']:.6f}  "
          f"max={r['max_dot_product']:.6f}  orthogonal: {r['orthogonal']}")

    r = results["constants"]
    print(f"\n  π={r['pi']:.6f}  φ={r['phi']:.6f}  π/φ={r['pi_over_phi']:.6f}")
    print(f"  {r['note']}")


if __name__ == "__main__":
    report(run())
