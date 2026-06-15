#!/usr/bin/env python3
"""
fritzing.py — Fritzing .fz / .fzz generator for SSR hardware
==============================================================

Fritzing .fz files are XML with embedded SVG part imagery.
PSVG is SVG with undefined operators.
The circuit diagram IS a sedenion pathway:
  current (J) flows through the circuit
  as J_red/J_blue flows through the sedenion algebra.

This module generates:
  .fzp    Fritzing part file  — one component (SVG + connectors)
  .fz     Fritzing sketch     — full circuit layout (XML)
  .fzz    Fritzing bundle     — sketch + parts in one ZIP
  PSVG    <FritzingSketch/>   — embed circuit as undefined operator in PSVG

SSR hardware parts:
  RTL_SDR     Software Defined Radio dongle  (RF channel)
  Microphone  Condenser microphone           (audio channel)
  SMA_Ant     SMA stub antenna               (RF input)
  USB_Hub     USB hub (power + data)
  SSR_Host    Host computer running LSHS

Circuit topology = sedenion graph:
  Antenna → RTL_SDR → USB_Hub → SSR_Host   (J_red: RF upward)
  SSR_Host → USB_Hub → RTL_SDR → Antenna   (J_blue: control downward)
  Microphone → SSR_Host                    (audio channel, direct)
  The zero divisor: the boundary between analog RF and digital sedenion.
"""

from __future__ import annotations

import os
import io
import uuid
import zipfile
from typing import Dict, List, Optional, Tuple


# ── SVG primitives for Fritzing part imagery ──────────────────────────────────

def _part_svg(title: str, color: str, width: int, height: int,
              connectors: List[Tuple[str, float, float, str]]) -> str:
    """
    Minimal breadboard-view SVG for a Fritzing part.
    connectors: [(name, cx, cy, direction), ...]  direction: n/s/e/w
    """
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
        f'"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'version="1.1" x="0" y="0" '
        f'width="{width}px" height="{height}px" '
        f'viewBox="0 0 {width} {height}">',
        f'  <g id="breadboard">',
        # body
        f'    <rect x="4" y="4" width="{width-8}" height="{height-8}" '
        f'rx="4" ry="4" fill="{color}" stroke="#333" stroke-width="1.5"/>',
        f'    <text x="{width//2}" y="{height//2+4}" '
        f'text-anchor="middle" font-family="monospace" '
        f'font-size="{min(10, width//len(title)+1)}" fill="#fff">{title}</text>',
    ]
    # connector dots
    for name, cx, cy, _dir in connectors:
        lines.append(
            f'    <circle id="connector_{name}" cx="{cx:.1f}" cy="{cy:.1f}" '
            f'r="3" fill="#888" stroke="#555" stroke-width="1"/>'
        )
    lines += ['  </g>', '</svg>']
    return '\n'.join(lines)


def _schematic_svg(title: str, width: int, height: int,
                   connectors: List[Tuple[str, float, float, str]]) -> str:
    """Minimal schematic-view SVG."""
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}px" height="{height}px" viewBox="0 0 {width} {height}">',
        f'  <g id="schematic">',
        f'    <rect x="8" y="8" width="{width-16}" height="{height-16}" '
        f'fill="none" stroke="#000" stroke-width="1"/>',
        f'    <text x="{width//2}" y="{height//2+4}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="#000">{title}</text>',
    ]
    for name, cx, cy, _dir in connectors:
        lines.append(
            f'    <circle id="connector_{name}" cx="{cx:.1f}" cy="{cy:.1f}" '
            f'r="2.5" fill="none" stroke="#000" stroke-width="1"/>'
        )
    lines += ['  </g>', '</svg>']
    return '\n'.join(lines)


# ── Fritzing part definitions (SSR hardware) ──────────────────────────────────

