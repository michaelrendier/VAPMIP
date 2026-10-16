#!/usr/bin/env python3
"""
evidence.py: every measurement the paper reports, taken fresh from the running engine. Nothing here changes an engine file.

Safety rules (learned the hard way, 2026-10-15):
  * `ptol` writes SVG/PPM "papers" into $HOME/.ptolemy, so it is always run with HOME pointed at a scratch directory;
  * `ptolemy -r -n` never saves its store, so it runs with the real HOME (that is where the store is);
  * the resident service folds conversation into PtolC/monad3_c.bin on its own, so that file's checksum is REPORTED, not asserted unchanged.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

VAPMIP = Path(__file__).resolve().parent.parent
PTOLC = VAPMIP / 'PtolC'
PROMPTS = ["finger pointer", "what is a tree", "neutron generation in different reactor types",
           "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered"]
EYES = (("R", 1.0), ("C", 0.75), ("H", 0.5), ("O", 0.25), ("S", 0.0))
_P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]      # read from ptol.c below and asserted equal
_SCRATCH = tempfile.mkdtemp(prefix='vapmip_paper_home_')
import atexit, shutil  # noqa: E402
atexit.register(shutil.rmtree, _SCRATCH, ignore_errors=True)   # ptol writes papers into $HOME/.ptolemy: keep the scratch HOME, then remove it


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def _blue(k: int) -> bool:
    return 4 <= k <= 7 or 12 <= k <= 15


def primes_from_source() -> list[int]:
    src = (PTOLC / 'ptol.c').read_text()
    m = re.search(r'P\[\s*16\s*\]\s*=\s*\{([^}]*)\}', src)
    return [int(x) for x in m.group(1).replace('\n', ' ').split(',') if x.strip()]


def project(s: bytes, k: int, sig: float) -> float:
    f = 2 * math.pi / _P[k]
    return sum(c * i ** (-sig) * (math.sin(f * i) if _blue(k) else math.cos(f * i)) for i, c in enumerate(s, 1))


def vector(s: bytes, sig: float) -> list[float]:
    x = [project(s, k, sig) for k in range(16)]
    n = math.sqrt(sum(a * a for a in x))
    return [a / n for a in x]


def p_red(v: list[float]) -> float:
    return sum(v[k] ** 2 for k in range(16) if not _blue(k))


def sigma_self(s: bytes, sig: float) -> float:
    return p_red(vector(s, sig))


def _words() -> list[str]:
    """Random-prompt vocabulary: /usr/share/dict/words if present, else every WordNet lemma (sorted, so the draw is reproducible)."""
    try:
        return [w.strip() for w in open('/usr/share/dict/words')]
    except OSError:
        from nltk.corpus import wordnet
        return sorted({n for n in wordnet.all_lemma_names() if n.isalpha()})


def ptol(*args: str, timeout: int = 180, real_home: bool = False):
    """Run the compiled monad. `-say` must use the REAL HOME (it writes no files and its sentence bridge needs the user's
    site-packages and ~/nltk_data; with a scratch HOME ptol silently falls back to the word bag). Everything else that
    can write papers into $HOME/.ptolemy runs with a scratch HOME."""
    env = os.environ.copy() if real_home else dict(os.environ, HOME=_SCRATCH)
    t = time.perf_counter()
    r = subprocess.run([str(PTOLC / 'ptol'), *args], capture_output=True, text=True, cwd=PTOLC, env=env, timeout=timeout)
    return r.stdout, r.stderr, (time.perf_counter() - t) * 1000


def repl(prompt: str):
    t = time.perf_counter()
    r = subprocess.run([str(PTOLC / 'ptolemy'), '-r', '-n'], input=prompt + '\n\n', capture_output=True, text=True, cwd=PTOLC, timeout=120)
    first = next((ln[4:].strip() for ln in r.stdout.splitlines() if ln.startswith('>>> ') and ln[4:].strip()), '')
    zork = next((ln.strip() for ln in (r.stdout + '\n' + r.stderr).splitlines() if ln.startswith('[zork]')), '')
    return first, zork, (time.perf_counter() - t) * 1000


# ── 0. state ────────────────────────────────────────────────────────────────────
def engine_state() -> dict:
    files = ['PtolC/ptol.c', 'PtolC/ptol', 'PtolC/monad.c', 'PtolC/monad.h', 'PtolC/ptolemy.h', 'PtolC/monad3c.h', 'PtolC/zork.c', 'PtolC/monad_harness.c',
             'PtolC/ptol_layer.py', 'engine/grammar/ptolc_bridge.py', 'scaled_mind_eye_boxkite_kernel_monad.py', '19D_rotary_boxkite_monad.py',
             '19D_boxkite_context_monad.py', 'rotary_rerun_monad.py', 'ptolemy_monad.py', 'zork_parser.py', 'wordnet_boxkite.py', '../PtolemyDesktop/ptolemy_console.py',
             '../ValaQuenta/modules/box_kite/maths.py']
    out = {}
    for f in files:
        p = (VAPMIP / f).resolve()
        if p.exists():
            out[f] = sha(p)
    store = VAPMIP / 'PtolC' / 'monad3_c.bin'
    head = subprocess.run(['git', '-C', str(VAPMIP), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    return {'files': out, 'store_bytes': store.stat().st_size, 'git_head': head,
            'ptol_c_lines': len((PTOLC / 'ptol.c').read_text().splitlines())}


# ── 1. the fixed question: projection, eyes, identities ──────────────────────────
def question_and_eyes() -> dict:
    global _P
    _P = primes_from_source()
    assert _P == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    raw_worst, eye_worst, rows = 0.0, 0.0, []
    for p in PROMPTS:
        out, err, _ = ptol('-r', p)
        c = [float(x) for x in out.split('---\n')[0].splitlines()[:16]]
        py = vector(p.encode(), 0.5)
        raw_worst = max(raw_worst, max(abs(a - b) for a, b in zip(c, py)))
        gam = float(re.search(r'Γ:\s*([-+0-9.]+)', err).group(1))
        sig_c = float(re.search(r'σ_self:\s*([-+0-9.]+)', err).group(1))
        sig_py = p_red(py)
        row = {'prompt': p, 'len': len(p), 'sigma_self': sig_py, 'gamma': 2 * sig_py - 1, 'gamma_c': gam, 'eyes': {}}
        assert abs(sig_c - sig_py) < 1e-8 and abs(gam - (2 * sig_py - 1)) < 1e-8
        for eye, sg in EYES:
            o2, e2, _ = ptol('-eye', eye, '-r', p)
            sc = float(re.search(r'σ_self:\s*([-+0-9.]+)', e2).group(1))
            sp = sigma_self(p.encode(), sg)
            eye_worst = max(eye_worst, abs(sc - sp))
            row['eyes'][eye] = sp
        rows.append(row)
    return {'rows': rows, 'raw_worst': raw_worst, 'eye_worst': eye_worst}


def identities_and_claims(n_random: int = 2000) -> dict:
    """What holds exactly, and what the source comments claim that the running code does not reproduce."""
    rnd = random.Random(11)
    words = _words()
    prod_max, sum_dev, mono = 0.0, 0.0, {}
    grid = [i / 20 for i in range(21)]
    ends = []
    for _ in range(n_random):
        s = ' '.join(rnd.choice(words) for _ in range(rnd.randint(1, 12)))
        b = s.encode()
        for sg in (0.0, 0.5, 1.0):
            v = vector(b, sg)
            pr = p_red(v)
            pb = sum(v[k] ** 2 for k in range(16) if _blue(k))
            sum_dev = max(sum_dev, abs(pr + pb - 1))
            prod_max = max(prod_max, pr * pb)
        c = [sigma_self(b, g) for g in grid]
        ok = all(y >= x - 1e-12 for x, y in zip(c, c[1:]))
        key = min(len(s) // 10, 9) * 10
        t = mono.setdefault(key, [0, 0])
        t[0] += ok
        t[1] += 1
        ends.append((c[0], c[-1]))
    # the source comment says sigma_self -> 1 at sigma = 1 and -> 0 at sigma = 0
    hi = sorted(e[1] for e in ends)
    lo = sorted(e[0] for e in ends)
    # product spread on the six prompts at five sigma
    spread = []
    for p in PROMPTS:
        for sg in (0.0, 0.25, 0.5, 0.75, 1.0):
            pr = sigma_self(p.encode(), sg)
            spread.append(pr * (1 - pr))
    return {'sum_dev': sum_dev, 'prod_max': prod_max, 'mono': mono, 'n_random': n_random,
            'sigma1_median': hi[len(hi) // 2], 'sigma1_max': hi[-1], 'sigma0_median': lo[len(lo) // 2], 'sigma0_min': lo[0],
            'prod_min6': min(spread), 'prod_max6': max(spread)}


def u_shape(n: int = 300) -> dict:
    """For inputs of 20+ characters sigma_self(sigma) is U-shaped on [0,1]; measure it, with a random-letter control."""
    rnd = random.Random(6)
    words = _words()
    grid = [i / 20 for i in range(21)]
    upper = tot = 0
    argmin, ratio = [], []
    while tot < n:
        s = ' '.join(rnd.choice(words) for _ in range(rnd.randint(4, 12)))
        if len(s) < 20:
            continue
        c = [sigma_self(s.encode(), g) for g in grid]
        tot += 1
        upper += all(c[i + 1] >= c[i] - 1e-12 for i in range(10, 20))
        i = min(range(21), key=lambda j: c[j])
        argmin.append(grid[i])
        ratio.append(c[0] / c[i])
    rb = random.Random(1)
    ctrl = []
    for _ in range(100):
        s = bytes(rb.randrange(97, 123) for _ in range(40))
        c = [sigma_self(s, g) for g in grid]
        ctrl.append(grid[min(range(21), key=lambda j: c[j])])
    med = lambda a: sorted(a)[len(a) // 2]
    return {'n': tot, 'upper': upper, 'argmin_med': med(argmin), 'argmin_lo': sorted(argmin)[len(argmin) // 10], 'argmin_hi': sorted(argmin)[9 * len(argmin) // 10],
            'ratio_med': med(ratio), 'ctrl_med': med(ctrl)}


def near_d_star(n: int = 2000) -> dict:
    """Chance rate for P_forward*P_return landing within 1e-4 of 0.2460 (random prompts, five dial settings)."""
    rnd = random.Random(7)
    words = _words()
    hit = tot = 0
    for _ in range(n):
        s = ' '.join(rnd.choice(words) for _ in range(rnd.randint(2, 6))).encode()
        for sg in (0.0, 0.25, 0.5, 0.75, 1.0):
            pr = sigma_self(s, sg)
            tot += 1
            hit += abs(pr * (1 - pr) - 0.2460) < 1e-4
    ne = b'neutron generation in different reactor types'
    vals = [sigma_self(ne, sg) * (1 - sigma_self(ne, sg)) for sg in (0.0, 1.0)]
    rate = hit / tot
    return {'n': tot, 'rate': rate, 'p30': 1 - (1 - rate) ** 30, 'neutron': vals}


# ── 2. words: what each voice returns ────────────────────────────────────────────
def surface() -> dict:
    rows = []
    for p in PROMPTS:
        a, ea, ta = ptol(p)
        b, eb, tb = ptol(p)
        strip = lambda t: '\n'.join(ln for ln in t.splitlines() if not ln.startswith('paper:'))
        s1, es1, ts1 = ptol('-say', p, real_home=True)
        s2, es2, ts2 = s1, es1, ts1      # -say takes ~12 s: measured once per prompt
        r1, z1, tr1 = repl(p)
        r2, z2, tr2 = repl(p)
        rows.append({'prompt': p, 'ptol': a.strip(), 'ptol_det': strip(a + ea) == strip(b + eb), 'ptol_ms': min(ta, tb),
                     'say': s1.strip(), 'say_det': s1 == s2, 'say_ms': min(ts1, ts2),
                     'repl': r1, 'repl_zork': z1, 'repl_det': (r1, z1) == (r2, z2), 'repl_ms': min(tr1, tr2)})
    return {'rows': rows}


_TWIN_CHILD = r"""
import contextlib, io, json, sys, time
sys.path.insert(0, %(vap)r); sys.path.insert(0, %(pd)r)
P = %(prompts)r
q = io.StringIO(); t0 = time.perf_counter()
with contextlib.redirect_stdout(q), contextlib.redirect_stderr(q):
    import ptolemy_monad as pm
    m = pm.PtolemyMonad()
