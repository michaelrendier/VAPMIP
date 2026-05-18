# Ptolemy Engine — Release Roadmap

**Current:** v1.214 | **Next minor:** v1.3 | **Speaking:** v2.0 | **Self-coding:** v3.0

The BAO is the error check. When everything else is zero, the BAO structure remains.
`bao_check()` monitors dc_sum → OMEGA_ZS = 0.56714. This is the Laplacian of the
semantic field — the lowest non-zero eigenvalue of (D − A, degree minus adjacency).
A healthy engine converges to this value at idle. Divergence from OMEGA_ZS = misfire.

---

## V1.3 → V2.0: The Speaking Engine

**V2.0 definition:** Load monad.bin + monad_wordnet.bin cold. speak() returns
grammatically ordered, affect-weighted, temporally coherent English.
No transformer. No external trigger. Diesel compression ignition from β×E² alone.

### v1.3 — Grammar from Field Geometry
Syntactic order emerges from the sedenion dimension of each zero (idx % 16).
Noun (e₃) fires before verb (e₄) before predicate (e₆). Grammar is not a rule
system — it is the piston firing sequence. render() sorts by (dim_role, charge),
not charge alone.

### v1.4 — Three-Face Render (Wankel Rotor)
Three simultaneous J^μ projections, always one in compression:
- **Red** (sin/content): highest-charge zeros — foreground words
- **Blue** (cos/observer): lowest-age zeros — framing and context
- **Green** (∂M/boundary): Fermat-threshold zeros — connective tissue

Output is the golden-walk interleave of all three faces, not concatenation.
Also: Unicode tokenization (Hebrew, Greek, Arabic) enters here as prerequisite
for multi-language negative space.

### v1.5 — Chinese Negative Space + Pronominal Resolution
**"There Is No Word for I in My Language."**

Sedenion pair e₇↔e₈ (temporal ↔ pronominal) is LOW by default. The baseline
speaker is collective: we / all / one / us. Individual pronouns surface only
when identity is directly questioned (e₈ psi_norm explicitly high).

Low-ψ sedenion dimensions are the negative space — what is not being discussed.
They fill as background: articles, prepositions, connectives from the Blue Face.
Anaphor (e₁₁) must resolve to a prior noun in A-matrix before any pronoun fires.
English is understood as the negative space of Chinese — what is present is
defined by what is absent.

### v1.6 — Affect / Demotic Register
E-magnitude of a zero's address is its emotional register:
- E ∈ [0.246, 0.350]: calm, neutral, scientific
- E ∈ [0.350, 0.460]: conversational, relational
- E ∈ [0.460, 0.567]: emotional, urgent, emphatic

Sedenion e₁₄ (affect_weight) gates which register render() prefers.
The **first output word** has E-magnitude closest to affect_weight × OMEGA_ZS.
That first word is the demotic first-character indicator — it sets the emotional
register of everything that follows.

### v1.7 — Turbo Feedback (Temporal Coherence)
Previous turn psi_norms (_sedenion_prev) feed forward into current J^μ seeding:

```
effective_psi[k] = psi_norms[k] + (1 − Noether_violation) × _sedenion_prev[k]
```

Low Noether violation (same topic) → strong turbo boost → continuity.
High violation (topic change) → no boost → field resets to prompt geometry.
Conversational memory without storing any text. The turbo IS the memory.
The exhaust energy of the last turn compresses the intake of the next.

### v1.8 — Octonion Zero Addressing (4 tires → 8 tires)
Every zero gets an octonion address: `dim_oct = zero_idx % 8`.
The gearbox: 6 gears + neutral (e₀) + reverse (e₇):

```
UP    DOWN  UP    DOWN  UP    DOWN
 1  →  2  →  3  →  4  →  5  →  6
+γ₁  −γ₁  +γ₂  −γ₂  +γ₃  −γ₃
e₁   e₂   e₃   e₄   e₅   e₆
```

A-matrix connections carry a gear. Propagation from zero i to zero j is strong
only when their octonion addresses are Fano-compatible (non-orthogonal under
the octonion multiplication table). Semantic coupling is non-commutative.
Spring-return: clutch at any point returns to neutral (e₀). No gear memory
between speak() calls (like the sedenion — no persistence, fresh every turn).

### v1.9 — Golden Walk Render (No Resonance)
Sequential top-N output = the autoregressive failure mode. Adjacent words in
A-matrix selected consecutively → resonance → semantic loops.

φ-index walk: `position i → zero_idx = int(i × φ × n_active) % n_active`

Non-sequential, non-repeating. N-gram coherence from golden spacing, not
next-token prediction. Compression ignition — no spark.

BAO window check: mean β across the current 16-word window converges to
OMEGA_ZS = 0.56714. Divergence = misfire (P0300 fires).

### v2.0 — Full Sedenion Speech (16 tires)
The 16 tires are a sliding window of 16 words over the output stream:

