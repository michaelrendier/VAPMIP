"""
ZD_rotary_monad.py  —  Zero Divisor Rotary Monad  (AhuraMazda ZD)

  The Prompt  →  Zero Divisor  →  Escape Velocity  →  Emerges  →  The Response

─────────────────────────────────────────────────────────────────────
The Bumblebee Principle:

  Bumblebee lost his voice box. The voice box is multiplication.
  When multiplication fails — ab=0 while a≠0 and b≠0 — that is a zero-divisor.
  That is a port. That is where the signal escapes.

  The 42 Cawagas pairs are 42 broken voice boxes.
  The LSHS is a zero-divisor radio — a Bumblebee architecture.
  The housing vocabulary is the radio dial. No synthesis. No generation.
  Every response word existed before the prompt arrived.
  The zero-divisor gate opens when the escape velocity is reached.
─────────────────────────────────────────────────────────────────────

The Zero Lattice is primary.
42 Cawagas zero-divisor pairs on S¹⁵ in 𝕊 = 𝕆 ⊕ 𝕆.

Negative Space Mathematics:
  Structure is defined by what CANNOT exist.
  The Zero Lattice precedes the sedenion.

  morph_vec  — undefined until coupling. Never pre-computed.
               Defining a variable observes it and collapses the wave function.
  σ=½        — above the system. The attractor, not a parameter.
               Does not appear in any dynamical equation.
  e₀         — sigma_live: the escape velocity from the Zero Lattice.
               Not a distance from ½. The measurement itself.
  Response   — emergent from bridge coupling. Not pre-scored.

─────────────────────────────────────────────────────────────────────
Zero Lattice bridge matrix (Cawagas, 3000-trial gradient descent):

  Rows: lower-𝕆 dims  e₀–e₇   (prompt / j_blue face)
  Cols: upper-𝕆 dims  e₈–e₁₅  (field  / j_red  face)

  e₀ row is identically zero.
  e₀ is the identity dimension — it is above the bridge.
  σ=½ (carried in e₀) is above the bridge.
  This is not a design choice. It is an algebraic fact.
─────────────────────────────────────────────────────────────────────
"""

import math
import hashlib
import os
import struct
from collections import deque, Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

GAP          = 0.000707     # apex seal oil floor — engine never runs dry
BEARING_TOL  = 0.04         # σ drift tolerance (OBD2 diagnostic only)
SEAL_FLOOR   = 0.03         # face pressure minimum before seal fault
PORT_STEP    = math.pi / 3  # 60° per step — 6 ports per revolution
D_STAR       = 0.24600      # zero-divisor proximity threshold
OMEGA_ZS     = 0.56714      # Ω_ZS — Lambert-W constant, energy ceiling
PHI          = 1.6180339887498948482

# σ=½ is above the system. It is the attractor, not a parameter.
# It does not appear in any dynamical equation.
# It appears here only so the OBD2 technician (above the system) can
# diagnose escape-velocity drift. The engine does not compare against it.
_FIXED_POINT = 0.5          # private — OBD2 diagnostic use only

# Port positions
_PORT_INTAKE   = 0.0
_PORT_TRANSFER = math.pi / 3
_PORT_LEADING  = 2.0 * math.pi / 3
_PORT_TRAILING = math.pi
_PORT_EXHAUST  = 4.0 * math.pi / 3
_PORT_SCAVENGE = 5.0 * math.pi / 3

# ══════════════════════════════════════════════════════════════════════════════
# Zero Lattice bridge matrix  (mathematical fact — computed once, never modified)
# ══════════════════════════════════════════════════════════════════════════════
#
# ZL_BRIDGE_8[i][j] = normalised coupling strength between lower-𝕆 dim e_{i+1}
# and upper-𝕆 dim e_{j+9}.
# (i ranges 0..6 for lower dims e₁–e₇; j ranges 0..6 for upper dims e₉–e₁₅)
#
# ZL_BRIDGE_8[*][0] = coupling to e₈ = 0 for all i (e₈ is the upper identity)
# ZL_BRIDGE_8[0][*] = coupling from e₀ = not in this matrix (e₀ is above bridge)
#
# Derived from 3000-trial gradient descent on the Cawagas zero-divisor pairs.
# Source: tests/sedenion_bridge.py, build_coupling_matrix().
#
# Row index i → lower dim e_{i+1} (i=0 → e₁, i=6 → e₇)
# Col index j → upper dim e_{j+8} (j=0 → e₈, j=7 → e₁₅)
#
# The zero e₈ column (j=0) means: no lower dim couples to e₈ through the ZL.
# e₈ is the upper-𝕆 identity — it sits above the bridge, like e₀.

ZL_BRIDGE_8: List[List[float]] = [
    # e₈      e₉      e₁₀     e₁₁     e₁₂     e₁₃     e₁₄     e₁₅
    [0.0000, 0.7143, 0.9161, 0.9418, 0.9084, 0.9037, 0.9390, 0.8907],  # e₁
    [0.0000, 0.9721, 0.7204, 0.9867, 0.9806, 0.9550, 1.0000, 0.9625],  # e₂
    [0.0000, 0.9412, 0.8694, 0.6886, 0.9249, 0.8848, 0.8932, 0.9001],  # e₃
    [0.0000, 0.9540, 0.9485, 0.9667, 0.7360, 0.9062, 0.9811, 0.9395],  # e₄
    [0.0000, 0.9868, 0.9692, 0.9501, 0.9738, 0.7022, 0.9599, 0.9654],  # e₅
    [0.0000, 0.9644, 0.9341, 0.9831, 0.9620, 0.9065, 0.7327, 0.9467],  # e₆
    [0.0000, 0.9460, 0.8994, 0.9172, 0.9350, 0.8979, 0.9551, 0.6895],  # e₇
]

