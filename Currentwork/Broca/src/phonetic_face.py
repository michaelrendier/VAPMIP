#!/usr/bin/env python3
"""
phonetic_face.py — the phonetic face. ARPABET articulatory features as a
16-dimensional space, drop-in for DisCoCat's MeaningSpace.

THE THIRD FACE. As of 2026-07-28 the monad had:
    edges     — the A-matrix. Real. 1.9M co-occurrence edges after the
                addressing fix.
    semantic  — nominal only. E comes from the base-95 Horner address of the
                SPELLING, so "semantic depth" is orthographic.
    phonetic  — nothing. No phoneme layer anywhere in PtolC, monad.c, or any
                *_monad.py. Only a proposal in Ainulindale/wiki/fractals
                (cos=phonetic, tan=syntactic, sin=semantic) and an
                "IPA length proxy" comment in legacy PtolemyDesktop.

This builds the missing one.

────────────────────────────────────────────────────────────────────────────
WHY THIS IS DIFFERENT FROM EVERYTHING THAT FAILED TODAY
────────────────────────────────────────────────────────────────────────────
Four constructions failed (DisCoCat-harmonic, VSA, L_(I|O) on the tower,
L_(I|O) two-trees) and all four died the same way: vectors built from
character codes carry LENGTH and POSITION, not meaning. Measured:
project() = cbar*W(n,k,sigma) + D(content), content 2-3% of signal, cosine
tracking |len(a)-len(b)| and nothing else.

Phonemes are not characters. CMUdict is measured linguistic data — how words
are actually pronounced — and English orthography is famously NOT its
phonology ('though/through/tough', 'knight'). So this substrate is
independent of spelling in a way nothing tried today was.

The 16 features below are ARTICULATORY: real, standard distinctive features
(voicing, place, manner, vowel height/backness/rounding, stress). They are
not a projection of anything onto 16 dimensions — there happen to be
16 natural feature contrasts, and the sedenion basis has 16 slots. Nothing
was padded or truncated to make that fit.

LENGTH BIAS IS DESIGNED OUT: a word's vector is the MEAN feature vector over
its phonemes, not the sum. A mean is length-normalised by construction, so
the failure mode that killed the previous four cannot recur through the same
channel. verify_no_length_bias() tests this rather than assuming it.

PRIME DIRECTIVE #1: nothing fitted. Features are standard phonetics, taken
from the phoneme inventory, not tuned. No weights learned.
PRIME DIRECTIVE #2: words absent from CMUdict return the honest zero vector
— NO grapheme fallback. A spelling-based fallback would silently reimport
the exact signal this face exists to escape and would corrupt the
comparison.

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import os
import sys
from typing import Dict, List, Sequence, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from ValaQuenta.modules.translator_discocat.maths import MeaningSpace  # noqa: E402
from ValaQuenta.modules.translator_common.maths import cosine, norm    # noqa: E402

N_DIM = 16

# ── The 16 articulatory features (the sedenion slots) ────────────────────────
FEATURES: Tuple[str, ...] = (
    'vocalic',      # 0  is a vowel
    'consonantal',  # 1  true consonant (obstruent/nasal/liquid)
    'voiced',       # 2  vocal folds vibrating
    'nasal',        # 3  velum lowered
    'continuant',   # 4  airflow not fully stopped
    'strident',     # 5  high-amplitude turbulence (s, z, f, v, sh, ch, jh)
    'labial',       # 6  place: lips
    'coronal',      # 7  place: tongue tip/blade
    'dorsal',       # 8  place: tongue body
    'glottal',      # 9  place: glottis
    'high',         # 10 vowel height: high
    'low',          # 11 vowel height: low
    'back',         # 12 vowel backness
    'round',        # 13 lip rounding
    'tense',        # 14 tense vs lax
    'stressed',     # 15 primary stress on this phoneme
)
assert len(FEATURES) == N_DIM

_V = 'vocalic'; _C = 'consonantal'
# phoneme -> set of features that are 1 (stress handled separately)
ARPABET: Dict[str, Tuple[str, ...]] = {
    # ── vowels ──────────────────────────────────────────────────────────────
    'AA': (_V, 'voiced', 'continuant', 'low', 'back', 'tense'),
    'AE': (_V, 'voiced', 'continuant', 'low'),
    'AH': (_V, 'voiced', 'continuant'),
    'AO': (_V, 'voiced', 'continuant', 'back', 'round', 'tense'),
    'AW': (_V, 'voiced', 'continuant', 'low', 'back', 'round'),
    'AY': (_V, 'voiced', 'continuant', 'low', 'high'),
    'EH': (_V, 'voiced', 'continuant'),
    'ER': (_V, 'voiced', 'continuant', 'coronal'),
    'EY': (_V, 'voiced', 'continuant', 'tense'),
    'IH': (_V, 'voiced', 'continuant', 'high'),
    'IY': (_V, 'voiced', 'continuant', 'high', 'tense'),
    'OW': (_V, 'voiced', 'continuant', 'back', 'round', 'tense'),
    'OY': (_V, 'voiced', 'continuant', 'back', 'round', 'high'),
    'UH': (_V, 'voiced', 'continuant', 'high', 'back', 'round'),
    'UW': (_V, 'voiced', 'continuant', 'high', 'back', 'round', 'tense'),
    # ── stops ───────────────────────────────────────────────────────────────
    'P':  (_C, 'labial'),
    'B':  (_C, 'voiced', 'labial'),
    'T':  (_C, 'coronal'),
    'D':  (_C, 'voiced', 'coronal'),
    'K':  (_C, 'dorsal'),
    'G':  (_C, 'voiced', 'dorsal'),
    # ── affricates ──────────────────────────────────────────────────────────
    'CH': (_C, 'strident', 'coronal'),
    'JH': (_C, 'voiced', 'strident', 'coronal'),
    # ── fricatives ──────────────────────────────────────────────────────────
    'F':  (_C, 'continuant', 'strident', 'labial'),
    'V':  (_C, 'voiced', 'continuant', 'strident', 'labial'),
    'TH': (_C, 'continuant', 'coronal'),
    'DH': (_C, 'voiced', 'continuant', 'coronal'),
    'S':  (_C, 'continuant', 'strident', 'coronal'),
    'Z':  (_C, 'voiced', 'continuant', 'strident', 'coronal'),
    'SH': (_C, 'continuant', 'strident', 'coronal'),
    'ZH': (_C, 'voiced', 'continuant', 'strident', 'coronal'),
    'HH': ('continuant', 'glottal'),
    # ── nasals ──────────────────────────────────────────────────────────────
    'M':  (_C, 'voiced', 'nasal', 'labial'),
    'N':  (_C, 'voiced', 'nasal', 'coronal'),
    'NG': (_C, 'voiced', 'nasal', 'dorsal'),
    # ── liquids / glides ────────────────────────────────────────────────────
    'L':  (_C, 'voiced', 'continuant', 'coronal'),
    'R':  (_C, 'voiced', 'continuant', 'coronal'),
    'W':  ('voiced', 'continuant', 'labial', 'dorsal', 'round'),
    'Y':  ('voiced', 'continuant', 'dorsal', 'high'),
}

_FIDX = {f: i for i, f in enumerate(FEATURES)}


def phoneme_vector(phone: str) -> List[float]:
    """
    ARPABET symbol (with optional trailing stress digit) -> 16 features.
    Unknown symbols return the zero vector rather than a guess.
    """
    stress = 0.0
    base = phone
    if base and base[-1].isdigit():
        stress = 1.0 if base[-1] == '1' else 0.0   # primary stress only
        base = base[:-1]
    v = [0.0] * N_DIM
    feats = ARPABET.get(base.upper())
    if feats is None:
        return v
    for f in feats:
        v[_FIDX[f]] = 1.0
    v[_FIDX['stressed']] = stress
    return v


class PhoneticSpace(MeaningSpace):
    """
    MeaningSpace over articulatory features. Drop-in: same
    noun()/verb_tensor()/contract(), so the pregroup layer is untouched.
    """

    def __init__(self, mode: str = 'kronecker'):
        super().__init__()
        if mode not in ('kronecker', 'relational'):
            raise ValueError("mode must be kronecker|relational")
        self.mode = mode
        from nltk.corpus import cmudict
        self._dict = cmudict.dict()
        self._cache: Dict[str, List[float]] = {}

    def pronunciation(self, token: str) -> List[str]:
        """First CMUdict pronunciation, or [] if the word is not listed."""
        p = self._dict.get(token.lower())
        return p[0] if p else []

    def noun(self, token: str) -> List[float]:
        """
        MEAN articulatory feature vector across the word's phonemes.

        Mean, not sum: a sum grows with phoneme count and would reintroduce
        the length dominance that killed every earlier attempt. The mean is
        the word's average articulatory profile and is length-free by
        construction.

        Out-of-dictionary -> zero vector. Deliberately NO grapheme fallback.
        """
        if token in self._cache:
            return self._cache[token]
        phones = self.pronunciation(token)
        if not phones:
            v = [0.0] * N_DIM
        else:
            acc = [0.0] * N_DIM
            for p in phones:
                pv = phoneme_vector(p)
                for i in range(N_DIM):
                    acc[i] += pv[i]
            v = [x / len(phones) for x in acc]
        self._cache[token] = v
        return v

    def verb_tensor(self, token: str) -> List[List[List[float]]]:
        v = self.noun(token)
        if self.mode == 'kronecker':
            return [[[v[i] * v[j] * v[k] for k in range(N_DIM)]
                     for j in range(N_DIM)] for i in range(N_DIM)]
        # relational: outer products over the word's own phoneme sequence,
        # so the tensor carries the word's internal articulatory transitions
        T = [[[0.0] * N_DIM for _ in range(N_DIM)] for _ in range(N_DIM)]
        phones = [phoneme_vector(p) for p in self.pronunciation(token)]
        for a, b in zip(phones, phones[1:]):
            for i in range(N_DIM):
                if a[i] == 0.0:
                    continue
                for j in range(N_DIM):
                    if v[j] == 0.0:
                        continue
                    Tij = T[i][j]
                    aij = a[i] * v[j]
                    for k in range(N_DIM):
                        Tij[k] += aij * b[k]
        return T

    def coverage(self, words: Sequence[str]) -> Dict[str, object]:
        missing = [w for w in words if not self.pronunciation(w)]
        return {'requested': len(words), 'in_dict': len(words) - len(missing),
                'missing': missing}


# ── diagnostics ──────────────────────────────────────────────────────────────

def verify_no_length_bias(space: 'PhoneticSpace',
                          words: Sequence[str]) -> Dict[str, object]:
    """
    THE test this face exists to pass. Four earlier constructions had cosine
    tracking |len(a)-len(b)|; group similarity by phoneme-count difference
    and check it is flat.
    """
    import itertools
    from collections import defaultdict
    g = defaultdict(list)
    for a, b in itertools.combinations(words, 2):
        va, vb = space.noun(a), space.noun(b)
        if norm(va) == 0.0 or norm(vb) == 0.0:
            continue
        d = abs(len(space.pronunciation(a)) - len(space.pronunciation(b)))
        g[d].append(abs(cosine(va, vb)))
    rows = {d: {'n': len(v), 'mean_abs_cos': sum(v) / len(v)}
            for d, v in sorted(g.items())}
    means = [r['mean_abs_cos'] for r in rows.values() if r['n'] >= 3]
    return {'by_phoneme_len_diff': rows,
            'spread': (max(means) - min(means)) if means else None}


def minimal_pairs_check(space: 'PhoneticSpace') -> List[Dict[str, object]]:
    """
    Sanity: words differing by ONE phoneme should be very close; words that
    LOOK alike but sound different should not be. The second group is the
    real test that this is phonetic and not orthographic.
    """
    out = []
    for a, b, kind in [('cat', 'bat', 'minimal pair (1 phoneme)'),
                       ('pin', 'bin', 'minimal pair (voicing)'),
                       ('sit', 'seat', 'minimal pair (vowel tense)'),
                       ('though', 'tough', 'SPELLED alike, sound different'),
                       ('know', 'now', 'SPELLED alike, sound different'),
                       ('eight', 'ate', 'SPELLED differently, HOMOPHONE')]:
        va, vb = space.noun(a), space.noun(b)
        out.append({'a': a, 'b': b, 'kind': kind,
                    'cos': cosine(va, vb) if norm(va) and norm(vb) else None,
                    'pron_a': ' '.join(space.pronunciation(a)),
                    'pron_b': ' '.join(space.pronunciation(b))})
    return out


def _main(argv: List[str]) -> int:
    import itertools
    print("phonetic_face.py — the third face")
    print("=" * 74)
    sp = PhoneticSpace()
    print(f"\nCMUdict entries: {len(sp._dict)}   features: {N_DIM}")

    words = ['hot', 'cold', 'up', 'down', 'light', 'dark', 'stone', 'river',
             'engine', 'copper', 'quiet', 'orbit', 'iron', 'garden', 'day',
             'night', 'good', 'bad', 'true', 'false', 'man', 'dog', 'water']
    cov = sp.coverage(words)
    print(f"coverage: {cov['in_dict']}/{cov['requested']}"
          + (f"   missing: {cov['missing']}" if cov['missing'] else "  (all present)"))

    print("\n[1] articulatory vectors")
    for w in ['hot', 'cold']:
        print(f"    {w:6} {' '.join(sp.pronunciation(w)):20} "
              f"{[round(x,2) for x in sp.noun(w)]}")

    print("\n[2] LENGTH BIAS — the failure mode of all four previous attempts")
    lb = verify_no_length_bias(sp, words)
    for d, r in lb['by_phoneme_len_diff'].items():
        print(f"    |phonemes(a)-phonemes(b)| = {d}:  mean|cos| = "
              f"{r['mean_abs_cos']:.6f}   (n={r['n']})")
    print(f"    spread across groups = {lb['spread']:.6f}"
          f"   (character-code encoder spread was 0.994 -> 0.868)")

    print("\n[3] is it phonetic or orthographic?")
    for r in minimal_pairs_check(sp):
        c = f"{r['cos']:+.4f}" if r['cos'] is not None else "n/a"
        print(f"    {r['a']:7}/{r['b']:7} cos={c}  {r['kind']}")
        print(f"      {r['pron_a']:22} vs {r['pron_b']}")

    print("\n[4] crowding vs the other two faces (lower = more separable)")
    cs = [abs(cosine(sp.noun(a), sp.noun(b)))
          for a, b in itertools.combinations(words, 2)
          if norm(sp.noun(a)) and norm(sp.noun(b))]
    print(f"    phonetic      mean|cos| = {sum(cs)/len(cs):.6f}")
    print(f"    (harmonic 0.981953, co-occurrence 0.548129 on a similar list)")
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
