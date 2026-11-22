#!/usr/bin/env python3
"""exp_v2_list.py — the word list for the zh/en experiment (experiment_v2/list.tsv; documented in 1024.md).

Rows 1..1024 are calibration_v1_en_zh.tsv (English chosen words, frozen file, read only).  For each, the Chinese analog is DIRECT when CC-CEDICT lists the
English word as a whole gloss of that Chinese word (the row's existing zh_trad if it qualifies, else the candidate most frequent in zh_v1.txt); otherwise the row
keeps the existing zh_trad and is marked NO-DIRECT (an interpretation).  Then FAULT rows, added on purpose: words with no counterpart in the other language,
English plurals / inflections that Chinese does not mark, and strings the tokenizer or filter is expected to drop.
"""
import csv, re, zipfile, collections, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dprint import dprint
rows = list(csv.DictReader(open(os.path.join(ROOT, "calibration", "calibration_v1_en_zh.tsv"), encoding="utf-8"), delimiter="\t"))
z = zipfile.ZipFile(os.path.join(ROOT, "corpora", "zh", "structure", "cedict_1_0_ts_utf-8_mdbg.zip")); txt = z.read(z.namelist()[0]).decode("utf-8")
by_gloss = collections.defaultdict(set)         # english gloss -> traditional headwords
for l in txt.splitlines():
    if l.startswith("#"): continue
    m = re.match(r"(\S+) (\S+) \[[^\]]*\] /(.*)/", l)
    if not m: continue
    for g in m.group(3).split("/"):
        g = re.sub(r"\(.*?\)", "", g).strip().lower(); g = re.sub(r"^to ", "", g)
        if g: by_gloss[g].add(m.group(1))
zh_text = open(os.path.join(ROOT, "corpora", "text", "zh_v1.txt"), encoding="utf-8").read()
out = []; used = collections.Counter()
for r in rows:
    en = r["en_us"].lower(); cur = r["zh_trad"]; cands = by_gloss.get(en, set())
    dprint("en", en); dprint("cands", sorted(cands)[:8])
    if cur in cands: zh, st = cur, "DIRECT"
    elif cands:
        best = max(cands, key=lambda c: (zh_text.count(c), -len(c)))
        zh, st = best, "DIRECT"
    else: zh, st = cur, "NO-DIRECT"
    dprint("zh", zh); dprint("status", st)
    out.append(dict(n=len(out) + 1, kind="MATCHED", half=r["half"], pair=r["pair"], pos=r["pos"], en=en, zh=zh, status=st, old_zh=cur, synset=r["synset"]))
# Fault rows: kind FAULT:<what>.  zh '-' = no counterpart.
F = []
def f(kind, en, zh): F.append((kind, en, zh))
for en, zh in [("foot", "腳"), ("feet", "腳"), ("mouse", "老鼠"), ("mice", "老鼠"), ("child", "孩子"), ("children", "孩子"), ("tooth", "牙"), ("teeth", "牙"),
               ("man", "男人"), ("men", "男人"), ("woman", "女人"), ("women", "女人"), ("goose", "鵝"), ("geese", "鵝"), ("tree", "樹"), ("trees", "樹"),
               ("book", "書"), ("books", "書"), ("word", "詞"), ("words", "詞")]:
    f("FAULT:plural-one-zh-word", en, zh)
for en, zh in [("walk", "走"), ("walked", "走"), ("walking", "走"), ("eat", "吃"), ("ate", "吃"), ("eaten", "吃"), ("eating", "吃")]:
    f("FAULT:tense-one-zh-word", en, zh)
for en in ["the", "a", "an", "of", "is", "to", "i", "don't", "well-known", "mother-in-law"]:
    f("FAULT:english-only-or-tokenizer", en, "-")
for zh in ["個", "隻", "條", "張", "本", "了", "過", "著", "的", "嗎", "呢", "們", "把", "被"]:
    f("FAULT:chinese-only", "-", zh)
f("FAULT:chinese-only-multichar", "-", "我們"); f("FAULT:chinese-only-multichar", "-", "他們")
for kind, en, zh in F:
    out.append(dict(n=len(out) + 1, kind=kind, half="", pair="", pos="", en=en, zh=zh, status="FAULT", old_zh="", synset=""))
with open(os.path.join(ROOT, "experiment_v2", "list.tsv"), "w", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), delimiter="\t"); w.writeheader(); w.writerows(out)
c = collections.Counter(o["status"] for o in out); print(dict(c), "rows", len(out))
