#!/usr/bin/env python3
"""exp_v2_filter.py — filter the two v1 corpora to the experiment's word lists (experiment_v2/list.tsv).  One output line per sentence (the engine ends a sentence at a newline),
only list words kept, space separated.  English: tokens [a-z']+ in the English list.  Chinese: Han runs segmented by LONGEST MATCH over the Chinese list; Han characters that
begin no list word are dropped.  Writes experiment_v2/text_en.txt, text_zh.txt, corpus_counts.tsv."""
import csv, os, re, sys, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); sys.path.insert(0, os.path.dirname(__file__))
from dprint import dprint
L = list(csv.DictReader(open(os.path.join(ROOT, "experiment_v2", "list.tsv"), encoding="utf-8"), delimiter="\t"))
EN = {r["en"] for r in L if r["en"] != "-"}; ZH = {r["zh"] for r in L if r["zh"] != "-"}
dprint("EN words", len(EN)); dprint("ZH words", len(ZH))
SENT_END = re.compile(r"[.!?\n…‼⁇⁈⁉。！？．]")
MAXZ = max(len(w) for w in ZH)
han = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0003134f]+")
tok = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
cnt = collections.Counter()
def seg(run):
    out = []; i = 0
    while i < len(run):
        for n in range(min(MAXZ, len(run) - i), 0, -1):
            w = run[i:i + n]
            if w in ZH: out.append(w); i += n; break
        else: i += 1
    return out
for lang, src, dst in (("en", "en_v1.txt", "text_en.txt"), ("zh", "zh_v1.txt", "text_zh.txt")):
    nl = nt = 0
    with open(os.path.join(ROOT, "corpora", "text", src), encoding="utf-8") as f, open(os.path.join(ROOT, "experiment_v2", dst), "w", encoding="utf-8") as o:
        buf = f.read()
        for sent in SENT_END.split(buf):
            if lang == "en": ws = [t.lower().replace("’", "'") for t in tok.findall(sent)]; ws = [w for w in ws if w in EN]
            else: ws = [w for run in han.findall(sent) for w in seg(run)]
            if not ws: continue
            for w in ws: cnt[(lang, w)] += 1
            o.write(" ".join(ws) + "\n"); nl += 1; nt += len(ws)
    print(lang, "sentences kept", nl, "tokens kept", nt)
with open(os.path.join(ROOT, "experiment_v2", "corpus_counts.tsv"), "w", encoding="utf-8") as o:
    o.write("lang\tword\tcount\n")
    for lang, words in (("en", EN), ("zh", ZH)):
        for w in sorted(words): o.write(f"{lang}\t{w}\t{cnt.get((lang, w), 0)}\n")
print("en words never seen:", sum(1 for w in EN if cnt[("en", w)] == 0), "zh words never seen:", sum(1 for w in ZH if cnt[("zh", w)] == 0), "| distinct zh", len(ZH), "distinct en", len(EN))
