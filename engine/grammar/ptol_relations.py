"""
ptol_relations.py — WordNet-STYLE relations, grown from ptol's own
experience, never rebuilding anyone else's dump.

Cody, 2026-09-12/13: "it shouldn't be difficult to fill out the full
wordnet style information on the fly... we don't have to rebuild anything
someone else does, we just need to add the 'experience' of ptol to add
contextual, semantic and phonetic 'relationships' in the same manner as
WordNet. The boxkite context is the only thing really that is going to be
needing to be updated... once a vocabulary is in place... and the sedenion
window can be that tool... but also the daemon running in the background
that your hook provides all the conversations here to."

Last turn established, concretely, against the real store: monad3_c.bin's
WordNet sub-store (c_monad_wordnet.bin) is a STATIC, one-time dump from the
system's wordnet-dev package — nothing in the live-ingest path (the daemon's
in-place fold, the periodic CSR rebuild) ever writes to it, and it can
disagree with NLTK's own WordNet coverage ("abelian": eng_idx real, 59 live
co-occurrence edges, wn_idx=-1 — blank, forever, under that path).

This is the SEPARATE, ptol-native structure that CAN grow — not a copy of
WordNet, not a rebuild of it: relation FACTS extracted from ordinary
sentences using slot_shells.find_anchor()'s no-parse geometric anchor
detection ("the sedenion window as that tool") plus plain word position
for the two arguments (see extract_facts()'s docstring for why position,
not assign_role()'s S/O_d/O_i/C/A labels, does the argument-finding —
measured directly, those labels are not yet reliable enough on short
common nouns for a fact worth persisting forever). Facts are stored keyed
exactly like WordNet's own 19 RELATION_METHODS (wordnet_boxkite.py) so
sem_hash.py's hypernym-closure walk can fold BOTH sources together — real
WordNet where it exists, ptol's own experience everywhere else, and both
where they agree.

WHAT THIS IS NOT, yet: "we don't have a 'sentence parser' yet, only a
'words in a sentence parser'" is exactly right (Cody's own words) — the
patterns below are deliberately narrow (single-clause, unambiguous
verb-argument structure only) BECAUSE slot_shells.assign_slots() classifies
each word independently, with no notion of clause boundaries, coordination,
or attachment. A guard (_looks_simple) refuses to extract from anything
that could confuse that independence — a wrong relation FACT persisted
forever is a much worse failure than a missed one.
"""
from __future__ import annotations
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

from . import slot_shells

_HERE = os.path.dirname(os.path.abspath(__file__))
_VAPMIP_ROOT = os.path.dirname(os.path.dirname(_HERE))     # .../VAPMIP
if _VAPMIP_ROOT not in sys.path:
    sys.path.insert(0, _VAPMIP_ROOT)
from wordnet_boxkite import RELATION_METHODS  # noqa: F401  (the real 19, for reference)
STORE_PATH = os.path.join(_HERE, "ptol_relations.json")

# verb -> the WordNet relation it establishes, direction fixed exactly the
# way WordNet defines that relation (part_meronyms(X) = the parts X HAS;
# member_holonyms(X) = the wholes X is A MEMBER OF). Reuses generate.py's
# own _VERB_PREP verb-semantics table — these verbs were already
# identified there as carrying a fixed relational meaning, independent of
# whether English routes the target through a direct object ("comprises
# pistons") or a preposition ("belongs to a bicycle", "consists of parts")
# — either way there is exactly ONE content word after the verb once
# function words are dropped, so no SPOCA role label is needed to find it
# (see extract_facts()'s docstring for why that label isn't relied on).
RELATION_VERBS: Dict[str, str] = {
    "comprise": "part_meronyms",
    "consist":  "part_meronyms",
    "contain":  "part_meronyms",
    "include":  "part_meronyms",
    "belong":   "member_holonyms",
    "resemble": "similar_tos",
}
_SYMMETRIC = {"similar_tos"}

_COPULA_LEMMAS = {"be"}


def _is_noun(word: str) -> bool:
    """Cheap, local — no fresh WordNet call if the schema already knows.
    Falls back to a direct synsets(pos='n') check (guarded per the
    nltk/sklearn ABI note in engine/grammar/__init__.py)."""
    from .generate import SCHEMA
    e = SCHEMA.get("fillers", {}).get(word)
    if e is not None:
        return e.get("pos") == "n"
    try:
        import sys
        for m in ("sklearn", "sklearn.feature_extraction",
                 "sklearn.feature_extraction.text"):
            sys.modules.setdefault(m, None)
        from nltk.corpus import wordnet as wn
        return bool(wn.synsets(word, pos="n"))
    except Exception:                                     # noqa: BLE001
        return False


_COMPLEXITY_MARKERS = (
    "and", "or", "but", "because", "although", "though", "while",
    "which", "who", "whom", "that", "when", "if", "since", "so",
)


def _has_complexity_marker(words: List[str]) -> bool:
    """A coordinator/subordinator/relative pronoun means more than one
    clause is probably present, and neither find_anchor() nor plain
    word-position has any notion of clause boundaries — content words
    from two different clauses would read as one flat argument pair."""
    return any(w in _COMPLEXITY_MARKERS for w in words)


