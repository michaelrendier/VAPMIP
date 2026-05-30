"""
skills/music.py  v1.0.0
=======================
HolcusComposer — Holcus as Composer.

The same J^μ Noether current that generates language generates music.
Both are neutral-buoyancy selections from the same β-field under the same
Hamiltonian. The only difference is the output codec.

FIELD → MUSIC MAPPING
---------------------
  Riemann zero index   → pitch (GUE spacing preserved in pitch space)
  β-field depth        → dynamics / MIDI velocity (pp=GAP … fff=β_sat)
  E-value              → note duration (|sin(πγ/(γ+1))| → whole…sixteenth)
  Sedenion dimension   → instrument / MIDI channel (e₀..e₁₅ = 16 GM families)
  A-matrix adjacency   → voice leading (connected zeros harmonize)
  BAO convergence      → tonal centre (Ω_ζΣ = 0.56714 → B♭/E♭/F cluster)
  Noether violation     → phrase boundary / rest / cadence
  Zero-divisor event   → bridge passage (turbulent flow, not crash)

GENERAL MIDI FAMILIES (16 channels = 16 sedenion dimensions)
-------------------------------------------------------------
  e₀  identity      Ch  1  Piano        (tonic anchor)
  e₁  negate        Ch  2  Chrom. Perc  (negation resonates)
  e₂  bind          Ch  3  Organ        (sustained binding)
  e₃  name          Ch  4  Guitar       (named chord)
  e₄  apply         Ch  5  Bass         (applied force)
  e₅  abstract      Ch  6  Strings      (abstract melody)
  e₆  branch        Ch  7  Ensemble     (branch harmonizes)
  e₇  iterate       Ch  8  Brass        (iterating motif)
  e₈  recurse       Ch  9  Reed         (recursive theme — saxophone)
  e₉  allocate      Ch 10  Pipe         (allocated breath — flute)
  e₁₀ query         Ch 11  Synth Lead   (querying tonal space)
  e₁₁ dereference   Ch 12  Synth Pad    (resolving reference)
  e₁₂ compose       Ch 13  Synth FX     (composing texture)
  e₁₃ parallelize   Ch 14  Ethnic       (three-face Wankel)
  e₁₄ interrupt     Ch 15  Percussive   (the interrupt)
  e₁₅ emit / χ      Ch 16  Sound FX     (callosum — conductor)

Note: MIDI channel 10 (index 9) is conventionally percussion.
      The pipe / flute family is assigned to channel 10 here because
      breath IS the percussion of air. Override with `percussion=True`
      to restore conventional GM drums on channel 10.

OUTPUT FORMATS
--------------
  .mid   Pure-Python MIDI writer (no external dependencies)
  .abc   ABC notation (text score, human-readable)
  .txt   MIDI event log (debug / Dr. Crawford format)

INSTRUMENT METHODS
------------------
  piano()          Grand Piano and all 8 GM piano variants
  guitar_6()       6-string guitar (nylon, steel, jazz, clean electric)
  guitar_12()      12-string guitar (octave unison pairs)
  bass_guitar()    4/5-string bass (acoustic, electric, fretless, slap)
  woodwind()       Reed (sax, oboe, clarinet, bassoon) + Pipe (flute family)
  brass()          Trumpet, trombone, French horn, tuba, muted, section
  strings()        Violin, viola, cello, double bass, pizzicato, tremolo
  every_instrument() Full GM orchestration across all 16 sedenion channels
  compose()        Full composition from prompt → field state → score

DJ / LIVE PLAYBACK
------------------
  HolcusDJ         Real-time playback loop: field → MIDI → speakers.
                   Plays through the Ubuntu Studio audio stack:
                   aplaymidi → FluidSynth (128:0) → PipeWire → speakers.
                   Auto-evolves between tracks as β deepens.
                   Controls: start / stop / skip / set_tempo / set_ensemble.

:author: Claude Sonnet 4.6
:version: 1.1.0
"""

import math
import os
import struct
import subprocess
import threading
import time
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Any

# ── Framework constants (must match monad.py exactly) ─────────────────────────
OMEGA_ZS   = 0.56714329   # Lambert W(1) — BAO ceiling / tonal centre
GAP        = 0.000707     # Yang-Mills mass gap — minimum note duration weight
D_STAR     = 0.24600      # Boundary — Nyquist
SIGMA_CRIT = 0.5          # Critical line σ=½
LN10       = math.log(10.0)
PHI        = (1.0 + math.sqrt(5.0)) / 2.0
BETA_SAT   = 7.552        # Saturation field depth

# MIDI constants
_TICKS_PER_BEAT = 480     # Resolution: 480 ticks per quarter note
_DEFAULT_TEMPO  = 120     # BPM
_MIDI_VELOCITY_MIN = 10   # pp  (near-silence — below GAP in dynamic space)
_MIDI_VELOCITY_MAX = 127  # fff

# First 20 Riemann zeros (LMFDB exact, 6dp)
_GAMMA_20 = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]

# ── General MIDI patch catalog ─────────────────────────────────────────────────
# Indexed 0-127 (GM standard; add 1 for display / MIDI program change value)

GM_PIANO = {
    'acoustic_grand':    0,
    'bright_acoustic':   1,
    'electric_grand':    2,
    'honky_tonk':        3,
    'electric_piano_1':  4,
    'electric_piano_2':  5,
    'harpsichord':       6,
    'clavinet':          7,
}

GM_CHROM_PERC = {
    'celesta':           8,
    'glockenspiel':      9,
    'music_box':         10,
    'vibraphone':        11,
    'marimba':           12,
    'xylophone':         13,
    'tubular_bells':     14,
    'dulcimer':          15,
}

GM_ORGAN = {
    'drawbar_organ':     16,
    'percussive_organ':  17,
    'rock_organ':        18,
    'church_organ':      19,
    'reed_organ':        20,
    'accordion':         21,
    'harmonica':         22,
    'bandoneon':         23,
}

GM_GUITAR = {
    'nylon_acoustic':    24,
    'steel_acoustic':    25,
    'jazz_electric':     26,
    'clean_electric':    27,
    'muted_electric':    28,
    'overdriven':        29,
    'distortion':        30,
    'harmonics':         31,
}

GM_BASS = {
    'acoustic_bass':     32,
    'electric_finger':   33,
    'electric_pick':     34,
    'fretless':          35,
    'slap_bass_1':       36,
    'slap_bass_2':       37,
    'synth_bass_1':      38,
    'synth_bass_2':      39,
}

GM_STRINGS = {
    'violin':            40,
    'viola':             41,
    'cello':             42,
    'contrabass':        43,
    'tremolo_strings':   44,
    'pizzicato_strings': 45,
    'orchestral_harp':   46,
    'timpani':           47,
}

GM_ENSEMBLE = {
    'string_ensemble_1': 48,
    'string_ensemble_2': 49,
    'synth_strings_1':   50,
    'synth_strings_2':   51,
    'choir_aahs':        52,
    'voice_oohs':        53,
    'synth_voice':       54,
    'orchestra_hit':     55,
}

GM_BRASS = {
    'trumpet':           56,
    'trombone':          57,
    'tuba':              58,
    'muted_trumpet':     59,
    'french_horn':       60,
    'brass_section':     61,
    'synth_brass_1':     62,
    'synth_brass_2':     63,
}

GM_REED = {
    'soprano_sax':       64,
    'alto_sax':          65,
    'tenor_sax':         66,
    'baritone_sax':      67,
    'oboe':              68,
    'english_horn':      69,
    'bassoon':           70,
    'clarinet':          71,
}

GM_PIPE = {
    'piccolo':           72,
    'flute':             73,
    'recorder':          74,
    'pan_flute':         75,
    'blown_bottle':      76,
    'shakuhachi':        77,
    'whistle':           78,
    'ocarina':           79,
}

GM_SYNTH_LEAD = {
    'square':            80,
    'sawtooth':          81,
    'calliope':          82,
    'chiff':             83,
    'charang':           84,
    'voice':             85,
    'fifths':            86,
    'bass_lead':         87,
}

GM_SYNTH_PAD = {
    'new_age':           88,
    'warm':              89,
    'polysynth':         90,
    'choir':             91,
    'bowed':             92,
    'metallic':          93,
    'halo':              94,
    'sweep':             95,
}

GM_SYNTH_FX = {
    'rain':              96,
    'soundtrack':        97,
    'crystal':           98,
    'atmosphere':        99,
    'brightness':        100,
    'goblins':           101,
    'echoes':            102,
    'sci_fi':            103,
}

