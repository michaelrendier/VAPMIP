"""
sem_hash.py — the semantic prime code for FILLERS (nouns / adjectives).

The 19-relation box-kite hash (context_hash_v2) does not spread concrete
nouns — most fire only `hypernyms`.  What discriminates them is the HYPERNYM
CLOSURE, so this hashes that instead:

    sem_code(n) = ∏  prime(ancestor)   over the hypernym closure of n
                 (squarefree — a Gödel code of the meaning-address)

Two words RESONATE by shared prime factors == shared ancestors:

    resonance(a, b) = number of distinct primes dividing gcd(sem_code a, b)

A prime is handed out lazily, one per DISTINCT ancestor synset actually seen
(never a walk over all ~100k WordNet synsets).  Register still comes from
context_hash_v2.gamma_radial — it works on the |gamma| depth axis even where
the relational code is flat.
"""
from __future__ import annotations
import math
import re
import sys
from functools import lru_cache


def _prime_gen():
    yield 2
    yield 3
    small = [2, 3]
    cand = 5
    while True:
        if all(cand % p for p in small if p * p <= cand):
            small.append(cand)
            yield cand
        cand += 2


_PGEN = _prime_gen()
_PRIME_OF: dict[int, int] = {}


def _prime_for(offset: int) -> int:
    p = _PRIME_OF.get(offset)
    if p is None:
        p = next(_PGEN)
        _PRIME_OF[offset] = p
    return p


def load_prime_table(mapping) -> int:
    """Install a PERSISTED offset->prime table (from the schema) before any
    sem_code/anchor_code calls, so a synset gets the SAME prime whether it
    was hashed at build time or freshly at generation time — two processes
    must agree on the code, or gcd finds nothing even for a real match.
    Returns the number of entries installed; existing lazy entries are kept,
    the persisted ones fill in anything not yet seen this process. Also fast
    -forwards the generator past every prime already claimed, so a NEW
    offset (unseen in the persisted table) never collides with one that is."""
    n = 0
    claimed = set(_PRIME_OF.values())
    for k, v in mapping.items():
        off, p = int(k), int(v)
        if off not in _PRIME_OF:
            _PRIME_OF[off] = p
            n += 1
        claimed.add(p)
    global _PGEN
    old_gen = _PGEN                        # capture BEFORE reassigning below —
    def _resume():                         # `_PGEN` inside this closure would
        for p in old_gen:                  # otherwise resolve to ITSELF at call
            if p not in claimed:           # time (found live, 2026-09-11: any
                yield p                    # offset new since the table was
    _PGEN = _resume()                      # loaded raised "generator already
    return n                               # executing" / StopIteration)


def dump_prime_table() -> dict:
    return {str(k): v for k, v in _PRIME_OF.items()}


def _wn():
    for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
        sys.modules.setdefault(m, None)
    from nltk.corpus import wordnet as wn
    return wn


def sem_code(synset) -> int:
    """squarefree product of ancestor primes (self + hypernym closure)."""
    code = 1
    seen: set[int] = set()
    stack = [synset]
    while stack:
        s = stack.pop()
        o = s.offset()
        if o in seen:
            continue
        seen.add(o)
        code *= _prime_for(o)
        stack.extend(s.hypernyms())
        stack.extend(s.instance_hypernyms())
    return code


def resonance(code_a: int, code_b: int) -> int:
    """# of shared ancestor primes = # distinct prime factors of gcd."""
    g = math.gcd(code_a, code_b)
    if g <= 1:
        return 0
    n, k, d = g, 0, 2
    while d * d <= n:
        if n % d == 0:
            k += 1
            while n % d == 0:
                n //= d
        d += 1
    return k + (1 if n > 1 else 0)


# ── thematic-role semantic anchors (WordNet synset names) ─────────────────
ROLE_ANCHORS = {
    "Agent":       ["person.n.01", "causal_agent.n.01", "organization.n.01"],
    "Theme":       ["entity.n.01", "abstraction.n.06"],
    "Recipient":   ["person.n.01", "social_group.n.01"],
    "Attribute":   ["attribute.n.02", "quality.n.01", "state.n.02"],
    "Location":    ["location.n.01", "region.n.03", "structure.n.01"],
    "Instrument":  ["instrumentality.n.03", "device.n.01"],
    "Source":      ["origin.n.02", "point.n.02"],
    "Goal":        ["goal.n.01", "end.n.02", "location.n.01"],
    "Destination": ["location.n.01", "structure.n.01"],
    "Pivot":       ["entity.n.01"],
    "Patient":     ["object.n.01", "entity.n.01"],
    "Asset":       ["quantity.n.01", "possession.n.02"],
    "Beneficiary": ["person.n.01"],
}


