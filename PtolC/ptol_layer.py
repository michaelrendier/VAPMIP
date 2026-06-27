#!/usr/bin/env python3
"""
ptol_layer.py — sedenion geometry → response.

Single command. The input defines the fixed point. The path is the response.
The output domain is chosen by the geometry — H_hat_RB observing itself.

usage:  python3 ptol_layer.py <prompt>
        python3 ptol_layer.py --layer <english|code|math|physics|meaning> <prompt>
        ./ptol -r <prompt> | python3 ptol_layer.py --stdin [--layer <name>]
"""

import sys, os, re, pickle, subprocess, math, glob

BIN_DIR  = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
PTOL_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ptol')

# ── All .bin files are tools — import the full domain, define nothing ─────────
# Scan BIN_DIR for every holcus_monad_*.bin. The layer name is derived from
# the filename. The math selects; we only provide access.

def _scan_layers():
    layers = {}
    for path in glob.glob(os.path.join(BIN_DIR, 'holcus_monad_*.bin')):
        name = os.path.basename(path)                   # holcus_monad_english.bin
        key  = name[len('holcus_monad_'):-len('.bin')]  # english
        layers[key] = name
    return layers

LAYERS = _scan_layers()

# SVG element name: capitalise first letter so <English> not <english>
def layer_element(layer):
    return layer.capitalize()

P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

# ── Vocabulary loading ────────────────────────────────────────────────────────

_cache = {}
def load(layer):
    if layer not in _cache:
        path = os.path.join(BIN_DIR, LAYERS[layer])
        with open(path, 'rb') as f:
            _cache[layer] = pickle.load(f)
    return _cache[layer]

def word_at(data, v):
    n, words = data['n'], data['words']
    idx = max(0, min(int((v + 1.0) / 2.0 * n), n - 1))
    for r in range(128):
        for d in ([0] if r == 0 else [r, -r]):
            i = idx + d
            if 0 <= i < n and words[i]:
                return words[i]
    return None

# ── Layer selection: H_hat_RB choosing what to observe ───────────────────────

_CODE_RE  = re.compile(r'[{};]|def |class |#include|->|=>|\w+\(\)|__\w+__')
_MATH_RE  = re.compile(r'[∑∫∂σζΓΩπφ]|theorem|proof|integral|eigenvalue|riemann|prime|modular')
_PHYS_RE  = re.compile(r'quantum|energy|mass\b|field|photon|gravity|entropy|wave|spin|boson')

def _input_scores(prompt):
    p = prompt.lower()
    raw = {
        'c':               len(_CODE_RE.findall(prompt)) * 3,
        'mathematics':     len(_MATH_RE.findall(p)) * 3,
        'physics':         len(_PHYS_RE.findall(p)) * 3,
        'english':         1,
        'englishwordnet':  1,  # same baseline as english — geometry selects
    }
    return {layer: raw.get(layer, 0) for layer in LAYERS}

def _is_code_token(w):
    return bool(w and (
        re.search(r'[_(){};]', w) or
        re.match(r'^[a-z][a-z0-9_]+$', w) and '_' in w or
        w.startswith('/') or w.endswith('.c') or w.endswith('.h')
    ))

def _s_rb_scores(s_rb):
    """Boost mathematics/physics when Σ_RB product (J_red×J_blue) is active.
    Large |s_rb[k]| means the Wankel cycle is firing in that channel pair.
    Shell 2 (k=4-7) ↔ Shell 1 (k=0-3): word-particle ZD crossing.
    Shell 4 (k=12-15) ↔ Shell 3 (k=8-11): deep-structure ZD crossing."""
    scores = {l: 0 for l in LAYERS}
    if not s_rb:
        return scores
    s_rb_total = sum(abs(v) for v in s_rb)
    if s_rb_total < 1e-8:
        return scores
    # Shell 2↔1 (indices 4-7 and 0-3): surface ZD — word / language
    surface_power = sum(abs(s_rb[k]) for k in range(8) if k < len(s_rb))
    # Shell 4↔3 (indices 12-15 and 8-11): deep ZD — maths / physics
    deep_power    = sum(abs(s_rb[k]) for k in range(8, 16) if k < len(s_rb))
    ratio = deep_power / (s_rb_total + 1e-15)
    # Deep ZD active → mathematics/physics boost
    boost = int(ratio * 10)
    if 'mathematics' in scores: scores['mathematics'] += boost
    if 'physics'     in scores: scores['physics']     += boost
    return scores

def _path_scores(scalars):
    """Score each layer by how well the active-prime words resonate."""
    scores = {l: 0 for l in LAYERS}
    order  = sorted(range(16), key=lambda k: -abs(scalars[k]))
    top4   = order[:4]
    for layer in LAYERS:
        try:
            data = load(layer)
        except Exception:
            continue
        for k in top4:
            w = word_at(data, scalars[k])
            if not w:
                continue
            if layer == 'c' and _is_code_token(w):
                scores['c'] += 2
            elif layer in ('mathematics', 'physics') and re.search(r'[∑∫\\^_{}]|\w{6,}', w):
                scores[layer] += 2
            elif layer == 'english' and re.match(r'^[A-Za-z][a-z]+$', w):
                scores['english'] += 2
            else:
                scores[layer] += 1
    return scores

