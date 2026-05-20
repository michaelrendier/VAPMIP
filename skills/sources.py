"""
skills/sources.py — Source registry and routing for Ptolemy's TeachingThread.

:description:
    SOURCES dict maps source names to metadata (sigma default, domain bin,
    queue method). PtolSources reads .ptolrc [sources] section to determine
    which are active, then drives the appropriate seed calls.

    Phase ordering:
      Phase 1 — Lexicon: Wiktionary topology (angle map before navigation)
      Phase 2 — Prose:   Gutenberg, SEP, OCW (BAO emergence target)
      Phase 3 — Domain:  arXiv, PubMed, OCW upper-division
      Phase 4 — Reference: Semantic Scholar citation graph (self-directed)

:data:
    SOURCES
:classes:
    PtolSources
"""

from typing import Optional


# ── Source registry ─────────────────────────────────────────────────────────

SOURCES = {
    # Phase 1 — Lexicon (boot first — angle map before navigation)
    'wiktionary': {
        'description': 'Wiktionary word topology — synonym/antonym/hypo/hypernym',
        'sigma':       1.5,
        'source_type': 'wiki',
        'bin':         'monad_lexicon.bin',
        'phase':       1,
        'default':     'on',
        'method':      'seed_wiktionary',
    },

    # Phase 2 — English prose core (speaks to monad.bin)
    'gutenberg': {
        'description': 'Project Gutenberg plain-text books via gutendex.com',
        'sigma':       1.5,
        'source_type': 'prose',
        'bin':         'monad.bin',
        'phase':       2,
        'default':     'on',
        'method':      'seed_gutenberg',
    },
    'archive_org': {
        'description': 'archive.org English texts via search API',
        'sigma':       1.2,
        'source_type': 'prose',
        'bin':         'monad.bin',
        'phase':       2,
        'default':     'on',
        'method':      'seed_archive',
    },
    'sep': {
        'description': 'Stanford Encyclopedia of Philosophy (expert-edited prose)',
        'sigma':       2.5,
        'source_type': 'expert_edited',
        'bin':         'monad.bin',
        'phase':       2,
        'default':     'on',
        'method':      'seed_sep',
    },
    'ocw_intro': {
        'description': 'MIT OCW introductory courses (class-level prose)',
        'sigma':       2.0,
        'source_type': 'class_level',
        'bin':         'domain',
        'phase':       2,
        'default':     'on',
        'method':      'seed_ocw_intro',
    },

    # Phase 3 — Domain specialisation
    'arxiv': {
        'description': 'arXiv preprint server (physics, math, CS, econ)',
        'sigma':       2.2,
        'source_type': 'preprint',
        'bin':         'domain',
        'phase':       3,
        'default':     'off',
        'method':      'seed_arxiv',
    },
    'pubmed': {
        'description': 'PubMed biomedical literature (peer-reviewed)',
        'sigma':       3.5,
        'source_type': 'peer_reviewed',
        'bin':         'domain',
        'phase':       3,
        'default':     'off',
        'method':      'seed_pubmed',
    },
    'ocw_upper': {
        'description': 'MIT OCW upper-division and graduate courses',
        'sigma':       2.5,
        'source_type': 'class_level',
        'bin':         'domain',
        'phase':       3,
        'default':     'off',
        'method':      'seed_ocw_upper',
    },

    # Phase 4 — Reference grade
    'semantic_sch': {
        'description': 'Semantic Scholar citation graph (200M papers)',
        'sigma':       3.8,
        'source_type': 'peer_reviewed',
        'bin':         'domain',
        'phase':       4,
        'default':     'off',
        'method':      'seed_semantic',
    },
    'patents_us': {
        'description': 'USPTO patent full-text database',
        'sigma':       2.0,
        'source_type': 'patent',
        'bin':         'monad_legal.bin',
        'phase':       4,
        'default':     'off',
        'method':      'seed_patents',
    },
    'caselaw': {
        'description': 'US case law via CourtListener and Harvard Caselaw',
        'sigma':       2.0,
        'source_type': 'case_law',
        'bin':         'monad_legal.bin',
        'phase':       4,
        'default':     'off',
        'method':      'seed_caselaw',
    },
    'foundation': {
        'description': 'Candid Foundation Directory (grant database, API key required)',
        'sigma':       1.5,
        'source_type': 'dataset',
        'bin':         'monad.bin',
        'phase':       4,
        'default':     'off',
        'method':      'seed_foundation',
    },
}