class FritzingPart:
    """One Fritzing component: .fzp metadata + SVG imagery."""

    def __init__(self, module_id: str, title: str, description: str,
                 bb_svg: str, sch_svg: str,
                 connectors: List[Dict]):
        self.module_id   = module_id
        self.title       = title
        self.description = description
        self.bb_svg      = bb_svg
        self.sch_svg     = sch_svg
        self.connectors  = connectors     # [{id, name, type, description}, ...]

    def fzp_xml(self) -> str:
        """Generate the .fzp XML for this part."""
        conn_lines = []
        for c in self.connectors:
            conn_lines.append(f"""    <connector id="{c['id']}" type="{c['type']}" name="{c['name']}">
      <description>{c['description']}</description>
      <views>
        <breadboardView>
          <p svgId="connector_{c['name']}" layer="breadboard"/>
        </breadboardView>
        <schematicView>
          <p svgId="connector_{c['name']}" layer="schematic"/>
        </schematicView>
      </views>
    </connector>""")

        conn_block = '\n'.join(conn_lines)
        return f"""<?xml version='1.0' encoding='UTF-8'?>
<module fritzingVersion="0.9.10" moduleId="{self.module_id}">
  <version>1.0.0</version>
  <title>{self.title}</title>
  <description>{self.description}</description>
  <author>SSR — Sedenion Spectral Relativity</author>
  <date>2026-06-15</date>
  <label>{self.title[:12]}</label>
  <tags>
    <tag>SSR</tag>
    <tag>SedenionSpectralRelativity</tag>
  </tags>
  <properties/>
  <views>
    <breadboardView>
      <layers image="breadboard/{self.module_id}.svg">
        <layer layerId="breadboard"/>
      </layers>
    </breadboardView>
    <schematicView>
      <layers image="schematic/{self.module_id}.svg">
        <layer layerId="schematic"/>
      </layers>
    </schematicView>
    <iconView>
      <layers image="breadboard/{self.module_id}.svg">
        <layer layerId="icon"/>
      </layers>
    </iconView>
  </views>
  <connectors>
{conn_block}
  </connectors>
</module>"""


# ── SSR part catalogue ─────────────────────────────────────────────────────────

