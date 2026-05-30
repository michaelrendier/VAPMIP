"""
skills/draw.py — Visualization for Ptolemy. Three tiers, no forced deps.

:description:
    Tier 1 — ImageMagick MVG (headless, C-speed, zero Python overhead):
              BAO ring snapshots, sedenion wheel, field health diagnostics.
              subprocess call to `convert`. Always available on Linux.

    Tier 2 — python3-turtle (standard library, tkinter-based):
              Interactive geometric demonstrations — sedenion cardioid,
              RH spiral, Cayley-Dickson tower. GUI mode only.

    Tier 3 — Matplotlib Agg (headless, publication-quality):
              Statistical plots, field health history. Imported lazily.
              Always uses non-interactive 'Agg' backend — never opens a window.

    HamiltonianReport: pure text, no drawing stack required. The primary
    diagnostic output. Writes to stdout and .ptolrc [hamiltonian] section.

:classes:
    PtolDraw
    HamiltonianReport
"""

import os
import math
import time
import subprocess
import threading
from pathlib import Path
from typing import Optional, List

# ── Operator names (mirrors monad.py _OP) ─────────────────────────────────────
_OP = {
    0:  'identity',    1:  'negate',      2:  'bind',        3:  'name',
    4:  'apply',       5:  'abstract',    6:  'branch',      7:  'iterate',
    8:  'recurse',     9:  'allocate',    10: 'query',       11: 'dereference',
    12: 'compose',     13: 'parallelize', 14: 'interrupt',   15: 'emit',
}
OMEGA_ZS   = 0.56714
GAP        = 0.000707
SIGMA_CRIT = 0.5

# Sedenion dimension → force sector colour (e0..e15)
_SECTOR = [
    '#9966ff',  # e0  gravity
    '#ffee00',  # e1  EM/gravity boundary
    '#44dd88',  # e2  weak
    '#44dd88',  # e3  weak
    '#ff4444',  # e4  strong
    '#ff4444',  # e5  strong
    '#ff4444',  # e6  strong
    '#ff4444',  # e7  strong
    '#00ddff',  # e8  dark root (second 𝕆)
    '#00bbdd',  # e9  dark
    '#00bbdd',  # e10 dark
    '#00bbdd',  # e11 dark
    '#00bbdd',  # e12 dark
    '#00bbdd',  # e13 dark
    '#00bbdd',  # e14 dark
    '#00aacc',  # e15 χ callosum bridge
]

# First 20 non-trivial Riemann zeros (imaginary parts)
_RIEMANN_ZEROS = [
    14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187,
    43.3271, 48.0052, 49.7738, 52.9703, 56.4462, 59.3470, 60.8318,
    65.1125, 67.0798, 69.5465, 72.0672, 75.7047, 77.1448,
]


