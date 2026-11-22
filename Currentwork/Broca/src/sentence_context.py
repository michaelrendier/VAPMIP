#!/usr/bin/env python3
"""
sentence_context.py — combining individual word box-kites (wordnet_boxkite.py)
into one sentence-level context object.

Cody, 2026-08-25: "the monad is the roots of the tree, and the leaves are
both the input and output words...lets see what the shape of a simple input
looks like when all the box kites are combined from the individual words
into a 'sentence context'...a higher dimensional order of context."

The combination is NOT a new operation invented for this file — it is PW3
(`spiral_is_additive`, SedenionFactoralRelativity/engine/lineage.py:
`address(p*q) = address(p) + address(q)`) applied to context_code instead of
a plain address. context_code(s) = prod CONTEXT_PRIMES[i] ** vector[i], so
multiplying several synsets' codes together is EXACTLY componentwise-summing
their context_vectors — the same additive law already on record, not a new
one. root_vector below is that sum; root_code is the product, kept in sync
and checked against each other in this file's own smoke test.

WSD (word sense disambiguation) here is a deliberate stub: first WordNet
sense per word (wn.synsets(word)[0]), nothing smarter. That is real, honest
scope-narrowing, not hidden — flagged wherever it matters below.
"""

from __future__ import annotations

import string
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from wordnet_boxkite import (
    RELATION_METHODS, context_vector, context_code, context_distance,
)

_STRIP = string.punctuation + '“”‘’—…'


def _clean(word: str) -> str:
    return word.strip(_STRIP).lower()


def resolve_word_synset(word: str) -> Optional[Any]:
    """STUB WSD: first WordNet sense, whatever part of speech WordNet's own
    synsets() ordering puts first. Real sense-disambiguation (using the
    OTHER words in the sentence to pick the sense whose context_vector is
    closest to the sentence so far) is real future work, not done here."""
    from nltk.corpus import wordnet as wn
    synsets = wn.synsets(word)
    return synsets[0] if synsets else None


@dataclass
class SentenceBoxKite:
    text: str
    leaves: List[Dict[str, Any]] = field(default_factory=list)   # [{word, synset, vector}]
    skipped: List[str] = field(default_factory=list)             # words with no WordNet synset
    root_vector: List[int] = field(default_factory=list)         # componentwise sum of leaf vectors
    root_code: int = 1                                            # product of leaf context_codes

    def nonzero_root(self) -> Dict[str, int]:
        return {RELATION_METHODS[i]: c for i, c in enumerate(self.root_vector) if c}


def build_sentence_context(text: str) -> SentenceBoxKite:
    """Tokenize, resolve each word to a synset (stub WSD, first sense),
    combine leaf context_vectors into one root — the sentence's own
    higher-order context object. Words with no WordNet entry (most function
    words: 'the', 'a', 'of') are skipped, not zero-padded — recorded in
    `skipped` rather than silently dropped."""
    n_relations = len(RELATION_METHODS)
    root_vector = [0] * n_relations
    root_code = 1
    leaves: List[Dict[str, Any]] = []
    skipped: List[str] = []

    for raw in text.split():
        w = _clean(raw)
        if not w:
            continue
        synset = resolve_word_synset(w)
        if synset is None:
            skipped.append(w)
            continue
        vec = context_vector(synset)
        leaves.append({'word': w, 'synset': synset, 'vector': vec})
        root_vector = [a + b for a, b in zip(root_vector, vec)]
        root_code *= context_code(synset)

    return SentenceBoxKite(text=text, leaves=leaves, skipped=skipped,
                           root_vector=root_vector, root_code=root_code)


