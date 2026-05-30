"""
skills/integrity.py — Field integrity: token validation and health diagnostics.

:description:
    Protects the β-field from pollution by numeric data, code symbols,
    OCR garbage, URLs, file paths, and other non-linguistic tokens.

    Two layers:

    1. **TokenValidator** — per-token classifier. ``classify_token()``
       returns a tag; ``scrub()`` strips a word list down to clean tokens.

    2. **FieldHealth** — DTC-style diagnostics on the live Crank vocabulary.
       ``report()`` returns a dict of fault codes and percentages.

:classes:
    TokenValidator, FieldHealth

:functions:
    classify_token, scrub
"""

import re
from typing import List, Dict, Any

# ── Token classification tags ──────────────────────────────────────────────────
TAG_CLEAN    = 'clean'
TAG_NUMERIC  = 'numeric'
TAG_HEX      = 'hex'
TAG_URL      = 'url'
TAG_PATH     = 'path'
TAG_CODE     = 'code'
TAG_OCR      = 'ocr'
TAG_SHORT    = 'short'
TAG_LONG     = 'long'

# ── DTC fault codes (OBDII-style, P04xx = field quality) ──────────────────────
DTC_CONTAMINATION = 'P0420'   # overall non-clean ratio
DTC_NUMERIC_FLOOD = 'P0430'   # numeric / hex tokens
DTC_CODE_SYMBOLS  = 'P0440'   # snake_case / camelCase / operator tokens
DTC_OCR_GARBAGE   = 'P0450'   # low vowel-ratio garbage
DTC_TOKEN_LENGTH  = 'P0460'   # length-boundary violations

# Thresholds that trigger a DTC fault
_DTC_THRESHOLDS = {
    DTC_CONTAMINATION: 0.15,   # > 15 % non-clean → fault
    DTC_NUMERIC_FLOOD: 0.05,   # > 5 %  numeric/hex
    DTC_CODE_SYMBOLS:  0.05,
    DTC_OCR_GARBAGE:   0.05,
    DTC_TOKEN_LENGTH:  0.08,
}

# ── Compiled patterns ──────────────────────────────────────────────────────────
_RE_NUMERIC  = re.compile(r'^[0-9][0-9,._\-\+e/]*%?$')
_RE_HEX      = re.compile(r'^(?:0x)?[0-9a-f]{6,}$', re.I)
_RE_URL      = re.compile(r'^(?:https?|ftp|ftps)://', re.I)
_RE_PATH     = re.compile(r'^(?:/|\.{1,2}/|[a-z]:\\|~/).*', re.I)
_RE_SNAKE    = re.compile(r'^[a-z][a-z0-9]*(?:_[a-z0-9]+){1,}$')
_RE_CAMEL    = re.compile(r'^[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]+$')
_RE_ALLCAPS  = re.compile(r'^[A-Z]{4,}$')
_RE_OPERATOR = re.compile(r'^[!@#$%^&*()\[\]{}|<>=+\-*/\\:;,]+$')
_RE_HASH_STR = re.compile(r'^[0-9a-f]{32,}$', re.I)


def classify_token(token: str) -> str:
    """
    Classify a single token into a contamination category.

    :param token: Raw token string (already lowercased/stripped is fine).
    :returns: One of the TAG_* constants.
    :rtype: str
    """
    t = token.strip()
    if not t:
        return TAG_SHORT

    # Length guards
    if len(t) <= 1:
        return TAG_SHORT
    if len(t) > 45:
        return TAG_LONG

    # URL / path
    if _RE_URL.match(t):
        return TAG_URL
    if _RE_PATH.match(t) and ('/' in t or '\\' in t):
        return TAG_PATH

    # Hexadecimal hash strings (before numeric so 0xDEAD catches first)
    if _RE_HEX.match(t) or _RE_HASH_STR.match(t):
        return TAG_HEX

    # Pure numeric (integers, floats, percentages, fractions)
    if _RE_NUMERIC.match(t):
        return TAG_NUMERIC

    # Code symbols
    if _RE_OPERATOR.match(t):
        return TAG_CODE
    if _RE_SNAKE.match(t) and '_' in t:
        return TAG_CODE
    if _RE_CAMEL.match(t):
        return TAG_CODE
    if _RE_ALLCAPS.match(t):
        return TAG_CODE

    # OCR garbage — consonant cluster test (vowel ratio)
    letters = [c for c in t.lower() if c.isalpha()]
    if len(letters) >= 5:
        vowels = sum(1 for c in letters if c in 'aeiou')
        if vowels / len(letters) < 0.15:
            return TAG_OCR

    return TAG_CLEAN


def scrub(tokens: List[str]) -> List[str]:
    """
    Filter a list of tokens, returning only TAG_CLEAN ones.

    :param tokens: List of token strings.
    :returns: List of clean tokens.
    :rtype: list
    """
    return [t for t in tokens if classify_token(t) == TAG_CLEAN]


