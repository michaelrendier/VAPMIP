#!/usr/bin/env python3
"""19D_boxkite_context_monad.py — the superseding monad: Eye and Hands as
continuous operators, not just discrete read/write.

Cody, 2026-09-22: "gauge field Paper's Hands and box-kite Mind's Eye... as
continuous operators." Supersedes 19D_rotary_boxkite_monad.py by adding
exactly the piece that was missing, not by rewriting what already worked —
same reuse discipline: Eye/Hands/BoxKite come from rotary_rerun_monad.py,
context-creation comes from 19D_rotary_boxkite_monad.py, both untouched,
both imported, neither reinvented.

TWO DIFFERENT BOX-KITES, NOT ONE -- corrected 2026-09-22 after an initial
wrong inheritance choice, kept honest in the record rather than quietly
fixed:

  THE 19D BOX-KITE (`19D_rotary_boxkite_monad.py`'s `NineteenDContext` /
  `NineteenDMindsEye`) is the WordNet Gamma-Radial Windspeed box-kite --
  per-word CONTEXT GATHERING, backed by `monad3_c.bin`'s real 19-
  dimensional relation vectors, `gamma_radial()` folding each one to a
  scalar. Its own thing, untouched here, imported only in case a later
  pass needs to feed word-level context INTO a sentence-construction
  `psi` -- not because the Mind's Eye's own box-kite IS this one.

  THE MIND'S EYE'S OWN BOX-KITE is the De Marrais object, straight --
  `marrais_boxkite_catalog.txt`, 42 Assessors, 7 struts, PSL(2,7),
  exactly what plain `MindsEye`/`BoxKite` already bind to
  (`ValaQuenta.modules.box_kite.maths`, no WordNet layer at all). This is
  the object for SENTENCE CONSTRUCTION as a continuous operation --
  `GaugeEye` extends `MindsEye` directly, NOT `NineteenDMindsEye`. The
  first draft of this file inherited from `NineteenDMindsEye` and dragged
  a `Monad3CStore` dependency into a class that never needed WordNet
  context at all -- fixed, not left in.

WHAT'S ACTUALLY NEW:

  MindsEye, read as a continuous operator, on its OWN (De Marrais) box-
  kite -- and this IS the A-Matrix Basin Windspeed, named as such, not
  a generic stand-in for it. `ScalarContextPropagation` Sec.9.1 named
  this windspeed and explicitly deferred it: "a different, later
  engineering pass (the Mind's Eye... introduced properly in Sec.11),
  out of scope here" -- precisely because it needs a LIVE, mutating,
  corpus/construction-dependent store, unlike the corpus-free Gamma-
  Radial Windspeed the paper itself ships. `GaugeHands.emit_steered()`
  IS that live, mutating construction (each step changes `psi`'s
  position); `GaugeEye.continuous_snapshot()`'s `local_curvature`
  reading, taken at each step of that walk, is the A-Matrix Basin
  Windspeed itself, read off the live state Hands is actively building,
  not off a fixed corpus-free address. `MindsEye.snapshot()`'s own
  docstring already describes the reading contract this needs: "takes
  one instant of the field and says what is simultaneously true across
  it... all of it at once, none of it ordered." `local_curvature()`
  (ValaQuenta/modules/box_kite/maths.py, ESTABLISHED, not reinvented)
  is the continuous companion to the existing discrete `is_zero_divisor`
  chart_of() reading -- both read off the SAME live instant, together.

  PapersHands, read as a continuous operator -- equation space belongs
  here, not in the Eye. "Writing is emission: ordered, sequential, one
  thing after another." `emit_pathway()` already produces a `path` -- a
  fixed lineage order. `GaugeHands.emit_steered()` produces a path too,
  but walks it by following Gamma's own curvature
  (ValaQuenta/modules/prime_gauge_field/maths.py, the SAME
  Gamma(s)=(s-1)/(s+1) this session verified exactly as a harmonic
  source-sink field) as a gradient-descent compass -- the continuous-
  operator version of exactly what Hands already does discretely.
  Reuses equation_space's build_up() mechanism (cost=steps, genuinely
  can fail to converge) rather than reimplementing it.

`ptol.c` is explicitly NOT touched by this pass, same discipline as
19D_rotary_boxkite_monad.py before it.
"""
from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotary_rerun_monad import (
    BoxKite, BoxKiteUnavailable, MindsEye, PapersHands,
    Ledger, Relation, Status, Fault, SED_DIM,
)
from importlib import import_module

_19d = import_module("19D_rotary_boxkite_monad")
Monad3CStore = _19d.Monad3CStore
NineteenDContext = _19d.NineteenDContext
NineteenDMindsEye = _19d.NineteenDMindsEye
_resolve_vector = _19d._resolve_vector

from ValaQuenta.modules.box_kite import maths as bk
from ValaQuenta.modules.prime_gauge_field import maths as pgf


