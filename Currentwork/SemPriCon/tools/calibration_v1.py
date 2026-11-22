#!/usr/bin/env python3
"""calibration_v1.py — the calibration set, version 1: English and written Chinese (Traditional) only.

1 024 words in two halves of 512.  Each concept in the first half (S) has a SIMPLE word; its partner in the second half (L) is a DIFFERENT word of the SAME meaning that carries a
deeper contextual interpretation (circle / sphere ... ball / orb).  Both halves exist directly in English and in written Chinese.
Construction (all from data on disk; nothing typed by hand):
  concept      a WordNet synset with >= 2 single-word English lemmas and >= 2 single-token Mandarin lemmas in the Open Multilingual WordNet (OMW cmn, converted to Traditional with OpenCC s2twp)
  S, L (en)    S = the most frequent lemma (and this synset is one of its first three WordNet senses; nouns, verbs and adjectives only) in English Wikipedia text; L = the lemma with the most WordNet senses among the rarer ones (frequency <= 2/3 of S's, >= 8 occurrences)
  S, L (zh)    the same over the synset's Mandarin lemmas, each REQUIRED to be confirmed by CC-CEDICT (its English definition contains a lemma of the synset); L has the most CEDICT definitions
               among the rarer ones (frequency <= 2/3 of S's, >= 2 occurrences)
  selection    512 concepts by depth evidence  log10(f_S/f_L) in English + in Chinese (each capped at 3) + a polysemy term, with at most 15 % of the concepts from one lexicographer class
Writes calibration/calibration_v1_en_zh.tsv and calibration/FROZEN.sha256."""
import collections, csv, hashlib, io, json, math, os, re, subprocess, sys, zipfile, unicodedata as ud
from nltk.corpus import wordnet as wn
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); C = os.path.join(ROOT, "corpora"); OUT = os.path.join(ROOT, "calibration")
EN_CHARS, ZH_CHARS = 80_000_000, 40_000_000


def text_of(path, chars):
    pf = pq.ParquetFile(path); out, n = [], 0
    for g in range(pf.num_row_groups):
        for t in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]: out.append(t); n += len(t)
        if n >= chars: break
    return "\n".join(out)[:chars]


def opencc(cfg, words):
    r = subprocess.run([os.path.join(HERE, "opencc_local.sh"), cfg], input="\n".join(words), capture_output=True, text=True).stdout.split("\n"); return r[:len(words)]


# 1. candidate synsets
cands = []
for s in wn.all_synsets():
    E = [l for l in s.lemma_names() if l.isascii() and l.isalpha() and l.islower()]
    Z = [z for z in s.lemma_names("cmn") if "_" not in z and " " not in z]
    if len(E) >= 2 and len(Z) >= 2: cands.append((s, E, Z))
print("synsets with >=2 English and >=2 Mandarin lemmas:", len(cands), flush=True)
simp = sorted({z for _, _, Z in cands for z in Z}); trad = dict(zip(simp, opencc("s2twp", simp)))
# 2. CC-CEDICT: traditional headword -> definition words, number of definitions
zf = zipfile.ZipFile(os.path.join(C, "zh", "structure", "cedict_1_0_ts_utf-8_mdbg.zip")); ced = collections.defaultdict(lambda: [set(), 0])
for line in io.TextIOWrapper(zf.open(zf.namelist()[0]), encoding="utf-8"):
    if line.startswith("#"): continue
    m = re.match(r"(\S+) (\S+) \[[^\]]*\] /(.*)/", line)
    if not m: continue
    d = ced[m.group(1)]; defs = m.group(3).split("/"); d[1] += len(defs)
    for x in defs: d[0].update(re.findall(r"[a-z]+", x.lower()))
# 3. frequencies (cached: they depend only on the corpora and the candidate list)
import pickle
cache = os.path.join(C, "derived", "calibration_v1_freq.pkl")
if os.path.exists(cache): cnt_en, freq_zh = pickle.load(open(cache, "rb")); print("frequencies from cache", flush=True)
else:
    en_words = {e for _, E, _ in cands for e in E}; en = text_of(os.path.join(C, "wikipedia", "en-00.parquet"), EN_CHARS)
    cnt_en = collections.Counter(w for w in re.findall(r"[a-z]+", en.lower()) if w in en_words); del en; print("english frequencies done", flush=True)
    zh = text_of(os.path.join(C, "wikipedia", "zh-00.parquet"), ZH_CHARS); forms = set(trad.values()) | set(simp); cz = collections.Counter()
    for n_ in sorted({len(f) for f in forms}):
        cs = {f for f in forms if len(f) == n_}; cz.update(filter(cs.__contains__, (zh[i:i + n_] for i in range(len(zh) - n_ + 1))))
    del zh; freq_zh = {s_: cz[trad[s_]] + (cz[s_] if s_ != trad[s_] else 0) for s_ in simp}; print("chinese frequencies done", flush=True)
    pickle.dump((cnt_en, freq_zh), open(cache, "wb"))
