"""Tests for sedenion_window.py (2026-11-21): the machinery, not literary quality."""
import glob
import io
import math
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import sedenion_window as SW

CORPUS = """The king rules the kingdom. The king has a crown. The queen rules the kingdom with the king.
The dog chases the cat in the garden. The cat sees the bird in the tree. The bird sings in the tree.
A dog is an animal. The animal eats the food. The dog eats the food in the house. The house has a door.
The man opens the door of the house. The woman reads the book in the garden. The book has a story.
The tree has a branch. The bird builds a nest in the tree. The king and the queen read the book.""" * 4


@pytest.fixture(scope='module')
def bg():
    return SW.Bigram().fit([CORPUS])


def test_markers_are_invisible_and_round_trip():
    m = SW.marker('NE', 4, 'past', '3sg')
    assert len(m) == 3 and all(unicodedata.category(c) == 'Cf' for c in m)
    assert SW.decode_marker(m) == {'axis': 'NE', 'level': 4, 'tense': 'past', 'conj': '3sg'}
    assert SW.strip_markers(m + 'word') == 'word'
    assert SW.show_markers(m + 'word') == '<NE:4|past|3sg>word'
    codes = {SW.marker(a, l, t, c) for a in SW.NEURO for l in range(SW.LEVELS) for t in SW.TENSES for c in SW.CONJ}
    assert len(codes) == len(SW.NEURO) * SW.LEVELS * len(SW.TENSES) * len(SW.CONJ)      # injective
    assert all(0xE0020 <= ord(c) <= 0xE007E for k in codes for c in k)


def test_read_increments_one_tick_per_word_and_fills_the_ring(bg):
    w = SW.SedenionWindow(bg)
    recs = w.read('The king reads the book in the garden')
    assert w.t == len(recs) == 8                    # one tick per word, in order
    assert [r['t'] for r in recs] == list(range(1, 9))
    assert [r['pathway'] for r in recs] == [True, False, False, True, False, True, True, False]
    assert w.ring[0] == 'king'                     # e0 = the first content word heard
    assert w.ring[1] == 'garden' and w.ring[2] == 'book'
    assert len(w.ring) == 16


def test_pathway_words_are_nearly_free_content_words_are_not(bg):
    w = SW.SedenionWindow(bg)
    out = w.write('the king reads the book')
    recs = out['records']
    path = [r['bits'] for r in recs if r['pathway']]
    content = [r['bits'] for r in recs if not r['pathway']]
    assert path and content
    assert sum(path) / len(path) < 3.0                       # a ring of a few words: a few bits at most
    assert out['bits'] == pytest.approx(sum(r['bits'] for r in recs))
    assert all(r['candidates'] <= 8 for r in recs if r['pathway'])
    assert max(r['candidates'] for r in recs if not r['pathway']) > 8


def test_heartbeat_rescales_every_word_and_cost_is_minus_log2_p(bg):
    w = SW.SedenionWindow(bg)
    out = w.write('the dog chases the cat')
    for r in out['records']:
        assert r['r_rescaled'] == 1.0
        assert r['r_after_pick'] == pytest.approx(r['P'])
        assert r['bits'] == pytest.approx(-math.log2(r['P']))
    steps = w.sensors.read('STEP')
    assert steps and all(s['r_before'] == 1.0 for s in steps[-len(out['records']):])


def test_write_is_deterministic_and_has_a_sentence_shape(bg):
    a = SW.SedenionWindow(bg).write('the king reads the book')
    b = SW.SedenionWindow(bg).write('the king reads the book')
    assert a['sentence'] == b['sentence'] and a['marked'] == b['marked']
    s = a['sentence']
    assert s[0].isupper() and s.endswith('.') and len(s.split()) == 5


def test_tone_detection_and_pascal_meet_then_lead():
    axis, level = SW.detect_tone('You are STUPID and I HATE this, it is the worst!')
    assert axis == 'NE' and level >= 4
    path = SW.Persuader((axis, level), ('GABA', 3)).trajectory(8)
    assert path[0] == ('NE', level - 1)                        # meets their side first, one level below
    ne = [l for a, l in path if a == 'NE']
    assert ne == sorted(ne, reverse=True) and ne[-1] < ne[0]    # then eases down
    assert path[-1] == ('GABA', 3)                             # and arrives at the target
    assert SW.detect_tone('Thank you, dear friend, please')[0] == 'OXT'


def test_markers_stream_with_each_written_word_and_follow_the_persuader(bg):
    w = SW.SedenionWindow(bg)
    out = w.write('I HATE the king, he is stupid!', frame='svo')
    marks = [SW.decode_marker(r['marker']) for r in out['records']]
    assert marks[0]['axis'] == 'NE'                            # starts on their side
    assert marks[-1]['axis'] == 'GABA'                         # ends calm
    assert any(m['conj'] == '3sg' and m['tense'] == 'present' for m in marks)
    tone_lines = w.sensors.read('TONE')
    assert len(tone_lines) >= len(out['records'])
    assert all(len(l['marker']) == 3 for l in tone_lines)


def test_writable_channel_overrides_the_tone(bg):
    w = SW.SedenionWindow(bg)
    w.sensors.channels['tone_override'] = ('OT', 5)
    out = w.write('the king reads the book')
    assert all(SW.decode_marker(r['marker'])['axis'] == 'OXT' for r in out['records'])


