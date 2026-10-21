# 13 · M1 — English to the ½ line (the machinery behind `holcus·same·stuff·seemy`)

**Job.** Write down, exactly, how the May-2026 C monad (`PtolC/monad.c` at `eb28ce8`) puts an English word on the critical line σ = ½. The code is authoritative; this page is the mechanism as it ran. Full account: `SemPriCon/paper/The_Golden_Ratio_Monad.md` §5, §6, §12. Executable port: `SemPriCon/tools/monad_py.py` (8 of 8 replies identical to the compiled binary).

Label: `OURS` for the construction; the golden-ratio multiplication is `Post-Hoc:` Fibonacci hashing (Knuth 1973); the golden-angle step is `Post-Hoc:` Vogel 1979 / three-distance theorem (Sós 1958).

## The mechanism (a word is a spelling)

| step | operation |
|---|---|
| A1 | digit of each byte: `c − 31` for printable ASCII, **0** for every other byte |
| A2 | Horner, base 95: `v ← 95·v + digit`, unsigned 64-bit, wraps mod 2⁶⁴ |
| A3 | `v ← v − 1` when `v > 0` |
| A4 | golden ratio: `seed = fmod((double)v · φ, 1.0)`, φ = 1.6180339887498948482 |
| A5 | slot: `idx = ⌊seed · N⌋`, N = 25 000 |
| A6 | energy: `E = d* + seed · (Ω − d*)`, d* = 0.24600, Ω = 0.56714 |
| Z | the slot's number: `γ = zeros[idx]`; `σ = ½` is the constant the engine prints |

`holcus`: v = 571 442 774 203 → seed 0.985595703125 → slot 24 639, E = 0.562514.

The walk that speaks steps `golden_step = round(N/φ²) = 9549` slots at a time (the golden angle of the slot ring, 137.5°; gcd(9549, 25 000) = 1). The first word is the slot whose stored E is nearest `target_E` ≈ Ω among open slots: slot 24 639, shown as `holcus`.

## What the mechanism measurably is

1. **The slot is a function of spelling.** Two words land together because their spellings hash together. Same-synset English pairs sit at the unrelated-placement quartiles (`SemPriCon_requ_conf.md` §4).
2. **E is not a second coordinate.** `slot = ⌊seed·N⌋` and `E = d* + seed(Ω − d*)` use one seed: E = d* + (slot + fraction)(Ω − d*)/N. Seen on the unit circle, (E, slot) is one turn of an Archimedean spiral, radius growing linearly with azimuth (see [15](15_M3_english_in_uns.md)).
3. **Words of eight letters or more all land on slot 0** (E = d*), because `(double)v · φ` exceeds 2⁵² and `fmod(·, 1)` returns 0. Measured in the paper §6.1. The Unicode build replaced the float seed with an exact 64-bit integer seed; M1 keeps the float seed on purpose, as the record of what produced the reply.
4. **The zeros are not zeros.** `generate_zeros` copies the first 20 tabulated zeros, then Newton-solves the smooth counting formula `N(t) = (t/2π)(ln(t/2π) − 1) + 7/8`. Against `mpmath.zetazero`: n = 21 off by 1.81, n = 100 by 0.33, n = 1000 by 0.67, n = 25 000 by 0.28. A word on slot k is on the critical line at a height near ρ_k, not on ρ_k. (M2 uses exact zeros, [14](14_M2_chinese_to_half_line.md).)
5. **One label per slot, the higher E wins** (`E > vocab[idx].E`). All β and links accumulate for every word; only the name is single. Logged as fault F1.

## Status

Frozen as the historical mechanism. Not edited. The conversion to Universal Native Space is [15](15_M3_english_in_uns.md).
