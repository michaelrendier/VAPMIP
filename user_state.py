#!/usr/bin/env python3
"""
user_state.py -- the USER'S EMOTIONAL STATE from the text of a prompt: a battery of small NLP meters, each adding
evidence to ONE 15-layer object, the user's neurotransmitter "solution".

Cody, 2026-11-22: "what combinations of what neurotransmitters describes the mind that wrote the prompt ... a simple small
set of tools used in a 'battery' of NLP ... building a 'mindset' from that." The cold prompt ASSIGNS the NLP findings; each later
prompt ADDS a reading ("warms up"), so the drift can be seen. Nothing here reads the recipes (neuro_recipes.py) yet; the state is
the INPUT side of the machine.

THE OBJECT (the 15 layers, a sedenion's 15 imaginary units; the real part is the scalar output)
    dark  V I B G Y O R | R O Y G B I V  light          (7 + 1 + 7 = 15; the Cayley-Dickson split: e1..e7, e8, e9..e15)
    every neurotransmitter has TWO poles that stay separate: a dark pole (negative speaking tone) and a light pole (positive).
    level 0..9 per pole (10 steps); 0 = no change (black).  the centre e8 is the cursor (the window of the slide rule).
    e0 = the single scalar, from halving the dark side against the light side (see `scalar`).

THE SEVEN, in kite order = rainbow order:  OPI red (hub) . GLU orange . GABA yellow . DA green . 5HT blue . NE indigo . OXT violet

THE METERS (each returns {NT: (dark, light)} in 0..1 and a weight)
    vader            valence (NLTK VADER lexicon)
    go_emotions      28-label emotion model (SamLowe/roberta-base-go_emotions)
    hartmann         7-emotion model (j-hartmann/emotion-english-distilroberta-base)
    irony            irony / sarcasm model (cardiffnlp/twitter-roberta-base-irony)  -> inverts the affect axes (the eye roll)
    arousal          caps, exclamations, repeated punctuation, elongation -> NE / GLU, signed by the valence
    profanity        density of profanity -> GABA (disinhibition), and OXT when it is aimed at "you"
    dialogue_act     NLTK NPS Chat naive-Bayes act (Reject / Accept / Clarify / Greet / Emphasis ...)
The label -> neurotransmitter tables are SETPOINTS chosen from the direction of effect in the recipe book's sources; they are tested
against human labels in Currentwork/UserState/run_battery.py and retooled from the result.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── the statistics engine: ValaQuenta/modules/bell_curve/maths.py (stdlib only; loaded by path, no package side effects) ──
def _load_bell_curve():
    for root in (os.path.join(_HERE, '..', 'ValaQuenta'), os.environ.get('VALAQUENTA_PATH', '')):
        p = os.path.join(root, 'modules', 'bell_curve', 'maths.py') if root else ''
        if p and os.path.exists(p):
            spec = importlib.util.spec_from_file_location('bell_curve_maths', p)
            m = importlib.util.module_from_spec(spec)
            import sys
            sys.modules['bell_curve_maths'] = m          # dataclasses need the module registered
            spec.loader.exec_module(m)
            return m
    raise ImportError('ValaQuenta/modules/bell_curve/maths.py not found; set VALAQUENTA_PATH')
BC = _load_bell_curve()

# ═════════════════════════ THE 15 LAYERS ═════════════════════════════════════════
NT = ('OPI', 'GLU', 'GABA', 'DA', '5HT', 'NE', 'OXT')                  # kite order = rainbow order, red .. violet
NT_NAME = {'OPI': 'mu-opioid (hub)', 'GLU': 'glutamate', 'GABA': 'GABA', 'DA': 'dopamine', '5HT': 'serotonin',
           'NE': 'norepinephrine', 'OXT': 'oxytocin'}
# the author's palette from emotional-console-idea.svg: (dark half, light half)
PALETTE: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
    'OPI':  ((0x80, 0x00, 0x00), (0xFF, 0x00, 0x00)),     # red
    'GLU':  ((0xB0, 0x40, 0x00), (0xFF, 0x80, 0x30)),     # orange
    'GABA': ((0x80, 0x80, 0x00), (0xFF, 0xFF, 0x00)),     # yellow
    'DA':   ((0x00, 0x80, 0x00), (0x00, 0xFF, 0x00)),     # green
    '5HT':  ((0x00, 0x00, 0x80), (0x00, 0x00, 0xFF)),     # blue
    'NE':   ((0x80, 0x00, 0x80), (0xFF, 0x00, 0xFF)),     # indigo (the svg draws it magenta)
    'OXT':  ((0x40, 0x00, 0x50), (0x80, 0x00, 0x80)),     # violet
}
LEVELS = 10
# the 15 layers in display order: dark side VIBGYOR (violet first), the cursor, light side ROYGBIV
LAYER_ORDER: List[Tuple[str, str]] = [(a, 'dark') for a in reversed(NT)] + [('', 'cursor')] + [(a, 'light') for a in NT]
# sedenion index: e1..e7 = dark side in LAYER_ORDER, e8 = the cursor (Cayley-Dickson doubling unit), e9..e15 = light side
SED_INDEX = {lay: i + 1 for i, lay in enumerate(LAYER_ORDER)}


class Reading(dict):
    """{NT: [dark, light]} floats in 0..1.  Missing NT = no evidence."""

    @staticmethod
    def zero() -> 'Reading':
        return Reading({a: [0.0, 0.0] for a in NT})


# ═════════════════════════ LABEL -> NEUROTRANSMITTER SETPOINTS ═══════════════════
# signed: + = light pole, - = dark pole.  Direction of effect from the sources in the Neurochemical Recipe Book (panksepp 2010 etc.).
EMO: Dict[str, Dict[str, float]] = {
    'admiration': {'OXT': .5, 'DA': .4, '5HT': .4},
    'amusement': {'DA': .6, 'OPI': .4, 'OXT': .3, 'GABA': .2},
    'anger': {'NE': -.8, 'GLU': -.7, 'GABA': -.8, '5HT': -.5, 'OPI': -.3},
    'annoyance': {'NE': -.4, 'GABA': -.4, '5HT': -.3},
    'approval': {'5HT': .4, 'OXT': .3, 'DA': .2},
    'caring': {'OXT': .8, 'OPI': .5, '5HT': .3},
    'confusion': {'NE': .4, 'DA': -.3, '5HT': -.2},
    'curiosity': {'DA': .7, 'GLU': .6, 'NE': .4},
    'desire': {'DA': .8, 'OXT': .3, 'NE': .3},
    'disappointment': {'DA': -.7, '5HT': -.5, 'OPI': -.4},
    'disapproval': {'5HT': -.3, 'OXT': -.3, 'NE': -.2},
    'disgust': {'5HT': -.4, 'OXT': -.5, 'GABA': -.2, 'NE': -.3},
    'embarrassment': {'5HT': -.6, 'NE': -.4, 'OXT': -.2},
    'excitement': {'DA': .8, 'NE': .6, 'GLU': .6},
    'fear': {'NE': -.9, 'GLU': -.6, 'GABA': -.7, 'OXT': -.2},
    'gratitude': {'OXT': .8, '5HT': .5, 'OPI': .5},
    'grief': {'OPI': -.9, 'OXT': -.5, '5HT': -.7, 'DA': -.5},
    'joy': {'DA': .7, '5HT': .7, 'OPI': .6, 'OXT': .3},
    'love': {'OXT': .9, 'OPI': .7, 'DA': .5, '5HT': .5},
    'nervousness': {'NE': -.6, 'GABA': -.5, 'GLU': -.3, 'DA': -.2},
    'optimism': {'DA': .6, '5HT': .6, 'NE': .2},
    'pride': {'5HT': .7, 'DA': .5},
    'realization': {'GLU': .5, 'DA': .3, 'NE': .3},
    'relief': {'GABA': .7, 'OPI': .6, '5HT': .4},
    'remorse': {'5HT': -.5, 'OPI': -.3, 'NE': -.2},
    'sadness': {'5HT': -.7, 'DA': -.6, 'OPI': -.6, 'OXT': -.2},
    'surprise': {'NE': .5, 'GLU': .4, 'DA': .2},
    'cynical': {'DA': -.5, '5HT': -.5, 'OXT': -.4, 'NE': -.2, 'OPI': -.2},       # the eye roll: warm words, cold meaning
    'neutral': {},
    # the 7-emotion model's names that differ
}
ACT = {'Reject': {'OXT': -.3, '5HT': -.3, 'NE': -.2}, 'Accept': {'OXT': .3, '5HT': .3}, 'Clarify': {'DA': .3, 'GLU': .3},
       'Greet': {'OXT': .4, '5HT': .2}, 'Bye': {'OXT': .1}, 'Emphasis': {}, 'Emotion': {}}
AFFECT_AXES = ('OPI', 'DA', '5HT', 'OXT')                     # the axes an irony inverts (the word reading flips)


def _signed_to_reading(weights: Dict[str, float]) -> Reading:
    r = Reading.zero()
    for a, v in weights.items():
        r[a][1 if v > 0 else 0] = min(1.0, abs(v))
    return r


def mix_labels(probs: Dict[str, float], table: Dict[str, Dict[str, float]] = EMO) -> Reading:
    """Probability-weighted sum of the label setpoints, pole by pole (not signed-averaged, so mixed feelings keep both poles)."""
    r = Reading.zero()
    for lab, p in probs.items():
        for a, v in table.get(lab, {}).items():
            r[a][1 if v > 0 else 0] += p * abs(v)
    for a in NT:
        r[a] = [min(1.0, r[a][0]), min(1.0, r[a][1])]
    return r


# ═════════════════════════ RAW METERS (cached) ═══════════════════════════════════
_TOK = re.compile(r"[A-Za-z']+")
PROFANE = {w for w in """fuck fucking fucked fucker fucks shit shitty bullshit bitch bitches asshole assholes bastard damn damned dammit
crap crappy dick dickhead piss pissed pissing cunt twat wanker prick bollocks slut whore douche douchebag motherfucker motherfucking
goddamn goddamned hell arse arsehole jackass dumbass dipshit shithead wtf stfu""".split()}
HEDGE = {'maybe', 'perhaps', 'possibly', 'might', 'could', 'probably', 'guess', 'seems', 'somewhat'}


def arousal_features(text: str) -> Dict[str, float]:
    letters = [c for c in text if c.isalpha()]
    caps = sum(1 for c in letters if c.isupper()) / len(letters) if len(letters) >= 4 else 0.0
    words = text.split()
    allcaps = sum(1 for w in words if len(w) > 2 and w.isalpha() and w.isupper())
    ex = text.count('!')
    qm = text.count('?')
    rep = len(re.findall(r'([!?.])\1{1,}', text))
    elong = len(re.findall(r'([a-zA-Z])\1{2,}', text))
    toks = [t.lower() for t in _TOK.findall(text)]
    prof = sum(1 for t in toks if t in PROFANE)
    you = 1 if any(t in ('you', "you're", 'your', 'youre', 'u') for t in toks) else 0
    return {'caps': caps, 'allcaps_words': allcaps, 'ex': ex, 'qm': qm, 'rep_punct': rep, 'elong': elong,
            'profane': prof, 'ntok': len(toks), 'you': you, 'hedge': sum(1 for t in toks if t in HEDGE),
            'chars': len(text)}


_EMP = None


def empath_counts(text: str) -> Dict[str, int]:
    global _EMP
    if _EMP is None:
        from empath import Empath
        _EMP = Empath()
    return {k: int(v) for k, v in _EMP.analyze(text, categories=EMPATH_CATS, normalize=False).items()}


class RawMeters:
    """Runs the models and lexicons once per text and returns plain data, so scoring can be retooled without re-running."""

    def __init__(self, load_models: bool = True, device: int = -1):
        self.models = {}
        self.vader = None
        self.act_clf = None
        if load_models:
            os.environ.setdefault('HF_HUB_OFFLINE', '1')
            os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
            from transformers import pipeline
            for key, name, k in (('go', 'SamLowe/roberta-base-go_emotions', None),
                                 ('hartmann', 'j-hartmann/emotion-english-distilroberta-base', None),
                                 ('irony', 'cardiffnlp/twitter-roberta-base-irony', None)):
                self.models[key] = pipeline('text-classification', model=name, device=device, top_k=None, truncation=True,
                                            max_length=128)
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        self.vader = SentimentIntensityAnalyzer()
        self._train_act()

    def _train_act(self):
        import nltk
        from nltk.corpus import nps_chat
        feats = lambda t: {w.lower(): True for w in _TOK.findall(t)}
        data = [(feats(p.text), p.get('class')) for p in nps_chat.xml_posts()]
        self.act_clf = nltk.NaiveBayesClassifier.train(data)
        self._act_feats = feats

    def act(self, text: str) -> Dict[str, float]:
        d = self.act_clf.prob_classify(self._act_feats(text))
        return {k: round(d.prob(k), 4) for k in d.samples()}

    def batch(self, texts: Sequence[str], batch_size: int = 32) -> List[Dict]:
        out = [{'text': t} for t in texts]
        for key, pipe in self.models.items():
            res = pipe(list(texts), batch_size=batch_size)
            for o, r in zip(out, res):
                o[key] = {x['label']: round(x['score'], 4) for x in r}
        for o in out:
            o['vader'] = self.vader.polarity_scores(o['text'])
            o['act'] = self.act(o['text'])
            o['feat'] = arousal_features(o['text'])
            o['empath'] = empath_counts(o['text'])
        return out


# ═════════════════════════ METERS: raw -> Reading ════════════════════════════════
def meter_vader(raw: Dict) -> Tuple[Reading, float]:
    c = raw['vader']['compound']
    r = Reading.zero()
    for a, w in (('DA', .6), ('5HT', .6), ('OPI', .4)):
        r[a][1 if c > 0 else 0] = abs(c) * w
    return r, 0.5


def meter_go(raw: Dict) -> Tuple[Reading, float]:
    return mix_labels(raw['go']), 1.0


def meter_hartmann(raw: Dict) -> Tuple[Reading, float]:
    return mix_labels(raw['hartmann']), 1.0


def meter_arousal(raw: Dict) -> Tuple[Reading, float]:
    f = raw['feat']
    ar = min(1.0, 0.9 * f['caps'] + 0.12 * f['allcaps_words'] + 0.15 * f['ex'] + 0.2 * f['rep_punct'] + 0.1 * f['elong'])
    r = Reading.zero()
    if ar < 0.1:
        return r, 0.0
    c = raw['vader']['compound']
    pole = 1 if c > 0.05 else 0                               # positive affect: the energised, light side; else the stress side
    for a, w in (('NE', .8), ('GLU', .5)):
        r[a][pole] = ar * w
    if pole == 0:
        r['GABA'][0] = ar * 0.5
    return r, 0.4 * ar


def meter_profanity(raw: Dict) -> Tuple[Reading, float]:
    f = raw['feat']
    r = Reading.zero()
    if not f['profane']:
        return r, 0.0
    d = min(1.0, f['profane'] / max(3, f['ntok'] * 0.25) + 0.25)
    c = raw['vader']['compound']
    if c > 0.4:                                               # "this is fucking amazing": disinhibited but warm
        r['GABA'][0] = d * 0.3; r['DA'][1] = d * 0.4
    else:
        r['GABA'][0] = d * 0.8; r['5HT'][0] = d * 0.3
        if f['you']:
            r['OXT'][0] = d * 0.6; r['NE'][0] = d * 0.5
    return r, 0.5 + 0.5 * d


def meter_act(raw: Dict) -> Tuple[Reading, float]:
    probs = raw['act']
    r = mix_labels(probs, ACT)
    return r, 0.2


# ── v2 meters (added after the v1 battery run, 2026-11-22; see Currentwork/UserState/out/REPORT_v1.md for what failed) ──
# Empath domain categories -> setpoints (care and loss that carry no emotion word: "hospital", "the last time I see her")
EMPATH_MAP = {
    'death': {'OPI': -.5, 'OXT': -.3, '5HT': -.3}, 'medical_emergency': {'NE': -.4, 'GABA': -.3}, 'pain': {'OPI': -.5},
    'suffering': {'OPI': -.5, '5HT': -.3}, 'fear': {'NE': -.5, 'GABA': -.4}, 'nervousness': {'NE': -.4, 'GABA': -.3},
    'sadness': {'5HT': -.5, 'DA': -.4}, 'anger': {'NE': -.5, 'GABA': -.5}, 'rage': {'NE': -.6, 'GABA': -.6}, 'hate': {'OXT': -.5, 'NE': -.3},
    'irritability': {'NE': -.3, 'GABA': -.3}, 'shame': {'5HT': -.5, 'NE': -.3}, 'violence': {'NE': -.4, 'GABA': -.4},
    'love': {'OXT': .5, 'OPI': .4}, 'affection': {'OXT': .5, 'OPI': .3}, 'sympathy': {'OXT': .5}, 'trust': {'OXT': .4, '5HT': .3},
    'joy': {'DA': .4, '5HT': .4}, 'cheerfulness': {'DA': .4, '5HT': .3}, 'optimism': {'DA': .4, '5HT': .4}, 'contentment': {'5HT': .5},
    'family': {'OXT': .2}, 'home': {'OXT': .1}}
EMPATH_CATS = list(EMPATH_MAP)


def meter_empath(raw: Dict) -> Tuple[Reading, float]:
    cnt = raw.get('empath') or {}
    r = Reading.zero()
    hit = 0
    for cat, n in cnt.items():
        if n:
            hit += n
            for a, v in EMPATH_MAP[cat].items():
                r[a][1 if v > 0 else 0] += min(1.0, 0.35 * n) * abs(v)
    for a in NT:
        r[a] = [min(1.0, r[a][0]), min(1.0, r[a][1])]
    return r, (0.45 if hit else 0.0)


# defensive / doubling-down stance: rule phrases (cg3-style small rules); each match adds to the stance score
STANCE = [(r"\bi (already|just) (told|said|checked|explained|wrote)\b", .6), (r"\bi told you\b", .6), (r"\bi('m| am) not (changing|going to|doing|wrong)\b", .6),
          (r"\bi don'?t need (your|any|help)\b", .6), (r"\bit('s| is) fine( the way)?\b", .4), (r"\b(not|isn'?t) (the|my) (problem|fault|issue)\b", .5),
          (r"\b(on|at) your end\b", .5), (r"\byou know (it|that|i'?m)\b", .4), (r"\bare you even (reading|listening)\b", .6), (r"\bas i (said|mentioned)\b", .4),
          (r"\b(it'?s|that'?s) not (the|a|my|what)\b", .3), (r"\bit worked before\b", .5), (r"\bi('ve| have) been (doing|at) this\b", .4),
          (r"\bwhy would i\b", .4), (r"\bi'?m not convinced\b", .4), (r"\bwhere'?s? (is |the )?(your )?(evidence|proof)\b", .4), (r"\bobviously\b", .2),
          (r"\bwhatever\b", .3), (r"\bforget it\b", .4)]
_STANCE_RE = [(re.compile(p, re.I), w) for p, w in STANCE]


def stance_score(text: str) -> float:
    return min(1.0, sum(w for rx, w in _STANCE_RE if rx.search(text)))


def meter_stance(raw: Dict) -> Tuple[Reading, float]:
    st = stance_score(raw['text'])
    r = Reading.zero()
    if st <= 0:
        return r, 0.0
    r['5HT'][0] = 0.6 * st; r['NE'][0] = 0.5 * st; r['OXT'][0] = 0.4 * st; r['GABA'][0] = 0.2 * st
    return r, 0.7 * st


# sarcasm is a PAIR: the word reading (warm) against the situation reading (cold).  Cues for the cold situation next to warm words.
IRONY_CUES = [(r"\bonly took\b", .6), (r"\bsure,? because\b", .8), (r"\boh,? (great|wonderful|good|nice|fantastic|brilliant|lovely|perfect)\b", .7),
              (r"\byeah,? (right|sure)\b", .8), (r"\b(truly|really|so) (helpful|impressive|brilliant|great|useful)\b", .4), (r"\bthanks for nothing\b", .9),
              (r"\bjust love\b", .4), (r"\bas if\b", .5), (r"like that('?s| is) ever\b", .7), (r"\bworked so well\b", .6), (r"\bgreat job,? you\b", .6),
              (r"\bfinally\b", .25), (r"\b(again|another|still)\b", .25), (r"\b(hours?|days?|weeks?|months?)\b", .2),
              (r"\b(broke|broken|crash(ed)?|typo|bug|error|fail(ed|s)?)\b", .3), (r"\bbrilliant\b", .2), (r"\bimpressive\b", .2)]
_IRONY_RE = [(re.compile(p, re.I), w) for p, w in IRONY_CUES]


def incongruity(text: str, vader_compound: float) -> float:
    """Evidence of the word/situation pair: cold-situation cues, counted fully only when the words are warm."""
    s = sum(w for rx, w in _IRONY_RE if rx.search(text))
    warm = 1.0 if vader_compound > 0.2 else 0.4 if vader_compound > -0.2 else 0.1
    return min(1.0, s) * warm


def irony_k(q: float, s: float) -> float:
    g = max(0.0, (q - 0.8) / 0.2)
    return min(1.0, s * (0.6 + 0.4 * g) + 0.15 * g * (1 if s > 0 else 0))


def apply_irony(r: Reading, q: float, s: float = 0.0) -> Reading:
    """The eye roll.  k comes mostly from the incongruity cues; the model's score only adds a little (it cannot tell 'I love this,
    it's finally working!!' from 'Thanks, that actually helped': both ~0.95, and it fires on 87% of instruction prompts).
    Applied only where the reading leans light; the affect axes blend toward the cynical setpoint."""
    k = irony_k(q, s)
    if k <= 0.05 or net(r) <= -0.02:
        return r
    out = Reading({a: list(v) for a, v in r.items()})
    cyn = EMO['cynical']
    for a in AFFECT_AXES + ('NE',):
        d, l = r[a]
        cd = abs(cyn.get(a, 0.0))
        out[a] = [d * (1 - k) + cd * k, l * (1 - k)]
    return out


METERS = {'vader': meter_vader, 'go': meter_go, 'hartmann': meter_hartmann, 'arousal': meter_arousal,
          'profanity': meter_profanity, 'act': meter_act, 'empath': meter_empath, 'stance': meter_stance}
DEFAULT_USE = ('vader', 'go', 'hartmann', 'arousal', 'profanity', 'act', 'empath', 'stance')


def score(raw: Dict, use: Iterable[str] = DEFAULT_USE, irony: bool = True) -> Reading:
    """One prompt -> one Reading: the evidence-weighted mean of the meters, pole by pole, then the irony swap."""
    num = {a: [0.0, 0.0] for a in NT}
    den = 0.0
    for name in use:
        r, w = METERS[name](raw)
        if w <= 0:
            continue
        den += w
        for a in NT:
            num[a][0] += w * r[a][0]
            num[a][1] += w * r[a][1]
    out = Reading({a: [num[a][0] / den, num[a][1] / den] if den else [0.0, 0.0] for a in NT})
    if irony and 'irony' in raw:
        out = apply_irony(out, raw['irony'].get('irony', 0.0), incongruity(raw['text'], raw['vader']['compound']))
    return out


# ═════════════════════════ THE 15-LAYER OBJECT, THE SCALAR, THE CODE ═════════════
def digits(r: Reading) -> Dict[Tuple[str, str], int]:
    """Each pole's level 0..9 (10 steps).  Keyed (NT, 'dark'|'light')."""
    d = {}
    for a in NT:
        d[(a, 'dark')] = min(LEVELS - 1, int(round(r[a][0] * (LEVELS - 1) / 0.8)))   # 0.8 of full scale reads as level 9
        d[(a, 'light')] = min(LEVELS - 1, int(round(r[a][1] * (LEVELS - 1) / 0.8)))
    return d


