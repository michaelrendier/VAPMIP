import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pytest
import tone_chord as TC


def test_every_tense_and_conjugation_key_decodes_exactly():
    lv = {a: (i % 7) / 6 for i, a in enumerate(TC.NEURO7)}
    for t, c in itertools.product(range(8), range(8)):
        d = TC.decode(TC.encode(lv, t, c))
        assert d['tense'] == t and d['conj'] == c
        assert d['levels'] == pytest.approx({a: round(v * 6) / 6 for a, v in lv.items()})


def test_all_level_combinations_of_two_axes_and_noise():
    rng = np.random.default_rng(0)
    for a, b in ((0, 0), (6, 1), (3, 5), (6, 6)):
        lv = {x: 0.0 for x in TC.NEURO7}; lv['NE'] = a / 6; lv['GABA'] = b / 6
        x = TC.encode(lv, 5, 2) + rng.normal(0, 0.2, TC.N)                  # heavy noise, still identified
        d = TC.decode(x)
        assert d['tense'] == 5 and d['conj'] == 2
        assert abs(d['levels']['NE'] - a / 6) < 1e-9 and abs(d['levels']['GABA'] - b / 6) < 1e-9


def test_knobs_move_in_the_documented_direction():
    base = TC.Tone7().knobs()
    up = lambda a: TC.Tone7.from_axis(a, 1.0).knobs()
    assert up('DA')['novelty_rank'] > base['novelty_rank']
    assert up('5HT')['coherence'] > base['coherence']
    assert up('NE')['pool_size'] < base['pool_size'] and up('NE')['short_frame'] and not base['short_frame']
    assert up('OXT')['user_boost'] > base['user_boost']
    assert up('GLU')['pool_size'] > base['pool_size'] and up('GLU')['hops'] == 2
    assert up('GABA')['prune_floor'] > base['prune_floor'] and up('GABA')['echo_cap'] < base['echo_cap']
    assert up('CB1')['relax_rate'] > base['relax_rate']


def test_cb1_relaxes_toward_baseline():
    t = TC.Tone7.from_axis('NE', 1.0); t.levels['CB1'] = 1.0
    first = t.levels['NE']
    for _ in range(8): t.relax()
    assert t.levels['NE'] < first and abs(t.levels['NE'] - 0.3) < 0.15
