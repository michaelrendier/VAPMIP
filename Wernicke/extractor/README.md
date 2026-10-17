# The content extractor (v0): deterministic, a straight ruleset

Prompt in, the literal words out, each assigned to one of the seven data points (`SHELL ANCHOR SPAN{relation,claim,frame} SCAFFOLD ELABORATE HOOK WRAP`).
No training, no model, no orbweaver web: a regex tokenizer, hardcoded closed-class tables, WordNet 3.0 through NLTK (`morphy`, synset lists, sense counts),
and ordered disambiguation rules. The same input always gives the same output.  `python3 extract_v0.py "can you play the piano?"`
(use `VAPMIP/.venv/bin/python`; the first call builds a lemma index for the typo suggestions, about 3 seconds).

What it records, beyond the words: each word's lemma and POS (with the alternatives kept when ambiguous); pronouns with person, number and case
(not resolved: that is the final repass); the verb group as features (tense, aspect, voice, modal, person, number); `SHELL` act, polarity, the wh-gap, interjections;
capital-letter emphasis (kept for the tone channel); typo candidates for words WordNet does not know; zero-width characters stripped and counted; and, per content word,
how specific the vocabulary is (WordNet depth, sense count, hyponym count) with the share of technical or unknown words: the granularity indicator for now.

Files: `extract_v0.py` (the extractor), `silk_map.py` (the seven roles as data), `crosswalk_tests.py` (tests against UD, PropBank, WordNet, VerbNet), `compare_answers.py`
(agreement with the 40 reference answers), `view.py` (readable output). `CROSSWALK.md` / `CROSSWALK_REPORT.md` hold the earlier role-map tests.

## Tested on Cody's own prompts (2026-10-17)
32 prompts from this session, 3 to 251 words each (1,489 tokens), run locally; the prompts themselves are not committed (`.gitignore`). Every token lands in a data point (100%; that
says nothing about correctness). It takes 11 s for all 32 including the one-off index. Against the 40 model-provided reference answers (Claude's, unreviewed): SHELL act
37/40, polarity 38/40; per slot, shared words: ANCHOR 60% precision / 62% recall, relation 50/51, SCAFFOLD 71/62, ELABORATE 79/73, HOOK 75/55, WRAP 88/70, frame 33/65,
claim 87/24 (the reference claims hold embedded-clause words that v0 puts in a clause of their own, so claim recall is understated).

## Known failures (to be fixed, not to disqualify the method)
* No clause recursion: an embedded clause is a separate clause with no link to its parent slot.
* Time noun phrases ("last session") land as claim, not frame; "first" after a noun ("the content first") is not an adverb here.
* Noun-noun compounds with no determiner can read as verb plus noun when the noun reading is rarer; the rules cover common cases only.
* A conjoined noun phrase is not grouped ("seam edge and anchor displacement").
* Typo suggestions are candidates, never corrections: they also fire on real coinages (wiki -> wifi, hardcode -> hardcore, repass -> repast).
* Title phrases with a lowercase article inside ("Tuning the Engine") are only partly marked as names.
