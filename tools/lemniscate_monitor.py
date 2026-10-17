#!/usr/bin/env python3
"""lemniscate_monitor.py — live Broca / Wernicke lemniscate monitor.

The aphasia diagram has three shapes: damage to Broca's area on one side,
damage to Wernicke's area on the other, and a lemniscate (∞) between them
where intact responses fall.  This draws that diagram and plots each reply
as a point on it, live, so the engine can be read against a reference.

Mapping (this file's own choice; every constant is a [PARAM]):

    S  semantic score   in [0, 1]   Wernicke side: content relevant to the prompt
    G  structure score  in [0, 1]   Broca side:    order, grammar, connectives

    x = G − S            imbalance.  x < 0: structure deficit  (Broca-type, telegraphic)
                                     x > 0: content deficit    (Wernicke-type, fluent, empty)
    y = 1 − (S + G)/2    overall deficit.  0 = nothing missing.

    intact region = inside a Bernoulli lemniscate (r⁴ = A²(y² − x²), the ∞ stood
    upright) about the origin: a perfect reply sits at the pinch, and the lobe is
    the tolerated drift (more imbalance is tolerated at small deficit than large).
    Outside it, left of the axis = Broca-type, right = Wernicke-type; a point
    straight above (|x| < DEAD) with a large deficit is both-deficit.

Taoist mode (--mode taoist, key `t` live): the same two scores drawn as a yin-yang.
The S is the Waveform / Standing Wave: on the S-axis diameter (flat torus) the nodes
are 0, 1/2, 1 (rim, centre) and the antinodes 1/4, 3/4 (the two dots).  Yang (white,
active, Broca) holds the black dot; yin (black, passive, Wernicke) holds the white dot.
The dots drive the spin.  Damage is on the OUTSIDE of a half; the interface (the S
line) is not scored (a gap or overlap there is drawn, nothing more).

    d_yang = 1 − G,  d_yin = 1 − S,  rel = d_yang − d_yin
    scale k = 1 − (d_yang + d_yin)/2          overall size (equal damage: centred, smaller)
    the more damaged half runs faster (rate 1 + KAPPA·|rel|) and its outer arc is dented
    (depth DEFORM·|rel|); the other half keeps the common rate and its shape
    passive is entrained by active: dθ_yin += K_LOCK·sin(θ_yang − θ_yin)
    barycentre b = Σ A_i·c_i·e^{iθ_i} / Σ A_i   (polygon area and centroid of each half)

The SHAPE of the epicycle is the measurement; the live Lyapunov exponent (--lyap) is only a cross-check.
The two comparisons always run together: the same scores on a static centre and on a free centre.

Healthy: equal rates, no dent, b = 0 (a point).  Small |rel|: the halves lock at a fixed
phase offset and b is a circle.  Larger |rel| beats the lock: the offset drifts and b
traces an epicycle.  Yin and yang are congruent under a 180° turn, so the two cases
differ only through the asymmetric constants (KAPPA, DEFORM, K_LOCK): all [PARAM].

What this file does NOT supply: the scores.  S and G come from the T1 metrics
(relevance and order, see docs/semantic_orbweaver_notes.md).  Until those exist
the monitor only displays whatever is written to its input.  The reference
series ("ref") is whatever a transformer scores on the SAME prompts with the
SAME scorers; the monitor cannot invent it.

Input: a JSON-lines file, one object per line, appended live.  M (optional, [0,1]) is how
well the two halves work together (the seam); absent, M = 1 − |S − G|:

    {"S": 0.62, "G": 0.20, "M": 0.50, "label": "what is your name", "src": "monad"}
    {"S": 0.71, "G": 0.80, "label": "what is your name", "src": "ref"}

Usage:
    lemniscate_monitor.py FILE            follow FILE live (window)
    lemniscate_monitor.py FILE --png OUT  render what FILE holds now, headless
    lemniscate_monitor.py --demo [--png OUT]
"""

import argparse
import cmath
import collections
import json
import math
import os
import random
import sys

import matplotlib

A = 0.45            # [PARAM] lemniscate size: tolerated deficit/imbalance
DEAD = 0.08         # [PARAM] |x| below this with a large deficit = both-deficit
TRAIL = 40          # [PARAM] points kept per source
COLOUR = {'monad': '#c0392b', 'ref': '#2471a3', 'monad:free': '#c0392b', 'monad:static': '#2471a3', 'ref:free': '#7f8c8d'}


