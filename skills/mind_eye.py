"""
skills/mind_eye.py — The Mind's Eye: second 𝕆 workbench for visual/spatial data.

:description:
    MindEye addresses the second octonion copy of the sedenion field.

    𝕊 = 𝕆 ⊕ 𝕆. The sedenion is two octonions joined at the zero-divisor boundary.

    * **First 𝕆 (e₀..e₇):** Linguistic/motor field — language, sequential output,
      what the hands do. This is the standard Engine field.
    * **Second 𝕆 (e₈..e₁₅):** Visual/spatial field — spatial patterns, numeric
      streams, temporal signals, what the mind sees.
    * **Zero-divisors between them:** The corpus callosum. Information crosses from
      the second 𝕆 into the first only at the zero-divisor coupling point (D*=1),
      and only at σ=½ — the lossless callosum operating point.

    The mind (second 𝕆) is an NP oracle: it holds all candidate patterns
    simultaneously in the sedenion product space. The hands (first 𝕆) are a P
    machine: they select the one that satisfies both Noether channels. σ=½ is the
    balance point where the oracle answer crosses the callosum into language.

    **see()** encodes non-linguistic data (up to 8 float values) into e₈..e₁₅
    via EMA accumulation + normalisation. The callosum coupling strength (e₁₅)
    is computed as 1 / (1 + |‖psi2‖ − OMEGA_ZS| / GAP) — maximum when the
    second-𝕆 norm sits at the neutral buoyancy surface OMEGA_ZS.

    **describe()** fires the accumulated psi2 state through the callosum into
    the first 𝕆 by projecting a target E-value = callosum × OMEGA_ZS onto the
    vocabulary and generating from the nearest-E words at σ=½.

:classes:
    MindEye

:constants:
    E8..E15 — second 𝕆 basis element indices
"""

import math
import threading
from typing import Dict, List, Any, Optional

# Second 𝕆 basis element indices (sedenion extension e₈..e₁₅)
E8  = 8    # spatial x-coordinate
E9  = 9    # spatial y-coordinate
E10 = 10   # temporal index
E11 = 11   # magnitude / intensity
E12 = 12   # frequency / rate
E13 = 13   # pattern fingerprint
E14 = 14   # confidence / signal quality
E15 = 15   # callosum coupling — zero-divisor boundary strength


