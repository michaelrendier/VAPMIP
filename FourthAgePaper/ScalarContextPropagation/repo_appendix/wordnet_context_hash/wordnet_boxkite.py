#!/usr/bin/env python3
"""
wordnet_boxkite.py — the box-kite context hash, retooled onto real WordNet
synset relations (Cody, 2026-08-24: "retool the prime hashing algorithm to
use wordnet boxkites").

context_addr(synset) depends ONLY on relational structure — hypernym count,
meronym count, and so on — NEVER on which word carries it, never on
spelling. That is the actual design constraint this file exists to satisfy:
"that number containing the context but not the word."

spelling_code(word) is kept separate on purpose — the same split drawn in
conversation: spell the word with prime letters, hash context into a
DIFFERENT number, keep the two distinguishable rather than merging them
into one number that hides which part is which.

Requires: nltk + the wordnet corpus. Both confirmed present in
ValaQuenta/.venv (checked directly, not assumed). Run this file with that
interpreter:
    ValaQuenta/.venv/bin/python3 wordnet_boxkite.py

Predecessor: ContextPlease/claude/scratchpad/2026-08-18_three_faces_and_
identity_bin/boxkite_prime_hash.py — next_prime()/_is_prime() reused
verbatim below; nothing about that arithmetic core needed changing, only
what feeds it.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ── the arithmetic core, reused verbatim from boxkite_prime_hash.py ────────

def _sieve(n: int) -> List[int]:
    sv = bytearray([1]) * (n + 1)
    sv[0] = sv[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    return [i for i in range(n + 1) if sv[i]]


_P = _sieve(200_000)

LETTER_CAP = 71
LETTER_PRIMES: List[int] = [p for p in _P if p <= LETTER_CAP]   # 20 — spelling tier
CONTEXT_PRIMES: List[int] = [p for p in _P if p > LETTER_CAP]   # context tier


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    n = max(2, n)
    if n == 2:
        return 2
    if n % 2 == 0:
        n += 1
    while not _is_prime(n):
        n += 2
    return n


# ── context — the standard WordNet relation vocabulary, fixed, not arbitrary
# 19 real relation types, principled 1-to-1 with assessor-lines: each type
# gets its OWN fixed line, no invented grouping — this is what "not an
# arbitrary construction of a number theory grouping" means in code. The
# exponent on a line is a COMPRESSED COUNT of that relation's targets —
# degree, not identity. Target-identity sensitivity is real future work,
# not hidden here as if it were already done.

RELATION_METHODS: List[str] = [
    'hypernyms', 'instance_hypernyms', 'hyponyms', 'instance_hyponyms',
    'member_holonyms', 'substance_holonyms', 'part_holonyms',
    'member_meronyms', 'substance_meronyms', 'part_meronyms',
    'attributes', 'entailments', 'causes', 'also_sees', 'verb_groups',
    'similar_tos', 'topic_domains', 'region_domains', 'usage_domains',
]

assert len(RELATION_METHODS) <= len(CONTEXT_PRIMES)


def compress_count(count: int) -> int:
    """The count of a relation's targets, log-compressed BEFORE it becomes
    an exponent — this compresses the INPUT DATA, not "the exponent"
    (logging an exponent would just undo the exponentiation; that's not
    what happens here). Confirmed 2026-08-24 against real data: raw count
    used directly as an exponent makes context_code(tree.n.01) a 364-digit
    number (hyponyms=180 -> 83^180); log2-compressing the count first
    (round(log2(180+1))=8 -> 83^8) brings the same synset down to 28
    digits, with no real downside found. Kept as its own named function
    because "log-compressed exponent" as a phrase reads backwards —
    logs and exponents are inverse operations, so name the thing that's
    actually happening: the COUNT gets compressed, then USED as an
    exponent."""
    return round(math.log2(count + 1))


def context_vector(synset: Any) -> List[int]:
    """One exponent per RELATION_METHODS entry — compress_count() of that
    relation's target count for this synset. Nothing about the surface
    word (synset.name(), synset.lemma_names()) is read anywhere in this
    function, on purpose."""
    exponents = []
    for method_name in RELATION_METHODS:
        try:
            targets = getattr(synset, method_name)()
            exponents.append(compress_count(len(targets)))
        except Exception:
            exponents.append(0)
    return exponents


def raw_context_vector(synset: Any) -> List[int]:
    """Uncompressed — the count itself, no log. Kept for reference/
    debugging (this is what context_vector() computed before 2026-08-24;
    see the size comparison in compress_count()'s docstring for why the
    compressed version is now the default)."""
    exponents = []
    for method_name in RELATION_METHODS:
        try:
            targets = getattr(synset, method_name)()
            exponents.append(len(targets))
        except Exception:
            exponents.append(0)
    return exponents


def context_code(synset: Any) -> int:
    """prod CONTEXT_PRIMES[i]^exponent_i — a pure function of relational
    structure. No word, no spelling, anywhere in this computation."""
    code = 1
    for p, e in zip(CONTEXT_PRIMES, context_vector(synset)):
        if e:
            code *= p ** e
    return code


def context_addr(synset: Any) -> Dict[str, int]:
    """(addr, delta) — the lossless pair (boxkite_prime_hash.py's own
    mechanism). addr = next_prime(code) is the synset's location in
    context space; delta recovers the exact code, hence the exact
    relation-counts, exactly."""
    code = context_code(synset)
    addr = next_prime(code)
    return {'code': code, 'addr': addr, 'delta': addr - code}


# ── vector distance — "nearly the same", the piece the address gap ────────
# couldn't answer (see compress_count()'s docstring: a 1-step count change
# multiplies the WHOLE address by a prime, so the gap can't carry
# closeness). Comparing the exponent VECTORS directly is the same move
# boxkite_prime_hash.py's unpack() already makes on a collision — shared
# context = componentwise MIN, the disagreement = what's left over on each
# side. Applied here to any two synsets, not just ones that collided.

def compare_context(s1: Any, s2: Any) -> Dict[str, Any]:
    """shared = componentwise min (what both have, exactly unpack()'s own
    move) — only_1 / only_2 = what's left over on each side once the
    shared part is removed. hamming = how many dimensions differ AT ALL
    (presence/absence of a difference); l1 = how BIG the differences are,
    summed. Both distances returned — they answer different questions,
    same as this project's own tension-vs-Hamiltonian split did."""
    v1, v2 = context_vector(s1), context_vector(s2)
    shared = [min(a, b) for a, b in zip(v1, v2)]
    only_1 = [a - m for a, m in zip(v1, shared)]
    only_2 = [b - m for b, m in zip(v2, shared)]
    hamming = sum(1 for a, b in zip(v1, v2) if a != b)
    l1 = sum(abs(a - b) for a, b in zip(v1, v2))
    return {
        'shared': dict((RELATION_METHODS[i], c) for i, c in enumerate(shared) if c),
        'only_1': dict((RELATION_METHODS[i], c) for i, c in enumerate(only_1) if c),
        'only_2': dict((RELATION_METHODS[i], c) for i, c in enumerate(only_2) if c),
        'hamming': hamming,
        'l1': l1,
    }