def lemniscate(a=A, n=400):
    """Bernoulli lemniscate r² = a² cos 2θ, two lobes joined at the origin, turned
    to stand along y (x, y here are the monitor's own axes)."""
    xs, ys = [], []
    for k in range(n + 1):
        t = -math.pi / 4 + (math.pi / 2) * k / n
        r = a * math.sqrt(max(math.cos(2 * t), 0.0))
        xs.append(r * math.cos(t)); ys.append(r * math.sin(t))
    lx = [-x for x in reversed(xs)]
    ly = [-y for y in reversed(ys)]
    X, Y = xs + lx, ys + ly
    return Y, X                      # stood upright: lobes along y


def to_xy(S, G):
    return G - S, 1.0 - (S + G) / 2.0


def inside(S, G, a=A):
    """True when the point lies inside the upright lemniscate (the intact region)."""
    x, y = to_xy(S, G)
    return y >= 0 and (x * x + y * y) ** 2 <= a * a * (y * y - x * x)


def region(S, G):
    """intact; else Broca-type (x < 0), Wernicke-type (x > 0), or both-deficit
    (|x| < DEAD: the imbalance says nothing, the deficit says everything)."""
    if inside(S, G):
        return 'intact'
    x, _ = to_xy(S, G)
    if abs(x) < DEAD:
        return 'both-deficit'
    return 'Broca-type' if x < 0 else 'Wernicke-type'


class Feed:
    """Reads new lines from a JSONL file; remembers its offset."""
    def __init__(self, path):
        self.path, self.pos, self.rows = path, 0, {'monad': [], 'ref': []}

    def poll(self):
        if not self.path or not os.path.exists(self.path):
            return
        with open(self.path) as f:
            f.seek(self.pos)
            for line in f:
                if not line.endswith('\n'):
                    break
                self.pos += len(line.encode())
                try:
                    r = json.loads(line)
                    src = r.get('src', 'monad')
                    m = r.get('M')
                    self.rows.setdefault(src, []).append(
                        (float(r['S']), float(r['G']), r.get('label', ''),
                         None if m is None else float(m)))
                except (ValueError, KeyError, TypeError):
                    continue
        for k in self.rows:
            self.rows[k] = self.rows[k][-TRAIL:]


def demo_rows():
    rnd = random.Random(7)
    out = {'monad': [], 'ref': []}
    for _ in range(25):
        out['monad'].append((rnd.uniform(.25, .75), rnd.uniform(.05, .45), 'demo', None))
        out['ref'].append((rnd.uniform(.65, .95), rnd.uniform(.65, .95), 'demo', None))
    return out


def draw(ax, rows):
    ax.clear()
    ax.set_aspect('equal'); ax.set_xlim(-1, 1); ax.set_ylim(-0.1, 1.0)
    ax.axvspan(-1, -DEAD, color='#f5b7b1', alpha=.25, lw=0)
    ax.axvspan(DEAD, 1, color='#aed6f1', alpha=.25, lw=0)
    lx, ly = lemniscate()
    ax.fill(lx, ly, color='#abebc6', alpha=.55, lw=0)
    ax.plot(lx, ly, color='#1e8449', lw=1.6)
    ax.text(-.95, .93, 'Broca-type damage\nstructure deficit\n(telegraphic)', va='top', fontsize=8)
    ax.text(.95, .93, 'Wernicke-type damage\ncontent deficit\n(fluent, empty)', va='top', ha='right', fontsize=8)
    ax.text(0, A * .45, 'intact', ha='center', fontsize=8, color='#145a32')
    ax.set_xlabel('x = G − S   (structure − semantic)')
    ax.set_ylabel('y = 1 − (S+G)/2   (overall deficit)')
    for src, pts in rows.items():
        if not pts:
            continue
        xy = [to_xy(p[0], p[1]) for p in pts]
        c = COLOUR.get(src, '#555')
        ax.plot([p[0] for p in xy], [p[1] for p in xy], '-', color=c, alpha=.25, lw=1)
        ax.scatter([p[0] for p in xy[:-1]], [p[1] for p in xy[:-1]], s=14, color=c, alpha=.45)
        S, G = pts[-1][0], pts[-1][1]
        ax.scatter([xy[-1][0]], [xy[-1][1]], s=70, color=c, edgecolor='k', zorder=5,
                   label=f'{src}: {region(S, G)}')
    ax.legend(loc='lower center', fontsize=8, ncol=2, frameon=False)



