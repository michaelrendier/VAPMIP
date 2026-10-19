#!/usr/bin/env python3
"""vocab_build.py — per-language vocabulary tables from the Wiktionary extracts (kaikki.org), and the words that exist in only one language.

For every language in corpora/lexicon/kaikki-<Language>.jsonl:
  key        NFC, lower-cased headword (the string the Unicode engine's tokenizer would produce, when it is a single token)
  is_form    the entry is an inflected form or alternative form of another headword (form_of / alt_of in a sense)
  etym       inherited | borrowed | derived | unknown   (from the first words of etymology_text; Wiktionary's own phrasing)
  mentions   test-bed or contact languages named in the etymology text (a contact flag, not a verdict)
Exclusive = the key is a lemma of this language and of no other test-bed language (string level, after NFC + lower-casing).
Clean     = exclusive, not borrowed, and no contact language mentioned in its etymology (no evidence of borrowing).
Verified  = clean and the etymology says inherited or derived (an etymology is given and it is native).

    python3 tools/vocab_build.py            # writes corpora/derived/lex_<lang>.tsv, exclusive_<lang>.txt, vocab_report.json
"""
import collections, glob, json, os, re, sys, unicodedata as ud
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
LEX = os.path.join(ROOT, "corpora", "lexicon"); OUT = os.path.join(ROOT, "corpora", "derived")
sys.path.insert(0, HERE)
LANGS = ["English", "Chinese", "Swahili", "Finnish", "Indonesian", "Quechua"]
CONTACT = ["Chinese", "Mandarin", "Hokkien", "Min Nan", "Cantonese", "Hakka", "Old Chinese", "Middle Chinese", "English", "Arabic", "Spanish", "Portuguese", "Latin", "Greek",
           "Swedish", "German", "Dutch", "French", "Sanskrit", "Malay", "Javanese", "Persian", "Hindi", "Russian", "Japanese", "Aymara", "Quechua", "Finnish", "Indonesian",
           "Swahili", "Old Norse", "Proto-Germanic", "Proto-Indo-European", "Turkish", "Tamil", "Gujarati", "Italian", "Norman", "Old French", "Middle English", "Old English"]
CONTACT_RE = re.compile(r"\b(" + "|".join(re.escape(c) for c in sorted(CONTACT, key=len, reverse=True)) + r")\b")
BORROW_RE = re.compile(r"^\s*(Borrowed|Learned borrowing|Semi-learned|Calque|Loan|Unadapted borrowing|Partial calque|From (?!Proto-)|Back-formation|Clipping of)", re.I)
INHER_RE = re.compile(r"^\s*(Inherited|From Proto-|Cognate|Unknown|Uncertain|Native)", re.I)
DERIV_RE = re.compile(r"^\s*(Derived from|Compound|Univerbation|From [^,.]* \+|Formed from|\S+ \+ \S+)", re.I)


def etym_class(t):
    if not t: return "unknown"
    h = t.strip()[:160]
    if INHER_RE.match(h): return "inherited"
    if BORROW_RE.match(h): return "borrowed"
    if DERIV_RE.match(h): return "derived"
    return "unknown"


def key_of(w): return ud.normalize("NFC", w).casefold()


def read(lang):
    rows = {}
    path = os.path.join(LEX, f"kaikki-{lang}.jsonl")
    man = os.path.join(ROOT, "corpora", "MANIFEST.tsv")             # a file counts only once fetch.sh has recorded it as complete
    if not os.path.exists(path) or f"lexicon/kaikki-{lang}.jsonl\t" not in open(man).read(): return None
    for line in open(path, encoding="utf-8"):
        d = json.loads(line); w = d.get("word", "")
        if not w or " " in w.strip(): continue                     # single-token headwords only (the engine's unit)
        sens = d.get("senses", [])
        is_form = bool(sens) and all(("form_of" in s or "alt_of" in s) for s in sens)
        gl = next((g for s in sens for g in s.get("glosses", [])), "")
        t = d.get("etymology_text", "")
        k = key_of(w); r = rows.setdefault(k, dict(key=k, pos=set(), is_form=True, etym="unknown", mentions=set(), gloss="", n=0))
        r["pos"].add(d.get("pos", "")); r["n"] += 1
        r["is_form"] = r["is_form"] and is_form
        if t and r["etym"] == "unknown": r["etym"] = etym_class(t)
        r["mentions"].update(m for m in CONTACT_RE.findall(t) if m != lang)
        if not r["gloss"] and gl: r["gloss"] = gl[:80]
    return rows


def main():
    tabs = {}
    for L in LANGS:
        t = read(L)
        if t is None: print("missing", L); continue
        tabs[L] = t
    lemma_keys = {L: {k for k, r in t.items() if not r["is_form"]} for L, t in tabs.items()}
    all_keys = {L: set(t) for L, t in tabs.items()}
    rep = {}
    os.makedirs(OUT, exist_ok=True)
    for L, t in tabs.items():
        others = set().union(*[all_keys[o] for o in all_keys if o != L]) if len(all_keys) > 1 else set()
        excl = {k for k in lemma_keys[L] if k not in others}
        clean = {k for k in excl if t[k]["etym"] != "borrowed" and not t[k]["mentions"]}      # no evidence of borrowing
        verified = {k for k in clean if t[k]["etym"] in ("inherited", "derived")}               # an etymology is given and says native
        shared = {k for k in lemma_keys[L] if k in others}
        with open(os.path.join(OUT, f"lex_{L}.tsv"), "w", encoding="utf-8") as f:
            f.write("key\tpos\tis_form\tetym\tmentions\texclusive\tclean\tgloss\n")
            for k in sorted(t):
                r = t[k]; f.write("\t".join([k, "/".join(sorted(r["pos"])), str(int(r["is_form"])), r["etym"], ",".join(sorted(r["mentions"])), str(int(k in excl)), str(int(k in clean)), r["gloss"]]) + "\n")
        open(os.path.join(OUT, f"exclusive_{L}.txt"), "w", encoding="utf-8").write("\n".join(sorted(excl)) + "\n")
        ec = collections.Counter(r["etym"] for k, r in t.items() if k in lemma_keys[L])
        rep[L] = dict(headwords=len(t), lemmas=len(lemma_keys[L]), forms=len(t) - len(lemma_keys[L]), etym=dict(ec), shared_with_another_language=len(shared),
                      exclusive=len(excl), clean_exclusive=len(clean), verified_native_exclusive=len(verified))
        print(L, rep[L])
    json.dump(rep, open(os.path.join(OUT, "vocab_report.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
