#!/usr/bin/env python3
"""
three_hearers.py -- Tao Te Ching 41 as a rule of the conversation harness.

Cody, 2026-11-22. Chapter 41 (Legge): the highest class of scholar, when he hears of the Tao, earnestly puts it into practice; the
middle class seems now to keep it and now to lose it; the lowest class laughs greatly at it. *If it were not laughed at, it would not
be fit to be the Tao.* (Read 2026-11-22 from the MIT Classics page of Legge's translation, confirmed by a web search; the wording
here is a paraphrase, not a quotation.) For the Monad: humans are absurd, stubborn, often wrong by choice, and **laughter at a
new construct is not evidence that the construct is wrong; it is expected.** The harness must not read ridicule as correction.

    DILIGENT   the user takes it up and keeps using it         -> reinforce
    WAVERING   now keeps it, now drops it                       -> hold, keep the edge, ask nothing of it
    LAUGHS     mockery, derision, laughter                      -> EXPECTED: no irritation, no retraction, no softening;
                                                                   the reaction is recorded (USER SELF) as a signature
    CORRECTS   an explicit factual correction ("no, X is Y")    -> the one reaction that can retract an edge (the teacher)

`classify_reaction(text)` labels one reaction; `ThreeHearers` keeps the history per subject and says which hearer the user is being
about it; `policy(kind)` is what the harness does: `emote_delta` (what is added to the C monad's `emote`: laughter adds 0, and never
the HARDEN/THROTTLE step), `retract` (only a correction), `hold_course`. Python first; the C side (monad_harness.c: a `reaction`
support-line kind beside `MH_S_PTOLEMY_JUDGEMENT`, and monad_emote left untouched on laughter) is to follow after testing.
"""
from __future__ import annotations
import collections
import re
from typing import Any, Deque, Dict, List, Optional

_LAUGH = re.compile(r"\b(lol|lmao|rofl|haha+|hehe+|ha ha|laugh\w*|hilarious|ridiculous|absurd|silly|what a joke|nonsense|"
                    r"you'?re joking|are you serious|that'?s funny|cute idea)\b|😂|🤣", re.I)
_ACCEPT = re.compile(r"\b(yes|yeah|right|exactly|good|great|thanks|thank you|makes sense|agreed|i'?ll try|working on it|"
                     r"i did it|it works|keep going|continue|go on)\b", re.I)
_CORRECT = re.compile(r"(^|\W)(no[,.!]|wrong|incorrect|that'?s not|that is not|not true|actually|i meant|you misunderstood)(\W|$)", re.I)


def classify_reaction(text: str) -> str:
    """'laughs' | 'corrects' | 'accepts' | 'neutral'. Laughter outranks the rest: "lol no" is laughter."""
    if _LAUGH.search(text):
        return 'laughs'
    if _CORRECT.search(text):
        return 'corrects'
    if _ACCEPT.search(text):
        return 'accepts'
    return 'neutral'


def policy(kind: str) -> Dict[str, Any]:
    """What the harness does with a reaction."""
    return {
        'laughs':   {'emote_delta': 0.0, 'retract': False, 'hold_course': True,
                     'note': 'expected (Tao 41): not irritation, not correction; recorded'},
        'corrects': {'emote_delta': 0.0, 'retract': True, 'hold_course': False,
                     'note': 'the teacher: an explicit correction may retract the edge it names'},
        'accepts':  {'emote_delta': 0.0, 'retract': False, 'hold_course': True, 'note': 'reinforce'},
        'neutral':  {'emote_delta': 0.0, 'retract': False, 'hold_course': True, 'note': 'nothing learned'},
    }[kind]


class ThreeHearers:
    """History of a user's reactions per subject (a vocabulary item, a proposal, a sentence), and which hearer they are being."""

    def __init__(self, window: int = 8):
        self.window = window
        self.history: Dict[str, Deque[str]] = collections.defaultdict(lambda: collections.deque(maxlen=window))

    def note(self, subject: str, text: str) -> Dict[str, Any]:
        kind = classify_reaction(text)
        self.history[subject].append(kind)
        out = dict(policy(kind)); out['kind'] = kind; out['hearer'] = self.hearer(subject)
        return out

    def hearer(self, subject: str) -> str:
        h = [k for k in self.history[subject] if k != 'neutral']
        if not h:
            return 'unknown'
        if h.count('laughs') > len(h) / 2:
            return 'laughs'                                  # the lowest hearer: laughs greatly
        takes, drops = h.count('accepts'), h.count('laughs') + h.count('corrects')
        if takes and drops:
            return 'wavering'                                # now keeps it, now loses it
        if takes >= 2 and not drops:
            return 'diligent'                                # takes it up and keeps at it
        return 'unknown'