# ── Taoist mode ─────────────────────────────────────────────────────────────

DOT_R = 5 / 38          # dot radius / outer radius, Wikimedia Commons Yin_yang.svg (public domain)
OMEGA0 = 1.2            # [PARAM] common spin, rad/s
K_LOCK = 1.0            # [PARAM] active -> passive entrainment
KAPPA = {'yang': 1.5, 'yin': 1.0}     # [PARAM] how much faster a damaged half runs
DEFORM = {'yang': 0.6, 'yin': 0.4}    # [PARAM] outer-arc dent depth per unit of relative damage
SCALE_FLOOR = 0.15      # smallest drawn size
TRACE_N = 600           # barycentre points kept
DOT_AT = {'yang': (0.0, 0.5), 'yin': (0.0, -0.5)}   # black dot in white at 1/4, white dot in black at 3/4


def _lin(a, b, n):
    return [a + (b - a) * i / n for i in range(n + 1)]


def _s_curve(n=90):
    """The S, (0,1) -> (0,0) -> (0,-1): two semicircles of radius 1/2, the first
    bulging right, the second left."""
    up = [(0.5 * math.cos(p), 0.5 + 0.5 * math.sin(p)) for p in _lin(math.pi / 2, -math.pi / 2, n)]
    lo = [(0.5 * math.cos(p), -0.5 + 0.5 * math.sin(p)) for p in _lin(math.pi / 2, 3 * math.pi / 2, n)]
    return up + lo


def _arc(a0, a1, delta, n=90):
    """Outer arc a0 -> a1; radius 1 at both ends, dented by delta in the middle."""
    out = []
    for i in range(n + 1):
        u = i / n
        a = a0 + (a1 - a0) * u
        r = 1.0 - delta * math.sin(math.pi * u) ** 2
        out.append((r * math.cos(a), r * math.sin(a)))
    return out


def half_poly(name, delta=0.0, n=90):
    """Outline of one half at unit radius.  yang = white (left arc), yin = black (right arc)."""
    arc = _arc(3 * math.pi / 2, math.pi / 2, delta, n) if name == 'yang' \
        else _arc(-math.pi / 2, math.pi / 2, delta, n)
    return arc + _s_curve(n)


def poly_ac(P):
    """(area, cx, cy) of a closed polygon (shoelace)."""
    a = cx = cy = 0.0
    m = len(P)
    for i in range(m):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % m]
        w = x0 * y1 - x1 * y0
        a += w; cx += (x0 + x1) * w; cy += (y0 + y1) * w
    a *= 0.5
    return abs(a), cx / (6 * a), cy / (6 * a)


class Tao:
    """One yin-yang: two halves, their phases, the barycentre and its trace."""
    def __init__(self):
        self.th = {'yang': 0.0, 'yin': 0.0}
        self.k = 1.0
        self.delta = {'yang': 0.0, 'yin': 0.0}
        self.b = 0j
        self.regime = 'intact'
        self.trace = collections.deque(maxlen=TRACE_N)

    def step(self, S, G, dt):
        dy, dw = 1.0 - G, 1.0 - S
        rel = dy - dw
        self.k = max(SCALE_FLOOR, 1.0 - (dy + dw) / 2.0)
        w_yang = OMEGA0 * (1.0 + KAPPA['yang'] * max(rel, 0.0))
        w_yin = OMEGA0 * (1.0 + KAPPA['yin'] * max(-rel, 0.0))
        self.delta = {'yang': DEFORM['yang'] * max(rel, 0.0), 'yin': DEFORM['yin'] * max(-rel, 0.0)}
        d_omega = abs(w_yang - w_yin)
        self.regime = ('intact' if d_omega < 1e-9 and max(self.delta.values()) < 1e-9
                       else 'locked' if d_omega < K_LOCK else 'drifting')
        w_yin += K_LOCK * math.sin(self.th['yang'] - self.th['yin'])
        self.th['yang'] += w_yang * dt
        self.th['yin'] += w_yin * dt
        self.b = self.barycentre()
        self.trace.append(self.b)

    def barycentre(self):
        tot, area = 0j, 0.0
        for name in ('yang', 'yin'):
            a, cx, cy = poly_ac(half_poly(name, self.delta[name]))
            a *= self.k ** 2
            tot += a * complex(cx, cy) * self.k * cmath.exp(1j * self.th[name])
            area += a
        return tot / area