def _make_parts() -> Dict[str, FritzingPart]:
    parts = {}

    # ── RTL-SDR dongle ────────────────────────────────────────────────────────
    bb  = _part_svg('RTL-SDR', '#1a3a6a', 80, 40, [
        ('USB', 8, 20, 'w'),
        ('SMA', 72, 20, 'e'),
    ])
    sch = _schematic_svg('RTL-SDR', 80, 40, [
        ('USB', 8, 20, 'w'),
        ('SMA', 72, 20, 'e'),
    ])
    parts['RTL_SDR'] = FritzingPart(
        module_id   = 'RTL_SDR',
        title       = 'RTL-SDR Dongle',
        description = 'Software Defined Radio receiver. '
                      'RF input via SMA. Data/power via USB. '
                      'RZIF-RF channel for SSR oscilloscope.',
        bb_svg  = bb,
        sch_svg = sch,
        connectors = [
            {'id': 'connector0', 'name': 'USB',  'type': 'female',
             'description': 'USB 2.0 — power + I/Q data stream'},
            {'id': 'connector1', 'name': 'SMA',  'type': 'female',
             'description': 'SMA female — RF antenna input (24MHz–1.7GHz)'},
        ]
    )

    # ── SMA stub antenna ─────────────────────────────────────────────────────
    bb  = _part_svg('Antenna', '#2a5a2a', 20, 80, [
        ('SMA', 10, 72, 's'),
    ])
    sch = _schematic_svg('ANT', 20, 80, [('SMA', 10, 72, 's')])
    parts['SMA_ANT'] = FritzingPart(
        module_id   = 'SMA_ANT',
        title       = 'SMA Stub Antenna',
        description = 'Quarter-wave stub antenna. '
                      'SMA male plug to RTL-SDR. '
                      'The point where EM → digital. '
                      'The crossing through i at RF.',
        bb_svg  = bb,
        sch_svg = sch,
        connectors = [
            {'id': 'connector0', 'name': 'SMA', 'type': 'male',
             'description': 'SMA male — connects to RTL-SDR SMA female'},
        ]
    )

    # ── Condenser microphone ──────────────────────────────────────────────────
    bb  = _part_svg('Mic', '#5a2a2a', 40, 40, [
        ('OUT', 32, 20, 'e'),
        ('GND', 20, 32, 's'),
    ])
    sch = _schematic_svg('MIC', 40, 40, [
        ('OUT', 32, 20, 'e'),
        ('GND', 20, 32, 's'),
    ])
    parts['MICROPHONE'] = FritzingPart(
        module_id   = 'MICROPHONE',
        title       = 'Condenser Microphone',
        description = 'Electret condenser mic. '
                      'Audio channel for SSR oscilloscope. '
                      'English → acoustic phonon → QPhonon/PPhonon → RZIF → sedenion.',
        bb_svg  = bb,
        sch_svg = sch,
        connectors = [
            {'id': 'connector0', 'name': 'OUT', 'type': 'male',
             'description': 'Audio output — 3.5mm or direct wire'},
            {'id': 'connector1', 'name': 'GND', 'type': 'male',
             'description': 'Ground'},
        ]
    )

    # ── USB hub ───────────────────────────────────────────────────────────────
    bb  = _part_svg('USB Hub', '#3a3a1a', 80, 60, [
        ('HOST', 8,  30, 'w'),
        ('P1',  40,  4,  'n'),
        ('P2',  60,  4,  'n'),
        ('P3',  40, 56,  's'),
    ])
    sch = _schematic_svg('USB HUB', 80, 60, [
        ('HOST', 8, 30, 'w'), ('P1', 40, 4, 'n'),
        ('P2', 60, 4, 'n'), ('P3', 40, 56, 's'),
    ])
    parts['USB_HUB'] = FritzingPart(
        module_id   = 'USB_HUB',
        title       = 'USB Hub',
        description = 'Powered USB hub. '
                      'Connects RTL-SDR + microphone interface to host. '
                      'The branching point — J current distributes here.',
        bb_svg  = bb,
        sch_svg = sch,
        connectors = [
            {'id': 'connector0', 'name': 'HOST', 'type': 'female',
             'description': 'USB to host computer'},
            {'id': 'connector1', 'name': 'P1', 'type': 'male',
             'description': 'USB port 1 — RTL-SDR'},
            {'id': 'connector2', 'name': 'P2', 'type': 'male',
             'description': 'USB port 2 — audio interface'},
            {'id': 'connector3', 'name': 'P3', 'type': 'male',
             'description': 'USB port 3 — future expansion'},
        ]
    )

    # ── SSR Host (computer) ───────────────────────────────────────────────────
    bb  = _part_svg('SSR Host', '#2a1a4a', 120, 80, [
        ('USB',  8,  40, 'w'),
        ('AUD', 60,   4, 'n'),
        ('OUT', 112, 40, 'e'),
    ])
    sch = _schematic_svg('SSR HOST', 120, 80, [
        ('USB', 8, 40, 'w'), ('AUD', 60, 4, 'n'), ('OUT', 112, 40, 'e'),
    ])
    parts['SSR_HOST'] = FritzingPart(
        module_id   = 'SSR_HOST',
        title       = 'SSR Host Computer',
        description = 'Host running lshs_sdr.py + phonon.py + ssr_scope.py. '
                      'RZIF-RF + RZIF-audio → sedenion fingerprint → J^μ Noether current. '
                      'The ZD fault lives here: analog RF/audio → digital sedenion.',
        bb_svg  = bb,
        sch_svg = sch,
        connectors = [
            {'id': 'connector0', 'name': 'USB', 'type': 'female',
             'description': 'USB — receives RTL-SDR + audio data'},
            {'id': 'connector1', 'name': 'AUD', 'type': 'female',
             'description': 'Audio in — 3.5mm microphone jack'},
            {'id': 'connector2', 'name': 'OUT', 'type': 'male',
             'description': 'PSVG output — sedenion fingerprint stream'},
        ]
    )

    return parts


