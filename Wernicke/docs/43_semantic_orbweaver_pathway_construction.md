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

### Cody's answers, 2026-10-17

1. **The original semantic prime hash is H2**, the golden-ratio seed (`monad_word_coords`, `PtolC/monad.c`). H1 (Horner → prime) and H3 (WordNet prime codes) are not it.
2. **Engineering mode:** every test is acceptable if it finds the lowest-overhead happy spot. Code golf comes later, once a working model exists. So T4 (cost) is measured on every rung, not only at the end.
3. **The phonetic field is morphology.** It is to supply the conjugation (CONNECTION) part of the equation, eventually.

### Historic checkpoints (T0 material), found 2026-10-17

Format of the May bins: `PTOL` magic, then `<5I` = version, N, vocab, A-edges, word_count. Checked from the headers, not from the filenames.

**The store behind the May screenshots 2 and 3** (`vocab=24485 A=6825748 wc=121914388`) is the header of `monad_wordnet_v4_20260519.bin` (PTOL v4, 110,040,527 B). It was in `~/.ptolemy/clean/` and, as a byte-identical copy (md5 `4213c678…`), in `~/.ptolemy/dirty/monad_wordnet.bin`. **It is not in PTorrent's `bin_archive/`:** the `monad_wordnet.bin` there (v2, 23895 / 9600426 / 34494302) is the polluted v1.111 state, a different file.

Copied (local only, `*.bin` is gitignored) into `VAPMIP/checkpoints/clean/`:

| file | header (ver, N, vocab, A, wc) | sha256 (first 16) | role |
|---|---|---|---|
| `monad_wordnet_v4_20260519.bin` | 4, 25000, 24485, 6825748, 121914388 | `66f70c70dcd8d860` | **T0**: the store that said "holcussamestuffseemy" |
| `monad_English_v2_baseline.bin` | 2, 25000, 14164, 766027, 1608903 | `06e82b9f914179ac` | pure-WordNet ground-state control (3.6 % pollution) |

Caveats to settle by measurement:

- `~/.ptolemy/dirty/monad_wordnet.bin.assessment.json` (2026-05-17, wc 44,782,621, 5.04 % polluted) describes an earlier state of the same filename; the file on disk was overwritten by the 05-19 state (wc 121.9 M). Its pollution is therefore **unassessed**: run `tools/eval_checkpoint.py` before trusting the "clean" label.
- The May bins use the golden-ratio hash over N = 25,000 zeros; the current store (`monad3_c.bin`, 347k words) does not. T0 on the May bin and T0 on today's store are two separate results.

Other candidates located, not copied (all gitignored, local):

| path | header / note |
|---|---|
| `~/.ptolemy/dirty/monad_wordnet_v2_polluted_v1111.bin` = `PTorrent/bin_archive/dirty/{monad_wordnet,holcus_monad_wordnet,phone_20260601_monad_wordnet}.bin` (md5 `372a111e…`) | v2, 23895 / 9600426 / 34494302; POLLUTED (PDF-OCR consonant clusters) |
| `~/.ptolemy/dirty/monad_wordnet.polluted.bin` | v2, 23992 / 9739507 / 37971608 |
| `~/.ptolemy/dirty/monad_wordnet_20260516_*_pre_vowelfix.bin` (3 files) | v2, 25000 / 10805498 / 60618542, 35.6 % polluted |
| `~/.ptolemy/archive/monad_wordnet_polluted_20260516.bin` | v1, 25000 / 10797279 / 257482236 |
| `PTorrent/bin_archive/clean/monad_englishwordnet.bin` | v3, 164283 words, 2463413 edges, word_count 0 (geometric init, no corpus) |
| `PTorrent/bin_archive/clean/*english*`, `monad_*.bin` | v1.218 pickles (not `PTOL`), phone and holcus copies |
| `~/.ptolemy/clean/monad_english_ptol_20260526.ptol` | Gutenberg 22-book canon, pickle |

### Companion notebook

None yet. When the phase is built, add `specs/phase_43.py` and rebuild per `notebooks/tuning_the_engine/README.md`.
