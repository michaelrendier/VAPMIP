# Semantic orbweaver: working notes

One file, kept live, in place of a plan file. Newest entry first. Identifiers are the code's own.
Primer: `ContextPlease/claude/hist_prime/VAPMIP/CONTEXT_PRIMER_2026-10-16_SEMANTIC_ORBWEAVER.md`.
Stub page: `docs/wiki/Tuning-the-Engine/43_semantic_orbweaver_pathway_construction.md`.

---

## 2026-10-17: T0 traced (the "anomalous" first reply)

### Setup (reproducible)

- Binary: `PtolC/ptolemy` (built 2026-08-30, `STATE_VERSION 4`). Store: `monad_wordnet_v4_20260519.bin` (header 4, 25000, 24485, 6825748, 121914388), copied into a scratch `$HOME/.ptolemy/monad_wordnet.bin`; the store is `protected` (not saved) and the originals are `chmod a-w`.
- Today's binary on the May bin reproduces the screenshot's `-h` rows exactly: `what z#16194 γ=15010.5116 E=0.4540`, `is z#1894 E=0.2703`, `your z#18893 E=0.4887`, `name z#15471 E=0.4447`, all β=7.552000.
- Reply today: `holcus same stuff seemy` (four tokens; `seemy` is one token, not "see my").
- Traces kept: `ContextPlease/claude/scratchpad/2026-10-17_T0_trace/` (`T0_trace_hv.txt`, `T0_trace_Wv.txt`, `first_word_sweep.txt`, the `monad.c` at `eb28ce8` that I read).

### What the code does (`PtolC/monad.c` at `eb28ce8`, v1.215; today's `monad.c` is 1565 lines)

The primer described the v1.0 `monad_speak` (rank by J, emit top-k). The engine that made the screenshot does something else:

