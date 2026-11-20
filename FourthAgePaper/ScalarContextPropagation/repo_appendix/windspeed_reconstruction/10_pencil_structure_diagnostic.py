import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

conserved = {1, 3, 6}

print("=== pencil structure per strut, looking for what distinguishes {1,3,6} ===")
for s in range(1, 8):
    stations = bk.pencil(s)
    gens_min = [min(a,b) for a,b in stations]
    gens_max = [max(a,b) for a,b in stations]
    xor_all = 0
    for g in gens_min: xor_all ^= g
    tag = "CONSERVED" if s in conserved else "drifts"
    print(f"\nstrut {s} [{tag}]  (binary {s:03b}):")
    print(f"  pencil: {stations}")
    print(f"  min-generators: {gens_min}   sum={sum(gens_min)}   xor={xor_all}")
    print(f"  max-generators: {gens_max}   sum={sum(gens_max)}")
    # is s itself among the generators?
    print(f"  strut index {s} appears in min-gens: {s in gens_min}   in max-gens: {s in gens_max}")
    # does the pencil contain the pair (s, something)? i.e. is s one of the 15 points touched
    touched = set()
    for a,b in stations: touched.add(a); touched.add(b)
    print(f"  all 14 touched indices: {sorted(touched)}  (15 total points minus s itself: {s not in touched})")
