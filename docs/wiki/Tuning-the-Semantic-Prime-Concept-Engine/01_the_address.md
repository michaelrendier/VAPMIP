# 01 — The address

**Job.** Turn a word into a slot (`idx`, 0 … N−1) and an energy `E ∈ [d*, Ω)`. Everything else in the engine is keyed by the slot.

## The original (2026-05 build, ASCII; kept for reference and for the historical paper)
`PtolC/monad.c: monad_word_coords` at `eb28ce8`. Base-95 Horner over printable ASCII bytes in `uint64`, then `seed = fmod((double)v · φ, 1.0)`, `idx = ⌊seed · N⌋`, `E = d* + seed (Ω − d*)`. Two defects, both measured: the float seed has no fractional bits once `v·φ > 2⁵²`, so **every word of ≥ 8 letters addresses to slot 0**; every non-ASCII byte contributes digit 0. Example: `holcus` → slot 24639, E 0.5625142; `philadelphos` → slot 0, E 0.246.

## The current code (Unicode build, `STATE_VERSION 5`)
`SemPriCon/src/PtolC_unicode/monad.c: monad_word_coords`.

```
v    = 0
for each code point cp of the word:  v = (v · 0x110001 + (cp + 1)) mod (2⁶¹ − 1)
seed64 = (v · 0x9E3779B97F4A7C15) mod 2⁶⁴          # 0x9E37… = round(2⁶⁴/φ): the fraction of v/φ, in units of 2⁻⁶⁴, exact integers
idx    = ⌊seed64 · N / 2⁶⁴⌋
E      = d* + (seed64 ≫ 11)/2⁵³ · (Ω − d*)
```
Constants: N = 25 000, d* = 0.24600, Ω = 0.56714. Every code point of a word of any length reaches the address; no float precision is lost; the golden-ratio multiplication is multiplicative (Fibonacci) hashing, which spreads consecutive integers evenly.

| word | slot | E | tokens |
|---|---|---|---|
| `tree` | 23968 | 0.5539 | tree |
| `puu` (Finnish) | 9748 | 0.3712 | puu |
| `mti` (Swahili) | 20495 | 0.5093 | mti |
| `pohon` (Indonesian) | 2731 | 0.2811 | pohon |
| `sach'a` (Quechua) | 10490 | 0.3808 | sach'a |
| `樹` | 20407 | 0.5081 | 樹 |
| `木` | 16490 | 0.4578 | 木 |
| `長椅` | 7885 | 0.3473 | 長, 椅 |
| `philadelphos` | 1484 | 0.2651 | philadelphos |
| `epäjärjestelmällisyys` | 10141 | 0.3763 | epäjärjestelmällisyys |

Old stores (versions 1–4) are **refused** by `state_load`: their slots were made by the ASCII address and would not match.

**Check:** `python3 SemPriCon/tools/verify_unicode_against_c.py` (binary vs port, learned state exact); `SemPriCon/tools/unicode_address_measure.py` (resolution on real headwords).
**Open:** the address is a function of spelling. The prime-concept hash replaces it with a function of concept, placed by The Baseline ([05](05_the_baseline.md)); this page will then specify the concept key in front of this code.


## Language alphabets
Since Fresh Start v2.0 every store uses Horner over **its own alphabet**, base = the alphabet's size (ASCII-95 for English and Indonesian, a table for Chinese and Finnish). The code-point Horner (base `0x110001`) described above was the v1.0 Chinese build and is archived. See [09](09_the_test_bins.md).
