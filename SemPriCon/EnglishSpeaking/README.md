# EnglishSpeaking — live toolset

Layers that attach to any English-speaking TestMonad as the last step before speaking. Workbench code (see ../README.md): this folder is the current state, not an archive.

| file | what |
|---|---|
| `english_speaking_wordnet.py` | `EnglishWordNetLayer`: joint WordNet sense choice for a list of English words in any order, the WordNet edges between them, and three orderings (given / english / chain) framed as a sentence. Original WordNet method (NLTK), not the boxkite |

Run with `../../PtolemyDesktop/.venv/bin/python` (has nltk; system python3 crashes on `import nltk`). Attach: `TestMonad_english_v3.py --wordnet [--order given|english|chain|all]`.
Intent (Cody, 2026-10-22): in the pair speakers the slots are chosen by the Chinese mechanism and the words come from the assigned English side; the WordNet layer works on the English side of any assignment, so the same reply can be compared in Chinese-walk order and in English order, and against the same bin with English word selection.
