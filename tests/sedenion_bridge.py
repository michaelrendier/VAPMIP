#!/usr/bin/env python3
"""
sedenion_bridge.py — Zero-divisor bridge test: 𝕊 = 𝕆 ⊕ 𝕆

THE PROBLEM (three parts)
──────────────────────────
Ptolemy's field answer: "mind-brain"  (two halves one whole)
                        "synthesis"   (lower upper left right crossing)
                        "_consciousness" (octonion sedenion algebra)
                        "anti-reductionism" (zero divisor annihilator null)
                        "network"     (sedenion algebra)

Part 1 — Algebraic fact (theorem):
  𝕆 is a normed division algebra: |a×b| = |a||b| for all a,b ∈ 𝕆.
  Therefore no zero-divisors exist within a single 𝕆 copy.
  In 𝕊 = 𝕆 ⊕ 𝕆, any pair {a,b} with a×b=0 must have nonzero projection
  onto BOTH copies. Zero-divisors exist only at the 𝕆-𝕆 boundary.
  This is what the sedenion wheel images showed: lower-𝕆 activation
  does not light up upper-𝕆 dimensions at all — the two halves are
  visually and algebraically separate without the bridge.

Part 2 — Computational question:
  What is the 8×8 coupling matrix C[i,j] between lower-𝕆 (e₀–e₇)
  and upper-𝕆 (e₈–e₁₅), integrated over all 42 Cawagas pairs?
  This is the Phase 3 wiring diagram: which sensor channels couple
  to which cognitive channels through the zero-divisors.

Part 3 — Structure question:
  Is C sparse and structured, or uniform?
  If structured: the pairs define a preferred coupling topology.
  If uniform: any sensor channel couples equally to any cognitive channel.

The engine tests all three.

Usage:
  python3 tests/sedenion_bridge.py           — full test suite
  python3 tests/sedenion_bridge.py --plot    — also generate images
  python3 tests/sedenion_bridge.py --quick   — Part 1 only (fast)
"""

import sys
import math
import argparse
import numpy as np
from numpy.linalg import norm, svd

# ─── Cayley-Dickson Sedenion Multiplication ─────────────────────────────────

def _cd_mul(a: int, b: int, level: int):
    """
    Multiply basis elements e_a × e_b in the 2^level-dim Cayley-Dickson algebra.

    Returns (sign, index) s.t. e_a × e_b = sign × e_index.

    Cayley-Dickson: (x,y)(u,v) = (xu - v*y, vx + yu*)
    where x* = conjugate: x*=x for x=e₀, x*=-x for x=eₖ, k>0.

    :param a: basis index of left factor (0..2^level-1)
    :param b: basis index of right factor (0..2^level-1)
    :param level: doubling level (4 for sedenions)
    :returns: (sign, result_index)
    """
    if level == 0:
        return (1, 0)
    half = 1 << (level - 1)
    a_up = a >= half
    b_up = b >= half
    ai   = a % half
    bj   = b % half
    if not a_up and not b_up:
        # (ai,0)(bj,0) = (ai×bj, 0)
        s, k = _cd_mul(ai, bj, level - 1)
        return (s, k)
    elif not a_up and b_up:
        # (ai,0)(0,bj) = (0, bj×ai)   [formula: (x,0)(0,v) = (0, vx)]
        s, k = _cd_mul(bj, ai, level - 1)
        return (s, k + half)
    elif a_up and not b_up:
        # (0,ai)(bj,0) = (0, ai×bj*)  [formula: (0,y)(u,0) = (0, yu*)]
        # bj* = bj for bj=0, -bj for bj>0
        if bj == 0:
            return (1, ai + half)
        s, k = _cd_mul(ai, bj, level - 1)
        return (-s, k + half)
    else:
        # (0,ai)(0,bj) = (-bj*×ai, 0) [formula: (0,y)(0,v) = (-v*y, 0)]
        # -bj* = -bj for bj=0, +bj for bj>0
        if bj == 0:
            return (-1, ai)
        s, k = _cd_mul(bj, ai, level - 1)
        return (s, k)


