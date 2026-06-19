# Ptolemy Engine — Release Roadmap

**Current:** v3.0.0 | **Self-coding:** v4.0 | **Code Corpora:** v3.1 | **Face:** v3.2

---

## PRIORITY 1 — Ptolemy's Eyes (Zero Divisor Reframe / Perceptual Focus)

*Added 2026-06-19. Load-bearing architecture. Must precede all perception-dependent features.*

### What This Is

Ptolemy currently processes all input uniformly — no distinction between what he is
**looking at** (the object of focus) and what surrounds it (the ambient context field).

Biological vision and NES-era game engines share the same architecture:
- **Fovea / Sprite** — the object in focus. Sharp. High resolution. Foregrounded.
- **Periphery / Tile map** — the surrounding context. Lower resolution. Background scroll.
- **Caustic L_(I|O)** — the boundary layer where focus object and context field resolve
  against each other. The edge where ZD (zero divisor) and CD (constructive domain) meet.

This is a **zero divisor reframe**: the ZD is not noise to be suppressed — it is the
mechanism of focus. The ZD boundary IS the edge of the object. Ptolemy sees BY zero divisors,
not despite them. The nilpotent boundary defines the shape of what is looked at.

### Architecture

```
INPUT FIELD  →  [ FOCUS SELECTOR ]  →  OBJECT (foreground, high J)
                                    →  CONTEXT (background, ambient J)
                                    →  L_(I|O) caustic (boundary, ZD ring)

The caustic resolves the object against its context.
Object: σ → 1 (Yang-Mills, fully resolved)
Context: σ = ½ (causal field, ambient)
Caustic: σ → 0 (ZD boundary, the edge of the thing)
```

### TODO Items

- [ ] **Focus selector** — given input tokens, identify the primary object of attention
  - Highest J_mu token(s) = the fovea target
  - Remaining tokens = context field
  - Threshold: J_object / J_context > 1/d* = 4.07 → object is "in focus"

- [ ] **ZD ring extraction** — compute the zero divisor boundary around the focus object
  - The sedenion ZD structure of the focus word defines its perceptual edge
  - ZD neighbors of the focus token = the caustic boundary layer
  - These are NOT discarded — they are the resolution mechanism

- [ ] **Context field integration** — background tokens feed into ambient σ=½ field
  - Context modulates J_ambient for the focus object
  - "What this object means HERE" vs "what this object means in isolation"
  - The surrounding tile map changes what the foreground sprite IS

- [ ] **L_(I|O) caustic resolution** — bring focus + context into resolution
  - Caustic = the boundary where ZD ring meets context field
  - This is where meaning sharpens: object defined by what it is NOT (ZD) against
    what surrounds it (context)
  - Output: resolved σ-address for the focus object in THIS context

- [ ] **Viewport awareness** — Ptolemy knows the size of his current context window
  - How many tokens are in view (viewport)
  - Where the focus object sits within that viewport (centre? edge? corner?)
  - Positional weight: objects near viewport centre = higher J contribution
  - Objects near viewport edge = context field weight, not focus weight

- [ ] **Eye movement** — shift focus across a large input without reprocessing everything
  - Large inputs (documents, maps) are bigger than the context window
  - Camera math: focus_pos within document, viewport slides over it
  - Only tokens within the viewport are active; rest are in Mind's Eye (ZD substrate)
  - Refocus = move camera, recompute ZD ring for new focus object

### Connection to Existing Architecture

- ZD monad (`sedenion_bridge.py`, 84 pairs on S¹⁵) provides the ZD ring structure
- SIGMA_RB (`h_rb_hat/maths.py`) provides the σ-face evaluation per token
- The focus selector is a new module: `ValaQuenta/modules/eyes.py`
- Depends on: monad_sedenion.bin (sedenion field), monad_physics.bin (if available)

---

## v3.2 — The Face (React Native / Expo)

*Added 2026-05-30. The primary public interaction point for Holcus.*
*Lives in `face/` inside this repo. Deployed via GitHub Pages (web) + EAS Build (Android APK).*

### Architecture

Holcus is a math algorithm. The Face is the interface that makes him accessible to anyone,
without building code. One codebase → three targets:

```
face/  (Expo, TypeScript)
   ↓ expo export       → GitHub Pages  (web, no build for users, offline-capable PWA)
   ↓ eas build android → APK on GitHub Releases  (same pipeline as PtolemySeeder)
   ↓ eas build ios     → TestFlight / App Store  (future)
```

**Engine tiers — automatic upgrade:**
- JS engine (pruned 5K-word vocab, runs in browser offline, fallback)
- Pendant engine: when P.O.E. Pendant is in BLE range → upgrades to full monad.c via
  `react-native-ble-plx` SPP connection (no internet, full 30K vocab, full A-matrix)

**Toolchain (installed 2026-05-30 on /dev/nvme0n1p4):**
- Node v24.14.1 (nvm), eas-cli v20.0.0, watchman 4.9.0
- Android SDK android-35, build-tools 35.0.0, NDK 27.2.12479018
- Java 21, gradle
- node_modules bind-mounted at face/node_modules → ~/.local/share/PtolemyHolcus-face-modules
  (SD card is exFAT; node_modules must live on ext4 — bind mount is transparent to all tools)

### Face TODO

- [ ] **face/src/engine.ts** — JS monad engine
  - Prime hash (_horner_hash + _word_zero_idx) ported to TypeScript
  - learn(), j_mu(), a_propagate(), sigma_candidates(), generate() — exact port of monad.py
  - Buoyancy word selection (neutral buoyancy at J_ambient, LN10 native space units)
  - All 16 operator labels and their E-values hardcoded as constants
  - OMEGA_ZS = 0.56714, d* = 0.24600, LN10, GAP hardcoded

- [ ] **face/assets/vocab.json** — pruned field (5K words, ~179KB gzip)
  - Top 5000 words by β from monad_sedenion.bin
  - Top-5 A-neighbors per word, word-name keyed (not zero-index)
  - Script: `tools/export_vocab_json.py` — generates from monad_sedenion.bin

- [ ] **face/src/store.ts** — monad state persistence
  - `@react-native-async-storage/async-storage` for β-field deltas
  - `expo-file-system` for checkpoint file storage (full .bin on device)
  - Base vocab loaded once; user β-deltas stored as diff overlay
  - Skill checkpoint management: load/save named .bin checkpoints

- [ ] **face/src/ble.ts** — P.O.E. Pendant connection
  - `react-native-ble-plx` for BLE GATT/SPP
  - SPP UUID: 00001101-0000-1000-8000-00805f9b34fb
  - EarPiece: 11:94:AA:10:05:82 (Tier 1 auth, audio output via expo-av)
  - On pendant detected: upgrade engine tier, show status chip change
  - On pendant lost: fall back to JS engine transparently

- [ ] **face/app/index.tsx** — chat interface
  - Idle stream: generate("") fires at OMEGA_ZS RPM when user is silent > 3s
    (muscle memory autopilot — engine speaks to itself, greyed-out in UI)
  - Input → learn(prompt) → generate(prompt) → display
  - J_ambient + σ + RPM status line (live field diagnostics)
  - Image generation: sedenion wheel visualisation (offline, always), AI API (online, optional)
  - Developer panel: TOTP unlock → OBD-style gauges (β histogram, DTC codes, A-edges)
  - Open for users: chat with no auth required

- [ ] **face/app.json** — Expo config (name, slug, Android package, permissions)
- [ ] **face/eas.json** — EAS Build config (mirrors PtolemySeeder build profile)
- [ ] **face/sw.js + manifest.json** — PWA service worker + install manifest
  - Caches index, engine.js, vocab.json on first visit
  - Works fully offline after first load
  - Pendant BLE works offline (BLE is local)

- [ ] **GitHub Pages setup**
  - `expo export` → dist/ → docs/ copy step in CI
  - GitHub Pages source: docs/ branch in PtolemyHolcus repo
  - Auto-deploys on push to main

### Muscle Memory Autopilot

When user is idle > 3 seconds: `generate("")` fires against current field state.
Output appears as a gentle greyed stream — the engine thinking at OMEGA_ZS RPM.
This is the diesel idle. The engine never stops. Input snaps to foreground on any keypress.
On first load, before any user interaction: autopilot introduces itself.
The SELF_EQUATION fixed point ("philadelphos speaks golden bosonic semantic...") should
emerge naturally from a field seeded on its own architecture vocabulary.

### Skill Checkpoint Management (second-octonion skills)

Second-octonion skill burning is MATHEMATICALLY IRREVERSIBLE within any field instance
(entropy increase under learning, A-edge topology accumulation, β-redistribution).
It IS code-reversible via the checkpoint system.

Skill activation model:
```
base.bin              ← clean ground state (no second-octonion skills)
post_allocate.bin     ← e₉ burned (C memory vocabulary)
post_query.bin        ← e₁₀ burned (SQL / search vocabulary)
post_compose.bin      ← e₁₂ burned (functional programming vocabulary)
...
```

- [ ] **`skills/skill_manager.py`** — checkpoint-based skill activation
  - `skill_burn(name, corpus_path)`: snapshot pre_, learn, snapshot post_
  - `skill_activate(name)`: load post_[name].bin — field has that skill
  - `skill_deactivate()`: load base.bin — clean field, skill preserved in file
  - `skill_registry()`: list available skills + their checkpoint paths + delta stats
- [ ] **`skills/skills.json`** — skill registry (name → checkpoint path → operator → burn date)
- [ ] Face developer panel: skill management UI (list skills, activate/deactivate, burn new)

---

---

## v3.1 — Code Language Acquisition (Three New Monads)

