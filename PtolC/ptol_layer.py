#!/usr/bin/env python3
"""
ptol_layer.py — sedenion geometry → response.

Single command. The input defines the fixed point. The path is the response.
The output domain is chosen by the geometry — H_hat_RB observing itself.

usage:  python3 ptol_layer.py <prompt>
        python3 ptol_layer.py --layer <english|code|math|physics|meaning> <prompt>
        ./ptol -r <prompt> | python3 ptol_layer.py --stdin [--layer <name>]
"""

import sys, os, re, pickle, subprocess, math

BIN_DIR  = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
PTOL_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ptol')

LAYERS = {
    'english': 'holcus_monad_english.bin',
    'code':    'holcus_monad_c.bin',
    'math':    'holcus_monad_mathematics.bin',
    'physics': 'holcus_monad_physics.bin',
    'meaning': 'holcus_monad_meaning.bin',
}

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
    return {
        'code':    len(_CODE_RE.findall(prompt)) * 3,
        'math':    len(_MATH_RE.findall(p)) * 3,
        'physics': len(_PHYS_RE.findall(p)) * 3,
        'english': 1,
        'meaning': 0,
    }

def _is_code_token(w):
    return bool(w and (
        re.search(r'[_(){};]', w) or
        re.match(r'^[a-z][a-z0-9_]+$', w) and '_' in w or
        w.startswith('/') or w.endswith('.c') or w.endswith('.h')
    ))

def _path_scores(scalars):
    """Score each layer by how well the active-prime words resonate."""
    scores = {l: 0 for l in LAYERS}
    order  = sorted(range(16), key=lambda k: -abs(scalars[k]))
    top4   = order[:4]          # most prominent dimensions
    for layer in LAYERS:
        data = load(layer)
        for k in top4:
            w = word_at(data, scalars[k])
            if not w:
                continue
            if layer == 'code' and _is_code_token(w):
                scores['code'] += 2
            elif layer in ('math', 'physics') and re.search(r'[∑∫\\^_{}]|\w{6,}', w):
                scores[layer] += 2
            elif layer == 'english' and re.match(r'^[A-Za-z][a-z]+$', w):
                scores['english'] += 2
            else:
                scores[layer] += 1
    return scores

def select_layer(prompt, scalars):
    is_  = _input_scores(prompt)
    ps_  = _path_scores(scalars)
    combined = {l: is_[l] + ps_[l] for l in LAYERS}
    # tie-break: english always has floor 1
    return max(combined, key=combined.get)

# ── Geometry: call ptol.c binary ─────────────────────────────────────────────

def geometry(prompt):
    result = subprocess.run(
        [PTOL_BIN, '-r', prompt],
        capture_output=True, text=True
    )
    lines   = result.stdout.strip().split('\n')
    sep     = lines.index('---') if '---' in lines else 16
    scalars = [float(l) for l in lines[:sep]]
    primes  = set()
    for l in lines[sep+1:]:
        l = l.strip()
        if l.lstrip('-').isdigit():
            primes.add(int(l))
    return scalars, primes

def geometry_stdin():
    lines   = sys.stdin.read().strip().split('\n')
    sep     = lines.index('---') if '---' in lines else 16
    scalars = [float(l) for l in lines[:sep]]
    primes  = set()
    for l in lines[sep+1:]:
        l = l.strip()
        if l.lstrip('-').isdigit():
            primes.add(int(l))
    return scalars, primes

# ── Path assembly: cursive — continuous path with halts ──────────────────────

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

def respond(prompt, forced_layer=None, scalars=None, primes=None):
    if scalars is None:
        scalars, primes = geometry(prompt)

    layer = forced_layer or select_layer(prompt, scalars)
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

    while args and args[0].startswith('--'):
        flag = args.pop(0)
        if flag == '--layer' and args:
            forced_layer = args.pop(0)
        elif flag == '--stdin':
            use_stdin = True

    if use_stdin:
        scalars, primes = geometry_stdin()
        prompt = ' '.join(args) if args else '(stdin)'
        respond(prompt, forced_layer, scalars, primes)
    elif args:
        respond(' '.join(args), forced_layer)
    else:
        print(__doc__)
        sys.exit(1)
