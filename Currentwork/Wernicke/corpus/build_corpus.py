#!/usr/bin/env python3
"""build_corpus.py — the STANDARD TESTING CORPUS of the semantic orbweaver (Wernicke tree).

What it does (deterministic; re-run it and the outputs do not change):
  1. reads the mirrored texts in texts/ (never modifies them), decoding each with a fallback chain,
  2. writes MANIFEST.json (sha256, size, title, author, year, genre, why chosen, where the original was found),
  3. samples prompts_corpus.jsonl: 135 sentences (15 per prose work, round-robin by type) from the
     body text, bucketed question / imperative / copular / statement by SIMPLE HEURISTICS (punctuation and
     first words; the type label is a convenience, not an annotation),
  4. leaves prompts_chat.jsonl and answers_seed.jsonl alone (hand-written; see README.md).

Rules of use: the texts and the prompt files are never edited to fit a result; a new corpus version gets a
new directory.  Seed 20261017.  No NLTK needed (the tagger data are not on this machine yet).
"""
import hashlib
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTS = os.path.join(HERE, "texts")
SEED = 20261017
PER_WORK_PER_TYPE = {"question": 4, "imperative": 3, "copular": 4, "statement": 4}   # 15 per work

WORKS = [
    # file, short id, title, author, year, genre, why, found at, prompt sampling?
    ("chesterton_innocence_of_father_brown_1911.txt", "fb1", "The Innocence of Father Brown", "G. K. Chesterton", 1911,
     "dialogue-heavy detective fiction", "short stories: dense dialogue, questions, commands, deduction in plain statements",
     "~/Documents/eBooks/General.zip (Project Gutenberg etext)", True),
    ("chesterton_incredulity_of_father_brown_1926.txt", "fb2", "The Incredulity of Father Brown", "G. K. Chesterton", 1926,
     "dialogue-heavy detective fiction", "second collection: longer argued dialogue, more abstract speech acts",
     "~/Documents/eBooks/General.zip (Project Gutenberg of Australia)", True),
    ("abbott_flatland_1884.txt", "fl", "Flatland: A Romance of Many Dimensions", "Edwin A. Abbott", 1884,
     "expository narrative, geometry", "first-person explanation of dimension and shape: copular definitions, the project's own vocabulary",
     "~/Documents/eBooks/General.zip (Project Gutenberg etext)", True),
    ("cooper_last_of_the_mohicans_1826.txt", "lm", "The Last of the Mohicans", "James Fenimore Cooper", 1826,
     "adventure narrative", "long periodic narrative sentences, archaic dialogue, many adverbial frames",
     "~/.ptolemy/.ptoltemp/940-0.txt (Project Gutenberg 940)", True),
    ("pepys_diary_complete_pg4200.txt", "py", "Diary of Samuel Pepys, Complete", "Samuel Pepys", 1660,
     "plain first-person prose", "short declaratives with dates, places, names and numbers: the aggregate (HOOK) role",
     "~/.ptolemy/.ptoltemp/4200-0.txt (Project Gutenberg 4200)", True),
    ("kant_critique_of_pure_reason_1781_meiklejohn_pg4280.txt", "ka", "The Critique of Pure Reason (Meiklejohn translation)", "Immanuel Kant", 1781,
     "dense abstract exposition", "stress test: nominalised, subordinated argument with almost no events",
     "~/.ptolemy/.ptoltemp/4280-0.txt (Project Gutenberg 4280)", True),
    ("demorgan_budget_of_paradoxes_vol1_pg23100.txt", "dm", "A Budget of Paradoxes, Volume I", "Augustus De Morgan", 1872,
     "mathematical and critical exposition", "witty argued prose about mathematics: contrast, concession, quotation",
     "~/.ptolemy/.ptoltemp/23100-8.txt (Project Gutenberg 23100)", True),
    ("roscher_principles_of_political_economy_pg27698.txt", "ro", "Principles of Political Economy (translation)", "William Roscher", 1878,
     "technical expository prose", "definitions, classifications and enumerations: the elaborate and wrap roles",
     "~/.ptolemy/.ptoltemp/27698-0.txt (Project Gutenberg 27698)", True),
    ("pliny_natural_history_vol3_pg59131.txt", "pl", "The Natural History of Pliny, Volume 3 (translation)", "Pliny the Elder", 77,
     "descriptive natural history", "catalogues of things with attributes: the specifics (HOOK) and modifiers (ELABORATE) roles",
     "~/.ptolemy/.ptoltemp/59131-0.txt (Project Gutenberg 59131)", True),
    ("milton_paradise_lost_pg20.txt", "mi", "Paradise Lost", "John Milton", 1667,
     "archaic blank verse", "stress test only (verse inverts normal order); not sampled for prompts",
     "~/Documents/paradiselost.txt (Project Gutenberg 20)", False),
    ("dante_inferno_longfellow_pg1001.txt", "da", "Divine Comedy, Hell (Longfellow's translation)", "Dante Alighieri", 1320,
     "verse translation", "stress test only (verse); not sampled for prompts",
     "~/Projects/ThePlace/FourthAgePapers/HyperindexingSystem/corpus/pg1001.txt (Project Gutenberg 1001)", False),
]

