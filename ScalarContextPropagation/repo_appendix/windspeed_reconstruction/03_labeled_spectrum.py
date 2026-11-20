import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import numpy as np
import maths as bk

def torsion_sign(i, j):
    c = bk.commutator(i, j)
    return c[i ^ j]

def weighted_L(strut, windspeed):
    g = bk.box_kite_graph(strut)
    V, E = g['vertices'], g['edges']
    L = np.zeros((6, 6))
    for (i, j) in E:
        a, b = V[i]; c, d = V[j]
        w = 1.0 + windspeed * torsion_sign(a, c)
        L[i, j] -= w; L[j, i] -= w
        L[i, i] += w; L[j, j] += w
    return L, V, E

def labeled_spectrum(strut, windspeed):
    L0, V, E = weighted_L(strut, 0.0)               # baseline, w=0
    ev0, evec0 = np.linalg.eigh(L0)
    labels = ['strut' if abs(v - 4) < 1e-6 else ('sail' if abs(v - 6) < 1e-6 else 'zero')
              for v in ev0]
    L, _, _ = weighted_L(strut, windspeed)
    # project the DEFORMED matrix onto the BASELINE eigenbasis to track each mode
    tracked = evec0.T @ L @ evec0
    tracked_diag = np.diag(tracked)                  # how each baseline mode's energy moved
    return ev0, labels, tracked_diag

wA, wB = 0.342035, -0.151155

print("=== which baseline modes are 'strut' vs 'sail', and how each moves under wind ===")
for strut in range(1, 8):
    ev0, labels, trA = labeled_spectrum(strut, wA)
    _, _,   trB = labeled_spectrum(strut, wB)
    print(f"\nstrut {strut}:")
    for lam, lab, ta, tb in zip(ev0, labels, trA, trB):
        moved_A = abs(ta - lam) > 1e-9
        moved_B = abs(tb - lam) > 1e-9
        print(f"  baseline={lam:+.4f} ({lab:5s})  under A: {ta:+.4f} {'moved' if moved_A else 'BLIND'}"
              f"   under B: {tb:+.4f} {'moved' if moved_B else 'BLIND'}")
