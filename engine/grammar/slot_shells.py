"""
slot_shells.py — the sedenion window AS grammar positions.

Cody, 2026-09-11: "lets use the sedenion window as 'slots'. so that it can
assign slots as well when they show up in input or internet traffic...
the slots should be 'grammar positions'."

e0 stays what Ring.anchor's own docstring already calls it: the head/verb,
no edge, the ground stake (box_kite.md: e0 "is not a vertex of any
box-kite"). The other 15 shells split 3-each across the 5 non-head SPOCA
roles sails.py's SlotSpec actually uses (S, O_i, O_d, C, A), in canonical
SPOCA order:

    e1-e3    S       e10-e12  C
    e4-e6    O_i     e13-e15  A
    e7-e9    O_d

Assignment needs no UD parse — it is the same Dirichlet projection
console_speak() already runs per firing word (PtolC/ptol.c's project()),
just read in the other direction: instead of "which word best fits shell
k" (picking a filler, get_monad_words()), "given this word, which shell(s)
does it fire in" (assigning a role). That makes it usable on text a
treebank never saw — a live prompt, or a page pulled by monad_browse /
Callimachus.vocab_update's --url path — closing the gap shadow.reduce()
can't (it needs a real CoNLL-U parse and only ever sees EWT/GUM).
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional

P16 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
PHI = (1.0 + 5.0 ** 0.5) / 2.0

ROLE_SHELLS: Dict[str, tuple] = {
    "S":   (1, 2, 3),
    "O_i": (4, 5, 6),
    "O_d": (7, 8, 9),
    "C":   (10, 11, 12),
    "A":   (13, 14, 15),
}


def project(text: str, k: int, sigma: float = 0.5) -> float:
    """The exact ptol.c project() (PtolC/ptol.c:224), ported faithfully and
    verified byte-for-byte against the real binary's `-r` output (norm-1
    vector; this returns the pre-norm scalar, which is all a per-word
    threshold test needs — dividing every shell by the same positive norm
    never changes which shell is the peak). Dirichlet-weighted inner
    product against prime frequency P16[k]; shells 4-7 and 12-15 are
    J_blue (sin), everything else is J_red (cos) — the same duality as
    measure_sigma()/measure_gamma().

    NOT engines/_sedenion.py's project() — that port always uses cos, no
    j_blue branch; a real discrepancy from the C original, noted here but
    not touched (out of scope for this file)."""
    s = text.encode("utf-8", errors="replace")
    if not s:
        return 0.0
    freq = 2.0 * math.pi / P16[k]
    j_blue = 4 <= k <= 7 or 12 <= k <= 15
    total = 0.0
    for i, byte in enumerate(s, start=1):
        phase = freq * i
        w = math.sin(phase) if j_blue else math.cos(phase)
        total += byte * (i ** -sigma) * w
    return total


def word_shells(word: str, sigma: float = 0.5) -> List[float]:
    """The 16 raw projections for one word, e0..e15."""
    return [project(word, k, sigma) for k in range(16)]


# ── the per-shell baseline — a real control, not a guess ───────────────────
# Measured, 2026-09-11: the RAW per-shell magnitude is dominated by an
# artifact of prime size vs. word length, almost independent of the word
# itself. freq = 2π/P16[k] sets how fast the phase advances per byte; for a
# short word, a SMALL prime (fast phase) drives destructive interference
# across the sum (terms partly cancel, low magnitude), while a LARGE prime
# (slow phase) barely turns over across the same word (terms mostly agree
# in sign, high magnitude) — a property of the SHELL, not of the word's
# grammatical role. Confirmed directly: over 785 real schema words, RMS
# magnitude runs ~40-65 on shells 0-3 (small primes) vs. ~200-315 on shells
# 8-11 (mid-large primes) — a ~5-7x systematic gap. Comparing raw
# magnitudes across shells with no correction collapses almost every word
# onto whichever role owns the shells with the biggest primes (C, here) —
# confirmed live before this fix. assign_role() below compares each
# shell's magnitude to ITS OWN baseline, not to other shells' raw values.
from functools import lru_cache


@lru_cache(maxsize=1)
def _shell_baseline() -> tuple:
    from .generate import SCHEMA
    sample = (list(SCHEMA.get("verbs", {}).keys())[:400] +
             list(SCHEMA.get("fillers", {}).keys())[:400])
    sample = [w for w in sample if w.isalpha()] or ["the", "a", "is", "of"]
    acc = [0.0] * 16
    for w in sample:
        for k in range(16):
            acc[k] += project(w, k) ** 2
    return tuple(math.sqrt(a / len(sample)) or 1.0 for a in acc)


def assign_role(word: str, sigma: float = 0.5) -> Optional[str]:
    """Which SPOCA role (S/O_i/O_d/C/A) this WORD's own projection fires
    into, AFTER dividing out the per-shell baseline (see the module note
    above — the raw magnitudes are not comparable across shells). e0 is
    excluded on purpose — that shell belongs to the anchor, assigned
    separately by verb-schema lookup in assign_slots(), never by this
    classifier (box_kite.md: e0 is a vertex of no box-kite). The aperture
    is peak/φ, the same threshold console_speak() uses throughout, applied
    to the baseline-corrected ratio — a role only counts if some shell in
    its group clears it, and among role-groups that clear it the largest
    ratio wins. None if nothing clears threshold at all."""
    v = word_shells(word, sigma)
    base = _shell_baseline()
    ratio = [abs(v[k]) / base[k] for k in range(16)]
    rest = ratio[1:]
    peak = max(rest) if rest else 0.0
    if peak <= 0.0:
        return None
    thresh = peak / PHI
    best_role, best_mag = None, 0.0
    for role, ks in ROLE_SHELLS.items():
        mag = max(ratio[k] for k in ks)
        if mag >= thresh and mag > best_mag:
            best_role, best_mag = role, mag
    return best_role


def _verb_lemma(word: str) -> Optional[str]:
    """morphy the word down to a verb base form ('converges' -> 'converge')
    before checking it against the schema — a bare `word in verbs`
    membership test is lemma-blind and will latch onto whichever word in
    the sentence HAPPENS to already be in base form and ALSO have some
    unrelated verb sense (confirmed live: "the integral converges to a
    finite limit..." picked 'limit' as the anchor over 'converges', purely
    because 'limit' needed no inflection to already equal its own VerbNet
    lemma while 'converges' did)."""
    try:
        import sys
        for m in ("sklearn", "sklearn.feature_extraction",
                 "sklearn.feature_extraction.text"):
            sys.modules.setdefault(m, None)
        from nltk.corpus import wordnet as wn
    except Exception:                                     # noqa: BLE001
        return word
    return wn.morphy(word, "v") or word


def assign_slots(text: str, verbs: Optional[dict] = None,
                 sigma: float = 0.5) -> Dict[str, List[str]]:
    """Tokenize `text`, find the anchor (P), then assign every OTHER word
    a role via assign_role(). Returns {role: [words]}, 'P' included in
    canonical SPOCA order, reading order preserved within each role.
    Usable straight into a ParseSpec — no UD parse anywhere in this path,
    so it works on live input or crawled text a treebank never saw.

    The anchor: the first word whose verb-lemma (_verb_lemma) is IN the
    schema, in reading order — the same convention ptolc_bridge.py already
    uses. Disclosed limitation, tried and measured rather than assumed:
    many common words are verb/noun homographs ("board", "water", "point",
    "new" all carry a registered verb sense too), so this picks the wrong
    anchor on some ordinary sentences ("The board elected a new chair..."
    picks 'board' over 'elected'). e0's own magnitude was tried as a
    tie-break — project() at k=0, the shell console_speak() reads
    σ_self/Γ off — and measured WORSE: it picked 'new' (a bare adjective)
    over every real verb candidate in that same sentence, confirming e0
    encodes word identity/shape, not syntactic function, and cannot
    principled-ly settle a homograph question. Reading-order-first, while
    still wrong on some sentences, was strictly better or equal across
    every test case measured here. A real fix needs POS information this
    module was built specifically to avoid requiring."""
    if verbs is None:
        from .generate import SCHEMA
        verbs = SCHEMA.get("verbs", {})
    words = [w.strip(".,;:!?\"'()").lower() for w in text.split()]
    words = [w for w in words if w]

    anchor_idx = next((i for i, w in enumerate(words)
                       if _verb_lemma(w) in verbs), -1)

    out: Dict[str, List[str]] = {}
    for i, w in enumerate(words):
        if i == anchor_idx:
            out.setdefault("P", []).append(w)
            continue
        role = assign_role(w, sigma)
        if role:
            out.setdefault(role, []).append(w)
    return out


if __name__ == "__main__":
    samples = [
        "The integral converges to a finite limit as the series decreases.",
        "The board elected a new chair to lead the committee.",
        "Water flows downhill because gravity pulls it toward the lowest point.",
    ]
    for s in samples:
        print(f"\nTEXT: {s}")
        slots = assign_slots(s)
        for role in ("P", "S", "O_i", "O_d", "C", "A"):
            if role in slots:
                print(f"  {role:4} {slots[role]}")
        unassigned = [w for w in [t.strip('.,;:!?"\'()').lower()
                                  for t in s.split()]
                     if w and w not in [x for v in slots.values() for x in v]]
        if unassigned:
            print(f"  (unassigned: {unassigned})")