def _rot(P, th, k):
    c, s = math.cos(th), math.sin(th)
    return [(k * (x * c - y * s), k * (x * s + y * c)) for x, y in P]


def draw_tao(ax, tao, title):
    from matplotlib.patches import Circle, Polygon
    ax.clear()
    ax.set_aspect('equal'); ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
    ax.set_xticks([]); ax.set_yticks([])
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec='#999', lw=0.8, ls=':'))
    phys = hasattr(tao, 'outline')
    for name, fc in (('yin', 'black'), ('yang', 'white')):
        P = tao.outline(name, tao.delta[name]) if phys else _rot(half_poly(name, tao.delta[name]), tao.th[name], tao.k)
        ax.add_patch(Polygon(P, closed=True, fc=fc, ec='#444', lw=1.0, alpha=0.9))
    for name, fc, ec in (('yang', 'black', 'black'), ('yin', 'white', 'black')):
        x, y = tao.dot(name) if phys else _rot([DOT_AT[name]], tao.th[name], tao.k)[0]
        ax.add_patch(Circle((x, y), DOT_R * tao.k, fc=fc, ec=ec, lw=0.8))
    if phys:
        wx, wy = tao.whole()
        ax.plot([wx], [wy], 'o', color='#1e8449', ms=5)                            # the whole (centre body)
        # the barycentre: the drawn origin when free, offset by −b from the fixed centre when pinned
        bx, by = (-tao.b.real, -tao.b.imag) if tao.pin else (0.0, 0.0)
        ax.plot([bx], [by], 'x', color='#c0392b', ms=8, mew=2)
    else:
        ax.plot([0], [0], '+', color='#1e8449', ms=9)
        ax.plot([tao.b.real], [tao.b.imag], 'x', color='#c0392b', ms=8, mew=2)
    ax.set_title(title, fontsize=7)


def draw_trace(ax, taos):
    """The barycentre path.  The view is derived from the trace each frame (nothing stored):
    half-extent = max |b| plus 20 %, never below MIN so a still disc stays a point."""
    ax.clear()
    ax.set_aspect('equal'); ax.axhline(0, color='#ccc', lw=.5); ax.axvline(0, color='#ccc', lw=.5)
    ext = 0.0
    for src, t in taos.items():
        pts = list(t.trace)
        if not pts:
            continue
        c = COLOUR.get(src, '#555')
        ax.plot([p.real for p in pts], [p.imag for p in pts], '-', color=c, lw=1, alpha=.7, label=src)
        ax.plot([pts[-1].real], [pts[-1].imag], 'o', color=c)
        ext = max(ext, max(abs(p) for p in pts))
    ext = max(ext * 1.2, 0.05)
    ax.set_xlim(-ext, ext); ax.set_ylim(-ext, ext)
    ax.set_title(f'barycentre path  (half-extent {ext:.3f} R)', fontsize=9)
    ax.legend(loc='lower right', fontsize=7, frameon=False)


# ── Taoist mode, three-body physics (tools/taoist_physics.py, System3) ───────
EDGE_GAIN = 0.6         # [PARAM] outer-arc dent per unit of a half's own damage
RHO_MM = 0.4            # [PARAM] density loss of the yin half per unit of seam damage
CMD_Y = 1.0             # [PARAM] yang dot spins faster by this × seam damage
CMD_W = 0.6             # [PARAM] yin dot spins slower by this × seam damage
LYAP_WINDOW = 60.0      # s: the live chaos readout averages the local exponent over this span
CHAOS_AT = 0.05         # /s: above this the readout says chaotic (regular baseline measured ~0.01)


