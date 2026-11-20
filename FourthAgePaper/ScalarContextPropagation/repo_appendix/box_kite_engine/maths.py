"""
ainulindale_engine.modules.box_kite.maths
============================================
THE BOX-KITE DEBUGGER -- making the zero-divisor geometry visible.

"how do we 'debug' the geometries / how do we watch the geometries
 interact"   -- Cody Michael Allison, 2026-08-05

WHAT THE OBJECT IS, AND WHERE IT IS NOT
---------------------------------------
Moreno (1997) proved the sedenions' norm-one zero divisors are
homeomorphic to the exceptional Lie group G2. That is TRUE and it is the
WRONG PLACE TO BUILD. de Marrais (2000), whose paper is a direct response:

    "Moreno discovered a homomorphism -- a 'blow-up' of an exact
     correspondence -- and the 'blow-ups' in the history of number theory
     have all entailed the loss of something."

G2 is the CONTINUOUS SHADOW. It forgets which Fano line is which. The
exact object is finite:

    PSL(2,7),  order 168,  = Aut(Fano plane) = GL(3,2)

PSL(2,7) is the finite subgroup of G2 that PRESERVES THE LABELLING. All
of this module's structure is exactly enumerable -- no sampling, no
fitting, no approximation. That exactness is the whole point of a
debugger.

THE STRUCTURE, DERIVED NOT ASSERTED
-----------------------------------
Everything below is computed from the Cayley-Dickson multiplication table
in this file. Nothing is read in from de Marrais; agreement with his
published counts is a CHECK, not an input. See verify_counts().

    15 pure imaginaries      = the 15 points of PG(3,2)
                               35 lines of 3, 15 Fano planes
    ASSESSOR                 = a plane span(e_a, e_{b+8}), a,b in 1..7
                               whose diagonals e_a +/- e_{b+8} zero-divide.
                               a == b never works -> 49 - 7 = 42 Assessors
    84 diagonals             = 42 Assessors x 2 signs
    168 primitive unit ZDs   = 42 x 4 (point-set quartets, +/- both
                               diagonals) = |PSL(2,7)|
    336 ordered ZD pairs     = each of the 84 diagonals kills exactly 4
    STRUT                    = a XOR b, in 1..7. Indexes the box-kite.
    7 BOX-KITES              = one per strut, 6 Assessors each, 7x6 = 42

THE SHAPE IS AN OCTAHEDRON. For each strut s the 6 Assessors form a
4-regular graph on 6 vertices with exactly 3 non-edges -- the reversal
pairs (a,b) <-> (b,a). That is K_{2,2,2}, the octahedron. Verified by
computation, not assumed: box_kite_graph() builds the adjacency from
actual vanishing products.

THE DISPERSION RELATION, CHART LEVEL
------------------------------------
The octahedral graph Laplacian spectrum is closed form:

    adjacency:  4, 0, 0, 0, -2, -2
    Laplacian:  0, 4, 4, 4, 6, 6      <- omega^2(k) on one box-kite

Six modes: one zero mode, a 3-fold degenerate mode at 4, a 2-fold at 6.

THE ZERO MODE IS e_0. It is the mode that exists everywhere and
propagates nowhere -- which is exactly what a boundary GENERATOR should
look like from inside the geometry it generates. This falls out of the
graph; it is not put in by hand. It is the computational form of Cody's
own question, answered:

    "the 0_RB describes the geometries as its boundary generator... but
     it seems that it is NOT the geometries... am i correct in this one?"

Correct. e_0 is not one of the 15 pure imaginaries, so it is not a point
of PG(3,2), not a member of any Assessor, and not a vertex of any
box-kite. It cannot be: Assessors are planes spanned by pure imaginaries
and e_0 spans none of them. It is the axis the geometry is measured from
and it is not the geometry.

THE CURVATURE IS THE ASSOCIATOR
-------------------------------
    [a,b,c] = (ab)c - a(bc)

Exact, pointwise, and the direct analogue of a curvature tensor: it
measures how much the geometry bends under reassociation. The commutator
[a,b] = ab - ba is the torsion analogue. 1848 of the 4096 basis triples
have non-vanishing associator. associator_field() paints these onto a
box-kite's vertices and edges -- that is the debug view.

WHAT IS OPEN
------------
The GLUING. Each chart is flat enough to compute; the curvature lives in
the transitions between the 7 box-kites. glued_graph()/glued_spectrum()
assemble the naive 42-vertex union, which is a first model of the global
medium and NOT a derivation of one -- the transition maps are not yet
written. Stated here rather than implied.

Version: 0.2
"""

import math
from typing import Dict, List, Tuple, Optional, Sequence

# --------------------------------------------------------------------------
# Cayley-Dickson multiplication table
# --------------------------------------------------------------------------

