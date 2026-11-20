import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

# Observer position, stated: orientation = native (continuous great-circle
# generators, not lattice-pinned basis vectors); aperture = one strut's
# pencil at a time, swept across all 7 struts, continuous t in [0,1].

N = 16
def e(k):
    v = [0.0]*N; v[k] = 1.0; return v

def gen_continuous(a, b, phi):
    v = [0.0]*N
    v[a] = math.cos(phi)
    v[b] = math.sin(phi)
    return v

def partial_product_re(stations, phis):
    prod = gen_continuous(*stations[0], phis[0])
    for k in range(1, len(stations)):
        prod = bk.multiply(prod, gen_continuous(*stations[k], phis[k]))
    return prod[0]

def sweep(stations, rate_fn, ts):
    vals = []
    for t in ts:
        phis = [rate_fn(k, t) for k in range(len(stations))]
        vals.append(partial_product_re(stations, phis))
    return vals

ts = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

print("=== pencil-ordered rate  phi_k = t*(k+1)/7*(pi/2)  -- across all 7 struts ===")
for strut in range(1, 8):
    stations = bk.pencil(strut)
    rate_fn = lambda k, t: t * (k+1)/7 * (math.pi/2)
    vals = sweep(stations, rate_fn, ts)
    spread = max(vals) - min(vals)
    conserved = spread < 1e-9
    print(f"strut {strut}: H(t) = {[round(v,6) for v in vals]}   "
          f"spread={spread:.2e}   CONSERVED={conserved}")

print()
print("=== control: uniform rate phi_k=t (already shown non-conserving on strut 1) -- all 7 struts ===")
for strut in range(1, 8):
    stations = bk.pencil(strut)
    rate_fn = lambda k, t: t
    vals = sweep(stations, rate_fn, ts)
    spread = max(vals) - min(vals)
    print(f"strut {strut}: H(t) = {[round(v,6) for v in vals]}   spread={spread:.4f}")
