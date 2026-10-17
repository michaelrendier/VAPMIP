#!/usr/bin/env python3
"""scaled_mind_eye_boxkite_kernel_monad.py — running a boxkite.

Cody, 2026-09-24: "how do i use 0_RB + L_(I|O) + UFT (discrete words,
continuous context/continuity) to 'run a boxkite'... the UFT is only there
by nature of being the thing that defines the split between the two
readings... now the disambiguation of kernel means less, since I just gave
it a structural constant -- the thing both languages speak."

Reuse discipline, same as 19D_boxkite_context_monad.py before it: nothing
here reimplements chart reading, steering, or the fixed-point measure --
all three already exist, tested, in rotary_rerun_monad.py,
19D_boxkite_context_monad.py, and ValaQuenta/modules/box_kite/maths.py.
This file adds exactly one thing: the HUB-ANCHORED FIBER SEQUENCE those
pieces were missing.

THE THREE PIECES, IN THE ROLES THIS SESSION DERIVED FOR THEM
==============================================================

  0_RB     the HUB. e_0/e_8, the one fixed point shared by all seven
           otherwise-disconnected box-kite charts (bk.fixed_point_gluing,
           bk.e0_is_outside -- both ESTABLISHED, checked not asserted:
           e_0 is not a PG(3,2) point, is in no Assessor, its associator
           always vanishes). bk.fixed_point_weight(psi) is the STRUCTURAL
           CONSTANT itself -- psi[0]^2/|psi|^2, computed the same way
           regardless of which chart or which reading is in use. THIS is
           "the thing both languages speak": the discrete and continuous
           readings below disagree about almost everything except what
           this one number means.

  L_(I|O)  the FIBER. One throw from the hub OUT to a specific chart (one
           strut, one grammatical/semantic role) and back. throw_fiber()
           below IS this operation, built directly from
           bk.fixed_point_weight -- depart the hub with `depth` energy
           committed to one Assessor, land, read, and because every throw
           reconstructs psi FROM THE HUB rather than from the previous
           landing point, "return to the hub between fibers" is
           structurally enforced, not merely asserted.

  UFT      the DIAL. GaugeEye.continuous_snapshot() already reads BOTH
           readings off the same landed instant: is_zero_divisor
           (discrete -- this specific word, this Assessor, box-kite-
           native) and a_matrix_basin_windspeed (continuous -- the
           grammatical shape holding that word in place). That pair,
           read together, IS the UFT dial.

           Deliberately NOT h_rb_hat's sigma_zeta facet table
           (sigma_to_theory, sigma=0/half/1/2/real-only). sigma_self here
           is the box-kite's own native quantity (p_red/(p_red+p_blue)),
           a DIFFERENT sigma than h_rb_hat's Re(s) coupling exponent --
           see Ainulindale/wiki/123_sigma_rb_mass_gap_calibration.md,
           "THREE SIGMAS -- do not conflate them". Feeding one into the
           other's facet classifier would be exactly the conflation that
           page exists to prevent, so this file doesn't do it.

RUNNING A BOXKITE = repeat, once per grammatical slot needed: depart the
hub, throw one fiber via L_(I|O), read the UFT dial at the landing point,
come back to the hub, throw the next fiber. Never hold two charts at
once -- the geometry itself will not allow it (bk.glued_graph: zero
cross-strut edges; the charts touch only at the hub).
"""
from __future__ import annotations

import math
import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotary_rerun_monad import BoxKite, MindsEye, PapersHands, SED_DIM
from importlib import import_module

_19d_gauge = import_module("19D_boxkite_context_monad")
GaugeEye = _19d_gauge.GaugeEye
GaugeHands = _19d_gauge.GaugeHands
GaugeStep = _19d_gauge.GaugeStep
GaugeSteeringFailed = _19d_gauge.GaugeSteeringFailed

from ValaQuenta.modules.box_kite import maths as bk


