#!/usr/bin/env python3
"""serve_checks.py -- two checks taken from Kiely, Inference Engineering (2026): latency PERCENTILES (sec. 1.4.1), and a quality check after quantizing (sec. 5.1.3, 6.2.2:
same inputs through original and quantized, cosine similarity of outputs, >= 0.99 to trust it).  Applied to prompt_to_state.PromptToState (no transformer).
Expectation written first: p95 under 20 ms per prompt; float16 weights keep cosine >= 0.99 of the 14-pole output."""
import json, os, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H); sys.argv = ['x']
from prompt_to_state import PromptToState, cos
P = PromptToState()
rows = [json.loads(l) for l in open(os.path.join(H, 'corpus.jsonl'))]
txt = [r['text'] for r in rows if r['source'] in ('goemotions', 'nps_chat', 'probe')][:800]
for t in txt[:20]: P.dose(t)                                           # warm
ms = []
for t in txt: t0 = time.perf_counter(); P.dose(t); ms.append((time.perf_counter() - t0) * 1e3)
p = np.percentile(ms, [50, 95, 99]); print(f'latency over {len(ms)} prompts (ms): p50 {p[0]:.1f}  p95 {p[1]:.1f}  p99 {p[2]:.1f}  max {max(ms):.1f}')
m = P.mdl; X = P.vec.transform(txt); ref = m.predict(X)
w32 = m.coef_.copy(); b32 = m.intercept_.copy()
for name, dt in (('float16', np.float16), ('int8 (per-pole scale)', None)):
    if dt is not None: m.coef_ = w32.astype(dt).astype(np.float32); m.intercept_ = b32.astype(dt).astype(np.float32)
    else:
        sc = np.abs(w32).max(axis=1, keepdims=True) / 127.0; m.coef_ = (np.round(w32 / sc) * sc).astype(np.float32)
    q = m.predict(X); cs = np.array([cos(a, b) for a, b in zip(ref, q)]); mae = np.abs(ref - q).mean()
    print(f'{name}: cosine to float32 output: mean {cs.mean():.5f}, min {cs.min():.5f}, share >= 0.99: {np.mean(cs >= 0.99):.3f}; mean abs diff {mae:.5f} (levels 0-1)')
m.coef_ = w32; m.intercept_ = b32
import joblib; print('usage_model.joblib size', os.path.getsize(os.path.join(H, 'usage_model.joblib')) // 1024, 'KB; coef', w32.shape, w32.nbytes // 1024, 'KB float32 /', w32.astype(np.float16).nbytes // 1024, 'KB float16 /', w32.size // 1024, 'KB int8')
