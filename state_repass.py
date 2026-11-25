#!/usr/bin/env python3
"""
state_repass.py -- the USER-STATE half of the sedenion window's self-correcting repass.   (Cody's design, 2026-11-25)

The window (sedenion_window.py) always has 16 slots, even when only 9 words exist.  The user's state has 16 numbers too:

    e0        the anchor: how far the reading is from RECEPTIVE (the state in which information is taken in)
    e1..e7    the DARK pole of the seven axes, in kite order   OPI GLU GABA DA 5HT NE OXT   (OPI = e1 = the hub)
    e8        the cursor (net valence: mean light minus mean dark)
    e9..e15   the LIGHT pole of the same seven axes (slot j+8)

Why this labelling is not arbitrary (it is checked in tests/test_state_repass.py, from the box-kite code):
  * the dark and light pole of one axis are always XOR 8 apart: one edge label for all seven (the Cayley-Dickson doubling);
  * the three antagonist struts GLU|GABA, DA|5HT, NE|OXT sit at slots 2|3, 4|5, 6|7, so each strut pair is XOR 1 apart,
    and 1 is the hub's slot: in the Fano plane the three lines through the hub are exactly the three struts
    (the strut constant of box-kite 1 is a XOR b = 1; its six vertices are (2,3)(3,2)(4,5)(5,4)(6,7)(7,6)).

The repass, per user turn (`observe`):
  1. READ    the engine (prompt_to_state.PromptToState.turn) gives 14 pole concentrations and their SPREAD (the two meters'
             disagreement).  A pole whose deviation from baseline is no larger than its spread is HEALED to baseline: a reading inside
             the noise is not acted on.
  2. MIX     per axis: level = BASELINE + (light deviation - dark deviation)/9, clamped to 0..1.
  3. CANCEL  neuro_recipes.conjugate(mix, k): the noise-cancelling reply, RECEPTIVE - k (mix - RECEPTIVE), held when the user is inside
             the dead-band.  k is scaled by sqrt(filled/16): the fewer of the 16 window slots hold a word, the less evidence the
             correction rests on, so the smaller the correction (it cannot overshoot on thin context).
  4. LEAD    neuro_recipes.meet_then_lead: start at the user's mix, arrive at the target (Pascal: meet, then lead); per word the
             window turns the one axis farthest from RECEPTIVE and writes it as the invisible tone marker (axis, level 0..6).
Update = the next `observe` re-reads, re-gates and re-plans.  No model is loaded here: the engine is passed in (any object with
.turn(text) -> {'conc': 14, 'spread': 14}, optional .base (14) and .NT), so the machinery is testable without the meters.
Provisional: the clamp gain 1/9, the sqrt confidence law and the OPI -> CB1 tone alias are engineering choices, not measurements.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

import neuro_recipes as NR

AXES = NR.AXES                                              # ('OPI','GLU','GABA','DA','5HT','NE','OXT'): hub then the three struts
SLOT = {a: i + 1 for i, a in enumerate(AXES)}               # e1..e7
STRUTS = [('GLU', 'GABA'), ('DA', '5HT'), ('NE', 'OXT')]
HUB = AXES[0]
TONE_ALIAS = {'OPI': 'CB1'}                                 # tone_chord.Tone7 still has CB1 (its relax_rate knob), not OPI; the Recipe Book's hub takes that knob


def dark_slot(a: str) -> int:
    return SLOT[a]


def light_slot(a: str) -> int:
    return SLOT[a] + 8


class StateRepass:
    def __init__(self, engine, k: float = NR.K_CANCEL, band: float = NR.BAND):
        self.engine, self.k, self.band = engine, k, band
        self.nt = tuple(getattr(engine, 'NT', None) or AXES)
        assert self.nt == AXES, 'the engine must list its axes in kite order'
        self.reading: Optional[Dict[str, Any]] = None
        self.dev14 = np.zeros(14); self.healed = np.zeros(14, bool)
        self.mix: Dict[str, float] = dict(NR.BASELINE)
        self.target: Dict[str, float] = dict(NR.BASELINE)
        self.held = True; self.turns = 0

    # ---- 1-3: read, heal, mix, cancel -----------------------------------------------------------------
    def observe(self, text: str, fill: int = 16) -> Dict[str, Any]:
        """Read one user turn and re-plan.  `fill` = how many of the window's 16 slots hold a word (the evidence behind the correction)."""
        r = self.engine.turn(text); self.reading = r; self.turns += 1
        c = np.asarray(r['conc'], float); sp = np.asarray(r['spread'], float); base = np.asarray(getattr(self.engine, 'base', np.zeros(14)), float)
        dev = c - base; self.healed = np.abs(dev) <= sp; self.dev14 = np.where(self.healed, 0.0, dev)
        self.mix = {a: float(min(1.0, max(0.0, NR.BASELINE[a] + (self.dev14[2 * i + 1] - self.dev14[2 * i]) / 9.0))) for i, a in enumerate(AXES)}
        self.k_eff = self.k * math.sqrt(max(1, min(16, fill)) / 16.0)
        self.target = NR.conjugate(self.mix, self.k_eff, self.band)
        self.held = NR.dist(self.mix, NR.RECEPTIVE) < self.band
        return self.summary()

    # ---- the 16-vector (one number per sedenion slot; always 16, however many words exist) -------------
    def state16(self) -> List[float]:
        r = self.reading
        c = np.asarray(r['conc'], float) if r else np.zeros(14)
        v = [0.0] * 16
        v[0] = float(NR.dist(self.mix, NR.RECEPTIVE))                       # anchor: distance from RECEPTIVE
        for i, a in enumerate(AXES):
            v[dark_slot(a)] = float(c[2 * i]); v[light_slot(a)] = float(c[2 * i + 1])
        v[8] = float((c[1::2].mean() - c[0::2].mean()))                    # cursor: net valence
        return v

    def summary(self) -> Dict[str, Any]:
        return {'mix': {a: round(x, 2) for a, x in self.mix.items()}, 'target': dict(self.target), 'held': self.held, 'healed_poles': int(self.healed.sum()),
                'k_eff': round(self.k_eff, 3), 'axis': self.heard_tone()[0], 'move': (self.reading or {}).get('move')}

    # ---- 4: lead --------------------------------------------------------------------------------------
    def heard_tone(self) -> Tuple[str, int]:
        """(axis, level 0..6) of the axis farthest from RECEPTIVE: what the window 'hears' in place of the lexicon count."""
        a = max(AXES, key=lambda x: abs(self.mix[x] - NR.RECEPTIVE[x]))
        return (a, int(round(6 * self.mix[a])))

    def trajectory(self, n: int) -> List[Tuple[str, int]]:
        steps = NR.meet_then_lead(self.mix, self.target, max(1, n)); out = []
        for s in steps:
            a = max(AXES, key=lambda x: abs(s[x] - NR.RECEPTIVE[x])); out.append((TONE_ALIAS.get(a, a), int(round(6 * s[a]))))
        return out


class StatePersuader:
    """Drop-in for sedenion_window.Persuader: same attributes, trajectory(n) from the user-state repass."""

    def __init__(self, state: StateRepass, target: Tuple[str, int] = ('GABA', 3)):
        self.state, self.target = state, target
        a, l = state.heard_tone(); self.heard = (TONE_ALIAS.get(a, a), l)

    def trajectory(self, n: int) -> List[Tuple[str, int]]:
        return self.state.trajectory(n)
