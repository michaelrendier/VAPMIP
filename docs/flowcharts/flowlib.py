#!/usr/bin/env python3
"""flowlib.py -- a tiny code-flow-chart drawer (SVG) in the ISO 5807:1985 symbol set.   (2026-11-25)

Symbols (ISO 5807 / ANSI flowchart convention; https://en.wikipedia.org/wiki/ECMA-4 for the standard's lineage, https://creately.com/guides/flowchart-symbols/ for the plain-language list):
    terminator  oval              start / end                          process     rectangle            one step
    decision    diamond           a branch on a condition              input/output parallelogram       data in or out
    predefined  rectangle, double side bars   a named sub-process defined elsewhere (here: another lane or the other chart)
    stored data cylinder          a file the code reads or writes      connector   labelled arrow        control flow
Every title is a name from the code (a C function, a struct, a file); the second line says what it does.  Colours are fixed fills with near-black text, so the picture reads in either theme.
"""
from __future__ import annotations
import textwrap
from xml.sax.saxutils import escape

INK, PAPER, LINE = '#16202c', '#fbfaf6', '#3a4656'
FILL = {'term': '#cdebd6', 'proc': '#dbe7f6', 'dec': '#fbe6b8', 'io': '#e4d9f2', 'pre': '#f6d5d5', 'data': '#e6e0cc'}
W, H = 252, 66


