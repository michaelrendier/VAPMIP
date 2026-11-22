#!/usr/bin/env python3
"""word_freq.py — how common each calibration candidate is in its language's Wikipedia text (corpora/wikipedia/*.parquet).

Candidates: Swahili and Quechua headwords (Wiktionary gloss rank <= 9) for the keys in corpora/derived/omw_candidates.json; Mandarin, Finnish and Indonesian lemmas from the same file.
Latin-script languages: exact lower-case token counts over the first CHARS characters.  Mandarin: n-gram counts of the Traditional and the Simplified form (the dump mixes both) over 40 M characters.
Writes corpora/derived/word_freq.json  {lang: {word: count}}  (Chinese keyed by the Traditional form)."""
import collections, json, os, re, subprocess, sys
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); D = os.path.join(ROOT, "corpora", "derived")
CHARS = int(os.environ.get("FREQ_CHARS", 60_000_000))
FILES = {"Quechua": "qu.parquet", "Swahili": "sw.parquet", "Finnish": "fi-00.parquet", "Indonesian": "id-00.parquet", "Chinese": "zh-00.parquet"}
om = json.load(open(os.path.join(D, "omw_candidates.json")))
ix = {l: json.load(open(os.path.join(D, f"concept_index_{l}.json"))) for l in ("Swahili", "Quechua")}
cands = {"Swahili": {hw for k in om for hw, r, _ in ix["Swahili"][k] if r <= 9}, "Quechua": {hw for k in om for hw, r, _ in ix["Quechua"][k] if r <= 9},
         "Finnish": {x for v in om.values() for x in v["fin"]}, "Indonesian": {x for v in om.values() for x in v["ind"]}}
zhpairs = {(t, s) for v in om.values() for s, t in zip(v["cmn_simp"], v["cmn_trad"])}
print({l: len(c) for l, c in cands.items()}, "zh", len(zhpairs), flush=True)
out = {}
for l in FILES:
    text, n = [], 0
    pf = pq.ParquetFile(os.path.join(ROOT, "corpora", "wikipedia", FILES[l]))
    for g in range(pf.num_row_groups):
        for t in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]: text.append(t); n += len(t)
        if n >= CHARS: break
    text = "\n".join(text)[:CHARS]; print(l, "chars", len(text), flush=True)
    if l == "Chinese":
        text = text[:40_000_000]; forms = {f for p in zhpairs for f in p}; cnt = collections.Counter()
        for n_ in sorted({len(f) for f in forms}):
            cs = {f for f in forms if len(f) == n_}
            cnt.update(filter(cs.__contains__, (text[i:i + n_] for i in range(len(text) - n_ + 1))))
        out[l] = {}
        for t_, s_ in zhpairs: out[l][t_] = max(out[l].get(t_, 0), cnt[t_] + (cnt[s_] if s_ != t_ else 0))
    else:
        c = collections.Counter(re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", text.lower())); out[l] = {h: c.get(h.lower(), 0) for h in cands[l]}
    print(l, "attested (>=3):", sum(1 for v in out[l].values() if v >= 3), "of", len(out[l]), flush=True)
json.dump(out, open(os.path.join(D, "word_freq.json"), "w"), ensure_ascii=False)
