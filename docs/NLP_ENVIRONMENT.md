# The NLP environment (set up 2026-10-17)

What the machine has for content extraction and scaling, where it lives, and how to check it. Verified by
`tools/verify_nlp_environment.py` (run it under every interpreter; each line says PASS, MISS or FAIL).

## Who gets what

| interpreter | what it has | result of the check |
|---|---|---|
| system `python3` (3.12, `~/.local` user site) | **everything**: nltk 3.10.3, spaCy 3.8.16 with en_core_web sm, md, lg, Stanza 1.15 (with torch), gensim, textblob, pywsd, lemminflect, inflect, conllu, `wn`, rapidfuzz, pandas 3.0.6, scikit-learn, numpy 2.4.6 | 44 PASS, 0 MISS, 0 FAIL |
| `VAPMIP/.venv` | **only what VAPMIP's function needs**: nltk, spaCy with sm and md, lemminflect (the conjugation `repass()`), inflect, conllu, `wn`, rapidfuzz, pandas, scikit-learn, networkx, requests. Not Stanza or torch (about 5 GB), gensim, textblob, pywsd, or the large model. Additive list: `requirements-nlp.txt`; `requirements.txt` is unchanged. | 36 PASS, 8 MISS, 0 FAIL (the deliberate omissions: Stanza, gensim, textblob, pywsd, transformers, frame-semantic-transformer, fastcoref, the large spaCy model) |
| `ValaQuenta/.venv` | **everything every repository gets**: it already held the union of the other venvs; added PyQt5, PyAudio, colorama and the spaCy models so it is a superset of VAPMIP's | 36 PASS, 8 MISS, 0 FAIL (the same omissions) |

The VAPMIP venv already existed (2026-08-15, for the same numpy reason described in `env.sh`); it was extended, not rebuilt.
The system python's old import crash (`numpy.dtype size changed`) was apt's pandas and numexpr built for numpy 1.x shadowed by a
numpy 2 in `~/.local`; fixed by installing current pandas, numexpr and bottleneck in the user site.

## Where the data lives (none of it is in git)

| path | what | size |
|---|---|---|
| `~/nltk_data/` | the NLTK data collection `all`, 122 packages: WordNet 3.0, 3.1, 2021, 2022 and Open English WordNet, OMW, **VerbNet** (2.1 and 3.x), PropBank, NomBank, FrameNet 1.5 and 1.7, SemCor, wordnet_ic, SentiWordNet, CMU dict, punkt_tab, the POS taggers, the NE chunker, conll2000/2002/2007, treebank, dependency_treebank, nps_chat (dialogue acts), brown, and more | 3.5 GB |
| `~/nlp_data/` | Princeton's own distributions and companions, extracted next to their archives: WordNet 3.1 and 3.0 sources, **SQL** and **Prolog** forms, sense mappings, **SemCor 1.6**, the **gloss-tagged corpus**, Core WordNet, **morphosemantic links**, logical-form glosses, SUMO mappings; VerbNet 3.4, SemLink and PropBank frames from GitHub; the spaCy model wheels. `MANIFEST.md` there lists URL, size and sha256 of every file | 1.7 GB |
| `~/.wn_data/` | the `wn` library: Open English WordNet 2025 and 2024, OMW English (Princeton 3.0 and 3.1 forms), and the Open Multilingual WordNet (all languages, `omw:1.4`) | 1.1 GB |
| `~/nlp_data/` (second batch, same directory) | **ConceptNet 5.7** assertions (kept as `.gz`, stream with `zcat`), **Numberbatch 19.08** (English and multilingual, `.gz`), the English **Wiktionary** dump (raw, `.bz2`) and the structured English extract (Wiktextract/kaikki JSONL, 3.3 GB), **eXtended WordNet 2.0-1.1** (parsed, sense-tagged glosses; WordNet 2.0 senses), **UD English-EWT and GUM**, the **Georgetown GUM** multilayer corpus (dependencies, constituents, coreference, RST), **LitBank**, **UniMorph English**, **MorphoLex-en**, and **DISRPT 2019, 2021, 2023** (discourse segmentation and connectives) | see the total below |
| `~/.cache/stanza/` | Stanza English models: tokenize, mwt, pos, lemma, depparse, ner, constituency, coref, sentiment | 0.7 GB |
| `/usr/share/wordnet` | WordNet 3.0 for the native C library (apt `wordnet`, `wordnet-dev`) | small |

