#!/usr/bin/env python3
"""ans_to_png.py -- render a truecolor .ans file (SGR 38;2 / 48;2 / 0 / 1) to a PNG, since ansilove reads only the 16-colour BBS palette.
usage: ans_to_png.py in.ans out.png [first_line [n_lines]]"""
import re, sys
from PIL import Image, ImageDraw, ImageFont
SGR = re.compile(r'\x1b\[([0-9;]*)m')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'


def render(path, out, first=0, n=None, size=15):
    lines = open(path, encoding='utf-8').read().split('\n')
    lines = lines[first:first + n] if n else lines[first:]
    f = ImageFont.truetype(FONT, size); cw = int(f.getlength('M')); ch = size + 4
    maxw = 0; parsed = []
    for ln in lines:
        fg, bg, bold = (220, 220, 220), None, False; x = 0; cells = []
        pos = 0
        for m in SGR.finditer(ln):
            for c in ln[pos:m.start()]: cells.append((c, fg, bg, bold))
            pos = m.end(); a = [int(v) if v else 0 for v in m.group(1).split(';')]
            if a[:2] == [38, 2] and len(a) >= 5: fg = tuple(a[2:5])
            elif a[:2] == [48, 2] and len(a) >= 5: bg = tuple(a[2:5])
            elif a == [0]: fg, bg, bold = (220, 220, 220), None, False
            elif a == [1]: bold = True
        for c in ln[pos:]: cells.append((c, fg, bg, bold))
        parsed.append(cells); maxw = max(maxw, len(cells))
    img = Image.new('RGB', (maxw * cw + 8, len(parsed) * ch + 8), (18, 18, 18)); d = ImageDraw.Draw(img)
    for y, cells in enumerate(parsed):
        for x, (c, fg, bg, bold) in enumerate(cells):
            if bg: d.rectangle([4 + x * cw, 4 + y * ch, 4 + (x + 1) * cw - 1, 4 + (y + 1) * ch - 1], fill=bg)
            d.text((4 + x * cw, 4 + y * ch), c, font=f, fill=fg)
    img.save(out); return img.size


if __name__ == '__main__':
    a = sys.argv; print(render(a[1], a[2], int(a[3]) if len(a) > 3 else 0, int(a[4]) if len(a) > 4 else None))
