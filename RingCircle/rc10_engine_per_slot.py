#!/usr/bin/env python3
"""rc10_engine_per_slot.py — read each slot, and each pair of slots, through the EXISTING bracketing & firing-order engine
(SedenionSpectralRelativity/bracket_firing_engine.py: the 31-node Cayley–Dickson block tree, smaller-norm child fires first).  The engine is imported as a library;
its own main() is not run (it rewrites an SVG inside that repo).  Writes rc10_results.json."""
import json, os, sys, itertools
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__)); SSR = os.path.abspath(os.path.join(HERE, "..", "..", "SedenionSpectralRelativity")); sys.path.insert(0, SSR)
from bracket_firing_engine import build_tree, firing_order, spectral_summary, verify_block_identity
from emerger_spectrum import e as unit_e
def vec(*terms):
    v = [F(0)] * 16
    for k, c in terms: v[k] += F(c)
    return tuple(v)
def nonzero_path(tree):
    out = []
    def walk(n):
        if n["norm_sq"] != 0: out.append(n["path"])
        for c in (n["children"] or []): walk(c)
    walk(tree); return out
res = {"single_slots": {}, "pairs": {}}
for k in range(16):
    v = vec((k, 1)); t = build_tree(v); o = firing_order(t); s = spectral_summary(t)
    chain = nonzero_path(t)
    res["single_slots"][k] = {"nonzero_chain_root_to_leaf": chain, "leaf": chain[-1], "firing_order_first_8": [n["path"] for n in o][:8], "all_nodes_isometry_exact": all(x["per_node_spread_all_one"] for x in s.values() if x["per_node_spread_max"] is not None)}
# pairs e_a ± e_b: zero divisors and equator ties
zd_pairs = []; tie_levels = {}
for a, b in itertools.combinations(range(16), 2):
    for sgn in (1, -1):
        v = vec((a, 1), (b, sgn)); t = build_tree(v); s = spectral_summary(t)
        zd = s[16]["n_zd"] > 0
        if zd: zd_pairs.append((a, b, sgn))
res["pairs"] = {"vectors_e_a_plus_minus_e_b": 240, "zero_divisor_vectors": len(zd_pairs), "zero_divisor_vectors_list": zd_pairs[:60],
                "all_have_a_under_8_and_b_8_or_over": all(a < 8 <= b for a, b, s in zd_pairs)}
json.dump(res, open(os.path.join(HERE, "rc10_results.json"), "w"), indent=1)
print(json.dumps(res["pairs"], indent=1)[:800]); print({k: (v["leaf"], v["nonzero_chain_root_to_leaf"]) for k, v in list(res["single_slots"].items())[:6]})
