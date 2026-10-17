#!/usr/bin/env python3
"""extract_v0.py — deterministic content extraction from a prompt: grab the literal words, assign them to the seven data points.

A straight ruleset (Cody, 2026-10-17: no training, deterministic behaviour).  Nothing statistical: a regex tokenizer, hardcoded
closed-class tables, WordNet 3.0 lookups through NLTK (`morphy` and the synset list, both rule and table driven), and an ordered list of
disambiguation rules.  The same input always gives the same output.  The orbweaver web is not involved: no spreading, no A-edges.

The seven data points (see silk_map.py):  SHELL ANCHOR SPAN{relation,claim,frame} SCAFFOLD ELABORATE HOOK WRAP.
Pronouns are NOT resolved (they belong to the final conjugation/tense/participle repass): each is kept with person, number, case.
Granularity (for now): per content word, how specific its vocabulary is (WordNet depth, sense count, hyponym count, unknown/technical).
Invisible zero-width characters are stripped and counted (they are a separate side channel, not part of the words).

    python3 extract_v0.py "can you play the piano?"     one prompt
    python3 extract_v0.py FILE.jsonl [OUT.jsonl]        a file of {"id","text"} lines
"""
import json
import re
import sys
import unicodedata

from nltk.corpus import wordnet as wn

# ── closed-class tables (the Zork-style hardcoded reference) ────────────────────────────────────────────────────────────
DET = set("a an the this that these those my your his her its our their some any each every no all both either neither another other such".split())
POSS = {"my": "1sg", "your": "2", "his": "3sg-m", "her": "3sg-f", "its": "3sg-n", "our": "1pl", "their": "3pl"}
PRON = {  # form: (person, number, case)
    "i": ("1", "sg", "nom"), "me": ("1", "sg", "acc"), "myself": ("1", "sg", "refl"), "mine": ("1", "sg", "poss"),
    "you": ("2", "sg/pl", "nom/acc"), "yourself": ("2", "sg", "refl"), "yours": ("2", "sg/pl", "poss"), "yourselves": ("2", "pl", "refl"),
    "he": ("3", "sg-m", "nom"), "him": ("3", "sg-m", "acc"), "himself": ("3", "sg-m", "refl"),
    "she": ("3", "sg-f", "nom"), "hers": ("3", "sg-f", "poss"), "herself": ("3", "sg-f", "refl"),
    "it": ("3", "sg-n", "nom/acc"), "itself": ("3", "sg-n", "refl"),
    "we": ("1", "pl", "nom"), "us": ("1", "pl", "acc"), "ours": ("1", "pl", "poss"), "ourselves": ("1", "pl", "refl"),
    "they": ("3", "pl", "nom"), "them": ("3", "pl", "acc"), "theirs": ("3", "pl", "poss"), "themselves": ("3", "pl", "refl"),
    "one": ("3", "sg", "gen"), "someone": ("3", "sg", "indef"), "somebody": ("3", "sg", "indef"), "something": ("3", "sg", "indef"),
    "anyone": ("3", "sg", "indef"), "anybody": ("3", "sg", "indef"), "anything": ("3", "sg", "indef"), "everyone": ("3", "sg", "indef"),
    "everybody": ("3", "sg", "indef"), "everything": ("3", "sg", "indef"), "nobody": ("3", "sg", "indef"), "nothing": ("3", "sg", "indef"),
    "none": ("3", "sg", "indef"), "there": ("3", "-", "expl"),
}
SUBJ_PRON = {"i", "you", "he", "she", "it", "we", "they", "there"}
PREP = set(("of in on at for with by from about into through over under between among against during before after above below up down out off near "
            "across behind beside beyond within without upon toward towards onto per via than like unlike around along throughout despite except "
            "inside outside past since until till as to amid").split())
COORD = {"and", "or", "but", "nor", "yet"}
SUBORD = set("if because although though while whereas unless whether once whenever wherever so that".split())
WH = {"what", "who", "whom", "whose", "which", "when", "where", "why", "how"}
NEG = {"not", "n't", "never", "nor", "cannot", "neither"}
INTJ = set("hello hi hey yes yeah ok okay please thanks thank oh wow hmm bye goodbye".split())
GREET_FORMULA = [("good", "morning"), ("good", "afternoon"), ("good", "evening"), ("good", "night"), ("how", "do", "you", "do"), ("thank", "you")]
MODAL = set("can could may might must shall should will would ought".split())
BE = {"am": ("1", "sg", "present"), "is": ("3", "sg", "present"), "are": ("2/3", "sg/pl", "present"), "was": ("1/3", "sg", "past"),
      "were": ("2/3", "sg/pl", "past"), "be": ("-", "-", "base"), "been": ("-", "-", "participle"), "being": ("-", "-", "gerund")}
