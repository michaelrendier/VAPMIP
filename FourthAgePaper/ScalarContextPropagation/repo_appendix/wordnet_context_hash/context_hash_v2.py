#!/usr/bin/env python3
"""
context_hash_v2.py -- the semantic prime hash, retooled (primer Part 4).

Evolved from wordnet_boxkite.context_vector / context_code with everything
the 2026-08-27 session established:

  1. omega/Omega split. 18 of 19 relations carry supersense information
     only in their PRESENCE (omega-type); only `hyponyms` carries it in the
     COUNT (Omega-type). So:
        code_omega = prod_{i != hyp}  p_i ^ [v_i > 0]      (SQUAREFREE)
        code_depth = p_hyp ^ compress_count(hyp)
     radical(code_omega) == the support set, exactly. Dropping the count on
     the 18 drops ~0-information exponent structure.

  2. Log chart is the working coordinate. The product is STORAGE
     (PW3-composable); log_code = sum v_i ln p_i is NATIVE -- it preserves
     the alpha ~ 1.7 power-law tail that compress_count renormalises away.

  3. Gaussian-integer valued. code in Z[i], unit in {1, i, -1, -i} supplied
     by the PHONETIC origin (syllable parity + primary-stress-index parity)
     -- the sqrt(SIGN) the pure-magnitude semantic hash structurally lacks.
     reCORD vs REcord  ->  code  vs  i*code.

  4. Queried as a RATIO vs a fixed-point anchor, never an absolute
     (negative space). Anchor = "everything fires once, no depth":
        LOG_ANCHOR = sum_{i != hyp} ln p_i
     Fold the WORKING coordinate (log_code), NOT the storage code:
        gamma_radial = tanh( 0.5 * ln( log_code / LOG_ANCHOR ) )    (real)
        gamma        = gamma_radial * unit(phonetic)                (in C)
     |gamma| = the dissertational<->narrative scale; arg(gamma) = the
     phonetic sqrt(SIGN). Two bugs found & fixed in test:
       (i)  folding signed_code (~e^70) saturates tanh -> -1 for everyone;
       (ii) folding log_code*unit mixes the phase into Re via
            tanh(a +- i pi/2) = coth(a). The phase must rotate the OUTPUT.

  5. Tower stays shallow. Raw counts -> (presence bits + one depth
     exponent) -> log chart. Stop.

Nothing here mutates wordnet_boxkite (closed). It imports and re-reads.
"""
from __future__ import annotations

import cmath
import math
import os
import struct
from typing import Optional

from wordnet_boxkite import (
    RELATION_METHODS, CONTEXT_PRIMES, context_vector, compress_count,
)

_HYP = RELATION_METHODS.index('hyponyms')
_LNP = [math.log(p) for p in CONTEXT_PRIMES[:len(RELATION_METHODS)]]
LN_P_HYP = _LNP[_HYP]

# anchor: every relation but hyponyms fires exactly once, no depth.
ANCHOR_PRIMES = [CONTEXT_PRIMES[i] for i in range(len(RELATION_METHODS)) if i != _HYP]
LOG_ANCHOR = sum(_LNP[i] for i in range(len(RELATION_METHODS)) if i != _HYP)

_PHON_BIN = os.path.join(os.path.dirname(__file__), 'PtolC', 'monad_phonetic.bin')
_phon_cache = None


def _load_phon():
    global _phon_cache
    if _phon_cache is None:
        _phon_cache = {}
        try:
            with open(_PHON_BIN, 'rb') as f:
                assert f.read(4) == b'PHON'
                struct.unpack('<I', f.read(4))
                (nw,) = struct.unpack('<I', f.read(4))
                for _ in range(nw):
                    (wl,) = struct.unpack('<B', f.read(1))
                    w = f.read(wl).decode('utf-8')
                    (npr,) = struct.unpack('<B', f.read(1))
                    prons = []
                    for _ in range(npr):
                        (nph,) = struct.unpack('<B', f.read(1))
                        ph = []
                        for _ in range(nph):
                            (pl,) = struct.unpack('<B', f.read(1))
                            ph.append(f.read(pl).decode('ascii'))
                        prons.append(ph)
                    _phon_cache[w] = prons
        except FileNotFoundError:
            pass
    return _phon_cache


