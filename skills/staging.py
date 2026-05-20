"""
skills/staging.py — File staging and checksum cache for Ptolemy.

:description:
    Manages ~/.ptolemy/.ptoltemp/ for fetch-stage-ingest-remove cycle.
    Tracks visited URLs in a flat checksum log to prevent re-ingestion.
    Staged files persist across crashes — TeachingThread resumes from them.

:classes:
    PtolStaging
"""

import os
import hashlib
import threading
from pathlib import Path


class PtolStaging:
    """
    Staging area and visit cache.

    :param temp_dir: Staging directory path.
    :param cache_dir: Cache directory path (visited.log lives here).
    """

    def __init__(self, temp_dir: str, cache_dir: str):
        self._temp  = Path(os.path.expanduser(temp_dir))
        self._cache = Path(os.path.expanduser(cache_dir))
        self._lock  = threading.Lock()
        self._visited: set = set()
        self.ensure_dirs()
        self._load_visited()

    def ensure_dirs(self):
        """Create staging and cache directories if absent."""
        self._temp.mkdir(parents=True, exist_ok=True)
        self._cache.mkdir(parents=True, exist_ok=True)

    def _load_visited(self):
        vpath = self._cache / 'visited.log'
        if not vpath.exists():
            return
        with open(vpath, encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                parts = line.split()
                if parts:
                    self._visited.add(parts[0])

    def already_seen(self, url: str) -> bool:
        """
        :param url: URL to check.
        :returns: True if URL has been ingested previously.
        :rtype: bool
        """
        with self._lock:
            return url in self._visited

    def mark_visited(self, url: str, checksum: str):
        """
        Record URL as ingested.

        :param url: Ingested URL.
        :param checksum: SHA-256 hex digest of fetched content.
        """
        vpath = self._cache / 'visited.log'
        with self._lock:
            self._visited.add(url)
            with open(vpath, 'a', encoding='utf-8') as fh:
                fh.write(f"{url} {checksum}\n")

    def stage_path(self, filename: str) -> Path:
        """
        Return a unique path in .ptoltemp/ for this filename.

        :param filename: Base filename.
        :returns: Unique Path in temp dir.
        :rtype: Path
        """
        dest = self._temp / filename
        counter = 0
        stem   = Path(filename).stem
        suffix = Path(filename).suffix or '.txt'
        while dest.exists():
            counter += 1
            dest = self._temp / f"{stem}_{counter}{suffix}"
        return dest

    def checksum(self, path) -> str:
        """
        SHA-256 of file content.

        :param path: File path.
        :returns: Hex digest string.
        :rtype: str
        """
        h = hashlib.sha256()
        with open(path, 'rb') as fh:
            for block in iter(lambda: fh.read(65536), b''):
                h.update(block)
        return h.hexdigest()

    def remove(self, path):
        """
        Delete a staged file. Silently ignores missing files.

        :param path: File path to delete.
        """
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    def pending(self):
        """
        Files in temp dir awaiting ingestion (crash resume).

        :returns: List of Path objects.
        :rtype: list
        """
        try:
            return [p for p in self._temp.iterdir() if p.is_file()]
        except Exception:
            return []