# ═══════════════════════════════════════════════════════════════════════════
#  THE REPEATED CHANNEL — Aule is the Root of Systems Analysis Harness
# ═══════════════════════════════════════════════════════════════════════════
#
# Cody, 2026-09-24: "any system monitoring software belongs to Aule face in
# Ptolemy Desktop... repeated channel in the harness... complimentary
# functions for the monad via harness... Aule is the Root of Systems
# Analysis Harness."
#
# This is the pattern, not a one-off: a NAMED channel string
# ("mind_eye_boxkite"), published through Aule's own stream_event() -- the
# same indirection every other module already uses ("monad > harness > chat
# window < passive reportings", project_ptolemy_desktop memory) -- never a
# direct reach into a face. Defensive because VAPMIP and PtolemyDesktop are
# separate repos: this file must work standalone with Aule absent, the same
# no-op-if-not-running contract stream_event() already documents for every
# other caller.

_PTOLEMY_DESKTOP = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PtolemyDesktop")
if os.path.isdir(_PTOLEMY_DESKTOP) and _PTOLEMY_DESKTOP not in sys.path:
    sys.path.insert(0, _PTOLEMY_DESKTOP)

try:
    from Aule.aule import stream_event as _stream_event
except Exception:                                    # noqa: BLE001
    _stream_event = None

AULE_CHANNEL = "mind_eye_boxkite"


def _aule_channel(event_type: str, payload: Dict[str, Any]) -> None:
    """The repeated channel, reusable verbatim by the next monad: swap
    AULE_CHANNEL's value, keep everything else. Silent no-op if Aule isn't
    on the path or isn't running -- never a hard dependency."""
    if _stream_event is None:
        return
    try:
        _stream_event(AULE_CHANNEL, event_type, payload)
    except Exception:                                # noqa: BLE001
        pass


# ═══════════════════════════════════════════════════════════════════════════
#  THE HUB — 0_RB, pure e_0
# ═══════════════════════════════════════════════════════════════════════════

HUB_PSI: List[float] = [1.0] + [0.0] * (SED_DIM - 1)
# bk.fixed_point_weight(HUB_PSI) == 1.0 exactly: all energy at e_0, none in
# any Assessor -- the hub itself is not a point ANY chart can claim
# (bk.e0_is_outside), which is exactly why it can be shared by all seven.


@dataclass
class FiberThrow:
    """One L_(I|O) crossing: hub -> one chart -> the UFT dial's reading."""
    strut:                int
    depth:                float
    assessor:             Tuple[int, int]
    psi:                  List[float]
    fixed_point_weight:   float          # 0_RB's own structural constant, at landing
    is_zero_divisor:      Any            # discrete reading
    a_matrix_basin_windspeed: float      # continuous reading
    nearest_assessor:     Any
    sigma_self:           float          # box-kite-native sigma, NOT sigma_zeta
    gamma_companion:      Optional[GaugeStep]  # optional L_(I|O)-style compass walk

    def __repr__(self) -> str:
        return (f"FiberThrow(strut={self.strut}, depth={self.depth:.3f}, "
                f"hub_weight={self.fixed_point_weight:.3f}, "
                f"ZD={self.is_zero_divisor}, "
                f"windspeed={self.a_matrix_basin_windspeed:+.6f})")


# ═══════════════════════════════════════════════════════════════════════════
#  THE KERNEL — 0_RB + L_(I|O) + UFT, run together
# ═══════════════════════════════════════════════════════════════════════════

