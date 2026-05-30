"""
skills/corpus.py — Generic parameterised corpus seeder.

Any ``[TAG] URL`` corpus .txt file becomes a study loop.
FoundationsCorpus and MeaningCorpus are specialisations; this class
handles arbitrary corpora (Python PEPs, C/POSIX, future additions).

Architecture: one Engine instance per corpus — completely isolated
from the primary field and from each other.

:bin path:  ``~/.ptolemy/monad_<name>.bin``
:txt path:  supplied at construction or defaulted from corpus name
"""

import os
import re
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# Import Engine from the parent package.  When running inside the APK
# the package root is on sys.path; when running from the repo root the
# import also resolves correctly.
from monad import Engine


# Tags that receive weight 2.0 by default when no custom set is supplied.
_DEFAULT_PRIMARY_TAGS: Set[str] = {
    'PRIMARY', 'TESTIMONY', 'ATTRACTOR',
    'SPEC', 'POSIX', 'CAPI',
    'DATAMODEL', 'REFERENCE', 'PEP', 'WHATSNEW', 'API',
}


def parse_corpus_txt(
    txt_path: str,
    primary_tags: Optional[Set[str]] = None,
    primary_weight: float = 2.0,
    context_weight: float = 1.0,
) -> List[Tuple[str, str, float]]:
    """Parse a ``[TAG] URL`` corpus file into ``(tag, url, weight)`` tuples.

    Lines that do not match ``[TAG] https://...`` are ignored (comments,
    blank lines, section headers).

    :param txt_path: Path to corpus ``.txt`` file.
    :param primary_tags: Set of tag strings that receive *primary_weight*.
        Defaults to :data:`_DEFAULT_PRIMARY_TAGS`.
    :param primary_weight: Weight for primary-tier tags.
    :param context_weight: Weight for all other tags.
    :returns: List of ``(tag, url, weight)`` tuples.
    :rtype: list
    """
    if primary_tags is None:
        primary_tags = _DEFAULT_PRIMARY_TAGS
    results: List[Tuple[str, str, float]] = []
    pattern = re.compile(r'^\[([A-Z]+)\]\s+(https?://\S+)')
    try:
        with open(txt_path, encoding='utf-8') as f:
            for line in f:
                m = pattern.match(line.strip())
                if m:
                    tag, url = m.group(1), m.group(2)
                    weight = primary_weight if tag in primary_tags else context_weight
                    results.append((tag, url, weight))
    except OSError:
        pass
    return results


