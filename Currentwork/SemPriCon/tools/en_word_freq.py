#!/usr/bin/env python3
"""en_word_freq.py — frequency of every lowercase [a-z]+ word in the first 80 000 000 characters of the English Wikipedia dump on disk (corpora/wikipedia/en-00.parquet).
Writes corpora/derived/en_word_freq_v3.pkl (a Counter; words seen once are dropped).  Needs pyarrow (system python3)."""
import collections, os, pickle, re
import pyarrow.parquet as pq
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pf = pq.ParquetFile(os.path.join(ROOT, "corpora", "wikipedia", "en-00.parquet")); cnt = collections.Counter(); n = 0; rx = re.compile(r"[a-z]+")
for g in range(pf.num_row_groups):
    for t in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]:
        cnt.update(rx.findall(t.lower())); n += len(t)
    if n >= 80_000_000: break
cnt = collections.Counter({w: c for w, c in cnt.items() if c > 1})
pickle.dump(cnt, open(os.path.join(ROOT, "corpora", "derived", "en_word_freq_v3.pkl"), "wb"))
print("characters scanned", n, "distinct words (>1)", len(cnt), "total", sum(cnt.values()))
