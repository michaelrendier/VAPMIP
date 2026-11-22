"""
ptolc_bridge.py — the sentence creator, called from ptol.c's console_speak().

console_speak() already computes everything a ParseSpec needs except the
speech act (a small wh-word scan, done in C — see infer_speech_act() in
ptol.c): the firing word bag (WORDS), the halocline depth via Γ (GAMMA).
This is the other half of the bridge proposed in the Tuning-the-Engine design
pass — get_monad_words() stays as the guaranteed fallback; this replaces its
output as the DEFAULT voice, not an opt-in mode (2026-09-11).

stdin, three lines:
    GAMMA <float>                Γ ∈ (−1, 1), from measure_gamma()
    ACT   <speech_act>           one of sails.SPEECH_ACTS' 7 keys
    WORDS <lemma> <lemma> ...    the firing word bag, spiral order

stdout, on success (exit 0): ONE line, the surface sentence.
On any failure (bad word list, WordNet/VerbNet unreachable, empty schema):
prints nothing and exits nonzero — console_speak() keeps its own word-bag
`out` untouched, per "work on guarantees": no hard guarantee here, so the
old placeholder is the explicit fallback, never a confident wrong sentence.
"""
from __future__ import annotations
import sys

from .generate import ParseSpec, build_response
from .sails import band_of

# Per-speech-act default verb, used only when NONE of the firing words are a
# known VerbNet lemma — picked from the same verbs used as DIRECTION_MAP's
# defaults in rotary_bridge.py, so the two speaking paths (the C console and
# the Python rotary monad) land on the same voice when they have no better
# steer.
_DEFAULT_VERB = {
    "what_does_X_do": "relate",
    "who_Xs":         "give",
    "how":            "apply",
    "why":            "result",
    "where":          "occur",
    "define_X":       "be",
    "yesno":          "be",
}


def _pick_spec(gamma: float, act: str, words: list[str]) -> tuple[ParseSpec, str]:
    from .generate import SCHEMA
    if act not in SCHEMA.get("speech_acts", {}):
        act = "what_does_X_do"                       # unrecognised -> safest act

    verbs = SCHEMA.get("verbs", {})
    lemmas = [w.lower() for w in words if w]
    verb = next((w for w in lemmas if w in verbs), None)
    topic = [w for w in lemmas if w != verb]
    if verb is None:
        verb = _DEFAULT_VERB.get(act, "be")
        topic = lemmas

    depth = band_of(abs(gamma))
    return ParseSpec(speech_act=act, verb=verb, topic_lemmas=topic), depth


def run(gamma: float, act: str, words: list[str]) -> str | None:
    spec, depth = _pick_spec(gamma, act, words)
    result = build_response(spec, depth)
    text = (result.get("surface") or "").strip()
    return text or None


def main() -> int:
    gamma, act, words = 0.0, "what_does_X_do", []
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line.startswith("GAMMA "):
            try:
                gamma = float(line[6:].strip())
            except ValueError:
                pass
        elif line.startswith("ACT "):
            act = line[4:].strip() or act
        elif line.startswith("WORDS "):
            words = line[6:].split()

    text = run(gamma, act, words)
    if not text:
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                 # noqa: BLE001
        # Any failure (WordNet unreachable offline, a malformed schema, an
        # unknown verb throwing deep in fill/linearize) is a fallback signal,
        # not a crash console_speak() should ever see.
        sys.exit(1)
