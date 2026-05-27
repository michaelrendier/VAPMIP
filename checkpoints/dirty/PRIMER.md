# Dirty Checkpoints

State files from experimental runs, pre-fix eras, or non-prose corpus sources.
Not safe to use as a production base without review.
Binary assets are in GitHub Releases — see links below.

---

## monad_wordnet_v2_polluted_v1111.bin

| Field | Value |
|---|---|
| Format | PTOL v2 binary |
| Date | 2026-05-16 |
| Size | 147 MB |
| Vocab | 23,895 / 25,000 slots |
| A-edges | 9,600,426 |
| Words ingested | 34,494,302 |

**Why dirty:** Consonant-cluster pollution (1,939 tokens), trailing-apostrophe noise
from PDF OCR (VW diesel manual, TRADOC FM21-76, survival manual). 10.7% polluted
tokens by count — below the 20% rejection threshold but not clean.
Full assessment: `checkpoints/monad_v1.111_documents.assessment.json`.

**GitHub Release:** v1.111 → `monad_wordnet.bin`

---

## monad_sedenion_apisniff_v4.bin

| Field | Value |
|---|---|
| Format | Pickle (Python session) |
| Date | 2026-05-19 |
| Size | 111 MB |
| Vocab | 32,078 |

**Why dirty:** Built from Python stdlib API names + C source symbols via `APISniff`,
not from prose. The β-field encodes code topology, not language semantics.
Valid for `--address-map` / `--nearest` callable queries but not for speak().
Address book companion: `monad_sedenion_addresses.pkl`.

**GitHub Release:** v2.1-checkpoints → `monad_sedenion_apisniff_v4.bin`

---

## monad_sedenion_addresses.pkl

| Field | Value |
|---|---|
| Format | Python pickle |
| Date | 2026-05-19 |
| Size | 1.6 MB |

**Why dirty:** APISniff address book (callable name → sedenion address mapping).
Companion to `monad_sedenion_apisniff_v4.bin`. Useless without it.

**GitHub Release:** v2.1-checkpoints → `monad_sedenion_addresses.pkl`

---

## monad_prime_350k_sieve.bin

| Field | Value |
|---|---|
| Format | PTOL v4 binary |
| Date | 2026-05-17 |
| Size | 12 MB |
| Vocab | 328,071 / 350,000 slots |
| A-edges | 0 |
| Words ingested | 328,071 |

**Why dirty:** Prime number sieve table, not semantic corpus. Each "word" is a prime
number as a string. A-matrix is empty (no co-occurrence). Built as a P1 prime hash
reference table — zero-indices from sieve do not match the FNV-1a zero-indices used
in the current engine. Outdated once P1 is implemented.

**GitHub Release:** v2.1-checkpoints → `monad_prime_350k_sieve.bin`

---

## monad_prime_100k_sieve.bin

| Field | Value |
|---|---|
| Format | PTOL v4 binary |
| Date | 2026-05-17 |
| Size | 3.7 MB |
| Vocab | 100,000 / 100,000 slots |
| A-edges | 0 |

**Why dirty:** Smaller prime sieve (100k primes). Same caveats as the 350k version.
Kept as a faster-loading reference during P1 development.

**GitHub Release:** v2.1-checkpoints → `monad_prime_100k_sieve.bin`

---

## Pre-existing dirty files (vowelfix era)

The three `monad_wordnet_20260516_*_pre_vowelfix.bin` files (166 MB each) were
training snapshots taken during the vowelfix development run on 2026-05-16.
Each represents a different moment of the same training session before the
vowel normalization fix was applied. Kept for regression reference only.
Full assessments in `checkpoints/monad_wordnet_20260516_*.assessment.json`.

These are local-only — not uploaded to GitHub Releases due to size (3 × 166 MB).
