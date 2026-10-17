#!/usr/bin/env python3
"""nlp_data_manifest.py — regenerate ~/nlp_data/MANIFEST.md (URL, size, sha256, licence note for every downloaded file).
Only files that exist are listed (a missing one is reported, not invented).  Run after any download:
    python3 tools/nlp_data_manifest.py [--mirror]      # --mirror also copies it to docs/references/VAPMIPNLPData/
"""
import datetime
import hashlib
import os
import shutil
import sys

H = os.path.expanduser("~/nlp_data")
P = "https://wordnetcode.princeton.edu/"
GH = "https://github.com/"
ITEMS = [
    # (relative path, source URL, what, licence note)
    ("princeton/wn3.1.dict.tar.gz", P + "wn3.1.dict.tar.gz", "WordNet 3.1 database files (Princeton)", "Princeton WordNet licence"),
    ("princeton/WordNet-3.0.tar.bz2", P + "3.0/WordNet-3.0.tar.bz2", "WordNet 3.0 source and database (Princeton)", "Princeton WordNet licence"),
    ("princeton/WNprolog-3.0.tar.bz2", P + "3.0/WNprolog-3.0.tar.bz2", "WordNet 3.0 Prolog database", "Princeton WordNet licence"),
    ("princeton/WNsnsmap-3.0.tar.bz2", P + "3.0/WNsnsmap-3.0.tar.bz2", "WordNet 3.0 sense mappings", "Princeton WordNet licence"),
    ("princeton/wn_for_sql.tar.gz", P + "wn_for_sql.tar.gz", "WordNet in SQL form", "Princeton WordNet licence"),
    ("princeton/WordNet-3.0-glosstag.tar.bz2", P + "glosstag-files/WordNet-3.0-glosstag.tar.bz2", "Princeton Annotated Gloss Corpus (gloss-tagged WordNet 3.0)", "Princeton WordNet licence"),
    ("princeton/core-wordnet.txt", P + "standoff-files/core-wordnet.txt", "Core WordNet list", "Princeton WordNet licence"),
    ("princeton/morphosemantic-links.xls", P + "standoff-files/morphosemantic-links.xls", "Morphosemantic links", "Princeton WordNet licence"),
    ("princeton/morphosemantic-links.zip", P + "morpholinks/morphosemantic-links.zip", "Morphosemantic links (zip)", "Princeton WordNet licence"),
    ("princeton/LFglosses.standoff-files.zip", P + "morpholinks/LFglosses.standoff-files.zip", "Logical-form glosses standoff files", "Princeton WordNet licence"),
    ("princeton/SUMO-WordNet.zip", P + "sumo/SUMO-WordNet.zip", "SUMO to WordNet mappings (hosted by Princeton)", "check the SUMO licence before redistributing"),
    ("princeton/semcor16.tar.gz", P + "semcor16.tar.gz", "SemCor 1.6 (sense-tagged Brown corpus)", "Princeton WordNet licence"),
    ("verbnet/verbnet-cu-clear.zip", GH + "cu-clear/verbnet/archive/refs/heads/master.zip", "VerbNet (incl. 3.4)", "check the VerbNet licence"),
    ("verbnet/semlink-cu-clear.zip", GH + "cu-clear/semlink/archive/refs/heads/master.zip", "SemLink", "check the SemLink licence"),
    ("verbnet/propbank-frames.zip", GH + "propbank/propbank-frames/archive/refs/heads/main.zip", "PropBank frames", "check the PropBank licence"),
    ("spacy_models/en_core_web_sm-3.8.0-py3-none-any.whl", GH + "explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", "spaCy en_core_web_sm 3.8.0", "MIT (see the model card for training data)"),
    ("spacy_models/en_core_web_md-3.8.0-py3-none-any.whl", GH + "explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl", "spaCy en_core_web_md 3.8.0", "as above"),
    ("spacy_models/en_core_web_lg-3.8.0-py3-none-any.whl", GH + "explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl", "spaCy en_core_web_lg 3.8.0", "as above"),
    ("conceptnet/conceptnet-assertions-5.7.0.csv.gz", "https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz", "ConceptNet 5.7 assertions (Speer, Chin & Havasi 2017)", "CC BY-SA 4.0 (ConceptNet); read the attribution terms"),
    ("numberbatch/numberbatch-en-19.08.txt.gz", "https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-en-19.08.txt.gz", "ConceptNet Numberbatch 19.08, English", "CC BY-SA 4.0"),
    ("numberbatch/numberbatch-19.08.txt.gz", "https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-19.08.txt.gz", "ConceptNet Numberbatch 19.08, multilingual", "CC BY-SA 4.0"),
    ("wiktionary/enwiktionary-latest-pages-articles.xml.bz2", "https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles.xml.bz2", "English Wiktionary dump (raw wikitext)", "CC BY-SA 4.0 and GFDL (Wikimedia)"),
    ("wiktionary/kaikki.org-dictionary-English.jsonl", "https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl", "English Wiktionary, structured (Wiktextract by Tatu Ylonen)", "same licences as Wiktionary; cite Wiktextract"),
    ("github/xwn-davidar.zip", GH + "davidar/xwn/archive/refs/heads/master.zip", "eXtended WordNet 2.0-1.1 (UT Dallas; WordNet 2.0 senses; parsed, sense-tagged glosses)", "UT Dallas licence in the file: use, copy, modify, distribute for any purpose, notice kept on all copies"),
    ("github/ud-english-ewt.zip", GH + "UniversalDependencies/UD_English-EWT/archive/refs/heads/master.zip", "Universal Dependencies English-EWT", "CC BY-SA 4.0"),
    ("github/ud-english-gum.zip", GH + "UniversalDependencies/UD_English-GUM/archive/refs/heads/master.zip", "Universal Dependencies English-GUM", "per-genre CC licences (some NC); see the repo"),
    ("github/gum-georgetown.zip", GH + "amir-zeldes/gum/archive/refs/heads/master.zip", "GUM multilayer corpus (dep, const, coref, RST, entities); some texts need get_text.py to restore", "mixed CC BY / BY-SA / BY-NC-SA by genre; do not redistribute"),
    ("github/litbank.zip", GH + "dbamman/litbank/archive/refs/heads/master.zip", "LitBank (100 works of fiction: entities, coreference, events)", "no licence file in the repo; texts are Project Gutenberg"),
    ("github/unimorph-eng.zip", GH + "unimorph/eng/archive/refs/heads/master.zip", "UniMorph English inflection paradigms", "CC BY-SA 3.0 (UniMorph)"),
    ("github/morpholex-en.zip", GH + "hugomailhot/MorphoLex-en/archive/refs/heads/master.zip", "MorphoLex-en (70k words, morphological variables)", "see the repo (NOASSERTION)"),
    ("github/disrpt-sharedtask2019.zip", GH + "disrpt/sharedtask2019/archive/refs/heads/master.zip", "DISRPT 2019 discourse segmentation and connectives shared task data", "per-corpus licences; PDTB parts are stubs (LDC)"),
    ("github/disrpt-sharedtask2021.zip", GH + "disrpt/sharedtask2021/archive/refs/heads/master.zip", "DISRPT 2021", "as above"),
    ("github/disrpt-sharedtask2023.zip", GH + "disrpt/sharedtask2023/archive/refs/heads/master.zip", "DISRPT 2023", "as above"),
]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    out = ["# ~/nlp_data: what was acquired, from where, and when", "",
           f"Regenerated {datetime.date.today()} by tools/nlp_data_manifest.py. Every request carried a Mozilla user agent; public works only. "
           "Archives are kept; extracted copies sit in sibling directories. Nothing here is in git.",
           "Also on this machine, outside this directory: the NLTK data collection `all` (122 packages, 3.5 GB) in `~/nltk_data`; the `wn` library's "
           "Open English WordNet 2025/2024 and the Open Multilingual WordNet in `~/.wn_data`; Stanza English models in `~/.cache/stanza/1.15.0/resources`.", "",
           "| file | source URL | what | licence note | bytes | sha256 (first 16) |", "|---|---|---|---|---|---|"]
    missing, total = [], 0
    for rel, url, what, lic in ITEMS:
        path = os.path.join(H, rel)
        if not os.path.exists(path):
            missing.append(rel)
            continue
        n = os.path.getsize(path)
        total += n
        out.append(f"| {rel} | {url} | {what} | {lic} | {n:,} | {sha(path)[:16]} |")
    out += ["", f"{len(ITEMS) - len(missing)} files, {total / 1e9:.2f} GB of archives."]
    if missing:
        out += ["", "Listed but not present (not downloaded, or still downloading): " + ", ".join(missing)]
    out += ["", "Licence notes are reminders, not legal findings: read each licence before vendoring any of this into a repository."]
    text = "\n".join(out) + "\n"
    open(os.path.join(H, "MANIFEST.md"), "w").write(text)
    if "--mirror" in sys.argv:
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for d in (os.path.join(here, "docs", "references", "VAPMIPNLPData"),
                  os.path.join(os.path.dirname(here), "ContextPlease", "claude", "references", "VAPMIPNLPData")):
            os.makedirs(d, exist_ok=True)
            for old in os.listdir(d):
                if old.startswith("MANIFEST_nlp_data"):
                    os.remove(os.path.join(d, old))
            shutil.copy(os.path.join(H, "MANIFEST.md"), os.path.join(d, f"MANIFEST_nlp_data_{datetime.date.today()}.md"))
    print(len(ITEMS) - len(missing), "listed,", len(missing), "missing:", missing)


if __name__ == "__main__":
    main()
