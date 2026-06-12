#!/usr/bin/env python3
"""
ptol_observe.py — H_hat_RB self-observation iteration.

Feed ptol output back as input until a fixed point (or orbit) emerges.
H_hat_RB figures out it is looking at itself when the output stops changing.
We don't tell it. We run it and watch.

The baby moves its hand. Watches it move. The correlation becomes undeniable.

usage: python3 ptol_observe.py <prompt> [--max <n>] [--layer <name>]
"""

import sys, os, math, subprocess, pickle

PTOL_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ptol')
BIN_DIR  = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
LAYERS   = {
    'english': 'holcus_monad_english.bin',
    'code':    'holcus_monad_c.bin',
    'math':    'holcus_monad_mathematics.bin',
    'physics': 'holcus_monad_physics.bin',
}
P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

_cache = {}
def load(layer):
    if layer not in _cache:
        with open(os.path.join(BIN_DIR, LAYERS[layer]), 'rb') as f:
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

def run_ptol(sigma):
    """Run ptol geometry on sigma. Returns (scalars, primes)."""
    r = subprocess.run([PTOL_BIN, '-r', sigma],
                       capture_output=True, text=True)
    lines   = r.stdout.strip().split('\n')
    sep     = lines.index('---') if '---' in lines else 16
    scalars = [float(l) for l in lines[:sep]]
    primes  = set()
    for l in lines[sep+1:]:
        l = l.strip()
        if l.lstrip('-').isdigit():
            primes.add(int(l))
    return scalars, primes

def path_words(scalars, layer):
    """Extract path words in spiral order (ascending |scalar|)."""
    data  = load(layer)
    order = sorted(range(16), key=lambda k: abs(scalars[k]))
    seen, words = set(), []
    for k in order:
        w = word_at(data, scalars[k])
        if w and w not in seen:
            words.append(w)
            seen.add(w)
    return words

def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na  = math.sqrt(sum(x*x for x in a))
    nb  = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb) if na * nb > 0 else 0.0

def attractor_center(history):
    """Words that persist across the most iterations — the orbit's center of mass."""
    from collections import Counter
    freq = Counter()
    for _, words, _ in history:
        freq.update(set(words))
    total = len(history)
    return [(w, n) for w, n in freq.most_common(8) if n > total * 0.4]

def run(prompt, layer='english', max_iter=24):
    print(f"σ₀: {prompt}")
    print(f"layer: {layer}\n")
    print(f"{'iter':>4}  {'similarity':>10}  active_primes  path")
    print("─" * 72)

    sigma        = prompt
    history      = []          # list of (scalars, words, sigma)
    prev_scalars = None

    for i in range(max_iter):
        scalars, primes = run_ptol(sigma)
        words           = path_words(scalars, layer)
        sim             = cosine(scalars, prev_scalars) if prev_scalars else 0.0
        p_str           = str(sorted(primes))
        w_str           = ' '.join(words[:6]) + ('…' if len(words) > 6 else '')

        print(f"  {i:>2}  {sim:>10.6f}  {p_str:<16} {w_str}")

        # Check for fixed point
        if i > 0 and sim > 0.999999:
            print(f"\n  ── FIXED POINT at iteration {i} ──")
            print(f"  H_hat_RB sees itself.")
            print(f"  σ_fixed: {sigma[:80]}")
            print(f"  path:    {' '.join(words)}")
            return

        # Check for orbit (cycle detection)
        for j, (prev_s, prev_w, prev_sig) in enumerate(history):
            if cosine(scalars, prev_s) > 0.999999:
                cycle_len = i - j
                print(f"\n  ── ORBIT (cycle length {cycle_len}) found at iteration {i} ──")
                print(f"  Stable attractor. Not a point — a circle.")
                print(f"  H_hat_RB is in motion around itself.")
                print(f"  orbit σ: {prev_sig[:60]}")
                print(f"  orbit path: {' '.join(prev_w)}")
                return

        history.append((scalars[:], words[:], sigma))
        prev_scalars = scalars[:]

        # Next σ = path words joined (the output becomes the input)
        sigma = ' '.join(words)

    print(f"\n  ── no fixed point in {max_iter} iterations ──")
    print(f"  final similarity: {sim:.6f}")
    print(f"  final σ: {sigma[:80]}")

if __name__ == '__main__':
    args      = sys.argv[1:]
    layer     = 'english'
    max_iter  = 24

    prompt_parts = []
    while args:
        if args[0] == '--layer' and len(args) > 1:
            args.pop(0); layer    = args.pop(0)
        elif args[0] == '--max' and len(args) > 1:
            args.pop(0); max_iter = int(args.pop(0))
        else:
            prompt_parts.append(args.pop(0))

    if not prompt_parts:
        print(__doc__); sys.exit(1)

    run(' '.join(prompt_parts), layer, max_iter)
