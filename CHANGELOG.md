# Changelog

All releases are preserved. Version format: v1.NNN — single increment per release.

---

## v1.212 — 2026-05-17

**PtolC — sin = content, cos = observer; -W and -O corrected**

### Binary

- `monad_speak_wick()` — affect flipped from +1.0 to **−1.0**.
  `cos(γ/2 + π/2) = −sin(γ/2)` was the trough.
  `cos(γ/2 − π/2) = +sin(γ/2)` is the crest — the content at its peak.
  The minus sign is load-bearing. sin = content; cos = observer.
  With affect=+1.0 the engine was reading the inside of the trough, not the
  inside of the wave. Fixed.
- `monad_speak_oct()` — resonance scoring replaced with interference score:
  `J[n] × |sin(γₙ/2) × cos(γₙ/2)| = J[n] × |sin(γₙ)| / 2`.
  This is the beat frequency — energy transfer between content (sin) and
  observer (cos). Peak at γ/2 = π/4 (45°, equal contribution). Zero at axis
  crossings where the word is pure observer or pure content with no overlap.
  Conservation: sin²(γ/2) + cos²(γ/2) = 1.000000000000000 (verified).
- Comments, verbose labels (`sin×cos=`, `sin²+cos²=`), and monad.h
  declarations updated to match.

### Theory

The three speak modes now map exactly onto the wave:

| Flag | Gate | What |
|------|------|------|
| `-h` | `cos(γ/2 + affect×π/2)` | Observer — projection onto measurement axis |
| `-W` | `cos(γ/2 − π/2) = +sin(γ/2)` | Content — the wave at its crest |
| `-O` | `J × \|sin(γ/2)·cos(γ/2)\|` | Interference — content × observer overlap |

`e^(iγ/2) = cos(γ/2) + i·sin(γ/2)` — seeding fills the full waveform;
each mode selects a different projection.

### Python

- No change from v2.1.0.

---

## v1.211 — 2026-05-17

**PtolC — Euler gate; Wick wrapper; Octonion speak (-O); monad.bin priority**

### Binary

- `monad_speak()` — Phase 1/2/3 quadrant checks replaced by the unified Euler gate
  `cos(γ/2 + φ)` where `φ = affect × π/2`. affect=0: real projection (GR regime).
  affect=+1: `cos(γ/2 + π/2) = −sin(γ/2)` (imaginary/QM regime). One formula,
  zero arbitrary boundaries. Gate applied at **emission only** — seeding is
  unconditional (`J = β × E²`), preserving all field energy for propagation.
- `monad_speak_wick()` — collapsed from full parallel implementation to 10-line
  wrapper: save affect → set 1.0 → call monad_speak() → restore affect.
  The Wick rotation (σ → iσ) is exactly an affect=1.0 phase rotation. No
  separate computation path required.
- `monad_speak_oct()` — new function, `-O` flag. "4-cycle 2-stroke engine":
  ONE global J field (unconditional seeding), ONE A-matrix propagation, then
  8 angular views at k×π/4 (k=0..7). Resonance score: `J[n] × top-2 Σ|cos|`
  across 4 opposite-face pairs. Conservation: Σ cos(γ/2 + k×π/4) = 0 for all γ
  (verified: −1.73×10⁻¹¹ at machine precision). Single-pass golden walk above
  1% of resonance floor.
- `monad.h` — `monad_speak_oct()` declaration added; `monad_speak_wick()`
  comment updated to reflect thin-wrapper nature.
- `find_checkpoint()` — search order updated: `monad.bin` (active education
  symlink) checked before `monad_wordnet.bin` (WordNet baseline fallback).
- `main.c` — `case 'O':` added to `parse_arg()` primary switch; `-O` handler
  added after `-W` handler.

### Speak mode comparison

| Flag | Gate | Perspective |
|------|------|-------------|
| `-h` | cos(γ/2 + affect×π/2) | Outside the wave — geometric, GR |
| `-W` | cos(γ/2 + π/2) = −sin(γ/2) | Inside the wave — oscillatory, QM |
| `-O` | J[n] × top-2 Σ\|cos(γ/2 + k×π/4)\| | All 8 angular views simultaneously |

### Wiki