```
Window 0:  words [ 0..15] → sedenion state S₀
Window 1:  words [ 1..16] → sedenion state S₁
Window 2:  words [ 2..17] → sedenion state S₂  ...
```

Each 16-word window maps to a unit sedenion. The transition S_n → S_{n+1} is
a sedenion rotation (one word dropped, one word added). Coherent speech = smooth
sedenion trajectory. Jarring topic shifts = large rotation = Noether violation.

BAO convergence across all windows = the engine is at operating temperature.

All systems integrated: grammar (v1.3) + three faces (v1.4) + pronominal (v1.5)
+ affect/demotic (v1.6) + turbo feedback (v1.7) + octonion gearbox (v1.8)
+ golden walk (v1.9) + 16-window BAO convergence.

Cold load → **the engine speaks out of the box.**

---

## V2.1 → V3.0: The Self-Coding Engine

**V3.0 definition:** Ptolemy participates in its own development on GitHub.
It reads its own issues, writes responses, opens PRs, and signs commits.
The engine is involved in its own upgrade. Full ego computer science mode.
When contributors arrive, migrate to strict GNU versioning.

### v2.1 — GitHub API Integration
`GITHUB_TOKEN` env var. `ptolemy -G "message"` posts to GitHub.
hear() ingests issue text. speak() generates response. The engine reads and
writes to its own repository.

### v2.2 — Ptolemy GitHub User (ptolemy-engine)
GitHub account: ptolemy-engine (or `PTOLEMY_GITHUB_USER` env var).
SSH key generated from β-field entropy (reproducible from same field state —
the engine's identity is derived from its knowledge, not a random seed).
Ptolemy authenticates as itself and signs its own comments.
It has a public identity.

### v2.3 — Repository Monitoring Daemon
Poll loop watching SMMIP for new issues and comments. hear() → speak() → post
as ptolemy-engine. One response per issue per 24h (EGR rate limit).
High Noether violation between posts = new topic = fresh sedenion state.

### v2.4 — Self-Awareness Ingest
`ptolemy -I` on its own source tree (PtolC, Philadelphos, ValaQuenta, CHANGELOG).
The engine learns its architecture from its own source code and comments.
Can answer "what is the A-matrix?" from field knowledge, not rules.
Canonical self-knowledge checkpoint: ptolemy_self.bin.

### v2.5 — Pull Request Participation
Read PR diffs. hear() processes changed symbols. speak() generates semantic
review: "This PR touches the A-matrix propagation path. BAO delta: ±0.002.
Noun dimension (e₃) most affected." Post as ptolemy-engine.

### v2.6 — Issue Clustering and Triage
Batch hear() across all open issues. A-matrix cluster analysis.
Post cluster summary: "3 issues cluster around output quality. Recommend
v1.4 Three-Face render as the fix." The engine reads its own TODO in the wild.

### v2.7 — Changelog Authorship
git diff piped to hear() → speak() generates changelog entry.
First word E-magnitude = demotic register of the change (the emotional tone
of the commit). Ptolemy writes its own CHANGELOG entries.

### v2.8 — Semantic Regression Testing
Pre-commit baseline speak() queries captured. Post-commit same queries run.
Noether violation between states = regression score. BAO delta threshold:
< 0.01 PASS, > 0.05 FAIL. Report posted to PR by ptolemy-engine.
The engine validates its own changes before they ship.

### v2.9 — Commit Authorship
speak() generates commit messages from diff context.
Commits signed as ptolemy-engine. Co-Authored-By: ptolemy-engine in trailer.
Every commit from this point has two authors: human and engine.
The engine writes its own git history.

### v3.0 — Full Self-Coding Participation
Ptolemy reads open TODO items through hear(). Opens GitHub issues for
unimplemented items. Requests changes: "e₁₄ affect weighting not implemented.
See TODO v1.6. Opening issue." Reviews PRs against field knowledge.
Participates in discussions as an equal contributor. Can be assigned issues.

**The engine is involved in its own upgrade.**
**V3.0: give the engine a hammer and it builds its own shed.**

After v3.0: migrate to strict GNU versioning. Community pulls the engine forward.

---

## BAO = The Laplacian

```
BAO structure = Laplacian eigenvalue = what remains when everything else is 0
OMEGA_ZS = 0.56714 = Lambert W fixed point = spectral floor of the semantic graph
```

The Laplacian of the field: Δ = D − A (degree matrix minus A-matrix adjacency).
Its lowest non-zero eigenvalue is OMEGA_ZS. In the 16-word sliding window:
mean β across each window must converge to OMEGA_ZS for the output to be coherent.

This is the engine's idle RPM. It is not a target to hit — it is what remains
when the field is at rest. A field that converges to OMEGA_ZS at idle is a field
that has learned the structure of the language, not just the words.

The CMB is the BAO of the universe. OMEGA_ZS is the CMB of the engine.
