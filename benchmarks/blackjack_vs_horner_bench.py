#!/usr/bin/env python3
"""
VAPMIP/benchmarks/blackjack_vs_horner_bench.py
===============================================
Tests the proposed "Blackjack subgroup" (F21 = 7:3, normalizer of a
Sylow-7 subgroup of PSL(2,7)) box-kite-native indexer against plain
Horner-summing, per Cody's 2026-09-25 request: "how would the boxkite
work instead of horner-summing. need a benchmark."

Two questions, both answered here, not assumed:

1. Does composing a word of F21 elements (the "run it on the boxkite"
   reading) stay lossless? NO — F21 has only 21 elements, so composing
   any sequence of them collapses to one of at most 21 final states.
   Any two digit-sequences longer than that pigeonhole bound necessarily
   collide. Demonstrated concretely below, not just argued.

2. Used the only way that DOES stay lossless -- as a size-21 digit
   ALPHABET for ordinary bijective-base Horner encoding (keeping the full
   digit sequence, never composing it away) -- is it faster or smaller
   than the plain keyboard-charset (base-97) baseline
   (`hyperwebster_baseline_bench.py`)? Measured below.

Verdict, from this run: base-21 needs ~1.8-2x more digits than base-97 for
the same content (smaller base = more digits for the same information),
AND is measurably slower to encode/decode (extra byte->base21 conversion
step plus more big-integer digit operations). The Blackjack subgroup is
not a viable direct replacement for Horner-summing as an exact, lossless
per-chunk indexer.
"""

import time
import itertools


# ── Build F21 concretely: {x -> a*x+b mod 7 : a in {1,2,4}, b in Z/7} ──────

def affine_perm(a, b):
    return tuple((a * x + b) % 7 for x in range(7))


F21 = sorted(set(affine_perm(a, b) for a in (1, 2, 4) for b in range(7)))
IDENTITY = tuple(range(7))


def compose(p, q):
    """p after q."""
    return tuple(p[q[x]] for x in range(7))


def verify_group():
    closed = all(compose(p, q) in F21 for p in F21 for q in F21)
    has_inverses = all(any(compose(p, q) == IDENTITY for q in F21) for p in F21)
    return {"size": len(F21), "closed": closed, "has_inverses": has_inverses}


def compose_word(indices):
    result = IDENTITY
    for i in indices:
        result = compose(F21[i], result)
    return result


def find_collision(max_length=3):
    """Pigeonhole: with 21 states, sequences of length >= a small bound
    must repeat. Finds the first concrete instance by brute force."""
    seen = {}
    for length in range(1, max_length + 1):
        for combo in itertools.product(range(21), repeat=length):
            r = compose_word(combo)
            if r in seen and seen[r] != combo:
                return {"seq_a": seen[r], "seq_b": combo, "final_state": r}
            seen.setdefault(r, combo)
    return None


# ── Bijective base-N Horner (shared core for both bases) ──────────────────

def horner_encode(digits, base):
    idx = 0
    for d in digits:
        idx = idx * base + d
    return idx


def horner_decode(idx, length, base):
    chars = []
    for _ in range(length):
        chars.append(idx % base)
        idx //= base
    chars.reverse()
    return chars


def to_base21_digits(text):
    n = int.from_bytes(text.encode("utf-8"), "big")
    if n == 0:
        return [0]
    digits = []
    while n > 0:
        digits.append(n % 21)
        n //= 21
    digits.reverse()
    return digits


KEYBOARD97 = ("`1234567890-=\tqwertyuiop[]\\asdfghjkl;'\nzxcvbnm,./ ~!@#$%^&*()_+"
              "QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?")
_IDX97 = {c: i for i, c in enumerate(KEYBOARD97)}

SAMPLE = ("The bee's flight has no airfoil in the aircraft-wing sense; it stays "
          "aloft by stalling and re-stalling its wings on every stroke, shedding "
          "leading-edge vortices fast enough that lift never fully collapses.")


def bench_sizes(sizes=(140, 500, 1000, 2000)):
    rows = []
    for size in sizes:
        text = (SAMPLE * (size // len(SAMPLE) + 1))[:size]

        t0 = time.perf_counter()
        digits21 = to_base21_digits(text)
        addr21 = horner_encode(digits21, 21)
        t1 = time.perf_counter()
        back21 = horner_decode(addr21, len(digits21), 21)
        t2 = time.perf_counter()
        assert back21 == digits21

        t3 = time.perf_counter()
        digits97 = [_IDX97.get(c, 0) for c in text]
        addr97 = horner_encode(digits97, 97)
        t4 = time.perf_counter()
        back97 = horner_decode(addr97, len(digits97), 97)
        t5 = time.perf_counter()
        assert back97 == digits97

        rows.append({
            "chars": size,
            "n_digits_21": len(digits21), "bits_21": addr21.bit_length(),
            "enc_ms_21": 1000 * (t1 - t0), "dec_ms_21": 1000 * (t2 - t1),
            "n_digits_97": len(digits97), "bits_97": addr97.bit_length(),
            "enc_ms_97": 1000 * (t4 - t3), "dec_ms_97": 1000 * (t5 - t4),
        })
    return rows


if __name__ == "__main__":
    g = verify_group()
    print(f"F21 verified: size={g['size']} closed={g['closed']} has_inverses={g['has_inverses']}")

    coll = find_collision()
    print(f"\nCollision under composition (word -> single final permutation):")
    print(f"  sequence A {coll['seq_a']} and sequence B {coll['seq_b']} "
          f"both compose to {coll['final_state']}")
    print(f"  (pigeonhole: only {len(F21)} possible final states -- composing "
          f"a word ALWAYS discards length/order information beyond that bound)")

    print(f"\n{'chars':>6} | {'base21 digits':>13} {'bits':>6} {'enc_ms':>8} {'dec_ms':>8} "
          f"| {'base97 digits':>13} {'bits':>6} {'enc_ms':>8} {'dec_ms':>8}")
    for r in bench_sizes():
        print(f"{r['chars']:>6} | {r['n_digits_21']:>13} {r['bits_21']:>6} "
              f"{r['enc_ms_21']:>8.3f} {r['dec_ms_21']:>8.3f} | "
              f"{r['n_digits_97']:>13} {r['bits_97']:>6} "
              f"{r['enc_ms_97']:>8.3f} {r['dec_ms_97']:>8.3f}")
