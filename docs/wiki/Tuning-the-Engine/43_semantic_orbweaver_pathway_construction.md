## Phase 43: Semantic Orbweaver Pathway Construction (2026-10-16) — STUB

*Claude Sonnet 5.5, at Cody's direction at the end of the paper session. A stub: nothing here is built, nothing is measured, every claim is a design statement. The full context is in the primer `ContextPlease/claude/hist_prime/VAPMIP/CONTEXT_PRIMER_2026-10-16_SEMANTIC_ORBWEAVER.md`; read that first.*

---

### The phase

Engineer the orbweaver monad (Phase 35, `boxkite_orbweaver_monad.py`) into the **semantic** part of the sentence constructor, with the **original semantic prime hash** as the address space and a **spider's-web pathway** as the propagation model. **No box kite in this part.** The sentence constructor needs a semantic, a phonetic and a contextual function; the first monad (v1.0, 2026-05-15, `monad.c` at `fb7ba29`) was the simplest and lightest method used, and its first reply, "holcussamestuffseemy" (screenshot 3 of the paper, 2026-05-19), came from the spelling hash and co-occurrence alone.

### Standing directive (Cody, 2026-10-16)

**The semantic orbweaver pathway is weighted heavier than the context boxkite in sentence construction.** Proposed form, for Cody to confirm: `S = w_sem · S_web + w_ctx · S_kite` with `w_sem > w_ctx` (start 2 : 1, a **[PARAM]** settled by a measured sweep); the kite may extinguish a candidate but not outvote the web.

### What is to be tested (all `UNTESTED`)

1. **T0** the first monad's behaviour reproduced on today's store (`monad_speak` for `what is your name`).
2. **T1** the web alone against the bag: relevance (hypernym distance of emitted words from the hub) and order (connective relation licensed by a WordNet relation).
3. **T2** the `w_sem : w_ctx` sweep (1:1, 2:1, 3:1, 5:1, web only), every result kept.
4. **T3** a deliberately poisoned granular `.bin`, to exercise the sanitisation that was never exercised.
5. **T4** cost: ms, MB and µWh per reply, same harness as Phase 42.
6. **T5** the topic-space claim: is the hypernym structure self-similar enough (branching per level) to treat `reach` as a zoom?

### Pointers

Method menu, correspondence table (web part ↔ semantic object), traps and the reading order are in the primer §4–§7. Related pages: Phase 35 (the model and its saturation failure), 40 and 41 (the deformation battery), 42 (every-voice benchmark), `docs/context_flow_spec/`, `docs/wiki/Scaled-Kite-English-Thought-Center-Context.md`. Citation: Veritasium (2026), *Is spider web really stronger than steel?*, copy in `ContextPlease/claude/references/VAPMIPOrbweaver/` and `VAPMIP/docs/references/VAPMIPOrbweaver/`.

### Companion notebook

None yet. When the phase is built, add `specs/phase_43.py` and rebuild per `notebooks/tuning_the_engine/README.md`.
