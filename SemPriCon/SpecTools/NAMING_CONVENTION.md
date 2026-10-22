# NAMING CONVENTION — bins, speakers, assessments, mappings

Recorded 2026-10-22 from Cody's specification (SemPriCon control grouping). The version number in a file name points directly at the files used in that experiment battery.

## Grammar
`{L}` = a language token: lowercase full English name (`english`, `chinese`). `chinese` = the frozen Traditional Mandarin baseline. `{M}` = mapped language (the language whose address shape is walked). `{A}` = assigned language (the language whose words are slotted into `{M}`'s slots). `{S}` = spoken language (the language of the reply). `{V}` = integer experiment-battery number. **No `.0`**: `v3`, never `v3.0`.

| thing | pattern | example | meaning |
|---|---|---|---|
| single-language bin | `test_{L}_v{V}.bin` | `test_english_v3.bin` | language `{L}` mapped by its UNS mechanism; spoken = mapped |
| assignment bin | `test_{M}_{A}_v{V}.bin` | `test_chinese_english_v3.bin` | ideas mapped in `{M}`, `{A}` words assigned to those slots |
| single-language speaker | `TestMonad_{S}_v{V}.py` | `TestMonad_chinese_v3.py`, `TestMonad_english_v3.py` | the speaking mechanism for one language; reads `test_{S}_v{V}.bin` |
| assignment speaker | `TestMonad_{M}_{S}_v{V}.py` | `TestMonad_chinese_english_v3.py` | runs the prime-selection-for-speaking along the shape of `{M}` idea space and returns the `{A}`=`{S}` words slotted there; reads `test_{M}_{S}_v{V}.bin` |
| assessment | `{kind}_v{V}.json`, `{kind}_v{V}_prose.{json,md}` | `chinese_english_v3.json` | `{kind}` = the bin name without `test_` and `_v{V}.bin` |
| frozen list | `calibration_v{V}_{lang pair}.tsv` | `calibration_v3_en_zh.tsv` | the word list the battery was built from |

Order rule: mapped first, assigned/spoken second, always. Reverse experiments are their own files: `test_english_chinese_v{V}.bin` + `TestMonad_english_chinese_v{V}.py` (English idea shape, Chinese words returned). A speaker of version `V` reads only bins of version `V`.

## Constraints (N1–N6)
- **N1** Every `test_*` bin from v3 on is built only by the UNS mapping algorithms (M3 English, M4 Chinese). The mapping version rides in the battery number.
- **N2** The two single-language speakers are separate mechanisms on purpose (English and Chinese differ structurally); they are kept side by side to observe their functionality, not merged.
- **N3** The assignment speaker is the translator indicator: mapping then assigning, then speaking only works as translation if the mapping-plus-assignment is working at least a little. It is an observation instrument, not a success target; failures and error codes are data.
- **N4** Experiment speakers live next to the experiment data (`clean/`, beside the bins of their version). Reusable machinery (`monad_pyu.py`, `uns_mech.py`, …) stays in `tools/`. Mapping algorithms are being centralised in `mappings/{UNS,Flat}/`.
- **N5** Nothing is deleted: a superseded file moves to `archive/v{V}/` (existing: `clean/archive/v1.0`, `v2.0`) and its old name stays unchanged there.
- **N6** Edits to any TestMonad are documented in the SemPriCon wiki: additions go in, removals are deprecated and left.

## Experiment defaults (Cody, 2026-10-22)
- The assignment speaker normally speaks English (`{S}` = english, `{M}` = chinese), and the reverse (`TestMonad_english_chinese`) is wanted too. The experiments serve Cody's English understanding of whether the mechanism is correct; a fluent Chinese speaker is expected later.
- "TestMonad always speaks English" (2026-10-21) is amended: it is the default for the assignment experiments only. It rests on his assumption that Chinese is a good approximation of Idea Space (semantic neighbourhood) without further adjustment. That assumption is the thing under test; per requirement T1 the term "semantic neighbourhood" is not used for a result unless the data behind it is semantic.

## Where things stand (2026-10-22)
- Renamed `*_v3.0*` → `*_v3*`: three bins, nine assessment files, and every reference to them in `clean/MANIFEST.tsv`, `data/v3_build_summary.json`, `tools/v3_build.py`, `v3_speak.py`, `v3_pdf.py`, `SpecTools/README.md`, `SemPriCon_requ_conf.md` and wiki page 17. Bin sha256 unchanged and matches the manifest.
- No `TestMonad_*_v3.py` file exists yet. `tools/v3_speak.py` (driving `monad_pyu.MonadU`) is the stand-in speaker. Nothing is built until Cody says go.
- Older names stay as they were (`test_*_v1.0.bin`, `test_*_v2.0.bin`, `test_*_v2.bin`): archived, deprecated and left.
- `mappings/UNS/` and `mappings/Flat/` exist as empty homes (see `mappings/README.md`); the code has not moved.
- A script of version `V` named without a dot is also importable as a Python module (`import TestMonad_english_v3`), which `v3.0` was not.