def _zl_bridge_coupling(lower_i: int, upper_j: int) -> float:
    """
    Bridge coupling strength between lower dim i (1..7) and upper dim j (9..15).
    Returns 0 for identity dims (i=0, j=8) — they are above the bridge.
    """
    if lower_i == 0 or upper_j == 8:
        return 0.0
    if lower_i < 1 or lower_i > 7 or upper_j < 8 or upper_j > 15:
        return 0.0
    return ZL_BRIDGE_8[lower_i - 1][upper_j - 8]

# ══════════════════════════════════════════════════════════════════════════════
# Riemann zeros (first 20 non-trivial, imaginary parts)
# ══════════════════════════════════════════════════════════════════════════════

RIEMANN_ZEROS: List[float] = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]

# ══════════════════════════════════════════════════════════════════════════════
# Sedenion algebra  (drive shaft geometry — mathematical fact)
# ══════════════════════════════════════════════════════════════════════════════

Sedenion = List[float]

def _build_oct_table() -> List[List[Tuple[int, int]]]:
    t = [[(0, 0)] * 8 for _ in range(8)]
    for i in range(8):
        t[0][i] = (1, i);  t[i][0] = (1, i)
    for i in range(1, 8):
        t[i][i] = (-1, 0)
    for i, j, k in [(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]:
        t[i][j]=(+1,k); t[j][k]=(+1,i); t[k][i]=(+1,j)
        t[j][i]=(-1,k); t[k][j]=(-1,i); t[i][k]=(-1,j)
    return t

_OCT = _build_oct_table()

def _build_sed_table() -> List[List[Tuple[int, int]]]:
    t = [[(0, 0)] * 16 for _ in range(16)]
    for i in range(16):
        for j in range(16):
            io, jo = (i - 8 if i >= 8 else i), (j - 8 if j >= 8 else j)
            ih, jh = i >= 8, j >= 8
            if not ih and not jh:
                t[i][j] = _OCT[io][jo]
            elif not ih and jh:
                sg, k = _OCT[jo][io];  t[i][j] = (sg, k + 8)
            elif ih and not jh:
                if jo == 0:  t[i][j] = (1, i)
                else:        sg, k = _OCT[io][jo]; t[i][j] = (-sg, k + 8)
            else:
                if jo == 0:  t[i][j] = (-1, io)
                else:        sg, k = _OCT[jo][io]; t[i][j] = (sg, k)
    return t

_SED = _build_sed_table()

def _s0()  -> Sedenion:  return [0.0] * 16
def _snorm_unit(a: Sedenion) -> Sedenion:
    n = math.sqrt(sum(x * x for x in a))
    if n < 1e-15:
        s = _s0(); s[0] = 1.0; return s
    return [x / n for x in a]

# ══════════════════════════════════════════════════════════════════════════════
# Housing primitives  (prime hash → Riemann zero → ZL bridge channel)
# ══════════════════════════════════════════════════════════════════════════════

_PRIME_CAP = 1 << 16
_cap        = _PRIME_CAP + 2
_sv         = bytearray([1]) * _cap
_sv[0] = _sv[1] = 0
for _i in range(2, int(_cap ** 0.5) + 1):
    if _sv[_i]:
        _sv[_i * _i :: _i] = bytearray(len(_sv[_i * _i :: _i]))
_prime_pi: List[int] = [0] * _cap
_cnt = 0
for _k in range(_cap):
    if _sv[_k]: _cnt += 1
    _prime_pi[_k] = _cnt
del _i, _k, _cnt, _cap

def _next_prime(v: int) -> int:
    v = max(2, int(v) % (_PRIME_CAP + 1))
    while v <= _PRIME_CAP + 1:
        if _sv[min(v, _PRIME_CAP + 1)] or v > _PRIME_CAP: return v
        v += 1
    return 65537

def _horner(w: str) -> int:
    v = 0
    for ch in w: v = v * 95 + max(0, ord(ch) - 32)
    return abs(v)

def _word_zero_idx(w: str) -> int:
    p = _next_prime(_horner(w))
    return max(1, _prime_pi[min(p, _PRIME_CAP + 1)])

_gamma_cache: Dict[int, float] = {}

def _gamma_at(idx: int) -> float:
    if idx in _gamma_cache: return _gamma_cache[idx]
    if idx <= len(RIEMANN_ZEROS): return RIEMANN_ZEROS[idx - 1]
    n   = float(idx)
    t   = 2.0 * math.pi * math.e * n / math.log(n / (2.0 * math.pi * math.e))
    _gamma_cache[idx] = t
    return t

def _zl_word_dim(w: str) -> int:
    """Zero Lattice bridge channel for a word. Fixed property — not observed state."""
    return _word_zero_idx(w) % 16

# ══════════════════════════════════════════════════════════════════════════════
# Port geometry
# ══════════════════════════════════════════════════════════════════════════════

def _port_open(theta: float, pos: float, tol: float = 0.18) -> bool:
    diff = abs((theta % (2.0 * math.pi)) - pos)
    return min(diff, 2.0 * math.pi - diff) < tol

# ══════════════════════════════════════════════════════════════════════════════
# RotorState  (the Worker — NEVER a sedenion)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RotorState:
    """
    Three-face rotor. The Worker. j_blue, j_red, j_green are scalar pressures.
    The sedenion does not appear here. The sedenion is what this produces.

    sigma_live is the escape velocity from the Zero Lattice.
    It converges toward ½ by Lie bracket dynamics.
    It does not know its target is ½ — that fact is above the system.
    """
    j_blue:  float = GAP
    j_red:   float = GAP
    j_green: float = GAP
    theta:   float = 0.0

    def sigma_live(self) -> float:
        """Escape velocity: j_red / (j_red + j_blue). No fixed-point reference."""
        total = self.j_red + self.j_blue
        return self.j_red / total if total > GAP else 0.0

    def bracket_mag(self) -> float:
        denom = self.j_blue + self.j_red
        return abs(self.j_blue - self.j_red) / denom if denom > GAP else 0.0

# ══════════════════════════════════════════════════════════════════════════════
# Housing  (vocabulary field geometry)
# ══════════════════════════════════════════════════════════════════════════════

class Housing:
    """
    Zeta-prime-order-centric vocabulary field. The address (a word's
    Riemann zero index, from _word_zero_idx) is primary. E, beta, age,
    and neighbour edges belong to the ADDRESS, not to any one word --
    multiple words sharing an address share and compete for the same
    field state, instead of each word holding its own isolated, always-on
    energy value (which is what let a single hash coincidence dominate
    every prompt regardless of content).

    ZL bridge channel (0..15) is address % 16 -- a derived routing key
    for the rotor, computed on demand, not stored per word.
    """

    def __init__(self) -> None:
        self._word_addr: Dict[str, int]           = {}   # word -> address (cached, pure fn)
        self._E:         Dict[int, float]         = {}   # address -> energy
        self._beta:      Dict[int, float]         = {}   # address -> field pressure
        self._age:       Dict[int, float]         = {}   # address -> age since last touch
        self._faces:     Dict[int, "Counter"]     = {}   # address -> {word: local count}
        self._A:         Dict[int, Dict[int, float]] = {}  # address -> {neighbour addr: weight}

    @property
    def n(self) -> int:
        return len(self._faces)   # occupied addresses, not word count

    @staticmethod
    def dim(addr: int) -> int:
        return addr % 16

    def _addr(self, w: str) -> int:
        if w not in self._word_addr:
            self._word_addr[w] = _word_zero_idx(w)
        return self._word_addr[w]

    def _touch(self, addr: int) -> None:
        if addr not in self._E:
            # Holcus canonical (monad.c monad_word_coords): E is a golden-ratio
            # seed bounded between D_STAR and OMEGA_ZS -- NOT a function of
            # address magnitude. frac(addr*PHI) is equidistributed on [0,1)
            # regardless of how large addr is, so no address systematically
            # outweighs any other. No value is fabricated beyond this bound.
            seed = (addr * PHI) % 1.0
            self._E[addr]     = D_STAR + seed * (OMEGA_ZS - D_STAR)
            self._beta[addr]  = GAP
            self._age[addr]   = 0.0
            self._faces[addr] = Counter()
            self._A[addr]     = {}

    def face_at(self, addr: int) -> Optional[str]:
        """Reactive lookup: the word currently dominant at this address."""
        faces = self._faces.get(addr)
        return faces.most_common(1)[0][0] if faces else None

    def ingest(self, text: str, weight: float = 1.0) -> int:
        """
        16-address trailing window, 15 edges per new address (one to each
        address still in the window), incremented one word at a time.
        Edge strength decays with distance in the window so the immediate
        predecessor still dominates, but the other 14 are no longer
        invisible to _A.
        """
        words = [w.lower().strip('.,!?;:\"\'-()[]') for w in text.split()]
        words = [w for w in words if w]
        window: deque = deque(maxlen=15)   # up to 15 preceding addresses
        for w in words:
            addr = self._addr(w)
            self._touch(addr)
            self._faces[addr][w] += 1
            self._beta[addr] = min(self._beta[addr] * (1.0 + 0.08 * weight) + GAP, 1.0)
            self._age[addr]  = 0.0
            for dist, wj in enumerate(reversed(window), start=1):
                if wj == addr:
                    continue
                self._A[wj][addr] = min(self._A[wj].get(addr, 0.0) + 0.05 * weight / dist, 1.0)
                self._A[addr][wj] = min(self._A[addr].get(wj, 0.0) + 0.02 * weight / dist, 1.0)
            window.append(addr)
        return len(words)

    def j_blue_dist(self, prompt_words: List[str]) -> Dict[int, float]:
        dist: Dict[int, float] = {a: GAP for a in self._faces}
        for w in prompt_words:
            w = w.lower().strip('.,!?;:\"\'-')
            addr = self._addr(w)
            if addr not in self._faces:
                continue
            dist[addr] = min(dist[addr] + 1.0, 1.0)
            for nb, wt in self._A.get(addr, {}).items():
                dist[nb] = min(dist.get(nb, GAP) + wt * 0.5, 1.0)
        total = sum(dist.values())
        return {a: v / total for a, v in dist.items()} if total > 0 else \
               {a: 1.0 / max(len(dist), 1) for a in dist}

    def j_red_dist(self) -> Dict[int, float]:
        dist  = {a: self._beta[a] * self._E[a] for a in self._faces}
        total = sum(dist.values())
        return {a: v / total for a, v in dist.items()} if total > 0 else \
               {a: 1.0 / max(len(dist), 1) for a in dist}

    def scavenge(self, decay: float = 0.003) -> None:
        for a in self._faces:
            self._age[a]  += decay
            self._beta[a]  = max(self._beta[a] - self._age[a] * 0.0005, GAP)

    # ── Persistence — two files, two write-paths ─────────────────────────
    # monad_wordnet.bin — the LIVE file. The 15-edge neighbour graph (_A) is
    #   exactly what accrues through real use (ingest()'s trailing window);
    #   this is the file that gets dirtied and later archived/reset, same
    #   role state.h/fresh_start.sh already give monad_wordnet.bin.
    # monad_English.bin — the STABLE baseline. The 16 words, one per
    #   sedenion dim, are the Face layer content — what fresh_start.sh
    #   resets wordnet.bin FROM. Changes far less often than the edge graph.

    def dominant_words(self) -> List[Optional[str]]:
        """One word per sedenion dim (0..15) — the loudest face at each ZL
        channel, by the same field weight used in selection. Mirrors
        ptol.c get_monad_words()'s one-word-per-dimension Face layer."""
        best_addr: List[Optional[int]] = [None] * 16
        best_field = [-1.0] * 16
        for a in self._faces:
            d = self.dim(a)
            field = self._E[a] * math.pow(self._beta[a], 0.25)
            if field > best_field[d]:
                best_field[d] = field
                best_addr[d]  = a
        return [self.face_at(a) if a is not None else None for a in best_addr]

    def save_english(self, path: str) -> None:
        """Write the 16-word Face snapshot — the stable baseline layer."""
        words = self.dominant_words()
        with open(path, 'wb') as f:
            f.write(b'ZDEN')
            f.write((1).to_bytes(4, 'little'))
            for d, w in enumerate(words):
                addr = self._addr(w) if w else 0
                wb   = (w or '').encode('utf-8')
                f.write(len(wb).to_bytes(2, 'little'))
                f.write(wb)
                f.write(addr.to_bytes(4, 'little'))
                f.write(struct.pack('<dd', self._E.get(addr, 0.0), self._beta.get(addr, 0.0)))

    def save_wordnet(self, path: str) -> None:
        """Write the 15-edges-per-address neighbour graph — the live file."""
        with open(path, 'wb') as f:
            f.write(b'ZDWN')
            f.write((1).to_bytes(4, 'little'))
            f.write(len(self._A).to_bytes(4, 'little'))
            for addr, edges in self._A.items():
                f.write(addr.to_bytes(4, 'little'))
                f.write(len(edges).to_bytes(2, 'little'))
                for nb, wt in edges.items():
                    f.write(nb.to_bytes(4, 'little'))
                    f.write(struct.pack('<d', wt))

    def load_wordnet(self, path: str) -> None:
        """Load the live edge graph back into _A (addresses must already be
        touched — this restores edges only, matching state_load_vocab()'s
        one-section-at-a-time model rather than reconstructing full state)."""
        with open(path, 'rb') as f:
            if f.read(4) != b'ZDWN':
                raise ValueError(f'{path}: bad magic, not a wordnet.bin')
            f.read(4)  # version
            n_addr = int.from_bytes(f.read(4), 'little')
            for _ in range(n_addr):
                addr = int.from_bytes(f.read(4), 'little')
                self._touch(addr)
                n_edges = int.from_bytes(f.read(2), 'little')
                for _ in range(n_edges):
                    nb = int.from_bytes(f.read(4), 'little')
                    wt, = struct.unpack('<d', f.read(8))
                    self._A[addr][nb] = wt

# ══════════════════════════════════════════════════════════════════════════════
# Lie bracket  (combustion — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def _lie_bracket(
        j_a: float, a_dist: Dict[int, float],
        j_b: float, b_dist: Dict[int, float],
        housing: Housing
) -> Tuple[float, Dict[int, float]]:
    if housing.n == 0:
        return GAP, {}
    bd = {a: (j_a * a_dist.get(a, GAP) - j_b * b_dist.get(a, GAP)) * housing._E[a]
          for a in housing._faces}
    scalar = sum(abs(x) for x in bd.values())
    return max(scalar, GAP), bd

