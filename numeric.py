#!/usr/bin/env python3
"""numeric.py -- numbers are not words.   (Cody, 2026-11-25: "numbers get treated differently. different machinery.")

A numeral is not in the lexicon, has no synset, no neighbours, no probability under the word bigram, and no slot in a frame.  So it never enters the
word machinery: `split(text)` takes numerals (and digit-bearing codes such as x2, h264, 3d) OUT of a text before the words are read, and returns them as
Number records for their own channel (`NumberChannel`: counts by kind, magnitudes, repeated values; its own bits are never mixed into the word bits).

    kinds  integer | decimal | percent | ordinal | currency | signed | code
Number WORDS ('three', 'hundred') are words and stay in the word machinery for now (open: whether they should also be read as numbers).
"""
from __future__ import annotations

import collections
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

NUMBER = re.compile(r"(?<![A-Za-z0-9_.])(?P<sign>[-+])?(?P<cur>[$€£])?(?P<int>\d[\d,]*)(?P<dec>\.\d+)?(?P<suf>%|st|nd|rd|th)?(?![A-Za-z0-9_])")
CODE = re.compile(r"\b[A-Za-z]+\d[A-Za-z0-9]*\b|\b\d+[A-Za-z][A-Za-z0-9]*\b")


@dataclass
class Number:
    text: str
    kind: str
    value: Optional[float]


def _parse(m) -> Number:
    g = lambda k: m.group('n_' + k) if 'n_' + k in m.re.groupindex else m.group(k)
    s = m.group(0); body = g('int').replace(',', '') + (g('dec') or '')
    try: v = float(body)
    except ValueError: v = None
    if v is not None and g('sign') == '-': v = -v
    kind = ('percent' if g('suf') == '%' else 'ordinal' if g('suf') else 'currency' if g('cur') else 'decimal' if g('dec')
            else 'signed' if g('sign') else 'integer')
    return Number(s, kind, v)


VERSION = re.compile(r"\b\d+(?:\.\d+){2,}\b")
_ALL = re.compile("(?P<ver>%s)|(?P<num>%s)|(?P<code>%s)" % (VERSION.pattern, NUMBER.pattern.replace('(?P<', '(?P<n_'), CODE.pattern))


def split(text: str) -> Tuple[str, List[Number]]:
    """(text with every number replaced by a space, the numbers in order).  Codes (x2, 3d, h264) and versions (3.10.3) are opaque: kind 'code', value None."""
    out: List[Number] = []

    def sub(m):
        if m.group('ver') or m.group('code'):
            out.append(Number(m.group(0), 'code', None))
        else:
            out.append(_parse(m))
        return ' '
    return _ALL.sub(sub, text), out


class NumberChannel:
    """The user's numbers, kept apart from the vocabulary: how many of each kind, the order of magnitude they live at, which exact values recur."""

    def __init__(self):
        self.kinds: collections.Counter = collections.Counter(); self.decades: collections.Counter = collections.Counter(); self.values: collections.Counter = collections.Counter()
        self.n = 0

    def hear(self, nums: List[Number]) -> None:
        for x in nums:
            self.n += 1; self.kinds[x.kind] += 1
            if x.value is not None:
                self.values[x.text] += 1
                if x.value != 0: self.decades[int(math.floor(math.log10(abs(x.value))))] += 1

    def to_json(self) -> Dict[str, Any]:
        return {'n': self.n, 'kinds': dict(self.kinds), 'decades': {str(k): v for k, v in self.decades.items()}, 'values': dict(self.values.most_common(200))}

    @classmethod
    def from_json(cls, j: Dict[str, Any]) -> 'NumberChannel':
        c = cls(); c.n = j.get('n', 0); c.kinds.update(j.get('kinds', {})); c.decades.update({int(k): v for k, v in j.get('decades', {}).items()}); c.values.update(j.get('values', {}))
        return c
