import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
import maths as bk

N = 16
def e(k):
    v = [0.0]*N; v[k] = 1.0; return v

STRUT = 1
stations = bk.pencil(STRUT)

def gen_continuous(a, b, phi):
    """A genuinely continuous point on the great circle between e_a and e_b --
    NOT a discrete pick of one endpoint. phi=0 -> e_a, phi=pi/2 -> e_b."""
    v = [0.0]*N
    v[a] = math.cos(phi)
    v[b] = math.sin(phi)
    return v

def partial_product_re(phis):
    prod = gen_continuous(*stations[0], phis[0])
    for k in range(1, len(stations)):
        prod = bk.multiply(prod, gen_continuous(*stations[k], phis[k]))
    return prod[0]

print("=== sweeping ONE station's phi continuously, others fixed at the discrete pick (phi=0, i.e. min(a,b)) ===")
fixed_phis = [0.0]*7
for phi in [0.0, 0.1, 0.2, 0.3, 0.39269908, 0.5, 0.7, 0.9, 1.0, 1.2, 1.4, 1.5707963]:
    phis = list(fixed_phis); phis[2] = phi     # vary station 3's angle continuously
    re = partial_product_re(phis)
    print(f"  station3 phi={phi:.4f} (0=e{stations[2][0]}, pi/2=e{stations[2][1]})   Re(Pi)={re:+.6f}")

print()
print("=== sweeping ALL 7 stations' phi together, continuously, phi(k) = t * (k/7) ===")
for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    phis = [t * (math.pi/2) * ((k+1)/7) for k in range(7)]
    re = partial_product_re(phis)
    print(f"  t={t:.2f}  Re(Pi)={re:+.6f}")

print()
print("=== is conservation special to phi_k=t*(k+1)/7, or does ANY uniform joint rotation conserve H? ===")
print("-- uniform: all seven phi_k = t (same angle, not staggered) --")
for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.5707963]:
    phis = [t]*7
    re = partial_product_re(phis)
    print(f"  t={t:.4f}  Re(Pi)={re:+.6f}")

print("-- staggered but REVERSED order: phi_k = t*(7-k)/7 --")
for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    phis = [t * (7-k)/7 * (math.pi/2) for k in range(7)]
    re = partial_product_re(phis)
    print(f"  t={t:.2f}  Re(Pi)={re:+.6f}")

print("-- random but fixed per-station rates (not the pencil order) --")
import random
random.seed(1)
rates = [random.uniform(0.3, 1.0) for _ in range(7)]
for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    phis = [t*r*(math.pi/2) for r in rates]
    re = partial_product_re(phis)
    print(f"  t={t:.2f}  Re(Pi)={re:+.6f}")