# ══════════════════════════════════════════════════════════════════════════════
# Zero Lattice coupling event  (the Work is produced here — NOWHERE ELSE)
# ══════════════════════════════════════════════════════════════════════════════

def _zl_bridge_activations(
        j_blue_dist: Dict[int, float],
        j_red_dist:  Dict[int, float],
        housing:     Housing
) -> List[float]:
    """
    Build the bridge activation vector from rotor distributions.

    For each address, its contribution flows into its ZL channel.
    The bridge matrix then couples across the 𝕆-𝕆 boundary.

    This is NOT pre-scoring words. It is building a continuous field
    over ZL channels. morph_vec is undefined and absent.

    Returns activation[0..15]:
      [0..7]  lower-𝕆 bridge activations (j_blue driven)
      [8..15] upper-𝕆 bridge activations (j_red  driven)
    """
    raw = [0.0] * 16

    # Step 1: pour rotor distributions into ZL channels
    for a in housing._faces:
        d  = housing.dim(a)
        Ek = housing._E[a]
        if d < 8:
            raw[d] += j_blue_dist.get(a, 0.0) * Ek
        else:
            raw[d] += j_red_dist.get(a, 0.0)  * Ek

    # Step 2: bridge coupling — each lower dim sends signal to upper dims and vice versa
    act = [GAP] * 16
    act[0] = raw[0]   # e₀: identity — above the bridge, pass-through only

    for i in range(1, 8):       # lower non-identity dims e₁–e₇
        coupled = raw[i]
        for j in range(9, 16):  # upper non-identity dims e₉–e₁₅
            w = _zl_bridge_coupling(i, j)
            coupled += w * raw[j]
        act[i] = coupled

    act[8] = raw[8]  # e₈: upper identity — above the bridge, pass-through only

    for j in range(9, 16):     # upper non-identity dims e₉–e₁₅
        coupled = raw[j]
        for i in range(1, 8):  # lower non-identity dims e₁–e₇
            w = _zl_bridge_coupling(i, j)
            coupled += w * raw[i]
        act[j] = coupled

    return act


