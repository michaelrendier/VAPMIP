> **2026-10-19:** `test_chinese_v2.0.bin` and `test_english_v2.0.bin` described below were deleted and replaced by the word-list bins `test_{chinese,english,chinese_english,english_chinese}_v2.bin` (see [11](11_baseline_mapping_zh_en.md)). The Finnish and Indonesian v2.0 stores below are unchanged.

# 09 — The test bins (Fresh Start v2.0)

Four single-language stores, each built separately with **its own alphabet**. Nothing here is multilingual: no word of one language is ever learned by another store. Swahili and Quechua are on hold.

The construction is the original one, with the alphabet changed per language: **Horner over the alphabet's digits, base = the alphabet's size**, then the exact-integer golden seed, `idx = seed64 · N >> 64`, `E = d* + (seed64>>11)/2⁵³ · (Ω − d*)`. The original alphabet was the 95 printable ASCII characters (base 95).

| store | binary (`build/v2/`) | alphabet | base | corpus (equal budget, 5.90 M tokens) | engine counts |
|---|---|---|---|---|---|
| `test_chinese_v2.0.bin` | `ptolemy_zh` (`-DALPHABET_TABLE`, `alphabet_zh.h`) | every assigned CJK ideograph in the engine's Han ranges (Unicode 15.0, category Lo), sorted by code point; digit = 1-based rank | 97 518 | 1 000 zh-tw Vital Articles, Han characters and `。！？，、；：` only | vocab 5 975, A 2 056 905 |
| `test_english_v2.0.bin` | `ptolemy_en` (`-DALPHABET_ASCII95`) | 95 printable ASCII; word = `[A-Za-z']` run | 95 | English Wikipedia, accents folded | vocab 24 940, A 9 373 394 |
| `test_indonesian_v2.0.bin` | `ptolemy_en` (same binary) | 95 printable ASCII | 95 | Indonesian Wikipedia, accents folded | vocab 24 972, A 8 728 395 |
| `test_finnish_v2.0.bin` | `ptolemy_fi` (`-DALPHABET_TABLE`, `alphabet_fi.h`) | `'` a–z å ä ö š ž | 32 | Finnish Wikipedia, other accents folded | vocab 25 000, A 15 457 197 |

A Han character is one token and one digit, so its address is its rank in the ideograph list. The whole repertoire (97 518 characters) maps to slots 0…24 999 and to `E ∈ [0.24600, 0.56714]`; every one of the 25 000 slots is reached, at most 5 characters share a slot (mean 3.9). The critical-line coordinate σ = ½ is the engine's own Noether forcing and holds for every slot.

**Versioning.** The number in the file name rises only when a Fresh Start is triggered. v1.0 (Chinese by code point, base `0x110001`) is archived in `SemPriCon/clean/archive/v1.0/`. English v2.0 is the v1.0 file with the version field 5 → 6 and nothing else (checked byte for byte), which shows the build is deterministic. State format v6 is v5 plus the rule that a store is only loaded by a build with the same state version.

**Rebuild** (HOME at a throwaway directory):

```
python3 tools/gen_alphabet.py                  # writes alphabet_zh.h, alphabet_fi.h
python3 tools/ingest_corpora.py                # corpora/text/{zh,en,id,fi}_v1.txt + TEXT_V1.sha256
# gcc ... -DALPHABET_TABLE -DALPHABET_HEADER='"alphabet_zh.h"' ... -o build/v2/ptolemy_zh   (fi likewise; en: -DALPHABET_ASCII95)
python3 -c "import ptol_bin; ptol_bin.write_ground('clean/test_chinese_v2.0.bin', version=6)"
build/v2/ptolemy_zh -q -c clean/test_chinese_v2.0.bin -l corpora/text/zh_v1.txt
```

**Footgun.** `-c <path>` only takes effect if the file already exists; otherwise `-l` saves to the protected `~/.ptolemy/monad_wordnet.bin`, which is not written, and the learning is lost. Create the ground-state file first.

**Status.** Frozen and read-only; sha256 in `SemPriCon/clean/MANIFEST.tsv`. Checked structurally only (stored slot = recomputed address; E in range). No lookup or speak has been run.

**Indonesian reduplication.** Plurals and distributives are written by repeating the word (`orang-orang`). The tokenizer splits on the hyphen, so the repeat reaches the engine as the same word twice in a row. The Indonesian corpus holds 52 324 full repeats of 2 858 words (`orang`, `negara`, `anak`, `kota` …), including fixed compounds that are not plurals (`masing-masing`, `rata-rata`, `undang-undang`, `laki-laki`). Not handled yet; it belongs to the Indonesian ruleset.