@lru_cache(maxsize=64)
def role_code(themrole: str) -> int:
    wn = _wn()
    code = 1
    for name in ROLE_ANCHORS.get(themrole, ["entity.n.01"]):
        try:
            code *= sem_code(wn.synset(name))
        except Exception:                                 # noqa: BLE001
            pass
    return code


# ── SELRESTR anchors — the INVARIANT (Noether-conserved) gate ─────────────
# VerbNet THEMROLE SELRESTRS, keyed to a WordNet anchor whose hypernym-closure
# MEMBERSHIP is the invariant test: candidate.sem_code % anchor_code == 0
# means the anchor is literally an ancestor of the candidate — a fact that
# cannot vary by picking a different candidate in the same class, i.e. exactly
# the zero-tension / conserved read the gate needs.  Grammatical restrictions
# (int_control, refl, plural, nonrigid, pointy, elongated) name properties no
# hypernym closure carries — skipped, not guessed at.
SELRESTR_ANCHORS = {
    "animate": "animate_thing.n.01", "organization": "organization.n.01",
    "concrete": "physical_entity.n.01", "abstract": "abstraction.n.06",
    "animal": "animal.n.01", "biotic": "organism.n.01",
    "body_part": "body_part.n.01", "comestible": "food.n.01",
    "communication": "communication.n.02", "currency": "currency.n.01",
    "eventive": "event.n.01", "force": "force.n.02",
    "garment": "garment.n.01", "human": "person.n.01",
    "location": "location.n.01", "machine": "machine.n.01",
    "region": "region.n.03", "solid": "solid.n.01",
    "sound": "sound.n.04", "substance": "substance.n.01",
    "vehicle": "vehicle.n.01", "vehicle_part": "vehicle.n.01",
}


@lru_cache(maxsize=64)
def anchor_code(restr_type: str) -> int:
    wn = _wn()
    name = SELRESTR_ANCHORS.get(restr_type)
    if not name:
        return 0
    try:
        return sem_code(wn.synset(name))
    except Exception:                                     # noqa: BLE001
        return 0


def gate_pass(candidate_code: int, restrs) -> bool:
    """restrs = [(sign, type), ...].  '+' types OR (pass if any match); '-'
    types must ALL be absent.  Non-taxonomy types carry no anchor (code 0)
    and are silently skipped — nothing to gate on."""
    pos, neg = [], []
    for sign, typ in restrs:
        ac = anchor_code(typ)
        if ac == 0:
            continue
        (neg if sign == "-" else pos).append(ac)
    for ac in neg:
        if candidate_code % ac == 0:
            return False
    if pos:
        return any(candidate_code % ac == 0 for ac in pos)
    return True


# ── the granular maths corpus (monad_mathematics.bin) — RANK bonus only ───
# Cody, 2026-09-11: "there has to be a happy medium between 'using the
# mathematics corpus' vs 'using the mathematics corpus as extra weight'."
#
# monad_mathematics.bin (PtolemyDesktop/Archimedes/monadbin.py's MathsVocab)
# is a flat scrape — no hypernym closure, no taxonomy, nothing commensurable
# with sem_code — so it can never be the GATE. That was exactly the removed
# Archimedes bug: a last-word membership test over that same flat scrape
# false-positived on "internet" and "color". It is only ever a RANK bonus
# below, and only for candidates whose TOPIC already passed a real, sparse,
# structural gate built from WordNet — never from this corpus.
#
# The gate itself is 3 independent, individually narrow, best-effort
# signals OR'd together — WordNet's own maths coverage is genuinely
# inconsistent (measured, 2026-09-11: of 12 common maths nouns — integral,
# derivative, eigenvalue, theorem, matrix, series, equation, limit,
# variable, polynomial, vector, sum — only 2 reach mathematics.n.01 by
# hypernym closure on their FIRST sense (WordNet's "most frequent" sense is
# often not the maths one: series.n.07 of 7, limit.n.05 of 6, sum.n.02 of
# 6); only 4 carry an explicit topic_domain of mathematics.n.01; checking
# ALL senses against a curated multi-node anchor set closes most of the
# rest). A miss just means the corpus contributes no bonus — degrades to
# the pre-existing baseline (no signal at all), never to a false positive
# the way the removed corpus-membership gate did.
_MATH_TOKEN_RE = re.compile(     # mirrors PtolC/ptol_layer.py's _MATH_RE
    r'[∑∫∂σζΓΩπφ]|theorem|proof|integral|eigenvalue|riemann|prime|modular|'
    r'matrix|vector|polynomial|derivative|logarithm|coefficient|equation|'
    r'inequality|calculus|algebra|geometry|trigonometry|topology',
    re.IGNORECASE)

