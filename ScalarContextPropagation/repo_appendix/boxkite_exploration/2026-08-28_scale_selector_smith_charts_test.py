"""
TEST — "a scalar real value selects scale from 0_RB and spits out that family of
equations, because shadows grow across an orthogonal set of Smith charts"  (Cody, 2026-08-28)

Distilled to checkable claims on the sedenion (0_RB lives at dim 16):

 C1  A single real scalar s in {0,1,2,3,4} selects a bifurcation LEVEL:
       Resolution R = 2^s   (dim per block)
       Scale      S = 16/R  (number of blocks)
     CLAIM: S * R = 16 exactly at every s  (the conserved hyperbola = xp = E).

 C2  At each s, L_a (unit sedenion, regular rep) partitions into an S x S grid
     of R x R blocks. The S diagonal blocks are a FAMILY: copies of ONE
     equation, differing only by sign / conjugation.
     CLAIM: for a = e_1, every diagonal block at level s is +/- the same
     R x R operator.

 C3  The S diagonal blocks are mutually orthogonal (Frobenius <A_i,A_j>=0),
     i != j  -- "an orthogonal set" of charts, one per block.

 C4  Smith-chart placement. r = S/R ; Gamma(r) = (r-1)/(r+1)  (two-ring fold,
     Z0 = 1). CLAIM: the 5 levels map to 5 real points symmetric about 0, with
     the CENTER (Gamma = 0) at s = 2, i.e. S = R = 4 = the QUATERNION level.

 C5  J_N involution. r -> 1/r swaps level s <-> level 4-s, and Gamma(1/r) =
     -Gamma(r) (Smith chart antisymmetric under the swap). J_N o J_N = id.

 C6  "Shadows grow across." shadow count = S (independent projections). CLAIM:
     monotone in s -- maximal spread (16 one-D shadows) at s=0, none (1 block)
     at s=4.
"""
import sys, math, itertools
sys.path.insert(0, "/home/rendier/Projects/ThePlace")
from SedenionFactoralRelativity.engine import cd_mul, unit

DIM = 16

def L_matrix(a):
    """Regular representation: columns are a * e_c."""
    return [[cd_mul(a, unit(DIM, c))[row] for c in range(DIM)] for row in range(DIM)]

def block(M, S, R, bi, bj):
    """The (bi,bj) block, R x R, of an S x S grid on the 16x16 M."""
    return [[M[bi*R + r][bj*R + c] for c in range(R)] for r in range(R)]

def fro_inner(A, B):
    return sum(A[i][j]*B[i][j] for i in range(len(A)) for j in range(len(A)))

def mat_eq(A, B, tol=1e-9):
    return all(abs(A[i][j]-B[i][j]) < tol for i in range(len(A)) for j in range(len(A)))

def mat_neg(A):
    return [[-x for x in row] for row in A]

# ─────────────────────────────────────────────────────────────────────────
print("="*74)
print("SCALE SELECTOR  x  ORTHOGONAL SMITH CHARTS  —  sedenion / 0_RB (dim 16)")
print("="*74)

a = unit(DIM, 1)               # a = e_1
La = L_matrix(a)

rows = []
for s in range(5):
    R = 2**s
    S = DIM // R
    r = S / R
    gamma = (r - 1.0) / (r + 1.0)

    # C1 — conserved product
    c1 = (S * R == DIM)

    # C2 — the family: diagonal blocks all +/- one operator
    diag_blocks = [block(La, S, R, b, b) for b in range(S)]
    base = diag_blocks[0]
    fam = all(mat_eq(B, base) or mat_eq(B, mat_neg(base)) for B in diag_blocks)
    signs = [("+" if mat_eq(B, base) else ("-" if mat_eq(B, mat_neg(base)) else "?"))
             for B in diag_blocks]

    # C3 — mutual Frobenius orthogonality of the diagonal blocks
    offdiag_ips = [fro_inner(diag_blocks[i], diag_blocks[j])
                   for i in range(S) for j in range(i+1, S)]
    c3 = all(abs(v) < 1e-9 for v in offdiag_ips) if S > 1 else True

    # C6 — shadow count
    shadows = S

    rows.append(dict(s=s, R=R, S=S, r=r, gamma=gamma, c1=c1, family=fam,
                     signs="".join(signs), c3=c3, shadows=shadows,
                     block=base))

print(f"\n{'s':>2} {'R(res)':>7} {'S(scl)':>7} {'S*R':>5} {'r=S/R':>8} "
      f"{'Gamma':>8} {'family?':>8} {'orthog?':>8} {'shadows':>8}")