# ── Fritzing sketch (.fz) ──────────────────────────────────────────────────────

class FritzingSketch:
    """
    A Fritzing sketch — the full SSR oscilloscope circuit layout.

    Topology (breadboard view):
      SMA_ANT → RTL_SDR → USB_HUB → SSR_HOST
      MICROPHONE ─────────────────→ SSR_HOST

    Current topology = sedenion graph:
      J_red flows upward:  antenna → SDR → hub → host → RZIF → sedenion
      J_blue flows down:   sedenion → host → hub → SDR → antenna (tuning)
      The zero divisor:    the SMA junction (analog ↔ digital boundary = i)
    """

    def __init__(self):
        self.instances: List[Dict] = []
        self.wires:     List[Dict] = []
        self._mid       = 0

    def _next_id(self) -> str:
        self._mid += 1
        return str(self._mid)

    def add_instance(self, module_id: str, title: str,
                     x: float, y: float, z: float = 0.5) -> str:
        iid = self._next_id()
        self.instances.append({
            'id': iid, 'module_id': module_id,
            'title': title, 'x': x, 'y': y, 'z': z,
        })
        return iid

    def add_wire(self, x1: float, y1: float, x2: float, y2: float,
                 color: str = '#606060', thickness: str = '0.9') -> str:
        wid = self._next_id()
        self.wires.append({
            'id': wid, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'color': color, 'thickness': thickness,
        })
        return wid

    def fz_xml(self) -> str:
        inst_lines = []
        for inst in self.instances:
                inst_lines.append(
                f'  <instance moduleIdRef="{inst["module_id"]}"'
                f' modelIndex="{inst["id"]}" id="{inst["id"]}">\n'
                f'    <title>{inst["title"]}</title>\n'
                f'    <views>\n'
                f'      <breadboardView>\n'
                f'        <geometry x="{inst["x"]}" y="{inst["y"]}" z="{inst["z"]}"'
                f' xFlip="false" yFlip="false"/>\n'
                f'      </breadboardView>\n'
                f'      <schematicView>\n'
                f'        <geometry x="{inst["x"]}" y="{inst["y"]}" z="{inst["z"]}"'
                f' xFlip="false" yFlip="false"/>\n'
                f'      </schematicView>\n'
                f'    </views>\n'
                f'  </instance>'
            )

        wire_lines = []
        for w in self.wires:
                wire_lines.append(
                f'  <wire moduleIdRef="WireModuleID"'
                f' modelIndex="{w["id"]}" id="{w["id"]}"'
                f' color="{w["color"]}" thickness="{w["thickness"]}" banded="false">\n'
                f'    <views>\n'
                f'      <breadboardView>\n'
                f'        <geometry x1="{w["x1"]}" y1="{w["y1"]}"'
                f' x2="{w["x2"]}" y2="{w["y2"]}"/>\n'
                f'      </breadboardView>\n'
                f'      <schematicView>\n'
                f'        <geometry x1="{w["x1"]}" y1="{w["y1"]}"'
                f' x2="{w["x2"]}" y2="{w["y2"]}"/>\n'
                f'      </schematicView>\n'
                f'    </views>\n'
                f'  </wire>'
            )

        uid        = uuid.uuid4().hex[:8]
        inst_block = '\n'.join(inst_lines)
        wire_block = '\n'.join(wire_lines)
        return (
            "<?xml version='1.0' encoding='UTF-8'?>\n"
            f'<module fritzingVersion="0.9.10" moduleId="SSR_Universal_Oscilloscope_{uid}">\n'
            '  <title>SSR Universal Oscilloscope</title>\n'
            '  <description>\n'
            '    Sedenion Spectral Relativity - Universal Oscilloscope hardware.\n'
            '    Antenna to RTL-SDR to USB Hub to SSR Host (LSHS / phonon / ssr_scope).\n'
            '    Microphone to SSR Host.\n'
            '    J_red current: EM signal upward to sedenion fingerprint.\n'
            '    J_blue current: control signal downward to hardware.\n'
            '    Zero divisor boundary: SMA junction (analog RF meets digital sedenion).\n'
            '    The heartbeat is the pi-shaped hyper-integral under the hypercomplex signal.\n'
            '    Integral over one complete cycle = 0 (Noether conservation).\n'
            '  </description>\n'
            '  <author>SSR - Sedenion Spectral Relativity / PtolemyHolcus</author>\n'
            '  <date>2026-06-15</date>\n'
            '  <instances>\n'
            f'{inst_block}\n'
            '  </instances>\n'
            '  <wires>\n'
            f'{wire_block}\n'
            '  </wires>\n'
            '</module>'
        )


