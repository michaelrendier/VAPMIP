"""
lyndon_conjugation.py -- STUB. Lyndon factorisation as the part of the equation that will handle conjugations and tenses.

STATUS (2026-11-25, Cody's go): the Lyndon core is real and checked (`verify()`). `conjugates()` and `inflection_frame()` are now BUILT
(section "verb group" below); the design is the author's engineering choice made on that day, recorded here, not a finding.
sedenion_window._repass calls it; tenseplan.py picks the tense.  Original 2026-10-14 note: the two hooks were stubs; that is superseded.

Why Lyndon words (from the Collatz work, FourthAgePapers/CollatzShift, and Cody's reading of it): a Lyndon
word is a word strictly smaller than all of its proper rotations. The Chen-Fox-Lyndon theorem: every word
factors UNIQUELY as a concatenation of Lyndon words in non-increasing order. Lyndon words are the
"primes" of words; the factorisation is the word-level fundamental theorem of arithmetic, the same
kind of object as the project's word-primes and sentence constructor.

One naming caution, kept explicit: in combinatorics on words, two words are CONJUGATE when one is a
rotation of the other (uv ~ vu). That is the necklace / cyclic-class sense. Whether it is the same
thing as grammatical conjugation (verb forms) is a question for the design, not something this stub
assumes. `conjugates()` below is written for the combinatorial sense only, and its stub status
refers to the grammatical sense.

What the real core provides (all stdlib, exact):
    duval(word)            the Lyndon factorisation (Duval's algorithm, one linear pass)
    is_lyndon(word)        the definition, tested directly
    least_rotation(word)   the canonical necklace representative
    primitive_root(word)   the smallest u with word = u^k, and k
    necklace_class(word)   all distinct rotations (the combinatorial conjugacy class)
    verify()               exhaustive check of the theorem over short words
"""
from __future__ import annotations

from itertools import product
from typing import List, Sequence, Tuple


def is_lyndon(w: Sequence) -> bool:
    """True when ``w`` is non-empty and strictly smaller than every proper rotation."""
    n = len(w)
    return n > 0 and all(tuple(w) < tuple(w[i:]) + tuple(w[:i]) for i in range(1, n))


def duval(w: Sequence) -> List[Tuple]:
    """The Lyndon factorisation of ``w``: Lyndon words ``l1 >= l2 >= ... >= lk`` with ``w = l1 l2 ... lk``."""
    w = tuple(w)
    n, i, out = len(w), 0, []
    while i < n:
        j, k = i + 1, i
        while j < n and w[k] <= w[j]:
            k = i if w[k] < w[j] else k + 1
            j += 1
        while i <= k:
            out.append(w[i:i + j - k])
            i += j - k
    return out


def least_rotation(w: Sequence) -> Tuple:
    """The least rotation of ``w`` (the canonical necklace representative)."""
    w = tuple(w)
    return min(w[i:] + w[:i] for i in range(len(w))) if w else w


