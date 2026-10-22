# SemPriCon_requ_conf — required configurations, constraints, tests

Created 2026-10-20. Notes on every required configuration Cody states, plus testing constraints, engineering constraints, and (marked SUGGESTION) toolsets or other perspectives on the maths. Each item is discussed individually while we engineer. Nothing below is built until Cody says go. Items are added here first, before anywhere else.

Status tags: **REQUIRED** (Cody said it) · **SUGGESTION** (Claude's, not yet discussed, not adopted) · **FAULT** (a code failure against the goal, logged, not repaired) · **OPEN** (needs Cody's decision).

## 0 · Goal and method

| id | item | tag |
|---|---|---|
| G1 | Target: two unrelated languages map to similar basin locations, **better than 70 % matching, across the board**. 70 % is deliberately high; at or above it the mechanism is on point or very close. | REQUIRED |
| G1a | "Matching" is not yet defined as a number (same slot? within k slots? same basin? same E band?). The 70 % figure needs one agreed definition, and a chance baseline reported beside every result. | OPEN |
| M1 | Method: step by step, fault by fault, error by error. Every failure of the **code** (not the maths) to reach the goal is a fault, logged, then engineered. | REQUIRED |
| M2 | Failures are data: logged, not repaired on the spot. No build until Cody says go. | REQUIRED (standing) |

## 1 · Collision and slot semantics

| id | item | tag |
|---|---|---|
| C1 | Colliding words must be **allowed to accumulate** at the slot (the "endpoint"). No word may "dominate", "outrank" or "take over" another. In the mixed bins the two languages sit next to each other in the slot. | REQUIRED |
| C1a | Current code does the opposite: `monad.c` learn keeps one label per slot and gives it to the higher-E word (`E > vocab[idx].E`). β and edges accumulate for every word, but only one word is named. Logged as FAULT F1. | FAULT |
| C1b | Cody's reading of my earlier word choice: I wrote "outranked / took over" about the label rule. That was the engine's rule described, not a design that is wanted. | note |
| C1c | Cody saw a set of words in my report and read them as evidence that collisions are not accumulating at the endpoints. My reading: the OUTRANKED-BY-HIGHER-E lists. Confirm that is the set meant. | OPEN |
| C2 | Order must matter in the two-language test: the mechanism as it exists is run on each language **separately**, then on the two orders. (Done as v2; the order effect came out as zero label differences, which is itself caused by C1a.) | REQUIRED |

## 2 · Languages

| id | item | tag |
|---|---|---|
| L1 | The mechanism was designed with English only in mind. Ideographic Chinese is far from English, and English is itself a composite ("bastard") language, so the **language structures** of both have to be visited before the mechanism is redesigned. | REQUIRED |
| L2 | Chinese Baseline stays frozen (Traditional Mandarin); fits of English and others are removable overlays with residuals kept. | REQUIRED (standing) |
| L3 | A structural account of what "semantic neighbourhood" means in English and in Chinese, separately, in non-mathematical terms. See §5. | REQUIRED |

## 3 · The term "semantic neighbourhood"

| id | item | tag |
|---|---|---|
| T1 | The algorithm contains no semantic data in the address. The term must not be used for a result unless the data behind it is semantic. Audit every use in the wiki/paper. | REQUIRED |
| T2 | Evaluate the existing English bin (`test_english_v1.0.bin`) with a human overview of what lands where. Done once, see §4. | REQUIRED |
| T4 | A semantic neighbourhood, if it exists, is not flat space and should represent semantic basins. Cody's reading (2026-10-20, "if I am constructing properly in my head"): the basins align with the A-Matrix Basin fields and the drift windspeed used in the scaled boxkite Mind's Eye (`GaugeEye.continuous_snapshot`, `a_matrix_basin_windspeed = local_curvature`). Consequence for testing: distance along the slot ring is a flat proxy; the real test reads the A link field of a learned bin as basins, with windspeed as local curvature. Not yet done; needs a learned v3.0 bin. | REQUIRED (to test) |
| T3 | Explore the space the original algorithm gives, to see how close it gets to a semantic neighbourhood in English. Valence/hydrogen belongs to a later construction in the dirty bins; it does not have to be reproduced. | REQUIRED |

## 4 · Findings so far (measured 2026-10-20, v1.0 English bin)

Source: `clean/archive/v1.0/test_english_v1.0.bin` (vocab 24,940, A-edges 9,373,394, English Wikipedia). Stored slots match the recomputed address for all 24,940 labels.

