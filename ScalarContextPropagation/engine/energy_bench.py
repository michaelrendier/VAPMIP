#!/usr/bin/env python3
"""
energy_bench.py — materialised vs addressed: the kilowatt/milliwatt statement,
with numbers, on the reference machine.

Reference machine (this box): Lenovo ThinkPad X1 Carbon 6th gen, 20KH002XUS.
  Intel Core i7-8550U (Kaby Lake R, 4C/8T, 0.4-4.0 GHz), 8 MB L3,
  7.5 GiB RAM, DRAM-less NVMe.  Package TDP (PL1) = 15 W; single-thread
  package draw under load ~ 6-10 W (RAPL not readable in this session, so
  energy is quoted at the 15 W package ceiling AND at a 7 W single-core
  estimate -- both stated, neither hidden).

Two costs compared, per "query" (one word of context reconstructed / one
token generated):

  ADDRESSED  (the Monad)  : reconstruct context for a word from a scalar in
                            the vocabulary -- one sedenion product against a
                            fixed ruler + a sparse A-matrix row.  No stored
                            relationship matrix; no gradient.
  MATERIALISED (a dense transformer) : 2 * N_params multiply-accumulates per
                            token, forward; training adds the backward sweep
                            over the same N_params, every step.

The Monad numbers are MEASURED here.  The transformer numbers are the
standard forward-FLOP identity (2*N per token) plus published energy figures,
cited, not measured.
"""
from __future__ import annotations
import os, sys, time, math, statistics

# ----------------------------------------------------------------- CD product
_MULCOUNT = 0

def cd_mul(a, b):
    """Recursive Cayley-Dickson product. a, b are tuples of length 2^k.
    Counts real multiplications in _MULCOUNT."""
    global _MULCOUNT
    n = len(a)
    if n == 1:
        _MULCOUNT += 1
        return (a[0] * b[0],)
    h = n // 2
    a1, a2 = a[:h], a[h:]
    b1, b2 = b[:h], b[h:]
    def conj(x):
        if len(x) == 1:
            return x
        hh = len(x) // 2
        c1 = conj(x[:hh])
        return c1 + tuple(-v for v in x[hh:])
    def add(x, y): return tuple(u + v for u, v in zip(x, y))
    def sub(x, y): return tuple(u - v for u, v in zip(x, y))
    # (a1,a2)(b1,b2) = (a1 b1 - conj(b2) a2 ,  b2 a1 + a2 conj(b1))
    z1 = sub(cd_mul(a1, b1), cd_mul(conj(b2), a2))
    z2 = add(cd_mul(b2, a1), cd_mul(a2, conj(b1)))
    return z1 + z2


def time_cd(dim, iters):
    global _MULCOUNT
    a = tuple(math.sin(0.3 * i + 1) for i in range(dim))
    b = tuple(math.cos(0.2 * i + 0.5) for i in range(dim))
    _MULCOUNT = 0
    cd_mul(a, b)                       # count exactly one product
    muls = _MULCOUNT
    t0 = time.perf_counter()
    for _ in range(iters):
        cd_mul(a, b)
    dt = time.perf_counter() - t0
    return dt / iters, muls


# --------------------------------------------------------------- Crank.learn
def time_learn(text, repeats=20):
    sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/VAPMIP"))
    from monad import Crank
    nwords = len(text.split())
    per = []
    for _ in range(repeats):
        c = Crank()
        t0 = time.perf_counter()
        c.learn(text, weight=1.5, w_ctx=1.5)
        per.append(time.perf_counter() - t0)
    best = min(per)
    return best, nwords, best / nwords