print("-"*74)
for x in rows:
    print(f"{x['s']:>2} {x['R']:>7} {x['S']:>7} {x['R']*x['S']:>5} "
          f"{x['r']:>8.4f} {x['gamma']:>8.4f} {str(x['family']):>8} "
          f"{str(x['c3']):>8} {x['shadows']:>8}")

# C1
c1_all = all(x['c1'] for x in rows)
print(f"\nC1  S*R = 16 at every level: {c1_all}   (the conserved hyperbola, = xp = E)")

# C2
c2_all = all(x['family'] for x in rows)
print(f"C2  diagonal blocks are one equation +/- sign, every level: {c2_all}")
for x in rows:
    tag = {0:'sign', 1:'complex i', 2:'quaternion', 3:'octonion', 4:'sedenion'}[x['s']]
    print(f"      s={x['s']}  {x['S']:>2} x ({x['R']}x{x['R']}) {tag:<11} signs: {x['signs']}")
print(f"      s=1 base block (should be the complex structure  [[0,-1],[1,0]]):")
print(f"        {rows[1]['block']}")

# C3
c3_all = all(x['c3'] for x in rows)
print(f"C3  the S diagonal blocks mutually Frobenius-orthogonal, every level: {c3_all}")

# C4
gammas = [x['gamma'] for x in rows]
center_at_s2 = abs(rows[2]['gamma']) < 1e-12 and rows[2]['R'] == rows[2]['S'] == 4
symmetric = all(abs(gammas[k] + gammas[4-k]) < 1e-12 for k in range(5))
print(f"C4  Smith center (Gamma=0) at s=2 = the quaternion level (R=S=4): {center_at_s2}")
print(f"    Gamma sequence symmetric about 0: {symmetric}   {[round(g,4) for g in gammas]}")

# C5
def JN(r): return 1.0 / r
swap_ok = all(abs(JN(rows[k]['r']) - rows[4-k]['r']) < 1e-12 for k in range(5))
anti_ok = all(abs(((JN(x['r'])-1)/(JN(x['r'])+1)) + x['gamma']) < 1e-12 for x in rows)
invol_ok = all(abs(JN(JN(x['r'])) - x['r']) < 1e-12 for x in rows)
print(f"C5  J_N: r->1/r swaps level s <-> 4-s: {swap_ok}")
print(f"    Gamma(1/r) = -Gamma(r) (chart antisymmetric): {anti_ok}")
print(f"    J_N o J_N = identity: {invol_ok}")

# C6
shadow_seq = [x['shadows'] for x in rows]
monotone = all(shadow_seq[i] > shadow_seq[i+1] for i in range(4))
print(f"C6  shadow count strictly decreasing in s: {monotone}   {shadow_seq}")
print(f"    max spread 16 one-D shadows at s=0; single block at s=4")

# cross-level orthogonality of the DOUBLING generator (the coupling that
# carries info between the two half-copies at each split)
print()
print("EXTRA  cross-level: the doubling coupling block at level s, and level s+1,")
print("       Frobenius inner product (0 => the successive splits are orthogonal):")
for s in range(4):
    R, S = 2**s, DIM // 2**s
    # off-diagonal (0,1) block at this level = the doubling coupling
    cpl_s  = block(La, S, R, 0, 1) if S >= 2 else None
    R2, S2 = 2**(s+1), DIM // 2**(s+1)
    cpl_s1 = block(La, S2, R2, 0, 1) if S2 >= 2 else None
    if cpl_s is None or cpl_s1 is None:
        continue
    # embed the smaller into the larger index frame for the inner product:
    # compare the coupling at level s to the (0,1) coupling at level s+1
    # restricted to the top-left R x R corner
    corner = [[cpl_s1[i][j] for j in range(R)] for i in range(R)]
    ip = fro_inner(cpl_s, corner)
    print(f"       s={s} -> s+1 : <coupling_s , coupling_(s+1)|_corner>_F = {ip:.6f}")

print()
print("="*74)
verdict = {
    "C1 S*R=16 conserved (=xp=E)":            c1_all,
    "C2 each level = one equation family":    c2_all,
    "C3 diagonal blocks mutually orthogonal": c3_all,
    "C4 Smith center = quaternion level":     center_at_s2 and symmetric,
    "C5 J_N swaps conjugate levels, antisym": swap_ok and anti_ok and invol_ok,
    "C6 shadows grow as s decreases":         monotone,
}
for k, v in verdict.items():
    print(f"  [{'PASS' if v else 'FAIL'}]  {k}")
print("="*74)
