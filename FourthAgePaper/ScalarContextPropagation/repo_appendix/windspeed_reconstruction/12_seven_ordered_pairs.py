# repo_appendix/windspeed_reconstruction/12_seven_ordered_pairs.py
# Lays out the seven ordered pairs of pencil(r) against De Marrais's Assessors, and checks the tension law H = -cos(sum eps_k phi_k).
# Self-contained: needs only ValaQuenta/modules/box_kite/maths.py (the module section 9.2 already uses). Run: python3 12_seven_ordered_pairs.py
import sys, os, math, random
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

P = range(1, 8)                                   # the lower Fano plane: indices 1..7, no e_0, no e_8

def group_stations(r):                            # the 7 ordered pairs of pencil(r), r in 1..7, by what they are
    kinds = []
    for (a, b) in bk.pencil(r):                   # pairs {a,b}, a XOR b == r, in pencil order (sorted by smaller member)
        kinds.append((a, b, "axis" if b < 8 else "pivot" if a == 8 else "shadow"))
    return kinds                                  # axis = a line {a,b,r} of the plane; shadow = its copy +8; pivot = the pair holding e_8

def kite_vertices(s):                             # De Marrais's 6 Assessors of chart s: ordered pairs of DISTINCT plane points, a XOR b == s
    return sorted((a, b) for a in P for b in P if a != b and a ^ b == s)

def gen(a, b, phi):                               # one station: cos(phi) e_a + sin(phi) e_b  =  e_a * exp(eta e_r phi)
    v = [0.0] * 16; v[a] = math.cos(phi); v[b] = math.sin(phi); return v

def H(r, phis):                                   # Re of the left-associated ordered product of the 7 stations
    st = bk.pencil(r); p = gen(*st[0], phis[0])
    for k in range(1, 7): p = bk.multiply(p, gen(*st[k], phis[k]))
    return p[0]

EPS = {1: "++--++-", 2: "+--++--", 3: "++--++-", 4: "+++++++", 5: "+-+-+-+", 6: "++--++-", 7: "+--++--"}   # fitted, section 9.7

if __name__ == "__main__":
    assessor_planes = {frozenset((a, b + 8)) for (a, b) in bk.assessors()}
    for r in P:
        g = group_stations(r)
        print(f"strut {r}:  axes {[(a, b) for a, b, k in g if k == 'axis']}  pivot {[(a, b) for a, b, k in g if k == 'pivot']}  "
              f"shadows {[(a, b) for a, b, k in g if k == 'shadow']}   eps = {EPS[r][:3]} | {EPS[r][3]} | {EPS[r][4:]}")
        assert kite_vertices(r) == sorted(bk.box_kites()[r])                       # De Marrais's chart r, rebuilt from the plane alone
        assert not any(frozenset((a, b)) in assessor_planes for a, b, k in g)      # none of the seven is an Assessor plane
        axes = [(a, b) for a, b, k in g if k == "axis"]
        assert sorted(axes) == sorted({tuple(sorted(v)) for v in kite_vertices(r)})   # the 3 axes are the kite's 3 antipodal pairs
    random.seed(1); worst = 0.0
    for r in P:
        for _ in range(60):
            ph = [random.uniform(0, math.pi / 2) for _ in range(7)]
            worst = max(worst, abs(H(r, ph) + math.cos(sum((1 if c == "+" else -1) * x for c, x in zip(EPS[r], ph)))))
    print(f"max |H + cos(sum eps_k phi_k)| over 7 struts x 60 random phase vectors = {worst:.1e}")
