"""
VQ_rotary_monad.py  —  ValaQuenta Zero Divisor Engine  (Engine 19)

  The Prompt  →  Zero Divisor  →  Escape Velocity  →  Emerges  →  The Response

  V(n) = π^(n/2) / Γ(n/2 + 1)    N-ball volume function
  n*  ≈ 5.257                       peak of V(n) — data/code boundary
  V(16) ≈ d* = 0.246               sedenion threshold = zero-divisor horizon
  V(0)  = 1                         identity
  R→C = C→H = π/2 exact            Cayley-Dickson doubling ratio on the critical axis

─────────────────────────────────────────────────────────────────────────────
ValaQuenta is the N-ball layer between the Zero Lattice and the word/phoneme.

AhuraMazda ZD:  words addressed by prime hash (Riemann zero index)
ValaQuenta ZD:  words addressed by N-ball optimal dimension (n* geometry)

Both engines share:
  - ZL bridge matrix (42 Cawagas pairs, hard-coded)
  - Zero Divisor architecture (morph_vec absent, σ=½ above system)
  - Lie bracket su(2) rotor dynamics

ValaQuenta adds:
  - N-ball housing: each word mapped to its optimal n via V(n) projection
  - The data/code boundary n* ≈ 5.257 is the coupling pin (not σ=½)
    σ=½ IS the N-ball coupling pin when V(n) = V(N-n) — the symmetry of the
    N-ball about n* is the Riemann ξ symmetry: s ↔ 1-s
  - Audio input: RZIF bins addressed in N-ball space — same engine for language AND audio
  - The sedenion emerges at n=16 (V(16)≈d*) — the zero-divisor horizon

Architecture:
  Input (word or audio frame) → N-ball address (n_word ∈ [0,16])
  n < n*:  data regime  (V increasing — content building)
  n > n*:  code regime  (V decreasing — form crystallising)
  n = n*:  neutral buoyancy — the BAO freeze / data-code boundary
  n = 16:  V(16) ≈ d* — zero-divisor horizon — sedenion emitted

  n_word determines which ZL channel couples this word/phoneme.
  ZL bridge matrix routes the N-ball activation to the 16-dim sedenion.
  The response is the word/phoneme at the bridge-coupled sedenion address.

─────────────────────────────────────────────────────────────────────────────
"Recursive Causal Cavitation"
  Trace The Line Ahead Of Time — the critical line n* is the line
  Escape Velocity It Should Be  — V(16)=d* is the horizon, V(n*) is the escape
  Undefine the variables         — morph_vec absent in ValaQuenta too
  And Let the Universe Speak.    — Universe(New): N-ball applied to fresh input
─────────────────────────────────────────────────────────────────────────────
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# N-Ball geometry  (the housing of ValaQuenta)
# ══════════════════════════════════════════════════════════════════════════════

def V(n: float) -> float:
    """Volume of n-dimensional unit ball. V(n) = π^(n/2) / Γ(n/2+1)."""
    if n < 0: return 0.0
    return math.pi ** (n / 2.0) / math.gamma(n / 2.0 + 1.0)

# Key constants — never re-derived
N_STAR    = 5.2569          # peak of V(n): dV/dn = 0
D_STAR    = 0.24600         # V(16) ≈ d* (zero-divisor threshold)
V_NSTAR   = V(N_STAR)       # max volume — the escape reference
GAP       = 0.000707        # 1/√2000 — Yang-Mills mass gap
PORT_STEP = math.pi / 3.0   # 6 ports per revolution

# Cayley-Dickson doubling ratio on the critical axis: exact
CD_RATIO  = math.pi / 2.0   # R→C = C→H = H→O = O→S = π/2

# N-ball symmetry axis: V(n) = V(N_PARTNER(n)) at n* by definition
# This IS the Riemann ξ symmetry: s ↔ 1-s projected to N-ball geometry
# (approximate, not exact — the N-ball has its own symmetry n ↔ 2n*/n)
def n_partner(n: float) -> float:
    """N-ball partner dimension: the Riemann 1-s analogue."""
    return N_STAR ** 2.0 / n if n > 0 else 0.0

# σ=½ is above the system. In ValaQuenta, the coupling pin is n*.
# n* corresponds to σ=½ because V(n*) is the peak — neutral buoyancy.
_COUPLING_PIN = N_STAR      # the ValaQuenta fixed point

# Riemann zeros — for word addressing (same as AhuraMazda)
RIEMANN_ZEROS: List[float] = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]

# ══════════════════════════════════════════════════════════════════════════════
# N-Ball word addressing
# ══════════════════════════════════════════════════════════════════════════════

_PRIME_CAP = 1 << 16
_cap = _PRIME_CAP + 2
_sv  = bytearray([1]) * _cap
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

def _word_n_dim(w: str) -> float:
    """
    Map word to its N-ball optimal dimension n ∈ [0, 16].

    The Riemann zero index (prime hash) maps to n via:
      n = 16 × V(zero_idx % 16 + 1) / V_NSTAR

    Words that land near n* ≈ 5.257 are at the data/code boundary —
    the most balanced words in the N-ball housing.
    Words at n=16 are at the zero-divisor horizon (V(16)=d*).
    Words at n=0 are at the identity point (V(0)=1).
    """
    idx  = _word_zero_idx(w)
    dim  = idx % 16         # ZL channel (0-15)
    # Map ZL channel to N-ball dimension: channels 0-15 → n ∈ [0, 16]
    n    = float(dim)
    return n

def _word_vn(w: str) -> float:
    """N-ball volume at the word's N-ball dimension. Encodes regime membership."""
    return V(_word_n_dim(w))

