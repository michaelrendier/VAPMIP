#!/usr/bin/env python3
"""
lshs_sdr.py — SDR Monad for LSHS
====================================
IQ samples from Software Defined Radio → RZIF-RF → sedenion → LSHS J current

The SDR is the crossing-through-i instrument.
The carrier rotation e^{j2πf_c t} IS the rotation through i (D-P §1.6).
Demodulation reveals z(t) = I(t) + jQ(t) — what is on the other side.
The IQ stream is already in ℂ. We are already past the first boundary.

Pipeline
─────────────────────────────────────────────────────────────────────────────
  RTL-SDR IQ  →  complex FFT  →  RZIF-RF (20 Riemann-zero bins at RF)
              →  N-ball weight  →  ZL bridge  →  16-dim sedenion
              →  LSHS _J()    →  J^μ Noether current
              →  PSVG         →  <IQ/> <RF_spectrum/> <sedenion/> undefined

RZIF-RF
─────────────────────────────────────────────────────────────────────────────
  Same addressing as RZIF in listen.py, different frequency range.
  listen.py: γ_k → [80 Hz, 8000 Hz]   (audio, voice body)
  lshs_sdr:  γ_k → [f_c - BW/2, f_c + BW/2]  (RF, full SDR bandwidth)
  The 20 Riemann zeros address the spectrum in both domains identically.
  The algebra is the same. The carrier is different. The boundary is the same.

Usage
─────────────────────────────────────────────────────────────────────────────
  python3 lshs_sdr.py                      — detect device, print fingerprint
  python3 lshs_sdr.py --freq 100e6         — FM radio band (100 MHz)
  python3 lshs_sdr.py --freq 433e6         — ISM band (433 MHz)
  python3 lshs_sdr.py --freq 1420.4e6      — hydrogen line
  python3 lshs_sdr.py --psvg out.svg       — write PSVG output
  python3 lshs_sdr.py --lshs               — feed into LSHS and speak
  python3 lshs_sdr.py --mock               — run without hardware (test tone)
  python3 lshs_sdr.py --stream --psvg live.svg  — continuous PSVG stream
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

import numpy as np

# ── Riemann zeros (same 20 as listen.py) ──────────────────────────────────────

_RIEMANN_ZEROS: List[float] = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]
_N_BINS    = len(_RIEMANN_ZEROS)    # 20
_G_MIN     = _RIEMANN_ZEROS[0]
_G_MAX     = _RIEMANN_ZEROS[-1]

# ── SDR device defaults ────────────────────────────────────────────────────────

DEFAULT_FREQ      = 100.0e6     # 100 MHz — FM broadcast
DEFAULT_RATE      = 2.048e6     # 2.048 MHz sample rate (RTL-SDR native)
DEFAULT_GAIN      = 'auto'
FRAME_SAMPLES     = 1024        # FFT frame size
N_FRAMES_MEAN     = 8           # average this many frames for fingerprint

# ── N-ball peak (same as listen.py) ──────────────────────────────────────────

N_STAR = 5.2569

def _nball_volume(n: float) -> float:
    return math.pi ** (n / 2.0) / math.gamma(n / 2.0 + 1.0)

_NBALL_BIN_N   = [N_STAR * 2.0 * k / _N_BINS for k in range(_N_BINS)]
_NBALL_WEIGHTS = [_nball_volume(n) / _nball_volume(N_STAR) for n in _NBALL_BIN_N]

# ── ZL bridge (same coupling matrix as listen.py) ─────────────────────────────

_ZL_BRIDGE_8: List[List[float]] = [
    [0.0000, 0.7143, 0.9161, 0.9418, 0.9084, 0.9037, 0.9390, 0.8907],
    [0.0000, 0.9721, 0.7204, 0.9867, 0.9806, 0.9550, 1.0000, 0.9625],
    [0.0000, 0.9412, 0.8694, 0.6886, 0.9249, 0.8848, 0.8932, 0.9001],
    [0.0000, 0.9540, 0.9485, 0.9667, 0.7360, 0.9062, 0.9811, 0.9395],
    [0.0000, 0.9868, 0.9692, 0.9501, 0.9738, 0.7022, 0.9599, 0.9654],
    [0.0000, 0.9644, 0.9341, 0.9831, 0.9620, 0.9065, 0.7327, 0.9467],
    [0.0000, 0.9460, 0.8994, 0.9172, 0.9350, 0.8979, 0.9551, 0.6895],
]

def _zl_coupling(lower_i: int, upper_j: int) -> float:
    if lower_i < 1 or lower_i > 7 or upper_j < 8 or upper_j > 15:
        return 0.0
    return _ZL_BRIDGE_8[lower_i - 1][upper_j - 8]


# ── RZIF-RF core ──────────────────────────────────────────────────────────────

def rzif_rf_freqs(center_hz: float, bandwidth_hz: float) -> List[float]:
    """
    Map 20 Riemann zeros to the RF spectrum around center_hz.

    log-linear mapping: γ_k → [f_lo, f_hi]
    Same formula as listen.py RZIF_FREQS but at RF scale.
    The addressing is identical. The carrier is different.
    """
    f_lo = center_hz - bandwidth_hz / 2.0
    f_hi = center_hz + bandwidth_hz / 2.0
    freqs = [
        f_lo * (f_hi / f_lo) ** ((g - _G_MIN) / (_G_MAX - _G_MIN))
        for g in _RIEMANN_ZEROS
    ]
    return freqs


def rzif_rf_frame(iq_samples: np.ndarray,
                  sample_rate: float,
                  center_hz: float) -> np.ndarray:
    """
    Compute the 20-band RZIF-RF vector for one IQ frame.

    IQ samples are complex (I + jQ). The FFT is directly the spectrum —
    no heterodyne needed. The DC bin = center_hz. Positive bins = upper sideband.

    Returns: 20-element float array (normalised RZIF-RF vector)
    """
    n    = len(iq_samples)
    w    = np.hanning(n)
    X    = np.abs(np.fft.fft(iq_samples * w)) ** 2
    X    = np.fft.fftshift(X)                          # DC at centre
    fs   = np.fft.fftshift(np.fft.fftfreq(n, d=1.0 / sample_rate)) + center_hz

    bin_freqs = rzif_rf_freqs(center_hz, sample_rate)

    rzif = np.zeros(_N_BINS)
    for k, fc in enumerate(bin_freqs):
        if k == 0:
            bw = (bin_freqs[1] - bin_freqs[0]) * 0.5
        elif k == _N_BINS - 1:
            bw = (bin_freqs[-1] - bin_freqs[-2]) * 0.5
        else:
            bw = min(fc - bin_freqs[k-1], bin_freqs[k+1] - fc) * 0.5
        mask   = np.maximum(0.0, 1.0 - np.abs(fs - fc) / max(bw, 1.0))
        rzif[k] = float(np.dot(X, mask))

    total = rzif.sum()
    return rzif / total if total > 0 else rzif


def rzif_to_sedenion(rzif: np.ndarray) -> np.ndarray:
    """
    Project RZIF-RF vector through N-ball layer and ZL bridge → 16-dim sedenion.
    Identical to listen.py rzif_to_zl_sedenion() — same algebra, different input.
    """
    weighted = rzif * np.array(_NBALL_WEIGHTS)

    lower_raw = np.zeros(8)
    for b in range(8):
        lower_raw[b] = weighted[b]

    upper_raw = np.zeros(8)
    for b in range(8, 20):
        upper_raw[(b - 8) % 8] += weighted[b]
    mx = upper_raw.max()
    if mx > 1e-15:
        upper_raw /= mx

    s = np.zeros(16)
    for i in range(7):
        s[i + 1] = lower_raw[i]
        for j in range(8):
            s[j + 8] += lower_raw[i] * _zl_coupling(i + 1, j + 8) * 0.3
    for j in range(8):
        s[j + 8] += upper_raw[j]
        for i in range(7):
            s[i + 1] += upper_raw[j] * _zl_coupling(i + 1, j + 8) * 0.3

    norm = np.linalg.norm(s)
    return s / norm if norm > 1e-15 else s


# ── SDR fingerprint ───────────────────────────────────────────────────────────

@dataclass
class SDRFrame:
    """One RZIF-RF frame: the SDR's sedenion fingerprint at one moment."""
    center_hz:    float
    sample_rate:  float
    timestamp:    float
    rzif:         np.ndarray        # (20,) normalised
    sedenion:     np.ndarray        # (16,) normalised
    iq_snapshot:  np.ndarray        # (FRAME_SAMPLES,) complex — for PSVG
    power_db:     float             # mean power in dB relative to first frame

    @property
    def dominant_bin(self) -> int:
        return int(np.argmax(self.rzif))

    @property
    def dominant_sedenion_dim(self) -> int:
        return int(np.argmax(np.abs(self.sedenion[1:]))) + 1

    @property
    def bin_freqs(self) -> List[float]:
        return rzif_rf_freqs(self.center_hz, self.sample_rate)