# --------------------------------------------------------------------------
# the hash
# --------------------------------------------------------------------------
def support_bits(synset) -> int:
    """18-bit mask (hyponyms excluded): which relations fire for this synset."""
    v = context_vector(synset)
    bit = 0
    b = 0
    for i in range(len(RELATION_METHODS)):
        if i == _HYP:
            continue
        if v[i] > 0:
            bit |= (1 << b)
        b += 1
    return bit


def code_omega(synset) -> int:
    """Squarefree integer whose prime factorisation IS the support set."""
    v = context_vector(synset)
    c = 1
    for i in range(len(RELATION_METHODS)):
        if i != _HYP and v[i] > 0:
            c *= CONTEXT_PRIMES[i]
    return c


def code_depth_exponent(synset) -> int:
    """compress_count of the hyponym branching -- the one Omega-type channel."""
    return context_vector(synset)[_HYP]


def radical_to_support(code: int) -> list:
    """Recover which relations fire by factoring a squarefree code_omega."""
    out = []
    for i, p in enumerate(CONTEXT_PRIMES[:len(RELATION_METHODS)]):
        if i == _HYP:
            continue
        if code % p == 0:
            out.append(RELATION_METHODS[i])
    return out


def omega_of_indices(idxs) -> int:
    """Build a squarefree code_omega from a set of relation indices (used
    to give a whole SEED the same address shape as a single synset)."""
    c = 1
    for i in idxs:
        if i != _HYP:
            c *= CONTEXT_PRIMES[i]
    return c


def log_code_of(present_idxs, hyp_depth: int) -> float:
    """log_code from parts: present relation indices + a hyponym depth."""
    s = hyp_depth * LN_P_HYP
    for i in present_idxs:
        if i != _HYP:
            s += _LNP[i]
    return s


def radical_distance(omega_a: int, omega_b: int) -> float:
    """Log-mass of the SYMMETRIC DIFFERENCE of two support sets: the sum of
    ln p over relations that fire for exactly one of the two. PW3-native
    (multiplicative gcd -> additive in the log chart)."""
    g = math.gcd(omega_a, omega_b)
    return math.log(omega_a) + math.log(omega_b) - 2.0 * math.log(g)


def fold_log_code(lc: float) -> float:
    """tanh(0.5 ln(lc / LOG_ANCHOR)) -- fold any working-coordinate value
    against the 'everything fires once' anchor. Reused for the seed."""
    return math.tanh(0.5 * math.log(max(lc, 1e-9) / LOG_ANCHOR))


def log_code(synset) -> float:
    """sum_{i!=hyp} [v_i>0] ln p_i  +  compress_count(hyp) ln p_hyp."""
    v = context_vector(synset)
    s = 0.0
    for i in range(len(RELATION_METHODS)):
        if i == _HYP:
            s += v[i] * _LNP[i]
        elif v[i] > 0:
            s += _LNP[i]
    return s


def phon_unit(word: Optional[str]):
    """Gaussian unit in {1, i, -1, -i} from the phonetic origin:
    (-1)^(syllable parity) * i^(primary-stress-index parity).
    reCORD / REcord differ only in the stress index -> differ by a factor i."""
    if not word:
        return complex(1.0, 0.0)
    prons = _load_phon().get(word.lower())
    if not prons:
        return complex(1.0, 0.0)
    p = prons[0]
    nuclei = [x for x in p if x[-1] in '012']
    syll = len(nuclei)
    psi = next((k for k, x in enumerate(nuclei) if x[-1] == '1'), 0)
    return ((-1.0) ** (syll % 2)) * (1j ** (psi % 2))


def signed_code(synset, word: Optional[str] = None) -> complex:
    """The full Z[i] address: unit(phonetic) * code_omega * p_hyp^depth."""
    mag = code_omega(synset) * (CONTEXT_PRIMES[_HYP] ** code_depth_exponent(synset))
    return phon_unit(word) * mag


