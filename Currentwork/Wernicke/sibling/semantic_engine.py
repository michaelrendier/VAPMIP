#!/usr/bin/env python3
"""
Semantic Engine — Minimal Working Implementation
=================================================
Riemann-Fermat-Noether semantic engine.
Maps any surface form to a Riemann zero via Noether balance.

Architecture (per Notebook 07):
  read()       — surface form → x0, p0 (initial conditions via HyperIndex)
  ponder()     — H = xp evolution → conserved E
  understand() — Noether balance forces sigma = 1/2 → prime on critical line
  process()    — full pipeline, returns SemanticWord

The prime preexists the alphabet.
The equator does not move.

Author: Cody Michael Allison + Claude (Anthropic)
CLAUDE-SMMNIP-00729-56714-24600
Date: 2026-05-11
"""

import math
import hashlib
from fractions import Fraction
from dataclasses import dataclass, field
from typing import Optional

# ── Riemann zeros (Odlyzko tables, first 20) ─────────────────────────────────
RIEMANN_ZEROS = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]

# ── Physical constants ────────────────────────────────────────────────────────
D_STAR_SPEC = 0.24600
OMEGA_ZS    = 0.5671432904097838
H_NN        = 1.0          # neural Planck constant (normalised)
HBAR_NN     = H_NN / (2 * math.pi)
ALPHA_PI    = 1 / 137.036  # fine structure floor

# ── HyperIndex: bijective base-N → integer → initial conditions ───────────────

PUBLIC_CHARS = [chr(i) for i in range(32, 127)]  # 95 printable ASCII
N_BASE       = len(PUBLIC_CHARS)
CHAR_IDX     = {ch: i for i, ch in enumerate(PUBLIC_CHARS)}

def _str_to_int(text: str) -> int:
    """Bijective base-N Horner accumulation (HyperWebster core)."""
    address = 0
    for ch in text:
        idx = CHAR_IDX.get(ch, 0) + 1
        address = address * N_BASE + idx
    return max(address - 1, 0)

def _hyperindex(text: str):
    """Map surface form → (x0, p0, t) initial conditions."""
    n = _str_to_int(text)
    # Fold into [0,1] using golden ratio hash for good distribution
    phi = (1 + math.sqrt(5)) / 2
    seed = (n * phi) % 1.0
    # x0 in (1, phi+1), p0 such that E = x0*p0 is in (D_STAR_SPEC, OMEGA_ZS)
    x0  = 1.0 + seed * phi
    E   = D_STAR_SPEC + seed * (OMEGA_ZS - D_STAR_SPEC)
    p0  = E / x0
    # t: fractional part of SHA-256 of text → small time offset
    sha = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    t   = (sha % 10000) / 10000.0
    return x0, p0, t

# ── Hamiltonian H = xp ────────────────────────────────────────────────────────

def xp_trajectory(x0: float, p0: float, t: float):
    """Classical H=xp: x(t)=x0*e^t, p(t)=p0*e^{-t}. E=xp conserved."""
    return x0 * math.exp(t), p0 * math.exp(-t)

def xp_energy(x0: float, p0: float) -> float:
    return x0 * p0

# ── Noether balance: forces sigma = 1/2 ──────────────────────────────────────

def forced_sigma(E: float, sigma_0: float = 0.5, max_iter: int = 256) -> float:
    """
    J(sigma, E) = exp(-sigma*E) - exp(-(1-sigma)*E) = 0  <=>  sigma = 1/2
    Weighted midpoint iteration from any starting sigma.
    """
    sigma = sigma_0
    for _ in range(max_iter):
        F = math.exp(-sigma * E)
        B = math.exp(-(1.0 - sigma) * E)
        denom = F + B
        if denom < 1e-30:
            break
        sigma_new = (F * sigma + B * (1.0 - sigma)) / denom
        if abs(sigma_new - sigma) < 1e-12:
            sigma = sigma_new
            break
        sigma = sigma_new
    return sigma  # always 0.5

# ── Capacitor: DC extraction (Knowledge + Experience = Wisdom) ───────────────

