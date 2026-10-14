## Phase 42 — Every Voice: all the monads, benchmarked on the same six prompts (2026-10-14)

*Claude Sonnet 5.5, at Cody's request ("use every available voice ... benchmark every step of the way"). A measurement session, not a build: no engine file changed. Scripts, raw JSON and logs: `.claude/scratchpad/2026-10-14_all_monads_benchmark/` (mirrored to `ContextPlease/claude/scratchpad/`). Machine: ThinkPad X1 Carbon 6th, Core i7-8550U, no GPU, laptop on battery (AC unplugged) for every run. Evidence labels: [MEASURED] unless stated.*

### 1. What was run, exactly
* **The list is the console's own.** `PtolemyDesktop/ptolemy_console.py` `discover_monads()` globs `VAPMIP/*monad*.py` (procedural, never hard-coded): **24 modules** on 2026-10-14. Each was loaded the way `/monad use <name>` loads it (`load_monad_by_name`), one fresh subprocess per monad, then asked the **same six prompts twice** (round 1 = cold, round 2 = warm): "finger pointer", "what is a tree", "neutron generation in different reactor types", "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered".
* **Every step timed:** console import, module load, RSS before/after load, per-reply wall time (cold and warm), CPU time per reply, whole-laptop battery power sampled every 0.5 s through the warm round.
* **State integrity:** `~/.ptolemy/monad*.bin` backed up beforehand, `PtolC/*.bin` checksummed before and after (unchanged), VAPMIP `git status` clean. Nothing was saved (`-n` for the C REPL).

### 2. The census of 24 [MEASURED by introspection and loading]
| Group | Count | Modules |
|---|---|---|
| A. Speak through the console loader (`say()` / `generate()` / known adapter) | 6 | `rotary_rerun_boxkite_monad` (BoxKiteMonad), `19D_rotary_boxkite_monad`, `scaled_mind_eye_boxkite_kernel_monad`, `monad`, `monad_harness_diagnostic`, `walkwithme_monad` |
| B. Speak through their own entry point, which the loader does not look for | 6 | `ptolemy_monad.PtolemyMonad.process_input`, `VQ_rotary_monad.ValaQuenta.speak`, `rotary_monad.AhuraMazda.speak`, `ZD_rotary_monad.AhuraMazda.speak`, `boxkite_orbweaver_monad.OrbWeaverMonad.weave`, `monad_english_io.MonadEnglish.basin` (the idea pool) |
| C. Structure / tooling, no speaking entry point found | 12 | `19D_boxkite_context_monad`, `RF_monad`, `UDEO_monad`, `intention_monad`, `lio_monad`, `monad_addressing`, `monad_browse`, `monad_bus`, `monad_combine` (its `hear` learns), `monad_identity`, `rotary_rerun_monad`, `translator_monad` |

The console's `/monad list` offers all 24 but `/monad use` can switch to only the 6 of group A; the 6 of group B each speak but are not wired (open item below).

### 3. The twelve voices, fastest first (warm = second round, mean of six prompts)
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

*Reading the energy column.* "Whole-laptop" means the display, radios and OS are included; baseline power (about 9 W, drifting 7.6-10.4 W) dominates, so energy per reply is essentially latency x about 9 W. Rows marked **measured** used the mean power sampled during that voice's warm round; rows marked **derived** were too short to sample (under 0.5 s) and use 9.255 W, the whole-laptop mean measured on 2026-10-13. The last column compares against the roughly 0.3 Wh public estimate for one typical LLM query (Google 0.24 Wh, OpenAI 0.34 Wh, Epoch AI about 0.3 Wh, via secondary coverage). The slowest voice here is still about 74 times lower.

### 4. The compiled voices, same six prompts
| Voice | Per reply | Memory | Replies |
|---|---|---|---|
| `ptolemy -r -n` (Zork REPL, in-process C monad) | **28.8 ms/line** (600 lines in 17.31 s; CPU 17.29 s) | 62 MB peak | `kite its engine probe`, `kite open and where`, `kite pores angular helicities` |
| `ptol "<prompt>"` (plain, word bag + SVG paper) | 839-914 ms | about 298 MB (measured 2026-10-13) | epic-vocabulary word bags |
| `ptol -say "<prompt>"` (sentence creator through Python + NLTK) | 12.2-12.7 s | about 320 MB (measured 2026-10-13) | `Priest relates country.`, `Time is able.`, `George relates country.` |

