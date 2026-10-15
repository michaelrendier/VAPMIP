LABEL = "6"
TITLE = "Definition from Above: The Shadow Cascade"
DATE = "2026-06-10"
PAGE = "06_definition_from_above_the_shadow_cascade.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The Cayley–Dickson ladder — which property is lost at each doubling?
Page: ℝ→ℂ (ordering), ℂ→ℍ (commutativity), ℍ→𝕆 (associativity), 𝕆→𝕊 (alternativity ⇒ zero-divisors).
This is the one thing in Phase 6 that is pure algebra, so compute it with the repo's `cd_mul` at n = 1, 2, 4, 8, 16 (basis-unit tests for commutativity/associativity/zero-divisors; random elements for alternativity, because basis units alone are alternative even in 𝕊)."""),
("code", """from _sedenion import cd_mul, e
def tests(n):
    E = [e(i, n) for i in range(n)]
    comm  = all(np.allclose(cd_mul(E[i],E[j]), cd_mul(E[j],E[i])) for i in range(n) for j in range(n))
    assoc = all(np.allclose(cd_mul(cd_mul(E[i],E[j]),E[k]), cd_mul(E[i],cd_mul(E[j],E[k]))) for i in range(n) for j in range(n) for k in range(n)) if n <= 16 else None
    rg = np.random.default_rng(11)
    def alt1(a, b): return np.allclose(cd_mul(cd_mul(a,a),b), cd_mul(a,cd_mul(a,b))) and np.allclose(cd_mul(a,cd_mul(b,b)), cd_mul(cd_mul(a,b),b))
    # basis units are alternative even in 𝕊; only GENERIC elements expose the failure, so test random ones
    alt   = all(alt1(rg.normal(size=n), rg.normal(size=n)) for _ in range(40)) if n > 1 else True
    zd    = any(max(abs(x) for x in cd_mul(E[i],E[j])) < 1e-12 for i in range(1,n) for j in range(1,n)) if n>1 else False
    return comm, assoc, alt, zd
names = {1:"ℝ", 2:"ℂ", 4:"ℍ", 8:"𝕆", 16:"𝕊"}
tab = {}
print(f"{'':3}{'n':>3}  commutative  associative  alternative  basis-ZD")
for n in (1, 2, 4, 8, 16):
    tab[n] = tests(n); c, s_, al, z = tab[n]
    print(f"{names[n]:3}{n:3}  {str(c):12} {str(s_):12} {str(al):12} {str(z)}")
L.check("ℂ is commutative, ℍ is not", tab[2][0] and not tab[4][0])
L.check("ℍ is associative, 𝕆 is not", tab[4][1] and not tab[8][1])
L.check("𝕆 is alternative, 𝕊 is not", tab[8][2] and not tab[16][2])
L.check("basis-unit zero-divisors first appear at 𝕊 (none in ℝ, ℂ, ℍ, 𝕆)", not any(tab[n][3] for n in (1,2,4,8)), f"𝕊 basis-unit pairs with e_i·e_j=0: {tab[16][3]} (the sedenion zero-divisors are sums e_a±e_b, not single units — see Phase 2)")
vecs, pairs = zd_vectors()
L.check("zero-divisors of 𝕊 exist as e_a ± e_b (84 of them)", len({k for p in pairs for k in p}) == 84)"""),
("md", """### Where does the ℝ→ℂ→ℍ shadow actually live?
The page also gives the order-loss: ℂ has no total order compatible with its field structure. That is a theorem (no ordered-field structure on ℂ since i²=−1<0 contradicts squares ≥ 0) — shown below, not simulated."""),
("code", """# In any ordered field, x² ≥ 0 for all x. In ℂ, i² = −1 < 0 .
i = 1j
L.check("ℂ cannot be an ordered field: i² = −1 < 0 contradicts x² ≥ 0", (i*i).real < 0)
# the Lie bracket as shadow of ℍ's non-commutativity: [i,j] = 2k in the quaternions
qi, qj, qk = e(1,4), e(2,4), e(3,4)
br = np.array(cd_mul(qi,qj)) - np.array(cd_mul(qj,qi))
L.check("quaternion bracket [i,j] = 2k (the su(2) structure the rotor inherits)", np.allclose(br, 2*np.array(qk)), f"[i,j] = {br}")
# three bracket relations cyclic
ok = all(np.allclose(np.array(cd_mul(a,b))-np.array(cd_mul(b,a)), 2*np.array(c)) for a,b,c in [(qi,qj,qk),(qj,qk,qi),(qk,qi,qj)])
L.check("[i,j]=2k, [j,k]=2i, [k,i]=2j (cyclic su(2))", ok)"""),
("md", """### The 'three witnesses' as one structure — what can and cannot be run
Gödel / Noether / Riemann are cited as one law (a system cannot define itself from within; the gaps are the shadow of the layer above). That is an interpretation. The only part with an executable counterpart is the algebra above; the rest is recorded as PROSE."""),
("code", """for c in ["'You can only define a system from above it' — Gödel, Noether, Riemann as three shadows of one law",
          "σ=½ is the shadow of the ξ(s)=ξ(1−s) symmetry on the engine dynamics ('convergence is the shadow falling')",
          "The engine is su(2) because su(2) is the shadow of ℍ in 𝕆 (the su(2) fact is checked above; 'because shadow' is interpretation)",
          "Zero-divisors as the contact surface between defining and defined layer"]:
    L.prose(c)"""),
]
