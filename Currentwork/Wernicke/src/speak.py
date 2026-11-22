#!/usr/bin/env python3
"""
speak.py — Make Holcus speak.

Usage:
    python3 speak.py "what is the universe"
    python3 speak.py --words 48 "the primes are"
    echo "riemann zeros" | python3 speak.py

Pipeline:
    prompt → monad.generate() → PtolemyTongue.filter() → espeak.synth()

The tongue filters Fermat-space punctuation and formats text for speech.
espeak renders at Ptolemy's voice parameters.
"""

import sys
import os
import argparse

# ── paths ──────────────────────────────────────────────────────────────────────
_HERE   = os.path.dirname(os.path.abspath(__file__))
_PTOL   = os.path.expanduser('~/.ptolemy')
_DESKTOP = os.path.join(os.path.dirname(_HERE), 'PtolemyDesktop')

sys.path.insert(0, _HERE)
sys.path.insert(0, _DESKTOP)

# ── espeak voice parameters ────────────────────────────────────────────────────
_VOICE  = 'en'          # en, en+m3 (male 3), en+f3 (female 3), grc (ancient Greek)
_RATE   = 148           # words per minute
_PITCH  = 62            # 0-99, Ptolemy's measured tone
_VOLUME = 82            # 0-200
_WORDGAP = 4            # extra gap between words (ms × 10)

def _get_voice(engine=None):
    from skills.voice import HolcusVoice
    return HolcusVoice(engine=engine)

def _load_iface(bin_path=None):
    """Load Engine + MonadInterface with the best available bin."""
    from monad import Engine, MonadInterface
    engine = Engine()
    path   = bin_path or os.path.join(_PTOL, 'monad.bin')
    if not os.path.exists(path):
        for candidate in [
            os.path.join(_HERE, 'monad_sedenion.bin'),
            os.path.join(_HERE, 'monad_wordnet.bin'),
            os.path.join(_HERE, 'monad_english.bin'),
            os.path.join(_HERE, 'monad_mathematics.bin'),
        ]:
            if os.path.exists(candidate):
                path = candidate
                break
    if os.path.exists(path):
        engine.load_bin(path)
        n = engine.crank.n if hasattr(engine.crank, 'n') else '?'
        print(f'[speak] loaded: {path}  vocab={n}', file=sys.stderr)
    else:
        print(f'[speak] no bin — cold start', file=sys.stderr)
    return MonadInterface(engine)

def _tongue_filter(text):
    """Apply PtolemyTongue output filter if available, else minimal cleanup."""
    try:
        sys.path.insert(0, os.path.join(_DESKTOP, 'Philadelphos'))
        from ptolemy_tongue import PtolemyTongue
        return PtolemyTongue().filter(text)
    except Exception:
        # minimal: strip Fermat-space separators, collapse whitespace
        import re
        text = re.sub(r'[     ]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

def speak_text(text, espeak_instance):
    """Speak a string through espeak. Blocks until audio completes."""
    import time
    espeak_instance.synth(text)
    # espeak Python binding is async — wait for completion
    words = len(text.split())
    wait  = (words / _RATE) * 60 + 1.5
    time.sleep(wait)

def generate_and_speak(prompt, n_words=32, bin_path=None, dry_run=False):
    """Full pipeline: prompt → generate → Holcus voice → speak."""
    iface = _load_iface(bin_path)
    voice = _get_voice(iface._engine)
    try:
        result = iface.generate(prompt, n_words=n_words)
        raw    = result.get('response', '')
        bao    = result.get('bao', 0.0)
        mode   = result.get('mode', '?')
        print(f'[speak] mode={mode}  BAO={bao:.5f}  {voice}', file=sys.stderr)
    except Exception as e:
        print(f'[speak] generate failed: {e}  — speaking prompt directly', file=sys.stderr)
        raw = prompt

    filtered = _tongue_filter(raw)
    print(f'[speak] → {filtered!r}', file=sys.stderr)

    if dry_run:
        print(filtered)
    else:
        voice.say(filtered)
    return filtered

# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description='Make Holcus speak')
    ap.add_argument('prompt', nargs='*', help='Prompt text (or pipe via stdin)')
    ap.add_argument('--words', '-n', type=int, default=32,
                    help='Max output words (default 32)')
    ap.add_argument('--bin', '-b', default=None,
                    help='Explicit .bin path (default: auto-select)')
    ap.add_argument('--voice', '-v', default=_VOICE,
                    help='espeak voice (en, en+m3, en+f3, grc)')
    ap.add_argument('--rate', '-r', type=int, default=_RATE,
                    help='Speech rate WPM (default 148)')
    ap.add_argument('--dry', action='store_true',
                    help='Print output instead of speaking')
    args = ap.parse_args()

    if args.voice != _VOICE:
        globals()['_VOICE'] = args.voice
    if args.rate != _RATE:
        globals()['_RATE'] = args.rate

    if args.prompt:
        prompt = ' '.join(args.prompt)
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        print('Usage: python3 speak.py "your prompt"', file=sys.stderr)
        sys.exit(1)

    generate_and_speak(prompt, n_words=args.words, bin_path=args.bin,
                       dry_run=args.dry)

if __name__ == '__main__':
    main()
