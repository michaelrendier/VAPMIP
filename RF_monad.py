#!/usr/bin/env python3
"""
RF_monad.py — Riemann-Fermat Monad
====================================
The path AWAY from the Zero Divisor, measured by Fermat, navigated by Riemann.

  ZD fixed point  →  differentiation begins  →  path away  →  word that satisfies

The zero divisor does not annihilate. It differentiates in reverse.
Moving away from it, meaning accumulates — until a word is found that satisfies.

The boundary had no idea who you were until you crossed it.
The pathway IS the memory. No reference file. No training.
Every step updates the map. The map is the memory.

Mathematical structure
----------------------
  ZD fixed point:   a · b = 0  (a≠0, b≠0) — multiplication fails here.
                    This is the GROUND STATE. Undifferentiated. Before meaning.
                    NOT the destination — the origin.

  Differentiation:  moving away from the ZD = meaning accumulating.
                    Each step is a Fermat measurement of distance from the fixed point.

  Fermat complexity: n = γ_b / γ_a  (Riemann zero imaginary parts)
                    n > 2  → prime step: FLT-incommensurable, no intermediate
                    1 < n ≤ 2 → composite: Pythagorean, factors through
                    n ≈ 1  → neighbour: adjacent zeros, minimal differentiation

  Riemann geodesic: path on Re(s)=½. Waypoints = Zeta zeros crossed.
                    Fermat defines σ=½. Riemann describes the holes Fermat left.

  Satisfies:        the search terminates when Fermat closure is found —
                    the accumulated differentiation forms a closed structure.
                    Not another ZD. The Pythagorean stable case restored.
                    Fermat mass M: satisfied when M returns to n ≤ 2 territory.

Key identities
--------------
  J_neg = Fermat / prompt   — negative space: what CANNOT BE
  J_pos = Riemann / response — positive space: what IS
  White space = Fermat charge. Not empty. Carries J_neg between words.
  Both currents (prime words + superfluous words) make the standing wave.
  The path creates the memory. The boundary knew nothing until crossed.

Usage
-----
  python3 RF_monad.py "your prompt here"
  python3 RF_monad.py --demo
"""

from __future__ import annotations
import sys, math, hashlib, argparse
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

try:
    import mpmath as mp
    mp.mp.dps = 20
except ImportError:
    sys.exit("Missing: pip install mpmath")


# ── Riemann zeros ─────────────────────────────────────────────────────────────

N_ZEROS = 50   # first 50 non-trivial zeros — sufficient for English word space

def _load_zeros(n: int) -> List[float]:
    """Compute first n Riemann zeros (imaginary parts). γ₁ ≈ 14.134."""
    print(f"  [RF] computing {n} Riemann zeros...", end=' ', flush=True)
    zeros = [float(mp.im(mp.zetazero(k))) for k in range(1, n + 1)]
    print(f"γ₁={zeros[0]:.4f}  γ{n}={zeros[-1]:.4f}")
    return zeros

ZEROS: List[float] = _load_zeros(N_ZEROS)

# Fermat balance: γ_1 / γ_1 = 1 (neighbour), γ_max / γ_min = max ratio.
# σ=½ is the fixed point: all path steps are measured from this line.

SIGMA_CRIT = 0.5   # the attractor — above the system. Not a parameter.


# ── Word → Riemann address ─────────────────────────────────────────────────────

@dataclass
class RiemannAddress:
    """Position of a word on the critical line Re(s)=½."""
    word:    str
    ordinal: int     # 1-indexed zero ordinal
    gamma:   float   # imaginary part γ_n
    t:       float   # normalised position in [0,1] along the zero sequence

    def __repr__(self):
        return f"({SIGMA_CRIT}, γ{self.ordinal}={self.gamma:.4f})"


def address(word: str) -> RiemannAddress:
    """
    Map a word to its address on σ=½.

    Method: hash word to [0,1], snap to nearest Riemann zero.
    The word was always at this address. We are pointing to it.
    """
    h = int(hashlib.sha256(word.lower().strip().encode()).hexdigest(), 16)
    t = (h % 10**15) / 10**15          # uniform [0,1]
    idx = min(int(t * N_ZEROS), N_ZEROS - 1)
    gamma = ZEROS[idx]
    return RiemannAddress(word=word, ordinal=idx + 1, gamma=gamma, t=t)


