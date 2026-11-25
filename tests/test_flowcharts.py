"""The flow charts (docs/flowcharts/) may only name things that exist in the C source they describe."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'docs', 'flowcharts'))
import make_flowcharts as MF

SRC = ''.join(open(os.path.join(ROOT, 'PtolC', f), encoding='utf-8').read() for f in ('ptol.c', 'monad_harness.c', 'monad_harness.h'))
PYS = ''.join(open(os.path.join(ROOT, f), encoding='utf-8').read() for f in os.listdir(ROOT) if f.endswith('.py'))


def names(chart):
    out = set()
    for n in chart.nodes.values():
        out |= set(re.findall(r'\b(?:cv|mh|MH)_[A-Za-z0-9_]+|\b(?:u_observe|ms_dose|ms_open)\b|\b(?:[a-z_]+\.py)\b', n['title'] + ' ' + n['sub']))
    for _, sub in chart.lanes: out |= set(re.findall(r'\b(?:cv|mh)_[A-Za-z0-9_]+', sub))
    out |= set(re.findall(r'\b[a-z_0-9]+\.py\b', chart.sub))
    return out


def test_every_c_name_in_the_charts_exists_in_the_c_source():
    for fn in (MF.monad, MF.harness):
        miss = [x for x in names(fn()) if not x.endswith('.py') and x not in SRC]
        assert not miss, (fn.__name__, miss)


def test_every_python_twin_named_in_the_charts_exists():
    for fn in (MF.monad, MF.harness):
        where = [ROOT, os.path.join(ROOT, 'Currentwork', 'UserState'), os.path.join(ROOT, '..', 'PtolemyDesktop')]
        miss = [x for x in names(fn()) if x.endswith('.py') and not any(os.path.exists(os.path.join(d, x)) for d in where)]
        assert not miss, (fn.__name__, miss)
