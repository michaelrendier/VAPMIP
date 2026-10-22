#!/usr/bin/env python3
"""v3_speak.py — run the speaking mechanism (the Unicode port monad_pyu.MonadU: hear, spread, demotic pick, golden walk) against a v3.0 bin, with the UNS mechanisms as the address of any word
the bin does not already hold (M3 for Latin words = the eb28ce8 float seed, M4 for a Han character).  Read-only on the bins.

    .venv/bin/python tools/v3_speak.py [--exact-zeros] [prompt ...]
Prints, for the reference store (the compiled eb28ce8 binary on the May-2026 store) and for each v3.0 bin: the reply, with the Fermat-space separators shown as ' | ', and the trace of how it was chosen."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import monad_pyu as pyu
from uns_mech import en_uns, zh_uns, horner95
from zh_half_line import Table, zeros as exact_zeros
import verify_against_c as vc
ROOT = os.path.abspath(os.path.join(HERE, ".."))
T = Table()
SEP = {chr(c) for c in range(0x200B, 0x2004)}


def uns_coords(surface, N=pyu.mp.N_DEFAULT):
    if len(surface) == 1 and pyu.u_is_han(ord(surface)) and surface in T.index:
        a = zh_uns(T, surface)
    else:
        a = en_uns(surface)
    return a["slot"], a["E"]


pyu.mp.word_coords = uns_coords                               # the UNS mechanisms address any word the bin does not hold


def show(s):
    return "".join(" | " if c in SEP else c for c in s)


def speak(path, prompt, exact):
    m = pyu.MonadU.from_bin(path)
    if exact: Z = exact_zeros(); m.zeros = [Z[k + 1] for k in range(m.N)]
    tr = {}; out = m.speak_wick(prompt, 50, tr)
    return m, out, tr


def main(argv):
    exact = "--exact-zeros" in argv; prompts = [a for a in argv if not a.startswith("--")] or ["what is your name"]
    bins = [("test_english_v3.0.bin", "M3 English"), ("test_chinese_v3.0.bin", "M4 Chinese"), ("test_chinese_english_v3.0.bin", "Chinese + English assigned")]
    print("zeros:", "EXACT (SpecTools)" if exact else "the engine's own approximation (generate_zeros)")
    for p in prompts:
        print(f"\n=== prompt: {p!r}")
        print("  reference (May-2026 store, compiled eb28ce8):", show(vc.c_reply(p)))
        for f, label in bins:
            m, out, tr = speak(os.path.join(ROOT, "clean", f), p, exact)
            heard = [(t, idx, ("known" if k else "new")) for idx, E, k, t in m.hear_raw(p)]
            print(f"  {label:28s} {show(out)!r}")
            print(f"     heard: {heard}")
            print(f"     lag {tr['lag_ratio']:.3f}  target_E {tr['target_E']:.5f}  demotic slot {tr['demotic']}  emitted {[(e[0], e[1], e[2]) for e in tr['emitted']]}")


if __name__ == "__main__":
    main(sys.argv[1:])