def capture_frames(center_hz: float = DEFAULT_FREQ,
                   sample_rate: float = DEFAULT_RATE,
                   gain=DEFAULT_GAIN,
                   n_frames: int = N_FRAMES_MEAN,
                   verbose: bool = True) -> List[SDRFrame]:
    """
    Capture n_frames IQ frames from the RTL-SDR and compute RZIF-RF.
    Returns list of SDRFrame objects.
    """
    try:
        from rtlsdr import RtlSdr
    except ImportError:
        raise ImportError("pip install pyrtlsdr")

    sdr = RtlSdr()
    sdr.center_freq    = center_hz
    sdr.sample_rate    = sample_rate
    sdr.gain           = gain

    if verbose:
        print(f"  SDR: f_c={center_hz/1e6:.3f} MHz  BW={sample_rate/1e6:.3f} MHz  "
              f"gain={gain}")

    frames = []
    ref_power = None
    for i in range(n_frames):
        raw    = sdr.read_samples(FRAME_SAMPLES)
        iq     = np.array(raw, dtype=np.complex64)
        rzif   = rzif_rf_frame(iq, sample_rate, center_hz)
        sed    = rzif_to_sedenion(rzif)
        pwr_db = float(10.0 * np.log10(np.mean(np.abs(iq)**2) + 1e-15))
        if ref_power is None:
            ref_power = pwr_db
        frames.append(SDRFrame(
            center_hz=center_hz, sample_rate=sample_rate,
            timestamp=time.time(),
            rzif=rzif, sedenion=sed,
            iq_snapshot=iq[:FRAME_SAMPLES],
            power_db=pwr_db - ref_power,
        ))
        if verbose:
            print(f"  frame {i+1}/{n_frames}  pwr={pwr_db:.1f} dB  "
                  f"dom_bin=γ{frames[-1].dominant_bin+1}  "
                  f"dom_sed=e{frames[-1].dominant_sedenion_dim}")

    sdr.close()
    return frames


