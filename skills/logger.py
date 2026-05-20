"""
skills/logger.py — Structured logging for Ptolemy.

:description:
    Five log files: learn, skip, gap, system, session.
    Thread-safe append writes. Auto-rotates at configurable size.
    Key=value format — machine-readable, human-readable.

:classes:
    PtolLogger
"""

import os
import time
import threading
from pathlib import Path


class PtolLogger:
    """
    Structured log writer for all five Ptolemy log channels.

    :param log_dir: Directory for log files.
    :param max_bytes: Rotate log when it exceeds this size.
    """

    CHANNELS = ('learn', 'skip', 'gap', 'system', 'session')

    def __init__(self, log_dir: str, max_bytes: int = 10 * 1024 * 1024):
        self._dir      = Path(os.path.expanduser(log_dir))
        self._max      = max_bytes
        self._lock     = threading.Lock()
        self._handles  = {}
        self._dir.mkdir(parents=True, exist_ok=True)
        for ch in self.CHANNELS:
            self._open(ch)

    def _open(self, channel: str):
        path = self._dir / f"{channel}.log"
        self._handles[channel] = open(path, 'a', encoding='utf-8', buffering=1)

    def _rotate(self, channel: str):
        path = self._dir / f"{channel}.log"
        self._handles[channel].close()
        archive = path.with_suffix(f".{int(time.time())}.log")
        path.rename(archive)
        self._open(channel)

    def _write(self, channel: str, fields: dict):
        ts   = time.strftime('%Y-%m-%dT%H:%M:%S')
        body = ' '.join(f"{k}={v}" for k, v in fields.items())
        line = f"{ts} {body}\n"
        with self._lock:
            fh = self._handles[channel]
            fh.write(line)
            if fh.tell() >= self._max:
                self._rotate(channel)

    # ── Public write methods ──────────────────────────────────────────────

    def learn(self, url: str, confidence: float, chunks: int,
              words_added: int, redundancy: float, novelty: float):
        """
        :param url: Source URL or path.
        :param confidence: Mean confidence score for ingested chunks.
        :param chunks: Number of chunks ingested.
        :param words_added: Cumulative words learned this session.
        :param redundancy: Mean redundancy score.
        :param novelty: Mean novelty score.
        """
        self._write('learn', {
            'url':   url[:120],
            'conf':  f"{confidence:.4f}",
            'chunks': chunks,
            'words':  words_added,
            'red':    f"{redundancy:.3f}",
            'nov':    f"{novelty:.3f}",
        })

    def skip(self, url: str, reason: str):
        """
        :param url: Source that was skipped.
        :param reason: Skip reason code or message.
        """
        self._write('skip', {'url': url[:120], 'reason': reason[:80]})

    def gap(self, word: str, j_pos: float, times_seen: int):
        """
        :param word: Gap word identified.
        :param j_pos: Current J_pos (beta) score.
        :param times_seen: How many times encountered.
        """
        self._write('gap', {
            'word':  word,
            'j_pos': f"{j_pos:.5f}",
            'seen':  times_seen,
        })

    def system(self, cpu_pct: float, ram_mb: float,
               queue_depth: int, wpm: float):
        """
        :param cpu_pct: CPU usage percent.
        :param ram_mb: RAM usage in megabytes.
        :param queue_depth: URL queue depth.
        :param wpm: Words per minute learned.
        """
        self._write('system', {
            'cpu':   f"{cpu_pct:.1f}",
            'ram':   f"{ram_mb:.0f}",
            'queue': queue_depth,
            'wpm':   f"{wpm:.1f}",
        })

    def session(self, event: str, **kwargs):
        """
        :param event: Event name (start, stop, checkpoint, etc.).
        :param kwargs: Additional key=value pairs.
        """
        fields = {'event': event}
        fields.update({k: str(v) for k, v in kwargs.items()})
        self._write('session', fields)

    def close(self):
        """Flush and close all log file handles."""
        with self._lock:
            for fh in self._handles.values():
                try:
                    fh.close()
                except Exception:
                    pass
