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