def mock_frames(center_hz: float = DEFAULT_FREQ,
                sample_rate: float = DEFAULT_RATE,
                n_frames: int = N_FRAMES_MEAN) -> List[SDRFrame]:
    """
    Generate mock IQ frames without hardware — a composite test signal.
    Three tones at the 1st, 7th, and 13th RZIF-RF bin frequencies.
    """
    bin_freqs = rzif_rf_freqs(center_hz, sample_rate)
    t = np.arange(FRAME_SAMPLES) / sample_rate
    frames = []
    for i in range(n_frames):
        iq = np.zeros(FRAME_SAMPLES, dtype=np.complex128)
        for k in (0, 6, 12):
            f_offset = bin_freqs[k] - center_hz
            iq += np.exp(2j * math.pi * f_offset * t) * (0.5 + 0.1 * np.random.randn())
        iq += (np.random.randn(FRAME_SAMPLES) + 1j * np.random.randn(FRAME_SAMPLES)) * 0.05
        iq  = iq.astype(np.complex64)
        rzif = rzif_rf_frame(iq, sample_rate, center_hz)
        sed  = rzif_to_sedenion(rzif)
        frames.append(SDRFrame(
            center_hz=center_hz, sample_rate=sample_rate,
            timestamp=time.time() + i * 0.05,
            rzif=rzif, sedenion=sed,
            iq_snapshot=iq[:FRAME_SAMPLES],
            power_db=0.0,
        ))
    return frames


