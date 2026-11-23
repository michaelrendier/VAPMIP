#!/usr/bin/env python3
"""Stage B (Schocken Complete Stories): raw meters on every sentence (resumable), with the cost of each pathway timed separately.
Writes schocken_raw.jsonl (local only) and kafka_cost.json (seconds per pathway over the whole run)."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from user_state import RawMeters
H = os.path.dirname(os.path.abspath(__file__))
paras = [json.loads(l) for l in open(os.path.join(H, 'schocken_paras.jsonl'))]
sents = [{'id': f"{p['id']}-s{i:03d}", 'text': s} for p in paras for i, s in enumerate(p['sentences'])]
cache = os.path.join(H, 'schocken_raw.jsonl'); done = set()
if os.path.exists(cache): done = {json.loads(l)['id'] for l in open(cache)}
todo = sorted((s for s in sents if s['id'] not in done), key=lambda s: len(s['text']))
print(len(sents), 'sentences,', len(done), 'cached,', len(todo), 'to do', flush=True)
rm = RawMeters(); B = 64; t0 = time.time()
with open(cache, 'a') as f:
    for i in range(0, len(todo), B):
        ch = todo[i:i + B]; res = rm.batch([c['text'] for c in ch], batch_size=32)
        for c, r in zip(ch, res): r['id'] = c['id']; f.write(json.dumps(r, ensure_ascii=False) + '\n')
        f.flush(); print(f'[schocken raw] {min(i + B, len(todo))}/{len(todo)} {time.time() - t0:.0f}s', flush=True)
print('SCHOCKEN RAW DONE', flush=True)
