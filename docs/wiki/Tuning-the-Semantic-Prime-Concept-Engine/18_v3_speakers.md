# 18 — The v3 speakers

**Job.** Say what `TestMonad_english_v3.py` and `TestMonad_chinese_v3.py` do, how they differ from the engine step they copy, and what their replies show.

**Files.** `Currentwork/SemPriCon/clean/TestMonad_english_v3.py`, `Currentwork/SemPriCon/clean/TestMonad_chinese_v3.py`; each reads its own `clean/test_{L}_v3.bin` (read-only). Run from `Currentwork/SemPriCon/`: `.venv/bin/python clean/TestMonad_{L}_v3.py [--bin P] [--exact-zeros] [prompt…]`. The English speaker also takes `--wordnet [--order given|english|chain|all]`. They import the mapping machinery from `mappings/{UNS,Flat}/` and `monad_pyu` from `tools/`. Both are copies of the engine step `monad_py.Monad.speak` (the Python port of `monad.c` at `eb28ce8`); each deviation is tagged `# TESTMONAD-<tag>` in the code. The port itself is never changed.

| tag | where | what | why |
|---|---|---|---|
| F1 | both | `J_floor = J_max·0.01` (engine: `max(J_max·0.01, GAP)`) | in every v3 bin `J_max` (1e-5…6e-4) is below `GAP` 7.07e-4, so nothing could pass; all three bins spoke '' with `tools/v3_speak.py` |
| F2 | both | trace `funnel`: vocabulary → J above floor → phase gate → accepted | shows where candidates die |
| F3 | both | the separator set is the eight Fermat spaces (U+2003–2009, U+200B) | the earlier range was empty, so separators were never recognised |
| S1 | both | spread radius and decay scaled by mean vocabulary spacing g = N/\|vocab\| | the engine's ±3 slots assumed a 25 000-word store; v3 holds 732 or 996 words |
| S2 | both | `say()`: English with spaces, capital, full stop; Chinese with 。 | the reply as a sentence |
| C1–C3 | chinese | Han-only labels; the character is the surface; no separators | spelling rules mean nothing for a character |
| W1 | english | `--wordnet`: the chosen words go through `EnglishSpeaking/english_speaking_wordnet.py` (senses chosen jointly; three word orders) | the original WordNet method as the last layer |

**What the replies show** (2026-10-22, engine zeros): 'what is your name' → "Bond free zone rake."; 'water fire' → "Sheaf browse subject allege."; Chinese 水 火 → "炟氣炬汧灣求沆炭污。". Chinese neighbours are structural (the water and fire radicals), as M4 predicts; English neighbours are spelling neighbours (the slot is a function of spelling), so they are not related in meaning. The v3 bins have no A edges: selection is ring proximity only, not association.

**Not built.** `TestMonad_chinese_english_v3.py` (the assignment speaker, the translator indicator) and `TestMonad_english_chinese_v3.py` (needs `test_english_chinese_v3.bin`). Candidates: a sentence-length stop rule; edges so selection can use association; how a Chinese reply should be ordered.
