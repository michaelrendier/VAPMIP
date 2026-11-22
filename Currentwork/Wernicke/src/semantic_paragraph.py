#!/usr/bin/env python3
"""
semantic_paragraph.py — paragraph recognition + higher-order prime semantic
hash, for the SEMANTIC section of monad3_c.bin.

Cody, 2026-09-04:

  The semantic part of the monad is the PARAGRAPH BUILDER along paragraph
  grammar; the phonetic is tied to context, the semantic is tied to
  content/prompt.  A prompt of more than one sentence IS a paragraph, by
  definition.  Register that in the semantic-hash side — a higher order of
  semantic hashing OUT OF A STRUCTURE.

The per-word prime semantic hash is the original one: `wordnet_boxkite`'s
`context_code` / `context_hash_v2`'s `code_omega` — each WordNet relation
carries a prime; a word's code is the squarefree product of the primes for
the relations it fires.  Codes are products, so they COMPOSE by
multiplication, and the "higher order" is the structure the multiplication
runs over:

    sentence_omega  = radical( prod over the sentence's content-word codes )
        squarefree — the SET of relations this sentence engages
    paragraph_omega = prod over the sentence omegas
        exponent of prime p_i  =  how many SENTENCES engage relation i

So the paragraph code factors into (relation, sentence-count) pairs: the
support is the paragraph's semantic footprint, and each exponent says how
sustained that relation is across the paragraph's structure.  Grammar = the
per-sentence dominant relation, in reading order — the paragraph's argument
arc (`classify → enumerate → explain → wrap`, etc.).

Recognition (`is_paragraph`, `split_sentences`) is stdlib-cheap and is what
the conversation-ingest hook calls; the WordNet hashing is done downstream
by the paragraph-builder off the sidecar spool (it loads WordNet, so it
never runs inside the hook).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

_ENDER = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]+")
# tight, explicit — a title/abbrev ending in "." is not a sentence break
_ABBREV = {"dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "mt", "vs",
           "fig", "no", "vol", "cf", "al", "etc", "e.g", "i.e", "ph.d"}
_STOP = set(
    "a an the of to in on and or is are was were be been being it its this "
    "that these those with for as at by from into over under about but so if "
    "then than there here have has had do does did not no yes i you he she we "
    "they them his her our your their my me us out up down off can will would "
    "should could may might must one two more most very just also".split())


# ── recognition — stdlib, cheap, hook-safe ─────────────────────────────────
def split_sentences(text: str) -> List[str]:
    raw = [s.strip() for s in _ENDER.split((text or "").strip()) if s.strip()]
    out: List[str] = []
    pending = ""
    for piece in raw:
        piece = (pending + " " + piece).strip() if pending else piece
        last = piece.rsplit(None, 1)[-1].rstrip(".!?\"')").lower()
        if last in _ABBREV:                   # ends on a title/abbrev — not a break
            pending = piece
            continue
        pending = ""
        out.append(piece)
    if pending:
        out.append(pending)
    return out


def is_paragraph(text: str) -> bool:
    """A prompt of more than one sentence is a paragraph, by definition."""
    return len(split_sentences(text)) > 1


def _content_words(sentence: str) -> List[str]:
    out, seen = [], set()
    for w in _WORD.findall(sentence.lower()):
        if len(w) > 2 and w not in _STOP and w not in seen:
            seen.add(w)
            out.append(w)
    return out


# ── the higher-order prime semantic hash (WordNet; downstream, not hook) ───
def _wn_bits():
    from nltk.corpus import wordnet as wn                                  # noqa: PLC0415
    from wordnet_boxkite import (RELATION_METHODS, CONTEXT_PRIMES,         # noqa: PLC0415
                                 context_vector)
    from context_hash_v2 import code_omega, _HYP                           # noqa: PLC0415
    return wn, RELATION_METHODS, CONTEXT_PRIMES, context_vector, code_omega, _HYP


def _best_synset(wn, word: str):
    ss = wn.synsets(word)
    return ss[0] if ss else None


def sentence_omega(sentence: str) -> int:
    """Squarefree code: the SET of WordNet relations the sentence's
    content-word synsets engage (radical of the product of their
    `code_omega`s)."""
    wn, _, primes, _, code_omega, _ = _wn_bits()
    present = set()
    for w in _content_words(sentence):
        s = _best_synset(wn, w)
        if s is None:
            continue
        c = code_omega(s)
        for p in primes:
            if p > c:
                break
            if c % p == 0:
                present.add(p)
    code = 1
    for p in sorted(present):
        code *= p
    return code


def paragraph_hash(sentences) -> Dict[str, Any]:
    """The structural semantic hash of a paragraph.

    `paragraph_omega` = product of the per-sentence squarefree omegas;
    factoring it gives `sentence_engage[relation] = # sentences engaging
    it` (the prime exponents) and `support` = sorted relation names.
    `grammar` = per-sentence dominant relation, in reading order."""
    wn, REL, primes, context_vector, _, hyp = _wn_bits()
    if isinstance(sentences, str):
        sentences = split_sentences(sentences)

    somegas = [sentence_omega(s) for s in sentences]
    pomega = 1
    for c in somegas:
        pomega *= c

    engage: Dict[str, int] = {}
    n = pomega
    for i, p in enumerate(primes[:len(REL)]):
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e:
            engage[REL[i]] = e

    grammar: List[str] = []
    for s in sentences:
        agg = [0] * len(REL)
        for w in _content_words(s):
            syn = _best_synset(wn, w)
            if syn is None:
                continue
            v = context_vector(syn)
            for k in range(len(REL)):
                agg[k] += v[k]
        agg[hyp] = 0                          # drop the branching channel — same
        #                                      reason code_omega excludes it
        grammar.append(REL[max(range(len(REL)), key=lambda k: agg[k])]
                       if any(agg) else "observe")

    return {
        "n_sentences": len(sentences),
        "paragraph_omega": pomega,
        "support": sorted(engage),
        "sentence_engage": engage,       # relation -> # sentences engaging it
        "grammar": grammar,              # dominant relation per sentence, in order
        "sentence_omegas": somegas,
    }


def verify() -> Dict[str, Any]:
    ok_p = (is_paragraph("The engine has sixteen operators. They fold into one "
                         "algebra.")
            and not is_paragraph("just one sentence here")
            and not is_paragraph("Dr. Crawford went home."))  # abbrev, 1 sent
    try:
        h = paragraph_hash("The volcano formed a mountain. Ash and lava fell "
                           "everywhere. The rock cooled slowly over time.")
        ok_h = (h["n_sentences"] == 3 and h["paragraph_omega"] > 1
                and len(h["grammar"]) == 3 and bool(h["support"]))
        # squarefree-per-sentence => every exponent is a sentence count
        ok_e = all(1 <= e <= h["n_sentences"]
                   for e in h["sentence_engage"].values())
        note = {"support": h["support"][:6], "grammar": h["grammar"],
                "engage": h["sentence_engage"]}
    except Exception as e:                                                 # noqa: BLE001
        ok_h = ok_e = False
        note = f"{type(e).__name__}: {e}"
    return {"ok": bool(ok_p and ok_h and ok_e),
            "recognition": ok_p, "hash": ok_h, "exponents_bounded": ok_e,
            "sample": note}


if __name__ == "__main__":
    import json
    for t in ["The engine contains sixteen distinct operators. They fold into "
              "a single algebra that speaks both continuous and discrete.",
              "She ordered the blue plate special. It came with grits.",
              "one sentence only, not a paragraph"]:
        print(f">>> {t}")
        print("   is_paragraph:", is_paragraph(t))
        if is_paragraph(t):
            print("   ", json.dumps(paragraph_hash(t), default=str)[:500])
    print(verify())