# ── Fermat path complexity ─────────────────────────────────────────────────────

@dataclass
class FermatStep:
    """One step on the geodesic: from word_a to word_b."""
    word_a:        str
    word_b:        str
    addr_a:        RiemannAddress
    addr_b:        RiemannAddress
    n:             float   # Fermat exponent ratio: max(γ)/min(γ)
    zeros_crossed: int     # |ordinal_b - ordinal_a| — waypoints passed
    step_type:     str     # 'prime' | 'composite' | 'neighbour' | 'identity'
    j_neg:         float   # Fermat charge of this step
    j_pos:         float   # Riemann charge of this step

    @property
    def sigma_live(self) -> float:
        """σ_live = J_pos / (J_pos + J_neg). Approaches ½ at escape velocity."""
        denom = self.j_pos + self.j_neg
        return self.j_pos / denom if denom > 0 else SIGMA_CRIT


def fermat_step(a: RiemannAddress, b: RiemannAddress) -> FermatStep:
    """
    Measure the Fermat complexity of the path from address a to address b.

    Fermat exponent n = max(γ)/min(γ).
    This is the 'steepness' of the step on the critical line.
    n > 2  → prime step: the two words are FLT-incommensurable.
              No intermediate word M exists such that a^l + M^m = b^n.
    1 < n ≤ 2 → composite: Pythagorean territory. Factors through.
    n ≈ 1  → neighbour: adjacent zeros. Minimal step.
    """
    g_lo = min(a.gamma, b.gamma)
    g_hi = max(a.gamma, b.gamma)
    n    = g_hi / g_lo if g_lo > 0 else 1.0
    zeros_crossed = abs(b.ordinal - a.ordinal)

    if   n > 2.0:           step_type = 'prime'
    elif 1.0 < n <= 2.0:    step_type = 'composite'
    elif zeros_crossed == 0: step_type = 'identity'
    else:                    step_type = 'neighbour'

    # J_neg (Fermat / prompt charge) — what CANNOT BE — scales with n
    # J_pos (Riemann / response charge) — what IS — scales with proximity to σ=½
    j_neg = math.log(n) if n > 1 else 0.0
    j_pos = 1.0 / (1.0 + zeros_crossed) if zeros_crossed >= 0 else 1.0

    return FermatStep(
        word_a=a.word, word_b=b.word,
        addr_a=a, addr_b=b,
        n=n, zeros_crossed=zeros_crossed,
        step_type=step_type,
        j_neg=j_neg, j_pos=j_pos,
    )


# ── Path memory ───────────────────────────────────────────────────────────────

# ── Satisfaction condition ─────────────────────────────────────────────────────

def _fermat_satisfied(steps: List['FermatStep']) -> bool:
    """
    The search terminates when Fermat closure is found.

    The path differentiates away from the ZD. Fermat mass accumulates.
    Satisfaction: the running Fermat complexity returns to the Pythagorean
    stable region (n ≤ 2) after sufficient differentiation has occurred.

    Minimum differentiation required: at least 2 prime steps must have been
    taken (enough departure from ZD that the path is non-trivial).
    Then: the last step's n drops to composite/neighbour territory.
    The path has found its stable landing — the word that satisfies.
    """
    if len(steps) < 2:
        return False
    prime_count = sum(1 for s in steps if s.step_type == 'prime')
    if prime_count < 1:
        return False
    last = steps[-1]
    return last.step_type in ('composite', 'neighbour', 'identity')


