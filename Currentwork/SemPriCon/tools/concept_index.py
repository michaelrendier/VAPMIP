#!/usr/bin/env python3
"""concept_index.py — reverse gloss index per language: English gloss word -> the headwords of that language whose Wiktionary sense is glossed by exactly that word.

For each language's kaikki file: every non-form entry, every sense, its glosses split on ';' and ','; a gloss that is ONE lower-case English word (optionally after 'to ') becomes
a key.  Rank = position of the gloss within the entry's first sense (0 = the primary gloss).  Chinese keeps Mandarin and untagged senses only (Cantonese, Hokkien, Min, Wu,
Hakka, Dungan, Classical and other tagged senses are dropped).  Output: corpora/derived/concept_index_<lang>.json  {english_word: [[headword, pos, rank, n_senses], ...]}."""
import collections, json, os, re, sys, time, unicodedata as ud
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); OUT = os.path.join(ROOT, "corpora", "derived")
BAD = {"Cantonese", "Hokkien", "Min Nan", "Min", "Taiwanese Hokkien", "Teochew", "Hakka", "Wu", "Dungan", "Gan", "Xiang", "Jin", "Eastern Min", "Hainanese", "Classical Chinese",
       "Literary Chinese", "Old Chinese", "Middle Chinese", "Shanghainese", "Taishanese", "Min Dong", "Puxian", "Pinghua", "obsolete", "archaic", "dialectal", "Taiwan Hokkien"}
POS = {"noun": "n", "verb": "v", "adj": "a", "adv": "r", "num": "n", "pron": "n", "name": None, "intj": None, "particle": None, "suffix": None, "prefix": None, "affix": None}
W = re.compile(r"^(?:to |the |a |an )?([a-z]+)$")


def build(lang):
    idx = collections.defaultdict(dict); n = 0; t0 = time.time()
    for line in open(os.path.join(ROOT, "corpora", "lexicon", f"kaikki-{lang}.jsonl"), encoding="utf-8"):
        n += 1
        d = json.loads(line); w = d.get("word", "")
        if not w or " " in w: continue
        pos = POS.get(d.get("pos"));
        if pos is None: continue
        senses = d.get("senses", [])
        if not senses or all(("form_of" in s or "alt_of" in s) for s in senses): continue
        ok = [s for s in senses if not (set(s.get("tags", [])) & BAD)]
        if lang == "Chinese" and not ok: continue
        for si, s in enumerate(ok[:6]):
            gl = []
            for g in s.get("glosses", [])[:2]:
                gl += [x.strip().lower() for x in re.split(r"[;,]", re.sub(r"\([^)]*\)", "", g))]
            for r, g in enumerate(gl[:6]):
                m = W.match(g)
                if m: 
                    key = (m.group(1), pos); prev = idx[key].get(ud.normalize("NFC", w))
                    rank = si * 10 + r
                    if prev is None or rank < prev[0]: idx[key][ud.normalize("NFC", w)] = (rank, len(ok))
    out = {f"{k[0]}|{k[1]}": [[hw, v[0], v[1]] for hw, v in d.items()] for k, d in idx.items()}
    json.dump(out, open(os.path.join(OUT, f"concept_index_{lang}.json"), "w"), ensure_ascii=False)
    print(lang, n, "entries,", len(out), "english gloss keys", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    for L in (sys.argv[1:] or ["Quechua", "Swahili", "Indonesian", "Chinese", "Finnish", "English"]): build(L)
