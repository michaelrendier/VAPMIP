#!/usr/bin/env python3
"""
sedenion_window.py -- the one object that reads and writes a sentence, word by word.

Cody, 2026-11-21. The window holds the machinery described over the day:

  W_S  the big web (Web_scaled): the sentence. It holds the frame (the slots of the sentence) and the
       16-slot sedenion ring of the context heard so far (slot 0 = e0, the anchor).
  w_s  the little web (Web_scalar): one word. It looks at the neighbourhood of the topic in the Scalar
       Boxkite context hash (relation neighbours in WordNet, their exact context class and gamma_radial basin)
       and at the word-to-word statistics of a corpus, and picks ONE word for the open slot.

  One heartbeat per word:   W_S shrinks to the open slot   ->   w_s picks the word   ->   W_S places it
  and the web is RESCALED back to the whole sentence   ->   repass (tone, tense, conjugation)   ->   next slot.
  "Rescale" (big -> scale small, small -> scale big) is the only word used for that step.

  PATHWAY words (the closed class: the, of, in, is, and ...) are not picked from the whole language: the open slot
  is a RING of a few dozen words, so choosing one costs a few bits. CONTENT words are picked from the context
  neighbourhood. The cost of every pick is -log2 P, summed per sentence (the compression reading: the sentence is
  a point in nested intervals, each pick narrows it by P).

  Invisible markers, three per word: TONE (a neuromodulator axis and a level), TENSE, CONJUGATION, as Unicode Tag
  characters (category Cf, no glyph). PROVISIONAL codebook: the neuromodulator set and the level scale are
  the design notes of 2026-11-20 (docs/wiki/Tuning-the-Semantic-Prime-Concept-Engine/10_design_notes.md) made
  concrete enough to run; the author has not fixed them.

  Sensors: a VAG-COM style live harness (the dPrint idea, altered): read/write, in the loop. `VAGCOM=1` prints
  `[vag]` measuring blocks and `[tone]` state lines as the window streams; writable channels (tone_target,
  pathway_ring) are read by the next step. Always recorded in `sensors.log` for tests.

  Persuasion: `Persuader` follows Pascal's rule from "De l'art de persuader" as the author named it (INTERPRETATION,
  to be confirmed): start from the side the other person views the matter from (grant what is true there), then
  lead. In tone terms: the first replies meet the detected tone one level below its strength, then move one level
  per word toward the target tone.

Limits (stated, not hidden): the generated sentences are frame-filled and are only as good as the neighbourhood and the
corpus given; the tests check the machinery (accounting, rescale, markers, determinism), not literary quality.
Python first; port to ptol.c only after the tests are green and the author says so.
"""
from __future__ import annotations

import collections
import math
import os
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple

import wordnet_boxkite as WB
from tone_chord import Tone7

# ── markers: tone, tense, conjugation as invisible Tag characters ───────────────────────────────────
TAG0 = 0xE0020                                   # TAG SPACE .. TAG TILDE = U+E0020..U+E007E (95 characters)
NEURO = ['DA', '5HT', 'NE', 'OXT', 'GLU', 'GABA', 'CB1', 'ACh', 'OPI']       # dopamine serotonin noradrenaline oxytocin
LEVELS = 7                                                                    # glutamate GABA endocannabinoid acetylcholine opioid
TENSES = ['base', 'past', 'present', 'future', 'perfect', 'progressive', 'imperative', 'conditional']
CONJ = ['base', '3sg', 'past', 'pastpart', 'ing', 'plural', 'comparative', 'superlative']
_T_TONE, _T_TENSE, _T_CONJ = 0, 64, 72           # offsets inside the Tag block (tone uses 0..62)


_ALIAS = {'OT': 'OXT', 'eCB': 'CB1'}


def tone_char(axis: str, level: int) -> str:
    axis = _ALIAS.get(axis, axis)
    return chr(TAG0 + _T_TONE + NEURO.index(axis) * LEVELS + max(0, min(LEVELS - 1, level)))


def tense_char(t: str) -> str:
    return chr(TAG0 + _T_TENSE + TENSES.index(t))


