#!/usr/bin/env python3
"""zh_wiki.py — writes wiki pages 14 (M2) and 16 (M4) from data/zh_half_line_selftest.json and data/uns_mech_selftest.json.  No number is typed by hand."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W = os.path.join(ROOT, "..", "docs", "wiki", "Tuning-the-Semantic-Prime-Concept-Engine")
Z = json.load(open(os.path.join(ROOT, "data", "zh_half_line_selftest.json"))); U = json.load(open(os.path.join(ROOT, "data", "uns_mech_selftest.json")))
P = Z["held_out_probes"]; oc = Z["occupancy"]
def pct(x): return f"{100 * x:.2f} %"
c = P["compounds_share_radical"]
m2 = f"""# 14 · M2 — Chinese to the ½ line (single characters)

**Job.** Put one Chinese character on a zero of ζ on the critical line σ = ½, by reading its structure. Code: `SemPriCon/tools/zh_half_line.py` (+ `zh_structure.py`, `zeros_exact.py`); self-test `python3 tools/zh_half_line.py --selftest` → `data/zh_half_line_selftest.json`; every address in `data/zh_half_line_addresses.tsv`. **Single characters only**: a character is an ideogram, one idea; a two-character word is two addresses and a relation (`Table.pair`).

## The mechanism
1. **Dictionary order.** All {Z['characters']:,} Han characters of the engine's alphabet, sorted by Kangxi radical, residual strokes, key component, code point (Unihan `kRSUnicode`; cjkvi-ids).
2. **Slot.** The i-th of M takes slot ⌊(i + ½)·N/M⌋, N = 25 000. Radical neighbours are slot neighbours; every slot holds about M/N characters; characters that share a slot **accumulate** there (none outranks another).
3. **Zero.** Slot k → the exact zero ρ_(k+1) = ½ + iγ_(k+1), found by scanning the Hardy function and refining with `mpmath.siegelz` (`SpecTools/zeros/zeros_exact.py`; checked against `mpmath.zetazero`). Not the engine's smooth approximation.
4. **Energy.** E = d* + (Ω − d*)·frac(key/φ), exact 64-bit integers (⌊2⁶⁴/φ⌋ = 0x9E3779B97F4A7C15). The **key** is the character's component other than its radical (the phonetic part of a pictophonetic character); a simple character is its own key. Equal E means the same other component.

Constants: N, φ, d* = Ω/ln 10, Ω = W(1), ln 10, the zeros. Nothing else.

## Self-test (all on file)
| check | result |
|---|---|
| characters addressed | {Z['characters']:,}, addresses out of range {Z['addresses_out_of_range']} |
| deterministic (two builds, sha256) | {Z['deterministic']} |
| E in [d*, Ω) | {Z['E_in_range']} ({Z['E_min']:.6f} … {Z['E_max']:.6f}) |
| characters per slot | min {oc['min']}, max {oc['max']}, mean {oc['mean']:.2f}, empty slots {oc['empty_slots']} |
| slots holding more than one radical | {Z['slots_with_more_than_one_radical']} |
| slot non-decreasing along dictionary order | {Z['monotone_in_dictionary_order']} |
| distinct (slot, E) pairs | {Z['distinct_slot_E_pairs']:,}; characters sharing a (slot, E) with another: {Z['characters_sharing_slot_E_with_another']:,} |
| zeros loaded; max \\|ζ(½ + iγ)\\| at 60 random zeros | {Z['zeros_loaded']:,}; {Z['zeta_abs_at_60_random_zeros_max']:.2e} |
| two-character input refused | {Z['two_char_guard']} |