def sedenion(r: Reading) -> List[float]:
    """The 16 components: [e0, e1..e7 dark side, e8 cursor, e9..e15 light side].  e1..e7, e9..e15 are the levels /9; e8 is the
    cursor, the NET of the light half against the dark half; e0 = `scalar`."""
    d = digits(r)
    v = [0.0] * 16
    for (a, side), lvl in d.items():
        v[SED_INDEX[(a, side)]] = lvl / (LEVELS - 1)
    v[SED_INDEX[('', 'cursor')]] = net(r)
    v[0] = scalar(r)
    return v


def net(r: Reading) -> float:
    """Light half against dark half, halved: in [-1, 1].  Light poles add, dark poles subtract."""
    return (sum(r[a][1] for a in NT) - sum(r[a][0] for a in NT)) / len(NT)


def scalar(r: Reading, k: float = 3.0) -> float:
    """e0: the single differentiable scalar.  tanh of the net, k sets how soon it saturates.  Smooth in every pole, so it can be a
    gradient; not injective (many mixtures share a net) -- `code` is the unique one."""
    return math.tanh(k * net(r))


def code(r: Reading) -> int:
    """The unique code: the 14 pole levels as 14 base-10 digits, dark side first (violet..red) then light side (red..violet).
    Injective on the quantised state, so two different states never share it (not differentiable)."""
    d = digits(r)
    n = 0
    for lay in LAYER_ORDER:
        if lay[1] == 'cursor':
            continue
        n = n * 10 + d[lay]
    return n


