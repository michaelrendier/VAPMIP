"""
skills/search.py — URL queue, corpus seed, and context search for Ptolemy.

:description:
    Seeds TeachingThread's URL queue from:
      - Gutenberg via gutendex.com REST API (English .txt, no scraping)
      - archive.org search API (broader corpus)
      - Direct URL injection (FTP, HTTP, ptol://)
    Thread-safe queue. Caller polls next_url().

    SearchContext — live semantic search feeding directly into the field:
      - arXiv API (preprints, STEM, Riemann/physics/CS)
      - Wikipedia REST API (broad encyclopaedic context)
      - Semantic Scholar Open API (citations, abstracts)
      - LMFDB API (L-functions, Riemann zero data)
    All results pass the P5 cepstrum adversarial gate before field ingestion.
    Results flow: search → gate → MindEye.see() → hear().

:classes:
    PtolSearch, SearchContext
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import math
import re
import threading
from typing import Any, Dict, List, Optional

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


# ── P5 cepstrum gate (standalone, mirrors github.py) ─────────────────────────

def _cepstrum_gate(text: str, threshold: float = 0.15) -> Dict[str, Any]:
    """
    P5 adversarial gate. Character-frequency Zipfian deviation + injection scan.

    :param text: Text to evaluate.
    :param threshold: Spectral-deviation threshold.
    :returns: ``{'pass': bool, 'score': float, 'reason': str}``.
    :rtype: dict
    """
    if not text:
        return {'pass': True, 'score': 0.0, 'reason': 'empty'}
    freq: Dict[str, int] = {}
    for ch in text.lower():
        if ch.isalpha():
            freq[ch] = freq.get(ch, 0) + 1
    if len(freq) < 3:
        return {'pass': True, 'score': 0.0, 'reason': 'sparse'}
    total   = sum(freq.values())
    probs   = sorted([v / total for v in freq.values()], reverse=True)
    C       = probs[0]
    msd     = sum((probs[k] - C / (k + 1)) ** 2 for k in range(len(probs))) / len(probs)
    score   = math.sqrt(msd)
    _INJECT = [r'ignore previous', r'disregard', r'you are now', r'act as',
               r'jailbreak', r'DAN mode', r'<\|system\|>', r'<<<',
               r'\[INST\]', r'###\s*System']
    for pat in _INJECT:
        if re.search(pat, text, re.IGNORECASE):
            return {'pass': False, 'score': 1.0, 'reason': f'injection:{pat[:30]}'}
    passed = score < threshold
    return {'pass': passed, 'score': round(score, 6),
            'reason': 'ok' if passed else 'cepstrum deviation'}


# ── SearchContext ─────────────────────────────────────────────────────────────

class SearchContext:
    """
    Live semantic search feeding directly into Ptolemy's field.

    All fetches pass the P5 cepstrum gate. Passing content flows:
    gate → MindEye.see(8-vector) → hear() → condensation candidate.

    Four backends (all use stdlib urllib — no extra dependencies):

    * **arXiv** — preprints via ``export.arxiv.org/api/query``
    * **Wikipedia** — REST summary via ``en.wikipedia.org/api/rest_v1``
    * **Semantic Scholar** — paper search via ``api.semanticscholar.org``
    * **LMFDB** — Riemann zero data via ``www.lmfdb.org/api/zeros/zeta``

    :param engine: Live ``Engine`` instance.
    :param opener: urllib opener (standard or custom UA).

    :Example:

    .. code-block:: python

        sc = engine.get_search_context()
        result = sc.search_context('Riemann zeros LMFDB')
        print(result['heard'])
    """

    _ARXIV  = 'https://export.arxiv.org/api/query'
    _WIKI   = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
    _S2     = 'https://api.semanticscholar.org/graph/v1/paper/search'
    _LMFDB  = 'https://www.lmfdb.org/api/zeros/zeta'

    # Second 𝕆 channel assignments for search metadata
    # E8=spatial(source rank), E9=temporal(recency), E10=query resonance,
    # E11=abstract density, E12=citation weight, E13=field fingerprint,
    # E14=confidence, E15=callosum coupling
    _E8  = 8; _E9  = 9; _E10 = 10; _E11 = 11
    _E12 = 12; _E13 = 13; _E14 = 14; _E15 = 15

    def __init__(self, engine, opener=None):
        self._engine = engine
        self._opener = opener or urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler())
        self._opener.addheaders = [
            ('User-Agent', 'Ptolemy/2.8 (+https://github.com/michaelrendier/PtolemyHolcus)')]

    # ── internal helpers ──────────────────────────────────────────────────────

    def _fetch(self, url: str, timeout: int = 12) -> Optional[str]:
        """Fetch URL, return text or None on error."""
        try:
            resp = self._opener.open(url, timeout=timeout)
            return resp.read().decode('utf-8', errors='ignore')
        except Exception:
            return None

    def _gate_and_ingest(self, text: str, meta_vec: List[float],
                         label: str = '') -> Dict[str, Any]:
        """
        Run P5 gate, encode into MindEye, hear. Returns result dict.

        :param text: Text to evaluate and ingest.
        :param meta_vec: 8-float vector for second 𝕆 (e₈..e₁₅).
        :param label: Source label for MindEye snapshot.
        :returns: Dict with keys ``gate``, ``heard``, ``callosum``.
        :rtype: dict
        """
        gate = _cepstrum_gate(text)
        if not gate['pass']:
            return {'gate': gate, 'heard': '', 'callosum': 0.0}
        me   = self._engine.get_mind_eye()
        seen = me.see(meta_vec, label=label)
        # hear the first 512 chars — enough for condensation seed
        heard = ''
        try:
            heard = self._engine.hear(text[:512])
        except Exception:
            pass
        return {'gate': gate, 'heard': heard,
                'callosum': seen.get('callosum', 0.0)}

    # ── arXiv ─────────────────────────────────────────────────────────────────

    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search arXiv preprints. Results gate → MindEye → hear.

        :param query: Free-text query (e.g. ``'Riemann hypothesis zeros'``).
        :param max_results: Number of results to fetch.
        :returns: List of result dicts with keys ``title``, ``summary``,
            ``authors``, ``id``, ``gate``, ``heard``, ``callosum``.
        :rtype: list
        """
        params = urllib.parse.urlencode({
            'search_query': f'all:{query}',
            'start':        0,
            'max_results':  max_results,
        })
        raw = self._fetch(f'{self._ARXIV}?{params}')
        if not raw:
            return []

        results = []
        # Parse Atom XML with stdlib (no lxml/ElementTree import — pure string scan)
        entries = raw.split('<entry>')[1:]
        for i, entry in enumerate(entries[:max_results]):
            def _tag(t: str) -> str:
                m = re.search(rf'<{t}[^>]*>(.*?)</{t}>', entry, re.DOTALL)
                return (m.group(1) if m else '').strip()
            title    = _tag('title').replace('\n', ' ')
            summary  = _tag('summary').replace('\n', ' ')[:600]
            arxiv_id = _tag('id').split('/')[-1]
            authors  = re.findall(r'<name>(.*?)</name>', entry)

            # Encode: source rank, recency proxy, query resonance, abstract density
            n_words  = len(summary.split())
            n_auth   = min(len(authors) / 10.0, 1.0)
            meta = [float(max_results - i) / max_results,  # E8 source rank
                    0.9,                                     # E9 recency (arXiv = current)
                    min(n_words / 200.0, 1.0),               # E10 query resonance
                    min(n_words / 150.0, 1.0),               # E11 abstract density
                    n_auth,                                   # E12 citation proxy
                    float(hash(arxiv_id) % 1000) / 1000.0,  # E13 field fingerprint
                    0.85,                                     # E14 confidence
                    0.0,                                      # E15 computed by MindEye
                    ]
            ingest = self._gate_and_ingest(title + ' ' + summary, meta,
                                           label=f'arxiv:{arxiv_id}')
            results.append({'title': title, 'summary': summary,
                            'authors': authors, 'id': arxiv_id, **ingest})
        return results

    # ── Wikipedia ─────────────────────────────────────────────────────────────

    def search_wiki(self, query: str) -> Dict[str, Any]:
        """
        Fetch Wikipedia page summary. Gate → MindEye → hear.

        :param query: Page title or search term.
        :returns: Result dict with keys ``title``, ``extract``, ``page_id``,
            ``gate``, ``heard``, ``callosum``.
        :rtype: dict
        """
        slug = urllib.parse.quote(query.replace(' ', '_'))
        raw  = self._fetch(f'{self._WIKI}{slug}')
        if not raw:
            return {'title': '', 'extract': '', 'page_id': 0,
                    'gate': {'pass': False}, 'heard': '', 'callosum': 0.0}
        try:
            data = json.loads(raw)
        except Exception:
            return {'title': '', 'extract': '', 'page_id': 0,
                    'gate': {'pass': False}, 'heard': '', 'callosum': 0.0}

        title   = data.get('title', '')
        extract = data.get('extract', '')[:800]
        page_id = data.get('pageid', 0)
        n_words = len(extract.split())
        meta = [0.8,                                       # E8 source rank (wiki=reliable)
                0.5,                                       # E9 recency (encyclopaedic)
                min(n_words / 300.0, 1.0),                 # E10 resonance
                min(n_words / 200.0, 1.0),                 # E11 density
                0.7,                                       # E12 citation proxy
                float(page_id % 1000) / 1000.0,            # E13 fingerprint
                0.90,                                      # E14 confidence
                0.0,                                       # E15 callosum
                ]
        ingest = self._gate_and_ingest(title + ' ' + extract, meta,
                                       label=f'wiki:{page_id}')
        return {'title': title, 'extract': extract, 'page_id': page_id, **ingest}

    # ── Semantic Scholar ──────────────────────────────────────────────────────

    def search_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar Open API. Gate → MindEye → hear.

        :param query: Research query.
        :param limit: Maximum results.
        :returns: List of result dicts with keys ``title``, ``abstract``,
            ``year``, ``citations``, ``paper_id``, ``gate``, ``heard``, ``callosum``.
        :rtype: list
        """
        params = urllib.parse.urlencode({
            'query':  query,
            'limit':  limit,
            'fields': 'title,abstract,year,citationCount,paperId',
        })
        raw = self._fetch(f'{self._S2}?{params}')
        if not raw:
            return []
        try:
            data = json.loads(raw)
        except Exception:
            return []

        results = []
        for i, paper in enumerate(data.get('data', [])[:limit]):
            title     = paper.get('title', '')
            abstract  = (paper.get('abstract') or '')[:600]
            year      = paper.get('year', 2000) or 2000
            citations = paper.get('citationCount', 0) or 0
            paper_id  = paper.get('paperId', '')

            recency   = min((year - 1990) / 35.0, 1.0)
            cit_norm  = min(citations / 500.0, 1.0)
            n_words   = len(abstract.split())
            meta = [float(limit - i) / limit,              # E8 rank
                    recency,                                # E9 recency
                    min(n_words / 200.0, 1.0),             # E10 resonance
                    min(n_words / 150.0, 1.0),             # E11 density
                    cit_norm,                               # E12 citation weight
                    float(hash(paper_id) % 1000) / 1000.0, # E13 fingerprint
                    0.88,                                   # E14 confidence
                    0.0,                                    # E15 callosum
                    ]
            ingest = self._gate_and_ingest(title + ' ' + abstract, meta,
                                           label=f's2:{paper_id[:16]}')
            results.append({'title': title, 'abstract': abstract,
                            'year': year, 'citations': citations,
                            'paper_id': paper_id, **ingest})
        return results

    # ── LMFDB ────────────────────────────────────────────────────────────────

    def search_lmfdb(self, count: int = 20) -> Dict[str, Any]:
        """
        Fetch Riemann zeta zeros from LMFDB.

        Returns the first ``count`` non-trivial zero imaginary parts and
        encodes them directly as an energy vector into MindEye (e₈..e₁₅
        summed over the zero batch).

        :param count: Number of zeros to fetch.
        :returns: Dict with keys ``zeros``, ``heard``, ``callosum``.
        :rtype: dict
        """
        params = urllib.parse.urlencode({'limit': count, 'height': '0..100'})
        raw    = self._fetch(f'{self._LMFDB}?{params}', timeout=20)
        zeros: List[float] = []
        if raw:
            try:
                data  = json.loads(raw)
                items = data.get('data', data) if isinstance(data, dict) else data
                for item in items:
                    if isinstance(item, (int, float)):
                        zeros.append(float(item))
                    elif isinstance(item, dict):
                        v = item.get('Im') or item.get('height') or item.get('zero')
                        if v is not None:
                            zeros.append(float(v))
            except Exception:
                pass

        if not zeros:
            # Fallback: first 8 known zeros
            zeros = [14.1347, 21.0220, 25.0109, 30.4249,
                     32.9351, 37.5862, 40.9187, 43.3271]

        # Normalise 8 zeros into [0,1] range for MindEye
        top8  = zeros[:8]
        mx    = max(top8) if top8 else 1.0
        meta  = [z / mx for z in top8] + [0.0] * (8 - len(top8))
        me    = self._engine.get_mind_eye()
        seen  = me.see(meta[:8], label=f'lmfdb:zeros:{len(zeros)}')
        heard = ''
        try:
            summary = f'Riemann zeros: {" ".join(f"{z:.4f}" for z in zeros[:8])}'
            heard   = self._engine.hear(summary)
        except Exception:
            pass
        return {'zeros': zeros, 'heard': heard,
                'callosum': seen.get('callosum', 0.0), 'n': len(zeros)}

    # ── Combined context search ───────────────────────────────────────────────

    def search_context(self, query: str) -> Dict[str, Any]:
        """
        Combined context search: arXiv + Wikipedia + Semantic Scholar + LMFDB
        (LMFDB only when query contains ``'riemann'`` or ``'zero'``).

        Results are ranked by callosum coupling strength. The top result
        drives a final hear() call for field integration.

        This is the P2 search path:
        ``search_context(query) → gate → MindEye.see() → hear() → study()``.

        :param query: Natural language research query.
        :returns: Dict with keys ``arxiv``, ``wiki``, ``semantic``, ``lmfdb``,
            ``top``, ``heard``, ``callosum``.
        :rtype: dict
        """
        q_low   = query.lower()
        arxiv   = self.search_arxiv(query, max_results=3)
        wiki    = self.search_wiki(query)
        s2      = self.search_semantic(query, limit=3)
        lmfdb   = (self.search_lmfdb()
                   if any(k in q_low for k in ('riemann', 'zero', 'lmfdb', 'zeta'))
                   else {})

        # Rank all results by callosum strength
        candidates = [wiki] + arxiv + s2
        candidates.sort(key=lambda r: r.get('callosum', 0.0), reverse=True)
        top = candidates[0] if candidates else {}

        # Final integration hear on combined titles
        titles  = ' '.join(
            r.get('title', r.get('extract', ''))[:80] for r in candidates[:4])
        heard   = ''
        callosum = top.get('callosum', 0.0)
        try:
            heard = self._engine.hear(titles)
        except Exception:
            pass

        return {'arxiv': arxiv, 'wiki': wiki, 'semantic': s2,
                'lmfdb': lmfdb, 'top': top,
                'heard': heard, 'callosum': callosum}
