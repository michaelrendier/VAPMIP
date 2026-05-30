"""
skills/sensor.py — Physical sensor bridge: e₀..e₇ (first 𝕆 / lower half).

:description:
    SensorReader maps 8 live sensor channels onto the first octonion copy
    of the sedenion field (e₀..e₇) via MindEye.see().

    The 8 channels mirror the lower-𝕆 operator labels::

        e₀  identity   — raw scalar / amplitude
        e₁  negate     — inverse / phase-flip signal
        e₂  bind       — coupling strength / coherence
        e₃  name       — source label hash (normalised)
        e₄  apply      — transform output / activation
        e₅  abstract   — spectral envelope / frequency centroid
        e₆  branch     — bifurcation index / modal split
        e₇  iterate    — temporal phase / cycle counter

    Data sources (all read from ``~/.ptolemy/live_state.json``):
      - Manual write by external process (e.g. microphone capture, GPIO)
      - MIT Dolphin acoustic channels (24D → 8D projection, pending)
      - Any 8-float vector keyed under ``"sensor"`` in the JSON

    The zero-divisor bridge means sensor data in e₀..e₇ reaches
    cognitive dims e₈..e₁₅ only through the 42 Cawagas callosum pairs.
    SensorReader feeds that lower half so the upper half can respond.

:classes:
    SensorReader

:constants:
    CHANNEL_NAMES, DEFAULT_STATE_PATH
"""

import json
import math
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional

DEFAULT_STATE_PATH = os.path.expanduser('~/.ptolemy/live_state.json')

# Lower-𝕆 operator labels (mirrors draw.py _OP)
CHANNEL_NAMES = {
    0: 'identity',
    1: 'negate',
    2: 'bind',
    3: 'name',
    4: 'apply',
    5: 'abstract',
    6: 'branch',
    7: 'iterate',
}


