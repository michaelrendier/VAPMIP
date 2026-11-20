"""PHASE 25's OPEN CONJECTURE, tested.

  "ZERO CROSS-STRUT EDGES. The gluing is NOT an edge problem -- either there is
   no global medium, or the transition maps are the PSL(2,7) ACTION ON STRUTS
   (group elements, not edges). The latter is the named next step."

Struts are s = a XOR b in 1..7 -- i.e. the 7 nonzero vectors of F_2^3, which are
the 7 points of the Fano plane. PSL(2,7) = GL(3,2) = Aut(Fano) acts on them.

THE TEST: does that action PRESERVE THE ZERO-DIVISOR STRUCTURE?
If yes, the group elements ARE transition maps and the atlas connects.
If no, the conjecture fails.
"""
import numpy as np, itertools, collections

N = 16
def conj(v): w = v.copy(); w[1:] = -w[1:]; return w
def mul(x, y):                                    # verified variant
    n = len(x)
    if n == 1: return np.array([x[0]*y[0]])
    h = n//2; a, b = x[:h], x[h:]; c, d = y[:h], y[h:]
    A = lambda v: conj(v) if len(v) > 1 else v.copy()
    return np.concatenate([mul(a, c) - mul(A(d), b), mul(d, a) + mul(b, A(c))])
def e(k):
    v = np.zeros(N); v[k] = 1.0; return v

# ── GL(3,2) ───────────────────────────────────────────────────────────────────
def gl32():
    """All invertible 3x3 matrices over F_2. |GL(3,2)| = 168 = |PSL(2,7)|."""
    out = []
    for bits in itertools.product([0, 1], repeat=9):
        M = np.array(bits, dtype=int).reshape(3, 3)
        # determinant over F_2
        d = (M[0,0]*(M[1,1]*M[2,2]-M[1,2]*M[2,1])
           - M[0,1]*(M[1,0]*M[2,2]-M[1,2]*M[2,0])
           + M[0,2]*(M[1,0]*M[2,1]-M[1,1]*M[2,0])) % 2
        if d == 1: out.append(M)
    return out

G = gl32()
print("="*74)
print("THE GROUP")
print("="*74)
print(f"  |GL(3,2)| = {len(G)}   (expect 168 = |PSL(2,7)| = ZD_COMPOSITE)")

def as_vec(k):  return np.array([(k>>2)&1, (k>>1)&1, k&1], dtype=int)
def as_idx(v):  return (int(v[0])<<2) | (int(v[1])<<1) | int(v[2])
def act(M, k):  return as_idx(M.dot(as_vec(k)) % 2)

# strut transforms linearly: M(a) XOR M(b) = M(a XOR b), because M is LINEAR
lin_ok = all(act(M,a) ^ act(M,b) == act(M, a^b)
             for M in G[:40] for a in range(1,8) for b in range(1,8) if a != b)
print(f"  strut map is linear:  M(a)^M(b) == M(a^b)  ->  {lin_ok}")

orb = {act(M,1) for M in G}
print(f"  orbit of strut 1 under the group: {sorted(orb)}")
print(f"  TRANSITIVE on the 7 struts: {sorted(orb) == list(range(1,8))}")

# ── the 84 assessor diagonals ────────────────────────────────────────────────
diags = []
for a in range(1,8):
    for b in range(1,8):
        if a == b: continue
        for s in (1,-1):
            diags.append((a, b, s))
D = {d: (e(d[0]) + d[2]*e(d[1]+8))/np.sqrt(2) for d in diags}
print(f"\n  assessor diagonals: {len(diags)}  (42 planes x 2)")

# annihilation relation
ann = set()
for i, d1 in enumerate(diags):
    for j, d2 in enumerate(diags):
        if i != j and np.linalg.norm(mul(D[d1], D[d2])) < 1e-9:
            ann.add((d1, d2))
print(f"  ordered annihilating pairs: {len(ann)}  (expect 336 = 84 x 4)")

# ── does the group action preserve annihilation? ─────────────────────────────
print()
print("="*74)
print("THE TEST — does the action preserve the ZD structure?")
print("="*74)
print("  basis action:  e_k -> e_{M.k}  for k in 1..7")
print("                 e_{k+8} -> e_{(M.k)+8}")
print("                 e_0, e_8 fixed  (the two in no Assessor)")
print()

def push(M, d):
    a, b, s = d
    return (act(M, a), act(M, b), s)

preserving, breaking = [], []
for M in G:
    ok = True
    for (d1, d2) in ann:
        if (push(M, d1), push(M, d2)) not in ann:
            ok = False; break
    (preserving if ok else breaking).append(M)

print(f"  group elements PRESERVING annihilation : {len(preserving)} / {len(G)}")
print(f"  group elements BREAKING  annihilation : {len(breaking)} / {len(G)}")

if preserving:
    sorb = {act(M,1) for M in preserving}
    print(f"\n  orbit of strut 1 under the PRESERVING subgroup: {sorted(sorb)}")
    transitive = sorted(sorb) == list(range(1,8))
    print(f"  TRANSITIVE on struts using only preserving elements: {transitive}")
    print()
    if transitive:
        print("  ==> THE CONJECTURE HOLDS. Every pair of charts is joined by a group")
        print("      element that carries the ZD structure with it. The atlas is")
        print("      connected by GROUP ACTION, exactly as Phase 25 proposed.")
    else:
        print("  ==> PARTIAL. The preserving elements form a subgroup that does NOT")
        print("      reach every strut. Some charts cannot be glued this way.")
        print(f"      reachable struts from 1: {sorted(sorb)}")
        print(f"      unreachable: {sorted(set(range(1,8)) - sorb)}")
else:
    print("\n  ==> THE CONJECTURE FAILS as stated: no element of GL(3,2) acting on")
    print("      indices preserves annihilation. The transition maps, if they")
    print("      exist, are not this action.")

# subgroup order check
if preserving:
    print(f"\n  |preserving subgroup| = {len(preserving)}"
          f"   index in GL(3,2) = {len(G)/max(len(preserving),1):.3f}")
    # is it closed under multiplication? (sanity: it should be a subgroup)
    Pset = {tuple(M.flatten()) for M in preserving}
    closed = all(tuple((preserving[i].dot(preserving[j])%2).flatten()) in Pset
                 for i in range(min(12,len(preserving)))
                 for j in range(min(12,len(preserving))))
    print(f"  closed under composition (sampled): {closed}")
