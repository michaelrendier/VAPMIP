# 04 — Learn and speak

**Job.** The engine's two verbs, as they run now. The ASCII-era mechanism, function by function, is `SemPriCon/paper/The_Golden_Ratio_Monad.pdf` (§4–§13); the Unicode build changes only what is listed under *Changed*.

## Learn (`monad_learn_ex`)
Split into sentences; tokenise ([02](02_the_tokenizer.md)); for each accepted token: address ([01](01_the_address.md)), `β ← min(β + E² · 0.01 · |sin γ| · π/2, 7.552)`, the slot displays the highest-`E` arrival, `prose_seen` set per slot; then for every pair within 12 accepted tokens `w = Eᵢ Eⱼ · couple / ((|γᵢ − γⱼ| + 0.000707) · d)` (`couple` 2 if same Dirac pole, else 1; `d` = distance in tokens) added to A.

## Speak (`monad_speak`, `-W` = `monad_speak_wick`)
Seed `J` from the prompt's slots (`β E² e^{−0.05 age}`) → spread to ±3 slots → two passes along A → length `4 + int(50 · ΣT/(ΣT+ΣV))` → pointer (median γ of the prompt) → golden-angle walk (step 9549) from the pointer, first word chosen by nearest `E` to `(ΣV/(ΣV+ΣT)) Ω` → `near_canonical` surface → separators by `J/J_max`.

## Changed in the Unicode build (state version 5)
- tokenizer, address, sentence ends, vowel gate: pages 01–02;
- `surface_canonical` (the surface translation layer): length counted in code points, ≥ 1 for Han and ≥ 3 otherwise, vowel rule for Latin script only;
- `STATE_VERSION 5`; older stores refused.

## Not changed (and therefore still true)
The zeros are Newton approximations; reply length is ≈ 4 for short prompts; β saturates at 7.552; `MONAD_TAU`, `MONAD_WINDOW_MIN`, `MONAD_EMIT_THRESH` are unused; the stored `emission_threshold` is never read. Each is measured in the paper's §17.

**Check:** `python3 SemPriCon/tools/verify_unicode_against_c.py` and `verify_learn_against_c.py`.


## State version 6
Fresh Start v2.0 raised the state version to 6: the address is Horner over the language's alphabet (see [09](09_the_test_bins.md)), and a store is refused by any build whose state version differs. The file layout is the same as v5.
