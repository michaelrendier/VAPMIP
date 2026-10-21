# 15 · M3 — English in Universal Native Space (the π/2 equatorial great circle)

**Job.** Restate M1 ([13](13_M1_english_to_half_line.md)) as an algorithm in Universal Native Space (UNS): the radial, complex, spherical-polar chart that holds the shape of mathematics and, with it, the shape of the real world. Destination: the π/2 equatorial great circle. Code: `SemPriCon/tools/uns_mech.py` (`en_uns`).

## The chart (as used here; Cody to correct)

A point is (r, θ, φ).

| coordinate | meaning | source in the project |
|---|---|---|
| r | radial, in radial units of d*_taut = Ω/ln 10; a natural-log quantity divided by ln 10 is a count of radial units (decimal-log metric) | wiki 17: "The Flow", the radial unit; "The Translator", ×ln 10 |
| θ | polar angle from the σ-axis, σ = θ/π; **σ = ½ is θ = π/2, the equator** | wiki 33: the equatorial great circle (σ = ½) is the gyroscope's equatorial plane, poles at σ = 0 and σ = 1 |
| φ | azimuth round the equator; the complex phase e^{iφ} | the engine already uses e^{iγ/2} (the `emit` lines print it) |

The N = 25 000 zeros are N ordered marks on the equator. A slot k is the azimuth bin ⌊N·φ/2π⌋ and carries the zero ρ_k. Every angle is held as a **turn** (a fraction of 2π in [0, 1)) until the last step, so composing rotations is addition mod 1.

## The algorithm

1. **Winding count.** v = the base-95 Horner count of the spelling (M1 steps A1–A3, unchanged).
2. **Rotate.** The word is v golden-angle rotations about the polar axis, starting at φ = 0 on the equator: `turn = frac(v/φ)`. The golden angle is α = 2π/φ² = 137.5077°, and 2π/φ ≡ −α (mod 2π), so this is v rotations of −α. (Vogel's phyllotaxis index.)
3. **Place.** θ = π/2. φ = 2π · turn. Slot = ⌊N · turn⌋.
4. **Radius.** One turn of an Archimedean spiral in the equatorial plane: `E = d* + turn · (Ω − d*)`, `r = E / d*_taut`. The radius is the azimuth, which is exactly why M1's E was never a second coordinate.

M3 keeps the eb28ce8 float seed (`frac(float(v)·φ)`) so it is the same machine. `en_uns(word, exact=True)` gives the integer-turn form (`turn64 = v · ⌊2⁶⁴/φ⌋ mod 2⁶⁴`), which is what the Unicode build does.

## Verified (`python3 tools/uns_mech.py --selftest`, results in `data/uns_mech_selftest.json`)

| check | result |
|---|---|
| words in the two English bins plus the reply words: M3 slot and E against M1 | 47 233 words, **0 differences** |
| the 8 prompts: compiled eb28ce8 binary against the Python port with M3 as its address | **8 of 8 identical**, including `holcus·same·stuff·seemy` |
| θ = π/2 for every point | true |
| words of 8 letters or more at slot 0 (M1 defect, carried) | 13 097 |
| exact-integer turns against M1 | differ on 8 101 words under 8 letters and 13 096 of 8 or more: the float seed of M1 keeps few bits for 6–7-letter words and none for longer ones |

## What this does and does not change

It changes the **language** of the mechanism: a word is a count of golden-angle rotations on the equator and its radius is read off the spiral. It changes **no output**: the replies are byte-identical. The English word still carries no meaning in its angle. Nothing here is semantic; that is a property of M1 that M3 makes visible (the spelling is a winding number).

Open: the lower radial bound. With the engine's d* = 0.24600 the shell is r ∈ [0.99875, 2.3055]; with d*_taut it is exactly [1, ln 10]. The 0.00287 difference at the top is the d*_spec / d*_taut gap.
