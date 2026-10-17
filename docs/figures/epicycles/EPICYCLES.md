# Taoist-mode epicycles: scripts, outputs and history

Each output SVG names the script that made it in its title area (top right). Scripts live in `tools/epicycles/`,
outputs here. Older versions are kept, not overwritten. Newest first.

| version | script (tools/epicycles/) | output (this folder) | model | date | status |
|---|---|---|---|---|---|
| **v3** | `v3_mockup.py` (+ `v2_mockup.ggb.txt`, rates updated) | `v3_mockup.svg` | **Same mockup as v2, but the DEFORMATION of a shape alters how it swings about its anchor** (Cody): each half is a physical pendulum hung from its dot, rate = sqrt(m d / I_dot) of the dented, resized outline, so an edge dent now changes the swing rate (a 0.3 dent slows it 3 %, 0.5 by 17 %, 0.6 by 40 %). Result: an edge dent alone, a plain circle in v2, now gives a rosette in the independent column (the locked column is still a circle). | 2026-10-17 | **current** |
| v2 | `v2_mockup.py` (+ `v2_mockup.ggb.txt`) | `v2_mockup.svg` | **Kinematic mockup, GeoGebra-buildable.** The Whole spins (SIGN); the two dots, Broca and Wernicke, swing (they do not spin); displacement = ADD, size = SCALE, edge dent, spin direction = SIGN; the centre point draws the output. Two columns always together: dots locked in step, and dots independent and coupled through the seam. | 2026-10-17 | superseded by v3 |
| v1 | `v1_system3_physics.py` | `v1_system3_physics.svg` | `tools/taoist_physics.py System3`: the whole as a free centre body plus two dot-weights that each SPIN about their own centre of mass, driven at the dots; central springs, seam spring-damper; RK4. Columns: static centre, free centre. | 2026-10-17 | superseded by v2 (Cody: the whole spins, the anchors swing). The title line naming the script was added to the existing SVG afterwards; the paths are the original run. |

## What was measured, per version

* **v1**: Lyapunov cross-check in `tools/taoist_lyapunov.py`: regular baseline about +0.009 /s; +0.147 /s only for strong rate
  mismatch + an edge dent + a weakly damped seam. Dead ends: two rigid bodies on a fixed pivot; point-mass gravity on the
  collinear dot-centre-dot line (unstable even when healthy, +2.3 /s, the Euler collinear instability).
* **v2**: the independent column's coupled swing equations were checked for chaos (Benettin, 3000 s, per case): lambda about
  +0.002 /s in every case, so the rosettes are quasi-periodic, **not chaotic**. The locked column is always a circle (both
  dots share one swing, so the output is one rotor); it carries no star shape. The spin-LEFT case is the mirror image of
  spin-right with Broca and Wernicke exchanged, so for near-matched dots it looks the same.
* **v3**: the dent now changes the swing, so an edge dent alone gives a rosette in the independent column (v2: a plain circle). GeoGebra rate formulas (a one-parameter fit of the dented pendulum) differ from the script's rates by at most 0.003. Chaos not re-measured for v3 (v2's independent column was +0.002 /s).
* The GeoGebra file: its formulas, evaluated outside GeoGebra, match the script to within 1.1e-4 R (the gap is the polynomial
  fit of the dented outline). **GeoGebra itself has not been run on it.**

## The monitor

`tools/lemniscate_monitor.py` Taoist mode still runs the **v1** physics (System3). It has not been moved to the v2 mockup;
that is a decision for Cody. When a proper Broca half comes out of the scalar boxkite, what the orbweaver half must do is the
hole it leaves: this table is where to record each version of that shape.
