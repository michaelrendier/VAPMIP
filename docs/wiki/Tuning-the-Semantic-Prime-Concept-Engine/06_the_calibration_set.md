# 06 — The calibration set (testing and debugging data set)

**Job.** A fixed list of **1 024 concepts**, each with a **direct word in every language of the test bed**, used to calibrate and debug the engine: if the semantic prime-concept hash is working, a concept's words in different languages must behave as one concept (semantic collisions, [03](03_the_slots_and_collisions.md)), and a simple concept and its layered analogue must stand in the relation the construction predicts. Files: `SemPriCon/calibration/calibration_1024.tsv` (the set), `calibration_pool_all.tsv` (every candidate, graded). Builder: `SemPriCon/tools/calibration_build.py`.

## Specification
1. **Languages:** English (US and UK spellings), Mandarin (Traditional), Swahili, Finnish, Indonesian, Quechua.
2. **Inclusion rule (Cody, 2026-10-18).** A concept is in the set only if *every* language has a **direct** analogue: one word, not a phrase, not a loan from another test-bed language, meaning the same thing. **One missing analogue in one language fails the concept.**
3. **Two tiers, 512 each.** **S**: simple concepts (concrete, few senses). **L**: layered concepts, "analogous vocabulary carrying more complexity" (abstract, many senses). Tiers are assigned by an explicit score, not by hand: `layer_score = 3·[abstract lexicographer class] + n_senses/3` on the English WordNet synset; the lower half of the selected 1 024 is S, the upper half is L. A pair (S, L) is recorded when WordNet ties them (derivationally related form or hypernym link).
4. **Concept unit:** an English WordNet synset (the first synset of an English word and part of speech that has lemmas in the Open Multilingual WordNet for Mandarin, Finnish and Indonesian).
5. **Word choice per language:** Mandarin, Finnish, Indonesian: the lemmas of that synset in the Open Multilingual WordNet (Mandarin converted to Traditional with OpenCC `s2twp`); Swahili, Quechua (no WordNet): the Wiktionary headword whose gloss is the English word (rank 0 = primary gloss). Among several candidates the **most frequent in that language's Wikipedia text** is taken, then the non-borrowed one.
6. **Evidence grade** (the worst across languages): **A** primary gloss in Swahili and Quechua and every chosen word attested at least 3 times in its Wikipedia sample; **B** gloss within the first two; **C** within the first four; **D** weaker, or a word not attested. Only grade A meets the data criterion for "direct analogue" by itself.
7. **Review column.** `data-verified` = grade A and no etymology flag (no `borrowed`, no mention of another test-bed language in the etymology). Everything else is `pending` until a speaker of each language confirms the word. Pending is not a pass.

## Status (1024 concepts selected from 1070 candidates)
| | S | L | total |
|---|---|---|---|
| concepts | 512 | 512 | 1024 |
| grade A | 198 | 175 | 373 |
| grade B | 75 | 87 | 162 |
| grade C | 33 | 41 | 74 |
| grade D | 206 | 209 | 415 |

- **Data-verified (A, no flags): 158 of 1024.** Grade A alone: 373. The rest awaits review: the open data cannot reach 1 024 verified concepts, because Quechua is thin (2 150 Wiktionary headwords, a 13 MB Wikipedia). That shortfall is a finding, not a defect of the list.
- Parts of speech: {'n': 588, 'a': 103, 'v': 330, 'r': 3}. Concepts whose US and UK spellings differ: 15. Concepts with an etymology flag in at least one language: 555. Pairs (S, L): 41.
- Known noise (examples in the file): OMW sometimes gives a near rather than direct match (Indonesian *pelanggaran* for *accident*); Mandarin picks are frequent words, not always the best match; Wikipedia frequency is a weak proxy for Quechua.

## Columns of `calibration_1024.tsv`
`id, tier, pair, pair_relation, pos, en_us, en_uk, zh_trad, sw, fi, id_, qu, grade, ranks_zh_sw_fi_id_qu, freq_zh_sw_fi_id_qu, flags, lexname, n_senses, synset, en_gloss, review`

## Sample (grade A, no flags)
| id | en | pos | zh | sw | fi | id | qu | grade |
|---|---|---|---|---|---|---|---|---|
| C0011 | addition | n | 增加 | nyongeza | lisääminen | tambahan | yapay | A |
| C0017 | all | a | 都 | ote | koko | semua | tukuy | A |
| C0029 | approach | v | 接近 | sogea | lähestyä | hampir | chimpay | A |
| C0037 | back | n | 後面 | nyuma | takaosa | belakang | wasa | A |
| C0043 | basket | n | 籃子 | kikapu | koppa | raga | isanka | A |
| C0076 | bridge | n | 橋 | kivuko | silta | jambatan | chaka | A |
| C0103 | chest | n | 胸 | kifua | rintakehä | dada | qhasqu | A |
| C0122 | corpse | n | 遺體 | mfu | ruumis | mayat | aya | A |
| C0490 | assemble | v | 組合 | konga | yhdistää | mengumpulkan | aylluy | A |
| C0497 | base | n | 基地 | msingi | tukikohta | dasar | tiksi | A |
| C0498 | be | v | 是 | wa | olla | makhluk | kay | A |
| C0499 | beat | v | 征服 | chapa | voittaa | mengalahkan | thatkiy | A |
| C0503 | begin | v | 開始 | anza | alkaa | mulai | qallariy | A |
| C0508 | birth | n | 出生 | uzazi | synnytys | kelahiran | wachay | A |
| C0517 | break | v | 結束 | vunja | kukistaa | menghentikan | p'akiy | A |
| C0519 | bundle | n | 包 | mtumba | pakkaus | bundel | q'ipi | A |

## Use
- *Calibration:* every concept's six words must be addressable (tokenise to the expected tokens; Mandarin words split into characters).
- *Debugging:* a concept whose words land far apart after the hash is a finding about the hash or about the concept; a concept the engine cannot address at all is a tokenizer or filter bug.
- *Fitting:* the set is the held-out check for the fit of English and the other languages to The Baseline ([05](05_the_baseline.md)): fit on other alignments, test on these.

## Open
- "Analogous" for the S/L pairs: the current relation is lexical (derivation, hypernymy), which gives 41 pairs; Cody's intended relation may be broader.
- Review by speakers of each language; replacement of failed concepts from the candidate pool (the next grade-A candidates are in `calibration_pool_all.tsv`).
