#!/usr/bin/env python3
"""v1_system3_physics.py — draw the epicycles of the Taoist mode as one SVG (VERSION 1, kept as history).

Model: tools/taoist_physics.py System3 (the whole + two dot-weights spinning about their own centres of mass,
driven at the dots).  SUPERSEDED on 2026-10-17 by v2_mockup.py after Cody's correction: the whole spins, the dots
swing.  Output: docs/figures/epicycles/v1_system3_physics.svg

Each row is one damage case (S, G, M as the monitor takes them); the two columns are the two
comparisons that always run together: a STATIC centre and a FREE centre.  The path is the
whole's offset from the system barycentre (the epicycle), run through PhysTao exactly as the
monitor does, so the picture and the live window agree.  Every cell has its own scale (the
shape is the measurement); the half-extent in units of R is printed in the cell.

Usage: v1_system3_physics.py OUT.svg [seconds]
"""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tools/
os.environ.setdefault("MPLBACKEND", "Agg")

CASES = [
    ("healthy: shapes match",               1.0, 1.0, None),
    ("matched edges (both halves dented)",  0.8, 0.8, None),
    ("one edge damaged: yang (Broca)",      1.0, 0.7, 1.0),
    ("one edge damaged: yin (Wernicke)",    0.7, 1.0, 1.0),
    ("seam mildly distorted",               0.9, 0.6, None),
    ("seam distorted",                      0.9, 0.3, None),
    ("seam badly distorted",                0.9, 0.1, 0.0),
]


def _run(job):
    title, S, G, M, pin, T = job
    import lemniscate_monitor as L
    t = L.PhysTao(pin=pin)
    pts = []
    for k in range(int(T / 0.04)):
        t.step(S, G, 0.04, M)
        if k % 2 == 0:
            pts.append((t.b.real, t.b.imag))
    return pts


def svg(results, T):
    cw, ch, left, top = 300, 230, 250, 70
    W, H = left + 2 * cw + 20, top + len(CASES) * ch + 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<text x="14" y="26" font-size="17" font-weight="bold">Taoist mode: the epicycles ({T:g} s of motion)</text>',
           f'<text x="{W - 14}" y="26" font-size="12" text-anchor="end" fill="#8e44ad">script: {os.path.basename(__file__)} (v1, superseded)</text>',
           '<text x="14" y="46" font-size="11" fill="#444">The whole\'s offset from the barycentre. Each cell is scaled to its own path; '
           'the half-extent is printed in units of R. The shape is the measurement.</text>',
           f'<text x="{left + cw / 2}" y="64" font-size="13" text-anchor="middle" fill="#2471a3">static centre</text>',
           f'<text x="{left + cw * 1.5}" y="64" font-size="13" text-anchor="middle" fill="#c0392b">free centre</text>']
    for r, (title, S, G, M) in enumerate(CASES):
        y0 = top + r * ch
        mm = 1 - abs(S - G) if M is None else M
        out.append(f'<text x="14" y="{y0 + 22}" font-size="13" font-weight="bold">{title}</text>')
        out.append(f'<text x="14" y="{y0 + 40}" font-size="11" fill="#555">S={S:g}  G={G:g}  M={mm:.2f}</text>')
        out.append(f'<line x1="10" y1="{y0 + ch - 6}" x2="{W - 10}" y2="{y0 + ch - 6}" stroke="#ddd"/>')
        for c, (pin, colour) in enumerate(((True, '#2471a3'), (False, '#c0392b'))):
            pts = results[(r, pin)]
            ext = max(max(abs(x) for x, _ in pts), max(abs(y) for _, y in pts), 1e-6)
            cx, cy = left + c * cw + cw / 2, y0 + ch / 2 - 4
            sc = (ch / 2 - 22) / ext if ext > 1e-6 else 1.0
            out.append(f'<line x1="{cx - cw / 2 + 20}" y1="{cy}" x2="{cx + cw / 2 - 20}" y2="{cy}" stroke="#eee"/>')
            out.append(f'<line x1="{cx}" y1="{cy - ch / 2 + 22}" x2="{cx}" y2="{cy + ch / 2 - 30}" stroke="#eee"/>')
            if ext < 1e-6:
                out.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{colour}"/>')
                out.append(f'<text x="{cx}" y="{y0 + ch - 12}" font-size="11" text-anchor="middle" fill="#555">a point (extent &lt; 1e-6 R)</text>')
                continue
            d = "M" + " L".join(f"{cx + x * sc:.1f},{cy - y * sc:.1f}" for x, y in pts)
            out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="0.7" stroke-opacity="0.85"/>')
            ex, ey = pts[-1]
            out.append(f'<circle cx="{cx + ex * sc:.1f}" cy="{cy - ey * sc:.1f}" r="3" fill="{colour}"/>')
            out.append(f'<text x="{cx}" y="{y0 + ch - 12}" font-size="11" text-anchor="middle" fill="#555">half-extent {ext:.3f} R</text>')
    out.append('</svg>')
    return "\n".join(out)


if __name__ == '__main__':
    out = sys.argv[1]
    T = float(sys.argv[2]) if len(sys.argv) > 2 else 240.0
    jobs = [(c[0], c[1], c[2], c[3], pin, T) for c in CASES for pin in (True, False)]
    with Pool(8) as p:
        res = p.map(_run, jobs)
    results = {}
    for i, c in enumerate(CASES):
        results[(i, True)] = res[2 * i]
        results[(i, False)] = res[2 * i + 1]
    open(out, 'w').write(svg(results, T))
    print(out)
