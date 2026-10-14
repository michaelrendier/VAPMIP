

* **DECISION (Cody, 2026-10-13): stay with NLTK for content processing**, because the scalar boxkite already uses it. This supersedes the spaCy recommendation in section 14. NLTK pieces to use: WordNet (installed), `lesk` (weak, baseline only), `pos_tag` + `RegexpParser` chunking (tagger data MISSING from the venv), `wordnet_ic` similarity measures, TextTiling. One-time data downloads needed: averaged_perceptron_tagger_eng, punkt_tab, stopwords (not yet fetched).
