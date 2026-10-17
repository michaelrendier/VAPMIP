"""
rotary_bridge.py — test the sentence creator against RotaryBoxKiteMonad

rotary_rerun_boxkite_monad.py's `assemble_sentence(direction, words_out)` is
the same placeholder as ptol.c's console_speak word-bag: it fills one of 11
canned templates ("it is part of {0}.") with whatever WordNet-ranked word
came out, with no grammar check — "adjoin" (a verb) can land in a noun slot
and it will say "it is part of adjoin."

This does NOT edit that file (real, tested, `7:7:7` — modify-don't-rewrite).
It monkeypatches the module-level `assemble_sentence` name for the duration
of a test call, so `RotaryBoxKiteMonad.process_input()` runs unchanged except
for that one function, and everything else (MindsEye/PapersHands, the
strut-overlap measurement, the Encounter record) stays the real pipeline.
"""
from __future__ import annotations
from typing import Any, List, Optional

from .generate import ParseSpec, build_response
from .sails import band_of

# direction (from ptolemy_monad.infer_direction) -> (speech_act, verb)
DIRECTION_MAP = {
    "decompose":     ("what_does_X_do", "comprise"),
    "situate":       ("how",            "belong"),
    "characterize":  ("define_X",       "be"),
    "explain":       ("why",            "result"),
    "imply":         ("what_does_X_do", "lead"),
    "associate":     ("what_does_X_do", "relate"),
    "compare":       ("what_does_X_do", "resemble"),
    "contextualize": ("where",          "belong"),
    "localize":      ("where",          "occur"),
    "register":      ("how",            "apply"),
    "observe":       ("define_X",       "be"),
}


def _depth_from_words(words: List[str]) -> str:
    """Prefer the schema's precomputed filler bands (no WordNet at request
    time); fall back to a fresh context_hash_v2 read if a word is unlisted."""
    from .generate import _FILLERS
    bands, order = [], ["narrative", "surface", "technical", "thesis"]
    for w in words[:6]:
        e = _FILLERS.get(w.lower().replace(" ", "_"))
        if e:
            bands.append(order.index(e["band"]))
    if not bands:
        return "surface"
    return order[round(sum(bands) / len(bands))]


def assemble_sentence_v2(direction: str, words_out: List[str],
                         subject: Optional[str] = None) -> str:
    """Drop-in replacement for rotary_rerun_boxkite_monad.assemble_sentence.
    Same signature, so the monkeypatch in run_encounter() needs no other
    change to process_input()."""
    if not words_out:
        return "(no candidates found)"
    act, verb = DIRECTION_MAP.get(direction, ("define_X", "be"))
    depth = _depth_from_words(words_out)
    topic = [w.replace(" ", "_") for w in words_out]
    spec = ParseSpec(speech_act=act, verb=verb, subject_hint=subject or "it",
                     topic_lemmas=topic, topic_gamma=0.3)
    r = build_response(spec, depth)
    if r["verdict"] != "prime":                    # the halocline probe failed
        from rotary_rerun_boxkite_monad import assemble_sentence as _old
        return _old(direction, words_out) + f"  [creator: {r['verdict']}/{r['residue']}, fell back]"
    return r["surface"] + f"  [{act}/{r['sail']}/{depth}]"


def install() -> bool:
    """Permanently swap in the real creator for a LONG-LIVED process — the
    Chat tab's BoxKiteMonad._load() in ptolemy_console.py, which builds one
    RotaryBoxKiteMonad and keeps it resident for the whole session. Unlike
    run_encounter()'s try/finally (built for A/B comparison, restores the
    template afterward), this does not restore: the creator becomes the
    module's assemble_sentence for the rest of the process. Idempotent —
    safe to call every time the Chat tab boots. Returns True once the
    creator is confirmed installed, so the caller can report it truthfully
    instead of assuming."""
    import sys
    for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
        sys.modules.setdefault(m, None)
    import rotary_rerun_boxkite_monad as rb

    if getattr(rb.assemble_sentence, "_is_creator", False):
        return True                                     # already installed
    assemble_sentence_v2._is_creator = True               # type: ignore[attr-defined]
    rb.assemble_sentence = assemble_sentence_v2
    return rb.assemble_sentence is assemble_sentence_v2


def run_encounter(text: str, use_creator: bool = True):
    """Run RotaryBoxKiteMonad.process_input(text), optionally through the
    real sentence creator instead of the template assembler.  Returns
    (Encounter, old_response) so the two can be compared side by side."""
    import sys
    for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
        sys.modules.setdefault(m, None)
    import rotary_rerun_boxkite_monad as rb

    old_fn = rb.assemble_sentence
    old_response = None
    try:
        # always compute the OLD template response first, for comparison
        m0 = rb.RotaryBoxKiteMonad()
        enc0 = m0.process_input(text)
        old_response = enc0.response
        if use_creator:
            rb.assemble_sentence = assemble_sentence_v2
            m1 = rb.RotaryBoxKiteMonad()
            enc = m1.process_input(text)
        else:
            enc = enc0
    finally:
        rb.assemble_sentence = old_fn
    return enc, old_response


if __name__ == "__main__":
    texts = [
        "The integral converges to a finite limit as the series decreases.",
        "The board elected a new chair to lead the committee.",
        "Water flows downhill because gravity pulls it toward the lowest point.",
        "The engine converts fuel into motion through controlled combustion.",
    ]
    for t in texts:
        enc, old = run_encounter(t)
        print(f"\nTEXT: {t}")
        print(f"  direction   : {enc.direction}   words_out: {enc.words_out}")
        print(f"  OLD (template): {old}")
        print(f"  NEW (creator) : {enc.response}")
        print(f"  struts in/out/shared: {enc.lit_struts_in}/{enc.lit_struts_out}/{enc.shared_struts}"
              f"  ({len(enc.shared_struts)}/{len(enc.lit_struts_in) or 1})")