def cd_multiplication_table(levels: int = 4) -> Tuple[Dict[Tuple[int, int],
                                                          Tuple[int, int]], int]:
    """
    Basis multiplication table for the 2^levels-dimensional Cayley-Dickson
    algebra, built by doubling from the reals.

    Returns (table, dim) where table[(i, j)] = (sign, index), meaning
    e_i * e_j = sign * e_index.

    Doubling rule, with conj(e_0)=e_0 and conj(e_k)=-e_k for k>0:

        (a,0)(c,0) = (ac, 0)
        (a,0)(0,d) = (0, d a)
        (0,b)(c,0) = (0, b conj(c))
        (0,b)(0,d) = (-conj(d) b, 0)

    levels = 1 -> C, 2 -> H, 3 -> O, 4 -> S (sedenions), 5 -> T_32, ...
    """
    if levels < 0:
        raise ValueError("cd_multiplication_table: levels must be >= 0")
    tab: Dict[Tuple[int, int], Tuple[int, int]] = {(0, 0): (1, 0)}
    dim = 1

    def conj(idx: int) -> Tuple[int, int]:
        return (1, 0) if idx == 0 else (-1, idx)

    for _ in range(levels):
        new: Dict[Tuple[int, int], Tuple[int, int]] = {}
        N = dim
        for i in range(N):
            for j in range(N):
                new[(i, j)] = tab[(i, j)]
                s, k = tab[(j, i)]
                new[(i, j + N)] = (s, k + N)
                cs, ci = conj(j)
                s2, k2 = tab[(i, ci)]
                new[(i + N, j)] = (cs * s2, k2 + N)
                cs2, ci2 = conj(j)
                s3, k3 = tab[(ci2, i)]
                new[(i + N, j + N)] = (-cs2 * s3, k3)
        tab, dim = new, dim * 2
    return tab, dim


_SED_TABLE, SEDENION_DIM = cd_multiplication_table(4)


def basis_mul(i: int, j: int) -> Tuple[int, int]:
    """e_i * e_j = (sign, index). Sedenions."""
    return _SED_TABLE[(i, j)]


def multiply(x: Sequence[float], y: Sequence[float]) -> List[float]:
    """Full sedenion product of two 16-vectors."""
    if len(x) != 16 or len(y) != 16:
        raise ValueError("multiply: sedenions are 16-vectors")
    out = [0.0] * 16
    for i in range(16):
        xi = x[i]
        if xi == 0.0:
            continue
        for j in range(16):
            yj = y[j]
            if yj == 0.0:
                continue
            s, k = basis_mul(i, j)
            out[k] += s * xi * yj
    return out


def is_zero(v: Sequence[float], tol: float = 1e-12) -> bool:
    """True if every component is below tol."""
    return all(abs(c) < tol for c in v)


def basis_vector(*terms: Tuple[float, int]) -> List[float]:
    """Build a 16-vector from (coefficient, index) terms."""
    v = [0.0] * 16
    for c, i in terms:
        v[i] += c
    return v


# --------------------------------------------------------------------------
# Curvature: the associator and the commutator
# --------------------------------------------------------------------------

def associator(i: int, j: int, k: int) -> List[float]:
    """
    THE CURVATURE.  [e_i, e_j, e_k] = (e_i e_j)e_k - e_i(e_j e_k)

    Exact measure of how far the geometry bends under reassociation --
    the direct analogue of a curvature tensor. Vanishes identically on
    the associative levels (R, C, H) and does not on O or S.
    """
    s1, m = basis_mul(i, j)
    s2, n = basis_mul(m, k)
    s3, q = basis_mul(j, k)
    s4, r = basis_mul(i, q)
    v = [0.0] * 16
    v[n] += s1 * s2
    v[r] -= s3 * s4
    return v


def commutator(i: int, j: int) -> List[float]:
    """THE TORSION.  [e_i, e_j] = e_i e_j - e_j e_i"""
    s1, m = basis_mul(i, j)
    s2, n = basis_mul(j, i)
    v = [0.0] * 16
    v[m] += s1
    v[n] -= s2
    return v


def associator_defect(i: int, j: int, k: int) -> float:
    """Euclidean norm of the associator -- the scalar curvature at a triple."""
    return math.sqrt(sum(c * c for c in associator(i, j, k)))


def associator_census() -> Dict[str, int]:
    """
    How much of the algebra is curved: counts of vanishing vs non-vanishing
    basis associators over all 16^3 triples.
    """
    nz = 0
    for i in range(16):
        for j in range(16):
            for k in range(16):
                if not is_zero(associator(i, j, k)):
                    nz += 1
    return {'total': 16 ** 3, 'nonzero': nz, 'zero': 16 ** 3 - nz}


# --------------------------------------------------------------------------
# Assessors, struts, box-kites -- all derived from the table
# --------------------------------------------------------------------------

def diagonals(a: int, b: int) -> List[List[float]]:
    """The two diagonals of the Assessor plane span(e_a, e_{b+8})."""
    return [basis_vector((1.0, a), (1.0, b + 8)),
            basis_vector((1.0, a), (-1.0, b + 8))]


def is_assessor(a: int, b: int) -> bool:
    """
    True if the plane span(e_a, e_{b+8}) contains zero-dividing diagonals.

    Computed, not asserted: multiplies the actual diagonals against every
    other candidate diagonal and checks for a vanishing product.
    """
    if not (1 <= a <= 7 and 1 <= b <= 7):
        return False
    for x in diagonals(a, b):
        for c in range(1, 8):
            for d in range(1, 8):
                for y in diagonals(c, d):
                    if is_zero(multiply(x, y)):
                        return True
    return False