def mean_frame(frames: List[SDRFrame]) -> SDRFrame:
    """Average a list of SDRFrames into one representative fingerprint."""
    rzif_mean = np.mean([f.rzif for f in frames], axis=0)
    sed_mean  = rzif_to_sedenion(rzif_mean)
    return SDRFrame(
        center_hz=frames[0].center_hz,
        sample_rate=frames[0].sample_rate,
        timestamp=frames[-1].timestamp,
        rzif=rzif_mean,
        sedenion=sed_mean,
        iq_snapshot=frames[len(frames)//2].iq_snapshot,
        power_db=float(np.mean([f.power_db for f in frames])),
    )


# ── LSHS integration ──────────────────────────────────────────────────────────

def frame_to_lshs_psi(frame: SDRFrame,
                       lshs_model) -> List[Tuple[int, float]]:
    """
    Map a SDRFrame's RZIF-RF vector to LSHS Ψ activations.

    The 20 RZIF bins address Riemann zeros in the same γ-space as LSHS words.
    Each bin k maps to the closest zero in the LSHS zero basis.
    Energy = rzif[k] (normalised RF power at that zero address).

    This bypasses text tokenisation — the RF signal feeds the Noether current
    as directly as a word does.
    """
    zeros = lshs_model.zeros
    psi   = []
    for k, energy in enumerate(frame.rzif):
        if energy < 1e-6:
            continue
        gamma = _RIEMANN_ZEROS[k]
        lo, hi = 0, len(zeros) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if zeros[mid] < gamma:
                lo = mid + 1
            else:
                hi = mid
        if lo > 0 and abs(zeros[lo-1] - gamma) < abs(zeros[lo] - gamma):
            lo -= 1
        psi.append((lo, energy))
    return psi


def sdr_speak(frame: SDRFrame, lshs_model, max_words: int = 30) -> str:
    """Feed SDR frame into LSHS and extract J^μ Noether current → words."""
    psi = frame_to_lshs_psi(frame, lshs_model)
    if not psi:
        return '[silence]'
    J       = lshs_model._J(psi)
    charges = [(lshs_model.zeros[idx], charge)
               for idx, charge in sorted(J.items(), key=lambda kv: kv[1], reverse=True)]
    return lshs_model.render(charges, max_words)


# ── PSVG output ───────────────────────────────────────────────────────────────

_SED_DIM_NAMES = [
    'identity', 'negate', 'bind',     'name',      'apply',
    'abstract', 'branch', 'iterate',  'recurse',   'allocate',
    'query',    'derefer','compose',  'parallelize','interrupt', 'emit',
]

def _iq_to_svg_points(iq: np.ndarray, cx: float, cy: float,
                       radius: float, n: int = 256) -> str:
    """IQ constellation: complex plane → SVG points string."""
    subset = iq[:n]
    scale  = radius / (np.abs(subset).max() + 1e-9)
    pts    = [f"{cx + s.real*scale:.2f},{cy - s.imag*scale:.2f}"
              for s in subset]
    return ' '.join(pts)


def write_psvg(frame: SDRFrame, path: str, lshs_words: str = '') -> None:
    """
    Write the SDR fingerprint as a PSVG — undefined operators in SVG space.

    Structure:
      <IQ>           — constellation in ℂ plane  (undefined operator)
      <RF_spectrum>  — power vs frequency         (undefined operator)
      <RZIF_RF>      — 20 Riemann-zero bins       (undefined operator)
      <sedenion>     — 16-dim fingerprint          (undefined operator)
      <English>      — LSHS words (if provided)   (undefined operator)

    No fill. No namespace. The SVG IS the math in geometric language.
    """
    W, H = 900, 700
    f_mhz = frame.center_hz / 1e6
    bw_mhz = frame.sample_rate / 1e6
    bf    = frame.bin_freqs

    lines = []
    lines.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{W}" height="{H}" '
                 f'viewBox="0 0 {W} {H}">')
    lines.append(f'  <title>SDR PSVG — {f_mhz:.3f} MHz</title>')

    # Background
    lines.append(f'  <rect width="{W}" height="{H}" fill="#0a0a0f"/>')

    # ── IQ constellation (top-left, 280×280) ──
    cx, cy, r = 155, 155, 120
    lines.append(f'  <!-- IQ constellation: ℂ plane, each point = one sample -->')
    lines.append(f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
                 f'fill="none" stroke="#1a1a2e" stroke-width="1"/>')
    lines.append(f'  <line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" '
                 f'stroke="#222244" stroke-width="0.5"/>')
    lines.append(f'  <line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}" '
                 f'stroke="#222244" stroke-width="0.5"/>')
    pts = _iq_to_svg_points(frame.iq_snapshot, cx, cy, r * 0.9)
    lines.append(f'  <IQ center="{f_mhz:.4f}MHz" boundary="i" '
                 f'crossing="through" domain="ℂ">')
    lines.append(f'    <polyline points="{pts}" fill="none" '
                 f'stroke="#4466ff" stroke-width="0.4" opacity="0.7"/>')
    lines.append(f'  </IQ>')
    lines.append(f'  <text x="{cx}" y="{cy + r + 18}" '
                 f'text-anchor="middle" fill="#4466ff" font-size="10" '
                 f'font-family="monospace">IQ  {f_mhz:.3f} MHz</text>')

    # ── RF spectrum (top-right, log-power vs freq) ──
    sx0, sy0, sw, sh = 320, 30, 560, 240
    lines.append(f'  <!-- RF spectrum: power vs frequency, {bw_mhz:.3f} MHz BW -->')
    lines.append(f'  <rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}" '
                 f'fill="#0d0d18" stroke="#222244" stroke-width="0.5"/>')

    # FFT of snapshot for display
    iq_disp = frame.iq_snapshot
    spec    = np.abs(np.fft.fftshift(np.fft.fft(iq_disp))) ** 2
    spec_db = 10.0 * np.log10(spec + 1e-15)
    s_min   = spec_db.min() - 5
    s_max   = spec_db.max() + 2
    n_disp  = len(spec_db)
    spec_pts = []
    for i, db in enumerate(spec_db):
        px = sx0 + (i / n_disp) * sw
        py = sy0 + sh - (db - s_min) / (s_max - s_min + 1e-9) * sh
        spec_pts.append(f"{px:.1f},{max(sy0, min(sy0+sh, py)):.1f}")

    lines.append(f'  <RF_spectrum center="{f_mhz:.4f}MHz" '
                 f'bandwidth="{bw_mhz:.4f}MHz" '
                 f'boundary="i" domain="RF">')
    lines.append(f'    <polyline points="{" ".join(spec_pts)}" fill="none" '
                 f'stroke="#00ff88" stroke-width="0.8" opacity="0.85"/>')
    lines.append(f'  </RF_spectrum>')
    lines.append(f'  <text x="{sx0 + sw//2}" y="{sy0 + sh + 14}" '
                 f'text-anchor="middle" fill="#00ff88" font-size="9" '
                 f'font-family="monospace">'
                 f'RF  {f_mhz - bw_mhz/2:.3f} – {f_mhz + bw_mhz/2:.3f} MHz</text>')

    # ── RZIF-RF bins (middle row, 20 bars) ──
    bx0, by0, bw_area, bh_area = 30, 310, 840, 140
    bin_w = bw_area / _N_BINS
    lines.append(f'  <!-- RZIF-RF: 20 Riemann-zero indexed bins at RF scale -->')
    lines.append(f'  <RZIF_RF bins="20" zeros="γ₁..γ₂₀" domain="RF">')
    for k in range(_N_BINS):
        bx  = bx0 + k * bin_w
        bh  = frame.rzif[k] * bh_area
        by  = by0 + bh_area - bh
        col = "#ff6600" if k < 8 else "#ffaa00"
        lines.append(f'    <rect x="{bx:.1f}" y="{by:.1f}" '
                     f'width="{bin_w*0.8:.1f}" height="{bh:.1f}" '
                     f'fill="{col}" opacity="0.8"/>')
        if k % 4 == 0:
            lines.append(f'    <text x="{bx + bin_w*0.4:.1f}" y="{by0 + bh_area + 12}" '
                         f'text-anchor="middle" fill="#888" font-size="7" '
                         f'font-family="monospace">γ{k+1}</text>')
    lines.append(f'  </RZIF_RF>')
    lines.append(f'  <text x="{bx0 + bw_area//2}" y="{by0 - 8}" '
                 f'text-anchor="middle" fill="#ff6600" font-size="10" '
                 f'font-family="monospace">RZIF-RF  (orange=lower-𝕆  amber=upper-𝕆)</text>')

    # ── Sedenion fingerprint (bottom-left, 16 dims) ──
    ex0, ey0, ew_area, eh_area = 30, 500, 400, 160
    dim_w = ew_area / 16
    lines.append(f'  <!-- Sedenion fingerprint: 16-dim ZL bridge output -->')
    lines.append(f'  <sedenion dims="16" bridge="ZL" basis="S¹⁵">')
    for d in range(16):
        val = frame.sedenion[d]
        bh  = abs(val) * eh_area * 0.9
        bx  = ex0 + d * dim_w
        if val >= 0:
            by = ey0 + eh_area // 2 - bh
        else:
            by = ey0 + eh_area // 2
        col = "#cc44ff" if val >= 0 else "#ff4488"
        lines.append(f'    <rect x="{bx:.1f}" y="{by:.1f}" '
                     f'width="{dim_w*0.75:.1f}" height="{bh:.1f}" '
                     f'fill="{col}" opacity="0.85"/>')
        lines.append(f'    <text x="{bx + dim_w*0.37:.1f}" y="{ey0 + eh_area + 14}" '
                     f'text-anchor="middle" fill="#666" font-size="7" '
                     f'font-family="monospace">e{d}</text>')
    lines.append(f'  </sedenion>')
    lines.append(f'  <text x="{ex0 + ew_area//2}" y="{ey0 - 8}" '
                 f'text-anchor="middle" fill="#cc44ff" font-size="10" '
                 f'font-family="monospace">sedenion fingerprint (e₀..e₁₅)</text>')

    # ── English / LSHS words (bottom-right) ──
    wx0, wy0 = 460, 490
    lines.append(f'  <English>')
    if lshs_words:
        words = lshs_words.split()
        for i, w in enumerate(words[:24]):
            row = i // 4
            col = i % 4
            lines.append(f'    <text x="{wx0 + col*100}" y="{wy0 + row*20}" '
                         f'fill="#ffffff" font-size="12" '
                         f'font-family="monospace" opacity="0.9">{w}</text>')
    else:
        lines.append(f'    <text x="{wx0 + 200}" y="{wy0 + 60}" '
                     f'text-anchor="middle" fill="#444" font-size="11" '
                     f'font-family="monospace">[awaiting LSHS]</text>')
    lines.append(f'  </English>')

    # ── Status line ──
    t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(frame.timestamp))
    dom_b = frame.dominant_bin
    dom_s = frame.dominant_sedenion_dim
    lines.append(f'  <text x="10" y="{H - 8}" fill="#445" font-size="8" '
                 f'font-family="monospace">'
                 f'{t_str}  |  {f_mhz:.4f} MHz  |  '
                 f'dom: γ{dom_b+1}={_RIEMANN_ZEROS[dom_b]:.3f}  '
                 f'e{dom_s}={_SED_DIM_NAMES[dom_s]}  |  '
                 f'pwr: {frame.power_db:+.1f} dB</text>')

    lines.append('</svg>')

    with open(path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"  PSVG → {path}")