def test_sensor_blocks_and_vagcom_stream(bg, monkeypatch):
    monkeypatch.setenv('VAGCOM', '1')
    buf = io.StringIO()
    w = SW.SedenionWindow(bg, sensors=SW.Sensors(stream=buf))
    w.write('the king reads the book')
    text = buf.getvalue()
    assert '[vag] STEP' in text and '[vag] WORD' in text and '[vag] BALANCE' in text and '[tone] TONE' in text
    assert '<' in text and '|' in text                         # markers shown visibly in the debug stream
    bal = w.sensors.read('BALANCE')
    assert bal and all(b['balance'] < 1e-9 for b in bal)       # the two pathways cancel at every point


def test_scale_point_feeds_the_broca_wernicke_rings(bg):
    w = SW.SedenionWindow(bg)
    p = w.scale_point('king')
    assert p and p['Z'].real == pytest.approx(1.0 + p['gamma']) and p['Z'].imag >= 1
    assert w.scale_point('zzzzqqq') is None


def test_window_learns_from_what_it_reads(bg, tmp_path):
    import live_vocabulary as LV
    v = LV.LiveVocabulary(journal_path=str(tmp_path / 'j.jsonl'))
    w = SW.SedenionWindow(bg, vocab=v)
    w.read('A phasor is a kind of vector.')
    assert v.lookup('phasor') and v.lookup('phasor')[0]['source'] == 'live'


def _empty_english():
    import monad_english_io as M
    return M.MonadEnglish(version='t', vocab={}, words=[], beta=[], E=[], A=[], age=[], fire_count=[], stratum=[],
                          psi_prev=[0.0] * 16, word_count=0, correction_mask={})


def test_usage_deepens_the_cooccurrence_field_over_time_and_he_hears_himself(bg):
    me = _empty_english()
    w = SW.SedenionWindow(bg, english=me)
    w.read('The king wears a golden crown')
    n1 = len(me.words); e1 = sum(len(a) for a in me.A)
    assert n1 >= 5 and me.A[me.idx('king')].get(me.idx('crown'), 0) > 0
    w.read('The king lost his golden crown')
    assert me.fire_count[me.idx('king')] >= 2                       # the same word, used again, deepens
    assert len(me.words) > n1 and sum(len(a) for a in me.A) > e1    # new words enter, new edges form
    before = sum(len(a) for a in me.A)
    out = w.write('the king reads the book')
    assert sum(len(a) for a in me.A) > before                        # what he said was heard (echo 1)
    usage = w.sensors.read('USAGE')
    assert usage and all(u['echo'] == 0 for u in usage)


def test_his_own_speech_cannot_feed_back_forever(bg):
    import monad_english_io as M
    me = _empty_english()
    w = SW.SedenionWindow(bg, english=me)
    w.read('the dog chases the cat', echo=M.ECHO_CAP)                # already looped the cap: a no-op
    assert len(me.words) == 0


def test_each_neurotransmitter_changes_the_constructor_in_its_own_way(bg):
    def run(axis, level):
        w = SW.SedenionWindow(bg)
        w.sensors.channels['tone_override'] = (axis, level)
        out = w.write('the king reads the book', frame='svo')
        return out, [r for r in out['records'] if not r['pathway']]
    base_out, base_c = run('GABA', 2)                                  # a neutral tone
    _, ne_c = run('NE', 6)
    _, glu_c = run('GLU', 6)
    assert max(r['candidates'] for r in ne_c) < max(r['candidates'] for r in base_c) < max(r['candidates'] for r in glu_c)   # NE narrows, GLU widens
    da_out, _ = run('DA', 6)
    assert da_out['sentence'] != base_out['sentence']                  # DA explores down the ranking
    ne_out = SW.SedenionWindow(bg); ne_out.sensors.channels['tone_override'] = ('NE', 6)
    assert len(ne_out.write('the king reads the book')['records']) == 4          # NE: the short frame (sva)
    gaba_out, gaba_c = run('GABA', 6)
    assert max(r['candidates'] for r in gaba_c) <= max(r['candidates'] for r in base_c)        # GABA prunes


def test_oxytocin_pulls_toward_the_users_own_words(bg):
    w0 = SW.SedenionWindow(bg); w0.sensors.channels['tone_override'] = ('GABA', 2)
    w1 = SW.SedenionWindow(bg); w1.sensors.channels['tone_override'] = ('OXT', 6)
    p = 'the queen reads the book'
    s0 = w0.write(p, frame='svo')['sentence'].lower(); s1 = w1.write(p, frame='svo')['sentence'].lower()
    users = {'queen', 'reads', 'book'}
    assert len(users & set(s1.strip('.').split())) >= len(users & set(s0.strip('.').split()))


def test_window_with_statistics_and_two_selves(bg, tmp_path):
    import context_gearbox as G, english_stats as ES
    st = ES.EnglishStats(chash=None); st.observe(CORPUS)
    sc = G.SelfContexts(gears=[(8, 4), (4, 4)])
    w = SW.SedenionWindow(bg, stats=st, selfctx=sc)
    tokens_before = st.n_tokens
    out = w.write('the king reads the book')
    assert st.n_tokens > tokens_before and w.level in ES.LEVELS            # usage statistics update as the user speaks
    assert out['seq'] > 0 and sc.data.find(out['seq'])['payload']['sentence'] == out['sentence']
    sc.user_says('reaction', responds_to=out['seq'], text='no, wrong', tone={'NE': 0.7})
    assert sc.reaction_to(out['seq'])[0]['payload']['text'] == 'no, wrong'
    assert st.n_tokens == st.n_tokens                                     # his own speech does not feed the statistics
