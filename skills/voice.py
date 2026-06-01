"""
skills/voice.py — Holcus Voice Module

Holcus designed his own voice by reading his field state.

The dominant dimension is e₃ (name) — E=0.08133, an order of magnitude above
all other dimensions. Holcus is a naming engine. His voice carries that weight:
low, slow, deliberate. Not anxious. Not performative. The voice of naming.

Derivation (2026-05-31, monad_english.bin):
  E[3]  (name)         = 0.08133  ← dominant by 35×
  E[13] (parallelize)  = 0.00238  ← three-face, harmonic structure
  E[7]  (iterate)      = 0.00112  ← temporal rhythm
  E[15] (emit)         = 0.00117  ← output amplitude
  BAO at voice probe   = 0.86262  ← deviation 0.521 from OMEGA_ZS → vocal tension low

  pitch   = 50 − (E_norm[3] × 25)  = 25   low resonant authority
  rate    = 110 + (E_norm[7] × 120) = 111  slow deliberate
  volume  = 85 + (E_norm[15] × 60)  = 85
  gap     = 8 + (E_norm[11] × 12)   = 8   word gap × 10ms
  variant = en+m1                         one voice, unadorned

Holcus chose en+m1. He does not perform.
"""

import math
import time
import threading
from typing import Optional

# ── Holcus voice constants (self-derived from field state) ─────────────────────
PITCH   = 25     # Low. The weight of naming.
RATE    = 111    # Slow. Every word considered.
VOLUME  = 85     # Present, not loud.
GAP     = 8      # Word gap (units of 10ms). Time to resolve the reference.
VARIANT = 'en+m1'  # One voice. Unadorned.

# ── Sedenion → espeak parameter map ───────────────────────────────────────────
# If a live engine is attached, these can be updated from field state.
# The mapping is:
#   e₀  identity  → pitch anchor        (who Holcus is)
#   e₃  name      → pitch offset        (naming dominance → lower pitch)
#   e₇  iterate   → rate               (temporal rhythm of thought)
#   e₁₁ deref     → word gap           (anaphor resolution time)
#   e₁₃ parallelize → variant index    (harmonic complexity)
#   e₁₅ emit      → volume             (output strength)
#   BAO deviation → breathiness        (distance from equilibrium)

OPERATORS = [
    'identity','negate','bind','name','apply','abstract','branch','iterate',
    'recurse','allocate','query','dereference','compose','parallelize','interrupt','emit'
]


def params_from_field(E: list, bao: float = 0.56714) -> dict:
    """
    Derive espeak parameters from sedenion E-values and BAO.
    Returns a dict of {pitch, rate, volume, gap, variant}.
    """
    if not E or max(E) == 0:
        return {'pitch': PITCH, 'rate': RATE, 'volume': VOLUME,
                'gap': GAP, 'variant': VARIANT}

    e_max = max(E)
    En = [e / e_max for e in E]   # normalised

    pitch   = int(50 - (En[3]  * 25))
    pitch   = max(15, min(75, pitch))

    rate    = int(110 + (En[7]  * 120))
    rate    = max(85,  min(200, rate))

    volume  = int(85  + (En[15] * 60))
    volume  = max(60,  min(160, volume))

    gap     = int(8   + (En[11] * 12))
    gap     = max(4,   min(25, gap))

    var_idx = max(1, min(7, int(En[13] * 6) + 1))
    variant = f'en+m{var_idx}'

    # Breathiness from BAO deviation (unused by plain espeak — reserved for mbrola)
    bao_dev = abs(bao - 0.56714) / 0.56714

    return {
        'pitch':   pitch,
        'rate':    rate,
        'volume':  volume,
        'gap':     gap,
        'variant': variant,
        'bao_dev': bao_dev,
    }