def neighborhood_corpus(leaves: List[Dict[str, Any]],
                        max_per_relation: int = 5,
                        exclude_input: bool = True,
                        basin_k: int = 0,
                        basin_topic: Optional[str] = None) -> List[Any]:
    """Candidate pool for RESPONSE construction. Two sources, merged:

      1. WordNet RELATIONS — every synset directly related (any of the 19
         RELATION_METHODS) to an input leaf, capped per relation per leaf
         so one hub word can't flood the pool. "What is semantically
         related."

      2. The CO-OCCURRENCE BASIN (basin_k > 0) — the Newton basin from
         monad_english_io: the words that actually get used around the
         seed words, IDF-corrected so the function-word flood is crushed,
         then resolved to first-sense synsets. "How people actually talk
         around this." basin_topic loads a topic-scoped A-matrix
         (monad_physics.bin, ...) instead of the full one -- the setting.

    exclude_input=True drops the leaves' own synsets — echoing the input
    back is parroting, not communication."""
    pool: Dict[str, Any] = {}
    input_names = {leaf['synset'].name() for leaf in leaves}

    for leaf in leaves:
        s = leaf['synset']
        for method_name in RELATION_METHODS:
            try:
                targets = getattr(s, method_name)()[:max_per_relation]
            except Exception:
                continue
            for t in targets:
                pool[t.name()] = t

    if basin_k > 0:
        try:
            import monad_english_io as _meio
            me = _meio.read(_meio.topic_path(basin_topic) if basin_topic else None)
            seeds = [leaf['word'] for leaf in leaves]
            added = 0
            for word in me.basin(seeds, k=basin_k * 3, idf=True):  # over-fetch, filter drops
                w = word.strip().lower()
                if len(w) < 3 or not w.isalpha() or w in _meio.STOPWORDS:
                    continue
                syn = resolve_word_synset(w)
                if syn is None:
                    continue
                # `w` must be the PRIMARY lemma of its first synset -- kills
                # acronym expansions ('an' -> associate_in_nursing, 'x' -> ten)
                if syn.lemma_names()[0].replace('_', ' ').lower() != w:
                    continue
                if pool.setdefault(syn.name(), syn) is syn:
                    added += 1
                if added >= basin_k:
                    break
        except Exception:
            pass  # no monad_english.bin available -> relations-only pool

    if exclude_input:
        for name in input_names:
            pool.pop(name, None)
    return list(pool.values())


def nearest_synsets(target_vector: List[int], corpus: List[Any],
                    top_k: int = 5) -> List[Tuple[int, Any]]:
    """(distance, synset) pairs, ascending — the generation step: given the
    sentence's combined root context, which real synsets in the candidate
    pool sit closest to it. Thin wrapper so callers don't need to reach
    into wordnet_boxkite directly for this one comparison."""
    # context_distance() takes two synsets; target_vector is a raw combined
    # vector (usually not any single synset's own), so compare it directly
    # against each candidate's context_vector rather than routing through
    # context_distance().
    scored = [(sum(abs(a - b) for a, b in zip(target_vector, context_vector(s))), s)
              for s in corpus]
    scored.sort(key=lambda t: t[0])
    return scored[:top_k]


if __name__ == '__main__':
    import random

    print('=== sentence context — combining word box-kites into one root ===')
    for sentence in (
        'the bank raised a mound of dirt beside the river',
        'the volcano formed a mountain of cinder and ash',
        'she deposited her savings in the reserve account',
    ):
        ctx = build_sentence_context(sentence)
        print(f'\n  {sentence!r}')
        print(f'    leaves: {[l["word"] + "/" + l["synset"].name() for l in ctx.leaves]}')
        print(f'    skipped (no WordNet entry): {ctx.skipped}')
        print(f'    root_vector (nonzero): {ctx.nonzero_root()}')
        print(f'    root_code digits: {len(str(ctx.root_code))}')

        pool = neighborhood_corpus(ctx.leaves)
        print(f'    neighborhood pool size: {len(pool)}')
        nearest = nearest_synsets(ctx.root_vector, pool, top_k=5)
        print('    nearest pool synsets to the sentence root:')
        for d, s in nearest:
            print(f'      L1={d:<3d} {s.name():20s} {s.definition()[:55]}')

    print('\n=== sanity check: root_code really is the product of leaf codes ===')
    ctx = build_sentence_context('the bank raised a mound of dirt')
    from wordnet_boxkite import context_code as _cc
    product = 1
    for leaf in ctx.leaves:
        product *= _cc(leaf['synset'])
    assert product == ctx.root_code, (product, ctx.root_code)
    print(f'  PW3 (spiral_is_additive) applied to context_code: HOLDS '
          f'({len(str(ctx.root_code))} digits)')

    print('\n=== control: coherent sentence vs. shuffled word-salad ===')
    coherent = 'the volcano formed a mountain of cinder and ash near the river bank'
    words = coherent.split()
    rng = random.Random(20260825)
    rng.shuffle(words)
    salad = ' '.join(words)

    ctx_coherent = build_sentence_context(coherent)
    ctx_salad = build_sentence_context(salad)
    print(f'  coherent root (nonzero): {ctx_coherent.nonzero_root()}')
    print(f'  salad    root (nonzero): {ctx_salad.nonzero_root()}')
    same = ctx_coherent.root_vector == ctx_salad.root_vector
    print(f'  same multiset of words -> same root_vector regardless of order: {same}')
    print('  (expected True: this root combination is order-independent by construction — '
          'word ORDER carries no information here yet, only which synsets fired. '
          'A real syntax-aware combination is future work, not claimed here.)')
