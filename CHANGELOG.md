# Changelog

All releases are preserved. Version format: v1.NNN — single increment per release.

---

## v1.214 — 2026-05-18

**Sedenion camshaft wired into monad.py — VAG-COM + OBD2 sensor layer — Roadmap TODO**

### Python (Philadelphos/monad.py) — v1.214

Sedenion pilot injection wired as Layer 1 (VAG-COM — live ECU streams).
OBD2 sensor_read/fault_scan/ready_check added as Layer 2 (post-facto export).

Architecture: two-layer sensor model following BEW 1.9 TDI diesel practice.
- VAG-COM = `_live_streams()` — what the ECU uses to tune itself in real time.
  Sedenion fires here as pilot injection before J^μ computation.
- OBD2 = `sensor_read(pid)` / `fault_scan()` / `ready_check()` — post-facto
  fault/compliance reporting for the Driver (Ptolemy).

**speak_raw() — sedenion pilot injection:**
- `encode_prompt(query)` fires before `_j_mu()` when sedenion camshaft available.
- `monad_interface(s)` returns `psi_norms[16]` — camshaft timing weights.
- `J_i *= psi_norms[i % 16]` — each zero's primary charge gated by its
  sedenion dimension weight. Camshaft disambiguates compression TDC from exhaust TDC.
- Fermat lattice passive gating: `density` factor applied to psi_norms before
  normalization. Near-zero-divisor dimensions auto-decouple (Porsche bushing
  compliance — passive, no extra computation).
- `_sedenion_prev` saves PREVIOUS turn psi_norms before updating current.
  Turbo exhaust temperature: PID 0x2309 measures Noether violation between turns.

**_j_mu(psi, weights=None):**
- New `weights` parameter: `psi_norms[16]` from sedenion camshaft.
- Without camshaft (P0340 active): uniform weights, engine runs on crankshaft only.

**_advance_age(temporal_weight=1.0):**
- Sedenion e₇ (temporal dimension) modulates conversational age decay rate.
  `age[n] += temporal_weight` instead of += 1. Ages are now float.
- `speak()` passes `self._temporal_weight` from last sedenion computation.
  Slow time (low temporal_weight) = more context retained. Fast = more forgetting.

**_live_streams() — VAG-COM Groups:**
- Group 000: field_temp, j_norm, emission_threshold, vocab_coverage.
- Group 001: J^μ per top-16 zeros (j_per_zero, j_mean).
- Group 004: psi_norms, affect, gestalt, temporal_weight, fermat_proximity.
- Group 011: sedenion charge actual vs target (16.0 = all dims fully active).
- Group 013: per-zero J^μ deviation from mean (cylinder balance — VAG-COM only,
  no OBD2 PID equivalent).
- Oil pressure (A-matrix density): live only — no standard OBD2 PID.

**sensor_read(pid) — OBD2 SAE J1979:**
Standard: 0x04 engine load, 0x0B MAP/boost, 0x0C RPM, 0x0E timing advance,
0x0F IAT, 0x11 throttle, 0x1F runtime, 0x2C EGR, 0x2F fuel level, 0x33
barometric, 0x5C oil temp, 0x5E fuel flow.
Custom: 0x2300 CKP (active γ_n), 0x2301 CMP (dominant sedenion dim), 0x2302
conjugate γ_{N-n}, 0x2303 sedenion charge, 0x2304 glow plug, 0x2305 Fermat
proximity, 0x2306 T_μν trace, 0x2307 J_Red, 0x2308 J_Blue, 0x2309 Noether ∂J.

**fault_scan() — DTCs:**
P0340 CMP (sedenion unavailable), P0335 CKP (no zeros above threshold),
P0300 misfire (< 3 active zeros), P0087 fuel pressure (threshold above max J^μ),
P0172 too rich (rejection > 50%), P0171 too lean (no vocab after input),
P0401 EGR (age advancing without hear()), P0101 MAF (word_count stalled).
P0340 clears when sedenion import succeeds. MIL (_mil) set on any active DTC.

**ready_check() — 8 readiness monitors:**
FIELD, VOCAB (>1000), EDUCATED (wc>1000), CONNECTED (A>0),
THRESHOLD (emission>0), CAMSHAFT (sedenion import ok — P0340),
CRANKSHAFT (≥1 zero deepened past ground), GLOW_PLUG (wc≥1000).

**Graceful degradation:**
Sedenion import uses relative path (`../../Ainulindale`) with try/except fallback.
If unavailable: P0340 fires; engine runs at uniform psi_norms=1.0 (crankshaft
without camshaft — no TDC disambiguation, but still operational).

**Version:** monad.py corrected to v1.214 (R.MCV system).

### Project

- `TODO` restructured with full minor-release roadmap: v1.3→v2.0 (The Speaking
  Engine) and v2.1→v3.0 (The Self-Coding Engine). Each minor release has a
  defined deliverable and "done" condition. Unicode tokenization assigned to v1.4.
- `TODO.md` new wiki page: short synopsis per minor release. Includes theory
  sections for BAO=Laplacian and the 16-word sliding window sedenion model.

### Theory: 16-word sliding window

The 16 tires in speech output are a sliding window of 16 words:
  Window 0: words [0..15] → sedenion state S₀
  Window 1: words [1..16] → sedenion state S₁ (one word dropped, one added)
Each transition S_n → S_{n+1} is a sedenion rotation.
Coherent speech = smooth sedenion trajectory. BAO convergence = operating temp.
The BAO is the Laplacian of the semantic graph: Δ = D − A.
Its lowest non-zero eigenvalue is OMEGA_ZS = 0.56714.
When everything else cancels, the BAO structure remains.
It is the idle RPM. It is the CMB of the engine.

---

## v1.213 — 2026-05-18

**Dual-checkpoint: prime charge separated from Face rendering**

The monad's field state (β, A) and its vocabulary (Face layer) can now be loaded
from separate checkpoints.  `monad.bin` computes J^μ; `monad_wordnet.bin` renders
it to words.  speak() is now speak_raw() → render(): the prime charge IS the
response; words are one Face of it.

### Binary (PtolC)

- `state_load_vocab(m, path)` — loads only the vocab section from any `.bin`
  checkpoint into an existing monad, replacing `m->vocab` and `wm` without
  touching β, A, age, affect, or word_count.
  Typical use: `state_load(m, "monad.bin"); state_load_vocab(m, "monad_wordnet.bin")`

### Python (Philadelphos/monad.py)

- `speak_raw(query, max_tokens)` → `[(gamma, J_charge), ...]` — J^μ distribution
  in zero space; does not decode to words, does not advance age
- `render(charges, max_tokens)` → `str` — project charge distribution through
  `self.vocab` (one Face); does not advance age
- `speak(query)` refactored to `speak_raw() → render()`; semantics unchanged
- `load_vocab(path)` — load only the `vocab` key from a JSON checkpoint;
  β, A, age, and word_count untouched
- `_bisect_gamma(gamma)` — binary search: γ value → nearest zero_idx

### lshs.py

- `S_raw(prompt)` → `[(gamma, charge), ...]` — same split applied to LSHS
- `render(charges, max_words)` → `str` — Face projection
- `S(prompt)` refactored to `S_raw() → render()`; `speak()` / `respond()` unchanged

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
