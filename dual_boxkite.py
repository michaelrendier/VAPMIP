#!/usr/bin/env python3
"""dual_boxkite.py -- every boxkite construction or exploration runs on BOTH boxkites, side by side.

Cody, 2026-11-21: "any boxkite constructions or explorations get automatically done to my construction and the de Marrais
'control' boxkite."
  MINE      the scalar boxkite of this project: the pencil(s) of 7 ordered pairs (3 axes + pivot + 3 shadows) and the 19-relation
            context hash (wordnet_boxkite.py)
  CONTROL   de Marrais's box-kite (arXiv:math/0011260): per strut s, 6 Assessors (ordered pairs (a,b), a != b, a^b = s), 12 edges
            (vanishing products), ValaQuenta/modules/box_kite/maths.py

`explore(name, mine, control)` runs both callables, records one row (name, mine, control, agree) in `LOG`, and returns it. Nothing here
decides which is right: the control is the established object, mine is the construction under test; a difference is a result.
Built-in explorations: `f21_action` (the Blackjack group F21 acting on each kite).
"""
from __future__ import annotations
import itertools, os, sys
from typing import Any, Callable, Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ValaQuenta.modules.box_kite import maths as BK

LOG: List[Dict[str, Any]] = []


def explore(name: str, mine: Callable[[], Any], control: Callable[[], Any]) -> Dict[str, Any]:
    m, c = mine(), control()
    row = {'name': name, 'mine': m, 'control': c, 'agree': m == c}
    LOG.append(row)
    return row


# ── the Blackjack group F21 on the 15 sedenion labels ──────────────────────────────────────────────
def _mul(a, b):
    r = 0
    for i in range(3):
        if (b >> i) & 1: r ^= a << i
    for i in (4, 3):
        if (r >> i) & 1: r ^= 0b1011 << (i - 3)
    return r


def f21() -> List[tuple]:
    ext = lambda f: (lambda x: (f(x & 7) | (x & 8)) if (x & 7) else x)
    gens = [tuple([0] + [ext(lambda x: _mul(x, 2))(p) for p in range(1, 16)]),
            tuple([0] + [ext(lambda x: _mul(x, x))(p) for p in range(1, 16)])]
    G = {tuple(range(16))}; fr = list(G)
    while fr:
        new = []
        for g in fr:
            for h in gens:
                c = tuple(g[h[i]] for i in range(16))
                if c not in G: G.add(c); new.append(c)
        fr = new
    return sorted(G)


def _orbit_sizes(stab, items, act):
    seen, sizes = set(), []
    for x in items:
        if x in seen: continue
        o = {act(g, x) for g in stab}
        seen |= o; sizes.append(len(o))
    return sorted(sizes)


def f21_action(s: int) -> Dict[str, Any]:
    """The stabiliser of strut s in F21, acting on (mine) the 7 pencil stations and (control) the 6 Assessors of kite s."""
    G = f21(); stab = [g for g in G if g[s] == s]
    stations = [tuple(sorted(p)) for p in BK.pencil(s)]
    kite = BK.box_kites()[s]
    def act_pair(g, p): return tuple(sorted((g[p[0]], g[p[1]])))
    def act_ass(g, a): return (g[a[0]], g[a[1]])
    mine_ok = all(sorted(act_pair(g, p) for p in stations) == sorted(stations) for g in stab)
    ctrl_ok = all(sorted(act_ass(g, a) for a in kite) == sorted(kite) for g in stab)
    edges = {frozenset((a, b)) for a, b in itertools.combinations(kite, 2) if BK.assessors_adjacent(a, b)}
    edge_ok = all({frozenset((act_ass(g, a), act_ass(g, b))) for a, b in map(tuple, edges)} == edges for g in stab)
    return {'strut': s, 'stabiliser_order': len(stab),
            'mine': {'object': 'pencil(%d), 7 stations' % s, 'preserved': mine_ok, 'orbit_sizes': _orbit_sizes(stab, stations, act_pair)},
            'control': {'object': 'de Marrais kite %d, 6 Assessors' % s, 'preserved': ctrl_ok, 'edges': len(edges),
                        'edges_preserved': edge_ok, 'orbit_sizes': _orbit_sizes(stab, kite, act_ass)}}


def run_f21_all() -> List[Dict[str, Any]]:
    out = []
    for s in range(1, 8):
        r = f21_action(s)
        out.append(explore('f21_action(strut=%d)' % s, lambda r=r: r['mine']['orbit_sizes'], lambda r=r: r['control']['orbit_sizes']))
        out[-1]['detail'] = r
    return out


if __name__ == '__main__':
    for row in run_f21_all():
        d = row['detail']
        print('strut %d |stab|=%d  mine %s orbits %s | control %s edges %d preserved=%s orbits %s' % (
            d['strut'], d['stabiliser_order'], d['mine']['preserved'], d['mine']['orbit_sizes'], d['control']['preserved'],
            d['control']['edges'], d['control']['edges_preserved'], d['control']['orbit_sizes']))