def conj_char(c: str) -> str:
    return chr(TAG0 + _T_CONJ + CONJ.index(c))


def marker(axis: str, level: int, tense: str, conj: str) -> str:
    return tone_char(axis, level) + tense_char(tense) + conj_char(conj)


def decode_marker(m: str) -> Dict[str, Any]:
    a, b, c = (ord(x) - TAG0 for x in m[:3])
    return {'axis': NEURO[(a - _T_TONE) // LEVELS], 'level': (a - _T_TONE) % LEVELS,
            'tense': TENSES[b - _T_TENSE], 'conj': CONJ[c - _T_CONJ]}


def strip_markers(s: str) -> str:
    return ''.join(ch for ch in s if not (0xE0020 <= ord(ch) <= 0xE007E))


def show_markers(s: str) -> str:
    """The debugging view: the invisible markers made visible as <axis:level|tense|conj>."""
    out, i = [], 0
    while i < len(s):
        if 0xE0020 <= ord(s[i]) <= 0xE007E and i + 2 < len(s):
            d = decode_marker(s[i:i + 3]); out.append('<%s:%d|%s|%s>' % (d['axis'], d['level'], d['tense'], d['conj'])); i += 3
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


# ── the VAG-COM style sensor harness ───────────────────────────────────────────────────────────────
class Sensors:
    """Live measuring blocks (read) and adaptation channels (write). Prints when VAGCOM=1; always records."""

    def __init__(self, stream=None):
        self.flag = os.environ.get('VAGCOM', '0') == '1'
        self.stream = stream or sys.stderr
        self.log: List[Tuple[str, Dict[str, Any]]] = []
        self.channels: Dict[str, Any] = {'tone_target': ('GABA', 3), 'pathway_ring': None}

    def emit(self, group: str, **f) -> None:
        self.log.append((group, f))
        if self.flag:
            tag = '[tone]' if group == 'TONE' else '[vag]'
            body = ' '.join('%s=%s' % (k, (show_markers(v) if k == 'marker' else v)) for k, v in f.items())
            print('%s %-7s %s' % (tag, group, body), file=self.stream, flush=True)

    def read(self, group: str) -> List[Dict[str, Any]]:
        return [f for g, f in self.log if g == group]


# ── tone: detection, and Pascal's meet-then-lead ──────────────────────────────────────────────────
_LEX = {
    'NE':  "angry anger furious rage hate hated stupid idiot damn shut liar never always worst terrible awful useless".split(),
    'OPI': "sad sorry grief lonely hopeless tired empty cry crying lost hurt pain".split(),
    'DA':  "great love wonderful excited yes amazing fantastic win happy glad".split(),
    'OXT': "thanks thank please friend together dear kind welcome care".split(),
    'GABA': "calm quiet peace easy gentle slow rest okay fine".split(),
}


def detect_tone(text: str) -> Tuple[str, int]:
    """(axis, level) of the dominant neuromodulator axis by lexicon count; ('GABA', 2) when nothing matches."""
    words = re.findall(r"[a-z']+", text.lower())
    score = {a: sum(w in lex for w in words) for a, lex in _LEX.items()}
    bang = text.count('!') + sum(1 for w in re.findall(r"\b[A-Z]{3,}\b", text))
    if score['NE']:
        score['NE'] += bang
    axis = max(score, key=lambda a: score[a])
    if score[axis] == 0:
        return ('GABA', 2)
    return (axis, min(LEVELS - 1, 1 + score[axis]))


class Persuader:
    """Pascal's rule: meet the other side first, then lead. trajectory(k) gives the tone for the k-th word."""

    def __init__(self, heard: Tuple[str, int], target: Tuple[str, int] = ('GABA', 3)):
        self.heard, self.target = heard, target

    def trajectory(self, n: int) -> List[Tuple[str, int]]:
        """Tone for each of n words: meet the heard tone one level below its strength, ease toward calm, ARRIVE on the target by
        the last word (the levels of the heard axis fall linearly over the first n-1 words)."""
        ax, lv = self.heard
        tax, tlv = self.target
        if n <= 1:
            return [(tax, tlv)] if ax == tax else [(ax, max(0, lv - 1))]
        start = max(0, lv - 1)
        out = []
        for k in range(n - 1):
            level = start if n - 1 <= 1 else int(round(start * (1 - k / (n - 1))))
            out.append((ax, level))
        out.append((tax, min(LEVELS - 1, tlv)))
        return out


# ── the language statistics (word to word) ────────────────────────────────────────────────────────
DET = set("a an the this that these those my your his her its our their some any each every no".split())
PREP = set(("of in on at for with by from about into through over under between among against during before after "
            "above below up down out off near to toward upon within without").split())
CONJ_W = set("and or but nor yet so".split())
AUX = set("is are was were be been am has have had will would can could may might shall should do does did".split())
PRON = set("i you he she it we they me him her us them who which what".split())
RING = {'DET': DET, 'PREP': PREP, 'CONJ': CONJ_W, 'AUX': AUX}
_BE = set('is are was were be been am'.split()); _HAVE = set('has have had'.split())
CLOSED = set().union(*RING.values()) | PRON


class Bigram:
    """Word-to-word probabilities from a corpus: P(w | prev) = lam*bigram + (1-lam)*unigram (add-0.1 floor)."""

    def __init__(self, lam: float = 0.7):
        self.uni: collections.Counter = collections.Counter()
        self.bi: collections.Counter = collections.Counter()
        self.ctx: collections.Counter = collections.Counter()
        self.lam = lam
        self.total = 0

    def fit(self, texts: Sequence[str]) -> 'Bigram':
        for t in texts:
            toks = re.findall(r"[a-z]+(?:'[a-z]+)?", t.lower())
            self.uni.update(toks)
            for a, b in zip(toks, toks[1:]):
                self.bi[(a, b)] += 1
                self.ctx[a] += 1
        self.total = sum(self.uni.values())
        return self

    def p(self, w: str, prev: Optional[str]) -> float:
        pu = (self.uni.get(w, 0) + 0.1) / (self.total + 0.1 * (len(self.uni) + 1))
        if prev is None or not self.ctx.get(prev):
            return pu
        return self.lam * self.bi.get((prev, w), 0) / self.ctx[prev] + (1 - self.lam) * pu

    def frequent(self, wn, pos: str, n: int) -> List[str]:
        out = []
        for w, _ in self.uni.most_common():
            if w in CLOSED or len(w) < 3:
                continue
            if wn.synsets(w, pos):
                out.append(w)
                if len(out) >= n:
                    break
        return out


# ── the context neighbourhood in the Scalar Boxkite hash ───────────────────────────────────────────
class Neighborhood:
    """Relation neighbours of a topic word in WordNet, each with its exact context class and gamma_radial."""

    def __init__(self):
        from nltk.corpus import wordnet as wn
        self.wn = wn
        self._cls: Dict[tuple, int] = {}

    def point(self, synset) -> Dict[str, Any]:
        v = tuple(WB.context_vector(synset))
        cls = self._cls.setdefault(v, len(self._cls) + 1)
        g = WB.gamma_radial(list(v))
        return {'vec19': v, 'class': cls, 'gamma': g, 'broca': sum(1 for x in v if x), 'wernicke': None if g is None else 1.0 + g}

    def around(self, word: str, pos: str, hops: int = 2) -> Dict[str, float]:
        """lemma -> weight, over the relation neighbourhood of the first sense of `word` (itself weight 1.0)."""
        ss = self.wn.synsets(word, pos)
        out: Dict[str, float] = {}
        if not ss:
            return out
        s0 = ss[0]

        def add(syn, w):
            for l in syn.lemma_names():
                if '_' in l or not l.isalpha():
                    continue
                out[l.lower()] = max(out.get(l.lower(), 0.0), w)
        add(s0, 1.0)
        rel = ('hypernyms', 'hyponyms', 'member_holonyms', 'part_holonyms', 'member_meronyms', 'part_meronyms',
               'similar_tos', 'also_sees', 'entailments', 'verb_groups', 'attributes')
        for m in rel:
            for t in getattr(s0, m)():
                add(t, 0.6)
        if hops >= 2:
            for h in s0.hypernyms():
                for sib in h.hyponyms():
                    add(sib, 0.35)
        return out


# ── the window ─────────────────────────────────────────────────────────────────────────────────────
FRAMES = {
    'svo': ['DET', 'N', 'V', 'DET', 'N'],
    'sv_prep': ['DET', 'N', 'V', 'PREP', 'DET', 'N'],
    'sva': ['DET', 'N', 'AUX', 'ADJ'],
}


class SedenionWindow:
    """Reads and writes sentences one word at a time. `vocab` (optional LiveVocabulary) learns from what is read."""

    def __init__(self, bigram: Bigram, vocab=None, sensors: Optional[Sensors] = None, tone_target=('GABA', 3), english=None,
                 stats=None, selfctx=None, state=None, usage=None, web=False):
        self.bg = stats if stats is not None else bigram      # EnglishStats (usage frequency, levels) or the plain Bigram
        self.stats = stats                  # EnglishStats: learns from what the user says (outside text only), never from his own speech
        self.selfctx = selfctx              # context_gearbox.SelfContexts: DATA SELF (what he says/does) and USER SELF (how the user reacts)
        self.tone7 = Tone7()                # the seven neuromodulator levels now in force (the constructor reads knobs() from it)
        self.level = 'general'              # the assumed educational response desire
        self._user_words: set = set()
        self._last_user: Optional[int] = None
        self.vocab = vocab                 # LiveVocabulary: relation edges, senses, history
        self.english = english             # MonadEnglish: the co-occurrence field (A-matrix), deepened by every word read or said
        self.sensors = sensors or Sensors()
        self.sensors.channels['tone_target'] = tone_target
        self.nb = Neighborhood()
        self.t = 0                                   # words processed (read and written), one tick each
        self.ring: List[Optional[str]] = [None] * 16     # the sedenion ring: slot 0 = e0 (anchor)
        self.cum_bits = 0.0
        self.persuader: Optional[Persuader] = None
        self.heard_tone: Tuple[str, int] = ('GABA', 2)
        self.usage = usage                 # conversation_usage.ConversationUsage (optional): the user's own usage mixed into every P, and the bw_correction channel
        self.state = state                 # state_repass.StateRepass (optional): the user's 14 poles read into the repass (2026-11-25)
        self.imitation = 0.0               # a child repeats what it hears: extra weight on the speaker's own words (0 = off; responder/scaled orbweaver set it)
        self.web = web                     # the orbweaver step at sentence scale (weave_cycle.py): a thin-margin pick is re-picked along the strut (2026-11-25)
        self._last_pick: Dict[str, Any] = {}
        self._mt: Optional[str] = None     # the marker tense of the last repass

    def _p(self, w: str, prev: Optional[str]) -> float:
        p = self.stats.p(w, prev, self.level) if self.stats is not None else self.bg.p(w, prev)
        if self.usage is not None:                                  # the user's own usage as probability: lambda = N/(N+200), cold store = general English
            lam = self.usage.store.confidence()
            p = (1.0 - lam) * p + lam * self.usage.store.p_word(w)
        return p

    # -- sedenion ring --------------------------------------------------------
    def fill(self) -> int:
        """Slots of the 16-slot ring that hold a word. The resolution is always 16; this is how many of them have evidence."""
        return sum(1 for x in self.ring if x is not None)

    def _place(self, word: str) -> None:
        if self.ring[0] is None:
            self.ring[0] = word
        else:
            self.ring = [self.ring[0]] + [word] + self.ring[1:15]      # e0 stays; newest enters slot 1

    # -- sensors --------------------------------------------------------------
    def _read_blocks(self, word: str, pos: str, slot: str, r_before: float, r_after: float, bits: float,
                     pathway: bool, mk: str, tone: Tuple[str, int], tense: str, conj: str) -> None:
        pt = None
        ss = self.nb.wn.synsets(word, pos if pos in ('n', 'v', 'a', 'r') else 'n')
        if ss:
            pt = self.nb.point(ss[0])
        self.sensors.emit('STEP', t=self.t, slot=slot, r_before=round(r_before, 6), r_after=round(r_after, 6),
                          bits=round(bits, 3), cum_bits=round(self.cum_bits, 3))
        self.sensors.emit('WORD', t=self.t, word=word, pathway=pathway,
                          cls=None if pt is None else pt['class'], gamma=None if not pt or pt['gamma'] is None else round(pt['gamma'], 4))
        if pt and pt['gamma'] is not None:
            Z = complex(pt['wernicke'], pt['broca'])
            Z0 = 1.0
            gin = (Z - Z0) / (Z + Z0)
            gout = ((Z0 * Z0 / Z) - Z0) / ((Z0 * Z0 / Z) + Z0)
            self.sensors.emit('BALANCE', t=self.t, wernicke=round(Z.real, 4), broca=int(Z.imag), gamma_in=round(abs(gin), 4),
                              gamma_out=round(abs(gout), 4), balance=round(abs(gin + gout), 12))
        self.sensors.emit('TONE', t=self.t, word=word, tone='%s:%d' % tone, tense=tense, conj=conj, marker=mk)

    # -- reading ----------------------------------------------------------------
    def read(self, text: str, echo: int = 0) -> List[Dict[str, Any]]:
        """Read text word by word. Every word advances the window one tick. Returns one record per word. `echo` counts how often
        this content has already looped through the Monad (its own speech heard again is echo 1; the cap is monad_english_io.ECHO_CAP)."""
        if self.state is not None and echo == 0:                     # the user's turn: read the 14-pole state, heal, cancel, re-plan (state_repass.py)
            import state_repass as _sr
            summ = self.state.observe(text, fill=self.fill())
            self.heard_tone = self.state.heard_tone()
            self.persuader = _sr.StatePersuader(self.state, self.sensors.channels['tone_target'])
            self.sensors.emit('STATE', t=self.t, fill=self.fill(), held=summ['held'], healed=summ['healed_poles'], k_eff=summ['k_eff'], axis=summ['axis'])
        else:
            self.heard_tone = detect_tone(text)
            self.persuader = Persuader(self.heard_tone, self.sensors.channels['tone_target'])
        import numeric as _num
        text, nums = _num.split(text)                                   # numbers are not words: they leave here and are never read, placed or priced as words
        if nums: self.sensors.emit('NUM', t=self.t, numbers=[(n.text, n.kind) for n in nums])
        self._user_words = set(re.findall(r"[a-z']+", text.lower())) - CLOSED
        if echo == 0 and self.stats is not None:
            self.stats.observe(text)                                   # usage statistics update as time passes
            self.level = self.stats.level_for(text)
        if echo == 0 and self.selfctx is not None:
            self._last_user = self.selfctx.user_says('prompt', text=text, tone={self.heard_tone[0]: self.heard_tone[1] / 6.0},
                                                      level=self.level)
        recs = []
        prev = None
        for w in re.findall(r"[A-Za-z']+", text):
            lw = w.lower()
            pathway = lw in CLOSED
            p = self._p(lw, prev)
            bits = -math.log2(p)
            if pathway:
                bits = min(bits, -math.log2(max(p, 1e-9)))
            self.t += 1
            self.cum_bits += bits
            if not pathway:
                self._place(lw)
                if self.vocab is not None:
                    self.vocab.note_unknown(lw)
            mk = marker(self.heard_tone[0], self.heard_tone[1], 'present', 'base')
            self._read_blocks(lw, 'n', 'heard', 1.0, p, bits, pathway, mk, self.heard_tone, 'present', 'base')
            recs.append({'t': self.t, 'word': lw, 'pathway': pathway, 'bits': bits, 'ring': list(self.ring)})
            prev = lw
        if self.vocab is not None:
            self.vocab.hear(text)
        if self.english is not None:
            import monad_english_io as _meio
            edges, new = _meio.hear(self.english, text, echo=echo)
            self.sensors.emit('USAGE', t=self.t, edges_deepened=edges, new_words=new, echo=echo)
        return recs

    # -- writing: the heartbeat ----------------------------------------------
    def _pick(self, slot: str, prev: Optional[str], topic: Dict[str, Dict[str, float]], taken: set
              ) -> Tuple[str, float, int]:
        """w_s: one word for the open slot. Returns (word, P, candidate count). P is the pick's weight rescaled over
        the candidate set. Pathway slots draw from a RING; content slots from the topic neighbourhood."""
        ring = self.sensors.channels.get('pathway_ring')
        if slot in RING:
            cand = {w: 1.0 for w in (ring if ring and slot == 'DET' else RING[slot])}
            if slot == 'DET':
                cand = {w: 1.0 for w in ('the', 'a', 'an', 'this', 'that', 'its')}
        elif slot in ('N', 'V', 'ADJ'):
            pos = {'N': 'n', 'V': 'v', 'ADJ': 'a'}[slot]
            cand = {}
            for src in topic.get(pos, {}):
                cand[src] = topic[pos][src]
            if not cand:
                cand = {w: 0.2 for w in self.bg.frequent(self.nb.wn, pos, 60)}
            cand = {w: x for w, x in cand.items() if w not in taken}
        else:
            cand = {}
        if not cand:
            return ('', 1.0, 0)
        self._last_pick = {}
        if slot not in ('N', 'V', 'ADJ'):                                 # a pathway ring: a few dozen words, picked cheaply
            weights = {w: self._p(w, prev) for w in cand}
            tot = sum(weights.values())
            best = max(weights, key=lambda w: (weights[w], w))
            return (best, weights[best] / tot, len(weights))
        kn = self.tone7.knobs()                                           # the seven tones act here
        weights = {}
        for w, x in cand.items():
            g = (self.usage.channels.get('bw_correction', 0.0) if self.usage is not None else 0.0) + self.sensors.channels.get('bw_correction', 0.0)
            v = (self._p(w, prev) ** (kn['coherence'] * max(0.0, 1.0 + g))) * x        # 5HT: weight on the word-to-word statistics; g = Broca-Wernicke drift correction (bw_drift.py): >0 favour probable words (cheaper to write), <0 flatten
            if w in self._user_words:
                v *= kn['user_boost'] + self.imitation                    # OXT: alignment with the user's own words (+ imitation: the child repeats what it heard)
            weights[w] = v
        mx = max(weights.values())
        if self.imitation > 0 and self._user_words:                       # the child's own ear: a word it just heard is at least as likely as the best, whatever its frequency
            mx0 = max(weights.values())
            for w in list(weights):
                if w in self._user_words or any(w == (self.nb.wn.morphy(u, 'n') or self.nb.wn.morphy(u, 'v') or u) for u in self._user_words):
                    weights[w] = max(weights[w], 1.1 * mx0)
            mx = max(weights.values())
        weights = {w: v for w, v in weights.items() if v >= kn['prune_floor'] * mx}          # GABA: prune weak candidates
        ranked = sorted(weights, key=lambda w: (-weights[w], w))[:kn['pool_size']]            # NE narrows, GLU widens
        weights = {w: weights[w] for w in ranked}
        tot = sum(weights.values())
        best = ranked[min(kn['novelty_rank'], len(ranked) - 1)]            # DA: explore down the ranking
        self._last_pick = {'weights': dict(weights), 'tot': tot}
        return (best, weights[best] / tot, len(weights))

    def write(self, prompt: str, frame: Optional[str] = None, tense: Optional[str] = 'present', depth: Optional[int] = None, reach: Optional[int] = None,
              number: str = 'sg', read: bool = True) -> Dict[str, Any]:
        """Write one sentence in answer to `prompt`. Returns the sentence (plain and marked), the per-word records.
        `tense`: any name lyndon_conjugation.parse_tense understands ('past', 'future progressive', 'past perfect' ...); 'auto' takes it from the lemniscate
        station (`depth` of `reach`, tenseplan.py); 'mirror' follows the user's own tense; None is 'present'.  `read=False`: the prompt was already read (a paragraph)."""
        import tenseplan as _tp
        tense = _tp.resolve(tense, prompt, depth, reach)
        if read:
            self.read(prompt)
        toks = re.findall(r"[a-z']+", prompt.lower())
        topic: Dict[str, Dict[str, float]] = {'n': {}, 'v': {}, 'a': {}}
        for w in toks:
            if w in CLOSED:
                continue
            for pos in ('n', 'v', 'a'):
                for k, x in self.nb.around(w, pos).items():
                    topic[pos][k] = max(topic[pos].get(k, 0.0), x)
        if self.imitation > 0:                                              # a child can say the words it just heard, in the parts of speech it knows them as
            for w in toks:
                if w in CLOSED: continue
                for pos in ('n', 'v', 'a'):
                    lem = self.nb.wn.morphy(w, pos) or w                  # 'rules' as a verb is the lemma 'rule' (the verb group inflects it; a surface form would be inflected twice)
                    if self.nb.wn.synsets(lem, pos): topic[pos][lem] = max(topic[pos].get(lem, 0.0), 1.0)
        nouns = [w for w in toks if w not in CLOSED and self.nb.wn.synsets(w, 'n')]
        first = self.sensors.channels.get('tone_override') or (self.persuader.trajectory(1)[0] if self.persuader else self.heard_tone)
        t0 = Tone7.from_axis(first[0], first[1] / 6.0)
        short = t0.knobs()['short_frame']                                  # NE: shorter frames under urgency
        slots = FRAMES[frame or ('sva' if short else ('svo' if len(nouns) >= 2 else 'sv_prep'))]
        traj = self.persuader.trajectory(len(slots)) if self.persuader else [self.heard_tone] * len(slots)
        words, marked, recs, taken, prev = [], [], [], set(), None
        sentence_bits = 0.0
        for k, slot in enumerate(slots):
            r_big = 1.0                                    # W_S: the whole sentence, full scale
            ov = self.sensors.channels.get('tone_override')
            ax, lv = ov or traj[k]
            self.tone7 = Tone7.from_axis(ax, lv / 6.0)                 # the tone in force for this slot
            word, P, ncand = self._pick(slot, prev, topic, taken)      # W_S shrinks to the slot; w_s picks
            if not word:
                continue
            if self.web and slot in ('N', 'V', 'ADJ'):                 # the orbweaver step at sentence scale: thin margin -> reverse along the strut
                word, P, ncand, (ax, lv) = self._revisit(slot, prev, topic, taken, (word, P, ncand), (ax, lv))
                self.tone7 = Tone7.from_axis(ax, lv / 6.0)
                import weave_cycle as _wc
                ww = _wc.word_web(self, word, toks)                    # the same step at word scale (scalar kite, read-only): which sense, which spokes
                if ww: self.sensors.emit('WEB', t=self.t, scale='word', word=word, sense=ww['sense'], senses=ww['senses'], spokes=ww['spokes'], turbulent=ww['turbulent'], reversed=ww['reversed'])
            r_small = r_big * P                            # the interval narrowed by the pick
            bits = -math.log2(P)
            sentence_bits += bits
            self.cum_bits += bits
            self.t += 1
            surface, conj = self._repass(word, slot, tense, words, number)
            axis, level = self.sensors.channels.get('tone_override') or (ax, lv)
            mt = self._mt or ('base' if slot != 'V' else 'present')
            mk = marker(axis, level, mt, conj)
            if slot in ('N', 'V', 'ADJ'):
                self._place(word); taken.add(word)
            self._read_blocks(word, {'N': 'n', 'V': 'v', 'ADJ': 'a'}.get(slot, 'n'), slot, r_big, r_small, bits,
                              slot in RING, mk, (axis, level), mt, conj)
            r_big = 1.0                                    # RESCALED: back to the whole sentence, word in place
            words.append(surface)
            marked.append(mk + surface)
            recs.append({'t': self.t, 'slot': slot, 'word': surface, 'P': P, 'bits': bits, 'candidates': ncand,
                         'pathway': slot in RING, 'r_after_pick': r_small, 'r_rescaled': r_big, 'marker': mk})
            prev = word
        text = ' '.join(words)
        text = (text[:1].upper() + text[1:] + '.') if text else ''
        if text and self.english is not None:                  # he hears what he says (echo 1): usage deepens the field
            import monad_english_io as _meio
            _meio.hear(self.english, text, echo=1)
        out = {'sentence': text, 'marked': ' '.join(marked) + '.', 'records': recs, 'bits': sentence_bits,
               'topic_size': {k: len(v) for k, v in topic.items()}, 'level': self.level}
        if self.selfctx is not None and text:
            out['seq'] = self.selfctx.ptolemy('say', responds_to=self._last_user, sentence=text, bits=round(sentence_bits, 3),
                                              tone=dict(self.tone7.levels), level=self.level)
        return out

    def _revisit(self, slot, prev, topic, taken, pick, tone):
        """Sentence-scale web step (weave_cycle.web_step): when >= 3 candidates sit within half of the best (the orbweaver's turbulence rule) the
        spiral reverses along a strut: the slot is picked again under the antagonist tone (GLU|GABA, DA|5HT, NE|OXT) and the sharper pick is kept."""
        import weave_cycle as WC
        word, P, ncand = pick; ax, lv = tone
        w0 = dict(self._last_pick.get('weights') or {})
        if not w0 or ax not in WC.STRUT_PARTNER:
            return word, P, ncand, tone
        keep = self.tone7; alt: Dict[str, Any] = {}

        def reverse():
            self.tone7 = Tone7.from_axis(WC.STRUT_PARTNER[ax], lv / 6.0)
            w2, P2, n2 = self._pick(slot, prev, topic, taken); alt.update(word=w2, P=P2, n=n2, w=dict(self._last_pick.get('weights') or {}))
            return w2, alt['w'] or {w2: 1.0}
        info = WC.web_step('sentence', w0, reverse, chosen=word)
        self.tone7 = keep
        self.sensors.emit('WEB', t=self.t, scale='sentence', slot=slot, peaks=info['peaks'], turbulent=info['turbulent'], reversed=info['reversed'])
        if info['reversed']:
            return alt['word'], alt['P'], alt['n'], (WC.STRUT_PARTNER[ax], lv)
        return word, P, ncand, tone

    def _repass(self, word: str, slot: str, tense: str, said: List[str], number: str = 'sg') -> Tuple[str, str]:
        """Tense and conjugation of the placed word through the Lyndon verb group (lyndon_conjugation.py); returns (surface, conjugation code).
        The marker tense of this word is left in self._mt."""
        import lyndon_conjugation as LC
        self._mt = None
        if slot == 'V':
            fr = LC.inflection_frame(tense, word, number, 3 if number == 'sg' else 3)
            self._mt = fr['tense']
            return ' '.join(fr['surface']), fr['conj']
        if slot == 'AUX' and tense != 'present' and word in _BE | _HAVE:                  # the auxiliary of an 'sva' frame follows the tense; 'present' keeps the ring's word
            lemma = 'be' if word in _BE else 'have'
            fr = LC.inflection_frame(tense, lemma, number, 3)
            self._mt = fr['tense']
            return ' '.join(fr['surface']), fr['conj']
        return word, 'base'

    # -- rings: the Broca-Wernicke reading, for the Scale engine ---------------
    def scale_point(self, word: str, pos: str = 'n') -> Optional[Dict[str, Any]]:
        """Z = wernicke + i*broca for the word's first sense (feed to ValaQuenta scale: broca_wernicke_ring_chart)."""
        ss = self.nb.wn.synsets(word, pos)
        if not ss:
            return None
        pt = self.nb.point(ss[0])
        if pt['wernicke'] is None:
            return None
        return {'word': word, 'Z': complex(pt['wernicke'], pt['broca']), 'class': pt['class'], 'gamma': pt['gamma']}
