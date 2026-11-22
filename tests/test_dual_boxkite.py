"""Tests for dual_boxkite.py: every exploration runs on both the project's boxkite and de Marrais's control."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dual_boxkite as D


def test_f21_acts_on_both_boxkites_with_the_expected_orbits():
    D.LOG.clear()
    rows = D.run_f21_all()
    assert len(rows) == 7 and len(D.LOG) == 7
    for r in rows:
        d = r['detail']
        assert d['stabiliser_order'] == 3
        assert d['mine']['preserved'] and d['mine']['orbit_sizes'] == [1, 3, 3]            # pivot + axes + shadows
        assert d['control']['preserved'] and d['control']['edges_preserved'] and d['control']['edges'] == 12
        assert d['control']['orbit_sizes'] == [3, 3]                                          # the 6 Assessors: two 3-cycles
        assert r['agree'] is False                                                            # the difference is the pivot


def test_explore_records_a_row():
    D.LOG.clear()
    row = D.explore('same', lambda: 7, lambda: 7)
    assert row['agree'] and D.LOG[-1] is row
