#!/usr/bin/env python3
"""zh_char_freq.py — frequency of every Han character in the first 40 000 000 characters of the Chinese Wikipedia dump on disk (corpora/wikipedia/zh-00.parquet).
Writes corpora/derived/zh_char_freq_v3.pkl (a Counter).  Needs pyarrow (system python3).  The text mixes Simplified and Traditional forms; callers add the two forms of a character."""
import collections, os, pickle, sys
import pyarrow.parquet as pq
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pf = pq.ParquetFile(os.path.join(ROOT, "corpora", "wikipedia", "zh-00.parquet")); cnt = collections.Counter(); n = 0
for g in range(pf.num_row_groups):
    for t in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]:
        cnt.update(c for c in t if "㐀" <= c <= "鿿" or "\U00020000" <= c <= "\U0002ffff"); n += len(t)
    if n >= 40_000_000: break
pickle.dump(cnt, open(os.path.join(ROOT, "corpora", "derived", "zh_char_freq_v3.pkl"), "wb"))
print("characters scanned", n, "distinct Han", len(cnt), "total Han", sum(cnt.values()))
