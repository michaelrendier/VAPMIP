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

# Direct Gutenberg cache URLs — used when gutendex.com API is unavailable.
# Format: /cache/epub/{id}/pg{id}.txt — stable, no redirect required.
_GUTENBERG_DIRECT = [
    'https://www.gutenberg.org/cache/epub/2701/pg2701.txt',   # Moby Dick
    'https://www.gutenberg.org/cache/epub/1342/pg1342.txt',   # Pride and Prejudice
    'https://www.gutenberg.org/cache/epub/2600/pg2600.txt',   # War and Peace
    'https://www.gutenberg.org/cache/epub/98/pg98.txt',       # A Tale of Two Cities
    'https://www.gutenberg.org/cache/epub/84/pg84.txt',       # Frankenstein
    'https://www.gutenberg.org/cache/epub/11/pg11.txt',       # Alice in Wonderland
    'https://www.gutenberg.org/cache/epub/1661/pg1661.txt',   # Sherlock Holmes
    'https://www.gutenberg.org/cache/epub/76/pg76.txt',       # Huckleberry Finn
    'https://www.gutenberg.org/cache/epub/174/pg174.txt',     # Dorian Gray
    'https://www.gutenberg.org/cache/epub/1400/pg1400.txt',   # Great Expectations
    'https://www.gutenberg.org/cache/epub/345/pg345.txt',     # Dracula
    'https://www.gutenberg.org/cache/epub/4300/pg4300.txt',   # Ulysses
    'https://www.gutenberg.org/cache/epub/5200/pg5200.txt',   # Metamorphosis
    'https://www.gutenberg.org/cache/epub/2852/pg2852.txt',   # Hound of the Baskervilles
    'https://www.gutenberg.org/cache/epub/55/pg55.txt',       # Wizard of Oz
    'https://www.gutenberg.org/cache/epub/1232/pg1232.txt',   # The Prince (Machiavelli)
    'https://www.gutenberg.org/cache/epub/1080/pg1080.txt',   # A Modest Proposal
    'https://www.gutenberg.org/cache/epub/16/pg16.txt',       # Peter Pan
    'https://www.gutenberg.org/cache/epub/1952/pg1952.txt',   # The Yellow Wallpaper
    'https://www.gutenberg.org/cache/epub/219/pg219.txt',     # Heart of Darkness
    'https://www.gutenberg.org/cache/epub/1260/pg1260.txt',   # Jane Eyre
    'https://www.gutenberg.org/cache/epub/766/pg766.txt',     # David Copperfield
    'https://www.gutenberg.org/cache/epub/2814/pg2814.txt',   # Dubliners
    'https://www.gutenberg.org/cache/epub/514/pg514.txt',     # Little Women
    'https://www.gutenberg.org/cache/epub/1251/pg1251.txt',   # Leviathan (Hobbes)
    'https://www.gutenberg.org/cache/epub/4363/pg4363.txt',   # Beyond Good and Evil
    'https://www.gutenberg.org/cache/epub/5827/pg5827.txt',   # Thus Spoke Zarathustra
    'https://www.gutenberg.org/cache/epub/1184/pg1184.txt',   # The Count of Monte Cristo
    'https://www.gutenberg.org/cache/epub/2591/pg2591.txt',   # Grimms Fairy Tales
    'https://www.gutenberg.org/cache/epub/3207/pg3207.txt',   # Critique of Pure Reason
]


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
        Falls back to _GUTENBERG_DIRECT list when gutendex API is unavailable.
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
            resp = self._opener.open(url, timeout=10)
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

        # Fallback: direct Gutenberg cache URLs (stable, no API required)
        direct_idx = getattr(self, '_direct_idx', 0)
        batch = _GUTENBERG_DIRECT[direct_idx:direct_idx + 5]
        if not batch:
            self._direct_idx = 0
            batch = _GUTENBERG_DIRECT[:5]
        else:
            self._direct_idx = direct_idx + 5
        with self._lock:
            for link in batch:
                self._queue.append({'url': link, 'meta': None})
        return len(batch) > 0

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
