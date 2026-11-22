---
name: cs-paper-code-conventions
description: Standard conventions for presenting Python/code machinery inside a computer-science paper — when to show a runnable code Listing vs. when to describe an API in prose vs. when to use boxed pseudocode vs. a literal REPL transcript, how to caption/number/cite each, and the "perpetual now" rule that every Listing must read cold, without silently assuming the reader carried forward state from an earlier one. Use when writing or revising any paper in FourthAgePapers (or any other engineering-structure paper) that has running code behind a claim, whenever the draft is leaning on dense mathematical notation (Σ, ∫, custom symbols) to describe something that is actually a short function, whenever a section has more than one code Listing and you need to check none of them depends on invisible state from an earlier one, whenever the artifact is a console/REPL session rather than a function, or when the user says "show the code, not the maths" / asks how a CS paper should present code / asks to check a paper's code-block conventions.
version: 0.4.0
---

# CS Paper Code Conventions

The standing failure mode this skill corrects: writing a mechanism as a
mathematical formula (`H(w) = Σ_k ord(w_k)·95^(|w|−1−k)`) when the actual
artifact is eight lines of Python that already runs. That is leaning
mathematically on something that is not, in its native form, mathematics —
it is code. Established via direct research on real papers
(2026-09-19), not assumed.

## 0. Four real conventions, verified by reading the actual sources — not one

There is no single "how CS papers show code." Four different, equally
legitimate conventions exist, verified directly (not from memory):

**A — The software paper: no code in the body at all.**
Pedregosa et al., *Scikit-learn: Machine Learning in Python* (JMLR 12,
2011, `arxiv.org/abs/1201.0490`) — the paper most people cite as "the"
Python ML software paper — contains **zero code blocks**. Six pages,
all prose. The API is described entirely through inline `monospace`
identifiers in running text ("the central object is an `estimator`, that
implements a `fit` method... transformers... implement a `transform`
method"), one benchmark table, and "source code... can be downloaded
from `http://scikit-learn.sourceforge.net`." The paper describes the
*shape* of the interface; the repository is the code.

**B — The literate/annotated paper: the paper IS the notebook.**
Sasha Rush et al., *The Annotated Transformer* (Harvard NLP,
`nlp.seas.harvard.edu/annotated-transformer`) — a full re-presentation
of *Attention Is All You Need* — alternates markdown prose and complete,
runnable code cells, in the original paper's own order, each code block
placed immediately after the paragraph/equation it implements (verified
directly: `EncoderDecoder`, `Generator`, `Encoder` classes each follow
the one or two sentences of prose that motivate them, not a separate
appendix). Kept in sync with an executable `.py` via `jupytext` — the
paper *is* a notebook export, not a description of one. Original LaTeX
math is kept inline exactly as the source paper had it; the annotator's
own commentary is typographically set apart (blockquoted) from restated
original text, so a reader always knows which voice is speaking. Runnable
example code is gated behind a flag (`RUN_EXAMPLES`, `is_interactive_notebook()`)
so the paper can be read as a document or executed as a script without
forking the source.

**C — The mainstream ML paper: boxed pseudocode + a code-availability
statement, not literal source.** The convention used by the large
majority of NeurIPS/ICML-style papers: numbered, boxed `Algorithm`
environments in language-agnostic pseudocode (never a real language's
literal syntax), a one-line "Code available at [URL]" statement (often a
footnote), and, increasingly, a **Reproducibility Checklist** appendix —
a fixed list of yes/no/N-A items (data availability, hyperparameters,
compute used, seeds, number of runs) that a reviewer can scan without
reading the paper body. The checklist format is the closest existing
precedent to this project's own provenance-label system (`ESTABLISHED` /
`OURS` / `FIRST STATED HERE` / `THEORETICAL` / `THEORETICAL:CALCULATED` in
`FourthAgePapers/*/README.md` §2 or §0) — same job, per-component instead
of per-paper.