def context_distance(s1: Any, s2: Any) -> int:
    """L1 distance between the two compressed exponent vectors — the
    scalar to sort/search by. Cheap: at most 19 small-integer subtractions,
    nothing prime-sized touched at all."""
    v1, v2 = context_vector(s1), context_vector(s2)
    return sum(abs(a - b) for a, b in zip(v1, v2))


def search_context(target: Any, corpus, top_k: int = 10):
    """target: a synset OR a raw 19-length vector (a partial/desired
    "shape" to search FOR, not necessarily any real synset's own vector).
    corpus: an iterable of synsets to search over. Returns the top_k
    closest by context_distance, ascending. This is the mechanism behind
    "context as a search term the monad uses to structure a response" —
    given a desired context-shape, find which real synsets sit nearest it."""
    target_vec = target if isinstance(target, (list, tuple)) else context_vector(target)
    scored = []
    for s in corpus:
        v = context_vector(s)
        d = sum(abs(a - b) for a, b in zip(target_vec, v))
        scored.append((d, s))
    scored.sort(key=lambda t: t[0])
    return scored[:top_k]


# ── spelling — kept separate on purpose ─────────────────────────────────────

def spelling_code(word: str) -> int:
    """Godel-style: position i uses LETTER_PRIMES[i % 20] (cyclic through
    the 20-symbol letter tier), exponent = the letter's alphabet index
    (a=1..z=26) — order-sensitive, no information lost. PROVISIONAL: the
    exact letter-tier mechanics weren't pinned down before this build;
    this is a first working pass, explicitly not a locked design."""
    code = 1
    for i, ch in enumerate(w for w in word.lower() if w.isalpha()):
        p = LETTER_PRIMES[i % len(LETTER_PRIMES)]
        exp = ord(ch) - ord('a') + 1
        code *= p ** exp
    return code


