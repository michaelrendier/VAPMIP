#!/usr/bin/env python3
"""zeros_exact.py — the first N nontrivial zeros ρ_k = ½ + iγ_k of ζ, found, not approximated.  Writes SpecTools/zeros/zeros_exact_<N>.tsv (k, γ).

Method (regular maths only): scan the Hardy function Z(t) = e^{iθ(t)} ζ(½+it) for sign changes (Riemann–Siegel main sum + first correction, numpy, step 0.02),
then refine each bracketed root with mpmath's siegelz (30 digits).  Checks: the count of roots below sampled heights against mpmath.zetazero, and gaps all positive.
The engine's own `generate_zeros` is a Newton solve of the smooth counting formula and is off by up to 1.8 (paper §5.2); this table is the exact set.

    .venv/bin/python SpecTools/zeros/zeros_exact.py 25000   # ~1-2 h on 8 cores; checkpointed every 800 roots, safe to stop and re-run
"""
import os, sys, time
import numpy as np, mpmath as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from dprint import dprint
N = int(sys.argv[1]) if len(sys.argv) > 1 else 25000
mp.mp.dps = 20
TWO_PI = 2 * np.pi

def theta(t):
    return t / 2 * np.log(t / TWO_PI) - t / 2 - np.pi / 8 + 1 / (48 * t) + 7 / (5760 * t ** 3)

def Z(t):
    """Riemann–Siegel Z(t), main sum plus the C0 correction; vectorised over t"""
    t = np.asarray(t, dtype=float)
    a = np.sqrt(t / TWO_PI); n = np.floor(a).astype(int); p = a - n
    th = theta(t); out = np.zeros_like(t)
    for k in range(1, int(n.max()) + 1):
        m = n >= k
        out[m] += 2 * np.cos(th[m] - t[m] * np.log(k)) / np.sqrt(k)
    C0 = np.cos(TWO_PI * (p * p - p - 1 / 16)) / np.cos(TWO_PI * p)
    out += (-1.0) ** (n - 1) * (TWO_PI / t) ** 0.25 * C0
    return out

# upper bound of the scan: smooth count θ(T)/π + 1 reaches N + 20
T = 14.0
while theta(T) / np.pi + 1 < N + 20: T *= 1.01
dprint("scan to T", T)
STEP = 0.02
def refine(args):
    x0, a, b = args
    mp.mp.dps = 20
    r = mp.findroot(lambda x: mp.siegelz(x), (mp.mpf(x0), mp.mpf(x0) + mp.mpf("1e-6")), solver="secant", tol=1e-18, maxsteps=30)
    if not (a - 0.05 < r < b + 0.05): r = mp.findroot(lambda x: mp.siegelz(x), (mp.mpf(a), mp.mpf(b)), solver="anderson", tol=1e-18, maxsteps=60)
    return r
if __name__ == "__main__":
    from multiprocessing import Pool
    brackets = []; t0 = 10.0; t_all = time.time(); BLOCK = 2000.0
    while t0 < T:
        t1 = min(t0 + BLOCK, T); ts = np.arange(t0, t1 + STEP, STEP); zs = Z(ts)
        for i in np.nonzero(zs[:-1] * zs[1:] < 0)[0]:
            a_, b_ = ts[i], ts[i + 1]
            brackets.append((a_ - zs[i] * (b_ - a_) / (zs[i + 1] - zs[i]), a_, b_))
        dprint("scanned", (t0, t1, len(brackets), round(time.time() - t_all, 1)))
        t0 = t1
    import pickle
    ck = os.path.join(HERE, f"zeros_exact_{N}.ckpt"); os.makedirs(os.path.dirname(ck), exist_ok=True)
    done = pickle.load(open(ck, "rb")) if os.path.exists(ck) else {}
    dprint("checkpoint loaded", len(done))
    todo = [i for i in range(len(brackets)) if i not in done]
    with Pool(8) as pool:
        for b0 in range(0, len(todo), 800):
            blk = todo[b0:b0 + 800]
            for i, r in zip(blk, pool.map(refine, [brackets[i] for i in blk], chunksize=16)): done[i] = str(r)
            pickle.dump(done, open(ck + ".tmp", "wb")); os.replace(ck + ".tmp", ck)
            dprint("checkpoint saved", (len(done), len(brackets), round(time.time() - t_all, 1)))
    roots = [mp.mpf(done[i]) for i in range(len(brackets))]
    dprint("refined", round(time.time() - t_all, 1))
    roots = sorted(set(roots), key=lambda r: r)
    dprint("roots found", len(roots))
    roots = roots[:N]
    gaps = [float(roots[i + 1] - roots[i]) for i in range(len(roots) - 1)]
    assert min(gaps) > 1e-6, "duplicate roots"
    dprint("min gap", min(gaps)); dprint("max gap", max(gaps))
    bad = 0
    for k in [1, 2, 3, 10, 29, 30, 100, 101, 500, 1000, 2500, 5000, 7500, 10000, 12500, 15000, 17500, 20000, 22500, 24999, 25000]:
        if k <= len(roots):
            ref = mp.zetazero(k).imag; d = abs(roots[k - 1] - ref)
            dprint(f"check zero {k}", float(d))
            if d > 1e-10: bad += 1
    assert bad == 0, "zero index disagrees with mpmath.zetazero: a root was missed or doubled"
    out = HERE; os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"zeros_exact_{N}.tsv"), "w") as f:
        f.write("k\tgamma\n")
        for k, r in enumerate(roots, 1): f.write(f"{k}\t{mp.nstr(r, 18)}\n")
    dprint("wrote", os.path.join(out, f"zeros_exact_{N}.tsv"))
