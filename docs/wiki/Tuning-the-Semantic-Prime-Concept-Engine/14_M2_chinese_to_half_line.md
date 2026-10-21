# 14 · M2 — Chinese to the ½ line (single characters)

**Job.** Put one Chinese character on a zero of ζ on the critical line σ = ½, by reading its structure. Code: `SemPriCon/tools/zh_half_line.py` (+ `zh_structure.py`, `zeros_exact.py`); self-test `python3 tools/zh_half_line.py --selftest` → `data/zh_half_line_selftest.json`; every address in `data/zh_half_line_addresses.tsv`. **Single characters only**: a character is an ideogram, one idea; a two-character word is two addresses and a relation (`Table.pair`).

## The mechanism
1. **Dictionary order.** All 97,518 Han characters of the engine's alphabet, sorted by Kangxi radical, residual strokes, key component, code point (Unihan `kRSUnicode`; cjkvi-ids).
2. **Slot.** The i-th of M takes slot ⌊(i + ½)·N/M⌋, N = 25 000. Radical neighbours are slot neighbours; every slot holds about M/N characters; characters that share a slot **accumulate** there (none outranks another).
3. **Zero.** Slot k → the exact zero ρ_(k+1) = ½ + iγ_(k+1), found by scanning the Hardy function and refining with `mpmath.siegelz` (`SpecTools/zeros/zeros_exact.py`; checked against `mpmath.zetazero`). Not the engine's smooth approximation.
4. **Energy.** E = d* + (Ω − d*)·frac(key/φ), exact 64-bit integers (⌊2⁶⁴/φ⌋ = 0x9E3779B97F4A7C15). The **key** is the character's component other than its radical (the phonetic part of a pictophonetic character); a simple character is its own key. Equal E means the same other component.

Constants: N, φ, d* = Ω/ln 10, Ω = W(1), ln 10, the zeros. Nothing else.

## Self-test (all on file)
| check | result |
|---|---|
| characters addressed | 97,518, addresses out of range 0 |
| deterministic (two builds, sha256) | True |
| E in [d*, Ω) | True (0.246312 … 0.567123) |
| characters per slot | min 3, max 4, mean 3.90, empty slots 0 |
| slots holding more than one radical | 160 |
| slot non-decreasing along dictionary order | True |
| distinct (slot, E) pairs | 90,994; characters sharing a (slot, E) with another: 12,034 |
| zeros loaded; max \|ζ(½ + iγ)\| at 60 random zeros | 25,000; 2.89e-11 |
| two-character input refused | True |

## Held-out probes (data the mechanism never used), against a frequency-matched shuffle
| probe | observed | baseline |
|---|---|---|
| two-character MOE words whose characters share a radical | 7.62 % | 1.53 % |
| compounds within 0.2 % of the ring (≈ 50 slots) | 2.05 % | 0.49 % (×4.19) |
| compounds within 2 % | 10.16 % | 4.32 % (×2.35) |
| compounds in the same slot / ±1 / ±3 / ±10 slots | 0.03 % / 0.07 % / 0.18 % / 0.54 % | 0.01 % / 0.02 % / 0.04 % / 0.11 % |
| shared Unihan gloss word, pairs within 0.2 % vs farther | 9.91 % | 1.59 % (×6.23) |
| shared gloss word, within 2 % vs farther | 4.73 % | 1.49 % (×3.16) |
| variant pairs (trad/simp/semantic) within 2 % | 81.97 % | 3.73 % (8,576 pairs) |
| same key component ⇒ same toneless pinyin | 21.39 % (840,192 pairs) | 0.51 % |

For comparison, the earlier mechanism (Horner over the Han rank, golden-ratio hash) measured at chance on the same probes (page 11; `SemPriCon_requ_conf.md` §4).

## What failed on the way (kept)
A pure mixed-radix position (radical arc × residual-stroke fraction, no population table) left 82 % of slots empty and put up to 372 characters in one slot. A golden hash of the dictionary rank gave chance on every probe. Ordering radicals by the 說文解字 section sequence instead of Kangxi, and ordering inside a radical by key, frequency or total strokes, changed enrichments by a few per cent only.

## Limits
These probes measure what a character's structure carries: radical co-membership is the whole of the semantic signal at this scale. The slot ring is a flat proxy; a semantic neighbourhood is a basin (A-Matrix Basin field, drift windspeed) and is tested only on a learned bin (`SemPriCon_requ_conf.md` T4). Open: d* = d*_taut here against the engine's 0.24600 (X8).
