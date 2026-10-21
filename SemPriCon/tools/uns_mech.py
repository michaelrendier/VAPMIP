#!/usr/bin/env python3
"""uns_mech.py — M3 and M4: the two ½-line mechanisms restated in Universal Native Space (UNS), destination = the π/2 equatorial great circle.

UNS here is the radial, complex, spherical-polar chart of the project: a point is (r, θ, φ).
  r  radial, in radial units of d*_taut = Ω/ln 10 (the decimal-log metric: a quantity in natural-log units divided by ln 10 is a count of radial units)
  θ  polar angle from the σ-axis, σ = θ/π; the critical line σ = ½ is θ = π/2, the EQUATOR (the great circle on which the zeros lie)
  φ  azimuth round the equator; the complex phase e^{iφ}.  The N = 25 000 zeros ρ_k are N ordered marks on this circle (slot k = azimuth bin ⌊N·φ/2π⌋).
Every angle is kept as a TURN (a fraction of 2π in [0, 1)) until the last step, so a rotation is an addition mod 1 and nothing is lost to a π.

  M3  English → UNS.   v = base-95 Horner count of the word's spelling.  The word is v golden-angle rotations about the polar axis from φ = 0 on the equator:
                       turn = frac(v/φ)  (the golden angle is 2π/φ², and 2π/φ ≡ −2π/φ² mod 2π).  θ = π/2.  r on one turn of an Archimedean spiral in the equatorial plane,
                       r = (d* + turn·(Ω − d*)) / d*_taut.  Slot = azimuth bin.  This is the machinery of eb28ce8 (including its float seed) written as angles.
  M4  Chinese → UNS.   One character.  Its turn is its place in the dictionary order (radical, residual strokes, key component, code point): turn = (i + ½)/M.  θ = π/2.
                       r = (d* + frac(key/φ)·(Ω − d*)) / d*_taut: the golden-ratio hash of the key component sets the radius.  Slot = azimuth bin.  This is M2 written as angles.

    .venv/bin/python tools/uns_mech.py --selftest
"""
import json, math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dprint import dprint
import monad_py as mp
from zh_half_line import Table, energy, DSTAR as D_TAUT, OMEGA, GOLD64, N, M64
ROOT = os.path.abspath(os.path.join(HERE, ".."))
TWO_PI = 2 * math.pi
PHI = mp.PHI
ALPHA_GOLD = TWO_PI / (PHI * PHI)            # the golden angle, 137.5077…°

def horner95(word):
    """as eb28ce8 (AS-IS: a non-ASCII byte is digit 0; the value wraps mod 2⁶⁴)"""
    v = 0
    for c in word.encode("utf-8"):
        v = (v * 95 + ((c - 32 + 1) if 32 <= c < 127 else 0)) & M64
    return v - 1 if v > 0 else v

def en_uns(word, exact=False):
    """M3.  exact=False: the float seed of eb28ce8 (frac(float(v)·φ), 53 bits); exact=True: integer turns, turn64 = v·⌊2⁶⁴/φ⌋ mod 2⁶⁴ (what the Unicode build does)"""
    v = horner95(word)
    turn = ((v * GOLD64) & M64) / 18446744073709551616.0 if exact else (lambda s: s + 1.0 if s < 0.0 else s)(math.fmod(float(v) * PHI, 1.0))
    E = mp.D_STAR + turn * (mp.OMEGA_ZS - mp.D_STAR)
    slot = min(max(int(turn * mp.N_DEFAULT), 0), mp.N_DEFAULT - 1)
    return {"word": word, "winding_count": v, "turn": turn, "r": E / D_TAUT, "theta": math.pi / 2, "phi": TWO_PI * turn, "slot": slot, "E": E}

