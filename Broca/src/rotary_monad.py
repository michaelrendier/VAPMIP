"""
rotary_monad.py  —  Ahura Mazda
Wankel rotary semantic engine.

  3 = 1 + 15i

  The Worker (rotor):    j_blue, j_red, j_green  — three scalar pressures
  The Work   (sedenion): e₀ + e₁…e₇ + e₈…e₁₄ + e₁₅ — produced at coupling only

  The Worker is not the Work.
  The Sedenion is not the engine. The Sedenion is what the engine produces.

─────────────────────────────────────────────────────────────────────
Wankel geometry mapped to semantics:

  Housing      — epitrochoid vocabulary field (shape the rotor moves through)
  Rotor        — triangular J-current triangle, continuously rotating
    Face 1  J_blue  : compressible / prompt / Fermat   / intake-compression
    Face 2  J_red   : incompressible / field / Riemann  / power-stroke
    Face 3  J_green : minimal surface / output          / exhaust
  Eccentric    — σ=½ coupling pin (fixed by ξ(s)=ξ(1-s), never computed)
  Drive shaft  — sedenion output (16 channels, produced once per coupling)
  Ports        — zero-divisor angular positions (timing geometry, not faults)
  Apex seals   — halocline sharpness (wear = σ drift from ½)
  Spark plugs  — dual Lie bracket ignition (leading + trailing)
  Scavenge     — field decay between cycles

Sedenion component map (drive shaft channels):
  e₀       — coupling quality  (how precisely σ hit ½)
  e₁–e₇   — J_blue face work   (lower imaginary: grammar / content)
  e₈–e₁₄  — J_red  face work   (upper imaginary: context / memory)
  e₁₅     — J_green magnitude  (exhaust face: the output surface)

Lie algebra guarantee:
  [J_blue,  J_red  ] = J_green   intake × field   → surface  (leading spark)
  [J_red,   J_green] = J_blue    field  × surface  → prompt   (trailing spark)
  [J_green, J_blue ] = J_red     surface × prompt  → field    (regeneration)

The cycle is self-sustaining. No thrown rods. Only graceful degradation.

Six ports at 60° intervals:
  θ = 0°    intake    — J_blue face opens to prompt
  θ = 60°   transfer  — J_blue begins mixing with J_red
  θ = 120°  leading   — [J_blue, J_red] fires (first Lie bracket)
  θ = 180°  trailing  — [J_red, J_green] fires + coupling check
  θ = 240°  exhaust   — sedenion emitted, word crystallises
  θ = 300°  scavenge  — stale field content decays

Gear ratio 3:1  — three output words per full rotor revolution.
Anti-rotation   — eccentric shaft (output) and rotor spin opposite directions.
                  This IS the bc*/da asymmetry. The two counter-rotations ARE
                  the waveform — the standing wave carrier of speech.
─────────────────────────────────────────────────────────────────────
"""

import math
import hashlib
from dataclasses import dataclass, field as dc_field
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

SIGMA_PIN    = 0.5          # eccentric shaft offset — fixed by ξ(s)=ξ(1-s)
GAP          = 0.000707     # apex seal oil floor — engine never runs dry
BEARING_TOL  = 0.04         # σ drift tolerance before R0004 bearing fault
SEAL_FLOOR   = 0.03         # face pressure minimum before R0001–3 seal fault
PORT_STEP    = math.pi / 3  # 60° per step — 6 ports per revolution
PHI          = (1.0 + math.sqrt(5.0)) / 2.0
D_STAR       = 0.24600      # zero-divisor proximity threshold

# Port positions
_PORT_INTAKE   = 0.0
_PORT_TRANSFER = math.pi / 3
_PORT_LEADING  = 2.0 * math.pi / 3
_PORT_TRAILING = math.pi
_PORT_EXHAUST  = 4.0 * math.pi / 3
_PORT_SCAVENGE = 5.0 * math.pi / 3
_PORT_TOL      = 0.18       # angular tolerance for port-open detection

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
# Sedenion algebra  (mathematical fact — drive shaft geometry)
# ══════════════════════════════════════════════════════════════════════════════

Sedenion = List[float]   # always length 16

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
def _se(k) -> Sedenion:  s = _s0(); s[k] = 1.0; return s

