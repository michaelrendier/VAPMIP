# The Scaled De Marrais Kite as the Thought Centre for English — context for the document planner (2026-10-13)

*Claude Sonnet 5.5. A CONTEXT page, not a build. Nothing here changes an engine file. It fixes what already exists, what was shelved and why,
and which pieces of the 2026-10-12/13 De Marrais battery plug into which existing design. Labels: [MEASURED] [DERIVED] [LIT] [HYP]. Everything
marked [HYP] is a candidate, not a result.*

## Status, 2026-11-21 (read first)

* **Page restored.** Between 2026-10-13 and today this page had shrunk to one section (§24) because each later append replaced the file instead of adding to it. Sections 0–23 were recovered from git history (commit 6f4d66e for §0–9, then one commit per later section) and §24 is as it stood. Nothing in §0–24 was reworded.
* **What is current on this page** is the design record for the *scaled* boxkite (the Mind's-Eye kite in motion; `scaled_mind_eye_boxkite_kernel_monad.py`, `Currentwork/Broca/`) and how it meets the *scalar* boxkite (discrete, static: seven ordered pairs, pencil, string, flashlight, tension law; `19D_rotary_boxkite_monad.py`). The scalar kite is never given motion; the scaled kite never gets static functions.
* **Corrections A–F of 2026-10-13 (§8) still govern**: the weaver and topic shift are design targets, not authoritative (A); windspeed must deform the kite (B); basin attractors extinguish response possibilities (C); how zero divisors enter sentence construction is open (D); the Contractor (Lagrangian, stable-action path) and the Dilator (cardioid attractor) are the same object (E); the granular `.bin` poison was improper sanitisation and never exercised (F).
* **Symbols:** where this page says "d* / W" (§7) it predates the ruling: Ω_ζΣ = d* = 0.2463 (Riemann: Hagedorn, entropy) and A_π = W(1) = 0.5671 (Fermat: causality, inertia). `@RCCM_SYMBOLS`.
* **Still open (from §7 and §10–13):** windspeed as emission of a sentence part, with the Recamán repass for inexact matches; connection (tense/participle conjugation map; no grammatical tense code exists); context flow; the orbweaver scorers. NLP content processing stays on NLTK (decision §16).
* Copies: this page is at `docs/wiki/` (home) and `Currentwork/Broca/docs/` (copy).

## 0. Rule for reading this page
The sentence/document-planner design is NOT new. It is the spider-web (orb-weaver) composition cycle (`Tuning-the-Engine/35`), the Kings-Maille rings
(`Kings-Maille-Box-Kite-Rings-As-Sentences.md`), the sails/frames grammar (`engine/grammar/`), the three-ring scale (`ValaQuenta/wiki/three_ring_scale.md`)
and the A-Matrix Basin. The Context Flow spec (`docs/context_flow_spec/`) is historic tooling context (Cody): its metrics and calibration set are reusable
as benchmarks; its RST connective table duplicates Phase 35's connective lexicon and should yield to it.

## 1. Two objects that must not be confused
| | scalar context boxkite | scaled boxkite (Mind's Eye) |
|---|---|---|
| what | 7 ordered pairs of pencil(s): 3 axes + 1 pivot + 3 shadows, hashed into every word | the live, continuously moving representation of the Monad |
| nature | discrete, static; pencil / string / flashlight / tension law H = -cos(sum eps_k phi_k) | moves the way De Marrais's kite moves: the G2 family (Der dim 14), exp(theta e8), characters x GL(3,2) |
| windspeed | Gamma-Radial: one scalar, tanh(1/2 ln(log_code/anchor)) | A-Matrix Basin: a conversational measurement, not constant |
| not an Assessor? | none of the 7 stations is an Assessor plane [MEASURED] | the Assessors (42 planes, 84 diagonals) ARE its vertices |
Consequence [DERIVED from the battery]: the pencil/tension machinery is not applied to the scaled kite (Phase 40 scope note).

## 2. What the battery gives the thought centre (all [MEASURED] unless noted; records in `Boxkite-Deformation-Record-2026-10-12.md`)
* The kite is moved exactly by G2 (all 84 diagonals lie on ONE orbit; stabiliser SU(2)). So "the kite moving" = a path in G2 plus the finite 2688 group.
* Invariants under the motion (usable as fixed readings): norm, e0/e8 weights, lower/upper split, singular spectra of L_v / R_v, associator norm K(v).
  Frame-relative (change with the motion): chart energies, local_curvature, Walsh coefficients, sigma_RB tilt.
* sigma_RB is the FIXED question frame; the kite moves relative to it. The question is the lens, the thought is what moves.
* Each zero divisor y has an annihilator N(y) = S3 of partners (4 lattice neighbours = an orthonormal basis; not closed under product).
* {4:8:4} per ZD: past null block (4) | now isometric octonion (8) | future other-sign diagonals (4). The fibre/throw lies in the NOW block of its Assessor
  (ratio 1.0000, 14 Assessors, both diagonals) => the earlier "defect" is a different bracketing, not a defect.
* Frustration: every one of the 8 faces of a kite has sign holonomy -1; no octonion on 3 mutually annihilating diagonals.

## 3. Existing English design to bolt these onto (read, not invented)
* Kings-Maille: sentence = double box-kite ring (ring A from monad3_c.bin lang, ring B from monad_mathematics.bin); NOUN -> slot, PREP -> relation, VERB -> operator.
* Sails: 7 clause patterns SV SVO SVC SVA SVOO SVOC SVOA around e0 = the finite verb, the anchor that does no work (`engine/grammar/sails.py`).
* Phase 35 spider web: ANCHOR BRIDGE FRAME HUB RADIUS SCAFFOLD_SPIRAL CAPTURE_SPIRAL ELABORATE HOOK WRAP SHELL SIGNPOST; connective classes with radial moves
  (+1 out, -1 in, 0 lateral, pivot); E8 content packing; Apollonian gasket context flow; Cassini b/c knob (continuous <-> discrete); genre = field configuration.
  Its failed measure: 7-strut overlap (saturated). Its working measure: Cassini b/c (kite-free). Radius abstraction later flagged wrong (paragraphs are anisotropic gasket cells).
* Why spiders: seven web types ~ seven silks ~ seven clause patterns ~ seven Fano points (Phase 35 claim 3), and the web is built piece by piece along a path.
  It is the main method for building sentences from idea-adjacent vocabularies.
* Test bench: `VAPMIP/boxkite_orbweaver_monad.py`. STATUS: shelved/poisoned.

## 4. Why the orb-weaver monad was shelved (Cody, 2026-10-13)
The granular .bin files were poisoned: they had never actually been worked with when the weaver was built. Standing rules that follow
(`VAPMIP/TODO.md` poison check; `monad_bin/README.md`):
1. A domain .bin must not shift english.bin's granule scale. Granular bins attach as a temporary weight per turn, never written back.
2. "Idea-adjacent vocabulary" = basin(seeds) pool = a READ-ONLY view. Do not rely on the poisoned granular files until the poison-check test passes.
3. Nouns / verbs / tenses should carry ~90% of the way to the next word on their own; connecting words are a separate mechanism. A-Matrix Basin is an idea basin, not a word selector. Phase 35's random draw is off the table for now.

## 5. Candidate mapping of the moving kite onto the weaver  [HYP, all]
| English object | kite object | note |
|---|---|---|
| clause | octonion ring O_u (the NOW block), verb at e0 | dependents on Fano points; relations = lines; voice = line orientation sign |
| double ring lang/maths | Cayley-Dickson pair (a,b); Assessors = cross-ring couplings | matches Kings-Maille ring A / ring B |
| prompt -> response | response in N(prompt) (S3 of partners) | additive "prompt+response=0" (Phase 08) vs multiplicative xy=0 here: choose |
| HUB (zero-divisor reframe of the input) | the G2 element aligning the reference kite to the prompt's nearest ZD | |
| scaffold / capture spirals | paths in the G2 orbit; frustration = holonomy -1 around faces | |
| past / now / future | Hands (record) / fire / Mind's Eye (writing) | {4:8:4} |
| topic shift | change of N(prompt) between sentences (or of the aligning G2 element) | TextTiling analogue |

## 6. NLP variants slotted in (Neuro-Linguistic-Programming-era NLP, not transformers)
TextTiling = eddies/sections; Centering = HUB/radius focus; RST = Phase 35 connective moves; the Context Flow spec's calibration set and 95 UNIMPLEMENTED tests = benchmark for the weaver.

## 7. Open
Which of d* / W is Contractor (catastrophe, origin) vs Dilator (cardioid, outer limit) in the English path; whether the A-Matrix windspeed is scalar-per-read or per-station
(Phase 40); the additive-vs-multiplicative response rule; the poison-check test; bracketing x emerger-bracket dive.

## 8. Corrections from Cody, 2026-10-13 (supersede anything above that conflicts)
A. **Topic shift and the orb-weaver are DESIGN TARGETS, not authoritative.** Phase 35 is the starting design and the test bench, not settled doctrine; sections 3, 5 and 6 are inputs to design.
B. **The A-Matrix windspeed must be able to DEFORM the De Marrais kite** (i.e. act as a G2 / exp(theta e8) generator on it). Scalar-per-read (leaves the rigid struts rigid) is therefore not sufficient by itself; the deformation battery lists what is available.
C. **Basin attractors = an anisotropic, multi-focal locus of knowledge pulled out of storage and checked against itself** (what maps onto the same objects, what does not) to EXTINGUISH response possibilities. First measurement (scratchpad 2026-10-13_extinction_by_annihilator_intersection, [MEASURED], model [HYP]): foci as zero divisors, survivors = common annihilator; 3024/3024 different-strut pairs leave nothing, same-strut pairs leave 2 or 4 dims, triples almost always nothing. One coherent context = one kite.
D. **OPEN: how zero divisors enter the sentence-construction algebras.**
E. **Contractor (Lagrangian path of stable action) and Dilator (cardioid attractor) are the SAME object.** After the twist of the Penrose swap of time and space, time dilation / length contraction become time contraction / length dilation. Time is a necessary component of describing length (how long it takes to get from a to b), not just distance. Earlier start/end assignment question withdrawn.
F. **The granular .bin poisoning was improper sanitisation (those uses had never been exercised), not a design flaw.** The orb-weaver monad has its OWN sentence constructor inside it; the first ptol -w responses from it were garbage because of the poisoned granular .bin files. Fix = sanitise the granular bins; the constructor itself was never fairly tested.

## 9. Second pass (2026-10-13, after Cody's reactor example and the Contractor/Dilator pointer)
* **D (worked example, Cody).** Prompt "neutron generation in different reactor types": five candidate responses, three on reactor types, two on nuclear weapons. The prompt names reactors, so the weapons responses are extinguished, EXCEPT the history of the first reactor, which lies on both branches (reactor engineering and weapons engineering; its first form was aimed at weapons). Survival is therefore "maps onto the prompt's focal objects", not "excludes the other topic". Measured analogue [HYP mapping, MEASURED algebra]: foci of the same strut leave a 2-dim common annihilator (exactly the kite EDGES, 168/168) = a response that sits on both; foci of different struts leave none (3024/3024).
* **E (Cody).** Lagrangian = many-to-one, attractor = one-to-many; both tested months ago: Ainulindale/wiki/17_alpha_omega_d_star.md (Contractor/Dilator "self-adjoint conjugates"), 22, 74, and the gain-spectrum block in canonical maths (sv 0 CONTRACT / 1 NEUTRAL / sqrt2 DILATE, sum sv^2 = dim, "what the dilator gains the contractor loses"). Measured here: x -> xy has sv {0 x4, 1 x8, sqrt2 x4}; forward it is many-to-one, read backward it is one-to-many, same map. {contract : neutral : dilate} = {past : now : future}.
* **Project today** = Contextual Flow with NATURAL language processing (Cody's correction; earlier "neuro-linguistic" reading withdrawn). Origin: the Zork Parser was to use the python2 `nlp` package (now python3 `datasets`) to pull meanings out of a prompt -> document planning + sentence construction: extract puzzle pieces from the prompt and embed them in a properly scaled response. Several models by granularity, first graded by schooling level (vocabulary AND concept/topic). NOTE (flagged plainly): the HuggingFace `nlp`/`datasets` package loads corpora and metrics; it does not itself extract meaning, so the extraction step belongs to the Zork parser / WordNet / a parser library, with `datasets` as a source of graded corpora.
* Scratchpad: 2026-10-13_extinction_by_annihilator_intersection (tests2.py, tests3.py).



## 10. Emission, not hash (Cody, 2026-10-13, third pass) [design direction, HYP]
* Parser lineage: the Zork parser is the hard-coded table (Infocom: every input reduces to one entry in a hard-coded file); the scalar boxkite context is that table's hashed form; the old `nlp` topic/subject extraction is its scaled-up parse. Poisoned-bin sanitising is a LATER project, after prompt->response context flow is approximated.
* A-Matrix Basin may NOT be the windspeed but is still part of the SELECTION algorithm.
* Scalar kite: pencil grabs boxkite AND boxkite grabs pencil. Scaled De Marrais kite: the windspeed is an EMISSION OF A SENTENCE PART (vertex = argument slot, edge = relation, e0 = verb), not a hashing scalar. It need not be static, unmoving or exact because of the RECAMAN REPASS (set-membership test against everything visited, flip direction on collision; ValaQuenta/wiki/bracketing_firing_order.md + add_scale_sign trajectory/collisions/would_collide).
* Two membership tests: extinction (candidate must lie in the common annihilator of the foci) and repass (candidate must not already be visited).



## 11. Gathered inputs and the two-mechanism split (Cody, 2026-10-13, fourth pass)
* **The session-opening paste (Google AI answer), recorded so it is never re-requested.** (Order corrected by Cody: the package SURVEY was the FIRST paste, the `nlp`->`datasets` answer the SECOND.) FIRST: the Python NLP package survey = Hugging Face's 2020 library, renamed `datasets` (corpora/metrics); a legacy PyPI `nlp` is an unmaintained stub; stdlib offers only `re` and `collections.Counter`. SECOND: the literal `nlp` package = Hugging Face's 2020 library renamed `datasets`. Survey contents: spaCy (NER, dependency parse, Cython), Hugging Face Transformers (excluded as weights; METHODS wanted), NLTK (corpora, WordNet), Stanza (Stanford, 70+ languages, PyTorch), TextBlob (noun-phrase extraction, POS), VADER (rule-based sentiment lexicon), Gensim (unsupervised topic modelling, LDA, similarity), Polyglot (130 languages). Closest to "topics and subjects out of an input sentence": TextBlob noun phrases, spaCy NER/dependency, Gensim LDA. Constraint: laptop, offline, no GPU, ms latency, no transformer weights.
* **Two mechanisms, design not started.** (1) EMISSION: a discrete addition of words (noun/verb/adverb, each already context-encoded in the vocabulary) into the response. (2) CONNECTION: a separate mechanism that joins those words in the proper forms: the conjugation map (future, past, present, participles, on down). Verified 2026-10-13: no grammatical conjugation/tense map exists in VAPMIP code (the weaver's `tense` field is a light-cone band past/now/future, not grammar), so mechanism (2) is wholly undesigned.
* **Sequence Cody set:** which windspeed types suit EMISSION -> then the connecting-words mechanism -> then prompt-to-response context flow. Bin sanitising comes after.



## 12. document_planner re-opened (Cody, 2026-10-13): where the session had stopped
* **Model as last agreed (earlier this session):** Gamma-Radial windspeed = constant single-scalar carrier propagating context word to word. A-Matrix Basin = read live off the kite, varying, conveys the IDEA through word representations (topic + sub-subjects), propagates nothing. Smith-chart locator = depth of usage in the vocabulary (where stored knowledge is). Response = prompt location scaled up by two mechanisms: vocabulary and document_planner. The monad already does the expensive transformer part (19-slot relation vector per WordNet entry in monad3_c.bin, folded by monad3_gamma_radial; a lookup is a binary search + memory read).
* **Proposed shape (Claude, not built, not authoritative):** `document_planner(reading, basin_read, vocab_view, config) -> plan`. Content determination = basin topic and sub-subjects; structuring = exact ordering over the few sub-subjects (try all orders, Centering to minimise rough shifts, shortest reach first); sizing = word budget by basin weight x REGISTER_BANDS; output = ordered units each with focus entity, speech act, register, content-word pool (frames and function words left to the sentence constructor); liveness = re-read the basin at every unit boundary (Eye/Hands split as in rotary_rerun_monad.py).
* **Update from the measurements:** the earlier open question "is a sub-subject a lit strut?" now has a candidate answer [HYP]: TOPIC = a strut (one kite, all foci in it survive together), SUB-SUBJECT = a vertex (Assessor) or edge inside it. Cody's example: topic "Neutron Generation", sub-subject "Pressurized Water Reactors". Also: `lit_struts` (rotary_rerun_monad.py:597) tests |psi[a]|>1e-12 on any vertex index, so any dense 16-vector lights all seven (read from the code, not run); a threshold or a focus-count rule is required.
* **Still unverified:** that the 16-vector from ptol.c `project` is the same kind of psi that `local_curvature` / `lit_struts` take.



## 13. Basin relationships from the prompt extraction (Cody, 2026-10-13): first look
* **What exists.** `monad_english_io.basin(seeds)`: seeds are a FLAT bag; pull(j) = max over seeds of A[i][j] (learned word-to-word weights, untyped), times idf, min_pull 0.25. No roles, no relation types. The 19 typed WordNet relations (`wordnet_boxkite.RELATION_METHODS`: hypernyms ... usage_domains) are stored in monad3_c.bin as compress_count(DEGREE) per relation, not target identity ("target-identity sensitivity is real future work", same file). So typed basin edges that need identity must be read from WordNet at extraction time.
* **Probe (WordNet via PtolemyDesktop/.venv, run 2026-10-13) on "neutron generation in different reactor types":** `reactor` has 2 senses (electrical reactance vs nuclear_reactor.n.01); `generation` has 6+ (generation.n.06 = production of heat or electricity); nuclear_reactor.n.01 has 8 hyponyms (gas-cooled, thermal, thermonuclear, atomic_pile, fast, liquid-metal, water-cooled, breeder) = the "different types"; part_meronyms moderator, control_rod, core. "Pressurized water reactor" is NOT a synset (nearest water-cooled_reactor), so the sub-subject needs vocabulary beyond WordNet. nuclear_reactor, atom_bomb, neutron are NOT linked by taxonomy (lowest common hypernyms: instrumentality / whole; path similarity 0.14 / 0.077): the topical tie that holds the example together (neutrons, chain reaction, both branches) is not a typed WordNet edge, so it must come from the associative A edges.
* **Proposed edge families for the basin [HYP, design input]:** (1) TOPICAL = A edges (associative; defines the locus/strut); (2) TAXONOMIC = hypernym/hyponym ("types of" enumerates hyponyms); (3) PART-WHOLE = mero/holonyms ("in", "of"); (4) PROCESS = causes/entailments (verbs); (5) DOMAIN = topic/usage/region domains (sense filter); (6) GRAMMATICAL ROLE from the parse (subject > object > other, as Centering ranks) to weight seeds instead of a flat max.
* **Extraction output to define:** per piece {surface, lemma, POS, role, candidate synsets, scope operator}. Scope operators seen in the example: "different ... types" = enumerate hyponyms; "in" = containment/scope. Sense choice (electrical vs nuclear reactor) may be done by extinction: the sense whose foci share a strut with the other pieces survives [HYP, untested].



## 14. Toolset for prompt understanding (topic, sub-topics, disambiguation): survey and environment check (2026-10-13)
* **Environment as found** (PtolemyDesktop/.venv): nltk 3.10.3 (wordnet and punkt present; averaged_perceptron_tagger, punkt_tab, stopwords, maxent_ne_chunker MISSING), scikit-learn 1.9.0. NOT installed: spaCy, gensim, TextBlob, Stanza, VADER, YAKE, rake_nltk, pytextrank, datasets. No spaCy model on system python3 either. VAPMIP/datasets also holds UD_English-EWT and UD_English-GUM treebanks.
* **No document planner is in the pastes.** The pastes list packages. The planner model is Reiter & Dale (from Claude, earlier). To Claude's knowledge no off-the-shelf open-text document planner exists; planners are hand-built per domain (McKeown TEXT schemas, Hovy RST planning). Stated from memory, not re-verified.
* **Recommended stack (non-transformer, CPU, offline at run time):** (1) spaCy small English pipeline for tokens/lemmas/POS/noun chunks/dependency roles/NER (small CNN, not a transformer; speed claim unmeasured); NLTK perceptron tagger + RegexpParser is the lighter fallback. (2) WSD by personalised PageRank over the WordNet graph seeded with the prompt's other pieces (UKB, Agirre & Soroa 2009, from memory) with most-frequent-sense as baseline and NLTK Lesk as the weak classic; this is the same operation as basin(seeds) run on the typed WordNet graph. (3) Topic = role-weighted noun-chunk heads lifted through WordNet (hypernyms, lexnames, topic_domains); keyphrase extractors (RAKE, YAKE, TextRank) for long inputs; LDA (gensim) is a corpus-level tool, poor for one sentence. (4) Related vocabulary = the basin over A plus typed WordNet expansion.
* Not needed: Stanza (PyTorch neural), VADER (sentiment), Polyglot (multilingual), TextBlob (wrapper over NLTK/Pattern).



## 15. The third Google-AI exchange (the "context flow packages" answer, re-supplied by Cody 2026-10-13)
* **Cody's prompt (gist):** new model of forward information propagation, "context flow"; 19-D WordNet relationships bundled into a prime-spelled, hashed word, hashed again to a prime with a single gamma-radial windspeed scalar that reconstructs the 19-D WordNet boxkite (De Marrais kites with his own relationships inside); used HF `nlp`/`datasets` to pull context for topic and granularity; A-Matrix basins choose (A) vocabulary by topic and (B) carry the main idea from prompt into response; NO LLM, no transformers; focus = scale and flow context into the right size and shape.
* **The answer's packages:** NetworkX / RustworkX (graph transitions, low latency), SciPy sparse (A-Matrix basins, trajectories, stability), NumPy + Numba @njit (windspeed reconstruction, prime hashing), NLTK (WordNet navigation to fill the 19 slots), Gensim (Log-Entropy, fastText/Word2Vec baseline distributions). Framing: a nonlinear dynamical system; prompt boxkite = initial state injected into the basin; windspeed = scaling factor on the rate of diffusion/advection across the graph. Closing question: how are the response's size/shape boundary conditions defined (information density, basin depth, number of graph nodes)?
* **Claude's assessment (not authoritative):** generic and flattering; contains no parser, disambiguation or topic-extraction tool, the part now needed. SciPy sparse suits a typed WordNet adjacency and personalised-PageRank WSD (own few-line power iteration; NetworkX is the slower, simpler route); but basin pull is a MAX over seeds, not a sum, so plain sparse matmul does not compute it (row-wise max reduction needed). Numba is unnecessary given the python3 -> ptol.c plan and its JIT compile can cost seconds on first call (from memory, unmeasured). Gensim fastText is the one item with a unique offer (subword vectors for out-of-vocabulary words). Its "windspeed = diffusion rate" framing conflicts with the settled model (Gamma-Radial = constant carrier; scaled-kite wind = emission/G2 deformation; basin pull = max, not diffusion). Its closing question is the real design question and the repo already holds candidate answers: REGISTER_BANDS, Cassini b/c, Smith-chart stop rules (cover the ring or spend the budget), per-unit word budgets.



## 16. NLTK as the base; Lesk vs MFS vs personalised PageRank, a first measurement (2026-10-13)
* **Cody's reading:** NLTK is the base of most of the other libraries and has superior tools such as Lesk. **Claude's correction (stated from memory):** only TextBlob wraps NLTK (with Pattern); spaCy, Gensim and Stanza are independent codebases. NLTK is still the right base HERE: installed, offline, pure Python, WordNet-native. Its `nltk.wsd.lesk` is the simplified classic, not the strongest disambiguator.
* **Measured** (scratchpad 2026-10-13_wsd_lesk_vs_ppr, 7 sentences, illustrative only): Lesk 2/7, most-frequent-sense 2/7, personalised PageRank over the typed WordNet graph 2/7. On the target prompt, Lesk and MFS pick the electrical `reactor.n.01`; PPR picks `nuclear_reactor.n.01` (right) but all three miss `generation.n.06`. Taxonomy-only edges lack the topical tie, so an associative or gloss edge family is needed (consistent with section 13). PPR ~50-80 ms per query unoptimised; the 118k-synset graph takes ~14 s to build, so it must be precomputed.



* **DECISION (Cody, 2026-10-13): stay with NLTK for content processing**, because the scalar boxkite already uses it. This supersedes the spaCy recommendation in section 14. NLTK pieces to use: WordNet (installed), `lesk` (weak, baseline only), `pos_tag` + `RegexpParser` chunking (tagger data MISSING from the venv), `wordnet_ic` similarity measures, TextTiling. One-time data downloads needed: averaged_perceptron_tagger_eng, punkt_tab, stopwords (not yet fetched).



## 17. NLTK-only extraction and disambiguation: what it looks like (prototype, 2026-10-13)
* **NLTK has no C API.** The "C port path" in the 4th Google-AI answer means using NLTK's algorithms as a blueprint. Its citations (a vixra paper and De Marrais boxkite papers) do not support its NLTK claims. Portable pieces: WordNet's plain dict files (inside ~/nltk_data/corpora/wordnet.zip, 10.7 MB, format per wndb(5WN)), the `morphy` suffix/exception algorithm, perceptron tagger weights (export the dict to flat arrays), regexp chunk patterns (finite-state), overlap counting.
* **Pipeline built from stock NLTK parts plus the UD-EWT treebank already on disk** (scratchpad 2026-10-13_nltk_extraction_pipeline): tokenise (NLTKWordTokenizer, no data) -> POS (PerceptronTagger trained offline: UPOS 0.9389 on EWT test, 4.1 MB, 0.28 ms/sentence) -> chunk (RegexpParser NP/PP) -> lemma (wn.morphy) -> sense (own extended Lesk). 3-19 ms warm per prompt (first call ~3.9 s WordNet load).
* **Measured:** correct on bank (depository_financial_institution.n.01), power-plant `plant.n.01`, "first reactor" -> nuclear_reactor.n.01, neutron, fission. FAILS on the target prompt: reactor -> electrical reactor.n.01, generation -> coevals.n.01. Short prompts give too little gloss overlap, and the neutron-reactor-generation tie is not in WordNet glosses: the associative A edges are still the missing piece. Tagger error: "produces" tagged NOUN.
* NLTK pieces not used (bloat): parse, sem, inference, ccg, translate, cluster, classify, lm, sentiment, stem (other than WordNet morphy).



## 18. Topic learned from a search overview, then used to disambiguate (Cody's idea, tested 2026-10-13)
* **Cody's original idea:** a Google search plus a crawl of the top 10 links to learn what "neutron generation" covers; the search now returns an AI overview that can be grabbed instead. LEARNING-TIME ingestion (the run-time monad stays offline); the overview is itself model-written text, so it must be stored with provenance and treated as unverified input.
* **The overview** (kept verbatim in scratchpad 2026-10-13_nltk_extraction_pipeline/neutron_generation_overview.txt, URLs stripped) names four methods (compact fusion generators D-D/D-T, spallation sources, fission reactors, radioisotope and (alpha,n) sources) plus applications. It also shows the SHAPE of a good response for this topic: a definition, grouped sub-topics, applications, a closing question.
* **Measured:** topic bag of 114 lemmas (neutron 15, fission 6, nuclear 4, deuterium 4 ...). Sense = overlap of the sense's gloss bag with the topic bag: reactor -> nuclear_reactor.n.01 (21 vs 2), generation -> generation.n.06 (3 vs 2, thin), neutron -> neutron.n.01. These are the three words the prompt-only extractor missed. Failure: generic "type" -> type.n.06 (printing block) on noise (2 vs 1): generic words need a margin rule with an explicit most-frequent-sense fallback.
* **Reading:** the topical tie missing from WordNet (sections 13, 16, 17) is supplied by an ingested topic bag. In the project's terms it is learned `A` edges, built by the conversational-ingest route. Sub-topic discovery (the four methods) is a separate step from sense choice.



## 19. Extending WordNet in its own methodology: ingested text updates the 19 relations (Cody, 2026-10-13) [design discussion]
* **What already exists.** `VAPMIP/tools/make_englishwordnet_bin.py` combines the co-occurrence A-matrix (holcus_monad_english.bin, 164,283 words) with NLTK WordNet typed edges; merge rule "repeats deepen context: max(existing, new), no renormalisation". The `monad3_c.bin` word vector stores `compress_count` of each relation's target COUNT (degree, not identity; `wordnet_boxkite.py`). So the extension path is: ingested text -> new typed edges -> degree changes -> the 19-D vector moves.
* **WordNet's own methodology to keep:** synsets of synonyms with a gloss; typed pointers from the same 19 families; a lexicographer category per synset; sense order by frequency. Extensions: (a) new edges between existing synsets; (b) new synsets for missing terms (measured: "pressurized water reactor" is absent; nearest `water-cooled_reactor.n.01`); (c) updated sense frequencies, which improves the most-frequent-sense fallback.
* **Extraction.** Hearst-style patterns ("X such as/like Y" -> hyponym; "X consists of Y" -> part; "X produces Y" -> causes). Measured on the ingested overview: raw-string regex gave 12 candidates, about 3 plausible (fissile materials -> uranium-235/plutonium; fission emitters -> californium-252; light target -> beryllium), the rest fragments. Patterns must be anchored on NP chunk heads, not raw strings (scratchpad 2026-10-13_nltk_extraction_pipeline/hearst.py).
* **Safeguards [HYP]:** keep the base WordNet immutable and write ingested edges to an OVERLAY with provenance and a count; promote an edge into the 19-D vector only after independent sources agree; keep edge IDENTITY in the overlay (the vector stays degree-only); run the granule-scale poison check (a domain change must not shift english.bin's scale) before any promotion; self-sense-tagging frequencies risk confirmation bias (the disambiguator would be training its own fallback).



## 20. Are the struts singular or multiple? Is there friction where they cross? (Cody's question, measured 2026-10-13)
* **Definition used:** strut = antipodal pair of kite vertices = reversal pair of Assessors {(a,b),(b,a)} (21 struts, 7 kites x 3); four diagonals each. Scratchpad 2026-10-13_strut_components_friction (README has all numbers).
* **Multiple, not singular [MEASURED]:** the four diagonals of a strut mutually anticommute exactly and form TWO components, {(a,b,+),(b,a,-)} and {(a,b,-),(b,a,+)}, each pair sharing a 4-dim partner space (N+ and N-). N+ and N- are orthogonal and together span 8 dims = the complement of the strut's J_red-type half (for strut (1,2): partners on indices 4-7,12-15; the diagonals themselves on 0-3,8-11). That 8-dim span is not a subalgebra. So "one forward, one backward" fits as the + and - pairs; whether they are Cody's J_red/J_blue is NOT tested (his J_red/J_blue are forward/reverse Dirichlet series).
* **Friction [MEASURED]:** none inside a kite: same-kite diagonals either annihilate (xy = 0) or anticommute exactly. Between kites (3024 pairs) 2184 anticommute exactly and 840 carry a symmetric residue; those 840 are exactly the pairs whose supports share one basis axis e_i (same count, 5/18, for every kite pair). Distinct basis units always anticommute, so friction can only come from a shared axis: the sticks rub only where they share a lattice axis.

## 21. Correction to section 17 (Cody, 2026-10-13): the C side and the Zork parser are live
* Princeton WordNet's own C library is already used: `PtolC/dump_boxkite_bin.c` rebuilds `c_monad_wordnet.bin` (154,725 first-sense entries, the same 19-D vector as the NLTK-based Python) and `wntest.c` checks it against Python; `ptol.c` mmaps `monad3_c.bin` and runs the Gamma-Radial windspeed in C. NLTK itself is only called from Python (`popen`ed by `ptol.c` for the word bag and sentence creator). Section 17's "port the dict files by hand" understated this.
* `zork.c` is compiled into `ptolemy` and `zork_parse()` is the front door of the `-r` REPL in `main.c`: verb → operator e0..e15 → `prompt` → `monad_speak()`. The NLTK extraction work therefore extends a live component, not a historical one. Skill: `nltk-zork-wordnet` §1 and §8.



## 22. Baseline: what the live monad says today (run 2026-10-13, `PtolC/ptol`, no changes made)
* `ptol "<prompt>"` prints a word bag and writes an SVG paper to `~/.ptolemy/papers/`: "neutron generation in different reactor types" -> `weaver-of-peace glory-decked monenda · hard-scrabble massy`; "what is a tree" -> `horseback whirleth · tilt · innovators marsyas arrow-swift …` (archaic/epic vocabulary from the English store; no visible tie to the prompt).
* `ptol -say "<prompt>"` (the sentence creator's voice, offline): reactors prompt -> `Priest relates country.` (σ=0.2454, Γ=−0.5092, firing word `squirting`, Gamma-Radial windspeed −0.890); "what is a tree" -> `Time is able.` (no firing word with a WordNet vector); "the first reactor was built after neutrons were discovered" -> `George relates country.` (firing word `countryfolk`, windspeed −0.905).
* Reading [MEASURED outputs, my interpretation]: the monad already produces short grammatical sentences from the firing words (Cody: "contextual decompositional conversational bits and pieces"); on these three prompts the content does not follow the prompt's topic, which is the gap the prompt-extraction, disambiguation and topic-bag work (sections 13-19) is meant to close. Three prompts is not a benchmark. Each run wrote an SVG to `~/.ptolemy/papers/`.



## 23. Latency and memory of the live monad (measured 2026-10-13, this laptop, 8 cores, no GPU)
* `ptolemy -r -n` (the Zork REPL, in-process monad, no save): 2 input lines in 0.182 s wall (startup included, 63 MB peak RSS); 82 lines in 1.672 s, so **about 18.6 ms per line** (Zork parse + speak + print), `(1.672 - 0.182) / 80`. Sample replies: "what is a tree" -> Zork `e0/identity "identity is tree"` -> `kite its engine probe`; "examine the reactor" -> `disjunction kite duration pores`.
* `ptol -M tree` (one bsearch of the mmapped `monad3_c.bin`): 0.00 s wall, 3.2 MB RSS (`gamma_radial` -0.904887, `vec19` for the WordNet entry). Plain `ptol "<prompt>"`: 0.54 s wall, 298 MB peak RSS. `ptol -say` (sentence creator through Python + NLTK): about 7.8 s wall, 320 MB peak RSS; the Python/NLTK launch dominates, as noted from reading `ptol.c`.
* Not measured: energy. Cody's comparison is "36 ms for the monad vs kilowatt-hour queries"; the 36 ms is consistent with (slower than) the 18.6 ms per REPL line measured here. No energy figure for either side was measured; a whole agentic session and a single monad response are not the same unit.



* **Energy, public figures (searched 2026-10-13, secondary sources):** Google reports a median Gemini text prompt of about 0.24 Wh (May 2025); OpenAI's CEO gave about 0.34 Wh for an average ChatGPT query; Epoch AI estimates about 0.3 Wh; "thinking" models and long responses are much higher (one less rigorous blog: 18-40 Wh for a medium GPT-5 response). So the documented scale per typical query is **watt-hours (tenths of a Wh), not kilowatt-hours**; a "kWh per query" statement would be about a thousand times too high and should not go in the paper or the email. The monad's own energy is NOT measured: `/sys/class/powercap/intel-rapl*/energy_uj` is permission-denied here. Back-of-envelope only (assumes 15-25 W package power, which was not measured): 1.67 s for 82 lines is roughly 7-12 mWh, i.e. on the order of 0.1 mWh per reply, which would be a few thousand times below a typical 0.3 Wh query. Measure with RAPL before quoting it.



* **Energy, measured on battery (AC unplugged, 2026-10-13; scratchpad 2026-10-13_monad_energy):** 5000 replies through `ptolemy -r -n` took 129.3 s (25.9 ms/reply under the sampler) while the whole laptop drew a mean 9.255 W; idle baselines were 7.57 W before and 10.35 W after (drift 2.8 W), so the monad's incremental power is below this method's resolution (the 0.296 W difference from the mean idle is smaller than the drift). Defensible figures: **whole-system energy per reply = 9.255 W x 25.9 ms = 0.240 J = 66.6 uWh**, and an upper bound on the monad's own share of about 12 uWh per reply (using the lower idle baseline). Against ~0.3 Wh for a typical public LLM query the whole-system figure is about 4,500 times lower. The earlier 0.1 mWh back-of-envelope estimate is superseded by this measurement.



## 24. Correction to section 22 (screenshot from Cody, reproduced 2026-10-13): there are two voices
* Cody's screenshot (`SpaceClaude/downloads/claude-stuff.png`, curses console, 2026-09-11) shows the **box-kite monad** (`rotary_rerun_boxkite_monad.py`, status bar `monad:rotary_rerun_boxkite`): the frame is chosen by the WordNet relation that dominates the prompt's context (`infer_direction`; 13 templates: classify, enumerate, decompose, situate, characterize, explain, imply, associate, compare, contextualize, localize, register, observe) and filled from the words nearest that context, e.g. "finger pointer" -> "it is made of pinkie and pinky. [decompose; words: pinkie, pinky, knuckle, fingernail, thumb, point, head, shaft]". Reproduced headlessly today (`.claude/scratchpad/2026-10-13_boxkite_monad_voice/bk_try.py`): "finger pointer" -> "it is made of pinkie and pinky." (identical), "can you play the piano?" -> "it is made of service and grand.", "what is a tree" -> "it is made of Israelite and coward.", the reactors prompt -> "it resembles varied.". About 1.8-2.4 s per reply in Python (first call 8 s, WordNet load).
* Section 22's reading (that the monad's replies do not follow the prompt's topic) came from the **compiled** voice (`ptol`, `ptol -say`, `ptolemy -r`: ms latency, word-bag/fragment replies) and must not be applied to the box-kite voice, which does follow the topic on some prompts ("finger pointer" -> fingernail, knuckle, thumb) and misses on others. The two voices are different programs: compiled (ms, 63 MB) and Python box-kite (about 2 s). Porting the relational composter to C is the step that joins them (`ptol.c` already marks it future work).

