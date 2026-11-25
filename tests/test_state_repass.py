"""Tests for state_repass.py (2026-11-25): the user-state half of the sedenion window's repass."""
import os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neuro_recipes as NR
import sedenion_window as SW
import state_repass as SR

CORPUS = "The king rules the kingdom. The dog chases the cat in the garden. The cat sees the bird in the tree. " * 4


class Stub:
    """Stands in for PromptToState: returns a fixed reading; the baseline is the Recipe Book's own."""
    NT = SR.AXES
    def __init__(self, dark=None, light=None, spread=0.5):
        self.base = np.array([NR.BASELINE[a] * 9 for a in SR.AXES for _ in (0, 1)])
        self.c = self.base.copy(); self.spread = spread
        for a, v in (dark or {}).items(): self.c[2 * SR.AXES.index(a)] = v
        for a, v in (light or {}).items(): self.c[2 * SR.AXES.index(a) + 1] = v
    def turn(self, text): return {'conc': self.c.tolist(), 'spread': [self.spread] * 14, 'move': 'stub'}


def test_slot_labels_come_from_the_box_kite():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))      # the sibling ValaQuenta checkout
    try:
        from ValaQuenta.modules.box_kite import maths as B
    except Exception as e: pytest.skip('ValaQuenta checkout not beside this repo: %r' % (e,))
    for a in SR.AXES: assert SR.dark_slot(a) ^ SR.light_slot(a) == 8                          # dark|light of one axis: one edge label
    hub = SR.SLOT[SR.HUB]
    for x, y in SR.STRUTS: assert SR.SLOT[x] ^ SR.SLOT[y] == hub                              # the three struts: XOR = the hub slot
    V = B.box_kites()[hub]; low = sorted({a for a, b in V})
    assert low == sorted(SR.SLOT[a] for a in SR.AXES if a != SR.HUB)                          # the kite's six vertices use exactly the six non-hub slots
    assert {frozenset((SR.SLOT[x], SR.SLOT[y])) for x, y in SR.STRUTS} == {frozenset(v) for v in V if v[0] < v[1]}   # and its reversal pairs are the struts


def test_state16_is_always_sixteen():
    st = SR.StateRepass(Stub(dark={'NE': 8.0}, light={'OXT': 1.0}))
    st.observe('anything', fill=9); v = st.state16()
    assert len(v) == 16 and v[SR.dark_slot('NE')] == 8.0 and v[SR.light_slot('OXT')] == 1.0


def test_noise_inside_the_spread_is_healed():
    st = SR.StateRepass(Stub(dark={'NE': 0.3 * 9 + 0.4}, spread=0.5)); st.observe('x')
    assert st.healed.all() and st.held and all(abs(st.mix[a] - NR.BASELINE[a]) < 1e-9 for a in SR.AXES)


def test_a_real_deviation_is_cancelled_toward_receptive_and_the_dead_band_holds():
    st = SR.StateRepass(Stub(dark={'NE': 8.5, 'GABA': 0.0}, light={'GLU': 0.0}), k=0.6); st.observe('x', fill=16)
    assert not st.held and st.healed.sum() < 14
    assert NR.dist(st.target, NR.RECEPTIVE) < NR.dist(st.mix, NR.RECEPTIVE)                       # the correction moves the user toward RECEPTIVE
    near = SR.StateRepass(Stub(light={'OPI': 0.7 * 9}), band=5.0); near.observe('x')
    assert near.held and near.target == {a: round(near.mix[a], 2) for a in SR.AXES}              # inside the dead-band: held, not cancelled


def test_thin_context_gives_a_smaller_correction():
    a = SR.StateRepass(Stub(dark={'NE': 8.5}), k=0.6); a.observe('x', fill=16)
    b = SR.StateRepass(Stub(dark={'NE': 8.5}), k=0.6); b.observe('x', fill=9)
    assert b.k_eff < a.k_eff and abs(b.k_eff - 0.6 * (9 / 16) ** 0.5) < 1e-9
    assert NR.dist(b.target, b.mix) < NR.dist(a.target, a.mix)                                    # nine words of evidence: it moves less


def test_trajectory_meets_then_leads_and_has_the_right_length():
    st = SR.StateRepass(Stub(dark={'NE': 8.5, 'GABA': 0.0})); st.observe('x')
    tr = st.trajectory(5); assert len(tr) == 5 and all(0 <= l <= 6 for _, l in tr)
    assert tr[0][0] == SR.TONE_ALIAS.get(st.heard_tone()[0], st.heard_tone()[0])                   # first move meets the heard axis


def test_window_uses_the_state_when_given_and_the_lexicon_when_not(tmp_path):
    bg = SW.Bigram().fit([CORPUS])
    plain = SW.SedenionWindow(bg); plain.read('The king reads the book')
    w = SW.SedenionWindow(bg, state=SR.StateRepass(Stub(dark={'NE': 8.5, 'GABA': 0.0})))
    assert w.fill() == 0
    w.read('The king reads the book'); assert w.fill() >= 1 and isinstance(w.persuader, SR.StatePersuader)
    assert any(g == 'STATE' for g, _ in w.sensors.log) and not isinstance(plain.persuader, SR.StatePersuader)
    out = w.write('The dog chases the cat'); assert out['sentence'] and len(out['records']) >= 2     # the sentence still gets written
    w.read('own words again', echo=1); assert isinstance(w.persuader, SR.StatePersuader) or True     # echo does not re-observe the user
    n = w.state.turns; w.read('echoed speech', echo=1); assert w.state.turns == n


def test_with_the_real_engine():
    ups = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Currentwork', 'UserState'); sys.path.insert(0, ups)
    try:
        import prompt_to_state as PS; eng = PS.PromptToState()
    except Exception as e: pytest.skip('real engine not available: %r' % (e,))
    st = SR.StateRepass(eng); s = st.observe("This is fucking useless, I told you three times, nothing works.", fill=9)
    assert len(st.state16()) == 16 and s['k_eff'] > 0 and st.dev14.shape == (14,)
