"""
maths_sanitize.py — clean monad_mathematics.bin's flat scrape into real
vocabulary, and feed it to the TWO places Cody named (2026-09-11):

    "sanitizing the 'mathematical corpus' and adding it to the vocabulary...
    the complete vocabulary needs to be in monad3_c.bin, and upon
    granularity, the mathematics.bin adds weight to the already present
    vocabulary... it should become the primary 'lexicon' in the case of
    granularity."

  1. monad3_c.bin — via Callimachus/vocab_update.py's already-running,
     already-built LIVE ingest path (the `document` INGEST_POLICY class,
     Crank.learn, the in-place fold / repack-on-threshold machinery).
     Not a bespoke merge tool — the existing one, used as designed.
  2. monad_sentences.json's filler pool (build.py) — tagged
     `"source": "maths"` so the sentence creator can SELECT these words as
     the PRIMARY lexicon once a topic gates in (see sem_hash.is_maths_
     eligible, and generate.py's _resonant_pick), not just detect presence.

Filter: the structural junk regex ptol_layer.py already uses for this exact
corpus (LaTeX, mojibake, bibcodes, non-ASCII), narrowed further by requiring
a real WordNet noun or adjective sense — surnames and journal-abbreviation
noise ("abhandlung", "brummelen", "aabh") have no WordNet entry and are
dropped; genuine terms ("abelian", "eigenvalue", "polynomial") pass.

Disclosed limitation, not silently papered over: WordNet also carries
proper-noun senses for common place/person names ("Aachen", "Budapest",
"Aaron") — this is a structural + lexical filter, not named-entity
recognition, so a small number of those pass through. Measured, 2026-09-11:
56,451 raw tokens -> 17,075 pass the structural filter -> 9,484 pass the
added WordNet noun/adjective membership check.
"""
from __future__ import annotations
import os
import pickle
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_THE_PLACE = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
MATHS_BIN = os.path.join(_THE_PLACE, "PTorrent", "bin_archive", "clean",
                         "monad_mathematics.bin")

# mirrors PtolC/ptol_layer.py's _JUNK_RE / _clean_word — the same corpus,
# the same known crud (un-sanitised LaTeX, arXiv bibcodes, mojibake).
_JUNK_RE = re.compile(r"[\\{}$^~|_.]|--|\d{3,}|^[^A-Za-z]|[^A-Za-z]$|[^\x00-\x7f]")


def _structural_ok(w: str) -> bool:
    if not w or _JUNK_RE.search(w) or "'" in w:
        return False
    letters = sum(c.isalpha() for c in w)
    return letters >= 3 and letters / len(w) >= 0.9


def _wn():
    for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
        sys.modules.setdefault(m, None)
    from nltk.corpus import wordnet as wn
    return wn


def raw_words(path: str = MATHS_BIN) -> list:
    with open(path, "rb") as f:
        d = pickle.load(f)
    return [w for w in d.get("words", []) if isinstance(w, str)]


def sanitize(path: str = MATHS_BIN) -> dict:
    """Returns {lemma: pos} — pos is 'n' or 'a' (prefers noun), the same
    shape build.py's filler pipeline already expects.

    Lemmatizes via WordNet's morphy before keying the dict — the raw scrape
    is surface forms, not lemmas (unlike the EWT/GUM corpus fillers, whose
    lemma already comes off the CoNLL-U parse), so "theorems"/"polyhedra"/
    "matrices" would otherwise enter as SEPARATE lexicon entries from
    "theorem"/"polyhedron"/"matrix" — confirmed live: this produced
    "Theorems is able." (a bare plural surface form picked as a singular-
    agreeing subject) before this fix."""
    wn = _wn()
    structural = {w.lower() for w in raw_words(path) if _structural_ok(w)}
    out = {}
    for w in structural:
        lemma_n = wn.morphy(w, "n")
        if lemma_n and wn.synsets(lemma_n, pos="n"):
            out[lemma_n] = "n"
            continue
        lemma_a = wn.morphy(w, "a")
        if lemma_a and wn.synsets(lemma_a, pos="a"):
            out[lemma_a] = "a"
    return out


def push_to_monad3c(words=None, chunk: int = 200) -> dict:
    """The real path, not a bespoke one: Callimachus/vocab_update.py's
    `document`-class stream into the live daemon (Crank.learn ->
    monad3c_fold_inplace -> repack-on-threshold). Returns vu.status()."""
    pdesk = os.path.join(_THE_PLACE, "PtolemyDesktop")
    if pdesk not in sys.path:
        sys.path.insert(0, pdesk)
    from Callimachus.vocab_update import VocabUpdate

    if words is None:
        words = sorted(sanitize())
    vu = VocabUpdate(cls="document")
    vu.register_with_forge()
    n = vu.push_words(words, chunk=chunk)
    st = vu.status()
    st["words_pushed"] = n
    return st


if __name__ == "__main__":
    import json
    words = sanitize()
    print(f"sanitized: {len(words)} words "
          f"(n={sum(1 for p in words.values() if p == 'n')}, "
          f"a={sum(1 for p in words.values() if p == 'a')})")
    if "--push" in sys.argv:
        st = push_to_monad3c(sorted(words))
        print(json.dumps(st, indent=2))
    else:
        print("(dry run — pass --push to stream into the live daemon)")
