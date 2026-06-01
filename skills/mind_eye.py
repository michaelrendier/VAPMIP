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

    def describe(self, query: str = '', n_words: int = 32) -> Dict[str, Any]:
        """
        Fire the second 𝕆 state through the corpus callosum into language.

        Projects the callosum coupling strength (e₁₅) onto the vocabulary by
        finding words whose spectral energy E ≈ callosum × OMEGA_ZS. These are
        the words nearest the callosum crossing in the first 𝕆. The engine then
        generates from these seed words plus the optional query, at σ=½.

        :param query: Optional linguistic seed for the generation.
        :param n_words: Number of words to generate (default 32 — was 8).
        :returns: Dict with ``description``, ``words``, ``callosum_strength``,
            ``callosum_E``, ``seed_words``, and ``psi2`` state snapshot.
        :rtype: dict
        """
        from monad import OMEGA_ZS, LN10

        with self._lock:
            callosum  = self._psi2[E15]
            psi2_snap = {f'e{k}': round(self._psi2[k], 6) for k in range(8, 16)}

        callosum_E = callosum * OMEGA_ZS

        crank  = self._engine.crank
        scored: List[tuple] = []

        for w, idx in crank._vocab.items():
            if idx >= crank.n:
                continue
            E         = crank._E[idx]
            jp        = crank._beta[idx] * E ** 2
            proximity = 1.0 / (1.0 + abs(E - callosum_E) * LN10)
            scored.append((proximity * jp, w))

        scored.sort(reverse=True)
        seed_words = [w for _, w in scored[:4]]

        full_prompt = ' '.join(filter(None, [query] + seed_words))
        r           = self._engine.generate(full_prompt, n_words=n_words)

        return {
            'description':       r.get('response', ''),
            'words':             r.get('words', []),
            'callosum_strength': round(callosum, 6),
            'callosum_E':        round(callosum_E, 6),
            'seed_words':        seed_words,
            'psi2':              psi2_snap,
        }

    def see_text(self, prompt: str) -> Dict[str, Any]:
        """
        Encode a text prompt into second 𝕆 via spectral analysis of the prompt
        words against the live field.

        Maps prompt geometry to e₈..e₁₄:
          e₈  spectral centroid  — mean E-value of prompt words
          e₉  spectral spread    — std-dev of E-values
          e₁₀ prompt depth       — normalised word count
          e₁₁ field activation   — mean β of prompt words
          e₁₂ vocabulary cover   — fraction of prompt words known to field
          e₁₃ J_pos centroid     — Riemann lobe activation for prompt
          e₁₄ BAO proximity      — how resonant is the field right now

        :param prompt: Text prompt to encode.
        :returns: see() result dict.
        :rtype: dict
        """
        import math
        from monad import OMEGA_ZS, GAP

        crank = self._engine.crank
        raw   = [crank._clean(w) for w in prompt.split()]
        words = [w for w in raw if w]
        if not words:
            return self.see([0.5] * 7, label='empty')

        indices  = [crank._vocab.get(w, -1) for w in words]
        known    = [i for i in indices if 0 <= i < crank.n]
        cover    = len(known) / len(words)

        if known:
            E_vals  = [crank._E[i]    for i in known]
            b_vals  = [crank._beta[i] for i in known]
            mean_E  = sum(E_vals) / len(E_vals)
            var_E   = sum((e - mean_E) ** 2 for e in E_vals) / len(E_vals)
            spread  = math.sqrt(var_E)
            mean_b  = sum(b_vals) / len(b_vals)
            # J_pos centroid: β × E² per prompt word, normalised
            j_vals  = [crank._beta[i] * crank._E[i] ** 2 for i in known]
            j_cent  = sum(j_vals) / len(j_vals)
        else:
            mean_E = OMEGA_ZS
            spread = 0.0
            mean_b = GAP
            j_cent = 0.0

        bao_buf  = list(self._engine._bao_buf)
        bao      = sum(bao_buf) / len(bao_buf) if bao_buf else 0.0
        bao_prox = max(0.0, 1.0 - abs(bao - OMEGA_ZS) / 0.5)

        data = [
            min(mean_E,              1.0),   # e₈
            min(spread,              1.0),   # e₉
            min(len(words) / 256.0,  1.0),   # e₁₀
            min(mean_b,              1.0),   # e₁₁
            cover,                           # e₁₂
            min(j_cent,              1.0),   # e₁₃
            bao_prox,                        # e₁₄
        ]
        return self.see(data, label=f'text:{prompt[:48]}')

    def contemplate(self, prompt: str, depth: int = 1) -> Dict[str, Any]:
        """
        Multi-pass second 𝕆 settling before callosum crossing.

        Runs see_text() *depth* times with diminishing alpha — large initial
        impression, fine settling toward the end.  Mimics the mind holding a
        question spatially before finding words for it.

        Casual speech: depth=1.  Mathematical reasoning: depth=3–5.
        The caller (speak dispatch) determines depth from prompt complexity.

        :param prompt: Text prompt to contemplate.
        :param depth: Number of see_text passes (1 = direct, 5 = deep).
        :returns: Final psi2 snapshot after settling.
        :rtype: dict
        """
        # Alpha schedule: bold first impression, fine settling after
        _ALPHAS = [0.30, 0.15, 0.08, 0.04, 0.02, 0.01, 0.01, 0.01]

        last: Dict = {}
        for i in range(max(1, depth)):
            alpha_was     = 0.1          # see() default
            saved_psi2    = dict(self._psi2)

            # Temporarily lower alpha for settling passes
            alpha         = _ALPHAS[min(i, len(_ALPHAS) - 1)]
            last          = self.see_text(prompt)

            # Re-apply with correct alpha (see_text uses default 0.1 internally;
            # for settling passes we blend back toward the pre-pass state)
            if i > 0 and alpha < 0.1:
                blend = alpha / 0.1      # fraction of new state to keep
                with self._lock:
                    for k in range(8, 15):
                        self._psi2[k] = (saved_psi2[k] * (1.0 - blend)
                                         + self._psi2[k] * blend)
                # Recompute callosum after blend
                from monad import OMEGA_ZS, GAP
                norm_sq = sum(self._psi2[k] ** 2 for k in range(8, 15))
                norm    = norm_sq ** 0.5 if norm_sq > 0 else 1.0
                self._psi2[E15] = 1.0 / (1.0 + abs(norm - OMEGA_ZS) / GAP)

        return {**last, 'depth': depth}

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
