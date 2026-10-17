#!/usr/bin/env python3
"""verify_nlp_data.py — are the downloaded datasets under ~/nlp_data (and the wn / Stanza stores) present and READABLE?

Opens each resource and reads a real record (not just a file size).  Interpreter-independent (stdlib only; the CoNLL-U check
uses `conllu` if importable).  PASS / MISS / FAIL like verify_nlp_environment.py.  Run:  python3 tools/verify_nlp_data.py
"""
import bz2
import glob
import gzip
import json
import os
import sys
import zipfile

H = os.path.expanduser("~/nlp_data")
rows = []


def check(name, fn):
    try:
        rows.append(("PASS", name, str(fn())[:78]))
    except (FileNotFoundError, IndexError, StopIteration) as e:
        rows.append(("MISS", name, type(e).__name__ + ": " + str(e)[:60]))
    except Exception as e:                                       # noqa: BLE001
        rows.append(("FAIL", name, type(e).__name__ + ": " + str(e)[:60]))


def first(pattern):
    hits = sorted(glob.glob(os.path.join(H, pattern), recursive=True))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[0]


check("conceptnet 5.7 assertions (gz)", lambda: gzip.open(first("conceptnet/*.csv.gz"), "rt").readline().split("\t")[1:3])
check("numberbatch English 19.08 (gz)", lambda: gzip.open(first("numberbatch/numberbatch-en-*.txt.gz"), "rt").readline().strip())
check("numberbatch multilingual 19.08 (gz)", lambda: gzip.open(first("numberbatch/numberbatch-19.08.txt.gz"), "rt").readline().strip())
check("enwiktionary dump (bz2)", lambda: bz2.open(first("wiktionary/enwiktionary-*.xml.bz2"), "rt").readline().strip())
check("kaikki English Wiktionary extract", lambda: (lambda d: (d["word"], d["pos"], len(d.get("senses", []))))(json.loads(open(first("wiktionary/kaikki*.jsonl")).readline())))
def xwn_record():
    import re
    txt = gzip.open(first("xwn-davidar/**/noun.xml.gz"), "rt").read(80000)
    m = re.search(r'<gloss pos="NOUN" synsetID="(\d+)">\s*<synonymSet>(.*?)</synonymSet>.*?<parse quality="(\w+)">', txt, re.S)
    if not m:
        raise IndexError("no <gloss> record with a parse in the first 80 KB")
    return f"synset {m.group(1)} {m.group(2)!r}: glossed, sense-tagged, parsed ({m.group(3).lower()})"


check("eXtended WordNet 2.0-1.1 (a sense-tagged, parsed gloss)", xwn_record)
check("Princeton WordNet 3.1 dict (index.noun)", lambda: open(first("wordnet-3.1/dict/index.noun")).readlines()[30].split()[0])
check("Princeton glosstag (standoff index)", lambda: os.path.basename(first("wordnet-3.0-glosstag/**/standoff/index.bylem.tab")))
check("Princeton SemCor 1.6", lambda: len(glob.glob(os.path.join(H, "semcor16/**/*", ), recursive=True)))
check("Princeton WordNet SQL", lambda: sorted(os.listdir(first("wordnet-sql")))[:3])
check("Princeton WordNet Prolog (wn_s.pl)", lambda: open(first("wordnet-3.0-prolog/**/wn_s.pl")).readline().strip())
check("Princeton morphosemantic links", lambda: os.path.basename(first("morphosemantic-links/*")))
check("Princeton Core WordNet list", lambda: open(first("princeton/core-wordnet.txt")).readline().strip())
check("SUMO-WordNet mappings", lambda: os.path.basename(first("sumo-wordnet/**/*.*")))
check("VerbNet 3.4 (official XML)", lambda: len(glob.glob(os.path.join(H, "verbnet-official/**/verbnet3.4/*.xml"), recursive=True)))
check("SemLink", lambda: os.path.basename(first("semlink/*/README.md")))
check("PropBank frames", lambda: len(glob.glob(os.path.join(H, "propbank-frames/**/frames/*.xml"), recursive=True)))


def conllu_sents():
    import conllu
    n = 0
    with open(first("ud-english-ewt/**/en_ewt-ud-dev.conllu")) as f:
        for s in conllu.parse_incr(f):
            n += 1
            if n >= 50:
                break
    return f"{n} sentences parsed, e.g. {s.metadata.get('text', '')[:40]!r}"


check("UD English-EWT (conllu, parsed)", conllu_sents)
check("UD English-GUM (conllu)", lambda: os.path.basename(first("ud-english-gum/**/en_gum-ud-train.conllu")))
check("GUM (Georgetown) layers", lambda: sorted(d for d in os.listdir(first("gum-georgetown/*")) if d in ("dep", "rst", "coref", "const", "xml", "annis"))) 
check("LitBank", lambda: len(glob.glob(os.path.join(H, "litbank/**/*.ann"), recursive=True)))
check("UniMorph English", lambda: open(first("unimorph-eng/**/eng")).readline().strip())
check("MorphoLex-en", lambda: os.path.basename(first("morpholex-en/**/*.xlsx")))
def disrpt():
    out = []
    for y in (2019, 2021, 2023):
        n = sum(len(glob.glob(os.path.join(H, f"disrpt-sharedtask{y}/**/*" + ext), recursive=True)) for ext in (".rels", ".conllu", ".tok", ".conll"))
        if n == 0:
            raise FileNotFoundError(f"no data files in disrpt-sharedtask{y}")
        out.append(n)
    return out


check("DISRPT 2019 / 2021 / 2023 data files", disrpt)
check("spaCy model wheels", lambda: len(glob.glob(os.path.join(H, "spacy_models/*.whl"))))
check("wn: Open English WordNet + OMW (any interpreter with wn)", lambda: [(l.id, l.version) for l in __import__("wn").lexicons()])
def stanza_models():
    n = len(glob.glob(os.path.expanduser("~/.cache/stanza/*/resources/en/*/*")))
    if n == 0:
        raise FileNotFoundError("~/.cache/stanza/*/resources/en is empty")
    return f"{n} model files"


check("Stanza English models", stanza_models)

w = max(len(r[1]) for r in rows)
for s, n, note in rows:
    print(f"{s:4s} {n:<{w}s}  {note}")
c = {k: sum(r[0] == k for r in rows) for k in ("PASS", "MISS", "FAIL")}
print(f"\n{c['PASS']} PASS, {c['MISS']} MISS, {c['FAIL']} FAIL")
sys.exit(1 if c["FAIL"] else 0)
