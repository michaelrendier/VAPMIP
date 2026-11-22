import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import three_hearers as TH


def test_laughter_is_expected_not_correction():
    for s in ('lol that is absurd', 'haha what a joke', '😂', "Are you serious?", 'lol no'):
        assert TH.classify_reaction(s) == 'laughs'
    p = TH.policy('laughs')
    assert p['emote_delta'] == 0.0 and p['retract'] is False and p['hold_course'] is True


def test_only_an_explicit_correction_retracts():
    assert TH.classify_reaction('No, a phasor is not a vector.') == 'corrects'
    assert TH.policy('corrects')['retract'] is True
    assert all(TH.policy(k)['retract'] is False for k in ('laughs', 'accepts', 'neutral'))
    assert TH.classify_reaction('thanks, that makes sense') == 'accepts'
    assert TH.classify_reaction('the weather is mild') == 'neutral'


def test_three_hearers_over_time():
    h = TH.ThreeHearers()
    for s in ('yes exactly', 'good, continue'):
        h.note('a', s)
    assert h.hearer('a') == 'diligent'
    for s in ('yes', 'lol no', 'ok great'):
        h.note('b', s)
    assert h.hearer('b') == 'wavering'
    for s in ('haha', 'ridiculous', 'lol'):
        h.note('c', s)
    assert h.hearer('c') == 'laughs'
    assert h.hearer('never seen') == 'unknown'


def test_the_harness_notes_reactions_and_never_raises_emote_on_laughter():
    import harness as H
    hs = H.Harness()
    hs._fifo_write = lambda msg: True                 # no daemon in the test
    hs.observe('lol that is absurd, a word that learns itself', 'external', 'p1')
    r = hs.last_reaction
    assert r['kind'] == 'laughs' and r['emote_delta'] == 0.0 and r['retract'] is False
    hs.observe('No, that is wrong.', 'external', 'p2')
    assert hs.last_reaction['retract'] is True
    hs.observe('assistant prose here.', 'internal', 'p2')           # his own speech is not a reaction
    assert hs.last_reaction['kind'] == 'corrects'