class SensorReader:
    """
    Physical sensor bridge for the lower octonion (e₀..e₇).

    Reads ``~/.ptolemy/live_state.json``, extracts 8 channel values,
    and forwards them into ``MindEye.see()`` so the cognitive half
    (e₈..e₁₅) can respond via zero-divisor callosum coupling.

    :param engine: Live ``Engine`` instance.
    :param state_path: Path to ``live_state.json``. Defaults to
        ``~/.ptolemy/live_state.json``.

    :Example:

    .. code-block:: python

        sr = engine.get_sensor_reader()
        result = sr.see()
        print(result['callosum'], result['channels'])

        # Start background poll loop
        sr.watch(interval=1.0)
        # ... later ...
        sr.stop()
    """

    def __init__(self, engine, state_path: str = DEFAULT_STATE_PATH):
        self._engine     = engine
        self._state_path = state_path
        self._lock       = threading.Lock()
        self._watching   = False
        self._thread: Optional[threading.Thread] = None
        self._last_read: Dict[str, Any] = {}
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []

    # ── I/O ──────────────────────────────────────────────────────────────────

    def read(self) -> Dict[str, float]:
        """
        Read 8 sensor channels from ``live_state.json``.

        Returns a dict keyed by channel name. Missing channels default to 0.0.
        If the file does not exist or cannot be parsed, returns all zeros.

        :returns: Dict mapping channel name → float value.
        :rtype: dict
        """
        channels: Dict[str, float] = {name: 0.0 for name in CHANNEL_NAMES.values()}
        if not os.path.exists(self._state_path):
            return channels
        try:
            with open(self._state_path, 'r') as f:
                data = json.load(f)
        except Exception:
            return channels

        sensor = data.get('sensor', {})
        if isinstance(sensor, list):
            # list form: [v0, v1, ..., v7]
            for i, v in enumerate(sensor[:8]):
                if i in CHANNEL_NAMES:
                    channels[CHANNEL_NAMES[i]] = float(v)
        elif isinstance(sensor, dict):
            # dict form: {'identity': 0.3, 'negate': 0.7, ...}
            # also accepts integer keys '0'..'7'
            for k, v in sensor.items():
                if k in CHANNEL_NAMES.values():
                    channels[k] = float(v)
                elif str(k).isdigit():
                    idx = int(k)
                    if idx in CHANNEL_NAMES:
                        channels[CHANNEL_NAMES[idx]] = float(v)

        with self._lock:
            self._last_read = dict(channels)
        return channels

    def write(self, channels: Dict[str, float]) -> bool:
        """
        Write sensor channels to ``live_state.json`` (creates if absent).

        Only writes the ``"sensor"`` key; preserves all other top-level keys.

        :param channels: Dict mapping channel name or int index → value.
        :returns: True on success, False on error.
        :rtype: bool
        """
        data: Dict[str, Any] = {}
        if os.path.exists(self._state_path):
            try:
                with open(self._state_path, 'r') as f:
                    data = json.load(f)
            except Exception:
                pass
        # Normalise to name-keyed dict
        norm: Dict[str, float] = {}
        for k, v in channels.items():
            if k in CHANNEL_NAMES.values():
                norm[k] = float(v)
            elif str(k).isdigit():
                idx = int(k)
                if idx in CHANNEL_NAMES:
                    norm[CHANNEL_NAMES[idx]] = float(v)
        data['sensor'] = norm
        try:
            os.makedirs(os.path.dirname(self._state_path), exist_ok=True)
            with open(self._state_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    # ── field ingestion ───────────────────────────────────────────────────────

    def see(self) -> Dict[str, Any]:
        """
        Read sensor state and encode into MindEye (e₈..e₁₅).

        The 8 channel values become the second-𝕆 vector. The callosum
        coupling strength (e₁₅) is computed by MindEye from the vector norm
        vs. OMEGA_ZS. High coupling = sensor state near the neutral buoyancy
        surface = maximum zero-divisor channel activation.

        :returns: Dict with keys ``channels``, ``callosum``, ``heard``.
        :rtype: dict
        """
        channels = self.read()
        vec      = [channels[CHANNEL_NAMES[i]] for i in range(8)]

        # Normalise vector to unit range for MindEye
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]

        me   = self._engine.get_mind_eye()
        seen = me.see(vec, label='sensor')
        heard = ''
        try:
            # Synthesise a description from the strongest channel
            top_dim = max(range(8), key=lambda i: abs(vec[i]))
            prompt  = CHANNEL_NAMES[top_dim]
            heard   = self._engine.hear(prompt)
        except Exception:
            pass
        return {'channels': channels, 'vec': vec,
                'callosum': seen.get('callosum', 0.0), 'heard': heard}

    # ── poll loop ─────────────────────────────────────────────────────────────

    def on_update(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback invoked on each successful sensor read during watch().

        :param callback: Callable receiving the result dict from ``see()``.
        """
        self._callbacks.append(callback)

    def watch(self, interval: float = 1.0):
        """
        Start background poll loop. Calls ``see()`` every ``interval`` seconds.

        Non-blocking — spawns a daemon thread. Safe to call multiple times
        (second call is a no-op if already watching).

        :param interval: Poll interval in seconds.
        """
        if self._watching:
            return
        self._watching = True

        def _loop():
            while self._watching:
                try:
                    result = self.see()
                    for cb in list(self._callbacks):
                        try:
                            cb(result)
                        except Exception:
                            pass
                except Exception:
                    pass
                time.sleep(interval)

        self._thread = threading.Thread(target=_loop, daemon=True,
                                        name='SensorReader')
        self._thread.start()

    def stop(self):
        """
        Stop the background poll loop.

        :returns: ``{'watching': False}``.
        :rtype: dict
        """
        self._watching = False
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        return {'watching': False}

    def status(self) -> Dict[str, Any]:
        """
        Return current watcher status and last read channels.

        :returns: Dict with keys ``watching``, ``last_read``, ``path``.
        :rtype: dict
        """
        with self._lock:
            last = dict(self._last_read)
        return {'watching': self._watching, 'last_read': last,
                'path': self._state_path}
