#!/usr/bin/env python3
"""
rotary_boxkite_window.py — the conversation window for RotaryBoxKiteMonad.

Cody, 2026-08-25: "the old pre-harness window UI is fine for this job." This
reuses holcus_window.py's chrome directly — three-panel layout, same render
loop, same input handling — rewired to RotaryBoxKiteMonad instead of
monad.py's Engine, and to the walk-with-me disambiguation flow dropped
entirely (that was Engine/walkwithme_monad-specific; this Monad doesn't ask,
it answers).

  ┌────────────────────┬──────────────────────────────────┬─────────────┐
  │ HELP (hidden, ^B)   │ ROTARY BOXKITE                    │  ARTIFACTS  │
  │─────────────────────│──────────────────────────────────│─────────────│
  │ commands:           │ You: the engine contains sixteen  │ direction:  │
  │  /help              │      distinct operators           │  enumerate  │
  │  /diag <n>          │                                    │             │
  │  /clear /quit       │      Monad: it includes generator, │ (diag>=2)   │
  │ diagnostic levels:  │      function, and large integer.  │ sigma in/out│
  │  0 response only    │                                    │ trochoid    │
  │  1 + direction      │                                    │ struts      │
  │  2 + sigma/struts   │                                    │             │
  │  3 + full exchange  │                                    │ (diag>=3)   │
  ├─────────────────────┴──────────────────────────────────┴─────────────┤
  │ > _                                                                   │
  ├────────────────────────────────────────────────────────────────────────┤
  │ ^X Quit  ^B Help  ^P Art  ^L Clear                                    │
  └────────────────────────────────────────────────────────────────────────┘

Primary function is input -> output (Cody): type a sentence, see the
response — that's the whole point of this window. Everything else — /help,
diagnostic verbosity — lives in the help sidebar, HIDDEN BY DEFAULT, toggled
with ^B. Diagnostic level gates how much the artifacts sidebar shows; it
does not gate the chat itself, which always just shows You/Monad.

Usage:
    python3 rotary_boxkite_window.py
"""

import curses
import os
import sys
import textwrap
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rotary_rerun_boxkite_monad import RotaryBoxKiteMonad, Encounter
from harness import Harness
from wordnet_boxkite import RELATION_METHODS

TITLE = "ROTARY BOXKITE"
LEFT_W  = 22   # help / diagnostic-level sidebar
RIGHT_W = 20   # artifacts sidebar

SHORTCUT_BAR = "^X Quit  ^B Help  ^P Art  ^L Clear   Up/Down scroll"

HELP_LINES = [
    "commands:",
    " /help       this panel",
    " /diag <n>   diag level 0-3",
    " /art        list sections",
    " /art <name> toggle 1 on/off",
    " /art all    all on",
    " /art none   all off",
    " /clear      clear chat",
    " /quit       quit",
    "",
    "keys:",
    " ^X quit",
    " ^B toggle this panel",
    " ^P toggle artifacts",
    " ^L clear chat",
    " Up/Down scroll",
    "",
    "diag LEVEL (coarse):",
    " 0  response only",
    " 1  + selector",
    " 2  + sigma/trochoid/",
    "    struts/decompose/",
    "    repass",
    " 3  + root ctx/",
    "    candidates",
    "",
    "artifact SECTIONS",
    "(toggle live, /art):",
    " direction  (>=0)",
    " selector   (>=1)",
    " sigma      (>=2)",
    " trochoid   (>=2)",
    " struts     (>=2)",
    " decompose  (>=2)",
    " repass     (>=2)",
    " root_ctx   (>=3)",
    " candidates (>=3)",
    "shows iff toggle ON",
    " AND diag >= its min.",
]

