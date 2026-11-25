# Forward Propagation of Information

### Teaching The Maths how to speak English: the Monad and the Harness, in Python and in C

**Cody Michael Allison** (Michael Rendier), independent researcher · the.wandering.god@gmail.com · ORCID 0009-0007-7239-6760\
**Written by an AI assistant:** Claude Sonnet 5.5 (`claude-sonnet-5-5`), with the author's `cs-paper-code-conventions` skill running (`ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md`)\
**Date:** @@DATE@@ · **Status:** rewritten from the current machinery · **Code:** `VAPMIP`, commit `@@HEAD@@` · **Paths:** `REPO/directory/file` lives under `https://github.com/michaelrendier/`

---

> ## Read this first: who wrote this, and how
>
> **The assistant.** This paper was written by a transformer language model, Claude Sonnet 5.5 (`claude-sonnet-5-5`), with the author's `cs-paper-code-conventions` skill active; the skill decides how code is shown (§10 of the skill: the CS engineering white paper). Every number that comes from code was produced by `VAPMIP/paper/evidence.py` when `VAPMIP/paper/make_paper.py` last ran; none is typed in by hand. Listings are extracted from the source by name, never retyped.
>
> **The author.** The author is a software engineer, not a trained mathematician or linguist, and says so. Every statement not attributed to a cited source should be read as unverified until an expert has checked it. The author does not tell the assistant what result he hopes for; tasks are given as measurements ("run it", "chase that to its source"). That is a safeguard, not a guarantee; the real safeguards are fresh runs, exact comparison where an exact answer exists (§9), and failures kept in the text (§11).
>
> **Licence and symbols.** The code and this method are proprietary: Copyright (c) 2026 Cody Michael Allison, all rights reserved (`VAPMIP/LICENSE`); the mathematics behind them is published separately under the GNU licence outside VAPMIP. In the code, `OMEGA_ZS` = 0.56714 is A_π = W(1), `D_STAR` = 0.24600 is the rounded Ω_ζΣ = d*, and α is the fine-structure constant; nothing in this paper depends on them.
>
> **What kind of paper this is.** An engineering white paper about the machinery that runs today. It has no proofs and makes no prediction. It does not narrate how the machinery was reached; earlier versions are pointed at in the appendix, next to the description of ContextPlease, and nowhere else.

---

## Abstract

Language models have become costly in four ways at once: they draw large amounts of power; they are trained by backpropagation, which keeps development on clusters and off the developer's laptop; they spend compute to rediscover relations between words that WordNet already records; and their weights and training data are closed, so a reader cannot see why a model says what it says. This paper describes the Monad and the Harness, built to avoid all four. A prompt is read by a Harness that removes numbers (numbers are not words), prices every word against the speaker's own usage, reads the speaker's state into seven neurotransmitter axes, and measures the cost of the reply against the cost of the speaker's words. The Monad, a sixteen-slot window on a scaled box-kite, plans a reply as a web of radii taken from WordNet's relation counts, picks every word of every sentence itself under seven tones, and conjugates verbs as Lyndon factor lists. There is no gradient descent and no trained weights in the Monad; the only fitted model is a ridge regression for the user's state (45,448 TF-IDF features, 14 outputs). Both halves exist twice: in Python, where each mechanism is tested first, and in C (`ptol.c`, `monad_harness.c`), ported afterwards and checked against the Python by @@PARITY@@ parity tests (@@SUITE_PASSED@@ tests in all). A C turn takes about ⟦@@C_MS@@⟧ ms on one laptop CPU with no network and no GPU. The replies are not yet good English; §11 records, with transcripts, where they fall short and where the C and the Python differ.

---

## 1. Problem and approach

