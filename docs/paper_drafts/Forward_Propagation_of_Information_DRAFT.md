# Forward Propagation of Information: Teaching The Maths how to speak English

**Cody Michael Allison** (Michael Rendier) · independent researcher · the.wandering.god@gmail.com · ORCID 0009-0007-7239-6760

> **DRAFT: NOT THE PAPER.** Working abstract and the opening benchmark section, kept here until the paper is written (it will take another injection or two of insight first). Started 2026-10-13; this version 2026-10-14. The thesis "teach the maths to speak English" is first stated in this draft; `Ainulindale/AgeThird/VAPMIP_Paper.md` records it as deferred. Engineered-operator vocabulary only (no theory names), per the standing rule for the speaking engine. Companion pages: `docs/wiki/Tuning-the-Engine/42_every_voice_benchmark.md` (every transcript), `…/Scaled-Kite-English-Thought-Center-Context.md` §22–§24.

## Abstract (draft v3)

We report a successful experiment in teaching the maths to speak English. A language engine built from engineered operators runs entirely offline on a 2018 ThinkPad X1 Carbon (Core i7-8550U, no GPU, no network). It is a family of 24 monad modules, discovered procedurally from the file system, of which twelve speak; we benchmarked every one on the same six prompts. A verb-governed parser in the Infocom/Zork tradition selects one of sixteen operators, and the store holds each word as the counts of its 19 WordNet relation pointers. Across the twelve voices a warm reply takes from 0.3 ms to 1.5 s and adds 3 to 280 MB; measured on battery, the whole laptop spends from about 1 µWh to 4 mWh per reply, between 74 and about 389,000 times less than the roughly 0.3 Wh public estimate for one typical LLM query (the compiled REPL: 29 ms, 62 MB, 66.6 µWh measured). The voices differ in kind. One answers in a millisecond with the hypernym words of the prompt ("can you play the piano?" → "container stringed instrument percussion instrument keyboard instrument grand piano"); one is grammar-gated and returns "Pointer fingers." or an honest null where no verb resolves; one chooses its sentence frame from the dominant WordNet relation ("it comprises thumb", decompose · pinkie, pinky, knuckle, fingernail, thumb); and a document planner lays out a room, a bridge and a spiral of connectives in two milliseconds. Section 1 reports these benchmarks as literal transcripts, each with its script; the sections after it define the address, the parser and the store as code that runs. The road from here is one voice that carries the prompt's topic through the reply, with a prompt-extraction front end already built (3 to 19 ms warm; a part-of-speech tagger trained offline to 93.9%).

## 1. Benchmarks: every voice (convention D: measured, with the script path)

**1.1 Machine and method.** ThinkPad X1 Carbon 6th (20KH002XUS), i7-8550U, laptop on battery for every run. The 24 monad modules are the console's own `discover_monads()` list (`VAPMIP/*monad*.py`). Each was loaded as `/monad use <name>` loads it, in a fresh subprocess, then asked six prompts twice (cold, then warm). Scripts: `.claude/scratchpad/2026-10-14_all_monads_benchmark/` (`child.py`, `child2.py`, `bench_monads.py`, `compiled.py`, `gen_docs.py`). State checks: bins checksummed before and after (unchanged), `git status` clean.

**1.2 Census.** 6 modules speak through the console loader; 6 more speak through their own entry point (`process_input`, `speak`, `weave`, `basin`) that the loader does not look for; 12 are structure or tooling with no speaking entry point found.

**1.3 The twelve voices** (warm = second round, mean of six prompts; energy is whole-laptop, display and OS included, "derived" rows use the 9.255 W mean measured on 2026-10-13):

