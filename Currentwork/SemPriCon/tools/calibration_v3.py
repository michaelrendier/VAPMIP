#!/usr/bin/env python3
"""calibration_v3.py — the calibration set, version 3.0 (Fresh Start v3.0): English words and SINGLE Chinese characters (Traditional).

Changed from calibration_v1.py (v1 is frozen and untouched): every Chinese word is ONE character that lies in the engine's Han alphabet (the M2/M4 mechanism maps single characters only). Because
the Open Multilingual WordNet holds only 135 synsets with two single-character Mandarin lemmas, the Chinese candidates of a concept are the single characters whose CC-CEDICT entry lists one of the
synset's English lemmas as a whole gloss (the DIRECT rule of the v2 experiment). Everything else is the same protocol: 2 x 512, S simple / L deeper, direct analogues, CC-CEDICT confirmation, one use per surface word.

1 024 words in two halves of 512.  Each concept in the first half (S) has a SIMPLE word; its partner in the second half (L) is a DIFFERENT word of the SAME meaning that carries a
deeper contextual interpretation (circle / sphere ... ball / orb).  Both halves exist directly in English and in written Chinese.
Construction (all from data on disk; nothing typed by hand):
  concept      a WordNet synset with >= 2 single-word English lemmas and >= 2 single-token Mandarin lemmas in the Open Multilingual WordNet (OMW cmn, converted to Traditional with OpenCC s2twp)
  S, L (en)    S = the most frequent lemma (and this synset is one of its first three WordNet senses; nouns, verbs and adjectives only) in English Wikipedia text; L = the lemma with the most WordNet senses among the rarer ones (frequency <= 2/3 of S's, >= 8 occurrences)
  S, L (zh)    the same over the synset's Mandarin lemmas, each REQUIRED to be confirmed by CC-CEDICT (its English definition contains a lemma of the synset); L has the most CEDICT definitions
               among the rarer ones (frequency <= 2/3 of S's, >= 2 occurrences)
  selection    512 concepts by depth evidence  log10(f_S/f_L) in English + in Chinese (each capped at 3) + a polysemy term, with at most 15 % of the concepts from one lexicographer class
Writes calibration/calibration_v3_en_zh.tsv and calibration/FROZEN_v3.sha256."""
import collections, csv, hashlib, io, json, math, os, re, subprocess, sys, zipfile, unicodedata as ud
from nltk.corpus import wordnet as wn
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); C = os.path.join(ROOT, "corpora"); OUT = os.path.join(ROOT, "calibration")
EN_CHARS, ZH_CHARS = 80_000_000, 40_000_000


def text_of(path, chars):
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(path); out, n = [], 0
    for g in range(pf.num_row_groups):
        for t in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]: out.append(t); n += len(t)
        if n >= chars: break
    return "\n".join(out)[:chars]


def opencc(cfg, words):
    r = subprocess.run([os.path.join(HERE, "opencc_local.sh"), cfg], input="\n".join(words), capture_output=True, text=True).stdout.split("\n"); return r[:len(words)]


# 1. candidate synsets: >= 2 single-word English lemmas
cands = []
for s in wn.all_synsets():
    E = [l for l in s.lemma_names() if l.isascii() and l.isalpha() and l.islower()]
    if len(E) >= 2 and s.pos() in "nva": cands.append((s, E))
print("synsets with >=2 English lemmas (n/v/a):", len(cands), flush=True)
# 2. CC-CEDICT: every SINGLE Han character in the engine's alphabet whose entry lists an English word as a WHOLE gloss ("DIRECT": the protocol of the v2 experiment)
sys.path.insert(0, HERE); import zh_structure
ALPHA = {chr(c) for c in zh_structure.load()["alpha"]}
zf = zipfile.ZipFile(os.path.join(C, "zh", "structure", "cedict_1_0_ts_utf-8_mdbg.zip")); gloss = collections.defaultdict(set); ndef = collections.Counter()
for line in io.TextIOWrapper(zf.open(zf.namelist()[0]), encoding="utf-8"):
    if line.startswith("#"): continue
    m = re.match(r"(\S+) (\S+) \[[^\]]*\] /(.*)/", line)
    if not m or len(m.group(1)) != 1 or m.group(1) not in ALPHA: continue
    ch = m.group(1); defs = m.group(3).split("/"); ndef[ch] += len(defs)
    for pos_, d in enumerate(defs):
        if pos_ > int(os.environ.get("GLOSS_POS", "3")): break                                                  # the gloss must be among the character's first four definitions
        d = re.sub(r"\([^)]*\)", "", d.lower()).strip(); d = re.sub(r"^(to|a|an|the) ", "", d).strip()
        if re.fullmatch(r"[a-z]+", d): gloss[d].add(ch)
