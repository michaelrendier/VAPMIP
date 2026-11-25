"""Tests for scaled_boxkite_orbweaver_monad.py (2026-11-25): the rebuilt orbweaver bench."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import sedenion_window as SW
import scaled_boxkite_orbweaver_monad as S
import boxkite_orbweaver_monad as OW
import responder as R

T1 = "The king rules the kingdom and the dog chases the cat in the garden. I told him 3 times in 2024 and x2."
T2 = "Why does the bridge keep breaking when the river floods the valley and the farmers rebuild the road every spring?"
T3 = "The painter mixes the colour and the sculptor carves the stone while the musician plays the song in the temple."


@pytest.fixture(scope='module')
def bg(): return R.default_bigram()


def make(bg, t, **kw):
    w = SW.SedenionWindow(bg, web=True); w.read(t); return S.ScaledOrbWeaverMonad(w, **kw)


@pytest.mark.parametrize('t', [T1, T2, T3])
def test_every_audit_check_holds(bg, t):
    m = make(bg, t); c = m.compose(t); a = m.audit(c)
    assert c.text and all(a.values()), {k: v for k, v in a.items() if not v}


def test_numbers_are_reported_apart_and_never_spoken(bg):
    m = make(bg, T1); c = m.compose(T1)
    assert [n.text for n in c.numbers] == ['3', '2024', 'x2'] and not any(ch.isdigit() for ch in c.text)


def test_the_plan_is_deterministic_across_runs_unlike_the_hash_sniffer(bg):
    a = make(bg, T2).compose(T2); b = make(bg, T2).compose(T2)
    assert a.text == b.text and a.plan == b.plan and a.plan['directions']


def test_the_sentence_vector_is_the_sum_of_real_word_vectors(bg):
    m = make(bg, T3); r = m.read_input(T3)
    import weave_cycle as WC
    tot = [0] * 19
    for w, i in r['infos'].items(): tot = [x + y for x, y in zip(tot, WC._store(m.win).vector_of(i['sense']))]
    assert r['rv'] == tot and any(tot) and set(r['infos']) <= set(r['words'])


def test_the_child_repeats_the_speakers_words(bg):
    m = make(bg, T1); c = m.compose(T1)
    said = set(c.text.lower().replace(',', '').split()); heard = set(T1.lower().replace('.', '').split())
    assert said & heard - SW.CLOSED, 'the reply shares no content word with the speaker'


def test_turbulence_makes_a_pivot_with_the_antagonist_tone_when_there_are_two_radii(bg):
    m = make(bg, T3, seed=7)
    c = m.compose(T3, max_pieces=8)
    if c.plan['turbulent'] and len(c.plan['directions']) > 1:
        pv = [p for p in c.pieces if p.kind == 'pivot']
        assert pv and pv[0].tone[0] in ('GLU', 'GABA', 'DA', '5HT', 'NE', 'OXT') and pv[0].connective in OW._CONNECTIVES['reverse']
    else:
        assert all(p.kind != 'pivot' for p in c.pieces)


def test_tense_follows_depth_when_the_web_is_deep(bg):
    m = make(bg, T3); c = m.compose(T3, scale=3.0, max_pieces=8)
    assert c.plan['reach'] >= 2 and {'past', 'future'} & set(c.plan['tenses'])
    assert [p.tense for p in c.pieces if p.kind == 'paragraph'][0] == 'past'                     # the deepest loop is the past lobe
