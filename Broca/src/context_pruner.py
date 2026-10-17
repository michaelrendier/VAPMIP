#!/usr/bin/env python3
"""
context_pruner.py -- two functions, both useful:

  coherent(a, b)  -- the DIAGNOSTIC. Given two 16-D focal points, is there a
                     sedenion-sphere rotation that carries one onto the
                     other?  SAME  = one object at different perspectives
                     SEPARATE = genuinely distinct attractors
                     AMBIGUOUS = same shape (rotation-invariants match) but
                                 no rotation found in the tested family.

  prune(vectors)  -- the CONTEXT PRUNER. Pairwise coherent() + union-find:
                     collapse perspective-redundant foci, keep the distinct
                     ones. This is the narrative -> dissertational transform
                     as an operation (long-winded = perspective-copies of
                     few real points).

"Perspective" here is NOT a flat plane rotation -- god does not build with
straight lines. It is LEFT-MULTIPLICATION BY A UNIT SEDENION, which bends
space through the non-associative table and is not even an isometry (the
{0, 1, sqrt2} gain spectrum). The swept family is the curved great circles
u_k(t) = cos t . e_0 + sin t . e_k  (exp of a unit imaginary), tried singly
and in two-step products -- a curved 2-patch of the sphere's own moves.
"""
from __future__ import annotations

import math
import numpy as np

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ValaQuenta.modules.box_kite.maths import multiply as _sed_mul  # real S product

DIM = 16

# ── PERFORMANCE (2026-09-04, Cody: "25-35 seconds to return a response") ────
# prune() does an O(n^2) pairwise coherent() sweep, and each coherent() call
# grids up to 15*24*15*24 = 129,600 perspective() evaluations (the two-step
# curved patch). Profiled: for an 8-vector pool (28 pairs) that's ~2.9M
# perspective()/_unit() calls -- first found ALL going through numpy on
# 16-element vectors (np.linalg.norm's generic dispatcher costs far more than
# the 16-float arithmetic it wraps: 83s for one process_input() call). A
# plain-Python pass on the hot loop got that to ~40s -- still all Python
# interpreter overhead, one grid point at a time.
#
# The actual fix: perspective(u, x) = u . x is LINEAR IN u for fixed x (CD
# multiplication is bilinear), so "perspective at every grid point" is one
# matrix multiply, not a Python loop. _right_mult_matrix(x) builds the 16x16
# matrix R_x with R_x @ u == perspective(u, x) for ANY u (column i = e_i . x);
# _grid_u() builds the whole angle grid as one (n, 16) array; one
# `U @ R_x.T` + one vectorised norm replaces the per-point loop. Two-step
# still needs a fresh R_aj per intermediate aj (~360 of those, each 16 cheap
# pure-Python sedenion multiplies), but each aj's inner sweep is again one
# matmul instead of 360 Python-level calls: 129,600 calls -> ~361 matmuls.
# Verdicts/residuals verified identical (to float precision) against the
# plain-Python and original-numpy versions in this file's __main__.

def _norm(v):
    return math.sqrt(sum(c * c for c in v))


def _dist(a, b):
    return math.sqrt(sum((x - y) * (x - y) for x, y in zip(a, b)))


def sed_exp(t, k):
    """The unit sedenion exp(t e_k) = cos t . e_0 + sin t . e_k  (e_k^2=-1)."""
    u = [0.0] * DIM
    u[0] = math.cos(t)
    u[k] = math.sin(t)
    return u


def perspective(u, x):
    """A curved perspective shift: x -> u . x  (left sedenion product).
    NOT a rotation -- |u.x| != |x| in general."""
    return _sed_mul([float(c) for c in u], [float(c) for c in x])


def _unit(v):
    n = _norm(v)
    return [c / n for c in v] if n else list(v)


