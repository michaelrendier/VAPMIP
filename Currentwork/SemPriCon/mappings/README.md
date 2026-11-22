# mappings/ — the mapping algorithms, centralised

A mapping is the function that turns a surface form (word, character) into an address (slot, energy). Every bin is built by exactly one mapping per language, and the **UNS** mappings are the only ones allowed to build `test_*` bins from v3 on (NAMING_CONVENTION.md, rule N1).

| directory | holds |
|---|---|
| `UNS/` | Universal Native Space mappings — M3 English (golden-angle turns on the π/2 equator), M4 Chinese (dictionary-order turn, key-component radius, exact zeros). Currently implemented in `../tools/uns_mech.py` (`en_uns`, `zh_uns`) |
| `Flat/` | flat-line mappings — M1 English → ½ line (eb28ce8 as it ran, `../tools/monad_py.py`), M2 Chinese → ½ line (`../tools/zh_half_line.py`). Kept as the control grouping |

Status 2026-10-22: the directories exist; the code has NOT been moved (`v3_build.py`, `v3_speak.py` import `tools/uns_mech.py`). Moving it is a separate step that needs its imports updated and re-verified (`uns_mech.py --selftest`, bin sha256 in `clean/MANIFEST.tsv`). Until then, put a pointer file here for each mapping, not a copy.
