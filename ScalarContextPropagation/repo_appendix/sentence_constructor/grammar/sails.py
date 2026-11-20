"""
sails.py — the generative grammar core: typed slot templates, speech acts,
register bands.  Hand-authored (small closed sets); the rest of
monad_sentences.bin is derived.  Each SAIL is one flight-path of the box-kite
ring around e0 (the finite verb, the anchor that does no work).
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SlotSpec:
    role: str            # S P O_d O_i C A
    deprel: str          # UD relation on the edge
    themrole: str        # default VerbNet thematic role for the filler
    head: bool = False   # the finite verb itself


# canonical English order is the list order
SAILS: dict[str, list[SlotSpec]] = {
    "SV":   [SlotSpec("S", "nsubj", "Agent"), SlotSpec("P", "root", "-", True)],
    "SVO":  [SlotSpec("S", "nsubj", "Agent"), SlotSpec("P", "root", "-", True),
             SlotSpec("O_d", "obj", "Theme")],
    "SVC":  [SlotSpec("S", "nsubj", "Theme"), SlotSpec("P", "cop", "-", True),
             SlotSpec("C", "root", "Attribute")],
    "SVA":  [SlotSpec("S", "nsubj", "Theme"), SlotSpec("P", "root", "-", True),
             SlotSpec("A", "obl", "Location")],
    "SVOO": [SlotSpec("S", "nsubj", "Agent"), SlotSpec("P", "root", "-", True),
             SlotSpec("O_i", "iobj", "Recipient"), SlotSpec("O_d", "obj", "Theme")],
    "SVOC": [SlotSpec("S", "nsubj", "Agent"), SlotSpec("P", "root", "-", True),
             SlotSpec("O_d", "obj", "Theme"), SlotSpec("C", "xcomp", "Attribute")],
    "SVOA": [SlotSpec("S", "nsubj", "Agent"), SlotSpec("P", "root", "-", True),
             SlotSpec("O_d", "obj", "Theme"), SlotSpec("A", "obl", "Location")],
}

RHYTHM_AFFINITY = {                       # sail -> {contour: weight}
    "SV": {"loose": .8, "periodic": .2}, "SVO": {"loose": .7, "periodic": .3},
    "SVC": {"loose": .9, "periodic": .1}, "SVA": {"loose": .6, "periodic": .4},
    "SVOO": {"loose": .5, "periodic": .5}, "SVOC": {"loose": .4, "cumulative": .6},
    "SVOA": {"loose": .5, "periodic": .5},
}

# speech act -> (sail, focus role, extra)
SPEECH_ACTS: dict[str, dict] = {
    "what_does_X_do": {"sail": "SVO", "focus": "P", "subject": "X"},
    "who_Xs":         {"sail": "SVO", "focus": "S"},
    "how":            {"sail": "SVA", "focus": "A"},
    "why":            {"sail": "SVO", "focus": "reason", "advcl": "because"},
    "where":          {"sail": "SVA", "focus": "A"},
    "define_X":       {"sail": "SVC", "focus": "C", "subject": "X"},
    "yesno":          {"sail": "SVC", "focus": "polarity"},
}

# |gamma| band -> register.  gamma is context_hash_v2's dissertational<->narrative
# scale (tanh-folded ratio vs the "everything fires once" anchor).
REGISTER_BANDS = [
    ("narrative", 0.00, 0.33),
    ("surface",   0.33, 0.55),
    ("technical", 0.55, 0.78),
    ("thesis",    0.78, 1.01),
]
BAND_INDEX = {name: i for i, (name, _, _) in enumerate(REGISTER_BANDS)}


def band_of(gamma_mag: float) -> str:
    for name, lo, hi in REGISTER_BANDS:
        if lo <= gamma_mag < hi:
            return name
    return "thesis"


def needs_gloss(filler_band: str, audience_band: str) -> bool:
    """A filler above the listener's halocline -> inject a definition."""
    return BAND_INDEX[filler_band] > BAND_INDEX[audience_band]
