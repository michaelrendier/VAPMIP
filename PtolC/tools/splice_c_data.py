#!/usr/bin/env python3
"""splice_c_data.py -- put the generated tables into ptol.c and monad_harness.c between their BEGIN/END GENERATED markers.   (2026-11-25)
Run after export_c_monad_data.py.  Idempotent.  The two C files stay self-contained: the tables live inside them, not in a third file."""
import os, re
PC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for c, d, tag in (('ptol.c', 'ptol_voice_data.txt', 'ptol_voice_data'), ('monad_harness.c', 'harness_data.txt', 'harness_data')):
    s = open(os.path.join(PC, c)).read(); b, e = '/* BEGIN GENERATED %s */' % tag, '/* END GENERATED %s */' % tag
    if b not in s or e not in s: print('skipped', c, '(no markers yet)'); continue
    s = s[:s.index(b) + len(b)] + '\n' + open(os.path.join(PC, d)).read() + s[s.index(e):]
    open(os.path.join(PC, c), 'w').write(s); print('spliced', c)
