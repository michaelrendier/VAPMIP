#!/usr/bin/env python3
"""
monad_observe.py — Claude Code hook: pipe a conversation turn into the Monad.

Wired in ~/.claude/settings.json:
    UserPromptSubmit -> monad_observe.py external
    Stop             -> monad_observe.py internal

Reads the hook JSON on stdin. For `external` it takes the prompt text; for
`internal` it takes the LAST assistant message from the transcript and keeps
only its text blocks — thinking blocks and tool calls / results are dropped
before anything is sent. The text is prose-sanitised by
harness.strip_to_prose (fenced code, tables, box-drawing, links and
notation-dense lines removed — the WORDS for any maths are expected to come
from the calculator's own narration, not raw glyphs) and written
non-blocking to the ingest FIFO, or appended to the local spool if the
daemon / its drive is unavailable.

A prompt and the response it draws are linked by a pair id (stashed per
session in ~/.ptolemy/.pair-<session>), so the daemon can log the
prompt-bytes -> response-bytes sample for a response-scaling engine.

This hook must never block the prompt and never fail the turn: everything is
best-effort and it always exits 0.
"""
import json
import os
import sys

# where harness.py lives — override with MONAD_HARNESS_DIR if the tree moves
_VAPMIP = os.environ.get(
    'MONAD_HARNESS_DIR',
    os.path.expanduser('~/Projects/ThePlace/VAPMIP'))
if _VAPMIP not in sys.path:
    sys.path.insert(0, _VAPMIP)


def _load_harness_bits():
    from harness import (strip_to_prose, _sentences, OBSERVE_FIFO,
                         OBSERVE_SPOOL, INGEST_POLICY)
    return strip_to_prose, _sentences, OBSERVE_FIFO, OBSERVE_SPOOL, INGEST_POLICY


def _last_assistant_prose(transcript_path):
    """Last assistant turn, text blocks only — no thinking, no tool I/O."""
    if not transcript_path or not os.path.exists(transcript_path):
        return ''
    last = None
    with open(transcript_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if obj.get('type') == 'assistant':
                last = obj
    if not last:
        return ''
    msg = last.get('message', last)
    content = msg.get('content', '')
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get('type') == 'text':
            parts.append(block.get('text', ''))
    return '\n'.join(parts)


def _pair_path(session_id):
    sid = ''.join(c for c in (session_id or 'nosession') if c.isalnum() or c in '-_')
    return os.path.expanduser(f'~/.ptolemy/.pair-{sid}')


def _pair_id(cls, session_id):
    """external: mint a fresh id and stash it. internal: read + consume it."""
    p = _pair_path(session_id)
    try:
        if cls == 'external':
            pid = os.urandom(6).hex()
            with open(p, 'w') as f:
                f.write(pid)
            return pid
        with open(p) as f:
            pid = f.read().strip()
        os.unlink(p)
        return pid or None
    except OSError:
        return None


def _emit(msg, fifo, spool):
    data = msg.encode('utf-8', 'replace')
    try:
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
        try:
            if os.write(fd, data) == len(data):
                return
        finally:
            os.close(fd)
    except OSError:
        pass
    try:
        os.makedirs(os.path.dirname(spool), exist_ok=True)
        with open(spool, 'a', encoding='utf-8') as f:
            f.write(msg)
    except OSError:
        pass


def main():
    cls = sys.argv[1] if len(sys.argv) > 1 else 'external'
    try:
        hook = json.load(sys.stdin)
    except Exception:
        hook = {}
    session_id = hook.get('session_id') or hook.get('sessionId')

    if cls == 'external':
        text = hook.get('prompt') or hook.get('user_input') or ''
        if not text:
            tp = hook.get('transcript_path') or hook.get('transcriptPath')
            # fall back: last user line in the transcript
            try:
                with open(tp, encoding='utf-8', errors='replace') as f:
                    for line in f:
                        o = json.loads(line)
                        if o.get('type') == 'user':
                            c = o.get('message', {}).get('content', '')
                            text = c if isinstance(c, str) else '\n'.join(
                                b.get('text', '') for b in c
                                if isinstance(b, dict) and b.get('type') == 'text')
            except Exception:
                pass
    else:
        text = _last_assistant_prose(hook.get('transcript_path')
                                     or hook.get('transcriptPath'))

    if not text or not text.strip():
        return

    try:
        strip_to_prose, _sentences, FIFO, SPOOL, POLICY = _load_harness_bits()
    except Exception:
        return
    if cls not in POLICY:
        return

    prose = strip_to_prose(text)
    if not prose.strip():
        return

    pid = _pair_id(cls, session_id) if cls in ('external', 'internal') else None
    hdr = f"{cls} {pid}" if pid else cls
    msg = f"{hdr}\n" + "\n".join(_sentences(prose)) + "\n.\n"
    _emit(msg, FIFO, SPOOL)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
