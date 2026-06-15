"""
_sedenion.py — shared sedenion algebra for validation engines.

Cayley-Dickson construction: 4 doublings from R → C → H → O → S (16D).
Multiplication, conjugate, norm, inside-out operator.
"""

import math

P16 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
OMEGA_ZS = 0.56714329040978387299996866221
D_STAR   = 0.24600
GAP      = 1.0 / (1000.0 * math.sqrt(2.0))   # 0.000707357... = OMEGA_ZS − D_STAR·ln(10)
MONAD_PHI = 1.6180339887


# ── Cayley-Dickson algebra ────────────────────────────────────────────────────

def cd_conj(a):
    """Conjugate: negate all non-real components."""
    return [a[0]] + [-x for x in a[1:]]


def cd_add(a, b):
    return [x + y for x, y in zip(a, b)]


def cd_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def cd_neg(a):
    return [-x for x in a]


def cd_scale(a, s):
    return [x * s for x in a]


def cd_norm2(a):
    return sum(x * x for x in a)


def cd_norm(a):
    return math.sqrt(cd_norm2(a))


def cd_mul(a, b):
    """
    Cayley-Dickson multiplication (a,b)*(c,d) = (ac - conj(d)*b, d*a + b*conj(c))
    Works for any power-of-2 dimension.
    """
    n = len(a)
    assert n == len(b) and n >= 1
    if n == 1:
        return [a[0] * b[0]]
    h = n // 2
    a1, a2 = a[:h], a[h:]
    b1, b2 = b[:h], b[h:]
    c1 = cd_sub(cd_mul(a1, b1), cd_mul(cd_conj(b2), a2))
    c2 = cd_add(cd_mul(b2, a1), cd_mul(a2, cd_conj(b1)))
    return c1 + c2


def e(k, n=16):
    """Basis element e_k in n-dimensional algebra."""
    v = [0.0] * n
    v[k] = 1.0
    return v


def basis_table(n=16):
    """Full multiplication table: table[i][j] = e_i * e_j."""
    return [[cd_mul(e(i, n), e(j, n)) for j in range(n)] for i in range(n)]


# ── Dirichlet projection at σ=½ ───────────────────────────────────────────────

def project(text, k, primes=P16):
    """Project text onto sedenion dimension k via Dirichlet at σ=½."""
    x = 0.0
    for i, c in enumerate(text.encode('utf-8', errors='replace'), 1):
        x += c * (i ** -0.5) * math.cos(2.0 * math.pi * i / primes[k])
    return x


def geometry(text, primes=P16):
    """16 raw projections for text."""
    return [project(text, k, primes) for k in range(16)]


def geometry_normalised(text, primes=P16):
    raw = geometry(text, primes)
    norm = math.sqrt(sum(x * x for x in raw))
    if norm == 0.0:
        return raw, raw, norm
    return [x / norm for x in raw], raw, norm


def firing_order(v):
    """Return dimension indices sorted by ascending |v[k]| — Riemann spiral."""
    return sorted(range(len(v)), key=lambda k: abs(v[k]))


def active_gates(v_norm, raw, thresh_raw):
    """Dimensions where |raw[k]| >= thresh_raw."""
    return [k for k in range(len(v_norm)) if abs(raw[k]) >= thresh_raw]


# ── Inside-out operator ───────────────────────────────────────────────────────

def inside_out(v):
    """
    Inside-out: map v → v' by cycling components through the sedenion structure.
    Implemented as: v'[k] = sum of v[j] * (e_j * e_k)[0] for j in range(16)
    i.e. project each basis product onto the real component.
    """
    tbl = basis_table(len(v))
    result = [0.0] * len(v)
    for k in range(len(v)):
        for j in range(len(v)):
            result[k] += v[j] * tbl[j][k][0]
    return result


# ── J2 involution ─────────────────────────────────────────────────────────────

def j2_swap(v):
    """
    J₂ involution: swap Red (e8-e15) and Blue (e0-e7) sub-algebras.
    R↔B swap.
    """
    n = len(v)
    h = n // 2
    return v[h:] + v[:h]


def j2_is_involution(n=16):
    """Test J₂² = identity on all basis elements."""
    for k in range(n):
        ek = e(k, n)
        swapped = j2_swap(j2_swap(ek))
        if swapped != ek:
            return False
    return True