# ── contextual-neighbor collisions — the test that actually held up ────────
# HISTORY, kept honest rather than deleted: the first version of this test
# checked (synset, its own hypernym) pairs for small prime gaps -- that was
# testing SEMANTIC neighborhood (taxonomic relatedness), which Cody
# explicitly corrected: "twin primes were to illustrate the idea of
# contextual neighborhood...not semantic neighborhood." Retested correctly
# on 2026-08-24: EXACT context-vector matches (same relation-counts,
# regardless of meaning) produce exact address collisions every time --
# confirmed on real data, e.g. hilbert.n.01 (mathematician), irrawaddy.n.01
# (a river), and new_york.n.03 all share one shape (named-instance, one
# instance_hypernym, nothing else) despite zero semantic relationship.
# NEAR-miss vectors (differ by 1 in one dimension) do NOT reliably produce
# small gaps even with compress_count() -- see compress_count()'s own
# docstring for the traced example (roll.n.02/depression.n.01, gap
# ~1.96e15, exactly code(roll) * 82 because the encoding multiplies, so a
# single-step count change multiplies the WHOLE number by that dimension's
# prime). "Same or nearly same" is answered two different ways: SAME =
# exact vector match, cheap, already works. NEARLY = needs a direct
# vector-distance comparison (Hamming/componentwise-min, the same tool
# unpack() uses for a collision's shared context), not the address gap.

def find_collisions(n_sample: int = 4000, seed: int = 20260824):
    """Sample real noun synsets, bucket by exact context_vector match, and
    return the buckets with >1 member -- real contextual-neighbor
    collisions, auditable against each synset's own definition()."""
    from nltk.corpus import wordnet as wn

    rng = random.Random(seed)
    all_synsets = list(wn.all_synsets('n'))
    sample = rng.sample(all_synsets, min(n_sample, len(all_synsets)))

    buckets: Dict[Tuple[int, ...], list] = {}
    for s in sample:
        v = tuple(context_vector(s))
        buckets.setdefault(v, []).append(s)

    return {v: ss for v, ss in buckets.items() if len(ss) > 1}, len(sample)


# ── the shared snapshot schema — same fields as PtolC/boxkite_bin.h's
# BoxKiteEntry, a different serialization of the SAME data (pickle here,
# a packed C struct there), not a different schema. Cross-verified
# 2026-08-25 against the real C build (dump_boxkite_bin.c / wordnet-dev):
# bank/tree/volcano's synset offsets and all 19 relation values matched
# exactly between this file's context_vector() and the C library's
# ptrtyp[] tally. depth_weight is the one adjustable knob both sides
# share — a per-entry scalar (default 1.0) scaling how strongly that
# entry's context counts when CONSUMED (sentence-root summing, nearest-
# neighbor distance) — not a multi-hop graph-depth traversal, which is
# real future work, not built here.