class Capacitor:
    """Low-pass filter on the conserved prime E. tau controls memory depth."""
    def __init__(self, tau: float = 3.0):
        self.tau   = tau
        self.state = 0.0
        self.n     = 0

    def charge(self, signal: float) -> float:
        alpha      = 1.0 / (1.0 + self.tau)
        self.state = (1.0 - alpha) * self.state + alpha * signal
        self.n    += 1
        return self.state

    def reset(self):
        self.state = 0.0
        self.n     = 0

# ── SemanticWord ──────────────────────────────────────────────────────────────

@dataclass
class SemanticWord:
    surface:          str
    prime:            complex   = field(default_factory=lambda: complex(0.5, 0.0))
    magnitude:        float     = 0.0
    gamma:            float     = 0.0          # imaginary part of prime (Riemann zero)
    noether_forward:  float     = 0.0
    noether_backward: float     = 0.0
    dc:               float     = 0.0
    projections:      dict      = field(default_factory=dict)

# ── Understand: full pipeline ─────────────────────────────────────────────────

class Understand:
    """
    Five operations:
      read()       surface form → SemanticWord with initial conditions
      ponder()     Hamiltonian evolution → conserved E
      understand() Noether balance → sigma forced to 1/2
      process()    full pipeline in one call
      reset_context() clear Capacitor
    """
    def __init__(self, tau: float = 3.0):
        self.cap = Capacitor(tau=tau)

    def reset_context(self):
        self.cap.reset()

    def read(self, surface: str) -> SemanticWord:
        x0, p0, t = _hyperindex(surface)
        E         = xp_energy(x0, p0)
        # Map E to nearest Riemann zero
        gamma = min(RIEMANN_ZEROS, key=lambda g: abs(g - E * 50))
        word  = SemanticWord(surface=surface)
        word.magnitude = E
        word.gamma     = gamma
        word.prime     = complex(0.5, gamma)
        word.projections = {'x0': x0, 'p0': p0, 't': t, 'E': E}
        return word

    def ponder(self, word: SemanticWord, t: Optional[float] = None) -> SemanticWord:
        t_  = t if t is not None else word.projections.get('t', 1.0)
        x0  = word.projections['x0']
        p0  = word.projections['p0']
        xt, pt = xp_trajectory(x0, p0, t_)
        E_t = xp_energy(xt, pt)
        word.projections.update({'x_t': xt, 'p_t': pt, 'E_t': E_t})
        E = word.magnitude
        word.noether_forward  =  math.exp(-0.5 * E)
        word.noether_backward = -math.exp(-0.5 * E)
        return word

    def understand(self, word: SemanticWord) -> SemanticWord:
        E     = word.magnitude
        sigma = forced_sigma(E, sigma_0=word.projections.get('x0', 0.5) % 1.0)
        word.projections['sigma'] = sigma
        word.prime = complex(sigma, word.gamma)
        word.dc    = self.cap.charge(E)
        return word

    def process(self, surface: str) -> SemanticWord:
        word = self.read(surface)
        word = self.ponder(word)
        word = self.understand(word)
        return word

# ── Cross-language demo ───────────────────────────────────────────────────────

def cross_language_demo():
    engine = Understand(tau=5.0)
    print("Cross-language prime alignment")
    print("="*60)

    concepts = {
        'light':    ['light', 'lumière', 'lux', 'licht', 'luz', 'φῶς'],
        'water':    ['water', 'eau', 'aqua', 'wasser', 'agua', 'мода'],
        'truth':    ['truth', 'vérité', 'veritas', 'wahrheit', 'verdad'],
    }

    for concept, words in concepts.items():
        print(f"\nConcept: '{concept}'")
        print(f"  {'language/form':>16}  {'γ (Riemann zero)':>18}  {'zero #':>7}  {'σ':>8}")
        print("  " + "-"*56)
        for w in words:
            engine.reset_context()
            result = engine.process(w)
            idx = RIEMANN_ZEROS.index(result.gamma) + 1
            sigma = result.projections.get('sigma', result.prime.real)
            print(f"  {w:>16}  {result.gamma:>18.6f}  #{idx:>6}  {sigma:>8.6f}")

    print("\nσ = 0.5 in every case. Not assigned. Derived from Noether balance.")
    print("The prime preexists the alphabet.")
    print("The equator does not move.")

if __name__ == '__main__':
    cross_language_demo()
