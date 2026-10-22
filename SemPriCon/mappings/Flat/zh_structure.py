#!/usr/bin/env python3
"""zh_structure.py — the Chinese data on file, one record per Han character of the engine's alphabet (gen_alphabet.zh(), 97,518 characters).  Read-only on corpora/.

record fields: rad (Kangxi radical 1..214, from Unihan kRSUnicode), res (residual strokes), tot (kTotalStrokes), ids (cjkvi-ids decomposition, first entry),
mmh (makemeahanzi: radical, decomposition, etymology type/phonetic/semantic), defn (Unihan kDefinition), moe (count of the character in the MOE dictionary text),
and the MOE two-character headwords (list of (c1, c2)).  Cached in data/zh_structure.pkl.

    from zh_structure import load; S = load()
"""
import collections, io, json, lzma, os, pickle, re, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dprint import dprint
import gen_alphabet
ROOT = os.path.abspath(os.path.join(HERE, ".."))
Z = os.path.join(ROOT, "corpora", "zh")
CACHE = os.path.join(ROOT, "data", "zh_structure.pkl")

def build():
    alpha = gen_alphabet.zh(); aset = set(alpha); dprint("alphabet size", len(alpha))
    zf = zipfile.ZipFile(os.path.join(Z, "structure", "Unihan.zip")); U = collections.defaultdict(dict)
    for n in zf.namelist():
        for line in io.TextIOWrapper(zf.open(n), encoding="utf-8"):
            if line.startswith("#") or "\t" not in line: continue
            cp, k, v = line.rstrip("\n").split("\t", 2)
            if k in ("kRSUnicode", "kTotalStrokes", "kDefinition", "kSemanticVariant", "kTraditionalVariant", "kSimplifiedVariant", "kMandarin"):
                U[int(cp[2:], 16)][k] = v
    ids = {}
    for line in open(os.path.join(Z, "structure", "cjkvi-ids.txt"), encoding="utf-8"):
        if line.startswith("#") or "\t" not in line: continue
        f = line.rstrip("\n").split("\t")
        if len(f) >= 3: ids[f[1]] = re.sub(r"\[[A-Z]+\]", "", f[2])
    mmh = {}
    for line in open(os.path.join(Z, "structure", "makemeahanzi-dictionary.txt"), encoding="utf-8"):
        j = json.loads(line); mmh[j["character"]] = j
    moe_cnt = collections.Counter(); two = []
    with lzma.open(os.path.join(Z, "moedict", "dict-revised.json.xz"), "rt", encoding="utf-8") as fh:
        D = json.load(fh)
    for e in D:
        t = e.get("title", "")
        han = [c for c in t if ord(c) >= 0x3400]
        if len(han) == 2 and len(t) == 2: two.append((t[0], t[1]))
        for c in t: moe_cnt[c] += 1
        for h in e.get("heteronyms", []):
            for d_ in h.get("definitions", []):
                for k in ("def", "example", "quote"):
                    v = d_.get(k)
                    if isinstance(v, str):
                        for c in v: moe_cnt[c] += 1
    S = {}
    for cp in alpha:
        c = chr(cp); u = U.get(cp, {}); rec = {"cp": cp}
        m = re.match(r"(\d+)('*)\.(-?\d+)", u.get("kRSUnicode", ""))
        if m: rec["rad"] = int(m.group(1)); rec["res"] = int(m.group(3))
        if "kTotalStrokes" in u: rec["tot"] = int(u["kTotalStrokes"].split()[0])
        if c in ids: rec["ids"] = ids[c]
        if c in mmh: rec["mmh"] = {k: mmh[c].get(k) for k in ("radical", "decomposition", "etymology", "definition")}
        if "kDefinition" in u: rec["defn"] = u["kDefinition"]
        if "kMandarin" in u: rec["mand"] = u["kMandarin"].split()[0]
        for kk, nm in (("kSemanticVariant", "sem"), ("kTraditionalVariant", "trad"), ("kSimplifiedVariant", "simp")):
            if kk in u: rec[nm] = u[kk]
        rec["moe"] = moe_cnt.get(c, 0)
        S[c] = rec
    out = {"chars": S, "alpha": alpha, "two": two}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    pickle.dump(out, open(CACHE, "wb"))
    return out

def load():
    if os.path.exists(CACHE): return pickle.load(open(CACHE, "rb"))
    return build()

if __name__ == "__main__":
    S = build(); C = S["chars"]
    print("characters", len(C), "with radical", sum("rad" in r for r in C.values()), "with strokes", sum("tot" in r for r in C.values()),
          "with ids", sum("ids" in r for r in C.values()), "with mmh", sum("mmh" in r for r in C.values()), "in MOE text", sum(r["moe"] > 0 for r in C.values()),
          "two-char MOE headwords", len(S["two"]))