HAVE = {"have": "present", "has": "present", "had": "past", "having": "gerund"}
DO = {"do": "present", "does": "present", "did": "past", "doing": "gerund", "done": "participle"}
ADV_CLOSED = set("very too just also only even still already always often again now then here there quite rather really almost maybe perhaps else "
                 "however therefore thus instead somewhere anywhere everywhere elsewhere today tomorrow yesterday tonight soon later once twice".split())
ADV_FRAME = set("now then here there today tomorrow yesterday tonight soon later somewhere anywhere everywhere elsewhere".split())  # scope adverbs (time and place)
NUMWORDS = set("zero one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty hundred thousand million first second third".split())
STOP_ADV_NOT_ELAB = {"not", "n't", "never"}
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)

TOKEN_RE = re.compile(r"""
    (?P<ell>\.{2,}|…)
  | (?P<list>\b\d{1,2}\)(?=\s))
  | (?P<frac>\d+/\d+)
  | (?P<tech>\.[A-Za-z_]\w*(?:[._]\w+)*|[A-Za-z]+(?:[._][A-Za-z0-9]+)+|[A-Z]{2,}[a-z]*\d*|[A-Za-z]+\d+[A-Za-z0-9]*)
  | (?P<num>\d+(?:\.\d+)?)
  | (?P<word>[A-Za-z]+(?:['’][A-Za-z]+)*)
  | (?P<punct>[^\sA-Za-z0-9])
""", re.X)
NOAPOS = {"im": ("i", "am"), "youre": ("you", "are"), "dont": ("do", "n't"), "cant": ("ca", "n't"), "wont": ("wo", "n't"), "isnt": ("is", "n't"),
          "arent": ("are", "n't"), "didnt": ("did", "n't"), "doesnt": ("does", "n't"), "wasnt": ("was", "n't"), "thats": ("that", "'s"),
          "whats": ("what", "'s"), "ive": ("i", "have"), "ill": ("i", "will"), "theyre": ("they", "are"), "weve": ("we", "have"), "hes": ("he", "'s"), "shes": ("she", "'s")}
CONTRACT = [("n't", "not"), ("'re", "are"), ("'ve", "have"), ("'ll", "will"), ("'m", "am"), ("'d", "would")]


def tokenize(text):
    """Regex tokens (kind, surface).  Contractions are split in two; a leading-dot filename like .bin is one token."""
    text = text.translate(ZERO_WIDTH)
    out = []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        s = m.group().replace("’", "'")
        if kind == "word":
            low = s.lower()
            done = False
            if low in NOAPOS and low != "ill" and low != "hes":
                out.append(("word", NOAPOS[low][0])); out.append(("word", NOAPOS[low][1])); continue
            for suf, _ in CONTRACT:
                if low.endswith(suf) and len(low) > len(suf):
                    stem = s[: -len(suf)]
                    if low == "won't":
                        out.append(("word", "wo")); out.append(("word", "n't")); done = True; break
                    if low == "can't":
                        out.append(("word", "ca")); out.append(("word", "n't")); done = True; break
                    out.append(("word", stem)); out.append(("word", s[-len(suf):])); done = True; break
            if not done and low.endswith("'s") and len(low) > 2:
                out.append(("word", s[:-2])); out.append(("word", "'s")); done = True
            if not done:
                out.append((kind, s))
        else:
            out.append((kind, s))
    return out


def is_tech(s):
    return bool(re.search(r"[_]|\.[A-Za-z]", s)) or (s.isupper() and len(s) >= 2) or bool(re.search(r"[A-Za-z]\d|\d[A-Za-z]", s)) or s.startswith(".")


_LEMMAS = None


def typo_of(word):
    """Deterministic typo candidates for a word WordNet does not know: lemmas at edit distance 1 (substitution, deletion, insertion,
    transposition) sharing the first letter, most frequent first."""
    global _LEMMAS
    if _LEMMAS is None:
        _LEMMAS = {}
        for l in wn.all_lemma_names():
            if l.isalpha():
                _LEMMAS.setdefault(l[0], set()).add(l)
    from rapidfuzz.distance import Levenshtein
    w = word.lower()
    if len(w) < 5 or not w.isalpha():
        return []
    maxd = 2 if len(w) >= 7 else 1
    hits = []
    for c in _LEMMAS.get(w[0], ()):
        if abs(len(c) - len(w)) <= maxd and c != w:
            d = Levenshtein.distance(w, c, score_cutoff=maxd)
            if d <= maxd:
                hits.append((d, c))

    def freq(c):
        return sum(l.count() for s_ in wn.synsets(c) for l in s_.lemmas() if l.name().lower() == c)
    return [c for d, c in sorted(hits, key=lambda x: (x[0], -freq(x[1]), x[1]))[:3]]