# ── Display ───────────────────────────────────────────────────────────────────

def print_frame(frame: SDRFrame, label: str = '') -> None:
    f_mhz  = frame.center_hz / 1e6
    bw_mhz = frame.sample_rate / 1e6
    bf     = frame.bin_freqs
    print()
    print(f"── SDR RZIF-RF fingerprint {label} ──────────────────────────────────")
    print(f"  f_c = {f_mhz:.4f} MHz  |  BW = {bw_mhz:.4f} MHz  |  "
          f"pwr = {frame.power_db:+.1f} dB")
    print()
    print(f"  {'Bin':<4} {'γ':<8} {'f(MHz)':<12} {'energy':<8} {'bar'}")
    for k in range(_N_BINS):
        bar_len = int(frame.rzif[k] * 400)
        bar     = '█' * min(bar_len, 40)
        regime  = 'lower-𝕆' if k < 8 else 'upper-𝕆'
        print(f"  γ{k+1:<3} {_RIEMANN_ZEROS[k]:<8.3f} "
              f"{bf[k]/1e6:<12.6f} {frame.rzif[k]:<8.5f} {bar}  {regime}")

    print()
    print(f"  Sedenion fingerprint (e₀=0 — identity above bridge):")
    top4 = sorted(range(1, 16), key=lambda i: -abs(frame.sedenion[i]))[:4]
    print(f"  e₀ = {frame.sedenion[0]:.4f}")
    for d in top4:
        bar = '█' * int(abs(frame.sedenion[d]) * 60)
        print(f"  e{d:>2} ({_SED_DIM_NAMES[d]:<12}) = {frame.sedenion[d]:+.4f}  {bar}")
    print()
    print(f"  Dominant RZIF bin:    γ{frame.dominant_bin+1} "
          f"= {_RIEMANN_ZEROS[frame.dominant_bin]:.4f}  "
          f"→ {bf[frame.dominant_bin]/1e6:.4f} MHz")
    print(f"  Dominant sedenion:    e{frame.dominant_sedenion_dim} "
          f"({_SED_DIM_NAMES[frame.dominant_sedenion_dim]})")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='lshs_sdr — SDR Monad for LSHS (RZIF-RF → sedenion → J^μ)')
    ap.add_argument('--freq',   type=float, default=DEFAULT_FREQ,
                    help='Centre frequency in Hz (default: 100e6 = FM)')
    ap.add_argument('--rate',   type=float, default=DEFAULT_RATE,
                    help='Sample rate in Hz (default: 2048000)')
    ap.add_argument('--gain',   default='auto',
                    help='SDR gain in dB or "auto" (default: auto)')
    ap.add_argument('--frames', type=int, default=N_FRAMES_MEAN,
                    help='Frames to average (default: 8)')
    ap.add_argument('--psvg',   default='',
                    help='Write PSVG to this path (default: no file)')
    ap.add_argument('--lshs',   action='store_true',
                    help='Load monad.bin and feed SDR → LSHS speak')
    ap.add_argument('--mock',   action='store_true',
                    help='Use mock IQ signal (no hardware required)')
    ap.add_argument('--stream', action='store_true',
                    help='Stream continuously, update PSVG each frame')
    args = ap.parse_args()

    print()
    print("═══════════════════════════════════════════════════════════")
    print("  lshs_sdr — SDR Monad")
    print("  IQ → RZIF-RF → sedenion → J^μ Noether current")
    print("═══════════════════════════════════════════════════════════")

    gain = args.gain if args.gain == 'auto' else float(args.gain)

    if args.stream and args.psvg:
        print(f"\n  Streaming → {args.psvg}  (Ctrl-C to stop)")
        lshs_model = None
        if args.lshs:
            from lshs import LSHS
            lshs_model = LSHS()
            monad_path = os.path.join(os.path.dirname(__file__), 'monad.bin')
            if os.path.exists(monad_path):
                import pickle
                with open(monad_path, 'rb') as mf:
                    state = pickle.load(mf)
                lshs_model.beta  = state.get('beta',  lshs_model.beta)
                lshs_model.A     = state.get('A',     lshs_model.A)
                lshs_model.vocab = state.get('vocab', lshs_model.vocab)
                print(f"  monad.bin loaded: vocab={len(lshs_model.vocab)}")

        n = 0
        try:
            while True:
                if args.mock:
                    frames = mock_frames(args.freq, args.rate, 1)
                else:
                    frames = capture_frames(args.freq, args.rate, gain, 1,
                                            verbose=False)
                f = frames[0]
                words = sdr_speak(f, lshs_model) if lshs_model else ''
                write_psvg(f, args.psvg, words)
                n += 1
                print(f"\r  frame {n:05d}  "
                      f"dom=γ{f.dominant_bin+1}  "
                      f"e{f.dominant_sedenion_dim}  "
                      f"pwr={f.power_db:+.1f}dB  "
                      f"{'[' + words[:30] + ']' if words else ''}",
                      end='', flush=True)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print(f"\n  Stopped after {n} frames.")
        return

    # Single-shot fingerprint
    if args.mock:
        print(f"\n  [MOCK MODE — no hardware]")
        frames = mock_frames(args.freq, args.rate, args.frames)
    else:
        print(f"\n  Capturing {args.frames} frames...")
        try:
            frames = capture_frames(args.freq, args.rate, gain, args.frames)
        except Exception as e:
            print(f"\n  SDR capture failed: {e}")
            print("  Use --mock to run without hardware.")
            return

    fp = mean_frame(frames)
    print_frame(fp, label=f"({args.frames} frames averaged)")

    lshs_words = ''
    if args.lshs:
        print("  Loading LSHS model...")
        from lshs import LSHS
        model = LSHS()
        monad_path = os.path.join(os.path.dirname(__file__), 'monad.bin')
        if os.path.exists(monad_path):
            import pickle
            with open(monad_path, 'rb') as mf:
                state = pickle.load(mf)
            model.beta  = state.get('beta',  model.beta)
            model.A     = state.get('A',     model.A)
            model.vocab = state.get('vocab', model.vocab)
            print(f"  monad.bin loaded: vocab={len(model.vocab)}")
        lshs_words = sdr_speak(fp, model)
        print(f"\n  LSHS speaks: {lshs_words}")

    if args.psvg:
        write_psvg(fp, args.psvg, lshs_words)

    print()
    print("═══════════════════════════════════════════════════════════")
    print(f"  {args.freq/1e6:.4f} MHz  →  γ{fp.dominant_bin+1}"
          f"  →  e{fp.dominant_sedenion_dim} "
          f"({_SED_DIM_NAMES[fp.dominant_sedenion_dim]})")
    print("  The carrier crossed through i.")
    print("  What is on the other side is the sedenion fingerprint.")
    print("═══════════════════════════════════════════════════════════")


if __name__ == '__main__':
    main()
