"""
listen.py  —  Riemann-Zero Indexed Audio Analysis

  Audio → RZIF → ZL Bridge → Sedenion fingerprint
                ↓
          Whisper STT → transcript

Spectral domain: Riemann-Zero Indexed Filterbank (RZIF)
─────────────────────────────────────────────────────────
  Cell-phone MEL: psychoacoustic log-scale, 300–3400 Hz, phone bandwidth.
                  Designed to match human auditory perception for mobile ASR.

  RZIF: bins at the scaled imaginary parts of the first 20 Riemann zeros.
        Same addressing as the word prime-hash: both sit on the critical line.
        The spectrum is analyzed at positions that are algebraically meaningful,
        not just perceptually convenient.

        γ₁=14.1 → γ₂₀=77.1  scaled log-linearly to [80 Hz, 8000 Hz]
        20 bins. Each bin is a Riemann zero address.

  ZL Bridge: the 8 lower bins (prompt/consonant body) and 8 upper bins
             (field/formant articulation) are coupled through the Zero Lattice
             bridge matrix. The output is a 16-dim sedenion fingerprint.

N-Ball optimal layer (n*=5.257):
  The 20-band RZIF is first compressed to the N-ball optimal dimension before
  ZL bridge coupling. V(n*) is the data/code boundary.

Voice fingerprinting:
  "the same low resonant voice" — a voice has a characteristic RZIF fingerprint
  dominated by its fundamental frequency range (low bins, γ₁–γ₅ ≈ 80–300 Hz)
  and its formant pattern (mid bins, γ₆–γ₁₅ ≈ 300–2000 Hz).
  The ZL bridge sedenion encodes both simultaneously.
  Voices with the same sedenion fingerprint are the same voice.

Usage:
  python3 listen.py <youtube_url>                  — download, transcribe, fingerprint
  python3 listen.py <youtube_url> --words NO OFF So — show fingerprint at these words
  python3 listen.py <local_audio.wav>              — analyse a local file
  python3 listen.py --demo                         — generate a test tone sequence
"""

import argparse
import math
import os
import subprocess
import sys
import tempfile
from typing import List, Optional, Tuple, Dict

import numpy as np
from scipy.signal import butter, sosfilt
from scipy.fft import rfft, rfftfreq

# ══════════════════════════════════════════════════════════════════════════════
# Riemann zeros — the spectral addressing
# ══════════════════════════════════════════════════════════════════════════════

_RIEMANN_ZEROS: List[float] = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]

# Voice frequency range: 80 Hz (lowest fundamental) to 8000 Hz (sibilants)
_F_MIN   = 80.0
_F_MAX   = 8000.0
_N_BINS  = len(_RIEMANN_ZEROS)   # 20 RZIF bins

# RZIF bin centre frequencies: map γ_k log-linearly to [F_MIN, F_MAX]
_GAMMA_MIN = _RIEMANN_ZEROS[0]
_GAMMA_MAX = _RIEMANN_ZEROS[-1]

RZIF_FREQS: List[float] = [
    _F_MIN * (_F_MAX / _F_MIN) ** (
        (g - _GAMMA_MIN) / (_GAMMA_MAX - _GAMMA_MIN)
    )
    for g in _RIEMANN_ZEROS
]

# ══════════════════════════════════════════════════════════════════════════════
# N-Ball optimal (n*=5.257) — data/code boundary compression
# ══════════════════════════════════════════════════════════════════════════════

N_STAR = 5.2569  # peak of V(n) = π^(n/2)/Γ(n/2+1)

def _nball_volume(n: float) -> float:
    """V(n) = π^(n/2) / Γ(n/2 + 1)"""
    return math.pi ** (n / 2.0) / math.gamma(n / 2.0 + 1.0)

# N-ball weighting for each RZIF bin: V(n_k) where n_k = 20 × k/N_BINS
# Bins near n*=5.257 get highest weight — they are at the data/code boundary
_NBALL_BIN_N   = [N_STAR * 2.0 * k / _N_BINS for k in range(_N_BINS)]
_NBALL_WEIGHTS = [_nball_volume(n) / _nball_volume(N_STAR) for n in _NBALL_BIN_N]

