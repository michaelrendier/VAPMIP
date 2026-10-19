#!/usr/bin/env python3
"""zh_census.py — what the Chinese-only baseline sources contain, measured.

Reads corpora/zh/*: MOE 重編國語辭典修訂本 (moedict), CC-CEDICT, 說文解字 / 爾雅 (gujilab, CC0), Unihan, makemeahanzi, cjkvi-ids.
Reports: sizes; word-length distribution (headwords); distinct characters; script purity (Simplified-only characters, by Unihan variants);
marker characters of Cantonese / Hokkien-Min written forms; character structure types; 爾雅 chapters.  Writes corpora/derived/zh_census.json."""
import collections, io, json, lzma, os, re, sys, unicodedata as ud, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); Z = os.path.join(ROOT, "corpora", "zh")
OUT = os.path.join(ROOT, "corpora", "derived"); os.makedirs(OUT, exist_ok=True)
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0002FA1F\U00030000-\U000323AF]")
# characters written for Cantonese words (not used in standard written Mandarin) and for Hokkien / Min words; a marker is a flag, not a verdict
CANTONESE = set("嘅唔咗喺冇佢哋啲嘢咁嚟咩乜嗰畀睇俾攞嘥啱冧瞓諗嚿噉啩嘛㗎喎囉啫喇咋架")  - set("嘛囉喇咋架")   # 嘛囉喇架 occur in Mandarin
HOKKIEN_MIN = set("袂佮囝厝甲𪜶伊𠊎")  - set("甲伊")                                              # 甲 伊 occur in Mandarin
rep = {}


def unihan():
    zf = zipfile.ZipFile(os.path.join(Z, "structure", "Unihan.zip")); d = collections.defaultdict(dict)
    for n in zf.namelist():
        for line in io.TextIOWrapper(zf.open(n), encoding="utf-8"):
            if line.startswith("#") or "\t" not in line: continue
            cp, k, v = line.rstrip("\n").split("\t", 2); d[chr(int(cp[2:], 16))][k] = v
    return d


U = unihan(); rep["unihan_characters"] = len(U)
SIMP_ONLY = {c for c, f in U.items() if "kTraditionalVariant" in f and f["kTraditionalVariant"].split()[0] != "U+%04X" % ord(c) and not "kSimplifiedVariant" in f}
rep["unihan_fields"] = {k: sum(1 for f in U.values() if k in f) for k in ["kDefinition", "kMandarin", "kCantonese", "kFrequency", "kGradeLevel", "kTotalStrokes", "kRSUnicode", "kTraditionalVariant", "kSimplifiedVariant", "kSemanticVariant", "kZVariant", "kIICore"]}
rep["simplified_only_by_unihan"] = len(SIMP_ONLY)

# MOE dictionary
moe = json.load(lzma.open(os.path.join(Z, "moedict", "dict-revised.json.xz"), "rt", encoding="utf-8"))
titles = [e["title"] for e in moe]; L = collections.Counter(len(t) for t in titles)
text_all = "".join(json.dumps(e, ensure_ascii=False) for e in moe)
chars = collections.Counter(c for c in text_all if HAN.match(c))
rep["moe"] = dict(entries=len(moe), headword_length={k: L[k] for k in sorted(L)[:8]}, two_char_share=round(L[2] / len(titles), 3), distinct_han_in_text=len(chars),
                  distinct_han_in_titles=len({c for t in titles for c in t if HAN.match(c)}), han_chars_in_text=sum(chars.values()),
                  simplified_only_chars=sum(n for c, n in chars.items() if c in SIMP_ONLY), cantonese_markers=sum(n for c, n in chars.items() if c in CANTONESE),
                  hokkien_min_markers=sum(n for c, n in chars.items() if c in HOKKIEN_MIN), keys=sorted(moe[0].keys()), heteronym_keys=sorted(moe[0]["heteronyms"][0].keys()))
rep["moe"]["top_simplified_only"] = [(c, n) for c, n in chars.most_common() if c in SIMP_ONLY][:12]
rep["moe"]["cantonese_marker_chars"] = [(c, chars[c]) for c in CANTONESE if chars[c]]
rep["moe"]["coverage"] = {p: next(i + 1 for i, s in enumerate(__import__("itertools").accumulate(n for _, n in chars.most_common())) if s >= p * sum(chars.values())) for p in (0.5, 0.9, 0.99)}
# CC-CEDICT
zf = zipfile.ZipFile(os.path.join(Z, "structure", "cedict_1_0_ts_utf-8_mdbg.zip")); ced = [l for l in io.TextIOWrapper(zf.open(zf.namelist()[0]), encoding="utf-8") if not l.startswith("#")]
tw = [l.split(" ")[0] for l in ced]; CL = collections.Counter(len(t) for t in tw)
rep["cedict"] = dict(entries=len(ced), traditional_headword_length={k: CL[k] for k in sorted(CL)[:7]}, two_char_share=round(CL[2] / len(ced), 3))
# classical
sw = json.load(open(os.path.join(Z, "classical", "shuowen.json"), encoding="utf-8")); rep["shuowen"] = dict(type=type(sw).__name__, n=len(sw), sample=json.dumps(sw[0] if isinstance(sw, list) else list(sw.items())[0], ensure_ascii=False)[:300])
ey = json.load(open(os.path.join(Z, "classical", "erya.json"), encoding="utf-8")); rep["erya"] = dict(type=type(ey).__name__, n=len(ey), sample=json.dumps(ey[0] if isinstance(ey, list) else list(ey.items())[0], ensure_ascii=False)[:300])
# makemeahanzi, cjkvi-ids
mm = [json.loads(l) for l in open(os.path.join(Z, "structure", "makemeahanzi-dictionary.txt"), encoding="utf-8")]
et = collections.Counter((m.get("etymology") or {}).get("type", "none") for m in mm); rep["makemeahanzi"] = dict(characters=len(mm), etymology_types=dict(et), pictophonetic_share=round(et["pictophonetic"] / len(mm), 3))
ids = [l for l in open(os.path.join(Z, "structure", "cjkvi-ids.txt"), encoding="utf-8") if l.startswith("U+")]; rep["cjkvi_ids"] = dict(entries=len(ids))
json.dump(rep, open(os.path.join(OUT, "zh_census.json"), "w"), indent=1, ensure_ascii=False); print(json.dumps(rep, indent=1, ensure_ascii=False)[:5200])
