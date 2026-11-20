import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

N = 16
def gen_continuous(a, b, phi):
    v = [0.0]*N
    v[a] = math.cos(phi); v[b] = math.sin(phi)
    return v

def partial_product_re(stations, phis, swap=False):
    st = [(b,a) if swap else (a,b) for a,b in stations]
    prod = gen_continuous(*st[0], phis[0])
    for k in range(1, len(st)):
        prod = bk.multiply(prod, gen_continuous(*st[k], phis[k]))
    return prod[0]

ts = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
rate_fn = lambda k, t: t * (k+1)/7 * (math.pi/2)

print("=== same rate law, generator = e_a -> e_b swapped (max-first instead of min-first) ===")
for strut in range(1, 8):
    stations = bk.pencil(strut)
    vals = [partial_product_re(stations, [rate_fn(k,t) for k in range(7)], swap=True) for t in ts]
    spread = max(vals) - min(vals)
    print(f"strut {strut}: spread={spread:.2e}  CONSERVED={spread<1e-9}   H(t=0)={vals[0]:+.4f}")
