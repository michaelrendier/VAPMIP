#!/usr/bin/env python3
"""tenseplan.py -- where a sentence's tense comes from.   (2026-11-25; the choices are the author's engineering, not measurements)

Three sources, one name each (sedenion_window.write(tense=...)):
    a tense name           'past', 'present', 'future', 'conditional', 'past perfect', 'future progressive' ... (lyndon_conjugation.parse_tense)
    'auto'                 the LEMNISCATE STATION of the sentence: boxkite_orbweaver_monad.OrbWeaverMonad._tense(depth, reach) -- the deepest loop of the web
                           is the past lobe, the shallowest the future lobe, the middle the node (now).  Needs depth and reach.
    'mirror'               the user's own tense, read from the prompt (was/were/had/did/-ed -> past; will/shall/going to -> future; else present)
    None                   'present'
"""
from __future__ import annotations

import re
from typing import Optional

STATION = {'past': 'past', 'now': 'present', 'future': 'future'}          # the orbweaver's three names -> grammatical tense


def lemniscate_tense(depth: int, reach: int) -> str:
    """Same rule as OrbWeaverMonad._tense: reach <= 1 is now; else the fraction (reach-depth)/(reach-1): < 1/3 past, > 2/3 future, else now."""
    if reach <= 1:
        return 'present'
    frac = (reach - depth) / (reach - 1)
    return 'past' if frac < 0.34 else 'future' if frac > 0.66 else 'present'


_PAST = re.compile(r"\b(was|were|had|did|went|said|made|came|saw|took|got|knew|thought|told|found|gave|\w{3,}ed)\b", re.I)
_FUT = re.compile(r"\b(will|shall|won't|going to|gonna|tomorrow|next)\b", re.I)


def mirror_tense(text: str) -> str:
    if _FUT.search(text): return 'future'
    if len(_PAST.findall(text)) >= 1: return 'past'
    return 'present'


def resolve(tense: Optional[str], prompt: str = '', depth: Optional[int] = None, reach: Optional[int] = None) -> str:
    if tense is None: return 'present'
    if tense == 'auto': return lemniscate_tense(depth, reach) if (depth is not None and reach is not None) else 'present'
    if tense == 'mirror': return mirror_tense(prompt)
    return STATION.get(tense, tense)