load = time.perf_counter() - t0
rounds = []
for _ in range(2):
    rows = []
    for p in P:
        t = time.perf_counter()
        with contextlib.redirect_stdout(q), contextlib.redirect_stderr(q):
            r = m.process_input(p)
        rows.append({'prompt': p, 'reply': r.text, 'direction': str(getattr(r, 'direction', '')), 'ms': (time.perf_counter() - t) * 1000})
    rounds.append(rows)
print(json.dumps({'load_s': load, 'cold': rounds[0], 'warm': rounds[1]}))
"""


def twin(seed: int = 0) -> dict:
    """The Python twin in a fresh process with PYTHONHASHSEED=seed (its replies depend on the hash seed: Phase 32)."""
    code = _TWIN_CHILD % {'vap': str(VAPMIP), 'pd': str(VAPMIP.parent / 'PtolemyDesktop'), 'prompts': PROMPTS}
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=env, timeout=600)
    import json
    d = json.loads(r.stdout.strip().splitlines()[-1])
    d['same'] = all(a['reply'] == b['reply'] for a, b in zip(d['cold'], d['warm']))
    d['seed'] = seed
    return d


def twin_seeds(seeds=(0, 1, 2, 3, 4)) -> dict:
    runs = [twin(s) for s in seeds]
    per_prompt = []
    for i, p in enumerate(PROMPTS):
        replies = [r['warm'][i]['reply'] for r in runs]
        per_prompt.append({'prompt': p, 'replies': replies, 'distinct': len(set(replies))})
    return {'runs': runs, 'per_prompt': per_prompt, 'seeds': list(seeds)}



# ── the scaled adapter (the Python monad's speaking path) ─────────────────────────────────────
_ADAPTER_CHILD = r"""
import contextlib, io, json, sys, time
sys.path.insert(0, %(vap)r); sys.path.insert(0, %(pd)r)
q = io.StringIO(); t0 = time.perf_counter()
with contextlib.redirect_stdout(q), contextlib.redirect_stderr(q):
    import ptolemy_console as pc
    ad = pc.ScaledMindEyeMonadAdapter()