def decode(n: int) -> Dict[Tuple[str, str], int]:
    s = f'{n:014d}'
    lays = [l for l in LAYER_ORDER if l[1] != 'cursor']
    return {lay: int(c) for lay, c in zip(lays, s)}


# ═════════════════════════ THE WARMING CONVERSATION ══════════════════════════════
class UserEmotionalState:
    """The user's state across a conversation.  The cold prompt assigns; each next prompt adds a reading.  The state is a running
    mean with weight 1/n until a floor (so a long conversation still moves), kept per pole as a Moments accumulator so the spread
    and the drift (slope of the last readings) are available."""

    def __init__(self, floor: float = 0.3):
        self.floor = floor
        self.n = 0
        self.state = Reading.zero()
        self.history: List[Reading] = []
        self.moments = {(a, i): BC.Moments() for a in NT for i in (0, 1)}

    def add(self, reading: Reading) -> Reading:
        self.n += 1
        w = max(self.floor, 1.0 / self.n)
        for a in NT:
            for i in (0, 1):
                self.state[a][i] = reading[a][i] if self.n == 1 else (1 - w) * self.state[a][i] + w * reading[a][i]
                self.moments[(a, i)].add(reading[a][i])
        self.history.append(Reading({a: list(v) for a, v in reading.items()}))
        return self.state

    def drift(self, window: int = 4) -> Dict[str, float]:
        """Slope per turn of the net over the last `window` readings: positive = warming toward light."""
        h = self.history[-window:]
        if len(h) < 2:
            return {'net_slope': 0.0}
        return {'net_slope': BC.ols(list(range(len(h))), [net(x) for x in h])['slope']}
