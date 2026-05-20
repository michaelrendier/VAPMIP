"""
skills/crawler.py — Fetch, classify, and chunk web content for Ptolemy.

:description:
    Mozilla UA opener. robots.txt compliance cached per host.
    html2text strips HTML to prose. Plain .txt bypasses conversion.
    iter_paragraphs() yields blank-line-delimited chunks line-by-line
    (C-buffered I/O — approaches RAM access speed for large files).

:classes:
    PtolCrawler
"""

import os
import time
import threading
import urllib.request
import urllib.robotparser
import urllib.parse
import urllib.error
from pathlib import Path

try:
    import html2text as _h2t_mod
    _H2T_AVAILABLE = True
except ImportError:
    _H2T_AVAILABLE = False

_UA = ('Mozilla/5.0 (X11; Linux x86_64; rv:109.0) '
       'Gecko/20100101 Firefox/115.0')

_ACCEPT = ('text/html,text/plain,application/xhtml+xml,'
           'application/xml;q=0.9,*/*;q=0.8')


class PtolCrawler:
    """
    Fetcher and text extractor.

    :param staging: PtolStaging instance.
    :param logger: PtolLogger instance.
    :param config: PtolConfig instance.
    """

    def __init__(self, staging, logger, config):
        self._staging = staging
        self._logger  = logger
        self._config  = config
        self._robots  = {}
        self._rlock   = threading.Lock()

        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('User-Agent',      _UA),
            ('Accept',          _ACCEPT),
            ('Accept-Language', 'en-US,en;q=0.9'),
        ]
        urllib.request.install_opener(self.opener)

        if _H2T_AVAILABLE:
            self._h2t = _h2t_mod.HTML2Text()
            self._h2t.ignore_links   = True
            self._h2t.ignore_images  = True
            self._h2t.ignore_tables  = False
            self._h2t.body_width     = 0
            self._h2t.unicode_snob   = True
        else:
            self._h2t = None

    # ── robots.txt ────────────────────────────────────────────────────────

    def _robots_ok(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        scheme = parsed.scheme
        if scheme in ('ftp', 'file', 'ptol'):
            return True
        host = parsed.netloc
        with self._rlock:
            if host not in self._robots:
                rp = urllib.robotparser.RobotFileParser()
                try:
                    rp.set_url(f"{scheme}://{host}/robots.txt")
                    rp.read()
                except Exception:
                    rp = None
                self._robots[host] = rp
            rp = self._robots[host]
        return rp is None or rp.can_fetch(_UA, url)

    # ── fetch ─────────────────────────────────────────────────────────────

    def fetch(self, url: str, timeout: int = 60):
        """
        Download URL to staging area.

        :param url: URL to fetch (http/https/ftp/file).
        :param timeout: Request timeout in seconds.
        :returns: (Path, content_type_str) or (None, reason_str).
        :rtype: tuple
        """
        if self._staging.already_seen(url):
            return None, 'cached'

        if not self._robots_ok(url):
            self._logger.skip(url, 'robots')
            return None, 'robots'

        parsed   = urllib.parse.urlparse(url)
        raw_name = parsed.path.split('/')[-1] or 'download'
        dest     = self._staging.stage_path(raw_name)

        delay = self._config.getfloat('crawl_delay', 1.5)
        time.sleep(delay)

        try:
            urllib.request.urlretrieve(url, dest)
        except urllib.error.HTTPError as exc:
            self._logger.skip(url, f"http_{exc.code}")
            return None, f"http_{exc.code}"
        except urllib.error.URLError as exc:
            self._logger.skip(url, f"url:{exc.reason}")
            return None, 'url_error'
        except Exception as exc:
            self._logger.skip(url, f"err:{exc}")
            return None, 'error'

        checksum = self._staging.checksum(dest)
        self._staging.mark_visited(url, checksum)
        ctype = self._detect_type(dest, url)
        return dest, ctype

    # ── type detection ────────────────────────────────────────────────────

    def _detect_type(self, path, url: str) -> str:
        url_l = url.lower()
        if url_l.endswith('.txt'):  return 'text'
        if url_l.endswith('.htm'):  return 'html'
        if url_l.endswith('.html'): return 'html'
        if url_l.endswith('.pdf'):  return 'pdf'
        try:
            with open(path, 'rb') as fh:
                head = fh.read(512).decode('utf-8', errors='ignore').lower()
            if '<html' in head or '<!doc' in head:
                return 'html'
        except Exception:
            pass
        return 'text'

    # ── text extraction ───────────────────────────────────────────────────

    def to_text(self, path, content_type: str):
        """
        Convert staged file to plain text string.

        :param path: Path to staged file.
        :param content_type: 'text', 'html', or 'pdf'.
        :returns: Plain text string or None on failure.
        :rtype: str or None
        """
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                raw = fh.read()
            if content_type == 'html':
                if self._h2t:
                    return self._h2t.handle(raw)
                # fallback: strip tags naively
                import re
                return re.sub(r'<[^>]+>', ' ', raw)
            return raw
        except Exception:
            return None

    # ── chunking ──────────────────────────────────────────────────────────

    def iter_paragraphs(self, text: str):
        """
        Yield paragraph-sized chunks from plain text.
        Uses line-by-line iteration (C-buffered, RAM-speed for large files).
        Blank lines delimit paragraphs.

        :param text: Plain text string.
        :returns: Generator of paragraph strings.
        :rtype: generator
        """
        chunk = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                chunk.append(stripped)
            elif chunk:
                yield ' '.join(chunk)
                chunk = []
        if chunk:
            yield ' '.join(chunk)
