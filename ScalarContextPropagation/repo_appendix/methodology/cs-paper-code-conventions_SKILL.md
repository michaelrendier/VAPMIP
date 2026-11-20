---
name: cs-paper-code-conventions
description: Standard conventions for presenting Python/code machinery inside a computer-science paper — when to show a runnable code Listing vs. when to describe an API in prose vs. when to use boxed pseudocode, and how to caption, number, and cite each. Use when writing or revising any paper in FourthAgePapers (or any other engineering-structure paper) that has running code behind a claim, whenever the draft is leaning on dense mathematical notation (Σ, ∫, custom symbols) to describe something that is actually a short function, or when the user says "show the code, not the maths" / asks how a CS paper should present code / asks to check a paper's code-block conventions.
version: 0.1.0
---

# CS Paper Code Conventions

The standing failure mode this skill corrects: writing a mechanism as a
mathematical formula (`H(w) = Σ_k ord(w_k)·95^(|w|−1−k)`) when the actual
artifact is eight lines of Python that already runs. That is leaning
mathematically on something that is not, in its native form, mathematics —
it is code. Established via direct research on real papers
(2026-09-19), not assumed.

## 0. Three real conventions, verified by reading the actual sources — not one

There is no single "how CS papers show code." Three different, equally
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

## Sources (verified directly, 2026-09-19)

- Pedregosa, F. et al. *Scikit-learn: Machine Learning in Python.* JMLR 12
  (2011), 2825–2830. `arxiv.org/abs/1201.0490` — read in full (6 pp.);
  confirmed zero code blocks.
- Rush, A. et al. *The Annotated Transformer.* Harvard NLP.
  `nlp.seas.harvard.edu/annotated-transformer` — fetched and parsed
  directly; confirmed prose/code interleaving order and the
  `jupytext`-paired-script production method.
