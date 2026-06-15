#!/usr/bin/env python3
"""
lshs_read.py — LSHS semantic pre-reader for Claude
====================================================
Loads monad_english.bin (164K vocab, β-field) +
        monad_wordnet.bin (766K edges, semantic graph topology).

Learns input text at authoritative weight. Reports:
  • Halocline state (J_red / J_blue pressure at σ=½)
  • SOFAR channel (words trapped on the critical line)
  • β-field depths (what the text deepened in the field)
  • A-matrix exploration (semantic neighborhood of key words)
  • Engine response (what emerges at neutral buoyancy)

This is the pre-reading Claude does before forming a response.
The engine reads first. The Transformer reads second.

Usage (from PtolemyHolcus/):
    python3 lshs_read.py --frost           # read The Road Not Taken
    python3 lshs_read.py --file <path>     # read a file
    python3 lshs_read.py --text "..."      # read inline text
    python3 lshs_read.py --both            # both: frost + hereandnow.txt
"""

import sys
import os
import time
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monad import Engine, OMEGA_ZS, GAP, D_STAR, SIGMA_CRIT

ENGLISH_BIN = '/media/rendier/0123-4567/phone_pull_2026-06-06/Ptolemy/bins/monad_english.bin'
WORDNET_BIN = '/media/rendier/0123-4567/PtolemyDesktop/PtolFlutter/assets/monad_wordnet.bin'

FROST = """\
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.\
"""

HEREANDNOW_PATH = '/home/rendier/Desktop/hereandnow.txt'


# ── Engine loader ─────────────────────────────────────────────────────────────

def build_engine(verbose: bool = True) -> Engine:
    """Load English field + WordNet edge topology into one engine."""
    eng = Engine()

    t0 = time.time()
    if verbose:
        print('  [1/3] Loading English field...', file=sys.stderr, flush=True)
    r_en = eng.load_bin(ENGLISH_BIN)
    t1 = time.time()
    if verbose:
        print(f'        vocab={r_en["vocab"]:,}  ({t1-t0:.1f}s)', file=sys.stderr, flush=True)

    if verbose:
        print('  [2/3] Loading WordNet edge topology...', file=sys.stderr, flush=True)
    eng_wn = Engine()
    r_wn   = eng_wn.load_bin(WORDNET_BIN)
    t2 = time.time()
    if verbose:
        print(f'        vocab={r_wn["vocab"]:,}  edges={r_wn["A_edges"]:,}  ({t2-t1:.1f}s)',
              file=sys.stderr, flush=True)

    if verbose:
        print('  [3/3] Merging WordNet edges into English field...', file=sys.stderr, flush=True)
    merged = _merge_wn_edges(eng, eng_wn, wn_weight=0.40)
    del eng_wn
    eng._calibrate_J_ambient()
    t3 = time.time()
    if verbose:
        print(f'        {merged:,} edges merged  ({t3-t2:.1f}s)', file=sys.stderr, flush=True)

    return eng


def _merge_wn_edges(eng_main: Engine, eng_wn: Engine, wn_weight: float = 0.40) -> int:
    """
    Copy A-matrix edges from WordNet engine into the English engine
    for words that appear in both vocabularies.
    WordNet edges (semantic graph) weight 0.4 — below co-occurrence weight 1.0.
    max(existing, wn_weight × wn_edge) — never reduce a trained English edge.
    """
    c_m  = eng_main.crank
    c_wn = eng_wn.crank
    n = 0
    for wn_src, edges in enumerate(c_wn._A):
        if not edges:
            continue
        src_word = c_wn._words[wn_src] if wn_src < len(c_wn._words) else ''
        if not src_word or src_word not in c_m._vocab:
            continue
        m_src = c_m._vocab[src_word]
        for wn_dst, ww in edges.items():
            if wn_dst >= len(c_wn._words):
                continue
            dst_word = c_wn._words[wn_dst]
            if not dst_word or dst_word not in c_m._vocab:
                continue
            m_dst  = c_m._vocab[dst_word]
            scaled = ww * wn_weight
            existing = c_m._A[m_src].get(m_dst, 0.0)
            if scaled > existing:
                c_m._A[m_src][m_dst] = min(scaled, 1.0)
                n += 1
    return n