class PhysTao:
    """The whole (a free centre body) and the two dot-weights: three anchors, two of them
    turning together around the third.  Damage kinds, kept apart:
        edge_y = 1 − G, edge_w = 1 − S   dents on the outside of each half (shape, mass, centre of mass)
        seam   = 1 − M                   how badly the halves work together: the dots' rates
                                         part company and the seam spring/damper weakens
    Shapes that match: nothing moves.  Edges that differ: regular, periodic epicycles.
    A distorted seam: the dots part company and throw the whole off the barycentre; measured
    chaotic only when the mismatch is strong (see the live readout)."""
    SUB = 0.01

    def __init__(self, pin=False, measure=False):
        import numpy as np
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import taoist_physics as TP
        self.np, self.TP, self.pin, self.measure = np, TP, pin, measure
        self.sys = TP.System3(pin=pin)
        self.shadow = None
        self.lam, self._acc, self._t = 0.0, [], 0.0
        self.th = {'yang': 0.0, 'yin': 0.0}
        self.k = 1.0
        self.delta = {'yang': 0.0, 'yin': 0.0}
        self.b = 0j
        self.regime = 'intact'
        self.trace = collections.deque(maxlen=TRACE_N)

    def params(self, S, G, M):
        TP = self.TP
        M = max(0.0, min(1.0, 1.0 - abs(S - G) if M is None else M))
        mu = 1.0 - M
        dy, dw = EDGE_GAIN * (1.0 - G), EDGE_GAIN * (1.0 - S)
        return (dict(delta_y=dy, delta_w=dw, rho_y=1.0, rho_w=1.0 - RHO_MM * mu,
                     cmd_y=TP.OMEGA0 * (1.0 + CMD_Y * mu), cmd_w=TP.OMEGA0 * (1.0 - CMD_W * mu)),
                dict(k_g=0.05 + (TP.K_G - 0.05) * M, c_g=0.01 + (TP.C_G - 0.01) * M), mu, dy, dw)

    def step(self, S, G, dt, M=None):
        TP, np = self.TP, self.np
        p, seam, mu, dy, dw = self.params(S, G, M)
        for sy in [self.sys] + ([self.shadow] if self.shadow else []):
            sy.k_g, sy.c_g = seam['k_g'], seam['c_g']
            sy.set_params(**p)
        if self.measure and self.shadow is None:
            self.shadow = TP.System3(pin=self.pin)
            self.shadow.k_g, self.shadow.c_g = seam['k_g'], seam['c_g']
            self.shadow.set_params(**p)
            self.shadow.load(self.sys.state() + 1e-7 * np.eye(16)[0])
        for _ in range(max(1, int(round(dt / self.SUB)))):
            self.sys.step(self.SUB)
            if self.shadow is not None:
                self.shadow.step(self.SUB)
            self._t += self.SUB
        d = np.linalg.norm(self.shadow.state() - self.sys.state()) if self.shadow is not None else 0.0
        if d > 0:
            self._acc.append((self._t, math.log(d / 1e-7)))
            self.shadow.load(self.sys.state() + (self.shadow.state() - self.sys.state()) * (1e-7 / d))
            span = [x for x in self._acc if x[0] > self._t - LYAP_WINDOW]
            if len(span) > 20:
                self.lam = sum(x[1] for x in span) / (span[-1][0] - span[0][0] + self.SUB * 4)
            self._acc = span
        self.th = {'yang': self.sys.yaw(0), 'yin': self.sys.yaw(1)}
        self.delta = {'yang': dy, 'yin': dw}
        b = self.sys.barycentre()
        self.b = complex(b[0], b[1])
        self.regime = ('intact' if max(dy, dw, mu) < 1e-9 else 'damaged' if not self.measure
                       else 'chaotic' if self.lam > CHAOS_AT else 'regular')
        self.trace.append(self.b)

    def _off(self):
        """Origin of the drawn frame.  A free system drifts when the masses change, so it is
        drawn in the barycentric frame; a pinned centre keeps its own fixed frame."""
        if self.pin:
            return (0.0, 0.0)
        B = self.sys.xc - self.sys.barycentre()          # the system barycentre, lab coordinates
        return (float(B[0]), float(B[1]))

    def outline(self, name, delta):
        """Outline of a half, carried by its own body, in the drawn frame."""
        i = 0 if name == 'yang' else 1
        ox, oy = self._off()
        return [(x - ox, y - oy) for x, y in self.sys.to_lab(i, half_poly(name, delta))]

    def dot(self, name):
        i = 0 if name == 'yang' else 1
        ox, oy = self._off()
        x, y = self.sys.to_lab(i, [DOT_AT[name]])[0]
        return x - ox, y - oy

    def whole(self):
        """Where the whole (the centre body) sits in the drawn frame."""
        ox, oy = self._off()
        return (float(self.sys.xc[0]) - ox, float(self.sys.xc[1]) - oy)


