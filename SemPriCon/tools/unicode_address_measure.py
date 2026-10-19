#!/usr/bin/env python3
"""unicode_address_measure.py — address resolution of the 2026-05 build against the Unicode build, on real headwords of each language.

For every language with a completed Wiktionary extract: the single-token headwords the Unicode tokenizer keeps; how many distinct slots they reach
(new), how many a uniform hash into N slots would reach (expected = N(1 - exp(-n/N))), and, for the ASCII-only subset the old build could read,
how many distinct slots and how many at slot 0 (old).  Writes corpora/derived/address_measure.md."""
import collections, json, math, os, sys, unicodedata as ud
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); sys.path.insert(0, HERE)
import monad_py as old, monad_pyu as new
N = 25000
rows = []
man = open(os.path.join(ROOT, "corpora", "MANIFEST.tsv")).read()
for L in ["English", "Chinese", "Swahili", "Finnish", "Indonesian", "Quechua"]:
    if f"lexicon/kaikki-{L}.jsonl\t" not in man: continue
    heads = set()
    for line in open(os.path.join(ROOT, "corpora", "lexicon", f"kaikki-{L}.jsonl"), encoding="utf-8"):
        w = ud.normalize("NFC", json.loads(line)["word"]).casefold()
        t = new.tok_split(w)
        if t == [w] and new.token_accept(w): heads.add(w)
    n = len(heads); ns = {new.word_coords(w)[0] for w in heads}
    asc = [w for w in heads if w.isascii() and old.token_accept(w)]; os_ = {old.word_coords(w)[0] for w in asc}
    long_ = [w for w in heads if len(w) >= 8]; long_asc = [w for w in long_ if w.isascii() and old.token_accept(w)]
    rows.append((L, n, len(ns), round(N * (1 - math.exp(-n / N))), len(asc), len(os_), sum(1 for w in asc if old.word_coords(w)[0] == 0),
                 len(long_), len({new.word_coords(w)[0] for w in long_}), len(long_asc), len({old.word_coords(w)[0] for w in long_asc})))
hdr = ["language", "single-token headwords", "distinct slots (Unicode build)", "expected if uniform", "ASCII subset", "distinct slots (2026-05 build)", "of them at slot 0",
       "words ≥ 8 letters", "their distinct slots (new)", "≥ 8 letters, ASCII", "their distinct slots (old)"]
md = "| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr) + "\n" + "\n".join("| " + " | ".join(f"{c:,}" if isinstance(c, int) else str(c) for c in r) + " |" for r in rows) + "\n"
open(os.path.join(ROOT, "corpora", "derived", "address_measure.md"), "w").write(md); print(md)
