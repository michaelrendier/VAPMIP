"""
build monad_sentences.json — the box-kite sentence index.

  verbs    : lemma -> frame  (VerbNet classes/roles + PropBank rolesets +
             the licensed clause patterns — which SAILS the verb's ring can fly)
  sails    : pattern -> {deprel skeleton, frequency, example}
             each of the 7 clause patterns is one sail of the box-kite: a fixed
             subset of the ~37 UD relation-edges lit up around e0 (the finite verb).
  meta     : corpus counts, reducer verdict tallies.

To construct a sentence: pick e0 (a verb), pick one of its licensed sails,
fill the lit edges with fillers.  monad_sentences.bin is the packed form of this.
"""
from __future__ import annotations
import json
import os
from collections import Counter, defaultdict
from . import conllu
from .frames import frame_of, verbnet_index, propbank_index, PATTERNS
from .shadow import reduce, check

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "monad_sentences.json")


def run():
    sail_edges = defaultdict(Counter)      # pattern -> Counter(deprel)
    sail_freq = Counter()
    sail_example = {}
    verd = Counter()
    verbs_seen = Counter()
    n = 0
    for split in ("train", "dev", "test"):
        for corpus in (conllu.EWT, conllu.GUM):
            path = corpus[split]
            if not os.path.exists(path):
                continue
            for s in conllu.read(path):
                sh = reduce(s)
                if sh is None:
                    continue
                n += 1
                sail_freq[sh.pattern] += 1
                sail_edges[sh.pattern].update(sh.ring.keys())
                sail_example.setdefault(sh.pattern, s.text[:120])
                verbs_seen[sh.verb_lemma] += 1
                c = check(sh)
                verd[c["verdict"] if c["verb_known"] else "verb-unknown"] += 1

    vi, pi = verbnet_index(), propbank_index()
    all_lemmas = sorted(set(vi) | set(pi))
    verbs = {}
    for lem in all_lemmas:
        fr = frame_of(lem)
        verbs[lem] = {
            "vn_classes": fr["vn_classes"],
            "themroles": fr["themroles"],
            "pb_rolesets": fr["pb_rolesets"],
            "pb_argmax": fr["pb_argmax"],
            "sails": fr["licensed_patterns"],         # the sails this ring can fly
            "corpus_count": verbs_seen.get(lem, 0),
        }

    sails = {}
    for p in PATTERNS:
        skel = [d for d, _ in sail_edges[p].most_common(10)]
        sails[p] = {
            "skeleton": skel,
            "core": [d for d in skel if d in
                     ("nsubj", "obj", "iobj", "cop", "obl", "xcomp", "ccomp")],
            "frequency": sail_freq[p],
            "example": sail_example.get(p, ""),
        }

    index = {
        "meta": {
            "sentences": n,
            "verbs": len(verbs),
            "vn_lemmas": len(vi), "pb_lemmas": len(pi),
            "verdicts": dict(verd),
            "note": "e0 = the finite verb (anchor); the 7 sails are subsets of the "
                    "UD relation-edges; a verb's ring flies only its licensed sails.",
        },
        "sails": sails,
        "verbs": verbs,
    }
    with open(OUT, "w") as f:
        json.dump(index, f, indent=1, default=list)
    print(f"wrote {os.path.relpath(OUT)}  —  {n} sentences, {len(verbs)} verbs")
    print(f"sail frequencies: {dict(sail_freq.most_common())}")
    print(f"reducer verdicts: {dict(verd)}")
    for p in PATTERNS:
        print(f"  {p:5} core edges: {sails[p]['core']}   (n={sail_freq[p]})")
    return index


if __name__ == "__main__":
    run()
