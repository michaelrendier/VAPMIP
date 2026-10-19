#!/usr/bin/env python3
"""ingest_corpora.py — the two single-language running-text corpora for test_chinese / test_english v1.0.

  corpora/text/zh_v1.txt   Traditional written Chinese: the 1,000 zh-tw Level-3 Vital Article pages (corpora/zh/vital/paragraphs.tsv).
                           Only Han characters and the sentence/clause marks 。！？，、；： are kept; Latin letters, digits and every other script are removed,
                           because the Chinese store carries no alphabet but its own.
  corpora/text/fi_v1.txt   Finnish Wikipedia (fi-00.parquet): letters of the Finnish alphabet (a-z, å ä ö š ž, apostrophe) kept; other accents folded; same 2 % rule.
  corpora/text/id_v1.txt   Indonesian Wikipedia (id-00.parquet): treated like English (ASCII only, accents folded).
  corpora/text/en_v1.txt   English Wikipedia (corpora/wikipedia/en-00.parquet), paragraphs in file order. Accents are folded (NFKD, combining marks dropped);
                           a paragraph with more than 2 % non-ASCII characters left after folding is skipped; the rest is ASCII only.
Equal budget: the English file stops when it holds as many tokens as the Chinese one (tokens counted the way each engine build counts them:
Han character = 1 token; English = maximal [A-Za-z'] run of >= 2 characters not starting with an apostrophe).
Deterministic: no sampling, no shuffle; the output hash is recorded in corpora/text/TEXT_V1.sha256.
"""
import hashlib, os, re, unicodedata as ud
import pyarrow.parquet as pq
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
C = os.path.join(ROOT, "corpora"); OUT = os.path.join(C, "text"); os.makedirs(OUT, exist_ok=True)

HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0002fa1f]")
KEEP_ZH = re.compile(r"[㐀-䶿一-鿿豈-﫿\U00020000-\U0002fa1f。！？，、；：]")
WORD_EN = re.compile(r"[A-Za-z']+")

def zh_clean(t):
    return "".join(KEEP_ZH.findall(t))

def en_clean(p):
    f = "".join(c for c in ud.normalize("NFKD", p) if not ud.combining(c))
    f = f.replace("’", "'").replace("‘", "'")
    bad = sum(1 for c in f if ord(c) > 126)
    if not f or bad * 50 > len(f):
        return ""
    return "".join(c if ord(c) < 127 else " " for c in f).strip()

FI_KEEP = set("abcdefghijklmnopqrstuvwxyzåäöšž'")
WORD_FI = re.compile(r"[a-zåäöšž']+")

def fi_clean(p):
    out = []; bad = 0
    p = ud.normalize("NFC", p).replace("\u2019", "'").replace("\u2018", "'")
    for c in p:
        if c.lower() in FI_KEEP or c == " " or not c.isalpha() and ord(c) < 127: out.append(c); continue
        f = "".join(x for x in ud.normalize("NFKD", c) if not ud.combining(x))
        if f and all(ord(x) < 127 for x in f): out.append(f)
        elif c.isalpha(): bad += 1; out.append(" ")
        else: out.append(" ")
    r = "".join(out).strip()
    return "" if not r or bad * 50 > len(r) else r

def fi_tokens(s):
    return sum(1 for w in WORD_FI.findall(s.lower()) if len(w) >= 2 and w[0] != "'")

def en_tokens(s):
    return sum(1 for w in WORD_EN.findall(s) if len(w) >= 2 and w[0] != "'")

def main():
    n_zh = 0
    with open(os.path.join(OUT, "zh_v1.txt"), "w", encoding="utf-8") as fo:
        for line in open(os.path.join(C, "zh", "vital", "paragraphs.tsv"), encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4: continue
            t = zh_clean(ud.normalize("NFC", parts[3]))
            k = len(HAN.findall(t))
            if k < 10: continue
            fo.write(t + "\n"); n_zh += k
    print("zh_v1.txt: Han tokens", n_zh)
    def latin(name, parquet, clean, count, enc):
        n = 0
        pf = pq.ParquetFile(os.path.join(C, "wikipedia", parquet))
        with open(os.path.join(OUT, name), "w", encoding=enc) as fo:
            done = False
            for g in range(pf.num_row_groups):
                for text in pf.read_row_group(g, columns=["text"]).to_pydict()["text"]:
                    for p in text.split("\n"):
                        p = clean(p)
                        if len(p) < 60: continue
                        k = count(p)
                        if n + k > n_zh: done = True; break
                        fo.write(p + "\n"); n += k
                    if done: break
                if done: break
        print(name + ": tokens", n)
    latin("en_v1.txt", "en-00.parquet", en_clean, en_tokens, "ascii")
    latin("id_v1.txt", "id-00.parquet", en_clean, en_tokens, "ascii")
    latin("fi_v1.txt", "fi-00.parquet", fi_clean, fi_tokens, "utf-8")
    with open(os.path.join(OUT, "TEXT_V1.sha256"), "w") as f:
        for n in ("zh_v1.txt", "en_v1.txt", "id_v1.txt", "fi_v1.txt"):
            f.write(hashlib.sha256(open(os.path.join(OUT, n), "rb").read()).hexdigest() + "  " + n + "\n")

if __name__ == "__main__":
    main()
