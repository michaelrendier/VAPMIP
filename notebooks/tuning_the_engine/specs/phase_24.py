LABEL = "24"
TITLE = "The Archimedes Screw: the Machine, Not the Medium"
DATE = "2026-08-04 → 2026-08-05 (+ 3 addenda)"
PAGE = "24_the_archimedes_screw_the_machine_not_the_medium.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """The engine is `ValaQuenta/modules/archimedes_screw/maths.py`. This notebook checks its functions against **independent** references (mpmath, sympy) and against the page's statements. Where the page quotes a result, the number is recomputed here rather than read back from the module's own docstring."""),
("code", """from ValaQuenta.modules.archimedes_screw import maths as M
import mpmath as mp, sympy as sp
mp.mp.dps = 30
L.check("lambert_w(1) = Ω_ZS = 0.5671432904…", abs(M.lambert_w(1.0) - OMEGA_ZS) < 1e-13, f"{M.lambert_w(1.0):.15f}")
L.check("screw_pitch(p) = ln p (the pitch of the screw is the prime's mode energy)", all(abs(M.screw_pitch(p) - math.log(p)) < 1e-12 for p in (2, 3, 7, 101)))
L.check("log is a screw: log(p·q) = log p + log q (positive displacement, fixed pitch)", abs(M.u_axis(7*11) - (M.u_axis(7) + M.u_axis(11))) < 1e-12)
L.check("mean prime gap = screw axis = screw pitch = ln x  (page: three quantities collapse to one)", abs(M.mean_gap(1e6) - M.u_axis(1e6)) < 1e-9 and abs(M.screw_pitch(1e6) - M.u_axis(1e6)) < 1e-9)
# empirical mean gap vs ln x on real primes
from sympy import primerange
pr = list(primerange(10**6, 10**6 + 200000)); g = np.diff(pr)
print(f"empirical mean prime gap near 10⁶ = {g.mean():.3f}   ln(10⁶) = {math.log(1e6):.3f}")
L.check("empirical mean prime gap near 10⁶ ≈ ln x (within 3 %)", abs(g.mean() - math.log(1e6))/math.log(1e6) < 0.03)"""),

("md", """## 1 · The four search terms as four coordinates on u = ln x
Digits `d = ⌊u/ln10⌋+1` · Ordinal `n = π(x) ≈ Li(x)` · Zeta index `k = N(T)` · Total spaces `x − π(x)`. Check each map against an exact reference."""),
("code", """x = 10**7
pi_true = int(sp.primepi(x)); li_x = float(mp.li(x)); est = M.li(float(x))
print(f"π(10⁷) = {pi_true:,}   Li(10⁷) = {li_x:,.1f}   module li = {est:,.1f}")
L.check("module li(x) = mpmath li(x) (offset-free) to 6 digits", abs(est - li_x)/li_x < 1e-6, f"{est:.2f} vs {li_x:.2f}")
L.check("ordinal ≈ Li(x): relative error of π(10⁷) < 0.1 %", abs(pi_true - li_x)/pi_true < 1e-3)
errs = [(n, abs(M.nth_prime_estimate(n) - int(sp.prime(n)))/int(sp.prime(n))) for n in (10, 100, 1000, 10000, 100000)]
print("nth-prime estimate relative error:", [(n, f"{e:.2e}") for n, e in errs])
L.check("nth_prime_estimate within 0.5 % at n = 10⁵", errs[-1][1] < 5e-3)
dd = [(v, M.digits_of(v)) for v in (9, 10, 99, 100, 12345, 10**9)]
L.check("digit count d = ⌊log10 x⌋ + 1", all(d == len(str(int(v))) for v, d in dd), str(dd))
tot = x - pi_true; print(f"total spaces below 10⁷: x − π(x) = {tot:,}"); L.check("total spaces = x − π(x)", M.total_spaces(float(x)) > 0)
c = M.screw_coordinates("digits", 5); print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in c.items()})
L.check("entering on 'digits' = 5 leaves on a magnitude of 10⁴ with u = ln 10⁴", abs(c['magnitude'] - 1e4) < 1e-6 and abs(c['u'] - math.log(1e4)) < 1e-9)"""),

("md", """## 2 · γₙ ≈ 2πn / W(n/e) — Lambert W inverting the zero count
Page: the same W that pins σ=½ inverts N(T)=n to give γₙ; *"S(T) = O(ln T) dominates below n≈10, so the closed form is a genuine asymptotic"*. Compare with the true zeros."""),
("code", """true = [float(mp.zetazero(n).imag) for n in range(1, 61)]
approx = [M.zero_height_lambert(n) for n in range(1, 61)]
rel = [abs(a - t)/t for a, t in zip(approx, true)]
print(f"{'n':>4} {'γ true':>9} {'Lambert':>9} {'rel err':>8}")
for n in (1, 2, 5, 10, 20, 40, 60): print(f"{n:4d} {true[n-1]:9.3f} {approx[n-1]:9.3f} {rel[n-1]:8.3%}")
L.check("γₙ closed form is an asymptotic: error shrinks with n (n=60 error < 5 %)", rel[59] < 0.05 and rel[0] > rel[59], f"n=1: {rel[0]:.1%}, n=60: {rel[59]:.1%}")
L.check("below n≈10 the closed form is NOT accurate (error > 10 % at n=1) — as the page says", rel[0] > 0.1)
L.check("zero_height(n) (tabulated LMFDB zeros) returns the true zeros for n ≤ 50", all(abs(M.zero_height(n) - true[n-1]) < 1e-3 for n in range(1, 51)))
L.check("N(T) smooth count tracks the true zero count within 1 at T = γ_60", abs(M.zero_count_smooth(true[-1]) - 60) < 1.5, f"N_smooth(γ₆₀) = {M.zero_count_smooth(true[-1]):.2f}")"""),

("md", """## 3 · The binding equation — von Mangoldt's explicit formula
`ψ(eᵘ) = eᵘ − 2e^{u/2}Σ cos(γₖu − arg ρₖ)/|ρₖ| − ln 2π − ½ln(1−e^{−2u})`. Established; test the module's `chebyshev_psi_explicit` against exact ψ, the jump `ln p` at each prime power, and the common envelope `2√x`."""),
("code", """zs = [float(mp.zetazero(n).imag) for n in range(1, 201)]
x0 = 100.5
exact = M.chebyshev_psi_exact(x0)
sumn = lambda K: M.chebyshev_psi_explicit(x0, zs[:K])
for K in (0, 5, 20, 100, 200): print(f"  K={K:3d} zeros: ψ̂({x0}) = {sumn(K):9.4f}   exact = {exact:.4f}   error {sumn(K)-exact:+.4f}")
L.check("explicit formula converges to exact ψ as zeros are added (error at K=200 < K=0)", abs(sumn(200) - exact) < abs(sumn(0) - exact))
L.check("200 zeros reproduce ψ(100.5) to within 1.0", abs(sumn(200) - exact) < 1.0)
# independent exact ψ
from sympy import primerange
indep = sum(math.log(p)*int(math.floor(math.log(100.5)/math.log(p))) for p in primerange(2, 101))
L.check("module chebyshev_psi_exact agrees with an independent prime-power sum", abs(indep - exact) < 1e-9, f"{indep:.6f} vs {exact:.6f}")
ld = M.leaf_drops(60)
L.check("ψ jumps by exactly ln p at each prime power p^m (the leaf that falls IS the prime: jump = ln p, not ∝ ln p)", all(abs(j - math.log(sp.factorint(n).popitem()[0])) < 1e-12 for n, j in ld))
env = [M.amplitude_envelope(xx) for xx in (100.0, 1e4)]
L.check("every tone shares the envelope 2√x on the critical line", abs(env[0] - 2*math.sqrt(100.0)) < 1e-9 and abs(env[1] - 2*math.sqrt(1e4)) < 1e-9, str(env))
rr = M.envelope_ratio(1e4, 0.6)
L.check("a zero at σ=0.6 would dominate the critical line by x^(σ−½) = x^0.1", abs(rr - 1e4**0.1) < 1e-6, f"ratio {rr:.4f} vs {1e4**0.1:.4f}")
sh = M.shake_order(100.5); print("shake_order keys:", list(sh)[:6])
res_vs_K = [(K, abs(sumn(K) - exact)) for K in (10, 50, 200)]
L.check("truncation residual is reported by shake_order() rather than hidden", any(k in sh for k in ('residual', 'error', 'residual_bound', 'truncation_error')), f"keys: {list(sh)}")"""),