# 3. frequencies: English words from tools/en_word_freq.py, Chinese characters from tools/zh_char_freq.py (the same 80 M / 40 M character windows as calibration_v1)
import pickle
cnt_en = pickle.load(open(os.path.join(C, "derived", "en_word_freq_v3.pkl"), "rb"))      # tools/en_word_freq.py
cz = pickle.load(open(os.path.join(C, "derived", "zh_char_freq_v3.pkl"), "rb"))
chars = sorted({c for _, E in cands for e in E for c in gloss.get(e, ())})
simp = dict(zip(chars, opencc("t2s", chars)))
freq_zh = {c: cz[c] + (cz[simp[c]] if simp[c] != c else 0) for c in chars}
missing = [e for _, E in cands for e in E if e not in cnt_en]
print("English lemmas missing from the frequency cache:", len(set(missing)), "(treated as frequency 0)", flush=True)
# 4. pairs
pairs = []
for s, E in cands:
    fe = sorted(E, key=lambda e: -cnt_en[e]); S_en = fe[0]
    L_en_c = [e for e in fe[1:] if cnt_en[e] >= 8 and cnt_en[e] * 1.5 <= cnt_en[S_en]]
    if s not in wn.synsets(S_en, s.pos())[:3] or cnt_en[S_en] < 30 or not L_en_c: continue          # this synset is one of S's first three WordNet senses
    L_en = max(L_en_c, key=lambda e: (len(wn.synsets(e)), cnt_en[e]))
    Zs = sorted(gloss.get(S_en, ()), key=lambda c: -freq_zh[c])               # S's Chinese word is a direct analogue of the English S word (a whole gloss); L's is any single character whose CEDICT gloss is a lemma of the synset (the synset-level rule of calibration_v1)
    if not Zs or freq_zh[Zs[0]] < 10: continue
    S_zh = Zs[0]; L_zh_c = [c for c in {c for e in E for c in gloss.get(e, ())} if c != S_zh and freq_zh[c] >= 2 and freq_zh[c] * 1.5 <= freq_zh[S_zh]]
    if not L_zh_c: continue
    L_zh = max(L_zh_c, key=lambda c: (ndef[c], freq_zh[c]))
    depth = min(math.log10(cnt_en[S_en] / cnt_en[L_en]), 3) + min(math.log10(freq_zh[S_zh] / max(freq_zh[L_zh], 1)), 3) + 0.1 * min(max(len(wn.synsets(L_en)) - len(wn.synsets(S_en)), 0), 10)
    pairs.append(dict(s=s, S_en=S_en, L_en=L_en, Zs=[c for c in Zs if freq_zh[c] >= 10], Zall=sorted({c for e in E for c in gloss.get(e, ())}), depth=depth))
print("pairs:", len(pairs), flush=True)
# 5. selection with a cap per lexicographer class; one pair per surface word.  A character already taken is replaced by the next direct analogue (S: by frequency; L: by CEDICT definitions, then frequency).
sel, per, used = [], collections.Counter(), set()
for p in sorted(pairs, key=lambda p: -p["depth"]):
    ln = p["s"].lexname()
    if per[ln] >= 103 or {p["S_en"], p["L_en"]} & used: continue
    pick = None
    for S_zh in p["Zs"]:
        if S_zh in used: continue
        Lc = [c for c in p["Zall"] if c != S_zh and c not in used and freq_zh[c] >= 2 and freq_zh[c] * 1.5 <= freq_zh[S_zh]]
        if Lc: pick = (S_zh, max(Lc, key=lambda c: (ndef[c], freq_zh[c]))); break
    if pick is None: continue
    S_zh, L_zh = pick; S_en, L_en = p["S_en"], p["L_en"]
    p.update(S_zh=S_zh, L_zh=L_zh, fe=(cnt_en[S_en], cnt_en[L_en]), fz=(freq_zh[S_zh], freq_zh[L_zh]), poly=(len(wn.synsets(S_en)), len(wn.synsets(L_en))), cedict=ndef[L_zh],
             depth=min(math.log10(cnt_en[S_en] / cnt_en[L_en]), 3) + min(math.log10(freq_zh[S_zh] / max(freq_zh[L_zh], 1)), 3) + 0.1 * min(max(len(wn.synsets(L_en)) - len(wn.synsets(S_en)), 0), 10))
    sel.append(p); per[ln] += 1; used |= {S_en, L_en, S_zh, L_zh}
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
path = os.path.join(OUT, "calibration_v3_en_zh.tsv")
if os.path.exists(path): os.chmod(path, 0o644)
with open(path, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t"); w.writerow(cols); i = 0
    for k, p in enumerate(sel, 1):
        for half, e, z, fe_, fz_, po in (("S", p["S_en"], p["S_zh"], p["fe"][0], p["fz"][0], p["poly"][0]), ("L", p["L_en"], p["L_zh"], p["fe"][1], p["fz"][1], p["poly"][1])):
            i += 1; w.writerow([f"K{i:04d}", half, k, p["s"].pos(), e, us2uk.get(e, e), z, p["s"].name(), p["s"].lexname(), fe_, fz_, po, p["cedict"] if half == "L" else "", f"{p['depth']:.2f}", p["s"].definition()])
h = hashlib.sha256(open(path, "rb").read()).hexdigest()
open(os.path.join(OUT, "FROZEN_v3.sha256"), "w").write(f"{h}  calibration_v3_en_zh.tsv\n"); os.chmod(path, 0o444)
print("wrote", path, "rows", 2 * len(sel), "sha256", h)
print("lexnames:", dict(per.most_common(8)), "| median depth", sorted(p["depth"] for p in sel)[len(sel) // 2])
