#!/usr/bin/env python3
"""rc11_followups.py — characterise the three structures the first battery found: (a) which 4-slot circle sets deform, (b) which 3-slot sets are associative, (c) the sign rule of the balanced bracket on slot 15."""
import itertools, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = ["x"]
src = open(os.path.join(HERE, "ring_circle_battery.py")).read().split("# ── RC-1")[0]; __file__ = os.path.join(HERE, "ring_circle_battery.py"); exec(src)
rng = np.random.default_rng(11)
def trees(items):
    if len(items) == 1: yield items[0]; return
    for m in range(1, len(items)):
        for l in trees(items[:m]):
            for r in trees(items[m:]): yield (l, r)
def ev(tr, v): return v[tr] if isinstance(tr, int) else mul(ev(tr[0], v), ev(tr[1], v))
def circ_el(k, th): return math.cos(th) * unit(0) + math.sin(th) * unit(k)
deforming_pairs = {(i, j) for i in range(1, 8) for j in range(9, 16) if j - 8 != i}
lines = {tuple(sorted(s)) for s in itertools.combinations(range(1, 16), 3) if s[0] ^ s[1] == s[2] or s[0] ^ s[2] == s[1] or s[1] ^ s[2] == s[0]}
out = {}
# (b) 3-slot sets: number of distinct results vs line membership
hist = {}
for S in itertools.combinations(range(1, 16), 3):
    ph = rng.uniform(0, 2 * math.pi, 3); outs = set()
    for order in itertools.permutations(range(3)):
        v = {i: circ_el(S[order[i]], ph[order[i]]) for i in range(3)}
        for tr in trees([0, 1, 2]): outs.add(tuple(np.round(ev(tr, v), 9)))
    key = (S in lines, len(outs)); hist[str(key)] = hist.get(str(key), 0) + 1
out["three_slot_sets: (is_a_line_of_PG(3,2), distinct_results) -> count"] = hist
# (a) 4-slot sets that leave the unit sphere
def worst(S):
    w = 0.0
    for _ in range(4):
        ph = rng.uniform(0, 2 * math.pi, 4)
        for order in itertools.permutations(range(4)):
            v = {i: circ_el(S[order[i]], ph[order[i]]) for i in range(4)}
            for tr in trees(list(range(4))): w = max(w, abs(np.linalg.norm(ev(tr, v)) - 1))
    return w
cls = {}
for S in itertools.combinations(range(1, 16), 4):
    dp = sum(1 for a, b in itertools.combinations(S, 2) if (a, b) in deforming_pairs)
    xor0 = (S[0] ^ S[1] ^ S[2] ^ S[3]) == 0                # the four slots XOR to 0: a "plane" of PG(3,2) (affine 2-flat)
    w = worst(S); k = (f"deforming_pairs_inside={dp}", f"xor_of_four_is_zero={xor0}", "deforms" if w > 1e-9 else "pure")
    cls[str(k)] = cls.get(str(k), 0) + 1
out["four_slot_sets: (deforming pairs inside, XOR of the four = 0, outcome) -> count"] = cls
# (c) the sign rule of the balanced bracket ((a b)(c d)) on the generators 1,2,4,8
tab = {}
for order in itertools.permutations((1, 2, 4, 8)):
    r = mul(mul(unit(order[0]), unit(order[1])), mul(unit(order[2]), unit(order[3]))); tab[order] = int(round(r[15]))
parity = lambda p: sum(1 for a in range(4) for b in range(a + 1, 4) if p[a] > p[b]) % 2
by = {}
for order, sg in tab.items():
    pairing = tuple(sorted([tuple(sorted(order[:2])), tuple(sorted(order[2:]))])); by.setdefault(pairing, set()).add(sg * (-1) ** parity(order))
out["balanced_bracket_((ab)(cd))_on_1,2,4,8: pairing -> set of sign·(-1)^parity"] = {str(k): sorted(v) for k, v in by.items()}
json.dump(out, open(os.path.join(HERE, "rc11_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