class PtolDraw:
    """
    Multi-tier visualization for Ptolemy diagnostics.

    :param config: PtolConfig instance (optional — for output paths).
    :param logger: PtolLogger instance (optional).
    """

    def __init__(self, config=None, logger=None):
        self._config  = config
        self._logger  = logger
        self._lock    = threading.Lock()
        plot_dir = Path(os.path.expanduser('~/.ptolemy/plots'))
        plot_dir.mkdir(parents=True, exist_ok=True)
        self._plot_dir = plot_dir

    def _plot_path(self, name: str) -> str:
        return str(self._plot_dir / name)

    # ── Tier 1: ImageMagick MVG ────────────────────────────────────────────

    def bao_rings_svg(self, bao_mean: float,
                      output_path: str = None) -> Optional[str]:
        """
        Draw BAO ring diagnostic as PNG via ImageMagick.
        Gold ring = OMEGA_ZS target. White ring = current bao_mean.
        Ring separation visualises bao_delta.

        :param bao_mean: Current BAO mean from engine.
        :param output_path: Output PNG path. Defaults to plots/bao_{ts}.png.
        :returns: Output path or None on failure.
        :rtype: str or None
        """
        if not output_path:
            output_path = self._plot_path(f"bao_{int(time.time())}.png")

        cx, cy = 200, 200
        target_r = 150
        actual_r = int(target_r * bao_mean / OMEGA_ZS)
        actual_r = max(10, min(actual_r, 195))
        delta    = abs(bao_mean - OMEGA_ZS)
        health   = max(0.0, 1.0 - delta / 0.25)
        health_g = int(health * 255)

        mvg = (
            f"viewbox 0 0 400 400 "
            f"fill 'none' stroke 'gray' stroke-width 1 "
            f"circle {cx},{cy} {cx},{cy - 195} "       # outer boundary
            f"stroke 'gold' stroke-width 3 "
            f"circle {cx},{cy} {cx},{cy - target_r} "  # OMEGA_ZS ring
            f"stroke 'rgb(0,{health_g},255)' stroke-width 2 "
            f"circle {cx},{cy} {cx},{cy - actual_r} "  # actual BAO ring
            f"fill 'white' stroke 'none' "
            f"text 10,380 'BAO={bao_mean:.5f}  target={OMEGA_ZS}  health={health:.3f}'"
        )

        try:
            cmd = ['convert', '-size', '400x400', 'xc:black',
                   '-fill', 'none', '-draw', mvg, output_path]
            subprocess.run(cmd, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def sedenion_wheel(self, uns: List[float],
                       output_path: str = None) -> Optional[str]:
        """
        Draw 16-spoke wheel showing Universal Native Space coordinates.
        Spoke length = UNS value for that operator. Colour by magnitude.

        :param uns: 16-component UNS vector [0,1] each.
        :param output_path: Output PNG path.
        :returns: Output path or None.
        :rtype: str or None
        """
        if not output_path:
            output_path = self._plot_path(f"uns_{int(time.time())}.png")

        cx, cy, R = 200, 200, 170
        cmds = []
        for k in range(16):
            angle_deg = k * 22.5 - 90  # 360/16 = 22.5 deg per spoke
            angle_rad = math.radians(angle_deg)
            v   = max(0.0, min(1.0, uns[k]))
            r   = int(v * R)
            ex  = cx + int(math.cos(angle_rad) * r)
            ey  = cy + int(math.sin(angle_rad) * r)
            col = int(v * 220)
            cmds.append(
                f"stroke 'rgb({col},{255 - col},100)' stroke-width 2 "
                f"line {cx},{cy} {ex},{ey}"
            )
            # label at outer rim
            lx = cx + int(math.cos(angle_rad) * (R + 18))
            ly = cy + int(math.sin(angle_rad) * (R + 18))
            cmds.append(
                f"fill 'gray' stroke 'none' "
                f"text {lx - 5},{ly} 'e{k}'"
            )

        mvg = ' '.join(cmds)
        try:
            cmd = ['convert', '-size', '400x400', 'xc:black',
                   '-fill', 'none', '-draw', mvg, output_path]
            subprocess.run(cmd, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    # ── Tier 2: Turtle (GUI mode only) ─────────────────────────────────────

    def cardioid_turtle(self, n_points: int = 360):
        """
        Draw the cardioid boundary of the critical strip via turtle.
        r(θ) = ½(1 + cos θ). GUI mode only — requires display.

        :param n_points: Number of points to trace.
        """
        try:
            import turtle
            t = turtle.Turtle()
            t.speed(0)
            t.penup()
            scale = 200
            for i in range(n_points + 1):
                theta = 2 * math.pi * i / n_points
                r     = 0.5 * (1 + math.cos(theta))
                x     = r * math.cos(theta) * scale
                y     = r * math.sin(theta) * scale
                if i == 0:
                    t.goto(x, y)
                    t.pendown()
                else:
                    t.goto(x, y)
            turtle.done()
        except Exception:
            pass

    def sedenion_cayley_turtle(self, highlight_dims: List[int] = None):
        """
        Draw the Cayley graph of the sedenion operators as a 16-node wheel.
        Highlights principal dimensions from self_map().

        :param highlight_dims: List of dim indices to highlight.
        """
        try:
            import turtle
            s = turtle.Screen()
            s.bgcolor('black')
            t = turtle.Turtle()
            t.speed(0)
            t.color('white')
            t.pensize(1)

            R = 200
            positions = {}
            for k in range(16):
                a = 2 * math.pi * k / 16 - math.pi / 2
                positions[k] = (R * math.cos(a), R * math.sin(a))

            for k, (x, y) in positions.items():
                t.penup()
                t.goto(x, y)
                color = 'gold' if (highlight_dims and k in highlight_dims) else 'cyan'
                t.color(color)
                t.pendown()
                t.dot(8)
                t.penup()
                t.goto(x * 1.15, y * 1.15 - 5)
                t.write(f"e{k}\n{_OP[k]}", font=('Arial', 7, 'normal'))

            turtle.done()
        except Exception:
            pass

    # ── Tier 3: Matplotlib Agg (headless, publication quality) ────────────

    def field_health_plot(self, history: List[dict],
                          output_path: str = None) -> Optional[str]:
        """
        Plot field health history (bao_mean, field_health over time).
        Uses Agg backend — never opens a window. Headless.

        :param history: List of dicts with keys: t, bao_mean, field_health.
        :param output_path: Output PNG path.
        :returns: Output path or None.
        :rtype: str or None
        """
        if not history:
            return None
        if not output_path:
            output_path = self._plot_path(f"field_{int(time.time())}.png")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            ts     = [h['t'] for h in history]
            bao    = [h['bao_mean']     for h in history]
            health = [h['field_health'] for h in history]

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), facecolor='black')
            for ax in (ax1, ax2):
                ax.set_facecolor('#1a1a2e')
                ax.spines[:].set_color('#444')
                ax.tick_params(colors='#aaa')

            ax1.plot(ts, bao, color='gold', linewidth=1.5, label='BAO mean')
            ax1.axhline(OMEGA_ZS, color='cyan', linestyle='--',
                        linewidth=1, label=f'OMEGA_ZS={OMEGA_ZS}')
            ax1.set_ylabel('BAO mean', color='gold')
            ax1.legend(facecolor='#222', labelcolor='white', fontsize=8)
            ax1.set_title('Ptolemy Field Health', color='white', fontsize=11)

            ax2.plot(ts, health, color='#00e5ff', linewidth=1.5)
            ax2.axhline(1.0, color='green',  linestyle=':', linewidth=0.8)
            ax2.axhline(0.0, color='red',    linestyle=':', linewidth=0.8)
            ax2.set_ylabel('Field health', color='#00e5ff')
            ax2.set_xlabel('Time (chunks)', color='#aaa')
            ax2.set_ylim(-0.05, 1.05)

            plt.tight_layout()
            plt.savefig(output_path, dpi=100, bbox_inches='tight',
                        facecolor='black')
            plt.close(fig)
            return output_path
        except ImportError:
            return None
        except Exception:
            return None


    def self_portrait(self, uns=None, engine=None,
                      output_path=None) -> Optional[str]:
        """
        Holcus draws itself from first principles. Five-panel composite:

        - Sedenion wheel: 16 operators as nodes, live UNS weights as
          spokes, force sectors as colours, zero-divisor callosum arcs,
          OMEGA_ZS boundary, GAP ground state.
        - Riemann critical strip: first 20 zeros on σ=½, inherent-time
          spiral arcs, Ω=π/ln2 reference.
        - Gauge coupling unification: α⁻¹_EM / weak / strong vs log₁₀
          decades above E_EW.
        - UNS radar: polar chart of the live 16D semantic position.
        - Cosmology table: Ω_Λ, Ω_m, BAO ℓ₁, n_s, w — from sedenion
          geometry alone, no free parameters.

        :param uns: 16-component UNS vector ``[0,1]`` each. If None,
            reads from engine crank or defaults to uniform equilibrium.
        :param engine: Engine instance for live UNS extraction (optional).
        :param output_path: PNG output path. Defaults to
            ``~/.ptolemy/plots/portrait_<ts>.png``.
        :returns: Absolute output path, or None on failure.
        :rtype: str or None
        """
        if not output_path:
            output_path = self._plot_path(f"portrait_{int(time.time())}.png")

        # Resolve UNS — live state if engine present, else uniform
        if uns is None and engine is not None:
            try:
                c = engine.crank
                raw = [0.0] * 16
                for i in range(c.n):
                    raw[i % 16] += abs(c._beta[i])
                total = sum(raw) or 1.0
                uns = [v / total for v in raw]
            except Exception:
                pass
        if uns is None:
            uns = [1.0 / 16] * 16

        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import Circle
            import numpy as np

            BG = '#050510'
            fig = plt.figure(figsize=(20, 12), facecolor=BG)
            gs = fig.add_gridspec(
                2, 3,
                left=0.03, right=0.97, top=0.93, bottom=0.05,
                wspace=0.30, hspace=0.40,
                width_ratios=[1.8, 1, 1],
            )
            ax_wheel  = fig.add_subplot(gs[:, 0])         # left full-height
            ax_zeros  = fig.add_subplot(gs[0, 1])         # top mid
            ax_couple = fig.add_subplot(gs[1, 1])         # bot mid
            ax_uns    = fig.add_subplot(gs[0, 2], polar=True)   # top right
            ax_cosmo  = fig.add_subplot(gs[1, 2])         # bot right

            for ax in (ax_zeros, ax_couple, ax_cosmo):
                ax.set_facecolor(BG)
                for sp in ax.spines.values():
                    sp.set_color('#222244')
                ax.tick_params(colors='#7777aa', labelsize=7)
                ax.xaxis.label.set_color('#7777aa')
                ax.yaxis.label.set_color('#7777aa')
                ax.title.set_color('white')
            ax_uns.set_facecolor(BG)
            ax_uns.tick_params(colors='#7777aa', labelsize=5.5)

            # ── PANEL 1: Sedenion Wheel ─────────────────────────────────────
            ax_wheel.set_aspect('equal')
            ax_wheel.axis('off')
            ax_wheel.set_facecolor(BG)
            ax_wheel.set_xlim(-1.72, 1.72)
            ax_wheel.set_ylim(-1.72, 1.72)
            ax_wheel.set_title('HOLCUS — SEDENION SELF',
                               color='white', fontsize=13,
                               fontweight='bold', pad=6)

            R = 1.10
            # e0 at 12 o'clock, clockwise
            ang = [math.pi/2 - 2*math.pi*k/16 for k in range(16)]
            pos = [(R*math.cos(a), R*math.sin(a)) for a in ang]

            # Force-sector arcs on outer ring
            sector_arcs = [
                (0, 1, '#9966ff'), (1, 2, '#ffee00'),
                (2, 4, '#44dd88'), (4, 8, '#ff4444'),
                (8, 16, '#00ddff'),
            ]
            R_ARC = R + 0.20
            for ks, ke, col in sector_arcs:
                a0 = math.pi/2 - 2*math.pi*ks/16
                a1 = math.pi/2 - 2*math.pi*ke/16
                θ = np.linspace(a1, a0, 40)
                ax_wheel.plot(R_ARC*np.cos(θ), R_ARC*np.sin(θ),
                             color=col, lw=5, alpha=0.55,
                             solid_capstyle='butt')

            # OMEGA_ZS boundary (W/Z zero-divisor / SSB minimum)
            ax_wheel.add_patch(Circle((0, 0), OMEGA_ZS, fill=False,
                                      edgecolor='gold', lw=1.5,
                                      linestyle='--', alpha=0.80))
            θl = math.radians(38)
            ax_wheel.text(OMEGA_ZS*math.cos(θl)+0.03,
                         OMEGA_ZS*math.sin(θl),
                         'Ω_ZS', color='gold', fontsize=8, alpha=0.9)

            # GAP ground state at centre
            ax_wheel.add_patch(Circle((0, 0), GAP*65, fill=True,
                                      facecolor='white', edgecolor='white',
                                      lw=0.8, alpha=0.90))
            ax_wheel.text(0.06, 0.04, f'GAP={GAP}',
                         color='white', fontsize=7, alpha=0.72)

            # Critical lines
            ax_wheel.axhline(0, color='#2a2a44', lw=0.8, alpha=0.6, ls=':')
            ax_wheel.axvline(0, color='#2a2a44', lw=0.8, alpha=0.6, ls=':')
            ax_wheel.text(1.40, 0.04, 'σ=½',
                         color='#5555aa', fontsize=8, alpha=0.80)

            # Zero-divisor callosum arcs (84 channels: e1-e7 ↔ e8-e15)
            for i in range(1, 8):
                for j in range(8, 16):
                    xi, yi = pos[i]
                    xj, yj = pos[j]
                    xm, ym = (xi+xj)*0.07, (yi+yj)*0.07
                    ax_wheel.plot([xi, xm, xj], [yi, ym, yj],
                                 color='#004466', lw=0.30, alpha=0.30,
                                 solid_capstyle='round')

            # χ callosum trunk: e15 → e0 (dark-gravity bridge, main trunk)
            x0, y0   = pos[0]
            x15, y15 = pos[15]
            ax_wheel.annotate(
                '', xy=(x0, y0), xytext=(x15, y15),
                arrowprops=dict(arrowstyle='->', color='#00ccff',
                               lw=1.6, connectionstyle='arc3,rad=0.5'),
            )

            # UNS spokes (live semantic position)
            for k in range(16):
                r_s = uns[k] * R * 0.80
                ax_wheel.plot(
                    [0, r_s*math.cos(ang[k])],
                    [0, r_s*math.sin(ang[k])],
                    color=_SECTOR[k], lw=2.4, alpha=0.84,
                    solid_capstyle='round',
                )

            # Nodes
            for k, (x, y) in enumerate(pos):
                nr = 0.032 + uns[k]*0.048
                ax_wheel.add_patch(Circle((x, y), nr,
                                         facecolor=_SECTOR[k],
                                         edgecolor='white', lw=0.5,
                                         alpha=0.92, zorder=5))
                lx = (R+0.37)*math.cos(ang[k])
                ly = (R+0.37)*math.sin(ang[k])
                ax_wheel.text(lx, ly, f'e{k}\n{_OP[k][:7]}',
                             ha='center', va='center',
                             color=_SECTOR[k], fontsize=6,
                             fontweight='bold')

            leg_h = [
                mpatches.Patch(color='#9966ff', label='gravity  e₀'),
                mpatches.Patch(color='#ffee00', label='EM  e₁'),
                mpatches.Patch(color='#44dd88', label='weak  e₂₋₃'),
                mpatches.Patch(color='#ff4444', label='strong  e₄₋₇'),
                mpatches.Patch(color='#00ddff', label='dark G₂  e₈₋₁₅'),
            ]
            ax_wheel.legend(handles=leg_h, loc='lower left', fontsize=7,
                           facecolor='#0a0a20', labelcolor='white',
                           edgecolor='#333355', framealpha=0.88)

            ax_wheel.text(0, -0.24, f'Ω_ZS = {OMEGA_ZS}  (Lambert W₀(1))',
                         ha='center', color='gold', fontsize=9, style='italic')
            ax_wheel.text(0, -0.36, '84 zero-divisor callosum channels',
                         ha='center', color='#00aacc', fontsize=7.5)
            ax_wheel.text(0, -0.48, 'W, Z bosons = sedenion zero-divisors at D*=1',
                         ha='center', color='#666688', fontsize=7)

            # ── PANEL 2: RH Critical Strip ──────────────────────────────────
            ax_zeros.set_title('Riemann Critical Strip', fontsize=9)
            ax_zeros.set_xlabel('σ (real part)', fontsize=7)
            ax_zeros.set_ylabel('t (imaginary part)', fontsize=7)
            ax_zeros.set_xlim(0.0, 1.0)
            ax_zeros.set_ylim(0, 82)

            ax_zeros.axvspan(0.0, 1.0, alpha=0.06, color='navy')
            ax_zeros.axvline(0.0, color='#334466', lw=1.0, alpha=0.7)
            ax_zeros.axvline(1.0, color='#334466', lw=1.0, alpha=0.7)
            ax_zeros.axvline(0.5, color='gold', lw=1.6, alpha=0.90,
                            label='σ=½  critical line')
            ax_zeros.axvline(OMEGA_ZS, color='gold', lw=0.7,
                            linestyle=':', alpha=0.45)
            ax_zeros.text(OMEGA_ZS+0.01, 79.5, 'Ω_ZS',
                         color='gold', fontsize=6, alpha=0.75)

            for i, gamma in enumerate(_RIEMANN_ZEROS):
                ax_zeros.plot(0.5, gamma, 'o', color='gold',
                             markersize=4.5, alpha=0.88, zorder=5)
                if i < 6:
                    ax_zeros.text(0.54, gamma, f'γ_{i+1}={gamma:.3f}',
                                 color='#aaaacc', fontsize=5.5, va='center')

            # Spiral arcs between consecutive zeros
            for i in range(len(_RIEMANN_ZEROS) - 1):
                g0 = _RIEMANN_ZEROS[i]
                g1 = _RIEMANN_ZEROS[i+1]
                xm = 0.5 + (0.14 if i % 2 == 0 else -0.14)
                ax_zeros.plot([0.5, xm, 0.5], [g0, (g0+g1)/2, g1],
                             color='#0099cc', lw=0.7, alpha=0.45)

            OMEGA_TIME = math.pi / math.log(2)
            ax_zeros.axhline(OMEGA_TIME, color='cyan', lw=0.9,
                            linestyle='--', alpha=0.55)
            ax_zeros.text(0.55, OMEGA_TIME+0.9,
                         f'Ω={OMEGA_TIME:.3f}', color='cyan', fontsize=6)

            ax_zeros.legend(loc='upper left', fontsize=6.5,
                           facecolor='#0a0a20', labelcolor='white',
                           edgecolor='#333355', framealpha=0.82)

            # ── PANEL 3: Gauge Coupling Unification ─────────────────────────
            ax_couple.set_title('Gauge Coupling Unification', fontsize=9)
            ax_couple.set_xlabel('log₁₀(E / E_EW)', fontsize=7)
            ax_couple.set_ylabel('1/α', fontsize=7)

            _L10 = math.log(10)
            x_arr = np.linspace(0.0, 16.0, 400)
            inv_em     = 98.40  + (-0.653) * _L10 * x_arr
            inv_weak   = 29.59  + ( 0.504) * _L10 * x_arr
            inv_strong =  8.470 + ( 1.114) * _L10 * x_arr

            ax_couple.plot(x_arr, inv_em,     color='#ffee00', lw=1.5,
                          label='α⁻¹_EM')
            ax_couple.plot(x_arr, inv_weak,   color='#44dd88', lw=1.5,
                          label='α⁻¹_weak')
            ax_couple.plot(x_arr, inv_strong, color='#ff4444', lw=1.5,
                          label='α⁻¹_strong')

            # GUT convergence window
            ax_couple.axvspan(13.0, 15.0, alpha=0.08, color='white')
            ax_couple.text(13.2, 6, 'GUT\nwindow',
                          color='white', fontsize=5.5, va='bottom', alpha=0.72)
            ax_couple.axvline(15.5, color='cyan', lw=0.7,
                             linestyle='--', alpha=0.50)
            ax_couple.text(15.0, 95,
                          'E_P\nalgebraic\nunification',
                          color='cyan', fontsize=5, ha='center', alpha=0.82)

            ax_couple.set_xlim(0, 16)
            ax_couple.set_ylim(0, 110)
            ax_couple.legend(loc='upper right', fontsize=6.5,
                            facecolor='#0a0a20', labelcolor='white',
                            edgecolor='#333355', framealpha=0.82)

            # ── PANEL 4: UNS Radar ──────────────────────────────────────────
            ax_uns.set_title('UNS Position  (16D)', color='white',
                            fontsize=9, pad=10)
            ax_uns.set_theta_offset(math.pi / 2)
            ax_uns.set_theta_direction(-1)

            N = 16
            θ_uns = [2*math.pi*k/N for k in range(N)] + [0]
            r_uns = list(uns) + [uns[0]]
            r_ref = [1.0/N] * (N+1)

            ax_uns.plot(θ_uns, r_uns, color='cyan', lw=1.6, alpha=0.88)
            ax_uns.fill(θ_uns, r_uns, color='cyan', alpha=0.13)
            ax_uns.plot(θ_uns, r_ref, color='#444466',
                       lw=0.8, linestyle='--', alpha=0.60)

            ax_uns.set_xticks([2*math.pi*k/N for k in range(N)])
            ax_uns.set_xticklabels([f'e{k}' for k in range(N)], fontsize=5)
            ax_uns.set_ylim(0, max(max(uns)*1.28, 0.11))
            ax_uns.yaxis.set_visible(False)
            ax_uns.spines['polar'].set_color('#333355')
            ax_uns.grid(color='#1a1a33', alpha=0.72)

            peak_k = uns.index(max(uns))
            peak_v = max(uns)
            dom = ('uniform equilibrium' if abs(peak_v - 1/16) < 0.0005
                   else f'e{peak_k}  {_OP[peak_k]}')
            ax_uns.text(0.5, -0.10, f'dominant: {dom}',
                       transform=ax_uns.transAxes,
                       ha='center', color='cyan', fontsize=7)

            # ── PANEL 5: Cosmology Summary ───────────────────────────────────
            ax_cosmo.set_title('Cosmology from Sedenion Geometry', fontsize=9)
            ax_cosmo.axis('off')

            _LN2  = math.log(2)
            _LN5  = math.log(5)
            _LN10 = math.log(10)
            # 10 = 2 × 5 — prime factorisation of base-10
            _OmM  = _LN2 / _LN10          # log₁₀(2) ≈ 0.30103  matter (first 𝕆)
            _OmL  = _LN5 / _LN10          # log₁₀(5) ≈ 0.69897  dark energy (second 𝕆 + vacuum)
            _OmB  = _LN2 / (7 * _LN10)    # Ω_m/7 ≈ 0.04300    baryons (1 EM generator)
            _OmDM = 6*_LN2 / (7 * _LN10)  # 6Ω_m/7 ≈ 0.25803   dark matter (6 non-EM)

            cosmo_rows = [
                ('Ω_Λ = log₁₀(5)',    f'{_OmL:.5f}', 'gold',    'obs 0.689  (1.4%)'),
                ('Ω_m = log₁₀(2)',    f'{_OmM:.5f}', '#44dd88', 'obs 0.311  (3.4%)'),
                ('Ω_b = Ω_m/7',       f'{_OmB:.5f}', '#88cc88', 'obs 0.049  (12%)'),
                ('Ω_dm = 6Ω_m/7',     f'{_OmDM:.5f}','#00aacc', 'obs 0.262  (1.5%)'),
                ('Ω_total',           '1.00000',      'white',   'log₁₀(10)=1 ✓'),
                ('BAO  ℓ₁',           '225.2',        'gold',    'obs 220  (2.4%)'),
                ('n_s  spectral',     '0.9667',       '#00ccff', 'obs 0.9649 ✓'),
                ('w  dark energy',    f'{-_OmL:.5f}', 'gold',    '(1+w)=Ω_m  dual'),
                ('void fill',         '~80%',         '#00aacc', '84 callosum ch.'),
            ]
            ax_cosmo.text(0.5, 0.99, '10 = 2 × 5  →  log₁₀(2) + log₁₀(5) = 1',
                         ha='center', va='top', transform=ax_cosmo.transAxes,
                         color='gold', fontsize=7.5, fontweight='bold')
            rh = 0.096
            for i, (lbl, val, vcol, note) in enumerate(cosmo_rows):
                y = 0.89 - i*rh
                ax_cosmo.text(0.01, y, lbl, transform=ax_cosmo.transAxes,
                             color='#777799', fontsize=6.5, va='top')
                ax_cosmo.text(0.52, y, val, transform=ax_cosmo.transAxes,
                             color=vcol, fontsize=7, va='top',
                             fontweight='bold')
                if note:
                    ax_cosmo.text(0.77, y, note,
                                 transform=ax_cosmo.transAxes,
                                 color='#555577', fontsize=5.5, va='top')

            # ── Title ────────────────────────────────────────────────────────
            fig.suptitle(
                f'HOLCUS — SELF PORTRAIT    '
                f'Ω_ZS={OMEGA_ZS}   GAP={GAP}   σ_crit=½   '
                f'{time.strftime("%Y-%m-%dT%H:%M:%S")}',
                color='white', fontsize=11, fontweight='bold', y=0.975,
            )

            plt.savefig(output_path, dpi=120, bbox_inches='tight',
                        facecolor=BG)
            plt.close(fig)
            return output_path

        except ImportError:
            return None
        except Exception:
            return None


