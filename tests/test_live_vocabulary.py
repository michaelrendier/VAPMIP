"""Tests for live_vocabulary.py: learn new words on the fly, keep the history, repack the C store (2026-11-21)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import live_vocabulary as LV
import wordnet_boxkite as WB

PTOLC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'PtolC')
STORE = os.path.join(PTOLC, 'monad3_c.bin')


def clock():
    n = [0]
    def tick():
        n[0] += 1
        return '2026-11-21T00:00:%02d.000000+00:00' % n[0]
    return tick


@pytest.fixture
def vocab(tmp_path):
    return LV.LiveVocabulary(journal_path=str(tmp_path / 'j.jsonl'), clock=clock())


def test_unknown_word_becomes_a_sense_with_a_vector(vocab):
    # 'phasor' has no synset in WordNet 3.0 (checked): the Monad learns it from one sentence
    assert vocab._wn.synsets('phasor') == []
    ev = vocab.hear('A phasor is a kind of vector.')
    assert len(ev) == 1 and ev[0]['new']
    s = vocab.lookup('phasor')
    assert len(s) == 1 and s[0]['source'] == 'live' and s[0]['vector'][LV._REL_IDX['hypernyms']] == 1
    assert s[0]['gamma_radial'] is not None
    # the reciprocal edge landed on the WordNet sense of 'vector' (hyponyms + 1)
    v = [x for x in vocab.lookup('vector') if x['source'] == 'wordnet'][0]
    base = WB.context_vector(vocab._wn.synset_from_pos_and_offset('n', int(v['sense'][4:])))
    assert v['vector'][LV._REL_IDX['hyponyms']] >= base[LV._REL_IDX['hyponyms']]
    sv = vocab.senses[v['sense']]
    assert sv.raw()[LV._REL_IDX['hyponyms']] == sv.base_raw[LV._REL_IDX['hyponyms']] + 1


def test_vector_matches_wordnet_definition_for_untouched_senses(vocab):
    s = vocab.resolve('tree', 'n')
    ss = vocab._wn.synset_from_pos_and_offset('n', int(s.id[4:]))
    assert s.vector() == WB.context_vector(ss)


def test_such_as_list_and_support_refinement(vocab):
    ev = vocab.hear('Vectors such as phasors, spinors and twistors.')
    assert len(ev) == 3 and all(e['new'] for e in ev)
    again = vocab.hear('A phasor is a kind of vector.')
    again2 = vocab.hear('A phasor is a kind of vector.')
    assert again[0]['new'] is False and again2[0]['new'] is False
    h = vocab.history('phasor')
    kinds = [e['kind'] for e in h]
    assert kinds[:2] == ['seen', 'created'] and 'edge' in kinds and kinds.count('support') == 2
    assert [e['t'] for e in h] == sorted(e['t'] for e in h)


def test_unknown_token_is_remembered_before_it_has_evidence(vocab):
    vocab.hear('The zorblax hums.')
    vocab.hear('The zorblax hums again.')
    u = vocab.unknown['zorblax']
    assert u['count'] == 2 and u['first'] < u['last']
    vocab.hear('A zorblax is a kind of machine.')
    assert 'zorblax' not in vocab.unknown and vocab.lookup('zorblax')[0]['source'] == 'live'


def test_part_member_substance_cause_similar(vocab):
    ev = vocab.hear('A wheel is part of a car. A senator is a member of a senate. A statue is made of bronze. '
                    'Killing causes dying. Smoking causes cancer. Vast is similar to huge.')
    rels = [(e['relation'], e['new'], e.get('skipped')) for e in ev]
    assert ('part_holonyms', True, None) in rels and ('member_holonyms', True, None) in rels
    assert ('substance_meronyms', True, None) in rels
    assert ('causes', True, None) in rels                         # kill -> die: verb-verb
    assert ('causes', False, 'not verb-verb') in rels             # smoking -> cancer: noun causation is skipped
    assert ('similar_tos', True, None) in rels
    w = vocab.lookup('wheel')[0]
    assert w['vector'][LV._REL_IDX['part_holonyms']] >= 1


def test_journal_replay_rebuilds_the_same_state(tmp_path):
    p = str(tmp_path / 'j.jsonl')
    a = LV.LiveVocabulary(journal_path=p, clock=clock())
    a.hear('A phasor is a kind of vector. Vectors such as spinors and twistors. A phasor is a kind of vector.')
    b = LV.LiveVocabulary(journal_path=p, clock=clock())     # replays
    assert {k: v.vector() for k, v in a.senses.items()} == {k: v.vector() for k, v in b.senses.items()}
    assert {k: v.support for k, v in a.senses.items()} == {k: v.support for k, v in b.senses.items()}
    lines = open(p, encoding='utf-8').read().strip().split('\n')
    assert len(lines) == len(a.journal) == len(b.journal)


def test_split_records_when_a_word_became_two(vocab):
    vocab.hear('A glorp is a kind of institution. A glorp is a kind of slope.')
    s = vocab.lookup('glorp')[0]
    props = vocab.propose_splits('glorp')
    assert props and len(props[0]['groups']) == 2
    sid = props[0]['sense']
    moved = {'hypernyms': props[0]['groups'][1]}
    nid = vocab.split_sense(sid, moved)
    assert nid != sid and len(vocab.lookup('glorp')) == 2
    assert vocab.senses[sid].added['hypernyms'] == props[0]['groups'][0]
    assert any(e['kind'] == 'split' for e in vocab.history('glorp'))
    # the reciprocal edge now points at the new sense
    tgt = vocab.senses[moved['hypernyms'][0]]
    assert nid in tgt.added['hyponyms'] and sid not in tgt.added['hyponyms']


def test_sedenion_frames_are_sixteen_nodes_with_an_anchor(vocab):
    words = ['wug' + 'abcdefghijklmnopqrst'[i] for i in range(20)]
    vocab.hear('Things such as ' + ', '.join(words[:-1]) + ' and ' + words[-1] + '.')
    fr = vocab.dirty_frames()
    assert all(len(f['nodes']) <= 16 and len(f['edges']) <= 15 for f in fr)
    assert all(f['e0'] == f['nodes'][0] and not f['unreached'] for f in fr)
    assert len(fr) == 2                                  # hub + 20 siblings: two frames sharing the hub as e0
    assert fr[0]['e0'] == fr[1]['e0']
    covered = {n for f in fr for n in f['nodes']}
    assert covered == {s.id for s in vocab.touched_senses()}


@pytest.mark.skipif(not os.path.exists(STORE), reason='monad3_c.bin not present')
def test_repack_adds_words_and_ptol_sees_them(tmp_path):
    v = LV.LiveVocabulary(journal_path=str(tmp_path / 'j.jsonl'), clock=clock(), base_bin=STORE)
    v.hear('A phasor is a kind of vector. A glorp is a kind of institution.')
    rows = v.bin_rows()
    dst = str(tmp_path / 'monad3_c.bin')
    before = os.path.getsize(STORE)
    info = LV.repack_monad3c(STORE, dst, rows)
    assert os.path.getsize(STORE) == before                       # the source is untouched
    assert info['words_after'] >= info['words_before'] + 2 and 'phasor' in info['new_keys']
    # python reader
    import monad_combine as MC
    r = MC.read_c(dst)
    got = r['lookup']('phasor')
    assert got and got['wn_vec19'][LV._REL_IDX['hypernyms']] == 1
    o = MC.read_c(STORE)
    assert r['header']['n_eng'] == o['header']['n_eng'] and r['header']['nnz'] == o['header']['nnz']
    import random
    names = LV.read_c_store(STORE)['names']
    random.Random(7).shuffle(names)
    changed = set(rows)
    for w in names[:400] + ['tree', 'vector', 'the', 'water']:
        a, b = o['lookup'](w), r['lookup'](w)
        assert a is not None and b is not None, w
        for k in ('eng_idx', 'phon_idx', 'beta', 'degree', 'n_prons'):      # the English field and phonetics are intact
            assert a.get(k) == b.get(k), (w, k)
        if w not in changed:
            assert a.get('wn_vec19') == b.get('wn_vec19'), w
    # the C binary itself
    work = tmp_path / 'ptolc'
    work.mkdir()
    shutil.copy(os.path.join(PTOLC, 'ptol'), work / 'ptol')
    shutil.copy(dst, work / 'monad3_c.bin')
    out = subprocess.run([str(work / 'ptol'), '-M', 'phasor'], capture_output=True, text=True, timeout=60).stdout
    assert 'wn_idx=' in out and 'vec19=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]' in out
    assert 'gamma_radial' in out