### 5. Transcripts (Convention D: prompt, then the reply; warm round; the spaces inside the `generate` voices are hair/thin/em-space characters, shown here as plain spaces)

**VQ_rotary_monad.ValaQuenta.speak** (str)
```
> finger pointer
pointer
> what is a tree
is
> neutron generation in different reactor types
is
> good morning
morning
> can you play the piano?
can
> the first reactor was built after neutrons were discovered
is
```

**rotary_monad.AhuraMazda.speak** (str)
```
> finger pointer
finger
> what is a tree
finger
> neutron generation in different reactor types
finger
> good morning
finger
> can you play the piano?
finger
> the first reactor was built after neutrons were discovered
finger
```

**ptolemy_monad.PtolemyMonad.process_input** (resp)
```
> finger pointer
digit hand extremity mark thumb
> what is a tree
woody plant metric linear unit cinchona limb nanometer
> neutron generation in different reactor types
electrical device varied linear unit difference kind
> good morning
day early-morning hour common good advantage time period
> can you play the piano?
container stringed instrument percussion instrument keyboard instrument grand piano
> the first reactor was built after neutrons were discovered
electrical device rank make coil nucleon
```

**boxkite_orbweaver_monad.OrbWeaverMonad.weave** (doc)
```
> finger pointer
[paper  scale=2.0  reach=2  laminar  radii=2  blocks=9] ⏎ ROOM  : Cassini b/c=0.640  discrete  (c=0.781 b=0.500)  sample6=[0.63, 0.62, 0.59, 0.56, 0.51, 0.47] ⏎ BRIDGE: it belongs to the domain of finger. ⏎ FRA
> what is a tree
[paper  scale=2.0  reach=2  laminar  radii=1  blocks=7] ⏎ ROOM  : Cassini b/c=1.028  lemniscate  (c=0.486 b=0.500)  sample6=[0.56, 0.55, 0.54, 0.53, 0.52, 0.5] ⏎ BRIDGE: it belongs to the domain of what. ⏎ FRAM
> neutron generation in different reactor types
[paper  scale=2.0  reach=2  turbulent  radii=2  blocks=13] ⏎ ROOM  : Cassini b/c=0.621  discrete  (c=0.460 b=0.286)  sample6=[0.37, 0.36, 0.34, 0.32, 0.29, 0.26] ⏎ BRIDGE: it belongs to the domain of neutron. ⏎
> good morning
[paper  scale=2.0  reach=2  laminar  radii=2  blocks=9] ⏎ ROOM  : Cassini b/c=0.672  discrete  (c=0.744 b=0.500)  sample6=[0.62, 0.61, 0.59, 0.56, 0.52, 0.48] ⏎ BRIDGE: it belongs to the domain of good. ⏎ FRAME
> can you play the piano?
[paper  scale=2.0  reach=2  turbulent  radii=2  blocks=13] ⏎ ROOM  : Cassini b/c=1.167  continuous  (c=0.286 b=0.333)  sample6=[0.36, 0.36, 0.36, 0.35, 0.34, 0.33] ⏎ BRIDGE: it belongs to the domain of can. ⏎ F
> the first reactor was built after neutrons were discovered
[paper  scale=2.0  reach=2  turbulent  radii=3  blocks=19] ⏎ ROOM  : Cassini b/c=0.577  discrete  (c=0.495 b=0.286)  sample6=[0.38, 0.37, 0.35, 0.32, 0.29, 0.25] ⏎ BRIDGE: it belongs to the domain of first. ⏎ F
```

**ZD_rotary_monad.AhuraMazda.speak** (str)
```
> finger pointer
∅
> what is a tree
∅
> neutron generation in different reactor types
∅
> good morning
∅
> can you play the piano?
∅
> the first reactor was built after neutrons were discovered
∅
```