def wn_pos(lemma_lower):
    """POS candidates in WordNet 3.0 with the lemma morphy gives for each, plus the summed sense counts (frequency, deterministic)."""
    cands = {}
    for p, tag in (("n", "NOUN"), ("v", "VERB"), ("a", "ADJ"), ("r", "ADV")):
        lem = wn.morphy(lemma_lower, p)
        if lem:
            cnt = sum(l.count() for s in wn.synsets(lem, p) for l in s.lemmas() if l.name().lower() == lem)
            cands[tag] = (lem, cnt)
    return cands


def verb_form(surface, lemma):
    low = surface.lower()
    if low == lemma:
        return "base"
    if low.endswith("ing"):
        return "gerund/participle"
    exc = wn._exception_map["v"].get(low) if hasattr(wn, "_exception_map") else None
    if exc:
        return "past/participle (irregular)"
    if low.endswith("ed"):
        return "past/participle"
    if low.endswith("s"):
        return "present 3sg"
    return "inflected"


# ── the ordered POS rules ────────────────────────────────────────────────────────────────────────────────────────────────
def tag(tokens):
    """Give every token a chosen POS and keep the candidate list when ambiguous.  Returns a list of dicts."""
    T = []
    for i, (kind, s) in enumerate(tokens):
        low = s.lower()
        t = {"i": i, "kind": kind, "w": s, "low": low, "lemma": low, "cands": [], "pos": None, "feat": {}}
        T.append(t)
    n = len(T)

    def nxt(i, k=1):
        return T[i + k] if i + k < n else None

    def prv(i, k=1):
        return T[i - k] if i - k >= 0 else None

    # pass 1: everything whose class does not depend on context
    for t in T:
        low, s, kind = t["low"], t["w"], t["kind"]
        if kind in ("punct", "ell", "list"):
            t["pos"] = "PUNCT" if kind == "punct" else kind.upper()
            continue
        if kind in ("num", "frac") or low in NUMWORDS and kind == "word" and low not in ("one", "first", "second"):
            t["pos"] = "NUM"
            continue
        if (kind == "tech" or kind == "word") and s.isupper() and len(s) > 1 and s.isalpha() and (low in PRON or low in DET or low in PREP or low in BE or low in WH or low in COORD or low in MODAL or wn.morphy(low) or wn.morphy(low, "n") or wn.morphy(low, "v") or wn.morphy(low, "a") or wn.morphy(low, "r")):
            t["feat"]["emphasis"] = True               # LEAST, IS, ALL: an ordinary word in capitals (tone marker, kept for the tone channel)
            t["w_caps"] = s
        elif kind == "tech" or (kind == "word" and is_tech(s)):
            t["pos"] = "TECH"
            continue
        if low in WH:
            t["pos"] = "WH"
        elif low in NEG:
            t["pos"] = "NEG"
        elif low in ("etc", "versa", "vice", "cetera") and (low != "vice" or (T[t["i"] + 1]["low"] if t["i"] + 1 < len(T) else "") == "versa"):
            t["pos"] = "FORMULA"
        elif low in INTJ:
            t["pos"] = "INTJ"
        elif low in COORD:
            t["pos"] = "CONJ"
        elif low in MODAL:
            t["pos"] = "MODAL"
        elif low in BE:
            t["pos"] = "AUX"; t["lemma"] = "be"
            t["feat"] = dict(zip(("person", "number", "form"), BE[low])); t["feat"]["copula_or_aux"] = True
        elif low == "'s":
            t["pos"] = "POSS_OR_BE"
        elif low in PRON and low != "one":
            t["pos"] = "EXPL" if low == "there" else "PRON"
            t["feat"] = dict(zip(("person", "number", "case"), PRON[low]))
        elif low in POSS:
            t["pos"] = "DET"; t["feat"] = {"possessive": True, "person_number": POSS[low]}
        elif low in ("this", "these", "those"):
            q = T[t["i"] + 1] if t["i"] + 1 < n else None
            nounish = q is not None and q["kind"] == "word" and (wn.morphy(q["low"], "n") or wn.morphy(q["low"], "a")) and q["low"] not in BE and q["low"] not in PREP and q["low"] not in MODAL
            if nounish:
                t["pos"] = "DET"
            else:
                t["pos"] = "PRON"; t["feat"] = {"person": "3", "number": "sg-n" if low == "this" else "pl", "case": "demonstrative"}
        elif low in DET and low not in ("that", "no", "other", "another", "such", "all", "both"):
            t["pos"] = "DET"
    # pass 2: context-dependent closed-class words
    for t in T:
        if t["pos"] is not None:
            continue
        low, i = t["low"], t["i"]
        p, q = prv(i), nxt(i)
        qlow = q["low"] if q else ""
        if low in ("have", "has", "had", "having", "do", "does", "did", "doing", "done"):
            ahead = [x for x in T[i + 1:i + 4] if x["kind"] == "word" and x["pos"] in (None, "AUX", "NEG", "ADV")]
            verbish = any(wn.morphy(x["low"], "v") for x in ahead[:2])
            t["pos"] = "AUX" if (verbish and (qlow not in ("a", "an", "the") and not (q and q["low"] in DET))) else "VERB"
            t["lemma"] = "have" if low.startswith("ha") else "do"
            t["feat"] = {"form": (HAVE.get(low) or DO.get(low))}
        elif low == "to":
            nq = None
            for x in T[i + 1:i + 3]:
                if x["low"] in ADV_CLOSED:
                    continue
                nq = x
                break
            t["pos"] = "PART" if (nq and nq["kind"] == "word" and nq["low"] not in DET and nq["low"] not in PRON and nq["low"] not in POSS
                                  and (wn.morphy(nq["low"], "v") and not (nq["low"] in ("the",)))) else "PREP"
        elif low == "that":
            if q and (q["low"] in PRON and q["low"] in SUBJ_PRON or q["low"] in DET or q["low"] in POSS):
                t["pos"] = "SCONJ"
            elif q and (q["low"] in MODAL or q["low"] in BE or (q["kind"] == "word" and wn.morphy(q["low"], "v") and not wn.morphy(q["low"], "n"))):
                t["pos"] = "REL"
            elif p and p["kind"] == "word" and wn.morphy(p["low"], "n") and q and q["kind"] == "word" and wn.morphy(q["low"], "v") and q["low"].endswith("s"):
                t["pos"] = "REL"            # "the machinery that extracts the content"
            elif q and q["kind"] == "word" and (wn.morphy(q["low"], "n") or wn.morphy(q["low"], "a")) and q["low"] not in PREP:
                t["pos"] = "DET"
            else:
                t["pos"] = "PRON"; t["feat"] = {"person": "3", "number": "sg-n", "case": "demonstrative"}
        elif low in ("no", "other", "another", "such", "all", "both"):
            t["pos"] = "DET" if (q and (wn.morphy(qlow, "n") or wn.morphy(qlow, "a"))) else "INTJ" if low == "no" else "DET"
        elif low in SUBORD:
            t["pos"] = "SCONJ"
        elif low in PREP:
            clause_next = q and q["low"] in PRON and q["low"] in SUBJ_PRON
            t["pos"] = "SCONJ" if (low in ("as", "since", "before", "after", "until", "than", "like", "for") and clause_next) else "PREP"
        elif low in ADV_CLOSED:
            t["pos"] = "ADV"
        elif low == "one":
            t["pos"] = "NUM" if (q and wn.morphy(qlow, "n")) else "PRON"
            t["feat"] = {"person": "3", "number": "sg", "case": "generic"}
    # pass 3: open class by WordNet candidates, then ordered rules
    for t in T:
        if t["pos"] is not None:
            continue
        low = t["low"]
        c = wn_pos(low)
        t["cands"] = sorted(c, key=lambda k: -c[k][1])
        t["wn"] = c
        if not c:
            t["pos"] = "PROPN" if (t["w"][0].isupper() and t["i"] > 0) else "UNK"
            if t["pos"] == "UNK":
                sug = typo_of(low)
                if sug:
                    t["feat"]["typo_of"] = sug
            continue
        t["pos"] = None
    for t in T:
        if t["pos"] is not None or "wn" not in t:
            continue
        i, c, p, q = t["i"], t["wn"], prv(t["i"]), nxt(t["i"])
        ppos = p["pos"] if p else None
        qpos_cands = (q.get("wn") or {}) if q else {}
        choice = None
        if ppos in ("DET", "NUM") or (p and p["low"] in POSS):
            choice = "NOUN" if "NOUN" in c and not ("ADJ" in c and "NOUN" in qpos_cands) else ("ADJ" if "ADJ" in c else None)
        elif ppos == "PART" or ppos == "MODAL":
            choice = "VERB" if "VERB" in c else None
        elif ppos == "AUX" and p["feat"].get("form") in ("participle", "gerund", "base"):
            choice = "VERB" if "VERB" in c else None
        elif ppos in ("PRON", "EXPL") and p["feat"].get("case") in ("nom", "nom/acc") and "VERB" in c and (not q or q["pos"] != "PUNCT" or True):
            choice = "VERB" if ("NOUN" not in c or (q and q["pos"] in (None, "DET", "PRON", "PREP", "ADV", "NEG"))) else None
        elif ppos == "PREP":
            choice = "NOUN" if "NOUN" in c else ("ADJ" if "ADJ" in c else None)
        elif ppos == "NEG" and "VERB" in c:
            choice = "VERB"
        elif i == 0 or (p and p["pos"] in ("PUNCT", "ELL", "LIST")) :
            if "VERB" in c and c["VERB"][0] == low and c["VERB"][1] >= c.get("NOUN", ("", 0))[1] and (q is not None) and (q["low"] in DET or q["low"] in PRON or q["low"] in POSS or q["low"] in PREP or q["kind"] != "punct" and q["low"] in ADV_CLOSED or "NOUN" in qpos_cands):
                choice = "VERB"; t["feat"]["imperative_candidate"] = True
        if choice is None and low.endswith("ly") and "ADV" in c:
            choice = "ADV"
        if choice is None and q and q["pos"] is None and "ADJ" in c and "NOUN" in (q.get("wn") or {}) and ppos not in ("PRON",):
            choice = "ADJ"
        if choice is None and ppos == "VERB" and any(k in c for k in ("ADV", "ADJ")) and not (p and p.get("feat", {}).get("form") in (None,) and False):
            # a word right after a main verb: an adverb or adjective rather than a second verb or a noun ("spin right", "run together")
            choice = "ADV" if "ADV" in c else "ADJ"
        if choice is not None and choice != "VERB" and "VERB" in c and q and q["low"] in ("out", "up", "off", "down", "over", "away", "back", "along") and ppos not in ("DET", "NUM", "ADJ"):
            choice = "VERB"                 # particle verbs: "figure out", "get up"
        if low.endswith("s") and c.get("NOUN") and c["NOUN"][0] != low and ppos in ("NOUN", "TECH", "UNK", "ADJ", "PROPN", "NUM", "DET"):
            choice = "NOUN"                 # a plural after a noun, adjective or determiner: ".bin files", "my gains"
        if choice == "VERB" and ppos in ("NOUN", "PROPN", "TECH", "UNK") and "NOUN" in c and c["NOUN"][1] > c["VERB"][1] and not (p and p["low"].endswith("s") and False):
            choice = "NOUN"                 # noun compounds: "opposite color anchor"
        if choice == "VERB" and ppos == "VERB" and ("ADV" in c or "ADJ" in c):
            choice = "ADV" if "ADV" in c else "ADJ"
        if choice == "ADJ" and "NOUN" in c and ppos not in ("DET", "NUM", "ADJ") and c["ADJ"][1] * 4 < c["NOUN"][1]:
            choice = "NOUN"                 # a noun-dominant word between nouns ("dot center dot") stays a noun
        if choice is None:
            choice = t["cands"][0]
        t["pos"] = choice
        t["lemma"] = c[choice][0]
        t["ambiguous"] = len(c) > 1
    for t in T:
        if t["pos"] == "VERB" and "wn" in t:
            t["feat"]["form"] = verb_form(t["w"], t["lemma"])
        if t["pos"] == "POSS_OR_BE":
            p = prv(t["i"])
            q = nxt(t["i"])
            if p and p["low"] in ("it", "he", "she", "that", "there", "what", "who", "here", "where", "how") or (q and q["pos"] in (None, "VERB", "ADJ") and q["low"] in ("a", "an", "the", "not", "been", "going", "got")):
                t["pos"] = "AUX"; t["lemma"] = "be"; t["feat"] = {"person": "3", "number": "sg", "form": "present", "copula_or_aux": True}
            else:
                t["pos"] = "POSS"
        if t["pos"] == "NOUN" and t["low"] != t["lemma"]:
            t["feat"]["number"] = "pl"
    return T