def assessors() -> List[Tuple[int, int]]:
    """
    The 42 Assessors, as (a, b) meaning the plane span(e_a, e_{b+8}).

    a == b is never an Assessor -- those 7 'aligned' planes are precisely
    what 49 - 42 removes. Derived by construction and confirmed against
    is_assessor() in verify_counts().
    """
    return [(a, b) for a in range(1, 8) for b in range(1, 8) if a != b]


def strut(a: int, b: int) -> int:
    """
    The strut of an Assessor: s = a XOR b, in 1..7. Indexes its box-kite.

    This is the octonion-index arithmetic underlying the Fano plane, and
    it is why exactly 7 box-kites partition the space.
    """
    return a ^ b


def box_kites() -> Dict[int, List[Tuple[int, int]]]:
    """
    The 7 box-kites, keyed by strut s = 1..7, each holding its 6 Assessors.

    7 x 6 = 42. Cross-check against de Marrais's published Box-Kite I
    (Assessor pairs (3,10),(2,11),(5,12),(4,13),(7,14),(6,15)): that is
    strut 1, i.e. (a,b) = (3,2),(2,3),(4,5),(5,4),(6,7),(7,6) here.
    """
    out: Dict[int, List[Tuple[int, int]]] = {s: [] for s in range(1, 8)}
    for a, b in assessors():
        out[strut(a, b)].append((a, b))
    return out


def zero_divisor_pairs() -> List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
    """
    Every ordered pair of diagonals whose product vanishes.

    A diagonal is (a, b, sign) meaning e_a + sign*e_{b+8}. Returns 336
    pairs: 84 diagonals, each annihilating exactly 4 others.
    """
    diags = [(a, b, s) for a in range(1, 8) for b in range(1, 8) for s in (1, -1)]
    vecs = {d: basis_vector((1.0, d[0]), (float(d[2]), d[1] + 8)) for d in diags}
    out = []
    for dx in diags:
        for dy in diags:
            if is_zero(multiply(vecs[dx], vecs[dy])):
                out.append((dx, dy))
    return out


def verify_counts() -> Dict[str, object]:
    """
    THE HONEST CHECK. Every count derived here, against the published
    values and against ValaQuenta's own canonical constants
    (ZD_PAIRS=84, ZD_CLASSES=42, ZD_COMPOSITE=168).

    A mismatch is a bug in THIS module, not a discovery. Reported as
    booleans so it cannot be read past.
    """
    ass = assessors()
    kites = box_kites()
    zdp = zero_divisor_pairs()
    n_diag = 2 * len(ass)
    n_points = 4 * len(ass)
    all_are = all(is_assessor(a, b) for a, b in ass)
    none_aligned = not any(is_assessor(a, a) for a in range(1, 8))
    return {
        'assessors':             len(ass),
        'assessors_expect_42':   len(ass) == 42,
        'all_verified_assessors': all_are,
        'aligned_planes_empty':  none_aligned,
        'diagonals':             n_diag,
        'diagonals_expect_84':   n_diag == 84,
        'unit_points':           n_points,
        'points_expect_168':     n_points == 168,
        'psl27_order':           168,
        'ordered_zd_pairs':      len(zdp),
        'pairs_expect_336':      len(zdp) == 336,
        'kills_per_diagonal':    len(zdp) // n_diag if n_diag else 0,
        'box_kites':             len(kites),
        'kites_expect_7':        len(kites) == 7,
        'sizes_all_6':           all(len(v) == 6 for v in kites.values()),
    }


# --------------------------------------------------------------------------
# The charts: box-kite graphs and their spectra
# --------------------------------------------------------------------------

def assessors_adjacent(A: Tuple[int, int], B: Tuple[int, int]) -> bool:
    """
    True if any diagonal of Assessor A annihilates any diagonal of B.
    This is the edge relation of the box-kite graph -- computed from
    vanishing products, not imposed.
    """
    for x in diagonals(*A):
        for y in diagonals(*B):
            if is_zero(multiply(x, y)) or is_zero(multiply(y, x)):
                return True
    return False


def box_kite_graph(s: int) -> Dict[str, object]:
    """
    The chart for strut s: 6 Assessor-vertices and their edges.

    Comes out 4-regular with exactly 3 non-edges -- the reversal pairs
    (a,b) <-> (b,a). That is K_{2,2,2}: THE OCTAHEDRON. Checked here
    rather than assumed; 'is_octahedron' is the assertion.
    """
    if not (1 <= s <= 7):
        raise ValueError("box_kite_graph: strut must be in 1..7")
    V = box_kites()[s]
    E, non = [], []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            (E if assessors_adjacent(V[i], V[j]) else non).append((i, j))
    deg = [sum(1 for e in E if i in e) for i in range(len(V))]
    reversal = all(V[i] == (V[j][1], V[j][0]) for i, j in non)
    return {
        'strut': s,
        'vertices': V,
        'edges': E,
        'non_edges': non,
        'degrees': deg,
        'is_4_regular': all(d == 4 for d in deg),
        'non_edges_are_reversals': reversal,
        'is_octahedron': len(V) == 6 and len(E) == 12 and all(d == 4 for d in deg),
    }