Four constraints bound the work. **Power:** public figures for one typical language-model query are 0.24 to 0.34 Wh (Vahdat et al., 2025; Altman, 2025; You, 2025; copies in `paper/references/`), and training is far above that. **A hard wall:** training by backpropagation puts development on clusters; a developer on one laptop can only use what others trained. **Wasted compute:** a model that learns from raw text re-derives the relations between words (hypernym, part, cause, entailment) that a lexical resource (Miller, 1995; Fellbaum, 1998; cited, not fetched) records directly. **Opacity:** with closed weights and data, a reader cannot ask why a word was chosen.

Making a model smaller does not remove any of the four, because each follows from learning the language from text by gradient descent. We remove the cause. Language is split into two kinds of object. A *word* is discrete: it has a WordNet entry, a part of speech, nineteen relation counts and a probability under the speaker's usage. Context is a *flow* the words are placed along: a web of radii, each radius a relation WordNet already counts. The Monad picks one word at a time from the neighbourhood of the words it has heard, under tones derived from the speaker's state; the Harness owns everything that is measured about the speaker and about the reply. Numbers are a different kind of object and take a different path (§4).

Every mechanism is written and tested in Python first, then ported to C; the port is checked against the Python (§9). The charts in §9 (Figures 1 and 2) show the whole of both halves. Sections 3 to 8 give the mechanisms in the order the code runs, §10 shows measurements as transcripts, §11 lists what does not work, and the appendix gives the files used.

---

## 2. Labels and conventions

`ESTABLISHED` = mathematics or computer science that predates this work, cited; `OURS` = built for this work; `THEORETICAL` = designed, not reduced to running code; `OPEN` = a question this paper cannot settle; the suffix `:CALCULATED` = a number the paper's own code produced. Maths is written in Unicode; identifiers are the code's own. A short mechanism that is the contribution is shown as a numbered **Listing**, extracted verbatim by name and shown with its source path and lines (convention B); an interactive check is a literal `>>>` transcript produced by running the module (convention D); a long mechanism is named and pointed at (convention A); a drawing of control flow is a numbered **Figure** (convention G).

---

## 3. The store and the scalar word (`wordnet_boxkite.py`, `monad3_c.bin`, `voice_lex.bin`)

`ESTABLISHED` input, `OURS` encoding. A word's semantic centre is its first WordNet synset's nineteen relation counts (hypernyms, instance hypernyms, hyponyms, … usage domains), each compressed by `compress_count` and kept as an exponent over a fixed list of nineteen primes (`WordNet box-kite`; `wordnet_boxkite.context_vector`, `gamma_radial`). The scalar box-kite is the static object: one word, one vector; it never moves. `gamma_radial` folds the vector to one real in (−1, 1); the C port is `monad3_gamma_radial` in `PtolC/ptol.c`, whose comment records agreement with the Python value on one word to six places (not re-run here).

The C monad reads three stores, all next to the binary and none written by the voice:

| file | what | size (this run) |
|---|---|---|
| `monad3_c.bin` | the co-occurrence matrix (compressed sparse rows) over English words, a WordNet and a phonetic table in one mmap-able file (`PtolC/monad3c.h`) | @@MONAD3_MB@@ MB |
| `voice_lex.bin` | every single-word WordNet lemma: the parts of speech it has, and the 19 counts of its first synset (`PtolC/tools/export_c_monad_data.py --lex`) | @@LEX_MB@@ MB |
| `user_state.bin` | the usage ridge: TF-IDF 1–2-gram vocabulary, idf, 45,448 × 14 coefficients, calibration gain, base and spread | @@US_MB@@ MB |

`voice_lex.bin` exists because `monad3_c.bin` keeps one lossy entry per word (the word "dog" is stored as a verb; "rules" is absent): §11.5 measures the difference.

---

## 4. Numbers are not words (`numeric.py`, `mh_split_numbers`)

`OURS`. A numeral has no lexicon entry, no synset, no neighbours, no probability under a word bigram and no slot in a sentence frame. So no numeral reaches any word machinery: `numeric.split` replaces every number, code (`x2`, `h264`, `3d`) and version (`3.10.3`) with one space and returns them as records for their own channel, `NumberChannel` (counts by kind, decade, repeated values).