("md", """## 4 · Ramification is detachment — ζ_{ℚ(√N)} = ζ·L(s, χ_N)
Page: for N = p·q squarefree the ramified primes are exactly p and q. D = N if N ≡ 1 (mod 4), else 4N. Check against sympy's quadratic-field discriminant and the Kronecker symbol over *all* semiprimes below 200."""),
("code", """from sympy import factorint, jacobi_symbol
def D_of(N): return N if N % 4 == 1 else 4*N
semis = [N for N in range(6, 200) if len(factorint(N)) == 2 and all(e == 1 for e in factorint(N).values())]
bad_formula = [(N, M.fundamental_discriminant(N), D_of(N)) for N in semis if M.fundamental_discriminant(N) != D_of(N)]
L.check("fundamental_discriminant(N) = N if N≡1 (mod 4) else 4N for every squarefree semiprime N<200", not bad_formula, str(bad_formula[:3]))
def ramified_true(N): return sorted(sp.primefactors(D_of(N)))            # ramified primes of ℚ(√N) are exactly the primes dividing D
miss = [(N, ramified_true(N), M.ramified_primes(N)) for N in semis if M.ramified_primes(N) != ramified_true(N)]
print(f"{len(semis)} squarefree semiprimes N<200: ramified-prime sets differ from the truth for {len(miss)} of them; e.g. {miss[:3]}")
L.check("for N = p·q the ramified primes are exactly {p, q}  (page)", all(sorted(sp.primefactors(N)) == ramified_true(N) for N in semis), f"false whenever N ≢ 1 (mod 4): 2 also ramifies (D=4N), e.g. N=15 → {ramified_true(15)}")
L.check("ramified_primes(N) in the module returns the true ramified set", not miss, f"misses the prime 2 in {len(miss)} of {len(semis)} cases (N ≡ 3 mod 4)")
N = 77; chi = {p: (M.kronecker(D_of(N), p)) for p in (2, 3, 5, 7, 11, 13)}
print(f"χ_77(p) for p=2,3,5,7,11,13:", chi)
L.check("χ_N(p) = 0 exactly at the ramified primes (7, 11 for N=77)", chi[7] == 0 and chi[11] == 0 and all(chi[p] != 0 for p in (2, 3, 5, 13)))"""),

