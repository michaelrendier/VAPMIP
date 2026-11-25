#!/usr/bin/env python3
"""responder.py -- the live path: one user turn in, one reply out, everything wired together.   (Cody's go, 2026-11-25)

    user turn --Harness.observe('external')--> usage store + Broca-Wernicke drift (conversation_usage)
              --SedenionWindow.read-->  StateRepass (14 poles -> heal -> mix -> cancel -> meet_then_lead)  ->  tone path
              --weave_cycle.paragraph--> orbweaver plan (radii, scaffold, capture, pivot on turbulence), tense per block from the lemniscate
                    each paragraph block --SedenionWindow.write(web=True)-->  sentence:  slots picked under the tone path (Tone7.knobs),
                    thin-margin slots re-picked along the strut (weave_cycle.web_step), word sense chosen by the word web,
                    verb group through lyndon_conjugation, probabilities = the user's own usage mixed into general English, bent by bw_correction
              --Harness.observe('internal')--> the reply is priced, completes the pair, and moves the drift for the NEXT turn.

`engine` is anything with .turn(text) -> {'conc','spread'} (prompt_to_state.PromptToState when its models are present, else the lexical tone detector).
`harness` is anything with observe(text, cls, pair_id) and .usage (harness.Harness); without one the Responder keeps its own ConversationUsage.
No claim is made here that the replies are good: the machinery is wired and measured (tests/test_responder.py), the quality is for the conversation to show.
"""
from __future__ import annotations

import os
import sys
import uuid
from typing import Any, Dict, Optional

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)

import sedenion_window as SW
import weave_cycle as WC


def default_bigram(path: Optional[str] = None) -> 'SW.Bigram':
    p = path or os.path.join(H, 'english_corpus.txt')
    return SW.Bigram().fit([open(p, encoding='utf-8', errors='ignore').read()])


def default_engine():
    """The user-state engine if its models are on disk (prompt_to_state.PromptToState); None otherwise (the window then uses detect_tone)."""
    try:
        sys.path.insert(0, os.path.join(H, 'Currentwork', 'UserState'))
        import prompt_to_state
        return prompt_to_state.PromptToState()
    except Exception:                                                          # noqa: BLE001
        return None


class Responder:
    def __init__(self, harness=None, engine=None, bigram=None, usage=None, max_sentences: int = 3, genre: str = 'paper'):
        self.harness = harness
        self.max_sentences, self.genre = max_sentences, genre
        self.usage = usage or (harness.usage if harness is not None and getattr(harness, 'usage', None) else None)
        if self.usage is None and os.environ.get('PTOL_USAGE', '1') != '0':
            import conversation_usage
            self.usage = conversation_usage.ConversationUsage()
        self.engine = engine if engine is not None else default_engine()
        import state_repass
        self.state = state_repass.StateRepass(self.engine) if self.engine is not None else None
        self.window = SW.SedenionWindow(bigram or default_bigram(), state=self.state, usage=self.usage, web=True)
        self.turns = 0

    def _observe(self, text: str, cls: str, pair: str) -> None:
        if self.harness is not None: self.harness.observe(text, cls, pair)
        elif self.usage is not None: self.usage.hear(text, cls, pair)

    def turn(self, prompt: str, tense: Optional[str] = None) -> Dict[str, Any]:
        """One user turn -> the reply and the evidence of what moved.  `tense`: None lets the web decide (lemniscate station per block)."""
        pair = uuid.uuid4().hex[:8]; self.turns += 1
        self._observe(prompt, 'external', pair)
        self.window.usage = self.usage = (self.harness.usage if self.harness is not None and getattr(self.harness, 'usage', None) else self.usage)
        self.window.read(prompt)                                              # state repass: read, heal, mix, cancel, plan
        if tense is None:
            para = WC.paragraph(self.window, prompt, genre=self.genre, max_sentences=self.max_sentences)
            reply = para['text']
        else:
            r = self.window.write(prompt, tense=tense, read=False); para = {'sentences': [r['sentence']], 'tenses': [tense]}; reply = r['sentence']
        self._observe(reply, 'internal', pair)
        st = self.state.summary() if self.state is not None else None
        return {'reply': reply, 'pair': pair, 'plan': {k: para.get(k) for k in ('tenses', 'reach', 'turbulent', 'regime', 'tense_phrases', 'monotony')},
                'state': st, 'heard': self.window.heard_tone, 'fill': self.window.fill(),
                'drift': (self.usage.last if self.usage is not None else None), 'bw_correction': (self.usage.channels.get('bw_correction') if self.usage is not None else None)}