def zh_uns(T, c):
    """M4"""
    if len(c) != 1: raise ValueError("M4 maps a single character")
    i = T.index[c]; turn = (i + 0.5) / T.M; E = energy(ord(T.key[c]))
    return {"char": c, "dictionary_index": i, "turn": turn, "r": E / D_TAUT, "theta": math.pi / 2, "phi": TWO_PI * turn, "slot": min(int(turn * N), N - 1), "E": E}

def selftest(out):
    res = {}
    # M3 against M1 on every word the English bins hold, and on the 8 prompts through the compiled binary
    sys.path.insert(0, HERE); import ptol_bin
    words = set()
    for p in (os.path.join(ROOT, "clean", "archive", "v1.0", "test_english_v1.0.bin"), os.path.join(ROOT, "dirty", "monad_wordnet_v4_20260519.bin")):
        words |= {w for _, w, *_ in ptol_bin.load(p, with_edges=False)["vocab"]}
    words |= {"holcus", "same", "stuff", "seemy", "what", "is", "your", "name", "philadelphos", "epajarjestelmallisyys"}
    bad = 0; bad_exact = 0; long_slot0 = 0
    for w in words:
        a = en_uns(w); idx, E = mp.word_coords(w)
        bad += not (a["slot"] == idx and a["E"] == E)
        long_slot0 += (len(w) >= 8 and idx == 0)
    res["M3_words_checked"] = len(words); res["M3_float_differs_from_M1"] = bad
    res["M1_words_of_8_or_more_letters_at_slot_0"] = long_slot0
    from collections import Counter
    ex_diff = sum(en_uns(w, exact=True)["slot"] != mp.word_coords(w)[0] for w in words if len(w) < 8)
    res["M3_exact_integer_differs_from_M1_among_words_under_8_letters"] = ex_diff
    res["M3_exact_integer_differs_from_M1_among_words_8_plus"] = sum(en_uns(w, exact=True)["slot"] != mp.word_coords(w)[0] for w in words if len(w) >= 8)
    res["M3_equator"] = all(abs(en_uns(w)["theta"] - math.pi / 2) < 1e-15 for w in list(words)[:1000])
    # the reply: the compiled binary vs the Python port with M3 as its address
    import verify_against_c as vc
    prompts = ["what is your name", "can you hear what i am typing", "who are you", "what is a tree", "good morning", "the cat sat on the mat", "how do you do", "tell me about water"]
    orig = mp.word_coords
    def via_uns(surface, N=mp.N_DEFAULT):
        a = en_uns(surface); return a["slot"], a["E"]
    rows = []
    for p in prompts:
        c = vc.c_reply(p)
        mp.word_coords = via_uns
        try: m = mp.Monad.from_bin(vc.STORE); py = m.speak_wick(p, 50, {})
        finally: mp.word_coords = orig
        rows.append({"prompt": p, "binary": c, "uns_port": py, "identical": c == py})
    res["M3_replies"] = rows; res["M3_replies_identical"] = sum(r["identical"] for r in rows)
    # M4 against M2 for every character
    T = Table(); bad4 = 0; off_equator = 0
    for c in T.C:
        u = zh_uns(T, c)
        bad4 += not (u["slot"] == T.slot[c] and u["E"] == energy(ord(T.key[c]))); off_equator += abs(u["theta"] - math.pi / 2) > 1e-15
    res["M4_characters"] = len(T.C); res["M4_differs_from_M2"] = bad4; res["M4_off_equator"] = off_equator
    res["M4_r_range"] = [min(zh_uns(T, c)["r"] for c in T.C), max(zh_uns(T, c)["r"] for c in T.C)]
    res["radial_shell_expected"] = [1.0, math.log(10)]
    res["golden_angle_degrees"] = math.degrees(ALPHA_GOLD)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    return res

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print(json.dumps(selftest(os.path.join(ROOT, "data", "uns_mech_selftest.json")), ensure_ascii=False, indent=1))
    else:
        T = Table()
        for w in sys.argv[1:]: print(en_uns(w) if w.isascii() else zh_uns(T, w))
