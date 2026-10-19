# corpora/ — the Unicode test bed's data (data itself is gitignored; fetch scripts and MANIFEST.tsv are committed)

Test bed: English (US, UK) + Mandarin, Swahili, Finnish, Indonesian, Quechua. Chinese first, as the baseline: **written Mandarin, Traditional script; no Cantonese, Hokkien or Min sources**.

| path | source | licence | status |
|---|---|---|---|
| `lexicon/kaikki-*.jsonl` | Wiktionary extracts, kaikki.org (wiktextract; cite Ylonen 2022) | CC BY-SA 4.0 + GFDL | Quechua, Swahili, Indonesian, Chinese done; Finnish and English running (`fetch.sh` resumes) |
| `lexicon/varcon*.txt` | VarCon US/UK spelling pairs (Atkinson, Titze) | permissive (see README) | done |
| `wikipedia/*.parquet` | Wikimedia dump 20231101 via Hugging Face | CC BY-SA 4.0 + GFDL | queued in `fetch.sh` |
| `tatoeba/` | Tatoeba sentences + translation links | CC BY 2.0 FR | queued in `fetch.sh` |
| `zh/moedict/` | 教育部重編國語辭典修訂本 (g0v/moedict-data) | CC BY-ND 3.0 TW (text unchanged; format conversion allowed per MOE reading in its README) | done: 161,194 entries |
| `zh/classical/` | gujilab/chinese-classical-corpus: 說文解字, 爾雅, 四書 | CC0 | done; Simplified-mixed (12–25 % of characters change under s2t), convert before use |
| `zh/structure/` | Unihan, makemeahanzi dictionary, cjkvi-ids, CC-CEDICT | Unicode License; see MANIFEST | done |
| `zh/vital/` | English Wikipedia Level-3 Vital Articles → zh.wikipedia (zh-tw variant), 1,000 topics in 11 categories | CC BY-SA 4.0 | running (`tools/zh_vital_fetch.py`) |
| `zh/src/opencc-root` | OpenCC 1.1.7 from the Ubuntu .deb files (`apt-get download`, no root) | Apache-2.0 | done; `tools/opencc_local.sh s2twp` |

**Closed doors (recorded, not opened):** Leipzig Corpora Collection (Anubis bot challenge on every page); dictionary.writtenchinese.com has no bulk export and renders CC-CEDICT, so the underlying CC-CEDICT was fetched directly. Wikimedia's API sent HTTP 429 once after a burst; the fetcher now honours Retry-After, waits at least 2.5 s between requests and stops after four consecutive 429s.
**Excluded on purpose:** `g0v/moedict-data-twblg` (Hokkien), Cantonese and Min sources, Debian `fortunes-zh` (Simplified), `libchewing3-data` (compiled binary only).
