"""
TEST — "show me where each facet of 0_RB has its constant, in relation to the
others, ACCORDING TO SCALE" (Cody, 2026-08-28)

The chart is ONE object: the Smith / Joukowsky fold
      Γ(c ; Z0) = (c − Z0) / (c + Z0)  =  tanh( ½ · ln(c/Z0) )
i.e. the compression of the infinite log-scale line ln(c/Z0) ∈ (−∞,∞) into the
disk Γ ∈ (−1,1), Γ=0 at c=Z0. Same move as Penrose's arctan compactification.

"2-ring / 3-ring / 4-ring" are three READINGS of that one fold, at three
physically-meaningful anchors:

  2-ring  space | time          Z0 = √(α_F · Ω_ζΣ)   (geom-mean of the BK
                                                      operator domain endpoints
                                                      → α_F and Ω_ζΣ land
                                                      symmetric, ±Γ)
  3-ring  past | now | future   Z0 = d*               (the σ=½ "Boundary" — the
                                                      framework's literal "now")
  4-ring  N | S | E | W         Z0 = d* (complex)     (log-polar / native
                                                      spherical-complex-radial-
                                                      polar space; magnitude on
                                                      the N–S meridian, phase on
                                                      E–W, so i / √2·i / Λ pull
                                                      off the real axis)

Uses SedenionFactoralRelativity.engine.ring_chart_gamma / cross_ratio /
chart_scale_factor  (the fold + its invariants, already built 2026-08-23).
"""
import sys, math, cmath
sys.path.insert(0, "/home/rendier/Projects/ThePlace")
from SedenionFactoralRelativity.engine import (
    ring_chart_gamma, cross_ratio, chart_scale_factor,
)

# ────────────────────────────────────────────────────────────────────────────
# constants — the Tier-0 facets of 0_RB  (ValaQuenta/wiki/constants.md:
#   "π φ e √ i Ω_ζΣ α_F d* Λ — all drop out of Ĥ_RB algebraic structure")
# ────────────────────────────────────────────────────────────────────────────
LN10 = math.log(10.0)

def lambert_W(x, n=80):
    """W(x): Newton on w·e^w = x. W(1) = Ω_ZS."""
    w = 0.5 if x < 3 else math.log(x)
    for _ in range(n):
        ew = math.exp(w)
        f = w * ew - x
        w -= f / (ew * (w + 1) - (w + 2) * f / (2 * w + 2))
    return w

OMEGA = lambert_W(1.0)                    # Ω_ζΣ  = W(1)  = Ω_RiemannZeta
# ── the FOUR FACES of d* (one point, four measuring geometries) ────────────
# Cody, 2026-08-28: 0_RB emits d*_TAUT as the geometry — the tautological /
# "Flow" face, zero gap BY CONSTRUCTION. It is NOT the measured Boundary face.
# The earlier run used this value and called it "d*" — mislabelled, not wrong
# about what 0_RB produces. Proposal: the 4 quads of the orthogonal Smith chart
# = these 4 faces, each appearing residually on its quadrant.
D_STAR_TAUT     = OMEGA / LN10           # "The Flow"       = Ω_ζΣ/ln10   (what 0_RB spits out)
D_STAR_BOUNDARY = 0.24600               # "The Boundary"   σ=½ spectral (MEASURED = d*_spec)
D_STAR_TRANS    = OMEGA                  # "The Translator" = d*·ln10 = Ω_ζΣ (the metric bridge)
D_STAR_RG       = None                   # "The Stability"  CD-tower RG fixed point — OPEN
D_STAR = D_STAR_TAUT                     # keep the old name pointing at the face the geometry gives
D_STAR_SPEC = D_STAR_BOUNDARY
ALPHA_F = 1.0 / 137.035999084            # α_Fermat — the CALIBRATOR (live ECU trim); also BK floor
GAP = OMEGA - D_STAR_SPEC * LN10          # the mass gap Δ = the ERROR CHECK (OBD-II fault code)
                                         # = ln10·(d*_taut − d*_boundary) — the residual between two faces
