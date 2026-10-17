#!/usr/bin/env python3
"""taoist_physics.py — rigid-body physics behind the Taoist mode of lemniscate_monitor.py.

Two bodies (the yang half and the yin half) share one pivot O at the centre of the
yin-yang.  Each is a flat lump of mass sampled from its outline (the same outline
`lemniscate_monitor.half_poly` draws), spun by a "dot" about the common axis z.

Two different sources of off-centre motion, kept separate on purpose:

  EDGE      Damage on the OUTSIDE of a half dents its outer arc and piles the mass on that
            side: the dent removes area and the half's plane tilts toward the dent
            (z = LIFT·delta·(x cos a + y sin a)).  The tilt gives the half a product of
            inertia, so z is not a principal axis, and its barycentre leaves the axis.
            Locked to the other half (rigid seam) this is one torque-free-about-the-pivot
            rigid body (Euler–Poinsot) driven about z: integrable, so the barycentre
            path is regular and periodic/quasi-periodic (the Greenland-ice case: one
            component of the tilt thrown off).

  MISMATCH  The two halves differ in density and in commanded spin rate (the dots drive
            the spin), and are joined by a seam torque
                τ_w = −K_SEAM·axial(R_yᵀR_w) − C_SEAM·(ω_w − ω_y),   τ_y = −τ_w
            where axial() is the vector of the antisymmetric part (|axial| = sin of the
            relative angle: the Kuramoto sin, in 3-D).  Two gyrostatic bodies with
            different inertia tensors, coupled through that nonlinear torque and driven
            at different rates, are not integrable; whether the barycentre path is
            chaotic is MEASURED by `lyapunov()` (Benettin, two nearby trajectories), not
            assumed.

Every constant is a [PARAM].  Units: outer radius 1, density 1, spin OMEGA0 ≈ 1.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OMEGA0 = 1.2          # common spin rad/s
GAMMA = 6.0           # drive stiffness: torque about z toward the commanded rate
LIFT = 1.2            # [PARAM] out-of-plane tilt of a half per unit dent (z slope)
THICK = 0.25          # [PARAM] slab thickness of each half
K_SEAM = 2.0          # [PARAM] seam spring (axial part of the relative rotation)
C_SEAM = 0.15         # [PARAM] seam damping on the relative angular velocity
C_TILT = 0.004        # [PARAM] weak damping of angular velocity off z
TILT0 = 0.05          # [PARAM] initial tilt of each spin axis (rad): the regular case then shows nutation
GRID = 56             # sample grid for mass moments
DENT_DIR = {'yang': math.pi, 'yin': 0.0}    # the half's outer side: yang left, yin right


def _inside(P, X, Y):
    from matplotlib.path import Path
    return Path(P).contains_points(np.column_stack([X.ravel(), Y.ravel()])).reshape(X.shape)


_GRID = None


def _grid():
    global _GRID
    if _GRID is None:
        xs = (np.arange(GRID) + 0.5) / GRID * 2 - 1
        X, Y = np.meshgrid(xs, xs)
        _GRID = (X, Y, (2.0 / GRID) ** 2)
    return _GRID


_CACHE = {}


def half_mass(name, delta, rho):
    """(mass, barycentre 3-vector, inertia 3x3 about O) of one half, body frame."""
    key = (name, round(delta, 4), round(rho, 4))
    if key in _CACHE:
        return _CACHE[key]
    import lemniscate_monitor as L
    X, Y, dA = _grid()
    m = _inside(L.half_poly(name, delta, 90), X, Y)
    x, y = X[m], Y[m]
    a = DENT_DIR[name]
    z = LIFT * delta * (x * math.cos(a) + y * math.sin(a))
    dm = rho * dA
    M = dm * len(x)
    if M <= 0:
        out = (0.0, np.zeros(3), np.eye(3) * 1e-9)
    else:
        r = np.column_stack([x, y, z])
        c = r.sum(axis=0) * dm / M
        I = np.zeros((3, 3))
        r2 = (r * r).sum(axis=1)
        I += dm * np.diag([r2.sum()] * 3) - dm * r.T @ r
        I[0, 0] += M * THICK ** 2 / 12.0
        I[1, 1] += M * THICK ** 2 / 12.0
        out = (M, c, I)
    _CACHE[key] = out
    return out


def _hat(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0.0]])


def _axial(Q):
    A = 0.5 * (Q - Q.T)
    return np.array([A[2, 1], A[0, 2], A[1, 0]])


def _orth(R):
    u, _, vt = np.linalg.svd(R)
    return u @ vt


class System:
    """Two driven rigid bodies, one pivot.  params: dict with
    delta_y, delta_w (outer-edge dents), rho_y, rho_w (densities), cmd_y, cmd_w (commanded
    spin rates), k_seam (default K_SEAM)."""

    def __init__(self, delta_y=0.0, delta_w=0.0, rho_y=1.0, rho_w=1.0,
                 cmd_y=OMEGA0, cmd_w=OMEGA0, k_seam=K_SEAM, c_seam=C_SEAM):
        self.k_seam, self.c_seam = k_seam, c_seam
        self.set_params(delta_y, delta_w, rho_y, rho_w, cmd_y, cmd_w)
        self.R = [np.eye(3), np.eye(3)]
        self.w = [np.array([TILT0 * OMEGA0, 0, OMEGA0]), np.array([0, TILT0 * OMEGA0, OMEGA0])]   # body frame
        self.t = 0.0

    def set_params(self, delta_y, delta_w, rho_y, rho_w, cmd_y, cmd_w):
        self.mass = []; self.c = []; self.I = []
        for name, d, r in (('yang', delta_y, rho_y), ('yin', delta_w, rho_w)):
            M, c, I = half_mass(name, d, r)
            self.mass.append(M); self.c.append(c); self.I.append(I)
        self.Iinv = [np.linalg.inv(I) for I in self.I]
        self.cmd = [cmd_y, cmd_w]

    # state <-> vector for RK4
    def _deriv(self, R, w):
        wl = [R[i] @ w[i] for i in range(2)]
        Q = R[0].T @ R[1]
        ax = R[0] @ _axial(Q)                        # lab-frame axis of the relative rotation
        tau_w = -self.k_seam * ax - self.c_seam * (wl[1] - wl[0])
        tau = [-tau_w, tau_w]
        dR, dw = [], []
        for i in range(2):
            zhat = R[i][2, :]                        # lab z expressed in body frame
            drive = GAMMA * (self.cmd[i] - wl[i][2]) * zhat
            t_body = R[i].T @ tau[i] + drive - C_TILT * (w[i] - (w[i] @ zhat) * zhat)
            Iw = self.I[i] @ w[i]
            dw.append(self.Iinv[i] @ (np.cross(Iw, w[i]) + t_body))
            dR.append(R[i] @ _hat(w[i]))
        return dR, dw

    def step(self, dt):
        R, w = self.R, self.w
        k1R, k1w = self._deriv(R, w)
        R2 = [R[i] + 0.5 * dt * k1R[i] for i in range(2)]; w2 = [w[i] + 0.5 * dt * k1w[i] for i in range(2)]
        k2R, k2w = self._deriv(R2, w2)
        R3 = [R[i] + 0.5 * dt * k2R[i] for i in range(2)]; w3 = [w[i] + 0.5 * dt * k2w[i] for i in range(2)]
        k3R, k3w = self._deriv(R3, w3)
        R4 = [R[i] + dt * k3R[i] for i in range(2)]; w4 = [w[i] + dt * k3w[i] for i in range(2)]
        k4R, k4w = self._deriv(R4, w4)
        for i in range(2):
            self.R[i] = _orth(R[i] + dt / 6 * (k1R[i] + 2 * k2R[i] + 2 * k3R[i] + k4R[i]))
            self.w[i] = w[i] + dt / 6 * (k1w[i] + 2 * k2w[i] + 2 * k3w[i] + k4w[i])
        self.t += dt

    def barycentre(self):
        """System barycentre relative to the pivot, lab frame (3-vector)."""
        tot = sum(self.mass[i] * (self.R[i] @ self.c[i]) for i in range(2))
        return tot / sum(self.mass)

    def yaw(self, i):
        return math.atan2(self.R[i][1, 0], self.R[i][0, 0])

    def state(self):
        return np.concatenate([self.R[0].ravel(), self.R[1].ravel(), self.w[0], self.w[1]])

    def load(self, v):
        self.R = [v[0:9].reshape(3, 3).copy(), v[9:18].reshape(3, 3).copy()]
        self.w = [v[18:21].copy(), v[21:24].copy()]


def run(sys_, T, dt=0.01, every=5):
    """Barycentre path (n,3) over T seconds."""
    out = []
    n = int(T / dt)
    for k in range(n):
        sys_.step(dt)
        if k % every == 0:
            out.append(sys_.barycentre())
    return np.array(out)


def lyapunov(make, T=400.0, dt=0.01, renorm=0.5, eps=1e-7, burn=40.0):
    """Largest Lyapunov exponent (Benettin) of the barycentre dynamics.  `make()` returns a
    fresh System.  Two copies, one perturbed by eps, renormalised every `renorm` seconds;
    the first `burn` seconds are discarded (the drive spins the bodies up)."""
    a = make(); b = make()
    for _ in range(int(burn / dt)):
        a.step(dt)
    b.load(a.state())
    rng = np.random.default_rng(3)
    d = rng.normal(size=24); d /= np.linalg.norm(d)
    v = a.state() + eps * d
    b.load(v)
    b.R = [_orth(r) for r in b.R]
    tot, n = 0.0, int((T - burn) / renorm)
    for _ in range(n):
        for _ in range(int(renorm / dt)):
            a.step(dt); b.step(dt)
        sa, sb = a.state(), b.state()
        dist = np.linalg.norm(sb - sa)
        tot += math.log(dist / eps)
        b.load(sa + (sb - sa) * (eps / dist))
        b.R = [_orth(r) for r in b.R]
    return tot / (n * renorm)


# ═══════════════════════════════════════════════════════════════════════════
# Three bodies (planar): the WHOLE (centre body) and the two weights.
#
# The whole is one object (mass M0) with its own motion; the two weights orbit it, each a
# deformable shape (mass, centre of mass and spin inertia taken from its outline), driven
# at its dot.  Nothing is pinned: no external force, so the system barycentre is fixed and
# the epicycle drawn is where the WHOLE sits relative to it.
#   anchor   central spring from the whole to each weight's centre of mass (rest length L0)
#   dots     each dot is the engine of its half: torque GAMMA·(cmd − ω) on the half
#   seam     a spring-damper between the two halves' S-centre points: a gap or an overlap
#            there is a force; K_G and C_G fall with seam damage
# Healthy (equal shapes, equal rates): exact rigid rotation, the whole stays on the
# barycentre.  Damage changes mass, centre of mass and inertia of a half (edge), and the
# seam; whether the result is regular or chaotic is measured with `lyapunov3()`.
# ═══════════════════════════════════════════════════════════════════════════
M0 = 1.0              # [PARAM] mass of the whole (centre body)
L0 = 0.1              # [PARAM] rest length of the anchor springs
K_G = 4.0             # [PARAM] seam spring stiffness at full health
C_G = 0.30            # [PARAM] seam damping at full health
C_A = 0.01            # [PARAM] anchor damping
_CACHE2 = {}


def half_mass2(name, delta, rho):
    """(mass, centre-of-mass 2-vector, spin inertia about it) of one half, polygon frame."""
    key = (name, round(delta, 4), round(rho, 4))
    if key in _CACHE2:
        return _CACHE2[key]
    import lemniscate_monitor as L
    X, Y, dA = _grid()
    m = _inside(L.half_poly(name, delta, 90), X, Y)
    x, y = X[m], Y[m]
    dm = rho * dA
    M = dm * len(x)
    c = np.array([x.mean(), y.mean()])
    J = dm * (((x - c[0]) ** 2 + (y - c[1]) ** 2).sum()) + M * 0.0
    out = (M, c, J)
    _CACHE2[key] = out
    return out


def _rot2(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]])


def _cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


class System3:
    """The whole + two weights.  See the block comment above."""

    def __init__(self, delta_y=0.0, delta_w=0.0, rho_y=1.0, rho_w=1.0,
                 cmd_y=OMEGA0, cmd_w=OMEGA0, k_g=K_G, c_g=C_G, pin=False):
        self.k_g, self.c_g, self.pin = k_g, c_g, pin       # pin: a static centre (regular, star-shaped)
        # springs sized once on the HEALTHY halves so the healthy state is exact rigid rotation
        self.K = []
        for name in ('yang', 'yin'):
            M, c, _ = half_mass2(name, 0.0, 1.0)
            r = float(np.linalg.norm(c))
            self.K.append(M * OMEGA0 ** 2 * r / (r - L0))
        self.set_params(delta_y, delta_w, rho_y, rho_w, cmd_y, cmd_w)
        self.xc = np.zeros(2); self.vc = np.zeros(2)
        self.x, self.v, self.th, self.om = [], [], [0.0, 0.0], [OMEGA0, OMEGA0]
        for name in ('yang', 'yin'):
            _, c, _ = half_mass2(name, 0.0, 1.0)
            self.x.append(c.copy())
            self.v.append(OMEGA0 * np.array([-c[1], c[0]]))
        self.t = 0.0

    def set_params(self, delta_y, delta_w, rho_y, rho_w, cmd_y, cmd_w):
        self.m, self.c, self.J = [], [], []
        for name, d, r in (('yang', delta_y, rho_y), ('yin', delta_w, rho_w)):
            M, c, J = half_mass2(name, d, r)
            self.m.append(M); self.c.append(c); self.J.append(J)
        self.cmd = [cmd_y, cmd_w]

    def _acc(self, xc, vc, x, v, th, om):
        n = [x[i] + _rot2(th[i]) @ (-self.c[i]) for i in range(2)]                 # S-centre points
        nv = [v[i] + om[i] * np.array([-(n[i] - x[i])[1], (n[i] - x[i])[0]]) for i in range(2)]
        Fs = -self.k_g * (n[0] - n[1]) - self.c_g * (nv[0] - nv[1])                # on yang
        ax, al, Fc_tot = [], [], np.zeros(2)
        for i in range(2):
            d = x[i] - xc
            r = float(np.linalg.norm(d)) + 1e-12
            u = d / r
            rv = float((v[i] - vc) @ u)
            Fc = -(self.K[i] * (r - L0) + C_A * rv) * u                            # on the weight
            Fc_tot += Fc
            Fseam = Fs if i == 0 else -Fs
            F = Fc + Fseam
            tau = _cross2(n[i] - x[i], Fseam) + GAMMA * (self.cmd[i] - om[i])
            ax.append(F / self.m[i]); al.append(tau / self.J[i])
        return -Fc_tot / M0, ax, al

    def _f(self, s):
        xc, vc, x, v, th, om = s
        ac, ax, al = self._acc(xc, vc, x, v, th, om)
        if self.pin:
            return (np.zeros(2), np.zeros(2), v, ax, om, al)
        return (vc, ac, v, ax, om, al)

    def step(self, dt):
        s0 = (self.xc, self.vc, self.x, self.v, self.th, self.om)

        def comb(base, k, h):
            return (base[0] + h * k[0], base[1] + h * k[1],
                    [base[2][i] + h * k[2][i] for i in range(2)], [base[3][i] + h * k[3][i] for i in range(2)],
                    [base[4][i] + h * k[4][i] for i in range(2)], [base[5][i] + h * k[5][i] for i in range(2)])
        k1 = self._f(s0)
        k2 = self._f(comb(s0, k1, dt / 2))
        k3 = self._f(comb(s0, k2, dt / 2))
        k4 = self._f(comb(s0, k3, dt))

        def avg(j, i=None):
            g = (lambda k: k[j]) if i is None else (lambda k: k[j][i])
            return (g(k1) + 2 * g(k2) + 2 * g(k3) + g(k4)) * dt / 6
        self.xc = self.xc + avg(0); self.vc = self.vc + avg(1)
        for i in range(2):
            self.x[i] = self.x[i] + avg(2, i); self.v[i] = self.v[i] + avg(3, i)
            self.th[i] += avg(4, i); self.om[i] += avg(5, i)
        self.t += dt

    def barycentre(self):
        """The whole's centre relative to the system barycentre (the epicycle), 2-vector."""
        M = M0 + sum(self.m)
        B = (M0 * self.xc + sum(self.m[i] * self.x[i] for i in range(2))) / M
        return self.xc - B

    def gap(self):
        """Separation of the two halves' S-centre points (the seam gap), 2-vector."""
        n = [self.x[i] + _rot2(self.th[i]) @ (-self.c[i]) for i in range(2)]
        return n[0] - n[1]

    def yaw(self, i):
        return self.th[i]

    def to_lab(self, i, pts):
        """Polygon-frame points of half i -> lab frame."""
        R = _rot2(self.th[i])
        return [tuple(self.x[i] + R @ (np.array(p) - self.c[i])) for p in pts]

    def state(self):
        return np.concatenate([self.xc, self.vc, self.x[0], self.v[0], [self.th[0], self.om[0]],
                               self.x[1], self.v[1], [self.th[1], self.om[1]]])

    def load(self, q):
        self.xc, self.vc = q[0:2].copy(), q[2:4].copy()
        self.x = [q[4:6].copy(), q[10:12].copy()]
        self.v = [q[6:8].copy(), q[12:14].copy()]
        self.th = [float(q[8]), float(q[14])]
        self.om = [float(q[9]), float(q[15])]


def run3(sys_, T, dt=0.01, every=5):
    out = []
    for k in range(int(T / dt)):
        sys_.step(dt)
        if k % every == 0:
            out.append(sys_.barycentre())
    return np.array(out)


def lyapunov3(make, T=300.0, dt=0.01, renorm=1.0, eps=1e-7, burn=30.0):
    a, b = make(), make()
    for _ in range(int(burn / dt)):
        a.step(dt)
    rng = np.random.default_rng(5)
    d = rng.normal(size=16); d /= np.linalg.norm(d)
    b.load(a.state() + eps * d)
    tot, n = 0.0, int((T - burn) / renorm)
    for _ in range(n):
        for _ in range(int(renorm / dt)):
            a.step(dt); b.step(dt)
        sa, sb = a.state(), b.state()
        dist = np.linalg.norm(sb - sa)
        tot += math.log(dist / eps)
        b.load(sa + (sb - sa) * (eps / dist))
    return tot / (n * renorm)