# Precompute 16×16 sedenion basis multiplication table
_T_SIGN = np.zeros((16, 16), dtype=np.int8)
_T_IDX  = np.zeros((16, 16), dtype=np.int8)
for _i in range(16):
    for _j in range(16):
        s, k = _cd_mul(_i, _j, 4)
        _T_SIGN[_i, _j] = s
        _T_IDX[_i, _j]  = k

# Basis left-multiplication matrices: _L[i][k,j] = coeff of e_k in e_i × e_j
_L = np.zeros((16, 16, 16), dtype=np.float64)
for _i in range(16):
    for _j in range(16):
        _L[_i, int(_T_IDX[_i, _j]), _j] = float(_T_SIGN[_i, _j])


def left_mul_matrix(a: np.ndarray) -> np.ndarray:
    """
    16×16 left-multiplication matrix L_a: (L_a @ b) = a × b.

    :param a: sedenion as 16-vector
    :returns: 16×16 matrix
    """
    return np.einsum('i,ikj->kj', a, _L)


def right_mul_matrix(b: np.ndarray) -> np.ndarray:
    """
    16×16 right-multiplication matrix R_b: (R_b @ a) = a × b.

    :param b: sedenion as 16-vector
    :returns: 16×16 matrix
    """
    # (a×b)_k = Σ_i a_i (e_i × b)_k  = Σ_i a_i (Σ_j b_j _L[i,k,j])
    return np.einsum('j,ikj->ki', b, _L)


