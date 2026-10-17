"""
Tests for tools/lemniscate_monitor.py Taoist mode: the yin-yang geometry, the barycentre,
and the two behaviours (locked circle / drifting epicycle).  Pure maths, no display.
Run: python3 tests/test_taoist_geometry.py   (or pytest)
"""
import cmath
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
os.environ.setdefault("MPLBACKEND", "Agg")
import lemniscate_monitor as L  # noqa: E402


def _c(name, delta=0.0):
    a, x, y = L.poly_ac(L.half_poly(name, delta))
    return a, complex(x, y)


def test_halves_have_half_the_disc_each():
    for name in ("yang", "yin"):
        a, _ = _c(name)
        assert abs(a - math.pi / 2) < 2e-3


def test_centroids_are_opposite_at_the_measured_place():
    _, cy = _c("yang")
    _, cw = _c("yin")
    assert abs(cy + cw) < 1e-9                                  # point symmetry
    assert abs(abs(cy.real) - 1 / math.pi) < 2e-3               # 0.3183 R
    assert abs(abs(cy.imag) - 0.25) < 2e-3                      # 0.25 R


def test_healthy_barycentre_is_the_centre_at_any_phase():
    t = L.Tao()
    for th in (0.0, 0.7, 2.9):
        t.th = {"yang": th, "yin": th}
        assert abs(t.barycentre()) < 1e-9


def test_closed_form_for_scaled_halves():
    _, c = _c("yang")
    for sy, sw in ((0.7, 1.0), (1.0, 0.7), (0.5, 1.0), (0.7, 0.7)):
        a_y, x_y, y_y = L.poly_ac(L._rot(L.half_poly("yang"), 0, sy))
        a_w, x_w, y_w = L.poly_ac(L._rot(L.half_poly("yin"), 0, sw))
        b = (a_y * complex(x_y, y_y) + a_w * complex(x_w, y_w)) / (a_y + a_w)
        f = c * (sy ** 3 - sw ** 3) / (sy ** 2 + sw ** 2)
        assert abs(b - f) < 2e-3


def test_misaligned_halves_give_a_barycentre_of_c_sin_half_psi():
    t = L.Tao()
    _, c = _c("yang")
    for psi in (0.3, 1.0, 2.0):
        t.th = {"yang": psi, "yin": 0.0}
        assert abs(abs(t.barycentre()) - abs(c) * abs(math.sin(psi / 2))) < 2e-3


def test_a_dent_on_one_half_moves_the_barycentre_and_rigid_spin_keeps_it_a_circle():
    t = L.Tao()
    t.delta = {"yang": 0.3, "yin": 0.0}
    radii = []
    for th in (0.0, 1.0, 2.0, 4.0):
        t.th = {"yang": th, "yin": th}
        radii.append(abs(t.barycentre()))
    assert min(radii) > 1e-3
    assert max(radii) - min(radii) < 1e-9


def test_equal_damage_is_centred_and_smaller():
    t = L.Tao()
    for _ in range(300):
        t.step(0.6, 0.6, 0.04)
    assert t.k < 0.7 and abs(t.b) < 1e-6 and t.regime == "intact"


def test_intact_scores_stay_a_point():
    t = L.Tao()
    for _ in range(300):
        t.step(1.0, 1.0, 0.04)
    assert max(abs(p) for p in t.trace) < 1e-9


def _run(S, G, n=1500):
    t = L.Tao()
    for _ in range(n):
        t.step(S, G, 0.04)
    r = [abs(p) for p in list(t.trace)[-300:]]
    return t, max(r) - min(r)


def test_small_relative_damage_locks_and_the_path_is_a_circle():
    t, spread = _run(0.9, 0.5)
    assert t.regime == "locked" and spread < 1e-3


def test_large_relative_damage_drifts_and_the_path_is_an_epicycle():
    t, spread = _run(0.9, 0.2)
    assert t.regime == "drifting" and spread > 1e-2


def test_the_two_cases_differ_only_because_the_constants_are_asymmetric():
    ty, sy = _run(0.9, 0.2)          # yang (active) more damaged
    tw, sw = _run(0.2, 0.9)          # yin (passive) more damaged, same |rel|
    assert (ty.regime, tw.regime) == ("drifting", "locked")
    saved = (dict(L.KAPPA), dict(L.DEFORM))
    try:
        L.KAPPA.update(yang=1.0, yin=1.0); L.DEFORM.update(yang=0.5, yin=0.5)
        ty, _ = _run(0.9, 0.2); tw, _ = _run(0.2, 0.9)
        assert ty.regime == tw.regime          # symmetric constants: congruent behaviour
    finally:
        L.KAPPA.update(saved[0]); L.DEFORM.update(saved[1])


def test_normal_mode_regions():
    assert L.region(0.95, 0.95) == "intact"
    assert L.region(0.9, 0.5) == "Broca-type"
    assert L.region(0.2, 0.9) == "Wernicke-type"
    assert L.region(0.1, 0.1) == "both-deficit"


if __name__ == "__main__":
    n = 0
    for k, v in sorted(globals().items()):
        if k.startswith("test_"):
            v(); n += 1; print("ok ", k)
    print(n, "passed")
