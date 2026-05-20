"""
skills/monitor.py — Process monitoring and throttle control.

:description:
    Polls CPU and RAM usage on a configurable interval.
    Sets a throttle signal when either exceeds configured limits.
    TeachingThread checks should_throttle() before each chunk.
    Writes system metrics to system.log via PtolLogger.

:classes:
    PtolMonitor
"""

import os
import sys
import time
import resource
import threading


class PtolMonitor:
    """
    System resource monitor and teaching throttle.

    :param logger: PtolLogger instance.
    :param config: PtolConfig instance.
    """

    def __init__(self, logger, config):
        self._logger    = logger
        self._config    = config
        self._stop      = threading.Event()
        self._throttle  = threading.Event()
        self._lock      = threading.Lock()
        self._wpm       = 0.0
        self._queue_d   = 0
        self._cpu_prev  = self._cpu_times()
        self._time_prev = time.monotonic()
        self._thread    = threading.Thread(
            target=self._loop, name='MonitorThread', daemon=True)

    def start(self):
        """Start the background monitor thread."""
        self._thread.start()

    def stop(self):
        """Signal monitor thread to exit."""
        self._stop.set()

    def should_throttle(self) -> bool:
        """
        :returns: True when teaching thread should yield.
        :rtype: bool
        """
        return self._throttle.is_set()

    def update_stats(self, wpm: float = None, queue_depth: int = None):
        """
        Update live stats for system.log.

        :param wpm: Words per minute currently being learned.
        :param queue_depth: URL queue depth.
        """
        with self._lock:
            if wpm is not None:
                self._wpm = wpm
            if queue_depth is not None:
                self._queue_d = queue_depth

    def _cpu_times(self) -> float:
        t = os.times()
        return t.user + t.system

    def _ram_mb(self) -> float:
        if sys.platform == 'linux':
            try:
                with open('/proc/self/status', encoding='utf-8') as fh:
                    for line in fh:
                        if line.startswith('VmRSS:'):
                            return int(line.split()[1]) / 1024.0
            except Exception:
                pass
        ru = resource.getrusage(resource.RUSAGE_SELF)
        # Linux: KB, macOS: bytes
        divisor = 1024.0 if sys.platform == 'linux' else (1024.0 * 1024.0)
        return ru.ru_maxrss / divisor

    def _loop(self):
        while not self._stop.wait(0):
            interval = self._config.getfloat('monitor_interval', 30)
            if self._stop.wait(interval):
                break

            now        = time.monotonic()
            cpu_now    = self._cpu_times()
            elapsed    = now - self._time_prev
            cpu_pct    = ((cpu_now - self._cpu_prev) / elapsed * 100.0
                          if elapsed > 0 else 0.0)
            ram_mb     = self._ram_mb()
            max_cpu    = self._config.getfloat('max_cpu_percent', 25)
            max_ram    = self._config.getfloat('max_ram_mb', 512)

            with self._lock:
                wpm  = self._wpm
                qdep = self._queue_d

            self._logger.system(cpu_pct, ram_mb, qdep, wpm)

            if cpu_pct > max_cpu or ram_mb > max_ram:
                self._throttle.set()
            else:
                self._throttle.clear()

            self._cpu_prev  = cpu_now
            self._time_prev = now