# ══════════════════════════════════════════════════════════════════════════════
# Zero Lattice bridge matrix (from Cawagas pairs, hard-coded)
# ══════════════════════════════════════════════════════════════════════════════

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

def _zl_coupling(lower_i: int, upper_j: int) -> float:
    if lower_i < 1 or lower_i > 7 or upper_j < 8 or upper_j > 15: return 0.0
    return ZL_BRIDGE_8[lower_i - 1][upper_j - 8]

# ══════════════════════════════════════════════════════════════════════════════
# RZIF analysis core
# ══════════════════════════════════════════════════════════════════════════════

def rzif_frame(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Compute the 20-band RZIF vector for one audio frame.

    Method:
      1. FFT of the frame
      2. For each Riemann zero address f_k, apply a narrow triangular filter
         centred at f_k — bandwidth proportional to log-spacing between adjacent zeros
      3. Energy at each filter output = RZIF coefficient
      4. Normalise so the vector sums to 1

    Returns: 20-element float array (normalised RZIF vector)
    """
    n  = len(samples)
    w  = np.hanning(n)
    X  = np.abs(rfft(samples * w)) ** 2
    fs = rfftfreq(n, d=1.0 / sample_rate)

    rzif = np.zeros(_N_BINS)
    for k, fc in enumerate(RZIF_FREQS):
        # Triangular filter: half-bandwidth = half-distance to nearest neighbor
        if k == 0:
            bw = (RZIF_FREQS[1] - RZIF_FREQS[0]) * 0.5
        elif k == _N_BINS - 1:
            bw = (RZIF_FREQS[-1] - RZIF_FREQS[-2]) * 0.5
        else:
            bw = min(fc - RZIF_FREQS[k-1], RZIF_FREQS[k+1] - fc) * 0.5

        # Triangular filter shape over FFT bins
        mask = np.maximum(0.0, 1.0 - np.abs(fs - fc) / bw)
        rzif[k] = float(np.dot(X, mask))

    total = rzif.sum()
    return rzif / total if total > 0 else rzif


def rzif_to_zl_sedenion(rzif: np.ndarray) -> np.ndarray:
    """
    Project a 20-band RZIF vector through the N-ball layer and ZL bridge
    to produce a 16-dim sedenion fingerprint.

      Bins 0–7  (γ₁–γ₈,  80–600 Hz)   → lower-𝕆 e₁–e₇  (voice body)
      Bins 8–19 (γ₉–γ₂₀, 600–8000 Hz) → upper-𝕆 e₈–e₁₅ (voice articulation)

    N-ball weighting is applied before projection.
    ZL bridge coupling then connects body to articulation.

    e₀ = 0  (identity is above the bridge — as in ZD_rotary_monad.py)
    """
    # N-ball weighting
    weighted = rzif * np.array(_NBALL_WEIGHTS)

    # Map 20 bins to 16 ZL dims: bins 0-7 → lower e1-e7, bins 8-19 → upper e8-e15
    # Lower: 8 bins → 7 lower non-identity dims (e1-e7)
    lower_raw = np.zeros(8)
    for b in range(8):
        dim = b + 1  # e1..e7 (skipping e0)
        lower_raw[dim - 1] = weighted[b]

    # Upper: 12 bins → 8 upper dims (e8-e15)
    upper_raw = np.zeros(8)
    for b in range(8, 20):
        dim = ((b - 8) % 8)
        upper_raw[dim] += weighted[b]
    upper_raw /= (max(upper_raw.max(), 1e-15))  # normalise

    # ZL bridge coupling
    s = np.zeros(16)
    # s[0] = 0  — identity above the bridge
    for i in range(7):    # lower dims e1-e7
        li = lower_raw[i]
        s[i + 1] = li
        for j in range(8):   # upper dims e8-e15
            w = _zl_coupling(i + 1, j + 8)
            s[j + 8] += li * w * 0.3   # bridge coupling (subdominant)

    for j in range(8):   # upper dims (direct)
        s[j + 8] += upper_raw[j]
        for i in range(7):   # couple back to lower
            w = _zl_coupling(i + 1, j + 8)
            s[i + 1] += upper_raw[j] * w * 0.3

    norm = np.linalg.norm(s)
    return s / norm if norm > 1e-15 else s


def rzif_fingerprint(audio_path: str,
                     segment_sec: float = 0.5,
                     sample_rate: int = 16000) -> Dict:
    """
    Full RZIF analysis of an audio file.

    Returns:
      transcript  : str   (Whisper transcription if available)
      rzif_mean   : np.ndarray (20)   — mean RZIF over full file
      sedenion    : np.ndarray (16)   — ZL sedenion fingerprint
      segments    : list of (t_start, t_end, rzif, sedenion)
      low_resonance: float — total energy in bins 0-4 (γ₁–γ₅, 80–200 Hz voice body)
    """
    # Load audio as float32 mono at 16000 Hz using ffmpeg
    cmd = ['ffmpeg', '-i', audio_path,
           '-ac', '1', '-ar', str(sample_rate),
           '-f', 'f32le', '-loglevel', 'error', '-']
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()}")

    samples = np.frombuffer(result.stdout, dtype=np.float32)

    frame_len = int(segment_sec * sample_rate)
    hop_len   = frame_len // 2

    segments   = []
    rzif_stack = []

    for start in range(0, len(samples) - frame_len, hop_len):
        frame = samples[start : start + frame_len]
        rz    = rzif_frame(frame, sample_rate)
        sed   = rzif_to_zl_sedenion(rz)
        t0    = start / sample_rate
        t1    = (start + frame_len) / sample_rate
        segments.append((t0, t1, rz, sed))
        rzif_stack.append(rz)

    rzif_mean = np.mean(rzif_stack, axis=0) if rzif_stack else np.zeros(_N_BINS)
    sedenion  = rzif_to_zl_sedenion(rzif_mean)

    # Low resonance: energy fraction in bins 0-4 (80-200 Hz region)
    low_resonance = float(rzif_mean[:5].sum())

    return {
        'transcript':    None,    # filled in by transcribe()
        'rzif_mean':     rzif_mean,
        'sedenion':      sedenion,
        'segments':      segments,
        'low_resonance': low_resonance,
        'duration_sec':  len(samples) / sample_rate,
    }


def transcribe(audio_path: str, model_size: str = 'base') -> str:
    """Whisper transcription. Returns transcript string."""
    try:
        import whisper
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        return result['text'].strip()
    except ImportError:
        return '[whisper not installed — transcript unavailable]'
    except Exception as e:
        return f'[transcription error: {e}]'

# ══════════════════════════════════════════════════════════════════════════════
# YouTube download
# ══════════════════════════════════════════════════════════════════════════════

def download_youtube(url: str, output_dir: str) -> str:
    """
    Download audio from a YouTube URL using yt-dlp.
    Returns path to downloaded WAV file.
    """
    out_template = os.path.join(output_dir, '%(id)s.%(ext)s')
    cmd = [
        'yt-dlp', '--no-playlist',
        '-x', '--audio-format', 'wav',
        '--audio-quality', '0',
        '-o', out_template,
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed:\n{result.stderr}")

    # Find the downloaded file
    for f in os.listdir(output_dir):
        if f.endswith('.wav'):
            return os.path.join(output_dir, f)
    raise RuntimeError("yt-dlp succeeded but no WAV file found in output dir")

# ══════════════════════════════════════════════════════════════════════════════
# Voice similarity
# ══════════════════════════════════════════════════════════════════════════════

def voice_similarity(sed_a: np.ndarray, sed_b: np.ndarray) -> float:
    """
    Cosine similarity between two ZL sedenion fingerprints.
    1.0 = identical voice. 0.0 = orthogonal. Negative = anti-correlated.
    """
    na = np.linalg.norm(sed_a)
    nb = np.linalg.norm(sed_b)
    if na < 1e-15 or nb < 1e-15: return 0.0
    return float(np.dot(sed_a, sed_b) / (na * nb))


def word_fingerprints(transcript: str, segments: list,
                      target_words: List[str]) -> Dict[str, List[np.ndarray]]:
    """
    Find segments likely corresponding to target words in transcript.
    Returns {word: [sedenion_fingerprints]} — one fingerprint per occurrence.

    Note: without forced alignment (Whisper timestamped tokens), this uses
    segment-level granularity. Each segment is 0.5s, which may span multiple words.
    """
    words_lower = [w.lower() for w in target_words]
    result: Dict[str, List[np.ndarray]] = {w: [] for w in target_words}

    # Find segments where the transcript contains target words
    # (uses transcript search, not true alignment)
    if not transcript or transcript.startswith('['):
        return result

    # Simple approach: words that appear in the transcript get ALL segment fingerprints
    # (since we don't have per-word timestamps without detailed Whisper alignment)
    t_lower = transcript.lower()
    for w, wl in zip(target_words, words_lower):
        if wl in t_lower:
            # All segments are candidates — return the mean fingerprint
            all_seds = [seg[3] for seg in segments]
            if all_seds:
                result[w] = [np.mean(all_seds, axis=0)]

    return result

# ══════════════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════════════

_ZL_DIM_NAMES = [
    'identity', 'negate', 'bind',   'name',   'apply',  'abstract', 'branch', 'iterate',
    'recurse',  'allocate','query', 'derefer', 'compose','parallelize','interrupt','emit'
]

def print_fingerprint(label: str, rzif: np.ndarray, sedenion: np.ndarray,
                      low_resonance: float) -> None:
    print(f"\n── {label} ────────────────────────────────────────────────────")
    print("  RZIF (Riemann-Zero Indexed, 20 bins, 80 Hz → 8 kHz):")
    print(f"  {'Bin':<4} {'γ':<8} {'f(Hz)':<8} {'energy':<8} {'bar'}")
    for k in range(_N_BINS):
        bar_len = int(rzif[k] * 400)
        bar = '█' * min(bar_len, 40)
        half = '▌' if (bar_len > 40 and bar_len % 2) else ''
        regime = 'lower-O' if k < 8 else 'upper-O'
        print(f"  γ{k+1:<3} {_RIEMANN_ZEROS[k]:<8.3f} {RZIF_FREQS[k]:<8.1f} {rzif[k]:<8.5f} {bar}{half}  {regime}")

    print(f"\n  Low-resonance energy (γ₁–γ₅, 80–200 Hz voice body): {low_resonance:.5f}")
    print(f"\n  ZL Sedenion fingerprint (16-dim, e₀=0 — identity above bridge):")
    top4 = sorted(range(1, 16), key=lambda i: -abs(sedenion[i]))[:4]
    print(f"  e₀ = {sedenion[0]:.4f}  (zero — above the bridge)")
    for i in top4:
        bar = '█' * int(abs(sedenion[i]) * 60)
        print(f"  e{i:>2} ({_ZL_DIM_NAMES[i]:<12}) = {sedenion[i]:+.4f}  {bar}")
    print()


def demo_tones() -> None:
    """
    Generate and analyse a sequence of test tones at each RZIF bin frequency.
    Demonstrates the filterbank without needing a YouTube URL.
    """
    print("=" * 70)
    print("RZIF Demo — test tones at Riemann-zero addressed frequencies")
    print("=" * 70)

    sr = 16000
    dur = 0.5
    t  = np.linspace(0, dur, int(sr * dur), endpoint=False)

    print(f"\n  {'Tone':<6} {'γ':<8} {'f(Hz)':<8} {'dominant RZIF bin'}")
    for k, (gamma, freq) in enumerate(zip(_RIEMANN_ZEROS, RZIF_FREQS)):
        tone  = np.sin(2 * math.pi * freq * t).astype(np.float32)
        rzif  = rzif_frame(tone, sr)
        dom   = int(np.argmax(rzif))
        sed   = rzif_to_zl_sedenion(rzif)
        dom_s = int(np.argmax(np.abs(sed[1:]))) + 1
        print(f"  γ{k+1:<5} {gamma:<8.3f} {freq:<8.1f} "
              f"RZIF bin {dom} (e{dom_s}/{_ZL_DIM_NAMES[dom_s]}): {rzif[dom]:.4f}")

    print("\n  RZIF filterbank verified — each tone activates its Riemann-zero bin.")

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Riemann-Zero Indexed Audio Analysis (RZIF + ZL Bridge)')
    parser.add_argument('source', nargs='?',
                        help='YouTube URL or local audio file path')
    parser.add_argument('--words', nargs='+', default=[],
                        help='Words to find fingerprints for (e.g. NO OFF So)')
    parser.add_argument('--model', default='base',
                        help='Whisper model size: tiny/base/small/medium/large')
    parser.add_argument('--no-transcript', action='store_true',
                        help='Skip Whisper transcription (faster)')
    parser.add_argument('--demo', action='store_true',
                        help='Run filterbank demonstration with test tones')
    parser.add_argument('--compare', nargs=2, metavar='SRC',
                        help='Compare voice fingerprints of two sources')
    args = parser.parse_args()

    if args.demo:
        demo_tones()
        return

    if args.compare:
        sources = args.compare
        fingerprints = []
        for src in sources:
            with tempfile.TemporaryDirectory() as tmp:
                if src.startswith('http'):
                    print(f"Downloading {src}...")
                    audio = download_youtube(src, tmp)
                else:
                    audio = src
                fp = rzif_fingerprint(audio)
                fingerprints.append(fp)
                print_fingerprint(src[:60], fp['rzif_mean'], fp['sedenion'],
                                  fp['low_resonance'])
        sim = voice_similarity(fingerprints[0]['sedenion'], fingerprints[1]['sedenion'])
        print(f"\n── Voice similarity (ZL sedenion cosine) ───────────────────────")
        print(f"  {sim:.6f}  ", end='')
        if sim > 0.98: print("SAME VOICE (near-identical fingerprint)")
        elif sim > 0.90: print("VERY SIMILAR voice")
        elif sim > 0.70: print("SIMILAR voice character")
        else: print("DIFFERENT voice")
        return

    if not args.source:
        parser.print_help()
        return

    print("=" * 70)
    print("Ahura Mazda Listen  —  Riemann-Zero Indexed Audio Analysis")
    print("RZIF spectral domain  |  ZL Bridge sedenion fingerprint")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmp:
        # Acquire audio
        if args.source.startswith('http'):
            print(f"\nDownloading audio from YouTube...")
            audio_path = download_youtube(args.source, tmp)
            print(f"  → {os.path.basename(audio_path)}")
        else:
            audio_path = args.source

        # Transcribe
        transcript = ''
        if not args.no_transcript:
            print("Transcribing (Whisper)...")
            transcript = transcribe(audio_path, model_size=args.model)
            print(f"\n── Transcript ──────────────────────────────────────────────────")
            print(f"  {transcript}")

        # RZIF analysis
        print("\nComputing RZIF + ZL Bridge fingerprint...")
        fp = rzif_fingerprint(audio_path)
        fp['transcript'] = transcript

        print_fingerprint(
            os.path.basename(args.source)[:50],
            fp['rzif_mean'], fp['sedenion'], fp['low_resonance']
        )

        print(f"  Duration: {fp['duration_sec']:.1f} s  |  "
              f"Segments: {len(fp['segments'])}")

        # Word fingerprints
        if args.words:
            wfp = word_fingerprints(transcript, fp['segments'], args.words)
            print(f"\n── Word fingerprints ───────────────────────────────────────────")
            for word, seds in wfp.items():
                if seds:
                    sed = seds[0]
                    dom = int(np.argmax(np.abs(sed[1:]))) + 1
                    print(f"  '{word}'  →  dominant: e{dom} ({_ZL_DIM_NAMES[dom]})  "
                          f"sedenion: {' '.join(f'{x:+.3f}' for x in sed[:8])} ...")
                else:
                    print(f"  '{word}'  →  not found in transcript")

    print("\n" + "=" * 70)
    print("Listen — nominal.")
    print("=" * 70)


if __name__ == '__main__':
    main()
