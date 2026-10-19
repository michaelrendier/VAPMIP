# Literature on the version 1.0 test bins (Fresh Start v1.0 → archived at the v2.0 Fresh Start)

Assessed 2026-10-19, read-only, from the archived files in this directory with `tools/assess_bin.py`
(JSON in `assessment/`) plus the measurements below. Every number is a measurement of the file; where
something is a hypothesis it says so.

## 1. What the two files are

| | `test_chinese_v1.0.bin` | `test_english_v1.0.bin` |
|---|---|---|
| sha256 | de8d7146…d7b8 | 6731ac57…82cd |
| size | 33,459,268 B | 150,896,163 B |
| header version | 5 | 5 |
| N (zeros) | 25,000 | 25,000 |
| vocab | 5,981 | 24,940 |
| A edges | 2,064,975 | 9,373,394 |
| word_count | 5,902,011 | 5,858,570 |
| corpus | `corpora/text/zh_v1.txt` | `corpora/text/en_v1.txt` |
| build | `ptolemy_zh_codepoint_horner` | `ptolemy_en_ascii95_v5` |
| alphabet / address | Unicode code point, Horner base 0x110001 mod 2⁶¹−1 | ASCII-95, Horner base 95 |

Each is the result of one Fresh Start: ground state → one learning pass over one corpus (equal ~5.9 M-token budget).
Provenance and the exact commands are in `MANIFEST_v1.0.tsv`.

## 2. What is in them (structure)

- **Vocabulary**: Chinese = 5,981 single Han characters (every entry length 1, all Unicode category Lo). English = 24,940 words, lengths 2–21+,
  mode at 7–8 letters, all ASCII.
- **Slot occupancy**: every word has its own slot in both files (0 slots with more than one word). Slots are spread uniformly:
  per-decile counts differ by ≤ 4 % (zh 583–614 of 5,981; en 2,489–2,497 of 24,940). English words of length ≥ 8 are NOT collapsed to low slots
  (fraction of slot < 1000 is 3.3–4.3 % at every length band; expectation 4 %).
- **E values** (golden-ratio position in [d*, Ω]): zh 0.24603–0.56709 (mean 0.4068); en 0.24601–0.56714 (mean 0.4066).
- **Strata**: all words are home=1, gen=1, prose_seen=1; age is 0 for all slots (no aging pass was run).
- **Field**: `occupied_zeros` reads 25,000 in both files but that is the ground state (β>0 everywhere), not vocabulary occupancy; the vocabulary
  occupies 5,981 / 24,940 slots. β saturated at 7.552: zh 312 slots, en 104. Entropy of β: zh 10.39 bits (71.1 % of max), en 12.54 (85.8 %);
  Gini zh 0.832, en 0.788. Median β zh 7.6e-5, en 0.051 (zh β is far more concentrated).
- **Edges**: zh mean weight 0.0026, max 1370.6 (是–的); en mean 3.3e-4, max 155.7 (implication–hendrik). Strongest zh pairs are real collocations
  (研究, 主權, 是的); the strongest en pairs are rare-word pairs from one article (implication, hendrik, sibilants, pelham).

## 3. Known properties and limits

1. **Chinese addressing differs from the later scheme entirely.** v1 hashed code points with Horner base 0x110001 mod 2⁶¹−1. Against `test_chinese_v2.0.bin`
   (per-alphabet bijective base 97,518): 0 of 5,897 shared characters sit in the same slot. v1 Chinese slots are not comparable to anything built later.
2. **English addressing is identical to the later scheme.** `test_english_v2.0.bin` has the same 24,940 words, all in the same slots (24,940 / 24,940),
   same word_count, same header layout; only the header version differs (5 → 6). The v1 → v2 change for English is the version number, not the mapping.
3. **Vocabulary differs for Chinese**: 84 characters in v1 are absent from v2 and 78 in v2 are absent from v1 (all Lo). Cause not established;
   hypothesis: slot-collision eviction under the two different hash schemes (not tested).
4. **The poison/pollution tools are English-shaped.** `eval_checkpoint` flags 5,981 / 5,981 Chinese entries as "single-char" and the sanitiser files them
   as Q:garbage (100 %). That is a tool limitation, not a finding about the file. English: 60 polluted (0.24 %: 41 consonant-only, 24 no-vowel,
   18 consonant-cluster-3, 16 hex-string, 4 low-vowel-ratio); sanitiser quarantine 27 (0.11 %).
5. **English is wide, not clean**: 14,796 words are tier B (candidate, evidence pending), 9,176 in WordNet, 909 proper nouns, 32 function words.
   No stopword or frequency floor beyond the corpus builder's own.
6. **Header version 5.** The current engine refuses it (`state.c`: version < 6). To read these files use `tools/ptol_bin.py` (`load`), not the current C build;
   to reproduce them use the archived binaries beside this file.
7. **Not examined**: no speak/lookup was run on either file; no calibration set (`calibration_v1_en_zh.tsv`) score was computed here.

## 4. Reproduce / verify

    awk -F'\t' '/\.bin\t/{print $2"  "$1}' MANIFEST_v1.0.tsv | sha256sum -c   # run inside this directory
    python3 tools/assess_bin.py clean/archive/v1.0/test_<chinese|english>_v1.0.bin out.json

## 5. Role in the Fresh Start Protocol

These two files are the frozen v1.0 pair. They are read-only and never edited; the version in the name rose to 2.0 only because a Fresh Start was triggered.
The v2.0 pair is the reference for what changed: Chinese address scheme (§3.1), English unchanged apart from header (§3.2).
