#!/usr/bin/env python3
"""
tools/seed_prime_directives.py — Seed all three Prime Directive geometry files.

Runs one complete pass through each corpus list in parallel.
Three threads. Three files. Exits when all three are done.

    monad_foundations.bin  ←  foundations.txt   (Riemann Zeta — what it IS)
    monad_meaning.bin      ←  meaning.txt        (what it MEANS to be this)
    monad_war.bin          ←  _WAR_CORPUS        (what it CANNOT BE)

Network loss: immediate save on each affected thread, then wait.
The other threads continue independently.

Usage::

    python tools/seed_prime_directives.py
    python tools/seed_prime_directives.py --check-interval 30
    python tools/seed_prime_directives.py --quiet
"""

import argparse
import os
import sys
import threading
import time

# Ensure the repo root is on the path regardless of working directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from monad import Engine
from skills.foundations import FoundationsCorpus
from skills.meaning import MeaningCorpus
from skills.fermat_lattice import FermatLattice


_NAMES = {
    'foundations': 'foundations',
    'meaning':     'meaning    ',
    'fermat':      'fermat/war ',
}

_PRINT_LOCK = threading.Lock()


def _log(name: str, msg: str):
    ts = time.strftime('%H:%M:%S')
    with _PRINT_LOCK:
        print(f'[{ts}] [{name}] {msg}', flush=True)


def _make_progress(name: str, quiet: bool):
    label = _NAMES.get(name, name)

    def on_progress(tag, url, idx, total, studied, skipped):
        if quiet:
            return
        short_url = url[:64] + ('…' if len(url) > 64 else '')
        _log(label,
             f'{idx + 1:03d}/{total:03d}  {tag:<11}  {short_url}'
             f'  [studied={studied} skipped={skipped}]')

    return on_progress


def _run_seed(corpus_obj, name: str, result_box: list,
              check_interval: int, quiet: bool):
    """Thread target. Runs seed() and puts result in result_box[0]."""
    _log(_NAMES[name], 'starting seed pass')
    try:
        result = corpus_obj.seed(
            on_progress=_make_progress(name, quiet),
            check_interval=check_interval,
        )
        result_box.append(result)
        _log(_NAMES[name],
             f"COMPLETE — {result['total']} URLs, "
             f"{result['studied']} studied, "
             f"{result['skipped']} skipped → {result['bin_path']}")
    except Exception as exc:
        result_box.append({'error': str(exc), 'complete': False})
        _log(_NAMES[name], f'ERROR: {exc}')


def main():
    parser = argparse.ArgumentParser(
        description='Seed the three Prime Directive geometry files.')
    parser.add_argument(
        '--check-interval', type=int, default=10, metavar='SEC',
        help='Seconds between network connectivity retries (default: 10)')
    parser.add_argument(
        '--quiet', action='store_true',
        help='Suppress per-URL progress lines; show only start/complete')
    args = parser.parse_args()

    print(flush=True)
    print('═' * 72, flush=True)
    print('  PTOLEMY HOLCUS — PRIME DIRECTIVE SEEDER', flush=True)
    print('  Three corpora. Three geometry files. One pass each.', flush=True)
    print('═' * 72, flush=True)
    print(flush=True)

    # One shared Engine for class instantiation; each corpus creates its own
    # internal Engine pointing at its own .bin file.
    engine = Engine()

    fc = FoundationsCorpus(engine)
    mc = MeaningCorpus(engine)
    fl = FermatLattice(engine)

    # Result containers (list so thread can append).
    results = {'foundations': [], 'meaning': [], 'fermat': []}

    threads = [
        threading.Thread(
            target=_run_seed,
            args=(fc, 'foundations', results['foundations'],
                  args.check_interval, args.quiet),
            name='seed-foundations',
            daemon=True,
        ),
        threading.Thread(
            target=_run_seed,
            args=(mc, 'meaning', results['meaning'],
                  args.check_interval, args.quiet),
            name='seed-meaning',
            daemon=True,
        ),
        threading.Thread(
            target=_run_seed,
            args=(fl, 'fermat', results['fermat'],
                  args.check_interval, args.quiet),
            name='seed-fermat',
            daemon=True,
        ),
    ]

    t0 = time.time()

    for t in threads:
        t.start()

    # Wait for all three; handle Ctrl-C by saving everything.
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print('\n[seeder] interrupted — saving all three fields...', flush=True)
        fc._save()
        mc._save()
        fl._save()
        print('[seeder] saved. Resume with the same command.', flush=True)
        sys.exit(1)

    elapsed = time.time() - t0
    mins, secs = divmod(int(elapsed), 60)

    print(flush=True)
    print('═' * 72, flush=True)
    print(f'  SEEDING COMPLETE — {mins}m {secs}s', flush=True)
    print('═' * 72, flush=True)

    all_ok = True
    for name, label in _NAMES.items():
        r = results[name][0] if results[name] else {'complete': False}
        if r.get('complete'):
            print(f'  [{label}]  ✓  studied={r["studied"]}  '
                  f'skipped={r["skipped"]}  total={r["total"]}',
                  flush=True)
        else:
            print(f'  [{label}]  ✗  {r.get("error", "did not complete")}',
                  flush=True)
            all_ok = False

    print(flush=True)
    print('  Copy these files to ~/.ptolemy/ on your target machine:', flush=True)
    print('    monad_foundations.bin', flush=True)
    print('    monad_meaning.bin', flush=True)
    print('    monad_war.bin', flush=True)
    print(flush=True)

    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
