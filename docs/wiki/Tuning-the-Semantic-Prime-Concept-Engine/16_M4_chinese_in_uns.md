# 16 · M4 — Chinese in Universal Native Space (the π/2 equatorial great circle)

**Job.** Restate M2 ([14](14_M2_chinese_to_half_line.md)) in UNS ([15](15_M3_english_in_uns.md) defines the chart). Code: `SemPriCon/tools/uns_mech.py` (`zh_uns`).

## The algorithm
1. **Turn.** The character's place in the dictionary order, i of M: `turn = (i + ½)/M`. No hash; the circle is the dictionary closed into a ring.
2. **Place.** θ = π/2 (the equator), φ = 2π·turn, slot = ⌊N·turn⌋ = the azimuth bin of the zero ρ_(slot+1).
3. **Radius.** `E = d* + (Ω − d*)·frac(key/φ)`, `r = E/d*_taut`: the golden-ratio hash of the key component sets the radius in radial units; r ∈ [1, ln 10).

Azimuth is structure (semantic order), radius is the key component (phonetic order): two independent coordinates, unlike M1/M3 where E was the azimuth read twice.

## Verified (`python3 tools/uns_mech.py --selftest`)
| check | result |
|---|---|
| characters | 97,518; differ from M2 in slot or E: **0** |
| off the equator | 0 |
| r range | 1.000020 … 2.302502 (shell [1, ln 10 = 2.302585]) |

M4 is M2 rewritten as angles; it changes no placement. The English counterpart is [15](15_M3_english_in_uns.md).
