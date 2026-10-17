"""
Fast tests for tools/taoist_physics.py System3 (the whole + two dot-weights, planar).
The chaos measurement is slow and lives in tools/taoist_lyapunov.py (run on demand).
Run: python3 tests/test_taoist_physics.py   (or pytest)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
os.environ.setdefault("MPLBACKEND", "Agg")
import taoist_physics as P  # noqa: E402


def _path(T=40, **kw):
    s = P.System3(**kw)
    return s, P.run3(s, T, dt=0.01, every=5)


def test_healthy_is_exact_rigid_rotation_and_the_whole_stays_on_the_barycentre():
    s, path = _path()
    assert np.abs(path).max() < 1e-9
    assert abs(s.om[0] - P.OMEGA0) < 1e-9 and abs(s.om[1] - P.OMEGA0) < 1e-9
    assert np.linalg.norm(s.gap()) < 1e-7


def test_shapes_that_match_leave_the_centre_alone():
    _, path = _path(delta_y=0.3, delta_w=0.3)
    assert np.abs(path).max() < 1e-9               # equal dents on both halves: point-symmetric


def test_one_edge_damaged_gives_an_epicycle_that_stays_bounded():
    _, path = _path(T=80, delta_y=0.3)
    r = np.linalg.norm(path, axis=1)
    assert r.max() > 5e-3 and r.max() < 0.3


def test_the_barycentre_is_conserved_when_nothing_pushes_from_outside():
    s = P.System3(delta_y=0.3, rho_w=0.7, cmd_y=1.6, cmd_w=1.0)
    M = P.M0 + sum(s.m)

    def centre_of_mass(sy):
        return (P.M0 * sy.xc + sum(sy.m[i] * sy.x[i] for i in range(2))) / M

    def momentum(sy):
        return P.M0 * sy.vc + sum(sy.m[i] * sy.v[i] for i in range(2))
    p0 = momentum(s)
    for _ in range(3000):
        s.step(0.01)
    assert np.linalg.norm(momentum(s) - p0) < 1e-9        # internal forces only


def test_a_pinned_centre_stays_put():
    s = P.System3(delta_y=0.3, rho_w=0.7, pin=True)
    for _ in range(500):
        s.step(0.01)
    assert np.linalg.norm(s.xc) == 0.0


def test_a_distorted_seam_opens_a_gap():
    s, _ = _path(T=20, rho_w=0.6, cmd_y=1.7, cmd_w=1.0, k_g=0.5, c_g=0.01)
    assert np.linalg.norm(s.gap()) > 1e-2


if __name__ == "__main__":
    n = 0
    for k, v in sorted(globals().items()):
        if k.startswith("test_"):
            v(); n += 1; print("ok ", k)
    print(n, "passed")