# ── clause and slot assignment (the Zork-style templates) ────────────────────────────────────────────────────────────────────────────
def clauses(T):
    """(see clauses_flagged)"""
    return [c for c, _ in clauses_flagged(T)]


def clauses_flagged(T):
    """Split the tagged tokens into clauses at sentence ends, ellipses, list markers, semicolons and colons, and before a coordinating
    conjunction or subordinator that starts a new verb group."""
    out, cur = [], []
    for t in T:
        if t["pos"] in ("ELL", "LIST") or (t["pos"] == "PUNCT" and t["w"] in ".?!;:"):
            if t["pos"] == "PUNCT" and t["w"] in "?!":
                cur.append(t)
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    res = []
    for c in out:
        i = 0
        piece = []
        first_piece = True
        for j, t in enumerate(c):
            # a nominative pronoun right after a noun and before a verb group starts a (reduced) relative clause: "the primer i had created"
            if t["pos"] == "PRON" and t["feat"].get("case") == "nom" and t["low"] != "it" and piece and j > 0 and \
                    c[j - 1]["pos"] in ("NOUN", "PROPN", "TECH", "UNK", "NUM") and any(x["pos"] in ("VERB", "AUX", "MODAL") for x in piece) and \
                    any(x["pos"] in ("VERB", "AUX", "MODAL") for x in c[j + 1:j + 3]):
                res.append((piece, {"sentence_start": first_piece}))
                first_piece = False
                piece = []
            if t["pos"] in ("CONJ", "SCONJ", "REL", "WH") and piece and any(x["pos"] in ("VERB", "AUX", "MODAL") for x in piece):
                rest = c[j + 1:j + 11]
                if any(x["pos"] in ("VERB", "AUX", "MODAL") for x in rest):
                    res.append((piece, {"sentence_start": first_piece}))
                    first_piece = False
                    piece = []
            piece.append(t)
        if piece:
            res.append((piece, {"sentence_start": first_piece}))
    return res