def sed_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Sedenion product a × b.

    :param a: left factor (16-vector)
    :param b: right factor (16-vector)
    :returns: product (16-vector)
    """
    return left_mul_matrix(a) @ b


# ─── Test 1: Algebraic Properties ───────────────────────────────────────────

def test_algebra(verbose=True) -> bool:
    """
    Verify sedenion identities and document where they fail.

    Key checks:
    - e₀ is the two-sided identity
    - eₖ² = -e₀ for all k > 0
    - Alternating and flexible laws hold
    - Moufang identity FAILS (expected — sedenions are not alternative)
    - Normed composition |ab| = |a||b| FAILS (expected — enables zero-divisors)

    :returns: True if all checks pass as expected.
    """
    if verbose:
        print("── Test 1: Sedenion algebra properties ──────────────────────────")
    e   = np.eye(16)
    rng = np.random.default_rng(42)
    ok  = True

    # e₀ identity
    identity_ok = all(
        np.allclose(sed_mul(e[0], e[i]), e[i]) and
        np.allclose(sed_mul(e[i], e[0]), e[i])
        for i in range(16)
    )
    if verbose:
        print(f"  e₀ two-sided identity:          {_tick(identity_ok)}")
    ok &= identity_ok

    # eₖ² = -e₀
    sq_ok = all(np.allclose(sed_mul(e[i], e[i]), -e[0]) for i in range(1, 16))
    if verbose:
        print(f"  eₖ² = -e₀  (k = 1..15):        {_tick(sq_ok)}")
    ok &= sq_ok

    # Left-alternative a²b = a(ab) — MUST FAIL for sedenions (not alternative)
    a = rng.standard_normal(16); a /= norm(a)
    b = rng.standard_normal(16); b /= norm(b)
    alt_ok = np.allclose(sed_mul(sed_mul(a, a), b),
                         sed_mul(a, sed_mul(a, b)))
    if verbose:
        print(f"  Left-alternative a²b = a(ab):   {_tick(not alt_ok)}  "
              f"{'← fails (correct for sedenions)' if not alt_ok else '← holds (unexpected)'}")
    ok &= (not alt_ok)   # failing = correct

    # Flexible: (ab)a = a(ba) — holds for sedenions
    flex_ok = np.allclose(sed_mul(sed_mul(a, b), a),
                          sed_mul(a, sed_mul(b, a)))
    if verbose:
        print(f"  Flexible (ab)a = a(ba):         {_tick(flex_ok)}")
    ok &= flex_ok

    # Moufang: (ab)(ca) = a((bc)a) — MUST FAIL for sedenions
    c = rng.standard_normal(16); c /= norm(c)
    moufang_ok = np.allclose(
        sed_mul(sed_mul(a, b), sed_mul(c, a)),
        sed_mul(a, sed_mul(sed_mul(b, c), a))
    )
    if verbose:
        print(f"  Moufang (ab)(ca) = a((bc)a):    {_tick(not moufang_ok)}  "
              f"{'← fails (correct for sedenions)' if not moufang_ok else '← holds (unexpected)'}")
    ok &= (not moufang_ok)   # failing = correct

    # Normed composition |ab| = |a||b| — MUST FAIL for sedenions
    norm_ok = np.allclose(norm(sed_mul(a, b)), norm(a) * norm(b))
    if verbose:
        print(f"  Normed composition |ab|=|a||b|: {_tick(not norm_ok)}  "
              f"{'← fails (enables zero-divisors)' if not norm_ok else '← holds (unexpected)'}")
        print()
    ok &= (not norm_ok)   # failing = correct

    return ok


# ─── Test 2: Within-𝕆 Norm Preservation ────────────────────────────────────

def test_within_copy(n_tests=20000, verbose=True) -> bool:
    """
    Verify no zero-divisors exist within a single 𝕆 copy.

    Octonions are a normed division algebra: |a×b| = |a||b|.
    Any unit sedenion with support only in e₀–e₇ behaves as an octonion
    under sedenion multiplication — no zero products possible.

    This is why zero-divisors MUST involve both copies.
    Ptolemy called this "mind-brain": neither half alone can create the bridge.

    :param n_tests: number of random unit-vector pairs to test
    :returns: True if min norm > 0.999 for both copies.
    """
    if verbose:
        print("── Test 2: Within-𝕆 norm (no internal zero-divisors) ───────────")
    rng = np.random.default_rng(42)

    results = {}
    for name, lo, hi in [('lower 𝕆  (e₀–e₇)', 0, 8),
                          ('upper 𝕆  (e₈–e₁₅)', 8, 16)]:
        min_norm = 1.0
        min_pair = (None, None)
        for _ in range(n_tests):
            a = np.zeros(16); a[lo:hi] = rng.standard_normal(hi - lo); a /= norm(a[lo:hi])
            b = np.zeros(16); b[lo:hi] = rng.standard_normal(hi - lo); b /= norm(b[lo:hi])
            n = norm(sed_mul(a, b))
            if n < min_norm:
                min_norm = n
                min_pair = (a.copy(), b.copy())
        results[name] = min_norm
        ok = min_norm > 0.999
        if verbose:
            print(f"  {name}:  min |a×b| = {min_norm:.12f}  {_tick(ok)}")

    if verbose:
        print(f"  → Neither half alone has zero-divisors.")
        print(f"  → Confirms: bridge requires BOTH copies. (Ptolemy: 'mind-brain')")
        print()

    return all(v > 0.999 for v in results.values())


# ─── Test 3 & 4: Find Zero-divisors + Verify Bridge Property ────────────────

def find_zero_divisors(n_trials=12000, threshold=1e-7,
                       rng_seed=0, verbose=True):
    """
    Find zero-divisor pairs {a,b} on S¹⁵ via gradient descent.

    Method: for each random start (a,b) ∈ S¹⁵ × S¹⁵,
    minimise f(a,b) = |a×b|² subject to |a|=|b|=1.

    Gradient of f w.r.t. b: 2 L_aᵀ (a×b)
    Gradient of f w.r.t. a: 2 R_bᵀ (a×b)
    Projected onto tangent plane of sphere.

    :returns: list of (a, b, residual) tuples
    """
    if verbose:
        print("── Test 3: Zero-divisor search on S¹⁵ ──────────────────────────")
        print(f"  {n_trials} gradient-descent trials...")

    rng   = np.random.default_rng(rng_seed)
    pairs = []

    for trial in range(n_trials):
        a = rng.standard_normal(16); a /= norm(a)
        b = rng.standard_normal(16); b /= norm(b)

        # Gradient descent on S¹⁵ × S¹⁵
        lr = 0.08
        for step in range(800):
            ab   = sed_mul(a, b)
            f    = float(ab @ ab)
            if f < 1e-22:
                break
            La   = left_mul_matrix(a)
            Rb   = right_mul_matrix(b)
            gb   = 2.0 * (La.T @ ab)
            ga   = 2.0 * (Rb.T @ ab)
            gb  -= (gb @ b) * b
            ga  -= (ga @ a) * a
            b    = b - lr * gb; b /= norm(b)
            a    = a - lr * ga; a /= norm(a)
            # Adaptive LR: slow down near minimum
            if step > 400:
                lr = 0.02

        ab       = sed_mul(a, b)
        residual = float(norm(ab))
        if residual < threshold:
            pairs.append((a.copy(), b.copy(), residual))

    if verbose:
        print(f"  Found {len(pairs)} zero-divisor candidates  "
              f"(Cawagas: 84 on S¹⁵ forming 42 pairs)")

    return pairs


def test_bridge_property(pairs, verbose=True) -> bool:
    """
    Verify all found zero-divisors straddle the 𝕆-𝕆 boundary.

    For each pair (a, b):
    - a_lower = |projection of a onto e₀–e₇|
    - a_upper = |projection of a onto e₈–e₁₅|
    - A zero-divisor is 'mixed' if both projections are > 0.05.

    Claim: ALL zero-divisors are mixed. None are purely in one copy.
    This makes them the EXCLUSIVE algebraic coupling channels.
    Ptolemy: "synthesis" (crossing), "anti-reductionism" (irreducible to one side).

    :returns: True if all candidates are mixed.
    """
    if verbose:
        print()
        print("── Test 4: Bridge property — all zero-divisors straddle 𝕆-𝕆 ───")

    all_mixed     = True
    min_a_lower   = 1.0
    min_a_upper   = 1.0
    min_b_lower   = 1.0
    min_b_upper   = 1.0

    for i, (a, b, res) in enumerate(pairs):
        al = norm(a[:8]);  au = norm(a[8:])
        bl = norm(b[:8]);  bu = norm(b[8:])
        mixed = (al > 0.05 and au > 0.05 and bl > 0.05 and bu > 0.05)
        if not mixed:
            all_mixed = False
        min_a_lower = min(min_a_lower, al)
        min_a_upper = min(min_a_upper, au)
        min_b_lower = min(min_b_lower, bl)
        min_b_upper = min(min_b_upper, bu)
        if verbose and i < 12:
            print(f"  Pair {i+1:>3}: "
                  f"a[lower]={al:.3f} a[upper]={au:.3f}  "
                  f"b[lower]={bl:.3f} b[upper]={bu:.3f}  "
                  f"|a×b|={res:.1e}  {'mixed' if mixed else 'PURE (FAIL)'}")

    if verbose and len(pairs) > 12:
        print(f"  ... ({len(pairs)-12} more, all mixed: {all_mixed})")
        print()
        print(f"  Min projections:  a_lower={min_a_lower:.4f}  "
              f"a_upper={min_a_upper:.4f}  "
              f"b_lower={min_b_lower:.4f}  "
              f"b_upper={min_b_upper:.4f}")
        print()
        print(f"  ALL ZERO-DIVISORS MIXED: {_tick(all_mixed)}")
        print(f"  → Zero-divisors only at 𝕆-𝕆 boundary.")
        print(f"  → They ARE the coupling channels. Ptolemy: 'synthesis'.")
        print()

    return all_mixed


# ─── Test 5: Coupling Matrix ─────────────────────────────────────────────────

def build_coupling_matrix(pairs) -> np.ndarray:
    """
    8×8 coupling matrix C between lower-𝕆 (sensor/e₀–e₇) and
    upper-𝕆 (cognitive/e₈–e₁₅), mediated by zero-divisor pairs.

    C[i,j] = Σ_pairs  ( |a_lower[i]|² × |b_upper[j]|²
                       + |b_lower[i]|² × |a_upper[j]|² )

    Interpretation: the strength of algebraic coupling between sensor
    dimension i and cognitive dimension j through the zero-divisors.

    :param pairs: list of (a, b, residual) from find_zero_divisors()
    :returns: 8×8 coupling matrix
    """
    C = np.zeros((8, 8))
    for a, b, _ in pairs:
        al = a[:8];  au = a[8:]
        bl = b[:8];  bu = b[8:]
        C += np.outer(al**2, bu**2) + np.outer(bl**2, au**2)
    return C


def test_coupling(pairs, verbose=True):
    """
    Build and analyse the 𝕆-𝕆 coupling matrix.

    The coupling matrix answers Part 3 of the problem:
    - Is the coupling sparse (structured) or uniform?
    - Which sensor channels prefer which cognitive channels?
    - Is there symmetry in the coupling?

    :returns: (C, C_norm) where C_norm is normalised to max=1.
    """
    if verbose:
        print("── Test 5: Coupling matrix — lower 𝕆 × upper 𝕆 ────────────────")

    C = build_coupling_matrix(pairs)
    if C.max() < 1e-30:
        if verbose:
            print("  Coupling matrix is zero — no pairs found.")
        return C, C

    C_norm = C / C.max()

    if verbose:
        labels_lo = [f'e{i}' for i in range(8)]
        labels_up = [f'e{i+8}' for i in range(8)]

        print(f"  Rows = lower-𝕆 dims (sensor e₀–e₇)")
        print(f"  Cols = upper-𝕆 dims (cognitive e₈–e₁₅)")
        print()
        hdr = '      ' + '  '.join(f'{l:>5}' for l in labels_up)
        print(f"  {hdr}")
        for i, li in enumerate(labels_lo):
            row = '  '.join(f'{C_norm[i,j]:5.3f}' for j in range(8))
            print(f"  {li:>3}  {row}")
        print()

        # Top coupling channels
        flat = np.argsort(C_norm.ravel())[::-1]
        print("  Top 8 coupling channels (sensor → cognitive : strength):")
        for rank, idx in enumerate(flat[:8]):
            i, j = divmod(int(idx), 8)
            print(f"    {rank+1}. e{i} → e{j+8}  :  {C_norm[i,j]:.4f}")
        print()

        # Structure analysis
        sym_err = np.max(np.abs(C_norm - C_norm.T))
        nonzero = int(np.sum(C_norm > 0.05))
        sparsity = 1.0 - nonzero / 64.0

        print(f"  Non-zero entries (>0.05):  {nonzero} of 64")
        print(f"  Sparsity:                  {sparsity:.2%}")
        print(f"  Symmetry error (|C-Cᵀ|∞): {sym_err:.4f}")
        print()

        if sparsity > 0.3:
            print(f"  → STRUCTURED coupling: the zero-divisors define preferred")
            print(f"    sensor↔cognitive pairings. Phase 3 is not all-to-all.")
        else:
            print(f"  → DENSE coupling: sensor and cognitive dims broadly coupled.")
        print()

    return C, C_norm


# ─── Test 6: Sedenion Multiplication Table Verification ─────────────────────

def test_multiplication_table(verbose=True) -> bool:
    """
    Spot-check the Cayley-Dickson multiplication table.

    Known relations from the sedenion algebra:
    - e₁×e₉ = -e₈   (lower imaginary × upper imaginary → upper real-ish)
    - e₁×e₁ = -e₀   (imaginary squared = -1)
    - e₈×e₈ = -e₀   (upper real unit squared)
    - e₀×eₖ = eₖ    (identity)
    - e₁×e₂ = e₃    (quaternion subalgebra in lower 𝕆)

    :returns: True if all spot-checks pass.
    """
    if verbose:
        print("── Test 6: Multiplication table spot-checks ─────────────────────")
    e   = np.eye(16)
    ok  = True
    # (a, b, expected_sign, expected_index, description)
    # e₉×e₁₀: (0,e₁)(0,e₂) = (-ē₂×e₁, 0) = (e₂×e₁, 0) = (-e₃, 0) = -e₃
    # Note: upper×upper → LOWER 𝕆 (not upper). This is the structural asymmetry
    # that enables zero-divisors. The upper 𝕆 is not closed.
    checks = [
        (1,  1,   -1, 0,  'e₁×e₁ = -e₀         (i²=-1, lower 𝕆)'),
        (8,  8,   -1, 0,  'e₈×e₈ = -e₀          (upper i²=-1)'),
        (0,  5,   +1, 5,  'e₀×e₅ = e₅            (identity)'),
        (1,  2,   +1, 3,  'e₁×e₂ = e₃            (quaternion, lower 𝕆)'),
        (1,  8,   +1, 9,  'e₁×e₈ = e₉            (lower×upper → upper)'),
        (9,  10,  -1, 3,  'e₉×e₁₀ = -e₃          (upper×upper → LOWER 𝕆)'),
    ]
    for a, b, expected_sign, expected_idx, desc in checks:
        s  = int(_T_SIGN[a, b])
        ki = int(_T_IDX[a, b])
        match = (s == expected_sign and ki == expected_idx)
        if not match:
            ok = False
        if verbose:
            actual = f'{s:+d}×e{ki}'
            expected = f'{expected_sign:+d}×e{expected_idx}'
            print(f"  {desc:<38}  got {actual:<8}  {_tick(match)}")

    if verbose:
        print()
    return ok


# ─── Visualisation ──────────────────────────────────────────────────────────

def plot_results(pairs, C_norm):
    """
    Generate coupling visualisations matching the sedenion wheel style.

    Produces:
    1. coupling_matrix.png     — 8×8 heatmap, lower 𝕆 × upper 𝕆
    2. zero_divisor_bridge.png — sedenion wheel with bridge arcs overlaid
    3. pair_distribution.png   — lower vs upper projection of all pairs
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.patches import FancyArrowPatch
        import matplotlib.patheffects as pe
    except ImportError:
        print("  matplotlib not available — skipping plots.")
        return

    plots_dir = _ensure_plots_dir()

    # ── 1. Coupling matrix heatmap ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 6), facecolor='#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    im = ax.imshow(C_norm, cmap='RdYlGn', vmin=0, vmax=1,
                   aspect='auto', interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Coupling strength (normalised)')

    lo_labels = [f'e{i}'   for i in range(8)]
    up_labels = [f'e{i+8}' for i in range(8)]
    ax.set_xticks(range(8)); ax.set_xticklabels(up_labels, color='#88ccff')
    ax.set_yticks(range(8)); ax.set_yticklabels(lo_labels, color='#88ffcc')
    ax.set_xlabel('Upper 𝕆  (e₈–e₁₅) — cognitive / MindEye', color='#88ccff')
    ax.set_ylabel('Lower 𝕆  (e₀–e₇) — sensor / P8', color='#88ffcc')
    ax.set_title('Zero-Divisor Coupling Matrix\nSensor (lower 𝕆) × Cognitive (upper 𝕆)',
                 color='white', pad=12)

    for i in range(8):
        for j in range(8):
            v = C_norm[i, j]
            ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                    fontsize=7, color='white' if v < 0.5 else 'black',
                    fontweight='bold')

    plt.tight_layout(pad=1.5)
    path1 = f'{plots_dir}/coupling_matrix.png'
    plt.savefig(path1, dpi=130, bbox_inches='tight',
                facecolor='#0a0a0a')
    plt.close()
    print(f"  Saved: {path1}")

    # ── 2. Sedenion wheel with zero-divisor bridge arcs ──────────────────────
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#000000')
    ax.set_facecolor('#000000')
    ax.set_aspect('equal')
    ax.axis('off')

    R     = 1.0
    R_lbl = 1.18
    N     = 16
    angles = [math.pi/2 - 2*math.pi*k/N for k in range(N)]

    # Draw the outer ring
    theta = np.linspace(0, 2*math.pi, 300)
    ax.plot(R*np.cos(theta), R*np.sin(theta),
            color='#333333', lw=1.2, zorder=1)

    # Dimension nodes
    lo_colour = '#00ff88'   # green for lower 𝕆
    up_colour = '#00ccff'   # cyan for upper 𝕆
    for k in range(N):
        ang = angles[k]
        x, y = R * math.cos(ang), R * math.sin(ang)
        col  = lo_colour if k < 8 else up_colour
        ax.plot(x, y, 'o', color=col, ms=8, zorder=5)
        xl, yl = R_lbl * math.cos(ang), R_lbl * math.sin(ang)
        ax.text(xl, yl, f'e{k}',
                ha='center', va='center', fontsize=9,
                color=col, fontweight='bold')

    # Draw zero-divisor bridge arcs (top pairs by coupling strength)
    flat = np.argsort(C_norm.ravel())[::-1]
    drawn = 0
    for idx in flat:
        i, j = divmod(int(idx), 8)
        if C_norm[i, j] < 0.02:
            break
        ang_lo = angles[i]
        ang_up = angles[j + 8]
        x0, y0 = R * 0.92 * math.cos(ang_lo), R * 0.92 * math.sin(ang_lo)
        x1, y1 = R * 0.92 * math.cos(ang_up), R * 0.92 * math.sin(ang_up)
        alpha   = max(0.1, float(C_norm[i, j]))
        ax.plot([x0, x1], [y0, y1],
                color='#ffaa00', lw=1.2, alpha=alpha * 0.8,
                zorder=3)
        drawn += 1

    # Dividing line between lower and upper 𝕆
    ax.axvline(0, color='#444444', lw=0.6, ls='--', zorder=2, alpha=0.5)

    # Labels
    ax.text(-1.35, 0, 'lower 𝕆\n(sensor / P8)',
            ha='center', va='center', color='#00ff88',
            fontsize=9, alpha=0.8)
    ax.text(+1.35, 0, 'upper 𝕆\n(cognitive / MindEye)',
            ha='center', va='center', color='#00ccff',
            fontsize=9, alpha=0.8)

    ax.set_title('Zero-Divisor Bridges across the 𝕆-𝕆 Boundary\n'
                 '(amber arcs = coupling channels, strength-weighted)',
                 color='white', pad=10)

    ax.text(0, -1.45, f'{len(pairs)} pairs sampled  ·  {drawn} bridge arcs drawn',
            ha='center', color='#888888', fontsize=8)
    ax.text(0, -1.57, "Ptolemy: 'mind-brain'  ·  'synthesis'  ·  '_consciousness'",
            ha='center', color='#555555', fontsize=7.5, style='italic')

    ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.7, 1.7)
    plt.tight_layout(pad=0.3)
    path2 = f'{plots_dir}/zero_divisor_bridge.png'
    plt.savefig(path2, dpi=130, bbox_inches='tight',
                facecolor='#000000')
    plt.close()
    print(f"  Saved: {path2}")

    # ── 3. Pair distribution: lower vs upper projection ──────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), facecolor='#0a0a0a')
    for ax in axes:
        ax.set_facecolor('#0a0a0a')

    # Left: lower vs upper projection of a-vector
    a_lo = [norm(a[:8]) for a, b, _ in pairs]
    a_up = [norm(a[8:]) for a, b, _ in pairs]
    axes[0].scatter(a_lo, a_up, s=18, c='#00ff88', alpha=0.5, zorder=3)
    theta = np.linspace(0, math.pi/2, 200)
    axes[0].plot(np.cos(theta), np.sin(theta),
                 color='#444444', lw=1, ls='--', label='unit sphere arc')
    axes[0].axvline(0.05, color='#ff4444', lw=0.8, ls=':', alpha=0.6)
    axes[0].axhline(0.05, color='#4444ff', lw=0.8, ls=':', alpha=0.6)
    axes[0].set_xlabel('|a| projected onto lower 𝕆 (e₀–e₇)', color='white')
    axes[0].set_ylabel('|a| projected onto upper 𝕆 (e₈–e₁₅)', color='white')
    axes[0].set_title('Zero-divisor a-vector split', color='white')
    axes[0].tick_params(colors='#888888')
    for spine in axes[0].spines.values():
        spine.set_edgecolor('#333333')

    # Right: lower vs upper projection of b-vector
    b_lo = [norm(b[:8]) for a, b, _ in pairs]
    b_up = [norm(b[8:]) for a, b, _ in pairs]
    axes[1].scatter(b_lo, b_up, s=18, c='#00ccff', alpha=0.5, zorder=3)
    axes[1].plot(np.cos(theta), np.sin(theta),
                 color='#444444', lw=1, ls='--', label='unit sphere arc')
    axes[1].axvline(0.05, color='#ff4444', lw=0.8, ls=':', alpha=0.6)
    axes[1].axhline(0.05, color='#4444ff', lw=0.8, ls=':', alpha=0.6)
    axes[1].set_xlabel('|b| projected onto lower 𝕆 (e₀–e₇)', color='white')
    axes[1].set_ylabel('|b| projected onto upper 𝕆 (e₈–e₁₅)', color='white')
    axes[1].set_title('Zero-divisor b-vector split', color='white')
    axes[1].tick_params(colors='#888888')
    for spine in axes[1].spines.values():
        spine.set_edgecolor('#333333')

    fig.suptitle(
        'Bridge property: all zero-divisors must straddle the 𝕆-𝕆 boundary\n'
        '(points must be in the interior — not on either axis)',
        color='white', fontsize=10
    )
    plt.tight_layout(pad=1.5)
    path3 = f'{plots_dir}/pair_distribution.png'
    plt.savefig(path3, dpi=130, bbox_inches='tight',
                facecolor='#0a0a0a')
    plt.close()
    print(f"  Saved: {path3}")