**monad_english_io.MonadEnglish.basin** (pool)
```
> finger pointer
pool: his, in, at, seven, of, a, and, on, her, my, to, he
> what is a tree
pool: aileth, needeth, happens, knows, wonder, sort, follows, exactly, else, news, cause, ho
> neutron generation in different reactor types
pool: ambitransitive, natures, degrees, ways, kinds, meanings, types, parts, classes, times, sort, sorts
> good morning
pool: morrow, cheer, behavior, deal, luck, manners, news, madam, earnest, counsel, faith, fortune
> can you play the piano?
pool: countess’s, perizzites, hivites, caul, foundation’s, saracens, antonines.—part, wayback, doer, augustan, specifick, fourteenth
> the first reactor was built after neutrons were discovered
pool: countess’s, perizzites, hivites, caul, foundation’s, saracens, antonines.—part, wayback, doer, augustan, specifick, fourteenth
```

**scaled_mind_eye_boxkite_kernel_monad** (ScaledMindEyeMonadAdapter)
```
> finger pointer
Pointer fingers.  [direction:decompose verdict:prime licensed:['SV', 'SVO']] [hub fiber: strut=6 fixed_point_weight=0.6400 is_zero_divisor=False]
> what is a tree
A ises tree.  [direction:situate verdict:prime licensed:['SVO']] [hub fiber: strut=5 fixed_point_weight=0.6400 is_zero_divisor=False]
> neutron generation in different reactor types
(19D: direction='compare' has no speech_act mapping yet — reporting the real finding rather than forcing one: leaves=['neutron', 'generation', 'in', 'different', 'reactor'])
> good morning
(19D: nothing resolved — no WordNet verb found, 2 content word(s) resolved. NULL, not fabricated — no sentence generated.)
> can you play the piano?
Play cans piano into piano.  [direction:decompose verdict:prime licensed:['SV', 'SVO', 'SVOA']] [hub fiber: strut=5 fixed_point_weight=0.6400 is_zero_divisor=False]
> the first reactor was built after neutrons were discovered
(19D: direction='compare' has no speech_act mapping yet — reporting the real finding rather than forcing one: leaves=['first', 'reactor', 'built', 'after', 'neutrons', 'were', 'discovered'])
```

**19D_rotary_boxkite_monad** (NineteenDMonadAdapter)
```
> finger pointer
Pointer fingers.  [direction:decompose verdict:prime licensed:['SV', 'SVO']]
> what is a tree
A ises tree.  [direction:situate verdict:prime licensed:['SVO']]
> neutron generation in different reactor types
(19D: direction='compare' has no speech_act mapping yet — reporting the real finding rather than forcing one: leaves=['neutron', 'generation', 'in', 'different', 'reactor'])
> good morning
(19D: nothing resolved — no WordNet verb found, 2 content word(s) resolved. NULL, not fabricated — no sentence generated.)
> can you play the piano?
Play cans piano into piano.  [direction:decompose verdict:prime licensed:['SV', 'SVO', 'SVOA']]
> the first reactor was built after neutrons were discovered
(19D: direction='compare' has no speech_act mapping yet — reporting the real finding rather than forcing one: leaves=['first', 'reactor', 'built', 'after', 'neutrons', 'were', 'discovered'])
```

**walkwithme_monad** (GenerateMonadAdapter)
```
> finger pointer
a morning pointer first finger the different play discovered is a morning pointer finger first different play morning is a is pointer finger finger a is pointer a a finger is pointer is pointer a is finger is f
> what is a tree
is finger pointer a pointer is pointer finger a finger is finger pointer a finger is finger pointer pointer finger a is pointer pointer finger a is a is pointer a is pointer finger a pointer is pointer is a a f
> neutron generation in different reactor types
is a finger pointer pointer is pointer finger a pointer is pointer finger a finger is a pointer pointer a is finger pointer pointer a is finger is finger pointer is a is a pointer pointer a finger finger pointe
> good morning
a pointer finger finger a finger pointer finger pointer finger pointer a pointer a finger a is morning a pointer a morning pointer finger a is finger pointer finger a pointer finger pointer finger is is finger 
> can you play the piano?
is a finger pointer pointer is pointer finger a pointer is finger pointer a pointer is finger a finger pointer a finger a finger is a finger a pointer is is finger pointer finger a a finger pointer finger is is
> the first reactor was built after neutrons were discovered
is pointer finger a pointer is pointer finger a pointer is finger pointer a pointer is finger pointer finger a pointer is pointer is a pointer is finger finger a a is a is pointer pointer is finger is pointer p
```

