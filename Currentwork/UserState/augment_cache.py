#!/usr/bin/env python3
"""Add the Empath domain counts to every record of raw_cache.jsonl (v2 meter), in place."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..'))
from user_state import empath_counts
p = os.path.join(H, 'raw_cache.jsonl'); rows = [json.loads(l) for l in open(p)]
for r in rows:
    if 'empath' not in r: r['empath'] = empath_counts(r['text'])
with open(p, 'w') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(rows), 'records, empath added')
