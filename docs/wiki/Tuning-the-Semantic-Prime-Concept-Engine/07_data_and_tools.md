# 07 — Data and tools

Everything is under `VAPMIP/SemPriCon/`. Data is gitignored; the fetch scripts, `corpora/MANIFEST.tsv` (source URL, size, sha256, licence, date) and `corpora/README.md` are committed.

## Data
| path | what | licence |
|---|---|---|
| `corpora/lexicon/kaikki-{English,Chinese,Swahili,Finnish,Indonesian,Quechua}.jsonl` | Wiktionary extracts with glosses, etymology, translations | CC BY-SA 4.0 + GFDL |
| `corpora/lexicon/varcon.txt` | US/UK spelling pairs | permissive |
| `corpora/wikipedia/*.parquet` | Wikipedia, dump 20231101 | CC BY-SA 4.0 |
| `corpora/tatoeba/` | aligned sentences | CC BY 2.0 FR |
| `corpora/zh/` | The Baseline sources (see [05](05_the_baseline.md)) | per `MANIFEST.tsv` |

**Closed doors:** Leipzig Corpora Collection (bot challenge); Wikimedia API rate limit (the fetcher honours Retry-After). **Excluded on purpose:** Hokkien dictionary, Cantonese and Min sources.

## Tools (`SemPriCon/tools/`)
| tool | does |
|---|---|
| `corpora/fetch.sh`, `corpora/fetch_zh.sh` | resumable, rate-limited downloads, recorded in the manifest |
| `zh_vital_fetch.py` | topic-labelled Traditional corpus from the Vital Articles list |
| `zh_census.py` | what the Baseline sources contain (writes `derived/zh_census.json`) |
| `vocab_build.py` | per-language vocabularies; words exclusive to one language; borrowed/inherited flags |
| `text_build.py` | equal-budget text per language; en-GB / en-US labelled corpora; Tatoeba pairs |
| `opencc_local.sh` | OpenCC from the Ubuntu packages, no root (`opencc_local.sh s2twp`) |
| `en_translations.py`, `concept_index.py`, `calibration_build.py` | the calibration set ([06](06_the_calibration_set.md)) |
| `monad_pyu.py`, `ptol_bin.py`, `verify_*.py` | the port, the store reader, the checks ([08](08_verification.md)) |


## Test-bin tools
`tools/ingest_corpora.py` builds `corpora/text/{zh,en,id,fi}_v1.txt` (equal token counts). `tools/gen_alphabet.py` writes `alphabet_zh.h` and `alphabet_fi.h`. `tools/calibration_v2.py` builds the Finnish/Indonesian candidate columns. The binaries are built from `src/PtolC_unicode` with `-DALPHABET_ASCII95` or `-DALPHABET_TABLE`. Details: [09](09_the_test_bins.md).
