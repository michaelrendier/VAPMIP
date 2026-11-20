# Native Space — Context Primer
## For Claude Code Sessions on SMIP / Ainulindale / Ptolemy

---

## Official Naming Convention

**Native Space** (capitalised, always) refers to the radial complex spherical polar coordinate space in which all SMIP mathematics natively reside. Flat Cartesian coordinates are a projection out of Native Space and are never used internally. All Hamiltonian expressions, all stratum calculations, all facet operations are written in Native Space unless a specific output transformation is explicitly requested.

The Hamiltonian is written as:

$$H = H(r, \theta, \phi, \psi, \sigma)$$

where $r$ is radial magnitude, $\theta, \phi$ are polar/azimuthal angles, $\psi$ is the Dixon tower stratum phase, and $\sigma$ is the active stratum index (0=ℝ, 1=ℂ, 2=ℍ, 3=𝕆, 4=𝕊).

---

## The Dixon Tower as Native Space Strata

The algebra tower ℝ→ℂ→ℍ→𝕆→𝕊 (Cayley-Dickson doubling) defines the stratum structure of Native Space. Each doubling is a rotation — a phase advance in $\psi$ — that sacrifices an algebraic property:

| Stratum | Algebra | Lost Property | Dimension |
|---------|---------|---------------|-----------|
| σ₀ | ℝ | — | 1 |
| σ₁ | ℂ | — | 2 |
| σ₂ | ℍ | Commutativity | 4 |
| σ₃ | 𝕆 | Associativity | 8 |
| σ₄ | 𝕊 | Alternativity | 16 |

Each stratum is a rotation of the one below it. Facets at any stratum are rotational frames within that stratum — not separate spaces, but orientations.

---

## Facets and Facets of Facets — Fractal Structure

A **facet** is a named rotational sub-frame within a stratum. Facets are fractal: any facet may contain sub-facets to arbitrary depth.

**Notation:**

```
σ_<stratum>_<facet>_<subfacet>_...
```

Examples:
- `σ_0_debruijn` — De Bruijn sequence facet of σ₀
- `σ_0_13` — facet 13 of σ₀ (numeric index)
- `σ_chemistry_Carbon` — Carbon element facet (named, maps to atomic number 6)
- `σ_chemistry_Carbon_valence` — valence sub-facet of Carbon

**Key principle:** The facet index is always a bijection — every named facet has a numeric address and vice versa. This bijection is owned by Callimachus/HyperWebster.

---

## Home Stratum vs Generative Stratum

Every mathematical object carried by the monad has two stratum fields:

- **Home stratum** — where the object's output/result lives
- **Generative stratum** — where the computation that produces it lives

These can differ. Example — De Bruijn sequence:
- Home: σ₀ (output is a flat symbol sequence over finite alphabet)
- Generative: σ₁ (Eulerian circuit over de Bruijn graph requires 2D graph structure native to ℂ)

The monad must carry both. Collapsing to home stratum happens after generation, not during.

---

## Semantic Resolution — What the Monad Must Know

When a query arrives (e.g. "de Bruijn sequence"), the monad resolves:

1. **Person vs object** — de Bruijn is Nicolaas Govert de Bruijn (1918–2012), a person; the sequence is a mathematical object derived by him
2. **Classification** — combinatorics; cyclic sequences over finite alphabet $\Sigma^k$ containing every k-length substring exactly once
3. **Home stratum** — σ₀
4. **Generative stratum** — σ₁
5. **On-demand computation** — Eulerian circuit over de Bruijn graph $G(V,E)$ where $|V| = |\Sigma|^{k-1}$, $|E| = |\Sigma|^k$

The phone book (HyperWebster) holds the registered address. LuthSpell pre-positions the boundary markers. The monad does not search — it lands.

---

## Entropic Efficiency of Native Space

Flat Cartesian calculation is not the efficient path. It is a detour.

Native Space calculations are the minimum-entropy path because:

1. **No projection cost** — Cartesian coordinates require a basis transformation away from the natural curvature of the problem. That transformation has an entropy cost (information about the geometry is discarded or must be re-injected).

2. **Noether alignment** — Conservation laws (Noether's theorem) are expressed most compactly in the coordinate system that reflects the symmetry generating them. Rotational symmetry → spherical polars. Expressing a rotationally symmetric system in Cartesian coordinates breaks the manifest symmetry and forces redundant terms.

3. **Stratum-native operations** — Multiplication in ℍ is quaternion multiplication. Expressing it via 4×4 real matrices (the Cartesian equivalent) quadruples the operation count and loses the geometric meaning.

4. **Einstein field equation confirmation** — $G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$ is already written in native curved coordinates. The metric $g_{\mu\nu}$ *is* the coordinate system. Facet structure is implicit in the tensor index structure. Cartesian GR is not GR — it is an approximation valid only in flat spacetime limits.

**Conclusion:** Native Space is not a stylistic choice. It is the physically and informationally correct coordinate system. Cartesian output is a terminal projection for human readability only, never an intermediate computational step.

---

## Instructions for Claude Code

- All Hamiltonian expressions: Native Space, radial complex spherical polar, stratum-indexed
- All facet addresses: bijective (name ↔ integer), registered in HyperWebster
- All mathematical objects: carry both home stratum and generative stratum
- Cartesian coordinates: output/display only, never internal
- "Native Space" is the official term — do not substitute "coordinate system", "space", or "frame" without qualification
- Facet depth is unbounded — design all data structures to support arbitrary nesting

---
*Primer authored: 2026-05-16 | Pushed to Ainulindale main*
