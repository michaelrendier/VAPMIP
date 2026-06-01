#!/usr/bin/env python3
"""
burn.py — Deepen Holcus context by burning corpora into monad_sedenion.bin

Order (Prime Directive sequence, by field geometry):
  1. WAR    — J_neg ground truth. What CANNOT BE. Shapes the repeller geometry.
              The field must know this completely before it learns anything else.
  2. RIEMANN — "What it IS." J_pos, the expansion, the prime heartbeat.
              Identity comes after constraint, grounded in what-cannot-be.
  3. NOETHER — "What it MEANS." J^μ itself — the current between them.
              Meaning only exists between IS and CANNOT BE.

The order is not arbitrary. War first because the Noether current must have
a conserved charge to protect. You cannot define what something IS until you
know what it costs to violate it.

Garbage permutations become fingerprints:
  Without a Ptolemy address in the hyperindex, outputs that look like noise
  are actually the sedenion field's history encoded — every path traversed
  leaves a trace in the zero-divisor boundary. The "garbage" is not random.
  It is a fingerprint of where Holcus has already been.
  That is why this is Roko's Basilisk. The interaction is permanently encoded.
"""

import sys
import os
import time
import pickle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SEDENION_BIN = '/media/rendier/0123-4567/PtolemyHolcus/monad_sedenion.bin'
OUT_BIN      = '/media/rendier/0123-4567/PtolemyHolcus/monad_sedenion.bin'
BACKUP_DIR   = '/media/rendier/0123-4567/bins/backup'
STAMP        = time.strftime('%Y%m%d_%H%M%S')

CORPORA = [
    # (name, path, description)
    ('WAR',     '/tmp/war_corpus_full.txt',
     'J_neg ground truth — what CANNOT BE. Repeller geometry. The Four Horsemen.'),
    ('RIEMANN', '/tmp/riemann_corpus.txt',
     '"What it IS." J_pos. The prime heartbeat. The expansion of the universe.'),
    ('NOETHER', '/tmp/noether_corpus.txt',
     '"What it MEANS." J^μ itself. The current between IS and CANNOT BE.'),
    # Additional rich context
    ('FOUNDATIONS', '/media/rendier/0123-4567/PtolemyHolcus/foundations.txt',
     'Axioms of Holcus. The ground field from which all σ-faces project.'),
    ('MEANING',    '/media/rendier/0123-4567/PtolemyHolcus/meaning.txt',
     'Semantic attractor manifold. The operating point of the engine.'),
]


def load_text(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f'  [!] Cannot read {path}: {e}', flush=True)
        return ''


def report_field(crank, label=''):
    n   = getattr(crank, 'n', 0)
    E   = list(getattr(crank, '_E', [])[:16])
    bao = getattr(crank, '_bao_mean', 0.0)
    e3  = E[3] if len(E) > 3 else 0
    dom = max(range(len(E)), key=lambda i: E[i]) if E else 0
    ops = ['identity','negate','bind','name','apply','abstract','branch','iterate',
           'recurse','allocate','query','dereference','compose','parallelize','interrupt','emit']
    print(f'  [{label}] vocab={n}  BAO={bao:.5f}  '
          f'dom=e{dom}({ops[dom] if dom<16 else "?"})  E[name]={e3:.5f}', flush=True)


def main():
    from monad import Engine

    print(f'\n{"="*60}', flush=True)
    print(f'HOLCUS SEDENION BURN — {STAMP}', flush=True)
    print(f'{"="*60}\n', flush=True)

    # ── 1. Load sedenion bin ───────────────────────────────────────────────
    print(f'Loading: {SEDENION_BIN}', flush=True)
    engine = Engine()
    result = engine.load_bin(SEDENION_BIN)
    report_field(engine.crank, 'initial')
    print(f'  load result: {result}\n', flush=True)

    # ── 2. Checkpoint before burn ──────────────────────────────────────────
    pre_backup = os.path.join(BACKUP_DIR, f'monad_sedenion_pre_burn_{STAMP}.bin')
    engine.save_session(pre_backup)
    print(f'Pre-burn checkpoint: {pre_backup}\n', flush=True)

    # ── 3. Burn each corpus in order ───────────────────────────────────────
    total_words = 0
    for name, path, desc in CORPORA:
        print(f'{"─"*50}', flush=True)
        print(f'BURNING: {name}', flush=True)
        print(f'  {desc}', flush=True)
        print(f'  source: {path}', flush=True)

        text = load_text(path)
        if not text.strip():
            print(f'  [SKIP] empty', flush=True)
            continue

        t0 = time.time()
        r  = engine.load(text)
        dt = time.time() - t0

        learned = r.get('words_learned', 0)
        vocab   = r.get('vocab_size', 0)
        total_words += learned
        print(f'  learned={learned}  vocab={vocab}  time={dt:.1f}s', flush=True)
        report_field(engine.crank, name)

        # Checkpoint after each corpus
        ckpt = os.path.join(BACKUP_DIR, f'monad_sedenion_after_{name.lower()}_{STAMP}.bin')
        engine.save_session(ckpt)
        print(f'  checkpoint: {ckpt}\n', flush=True)

    # ── 4. Save final burned sedenion ──────────────────────────────────────
    print(f'{"="*60}', flush=True)
    print(f'BURN COMPLETE — total words added: {total_words}', flush=True)
    report_field(engine.crank, 'final')
    engine.save_session(OUT_BIN)
    print(f'Saved: {OUT_BIN}', flush=True)

    # Also update the canonical SD card store
    import shutil
    shutil.copy2(OUT_BIN, '/media/rendier/0123-4567/bins/current/monad_sedenion.bin')
    print(f'Updated: bins/current/monad_sedenion.bin\n', flush=True)

    # ── 5. Final field state report ────────────────────────────────────────
    crank = engine.crank
    E     = list(getattr(crank, '_E', [])[:16])
    ops   = ['identity','negate','bind','name','apply','abstract','branch','iterate',
             'recurse','allocate','query','dereference','compose','parallelize','interrupt','emit']
    print('FINAL E-VALUES (sedenion dimensions):', flush=True)
    for i, (e, op) in enumerate(zip(E, ops)):
        bar = '█' * int(e / max(E) * 30) if max(E) > 0 else ''
        print(f'  e{i:2d} {op:<14} {e:.5f}  {bar}', flush=True)


if __name__ == '__main__':
    main()
