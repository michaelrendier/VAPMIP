"""Tests for responder.py (2026-11-25): the wired live path, with a stub user-state engine and a private usage store."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pytest
import neuro_recipes as NR
import responder as R
import conversation_usage as CU
import state_repass as SR


class Stub:
    NT = SR.AXES
    def __init__(self): self.base = np.array([NR.BASELINE[a] * 9 for a in SR.AXES for _ in (0, 1)]); self.n = 0
    def turn(self, text):
        c = self.base.copy()
        if 'broken' in text: c[2 * SR.AXES.index('NE')] = 8.5; c[2 * SR.AXES.index('GABA')] = 0.0
        return {'conc': c.tolist(), 'spread': [0.5] * 14, 'move': 'stub'}


class FakeHarness:
    """The two things Responder needs from Harness: observe(text, cls, pair) and .usage."""
    def __init__(self, usage): self.usage = usage; self.seen = []
    def observe(self, text, cls='external', pair_id=None):
        self.seen.append((cls, pair_id, text)); self.usage.hear(text, cls, pair_id)


BG = "The king rules the kingdom. The dog chases the cat in the garden. The cat sees the bird in the tree. " * 6


def test_one_turn_goes_through_every_stage(tmp_path):
    from sedenion_window import Bigram
    cu = CU.ConversationUsage(str(tmp_path)); h = FakeHarness(cu)
    r = R.Responder(harness=h, engine=Stub(), bigram=Bigram().fit([BG]), max_sentences=3)
    out = r.turn('The king rules the kingdom and everything is broken again.')
    assert out['reply'] and [c for c, _, _ in h.seen] == ['external', 'internal'] and h.seen[0][1] == h.seen[1][1] == out['pair']      # observed as a pair
    assert out['state']['axis'] and not out['state']['held']                                       # the user state was read and re-planned
    assert set(out['plan']['tenses']) <= {'past', 'present', 'future'}                              # tense came from the orbweaver's lemniscate
    assert out['drift'] is not None and 'bw_correction' in cu.channels and cu.store.n_obs > 0       # the reply was priced and the drift moved
    assert out['fill'] <= 16


def test_second_turn_uses_the_correction_and_the_explicit_tense_override(tmp_path):
    from sedenion_window import Bigram
    cu = CU.ConversationUsage(str(tmp_path)); r = R.Responder(harness=FakeHarness(cu), engine=Stub(), bigram=Bigram().fit([BG]))
    r.turn('The king rules the kingdom.'); out = r.turn('The dog chases the cat in the garden.', tense='past')
    assert out['reply'] and out['plan']['tenses'] == ['past'] and r.turns == 2


def test_without_an_engine_the_window_still_answers(tmp_path, monkeypatch):
    from sedenion_window import Bigram
    monkeypatch.setattr(R, 'default_engine', lambda: None)
    r = R.Responder(harness=FakeHarness(CU.ConversationUsage(str(tmp_path))), bigram=Bigram().fit([BG]))
    assert r.state is None and r.turn('The king rules the kingdom.')['reply']