**D — The computational-algebra-system paper: a literal REPL transcript,
in the system's own language, not pseudocode and not a full listing.**
Bosma, Cannon, Playoust, *The Magma Algebra System I: The User Language*
(J. Symbolic Comput. 24, 1997 — verified directly, 2026-09-27) presents
its examples as bare interactive-session transcripts, prompt included:
input lines start with a literal `>`, followed by the system's own
printed output, exactly as a user would see it at a terminal (e.g. a
free-group element constructed, assigned, then echoed back by typing its
name alone at the next prompt) — not fenced as a language's syntax
block, not boxed as `Algorithm`, not narrated in prose first. This is
the natural convention wherever the "code" *is* a sequence of commands
typed at a live evaluator and the reader is meant to be able to retype
them at their own prompt and see the same output — the paper is a
transcript of a session, not a description of a program. Directly
relevant to this project's own console tools (`derivation`'s curses
SymPy console, `ptol.c`'s shell) — a worked example there is Convention
D, not B: show the literal prompt and its literal echoed result, not a
function definition.

A large multi-file simulation suite takes a fifth shape worth naming
separately from A, though it is a scaled-up case of A, not a new
convention: Jansen & Urbach, *tmLQCD: A Program Suite to Simulate Wilson
Twisted Mass Lattice QCD* (Comput. Phys. Commun. 180, 2009,
`arXiv:0905.3331` — verified directly, 2026-09-27), a gauge-theory
(lattice QCD) codebase paper, carries **no inline code at all** across
44 pages — the Hybrid Monte Carlo algorithm and its variants are
described in closed-form update equations (the physics, in real
mathematical notation, because the *algorithm* genuinely is math here),
and the actual C code is covered by ordinary software-manual sections
("Prerequisites," "Configuring the package," "Building and Installing,"
"Benchmark Executable") that tell a reader how to obtain, build, and run
the suite, never what any specific function's body contains. This is
Convention A pushed to its natural limit: when the codebase is large
enough that no excerpt would be representative, the paper stops trying
to excerpt it at all and documents the *installation and use* of the
whole thing instead — the same move scikit-learn makes at six pages,
here stretched to forty-four because the domain (lattice gauge theory)
needs that much closed-form setup before "how to run it" makes sense.

## 0b. Three more conventions, from the permutation/indexing literature (verified 2026-09-29)

Found by pulling the most-cited papers on permutations, string rotations and permutation-based
indexing and reading the ones that were open (`Ainulindale/references/permutation_papers/`;
citation counts are OpenAlex, 2026-09-29). Each one is a real, working way to show code in a
paper that is a storage/indexing mechanism.

**E — Named-step algorithm + ONE running example, in prose.**
Burrows & Wheeler, *A Block-sorting Lossless Data Compression Algorithm* (DEC SRC-RR-124, 1994;
2,352 cites; read in full, 8 pp.). The two procedures are "Algorithm C" (compress transform)
and "Algorithm D" (inverse), each written as numbered, bracket-titled steps — "C1. [sort
rotations]", "C2. [find last characters of rotations]", "D1. [find first characters of
rotations]" — in Knuth's style, with no code in any language. One example string, `abraca`,
is carried through EVERY step, and the intermediate matrix M is printed after C1, so a reader
can check each step by hand. Natural fit for a reversible mapping whose round trip is the
claim (string ↔ address): state the forward and inverse as two lettered algorithms and
hand-run one short string through both.

**F — Short-paper pseudocode + the enumerated table for a tiny case.**
Myrvold & Ruskey, *Ranking and unranking permutations in linear time* (Inf. Process. Lett.
79, 2001; 127 cites; read in full, 4 pp.). Pascal-style `procedure unrank1(n, r, π)` /
`function rank1(...)`, a two-sentence correctness argument, and a figure listing ALL 24
permutations of n=4 with their ranks (Fig. 1, Fig. 2) — exhaustive over the smallest
non-trivial case instead of sampled. The order of the permutations is *defined by the
unranking algorithm*, and the paper says so. Natural fit for any bijection over a finite set:
show the whole table at n=4 and let the reader see the bijection.

