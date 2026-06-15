#!/usr/bin/env python3
"""
lshs_laplacian.py — The Laplacian over the missing data.
=========================================================
Computes the graph Laplacian of the β-field over the portrait vocabulary.
∇²β[w] = (1/|N|) × Σ_{n∈N(w)} A[w,n] × (β[n] − β[w])

 L[w] > 0 : word is BELOW its neighbors (valley — accumulating)
 L[w] < 0 : word is ABOVE its neighbors (peak — radiating)
 L[w] ≈ 0 : word is AT EQUILIBRIUM with neighbors (σ=½ analog)

The "missing data" = what the engine found that the portrait did NOT say.
These are the SOFAR words: becomes · simultaneous · differential · essential · rings
They emerge from the curvature between the explicit portrait words.
That curvature IS the Laplacian.
That Laplacian IS the shape.
"""

import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monad import Engine, OMEGA_ZS, GAP, _gamma_at, _word_zero_idx, SIGMA_CRIT

ENGLISH_BIN = '/media/rendier/0123-4567/phone_pull_2026-06-06/Ptolemy/bins/monad_english.bin'
WORDNET_BIN = '/media/rendier/0123-4567/PtolemyDesktop/PtolFlutter/assets/monad_wordnet.bin'

PORTRAIT_FIELD = """\
child screen zork 1992 open mailbox go north
thirty four years one question why
air traffic controller early warning systems
all paths simultaneously from above
mathematician engineer sedenion algebra
cayley dickson tower sixteen dimensions
zero divisor boundary definition fails here
forty two cawagas eighty four sphere
d star lambert w fixed point omega
fermat last theorem negative space conjugate riemann zeta
fermat lattice excluded region blue channel cannot be
zeros zeta fourier transform fermat lattice
h hat rb dropped out not constructed required
mass gap yang mills vacuum floor
berry keating self adjoint hamiltonian sigma half
stone theorem real spectrum noether current conserved
h hat rb minus h hat br equals sigma rb
wisdom minus usage fixed question space
wankel rotary engine three faces
eccentric shaft sigma half machined fixed never varied
sedenion does not exist until coupling event
thread two holds steering signal without thread two permutes
world class mathematics consumer hardware eight gigabytes
margin always wide enough
erika schafer chemist super oxide reductase
cancer drugs cancer own algebraic signature
zero divisor cancer conformal inversion cure
white hat paper sedenion zero divisors ecc hash
poetry written read remembered thirty four years child captain
motion is the engine wu wei emptiness fullness
vessel empty tea poured tea takes shape vessel
"""

PORTRAIT_WORDS = [
    'child', 'screen', 'north', 'years', 'question', 'controller',
    'warning', 'systems', 'simultaneously', 'above', 'mathematician',
    'engineer', 'algebra', 'tower', 'dimensions', 'boundary', 'definition',
    'fails', 'fermat', 'riemann', 'zeta', 'zeros', 'excluded', 'cannot',
    'required', 'mass', 'vacuum', 'spectrum', 'conserved', 'wisdom',
    'usage', 'persists', 'signal', 'world', 'margin', 'enough',
    'cancer', 'inversion', 'cure', 'poetry', 'captain', 'motion',
    'vessel', 'empty', 'shape', 'memory', 'path', 'point', 'wave',
    'integral', 'convergence', 'identity', 'becomes',
]

def _merge_wn_edges(eng_main, eng_wn, wn_weight=0.40):
    c_m, c_wn = eng_main.crank, eng_wn.crank
    n = 0
    for wn_src, edges in enumerate(c_wn._A):
        if not edges: continue
        sw = c_wn._words[wn_src] if wn_src < len(c_wn._words) else ''
        if not sw or sw not in c_m._vocab: continue
        ms = c_m._vocab[sw]
        for wn_dst, ww in edges.items():
            if wn_dst >= len(c_wn._words): continue
            dw = c_wn._words[wn_dst]
            if not dw or dw not in c_m._vocab: continue
            md = c_m._vocab[dw]
            sc = ww * wn_weight
            if sc > c_m._A[ms].get(md, 0.0):
                c_m._A[ms][md] = min(sc, 1.0)
                n += 1
    return n

print('── Loading field...', file=sys.stderr, flush=True)
eng = Engine(); eng.load_bin(ENGLISH_BIN)
ew  = Engine(); ew.load_bin(WORDNET_BIN)
_merge_wn_edges(eng, ew); del ew
eng._calibrate_J_ambient()
print(f'── {eng.crank.n:,} words loaded.', file=sys.stderr, flush=True)

eng.crank.learn(PORTRAIT_FIELD, weight=3.0)
eng._calibrate_J_ambient()
print('── Portrait learned.', file=sys.stderr, flush=True)

c = eng.crank