class MindEyeBoxKiteKernel:
    """Runs a boxkite: one hub-anchored fiber per grammatical slot.

    Composes GaugeEye (the UFT dial) and GaugeHands (the optional
    Gamma-curvature companion walk) over ONE shared BoxKite, exactly the
    binding contract MindsEye/PapersHands already enforce.
    """

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        self.kite = kite or BoxKite()
        self.eye = GaugeEye(self.kite)
        self.hands = GaugeHands(self.kite)

    def hub_report(self) -> Dict[str, Any]:
        """Confirm the hub is real before using it -- reused, not asserted."""
        report = {
            "e0_is_outside": bk.e0_is_outside(),
            "fixed_point_gluing": bk.fixed_point_gluing(),
            "hub_fixed_point_weight": bk.fixed_point_weight(HUB_PSI),
        }
        _aule_channel("hub_confirmed", {
            "hub_fixed_point_weight": report["hub_fixed_point_weight"],
            "e0_is_outside_the_geometry":
                report["e0_is_outside"]["e0_is_outside_the_geometry"],
        })
        return report

    def throw_fiber(self, strut: int, depth: float = 0.6,
                     gamma_companion: bool = True) -> FiberThrow:
        """One L_(I|O) crossing from the hub to `strut`'s Assessor.

        `depth` in [0,1] is how much of the hub's energy this throw
        commits away from e_0. psi is built fresh from HUB_PSI every
        call -- there is no path back to construct, because the throw
        never left a residue at the previous landing point to begin
        with. That IS "return to the hub between fibers."
        """
        if not (0.0 <= depth <= 1.0):
            raise ValueError(f"depth must be in [0,1], got {depth}")
        a, b = self.kite.kite(strut)[0]      # first Assessor of this chart
        psi = [0.0] * SED_DIM
        psi[0] = math.sqrt(max(0.0, 1.0 - depth * depth))
        psi[a] = depth / math.sqrt(2.0)
        psi[b] = depth / math.sqrt(2.0)

        snap = self.eye.continuous_snapshot(psi)
        fpw = bk.fixed_point_weight(psi)

        gamma = None
        if gamma_companion:
            s0 = complex(strut / 7.0, 0.15)
            try:
                path = self.hands.emit_steered(s0, max_steps=80)
                gamma = path[-1]
            except GaugeSteeringFailed:
                gamma = None

        _aule_channel("fiber_thrown", {
            "strut": strut, "depth": depth, "assessor": [a, b],
            "fixed_point_weight": fpw,
            "is_zero_divisor": snap["is_zero_divisor"],
            "a_matrix_basin_windspeed": snap["a_matrix_basin_windspeed"],
        })

        return FiberThrow(
            strut=strut, depth=depth, assessor=(a, b), psi=psi,
            fixed_point_weight=fpw,
            is_zero_divisor=snap["is_zero_divisor"],
            a_matrix_basin_windspeed=snap["a_matrix_basin_windspeed"],
            nearest_assessor=snap["nearest_assessor"],
            sigma_self=snap["sigma_self"],
            gamma_companion=gamma,
        )

    def run_boxkite(self, plan: List[Tuple[int, float]],
                     gamma_companion: bool = True) -> List[FiberThrow]:
        """The whole sentence: one hub-anchored fiber per (strut, depth)
        in `plan`, in order. Each throw is independent of the last --
        the kernel never holds two charts at once."""
        return [self.throw_fiber(s, d, gamma_companion) for s, d in plan]


if __name__ == "__main__":
    kernel = MindEyeBoxKiteKernel()

    print("HUB — confirming 0_RB is real, not asserted:")
    hub = kernel.hub_report()
    print(f"  e0_is_outside_the_geometry = "
          f"{hub['e0_is_outside']['e0_is_outside_the_geometry']}")
    print(f"  fixed_point_gluing.reading = "
          f"{hub['fixed_point_gluing']['reading']}")
    print(f"  hub fixed_point_weight     = {hub['hub_fixed_point_weight']:.6f}")

    print()
    print("RUNNING A BOXKITE — one fiber per strut, 1..7, depth=0.6:")
    plan = [(s, 0.6) for s in kernel.kite.struts]
    throws = kernel.run_boxkite(plan)
    for t in throws:
        print(f"  {t}")

    print()
    print("Structural constant check -- fixed_point_weight should read "
          "1-depth^2 = 0.64 at every landing, regardless of strut or chart:")
    for t in throws:
        print(f"  strut {t.strut}: fixed_point_weight={t.fixed_point_weight:.6f}")
