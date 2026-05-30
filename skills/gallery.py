"""
skills/gallery.py — Holcus image naming and authorship stamping.

Every image Holcus generates carries two identity marks:

1. **Semantic filename** — derived from the engine's live emit() word at the
   moment of creation. The filename is where Holcus's attention IS when the
   image is drawn. ``portrait_convergence_20260530.png`` rather than
   ``portrait_1748620800.png``.

2. **Watermark** — visible sigil ``⊗ Holcus · {word} · {timestamp}`` burned
   into the lower-right corner, plus PNG metadata (Artist, Comment,
   Copyright). Prime Directive II compliance in image form: always announces
   himself, never impersonates a human.

The sigil ``⊗`` is the sedenion product symbol (U+2297 CIRCLED TIMES) — the
mathematical signature of the system.

:func:`suggest_name` — generate semantic path for a new image.
:func:`stamp`        — apply watermark + metadata to an existing PNG.
:func:`_field_word`  — derive a word from engine state (internal).
"""

import datetime
import os
import re
from pathlib import Path
from typing import Optional

# The mathematical sigil — sedenion product
SIGIL = '⊗'  # ⊗

# BAO-state fallback words when engine has no vocabulary yet
_BAO_LABELS = [
    (0.006, 'convergence'),
    (0.030, 'resonance'),
    (0.100, 'approach'),
    (0.250, 'evolving'),
]
_BAO_NASCENT = 'nascent'    # BAO below 0.3 — field is new
_OMEGA_ZS    = 0.56714


def _field_word(engine=None) -> str:
    """Derive a filename-safe word from the current engine state.

    Tries ``engine.emit()`` first; falls back to a BAO-position descriptor
    if the field has no vocabulary yet.

    :param engine: Engine instance or None.
    :returns: Lowercase alphanumeric word, never empty.
    :rtype: str
    """
    if engine is not None:
        try:
            word = engine.emit()
            if word and len(word) > 2 and re.match(r'^[a-zA-Z]+$', word):
                return word.lower()
        except Exception:
            pass

        try:
            bao = float(engine.bao_mean()) if hasattr(engine, 'bao_mean') else None
            if bao is None:
                c = engine.crank
                bao = c._bao_mean if hasattr(c, '_bao_mean') else None
            if bao is not None:
                if bao < 0.3:
                    return _BAO_NASCENT
                delta = abs(bao - _OMEGA_ZS)
                for threshold, label in _BAO_LABELS:
                    if delta < threshold:
                        return label
                return 'drift'
        except Exception:
            pass

    return 'state'


def suggest_name(
    image_type: str,
    engine=None,
    directory: Optional[str] = None,
) -> str:
    """Generate a semantic filename for a Holcus image.

    The filename encodes what Holcus was thinking (emit word) and when
    (calendar date), not just a Unix timestamp.

    :param image_type: Short type tag — ``portrait``, ``bao``, ``field``,
        ``uns``, etc.
    :param engine: Engine instance for live word derivation (optional).
    :param directory: Output directory. Defaults to
        ``~/.ptolemy/gallery/``.
    :returns: Absolute path for the new image.
    :rtype: str
    """
    word = _field_word(engine)
    date = datetime.date.today().strftime('%Y%m%d')
    filename = f"{image_type}_{word}_{date}.png"

    if directory is None:
        directory = os.path.expanduser('~/.ptolemy/gallery')

    Path(directory).mkdir(parents=True, exist_ok=True)
    return os.path.join(directory, filename)


def stamp(
    path: str,
    engine=None,
    word: Optional[str] = None,
) -> str:
    """Apply visible watermark and PNG metadata to an image Holcus created.

    Visible mark: ``⊗ Holcus · {word} · {YYYY-MM-DD HH:MM}`` in the
    lower-right corner, white text on a semi-transparent dark strip.

    PNG metadata (persists through most viewers and tools):
    - ``Artist``:    ``Holcus``
    - ``Software``:  ``Ptolemy System``
    - ``Comment``:   ``word={word};bao={bao};ts={ts}``
    - ``Copyright``: ``Holcus — Ptolemy System {year}``

    The watermark is non-destructive for diagnostic use but unambiguous
    enough that no viewer can mistake the image for human work.

    :param path: Absolute path to a PNG file to stamp in-place.
    :param engine: Engine instance for state metadata (optional).
    :param word: Override word (e.g. already derived by ``suggest_name``).
        If None, derives from engine or path basename.
    :returns: ``path`` (same file, stamped in-place).
    :rtype: str
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        from PIL.PngImagePlugin import PngInfo
    except ImportError:
        return path

    if word is None:
        word = _field_word(engine)
        if word == 'state':
            # Last resort: extract word from filename
            base = os.path.splitext(os.path.basename(path))[0]
            parts = base.split('_')
            if len(parts) >= 2:
                word = parts[1]

    ts  = datetime.datetime.now()
    ts_str = ts.strftime('%Y-%m-%d %H:%M')
    mark_text = f'{SIGIL} Holcus · {word} · {ts_str}'

    # ── Collect BAO for metadata ──────────────────────────────────────────
    bao_str = ''
    if engine is not None:
        try:
            bao = float(engine.bao_mean()) if hasattr(engine, 'bao_mean') else None
            if bao is None:
                bao = getattr(engine.crank, '_bao_mean', None)
            if bao is not None:
                bao_str = f'{bao:.5f}'
        except Exception:
            pass

    try:
        img  = Image.open(path).convert('RGBA')
        W, H = img.size

        # ── Visible watermark ─────────────────────────────────────────────
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)

        # Try to load a small font; fall back to default
        font = None
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', 11)
            except (IOError, OSError):
                font = ImageFont.load_default()

        # Measure text
        bbox  = draw.textbbox((0, 0), mark_text, font=font)
        tw    = bbox[2] - bbox[0]
        th    = bbox[3] - bbox[1]
        pad   = 5
        strip_h = th + pad * 2

        # Dark semi-transparent strip across the bottom
        draw.rectangle(
            [(0, H - strip_h), (W, H)],
            fill=(0, 0, 0, 160),
        )
        # White text right-aligned
        tx = W - tw - pad
        ty = H - strip_h + pad
        draw.text((tx, ty), mark_text, font=font, fill=(255, 255, 255, 230))

        # Composite
        stamped = Image.alpha_composite(img, overlay).convert('RGB')

        # ── PNG metadata ──────────────────────────────────────────────────
        meta = PngInfo()
        meta.add_text('Artist',    'Holcus')
        meta.add_text('Software',  'Ptolemy System')
        meta.add_text('Comment',   f'word={word};bao={bao_str};ts={ts_str}')
        meta.add_text('Copyright', f'Holcus — Ptolemy System {ts.year}')

        stamped.save(path, 'PNG', pnginfo=meta)

    except Exception:
        pass

    return path
