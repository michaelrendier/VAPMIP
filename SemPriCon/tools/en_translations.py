#!/usr/bin/env python3
"""en_translations.py — which English words have a single-word translation in every test-bed language, according to Wiktionary's translation tables.

Streams corpora/lexicon/kaikki-English.jsonl (3.3 GB).  For each single-word English entry it keeps the translations into
  Chinese (Mandarin or untagged written Chinese; Cantonese, Hokkien, Min, Dungan, Wu, Hakka ... tags are dropped), Swahili, Finnish, Indonesian, Quechua,
as long as the target is ONE word (no space).  The Quechua requirement is applied first: it is the scarce language.
Writes corpora/derived/en_translations.jsonl (one record per English entry that has a translation in every language) and a count summary."""
import collections, json, os, sys, time, unicodedata as ud
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); OUT = os.path.join(ROOT, "corpora", "derived")
os.makedirs(OUT, exist_ok=True)
CODES = {"zh": "zh", "cmn": "zh", "sw": "sw", "fi": "fi", "id": "id", "qu": "qu", "quz": "qu", "qvc": "qu", "qvi": "qu", "que": "qu"}
BAD_ZH = {"Cantonese", "Hokkien", "Min Nan", "Min", "Taiwanese Hokkien", "Teochew", "Hakka", "Wu", "Dungan", "Gan", "Xiang", "Jin", "Min Dong", "Puxian", "Shanghainese", "Old Chinese",
          "Middle Chinese", "Classical Chinese", "Literary Chinese", "Eastern Min", "Leizhou", "Hainanese", "Taishanese", "Hokkien Pe̍h-ōe-jī", "Pinghua", "Huizhou"}
NEED = ("zh", "sw", "fi", "id", "qu")
t0 = time.time(); n = kept = 0
cover = collections.Counter(); out = open(os.path.join(OUT, "en_translations.jsonl"), "w", encoding="utf-8")
for line in open(os.path.join(ROOT, "corpora", "lexicon", "kaikki-English.jsonl"), encoding="utf-8"):
    n += 1
    if n % 200000 == 0: print(n, "entries", kept, "kept", round(time.time() - t0), "s", flush=True)
    d = json.loads(line); w = d.get("word", "")
    if not w.isascii() or not w.replace("-", "").isalpha() or w != w.lower(): continue
    tr = collections.defaultdict(list)
    for t in d.get("translations") or []:
        L = CODES.get(t.get("lang_code") or t.get("code"))
        if not L: continue
        tw = ud.normalize("NFC", t.get("word", "")).strip(); tags = t.get("tags", [])
        if not tw or " " in tw: continue
        if L == "zh" and (set(tags) & BAD_ZH): continue
        tr[L].append(dict(w=tw, tags=tags, roman=t.get("roman", ""), sense=t.get("sense", "")))
    for L in NEED: cover[L] += bool(tr.get(L))
    if all(tr.get(L) for L in NEED):
        senses = [g for s in d.get("senses", []) for g in s.get("glosses", [])][:4]
        out.write(json.dumps(dict(word=w, pos=d.get("pos"), glosses=senses, tr=tr), ensure_ascii=False) + "\n"); kept += 1
print("entries", n, "| single-word English entries with a translation in each language:", dict(cover), "| in ALL five:", kept, "| seconds", round(time.time() - t0))