# 4. pairs
pairs = []
for s, E, Z in cands:
    fe = sorted(E, key=lambda e: -cnt_en[e]); S_en = fe[0]
    L_en_c = [e for e in fe[1:] if cnt_en[e] >= 8 and cnt_en[e] * 1.5 <= cnt_en[S_en]]
    if s.pos() not in "nva" or s not in wn.synsets(S_en, s.pos())[:3] or cnt_en[S_en] < 30 or not L_en_c: continue        # noun, verb or adjective; this synset is one of S's first three WordNet senses
    L_en = max(L_en_c, key=lambda e: (len(wn.synsets(e)), cnt_en[e]))
    ok = [z for z in Z if trad[z] in ced and set(E) & ced[trad[z]][0]]
    ok = sorted(set(ok), key=lambda z: -freq_zh[z])
    if len(ok) < 2 or freq_zh[ok[0]] < 10: continue
    S_zh = ok[0]; L_zh_c = [z for z in ok[1:] if freq_zh[z] >= 2 and freq_zh[z] * 1.5 <= freq_zh[S_zh] and trad[z] != trad[S_zh]]
    if not L_zh_c: continue
    L_zh = max(L_zh_c, key=lambda z: (ced[trad[z]][1], freq_zh[z]))
    depth = min(math.log10(cnt_en[S_en] / cnt_en[L_en]), 3) + min(math.log10(freq_zh[S_zh] / max(freq_zh[L_zh], 1)), 3) + 0.1 * min(max(len(wn.synsets(L_en)) - len(wn.synsets(S_en)), 0), 10)
    pairs.append(dict(s=s, S_en=S_en, L_en=L_en, S_zh=trad[S_zh], L_zh=trad[L_zh], depth=depth, fe=(cnt_en[S_en], cnt_en[L_en]), fz=(freq_zh[S_zh], freq_zh[L_zh]),
                      poly=(len(wn.synsets(S_en)), len(wn.synsets(L_en))), cedict=ced[trad[L_zh]][1]))
print("pairs:", len(pairs), flush=True)
# 5. selection with a cap per lexicographer class; one pair per surface word
sel, per, used = [], collections.Counter(), set()
for p in sorted(pairs, key=lambda p: -p["depth"]):
    ln = p["s"].lexname()
    if per[ln] >= 103 or {p["S_en"], p["L_en"], p["S_zh"], p["L_zh"]} & used: continue
    sel.append(p); per[ln] += 1; used |= {p["S_en"], p["L_en"], p["S_zh"], p["L_zh"]}
    if len(sel) == 512: break
sel.sort(key=lambda p: (p["s"].lexname(), p["s"].name()))
# 6. UK spellings
us2uk = {}
for line in open(os.path.join(C, "lexicon", "varcon.txt"), encoding="latin-1"):
    if line.startswith("#") or ":" not in line: continue
    us = uk = None
    for part in line.strip().split(" / "):
        tags, _, w = part.partition(":"); tg = tags.replace("v", "").split(); w = w.strip().lower()
        if "A" in tg and us is None: us = w
        if "B" in tg and uk is None: uk = w
    if us and uk and us != uk: us2uk[us] = uk
cols = ["id", "half", "pair", "pos", "en_us", "en_uk", "zh_trad", "synset", "lexname", "freq_en", "freq_zh", "wn_senses", "cedict_defs", "depth_evidence", "definition"]
path = os.path.join(OUT, "calibration_v1_en_zh.tsv")
if os.path.exists(path): os.chmod(path, 0o644)
with open(path, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t"); w.writerow(cols); i = 0
    for k, p in enumerate(sel, 1):
        for half, e, z, fe_, fz_, po in (("S", p["S_en"], p["S_zh"], p["fe"][0], p["fz"][0], p["poly"][0]), ("L", p["L_en"], p["L_zh"], p["fe"][1], p["fz"][1], p["poly"][1])):
            i += 1; w.writerow([f"K{i:04d}", half, k, p["s"].pos(), e, us2uk.get(e, e), z, p["s"].name(), p["s"].lexname(), fe_, fz_, po, p["cedict"] if half == "L" else "", f"{p['depth']:.2f}", p["s"].definition()])
h = hashlib.sha256(open(path, "rb").read()).hexdigest()
open(os.path.join(OUT, "FROZEN.sha256"), "w").write(f"{h}  calibration_v1_en_zh.tsv\n"); os.chmod(path, 0o444)
print("wrote", path, "rows", 2 * len(sel), "sha256", h)
print("lexnames:", dict(per.most_common(8)), "| median depth", sorted(p["depth"] for p in sel)[len(sel) // 2])
