# ScalarContextPropagation

**19 Dimensional Scalar WordNet Context Propagation** — Fourth Age Paper, "The Middle Part of *Teaching the Maths English*". Author: Cody Michael Allison (Michael Rendier). Draft, v4.0. Entry page rewritten 2026-11-21 (it used to be a second copy of the paper).

**Licence: Proprietary. All rights reserved** (`../../LICENSE`). The method, the code described and the notebooks are proprietary; the mathematics they use is published under the GNU licence outside VAPMIP. WordNet and Open English WordNet keep their own licences (`NOTICE`, `WORDNET_LICENSE.txt`). Copies obtained while this paper was published under GPLv3 remain under it.

## What it claims

Each of the 146,743 Open English WordNet synsets maps to one prime that encodes its exact spelling and its 19-dimensional relational signature, with no learned parameters. 146,743 of 146,743 synsets round-trip exactly; one deliberate lossy step affects 1.1% of individual relation counts. The scalar boxkite (pencil, string, flashlight, the tension law) is the discrete, static reading of the same structure. Components on established mathematics ship and are tested; open constructions are marked THEORETICAL, and `THEORETICAL:CALCULATED` where the paper's own code computes a result about them. Full abstract: the paper, §Abstract.

## Files

| file | what |
|---|---|
| `19_Dimensional_Scalar_WordNet_Context_Propagation_v4.0.md` | the paper (source) |
| `19_Dimensional_Scalar_WordNet_Context_Propagation_v4.0.pdf` | the paper (the only PDF kept at the top level) |
| `notebooks/` | 6 notebooks the paper cites (01 prime hashing … 06.5 monad3c update) |
| `engine/`, `bench/` | the energy and round-trip benches and their recorded results |
| `repo_appendix/` | the complete code index: every file the mechanism touches, with `repo_appendix/README.md` mapping each directory to the section it backs. Copies of VAPMIP pages there are mirrors of the home pages |
| `figures/` | the paper's figures |
| `NOTEBOOK_PAPER_PLAN.md` | the plan under which the notebooks were built |
| `RECHECK_LOG.md` | dated consistency re-checks (2026-09-27, 2026-09-28) |
| `archive/versions/` | v2, v3, v3.1–v3.4 (md and pdf); Git holds the history |
| `archive/draft_sections/` | `draft_section_03` … `13`, the sources v4.0 was assembled from |

## State (2026-11-21)

* Status block at the top of the paper (2026-11-14 correction pass): the Noether-current statements for the σ = ½ map are retired as conserved-current statements; the Telperion/Laurelin labelling follows the current assignment (Telperion = the primes tree, Laurelin = the factors); d* has four faces.
* Notebook code cells with recorded outputs: 37 of 44.
* Symbols: α = fine-structure constant; A_π = W(1) = 0.5671; Ω_ζΣ = d* = 0.2463 (`@RCCM_SYMBOLS`).
* Not done: the engineering white paper that presents this work for engineers (CS framing, no narrative) is a separate document, written last; see `../../UPDATE_JOB_2026-11-21.md`.

## Build the PDF

`pandoc` with `lualatex`, DejaVu fonts and a Unifont fallback; the recipe and its pitfalls are in `ContextPlease/claude/scratchpad/2026-10-13_paper_pdf_build/README.md`.