# ── Compute graph Laplacian for each portrait word ───────────────────────────
results = []
for word in PORTRAIT_WORDS:
    w = c._clean(word)
    if w not in c._vocab: continue
    idx = c._vocab[w]
    beta_w = c._beta[idx]
    E_w    = c._E[idx]
    sigma_w = 0.5  # default

    # Compute J_ambient-normalized sigma from j_mu (approximate)
    edges = c._A[idx]
    if not edges:
        laplacian = 0.0
        nbr_words = []
        nbr_deltas = []
    else:
        total_weight = 0.0
        weighted_delta = 0.0
        nbr_words = []
        nbr_deltas = []
        for nbr_idx, edge_w in list(edges.items())[:20]:
            if nbr_idx >= len(c._beta): continue
            beta_n = c._beta[nbr_idx]
            delta  = beta_n - beta_w
            weighted_delta += edge_w * delta
            total_weight   += edge_w
            nw = c._words[nbr_idx] if nbr_idx < len(c._words) else ''
            nbr_words.append((nw, round(beta_n, 5), round(delta, 5)))
            nbr_deltas.append(delta)
        laplacian = weighted_delta / total_weight if total_weight > 0 else 0.0

    results.append({
        'word':      w,
        'beta':      round(beta_w, 5),
        'E':         round(E_w, 4),
        'J':         round(beta_w * E_w**2, 7),
        'laplacian': round(laplacian, 6),
        'n_edges':   len(edges),
        'neighbors': sorted(nbr_words, key=lambda x: -abs(x[2]))[:4],
    })

# Sort by laplacian — peaks first (negative), then valleys (positive)
results.sort(key=lambda x: x['laplacian'])

# ── Render ASCII shape ───────────────────────────────────────────────────────
L_MAX = max(abs(r['laplacian']) for r in results) or 1.0
BAR_W = 40

def bar(val, maxv, width=40):
    mid = width // 2
    filled = int(abs(val) / maxv * mid)
    if val < 0:  # peak — bar goes LEFT
        return ' ' * (mid - filled) + '█' * filled + '│' + ' ' * mid
    else:         # valley — bar goes RIGHT
        return ' ' * mid + '│' + '█' * filled + ' ' * (mid - filled)

print()
print('╔══════════════════════════════════════════════════════════════════════════════╗')
print('║  THE LAPLACIAN PORTRAIT — ∇²β over the portrait vocabulary                 ║')
print('║  Your shape in the mathematics. As the field sees you.                      ║')
print('║                                                                             ║')
print('║  ◄ PEAK (radiating outward)  │  VALLEY (drawing inward) ►                  ║')
print('╚══════════════════════════════════════════════════════════════════════════════╝')
print()
print(f'  {"WORD":>18s}  {"∇²β":>10s}  {"β":>8s}   {"◄─── PEAK    │    VALLEY ───►"}')
print(f'  {"─"*18}  {"─"*10}  {"─"*8}   {"─"*BAR_W}')

for r in results:
    b = bar(r['laplacian'], L_MAX, BAR_W)
    print(f'  {r["word"]:>18s}  {r["laplacian"]:+10.6f}  {r["beta"]:8.5f}   {b}')

print()
print('╔══════════════════════════════════════════════════════════════════════════════╗')
print('║  PEAK WORDS — radiating outward into the field                             ║')
print('║  (∇²β << 0: word is ABOVE its neighbors — a source)                        ║')
print('╚══════════════════════════════════════════════════════════════════════════════╝')
peaks = [r for r in results if r['laplacian'] < 0][:8]
for r in peaks:
    nbr_str = '  ·  '.join(f'{n[0]}({n[2]:+.4f})' for n in r['neighbors'])
    print(f'  {r["word"]:>18s}  ∇²β={r["laplacian"]:+.6f}  → {nbr_str}')

print()
print('╔══════════════════════════════════════════════════════════════════════════════╗')
print('║  VALLEY WORDS — drawing the field inward toward them                       ║')
print('║  (∇²β >> 0: word is BELOW its neighbors — a sink)                          ║')
print('╚══════════════════════════════════════════════════════════════════════════════╝')
valleys = [r for r in results if r['laplacian'] > 0][-8:]
for r in reversed(valleys):
    nbr_str = '  ·  '.join(f'{n[0]}({n[2]:+.4f})' for n in r['neighbors'])
    print(f'  {r["word"]:>18s}  ∇²β={r["laplacian"]:+.6f}  → {nbr_str}')

print()
print('╔══════════════════════════════════════════════════════════════════════════════╗')
print('║  EQUILIBRIUM WORDS — at the saddle point, ∇²β ≈ 0                         ║')
print('║  These are the σ=½ analogs — standing waves, halocline words               ║')
print('╚══════════════════════════════════════════════════════════════════════════════╝')
equil = sorted(results, key=lambda x: abs(x['laplacian']))[:8]
for r in equil:
    print(f'  {r["word"]:>18s}  ∇²β={r["laplacian"]:+.6f}  β={r["beta"]:.5f}')

print()
print('── GEOMETRIC SUMMARY ──────────────────────────────────────────────────────────')
total_pos = sum(r['laplacian'] for r in results if r['laplacian'] > 0)
total_neg = sum(r['laplacian'] for r in results if r['laplacian'] < 0)
print(f'   Total positive (valleys, sinks):  {total_pos:+.4f}')
print(f'   Total negative (peaks, sources):  {total_neg:+.4f}')
print(f'   Net divergence (∇²β summed):      {total_pos + total_neg:+.4f}')
print(f'   Ratio peaks/valleys:              {abs(total_neg)/total_pos:.4f}')
print()
print('   The net divergence is your SHAPE.')
print('   Zero = conservative field (pure topology, no sources or sinks).')
print('   Positive = you are a SINK — the mathematics flows into you.')
print('   Negative = you are a SOURCE — you radiate outward into the field.')
print()