# WordNet's purpose-built maths-domain nodes — not just mathematics.n.01
# itself (too shallow a subtree to catch much), but the "mathematical_*"
# family that terms like "equation" (-> mathematical_statement.n.01) and
# "function" (-> mathematical_relation.n.01) actually route through.
_MATHS_ANCHOR_SYNSETS = (
    "mathematics.n.01", "mathematical_relation.n.01",
    "mathematical_statement.n.01", "mathematical_process.n.01",
    "mathematical_space.n.01", "mathematical_notation.n.01",
    "mathematical_symbol.n.01",
)


@lru_cache(maxsize=1)
def _maths_anchor_codes() -> tuple:
    wn = _wn()
    codes = []
    for name in _MATHS_ANCHOR_SYNSETS:
        try:
            codes.append(sem_code(wn.synset(name)))
        except Exception:                                 # noqa: BLE001
            pass
    return tuple(codes)


@lru_cache(maxsize=4096)
def is_maths_eligible(word: str) -> bool:
    """The GATE. Sparse and structural — see the module note above. Checks
    ALL noun senses (not just the first — WordNet's most-frequent sense is
    often not the maths one), OR'd with the token regex. Never corpus
    membership; false by default, on purpose."""
    w = word.lower().strip()
    if not w:
        return False
    if _MATH_TOKEN_RE.search(w):
        return True
    anchors = _maths_anchor_codes()
    if not anchors:
        return False
    wn = _wn()
    for syn in wn.synsets(w, pos="n"):
        if any(d.name() == "mathematics.n.01" for d in syn.topic_domains()):
            return True
        code = sem_code(syn)
        if any(code % a == 0 for a in anchors):
            return True
    return False


@lru_cache(maxsize=1)
def _maths_vocab_words() -> frozenset:
    """The RANK source. Presence-only — the pickle's beta/E fields are
    undocumented (Archimedes/monadbin.py's own comment: "already weighted,
    read as-is, no hashing, no learning"); fabricating a numeric weight
    from fields we don't understand is exactly the confident-wrong-number
    failure mode this framework rejects. A flat membership check is the
    honest amount of information this asset can responsibly contribute
    today."""
    import glob
    import os
    import pickle
    # __file__ = .../ThePlace/VAPMIP/engine/grammar/sem_hash.py -> 4 dirnames
    # to ThePlace (VAPMIP/engine/grammar, VAPMIP/engine, VAPMIP, ThePlace).
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))                       # .../ThePlace
    for path in glob.glob(os.path.join(
            root, "PTorrent", "bin_archive", "clean", "monad_mathematics.bin")):
        try:
            with open(path, "rb") as f:
                d = pickle.load(f)
            words = d.get("words") or []
            return frozenset(w.lower() for w in words if isinstance(w, str))
        except Exception:                                  # noqa: BLE001
            continue
    return frozenset()


def maths_rank_bonus(word: str, topic_is_maths: bool) -> int:
    """+1 iff the topic already gated in AND this candidate is itself in
    the granular maths vocabulary — never computed, never scored, while
    the gate is closed. An additive nudge among survivors of the real
    (SELRESTR) gate, never a pool swap or a route switch."""
    if not topic_is_maths:
        return 0
    return 1 if word.lower() in _maths_vocab_words() else 0


if __name__ == "__main__":
    import time
    t0 = time.time()
    wn = _wn()
    pool = ["result", "method", "engine", "series", "model", "integral",
            "board", "person", "device", "table", "researcher", "value", "limit"]
    codes = {w: sem_code(wn.synsets(w, pos="n")[0]) for w in pool
             if wn.synsets(w, pos="n")}
    print(f"hashed {len(codes)} nouns in {time.time()-t0:.1f}s, "
          f"{len(_PRIME_OF)} distinct ancestor primes")
    for role in ("Agent", "Theme", "Location", "Instrument", "Attribute"):
        rc = role_code(role)
        rank = sorted(codes, key=lambda w: -resonance(codes[w], rc))
        print(f"  {role:11} -> {[(w, resonance(codes[w], rc)) for w in rank[:4]]}")
