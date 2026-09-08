"""
Verb frame index — which clause SHADOWS a verb is licensed to cast.

VerbNet 3.4  : class -> thematic roles + syntactic-frame 'primary' strings
PropBank 3.4 : lemma -> rolesets (Arg0..ArgN descriptors) + VerbNet links

primary -> one of the 7 clause patterns (Quirk et al.):
    SV  SVO  SVC  SVA  SVOO  SVOC  SVOA
"""
from __future__ import annotations
import os
import re
import glob
import xml.etree.ElementTree as ET
from functools import lru_cache

_DS = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
VN_DIR = os.path.join(_DS, "verbnet", "verbnet3.4")
PB_DIR = os.path.join(_DS, "propbank-frames", "frames")

PATTERNS = ("SV", "SVO", "SVC", "SVA", "SVOO", "SVOC", "SVOA")


def primary_to_pattern(primary: str) -> str:
    """VerbNet frame 'primary' string -> a 7-pattern label (best effort)."""
    p = primary.strip()
    toks = p.split()
    # normalise: keep V, NP, and the head of each PP/ADJ/ADV/S slot
    slots = []
    for t in toks:
        b = t.split(".")[0].split("_")[0]
        if b in ("NP", "V", "ADJ", "ADJP", "ADV", "ADVP", "S", "S-Quote"):
            slots.append("ADJ" if b == "ADJP" else "ADV" if b == "ADVP" else b)
        elif b in ("PP", "PREP"):
            slots.append("PP")
    if "V" not in slots:
        return "SV"
    v = slots.index("V")
    after = slots[v + 1:]
    nps = after.count("NP")
    has_pp = "PP" in after
    has_adj = "ADJ" in after
    has_adv = "ADV" in after
    has_s = "S" in after or "S-Quote" in after
    if nps == 0:
        if has_adj:
            return "SVC"
        if has_pp or has_adv:
            return "SVA"
        return "SV"
    if nps == 1:
        if has_adj or has_s:
            return "SVC"          # NP V NP.ADJ handled as SVO below unless first NP is subj-comp
        if has_pp:
            # NP V NP PP.recipient == ditransitive; else complex-transitive locative
            return "SVOO" if re.search(r"PP\.(recipient|beneficiary|goal)", p) else "SVOA"
        if has_adv:
            return "SVOA"
        return "SVO"
    # nps >= 2
    if has_adj:
        return "SVOC"
    return "SVOO"