@@L_split@@

@@T_numeric@@

The C scanner `mh_split_numbers` (`@@LOC_C_SPLIT@@`) is a hand-written port of the same patterns, including the regular expression's backtracking order. It agrees with `numeric.split` on 4,000 random strings and a fixed set (§9). Number *words* ("three") are words and stay in the word machinery; whether they should also be read as numbers is `OPEN`.

---

## 5. The Harness hears (`conversation_usage.py`, `bw_drift.py`, `state_repass.py`; `monad_harness.c`)

The Harness is everything measured about the speaker and about the reply. It hears three ways.

**5.1 Usage as probability.** The speaker's own words are the probabilities the Monad writes under. A word's probability is the speaker's usage mixed into general English, with the confidence λ = N/(N+200) growing as the store grows (`vocab_store.UsageStore.p_word`), so a cold store is general English and a warm one is the speaker. Bits per word is −log₂ p, read as a compression cost: the fewer bits a word costs a reader who knows the speaker, the more probable it is.

@@L_pword@@

@@T_usage@@

**5.2 Broca–Wernicke drift.** The user's words cost w bits each; the reply's words cost b. The reply is *Broca-heavy* when b > w. The drift is the log ratio δ = ln(b/w); a correction switches on when |δ| passes 0.35 and off below 0.15 (hysteresis), and is signed so that a dearer reply pushes the next reply toward probable words. The chosen thresholds are engineering values, not measurements (`OPEN`).

@@L_drift@@

@@T_drift@@

**5.3 The speaker's state.** `prompt_to_state.PromptToState` reads a turn into fourteen poles, seven neurotransmitters × dark and light (OPI, GLU, GABA, DA, 5HT, NE, OXT), by a ridge regression on TF-IDF features and lexical meters; a reading within its own spread is healed to baseline; the pole pairs become a seven-axis mix; `neuro_recipes.conjugate` plans a reply toward RECEPTIVE, the state in which information is taken in (`neuro_recipes.RECEPTIVE`), with gain 0.6 scaled by √(fill/16), where *fill* is how many of the window's sixteen slots hold a word, so thin context makes a smaller correction. `meet_then_lead` turns the plan into one (axis, level) per word: agree with the speaker first, then lead.

@@L_observe@@

@@T_state@@

The C meter is the usage ridge only (§11.4). Its running state, healing, mix, k_eff, target and trajectory agree with the Python on eight prompts (§9).

---

## 6. The window (`sedenion_window.py`, `tone_chord.py`; `ptol.c: cv_write`)

`OURS`. The window is the scaled box-kite: a sentence is written one word at a time into sixteen slots (e₀ is the anchor, the newest word enters slot 1). The slots have a fixed labelling for the speaker's state: e₁…e₇ the dark poles in kite order OPI GLU GABA DA 5HT NE OXT, e₈ the cursor, e₉…e₁₅ the light poles; dark and light of one axis are XOR 8 apart, and the three antagonist pairs GLU|GABA, DA|5HT, NE|OXT sit XOR 1 apart (slot 1 is the OPI hub), so they are the three struts of the neurotransmitter kite (checked in `tests/test_state_repass.py`).

**Seven tones.** `Tone7` holds seven levels; `knobs()` turns them into what the constructor does: DA = novelty rank, 5HT = the exponent on word-to-word statistics, NE = pool size and short frames, OXT = boost for the speaker's own words, GLU = pool size, GABA = pruning floor, OPI (the CB1 slot) = relaxation. These are the author's design, not results.

**One word.** For an open slot, `_pick` builds candidates (the topic neighbourhood minus words already used), weights each by P(w | previous)^(coherence·(1+g)) × x, where g is the drift correction of §5.2, multiplies the speaker's own words by `user_boost` + `imitation`, prunes below a floor, truncates to the pool size and takes the word at the novelty rank. **Imitation:** a child repeats what it heard before it invents; a heard word (or its lemma) is at least as likely as the best candidate. The method is @@PICK_LINES@@ lines, so it is pointed at, not shown (`@@LOC_PICK@@`).

