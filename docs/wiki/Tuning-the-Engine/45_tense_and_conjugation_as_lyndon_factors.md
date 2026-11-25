## Phase 45: Tense and Conjugation as Lyndon Factors (2026-11-25)

*Claude Sonnet 5.5, at Cody's explicit go ("do the lyndon conjugation, then 1-3"; the stub of 2026-10-14 had been waiting for it). The design is the author's engineering choice of this day, not a finding.*

---

### The phase

`lyndon_conjugation.py` had a real Lyndon core (`duval`, `is_lyndon`, `least_rotation`, `primitive_root`, `verify`: every word of length ≤ 10 over {a, b} factors correctly, 0 failures) and two stubs that raised `NotImplementedError`. This phase builds them.

### The verb group as a factor list

English fixes the order of a verb group: TENSE (with an optional modal), have + -en (perfect), be + -ing (progressive), then the main verb. Ranks: TENSE 4 > MODAL 3 > PERF 2 > PROG 1 > V 0. A group is the word of its ranks in non-increasing order; its Lyndon factors (`duval`) are its features. `divides`, `gcd` and `lcm` act on the exponents: gcd(past perfect, past progressive) = past; lcm = past perfect progressive. Realisation is affix hopping (`conjugates`): a PERF factor makes the next word -en, a PROG factor the next word -ing, the modal (or the first verbal word) carries the tense; `be` and `have` are tabled, other verbs come from `lemminflect`. `conjugates('see', 'future progressive')` = will be seeing. `inflection_frame` returns the surface words and the two marker codes the window writes (the tense carrier, and the form of the main verb).

**What the Lyndon view does and does not add.** With distinct ranks every factor is one letter, so the factorisation is a sort. It contributes the canonical form and the factor algebra, plus the necklace and primitive-root tools used on a paragraph's tense stream (`tense_phrases`, `tense_monotony`, `rotate_tense`; the past → present → future cycle is the orbweaver's lemniscate).

### Where the tense comes from (`tenseplan.py`)

A name (`past`, `future perfect progressive`, …); `auto`: the orbweaver's lemniscate station by depth (`OrbWeaverMonad._tense`: the deepest loop is the past lobe, the shallowest the future lobe, the middle the node); `mirror`: the speaker's own tense. `tests/test_lyndon_conjugation.py` checks `lemniscate_tense` against the orbweaver for every (depth, reach) with reach ≤ 5.

### Measured

15 tenses × any verb: surface, tense code and conjugation code agree between `lyndon_conjugation.py` and, since Phase 47, the C (`cv_inflect`) for 460 verbs × number × person. Window: `write(tense=…)` accepts compound names; the AUX slot of the `sva` frame follows the tense when it is not present. The `_repass` default is unchanged (present), so the earlier tests did not move.

### Not built

Negation, questions and do-support; number agreement other than singular; a boundary rule for Lyndon factors of whole sentences (the Collatz boundary effect recorded in `docs/wiki/Lyndon-Factorisation.md` is untouched, because the factors here are of the verb group, not of a token stream).

### Pointers

`VAPMIP/lyndon_conjugation.py`, `tenseplan.py`, `docs/wiki/Lyndon-Factorisation.md` (§ *Built 2026-11-25*). VAPMIP commit `11e6ce7`.
