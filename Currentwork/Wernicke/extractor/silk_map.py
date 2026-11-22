#!/usr/bin/env python3
"""silk_map.py — the seven deconstruction roles as DATA: the rule base of the content extractor (Wernicke tree).

Deconstruction uses ONLY the seven silk types; the orbweaver web (candidate spreading) is not involved here.
    ANCHOR     piriform           the topic, the given, the anaphor
    SPAN       major ampullate    the load-bearing line, with three independent fields:
                                  relation (an event verb, or NAME for a copula), claim (the complement), frame (the scope)
    SCAFFOLD   minor ampullate    auxiliaries, copulas, modals, tense, voice, expletives
    ELABORATE  flagelliform       attributive modifiers (the extensible slack)
    HOOK       aggregate          names, numbers, examples (specifics)
    WRAP       aciniform          connectives and complementisers
    SHELL      tubuliform         speech act, mood, polarity, interjection, wh-gap

A token gets a SET of (role, field) pairs: a proper-name subject is both ANCHOR and HOOK.  The tables below are the first draft
(2026-10-17); crosswalk_tests.py measures them against UD English-EWT, PropBank, WordNet and VerbNet frames, and the report is
the evidence for changing them.  Nothing here uses WordNet spreading, A-edges or the kite.
"""

ROLES = ("ANCHOR", "SPAN", "SCAFFOLD", "ELABORATE", "HOOK", "WRAP", "SHELL")
SPAN_FIELDS = ("relation", "claim", "frame")

# Universal Dependencies relation -> (role, SPAN field or None).  Subtypes fall back to the base relation (obl:tmod -> obl).
UD_ROLE = {
    "nsubj": ("ANCHOR", None), "nsubj:pass": ("ANCHOR", None), "csubj": ("ANCHOR", None), "csubj:pass": ("ANCHOR", None),
    "det": ("ANCHOR", None), "det:predet": ("ANCHOR", None), "nmod:poss": ("ANCHOR", None),      # givenness markers, possessors
    "expl": ("SCAFFOLD", None), "aux": ("SCAFFOLD", None), "aux:pass": ("SCAFFOLD", None), "cop": ("SCAFFOLD", None),
    "obj": ("SPAN", "claim"), "iobj": ("SPAN", "claim"), "ccomp": ("SPAN", "claim"), "xcomp": ("SPAN", "claim"),
    "obl:agent": ("SPAN", "claim"),
    "obl": ("SPAN", "frame"), "advcl": ("SPAN", "frame"), "case": ("SPAN", "frame"), "obl:tmod": ("SPAN", "frame"),
    "obl:npmod": ("SPAN", "frame"), "nmod:tmod": ("SPAN", "frame"),
    "compound:prt": ("SPAN", "relation"),
    "amod": ("ELABORATE", None), "advmod": ("ELABORATE", None), "advmod:emph": ("ELABORATE", None), "compound": ("ELABORATE", None),
    "appos": ("ELABORATE", None), "acl": ("ELABORATE", None), "acl:relcl": ("ELABORATE", None), "nmod": ("ELABORATE", None),
    "nmod:npmod": ("ELABORATE", None), "nummod": ("ELABORATE", None),
    "mark": ("WRAP", None), "cc": ("WRAP", None), "cc:preconj": ("WRAP", None),
    "discourse": ("SHELL", None), "vocative": ("SHELL", None),
}
# relations that take the role of what they attach to
INHERIT = {"conj", "flat", "flat:name", "flat:foreign", "fixed", "goeswith"}
# relations the seven roles do not cover (reported, not hidden)
UNCOVERED = {"dep", "list", "orphan", "reparandum", "dislocated", "clf", "parataxis"}

NEG_LEMMAS = {"not", "n't", "never", "no", "nor", "neither", "nothing", "nobody", "none", "nowhere", "cannot"}


def ud_base(rel):
    return rel.split(":")[0]