**monad** (GenerateMonadAdapter)
```
> finger pointer
a morning pointer first finger the different play discovered is a morning pointer finger first different play morning is a is pointer finger finger a is pointer a a finger is pointer is pointer a is finger is f
> what is a tree
is finger pointer a pointer is pointer finger a finger is finger pointer a finger is finger pointer pointer finger a is pointer pointer finger a is a is pointer a is pointer finger a pointer is pointer is a a f
> neutron generation in different reactor types
is a finger pointer pointer is pointer finger a pointer is pointer finger a finger is a pointer pointer a is finger pointer pointer a is finger is finger pointer is a is a pointer pointer a finger finger pointe
> good morning
a pointer finger finger a finger pointer finger pointer finger pointer a pointer a finger a is morning a pointer a morning pointer finger a is finger pointer finger a pointer finger pointer finger is is finger 
> can you play the piano?
is a finger pointer pointer is pointer finger a pointer is finger pointer a pointer is finger a finger pointer a finger a finger is a finger a pointer is is finger pointer finger a a finger pointer finger is is
> the first reactor was built after neutrons were discovered
is pointer finger a pointer is pointer finger a pointer is finger pointer a pointer is finger pointer finger a pointer is pointer is a pointer is finger finger a a is a is pointer pointer is finger is pointer p
```

**monad_harness_diagnostic** (GenerateMonadAdapter)
```
> finger pointer
a morning pointer first finger the different play discovered is a morning pointer finger first different play morning is a is pointer finger finger a is pointer a a finger is pointer is pointer a is finger is f
> what is a tree
is finger pointer a pointer is pointer finger a finger is finger pointer a finger is finger pointer pointer finger a is pointer pointer finger a is a is pointer a is pointer finger a pointer is pointer is a a f
> neutron generation in different reactor types
is a finger pointer pointer is pointer finger a pointer is pointer finger a finger is a pointer pointer a is finger pointer pointer a is finger is finger pointer is a is a pointer pointer a finger finger pointe
> good morning
a pointer finger finger a finger pointer finger pointer finger pointer a pointer a finger a is morning a pointer a morning pointer finger a is finger pointer finger a pointer finger pointer finger is is finger 
> can you play the piano?
is a finger pointer pointer is pointer finger a pointer is finger pointer a pointer is finger a finger pointer a finger a finger is a finger a pointer is is finger pointer finger a a finger pointer finger is is
> the first reactor was built after neutrons were discovered
is pointer finger a pointer is pointer finger a pointer is finger pointer a pointer is finger pointer finger a pointer is pointer is a pointer is finger finger a a is a is pointer pointer is finger is pointer p
```

**rotary_rerun_boxkite_monad** (BoxKiteMonad)
```
> finger pointer
It comprises thumb.  [what_does_X_do/SVO/technical]   [decompose · words: pinkie, pinky, knuckle, fingernail, thumb, point, head, shaft]
> what is a tree
It comprises solution.  [what_does_X_do/SVO/surface]   [decompose · words: Israelite, coward, mixture, furlong, treetop, beggar]
> neutron generation in different reactor types
It resembles time.  [what_does_X_do/SVO/technical]   [compare · words: varied, pica, informal, mandarin, underling]
> good morning
It belongs to martin.  [how/SVA/thesis]   [situate · words: tidings, morrow, breeding, bosom, hope, sir, time, clip]
> can you play the piano?
It comprises service.  [what_does_X_do/SVO/technical]   [decompose · words: service, understand, grand]
> the first reactor was built after neutrons were discovered
It comprises martin.  [what_does_X_do/SVO/technical]   [decompose · words: standing, compare, citizen, syllable]
```


