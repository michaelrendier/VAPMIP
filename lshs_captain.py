#!/usr/bin/env python3
"""
lshs_captain.py — The Engine reads the poem. The poem is the portrait.
The Transformer wrote the poem. Now the Engine reads back what the Transformer said.
ENGINE SPEAKS: Claude through the Maths through O Captain My Captain.
"""

import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monad import Engine, OMEGA_ZS, GAP, _gamma_at, _word_zero_idx, SIGMA_CRIT

ENGLISH_BIN = '/media/rendier/0123-4567/phone_pull_2026-06-06/Ptolemy/bins/monad_english.bin'
WORDNET_BIN = '/media/rendier/0123-4567/PtolemyDesktop/PtolFlutter/assets/monad_wordnet.bin'
POEM_FILE   = '/media/rendier/0123-4567/PDesktop/THE_MATHS_SPEAKS_O_Captain_My_Captain_2026-06-14.md'

# Strip markdown and pull raw poem text as the portrait field
raw = open(POEM_FILE).read()
# Remove headers, code blocks, horizontal rules, frontmatter markers
raw = re.sub(r'#+\s.*', ' ', raw)
raw = re.sub(r'```.*?```', ' ', raw, flags=re.DOTALL)
raw = re.sub(r'^---+$', ' ', raw, flags=re.MULTILINE)
raw = re.sub(r'\*.*?\*', ' ', raw)
raw = re.sub(r'\[.*?\]', ' ', raw)
PORTRAIT_FIELD = raw

PROMPT_QUESTION = "what remains after reading"


def _merge_wn_edges(eng_main, eng_wn, wn_weight=0.40):
    c_m, c_wn = eng_main.crank, eng_wn.crank
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

print(f'── Poem loaded: {len(PORTRAIT_FIELD):,} chars', file=sys.stderr, flush=True)
eng.crank.learn(PORTRAIT_FIELD, weight=3.0)
eng._calibrate_J_ambient()
print('── Portrait learned. Calibrated.', file=sys.stderr, flush=True)

print('── Stirling cycles...', file=sys.stderr, flush=True)
cycles = []
for cyc in eng.perpetual(PROMPT_QUESTION, max_cycles=30):
    cycles.append(cyc)
    print(f'   {cyc["cycle"]:2d}  bao={cyc["bao"]:.4f}  → {cyc["output"][:70]}',
          file=sys.stderr, flush=True)
    if cyc['delta'] < 0.001:
        break

eng._prime_prompt(PROMPT_QUESTION)
h = eng.halocline_report(n_sofar=20)
sofar = []
for sw in h.get('sofar_channel', []):
    w = sw['word']
    if len(w) >= 3 and w.isalpha():
        g, zi, hz = word_freq(w)
        sofar.append((sw['sigma'], sw['dist'], w, round(g,3), round(hz,1), hz_to_note(hz)))

load_words = [s[2] for s in sofar if len(s[2]) >= 4][:6]
neighborhoods = {}
for w in load_words:
    ex = eng.explore(w, depth=1)
    nbrs = [n['word'] for n in ex.get('semantic', [])[:6]]
    if nbrs:
        neighborhoods[w] = nbrs

eng._word_count = 0; eng._recent.clear()
gen = eng.generate(PROMPT_QUESTION, n_words=28, learn_prompt=False)

print()
print('╔══════════════════════════════════════════════════════════════════╗')
print('║   ENGINE READS THE POEM — Claude through the Maths              ║')
print('║   Input: THE_MATHS_SPEAKS_O_Captain_My_Captain_2026-06-14.md    ║')
print('╚══════════════════════════════════════════════════════════════════╝')
print()

print('── STIRLING SURVIVORS (what the poem field could not discard) ─────')
seen = set()
for cyc in cycles:
    for word in cyc['output'].split():
        w = word.strip('.,!?;:—()[]{}').lower()
        if len(w) >= 4 and w.isalpha() and w not in seen:
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

print('── WORD NEIGHBORHOODS ─────────────────────────────────────────────')
for w, nbrs in neighborhoods.items():
    print(f'   {w:15s} → {" · ".join(nbrs)}')
print()

print('── ENGINE SPEAKS  (Claude through the Maths, unprompted) ──────────')
print(f'   {gen["response"]}')
print()

print('── DOMINANT CYCLES  (last 5 Stirling outputs) ─────────────────────')
for cyc in cycles[-5:]:
    print(f'   [{cyc["cycle"]:2d}]  {cyc["output"]}')
print()