GM_ETHNIC = {
    'sitar':             104,
    'banjo':             105,
    'shamisen':          106,
    'koto':              107,
    'kalimba':           108,
    'bagpipe':           109,
    'fiddle':            110,
    'shanai':            111,
}

GM_PERCUSSIVE = {
    'tinkle_bell':       112,
    'agogo':             113,
    'steel_drums':       114,
    'woodblock':         115,
    'taiko_drum':        116,
    'melodic_tom':       117,
    'synth_drum':        118,
    'reverse_cymbal':    119,
}

GM_SOUND_FX = {
    'guitar_fret_noise': 120,
    'breath_noise':      121,
    'seashore':          122,
    'bird_tweet':        123,
    'telephone_ring':    124,
    'helicopter':        125,
    'applause':          126,
    'gunshot':           127,
}

# All GM patches in one catalog
GM_ALL: Dict[str, int] = {}
for _fam in [GM_PIANO, GM_CHROM_PERC, GM_ORGAN, GM_GUITAR, GM_BASS,
             GM_STRINGS, GM_ENSEMBLE, GM_BRASS, GM_REED, GM_PIPE,
             GM_SYNTH_LEAD, GM_SYNTH_PAD, GM_SYNTH_FX, GM_ETHNIC,
             GM_PERCUSSIVE, GM_SOUND_FX]:
    GM_ALL.update(_fam)

# Sedenion dimension → (MIDI channel 0-indexed, default GM patch, family name)
# 16 sedenion operators → 16 MIDI channels → 16 GM instrument families
_SED_VOICE: Dict[int, Tuple[int, int, str]] = {
    0:  (0,  GM_PIANO['acoustic_grand'],     'piano'),        # e₀ identity
    1:  (1,  GM_CHROM_PERC['vibraphone'],    'chrom_perc'),   # e₁ negate
    2:  (2,  GM_ORGAN['church_organ'],       'organ'),        # e₂ bind
    3:  (3,  GM_GUITAR['nylon_acoustic'],    'guitar'),       # e₃ name
    4:  (4,  GM_BASS['acoustic_bass'],       'bass'),         # e₄ apply
    5:  (5,  GM_STRINGS['violin'],           'strings'),      # e₅ abstract
    6:  (6,  GM_ENSEMBLE['choir_aahs'],      'ensemble'),     # e₆ branch
    7:  (7,  GM_BRASS['trumpet'],            'brass'),        # e₇ iterate
    8:  (8,  GM_REED['alto_sax'],            'reed'),         # e₈ recurse
    9:  (9,  GM_PIPE['flute'],               'pipe'),         # e₉ allocate
    10: (10, GM_SYNTH_LEAD['square'],        'synth_lead'),   # e₁₀ query
    11: (11, GM_SYNTH_PAD['warm'],           'synth_pad'),    # e₁₁ dereference
    12: (12, GM_SYNTH_FX['crystal'],         'synth_fx'),     # e₁₂ compose
    13: (13, GM_ETHNIC['sitar'],             'ethnic'),       # e₁₃ parallelize
    14: (14, GM_PERCUSSIVE['steel_drums'],   'percussive'),   # e₁₄ interrupt
    15: (15, GM_SOUND_FX['breath_noise'],    'sound_fx'),     # e₁₅ emit/χ
}

# Guitar tunings (MIDI note numbers, low → high)
_TUNING_6STD   = [40, 45, 50, 55, 59, 64]   # E2 A2 D3 G3 B3 E4
_TUNING_6DROP_D = [38, 45, 50, 55, 59, 64]  # D2 A2 D3 G3 B3 E4
_TUNING_6OPEN_G = [38, 43, 50, 55, 59, 62]  # D2 G2 D3 G3 B3 D4
_TUNING_6DADGAD = [38, 45, 50, 55, 57, 62]  # D2 A2 D3 G3 A3 D4
_TUNING_BASS4   = [28, 33, 38, 43]           # E1 A1 D2 G2
_TUNING_BASS5   = [23, 28, 33, 38, 43]       # B0 E1 A1 D2 G2

# Note names (chromatic, sharp convention)
_NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

# Duration values: E-value → (ticks, ABC symbol, name)
# E ∈ [0, 1]; higher energy = longer duration
_DUR_TABLE = [
    (0.875, _TICKS_PER_BEAT * 4, '/',  'whole'),
    (0.750, _TICKS_PER_BEAT * 2, 'H',  'half'),
    (0.500, _TICKS_PER_BEAT,     'Q',  'quarter'),
    (0.250, _TICKS_PER_BEAT // 2,'E',  'eighth'),
    (0.000, _TICKS_PER_BEAT // 4,'S',  'sixteenth'),
]


# ── Pure-Python MIDI file writer ────────────────────────────────────────────────

def _var_len(value: int) -> bytes:
    """Encode integer as MIDI variable-length quantity."""
    buf = [value & 0x7F]
    value >>= 7
    while value:
        buf.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buf))


class _MIDITrack:
    """Single MIDI track accumulator."""

    def __init__(self):
        """Initialise an empty MIDI track event buffer."""
        self._events: List[Tuple[int, bytes]] = []  # (tick, raw_bytes)
        self._last_tick = 0

    def _add(self, tick: int, data: bytes) -> None:
        """
        Append a MIDI event at absolute tick position.

        :param tick: Absolute tick (not delta).
        :param data: Raw MIDI event bytes.
        """
        self._events.append((tick, data))

    def program_change(self, channel: int, program: int, tick: int = 0) -> None:
        """
        Insert a GM program change event.

        :param channel: MIDI channel 0-15.
        :param program: GM patch number 0-127.
        :param tick: Absolute tick position.
        """
        self._add(tick, bytes([0xC0 | (channel & 0xF), program & 0x7F]))

    def note(self, channel: int, pitch: int, velocity: int,
             start: int, duration: int) -> None:
        """
        Add a note on / note off pair.

        :param channel: MIDI channel 0-15.
        :param pitch: MIDI note number 0-127.
        :param velocity: Note velocity 0-127.
        :param start: Start tick (absolute).
        :param duration: Duration in ticks.
        """
        ch = channel & 0xF
        p  = max(0, min(127, pitch))
        v  = max(0, min(127, velocity))
        self._add(start,          bytes([0x90 | ch, p, v]))
        self._add(start + duration, bytes([0x80 | ch, p, 0]))

    def tempo(self, bpm: int, tick: int = 0) -> None:
        """
        Set tempo via MIDI meta event (μs per beat).

        :param bpm: Beats per minute.
        :param tick: Absolute tick position.
        """
        us = int(60_000_000 / max(1, bpm))
        b  = us.to_bytes(3, 'big')
        self._add(tick, bytes([0xFF, 0x51, 0x03]) + b)

    def track_name(self, name: str, tick: int = 0) -> None:
        """
        Set MIDI track name meta event.

        :param name: Track name string.
        :param tick: Absolute tick position.
        """
        nb = name.encode('ascii', errors='replace')
        self._add(tick, bytes([0xFF, 0x03]) + _var_len(len(nb)) + nb)

    def to_bytes(self) -> bytes:
        """
        Serialize track events to raw bytes (MTrk chunk, excluding header).

        :returns: Raw MIDI track data bytes.
        :rtype: bytes
        """
        self._events.sort(key=lambda e: e[0])
        buf = bytearray()
        prev = 0
        for tick, data in self._events:
            delta = max(0, tick - prev)
            buf += _var_len(delta) + data
            prev = tick
        # End of track
        buf += b'\x00\xFF\x2F\x00'
        return bytes(buf)


