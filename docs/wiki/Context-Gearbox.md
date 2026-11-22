# The Cyclic Context Gearbox

*2026-11-21. Code: `context_gearbox.py`; tests: `tests/test_context_gearbox.py` (7). Licence: proprietary, all rights reserved.*

The `.clauderc` files are a block and tackle: context 1 cycles into context 2, then on, each wheel holding the same information at a different compactness. The gearbox is that mechanism as an engine object, used twice: **DATA SELF** (what happens to Ptolemy: inputs, his sayings, faults, vocabulary changes) and **USER SELF** (how the user responds to that), in one language.

* **Odometer, FIFO.** `Gearbox(name, gears=[(cap, ratio), ...])`. Gear 0 holds raw events. When it holds more than `cap`, its oldest `ratio` events become ONE record of gear 1; gear 1 overflows into gear 2; and so on. A gear shift is a change of compactness, never a deletion. Tunable per box.
* **Lossless.** A compacted record carries a readable **digest** (count, span, kinds, top terms, mean tone: the shortcut), the whole block zlib-compressed, and its sha-256. `reconstruct(record)` expands back to the original raw events (hash-checked; a tampered block raises), recursively through the gears. Measured in the tests: 400 events, storage ratio above 1.5, every original event returned exactly.
* **Ledger.** An optional append-only JSONL holds the raw events; replaying it rebuilds the same gears (tested).
* **Threads.** Events carry a global `seq`, a `thread` (the seq of the first event of the train of thought) and `responds_to`. `reaction_to(seq)` returns how the user reacted to a Ptolemy event, wherever it now sits; `thread(seq)` returns the whole train of thought from its first event across both boxes, after any amount of compaction (tested over 60 further exchanges).
* **Shortcuts.** `shortcuts()` / `export_lines()` give canonical environment variables (`CTX_DATA_G0`, `CTX_USER_G2`, …), the `.clauderc` way of pulling a context block by name.

Used by `SedenionWindow(selfctx=...)`: every prompt is a USER SELF event (with the heard tone and the inferred level), every sentence a DATA SELF event that responds to it; later user reactions attach to the sentence they answer.

Not built: absurdity. The boxes keep contradictory and stubborn user input exactly as given and never "correct" it; nothing yet reads those patterns (for example a user who holds one position through every reply) to adjust behaviour.
