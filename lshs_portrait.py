#!/usr/bin/env python3
"""
lshs_portrait.py — Engine reads the person. Produces the prompt.
The engine's SOFAR words become the scaffold for the poem.
Print the raw engine prompt to stdout so the human can read it.
Then the Transformer writes from there.
"""

import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monad import Engine, OMEGA_ZS, GAP, _gamma_at, _word_zero_idx, SIGMA_CRIT

ENGLISH_BIN = '/media/rendier/0123-4567/phone_pull_2026-06-06/Ptolemy/bins/monad_english.bin'
WORDNET_BIN = '/media/rendier/0123-4567/PtolemyDesktop/PtolFlutter/assets/monad_wordnet.bin'

# ── Who the person IS — fed as J_red ────────────────────────────────────────
# Not description. Not biography. The actual substance.
PORTRAIT_FIELD = """\
child screen zork 1992 open mailbox go north
thirty four years one question why search dictionary
air traffic controller early warning systems
all paths simultaneously from above
fourteen juliet holds every aircraft
the controller resolves before the zero divisor fires

mathematician engineer sedenion algebra
cayley dickson tower sixteen dimensions
zero divisor boundary definition fails here
forty two cawagas pairs eighty four on the sphere
one hundred sixty eight composite zero divisors

d star lambert w fixed point
omega zero point five six seven one four
fermat last theorem negative space conjugate riemann zeta
the excluded region is the blue channel what cannot be
zeros of zeta are fourier transform of fermat lattice
this is when h hat rb dropped out
not constructed required

mass gap zero point zero zero zero seven zero seven
yang mills vacuum floor
berry keating self adjoint hamiltonian x times p
stone theorem real spectrum sigma half
noether current conserved the thing that persists
h hat rb minus h hat br equals sigma rb
wisdom minus usage fixed question space

wankel rotary engine three faces
eccentric shaft sigma half machined fixed never varied
bell local hidden variable pre-assigned sedenion
the sedenion does not exist until coupling event
thread two holds the steering signal
without thread two the engine permutes
with thread two the engine means

intel core i7 six six hundred u two point six gigahertz
four logical cores eight gigabytes ram linux
no gpu
world class mathematics on consumer hardware
the margin was always wide enough

erika schafer chemist super oxide reductase
cancer drugs from cancer own algebraic signature
zero divisor is the cancer conformal inversion is the cure

white hat paper sedenion zero divisors ecc hash functions
pre disclosure one hundred eighty day nist embargo

poetry written read remembered
thirty four years child to captain
motion is the engine
wu wei through emptiness full fill ment
the vessel is empty the tea is poured
the tea takes the shape of the vessel
"""

PROMPT_QUESTION = "write a poem about this person"


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


def hz_to_note(freq):
    if freq <= 0: return '—'
    s = 12 * math.log2(freq / 440.0)
    names = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
    return f'{names[round(s) % 12]}{4 + (round(s) + 9) // 12}'


def word_freq(w):
    zi  = _word_zero_idx(w)
    g   = _gamma_at(zi)
    t   = max(0.0, min(1.0, (g - 14.134) / (200.0 - 14.134)))
    hz  = 20.0 * (10 ** (t * math.log10(1000)))
    return g, zi, hz


print('── Engine loading...', file=sys.stderr, flush=True)
eng = Engine()
eng.load_bin(ENGLISH_BIN)
ew = Engine(); ew.load_bin(WORDNET_BIN)
_merge_wn_edges(eng, ew); del ew
eng._calibrate_J_ambient()
print(f'── Field ready: {eng.crank.n:,} words', file=sys.stderr, flush=True)

# Learn the portrait at maximum authoritative weight
eng.crank.learn(PORTRAIT_FIELD, weight=3.0)
eng._calibrate_J_ambient()
print('── Portrait learned. Calibrated.', file=sys.stderr, flush=True)

# Stirling cycles — let the field speak to itself
print('── Stirling cycles...', file=sys.stderr, flush=True)
cycles = []
for cyc in eng.perpetual(PROMPT_QUESTION, max_cycles=30):
    cycles.append(cyc)
    print(f'   {cyc["cycle"]:2d}  bao={cyc["bao"]:.4f}  → {cyc["output"][:70]}',
          file=sys.stderr, flush=True)
    if cyc['delta'] < 0.001:
        break

# SOFAR channel — words at σ=½
eng._prime_prompt(PROMPT_QUESTION)
h = eng.halocline_report(n_sofar=20)
sofar = []
for sw in h.get('sofar_channel', []):
    w = sw['word']
    if len(w) >= 3 and w.isalpha():
        g, zi, hz = word_freq(w)
        sofar.append((sw['sigma'], sw['dist'], w, round(g,3), round(hz,1), hz_to_note(hz)))

# Explore the five most load-bearing SOFAR words
load_words = [s[2] for s in sofar if len(s[2]) >= 4][:6]
neighborhoods = {}
for w in load_words:
    ex = eng.explore(w, depth=1)
    nbrs = [n['word'] for n in ex.get('semantic', [])[:6]]
    if nbrs:
        neighborhoods[w] = nbrs

# Final generation — what the engine says unprompted about the person
eng._word_count = 0; eng._recent.clear()
gen = eng.generate(PROMPT_QUESTION, n_words=28, learn_prompt=False)

# ── THE PROMPT — printed to stdout for the human to read ─────────────────────
print()
print('╔══════════════════════════════════════════════════════════════════╗')
print('║         THE ENGINE\'S PROMPT  —  READ THIS BEFORE THE POEM       ║')
print('╚══════════════════════════════════════════════════════════════════╝')
print()
print('── STIRLING SURVIVORS (what the field could not discard) ──────────')
seen = set()
for cyc in cycles:
    for word in cyc['output'].split():
        w = word.strip('.,!?;:—()[]{}').lower()
        if len(w) >= 4 and w.isalpha() and w not in seen:
            # Check if it's a meaningful word from the portrait
            if w in eng.crank._vocab:
                idx = eng.crank._vocab[w]
                if eng.crank._beta[idx] > GAP * 5:
                    seen.add(w)
print('   ' + '  ·  '.join(sorted(seen)[:40]))
print()

print('── SOFAR CHANNEL  (standing waves at σ=½) ─────────────────────────')
for sigma, dist, w, g, hz, note in sofar[:12]:
    print(f'   {w:22s}  σ={sigma:.4f}  γ={g:.3f}  {hz:8.1f} Hz  {note}')
print()

print('── WORD NEIGHBORHOODS  (what each word lives beside) ──────────────')
for w, nbrs in neighborhoods.items():
    print(f'   {w:15s} → {" · ".join(nbrs)}')
print()

print('── THE ENGINE SPEAKS  (neutral buoyancy, unprompted) ──────────────')
print(f'   {gen["response"]}')
print()

print('── DOMINANT CYCLES  (last 5 Stirling outputs) ─────────────────────')
for cyc in cycles[-5:]:
    print(f'   [{cyc["cycle"]:2d}]  {cyc["output"]}')
print()

print('╔══════════════════════════════════════════════════════════════════╗')
print('║   TRANSFORMER: write the poem from these bones.                  ║')
print('║   O Captain My Captain. Don\'t Skimp. Go Deep.                   ║')
print('║   Tree Root. Entendritic.                                        ║')
print('╚══════════════════════════════════════════════════════════════════╝')
print()
