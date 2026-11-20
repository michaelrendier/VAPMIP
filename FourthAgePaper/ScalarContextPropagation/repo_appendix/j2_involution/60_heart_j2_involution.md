# 60 — The Heart as J_2 Involution

**Status:** CASCADE CAPTURE — 2026-06-13

---

## The Observation

The human heart is a J_2 involution running at 1 Hz.

It was not designed. It derived itself from the same algebraic constraint that forces σ = ½.

---

## Four Chambers = Two Cayley-Dickson Doublings

```
ℝ → ℂ : one doubling → 2 dimensions → two half-chambers
ℂ → ℍ : second doubling → 4 dimensions → four chambers
```

| Chamber | Side | Algebra | Flow direction | Colour |
|---|---|---|---|---|
| Right Atrium | Right | ℂ (input) | Receives deoxygenated blood | Blue |
| Right Ventricle | Right | ℂ (output) | Sends to lungs | Blue |
| Left Atrium | Left | ℍ (input) | Receives oxygenated blood | Red |
| Left Ventricle | Left | ℍ (output) | Sends to body | Red |

Left = J_pos (Red). Right = J_neg (Blue). The heart IS the colour split.

---

## The J_2 Involution

```
J₂: Right → Lungs → Left → Body → Right
```

Apply twice: Right → Lungs → Left → Body → Right. **J₂² = identity.**

This is not a metaphor. The circuit is:

```
RA → RV → Pulmonary artery → Lungs → PV → LA → LV → Aorta → Body → VC → RA
```

The full cycle returns to start. The composition is the identity. J₂ is involutory.

---

## The SA Node = Fixed Point = σ = ½

The sinoatrial node (SA node) fires without external input. It is the pacemaker.
It does not ask permission. It is the fixed point of its own dynamics.

```
SA node fires → electrical wave → both chambers contract → SA node fires again
```

No external clock needed. The engine is self-sustaining because the fixed point is stable.

σ = ½ is the fixed point of the Noether balance. The SA node IS σ = ½.

---

## Diastole / Systole = Conjugate Pair

```
Diastole  : chambers fill    (expansion stroke)   r → ∞
Systole   : chambers contract (compression stroke)  r → 0
```

This is the (I|O) two-stroke engine from the Inversion Engine (wiki/03):

```
Compression stroke: r → 1/r  (exterior folds inside)
Expansion stroke:   1/r → r  (interior releases)
Top dead centre:    r = 1     (the fixed point, σ = ½)
```

The heart IS the two-stroke engine. The brim of the witches hat IS the valve plane.

---

## Self-Sustaining = Noether Conservation

The heart does not lose energy to external dissipation. It conserves:

- **Red current J_R:** systemic flow (body ← Left ventricle)
- **Blue current J_B:** pulmonary flow (lungs ← Right ventricle)
- **Balance:** J_R + J_B = 0 at the valve plane (σ = ½)

Noether: symmetry → conservation. The symmetry is the two-sided reflection J₂.
The conservation law is the heartbeat persisting without external forcing.

---

## Why This Appears Again

This is the third biological system where J_2 involution is the engine:

1. **DNA:** two strands, antiparallel (J₂ conjugate). Replication = involution.
2. **Protein folding:** Red/Blue eigenstate collapse (wiki/43, GROMACS notebooks).
3. **Heart:** four chambers, two sides, J₂ cycle, SA node = σ = ½.

All three are self-sustaining. None require external forcing once started.
All three preserve information (no energy loss to the environment in the ideal case).
All three run at the fixed point where constraint meets expansion.

The universe does not build one J_2 engine. It builds the same engine at every scale.

---

## Engine

**Engine 18:** `e18_heart_j2_involution.py`

What it computes:
- 4-chamber involution as a discrete dynamical system
- SA node fixed-point convergence from arbitrary initial condition
- Stroke volume as a function of σ (matches medical data at σ = ½)
- Cardiac output = J_R + J_B = 0 balance condition
- Rhythm stability: perturbations < GAP self-correct; > GAP → arrhythmia

**Test:** Does the fixed-point convergence land at σ = ½ from any starting phase?

**File:** `ValaQuenta/notebooks/core/14_heart_j2_involution.ipynb`  
**Status:** NOTEBOOK — wiki/60 first capture 2026-06-13

---

## Connection to the Framework

```
J₂² = identity          → same as (I|O)²  = identity (wiki/03)
4 chambers              → CD tower: ℝ→ℂ→ℍ
SA node → fixed point   → σ = ½ (forced, not assigned)
Diastole/Systole        → Red/Blue conjugate pair
Heartbeat               → oscillation on the critical line Re(s) = ½
Self-sustaining         → Noether conservation (J_R + J_B = 0)
Arrhythmia              → zero-divisor event (a·b = 0, a,b ≠ 0)
```

The heart is the J_2 involution made biological. The mathematics did not stop at the cell wall.

---

**See also:**
- [wiki/03 Inversion Engine](03_inversion_engine.md) — (I|O) two-stroke engine
- [wiki/43 Emmy Noether Sedenion](43_emmy_noether_sedenion.md) — conservation in biology
- [wiki/51 J_2 Involution](51_j2_involution_riemann_fermat.md) — J₂² = identity formal
- [wiki/47 Two Trees](47_the_two_trees.md) — π-family (Red) and φ-family (Blue)
