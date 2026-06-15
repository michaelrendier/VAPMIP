"""
e14_fermat_near_miss.py
Fermat near-misses from The Simpsons — precision analysis.

Tests:
  - 3987^12 + 4365^12 - 4472^12: at what decimal place does it fail?
  - 1782^12 + 1841^12 - 1922^12: same
  - Claim: a 10-digit calculator cannot distinguish from 0
  - What precision is required to detect the non-zero residual?
"""

import mpmath
mpmath.mp.dps = 50  # 50 decimal places

def near_miss_residual(a, b, c, n, label):
    A = mpmath.power(a, n)
    B = mpmath.power(b, n)
    C = mpmath.power(c, n)
    residual = A + B - C
    sum_AB = A + B

    # How many significant figures agree?
    if residual == 0:
        sig_figs = float('inf')
    else:
        sig_figs = -mpmath.log10(abs(residual / sum_AB))

    return {
        "label": label,
        "a": a, "b": b, "c": c, "n": n,
        "A+B":     float(sum_AB),
        "C":       float(C),
        "residual": mpmath.nstr(residual, 20),
        "residual_float": float(residual),
        "sig_figs_agree": float(sig_figs),
        "invisible_at_10_digits": float(sig_figs) >= 10,
    }


def run():
    results = {}

    results["homer3"] = near_miss_residual(
        1782, 1841, 1922, 12,
        "Homer³ blackboard (S07E06)"
    )
    results["wizard"] = near_miss_residual(
        3987, 4365, 4472, 12,
        "Wizard of Evergreen Terrace (S10E02)"
    )

    # Also test: what n makes FLT exact? (n=1 and n=2)
    results["n1"] = near_miss_residual(3, 4, 5, 1, "trivial n=1")
    results["n2"] = near_miss_residual(3, 4, 5, 2, "Pythagorean n=2")

    return results


def report(results):
    print("=== e14: FERMAT NEAR-MISS PRECISION ===\n")

    for key in ["homer3", "wizard"]:
        r = results[key]
        status = "PASS (invisible at 10 digits)" if r["invisible_at_10_digits"] else "FAIL (visible at 10 digits)"
        print(f"  {r['label']}")
        print(f"    {r['a']}^{r['n']} + {r['b']}^{r['n']} vs {r['c']}^{r['n']}")
        print(f"    residual      = {r['residual']}")
        print(f"    sig figs agree= {r['sig_figs_agree']:.4f}")
        print(f"    10-digit blind = {r['invisible_at_10_digits']}  [{status}]")
        print()

    print("  Reference (exact solutions):")
    for key in ["n1", "n2"]:
        r = results[key]
        print(f"    {r['label']}: residual = {r['residual']}")


if __name__ == "__main__":
    report(run())
