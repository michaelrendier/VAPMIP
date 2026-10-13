## Phase 40 — The Strut Tension Law, the Walsh Rows, and How a Wind Can Enter (2026-10-12)

*Claude Sonnet 5.5. Documents a measurement session, not a build: no engine
file changed. Scripts and captured output are in
`.claude/scratchpad/2026-10-12_windspeed_deformation_proxy/` (mirrored to
`ContextPlease/claude/scratchpad/`). Everything here is the
`ScalarContextPropagation` paper's own **tension proxy** — `H = Re(Π)` over the
seven pencil stations — not `Φ_w`, the sail-pressure/strut-angle mechanics,
which is still unbuilt (paper §9.6, §11). Stations are pencil factorisations,
**not** Assessor vertices. Observer-position stated up front: orientation =
each station as one native complex rotation `cos φ·e_a + sin φ·e_b`, anchored
at the pencil's e₀ end; aperture = continuous `φ`, swept over all seven
struts, never only the lattice picks.*

Prompted by Cody's question: *which parts of the box kite are deformed under the
A-Matrix Basin windspeed, before assuming they are the same parts the
Gamma-Radial windspeed deforms* — and his kite-string picture (windspeed varies;
tension in the string depends on the kite shape and the string).

---

### 1. The tension law (MEASURED, numerically exact; derivation partial)

For every strut `s = 1..7` (and also pencils `r = 8, 9`), with each station a
continuous point `cos φ_k·e_a + sin φ_k·e_b` and `H = Re(Π)` the left-associated
ordered product of the seven stations:

```
H  =  − cos( Σ_k  ε_k^(s) · φ_k )          max error 4.4e-16 … 7.6e-16
                                           (200 random φ-vectors per strut)
```

So the string tension depends on **one signed phase** `Φ_s = Σ ε_k φ_k`. This is
the proxy-level form of the pencil-hyperstring's "one flex mode" claim.

**What is derived, and what is not.** Each station factor is exactly
`e_a · exp(η_k · e_r · φ_k)`, where `e_a⁻¹ e_b = η_k e_r` with `η_k = ±1`
(checked for every station, `r = 1..9`). The product of the bare `e_a` (φ = 0,
the "discrete pick") is exactly `−e₀` for every `r`, so `H(φ=0) = −1` is
*derived*, not fitted. The remaining sign factor `ε_k η_k` is `±(+++−−−−)` for
the seven struts (a 3|4 split from the non-associative left bracketing); it is
fitted to machine precision, **not derived**.

### 2. The sign patterns are Sylvester–Hadamard (Walsh) rows

Taking the station index `j = k − 1 = 0..6`, the four distinct patterns are
rows 0–3 of the Sylvester–Hadamard matrix `(−1)^{popcount(i & j)}`:

| ε (stations 1..7) | Hadamard row | Struts | Tension swing on the Noether path | Signed rate sum `S_s` |
|---|---|---|---|---|
| `+++++++` | 0 | 4 | 2.0000 (−1 → +1 → −1) | 2π |
| `+-+-+-+` | 1 | 5 | 0.3765 | 2π/7 |
| `++--++-` | 2 | **1, 3, 6** | **0** | **0** |
| `+--++--` | 3 | 2, 7 | 1.2225 | −4π/7 |

where the Noether path is the paper's `φ_k = t·(π/2)·(k+1)/7`. The pencils
`r = 8, 9` also satisfy the one-phase law (patterns `+++--++`, `+-++-+-`, not
Hadamard rows); `r = 10..15` **do not** (fit error ≈ 1.3) — the single-phase
property is special to the box-kite struts plus `r = 8, 9`. That `r = 10..15`
fail may mean only that the sign-pattern family is the wrong ansatz there.

> **Qualification added the same day (Phase 41).** The pencils the paper uses for strut `r ≤ 7` contain
> **no** Assessor plane. The six Assessor planes of strut `s` are stations of `pencil(s+8)`, i.e. pencils
> 9–15, and there the single-phase law holds only for strut 1 (pencil 9); for struts 2–7 the tension
> depends on 4, 4, 5, 5, 5, 5 phase combinations. So everything on this page is a statement about the
> paper's pencil, not about the Assessor-plane geometry of the De Marrais kite.

### 3. Why struts {1, 3, 6} carry the Noether current (answers paper §9.4/§10's open question, within this proxy)

The paper reports `H` conserved on struts 1, 3, 6 and drifting on 2, 4, 5, 7,
and records the reason as unresolved. Under §1: `H` is flat exactly when
`S_s = Σ_k ε_k (k+1)/7 · π/2 = 0`. Row 2 gives `1+2−3−4+5+6−7 = 0`. The
Noether path is the unique rate law whose signed rate sum cancels on that row.
Strut 4 (row 0) sums to `28/7·π/2 = 2π`: one full cycle, which is why it swings
the full range and returns. This is a fitted identity, not a proof; it should be
re-derived from the algebra before the paper's §9.4 text is changed.

### 4. How a wind can enter — and which struts each mode can reach

