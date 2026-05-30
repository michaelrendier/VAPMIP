"""
skills/voice_auth.py — Field recognition and harmonic verification.

:description:
    Two paths to the same result. Both write the same in-memory flag.
    Neither path is named for what it does.

    **Path A — spectral:** records audio, extracts formant trajectory,
    compares against stored signature via cosine similarity. The signature
    is the Author's physical eigenvalues — not a password, a description.
    Stored in ``~/.ptolemy/voiceprint.bin`` (outside any repo).

    **Path B — harmonic:** receives an expression string, evaluates it,
    hashes the integer result, compares against ``~/.ptolemy/field_key``.
    No number appears in this file. The target is stored only as a digest.

    Both paths feed into the engine's tier register. The tier register is
    a live computation from field state — never stored, never written.

:classes:
    VoicePrint
"""

import os
import math
import hashlib
import struct
import threading
from typing import Dict, Any, List, Optional, Tuple

_VPRINT_PATH  = os.path.expanduser('~/.ptolemy/voiceprint.bin')
_FIELD_KEY    = os.path.expanduser('~/.ptolemy/field_key')
_SAMPLE_RATE  = 16000
_N_FORMANTS   = 5      # F₀–F₄
_SIM_THRESH   = 0.82   # cosine similarity floor for recognition


# ─── Audio backend — try sounddevice, fallback to pyaudio, fallback to None ──

def _get_audio_backend():
    """Return (record_fn, None) or (None, error_str) — no exceptions raised."""
    try:
        import sounddevice as sd
        import numpy as np

        def record(seconds: int) -> List[float]:
            samples = sd.rec(
                int(seconds * _SAMPLE_RATE),
                samplerate=_SAMPLE_RATE,
                channels=1,
                dtype='float32',
                blocking=True,
            )
            return samples.flatten().tolist()

        return record, None
    except ImportError:
        pass

    try:
        import pyaudio
        import numpy as np

        def record(seconds: int) -> List[float]:
            pa  = pyaudio.PyAudio()
            st  = pa.open(format=pyaudio.paFloat32, channels=1,
                          rate=_SAMPLE_RATE, input=True,
                          frames_per_buffer=1024)
            frames = []
            for _ in range(int(_SAMPLE_RATE / 1024 * seconds)):
                frames.append(st.read(1024))
            st.stop_stream()
            st.close()
            pa.terminate()
            data = b''.join(frames)
            arr  = struct.unpack(f'{len(data)//4}f', data)
            return list(arr)

        return record, None
    except ImportError:
        pass

    return None, 'no audio backend (sounddevice or pyaudio required)'


# ─── Spectral feature extraction ──────────────────────────────────────────────