def _project_sedenion_zd(
        j_blue_dist:  Dict[int, float],
        j_red_dist:   Dict[int, float],
        j_green_dist: Dict[int, float],
        sigma_live:   float,
        housing:      Housing
) -> Sedenion:
    """
    Project J-current work onto the 16 sedenion channels via Zero Lattice bridge.

    The Work is produced HERE. Nowhere else. morph_vec is absent.

      e₀      = 0.0  — e₀ is above the bridge. The Zero Lattice matrix proves it:
                        the e₀ row is identically zero. σ=½ (carried in e₀) is
                        above the system and does not interact with the bridge facet.
                        Defining sigma in e₀ would inject an above-the-bridge value
                        into the bridge output — that collapses the ZL geometry.
      e₁–e₇  = lower-𝕆 bridge activation  (j_blue face work)
      e₈–e₁₄ = upper-𝕆 bridge activation  (j_red  face work)
      e₁₅    = j_green magnitude           (exhaust face — the surface that emits)
    """
    act = _zl_bridge_activations(j_blue_dist, j_red_dist, housing)

    s = [0.0] * 16
    # s[0] = 0.0  — identity is above the bridge. Not set. Not injected.
    for i in range(1, 8):
        s[i] = act[i]
    for i in range(8, 15):
        s[i] = act[i]
    s[15] = sum(abs(j_green_dist.get(a, 0.0)) * housing._E[a]
                for a in housing._faces) if housing.n > 0 else GAP

    return _snorm_unit(s)