- **F1 label rule** (exact, from a Python port that reproduces the bin: 5,858,570 accepted tokens = the bin's `word_count`, same 24,940 slots, 0 labels that are not the highest-E member). 153,220 distinct accepted words sit on 24,940 slots, 6.14 per slot (1 to 18); 60 slots are empty. The label is the most frequent word of its slot in 5,166 slots (20.7 %). Label words carry 25.5 % of all accepted tokens; the most frequent word of each slot carries 89.1 %. Example: slot 8062 is labelled `snowmobiles` (1 occurrence) while `hydrogen` (559) lives there. (An earlier unfiltered count of 160,231 words / 6.4 per slot / 20 % / 25.3 % is superseded by these.)
- **F2 address.** The slot is a function of spelling. 512 same-synset English pairs from the calibration set: |Δslot|/N quartiles [0.126, 0.280, 0.472] against [0.134, 0.293, 0.5] for unrelated placement; 7 within 1 % of N against about 10 expected. Random ±3 slot neighbourhoods read as unrelated words.
- **Edges are where the English signal lives, weakly.** Co-occurrence edges (12-token window) are data about context. Same-synset pairs share edge-neighbourhoods at median Jaccard 0.0084, the same as random pairs; 35 of 512 pairs exceed the random 95th percentile (chance 26). The pairs that do: bite/sting, shadow/apparition, agriculture/farming, gravity/gravitation, hospital/infirmary, car/automobile.
- `valence` (slot 9992, E 0.374) and `hydrogen` (slot 8062, E 0.350) are 1,930 slots apart in this bin, but share 241 edge targets (of 537 and 1,409): beryllium, halogens, berkelium, bonding, alkali, dioxide, plus hub words (be, was, per). Hub words are not removed from that count.
- Caveat for all of the above: edges are slot-to-slot, so a slot shared by six words mixes six words' contexts. This was read by taking the most frequent token per slot.

Slot dictionary of this bin, every word per slot in order of first appearance, plus the full assessment: `/home/rendier/Desktop/SpaceClaude/SemPriCon/SemPriCon_dict_english_v1.0.pdf` (built by `tools/en1_dict_pdf.py`, run with `SemPriCon/.venv`).

Carried from the v2 four-bin run (page 11): 0 of 1,051 matched English–Chinese pairs within 3 slots; quartiles indistinguishable from independent placement; 42 cross-language shared slots are hash collisions.

## 5 · Language structure (to discuss; no new measurement behind this section)

- **English**: a word is a spelling with no meaning in its letters. Meaning sits in the stem and affix (act, action, react, actor), in the historical layer (Germanic everyday word, Latinate learned word, Greek technical word, which is why `deed` and `act` and `action` are three registers of one idea), in sense relations (synonym, hypernym), and in what it appears beside. A neighbourhood in English is therefore a word family, a sense group, or a collocation set. None is in the letters.
- **Chinese**: a character is a morpheme with a stored form. Meaning is partly in the form (radical = category, phonetic component = sound; 72.8 % of 9,574 characters are pictophonetic per wiki 05) and in compounds built from characters (火 → 火車, 火山, 火花). A neighbourhood in Chinese is a shared character, a shared radical class, or a compound family.
- Consequence to discuss: the two systems put meaning in different places (English: stems, layers and context; Chinese: components and compounds), so a letter-level and a character-level hash cannot meet at meaning.

## 6 · Faults logged against G1 (code, not maths)

| id | fault | evidence |
|---|---|---|
| F1 | One label per slot, higher E wins; label word is usually not the dominant word | §4: label = dominant in 20 % of slots |
| F2 | Address is a hash of spelling, so translation pairs are independent draws | 0 of 1,051 pairs within 3 slots; English synonym pairs at baseline |
| F3 | Chinese segmentation with a list-only dictionary matches inside unrelated text | OBSERVATIONS 8, page 11 |
| F4 | Tokenizer drops tokens under 2 letters (`a`, `i`, `g`, `l`, `m`, `s`) and the token filter rejects `cm hr kg km ms scratch tv` | page 11 |
| F5 | Hyphen compounds fall outside the union alphabet (`mother-in-law`, `well-known`) and Han 〇 is outside the Han set | page 11 |
| F6 | 391 of 906 DIRECT analogs are single characters (weak analogs) | `1024.md` |
| F7 | N = 25,000 against 153,220 English words means 6.14 words per slot; at that load a slot cannot be a word | §4 |
| F8 | Hex-string gate rejects ordinary words made only of the letters a–f, 6 or more (decade, facade, defaced, accede, beaded): 520 tokens | PDF assessment §2 |
| F9 | Tokenizer drops whole tokens that begin with an apostrophe (3,327 tokens) | PDF assessment §2 |
| F10 | Trailing-apostrophe tokens rejected rather than trimmed: 4,927 tokens (years', states', workers') | PDF assessment §2 |
| F11 | Vowel-ratio gate (under 15 % vowels, 6 or more letters) rejects real words: strength (428), flights, strings, knights, springs, scripts, lengths: 3,552 tokens. The "no vowel" gate takes 34,396 tokens, mostly fragments (th, st, bc) | PDF assessment §2 |

## 7 · Four mechanisms and v3.0 (Cody, 2026-10-20)

| id | item | tag |
|---|---|---|
| X1 | Four mechanisms, each documented in the wiki: M1 English → ½ line (the exact machinery behind `holcus·same·stuff·seemy`, eb28ce8); M2 Chinese → ½ line (new); M3 = M1 in UNS; M4 = M2 in UNS. English and Chinese need entirely different mechanisms. | REQUIRED |
| X2 | M2 maps SINGLE characters only (a character is an ideogram: one idea). Two-character words are two addresses plus a relation; that relation is where direct semantic data is expected. | REQUIRED |
| X3 | Hard constraint on M2: UNS constants only (golden ratio/angle, d*, Ω, ln 10 …) plus regular maths; the golden ratio/angle is to be included; respect the UNS nature of the language the maths speaks. | REQUIRED |
| X4 | UNS = Universal Native Space = radial complex spherical-polar coordinates; the coordinate system that holds the shape of mathematics and so the shape of the real world. M3/M4 destination = the π/2 equatorial great circle of Primes. The conversion is not to be done before M2 is finished. | REQUIRED |
| X5 | After the four mechanisms are written and documented: Fresh Start Protocol (push all assessments to their places, archive the current v2 bins as dirty, version → v3.0), then each mechanism runs on its own language individually, so coordinate systems and language structures can be compared. | REQUIRED |
| X6 | Next experiment in v3.0: assign English words to the respective Chinese idea slots. Not a hard encoding of English to primes: an assignment of English words to Chinese idea slots. Discussion pending, after the four mechanisms. | REQUIRED (discuss) |
| X7 | "Works" for M2 = works for the entirety of the Chinese on file: all 97,518 Han characters of the engine's alphabet, with radical and stroke data for every one. | REQUIRED |
| X8 | OPEN: M2 uses d* = d*_taut = Ω/ln 10 = 0.246307… (The Boundary face) for the lower E bound; M1 keeps the engine's 0.24600 (the quarantined d*_spec). The two differ by 3.07e-4. Cody to say which M2/M4 should carry. | OPEN |
| X10 | The sentence constructor's **basin** gets the Lorenz–Stirling attractor code, copied into SemPriCon (done: `orbweaver/LorenzStirling.py`, byte-identical, provenance in `orbweaver/PROVENANCE.md`). It is to be part of the **pathway mechanism for the orbweaver**. Not wired in. | REQUIRED (done: copy) |
| X11 | Test whether Ring Theory is the clearest reading of both UNS and 0_RB (adding an axis across a ring to rotate in place; the sedenion as a set of circle-modifying operators: deform / partition / permute / scale), find the smallest number of operators of UNS's hypercomplex language, and record, per slot with bracketings and firing orders, what each produces or makes available equation-wise, in the Ainulindale, SedenionSpectralRelativity and VAPMIP wikis. Uses the existing bracketing and firing-order engine (`SedenionSpectralRelativity/bracket_firing_engine.py`). Battery: `VAPMIP/RingCircle/`. | REQUIRED (in progress) |
| X9 | The engine's `generate_zeros` places words on a smooth Newton approximation of the counting function (error up to 1.8 at low n, 0.28 at n = 25,000), not on zeros. M2 uses the exact zeros (`tools/zeros_exact.py`). | note |

## 8 · SUGGESTIONS (not adopted; for individual discussion)

| id | suggestion |
|---|---|
| S1 | Define "match" as a pair of numbers, reported together: fraction within k slots and fraction in the same basin, each next to its chance value. Without this 70 % cannot be scored. |
| S2 | Make the slot a multiset: every word that hashes there is kept with its count, and the label becomes a view (top by count), not a winner. This is C1 as a data structure. |
| S3 | Score English semantics on the edges first (context), with hub words down-weighted by degree, because the slot carries none. A test harness over the 512 + 512 calibration pairs already exists in the data. |
| S4 | English: stem/affix tokenization so word families share a key; test whether families cluster. |
| S5 | Chinese: character/radical components as the unit, using the Baseline stores already in the repo (Unihan, makemeahanzi, cjkvi-ids, Shuowen). |
| S6 | Report every result with its chance baseline (the triangle for slot distance), as page 11 does. |

## 9. v3.0 (2026-10-21)
- **Baseline language.** Chinese is the baseline for the measurement (Cody): ideographic; alive and spoken well today; over five millennia old; believed one of the most efficient partitionings of idea space (assumption, unmeasured). Bare minimum of ideas space; separates couch from chair. Recorded in wiki 17.
- **Word list v3.0.** `calibration/calibration_v3_en_zh.tsv`, frozen: 512 × 2, single Chinese characters. **Bins:** `clean/test_english_v3.0.bin` (M3) and `clean/test_chinese_v3.0.bin` (M4), exact zeros, no token filter, no A edges.
- **First survey:** English 732 occupied slots with 210 words on slot 0 (M1 float-seed defect carried by M3); Chinese 996 occupied slots, at most 3 per slot; same concept in the same slot in 0 of 1 024 rows. X6 (assign English words to Chinese idea slots) is the next discussion, not started.
- **Assignment experiment (2026-10-21):** `clean/test_chinese_english_v3.0.bin`: English words assigned to the slot of their Chinese partner, each keeping its own energy; 611 Chinese / 385 English labels. All three v3.0 bins are silent on "what is your name" (no edges; β below the engine's GAP floor; one phase-filter rejection). Assessments in `clean/assessment/`; the assessors misgrade single-character and mixed-script bins (data, not repaired). See wiki 17.