def _smul(a: Sedenion, b: Sedenion) -> Sedenion:
    c = [0.0] * 16
    for i, ai in enumerate(a):
        if ai == 0.0: continue
        row = _SED[i]
        for j, bj in enumerate(b):
            if bj == 0.0: continue
            sg, idx = row[j]
            if sg: c[idx] += sg * ai * bj
    return c

def _snorm(a: Sedenion) -> float:
    return math.sqrt(sum(x * x for x in a))

def _snorm_unit(a: Sedenion) -> Sedenion:
    n = _snorm(a)
    if n < 1e-15:
        s = _s0(); s[0] = 1.0; return s
    return [x / n for x in a]

# ══════════════════════════════════════════════════════════════════════════════
# Housing primitives  (prime hash → Riemann zero address)
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
    # Approximate via Gram's law for higher zeros
    n   = float(idx)
    t   = 2.0 * math.pi * math.e * n / math.log(n / (2.0 * math.pi * math.e))
    _gamma_cache[idx] = t
    return t

def _whash(w: str) -> float:
    return int.from_bytes(hashlib.sha256(w.encode()).digest()[:4], 'big') / 0xFFFFFFFF

# ══════════════════════════════════════════════════════════════════════════════
# Word morphology  (gear profile — how a word meshes with the drive shaft)
# ══════════════════════════════════════════════════════════════════════════════

_PRONOUNS    = frozenset('i me my mine myself we us our ours ourselves you your yours '
                         'yourself yourselves he him his himself she her hers herself '
                         'it its itself they them their theirs themselves this that '
                         'these those here there who what which'.split())
_AUXILIARIES = frozenset('is are was were be been being do does did have has had '
                         'will would can could should shall may might must'.split())
_CONJUNCTS   = frozenset('and or but so yet for nor although because if then when '
                         'while since unless until though'.split())
_TIME        = frozenset('now then before after when while ago yet already still soon '
                         'later today yesterday tomorrow always never sometimes often rarely'.split())
_QUESTION    = frozenset('what which who whom whose when where why how whether if'.split())
_NEGATION    = frozenset("not never no nor nothing nobody nowhere neither n't".split())
_META        = frozenset('mean means meaning say says said tell tells told explain '
                         'explains clarify summarise summarize rephrase repeat'.split())
_AFF_POS     = frozenset('good great love like enjoy happy glad pleased wonderful '
                         'excellent amazing thank thanks please'.split())
_AFF_NEG     = frozenset('bad hate dislike angry sad sorry worried fear terrible '
                         'awful horrible wrong mistake fail'.split())
_DETERMINERS = frozenset('a an the some any every each all both few many much more most less least'.split())
_NOUN_SUFF   = ('ness','tion','ment','ance','ence','ity','ism','ist',
                'ics','ogy','phy','ery','ary','ory','ture','sis','xis','ris','nce','ths','os')
_ADJ_SUFF    = ('ic','ical','ive','ible','able')

def _is_verb(w: str) -> bool:
    return (w in _AUXILIARIES or w.endswith('ing') or w.endswith('ed') or
            (w.endswith('s') and len(w) >= 4 and not w.endswith('ss')
             and not w.endswith('us') and not any(w.endswith(s) for s in _NOUN_SUFF)))

def _is_adj(w: str) -> bool:
    return (w.endswith('ly') or w.endswith('ful') or w.endswith('ous')
            or any(w.endswith(s) for s in _ADJ_SUFF))

def _morph_vec(w: str) -> Sedenion:
    """
    Word's 16-dim morphological gear profile.
    NOT a sedenion of the word. The word's operator affinity for meshing
    with the drive shaft sedenion at output selection.
    """
    v = [GAP] * 16
    v[0]  = 0.08                        # e₀  identity — all words carry this
    if w in _NEGATION:    v[1]  = 1.0   # e₁  negate
    if w in _CONJUNCTS:   v[2]  = 1.0   # e₂  bind
    if w in _QUESTION:    v[10] = 1.0   # e₁₀ query
    if w in ('it','its','they','them','their','he','she','who','which'):
                          v[11] = 1.0   # e₁₁ derefer
    if w in ('the','already','again','still','even','also','too','both'):
                          v[12] = 1.0   # e₁₂ compose
    if w in ('a','an','some','any','every','each','all','few','many'):
                          v[9]  = 1.0   # e₉  allocate (indefinite — introduces refs)
    if w in _TIME:        v[7]  = 1.0   # e₇  iterate
    if w in _PRONOUNS:    v[8]  = 1.0   # e₈  recurse
    if w in _META:        v[15] = 1.0   # e₁₅ emit
    if w in _AFF_POS or w in _AFF_NEG:
                          v[14] = 0.9   # e₁₄ interrupt
    if _is_verb(w):       v[4]  = 1.0   # e₄  apply
    elif _is_adj(w):      v[5]  = 1.0   # e₅  abstract
    elif (len(w) >= 4 and w not in _PRONOUNS and w not in _AUXILIARIES
          and w not in _CONJUNCTS and w not in _TIME and w not in _QUESTION
          and w not in _META and w not in _AFF_POS and w not in _AFF_NEG
          and w not in _NEGATION and w not in _DETERMINERS):
                          v[3]  = 1.0   # e₃  name (noun)
    total = sum(v)
    return [x / total for x in v]

