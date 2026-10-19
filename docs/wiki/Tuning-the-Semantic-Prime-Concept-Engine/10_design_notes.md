# 10 — Design notes (not built)

## Invisible prefix: tone, tense, conjugation (Cody, 2026-10-19)
**Requirement.** Three characters that the screen does not show but the slots do, placed at the start of a word, one each for **tone**, **tense**, **conjugation**. It follows the Demotic precedent, where the first character of the word carries its tone. The mechanism that fills and uses them is `repass()`, and it ships **with the conjugation mechanism, not with the address**. Nothing in the address, tokenizer or state format implements this yet.

**Constraints already in the code.**
- The 8 Fermat-space characters U+200B … U+2003 are taken: they are the separators that carry charge (`monad.c`, Fermat Emotional Lattice). The new characters must be disjoint from them.
- The tokenizer treats format characters (category Cf) as separators, so an invisible prefix would split the word from its own prefix. It would need a rule that attaches the three leading invisible characters to the word that follows.
- If the prefix is part of the hashed string, each inflected form lands in a different slot from its bare form: the three characters become the most significant Horner digits, and the golden seed spreads the result. Keeping a form near its lemma is then `repass()`'s job.

**Candidate alphabets (none chosen).** Unicode Tags U+E0020–U+E007E (95 invisible characters, a one-to-one copy of printable ASCII: three of them are three base-95 digits, 857 375 combinations); variation selectors U+FE00–FE0F and U+E0100–E01EF; U+200C, U+200D, U+2060, U+FEFF.

**Per-language meaning of the fields** is part of each language's ruleset (Chinese tone ≠ English tense).
