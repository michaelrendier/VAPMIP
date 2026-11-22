#!/usr/bin/env python3
"""omw_candidates.py — calibration candidates aligned at the SYNSET level.

A candidate is an English (word, POS) that is a gloss in BOTH the Swahili and the Quechua Wiktionary extracts (the two languages without a WordNet) and whose first WordNet synset
has lemmas in the Open Multilingual WordNet for Mandarin (cmn, Simplified in OMW; converted to Traditional with OpenCC s2twp), Finnish (fin) and Indonesian (ind).
Writes corpora/derived/omw_candidates.json  {"word|pos": {"synset", "cmn_simp", "cmn_trad", "fin", "ind"}}."""
import json, os, subprocess, sys
from nltk.corpus import wordnet as wn
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); D = os.path.join(ROOT, "corpora", "derived")
ix = {l: json.load(open(os.path.join(D, f"concept_index_{l}.json"))) for l in ("Swahili", "Quechua")}
out = {}
for k in sorted(set(ix["Swahili"]) & set(ix["Quechua"])):
    w, p = k.split("|"); ss = wn.synsets(w, p)
    for s in ss:
        L = {l: [x for x in s.lemma_names(l) if "_" not in x and " " not in x] for l in ("cmn", "fin", "ind")}
        if all(L.values()): out[k] = dict(synset=s.name(), cmn_simp=L["cmn"], fin=L["fin"], ind=L["ind"]); break
flat = sorted({x for v in out.values() for x in v["cmn_simp"]})
trad = subprocess.run([os.path.join(HERE, "opencc_local.sh"), "s2twp"], input="\n".join(flat), capture_output=True, text=True).stdout.split("\n")[:len(flat)]
t = dict(zip(flat, trad))
for v in out.values(): v["cmn_trad"] = [t[x] for x in v["cmn_simp"]]
json.dump(out, open(os.path.join(D, "omw_candidates.json"), "w"), ensure_ascii=False); print(len(out), "candidates")