def make_ssr_sketch() -> FritzingSketch:
    """
    Build the standard SSR oscilloscope circuit.

    Layout (breadboard coordinates, 100-unit grid):
      Antenna  (50,  60)
      RTL-SDR  (150, 100)
      USB Hub  (300, 100)
      Host     (450, 80)
      Mic      (420, 220)
    """
    sk = FritzingSketch()

    sk.add_instance('SMA_ANT',    'Antenna',          50,  60)
    sk.add_instance('RTL_SDR',    'RTL-SDR',         150, 100)
    sk.add_instance('USB_HUB',    'USB Hub',         300, 100)
    sk.add_instance('SSR_HOST',   'SSR Host',        450,  80)
    sk.add_instance('MICROPHONE', 'Microphone',      420, 220)

    # RF chain (J_red — orange)
    sk.add_wire( 70, 80, 150, 120, color='#cc6600', thickness='1.2')   # ant→sdr
    sk.add_wire(230, 120, 300, 120, color='#cc6600', thickness='1.2')  # sdr→hub
    sk.add_wire(380, 120, 450, 120, color='#cc6600', thickness='1.2')  # hub→host

    # Audio chain (J_blue — blue)
    sk.add_wire(460, 240, 510, 160, color='#4060cc', thickness='1.0')  # mic→host

    # Control return (J_blue back — dashed equivalent, purple)
    sk.add_wire(450, 130, 380, 140, color='#8040cc', thickness='0.7')  # host→hub back
    sk.add_wire(300, 140, 230, 130, color='#8040cc', thickness='0.7')  # hub→sdr back

    return sk


# ── .fzz bundle (ZIP) ─────────────────────────────────────────────────────────

def write_fzz(path: str, sketch: FritzingSketch,
              parts: Optional[Dict[str, FritzingPart]] = None) -> None:
    """
    Write a .fzz bundle: sketch.fz + all part files inside a ZIP.
    Fritzing opens .fzz directly.
    """
    if parts is None:
        parts = _make_parts()

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Main sketch
        zf.writestr('sketch.fz', sketch.fz_xml())

        # Parts
        for pid, part in parts.items():
            zf.writestr(f'parts/{pid}.fzp',           part.fzp_xml())
            zf.writestr(f'parts/breadboard/{pid}.svg', part.bb_svg)
            zf.writestr(f'parts/schematic/{pid}.svg',  part.sch_svg)

    print(f'  Fritzing bundle → {path}')
    print(f'  Parts: {len(parts)}  |  Instances: {len(sketch.instances)}'
          f'  |  Wires: {len(sketch.wires)}')


def write_fz(path: str, sketch: FritzingSketch) -> None:
    """Write just the .fz sketch XML (no part files)."""
    with open(path, 'w') as f:
        f.write(sketch.fz_xml())
    print(f'  Fritzing sketch → {path}')


# ── PSVG integration: <FritzingSketch/> undefined operator ───────────────────

