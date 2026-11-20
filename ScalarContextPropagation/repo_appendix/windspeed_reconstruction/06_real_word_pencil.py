import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/VAPMIP"))
import numpy as np
import maths as bk
from wordnet_boxkite import context_vector, RELATION_METHODS
from context_pruner import embed16
from nltk.corpus import wordnet as wn

WORD = "resentment"
syn = wn.synsets(WORD)[0]
v19 = context_vector(syn)
print(f"word={WORD!r}  synset={syn.name()}")
print(f"  19-vector: {dict((RELATION_METHODS[i], c) for i, c in enumerate(v19) if c)}")

v16 = embed16(v19)
nrm = np.linalg.norm(v16)
if nrm == 0:
    print("all-zero vector, picking a fallback word")
    sys.exit(1)
v16u = (v16 / nrm).tolist()
# embed16 drops 3 of 19 -- pad to 16 full sedenion components e0..e15
# (v16 already has exactly 16 entries after dropping 3 of 19)
v_full = [0.0] + v16u[:15] if len(v16u) == 16 else v16u
# actually embed16 returns exactly 16 values already (19-3=16) -- use directly as e0..e15
v_full = v16u
print(f"  embed16 (unit norm): {[round(x,3) for x in v_full]}")

info = bk.chart_of(v_full, check_zd=False)
print(f"  chart_of: dominant_chart={info['dominant_chart']}  chart_share={info['chart_share']:.4f}"
      f"  outside_share={info['outside_share']:.4f}  is_zero_divisor={info['is_zero_divisor']}")

STRUT = info['dominant_chart']
print(f"\n=== real strut selected from real WordNet data: strut {STRUT} ===")
pencil_stations = bk.pencil(STRUT)
print(f"pencil({STRUT}) = {pencil_stations}")

# generators: e_{min(a,b)} per station, matching notebook 04's tested convention
gens = [min(a, b) for a, b in pencil_stations]
print(f"generators (min index per station): {gens}")

# pick a real anchor ZD point on this strut: one of its own Assessors
kite = bk.box_kites()[STRUT]
p, q = kite[0]                      # first Assessor of this strut, e.g. (a,b)
N = 16
def e(k):
    x = [0.0]*N; x[k] = 1.0; return x
def L_of(a):
    M = np.zeros((N, N))
    for j in range(N):
        M[:, j] = bk.multiply(a, e(j))
    return M

anchor = [0.0]*N
anchor[p] = 1/2**0.5; anchor[q+8] = 1/2**0.5
Ma = L_of(anchor)
eigvals, eigvecs = np.linalg.eigh((Ma + Ma.T)/2)  # symmetric part for real eigh; also do direct null check
# proper null space of the (non-symmetric) real matrix:
u, s, vt = np.linalg.svd(Ma)
null_mask = s < 1e-9
null_dirs = vt[-4:] if np.sum(s < 1e-9) >= 4 else vt[len(s)-4:]
print(f"\nanchor Assessor on strut {STRUT}: (e{p}, e{q+8})  -> anchor vector nonzero at indices [{p},{q+8}]")
sv = sorted(s)
print(f"singular values (smallest 6): {[round(x,4) for x in sv[:6]]}")
null_idx = [i for i, sig in enumerate(s) if sig < 1e-9]
print(f"null-space dimension: {len(null_idx)}")
for i in sorted(range(N), key=lambda i: s[i])[:4]:
    vec = vt[i]
    top = sorted(range(N), key=lambda k: -abs(vec[k]))[:2]
    print(f"  null partner (sigma={s[i]:.2e}): nonzero at indices {top}, values {[round(vec[k],3) for k in top]}")

print(f"\ngenerator indices from the pencil: {sorted(set(gens))}")
print(f"anchor's own indices: [{p}, {q+8}]")
overlap = set(gens) & set([p, q+8])
print(f"overlap between pencil generators and anchor's own indices: {overlap}")