def primitive_root(w: Sequence) -> Tuple[Tuple, int]:
    """``(u, k)`` with ``w = u^k`` and ``u`` the shortest such word."""
    w = tuple(w)
    n = len(w)
    for d in range(1, n + 1):
        if n % d == 0 and w[:d] * (n // d) == w:
            return w[:d], n // d
    return w, 1


def necklace_class(w: Sequence) -> List[Tuple]:
    """The distinct rotations of ``w``: its class under conjugation in the combinatorial sense (uv ~ vu)."""
    w = tuple(w)
    return sorted({w[i:] + w[:i] for i in range(len(w))}) if w else [w]


# ── the verb group as a Lyndon factor list (2026-11-25) ──────────────────────────────────────────────────────────────────────────────────
# English fixes the order of a verb group: TENSE (+ modal), have+-en (perfect), be+-ing (progressive), then the main verb.  Give each
# feature a rank (outer = larger):  TENSE 4 > MODAL 3 > PERF 2 > PROG 1 > V 0.  A verb group is the word of its ranks in NON-INCREASING order
# (the order Chen-Fox-Lyndon factorisations come in), and its Lyndon factorisation (duval) is the list of its primes, one per feature.
# So: a tense is a factor list; the group is determined by the multiset of its factors (the integer analogy: Omega = number of factors);
# `divides`, `gcd`, `lcm` act on the exponents; and realising the group is "affix hopping": a PERF factor makes the next word -en,
# a PROG factor makes the next word -ing, the TENSE (or the modal) is carried by the first word.  With distinct ranks every factor is a
# single letter, so the factorisation is a sort; what the Lyndon view contributes is the canonical form, the factor algebra, and (below) the
# necklace/primitive-root tools used on a paragraph's tense stream.
RANK = {'TENSE': 4, 'MODAL': 3, 'PERF': 2, 'PROG': 1, 'V': 0}
_NAME = {v: k for k, v in RANK.items()}
_TENSE_WORDS = {'past', 'present', 'future', 'conditional'}


def parse_tense(spec) -> dict:
    """'past perfect progressive' -> {'tense': 'past'|'present', 'modal': None|'will'|'would', 'perf': bool, 'prog': bool, 'mood': ...}.
    Accepts the sedenion_window TENSES names (base, past, present, future, perfect, progressive, imperative, conditional) and compounds of them."""
    toks = set(str(spec or 'present').lower().replace('-', ' ').split())
    d = {'tense': 'present', 'modal': None, 'perf': 'perfect' in toks, 'prog': 'progressive' in toks, 'mood': 'indicative'}
    if 'past' in toks: d['tense'] = 'past'
    if 'future' in toks: d['modal'] = 'will'
    if 'conditional' in toks: d['modal'], d['tense'] = 'would', 'past'
    if 'imperative' in toks or 'base' in toks: d['mood'] = 'imperative' if 'imperative' in toks else 'base'; d['tense'] = 'base'
    return d


def verb_group(spec) -> Tuple[int, ...]:
    """The group as a non-increasing rank word, e.g. 'past perfect' -> (4, 2, 0); 'future progressive' -> (4, 3, 1, 0)."""
    d = parse_tense(spec)
    w = [RANK['V']]
    if d['prog']: w.append(RANK['PROG'])
    if d['perf']: w.append(RANK['PERF'])
    if d['modal']: w.append(RANK['MODAL'])
    if d['tense'] != 'base': w.append(RANK['TENSE'])
    return tuple(sorted(w, reverse=True))


def factors(spec) -> List[str]:
    """The Lyndon factor list of the group, by name: ['TENSE', 'PERF', 'V'] for the past perfect."""
    return [_NAME[f[0]] for f in duval(verb_group(spec))]


def exponents(spec) -> dict:
    return {n: factors(spec).count(n) for n in RANK if n in factors(spec)}


def divides(a, b) -> bool:
    """The group of `a` divides the group of `b` (every factor of a is a factor of b): 'perfect' divides 'past perfect progressive'."""
    ea, eb = exponents(a), exponents(b)
    return all(eb.get(k, 0) >= v for k, v in ea.items())


def gcd(a, b) -> Tuple[int, ...]:
    ea, eb = exponents(a), exponents(b)
    return tuple(sorted([RANK[k] for k in RANK for _ in range(min(ea.get(k, 0), eb.get(k, 0)))], reverse=True))


def lcm(a, b) -> Tuple[int, ...]:
    ea, eb = exponents(a), exponents(b)
    return tuple(sorted([RANK[k] for k in RANK for _ in range(max(ea.get(k, 0), eb.get(k, 0)))], reverse=True))


_BE = {('present', 'sg', 1): 'am', ('present', 'sg', 2): 'are', ('present', 'sg', 3): 'is', ('present', 'pl', 1): 'are', ('present', 'pl', 2): 'are', ('present', 'pl', 3): 'are',
       ('past', 'sg', 1): 'was', ('past', 'sg', 2): 'were', ('past', 'sg', 3): 'was', ('past', 'pl', 1): 'were', ('past', 'pl', 2): 'were', ('past', 'pl', 3): 'were'}


def _form(lemma: str, tag: str, number: str, person: int) -> str:
    """One finite or non-finite form of `lemma` by Penn tag; `be` and `have` are tabled, the rest come from lemminflect (irregulars included)."""
    if lemma == 'be':
        return {'VB': 'be', 'VBN': 'been', 'VBG': 'being'}.get(tag) or _BE[('past' if tag == 'VBD' else 'present', number, person)]
    if lemma == 'have':
        return {'VB': 'have', 'VBN': 'had', 'VBG': 'having', 'VBD': 'had'}.get(tag) or ('has' if (number, person) == ('sg', 3) else 'have')
    if tag == 'VB':
        return lemma
    if tag == 'VBP':
        return lemma
    try:
        from lemminflect import getInflection
        f = getInflection(lemma, tag=tag)
        if f: return f[0]
    except Exception:                                   # noqa: BLE001
        pass
    return lemma + {'VBD': 'ed', 'VBN': 'ed', 'VBG': 'ing', 'VBZ': 's'}[tag]


def conjugates(lemma: str, spec='present', number: str = 'sg', person: int = 3) -> List[dict]:
    """The realised verb group of `lemma`: a list of {'word', 'tag', 'factor'} in order (affix hopping over the factor list).
    conjugates('walk', 'past perfect') -> had|walked ; ('see','future progressive') -> will|be|seeing ; ('go','present','sg',3) -> goes."""
    d = parse_tense(spec)
    if d['tense'] == 'base':
        return [{'word': lemma, 'tag': 'VB', 'factor': 'V'}]
    heads = ([('MODAL', d['modal'])] if d['modal'] else []) + ([('PERF', 'have')] if d['perf'] else []) + ([('PROG', 'be')] if d['prog'] else []) + [('V', lemma)]
    out, pending = [], None                               # pending = the tag the NEXT word must take (from a PERF or PROG factor above it)
    for i, (f, w) in enumerate(heads):
        if f == 'MODAL':                                  # the modal carries the tense and is itself uninflected; what follows is a bare stem
            out.append({'word': w, 'tag': 'MD', 'factor': f}); pending = 'VB'; continue
        if pending is None:                               # first verbal word: it carries TENSE
            tag = 'VBD' if d['tense'] == 'past' else ('VBZ' if (number, person) == ('sg', 3) else 'VBP')
        else:
            tag = pending
        out.append({'word': _form(w, tag, number, person), 'tag': tag, 'factor': f})
        pending = {'PERF': 'VBN', 'PROG': 'VBG'}.get(f, 'VB')
    return out


def inflection_frame(spec='present', lemma: str = 'walk', number: str = 'sg', person: int = 3) -> dict:
    """The tense layer of one verb: its rank word, its Lyndon factors, the surface words, and the two marker codes sedenion_window writes
    (`tense` = the tense carrier, `conj` = the form of the main verb)."""
    d = parse_tense(spec); grp = conjugates(lemma, spec, number, person)
    if d['mood'] in ('imperative', 'base'): mt = d['mood']
    elif d['modal'] == 'will': mt = 'future'
    elif d['modal'] == 'would': mt = 'conditional'
    elif d['tense'] == 'present' and d['perf'] and not d['prog']: mt = 'perfect'
    elif d['tense'] == 'present' and d['prog'] and not d['perf']: mt = 'progressive'
    else: mt = d['tense']
    mtag = grp[-1]['tag']
    conj = {'VBZ': '3sg', 'VBP': 'base', 'VBD': 'past', 'VBN': 'pastpart', 'VBG': 'ing', 'VB': 'base'}[mtag]
    return {'word': verb_group(spec), 'factors': factors(spec), 'surface': [g['word'] for g in grp], 'group': grp, 'tense': mt, 'conj': conj}


# ── a paragraph's tense stream, with the necklace and primitive-root tools ───────────────────────────────────────────────────────────────
TENSE_CYCLE = ('past', 'present', 'future')              # the lemniscate's three stations: past lobe, the node (now), future lobe


def rotate_tense(t: str, k: int = 1) -> str:
    """Conjugation in the COMBINATORIAL sense (rotation) on the tense cycle: past -> present -> future -> past."""
    return TENSE_CYCLE[(TENSE_CYCLE.index(t) + k) % 3] if t in TENSE_CYCLE else t


def tense_phrases(stream: Sequence[str]) -> List[Tuple]:
    """Duval factorisation of a paragraph's tense stream (tenses ranked past < present < future): the runs the paragraph is built from."""
    rk = {t: i for i, t in enumerate(TENSE_CYCLE)}
    return duval([rk.get(t, 1) for t in stream])


def tense_monotony(stream: Sequence[str]) -> dict:
    """(primitive root, repeats) of the stream: root length 1 with repeats > 1 means one tense all the way through (nothing moved)."""
    rk = {t: i for i, t in enumerate(TENSE_CYCLE)}
    u, k = primitive_root([rk.get(t, 1) for t in stream])
    return {'root': [TENSE_CYCLE[i] for i in u], 'repeats': k, 'flat': len(u) == 1 and k > 1}


def verify(max_len: int = 10, alphabet: Sequence = "ab") -> dict:
    """Exhaustive check of Chen-Fox-Lyndon over every word of length <= ``max_len`` on ``alphabet``.

    Checks, for each word: the factors concatenate to the word, each factor is Lyndon, the factors
    are non-increasing, and the number of Lyndon words of each length equals (1/n) sum mu(d) k^(n/d).
    """
    def mu(n):
        r, m, p = 1, n, 2
        while p * p <= m:
            if m % p == 0:
                m //= p
                if m % p == 0:
                    return 0
                r = -r
            p += 1
        return -r if m > 1 else r
    k = len(alphabet)
    words = bad = 0
    count = {}
    for n in range(1, max_len + 1):
        for w in product(alphabet, repeat=n):
            words += 1
            f = duval(w)
            ok = (tuple(x for l in f for x in l) == w and all(is_lyndon(l) for l in f)
                  and all(f[i] >= f[i + 1] for i in range(len(f) - 1)))
            bad += not ok
            count[n] = count.get(n, 0) + is_lyndon(w)
    formula = {n: sum(mu(d) * k ** (n // d) for d in range(1, n + 1) if n % d == 0) // n for n in range(1, max_len + 1)}
    return {"words_checked": words, "failures": bad, "lyndon_counts": count, "counts_match_formula": count == formula}


if __name__ == "__main__":
    print(verify())
    for s in ("banana", "abracadabra", "the cat sat on the mat".split()):
        print(s if isinstance(s, str) else " ".join(s), "->", ["".join(x) if isinstance(s, str) else " ".join(x) for x in duval(s)])
    for sp in ("present", "past", "future", "past perfect", "future progressive", "conditional", "present perfect progressive"):
        print("%-28s" % sp, factors(sp), " ".join(g["word"] for g in conjugates("see", sp)))
