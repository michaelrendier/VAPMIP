"""Tests for english_stats.py: usage frequency as one data object; granularity by level; no phonetics."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import english_stats as ES

TEXT = ("the king rules the kingdom . the queen rules the kingdom with the king . the dog chases the cat in the garden . "
        "the cat sees the bird in the tree . the bird sings in the tree . the king reads the book in the garden . ") * 6


@pytest.fixture(scope='module')
def ch():
    return ES.ContextHash()


def test_context_hash_gives_the_final_number_for_a_word(ch):
    o = ch.of('king')
    assert o and o['class'] >= 1 and o['gamma'] is not None and o['addr'] > 1
    assert ch.of('zzzzqq') is None
    assert ch.of('tree')['class'] == ch.of('tree')['class']


def test_frequency_not_just_cooccurrence(ch):
    s = ES.EnglishStats(chash=ch); s.observe(TEXT)
    assert s.bigram[('the', 'king')] > s.bigram[('the', 'dog')]               # counts, not max-merged presence
    assert s.p('king', 'the') > s.p('dog', 'the') > s.p('zebra', 'the')


def test_the_mixture_is_a_distribution_over_the_vocabulary(ch):
    s = ES.EnglishStats(chash=ch); s.observe(TEXT)
    tot = sum(s.p(w, 'the') for w in s.unigram)
    assert 0.9 <= tot <= 1.05


def test_it_learns_bits_fall_with_teaching_and_the_class_part_helps_unseen_pairs(ch):
    held = "the queen reads the book in the garden . the king sees the bird in the tree ."
    s0 = ES.EnglishStats(chash=ch); s0.observe(TEXT[:200])
    s1 = ES.EnglishStats(chash=ch); s1.observe(TEXT)
    b0, n0 = s0.bits(held); b1, n1 = s1.bits(held)
    assert b1 / n1 < b0 / n0                                                      # taught more: fewer bits per word
    nohash = ES.EnglishStats(); nohash.observe(TEXT)
    assert s1.bits(held)[0] <= nohash.bits(held)[0] * 1.05                        # the context-class part does not hurt


def test_levels_are_rank_cuts_and_a_rare_word_is_spoken_from_its_class(ch):
    s = ES.EnglishStats(chash=ch); s.observe(TEXT)
    s.level_cut['child'] = 3
    assert len(s.vocabulary_at('child')) == 3 and len(s.vocabulary_at('specialist')) == len(s.unigram)
    assert s.p('bird', 'the', 'child') <= s.p('bird', 'the', 'specialist')       # beyond the cut: no word-pair evidence
    assert s.p('the', 'in', 'child') > 0


def test_level_for_the_users_vocabulary(ch):
    s = ES.EnglishStats(chash=ch, rank_levels=(5, 10, 15)); s.observe(TEXT * 3 + " zephyr quixotic obfuscation . ")
    assert s.level_for('the king rules the kingdom') == 'child'
    assert s.level_for('quixotic obfuscation zephyr') == 'specialist'


def test_poll_is_plain_data_and_there_is_no_phonetics(ch):
    s = ES.EnglishStats(chash=ch); s.observe(TEXT)
    p = s.poll()
    assert set(p) >= {'tokens', 'vocabulary', 'pairs', 'classes_seen', 'levels', 'top_words', 'mix', 'granularity'}
    assert p['tokens'] > 100 and p['levels']['specialist'] == p['vocabulary']
    import inspect
    assert 'phon' not in inspect.getsource(ES).lower().replace('phonetics left out', '').replace('phonetics', '')
