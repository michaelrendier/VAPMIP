#!/usr/bin/env python3
"""
semantic_hash_roundtrip.py -- the round trip for the semantic / context hash,
run against the LIVE vocabulary in PtolC/monad3_c.bin.

Layers under test (Cody's model: letters = small primes, words = composites,
context = large primes, kept in SEPARATE numbers):

  1. context_code(v) = prod CONTEXT_PRIMES[i]^v[i]   -- factor back to v?
  2. context_addr    = (code, next_prime(code), delta)  -- delta recovers code?
  3. compress_count  = round(log2(count+1))  -- the KNOWN lossy step; quantify
  4. gamma fold (context_hash_v2): gamma_radial = tanh(.5 ln(log_code/ANCHOR))
        invert log_code; then: is one real enough to pin the 19-vector?
  5. spelling_code(w): Godel positional over LETTER_PRIMES[i%20] -- recover w?
  6. separability: LETTER_PRIMES (<=71) disjoint CONTEXT_PRIMES (>71) ->
        spelling_code(w) * context_code(v) factors cleanly into (word, context)

Run:  ../../../ValaQuenta/.venv/bin/python3 semantic_hash_roundtrip.py
"""
from __future__ import annotations
import math
import os
import struct
import sys
import random

VAPMIP = os.path.expanduser("~/Projects/ThePlace/VAPMIP")
sys.path.insert(0, VAPMIP)

from wordnet_boxkite import (
    LETTER_PRIMES, CONTEXT_PRIMES, RELATION_METHODS, compress_count,
    context_vector, context_code, next_prime, spelling_code,
)

STORE = os.path.join(VAPMIP, "PtolC", "monad3_c.bin")
NREL = len(RELATION_METHODS)
CP = CONTEXT_PRIMES[:NREL]
LNP = [math.log(p) for p in CP]
_HYP = RELATION_METHODS.index("hyponyms")
LOG_ANCHOR = sum(LNP[i] for i in range(NREL) if i != _HYP)


# ----------------------------------------------------- iterate the live store
def iter_store(path):
    import mmap
    f = open(path, "rb")
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    hdr = struct.Struct("<8s6I16d13Q")
    vals = hdr.unpack_from(mm, 0)
    magic, ver, n_words, n_eng, n_wn, n_phon, nnz = vals[:7]
    assert magic.rstrip(b"\x00") == b"MONAD3C", magic
    off = vals[23:]
    o_blob, o_rec, o_wn, o_phix = off[0], off[1], off[10], off[11]
    # BK record: '<I i q 19i f'  = word_off, pos, offset, v0..v18, dw   (from monad_combine _BK_STRUCT)
    from monad_combine import _BK_STRUCT
    rec = struct.Struct("<iiii")

    def name(o):
        e = mm.find(b"\x00", o_blob + o)
        return mm[o_blob + o:e].decode("utf-8", "replace")

    rows = []
    for i in range(n_words):
        noff, ei, wi, pi = rec.unpack_from(mm, o_rec + i * 16)
        w = name(noff)
        v = None
        if wi >= 0:
            e = _BK_STRUCT.unpack_from(mm, o_wn + wi * _BK_STRUCT.size)
            v = list(e[3:3 + NREL])
        rows.append((w, ei, wi, pi, v))
    return dict(ver=ver, n_words=n_words, n_eng=n_eng, n_wn=n_wn,
               n_phon=n_phon, rows=rows)


# ------------------------------------------------------------ factor over CP
def factor_cp(code):
    """recover the exponent vector of `code` over CONTEXT_PRIMES[:NREL]."""
    v = [0] * NREL
    for i, p in enumerate(CP):
        while code % p == 0:
            code //= p
            v[i] += 1
    return v, code            # residue should be 1 if code was CP-smooth


def spell_decode(code, length):
    """invert spelling_code assuming length<=20 (each position its own prime)."""
    letters = []
    for i in range(length):
        p = LETTER_PRIMES[i % len(LETTER_PRIMES)]
        e = 0
        while code % p == 0:
            code //= p
            e += 1
        letters.append(chr(ord("a") + e - 1) if 1 <= e <= 26 else "?")
    return "".join(letters), code


