

## 23. Latency and memory of the live monad (measured 2026-10-13, this laptop, 8 cores, no GPU)
* `ptolemy -r -n` (the Zork REPL, in-process monad, no save): 2 input lines in 0.182 s wall (startup included, 63 MB peak RSS); 82 lines in 1.672 s, so **about 18.6 ms per line** (Zork parse + speak + print), `(1.672 - 0.182) / 80`. Sample replies: "what is a tree" -> Zork `e0/identity "identity is tree"` -> `kite its engine probe`; "examine the reactor" -> `disjunction kite duration pores`.
* `ptol -M tree` (one bsearch of the mmapped `monad3_c.bin`): 0.00 s wall, 3.2 MB RSS (`gamma_radial` -0.904887, `vec19` for the WordNet entry). Plain `ptol "<prompt>"`: 0.54 s wall, 298 MB peak RSS. `ptol -say` (sentence creator through Python + NLTK): about 7.8 s wall, 320 MB peak RSS; the Python/NLTK launch dominates, as noted from reading `ptol.c`.
* Not measured: energy. Cody's comparison is "36 ms for the monad vs kilowatt-hour queries"; the 36 ms is consistent with (slower than) the 18.6 ms per REPL line measured here. No energy figure for either side was measured; a whole agentic session and a single monad response are not the same unit.