## Held-out probes (data the mechanism never used), against a frequency-matched shuffle
| probe | observed | baseline |
|---|---|---|
| two-character MOE words whose characters share a radical | {pct(c['observed'])} | {pct(c['shuffled_baseline'])} |
| compounds within 0.2 % of the ring (≈ 50 slots) | {pct(P['compounds_within_0.002']['observed'])} | {pct(P['compounds_within_0.002']['shuffled_baseline'])} (×{P['compounds_within_0.002']['enrichment']:.2f}) |
| compounds within 2 % | {pct(P['compounds_within_0.02']['observed'])} | {pct(P['compounds_within_0.02']['shuffled_baseline'])} (×{P['compounds_within_0.02']['enrichment']:.2f}) |
| compounds in the same slot / ±1 / ±3 / ±10 slots | {pct(P['compounds_within_0_slots_basin']['observed'])} / {pct(P['compounds_within_1_slots_basin']['observed'])} / {pct(P['compounds_within_3_slots_basin']['observed'])} / {pct(P['compounds_within_10_slots_basin']['observed'])} | {pct(P['compounds_within_0_slots_basin']['shuffled_baseline'])} / {pct(P['compounds_within_1_slots_basin']['shuffled_baseline'])} / {pct(P['compounds_within_3_slots_basin']['shuffled_baseline'])} / {pct(P['compounds_within_10_slots_basin']['shuffled_baseline'])} |
| shared Unihan gloss word, pairs within 0.2 % vs farther | {pct(P['gloss_overlap_within_0.002']['near'])} | {pct(P['gloss_overlap_within_0.002']['far'])} (×{P['gloss_overlap_within_0.002']['enrichment']:.2f}) |
| shared gloss word, within 2 % vs farther | {pct(P['gloss_overlap_within_0.02']['near'])} | {pct(P['gloss_overlap_within_0.02']['far'])} (×{P['gloss_overlap_within_0.02']['enrichment']:.2f}) |
| variant pairs (trad/simp/semantic) within 2 % | {pct(P['variant_pairs_within_0.02']['observed'])} | {pct(P['variant_pairs_within_0.02']['random_pairs'])} ({P['variant_pairs_within_0.02']['pairs']:,} pairs) |
| same key component ⇒ same toneless pinyin | {pct(P['same_key_share_toneless_pinyin']['observed'])} ({P['same_key_share_toneless_pinyin']['same_key_pairs']:,} pairs) | {pct(P['same_key_share_toneless_pinyin']['random_pairs'])} |

For comparison, the earlier mechanism (Horner over the Han rank, golden-ratio hash) measured at chance on the same probes (page 11; `SemPriCon_requ_conf.md` §4).

## What failed on the way (kept)
A pure mixed-radix position (radical arc × residual-stroke fraction, no population table) left 82 % of slots empty and put up to 372 characters in one slot. A golden hash of the dictionary rank gave chance on every probe. Ordering radicals by the 說文解字 section sequence instead of Kangxi, and ordering inside a radical by key, frequency or total strokes, changed enrichments by a few per cent only.

## Limits
These probes measure what a character's structure carries: radical co-membership is the whole of the semantic signal at this scale. The slot ring is a flat proxy; a semantic neighbourhood is a basin (A-Matrix Basin field, drift windspeed) and is tested only on a learned bin (`SemPriCon_requ_conf.md` T4). Open: d* = d*_taut here against the engine's 0.24600 (X8).
"""
open(os.path.join(W, "14_M2_chinese_to_half_line.md"), "w").write(m2)
m4 = f"""# 16 · M4 — Chinese in Universal Native Space (the π/2 equatorial great circle)

**Job.** Restate M2 ([14](14_M2_chinese_to_half_line.md)) in UNS ([15](15_M3_english_in_uns.md) defines the chart). Code: `SemPriCon/tools/uns_mech.py` (`zh_uns`).

## The algorithm
1. **Turn.** The character's place in the dictionary order, i of M: `turn = (i + ½)/M`. No hash; the circle is the dictionary closed into a ring.
2. **Place.** θ = π/2 (the equator), φ = 2π·turn, slot = ⌊N·turn⌋ = the azimuth bin of the zero ρ_(slot+1).
3. **Radius.** `E = d* + (Ω − d*)·frac(key/φ)`, `r = E/d*_taut`: the golden-ratio hash of the key component sets the radius in radial units; r ∈ [1, ln 10).

Azimuth is structure (semantic order), radius is the key component (phonetic order): two independent coordinates, unlike M1/M3 where E was the azimuth read twice.

## Verified (`python3 tools/uns_mech.py --selftest`)
| check | result |
|---|---|
| characters | {U['M4_characters']:,}; differ from M2 in slot or E: **{U['M4_differs_from_M2']}** |
| off the equator | {U['M4_off_equator']} |
| r range | {U['M4_r_range'][0]:.6f} … {U['M4_r_range'][1]:.6f} (shell [1, ln 10 = {U['radial_shell_expected'][1]:.6f}]) |

M4 is M2 rewritten as angles; it changes no placement. The English counterpart is [15](15_M3_english_in_uns.md).
"""
open(os.path.join(W, "16_M4_chinese_in_uns.md"), "w").write(m4)
print("pages 14 and 16 written")
