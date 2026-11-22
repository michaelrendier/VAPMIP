#!/usr/bin/env python3
"""compare_answers.py — slot-by-slot agreement of extract_v0 with the 40 model-provided reference answers (Wernicke/corpus/answers_seed.jsonl).
The references are Claude's, unreviewed: this measures consistency with them, not truth.  Agreement is on lowercase word sets, per slot."""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_v0 as X
HERE = os.path.dirname(os.path.abspath(__file__))
from nltk.corpus import wordnet as wn
def norm(w):
    return next((m for p in "nvar" if (m := wn.morphy(w, p))), w)
def toks(x):
    out = set()
    for e in x if isinstance(x, list) else [x]:
        if isinstance(e, list):
            out |= toks(e)
        elif isinstance(e, dict):
            w = e.get("w", "").lower()
            if e.get("lemma") not in ("NAME",) and w:
                out.add(norm(w))
        else:
            out |= {norm(w) for w in re.findall(r"[a-z0-9'’./-]+", str(e).lower()) if not w.startswith("<") and w not in ("you", "the", "a", "an", "to", "of", "in", "on", "at", "for", "with", "about", "by", "from", "name_")}
    return {w for w in out if w}
def mine(r, key):
    S = [c["slots"] for c in r["clauses"]]
    if key == "ANCHOR":
        return set().union(*[toks(s["ANCHOR"]) for s in S]) if S else set()
    if key in ("relation", "claim", "frame"):
        return set().union(*[toks(s["SPAN"][key]) for s in S]) if S else set()
    return set().union(*[toks(s[key]) for s in S]) if S else set()
def ref(a, key):
    if key == "ANCHOR": return toks(a["ANCHOR"])
    sp = a["SPAN"]
    if isinstance(sp, list):
        sp = {k: sum((x.get(k) or [] for x in sp if isinstance(x.get(k), list)), []) + [x[k] for x in sp if isinstance(x.get(k), str)] for k in ("relation", "claim", "frame")}
    if key in ("relation", "claim", "frame"):
        v = sp.get(key)
        return toks(v if isinstance(v, list) else [v] if v else [])
    return toks(a.get(key, []))
tot = {k: [0, 0, 0] for k in ("ANCHOR", "relation", "claim", "frame", "SCAFFOLD", "ELABORATE", "HOOK", "WRAP")}
act_ok = pol_ok = n = 0
for line in open(os.path.join(HERE, "..", "corpus", "answers_seed.jsonl")):
    a = json.loads(line); r = X.extract(a["text"]); n += 1
    s0 = r["clauses"][0]["slots"]["SHELL"] if r["clauses"] else {}
    acts = {c["slots"]["SHELL"]["act"] for c in r["clauses"]}
    act_ok += a["SHELL"]["act"] in acts or (a["SHELL"]["act"] == "greet" and "interjection" in acts)
    pol_ok += any(c["slots"]["SHELL"]["polarity"] == a["SHELL"]["polarity"] for c in r["clauses"]) or a["SHELL"]["polarity"] == "pos" and not any(c["slots"]["SHELL"]["polarity"] == "neg" for c in r["clauses"])
    for k in tot:
        m, f = mine(r, k), ref(a, k)
        tot[k][0] += len(m & f); tot[k][1] += len(m); tot[k][2] += len(f)
print(f"{n} reference answers; SHELL.act matched {act_ok}/{n}, polarity {pol_ok}/{n}")
for k, (hit, nm, nf) in tot.items():
    p = hit / nm if nm else 0; rc = hit / nf if nf else 0
    print(f"  {k:10s} words extracted {nm:3d}, reference {nf:3d}, shared {hit:3d}   precision {100*p:4.0f}%  recall {100*rc:4.0f}%")