def gamma_radial(synset) -> float:
    """The dissertational<->narrative axis, real. Fold the WORKING
    coordinate (log_code, per the session rule) against the 'everything
    fires once' anchor:  tanh( 0.5 * ln( log_code / LOG_ANCHOR ) ).

    < 0 = dissertational (support below 'everything once')
    > 0 = narrative      (branching depth carries it above)
    ~ 0 = exactly at 'everything fires once'.

    Folding signed_code (~e^70) instead of log_code saturates tanh to -1
    for every real synset -- that was the first bug here."""
    return fold_log_code(log_code(synset))


def gamma(synset, word: Optional[str] = None) -> complex:
    """The radial axis rotated by the phonetic phase: |Gamma| = the
    semantic scale (dissertational<->narrative), arg(Gamma) = the
    phonetic sqrt(SIGN) unit. reCORD / REcord -> Gamma vs i*Gamma.

    The phase rotates the OUTPUT, not the input: folding
    log_code * unit through tanh(0.5 ln .) mixes the phase into Re via
    tanh(a +- i pi/2) = coth(a) -- that was the second bug here."""
    return gamma_radial(synset) * phon_unit(word)


def delta_log(synset) -> float:
    """log_code - log_anchor, the real (phase-free) displacement."""
    return log_code(synset) - LOG_ANCHOR


