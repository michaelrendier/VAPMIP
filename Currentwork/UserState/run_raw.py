#!/usr/bin/env python3
"""Stage 1: run the raw meters (VADER, three models, arousal features, dialogue act) over corpus.jsonl and cache them to
raw_cache.jsonl (resumable; one JSON per prompt).  Scoring and statistics (run_battery.py) read the cache, so the mapping can be
retooled and re-run without touching the models."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from user_state import RawMeters
H = os.path.dirname(os.path.abspath(__file__))
corp = [json.loads(l) for l in open(os.path.join(H, 'corpus.jsonl'))]
cache = os.path.join(H, 'raw_cache.jsonl')
done = set()
if os.path.exists(cache):
    done = {json.loads(l)['id'] for l in open(cache)}
todo = sorted((c for c in corp if c['id'] not in done), key=lambda c: len(c['text']))
print(f'{len(corp)} prompts, {len(done)} cached, {len(todo)} to do', flush=True)
rm = RawMeters()
t0 = time.time(); B = 64
with open(cache, 'a') as f:
    for i in range(0, len(todo), B):
        chunk = todo[i:i + B]
        res = rm.batch([c['text'] for c in chunk], batch_size=32)
        for c, r in zip(chunk, res):
            r['id'] = c['id']; f.write(json.dumps(r, ensure_ascii=False) + '\n')
        f.flush()
        print(f'[raw] {min(i + B, len(todo))}/{len(todo)}  {time.time() - t0:.0f}s', flush=True)
print('RAW DONE', flush=True)
