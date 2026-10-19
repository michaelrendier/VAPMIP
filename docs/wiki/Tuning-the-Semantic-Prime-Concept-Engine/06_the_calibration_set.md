# 06 — The calibration set (testing and debugging data set)

**Job.** A fixed, **non-mutating** list of **1 024 words** to calibrate and debug the engine against. Written language only: it is about writing, not about how people speak. English (US and UK spellings) and Chinese (Traditional) are the only languages in version 1; the other four are on hold.

## Specification (Cody, 2026-10-18)
1. **Two halves of 512.** The **first half (S)**: simple words for contextually simple, prime concepts. The **second half (L)**: *different words that carry the same meaning* as the first half but have a **deeper contextual interpretation** available (S *ball*, *city*, *road*; L *globe*, *metropolis*, *route*). The two halves are the calibration mechanism to shoot towards: the engine is calibrated when an S word and its L partner behave as one meaning with different depth.
2. **Direct analogues.** Every concept has a word in English and a word in written Chinese. One missing analogue fails the concept.
3. **It does not mutate.** `calibration/calibration_v1_en_zh.tsv` is read-only and pinned by `calibration/FROZEN.sha256`. A correction is a **new version** (`calibration_v2_…`), never an edit.
4. **Each language gets its own ruleset.** Languages differ in how writing carries meaning: strongly phonetic alphabets (Spanish and the other Romance languages), near-phonemic agglutinative writing (Finnish), opaque alphabetic orthography (English), logographic writing in which a character is a morpheme (Chinese). Their semantics differ, so each type of semantic association is its own experiment and its own ruleset. The current engine has one generic ruleset ([02](02_the_tokenizer.md)); this page fixes only the standard to measure against.

## How version 1 was built (`SemPriCon/tools/calibration_v1.py`; nothing typed by hand)
- **Concept:** a WordNet synset with at least two single-word English lemmas and two single-token Mandarin lemmas in the Open Multilingual WordNet (Mandarin converted to Traditional with OpenCC `s2twp`); S's word is one of the synset's first three senses.
- **English:** S = the most frequent lemma in English Wikipedia text; L = a rarer lemma (at most 2/3 of S's frequency, at least 8 occurrences) with the most WordNet senses.
- **Chinese:** the same over the synset's Mandarin lemmas, each **confirmed by CC-CEDICT** (its definition contains a lemma of the synset); L has the most CEDICT definitions among the rarer ones.
- **Selection:** 512 concepts by *depth evidence* (log₁₀ frequency ratio S:L in English plus in Chinese, each capped at 3, plus a polysemy term); every English word and every Chinese word occurs once; at most 20 % of concepts from one lexicographer class. 

## The file (`calibration_v1_en_zh.tsv`, sha256 `6180c3c60e446640b59516c2a3ba7346208de1e1bf8a11f034c5669cf64beaa8`)
`id, half, pair, pos, en_us, en_uk, zh_trad, synset, lexname, freq_en, freq_zh, wn_senses, cedict_defs, depth_evidence, definition`. 1 024 rows: each pair is two consecutive rows, S then L. Nouns 341, verbs 171 (no adjective passed the gates). US and UK spellings differ in 21 rows. Largest lexicographer classes: {'noun.artifact': 64, 'noun.act': 34, 'noun.person': 30, 'verb.communication': 29, 'verb.social': 26}.

| S (en) | L (en) | S (zh) | L (zh) | meaning |
|---|---|---|---|---|
| feather | plume | 羽 | 羽毛 | the light horny waterproof structure forming the external co |
| road | route | 路 | 道路 | an open way (generally public) for travel or transportation |
| width | breadth | 寬度 | 廣度 | the extent of something from side to side |
| heart | bosom | 心 | 內心 | the locus of feelings and intuitions |
| anger | ire | 憤怒 | 火氣 | a strong emotion; a feeling that is oriented toward some rea |
| city | metropolis | 城 | 城市 | a large and densely populated urban area; may include severa |
| ball | globe | 球 | 球狀物 | an object with a spherical shape |

## Known noise (version 1 is frozen as it stands; corrections go to version 2)
WordNet's senses and OMW alignments are not perfect: a few pairs are a near rather than a direct match (*despite/contempt* as a noun sense, *mood/temper*). Frequency is measured on Wikipedia, which is not everyday speech (and the set is about writing). No adjectives passed the gates.

## Use
- *Calibration:* an S word and its L partner, in English and in Chinese, must each tokenise as expected (Chinese words split into characters, [02](02_the_tokenizer.md)); then they are the targets of the concept key ([01](01_the_address.md)).
- *Debugging:* a pair whose words land far apart after the hash is a finding about the hash or about the pair; a word the engine cannot address is a tokenizer or filter bug.
- *Fitting:* the set is the held-out check for the fit of English to The Baseline ([05](05_the_baseline.md)): fit on other alignments, test on these.

## On hold: the six-language set
Swahili, Finnish, Indonesian and Quechua are on hold (Quechua and Swahili data are thin: only 158 of the earlier 1 024-concept six-language set were data-verified). The earlier files are kept, unchanged, in `SemPriCon/calibration/on_hold/` and are not part of this specification.


## Version 2 candidate: Finnish and Indonesian
`calibration/calibration_v2_en_zh_fi_id.tsv` (built by `tools/calibration_v2.py`) carries every v1 row unchanged and adds `fi_word`, `fi_note`, `id_word`, `id_note`. Words come from the Open Multilingual WordNet lemmas of the row's synset, single words only, chosen by corpus frequency. Coverage of the 1 024 rows: Finnish 808 ok, 141 repeat, 61 unattested, 14 no lemma; Indonesian 874 ok, 86 repeat, 18 unattested, 46 no lemma. This is a machine-made **candidate**: it is frozen only after a speaker reviews it. v1 is not changed.
