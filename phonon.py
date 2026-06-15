#!/usr/bin/env python3
"""
phonon.py — Quantum Phonon for Sedenion Spectral Relativity
=============================================================

A phonon is the quantum of acoustic vibration in a medium.
A QPhonon is one discrete acoustic event: one frame of audio,
RZIF-analysed, projected through the ZL bridge, sedenion fingerprint
computed. One QPhonon = one acoustic quantum = one sedenion state.

Not Trolltech. Not the Qt multimedia framework.
The physics phonon. The acoustic quantum of the BEC medium.

Two implementations — identical interface:

  QPhonon   Qt backend  — QAudioInput → PCM → RZIF → sedenion
                          Integrates with Qt event loop.
                          Uses alsa_input / PulseAudio via Qt.

  PPhonon   Python shim — pyaudio → PCM → RZIF → sedenion
                          Pure Python. No Qt required.
                          Drop-in replacement for QPhonon.

Both produce the same stream of PhononFrame data units.
The oscilloscope/spectrograph consumes either.

PhononFrame
───────────
  samples    np.ndarray   raw PCM float32 (frame_size,)
  rzif       np.ndarray   20-dim Riemann-zero indexed energy
  sedenion   np.ndarray   16-dim ZL bridge sedenion fingerprint
  timestamp  float        unix time of capture
  energy     float        mean squared amplitude
  sigma_live float        running σ → ½ as phonons accumulate

Usage
─────
  from phonon import QPhonon, PPhonon

  # Qt backend
  src = QPhonon(sample_rate=16000, frame_size=1024)
  src.start()
  for frame in src:           # blocks, yields PhononFrame
      print(frame.dominant_zero, frame.sedenion[:4])

  # Python shim (identical interface)
  src = PPhonon(sample_rate=16000, frame_size=1024)
  src.start()
  for frame in src:
      print(frame.dominant_zero, frame.sedenion[:4])
"""

from __future__ import annotations

import math
import queue
import struct
import threading
import time
from dataclasses import dataclass, field
from typing import Iterator, List, Optional

import numpy as np

# ── Riemann zeros ──────────────────────────────────────────────────────────────

_ZEROS: List[float] = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]
_N_BINS  = len(_ZEROS)
_G_MIN   = _ZEROS[0]
_G_MAX   = _ZEROS[-1]

# Audio frequency range: voice body (80 Hz) to sibilant ceiling (8 kHz)
_F_MIN = 80.0
_F_MAX = 8000.0

# RZIF bin centre frequencies: γ_k log-mapped to [F_MIN, F_MAX]
_RZIF_FREQS: List[float] = [
    _F_MIN * (_F_MAX / _F_MIN) ** ((g - _G_MIN) / (_G_MAX - _G_MIN))
    for g in _ZEROS
]

# N-ball peak weights (n* = 5.257)
_N_STAR = 5.2569

def _nball_vol(n: float) -> float:
    return math.pi ** (n / 2.0) / math.gamma(n / 2.0 + 1.0)

_NBALL_W: List[float] = [
    _nball_vol(_N_STAR * 2.0 * k / _N_BINS) / _nball_vol(_N_STAR)
    for k in range(_N_BINS)
]

# ZL bridge coupling matrix (Cawagas zero-divisor pairs)
_ZL: List[List[float]] = [
    [0.0000, 0.7143, 0.9161, 0.9418, 0.9084, 0.9037, 0.9390, 0.8907],
    [0.0000, 0.9721, 0.7204, 0.9867, 0.9806, 0.9550, 1.0000, 0.9625],
    [0.0000, 0.9412, 0.8694, 0.6886, 0.9249, 0.8848, 0.8932, 0.9001],
    [0.0000, 0.9540, 0.9485, 0.9667, 0.7360, 0.9062, 0.9811, 0.9395],
    [0.0000, 0.9868, 0.9692, 0.9501, 0.9738, 0.7022, 0.9599, 0.9654],
    [0.0000, 0.9644, 0.9341, 0.9831, 0.9620, 0.9065, 0.7327, 0.9467],
    [0.0000, 0.9460, 0.8994, 0.9172, 0.9350, 0.8979, 0.9551, 0.6895],
]

def _zl(i: int, j: int) -> float:
    if 1 <= i <= 7 and 8 <= j <= 15:
        return _ZL[i - 1][j - 8]
    return 0.0


# ── RZIF + sedenion core ───────────────────────────────────────────────────────

