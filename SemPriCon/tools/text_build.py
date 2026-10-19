#!/usr/bin/env python3
"""text_build.py — running-text corpora for the Unicode test bed, equal-sized per language.

Sources (corpora/MANIFEST.tsv): Wikipedia (parquet), Tatoeba (sentences + translation links), VarCon (US/UK spelling variants).
  corpora/text/<lang>.txt       NFC-normalised article text, one paragraph per line, truncated to the token budget (tokens counted by the
                                Unicode engine's own tokenizer, tools/monad_pyu.tok_split)
  corpora/text/en-GB.txt, en-US.txt   English Wikipedia articles labelled by spelling: an article is UK when it uses >= MIN_VARIANTS UK-only
                                spellings and no US-only spelling, US in the mirror case (VarCon, lists below), then truncated to the same budget
  corpora/text/aligned_<lang>-eng.tsv   Tatoeba sentence pairs (target sentence, English sentence) joined through the translation links
Budget: --budget N tokens per language (default: the number of tokens in the smallest source, Quechua Wikipedia).
"""
import argparse, bz2, collections, io, os, re, sys, tarfile, unicodedata as ud
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import monad_pyu as mu
import pyarrow.parquet as pq
C = os.path.join(ROOT, "corpora"); OUT = os.path.join(C, "text"); os.makedirs(OUT, exist_ok=True)
WIKI = {"quechua": "qu.parquet", "swahili": "sw.parquet", "finnish": "fi-00.parquet", "indonesian": "id-00.parquet", "mandarin": "zh-00.parquet", "english": "en-00.parquet"}
MIN_VARIANTS = 2


def paragraphs(path):
    """yield (title, paragraph) from a Wikipedia parquet, NFC-normalised, one paragraph per item"""
    pf = pq.ParquetFile(path)
    for g in range(pf.num_row_groups):
        t = pf.read_row_group(g, columns=["title", "text"]).to_pydict()
        for title, text in zip(t["title"], t["text"]):
            yield title, [ud.normalize("NFC", p).strip() for p in text.split("\n") if p.strip()]


def varcon():
    us, uk = set(), set()
    for line in open(os.path.join(C, "lexicon", "varcon.txt"), encoding="utf-8"):
        if line.startswith("#") or ":" not in line: continue
        for part in line.strip().split(" / "):
            tags, _, w = part.partition(":"); tags = tags.replace("v", "").split(); w = w.strip().lower()
            if " " in w or not w: continue
            if "A" in tags and "Z" not in tags and "B" not in tags: us.add(w)
            elif "B" in tags and "A" not in tags and "Z" not in tags: uk.add(w)
    return us - uk, uk - us


def take(paras_iter, budget, keep=None):
    n, out = 0, []
    for title, paras in paras_iter:
        if keep is not None and not keep(paras): continue
        for p in paras:
            k = len(mu.tok_split(p))
            if k == 0: continue
            out.append(p); n += k
            if n >= budget: return out, n
    return out, n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--budget", type=int, default=0); a = ap.parse_args()
    avail = {}
    if a.budget == 0:                                   # the budget is what the smallest source holds
        out, n = take(paragraphs(os.path.join(C, "wikipedia", WIKI["quechua"])), 10 ** 12); a.budget = n
        open(os.path.join(OUT, "quechua.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n"); avail["quechua"] = n
    print("budget (tokens per language):", a.budget)
    for lang, f in WIKI.items():
        if lang in avail or not os.path.exists(os.path.join(C, "wikipedia", f)): continue
        out, n = take(paragraphs(os.path.join(C, "wikipedia", f)), a.budget)
        open(os.path.join(OUT, f"{lang}.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n"); avail[lang] = n; print(lang, n)
    # UK / US labelled English
    us, uk = varcon(); print("VarCon US-only", len(us), "UK-only", len(uk))
    wre = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?", re.U)
    def label(paras):
        c = collections.Counter(("US" if w in us else "UK") for p in paras for w in wre.findall(p.lower()) if w in us or w in uk)
        return "UK" if c["UK"] >= MIN_VARIANTS and c["US"] == 0 else ("US" if c["US"] >= MIN_VARIANTS and c["UK"] == 0 else None)
    for tag in ("UK", "US"):
        out, n = take(paragraphs(os.path.join(C, "wikipedia", WIKI["english"])), a.budget, keep=lambda ps, tag=tag: label(ps) == tag)
        open(os.path.join(OUT, f"en-{'GB' if tag == 'UK' else 'US'}.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n"); avail["en-" + tag] = n; print("en", tag, n)
    # Tatoeba aligned pairs
    want = {"swh": "swahili", "que": "quechua", "fin": "finnish", "ind": "indonesian", "cmn": "mandarin"}
    sent = {}
    for code in list(want) + ["eng"]:
        d = {}
        for line in bz2.open(os.path.join(C, "tatoeba", f"{code}_sentences.tsv.bz2"), "rt", encoding="utf-8"):
            i, _, t = line.rstrip("\n").split("\t", 2); d[i] = ud.normalize("NFC", t)
        sent[code] = d; print("tatoeba", code, len(d))
    pairs = collections.defaultdict(list); tf = tarfile.open(os.path.join(C, "tatoeba", "links.tar.bz2"), "r:bz2")
    code_of = {i: c for c in want for i in sent[c]}
    for m in tf:
        if not m.isfile(): continue
        for line in io.TextIOWrapper(tf.extractfile(m), encoding="utf-8"):
            x, _, y = line.rstrip("\n").partition("\t")
            if x in code_of and y in sent["eng"]: pairs[code_of[x]].append((sent[code_of[x]][x], sent["eng"][y]))
    for c, ps in pairs.items():
        with open(os.path.join(OUT, f"aligned_{want[c]}-eng.tsv"), "w", encoding="utf-8") as f:
            for t, e in ps: f.write(f"{t}\t{e}\n")
        print("aligned", want[c], len(ps))
    open(os.path.join(OUT, "text_report.tsv"), "w").write("\n".join(f"{k}\t{v}" for k, v in avail.items()) + "\n")


if __name__ == "__main__":
    main()