def scrub_text(text: str) -> str:
    """
    Scrub raw text: tokenise on whitespace, strip contaminated tokens,
    return rejoined clean text.

    :param text: Raw input text.
    :returns: Cleaned text safe for field ingestion.
    :rtype: str
    """
    tokens = text.split()
    return ' '.join(scrub(tokens))


class TokenValidator:
    """
    Stateful token auditor. Counts how many tokens pass and fail per category.
    Useful for logging scrub statistics without re-scanning twice.

    :Example:

    .. code-block:: python

        v = TokenValidator()
        clean = v.validate_all(['hello', 'world', '0xDEAD'])
        print(v.stats())
    """

    def __init__(self):
        self._total  = 0
        self._counts: Dict[str, int] = {}

    def validate(self, token: str) -> str:
        """
        Classify one token and update internal counts.

        :param token: Token to classify.
        :returns: Classification tag.
        :rtype: str
        """
        tag = classify_token(token)
        self._total += 1
        self._counts[tag] = self._counts.get(tag, 0) + 1
        return tag

    def validate_all(self, tokens: List[str]) -> List[str]:
        """
        Classify and filter a list, returning only clean tokens.

        :param tokens: List of tokens.
        :returns: Clean tokens only.
        :rtype: list
        """
        return [t for t in tokens if self.validate(t) == TAG_CLEAN]

    def stats(self) -> Dict[str, Any]:
        """
        :returns: Dict with total, per-tag counts and contamination ratio.
        :rtype: dict
        """
        contam = self._total - self._counts.get(TAG_CLEAN, 0)
        ratio  = contam / self._total if self._total else 0.0
        return {
            'total':       self._total,
            'clean':       self._counts.get(TAG_CLEAN, 0),
            'contaminated': contam,
            'ratio':       round(ratio, 4),
            'by_tag':      dict(self._counts),
        }

    def reset(self):
        """Reset all counters."""
        self._total  = 0
        self._counts = {}


class FieldHealth:
    """
    DTC-style diagnostic scanner for the live β-field vocabulary.

    Walks every word in the Crank vocabulary and classifies it.
    Returns fault codes (P04xx) for categories that exceed thresholds.

    :param crank: ``Crank`` instance from ``Engine.crank``.

    :Example:

    .. code-block:: python

        fh = FieldHealth(engine.crank)
        report = fh.report()
        for dtc in report['faults']:
            print(dtc)
    """

    def __init__(self, crank):
        self._crank = crank

    def scan(self) -> Dict[str, Any]:
        """
        Scan all vocabulary words and return per-tag counts and ratios.

        :returns: Dict with total, per-tag breakdown, ratios.
        :rtype: dict
        """
        words = self._crank._words
        total = len(words)
        if total == 0:
            return {'total': 0, 'ratios': {}, 'by_tag': {}}

        counts: Dict[str, int] = {}
        for w in words:
            tag = classify_token(w)
            counts[tag] = counts.get(tag, 0) + 1

        ratios = {tag: round(n / total, 4) for tag, n in counts.items()}
        return {'total': total, 'by_tag': counts, 'ratios': ratios}

    def report(self) -> Dict[str, Any]:
        """
        Full diagnostic report with DTC fault codes.

        :returns: Dict with scan results plus ``faults`` list of DTC codes
            and their measured ratios.
        :rtype: dict
        """
        scan = self.scan()
        ratios = scan.get('ratios', {})
        total  = scan.get('total', 0)

        # Contamination ratio = all non-clean
        clean_ratio = ratios.get(TAG_CLEAN, 1.0)
        contam      = round(1.0 - clean_ratio, 4)

        dtc_ratios = {
            DTC_CONTAMINATION: contam,
            DTC_NUMERIC_FLOOD: ratios.get(TAG_NUMERIC, 0.0) + ratios.get(TAG_HEX, 0.0),
            DTC_CODE_SYMBOLS:  ratios.get(TAG_CODE, 0.0),
            DTC_OCR_GARBAGE:   ratios.get(TAG_OCR, 0.0),
            DTC_TOKEN_LENGTH:  ratios.get(TAG_SHORT, 0.0) + ratios.get(TAG_LONG, 0.0),
        }

        faults = [
            {'code': code, 'ratio': round(ratio, 4)}
            for code, ratio in dtc_ratios.items()
            if ratio > _DTC_THRESHOLDS[code]
        ]

        return {
            'total':      total,
            'by_tag':     scan.get('by_tag', {}),
            'ratios':     ratios,
            'dtc_ratios': {k: round(v, 4) for k, v in dtc_ratios.items()},
            'faults':     faults,
            'clean':      not bool(faults),
        }