| Voice (module.class.method or adapter) | load s | RSS +MB | 1st-round ms | warm ms | whole-laptop µWh per reply | vs 0.3 Wh |
|---|---|---|---|---|---|---|
| VQ_rotary_monad.ValaQuenta.speak (str) | 0.08 | 3.3 | 0.30 | 0.30 | 0.77 (derived 9.255 W) | 388,979× lower |
| rotary_monad.AhuraMazda.speak (str) | 0.06 | 6.9 | 0.40 | 0.53 | 1.37 (derived 9.255 W) | 218,801× lower |
| ptolemy_monad.PtolemyMonad.process_input (resp) | 0.08 | 3.7 | 1,051.3 | 1.40 | 3.60 (derived 9.255 W) | 83,353× lower |
| boxkite_orbweaver_monad.OrbWeaverMonad.weave (doc) | 0.12 | 10.9 | 29.5 | 1.80 | 4.63 (derived 9.255 W) | 64,830× lower |
| ZD_rotary_monad.AhuraMazda.speak (str) | 0.08 | 6.8 | 1.60 | 1.97 | 5.06 (derived 9.255 W) | 59,336× lower |
| monad_english_io.MonadEnglish.basin (pool) | 0.73 | 279.5 | 40.0 | 3.58 | 9.21 (derived 9.255 W) | 32,566× lower |
| scaled_mind_eye_boxkite_kernel_monad (ScaledMindEyeMonadAdapter) | 1.23 | 84.2 | 1,852.9 | 31.0 | 87.5 (measured 10.17 W) | 3,427× lower |
| 19D_rotary_boxkite_monad (NineteenDMonadAdapter) | 0.79 | 73.3 | 2,056.8 | 32.4 | 83.2 (derived 9.255 W) | 3,605× lower |
| walkwithme_monad (GenerateMonadAdapter) | 0.2 | 5.3 | 307.5 | 111.8 | 318.2 (measured 10.25 W) | 943× lower |
| monad (GenerateMonadAdapter) | 0.03 | 5.1 | 329.2 | 120.9 | 286.1 (measured 8.52 W) | 1,048× lower |
| monad_harness_diagnostic (GenerateMonadAdapter) | 0.05 | 6.0 | 327.1 | 125.5 | 297.0 (measured 8.52 W) | 1,010× lower |
| rotary_rerun_boxkite_monad (BoxKiteMonad) | 2.08 | 154.2 | 3,548.4 | 1,507.2 | 4,065.3 (measured 9.71 W) | 74× lower |

**1.4 The compiled engine.** `ptolemy -r -n` (Zork parser in front of the C monad): 28.8 ms per line over 600 lines, 62 MB peak, CPU 17.3 s, replies such as `kite its engine probe`. Whole-laptop energy on battery on 2026-10-13: 9.255 W × 25.9 ms = **66.6 µWh per reply**; the engine's own share sits below the method's resolution (idle drifted 7.57 → 10.35 W), at most about 12 µWh. `ptol -say` (sentence creator through Python): 12.2 to 12.7 s per reply; `ptol` plain: 0.84 to 0.91 s.

**1.5 Sample transcripts** (prompt, then reply):
```
ptolemy_monad.process_input        (1.4 ms warm)
> can you play the piano?
container stringed instrument percussion instrument keyboard instrument grand piano
> finger pointer
digit hand extremity mark thumb

19D_rotary_boxkite_monad           (32 ms warm, grammar-gated)
> finger pointer
Pointer fingers.  [direction:decompose verdict:prime licensed:['SV', 'SVO']]
> good morning
(19D: nothing resolved — no WordNet verb found, 2 content word(s) resolved. NULL, not fabricated — no sentence generated.)

rotary_rerun_boxkite_monad         (1.5 s warm, relational frame)
> finger pointer
It comprises thumb.  [what_does_X_do/SVO/technical]   [decompose · words: pinkie, pinky, knuckle, fingernail, thumb, point, head, shaft]

boxkite_orbweaver_monad.weave_via  (2 to 8 s, document plan)
> finger pointer
[paper  scale=2.0  reach=2  turbulent  radii=2  blocks=13]
BRIDGE: it belongs to the domain of pinkie.
SCAFFOLD: decompose: it is made of pinkie and pinky.  /  situate: it is part of pinkie.
CAPTURE: hence · as for · more precisely · for instance · that said · overall · namely · in detail · in other words · for example · on the whole
```
Full transcripts for all twelve voices: `docs/wiki/Tuning-the-Engine/42_every_voice_benchmark.md` §5.

**1.6 Evidence for the abstract's numbers.** Latency, memory and the voice table: this section's scripts. Energy: `.claude/scratchpad/2026-10-13_monad_energy/` (battery discharge, AC unplugged; the 0.3 Wh comparison uses public figures: Google 0.24 Wh, OpenAI 0.34 Wh, Epoch AI about 0.3 Wh, via secondary coverage). Extraction front end: `.claude/scratchpad/2026-10-13_nltk_extraction_pipeline/` (3 to 19 ms warm; UD-EWT UPOS accuracy 0.9389). The 19-count address round trip (146,743 of 146,743) is recorded in the companion paper and was not re-run here.

## Conventions (cs-paper-code-conventions)
Benchmarks = D. Parser, address, store = B (short verbatim listings) or A (path + function) by size. WordNet, NLTK and Infocom/Zork = A: cited, not re-derived; Zork is built-against, not post-hoc. The unported composter and the single-voice target = C, labelled THEORETICAL.