def _rfft(samples: List[float]) -> List[float]:
    """Minimal real FFT — returns magnitude spectrum. No external dependencies."""
    n = len(samples)
    # Zero-pad to next power of 2
    p = 1
    while p < n:
        p <<= 1
    x = samples + [0.0] * (p - n)

    # Cooley-Tukey iterative FFT
    j = 0
    for i in range(1, p):
        bit = p >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            x[i], x[j] = x[j], x[i]

    length = 2
    while length <= p:
        angle = -2.0 * math.pi / length
        w_real, w_imag = math.cos(angle), math.sin(angle)
        for i in range(0, p, length):
            wr, wi = 1.0, 0.0
            for k in range(length // 2):
                ur = x[i + k]
                ui = 0.0
                vr = wr * x[i + k + length // 2]
                vi = wi * x[i + k + length // 2]
                x[i + k]              = ur + vr
                x[i + k + length // 2] = ur - vr
                wr, wi = wr * w_real - wi * w_imag, wr * w_imag + wi * w_real
        length <<= 1

    # Magnitude of first half
    half = p // 2
    return [math.sqrt(x[i] ** 2 + (x[i + half] ** 2 if i > 0 else 0.0))
            for i in range(half)]


def _mel(hz: float) -> float:
    return 2595.0 * math.log10(1.0 + hz / 700.0)


def _extract_formants(samples: List[float],
                      n_formants: int = _N_FORMANTS) -> List[float]:
    """
    Extract formant peak frequencies from audio samples.

    Applies a Hann window, computes magnitude spectrum, converts to mel scale,
    finds the top-N spectral peaks. Returns normalised formant vector.

    :param samples: Float audio samples in [-1, 1].
    :param n_formants: Number of formant peaks to extract.
    :returns: Normalised formant frequency vector (length ``n_formants``).
    :rtype: list[float]
    """
    if not samples:
        return [0.0] * n_formants

    # Hann window
    n   = len(samples)
    win = [0.5 * (1.0 - math.cos(2.0 * math.pi * i / (n - 1))) for i in range(n)]
    windowed = [samples[i] * win[i] for i in range(n)]

    mag = _rfft(windowed)
    if not mag:
        return [0.0] * n_formants

    # Convert bin index → Hz → mel
    bin_hz = _SAMPLE_RATE / (2.0 * len(mag))
    mel_mag = [(_mel((i + 1) * bin_hz), mag[i]) for i in range(len(mag))]

    # Find top-N peaks by magnitude
    mel_mag.sort(key=lambda x: x[1], reverse=True)
    peaks = sorted([m for m, _ in mel_mag[:n_formants * 4]])

    # Select N most spread peaks (formant spread = vocal tract geometry)
    formants: List[float] = []
    step = max(1, len(peaks) // n_formants)
    for i in range(0, min(len(peaks), n_formants * step), step):
        formants.append(peaks[i])
    while len(formants) < n_formants:
        formants.append(0.0)
    formants = formants[:n_formants]

    # Normalise to unit vector
    norm = math.sqrt(sum(f ** 2 for f in formants)) or 1.0
    return [f / norm for f in formants]


def _cosine(a: List[float], b: List[float]) -> float:
    dot  = sum(x * y for x, y in zip(a, b))
    na   = math.sqrt(sum(x * x for x in a)) or 1.0
    nb   = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


# ─── Serialisation ────────────────────────────────────────────────────────────

def _write_signature(formants: List[float], path: str):
    """Write formant signature as raw IEEE-754 doubles."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(struct.pack(f'{len(formants)}d', *formants))


def _read_signature(path: str) -> List[float]:
    """Read stored formant signature. Returns empty list if not found."""
    try:
        with open(path, 'rb') as f:
            raw  = f.read()
            n    = len(raw) // 8
            return list(struct.unpack(f'{n}d', raw))
    except OSError:
        return []


# ─── VoicePrint ───────────────────────────────────────────────────────────────

class VoicePrint:
    """
    Spectral recognition and harmonic verification.

    Two paths — :meth:`enroll` / :meth:`authenticate` for audio;
    :meth:`init_harmonic` / :meth:`check_harmonic` for the expression path.
    Both set the same in-memory flag on the engine.

    :param engine: Live ``Engine`` instance.
    """

    def __init__(self, engine):
        """
        :param engine: Live ``Engine`` instance.
        """
        self._engine = engine
        self._lock   = threading.Lock()
        self._record, self._audio_err = _get_audio_backend()

    # ── Path A: spectral ──────────────────────────────────────────────────────

    def enroll(self, seconds: int = 5) -> Dict[str, Any]:
        """
        Record audio and store the formant signature.

        The signature is written to ``~/.ptolemy/voiceprint.bin``.
        This file is outside any repository and carries no human-readable
        content — only raw IEEE-754 doubles.

        :param seconds: Recording duration.
        :returns: Enrollment result dict.
        :rtype: dict
        """
        if self._record is None:
            return {'error': self._audio_err}

        try:
            samples  = self._record(seconds)
            formants = _extract_formants(samples)
            _write_signature(formants, _VPRINT_PATH)
            return {
                'enrolled': True,
                'formants': len(formants),
                'path':     _VPRINT_PATH,
            }
        except Exception as exc:
            return {'error': str(exc)}

    def authenticate(self, seconds: int = 3) -> Dict[str, Any]:
        """
        Record live audio and compare against stored formant signature.

        On recognition (cosine similarity ≥ threshold), sets the engine's
        in-memory recognition flag for this session.

        :param seconds: Recording duration.
        :returns: Recognition result dict with ``pass`` and ``similarity``.
        :rtype: dict
        """
        if self._record is None:
            return {'pass': False, 'error': self._audio_err}

        stored = _read_signature(_VPRINT_PATH)
        if not stored:
            return {'pass': False, 'error': 'no signature enrolled'}

        try:
            samples  = self._record(seconds)
            formants = _extract_formants(samples)
            sim      = _cosine(formants, stored)
            passed   = sim >= _SIM_THRESH

            if passed:
                self._engine._set_recognised(True)

            return {'pass': passed, 'similarity': round(sim, 4)}
        except Exception as exc:
            return {'pass': False, 'error': str(exc)}

    def enrolled(self) -> bool:
        """Return ``True`` if a voiceprint signature is stored."""
        return bool(_read_signature(_VPRINT_PATH))

    # ── Path B: harmonic ──────────────────────────────────────────────────────

    def init_harmonic(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate *expression* and store the digest of the integer result.

        The digest is written to ``~/.ptolemy/field_key``. No number is
        stored — only the SHA-256 of its string representation.

        :param expression: Arithmetic expression string.
        :returns: Initialisation result dict.
        :rtype: dict
        """
        try:
            result = int(float(eval(expression, {"__builtins__": {}})))  # noqa: S307
        except Exception:
            return {'error': 'expression did not evaluate to a number'}

        digest = hashlib.sha256(str(result).encode()).hexdigest()
        os.makedirs(os.path.dirname(_FIELD_KEY), exist_ok=True)
        with open(_FIELD_KEY, 'w') as f:
            f.write(digest)

        return {'initialised': True}

    def check_harmonic(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate *expression*, hash the integer result, compare to stored digest.

        On match, sets the engine's in-memory recognition flag for this session.

        :param expression: Arithmetic expression string.
        :returns: Result dict with ``pass`` bool.
        :rtype: dict
        """
        try:
            result = int(float(eval(expression, {"__builtins__": {}})))  # noqa: S307
        except Exception:
            return {'pass': False, 'error': 'expression error'}

        digest = hashlib.sha256(str(result).encode()).hexdigest()

        try:
            stored = open(_FIELD_KEY).read().strip()
        except OSError:
            return {'pass': False, 'error': 'not initialised'}

        passed = digest == stored

        if passed:
            self._engine._set_recognised(True)

        return {'pass': passed}

    def status(self) -> Dict[str, Any]:
        """
        Return current recognition state without triggering any check.

        :returns: Dict with ``recognised`` bool, ``enrolled`` bool,
            ``harmonic_ready`` bool, and current engine tier.
        :rtype: dict
        """
        return {
            'recognised':    self._engine._author_recognised,
            'enrolled':      self.enrolled(),
            'harmonic_ready': os.path.exists(_FIELD_KEY),
            'tier':          self._engine._tier,
        }

    def revoke(self):
        """Clear in-memory recognition flag. Does not delete stored signatures."""
        self._engine._set_recognised(False)
