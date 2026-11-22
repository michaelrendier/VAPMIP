# PtolemyHolcus — RedBlue Geometries Engine (VAPMIP)

**Ptolemaious Holcaios Philadelphos** — *Ptolemy, The Extractor, Brother-Loving* — v5.2.0 "Virtual Action Potential"

*Formerly SMMIP (renamed 2026-05-26). Page last rewritten 2026-11-21.*

**Licence: Proprietary. All rights reserved** (see `LICENSE`, `NOTICE`). The mathematics behind it is published separately under the GNU licence, outside this repository. WordNet 3.0 and the other third-party data keep their own licences (`WORDNET_LICENSE.txt`, `NOTICE`).

## What this repository is

An offline language engine. Each word is stored as the counts of its 19 WordNet relation pointers and carries a prime-number address; a verb-governed parser in the Infocom/Zork tradition (`zork_parser.py`, `PtolC/zork.c`) selects one of sixteen operators; the voices turn a prompt into a reply. It runs on a laptop CPU with no GPU and no network. Twenty-four monad modules, twelve of which speak; a warm reply takes 0.3 ms to 1.5 s (measured 2026-10-14, table in `docs/Repository_Reference.md`).

The paper reporting those measurements is `paper/Forward_Propagation_of_Information.pdf` (source `paper/Forward_Propagation_of_Information.md`).

## Current work (2026-11)

Three tools, in the order they are used. None is a finished voice.

| tool | what it is | where |
|---|---|---|
| **Scalar boxkite** | the discrete, static kite: seven ordered pairs, pencil, string, flashlight, tension law. One word. Never given motion. | `19D_rotary_boxkite_monad.py`, `Currentwork/Broca/` |
| **Scaled boxkite** | the Mind's-Eye kite that moves: context relations, struts, the kite in motion, context flow. A sentence. Constrains and orders; supplies no candidates. | `scaled_mind_eye_boxkite_kernel_monad.py`, `Currentwork/Broca/` |
| **Orbweaver monads** | the semantic web: which words, chosen by their relation to the prompt; open vocabulary, graded weights; seven deconstruction names `ANCHOR SPAN SCAFFOLD ELABORATE HOOK WRAP SHELL`. Benched, not yet played as a voice; the content extractor v0, the sanitiser and the standard testing corpus are built (`Currentwork/Wernicke/`). | `boxkite_orbweaver_monad.py` (`OrbWeaverMonad.weave`), `Currentwork/Wernicke/` |

Beside them: **SemPriCon** (the prime-concept baseline, Chinese first; `Currentwork/SemPriCon/`) and **ScalarContextPropagation** (the paper on carrying context along the field; `FourthAgePaper/ScalarContextPropagation/`).

Open: context flow, carrying the prompt's topic through the reply as discrete words along a field scaled for the response; scorers for the orbweaver; the engineering white paper.

## Layout (restructured 2026-11-21)

`Currentwork/` (Broca, Wernicke, SemPriCon) · `docs/` · `paper/` and `FourthAgePaper/` · `outreach/` · `records/` · `archive/` · the engine files at the root (`docs/FILE_MAP.md` maps them). Old path → new path: `Currentwork/README.md`.

## Where to read

| to learn | read |
|---|---|
| the scaled/scalar boxkite | `Currentwork/Broca/README.md`, `docs/wiki/Scaled-Kite-English-Thought-Center-Context.md`, `docs/wiki/Boxkite-Relational-Atlas.md` |
| the orbweaver | `Currentwork/Wernicke/README.md`, `docs/semantic_orbweaver_notes.md` |
| the context-flow tests | `docs/context_flow_spec/` (95 tests) |
| SemPriCon | `Currentwork/SemPriCon/README.md`, `docs/wiki/Tuning-the-Semantic-Prime-Concept-Engine/00_index.md` |
| the English field in the Scale engine's rings (the stored A-matrix has no direction) | `docs/wiki/English-Field-Rings.md` |
| Tao 41 in the harness (laughter is expected, not correction) | `three_hearers.py`, `harness.py` |
| the Cyclic Context Gearbox (DATA SELF and USER SELF, lossless FIFO odometer) | `docs/wiki/Context-Gearbox.md`, `context_gearbox.py` |
| English usage statistics as one poll; levels by educational response | `docs/wiki/English-Statistics.md`, `english_stats.py` |
| the sedenion window (reads and writes a sentence; sensors; tone/tense/conjugation markers) | `docs/wiki/Sedenion-Window.md`, `sedenion_window.py` |
| every boxkite exploration on both boxkites | `dual_boxkite.py` |
| the exhaustive Scalar Boxkite context map, basins and pictures | `FourthAgePaper/ScalarContextPropagation/map/README.md` |
| the live vocabulary (the Monad adds and refines its own words) | `docs/wiki/Live-Vocabulary.md`, `live_vocabulary.py` |
| how to run it | `docs/wiki/Operating-the-Monad.md`, `docs/NLP_ENVIRONMENT.md` |
| names and symbols | `docs/wiki/Name-Table.md` |
| everything else that was in this README | `docs/Repository_Reference.md` (section map at its top) |
| the chronology of how the engine was tuned | `docs/wiki/Tuning-the-Engine/00_index.md` (a record; not edited) |
| what changed, and when | `CHANGELOG.md`, `TODO.md` |
| the open documentation job | `records/UPDATE_JOB_2026-11-21.md`, `records/AUDIT_2026-11-21.md` |

## Symbols (author's standing ruling)

| symbol | meaning | value |
|---|---|---|
| α | fine-structure constant | 1/137.036 |
| A_π | Lambert W fixed point W(1); the Fermat side: speed of causality, inertia | 0.5671432904 |
| Ω_ζΣ (= Ω_RZ) | d*; the Riemann side: Hagedorn information ceiling, entropy | 0.2463072015 |

d*·ln 10 = A_π. The code predates the ruling: it names the value 0.56714 `OMEGA_ZS`, and `D_STAR` = 0.24600 is the rounded spectral value. When a name and a value disagree, the table decides.

## Try it (about five minutes)

```
cd PtolC && make                          # builds ptol and ptolemy (needs gcc, make, libm, libxml2-dev)
./ptolemy -r -n                           # the Zork REPL, nothing saved; try: what is a tree
./ptol -M tree                            # one word: its store entry and Gamma-Radial windspeed
./ptol -w                                 # the tabbed console; then /monad list and /monad use ptolemy_monad
cd .. && python3 benchmarks/all_voices/benchmark_voices.py    # the all-voices table, about 3 minutes
```

If the system `python3` cannot import `nltk`, use `../PtolemyDesktop/.venv/bin/python` (each repository has its own `.venv`).

## Related repositories

| Repo | Contents |
|---|---|
| **[PtolemyHolcus](https://github.com/michaelrendier/PtolemyHolcus)** (this) | the engine: C source, Python reference, Face, releases |
| **[PtolemyDesktop](https://github.com/michaelrendier/PtolemyDesktop)** | desktop application, the Faces, PtolBus |
| **[Ainulindale](https://github.com/michaelrendier/Ainulindale)** | the Ĥ_RB derivation, Witches Hat geometry |
| **[POE](https://github.com/michaelrendier/POE)** | pendant hardware, vehicle interface, authentication, radio |

*CLAUDE-SMMNIP-00729-56714-24600*