class HamiltonianReport:
    """
    Ptolemy's 'My Location' function.

    Reads engine state, extracts Universal Native Space coordinates (16D
    sedenion projection), and generates a formatted diagnostic report.
    Writes UNS and field state to .ptolrc [hamiltonian] section.

    The UNS vector is the L1-normalized per-dimension sum of |beta| across
    all vocabulary words assigned to that sedenion dimension (k % 16).
    This is the center-of-mass of the current semantic state in 16D.

    :param engine: Engine instance.
    :param config: PtolConfig instance.
    :param sensors: SensorArray instance.
    """

    def __init__(self, engine, config, sensors=None):
        self._engine  = engine
        self._config  = config
        self._sensors = sensors

    def uns_coords(self) -> List[float]:
        """
        Extract 16-component Universal Native Space vector.
        uns[k] = sum of |beta[i]| for all i where i % 16 == k,
        then L1-normalized so sum(uns) == 1.0.

        :returns: 16-component UNS vector.
        :rtype: list
        """
        c   = self._engine.crank
        uns = [0.0] * 16
        for i in range(c.n):
            uns[i % 16] += abs(c._beta[i])
        total = sum(uns) or 1.0
        return [v / total for v in uns]

    def field_state(self) -> dict:
        """
        Collect full field state for the report.

        :returns: Dict with uns, bao, field_health, noether, sigma_crit_dist, etc.
        :rtype: dict
        """
        c   = self._engine.crank
        n   = c.n

        uns = self.uns_coords()

        bao_buf  = list(self._engine._bao_buf)
        bao_mean = sum(bao_buf) / len(bao_buf) if bao_buf else 0.0
        bao_delta = abs(bao_mean - OMEGA_ZS)
        field_health = max(0.0, 1.0 - bao_delta / 0.25)

        beta_vals = c._beta[:n] or [0.0]
        beta_mean = sum(beta_vals) / max(n, 1)

        # J_pos / J_neg totals (approximate — sum across all vocab)
        j_pos_total = sum(b * e**2 for b, e in zip(c._beta[:n], c._E[:n]))
        j_neg_total = sum((1.0 - b) * e**2 for b, e in zip(c._beta[:n], c._E[:n]))
        j_total     = j_pos_total + j_neg_total or 1.0

        # Sigma_crit proximity: beta_mean vs 0.5
        sigma_dist = abs(beta_mean - SIGMA_CRIT)

        # GAP proximity: min(beta) vs GAP
        min_beta  = min(beta_vals) if beta_vals else 0.0
        gap_prox  = abs(min_beta - GAP)

        # Noether violation
        noether = self._engine.noether_violation()

        # DTC codes
        dtcs = list(self._engine._dtcs[-10:])
        if bao_delta > 0.25:
            dtcs.append('P0087')
        if n == 0:
            dtcs.append('P0340')

        return {
            'uns':           uns,
            'bao_mean':      bao_mean,
            'bao_delta':     bao_delta,
            'field_health':  field_health,
            'beta_mean':     beta_mean,
            'j_pos_ratio':   j_pos_total / j_total,
            'j_neg_ratio':   j_neg_total / j_total,
            'sigma_crit_dist': sigma_dist,
            'on_critical_line': sigma_dist < 0.05,
            'gap_proximity': gap_prox,
            'at_gap':        gap_prox < 0.0001,
            'noether_violation': noether,
            'vocab_size':    n,
            'word_count':    self._engine._word_count,
            'segfaults':     self._engine._segfaults,
            'dtcs':          list(dict.fromkeys(dtcs)),
            'version':       self._engine.version,
            'timestamp':     time.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    def write_to_ptolrc(self, state: dict = None):
        """
        Write UNS coordinates and field state to .ptolrc [hamiltonian] section.
        Also writes [sedenion] section with current operator activations.

        :param state: Pre-computed field state dict. If None, computes fresh.
        """
        if state is None:
            state = self.field_state()

        ts = state['timestamp']
        self._config.set_ptolrc('hamiltonian', 'report_time',   ts)
        self._config.set_ptolrc('hamiltonian', 'field_health',  f"{state['field_health']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'bao_mean',      f"{state['bao_mean']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'bao_delta',     f"{state['bao_delta']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'j_pos',         f"{state['j_pos_ratio']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'j_neg',         f"{state['j_neg_ratio']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'sigma_crit_dist', f"{state['sigma_crit_dist']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'noether',       f"{state['noether_violation']:.6f}")
        self._config.set_ptolrc('hamiltonian', 'vocab_size',    str(state['vocab_size']))
        self._config.set_ptolrc('hamiltonian', 'dtcs',          ' '.join(state['dtcs']))

        for k, v in enumerate(state['uns']):
            self._config.set_ptolrc('sedenion', f'e{k}_{_OP[k]}', f"{v:.6f}")

    def render_text(self, state: dict = None, width: int = 62) -> str:
        """
        Generate the formatted Hamiltonian Report text.

        :param state: Pre-computed state dict. If None, computes fresh.
        :param width: Report box width.
        :returns: Multi-line report string.
        :rtype: str
        """
        if state is None:
            state = self.field_state()

        W   = width
        sep = '=' * W
        mid = '-' * W
        uns = state['uns']

        def row(label, value, width=W):
            label = str(label)
            value = str(value)
            pad   = width - len(label) - len(value) - 4
            return f"| {label}{' ' * max(pad, 1)}{value} |"

        lines = []
        lines.append(sep)
        title = f"PTOLEMY HAMILTONIAN REPORT  {state['timestamp']}"
        lines.append(f"|{title:^{W - 2}}|")
        lines.append(sep)

        lines.append(f"|{'UNIVERSAL NATIVE SPACE COORDINATES':^{W - 2}}|")
        lines.append(mid)
        for k in range(0, 16, 2):
            op0 = f"e{k:2d} {_OP[k]:13s} {uns[k]:.4f}"
            op1 = f"e{k+1:2d} {_OP[k+1]:13s} {uns[k+1]:.4f}"
            line = f"  {op0}    {op1}"
            lines.append(f"|{line:<{W - 2}}|")
        lines.append(sep)

        lines.append(f"|{'FIELD HEALTH':^{W - 2}}|")
        lines.append(mid)
        bao_bar = ('OK' if state['bao_delta'] < 0.05 else
                   'COAXING' if state['bao_delta'] < 0.25 else 'FAULT P0087')
        lines.append(row(f"BAO mean",
                         f"{state['bao_mean']:.5f}  target={OMEGA_ZS}  [{bao_bar}]"))
        lines.append(row("Field health",
                         f"{state['field_health']:.4f}  "
                         f"{'|' * int(state['field_health'] * 20):<20s}"))
        sigma_str = ('ON CRITICAL LINE' if state['on_critical_line']
                     else f"off by {state['sigma_crit_dist']:.4f}")
        lines.append(row(f"sigma=1/2 (crit line)", sigma_str))
        gap_str   = ('AT GROUND STATE' if state['at_gap']
                     else f"gap_prox={state['gap_proximity']:.6f}")
        lines.append(row("Yang-Mills gap", gap_str))
        lines.append(row("Noether violation", f"{state['noether_violation']:.6f}"))
        lines.append(sep)

        lines.append(f"|{'NOETHER CURRENTS':^{W - 2}}|")
        lines.append(mid)
        lines.append(row("J_pos (Riemann / response)", f"{state['j_pos_ratio']:.4f}"))
        lines.append(row("J_neg (Fermat  / prompt)",   f"{state['j_neg_ratio']:.4f}"))
        lines.append(row("J_total",                    "1.0000 (conserved)"))
        lines.append(sep)

        lines.append(f"|{'ENGINE STATUS':^{W - 2}}|")
        lines.append(mid)
        lines.append(row("Version",    state['version']))
        lines.append(row("Vocabulary", f"{state['vocab_size']:,} words"))
        lines.append(row("Words fired", f"{state['word_count']:,}"))
        lines.append(row("Segfaults",  str(state['segfaults'])))
        dtc_str = ' '.join(state['dtcs']) if state['dtcs'] else 'none'
        lines.append(row("DTC codes",  dtc_str))
        lines.append(sep)

        return '\n'.join(lines)

    def print_report(self):
        """Compute state, render text, write to .ptolrc, print to stdout."""
        state = self.field_state()
        print(self.render_text(state))
        self.write_to_ptolrc(state)