PHI = (1.0 + 5.0 ** 0.5) / 2.0
LN_PHI = math.log(PHI)

# PROVENANCE (Cody, 2026-08-28): d* and Ω_ζΣ = W(1) are ENGINEERED anchor points
# — conditions imposed to place them as the two ends of an ERROR-CHECK experiment
# (the Riemann-vs-Fermat-across-a-horizon construction). "Lambert-W fixed point /
# de Sitter attractor / BK domain endpoint" are POST-HOC descriptive names, not
# the provenance. α_Fermat = "the CALIBRATOR" (reference standard). The mass gap
# Δ = the ERROR CHECK itself (readout of engineered d*_taut vs measured d*_spec).
# This applies to d*/W(1) ONLY — π, e, φ, √2, i are genuinely the known constants.
CONST = {
    # name          value                    role
    "α_Fermat":   (ALPHA_F,   "the CALIBRATOR — reference standard (also: BK floor, v₁=α·c<c)"),
    "mass gap Δ": (GAP,       "the ERROR CHECK — readout: engineered d*_taut vs measured d*_spec"),
    "d*":         (D_STAR,    "ENGINEERED anchor (entropy end); σ=½ 'Boundary' = NOW; d*·ln10=Ω_ζΣ"),
    "ln φ":       (LN_PHI,    "golden log — Fibonacci growth rate / arcsinh(½)"),
    "Ω_RiemannZ": (OMEGA,     "ENGINEERED anchor (inertia end); W(1). 'de Sitter / Lambert' = post-hoc names"),
    "Lambert W1": (OMEGA,     "W(1): same engineered point as Ω_ζΣ, marks the w·e^w=1 fixed pt"),
    "e":          (math.e,    "natural base — the log identity (known constant)"),
    "π":          (math.pi,   "circle — the rotation identity, ½ turn = π (known constant)"),
    "i":          (1.0,       "imag unit — 90° rotation; |i|=1, phase π/2 (OFF the real axis)"),
}
IMAG = {"i"}  # placed at phase π/2, not on the real diameter

EXTRA = {"φ": PHI, "√2": math.sqrt(2), "1 (identity)": 1.0, "d*_spec": D_STAR_SPEC,
         "10 (decade)": 10.0}

GEOM_MEAN = math.sqrt(ALPHA_F * OMEGA)    # 2-ring anchor

print("═" * 78)
print("CONSTANTS  (facets of 0_RB)")
print("═" * 78)
for name, (val, role) in CONST.items():
    print(f"  {name:12s} = {val:>18.12f}   {role}")
print(f"\n  Ω_ζΣ·… checks:  d*·ln10 = {D_STAR*LN10:.12f}  (= Ω_ζΣ = {OMEGA:.12f})  ✓")
print(f"                 Ω_ζΣ − d*_spec·ln10 = {GAP:.3e}   1/(1000√2) = {1/(1000*math.sqrt(2)):.3e}")
print(f"  BK domain [α_F, Ω_ζΣ] width = {OMEGA-ALPHA_F:.6f} ;  geom-mean √(α_F·Ω_ζΣ) = {GEOM_MEAN:.6f}")


def fold(c, Z0):
    G = ring_chart_gamma(complex(c), complex(Z0))
    u = math.log(abs(c) / abs(Z0)) if c and Z0 else float("nan")
    return G, abs(G), u


def table(title, Z0, names):
    print("\n" + "─" * 78)
    print(f"{title}   ·   anchor Z0 = {Z0!r}   (Γ=0 here)")
    print("─" * 78)
    print(f"  {'constant':12s} {'value':>14s}  {'Γ (real fold)':>14s} {'|Γ|':>8s} "
          f"{'u=ln(c/Z0)':>11s}  side")
    rows = []
    for nm in names:
        c = CONST[nm][0] if nm in CONST else EXTRA[nm]
        G, aG, u = fold(c, Z0)
        side = "· NOW ·" if aG < 0.2449 else ("PAST  (→i⁻)" if G.real < 0 else "FUTURE (→i⁺)")
        if nm in IMAG:
            side = "N–S axis (phase π/2)"
        print(f"  {nm:12s} {c:>14.8f}  {G.real:>14.6f} {aG:>8.4f} {u:>11.5f}  {side}")
        rows.append((nm, c, G.real, aG, u))
    return rows


