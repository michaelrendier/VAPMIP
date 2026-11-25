"""Tests for numeric.py (2026-11-25): numbers are not words."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numeric as N
import conversation_usage as CU
import sedenion_window as SW

T = "I told you 3 times, 2.5% of $1,200 in the 4th row, x2 and h264, -7 degrees, 1,000,000 words. version 3.10.3 ok"


def test_split_takes_every_numeral_and_code_out():
    w, ns = N.split(T)
    assert not any(c.isdigit() for c in w) and 'times' in w and 'degrees' in w
    assert [(n.text, n.kind) for n in ns] == [('3', 'integer'), ('2.5%', 'percent'), ('$1,200', 'currency'), ('4th', 'ordinal'), ('x2', 'code'), ('h264', 'code'),
                                               ('-7', 'signed'), ('1,000,000', 'integer'), ('3.10.3', 'code')]
    assert [n.value for n in ns][:3] == [3.0, 2.5, 1200.0] and ns[6].value == -7.0 and ns[7].value == 1000000.0 and ns[8].value is None


def test_words_with_no_digits_are_untouched():
    t = 'The king rules the kingdom.'; assert N.split(t) == (t, [])


def test_the_usage_store_never_counts_a_number_as_a_lemma_and_the_number_channel_does(tmp_path):
    cu = CU.ConversationUsage(str(tmp_path)); cu.hear('I told you 3 times in 2024 that x2 is broken.', 'external', 'p')
    assert not any(any(c.isdigit() for c in l) for l in cu.store.lemmas) and cu.store.lemmas.get('told')
    assert cu.numbers.n == 3 and cu.numbers.kinds['integer'] == 2 and cu.numbers.kinds['code'] == 1
    j = json.load(open(os.path.join(str(tmp_path), 'numbers.json'))); assert j['n'] == 3
    again = CU.ConversationUsage(str(tmp_path)); assert again.numbers.n == 3                     # persisted
    cu.hear('Committed docs 99 and 100.', 'document'); assert cu.numbers.n == 3                  # documents never feed the user's number channel


def test_the_window_reads_numbers_on_their_own_channel_and_places_no_digit(tmp_path):
    bg = SW.Bigram().fit(["The king rules the kingdom. The dog chases the cat. " * 5]); w = SW.SedenionWindow(bg)
    recs = w.read('The king told me 3 times in 2024 about x2')
    assert all(not any(c.isdigit() for c in r['word']) for r in recs) and not any(any(c.isdigit() for c in (x or '')) for x in w.ring)
    ev = w.sensors.read('NUM'); assert ev and [t for t, _ in ev[0]['numbers']] == ['3', '2024', 'x2']
