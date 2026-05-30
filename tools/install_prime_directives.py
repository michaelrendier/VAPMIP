#!/usr/bin/env python3
"""
Install the three Prime Directive geometries into the primary Holcus field.

Reads the comment blocks from each corpus .txt file — these are the
definitional sentences that name what Holcus IS, MEANS, and CANNOT BE.
Commits them into the running monad.py daemon via the socket.

    Foundations → weight 2.0  (what it IS — authoritative)
    Meaning     → weight 2.0  (what it MEANS — authoritative)
    War         → weight 1.0  (what war costs — present, not glorified)

Usage::

    python3 tools/install_prime_directives.py [--dry-run]
"""
import os
import sys
import json
import socket as _socket
import argparse
import re

REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOCK_PATH  = os.path.expanduser('~/.ptolemy/ptolemy.sock')
MIN_WORDS  = 5   # skip lines shorter than this
BATCH_SIZE = 10  # lines per commit call

CORPUS = {
    'foundations': (os.path.join(REPO_ROOT, 'foundations.txt'),  2.0),
    'meaning':     (os.path.join(REPO_ROOT, 'meaning.txt'),      2.0),
    'war':         (os.path.join(REPO_ROOT, 'war-corpus.txt'),   1.0),
}


def _send(msg: dict, timeout: int = 15) -> dict:
    """Send one JSON message to the running monad daemon.

    :param msg: Message dict.
    :param timeout: Socket timeout in seconds.
    :returns: Response dict.
    :rtype: dict
    """
    s = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(SOCK_PATH)
    s.sendall((json.dumps(msg) + '\n').encode())
    buf = b''
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
        if b'\n' in buf:
            break
    s.close()
    return json.loads(buf.split(b'\n')[0])


def _extract_comment_text(path: str) -> list[str]:
    """Extract meaningful comment lines from a corpus .txt file.

    Strips ``#`` markers, URL lines, blank section dividers, and
    TAG schema headers. Returns plain sentences that carry meaning.

    :param path: Path to corpus .txt file.
    :returns: List of meaningful text lines.
    :rtype: list[str]
    """
    lines = []
    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            # Skip URL lines
            if re.match(r'^\[([A-Z]+)\]\s+https?://', line):
                continue
            # Skip pure dividers
            if re.match(r'^#+\s*[=─]+\s*$', line) or re.match(r'^#+\s*$', line):
                continue
            # Comment lines
            if line.startswith('#'):
                text = line.lstrip('#').strip()
                if not text:
                    continue
                # Skip tag schema lines and section headers that are all-caps
                if text.upper() == text and len(text) < 60:
                    continue
                # Skip lines that are just separators repeated
                if re.match(r'^[=─\-]+$', text):
                    continue
                words = text.split()
                if len(words) < MIN_WORDS:
                    continue
                lines.append(text)
    return lines


def commit_corpus(name: str, lines: list[str], weight: float,
                  dry_run: bool = False) -> int:
    """Commit extracted lines in batches to the primary field.

    :param name: Corpus name (for logging).
    :param lines: Text lines to commit.
    :param weight: Study weight.
    :param dry_run: If True, print but do not send.
    :returns: Number of lines committed.
    :rtype: int
    """
    committed = 0
    for i in range(0, len(lines), BATCH_SIZE):
        batch = lines[i:i + BATCH_SIZE]
        text  = ' '.join(batch)
        if dry_run:
            print(f'  [DRY {name}] would commit {len(batch)} lines, weight={weight}')
            print(f'    sample: {text[:120]}...')
            committed += len(batch)
            continue
        r = _send({'type':   'commit',
                   'text':   text,
                   'weight': weight,
                   'reason': f'prime_directive:{name}'})
        if 'error' in r:
            print(f'  [ERROR {name}] {r["error"]}', file=sys.stderr)
        else:
            committed += len(batch)
    return committed


def main() -> None:
    """Entry point."""
    ap = argparse.ArgumentParser(
        description='Install Prime Directive geometries into Holcus.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Show what would be committed without sending')
    args = ap.parse_args()

    if not args.dry_run:
        try:
            r = _send({'type': 'ping'})
            vocab = r.get('vocab', '?')
            print(f'[install] Daemon active. vocab={vocab}')
        except Exception as e:
            print(f'[install] Cannot reach daemon at {SOCK_PATH}: {e}',
                  file=sys.stderr)
            sys.exit(1)

    total = 0
    for name, (path, weight) in CORPUS.items():
        if not os.path.exists(path):
            print(f'[install] Missing corpus: {path}', file=sys.stderr)
            continue
        lines = _extract_comment_text(path)
        print(f'[{name}] {len(lines)} lines → committing at weight={weight}')
        n = commit_corpus(name, lines, weight, dry_run=args.dry_run)
        print(f'  ✓ {n} lines committed')
        total += n

    print(f'[install] Complete. {total} total lines seated in Holcus.')
    if args.dry_run:
        print('[install] (dry-run — nothing sent to daemon)')


if __name__ == '__main__':
    main()