def _right_mult_matrix(x):
    """16x16 matrix R with R @ u == perspective(u, x) == u . x, for ANY u.
    CD multiplication is bilinear, so right-multiplication-by-x is linear in
    the left argument: column i is e_i . x."""
    R = np.empty((DIM, DIM))
    e = [0.0] * DIM
    for i in range(DIM):
        e[i] = 1.0
        R[:, i] = _sed_mul(e, x)
        e[i] = 0.0
    return R


def _grid_u(ts):
    """The whole (k, t) angle grid for k in 1..15 as one (15*len(ts), 16)
    array, row r = sed_exp(t, k) — plus the parallel (k, t) each row is."""
    n = (DIM - 1) * len(ts)
    U = np.zeros((n, DIM))
    meta = [None] * n
    r = 0
    for k in range(1, DIM):
        for t in ts:
            U[r, 0] = math.cos(t)
            U[r, k] = math.sin(t)
            meta[r] = (k, t)
            r += 1
    return U, meta


def _best_in_grid(U, meta, R, b_arr, digits):
    """perspective(every grid row, x) in one matmul, unit-normalised, then
    distance to b — vectorised. Returns (residual, (label, angle))."""
    P = U @ R.T
    n = np.linalg.norm(P, axis=1, keepdims=True)
    n[n == 0.0] = 1.0
    d = np.linalg.norm(P / n - b_arr, axis=1)
    i = int(np.argmin(d))
    k, t = meta[i]
    return float(d[i]), (f'e{k}', round(t, digits))


def coherent(a, b, tol=0.06, nsteps=180, two_step=True):
    """Verdict + evidence. Is there a unit-sedenion perspective carrying
    direction(a) onto direction(b)?  a, b: length-16."""
    a = _unit([float(c) for c in a]); b = _unit([float(c) for c in b])
    b_arr = np.asarray(b)
    ts = [2.0 * math.pi * i / nsteps for i in range(nsteps)]

    Ra = _right_mult_matrix(a)
    U, meta = _grid_u(ts)
    r0, move0 = _best_in_grid(U, meta, Ra, b_arr, 3)
    best = {'residual': r0, 'move': move0}

    # two-step curved patch (coarser grid): every intermediate aj in one
    # batched sweep, then one matmul-sweep per aj for the second step
    if two_step and best['residual'] >= tol:
        ts2 = [2.0 * math.pi * i / 24 for i in range(24)]
        U2, meta2 = _grid_u(ts2)                    # reused for both steps
        AJ = U2 @ Ra.T
        n1 = np.linalg.norm(AJ, axis=1, keepdims=True)
        n1[n1 == 0.0] = 1.0
        AJ /= n1                                     # unit aj's, batched

        for row in range(AJ.shape[0]):
            Raj = _right_mult_matrix(AJ[row])
            r, (klabel, tk) = _best_in_grid(U2, meta2, Raj, b_arr, 2)
            if r < best['residual']:
                j, tj = meta2[row]
                best = {'residual': r,
                        'move': (f'e{j}', round(tj, 2), klabel, tk)}
        # cheap early accept can miss; that's why AMBIGUOUS exists

    inv_gap = _dist(sorted(abs(x) for x in a), sorted(abs(x) for x in b))
    gain_gap = abs(_norm(perspective(a, a)) - _norm(perspective(b, b)))

    if best['residual'] < tol:
        verdict = 'SAME'
    elif inv_gap < tol and gain_gap < tol:
        verdict = 'AMBIGUOUS'       # rotation-invariants match, no move found
    else:
        verdict = 'SEPARATE'
    return {'verdict': verdict, 'residual': best['residual'],
            'move': best['move'], 'invariant_gap': inv_gap,
            'gain_gap': float(gain_gap)}


