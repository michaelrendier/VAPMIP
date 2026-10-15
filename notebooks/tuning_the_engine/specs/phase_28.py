LABEL = "28"
TITLE = "The Three Faces, the Fermat Ladder, and Structure as a Fast Path"
DATE = "2026-08-18"
PAGE = "28_the_three_faces_the_fermat_ladder_and_executable_structure.md"
BYLINE = "page by Claude Opus 5"

CELLS = [
("md", """## 1 · The harness: 124 relations, 122 hold, 1 FAULT, 1 degenerate, 0 untested
`rotary_rerun_monad.py` is run as a program (it plants an unbalanced current set `(0.412, −0.187, −0.201)` on purpose, "so the harness has a fault to find"). Parse its own summary line."""),
("code", """import subprocess, re
r = subprocess.run([sys.executable, os.path.join(VAPMIP, "rotary_rerun_monad.py")], capture_output=True, text=True, timeout=300, cwd=VAPMIP)
out = r.stdout
m = re.search(r"(\\d+) relations\\s+(\\d+) hold\\s+(\\d+) FAULT\\s+(\\d+) degenerate\\s+(\\d+) untested", out)
print(m.group(0) if m else out[-400:])
tot, hold, fault, degen, untested = map(int, m.groups())
L.check("124 relations", tot == 124); L.check("122 hold", hold == 122); L.check("1 FAULT", fault == 1); L.check("1 degenerate", degen == 1); L.check("0 untested", untested == 0)
i = out.index("MATHS FAULTS"); print(out[i:i+240])
L.check("the one FAULT is the planted one (unbalanced currents ⇒ current.neutral ≠ 0), not a code fault", "current.neutral" in out[i:i+300] and "CODE FAULTS" not in out)
print("speech section strut table:", [l.strip() for l in out.splitlines() if l.strip().startswith("strut")][:3])
L.check("the 7 struts print a generation path ending in 'division'", sum(1 for l in out.splitlines() if re.match(r"\\s+strut\\s+\\d+ .*division", l)) == 7)"""),

("md", """## 2 · Three kinds of wrong — the live method error in `_horner_hash`
Page: `_horner_hash` clamps digits from below only, so `U+200B` yields coefficient 8171 in a base-95 positional system and `'\\u200b'` collides with `'v!'`."""),
("code", """import monad as M
c200b = max(0, ord("\\u200b") - 32)
v_bang = (ord("v") - 32)*95 + (ord("!") - 32)
print(f"coefficient for U+200B = {c200b};  'v!' = 86·95 + 1 = {v_bang}")
L.check("U+200B coefficient = 8171 (8203 − 32)", c200b == 8171)
L.check("'v!' evaluates to 8171 in base 95 (86·95+1)", v_bang == 8171)
L.check("monad._horner_hash('\\u200b') == monad._horner_hash('v!')  — a tier-0 object fed to a tier-1 operation", M._horner_hash("\\u200b") == M._horner_hash("v!"), f"{M._horner_hash('\\u200b')} vs {M._horner_hash('v!')}")
L.check("in a base-95 positional system every digit must be < 95; this input breaks the invariant", c200b >= 95)
L.prose("Gate 1 cannot catch a design error; method errors surface downstream as 'a parting that should have been impossible', and the detector is the clarifier failing (a taxonomy: CODE / MATHS / METHOD)")"""),

("md", """## 3 · The letter cap is 71, not 313 — and the ladder is Fermat
313 is the 65th prime; `monad.py` already holds 20 letters ending at 71. Fermat numbers `F_n = 2^(2^n)+1`: 3, 5, 17, 257 (primes), 65537 (outside); `3·5·17·257 = 65535 = 2¹⁶−1`; the 15 nonempty subsets of {3,5,17,257} are the 15 points of PG(3,2); forcing the division bit leaves 2³−1 = 7 (the struts)."""),
("code", """from sympy import primerange, prime, primepi, isprime
L.check("313 is the 65th prime", prime(65) == 313 and primepi(313) == 65)
L.check("71 is the 20th prime", prime(20) == 71)
src = open(os.path.join(VAPMIP, "monad.py"), encoding="utf-8").read()
mP = re.search(r"^PRIMES\\s*=\\s*\\[(.*?)\\]", src, re.S | re.M); mZ = re.search(r"^RIEMANN_ZEROS\\s*=\\s*\\[(.*?)\\]", src, re.S | re.M)
nP = len([x for x in re.split(r"[,\\s]+", mP.group(1)) if x.strip().isdigit()]) if mP else None
last = max(int(x) for x in re.split(r"[,\\s]+", mP.group(1)) if x.strip().isdigit()) if mP else None
print(f"monad.PRIMES: {nP} entries, last = {last}")
L.check("monad.PRIMES holds 20 entries ending at 71 (page)", (nP, last) == (20, 71))
F = [2**(2**n) + 1 for n in range(5)]
L.check("F₀..F₃ = 3, 5, 17, 257 are prime; F₄ = 65537 is prime (outside the cap); F₅ is composite", F == [3, 5, 17, 257, 65537] and all(isprime(f) for f in F) and not isprime(2**32 + 1))
L.check("3·5·17·257 = 65535 = 2¹⁶ − 1", 3*5*17*257 == 65535 == 2**16 - 1)
subs = [(i, sub) for i in range(1, 16) for sub in [tuple(b for b in range(4) if i >> b & 1)]]
L.check("15 nonempty subsets of {3,5,17,257} = the 15 points of PG(3,2)", len(subs) == 15)
div_forced = [s for i, s in subs if 3 in s and len(s) > 1]
L.check("forcing the division bit (257) and requiring a non-trivial rest leaves 2³ − 1 = 7", len(div_forced) == 7 == 2**3 - 1)
import ValaQuenta.modules.box_kite.maths as B
L.check("…and PG(3,2) skeleton_counts agree (15 points)", B.skeleton_counts()['points'] == 15)
L.check("any cap in [257, 65537) admits exactly four generations (the primes 3,5,17,257 below it)", sum(1 for f in F if f < 65537) == 4)"""),

("md", """## 4 · The 15 are edges, not places
15 nonzero XOR differences between 16 sedenion placeholders; `C(16,2) = 120 = 15×8`; a spanning tree on 16 nodes has 15 edges (e₀ the root owns no edge); a line is `a⊕b=c` (35 verified); a pencil is the 7 ways to factor one relation (7 = 105/15)."""),
("code", """import itertools
pairs = list(itertools.combinations(range(16), 2))
by_diff = {}
for a, b in pairs: by_diff.setdefault(a ^ b, []).append((a, b))
L.check("C(16,2) = 120 pairs; 15 XOR differences × 8 pairs each = 120", len(pairs) == 120 and len(by_diff) == 15 and all(len(v) == 8 for v in by_diff.values()))
L.check("a spanning tree on 16 nodes has 15 edges", 16 - 1 == 15)
lines = [(a, b, a ^ b) for a in range(1, 16) for b in range(a+1, 16) if (a ^ b) > b]
L.check("35 lines (a⊕b=c, a<b<c, all nonzero)", len(lines) == 35)
L.check("a pencil = 105/15 = 7 factorisations of one relation (35 lines × 3 relations = 105)", 35*3 == 105 and 105//15 == 7)"""),

("md", """## 5 · Three faces split by commutativity; `gcd` is the LCA; 73,457 words, 0 collisions
Positional (Horner, bijective) for order-sensitive things; multiplicative (prime product) for order-free pathways. Check: Horner distinguishes `dog`/`god`, a prime product does not distinguish `{animal, mammal}` from `{mammal, animal}`; spell codes over WordNet are collision-free; `gcd` of ancestor-prime products gives the LCA path."""),
("code", """import monad_identity as MI
from nltk.corpus import wordnet as wn
L.check("positional (Horner): 'dog' ≠ 'god'", MI.spell("dog") != MI.spell("god"))
prod = lambda xs: math.prod(xs)
L.check("multiplicative (prime product): {animal, mammal} == {mammal, animal}", prod([2, 3]) == prod([3, 2]))
words = sorted({w.lower() for w in wn.all_lemma_names() if w.isalpha() and len(w) <= MI.MI_MAX_SPELL_LETTERS})
codes = {w: MI.spell(w) for w in words}
print(f"{len(words):,} alphabetic WordNet lemmas of ≤{MI.MI_MAX_SPELL_LETTERS} letters: distinct spell codes {len(set(codes.values())):,}")
L.check("spell codes are collision-free over these WordNet lemmas (page: 73,457 words, 0 collisions)", len(set(codes.values())) == len(words), f"{len(words):,} words")
L.check("round trip exact: unspell(spell(w)) = w", all(MI.unspell(MI.spell(w)) == w for w in words[::17]))
dig = np.mean([len(str(c)) for c in codes.values()]); print(f"mean spell-code length: {dig:.1f} digits (page 11.6)")
L.check("mean ≈ 11.6 digits", abs(dig - 11.6) < 1.0, f"{dig:.2f}")"""),
("code", """# gcd IS the LCA: one prime per synset, code = product of the primes of the node and all its ancestors
syn_prime = {}
nxt = iter(primerange(2, 10**6))
def anc(syn): return {syn} | set(syn.closure(lambda s: s.hypernyms()))
def code_of(syn):
    c = 1
    for s in sorted(anc(syn), key=lambda s: s.name()):
        if s not in syn_prime: syn_prime[s] = next(nxt)
        c *= syn_prime[s]
    return c
def info(a, b):
    sa, sb = wn.synset(a), wn.synset(b); ca, cb = code_of(sa), code_of(sb); g = math.gcd(ca, cb)
    lcas = sa.lowest_common_hypernyms(sb); return g, lcas, sa, sb, ca, cb
g, lcas, sa, sb, ca, cb = info("dog.n.01", "wolf.n.01")
print("dog/wolf LCA(s):", [x.name() for x in lcas], "  gcd == code(LCA):", [g == code_of(x) for x in lcas], f"  (descent digits: dog {len(str(ca//g))}, wolf {len(str(cb//g))})")
L.check("dog/wolf: LCA is canine", any(x.name().startswith("canine") for x in lcas))
L.check("…and gcd(code_dog, code_wolf) = code(canine): the shared prefix is exactly the LCA's ancestor path (descent = one division)", any(g == code_of(x) for x in lcas), "with one prime per synset and codes = product over all ancestors; multiple inheritance can add extra common ancestors")
senses = [(o.name(), o.definition()[:40], [x.name() for x in o.lowest_common_hypernyms(wn.synset("justice.n.01"))]) for o in wn.synsets("oak", "n")]
print("oak senses vs justice.n.01:", senses)
tree = next(o for o in wn.synsets("oak", "n") if "plant" in " ".join(h.name() for h in o.closure(lambda s: s.hypernyms())))
g2, lcas2, sa2, sb2, ca2, cb2 = info(tree.name(), "justice.n.01")
print(f"oak (tree sense {tree.name()}) / justice LCA(s):", [x.name() for x in lcas2], " (page: entity); gcd == code(LCA):", [g2 == code_of(x) for x in lcas2])
L.check("oak (the tree sense) / justice: LCA is entity", any(x.name().startswith("entity") for x in lcas2), "the first listed sense oak.n.01 gives abstraction.n.06 as LCA (it is not the tree sense in this WordNet)")
L.check("…and gcd = code(entity)", any(g2 == code_of(x) for x in lcas2))
L.check("ca / gcd = the descent from the LCA (an exact division, no tree walk)", ca % g == 0 and cb % g == 0 and ca // g > 1)
L.prose("'How much context do you need = enough to reach the common ancestor of prompt and response; not less, not more (at the limit e₀ carries nothing)' — a design statement; the gcd = LCA identity it rests on is verified above")"""),

("md", """## 6 · Only definitional identity gets prime hashed — WordNet's inclusion criterion"""),
("code", """names = set(wn.all_lemma_names())
closed = ["of", "the", "and", "to", "because", "a", "in", "is", "for", "with"]
inwn = [w for w in closed if w in names]
print("closed-class words present in WordNet's lemma list:", inwn)
L.check("WordNet excludes of / the / and / to / because (page)", not any(w in names for w in ("of", "the", "and", "to", "because")))
print("pointer relations present as edges: ", sorted({p for s in list(wn.all_synsets())[:2000] for p in ("part_meronyms","hypernyms","member_meronyms","substance_meronyms") if getattr(s, p)()}))
L.check("the relation `mero_part` exists as an edge type while the word 'of' does not", len(wn.synset("hand.n.01").part_meronyms()) > 0 and "of" not in names)"""),

("md", """## 7 · `monad_identity.bin` — layouts, round trip, discardability
Build artefact: `ContextPlease/claude/scratchpad/2026-08-18_three_faces_and_identity_bin/monad_identity.bin` (594,393 bytes). Layout sizes verified against gcc `sizeof`; read with `monad_identity.Reader`."""),
("code", """import ctypes as C
for st, want in ((MI.mi_header_t, 384), (MI.mi_entry_t, 96), (MI.mi_chan_t, 8), (MI.mi_edge_t, 12)):
    L.check(f"python ctypes sizeof({st.__name__}) = {want}", C.sizeof(st) == want)
d = scratch("miC_")
csrc = '''#include <stdio.h>
#include <stddef.h>
#include "monad_identity.h"
int main(void){ printf("%zu %zu %zu %zu\\\\n", sizeof(mi_header_t), sizeof(mi_entry_t), sizeof(mi_chan_t), sizeof(mi_edge_t)); return 0; }'''
open(os.path.join(d, "t.c"), "w").write(csrc)
cc = subprocess.run(["gcc", "-I", os.path.join(VAPMIP, "PtolC"), "-o", os.path.join(d, "t"), os.path.join(d, "t.c")], capture_output=True, text=True)
if cc.returncode == 0:
    sz = subprocess.run([os.path.join(d, "t")], capture_output=True, text=True).stdout.split(); print("gcc sizeof:", sz)
    L.check("gcc sizeof(header, entry, chan, edge) = 384, 96, 8, 12 — same as the Python mirror", sz == ["384", "96", "8", "12"])
else:
    L.check("monad_identity.h compiles for a sizeof probe", False, cc.stderr[-200:])
binp = os.path.join(PLACE, "ContextPlease", "claude", "scratchpad", "2026-08-18_three_faces_and_identity_bin", "monad_identity.bin")
rd = MI.Reader(binp); v = rd.verify(); print(v)
L.check("file size 594,393 bytes (≈594 KB)", os.path.getsize(binp) == 594393)
L.check("checksum_ok", v['checksum_ok'])
L.check("3,081 entries, 24,993 channels, 3,080 edges", (v['entries'], len(rd.chans), len(rd.edges)) == (3081, 24993, 3080), f"{v['entries']}, {len(rd.chans)}, {len(rd.edges)}")
ns, nt = map(int, v['spell_roundtrip'].split('/'))
L.check("spell round-trip is exact for every non-overflowing entry (2591/2591)", ns == nt and v['spell_roundtrip'] == "2591/2591", v['spell_roundtrip'])
L.check("490 entries flagged overflow (>13 letters) — flagged, not truncated", v['spell_overflow'].startswith("490"), v['spell_overflow'])
a_, b_ = map(int, v['address_recomputed'].split('/'))
L.check("the discardability test: address recomputed from positions alone for 3081/3081", a_ == b_ == 3081, v['address_recomputed'])
L.check("193 bytes per entry on average (594,393 / 3,081)", abs(594393/3081 - 193) < 1, f"{594393/3081:.1f}")
parents = {int(e.parent) for e in rd.entries}; print("distinct parent ids:", len(parents))
L.check("MI_LETTER_CAP in monad_identity.py is 71 (the page's corrected cap), not 313", MI.MI_LETTER_CAP == 71, f"MI_LETTER_CAP = {MI.MI_LETTER_CAP}")"""),

("md", """## 8 · IEEE contains no irrational numbers"""),
("code", """from fractions import Fraction
fr = Fraction(math.sqrt(2)); print(fr, " denominator is 2^52:", fr.denominator == 2**52)
L.check("math.sqrt(2) = 6369051672525773 / 4503599627370496 (denominator 2⁵²)", fr == Fraction(6369051672525773, 4503599627370496))
L.check("(√2)² in double precision = 2.0000000000000004", math.sqrt(2)**2 == 2.0000000000000004)
L.check("√2¹² in floats = 64.00000000000006, not 64", abs(math.sqrt(2)**12 - 64.00000000000006) < 1e-12 and math.sqrt(2)**12 != 64.0, f"{math.sqrt(2)**12!r}")
class Q2:                      # a + b√2, exact integer arithmetic (a quadratic surd)
    def __init__(s, a, b=0): s.a, s.b = Fraction(a), Fraction(b)
    def __mul__(s, o): return Q2(s.a*o.a + 2*s.b*o.b, s.a*o.b + s.b*o.a)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __repr__(s): return f"{s.a}+{s.b}√2"
r2 = Q2(0, 1); p = Q2(1)
for _ in range(12): p = p * r2
L.check("exact ℚ(√2): (√2)² = 2 and (√2)¹² = 64, both exactly", r2*r2 == Q2(2) and p == Q2(64), f"(√2)¹² = {p}")
L.check("one irrational, two integers per value, closed arithmetic (the product of two surds is a surd)", isinstance(r2*Q2(3, 5), Q2))
# a float orbit on the torus closes: 1:√2 is rational in floats
r = Fraction(1)/Fraction(math.sqrt(2)); print("1/√2 as a float is the rational", r.numerator, "/", r.denominator)
L.check("the float frequency ratio 1:√2 is RATIONAL, so a computed orbit is periodic (period ≤ 2⁵²)", r.denominator <= 2**53)
L.prose("The hashing algorithm is float-free; all float exposure is in the geometry layer (a code-reading statement; consistent with the integer Horner/Knuth arithmetic of Phase 23)")"""),

("md", """## 9 · Structure is executable — four benchmarked speedups
Setup: `L_a`, the 16×16 left-multiplication matrix of a unit pure-imaginary sedenion a (non-ZD ⇒ L_a skew, orthogonal, `L_a² = −I`) and of a zero-divisor a = (e₁+e₁₀)/√2. Speed-ups are machine-dependent; what is checked is *correctness of the shortcut* and the order of the gain."""),
("code", """from _sedenion import cd_mul, e
from scipy.linalg import expm
import timeit
Lmat = lambda a: np.array([cd_mul(list(a), list(e(j, 16))) for j in range(16)]).T
a = np.zeros(16); a[3] = 1.0; La = Lmat(a)
L.check("non-ZD unit imaginary a: L_a is skew-symmetric and orthogonal, L_a² = −I", np.allclose(La, -La.T) and np.allclose(La @ La.T, np.eye(16)) and np.allclose(La @ La, -np.eye(16)))
t = 0.7
closed = np.cos(t)*np.eye(16) + np.sin(t)*La
L.check("exp(tL) = cos t·I + sin t·L  (closed form, exact in t)", np.allclose(expm(t*La), closed, atol=1e-12))
t_closed = min(timeit.repeat(lambda: np.cos(t)*np.eye(16) + np.sin(t)*La, number=2000, repeat=5))/2000
def expm_taylor(A, terms=18):
    nrm = np.linalg.norm(A, 1); sq = max(0, int(np.ceil(np.log2(max(nrm, 1e-16)))) + 1); B = A/2**sq
    R = np.eye(len(A)); T = np.eye(len(A))
    for k in range(1, terms): T = T @ B/k; R = R + T
    for _ in range(sq): R = R @ R
    return R
L.check("Taylor+squaring reference agrees with scipy expm (so the comparison is of like with like)", np.allclose(expm_taylor(t*La), expm(t*La), atol=1e-10))
t_expm = min(timeit.repeat(lambda: expm_taylor(t*La), number=300, repeat=5))/300
t_scipy = min(timeit.repeat(lambda: expm(t*La), number=300, repeat=5))/300
t_inv = min(timeit.repeat(lambda: np.linalg.inv(La), number=2000, repeat=5))/2000; t_T = min(timeit.repeat(lambda: La.T, number=20000, repeat=5))/20000
print(f"1. exp(tL): closed form {t_closed*1e6:.1f} µs vs Taylor+squaring {t_expm*1e6:.1f} µs → {t_expm/t_closed:.1f}×   (page 15.5×);  vs scipy Padé expm {t_scipy*1e6:.1f} µs → {t_scipy/t_closed:.1f}×")
print(f"2. inverse: transpose {t_T*1e6:.2f} µs vs np.linalg.inv {t_inv*1e6:.1f} µs → {t_inv/t_T:.0f}×   (page 77×)")
L.check("closed form is ≈ 15× faster than Taylor+squaring (page: 15.5×)", t_expm/t_closed > 8, f"{t_expm/t_closed:.1f}× vs Taylor+squaring, {t_scipy/t_closed:.1f}× vs scipy Padé (machine-dependent)")
L.check("orthogonal inverse = transpose, exact, and ≥ 20× faster than a general inverse (page 77×)", np.allclose(La.T @ La, np.eye(16)) and t_inv/t_T > 20, f"{t_inv/t_T:.0f}×")
z = np.zeros(16); z[1] = z[10] = 1/math.sqrt(2); Lz = Lmat(z)
nullity = 16 - np.linalg.matrix_rank(Lz)
L.check("3. kernel never moves: the ZD's L has a 4-dimensional null space ⇒ skip 4 of 16 dims = 25 % fewer ops", nullity == 4 and 4/16 == 0.25, f"nullity {nullity}")
fill = np.count_nonzero(np.abs(Lz) > 1e-12)/256
L.check("4. storage: skew-symmetric upper triangle = 120 doubles instead of 256", 16*15//2 == 120 and np.allclose(La, -La.T))
L.check("…and sparse: the ZD's L fills ≈ 12 % of its 256 entries (page: 12 %)", abs(fill - 0.125) < 0.02, f"fill {fill*100:.1f} % ({np.count_nonzero(np.abs(Lz) > 1e-12)} of 256)")
L.check("the ZD's L is also skew-symmetric (so the 120-double storage applies to it)", np.allclose(Lz, -Lz.T) if True else False, "L_z for a = (e₁+e₁₀)/√2 has zero real part ⇒ skew")"""),
("md", """## 10 · Retractions and what remains open (as the page records them)"""),
("code", """for c in ["Retractions 'one of them mine three times over' — the page's own list (§10); the specific items are statements about the author's session, not machinery",
          "Budget: with the cap at 71, the 42 assessors take 94 digits (< 100); at 313 they took 112 — the digit accounting depends on the encoding of an assessor layer not present in the repo as a function",
          "STILL OPEN (§11): see the page; nothing is reproduced for items the page lists as open"]:
    L.prose(c)"""),
]