# ── FRAMING 1 — the master fold at four anchors ────────────────────────────
print("\n\n" + "█" * 78)
print("█  FRAMING 1 — the one fold, four anchors")
print("█" * 78)
NAMES = [n for n in CONST if n not in IMAG] + ["φ", "√2", "1 (identity)", "10 (decade)"]
for label, Z0 in [("bare identity", 1.0), ("d*  (σ=½, the NOW)", D_STAR),
                  ("√(α_F·Ω_ζΣ)  (BK log-centre)", GEOM_MEAN), ("e  (log identity)", math.e)]:
    table(f"anchor: {label}", Z0, NAMES)


# ── FRAMING 2 — TWO-RING  space | time   (GR / QM / UFT) ───────────────────
print("\n\n" + "█" * 78)
print("█  FRAMING 2 — TWO-RING   space (Scale) | time (Resolution)")
print("█  ring1 = c^{-σ} (J_red / space) ,  ring2 = c^{-(1-σ)} (J_blue / time)")
print("█  GR: σ=2   ·   QM: σ=½ (ring1=ring2, self-dual)   ·   UFT: the σ-sweep")
print("█" * 78)
for sigma, tag in [(0.5, "QM  σ=½  (Noether balance — ring1=ring2)"),
                   (1.0, "YM  σ=1"),
                   (2.0, "GR  σ=2")]:
    print("\n" + "─" * 78)
    print(f"  {tag}")
    print("─" * 78)
    print(f"  {'constant':12s} {'space c^-σ':>13s} {'time c^-(1-σ)':>14s} "
          f"{'|Γ|':>8s} {'scale-fac':>10s}   Γ (Z0=1+1j)")
    for nm in [n for n in CONST if n not in IMAG] + ["φ"]:
        c = CONST[nm][0] if nm in CONST else EXTRA[nm]
        r1 = c ** (-sigma)
        r2 = c ** (-(1.0 - sigma))
        Z = complex(r1, r2)
        Z0 = complex(1.0, 1.0)
        G = ring_chart_gamma(Z, Z0)
        sf = chart_scale_factor(Z, Z0)
        print(f"  {nm:12s} {r1:>13.6f} {r2:>14.6f} {abs(G):>8.4f} {sf:>10.4f}   "
              f"{G.real:+.4f}{G.imag:+.4f}j")
    # i on the pure-time axis
    Z = complex(0.0, 1.0)
    G = ring_chart_gamma(Z, complex(1.0, 1.0))
    print(f"  {'i':12s} {'0':>13s} {'1':>14s} {abs(G):>8.4f} "
          f"{chart_scale_factor(Z, complex(1,1)):>10.4f}   {G.real:+.4f}{G.imag:+.4f}j   "
          f"← pure time (space part 0)")


# ── FRAMING 3 — THREE-RING  past | now | future  (Penrose {4:8:4}) ─────────
print("\n\n" + "█" * 78)
print("█  FRAMING 3 — THREE-RING   past (gain 0, i⁻) | now (gain 1) | future (gain √2, i⁺)")
print("█  anchor Z0 = d*  (the σ=½ Boundary = the Cauchy slice = the NOW)")
print("█" * 78)
rows = table("Penrose reading", D_STAR, [n for n in CONST if n not in IMAG] +
             ["φ", "√2", "1 (identity)", "d*_spec", "10 (decade)"])
