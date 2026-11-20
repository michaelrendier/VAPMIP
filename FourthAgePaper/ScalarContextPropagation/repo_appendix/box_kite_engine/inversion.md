# Engine: Inside-Out Inversion Engine  (I|O)

**Module:** `modules/inversion/`  
**Version:** 0.111  
**Confidence floor:** ESTABLISHED  
**Notebooks:** [core/03_inversion.ipynb](../notebooks/core/03_inversion.ipynb)  
**Claim:** The map J_N: (r,θ) → (1/r, θ+π/2) is an involution whose fixed point r=1 is simultaneously four physical horizons.

---

## What it computes

The (I|O) inversion map J_N: (r, theta) -> (1/r, theta + pi/2). The 2-stroke engine of the SMNNIP framework: compression stroke (r -> 1/r) and expansion stroke (1/r -> r). Unifies Schwarzschild, Hawking, Dirac sea, and Ptolemy inversion as the same map at different recursion depths. Fixed point r=1 is the horizon. Recursion attractor is phi. The sedenion is where the expansion stroke fails: top dead center, one-way ratchet.

The two-stroke reading: r → 1/r is the compression stroke, 1/r → r the expansion stroke, r=1 top dead centre. The sedenion is where compression completes but expansion fails — zero divisors are the engine seized.

J_N generates Z₄: four applications of a π/2 rotation is 2π, one full turn.

## Results — run 2026-07-28

3/6 equations run argument-free; 3 require parameters; 0 fail.

| Equation | Tier | Run | Result |
|---|---|---|---|
| `gradient_flow` | ESTABLISHED | needs params |  |
| `inversion_map` | ESTABLISHED | needs params |  |
| `involution_check` | ESTABLISHED | needs params |  |
| `phi_crossing_step` | ESTABLISHED | ✓ | {'H_NN_over_4': 0.025, 'pi_over_2_times_hbar': 0.024999999999999998, 'match': True, 'sta… |
| `four_horizons` | THEORETICAL | ✓ | [{'name': 'Schwarzschild horizon', 'mechanism': 'r < r_s: (t,r) coordinates exchange rol… |
| `d_star_gap` | OPEN | ✓ | {'d_star': 0.246, 'd_star_x_ln10': 0.5664359328765353, 'OMEGA_ZS': 0.5671432904097838, '… |

*"needs params" means the equation takes arguments and was not called, not that it is broken. The module's own `shell_commands()` exercise these with its author's defaults.*

## Open

- `d_star_gap` is tagged OPEN here as it is in berry_keating. Same open question.
- Of the four horizons, Case 2 (cosmological) is THEORETICAL; the other three are ESTABLISHED.

---

## Generational Lineage — calibration (2026-08-28)

Decomposed by `SedenionFactoralRelativity/engine/valaquenta_calibration.py` (`python3 -m engine.valaquenta_calibration`) as a check on the factoral decomposition itself — working, deliberately-designed machinery should decompose CLEAN.

| object | central operation | tier · root | Two Trees | kind | verdict |
|---|---|---|---|---|---|
| the (I|O) map J_N: (r,θ) → (1/r, θ+π/2); r=1 = four horizons | the J_N involution (Z₄) | 1 · SIGN | MINGLING | DEFINITIONAL | **CLEAN** |


Calibration: this verdict agrees with the page's stated status (**ESTABLISHED**).