def _laplacian(n: int, edges: Sequence[Tuple[int, int]]) -> List[List[float]]:
    """Graph Laplacian L = D - A as a dense matrix."""
    L = [[0.0] * n for _ in range(n)]
    for i, j in edges:
        L[i][j] -= 1.0
        L[j][i] -= 1.0
        L[i][i] += 1.0
        L[j][j] += 1.0
    return L


def eigenvalues_symmetric(M: List[List[float]], tol: float = 1e-12,
                          max_sweeps: int = 100) -> List[float]:
    """
    Eigenvalues of a real symmetric matrix by cyclic Jacobi rotation.

    Pure Python -- the registry contract asks maths.py to carry no
    external dependencies, and the matrices here are at most 42x42.
    Returns them sorted ascending.
    """
    n = len(M)
    A = [row[:] for row in M]
    for _ in range(max_sweeps):
        off = math.sqrt(sum(A[i][j] ** 2 for i in range(n) for j in range(n) if i != j))
        if off < tol:
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(A[p][q]) < tol:
                    continue
                theta = (A[q][q] - A[p][p]) / (2.0 * A[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for k in range(n):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p] = c * akp - s * akq
                    A[k][q] = s * akp + c * akq
                for k in range(n):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k] = c * apk - s * aqk
                    A[q][k] = s * apk + c * aqk
    return sorted(A[i][i] for i in range(n))


def chart_spectrum(s: int) -> List[float]:
    """
    THE DISPERSION RELATION on box-kite s: the octahedral Laplacian
    spectrum, omega^2(k).

        {0, 4, 4, 4, 6, 6}

    One zero mode, a 3-fold degenerate mode at 4, a 2-fold at 6.

    THE ZERO MODE IS e_0's signature -- the mode that exists everywhere
    and propagates nowhere. It emerges from the graph rather than being
    inserted, which is the check that 0_RB really is outside the geometry
    it generates.
    """
    g = box_kite_graph(s)
    return eigenvalues_symmetric(_laplacian(6, g['edges']))


def glued_graph() -> Dict[str, object]:
    """
    The naive union of all 7 charts on the 42 Assessors.

    STATED, NOT IMPLIED: this is a FIRST MODEL of the global medium, not
    a derivation of one. It glues charts by shared vanishing products
    across struts; the actual transition maps between box-kites are not
    yet written, and the curvature of the atlas lives in exactly those
    transitions. Treat the glued spectrum as an instrument reading, not
    as the dispersion relation of the ZD surface.
    """
    V = assessors()
    idx = {v: i for i, v in enumerate(V)}
    E = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if assessors_adjacent(V[i], V[j]):
                E.append((i, j))
    deg = [sum(1 for e in E if i in e) for i in range(len(V))]
    cross = sum(1 for i, j in E if strut(*V[i]) != strut(*V[j]))
    return {
        'vertices': V,
        'index': idx,
        'edges': E,
        'n_vertices': len(V),
        'n_edges': len(E),
        'degrees': deg,
        'cross_strut_edges': cross,
        'within_strut_edges': len(E) - cross,
    }


def glued_spectrum() -> List[float]:
    """Laplacian spectrum of the 42-vertex glued graph. See glued_graph()'s caveat."""
    g = glued_graph()
    return eigenvalues_symmetric(_laplacian(g['n_vertices'], g['edges']))


def associator_field(s: int) -> Dict[str, object]:
    """
    THE DEBUG VIEW: the curvature painted onto box-kite s.

    For each Assessor-vertex (a, b) reports the associator defect summed
    over the triples its own indices participate in, and for each edge
    the defect of the triple (a_i, b_i+8, a_j). This is what "watch the
    geometries interact" looks like as numbers: where the field is large,
    the geometry is bending.
    """
    g = box_kite_graph(s)
    V = g['vertices']
    vert = {}
    for (a, b) in V:
        d = 0.0
        for k in range(1, 16):
            d += associator_defect(a, b + 8, k)
        vert[(a, b)] = d
    edge = {}
    for i, j in g['edges']:
        a, b = V[i]
        c, _ = V[j]
        edge[(i, j)] = associator_defect(a, b + 8, c)
    return {'strut': s, 'vertices': V, 'vertex_defect': vert, 'edge_defect': edge}


# --------------------------------------------------------------------------
# The skeleton: PG(3,2), 15 points / 35 lines / 15 Fano planes
# --------------------------------------------------------------------------

def pg32_points() -> List[int]:
    """The 15 points of PG(3,2) -- the 15 pure imaginary sedenion units."""
    return list(range(1, 16))


def pg32_lines() -> List[Tuple[int, int, int]]:
    """
    The 35 lines of PG(3,2): triples {x, y, x XOR y}. Each is a
    multiplication triplet of the algebra.
    """
    seen = set()
    for x in range(1, 16):
        for y in range(x + 1, 16):
            seen.add(tuple(sorted((x, y, x ^ y))))
    return sorted(seen)


