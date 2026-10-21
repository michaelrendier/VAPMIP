#!/usr/bin/env python3
"""rc12_euler_circles.py — each prime's Euler factor on the critical line is an exact circle.  (Slot k ↔ the k-th of the first 16 primes, as in SedenionSpectralRelativity/README.)
f_p(t) = (1 − p^(−1/2 − it))^(−1).  w = p^(−1/2) e^(−it ln p) runs on a circle of radius a = p^(−1/2); 1/(1−w) is a Möbius image of that circle, so a circle with centre 1/(1−a²) and radius a/(1−a²).
Angular rate ln p per unit t; in UNS (decimal-log metric, ds = d log10 p) that is ln10 · log10 p.  Checked by direct fit."""
import json, math, os
import numpy as np
PR = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
HERE = os.path.dirname(os.path.abspath(__file__)); out = {}
t = np.linspace(0, 2 * math.pi / 1.0, 4000)
for k, p in enumerate(PR):
    a = p ** -0.5; tt = np.linspace(0, 2 * math.pi / math.log(p), 2000, endpoint=False)
    f = 1 / (1 - a * np.exp(-1j * tt * math.log(p)))
    c = 1 / (1 - a * a); r = a / (1 - a * a)
    out[k] = {"prime": p, "centre_predicted": c, "radius_predicted": r, "max_deviation_from_that_circle": float(np.max(np.abs(np.abs(f - c) - r))),
              "angular_rate_ln_p": math.log(p), "UNS_rate_ln10_times_log10_p": math.log(10) * math.log10(p), "period_in_t": 2 * math.pi / math.log(p)}
json.dump(out, open(os.path.join(HERE, "rc12_results.json"), "w"), indent=1)
print({k: (v["prime"], round(v["max_deviation_from_that_circle"], 15), round(v["radius_predicted"], 4)) for k, v in out.items()})
