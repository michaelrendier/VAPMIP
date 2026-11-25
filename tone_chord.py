#!/usr/bin/env python3
"""
tone_chord.py -- the seven neuromodulator tones, a tense tone and a conjugation tone, as one chord (dial-tone style).

Cody, 2026-11-21: "a waveform for each component neurotransmitter. That tone combined with a tone for tense and one for
conjugation. I use tone here analogous to dial-tone phones: multiple tones played at once leading to identification of the number
pressed."  DTMF: a key is a pair of frequencies (one from a row group, one from a column group) and a decoder identifies the key by
measuring those frequencies with Goertzel filters. Here:

    7 neuromodulator tones  DA 5HT NE OXT GLU GABA CB1: one frequency each; the AMPLITUDE is the level (0 = absent, 1 = full)
    tense                   one of 8, a DTMF pair: 4 row frequencies x 2 column frequencies
    conjugation             one of 8, a DTMF pair of its own
    Fs = 16000 Hz, N = 1600 samples (0.1 s); every frequency is a multiple of 10 Hz, so each tone falls exactly on a Goertzel bin
    and the others contribute nothing (no leakage): the chord is decoded exactly, and survives noise.

`Tone7` is the state vector (levels 0..1) with the effect of each axis on the sentence constructor (`knobs()`), and the retrograde
relaxation toward baseline that CB1 controls. The effects are the author's analogy table made operational (computational analogues
from the Gemini neurotransmitter pass of 2026-11-20, translated to the knobs this constructor really has); they are design, not result.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np

NEURO7 = ['DA', '5HT', 'NE', 'OXT', 'GLU', 'GABA', 'CB1']
_ALIAS = {'OT': 'OXT', 'eCB': 'CB1', 'OPI': 'CB1'}      # OPI: the Recipe Book's hub (mu-opioid) takes the CB1 slot's relaxation knob (2026-11-25; before, from_axis('OPI') was silently ignored)
FS, N = 16000, 1600
F_NEURO = {'DA': 350, '5HT': 440, 'NE': 560, 'OXT': 700, 'GLU': 880, 'GABA': 1100, 'CB1': 1380}
TENSE_ROWS, TENSE_COLS = [1800, 2000, 2250, 2500], [2800, 3100]
CONJ_ROWS, CONJ_COLS = [3400, 3600, 3800, 4000], [4300, 4600]
LEVELS = 6                                              # amplitude steps: level k/6
AMP = 0.3                                               # amplitude of a full-level tone


def _tone(f: float, amp: float) -> np.ndarray:
    return amp * np.sin(2 * math.pi * f * np.arange(N) / FS)


def goertzel(x: np.ndarray, f: float) -> float:
    """Amplitude of frequency f in x (exact for f a multiple of FS/N)."""
    k = round(f * N / FS)
    w = 2 * math.pi * k / N
    c = 2 * math.cos(w)
    s1 = s2 = 0.0
    for v in x:
        s0 = v + c * s1 - s2
        s2, s1 = s1, s0
    power = s1 * s1 + s2 * s2 - c * s1 * s2
    return 2 * math.sqrt(max(power, 0.0)) / N


def encode(levels: Dict[str, float], tense: int, conj: int) -> np.ndarray:
    """The chord for one word: neuromodulator levels (0..1), tense index 0..7, conjugation index 0..7."""
    x = np.zeros(N)
    for a, f in F_NEURO.items():
        lv = levels.get(a, 0.0)
        if lv > 0:
            x += _tone(f, AMP * lv)
    x += _tone(TENSE_ROWS[tense // 2], AMP) + _tone(TENSE_COLS[tense % 2], AMP)
    x += _tone(CONJ_ROWS[conj // 2], AMP) + _tone(CONJ_COLS[conj % 2], AMP)
    return x


def decode(x: np.ndarray) -> Dict[str, object]:
    """Identify the chord: levels quantised to 0..6 sixths, tense and conjugation by the strongest row and column tone."""
    lv = {a: round(goertzel(x, f) / AMP * LEVELS) / LEVELS for a, f in F_NEURO.items()}
    def pick(rows, cols):
        r = int(np.argmax([goertzel(x, f) for f in rows])); c = int(np.argmax([goertzel(x, f) for f in cols]))
        return 2 * r + c
    return {'levels': lv, 'tense': pick(TENSE_ROWS, TENSE_COLS), 'conj': pick(CONJ_ROWS, CONJ_COLS)}


@dataclass
class Tone7:
    levels: Dict[str, float] = field(default_factory=lambda: {a: 0.3 for a in NEURO7})
    baseline: Dict[str, float] = field(default_factory=lambda: {a: 0.3 for a in NEURO7})

    @classmethod
    def from_axis(cls, axis: str, level: float, base: float = 0.3) -> 'Tone7':
        axis = _ALIAS.get(axis, axis)
        t = cls(levels={a: base for a in NEURO7}, baseline={a: base for a in NEURO7})
        if axis in t.levels:
            t.levels[axis] = max(0.0, min(1.0, level))
        return t

    def q(self, a: str) -> float:
        return round(max(0.0, min(1.0, self.levels[a])) * LEVELS) / LEVELS

    def knobs(self) -> Dict[str, float]:
        """What each axis does to the sentence constructor (the window's picking step):
        DA   explore: pick the k-th ranked candidate, k = round(3*DA)            (Gemini: temperature / top-p, associative jump)
        5HT  coherence: weight on the word-to-word statistics, exponent 0.5+1.5*5HT   (low-pass on off-register jumps)
        NE   focus: pool shrinks, frames shorten                                   (attention sharpening, urgency, short horizon)
        OXT  alignment: boost for the user's own words, 1+3*OXT                    (empathy, cooperative tone)
        GLU  throughput: pool size and neighbourhood depth grow                    (compute allocation, reasoning density)
        GABA prune: drop candidates below a fraction of the best, lower echo cap   (noise suppression, loop suppression)
        CB1  recover: every level relaxes toward baseline after each word          (retrograde damping, stress recovery)"""
        qb = {a: round(self.baseline[a] * LEVELS) / LEVELS for a in NEURO7}
        x = {a: (self.q(a) - qb[a]) / (1.0 - qb[a]) if self.q(a) >= qb[a] else (self.q(a) - qb[a]) / max(qb[a], 1e-9)
             for a in NEURO7}                                   # deviation from baseline: -1 (absent) .. 0 (neutral) .. +1 (full)
        up = lambda a: max(0.0, x[a])
        return {'novelty_rank': int(round(3 * up('DA'))), 'coherence': 1.0 + 1.5 * x['5HT'] * (1 if x['5HT'] >= 0 else 0.5),
                'pool_size': int(max(3, min(60, round(12 * (1.0 + 1.5 * x['GLU']) * (1.0 - 0.6 * x['NE']))))),
                'hops': 2 if x['GLU'] > 0.3 else 1, 'user_boost': 1.0 + 3.0 * up('OXT'), 'prune_floor': 0.3 * up('GABA'),
                'short_frame': x['NE'] > 0.3, 'echo_cap': max(1, 5 - int(round(2 * up('GABA')))),
                'relax_rate': 0.1 + 0.4 * (self.q('CB1'))}

    def relax(self) -> None:
        r = self.knobs()['relax_rate']
        for a in NEURO7:
            self.levels[a] += (self.baseline[a] - self.levels[a]) * r