# ── Colour pairs ─────────────────────────────────────────────────────────
C_TITLE  = 1
C_LEFT   = 2
C_RIGHT  = 3
C_YOU    = 4
C_MONAD  = 5
C_STATUS = 7
C_INPUT  = 8
C_BORDER = 9


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(C_TITLE,  curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(C_LEFT,   curses.COLOR_CYAN,   bg)
    curses.init_pair(C_RIGHT,  curses.COLOR_YELLOW, bg)
    curses.init_pair(C_YOU,    curses.COLOR_WHITE,  bg)
    curses.init_pair(C_MONAD,  curses.COLOR_GREEN,  bg)
    curses.init_pair(C_STATUS, curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(C_INPUT,  curses.COLOR_WHITE,  bg)
    curses.init_pair(C_BORDER, curses.COLOR_CYAN,   bg)


class Msg:
    __slots__ = ('role', 'text')
    def __init__(self, role: str, text: str):
        self.role = role   # 'you' | 'monad' | 'status'
        self.text = text

    def label(self):
        if self.role == 'you':   return "You:"
        if self.role == 'monad': return "Monad:"
        return ""

    def color(self):
        if self.role == 'you':   return C_YOU
        if self.role == 'monad': return C_MONAD
        return C_STATUS


class Artifacts:
    """Real fields off the last Encounter. Two independent gates, both
    LIVE (re-read every render): the diagnostic LEVEL (0-3, coarse) and
    per-SECTION on/off toggles. Data is always computed; only DISPLAY is
    gated -- turning a section off, or dropping diag level, takes effect
    on the next frame, no new input required.

    Each section carries its minimum diag level; a section shows iff
    (its toggle is on) AND (diag_level >= its minimum)."""

    # name -> (label, minimum diag level)
    SECTIONS = [
        ('direction',  ('direction',   0)),
        ('selector',   ('selector',    1)),
        ('sigma',      ('sigma',       2)),
        ('trochoid',   ('trochoid',    2)),
        ('struts',     ('struts',      2)),
        ('decompose',  ('decompose',   2)),   # pruned schema groups
        ('repass',     ('repass',      2)),   # Mind's Eye coverage
        ('root_ctx',   ('root ctx',    3)),
        ('candidates', ('candidates',  3)),
    ]

    def __init__(self):
        self.direction = '—'
        self.selector = '—'
        self.sigma_in = self.sigma_out = 0.0
        self.trochoid_in = self.trochoid_out = 0.0
        self.lit_in: list = []
        self.lit_out: list = []
        self.shared: list = []
        self.root_nonzero: dict = {}
        self.words_out: list = []
        self.pruned: dict = {}
        self.repass: dict = {}
        # per-section toggles — all on by default
        self.enabled = {name: True for name, _ in self.SECTIONS}

    def toggle(self, name: str) -> Optional[bool]:
        """Flip one section. Returns its new state, or None if unknown."""
        if name not in self.enabled:
            return None
        self.enabled[name] = not self.enabled[name]
        return self.enabled[name]

    def off_sections(self) -> list:
        return [n for n in self.enabled if not self.enabled[n]]

    def update(self, enc: Encounter) -> None:
        self.direction = enc.direction
        self.selector = getattr(enc, 'selector', '—')
        self.sigma_in = enc.snapshot['sigma_self']
        self.sigma_out = enc.snapshot_out['sigma_self']
        self.trochoid_in = enc.snapshot['trochoid_loss']
        self.trochoid_out = enc.snapshot_out['trochoid_loss']
        self.lit_in = enc.lit_struts_in
        self.lit_out = enc.lit_struts_out
        self.shared = enc.shared_struts
        self.root_nonzero = {RELATION_METHODS[i]: c
                             for i, c in enumerate(enc.root_vector) if c}
        self.words_out = enc.words_out
        self.pruned = getattr(enc, 'pruned', {}) or {}
        self.repass = getattr(enc, 'repass', {}) or {}

    def _show(self, name: str, diag_level: int) -> bool:
        lvl = dict((n, m) for n, (_, m) in self.SECTIONS)[name]
        return self.enabled.get(name, True) and diag_level >= lvl

    def lines(self, width: int, diag_level: int) -> list:
        w = max(4, width - 2)
        out: list = []
        if self._show('direction', diag_level):
            out += ["direction:", f" {self.direction}"]
        if self._show('selector', diag_level):
            out += ["selector:", f" {self.selector}"]
        if self._show('sigma', diag_level):
            out += ["─" * w,
                    f"sigma in:  {self.sigma_in:.4f}",
                    f"sigma out: {self.sigma_out:.4f}"]
        if self._show('trochoid', diag_level):
            out += [f"troch in:  {self.trochoid_in:.4f}",
                    f"troch out: {self.trochoid_out:.4f}"]
        if self._show('struts', diag_level):
            out += ["struts in:", f" {self.lit_in}",
                    "struts out:", f" {self.lit_out}",
                    "shared:", f" {self.shared}"]
        if self._show('decompose', diag_level):
            out += ["─" * w, "decompose:",
                    f" kept {self.pruned.get('kept', '—')}"
                    f" / dropped {self.pruned.get('dropped', '—')}"]
            for g in self.pruned.get('groups', []):
                if len(g) > 1:
                    out.append(f" {' + '.join(g)}"[:w])
        if self._show('repass', diag_level):
            cov = self.repass.get('coverage', {})
            out += ["repass:",
                    f" {cov.get('passes', '—')} passes /"
                    f" {cov.get('frames', '—')} frames",
                    f" complete={cov.get('complete', '—')}"]
            if cov.get('unrefined'):
                out.append(f" bare: {cov['unrefined']}"[:w])
        if self._show('root_ctx', diag_level):
            out += ["─" * w, "root ctx:"]
            for k, v in self.root_nonzero.items():
                out.append(f" {k}={v}"[:w])
        if self._show('candidates', diag_level):
            out.append("candidates:")
            for cw in self.words_out:
                out.append(f" {cw}"[:w])
        return out


class RotaryBoxKiteWindow:
    def __init__(self, monad: RotaryBoxKiteMonad):
        self.monad = monad
        self.chat: list = []
        self.artifacts = Artifacts()
        self.diag_level = 0

        self.input_buf: list = []
        self.input_pos = 0
        self.chat_scroll = 0

        self.show_left  = False   # help sidebar — hidden by default
        self.show_right = True    # artifacts sidebar — visible, gated by diag_level

    # ── Monad plugin ────────────────────────────────────────────────────

    def _monad_turn(self, user_text: str) -> list:
        enc = self.monad.process_input(user_text)
        self.artifacts.update(enc)
        return [Msg('monad', enc.response)]

    # ── Render — ported from holcus_window.py, three-panel chrome ───────

    def _addstr_safe(self, win, y, x, text, attr=0):
        rows, cols = win.getmaxyx()
        if y < 0 or y >= rows or x < 0 or x >= cols:
            return
        max_len = cols - x - 1
        if max_len <= 0:
            return
        try:
            win.addstr(y, x, str(text)[:max_len], attr)
        except curses.error:
            pass

    def _render(self, stdscr):
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()

        if rows < 8 or cols < 24:
            stdscr.addstr(0, 0, "Terminal too small.")
            stdscr.refresh()
            return

        lw = LEFT_W if self.show_left else 0
        rw = RIGHT_W if self.show_right else 0
        cw = cols - lw - rw
        if cw < 10:
            lw = 0; rw = 0; cw = cols

        title_row = 0
        content_h = rows - 3
        input_row = rows - 2
        short_row = rows - 1
        chat_h    = content_h - 1

        # ── Title bar ─────────────────────────────────────────────────
        diag_str  = f"diag={self.diag_level}"
        title_line = f" {TITLE}"
        pad = cols - len(title_line) - len(diag_str) - 2
        title_full = title_line + " " * max(1, pad) + diag_str + " "
        self._addstr_safe(stdscr, title_row, 0, title_full[:cols],
                          curses.color_pair(C_TITLE))

        # ── Left sidebar (help) ──────────────────────────────────────
        if lw > 0:
            cp_l = curses.color_pair(C_LEFT)
            for r in range(1, content_h):
                self._addstr_safe(stdscr, r, 0, " " * (lw - 1), cp_l)
                self._addstr_safe(stdscr, r, lw - 1, "│", curses.color_pair(C_BORDER))
            self._addstr_safe(stdscr, 1, 1, "Help"[:lw - 2], cp_l | curses.A_BOLD)
            self._addstr_safe(stdscr, 2, 1, "─" * (lw - 2), cp_l)
            for i, line in enumerate(HELP_LINES):
                r = 3 + i
                if r >= content_h: break
                self._addstr_safe(stdscr, r, 1, line[:lw - 2], cp_l)

        # ── Right sidebar (artifacts) ────────────────────────────────
        if rw > 0:
            cp_r = curses.color_pair(C_RIGHT)
            rx = cols - rw
            for r in range(1, content_h):
                self._addstr_safe(stdscr, r, rx, " " * (rw - 1), cp_r)
            self._addstr_safe(stdscr, 1, rx, "│", curses.color_pair(C_BORDER))
            self._addstr_safe(stdscr, 1, rx + 1, "Artifacts"[:rw - 2], cp_r | curses.A_BOLD)
            self._addstr_safe(stdscr, 2, rx + 1, "─" * (rw - 2), cp_r)
            art_lines = self.artifacts.lines(rw, self.diag_level)
            for i, line in enumerate(art_lines):
                r = 3 + i
                if r >= content_h: break
                self._addstr_safe(stdscr, r, rx + 1, line[:rw - 2], cp_r)
                self._addstr_safe(stdscr, r, rx, "│", curses.color_pair(C_BORDER))

        # ── Chat area ─────────────────────────────────────────────────
        rendered = []
        for msg in self.chat:
            cp = curses.color_pair(msg.color())
            attr = curses.A_BOLD if msg.role in ('you', 'monad') else 0
            label = msg.label()
            lines = (msg.text or '').splitlines() or ['']
            first_text = f"  {label} {lines[0]}" if label else f"  {lines[0]}"
            for wl in (textwrap.wrap(first_text, max(1, cw - 2)) or [first_text]):
                rendered.append((wl, cp, attr))
            for l in lines[1:]:
                continuation = f"    {l}"
                for wl in (textwrap.wrap(continuation, max(1, cw - 2)) or [continuation]):
                    rendered.append((wl, cp, 0))
            rendered.append(('', curses.color_pair(C_YOU), 0))

        total = len(rendered)
        start = max(0, total - chat_h - self.chat_scroll)
        view = rendered[start:start + chat_h]
        cx_off = lw

        for i, (line, cp, attr) in enumerate(view):
            r = 1 + i
            if r >= content_h: break
            self._addstr_safe(stdscr, r, cx_off, line[:cw - 1], cp | attr)

        # ── Divider + input + shortcut bar ──────────────────────────────
        self._addstr_safe(stdscr, content_h, 0, "─" * (cols - 1), curses.color_pair(C_BORDER))

        prefix = "> "
        ibuf = "".join(self.input_buf)
        iline = prefix + ibuf
        if len(iline) >= cols - 1:
            iline = iline[-(cols - 2):]
        self._addstr_safe(stdscr, input_row, 0, iline.ljust(cols - 1), curses.color_pair(C_INPUT))
        cursor_x = len(prefix) + self.input_pos
        if cursor_x < cols - 1:
            stdscr.move(input_row, cursor_x)

        bar = SHORTCUT_BAR[:cols - 1].ljust(cols - 1)
        self._addstr_safe(stdscr, short_row, 0, bar, curses.color_pair(C_STATUS))

        stdscr.refresh()

    # ── Input handling — ported from holcus_window.py ────────────────────

    def _handle_key(self, key) -> bool:
        if key in (curses.KEY_ENTER, 10, 13):
            text = "".join(self.input_buf).strip()
            self.input_buf.clear()
            self.input_pos = 0
            if text:
                self._submit(text)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if self.input_pos > 0:
                del self.input_buf[self.input_pos - 1]
                self.input_pos -= 1
        elif key == curses.KEY_DC:
            if self.input_pos < len(self.input_buf):
                del self.input_buf[self.input_pos]
        elif key == curses.KEY_LEFT:
            self.input_pos = max(0, self.input_pos - 1)
        elif key == curses.KEY_RIGHT:
            self.input_pos = min(len(self.input_buf), self.input_pos + 1)
        elif key == curses.KEY_HOME:
            self.input_pos = 0
        elif key == curses.KEY_END:
            self.input_pos = len(self.input_buf)
        elif key == curses.KEY_UP:
            self.chat_scroll += 3
        elif key == curses.KEY_DOWN:
            self.chat_scroll = max(0, self.chat_scroll - 3)
        elif key == 24:   # ^X — quit
            return False
        elif key == 2:    # ^B — toggle help sidebar
            self.show_left = not self.show_left
        elif key == 16:   # ^P — toggle artifacts sidebar
            self.show_right = not self.show_right
        elif key == 12:   # ^L — clear chat
            self._submit('/clear')
        elif isinstance(key, int) and 32 <= key <= 126:
            self.input_buf.insert(self.input_pos, chr(key))
            self.input_pos += 1
        return True

    def _submit(self, text: str):
        if text in ('/quit', '/exit'):
            raise SystemExit(0)

        if text == '/clear':
            self.chat.clear()
            self.chat_scroll = 0
            return

        if text == '/help':
            self.show_left = True
            return

        if text.startswith('/diag'):
            arg = text[len('/diag'):].strip()
            if arg.isdigit():
                self.diag_level = max(0, min(3, int(arg)))
                self.chat.append(Msg('status', f"diagnostic level -> {self.diag_level}"))
            else:
                self.chat.append(Msg('status', "usage: /diag <0-3>"))
            self.chat_scroll = 0
            return

        if text.startswith('/art'):
            arg = text[len('/art'):].strip().lower()
            if not arg:
                on  = [n for n in self.artifacts.enabled if self.artifacts.enabled[n]]
                off = self.artifacts.off_sections()
                self.chat.append(Msg('status', f"artifacts ON:  {', '.join(on) or '(none)'}"))
                self.chat.append(Msg('status', f"artifacts OFF: {', '.join(off) or '(none)'}"))
            elif arg in ('all', 'on'):
                for n in self.artifacts.enabled:
                    self.artifacts.enabled[n] = True
                self.chat.append(Msg('status', "all artifact sections ON"))
            elif arg in ('none', 'off'):
                for n in self.artifacts.enabled:
                    self.artifacts.enabled[n] = False
                self.chat.append(Msg('status', "all artifact sections OFF"))
            else:
                new = self.artifacts.toggle(arg)
                if new is None:
                    self.chat.append(Msg('status',
                        f"unknown section {arg!r} — /art to list"))
                else:
                    self.chat.append(Msg('status',
                        f"{arg} -> {'ON' if new else 'OFF'}"))
            self.chat_scroll = 0
            return   # returns to run() -> _render() this frame: LIVE

        # Normal conversation turn — input -> output, the primary job.
        self.chat.append(Msg('you', text))
        self.chat.extend(self._monad_turn(text))
        self.chat_scroll = 0

    # ── Main curses loop ─────────────────────────────────────────────────

    def run(self, stdscr):
        init_colors()
        curses.curs_set(1)
        stdscr.nodelay(False)
        stdscr.keypad(True)

        self.chat.append(Msg('status',
            "RotaryBoxKiteMonad ready. Type a sentence. /help for commands."))

        running = True
        while running:
            self._render(stdscr)
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                break
            running = self._handle_key(key)


def _install_silent_viewport(h: Harness) -> None:
    """The curses window already shows Encounter.response directly — it
    does not need harness.present()'s output. Without this, present()'s
    stdout fallback (no viewport registered) would print raw text over the
    curses display and corrupt it. This registers a real 'viewport' Face
    that does nothing, so present() routes here instead of stdout."""
    from harness import FaceResult
    h.toolset_registry.register(
        'window_sink', ['viewport'],
        lambda capability, action, **p: FaceResult(ok=True, handled_by='window_sink'))


def main():
    print("Building the Monad...", file=sys.stderr)
    h = Harness()
    _install_silent_viewport(h)
    monad = RotaryBoxKiteMonad(harness=h)
    if monad.box_kite is None:
        print(f"  [BoxKite unavailable: {monad._kite_error}]", file=sys.stderr)
    window = RotaryBoxKiteWindow(monad)

    try:
        curses.wrapper(window.run)
    except SystemExit:
        pass
    finally:
        # The sedenion window carries the write functionality for the
        # combined store: persist on exit whatever hear() deepened this
        # session. (Interval checkpointing from the render loop is a
        # follow-up; on-exit is the guarantee.)
        try:
            path = monad.checkpoint()
            if path:
                print(f"  [combined store checkpointed -> {path}]", file=sys.stderr)
        except Exception as exc:                       # recorded, not hidden
            print(f"  [checkpoint failed: {exc}]", file=sys.stderr)
    print("Rotary boxkite window closed.", file=sys.stderr)


if __name__ == '__main__':
    main()
