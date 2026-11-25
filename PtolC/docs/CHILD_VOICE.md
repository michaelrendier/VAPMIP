# The child's voice in C (ptol.c + monad_harness.c)

*2026-11-25. The Monad is built and tested in Python first; the C is the port. Python is the test bench: `tests/test_c_parity.py`.*

"This is a child we have to teach how to speak English." Talk to it as plain text.

```
make ptol                                   # in PtolC/
./ptol -chat                                # terminal chat, one resident session, state kept between lines (blank line quits)
./ptol -turn "The king rules the kingdom."  # one turn from the shell
./ptol -w                                   # the Python console on the frame link: say/cmd frames are answered by the child; /legacy <text> = the old word-shadow voice
```

Commands (plain text, `/` first): `/help` `/state` (the 14 poles read into the 7-axis mix, held or cancelled) `/drift` (usage, Broca–Wernicke, numbers) `/plan` (the last web: reach, regime, radii, pieces)
`/trace` (the last sentence word by word, with each pick's probability and tone) `/audit` (seven checks) `/tense <name|auto|mirror>` (`past perfect`, `future progressive`, ...).

## Who does what
| file | role | ported from |
|---|---|---|
| `monad_harness.c/.h` | the **harness hears**: numbers leave first; the usage store (λ = N/(N+200)); the reply is priced and moves the Broca–Wernicke drift; the user's 14 poles from a TF-IDF ridge, the running solution, heal / mix / cancel / meet-then-lead | `numeric.py`, `bw_drift.py`, `conversation_usage.py`, `state_repass.py`, `prompt_to_state.py` (usage meter) |
| `ptol.c` (section *THE CHILD'S VOICE*) | the **monad speaks**: 16-slot window, Tone7 knobs, imitation, strut revisit, Lyndon verb group, tense plan, scaled orbweaver, `cam_encode` | `sedenion_window.py`, `tone_chord.py`, `lyndon_conjugation.py`, `tenseplan.py`, `weave_cycle.py`, `scaled_boxkite_orbweaver_monad.py`, `monad.cam_encode` |

## Data (generated, gitignored like the other `.bin`; `tools/export_c_monad_data.py` then `tools/splice_c_data.py`)
`user_state.bin` (the usage ridge: 45,448 TF-IDF 1–2-gram features × 14 poles, calibration gain/base, spread), `voice_lex.bin` (77,477 WordNet words: parts of speech and the first synset's 19 relation counts),
`monad3_c.bin` (existing: the co-occurrence matrix, used for neighbours). The irregular-verb table and the `cam_encode` word sets are generated *into* the two C files between `BEGIN/END GENERATED` markers.
Where the files are looked for: next to the binary; `PTOLC_DIR` overrides. State: `PTOL_USAGE_DIR` (default `~/.ptolemy/usage_c`; `usage_c.txt`, `numbers_c.txt`).

## Exact against Python (tested)
numbers (4,000 random strings + fixed), the drift (300 steps), the usage meter (14 poles), the solution and repass (mix, target, healed, held, k_eff, heard tone, 5-step trajectory), usage counts and p_word,
verb groups (15 tenses × 460 verbs × number × person: surface, tense code, conjugation code, ranks, factor count), the tense plan, the mirror tense, `cam_encode` (1e-9), the bigram (1e-12),
the orbweaver plan on first senses (reach, regime, b/c, turbulence, peaks, radii). The resident frame link is tested with a scripted console.

## Different from Python (not hidden)
- **No lexical meters.** The C user-state meter is the usage ridge only (VADER, arousal, profanity, dialogue act, stance and the continuation cues are not ported); `spread` is the median per-pole disagreement of the two Python meters, exported. The meter reads the raw text (no aspect mask).
- **No senses.** Python's word web picks a sense by gloss overlap and the user's history; C reads the first synset. Neighbours of a seed word come from the co-occurrence matrix (top 12 of the right part of speech, lemmatised), not from WordNet relations.
- **Connectives** rotate in a fixed order (Python picks with `random`), so the C and Python texts differ; the plan (reach, radii, tenses, pivots) does not.
- **General-English prior** under the user's usage is the corpus unigram, not Brown. A word is "known" if it is in `voice_lex.bin`.
- ASCII only for the tokenisers; non-ASCII bytes count as letters. The reach for a numeric `scale` is `round(scale)`, not the GenerationalLineage descent.
- Noun irregulars (children, mice) are not in the lemma rules; irregular verbs are (table).
