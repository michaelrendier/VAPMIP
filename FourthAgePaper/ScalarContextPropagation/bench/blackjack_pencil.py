"""blackjack_pencil.py (2026-11-21): where the Blackjack group F21 sits in the Scalar Boxkite.
F21 = <multiplication by x, Frobenius a->a^2> acting on F8 = F2[x]/(x^3+x+1); its 7 nonzero points are the Fano points 1..7,
and it is extended to the 15 sedenion labels by keeping the shadow bit (label + 8). Checks: the group has order 21 and is linear
(preserves XOR) on all 15 labels; for every strut s in 1..7 the stabiliser of s (order 3) preserves pencil(s) and splits its 7
stations into orbits of size 1+3+3 (pivot, axes, shadows). Run from VAPMIP/ with ValaQuenta/.venv/bin/python (or any python
with ValaQuenta importable: sys.path gets the parent directory)."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from ValaQuenta.modules.box_kite import maths as M
def mul(a, b):
    r = 0
    for i in range(3):
        if (b >> i) & 1: r ^= a << i
    for i in (4, 3):
        if (r >> i) & 1: r ^= 0b1011 << (i - 3)
    return r
mulA = lambda x: mul(x, 2); frob = lambda x: mul(x, x)
def ext(f): return lambda x: (f(x & 7) | (x & 8)) if (x & 7) else x
gens = [tuple([0] + [ext(mulA)(p) for p in range(1, 16)]), tuple([0] + [ext(frob)(p) for p in range(1, 16)])]
G = {tuple(range(16))}; fr = list(G)
while fr:
    new = []
    for g in fr:
        for h in gens:
            c = tuple(g[h[i]] for i in range(16))
            if c not in G: G.add(c); new.append(c)
    fr = new
print('group order on 15 labels:', len(G))
print('linear on all 15 labels:', all(all(g[a ^ b] == g[a] ^ g[b] for a in range(1, 16) for b in range(1, 16) if a != b) for g in G))
for s in range(1, 8):
    pen = [tuple(sorted(p)) for p in M.pencil(s)]
    st = [g for g in G if g[s] == s]
    ok = all(sorted(tuple(sorted((g[a], g[b]))) for a, b in pen) == sorted(pen) for g in st)
    orbs = sorted({tuple(sorted({tuple(sorted((g[a], g[b]))) for g in st})) for a, b in pen}, key=len)
    print('strut', s, '|stab|', len(st), 'pencil preserved:', ok, 'orbit sizes on the 7 stations:', sorted(len(o) for o in orbs))
print('pencil(1):', M.pencil(1))