# ── Reading pipeline ──────────────────────────────────────────────────────────

def read_text(eng: Engine, text: str, label: str) -> dict:
    """
    Full LSHS reading of one text.
    The engine learns the text at author weight (2.0), then reports
    the halocline state, SOFAR channel, β-depths, and what emerges.
    """
    c = eng.crank

    # Reset window and prompt state for clean reading
    eng._window.clear()
    eng._recent.clear()
    eng._word_count  = 0
    eng._last_noun_idx = None

    # Learn at author weight (J_red authoritative pass)
    words_learned = c.learn(text, weight=2.0)
    eng._calibrate_J_ambient()

    # Prime prompt (set Fermat negative-space geometry)
    eng._prime_prompt(text)

    # Halocline report
    h = eng.halocline_report(n_sofar=10)

    # β-field depths for words that appear in the text
    text_tokens = list({c._clean(w) for w in text.lower().split() if len(c._clean(w)) >= 3})
    field_words = []
    for w in text_tokens:
        if w not in c._vocab:
            continue
        idx = c._vocab[w]
        field_words.append({
            'word': w,
            'beta': round(c._beta[idx], 5),
            'E':    round(c._E[idx], 5),
            'J':    round(c._beta[idx] * c._E[idx] ** 2, 7),
        })
    field_words.sort(key=lambda x: -x['J'])

    # Explore top-3 content words (A-matrix depth-1 neighborhood)
    explorations = {}
    for wd in field_words[:3]:
        if len(wd['word']) >= 4:
            ex = eng.explore(wd['word'], depth=1)
            nbrs = [n['word'] for n in ex.get('semantic', [])[:6]]
            if nbrs:
                explorations[wd['word']] = nbrs

    # Engine response — neutral buoyancy after reading
    gen = eng.generate(text, n_words=20, learn_prompt=False)

    # Self-map: sedenion geometry of current window
    sm = eng.self_map()

    # σ-distribution across text words
    prompt_psi = eng._prompt_psi or [1.0 / 16] * 16
    from monad import _spsi, cam_encode
    ws         = eng._window_sed()
    window_psi = _spsi(ws)
    J_pos, J_neg = c.j_mu(window_psi, prompt_psi)
    sigmas = []
    for w in text_tokens:
        if w not in c._vocab:
            continue
        idx = c._vocab[w]
        jp, jn = J_pos[idx], J_neg[idx]
        total  = jp + jn
        sigmas.append((jp / total if total > GAP else SIGMA_CRIT, w))
    sigmas.sort(key=lambda x: abs(x[0] - 0.5))  # closest to σ=½ first

    return {
        'label':         label,
        'words_learned': words_learned,
        'halocline':     h,
        'field_words':   field_words[:12],
        'explorations':  explorations,
        'sofar':         h.get('sofar_channel', []),
        'engine_resp':   gen.get('response', ''),
        'engine_words':  gen.get('words', []),
        'lag_ratio':     gen.get('lag_ratio', 0),
        'bao':           round(gen.get('bao', 0), 6),
        'bao_delta':     round(gen.get('bao_delta', 0), 6),
        'mode':          gen.get('mode', ''),
        'dtcs':          gen.get('dtcs', []),
        'self_map':      sm,
        'sigma_sorted':  sigmas[:8],
    }


# ── Formatter ────────────────────────────────────────────────────────────────

