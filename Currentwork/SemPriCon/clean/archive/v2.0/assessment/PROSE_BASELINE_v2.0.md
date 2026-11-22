# Prose-word baseline — all test bins (assessed 2026-10-19)

Tool: `tools/assess_prose.py` (read-only). Per-bin detail: `*_prose.md` / `*_prose.json` beside this file (v1.0 pair: `archive/v1.0/assessment/`).
Purpose: a language-by-language record of how much of each bin's vocabulary is a prose word of its own language, for the calibration check at the next Fresh Start.

## How the assessment chooses what applies (explore first)

1. **Explore.** Script census of the vocabulary; unit type = *logographic* if ≥ 95 % of entries are single Han code points, else *alphabetic*.
2. **Language.** Alphabetic bins: each entry is scored by a character-trigram model trained on each dictionary's own words (27,000 words per language, equal footing);
   the bin's language is the plurality. Dictionary coverage is reported too but is not the vote (the Wiktionary extracts differ ~40-fold in size: Indonesian 27 k headwords, English 1.04 M).
3. **Choose tests.** Letter inventory, vowel presence, longest consonant run and longest identical-letter run are measured on that language's dictionary words; a shape test
   is applied only if ≥ 99.5 % of the dictionary's own words pass it, with limits at the dictionary's 99.9th percentile. Digits always fail. Logographic bins use one rule: a single Han code point, category Lo.
4. **Grade.** Order: shape failure → NONPROSE:shape; dictionary word entry → PROSE:dict; dictionary lists only as a proper noun → PROSE:name; dictionary lists only as affix/symbol/redirect → NONPROSE:dict-*;
   listed word of another test language and trigram-attributed to it → NONPROSE:foreign-*; dictionary silent: capitalised mid-sentence ≥ 2× and ≥ 4× its lowercase uses in the language's own corpus → UNLISTED:name-like;
   lowercase ≥ 3× in the corpus → PROSE:attested; otherwise UNLISTED (foreign-looking or native-looking, rare).

## Results

| file | vocab | language | dict word | dict name | attested in text | name-like (unlisted) | native-looking rare | foreign-looking | foreign (dict-confirmed) | shape/affix/redirect | prose % | non-prose % |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| test_chinese_v2.0.bin | 5,975 | Chinese | 5,809 | 0 | 0 | 0 | 14 | 0 | 0 | 152 | 97.22 | 2.54 |
| test_english_v2.0.bin | 24,940 | English | 12,334 | 3,242 | 125 | 2,096 | 4,296 | 2,705 | 123 | 19 | 62.96 | 0.57 |
| test_finnish_v2.0.bin | 25,000 | Finnish | 3,139 | 273 | 3,207 | 1,949 | 12,826 | 2,595 | 854 | 157 | 26.48 | 4.04 |
| test_indonesian_v2.0.bin | 24,972 | Indonesian | 2,413 | 156 | 1,995 | 4,148 | 7,562 | 5,002 | 3,674 | 22 | 18.28 | 14.8 |
| test_chinese_v1.0.bin | 5,981 | Chinese | 5,811 | 0 | 0 | 0 | 14 | 0 | 0 | 156 | 97.16 | 2.61 |
| test_english_v1.0.bin | 24,940 | English | 12,334 | 3,242 | 125 | 2,096 | 4,296 | 2,705 | 123 | 19 | 62.96 | 0.57 |

(`attested in text` = prose by usage where the dictionary is silent, typically inflected forms. `foreign-looking` is a trigram suspicion only; `foreign (dict-confirmed)` has dictionary support.)

## What the baseline says, per language (own-language terms)

- **Chinese** (Traditional, single Han characters): 97.2 % are dictionary characters. The 2.5 % flagged are `soft-redirect` entries — Japanese new-form and Simplified variants (舎 区 仏 変 …) that Wiktionary
  redirects to the Traditional form; they are not Traditional-Chinese prose characters, so they sit in the store as variant glyphs. 14 characters (0.23 %) are not in the dictionary at all (rare/variant).
- **English** (ASCII-95): 49.5 % dictionary words + 13.0 % dictionary proper nouns + 0.5 % attested; 8.4 % more are name-like by capitalisation. 0.57 % fail the shape tests —
  Wikipedia markup residue (`archipelago'''s`, `wine'''s`, `scaleno'''hedron`), Roman numerals (`xxiii`, `xviii`), stretched spellings (`goodbyeee`, `yooooou`). 17.2 % are unlisted and rare (the long tail of Wikipedia vocabulary).
- **Finnish** (32-letter alphabet): the dictionary lists only 12.6 % of the 25 k entries because Finnish is agglutinative and the extract lists lemmas and a subset of forms; a further 12.8 % are attested as lowercase prose in the corpus,
  7.8 % are name-like, 51 % are unlisted and rare (long compounds and case forms). 0.5 % fail the letter inventory (non-Finnish letters), 3.4 % are other-language words (English, Indonesian) in the store.
- **Indonesian** (ASCII-95 build): the dictionary is small (27 k) so only 9.7 % match; **14.8 % non-prose by this measure**, the largest of the four: 12.8 % are English words and 1.9 % Finnish words that sit in the store (Wikipedia text carries untranslated English/foreign phrases),
  plus 16.6 % name-like. Reduplications written with a hyphen (`orang-orang`) are split by the tokenizer and so appear as the base word.

## Limits of this measurement

- The dictionary is Wiktionary (kaikki extract), not a closed authority; a word absent from it is **UNLISTED, not wrong**. Only the NONPROSE classes carry a verdict.
- The trigram language attribution is weak for short and rare words (it assigns ~18 % of English entries to Indonesian/Finnish); it is used for the language vote (a plurality over thousands of words) and as a suspicion label, never as the only basis for NONPROSE.
- Proper nouns count as prose words of the language (PROSE:name); a stricter reading would drop them — the counts are separate for that reason.
- v1.0 and v2.0 English are identical in vocabulary and give identical grades; the v1.0 → v2.0 Chinese difference (84 vs 78 characters) is within the 0.1 % band here.
