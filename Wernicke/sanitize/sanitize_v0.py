#!/usr/bin/env python3
"""sanitize_v0.py — token-level sanitiser for the granular bins (Wernicke tree).  Deterministic ruleset; no training.

Shape: ENV is a dict of named tables, used like a Bash environment.  A loop looks a keyword up and the value (a function or
data) is what runs; to change a rule, override one key (`ENV["TIER"]["PROPER"] = ...`) rather than edit a branch.
    ENV["CLASS"]   math_isolate.classify() result  -> handler(tok)   (GARBAGE/REF/FORMULA/NUMBER/GREEK are quarantined by reason)
    ENV["ADMIT"]   ordered {check_name: fn(tok) -> reason|None}      (first failing check names the quarantine reason)
    ENV["TIER"]    {A|B|C: fn(lemma) -> bool}                        (which WordNet write tier a clean token belongs to)
    ENV["CHROME"]  data: page-chrome words (Wikipedia UI, citation scaffolding, interlanguage names)

Tiers (Wernicke/sanitize README in the notes):  A = lemma in WordNet (relation evidence only),  C = proper noun (HOOK table, never
vocabulary),  B = candidate new entry — needs PROSE evidence (>=2 sentences, >=2 documents, a definitional frame naming a WordNet
hypernym), which a bag-of-words bin cannot supply, so here B is only "candidate, evidence pending".
Nothing is deleted: every rejected token goes to the quarantine table with a reason code.
"""
import collections, json, os, pickle, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
import math_isolate as mi
for _m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
    sys.modules.setdefault(_m, None)
from nltk.corpus import wordnet as wn

CHROME = {w for w in """wikipedia jump to content search donate create account log in personal tools languages edit links from the free
encyclopedia navigation retrieved archived isbn issn oclc doi bibcode jstor pmid arxiv hdl cs1 citation mathworld wolfram hyperphysics feynman
main page contents current events random article about contact help learn community portal recent changes upload file special pages
permanent link page information cite this print export download printable version what here related changes tools appearance hide
deutsch español français italiano português nederlands polski svenska türkçe čeština dansk suomi magyar română català esperanto euskara
cymraeg eesti brezhoneg bosanski føroyskt simple english tiếng việt afrikaans alemannisch aragonés ænglisc asturianu azərbaycanca
bân-lâm-gí emiliàn rumagnòl vosa vakaviti võro žemaitėška zazaki""".split()}
VOWEL = re.compile(r"[aeiouy]")
LATIN_WORD = re.compile(r"^[a-z]+(?:['-][a-z]+)*$")
TIME_EXPR = re.compile(r"^(mid-)?\d{1,4}(st|nd|rd|th|s)$")
from nltk.corpus import stopwords as _sw
CLOSED = set(_sw.words("english")) | {"whom", "whose", "thus", "hence", "via", "per", "upon", "within", "without", "among", "amongst", "toward", "towards", "although", "though", "whereas", "whether", "unless", "since", "while", "because"}


class Rules:
    """Every dispatch function is a pure @staticmethod: token (or lemma) in, verdict out, no state, no self, no side effects
    (the shape Archimedes' maths functions use).  ENV below maps keywords to these functions."""

    @staticmethod
    def q_garbage(tok):
        return ("Q", "garbage")

    @staticmethod
    def q_ref(tok):
        return ("Q", "ref")

    @staticmethod
    def q_formula(tok):
        return ("Q", "formula")

    @staticmethod
    def q_number(tok):
        return ("Q", "number")

    @staticmethod
    def q_greek(tok):
        return ("Q", "greek")

    @staticmethod
    def q_unclassified(tok):
        return ("Q", "unclassified")

    @staticmethod
    def pass_word(tok):
        return None

    @staticmethod
    def check_time(tok):
        return "time_expression" if TIME_EXPR.match(tok.lower()) else None

    @staticmethod
    def check_chrome(tok):
        return "chrome" if tok.lower() in CHROME else None

    @staticmethod
    def check_script(tok):
        return None if LATIN_WORD.match(tok.lower()) else "non_latin_or_symbol"

    @staticmethod
    def check_variable(tok):
        t = tok.lower().replace("'s", "")
        return "single_letter" if len(t) < 2 and t not in ("a", "i") else None

    @staticmethod
    def check_vowel(tok):
        t = tok.lower().replace("-", "").replace("'s", "")
        return "no_vowel" if len(t) >= 2 and not VOWEL.search(t) else None

    @staticmethod
    def check_shape(tok):
        parts = tok.lower().replace("'s", "").split("-")
        return "consonant_run" if any(re.search(r"[^aeiouy]{6,}", x) for x in parts) else None

    @staticmethod
    def tier_proper(lemma):
        ss = wn.synsets(lemma, pos="n")
        return bool(ss) and all(s.instance_hypernyms() for s in ss) and not wn.synsets(lemma, pos="v") and not wn.synsets(lemma, pos="a")

    @staticmethod
    def tier_function(lemma):
        return lemma in CLOSED

    @staticmethod
    def lemma_of(tok):
        t = tok.lower()
        t = t[:-2] if t.endswith("'s") else t
        for p in "nvar":
            l = wn.morphy(t, p)
            if l and wn.synsets(l, pos=p):
                return l, p
        return (t, None) if wn.synsets(t) else (None, None)


