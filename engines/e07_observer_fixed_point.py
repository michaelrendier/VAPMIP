"""
e07_observer_fixed_point.py
Observer as fixed point: Wankel dual-thread iteration converges to OMEGA_ZS?
wiki/48: σ=½ is an infinitesimal circle with infinite partitions.

Tests:
  - Does iterated sedenion geometry converge to a fixed point?
  - What is that fixed point numerically?
  - Is it OMEGA_ZS = 0.56714329?
  - Gnarl iteration (e02 engine style) from sedenion state → does it converge?
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def gnarl_step(x, y, h=0.01, alpha=3.0):
    """One Gnarl/Popcorn iteration (discrete RedBlue Hamiltonian)."""
    x_new = x - h * math.sin(y + math.tan(alpha * y))
    y_new = y + h * math.sin(x + math.tan(alpha * x))
    return x_new, y_new


def gnarl_converge(x0, y0, h=0.01, alpha=3.0, steps=5000, tol=1e-8):
    """Run Gnarl until convergence or max steps."""
    x, y = x0, y0
    for step in range(steps):
        xn, yn = gnarl_step(x, y, h, alpha)
        if abs(xn - x) < tol and abs(yn - y) < tol:
            return x, y, step, True
        x, y = xn, yn
    return x, y, steps, False


def sedenion_norm_iterate(text, steps=200):
    """
    Iterate: text → geometry → norm → use norm as new 'text scale' → repeat.
    Does ||v|| converge to OMEGA_ZS?
    """
    v, raw, norm = geometry_normalised(text)
    history = [norm]
    for _ in range(steps):
        # Use the norm-scaled firing to generate a new geometry proxy
        # Map: norm → a scalar that feeds back into the geometry
        # Simple feedback: use norm as the 'amplitude' of a constant signal
        scale = norm
        new_raw = [x * scale for x in raw]
        new_norm = math.sqrt(sum(x*x for x in new_raw))
        norm = new_norm / max(new_norm, 1e-12)  # keep normalised
        history.append(norm)
    return history


def fixed_point_from_sedenion_state(text):
    """
    Start Gnarl iteration from the sedenion geometry of text.
    Does it converge, and to what value?
    """
    v, raw, norm = geometry_normalised(text)
    # Use first two normalised components as (x0, y0)
    x0, y0 = v[0], v[1]
    x_eq, y_eq, n_steps, converged = gnarl_converge(x0, y0)
    return {
        "text":       text[:40],
        "x0":         x0, "y0": y0,
        "x_eq":       x_eq, "y_eq": y_eq,
        "r_eq":       math.sqrt(x_eq**2 + y_eq**2),
        "steps":      n_steps,
        "converged":  converged,
        "delta_omega": abs(math.sqrt(x_eq**2 + y_eq**2) - OMEGA_ZS),
    }


CORPUS = [
    "what should we call you",
    "how do i hear your voice",
    "sedenion zero divisors",
    "fermat defines riemann fires",
    "the observer is the fixed point",
    "sigma equals one half",
]


def run():
    results = {}

    # Gnarl fixed point from multiple starting points (sedenion geometries)
    fp_results = [fixed_point_from_sedenion_state(text) for text in CORPUS]
    results["fixed_points"] = fp_results

    # Convergence statistics
    converged = [r for r in fp_results if r["converged"]]
    deltas = [r["delta_omega"] for r in converged]
    results["convergence"] = {
        "n_converged": len(converged),
        "n_total": len(fp_results),
        "mean_delta_omega": sum(deltas)/len(deltas) if deltas else None,
        "max_delta_omega": max(deltas) if deltas else None,
        "all_near_omega": all(d < 0.1 for d in deltas),
        "OMEGA_ZS": OMEGA_ZS,
        "pass": len(converged) > 0 and all(d < 0.5 for d in deltas),
    }

    # Direct Gnarl test: from many random starting points, all converge to OMEGA_ZS?
    import random
    random.seed(42)
    random_results = []
    for _ in range(50):
        x0 = random.uniform(-1, 1)
        y0 = random.uniform(-1, 1)
        x_eq, y_eq, steps, conv = gnarl_converge(x0, y0)
        r_eq = math.sqrt(x_eq**2 + y_eq**2)
        random_results.append({
            "r_eq": r_eq,
            "delta": abs(r_eq - OMEGA_ZS),
            "converged": conv,
        })

    conv_random = [r for r in random_results if r["converged"]]
    results["random_starts"] = {
        "trials": 50,
        "converged": len(conv_random),
        "mean_r_eq": sum(r["r_eq"] for r in conv_random)/len(conv_random) if conv_random else None,
        "mean_delta_omega": sum(r["delta"] for r in conv_random)/len(conv_random) if conv_random else None,
        "pass": len(conv_random) > 20 and (
            sum(r["delta"] for r in conv_random)/len(conv_random) < 0.1 if conv_random else False
        ),
    }

    return results


def report(results):
    print("=== e07: OBSERVER FIXED POINT ===\n")
    print(f"  OMEGA_ZS = {OMEGA_ZS}\n")

    print("  Gnarl convergence from sedenion starting points:")
    print(f"  {'text':<42} {'r_eq':>8}  {'Δω':>8}  {'steps':>7}  conv")
    for r in results["fixed_points"]:
        print(f"  {r['text']:<42} {r['r_eq']:>8.5f}  {r['delta_omega']:>8.5f}  "
              f"{r['steps']:>7}  {r['converged']}")

    c = results["convergence"]
    print(f"\n  Converged: {c['n_converged']}/{c['n_total']}")
    print(f"  Mean Δω:   {c['mean_delta_omega']:.6f}" if c['mean_delta_omega'] else "  (none converged)")
    print(f"  All near OMEGA_ZS (Δ<0.1): {c['all_near_omega']}  [{'PASS' if c['pass'] else 'FAIL'}]")

    r = results["random_starts"]
    print(f"\n  Random starts (50 trials): {r['converged']} converged")
    if r["mean_r_eq"]:
        print(f"  Mean |eq| = {r['mean_r_eq']:.6f}  Mean Δω = {r['mean_delta_omega']:.6f}  "
              f"[{'PASS' if r['pass'] else 'FAIL'}]")


if __name__ == "__main__":
    report(run())
