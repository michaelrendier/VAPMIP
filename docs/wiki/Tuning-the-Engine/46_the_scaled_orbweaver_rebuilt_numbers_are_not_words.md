## Phase 46: The Scaled Orbweaver Rebuilt, Numbers Are Not Words, Imitation (2026-11-25)

*Claude Sonnet 5.5, at Cody's direction: "this is a child we have to teach how to speak English. Numbers are not words. Numbers get treated differently. Different machinery."*

---

### The phase

The orbweaver bench of Phase 35 (`boxkite_orbweaver_monad.py`, kept as it was) planned a web and filled it with **template prose** ("it is a kind of {0}"; first replies such as "the part instanced the theory"). `scaled_boxkite_orbweaver_monad.py` keeps the plan (a subclass: room shape, reach, turbulence rule, connective lexicon, lemniscate tense) and replaces every piece of prose with the window.

### What changed

- **The sentence vector.** The old `_sniff` summed `hash(w) % 19`; Python's string hash changes between processes, so the plan changed from run to run. The rebuild sums the real nineteen-count vectors of the words (`weave_cycle.word_web`). `tests/test_scaled_orbweaver.py` checks the sum and determinism.
- **One step, three scales** (`weave_cycle.web_step`): word (senses; reversal = a wider context), sentence (candidates; reversal = re-pick under the antagonist tone of the strut: GLU|GABA, DA|5HT, NE|OXT), paragraph (radii; the pivot and wrap). Turbulence is the orbweaver's own rule: three or more within half of the strongest. A reversal is kept only if it takes a larger share (the sharper pick wins).
- **Numbers are not words** (`numeric.py`). A numeral has no lexicon entry, no synset, no probability under the word bigram, no slot in a frame: `numeric.split` removes numerals, codes (`x2`, `h264`, `3d`) and versions (`3.10.3`) before any word is read; `NumberChannel` keeps them (counts by kind, decade, repeats; `numbers.json`). `vocab_store.content_lemmas` no longer counts digit tokens as lemmas. Number words ("three") stay words (open).
- **Imitation.** A child repeats what it heard: `SedenionWindow.imitation` weights the speaker's words (and their lemmas) above the best candidate. The first version produced "rulesed" (a surface form inflected twice) and "the breaking bridged the farmer" (a heard word used in the wrong part of speech); the lemma fix is in, the part-of-speech problem is not.
- **`audit()`**: seven named checks (no numerals; no template phrase; tense = station; tense marker present; every word known or heard; a pivot only when turbulent; stations are the three).

### Measured

175 tests passed after the rebuild (`tests/test_numeric.py`, `test_scaled_orbweaver.py`, `test_weave_cycle.py`, `test_responder.py`). The audit's seven checks hold on three test prompts. `responder.Responder` and `Harness.respond` run the whole path; the first live turns on a real conversation are not yet observed.

### Not established

Reply quality (the replies are child-grade); whether imitation helps or hides the model; part-of-speech-aware imitation.

### Pointers

`VAPMIP/scaled_boxkite_orbweaver_monad.py`, `weave_cycle.py`, `numeric.py`, `responder.py`; Phase 35 and 43 for the model and the stub. VAPMIP commit `ce8dc16`; copies in `Currentwork/Wernicke/src/` and `Currentwork/Broca/src/` (the root files are the originals).
