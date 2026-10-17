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

What this file does NOT supply: the scores.  S and G come from the T1 metrics
(relevance and order, see docs/semantic_orbweaver_notes.md).  Until those exist
the monitor only displays whatever is written to its input.  The reference
series ("ref") is whatever a transformer scores on the SAME prompts with the
SAME scorers; the monitor cannot invent it.

Input: a JSON-lines file, one object per line, appended live:

    {"S": 0.62, "G": 0.20, "label": "what is your name", "src": "monad"}
    {"S": 0.71, "G": 0.80, "label": "what is your name", "src": "ref"}

Usage:
    lemniscate_monitor.py FILE            follow FILE live (window)
    lemniscate_monitor.py FILE --png OUT  render what FILE holds now, headless
    lemniscate_monitor.py --demo [--png OUT]
"""

import argparse
import json
import math
import os
import random
import sys

import matplotlib

A = 0.45            # [PARAM] lemniscate size: tolerated deficit/imbalance
DEAD = 0.08         # [PARAM] |x| below this with a large deficit = both-deficit
TRAIL = 40          # [PARAM] points kept per source
COLOUR = {'monad': '#c0392b', 'ref': '#2471a3'}


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
                    self.rows.setdefault(src, []).append(
                        (float(r['S']), float(r['G']), r.get('label', '')))
                except (ValueError, KeyError, TypeError):
                    continue
        for k in self.rows:
            self.rows[k] = self.rows[k][-TRAIL:]


def demo_rows():
    rnd = random.Random(7)
    out = {'monad': [], 'ref': []}
    for _ in range(25):
        out['monad'].append((rnd.uniform(.25, .75), rnd.uniform(.05, .45), 'demo'))
        out['ref'].append((rnd.uniform(.65, .95), rnd.uniform(.65, .95), 'demo'))
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
        xy = [to_xy(S, G) for S, G, _ in pts]
        c = COLOUR.get(src, '#555')
        ax.plot([p[0] for p in xy], [p[1] for p in xy], '-', color=c, alpha=.25, lw=1)
        ax.scatter([p[0] for p in xy[:-1]], [p[1] for p in xy[:-1]], s=14, color=c, alpha=.45)
        S, G, lab = pts[-1]
        ax.scatter([xy[-1][0]], [xy[-1][1]], s=70, color=c, edgecolor='k', zorder=5,
                   label=f'{src}: {region(S, G)}')
    ax.legend(loc='lower center', fontsize=8, ncol=2, frameon=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('file', nargs='?')
    ap.add_argument('--png')
    ap.add_argument('--demo', action='store_true')
    ap.add_argument('--interval', type=int, default=500, help='ms between polls')
    a = ap.parse_args()
    if not a.file and not a.demo:
        ap.error('give a FILE or --demo')
    if a.png:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    feed = Feed(a.file)
    fig, ax = plt.subplots(figsize=(7, 4.6))
    if a.png:
        feed.poll()
        draw(ax, demo_rows() if a.demo else feed.rows)
        fig.tight_layout(); fig.savefig(a.png, dpi=130)
        print(a.png)
        return 0

    def tick(_):
        feed.poll()
        draw(ax, demo_rows() if a.demo else feed.rows)

    ani = FuncAnimation(fig, tick, interval=a.interval, cache_frame_data=False)
    fig.tight_layout(); plt.show()
    return 0


if __name__ == '__main__':
    sys.exit(main())