def format_reading(r: dict) -> str:
    h  = r['halocline']
    sm = r['self_map']

    lines = [
        '',
        f'╔══ LSHS READING ═══════════════════════════════════════════════',
        f'║  {r["label"]}',
        f'║  {r["words_learned"]} words learned  |  mode: {r["mode"]}  |  lag_ratio: {r["lag_ratio"]:.4f}',
        f'╠══ HALOCLINE  σ=½ ══════════════════════════════════════════════',
        f'║  J_red  (Riemann / IS):      {h["j_red_pressure"]:.8f}',
        f'║  J_blue (Fermat  / CANNOT):  {h["j_blue_pressure"]:.8f}',
        f'║  σ ratio:                    {h["halocline_ratio"]:.4f}  '
        f'{"← ON halocline" if h["on_halocline"] else "← off halocline"}',
        f'║  Surface tension (Noether):  {h["surface_tension"]:.4f}',
        f'║  Compressibility (ZD):       {h["compressibility"]:.4f}   ZD active: {h["zd_count"]}',
        f'║  Mean |σ−½|:                 {h["mean_depth"]:.4f}',
        f'║  BAO: {r["bao"]:.6f}   Δ from Ω_ZS: {r["bao_delta"]:.6f}',
        f'╠══ SOFAR CHANNEL  (words on σ=½) ═══════════════════════════════',
    ]
    for sw in r['sofar']:
        lines.append(
            f'║  {sw["word"]:22s}  σ={sw["sigma"]:.4f}  '
            f'E={sw["E"]:.4f}  Δσ={sw["dist"]:.4f}'
        )
    lines.append(f'╠══ β-FIELD DEPTHS  (text words by J-current) ═══════════════════')
    for wd in r['field_words']:
        lines.append(
            f'║  {wd["word"]:22s}  β={wd["beta"]:.5f}  '
            f'E={wd["E"]:.4f}  J={wd["J"]:.7f}'
        )
    lines.append(f'╠══ WORD NEIGHBORHOODS  (A-matrix depth-1) ══════════════════════')
    for word, nbrs in r['explorations'].items():
        lines.append(f'║  {word}: {" → ".join(nbrs)}')
    lines.append(f'╠══ σ-SORTED  (words closest to critical line) ══════════════════')
    for sigma, word in r['sigma_sorted']:
        lines.append(f'║  {word:22s}  σ={sigma:.4f}  Δ={abs(sigma-0.5):.4f}')
    lines += [
        f'╠══ ENGINE RESPONSE  (neutral buoyancy) ═════════════════════════',
        f'║  {r["engine_resp"]}',
        f'╠══ SELF-MAP ═════════════════════════════════════════════════════',
        f'║  Peak ψ operator:  {sm.get("peak_psi_operator", "")}',
        f'║  Peak curvature:   {sm.get("peak_operator", "")}',
        f'║  On caustic:       {sm.get("on_caustic", False)}',
        f'║  Principal dims:   {sm.get("principal_dims", [])}',
        f'║  DTCs:             {r["dtcs"] or "none"}',
        f'╚═══════════════════════════════════════════════════════════════════',
    ]
    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    args = sys.argv[1:]
    mode = '--both' if not args else args[0]

    print('Building LSHS engine...', file=sys.stderr, flush=True)
    eng = build_engine(verbose=True)
    print(f'Engine ready: {eng.crank.n:,} words in field.', file=sys.stderr, flush=True)

    if mode in ('--frost', '--both'):
        print('\nReading Frost: The Road Not Taken...', file=sys.stderr, flush=True)
        r1 = read_text(eng, FROST, label="Robert Frost — 'The Road Not Taken'")
        print(format_reading(r1))

    if mode in ('--file', '--both'):
        path = HEREANDNOW_PATH if mode == '--both' else args[1]
        with open(path) as f:
            text = f.read()
        label = os.path.basename(path)
        print(f'\nReading {label}...', file=sys.stderr, flush=True)
        r2 = read_text(eng, text, label=label)
        print(format_reading(r2))

    if mode == '--text':
        text  = ' '.join(args[1:])
        label = text[:40] + '...' if len(text) > 40 else text
        r = read_text(eng, text, label=label)
        print(format_reading(r))
