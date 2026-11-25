"""Tests for weave_cycle.py (2026-11-25): the orbweaver step at word, sentence and paragraph scale."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import sedenion_window as SW
import weave_cycle as WC
import tone_chord as TC

CORPUS = "The king rules the kingdom. The dog chases the cat in the garden. The cat sees the bird in the tree. The woman reads the book in the garden. " * 5


@pytest.fixture(scope='module')
def bg():
    return SW.Bigram().fit([CORPUS])


def test_turbulence_rule_is_the_orbweavers():
    import boxkite_orbweaver_monad as B
    for v in ([5, 4, 3, 0], [9, 2, 1], [1, 1, 1, 1], [0, 0], [3, 3, 0, 2, 1]):
        assert WC.turbulent(v) == B.OrbWeaverMonad._turbulence(list(v))


def test_web_step_keeps_the_sharper_pick_and_never_reverses_a_calm_flow():
    calm = WC.web_step('x', {'a': 9, 'b': 1, 'c': 1}, lambda: ('b', {'b': 1.0}))
    assert not calm['turbulent'] and not calm['reversed'] and calm['chosen'] == 'a'
    sharper = WC.web_step('x', {'a': 3, 'b': 3, 'c': 2}, lambda: ('c', {'c': 9, 'a': 1}))
    assert sharper['turbulent'] and sharper['reversed'] and sharper['chosen'] == 'c'
    blunter = WC.web_step('x', {'a': 3, 'b': 3, 'c': 2}, lambda: ('c', {'c': 3, 'a': 3, 'b': 3}))
    assert not blunter['reversed'] and blunter['chosen'] == 'b'      # a tie among the leaders: the later name wins, as in max((value, name))


def test_struts_are_the_three_antagonist_pairs_and_the_hub_has_none():
    assert {frozenset(p) for p in WC.STRUT_PARTNER.items()} == {frozenset(('GLU', 'GABA')), frozenset(('DA', '5HT')), frozenset(('NE', 'OXT'))}
    assert 'OPI' not in WC.STRUT_PARTNER


def test_opi_is_no_longer_ignored_by_tone7():
    t = TC.Tone7.from_axis('OPI', 1.0)
    assert t.levels['CB1'] == 1.0 and t.knobs()['relax_rate'] > TC.Tone7().knobs()['relax_rate']


def test_word_web_reads_senses_and_spokes_without_touching_the_window(bg):
    w = SW.SedenionWindow(bg); before = list(w.ring)
    r = WC.word_web(w, 'bank', ['river', 'water', 'fish'])
    assert r and r['senses'] > 3 and r['sense'].startswith('bank.') and r['spokes'] and w.ring == before


def test_the_window_with_web_on_emits_word_and_sentence_events_and_stays_deterministic(bg):
    a = SW.SedenionWindow(bg, web=True); b = SW.SedenionWindow(bg, web=True)
    ra = a.write('the king reads the book in the garden'); rb = b.write('the king reads the book in the garden')
    assert ra['sentence'] == rb['sentence'] and ra['sentence']
    ev = a.sensors.read('WEB'); assert ev and {e['scale'] for e in ev} >= {'word'}


def test_tense_follows_the_lemniscate_and_the_verb_group(bg):
    w = SW.SedenionWindow(bg)
    past = w.write('the king rules the kingdom', tense='past')
    fut = w.write('the king rules the kingdom', tense='future perfect')
    assert 'will have' in fut['sentence'] and SW.show_markers(fut['marked']).count('|future|') >= 1
    assert '|past|' in SW.show_markers(past['marked'])
    auto = w.write('the king rules the kingdom', tense='auto', depth=3, reach=3)
    assert '|past|' in SW.show_markers(auto['marked'])


def test_paragraph_scale_plans_with_the_orbweaver_and_writes_with_the_window(bg):
    w = SW.SedenionWindow(bg, web=True); w.read('The king rules the kingdom and the dog chases the cat')
    p = WC.paragraph(w, 'The king rules the kingdom and the dog chases the cat', max_sentences=3)
    assert 1 <= len(p['sentences']) <= 3 and p['text'] and len(p['tenses']) == len(p['sentences'])
    assert set(p['tenses']) <= {'past', 'present', 'future'} and p['monotony']['repeats'] >= 1
