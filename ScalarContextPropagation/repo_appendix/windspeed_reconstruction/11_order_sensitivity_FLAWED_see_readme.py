import sys, os, math, itertools, random
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

N = 16
def gen_continuous(idx, phi):
    v = [0.0]*N; v[idx] = math.cos(phi); v[idx+1] if False else None
    return v

# same generator SET as struts 4,5,6,7 -- {1,2,3,8,9,10,11} -- but as a
# single fixed axis per slot (no pair-partner needed for this diagnostic;
# reuse the exact same continuous-sweep machinery on single basis directions)
def gen_single(idx, phi):
    v = [0.0]*N
    v[idx] = 1.0
    return v

SET = [1, 2, 3, 8, 9, 10, 11]

def product_re(order):
    def e(k):
        v=[0.0]*N; v[k]=1.0; return v
    prod = e(order[0])
    for k in order[1:]:
        prod = bk.multiply(prod, e(k))
    return prod[0]

# the four struts' ACTUAL pencil orders for this generator set
struts_orders = {}
for s in [4,5,6,7]:
    gens = [min(a,b) for a,b in bk.pencil(s)]
    struts_orders[s] = gens

print("the four real pencil orderings of {1,2,3,8,9,10,11}:")
conserved_now = {1,3,6}
for s, order in struts_orders.items():
    re = product_re(order)
    print(f"  strut {s}: {order}  Re(Pi)={re:+.4f}  (conserved earlier: {s in conserved_now})")

print()
print("how common is a 'conserving-looking' bare product among random orderings of the same 7?")
random.seed(7)
sample = set()
vals = []
for _ in range(200):
    perm = SET[:]
    random.shuffle(perm)
    vals.append(product_re(perm))
from collections import Counter
c = Counter(round(v,4) for v in vals)
print("distribution of Re(Pi) over 200 random orderings of the SAME 7-element set:")
for val, cnt in c.most_common(10):
    print(f"    Re(Pi)={val:+.4f}   count={cnt}/200")
