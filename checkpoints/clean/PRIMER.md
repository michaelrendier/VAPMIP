# Clean Checkpoints

State files that are mathematically valid, stable, and safe to load.
No known corpus pollution. BAO convergence verified or expected.
Binary assets are in GitHub Releases — see links below.

---

## monad_wordnet_v4_20260519.bin

| Field | Value |
|---|---|
| Format | PTOL v4 binary |
| Date | 2026-05-19 |
| Size | 104 MB |
| Vocab | 24,485 / 25,000 slots |
| A-edges | 6,825,748 |
| Words ingested | 121,914,388 |
| Engine version | ptolemy-monad v1.218 |

**Corpus:** WordNet 3.1 + Gutenberg English corpus (overnight teach_english.sh run).
Post-vowelfix. Highest word-count state before the 2026-05-27 fresh start.
The most thoroughly trained English field in the archive.

**Load:** `python3 monad.py --load-bin ~/.ptolemy/clean/monad_wordnet_v4_20260519.bin`

**GitHub Release:** v2.1-checkpoints → `monad_wordnet_v4_20260519.bin`

---

## monad_english_ptol_20260526.ptol

| Field | Value |
|---|---|
| Format | Pickle (Python session state) |
| Date | 2026-05-26 |
| Size | 35 MB |
| Source | teach_english.sh overnight run |

**Corpus:** Gutenberg 22-book English canon (KJV, Shakespeare, Moby Dick, etc.)
+ system man pages + local prose. Last saved state before the 2026-05-27 fresh start.
Compatible with `monad.py --load-bin`.

**GitHub Release:** v2.1-checkpoints → `monad_english_ptol_20260526.ptol`

---

## monad_English_v2_baseline.bin

| Field | Value |
|---|---|
| Format | PTOL v2 binary |
| Date | 2026-05-16 |
| Size | 12 MB |
| Vocab | 14,164 / 25,000 slots |
| A-edges | 766,027 |
| Words ingested | 1,608,903 |

**Corpus:** English prose baseline — early training run, smaller A-matrix.
Reference point for regression testing. Already in GitHub Release v1.113.

**GitHub Release:** v1.113 → `monad_English.bin`
