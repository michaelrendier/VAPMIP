"""
skills/lexicon.py — Vocabulary topology via Wiktionary and Wikithesaurus.

:description:
    Wiktionary is not a dictionary. It is the geometry of the vocabulary space.

    Co-occurrence learning (Gutenberg) teaches that "ship" and "sea" appear near each other.
    Wiktionary teaches that "ship" and "vessel" are the SAME REGION (synonyms = same
    angular position in semantic space), that "boat" is a hyponym (nested inside "ship"),
    that "transportation" is a hypernym ("ship" is a rotation of "transportation").

    This is topology, not statistics. The synonym cluster is the sedenion's calibration
    dataset: angle map without requiring co-occurrence inference.

    Two modes:
      batch  — seed from top-N common English words (boot phase)
      demand — triggered by gap.log word misses (targeted acquisition)

    Output: monad_lexicon.bin accumulates word topology.
    The gap logger feeds back into demand mode automatically.

:classes:
    PtolLexicon
"""

import json
import time
import threading
import urllib.request
import urllib.parse
import re
from typing import Optional

_WIKT_API  = 'https://en.wiktionary.org/w/api.php'
_THES_PAGE = 'Thesaurus:{word}'

# Top 100 English content words for batch seeding (stripped of function words)
COMMON_WORDS_SEED = [
    'time', 'year', 'people', 'way', 'day', 'man', 'woman', 'child',
    'world', 'life', 'hand', 'part', 'place', 'case', 'week', 'company',
    'system', 'program', 'question', 'work', 'government', 'number',
    'night', 'point', 'city', 'play', 'water', 'country', 'money',
    'story', 'fact', 'month', 'lot', 'right', 'study', 'book', 'eye',
    'job', 'word', 'business', 'issue', 'side', 'kind', 'head', 'house',
    'service', 'friend', 'father', 'power', 'hour', 'game', 'line',
    'end', 'among', 'state', 'family', 'student', 'group', 'body',
    'music', 'color', 'stand', 'sun', 'nature', 'force', 'measure',
    'social', 'image', 'change', 'lead', 'view', 'love', 'feel', 'form',
    'rise', 'fall', 'walk', 'grow', 'hold', 'turn', 'start', 'hand',
    'live', 'move', 'believe', 'create', 'develop', 'increase', 'reduce',
    'include', 'continue', 'provide', 'remain', 'suggest', 'follow',
    'allow', 'understand', 'begin', 'consider', 'receive', 'prevent',
    'appear', 'become', 'control', 'produce', 'result', 'support',
]