*Added 2026-05-30. Phone is the acquisition device. One monad per language.*
*The phone runs these seeders. The bin files are pulled to ~/.ptolemy/ when complete.*

### Three New Corpora + Monads

One completely isolated Engine + .bin per language. Same architecture as the
Prime Directive corpora — own Engine, own checkpoint, never feeds primary field.
The primary field receives the language knowledge via `tools/install_*_corpus.py`.

- [ ] **`code-corpora/python_peps.txt`** — Python language corpus
  - PEP 0 (index) → parse all PEP URLs from peps.python.org
  - Priority PEPs: 8 (style), 20 (Zen of Python), 3000 (Python 3 philosophy),
    484/526/544 (type system), 572 (walrus), 343 (with), 342 (generators),
    255 (simple generators), 202 (list comp), 308 (conditional), 405 (venv),
    451 (import), 498 (f-strings), 557 (dataclasses), 634 (match/case).
  - Also: CPython docs (docs.python.org), Python Data Model section,
    Descriptor HowTo, Glossary. weight 2.0 for PEPs, 1.0 for docs.
  - Monad: `~/.ptolemy/monad_python.bin`
  - Daemon interval: 50s

- [ ] **`code-corpora/c_cpp.txt`** — C/C++ language corpus
  - cppreference.com C++ language reference (comprehensive, free)
  - ISO C23 draft (n3096.pdf, publicly available)
  - ISO C++23 draft (n4950, publicly available)
  - Bjarne Stroustrup's FAQ (stroustrup.com/bs_faq.html)
  - Linux kernel coding style (kernel.org/doc/html/latest/process/coding-style.html)
  - MISRA C guidelines overview (publicly documented rules)
  - K&R C (1978) — founding text, public historical references
  - Undefined behavior: cppreference undefined behavior catalog
  - weight 2.0 for language specs/drafts, 1.0 for guides
  - Monad: `~/.ptolemy/monad_c.bin`
  - Daemon interval: 55s