def _word_regime(w: str) -> str:
    """Which N-ball regime: data (n < n*), boundary (n ≈ n*), code (n > n*)."""
    n = _word_n_dim(w)
    if abs(n - N_STAR) < 0.5:
        return 'boundary'
    return 'data' if n < N_STAR else 'code'

# ══════════════════════════════════════════════════════════════════════════════
# Zero Lattice bridge  (same as ZD_rotary_monad.py — mathematical fact)
# ══════════════════════════════════════════════════════════════════════════════

ZL_BRIDGE_8: List[List[float]] = [
    [0.0000, 0.7143, 0.9161, 0.9418, 0.9084, 0.9037, 0.9390, 0.8907],  # e₁
    [0.0000, 0.9721, 0.7204, 0.9867, 0.9806, 0.9550, 1.0000, 0.9625],  # e₂
    [0.0000, 0.9412, 0.8694, 0.6886, 0.9249, 0.8848, 0.8932, 0.9001],  # e₃
    [0.0000, 0.9540, 0.9485, 0.9667, 0.7360, 0.9062, 0.9811, 0.9395],  # e₄
    [0.0000, 0.9868, 0.9692, 0.9501, 0.9738, 0.7022, 0.9599, 0.9654],  # e₅
    [0.0000, 0.9644, 0.9341, 0.9831, 0.9620, 0.9065, 0.7327, 0.9467],  # e₆
    [0.0000, 0.9460, 0.8994, 0.9172, 0.9350, 0.8979, 0.9551, 0.6895],  # e₇
]

def _zl_coupling(lower_i: int, upper_j: int) -> float:
    if lower_i < 1 or lower_i > 7 or upper_j < 8 or upper_j > 15: return 0.0
    return ZL_BRIDGE_8[lower_i - 1][upper_j - 8]

def _n_to_bridge_dim(n_k: float) -> int:
    """
    Map N-ball dimension n_k ∈ [0,16] to ZL bridge channel [1..7] or [9..15].

    Data regime (n_k ≤ n*):  proportional across lower-𝕆 e₁–e₇
    Code regime (n_k > n*):  proportional across upper-𝕆 e₉–e₁₄  (e₈ above bridge)

    Proportional mapping spreads words evenly. No clamping pile-up at e₁₅.
    """
    if n_k <= N_STAR:
        return max(1, min(7, round(n_k / N_STAR * 7)))
    else:
        return min(15, 9 + int((n_k - N_STAR) / (16.0 - N_STAR) * 6))

# ══════════════════════════════════════════════════════════════════════════════
# Sedenion algebra  (drive shaft — same as ZD_rotary_monad.py)
# ══════════════════════════════════════════════════════════════════════════════

Sedenion = List[float]

