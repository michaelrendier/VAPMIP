#!/usr/bin/env python3
"""scaled_boxkite_orbweaver_monad.py -- the orbweaver REBUILT on the scaled boxkite, as a test bench.   (Cody, 2026-11-25)

"This is a child we have to teach how to speak English."  The old bench (boxkite_orbweaver_monad.py, kept as it was) planned a web and then filled it
with TEMPLATE prose ('it is a kind of {0}', 'the part instanced the theory').  Nothing a child says comes from a template.  This bench keeps the orbweaver's PLAN
(subclass: room shape, reach, turbulence rule, connective lexicon, lemniscate tense) and replaces every piece of prose with the scaled boxkite:

    input         numbers leave first (numeric.py: not words).  The content words are read ONE BY ONE through the word web (weave_cycle.word_web): a sense, 19 relation
                  spokes.  The SENTENCE vector is the SUM of those real 19-vectors (the old bench used hash(w) % 19, which changes from run to run; this does not).
    radii         the ranked directions of that vector (ptolemy_monad.infer_direction); each content word belongs to the direction of its own strongest spoke.
    scaffold      depth x radius outline, `reach` from the room shape.
    capture       in order, deepest loop first: one sentence per radius, WRITTEN BY THE WINDOW (sedenion_window.write) from that radius's words, tense = the lemniscate
                  station of its depth (past lobe -> node -> future lobe), led by the closed-class connective of its move.
    turbulence    >= 3 radii within half of the strongest: at the deepest loop the spiral REVERSES along a strut: 'but/however' + a sentence under the ANTAGONIST tone
                  (GLU|GABA, DA|5HT, NE|OXT), then a recap sentence from the hub radius, then the next radius.
    never         a template, a numeral, or a word the window did not pick.  Connectives are function words, the only prose that is not picked.

`audit(composition)` is the test bench: a list of named checks, each True or False (no numerals in the reply, no template phrase, tense = station, every sentence carries a
verb marker of its tense, every content word is in WordNet or was heard, pivots iff turbulent).  Replies are NOT claimed to be good English: the bench measures whether the wiring
holds, so that quality work has something fixed to stand on.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import boxkite_orbweaver_monad as OW
import numeric
import tenseplan as TP
import weave_cycle as WC
import sedenion_window as SW


@dataclass
class Piece:
    kind: str                 # paragraph | pivot | wrap
    depth: int
    radius: Optional[str]
    seed: List[str]
    connective: str
    tense: str
    tone: Any
    sentence: str
    marked: str = ''


@dataclass
class Composition:
    text: str
    pieces: List[Piece]
    plan: Dict[str, Any]
    numbers: List[Any] = field(default_factory=list)
    unknown: List[str] = field(default_factory=list)


class ScaledOrbWeaverMonad(OW.OrbWeaverMonad):
    def __init__(self, window: 'SW.SedenionWindow', seed: int = 20260903):
        super().__init__()
        self.win, self.seed = window, seed
        window.imitation = max(window.imitation, 2.0)                 # the child repeats the speaker's words before it invents any

    # ── input: words, never numbers ──────────────────────────────────────────────────
    def read_input(self, text: str) -> Dict[str, Any]:
        body, nums = numeric.split(text)
        toks = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]+", body)]
        seen: set = set(); content = []
        for w in toks:
            if w in SW.CLOSED or w in seen or len(w) < 3: continue
            seen.add(w); content.append(w)
        wn = self.win.nb.wn
        known = [w for w in content if wn.synsets(w)]; unknown = [w for w in content if w not in known]
        infos, rv = {}, [0] * 19
        for w in known:
            info = WC.word_web(self.win, w, known)
            if not info: continue
            vec = WC._store(self.win).vector_of(info['sense'])
            infos[w] = {**info, 'direction': OW.infer_direction(list(vec)) if any(vec) else 'observe'}
            rv = [a + b for a, b in zip(rv, vec)]
        return {'words': known, 'unknown': unknown, 'numbers': nums, 'infos': infos, 'rv': rv, 'body': body}

    # ── the cycle ────────────────────────────────────────────────────────────────────
    def compose(self, text: str, genre: str = 'paper', scale: Any = 'auto', max_pieces: int = 6) -> Composition:
        rng = random.Random(self.seed)
        r = self.read_input(text); words, rv = r['words'], r['rv']
        turbulent, peaks = self._turbulence(rv)
        room = self.room_shape(r['body'], words or ['it'], peaks)
        reach = self._reach_from_room(room, genre) if scale == 'auto' else self._reach(scale, genre)
        n_axes = max(1, min(reach + 1, max(1, len(words))))
        dirs = self._ranked_directions(rv, n_axes)
        owned: Dict[str, List[str]] = {d: [] for d in dirs}
        for w in words:                                                  # each word to the radius of its own strongest spoke; the rest round-robin
            d = r['infos'].get(w, {}).get('direction')
            (owned[d] if d in owned else owned[dirs[len(owned[dirs[0]]) % len(dirs)]]).append(w)
        for i, d in enumerate(dirs):
            if not owned[d] and words: owned[d] = [words[i % len(words)]]
        pieces: List[Piece] = []
        heard_axis = self.win.heard_tone[0]
        def say(kind, depth, radius, seed, conn, tense, tone=None):
            old = self.win.sensors.channels.get('tone_override')
            if tone: self.win.sensors.channels['tone_override'] = tone
            try: o = self.win.write(' '.join(seed) or 'it', tense=tense, read=False)
            finally:
                if tone: self.win.sensors.channels['tone_override'] = old
                if not old: self.win.sensors.channels.pop('tone_override', None)
            s = o['sentence']
            if not s: return
            lead = conn.capitalize() + ', ' + s[:1].lower() + s[1:] if conn else s
            pieces.append(Piece(kind, depth, radius, list(seed), conn, tense, tone, lead, o['marked']))
        first = True
        for depth in range(reach, 0, -1):
            tense = TP.STATION[self._tense(depth, reach)]
            for pos, d in enumerate(dirs):
                if len(pieces) >= max_pieces: break
                conn = self._conn('throughline' if first else 'elaborate', rng)[0]; first = False
                say('paragraph', depth, d, owned[d], conn, tense)
                if turbulent and depth == reach and pos < len(dirs) - 1 and len(pieces) < max_pieces:        # the eddy: reverse along the strut
                    partner = WC.STRUT_PARTNER.get(heard_axis, 'GABA')
                    say('pivot', depth, d, owned[d], self._conn('reverse', rng)[0], tense, (partner, self.win.heard_tone[1]))
                    say('wrap', depth, dirs[0], owned[dirs[0]], self._conn('wrap', rng)[0], tense)
        text_out = ' '.join(p.sentence for p in pieces)
        import lyndon_conjugation as LC
        tenses = [p.tense for p in pieces]
        plan = {'reach': reach, 'turbulent': turbulent, 'peaks': peaks, 'regime': room.regime, 'directions': dirs, 'tenses': tenses, 'genre': genre,
                'tense_phrases': LC.tense_phrases(tenses) if tenses else [], 'monotony': LC.tense_monotony(tenses) if tenses else None}
        return Composition(text_out, pieces, plan, r['numbers'], r['unknown'])

    # ── the test bench ───────────────────────────────────────────────────────────────
    def audit(self, c: Composition) -> Dict[str, bool]:
        wn = self.win.nb.wn; words = re.findall(r"[A-Za-z']+", SW.strip_markers(c.text).lower())
        conns = {x for v in OW._CONNECTIVES.values() for x in v for x in x.split()}
        def known(w): return w in SW.CLOSED or w in conns or bool(wn.synsets(w)) or bool(wn.morphy(w)) or w in self.win._user_words
        stations = {p.tense for p in c.pieces}
        prefixes = [re.sub(r'\{\d\}.*', '', t).strip().lower() for t in OW._SENTENCE_TEMPLATES.values()]
        paras = [p for p in c.pieces if p.kind == 'paragraph']
        return {
            'no_numerals': not re.search(r'\d', c.text),
            'no_template_phrase': not any(len(x) > 6 and x in c.text.lower() for x in prefixes),
            'tense_is_the_lemniscate_station': all(p.tense == TP.lemniscate_tense(p.depth, c.plan['reach']) for p in paras),
            'every_paragraph_sentence_carries_its_tense_marker': all(('|%s|' % p.tense) in SW.show_markers(p.marked) for p in paras),
            'every_word_is_known_or_heard': all(known(w) for w in words),
            'a_pivot_only_when_turbulent': all(p.kind != 'pivot' for p in c.pieces) or c.plan['turbulent'],
            'stations_are_the_three': stations <= {'past', 'present', 'future'},
        }