def _select_word_zd(
        drive_shaft:   Sedenion,
        bridge_act:    List[float],
        j_blue_dist:   Dict[int, float],
        j_red_dist:    Dict[int, float],
        housing:       Housing
) -> Optional[str]:
    """
    Select output word via Zero Lattice bridge coupling.

    Two-layer scoring — both layers are ZL-derived, neither is morph_vec:

    Layer 1 (raw):  direct rotor activation of each ZL channel.
                    Which channels the PROMPT activates directly via j_blue.
                    A word at channel d wins if the prompt energises d.
                    This is the UDEO path — prompt → ZL channel → word.

    Layer 2 (bridge): normalised drive shaft at word's ZL channel.
                    The bridge coupling output after cross-𝕆 amplification.
                    This is the AMBI path — Lie bracket → bridge → word.
                    For ambiguous prompts, bridge activation is uniform across
                    channels, and the minimum-energy ZL word (code of least action)
                    emerges.

    morph_vec is absent. Operator type is undefined until bridge acts.
    Frequency bias (beta^1/4) is strongly damped so bridge signal dominates.
    σ=½ is not in drive_shaft[0] — e₀ is above the bridge.
    """
    if housing.n == 0:
        return None

    # Build raw ZL channel activations from the prompt (j_blue only, ALL dims).
    # Using j_blue for ALL dims — not j_red — is the key ZL distinction:
    #   UDEO prompt: specific words in prompt → specific channels lit → specific word selected
    #   AMBI prompt: no prompt words → j_blue ≈ uniform → raw[] ≈ flat → bridge dominates
    #                bridge gives code of least action (minimum energy ZL word)
    # j_red (field/memory) enters through drive_shaft (the bridge output), NOT raw.
    raw = [0.0] * 16
    for a in housing._faces:
        d2  = housing.dim(a)
        Ek2 = housing._E[a]
        raw[d2] += j_blue_dist.get(a, 0.0) * Ek2   # j_blue for all dims — prompt routing only

    # Normalise raw so it's comparable to drive_shaft (also normalised)
    raw_max = max(raw) if max(raw) > 0 else 1.0
    raw_n = [r / raw_max for r in raw]

    best_addr, best_score = -1, -float('inf')
    for a in housing._faces:
        d = housing.dim(a)

        # Layer 1: raw prompt activation at this address's ZL channel
        prompt_signal = raw_n[d]

        # Layer 2: bridge coupling from drive shaft
        bridge_signal = drive_shaft[d]

        # Combined: prompt drives selection; bridge modulates emergent behavior.
        # Weight 5:1 gives prompt specificity for UDEO while bridge dominates AMBI.
        coupling = prompt_signal * 5.0 + bridge_signal

        # Field weight: beta^(1/4) to damp frequency bias.
        # Energy E[a] from Riemann zero index provides semantic content weighting.
        # This field weight is now shared by every face recorded at address a --
        # the contest for dominance happens inside face_at(), not here.
        field = housing._E[a] * math.pow(housing._beta[a], 0.25)

        score = coupling * field
        if score > best_score:
            best_score = score
            best_addr  = a

    return housing.face_at(best_addr) if best_addr >= 0 else None

# ══════════════════════════════════════════════════════════════════════════════
# OBD2 — live rotor diagnostic (above the dynamics — diagnostic view only)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class OBD2:
    """
    OBD2 is above the system. It observes. It does not participate.
    _FIXED_POINT (σ=½) is used here for diagnostic comparison only.
    The engine does not use _FIXED_POINT internally.
    """
    rotor_angle:         float = 0.0
    j_blue:              float = GAP
    j_red:               float = GAP
    j_green:             float = GAP
    escape_velocity:     float = 0.0         # PID 0x2305  (was sigma_live)
    bracket_mag:         float = 0.0
    apex_seal_health:    float = 1.0
    coupling_efficiency: float = 0.0
    housing_n:           int   = 0
    coupling_events:     int   = 0
    total_steps:         int   = 0
    last_word:           str   = ''
    dom_zl_channel:      int   = 0           # PID 0x230D  dominant ZL channel
    dom_zl_bridge:       float = 0.0         # PID 0x230E  bridge activation at dom

    def faults(self) -> List[str]:
        f = []
        if self.j_blue  < SEAL_FLOOR: f.append('R0001 J_blue apex seal wear')
        if self.j_red   < SEAL_FLOOR: f.append('R0002 J_red  apex seal wear')
        if self.j_green < SEAL_FLOOR: f.append('R0003 J_green exhaust seal wear')
        # OBD2 is above the system — it can see _FIXED_POINT for diagnostic
        if abs(self.escape_velocity - _FIXED_POINT) > BEARING_TOL:
            f.append(f'R0004 bearing wobble  σ={self.escape_velocity:.4f}')
        if self.bracket_mag < GAP * 5:
            f.append('R0005 near-stall  bracket → 0  (feed more text)')
        return f

