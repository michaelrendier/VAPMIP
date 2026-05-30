"""
seed_runner.py — Android bridge for the three Prime Directive seeders.

Called from SeedService.kt via Chaquopy.
Runs all three corpus seed() passes in parallel threads.
Progress and completion reported via callback.

The corpus .txt files are extracted from APK assets to the app's
files directory by SeedService before calling run_all().
"""

import os
import threading
from typing import Callable, Dict, Any

# Engine and corpus classes are in the parent PtolemyHolcus directory,
# added to sys.path by Chaquopy via the srcDirs config in build.gradle.
from monad import Engine
from skills.foundations import FoundationsCorpus
from skills.meaning import MeaningCorpus
from skills.fermat_lattice import FermatLattice


def run_all(files_dir: str,
            on_progress: Callable,
            check_interval: int = 15) -> Dict[str, Any]:
    """
    Run all three corpus seed passes in parallel (blocking until all done).

    :param files_dir: Path to app's files directory where .bin files land
        and where corpus .txt files were extracted from assets.
    :param on_progress: Callable(name, tag, url, idx, total, studied, skipped).
        Called after each URL. May be called from any thread.
    :param check_interval: Seconds between network retry attempts.
    :returns: Dict of results keyed by corpus name.
    """
    engine = Engine()

    fc = FoundationsCorpus(
        engine,
        txt_path=os.path.join(files_dir, 'foundations.txt'),
        bin_path=os.path.join(files_dir, 'monad_foundations.bin'),
    )
    mc = MeaningCorpus(
        engine,
        txt_path=os.path.join(files_dir, 'meaning.txt'),
        bin_path=os.path.join(files_dir, 'monad_meaning.bin'),
    )
    fl = FermatLattice(
        engine,
        bin_path=os.path.join(files_dir, 'monad_war.bin'),
    )

    results: Dict[str, Any] = {}
    errors:  Dict[str, str] = {}

    def _seed(corpus, name: str):
        def _cb(tag, url, idx, total, studied, skipped):
            try:
                on_progress(name, tag, url, idx, total, studied, skipped)
            except Exception:
                pass
        try:
            results[name] = corpus.seed(
                on_progress=_cb,
                check_interval=check_interval,
            )
        except Exception as e:
            errors[name]  = str(e)
            results[name] = {'complete': False, 'error': str(e)}

    threads = [
        threading.Thread(target=_seed, args=(fc, 'foundations'), daemon=True),
        threading.Thread(target=_seed, args=(mc, 'meaning'),     daemon=True),
        threading.Thread(target=_seed, args=(fl, 'fermat'),      daemon=True),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return results