print("\n  gain / sector reading (u = e-folds from the now):")
for nm, c, Gr, aG, u in rows:
    if aG < 0.2449:
        g = "gain 1  — isometric, occupiable (this IS the now)"
    elif Gr < 0:
        g = f"gain 0  — PAST: {abs(u):.2f} e-folds below d*, write-once, → i⁻"
    else:
        g = f"gain √2 — FUTURE: {u:.2f} e-folds above d*, forward-divergent, → i⁺"
    print(f"    {nm:12s} {g}")


# ── FRAMING 4 — FOUR-RING  N | S | E | W   (log-polar / native space) ──────
print("\n\n" + "█" * 78)
print("█  FRAMING 4 — FOUR-RING   log-polar (spherical complex radial polar)")
print("█  N–S meridian = magnitude fold (Z0=d*) ;  E–W = phase  (arg c)")
print("█  N: |c|>d*   S: |c|<d*   E: arg=0 (real+)   W: arg=π (real−)   poles: arg=±π/2 (i)")
print("█" * 78)
print(f"  {'constant':12s} {'|c|':>14s} {'arg(c)':>9s}  {'Γ_mag (N/S)':>12s} "
      f"{'compass':>10s}   note")
for nm in list(CONST):
    c = CONST[nm][0]
    if nm in IMAG:
        cc = complex(0.0, 1.0)
    else:
        cc = complex(c, 0.0)
    Gm = ring_chart_gamma(complex(abs(cc)), complex(D_STAR)).real
    arg = math.atan2(cc.imag, cc.real)
    if abs(abs(arg) - math.pi / 2) < 1e-9:
        comp = "N pole" if arg > 0 else "S pole"
        comp = "POLE (i)"
    elif abs(arg) < 1e-9:
        comp = ("NE" if Gm > 0 else "SE")
    else:
        comp = ("NW" if Gm > 0 else "SW")
    note = "on N–S polar axis — orthogonal to every real facet" if nm in IMAG else \
           ("outside BK ceiling" if c > OMEGA else
            "inside BK domain" if c >= ALPHA_F else "below BK floor")
    print(f"  {nm:12s} {abs(cc):>14.8f} {arg:>9.5f}  {Gm:>12.6f} {comp:>10s}   {note}")

print("""
  ALT 4-ring (for the PHYSICS REGIMES, not the constants): two involutions —
    E–W  =  s ↔ 1−s   fold, fixed at σ=½   (QM / Riemann functional equation)
    N–S  =  s ↔ 4−s   fold, fixed at σ=2   (GR / Cayley–Dickson–Joukowsky)
    UFT  =  both folds active (the full chart)
  places:  GR σ=2 (N–S centre) · YM σ=1 · QM σ=½ (E–W centre) · Riemann σ=½ (E–W centre)""")
for reg, sig in [("GR", 2.0), ("YM", 1.0), ("QM", 0.5), ("Riemann", 0.5)]:
    g_ew = (sig - 0.5) / (sig + 0.5)          # s↔1−s fold about σ=½
    g_ns = (sig - 2.0) / (sig + 2.0)          # s↔4−s fold about σ=2
    print(f"    {reg:9s} σ={sig:<3}  Γ_EW={g_ew:+.4f}  Γ_NS={g_ns:+.4f}")


# ── PAIRWISE — scale-blind relationships ──────────────────────────────────
print("\n\n" + "█" * 78)
print("█  PAIRWISE — how the facets sit RELATIVE to each other")
print("█" * 78)
core = ["α_Fermat", "mass gap Δ", "d*", "ln φ", "Ω_RiemannZ", "e", "π"]
print("\n  log-distance  ln(row / col)   (e-folds apart; + = row is larger):")
print("            " + "".join(f"{n[:9]:>10s}" for n in core))
for a in core:
    ca = CONST[a][0]
    line = f"  {a:9s} "
    for b in core:
        cb = CONST[b][0]
        line += f"{math.log(ca/cb):>10.3f}"
    print(line)

