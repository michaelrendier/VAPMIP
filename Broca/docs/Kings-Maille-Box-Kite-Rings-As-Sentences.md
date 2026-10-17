# King's Maille — Box-Kite Rings as Sentences

*The document-construction reading of Unified Chainmaille Theory. Companion to
`Ainulindale/wiki/119_unified_chainmaille_theory.md` (the graph / ring-theory
side). Written 2026-09-05.*

**Read alongside:** [Operating L_(I|O)](Operating-L-IO.md),
[Phase 25 — the box-kite debugger](Tuning-the-Engine/25_the_box_kite_debugger_and_the_negative_space.md),
[Phase 29 — generational lineage](Tuning-the-Engine/29_generational_lineage_and_the_anatomy_of_sigma.md),
[Phase 31 — WordNet box-kites](Tuning-the-Engine/31_wordnet_box_kites_and_the_pile_concept_emergence.md),
[Phase 35 — the spider-web composition cycle](Tuning-the-Engine/35_the_spider_web_composition_cycle.md).

---

## 0. The premise

The Archimedes Face document experiment (`plan: bubbly-pondering-wadler`) builds
text as **maille**, not as a stream:

    sentence   = a DOUBLE box-kite ring
                   ring A  from monad3_c.bin            (sentence construction)
                 + ring B  from monad_mathematics.bin   (granular maths vocab)
                 the OVERLAP of the two rings carries the extra weight
    line       = ring-sentences chained  →  a line of chainmail
    document   = lines stitched in the 3/1 pattern  →  King's Maille

**Why King's Maille specifically.** The King's / Byzantine weave is *recursive
doubling* — pairs of rings folded back through pairs, then those units folded
again. That is F₂'s Cayley graph, the Cayley–Dickson binary doubling, and the
box-kite's paired struts, all the same shape. A sentence is already a pair
(lang ring + maths ring); King's Maille is the weave whose unit of growth is a
**pair of pairs** — which is exactly `sentence → clause-pair → paragraph`.

---

## 1. The ring is an edge structure, so parse the edges

A box-kite ring: 16 slots, 15 relations (the nonzero XOR differences), 7 pencils
(ways to factor one relation into two). The **meaning of a ring-sentence lives on
the relations between its words, not on the words** — a LINE is three relations
that compose (`a XOR b = c`), and knowing two forces the third.

This is what the Zork parser (`Archimedes/parser.py`, reproduced from
`VAPMIP/zork_parser.py`) is doing:

    VERB  →  operator          (what the ring DOES)
    NOUN  →  slot              (which of the 16 placeholders)
    PREP  →  relation          (which of the 15 edges)

The parser fills slots; **the weave is the PREP structure.** Decompose the
relation a sentence expresses, not the objects it connects.

---

## 2. The three numbers as document diagnostics

From UCT: strength, superness, dispersal are one bilinear form per stitch read
along three traversal orders (`skill §4`). At the document scale:

| UCT quantity | traversal order | document reading |
|---|---|---|
| **ring strength** `N(r)` | one sentence's own closure | the weakest word-sense binding in the sentence — `min` over the ring. One unresolved anaphor caps the whole line, however strong the rest. |
| **superness** `‖I‖/‖O‖` | one stitch, both directions | per adjacent pair: how much they **mean the same** (`I` — shared payload, the ring-overlap weight) vs how much they **turn each other** (`O` — argumentative torque). |
| **dispersal** `λ₂(L)` | outward from the sentence under attack | how an objection to one sentence **distributes** through the paragraph. Large `λ₂` → the argument flexes around it; `λ₂ → 0` → brittle: crack one claim and the section drops because nothing else carried the load. |

`I` is the order-free part (the **multiplicative** encoding — a list, sentences
in any order); `O` is the order-bound part (the **positional** encoding — a
proof, sentences only in sequence). A paragraph that needs its order is
positional; one that does not is multiplicative. Choosing the wrong container
destroys exactly what that layer carries (Phase 33 / `skill §4`).

---

## 3. Inversion is not unwrapping (for a reader)

- **Unwrapping** a paragraph = reading it backward, sentence by sentence — the
  outline. Free, unique. The writer's `descend`.
- **Inverting** it = reconstructing the argument from the conclusion *without*
  the outline. A search. This is the reader's work, and it is where misreadings
  come from: the inverse of dispersal is **focusing** — the reader's attention
  channelled onto the one weak sentence, a Julia basin of bad readings. You
  cannot recover how an argument was built by replaying its conclusions.

`L_(I|O)` inherits this exactly (`Operating-L-IO.md` §0): you are always given
`theta` (the sentence as written) and never `beta` (what the writer meant). The
manual grants no new licence — a reading pulled from a step whose preconditions
were not met is wrong in language as it was wrong in `psi`.

---

## 4. σ = ½ — the well-built line

Every stitch carries as much shared meaning as directional push (`I = O`);
`N(r)` above the ambiguity threshold for every sentence; `λ₂` large enough that
no single sentence is load-bearing alone. Health check, per line:

    ln(I/O) + ln(O/I) = 0     to numerical tolerance

Drift from zero = the weave lost a sheet: a sentence that holds without coupling
(a non-sequitur that happens to be true) or couples without holding (a
transition with no content).

The **3/1**: one anchor sentence — the thesis, the load-bearing "1" — threaded
by three supporting sentences (the "3"). A pencil reading. King's Maille is 3/1
folded on itself: the paragraph becomes an anchor for the next.

---

## 5. Build home

- `PtolemyDesktop/Archimedes/chainmail.py` — `double_ring(lang_ring, maths_ring)`,
  `sentence_ring(...)`, `chainmail_line(rings)`, `persian_weave_3_1(lines)`;
  carry all three numbers per line + the `ln(I/O)+ln(O/I)=0` check.
- `PtolemyDesktop/wiki/Archimedes-Chainmail.md` — the stub note.
- Notated-for-later per the plan: the 3/1 Persian construction past the stub;
  `monad_mathematics.bin` rebuilt from the corpus; the C `mh_parse_mathdef()`
  wire.

Graph / ring-theory side: `Ainulindale/wiki/119_unified_chainmaille_theory.md`.
