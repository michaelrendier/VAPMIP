# ~/nlp_data: what was acquired, from where, and when

Acquired 2026-10-17 (2026-10-17 session). Every request carried a Mozilla user agent; public works only. Archives are kept; extracted copies sit in sibling directories.
Also on this machine, not in this directory: the NLTK data collection `all` (122 packages, 3.5 GB) in `~/nltk_data` (from the NLTK data index), and the `wn` library's Open English WordNet 2025 and 2024 and the OMW English WordNets (Princeton 3.0 and 3.1 forms) in `~/.wn_data` (466 MB).

| file | source URL | what | licence note | bytes | sha256 (first 16) |
|---|---|---|---|---|---|
| princeton/wn3.1.dict.tar.gz | https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz | WordNet 3.1 database files (Princeton) | Princeton WordNet licence | 16,358,468 | 3f7d8be8ef6ecc71 |
| princeton/WordNet-3.0.tar.bz2 | https://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.bz2 | WordNet 3.0 source and database (Princeton) | Princeton WordNet licence | 9,060,524 | 6c492d0c7b4a40e7 |
| princeton/WNprolog-3.0.tar.bz2 | https://wordnetcode.princeton.edu/3.0/WNprolog-3.0.tar.bz2 | WordNet 3.0 Prolog database (Princeton) | Princeton WordNet licence | 7,687,051 | c0427cc55ae8e136 |
| princeton/WNsnsmap-3.0.tar.bz2 | https://wordnetcode.princeton.edu/3.0/WNsnsmap-3.0.tar.bz2 | WordNet 3.0 sense mappings (Princeton) | Princeton WordNet licence | 2,343,834 | 439200fef47d17aa |
| princeton/wn_for_sql.tar.gz | https://wordnetcode.princeton.edu/wn_for_sql.tar.gz | WordNet in SQL form (Princeton) | Princeton WordNet licence | 10,493,960 | ccdc7e63ad8da6d8 |
| princeton/WordNet-3.0-glosstag.tar.bz2 | https://wordnetcode.princeton.edu/glosstag-files/WordNet-3.0-glosstag.tar.bz2 | Princeton Annotated Gloss Corpus (gloss-tagged WordNet 3.0) | Princeton WordNet licence | 57,291,600 | c7b8318ac873ecbe |
| princeton/Readme.txt | https://wordnetcode.princeton.edu/glosstag-files/Readme.txt | glosstag readme | Princeton | 26,243 | d2474bd4527b8de4 |
| princeton/core-wordnet.txt | https://wordnetcode.princeton.edu/standoff-files/core-wordnet.txt | Core WordNet list (Princeton standoff file) | Princeton WordNet licence | 255,511 | bddc8163a6091cb5 |
| princeton/morphosemantic-links.xls | https://wordnetcode.princeton.edu/standoff-files/morphosemantic-links.xls | Morphosemantic links (Princeton standoff file) | Princeton WordNet licence | 3,415,040 | 6fd954785e04295c |
| princeton/morphosemantic-links.zip | https://wordnetcode.princeton.edu/morpholinks/morphosemantic-links.zip | Morphosemantic links (Princeton) | Princeton WordNet licence | 1,038,382 | 7fd4553abf3f85db |
| princeton/LFglosses.standoff-files.zip | https://wordnetcode.princeton.edu/morpholinks/LFglosses.standoff-files.zip | Logical-form glosses standoff files (Princeton) | Princeton WordNet licence | 9,224,960 | a02b78f808533b61 |
| princeton/README.txt | https://wordnetcode.princeton.edu/morpholinks/README.txt | morpholinks readme | Princeton | 1,978 | bb62041b4de3cf1e |
| princeton/SUMO-WordNet.zip | https://wordnetcode.princeton.edu/sumo/SUMO-WordNet.zip | SUMO to WordNet mappings (hosted by Princeton) | check the SUMO licence before redistributing | 6,691,455 | c9427ec55a4d5c83 |
| princeton/semcor16.tar.gz | https://wordnetcode.princeton.edu/semcor16.tar.gz | SemCor 1.6 (sense-tagged Brown corpus, WordNet 1.6 senses) | Princeton WordNet licence | 5,597,085 | d1f812c903d2a2c2 |
| verbnet/verbnet-cu-clear.zip | https://github.com/cu-clear/verbnet/archive/refs/heads/master.zip | VerbNet (CU Boulder CLEAR, GitHub master; contains verbnet3.4) | check the VerbNet licence before redistributing | 1,529,554 | 2c7c32785aa13238 |
| verbnet/semlink-cu-clear.zip | https://github.com/cu-clear/semlink/archive/refs/heads/master.zip | SemLink (VerbNet, PropBank, FrameNet, WordNet mappings) | check the SemLink licence before redistributing | 4,787,903 | 75f8781ade525b5c |
| verbnet/propbank-frames.zip | https://github.com/propbank/propbank-frames/archive/refs/heads/main.zip | PropBank frames | check the PropBank licence before redistributing | 9,498,383 | 2e7849611653bed5 |
| spacy_models/en_core_web_sm-3.8.0-py3-none-any.whl | https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl | spaCy en_core_web_sm 3.8.0 | MIT (spaCy models; trained on OntoNotes/WordNet-derived data, see the model card) | 12,806,118 | 1932429db727d4bf |
| spacy_models/en_core_web_md-3.8.0-py3-none-any.whl | https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl | spaCy en_core_web_md 3.8.0 | as above | 33,480,380 | 5e6329fe3fecedb1 |
| spacy_models/en_core_web_lg-3.8.0-py3-none-any.whl | https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl | spaCy en_core_web_lg 3.8.0 | as above | 400,658,291 | 293e9547a655b254 |

Licence notes are reminders, not legal findings: read each licence before vendoring any of this into a repository. None of it is in git.
Verified by content, not by name: the archives were listed or opened (WordNet 3.1 `dict/` files, the glosstag `WordNet-3.0/glosstag/` tree, the Core WordNet list, the Composite Document of the morphosemantic links, VerbNet `verbnet3.4`).
