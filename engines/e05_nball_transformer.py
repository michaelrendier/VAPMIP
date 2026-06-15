"""
e05_nball_transformer.py
V(n) = π^(n/2) / Γ(n/2+1) — the Cayley-Dickson layer transformer.

Tests:
  - V(0)=1, V(1)=2, V(2)=π  (exact)
  - peak n* ≈ 5.257
  - ratio V(2k)/V(2k-2) at each CD doubling — is it π/2 throughout?
  - V(16) vs d* = 0.24600
  - where does the π/2 ratio break?
"""

import math
from scipy.special import gamma, digamma
from scipy.optimize import brentq

P16 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
OMEGA_ZS = 0.5671432904097838
D_STAR    = 0.24600
GAP       = OMEGA_ZS - D_STAR * math.log(10.0)   # 0.0007073575... exact given D_STAR


def V(n):
    return math.pi ** (n / 2.0) / gamma(n / 2.0 + 1.0)


def dV_dn(n):
    return V(n) * (math.log(math.pi) / 2.0 - digamma(n / 2.0 + 1.0) / 2.0)


def run():
    results = {}

    # ── exact values ──────────────────────────────────────────────────────────
    exact = {0: 1.0, 1: 2.0, 2: math.pi}
    for n, expected in exact.items():
        got = V(n)
        results[f"V({n})"] = {"got": got, "expected": expected,
                               "pass": abs(got - expected) < 1e-12}

    # ── peak ─────────────────────────────────────────────────────────────────
    n_peak = brentq(dV_dn, 4.0, 7.0)
    results["peak_n"] = {"got": n_peak, "expected": 5.2569, "pass": abs(n_peak - 5.2569) < 1e-3}

    # ── ratios at each CD doubling ─────────────────────────────────────────────
    # doublings: 1→2 (R→C), 2→4 (C→H), 4→8 (H→O), 8→16 (O→S)
    pi_half = math.pi / 2.0
    doublings = [(1, 2, "R→C"), (2, 4, "C→H"), (4, 8, "H→O"), (8, 16, "O→S")]
    for lo, hi, label in doublings:
        ratio = V(hi) / V(lo)
        results[f"ratio_{label}"] = {
            "got": ratio,
            "expected_if_pi_half": pi_half,
            "is_pi_half": abs(ratio - pi_half) < 1e-10,
        }

    # ── V(16) vs d* ──────────────────────────────────────────────────────────
    v16 = V(16)
    results["V16_vs_dstar"] = {
        "V16": v16,
        "d_star": D_STAR,
        "delta": abs(v16 - D_STAR),
        "ratio": v16 / D_STAR,
        "pass": abs(v16 - D_STAR) < 0.01,
    }

    # ── full table ────────────────────────────────────────────────────────────
    table = {n: V(n) for n in range(17)}
    results["table"] = table

    return results


def report(results):
    print("=== e05: N-BALL TRANSFORMER ===\n")

    for key in ["V(0)", "V(1)", "V(2)"]:
        r = results[key]
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  {key} = {r['got']:.15f}  expected {r['expected']:.15f}  [{status}]")

    print()
    r = results["peak_n"]
    status = "PASS" if r["pass"] else "FAIL"
    print(f"  peak n* = {r['got']:.10f}  expected ≈5.2569  [{status}]")

    print("\n  Ratios at each Cayley-Dickson doubling:")
    print(f"  {'Doubling':<8}  {'ratio':<18}  {'π/2':<18}  is π/2?")
    for label in ["R→C", "C→H", "H→O", "O→S"]:
        r = results[f"ratio_{label}"]
        mark = "✓" if r["is_pi_half"] else "✗"
        print(f"  {label:<8}  {r['got']:<18.10f}  {r['expected_if_pi_half']:<18.10f}  {mark}")

    print()
    r = results["V16_vs_dstar"]
    status = "PASS" if r["pass"] else "FAIL"
    print(f"  V(16)  = {r['V16']:.10f}")
    print(f"  d*     = {r['d_star']:.10f}")
    print(f"  delta  = {r['delta']:.10f}  ratio = {r['ratio']:.8f}  [{status}]")

    print("\n  Full V(n) table:")
    for n, v in results["table"].items():
        print(f"    V({n:2d}) = {v:.10f}")


if __name__ == "__main__":
    report(run())