**The strut revisit** (the orbweaver's turbulence rule at sentence scale). When three or more candidates sit within half of the best, the slot is picked again under the antagonist tone of the strut, and the sharper pick is kept:

@@L_webstep@@

@@T_webstep@@

---

## 7. Tense and conjugation as Lyndon factors (`lyndon_conjugation.py`, `tenseplan.py`)

`OURS`, on an `ESTABLISHED` theorem (Chen–Fox–Lyndon; Duval's algorithm). English fixes the order of a verb group: TENSE (with an optional modal), have + -en, be + -ing, then the main verb. Give each feature a rank, TENSE 4 > MODAL 3 > PERF 2 > PROG 1 > V 0; a verb group is the word of its ranks in non-increasing order, and its Lyndon factorisation (`duval`) is its list of features. Realising the group is affix hopping: a PERF factor makes the next word -en, a PROG factor the next word -ing, the modal (or the first verbal word) carries the tense. With distinct ranks every factor is one letter, so the factorisation is a sort; the Lyndon view contributes the canonical form and the factor algebra (`divides`, `gcd`, `lcm`: gcd(past perfect, past progressive) = past), not a new algorithm.

@@L_conj@@

@@T_conj@@

Table 7.1 gives all fifteen tenses for *see* from the Python and from the C (`cv_inflect`), with the check:

@@TABLE_TENSES@@

`tenseplan.py` chooses the tense: a name, `auto` (the orbweaver's lemniscate station by depth: the deepest loop is the past lobe, the shallowest the future lobe) or `mirror` (the speaker's own tense).

@@L_lemn@@

---

## 8. The scaled orbweaver (`scaled_boxkite_orbweaver_monad.py`, `weave_cycle.py`; `ptol.c: cv_compose`)

`OURS`. One web step (`weave_cycle.web_step`) runs at three scales. At **word** scale the options are a word's senses and the reversal re-reads the sense in a wider context (the Python reads senses; the C reads the first synset, §11.2); at **sentence** scale the options are the candidates of a slot and the reversal is the strut revisit of §6; at **paragraph** scale the options are the radii of the web.

The plan: content words (not closed-class, at least three letters) are read through the word web; the sentence vector is the sum of their nineteen-count vectors (the earlier bench used `hash(w) % 19`, which changes from run to run); the directions are the ranked radii of that sum (`ptolemy_monad.infer_direction`: the hypernym and hyponym counts measure branching, not aboutness, so they are the fallback); the room shape is a Cassini-oval fit (`cam_encode` of the prompt and of its bridge sentence) whose ratio b/c sets how deep the web goes; turbulence (three or more radii within half of the strongest) makes the deepest loop reverse along a strut with a *but/however* pivot, then recap from the hub radius. Every sentence is written by the window; the only prose that is not picked is the closed-class connective.

@@T_orb@@

`audit()` runs seven named checks on a reply (no numerals; no template phrase; each sentence's tense is its lemniscate station; each carries its tense marker; every word is known or heard; a pivot only when turbulent; stations are past, present or future).

---

## 9. The C port and the parity tests (`PtolC/ptol.c`, `PtolC/monad_harness.c`)

The Monad is the voice (`ptol.c`, @@VOICE_LINES@@ lines: window, `Tone7`, imitation, strut revisit, Lyndon verb group, tense plan, scaled orbweaver, `cam_encode`); the Harness is the ears (`monad_harness.c`, @@EARS_LINES@@ lines: numbers, usage, drift, the user's state). The console talks to them as plain text over a socket-pair of newline-JSON frames: `say` and `cmd` frames are answered by the child (`/legacy <text>` still reaches the earlier voice). The same text can be typed at `ptol -chat`.

![**Figure 1.** The Monad: one turn through `ptol.c` (ISO 5807 symbols; every title is a name in the code, checked by `tests/test_flowcharts.py`).](figures/monad_flow.png)

![**Figure 2.** The Harness: hearing a turn in `monad_harness.c`.](figures/harness_flow.png)

The Python monad is the test bench: `tests/test_c_parity.py` builds the C and compares. It checks, to the stated tolerance: numbers (4,000 random strings and a fixed set, exact); the drift (300 steps, 1e-6); the usage meter (14 poles, 2e-5); the running solution and the repass (mix 6e-4, target 0.011, healed, held, heard tone, five-step trajectory); usage counts and p_word (1e-9); verb groups (15 tenses × 460 verbs × number × person: surface, tense code, conjugation code, ranks, factor count, exact); the tense plan and the mirror tense (exact); `cam_encode` (1e-9); the bigram (1e-12); the orbweaver plan on first senses (reach, regime, b/c, turbulence, peaks, radii); and the resident frame link with a scripted console. A test that fails is a finding: it found a number-scanner backtracking error, a one-character truncation before counting, and a `tolower(*p++)` macro that skipped letters.

@@TABLE_SUITE@@

---

## 10. Measurements (transcripts)

All runs on one laptop (Intel Core i7-8550U, 2018, no GPU, no network). Timings are in ⟦brackets⟧ and are ignored by `make_paper.py --check`; everything else is compared exactly.

**10.1 The C monad, plain text** (`ptol -chat`, a fresh private usage store):

@@T_cchat@@

**10.2 The Python monad, the same pipeline** (`responder.Responder`, the real user-state engine):

@@T_pyconv@@

**10.3 Cost.** One C turn averages ⟦@@C_MS@@⟧ ms (40 turns in one resident session, state kept, process start included). The compiled voice is @@VOICE_LINES@@ lines and the harness ears @@EARS_LINES@@; the Python twins total @@PY_LINES@@ lines.

---

## 11. Failure modes and limits

Stated as results, each measured by the run above or by `evidence.py`.

**11.1 The replies are not good English.** Transcripts 10.1 and 10.2 are the evidence: sentences are well formed at the slot level (determiner, noun, inflected verb group, determiner, noun) and often wrong in meaning ("the stone mixes the sculptor"). Heard words are repeated whether or not they fit the slot's part of speech, because imitation weights them above the best candidate. A pivot at the deepest loop can repeat the same sentence.

**11.2 No sense choice in C.** The Python word web picks a sense by gloss overlap and the speaker's own history; the C reads the first synset. For the words below the two differ:

@@TABLE_SENSES@@

**11.3 Connectives are not Python's.** The Python picks connectives with a seeded `random`; the C rotates through the lexicon in a fixed order, so the same prompt gives the same plan but different connective words.

**11.4 The C user-state meter is one meter.** The Python state engine averages the usage ridge with lexical meters (VADER, arousal, profanity, dialogue act, stance, continuation cues); the C has the ridge only. The gap in dose units, over eight prompts:

@@TABLE_METER@@

**11.5 The lossy store.** `monad3_c.bin` maps a word to one entry, not to its senses. Before `voice_lex.bin`, four of five test prompts had a different sentence vector in C than in Python; with it, the orbweaver plans agree.

**11.6 Not built.** Negation, questions and do-support; noun irregulars (children, mice) in the C lemma rules; number agreement other than singular; the GenerationalLineage descent for a numeric web scale (the C uses round(scale)); non-ASCII text in the C tokenisers (bytes ≥ 0x80 count as letters). The number pattern consumes a trailing comma (`$1,200,` in the transcript of §4), in Python and in C alike; the value is unaffected.

**11.7 Choices that are not measurements.** The 1/9 clamp gain, the √(fill/16) law, the drift thresholds 0.35 and 0.15, the tone knob table, the imitation weight and the slot labelling of the user's state are engineering choices (`OPEN`).

---

## 12. Conclusion

The Monad and the Harness run on one laptop CPU with no gradient descent in the Monad, a lexicon that is WordNet's, and a speaker model that is a single ridge regression; every mechanism is a short listing, a named function or a transcript, and the C is checked against the Python it was ported from. What is missing is the English: the machinery picks every word and every tense, and the words are not yet the right ones. The next measurable step is part-of-speech-aware imitation, then sense choice in C.

---

## References

*ESTABLISHED, fetched and kept in `paper/references/`:* de Marrais, R. (2000), *The 42 Assessors and the Box-Kites They Fly*, arXiv:math/0011260; Moreno, G. (1998), *The zero divisors of the Cayley–Dickson algebras over the real numbers*, arXiv:q-alg/9710013; Corless et al. (1996), *On the Lambert W function*; Wankel, F. (1961), US 2,988,065; Vahdat et al. (2025), Google AI inference energy; Altman, S. (2025), *The Gentle Singularity*; You, J. (2025), Epoch AI, ChatGPT energy.

*ESTABLISHED, cited and not fetched (unverified until fetched):* Miller, G. (1995), *WordNet: a lexical database for English*, CACM 38(11); Fellbaum, C. (ed.) (1998), *WordNet: An Electronic Lexical Database*; Chen, K.-T., Fox, R. H., Lyndon, R. C. (1958), *Free differential calculus IV*; Duval, J.-P. (1983), *Factorizing words over an ordered alphabet*, J. Algorithms 4; ISO 5807:1985 (flowchart symbols; ANSI lineage; see https://www.wikipedia.org/wiki/ECMA-4 and https://creately.com/guides/flowchart-symbols/).

---

## Appendix. ContextPlease: what it is, what was used, and where the history is

**What ContextPlease is.** `ContextPlease` (`https://github.com/michaelrendier/ContextPlease`) is the author's persistent context for any model that works on his repositories: the `.clauderc*` files (constants, canonical maths, history by engine, citations, licences), the skills, the primers per project, the references each skill was built from, and a scratchpad of working scripts and measurements. A model that reads it can come up to speed on the projects with historical access, without the author repeating himself.

**Used for this paper.**

| file / skill | used for |
|---|---|
| `ContextPlease/claude/skills/cs-paper-code-conventions/` | how code is shown (conventions A–G; §10, the CS engineering white paper) |
| `ContextPlease/claude/clauderc/.clauderc_canonical_maths` | symbol definitions (α, A_π, Ω_ζΣ) |
| `ContextPlease/claude/hist_prime/VAPMIP/` | the primers of earlier work on the Monad |
| `ContextPlease/claude/references/INDEX.md` | the ledger of fetched literature |
| `ContextPlease/claude/scratchpad/gl_header_options/`, `2026-11-20_*` | working scripts (header options; inventories) |

**Where the history is** (pointers only; none of it is the subject of this paper):

| what | where |
|---|---|
| the previous version of this paper (34 pages, 19 sections: the compiled `ptol` and `scaled_mind_eye_boxkite_kernel_monad.py`) | `VAPMIP` commit `9a16a44`, `paper/Forward_Propagation_of_Information.md`; the PDF in the same commit |
| the engineering chronology, phase by phase (1–43 before this rewrite; 44–@@TTE_LAST@@ since) | `VAPMIP/docs/wiki/Tuning-the-Engine/` (never edited; new phases are new pages) |
| earlier voices (`rotary_rerun`, `19D_*`, `ptolemy_monad`, `scaled_mind_eye_boxkite_kernel_monad`) | the VAPMIP root and `Currentwork/Broca/`, `Currentwork/Wernicke/` (copies; the root files are the originals) |
| the notebooks of the earlier paper | `VAPMIP/notebooks/paper/`, `VAPMIP/notebooks/c/` |
| the flow charts and their generator | `VAPMIP/docs/flowcharts/` |
