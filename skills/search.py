"""
skills/search.py — URL queue and corpus seed for Ptolemy.

:description:
    Seeds TeachingThread's URL queue from:
      - Gutenberg via gutendex.com REST API (English .txt, no scraping)
      - archive.org search API (broader corpus)
      - Direct URL injection (FTP, HTTP, ptol://)
    Thread-safe queue. Caller polls next_url().

:classes:
    PtolSearch
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import threading

_GUTENDEX = 'https://gutendex.com/books/'
_ARCHIVE  = 'https://archive.org/search'
_ARCHIVE_DL = 'https://archive.org/download/{ident}/{ident}_djvu.txt'


class PtolSearch:
    """
    URL queue seeded from Gutenberg and archive.org APIs.

    :param opener: urllib opener with Mozilla UA installed.
    :param logger: PtolLogger instance.
    """

    def __init__(self, opener, logger):
        self._opener = opener
        self._logger = logger
        self._queue  = []
        self._lock   = threading.Lock()
        self._gutendex_page    = 1
        self._gutendex_zh_page = 1

    def queue_depth(self) -> int:
        """
        :returns: Number of URLs waiting.
        :rtype: int
        """
        with self._lock:
            return len(self._queue)

    def next_url(self):
        """
        Pop next item from queue.

        :returns: Dict {'url': str, 'meta': CiteMeta|None}, or None if empty.
        :rtype: dict or None
        """
        with self._lock:
            item = self._queue.pop(0) if self._queue else None
            if item is None:
                return None
            # backwards-compat: bare strings still work
            if isinstance(item, str):
                return {'url': item, 'meta': None}
            return item

    def add_url(self, url: str, meta=None):
        """
        Directly enqueue a URL (HTTP, HTTPS, FTP, ptol://) with optional CiteMeta.

        :param url: URL string.
        :param meta: CiteMeta instance (optional). None = default web weight.
        """
        with self._lock:
            self._queue.append({'url': url, 'meta': meta})

    def seed_gutenberg(self) -> bool:
        """
        Fetch one page of English plain-text books from gutendex.com.
        Advances internal page counter on success.

        :returns: True if URLs were added, False on error.
        :rtype: bool
        """
        params = urllib.parse.urlencode({
            'languages': 'en',
            'mime_type': 'text/plain',
            'page':      self._gutendex_page,
        })
        url = _GUTENDEX + '?' + params
        try:
            resp = self._opener.open(url, timeout=30)
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            added = 0
            for book in data.get('results', []):
                for fmt, link in book.get('formats', {}).items():
                    if 'text/plain' in fmt and link.lower().endswith('.txt'):
                        with self._lock:
                            self._queue.append({'url': link, 'meta': None})
                        added += 1
                        break
            if added:
                self._gutendex_page += 1
            return added > 0
        except Exception as exc:
            self._logger.skip(url, f"gutendex:{exc}")
            return False

    def seed_archive(self, query: str = 'language:english', rows: int = 50):
        """
        Fetch text items from archive.org search API.

        :param query: Search query string.
        :param rows: Number of results to request.
        """
        params = urllib.parse.urlencode({
            'q':      query + ' mediatype:texts',
            'fl[]':   'identifier',
            'rows':   rows,
            'output': 'json',
        })
        url = _ARCHIVE + '?' + params
        try:
            resp = self._opener.open(url, timeout=30)
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            docs = data.get('response', {}).get('docs', [])
            for doc in docs:
                ident = doc.get('identifier', '')
                if ident:
                    dl = _ARCHIVE_DL.format(ident=ident)
                    with self._lock:
                        self._queue.append({'url': dl, 'meta': None})
        except Exception as exc:
            self._logger.skip(url, f"archive:{exc}")

    def seed_mandarin(self) -> bool:
        """
        Fetch one page of Mandarin (zh) plain-text books from gutendex.com.
        Falls back to archive.org language:chinese query if gutendex returns nothing.
        Advances internal zh page counter on success.

        :returns: True if URLs were added, False on error.
        :rtype: bool
        """
        params = urllib.parse.urlencode({
            'languages': 'zh',
            'mime_type': 'text/plain',
            'page':      self._gutendex_zh_page,
        })
        url = _GUTENDEX + '?' + params
        added = 0
        try:
            resp = self._opener.open(url, timeout=30)
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            for book in data.get('results', []):
                for fmt, link in book.get('formats', {}).items():
                    if 'text/plain' in fmt and link.lower().endswith('.txt'):
                        with self._lock:
                            self._queue.append({'url': link, 'meta': None})
                        added += 1
                        break
            if added:
                self._gutendex_zh_page += 1
        except Exception as exc:
            self._logger.skip(url, f"gutendex_zh:{exc}")

        # Fallback: archive.org Chinese texts
        if not added:
            self.seed_archive(query='language:chinese')
            added = 1   # optimistic — archive may have results

        return added > 0

    def seed_ftp_gutenberg(self):
        """
        Add FTP mirror URLs for bulk Gutenberg access.
        urllib handles ftp:// natively — no HTTP rate limits.
        """
        ftp_roots = [
            'ftp://ftp.ibiblio.org/pub/docs/books/gutenberg/',
            'ftp://mirrors.xmission.com/gutenberg/',
        ]
        for root in ftp_roots:
            with self._lock:
                self._queue.append(root)