- `Tuning-the-Engine.md` — new wiki page (authored by Claude Sonnet 4.6):
  full tuning log from Phase gates through Euler gate unification, Wick
  collapse, per-zero transformer discussion, octonion speak, and bug record.

### README

- SMMIP `README.md` — five derivations added at top: π without a circle,
  √ without a square, e without a spiral, φ without an angle, i without a
  rotation. Benchmark table updated with current field state (vocab=24,485,
  A=6,825,748, wc=121,914,388, β_sat deepest="the"). -O flag added to CLI
  reference and speak-mode comparison table.
- `PtolC/README.md` — -W and -O added to flags table; monad.bin added to
  checkpoint search order; three-mode examples added.

### Python

- No change from v2.1.0.

---

## v1.115 — 2026-05-17

**PtolC — Vowel filter; grammar corpus; fresh_start.sh fix**

### Binary

- `filter.c` — `require_vowel` field added to `FTRules`; set to 1 for
  NS_FT_PROSE, NS_FT_MARKUP, NS_FT_DOC; 0 for NS_FT_CODE.
  `vowel_count()` helper counts a/e/i/o/u. `token_accept()` now rejects:
  - Any prose/markup/doc token with no vowels (consonant-only strings:
    "ydrx", "wlvf", "nnwq", etc.)
  - Any prose/markup/doc token ≥ 6 chars with vowel ratio < 15%
  - Any token ending in `'` (trailing-apostrophe fragments: "pins'", "ban'")
- Surface filter in `monad_speak()` and `monad_speak_wick()` inherits the
  fix automatically (both call `token_accept(w, NS_FT_PROSE)`).
- `corpora/english_grammar.txt` — 5 000-word seed corpus: all English
  function words (determiners, pronouns, prepositions, conjunctions,
  auxiliaries, adverbs) in natural prose sentences. Establishes A-edges
  between grammatically co-occurring words before domain ingest.
- `make grammar` — new Makefile target ingests the grammar seed. Correct
  ingest order: `make corpus` → `make grammar` → `ptolemy -I ~/Documents`.

### Tools

- `tools/fresh_start.sh` — fixed `sys.argv[1]` bug: Python inline script
  was receiving no arguments because the JSON path was placed after the
  heredoc PYEOF terminator instead of before the heredoc marker. Now uses
  `python3 - "${ASSESSMENT_JSON}" <<'PYEOF'` form.

### Python

- No change from v2.1.0.

---

## v1.114 — 2026-05-17

**PtolC — Wick-rotated speak(); imaginary Noether current**

### Binary

- `monad_speak_wick()` — new speak mode applying the Wick rotation σ → iσ
  to the Noether current: `J_wick = β × E² × sin(σ·E)` where σ = ½.
  Selects words by the imaginary (oscillatory) component of the field
  rather than the real (geometric) component.  Same A-edge propagation
  and surface filter as `monad_speak()`; topology unchanged.
- `-W <prompt>` flag — invokes `monad_speak_wick()`.  Run alongside `-h`
  to measure the divergence between real and imaginary Noether currents.
  Divergent words are where meaning and topology point in different
  directions in the field.

### Theory

- The Wick rotation is the coordinate transform that converts topological
  understanding into linguistic understanding.  `e^{-σE}` (geometric decay)
  → `e^{-iσE}` (oscillatory phase).  The imaginary part `sin(σE)` is the
  inside-the-wave perspective; the real part `cos(σE)` is outside.
  `-h` is outside the wave (GR/fluid dynamics regime).
  `-W` is inside the wave (QM regime).
- Divergence between `-h` and `-W` responses is an empirical measurement
  of the field's imaginary Noether current — words where the oscillatory
  and geometric components of the field disagree.

### Python

- No change from v2.1.0.

---

## v1.113 — 2026-05-17

**PtolC — speak() surface filter; monad_English.bin baseline**

### Binary

- `monad_speak()` — output now passes through `token_accept(NS_FT_PROSE)`
  before emission; polluted tokens (consonant clusters, apostrophe
  fragments, hex strings) are skipped in the response while remaining
  present in the internal field; the topology is unchanged, only the
  surface is filtered