class Chart:
    def __init__(self, title: str, sub: str, lanes: list[tuple[str, str]], lane_w=312, row_h=96, top=118, left=40):
        self.title, self.sub, self.lanes, self.lane_w, self.row_h, self.top, self.left = title, sub, lanes, lane_w, row_h, top, left
        self.nodes: dict[str, dict] = {}; self.edges: list[tuple] = []; self.notes: list[tuple] = []

    def node(self, id_, lane, row, shape, title, sub='', dy=0, w=W, h=None, tag='', tagside='r'):
        h = h or (H + 22 if shape == 'dec' else H)
        cx = self.left + self.lane_w * lane + self.lane_w / 2; cy = self.top + 36 + self.row_h * row + dy
        self.nodes[id_] = dict(lane=lane, row=row, shape=shape, title=title, sub=sub, cx=cx, cy=cy, w=w, h=h, tag=tag, tagside=tagside)

    def edge(self, a, b, label='', route='auto', bend=0):
        self.edges.append((a, b, label, route, bend))

    def note(self, lane, row, text, dy=0):
        self.notes.append((lane, row, text, dy))

    # ---- geometry helpers ----
    def _port(self, n, side):
        x, y, w, h = n['cx'], n['cy'], n['w'], n['h']
        return {'t': (x, y - h / 2), 'b': (x, y + h / 2), 'l': (x - w / 2, y), 'r': (x + w / 2, y)}[side]

    def _path(self, a, b, route, bend):
        A, B = self.nodes[a], self.nodes[b]
        if route == 'auto':
            if A['lane'] == B['lane']: route = 'down' if B['cy'] > A['cy'] else 'up'
            elif B['cy'] == A['cy']: route = 'side'
            else: route = 'elbow'
        if route == 'down': return [self._port(A, 'b'), self._port(B, 't')]
        if route == 'up': return [self._port(A, 't'), self._port(B, 'b')]
        if route == 'side':
            s, t = ('r', 'l') if B['cx'] > A['cx'] else ('l', 'r'); return [self._port(A, s), self._port(B, t)]
        if route == 'elbow':                                          # out of the side of A, along, then down/up into B
            s = 'r' if B['cx'] > A['cx'] else 'l'; p0 = self._port(A, s); t = 't' if B['cy'] > A['cy'] else 'b'; p1 = self._port(B, t)
            return [p0, (p1[0], p0[1]), p1]
        if route == 'loopr':                                          # back edge on the right of both nodes
            p0, p1 = self._port(A, 'r'), self._port(B, 'r'); x = max(p0[0], p1[0]) + 20 + bend; return [p0, (x, p0[1]), (x, p1[1]), p1]
        if route == 'loopl':
            p0, p1 = self._port(A, 'l'), self._port(B, 'l'); x = min(p0[0], p1[0]) - 20 - bend; return [p0, (x, p0[1]), (x, p1[1]), p1]
        if route == 'bottomside':                                     # from the bottom of A, across, into the side of B
            p0 = self._port(A, 'b'); s = 'l' if B['cx'] > A['cx'] else 'r'; p1 = self._port(B, s); return [p0, (p0[0], p1[1]), p1]
        if route == 'sidetop':                                        # from the side of A, across, down into the top of B (a lane to the right)
            return self._path(a, b, 'elbow', bend)
        raise ValueError(route)

    def _text(self, n):
        x, y, w, h, shape = n['cx'], n['cy'], n['w'], n['h'], n['shape']
        avail = {'proc': 0.92, 'pre': 0.80, 'io': 0.74, 'term': 0.80, 'data': 0.92, 'dec': 0.56}[shape] * w
        t, sub = n['title'], n['sub']; out = []
        fs = 13.0; cw = 0.605                                                   # monospace advance, em
        lines = [t]
        if len(t) * cw * fs > avail:
            fs = max(10.5, avail / (len(t) * cw))
            if len(t) * cw * fs > avail + 0.5:                                  # still too long: wrap on spaces
                fs = 11.5; lines = textwrap.wrap(t, max(8, int(avail / (cw * fs)))) or [t]
        sfs = 10.8 if shape != 'dec' else 10.2
        sl = []
        for ln in sub.split('\n') if sub else []: sl += textwrap.wrap(ln, max(10, int(avail / (0.52 * sfs)))) or ['']
        if len(sl) > 3: sfs = 9.6; sl = [q for ln in sub.split('\n') for q in textwrap.wrap(ln, max(10, int(avail / (0.52 * sfs))))]
        lh, sh = fs + 2.5, sfs + 2.2
        total = len(lines) * lh + len(sl) * sh; y0 = y - total / 2 + fs * 0.8 + (6 if shape == 'data' else 0)
        for k, ln in enumerate(lines):
            out.append(f'<text x="{x}" y="{y0 + k * lh:.1f}" font-size="{fs:.1f}" font-weight="700" fill="{INK}" text-anchor="middle" font-family="DejaVu Sans Mono, monospace">{escape(ln)}</text>')
        for k, ln in enumerate(sl):
            out.append(f'<text x="{x}" y="{y0 + len(lines) * lh + k * sh:.1f}" font-size="{sfs}" fill="{INK}" text-anchor="middle">{escape(ln)}</text>')
        return out

    def _shape(self, n):
        x, y, w, h, s = n['cx'], n['cy'], n['w'], n['h'], n['shape']; f = FILL[s]; a = f'fill="{f}" stroke="{LINE}" stroke-width="1.6"'
        l, r, t, b = x - w / 2, x + w / 2, y - h / 2, y + h / 2
        if s == 'term': return f'<rect x="{l}" y="{t}" width="{w}" height="{h}" rx="{h/2}" {a}/>'
        if s == 'proc': return f'<rect x="{l}" y="{t}" width="{w}" height="{h}" rx="4" {a}/>'
        if s == 'pre': return f'<rect x="{l}" y="{t}" width="{w}" height="{h}" rx="4" {a}/><line x1="{l+11}" y1="{t}" x2="{l+11}" y2="{b}" stroke="{LINE}" stroke-width="1.6"/><line x1="{r-11}" y1="{t}" x2="{r-11}" y2="{b}" stroke="{LINE}" stroke-width="1.6"/>'
        if s == 'dec': return f'<polygon points="{x},{t} {r},{y} {x},{b} {l},{y}" {a}/>'
        if s == 'io': return f'<polygon points="{l+16},{t} {r},{t} {r-16},{b} {l},{b}" {a}/>'
        if s == 'data':
            ry = 9; return (f'<path d="M{l},{t+ry} A{w/2},{ry} 0 0 1 {r},{t+ry} L{r},{b-ry} A{w/2},{ry} 0 0 1 {l},{b-ry} Z" {a}/>'
                            f'<path d="M{l},{t+ry} A{w/2},{ry} 0 0 0 {r},{t+ry}" fill="none" stroke="{LINE}" stroke-width="1.6"/>')
        raise ValueError(s)

    def svg(self) -> str:
        cols = len(self.lanes); width = self.left * 2 + self.lane_w * cols
        rows = max(n['row'] for n in self.nodes.values()) + 1; height = self.top + 80 + self.row_h * rows + 70
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="DejaVu Sans, Verdana, sans-serif">',
             f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>',
             f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
             f'<text x="{self.left}" y="46" font-size="26" font-weight="700" fill="{INK}">{escape(self.title)}</text>',
             f'<text x="{self.left}" y="74" font-size="14" fill="{INK}">{escape(self.sub)}</text>']
        for i, (nm, sub) in enumerate(self.lanes):                      # lanes
            x = self.left + self.lane_w * i
            o.append(f'<rect x="{x+6}" y="{self.top-6}" width="{self.lane_w-12}" height="{height-self.top-34}" rx="10" fill="{"#f3f1ea" if i % 2 == 0 else "#f8f6f0"}" stroke="#d6d1c3"/>')
            o.append(f'<text x="{x+self.lane_w/2}" y="{self.top+14}" font-size="14.5" font-weight="700" fill="{INK}" text-anchor="middle">{escape(nm)}</text>')
            o.append(f'<text x="{x+self.lane_w/2}" y="{self.top+30}" font-size="11" fill="{INK}" text-anchor="middle">{escape(sub)}</text>')
        for a, b, label, route, bend in self.edges:                    # edges under nodes
            pts = self._path(a, b, route, bend); d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.6" marker-end="url(#ah)"/>')
            if False:
                (x0, y0), (x1, y1) = pts[0], pts[1]; lx, ly = x0 + (6 if x1 == x0 else (14 if x1 > x0 else -14)), y0 + (14 if y1 > y0 and x1 == x0 else -5)
                if x1 != x0: ly = y0 - 6
                o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" font-weight="700" fill="{INK}" text-anchor="{"start" if x1 >= x0 else "end"}" paint-order="stroke" stroke="{PAPER}" stroke-width="4">{escape(label)}</text>')
        for n in self.nodes.values():
            o.append(self._shape(n)); o.extend(self._text(n))
        for a, b, label, route, bend in self.edges:                    # labels on top of the nodes
            if not label: continue
            pts = self._path(a, b, route, bend); (x0, y0), (x1, y1) = pts[0], pts[1]
            horizontal = y1 == y0; lx = x0 + (7 if not horizontal else (16 if x1 > x0 else -16)); ly = y0 + (15 if not horizontal and y1 > y0 else -6)
            if horizontal: ly = y0 - 6
            o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" font-weight="700" fill="{INK}" text-anchor="{"start" if (not horizontal or x1 >= x0) else "end"}" paint-order="stroke" stroke="{PAPER}" stroke-width="4">{escape(label)}</text>')
        for n in self.nodes.values():                                   # connectors: a circled label marks a call and the place it lands (ISO on-page connector)
            if n['tag']:
                tx = n['cx'] + (n['w'] / 2 + 4 if n['tagside'] == 'r' else -(n['w'] / 2 + 4)); ty = n['cy'] - n['h'] / 2 + 6
                o.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="12" fill="#ffd34d" stroke="{LINE}" stroke-width="1.6"/><text x="{tx:.1f}" y="{ty+4.5:.1f}" font-size="13" font-weight="700" fill="#000" text-anchor="middle">{escape(n["tag"])}</text>')
        for lane, row, text, dy in self.notes:
            x = self.left + self.lane_w * lane + self.lane_w / 2; y = self.top + 36 + self.row_h * row + dy
            for k, ln in enumerate(text.split('\n')): o.append(f'<text x="{x}" y="{y+k*13}" font-size="11" font-style="italic" fill="{INK}" text-anchor="middle">{escape(ln)}</text>')
        # legend
        ly = height - 26; lx = self.left
        o.append(f'<text x="{lx}" y="{ly}" font-size="11.5" fill="{INK}">symbols (ISO 5807): oval = start/end · rectangle = step · diamond = decision · parallelogram = input/output · double-barred rectangle = sub-process (another lane, or the other chart) · cylinder = stored data · every title is a name in the code</text>')
        o.append('</svg>')
        return '\n'.join(o)
