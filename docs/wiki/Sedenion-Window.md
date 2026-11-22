# The sedenion window

*2026-11-21. Code: `sedenion_window.py`; tests: `tests/test_sedenion_window.py` (11). Python first; nothing is ported to `ptol.c`. Symbols: `@RCCM_SYMBOLS`. Licence: proprietary, all rights reserved.*

One object that reads and writes a sentence, one word per tick. **W_S** is the big web (the sentence: its frame, and the 16-slot ring of the context heard, slot 0 = e0). **w_s** is the little web (one word). The heartbeat per word: W_S shrinks to the open slot, w_s picks the word, W_S places it and is **rescaled** to the whole sentence, `repass` (tone, tense, conjugation), next slot. The cost of a pick is −log₂ P, with P the pick's weight rescaled over the candidates; a sentence's cost is the sum.

## Parts
| part | what |
|---|---|
| `Bigram` | word-to-word probabilities from a corpus (the standard corpus in the run below) |
| `Neighborhood` | relation neighbours of a topic word in WordNet (hypernym, hyponym, member/part, similar, also-see, entailment, siblings), each with its exact context class, `gamma_radial`, Broca reading (non-zero relations) and Wernicke reading (1 + γ) |
| pathway ring | the closed class (determiners, prepositions, conjunctions, auxiliaries) is a ring of a few dozen words: a pathway pick draws from the ring, not from the language |
| `read(text)` | one tick per word; content words enter the ring; unknown words are noted; the sentence goes to `LiveVocabulary.hear` if one is attached |
| `write(prompt)` | frames `DET N V DET N`, `DET N V PREP DET N`; candidates from the prompt's neighbourhood; deterministic |
| `Sensors` | the VAG-COM style harness (the dPrint idea, altered): read/write, in the loop. `VAGCOM=1` prints `[vag]` blocks (STEP, WORD, BALANCE) and `[tone]` lines; always recorded in `sensors.log`. Writable channels: `tone_target`, `tone_override`, `pathway_ring` |
| markers | three invisible Tag characters (U+E0020–E007E, category Cf) per word: **tone** (one of 9 neuromodulator axes × 7 levels: DA 5HT NE OT GLU GABA eCB ACh OPI), **tense** (8), **conjugation** (8). Injective (tested); `show_markers` prints them as `<NE:4\|past\|3sg>` |
| `Persuader` | Pascal's rule as named (interpretation, to be confirmed): meet the heard tone one level below its strength, then step one level per word to the target tone |
| `scale_point(word)` | Z = Wernicke + i·Broca for the Scale engine's Broca–Wernicke Rings Scale |

The codebook (axes, levels, tense and conjugation lists) is provisional: the author has not fixed it.

## Usage over time (added 2026-11-21)
With `english=` (a `MonadEnglish`) every word read deepens the co-occurrence field (the A-matrix, `monad_english_io.hear`: windowed, weight decaying with distance, merged by max); new words enter; the same word used again deepens (`fire_count`). **He hears what he says**: a written sentence is fed back at echo 1, and `ECHO_CAP` (5) makes a fifth loop a no-op, which is the feedback-cancelling cap on the ears (tested). With `vocab=` (a `LiveVocabulary`) definitional sentences add senses and edges with history ([Live-Vocabulary](Live-Vocabulary.md)). Sensor block `USAGE` reports edges deepened and new words per read.

## The window as a two-way mirror
The window is the shared tool of Broca (discrete, the scalar boxkite) and Wernicke (continuous, the scaled boxkite): the same statement in both maths. In the Scale engine's terms it is the fold Γ = (Z − Z₀)/(Z + Z₀) with Z = Wernicke + i·Broca and its inversion (Γ → −Γ). **Bad lighting is measurable here:** the two readings live on different scales (Wernicke 1 + γ lies in 0.1 … 0.9, Broca counts 1 … 7), so the fold saturates, |Γ| of 0.85 to 0.92 in the run above: the mirror reflects almost everything and the other side cannot see through. Rescaling Broca to Wernicke's range, or choosing Z₀ per point, is the adjustment; which one is the author's call.

## A run (2026-11-21, the standard corpus as the language model)
```
VAGCOM=1  write("I HATE the king, he is stupid!")
[vag] STEP t=8  slot=DET  r_before=1.0 r_after=0.592927 bits=0.754
[vag] WORD t=9  word=king pathway=False cls=3 gamma=-0.3163
[vag] BALANCE   wernicke=0.6837 broca=4 gamma_in=0.9246 gamma_out=0.9246 balance=0.0
[tone] TONE t=10 word=hate tone=NE:2 tense=present conj=3sg marker=<NE:2|present|3sg>
SENTENCE: The king hates the simple.
MARKED  : <NE:4|base|base>the <NE:3|base|base>king <NE:2|present|3sg>hates <NE:1|base|base>the <GABA:3|base|base>simple.
```
The tone marker follows the Persuader: it starts on the heard side (NE, one level below the heard 5), eases one level per word and ends on the target (GABA).

## What the tests show, and what they do not
* Shown: one tick per word and the ring fill; every pick rescaled back to 1.0; cost = −log₂ P per pick and the sentence cost is their sum; pathway picks come from rings of at most 8 candidates (2.2 bits on average in the tests; 0.6 to 0.75 bits in the run), content picks from a pool of over a hundred; determinism; the marker trajectory; the sensors stream; the window teaches the live vocabulary.
* **Not shown, and not true yet:** content words are not cheap-to-choose because they are good, only because the prompt's own words dominate the neighbourhood (`king` costs 0.14 bits: it was in the prompt). The sentence above echoes the prompt's `hate`; tone only changes the markers, not the word choice. Nothing yet lets a neuromodulator axis steer which words are candidates.
* The BALANCE block is an identity (|Γ_in| = |Γ_out| and Γ_in + Γ_out = 0 for the inversion), a check that the arithmetic is right, not an independent measurement. J_red and J_blue are not yet measured in the window.
* Candidate pools come from WordNet relation neighbours. The context hash alone does not separate neighbourhoods for most words (88% of WordNet is one attractor basin: `FourthAgePaper/ScalarContextPropagation/map/README.md`).