def latest_scores(rows):
    return {src: pts[-1][:2] + (pts[-1][3] if len(pts[-1]) > 3 else None,) for src, pts in rows.items() if pts}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('file', nargs='?')
    ap.add_argument('--png')
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--mode', choices=('normal', 'taoist'), default='normal')
    ap.add_argument('--scores', help='S,G[,M] for one static monad channel (headless taoist test)')
    ap.add_argument('--kinematic', action='store_true', help='taoist: the old two-rotor model (no physics)')
    ap.add_argument('--lyap', action='store_true', help='taoist: also run a shadow copy and print the finite-time Lyapunov exponent (costs 2x; the SHAPE of the epicycle is the measurement)')
    ap.add_argument('--steps', type=int, default=900, help='taoist: simulation steps before a --png')
    ap.add_argument('--dt', type=float, default=0.04, help='taoist: seconds per step')
    ap.add_argument('--interval', type=int, default=40, help='ms between ticks (live)')
    a = ap.parse_args()
    if not a.file and not a.demo and not a.scores:
        ap.error('give a FILE, --demo or --scores S,G')
    if a.png:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    feed = Feed(a.file)
    taos = {}
    state = {'mode': a.mode}
    fig = plt.figure(figsize=(8.6, 4.8))

    def rows_now():
        if a.scores:
            v = [float(x) for x in a.scores.split(',')]
            return {'monad': [(v[0], v[1], 'static', v[2] if len(v) > 2 else None)]}
        if a.demo:
            return demo_rows()
        feed.poll()
        return feed.rows

    def build():
        fig.clf()
        if state['mode'] == 'normal':
            return [fig.add_subplot(1, 1, 1)]
        return [fig.add_subplot(1, 3, 1), fig.add_subplot(1, 3, 2), fig.add_subplot(1, 3, 3)]

    axes = build()

    def render(rows, advance=1):
        if state['mode'] == 'normal':
            draw(axes[0], rows)
            return
        sc = latest_scores(rows)
        # the two comparisons always run together: the same scores on a STATIC centre
        # (regular, star-shaped epicycles) and on a FREE centre (the dots' mismatch throws the
        # whole off the barycentre); a transformer reference, when present, on a free centre.
        for src, (S, G, M) in sc.items():
            variants = ('static', 'free') if src == 'monad' else ('free',)
            for var in variants:
                key = f'{src}:{var}'
                t = taos.setdefault(key, Tao() if a.kinematic else PhysTao(pin=(var == 'static'), measure=a.lyap))
                for _ in range(advance):
                    t.step(S, G, a.dt) if a.kinematic else t.step(S, G, a.dt, M)
        shown = [k for k in ('monad:static', 'monad:free') if k in taos] or [k for k in taos][:2]
        for ax, key in zip(axes[:2], shown):
            src = key.split(':')[0]
            S, G = sc[src][0], sc[src][1]
            t = taos[key]
            draw_tao(ax, t, f"{key}: {region(S, G)} | {t.regime}" + (f" (λ={t.lam:+.2f}/s)" if getattr(t, 'measure', False) else "")
                     + f"\n|b|={abs(t.b):.3f}R  dents {t.delta['yang']:.2f}/{t.delta['yin']:.2f}")
        axes[1].set_visible(len(shown) > 1)
        draw_trace(axes[2], taos)

    def on_key(ev):
        if ev.key == 't':
            state['mode'] = 'taoist' if state['mode'] == 'normal' else 'normal'
            axes[:] = build()

    if a.png:
        rows = rows_now()
        render(rows, advance=max(1, a.steps) if state['mode'] == 'taoist' else 1)
        fig.tight_layout(); fig.savefig(a.png, dpi=130)
        print(a.png)
        return 0

    fig.canvas.mpl_connect('key_press_event', on_key)

    def tick(_):
        render(rows_now())

    ani = FuncAnimation(fig, tick, interval=a.interval, cache_frame_data=False)
    fig.tight_layout(); plt.show()
    return 0


if __name__ == '__main__':
    sys.exit(main())