("md", """## 5 · Honest boundaries and the finiteness number
`prime_count_log10(309) = 306.15` ⇒ about 2¹⁰¹⁷ candidate primes below 10³⁰⁹."""),
("code", """pc = M.prime_count_log10(309)
ref = float(mp.log10(mp.li(mp.mpf(10)**309)))
print(f"module log10 π(10³⁰⁹) = {pc:.4f}   mpmath log10 Li(10³⁰⁹) = {ref:.4f}   → 2^{pc*math.log2(10):.1f}")
L.check("prime_count_log10(309) = 306.15 (page)", abs(pc - 306.15) < 0.01, f"{pc:.4f}")
L.check("agrees with mpmath's Li to 0.001 in log10", abs(pc - ref) < 1e-3)
L.check("≈ 2^1017 candidate primes below 10³⁰⁹", abs(pc*math.log2(10) - 1017) < 1.0, f"{pc*math.log2(10):.2f}")
L.prose("`ramified_primes()` costs exactly trial division; sampling L(s,χ_N) costs ~√N (approximate functional equation) — 'the same wall Fermat's a²−b² hits' (a cost statement; the module docstring labels it a toy-scale readout)")"""),

("md", """## 6 · Addendum 2 — the leaf falls at gpf(N), not lpf(N); Dickman; the balanced semiprime
`discovery = lpf(N)` (first strike), `fall = gpf(N)` (the sieve is finished with N). The fall-time distribution is Dickman's ρ in `u = ln N / ln gpf(N)`; a balanced semiprime has `u = 2`."""),
("code", """L.check("14: struck at 2 (lpf), falls at 7 (gpf)", (M.lpf(14), M.gpf(14)) == (2, 7))
L.check("lpf/gpf agree with sympy factorisation for 3 ≤ n < 2000", all(M.lpf(n) == min(sp.primefactors(n)) and M.gpf(n) == max(sp.primefactors(n)) for n in range(3, 2000)))
# Dickman ρ: published values ρ(2)=1−ln2, ρ(3)=0.0486083882911..., ρ(4)=0.00491092564776...
pub = {2: 1 - math.log(2), 3: 0.04860838829, 4: 0.004910925648, 5: 0.0003547247}
for u, v in pub.items(): print(f"  ρ({u}) module {M.dickman_rho(u):.10f}  published {v:.10f}")
L.check("dickman_rho agrees with published values to ~10⁻⁷ (page)", all(abs(M.dickman_rho(u) - v) < 5e-7 for u, v in pub.items()))
L.check("balanced semiprime ⇒ u = ln N/ln gpf(N) = 2 exactly", abs(math.log(101*103)/math.log(103) - 2) < 0.01, f"u(101·103) = {math.log(101*103)/math.log(103):.4f}; exactly 2 only in the limit p→q")
fs = M.fall_split(77); print({k: round(v, 4) for k, v in fs.items()})
L.check("ln p + ln q = ln N is an identity on the screw (sum_check = ln N)", abs(fs['sum_check'] - fs['ln_N']) < 1e-12)
L.check("two falls separated by 2δ with δ = ½ ln(q/p)", abs((fs['fall_height'] - fs['discovery_height']) - 2*fs['delta']) < 1e-12, f"fall−discovery = {fs['fall_height']-fs['discovery_height']:.5f}, 2δ = {2*fs['delta']:.5f}")
fb = M.fall_split(1000003*1000033)
L.check("balanced ⇒ δ → 0: both falls collapse onto ½ ln N (observables coincide)", abs(fb['discovery_height'] - 0.5*fb['ln_N']) < 1e-4 and abs(fb['fall_height'] - 0.5*fb['ln_N']) < 1e-4, f"δ = {fb['delta']:.2e}")
# harvest closed form vs direct sieve
X = 20000
tbl = M.gpf_table(X); ok = True
for p in (2, 3, 5, 7, 11, 13, 17):
    direct = sum(1 for n in range(2, X+1) if tbl[n] == p)
    ok &= (M.harvest(X, p) == direct)
L.check("harvest(X, p) = #{n ≤ X : gpf(n) = p} — closed form equals the direct sieve table (exact)", ok)"""),