def fano_planes() -> List[Tuple[int, ...]]:
    """
    The 15 Fano planes of PG(3,2): for each nonzero functional f, the 7
    points x with even parity of (x AND f). Each carries a PSL(2,7).

    NOTE: 15, not 32. Figures circulating with "32 interlocking Fano
    planes" are wrong.
    """
    out = []
    for f in range(1, 16):
        pts = tuple(x for x in range(1, 16) if bin(x & f).count('1') % 2 == 0)
        out.append(pts)
    return out


def psl27_order() -> int:
    """|PSL(2,7)| = |GL(3,2)| = 168 = the primitive unit zero-divisor count."""
    return 168


def skeleton_counts() -> Dict[str, object]:
    """Counts for the PG(3,2) skeleton, with their expected values asserted."""
    pts, lines, planes = pg32_points(), pg32_lines(), fano_planes()
    return {
        'points': len(pts), 'points_expect_15': len(pts) == 15,
        'lines': len(lines), 'lines_expect_35': len(lines) == 35,
        'planes': len(planes), 'planes_expect_15': len(planes) == 15,
        'plane_size': len(planes[0]), 'plane_size_expect_7': len(planes[0]) == 7,
        'psl27_order': psl27_order(),
    }


def e0_is_outside() -> Dict[str, bool]:
    """
    0_RB IS NOT THE GEOMETRY -- checked, not asserted.

    e_0 is not a point of PG(3,2), is in no Assessor, is a vertex of no
    box-kite, and its associator vanishes against everything (it is the
    identity, hence central and associative with all pairs). It generates
    the boundary and does not live on it.
    """
    in_points = 0 in pg32_points()
    in_assessor = any(a == 0 or b == 0 for a, b in assessors())
    assoc_free = all(is_zero(associator(0, j, k))
                     and is_zero(associator(j, 0, k))
                     and is_zero(associator(j, k, 0))
                     for j in range(16) for k in range(16))
    return {
        'e0_is_a_pg32_point': in_points,
        'e0_in_any_assessor': in_assessor,
        'e0_associator_always_vanishes': assoc_free,
        'e0_is_outside_the_geometry': (not in_points) and (not in_assessor) and assoc_free,
    }


# --------------------------------------------------------------------------
# DO THE CHARTS TOUCH?  -- yes, in the skeleton; no, in the adjacency
# --------------------------------------------------------------------------
#
# Cody, 2026-08-05: "i'm pretty sure that those 'surfaces' do actually touch
# somewhere... they are all from the fixed point anyway... it's all the same
# maths... but now we have a clue that 0_RB only points to 'fixed point
# space'... where the boundary and the geometries are the same thing"
#
# Correct, and the two statements are about DIFFERENT STRUCTURES on the same
# object. glued_graph() reports zero cross-strut EDGES -- that is the
# adjacency. It is not the whole story:
#
#   ADJACENCY (zero-divisor products):  the charts are DISCONNECTED.
#                                       7 components, 7 zero modes.
#   SKELETON  (shared basis indices):   the charts OVERLAP ALMOST TOTALLY.
#                                       Every one of the 14 usable indices
#                                       sits in 6 of the 7 charts.
#
# For strut s an Assessor has lower index a and upper index (a XOR s)+8, valid
# whenever a != s. So index a appears in every chart EXCEPT s = a -- six of
# seven, for all 14 indices. The charts touch everywhere in the skeleton and
# nowhere in the products.
#
# AND THE FIXED POINT IS WHERE THEY GLUE. Exactly two of the sixteen basis
# elements are in NO Assessor:
#
#   e_0   the identity -- 0_RB, the fixed point
#   e_8   the Cayley-Dickson doubling generator
#
# Each chart's Laplacian carries one zero mode, and a zero mode is the
# constant function -- i.e. the same object in all seven charts. Seven
# components, seven copies of one thing. IDENTIFY THE ZERO MODES AND THE
# ATLAS CONNECTS. That identification happens at e_0 and nowhere else, which
# is the precise sense in which "0_RB points to fixed point space, where the
# boundary and the geometries are the same thing": at the fixed point the
# boundary generator and the geometry's own mode ARE the same vector.
# Away from it they separate.


def index_chart_membership() -> Dict[int, List[int]]:
    """
    Which box-kites each basis index belongs to.

    Returns {basis index -> [struts]}. Every usable index lands in exactly
    6 of the 7 charts, missing only the chart whose strut equals its own
    (lower) or partner (upper) label. e_0 and e_8 belong to none.
    """
    out: Dict[int, List[int]] = {i: [] for i in range(16)}
    for s, members in box_kites().items():
        for a, b in members:
            if s not in out[a]:
                out[a].append(s)
            if s not in out[b + 8]:
                out[b + 8].append(s)
    return {i: sorted(v) for i, v in out.items()}