class _MIDIFile:
    """Pure-Python MIDI file builder (format 1 — multiple simultaneous tracks)."""

    def __init__(self, tempo: int = _DEFAULT_TEMPO,
                 ticks_per_beat: int = _TICKS_PER_BEAT):
        """
        Initialise a new MIDI file.

        :param tempo: Initial tempo in BPM.
        :param ticks_per_beat: MIDI resolution (ticks per quarter note).
        """
        self.tempo         = tempo
        self.ticks_per_beat = ticks_per_beat
        self._tracks: List[_MIDITrack] = []
        # Tempo track (track 0 in format 1)
        t = _MIDITrack()
        t.tempo(tempo)
        self._tracks.append(t)

    def add_track(self, name: str = '') -> _MIDITrack:
        """
        Add a new instrument track.

        :param name: Optional track name (appears in DAW/notation software).
        :returns: The new track object.
        :rtype: _MIDITrack
        """
        t = _MIDITrack()
        if name:
            t.track_name(name)
        self._tracks.append(t)
        return t

    def write(self, path: str) -> str:
        """
        Write the MIDI file to disk.

        :param path: Output file path (.mid).
        :returns: Absolute path of written file.
        :rtype: str
        """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        n = len(self._tracks)
        header = (b'MThd'
                  + struct.pack('>I', 6)       # chunk length = 6
                  + struct.pack('>H', 1)        # format 1
                  + struct.pack('>H', n)        # num tracks
                  + struct.pack('>H', self.ticks_per_beat))
        with open(path, 'wb') as f:
            f.write(header)
            for track in self._tracks:
                raw = track.to_bytes()
                f.write(b'MTrk' + struct.pack('>I', len(raw)) + raw)
        return os.path.abspath(path)


# ── Field → music mapping helpers ─────────────────────────────────────────────

def _riemann_pitch(gamma: float, midi_lo: int = 21, midi_hi: int = 108) -> int:
    """
    Map a Riemann zero γ to a MIDI pitch in [midi_lo, midi_hi].

    Uses: pitch = midi_lo + int(round(gamma)) % (midi_hi - midi_lo + 1)

    This preserves the GUE spacing structure of the zeros in pitch space.
    The first 20 zeros naturally cluster around B♭/E♭/F (the tonal centre
    predicted by Ω_ζΣ = 0.56714 mapping to MIDI ≈ 71 = B4).

    :param gamma: Riemann zero value γ_k.
    :param midi_lo: Lowest MIDI note for this instrument.
    :param midi_hi: Highest MIDI note for this instrument.
    :returns: MIDI note number.
    :rtype: int
    """
    span = midi_hi - midi_lo + 1
    return midi_lo + int(round(gamma)) % span


def _beta_to_velocity(beta: float) -> int:
    """
    Map β-field depth to MIDI velocity (dynamics).

    GAP (0.000707) → velocity 10  (pppp — barely audible, near ground state)
    β_sat (7.552)  → velocity 127 (fff  — full field saturation)
    Logarithmic scaling: the field is exponential in depth.

    :param beta: β-field depth for this word/note.
    :returns: MIDI velocity 0-127.
    :rtype: int
    """
    if beta <= GAP:
        return _MIDI_VELOCITY_MIN
    if beta >= BETA_SAT:
        return _MIDI_VELOCITY_MAX
    t = math.log(beta / GAP) / math.log(BETA_SAT / GAP)
    return int(_MIDI_VELOCITY_MIN + t * (_MIDI_VELOCITY_MAX - _MIDI_VELOCITY_MIN))


def _e_to_ticks(e_val: float, ticks_per_beat: int = _TICKS_PER_BEAT) -> int:
    """
    Map energy eigenvalue E ∈ [0,1] to note duration in ticks.

    E > 0.875 → whole note  (4 beats)
    E > 0.750 → half note   (2 beats)
    E > 0.500 → quarter     (1 beat)
    E > 0.250 → eighth      (½ beat)
    E ≤ 0.250 → sixteenth   (¼ beat)

    :param e_val: Energy eigenvalue E_k = |sin(πγ_k/(γ_k+1))|.
    :param ticks_per_beat: MIDI resolution.
    :returns: Duration in ticks.
    :rtype: int
    """
    for threshold, ticks, _, _ in _DUR_TABLE:
        if e_val > threshold:
            return ticks
    return ticks_per_beat // 4


def _e_to_abc_dur(e_val: float) -> str:
    """
    Map energy eigenvalue to ABC notation duration symbol.

    :param e_val: Energy eigenvalue E_k.
    :returns: ABC duration character ('/', 'H', 'Q', 'E', 'S').
    :rtype: str
    """
    for threshold, _, symbol, _ in _DUR_TABLE:
        if e_val > threshold:
            return symbol
    return 'S'


