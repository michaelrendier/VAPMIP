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