def psvg_block(sketch: FritzingSketch,
               x: float = 10, y: float = 10,
               w: float = 400, h: float = 300) -> str:
    """
    Render the SSR circuit as a <FritzingSketch/> undefined operator block
    for embedding in a PSVG file.

    The circuit is drawn as a simple block diagram with J_red / J_blue
    current paths visible. No fill beyond what the math requires.
    The topology IS the sedenion graph.
    """
    # Part display params keyed by module_id
    PART_STYLE: Dict[str, Tuple[str, str, int, int]] = {
        #              (label,       fill,      w,  h)
        'SMA_ANT':    ('ANT',       '#2a5a2a', 24, 48),
        'RTL_SDR':    ('RTL-SDR',   '#1a3a6a', 64, 32),
        'USB_HUB':    ('USB HUB',   '#3a3a1a', 56, 40),
        'SSR_HOST':   ('SSR HOST',  '#2a1a4a', 80, 56),
        'MICROPHONE': ('MIC',       '#5a2a2a', 32, 32),
    }

    # Scale sketch coordinates into (x, y, w, h) viewport
    xs = [inst['x'] for inst in sketch.instances]
    ys = [inst['y'] for inst in sketch.instances]
    sk_x0 = min(xs) - 20
    sk_y0 = min(ys) - 20
    sk_w  = max(xs) - min(xs) + 120
    sk_h  = max(ys) - min(ys) + 80

    def tx(vx: float) -> float:
        return x + (vx - sk_x0) / sk_w * w

    def ty(vy: float) -> float:
        return y + (vy - sk_y0) / sk_h * h

    def tw(vw: float) -> float:
        return vw / sk_w * w

    def th(vh: float) -> float:
        return vh / sk_h * h

    lines: List[str] = []
    lines.append(f'  <!-- Fritzing SSR circuit — <FritzingSketch/> undefined operator -->')
    lines.append(f'  <FritzingSketch'
                 f' circuit="SSR_Universal_Oscilloscope"'
                 f' topology="sedenion_graph"'
                 f' j_red="RF_chain" j_blue="audio+control"'
                 f' zero_divisor="SMA_junction"'
                 f' heartbeat="π-hyper-integral=0">')

    # Background
    lines.append(f'    <rect x="{x:.1f}" y="{y:.1f}" '
                 f'width="{w:.1f}" height="{h:.1f}" '
                 f'fill="#0a0a0a" stroke="#222" stroke-width="0.5" rx="4"/>')

    # Title
    lines.append(f'    <text x="{x+w/2:.1f}" y="{y+12:.1f}" '
                 f'text-anchor="middle" fill="#444" '
                 f'font-size="8" font-family="monospace">'
                 f'SSR CIRCUIT — Fritzing topology</text>')

    # Wires first (behind parts)
    WIRE_COLORS = {
        '#cc6600': ('J_red  RF', '#cc6600'),
        '#4060cc': ('J_blue audio', '#4060cc'),
        '#8040cc': ('J_blue ctrl', '#8040cc'),
    }
    for wire in sketch.wires:
        wx1, wy1 = tx(wire['x1']), ty(wire['y1'])
        wx2, wy2 = tx(wire['x2']), ty(wire['y2'])
        col = wire['color']
        lines.append(f'    <line x1="{wx1:.1f}" y1="{wy1:.1f}" '
                     f'x2="{wx2:.1f}" y2="{wy2:.1f}" '
                     f'stroke="{col}" stroke-width="{float(wire["thickness"])*0.8:.1f}" '
                     f'opacity="0.85"/>')

    # Parts
    for inst in sketch.instances:
        mid   = inst['module_id']
        style = PART_STYLE.get(mid, (mid[:8], '#333333', 48, 28))
        lbl, fill, pw, ph = style
        px = tx(inst['x']) - tw(pw) * 0.5
        py = ty(inst['y']) - th(ph) * 0.5
        rpw = tw(pw)
        rph = th(ph)

        lines.append(f'    <rect x="{px:.1f}" y="{py:.1f}" '
                     f'width="{rpw:.1f}" height="{rph:.1f}" '
                     f'fill="{fill}" stroke="#555" stroke-width="0.8" rx="2"/>')
        lines.append(f'    <text x="{px+rpw/2:.1f}" y="{py+rph/2+3:.1f}" '
                     f'text-anchor="middle" fill="#ddd" '
                     f'font-size="6" font-family="monospace">{lbl}</text>')

    # ZD marker at SMA junction (between ANT and RTL-SDR)
    ant_inst  = next((i for i in sketch.instances if i['module_id'] == 'SMA_ANT'), None)
    sdr_inst  = next((i for i in sketch.instances if i['module_id'] == 'RTL_SDR'), None)
    if ant_inst and sdr_inst:
        zd_x = (tx(ant_inst['x']) + tx(sdr_inst['x'])) / 2
        zd_y = (ty(ant_inst['y']) + ty(sdr_inst['y'])) / 2
        lines.append(f'    <circle cx="{zd_x:.1f}" cy="{zd_y:.1f}" r="4" '
                     f'fill="none" stroke="#c04060" stroke-width="1.2"/>')
        lines.append(f'    <text x="{zd_x:.1f}" y="{zd_y+14:.1f}" '
                     f'text-anchor="middle" fill="#c04060" '
                     f'font-size="6" font-family="monospace">ZD / i</text>')

    lines.append('  </FritzingSketch>')
    return '\n'.join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse, sys

    ap = argparse.ArgumentParser(
        description='fritzing.py — SSR hardware as Fritzing .fz/.fzz + PSVG')
    ap.add_argument('--fz',   default='', help='Write .fz sketch to this path')
    ap.add_argument('--fzz',  default='', help='Write .fzz bundle to this path')
    ap.add_argument('--psvg', default='', help='Write PSVG embed block to stdout/file')
    args = ap.parse_args()

    print()
    print('SSR Fritzing — Sedenion Spectral Relativity circuit')
    print('=' * 52)

    parts  = _make_parts()
    sketch = make_ssr_sketch()

    print(f'  Parts:     {list(parts.keys())}')
    print(f'  Instances: {len(sketch.instances)}')
    print(f'  Wires:     {len(sketch.wires)}')
    print()

    if args.fz:
        write_fz(args.fz, sketch)

    if args.fzz:
        write_fzz(args.fzz, sketch, parts)

    if args.psvg:
        block = psvg_block(sketch)
        if args.psvg == '-':
            print(block)
        else:
            # Wrap in minimal SVG for preview
            svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<svg xmlns="http://www.w3.org/2000/svg" '
                   'width="500" height="350" viewBox="0 0 500 350">\n'
                   '  <rect width="500" height="350" fill="#080810"/>\n'
                   + block + '\n</svg>')
            with open(args.psvg, 'w') as f:
                f.write(svg)
            print(f'  PSVG embed → {args.psvg}')

    if not any([args.fz, args.fzz, args.psvg]):
        # Default: write all to /tmp
        write_fz('/tmp/ssr_oscilloscope.fz', sketch)
        write_fzz('/tmp/ssr_oscilloscope.fzz', sketch, parts)
        block = psvg_block(sketch)
        svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<svg xmlns="http://www.w3.org/2000/svg" '
               'width="500" height="350" viewBox="0 0 500 350">\n'
               '  <rect width="500" height="350" fill="#080810"/>\n'
               + block + '\n</svg>')
        with open('/tmp/ssr_fritzing_psvg.svg', 'w') as f:
            f.write(svg)
        print('  PSVG embed → /tmp/ssr_fritzing_psvg.svg')

    print()
    print('  Topology: ANT → RTL-SDR → USB Hub → SSR Host')
    print('  J_red  (RF chain):   orange')
    print('  J_blue (audio/ctrl): blue/purple')
    print('  ZD / i:              SMA junction — analog ↔ digital boundary')
    print('  ∮ J dt = 0:          the π-integral closes at the ZD')