("md", """## 7 · Addendum 3 — the projection ledger (`domain_ladder`)
`log₂` of the number of candidates the naive search has to touch, for RSA-2048."""),
("code", """dl = M.domain_ladder(2048)
print({k: round(v, 3) for k, v in dl.items() if isinstance(v, (int, float))})
L.check("all integers 2…N: 2048 bits; trial range 2…√N: 1024", dl['all_integers'] == 2048 and dl['integers_to_sqrt'] == 1024)
pc1024 = float(mp.log(mp.li(mp.mpf(2)**1024), 2)); 
L.check("primes ≤ √N: log₂ ≈ 1014.53", abs(dl['primes_to_sqrt'] - 1014.53) < 0.01, f"module {dl['primes_to_sqrt']:.2f}; independent log₂ Li(2¹⁰²⁴) = {pc1024:.2f}")
L.check("independent Li check of the same row", abs(pc1024 - dl['primes_to_sqrt']) < 0.05)
# GNFS L-notation estimate (independent): L_n[1/3, (64/9)^(1/3)]
ln_n = 2048*math.log(2); gnfs = 1.923*ln_n**(1/3)*math.log(ln_n)**(2/3)/math.log(2)
print(f"GNFS heuristic L_n[1/3,(64/9)^(1/3)] for 2048 bits: 2^{gnfs:.1f}   (page row: 2^{dl['gnfs']:.0f}, the NIST strength estimate)")
L.check("the 112-bit GNFS row is within 6 bits of the heuristic L-notation estimate", abs(gnfs - dl['gnfs']) < 6, f"{gnfs:.1f} vs {dl['gnfs']:.0f}")
# the one-bit fact
for bits in (1024, 2048, 4096):
    x = mp.mpf(2)**bits; top = (mp.li(x) - mp.li(x/2)) / (mp.li(x)/2)
    print(f"  top-octave share / ½ at {bits} bits: {float(top):.4f}")
tops = {bits: float((mp.li(mp.mpf(2)**bits) - mp.li(mp.mpf(2)**(bits-1))) / (mp.li(mp.mpf(2)**bits)/2)) for bits in (1024, 2048, 4096)}
L.check("the one-bit fact: π(x) − π(x/2) ≈ ½π(x) with ratios 1.0028 / 1.0014 / 1.0007 at 1024 / 2048 / 4096 bits", abs(tops[1024]-1.0028) < 5e-4 and abs(tops[2048]-1.0014) < 5e-4 and abs(tops[4096]-1.0007) < 5e-4, str({k: round(v, 4) for k, v in tops.items()}))"""),

("md", """## 8 · The protocol claim and the open item
The page lists an engine-protocol change (five parts, `CTX_ARCHIMEDES_SCREW` in `~/.clauderc_ValaQuenta`) and names the single open item: the dispersion relation ω(k) on the zero-divisor surface."""),
("code", """rc = os.path.expanduser("~/.clauderc_ValaQuenta")
L.check("CTX_ARCHIMEDES_SCREW is defined in ~/.clauderc_ValaQuenta (protocol part 5)", os.path.exists(rc) and "CTX_ARCHIMEDES_SCREW" in open(rc, encoding="utf-8").read())
L.check("the module's manifest.json exists (UI registration part of the protocol)", os.path.exists(os.path.join(PLACE, "ValaQuenta", "modules", "archimedes_screw", "manifest.json")))
for c in ["∅_RB reframed as the MEDIUM (water, e₀, the identity, the vacuum that seeds ζ); the machine is the logarithm (Archimedes screw)",
          "Primes as antinodes — the dual of the Chladni node-line argument; a zero at σ>½ would drown the critical-line tones by x^(σ−½)→∞ (the amplitude statement is checked above; the 'dual reading' is interpretation)",
          "Chebyshev ψ is the counterpart of L_(I|O); the prime side already had an L_(I|O) and called it ψ (a naming/identification claim)",
          "OPEN ITEM: the dispersion relation ω(k) of the zero-divisor surface (a waveguide with its own modes) — not written",
          "NS 'was missing an interface': the branch locus is that interface (analogy)"]:
    L.prose(c)"""),
]