def slots(cl, flags=None):
    """The seven data points of one clause, as lists of literal words."""
    S = {"SHELL": {}, "ANCHOR": [], "SPAN": {"relation": [], "claim": [], "frame": []}, "SCAFFOLD": [], "ELABORATE": [], "HOOK": [], "WRAP": []}
    words = [t for t in cl if t["pos"] not in ("PUNCT",)]
    low = [t["low"] for t in words]
    qmark = any(t["w"] == "?" for t in cl)
    sent_start = True if flags is None else flags.get("sentence_start", True)

    def item(t, extra=None):
        d = {"w": t["w"], "lemma": t["lemma"], "pos": t["pos"], "i": t["i"]}
        if t["feat"]:
            d["feat"] = dict(t["feat"])
        if t.get("ambiguous"):
            d["alt"] = [c for c in t.get("cands", []) if c != t["pos"]]
        if extra:
            d.update(extra)
        return d

    # SHELL
    first = words[0] if words else None
    act = "statement"
    wh = [t for t in words if t["pos"] == "WH"]
    for f in GREET_FORMULA:
        if tuple(low[:len(f)]) == f and len(words) <= len(f) + 1:
            act = "thanks" if f[0] == "thank" else "greet"
    if low in (["hello"], ["hi"], ["hey"]):
        act = "greet"
    if low and low[0] in ("bye", "goodbye"):
        act = "bye"
    if act == "statement":
        if wh and ((sent_start or qmark) and (words[0]["pos"] == "WH" or (len(words) > 1 and words[1]["pos"] == "WH")) or (wh and qmark)):
            act = "whQuestion"
        elif first and first["pos"] in ("AUX", "MODAL") and len(words) > 2 and words[1]["pos"] in ("PRON", "DET", "NOUN", "PROPN", "TECH") or (qmark and not wh):
            act = "ynQuestion"
        else:
            lead = next((t for t in words if t["pos"] not in ("ADV", "CONJ", "SCONJ", "INTJ", "NEG")), None)
            if lead is not None and lead["pos"] == "VERB" and lead.get("feat", {}).get("form") == "base" and lead.get("wn") and \
                    lead["wn"].get("VERB", ("", 0))[1] >= lead["wn"].get("NOUN", ("", 0))[1]:
                act = "imperative"
    if act == "statement" and first and first["pos"] == "INTJ" and len(words) == 1:
        act = "interjection"
    S["SHELL"] = {"act": act, "polarity": "neg" if any(t["pos"] == "NEG" for t in words) else "pos"}
    if wh and act == "whQuestion":
        S["SHELL"]["gap"] = [t["w"] for t in wh]
    ij = [t["w"] for t in words if t["pos"] == "INTJ"]
    if ij:
        S["SHELL"]["interjection"] = ij

    # chunk: NP = (DET|POSS|NUM)* ADJ* (NOUN|PROPN|TECH|UNK)+ | PRON ; PP = PREP NP ; VG = (AUX|MODAL|NEG|ADV|PART)* VERB
    i, n = 0, len(words)
    seen_verb = False
    main_verb_idx = None
    for k, t in enumerate(words):
        if t["pos"] == "VERB" and main_verb_idx is None:
            if k > 0 and words[k - 1]["pos"] == "PART":
                continue                                                         # "acceptable to find": find is secondary
            if k == 0 and t["low"].endswith("ing") and len(words) > 1 and words[1]["pos"] in ("AUX", "MODAL"):
                t["pos"] = "NOUN"; t["feat"]["gerund_subject"] = True       # "scaling has not been designed": scaling is the subject
                continue
            main_verb_idx = k
    if main_verb_idx is not None:
        j = main_verb_idx
        while j + 1 < n and words[j + 1]["pos"] == "VERB" and words[j + 1]["low"].endswith(("ed", "en", "ing")) and words[j]["pos"] == "VERB" and False:
            j += 1
        main_verb_idx = j
    copula = main_verb_idx is None and any(t["pos"] == "AUX" and t["lemma"] == "be" for t in words)
    cop_idx = next((k for k, t in enumerate(words) if t["pos"] == "AUX" and t["lemma"] == "be"), None)
    split = main_verb_idx if main_verb_idx is not None else cop_idx
    # inverted copular questions ("what is your name", "is water wet"): the subject NP follows the copula and ends at its first noun-like head
    anchor_until = None
    if copula and cop_idx is not None and act in ("whQuestion", "ynQuestion") and (cop_idx == 0 or words[cop_idx - 1]["pos"] == "WH"):
        for kk in range(cop_idx + 1, n):
            if words[kk]["pos"] in ("NOUN", "PROPN", "TECH", "UNK", "PRON"):
                anchor_until = kk
                break
    k = 0
    while k < n:
        t = words[k]
        p = t["pos"]
        if p in ("AUX", "MODAL", "PART", "EXPL"):
            S["SCAFFOLD"].append(item(t))
        elif p == "NEG":
            S["SHELL"].setdefault("negation", []).append({"w": t["w"], "i": t["i"]})
        elif p == "FORMULA":
            S["WRAP"].append(item(t))
        elif p in ("CONJ", "SCONJ", "REL"):
            S["WRAP"].append(item(t))
        elif p == "WH":
            if act != "whQuestion" or k > 1:
                S["WRAP"].append(item(t))
        elif p == "INTJ":
            S["SHELL"].setdefault("interjection", []).append(t["w"]) if False else None
        elif p == "VERB" and k == main_verb_idx:
            S["SPAN"]["relation"].append(item(t))
        elif p == "VERB":
            S["SPAN"]["relation"].append(item(t, {"role": "secondary"}))      # an infinitive, participle or gerund inside the clause
        elif p == "PREP":
            j = k + 1
            frame = [item(t, {"role": "marker"})]
            while j < n and words[j]["pos"] not in ("PREP", "CONJ", "SCONJ", "REL", "AUX", "MODAL", "VERB", "WH", "PART"):
                x = words[j]
                frame.append(item(x))
                if x["pos"] in ("TECH", "PROPN", "NUM", "UNK") or (x["pos"] not in ("DET", "PRON", "POSS", "PREP") and x["w"][:1].isupper() and x["low"] != "i"):
                    S["HOOK"].append(item(x))
                if x["pos"] == "ADJ":
                    S["ELABORATE"].append(item(x))
                j += 1
            S["SPAN"]["frame"].append(frame)
            k = j - 1
        elif p in ("DET", "NUM", "ADJ", "NOUN", "PROPN", "TECH", "UNK", "PRON", "POSS"):
            target = "ANCHOR" if (split is None or k < split) else "claim"
            if anchor_until is not None and cop_idx < k <= anchor_until:
                target = "ANCHOR"
            if split is not None and k > split and p == "ADJ" and not any(w["pos"] in ("NOUN", "PROPN", "TECH", "UNK") for w in words[k + 1:k + 3]):
                target = "claim"
            if p == "NUM" and t["kind"] == "word" and k + 1 < n and words[k + 1]["pos"] in ("NOUN", "ADJ", "PROPN"):
                S["ELABORATE"].append(item(t, {"role": "quantity"}))          # "two comparisons": a quantifier, not a specific
                k += 1
                continue
            if p == "ADJ" and any(w["pos"] in ("NOUN", "PROPN", "TECH", "UNK") for w in words[k + 1:k + 3]) and not (copula and k == (cop_idx or 0) + 1 and False):
                S["ELABORATE"].append(item(t))
            elif p == "DET":
                S.setdefault("ANCHOR_markers", []).append(item(t))           # givenness markers and possessors travel with their NP
                if t["low"] == "no":
                    S["SHELL"]["polarity"] = "neg"
            elif target == "ANCHOR":
                S["ANCHOR"].append(item(t))
            else:
                S["SPAN"]["claim"].append(item(t))
            if p in ("TECH", "PROPN", "NUM", "UNK") or (p not in ("DET", "PRON", "POSS") and t["w"][:1].isupper() and k > 0 and t["low"] != "i") or (len(t["w"]) == 1 and t["w"].isupper() and t["low"] != "i" and t["low"] != "a"):
                S["HOOK"].append(item(t))
        elif p == "ADV":
            if t["low"] in ADV_FRAME:
                S["SPAN"]["frame"].append([item(t)])
            elif t["low"] not in STOP_ADV_NOT_ELAB:
                S["ELABORATE"].append(item(t))
        k += 1
    if copula and not any(e.get("role") != "secondary" for e in S["SPAN"]["relation"]):
        S["SPAN"]["relation"].insert(0, {"w": words[cop_idx]["w"], "lemma": "NAME", "pos": "COPULA", "i": words[cop_idx]["i"]})
    # verb group features (the raw material for the conjugation / tense / participle repass)
    vg = [t for t in words if t["pos"] in ("AUX", "MODAL", "NEG", "PART") or (t["pos"] == "VERB" and t is (words[main_verb_idx] if main_verb_idx is not None else None))]
    if vg:
        feat = {"tense": "present", "aspect": [], "voice": "active", "modal": None, "person": None, "number": None}
        mv = words[main_verb_idx] if main_verb_idx is not None else None
        for t in vg:
            f = t.get("feat", {})
            if t["pos"] == "MODAL":
                feat["modal"] = t["low"]
                feat["tense"] = "future" if t["low"] in ("will", "shall") else ("past/conditional" if t["low"] in ("would", "could", "should", "might") else "present")
            elif t["pos"] == "AUX" and t["lemma"] == "be":
                if f.get("form") == "past":
                    feat["tense"] = "past"
                feat["person"], feat["number"] = f.get("person"), f.get("number")
                if mv is not None and "gerund" in mv.get("feat", {}).get("form", ""):
                    feat["aspect"].append("progressive")
            elif t["pos"] == "AUX" and t["lemma"] == "have":
                feat["aspect"].append("perfect")
                if f.get("form") == "past":
                    feat["tense"] = "past"
            elif t["pos"] == "AUX" and t["lemma"] == "do":
                if f.get("form") == "past":
                    feat["tense"] = "past"
        if mv is not None:
            form = mv.get("feat", {}).get("form", "")
            if "past" in form and not any(t["pos"] == "AUX" for t in vg):
                feat["tense"] = "past"
            if any(t["pos"] == "AUX" and t["lemma"] == "be" for t in vg) and "participle" in form and "gerund" not in form:
                feat["voice"] = "passive"
            if "present 3sg" in form:
                feat["person"], feat["number"] = "3", "sg"
        S["verb_group"] = feat
    S["_used"] = sorted({x["i"] for key in ("ANCHOR", "SCAFFOLD", "ELABORATE", "HOOK", "WRAP", "ANCHOR_markers") for x in S.get(key, []) if "i" in x}
                        | {x["i"] for fld in S["SPAN"].values() for e in fld for x in (e if isinstance(e, list) else [e]) if "i" in x}
                        | {x["i"] for x in S["SHELL"].get("negation", [])})
    return S


