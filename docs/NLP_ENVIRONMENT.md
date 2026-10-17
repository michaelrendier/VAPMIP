# The NLP environment (set up 2026-10-17)

What the machine has for content extraction and scaling, where it lives, and how to check it. Verified by
`tools/verify_nlp_environment.py` (run it under every interpreter; each line says PASS, MISS or FAIL).

## Who gets what

| interpreter | what it has | result of the check |
|---|---|---|
| system `python3` (3.12, `~/.local` user site) | **everything**: nltk 3.10.3, spaCy 3.8.16 with en_core_web sm, md, lg, Stanza 1.15 (with torch), gensim, textblob, pywsd, lemminflect, inflect, conllu, `wn`, rapidfuzz, pandas 3.0.6, scikit-learn, numpy 2.4.6 | 41 PASS, 0 MISS, 0 FAIL |
| `VAPMIP/.venv` | **only what VAPMIP's function needs**: nltk, spaCy with sm and md, lemminflect (the conjugation `repass()`), inflect, conllu, `wn`, rapidfuzz, pandas, scikit-learn, networkx, requests. Not Stanza or torch (about 5 GB), gensim, textblob, pywsd, or the large model. Additive list: `requirements-nlp.txt`; `requirements.txt` is unchanged. | 36 PASS, 5 MISS (the five deliberate omissions), 0 FAIL |
| `ValaQuenta/.venv` | **everything every repository gets**: it already held the union of the other venvs; added PyQt5, PyAudio, colorama and the spaCy models so it is a superset of VAPMIP's | 36 PASS, 5 MISS (the same five), 0 FAIL |

The VAPMIP venv already existed (2026-08-15, for the same numpy reason described in `env.sh`); it was extended, not rebuilt.
The system python's old import crash (`numpy.dtype size changed`) was apt's pandas and numexpr built for numpy 1.x shadowed by a
numpy 2 in `~/.local`; fixed by installing current pandas, numexpr and bottleneck in the user site.

## Where the data lives (none of it is in git)

| path | what | size |
|---|---|---|
| `~/nltk_data/` | the NLTK data collection `all`, 122 packages: WordNet 3.0, 3.1, 2021, 2022 and Open English WordNet, OMW, **VerbNet** (2.1 and 3.x), PropBank, NomBank, FrameNet 1.5 and 1.7, SemCor, wordnet_ic, SentiWordNet, CMU dict, punkt_tab, the POS taggers, the NE chunker, conll2000/2002/2007, treebank, dependency_treebank, nps_chat (dialogue acts), brown, and more | 3.5 GB |
| `~/nlp_data/` | Princeton's own distributions and companions, extracted next to their archives: WordNet 3.1 and 3.0 sources, **SQL** and **Prolog** forms, sense mappings, **SemCor 1.6**, the **gloss-tagged corpus**, Core WordNet, **morphosemantic links**, logical-form glosses, SUMO mappings; VerbNet 3.4, SemLink and PropBank frames from GitHub; the spaCy model wheels. `MANIFEST.md` there lists URL, size and sha256 of every file | 1.7 GB |
| `~/.wn_data/` | the `wn` library: Open English WordNet 2025 and 2024, OMW English (Princeton 3.0 and 3.1 forms) | 466 MB |
| `/usr/share/wordnet` | WordNet 3.0 for the native C library (apt `wordnet`, `wordnet-dev`) | small |

The ledger entries are in `ContextPlease/claude/references/INDEX.md` and `~/.clauderc_citations`; the manifest is mirrored in
`docs/references/VAPMIPNLPData/`. Licences differ (WordNet, VerbNet, SemLink, PropBank, SUMO, spaCy models): read each before
vendoring any of it. The extracted Princeton and VerbNet files are on disk but **no code reads them yet**.

## C

NLTK has no C API. Two routes, both built and run (`tools/c_nlp/`, `make run`):

* `wn_c_test.c`: the native WordNet 3.0 C library (`libwordnet`, header `wn.h`): senses, hypernym chain, gloss of "tree".
* `nltk_embed_test.c`: C embedding CPython, which then uses the whole of NLTK (WordNet, **VerbNet**, the POS tagger): it printed 52
  synsets of "play", its VerbNet classes `meet-36.3-1` and `performance-26.7-1-1`, and the tags of "can you play the piano".

VerbNet XML (`~/nlp_data/verbnet-official/.../verbnet3.4`) can also be read from C with libxml2 (`libxml2-dev` is installed).

## What was not fetched (on purpose or blocked)

eXtended WordNet, ConceptNet and BabelNet (large or keyed), the Penn Discourse Treebank and RST-DT and CELEX (licensed), FrameNet from
its own site (the NLTK 1.5 and 1.7 copies are present). `pip` and `apt` traffic goes through those tools and carries their own user
agent; every request I made by hand (`curl`, the NLTK and `wn` downloaders) carried a Mozilla one. I first installed Stanza and torch
into the VAPMIP venv by mistake (6.3 GB) and removed them again; it is now about 1 GB.
