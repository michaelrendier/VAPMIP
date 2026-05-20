"""
skills/scholar.py — Academic, patent, and legal corpus acquisition.

:description:
    Routes around paywalls via Unpaywall → CORE → author preprint chain.
    Never hits a paywall directly. CiteMeta travels with every chunk and
    modifies field_health before the BAO adaptive threshold runs.

    APIs used (all free, no auth unless noted):
      Semantic Scholar  api.semanticscholar.org/graph/v1
      CrossRef          api.crossref.org/works/{doi}
      Unpaywall         api.unpaywall.org/v2/{doi}   (email required)
      OpenAlex          api.openalex.org/works
      arXiv             export.arxiv.org/api/query
      PubMed E-utils    eutils.ncbi.nlm.nih.gov
      USPTO Patents     developer.uspto.gov/ibd-api/v1
      CourtListener     courtlistener.com/api/rest/v3
      Harvard Caselaw   case.law/api/v1/cases
      SEP               plato.stanford.edu  (free, CC-BY)
      OCW MIT           ocw.mit.edu         (free, CC)

:classes:
    CiteMeta
    PtolScholar
"""

import json
import math
import time
import urllib.request
import urllib.parse
import urllib.error
import threading
from dataclasses import dataclass, field
from typing import Optional

# ── API roots ─────────────────────────────────────────────────────────────────
_SEMANTIC   = 'https://api.semanticscholar.org/graph/v1/paper/search'
_SEMANTIC_P = 'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
_CROSSREF   = 'https://api.crossref.org/works/{doi}'
_UNPAYWALL  = 'https://api.unpaywall.org/v2/{doi}?email={email}'
_OPENALEX   = 'https://api.openalex.org/works'
_ARXIV      = 'https://export.arxiv.org/api/query'
_PUBMED     = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
_USPTO      = 'https://developer.uspto.gov/ibd-api/v1/patent/application'
_COURTL     = 'https://www.courtlistener.com/api/rest/v3/search/'
_CASELAW    = 'https://api.case.law/v1/cases/'
_SEP_INDEX  = 'https://plato.stanford.edu/entries/'
_OCW_SEARCH = 'https://ocw.mit.edu/search/'

# OCW course prefix → domain bin
OCW_DOMAIN_MAP = {
    '1':  'monad_civil_eng.bin',    '2':  'monad_mech_eng.bin',
    '3':  'monad_materials.bin',    '5':  'monad_chemistry.bin',
    '6':  'monad_cs_ee.bin',        '7':  'monad_biology.bin',
    '8':  'monad_physics.bin',      '9':  'monad_brain.bin',
    '10': 'monad_chem_eng.bin',     '14': 'monad_econ.bin',
    '18': 'monad_math.bin',         '21': 'monad_humanities.bin',
    '22': 'monad_nuclear.bin',      '24': 'monad_linguistics.bin',
    'STS': 'monad_science_soc.bin',
}

# Known good SEP entries for English acquisition boot
SEP_SEED_ENTRIES = [
    'knowledge-analysis', 'truth', 'meaning', 'reference', 'consciousness',
    'logic-classical', 'set-theory', 'computability', 'information',
    'causation', 'time', 'space', 'identity', 'existence', 'probability',
    'induction-problem', 'scientific-explanation', 'reduction-biology',
    'mathematics-philosophy', 'language-thought',
]