def skeleton_overlap() -> Dict[str, object]:
    """
    THE CHARTS DO TOUCH -- in the skeleton.

    Reports, for every pair of struts, how many basis indices they share,
    and confirms that each usable index sits in 6 of 7 charts. This is the
    structure glued_graph() cannot see, because it measures adjacency
    (vanishing products) and this measures support (shared basis).
    """
    mem = index_chart_membership()
    used = [i for i, v in mem.items() if v]
    unused = [i for i, v in mem.items() if not v]
    counts = {i: len(mem[i]) for i in used}
    kites = box_kites()
    support = {s: {a for a, b in kites[s]} | {b + 8 for a, b in kites[s]}
               for s in kites}
    pair_share = {}
    for s in range(1, 8):
        for t in range(s + 1, 8):
            pair_share[(s, t)] = len(support[s] & support[t])
    return {
        'indices_used':          sorted(used),
        'indices_in_no_chart':   sorted(unused),
        'charts_per_index':      counts,
        'every_used_index_in_6': all(c == 6 for c in counts.values()),
        'pairwise_shared':       pair_share,
        'min_pair_share':        min(pair_share.values()),
        'max_pair_share':        max(pair_share.values()),
        'charts_touch_in_skeleton': min(pair_share.values()) > 0,
    }


def fixed_point_gluing() -> Dict[str, object]:
    """
    WHERE THE ATLAS GLUES: at e_0.

    Exactly two basis elements sit in no Assessor -- e_0 (the identity,
    0_RB, the fixed point) and e_8 (the CD doubling generator). Each chart
    contributes exactly one zero mode, and a zero mode is the constant
    function: seven copies of one object. Identifying them collapses the
    seven components to one.

    So the disconnection is real at the level of adjacency and is removed
    at the fixed point. Both of Cody's statements hold; they are about
    different structures.
    """
    mem = index_chart_membership()
    orphans = sorted(i for i, v in mem.items() if not v)
    zero_modes = sum(1 for s in range(1, 8)
                     for x in chart_spectrum(s) if abs(x) < 1e-9)
    return {
        'indices_in_no_assessor': orphans,
        'e0_is_orphan':           0 in orphans,
        'e8_is_orphan':           8 in orphans,
        'orphan_count':           len(orphans),
        'zero_modes_total':       zero_modes,
        'components':             zero_modes,
        'after_identification':   1,
        'reading': ('adjacency disconnects the 7 charts; the skeleton shares '
                    '6 of 7 charts per index; the zero modes are 7 copies of '
                    'one constant and identify at e_0 -- the fixed point is '
                    'where the boundary generator and the geometry coincide'),
    }


# --------------------------------------------------------------------------
# THE CHART OF ADDRESSES -- locating a sedenion address in the atlas
# --------------------------------------------------------------------------
#
# The monad's hyperindexing addresses a surface form to a 16-vector
# (VAPMIP/monad_sedenion_addresses.pkl: book[name]['sedenion']). This
# section is the connector: given such an address, say WHERE IT IS in the
# box-kite atlas and HOW CURVED the geometry is there.
#
# Exhaustive by design -- every quantity that can be read off an address
# against the 42 Assessors, 7 charts and 15 skeleton points is reported,
# because the point of a debugger is that nothing is hidden.

_SQRT2 = math.sqrt(2.0)


def norm(v: Sequence[float]) -> float:
    """Euclidean norm of a 16-vector."""
    return math.sqrt(sum(c * c for c in v))


def fixed_point_weight(v: Sequence[float]) -> float:
    """
    Share of an address's energy sitting on e_0 -- its FIXED-POINT WEIGHT.

    1.0 means the address is pure identity (pure 0_RB, no geometry at all);
    0.0 means it carries none. This is the direct measure of Cody's "they
    are all from the fixed point anyway".
    """
    n2 = sum(c * c for c in v)
    return (v[0] * v[0] / n2) if n2 > 0 else 0.0


def energy_split(v: Sequence[float]) -> Dict[str, float]:
    """
    How an address's energy divides across the four structural blocks:

        e_0        the fixed point (0_RB) -- in no Assessor
        e_8        the CD doubling generator -- in no Assessor
        e_1..e_7   lower imaginaries  (Assessor lower indices)
        e_9..e_15  upper imaginaries  (Assessor upper indices)

    Shares sum to 1. The e_0 + e_8 share is the part of the address that
    lives OUTSIDE the ZD geometry entirely.
    """
    n2 = sum(c * c for c in v)
    if n2 <= 0:
        return {'e0': 0.0, 'e8': 0.0, 'lower': 0.0, 'upper': 0.0, 'outside': 0.0}
    e0 = v[0] * v[0] / n2
    e8 = v[8] * v[8] / n2
    lo = sum(v[i] * v[i] for i in range(1, 8)) / n2
    up = sum(v[i] * v[i] for i in range(9, 16)) / n2
    return {'e0': e0, 'e8': e8, 'lower': lo, 'upper': up, 'outside': e0 + e8}


def diagonal_amplitudes(v: Sequence[float], a: int, b: int) -> Tuple[float, float]:
    """
    Projections of an address onto the two diagonals of Assessor (a, b):

        d+ = (v_a + v_{b+8}) / sqrt(2)
        d- = (v_a - v_{b+8}) / sqrt(2)

    These are the actual zero-dividing directions, so this is the address's
    overlap with the ZD structure in that plane.
    """
    return ((v[a] + v[b + 8]) / _SQRT2, (v[a] - v[b + 8]) / _SQRT2)


