# 12 · The four mechanisms

**Job.** Name the four address mechanisms and say how they differ, before the Fresh Start to v3.0 runs each one on its own language.

| | ½-line form | Universal Native Space form |
|---|---|---|
| **English** | **M1** [13](13_M1_english_to_half_line.md): spelling → Horner count → golden-ratio seed → slot + E (eb28ce8 as it ran) | **M3** [15](15_M3_english_in_uns.md): the same count as golden-angle rotations on the π/2 equatorial great circle |
| **Chinese** | **M2** [14](14_M2_chinese_to_half_line.md): single character → dictionary position → exact zero; E from the golden-ratio hash of the key component | **M4** [16](16_M4_chinese_in_uns.md): the same position as an azimuth turn on the equator, the key component as radius |

## Why English and Chinese need different mechanisms

English spelling carries no meaning: letters are arbitrary, so a hash of the spelling is the honest address and the golden ratio is the right way to spread it. A Chinese character is an ideogram: its structure (radical, strokes, components) is its meaning, so an address that scrambles it throws the meaning away. M2 reads structure and keeps neighbours together; M1 scrambles spelling on purpose. They share only the destination (the ½ line, then the equator) and the golden ratio.

## Shared constants (UNS constants only)

N = 25 000 · φ (and the golden angle 2π/φ²) · Ω = W(1) = 0.5671432904… · ln 10 · d*_taut = Ω/ln 10 = 0.2463072015… (M2, M4) or the engine's d* = 0.24600 (M1, M3) · the zeros of ζ. M2 and M4 use nothing else.

## Order of work

M1 documented → M2 designed and tested → M2 documented → M3, M4 as UNS conversions → Fresh Start Protocol (assessments pushed, v2 bins archived dirty, version v3.0) → each mechanism runs its own language alone.

Requirements, faults and open decisions for all four: `SemPriCon/SemPriCon_requ_conf.md`.
