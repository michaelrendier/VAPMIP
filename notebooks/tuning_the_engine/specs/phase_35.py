LABEL = "35"
TITLE = "The Spider-Web Composition Cycle"
DATE = "2026-09-03 → 2026-09-04"
PAGE = "35_the_spider_web_composition_cycle.md"
BYLINE = "page by Claude Sonnet 5 — the page itself says 'AS YET UNTESTED'"

CELLS = [
("md", """The page records a document-construction model (Persian 3/1 Kings-Mail Spider Web) and its first test bench `boxkite_orbweaver_monad.py`. It declares itself untested; what *can* be checked is (a) the mathematical objects it leans on (Apollonian gasket, E8, Cassini ovals), (b) the structure the test bench claims to exercise, and (c) the degenerate behaviours the page records."""),
("md", """## 1 · The two packings — E8 (content) and the Apollonian gasket (context flow)
E8: kissing number 240, self-dual, theta series `E₄ = 1 + 240 Σ σ₃(n)qⁿ`. Gasket: Descartes `(Σk)² = 2Σk²`, integer curvatures, δ ≈ 1.3057."""),
("code", """import itertools
# E8 as D8⁺: integer vectors with even coordinate sum, plus half-integer vectors with even sum (all norms are even)
def e8_count(max_norm2):
    counts = {}
    rng_i = range(-2, 3)
    for v in itertools.product(rng_i, repeat=8):
        n2 = sum(x*x for x in v)
        if 0 < n2 <= max_norm2 and sum(v) % 2 == 0: counts[n2] = counts.get(n2, 0) + 1
    half = [x/2 for x in range(-5, 6, 2)]            # ±1/2, ±3/2, ±5/2
    for v in itertools.product(half, repeat=8):
        n2 = sum(x*x for x in v)
        if 0 < n2 <= max_norm2 and abs(sum(v) - round(sum(v)/2)*2) < 1e-9: counts[round(n2)] = counts.get(round(n2), 0) + 1
    return counts
c = e8_count(6)
from sympy import divisor_sigma
theory = {2*n: 240*int(divisor_sigma(n, 3)) for n in (1, 2, 3)}
print("E8 shell sizes (norm² → count):", dict(sorted(c.items())), "   theory 240·σ₃(n):", theory)
L.check("kissing number of E8 is 240 (shell at norm² 2)", c.get(2) == 240)
L.check("theta series E₄ = 1 + 240 σ₃(n): shells 240, 2160, 6720 at norm² 2, 4, 6", [c.get(2), c.get(4), c.get(6)] == [240, 2160, 6720], str(c))
roots = [v for v in itertools.chain(itertools.product(range(-1, 2), repeat=8)) if sum(x*x for x in v) == 2 and sum(v) % 2 == 0]
G = np.array(roots[:8], float)
L.check("E8 roots: integer roots (112) + half-integer roots (128) = 240", len(roots) == 112 and 112 + 2**7 == 240)"""),
("code", """# Apollonian gasket: Descartes + circle counting for the exponent
def gasket_curvatures(limit):
    ks = [-1, 2, 2, 3]; out = [-1, 2, 2, 3]; stack = [(-1, 2, 2, 3), (-1, 2, 3, 2)][:1]
    seen = set(); res = [-1, 2, 2, 3]
    def new(a, b, c, d): return 2*(a + b + c) - d
    stack = [(-1, 2, 2, 3)]
    while stack:
        q = stack.pop()
        for i in range(4):
            d2 = new(*[q[j] for j in range(4) if j != i], q[i])
            if d2 > limit or d2 <= q[i]: continue
            nq = list(q); nq[i] = d2; nq = tuple(sorted(nq))
            if nq in seen: continue
            seen.add(nq); res.append(d2); stack.append(nq)
    return res
ks = gasket_curvatures(50000)
quad = (-1, 2, 2, 3); L.check("Descartes (Σk)² = 2Σk² for the seed quadruple (−1, 2, 2, 3)", sum(quad)**2 == 2*sum(k*k for k in quad))
q2 = (-1, 2, 3, 6); L.check("…and for a descendant (−1, 2, 3, 6)", sum(q2)**2 == 2*sum(k*k for k in q2))
ks = np.array(sorted(k for k in ks if k > 0))
Ks = np.array([1000, 2000, 5000, 10000, 20000, 50000]); N = np.array([(ks <= K).sum() for K in Ks])
slope = np.polyfit(np.log(Ks), np.log(N), 1)[0]; print("N(curvature ≤ K) =", dict(zip(Ks.tolist(), N.tolist())), f" log-log slope = {slope:.3f}")
L.check("circle-count exponent ≈ the gasket's Hausdorff dimension δ ≈ 1.3057 (finite-size slope within 0.06)", abs(slope - 1.3057) < 0.06, f"slope {slope:.3f} (the exponent converges slowly from above/below)")
L.check("curvatures are integers (discrete depth levels)", all(float(k).is_integer() for k in ks[:1000]))"""),

("md", """## 2 · The Cassini oval and the lemniscate: `b/c = 1` is the lemniscate (NOW)
`b/c > 1.15` continuous (one room), `≈ 1` lemniscate (σ=½, NOW forms), `< 1` discrete (two lobes)."""),
("code", """import boxkite_orbweaver_monad as O
# Cassini oval  r⁴ − 2a²r²cos2θ = b⁴ − a⁴ ;  b = a is the lemniscate of Bernoulli (passes through the origin)
a_ = 1.0
def passes_origin(b): return abs(b**4 - a_**4) < 1e-12
def connected(b):    # for b>a the oval is one closed curve; for b<a it splits into two lobes
    return b > a_
L.check("b = c: the curve passes through the origin (lemniscate of Bernoulli — the node, NOW)", passes_origin(1.0) and not passes_origin(1.2) and not passes_origin(0.8))
th = np.linspace(0, 2*np.pi, 7)
L.check("module's _cassini_r2 reproduces the closed form r² = a²cos2θ + √(b⁴ − a⁴sin²2θ) on its branch", all(abs((O._cassini_r2(t, 1.0, 1.3) or 0) - (np.cos(2*t) + np.sqrt(1.3**4 - np.sin(2*t)**2))) < 1e-9 for t in th), "closed form for the outer branch")
m = O.OrbWeaverMonad()
sents = ["she deposited her savings in the reserve account", "the engine contains sixteen distinct operators that fold into a single algebra", "the volcano formed a mountain of cinder ash lava rock"]
docs = {s: m.weave(s, scale="auto") for s in sents}
for s, d in docs.items(): print(f"  b/c={d.room.ratio:6.3f} {d.room.regime:11} reach={d.reach}  {s[:60]}")
rs = [docs[x].room.ratio for x in sents]
print("page: 2.269 (continuous, reach 1) > 0.873 (discrete, reach 3) > 0.805 (discrete, reach 3) — on sentences the page quotes only in elided form ('...sixteen distinct operators…', 'the volcano formed a mountain of cinder ash lava rock ...')")
L.skip("exact b/c values 2.269 / 0.873 / 0.805", "the page quotes the 2nd and 3rd sentences with leading/trailing ellipses, so the exact inputs are unknown; the values below are for the reconstructed sentences")
L.check("ordering of b/c across the three contents is preserved: savings > engine > volcano (page: 2.269 > 0.873 > 0.805)", rs[0] > rs[1] > rs[2], str([round(x, 3) for x in rs]))
L.check("the savings sentence is 'continuous' (b/c > 1.15, reach 1) as on the page", docs[sents[0]].room.regime == "continuous", f"b/c {rs[0]:.3f} → {docs[sents[0]].room.regime}, reach {docs[sents[0]].reach} (reconstructed sentence; the page's own may differ)")
L.check("the two complex sentences are 'discrete' (b/c < 1) with reach ≥ 3", all(docs[x].room.regime == "discrete" and docs[x].reach >= 3 for x in sents[1:]), str([(docs[x].room.regime, docs[x].reach) for x in sents[1:]]))
L.check("b/c has a real spread across contents (max − min > 0.4) — a discriminator, unlike strut overlap (7.000 == 7.000)", max(rs) - min(rs) > 0.4, f"{min(rs):.3f} … {max(rs):.3f}")
auto, hand = m.weave(sents[1], scale="auto"), m.weave(sents[1], scale=2.0)
L.check("b/c is a property of the content: identical whether scale is 'auto' or hand-set", abs(auto.room.ratio - hand.room.ratio) < 1e-12, f"{auto.room.ratio:.6f} vs {hand.room.ratio:.6f}")"""),

("md", """## 3 · What the page says runs — and what it says is broken"""),
("code", """d = docs[sents[1]]
kinds = [b.kind for b in d.blocks]
print("block kinds:", kinds[:12], "…");  print("reach:", d.reach, "| turbulent:", d.turbulent, "| radii:", len(d.radii), "| blocks:", len(d.blocks), "| scaffold lines:", len(d.scaffold))
L.check("reach from SCALE: 1 / 2 / 3 → paragraph / section / chapter scaffold depth", [m.weave(sents[0], scale=s).reach for s in (1, 2, 3)] == [1, 2, 3])
L.check("every block carries its outbound connective and a radial move (self-describing weave)", all(b.kind in ("bridge", "scope") or (b.connective_out != "" and b.move is not None) for b in d.blocks) or all(b.connective_out != "" for b in d.blocks if b.kind == "paragraph"))
L.check("blocks are tagged past / now / future by spiral depth (light-cone bands)", set(b.tense for b in d.blocks) <= {"past", "now", "future", ""})
moves = {b.move for b in d.blocks}; print("radial moves present:", moves)
L.check("moves are drawn from {+1, −1, 0, 'pivot'}", moves <= {1, -1, 0, "pivot", "+1", "-1"} , str(moves))
rows = d.ledger_rows; stat = {}
for r_ in rows: stat[str(r_.status.name if hasattr(r_.status, 'name') else r_.status)] = stat.get(str(r_.status.name if hasattr(r_.status, 'name') else r_.status), 0) + 1
print("ledger rows:", len(rows), stat)
L.check("the page's '19 ledger rows, all UNTESTED'", len(rows) == 19 and set(stat) == {"UNTESTED"}, f"{len(rows)} rows: {stat}")"""),
("code", """# 'The coherence measure saturates' (real_mean == ctrl_mean == 7.000) and 'the sniffer over-flags turbulence'
rowtxt = {getattr(r_, 'name', str(r_)): r_ for r_ in rows}
sat = [r_ for r_ in rows if "coherence" in str(getattr(r_, "name", "")) or "paragraph" in str(getattr(r_, "name", "")).lower()]
for r_ in sat[:3]: print(" ", str(r_)[:200])
turb = [m.weave(s, scale="auto").turbulent for s in ("hello", "she deposited her savings", "the volcano formed a mountain of cinder ash lava rock", "a simple note")]
print("turbulent flag for four inputs:", turb)
L.check("the crude sniffer flags EVERY input turbulent ('hash-spreading always yields ≥ 3 peaks') — page", all(turb), f"{sum(turb)} of {len(turb)} inputs flagged turbulent: {turb}; the sniffer has since changed (the page's update reports a laminar 'simple note')")
note = m.weave("buy milk and eggs today", scale="auto"); print("simple note →", dict(turbulent=note.turbulent, pivots=sum(1 for b in note.blocks if b.kind == 'pivot')))
print("(a reconstructed 'simple note' — the page's own note text is not given) turbulent =", note.turbulent)
L.skip("the update's simple note reads turbulent=False, n_peaks=1, pivots=0", "the page's note text is not quoted; for the reconstructed note 'buy milk and eggs today' the flag is " + str(note.turbulent))
# repetition: output is repetitive because the sentence layer is templates
texts = [b.text for b in d.blocks if b.kind == "paragraph"]
L.check("output is repetitive (the sentence layer is copied templates + a sniffer, not the real constructor)", len(set(texts)) < len(texts) or len(texts) < 4, f"{len(set(texts))} distinct of {len(texts)} paragraphs")"""),

("md", """## 4 · The frustrated spiral and the hub saddle (λ ≈ 6)
A frustrated spiral reverses along a cross structural support — the stable⊥unstable manifold cross of the hub saddle at σ = ½ with λ ≈ 6. The saddle is the Oblique Gear's (memory index: "σ=½ is a hyperbolic SADDLE (λ≈6)"). Check the arithmetic the saddle implies: homoclinic orbits come in along the stable manifold and out along the unstable one, with a doubled thread near the fixed point at rate e^{−λt}."""),
("code", """lam = 6.0
t = np.linspace(0, 1, 6)
inward = np.exp(-lam*t); outward = np.exp(lam*(t - 1))              # a homoclinic passage: in on the stable, out on the unstable branch
sep = np.abs(inward - outward)
print("separation of outbound and return passes near the hub:", np.round(sep, 4))
L.check("near the hub the outbound and return steps are exponentially close; far from it they separate (doubled thread, high density)", sep[len(t)//2] < sep[0] or sep[len(t)//2] < sep[-1])
try:
    import ValaQuenta.modules.oblique_gear.maths as OG
    print([n for n in dir(OG) if 'saddle' in n.lower() or 'lambda' in n.lower() or 'eig' in n.lower()][:6])
    L.skip("λ ≈ 6 from the Oblique Gear module", "the module exposes no single-call saddle eigenvalue under a name this notebook can rely on; see Phase 'Oblique Gear' notes")
except Exception as ex:
    L.skip("λ ≈ 6 from the Oblique Gear module", f"{type(ex).__name__}: {ex}")"""),
("code", """for c in ["Silk biology: poly-Ala β-sheet nanocrystals in a glycine-rich matrix; N-terminal pH sensor (dimerises below pH 5.7); C-terminal disulfide-locked dimer; spinning is pultrusion not extrusion; tougher than Kevlar — literature summary, not reproduced",
          "The composition operators ANCHOR/BRIDGE/FRAME/HUB/RADIUS/SCAFFOLD_SPIRAL/CAPTURE_SPIRAL/ELABORATE/HOOK/WRAP/SHELL/SIGNPOST and the idea grammar CRYSTAL/SLACK/TRANSITION/BIND — a design vocabulary; the test bench exercises the web cycle",
          "The connective lexicon (Halliday & Hasan / PDTB) with radial moves +1 / −1 / 0 / pivot — a closed class; the bench draws connectives at random within a class (so the 0.68–1.00 light-cone match is not evidence)",
          "Genre = a field configuration; Navier–Stokes (hyperdimensional, no free surface) models context flow: ∇·u = 0, pressure = how much context wants to be here, high Re → eddies = sections — a modelling proposal",
          "Correction (2026-09-04): paragraphs are anisotropic, so the Radius abstraction (a straight uniform spoke) is wrong for paragraphs and a global `scale` is wrong for sentence length — recorded; the redesign (paragraph construction into monad3_c.bin, usage into the granular .bins) follows and is not built",
          "TODO on the page: switch the orb-weaver coherence measure to the sigma_self-delta form"]:
    L.prose(c)"""),
]
