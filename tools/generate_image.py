#!/usr/bin/env python3
"""
tools/generate_image.py — Generate a Holcus field portrait from a text prompt.

Drives the monad engine with the prompt to excite the field, then renders a
self_portrait() from the live field state. The prompt shapes what Holcus sees
and therefore what he draws.

Usage (from PtolC REPL via /generate):
    python3 tools/generate_image.py "surreal landscape with Riemann zeros"
    python3 tools/generate_image.py --bin monad_sedenion.bin "describe yourself"

Prints the output image path to stdout on success, error message to stderr on failure.
"""

import sys
import os
import argparse

# ── Path setup ────────────────────────────────────────────────────────────────
_SCRIPT  = os.path.abspath(__file__)
_TOOLS   = os.path.dirname(_SCRIPT)
_REPO    = os.path.dirname(_TOOLS)          # PtolemyHolcus/
_PTOL    = os.path.expanduser('~/.ptolemy')

sys.path.insert(0, _REPO)

# ── Candidate bin files (priority order) ─────────────────────────────────────
def _find_bin(override=None):
    candidates = []
    if override:
        candidates.append(override)
    candidates += [
        os.path.join(_PTOL, 'monad.bin'),
        os.path.join(_PTOL, 'monad_wordnet.bin'),
        os.path.join(_REPO, 'monad_sedenion.bin'),
        os.path.join(_REPO, 'monad_wordnet.bin'),
        os.path.join(_REPO, 'monad_english.bin'),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


def generate(prompt: str, bin_path: str = None, n_words: int = 24) -> str:
    """
    Drive the field with *prompt*, then render and save a self_portrait.

    Returns the absolute path of the generated PNG.
    Raises RuntimeError on failure.
    """
    from monad import Engine
    from skills.draw import PtolDraw

    engine = Engine()
    found  = _find_bin(bin_path)
    if found:
        engine.load_bin(found)
        n = engine.crank.n if hasattr(engine.crank, 'n') else '?'
        print(f'[generate] loaded {found}  vocab={n}', file=sys.stderr)
    else:
        print('[generate] no bin found — cold start', file=sys.stderr)

    # Drive the field with the prompt
    if prompt.strip():
        engine.crank.learn(prompt)
        try:
            result = engine.generate(prompt, n_words=n_words)
            field_resp = result.get('response', '')
            bao        = result.get('bao', 0.0)
            print(f'[generate] field response: {field_resp!r}  BAO={bao:.5f}',
                  file=sys.stderr)
        except Exception as e:
            print(f'[generate] generate() failed: {e}', file=sys.stderr)

    # Render
    draw = PtolDraw()
    path = draw.self_portrait(engine=engine)
    if not path:
        raise RuntimeError('PtolDraw.self_portrait() returned None — check matplotlib/PIL')

    return path


def main():
    ap = argparse.ArgumentParser(
        description='Generate a Holcus field portrait from a text prompt')
    ap.add_argument('prompt', nargs='*',
                    help='Text prompt (drives field before rendering)')
    ap.add_argument('--bin', '-b', default=None,
                    help='Explicit .bin path')
    ap.add_argument('--words', '-n', type=int, default=24,
                    help='Words to generate before rendering (default 24)')
    args = ap.parse_args()

    prompt = ' '.join(args.prompt) if args.prompt else ''

    try:
        path = generate(prompt, bin_path=args.bin, n_words=args.words)
        print(path)           # stdout: path for the REPL to display
    except Exception as e:
        print(f'[generate] ERROR: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