def granularity(T):
    """How specific is this prompt's vocabulary?  Per content word: WordNet min_depth of its first sense, sense count, hyponym count."""
    rows, depths = [], []
    for t in T:
        if t["pos"] in ("NOUN", "VERB", "ADJ", "ADV") and "wn" in t and t["lemma"] in [c[0] for c in t["wn"].values()]:
            pos = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}[t["pos"]]
            ss = wn.synsets(t["lemma"], pos)
            if ss:
                d = ss[0].min_depth()
                rows.append({"lemma": t["lemma"], "pos": pos, "depth": d, "senses": len(ss), "hyponyms": len(ss[0].hyponyms())})
                if pos in ("n", "v"):
                    depths.append(d)
    unk = [t["w"] for t in T if t["pos"] in ("UNK", "TECH", "PROPN")]
    return {"words": rows, "mean_depth": round(sum(depths) / len(depths), 2) if depths else None,
            "technical_or_unknown": unk, "technical_share": round(len(unk) / max(1, sum(1 for t in T if t["pos"] not in ("PUNCT", "ELL", "LIST"))), 3)}


def extract(text):
    invisible = len(text) - len(text.translate(ZERO_WIDTH))
    T = tag(tokenize(text))
    cls = clauses_flagged(T)
    content = []
    for t in T:
        if t["pos"] in ("NOUN", "VERB", "ADJ", "ADV", "PROPN", "TECH", "UNK", "NUM") and not (t["pos"] == "ADV" and t["low"] in ADV_CLOSED and t["low"] not in ADV_FRAME):
            content.append({"w": t["w"], "lemma": t["lemma"], "pos": t["pos"]})
    used = set()
    for c, fl in cls:
        sl = slots(c, fl)
        used |= set(sl["_used"])
        for t in c:
            if t["pos"] in ("WH", "INTJ") or (t["pos"] == "NEG"):
                used.add(t["i"])                      # recorded in SHELL (gap, interjection, negation)
    unassigned = [{"w": t["w"], "pos": t["pos"]} for t in T if t["pos"] not in ("PUNCT", "ELL", "LIST") and t["i"] not in used]
    return {"text": text, "invisible_chars_stripped": invisible, "unassigned": unassigned, "n_tokens": sum(1 for t in T if t["pos"] not in ("PUNCT", "ELL", "LIST")),
            "clauses": [{"words": " ".join(t["w"] for t in c), "slots": slots(c, fl)} for c, fl in cls], "content_words": content, "granularity": granularity(T)}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith(".jsonl"):
        out = open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout
        for line in open(sys.argv[1]):
            d = json.loads(line)
            r = extract(d["text"])
            r["id"] = d.get("id")
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        print(json.dumps(extract(" ".join(sys.argv[1:])), indent=1, ensure_ascii=False))