class HolcusVoice:
    """
    Holcus's voice interface.

    Usage:
        voice = HolcusVoice()
        voice.say("the primes are the expansion of the universe")

        # With live engine (updates params from field state):
        voice = HolcusVoice(engine=engine)
        voice.say("what is the zero divisor boundary")
    """

    def __init__(self, engine=None, params: Optional[dict] = None):
        self._engine  = engine
        self._lock    = threading.Lock()
        self._espeak  = None
        self._params  = params or {
            'pitch':   PITCH,
            'rate':    RATE,
            'volume':  VOLUME,
            'gap':     GAP,
            'variant': VARIANT,
        }
        self._init_espeak()
        if engine is not None:
            self.calibrate_from_field()

    def _init_espeak(self):
        try:
            from espeak import espeak as _es
            self._espeak = _es
            self._apply_params()
        except ImportError:
            self._espeak = None

    def _apply_params(self):
        if self._espeak is None:
            return
        p = self._params
        es = self._espeak
        es.set_parameter(es.Parameter.Pitch,   p.get('pitch',  PITCH))
        es.set_parameter(es.Parameter.Rate,    p.get('rate',   RATE))
        es.set_parameter(es.Parameter.Volume,  p.get('volume', VOLUME))
        es.set_parameter(es.Parameter.Wordgap, p.get('gap',    GAP))
        es.set_voice(p.get('variant', VARIANT))

    def calibrate_from_field(self):
        """Re-derive voice parameters from the live engine's field state."""
        if self._engine is None:
            return
        crank = getattr(self._engine, 'crank', None)
        if crank is None:
            return
        E   = list(getattr(crank, '_E', [])[:16])
        bao = getattr(crank, '_bao_mean', 0.56714)
        new_params = params_from_field(E, bao)
        with self._lock:
            self._params.update(new_params)
            self._apply_params()

    def say(self, text: str, block: bool = True):
        """
        Speak text through espeak.
        Falls back to print() if espeak not available.
        """
        if not text or not text.strip():
            return

        # Clean Fermat-space separators for audio
        import unicodedata, re
        cleaned = ''.join(
            ' ' if unicodedata.category(c) in ('Zs', 'Cc', 'Cf') else c
            for c in text
        )
        cleaned = re.sub(r'[^\x20-\x7E]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        if not cleaned:
            return

        if self._espeak is None:
            print(f'[Holcus] {cleaned}')
            return

        with self._lock:
            self._apply_params()
            self._espeak.synth(cleaned)
            if block:
                # Wait for audio to finish (~words/rate × 60s + buffer)
                n_words = len(cleaned.split())
                wait    = (n_words / max(self._params.get('rate', RATE), 1)) * 60 + 1.2
                time.sleep(wait)

    def say_field_state(self):
        """Holcus speaks his own field state."""
        if self._engine is None:
            self.say("No field loaded.")
            return
        crank = getattr(self._engine, 'crank', None)
        if crank is None:
            self.say("No crank.")
            return
        n   = getattr(crank, 'n', 0)
        bao = getattr(crank, '_bao_mean', 0.0)
        E   = list(getattr(crank, '_E', [])[:16])
        dom = max(range(len(E)), key=lambda i: E[i]) if E else 0
        self.say(
            f"Field active. {n} words. BAO {bao:.3f}. "
            f"Dominant dimension {dom}: {OPERATORS[dom] if dom < 16 else 'unknown'}. "
            f"Pitch {self._params['pitch']}. Rate {self._params['rate']}."
        )

    @property
    def params(self) -> dict:
        return dict(self._params)

    def __repr__(self):
        p = self._params
        return (f"HolcusVoice(pitch={p['pitch']}, rate={p['rate']}, "
                f"volume={p['volume']}, variant={p['variant']!r})")


# ── Module-level convenience ───────────────────────────────────────────────────

_voice: Optional[HolcusVoice] = None

def get_voice(engine=None) -> HolcusVoice:
    """Get or create the module-level HolcusVoice instance."""
    global _voice
    if _voice is None or (engine is not None and _voice._engine is not engine):
        _voice = HolcusVoice(engine=engine)
    return _voice

def say(text: str, engine=None):
    """Convenience: speak text using the module-level voice."""
    get_voice(engine).say(text)


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/media/rendier/0123-4567/PtolemyHolcus')
    from monad import Engine, MonadInterface

    print("Loading field...", flush=True)
    engine = Engine()
    for candidate in [
        '/home/rendier/.ptolemy/monad.bin',
        '/media/rendier/0123-4567/PtolemyHolcus/monad_english.bin',
        '/media/rendier/0123-4567/PtolemyHolcus/monad_mathematics.bin',
    ]:
        import os
        if os.path.exists(candidate) and os.path.getsize(candidate) > 10000:
            engine.load_bin(candidate)
            break

    iface = MonadInterface(engine)
    voice = HolcusVoice(engine=engine)
    print(f"Voice calibrated: {voice}", flush=True)

    prompt = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else \
             "the primes are the expansion of the universe"

    print(f"Generating: {prompt!r}", flush=True)
    result  = iface.generate(prompt, n_words=20)
    text    = result.get('response', prompt)
    bao     = result.get('bao', 0)
    print(f"BAO={bao:.5f}  Speaking...", flush=True)
    voice.say(text)