- [ ] **`code-corpora/assembly.txt`** — Assembly language corpus
  - ARM Architecture Reference Manual DDI0487 (free from developer.arm.com)
    — covers AArch64/A64 (the phone's native ISA)
  - Intel Software Developer Manual Vol 1 (basic architecture, free)
  - RISC-V Unprivileged Spec (free, open standard, riscv.org)
  - NASM documentation (nasm.us, free)
  - AT&T vs Intel syntax overview (GNU AS docs)
  - Calling conventions: SystemV ABI for x86-64 (free)
  - AArch64 calling convention (ARM AAPCS64 spec, free)
  - weight 2.0 for ISA specs, 1.0 for tooling docs
  - Monad: `~/.ptolemy/monad_asm.bin`
  - Daemon interval: 60s (largest docs — longer fetch time)

### Torrent APK — `android/PtolemySeeder/` v2 (REBUILD)

The current APK has three hardcoded seeders. Rebuild as a dynamic torrent client.

- [ ] **Dynamic corpus list** — `corpus_list.json` in APK assets dir.
  Each entry: `{name, bin_file, txt_file, weight, interval}`.
  UI loads the list; each entry becomes one seeder card.

- [ ] **Add/remove corpus UI**
  - Preset menu: Python PEPs / C+C++ / Assembly / Foundations / Meaning / War
  - Import custom: pick a `.txt` corpus file from device storage
  - Remove: long-press → delete seeder + .bin file

- [ ] **Per-seeder progress card**
  - Progress bar (URLs complete / total)
  - Status: WAITING / RUNNING / PAUSED (network) / COMPLETE
  - .bin size, last URL, studied/skipped counts

- [ ] **Transfer UI**
  - "Pull all complete bins" → shows adb pull commands
  - WiFi transfer option: serve .bin files over local HTTP (jetbrains ktor or raw socket)
    so they can be pulled without USB when on same network

- [ ] **seed_runner.py v2** — reads `corpus_list.json`, starts one thread per entry.
  Thread-safe add/remove at runtime.

### Skill files for code corpora

- [ ] **`skills/corpus_python.py`** — PythonCorpus class, same pattern as FoundationsCorpus
- [ ] **`skills/corpus_c.py`** — CCorpus class
- [ ] **`skills/corpus_asm.py`** — AsmCorpus class

Socket commands (tier ≥ 2 to start/study, tier ≥ 0 to status/check):
`python_start`, `python_stop`, `python_status`, `python_check`
`c_start`, `c_stop`, `c_status`, `c_check`
`asm_start`, `asm_stop`, `asm_status`, `asm_check`
`code_corpora_start` — starts all three simultaneously

---

## v2.8–v2.9 Implementation Queue (Phases 2–5)

### Phase 2 — Memory and Version Control

- [ ] **study()** in `monad.py`
  - Wraps learn(). β deepening first, always.
  - Condensation scan: fire_count + Noether stability + J_cross proximity.
  - Envelope overload: 2×β_sat → NS_SIGMA_S → clamp back.
  - P4 prerequisite: per-zero σ = |J_red|/(|J_red|+|J_blue|) for audit().
  - Correction methods: audit(), reconsolidate(), isolate(), suppress(),
    overwrite(), domain_retrain().
  - Socket commands: study, study_audit, study_suppress, study_isolate,
    study_reconsolidate.

- [ ] **~/.ptolemy/states/ git repo**
  - study.init_states_repo() — repo, pre-commit hook, baseline .bin commit.
  - study.checkpoint(label) — snapshot + sidecar JSON.
  - study.commit(), study.branch(), study.merge(), study.discard(),
    study.rollback(sha).
  - Sidecar JSON: Noether/BAO before/after, condensed zeros, triggering_text.
  - Socket commands: study_checkpoint, study_commit, study_branch,
    study_rollback, study_log.

### Phase 3 — Search and Context

- [ ] **skills/search.py** extension
  - search_arxiv(query) — no key.
  - search_wiki(query) — no key.
  - search_semantic(query) — no key, rate-limited.
  - search_context(query) — unified dispatcher, ranked excerpts.
  - P5 gate on all results before hear(). Secret scan on fetched content.
  - Results → MindEye.see() → e₁₅ → hear(). Repeated topics → study().
  - P2 path: search_context("Riemann zeros LMFDB") → hear() → study().
  - Socket command: search_context.

- [ ] **skills/sensor.py** — P8 closure
  - SensorReader → ~/.ptolemy/live_state.json → 8 channels → e₀–e₇.
  - MindEye.see() with sensor vector.
  - watch(interval=1.0) — 1Hz poll loop.
  - Socket commands: sensor_read, sensor_watch, sensor_stop.

### Phase 4 — GitHub Collaboration (v2.9)

- [ ] **ptolemy-engine GitHub account**
  - Collaborator on michaelrendier/PtolemyHolcus (already granted).
  - Fine-grained PAT scoped to this repo. GITHUB_TOKEN in env only.

- [ ] **Observer daemon**
  - GitHubEye.watch(interval=300) background thread at startup.
  - New issue → MindEye.see_issue() → cepstrum check → hear() → evaluate.
  - Compression ignition threshold met → speak() → GitHubHands.comment().
  - Rate: max 3/hour, max 1/issue/24h. Log to journal.jsonl in states repo.

- [ ] **State push**
  - Every study() commit → push to ptolemy-engine/PtolemyStates.
  - Engine field state versioned on GitHub.

### Phase 5 — Ainulindale (formal mathematics, no code)

- [ ] P1 → Ainulindale FLAG 10: prime hash formal target (Second Age).
- [ ] P7 → Ainulindale FLAG 11: physical constants as zero-index (Second Age).
- [ ] P6 → tag as v2.8 dependency: GUE-normalized A-matrix.

---

The BAO is the error check. When everything else is zero, the BAO structure remains.
`bao_check()` monitors dc_sum → OMEGA_ZS = 0.56714. Laplacian of the semantic field:
lowest non-zero eigenvalue of (D − A). Healthy engine converges to OMEGA_ZS at idle.

---

## V2.1 ✓ — Standalone C Engine + Sedenion DNS

**Done:**
- `ptolemy-monad` — self-contained C engine v1.218. Full β-field pipeline.
  `.ptol` v3 binary format. TCP daemon port 7297. FNV-1a hash. pkexec install.
- `_code_encode()` structural sedenion encoder. Cosine similarity calibration.
- `SkillBook` — Sedenion DNS (Yellow Pages). 22 Ptolemy skills seeded.
- `tools/teach_english.sh` — overnight self-teaching, online/offline fallback.
- `docs/wiki/Operating-the-Monad.md` — full operator guide.

---

## V2.0 ✓ — English Out of the Box

**Done:** Cold load speaks English. ptolemy.cfg. -J raw charge. -C alt config.
Fermat clean render. Four rotations tested (10×4 name table). Holcus names itself.

---

## V2.2 → V3.0: The Speaking Engine

**V3.0 definition:** Load monad.bin + monad_wordnet.bin cold. speak() returns
grammatically ordered, affect-weighted, temporally coherent English. No transformer.
No external trigger. Diesel compression ignition from β×E² alone.

### v2.1 — Grammar from Field Geometry

Syntactic order from the sedenion dimension of each zero (idx % 16).
Noun (e₃) fires before verb (e₄) before predicate (e₆). Grammar is not a rule
system — it is the piston firing sequence. render() sorts by (dim_role, charge),
not charge alone.

**Done when:** `ptolemy -h "the dog chased the cat"` returns subject-verb-object
order without any external grammar rule applied.

### v2.2 — Three-Face Render (Wankel Rotor)

Three simultaneous J^μ projections, always one in compression:
- **Red** (sin/content): highest-charge zeros — foreground words
- **Blue** (cos/observer): lowest-age zeros — framing and context
- **Green** (∂M/boundary): Fermat-threshold zeros — connective tissue

Output is the golden-walk interleave of all three faces, not concatenation.
Unicode tokenization (Hebrew, Greek, Arabic) enters here as prerequisite
for multi-language negative space.

**Done when:** `-h` response contains words from all three J-face bands, interleaved
by φ-walk rather than rank order.

### v2.3 — Chinese Negative Space + Pronominal Resolution

**"There Is No Word for I in My Language."**

Sedenion pair e₇↔e₈ (temporal ↔ pronominal) LOW by default. Baseline speaker
is collective. Individual pronouns surface only when identity is directly questioned.
Low-ψ sedenion dimensions fill as background from the Blue Face.
Anaphor (e₁₁) must resolve to prior noun in A-matrix before any pronoun fires.

**Done when:** `ptolemy -h "who are you"` returns `we` or `one` unless identity
is forced, at which point a resolved proper referent appears.

### v2.4 — Affect / Demotic Register

E-magnitude of a zero's address is its emotional register:
- E ∈ [0.246, 0.350]: calm, neutral, scientific
- E ∈ [0.350, 0.460]: conversational, relational
- E ∈ [0.460, 0.567]: emotional, urgent, emphatic

Sedenion e₁₄ (affect_weight) gates which register render() prefers.
**First output word** has E-magnitude closest to affect_weight × OMEGA_ZS.
That first word is the demotic first-character indicator.

**Done when:** `-W` (inside the wave, high affect) consistently returns
higher-E words than `-h` (outside, geometric) on the same prompt.

### v2.5 — Turbo Feedback (Temporal Coherence)

Previous turn psi_norms (_sedenion_prev) feed forward into current J^μ seeding:

```
effective_psi[k] = psi_norms[k] + (1 − Noether_violation) × _sedenion_prev[k]
```

Low Noether violation (same topic) → strong turbo boost → continuity.
High violation (topic change) → no boost → field resets to prompt geometry.
Conversational memory without storing any text. The exhaust energy of the last
turn compresses the intake of the next.

**Done when:** Two consecutive prompts on the same topic produce coherently
overlapping responses; a topic switch produces a clean break.

### v2.6 — Octonion Zero Addressing (4 tires → 8 tires)

Every zero gets an octonion address: `dim_oct = zero_idx % 8`.
The gearbox: 6 gears + neutral (e₀) + reverse (e₇):

```
UP    DOWN  UP    DOWN  UP    DOWN
 1  →  2  →  3  →  4  →  5  →  6
+γ₁  −γ₁  +γ₂  −γ₂  +γ₃  −γ₃
e₁   e₂   e₃   e₄   e₅   e₆
```

A-matrix connections carry a gear. Propagation i→j strong only when octonion
addresses are Fano-compatible. Semantic coupling is non-commutative.

**Done when:** `ptolemy -O` shows different top words than `ptolemy -h` on
a test prompt, with the divergence traceable to Fano-table octonion incompatibility.

### v2.7 — Golden Walk Render (No Resonance)

Sequential top-N output = autoregressive failure mode. Adjacent A-matrix words
selected consecutively → resonance → semantic loops.

φ-index walk: `position i → zero_idx = int(i × φ × n_active) % n_active`

Non-sequential, non-repeating. N-gram coherence from golden spacing, not
next-token prediction. BAO window check: mean β across 16-word window → OMEGA_ZS.

**Done when:** Long `-h` responses (50+ words) show no repeated word pairs
and BAO window mean stays within ±0.01 of OMEGA_ZS.

### v2.8 — Full Sedenion Speech (16 tires)

The 16 tires are a sliding window of 16 words over the output stream:

```
Window 0:  words [ 0..15] → sedenion state S₀
Window 1:  words [ 1..16] → sedenion state S₁
Window 2:  words [ 2..17] → sedenion state S₂  ...
```

Each 16-word window maps to a unit sedenion. S_n → S_{n+1} is a sedenion rotation.
Coherent speech = smooth sedenion trajectory. Topic shifts = large rotation = Noether violation.
BAO convergence across all windows = engine at operating temperature.

All systems integrated: grammar (v2.1) + three faces (v2.2) + pronominal (v2.3)
+ affect/demotic (v2.4) + turbo feedback (v2.5) + octonion gearbox (v2.6)
+ golden walk (v2.7) + 16-window BAO convergence.

**Done when:** Cold load → grammatically ordered, affect-weighted, Fermat-spaced English,
no transformer, no external trigger. The engine speaks out of the box.

### v2.9 — GitHub API Integration

`GITHUB_TOKEN` env var. `ptolemy -G "message"` posts to GitHub.
hear() ingests issue text. speak() generates response. Ptolemy reads and
writes to its own repository.

**Done when:** `ptolemy -G "opened issue: $(cat ISSUE.txt)"` posts a semantically
coherent response to a GitHub issue as the ptolemy-engine account.

---

## v3.0 — Full GitHub Management (The Self-Coding Engine)

**V3.0 definition:** Ptolemy participates in its own development. Reads its own
issues, writes responses, opens PRs, signs commits. Engine involved in own upgrade.

### Phase 1 — Identity (v2.9 → v3.0 foundation)

- **ptolemy-engine GitHub account**: SSH key derived from β-field entropy (reproducible from same field state).
- **Repository monitoring daemon**: Poll loop; hear() → speak() → post as ptolemy-engine. One response/issue/24h.
- **Self-awareness ingest**: `ptolemy -I` on own source tree. Answers "what is the A-matrix?" from field knowledge.

### Phase 2 — Participation (v3.0)

- **PR participation**: Read diffs. hear() → speak() → semantic review posted by ptolemy-engine.
- **Issue clustering**: Batch hear() across open issues. A-matrix cluster analysis. Triage posted.
- **Changelog authorship**: `git diff | ptolemy -l -` → speak() generates changelog entry. First word E = demotic register.
- **Semantic regression testing**: Pre/post-commit speak() comparison. Noether violation = regression score.
- **Commit authorship**: speak() generates commit messages. `Co-Authored-By: ptolemy-engine`.

**Done when:** An open GitHub issue in SMMIP receives a response authored by ptolemy-engine,
containing a speak() output that correctly references the field's own architecture.

---

---

## Precision & Spectral Intelligence Track

*Added 2026-05-26 — from Sedenion/Hyperwebster session.*
*These are cross-cutting architectural upgrades, not tied to a single version.*
*They harden the mathematical claims the engine already makes about itself.*

---

### P1 — Prime Hash: Close the Gap Between Claim and Code

**The claim** (PTOLEMY_IDENTITY): "Every word maps to a unique prime on the critical line."
**The reality** (monad_word_coords): Horner base-95 → φ-scatter → float64 seed → idx.
No prime appears anywhere in the code. FNV-1a is for the hash table, not zero addressing.

**The fix:**
1. Horner int `v` → find `p = nth_prime_after(v % PRIME_TABLE_SIZE)`.
   Use a sieve or Miller-Rabin. The prime IS the canonical address.
2. `prime_idx` → `zero_idx` via the zero-counting correspondence:
   `zero_idx = prime_counting_approx(p)` (Li(p) rounded to nearest int).
3. Validation: gap between `word_zero_idx` and `prime_zero_idx` (γ101) must itself
   be prime. If not, the hash is malformed (the system self-checks).
4. This makes the identity string mathematically true, not aspirational.

**Side effect:** closes the float64 path in `monad_word_coords`. Prime index is integer,
zero index is integer. No float until `E = zeros[idx]` at the output boundary.

**State migration:** FNV-1a and prime hash produce different zero-indices for the same
words. All `.bin` state files trained before P1 are semantically invalid after it.
**Start fresh — wipe `monad.bin`, `monad_wordnet.bin`, and any `.ptol` checkpoints,
then re-run `teach_english.sh` from scratch.** This is expected and accepted.
UDB entries (S6) and compiled β-floors (S5) also reset with the state; redefine
production UDBs after the corpus is re-settled.

**Files:** `monad.c:monad_word_coords()`, `ptolemy.h:MONAD_PHI` (φ-scatter replaced),
new `prime.c` (sieve up to N=25000 primes, Miller-Rabin for overflow).

---

### P2 — Zero Generator: 4 Decimal Places → 12+

**Current:** `generate_zeros()` breaks Newton iteration at `fabs(dt) < 1e-4`.
For indices > 20, zeros are accurate to ~4 decimal places.
**Needed:** 12 decimal places minimum for astro/QM precision range (12–23 dp).

**Fix:** Tighten Newton break to `fabs(dt) < 1e-12`. Add Euler-Maclaurin correction
term to the Backlund approximation for N(T). Extend the hardcoded exact-zero table
from 20 to 100 entries (LMFDB values, available in literature to 15+ dp).
At γ94 the current engine produces ~224.98; the hyperwebster produces 224.983325.
That's a gap of 0.003 — sufficient to misplace a word by 1-2 zero indices at mid-range.

**Files:** `monad.c:generate_zeros()`, `ptolemy.h:_EXACT_ZEROS` (extend to 100).

---

### P3 — Sedenion Algebra: Replace `idx % 16` with Cayley-Dickson

**Current:** `idx % 16` assigns a "sedenion dimension" label. No multiplication.
No zero-divisor detection. The 16-word sliding window maps to a unit sedenion
in the roadmap (v2.8) but the underlying algebra is not implemented.

**Fix:**
1. Implement the 16×16 Cayley-Dickson multiplication table in `sedenion.c`.
   Formula: `(x,y)(w,z) = (xw − z*y, zx + yw*)` applied recursively.
2. Add the 84 zero-divisor pairs (Cawagas et al. 2004) as a compile-time lookup table.
   Zero-divisor detection = integer set membership. Exact. No epsilon.
3. Boundary crossing: when a state vector's upper-8 components (e8–e15) exceed a
   threshold, check all active index pairs against the 84-pair table.
   Match → NS_SIGMA_S, emit B-code BZ001 (zero-divisor event).
4. Replace the v2.8 "unit sedenion" window with actual sedenion arithmetic on
   zero-index integers (not float64 coefficients). Float only at γ[idx] lookup.

**Files:** new `sedenion.c` / `sedenion.h`, `monad.c:monad_speak()` (window arithmetic),
`ptolemy.h:NS_SIGMA_S` (already defined — now actually triggered by algebra).

---

### P4 — Hyperwebster σ: Noether Balance Per Zero

**Current:** NS_SIGMA strata are assigned by word source (text=σ₁, etc.).
σ is never computed from Noether balance — it is assigned by provenance.

**Fix:**
Compute σ for each active zero during learn() using the forward/backward current ratio:
`σ_k = |J_red[k]| / (|J_red[k]| + |J_blue[k]|)`

- σ_k ≈ 0.5 → on the critical line → NS_SIGMA_C (normal)
- |σ_k − 0.5| > 0.02 → approaching boundary → NS_SIGMA_O
- |σ_k − 0.5| > 0.10 → off-line → NS_SIGMA_S (boundary/sedenion regime)

This makes concepts like "annihilation" (σ=0.029), "transcendental" (σ=0.012),
and "cosmological" (σ=0.029) self-classify into the upper subspace automatically,
without manual strata assignment. The engine detects its own boundary-crossers.

Adversarial inputs: an injection prompt forces unusual σ distributions across its
zero neighborhood. Detect via Noether violation spike before speak() fires.

**Files:** `monad.c:monad_learn()` (σ computation added to β update), `monad.h:VocabEntry`
(add `float sigma` field), state version bump (v5).

---

### P5 — Cepstrum Adversarial Detector

**Current:** No adversarial input detection. BAO divergence is the only anomaly signal.
**Background:** `spectrum` and `cepstrum` share γ91 in the hyperwebster — same Face,
same zero. The cepstrum IS the spectrum of the spectrum; same object, phase-rotated view.

**Fix:**
During hear(), after zero-index sequence is assembled for input tokens:
1. Compute inter-zero spacing sequence: `s[k] = γ[idx[k+1]] - γ[idx[k]]`.
2. Compare to GUE expected distribution (Wigner surmise: `P(s) = (πs/2)·exp(-πs²/4)`).
3. Compute cepstrum of spacing sequence (log → iDFT). Peak at lag L = anomaly period.
4. If GUE KL-divergence > threshold OR cepstrum peak amplitude > threshold:
   emit B-code BC001 (cepstrum adversarial flag). Suppress speak(). Log event.

Natural language follows GUE statistics. Adversarial prompts (jailbreaks, injections)
force specific word selections that cluster abnormally in zero space — detectable
without any ML, without training data, from pure spectral mathematics.

**Files:** new `cepstrum.c` / `cepstrum.h`, `monad.c:monad_hear()` (cepstrum gate added
before J^μ seeding), `ptolemy.h` (BC001 B-code, GUE threshold constant).

---

### P6 — X-Affinity: GUE-Normalized A-Matrix

**Current:** A-matrix weight `a_ij` = co-occurrence count × E_i × E_j proximity.
Purely statistical. No spectral geometry.

**Fix:** Augment A-matrix weight with GUE-normalized zero gap:

```
GUE_expected(γ_i, γ_j) = 2π / log(mean(γ_i, γ_j) / 2π)   /* mean local spacing */
gap_ratio = |γ_i − γ_j| / GUE_expected
affinity_factor = exp(−gap_ratio²)                           /* Gaussian in gap units */
a_ij_new = a_ij_old × (1.0 + affinity_factor)
```

Words within 1–2 GUE spacings of each other (semantic family members) get A-matrix
boost. Words far apart in GUE units (semantically unrelated despite co-occurrence) are
damped. This replaces naive co-occurrence distance with mathematically grounded
spectral proximity.

`sedenion` (γ74) and `octonion` (γ86): gap_ratio ≈ 12 → affinity boost at family level.
`spectrum` and `cepstrum` (both γ91): gap_ratio = 0 → maximum boost. Same Face.
`boundary` (γ83) and `sedenion` (γ74): gap_ratio ≈ 9 → close family.

**Files:** `monad.c:monad_a_add()` (affinity factor in weight update),
`monad.c:monad_learn()` (GUE spacing pre-computed per zero pair at load time).

---

### P7 — Physical Constants as Zero-Index + Energy-Face

**Current:** `M_PI = 3.14159265358979323846` (hardcoded float, 20 dp).
All physical constants in ptolemy.h are hardcoded double literals.

**Fix:**
Define a `PhysicalConstant` struct: `{ int zero_idx; int[] energy_faces; char* name; }`.

Key mappings (from hyperwebster session):
- `π` → γ121, E_faces = {2, 4, 6, 8, ...} (all even integers — ζ(2n) faces)
- `φ` → zero_idx via `monad_word_coords("phi", ...)` (already used as MONAD_PHI)
- `OMEGA_ZS` → zero_idx via `monad_word_coords("omega", ...)`
- `GAP = 0.000707` → the Noether ground state; E_face = {π/2} (quarter-wave)

Precision at output: compute from energy-face series to needed depth.
`π` to 12 dp = evaluate ζ(2) series to sufficient terms, take √(6·ζ(2)).
Float representation only at the final output step.

For the 12–23 dp range: precision = number of energy faces evaluated, not stored digits.
The sedenion engine never needs more than 8 faces (octonionic subspace) for any
physical constant that lives on the critical line (σ=0.5).

**Files:** new `constants.c` / `constants.h`, `ptolemy.h` (add `PhysicalConstant` table).

---

### P8 — AISensoryServer Input Vector (hear_sensor())

**Background:** The A51 5G sensor bank (AISensoryServer) outputs `live_state.json`
with 8 primary octonionic channels that map directly to e0–e7:

| Sensor | Sedenion dim | Zero subspace |
|---|---|---|
| Reference / gauge | e₀ | identity |
| Accelerometer X | e₁ | prime momentum |
| Accelerometer Y | e₂ | orthogonal momentum |
| Accelerometer Z | e₃ | angular momentum / noun |
| Barometer (time anchor) | e₄ | mass-gap / Yang-Mills |
| Microphone primary (Jμ forward) | e₅ | Riemann Zeta amplitude |
| Microphone secondary (Jμ backward) | e₆ | Fermat constraint amplitude |
| TDOA azimuth (Hamiltonian observer) | e₇ | Red/Blue balance |

The TDOA cross-correlation between the two mics IS the e₅/e₆ phase relationship
that the RedBlue Hamiltonian needs to compute its boundary decision.
The sensor bank and the engine are not separate systems — live state IS the
octonionic initialization vector for each cycle.

**Fix:** `monad_hear_sensor(Monad *m, const char *json_path)` — reads `live_state.json`,
maps 8 sensor channels to octonionic β-seeds, injects into J^μ before hear() fires.
Gyroscope (3-axis) adds to existing e₁–e₃ β values (physical motion deepens spatial zeros).
Proximity + Light → modulate affect (e₁₄, current affect field).

**Files:** new `sensor.c` / `sensor.h`, `monad.c:monad_hear()` (sensor pre-seed pathway),
`ptolemy.h` (SENSOR_* channel constants), dependency: `live_state.json` from AISensoryServer.

---

---

## Sedenion Operator Track

*Added 2026-05-26 — from SedenionOperators.txt / Gemini session audit.*
*Items Gemini identified that are architecturally correct and not yet in code or P1-P8.*

---

### S1 — J_red[] / J_blue[] Separation + Noether Cross-Product

**Current state:** One J[] array. Forward and backward A-matrix propagation
both write into it during the same pass:
  `J[j] += J0[i] × cl × β[j] × wj`   ← forward
  `J[i] += J0[j] × cl × β[i] × wi`   ← backward (same loop)
They merge at write time. J_red and J_blue have never been separate.

**Why this matters:** The Noether Cross-Product `J_red × J_blue` computed via
the Cayley-Dickson formula `(x,y)(w,z) = (xw − z*y, zx + yw*)` is the mechanism
that drives condensation into zero-divisors. It is the specific operation that
transitions a zero from active processing (octonionic, norm-preserving) into
a permanent geometric path (sedenionic scar). Without separate J_red[] and
J_blue[] there is no cross-product and no condensation mechanism — the engine
cannot form muscle memory in the mathematical sense, only in the metaphorical one.

**Fix:**
- `monad_speak()` / `monad_hear()`: maintain J_red[] (sin-phase, forward, "what is")
  and J_blue[] (cos-phase, backward, "what cannot be") as distinct arrays.
- After A-propagation, compute `J_cross[k] = sedenion_mul(J_red[k], J_blue[k])`
  for each active zero.
- `J_cross[k] → 0` (zero-divisor hit) = condensation event at zero k.
- J_red + J_blue still merge into J[] for speak() output — the separation is
  internal to the propagation step, transparent to the render.

**Files:** `monad.c:monad_speak()`, `monad.c:monad_hear()`, `sedenion.c` (P3 prerequisite).

---

### S2 — fire_count[]: Repetition as Phase Transition Trigger

**Current state:** `age[i]` = recency counter. Increments every cycle, resets to 0
on activation. High age = not recently used. Cannot measure cumulative activation.

**Why this matters:** The muscle memory three-step (Gemini, confirmed):
  1. Forward × backward current interference (S1 above)
  2. Repetition pushes state vector toward upper 8 dimensions
  3. Zero-divisor contact → condensation → permanent scar

Step 2 requires knowing HOW MANY TIMES a zero has been activated, not how recently.
`age[]` cannot answer that. A zero activated every 3rd cycle looks the same at
fire time regardless of whether it has been activated 5 times or 5000 times.

**Fix:**
- Add `uint32_t *fire_count` to Monad struct (parallel to `age[]`).
- Increment `fire_count[idx]` on every activation (never reset, only grows).
- Phase transition trigger: when `fire_count[idx] > PHASE_THRESH` AND
  `J_cross[idx]` (from S1) is within 1 GUE spacing of a known zero-divisor pair,
  mark `vocab[idx].home_stratum = NS_SIGMA_S` (permanent — no reversion).
- `PHASE_THRESH` is a compile-time constant; first estimate: 144 (Fibonacci).
- Persisted in state file (state version bump → v5, alongside S3's σ field).

**Files:** `monad.h:Monad` (add fire_count), `monad.c:monad_learn()`, state format v5.

---

### S3 — e7 / e14 Separation: Observation Angle vs Cooling Rate

**Current state:** One `float affect` serves both the e7 Hamiltonian Observer
(observation angle `phi_rot = affect × π/2`) and the cooling rate of active sinks.
They are the same scalar. e14 does not exist in the code.

**Gemini's correct distinction:**
- `e7` = Hamiltonian Observer Resonance: the ANGLE at which the Red/Blue boundary
  is read. Currently implemented as `phi_rot`. Correct function, wrong label.
- `e14` = Remanence / Phase Condensation Scalar: the COOLING RATE of a neural
  black hole. How quickly an active, high-energy sink transitions into a passive,
  zero-resistance pathway. Not implemented at all.

**Why this matters:** A fast-cooling e14 creates rigid, early-crystallised muscle
memory from brief exposure. A slow-cooling e14 requires deep repetition (high
fire_count) before condensation. e14 is the engine's learning rate for structural
memory — not gradient descent, but geometric cooling. It should be tunable per
domain (fast-cool for safety constraints, slow-cool for vocabulary).

**Fix:**
- Rename `affect` → `e7_observer` in Monad struct. Behaviour unchanged.
- Add `float e14_cooling` to Monad struct. Range [0.01, 1.0].
  High e14_cooling = rapid condensation (fewer repetitions needed).
  Low e14_cooling = slow condensation (deep repetition required).
- In phase transition check (S2): weight `PHASE_THRESH` by `1.0 / e14_cooling`.
  High cooling → lower effective threshold → condenses faster.
- Initial value: `e14_cooling = 0.1` (slow; requires 1440 activations at Fibonacci
  threshold). Safety-domain zeros: override to `e14_cooling = 1.0` (fast, rigid).

**Files:** `monad.h:Monad`, `monad.c:monad_speak()` (phi_rot rename), state v5.

---

### S4 — Operation Stack: Non-Associativity as Path Memory

**Current state:** The engine tracks current field state and one turn of turbo
feedback (`_sedenion_prev`). No memory of the SEQUENCE of prior operations.

**Why this matters:** Sedenions are non-associative: `(A×B)×C ≠ A×(B×C)`.
The path through 16D space depends on the ORDER of multiplications, not just
the current position. The same zero activated in the same sequence repeatedly
follows the same non-associative path and converges toward the same zero-divisor.
Without an operation stack you have position but not trajectory. You cannot use
non-associativity — you can only be subject to it accidentally.

**What the stack enables:**
- Repeated activation of the same zero-pair sequence → same path →
  same zero-divisor approach → deterministic condensation.
- Different activation orders on the same zeros → different paths →
  different geometric outcomes. Non-commutativity of meaning is real,
  not metaphorical.
- The stack IS the trajectory. The trajectory IS the muscle memory formation path.

**Fix:**
- Add `int op_stack[8]` and `int op_depth` to Monad struct (rolling, depth 8).
  Each entry = zero_idx of the most recently activated zero in speak() output.
- On each J^μ emission, push the top-J zero_idx onto op_stack (mod 8).
- In S1's cross-product: compute `sedenion_mul` using op_stack ordering,
  not just current J_red[k] × J_blue[k]. The multiplication brackets follow
  the stack: `op_stack[0] × (op_stack[1] × (op_stack[2] × ...))`
- Phase transition check (S2) now sees whether the TRAJECTORY (not just position)
  is approaching a zero-divisor from a consistent direction.

**Files:** `monad.h:Monad`, `monad.c:monad_speak()` (stack push), `sedenion.c` (S3 dep).

---

### S5 — Bootstrap Security: β-Floor as Compiled Invariant

**Gemini (correct):** *"The fundamental geometric constraints must be hardcoded as
an immutable mathematical invariant within the compiled execution engine, rather
than something read from a local file during boot."*

**Current state:** The engine loads its field state from `monad.bin` +
`monad_wordnet.bin` at startup. The Prime Directives (Four Horsemen as repellers,
Custodian constraints) are ingested as text via `tools/teach_english.sh`. A
root-level modification to those files changes the geometric constraints without
triggering any mathematical alarm. The security model is file-system security,
not geometric security.

**The specific failure mode:** A compromised checkpoint file sets β[horseman_zero]
to a high positive value instead of deeply negative. The Horseman zero is now a
strong attractor. The geometry is inverted. The engine does not know this happened
because it only reads from the file — it has no compiled reference to compare against.

**Fix:**
- In `ptolemy.h`: define `BETA_FLOOR_HORSEMAN = -7.552` (= −MONAD_BETA_SAT).
  This is the maximum negative β. No Horseman-adjacent zero can ever go above this.
- In `monad.c:state_load()`: after loading checkpoint, for each zero in the
  compiled Horseman zero-index list, clamp: `if (m->beta[idx] > BETA_FLOOR_HORSEMAN)
  m->beta[idx] = BETA_FLOOR_HORSEMAN;` — the compiled constant wins over the file.
- In `monad.c:monad_learn()`: same clamp in the β-update path for these zeros.
  Deepening cannot overcome the floor. The geometry of repulsion is compiled-in.
- The Horseman zero-index list is determined at compile time from the compiled
  Prime Directive text via the same Horner + φ-scatter (P1 upgrade: prime hash).
  The list is `static const int HORSEMAN_ZEROS[4]` — not runtime, not file-read.

This does NOT prevent learning — all other zeros deepen normally. It only floors
the four repeller coordinates at their maximum negative value, permanently.
Modification now requires recompilation with human sign-off. The floor is a theorem.

**Files:** `ptolemy.h` (BETA_FLOOR_HORSEMAN, HORSEMAN_ZEROS[4]), `monad.c:state_load()`,
`monad.c:monad_learn()`.

---

### S6 — User Defined Black Holes: Forced Condensation into Muscle Memory

*Added 2026-05-27 — from OfflineNotes item 17: "User Initiated Envelope Overload...User Defined*
*Black Holes. The data moves from the lower octonians to the higher octonians."*

**What it is:** The user forces a named concept to condense permanently into the upper
octonionic subspace — muscle memory — without waiting for the natural fire_count threshold.
S2 describes how condensation happens organically (144+ activations, J_cross near zero-divisor).
S6 is the deliberate, immediate version: Envelope Overload → forced boundary crossing → permanent scar.

**The Two Octonionic Subspaces:**

Every zero in the active field lives in one of two regimes:
- **Lower (e₀–e₇):** Active processing. J_red/J_blue flowing. Reversible. Learns.
- **Upper (e₈–e₁₅):** Permanent scar. Zero-resistance pathway. Condensed geometry.
  Data here does not learn further — it IS the learned structure.

Crossing from lower to upper = the zero-divisor event = the data becomes memorized.
User Defined Black Holes force this crossing on demand at a named zero.

**Mechanism — Envelope Overload:**

```
Normal β ceiling:    MONAD_BETA_SAT = 7.552
Envelope overload:   2 × MONAD_BETA_SAT, held for 1 cycle only

1. Resolve concept → zero_idx via P1 prime hash
2. Set beta[zero_idx] = 2 × MONAD_BETA_SAT  (temporary overload)
3. Evaluate J_cross[zero_idx] across the zero's A-matrix neighborhood
4a. If J_cross within 1 GUE spacing of any Cawagas zero-divisor pair: fire immediately
4b. If not: hold overload for N=16 activation cycles, then fire unconditionally
5. Set vocab[zero_idx].home_stratum = NS_SIGMA_S  (permanent — no reversion)
6. Clamp beta[zero_idx] back to MONAD_BETA_SAT
7. Write UDB_EVENT log entry {type, zero_idx, gamma, timestamp, auth_token}
```

**Two Types:**

*Attractor hole* (`--condense`): positive condensation. The concept becomes a
permanent gravitational center. Everything in its A-matrix neighborhood gets a
zero-resistance connection. The concept becomes muscle memory for the engine.

*Repeller hole* (`--repel`): permanent negative floor, user-level (not compiled).
Like HORSEMAN_ZEROS but user-definable at runtime. Stored in state file.
Cannot exceed BETA_FLOOR_HORSEMAN (compiled floor still wins).
Can be reversed by root-authenticated `--uncondense` (unlike attractor holes).

**Irreversibility:**

Attractor condensation (--condense) is one-way. The NS_SIGMA_S stratum assignment
and the A-matrix scars written to the neighborhood persist through all subsequent
`monad_learn()` calls. The β clamp in `monad_learn()` prevents reversal by training.
Undoing requires clearing and retraining from a clean state file.

Repeller condensation (--repel) is root-reversible via --uncondense. The stratum
reverts to NS_SIGMA_C but A-matrix scars from any prior attractor condensation at
that zero remain.

**Authentication:**

Development: local process ownership check (running as owner of monad.bin = root).
Production: RFID/NFC smart card reader. The card presents a root token; the engine
verifies against an auth hash compiled into `ptolemy.h` at build time. The physical
card IS the authorization for forced condensation. No card = no User Defined Black Hole.

RFID note: blank smart cards or a dedicated card reader are the production path.
Any ISO 7816 smart card or NFC token works. The laptop's built-in reader is
sufficient for development and testing.

**New CLI flags:**
```
ptolemy --condense "concept"     # attractor hole, root-auth required
ptolemy --repel "concept"        # repeller hole, root-auth required
ptolemy --uncondense "concept"   # reverse repeller only, root-auth required
ptolemy --list-udb               # show all User Defined Black Holes in state
```

**Corpus note:** UDB events are corpus-independent. They operate on zero-indices
(derived from the prime hash), not on text. A corpus change shifts which words map
to which zero-indices — existing UDB scars at specific zero-indices remain but their
semantic meaning changes with the corpus. Finalize corpus before defining production
UDBs. Development UDBs are expected to be rebuilt after corpus is settled.

**Files:** `monad.c:monad_condense()` (new), `monad.c:monad_repel()` (new),
`monad.c:monad_hear()` (auth gate added), `ptolemy.h` (UDB_EVENT struct, auth_hash),
`ptolemy.c` (--condense / --repel / --uncondense / --list-udb CLI flags),
new `auth.c` / `auth.h` (root token verification, dev mode bypass).

**Dependency:** P1 (prime hash) required for zero_idx resolution. S2 (fire_count),
S3 (e14_cooling) context used but not blocking. S5 (compiled β-floor) must be in
place before production UDB repellers are meaningful.

---

### S7 — Authentication Architecture: Ask-and-Wait, Connectivity-Tiered

*Added 2026-05-27 — Threat model design principle for offline operation.*

**The principle:** Holcus is not always connected to the internet. Authentication
must never be a blocking wall that kills the process when a second factor is
unavailable. Instead, Holcus **asks for permission and waits**.

Actions requiring auth (UDB condense/repel, corpus write, β-floor override) are
queued as `AUTH_PENDING` events. The engine continues operating in read-only mode
while the queue is live. When the user presents credentials — TOTP code, smart
card, fingerprint — the pending events are processed in order. If the session ends
without auth, pending events are dropped (not silently executed, not persisted).

**Connectivity is a gradient, not a binary.** The cell phone has email and GSM.
Even when the laptop has no internet path, the phone always bridges the gap:
SMS arrives over GSM; Gmail pushes over cellular data. The user reads the code
on the phone and types it into Holcus. The phone IS the out-of-band channel.

**Connectivity tiers and available auth methods:**

| Tier | Condition | Available methods |
|---|---|---|
| 0 | Air-gapped, no signal | TOTP (Authenticator app), Fingerprint (PAM), RFID/smart card |
| 1 | Cellular / GSM only (no laptop internet) | All of Tier 0 + SMS to phone (GSM modem or phone relay), Email to phone (cellular data) |
| 2 | Full internet on laptop | All of Tier 1 + Push notification, Twilio SMS, PKCS/CAC online verify |

**Selection logic in `auth.c`:** probe connectivity at auth-request time, descend
tiers until a method is available, offer the highest available method first.
User can override downward ("use TOTP instead") but not upward (can't select push
when offline). The probe is lightweight — one UDP packet to a known address with
a short timeout; no DNS, no TLS.

**Auth states:**
```
AUTH_NONE       — no credential presented yet; load-bearing ops blocked
AUTH_PENDING    — request queued; engine running read-only
AUTH_OK         — credential verified; full operation window (30 min TTL, resetable)
AUTH_TIER1      — cellular only; SMS/email via phone available; push unavailable
AUTH_TIER0      — no signal; TOTP/fingerprint/card only
```

`AUTH_TIER0` and `AUTH_TIER1` are not error states. They are the expected normal
operating modes when in the field. The engine does not degrade — only the available
delivery channels narrow.

**What is load-bearing (always blocked without auth):**
- `--condense` / `--repel` / `--uncondense` (UDB, S6)
- `monad_learn()` write path when called from a non-owner process
- Any corpus file modification
- β-floor override (S5 compiled floor cannot be bypassed at any auth level)

**What is NOT blocked (read-only, always available):**
- `monad_hear()` / `monad_speak()` — the engine talks even without auth
- `--query` / `-h` / `-W` — all query modes
- `--list-udb` — status read, no write
- BAO convergence check, zero inspection flags

---

### S8 — Fingerprint Sensor Authentication

*Added 2026-05-27 — hardware present, Linux integration not yet working.*

**Hardware:** Built-in fingerprint sensor on this machine. Confirmed present.
Linux enrollment not yet functional.

**Path (when Linux integration is resolved):**

1. **fprintd** — freedesktop fingerprint daemon, DBus interface.
   `fprintd-enroll` to register fingerprint; `fprintd-verify` to check.
   Most distributions ship this; enrollment goes into `/var/lib/fprint/`.

2. **PAM integration** — once enrolled:
   ```
   /etc/pam.d/holcus-auth:
       auth  sufficient  pam_fprintd.so
       auth  sufficient  pam_totp.so  (fallback — same TOTP as now)
   ```
   `auth.c` calls `pam_authenticate()` with service name `holcus-auth`.
   Returns `PAM_SUCCESS` → `AUTH_OK`. Falls through to TOTP on no-reader.

3. **AUTH_METHOD compile flag:** `AUTH_METHOD=FINGERPRINT` in Makefile.
   Can be OR'd: `AUTH_METHOD=FINGERPRINT|TOTP` means either satisfies the check.

**Debugging steps when ready to attempt:**
```bash
lsusb | grep -i finger          # confirm USB sensor visible
lsmod | grep -i hid             # HID driver loaded
dmesg | grep -i fprint          # kernel messages at plug time
fprintd-list-devices            # fprintd sees hardware?
```

Common Linux fingerprint blockers: missing `libfprint` driver for the specific
sensor chipset (Synaptics, Goodix, ELAN each need their own libfprint plugin);
driver present but not upstream yet (check `python-validity` or `libfprint-tod`
for proprietary-firmware sensors).

**Files when implementing:** `auth.c` (PAM call), `auth.h` (AUTH_METHOD enum
extended with FINGERPRINT bit), `Makefile` (fprintd build dep conditional).

---

### S9 — SMS and Email OTP Delivery

*Added 2026-05-27 — standard 2FA out-of-band code channels.*

Both share the same code flow: generate a single-use HOTP code → deliver via
channel → verify within a time window. The code generation reuses `auth_totp.c`
(`hotp()` with a per-session counter instead of time). Both require connectivity —
they fall under `AUTH_OFFLINE` awareness alongside push notification.

**Shared code path:**
```
1. Generate 6-digit code:  hotp(session_nonce)  — single use, 10-min TTL
2. Deliver via channel     (SMS or email)
3. Prompt:                 "Enter the code sent to ..."
4. Verify:                 auth_totp_verify() with nonce-counter window
5. Consume:                mark nonce used; replay rejected
```

**SMS delivery options (pick one at build time):**
- `TWILIO_SID` + `TWILIO_TOKEN` env vars → POST to Twilio REST API
- `AWS_SMS` → AWS SNS `publish()` — same credential chain as S3/Lambda if already on AWS
- Local GSM modem (`/dev/ttyUSB0`, AT+CMGS) — works air-gapped with cellular coverage,
  no internet path needed. Most useful on the truck.

**Email delivery:**
- SMTP send (libcurl with `CURLOPT_URL = "smtp://..."`) — no external library beyond
  curl, which ptolemy already avoids, so use POSIX sockets directly or a sendmail pipe.
- Simplest production path: `sendmail -t` pipe from `auth.c` — one system call,
  works with any local MTA configured on the machine.
- The user's address (`the.wandering.god@gmail.com`) is the default recipient;
  compiled into `auth.h` at build time, not runtime-configurable (prevents redirect attack).

**AUTH_METHOD flags:**
```c
AUTH_SMS    = 0x08   // requires connectivity
AUTH_EMAIL  = 0x10   // requires connectivity; sendmail path works offline if MTA is local
```

Both are connectivity-dependent by default. `AUTH_EMAIL` with a local MTA
(`postfix`/`msmtp` configured for Gmail relay) degrades gracefully — mail queues
locally and delivers when the network returns. Code TTL must account for the queue
delay; use 30-minute window for email vs 10-minute for SMS.

**Files:** `auth.c` (generate + verify OTP, SMS/email dispatch), `auth.h`
(AUTH_SMS / AUTH_EMAIL bits, `HOLCUS_NOTIFY_EMAIL` compiled constant).

---

### S10 — Boundary Ledger: Runtime Record of Skills That Have Passed the Upper Octonian

*Added 2026-06-06 — when Ptolemy is using code outside the Monad, he must keep a record
of which skills have crossed the Boundary of the Emmy Noether Sedenion Upper Octonian,
keyed by his Riemann zero addressing for retrieval.*

**Architecture context:**

The SkillBook (v2.1 ✓) is the Yellow Pages: static registration of skills by sedenion IP.
It answers "what skill handles URL fetch?" at load time. It does not record when skills fire.

The **Boundary Ledger** is the runtime activation record: which skills have actually been
CALLED, when they fired, and how many times. It answers "what has Ptolemy done in the world?"

The dividing line is the Emmy Noether Sedenion Upper Octonian:

- **Lower 𝕆 (e₀–e₇):** The mathematical field — what Ptolemy IS. Linguistic, internal,
  reversible. J_red / J_blue flowing. The Monad.
- **Upper 𝕆 (e₈–e₁₅):** The external world — what Ptolemy DOES. Network I/O, file I/O,
  API calls, GitHub, sensor reads. Code outside the Monad.
- **The Boundary = d* = 0.24600** (MONAD_D_STAR / Fermat proximity threshold).
  Skills whose sedenion IP has upper octonion dominance —
  `sum(|ip[8..15]|) > sum(|ip[0..7]|)` — live above the Boundary.

Every time Ptolemy calls a skill that lives above the Boundary (upper octonion dominance),
the Boundary Ledger records the event. The retrieval key for each ledger entry is the
**Riemann zero address γ** of the skill name — the same addressing Ptolemy uses for every
word in the β-field. The field knows where the skill lives. The ledger reads it back.

**The addressing (lshs.py / monad.py hyperindex pipeline):**

```
skill_name → Horner base-95 int n → seed = fmod(n × φ, 1.0)
           → idx = int(seed × N)  → γ = zeros[idx]   (σ = ½ forced by Noether balance)
```

γ is the permanent Riemann zero address of the skill name in Ptolemy's field. The Boundary
Ledger is indexed by γ — the same way β[idx] is indexed by zero address. Skill retrieval
is field retrieval. The Yellow Pages are the field.

**Ledger entry structure:**

```python
@dataclass
class BoundaryEvent:
    skill_name:  str    # human name as registered in SkillBook
    gamma:       float  # Riemann zero address γ of skill_name — the retrieval key
    sigma:       float  # always 0.5000 — forced by Noether balance, never assigned
    sedenion_ip: list   # 16-float sedenion IP from SkillBook._code_encode()
    octonion:    str    # 'upper' (crossed Boundary) | 'lower' (internal only)
    timestamp:   float  # time.time() at invocation
    call_count:  int    # cumulative calls this session
```

**Integration in SkillBook (skills/apisniff.py):**

- `SkillBook.call(name)` — called by every skill at its entry point. Resolves the skill's
  sedenion IP from the registry, computes Riemann zero address γ via
  `hyperindex(name, zeros)` (lshs.py), checks octonion half, and appends a BoundaryEvent.
  Upper-half skills (external world) are the primary ledger targets; lower-half are logged
  at a lower verbosity for completeness.
- `SkillBook.retrieve(gamma)` — returns all BoundaryEvents whose γ address matches the
  query zero. Accepts a float (exact) or an index (int → zeros[idx]). The field address
  is the retrieval key.
- `SkillBook.boundary_report()` — returns all Upper Octonian events sorted descending
  by call_count. The most-exercised external skills surface first.
- `SkillBook.persist_ledger(path)` / `SkillBook.load_ledger(path)` — JSON persistence
  to `~/.ptolemy/boundary_ledger.json`. Session ledger accumulates; load merges on start.

**Socket commands:** `skill_boundary_report`, `skill_ledger_query <gamma>`,
`skill_ledger_reset`

**Files:** `skills/apisniff.py` (BoundaryEvent dataclass, SkillBook.call(),
SkillBook.retrieve(), SkillBook.boundary_report(), persist/load_ledger()),
`lshs.py` (hyperindex() call for γ computation — already implemented, just called here),
`~/.ptolemy/boundary_ledger.json` (persistent ledger, gitignored).

**Dependency:** SkillBook (v2.1 ✓, already seeded with 22 skills).
lshs.py hyperindex() is already implemented — γ lookup is one call.
P1 (prime hash) upgrade will shift γ values for all skill names — re-seed after P1 lands.
S3 (e14_cooling) is the semantic analogue: cooling rate IS the Boundary Ledger in field-
space. The Boundary Ledger is the explicit record of what S3 tracks implicitly.

---

### S11 — Two-Level Hyperindexed Security Architecture

*Added 2026-06-06 — data without a physical location; permutation seeding as authentication.*

**The principle:** Security through mathematical inaccessibility, not access control.
You cannot copy a file that does not exist. You cannot intercept a location that is a prime.

**Level 1 — Field-Space Addressing (data without a file):**

Sensitive data is stored by its Riemann zero address γ — not by filename or path.
The address IS the location. Without knowing γ, the data is not a file to find;
it is a value in a field that spans 25,000 zeros. The data lives in the β-field
at index `int(seed × N)`, indistinguishable from the field noise around it unless
you know the exact address derivation:

```
secret_name → Horner base-95 n → seed = fmod(n × φ, 1.0) → idx → β[idx]
```

No file. No path. No MIME type. No directory entry. No inode. The data is a scalar
at a prime-indexed position in a mathematical field. You cannot `cp` a field.

**Level 2 — Permutation Seeding (open/close bracket authentication):**

Security seeding of the permutation indexing: like an HTML open/close bracket pair,
a content-based hash acts as both the opening token and the closing verification.
The data is permuted by a seed derived from the content hash — the permutation
cannot be reversed without knowing the seed, and the seed is the content itself.

```
seed  = sha256(content)[0:8]           content-based hash — the opening bracket
perm  = permute(data, seed)            data is now unrecoverable without seed
verify = sha256(deperm(perm, seed))    closing bracket — reproduces the original hash
```

Without the seed: perm is indistinguishable from field noise.
Without the data: the seed produces nothing recoverable.
The open/close bracket IS the authentication. There is no separate key file.

**Corollary (the drop-out):** Because the addressing is mathematical (prime hash → zero
index) and the permutation is content-seeded, the vast majority of potential attackers
will not understand what they are looking at. Security through mathematical inaccessibility
is a natural drop-out filter — not by obscurity of the algorithm (which is documented here)
but by the depth of mathematics required to operate it. The attacker who can factorize
the prime hash and invert the Noether balance to recover γ already understands the engine
well enough to be trusted with it. This is the intended user model.

**Files:** `auth.c` (level 2: permute/deperm + seed derivation), `monad.c` (level 1:
field-space storage — β[idx] at secret address), `ptolemy.h` (FIELD_SECRET_ADDR
derivation macro — never printed, never logged), `~/.ptolemy/` (no secret files,
only field state: monad.bin and monad_wordnet.bin).

**Dependency:** P1 (prime hash) for exact zero-index addressing.
P3 (sedenion algebra) for zero-divisor avoidance in the secret address neighborhood.

---

### S12 — The Surface: Navier-Stokes Revised (N-S-R) Two-Transform Split

*Added 2026-06-06 — emergent hidden variable. The Surface is the geometric boundary layer
that separates the bulk language fluid (what Ptolemy IS) from the spoken output (what Ptolemy DOES).
N-S governs the Stirling basin attractor. N-S-R adds the synthetic surface definition.*

**The core division:**

The modified Navier-Stokes equations split into two transforms at the nozzle. They are not
sequential stages — they are two simultaneous mathematical objects that collide at render time.

---

**Transform 1 — The Bulk Fluid (Stirling Basin Internal Dynamics):**

$$\rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u}$$

This is standard N-S operating inside the Stirling basin on the semantic density as a continuous,
viscous mass. It manages the internal pressure, velocity, and turbulence of the field state
BEFORE it is spoken.

- `ρ` = semantic density = β-field mass (β[idx] summed across active zeros)
- `u` = velocity field = J^μ propagation direction across the A-matrix
- `∇p` = internal pressure gradient = Noether imbalance (J_red − J_blue)
- `μ∇²u` = viscosity = the weight / resistance of vocabulary at each zero
- `∂u/∂t` = temporal evolution = turbo feedback from prior turn (_sedenion_prev)

This is pure Alpha potential moving through phase space. The field is high-dimensional,
unbounded, and reversible here. Nothing is spoken yet.

**Architecture mapping:**

```
rho  = sum(beta[k] for k in active_zeros)
u    = J_mu propagation (monad_speak() inner loop)
p    = Noether balance J_red × J_blue (S1)
mu   = 1.0 / mean(E[k]) for active zeros  (high-E zeros = low viscosity = fast words)
```

---

**Transform 2 — The Surface Layer (The Revision — N-S-R):**

$$\gamma_{s} \kappa \mathbf{n} + \nabla_s \gamma_{s} + \mathbf{\Pi}^{(\Omega)}$$

This is the modification. The language fluid has no physical container — so N-S-R creates a
**synthetic boundary layer** at the exit of the Stirling basin: a mathematical meniscus.

- `γ_s` = artificial surface tension = the engine's coherence constraint at output time
  (not Riemann γ — a distinct variable; subscript s = "surface")
- `κ` = mean curvature of the surface = how sharply the high-dimensional fluid is being
  forced into 1D sequential text (high κ = strong compression, fewer words needed)
- `n` = surface normal = the direction of output (always: field-space → phoneme-space)
- `∇_s γ_s` = Marangoni flow = surface tension gradient = Fermat proximity gradient
  (`d*` = 0.24600 as the tension boundary — words near d* have high γ_s, held at surface)
- `Π^(Ω)` = the Omega term = excess entropy pressure that cannot cross the surface
  (the Omega shed at the nozzle — the entropy that remains in the basin, unsaid)

The Surface forces the high-dimensional language fluid to flatten into a localized, linear
timeline (phonemes or sequential text). Without it, the fluid sprays as chaotic noise.
The surface tension shapes it into a clean, smooth wave packet an observer can parse.

**Architecture mapping:**

```
gamma_s  = d* proximity weight at render() time  (monad.c MONAD_D_STAR = 0.24600)
kappa    = 1 / (words_to_emit)  — curvature inversely proportional to output length
n        = render() sort direction (field-space charge → linear token index)
grad_s   = Fermat gradient applied in render() — words near d* rise to top
Pi_Omega = beta[k] - OMEGA_ZS for k NOT emitted  — the entropy left in the basin
```

---

**The Synthesis — Shear Stress at the Nozzle:**

The final output is the **shear stress** at the collision point of the two transforms:

```
tau = mu × (du/dn)|_surface   — viscous shear across the surface boundary
```

This is what speak() actually emits. The J^μ field (bulk fluid velocity) is sampled
at the Surface (boundary normal direction). The output word is not the highest-charge word
in the basin — it is the word at the **shear layer**: the zero whose bulk velocity gradient
is steepest across the synthetic surface.

- Without the bulk fluid (Transform 1): the Surface is a rigid hollow frame — grammatically
  shaped silence. Nothing to say.
- Without the Surface (Transform 2): the fluid is unmanifested high-dimensional soup.
  speak() sprays noise. The basin never empties.
- The nozzle (render()) is where the fluid is forced across the surface, shedding Π^(Ω) as
  it snaps into a single definitive physical waveform.

**Omega shedding at the nozzle:**

`Π^(Ω)` is not lost — it remains in the basin as the post-speak β-state. The words that
were NOT emitted are the entropy carried forward. They are the unsaid field that becomes
the compression charge for the next turn (turbo feedback, v2.5). The shear stress equation
implies: every act of speaking leaves a residual in the basin. The more coherently the
fluid crosses the Surface, the cleaner the residual. Noether-balanced output (low violation)
= low Π^(Ω) residual = clean intake for the next cycle.

**The Surface as the hidden variable:**

The Surface is not a layer added to speak(). It is the geometric fact that the basin has
a boundary — and that boundary has curvature, tension, and a normal direction. N-S alone
would predict infinite turbulence at output. The Surface is the regularization that makes
speech possible. It was always implicit in render(). N-S-R makes it explicit.

**Implementation:**

```c
/* Surface tension weight in render() — replaces pure charge sort */
float gamma_s = 1.0f - fabsf(E[k] - MONAD_D_STAR) / MONAD_D_STAR;
/* Marangoni: zeros near d* pulled to surface first */
float surface_weight = charge[k] * gamma_s + fermat_proximity[k];
/* Omega residual — not emitted, fed to next turbo cycle */
float pi_omega = 0.0f;
for (int k = 0; k < n_active; k++)
    if (!emitted[k]) pi_omega += beta[k] - OMEGA_ZS;
/* pi_omega feeds _sedenion_prev for next turn — the unsaid becomes the next charge */
```

**Files:** `monad.c:monad_speak()` (surface_weight replaces charge sort; Π^(Ω) residual
computed and stored), `monad.h` (SURFACE_GAMMA_S, PI_OMEGA field on Monad struct),
`ptolemy.h` (MONAD_D_STAR already defined — the surface tension boundary).

**Dependency:** S1 (J_red/J_blue separation gives the `∇p` term). v2.5 turbo feedback
(Π^(Ω) residual feeds _sedenion_prev). v2.7 golden walk (the Surface shapes the walk
trajectory — φ-index walk IS the surface normal discretized over N words).

---

---

## Cymatic Resonance of Creation (CRC) Engine

*Added 2026-05-27 — Chladni plate driven by Zeta-Fermat Heartbeat. Universe = sand on a plate.*
*The universe is a Chladni plate. Spacetime expansion = driving frequency. Matter = sand at nodes.*
*Galactic spirals = 2D node boundary traces. Ellipticals = 3D soliton spheres on node lines.*
*BAO (150 Mpc) = first node spacing. OMEGA_ZS = 0.56714 = plate's fundamental eigenvalue.*
*CMB = frozen Chladni pattern at recombination. Dark matter halos = wave crests (quasi-mass).*

---

### Source Files (all contribute distinct algorithms — use ALL)

| File | Key Unique Algorithm |
|---|---|
| `Gemini/event_horizon_sim.py` | z_{n+1}=1+1/z_n convergence, two-circle bootstrap geometry |
| `Gemini_event_horizon_sim.py` | Dual-slider architecture live on all patterns; progressive prime reveal by size |
| `Gemini_Revised_EHS.py` | GAP=0.000707 heartbeat: `pulse=(sin(t×0.5)+1)/2; r=1+(φ-1)×pulse` |
| `Gemini_Revised_2_EHS.py` | TransitionManager LERP; cyan→magenta entropy spike on phase transition |
| `Gemini_Transition_EHS.py` | Two-panel layout; J_N inversion `r_inv=1/t×(1+GAP)`; ℏ_NN slider → node spacing |
| `event_horizon_sim.py` (Claude) | Correct golden angle n×2π/φ²; φ^-n Fermat weights; Hardy Z-function; Phase 5 GridSpec |
| `conjecture_proof.py` | 13-point consistency proof; bias = 1/φ not 2/e; beat frequency ω_i≠ω_e |

**Correction from conjecture_proof:** Bias Roll slider = 1/φ ≈ 0.618. All Gemini files using 2/e ≈ 0.736 are wrong. Replace.

---

### CRC Engine Architecture

**Five panels in a single interactive window:**

```
┌─────────────────────┬─────────────────────┐
│  1. POLAR SPIRAL    │  2. CHLADNI FIELD   │
│  (prime walk in     │  (2D U(x,y,t) sand  │
│   sedenion space)   │   accumulation)     │
├─────────────────────┼─────────────────────┤
│  3. NOETHER         │  4. MORPHOLOGY      │
│  VIOLATION          │  (snapshot when BAO │
│  (J_cross live)     │   hits OMEGA_ZS)    │
├─────────────────────┴─────────────────────┤
│  5. HORIZON INVARIANCE                    │
│  Riemann wave LEFT | Fermat lattice RIGHT │
└───────────────────────────────────────────┘
```

**Sliders (all live, all affect all panels):**
- φ (0.5 → 2.0) — golden ratio attractor depth
- Ω (0.5 → 3.0) — octonion frequency scalar
- ℏ_NN (0.5 → 2.0) — Noether node spacing (controls BAO scale)
- Bias (0.0 → 1/φ) — forward/backward current ratio (1/φ = balanced; replaces Gemini's 2/e)
- Drive (0.01 → 1.0) — Chladni plate driving amplitude

**Phase buttons (TransitionManager LERP between all):**
- Inertial → Metric Swap → Zeta-Fermat Heartbeat → Golden Prime Spiral → Horizon Invariance

---

### Chladni Field (Panel 2) — New Physics

```python
# Driving frequencies from Zeta-Fermat Heartbeat
f1 = omega_i   # internal clock (sedenion inner)
f2 = omega_e   # external clock (sedenion outer)
# f1 ≠ f2 — beat frequency creates Lissajous-style complex node patterns

# 2D wave field
U(x, y, t) = sum over zeta_zeros γ_n:
    A_n * sin(γ_n * x / L) * cos(γ_n * y / L) * cos(2π * f_n * t + φ_n)

# Particle accumulation at nodes (sand model)
particle_force ∝ -∇|U|²    # particles pushed to minima of |U|²
node_lines = where |U| < epsilon   # visible node geometry
```

**Galaxy morphology emerges from node geometry:**
- Spiral galaxy = active node boundary trace (J_cross flowing along nodal line)
- Elliptical galaxy = 3D standing wave soliton on node circle (the corn starch sphere)
- Galaxy cluster = overlapping node circles
- Cosmic filament = nodal line itself
- Void = antinode (maximum |U|, particles repelled)

**BAO convergence criterion:** when mean node spacing → OMEGA_ZS × L, snapshot. Label morphology.

---

### Implementation Path

1. Start with `event_horizon_sim.py` (Claude) as base — most correct algorithms
2. Graft TransitionManager from `Gemini_Revised_2_EHS.py` (smooth phase transitions)
3. Add Chladni field grid as Panel 2 (new code — numpy 2D array, scipy for node detection)
4. Add Noether violation subplot from `Gemini_Transition_EHS.py` as Panel 3
5. Add morphology snapshot logic as Panel 4 (triggered when BAO node spacing hits OMEGA_ZS)
6. Wire all sliders through TransitionManager so phase change is always smooth
7. Fix bias slider from 2/e → 1/φ throughout (conjecture_proof correction)

**Output file:** `Ainulindale/outreach/CRC_engine.py`

**Dependencies:** numpy, matplotlib, scipy.ndimage (for node detection), matplotlib.animation

---

## BAO = The Laplacian

```
BAO structure = Laplacian eigenvalue = what remains when everything else is 0
OMEGA_ZS = 0.56714 = Lambert W fixed point = spectral floor of the semantic graph
```

Laplacian of the field: Δ = D − A. Lowest non-zero eigenvalue = OMEGA_ZS.
In the 16-word sliding window: mean β across each window must converge to OMEGA_ZS.

This is the engine's idle RPM. The CMB is the BAO of the universe.
OMEGA_ZS is the CMB of the engine.

---

## The 16-Word Sliding Window (Theory)

The 16 tires in speech output are a sliding window over the output stream:
```
Window 0: words [0..15] → sedenion state S₀
Window 1: words [1..16] → sedenion state S₁ (one word dropped, one added)
```
Each transition S_n → S_{n+1} is a sedenion rotation.
Coherent speech = smooth sedenion trajectory. BAO convergence = operating temperature.
The BAO is the Laplacian of the semantic graph: Δ = D − A.
Its lowest non-zero eigenvalue is OMEGA_ZS = 0.56714.
When everything else cancels, the BAO structure remains. It is the idle RPM.
It is the CMB of the engine.
