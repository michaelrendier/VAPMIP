# Name Table

*One table of names: symbols, constants, the working tools, the trees, the repositories. Rebuilt 2026-11-21. The May 2026 experiment that used to stand here (the ten identity queries) is `Identity-Query-Table-2026-05-19.md`.*

Names are used exactly as written. In code and papers use the code's own identifiers.

## Symbols (author's standing ruling, `@RCCM_SYMBOLS`)

| name | is | value |
|---|---|---|
| α | fine-structure constant | 1/137.036 |
| A_π (A_pi, Alpha_Fermat) | Lambert W fixed point W(1); Fermat side: speed of causality, inertia | 0.5671432904 |
| Ω_ζΣ (Omega_sum_zeta, Ω_RZ) | d*; Riemann side: Hagedorn information ceiling, entropy | 0.2463072015 |
| d*·ln 10 | the Translator; equals A_π | 0.5671432904 |

Code names that disagree with the table: `OMEGA_ZS` (the value is A_π), `D_STAR` = 0.24600 (rounded d*, d*_spec). The table decides.

## The four faces of d*

| name | symbol | status |
|---|---|---|
| The Boundary | d* = Ω_ζΣ | 0.2463072015 |
| The Stability | d*_RG | dimension 8; numeric, no closed form |
| The Flow | d*_taut = Ω/ln 10 | tautology; never hard-coded |
| The Translator | d*_ln(10) = d*·ln 10 | = A_π |

Source: `@RCCM_FOUR_DSTAR`, `Ainulindale/wiki/17`, `FourthAgePapers/DStar/paper/dstar_paper.md`.

## Constants in the code

| identifier | value | read as |
|---|---|---|
| `OMEGA_ZS` | 0.56714 | A_π |
| `D_STAR` | 0.24600 | d*_spec |
| `GAP` | 0.000707 | A_π − d*_spec·ln 10 (rounding residual) |
| `MONAD_PHI` | 1.618034 | golden ratio; word hash base |
| `MONAD_N_DEFAULT` | 25000 | Riemann zeros in the field |

## The working tools (2026-11)

| name | file | what |
|---|---|---|
| scalar boxkite | `19D_rotary_boxkite_monad.py` | discrete static kite: 7 ordered pairs, pencil, string, flashlight, tension law |
| scaled boxkite (Mind's-Eye kite) | `scaled_mind_eye_boxkite_kernel_monad.py` | the kite in motion; context relations, struts |
| orbweaver | `boxkite_orbweaver_monad.py` (`OrbWeaverMonad.weave`) | semantic web; seven names `ANCHOR SPAN SCAFFOLD ELABORATE HOOK WRAP SHELL` |
| WordNet relation hash | `wordnet_boxkite.py` | the 19 relation pointers per word |
| Zork parser | `zork_parser.py`, `PtolC/zork.c` | verb-governed selection of 16 operators |
| prime hash | `prime_hash.py` | words land on primes |
| add_scale_sign | `add_scale_sign.py` (`ASS`, `ASSWord`) | engine name locked |
| SemPriCon | `SemPriCon/` | prime-concept baseline, Chinese first |

## The trees

| directory | branch | holds |
|---|---|---|
| `Broca/` | `boxkite` | scalar and scaled boxkite: the structure side (copies) |
| `Wernicke/` | `orbweaver` | the semantic orbweaver: the meaning side (copies) |

Never write "the two trees" for these two; use the directory names.

## Official names (`~/.clauderc_official_names`)

The Boundary, The Stability, The Flow, The Translator (above) · The Vector · The Origin · The Iterator · The Recursion Factor · The Anchor (fulcrum : pivot : anchor) · The Contractor / The Dilator · The Boxkite · The Waveform (The Standing Wave) · The Tilt / The Axis / The Twist. Definitions and where each emerges: `~/.clauderc_official_names`.

## Repositories

| repository | what |
|---|---|
| VAPMIP (PtolemyHolcus) | the engine; proprietary |
| ValaQuenta | the toolkit and the engine-name `constants.py`; GPL-3.0-only; authoritative over Ainulindale |
| Ainulindale | the Ĥ_RB derivation and wiki |
| PtolemyDesktop | desktop application, the Faces, PtolBus |
| POE | pendant hardware; proprietary |
| FourthAgePapers | the papers and their engines (`DStar/`, `EquationSpace/`, …) |
| SedenionSpectralRelativity | sedenion input/output of Ĥ_RB, hyperindexing, address systems |
| TuringStack | crypto collections (`BSD_Crypto/`) |
| ContextPlease | the `.clauderc*` files and context archive |
