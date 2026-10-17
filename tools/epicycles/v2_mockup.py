#!/usr/bin/env python3
"""v2_mockup.py — the Taoist-mode epicycles as a simple KINEMATIC mockup (VERSION 2, current).

Written 2026-10-17 after Cody's corrections.  No rigid-body physics: every line here is a construction
that can be rebuilt in GeoGebra (points, circles, rotations, sliders, a parametric curve).  The matching
GeoGebra command list is v2_mockup.ggb.txt.  Output: docs/figures/epicycles/v2_mockup.svg

The picture (Cody's words, 2026-10-17)
  * The Whole is the yin-yang.  It SPINS about the centre, clockwise or anti-clockwise: one bit, SIGN (sigma).
  * The two dots are Broca (the black dot, in the white/yang half) and Wernicke (the white dot, in the
    black/yin half).  They do NOT spin; they SWING about the centre like pendulum bobs, in relation to
    the spinning whole and to each other.
  * A dot's DISPLACEMENT (arm length change, ADD) or SIZE (SCALE) changes its swing period, as gravity
    would, and deforms the seam edge: the two halves stop meeting (a gap or an overlap).
  * The centre point always draws the output: where the Whole's centre sits relative to the barycentre.
    Matched halves: nothing moves.  Mismatched edges: regular, periodic epicycles.  A distorted seam:
    two nearly independent motions around the centre.
  * The two comparisons always run together: dots LOCKED in step (one shared swing, the Huygens limit:
    regular, star-shaped) and dots INDEPENDENT but coupled through the seam (each swings at its own
    period; a nonlinear seam coupling).

Construction (complex plane, outer radius 1; a, l, s, d, delta, psi are the per-dot quantities)
    Theta(t)   = sigma * OMEGA * t                              the Whole's spin angle
    a_B, a_W   = +90 deg, -90 deg                               rest angles of the dots (1/4 and 3/4 of the S-axis)
    l_i        = L0 + d_i                                       arm length  (d_i: ADD, the displacement)
    s_i                                                         size        (SCALE)
    omega_i    = OMEGA_S / sqrt((l_i / L0) * s_i)               swing rate  (pendulum: longer / bigger = slower)
    psi_i(t)                                                    swing angle about the rest direction
    alpha_i    = Theta + a_i + psi_i                            direction of the dot's arm
    D_i        = l_i * exp(i alpha_i)                           the dot
    m_i        = s_i^2 * area(delta_i) / (pi/2)                 mass of the half (delta_i: outer-edge dent)
    CM_i       = D_i + s_i * exp(i (alpha_i - a_i)) * e_i(delta_i)   the half's centre of mass
                 e_i = (centroid of the dented half) - (its dot), in the half's own frame
    OUTPUT(t)  = - sum(m_i CM_i) / (M0 + sum m_i)               the centre point, relative to the barycentre
  locked column:       psi_B = psi_W = PSI0 cos(mean(omega) t)
  independent column:  psi_i'' = -omega_i^2 sin psi_i - KAPPA sin(psi_i - psi_j)      (seam coupling)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))                      # tools/
os.environ.setdefault("MPLBACKEND", "Agg")
import lemniscate_monitor as L  # noqa: E402  (half_poly, poly_ac: the outlines)

SCRIPT = os.path.basename(__file__)
VERSION = "v2 (superseded by v3)"
OMEGA = 1.0         # [PARAM] the Whole's spin
OMEGA_S = 1.3       # [PARAM] swing rate of an undisturbed dot
L0 = 0.5            # arm length of an undisturbed dot (the dot sits at 1/4, 3/4 of the diameter)
PSI0 = 0.8          # [PARAM] release angle of the swing, rad
KAPPA = 0.25        # [PARAM] seam coupling of the independent column
M0 = np.pi / 2      # [PARAM] mass of the Whole (the centre body), one half's worth
DOT = {'B': (0.0, 0.5), 'W': (0.0, -0.5)}
REST = {'B': np.pi / 2, 'W': -np.pi / 2}
HALF = {'B': 'yang', 'W': 'yin'}          # Broca = the white half (black dot), Wernicke = the black half (white dot)

# name, dB, dW (ADD), sB, sW (SCALE), deltaB, deltaW (edge dents), sigma (SIGN)
CASES = [
    ("healthy: the halves match",                         0.00, 0.00, 1.00, 1.00, 0.0, 0.0, +1),
    ("matched edges (both halves dented)",                0.00, 0.00, 1.00, 1.00, 0.3, 0.3, +1),
    ("Broca dot displaced (ADD)",                         0.08, 0.00, 1.00, 1.00, 0.0, 0.0, +1),
    ("Broca dot resized (SCALE)",                         0.00, 0.00, 1.15, 1.00, 0.0, 0.0, +1),
    ("Broca edge dented",                                 0.00, 0.00, 1.00, 1.00, 0.3, 0.0, +1),
    ("displaced + resized, spin right",                   0.08, 0.00, 1.00, 1.15, 0.0, 0.0, +1),
    ("displaced + resized, spin LEFT (SIGN)",             0.08, 0.00, 1.00, 1.15, 0.0, 0.0, -1),
    ("everything: displaced, resized, dented, both dots", 0.08, -0.05, 1.15, 0.95, 0.3, 0.1, +1),
]

_CACHE = {}


def half_geometry(name, delta):
    """(area/(pi/2), e) of a half: e = centroid - dot, in the half's own frame, as a complex number."""
    key = (name, round(delta, 4))
    if key not in _CACHE:
        a, cx, cy = L.poly_ac(L.half_poly(name, delta))
        dot = DOT['B'] if name == 'yang' else DOT['W']
        _CACHE[key] = (a / (np.pi / 2), complex(cx - dot[0], cy - dot[1]))
    return _CACHE[key]


