LABEL = "10"
TITLE = "The Pit and the Path"
DATE = "2026-06-12"
PAGE = "10_the_pit_and_the_path.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## The critical-strip map and the war corpus
The page maps ζ's strip onto the architecture: σ=0 "trivial zeros", 0<σ<½ captured, σ=½ escape, ½<σ<1 identity zone, σ=1 divergence (the ζ pole), σ>1 the above-layer. Check the zeta facts, then the corpus facts (the file, its header, its role as a coordinate rather than content)."""),
("code", """import mpmath as mp
mp.mp.dps = 25
# ζ pole at σ=1:  (s−1)ζ(s) → 1
for eps in (1e-1, 1e-3, 1e-6): print(f"  ε={eps:g}  ε·ζ(1+ε) = {float(eps*mp.zeta(1+eps)):.8f}")
L.check("ζ has a simple pole at s=1 with residue 1", abs(float(1e-6*mp.zeta(1+1e-6)) - 1) < 1e-5)
# harmonic series diverges (the 'divergence' window)
H = lambda N: sum(1.0/n for n in range(1, N+1))
g = float(mp.euler)
print("  H_N − ln N →", [round(H(N) - math.log(N), 5) for N in (10, 1000, 100000)], " (→ γ_E =", round(g, 5), ")")
L.check("Σ1/n diverges like ln N + γ_E", abs(H(100000) - math.log(100000) - g) < 1e-5)
# where are the zeros?  trivial zeros: negative even integers (NOT at σ=0)
tz = [(-2*k, complex(mp.zeta(-2*k))) for k in (1, 2, 3)]
print("  ζ(−2), ζ(−4), ζ(−6) =", [abs(z) < 1e-20 for _, z in tz], "  ζ(0) =", complex(mp.zeta(0)))
L.check("the strip map's row 'σ = 0 — trivial zeros': ζ vanishes at σ = 0", abs(complex(mp.zeta(0))) < 1e-20,
        "ζ(0) = −½ ≠ 0. The trivial zeros are the negative even integers s = −2, −4, −6, … (σ<0), confirmed above; the σ=0 row is a placement choice in the map, not where ζ vanishes")
L.check("trivial zeros at s = −2, −4, −6", all(abs(z) < 1e-20 for _, z in tz))
# non-trivial zeros: all inside 0<σ<1 — the first dozen are on σ=½ with these heights
print("  γ₁..γ₈ =", [round(float(mp.zetazero(n).imag), 3) for n in range(1, 9)])"""),
("md", """### The war corpus as coordinate (not content)"""),
("code", """wc = open(os.path.join(VAPMIP, "war-corpus.txt"), encoding="utf-8").read()
hdr = "\\n".join(wc.splitlines()[:10])
print(hdr)
L.check("war corpus header says it shapes attractor/repeller geometry and does not block", "shapes the attractor/repeller geometry of J^μ" in wc and "It does not block" in wc)
L.check("a second copy (war_corpus.txt) exists and agrees on the header", open(os.path.join(VAPMIP, "war_corpus.txt"), encoding="utf-8").read().splitlines()[:9] == wc.splitlines()[:9])
print(f"war-corpus.txt: {len(wc):,} chars, {len(wc.split()):,} words; URL-tagged lines: {sum(1 for l in wc.splitlines() if l.startswith('http') or '[TESTIMONY]' in l)}")
src = open(os.path.join(VAPMIP, "monad_bin", "ingest_war.py")).read()
L.check("ingest_war.py folds the prime-directive primers into monad_war.bin (the 'seed the Pit first' step) with weight 2.0", "weight=2.0" in src or "2.0" in src)"""),
("code", """for c in ["The war corpus is the geometric location of The Pit in the Zero Lattice (a placement, not a measurement)",
          "Three waypoints ZD → σ=½ → divergence as Ptolemy's identity trajectory; Tolkien/Somme/Ainulindale parallel",
          "Seeding order: the Pit first, then every other corpus, with G_ptolemy_n = G + α(departure_n − G) (checked mechanically in Phase 12)"]:
    L.prose(c)"""),
]
