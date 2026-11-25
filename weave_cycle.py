#!/usr/bin/env python3
"""weave_cycle.py -- ONE orbweaver step function, run at three scales (Cody's design, 2026-11-25; the mappings are engineering choices).

The orbweaver (boxkite_orbweaver_monad.py): a web of RADII from a hub; a scaffold spiral out, a capture spiral in; when the flow is TURBULENT
(>= 3 radii within half of the strongest) the spiral REVERSES along a strut, recaps, and jumps radius.  Here that is one function, `web_step`, and
each scale of the Monad supplies its own options and its own reversal:

    scale      kite                       options (the radii)                    reversal along the strut
    word       scalar boxkite             the senses of a word                   re-read the sense in the WIDER context (the topic and the ring)
    sentence   scaled boxkite (window)    the candidates for an open slot        re-pick under the ANTAGONIST tone: GLU|GABA, DA|5HT, NE|OXT
    paragraph  the orbweaver proper       the section directions (relations)     the pivot + wrap blocks of OrbWeaverMonad.weave
Never insert static functionality into the scaled kite: the scalar word web only reads (senses and spokes); the window calls it, it does not call the window.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(H, 'Currentwork', 'UserState'))

STRUT_PARTNER = {'GLU': 'GABA', 'GABA': 'GLU', 'DA': '5HT', '5HT': 'DA', 'NE': 'OXT', 'OXT': 'NE'}      # the three De Marrais struts of the neurotransmitter kite; OPI (the hub) has none
_REL_NAMES: Optional[List[str]] = None


def turbulent(values, frac: float = 0.5, k: int = 3) -> Tuple[bool, int]:
    """The orbweaver's rule (OrbWeaverMonad._turbulence): peaks = how many values are >= frac * the largest; turbulent when peaks >= k."""
    vs = [v for v in values if v > 0]
    if not vs: return False, 0
    m = max(vs); peaks = sum(1 for v in vs if v >= frac * m)
    return peaks >= k, peaks


def web_step(scale: str, options: Dict[str, float], reverse: Optional[Callable[[], Tuple[str, Dict[str, float]]]] = None,
             chosen: Optional[str] = None) -> Dict[str, Any]:
    """Rank the options; if the flow is turbulent call `reverse()` -> (alternative, its options) and keep the alternative only if it takes a larger SHARE
    of its options than the first choice did of its own (the sharper pick wins; the reversal can fail, and then nothing changes)."""
    if not options:
        return {'scale': scale, 'chosen': chosen, 'turbulent': False, 'peaks': 0, 'reversed': False, 'alt': None}
    first = chosen if chosen in options else max(options, key=lambda o: (options[o], o))
    turb, peaks = turbulent(options.values())
    out = {'scale': scale, 'chosen': first, 'turbulent': turb, 'peaks': peaks, 'reversed': False, 'alt': None}
    if turb and reverse is not None:
        alt, aopts = reverse(); out['alt'] = alt
        share = lambda o, k: o.get(k, 0.0) / (sum(o.values()) or 1.0)
        if alt is not None and alt != first and share(aopts, alt) > share(options, first):
            out['reversed'] = True; out['chosen'] = alt
    return out


# ── word scale (the scalar boxkite: read-only) ────────────────────────────────────────────────────
_STORE = None


def _store(window):
    global _STORE
    cu = getattr(window, 'usage', None)
    if cu is not None: return cu.store
    if _STORE is None:
        from vocab_store import UsageStore
        _STORE = UsageStore()
    return _STORE


def word_web(window, word: str, ctx: List[str], k: int = 3) -> Optional[Dict[str, Any]]:
    """The web of one word: its senses are the options (UsageStore.disambiguate: rank prior, gloss overlap, THIS user's history); turbulent when >= 3 senses
    are within half of the best; the reversal re-reads in the wider context (topic + the 16-slot ring).  Returns the chosen sense and its k strongest spokes."""
    global _REL_NAMES
    import wordnet_boxkite as W
    store = _store(window)
    sid, sc = store.disambiguate(word, [c for c in ctx if c != word])
    if not sc: return None
    wide = set(ctx) | {x for x in getattr(window, 'ring', []) if x}
    info = web_step('word', sc, lambda: (lambda r: (r[0], r[1]))(store.disambiguate(word, [c for c in wide if c != word])), chosen=sid)
    sense = info['chosen']
    vec = store.vector_of(sense); names = W.RELATION_METHODS
    spokes = [names[i] for i in sorted(range(len(vec)), key=lambda i: -vec[i])[:k] if vec[i]]
    return {'word': word, 'sense': sense, 'senses': len(sc), 'spokes': spokes, **{x: info[x] for x in ('turbulent', 'peaks', 'reversed')}}


# ── paragraph scale (the orbweaver proper) ────────────────────────────────────────────────────────
_OW = None


def paragraph(window, prompt: str, genre: str = 'paper', scale: Any = 'auto', max_sentences: int = 4, seed: int = 20260903) -> Dict[str, Any]:
    """Plan with OrbWeaverMonad.weave (radii, scaffold, capture, the pivot on turbulence, tense per block from the lemniscate), then write each paragraph block as
    a sentence with the window (tense = the block's station), leading with the block's connective.  The window must already have read the user's turn."""
    global _OW
    import boxkite_orbweaver_monad as B
    import lyndon_conjugation as LC
    from tenseplan import STATION
    if _OW is None: _OW = B.OrbWeaverMonad()
    doc = _OW.weave(prompt, scale=scale, genre=genre, seed=seed)
    sents, tenses = [], []
    for b in doc.blocks:
        if len(sents) >= max_sentences: break
        if b.kind in ('bridge', 'scope'): continue
        tense = STATION.get(b.tense, 'present')
        if b.kind == 'paragraph':
            r = window.write(b.text, tense=tense, read=False)
            body = r['sentence'].rstrip('.')
            s = (b.connective_out.capitalize() + ', ' + body[:1].lower() + body[1:] + '.') if r['sentence'] else ''
        else:                                                           # pivot / wrap: the orbweaver's own structural sentence
            s = b.text
        if s: sents.append(s); tenses.append(tense)
    return {'text': ' '.join(sents), 'sentences': sents, 'tenses': tenses, 'reach': doc.reach, 'turbulent': doc.turbulent, 'regime': doc.room.regime,
            'tense_phrases': LC.tense_phrases(tenses), 'monotony': LC.tense_monotony(tenses)}