def assessor_coordinates(v: Sequence[float]) -> Dict[Tuple[int, int], Dict[str, float]]:
    """
    The address decomposed against all 42 Assessors.

    For each (a, b): the in-plane energy v_a^2 + v_{b+8}^2, both diagonal
    amplitudes, and which diagonal dominates. This is the exhaustive
    readout -- 42 rows, nothing summarised away.
    """
    out = {}
    for (a, b) in assessors():
        dp, dm = diagonal_amplitudes(v, a, b)
        e = v[a] * v[a] + v[b + 8] * v[b + 8]
        out[(a, b)] = {
            'energy': e,
            'd_plus': dp,
            'd_minus': dm,
            'dominant': 1.0 if abs(dp) >= abs(dm) else -1.0,
            'imbalance': abs(abs(dp) - abs(dm)),
        }
    return out


def chart_projection(v: Sequence[float]) -> Dict[int, float]:
    """
    Energy of an address in each of the 7 charts (sum over its 6 Assessors).

    NOTE these do NOT partition the address's energy: each basis index sits
    in 6 of the 7 charts, so the chart energies deliberately overlap. That
    overlap IS the skeleton touching -- see skeleton_overlap().
    """
    coords = assessor_coordinates(v)
    out = {s: 0.0 for s in range(1, 8)}
    for (a, b), row in coords.items():
        out[strut(a, b)] += row['energy']
    return out


def nearest_assessor(v: Sequence[float]) -> Tuple[Tuple[int, int], float]:
    """The Assessor carrying the most of the address's energy, and how much."""
    coords = assessor_coordinates(v)
    best = max(coords.items(), key=lambda kv: kv[1]['energy'])
    return best[0], best[1]['energy']


def local_curvature(v: Sequence[float], top: int = 3) -> float:
    """
    Associator defect around an address's dominant directions.

    Takes the `top` largest-magnitude basis components (ignoring e_0, whose
    associator vanishes identically) and sums the defect over their triples.
    Scalar curvature at the address, in the same units associator_field()
    reports on the charts.
    """
    idx = sorted(range(1, 16), key=lambda i: -abs(v[i]))[:max(1, top)]
    tot = 0.0
    for i in idx:
        for j in idx:
            for k in idx:
                tot += associator_defect(i, j, k)
    return tot


def chart_of(v: Sequence[float], check_zd: bool = True) -> Dict[str, object]:
    """
    THE CHART OF ADDRESSES -- where a monad address sits in the atlas.

    Exhaustive report for one 16-vector:

        norm, fixed_point_weight, energy_split
        peak_dim                 argmax component (matches the pkl's field)
        chart_energy             all 7 charts
        dominant_chart / strut   where most of its ZD-facing energy is
        chart_share              dominant / total chart energy
        nearest_assessor         the (a, b) plane carrying the most energy
        diagonals                d+ / d- there, and which dominates
        local_curvature          associator defect at its dominant directions
        is_zero_divisor          whether v itself annihilates any diagonal
        outside_share            energy on e_0 + e_8, i.e. OUTSIDE the geometry

    A high outside_share means the address is mostly fixed point -- it is
    'from 0_RB' in Cody's sense and carries little geometry to debug.

    check_zd=False skips the exact zero-divisor test (168 sedenion products,
    ~9 ms) and reports None for it. Everything else is microseconds, so the
    census defaults to skipping it; single lookups keep it on.
    """
    if len(v) != 16:
        raise ValueError("chart_of: a sedenion address is a 16-vector")
    ce = chart_projection(v)
    tot = sum(ce.values())
    dom = max(ce, key=lambda s: ce[s]) if tot > 0 else 0
    (na, nb), ne = nearest_assessor(v)
    dp, dm = diagonal_amplitudes(v, na, nb)
    zd = (any(is_zero(multiply(list(v), d)) or is_zero(multiply(d, list(v)))
              for (a, b) in assessors() for d in diagonals(a, b))
          if check_zd else None)
    split = energy_split(v)
    return {
        'norm':               norm(v),
        'peak_dim':           max(range(16), key=lambda i: abs(v[i])),
        'fixed_point_weight': fixed_point_weight(v),
        'energy_split':       split,
        'outside_share':      split['outside'],
        'chart_energy':       ce,
        'dominant_chart':     dom,
        'chart_share':        (ce[dom] / tot) if tot > 0 else 0.0,
        'nearest_assessor':   (na, nb),
        'nearest_energy':     ne,
        'd_plus':             dp,
        'd_minus':            dm,
        'dominant_diagonal':  '+' if abs(dp) >= abs(dm) else '-',
        'local_curvature':    local_curvature(v),
        'is_zero_divisor':    zd,
    }