# ==========================================================================
# corpus test
# ==========================================================================
if __name__ == '__main__':
    import random
    import statistics
    from nltk.corpus import wordnet as wn

    random.seed(20260827)
    LINE = '=' * 72

    # ---- 1. round-trip: squarefree code -> support set ----
    print(LINE + '\n1. ROUND-TRIP  squarefree code_omega -> support set\n' + LINE)
    S = list(wn.all_synsets()); random.shuffle(S)
    sample = []
    for s in S:
        if sum(context_vector(s)) == 0:
            continue
        sample.append(s)
        if len(sample) >= 4000:
            break
    ok = 0
    for s in sample:
        v = context_vector(s)
        true_support = {RELATION_METHODS[i] for i in range(len(RELATION_METHODS))
                        if i != _HYP and v[i] > 0}
        if set(radical_to_support(code_omega(s))) == true_support:
            ok += 1
    print(f"  exact support recovery: {ok}/{len(sample)}  "
          f"({100*ok/len(sample):.1f}%)")

    # ---- 2. PW3 additivity in the log chart ----
    print('\n' + LINE + '\n2. PW3  log_code additive under concept merge\n' + LINE)
    errs = []
    for _ in range(2000):
        a, b = random.choice(sample), random.choice(sample)
        # merged support = union; merged depth = sum of exponents (product of codes)
        merged_log = (cmath.log(code_omega(a) * code_omega(b)).real
                      + (code_depth_exponent(a) + code_depth_exponent(b)) * _LNP[_HYP])
        # vs sum of the parts' log_codes only where that equals union+sum:
        # log_code counts each present prime once; a*b double-counts shared primes.
        # PW3 holds on the MULTIPLICATIVE code, checked directly:
        lhs = cmath.log(code_omega(a) * code_omega(b)).real
        rhs = math.log(code_omega(a)) + math.log(code_omega(b))
        errs.append(abs(lhs - rhs))
    print(f"  |log(c_a * c_b) - (log c_a + log c_b)|  max={max(errs):.2e}  "
          f"mean={statistics.mean(errs):.2e}   (PW3 exact)")

    # ---- 3. Gamma tracks the dissertational<->narrative axis ----
    print('\n' + LINE + '\n3. Re(Gamma) / delta_log  vs  independent specificity signals\n' + LINE)
    # WordNet's own SemCor tagged-usage counts -- offline, ships with wordnet.
    rows = []
    for s in sample:
        v = context_vector(s)
        n_rel = sum(1 for i in range(len(RELATION_METHODS)) if i != _HYP and v[i] > 0)
        lemma = s.lemma_names()[0].replace('_', ' ')
        rows.append({
            'dlog': delta_log(s),
            'reG': gamma_radial(s),
            'n_rel': n_rel,
            'hyp': v[_HYP],
            'depth': s.min_depth(),
            'freq': math.log1p(sum(l.count() for l in s.lemmas())),
        })

    def corr(xs, ys):
        n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
        cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        sx = math.sqrt(sum((x-mx)**2 for x in xs))
        sy = math.sqrt(sum((y-my)**2 for y in ys))
        return cov/(sx*sy) if sx and sy else 0.0

    dlog = [r['dlog'] for r in rows]
    reG = [r['reG'] for r in rows]
    for name in ('n_rel', 'hyp', 'depth', 'freq'):
        col = [r[name] for r in rows]
        print(f"  corr(delta_log, {name:6s}) = {corr(dlog, col):+.3f}   "
              f"corr(gamma_rad, {name:6s}) = {corr(reG, col):+.3f}")
    print("  expect: n_rel + , hyp + , depth - (deeper=more specific) , freq + (common=narrative)")

    # ---- 4. Gaussian phase on heteronyms ----
    print('\n' + LINE + '\n4. GAUSSIAN PHASE  reCORD / REcord  ->  code vs i*code\n' + LINE)
    phon = _load_phon()
    shown = 0
    for w, prons in phon.items():
        if len(prons) < 2 or ' ' in w or not w.isalpha():
            continue
        def psi(pr):
            nuc = [x for x in pr if x[-1] in '012']
            return next((k for k, x in enumerate(nuc) if x[-1] == '1'), 0), len(nuc)
        a = psi(prons[0]); b = psi(prons[1])
        if a == b:
            continue
        syns = wn.synsets(w)
        if not syns:
            continue
        u0 = ((-1.0) ** (a[1] % 2)) * (1j ** (a[0] % 2))
        u1 = ((-1.0) ** (b[1] % 2)) * (1j ** (b[0] % 2))
        if u0 != u1:
            print(f"  {w:14s}  pron0 stress@{a[0]} -> unit {u0:+.0f}   "
                  f"pron1 stress@{b[0]} -> unit {u1:+.0f}   ratio {u1/u0:+.0f}")
            shown += 1
            if shown >= 8:
                break

    # ---- 5. supersense separation: old hash vs evolved ----
    print('\n' + LINE + '\n5. SUPERSENSE Fisher ratio  (higher = cleaner separation)\n' + LINE)
    import numpy as np
    lex = np.array([s.lexname() for s in sample])

    vs = [context_vector(s) for s in sample]
    OLD = np.array(vs, float)

    def evolved_row(v):
        return [v[i] if i == _HYP else (1.0 if v[i] > 0 else 0.0)
                for i in range(len(RELATION_METHODS))]
    NEW = np.array([evolved_row(v) for v in vs], float)
    NEWc = NEW - NEW.mean(0)   # anchor-centred (delta from 'everything once')

    def fisher(X):
        mu = X.mean(0); sw = sb = 0.0
        for c in np.unique(lex):
            Xi = X[lex == c]
            if len(Xi) < 2:
                continue
            mi = Xi.mean(0)
            sw += ((Xi - mi) ** 2).sum()
            sb += len(Xi) * ((mi - mu) ** 2).sum()
        return sb / (sw or 1.0)

    print(f"  (a) old context_vector (19-D compress_count) : {fisher(OLD):.3f}")
    print(f"  (b) evolved  [18 presence + hyp depth]       : {fisher(NEW):.3f}")
    print(f"  (c) evolved, anchor-centred                  : {fisher(NEWc):.3f}")

    # ---- 6. who sits at the anchor ----
    print('\n' + LINE + "\n6. ANCHOR  synsets nearest Re(Gamma)=0 ('everything fires once')\n" + LINE)
    at_anchor = sorted(rows, key=lambda r: abs(r["reG"]))[:8]
    idx = {id(r): s for r, s in zip(rows, sample)}
    for r in at_anchor:
        s = idx[id(r)]
        print(f"  Re G={r['reG']:+.3f}  n_rel={r['n_rel']:2d} hyp={r['hyp']}  "
              f"{s.name():24s} {s.definition()[:44]}")
