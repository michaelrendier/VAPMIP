# 09 — The test bins (Fresh Start v1.0)

Two single-language stores, built separately, each with its own alphabet. Nothing here is multilingual: no word of one language is ever learned by the other store.

| | `test_chinese_v1.0.bin` | `test_english_v1.0.bin` |
|---|---|---|
| binary | `build/zh/ptolemy_zh` | `build/en/ptolemy_en` (`-DALPHABET_ASCII95`) |
| alphabet | Unicode code points; Horner base `0x110001` mod 2⁶¹−1 | the 95 printable ASCII characters; Horner base 95 (wraps mod 2⁶⁴ past nine letters) |
| tokenizer | Unicode letters; each Han character is a token | `[A-Za-z']` runs only; any other code point separates words |
| corpus | `corpora/text/zh_v1.txt`: the 1 000 zh-tw Level-3 Vital Articles; only Han characters and `。！？，、；：` kept (5 902 011 tokens) | `corpora/text/en_v1.txt`: English Wikipedia, accents folded, ASCII only, cut at the same token count as the Chinese file |
| engine counts | vocab 5 981, A edges 2 064 975 | vocab 24 940, A edges 9 373 394 |

Both use the same slot count (N = 25 000), the same seed (`seed64 = v · 0x9E3779B97F4A7C15 mod 2⁶⁴`, `idx = seed64 · N >> 64`) and the same engine (state version 5). The only deviation from `eb28ce8` in the English build is that exact-integer seed: the original float seed sends every word of 8+ letters to slot 0.

**Versioning.** The version in the file name rises only when a Fresh Start is triggered. A Fresh Start archives the current pair, writes a new ground-state file, and re-ingests: `v1.0` → `v2.0`. A pair is never edited after it is written; it is read-only and its sha256 is in `SemPriCon/clean/MANIFEST.tsv`.

**Rebuild** (HOME pointed at a throwaway directory, so nothing touches `~/.ptolemy`):

```
python3 SemPriCon/tools/ingest_corpora.py                # writes corpora/text/{zh,en}_v1.txt + TEXT_V1.sha256
python3 -c "import ptol_bin; ptol_bin.write_ground('clean/test_chinese_v1.0.bin', version=5)"   # same for english
build/zh/ptolemy_zh -q -c clean/test_chinese_v1.0.bin -l corpora/text/zh_v1.txt
build/en/ptolemy_en -q -c clean/test_english_v1.0.bin -l corpora/text/en_v1.txt
```

**Footgun.** `-c <path>` only takes effect if the file already exists. If it does not, `-l` saves to `~/.ptolemy/monad_wordnet.bin`, which is protected and is not written, so the learning is lost. Always create the ground-state file first, as above.

**Status.** Both files were ingested and frozen. No lookup or speak has been run on either. They are the baseline that the comparison starts from.