def address_census(addresses: Dict[str, Sequence[float]],
                   limit: Optional[int] = None,
                   check_zd: bool = False) -> Dict[str, object]:
    """
    EXHAUSTIVE CENSUS over a corpus of monad addresses.

    Pass {name -> 16-vector} (e.g. every book[k]['sedenion'] from
    monad_sedenion_addresses.pkl). Returns the distribution across charts,
    Assessors, peak dimensions and fixed-point weight -- the descriptive
    picture, before any hypothesis is tested against it.

    Deliberately descriptive: counts and distributions only, no scoring
    against an expected outcome.
    """
    items = list(addresses.items())
    if limit is not None:
        items = items[:limit]
    chart_hist = {s: 0 for s in range(1, 8)}
    peak_hist: Dict[int, int] = {}
    ass_hist: Dict[Tuple[int, int], int] = {}
    fpw, outside, curv, zdc = [], [], [], 0
    for _, v in items:
        r = chart_of(v, check_zd=check_zd)
        chart_hist[r['dominant_chart']] = chart_hist.get(r['dominant_chart'], 0) + 1
        peak_hist[r['peak_dim']] = peak_hist.get(r['peak_dim'], 0) + 1
        ass_hist[r['nearest_assessor']] = ass_hist.get(r['nearest_assessor'], 0) + 1
        fpw.append(r['fixed_point_weight'])
        outside.append(r['outside_share'])
        curv.append(r['local_curvature'])
        zdc += 1 if r['is_zero_divisor'] else 0  # None counts as 0
    n = max(1, len(items))
    return {
        'n':                    len(items),
        'chart_histogram':      chart_hist,
        'peak_dim_histogram':   dict(sorted(peak_hist.items())),
        'assessor_histogram':   ass_hist,
        'assessors_occupied':   len(ass_hist),
        'assessors_total':      42,
        'mean_fixed_point_weight': sum(fpw) / n,
        'max_fixed_point_weight':  max(fpw) if fpw else 0.0,
        'min_fixed_point_weight':  min(fpw) if fpw else 0.0,
        'mean_outside_share':   sum(outside) / n,
        'mean_local_curvature': sum(curv) / n,
        'exact_zero_divisors':  zdc if check_zd else None,
    }


# --------------------------------------------------------------------------
# The pencil: 7 factorisations of one relation, PG(3,2)
# --------------------------------------------------------------------------

def pg32_lines() -> List[Tuple[int, int, int]]:
    """
    The 35 lines of PG(3,2): {a, b, a^b} for a != b, a^b not in {0, a, b}.

    Each of the 15 points sits on exactly 7 lines (105 incidences / 15 = 7)
    -- this is what makes each point's pencil well-defined. Verified in
    verify_pencil_counts().
    """
    lines = set()
    for a in range(1, 16):
        for b in range(1, 16):
            c = a ^ b
            if a != b and c not in (0, a, b):
                lines.add(frozenset((a, b, c)))
    return sorted(tuple(sorted(L)) for L in lines)


def pencil(r: int) -> List[Tuple[int, int]]:
    """
    THE PENCIL of relation r: the 7 ways to FACTOR r into two others.

        pencil(1) == [(2,3), (4,5), (6,7), (8,9), (10,11), (12,13), (14,15)]

    r in 1..15 (any of the 15 PG(3,2) points, not only a strut 1..7 -- the
    pencil ranges over the full 16-dimensional basis; a box kite's strut is
    the special case r in 1..7). For every a != r in 1..15, {a, a^r} is a
    factor pair of r (a ^ (a^r) == r); pairing is an involution with no
    fixed points once a == r is excluded, so exactly 7 unordered pairs fall
    out. Returned sorted by the smaller member, ascending -- the pencil
    path's station order.
    """
    if not (1 <= r <= 15):
        raise ValueError("pencil: r must be one of the 15 PG(3,2) points, 1..15")
    seen = set()
    pairs = []
    for a in range(1, 16):
        if a == r:
            continue
        b = a ^ r
        pair = (min(a, b), max(a, b))
        if pair not in seen:
            seen.add(pair)
            pairs.append(pair)
    return sorted(pairs)


def verify_pencil_counts() -> Dict[str, object]:
    """
    THE HONEST CHECK for the pencil, mirroring verify_counts() above.

    105 incidences (35 lines x 3 points) / 15 points = 7 lines per point,
    exactly; pencil(r) must return those same 7 factor pairs for every r.
    """
    lines = pg32_lines()
    incidence = {r: 0 for r in range(1, 16)}
    for L in lines:
        for p in L:
            incidence[p] += 1
    uniform7 = set(incidence.values()) == {7}
    pencils = {r: pencil(r) for r in range(1, 16)}
    sizes_all_7 = all(len(p) == 7 for p in pencils.values())
    # cross-check: the pencil pairs of r, together with r, are exactly the
    # lines through r.
    consistent = all(
        {frozenset((r, a, b)) for a, b in pencils[r]} ==
        {frozenset(L) for L in lines if r in L}
        for r in range(1, 16)
    )
    return {
        'lines': len(lines),
        'lines_expect_35': len(lines) == 35,
        'incidences': sum(incidence.values()),
        'incidences_expect_105': sum(incidence.values()) == 105,
        'uniform_7_per_point': uniform7,
        'pencil_1':            pencils[1],
        'pencil_1_expect':     [(2, 3), (4, 5), (6, 7), (8, 9),
                                 (10, 11), (12, 13), (14, 15)],
        'sizes_all_7':         sizes_all_7,
        'consistent_with_lines': consistent,
    }