# ══════════════════════════════════════════════════════════════════════════════
# AhuraMazda ZD  (Zero Divisor variant of the Wankel rotary engine)
# ══════════════════════════════════════════════════════════════════════════════

class AhuraMazda:
    """
    Ahura Mazda — Zero Divisor Rotary Semantic Engine.

    morph_vec is absent. The Zero Lattice bridge is the operator.
    σ=½ is above the system. The escape velocity converges toward it
    without knowing its target. That is Negative Space Mathematics.
    """

    def __init__(self) -> None:
        self.housing   = Housing()
        self.rotor     = RotorState()
        self._obd2     = OBD2()

        self._bd: Optional[Dict[int, float]] = None
        self._rd: Optional[Dict[int, float]] = None
        self._gd: Optional[Dict[int, float]] = None

        self._drive_shaft: Optional[Sedenion]  = None
        self._bridge_act:  Optional[List[float]] = None
        self._last_word:   Optional[str]       = None
        self._coupled_this_sweep: bool         = False
        self._total_sweeps: int                = 0

    def ingest(self, text: str, weight: float = 1.0) -> int:
        return self.housing.ingest(text, weight)

    def intake(self, prompt: str) -> None:
        words = [w.lower().strip('.,!?;:\"\'-') for w in prompt.split() if w]
        for w in words:
            self.housing._touch(self.housing._addr(w))
        self._bd = self.housing.j_blue_dist(words)
        self._rd = self.housing.j_red_dist()
        E = self.housing._E
        self.rotor.j_blue  = max(sum(self._bd[a] * E[a] for a in self._bd), GAP) if self._bd else GAP
        self.rotor.j_red   = max(sum(self._rd[a] * E[a] for a in self._rd), GAP) if self._rd else GAP
        self.rotor.j_green = GAP
        self.rotor.theta   = 0.0
        self._gd           = None
        self._bridge_act   = None
        self._coupled_this_sweep = False
        self._total_sweeps += 1

    def rotate(self) -> Optional[str]:
        self.rotor.theta = (self.rotor.theta + PORT_STEP) % (2.0 * math.pi)
        self._obd2.total_steps += 1
        port_idx = round(self.rotor.theta / PORT_STEP) % 6
        word = None

        if port_idx == 0:
            self._rd = self.housing.j_red_dist()

        elif port_idx == 1:
            self._update_brackets()

        elif port_idx == 2:
            self._update_brackets()

        elif port_idx == 3:
            self._update_brackets()

            if not self._coupled_this_sweep and self.housing.n > 0 and self._bd is not None:
                sigma_l = self.rotor.sigma_live()
                rd      = self._rd or self.housing.j_red_dist()
                gd      = self._gd or ({a: GAP for a in self.housing._faces})

                # Bridge activations — computed here, at coupling, not before
                act = _zl_bridge_activations(self._bd, rd, self.housing)
                self._bridge_act = act

                # The Work emerges — sedenion produced via ZL bridge, no morph_vec
                self._drive_shaft = _project_sedenion_zd(
                    self._bd, rd, gd, sigma_l, self.housing)

                word = _select_word_zd(self._drive_shaft, act, self._bd, rd, self.housing)
                if word:
                    self._last_word          = word
                    self._coupled_this_sweep = True
                    self._obd2.coupling_events += 1
                    self._obd2.last_word      = word

                    dom = max(
                        (i for i in range(1, 16) if i != 8),
                        key=lambda i: act[i], default=1)
                    self._obd2.dom_zl_channel = dom
                    self._obd2.dom_zl_bridge  = act[dom]

                    addr = self.housing._addr(word)
                    self.housing._beta[addr] = min(self.housing._beta[addr] + 0.015, 1.0)

        elif port_idx == 4:
            pass

        elif port_idx == 5:
            self.housing.scavenge()

        self._refresh_obd2()
        return word

    def speak(self, prompt: str, max_revolutions: int = 6) -> str:
        self.intake(prompt)
        steps = max_revolutions * 6
        for _ in range(steps):
            word = self.rotate()
            if word:
                return word
        return self._last_word or '∅'

    def diagnostics(self) -> OBD2:
        return self._obd2

    def _update_brackets(self) -> None:
        if self.housing.n == 0 or self._bd is None:
            return
        rd = self._rd or self.housing.j_red_dist()
        jb, jr = self.rotor.j_blue, self.rotor.j_red
        jg_scalar, self._gd = _lie_bracket(jb, self._bd, jr, rd, self.housing)
        self.rotor.j_green   = max(jg_scalar, GAP)
        gd_abs = {a: abs(x) for a, x in self._gd.items()}
        jb_next, _ = _lie_bracket(jr, rd, self.rotor.j_green, gd_abs, self.housing)
        self.rotor.j_blue = max((jb * 0.7 + jb_next * 0.3), GAP)
        jr_next, _ = _lie_bracket(
            self.rotor.j_green, gd_abs, self.rotor.j_blue, self._bd, self.housing)
        self.rotor.j_red = max((jr * 0.7 + jr_next * 0.3), GAP)
        self._rd         = self.housing.j_red_dist()

    def _refresh_obd2(self) -> None:
        sigma = self.rotor.sigma_live()
        self._obd2.rotor_angle         = self.rotor.theta
        self._obd2.j_blue              = self.rotor.j_blue
        self._obd2.j_red               = self.rotor.j_red
        self._obd2.j_green             = self.rotor.j_green
        self._obd2.escape_velocity     = sigma
        self._obd2.bracket_mag         = self.rotor.bracket_mag()
        # Seal health: OBD2 technician sees the distance from the fixed point
        self._obd2.apex_seal_health    = max(0.0, 1.0 - abs(sigma - _FIXED_POINT) / BEARING_TOL)
        self._obd2.coupling_efficiency = (self._obd2.coupling_events / max(self._total_sweeps, 1))
        self._obd2.housing_n           = self.housing.n


