# 10 — Design notes (not built)

## Invisible prefix: tone, tense, conjugation (Cody, 2026-10-19)
**Requirement.** Three characters that the screen does not show but the slots do, placed at the start of a word, one each for **tone**, **tense**, **conjugation**. It follows the Demotic precedent, where the first character of the word carries its tone. The mechanism that fills and uses them is `repass()`, and it ships **with the conjugation mechanism, not with the address**. Nothing in the address, tokenizer or state format implements this yet.

**Constraints already in the code.**
- The 8 Fermat-space characters U+200B … U+2003 are taken: they are the separators that carry charge (`monad.c`, Fermat Emotional Lattice). The new characters must be disjoint from them.
- The tokenizer treats format characters (category Cf) as separators, so an invisible prefix would split the word from its own prefix. It would need a rule that attaches the three leading invisible characters to the word that follows.
- If the prefix is part of the hashed string, each inflected form lands in a different slot from its bare form: the three characters become the most significant Horner digits, and the golden seed spreads the result. Keeping a form near its lemma is then `repass()`'s job.

**Candidate alphabets (none chosen).** Unicode Tags U+E0020–U+E007E (95 invisible characters, a one-to-one copy of printable ASCII: three of them are three base-95 digits, 857 375 combinations); variation selectors U+FE00–FE0F and U+E0100–E01EF; U+200C, U+200D, U+2060, U+FEFF.

**Per-language meaning of the fields** is part of each language's ruleset (Chinese tone ≠ English tense).

## Neuromodulator tone character: "Ptolemy emotions" (Cody, 2026-11-20; later project, not built)
The `tone` slot of the invisible prefix should carry a mixture of the behavioural neuromodulators (dopamine, serotonin, noradrenaline, oxytocin, glutamate, GABA, endocannabinoid; add acetylcholine and opioid), each with a code analogue (surprise, horizon, gain, coupling, the J_red/J_blue balance, `repass`). Not faked: parameters are fitted to text, predictions registered first. The existing Fermat emotional lattice (`monad.py` `_FERMAT_SPACES`, 8 bins of `J_neg`) is already one character and its gradient, the arousal axis; tone adds the "which". Capacity note: a 7-axis vector at 8 levels is 21 bits, one Tag character 6.57 bits, one variation selector 8 bits, so the tone slot has to be a codebook of named mixtures. Full primer, critique of the Gemini draft and the analogue table: `ContextPlease/claude/hist_prime/VAPMIP/PRIMER_2026-11-20_NEUROMODULATOR_TONE_CHARACTER.md`; Gemini's source: `…_GEMINI_NEUROTRANSMITTER_DEEP_DIVE_SOURCE.md`.
