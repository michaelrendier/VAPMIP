"""Tests for the Lyndon verb group (lyndon_conjugation.py, 2026-11-25) and tenseplan.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import lyndon_conjugation as LC
import tenseplan as TP
import sedenion_window as SW

CASES = [('present', 'sees'), ('past', 'saw'), ('future', 'will see'), ('conditional', 'would see'), ('perfect', 'has seen'), ('progressive', 'is seeing'),
         ('past perfect', 'had seen'), ('past progressive', 'was seeing'), ('future perfect', 'will have seen'), ('future progressive', 'will be seeing'),
         ('present perfect progressive', 'has been seeing'), ('past perfect progressive', 'had been seeing'), ('imperative', 'see')]


@pytest.mark.parametrize('spec,out', CASES)
def test_the_verb_group_realises_every_tense(spec, out):
    assert ' '.join(g['word'] for g in LC.conjugates('see', spec)) == out


def test_the_core_is_still_correct():
    assert LC.verify(8)['failures'] == 0 and LC.verify(8)['counts_match_formula']


def test_a_group_is_a_non_increasing_word_and_its_factors_are_its_primes():
    for spec, _ in CASES:
        w = LC.verb_group(spec)
        assert list(w) == sorted(w, reverse=True)                                  # the shape Chen-Fox-Lyndon factorisations take
        f = LC.duval(w); assert tuple(x for l in f for x in l) == w and all(LC.is_lyndon(l) for l in f)
        assert len(LC.factors(spec)) == len(w)                                      # Omega = the number of factors
    assert LC.factors('past perfect progressive') == ['TENSE', 'PERF', 'PROG', 'V']


def test_factor_algebra_divides_gcd_lcm():
    assert LC.divides('perfect', 'past perfect progressive') and not LC.divides('future', 'past')
    assert LC.gcd('past perfect', 'past progressive') == LC.verb_group('past')
    assert LC.lcm('past perfect', 'past progressive') == LC.verb_group('past perfect progressive')


def test_agreement_irregulars_and_be_have():
    f = lambda l, s, n='sg', p=3: ' '.join(g['word'] for g in LC.conjugates(l, s, n, p))
    assert f('be', 'present', 'sg', 1) == 'am' and f('be', 'past', 'pl', 3) == 'were' and f('be', 'perfect') == 'has been'
    assert f('go', 'past') == 'went' and f('go', 'present', 'pl') == 'go' and f('have', 'past perfect') == 'had had'
    assert f('walk', 'future perfect progressive') == 'will have been walking'


def test_the_frame_gives_the_two_marker_codes_and_they_are_valid_tags():
    for spec, _ in CASES:
        fr = LC.inflection_frame(spec, 'see')
        assert fr['tense'] in SW.TENSES and fr['conj'] in SW.CONJ
        SW.marker('GABA', 3, fr['tense'], fr['conj'])
    assert LC.inflection_frame('past perfect', 'walk')['conj'] == 'pastpart' and LC.inflection_frame('future', 'walk')['tense'] == 'future'


def test_the_tense_cycle_rotation_and_a_paragraphs_tense_stream():
    assert [LC.rotate_tense(t) for t in LC.TENSE_CYCLE] == ['present', 'future', 'past'] and LC.rotate_tense('past', 3) == 'past'
    assert LC.tense_monotony(['past'] * 4)['flat'] and not LC.tense_monotony(['past', 'present', 'future'])['flat']
    assert LC.tense_monotony(['past', 'present', 'past', 'present'])['root'] == ['past', 'present']
    assert LC.tense_phrases(['future', 'past', 'present'])[0] == (2,)


def test_tenseplan_matches_the_orbweaver_and_mirrors_the_user():
    import boxkite_orbweaver_monad as B
    for reach in range(1, 6):
        for depth in range(1, reach + 1):
            assert TP.STATION[B.OrbWeaverMonad._tense(depth, reach)] == TP.lemniscate_tense(depth, reach)
    assert TP.mirror_tense('I walked home yesterday') == 'past' and TP.mirror_tense('We will go') == 'future' and TP.mirror_tense('I walk') == 'present'
    assert TP.resolve('auto', '', 3, 3) == 'past' and TP.resolve('auto', '', 1, 3) == 'future' and TP.resolve(None) == 'present'
