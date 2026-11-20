# repo_appendix/windspeed_reconstruction/13_bracketing_and_firing_order.py
# Answers the question script 11 meant to ask: does the pencil-product tension law depend on HOW the seven stations are
# bracketed (132 ways) and in WHAT ORDER they fire (7! = 5040)?  Measured by the rank of the phase-dependence of H.
# Self-contained: needs ValaQuenta/modules/box_kite/maths.py only.  Run: python3 13_bracketing_and_firing_order.py   (about a minute)
import sys, os, math, random
import numpy as np
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

E = np.eye(16)
T = np.array([[bk.multiply(list(E[i]), list(E[j])) for j in range(16)] for i in range(16)])   # e_i e_j, built from the repo's own product
def mul(x, y): return np.einsum('i,j,ijk->k', x, y, T)

def trees(lo, hi):                                  # every full binary bracketing of factors lo..hi-1 (Catalan(6) = 132 for 7 factors)
    if hi - lo == 1: yield lo; return
    for mid in range(lo + 1, hi):
        for L in trees(lo, mid):
            for R in trees(mid, hi): yield (L, R)

def evaluate(tree, fs): return fs[tree] if isinstance(tree, int) else mul(evaluate(tree[0], fs), evaluate(tree[1], fs))
def station(a, b, phi): v = np.zeros(16); v[a] = math.cos(phi); v[b] = math.sin(phi); return v
def H(st, ph, tree, order): return evaluate(tree, [station(*st[k], ph[k]) for k in order])[0]

def analyse(r, tree, order=range(7), npts=8, rng=np.random.default_rng(5)):
    """rank of the gradient set of H over random phase vectors: 1 means H depends on ONE signed combination of the phases."""
    st = bk.pencil(r); G = []
    for _ in range(npts):
        ph = rng.uniform(0, math.pi / 2, 7); g = []
        for k in range(7):
            u, d = ph.copy(), ph.copy(); u[k] += 1e-6; d[k] -= 1e-6
            g.append((H(st, u, tree, order) - H(st, d, tree, order)) / 2e-6)
        G.append(g)
    sv = np.linalg.svd(np.array(G), compute_uv=False)
    return int(np.sum(sv > 1e-3 * sv[0])) if sv[0] > 1e-9 else 0

if __name__ == "__main__":
    TR = list(trees(0, 7)); left = ((((((0, 1), 2), 3), 4), 5), 6)
    print(f"{len(TR)} bracketings; pencils r = 1..8 are lines through a point of the plane (+e_8), r = 9..15 are the Assessor-plane pencils")
    for r in (1, 2, 4, 8, 9, 10, 12, 15):
        ranks = [analyse(r, t) for t in TR]
        print(f"pencil({r:2d}): one-phase law for {ranks.count(1):3d} of {len(TR)} bracketings; rank histogram {dict(sorted({k: ranks.count(k) for k in set(ranks)}.items()))}")
    random.seed(3)
    for r in (1, 9, 10):
        orders = [random.sample(range(7), 7) for _ in range(200)]
        n1 = sum(analyse(r, left, order=o, npts=8) == 1 for o in orders)
        print(f"pencil({r:2d}), left bracketing, 200 random firing orders: one-phase law for {n1:3d}")