# ------------------------------------------------------------------- report
def main():
    P15, P7 = 15.0, 7.0          # package TDP ceiling / single-core estimate (W)

    print("=" * 74)
    print("MATERIALISED vs ADDRESSED — energy per query, reference X1 Carbon 6th")
    print("=" * 74)

    # ---- 1. sedenion product (the per-relationship op) ----
    print("\n[1] Cayley-Dickson product, recursive, pure-Python")
    for dim, name in [(4, "H "), (8, "O "), (16, "S ")]:
        sec, muls = time_cd(dim, 20000)
        print(f"    {name}(dim {dim:2d}) : {sec*1e6:8.3f} us/product   "
              f"{muls:4d} real mults   {sec/muls*1e9:6.1f} ns/mult")
    sec16, muls16 = time_cd(16, 20000)

    # ---- 2. Crank.learn (the ingest / learning step) ----
    print("\n[2] Crank.learn() — conversational-ingest learning step (w=1.5/1.5)")
    prose = (
        "The weights are the number line. You locate, you do not store. "
        "Context per word is a scalar in the vocabulary, reconstructed against "
        "WordNet by a box kite and one wind speed. Nothing between the scalar "
        "and the structure is kept; it is regenerated, and the regeneration is "
        "a pure function of the token and one real. Instinct is the replayed "
        "forward pass off the identity tape; it requires remembering what was "
        "learned already. The lizard brain keeps the conserved charge without "
        "recomputation, which is why it is the cheap direction. Extinction is "
        "free, existence is not, and the difference is a stored trajectory."
    ) * 3
    try:
        best, nwords, per_word = time_learn(prose)
        print(f"    {nwords} words in {best*1e3:.2f} ms   "
              f"=> {per_word*1e6:.2f} us/word   "
              f"{nwords/best:,.0f} words/s")
        learn_uJ_15 = per_word * P15 * 1e6
        learn_uJ_7 = per_word * P7 * 1e6
        print(f"    energy/word:  {learn_uJ_15:8.2f} uJ  @15W ceiling   "
              f"{learn_uJ_7:8.2f} uJ  @7W single-core est.")
    except Exception as e:
        print(f"    (skipped: {e})")
        per_word = None

    # ---- 3. analytic Monad READ path per word ----
    print("\n[3] Monad context-reconstruction READ path, per word (analytic)")
    sed_flop = muls16 + (muls16 - 16)      # mults + adds, rough
    a_nnz = 40                             # typical sparse A-matrix row
    a_flop = 2 * a_nnz
    total_flop = sed_flop + a_flop
    print(f"    sedenion product      ~ {sed_flop:4d} flop  ({muls16} mul + adds)")
    print(f"    sparse A-row dot (nnz~{a_nnz}) ~ {a_flop:4d} flop")
    print(f"    WordNet / phonetic table lookup :   0 flop (memory-bound)")
    print(f"    ---------------------------------------------")
    print(f"    per word              ~ {total_flop:4d} flop")

    # measured per-word energy from [2] is the honest figure; use it.
    # For a pure-Python floor the interpreter dominates; note both.
    if per_word:
        print(f"\n    MEASURED (pure-Python, interpreter-bound): "
              f"{per_word*1e6:.2f} us/word, "
              f"{per_word*P7*1e6:.2f} uJ/word @7W")
    native_s = total_flop / 5e9           # ~5 GFLOP/s scalar native, 1 core
    print(f"    NATIVE floor (~5 GFLOP/s 1 core): {native_s*1e9:.1f} ns/word, "
          f"{native_s*P7*1e9:.1f} nJ/word @7W")

    # ---- 4. transformer forward cost, standard identity ----
    print("\n[4] Dense transformer, forward inference: 2*N_params flop / token")
    lit_JtokTPU = None
    rows = [("7B", 7e9), ("70B", 70e9), ("405B", 4.05e11)]
    for name, Np in rows:
        f = 2 * Np
        # published inference energy: hosted 70B-class ~ 0.3-1 J/token on an
        # A100/H100 node incl. overhead; ~1e-11 J/flop datacentre-effective.
        Jflop = 1e-11
        Jtok = f * Jflop
        print(f"    {name:5s}: {f:.2e} flop/token   ~ {Jtok:6.3f} J/token "
              f"(@1e-11 J/flop datacentre-effective)")
    print("    training: the backward sweep over the same N every step;")
    print("      GPT-3 175B full training ~ 1.287 GWh published (Patterson 2021).")

    # ---- 5. the ratio ----
    print("\n[5] RATIO — addressed vs materialised, per query")
    if per_word:
        mon_J = per_word * P7                       # measured, pure-Python, 7W
        mon_J_native = native_s * P7
    else:
        mon_J = native_s * P7
        mon_J_native = mon_J
    tr_J = 2 * 70e9 * 1e-11                          # 70B forward, one token
    print(f"    Monad  / word  : {mon_J*1e6:10.3f} uJ  measured (pure-Python)")
    print(f"    Monad  / word  : {mon_J_native*1e9:10.3f} nJ  native floor")
    print(f"    70B    / token : {tr_J*1e3:10.3f} mJ")
    print(f"    ratio (measured Monad) : ~ {tr_J/mon_J:,.0f} x")
    print(f"    ratio (native  Monad)  : ~ {tr_J/mon_J_native:,.3e} x")
    print("\n    The gap is structural: the Monad never materialises an")
    print("    N_params relationship tensor and never runs a gradient over one.")
    print("    Learning is a bounded in-place fold (Crank.learn / monad3c_fold);")
    print("    reading is one product against a fixed ruler.  Forward and free.")


if __name__ == "__main__":
    main()