def rates(case):
    _, dB, dW, sB, sW, *_ = case
    return (OMEGA_S / np.sqrt((L0 + dB) / L0 * sB), OMEGA_S / np.sqrt((L0 + dW) / L0 * sW))


def swings(case, t, coupled):
    """psi_B(t), psi_W(t) over the time array t."""
    wB, wW = rates(case)
    if not coupled:
        psi = PSI0 * np.cos(0.5 * (wB + wW) * t)
        return psi, psi
    dt = t[1] - t[0]
    x = np.array([PSI0, PSI0, 0.0, 0.0])

    def f(x):
        return np.array([x[2], x[3], -wB ** 2 * np.sin(x[0]) - KAPPA * np.sin(x[0] - x[1]),
                         -wW ** 2 * np.sin(x[1]) - KAPPA * np.sin(x[1] - x[0])])
    out = np.empty((len(t), 2))
    for k in range(len(t)):
        out[k] = x[:2]
        k1 = f(x); k2 = f(x + dt / 2 * k1); k3 = f(x + dt / 2 * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return out[:, 0], out[:, 1]


def output(case, T=240.0, dt=0.04, coupled=False):
    """The centre point's path (complex array) and the final configuration for the icon."""
    name, dB, dW, sB, sW, eB, eW, sigma = case
    t = np.arange(0.0, T, dt)
    psi = {'B': None, 'W': None}
    psi['B'], psi['W'] = swings(case, t, coupled)
    num = 0j
    den = M0
    par = {'B': (dB, sB, eB), 'W': (dW, sW, eW)}
    for k in ('B', 'W'):
        d, s, e = par[k]
        area, ev = half_geometry(HALF[k], e)
        m = s * s * area
        alpha = sigma * OMEGA * t + REST[k] + psi[k]
        D = (L0 + d) * np.exp(1j * alpha)
        cm = D + s * np.exp(1j * (alpha - REST[k])) * ev
        num = num - m * cm
        den += m
    return num / den, psi


def icon(case, psi0=None):
    """Polygons of the two halves at t = 0 (spin 0), each carried by its own dot: the seam gap/overlap."""
    name, dB, dW, sB, sW, eB, eW, sigma = case
    polys = []
    for k, (d, s, e) in (('B', (dB, sB, eB)), ('W', (dW, sW, eW))):
        ps = PSI0 if psi0 is None else psi0
        alpha = REST[k] + ps
        Dpt = (L0 + d) * np.exp(1j * alpha)
        rot = np.exp(1j * ps)
        dotp = complex(*DOT[k])
        pts = [Dpt + rot * s * (complex(x, y) - dotp) for x, y in L.half_poly(HALF[k], e, 60)]
        polys.append((k, pts, Dpt))
    return polys


def svg(results, T):
    cw, ch, left, top = 290, 230, 330, 74
    W, H = left + 2 * cw + 20, top + len(CASES) * ch + 20
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="14" y="26" font-size="17" font-weight="bold">Taoist mode: the epicycles, kinematic mockup ({T:g} s)</text>',
         f'<text x="{W - 14}" y="26" font-size="12" text-anchor="end" fill="#8e44ad">script: {SCRIPT} ({VERSION})</text>',
         '<text x="14" y="46" font-size="11" fill="#444">The Whole spins; the two dots (Broca black, Wernicke white) swing; the centre point draws the output '
         '(its offset from the barycentre). Each cell has its own scale; the half-extent is in units of R.</text>',
         f'<text x="{left + cw / 2}" y="66" font-size="13" text-anchor="middle" fill="#2471a3">dots locked in step</text>',
         f'<text x="{left + cw * 1.5}" y="66" font-size="13" text-anchor="middle" fill="#c0392b">dots independent, seam-coupled</text>']
    for r, case in enumerate(CASES):
        name, dB, dW, sB, sW, eB, eW, sigma = case
        y0 = top + r * ch
        o.append(f'<text x="14" y="{y0 + 20}" font-size="12.5" font-weight="bold">{name}</text>')
        o.append(f'<text x="14" y="{y0 + 37}" font-size="10.5" fill="#555">ADD d: B {dB:+.2f} W {dW:+.2f}   SCALE s: B {sB:.2f} W {sW:.2f}</text>')
        o.append(f'<text x="14" y="{y0 + 52}" font-size="10.5" fill="#555">edge dents: B {eB:.1f} W {eW:.1f}   SIGN: spin {"right" if sigma > 0 else "LEFT"}</text>')
        o.append(f'<line x1="10" y1="{y0 + ch - 6}" x2="{W - 10}" y2="{y0 + ch - 6}" stroke="#ddd"/>')
        # the icon: the two halves at t=0, each carried by its own dot
        ic_cx, ic_cy, sc_i = 80, y0 + 135, 62
        o.append(f'<circle cx="{ic_cx}" cy="{ic_cy}" r="{sc_i}" fill="none" stroke="#ccc" stroke-dasharray="2 3"/>')
        for k, pts, Dpt in icon(case)[::-1]:
            fill = '#ffffff' if k == 'B' else '#1a1a1a'
            d = "M" + " L".join(f"{ic_cx + p.real * sc_i:.1f},{ic_cy - p.imag * sc_i:.1f}" for p in pts) + "Z"
            o.append(f'<path d="{d}" fill="{fill}" fill-opacity="0.82" stroke="#444" stroke-width="0.8"/>')
        for k, pts, Dpt in icon(case):
            dotfill = '#000000' if k == 'B' else '#ffffff'
            o.append(f'<circle cx="{ic_cx + Dpt.real * sc_i:.1f}" cy="{ic_cy - Dpt.imag * sc_i:.1f}" r="{5 * sc_i / 38 * 2.2:.1f}" fill="{dotfill}" stroke="#000" stroke-width="0.8"/>')
        for c, colour in enumerate(('#2471a3', '#c0392b')):
            z = results[(r, c)]
            ext = float(max(np.abs(z.real).max(), np.abs(z.imag).max(), 1e-12))
            cx, cy = left + c * cw + cw / 2, y0 + ch / 2 - 4
            o.append(f'<line x1="{cx - cw / 2 + 20}" y1="{cy}" x2="{cx + cw / 2 - 20}" y2="{cy}" stroke="#eee"/>')
            o.append(f'<line x1="{cx}" y1="{cy - ch / 2 + 22}" x2="{cx}" y2="{cy + ch / 2 - 30}" stroke="#eee"/>')
            if ext < 1e-6:
                o.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{colour}"/>')
                o.append(f'<text x="{cx}" y="{y0 + ch - 12}" font-size="11" text-anchor="middle" fill="#555">a point (extent &lt; 1e-6 R)</text>')
                continue
            sc = (ch / 2 - 24) / ext
            d = "M" + " L".join(f"{cx + p.real * sc:.1f},{cy - p.imag * sc:.1f}" for p in z[::2])
            o.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="0.7" stroke-opacity="0.85"/>')
            o.append(f'<circle cx="{cx + z[-1].real * sc:.1f}" cy="{cy - z[-1].imag * sc:.1f}" r="3" fill="{colour}"/>')
            o.append(f'<text x="{cx}" y="{y0 + ch - 12}" font-size="11" text-anchor="middle" fill="#555">half-extent {ext:.3f} R</text>')
    o.append('</svg>')
    return "\n".join(o)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'docs', 'figures', 'epicycles', 'v2_mockup.svg')
    T = float(sys.argv[2]) if len(sys.argv) > 2 else 240.0
    res = {}
    for r, case in enumerate(CASES):
        for c in (0, 1):
            res[(r, c)] = output(case, T=T, coupled=bool(c))[0]
    open(out, 'w').write(svg(res, T))
    print(out)
