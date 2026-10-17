"""
The reducer + the check.

reduce(sent) -> Shadow:
    pos          the POS sequence
    ring         the box-kite ring: e0 = the finite verb (anchor, no work),
                 e1..eK = dependents; edges = UD deprels
    spoca        {slot: [forms]}  over S P O_d O_i C_s C_o A
    pattern      one of the 7 clause patterns  (the sail of the box-kite)
    verb, verb_lemma

check(shadow) -> {verdict, licensed, residue}:
    'prime'      the verb licenses this clause pattern  (well-formed)
    'composite'  it does not  (residue = the unlicensed pattern)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from . import conllu
from .frames import frame_of, PATTERNS

SUBJ = {"nsubj", "nsubj:pass", "csubj", "csubj:pass", "expl"}
DOBJ = {"obj"}
IOBJ = {"iobj"}
OBL  = {"obl", "obl:tmod", "obl:npmod", "advmod", "advcl"}
XC   = {"xcomp", "ccomp"}


@dataclass
class Shadow:
    text: str
    verb: str
    verb_lemma: str
    verb_upos: str
    pos: List[str]
    ring: Dict[str, str]                       # deprel -> head form (e1..eK)
    spoca: Dict[str, List[str]] = field(default_factory=dict)
    pattern: str = "SV"


def reduce(sent: conllu.Sent) -> Shadow | None:
    r = sent.root
    if r is None:
        return None
    kids = [t for t in sent.children(r.id) if t.deprel != "punct"]
    deprels = [t.deprel for t in kids]
    has_cop = any(t.deprel == "cop" for t in kids)
    # copular: the root is the predicate; the cop is the finite verb
    finite = next((t for t in kids if t.deprel == "cop"), r)

    spoca: Dict[str, List[str]] = {}
    for t in kids:
        d = t.deprel
        slot = ("S" if d in SUBJ else "O_d" if d in DOBJ else "O_i" if d in IOBJ
                else "C" if (d == "cop" or (has_cop and t is not finite and d not in SUBJ))
                else "A" if d in OBL else "X" if d in XC else None)
        if slot:
            spoca.setdefault(slot, []).append(t.form)

    n_od = sum(1 for t in kids if t.deprel in DOBJ)
    n_oi = sum(1 for t in kids if t.deprel in IOBJ)
    has_obl = any(t.deprel in ("obl",) for t in kids)
    has_xc = any(t.deprel in XC for t in kids)

    if has_cop:
        pat = "SVA" if (has_obl and not any(t.deprel in DOBJ for t in kids)
                        and r.upos not in ("ADJ", "NOUN", "PROPN", "PRON")) else "SVC"
    elif n_oi >= 1 and n_od >= 1:
        pat = "SVOO"
    elif n_od >= 1 and has_xc:
        pat = "SVOC"
    elif n_od >= 1 and has_obl:
        pat = "SVOA"
    elif n_od >= 1:
        pat = "SVO"
    elif has_obl and r.upos == "VERB" and not has_xc:
        pat = "SVA"
    else:
        pat = "SV"

    ring = {}
    for t in kids:
        ring[t.deprel] = ring.get(t.deprel, t.form)
    return Shadow(
        text=sent.text, verb=finite.form, verb_lemma=r.lemma if not has_cop else "be",
        verb_upos=finite.upos,
        pos=[t.upos for t in sent.toks], ring=ring, spoca=spoca, pattern=pat)


def check(sh: Shadow) -> dict:
    fr = frame_of(sh.verb_lemma)
    licensed = set(fr["licensed_patterns"])
    ok = sh.pattern in licensed
    return {
        "verdict": "prime" if ok else "composite",
        "pattern": sh.pattern,
        "licensed": sorted(licensed),
        "residue": None if ok else sh.pattern,
        "verb_known": fr["known"],
    }


if __name__ == "__main__":
    from collections import Counter
    dist, verd = Counter(), Counter()
    n = shown = 0
    for s in conllu.read(conllu.EWT["dev"]):
        sh = reduce(s)
        if sh is None:
            continue
        n += 1
        dist[sh.pattern] += 1
        c = check(sh)
        verd[c["verdict"] if c["verb_known"] else "verb-unknown"] += 1
        if shown < 8 and c["verb_known"]:
            shown += 1
            print(f"\n{s.text[:88]}")
            print(f"   verb={sh.verb_lemma:<12} pattern={sh.pattern:<5} "
                  f"SPOCA={ {k: v for k, v in sh.spoca.items()} }")
            print(f"   -> {c['verdict']}   licensed={c['licensed']}"
                  + (f"   residue={c['residue']}" if c['residue'] else ""))
    print(f"\n{n} sentences   pattern distribution: {dict(dist.most_common())}")
    print(f"check verdicts: {dict(verd)}")