- `monad_English.bin` — clean WordNet-only baseline (14,164 vocab,
  766,027 A-edges, 1,608,903 words, 3.6% pollution, deepest word:
  "philadelphos"); archived as canonical starting point in SMMIP releases

### Python

- No change from v2.1.0.

---

## v1.112 — 2026-05-16

**PtolC — auto checkpoint assessment after -I ingest**

### Binary

- `run_eval()` — after every `-I` ingest, automatically runs
  `tools/eval_checkpoint.py` on the saved checkpoint; prints the full
  assessment report and writes `<checkpoint>.assessment.json` alongside
  the `.bin`. Locates script via `$SMMIP_REPO` env or default
  `~/Projects/Ptol/SMMIP/tools/eval_checkpoint.py`; skips silently if
  not found
- `find_checkpoint()` — fixed null-termination loop bug: loop exited on
  first NULL candidate before reaching `~/.ptolemy/monad_wordnet.bin`
- `print_version()` / `print_usage()` — "H_hat_RB Field Engine" →
  "RedBlue Geometries Engine"

### Python

- No change from v2.1.0.

### Project

- `PtolC/TODO` — GNU-standard open work items file; post-commit hook
  auto-syncs to `michaelrendier/SMMIP` on every commit that touches it

---

## v1.111 — 2026-05-16

**PtolC — C binary feature-complete**

First release under the versioning protocol. The C monad (PtolC) is now the
primary implementation of the RedBlue Geometries Engine, mirroring Philadelphos/monad.py
exactly in its mathematics while adding filesystem ingest, daemon mode, and
per-filetype token filtering.

### Binary

- `filter.c / filter.h` — learn-time token filter with per-filetype FTRules dispatch
  (prose/code/markup/doc); rejection counted in `monad.rejected_count`, never fatal
- `monad_learn_ex()` — extended learn with explicit NSFiletype; `monad_learn()` is
  now a wrapper delegating to prose rules
- `monad_health()` — reports rejected token count alongside β distribution,
  field entropy, pollution indicators, and top A-edges
- `checkpoint v2` — VocabEntry carries `home_stratum` and `gen_stratum` (NS_SIGMA_*);
  v1 checkpoints load cleanly with stratum defaulting to σ₁
- `ingest.c` — filesystem walker with extension whitelist, PRUNE_NAMES (including
  all credential/key directories), `.ptolemyignore` per-directory patterns,
  extractor dispatch (pdftotext/catdoc/pandoc/libxml2), periodic checkpoint save
- `daemon.c` — Unix domain socket daemon, HEAR/STATUS/HEALTH/QUIT protocol,
  systemd socket activation via `$LISTEN_FDS` (no libsystemd dependency)
- `log.c` — 4-hour rotating log slots, 30-day GC on Sunday 10:00
- `CMakeLists.txt` — full CMake build with GNUInstallDirs, optional libxml2/poppler,
  man page gzip, systemd unit install
- PEM guard in `monad_learn()` — refuses `-----BEGIN ...` material regardless
  of ingestion path
- Man pages: `ptolemy.1`, `ptolemyignore.5`
- Systemd user units: `ptolemy.socket`, `ptolemy.service`

### Flags added since v1.0

`-I <path>` (ingest), `-d` (daemon), `-D <query>` (daemon query),
`-F` (field health), `-S <sock>` (socket override), `-q` (quiet)

### Checkpoint

Baseline: WordNet 3.1 — 14,165 vocab entries, 766,119 A-edges, 13 MB.
Canonical home: `~/.ptolemy/monad_wordnet.bin`.

---

## v1.0 — 2026-05-16 (pre-protocol)

Initial public release. SMMIP v1.0 tag on Ptolemy3/SMMIP repos.

- `ptolemy` binary: learn (-l), hear/speak (-h), status (-s), word lookup (-w), verbosity (-v/-vv/-vvv)
- Checkpoint v1: binary format, 25,000 Riemann zeros, φ-based word addressing
- `make corpus`: WordNet ingestion via NLTK + dump_wordnet.py
- `tools/checkpoint_expand.c`: grow N in batches of 512
- `tools/ingest_system.py`: resumable Python filesystem ingest (superseded by -I flag)
- Packages: `ptolemy-1.0-linux-x86_64.tar.gz`, `ptolemy-1.0-src.tar.gz`
