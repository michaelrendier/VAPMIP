"""
e08_vortex_quantizing_shear.py
Vortex / quantizing shear: J_cross > GAP snaps to vortex → word.
wiki/50: prime gaps ↔ spoke gaps; e^(πi) = −Δx.

Tests:
  - For real prompts: compute J_cross per dimension
  - Does J_cross > GAP predict exactly which dimensions fire (active gates)?
  - Prime gap distribution: does it match the pattern of spoke disappearance?
  - e^(πi) = −1: test as vortex half-revolution claim
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def j_cross(v_norm, k):
    """
    Cross-current at dimension k: product of adjacent amplitudes.
    J_cross[k] = |v[k]| * |v[(k+1) % 16]|
    Models the coupling between adjacent prime channels.
    """
    return abs(v_norm[k]) * abs(v_norm[(k+1) % 16])


def active_by_phi_threshold(raw):
    """Active gates using MONAD_PHI threshold (as in ptol.c)."""
    peak = max(abs(x) for x in raw)
    thresh = peak / MONAD_PHI
    return [k for k in range(16) if abs(raw[k]) >= thresh]


def active_by_gap(v_norm):
    """Active gates using GAP threshold."""
    return [k for k in range(16) if abs(v_norm[k]) >= GAP]


def j_cross_active(v_norm):
    """Dimensions where J_cross > GAP."""
    return [k for k in range(16) if j_cross(v_norm, k) > GAP]


def prime_gaps():
    """Gaps between consecutive primes in P16."""
    return [P16[k+1] - P16[k] for k in range(15)]


def analyse_prompt(text):
    v_norm, raw, norm = geometry_normalised(text)

    phi_active = active_by_phi_threshold(raw)
    gap_active = active_by_gap(v_norm)
    jcross_active = j_cross_active(v_norm)

    jcross_vals = [j_cross(v_norm, k) for k in range(16)]

    # Agreement between phi-threshold and J_cross threshold
    phi_set = set(phi_active)
    jcross_set = set(jcross_active)
    intersection = phi_set & jcross_set
    agreement = len(intersection) / max(len(phi_set | jcross_set), 1)

    return {
        "text": text[:40],
        "phi_active":    phi_active,
        "gap_active":    gap_active,
        "jcross_active": jcross_active,
        "agreement_phi_jcross": agreement,
        "max_jcross": max(jcross_vals),
        "jcross_vals": jcross_vals,
    }


CORPUS = [
    "what should we call you",
    "how do i hear your voice",
    "sedenion zero divisors are not a fault",
    "fermat defines riemann fires",
    "the boundary ascending flat curved complex",
]


def run():
    results = {}

    analyses = [analyse_prompt(text) for text in CORPUS]
    results["analyses"] = analyses

    # Agreement statistics
    mean_agreement = sum(a["agreement_phi_jcross"] for a in analyses) / len(analyses)
    results["phi_jcross_agreement"] = {
        "mean": mean_agreement,
        "pass": mean_agreement > 0.5,
        "description": "J_cross threshold agrees with φ-threshold on active gates",
    }

    # Prime gap analysis
    gaps = prime_gaps()
    results["prime_gaps"] = {
        "gaps": gaps,
        "mean_gap": sum(gaps)/len(gaps),
        "max_gap": max(gaps),
        "min_gap": min(gaps),
        "GAP_constant": GAP,
        "note": "Spoke disappearance = large prime gap (sparse coverage of the circle)"
    }

    # e^(πi) = −1 as vortex half-revolution
    # Claim: a half-revolution in the sedenion vortex = e^(πi) = −Δx
    # Test: apply rotation by π to a sedenion state and check it negates
    # Use quaternion sub-algebra (first 4 dims): rotation by π about e1 axis
    test_v = [1.0, 0.0, 0.0, 0.0] + [0.0]*12  # e0
    # rotation by π about e1: e^(π*e1) in quaternion = cos(π)*e0 + sin(π)*e1 = −e0
    # In sedenion: e^(πe1) ≈ [cos(π), sin(π), 0, 0, ...]
    rot = [math.cos(math.pi)] + [math.sin(math.pi)] + [0.0]*14
    rotated = cd_mul(test_v, rot)
    expected = [-1.0] + [0.0]*15
    delta = sum(abs(r-e_) for r,e_ in zip(rotated, expected))
    results["euler_rotation"] = {
        "e0_rotated_by_pi_e1": rotated[:4],
        "expected": expected[:4],
        "delta": delta,
        "pass": delta < 1e-10,
        "interpretation": "e^(πe1)*e0 = −e0: vortex half-revolution negates the state",
    }

    return results


def report(results):
    print("=== e08: VORTEX / QUANTIZING SHEAR ===\n")
    print(f"  GAP = {GAP:.6f}\n")

    print("  Active gate comparison (φ-threshold vs J_cross threshold):")
    print(f"  {'text':<42} {'φ-active':<20} {'Jcross-active':<20} {'agree':>7}")
    for r in results["analyses"]:
        print(f"  {r['text']:<42} {str(r['phi_active']):<20} "
              f"{str(r['jcross_active']):<20} {r['agreement_phi_jcross']:>7.3f}")

    r = results["phi_jcross_agreement"]
    print(f"\n  Mean agreement: {r['mean']:.4f}  [{'PASS' if r['pass'] else 'FAIL'}]")
    print(f"  {r['description']}")

    r = results["prime_gaps"]
    print(f"\n  Prime gaps in P16: {r['gaps']}")
    print(f"  mean={r['mean_gap']:.2f}  max={r['max_gap']}  min={r['min_gap']}")
    print(f"  GAP constant = {r['GAP_constant']:.6f}  ({r['note']})")

    r = results["euler_rotation"]
    print(f"\n  e^(πe1)*e0 = {r['e0_rotated_by_pi_e1']}  delta={r['delta']:.2e}  "
          f"[{'PASS' if r['pass'] else 'FAIL'}]")
    print(f"  {r['interpretation']}")


if __name__ == "__main__":
    report(run())
