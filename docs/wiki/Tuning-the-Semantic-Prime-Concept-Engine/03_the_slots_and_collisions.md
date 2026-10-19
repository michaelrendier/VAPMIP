# 03 — The slots, and collisions

**Job.** Say what a slot is, how many there are, how a word reaches one, and which collisions are the point.

## Slots
N = 25 000 (`MONAD_N_DEFAULT`). A slot holds a depth β, an age, a displayed word (the highest-`E` arrival), and links (A) to other slots. The link table packs `(i << 15) | j`, so **N must stay below 32 768** unless the packing changes. N was overshot on purpose (Cody, 2026-10-18): new concepts take free slots and no load-gauging mechanism is needed; ~50 % occupancy by The Baseline is the intended state.

## Occupancy of The Baseline (measured)
| quantity | value |
|---|---|
| distinct Han characters in the MOE dictionary text | 12 515 = **50.06 %** of N |
| distinct slots under the Unicode address | 12 013 (1 001 characters share a slot; at most 3 per slot) |
| distinct slots under a random hash (expectation) | 9 846 (2 669 characters would share) |
| the 1 640 characters that cover 90 % of the text | 1 635 distinct slots |
| golden-angle assignment `slot(k) = k · 9549 mod 25 000` (gcd = 1) | collision-free by construction, append-only |

## Which collisions are the point
Two kinds:
- **Semantic collisions** (intended, Cody 2026-10-18): two words of the same concept in different languages, or a simple word and its layered analogue, landing on one slot or on neighbours. These are what the calibration set ([06](06_the_calibration_set.md)) measures.
- **Accidental collisions** (errors): two unrelated words sharing a slot because the address is a function of spelling. The Baseline's placement is an assignment, not a hash, so it has none; the fits of other languages inherit the Baseline's slots and add residuals instead.

**Check:** `python3 SemPriCon/tools/unicode_address_measure.py`; the occupancy table is reproduced by the snippet in `SemPriCon/paper/` evidence and in this page's history.