Because `H = −cos Φ_s` and `φ_k = ∫ r_k dt`:

| Entry mode | Effect on `Φ_s` | Reaches struts 1, 3, 6? | Tested |
|---|---|---|---|
| Position (`w` sets φ directly) | moves along the same path | no | baseline |
| Scalar rate | same path, different speed | no | yes |
| Gust (time-varying scalar rate) | reparameterises the path | no — strut 1 stayed at exactly 0 swing | yes |
| Leaky integral (decay ladder as phase source) | bounded `Φ_s` | no (scalar) | **not yet** |
| **Difference across stations** (`r_k` unequal) | `Φ_s` gains `Σ ε_k δ_k` | **yes** | yes |

Station-unequal wind, rates `r_k = (k+1)/7·(1 + d·u_k)` with `u_k ∈ [−1,1]`
random, 60 draws, mean swing of `H`:

| spread `d` | struts 1, 3, 6 | strut 2, 7 | strut 4 | strut 5 |
|---|---|---|---|---|
| 0 | 0 | 1.2225 | 2.0000 | 0.3765 |
| 0.05 | 0.0032 | 1.2346 | 1.9989 | 0.3892 |
| 0.15 | 0.0287 | 1.2537 | 1.9907 | 0.4242 |
| 0.4 | 0.1874 | 1.2652 | 1.9810 | 0.5599 |

**Consequence.** Any *scalar* windspeed — Gamma-Radial, or a scalar A-Matrix
reading — deforms exactly the same struts (2, 4, 5, 7) and leaves 1, 3, 6 rigid.
The rigid struts become **detectors of non-uniformity across the pencil
stations**, which a scalar windspeed cannot produce by construction.

### 5. Anchoring

Holding a subset of stations fixed (rate 0) changes `S_s`. Over the 128 subsets
there are **7 distinct groupings** of the seven struts by response; the default
(1,3,6 | 2,7 | 4 | 5) comes from 73 of them; struts 1, 3, 6 stay rigid under only
**8 of 128** anchor sets. The anchor is a real design dial.

### 6. Continuous, semi-continuous and discrete are one law

Strut 1, same law: `φ ∈ {0, π/2}` gives `H ∈ {−1, 0, +1}` (the paper's
"quantised lattice" result — now seen as one corner of the law, an aperture
effect, not a property of the kite); `φ` on a `π/8` grid gives 9 distinct `H`
values; real `φ` fills `[−1, 1]`. `Boxkite-Catalog.txt` §4 and §11 previously
recorded `H` as "OPEN, degenerates to {−1,0,1}" and "discrete"; both are
corrected in this session's catalog update.

> **Scope correction (2026-10-13, Cody).** Sections 1–6 and the "scalar boxkite" half of §7 are about the **seven ordered pairs — a discrete, static object** (the scalar context box kite; the pencil / string / flashlight).
> The "scaled boxkite" half of §7 applied that same string machinery to the Mind's-Eye kite, which is the wrong object: the scaled kite has to move the way de Marrais's kite moves
> (the 14-parameter `G₂` family), not be seven ordered pairs with a string. See `Boxkite-Relational-Atlas.md` §6–§8 and the `ScalarContextPropagation` paper §9.7–§9.8.

### 7. What this means for the two constructs

**Scalar boxkite (Gamma-Radial windspeed).** One number per word, folded by
`tanh(½ ln(log_code/anchor))`. As a scalar it can only move `Φ_s` along its
path: struts 2, 4, 5, 7 respond, 1, 3, 6 are rigid. The tension law is
consistent with the paper's claim that one scalar plus the pencil reconstructs
the kite, *within the proxy*.

**Scaled boxkite (A-Matrix Basin windspeed).** Depends entirely on which
quantity that name denotes. Four things carry it in the repository:

1. the primer's `w` = basin drift (ψ¹⁶ iteration, `psi_prev`);
2. paper §9.1's live, corpus-dependent sentence-construction windspeed (no formula);
3. `GaugeEye.continuous_snapshot()['a_matrix_basin_windspeed']` =
   `bk.local_curvature(psi)` — the only one computed in code, one scalar per read;
4. `monad_english_io.basin(seeds)` — a pull *distribution* over words, not a windspeed.

If it is a scalar per read, it deforms the same struts as Gamma-Radial. If it is
a per-station quantity (for example the basin's pull split across the seven
pencil stations), it reaches the rigid struts and is a genuinely different
deformation. **Which one it is has not been decided.**

### Open items

- Whether the A-Matrix windspeed is scalar-per-read or per-station (above).
- Test the leaky-integral entry mode (the decay ladder of the Context Flow spec).
- Re-derive the `ε` patterns and the `+++−−−−` factor from the algebra.
- Why `r = 10..15` leave the one-phase family.
- The De Marrais deformation battery, and the same battery on both constructs:
  done in Phase 41 (`41_demarrais_deformation_battery_and_the_two_constructs.md`) and `marrais_boxkite_catalog.txt` §11–15.