load = time.perf_counter() - t0
rounds = []
for _ in range(2):
    rows = []
    for p in %(prompts)r:
        t = time.perf_counter()
        with contextlib.redirect_stdout(q), contextlib.redirect_stderr(q):
            reply, meta = ad.say(p)
        rows.append({'prompt': p, 'reply': reply, 'via': meta.get('via'), 'direction': meta.get('direction'), 'strut': meta.get('strut'), 'ms': (time.perf_counter() - t) * 1000})
    rounds.append(rows)
print(json.dumps({'load_s': load, 'kind': ad.kind, 'cold': rounds[0], 'warm': rounds[1]}))
"""


def adapter(seed: int = 0) -> dict:
    """ScaledMindEyeMonadAdapter on the six prompts in a fresh process with PYTHONHASHSEED=seed (two rounds: cold, warm)."""
    import json
    code = _ADAPTER_CHILD % {'vap': str(VAPMIP), 'pd': str(VAPMIP.parent / 'PtolemyDesktop'), 'prompts': PROMPTS}
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED=str(seed)), timeout=900)
    d = json.loads(r.stdout.strip().splitlines()[-1])
    d['same'] = all(a['reply'] == b['reply'] for a, b in zip(d['cold'], d['warm']))
    d['seed'] = seed
    return d


def adapter_seeds(seeds=(0, 1, 2, 3, 4)) -> dict:
    runs = [adapter(s) for s in seeds]
    per = [{'prompt': p, 'replies': [r['warm'][i]['reply'] for r in runs]} for i, p in enumerate(PROMPTS)]
    for x in per:
        x['distinct'] = len(set(x['replies']))
    return {'runs': runs, 'per_prompt': per, 'seeds': list(seeds)}


# ── the store header, read straight from the file ─────────────────────────────────────────────
def store_header() -> dict:
    import struct
    p = PTOLC / 'monad3_c.bin'
    with open(p, 'rb') as f:
        h = f.read(32)
    magic, version, n_words, n_eng, n_wn, n_phon, nnz = struct.unpack('<8sIIIIII', h[:32])
    return {'bytes': p.stat().st_size, 'magic': magic.rstrip(b'\0').decode(), 'version': version, 'n_words': n_words,
            'n_eng': n_eng, 'n_wn': n_wn, 'n_phon': n_phon, 'nnz': nnz}


def where(rel: str, name: str) -> str:
    """'path:first-last' of a C function (PtolC/…) or a Python def/class (anything .py), found by reading the source."""
    p = VAPMIP / rel
    src = p.read_text().split('\n')
    if rel.endswith('.py'):
        import ast
        tree = ast.parse(p.read_text())
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name:
                return f"{rel}:{n.lineno}-{n.end_lineno}"
        raise KeyError(name)
    pat = re.compile(r'^(static\s+)?[A-Za-z_][\w\s\*]*?\b' + re.escape(name) + r'\s*\(')
    for i, l in enumerate(src):
        if pat.match(l) and not l.rstrip().endswith(';'):
            depth, started, j = 0, False, i
            while j < len(src):
                depth += src[j].count('{') - src[j].count('}')
                started = started or '{' in src[j]
                if started and depth == 0:
                    break
                j += 1
            return f"{rel}:{i + 1}-{j + 1}"
    raise KeyError(name)


def notebook_ledgers() -> list:
    """PASS / FAIL counts read from the executed notebooks (the last 'PASS n · FAIL n' line, or the C notebooks' PASS/FAIL lines)."""
    import json
    out = []
    nb_root = VAPMIP / 'notebooks'
    for rel in ['paper/17_null_operator_and_hub.ipynb', 'paper/18_ptol_sentence_bridge.ipynb', 'paper/19_parser_tables.ipynb',
                'paper/20_scaled_kernel_fibers.ipynb', 'paper/21_scaled_adapter_encounter.ipynb', 'paper/22_fault_ledger_and_null.ipynb',
                'c/07c_ptol_projection_and_balance.ipynb', 'c/08c_ptol_store.ipynb']:
        d = json.loads((nb_root / rel).read_text())
        text = ''
        for c in d['cells']:
            for o in c.get('outputs', []):
                t = o.get('text', '')
                text += ''.join(t) if isinstance(t, list) else t
        m = re.findall(r'PASS (\d+) · FAIL (\d+)', text)
        if m:
            p, f = int(m[-1][0]), int(m[-1][1])
        else:
            p, f = text.count('PASS:'), text.count('FAIL:')
        errs = sum(1 for c in d['cells'] for o in c.get('outputs', []) if o.get('output_type') == 'error')
        out.append({'notebook': 'VAPMIP/notebooks/' + rel, 'pass': p, 'fail': f, 'errors': errs})
    return out


# ── 3. the parser ────────────────────────────────────────────────────────────────
def parser() -> dict:
    sys.path.insert(0, str(VAPMIP))
    import zork_parser as zp
    c = (PTOLC / 'zork.c').read_text()
    tbl = c[c.index('VerbEntry VERBS[]'):]
    tbl = tbl[:tbl.index('};')]
    cv = {m.group(1): int(m.group(2)) for m in re.finditer(r'\{\s*"([^"]+)"\s*,\s*(\d+)\s*\}', tbl)}
    pv = dict(zp.VERB_TO_OP)
    multi = {}
    for op, vs in zp.OPERATOR_VERBS.items():
        for v in vs:
            multi.setdefault(v, []).append(op)
    multi = {v: o for v, o in multi.items() if len(set(o)) > 1}
    diff = sorted(v for v in set(cv) & set(pv) if cv[v] != pv[v])
    per_op = {}
    for v, o in cv.items():
        per_op[o] = per_op.get(o, 0) + 1
    return {'c_verbs': len(cv), 'py_verbs': len(pv), 'only_py': sorted(set(pv) - set(cv)), 'only_c': sorted(set(cv) - set(pv)),
            'conflicts': [(v, cv[v], pv[v], multi.get(v)) for v in diff], 'ops_c': len(set(cv.values())), 'ops_py': len(set(pv.values())),
            'names': zp.OP_NAMES, 'per_op': dict(sorted(per_op.items()))}


if __name__ == '__main__':
    import json
    for name in ('engine_state', 'question_and_eyes', 'identities_and_claims', 'surface', 'twin_seeds', 'parser'):
        print(name, json.dumps(globals()[name](), default=str)[:300])


# ── parsing the executed notebooks, and a few direct runs for the paper's tables ─────────────
def nb_text(rel: str) -> str:
    import json
    d = json.loads((VAPMIP / 'notebooks' / rel).read_text())
    text = ''
    for c in d['cells']:
        for o in c.get('outputs', []):
            t = o.get('text', '')
            text += ''.join(t) if isinstance(t, list) else t
    return text


def c_constants() -> dict:
    h = (PTOLC / 'ptolemy.h').read_text()
    g = lambda n: re.search(r'#define\s+' + n + r'\s+([-\d.eE]+)', h).group(1)
    return {'beta_sat': g('MONAD_BETA_SAT'), 'window_max': g('MONAD_WINDOW_MAX'), 'alpha': g('MONAD_ALPHA_LEARN'), 'gap': g('MONAD_GAP')}


def store_notebook() -> dict:
    t = nb_text('c/08c_ptol_store.ipynb')
    look = [m.groups() for m in re.finditer(r'^(\w+)\s+hit=(\d)\s+eng=(-?\d+) wn=(-?\d+) phon=(-?\d+)\s+degree=(\d+)(?:\s+gamma_radial=(\S+))?', t, re.M)]
    coords = [m.groups() for m in re.finditer(r'^(\w+)\s+slot\s+(\d+)\s+E = ([\d.]+)', t, re.M)]
    return {'lookup': look, 'coords': coords}


def c07_diff() -> str:
    m = re.search(r'max \|extracted - real\| = (\S+)', nb_text('c/07c_ptol_projection_and_balance.ipynb'))
    return m.group(1) if m else '(not run)'


def tree_senses() -> list:
    """gamma_radial of every WordNet sense of 'tree' (Python, wordnet_boxkite)."""
    sys.path.insert(0, str(VAPMIP))
    from nltk.corpus import wordnet as wn
    import wordnet_boxkite as wb
    return [(s.name(), wb.gamma_radial(s)) for s in wn.synsets('tree')]


def kernel_rows() -> list:
    sys.path.insert(0, str(VAPMIP)); sys.path.insert(0, str(VAPMIP.parent))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import scaled_mind_eye_boxkite_kernel_monad as K
        kern = K.MindEyeBoxKiteKernel()
        throws = kern.run_boxkite([(s, 0.6) for s in kern.kite.struts])
    return [{'strut': t.strut, 'assessor': t.assessor, 'weight': t.fixed_point_weight, 'zd': t.is_zero_divisor,
             'wind': t.a_matrix_basin_windspeed, 'sigma_self': t.sigma_self} for t in throws]


def harness_counts() -> str:
    sys.path.insert(0, str(VAPMIP)); sys.path.insert(0, str(VAPMIP.parent))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import rotary_rerun_monad as rr
        h = rr.Harness(); h.run(psi=rr._demo_psi(), currents=(0.412, -0.187, -0.201))
    led = h.ledger
    c = {s.name: led.count(s) for s in rr.Status}
    f = {k.name: len(led.faults_of(k)) for k in rr.Fault if k.name != 'NONE'}
    first = led.faults()[0] if led.faults() else None
    txt = f"{len(led)} records; {c['HOLDS']} HOLDS, {c['VIOLATED']} VIOLATED, {c['DEGENERATE']} DEGENERATE, {c['UNTESTED']} UNTESTED; faults: {f['MATHS']} MATHS, {f['CODE']} CODE"
    if first:
        txt += f"; the one fault is `{first.name}` (expected {first.expected!r}, observed {first.observed:.3f})" if isinstance(first.observed, float) else f"; the one fault is `{first.name}`"
    return txt


def null_census() -> list:
    t = nb_text('paper/22_fault_ledger_and_null.ipynb')
    rows = []
    for l in t.splitlines():
        m = re.match(r'\s+(KEEPS NULL|SUPPLIES)\s+(.+?)\s+->\s+(.*)$', l)
        if m:
            rows.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return rows


def lineage_table() -> list:
    sys.path.insert(0, str(VAPMIP)); sys.path.insert(0, str(VAPMIP.parent))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import rotary_rerun_monad as rr
    return [(s, ' → '.join(map(str, rr.BoxKite.lineage(s)))) for s in range(1, 8)]


def tte_counts(phase: str) -> str:
    """'PASS n · FAIL n · PROSE n' of one executed Tuning-the-Engine notebook."""
    import json
    d = json.loads((VAPMIP / 'notebooks' / 'tuning_the_engine' / f'phase_{phase}.ipynb').read_text())
    text = ''
    for c in d['cells']:
        for o in c.get('outputs', []):
            t = o.get('text', '')
            text += ''.join(t) if isinstance(t, list) else t
    m = re.findall(r'PASS (\d+) · FAIL (\d+) · PROSE (\d+)', text)
    return f"{m[-1][0]} PASS, {m[-1][1]} FAIL, {m[-1][2]} PROSE" if m else 'not run'


def tte_totals() -> str:
    t = (VAPMIP / 'notebooks' / 'tuning_the_engine' / 'FINDINGS.md').read_text()
    m = re.search(r'\*\*44 notebooks · (\d+) PASS · (\d+) FAIL · (\d+) PROSE · (\d+) SKIP', t)
    return f"{m.group(1)} PASS, {m.group(2)} FAIL, {m.group(3)} PROSE, {m.group(4)} SKIP" if m else 'see FINDINGS.md'
