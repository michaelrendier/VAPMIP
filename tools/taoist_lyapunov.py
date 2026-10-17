#!/usr/bin/env python3
"""taoist_lyapunov.py — measure, don't assume: largest Lyapunov exponent (Benettin) of System3
for a list of damage cases.  The SHAPE of the epicycle is the measurement the monitor shows;
this is the cross-check, slow (about a minute per case), run on demand.

Measured 2026-10-17 (T=600 s, dt=0.01, renorm 1 s, 8 processes), /s:
    healthy, edge dents, matched shapes, rho mismatch ............ +0.009 .. +0.017  (regular baseline)
    seam soft, rate mismatch 2.4/0.4 on a healthy seam .......... +0.009            (regular)
    rate mismatch 2.4/0.4 + edge dent + seam k .5, c .01 ........ +0.147            (chaotic)
Chaos here needs three things together: strong rate mismatch, an edge dent, and a weakly
damped seam.  Every other case tried, including a very soft seam alone, stayed regular.
"""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taoist_physics as P  # noqa: E402

CASES = {
    'healthy':                        dict(),
    'rho .6':                         dict(rho_w=0.6),
    'edge yang .3':                   dict(delta_y=0.3),
    'matched edges .3/.3':            dict(delta_y=0.3, delta_w=0.3),
    'rate 2.4/.4 + edge, healthy seam': dict(delta_y=0.3, cmd_y=2.4, cmd_w=0.4),
    'rate 2.4/.4 + edge, seam k.5 c.01': dict(delta_y=0.3, cmd_y=2.4, cmd_w=0.4, k_g=0.5, c_g=0.01),
}


def _one(k):
    return k, P.lyapunov3(lambda: P.System3(**CASES[k]), T=600, dt=0.01, renorm=1.0, burn=30)


if __name__ == '__main__':
    with Pool(8) as pool:
        for k, lam in pool.map(_one, list(CASES)):
            print(f"{k:38s} lambda = {lam:+.4f} /s")