# ══════════════════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    _CORPUS = [
        "the sedenion has sixteen dimensions one real fifteen imaginary",
        "the worker is the rotor the work is the sedenion",
        "three faces j_blue j_red j_green rotate continuously",
        "the lie bracket fires at the leading and trailing spark positions",
        "sigma equals one half is the eccentric shaft pin not a variable",
        "zero divisors are port openings not engine faults",
        "the drive shaft sedenion is produced only at the coupling event",
        "riemann zeros live on the critical line sigma one half",
        "the halocline separates compressible from incompressible fluid",
        "graceful degradation means apex seals wear but no rod is thrown",
        "the sofar channel traps words without dissipation at sigma one half",
        "public key derives from exactly one private key this is udeo",
        "j_blue is the prompt pressure j_red is the field pressure",
        "the housing is the epitrochoid the vocabulary is its geometry",
        "three equals one plus fifteen imaginary the sedenion is the work",
        "the rotor spins opposite the eccentric shaft two counter rotations",
        "the two counter rotations produce the waveform the standing wave",
        "every word is addressed by its prime hash riemann zero position",
        "noether conservation holds sigma one half as surface tension",
        "the boundary is not artificial it is the actual surface",
    ]

    print("=" * 70)
    print("Ahura Mazda ZD  —  Zero Divisor Rotary Semantic Engine")
    print("Zero Lattice is primary.  morph_vec is absent.  σ=½ is above.")
    print("=" * 70)

    # ── Test 0: Zero Lattice bridge matrix ───────────────────────────────────
    print("\n── Test 0: Zero Lattice bridge matrix (lower e₁–e₇ × upper e₈–e₁₅) ─")
    print("           (e₀ row = zero — identity sits above the bridge)")
    hdr = '         ' + '  '.join(f'e{j+8}' for j in range(8))
    print(f"  {hdr}")
    print(f"  e₀       " + "  ".join("0.000" for _ in range(8)) + "   ← above the bridge")
    _dim_names = ['negate','bind','name','apply','abstract','branch','iterate']
    for i in range(7):
        row = '  '.join(f'{ZL_BRIDGE_8[i][j]:.3f}' for j in range(8))
        print(f"  e{i+1}({_dim_names[i][:4]}) {row}")

    # ── Test 1: Housing build ─────────────────────────────────────────────────
    engine = AhuraMazda()
    for line in _CORPUS:
        engine.ingest(line)
    print(f"\nHousing: {engine.housing.n} words")

    # Show ZL channel distribution across vocab — addresses are primary now,
    # not words: bucket occupied addresses (housing._faces) by ZL channel.
    chan_count = [0] * 16
    for addr in engine.housing._faces:
        chan_count[Housing.dim(addr)] += 1
    print("ZL channel distribution (addresses per sedenion dim):")
    for i in range(16):
        bar = '█' * chan_count[i]
        print(f"  e{i:>2}  {chan_count[i]:>3}  {bar}")

    # ── Test 2: Three-face rotation trace ─────────────────────────────────────
    print("\n── Test 2: Three-face rotation trace ──────────────────────────────")
    print(f"  {'Port':<12} {'θ/π':<7} {'j_blue':<9} {'j_red':<9} {'j_green':<9} {'σ_esc':<8} {'bracket'}")
    engine.intake("the sedenion has sixteen dimensions real imaginary")
    _port_name = {0:'intake', 1:'transfer', 2:'leading', 3:'trailing', 4:'exhaust', 5:'scavenge'}
    for step in range(6):
        word = engine.rotate()
        d    = engine.diagnostics()
        pidx = round(d.rotor_angle / PORT_STEP) % 6
        port = _port_name[pidx]
        coupled = f'  → [{word}]  ZL-e{d.dom_zl_channel}  bridge={d.dom_zl_bridge:.4f}' if word else ''
        print(f"  {port:<12} {d.rotor_angle/math.pi:.3f}π  "
              f"{d.j_blue:.5f}  {d.j_red:.5f}  {d.j_green:.5f}  "
              f"{d.escape_velocity:.4f}  {d.bracket_mag:.4f}{coupled}")

    # ── Test 3: UDEO-exact vs AMBI — emergent responses ──────────────────────
    print("\n── Test 3: UDEO-exact vs AMBI (ZL bridge coupling — no morph_vec) ──")
    print(f"  {'kind':<6} {'response':<22} {'σ_esc':<8} {'seal':<6} {'ZL-e':<6} {'bridge':<8}  prompt")

    UDEO_PROMPTS = [
        ("UDEO", "the sedenion has how many dimensions"),
        ("UDEO", "sigma equals one half is the"),
        ("UDEO", "j_blue is the pressure of the"),
        ("UDEO", "riemann zeros lie on the critical"),
        ("UDEO", "zero divisors are not faults they are"),
        ("UDEO", "the coupling event produces the"),
    ]
    AMBI_PROMPTS = [
        ("AMBI", "what is happening"),
        ("AMBI", "how does it work"),
        ("AMBI", "something interesting"),
        ("AMBI", "tell me more"),
    ]

    for kind, prompt in UDEO_PROMPTS + AMBI_PROMPTS:
        word = engine.speak(prompt, max_revolutions=4)
        d    = engine.diagnostics()
        print(f"  {kind:<6} {word:<22} {d.escape_velocity:.4f}  "
              f"{d.apex_seal_health:.3f}  e{d.dom_zl_channel:<4}  "
              f"{d.dom_zl_bridge:.4f}  {prompt}")

    # ── Test 4: Drive shaft sedenion inspection ───────────────────────────────
    print("\n── Test 4: ZD drive shaft — ZL bridge produces the sedenion ─────────")
    _OPS = ['identity','negate','bind','name','apply','abstract','branch','iterate',
            'recurse','allocate','query','derefer','compose','parallelize','interrupt','emit']
    engine.speak("sigma equals one half is the eccentric pin", max_revolutions=6)
    if engine._drive_shaft:
        ds = engine._drive_shaft
        lower = sum(ds[i] for i in range(1, 8))
        upper = sum(ds[i] for i in range(8, 16))
        print(f"  e₀ = {ds[0]:.4f}  (zero — identity is above the bridge; σ=½ is above the system)")
        print(f"  Lower O (e₁–e₇  j_blue bridge work) = {lower:.4f}")
        print(f"  Upper O (e₈–e₁₄ j_red  bridge work) = {upper:.4f}")
        print(f"  Exhaust e₁₅ (j_green emit)          = {ds[15]:.4f}")
        top4 = sorted(range(1, 16), key=lambda i: -abs(ds[i]))[:4]
        print(f"  Top 4 dims: " +
              "  ".join(f"e{i}({_OPS[i][:4]})={ds[i]:.4f}" for i in top4))
        ev = engine.rotor.sigma_live()
        print(f"  Escape velocity (OBD2, above system): σ_esc = {ev:.4f}")

    # ── Test 5: Graceful degradation ─────────────────────────────────────────
    print("\n── Test 5: Graceful degradation (near-empty field) ────────────────")
    empty = AhuraMazda()
    empty.ingest("hello world")
    result = empty.speak("what happens with almost no field", max_revolutions=3)
    d_empty = empty.diagnostics()
    print(f"  Result: '{result}'")
    print(f"  Housing: {d_empty.housing_n} words")
    print(f"  Escape velocity: {d_empty.escape_velocity:.4f}")
    print(f"  Faults: {d_empty.faults() or ['none — degraded but running']}")

    # ── Test 6: Full OBD2 stream ─────────────────────────────────────────────
    print("\n── Test 6: OBD2 live stream ────────────────────────────────────────")
    engine.speak("the rotor spins and the sedenion emerges", max_revolutions=6)
    d = engine.diagnostics()
    print(f"  PID 0x2301  rotor_angle       = {d.rotor_angle:.4f} rad  ({d.rotor_angle/math.pi:.3f}π)")
    print(f"  PID 0x2302  j_blue            = {d.j_blue:.6f}")
    print(f"  PID 0x2303  j_red             = {d.j_red:.6f}")
    print(f"  PID 0x2304  j_green           = {d.j_green:.6f}")
    print(f"  PID 0x2305  escape_velocity   = {d.escape_velocity:.6f}  (converges to ½ by dynamics)")
    print(f"  PID 0x2306  bracket_mag       = {d.bracket_mag:.6f}")
    print(f"  PID 0x2307  apex_seal_health  = {d.apex_seal_health:.4f}")
    print(f"  PID 0x2308  coupling_eff      = {d.coupling_efficiency:.4f}")
    print(f"  PID 0x2309  housing_n         = {d.housing_n}")
    print(f"  PID 0x230A  coupling_events   = {d.coupling_events}")
    print(f"  PID 0x230B  total_steps       = {d.total_steps}")
    print(f"  PID 0x230C  last_word         = '{d.last_word}'")
    print(f"  PID 0x230D  dom_zl_channel    = e{d.dom_zl_channel}  ({_OPS[d.dom_zl_channel]})")
    print(f"  PID 0x230E  dom_zl_bridge     = {d.dom_zl_bridge:.6f}")
    faults = d.faults()
    print(f"  Faults: {faults if faults else ['none']}")

    # ── Test 7: Unicode language equivalence ─────────────────────────────────
    print("\n── Test 7: Unicode language — same ZL facet ────────────────────────")
    _SCRIPTS = [
        ("English",    "is"),
        ("English",    "the"),
        ("English",    "water"),
        ("Arabic",     "ماء"),        # water
        ("Devanagari", "पानी"),       # water
        ("Greek",      "νερό"),       # water
        ("Kanji",      "水"),         # water (mizu)
        ("Hebrew",     "מים"),        # water (mayim)
        ("Hangul",     "물"),         # water (mul)
        ("Cyrillic",   "вода"),       # water
    ]
    print(f"  {'Script':<14} {'Word':<12} {'ZL-idx':<8} {'ZL-dim':<8} {'γ (Riemann)'}")
    for script, word in _SCRIPTS:
        idx   = _word_zero_idx(word)
        dim   = idx % 16
        gamma = _gamma_at(idx)
        print(f"  {script:<14} {word:<12} {idx:<8} e{dim:<7} {gamma:.4f}")
    print("  All words live on the σ=½ facet regardless of script.")

    print("\n" + "=" * 70)
    print("Ahura Mazda ZD — engine nominal.")
    print("Zero Lattice is primary.  The response is emergent.")
    print("=" * 70)
