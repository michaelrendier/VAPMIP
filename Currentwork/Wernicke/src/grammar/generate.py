"""
generate.py — the sentence CREATOR: the opposite side of the Zork parser.

The parser turns a command into structure; this turns structure into a
sentence.  Five phases (build order):

  1. parse loads context      (input side, existing — here: a light ParseSpec)
  2. structure phase   REAL   speech-act -> sail -> a Ring skeleton of Slots,
                              weave + rhythm + definition-points, all word-free
  3. fill phase        STUB   each Slot gets a placeholder Leaf from a tiny
                              themrole lexicon (the prime-hash resonance pick
                              replaces this later)
  4. linearize         REAL   Ring tree -> word order + rhythm contour
  5. check             REAL   shadow_from_ring -> frames: is the flown sail
                              licensed by the chosen verb?  (the halocline probe)

Everything is a dataclass tree — the lisp-ish s-expression the design calls for.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

import json as _json
import os as _os
from .sails import (SAILS, SPEECH_ACTS, RHYTHM_AFFINITY, band_of, needs_gloss,
                    SlotSpec)
from .frames import frame_of, slot_maps
from . import sem_hash
from .shadow import Shadow, check as shadow_check

_SCHEMA_PATH = _os.path.join(_os.path.dirname(__file__), "..", "..", "monad_sentences.json")
try:
    SCHEMA = _json.load(open(_SCHEMA_PATH))
except Exception:                                     # noqa: BLE001
    SCHEMA = {"verbs": {}, "sails": {}, "speech_acts": SPEECH_ACTS}
if SCHEMA.get("ancestor_primes"):
    sem_hash.load_prime_table(SCHEMA["ancestor_primes"])


def _verb(lem):
    return SCHEMA.get("verbs", {}).get(lem.lower()) or {
        "sails": frame_of(lem)["licensed_patterns"], "maps": slot_maps(lem),
        "context_hash": None}


_FOCUS_FALLBACK = {"P": ["SV", "SVA", "SVO"], "S": ["SVO", "SV", "SVC"],
                   "A": ["SVA", "SVOA", "SV"], "C": ["SVC", "SVA"],
                   "O_d": ["SVO", "SVOO", "SVOA"], "reason": ["SVO", "SV"],
                   "polarity": ["SVC", "SVO"]}


def choose_sail(spec_verb, want_sail, focus):
    """intersect the speech-act sail with the verb's licensed sails.
    Known limitation: VerbNet frames are aggregated across ALL senses of a
    lemma, so an intransitive verb can inherit a rare transitive sense's sail
    (e.g. "converge" ~ optics "converge the beams" licensing SVO) — this
    needs per-sense disambiguation to close, not a blanket rule."""
    licensed = set(_verb(spec_verb)["sails"])
    if want_sail in licensed:
        return want_sail
    for cand in _FOCUS_FALLBACK.get(focus, []) + sorted(licensed):
        if cand in licensed:
            return cand
    return next(iter(licensed), "SV")


# ── the tree ───────────────────────────────────────────────────────────────
@dataclass
class Leaf:
    lemma: str
    synset: Optional[str] = None
    gamma: float = 0.4                     # |gamma| — register scale (stub)

    def words(self) -> List[str]:
        return [self.lemma]


@dataclass
class Gloss:
    of: str
    text: str

    def words(self) -> List[str]:
        return [",", self.text, ","]


@dataclass
class Ring:                                 # a clause (or, recursively, an NP)
    anchor: str                            # e0 — the finite verb / head noun
    sail: str
    slots: List["Slot"] = field(default_factory=list)
    code: int = 0                          # box-kite context hash (stub 0)

    def slot(self, role: str) -> Optional["Slot"]:
        return next((s for s in self.slots if s.spec.role == role), None)


@dataclass
class Slot:
    spec: SlotSpec
    filler: object = None                  # Ring | Leaf | None
    gloss: Optional[Gloss] = None


@dataclass
class Sentence:
    main: Ring
    weave: str = "simple"
    rhythm: str = "loose"
    subs: List[Ring] = field(default_factory=list)


# ── phase 1: a light parse spec (the real ParseResult plugs in here) ───────
@dataclass
class ParseSpec:
    speech_act: str
    verb: str
    subject_hint: Optional[str] = None
    focus_hint: Optional[str] = None
    topic_gamma: float = 0.4
    topic_lemmas: List[str] = field(default_factory=list)   # prompt content words


# ── phase 2: structure (word-free) ───────────────────────────────────────
_TECHNICAL = {"integrate", "differentiate", "diagonalize", "factor", "converge",
              "quantize", "regularize", "decompose"}
_GLOSS = {"integrate": "add up the pieces", "diagonalize": "line up the axes",
          "factor": "break into building blocks", "converge": "settle to a value",
          "regularize": "tame an infinity", "decompose": "split into parts"}


def structure_phase(spec: ParseSpec, depth: str = "surface") -> Sentence:
    act = SCHEMA.get("speech_acts", SPEECH_ACTS)[spec.speech_act]
    sail = choose_sail(spec.verb, act["sail"], act.get("focus", "P"))
    themmap = _verb(spec.verb).get("maps", {}).get(sail, {})
    role_theme = {v: k for k, v in themmap.items()}       # slot_role -> themrole
    slots = []
    for ss in SAILS[sail]:
        tr = role_theme.get(ss.role, ss.themrole)
        slots.append(Slot(spec=SlotSpec(ss.role, ss.deprel, tr, ss.head)))
    ring = Ring(anchor=spec.verb, sail=sail, slots=slots)
    # weave from depth
    weave = {"narrative": "simple", "surface": "simple",
             "technical": "complex", "thesis": "complex"}[depth]
    # rhythm: draw the highest-weight contour the sail affords
    rhythm = max(RHYTHM_AFFINITY[sail], key=RHYTHM_AFFINITY[sail].get)
    if depth in ("technical", "thesis") and "cumulative" in RHYTHM_AFFINITY[sail]:
        rhythm = "cumulative"
    # definition-point: verb above the listener's halocline -> schedule a gloss
    vh = (_verb(spec.verb).get("context_hash") or {})
    verb_band = vh.get("band", "technical" if spec.verb in _TECHNICAL else "surface")
    if needs_gloss(verb_band, depth) and spec.verb in _GLOSS:
        p = ring.slot("P")
        if p:
            p.gloss = Gloss(of=spec.verb, text=f"that is, {_GLOSS[spec.verb]}")
    return Sentence(main=ring, weave=weave, rhythm=rhythm)


# ── phase 3: fill (STUB — placeholder lexicon per thematic role) ─────────
_ROLE_NP = {
    "Agent": Leaf("the method", gamma=0.45), "Theme": Leaf("the result", gamma=0.4),
    "Recipient": Leaf("the reader", gamma=0.3), "Attribute": Leaf("clear", gamma=0.35),
    "Location": Leaf("in the model", gamma=0.5),
    "Destination": Leaf("into the model", gamma=0.5), "Goal": Leaf("to the limit", gamma=0.5),
    "Source": Leaf("from the data", gamma=0.5), "Pivot": Leaf("the case", gamma=0.3),
    "Patient": Leaf("the object", gamma=0.4), "Asset": Leaf("the value", gamma=0.4),
    "Beneficiary": Leaf("the reader", gamma=0.3), "-": None,
}


def _pf_distinct(g: int) -> int:
    n, k, d = g, 0, 2
    while d * d <= n:
        if n % d == 0:
            k += 1
            while n % d == 0:
                n //= d
        d += 1
    return k + (1 if n > 1 else 0)


def _resonance(a: int, b: int) -> int:
    from math import gcd
    g = gcd(a, b)
    return 0 if g <= 1 else _pf_distinct(g)


_FILLERS = SCHEMA.get("fillers", {})
_ROLE_CODES = {k: int(v) for k, v in SCHEMA.get("role_codes", {}).items()}


def _band_ok(cand_band: str, want: str) -> bool:
    order = ["narrative", "surface", "technical", "thesis"]
    return abs(order.index(cand_band) - order.index(want)) <= 1


def _rank(candidates, pos: str, depth: str, target: int):
    """RANK only — resonance against target, count as the tie-break. Shared
    by both passes of _resonant_pick below."""
    best, best_score, best_cnt = None, 0, -1
    for lem, e in candidates:
        if e["pos"] != pos or not _band_ok(e["band"], depth):
            continue
        sc = _resonance(int(e["sem_code"]), target)
        if sc > best_score or (sc == best_score and sc > 0 and e["count"] > best_cnt):
            best, best_score, best_cnt = lem, sc, e["count"]
    return best, best_score


def _resonant_pick(themrole: str, pos: str, depth: str, topic_code: int,
                   restrs=(), topic_is_maths: bool = False):
    """two stages: GATE (invariant match, free — short-circuits) then
    RANK (resonance, work — only on survivors).

    topic_is_maths (sem_hash.is_maths_eligible on the spec's topic — a
    sparse, structural, WordNet-anchored test, never the maths corpus
    itself) makes the source="maths" fillers the PRIMARY lexicon: ranked
    FIRST, and used outright if any of them resonates at all. The full
    pool (source="maths" and "corpus" together) is the fallback — tried
    only when the primary lexicon has nothing that fits this slot, so a
    gated-in topic never comes up empty just because its own vocabulary
    happened to have no match for THIS particular themrole."""
    pool = list(_FILLERS.items())
    if restrs:
        pool = [(lem, e) for lem, e in pool
               if sem_hash.gate_pass(int(e["sem_code"]), restrs)]
        if not pool:                              # the gate itself says "no"
            return None                           # -> no ranking work needed
    role_c = _ROLE_CODES.get(themrole, 1)
    target = role_c * topic_code if topic_code > 1 else role_c

    if topic_is_maths:
        primary = [(lem, e) for lem, e in pool if e.get("source") == "maths"]
        best, best_score = _rank(primary, pos, depth, target)
        if best is not None and best_score > 0:
            return Leaf(best, synset=_FILLERS[best]["sense"],
                       gamma=abs(_FILLERS[best]["gamma_radial"]))
        # the primary lexicon has nothing for this slot -> fall through

    best, best_score = _rank(pool, pos, depth, target)
    if best is None or best_score == 0:          # no real resonance -> let the stub answer
        return None
    return Leaf(best, synset=_FILLERS[best]["sense"],
                gamma=abs(_FILLERS[best]["gamma_radial"]))


def fill_phase(sent: Sentence, spec: ParseSpec, depth: str = "surface") -> Sentence:
    topic_code = 1
    for lem in spec.topic_lemmas:
        e = _FILLERS.get(lem.lower())
        if e:
            topic_code *= int(e["sem_code"])
    # eligibility, computed once per sentence off the actual topic — never
    # off a candidate word, never off the granular corpus itself (see
    # sem_hash.is_maths_eligible's module note: that corpus is a flat
    # scrape, not a gate source).
    topic_is_maths = any(sem_hash.is_maths_eligible(w) for w in spec.topic_lemmas)
    for slot in sent.main.slots:
        if slot.spec.head:
            continue
        if slot.spec.role == "S" and spec.subject_hint:
            slot.filler = Leaf(spec.subject_hint, gamma=spec.topic_gamma)
            continue
        pos = "a" if slot.spec.role == "C" else "n"
        restrs = _verb(spec.verb).get("selrestrs", {}).get(slot.spec.themrole, [])
        pick = _resonant_pick(slot.spec.themrole, pos, depth, topic_code, restrs,
                              topic_is_maths)
        if pick is None:
            proto = _ROLE_NP.get(slot.spec.themrole)
            pick = Leaf(proto.lemma, gamma=proto.gamma) if proto else Leaf("it")
        slot.filler = pick
    return sent


# ── phase 4: linearize ─────────────────────────────────────────────────
_COP = {"SVC": "is"}


def _np_words(f) -> List[str]:
    if f is None:
        return []
    if isinstance(f, Ring):
        out = []
        for s in f.slots:
            out += _np_words(s.filler)
        return out
    return f.words()


_A_PREP = {"Destination": "into", "Source": "from", "Goal": "to",
          "Recipient": "to", "Beneficiary": "for", "Location": "in"}
_VERB_PREP = {"belong": "to", "consist": "of", "result": "from",
             "occur": "in", "apply": "in", "relate": "to"}


_THIRD_PERSON_IRREGULAR = {"be": "is", "have": "has", "do": "does", "go": "goes"}
_SIBILANT_END = ("s", "ss", "sh", "ch", "x", "z", "o")


def _third_person(verb: str) -> str:
    """Third-person-singular present, English orthography rules — not just
    a bare '+s': applY -> applies (consonant+y), pasS/watcH/fiX/buzZ/echO ->
    +es (sibilant/o), the four irregulars, else +s."""
    irr = _THIRD_PERSON_IRREGULAR.get(verb)
    if irr:
        return irr
    if verb.endswith("y") and len(verb) > 1 and verb[-2] not in "aeiou":
        return verb[:-1] + "ies"
    if verb.endswith(_SIBILANT_END):
        return verb + "es"
    return verb + "s"


def linearize(sent: Sentence) -> str:
    r = sent.main
    out: List[str] = []
    for slot in r.slots:
        if slot.spec.head:
            if r.sail == "SVC":
                out.append(_COP["SVC"])
            else:
                out.append(_third_person(r.anchor))
            if slot.gloss:
                out += slot.gloss.words()
        else:
            if slot.spec.role == "A" and slot.filler is not None:
                prep = _VERB_PREP.get(r.anchor) or _A_PREP.get(slot.spec.themrole, "in")
                out.append(prep)
            out += _np_words(slot.filler)
    s = " ".join(w for w in out if w).strip()
    s = s.replace(" ,", ",").replace(",,", ",").rstrip(", ")
    return s[0].upper() + s[1:] + "."


# ── phase 5: check (the halocline probe) ───────────────────────────────
def shadow_from_ring(r: Ring) -> Shadow:
    lemma = "be" if r.sail == "SVC" else r.anchor
    ring_edges = {s.spec.deprel: (s.filler.lemma if isinstance(s.filler, Leaf)
                                  else "…") for s in r.slots if not s.spec.head}
    spoca = {}
    for s in r.slots:
        if s.spec.head:
            continue
        slot = ("O_d" if s.spec.role == "O_d" else "O_i" if s.spec.role == "O_i"
                else s.spec.role)
        spoca.setdefault(slot, []).append(
            s.filler.lemma if isinstance(s.filler, Leaf) else "…")
    return Shadow(text="", verb=r.anchor, verb_lemma=lemma, verb_upos="VERB",
                  pos=[], ring=ring_edges, spoca=spoca, pattern=r.sail)


def check(sent: Sentence) -> dict:
    return shadow_check(shadow_from_ring(sent.main))


# ── the pipeline ──────────────────────────────────────────────────────
def build_response(spec: ParseSpec, depth: str = "surface") -> dict:
    sent = structure_phase(spec, depth)          # 2
    sent = fill_phase(sent, spec, depth)         # 3
    surface = linearize(sent)                    # 4
    verdict = check(sent)                        # 5
    return {"depth": depth, "sail": sent.main.sail, "weave": sent.weave,
            "rhythm": sent.rhythm, "surface": surface,
            "verdict": verdict["verdict"], "licensed": verdict["licensed"],
            "residue": verdict["residue"]}


if __name__ == "__main__":
    import json
    cases = [
        (ParseSpec("what_does_X_do", "converge", subject_hint="the series",
                   topic_lemmas=["series", "limit", "sum", "value"]), ("narrative", "thesis")),
        (ParseSpec("define_X", "be", subject_hint="an integral",
                   topic_lemmas=["integral", "area", "sum"]), ("surface", "thesis")),
        (ParseSpec("who_Xs", "give", topic_lemmas=["book", "reader", "gift"]), ("surface",)),
        (ParseSpec("how", "run", subject_hint="the engine",
                   topic_lemmas=["engine", "machine", "system"]), ("surface",)),
        (ParseSpec("what_does_X_do", "elect", subject_hint="the board",
                   topic_lemmas=["board", "chair", "member"]), ("surface",)),
    ]
    for spec, depths in cases:
        print(f"\n{spec.speech_act}  verb={spec.verb}")
        for d in depths:
            r = build_response(spec, d)
            print(f"  [{d:9}] {r['surface']}")
            print(f"              sail={r['sail']} weave={r['weave']} rhythm={r['rhythm']} "
                  f"-> {r['verdict']}"
                  + (f"  residue={r['residue']} licensed={r['licensed']}" if r['residue'] else ""))