class PtolLexicon:
    """
    Word topology acquisition from Wiktionary and Wikithesaurus.

    :param opener: urllib opener with Mozilla UA.
    :param logger: PtolLogger instance.
    :param config: PtolConfig instance.
    :param search: PtolSearch instance (queue target for demand mode).
    """

    def __init__(self, opener, logger, config, search=None):
        self._opener  = opener
        self._logger  = logger
        self._config  = config
        self._search  = search
        self._lock    = threading.Lock()
        self._cache   = {}   # word → topology dict (session cache)
        self._rate    = 0.0  # last request time

    def _throttle(self):
        """Wiktionary asks for ≥ 1 request/second politeness."""
        with self._lock:
            gap = time.time() - self._rate
            if gap < 1.2:
                time.sleep(1.2 - gap)
            self._rate = time.time()

    def _wiki_parse(self, page: str, prop: str = 'wikitext') -> Optional[str]:
        """
        Fetch MediaWiki parse API for a page.

        :param page: Page title.
        :param prop: Property to fetch (wikitext, sections).
        :returns: Raw wikitext string or None.
        :rtype: str or None
        """
        self._throttle()
        params = urllib.parse.urlencode({
            'action': 'parse',
            'page':   page,
            'prop':   prop,
            'format': 'json',
        })
        url = f"{_WIKT_API}?{params}"
        try:
            req  = urllib.request.Request(
                url, headers={'User-Agent': 'Ptolemy/1.0 (lexicon; ptol+lex)'}
            )
            resp = self._opener.open(req, timeout=15)
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            if 'error' in data:
                return None
            return data.get('parse', {}).get('wikitext', {}).get('*', '')
        except Exception as exc:
            self._logger.skip(url, f"lex:{exc}")
            return None

    # ── Core word metadata ─────────────────────────────────────────────────

    def fetch_word_meta(self, word: str) -> Optional[dict]:
        """
        Fetch etymology, part-of-speech, definitions, and usage examples
        from Wiktionary for a single word.

        :param word: English word.
        :returns: Dict with keys: word, pos, etymology, definitions, examples.
        :rtype: dict or None
        """
        if word in self._cache:
            return self._cache[word]

        wikitext = self._wiki_parse(word)
        if not wikitext:
            return None

        result = {
            'word':       word,
            'pos':        self._extract_pos(wikitext),
            'etymology':  self._extract_etymology(wikitext),
            'definitions': self._extract_definitions(wikitext),
            'examples':   self._extract_examples(wikitext),
        }
        with self._lock:
            self._cache[word] = result
        return result

    def _extract_pos(self, wikitext: str) -> list:
        """Extract part-of-speech headers."""
        pos_tags = ['Noun', 'Verb', 'Adjective', 'Adverb', 'Pronoun',
                    'Preposition', 'Conjunction', 'Interjection', 'Determiner']
        found = []
        for pos in pos_tags:
            if f'=={pos}==' in wikitext or f'==={pos}===' in wikitext:
                found.append(pos.lower())
        return found

    def _extract_etymology(self, wikitext: str) -> str:
        """Extract etymology section text."""
        match = re.search(
            r'==+Etymology[^=]*==+\n(.*?)(?=\n==|\Z)', wikitext,
            re.DOTALL)
        if not match:
            return ''
        raw = match.group(1).strip()
        raw = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', raw)
        raw = re.sub(r'\{\{[^}]+\}\}', '', raw)
        raw = re.sub(r"'{2,}", '', raw)
        return raw[:500].strip()

    def _extract_definitions(self, wikitext: str) -> list:
        """Extract numbered definitions (# lines)."""
        lines = wikitext.splitlines()
        defs  = []
        in_english = False
        for line in lines:
            if line.strip() == '==English==':
                in_english = True
                continue
            if in_english and line.startswith('==') and 'English' not in line:
                in_english = False
            if in_english and line.startswith('# ') and not line.startswith('#:'):
                d = line[2:].strip()
                d = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', d)
                d = re.sub(r'\{\{[^}]+\}\}', '', d)
                d = re.sub(r"'{2,}", '', d)
                d = d.strip()
                if d:
                    defs.append(d)
                if len(defs) >= 5:
                    break
        return defs

    def _extract_examples(self, wikitext: str) -> list:
        """Extract usage example lines (#: prefix)."""
        examples = []
        for line in wikitext.splitlines():
            if line.startswith('#: ') or line.startswith('#:: '):
                ex = line.lstrip('#: ').strip()
                ex = re.sub(r"'{2,}", '', ex)
                ex = re.sub(r'\[\[([^\]|]+\|)?([^\]]+)\]\]', r'\2', ex)
                if ex:
                    examples.append(ex)
                if len(examples) >= 3:
                    break
        return examples

    # ── Thesaurus / topology ───────────────────────────────────────────────

    def fetch_synonyms(self, word: str) -> dict:
        """
        Fetch synonym cluster from Wiktionary Thesaurus namespace.
        Returns semantic topology: synonyms, antonyms, hyponyms, hypernyms.

        :param word: English word.
        :returns: Dict with keys synonyms/antonyms/hyponyms/hypernyms (lists).
        :rtype: dict
        """
        page     = _THES_PAGE.format(word=word)
        wikitext = self._wiki_parse(page)
        if not wikitext:
            return {'synonyms': [], 'antonyms': [], 'hyponyms': [], 'hypernyms': []}

        return {
            'synonyms':  self._extract_relation(wikitext, 'Synonyms'),
            'antonyms':  self._extract_relation(wikitext, 'Antonyms'),
            'hyponyms':  self._extract_relation(wikitext, 'Hyponyms'),
            'hypernyms': self._extract_relation(wikitext, 'Hypernyms'),
        }

    def _extract_relation(self, wikitext: str, section: str) -> list:
        """Extract word list from a thesaurus section."""
        pattern = rf'====?{section}====?\n(.*?)(?=\n====?|\Z)'
        match   = re.search(pattern, wikitext, re.DOTALL)
        if not match:
            return []
        block = match.group(1)
        words = re.findall(r'\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]', block)
        words = [w.lower().strip() for w in words if w.strip()]
        return list(dict.fromkeys(words))[:20]

    # ── Topology as ingestion text ─────────────────────────────────────────

    def topology_text(self, word: str) -> Optional[str]:
        """
        Build a prose representation of word topology suitable for
        ingestion via monad.ingest(). This teaches the sedenion the
        ANGLE MAP — where synonyms sit relative to each other.

        Format: definition sentences + synonym/antonym statements.

        :param word: English word.
        :returns: Prose text for ingestion, or None.
        :rtype: str or None
        """
        meta = self.fetch_word_meta(word)
        syns = self.fetch_synonyms(word)

        lines = []
        if meta:
            pos = ' '.join(meta.get('pos', []))
            if pos:
                lines.append(f"{word} is a {pos}.")
            for d in meta.get('definitions', [])[:3]:
                if d:
                    lines.append(f"{word}: {d}.")
            for ex in meta.get('examples', [])[:2]:
                if ex:
                    lines.append(ex)
            etym = meta.get('etymology', '')
            if etym:
                lines.append(f"Etymology of {word}: {etym}")

        if syns.get('synonyms'):
            s = ', '.join(syns['synonyms'][:8])
            lines.append(f"{word} is similar to {s}.")
        if syns.get('antonyms'):
            a = ', '.join(syns['antonyms'][:4])
            lines.append(f"The opposite of {word} includes {a}.")
        if syns.get('hyponyms'):
            h = ', '.join(syns['hyponyms'][:6])
            lines.append(f"Types of {word} include {h}.")
        if syns.get('hypernyms'):
            hh = ', '.join(syns['hypernyms'][:4])
            lines.append(f"{word} is a kind of {hh}.")

        if not lines:
            return None
        return ' '.join(lines)

    # ── Batch seeding ──────────────────────────────────────────────────────

    def seed_common_words(self, words: list = None, demand: bool = False):
        """
        Enqueue topology acquisition for a word list.
        In demand mode, words are processed immediately (blocking).
        In batch mode, words are added to the search queue.

        :param words: Word list. Defaults to COMMON_WORDS_SEED.
        :param demand: If True, fetch and return topology immediately.
        :returns: List of topology dicts (demand mode only).
        :rtype: list
        """
        target = words or COMMON_WORDS_SEED
        if demand:
            results = []
            for w in target:
                text = self.topology_text(w)
                if text:
                    results.append({'word': w, 'text': text})
            return results
        # Batch: enqueue as ptol+lex:// URLs for TeachingThread
        for w in target:
            if self._search:
                self._search.add_url(f"ptol+lex://{w}")
        return []

    def demand_word(self, word: str) -> Optional[str]:
        """
        On-demand topology fetch triggered by gap.log miss.
        Returns prose text ready for monad.ingest().

        :param word: Gap word from logger.
        :returns: Topology prose or None.
        :rtype: str or None
        """
        return self.topology_text(word)