**The document planner, heavy path** (`OrbWeaverMonad.weave_via(RotaryBoxKiteMonad(), prompt)`, real words from the box-kite voice): 8.1 s for "finger pointer" (first call, includes WordNet), 3.0 s for "what is a tree", 2.1 s for the reactors prompt. For "finger pointer" it laid out 13 blocks: `ROOM: Cassini b/c=0.485 discrete`, `BRIDGE: it belongs to the domain of pinkie.`, `FRAME: it is part of pinkie.`, a scaffold (`decompose: it is made of pinkie and pinky.` / `situate: it is part of pinkie.`) and a capture spiral of 13 connectives (`hence`, `as for`, `more precisely`, `for instance`, `that said`, `overall`, `namely`, `in detail`, `in other words`, `for example`, `on the whole`, ...). The light path (`weave`, its own crude word sniff) produces the same skeleton in about 2 ms but anchors on whatever its sniff finds ("what" for "what is a tree").

### 6. What the numbers say
* **Range, same laptop, same prompts:** warm reply from 0.30 ms to 1.5 s; added memory from 3 MB to 280 MB; whole-laptop energy per reply from about 1 µWh to 4 mWh, i.e. every voice is between 74 and about 389,000 times below the typical public per-query figure.
* **Nine distinct behaviours, not twelve:** `monad`, `monad_harness_diagnostic` and `walkwithme_monad` return byte-identical word streams (one generator behind three files); `19D_rotary_boxkite_monad` and the scaled-mind-eye adapter return the same sentences (the second appends a hub-fiber reading).
* **1 ms and on topic:** `ptolemy_monad.process_input` answers with the hypernym/definition words of the prompt: "finger pointer" -> `digit hand extremity mark thumb`; "can you play the piano?" -> `container stringed instrument percussion instrument keyboard instrument grand piano`; "good morning" -> `day early-morning hour common good advantage time period`. The reactors prompt gets `electrical device ...` (the electrical sense again, as in Lesk).
* **Grammar-gated with honest nulls (about 32 ms):** the 19D voice returns `Pointer fingers.` and `A ises tree.`, licensed against SV/SVO/SVOA frames, and reports a null where nothing resolves (3 of 6 prompts: "good morning" had no WordNet verb; the two "compare" prompts have no speech-act mapping yet), instead of forcing a sentence.
* **Relational frames (1.5 s):** the box-kite voice chooses `decompose / compare / situate` from the dominant WordNet relation: `It comprises thumb. [decompose · words: pinkie, pinky, knuckle, fingernail, thumb, point, head, shaft]`; it misses on some prompts (`It comprises solution.` for "what is a tree").
* **Document planning in milliseconds:** the weaver produces room, bridge, frame, scaffold and connective spiral in about 2 ms (light) or 2-8 s (heavy path with real words).
* **Degenerate or minimal voices, recorded as results:** `rotary_monad.AhuraMazda.speak` answers `finger` to all six (state does not release between prompts); `ZD_rotary_monad.AhuraMazda.speak` answers the empty set `∅` to all six; `VQ_rotary_monad.ValaQuenta.speak` returns one word echoed from the prompt (`pointer`, `is`, `is`, `morning`, `can`, `is`).
* **The idea pool is the memory-heavy part:** `MonadEnglish.basin` takes 280 MB of RSS and 0.73 s to load but answers in 4 ms; its pools are sharp for some prompts ("good morning" -> `morrow, cheer, behavior, luck, manners, fortune`) and noise for others ("can you play the piano?" -> `countess's, perizzites, hivites, caul ...`), the granular-store sanitising item already on the list.

### 7. Open items from this session
1. `load_monad_by_name` only recognises `say()` / `generate()` and two named adapters; six speaking monads (group B) are listed but cannot be switched to. Adding `speak` / `process_input` / `weave` adapters would make all twelve selectable. Not done (no go given).
2. Whole-laptop energy per voice is dominated by baseline; resolving each voice's own share needs a longer run per voice or the display off.
3. First-round times (up to 3.5 s) are WordNet/NLTK loads; the compiled REPL pays none of that (28.8 ms/line).
4. Group C modules were not asked to speak; they may have conversational functions under names this survey did not match.