def roles_ud(tok, sent):
    """Role set of one UD token.  tok and sent follow the `conllu` library (id, head, deprel, upos, lemma, feats).
    Returns a set of (role, field) pairs, or {("PUNCT", None)} for punctuation, or {("UNCOVERED", deprel)} if no rule applies."""
    rel, upos = tok["deprel"], tok["upos"]
    if upos == "PUNCT" or rel == "punct":
        return {("PUNCT", None)}
    by_id = {t["id"]: t for t in sent if isinstance(t["id"], int)}
    out = set()
    feats = tok.get("feats") or {}
    lemma = (tok.get("lemma") or tok["form"]).lower()
    if upos in ("PROPN", "NUM", "SYM"):
        out.add(("HOOK", None))
    if upos == "INTJ":
        out.add(("SHELL", None))
    if feats.get("Polarity") == "Neg" or lemma in NEG_LEMMAS:
        out.add(("SHELL", "polarity"))
    if feats.get("PronType") == "Int":
        out.add(("SHELL", "gap"))
    base = ud_base(rel)
    if rel == "root":
        kids = [t for t in sent if t["head"] == tok["id"]]
        if upos in ("VERB", "AUX"):
            out.add(("SPAN", "relation"))
        elif any(k["deprel"] == "cop" for k in kids):
            out.add(("SPAN", "claim"))               # a copular predicate: the claim carries the load
        elif upos in ("NOUN", "PROPN", "PRON"):
            out.add(("ANCHOR", None))                # a noun-phrase fragment
        elif upos in ("ADJ", "ADV", "NUM"):
            out.add(("ELABORATE", None))
        elif upos == "INTJ":
            out.add(("SHELL", None))
        else:
            out.add(("UNCOVERED", "root:" + upos))
        return out
    if rel in UD_ROLE:
        out.add(UD_ROLE[rel])
    elif base in UD_ROLE and base not in INHERIT:
        out.add(UD_ROLE[base])
    elif rel in INHERIT or base in INHERIT:
        head = by_id.get(tok["head"])
        if head is not None and head is not tok:
            inherited = {r for r in roles_ud(head, sent) if r[0] not in ("HOOK",)}
            out |= inherited
    elif rel in UNCOVERED or base in UNCOVERED:
        out.add(("UNCOVERED", rel))
    else:
        out.add(("UNCOVERED", rel))
    if not out:
        out.add(("UNCOVERED", rel))
    return out


# NLTK nps_chat dialogue acts -> SHELL.act (the speech-act inventory the role needs)
NPS_TO_SHELL = {
    "Statement": "statement", "Emotion": "exclaim", "Emphasis": "exclaim", "whQuestion": "whQuestion", "ynQuestion": "ynQuestion",
    "yAnswer": "answer", "nAnswer": "answer", "Greet": "greet", "Bye": "bye", "Accept": "accept", "Reject": "reject",
    "Clarify": "clarify", "Continuer": "continuer", "System": "system", "Other": "other",
}

# PropBank labels -> the role the extractor should assign to the argument's head (the prediction the test checks)
PROPBANK_EXPECT = {
    "ARG0": "ANCHOR", "ARG1": "SPAN.claim", "ARG2": "SPAN.claim", "ARG3": "SPAN.claim", "ARG4": "SPAN.claim", "ARG5": "SPAN.claim",
    "ARGM-LOC": "SPAN.frame", "ARGM-TMP": "SPAN.frame", "ARGM-MNR": "SPAN.frame", "ARGM-CAU": "SPAN.frame", "ARGM-PRP": "SPAN.frame",
    "ARGM-DIR": "SPAN.frame", "ARGM-EXT": "SPAN.frame", "ARGM-PNC": "SPAN.frame", "ARGM-GOL": "SPAN.frame",
    "ARGM-MOD": "SCAFFOLD", "ARGM-NEG": "SHELL", "ARGM-DIS": "WRAP", "ARGM-ADV": "SPAN.frame", "ARGM-PRD": "SPAN.claim",
    "ARGM-LVB": "SPAN.relation", "ARGM-REC": "ANCHOR", "ARGM-COM": "SPAN.frame", "ARGM-ADJ": "SPAN.frame",
}