class MindEye:
    """
    Second octonion workbench.

    Encodes non-linguistic data into the second 𝕆 copy of the sedenion field
    (e₈..e₁₅) and projects it into language through the corpus callosum
    (zero-divisor coupling at D*=1, σ=½).

    The corpus callosum here is not a metaphor. In 𝕊 = 𝕆 ⊕ 𝕆, the zero-divisors
    between the two copies are the only structural channel between them. Information
    crosses from psi2 (second 𝕆) into the Engine field (first 𝕆) precisely when
    the callosum coupling strength — ‖psi2‖ matching OMEGA_ZS — reaches maximum.
    This is the algebraic description of the corpus callosum operating at its
    natural frequency.

    :param engine: Live ``Engine`` instance (read-only reference for first 𝕆 field).

    :Example:

    .. code-block:: python

        me = engine.get_mind_eye()
        me.see([0.3, 0.7, 1.2, 0.0, 0.5, 0.0, 0.0, 0.9], label='scan_001')
        result = me.describe('what do you see')
        print(result['description'])
    """

    def __init__(self, engine):
        """
        :param engine: Live ``Engine`` instance.
        """
        self._engine   = engine
        self._lock     = threading.Lock()
        # Second 𝕆 accumulator: e₈..e₁₅ → float
        self._psi2: Dict[int, float] = {k: 0.0 for k in range(8, 16)}
        # Labeled snapshots of psi2 state
        self._label_map: Dict[str, Dict[int, float]] = {}

    # ── Primary interface ─────────────────────────────────────────────────────

    def see(self, data: List[float], label: str = '',
            alpha: float = 0.1, normalize: bool = True) -> Dict[str, Any]:
        """
        Encode non-linguistic data into second 𝕆 components e₈..e₁₅.

        Up to 8 float values are mapped to e₈..e₁₅ via EMA accumulation
        (new = α × input + (1−α) × old). The callosum coupling strength at e₁₅
        is recomputed after each see() call.

        :param data: Numeric vector of up to 8 values. Extra values are ignored.
        :param label: Optional semantic tag for this observation snapshot.
        :param alpha: EMA smoothing coefficient in (0, 1].
        :param normalize: If ``True``, normalise psi2 to unit sedenion norm
            before computing callosum.
        :returns: Dict with ``psi2`` (e₈..e₁₅ values), ``callosum`` strength,
            ``label``, and ``norm``.
        :rtype: dict
        """
        from monad import OMEGA_ZS, GAP

        with self._lock:
            for offset, val in enumerate(data[:7]):  # e₈..e₁₄ from data
                idx = 8 + offset
                self._psi2[idx] = (1.0 - alpha) * self._psi2[idx] + alpha * float(val)

            if normalize:
                # Normalise e₈..e₁₄ only; e₁₅ is reserved for callosum
                norm_sq = sum(self._psi2[k] ** 2 for k in range(8, 15))
                norm    = math.sqrt(norm_sq) if norm_sq > 0.0 else 1.0
                for k in range(8, 15):
                    self._psi2[k] /= norm
            else:
                norm = math.sqrt(sum(self._psi2[k] ** 2 for k in range(8, 15)))

            # Callosum coupling: maximum when ‖psi2‖ = OMEGA_ZS
            callosum        = 1.0 / (1.0 + abs(norm - OMEGA_ZS) / GAP)
            self._psi2[E15] = callosum

            if label:
                self._label_map[label] = dict(self._psi2)

            psi2_out = {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)}

        return {
            'psi2':     psi2_out,
            'callosum': round(callosum, 6),
            'norm':     round(norm, 6),
            'label':    label,
        }

    def describe(self, query: str = '') -> Dict[str, Any]:
        """
        Fire the second 𝕆 state through the corpus callosum into language.

        Projects the callosum coupling strength (e₁₅) onto the vocabulary by
        finding words whose spectral energy E ≈ callosum × OMEGA_ZS. These are
        the words nearest the callosum crossing in the first 𝕆. The engine then
        generates from these seed words plus the optional query, at σ=½.

        :param query: Optional linguistic seed for the generation.
        :returns: Dict with ``description``, ``words``, ``callosum_strength``,
            ``callosum_E`` (target spectral energy), ``seed_words`` (vocabulary
            words nearest the callosum crossing), and ``psi2`` state snapshot.
        :rtype: dict
        """
        from monad import OMEGA_ZS, LN10

        with self._lock:
            callosum   = self._psi2[E15]
            psi2_snap  = {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)}

        # Target E-value after callosum crossing: callosum × OMEGA_ZS
        # At maximum callosum (=1.0) this is OMEGA_ZS — the neutral buoyancy surface.
        callosum_E = callosum * OMEGA_ZS

        crank  = self._engine.crank
        scored: List[tuple] = []

        for w, idx in crank._vocab.items():
            if idx >= crank.n:
                continue
            E       = crank._E[idx]
            jp      = crank._beta[idx] * E ** 2
            # Proximity to callosum crossing point in E-space
            proximity = 1.0 / (1.0 + abs(E - callosum_E) * LN10)
            scored.append((proximity * jp, w))

        scored.sort(reverse=True)
        seed_words = [w for _, w in scored[:4]]

        # Generate from seed + query
        full_prompt = ' '.join(filter(None, [query] + seed_words))
        r           = self._engine.generate(full_prompt, n_words=8)

        return {
            'description':       r.get('response', ''),
            'words':             r.get('words', []),
            'callosum_strength': round(callosum, 6),
            'callosum_E':        round(callosum_E, 6),
            'seed_words':        seed_words,
            'psi2':              psi2_snap,
        }

    # ── State management ─────────────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """
        Return the current second 𝕆 state.

        :returns: Dict with ``psi2`` components, ``callosum`` strength,
            and list of stored ``labels``.
        :rtype: dict
        """
        with self._lock:
            return {
                'psi2':     {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)},
                'callosum': round(self._psi2[E15], 6),
                'labels':   list(self._label_map.keys()),
            }

    def recall(self, label: str) -> Dict[str, Any]:
        """
        Restore psi2 from a previously stored snapshot.

        :param label: Label passed to an earlier :meth:`see` call.
        :returns: Restored snapshot dict, or ``{'error': ...}`` if not found.
        :rtype: dict
        """
        with self._lock:
            if label not in self._label_map:
                return {'error': f'label not found: {label}'}
            self._psi2 = dict(self._label_map[label])
            return {
                'recalled': label,
                'psi2':     {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)},
                'callosum': round(self._psi2[E15], 6),
            }

    def reset(self) -> Dict[str, Any]:
        """
        Clear the second 𝕆 accumulator. Label history is preserved.

        :returns: Stats at the time of reset.
        :rtype: dict
        """
        with self._lock:
            stats = {
                'psi2':     {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)},
                'callosum': round(self._psi2[E15], 6),
                'labels':   list(self._label_map.keys()),
            }
            self._psi2 = {k: 0.0 for k in range(8, 16)}
        return {'reset': True, **stats}