ABBREV = re.compile(r"\b(Mr|Mrs|Ms|Dr|St|Capt|Col|Gen|Prof|Sir|Hon|Rev|Messrs|No|vs|viz|etc|i\.e|e\.g)\.$")
IMPERATIVE_START = {"come", "look", "tell", "take", "give", "go", "let", "listen", "remember", "think", "stop", "leave",
                    "bring", "help", "forgive", "answer", "speak", "wait", "see", "stand", "hold", "keep", "read", "sit",
                    "stay", "ask", "say", "put", "hear", "trust", "do", "don't", "be", "pray", "behold", "mark", "observe"}
COPULA = re.compile(r"^(the|a|an|my|his|her|its|this|that|these|those|it|he|she|they|we|i|you|there)\b[^,;:]{0,40}?\b"
                    r"(is|are|was|were|am)\s+(?!not\b)\w+", re.I)
JUNK = re.compile(r"gutenberg|etext|e-text|copyright|license|http|www\.|\[|\]|_|\*|illustration|chapter [ivxlc]+", re.I)


def read(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "ignore"), "latin-1"


def body(text):
    """Strip the Project Gutenberg header and footer (markers when present, a line count when not)."""
    m = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG[^\n]*\n", text, re.I)
    if m:
        text = text[m.end():]
    else:
        lines = text.splitlines()
        text = "\n".join(lines[140:]) if len(lines) > 400 else text
    m = re.search(r"(\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG|End of (the )?Project Gutenberg)", text, re.I)
    return text[:m.start()] if m else text


def sentences(text):
    text = text.replace("\r", "")
    out = []
    for para in re.split(r"\n\s*\n", text):
        flat = " ".join(para.split())
        if len(flat) < 12:
            continue
        buf, start = [], 0
        for m in re.finditer(r"[.!?]+[\"”’')\]]*\s+(?=[\"“‘'(]?[A-Z])", flat):
            piece = flat[start:m.end()].strip()
            if ABBREV.search(flat[start:m.start() + 1]):
                continue
            buf.append(piece)
            start = m.end()
        buf.append(flat[start:].strip())
        out.extend(b for b in buf if b)
    return out


def unquote(s):
    s = s.strip()
    s = re.sub(r"^[\"“‘'`]+", "", s)
    s = re.sub(r"[\"”’']+$", "", s)
    return s.strip()


def kind(s):
    w = s.split()
    if s.endswith("?"):
        return "question"
    if len(w) <= 14 and w and w[0].lower().strip(",") in IMPERATIVE_START and s[-1] in ".!":
        return "imperative"
    if len(w) <= 10 and COPULA.match(s) and s[-1] in ".!":
        return "copular"
    if 5 <= len(w) <= 22 and s[-1] in ".!":
        return "statement"
    return None


def candidates(text):
    out = []
    for s in sentences(text):
        s = unquote(s)
        w = s.split()
        if not (3 <= len(w) <= 32) or JUNK.search(s) or not s[:1].isupper():
            continue
        if sum(c.isalpha() or c.isspace() or c in ",.;:!?'’-—“”\"" for c in s) / len(s) < 0.97:
            continue
        if s.isupper():
            continue
        if s.count('"') % 2 or s.count("“") != s.count("”"):      # a split inside a quotation: skip
            continue
        k = kind(s)
        if k:
            out.append((k, s))
    return out


def main():
    rng = random.Random(SEED)
    manifest, prompts = [], []
    for fn, wid, title, author, year, genre, why, found, sample in WORKS:
        path = os.path.join(TEXTS, fn)
        text, enc = read(path)
        raw = open(path, "rb").read()
        manifest.append({"file": "texts/" + fn, "id": wid, "title": title, "author": author, "year": year, "genre": genre,
                         "why": why, "found": found, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "decoded_as": enc, "prompt_sampling": sample,
                         "licence": "public domain (author died before 1930 or work published before 1929; translations pre-1900)"})
        if not sample:
            continue
        pool = candidates(body(text))
        for k, n in PER_WORK_PER_TYPE.items():
            ks = [s for kk, s in pool if kk == k]
            rng.shuffle(ks)
            for i, s in enumerate(ks[:n]):
                prompts.append({"id": f"{wid}-{k[:3]}{i + 1}", "work": wid, "type": k, "text": s})
    with open(os.path.join(HERE, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "prompts_corpus.jsonl"), "w") as f:
        for p in prompts:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "MANIFEST.md"), "w") as f:
        f.write("# Standard testing corpus: the documents chosen\n\nGenerated by build_corpus.py from MANIFEST.json; do not edit by hand.\n\n")
        f.write("| # | id | work | author | year | genre | bytes | sha256 (first 12) | used for prompts |\n|---|---|---|---|---|---|---|---|---|\n")
        for i, m in enumerate(manifest, 1):
            f.write(f"| {i} | {m['id']} | {m['title']} | {m['author']} | {m['year']} | {m['genre']} | {m['bytes']:,} | {m['sha256'][:12]} | {'yes' if m['prompt_sampling'] else 'no (verse, stress test)'} |\n")
        f.write("\n## Why each was chosen, and where the original was found\n\n")
        for m in manifest:
            f.write(f"* **{m['title']}** ({m['author']}, {m['year']}): {m['why']}. Found at {m['found']}.\n")
        f.write(f"\nTotal {sum(m['bytes'] for m in manifest):,} bytes in {len(manifest)} works. {len(prompts)} sampled prompts.\n")
    print(len(manifest), "works,", len(prompts), "prompts")


if __name__ == "__main__":
    main()
