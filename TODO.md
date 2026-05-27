# Ptolemy Engine — Release Roadmap

**Current:** v2.1.0 | **Speaking:** v3.0 | **Self-coding:** v4.0

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