ENV = {
    "CLASS": {"GARBAGE": Rules.q_garbage, "REF": Rules.q_ref, "FORMULA": Rules.q_formula, "NUMBER": Rules.q_number,
              "GREEK": Rules.q_greek, "WORD": Rules.pass_word},
    "ADMIT": {"time": Rules.check_time, "chrome": Rules.check_chrome, "script": Rules.check_script, "variable": Rules.check_variable,
              "vowel": Rules.check_vowel, "shape": Rules.check_shape},
    "TIER": {"C": Rules.tier_proper, "F": Rules.tier_function},
    "LEMMA": Rules.lemma_of,
    "CHROME": CHROME,
}


def sanitize_token(tok):
    """-> (tier, reason, lemma).  tier in A, B, C, F, Q."""
    tok = tok.replace("’", "'")
    r = ENV["CLASS"].get(mi.classify(tok), Rules.q_unclassified)(tok)
    if r:
        return r[0], r[1], None
    for name, fn in ENV["ADMIT"].items():
        reason = fn(tok)
        if reason:
            return "Q", reason, None
    base = tok.lower()[:-2] if tok.lower().endswith("'s") else tok.lower()
    if ENV["TIER"]["F"](base):
        return "F", "function_word", base
    lemma, pos = ENV["LEMMA"](tok)
    if lemma is None and "-" in base and all(ENV["LEMMA"](x)[0] for x in base.split("-")):
        return "B", "compound_of_known_parts", base
    if lemma is None:
        return "B", "candidate_evidence_pending", tok.lower().replace("'s", "")
    if ENV["TIER"]["C"](lemma):
        return "C", "proper_noun", lemma
    return "A", "in_wordnet", lemma


def run(bin_path, name):
    d = pickle.load(open(bin_path, "rb"))
    words = [w for w in d["words"] if isinstance(w, str)]
    tiers = collections.defaultdict(set)
    reasons = collections.Counter()
    sample = collections.defaultdict(list)
    for w in words:
        t, why, lem = sanitize_token(w)
        reasons[(t, why)] += 1
        if len(sample[(t, why)]) < 12:
            sample[(t, why)].append(w)
        if lem:
            tiers[t].add(lem)
    out = {"bin": name, "tokens": len(words), "reasons": {f"{t}:{why}": n for (t, why), n in sorted(reasons.items())},
           "tier_lemmas": {t: len(s) for t, s in tiers.items()}, "samples": {f"{t}:{why}": v for (t, why), v in sample.items()}}
    return out, tiers


if __name__ == "__main__":
    pt = os.environ.get("PTORRENT_BINS", "/home/rendier/Projects/ThePlace/PTorrent/bin_archive")
    report = {}
    for n in ("monad_mathematics", "monad_physics"):
        rep, tiers = run(f"{pt}/clean/{n}.bin", n)
        report[n] = rep
        json.dump({t: sorted(s) for t, s in tiers.items()}, open(os.path.join(HERE, f"{n}.tiers.json"), "w"), ensure_ascii=False)
    json.dump(report, open(os.path.join(HERE, "report_v0.json"), "w"), indent=1, ensure_ascii=False)
    for n, rep in report.items():
        print(n, rep["tokens"], "tokens; distinct lemmas per tier", rep["tier_lemmas"])
        for k, v in rep["reasons"].items():
            print(f"   {k:34} {v:6}   {rep['samples'][k][:8]}")