# ══════════════════════════════════════════════════════════════════════════════
# Port geometry
# ══════════════════════════════════════════════════════════════════════════════

def _port_open(theta: float, pos: float, tol: float = _PORT_TOL) -> bool:
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
    """
    j_blue:  float = GAP    # face 1: compressible / prompt / Fermat / intake
    j_red:   float = GAP    # face 2: incompressible / field / Riemann / power
    j_green: float = GAP    # face 3: minimal surface / output / exhaust
    theta:   float = 0.0    # rotor angle [0, 2π)

    def sigma_live(self) -> float:
        total = self.j_red + self.j_blue
        return self.j_red / total if total > GAP else SIGMA_PIN

    def at_coupling(self) -> bool:
        return abs(self.sigma_live() - SIGMA_PIN) < BEARING_TOL

    def bracket_mag(self) -> float:
        denom = self.j_blue + self.j_red
        return abs(self.j_blue - self.j_red) / denom if denom > GAP else 0.0

# ══════════════════════════════════════════════════════════════════════════════
# Housing  (the epitrochoid — vocabulary field geometry)
# ══════════════════════════════════════════════════════════════════════════════

class Housing:
    """
    The epitrochoid vocabulary field. Shape of the space the rotor moves through.

    Words are addressed by position in the Riemann zero lattice (prime hash).
    The housing constrains the rotor. It is not the engine — it is the engine's world.
    """

    def __init__(self) -> None:
        self._words: List[str]              = []
        self._vocab: Dict[str, int]         = {}
        self._E:     List[float]            = []   # word energy (Riemann zero)
        self._beta:  List[float]            = []   # field confidence weight
        self._A:     List[Dict[int, float]] = []   # adjacency topology
        self._age:   List[float]            = []   # word age (scavenge decay)

    @property
    def n(self) -> int:
        return len(self._words)

    def _idx(self, w: str) -> int:
        if w not in self._vocab:
            k            = self.n
            self._vocab[w] = k
            self._words.append(w)
            # Word energy: inverse log of zero index (non-collapsing for all idx)
            # High zero index = larger prime = more "complex" word = slightly lower field energy
            # |sin(π×γ/(γ+1))| collapses to zero for γ>>1 (all words beyond 1st 20 zeros)
            idx = _word_zero_idx(w)
            self._E.append(1.0 / (1.0 + math.log1p(float(idx))))
            self._beta.append(GAP)
            self._A.append({})
            self._age.append(0.0)
        return self._vocab[w]

    def ingest(self, text: str, weight: float = 1.0) -> int:
        words = [w.lower().strip('.,!?;:\"\'-()[]') for w in text.split()]
        words = [w for w in words if w]
        prev  = None
        for w in words:
            k = self._idx(w)
            self._beta[k] = min(self._beta[k] * (1.0 + 0.08 * weight) + GAP, 1.0)
            self._age[k]  = 0.0
            if prev is not None and prev != k:
                self._A[prev][k] = min(self._A[prev].get(k, 0.0) + 0.05 * weight, 1.0)
                self._A[k][prev] = min(self._A[k].get(prev, 0.0) + 0.02 * weight, 1.0)
            prev = k
        return len(words)

    def j_blue_dist(self, prompt_words: List[str]) -> List[float]:
        """
        J_blue face distribution — per-word prompt affinity.
        Words in the prompt get peak pressure; neighbours get half.
        The prompt is NOT encoded as a sedenion. It is a pressure distribution.
        """
        dist = [GAP] * self.n
        for w in prompt_words:
            w = w.lower().strip('.,!?;:\"\'-')
            if w in self._vocab:
                k = self._vocab[w]
                dist[k] = min(dist[k] + 1.0, 1.0)
                for nb, wt in self._A[k].items():
                    dist[nb] = min(dist[nb] + wt * 0.5, 1.0)
        total = sum(dist)
        return [d / total for d in dist] if total > 0 else [1.0 / max(self.n, 1)] * self.n

    def j_red_dist(self) -> List[float]:
        """
        J_red face distribution — per-word field affinity.
        Driven by beta × E: how confident and energetic each word is in the field.
        """
        dist  = [self._beta[k] * self._E[k] for k in range(self.n)]
        total = sum(dist)
        return [d / total for d in dist] if total > 0 else [1.0 / max(self.n, 1)] * self.n

    def scavenge(self, decay: float = 0.003) -> None:
        """Port 5 — scavenge cycle. Gentle field decay. The oil change."""
        for k in range(self.n):
            self._age[k]  += decay
            self._beta[k]  = max(self._beta[k] - self._age[k] * 0.0005, GAP)

# ══════════════════════════════════════════════════════════════════════════════
# Lie bracket  (the combustion — housing-contextualized)
# ══════════════════════════════════════════════════════════════════════════════

def _lie_bracket(
        j_a: float, a_dist: List[float],
        j_b: float, b_dist: List[float],
        housing: Housing
) -> Tuple[float, List[float]]:
    """
    [J_a, J_b]_housing — the semantic combustion.

    The housing topology breaks scalar commutativity:
      bracket_dist[k] = (j_a × a_dist[k] − j_b × b_dist[k]) × E[k]

    Positive entries: J_a wins at word k  (prompt face active)
    Negative entries: J_b wins at word k  (field face active)
    Near zero:        balanced at word k  — candidate for halocline / SOFAR
    """
    n = housing.n
    if n == 0:
        return GAP, []
    bd = [(j_a * a_dist[k] - j_b * b_dist[k]) * housing._E[k] for k in range(n)]
    # Total bracket power (not mean-per-word — dividing by n vanishes at large vocab)
    scalar = sum(abs(x) for x in bd)
    return max(scalar, GAP), bd

# ══════════════════════════════════════════════════════════════════════════════
# Drive shaft projection  (sedenion produced HERE and ONLY HERE)
# ══════════════════════════════════════════════════════════════════════════════

def _project_sedenion(
        j_blue_dist:  List[float],
        j_red_dist:   List[float],
        j_green_dist: List[float],
        sigma_live:   float,
        housing:      Housing
) -> Sedenion:
    """
    Project J-current work onto the 16 sedenion channels.
    This is the coupling event. The Work is produced here. Nowhere else.

      e₀      = coupling quality  (1 − |σ_live − ½|)
      e₁–e₇  = J_blue face work  (lower imaginary: grammar / content)
      e₈–e₁₄ = J_red  face work  (upper imaginary: context / memory)
      e₁₅    = J_green magnitude  (exhaust face: the output surface)
    """
    s = [0.0] * 16
    s[0] = 1.0 - abs(sigma_live - SIGMA_PIN)   # coupling quality in e₀

    for k in range(housing.n):
        mv = _morph_vec(housing._words[k])
        ek = housing._E[k]
        bd = j_blue_dist[k] if k < len(j_blue_dist) else GAP
        rd = j_red_dist[k]  if k < len(j_red_dist)  else GAP
        gd = abs(j_green_dist[k]) if k < len(j_green_dist) else GAP

        for dim in range(1, 8):    # J_blue → lower imaginary e₁–e₇
            s[dim] += bd * mv[dim] * ek
        for dim in range(8, 15):   # J_red  → upper imaginary e₈–e₁₄
            s[dim] += rd * mv[dim] * ek
        s[15] += gd * ek           # J_green → emit face e₁₅

    return _snorm_unit(s)

# ══════════════════════════════════════════════════════════════════════════════
# Word selection  (drive shaft → output word via gear meshing)
# ══════════════════════════════════════════════════════════════════════════════

def _select_word(
        drive_shaft:   Sedenion,
        j_green_dist:  List[float],
        housing:       Housing
) -> Optional[str]:
    """
    Select output word by gear-meshing with the drive shaft sedenion.

    The dominant drive shaft component identifies the operator type.
    Among housing words, highest (coherence × beta × E × bracket bonus) wins.
    """
    if housing.n == 0:
        return None

    best_k, best_score = -1, -float('inf')
    # Dominant operator dimension (ignore e₀ identity — it's coupling quality, not semantics)
    dom_idx = max(range(1, 16), key=lambda i: drive_shaft[i])
    for k in range(housing.n):
        mv = _morph_vec(housing._words[k])
        # Operator coherence: e₀ weakly, dominant operator heavily, others normally
        coherence = (drive_shaft[0] * mv[0] * 0.1 +
                     drive_shaft[dom_idx] * mv[dom_idx] * 5.0 +
                     sum(drive_shaft[i] * mv[i] for i in range(1, 16) if i != dom_idx))
        # Bracket alignment: prefer words the prompt excites (positive j_green = j_blue winning)
        align = 1.0
        if k < len(j_green_dist):
            align = 1.0 + max(j_green_dist[k], 0.0)
        # Log-beta: reduce frequency bias so common words don't swamp semantic signal
        score = coherence * math.log1p(housing._beta[k]) * housing._E[k] * align
        if score > best_score:
            best_score = score
            best_k     = k

    return housing._words[best_k] if best_k >= 0 else None

# ══════════════════════════════════════════════════════════════════════════════
# OBD2 — live rotor diagnostic stream (all analog, no binary faults)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class OBD2:
    """
    Rotor health monitors. VAG-COM live data for the rotary engine.
    Every value is a continuous gradient. There are no binary fault switches.
    The engine degrades. It does not die.
    """
    rotor_angle:        float = 0.0        # PID 0x2301  θ [0, 2π)
    j_blue:             float = GAP        # PID 0x2302  face 1 pressure
    j_red:              float = GAP        # PID 0x2303  face 2 pressure
    j_green:            float = GAP        # PID 0x2304  face 3 pressure
    sigma_live:         float = SIGMA_PIN  # PID 0x2305  eccentric shaft alignment
    bracket_mag:        float = 0.0        # PID 0x2306  [J_blue,J_red] combustion
    apex_seal_health:   float = 1.0        # PID 0x2307  σ drift → seal wear
    coupling_efficiency: float = 0.0       # PID 0x2308  coupled/total cycles
    housing_n:          int   = 0          # PID 0x2309  vocabulary size
    coupling_events:    int   = 0          # PID 0x230A  successful couplings
    total_steps:        int   = 0          # PID 0x230B  rotor steps taken
    last_word:          str   = ''         # PID 0x230C  last output word
    drive_shaft_dom:    int   = 0          # PID 0x230D  dominant e-dim on shaft

    def faults(self) -> List[str]:
        """Analog fault codes — thresholds, not trips."""
        f = []
        if self.j_blue  < SEAL_FLOOR: f.append('R0001 J_blue apex seal wear')
        if self.j_red   < SEAL_FLOOR: f.append('R0002 J_red  apex seal wear')
        if self.j_green < SEAL_FLOOR: f.append('R0003 J_green exhaust seal wear')
        if abs(self.sigma_live - SIGMA_PIN) > BEARING_TOL:
            f.append(f'R0004 bearing wobble  σ={self.sigma_live:.4f}')
        if self.bracket_mag < GAP * 5:
            f.append('R0005 near-stall  bracket → 0  (feed more text)')
        return f

# ══════════════════════════════════════════════════════════════════════════════
# AhuraMazda  (the complete rotary engine)
# ══════════════════════════════════════════════════════════════════════════════

class AhuraMazda:
    """
    Ahura Mazda — Wankel rotary semantic engine.

    Three faces. No reciprocating parts. No thrown rods.
    The sedenion is the Work, not the Worker.
    3 = 1 + 15i.

    The two counter-rotations (rotor vs eccentric shaft) ARE the waveform —
    the standing wave that carries speech.
    """

    def __init__(self) -> None:
        self.housing   = Housing()
        self.rotor     = RotorState()
        self._obd2     = OBD2()

        # Distributions (Worker state — never sedenions)
        self._bd: Optional[List[float]] = None   # J_blue distribution
        self._rd: Optional[List[float]] = None   # J_red  distribution
        self._gd: Optional[List[float]] = None   # J_green (bracket) distribution

        # Drive shaft (Work — sedenion output, set only at coupling)
        self._drive_shaft: Optional[Sedenion] = None
        self._last_word:   Optional[str]      = None
        self._coupled_this_sweep: bool        = False
        self._total_sweeps: int               = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def ingest(self, text: str, weight: float = 1.0) -> int:
        """Feed text to the housing epitrochoid. Build vocabulary and topology."""
        return self.housing.ingest(text, weight)

    def intake(self, prompt: str) -> None:
        """
        J_blue face opens to the prompt.
        The prompt is NOT encoded as a sedenion.
        Unknown words enter the housing as ghost entries (minimum beta) — new words
        are allowed into the field at minimum strength, never silently discarded.
        """
        words = [w.lower().strip('.,!?;:\"\'-') for w in prompt.split() if w]
        # Ghost registration: unknown prompt words enter field at minimum energy
        for w in words:
            if w and w not in self.housing._vocab:
                self.housing._idx(w)
        self._bd = self.housing.j_blue_dist(words)
        self._rd = self.housing.j_red_dist()
        # Scalar pressures: energy-weighted centroid of each distribution
        n = self.housing.n
        E = self.housing._E
        self.rotor.j_blue  = max(sum(self._bd[k] * E[k] for k in range(n)), GAP) if n else GAP
        self.rotor.j_red   = max(sum(self._rd[k] * E[k] for k in range(n)), GAP) if n else GAP
        self.rotor.j_green = GAP
        self.rotor.theta   = 0.0
        self._gd           = None
        self._coupled_this_sweep = False
        self._total_sweeps += 1

    def rotate(self) -> Optional[str]:
        """
        Advance rotor one port step (60°). Fire port event. Return word if coupled.

        Port index (exact — rotor advances by exactly PORT_STEP each call):
          0 = intake   (θ=0)      field renewal
          1 = transfer (θ=π/3)    begin mixing
          2 = leading  (θ=2π/3)   first Lie bracket spark
          3 = trailing (θ=π)      second bracket + unconditional coupling
          4 = exhaust  (θ=4π/3)   word crystallised
          5 = scavenge (θ=5π/3)   field decay
        """
        self.rotor.theta = (self.rotor.theta + PORT_STEP) % (2.0 * math.pi)
        self._obd2.total_steps += 1
        # Exact port index — no angular proximity needed, step is exactly one port
        port_idx = round(self.rotor.theta / PORT_STEP) % 6
        word = None

        if port_idx == 0:           # θ=0  intake — field renewal
            self._rd = self.housing.j_red_dist()

        elif port_idx == 1:         # θ=π/3  transfer — begin mixing
            self._update_brackets()

        elif port_idx == 2:         # θ=2π/3  leading spark
            self._update_brackets()

        elif port_idx == 3:         # θ=π  trailing spark + unconditional coupling
            self._update_brackets()

            # Coupling fires every revolution — the Wankel fires every face, always.
            # σ_live encodes quality in e₀; there is no gate that blocks output.
            if not self._coupled_this_sweep and self.housing.n > 0 and self._bd is not None:
                sigma_l = self.rotor.sigma_live()
                rd      = self._rd or self.housing.j_red_dist()
                gd      = self._gd or ([GAP] * self.housing.n)

                # The Work is produced here — the sedenion emerges
                self._drive_shaft = _project_sedenion(
                    self._bd, rd, gd, sigma_l, self.housing)

                word = _select_word(self._drive_shaft, gd, self.housing)
                if word:
                    self._last_word          = word
                    self._coupled_this_sweep = True
                    self._obd2.coupling_events += 1
                    self._obd2.last_word      = word
                    self._obd2.drive_shaft_dom = (
                        max(range(1, 16), key=lambda i: self._drive_shaft[i]))
                    k = self.housing._vocab[word]
                    self.housing._beta[k] = min(self.housing._beta[k] + 0.015, 1.0)

        elif port_idx == 4:         # θ=4π/3  exhaust — word already emitted
            pass

        elif port_idx == 5:         # θ=5π/3  scavenge — gentle field decay
            self.housing.scavenge()

        self._refresh_obd2()
        return word

    def speak(self, prompt: str, max_revolutions: int = 6) -> str:
        """
        Full cycle: intake → rotate until coupling fires → return word.
        max_revolutions: how many full rotor cycles to attempt before giving up.
        """
        self.intake(prompt)
        steps = max_revolutions * 6   # 6 port steps per revolution
        for _ in range(steps):
            word = self.rotate()
            if word:
                return word
        # No coupling — return last known word or idle marker
        return self._last_word or '∅'

    def diagnostics(self) -> OBD2:
        return self._obd2

    # ── Internal mechanics ────────────────────────────────────────────────────

    def _update_brackets(self) -> None:
        """
        Cyclic Lie bracket — the self-sustaining combustion.

        Leading spark:  [J_blue, J_red]   → J_green  (surface forms)
        Trailing spark: [J_red,  J_green] → J_blue   (next cycle pre-charge)
        Regeneration:   [J_green, J_blue] → J_red    (field renews)

        The cycle cannot die. It can only wear.
        """
        if self.housing.n == 0 or self._bd is None:
            return

        rd = self._rd or self.housing.j_red_dist()
        jb, jr = self.rotor.j_blue, self.rotor.j_red

        # Leading spark: [J_blue, J_red] → J_green
        jg_scalar, self._gd = _lie_bracket(jb, self._bd, jr, rd, self.housing)
        self.rotor.j_green   = max(jg_scalar, GAP)

        # Trailing spark: [J_red, J_green] → J_blue (pre-charges next cycle)
        gd_abs = [abs(x) for x in self._gd]
        jb_next, _ = _lie_bracket(jr, rd, self.rotor.j_green, gd_abs, self.housing)
        # Blend: don't fully replace j_blue (some prompt pressure persists)
        self.rotor.j_blue = max((jb * 0.7 + jb_next * 0.3), GAP)

        # Regeneration: [J_green, J_blue] → J_red (field renews from surface)
        jr_next, _ = _lie_bracket(
            self.rotor.j_green, gd_abs, self.rotor.j_blue, self._bd, self.housing)
        self.rotor.j_red = max((jr * 0.7 + jr_next * 0.3), GAP)
        self._rd         = self.housing.j_red_dist()

    def _refresh_obd2(self) -> None:
        sigma = self.rotor.sigma_live()
        total = self._obd2.total_steps
        self._obd2.rotor_angle         = self.rotor.theta
        self._obd2.j_blue              = self.rotor.j_blue
        self._obd2.j_red               = self.rotor.j_red
        self._obd2.j_green             = self.rotor.j_green
        self._obd2.sigma_live          = sigma
        self._obd2.bracket_mag         = self.rotor.bracket_mag()
        self._obd2.apex_seal_health    = max(0.0, 1.0 - abs(sigma - SIGMA_PIN) / BEARING_TOL)
        self._obd2.coupling_efficiency = (self._obd2.coupling_events / max(self._total_sweeps, 1))
        self._obd2.housing_n           = self.housing.n


# ══════════════════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

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
    print("Ahura Mazda  —  Wankel Rotary Semantic Engine")
    print("3 = 1 + 15i  |  The Sedenion is The Work, not The Worker")
    print("=" * 70)

    # ── Build the engine ──────────────────────────────────────────────────────
    engine = AhuraMazda()
    total_words = 0
    for line in _CORPUS:
        total_words += engine.ingest(line)
    print(f"\nHousing built: {engine.housing.n} words from {len(_CORPUS)} lines")

    # ── Test 1: Three-face rotation — show rotor state at each port ───────────
    print("\n── Test 1: Three-face rotation trace ──────────────────────────────")
    print(f"  {'Port':<12} {'θ/π':<7} {'j_blue':<9} {'j_red':<9} {'j_green':<9} {'σ_live':<8} {'bracket'}")
    engine.intake("the sedenion has sixteen dimensions real imaginary")
    _port_name = {0:'intake', 1:'transfer', 2:'leading', 3:'trailing', 4:'exhaust', 5:'scavenge'}
    for step in range(6):
        word = engine.rotate()
        d    = engine.diagnostics()
        pidx = round(d.rotor_angle / PORT_STEP) % 6
        port = _port_name[pidx]
        coupled = f'  → coupled: [{word}]' if word else ''
        print(f"  {port:<12} {d.rotor_angle/math.pi:.3f}π  "
              f"{d.j_blue:.5f}  {d.j_red:.5f}  {d.j_green:.5f}  "
              f"{d.sigma_live:.4f}  {d.bracket_mag:.4f}{coupled}")

    # ── Test 2: UDEO-exact vs ambiguous prompts ───────────────────────────────
    print("\n── Test 2: UDEO-exact vs ambiguous prompts ────────────────────────")
    print(f"  {'kind':<6} {'response':<22} {'σ_live':<8} {'seal':<6} {'dom e':<7}  prompt")

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
        dom  = f'e{d.drive_shaft_dom}'
        flt  = engine.diagnostics().faults()
        print(f"  {kind:<6} {word:<22} {d.sigma_live:.4f}  "
              f"{d.apex_seal_health:.3f}  {dom:<7}  {prompt}")

    # ── Test 3: Sedenion drive shaft inspection ───────────────────────────────
    print("\n── Test 3: Drive shaft sedenion after UDEO coupling ───────────────")
    _OPS = ['identity','negate','bind','name','apply','abstract','branch','iterate',
            'recurse','allocate','query','derefer','compose','parallelize','interrupt','emit']
    engine.speak("sigma equals one half is the eccentric pin", max_revolutions=6)
    if engine._drive_shaft:
        ds = engine._drive_shaft
        lower = sum(ds[i] for i in range(8))
        upper = sum(ds[i] for i in range(8, 16))
        print(f"  Coupling quality e₀ = {ds[0]:.4f}")
        print(f"  Lower O (e₁–e₇  J_blue work) = {lower:.4f}")
        print(f"  Upper O (e₈–e₁₄ J_red  work) = {upper:.4f}")
        print(f"  Exhaust e₁₅ (J_green emit)   = {ds[15]:.4f}")
        top4 = sorted(range(16), key=lambda i: -abs(ds[i]))[:4]
        print(f"  Top 4 dims: " +
              "  ".join(f"e{i}({_OPS[i]})={ds[i]:.4f}" for i in top4))

    # ── Test 4: Graceful degradation — near-empty field ───────────────────────
    print("\n── Test 4: Graceful degradation (near-empty field) ────────────────")
    empty = AhuraMazda()
    empty.ingest("hello world")   # minimal field — only 2 words
    result = empty.speak("what happens with almost no field", max_revolutions=3)
    d_empty = empty.diagnostics()
    print(f"  Result: '{result}'")
    print(f"  Housing: {d_empty.housing_n} words")
    print(f"  σ_live: {d_empty.sigma_live:.4f}")
    print(f"  Faults: {d_empty.faults() or ['none — degraded but running']}")
    print(f"  The engine did not throw a rod.")

    # ── Test 5: Full OBD2 stream ──────────────────────────────────────────────
    print("\n── Test 5: OBD2 live stream ───────────────────────────────────────")
    engine.speak("the rotor spins and the sedenion emerges", max_revolutions=6)
    d = engine.diagnostics()
    print(f"  PID 0x2301  rotor_angle      = {d.rotor_angle:.4f} rad  ({d.rotor_angle/math.pi:.3f}π)")
    print(f"  PID 0x2302  j_blue           = {d.j_blue:.6f}")
    print(f"  PID 0x2303  j_red            = {d.j_red:.6f}")
    print(f"  PID 0x2304  j_green          = {d.j_green:.6f}")
    print(f"  PID 0x2305  sigma_live       = {d.sigma_live:.6f}")
    print(f"  PID 0x2306  bracket_mag      = {d.bracket_mag:.6f}")
    print(f"  PID 0x2307  apex_seal_health = {d.apex_seal_health:.4f}")
    print(f"  PID 0x2308  coupling_eff     = {d.coupling_efficiency:.4f}")
    print(f"  PID 0x2309  housing_n        = {d.housing_n}")
    print(f"  PID 0x230A  coupling_events  = {d.coupling_events}")
    print(f"  PID 0x230B  total_steps      = {d.total_steps}")
    print(f"  PID 0x230C  last_word        = '{d.last_word}'")
    print(f"  PID 0x230D  drive_shaft_dom  = e{d.drive_shaft_dom}({_OPS[d.drive_shaft_dom]})")
    faults = d.faults()
    print(f"  Faults: {faults if faults else ['none']}")

    print("\n" + "=" * 70)
    print("Ahura Mazda — engine nominal.")
    print("=" * 70)