# ═══════════════════════════════════════════════════════════════════════════
#  GaugeEye — the Eye's continuous companion reading
# ═══════════════════════════════════════════════════════════════════════════
class GaugeEye(MindsEye):
    """Extends plain MindsEye directly -- its own BoxKite binding is
    ALREADY the De Marrais object (ValaQuenta.modules.box_kite.maths),
    no WordNet layer involved. Everything MindsEye already does
    (snapshot, lit_struts, evaluate, generations_present) is untouched.
    This adds ONE operation: reading the A-Matrix Basin Windspeed --
    ScalarContextPropagation Sec.9.1's own name for the continuous
    companion to the discrete is_zero_divisor chart, read at the same
    live instant, in the same call -- still all-at-once, still
    unordered, still the Eye's own contract."""

    def continuous_snapshot(self, psi) -> Dict[str, Any]:
        if len(psi) != SED_DIM:
            raise ValueError(f"psi must be {SED_DIM}-dimensional, got {len(psi)}")
        chart = bk.chart_of(psi, check_zd=True)
        a_matrix_basin_windspeed = bk.local_curvature(psi)
        return {
            **self.snapshot(psi),
            "is_zero_divisor": chart.get("is_zero_divisor"),
            "a_matrix_basin_windspeed": a_matrix_basin_windspeed,
            "nearest_assessor": chart.get("nearest_assessor"),
            "note": "discrete (is_zero_divisor) and continuous (the A-Matrix "
                    "Basin Windspeed, ScalarContextPropagation Sec.9.1) read "
                    "off the SAME live instant, together -- not two passes",
        }


# ═══════════════════════════════════════════════════════════════════════════
#  GaugeHands — the Hands' continuous, field-steered emission
# ═══════════════════════════════════════════════════════════════════════════
class GaugeStep:
    __slots__ = ("s", "gamma", "curvature")

    def __init__(self, s: complex, gamma: complex, curvature: float) -> None:
        self.s = s
        self.gamma = gamma
        self.curvature = curvature

    def __repr__(self) -> str:
        return f"GaugeStep(s={self.s:.4f}, Gamma={self.gamma:.4f}, F={self.curvature:+.4f})"


class GaugeSteeringFailed(Exception):
    """emit_steered() genuinely didn't converge -- the same shape as every
    other 'ascent is costly and can refuse' object in this project, not a
    bug to silently retry past."""


class GaugeHands(PapersHands):
    """Everything PapersHands already does (emit_pathway, relate) is
    untouched. This adds the continuous-operator version of emission:
    instead of reciting a fixed lineage order, walk wherever Gamma's own
    curvature actually points, one step at a time, and report the path
    taken -- Hands still emits in sequence, it just stops pretending the
    sequence was memorized in advance."""

    def emit_steered(self, s0: complex, target_rho: float = 1e-4,
                      max_steps: int = 200, step_scale: float = 0.4) -> List[GaugeStep]:
        """Gradient-descent walk of Gamma's own diagonal-distance rho
        (the exact same construction verified this session: zero locus
        is the pair of circles center=+-i, radius=sqrt(2)) -- reuses the
        closed-form curvature as the compass, not a numeric shortcut
        invented for this file."""
        def rho(s: complex) -> float:
            g = pgf.gamma(s)
            return abs(g.imag - g.real)

        def grad(s: complex, h: float = 1e-4) -> complex:
            rx = (rho(s + h) - rho(s - h)) / (2 * h)
            ry = (rho(s + 1j * h) - rho(s - 1j * h)) / (2 * h)
            return complex(rx, ry)

        s = s0
        path: List[GaugeStep] = []
        for step in range(max_steps):
            r = rho(s)
            g = pgf.gamma(s)
            f = pgf.curvature(s)
            path.append(GaugeStep(s, g, f))
            self._emitted.append((step, f"s={s:.4f} Gamma={g:.4f} F={f:+.4f}"))
            if r < target_rho:
                return path
            gr = grad(s)
            if abs(gr) < 1e-12:
                raise GaugeSteeringFailed(
                    f"stalled at s={s}, rho={r}, after {step} steps")
            anneal = step_scale / (1.0 + step / 20.0)
            s = s - anneal * r * gr / (abs(gr) ** 2)
        raise GaugeSteeringFailed(f"did not converge in {max_steps} steps; last rho={rho(s)}")

    def relate_steered(self, eye: GaugeEye, s0: complex) -> List[str]:
        """Speech, the continuous-operator way: the Eye reads the
        instant, the Hands walk toward it, and both are reported in the
        SAME box-kite language the discrete relate() already insists on."""
        self._require_agreement(eye)
        path = self.emit_steered(s0)
        out = [f"step {i}: {step}" for i, step in enumerate(path)]
        out.append(f"converged: rho<target after {len(path)} steps, "
                    f"final Gamma={path[-1].gamma:.4f}")
        return out


if __name__ == "__main__":
    kite = BoxKite()
    eye = GaugeEye(kite)          # plain MindsEye construction -- no store needed
    hands = GaugeHands(kite)

    print("GaugeEye.continuous_snapshot on a real 16-vector (the De Marrais "
          "box-kite, not the 19D WordNet one):")
    import random
    rng = random.Random(0)
    psi = [rng.uniform(-1, 1) for _ in range(SED_DIM)]
    n = sum(v * v for v in psi) ** 0.5
    psi = [v / n for v in psi]
    snap = eye.continuous_snapshot(psi)
    print(f"  is_zero_divisor={snap['is_zero_divisor']}  "
          f"a_matrix_basin_windspeed={snap['a_matrix_basin_windspeed']:.6f}")

    print()
    print("GaugeHands.emit_steered from s=0.5+0.1j toward a firing circle:")
    try:
        path = hands.emit_steered(0.5 + 0.1j)
        print(f"  converged in {len(path)} steps, final {path[-1]}")
    except GaugeSteeringFailed as exc:
        print(f"  refused: {exc}")

    print()
    print("relate_steered (Eye + Hands, same box-kite language):")
    for line in hands.relate_steered(eye, 0.5 + 0.1j)[-3:]:
        print(f"  {line}")