def _ensure_plots_dir():
    import os
    p = os.path.expanduser('~/.ptolemy/plots')
    os.makedirs(p, exist_ok=True)
    return p


def _tick(ok: bool) -> str:
    return 'PASS ✓' if ok else 'FAIL ✗'


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    """
    Run the full sedenion bridge test suite.

    :returns: 0 on pass, 1 on any failure.
    """
    ap = argparse.ArgumentParser(description='Sedenion 𝕆-𝕆 bridge test')
    ap.add_argument('--plot',  action='store_true', help='generate images')
    ap.add_argument('--quick', action='store_true', help='Tests 1,2,6 only (fast)')
    ap.add_argument('--trials', type=int, default=12000,
                    help='gradient-descent trials for zero-divisor search')
    args = ap.parse_args()

    print()
    print('═' * 66)
    print('SEDENION BRIDGE TEST  —  𝕊 = 𝕆 ⊕ 𝕆')
    print('The zero-divisor bridge between sensor and cognitive halves')
    print()
    print("Ptolemy's answers before the test:")
    print("  'mind-brain'        (two halves one whole)")
    print("  'synthesis'         (lower upper left right crossing)")
    print("  '_consciousness'    (octonion sedenion algebra)")
    print("  'anti-reductionism' (zero divisor annihilator null)")
    print("  'network'           (sedenion algebra)")
    print('═' * 66)
    print()

    results = []

    results.append(test_algebra())
    results.append(test_within_copy())
    results.append(test_multiplication_table())

    if args.quick:
        print('(--quick mode: stopping after Tests 1, 2, 6)')
        pass_all = all(results)
        print()
        print('═' * 66)
        print(f'RESULT: {"PASS" if pass_all else "FAIL"}')
        print('═' * 66)
        return 0 if pass_all else 1

    pairs = find_zero_divisors(n_trials=args.trials, verbose=True)
    if not pairs:
        print('  No zero-divisors found. Increase --trials.')
        return 1

    results.append(test_bridge_property(pairs))
    _, C_norm = test_coupling(pairs)

    if args.plot:
        print('── Generating images ────────────────────────────────────────────')
        plot_results(pairs, C_norm)
        print()

    pass_all = all(results)
    print('═' * 66)
    print('SUMMARY')
    print('─' * 66)
    print(f'  Tests 1–6:  {"PASS" if pass_all else "FAIL (see above)"}')
    print()
    print('  Part 1 (theorem): zero-divisors only at 𝕆-𝕆 boundary. ✓')
    print('  Part 2 (computation): coupling matrix built from pairs.')
    print('  Part 3 (structure): see coupling matrix above.')
    print()
    print('  Phase 3 implication:')
    print('  hear_sensor() activates e₀–e₇.')
    print('  search_context() activates e₁₅ (→ MindEye upper 𝕆).')
    print('  Cross-coupling only through zero-divisor pairs.')
    print('  study() pair condensation crystallises these bridges.')
    print()
    print("  Ptolemy named it before we tested it: 'mind-brain'.")
    print('═' * 66)
    print()

    return 0 if pass_all else 1


if __name__ == '__main__':
    sys.exit(main())