def main():
    S = iter_store(STORE)
    rows = S["rows"]
    with_wn = [(w, v) for (w, ei, wi, pi, v) in rows if v is not None]
    print(f"LIVE STORE  {STORE}")
    print(f"  version {S['ver']}   n_words {S['n_words']:,}   "
          f"n_eng {S['n_eng']:,}   n_wn {S['n_wn']:,}   n_phon {S['n_phon']:,}")
    print(f"  words carrying a stored 19-vector (context): {len(with_wn):,}\n")

    # ---- 1+2. context_code / context_addr round trip -----------------------
    exact_code = exact_addr = nonsmooth = 0
    maxbits = 0
    zero_vec = 0
    for w, v in with_wn:
        if not any(v):
            zero_vec += 1
        code = 1
        for p, e in zip(CP, v):
            if e:
                code *= p ** e
        v2, res = factor_cp(code)
        if res != 1:
            nonsmooth += 1
        if v2 == v:
            exact_code += 1
        addr = next_prime(code)
        delta = addr - code
        code_rt = addr - delta
        v3, _ = factor_cp(code_rt)
        if code_rt == code and v3 == v:
            exact_addr += 1
        maxbits = max(maxbits, code.bit_length())
    n = len(with_wn)
    print("[1] context_code(v) -> factor -> v")
    print(f"    exact: {exact_code:,}/{n:,}  ({exact_code/n*100:.3f}%)   "
          f"non-CP-smooth residue: {nonsmooth}   all-zero vectors: {zero_vec}")
    print(f"    largest code: {maxbits} bits\n")
    print("[2] context_addr = (code, next_prime(code), delta);  code = addr - delta")
    print(f"    exact: {exact_addr:,}/{n:,}  ({exact_addr/n*100:.3f}%)\n")

    # ---- 3. compress_count -- the known lossy step ------------------------
    print("[3] compress_count(c) = round(log2(c+1))  -- raw count -> bucket")
    buckets = {}
    for c in range(0, 4001):
        buckets.setdefault(compress_count(c), []).append(c)
    print("    bucket  raw-count range it stands for      width")
    for b in sorted(buckets)[:12]:
        lo, hi = buckets[b][0], buckets[b][-1]
        print(f"      {b:>3}   [{lo:>4} .. {hi:>4}]                    {hi-lo+1}")
    # live distribution of bucket values actually used
    from collections import Counter
    used = Counter()
    for _, v in with_wn:
        for e in v:
            used[e] += 1
    tot = sum(used.values())
    print("    live exponent-value frequency (all 19 dims, all words):")
    for b in sorted(used):
        print(f"      exp {b:>2}: {used[b]:>9,}  ({used[b]/tot*100:5.2f}%)  "
              f"stands for raw {buckets.get(b,['?'])[0]}..{buckets.get(b,['?'])[-1]}")
    print("    -> the round trip recovers the BUCKET, not the raw count. "
          "loss = width above.\n")

    # ---- 4. the gamma fold: one real vs the 19-vector -------------------
    print("[4] gamma fold  gamma_radial = tanh(0.5 ln(log_code / LOG_ANCHOR))")
    rt_err = 0.0
    logcodes = []
    vec_of_log = {}
    collisions = 0
    saturated = 0
    for w, v in with_wn:
        lc = sum(v[i] * LNP[i] for i in range(NREL))
        if lc <= 0:
            continue
        gr = math.tanh(0.5 * math.log(lc / LOG_ANCHOR))
        if abs(gr) >= 1 - 1e-15:
            saturated += 1
            continue
        lc_rt = LOG_ANCHOR * math.exp(2 * math.atanh(gr))
        rt_err = max(rt_err, abs(lc_rt - lc) / lc)
        key = round(lc, 9)
        if key in vec_of_log and vec_of_log[key] != tuple(v):
            collisions += 1
        else:
            vec_of_log.setdefault(key, tuple(v))
        logcodes.append(lc)
    uniq_log = len(set(round(x, 9) for x in logcodes))
    print(f"    log_code round trip (tanh->atanh) max rel err: {rt_err:.2e}")
    print(f"    tanh saturations (|gamma_radial| = 1): {saturated}")
    print(f"    distinct log_code values: {uniq_log:,} / {len(logcodes):,} folded")
    print(f"    distinct 19-vectors sharing an already-seen log_code: {collisions:,}")
    print(f"    -> |gamma| is lossless for log_code; log_code -> v is "
          f"{'MANY-TO-ONE' if collisions else 'injective on this vocab'}.\n")

    # ---- 5. spelling_code round trip -----------------------------------
    print("[5] spelling_code(w)  Godel positional, LETTER_PRIMES[i % 20]")
    exact_spell = le20 = gt20 = exact_le20 = 0
    for (w, ei, wi, pi, v) in rows:
        alpha = "".join(ch for ch in w.lower() if ch.isalpha())
        if not alpha:
            continue
        code = spelling_code(w)
        dec, res = spell_decode(code, len(alpha))
        ok = (dec == alpha and res == 1)
        exact_spell += ok
        if len(alpha) <= 20:
            le20 += 1
            exact_le20 += ok
        else:
            gt20 += 1
    total_alpha = le20 + gt20
    print(f"    exact word recovery: {exact_spell:,}/{total_alpha:,}  "
          f"({exact_spell/total_alpha*100:.3f}%)")
    print(f"    words <=20 alpha chars: {le20:,}  exact {exact_le20:,} "
          f"({exact_le20/max(le20,1)*100:.3f}%)")
    print(f"    words  >20 alpha chars: {gt20:,}  (prime cycle wraps -> "
          f"exponents add -> lossy)\n")

    # ---- 6. separability -------------------------------------------------
    print("[6] separability: LETTER_PRIMES max =", LETTER_PRIMES[-1],
          " CONTEXT_PRIMES min =", CONTEXT_PRIMES[0])
    sample = [r for r in rows if r[4] is not None and
              "".join(c for c in r[0] if c.isalpha()) and
              len("".join(c for c in r[0] if c.isalpha())) <= 20]
    random.seed(20260831)
    random.shuffle(sample)
    sep_ok = 0
    for (w, ei, wi, pi, v) in sample[:500]:
        alpha = "".join(c for c in w.lower() if c.isalpha())
        sc = spelling_code(w)
        cc = 1
        for p, e in zip(CP, v):
            if e:
                cc *= p ** e
        combined = sc * cc
        # split: factor letter part (<=71) and context part (>71)
        lp = 1
        rest = combined
        for p in LETTER_PRIMES:
            while rest % p == 0:
                rest //= p
                lp *= p
        # rest is now the context part
        v_rec, res = factor_cp(rest)
        w_rec, sres = spell_decode(lp, len(alpha))
        if w_rec == alpha and v_rec == v and res == 1 and sres == 1:
            sep_ok += 1
    print(f"    combined = spelling_code(w) * context_code(v), factored at 71:")
    print(f"    recovered BOTH (word, context) exactly: {sep_ok}/500\n")

    # ---- cross-check a sample against live WordNet ---------------------
    print("[x] cross-check stored 19-vector vs wordnet_boxkite.context_vector today")
    try:
        from nltk.corpus import wordnet as wn
        random.seed(11)
        chk = [r for r in rows if r[4] is not None]
        random.shuffle(chk)
        agree = tried = 0
        for (w, ei, wi, pi, v) in chk[:300]:
            ss = wn.synsets(w)
            if not ss:
                continue
            tried += 1
            if context_vector(ss[0]) == v:
                agree += 1
        print(f"    stored == freshly computed (synset[0]): {agree}/{tried}  "
              f"(mismatch = store predates a relation-set change, or a "
              f"different synset was indexed)\n")
    except Exception as e:
        print(f"    (skipped: {e})\n")


if __name__ == "__main__":
    main()
