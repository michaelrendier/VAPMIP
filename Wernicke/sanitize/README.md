# Wernicke/sanitize — token-level sanitiser for the granular bins

`sanitize_v0.py`: deterministic, no training.  `ENV` is a dict of named tables (CLASS, ADMIT, TIER, CHROME) used like a Bash environment: a loop looks up a keyword and runs the value; to change a rule, override one key.
Run: `VAPMIP/.venv/bin/python sanitize_v0.py` (reads `$PTORRENT_BINS/clean/monad_{mathematics,physics}.bin`, writes `report_v0.json` and `*.tiers.json`).

Tiers: **A** lemma in WordNet (relation evidence only) · **B** candidate new entry (`compound_of_known_parts` is the strong kind; `candidate_evidence_pending` needs prose evidence from ordered text that a bag-of-words bin cannot give) · **C** proper noun (HOOK table, never vocabulary) · **F** function word · **Q** quarantine with a reason code (garbage, ref, formula, number, greek, chrome, time_expression, single_letter, no_vowel [units and abbreviations], consonant_run, non_latin_or_symbol).
Nothing is deleted.  Sentence-level steps (page-chrome removal, prose test, definitional frames, formula spans) need re-fetched ordered text and are not built.