@dataclass
class CiteMeta:
    """
    Epistemological metadata attached to every ingested chunk.

    :param source_type: One of peer_reviewed|preprint|patent|case_law|
                        dataset|class_level|expert_edited|wiki|web.
    :param sigma: Statistical confidence (0-5). 5 = physics discovery threshold.
    :param n_samples: Sample/study size. -1 if not applicable.
    :param citation_count: Times cited. 0 for new/preprint.
    :param retracted: True if retraction watch flagged.
    :param replicated: True if independent replication confirmed.
    :param journal_quartile: Q1-Q4. None for non-journal sources.
    :param doi: DOI string if available.
    :param url: Source URL.
    :param domain_bin: Target domain bin override. None = monad.bin.
    """
    source_type:     str            = 'web'
    sigma:           float          = 1.0
    n_samples:       int            = -1
    citation_count:  int            = 0
    retracted:       bool           = False
    replicated:      bool           = False
    journal_quartile: Optional[int] = None
    doi:             Optional[str]  = None
    url:             str            = ''
    domain_bin:      Optional[str]  = None

    def weight(self) -> float:
        """
        Compute cite weight [0,1] for field_health scaling.

        :returns: Weight scalar.
        :rtype: float
        """
        if self.retracted:
            return 0.0
        sigma_w = min(1.0, self.sigma / 5.0)
        n_w     = min(1.0, math.log1p(max(self.n_samples, 0)) / 12.0) \
                  if self.n_samples > 0 else 0.3
        cit_w   = min(1.0, math.log1p(self.citation_count) / 8.0)
        base    = sigma_w * 0.5 + n_w * 0.3 + cit_w * 0.2
        mult = {
            'peer_reviewed': 1.00,
            'expert_edited': 0.85,
            'class_level':   0.70,
            'preprint':      0.65,
            'patent':        0.60,
            'case_law':      0.55,
            'dataset':       0.50,
            'wiki':          0.40,
            'web':           0.25,
        }.get(self.source_type, 0.30)
        return min(1.0, base * mult / 0.5)  # normalise so peer_reviewed σ=5 → 1.0

    @staticmethod
    def default_for(source_type: str) -> 'CiteMeta':
        """
        Factory for common source types.

        :param source_type: Source type string.
        :returns: CiteMeta with sensible defaults.
        :rtype: CiteMeta
        """
        defaults = {
            'peer_reviewed': CiteMeta(source_type='peer_reviewed', sigma=3.5),
            'preprint':      CiteMeta(source_type='preprint',      sigma=2.2),
            'class_level':   CiteMeta(source_type='class_level',   sigma=2.0),
            'expert_edited': CiteMeta(source_type='expert_edited',  sigma=2.5),
            'patent':        CiteMeta(source_type='patent',         sigma=2.0),
            'case_law':      CiteMeta(source_type='case_law',       sigma=2.0),
            'wiki':          CiteMeta(source_type='wiki',           sigma=1.5),
            'web':           CiteMeta(source_type='web',            sigma=0.8),
        }
        return defaults.get(source_type, CiteMeta())