class GenericCorpus:
    """Autonomous corpus study loop for any ``[TAG] URL`` corpus file.

    Creates its own Engine instance and checkpoint file.  Never feeds
    the primary monad field.

    :param engine: Engine instance (dedicated — do not share).
    :param txt_path: Path to corpus ``.txt`` file.
    :param bin_path: Path for the ``.bin`` checkpoint.
    :param name: Human-readable name used in logging.
    :param interval: Seconds between fetches in the continuous loop.
    :param primary_tags: Tags that receive weight 2.0.
    :param primary_weight: Weight applied to primary-tier URLs.
    :param context_weight: Weight applied to all other URLs.
    """

    def __init__(
        self,
        engine: Engine,
        txt_path: str,
        bin_path: str,
        name: str = 'corpus',
        interval: int = 60,
        primary_tags: Optional[Set[str]] = None,
        primary_weight: float = 2.0,
        context_weight: float = 1.0,
    ) -> None:
        self._engine         = engine
        self._txt_path       = txt_path
        self._bin_path       = bin_path
        self._name           = name
        self._interval       = interval
        self._primary_tags   = primary_tags or _DEFAULT_PRIMARY_TAGS
        self._primary_weight = primary_weight
        self._context_weight = context_weight

        self._lock    = threading.Lock()
        self._running = False
        self._halt    = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._studied = 0

        if os.path.exists(bin_path):
            try:
                self._engine.load_bin(bin_path)
            except Exception:
                pass

    # ── internal helpers ───────────────────────────────────────────────────

    def _get_corpus(self) -> List[Tuple[str, str, float]]:
        """Load and return the corpus URL list from the .txt file."""
        return parse_corpus_txt(
            self._txt_path,
            primary_tags=self._primary_tags,
            primary_weight=self._primary_weight,
            context_weight=self._context_weight,
        )

    def _fetch_text(self, url: str, timeout: int = 12) -> str:
        """Fetch plain text from *url*.  Returns empty string on failure."""
        try:
            import urllib.request
            import html.parser

            class _Stripper(html.parser.HTMLParser):
                def __init__(self):
                    super().__init__()
                    self._parts: List[str] = []
                    self._skip = False

                def handle_starttag(self, tag, attrs):
                    if tag in ('script', 'style', 'nav', 'footer'):
                        self._skip = True

                def handle_endtag(self, tag):
                    if tag in ('script', 'style', 'nav', 'footer'):
                        self._skip = False

                def handle_data(self, data):
                    if not self._skip:
                        self._parts.append(data)

                def text(self) -> str:
                    return ' '.join(self._parts)

            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Ptolemy/3.0 corpus-seeder'},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(1_000_000).decode('utf-8', errors='replace')
            s = _Stripper()
            s.feed(raw)
            return s.text()
        except Exception:
            return ''

    def _save(self) -> None:
        """Save Engine state to the checkpoint file."""
        try:
            self._engine.save_session(self._bin_path)
        except Exception:
            pass

    def _wait_network(self, check_interval: int = 10) -> None:
        """Block until 8.8.8.8:53 is reachable, saving state on first failure.

        :param check_interval: Seconds between connectivity checks.
        """
        first = True
        while True:
            try:
                s = socket.create_connection(('8.8.8.8', 53), timeout=3)
                s.close()
                return
            except OSError:
                if first:
                    self._save()
                    first = False
                time.sleep(check_interval)

    # ── public API ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the continuous background study loop."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._halt.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name=f'corpus-{self._name}',
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> Dict[str, Any]:
        """Stop the background study loop and save state.

        :returns: Status dict.
        :rtype: dict
        """
        self._halt.set()
        with self._lock:
            self._running = False
        self._save()
        return self.status()

    def status(self) -> Dict[str, Any]:
        """Return current corpus status.

        :returns: Dict with ``running``, ``studied``, ``corpus_size``,
            ``bin_path``, ``txt_path``, ``name``.
        :rtype: dict
        """
        corpus = self._get_corpus()
        return {
            'running':     self._running,
            'name':        self._name,
            'studied':     self._studied,
            'corpus_size': len(corpus),
            'bin_path':    self._bin_path,
            'txt_path':    self._txt_path,
            'bin_exists':  os.path.exists(self._bin_path),
        }

    def force_study(self, text: str, weight: float = 2.0) -> Dict[str, Any]:
        """Immediately study *text* into this corpus Engine.

        :param text: Text to study.
        :param weight: Study weight.
        :returns: Result dict.
        :rtype: dict
        """
        st = self._engine.get_study()
        with self._lock:
            st.study(text, weight=weight, triggering_text=f'force:{self._name}')
            self._studied += 1
        self._save()
        return {'studied': self._studied}

    def seed(
        self,
        on_progress: Optional[Callable] = None,
        check_interval: int = 10,
    ) -> Dict[str, Any]:
        """Run one complete pass through the corpus (blocking).

        Fetches every URL in order, studies each, saves on network failure
        and waits for connectivity before continuing.  Returns when the last
        URL has been attempted.

        :param on_progress: Callable(tag, url, idx, total, studied, skipped)
            invoked after each URL.
        :param check_interval: Seconds between network retry attempts.
        :returns: ``{'studied', 'skipped', 'total', 'complete', 'bin_path'}``.
        :rtype: dict
        """
        corpus  = self._get_corpus()
        total   = len(corpus)
        skipped = 0

        for idx, (tag, url, weight) in enumerate(corpus):
            self._wait_network(check_interval)
            text = self._fetch_text(url)
            if not text or len(text) < 40:
                skipped += 1
            else:
                st = self._engine.get_study()
                with self._lock:
                    st.study(text, weight=weight,
                             triggering_text=f'{tag} {url}')
                    self._studied += 1
                self._save()

            if on_progress:
                try:
                    on_progress(tag, url, idx, total, self._studied, skipped)
                except Exception:
                    pass

        self._save()
        return {
            'studied':  self._studied,
            'skipped':  skipped,
            'total':    total,
            'complete': True,
            'bin_path': self._bin_path,
        }

    # ── continuous loop ────────────────────────────────────────────────────

    def _loop(self) -> None:
        """Background study loop — fetches the full corpus repeatedly."""
        while not self._halt.is_set():
            corpus = self._get_corpus()
            for tag, url, weight in corpus:
                if self._halt.is_set():
                    break
                self._wait_network()
                text = self._fetch_text(url)
                if text and len(text) >= 40:
                    st = self._engine.get_study()
                    with self._lock:
                        st.study(text, weight=weight,
                                 triggering_text=f'{tag} {url}')
                        self._studied += 1
                    self._save()
                if not self._halt.wait(self._interval):
                    continue
        with self._lock:
            self._running = False