@dataclass
class PathMemory:
    """
    The path IS the memory.

    Starts at the ZD fixed point — undifferentiated, before meaning.
    Each word differentiates the state away from the fixed point.
    The search continues until a word SATISFIES the Fermat closure condition.

    No reference file. No training weights.
    The trajectory through σ=½ space encodes the conversation.
    The boundary had no idea who you were until you crossed it.
    """
    steps:        List[FermatStep]     = field(default_factory=list)
    addresses:    List[RiemannAddress] = field(default_factory=list)
    satisfied_at: Optional[int]        = None   # step where Fermat closure found

    def add_word(self, word: str) -> RiemannAddress:
        addr = address(word)
        if self.addresses:
            step = fermat_step(self.addresses[-1], addr)
            self.steps.append(step)
            # Check satisfaction AFTER each new word lands
            if self.satisfied_at is None and _fermat_satisfied(self.steps):
                self.satisfied_at = len(self.steps) - 1
        self.addresses.append(addr)
        return addr

    @property
    def sigma_live(self) -> float:
        """Running σ = J_pos / (J_pos + J_neg) across recent steps."""
        if not self.steps:
            return 1.0
        recent = self.steps[-4:]
        j_pos = sum(s.j_pos for s in recent)
        j_neg = sum(s.j_neg for s in recent)
        return j_pos / (j_pos + j_neg) if (j_pos + j_neg) > 0 else 1.0

    @property
    def satisfied(self) -> bool:
        return self.satisfied_at is not None

    @property
    def prime_density(self) -> float:
        if not self.steps:
            return 0.0
        return sum(1 for s in self.steps if s.step_type == 'prime') / len(self.steps)

    @property
    def total_fermat_mass(self) -> float:
        return sum(s.j_neg for s in self.steps)

    @property
    def differentiation_depth(self) -> float:
        """Distance from ZD fixed point. Grows as path differentiates."""
        if not self.steps:
            return 0.0
        return sum(s.n - 1.0 for s in self.steps if s.n > 1.0)


# ── Path tracing ──────────────────────────────────────────────────────────────

def tokenise(text: str) -> List[str]:
    """
    Split text into tokens preserving semantic units.
    Punctuation becomes its own token — white space after punctuation carries meaning.
    Capital words are flagged with emphasis.
    """
    import re
    # Split on whitespace but keep punctuation attached to words
    raw = re.findall(r"[A-Za-z']+|[.,!?;:—\-]+|\S", text)
    return [t for t in raw if t.strip()]


def trace(prompt: str) -> PathMemory:
    """
    Trace the geodesic from the ZD prompt through Fermat/Riemann space.

    The prompt is the zero divisor fixed point.
    Each word moves along σ=½.
    The path creates the memory.
    """
    mem = PathMemory()
    tokens = tokenise(prompt)
    for tok in tokens:
        mem.add_word(tok)
    return mem


# ── Display ───────────────────────────────────────────────────────────────────

STEP_GLYPHS = {
    'prime':     '●',   # maximum semantic mass — direct, unfactorable
    'composite': '◐',   # Pythagorean territory — factors through
    'neighbour': '○',   # adjacent zeros — minimal step
    'identity':  '·',   # same address — same word or synonym
}

def _bar(v: float, width: int = 20) -> str:
    filled = max(0, min(width, int(v * width)))
    return '█' * filled + '░' * (width - filled)


