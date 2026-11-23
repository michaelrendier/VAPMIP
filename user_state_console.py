#!/usr/bin/env python3
"""
user_state_console.py -- see the user's emotional state in a console, as a multi-scale slide rule.

Cody, 2026-11-22 ("emotional-console-idea.svg"): seven rulers, each a dark half and a light half, slid past ONE fixed cursor; what shows
through the cursor is the reading.  Inline: one cell per layer, a colour with a digit over it (0-9; 0 = black, no change).

    INLINE   V I B G Y O R | R O Y G B I V   +0.37          (15 cells: 7 dark, the cursor '|', 7 light, then e0)
    UPRIGHT  15 rows tall x 10 wide: one row per layer, the row's colour is the neurotransmitter, filled to its level, with a
             four-way line character ('┼') in the contrasting foreground; unfilled cells are black.
    A level dilutes the colour toward black (0) and saturates it toward the pure hue (9): a solution more or less concentrated.

ANSI truecolor (38;2 / 48;2).  Foreground contrast: light backgrounds get black text, dark backgrounds white.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from user_state import (LAYER_ORDER, LEVELS, NT, PALETTE, Reading, digits, net, scalar, code, sedenion)

RESET = '\x1b[0m'


def _rgb(layer: Tuple[str, str], level: int) -> Tuple[int, int, int]:
    """The layer's colour at a level: 0 -> black, 9 -> the pure palette colour (dark half or light half)."""
    if layer[1] == 'cursor':
        g = 60 + int(195 * level / (LEVELS - 1))
        return (g, g, g)
    base = PALETTE[layer[0]][0 if layer[1] == 'dark' else 1]
    f = 0.0 if level <= 0 else 0.3 + 0.7 * level / (LEVELS - 1)      # 0 stays black; level 1 is already visible
    return tuple(int(c * f) for c in base)


def _fg(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    lum = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return (0, 0, 0) if lum > 110 else (255, 255, 255)


def cell(text: str, rgb: Tuple[int, int, int]) -> str:
    fg = _fg(rgb)
    return f'\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m\x1b[38;2;{fg[0]};{fg[1]};{fg[2]}m{text}{RESET}'


def inline(r: Reading, with_scalar: bool = True) -> str:
    """The 15-cell strip: dark side V I B G Y O R, the cursor, light side R O Y G B I V.  Each cell shows its level digit."""
    d = digits(r)
    out = []
    for lay in LAYER_ORDER:
        if lay[1] == 'cursor':
            out.append(cell('|', (110, 110, 110)))
        else:
            lvl = d[lay]
            out.append(cell(str(lvl), _rgb(lay, lvl) if lvl else (0, 0, 0)))
    s = ''.join(out)
    if with_scalar:
        s += f' {scalar(r):+.2f}'
    return s


def upright(r: Reading) -> List[str]:
    """15 rows x 10 columns.  Row = layer (dark violet .. dark red, cursor, light red .. light violet); a row is filled to its level."""
    d = digits(r)
    rows = []
    for lay in LAYER_ORDER:
        if lay[1] == 'cursor':
            n = net(r)
            lvl = int(round(abs(n) * (LEVELS - 1) / 0.5)); lvl = min(LEVELS - 1, lvl)
            rgb = _rgb(lay, lvl or 0)
            row = ''.join(cell('┼' if i < lvl else ' ', rgb if i < lvl else (0, 0, 0)) for i in range(LEVELS))
            rows.append(row + f'  net {n:+.2f}')
            continue
        lvl = d[lay]
        rgb = _rgb(lay, lvl)
        row = ''.join(cell('┼' if i < lvl else ' ', rgb if i < lvl else (0, 0, 0)) for i in range(LEVELS))
        tag = f"{lay[0]:<4}{'−' if lay[1] == 'dark' else '+'}{lvl}"
        rows.append(row + '  ' + tag)
    return rows


def legend() -> str:
    parts = []
    for side, idx in (('dark', 0), ('light', 1)):
        order = list(reversed(NT)) if side == 'dark' else list(NT)
        parts.append(' '.join(cell(a[:3] if a != '5HT' else '5HT', PALETTE[a][idx]) for a in order))
    return 'dark: ' + parts[0] + '   |   light: ' + parts[1]


def ans_document(items: Iterable[Tuple[str, Reading, str]], title: str = 'User emotional state') -> str:
    """A .ans document: for each prompt a line with the inline strip and the prompt.  `items` = (text, reading, note)."""
    lines = [f'\x1b[1m{title}{RESET}', legend(), '',
             'layers: V I B G Y O R | R O Y G B I V   (dark side, cursor, light side)   digit = level 0-9, 0 = black = no change   '
             'order of colours = kite order = rainbow: OPI red, GLU orange, GABA yellow, DA green, 5HT blue, NE indigo, OXT violet',
             '']
    for text, r, note in items:
        t = ' '.join(text.split())
        t = t if len(t) <= 110 else t[:107] + '...'
        lines.append(f'{inline(r)}  {t}' + (f'  {note}' if note else ''))
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':          # a demonstration on the first state: the sample readings
    demo = Reading.zero()
    demo['DA'][1], demo['5HT'][1], demo['OXT'][1], demo['NE'][0], demo['GABA'][0] = .7, .55, .4, .3, .2
    print(legend()); print(inline(demo)); print('\n'.join(upright(demo)))