def _pos_code(synset) -> int:
    """wn.h's NOUN=1/VERB=2/ADJ=3/ADV=4 — matched here so a pickle entry's
    'pos' field means the same integer on both sides."""
    p = synset.pos()
    return {'n': 1, 'v': 2, 'a': 3, 's': 3, 'r': 4}.get(p, 0)


def synset_entry(word: str, synset: Any, depth_weight: float = 1.0) -> Dict[str, Any]:
    """One entry, same 5 fields as BoxKiteEntry: word, pos, synset_offset,
    vector, depth_weight."""
    return {
        'word': word,
        'pos': _pos_code(synset),
        'synset_offset': synset.offset(),
        'vector': context_vector(synset),
        'depth_weight': depth_weight,
    }


def export_pickle(path: str, words: Sequence[str] = None) -> int:
    """Dump first-sense-per-word entries to a pickle at `path`, same
    schema as c_monad_wordnet.bin. words=None dumps every headword WordNet
    itself lists (all POS) — matches dump_boxkite_bin.c's own full sweep;
    pass a smaller list for a quick/partial export."""
    import pickle
    from nltk.corpus import wordnet as wn

    if words is None:
        seen = set()
        for pos in ('n', 'v', 'a', 'r'):
            for w in wn.all_lemma_names(pos=pos):
                seen.add(w)
        words = sorted(seen)

    entries: List[Dict[str, Any]] = []
    for w in words:
        synsets = wn.synsets(w)
        if not synsets:
            continue
        entries.append(synset_entry(w, synsets[0]))

    with open(path, 'wb') as f:
        pickle.dump({'magic': 'BXKT', 'version': 1, 'entries': entries}, f)
    return len(entries)


def load_pickle(path: str) -> List[Dict[str, Any]]:
    import pickle
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data['entries']


def set_depth_weight(entries: List[Dict[str, Any]], word: str, weight: float) -> bool:
    """Mutate ONE entry's depth_weight in place (the list, in memory) —
    caller re-pickles with export_entries_pickle() to persist. Same
    contract as boxkite_bin.h's boxkite_set_depth_weight(): find by word,
    touch only that field, nothing else. Returns True if found."""
    for e in entries:
        if e['word'] == word:
            e['depth_weight'] = weight
            return True
    return False


def get_depth_weight(entries: List[Dict[str, Any]], word: str) -> Optional[float]:
    for e in entries:
        if e['word'] == word:
            return e['depth_weight']
    return None


def save_entries_pickle(path: str, entries: List[Dict[str, Any]]) -> None:
    import pickle
    with open(path, 'wb') as f:
        pickle.dump({'magic': 'BXKT', 'version': 1, 'entries': entries}, f)


if __name__ == '__main__':
    from nltk.corpus import wordnet as wn

    print('=== context_addr on real synsets — compressed, no word, no spelling ===')
    for word in ('tree', 'bank', 'run'):
        s = wn.synsets(word)[0]
        vec = context_vector(s)
        ca = context_addr(s)
        print(f'\n  {word!r} -> {s.name()}  ({s.definition()[:60]}...)')
        print(f'    context_vector (compressed): {dict(zip(RELATION_METHODS, vec))}')
        print(f'    code digits: {len(str(ca["code"]))}   addr digits: {len(str(ca["addr"]))}')

    print('\n=== spelling_code, kept separate ===')
    for word in ('tree', 'arbre'):
        print(f'  spelling_code({word!r}) digits: {len(str(spelling_code(word)))}')

    print('\n=== contextual-neighbor collisions — audit a few against their definitions ===')
    collisions, n = find_collisions(n_sample=2000)
    print(f'  {n} synsets sampled, {len(collisions)} shared context-shapes found')
    shown = 0
    for v, ss in collisions.items():
        if 2 <= len(ss) <= 3 and shown < 4:
            nz = {RELATION_METHODS[i]: c for i, c in enumerate(v) if c}
            print(f'\n  shape {nz}:')
            for s in ss:
                print(f'    {s.name():22s} — {s.definition()}')
            shown += 1