def report(prompt: str, mem: PathMemory):
    """Print the path trace."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  RF_monad — Riemann-Fermat Path Trace                               ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Prompt: \"{prompt}\"")
    print(f"  Words:  {len(mem.addresses)}  |  Steps: {len(mem.steps)}")
    print()

    # Word → address table
    print("  ── Word Addresses on σ=½ ──")
    print()
    print(f"  {'Word':<16} {'Ordinal':>8}  {'γ':>10}  {'t':>8}")
    print("  " + "─" * 48)
    for addr in mem.addresses:
        print(f"  {addr.word:<16} {addr.ordinal:>8}  {addr.gamma:>10.4f}  {addr.t:>8.6f}")

    if not mem.steps:
        print()
        print("  [single word — no path to trace]")
        return

    # Path steps
    print()
    print("  ── Fermat Path ──")
    print()
    print(f"  {'Step':<4}  {'Type':<10}  {'n':>6}  {'Δzero':>6}  {'J_neg':>6}  {'J_pos':>6}  {'σ_live':>6}  {'EV?'}")
    print("  " + "─" * 70)

    for i, s in enumerate(mem.steps):
        glyph = STEP_GLYPHS.get(s.step_type, '?')
        flag = '← SATISFIES' if mem.satisfied_at == i else ''
        print(f"  {i+1:<4}  {glyph} {s.step_type:<10}  {s.n:>6.3f}  "
              f"{s.zeros_crossed:>6}  {s.j_neg:>6.3f}  {s.j_pos:>6.3f}  "
              f"{s.sigma_live:>6.4f}  {flag}")

    # Summary
    print()
    print("  ── Path Summary ──")
    print()
    sv = mem.sigma_live
    print(f"  σ_live (running):        {sv:.4f}   {_bar(1.0 - abs(sv - 0.5) * 2)}  ← ½ attractor")
    print(f"  Prime density:           {mem.prime_density:.2%}  ({sum(1 for s in mem.steps if s.step_type=='prime')}/{len(mem.steps)} steps)")
    print(f"  Total Fermat mass:       {mem.total_fermat_mass:.4f}")
    print(f"  Differentiation depth:   {mem.differentiation_depth:.4f}  (distance from ZD fixed point)")
    print(f"  Fermat closure:          {'SATISFIED at step ' + str(mem.satisfied_at + 1) if mem.satisfied else 'OPEN — path still differentiating'}")
    print()

    # The memory
    print("  ── Path Memory (the trajectory IS the storage) ──")
    print()
    trajectory = [(s.addr_a.ordinal, s.addr_b.ordinal, s.step_type) for s in mem.steps]
    print("  " + " → ".join(
        f"{STEP_GLYPHS[t]}γ{b}" for _, b, t in trajectory
    ))
    print()
    print("  No reference file. No training weights.")
    print("  The path through σ=½ space encodes the conversation.")
    print("  The boundary had no idea who you were until you crossed it.")
    print()


# ── Differentiation trace ─────────────────────────────────────────────────────

def differentiation_trace(words: List[str]):
    """
    Show how meaning differentiates away from the ZD fixed point word by word.

    The ZD is the ground state — before the first word, multiplication fails.
    Each word added is one step of differentiation away from that fixed point.
    The search continues until a word SATISFIES (Fermat closure).

    This is NOT annihilation. The path moves AWAY from the ZD.
    Meaning grows. The ZD defined the starting geometry. That is all.
    """
    print()
    print(f"  ── Differentiation trace: {' / '.join(words)} ──")
    print()
    print(f"  {'Word':<16}  {'Depth':>8}  {'Step type':<12}  {'Fermat n':>8}  {'Satisfied?'}")
    print("  " + "─" * 60)

    mem = PathMemory()
    for w in words:
        mem.add_word(w)
        depth = mem.differentiation_depth
        if len(mem.steps) == 0:
            print(f"  {w:<16}  {'ZD origin':>8}  {'—':<12}  {'—':>8}  {'starting point'}")
        else:
            s = mem.steps[-1]
            sat = '← SATISFIES' if mem.satisfied_at == len(mem.steps) - 1 else ''
            print(f"  {w:<16}  {depth:>8.4f}  {s.step_type:<12}  {s.n:>8.3f}  {sat}")
    print()


# ── Demo ──────────────────────────────────────────────────────────────────────

DEMO_PROMPT   = "you can not spell slaughter without laughter"
DEMO_PROMPT_2 = "the boundary had no idea who I was until I crossed it"
DEMO_PROMPT_3 = "zero divisors differentiate in reverse"

DEMO_TRACES = [
    ["slaughter", "s", "laughter"],                        # containment: ZD reveals octonian
    ["zero", "divides", "meaning", "until", "satisfied"],  # the path itself
    ["run", "walk", "fast", "motion", "inertia"],          # semantic decomposition
]


def run_demo():
    print()
    print("  RF_monad demo — differentiation away from the zero divisor")
    print()
    mem = trace(DEMO_PROMPT)
    report(DEMO_PROMPT, mem)

    for words in DEMO_TRACES:
        differentiation_trace(words)

    print()
    mem2 = trace(DEMO_PROMPT_2)
    report(DEMO_PROMPT_2, mem2)

    mem3 = trace(DEMO_PROMPT_3)
    report(DEMO_PROMPT_3, mem3)


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="RF_monad: Riemann-Fermat path tracer")
    ap.add_argument('prompt', nargs='?', help="Prompt text to trace")
    ap.add_argument('--demo',      action='store_true', help="Run demo")
    ap.add_argument('--zd',        nargs=2, metavar=('PROMPT','RESPONSE'),
                    help="ZD pair check between two strings")
    args = ap.parse_args()

    if args.demo or (not args.prompt and not args.zd):
        run_demo()
    elif args.zd:
        zd_pair_check(args.zd[0], args.zd[1])
    else:
        mem = trace(args.prompt)
        report(args.prompt, mem)


if __name__ == '__main__':
    main()