@lru_cache(maxsize=1)
def verbnet_index() -> dict:
    """lemma -> {classes:set, themroles:set, patterns:Counter-as-dict}"""
    from collections import Counter
    idx: dict = {}
    for path in glob.glob(os.path.join(VN_DIR, "*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for vnclass in [root] + root.findall(".//VNSUBCLASS"):
            cid = vnclass.get("ID") or root.get("ID")
            roles = {r.get("type") for r in vnclass.findall("./THEMROLES/THEMROLE")}
            if not roles:
                roles = {r.get("type") for r in root.findall("./THEMROLES/THEMROLE")}
            pats = Counter(primary_to_pattern(f.find("DESCRIPTION").get("primary", ""))
                           for f in vnclass.findall("./FRAMES/FRAME")
                           if f.find("DESCRIPTION") is not None)
            members = [m.get("name") for m in vnclass.findall("./MEMBERS/MEMBER")]
            if not members and vnclass is root:
                members = [m.get("name") for m in root.findall("./MEMBERS/MEMBER")]
            for name in members:
                if not name:
                    continue
                lem = name.replace("_", " ").lower()
                e = idx.setdefault(lem, {"classes": set(), "themroles": set(),
                                         "patterns": Counter()})
                e["classes"].add(cid)
                e["themroles"] |= roles
                e["patterns"] += pats
    return idx


@lru_cache(maxsize=1)
def propbank_index() -> dict:
    """lemma -> [ {roleset, name, args:{n:descr}, argmax} ]"""
    idx: dict = {}
    for path in glob.glob(os.path.join(PB_DIR, "*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for pred in root.findall(".//predicate"):
            lem = (pred.get("lemma") or "").replace("_", " ").lower()
            for rs in pred.findall("./roleset"):
                args = {r.get("n"): r.get("descr")
                        for r in rs.findall("./roles/role") if r.get("n") not in (None, "m")}
                nums = [int(n) for n in args if n and n.isdigit()]
                idx.setdefault(lem, []).append({
                    "roleset": rs.get("id"), "name": rs.get("name"),
                    "args": args, "argmax": max(nums) if nums else -1})
    return idx


def frame_of(lemma: str) -> dict:
    lem = lemma.lower()
    vn = verbnet_index().get(lem, {})
    pb = propbank_index().get(lem, [])
    licensed = set(vn.get("patterns", {}).keys())
    # PropBank arity -> minimal licensed pattern
    for rs in pb:
        a = rs["argmax"]
        if a >= 0:
            licensed.add("SV")
        if a >= 1:
            licensed.add("SVO")
        if a >= 3:
            licensed.add("SVOO")
    if lem in COPULAR:
        licensed |= set(COPULAR[lem])
    return {
        "lemma": lem,
        "vn_classes": sorted(vn.get("classes", [])),
        "themroles": sorted(vn.get("themroles", [])),
        "vn_patterns": dict(vn.get("patterns", {})),
        "pb_rolesets": [rs["roleset"] for rs in pb],
        "pb_argmax": max((rs["argmax"] for rs in pb), default=-1),
        "licensed_patterns": sorted(licensed) or ["SVO"],
        "known": bool(vn or pb),
    }


# ── copular / linking verbs — VerbNet & PropBank don't tag these as SVC ────
COPULAR = {
    "be": ["SVC", "SVA"], "seem": ["SVC"], "become": ["SVC"], "appear": ["SVC"],
    "remain": ["SVC"], "stay": ["SVC"], "prove": ["SVC"], "keep": ["SVC"],
    "feel": ["SVC"], "look": ["SVC"], "sound": ["SVC"], "taste": ["SVC"],
    "smell": ["SVC"], "grow": ["SVC"], "turn": ["SVC"], "get": ["SVC"],
}


def _syntax_to_map(frame):
    """One VerbNet <FRAME> -> (sail, {themrole: slot_role})."""
    d = frame.find("DESCRIPTION")
    sail = primary_to_pattern(d.get("primary", "")) if d is not None else "SVO"
    syn = frame.find("SYNTAX")
    if syn is None:
        return sail, {}
    seen_verb = False
    last_prep = None
    post_nps = []
    mp = {}
    for ch in syn:
        if ch.tag == "VERB":
            seen_verb = True; last_prep = None; continue
        if ch.tag == "PREP":
            last_prep = (ch.get("value") or "").lower(); continue
        val = ch.get("value")
        if ch.tag == "NP" and not seen_verb:
            if val:
                mp[val] = "S"
        elif ch.tag == "NP" and seen_verb:
            post_nps.append((val, last_prep)); last_prep = None
        elif ch.tag in ("ADJ", "ADJP") and seen_verb and val:
            mp[val] = "C"
    bare = [tr for tr, pr in post_nps if not pr]
    prepped = [(tr, pr) for tr, pr in post_nps if pr]
    if len(bare) == 2:
        mp[bare[0]] = "O_i"; mp[bare[1]] = "O_d"
    elif len(bare) == 1:
        mp[bare[0]] = "O_d"
    for tr, pr in prepped:
        if tr:
            mp[tr] = "O_i" if pr in ("to", "for") else "A"
    return sail, mp


# hand map for the copular sails (VerbNet gives no SVC frame for "be")
_COP_MAP = {"SVC": {"Theme": "S", "Attribute": "C"},
            "SVA": {"Theme": "S", "Location": "A"}}


@lru_cache(maxsize=1)
def _all_slot_maps() -> dict:
    """ONE pass over VerbNet -> {lemma: {sail: {themrole: slot_role}}}."""
    idx: dict = {}
    for path in glob.glob(os.path.join(VN_DIR, "*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for vnclass in [root] + root.findall(".//VNSUBCLASS"):
            members = [m.get("name", "").replace("_", " ").lower()
                       for m in vnclass.findall("./MEMBERS/MEMBER")]
            if not members and vnclass is root:
                members = [m.get("name", "").replace("_", " ").lower()
                           for m in root.findall("./MEMBERS/MEMBER")]
            frames_src = vnclass.findall("./FRAMES/FRAME") or root.findall("./FRAMES/FRAME")
            pairs = [_syntax_to_map(fr) for fr in frames_src]
            for lem in members:
                if not lem:
                    continue
                e = idx.setdefault(lem, {})
                for sail, mp in pairs:
                    if mp:
                        e.setdefault(sail, {}).update(mp)
    return idx


def slot_maps(lemma: str) -> dict:
    lem = lemma.lower()
    out = dict(_all_slot_maps().get(lem, {}))
    if lem in COPULAR:
        for sail in COPULAR[lem]:
            out.setdefault(sail, {}).update(_COP_MAP.get(sail, {}))
    return {k: v for k, v in out.items() if v}


if __name__ == "__main__":
    import json
    vi, pi = verbnet_index(), propbank_index()
    print(f"VerbNet: {len(vi)} lemmas   PropBank: {len(pi)} lemmas")
    for w in ("give", "run", "put", "be", "elect", "nominate", "sleep", "seem"):
        print(json.dumps(frame_of(w), default=list))
