"""
seed_runner.py — Dynamic torrent-style corpus seeder for Android.

Reads corpus_list.json from the app files directory.
Creates one GenericCorpus + Engine per entry, runs all in parallel.
New corpora can be added by pushing an updated corpus_list.json via adb
without rebuilding the APK.

Called from SeedService.kt via Chaquopy.
"""

import json
import os
import threading
from typing import Any, Callable, Dict, List

from monad import Engine
from skills.corpus import GenericCorpus, parse_corpus_txt


def _build_corpus(entry: Dict[str, Any], files_dir: str) -> GenericCorpus:
    """Construct a GenericCorpus from a corpus_list.json entry.

    :param entry: Dict with name, bin, txt, primary_tags keys.
    :param files_dir: App external files directory.
    :returns: Configured GenericCorpus instance.
    :rtype: GenericCorpus
    """
    txt_path = os.path.join(files_dir, entry['txt']) if entry.get('txt') else None
    bin_path = os.path.join(files_dir, entry['bin'])
    primary_tags = set(entry.get('primary_tags', []))

    # FermatLattice fallback: war_corpus.txt with its existing content
    if txt_path is None or not os.path.exists(txt_path):
        # Try the canonical war corpus path if this is the war entry
        war_fallback = os.path.join(files_dir, 'war_corpus.txt')
        if os.path.exists(war_fallback):
            txt_path = war_fallback

    return GenericCorpus(
        engine=Engine(),
        txt_path=txt_path or '',
        bin_path=bin_path,
        name=entry.get('name', entry['bin']),
        interval=entry.get('interval', 60),
        primary_tags=primary_tags,
        primary_weight=float(entry.get('primary_weight', 2.0)),
        context_weight=float(entry.get('context_weight', 1.0)),
    )


def run_all(
    files_dir: str,
    on_progress: Callable,
    check_interval: int = 15,
) -> Dict[str, Any]:
    """Run all corpus seed passes defined in corpus_list.json (blocking).

    Reads corpus_list.json from *files_dir*. Each corpus runs in its own
    thread. Returns when all corpus URL lists are exhausted.

    :param files_dir: App external files directory containing corpus .txt
        files, corpus_list.json, and where .bin files are written.
    :param on_progress: Callable(name, tag, url, idx, total, studied, skipped).
        Called after each URL. May be called from any thread.
    :param check_interval: Seconds between network retry attempts.
    :returns: Dict of results keyed by corpus name.
    :rtype: dict
    """
    # Load corpus manifest — prefer files_dir copy (adb-pushable), fall back to assets
    list_path = os.path.join(files_dir, 'corpus_list.json')
    if not os.path.exists(list_path):
        raise FileNotFoundError(f'corpus_list.json not found in {files_dir}')

    with open(list_path, encoding='utf-8') as f:
        corpus_list: List[Dict[str, Any]] = json.load(f)

    results: Dict[str, Any] = {}

    def _seed(corpus: GenericCorpus, name: str) -> None:
        def _cb(tag: str, url: str, idx: int, total: int,
                studied: int, skipped: int) -> None:
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
            results[name] = {'complete': False, 'error': str(e)}

    threads = []
    for entry in corpus_list:
        try:
            corpus = _build_corpus(entry, files_dir)
        except Exception as e:
            name = entry.get('name', entry.get('bin', '?'))
            results[name] = {'complete': False, 'error': f'build failed: {e}'}
            continue
        name = entry.get('name', entry['bin'])
        t = threading.Thread(
            target=_seed,
            args=(corpus, name),
            daemon=True,
            name=f'seed-{name[:16]}',
        )
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return results