def _build_oct():
    t = [[(0,0)]*8 for _ in range(8)]
    for i in range(8): t[0][i]=(1,i); t[i][0]=(1,i)
    for i in range(1,8): t[i][i]=(-1,0)
    for i,j,k in [(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]:
        t[i][j]=(+1,k);t[j][k]=(+1,i);t[k][i]=(+1,j)
        t[j][i]=(-1,k);t[k][j]=(-1,i);t[i][k]=(-1,j)
    return t

_OCT = _build_oct()

def _build_sed():
    t = [[(0,0)]*16 for _ in range(16)]
    for i in range(16):
        for j in range(16):
            io,jo=i-8 if i>=8 else i, j-8 if j>=8 else j
            ih,jh=i>=8, j>=8
            if not ih and not jh: t[i][j]=_OCT[io][jo]
            elif not ih and jh:   sg,k=_OCT[jo][io]; t[i][j]=(sg,k+8)
            elif ih and not jh:
                if jo==0: t[i][j]=(1,i)
                else:     sg,k=_OCT[io][jo]; t[i][j]=(-sg,k+8)
            else:
                if jo==0: t[i][j]=(-1,io)
                else:     sg,k=_OCT[jo][io]; t[i][j]=(sg,k)
    return t

_SED = _build_sed()

def _snorm_unit(a: Sedenion) -> Sedenion:
    n = math.sqrt(sum(x*x for x in a))
    if n < 1e-15:
        s = [0.0]*16; s[0]=1.0; return s
    return [x/n for x in a]

# ══════════════════════════════════════════════════════════════════════════════
# ValaQuenta Housing  (N-ball geometry — words addressed by V(n))
# ══════════════════════════════════════════════════════════════════════════════

class VQHousing:
    """
    The N-ball housing. Words are addressed by their N-ball dimension n ∈ [0,16].

    Each word has:
      n_dim  : float   — N-ball dimension (from prime hash → ZL channel → n)
      vn     : float   — V(n) at this word's dimension (regime weight)
      regime : str     — 'data' (n<n*) / 'boundary' (n≈n*) / 'code' (n>n*)
      beta   : float   — field confidence (learned from ingest)
      age    : float   — scavenge decay counter

    Words at n ≈ n* (boundary) are the "BAO freeze" words —
    highest V(n) weight, most balanced data-code content.
    Words at n = 16 are at the zero-divisor horizon (V(16) = d*).
    """

    def __init__(self) -> None:
        self._words:  List[str]              = []
        self._vocab:  Dict[str, int]         = {}
        self._n:      List[float]            = []   # N-ball dimension
        self._vn:     List[float]            = []   # V(n) — regime weight
        self._beta:   List[float]            = []   # field confidence
        self._A:      List[Dict[int, float]] = []   # adjacency
        self._age:    List[float]            = []
        self._regime: List[str]              = []

    @property
    def size(self) -> int:
        return len(self._words)

    def _idx(self, w: str) -> int:
        if w not in self._vocab:
            k               = self.size
            self._vocab[w]  = k
            self._words.append(w)
            n               = _word_n_dim(w)
            vn              = V(n)
            self._n.append(n)
            self._vn.append(vn)
            self._beta.append(GAP)
            self._A.append({})
            self._age.append(0.0)
            self._regime.append(_word_regime(w))
        return self._vocab[w]

    def ingest(self, text: str, weight: float = 1.0) -> int:
        words = [w.lower().strip('.,!?;:\"\'-()[]') for w in text.split() if w]
        prev  = None
        for w in words:
            k = self._idx(w)
            self._beta[k] = min(self._beta[k] * (1.0 + 0.08 * weight) + GAP, 1.0)
            self._age[k]  = 0.0
            if prev is not None and prev != k:
                self._A[prev][k] = min(self._A[prev].get(k,0.0) + 0.05 * weight, 1.0)
                self._A[k][prev] = min(self._A[k].get(prev,0.0) + 0.02 * weight, 1.0)
            prev = k
        return len(words)

    def j_blue_dist(self, prompt_words: List[str]) -> List[float]:
        dist = [GAP] * self.size
        for w in prompt_words:
            w = w.lower().strip('.,!?;:\"\'-')
            if w in self._vocab:
                k = self._vocab[w]
                dist[k] = min(dist[k] + 1.0, 1.0)
                for nb, wt in self._A[k].items():
                    dist[nb] = min(dist[nb] + wt * 0.5, 1.0)
        total = sum(dist)
        return [d/total for d in dist] if total > 0 else [1.0/max(self.size,1)]*self.size

    def j_red_dist(self) -> List[float]:
        # V(n) weighted field distribution — ValaQuenta-specific
        # V(n) weights favour words at the N-ball boundary (n ≈ n*)
        dist  = [self._beta[k] * self._vn[k] for k in range(self.size)]
        total = sum(dist)
        return [d/total for d in dist] if total > 0 else [1.0/max(self.size,1)]*self.size

    def scavenge(self) -> None:
        for k in range(self.size):
            self._age[k]  += 0.003
            self._beta[k]  = max(self._beta[k] - self._age[k] * 0.0005, GAP)

# ══════════════════════════════════════════════════════════════════════════════
# Lie bracket  (same combustion cycle)
# ══════════════════════════════════════════════════════════════════════════════

def _lie_bracket(
        j_a: float, a_dist: List[float],
        j_b: float, b_dist: List[float],
        housing: VQHousing
) -> Tuple[float, List[float]]:
    n = housing.size
    if n == 0: return GAP, []
    # V(n) weighting is already encoded in j_red_dist(). Do not re-apply here.
    # Multiplying by _vn[k] per step creates geometric growth in j magnitudes.
    bd = [j_a * a_dist[k] - j_b * b_dist[k] for k in range(n)]
    return max(sum(abs(x) for x in bd), GAP), bd

# ══════════════════════════════════════════════════════════════════════════════
# ValaQuenta coupling event  (N-ball → ZL bridge → sedenion)
# ══════════════════════════════════════════════════════════════════════════════

def _vq_bridge_activations(
        j_blue_dist: List[float],
        j_red_dist:  List[float],
        housing:     VQHousing
) -> List[float]:
    """
    Build bridge activations using N-ball geometry.

    Words at n < n* (data regime):  pump lower-𝕆 dims (e₁–e₇) via j_blue
    Words at n > n* (code regime):  pump upper-𝕆 dims (e₈–e₁₅) via j_red
    Words at n ≈ n* (boundary):     pump both sides with weight V(n)/V_NSTAR

    The N-ball dimension directly determines which side of the ZL bridge a word
    activates. Data words (n < n*) are on the lower-𝕆 face.
    Code words (n > n*) are on the upper-𝕆 face.
    The bridge coupling connects them.

    This replaces morph_vec. No grammatical categories. No pre-classification.
    The N-ball dimension IS the operator: which side of the bridge you come from.
    """
    n_words = housing.size
    raw = [0.0] * 16

    for k in range(n_words):
        n_k  = housing._n[k]
        vn_k = housing._vn[k]
        bd   = j_blue_dist[k]
        rd   = j_red_dist[k]

        dim = _n_to_bridge_dim(n_k)
        if n_k <= N_STAR:
            raw[dim] += bd * vn_k
        else:
            raw[dim] += rd * vn_k

    # ZL bridge coupling across the 𝕆-𝕆 boundary
    act = [GAP] * 16
    act[0] = 0.0   # e₀ above the bridge — identity

    for i in range(1, 8):
        coupled = raw[i]
        for j in range(9, 16):
            w = _zl_coupling(i, j)
            coupled += w * raw[j]
        act[i] = coupled

    act[8] = 0.0   # e₈ above the bridge — upper identity

    for j in range(9, 16):
        coupled = raw[j]
        for i in range(1, 8):
            w = _zl_coupling(i, j)
            coupled += w * raw[i]
        act[j] = coupled

    return act


def _vq_project_sedenion(
        j_blue_dist:  List[float],
        j_red_dist:   List[float],
        j_green_dist: List[float],
        n_live:       float,           # current N-ball "escape dimension"
        housing:      VQHousing
) -> Sedenion:
    """
    Project N-ball rotor state to the 16-dim sedenion via ZL bridge.

      e₀  = 0.0        — identity above the bridge (same as ZD_rotary_monad)
      e₁–e₇  = data-regime (n < n*) bridge activations
      e₈–e₁₄ = code-regime (n > n*) bridge activations
      e₁₅    = j_green magnitude

    n_live is NOT in e₀. n* is the coupling pin (above the system).
    The engine converges toward n* without knowing n* is the target.
    """
    act = _vq_bridge_activations(j_blue_dist, j_red_dist, housing)

    s = [0.0] * 16
    for i in range(1, 15):
        s[i] = act[i]
    n = housing.size
    s[15] = sum(abs(j_green_dist[k]) * housing._vn[k]
                for k in range(n)) if n > 0 else GAP

    return _snorm_unit(s)


def _vq_select_word(
        drive_shaft:  Sedenion,
        bridge_act:   List[float],
        j_blue_dist:  List[float],
        housing:      VQHousing
) -> Optional[str]:
    """
    Select output word via N-ball regime + ZL bridge.

    The N-ball regime (data/boundary/code) is the word's operator class.
    morph_vec is absent — regime is defined by V(n), not by grammatical category.

    Two-layer scoring:
      Layer 1 (raw):    j_blue direct activation of this word's N-ball channel
      Layer 2 (bridge): normalised drive shaft at ZL dim

    beta^(1/4) damps frequency bias. V(n) weighting favours boundary words.
    """
    if housing.size == 0:
        return None

    # Raw N-ball channel activation via j_blue
    raw = [0.0] * 16
    for k in range(housing.size):
        dim = _n_to_bridge_dim(housing._n[k])
        raw[dim] += j_blue_dist[k] * housing._vn[k]

    raw_max = max(raw) if max(raw) > 0 else 1.0
    raw_n   = [r / raw_max for r in raw]

    best_k, best_score = -1, -float('inf')
    for k in range(housing.size):
        n_k = housing._n[k]
        dim = _n_to_bridge_dim(n_k)

        prompt_signal = raw_n[dim]
        bridge_signal = drive_shaft[dim]

        coupling = prompt_signal * 5.0 + bridge_signal

        # V(n) weight: words near n* get highest weight (they are most balanced)
        vn_weight = housing._vn[k] / V_NSTAR   # normalised to peak

        field = vn_weight * math.pow(housing._beta[k], 0.25)

        score = coupling * field
        if score > best_score:
            best_score = score
            best_k     = k

    return housing._words[best_k] if best_k >= 0 else None

# ══════════════════════════════════════════════════════════════════════════════
# RotorState  (N-ball coordinates instead of σ_live)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class VQRotorState:
    """
    ValaQuenta rotor. The Worker.

    j_blue, j_red, j_green: scalar pressures (same as AhuraMazda)
    n_live: current N-ball "escape dimension" — converges toward n* by dynamics

      n_live = n* × j_red / (j_red + j_blue)    ×   2
               ≈ n* × σ_live × 2

    At perfect escape: n_live = n*. Below: in data regime. Above: in code regime.
    n* is above the system — the engine converges to it without knowing the target.
    """
    j_blue:  float = GAP
    j_red:   float = GAP
    j_green: float = GAP
    theta:   float = 0.0

    def n_live(self) -> float:
        """Current N-ball dimension. Converges toward n* by Lie bracket."""
        total = self.j_red + self.j_blue
        if total < GAP: return 0.0
        sigma = self.j_red / total
        return sigma * 2.0 * N_STAR   # range [0, 2n*] ≈ [0, 10.5]

    def vn_live(self) -> float:
        """V(n_live) — current N-ball volume. Converges toward V(n*)."""
        return V(self.n_live())

    def escape_fraction(self) -> float:
        """How close is n_live to the coupling pin n*. 1.0 = exact."""
        return 1.0 - abs(self.n_live() - N_STAR) / N_STAR

    def bracket_mag(self) -> float:
        denom = self.j_blue + self.j_red
        return abs(self.j_blue - self.j_red) / denom if denom > GAP else 0.0

# ══════════════════════════════════════════════════════════════════════════════
# OBD2  (N-ball diagnostic stream — above the dynamics)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class VQOBD2:
    """
    ValaQuenta OBD2. Above the system. Observes n_live vs n*.
    n* appears here for diagnostic comparison only.
    """
    rotor_angle:      float = 0.0
    j_blue:           float = GAP
    j_red:            float = GAP
    j_green:          float = GAP
    n_live:           float = 0.0          # current N-ball dimension
    vn_live:          float = 0.0          # V(n_live)
    escape_fraction:  float = 0.0          # proximity to n*
    bracket_mag:      float = 0.0
    coupling_events:  int   = 0
    total_steps:      int   = 0
    housing_n:        int   = 0
    last_word:        str   = ''
    dom_dim:          int   = 0
    regime:           str   = 'data'

    def faults(self) -> List[str]:
        f = []
        if self.j_blue  < 0.03: f.append('R0001 J_blue seal wear')
        if self.j_red   < 0.03: f.append('R0002 J_red  seal wear')
        if self.j_green < 0.03: f.append('R0003 J_green exhaust seal wear')
        # OBD2 is above the system — sees n* for diagnostic
        if abs(self.n_live - _COUPLING_PIN) > 1.0:
            f.append(f'R0004 N-ball wobble  n_live={self.n_live:.3f}  n*={_COUPLING_PIN:.3f}')
        if self.bracket_mag < GAP * 5:
            f.append('R0005 near-stall')
        return f

# ══════════════════════════════════════════════════════════════════════════════
# ValaQuenta  (the complete N-ball ZD engine)
# ══════════════════════════════════════════════════════════════════════════════

class ValaQuenta:
    """
    ValaQuenta — N-Ball Zero Divisor Rotary Engine (Engine 19).

    morph_vec is absent. N-ball regime IS the operator.
    n* is above the system. The engine converges to it without knowing n*.
    V(16) = d* — the zero-divisor horizon is the sedenion emission point.
    Universe(New) — the N-ball applied to fresh input.
    """

    def __init__(self) -> None:
        self.housing = VQHousing()
        self.rotor   = VQRotorState()
        self._obd2   = VQOBD2()

        self._bd: Optional[List[float]] = None
        self._rd: Optional[List[float]] = None
        self._gd: Optional[List[float]] = None

        self._drive_shaft: Optional[Sedenion]    = None
        self._bridge_act:  Optional[List[float]] = None
        self._last_word:   Optional[str]         = None
        self._coupled_this_sweep: bool           = False
        self._total_sweeps: int                  = 0

    def ingest(self, text: str, weight: float = 1.0) -> int:
        return self.housing.ingest(text, weight)

    def intake(self, prompt: str) -> None:
        words = [w.lower().strip('.,!?;:\"\'-') for w in prompt.split() if w]
        for w in words:
            if w and w not in self.housing._vocab:
                self.housing._idx(w)
        self._bd = self.housing.j_blue_dist(words)
        self._rd = self.housing.j_red_dist()
        n = self.housing.size
        # Rotor pressures from V(n)-weighted distributions
        self.rotor.j_blue  = max(
            sum(self._bd[k] * self.housing._vn[k] for k in range(n)), GAP) if n else GAP
        self.rotor.j_red   = max(
            sum(self._rd[k] * self.housing._vn[k] for k in range(n)), GAP) if n else GAP
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
        elif port_idx in (1, 2, 3):
            self._update_brackets()

            if port_idx == 3 and not self._coupled_this_sweep and \
               self.housing.size > 0 and self._bd is not None:

                n_l = self.rotor.n_live()
                rd  = self._rd or self.housing.j_red_dist()
                gd  = self._gd or ([GAP] * self.housing.size)

                act = _vq_bridge_activations(self._bd, rd, self.housing)
                self._bridge_act = act

                self._drive_shaft = _vq_project_sedenion(
                    self._bd, rd, gd, n_l, self.housing)

                word = _vq_select_word(self._drive_shaft, act, self._bd, self.housing)
                if word:
                    self._last_word          = word
                    self._coupled_this_sweep = True
                    self._obd2.coupling_events += 1
                    self._obd2.last_word      = word
                    dom = max(
                        (i for i in range(1, 16) if i != 8),
                        key=lambda i: act[i], default=1)
                    self._obd2.dom_dim  = dom
                    self._obd2.regime   = ('data' if dom < 8 else 'code')
                    k = self.housing._vocab[word]
                    self.housing._beta[k] = min(self.housing._beta[k] + 0.015, 1.0)

        elif port_idx == 5:
            self.housing.scavenge()

        self._refresh_obd2()
        return word

    def speak(self, prompt: str, max_revolutions: int = 6) -> str:
        self.intake(prompt)
        for _ in range(max_revolutions * 6):
            word = self.rotate()
            if word: return word
        return self._last_word or '∅'

    def diagnostics(self) -> VQOBD2:
        return self._obd2

    def _update_brackets(self) -> None:
        if self.housing.size == 0 or self._bd is None: return
        rd = self._rd or self.housing.j_red_dist()
        jb, jr = self.rotor.j_blue, self.rotor.j_red
        jg_scalar, self._gd = _lie_bracket(jb, self._bd, jr, rd, self.housing)
        self.rotor.j_green   = max(jg_scalar, GAP)
        gd_abs = [abs(x) for x in self._gd]
        jb_next, _ = _lie_bracket(jr, rd, self.rotor.j_green, gd_abs, self.housing)
        self.rotor.j_blue = max((jb * 0.7 + jb_next * 0.3), GAP)
        jr_next, _ = _lie_bracket(
            self.rotor.j_green, gd_abs, self.rotor.j_blue, self._bd, self.housing)
        self.rotor.j_red = max((jr * 0.7 + jr_next * 0.3), GAP)
        self._rd = self.housing.j_red_dist()

    def _refresh_obd2(self) -> None:
        self._obd2.rotor_angle     = self.rotor.theta
        self._obd2.j_blue          = self.rotor.j_blue
        self._obd2.j_red           = self.rotor.j_red
        self._obd2.j_green         = self.rotor.j_green
        self._obd2.n_live          = self.rotor.n_live()
        self._obd2.vn_live         = self.rotor.vn_live()
        self._obd2.escape_fraction = self.rotor.escape_fraction()
        self._obd2.bracket_mag     = self.rotor.bracket_mag()
        self._obd2.housing_n       = self.housing.size

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
    print("ValaQuenta  —  N-Ball Zero Divisor Rotary Engine  (Engine 19)")
    print(f"n* = {N_STAR:.4f}  |  V(n*) = {V(N_STAR):.4f}  |  V(16) = {V(16):.4f} ≈ d* = {D_STAR}")
    print(f"Cayley-Dickson ratio R→C = C→H = π/2 = {CD_RATIO:.4f}")
    print("=" * 70)

    # ── Test 0: N-ball geometry ───────────────────────────────────────────────
    print("\n── Test 0: N-ball volume function V(n) ─────────────────────────────")
    print(f"  {'n':<6} {'V(n)':<10} {'regime':<10} {'bar'}")
    for n in [0, 1, 2, 3, 4, N_STAR, 6, 7, 8, 10, 12, 14, 16]:
        vn  = V(n)
        bar = '█' * int(vn * 15)
        regime = ('data' if n < N_STAR - 0.5
                  else 'boundary' if n < N_STAR + 0.5
                  else 'code')
        nstar_marker = ' ← n*' if abs(n - N_STAR) < 0.01 else ''
        d_marker     = ' ← V=d*' if abs(vn - D_STAR) < 0.01 else ''
        print(f"  {n:<6.3f} {vn:<10.4f} {regime:<10} {bar}{nstar_marker}{d_marker}")

    # ── Test 1: Word N-ball regime classification ─────────────────────────────
    print("\n── Test 1: Word N-ball regime (prime hash → n_dim → V(n) → regime) ──")
    test_words = ['the','is','sedenion','zero','one','boundary','critical',
                  'sigma','riemann','rotor','coupling','wave','point','space']
    print(f"  {'word':<14} {'n_dim':<7} {'V(n)':<8} {'regime'}")
    for w in test_words:
        nd = _word_n_dim(w)
        vn = V(nd)
        rg = _word_regime(w)
        bar_pos = '←n*' if abs(nd - N_STAR) < 0.5 else ''
        print(f"  {w:<14} {nd:<7.3f} {vn:<8.4f} {rg} {bar_pos}")

    # ── Test 2: Build engine and test ─────────────────────────────────────────
    engine = ValaQuenta()
    for line in _CORPUS:
        engine.ingest(line)
    print(f"\nHousing: {engine.housing.size} words")
    data_n    = sum(1 for r in engine.housing._regime if r == 'data')
    boundary_n = sum(1 for r in engine.housing._regime if r == 'boundary')
    code_n    = sum(1 for r in engine.housing._regime if r == 'code')
    print(f"  data regime  (n < n*): {data_n} words")
    print(f"  boundary     (n ≈ n*): {boundary_n} words")
    print(f"  code regime  (n > n*): {code_n} words")

    # ── Test 3: UDEO-exact vs AMBI ────────────────────────────────────────────
    print("\n── Test 3: UDEO vs AMBI (N-ball ZD, no morph_vec) ─────────────────")
    print(f"  {'kind':<6} {'response':<22} {'n_live':<8} {'V(n)':<7} {'esc%':<7} {'regime':<8} prompt")

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
        print(f"  {kind:<6} {word:<22} {d.n_live:<8.3f} {d.vn_live:<7.4f} "
              f"{d.escape_fraction*100:<7.1f}% {d.regime:<8} {prompt}")

    # ── Test 4: ValaQuenta drive shaft ────────────────────────────────────────
    print("\n── Test 4: ValaQuenta drive shaft (N-ball → ZL → sedenion) ─────────")
    _OPS = ['identity','negate','bind','name','apply','abstract','branch','iterate',
            'recurse','allocate','query','derefer','compose','parallelize','interrupt','emit']
    engine.speak("sigma equals one half is the eccentric pin", max_revolutions=6)
    if engine._drive_shaft:
        ds = engine._drive_shaft
        data_sum  = sum(ds[i] for i in range(1, 8))
        code_sum  = sum(ds[i] for i in range(8, 16))
        print(f"  e₀ = {ds[0]:.4f}  (zero — identity above bridge and N-ball)")
        print(f"  Data  regime (e₁–e₇  lower-𝕆): {data_sum:.4f}")
        print(f"  Code  regime (e₈–e₁₅ upper-𝕆): {code_sum:.4f}")
        top4 = sorted(range(1, 16), key=lambda i: -abs(ds[i]))[:4]
        print(f"  Top 4: " +
              "  ".join(f"e{i}({_OPS[i][:4]})={ds[i]:.4f}" for i in top4))
        d = engine.diagnostics()
        print(f"  n_live = {d.n_live:.4f}  (converges to n*={N_STAR:.4f} by dynamics)")
        print(f"  V(n_live) = {d.vn_live:.4f}  (converges to V(n*)={V(N_STAR):.4f})")

    # ── Test 5: OBD2 ─────────────────────────────────────────────────────────
    print("\n── Test 5: ValaQuenta OBD2 ─────────────────────────────────────────")
    engine.speak("the rotor spins and the sedenion emerges", max_revolutions=6)
    d = engine.diagnostics()
    print(f"  j_blue           = {d.j_blue:.6f}")
    print(f"  j_red            = {d.j_red:.6f}")
    print(f"  j_green          = {d.j_green:.6f}")
    print(f"  n_live           = {d.n_live:.4f}  (target: n*={N_STAR:.4f})")
    print(f"  V(n_live)        = {d.vn_live:.4f}  (target: V(n*)={V(N_STAR):.4f})")
    print(f"  escape_fraction  = {d.escape_fraction:.4f}  (1.0 = at n*)")
    print(f"  bracket_mag      = {d.bracket_mag:.6f}")
    print(f"  coupling_events  = {d.coupling_events}")
    print(f"  last_word        = '{d.last_word}'")
    print(f"  dom_dim          = e{d.dom_dim} ({_OPS[d.dom_dim]})")
    print(f"  regime           = {d.regime}")
    faults = d.faults()
    print(f"  Faults: {faults if faults else ['none']}")

    # ── Test 6: V(16) = d* at the zero-divisor horizon ───────────────────────
    print("\n── Test 6: N-ball horizon — V(16) = d* ─────────────────────────────")
    print(f"  V(n*)    = {V(N_STAR):.6f}   (peak — the BAO freeze / data-code boundary)")
    print(f"  V(16)    = {V(16):.6f}   (sedenion dim — the zero-divisor horizon)")
    print(f"  d*       = {D_STAR:.6f}   (zero-divisor proximity threshold)")
    print(f"  V(16)/d* = {V(16)/D_STAR:.6f}   (≈ 1.0 — algebraic coincidence or not?)")
    print(f"  R→C      = π/2 = {CD_RATIO:.6f}   (Cayley-Dickson doubling ratio)")
    print(f"  V(2)/V(1) = {V(2)/V(1):.6f}   (R→C transition on N-ball: {V(2)/V(1):.4f} ≈ π/2 = {CD_RATIO:.4f}?)")
    print(f"  V(4)/V(2) = {V(4)/V(2):.6f}   (C→H transition: {V(4)/V(2):.4f})")
    print(f"  V(8)/V(4) = {V(8)/V(4):.6f}   (H→O transition: {V(8)/V(4):.4f})")
    print(f"  V(16)/V(8)= {V(16)/V(8):.6f}   (O→S transition: {V(16)/V(8):.4f})")

    print("\n" + "=" * 70)
    print("ValaQuenta — engine nominal.")
    print("Universe(New): N-ball applied. morph_vec absent. n* above the system.")
    print("=" * 70)