The ledger entries are in `ContextPlease/claude/references/INDEX.md` and `~/.clauderc_citations`; the manifest is mirrored in
`docs/references/VAPMIPNLPData/`. Licences differ (WordNet, VerbNet, SemLink, PropBank, SUMO, spaCy models): read each before
vendoring any of it. Total on disk for all language data: about **17.7 GiB** (`~/nlp_data` 13 GB, `~/nltk_data` 3.5 GB, `~/.wn_data` 1.1 GB, Stanza 0.7 GB); 132 GB were free on `/home` afterwards. Everything is on disk and read back by `tools/verify_nlp_data.py` (27 of 27 PASS), but **no orbweaver code reads any of it yet**.

## C

NLTK has no C API. Two routes, both built and run (`tools/c_nlp/`, `make run`):

* `wn_c_test.c`: the native WordNet 3.0 C library (`libwordnet`, header `wn.h`): senses, hypernym chain, gloss of "tree".
* `nltk_embed_test.c`: C embedding CPython, which then uses the whole of NLTK (WordNet, **VerbNet**, the POS tagger): it printed 52
  synsets of "play", its VerbNet classes `meet-36.3-1` and `performance-26.7-1-1`, and the tags of "can you play the piano".

VerbNet XML (`~/nlp_data/verbnet-official/.../verbnet3.4`) can also be read from C with libxml2 (`libxml2-dev` is installed).

## Software added to the system python only (existing open-source tools)

`transformers` 5.20, `sentencepiece`, `frame-semantic-transformer` 1.1 (FrameNet parser on T5; its model downloads on first use), `fastcoref` 2.1 (coreference; model on first use), Stanza 1.15 with the English models above, plus the earlier spaCy (sm, md, lg), lemminflect, inflect, conllu, `wn`, gensim, textblob, pywsd. Not in `VAPMIP/.venv` (its rule: only what it needs); `ValaQuenta/.venv` is not given the heavy torch-based ones either, because no repository uses them yet.

## Open replacements for the licensed corpora (found on GitHub)

| licensed (not downloaded) | what stands in | note |
|---|---|---|
| Penn Discourse Treebank 3.0, RST-DT | GUM (RST, coreference, entities, dependencies) and DISRPT 2019 to 2023 (the PDTB parts there are stubs) | GUM restores some texts with `get_text.py`; licences are per genre, some non-commercial |
| CELEX | UniMorph English, MorphoLex-en, plus lemminflect | |
| OntoNotes | LitBank (entities, coreference, events in 100 works of fiction), UD English-EWT | |
| Penn Treebank | NLTK's 5% sample, UD English-EWT | |
| BabelNet | skipped on purpose (Cody) | not a free download |

Unauthorised copies of the licensed corpora were not looked for.

## Notes

* eXtended WordNet is built on WordNet **2.0** senses; using its sense tags with the 3.0 databases needs a sense mapping first.
* `pip`, `apt` and Stanza's downloader carry their own user agents; every request made by hand (`curl`, the NLTK and `wn` downloaders, GitHub archive URLs) carried a Mozilla one.
* I first installed Stanza and torch into the VAPMIP venv by mistake (6.3 GB) and removed them again; it is about 1 GB.
* `tools/nlp_data_manifest.py --mirror` regenerates `~/nlp_data/MANIFEST.md` (33 files, 10.1 GB of archives, sha256 for each).