**G — The algorithm lives in a numbered Figure; the running example is a drawing.**
Amato & Savino, *Approximate similarity search in metric spaces using inverted files*
(InfoScale 2008; 111 cites; read). "Figure 1: Example of perspective based space
transformation", "Figure 2: Inverted file obtained for the running example", "Figure 3: Basic
searching algorithm using inverted files" — the pseudocode is boxed as a Figure and referenced
by number, and each experiment is a numbered performance figure. This is Convention C
(boxed pseudocode) with the running example carried by the same Figure sequence.

## 1. Which one to use — decide per component, not per paper

Do not pick one convention for the whole paper. Decide **per component**,
the same granularity the provenance label already uses:

- **Established, cited, off-the-shelf mechanism, ships from a library**
  (Miller–Rabin primality, sieve of Eratosthenes, WordNet lookup) → **A**.
  Name it, cite it, point at the file and function that calls it. Do not
  reproduce it as a formula or a listing — it is not this paper's
  contribution and re-deriving it in notation implies more originality
  than is true.
- **A short (≤ 40 line), OURS or FIRST-STATED-HERE mechanism that IS the
  paper's contribution** (the Horner hash, the pencil accessor, the
  combined-address construction) → **B**. Show the real function verbatim
  as a numbered Listing, immediately after the paragraph that motivates
  it, exactly as it runs in the repo today — not a paraphrase, not a
  formula standing in for it. If the mechanism only *becomes* clear by
  reading the code (e.g. why two prime tiers can't collide), the listing
  carries weight the prose can't.
- **A long or many-file mechanism** (the full monad, the box-kite module)
  → **A**, with a path + function name, same as scikit-learn's "download
  the source" move. A 40-line listing of a 2,000-line file is not
  transparency, it's a sample.
- **An open/THEORETICAL construction with no running code yet** → **C**'s
  pseudocode box, clearly labeled `THEORETICAL`, so a reader can see the
  intended shape without being told it already runs.
- **An interactive session at a live console/REPL is the actual artifact**
  (a `derivation` curses-console walkthrough, a `ptol.c` shell trace) →
  **D**. Show the literal prompt and its literal echoed output, not a
  function body — the point is "type this, see this," reproducibility
  at the prompt, not reproducibility of a definition.

## 2. Mechanical rules once a Listing (convention B) is chosen

- Fence it as real code (` ```python `), not a math block. If it isn't
  valid Python today, it doesn't get a Listing — it gets C's pseudocode
  box and the `THEORETICAL` label instead.
- Number and caption it: `**Listing 3 — token → prime address (`monad.py`,
  `_word_zero_idx`)**`. Reference it by number in prose afterward
  ("Listing 3 is what actually runs"), the same way de Marrais or any
  cited paper is referenced by name, not restated each time.
- One listing = one complete, runnable unit (a function or a small class),
  not a fragment that only makes sense pasted into a larger file. If it
  needs an import to run standalone, include the import line.
- State the source path and whether it is verbatim or extracted (this
  project's own `001_original_2026-05-27_word_zero_idx.py` header —
  "Extracted verbatim from `VAPMIP/monad.py` as it stood at commit
  `204c75d`... Confirmed byte-identical... today" — is the right model:
  it tells a reader exactly what they're looking at and how stale it
  might be).
- Reserve actual mathematical notation (Σ, Π, ζ, ↦) for results that are
  genuinely mathematics first and code second — a closed-form identity,
  a conserved quantity, a group-theoretic fact. A hash function, a sieve,
  a string encoder are code first; write them as code.

## 3. What NOT to do (the failure this skill exists to stop)

Do not write `H(w) = Σ_k ord(w_k) · 95^(|w|−1−k)` for something that is
`v = 0; for ch in w: v = v*95 + (ord(ch)-32)`. The formula is not wrong,
but it is the wrong register — it borrows mathematics's authority for
something that has no proof obligation, only a running-or-not obligation.
A reader who wants to check it has to re-derive code from notation instead
of reading the four lines that are already sitting in the repo. This is
the concrete thing to watch for when revising a draft: any Σ/Π/↦ block
that is describing a loop, not a theorem, is a candidate to become a
Listing instead.

## 4. Applying this to an engineering-structure paper specifically

For papers following the `CollatzShift`/"departure from the template"
posture (provenance label per component, no claim beyond what's proven —
see `FourthAgePapers/ScalarContextPropagation/README.md` §0), convention
B is the natural default for every `OURS`/`FIRST STATED HERE` component,
because the paper's whole posture is "here is the code, it works, look at
it" rather than "here is a proof." Convention A stays correct for every
`ESTABLISHED` component (don't re-derive de Marrais's box kite in
notation; cite it and point at `maths.py`). Convention C's checklist slot
is already filled by the paper's own desk-rejection gate (G1–G10) — do
not also bolt on a generic NeurIPS checklist; the project already has the
sharper, component-scoped version of the same idea.

## 5. The "perpetual now" — every listing is a fresh arrival, not a checkpoint

Named by Cody (2026-09-27): an old console RPG's opening-town NPCs still
say their day-one line if you walk back through after finishing the
game — that dialogue layer was never wired to the player's progress, so
it reads the same on visit one and visit forty. A paper's code listings
should have the same property, deliberately: **no Listing may assume
the reader is silently carrying forward variable values, object state,
or "what we did three listings ago."** Convention B (§0) already
requires each listing to be "one complete, runnable unit... not a
fragment that only makes sense pasted into a larger file" (§2) — this
section names *why*, and extends it past syntax into content: even when
a later listing genuinely consumes an earlier one's output, restate
that input inline (a literal value, a one-line stub, a `# from
Listing 3: addr = 91847...`) rather than relying on the reader having
mentally executed the paper in reading order.

The audience these papers are written for (§4 — "assumes minimal
knowledge of the codebase") is not assumed to have read every prior
page attentively or in one sitting. A reader who jumps straight to
Listing 7 because a citation pointed them there must be able to read it
cold, the same way a save file loaded mid-game still gets correct
dialogue in the first town. A paper that requires "you saw this mutate
in Listing 4" to understand Listing 7 has made the reader's position in
the document part of the program's state — the same "opaque, not
independently readable" failure this project's own papers exist to
argue against in the *model's* representations; the rule says the
prose has to clear that bar too, not just the mechanism it describes.

**Verification note (2026-09-27):** checked directly against the 8
papers fetched for `ScalarContextPropagation`'s citation pass
(`Ainulindale/references/cs_hashing_overhead/`) — Bloom 1970, Broder
1997, Weinberger 2009, Jégou 2011, Matias's FKS exposition, Mikolov
2013, Miller 1995, Elhage 2022. None of these actually carry a
sequential, multi-listing code narrative — they describe mechanisms in
prose plus closed-form notation (Convention A/C territory, §0), not a
run of dependent Listings — so this specific batch does not
independently confirm the pattern one way or the other. The clean
positive example stays the one already in this skill: *The Annotated
Transformer* (§0-B), whose per-class listings (`EncoderDecoder`,
`Generator`, `Encoder`...) each stand next to the sentence that
motivates them without requiring the reader to have run the previous
cell to follow the next one. Recorded here rather than overclaimed —
sound on its own technical-writing merits, but this citation batch
happens not to be where it was directly observed.

**Mechanical check**, when a draft has more than one Listing in a
section: read each in isolation, as if the ones before it didn't exist.
If it doesn't parse that way, it's carrying invisible reader-state —
restate the missing piece inline. A Listing may still *reference* an
earlier one by number in prose ("as in Listing 3") — that's citation,
not a dependency. Genuine pipelines are fine (Listing 5 really does
consume Listing 4's output); what's not fine is a *silent* one. Show
the seam.

## Sources (verified directly, 2026-09-19; §5 added 2026-09-27; Convention D added 2026-09-27)

- Pedregosa, F. et al. *Scikit-learn: Machine Learning in Python.* JMLR 12
  (2011), 2825–2830. `arxiv.org/abs/1201.0490` — read in full (6 pp.);
  confirmed zero code blocks.
- Rush, A. et al. *The Annotated Transformer.* Harvard NLP.
  `nlp.seas.harvard.edu/annotated-transformer` — fetched and parsed
  directly; confirmed prose/code interleaving order and the
  `jupytext`-paired-script production method.
- Bosma, W., Cannon, J., Playoust, C. *The Magma Algebra System I: The
  User Language.* J. Symbolic Comput. 24 (1997), 235–265. 874 citations
  (verified 2026-09-27). Downloaded and read directly
  (`Ainulindale/references/cs_hashing_overhead/Bosma_1997_magma_algebra_system.pdf`);
  confirmed the `>`-prompt transcript convention (Convention D) firsthand.
- Jansen, K., Urbach, C. *tmLQCD: A Program Suite to Simulate Wilson
  Twisted Mass Lattice QCD.* Comput. Phys. Commun. 180 (2009), 2717–.
  `arXiv:0905.3331`. Downloaded and read directly (same directory,
  `JansenUrbach_2009_tmLQCD.pdf`, 44 pp.); confirmed zero inline code
  blocks and the software-manual structure described above.
- The 8 papers in `Ainulindale/references/cs_hashing_overhead/` (Bloom
  1970, Broder 1997, Weinberger 2009, Jégou 2011, Matias/FKS, Mikolov
  2013, Miller 1995, Elhage 2022) — checked directly for §5's pattern;
  none carry a multi-listing code narrative, noted honestly rather than
  forced to fit.

## 6. Applying it to an API reference, not a paper (ValaQuenta, 2026-09-28)

The same conventions worked for an API reference site (Sphinx). Worked example:
`ValaQuenta/docs/gen_listings.py` builds `docs/listings.rst`.

- **A** for everything: the API pages name each function and point at its file;
  the README's Code Reference is an index (import path, one line, links), never a listing.
- **B** for five short OURS mechanisms, but *generated*, not pasted: the generator
  extracts each unit from source by name (docstrings removed, statements verbatim), joins
  it with exactly the constants and imports it needs so it is ONE self-contained unit,
  executes it cold in an empty namespace, and records the REPL output it printed. The
  page says "extracted", the line count and the source path. `tests/test_listings.py`
  re-runs the extraction and compares it to the real module, so a listing that stops
  running fails CI — the "perpetual now" rule (§5) enforced by machine, not by reading.
- **D** for the README's `>>>` session, which `tests/test_readme.py` runs as a doctest.
  Running it found a real bug the first time (registering 38 modules printed 38 lines).
- A listing that needs a class shell (a method) is shown inside a minimal `class X:` wrapper
  and labelled as extracted.

## 7. A white paper on a storage mechanism (HyperindexingSystem, 2026-09-29)

Cody, 2026-09-29: "this paper does not demand narrative. it's straight a white paper on
hyperindexing storage." What that changes:

- **No lineage story in the body.** How the idea was reached (tools used, videos watched,
  who suggested what) is not the paper's job; the premise, definitions, mechanism, measurements
  and limits are. Provenance survives only as (a) the premise citation under the title
  (here: Borges, "The Library of Babel", and libraryofbabel.info's About page + forum) and
  (b) the citation list, tagged built-against (no tag) vs `Post-Hoc:`.
- **Order of a storage white paper:** premise → definitions (address, chunk, layer) → the
  mechanism as Listings (B) or named-step algorithms with one running example (E) → the
  exhaustive small-case table (F) → measurements as `>`-transcripts (D) → limits and negative
  results stated as results → citations. The two orders in which the reader can be lost are
  "measurement before definition" and "claim before limit".
- **Convention per component (this paper):** the string↔address bijection → E with a running
  example (or B); the rank of a string within a composition class → F (n=4 table) ; the
  benchmark sessions → D; the 256-bit fold and any unbuilt construction → C, labelled
  THEORETICAL; established ranking/generation algorithms (Myrvold–Ruskey, Fisher–Yates,
  Burrows–Wheeler) → A, cite and point at the file.
- **Every number in the paper is a measured number** with its script path, or is labelled
  as arithmetic. A claim the code audit could not reproduce (2026-09-29: vocabulary-reduction
  factors, the spectral-range search, the 97% figure) is not in the paper as a result.

## Sources added 2026-09-29 (§0b, §7)
- Burrows, M., Wheeler, D. J. *A Block-sorting Lossless Data Compression Algorithm.* SRC-RR-124 (1994). Read: `Ainulindale/references/permutation_papers/Burrows_Wheeler_1994.pdf`.
- Myrvold, W., Ruskey, F. *Ranking and unranking permutations in linear time.* IPL 79 (2001) 281–284. Read: `MyrvoldRuskey_2001.pdf`.
- Amato, G., Savino, P. *Approximate similarity search in metric spaces using inverted files.* InfoScale 2008. Read: `Amato_Savino_2008.pdf`.
- Not opened (paywalled, listed in `FourthAgePapers/HyperindexingSystem/citations.md`): Sedgewick 1977, Durstenfeld 1964, Ehrlich 1973, Cover 1973, Manber–Myers 1993, Ferragina–Manzini 2000, Chávez et al. 2008, Fagin et al. 2003, Bayer–Diaconis 1992.

## 8. Papers written with an assistant (added 2026-10-14, Cody)

Standing rules for every paper the author now writes with a model, first applied to `FourthAgePapers/CollatzShift/paper/` (*A Bit Shift Wearing A Disguise*), which is the worked example.

* **The assistant note comes first, not hidden.** An opening box, before the abstract: the model's name and id; that a transformer wrote the paper with this skill running (link to the skill in ContextPlease); who the author is and what he is not; the author's method of NOT telling the model what result he is looking for, so he is not handed the answers he wants (stated as a safeguard, not a guarantee); and what kind of paper this is.
* **Labels and hedging.** `ESTABLISHED` (cited), `OURS`, `THEORETICAL`, `OPEN`; the suffix `:CALCULATED` goes on any result the paper's own code produces (CALCULATED is not DERIVED). Keep the academic hedging; do not drop an academic label because code exists, append `:CALCULATED`.
* **A paper that uses GenerationalLineage describes the engine in its own section BEFORE it presents results from it,** and says plainly that engine and paper share an author and an assistant.
* **Every paper ends with an appendix: what in ContextPlease was used, and what ContextPlease is** (a short purpose paragraph so any model can come up to speed with historical access, then a table of files, skills and scratchpads used, each linked).
* **FourthAgePapers holds two kinds of paper** (author's ruling, 2026-11-16): hypotheses under test (One Claim, One Engine, One Set of Notebooks, One Wiki, prediction first) and workbench papers for anything headed for arXiv that is not Ainulindalë or VAPMIP work. A results/code paper with no prediction is a Fourth Age paper of the second kind; there is no rule that a Fourth Age paper must carry a prediction. Say which kind in a scope section. Notation and Disambiguation (five labels; no tag = built against, `Post-Hoc:` = noticed afterwards) follow `ScalarContextPropagation` §2.
* **A code paper has no proofs.** Show the programs (B for short mechanisms, A for long files, D for transcripts). Generate the paper from the engines (`paper/make_paper.py`): numbers taken from fresh runs, listings extracted verbatim and executed cold, and a `--check` mode so the committed text cannot drift from the code.
* **Literature:** every download of another person's work follows the Literature Download Protocol (`ContextPlease/claude/references/INDEX.md`; copy beside the paper; verify each file by its title page), and requests carry a browser-style User-Agent.

## 9. What an introduction is (added 2026-10-15, Cody; measured on six published white papers)

**Rule.** An introduction is **the problem and the intended way around it.** It is not the paper. Cody's formula: the abstract states the problem engineered against; the introduction says how the author plans to avoid it; results follow the code, and the code follows the definitions, in the order the code runs (define the machinery, then employ it).

**Shape (what all six exemplars share).** (1) the constraint in the field, stated plainly; (2) why the existing fixes do not remove it; (3) "we propose X", one or two sentences; (4) optionally one payoff sentence. Target **250–600 words.** At most a two-sentence pointer to where the construction starts. The shortest and most-read exemplars (Transformer, Bitcoin) have no results section, no definitions and no roadmap.

**Never in an introduction (unless asked):** result tables or numbers beyond one payoff sentence; definitions of the mechanism; the history of the project; a contributions list that restates the whole paper; a section-by-section tour; anything that is not in the code being described. **Do not draft a paper the author has not discussed yet.** Take the author's content section by section; ask nothing that the repositories already answer (check git and the code first).

**Exemplars** (public works; copies and title-page verification in `ContextPlease/claude/skills/cs-paper-code-conventions/references/WhitePaperIntroExemplars/`, ledger rows in `references/INDEX.md`; introduction lengths from `pdftotext`, approximate ±10 %):

| paper | engineered against | proposes | results (in the abstract) | intro | results in intro? |
|---|---|---|---|---|---|
| Vaswani et al. 2017, *Attention Is All You Need* | recurrence is sequential, blocks parallelism | the Transformer: attention only | 28.4 BLEU WMT14 En→De (+2 over best incl. ensembles); 41.8 En→Fr single model, 3.5 days on 8 GPUs | ~280 words | one payoff sentence ("twelve hours on eight P100 GPUs") |
| Radford et al. 2018, GPT-1 | scarce labelled data; unclear objective and transfer | generative pre-training + discriminative fine-tuning, task-aware inputs | SOTA on 9 of 12 tasks; +8.9 % Stories Cloze, +5.7 % RACE, +1.5 % MultiNLI, +5.5 % GLUE | ~600 | yes, a closing results paragraph |
| Nakamoto 2008, *Bitcoin* | payments need trusted third parties; double-spending | peer-to-peer timestamp server, proof of work | none; a security condition (honest nodes hold the CPU majority) | ~270 | no |
| Stevens et al. 2017, *The first collision for full SHA-1* | SHA-1 deprecated yet deployed because a collision looked impractical | combined cryptanalytic attack; chosen-prefix PDF forgery | first SHA-1 collision; 2^63.1 compressions, ~6,500 CPU-years + 100 GPU-years; >100,000× faster than brute force | ~920 | mostly history of MD5/SHA-1 attacks |
| Nemec et al. 2017, *The Return of Coppersmith's Attack* (ROCA, CVE-2017-15361) | an entropy flaw in the primes of a widely deployed RSA library | practical factorisation from the primes' structure; fast fingerprint test | 1024-bit < 3 CPU-months, 2048-bit < 100 CPU-years (worst case); tens of millions of devices | ~950 | contributions list (4) + a section roadmap |
| Kocher et al. 2018, *Spectre Attacks* (CVE-2017-5753/-5715) | speculative execution leaks across protection boundaries | practical attacks combining side channels, faults, ROP | arbitrary memory read; Intel, AMD, ARM | ~1,900 | background; results later |

**Observation to keep.** In all six, the numbers sit in the **abstract**; the introduction repeats the problem at length with citations. Cody's structure (abstract = problem, introduction = how it is avoided) matches the Transformer/Bitcoin pattern; the longer papers add contributions, history or a results paragraph, which he does not want here.
