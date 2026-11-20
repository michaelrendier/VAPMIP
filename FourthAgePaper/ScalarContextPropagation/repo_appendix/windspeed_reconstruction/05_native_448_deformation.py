import sys, os, cmath
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import numpy as np
import maths as bk

N = 16
def e(k):
    v = [0.0]*N; v[k] = 1.0; return v

def L_of(a):
    """16x16 real matrix of left-multiplication by sedenion a."""
    M = np.zeros((N, N))
    for j in range(N):
        col = bk.multiply(a, e(j))
        M[:, j] = col
    return M

def block_counts(eigs, tol=1e-6):
    zero = sum(1 for l in eigs if abs(l) < tol)
    one  = sum(1 for l in eigs if abs(abs(l) - 1.0) < 1e-3)
    root2= sum(1 for l in eigs if abs(abs(l) - 2**0.5) < 1e-3)
    other= len(eigs) - zero - one - root2
    return zero, one, root2, other

# the real zero divisor from Null-Space-of-the-Zero-Divisor.md
a0 = [0.0]*N
a0[1] = 1/2**0.5; a0[10] = 1/2**0.5     # a = (e1 + e10)/sqrt(2), strut 1^2=3

M0 = L_of(a0)
eig0 = np.linalg.eigvals(M0)
print("baseline a0 = (e1+e10)/sqrt(2), strut 3:")
print("  eig magnitudes:", sorted(round(abs(x), 4) for x in eig0))
print("  {4:8:4} block counts (zero, |1|, |sqrt2|, other):", block_counts(eig0))

# windspeed_B for "tree" = -0.151155, native rotation within a's own ZD-partner plane
# partner direction from the same doc: b0 = (e4 - e15)/sqrt(2), a real null-space partner of a0
b0 = [0.0]*N
b0[4] = 1/2**0.5; b0[15] = -1/2**0.5

wB = -0.151155
wA = 0.342035

def rotate(a, b, w):
    """Native rotation in the (a,b) plane by angle w -- radial-complex, not Cartesian
    translation. Stays unit-norm by construction (cos^2+sin^2=1)."""
    import math
    v = [math.cos(w)*a[i] + math.sin(w)*b[i] for i in range(N)]
    return v

for name, w in [("windspeed_B (tree, gamma_radial)", wB), ("windspeed_A (tree, basin drift)", wA)]:
    a_w = rotate(a0, b0, w)
    Mw = L_of(a_w)
    eigw = np.linalg.eigvals(Mw)
    detw = np.linalg.det(Mw)
    print(f"\n{name} = {w:+.6f}:")
    print("  is a(w) still unit norm:", round(sum(x*x for x in a_w), 6))
    print("  det(L_a(w)) (0 = still a zero divisor):", round(detw.real if hasattr(detw,'real') else detw, 6))
    print("  eig magnitudes:", sorted(round(abs(x), 4) for x in eigw))
    print("  {4:8:4} block counts (zero, |1|, |sqrt2|, other):", block_counts(eigw))

print("\n=== sanity check: rotate toward an UNRELATED direction, not a's own null partner ===")
# e0 (the fixed anchor, in NO Assessor) -- a genuinely different kind of direction
c0 = e(0)
for name, w in [("toward e0, windspeed_B", wB), ("toward e0, windspeed_A", wA)]:
    a_w = rotate(a0, c0, w)
    Mw = L_of(a_w)
    eigw = np.linalg.eigvals(Mw)
    detw = np.linalg.det(Mw)
    print(f"\n{name} = {w:+.6f}:")
    print("  det(L_a(w)):", round(detw.real if hasattr(detw,'real') else detw, 6))
    print("  {4:8:4} block counts:", block_counts(eigw))
    print("  eig magnitudes:", sorted(round(abs(x), 4) for x in eigw))

# and toward a totally unrelated Assessor diagonal (different strut entirely)
print("\n=== rotate toward an Assessor on a DIFFERENT strut ===")
d0 = [0.0]*N
d0[2] = 1/2**0.5; d0[11] = 1/2**0.5   # (e2+e9... wait use a real assessor: (e2, e3+8=e11)? strut 2^3=1
for name, w in [("toward different-strut Assessor, windspeed_B", wB), ("...windspeed_A", wA)]:
    a_w = rotate(a0, d0, w)
    Mw = L_of(a_w)
    eigw = np.linalg.eigvals(Mw)
    detw = np.linalg.det(Mw)
    print(f"\n{name} = {w:+.6f}:")
    print("  det(L_a(w)):", round(detw.real if hasattr(detw,'real') else detw, 6))
    print("  {4:8:4} block counts:", block_counts(eigw))
