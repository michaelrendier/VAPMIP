# 08 — Verification

| check | command | passes when |
|---|---|---|
| the 2026-05 engine, binary vs port | `python3 SemPriCon/tools/verify_against_c.py` | 8 of 8 replies byte-identical |
| learning, 2026-05 | `python3 SemPriCon/tools/verify_learn_against_c.py` | vocabulary, edge keys, weights exactly equal |
| **Unicode build, binary vs port** | `python3 SemPriCon/tools/verify_unicode_against_c.py` | 8 multilingual texts (Finnish, Mandarin, Swahili, Indonesian, Quechua, US and UK English, a mixed text with curly quotes, ellipsis, `İ`) learn to an identical state; replies identical |
| old stores refused | `ptolemy -c <v4 store> -W x` | prints "version 4 … Refusing." |
| address resolution | `python3 SemPriCon/tools/unicode_address_measure.py` | long words reach distinct slots (Swahili ≥ 8 letters: 6 355 distinct of 7 322; the 2026-05 build: 1) |

**Weak:** the speak-reply comparison runs on tiny stores (most replies empty). It must be repeated on a store learned from the real corpus before it counts.
**Not verified:** NFC handling, tokens outside the Basic Multilingual Plane beyond Han, and the C locale independence (the tables make it independent; no test changes the locale).
