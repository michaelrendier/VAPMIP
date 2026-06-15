"""
e16_penrose_swap.py
Penrose swap cryptography: (I|O)² ≠ (I|O)⁻¹, GAP as error check.

Tests:
  - (I|O)² ≠ (I|O)⁻¹ on sedenion states
  - (I|O)² ≠ identity (not self-inverse)
  - Perturbation < GAP → geometry snaps back to same firing order
  - Perturbation > GAP → different state nucleates
  - Many-to-one: multiple inputs → same firing order (within GAP basin)
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from _sedenion import *


def normalise(v):
    n = math.sqrt(sum(x*x for x in v))
    return [x/n for x in v] if n > 0 else v


def inside_out_sedenion(v):
    """
    Inside-out on a sedenion state vector v (16 reals on S¹⁵).
    Multiply v as a sedenion by the unit sedenion e1 (imaginary unit).
    This rotates the state through the sedenion structure.
    """
    e1 = e(1)  # first imaginary basis element
    # treat v as a sedenion element and multiply by e1
    result = cd_mul(v, e1)
    return normalise(result)


def apply_io_n_times(v, n):
    result = list(v)
    for _ in range(n):
        result = inside_out_sedenion(result)
    return result


def firing_signature(v):
    """Firing order as a tuple (canonical form for comparison)."""
    return tuple(firing_order(v))


def run():
    results = {}
    random.seed(42)

    # ── (I|O)² ≠ (I|O)⁻¹ ────────────────────────────────────────────────────
    # Test on several sedenion states
    test_states = []
    for text in ["what should we call you", "sedenion zero divisors",
                 "fermat defines riemann fires", "hack the planet"]:
        v, _, _ = geometry_normalised(text)
        test_states.append((text, v))

    io2_neq_io_inv = []
    io2_neq_identity = []
    for label, v in test_states:
        io1 = inside_out_sedenion(v)
        io2 = inside_out_sedenion(io1)

        # Try to find inverse: apply (I|O) repeatedly until we get back to v
        # If period is finite, (I|O)^period = identity
        period = None
        cur = list(v)
        for k in range(1, 33):
            cur = inside_out_sedenion(cur)
            if sum(abs(c-vc) for c, vc in zip(cur, v)) < 1e-8:
                period = k
                break

        # (I|O)⁻¹ would be (I|O)^(period-1) if period exists
        if period is not None:
            io_inv = apply_io_n_times(v, period - 1)
            io2_eq_io_inv = sum(abs(a-b) for a,b in zip(io2, io_inv)) < 1e-8
        else:
            io_inv = None
            io2_eq_io_inv = False

        io2_eq_identity = sum(abs(a-b) for a,b in zip(io2, v)) < 1e-8

        io2_neq_io_inv.append(not io2_eq_io_inv)
        io2_neq_identity.append(not io2_eq_identity)

        test_states[test_states.index((label, v))] = {
            "label": label,
            "period": period,
            "io2_eq_identity": io2_eq_identity,
            "io2_eq_io_inv": io2_eq_io_inv,
        }

    results["io_structure"] = {
        "states": test_states,
        "io2_neq_identity_all": all(io2_neq_identity),
        "io2_neq_io_inv_all": all(io2_neq_io_inv),
        "pass": all(io2_neq_identity),
    }

    # ── GAP as error check: perturbation below GAP ────────────────────────────
    v0, _, _ = geometry_normalised("what should we call you")
    original_sig = firing_signature(v0)

    below_gap_same = 0
    above_gap_different = 0
    n_trials = 100

    for _ in range(n_trials):
        # Perturbation below GAP
        eps_small = random.uniform(GAP * 0.01, GAP * 0.5)
        direction = [random.gauss(0, 1) for _ in range(16)]
        dn = math.sqrt(sum(x*x for x in direction))
        direction = [x/dn * eps_small for x in direction]
        v_perturbed = normalise([a+b for a,b in zip(v0, direction)])
        if firing_signature(v_perturbed) == original_sig:
            below_gap_same += 1

        # Perturbation above GAP
        eps_large = random.uniform(GAP * 2.0, GAP * 10.0)
        direction2 = [random.gauss(0, 1) for _ in range(16)]
        dn2 = math.sqrt(sum(x*x for x in direction2))
        direction2 = [x/dn2 * eps_large for x in direction2]
        v_perturbed2 = normalise([a+b for a,b in zip(v0, direction2)])
        if firing_signature(v_perturbed2) != original_sig:
            above_gap_different += 1

    results["gap_error_check"] = {
        "GAP": GAP,
        "trials": n_trials,
        "below_gap_firing_unchanged": below_gap_same,
        "above_gap_firing_changed": above_gap_different,
        "below_gap_stability": below_gap_same / n_trials,
        "above_gap_sensitivity": above_gap_different / n_trials,
        "pass": below_gap_same > n_trials * 0.5 and above_gap_different > n_trials * 0.5,
    }

    # ── Many-to-one: different inputs, same firing order ──────────────────────
    firing_orders = {}
    corpus = [
        "what should we call you",
        "What Should We Call You",
        "WHAT SHOULD WE CALL YOU",
        "what should  we  call  you",  # extra spaces
        "what should we call you?",
    ]
    for text in corpus:
        v, _, _ = geometry_normalised(text)
        sig = firing_signature(v)
        firing_orders[text] = sig

    unique_signatures = len(set(firing_orders.values()))
    results["many_to_one"] = {
        "inputs": len(corpus),
        "unique_firing_orders": unique_signatures,
        "many_to_one_confirmed": unique_signatures < len(corpus),
        "pass": unique_signatures < len(corpus),
    }

    return results


def report(results):
    print("=== e16: PENROSE SWAP / (I|O) STRUCTURE ===\n")

    r = results["io_structure"]
    print(f"  (I|O)² ≠ identity (not self-inverse): {'PASS' if r['io2_neq_identity_all'] else 'FAIL'}")
    print(f"  (I|O)² ≠ (I|O)⁻¹:                    {'PASS' if r['io2_neq_io_inv_all'] else 'FAIL'}")
    print()
    for s in r["states"]:
        if isinstance(s, dict):
            print(f"    '{s['label'][:35]}'  period={s['period']}  "
                  f"io2=identity:{s['io2_eq_identity']}  io2=io_inv:{s['io2_eq_io_inv']}")

    r = results["gap_error_check"]
    print(f"\n  GAP = {r['GAP']:.6f} as error check ({r['trials']} trials each):")
    print(f"    perturbation < GAP → same firing order:     "
          f"{r['below_gap_firing_unchanged']}/{r['trials']} = {r['below_gap_stability']:.2%}  "
          f"{'PASS' if r['below_gap_stability'] > 0.5 else 'FAIL'}")
    print(f"    perturbation > GAP → different firing order: "
          f"{r['above_gap_firing_changed']}/{r['trials']} = {r['above_gap_sensitivity']:.2%}  "
          f"{'PASS' if r['above_gap_sensitivity'] > 0.5 else 'FAIL'}")

    r = results["many_to_one"]
    print(f"\n  Many-to-one (variant inputs → same firing order):")
    print(f"    {r['inputs']} inputs → {r['unique_firing_orders']} unique firing orders  "
          f"{'PASS' if r['pass'] else 'FAIL'}")


if __name__ == "__main__":
    report(run())