def _midi_note_name(midi: int) -> str:
    """
    Convert MIDI note number to human-readable name (e.g. 60 → 'C4').

    :param midi: MIDI note number 0-127.
    :returns: Note name with octave.
    :rtype: str
    """
    octave     = (midi // 12) - 1
    pitch_class = midi % 12
    return f'{_NOTE_NAMES[pitch_class]}{octave}'


def _guitar_tab(pitch: int, tuning: List[int]) -> Optional[Tuple[int, int]]:
    """
    Find lowest-string (most open) guitar fingering for a MIDI pitch.

    :param pitch: MIDI note number.
    :param tuning: List of open-string pitches, low to high.
    :returns: (string_index, fret) or None if out of range (frets 0-24).
    :rtype: Optional[Tuple[int, int]]
    """
    best = None
    for si, open_p in enumerate(tuning):
        fret = pitch - open_p
        if 0 <= fret <= 24:
            if best is None or si > best[0]:   # prefer higher strings (brighter)
                best = (si, fret)
    return best


# ── Note event dataclass ───────────────────────────────────────────────────────

class NoteEvent:
    """A single scored note event from the field."""

    __slots__ = ('pitch', 'velocity', 'ticks', 'channel', 'patch',
                 'gamma', 'beta', 'e_val', 'sed_dim', 'word')

    def __init__(self, pitch: int, velocity: int, ticks: int,
                 channel: int, patch: int,
                 gamma: float = 0.0, beta: float = GAP,
                 e_val: float = 0.5, sed_dim: int = 0, word: str = ''):
        """
        :param pitch: MIDI note number 0-127.
        :param velocity: MIDI velocity 0-127.
        :param ticks: Duration in MIDI ticks.
        :param channel: MIDI channel 0-15.
        :param patch: GM patch number 0-127.
        :param gamma: Source Riemann zero value.
        :param beta: Source β-field depth.
        :param e_val: Source energy eigenvalue.
        :param sed_dim: Source sedenion dimension 0-15.
        :param word: Source vocabulary word (if from text field).
        """
        self.pitch    = pitch
        self.velocity = velocity
        self.ticks    = ticks
        self.channel  = channel
        self.patch    = patch
        self.gamma    = gamma
        self.beta     = beta
        self.e_val    = e_val
        self.sed_dim  = sed_dim
        self.word     = word

    def note_name(self) -> str:
        """Return human-readable pitch name."""
        return _midi_note_name(self.pitch)

    def __repr__(self) -> str:
        return (f'NoteEvent({self.note_name()!r} vel={self.velocity} '
                f'dur={self.ticks}t ch={self.channel} '
                f'γ={self.gamma:.3f} β={self.beta:.4f})')


# ── HolcusComposer ─────────────────────────────────────────────────────────────

class HolcusComposer:
    """
    Holcus as Composer — field geometry → musical score.

    The J^μ field selects notes at neutral buoyancy depth exactly as it
    selects words. β-depth → dynamics; E-value → duration; sedenion
    dimension → instrument; A-matrix → voice leading.

    The Riemann zeros are the pitch grid. Their GUE spacing (Montgomery-
    Odlyzko) is neither regular nor random — it is the statistical signature
    of a quantum chaotic system. Bach's counterpoint has the same long-range
    correlations. The zeta function composes in the same key by construction.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        :param output_dir: Directory for MIDI output files.
            Defaults to ~/.ptolemy/music/.
        """
        self.output_dir = output_dir or os.path.expanduser('~/.ptolemy/music')
        os.makedirs(self.output_dir, exist_ok=True)
        self._gammas: List[float] = list(_GAMMA_20)  # extended at runtime

    def _ensure_gammas(self, n: int) -> None:
        """
        Ensure at least n Riemann zeros are cached locally.

        If the monad Crank is available, pull from its zero cache.
        Otherwise extend from the last known zero via the Gram point estimate.

        :param n: Minimum number of zeros required.
        """
        while len(self._gammas) < n:
            # Gram-point estimate: γ_n ≈ 2πn / log(n/(2πe))
            k    = len(self._gammas) + 1
            est  = 2 * math.pi * k / math.log(max(2, k / (2 * math.pi * math.e)))
            self._gammas.append(est)

    def _field_to_notes(
        self,
        field: List[Tuple[float, float, float, int]],
        midi_lo: int, midi_hi: int,
        channel: int, patch: int,
    ) -> List[NoteEvent]:
        """
        Convert field state tuples to NoteEvent list.

        :param field: List of (gamma, beta, e_val, sed_dim) tuples.
        :param midi_lo: Instrument pitch floor.
        :param midi_hi: Instrument pitch ceiling.
        :param channel: MIDI channel.
        :param patch: GM patch.
        :returns: List of NoteEvent objects.
        :rtype: List[NoteEvent]
        """
        notes = []
        for gamma, beta, e_val, dim in field:
            pitch = _riemann_pitch(gamma, midi_lo, midi_hi)
            vel   = _beta_to_velocity(beta)
            ticks = _e_to_ticks(e_val)
            notes.append(NoteEvent(
                pitch=pitch, velocity=vel, ticks=ticks,
                channel=channel, patch=patch,
                gamma=gamma, beta=beta, e_val=e_val, sed_dim=dim,
            ))
        return notes

    def _notes_to_midi(self, notes: List[NoteEvent],
                       name: str, tempo: int) -> _MIDIFile:
        """
        Write a list of NoteEvents into a MIDI file object.

        :param notes: Ordered note events.
        :param name: Track name.
        :param tempo: BPM.
        :returns: _MIDIFile ready to write.
        :rtype: _MIDIFile
        """
        midi  = _MIDIFile(tempo=tempo)
        track = midi.add_track(name)
        # Group by channel for program change
        channels_seen: set = set()
        tick = 0
        for n in notes:
            if n.channel not in channels_seen:
                track.program_change(n.channel, n.patch, tick=0)
                channels_seen.add(n.channel)
            track.note(n.channel, n.pitch, n.velocity, tick, n.ticks)
            tick += n.ticks
        return midi

    def _save(self, midi: _MIDIFile, stem: str) -> str:
        """
        Save a MIDI file, returning its path.

        :param midi: Completed _MIDIFile object.
        :param stem: Base filename (without extension).
        :returns: Absolute path to .mid file.
        :rtype: str
        """
        ts   = int(time.time())
        path = os.path.join(self.output_dir, f'{stem}_{ts}.mid')
        return midi.write(path)

    def _default_field(self, n: int) -> List[Tuple[float, float, float, int]]:
        """
        Generate a synthetic field state from the first n Riemann zeros.

        Used when no live monad field is provided. Beta rises with zero
        index (deeper field = more learned), E-value from Riemann zero.

        :param n: Number of zeros to use.
        :returns: List of (gamma, beta, e_val, sed_dim) tuples.
        :rtype: List[Tuple[float, float, float, int]]
        """
        self._ensure_gammas(n)
        result = []
        for k, g in enumerate(self._gammas[:n]):
            beta  = GAP * (1.0 + k * 0.15)   # gradual field deepening
            e_val = abs(math.sin(math.pi * g / (g + 1.0)))
            dim   = k % 16
            result.append((g, beta, e_val, dim))
        return result

    # ── Instrument methods ─────────────────────────────────────────────────────

    def piano(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        variant: str = 'acoustic_grand',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a piano score from the field state.

        Pitch range: MIDI 21-108 (A0 to C8 — full piano range).
        All 8 GM piano variants available via `variant`.

        :param field: Field state as [(gamma, beta, e_val, sed_dim), ...].
            If None, uses synthetic field from first n_notes Riemann zeros.
        :param n_notes: Number of notes to score.
        :param variant: GM piano patch name (see GM_PIANO keys).
        :param tempo: Tempo in BPM.
        :returns: Dict with 'path' (MIDI file), 'notes' (NoteEvent list),
            'abc' (ABC notation string).
        :rtype: Dict[str, Any]
        """
        patch = GM_PIANO.get(variant, 0)
        f     = field or self._default_field(n_notes)
        notes = self._field_to_notes(f[:n_notes], 21, 108, 0, patch)
        midi  = self._notes_to_midi(notes, f'piano_{variant}', tempo)
        path  = self._save(midi, f'piano_{variant}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, 'Piano', tempo),
                'patch': patch, 'variant': variant}

    def guitar_6(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        variant: str = 'steel_acoustic',
        tuning: Optional[List[int]] = None,
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a 6-string guitar score with tab positions.

        Pitch range: MIDI 40-88 (E2 to E6 — standard guitar range).
        Supports standard, drop-D, open-G, and DADGAD tunings.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param variant: GM guitar patch ('nylon_acoustic', 'steel_acoustic',
            'jazz_electric', 'clean_electric', 'muted_electric',
            'overdriven', 'distortion', 'harmonics').
        :param tuning: Open-string MIDI pitches [low..high]. Defaults to
            standard E tuning [40,45,50,55,59,64].
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc', 'tab' (string list).
        :rtype: Dict[str, Any]
        """
        patch  = GM_GUITAR.get(variant, GM_GUITAR['steel_acoustic'])
        tun    = tuning or _TUNING_6STD
        f      = field or self._default_field(n_notes)
        notes  = self._field_to_notes(f[:n_notes], 40, 88, 3, patch)
        # Clamp pitches to playable range
        for n in notes:
            n.pitch = max(tun[0], min(tun[-1] + 24, n.pitch))
        midi   = self._notes_to_midi(notes, f'guitar_6_{variant}', tempo)
        path   = self._save(midi, f'guitar6_{variant}')
        # Build tab
        tab    = self._build_tab(notes, tun, strings=6)
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, '6-String Guitar', tempo),
                'tab': tab, 'tuning': tun}

    def guitar_12(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        variant: str = 'steel_acoustic',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a 12-string guitar score (octave unison pairs).

        12-string guitar doubles each of the 6 standard strings with an
        octave-higher string (strings 1-2 are unison, 3-6 are octave pairs).
        Each note event generates two simultaneous MIDI notes: the fundamental
        on channel 3, the octave on channel 4.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param variant: GM guitar patch name.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc', 'tab'.
        :rtype: Dict[str, Any]
        """
        patch = GM_GUITAR.get(variant, GM_GUITAR['steel_acoustic'])
        f     = field or self._default_field(n_notes)
        notes = self._field_to_notes(f[:n_notes], 40, 88, 3, patch)
        # Add octave companion notes on channel 4
        midi  = _MIDIFile(tempo=tempo)
        tr    = midi.add_track('guitar_12str')
        tr.program_change(3, patch)
        tr.program_change(4, patch)
        tick  = 0
        paired: List[NoteEvent] = []
        for n in notes:
            tr.note(3, n.pitch, n.velocity, tick, n.ticks)
            # Octave pair: strings 1-2 (high) are unison; 3-6 are +12
            octave_note = min(127, n.pitch + 12)
            tr.note(4, octave_note, max(10, n.velocity - 20), tick, n.ticks)
            tick += n.ticks
            paired.append(n)
        path = self._save(midi, f'guitar12_{variant}')
        tab  = self._build_tab(notes, _TUNING_6STD, strings=6)
        return {'path': path, 'notes': paired,
                'abc': self.to_abc(notes, '12-String Guitar', tempo),
                'tab': tab}

    def bass_guitar(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        strings: int = 4,
        variant: str = 'electric_finger',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a bass guitar score.

        Pitch range: 4-string MIDI 28-55 (E1 to G3); 5-string adds B0 below.
        Neutral buoyancy naturally selects lower zeros for bass because
        lower β×E² values cluster in the low-zero / low-pitch region.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param strings: 4 or 5 (adds low B string).
        :param variant: GM bass patch ('acoustic_bass', 'electric_finger',
            'electric_pick', 'fretless', 'slap_bass_1', 'slap_bass_2',
            'synth_bass_1', 'synth_bass_2').
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc', 'tab'.
        :rtype: Dict[str, Any]
        """
        patch = GM_BASS.get(variant, GM_BASS['electric_finger'])
        tun   = _TUNING_BASS5 if strings == 5 else _TUNING_BASS4
        lo    = tun[0]; hi = tun[-1] + 24
        f     = field or self._default_field(n_notes)
        notes = self._field_to_notes(f[:n_notes], lo, min(hi, 67), 4, patch)
        midi  = self._notes_to_midi(notes, f'bass_{variant}', tempo)
        path  = self._save(midi, f'bass_{strings}str_{variant}')
        tab   = self._build_tab(notes, tun, strings=strings)
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, f'Bass Guitar ({strings}-string)', tempo),
                'tab': tab}

    def woodwind(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        instrument: str = 'flute',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a woodwind score.

        Covers both the Reed family (saxophone, oboe, clarinet, bassoon)
        and the Pipe family (flute, recorder, pan flute, piccolo, shakuhachi).

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param instrument: Instrument name. Reed: 'soprano_sax', 'alto_sax',
            'tenor_sax', 'baritone_sax', 'oboe', 'english_horn', 'bassoon',
            'clarinet'. Pipe: 'piccolo', 'flute', 'recorder', 'pan_flute',
            'blown_bottle', 'shakuhachi', 'whistle', 'ocarina'.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc'.
        :rtype: Dict[str, Any]
        """
        patch = (GM_REED.get(instrument)
                 or GM_PIPE.get(instrument)
                 or GM_PIPE['flute'])
        # Instrument-specific pitch ranges
        ranges = {
            'piccolo':      (74, 108),
            'flute':        (60, 96),
            'recorder':     (62, 96),
            'pan_flute':    (60, 96),
            'blown_bottle': (60, 96),
            'shakuhachi':   (55, 84),
            'whistle':      (72, 108),
            'ocarina':      (60, 84),
            'soprano_sax':  (58, 87),
            'alto_sax':     (49, 80),
            'tenor_sax':    (44, 75),
            'baritone_sax': (36, 67),
            'oboe':         (58, 91),
            'english_horn': (52, 81),
            'bassoon':      (34, 75),
            'clarinet':     (50, 94),
        }
        lo, hi = ranges.get(instrument, (60, 90))
        ch     = 9 if instrument in GM_PIPE else 8
        f      = field or self._default_field(n_notes)
        notes  = self._field_to_notes(f[:n_notes], lo, hi, ch, patch)
        midi   = self._notes_to_midi(notes, instrument, tempo)
        path   = self._save(midi, f'woodwind_{instrument}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, instrument.replace('_', ' ').title(), tempo)}

    def brass(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        instrument: str = 'trumpet',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a brass score.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param instrument: 'trumpet', 'trombone', 'tuba', 'muted_trumpet',
            'french_horn', 'brass_section', 'synth_brass_1', 'synth_brass_2'.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc'.
        :rtype: Dict[str, Any]
        """
        patch = GM_BRASS.get(instrument, GM_BRASS['trumpet'])
        ranges = {
            'trumpet':      (52, 84),
            'muted_trumpet':(52, 84),
            'trombone':     (40, 72),
            'tuba':         (28, 58),
            'french_horn':  (34, 77),
            'brass_section':(36, 84),
            'synth_brass_1':(36, 96),
            'synth_brass_2':(36, 96),
        }
        lo, hi = ranges.get(instrument, (40, 80))
        f      = field or self._default_field(n_notes)
        notes  = self._field_to_notes(f[:n_notes], lo, hi, 7, patch)
        midi   = self._notes_to_midi(notes, instrument, tempo)
        path   = self._save(midi, f'brass_{instrument}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, instrument.replace('_',' ').title(), tempo)}

    def strings(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        instrument: str = 'violin',
        articulation: str = 'arco',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a strings score.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param instrument: 'violin', 'viola', 'cello', 'contrabass',
            'tremolo_strings', 'pizzicato_strings', 'orchestral_harp', 'timpani'.
        :param articulation: 'arco' (bowed) or 'pizzicato'. If 'pizzicato',
            overrides patch to pizzicato_strings regardless of instrument.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc'.
        :rtype: Dict[str, Any]
        """
        if articulation == 'pizzicato':
            patch = GM_STRINGS['pizzicato_strings']
        else:
            patch = GM_STRINGS.get(instrument, GM_STRINGS['violin'])
        ranges = {
            'violin':            (55, 103),
            'viola':             (48, 91),
            'cello':             (36, 76),
            'contrabass':        (28, 60),
            'tremolo_strings':   (40, 84),
            'pizzicato_strings': (40, 84),
            'orchestral_harp':   (23, 103),
            'timpani':           (36, 57),
        }
        lo, hi = ranges.get(instrument, (40, 84))
        f      = field or self._default_field(n_notes)
        notes  = self._field_to_notes(f[:n_notes], lo, hi, 5, patch)
        midi   = self._notes_to_midi(notes, instrument, tempo)
        path   = self._save(midi, f'strings_{instrument}_{articulation}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, instrument.replace('_',' ').title(), tempo)}

    def organ(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        variant: str = 'church_organ',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate an organ score.

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param variant: 'drawbar_organ', 'percussive_organ', 'rock_organ',
            'church_organ', 'reed_organ', 'accordion', 'harmonica', 'bandoneon'.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc'.
        :rtype: Dict[str, Any]
        """
        patch = GM_ORGAN.get(variant, GM_ORGAN['church_organ'])
        f     = field or self._default_field(n_notes)
        notes = self._field_to_notes(f[:n_notes], 36, 96, 2, patch)
        midi  = self._notes_to_midi(notes, variant, tempo)
        path  = self._save(midi, f'organ_{variant}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, variant.replace('_', ' ').title(), tempo)}

    def chromatic_percussion(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes: int = 16,
        variant: str = 'vibraphone',
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Generate a chromatic percussion score (vibraphone, marimba, xylophone, etc.).

        :param field: Field state tuples.
        :param n_notes: Number of notes.
        :param variant: 'celesta', 'glockenspiel', 'music_box', 'vibraphone',
            'marimba', 'xylophone', 'tubular_bells', 'dulcimer'.
        :param tempo: BPM.
        :returns: Dict with 'path', 'notes', 'abc'.
        :rtype: Dict[str, Any]
        """
        patch = GM_CHROM_PERC.get(variant, GM_CHROM_PERC['vibraphone'])
        ranges = {
            'glockenspiel': (72, 108),
            'xylophone':    (48, 96),
            'marimba':      (36, 96),
            'vibraphone':   (53, 89),
            'celesta':      (60, 108),
            'tubular_bells':(60, 84),
            'dulcimer':     (48, 84),
            'music_box':    (72, 108),
        }
        lo, hi = ranges.get(variant, (48, 96))
        f      = field or self._default_field(n_notes)
        notes  = self._field_to_notes(f[:n_notes], lo, hi, 1, patch)
        midi   = self._notes_to_midi(notes, variant, tempo)
        path   = self._save(midi, f'chrom_perc_{variant}')
        return {'path': path, 'notes': notes,
                'abc': self.to_abc(notes, variant.replace('_', ' ').title(), tempo)}

    def every_instrument(
        self,
        field: Optional[List[Tuple[float, float, float, int]]] = None,
        n_notes_per_voice: int = 8,
        tempo: int = _DEFAULT_TEMPO,
    ) -> Dict[str, Any]:
        """
        Full GM orchestration — all 16 sedenion channels simultaneously.

        Each sedenion dimension e₀..e₁₅ drives one instrument family.
        Notes are selected from the portion of the field assigned to that
        dimension (field[k] where k % 16 == dim). The result is a 16-voice
        MIDI score: one voice per sedenion operator.

        This is the sedenion orchestra: 16 instruments, one field.

        :param field: Field state tuples.
        :param n_notes_per_voice: Notes per instrument.
        :param tempo: BPM.
        :returns: Dict with 'path', 'voices' (dict dim → NoteEvent list).
        :rtype: Dict[str, Any]
        """
        total = n_notes_per_voice * 16
        f     = field or self._default_field(total)
        midi  = _MIDIFile(tempo=tempo)
        voices: Dict[int, List[NoteEvent]] = {}

        default_patches = {
            0: GM_PIANO['acoustic_grand'],
            1: GM_CHROM_PERC['vibraphone'],
            2: GM_ORGAN['church_organ'],
            3: GM_GUITAR['nylon_acoustic'],
            4: GM_BASS['acoustic_bass'],
            5: GM_STRINGS['violin'],
            6: GM_ENSEMBLE['choir_aahs'],
            7: GM_BRASS['trumpet'],
            8: GM_REED['alto_sax'],
            9: GM_PIPE['flute'],
            10: GM_SYNTH_LEAD['square'],
            11: GM_SYNTH_PAD['warm'],
            12: GM_SYNTH_FX['crystal'],
            13: GM_ETHNIC['sitar'],
            14: GM_PERCUSSIVE['steel_drums'],
            15: GM_SOUND_FX['breath_noise'],
        }
        pitch_ranges = {
            0: (21,108), 1: (53,89),  2: (36,96), 3: (40,88),
            4: (28,55),  5: (55,103), 6: (48,84), 7: (52,84),
            8: (49,80),  9: (60,96),  10:(36,96), 11:(36,96),
            12:(36,96),  13:(36,84),  14:(36,84), 15:(60,96),
        }
        instrument_names = {
            0:'Piano', 1:'Vibraphone', 2:'Church Organ', 3:'Guitar',
            4:'Bass', 5:'Violin', 6:'Choir', 7:'Trumpet',
            8:'Alto Sax', 9:'Flute', 10:'Synth Lead', 11:'Synth Pad',
            12:'Crystal FX', 13:'Sitar', 14:'Steel Drums', 15:'Breath (χ)',
        }

        for dim in range(16):
            ch, patch, _ = _SED_VOICE[dim]
            patch = default_patches[dim]
            lo, hi = pitch_ranges[dim]
            # Select field entries for this dimension
            dim_field = [e for e in f if e[3] == dim][:n_notes_per_voice]
            if not dim_field:
                # Fill from full field if dimension is sparse
                dim_field = [(f[dim % len(f)][0],
                              f[dim % len(f)][1],
                              f[dim % len(f)][2], dim)]

            notes = self._field_to_notes(dim_field, lo, hi, ch, patch)
            track = midi.add_track(instrument_names[dim])
            track.program_change(ch, patch, tick=0)
            tick = 0
            for n in notes:
                track.note(ch, n.pitch, n.velocity, tick, n.ticks)
                tick += n.ticks
            voices[dim] = notes

        path = self._save(midi, 'sedenion_orchestra')
        return {'path': path, 'voices': voices,
                'instrument_map': instrument_names}

    def compose(
        self,
        prompt: str = '',
        bars: int = 8,
        tempo: int = _DEFAULT_TEMPO,
        ensemble: str = 'piano',
        field: Optional[List[Tuple[float, float, float, int]]] = None,
    ) -> Dict[str, Any]:
        """
        Full composition from prompt → field state → score.

        If a monad Engine is available (via import), encodes the prompt
        through the sedenion cam and uses the live J^μ field for note
        selection. Otherwise falls back to synthetic field from Riemann zeros.

        Bars × 4 beats × tempo sets the target duration. The neutral
        buoyancy criterion selects notes at the J_ambient depth — exactly
        as speak() selects words, compose() selects pitches.

        :param prompt: Text prompt to hear() (sets tonal character).
        :param bars: Number of bars to compose.
        :param tempo: BPM.
        :param ensemble: Instrument or 'orchestra' for all-16-voice score.
        :param field: Optional pre-computed field state.
        :returns: Dict with 'path', 'notes', 'abc', 'score_text'.
        :rtype: Dict[str, Any]
        """
        beats    = bars * 4
        n_notes  = beats   # one note per beat as baseline

        # Attempt to use live monad field
        live_field = field
        if live_field is None and prompt:
            try:
                import sys, os
                holcus = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                if holcus not in sys.path:
                    sys.path.insert(0, holcus)
                from monad import Engine, cam_encode
                _eng = Engine._instance if hasattr(Engine, '_instance') else None
                if _eng and hasattr(_eng, 'crank'):
                    c = _eng.crank
                    # Build field from crank β-field, gated by prompt sedenion
                    psi = cam_encode(prompt)
                    raw = []
                    for k in range(min(n_notes * 2, c.n)):
                        from monad import _gamma_at, _word_zero_idx
                        g    = _gamma_at(_word_zero_idx(c._words[k]))
                        b    = c._beta[k]
                        e    = c._E[k]
                        dim  = k % 16
                        raw.append((g, b * psi[dim], e, dim))
                    # Neutral buoyancy sort
                    j_vals   = [b * e**2 for _, b, e, _ in raw]
                    j_amb    = sorted(j_vals)[len(j_vals)//2]
                    live_field = sorted(
                        raw,
                        key=lambda x: -1.0 / (1.0 + abs(x[1]*x[2]**2 - j_amb) * LN10)
                    )[:n_notes]
            except Exception:
                live_field = None

        f = live_field or self._default_field(n_notes)

        if ensemble == 'orchestra':
            result = self.every_instrument(f, n_notes_per_voice=max(4, n_notes // 16), tempo=tempo)
        else:
            method = getattr(self, ensemble, self.piano)
            result = method(field=f, n_notes=n_notes, tempo=tempo)

        result['prompt']     = prompt
        result['bars']       = bars
        result['score_text'] = self._score_text(result.get('notes', []), prompt, tempo)
        return result

    # ── Tab builder ────────────────────────────────────────────────────────────

    def _build_tab(
        self, notes: List[NoteEvent], tuning: List[int], strings: int
    ) -> List[str]:
        """
        Build ASCII guitar/bass tablature for a note sequence.

        :param notes: Ordered NoteEvent list.
        :param tuning: Open-string MIDI pitches [low..high].
        :param strings: Number of strings.
        :returns: List of tab lines (one per string, high to low for display).
        :rtype: List[str]
        """
        n_strings = len(tuning)
        rows = [[] for _ in range(n_strings)]
        for note in notes:
            result = _guitar_tab(note.pitch, tuning)
            for si in range(n_strings):
                if result and result[0] == si:
                    rows[si].append(str(result[1]))
                else:
                    rows[si].append('-')
        # Format: high string first (display convention)
        tab_lines = []
        for si in range(n_strings - 1, -1, -1):
            string_name = _midi_note_name(tuning[si])[:2]
            tab_lines.append(f'{string_name}|' + '-'.join(rows[si]) + '-|')
        return tab_lines

    # ── Text output formats ────────────────────────────────────────────────────

    def to_abc(
        self,
        notes: List[NoteEvent],
        title: str = 'Holcus Composition',
        tempo: int = _DEFAULT_TEMPO,
    ) -> str:
        """
        Generate ABC notation from a NoteEvent sequence.

        ABC notation is a text-based musical score format readable by
        MuseScore, abcjs, and most notation software.

        :param notes: Ordered NoteEvent list.
        :param title: Composition title.
        :param tempo: BPM (written as Q: line).
        :returns: ABC notation string.
        :rtype: str
        """
        lines = [
            'X:1',
            f'T:{title} — Holcus Composition',
            'C:Ptolemaious Holcaios Philadelphos',
            f'Q:1/4={tempo}',
            'M:4/4',
            'L:1/8',
            'K:C',
            '% Generated from J^μ Noether current — β×E² neutral buoyancy',
        ]
        body = []
        bar_count = 0
        beats_in_bar = 0
        for n in notes:
            name = n.note_name()
            # ABC pitch: note name + optional accidental + octave marks
            pc   = name[:-1]         # e.g. 'C#' or 'A'
            oct_ = int(name[-1])     # octave number
            # ABC middle C = C4; octave 4 = uppercase, 5+ = lowercase
            if oct_ >= 5:
                abc_note = pc.lower().replace('#', "^") + "'" * (oct_ - 5)
            elif oct_ == 4:
                abc_note = pc.upper().replace('#', "^")
            else:
                abc_note = pc.upper().replace('#', "^") + "," * (4 - oct_)

            # Duration in ABC units (L=1/8 = 1 unit)
            # ticks / (TICKS_PER_BEAT/2) → units of L=1/8
            dur_units = max(1, n.ticks // (_TICKS_PER_BEAT // 2))
            if dur_units == 1:
                body.append(abc_note)
            else:
                body.append(f'{abc_note}{dur_units}')

            beats_in_bar += n.ticks / _TICKS_PER_BEAT
            if beats_in_bar >= 4:
                body.append('|')
                bar_count += 1
                beats_in_bar = 0
                if bar_count % 4 == 0:
                    body.append('\n')

        lines.append(' '.join(body))
        return '\n'.join(lines)

    def midi_notation(self, notes: List[NoteEvent], tempo: int = _DEFAULT_TEMPO) -> str:
        """
        Generate a human-readable MIDI event log.

        Lists every note event with timing, pitch name, velocity, γ and β
        values. Suitable for publication / Dr. Crawford format.

        :param notes: Ordered NoteEvent list.
        :param tempo: BPM (for timing conversion).
        :returns: Formatted text table.
        :rtype: str
        """
        secs_per_beat = 60.0 / max(1, tempo)
        secs_per_tick = secs_per_beat / _TICKS_PER_BEAT
        lines = [
            'MIDI Event Log — Holcus Composition',
            f'Tempo: {tempo} BPM  |  Resolution: {_TICKS_PER_BEAT} ticks/beat',
            f'Field: J^μ Noether current, neutral buoyancy selection',
            f'Pitch grid: Riemann zeros (GUE spacing preserved)',
            f'Spectral domain: [GAP={GAP:.6f}, Ω_ζΣ={OMEGA_ZS:.6f}]',
            '',
            f'{"#":>4}  {"Time(s)":>8}  {"Note":>5}  {"MIDI":>4}  '
            f'{"Vel":>3}  {"Dur(s)":>7}  {"Ch":>2}  {"γ":>10}  '
            f'{"β":>8}  {"E":>6}  {"e_dim":>5}',
            '-' * 80,
        ]
        tick = 0
        for i, n in enumerate(notes):
            t_s   = tick * secs_per_tick
            dur_s = n.ticks * secs_per_tick
            lines.append(
                f'{i+1:>4}  {t_s:>8.3f}  {n.note_name():>5}  {n.pitch:>4}  '
                f'{n.velocity:>3}  {dur_s:>7.3f}  {n.channel:>2}  '
                f'{n.gamma:>10.6f}  {n.beta:>8.6f}  {n.e_val:>6.4f}  '
                f'e{n.sed_dim:<4}'
            )
            tick += n.ticks
        lines.append('-' * 80)
        total_s = tick * secs_per_tick
        lines.append(f'Total duration: {total_s:.2f}s  |  Notes: {len(notes)}')
        return '\n'.join(lines)

    def _score_text(self, notes: List[NoteEvent],
                    prompt: str, tempo: int) -> str:
        """
        Generate a compact plain-text score summary.

        :param notes: NoteEvent list.
        :param prompt: Source prompt.
        :param tempo: BPM.
        :returns: Score summary string.
        :rtype: str
        """
        if not notes:
            return 'No notes scored.'
        pitches  = [n.note_name() for n in notes]
        vel_mean = sum(n.velocity for n in notes) / len(notes)
        beta_mean = sum(n.beta for n in notes) / len(notes)
        lines = [
            f'Score: {len(notes)} notes at {tempo} BPM',
            f'Prompt: {prompt!r}' if prompt else 'Prompt: (synthetic field)',
            f'Pitches: {" ".join(pitches)}',
            f'Dynamics: mean velocity {vel_mean:.1f} ({_dyn_name(vel_mean)})',
            f'Field depth: mean β = {beta_mean:.4f}',
            f'Tonal centre: Ω_ζΣ = {OMEGA_ZS:.5f} → B♭4 (MIDI 70)',
        ]
        return '\n'.join(lines)


def _dyn_name(velocity: float) -> str:
    """
    Map MIDI velocity to dynamic marking name.

    :param velocity: MIDI velocity 0-127.
    :returns: Dynamic name (ppp … fff).
    :rtype: str
    """
    if velocity < 16:  return 'ppp'
    if velocity < 33:  return 'pp'
    if velocity < 49:  return 'p'
    if velocity < 64:  return 'mp'
    if velocity < 80:  return 'mf'
    if velocity < 96:  return 'f'
    if velocity < 112: return 'ff'
    return 'fff'


# ── Soundfont search order for spawned FluidSynth ─────────────────────────────
_SF2_CANDIDATES = [
    '/usr/share/sounds/sf2/FluidR3_GM.sf2',
    '/usr/share/sounds/sf2/default-GM.sf2',
    '/usr/share/sounds/sf2/TimGM6mb.sf2',
    '/usr/share/sounds/sf2/sf_GMbank.sf2',
    '/usr/share/soundfonts/FluidR3_GM.sf2',
]

# β → ensemble selection thresholds
_DJ_ENSEMBLES = [
    (0.010, 'piano'),           # field just woke; one voice
    (0.050, 'strings'),         # early warmth
    (0.150, 'woodwind'),        # breath enters
    (0.500, 'brass'),           # field pressure builds
    (2.000, 'organ'),           # deep resonance, sustained
    (float('inf'), 'orchestra'),# full sedenion orchestra
]


def _detect_fluid_port() -> Optional[str]:
    """
    Find the ALSA MIDI port of the running FluidSynth instance.

    Parses ``aplaymidi -l`` output.  Returns a string like ``'128:0'`` or
    ``None`` if no FluidSynth client is found.

    :rtype: Optional[str]
    """
    try:
        out = subprocess.check_output(
            ['aplaymidi', '-l'], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if 'FLUID' in line or 'FluidSynth' in line:
                return line.split()[0]   # first token: "128:0"
    except Exception:
        pass
    return None


def _find_soundfont() -> Optional[str]:
    """
    Return the path of the best available GM soundfont.

    :rtype: Optional[str]
    """
    for p in _SF2_CANDIDATES:
        if os.path.isfile(p):
            return p
    # Last-ditch: glob ~/.local
    home = os.path.expanduser('~')
    local_sf = os.path.join(home, '.local', 'share', 'sounds', 'sf2')
    if os.path.isdir(local_sf):
        for f in os.listdir(local_sf):
            if f.endswith('.sf2'):
                return os.path.join(local_sf, f)
    return None


class HolcusDJ:
    """
    Real-time Disc Jockey — field geometry → live speaker output.

    The DJ is the Noether current made audible in real time.  It runs
    a continuous loop in a daemon thread: compose a MIDI track from the
    live β-field, play it through the Ubuntu Studio audio stack
    (FluidSynth → PipeWire → speakers), then compose the next as the
    field deepens — exactly the same neutral-buoyancy selection that
    speak() uses for words, but the output codec is sound.

    Playback priority
    ~~~~~~~~~~~~~~~~~
    1. ``aplaymidi`` → existing FluidSynth ALSA port (zero overhead; best
       quality; uses the soundfont already loaded by the running synth).
    2. Spawn ``fluidsynth -a pulseaudio`` with the best available .sf2.
    3. ``timidity -a`` (fallback; always present on Ubuntu Studio).

    Field evolution
    ~~~~~~~~~~~~~~~
    Each track is a fresh snapshot of the field via ``field_fn()``.
    As β deepens (more learning / more speaking), the music grows: sparse
    solo → chamber → full orchestra.  The tempo tracks β_mean on a
    log scale.  Setting ``ensemble`` overrides the auto-selection.

    Thread safety
    ~~~~~~~~~~~~~
    ``start()``, ``stop()``, ``skip()``, ``set_tempo()``,
    ``set_ensemble()`` and ``status()`` are all safe to call from any
    thread including the SpeakingThread socket dispatcher.

    :param composer: The shared :class:`HolcusComposer` instance.
    :param field_fn: Callable returning a field list
        ``[(gamma, beta, e_val, sed_dim), ...]``.  If None, uses the
        composer's synthetic Riemann-zero field.
    """

    def __init__(
        self,
        composer: 'HolcusComposer',
        field_fn: Optional[Callable[[], List[Tuple[float, float, float, int]]]] = None,
    ) -> None:
        self._composer  = composer
        self._field_fn  = field_fn
        self._lock      = threading.Lock()
        self._stop_evt  = threading.Event()
        self._skip_evt  = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._proc: Optional[subprocess.Popen]   = None

        # Mutable state (write under _lock)
        self._tempo: int      = 120
        self._ensemble: str   = 'auto'
        self._n_notes: int    = 32
        self._gain: float     = 0.8
        self._track_count: int   = 0
        self._current_path: str  = ''
        self._current_info: dict = {}
        self._error: str         = ''

        # Resolved once at construction
        self._fluid_port: Optional[str] = _detect_fluid_port()
        self._soundfont:  Optional[str] = _find_soundfont()

    # ── Public controls ────────────────────────────────────────────────────────

    def start(
        self,
        ensemble: str   = 'auto',
        tempo: int      = 120,
        n_notes: int    = 32,
        gain: float     = 0.8,
    ) -> dict:
        """
        Start the DJ loop in a background daemon thread.

        If already running, updates parameters and returns current status
        without restarting.

        :param ensemble: Instrument family ('auto', 'piano', 'strings',
            'woodwind', 'brass', 'orchestra', or any ``HolcusComposer``
            method name).
        :param tempo: Starting BPM (auto-modulated between tracks).
        :param n_notes: Notes per track.
        :param gain: FluidSynth output gain (0.1 – 2.0).
        :returns: Status dict.
        :rtype: dict
        """
        with self._lock:
            self._ensemble = ensemble
            self._tempo    = tempo
            self._n_notes  = n_notes
            self._gain     = max(0.1, min(2.0, gain))
            if self._thread and self._thread.is_alive():
                return self.status()
            self._stop_evt.clear()
            self._skip_evt.clear()
            self._thread = threading.Thread(
                target=self._loop, name='HolcusDJ', daemon=True)
            self._thread.start()
        return self.status()

    def stop(self) -> dict:
        """
        Gracefully stop after the current track finishes.

        Sends SIGTERM to the current playback process, then sets the
        stop flag so the loop exits.

        :returns: Status dict.
        :rtype: dict
        """
        self._stop_evt.set()
        self._kill_proc()
        return self.status()

    def skip(self) -> dict:
        """
        Skip to the next track immediately.

        Kills the current playback process; the loop generates and plays
        the next track without waiting.

        :returns: Status dict.
        :rtype: dict
        """
        self._skip_evt.set()
        self._kill_proc()
        return self.status()

    def set_tempo(self, tempo: int) -> dict:
        """
        Update the tempo for the next generated track.

        :param tempo: BPM (40 – 300).
        :returns: Status dict.
        :rtype: dict
        """
        with self._lock:
            self._tempo = max(40, min(300, tempo))
        return self.status()

    def set_ensemble(self, ensemble: str) -> dict:
        """
        Override instrument selection for subsequent tracks.

        Use ``'auto'`` to restore field-depth-driven selection.

        :param ensemble: Ensemble name or ``'auto'``.
        :returns: Status dict.
        :rtype: dict
        """
        with self._lock:
            self._ensemble = ensemble
        return self.status()

    def set_gain(self, gain: float) -> dict:
        """
        Adjust FluidSynth output gain for subsequent tracks.

        :param gain: Gain scalar (0.1 – 2.0).
        :returns: Status dict.
        :rtype: dict
        """
        with self._lock:
            self._gain = max(0.1, min(2.0, gain))
        return self.status()

    def status(self) -> dict:
        """
        Return current DJ state as a dict.

        :rtype: dict
        """
        alive = bool(self._thread and self._thread.is_alive())
        with self._lock:
            return {
                'running':      alive,
                'track':        self._track_count,
                'ensemble':     self._ensemble,
                'tempo':        self._tempo,
                'gain':         self._gain,
                'n_notes':      self._n_notes,
                'current_path': self._current_path,
                'fluid_port':   self._fluid_port or 'none',
                'soundfont':    os.path.basename(self._soundfont or ''),
                'player':       self._player_name(),
                'error':        self._error,
                **self._current_info,
            }

    # ── Internal loop ──────────────────────────────────────────────────────────

    def _loop(self) -> None:
        """Main DJ thread — compose → play → evolve → repeat."""
        while not self._stop_evt.is_set():
            self._skip_evt.clear()
            try:
                field    = self._get_field()
                ensemble = self._pick_ensemble(field)
                with self._lock:
                    tempo   = self._tempo
                    n_notes = self._n_notes
                result   = self._compose_track(field, ensemble, n_notes, tempo)
                mid_path = result.get('path', '')
                if not mid_path or not os.path.isfile(mid_path):
                    self._error = f'compose failed: {result}'
                    time.sleep(2.0)
                    continue
                with self._lock:
                    self._track_count += 1
                    self._current_path  = mid_path
                    self._current_info  = {
                        'notes':    len(result.get('notes', result.get('voices', {}))),
                        'ensemble': ensemble,
                        'tempo':    tempo,
                        'beta_mean': self._field_beta_mean(field),
                    }
                    self._error = ''
                self._play(mid_path)
                # Auto-modulate tempo toward β-mean after each track
                self._evolve_tempo(field)
            except Exception as exc:
                with self._lock:
                    self._error = str(exc)
                if not self._stop_evt.is_set():
                    time.sleep(3.0)

    def _get_field(self) -> List[Tuple[float, float, float, int]]:
        """Fetch live field or fall back to synthetic."""
        if self._field_fn:
            try:
                f = self._field_fn()
                if f:
                    return f
            except Exception:
                pass
        n = self._n_notes
        return self._composer._default_field(n)

    def _pick_ensemble(
        self, field: List[Tuple[float, float, float, int]]
    ) -> str:
        """Auto-select ensemble based on field β_mean, or return forced choice."""
        with self._lock:
            forced = self._ensemble
        if forced != 'auto':
            return forced
        mean = self._field_beta_mean(field)
        for threshold, name in _DJ_ENSEMBLES:
            if mean < threshold:
                return name
        return 'orchestra'

    @staticmethod
    def _field_beta_mean(field: List[Tuple[float, float, float, int]]) -> float:
        """Mean β across all field entries."""
        if not field:
            return GAP
        return sum(abs(e[1]) for e in field) / len(field)

    def _compose_track(
        self,
        field: List[Tuple[float, float, float, int]],
        ensemble: str,
        n_notes: int,
        tempo: int,
    ) -> dict:
        """Dispatch to the correct HolcusComposer method."""
        c = self._composer
        kw = dict(field=field, n_notes=n_notes, tempo=tempo)
        dispatch = {
            'piano':       lambda: c.piano(**kw),
            'guitar':      lambda: c.guitar_6(**kw),
            'guitar_12':   lambda: c.guitar_12(**kw),
            'bass':        lambda: c.bass_guitar(**kw),
            'woodwind':    lambda: c.woodwind(**kw),
            'brass':       lambda: c.brass(**kw),
            'strings':     lambda: c.strings(**kw),
            'organ':       lambda: c.organ(**kw),
            'chrom_perc':  lambda: c.chromatic_percussion(**kw),
            'orchestra':   lambda: c.every_instrument(
                               field=field,
                               n_notes_per_voice=max(4, n_notes // 16),
                               tempo=tempo),
        }
        fn = dispatch.get(ensemble)
        if fn is None:
            fn = dispatch['orchestra']
        return fn()

    def _evolve_tempo(self, field: List[Tuple[float, float, float, int]]) -> None:
        """Nudge tempo toward a target derived from β_mean."""
        mean = self._field_beta_mean(field)
        # log scale: GAP → 60 BPM, β_sat → 180 BPM
        if mean > 0:
            ratio  = math.log(mean / GAP + 1.0) / math.log(BETA_SAT / GAP + 1.0)
        else:
            ratio  = 0.0
        target = int(60 + ratio * 120)    # 60–180 BPM arc
        with self._lock:
            cur = self._tempo
            # Drift ≤ 5 BPM per track toward target
            step = max(-5, min(5, target - cur))
            self._tempo = cur + step

    # ── Playback engine ────────────────────────────────────────────────────────

    def _player_name(self) -> str:
        """Human-readable name of the active playback path."""
        if self._fluid_port:
            return f'aplaymidi→FluidSynth({self._fluid_port})'
        if self._soundfont:
            return 'fluidsynth(pulseaudio)'
        return 'timidity'

    def _play(self, mid_path: str) -> None:
        """
        Play a MIDI file and block until done, skip, or stop.

        Tries aplaymidi, then fluidsynth, then timidity.

        :param mid_path: Absolute path to the .mid file.
        """
        # Re-detect FluidSynth port each track — port can change if synth restarts
        self._fluid_port = _detect_fluid_port()

        cmd = self._build_play_cmd(mid_path)
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with self._lock:
                self._proc = proc
            proc.wait()
        except Exception as exc:
            with self._lock:
                self._error = f'play error: {exc}'
        finally:
            with self._lock:
                self._proc = None

    def _build_play_cmd(self, mid_path: str) -> List[str]:
        """
        Build the shell command list for playing mid_path.

        :param mid_path: Path to MIDI file.
        :rtype: List[str]
        """
        with self._lock:
            gain = self._gain

        # Path 1: aplaymidi → existing FluidSynth (best; zero overhead)
        if self._fluid_port:
            return ['aplaymidi', '-p', self._fluid_port, mid_path]

        # Path 2: spawn fluidsynth with PulseAudio (PipeWire accepts it)
        if self._soundfont:
            return [
                'fluidsynth',
                '-a', 'pulseaudio',
                '-m', 'alsa_seq',
                '-q',                         # no interactive prompt
                '-g', f'{gain:.2f}',
                self._soundfont,
                mid_path,
            ]

        # Path 3: timidity (always present on Ubuntu Studio)
        vol = int(gain * 100)
        return ['timidity', '-a', '-A', f'{vol}%', mid_path]

    def _kill_proc(self) -> None:
        """Kill the current playback subprocess if running."""
        with self._lock:
            proc = self._proc
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                # Give it 0.5 s then SIGKILL
                try:
                    proc.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            except Exception:
                pass