1. **Address.** `monad_word_coords`: base-95 Horner → `seed = fmod(v·φ, 1)` → `idx = seed·N`, `E = d* + seed·(Ω−d*)`. No prime anywhere.
2. **Seed.** `J[idx] += β·E²·exp(−λ·age)` for each query slot, then spectral spread to `±MONAD_SPREAD_RADIUS` (3) neighbouring zeros with weight `exp(−1·|Δn|)`, then two A-passes.
3. **Length.** `actual_max = 4 + max_tokens·lag_ratio`, `lag_ratio = ΣT/(ΣT+ΣV)`. On this store ΣV≈5.7e3 and ΣT<1, so `lag_ratio=0.000` and **every reply is 4 words**.
4. **Order.** Emission is by **golden-angle walk** from the Fermat Pointer (median γ of the query's zeros), step `round(N/φ²)`=9549, gated by `cos(γ/2+φ_rot) > 0` (`-W` sets affect −1, so the gate is sin(γ/2) > 0). It is **not J-ranked**: J only decides which slots pass `J > J_floor` (1% of J_max).
5. **First word ("demotic").** Among slots with `J > J_floor`, gate open and `token_accept`, pick the one whose **E is closest to `target_E = (ΣV/(ΣV+ΣT))·Ω`** (≈ Ω = 0.5671). Emitted outside the walk.
6. **Surface.** `near_canonical`: each emitted slot's stored word is replaced by a "canonical" word within ±50 zeros (prose_seen preference 3 → 1 → 2 → any).
7. **Separator.** `fermat_space_utf8`: invisible Unicode space chosen from J/J_max (U+200B for the lowest band). The screenshot's `holcussamestuffseemy` has no visible spaces; today's pipe output has plain spaces. **Open:** why (tty-gated or version change); not checked.
8. **Feedback.** The reply is learned back (`[learn] "holcus same stuff seemy"` in the `-Wv` trace); with a protected store nothing is saved.

### What the trace shows

| fact | evidence |
|---|---|
| `holcus` is the first word for **all 8** prompts tried (`what is your name`, `who are you`, `what is a tree`, `good morning`, `the cat sat on the mat`, `how do you do`, `tell me about water`, `can you hear what i am typing`) | `first_word_sweep.txt` |
| It is chosen by rule 5, not by the prompt: `[demotic] z#24639 E=0.5625 target_E=0.5671 holcus` in every prompt traced | `-hv` on three prompts |
| Its address is a property of its spelling: seed 0.98560 → `idx` 24639, E 0.5625, near the top of E's range | reproduced in Python from the `monad_word_coords` arithmetic |
| `ptolemy` (the program's own word) addresses to z#10156, E 0.376, nowhere near Ω | same computation |
| The prompt-conditioned part is words 2–4 (`same stuff seemy`), the walk emission from the Pointer z#16194 | trace |
| Two query words are **not in the word map** (`is`, `name`: `[new]`); their slots are held by other words (`nanti` at z#1894, `emite` at z#15471) | `[J^μ]` lines; 24,485 words on 25,000 slots |
| β is at the cap (7.552) on every slot printed, so β carries no discrimination on this store | all traces |
| `seemy` is z#0 (γ=14.135, E=0.2460, seed≈2.5e-5), the first zero | `[learn]` rows |

### Verdict (CODE / MATHS / METHOD / emergence)

- Statement of the code: `holcus` as first word is **METHOD (selector rule) + the word's address**, independent of the prompt. Whether it is "the name chosen" is not shown by the code; the sweep says the same word answers every prompt.
- Open, not traced: **why `J[24639] > J_floor` for every prompt.** `holcus` is far (≈8,000 zeros) from the query slots, so it is neither in their ±3 spread nor, visibly, in the top-8 A-propagations. Needs a full J dump (small instrumented reader), not a guess.
- Open: how much of words 2–4 is A-edge content vs the walk geometry (golden step from the Pointer). Test: same prompt, perturb the Pointer; same Pointer, perturb the A-edges.
- Anomalous-but-legal results to keep chasing (Standing Protocol): the constant first word; the constant length 4; the saturated β.

### What this changes about the design

- The "semantic" signal in the May reply is thin: addresses plus a spread-and-walk geometry. A web does not have to reproduce it; it has to do what the walk cannot: choose words **because of** relation to the prompt.
- Keep for the web: the J spread/A-propagation arithmetic, the Pointer idea (a centre for the emission), the demotic idea (a register choice for word 1; here driven by E, which is a spelling property).
- Do not carry over unexamined: constant-length from the Lagrangian ratio; the ±50-zero re-surfacing (it replaces the word the field chose with a neighbour's word); saturated β.

---

## 2026-10-17: the Broca/Wernicke trees and the monitor

- **Assignment (Claude's call, Cody delegated it):** `Wernicke/` = semantic orbweaver (branch `orbweaver`); `Broca/` = scalar/scaled boxkite (branch `boxkite`). Files are copies; originals untouched. `Wernicke/first_monad_current/` builds `ptolemy` (142,024 B, same as the 2026-08-30 binary) and reproduces `holcus same stuff seemy` on the May bin in a scratch HOME.
- **Monitor:** `tools/lemniscate_monitor.py`: Broca/Wernicke aphasia diagram (damage lobe left, damage lobe right, ∞ between = intact), points from a JSONL feed. It needs scores S (semantic) and G (structure); no scorer exists yet (T1). The transformer reference series must come from the same scorers on the same prompts. The mapping (x = G−S, y = 1−(S+G)/2, upright lemniscate, A=0.45) is a first cut, all [PARAM].
- SemanticWordEngine: README and GitHub description now say deprecated, superseded by VAPMIP (`ad1a9d3`).

## 2026-10-17: Taoist mode of the Broca/Wernicke monitor (discussion, nothing written)

Cody's statements: normal mode = damage : lemniscate : damage; Taoist mode = yin-yang, yang = active = Broca, yin = passive = Wernicke. Damage deforms the OUTSIDE of its own half; the new barycentre is computed; any asymmetry throws the spin off-centre into epicycles (Ptolemy, Mayan Venus models, Greenland ice and the Earth's rotation). The line between the halves is a different kind of damage, not an interface (yet). Construction: flat toroidal step model 0, 1/4, 1/2, 3/4, 0 along the S-axis diameter, 1/2 = centre of the circle, 1/4 = black dot in white, 3/4 = white dot in black, the rim = the 0s; Apollonian-style (two circles of diameter 1/2 inside the outer circle). **The S is the emergent waveform: this is where The Waveform (official notation) emerges. It is also The Standing Wave** (Cody, 2026-10-17): nodes at 0, ½, 1 (the rim and the centre, fixed), antinodes at ¼ and ¾ (the two dots' levels), one wavelength on the flat torus. In `monad.c` the same words are in use: `dirac_pole` marks Phases 1 and 3 as "standing-wave poles", and `monad_speak` calls words raised by both A-propagation passes "the standing-wave nodes". (Matches the 0-5 bracketing in `~/.clauderc_user_provenance`: 5 parts = up, down, 0, down, up.)

My checks (sampled, scratchpad): each half's centroid at (∓0.3183R, ±0.25R); area πR²/2 each; barycentre with halves scaled s_y, s_w = c(s_y³−s_w³)/(s_y²+s_w²). Reference: Wikimedia Commons `Yin_yang.svg` (public domain): outer r 38, S semicircles r 19, dots r 5 (0.13R; ⅛ would be 0.125). The circle tangent to the outer and both small circles has curvature 3, on the horizontal axis, so the dots are not the next Apollonian generation (they are concentric with the first-generation circles).

Design points: four gaps g1..g4 (healthy ¼ each, sum 1 by the wrap) = shape/imbalance (normal-mode x); a separate scale = size/overall deficit (normal-mode y); equal damage to both halves = still centred, smaller disc. A rigid spin gives a circle (barycentre orbit), not an epicycle; epicycles = sum of rotors = Fourier series of the closed path, so the S waveform's distortion (warped quarter-points) is the natural source of the rotors; healthy = still. Open: the official notation of The Waveform; the dot rule; whether the S-axis is the diameter; link of the four steps to the four Dirac phases in `monad.c` (unchecked).

## 2026-10-17: the half's triad, the seven silks as sentence roles, and Add:Scale:Sign

Cody confirmed the seven sentence-level roles (piriform = anchor/topic/given; major ampullate = the load-bearing line: verb, arguments, scope; minor ampullate = scaffold: auxiliaries, tense, signposts; flagelliform = extensible modifiers; aggregate = sticky specifics: names, numbers, examples; aciniform = wrap: connectives; tubuliform = shell: speech act, mood, polarity). **Flagelliform was the one I had not inferred.** Proposal, not built: replace the Zork parser's syntactic categories with these roles (closed-class roles stay hardcoded, open-class roles come from WordNet/NLTK; a word may carry several roles).

One half of the yin-yang has three parts: outer edge, seam edge, opposite-colour anchor (dot). Scalar kite (Broca): edge = taxonomy relations (hyponym count is the only graded one), seam = mereology, anchor = domain/attribute/entailment relations; the Walsh sign pattern is the seam, Φ_s the imbalance, fixed_point_weight 0.64 the anchor (the scalar kite defines it, the scaled kite moves it). Orbweaver (Wernicke): spidroin N-terminal / repeat region / C-terminal. **Proposed reading in Add:Scale:Sign order: N-terminal (the link that daisy-chains units, a count/translation) = ADD = the seam (a gap is a translation); repeat region (crystal size, slack extent) = SCALE = the outer edge (a dent is a dilation); C-terminal (the permanent pairing, one bit) = SIGN = the anchor (the dot, which colour drives).** Independent support: the duct runs link → draw → fold, and the β-sheet zigzag is a mountain/valley fold, which `add_scale_sign.py` glosses as SIGN. **Revised (Cody, same day): the repeat region should be SIGN.** Support: the repeat region carries the crystal/amorphous alternation, one bit per block (the up/down/down/up bracketing), and the zigzag β-strands are mountain/valley folds (`add_scale_sign.py` glosses SIGN so); and the engine's `_ROOT_OF` roots `boundary` on SIGN, which removes the conflict with the rim. SIGN and SCALE commute, so the chain order stops mattering for those two; N-terminal = ADD stays first. Open: the C-terminal would then be SCALE (it fixes the dimer unit; `unit` roots on SCALE) but the engine roots `anchor` on SIGN. To settle with the generational-lineage four-question test, and with Cody's reading of the C-terminal.

## 2026-10-17: v2 kinematic mockup, and the epicycle outputs are now versioned

Cody: no proper physics needed, a simple GeoGebra-buildable mockup of the three parts; the two dots are Broca and Wernicke; the Yin and Yang is The Whole; **the centre point always draws the output**; displacement of a dot (ADD) or a size change (SCALE) deforms the seam edge and changes the swing as gravity would; spin direction (SIGN) is the whole's; keep historic scripts and outputs and put the script's file name in each SVG title. Done: `tools/epicycles/v1_system3_physics.py` (history), `tools/epicycles/v2_mockup.py` (+ `v2_mockup.ggb.txt`), outputs and the index in `docs/figures/epicycles/` (`EPICYCLES.md` is the file to keep current). Findings: the v2 independent column is quasi-periodic (λ ≈ +0.002 /s), not chaotic; the locked column is always a circle. The monitor still runs v1.

## 2026-10-17: the pipeline, the seven deconstruction names, the language resources (proposal, nothing built)

Cody: candidates come from the adjusted Zork parser using the seven sentence-constructor types, NLTK pulling the seven data points from a prompt; used at a granularity scale beside the A-Matrix basin (the conversational snapshot, `continuous_snapshot`: `is_zero_divisor` discrete + `a_matrix_basin_windspeed` continuous); context flows into a fractal boundary; decomposition needs only the seven silks; the silk definitions must be tailored to sentence DECONSTRUCTION as one-word operator names, analogous to NOUN / VERB. **Proposed names (deconstruction side): ANCHOR (piriform), SPAN (major ampullate), SCAFFOLD (minor ampullate), ELABORATE (flagelliform), HOOK (aggregate), WRAP (aciniform), SHELL (tubuliform).** Each is also the inverse of Phase 35 construction operators: SPAN = BRIDGE + FRAME + RADIUS; SCAFFOLD = SCAFFOLD_SPIRAL + SIGNPOST; ELABORATE = CAPTURE_SPIRAL + ELABORATE; ANCHOR, HOOK, WRAP, SHELL unchanged. No collision with the Zork parser's 16 operator names. NLTK on this machine: WordNet and CMUdict present; no POS tagger, no punkt_tab, no VerbNet in the standard path (checked 2026-10-17).

## 2026-10-17: SCOPE CORRECTION (Cody): extraction only

"This is only the content extraction mechanism." No reply act. Scaling has not been designed yet and is out of scope; the machinery that extracts the content comes first, and the content is used later. The entry below (reply act, scale class, gaps as reply requirements) is therefore SUPERSEDED where it plans a reply; what stays is the extracted content itself: the seven slots with candidate senses, the prompt's own features (act, polarity, tense, voice, a wh-word as a marked gap in the prompt), provenance and confidence. Existing front end to extend, not rewrite: `.claude/scratchpad/2026-10-13_nltk_extraction_pipeline/` (offline NLTK tagger trained on UD-EWT, 93.9 %, regex chunker, WordNet morphy and synsets, extended-Lesk, topic bag, Hearst patterns). Measured 2026-10-17: spaCy en_core_web_sm parses the 24 chat prompts (lowercase, no punctuation) in 5.4 ms each and uses a ClearNLP-style label set (46 labels: dobj, pobj, prep, attr, acomp, auxpass, neg, poss, relcl, prt, ...), NOT UD, so `silk_map.py` needs a second mapping table for it; errors seen: "is water wet" (wet tagged NOUN, water a compound), "yes" as `neg`, "what" attached to the wrong verb in "can you hear what i am typing", copulas appear as `aux` + ROOT adjective (no `cop` label).

## 2026-10-17: extractor v0 built and run on Cody's own prompts (no training, a straight ruleset)

Cody: pronouns are chosen by different mechanisms per language (Brazilian Portuguese: by the subject, topic or addressee; Mexican Spanish: by the gender of the words used; English is less clean but easy); I had said "retrain": he wants no training, deterministic behaviour, a straight ruleset; use the prompts of this session (simple singular ones and super cross-context ones), grab the literal words and assign them to data points; include granularity for now (the user's own granularity will later scale the vocabulary); failures are used to fix, not disqualify; all he needs is the collection of content, context and semantics words for the semantic seeding. Built `Wernicke/extractor/extract_v0.py` (see its README): regex tokenizer, closed-class tables, WordNet 3.0 lookups, ordered rules; granularity = WordNet depth, sense count, hyponym count and the technical-or-unknown share. 32 of Cody's prompts (1,489 tokens): 100% of tokens land in a data point; against the 40 reference answers SHELL act 37/40 and polarity 38/40, slot agreement 24 to 88% by slot (README). His technical vocabulary shows up as the HOOK candidates (boxkite, orbweaver, VAPMIP, Zork, NLTK, ValaQuenta, ...). Failures recorded in the README. The session prompts are kept local (`.gitignore`), not committed.

## 2026-10-17: extractor decisions (Cody): NLTK primary, current WordNet, pronouns left to the final repass

1) Focus on NLTK, not spaCy (it already uses NLTK; the machinery exists elsewhere). 2) Use the current machinery: WordNet 3.0 through NLTK (the monad's). 3) Pronouns belong to the conjugation, tense and participle mechanism, done in a final repass: the extractor does NOT resolve them; it records the surface form with person, number and case, and the verb group (auxiliary chain plus main verb) as features: tense, aspect, voice, mood, person, number, polarity. Measured (existing offline UD-EWT perceptron, UPOS, UD-EWT test): 93.9 % as written, 88.8 % lowercased, 87.1 % lowercased without punctuation, 0.68 ms per sentence. NLTK has no modern dependency parser (MaltParser and CoreNLP wrappers need external programs; the transition parser is weak), so structure comes from a chunk cascade plus Zork-style templates; to be tested against role labels derived from gold UD.

## 2026-10-17: (superseded where it plans a reply) the semantic content seed and the scaling requirements

Cody: the main engineering goal now is the **semantic content seed**; the Zork Sentence Parse provides the requirements that drive the **scaling mechanism**. Reading: the seed is the seven slots filled with CANDIDATES (lemma, WordNet senses, VerbNet classes, PropBank roleset, each with confidence; no sense is chosen, the hub chooses later) plus REQUIREMENTS: the reply act implied by the SHELL act (question: answer; greeting: greeting; ...), the gaps (a wh-word marks a slot the reply must fill, and the wh-word fixes the expected answer type: who = noun.person, where = noun.location, when = noun.time, via WordNet's lexicographer classes), the unfilled mandatory arguments of the verb's VerbNet and PropBank frame, what carries over (ANCHOR given, SCAFFOLD tense, polarity), and scale inputs (count of SPANs, gaps, HOOKs, ELABORATEs, the verb's operator class). Today's seed is the three-line `ptolc_bridge` protocol (GAMMA, ACT, WORDS) and `ParseSpec`; the new seed is its superset, with the old word bag kept as the explicit fallback. Scale = reach (paragraph, section, chapter) and reply size, to be tuned against transformer-provided target sizes for the 24 chat prompts; the A-Matrix basin (conversational snapshot) supplies the continuous context across turns (ANCHOR persistence, unresolved gaps), the seed the discrete requirements: the UFT dial pair.

## 2026-10-17: the content extractor begins: the seven roles tested against existing inventories (`Wernicke/extractor/`)

First build step (Cody: test the Zork operators against WordNet et al. and the English-literature operators; deconstruction uses only the silk types, not the web). `silk_map.py` holds the rule base as data; `crosswalk_tests.py` measures it; `CROSSWALK.md` is the interpretation, `CROSSWALK_REPORT.md` the raw output. Measured: 98.4% of 44,071 UD English-EWT tokens get a role; SCAFFOLD (16 lemmas), WRAP (79), frame markers (102) are closed classes (100% coverage), ELABORATE is open (2,667 lemmas); SPAN's claim and frame are free but not independent (phi -0.245 in text, -0.294 in VerbNet); 35 of 35 WordNet verb frames and all 1,310 VerbNet frames decompose; ARG0 lands on ANCHOR 66%, ARGM-MOD on SCAFFOLD 96%, but only 38% of PropBank predicates sit at the root: verbs in subordinate clauses need their own SPAN (clause recursion). Eight rule-base changes are listed in `CROSSWALK.md` section 6; none made yet.

## 2026-10-17: tone and sensing as invisible Unicode (Cody; stubbed; not built) and what survives

Cody: the machinery for tone or sensing is stubbed in the invisible Unicode blocks assigned to the emotional tone of words, like Demotic where the first character describes the tone of the word; it goes beside the conjugation and verb-tense machinery; these are the "quasi" particles of words: invisible to viewers, present for the model. The May engine already ran a first version: `monad_speak` wrote an invisible space between words chosen from J/J_max (`fermat_space_utf8`, the "Fermat emotional lattice", U+200B at the lowest band up to U+2003 at the top), which is why the screenshot's reply showed no spaces.

Survival test (2026-10-17, this machine's NLTK 3.10.3 and spaCy 3.8.16): the **U+2000-block spaces (thin, em, figure) are whitespace**: NFKC folds them to an ordinary space (the level is lost), `str.isspace` and `\s` match, NLTK splits the word in two and spaCy makes three tokens. The **zero-width family survives**: U+200B, U+200C, U+200D, U+2060, U+FEFF, U+00AD, variation selectors and tag characters are kept by NFKC and by JSON (ascii and utf-8), are not whitespace, and do not split a word in NLTK or spaCy (one token; the invisible character stays inside the token text, so strip it before a WordNet lookup and keep it as a side channel). So the 8-level space lattice would be destroyed by normalisation and split by tokenizers, while a zero-width alphabet (200B, 200C, 200D, 2060: two bits per character) is the robust choice. Tag characters and variation selectors survive too but are commonly stripped or flagged by platforms (the invisible-prompt-text vector). Still to test: terminal and editor rendering, clipboard, git.

## 2026-10-17: the standard testing corpus

Chosen and mirrored into `Wernicke/corpus/` (README there; documents listed in `MANIFEST.md`): 11 public-domain works, 8.7 MB: Chesterton (Innocence and Incredulity of Father Brown), Abbott's Flatland, Cooper's Last of the Mohicans, Pepys's Diary, Kant's Critique (Meiklejohn), De Morgan's Budget of Paradoxes vol. I, Roscher's Principles of Political Economy, Pliny's Natural History vol. 3, plus Paradise Lost and Longfellow's Inferno as verse stress tests. Left out on purpose: the modern copyrighted novels in `~/Documents/eBooks` and `~/Documents/books/eBooks`, and personal files. 134 sampled sentences (type labels are heuristics), 24 hand-written chat prompts, 40 model-provided reference answers (seven-slot decompositions, unreviewed). Deterministic builder, seed 20261017. All semantic-orbweaver functions are to be tested against this corpus.

## 2026-10-17: SPAN stays one slot, with three independent fields (Cody: verb and scope mostly independent)

Cody confirmed the seven names as a start. Verb and scope are mostly independent: "the sun is yellow" has a verb that does nothing but name the main character. Reading: SPAN is the load-bearing line with three independent fields, mirroring Phase 35's BRIDGE / RADIUS / FRAME on the one major-ampullate silk: **relation** (an event verb, or NAME/IDENTITY, Zork operators 3 and 0, for a copula), **claim** (the complement, the CRYSTAL), **frame** (the scope: prepositional and adverbial setting). In "the sun is yellow": ANCHOR the sun; SCAFFOLD is (tense, agreement); SPAN = relation NAME, claim yellow. The same word can be CRYSTAL or SLACK by function: "yellow" is SPAN's claim in "the sun is yellow" and ELABORATE in "the yellow sun rose". Keeps seven slots; to test: how independent verb-presence and scope-presence are on a corpus.

## 2026-10-17: v3: shape deformation alters the swing about the anchor

Cody: the deformation of the shapes should alter how each individually swings around its anchor; the Broca shapes (the dented white half, 'ammonite shell') look unique. v3 (`tools/epicycles/v3_mockup.py`): each half is a physical pendulum hung from its dot, swing rate = sqrt(m d / I_dot) of the dented, resized outline. A 0.3 dent slows the swing 3 %, 0.5 by 17 %, 0.6 by 40 %. An edge dent alone now gives a rosette in the independent column. v2 kept as history; EPICYCLES.md updated.

## 2026-10-17: CORRECTION to the physics (Cody): the whole spins, the anchors swing

"The spin is only around the center: the whole object spinning clockwise or anti-clockwise. The anchors do not spin, they swing." So: ONE spin (direction = the SIGN bit, a property of the whole); the two dots are pendula swinging about the centre, bounded, in relation to each other and to the spinning whole; their mismatch throws off the barycentre; the centre draws the epicycle. **`System3` as built is wrong on this point:** it gives each weight its own spin about its own centre of mass, driven by its dot (`cmd_y`, `cmd_w`), and the "reverse one dot's spin" experiment of the same day tested that wrong thing. What stays valid: edge dents as mass/centre-of-mass/inertia changes, the barycentre bookkeeping, the seam spring between the S-centre points, the static/free pair, the measurements as measurements of THAT model. Not rebuilt yet; the swing coupling and its restoring force are to be confirmed with Cody first (proposal: swing exchanges angular momentum with the spinning whole, so the whole's rate wobbles; restoring force = the anchor).

## 2026-10-17: Taoist mode physics, second pass (tools/taoist_physics.py System3; tests/test_taoist_physics.py, 6 pass)

Cody's refinements, in order: the weights are anchored at the DOTS, not the seam; the seam may deform and show gaps; the shapes spinning about a centre behave differently when they differ; "the center draws the epicyclic behavior": matched shapes, nothing moves; mismatched edges, regular periodic epicycles; a distorted seam is three anchors, two rotating together around a third (¼, ½, ¾: dot, centre, dot), which is the three-body chaos; a static centre gives regular (star-shaped) epicycles; the two comparisons always run together; **the SHAPE of the epicycle is the measurement**.

Built: System3 = the whole (a free centre body) + two deformable dot-weights (mass, centre of mass, spin inertia from the outline), central anchor springs sized on the healthy halves so healthy is exact rigid rotation, dot motors, a seam spring-damper between the halves' S-centre points (a gap is a force), RK4, `pin=True` for a static centre. The monitor always runs both (static and free centre) on the same scores.

Measured, not assumed (tools/taoist_lyapunov.py, T=600 s): regular baseline λ ≈ +0.009 /s; healthy, matched edges, edge dents, density mismatch: all regular. Chaotic (+0.147 /s) only for strong rate mismatch + an edge dent + a weakly damped seam together; a very soft seam alone stayed regular. **Dead ends kept:** (1) the first model, two rigid bodies on one fixed pivot with a 3-D seam torque (System): chaos only with edge + mismatch + low damping (+0.19), mismatch alone a regular rosette; (2) point-mass gravity on the collinear dot-centre-dot arrangement: every case unstable, including healthy (+2.3 /s), because the Euler collinear configuration is unstable. Open: whether the free-centre pictures are chaotic in the strict sense or irregular quasi-periodic (the λ cross-check is `--lyap`); the constants (EDGE_GAIN, RHO_MM, CMD_Y, CMD_W, seam stiffness/damping) are mine, not Cody's.

## 2026-10-17: Taoist mode built (tools/lemniscate_monitor.py, tests/test_taoist_geometry.py, 12 pass)

Mapping check done: the four sign-quadrants of (sin γ/2, cos γ/2) in `monad.c dirac_phase` ARE the quarter steps 0,¼,½,¾ of γ/2 mod 2π (cycle Phase 3 → 4 → 1 → 2); the seven phases printed in the May trace all agree; poles (Phases 1,3) = sin·cos > 0. So the four gaps of the yin-yang step model are the four Dirac phases. Names file: `~/.clauderc_official_names`.

Model (all constants [PARAM], in the file header): dots drive the spin; yang holds the black dot, yin the white dot; the more damaged half runs faster and its outer arc is dented, the other keeps the common rate and shape; equal damage = centred but smaller; the passive half is entrained by the active (K_LOCK). Results: healthy = a point (b=0); small relative damage = halves lock at a fixed offset, b is a circle; larger = the lock breaks, the offset drifts, b traces an epicycle. Yin-vs-yang give different behaviours ONLY through the asymmetric constants (the figure is congruent under a 180° turn); with symmetric constants the test shows the same regime. Seam (the S line) is drawn as gap/overlap, not scored.

## 2026-10-17: the historic sentence constructor (found)

Cody: the orbweaver's sentence constructor was built in full, then shelved at once because its granularity reached into the poisoned granular `.bin` files.

- **What I identify as it:** `engine/grammar/` (commits `943f77e` 2026-09-08 → `18531b6` 2026-09-13), "the sentence CREATOR: the opposite side of the Zork parser". Five phases: parse spec → structure (speech act → VerbNet sail → a word-free Ring of Slots) → fill (WordNet hypernym-closure resonance pick under an invariant SELRESTR gate) → linearize → check (shadow/frames: is the sail licensed by the verb). `ptol.c` `console_speak()` called it through `ptolc_bridge.py` as the default voice (`6200e40`, 2026-09-11); `rotary_bridge.py install()` put it in the Chat tab (`1b097c7`).
- **Where the granular poison enters:** `maths_sanitize.py` feeds `monad_mathematics.bin` into the filler pool of `monad_sentences.json` tagged `source="maths"`, and `generate.py _resonant_pick(topic_is_maths=True)` makes those fillers the PRIMARY lexicon once a topic gates in. That branch is the granularity.
- **Above it:** `boxkite_orbweaver_monad.py` (Phase 35, 2026-09-03/04, before the creator) is the web cycle: anchor/bridge/frame/hub/radii, scaffold and capture spirals, connectives, genre, turbulence, room shape. Its own sentences are the 13 copied `_SENTENCE_TEMPLATES`, not the creator. `weave_via()` is the path to the heavier layer.
- **Run today (offline, `PtolemyDesktop/.venv`):** `define_X` + `neutron reactor` → `Nucleon is clear.`; `what_does_X_do` + `tree wood` → `Priest trees wood.` (the verb picker took `tree` as the verb); `who_Xs` + `name` → `Priest names country.` Short, licensed, and the fill picks are loosely related to the words; nothing here is validated.
- **Copied (not moved):** `engine/grammar/*` → `Wernicke/src/grammar/`, `monad_sentences.json` → `Wernicke/`, `engine/math_isolate.py` → `Wernicke/src/`. Runs as `cd Wernicke/src && python -m grammar.ptolc_bridge`. By jurisdiction the structure files (`sails`, `frames`, `slot_shells`, `shadow`, linearize) read as Broca's and the fill (`_resonant_pick`, `sem_hash`, `maths_sanitize`) as Wernicke's; the package runs as one unit, so Broca/Wernicke split is Cody's call.

## Side note (Cody, 2026-10-17): the Zork Sentence Parser

The Zork Sentence Parser (`zork_parser.py`, `PtolC/zork.c`; copy in `Wernicke/src/`) is the **starting point of the context-acquisition work** that NLTK takes over later. Cody's assessment: it is very good at decomposing a sentence for parsing. Use it as the front end for prompt decomposition (verb → operator, PREP → relation label, IT → last noun) before NLTK's tagging, sense and topic extraction; see skill `nltk-zork-wordnet`.

## Decisions and standing statements (Cody, 2026-10-16/17)

- Original semantic hash = the golden-ratio seed hash (not a prime hash).
- Division of labour: orbweaver = semantic (word/idea selection, open vocabulary, graded); boxkite = context/structure (the Mind's Eye kite, in hypermotion, scaled). Weight: web heavier than kite; kite may extinguish, not outvote. **Open: which is Broca, which Wernicke** (see below).
- Phonetic field = morphology = the English conjugation, a final `repass()`.
- Engineering mode: every test is allowed to find the lowest-overhead point; code golf later.
- The May bins are historical and read-only; never modified.
- Pencil (scalar kite) → the orbweaver's anchoring mechanism; flashlight stays (scaling of the response).
- A-matrix basin = vocabulary selection tool (General Stirling 10 fractal, UFFormulary of Archimedes); needs continuous operation; Γ_rad works on still kites.

## Open questions

1. (settled 2026-10-17, Claude's call: orbweaver = Wernicke, boxkite = Broca.)
2. The lemniscate is the aphasia diagram (three shapes, ∞ between); monitor built, scorers (S, G) not.
3. File lists per tree are first-pass; Cody to adjust. `constructor.py` and `harness.py` are in neither tree (they need both).
4. Separator behaviour (U+200B vs plain space) between the screenshot and today's binary.

## Timeline of the engine (code, from `git log`)

| date | commit | what |
|---|---|---|
| 2026-05-11/12 | `bf33540` (SemanticWordEngine) | `semantic_engine.py`: golden-ratio hash + `forced_sigma` + nearest of first 20 zeros to `E·50`; `hyperwebster.py`: `_hash` = char-ordinal sum mod 360 |
| 2026-05-15 | `fb7ba29` | v1.0 `PtolC/` C monad: learn pairs, J spread, rank emission |
| 2026-05-16 | `bff4eeb`…`34e26f4` | v1.111–113: surface filter, `monad_English` baseline |
| 2026-05-16/17 | `d1a43ad`, `4d2662a` | `-W` Wick speak; `sin=content cos=observer` |
| 2026-05-18 | `eb28ce8` | v1.215: Fermat lattice, Lagrangian word count, golden walk, demotic, `near_canonical` (the engine of the screenshot) |
| 2026-05-19 | `a2c8451` | v2.1.0 standalone engine (screenshots dated 14:14, 15:26 precede it) |
| 2026-05-26 | `141d60d` | v2.3.0 Prime Directives, φ-walk, Three-Face Wankel |
| 2026-08-25 | `424241a` | v5.0.0 "Box Kite": WordNet-relation context hashing, `monad3c.h` |
| 2026-08-30 | (binary) | `PtolC/ptolemy` 142 KB, still reads PTOL v4 bins |