class PtolScholar:
    """
    Academic, patent, and legal corpus acquisition.
    Routes around paywalls. Never scrapes JSTOR directly.

    :param opener: urllib opener with Mozilla UA.
    :param logger: PtolLogger instance.
    :param search: PtolSearch instance (queue target).
    :param config: PtolConfig instance.
    """

    def __init__(self, opener, logger, search, config):
        self._opener = opener
        self._logger = logger
        self._search = search
        self._config = config
        self._lock   = threading.Lock()
        self._email  = config.get('scholar_email', 'ptolemy@localhost')
        self._rate   = {}  # host → last_request_time (rate limiting)

    def _throttle(self, host: str, min_gap: float = 1.0):
        """Polite rate limit per host."""
        with self._lock:
            last = self._rate.get(host, 0.0)
            gap  = time.time() - last
            if gap < min_gap:
                time.sleep(min_gap - gap)
            self._rate[host] = time.time()

    def _get_json(self, url: str, timeout: int = 20) -> Optional[dict]:
        """Fetch URL and parse JSON. Returns None on failure."""
        parsed = urllib.parse.urlparse(url)
        self._throttle(parsed.netloc)
        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent',
                           'Ptolemy/1.0 (academic; mailto:ptolemy@localhost)')
            resp = urllib.request.urlopen(req, timeout=timeout)
            return json.loads(resp.read().decode('utf-8', errors='ignore'))
        except Exception as exc:
            self._logger.skip(url, f"scholar_json:{exc}")
            return None

    def _get_text(self, url: str, timeout: int = 30) -> Optional[str]:
        """Fetch URL and return raw text. Returns None on failure."""
        parsed = urllib.parse.urlparse(url)
        self._throttle(parsed.netloc, min_gap=1.5)
        try:
            resp = self._opener.open(url, timeout=timeout)
            return resp.read().decode('utf-8', errors='ignore')
        except Exception as exc:
            self._logger.skip(url, f"scholar_text:{exc}")
            return None

    # ── Semantic Scholar ──────────────────────────────────────────────────

    def search_papers(self, query: str, limit: int = 20) -> list:
        """
        Keyword search via Semantic Scholar.

        :param query: Search terms.
        :param limit: Max results.
        :returns: List of paper dicts with title, doi, citationCount, year, openAccessPdf.
        :rtype: list
        """
        params = urllib.parse.urlencode({
            'query':  query,
            'limit':  min(limit, 100),
            'fields': 'title,externalIds,citationCount,year,openAccessPdf,publicationTypes',
        })
        data = self._get_json(f"{_SEMANTIC}?{params}")
        if not data:
            return []
        results = []
        for p in data.get('data', []):
            eids = p.get('externalIds', {})
            results.append({
                'title':          p.get('title', ''),
                'doi':            eids.get('DOI', ''),
                'arxiv':          eids.get('ArXiv', ''),
                'citation_count': p.get('citationCount', 0),
                'year':           p.get('year', 0),
                'open_pdf':       (p.get('openAccessPdf') or {}).get('url', ''),
                'pub_types':      p.get('publicationTypes', []),
            })
        return results

    # ── CrossRef DOI resolution ───────────────────────────────────────────

    def resolve_doi(self, doi: str) -> CiteMeta:
        """
        Resolve DOI via CrossRef → CiteMeta with journal quartile approximation.

        :param doi: DOI string (with or without https://doi.org/ prefix).
        :returns: CiteMeta populated from CrossRef metadata.
        :rtype: CiteMeta
        """
        doi = doi.replace('https://doi.org/', '').strip()
        url = _CROSSREF.format(doi=urllib.parse.quote(doi, safe=''))
        data = self._get_json(url)
        if not data:
            return CiteMeta(doi=doi)
        msg  = data.get('message', {})
        refs = len(msg.get('reference', []))
        cits = msg.get('is-referenced-by-count', 0)
        types_map = {
            'journal-article':    ('peer_reviewed', 3.5),
            'book-chapter':       ('expert_edited',  2.5),
            'proceedings-article':('preprint',        2.0),
            'dissertation':       ('preprint',        2.0),
            'report':             ('class_level',     1.5),
            'posted-content':     ('preprint',        2.0),
        }
        src_type, sigma = types_map.get(msg.get('type', ''), ('web', 1.0))
        return CiteMeta(
            source_type=src_type,
            sigma=sigma,
            citation_count=cits,
            doi=doi,
        )

    # ── Unpaywall ─────────────────────────────────────────────────────────

    def open_pdf(self, doi: str) -> Optional[str]:
        """
        Find legal open-access PDF via Unpaywall.

        :param doi: DOI string.
        :returns: Open-access PDF URL or None.
        :rtype: str or None
        """
        doi = doi.replace('https://doi.org/', '').strip()
        url = _UNPAYWALL.format(
            doi=urllib.parse.quote(doi, safe=''),
            email=self._email,
        )
        data = self._get_json(url)
        if not data or not data.get('is_oa'):
            return None
        best = data.get('best_oa_location') or {}
        return best.get('url_for_pdf') or best.get('url')

    # ── arXiv ─────────────────────────────────────────────────────────────

    def search_arxiv(self, query: str, max_results: int = 20) -> list:
        """
        Search arXiv preprint server.

        :param query: Search terms.
        :param max_results: Max papers to return.
        :returns: List of dicts with title, pdf_url, arxiv_id, summary.
        :rtype: list
        """
        params = urllib.parse.urlencode({
            'search_query': f'all:{query}',
            'max_results':  max_results,
            'sortBy':       'relevance',
        })
        text = self._get_text(f"{_ARXIV}?{params}")
        if not text:
            return []
        import xml.etree.ElementTree as ET
        ns   = 'http://www.w3.org/2005/Atom'
        results = []
        try:
            root = ET.fromstring(text)
            for entry in root.findall(f'{{{ns}}}entry'):
                arxiv_id = entry.find(f'{{{ns}}}id')
                title    = entry.find(f'{{{ns}}}title')
                summary  = entry.find(f'{{{ns}}}summary')
                links    = entry.findall(f'{{{ns}}}link')
                pdf_url  = next(
                    (l.get('href') for l in links if l.get('title') == 'pdf'),
                    None)
                if arxiv_id is not None and pdf_url:
                    results.append({
                        'arxiv_id': arxiv_id.text,
                        'title':    (title.text or '').strip(),
                        'summary':  (summary.text or '').strip(),
                        'pdf_url':  pdf_url,
                    })
        except Exception:
            pass
        return results

    # ── SEP — Stanford Encyclopedia of Philosophy ─────────────────────────

    def fetch_sep(self, entry: str) -> Optional[tuple]:
        """
        Fetch SEP article. Returns (text, bibliography_dois, CiteMeta).
        Strips navigation boilerplate — preamble and section text only.

        :param entry: SEP entry slug (e.g. 'knowledge-analysis').
        :returns: (plain_text, doi_list, CiteMeta) or None on failure.
        :rtype: tuple or None
        """
        url  = f"{_SEP_INDEX}{entry}/"
        html = self._get_text(url)
        if not html:
            return None

        # Strip HTML to text
        try:
            import html2text as h2t
            converter = h2t.HTML2Text()
            converter.ignore_links  = False
            converter.ignore_images = True
            converter.body_width    = 0
            text = converter.handle(html)
        except ImportError:
            import re
            text = re.sub(r'<[^>]+>', ' ', html)

        # Extract DOIs from bibliography links
        import re
        dois = re.findall(r'doi\.org/(10\.[^\s\)"\']+)', html)
        dois = list(dict.fromkeys(dois))  # deduplicate

        meta = CiteMeta(
            source_type='expert_edited',
            sigma=2.5,
            citation_count=0,
            url=url,
            domain_bin=None,  # SEP → monad.bin (speaking)
        )
        return text, dois, meta

    def seed_sep(self, entries: list = None):
        """
        Enqueue SEP articles into search queue with CiteMeta.

        :param entries: List of SEP slugs. Defaults to SEP_SEED_ENTRIES.
        """
        for slug in (entries or SEP_SEED_ENTRIES):
            url = f"ptol+sep://{slug}"
            self._search.add_url(url, CiteMeta.default_for('expert_edited'))

    # ── OCW MIT ───────────────────────────────────────────────────────────

    def seed_ocw(self, departments: list = None):
        """
        Enqueue OCW course lecture notes by department code.

        :param departments: List of dept codes ('8', '18', '24', etc.).
                            Defaults to physics, math, linguistics, CS, brain.
        """
        depts = departments or ['8', '18', '24', '6', '9']
        for dept in depts:
            domain_bin = OCW_DOMAIN_MAP.get(dept, 'monad.bin')
            url = f"ptol+ocw://{dept}"
            self._search.add_url(url, CiteMeta(
                source_type='class_level',
                sigma=2.0,
                domain_bin=domain_bin,
            ))

    # ── USPTO Patents ─────────────────────────────────────────────────────

    def search_patents(self, query: str, rows: int = 20) -> list:
        """
        Search USPTO full-text patent database.

        :param query: Search terms.
        :param rows: Max results.
        :returns: List of patent metadata dicts.
        :rtype: list
        """
        params = urllib.parse.urlencode({
            'searchText': query,
            'start':      0,
            'rows':       rows,
            'output':     'application/json',
        })
        data = self._get_json(f"{_USPTO}?{params}")
        if not data:
            return []
        results = []
        for p in data.get('response', {}).get('docs', []):
            results.append({
                'patent_number': p.get('patentNumber', ''),
                'title':         p.get('inventionTitle', ''),
                'abstract':      p.get('patentAbstract', ''),
                'date':          p.get('patentIssuedDateString', ''),
                'assignee':      p.get('assigneeEntityName', ''),
            })
        return results

    # ── CourtListener case law ────────────────────────────────────────────

    def search_caselaw(self, query: str, jurisdiction: str = '',
                       limit: int = 20) -> list:
        """
        Search CourtListener for US case law.

        :param query: Search terms.
        :param jurisdiction: Court jurisdiction filter (optional).
        :param limit: Max results.
        :returns: List of case dicts.
        :rtype: list
        """
        params: dict = {'q': query, 'type': 'o', 'format': 'json'}
        if jurisdiction:
            params['court'] = jurisdiction
        url  = _COURTL + '?' + urllib.parse.urlencode(params)
        data = self._get_json(url)
        if not data:
            return []
        results = []
        for r in data.get('results', [])[:limit]:
            results.append({
                'case_name':    r.get('caseName', ''),
                'date_filed':   r.get('dateFiled', ''),
                'court':        r.get('court', ''),
                'url':          r.get('absolute_url', ''),
                'snippet':      r.get('snippet', ''),
            })
        return results

    # ── Full pipeline: find → open → queue ───────────────────────────────

    def seed_scholar(self, query: str, limit: int = 10):
        """
        Search Semantic Scholar, find open PDFs, enqueue into search queue.

        :param query: Academic search query.
        :param limit: Max papers to enqueue.
        """
        papers = self.search_papers(query, limit=limit * 2)
        queued = 0
        for p in papers:
            if queued >= limit:
                break
            pdf_url = p.get('open_pdf', '')
            if not pdf_url and p.get('doi'):
                pdf_url = self.open_pdf(p['doi'])
            if not pdf_url and p.get('arxiv'):
                pdf_url = f"https://arxiv.org/pdf/{p['arxiv']}.pdf"
            if pdf_url:
                pub_types = p.get('pub_types', [])
                src_type  = ('peer_reviewed'
                             if 'JournalArticle' in pub_types
                             else 'preprint')
                meta = CiteMeta(
                    source_type=src_type,
                    sigma=3.5 if src_type == 'peer_reviewed' else 2.2,
                    citation_count=p.get('citation_count', 0),
                    doi=p.get('doi', ''),
                    url=pdf_url,
                )
                self._search.add_url(pdf_url, meta)
                queued += 1

    def seed_arxiv(self, query: str, max_results: int = 10):
        """
        Search arXiv and enqueue open PDFs.

        :param query: Search terms.
        :param max_results: Max papers.
        """
        papers = self.search_arxiv(query, max_results=max_results)
        for p in papers:
            if p.get('pdf_url'):
                self._search.add_url(
                    p['pdf_url'],
                    CiteMeta(source_type='preprint', sigma=2.2,
                             url=p['pdf_url']),
                )