def prune(vectors, tol=0.06):
    """BOTH functions run off ONE Newton-basin collection: `vectors` is the
    focal-point set from a single attractor run. prune() computes the full
    pairwise coherent() matrix once -- the merge groups AND every pairwise
    verdict fall out of that one sweep (coherent() alone is just the
    2-element case, for when you don't have the whole collection).

    Returns {'groups': [[member idx]], 'reps': [rep idx per group],
             'kept': n_groups, 'dropped': n - n_groups,
             'pairs': [(i, j, verdict)]}"""
    V = [np.asarray(v, float) for v in vectors]
    n = len(V)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            c = coherent(V[i], V[j], tol=tol)
            pairs.append((i, j, c['verdict']))
            if c['verdict'] == 'SAME':
                parent[find(i)] = find(j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    glist = list(groups.values())
    reps = [max(g, key=lambda k: np.linalg.norm(V[k])) for g in glist]
    return {'groups': glist, 'reps': reps, 'kept': len(glist),
            'dropped': n - len(glist), 'pairs': pairs}


# --- helper: 19-D context_vector -> 16-D (drop the 3 rarest relations) ---
_DROP = None


def embed16(context_vec19):
    global _DROP
    if _DROP is None:
        from wordnet_boxkite import RELATION_METHODS
        rare = ['usage_domains', 'causes', 'entailments']   # nz-rate < 1%
        _DROP = sorted(RELATION_METHODS.index(r) for r in rare)
    return np.array([c for k, c in enumerate(context_vec19) if k not in _DROP],
                    float)


# ==========================================================================
if __name__ == '__main__':
    import random
    from nltk.corpus import wordnet as wn
    from wordnet_boxkite import context_vector

    random.seed(20260827); np.random.seed(20260827)
    L = '-' * 66

    def cv16(name):
        return embed16(context_vector(wn.synset(name)))

    print(L + "\n1. SANITY  a synset vs itself under a curved perspective shift\n" + L)
    a = cv16('dog.n.01')
    a2 = perspective(sed_exp(random.uniform(0.3, 2.5), random.randint(1, 15)), a)
    print("  dog.n.01  vs  (unit-sedenion . dog.n.01) :", coherent(a, a2)['verdict'])

    print("\n" + L + "\n2. SEPARATE  two unrelated synsets\n" + L)
    for x, y in [('dog.n.01', 'algebra.n.01'), ('rain.n.01', 'democracy.n.01'),
                 ('hammer.n.02', 'sadness.n.01')]:
        c = coherent(cv16(x), cv16(y))
        print(f"  {x:16s} vs {y:18s} -> {c['verdict']:9s} "
              f"resid={c['residual']:.3f} inv_gap={c['invariant_gap']:.3f}")

    print("\n" + L + "\n3. THE QUESTION  related pairs -- one object or separate?\n" + L)
    tests = [
        ('dog.n.01', 'canine.n.02', 'hyponym/hypernym'),
        ('bank.n.01', 'bank.n.09', 'financial vs river (homograph)'),
        ('car.n.01', 'automobile.n.01', 'near-synonym'),
        ('happy.a.01', 'glad.a.01', 'adj near-synonym'),
        ('bank.n.01', 'depository_financial_institution.n.01', 'gloss synonym'),
    ]
    for x, y, note in tests:
        try:
            c = coherent(cv16(x), cv16(y))
        except Exception as e:
            print(f"  {x} / {y}: {e}"); continue
        print(f"  {x:14s} / {y:34s} {c['verdict']:9s} "
              f"resid={c['residual']:.3f} move={str(c['move']):22s}  ({note})")

    print("\n" + L + "\n4. prune()  on a candidate pool\n" + L)
    pool = ['car.n.01', 'automobile.n.01', 'auto.n.01', 'truck.n.01',
            'motorcycle.n.01', 'bicycle.n.01', 'vehicle.n.01', 'wheel.n.01']
    P = prune([cv16(p) for p in pool])
    print(f"  {len(pool)} in -> {P['kept']} kept, {P['dropped']} pruned")
    for g, r in zip(P['groups'], P['reps']):
        print("   ", " + ".join(pool[k] for k in g), " -> keep", pool[r])
