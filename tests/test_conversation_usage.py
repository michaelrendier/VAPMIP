"""Tests for the daemon's usage channel (2026-11-25): usage as probability, Broca-Wernicke drift, the Harness wiring, the window lever."""
import json, math, os, sys
import pytest
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, H); sys.path.insert(0, os.path.join(H, 'Currentwork', 'UserState'))
import bw_drift as BW
import conversation_usage as CU
import sedenion_window as SW


def test_usage_probability_starts_as_english_and_moves_to_the_user():
    from vocab_store import UsageStore
    s = UsageStore(); cold = s.p_word('phasor'); assert 0 < cold < 1e-4 and s.confidence() == 0
    for _ in range(40): s.observe('The phasor rotates. A phasor is a kind of vector.')
    assert s.p_word('phasor') > 20 * cold and s.confidence() > 0.3
    assert s.p_word('the') > 0 and s.p_word('zzzxq') > 0                    # never zero: Brown smoothing


def test_gamma_is_zero_on_the_lemniscate_and_grows_with_the_drift():
    assert abs(BW.gamma(5.0, 5.0)) < 1e-12
    g = [abs(BW.gamma(5.0, 5.0 * math.exp(d))) for d in (0.1, 0.3, 0.6, 1.2)]
    assert g == sorted(g) and g[-1] < 1.0
    assert abs(BW.gamma(5.0, 5.0 * math.exp(0.5))) == pytest.approx(abs(BW.gamma(5.0 * math.exp(0.5), 5.0)))       # symmetric in side


def test_gamma_matches_the_scale_engine():
    sys.path.insert(0, os.path.join(H, '..'))
    try:
        from ValaQuenta.modules.scale import maths as SC
    except Exception as e: pytest.skip('ValaQuenta checkout not beside this repo: %r' % (e,))
    w, b = 4.0, 7.0; a = math.sqrt(w * b)
    pt = SC.broca_wernicke_ring_chart(None, lambda o: b, lambda o: w, complex(a, a))
    assert abs(pt['gamma'] - BW.gamma(w, b)) < 1e-12


def test_hysteresis_and_sign_of_the_correction():
    d = BW.BWDrift()
    assert not d.update(5, 5 * math.exp(0.2))['active']                    # inside the band: drifting is expected
    r = d.update(5, 5 * math.exp(0.6)); assert r['active'] and r['bw_correction'] > 0 and r['side'] == 'broca'
    assert d.update(5, 5 * math.exp(0.2))['active']                        # stays on until it is back inside OFF
    assert not d.update(5, 5 * math.exp(0.1))['active']
    r = d.update(5 * math.exp(0.6), 5); assert r['active'] and r['bw_correction'] < 0 and r['side'] == 'wernicke'
    assert abs(r['bw_correction']) <= 1


def test_conversation_usage_flow_persists_and_only_the_user_counts(tmp_path):
    cu = CU.ConversationUsage(str(tmp_path))
    cu.hear('A phasor is a kind of vector. The phasor rotates.', 'external', 'p1')
    n = cu.store.n_obs; assert n > 0 and cu.vocab.lookup('phasor')                       # usage counted, a sense learned
    out = cu.hear('The vector rotates with the phasor in the plane.', 'internal', 'p1')
    assert out and out['wernicke'] > 0 and out['broca'] > 0 and cu.store.n_obs == n         # the reply is priced, never counted as usage
    assert cu.channels['bw_correction'] == out['bw_correction']
    assert os.path.exists(tmp_path / 'usage.json') and os.path.exists(tmp_path / 'vocab.jsonl') and len(open(tmp_path / 'drift.jsonl').readlines()) == 1
    cu2 = CU.ConversationUsage(str(tmp_path)); assert cu2.store.n_obs == n and cu2.vocab.lookup('phasor')    # reload keeps both
    assert cu.hear('Some committed page text.', 'document') is None and cu.store.n_obs == n


def test_the_harness_observe_feeds_the_usage_channel(tmp_path, monkeypatch):
    monkeypatch.setenv('PTOL_USAGE_DIR', str(tmp_path)); monkeypatch.delenv('PTOL_USAGE', raising=False)
    import harness
    h = harness.Harness(); monkeypatch.setattr(h, '_fifo_write', lambda m: True)
    h.observe('The phasor is a kind of vector in the plane.', 'external', 'q1'); h.observe('The vector turns in the plane.', 'internal', 'q1')
    assert h.usage is not None and h.usage.last is not None and h.usage.store.n_obs > 0
    monkeypatch.setenv('PTOL_USAGE', '0'); h2 = harness.Harness(); monkeypatch.setattr(h2, '_fifo_write', lambda m: True)
    h2.observe('Hello there.', 'external', 'q2'); assert h2.usage is None


def test_the_window_uses_the_user_s_usage_and_the_correction_channel(tmp_path):
    cu = CU.ConversationUsage(str(tmp_path))
    for _ in range(30): cu.hear('The king rules the kingdom. The queen reads the book.', 'external')
    bg = SW.Bigram().fit(["The king rules the kingdom. The dog chases the cat in the garden. " * 6])
    w0 = SW.SedenionWindow(bg); w1 = SW.SedenionWindow(bg, usage=cu)
    assert w1._p('queen', None) != w0._p('queen', None) and cu.store.confidence() > 0.2
    cu.channels['bw_correction'] = 1.0; a = w1.write('The king rules the kingdom')['bits']
    cu.channels['bw_correction'] = -1.0; b = w1.write('The king rules the kingdom')['bits']
    assert a <= b + 1e-9                                                     # a positive correction never makes the reply dearer than a negative one
