"""evidence.py: fresh runs of the CURRENT machinery for the VAPMIP paper (2026-11-25 rewrite).  Nothing here is typed in by hand: a number in the paper came out of one of these functions
when make_paper.py ran.  The previous version of this paper (and its evidence.py) is VAPMIP commit 9a16a44; it is not repeated here."""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # VAPMIP
PC = ROOT / 'PtolC'
PY = sys.executable

RUNNER = r'''
import sys, json, io, contextlib, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'Currentwork', 'UserState'))
ns = {}
for src in json.loads(sys.stdin.read()):
    print('>>> ' + src.replace('\n', '\n... '))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            try: v = eval(compile(src, '<t>', 'eval'), ns)
            except SyntaxError: exec(compile(src, '<t>', 'exec'), ns); v = None
            if v is not None: print(repr(v))
        except Exception as e: print(type(e).__name__ + ': ' + str(e))
    sys.stdout.write(buf.getvalue())
'''


def transcript(stmts: list[str], env: dict | None = None, timeout=300) -> str:
    r = subprocess.run([PY, '-c', RUNNER], input=json.dumps(stmts), capture_output=True, text=True, cwd=ROOT, timeout=timeout, env={**os.environ, **(env or {})})
    return (r.stdout + r.stderr[-300:]).rstrip()


def listing(rel: str, qual: str) -> tuple[str, str]:
    """(verbatim source of a function or method with its docstring removed, 'path:first-last'): extracted, never retyped."""
    p = ROOT / rel; src = p.read_text(encoding='utf-8'); tree = ast.parse(src); lines = src.splitlines()
    node = tree
    for part in qual.split('.'):
        node = next(n for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == part)
    a, b = node.lineno, node.end_lineno; body = node.body
    drop = set()
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) and isinstance(body[0].value.value, str):
        drop = set(range(body[0].lineno, body[0].end_lineno + 1))
    text = [l for i, l in enumerate(lines[a - 1:b], start=a) if i not in drop]
    return textwrap.dedent('\n'.join(text)), f'{rel}:{a}–{b}'


def cfunc(name: str, file: str = 'ptol.c') -> str:
    s = (PC / file).read_text(encoding='utf-8').splitlines()
    for i, l in enumerate(s):
        if re.match(r'(static )?[\w \*]+\b' + re.escape(name) + r'\(', l):
            j = i
            while j < len(s) and not s[j].startswith('}'): j += 1
            return f'PtolC/{file}:{i + 1}–{j + 1}'
    raise KeyError(name)


def git_head() -> str:
    return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def run(cmd, env=None, stdin=None, timeout=900):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, input=stdin, env={**os.environ, **(env or {})})


def suite() -> dict:
    t = time.time(); r = run([PY, '-m', 'pytest', '-q', 'tests'], timeout=1800); m = re.search(r'(\d+) passed', r.stdout); f = re.search(r'(\d+) failed', r.stdout)
    p = run([PY, '-m', 'pytest', '-q', 'tests/test_c_parity.py'], timeout=900); mp = re.search(r'(\d+) passed', p.stdout)
    return {'passed': int(m.group(1)) if m else 0, 'failed': int(f.group(1)) if f else 0, 'parity': int(mp.group(1)) if mp else 0, 'secs': round(time.time() - t)}


def build_c() -> None:
    r = run(['make', 'ptol'], timeout=600) if False else subprocess.run(['make', 'ptol'], cwd=PC, capture_output=True, text=True, timeout=600)
    assert (PC / 'ptol').exists(), r.stderr[-500:]


def cenv(tmp: str) -> dict:
    return {'PTOLC_DIR': str(PC), 'PTOL_USAGE_DIR': tmp}


def c_chat(lines: list[str]) -> list[tuple[str, str]]:
    with tempfile.TemporaryDirectory() as d:
        r = run([str(PC / 'ptol'), '-chat'], env=cenv(d), stdin='\n'.join(lines) + '\n')
    out = r.stdout.splitlines()
    return list(zip(lines, out))


def c_probe(lines: list[str]) -> list[list[str]]:
    with tempfile.TemporaryDirectory() as d:
        r = run([str(PC / 'ptol'), '-P'], env=cenv(d), stdin='\n'.join(lines) + '\n')
    return [l.split('\t') for l in r.stdout.splitlines()]


def c_latency(n: int = 40) -> float:
    lines = ['The king rules the kingdom and the dog chases the cat in the garden.'] * n
    with tempfile.TemporaryDirectory() as d:
        t = time.time(); run([str(PC / 'ptol'), '-chat'], env=cenv(d), stdin='\n'.join(lines) + '\n'); dt = time.time() - t
    return dt / n * 1000


def sizes() -> dict:
    sec = lambda f, a, b: (lambda s: s[s.index(a):s.index(b)].count('\n'))((PC / f).read_text(encoding='utf-8'))
    return {'ptol_voice_lines': sec('ptol.c', "THE CHILD'S VOICE", 'gr_report, added 2026-09-21'),
            'harness_ears_lines': sec('monad_harness.c', 'THE HARNESS HEARS (2026-11-25)', '#ifdef MH_SELFTEST'),
            'user_state_mb': round((PC / 'user_state.bin').stat().st_size / 1e6, 1), 'voice_lex_mb': round((PC / 'voice_lex.bin').stat().st_size / 1e6, 1),
            'monad3_mb': round((PC / 'monad3_c.bin').stat().st_size / 1e6, 1),
            'py_lines': {f: len((ROOT / f).read_text(encoding='utf-8').splitlines()) for f in ('numeric.py', 'bw_drift.py', 'state_repass.py', 'conversation_usage.py', 'lyndon_conjugation.py', 'tenseplan.py', 'weave_cycle.py',
                                                                                              'scaled_boxkite_orbweaver_monad.py', 'sedenion_window.py', 'tone_chord.py', 'responder.py')}}


def py_conversation(turns: list[str]) -> str:
    """The Python Responder (real user-state engine, a private usage store) on `turns`: the same pipeline the C runs."""
    stmts = ['import tempfile, responder as R, conversation_usage as CU', "cu = CU.ConversationUsage(tempfile.mkdtemp())", "r = R.Responder(usage=cu, max_sentences=3)"]
    for t in turns:
        stmts.append('out = r.turn(%r); print(out["reply"])' % t)
    return transcript(stmts, env={'PTOL_USAGE': '0'}, timeout=900)
