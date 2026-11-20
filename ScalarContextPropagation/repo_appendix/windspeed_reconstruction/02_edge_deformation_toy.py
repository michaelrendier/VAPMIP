import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

def torsion_sign(i, j):
    """Catalog sec.5: torsion_sign(i,j) = commutator(i,j)[i^j], canonically ±2."""
    c = bk.commutator(i, j)
    return c[i ^ j]

def weighted_laplacian(n, edges, weights):
    L = [[0.0]*n for _ in range(n)]
    for (i, j), w in zip(edges, weights):
        L[i][j] -= w; L[j][i] -= w
        L[i][i] += w; L[j][j] += w
    return L

def deformed_spectrum(strut, windspeed):
    g = bk.box_kite_graph(strut)
    V, E = g['vertices'], g['edges']
    weights = []
    for (i, j) in E:
        a, b = V[i]; c, d = V[j]
        tor = torsion_sign(a, c)          # local torsion between the two Assessors' 'a' indices
        w = 1.0 + windspeed * tor          # baseline edge weight 1, perturbed by wind*torsion
        weights.append(w)
    L = weighted_laplacian(len(V), E, weights)
    return sorted(bk.eigenvalues_symmetric(L)), weights

STRUT = 1
baseline = sorted(bk.chart_spectrum(STRUT))
wA, wB = 0.342035, -0.151155

specA, wtsA = deformed_spectrum(STRUT, wA)
specB, wtsB = deformed_spectrum(STRUT, wB)

def fmt(xs): return "[" + ", ".join(f"{x:+.4f}" for x in xs) + "]"

print(f"strut {STRUT}  baseline (uniform, w=0):        {fmt(baseline)}")
print(f"strut {STRUT}  windspeed_A={wA:+.4f} deformed:  {fmt(specA)}")
print(f"strut {STRUT}  windspeed_B={wB:+.4f} deformed:  {fmt(specB)}")
print()
print(f"edge weights under A: {[round(w,3) for w in wtsA]}")
print(f"edge weights under B: {[round(w,3) for w in wtsB]}")
print()
print("zero mode preserved (first eigval ~0) under A:", abs(specA[0]) < 1e-9)
print("zero mode preserved (first eigval ~0) under B:", abs(specB[0]) < 1e-9)
print("sum(eigs) baseline/A/B (trace, should all be 2*sum(weights)):",
      sum(baseline), sum(specA), sum(specB), "  2*sum(wtsA)=", 2*sum(wtsA), " 2*sum(wtsB)=", 2*sum(wtsB))

# Run the SAME two windspeeds across all 7 struts, same slot each time
print()
print("=== all 7 struts, same windspeeds, same slot (edge 0's torsion source) ===")
for s in range(1, 8):
    base = sorted(bk.chart_spectrum(s))
    sa, _ = deformed_spectrum(s, wA)
    sb, _ = deformed_spectrum(s, wB)
    same_AB = all(abs(x-y) < 1e-9 for x, y in zip(sa, sb))
    print(f"strut {s}: baseline={fmt(base)}  A={fmt(sa)}  B={fmt(sb)}  A==B: {same_AB}")
