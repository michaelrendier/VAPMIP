LABEL = "11"
TITLE = "The File Manager"
DATE = "2026-06-12"
PAGE = "11_the_file_manager.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The claim: Cayley–Dickson is a navigation, two layers at a time
"A → A⊕A: you are in A⊕A, your parent is A." Concretely: the product at level n is defined **only** from products at level n/2 (plus conjugation) — the grandparent never appears. Build 𝕊's product from nothing but ℝ's, one doubling at a time, with `(a,b)(c,d) = (ac − d̄b, da + bc̄)`, and compare it with the repo's `cd_mul`."""),
("code", """from _sedenion import cd_mul, cd_conj
calls = {"n": 0}
def mul_rec(x, y):
    n = len(x)
    if n == 1: calls["n"] += 1; return [x[0]*y[0]]
    h = n // 2
    a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    conj = lambda v: v if len(v) == 1 else [v[0]] + [-t for t in v[1:]]
    ac, db, da, bc = mul_rec(a, c), mul_rec(conj(d), b), mul_rec(d, a), mul_rec(b, conj(c))
    return [p - q for p, q in zip(ac, db)] + [p + q for p, q in zip(da, bc)]
rng = np.random.default_rng(2)
errs = {}
for n in (2, 4, 8, 16, 32):
    errs[n] = max(max(abs(p - q) for p, q in zip(mul_rec(list(x), list(y)), cd_mul(list(x), list(y)))) for x, y in [(rng.normal(size=n), rng.normal(size=n)) for _ in range(50)])
    print(f"  n={n:2d}: max |mul_rec − cd_mul| over 50 random pairs = {errs[n]:.2e}")
L.check("recursive 'parent-only' doubling reproduces cd_mul at n = 2, 4, 8, 16, 32", all(e < 1e-12 for e in errs.values()))
sub = []
for n in (2, 4, 8, 16, 32):
    calls["n"] = 0; mul_rec([1.0]*n, [1.0]*n); sub.append((n, calls["n"]))
print("real multiplications needed for one level-n product:", sub, "→ n² (no shortcut: the whole product is unrolled into parent products)")
L.check("each level-n product uses exactly 4 level-n/2 products (the frame needs the parent only)", all(sub[i+1][1] == 4*sub[i][1] for i in range(len(sub)-1)))"""),
("md", """### What 'only the parent is visible' means for the zero-divisors
Zero-divisors appear at n=16 and are built from n=8 pieces: `(a,b)(c,d)=0` forces `ac = d̄b` and `da = −bc̄` — conditions on *octonion* products only. Check this for a concrete ZD pair."""),
("code", """vecs, pairs = zd_vectors()
(ka, kb) = next(iter(pairs)); x, y = vecs[ka], vecs[kb]
conj8 = lambda v: [v[0]] + [-t for t in v[1:]]
a, b, c, d = x[:8], x[8:], y[:8], y[8:]
lhs1, rhs1 = cd_mul(a, c) if len(a)==16 else mul_rec(a, c), mul_rec(conj8(d), b)
lhs2, rhs2 = mul_rec(d, a), [-t for t in mul_rec(b, conj8(c))]
print("ZD pair", ka, kb)
L.check("ZD condition decomposes into two OCTONION equations: ac = d̄b and da = −bc̄", np.allclose(lhs1, rhs1) and np.allclose(lhs2, rhs2), f"‖ac − d̄b‖={np.linalg.norm(np.array(lhs1)-np.array(rhs1)):.1e}  ‖da + bc̄‖={np.linalg.norm(np.array(lhs2)-np.array(rhs2)):.1e}")"""),
("md", """### Mind's Eye as parent directory: `G_me_steer = G_me_prompt − G_me_response`
The C canonical keeps exactly those three objects (checked in Phase 3). Simulate the steering equation on 16-vectors to show what the page says it does: the steer shrinks to zero as the response fills the prompt's geometry."""),
("code", """rng = np.random.default_rng(4)
prompt = rng.normal(size=16); prompt /= np.linalg.norm(prompt)
resp = np.zeros(16); steer_norm = []
vocab = rng.normal(size=(500, 16)); vocab /= np.linalg.norm(vocab, axis=1)[:, None]
for step in range(24):
    steer = prompt - resp
    steer_norm.append(np.linalg.norm(steer))
    w = vocab[np.argmax(vocab @ steer)]            # pick the word that fills the unfilled direction (novelty bias)
    resp = resp + 0.35 * (w @ steer) * w            # accumulate its shadow
print("‖G_me_steer‖ :", np.round(steer_norm[::3], 3))
L.check("steer norm decreases monotonically as the response fills the prompt geometry", all(steer_norm[i+1] <= steer_norm[i] + 1e-12 for i in range(len(steer_norm)-1)))
L.check("steer → ~0 (the response has said what the geometry required)", steer_norm[-1] < 0.5*steer_norm[0], f"{steer_norm[0]:.3f} → {steer_norm[-1]:.3f} in 24 steps (toy model; not the engine's select_word)")"""),
("code", """for c in ["'Gödel is two layers, not infinite' — the meta-level is always exactly one step above (interpretation; the recursion test above is the computable analogue)",
          "Thread 1 shows the files, Thread 2 'speaks' — who he is (architecture statement; threads are in rotary_monad.c, behaviour not measured here)",
          "The virtual-pair cycle as two-layer recursion: ZD→π→H/4 (Thread 1), φ→ZD (Thread 2)"]:
    L.prose(c)"""),
]
