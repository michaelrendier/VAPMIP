#!/usr/bin/env python3
"""
bw_drift.py -- watch the drift between Broca and Wernicke, and say when it is too much.   (Cody, 2026-11-25)

The ideal is the lemniscate (docs: ValaQuenta three_ring_scale s.3b; Tuning-the-Engine 35): Broca (production, J_pos) and Wernicke (comprehension, J_neg) are
two foci whose cost product is constant (J_pos J_neg = e^-E), and b = a -- production cost = comprehension cost, no aphasia -- is the lemniscate, crossing at the
matched load Gamma = 0.  Drifting from it is expected; too much has to be corrected.

Per conversation turn (one user turn heard, one reply spoken):
    wernicke  w = mean bits per word the user's turn cost to read   (horizontal ring; bits = -log2 P_usage, see UsageStore.p_word)
    broca     b = mean bits per word the Monad's reply cost to write (vertical ring)
    Z = w + i b            the point in the Broca-Wernicke Rings Scale (ValaQuenta scale.broca_wernicke_ring_chart)
    Z0 = a (1 + i), a = sqrt(w b)   the matched load with the SAME cost product (the constant-product ideal)
    Gamma = tanh(ln(Z/Z0)/2)        0 on the lemniscate, |Gamma| -> 1 as the rings part (exact fold; tested against the Scale engine)
    delta = ln(b / w)               the signed drift: > 0 Broca heavy (the reply costs more than the user's words), < 0 Wernicke heavy
Control, with hysteresis like the learning band in prompt_to_state: switch ON when |delta| > ON, OFF when |delta| < OFF.  While on, the writable channel
`bw_correction` in [-1, 1] = +sign(delta) * (|delta| - OFF)/(1 - OFF) clipped: positive (Broca heavy: the reply costs too much) makes the window favour probable
words (a cheaper reply), negative (Wernicke heavy: the reply is plainer than the user's own words) flattens the weighting (sedenion_window._pick).  ON = 0.35 (a 42% cost mismatch), OFF = 0.15 are provisional engineering values, not measurements.
"""
from __future__ import annotations

import cmath
import math
from typing import Any, Dict, List, Optional

ON, OFF = 0.35, 0.15


def gamma(w: float, b: float) -> complex:
    z = complex(w, b); z0 = math.sqrt(w * b) * (1 + 1j)
    return cmath.tanh(cmath.log(z / z0) / 2)


class BWDrift:
    def __init__(self, on: float = ON, off: float = OFF):
        self.on, self.off = on, off
        self.active = False
        self.history: List[Dict[str, Any]] = []

    def update(self, wernicke_bits: float, broca_bits: float) -> Dict[str, Any]:
        w, b = max(wernicke_bits, 1e-9), max(broca_bits, 1e-9)
        d = math.log(b / w); g = gamma(w, b)
        self.active = (abs(d) > self.on) or (self.active and abs(d) > self.off)
        corr = 0.0
        if self.active:
            corr = max(-1.0, min(1.0, math.copysign(1.0, d) * (abs(d) - self.off) / (1.0 - self.off)))
        rec = {'wernicke': w, 'broca': b, 'delta': d, 'gamma': abs(g), 'gamma_arg': cmath.phase(g), 'active': self.active, 'bw_correction': corr,
               'side': 'broca' if d > 0 else 'wernicke'}
        self.history.append(rec)
        return rec