def select_layer(prompt, scalars, s_rb=None):
    is_  = _input_scores(prompt)
    ps_  = _path_scores(scalars)
    erb_ = _s_rb_scores(s_rb or [])
    combined = {l: is_[l] + ps_[l] + erb_[l] for l in LAYERS}
    # tie-break: english always has floor 1
    return max(combined, key=combined.get)

# ── Geometry: call ptol.c binary ─────────────────────────────────────────────

def _parse_raw(lines):
    """Parse ptol -r output: scalars / primes / s_rb (three --- sections)."""
    seps = [i for i, l in enumerate(lines) if l.strip() == '---']
    sep0 = seps[0] if len(seps) > 0 else 16
    sep1 = seps[1] if len(seps) > 1 else len(lines)
    sep2 = seps[2] if len(seps) > 2 else len(lines)

    scalars = []
    for l in lines[:sep0]:
        try: scalars.append(float(l))
        except ValueError: pass

    primes = set()
    for l in lines[sep0+1:sep1]:
        l = l.strip()
        if l.lstrip('-').isdigit():
            primes.add(int(l))

    s_rb = []
    for l in lines[sep1+1:sep2]:
        try: s_rb.append(float(l))
        except ValueError: pass

    return scalars, primes, s_rb

def geometry(prompt):
    result = subprocess.run(
        [PTOL_BIN, '-r', prompt],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split('\n')
    return _parse_raw(lines)

def geometry_stdin():
    lines = sys.stdin.read().strip().split('\n')
    return _parse_raw(lines)

# ── Path assembly: cursive — continuous path with halts ──────────────────────

def words_by_dimension(scalars, layer):
    """16 words, one per dimension k=0..15 (not spiral order)."""
    data = load(layer)
    return [word_at(data, scalars[k]) or '' for k in range(16)]

def assemble_path(scalars, layer):
    """
    Words ordered by ascending |scalar| — spiral from zero divisor outward.
    Halt (space) between words is the zero divisor between letters.
    Active prime words (largest |scalar|) are the conclusion.
    Cursive: the path does not restart per word, it continues.
    """
    data  = load(layer)
    order = sorted(range(16), key=lambda k: abs(scalars[k]))
    seen, path = set(), []
    for k in order:
        w = word_at(data, scalars[k])
        if w and w not in seen:
            path.append((k, scalars[k], w))
            seen.add(w)
    return path

# ── Main response ─────────────────────────────────────────────────────────────

def respond(prompt, forced_layer=None, scalars=None, primes=None, s_rb=None):
    if scalars is None:
        scalars, primes, s_rb = geometry(prompt)

    layer = forced_layer or select_layer(prompt, scalars, s_rb)
    path  = assemble_path(scalars, layer)

    # sedenion signature
    print(f"σ: {prompt}")
    print(f"\nlayer: {layer}  |  primes: {sorted(primes)}")
    print()

    # path table
    print(f"{'e':>3}  {'scalar':>10}  {'*':1}  word")
    print("─" * 48)
    for k, v, w in path:
        mark = '*' if P[k] in primes else ' '
        print(f"  e{k:<2} {v:+.6f}  {mark}  {w}")

    # cursive response: continuous path, zero divisor halts
    words = [w for _, _, w in path]
    print(f"\npath → {' '.join(words)}")

    # if English selected but code words appear in top 4 — show code shadow too
    if layer == 'english' and any(
        _is_code_token(word_at(load('code'), s))
        for s in sorted(scalars, key=abs, reverse=True)[:4]
    ):
        code_path = assemble_path(scalars, 'code')
        code_words = [w for _, _, w in code_path]
        print(f"\ncode shadow → {' '.join(code_words)}")

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    forced_layer = None
    use_stdin    = False
    words_only   = False

    while args and args[0].startswith('--'):
        flag = args.pop(0)
        if flag == '--layer' and args:
            forced_layer = args.pop(0)
        elif flag == '--stdin':
            use_stdin = True
        elif flag == '--words-only':
            words_only = True

    if words_only:
        if use_stdin:
            scalars, primes, s_rb = geometry_stdin()
        elif args:
            scalars, primes, s_rb = geometry(' '.join(args))
        else:
            sys.exit(1)
        layer = forced_layer or select_layer(' '.join(args) if args else '', scalars, s_rb)
        # Line 0: layer element name (the monad that fired)
        # Lines 1-16: one word per dimension
        print(layer_element(layer))
        for w in words_by_dimension(scalars, layer):
            print(w)
        sys.exit(0)

    if use_stdin:
        scalars, primes, s_rb = geometry_stdin()
        prompt = ' '.join(args) if args else '(stdin)'
        respond(prompt, forced_layer, scalars, primes, s_rb)
    elif args:
        respond(' '.join(args), forced_layer)
    else:
        print(__doc__)
        sys.exit(1)
