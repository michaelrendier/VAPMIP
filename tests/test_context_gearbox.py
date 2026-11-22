"""Tests for context_gearbox.py: lossless FIFO odometer compaction; DATA SELF and USER SELF."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import context_gearbox as G


def clock():
    n = [0]
    def tick():
        n[0] += 1
        return '2026-11-21T00:%02d:%02d.000000+00:00' % (n[0] // 60, n[0] % 60)
    return tick


def ev(i, text='the king rules the kingdom'):
    return {'seq': i, 't': '2026-11-21T00:00:%02d+00:00' % (i % 60), 'kind': 'say', 'who': 'ptolemy', 'thread': i,
            'payload': {'text': '%s number %d' % (text, i), 'tone': {'GABA': 0.4, 'NE': 0.1}}}


def test_odometer_carries_fifo_and_is_lossless():
    g = G.Gearbox('data', gears=[(8, 4), (4, 4), (4, 4)])
    for i in range(1, 201):
        g.push(ev(i))
    assert len(g.gears[0]) <= 8 and len(g.gears[1]) <= 4 and len(g.gears[2]) <= 4
    assert sum(len(x) for x in g.gears[1:]) > 0
    allv = g.all_events()
    assert [e['seq'] for e in allv] == list(range(1, 201))                  # nothing lost, order kept (FIFO)
    assert allv[0] == ev(1) and allv[-1] == ev(200)                          # exact originals
    assert g.gears[3][0]['span'][0] == 1                                     # the oldest block sits in the deepest gear


def test_compaction_shrinks_storage_and_digests_are_readable():
    g = G.Gearbox('data', gears=[(8, 4), (4, 4), (4, 4)])
    for i in range(1, 401):
        g.push(ev(i))
    s = g.sizes()
    assert s['ratio'] > 1.5 and s['total_stored'] < s['raw_bytes']
    d = g.digests()[3][0]
    assert d['n'] >= 16 and 'king' in d['terms'] and d['tone']['GABA'] == pytest.approx(0.4)
    assert d['seq'][0] == 1


def test_tunable_ratio_changes_compactness():
    a = G.Gearbox('x', gears=[(8, 2)]); b = G.Gearbox('x', gears=[(8, 8)])
    for i in range(1, 129):
        a.push(ev(i)); b.push(ev(i))
    assert [e['seq'] for e in a.all_events()] == [e['seq'] for e in b.all_events()] == list(range(1, 129))
    assert len(a.gears[1]) > len(b.gears[1])                                  # a finer gear ratio holds more, smaller blocks


def test_find_and_tamper_detection():
    g = G.Gearbox('x', gears=[(4, 2), (4, 2)])
    for i in range(1, 60):
        g.push(ev(i))
    assert g.find(3) == ev(3) and g.find(59) == ev(59) and g.find(999) is None
    rec = next(r for r in g.gears[1] if 'blob' in r)
    bad = dict(rec); bad['hash'] = '0' * 64
    with pytest.raises(ValueError):
        g.reconstruct(bad)


def test_ledger_replay_rebuilds_the_same_gears(tmp_path):
    p = str(tmp_path / 'l.jsonl')
    a = G.Gearbox('data', gears=[(6, 3), (3, 3)], ledger=p)
    for i in range(1, 80):
        a.push(ev(i))
    b = G.Gearbox('data', gears=[(6, 3), (3, 3)])
    assert b.replay(p) == 79
    assert [[r.get('hash', r.get('seq')) for r in g] for g in a.gears] == [[r.get('hash', r.get('seq')) for r in g] for g in b.gears]


def test_two_selves_reaction_and_thread_survive_compaction():
    sc = G.SelfContexts(gears=[(4, 2), (4, 2)], clock=clock())
    first = sc.ptolemy('say', text='the king rules the kingdom')
    r1 = sc.user_says('reaction', responds_to=first, text='no that is wrong', tone={'NE': 0.8})
    second = sc.ptolemy('say', responds_to=r1, text='the queen rules the kingdom')
    r2 = sc.user_says('reaction', responds_to=second, text='better, thanks', tone={'OXT': 0.6})
    for i in range(60):                                               # a long time goes by: everything is compacted
        s = sc.ptolemy('say', text='filler sentence %d' % i)
        sc.user_says('reaction', responds_to=s, text='ok')
    assert sc.data.find(first) is not None and not any(e['seq'] == first for e in sc.data.gears[0])
    reaction = sc.reaction_to(first)
    assert len(reaction) == 1 and reaction[0]['payload']['text'] == 'no that is wrong'
    th = sc.thread(first)
    assert [e['seq'] for e in th] == [first, r1, second, r2]            # the whole train of thought, from its first event
    assert {e['who'] for e in th} == {'ptolemy', 'user'}


def test_shortcuts_are_canonical_environment_lines():
    sc = G.SelfContexts(gears=[(4, 2), (4, 2)], clock=clock())
    for i in range(30):
        s = sc.ptolemy('say', text='the king reads a book %d' % i)
        sc.user_says('reaction', responds_to=s, text='good', tone={'OXT': 0.5})
    lines = sc.export_lines()
    keys = [l.split('=')[0] for l in lines]
    assert 'export CTX_DATA_G0' in keys and 'export CTX_USER_G1' in keys
    assert any('king' in l for l in lines)