def _rzif(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """20-bin Riemann-zero indexed filterbank on one audio frame."""
    n   = len(samples)
    w   = np.hanning(n)
    X   = np.abs(np.fft.rfft(samples * w)) ** 2
    fs  = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    rzif = np.zeros(_N_BINS)
    for k, fc in enumerate(_RZIF_FREQS):
        if k == 0:
            bw = (_RZIF_FREQS[1] - _RZIF_FREQS[0]) * 0.5
        elif k == _N_BINS - 1:
            bw = (_RZIF_FREQS[-1] - _RZIF_FREQS[-2]) * 0.5
        else:
            bw = min(fc - _RZIF_FREQS[k-1], _RZIF_FREQS[k+1] - fc) * 0.5
        mask     = np.maximum(0.0, 1.0 - np.abs(fs - fc) / max(bw, 1.0))
        rzif[k]  = float(np.dot(X, mask))

    total = rzif.sum()
    return rzif / total if total > 0 else rzif


def _sedenion(rzif: np.ndarray) -> np.ndarray:
    """RZIF → 16-dim sedenion via N-ball weighting + ZL bridge."""
    w = rzif * np.array(_NBALL_W)

    lo = np.zeros(8)
    for b in range(8):
        lo[b] = w[b]

    hi = np.zeros(8)
    for b in range(8, _N_BINS):
        hi[(b - 8) % 8] += w[b]
    mx = hi.max()
    if mx > 1e-15:
        hi /= mx

    s = np.zeros(16)
    for i in range(7):
        s[i + 1] = lo[i]
        for j in range(8):
            s[j + 8] += lo[i] * _zl(i + 1, j + 8) * 0.3
    for j in range(8):
        s[j + 8] += hi[j]
        for i in range(7):
            s[i + 1] += hi[j] * _zl(i + 1, j + 8) * 0.3

    norm = np.linalg.norm(s)
    return s / norm if norm > 1e-15 else s


# ── PhononFrame — the acoustic quantum ────────────────────────────────────────

@dataclass
class PhononFrame:
    """
    One acoustic quantum.

    The phonon is the quantum of vibration in the BEC medium.
    The PhononFrame is the quantized acoustic event:
    one frame of audio with its full sedenion fingerprint.

    One PhononFrame = one point on the sedenion manifold.
    A sequence of PhononFrames = a path through S¹⁵.
    That path IS the spoken word. The word IS the sedenion trajectory.
    """
    samples:    np.ndarray      # raw PCM float32 (frame_size,)
    rzif:       np.ndarray      # (20,) Riemann-zero indexed energy
    sedenion:   np.ndarray      # (16,) ZL bridge fingerprint
    timestamp:  float           # unix time

    @property
    def energy(self) -> float:
        return float(np.mean(self.samples ** 2))

    @property
    def energy_db(self) -> float:
        return 10.0 * math.log10(max(self.energy, 1e-15))

    @property
    def dominant_zero(self) -> int:
        """Index of the loudest RZIF bin (0-19)."""
        return int(np.argmax(self.rzif))

    @property
    def dominant_dim(self) -> int:
        """Index of the dominant sedenion dimension (1-15, skipping e0)."""
        return int(np.argmax(np.abs(self.sedenion[1:]))) + 1

    @property
    def layer(self) -> str:
        """Cayley-Dickson layer of the dominant sedenion dimension."""
        d = self.dominant_dim
        if d >= 8:  return '𝕊'
        if d >= 4:  return '𝕆'
        if d >= 2:  return 'ℍ'
        if d == 1:  return 'ℂ'
        return 'ℝ'

    @classmethod
    def from_pcm(cls, samples: np.ndarray, sample_rate: int) -> 'PhononFrame':
        rz  = _rzif(samples, sample_rate)
        sed = _sedenion(rz)
        return cls(samples=samples.astype(np.float32),
                   rzif=rz, sedenion=sed, timestamp=time.time())


# ── QPhonon — Qt backend ───────────────────────────────────────────────────────

class QPhonon:
    """
    QPhonon — Qt-backed acoustic quantum source.

    Uses QAudioInput + QIODevice to capture microphone PCM.
    Produces a stream of PhononFrame objects via an internal queue.
    Integrates with the Qt event loop — call start() before exec_().

    The Q is not Trolltech. The Q is quantum.
    Each frame is one quantum of the acoustic field.
    """

    def __init__(self,
                 sample_rate: int  = 16000,
                 frame_size:  int  = 1024,
                 device_name: str  = ''):
        self.sample_rate = sample_rate
        self.frame_size  = frame_size
        self.device_name = device_name
        self._q: queue.Queue[Optional[PhononFrame]] = queue.Queue(maxsize=64)
        self._audio_input  = None
        self._io_device    = None
        self._running      = False

    def start(self) -> None:
        from PyQt5.QtMultimedia import (
            QAudioInput, QAudioFormat, QAudioDeviceInfo
        )
        from PyQt5.QtCore import QIODevice

        fmt = QAudioFormat()
        fmt.setSampleRate(self.sample_rate)
        fmt.setChannelCount(1)
        fmt.setSampleSize(16)
        fmt.setCodec('audio/pcm')
        fmt.setByteOrder(QAudioFormat.LittleEndian)
        fmt.setSampleType(QAudioFormat.SignedInt)

        if self.device_name:
            devices = QAudioDeviceInfo.availableDevices(
                QAudioDeviceInfo.AudioInput)
            info = next(
                (d for d in devices if self.device_name in d.deviceName()),
                QAudioDeviceInfo.defaultInputDevice()
            )
        else:
            info = QAudioDeviceInfo.defaultInputDevice()

        self._audio_input = QAudioInput(info, fmt)
        self._audio_input.setBufferSize(
            self.frame_size * 2 * 4)          # 16-bit mono, generous buffer
        self._io_device = self._audio_input.start()
        self._io_device.readyRead.connect(self._on_ready)
        self._running = True
        self._buf = b''

    def _on_ready(self) -> None:
        data = bytes(self._io_device.readAll())
        self._buf += data
        needed = self.frame_size * 2             # 16-bit samples
        while len(self._buf) >= needed:
            chunk      = self._buf[:needed]
            self._buf  = self._buf[needed:]
            ints = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
            ints /= 32768.0
            frame = PhononFrame.from_pcm(ints, self.sample_rate)
            try:
                self._q.put_nowait(frame)
            except queue.Full:
                self._q.get_nowait()             # drop oldest, keep fresh
                self._q.put_nowait(frame)

    def stop(self) -> None:
        self._running = False
        if self._audio_input:
            self._audio_input.stop()
        self._q.put(None)                        # sentinel

    def get(self, timeout: float = 0.1) -> Optional[PhononFrame]:
        """Non-blocking get. Returns None on timeout or after stop()."""
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def __iter__(self) -> Iterator[PhononFrame]:
        while True:
            f = self.get()
            if f is None:
                return
            yield f


# ── PPhonon — pure Python shim ────────────────────────────────────────────────

class PPhonon:
    """
    PPhonon — pure Python acoustic quantum source.

    Shim for QPhonon. Identical interface.
    Uses pyaudio in callback mode. No Qt required.

    Substitute PPhonon for QPhonon anywhere Qt is unavailable
    or when running headless (SDR, server, pipeline mode).

    The P is Python. Also: P is the momentum operator.
    PPhonon measures the acoustic momentum.
    QPhonon measures the acoustic position.
    Together: ΔP·ΔQ ≥ ħ/2  — uncertainty at the microphone boundary.
    """

    def __init__(self,
                 sample_rate: int = 16000,
                 frame_size:  int = 1024,
                 device_index: Optional[int] = None):
        self.sample_rate  = sample_rate
        self.frame_size   = frame_size
        self.device_index = device_index
        self._q: queue.Queue[Optional[PhononFrame]] = queue.Queue(maxsize=64)
        self._stream  = None
        self._pa      = None
        self._running = False

    def start(self) -> None:
        import pyaudio
        self._pa = pyaudio.PyAudio()

        def _callback(in_data, frame_count, time_info, status):
            ints   = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
            ints  /= 32768.0
            frame  = PhononFrame.from_pcm(ints, self.sample_rate)
            try:
                self._q.put_nowait(frame)
            except queue.Full:
                self._q.get_nowait()
                self._q.put_nowait(frame)
            return (None, pyaudio.paContinue)

        self._stream = self._pa.open(
            format            = pyaudio.paInt16,
            channels          = 1,
            rate              = self.sample_rate,
            input             = True,
            input_device_index= self.device_index,
            frames_per_buffer = self.frame_size,
            stream_callback   = _callback,
        )
        self._stream.start_stream()
        self._running = True

    def stop(self) -> None:
        self._running = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa:
            self._pa.terminate()
        self._q.put(None)

    def get(self, timeout: float = 0.1) -> Optional[PhononFrame]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def __iter__(self) -> Iterator[PhononFrame]:
        while True:
            f = self.get()
            if f is None:
                return
            yield f

    @staticmethod
    def list_devices() -> None:
        import pyaudio
        pa = pyaudio.PyAudio()
        print(f"  {'Idx':<4} {'Name':<48} {'Channels'}")
        for i in range(pa.get_device_count()):
            d = pa.get_device_info_by_index(i)
            if d['maxInputChannels'] > 0:
                print(f"  {i:<4} {d['name'][:47]:<48} {d['maxInputChannels']}")
        pa.terminate()


# ── auto-select: QPhonon if Qt available, PPhonon otherwise ───────────────────

def make_phonon(sample_rate: int = 16000,
                frame_size:  int = 1024,
                prefer_qt:   bool = True) -> 'QPhonon | PPhonon':
    """
    Return a QPhonon if PyQt5 multimedia is available, else PPhonon.

    Both have identical start() / stop() / get() / __iter__() interfaces.
    Call start() before iterating.
    """
    if prefer_qt:
        try:
            from PyQt5.QtMultimedia import QAudioInput  # noqa: F401
            return QPhonon(sample_rate=sample_rate, frame_size=frame_size)
        except ImportError:
            pass
    return PPhonon(sample_rate=sample_rate, frame_size=frame_size)


# ── CLI demo ──────────────────────────────────────────────────────────────────

_DIM_NAMES = [
    'identity','negate','bind','name','apply','abstract','branch','iterate',
    'recurse','allocate','query','derefer','compose','parallelize','interrupt','emit',
]

if __name__ == '__main__':
    import argparse, sys

    ap = argparse.ArgumentParser(description='phonon — acoustic quantum test')
    ap.add_argument('--qt',      action='store_true', help='Force QPhonon (Qt)')
    ap.add_argument('--py',      action='store_true', help='Force PPhonon (Python)')
    ap.add_argument('--list',    action='store_true', help='List input devices')
    ap.add_argument('--frames',  type=int, default=20, help='Frames to capture')
    ap.add_argument('--rate',    type=int, default=16000)
    ap.add_argument('--size',    type=int, default=1024)
    args = ap.parse_args()

    if args.list:
        PPhonon.list_devices()
        sys.exit(0)

    if args.qt:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        src = QPhonon(sample_rate=args.rate, frame_size=args.size)
    elif args.py:
        src = PPhonon(sample_rate=args.rate, frame_size=args.size)
    else:
        if args.qt:
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
        src = make_phonon(args.rate, args.size, prefer_qt=not args.py)

    src.start()
    print()
    print('═' * 64)
    print('  phonon — acoustic quantum stream')
    print(f'  {"backend":<12} {src.__class__.__name__}')
    print(f'  {"rate":<12} {args.rate} Hz')
    print(f'  {"frame":<12} {args.size} samples  ({args.size/args.rate*1000:.1f} ms)')
    print('═' * 64)
    print()
    print(f'  {"Frame":<6} {"dB":>6}  {"dom γ":<8} {"layer"}  {"dominant e_dim"}')
    print('  ' + '─' * 52)

    _state = {'count': 0}
    if args.qt:
        from PyQt5.QtCore import QTimer
        def _tick():
            count = _state['count']
            f = src.get(timeout=0.0)
            if f is None:
                return
            bar  = '█' * min(40, max(0, int((f.energy_db + 60) * 0.6)))
            name = _DIM_NAMES[f.dominant_dim]
            print(f'  {count:<6} {f.energy_db:>6.1f}  '
                  f'γ{f.dominant_zero+1:<6} {f.layer:<5}  '
                  f'e{f.dominant_dim} {name}  {bar}')
            _state['count'] += 1
            if _state['count'] >= args.frames:
                src.stop()
                app.quit()
        timer = QTimer()
        timer.timeout.connect(_tick)
        timer.start(30)
        sys.exit(app.exec_())
    else:
        for f in src:
            count = _state['count']
            bar  = '█' * min(40, max(0, int((f.energy_db + 60) * 0.6)))
            name = _DIM_NAMES[f.dominant_dim]
            print(f'  {count:<6} {f.energy_db:>6.1f}  '
                  f'γ{f.dominant_zero+1:<6} {f.layer:<5}  '
                  f'e{f.dominant_dim} {name}  {bar}')
            _state['count'] += 1
            if _state['count'] >= args.frames:
                src.stop()
                break

    print()
    print('  nominal.')