class PtolRelationStore:
    """{relation: {word: {target: count}}} — the SAME shape as
    RELATION_METHODS' per-relation adjacency, just keyed by SURFACE WORD
    (ptol's vocabulary) rather than WordNet synset id (WordNet has none for
    a word it doesn't know). Append-only in spirit: a re-observed fact
    increments its count rather than being deduplicated away — count is
    the confidence signal, exactly compress_count()'s role in
    wordnet_boxkite.py for the real relations."""

    def __init__(self, path: str = STORE_PATH):
        self.path = path
        self.data: Dict[str, Dict[str, Dict[str, int]]] = {}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    self.data = json.load(f)
            except Exception:                             # noqa: BLE001
                self.data = {}

    def save(self) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=1, sort_keys=True)
        os.replace(tmp, self.path)

    def add(self, relation: str, word: str, target: str) -> None:
        bucket = self.data.setdefault(relation, {}).setdefault(word, {})
        bucket[target] = bucket.get(target, 0) + 1

    def targets(self, word: str, relation: Optional[str] = None) -> List[str]:
        if relation:
            return list(self.data.get(relation, {}).get(word, {}))
        out: List[str] = []
        for rel_bucket in self.data.values():
            out += list(rel_bucket.get(word, {}))
        return out

    def all_targets(self, word: str) -> List[str]:
        """Every target of every relation ptol has observed for `word` —
        the closure-walk input sem_hash.py needs (see its module note)."""
        return self.targets(word)


def extract_facts(text: str) -> List[Tuple[str, str, str]]:
    """The core extractor. Returns [(relation, self_word, target_word), ...]
    — never writes anywhere; callers decide whether/where to persist.

    Finds the anchor via slot_shells.find_anchor() ("the sedenion window
    as that tool" — no UD parse, so this runs on live conversation, not
    just treebank text), but does NOT use assign_role()'s S/O_d/O_i/C/A
    labels to pick out the two arguments. Measured directly, 2026-09-13:
    those labels are still unreliable on short common nouns even after
    the per-shell baseline fix (a real word can clear more than one
    role-group's threshold, and which one wins is sensitive to noise this
    task can't afford). Word POSITION relative to the anchor — the one
    content word immediately before it is the subject-like argument, the
    one immediately after is the object/complement-like argument — is a
    far more reliable signal for a plain S-verb-O/S-verb-C/S-verb-PP
    sentence, and needs no shell classification at all. This is the
    concrete shape of "a 'words in a sentence' parser, not a 'sentence'
    parser" (Cody's own framing): the anchor is found geometrically, the
    two arguments are found positionally, and nothing here understands
    clause structure beyond that — which is exactly why _has_complexity_
    marker and the exactly-one-content-word-per-side check exist: refuse
    rather than guess wherever that would matter."""
    words = slot_shells.tokenize(text)
    if not words or _has_complexity_marker(words):
        return []
    # find_anchor() searches all ~9000 VerbNet lemmas — fine for generation,
    # but needlessly homograph-prone here: this module cares about exactly
    # 7 verb lemmas, so scan for those specifically instead. Confirmed
    # live: find_anchor() picked 'group' over 'is' in "An abelian group is
    # a group." and 'wheel' over 'belongs' in "A wheel belongs to a
    # bicycle." — both real nouns that also happen to have an unrelated
    # verb sense, exactly the disclosed find_anchor() limitation, avoided
    # here by never asking the broad question.
    _known = _COPULA_LEMMAS | set(RELATION_VERBS)
    anchor_idx = next((i for i, w in enumerate(words)
                       if slot_shells._verb_lemma(w) in _known), -1)
    if anchor_idx < 0:
        return []

    before = [w for i, w in enumerate(words)
             if i < anchor_idx and w not in slot_shells._FUNCTION_WORDS]
    after = [w for i, w in enumerate(words)
            if i > anchor_idx and w not in slot_shells._FUNCTION_WORDS]
    if len(before) != 1 or len(after) != 1:
        return []                                  # ambiguous -> refuse
    s, t = before[0], after[0]
    if s == t:
        return []

    lemma = slot_shells._verb_lemma(words[anchor_idx])
    facts: List[Tuple[str, str, str]] = []

    if lemma in _COPULA_LEMMAS:
        if _is_noun(s) and _is_noun(t):
            facts.append(("hyponyms", t, s))       # t's hyponym is s
            facts.append(("hypernyms", s, t))      # s's hypernym is t
        return facts

    rel = RELATION_VERBS.get(lemma)
    if rel:
        facts.append((rel, s, t))
        if rel in _SYMMETRIC:
            facts.append((rel, t, s))
    return facts


def observe(text: str, store: Optional[PtolRelationStore] = None) -> int:
    """Extract + persist. Returns the number of facts recorded. This is
    the function a daemon/harness ingest hook would call per line of
    observed text — NOT yet wired to one (see the module note); callable
    standalone in the meantime, including directly on this conversation's
    own transcript."""
    own = store is None
    store = store or PtolRelationStore()
    facts = extract_facts(text)
    for rel, w, t in facts:
        store.add(rel, w, t)
    if facts and own:
        store.save()
    return len(facts)


if __name__ == "__main__":
    samples = [
        "An abelian group is a group.",
        "The engine comprises pistons.",
        "A wheel belongs to a bicycle.",
        "A duality resembles a symmetry.",
        "The board elected a new chair to lead the committee.",   # complex -> skipped
    ]
    store = PtolRelationStore(path=os.path.join(_HERE, "_ptol_relations_demo.json"))
    for s in samples:
        n = observe(s, store)
        print(f"{s!r:70} -> {n} fact(s)")
    store.save()
    print(json.dumps(store.data, indent=1))
