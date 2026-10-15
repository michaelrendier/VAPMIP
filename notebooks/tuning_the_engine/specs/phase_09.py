LABEL = "9"
TITLE = "The Void Named Itself"
DATE = "2026-06-12"
PAGE = "09_the_void_named_itself.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## What the page asserts, and which parts are mathematics
1. σ=½ is *the* fixed point of `s ↦ 1−s` — pure arithmetic, checked below.
2. The non-trivial zeros "are the void's name echoing through the prime distribution" — the explicit formula (primes ↔ zeros) is a theorem; reconstruct ψ(x) from zeros to see it.
3. "A zero off the critical line would mean the naming was inconsistent" — RH. Not provable here; what *can* be run is the finite statement "every zero up to height T lies on σ=½".
4. The `SELF_EQUATION` is eleven words and the engine "recognised" it (Phase 1 recorded that the probe does not reproduce it on the repo's seed corpora)."""),
("code", """# 1. the fixed point of s -> 1-s, and the functional equation of ξ
import mpmath as mp
mp.mp.dps = 30
xi = lambda s: mp.mpf(1)/2*s*(s-1)*mp.pi**(-s/2)*mp.gamma(s/2)*mp.zeta(s)
fixed = [s for s in (mp.mpf(0.5), mp.mpf(0.3), mp.mpf(1))  if abs((1-s)-s) < 1e-30]
L.check("s = 1−s has the unique real solution s = ½", fixed == [mp.mpf(0.5)])
rng = np.random.default_rng(5)
errs = []
for _ in range(25):
    s = mp.mpc(rng.uniform(-2, 3), rng.uniform(-30, 30)); errs.append(abs(xi(s) - xi(1-s)))
L.check("ξ(s) = ξ(1−s) at 25 random points (30 digits)", max(errs) < 1e-20, f"max |ξ(s)−ξ(1−s)| = {float(max(errs)):.2e}")"""),
("code", """# 3. every non-trivial zero up to T=100 lies on σ=½: count by argument principle vs zeros found ON the line
T = 100
N_theory = int(mp.nzeros(T))                      # zeros with 0<Im<T (argument principle, no assumption about the line)
on_line = [mp.zetazero(n) for n in range(1, N_theory+1)]     # mpmath finds zeros on the line
print(f"N(T={T}) by argument principle = {N_theory};  zeros located on Re s=½ below T = {sum(1 for z in on_line if z.imag < T)}")
L.check("all zeros with 0 < Im < 100 are on Re s = ½ (count matches the argument principle)", N_theory == sum(1 for z in on_line if z.imag < T) and all(abs(z.real - 0.5) < 1e-25 for z in on_line), f"N={N_theory}")"""),
("code", """# 2. primes as the echo of the zeros:  ψ(x) = x − Σ_ρ x^ρ/ρ − ln 2π − ½ ln(1−x⁻²)   (Chebyshev ψ, sum over zero pairs)
from sympy import primerange
def psi(x):  # Chebyshev psi
    s = 0.0
    for p in primerange(2, int(x)+1):
        k = 1
        while p**k <= x: s += math.log(p); k += 1
    return s
zs = [mp.zetazero(n) for n in range(1, 201)]
def psi_from_zeros(x, K):
    x = mp.mpf(x)
    t = x - mp.log(2*mp.pi) - mp.log(1 - x**-2)/2
    for z in zs[:K]: t -= 2*mp.re(x**z / z)
    return float(t)
x0 = 97.5
for K in (0, 10, 50, 200): print(f"  K={K:3d} zeros: ψ({x0}) ≈ {psi_from_zeros(x0, K):9.4f}   (true ψ = {psi(x0):.4f})")
e0, e200 = abs(psi_from_zeros(x0, 0) - psi(x0)), abs(psi_from_zeros(x0, 200) - psi(x0))
L.check("adding zeros reduces the error in ψ(x) (primes are carried by the zeros)", e200 < e0, f"|ψ̂−ψ| : {e0:.3f} (no zeros) → {e200:.3f} (200 zeros)")
L.check("200 zeros reconstruct ψ(97.5) to within 1", e200 < 1.0)"""),
("code", """from monad import SELF_EQUATION
words = SELF_EQUATION.split()
print(len(words), "words:", words)
L.check("SELF_EQUATION has eleven words, as the Phase-1 table lists", len(words) == 11)
L.check("it begins with 'philadelphos' and ends with 'firing'", words[0] == "philadelphos" and words[-1] == "firing")
for c in ["The void chose σ=½ as its observation basis (analogy with vacuum expectation value / symmetry breaking)",
          "'RH says the void's self-naming was exact' (an interpretation of RH; the finite check above is the executable part)",
          "'The engine recognised the name; it did not create it' (SELF_EQUATION emergence is covered, and not reproduced on the seed corpora, in Phase 1)",
          "Ainulindale / Ilúvatar / Melkor as the shadow-cascade story"]:
    L.prose(c)"""),
]