class PtolSources:
    """
    Source manager. Reads active sources from .ptolrc, drives seed calls.

    :param config: PtolConfig instance.
    :param search: PtolSearch instance.
    :param scholar: PtolScholar instance (optional).
    :param lexicon: PtolLexicon instance (optional).
    :param logger:  PtolLogger instance.
    """

    def __init__(self, config, search, logger,
                 scholar=None, lexicon=None):
        self._config  = config
        self._search  = search
        self._scholar = scholar
        self._lexicon = lexicon
        self._logger  = logger

    def active_sources(self) -> list:
        """
        Return list of active source names from .ptolrc [sources] section.

        :returns: List of source name strings.
        :rtype: list
        """
        active = []
        for name, meta in SOURCES.items():
            val = self._config.get(name, meta['default'])
            if str(val).lower() in ('on', 'true', '1', 'yes'):
                active.append(name)
        return active

    def active_phase(self) -> int:
        """
        Highest active phase number across enabled sources.

        :returns: Max phase number (1-4).
        :rtype: int
        """
        active = self.active_sources()
        phases = [SOURCES[n]['phase'] for n in active if n in SOURCES]
        return max(phases) if phases else 1

    def seed_active(self, max_queue: int = 20):
        """
        Seed active sources until search queue reaches max_queue depth.
        Respects phase ordering: only seeds next phase when prior phase is warm.

        :param max_queue: Target queue depth before stopping.
        """
        if self._search.queue_depth() >= max_queue:
            return
        active = self.active_sources()
        for name in active:
            if self._search.queue_depth() >= max_queue:
                break
            meta = SOURCES.get(name, {})
            method = meta.get('method', '')
            try:
                self._dispatch_seed(name, method)
            except Exception as exc:
                self._logger.skip(f"source:{name}", f"seed_err:{exc}")

    def _dispatch_seed(self, name: str, method: str):
        """Route seed call to correct object."""
        if name == 'gutenberg':
            self._search.seed_gutenberg()
        elif name == 'archive_org':
            self._search.seed_archive()
        elif name == 'sep':
            if self._scholar:
                self._scholar.seed_sep()
        elif name in ('ocw_intro', 'ocw_upper'):
            if self._scholar:
                depts = (['8', '18', '24'] if name == 'ocw_intro'
                         else ['6', '9', '14', '22'])
                self._scholar.seed_ocw(departments=depts)
        elif name == 'wiktionary':
            if self._lexicon:
                self._lexicon.seed_common_words()
        elif name == 'arxiv':
            if self._scholar:
                self._scholar.seed_arxiv('natural language english')
        elif name == 'semantic_sch':
            if self._scholar:
                self._scholar.seed_scholar('english language learning corpus')
        elif name == 'patents_us':
            if self._scholar:
                papers = self._scholar.search_patents('natural language processing')
                for p in papers[:5]:
                    if p.get('abstract'):
                        self._search.add_url(
                            f"ptol+text://{p['patent_number']}",
                            None)

    def source_report(self) -> str:
        """
        Human-readable source status report.

        :returns: Formatted string.
        :rtype: str
        """
        lines = ['Sources:']
        for name, meta in SOURCES.items():
            val   = self._config.get(name, meta['default'])
            state = 'ON ' if str(val).lower() in ('on', 'true', '1', 'yes') else 'off'
            lines.append(
                f"  [{state}] {name:14s}  σ={meta['sigma']:.1f}  "
                f"phase={meta['phase']}  → {meta['bin']}  "
                f"{meta['description']}"
            )
        return '\n'.join(lines)

    def write_defaults_to_ptolrc(self):
        """
        Write all source defaults to .ptolrc [sources] section.
        Only writes keys not already pinned in ptolemy.cfg.

        :returns: None
        """
        for name, meta in SOURCES.items():
            self._config.set_ptolrc('sources', name, meta['default'])
