#!/usr/bin/env python3
"""calibration_v2.py — extends the frozen calibration v1 (English US/UK + Traditional Chinese, 1 024 rows) with Finnish and Indonesian.

v1 is not touched. Every v1 row is carried over unchanged; two columns are added per language:  fi_word, fi_note, id_word, id_note.
Word choice: the Open Multilingual WordNet lemmas of the row's synset (nltk omw-1.4: fin, ind), single words only (no underscore). Among the lemmas that occur in the language's
corpus (corpora/text/{fi,id}_v1.txt), the S row takes the most frequent; the L row of the same pair takes the most frequent OTHER one if the synset has one, otherwise the
same word with note 'shared' (the pair has no second word). A word is used once in the whole column (a repeat is reassigned or noted 'repeat').
Notes: ok | shared | repeat | unattested (lemma not in the corpus; chosen anyway) | nolemma (no OMW lemma for the synset: blank).
Writes calibration/calibration_v2_en_zh_fi_id.tsv and prints coverage. The result is a CANDIDATE: it is frozen only when a speaker has reviewed it."""
import collections, csv, os, re
from nltk.corpus import wordnet as wn
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LANG = {"fi": ("fin", re.compile(r"[a-zåäöšž']+")), "id": ("ind", re.compile(r"[a-z']+"))}

def freq(code):
    rx = LANG[code][1]; c = collections.Counter()
    for line in open(os.path.join(ROOT, "corpora", "text", f"{code}_v1.txt"), encoding="utf-8"):
        c.update(rx.findall(line.lower()))
    return c

def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "calibration", "calibration_v1_en_zh.tsv"), encoding="utf-8"), delimiter="\t"))
    out_cols = {}
    for code, (omw, _) in LANG.items():
        f = freq(code); used = set(); words = {}; notes = {}
        for r in rows:                                   # rows are in pair order: S then L
            lem = [l.lower() for l in wn.synset(r["synset"]).lemma_names(omw) if "_" not in l]
            if not lem:
                words[r["id"]] = ""; notes[r["id"]] = "nolemma"; continue
            lem = sorted(set(lem), key=lambda w: -f[w])
            pick = next((w for w in lem if w not in used and f[w] > 0), None)
            note = "ok"
            if pick is None:
                pick = next((w for w in lem if w not in used), None)
                note = "unattested" if pick else "repeat"
                if pick is None: pick = lem[0]
            if pick in used and note == "ok": note = "repeat"
            used.add(pick); words[r["id"]] = pick; notes[r["id"]] = note
        out_cols[code] = (words, notes)
        print(code, collections.Counter(notes.values()))
    fn = list(rows[0].keys()) + ["fi_word", "fi_note", "id_word", "id_note"]
    with open(os.path.join(ROOT, "calibration", "calibration_v2_en_zh_fi_id.tsv"), "w", encoding="utf-8", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=fn, delimiter="\t"); w.writeheader()
        for r in rows:
            r = dict(r)
            for code in LANG:
                r[f"{code}_word"] = out_cols[code][0][r["id"]]; r[f"{code}_note"] = out_cols[code][1][r["id"]]
            w.writerow(r)

if __name__ == "__main__":
    main()
