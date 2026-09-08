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

from .sails import (SAILS, SPEECH_ACTS, RHYTHM_AFFINITY, band_of, needs_gloss,
                    SlotSpec)
from .frames import frame_of
from .shadow import Shadow, check as shadow_check


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
    speech_act: str                       # key of SPEECH_ACTS
    verb: str                             # the answer's finite verb
    subject_hint: Optional[str] = None    # the X in "what does X do"
    focus_hint: Optional[str] = None
    topic_gamma: float = 0.4              # |gamma| of the prompt's own vocab


# ── phase 2: structure (word-free) ───────────────────────────────────────
_TECHNICAL = {"integrate", "differentiate", "diagonalize", "factor", "converge",
              "quantize", "regularize", "decompose"}
_GLOSS = {"integrate": "add up the pieces", "diagonalize": "line up the axes",
          "factor": "break into building blocks", "converge": "settle to a value",
          "regularize": "tame an infinity", "decompose": "split into parts"}


def structure_phase(spec: ParseSpec, depth: str = "surface") -> Sentence:
    act = SPEECH_ACTS[spec.speech_act]
    sail = act["sail"]
    ring = Ring(anchor=spec.verb, sail=sail,
                slots=[Slot(spec=ss) for ss in SAILS[sail]])
    # weave from depth
    weave = {"narrative": "simple", "surface": "simple",
             "technical": "complex", "thesis": "complex"}[depth]
    # rhythm: draw the highest-weight contour the sail affords
    rhythm = max(RHYTHM_AFFINITY[sail], key=RHYTHM_AFFINITY[sail].get)
    if depth in ("technical", "thesis") and "cumulative" in RHYTHM_AFFINITY[sail]:
        rhythm = "cumulative"
    # definition-point: verb above the listener's halocline -> schedule a gloss
    if spec.verb in _TECHNICAL and needs_gloss("technical", depth):
        p = ring.slot("P")
        if p and spec.verb in _GLOSS:
            p.gloss = Gloss(of=spec.verb, text=f"that is, {_GLOSS[spec.verb]}")
    return Sentence(main=ring, weave=weave, rhythm=rhythm)


# ── phase 3: fill (STUB — placeholder lexicon per thematic role) ─────────
_ROLE_NP = {
    "Agent": Leaf("the method", gamma=0.45), "Theme": Leaf("the result", gamma=0.4),
    "Recipient": Leaf("the reader", gamma=0.3), "Attribute": Leaf("clear", gamma=0.35),
    "Location": Leaf("in the model", gamma=0.5), "-": None,
}


def fill_phase(sent: Sentence, spec: ParseSpec) -> Sentence:
    for slot in sent.main.slots:
        if slot.spec.head:
            continue
        if slot.spec.role == "S" and spec.subject_hint:
            slot.filler = Leaf(spec.subject_hint, gamma=spec.topic_gamma)
        elif slot.spec.role == "C" and sent.main.sail == "SVC":
            slot.filler = _ROLE_NP.get(slot.spec.themrole) or Leaf("defined")
        else:
            proto = _ROLE_NP.get(slot.spec.themrole)
            slot.filler = Leaf(proto.lemma, gamma=proto.gamma) if proto else Leaf("it")
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


def linearize(sent: Sentence) -> str:
    r = sent.main
    out: List[str] = []
    for slot in r.slots:
        if slot.spec.head:
            if r.sail == "SVC":
                out.append(_COP["SVC"])
            else:
                out.append(r.anchor + ("s" if not r.anchor.endswith("s") else ""))
            if slot.gloss:
                out += slot.gloss.words()
        else:
            out += _np_words(slot.filler)
    s = " ".join(w for w in out if w).strip()
    s = s.replace(" ,", ",")
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
    sent = fill_phase(sent, spec)                # 3 (stub)
    surface = linearize(sent)                    # 4
    verdict = check(sent)                        # 5
    return {"depth": depth, "sail": sent.main.sail, "weave": sent.weave,
            "rhythm": sent.rhythm, "surface": surface,
            "verdict": verdict["verdict"], "licensed": verdict["licensed"],
            "residue": verdict["residue"]}


if __name__ == "__main__":
    import json
    cases = [
        (ParseSpec("what_does_X_do", "converge", subject_hint="the series"), ("narrative", "thesis")),
        (ParseSpec("what_does_X_do", "integrate", subject_hint="the engine"), ("surface", "thesis")),
        (ParseSpec("define_X", "be", subject_hint="an integral"), ("surface",)),
        (ParseSpec("how", "run"), ("surface",)),
        (ParseSpec("who_Xs", "give"), ("surface",)),
        (ParseSpec("what_does_X_do", "elect", subject_hint="the board"), ("surface",)),
    ]
    for spec, depths in cases:
        print(f"\n{spec.speech_act}  verb={spec.verb}")
        for d in depths:
            r = build_response(spec, d)
            print(f"  [{d:9}] {r['surface']}")
            print(f"              sail={r['sail']} weave={r['weave']} rhythm={r['rhythm']} "
                  f"-> {r['verdict']}"
                  + (f"  residue={r['residue']} licensed={r['licensed']}" if r['residue'] else ""))