print("\n  cross-ratio  (α_F, d*, Ω_ζΣ ; c)  — scale-blind position of c in the BK domain")
print("  (α_F→0, d*→∞, Ω_ζΣ→1 are the reference-point images; c between them reads as a ratio):")
for nm in core + ["φ", "√2", "1 (identity)"]:
    c = CONST[nm][0] if nm in CONST else EXTRA[nm]
    if min(abs(c - ALPHA_F), abs(c - D_STAR), abs(c - OMEGA)) < 1e-12:
        print(f"    {nm:12s}  (reference point)")
        continue
    cr = cross_ratio(complex(ALPHA_F), complex(D_STAR), complex(OMEGA), complex(c))
    print(f"    {nm:12s}  CR = {cr.real:+.6f}{cr.imag:+.6f}j")

print("\n\n" + "█" * 78)
print("█  FOLD ACCOUNTING — every constant as one ADD:SCALE:SIGN chain")
print("█  past = ADD (pick the origin d*_face) · now = SCALE (the fold) · future = SIGN (the side)")
print("█  the fold: Γ = tanh(½·u),  u = ln(c / d*_face)   —  ONE SCALE per (constant, face)")
print("█  shape = tanh (hyperbolic) ;  direction = sign(u) ;  depth = 1 (no re-anchoring here)")
print("█" * 78)
FACES = [("Boundary", D_STAR_BOUNDARY), ("Flow/taut", D_STAR_TAUT), ("Translator", D_STAR_TRANS)]
print(f"\n  {'constant':12s} " + "".join(f"{('u/'+n)[:11]:>12s}" for n, _ in FACES)
      + f"{'|Γ|@Flow':>10s} {'dir':>5s}   chain (SIGN∘SCALE∘ADD on ln c)")
for nm in [n for n in CONST if n not in IMAG] + ["φ", "√2"]:
    c = CONST[nm][0] if nm in CONST else EXTRA[nm]
    cells = ""
    for _, fv in FACES:
        u = math.log(c / fv)
        cells += f"{u/LN10:>12.4f}"          # decades from that face  (ln(10) coordinate)
    G_flow, aG, u_flow = fold(c, D_STAR_TAUT)
    direction = "→i⁺" if u_flow > 0 else "→i⁻"
    g = "+1" if u_flow > 0 else "-1"
    chain = f"SIGN({g}) ∘ SCALE(tanh, |u|={abs(u_flow):.3f}) ∘ ADD(-ln d*_Flow)"
    print(f"  {nm:12s} {cells}{aG:>10.4f} {direction:>5s}   {chain}")
print(f"""
  reading:
   · ADD and SIGN are FREE (translation + one bit) — they only choose the origin
     face and the side. ALL the work is the single SCALE fold, tanh-shaped.
   · one traversal of N constants at one face = N folds, all depth 1, all tanh.
   · re-anchoring (fold the folded: d*_face → some c → new anchor) is what raises
     depth; nested folds compose as  Γ_total = tanh(½ Σ_k u_k).
   · GROUND STATE: a_k→0, s_k→1, g_k→+1  ⇒  c = d*_face  ⇒  Γ = 0  ⇒  the now / viewport.
   · the 4th column (Stability / RG face) is OPEN — its decade-coordinate is the
     missing entry that would close the 4D d* frame.""")

print("\n  notable ratios:")
for lbl, v in [
    ("d* / d*_spec", D_STAR / D_STAR_SPEC),
    ("Ω_ζΣ / d*  (= ln 10)", OMEGA / D_STAR),
    ("π / e", math.pi / math.e),
    ("ln φ / d*", LN_PHI / D_STAR),
    ("Ω_ζΣ / ln φ", OMEGA / LN_PHI),
    ("d* / ln φ", D_STAR / LN_PHI),
    ("(α_F·Ω_ζΣ)^½ / d*", GEOM_MEAN / D_STAR),
    ("mass gap Δ / α_F", GAP / ALPHA_F),
    ("α_F · 100 · √2", ALPHA_F * 100 * math.sqrt(2)),
    ("1/α_F", 1 / ALPHA_F),
    ("e^{-1/d*}", math.exp(-1 / D_STAR)),
]:
    print(f"    {lbl:24s} = {v:.8f}")
