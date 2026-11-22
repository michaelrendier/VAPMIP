# VAPMIP documentation update job (2026-11-21)

**Status 2026-11-21: steps 1–6 of section G are done (commits b531f6f, 9a16a44, 7e6f3d8 and the one after); step 7 (the engineering white paper) is open.** Corrections to this plan found while doing it: `skills/` at the root is the monad's skill-burning Python modules, not a mirror of the Claude skills (no job); the `README.md` of ScalarContextPropagation was a second copy of the paper (replaced by an entry page); the Scaled-Kite page was not short by design but overwritten (restored from git); the outreach emails moved to `outreach/`; the Broca/Wernicke copies are kept as declared copies (verified identical to their homes); `foundations.txt` and `SedenionOperators.txt` are source corpora/transcripts, not documentation, and were left unchanged.

Documentation and papers only. No code, no tests, no builds, except rebuilding a paper's PDF from its own markdown. Nothing here changes how any program behaves.

## Rules for the whole job
1. **Tuning-the-Engine is not touched.** Excluded: `docs/wiki/Tuning-the-Engine/` (all pages), `docs/wiki/Tuning-the-Engine.ARCHIVED-2026-08-13.md`, and its copies `Broca/docs/40_*`, `Broca/docs/41_*`, `Wernicke/docs/35_*`, `42_*`, `43_*`. I also treat `notebooks/tuning_the_engine/` (`FINDINGS.md`, `README.md`) as part of that record and leave it. Say if that is wrong.
2. **Dated records are not rewritten**: `CHANGELOG.md` entries, `Boxkite-Deformation-Record-2026-10-12.md`, sent outreach emails, `SemPriCon/clean/archive/*`, `SemPriCon/dirty/*`. Where such a page uses an old symbol, the fix is one note line at the top ("Symbols in this record: see `@RCCM_SYMBOLS`"), not an edit of the body.
3. **Symbol table to apply** (author's ruling, `~/.clauderc_canonical_maths` `@RCCM_SYMBOLS`): α = 1/137.036; A_π = W(1) = 0.5671 (Fermat: speed of causality, inertia); Ω_ζΣ = Ω_RZ = d* = 0.2463 (Riemann: Hagedorn, entropy); d*·ln 10 = A_π. The four faces of d* are in `Ainulindale/wiki/17` and `@RCCM_FOUR_DSTAR`; d*_RG has no closed form.
4. **Labels to remove from live pages**: "BAO" and "Yang–Mills mass gap" as names for Δ = A_π − 0.246·ln 10 (tested, not supported: `FourthAgePapers/DStar/bao_test.py`); "frozen" about Tuning-the-Engine (it is the last state of the work, not frozen).
5. **Licence line on every live page**: "Proprietary. All rights reserved." (the mathematics is GNU, published outside VAPMIP). The GPL mention goes.
6. **Method of work:** `cs-paper-code-conventions` for any page that shows code (no narrative, the code's own names).
7. **Basis of this list:** file dates, sizes, headings and a pattern scan (`/tmp` JSON, counts below). I have not read every page in full; "to read" means a full read is the first step of that page's job.

## A. Root pages

| page | size, last change | job |
|---|---|---|
| `README.md` | 70 KB, 2026-11-21 (licence line only) | Rebuild as the front door. It holds seven eras stacked: "Start Here (2026-10-14)", "Current machinery: Broca/Wernicke (2026-10-17)", "Current Repo Focus (v5.2.0, 2026-09-26)", "Prime Directives", "The Body (v3.1, 2026-06-30)", "Release Roadmap v2.0→v3.0", "Five Derivations", "Benchmarks", "The Engine", "Word Addressing", "learn()/speak()", "Constants", and more. Job per section: keep / update / move to the wiki / delete. Fix `Constants` (line ~944, the `OMEGA_ZS = 0.56714` family, 6 hits; `GAP … Yang-Mills mass gap` at line ~1067, 3 BAO/gap hits; the BAO-as-intrusion-detector bullet at ~386). Replace the "Individual files going stale is fine" note in "Current Repo Focus" with the current-state paragraph. Add: ScalarContextPropagation proprietary, scaled boxkite / scalar boxkite / orbweaver as the current tools, pointer to this job. Section map first, then rewrite. |
| `TODO.md` | 104 KB, 2026-10-22 | Dated TODO items stay as dated records. Update: 22 `Ω_ζΣ=W(1)` hits (the live items, not the history), the "BAO = The Laplacian" section (line ~1751), "PRIORITY 0 — Separate ValaQuenta from Ainulindale" (check whether done), the 2026-10-22 amygdala item. Add a top block "Current" listing only open items for the three working tools. To read. |
| `CHANGELOG.md` | 84 KB, 2026-10-17 | Historical; leave existing entries. Add one dated entry for 2026-11-21: licence to proprietary, symbol ruling, BAO label removed, d* paper, audit and this job. Its "Unreleased" heading needs a decision: release a version number or keep unreleased. |
| `LICENSE`, `NOTICE` | 2026-11-21 | Done. Re-read once after the other pages change. |
| `AUDIT_2026-11-21.md` | mine | Correct the line calling Tuning-the-Engine "frozen"; point to this file. |
| `foundations.txt` (51 KB, 2026-08-15), `meaning.txt` (39 KB, 2026-05-29) | | To read. `foundations.txt` has 1 BAO/gap hit. Decide per file: still a foundation, or archive. |
| `Boxkite-Catalog.txt`, `marrais_boxkite_catalog.txt`, `SedenionOperators.txt` | de Marrais catalogues, 2–3 hits each | Each exists three times (root, `Broca/catalogs/`, and a copy under ScalarContextPropagation's appendix). Pick one home, make the others a one-line pointer. Fix the `Ω_ζΣ=W(1)` and BAO/gap hits once. |
| `EarPiece.txt`, `face/AGENTS.md`, `face/CLAUDE.md`, `benchmarks/all_voices/README.md`, `RingCircle/slot_table.md`, `HyperindexCompression/horner_vs_arithmetic.txt` | all small | To read; probably unchanged, confirm dates and the symbol/licence lines. |
| `monad_bin/README.md`, `monad_bin/SPEC.md`, `monad_bin/hooks/README.md` | 2026-08/09 | To read: they describe the bin format and the hook; check against the current harness. `SPEC.md` is duplicated in ScalarContextPropagation's appendix. |
| `PtolC/README.md`, `PtolC/docs/corpus-inventory.md` | 2026-05, 12 KB | Stale by date (5 months, before the Broca/Wernicke split). To read; same text is copied three times in `SemPriCon/src/`. |
| `skills/` mirror | | The VAPMIP copy of the skills is stale against `ContextPlease/claude/skills`; the job is to replace it with a pointer. |

## B. `docs/`

| page | job |
|---|---|
| `docs/NLP_ENVIRONMENT.md` (2026-10-17) | Stale: it says the system python has everything; superseded (each repo has its own `.venv`; the system python is broken). Rewrite that section. |
| `docs/SYSTEM_SPECS_ThinkPad_X1_Carbon_6th.md` | Check battery numbers against the current note (57 Wh design, 25.65 Wh now). Copy exists in the appendix. |
| `docs/semantic_orbweaver_notes.md` (38 KB, 2026-10-17) | Current tool. Also lives at `Wernicke/docs/`. One home, one pointer. Add the standard-corpus results section if the author wants it; update status lines. To read. |
| `docs/paper_drafts/Forward_Propagation_of_Information_DRAFT.md` | Older draft of the paper (licence line already fixed). Replace with a pointer to `paper/`, or archive. |
| `docs/context_flow_spec/00`–`12` (13 pages, 2026-10-12) | The 95-test spec. Duplicated verbatim in `Broca/docs/context_flow_spec/`. One home. `00_README` and `10_calibration_set_spec` use "frozen" (2 hits): check whether it means the calibration set (keep) or the project (remove). |
| `docs/figures/epicycles/EPICYCLES.md` | To read; date 2026-10-17. |
| `docs/outreach/*` (4 emails, 2026-06-01) | Sent letters; leave. |
| `docs/poems/recursive_causal_cavitation.md` | Leave. |

## C. `docs/wiki/` (everything except Tuning-the-Engine)

| page | size, date | job |
|---|---|---|
| `Operating-the-Monad.md` | 13 KB, 2026-05-19 | **Highest priority.** 10 `Ω_ζΣ=W(1)` hits, 1 BAO/gap, 1 `d*=0.246`. Five months stale. Full rewrite of the constants and the d* text; operating steps checked against the current harness. |
| `Operating-L-IO.md` | 28 KB, 2026-08-15 | To read. L_(I\|O) is the intertwiner; check against the Two Trees note. |
| `Name-Table.md` | 6 KB, 2026-05-19 | Stale by date; the naming has changed (Broca, Wernicke, SemPriCon, ASS, the symbols). Rebuild as the one table of names: symbols, engines, repos. |
| `J_red-J_blue-0_RB-Record.md` | 20 KB, 2026-11-13 | 1 BAO/gap hit. Rule: any mention of J_red/J_blue appends to this record. Add the 2026-11-21 entry. |
| `Boxkite-Relational-Atlas.md` | 28 KB, 2026-11-09 | Current. Check the Ω/d* lines. Copy in `Broca/docs/`. |
| `Boxkite-Deformation-Record-2026-10-12.md` | 106 KB | Dated record, 7 hits. Header note only (rule 2). Copy in `Broca/docs/`. |
| `Scaled-Kite-English-Thought-Center-Context.md` | 1.7 KB, 2026-10-13 | Current-tool page, too short. Expand from `project_scaled_kite_english_corrections` (corrections A–F of 2026-10-13) in the author's own words. Copy in `Broca/docs/`. |
| `Kings-Maille-Box-Kite-Rings-As-Sentences.md` | 6 KB, 2026-09-05 | To read; copy in `Broca/docs/`. |
| `Grammar-Resources-For-Monad-Sentences.md` | 10 KB, 2026-09-05 | To read. |
| `Lyndon-Factorisation.md`, `Ring-Circle-Operators.md` | 2026-10 | To read; recent. |
| `Definition-from-Above.md`, `Existential-Velocity.md`, `Zero-Lattice.md` | 2026-06-12 | To read; five months old. Zero-Lattice: check the d*/symbol lines. |
| `Null-Space-of-the-Zero-Divisor.md`, `RedBlue-Hamiltonian-Sedenion-Matrix-Space.md` | 2026-08-15 | To read. |
| `Tuning-the-Semantic-Prime-Concept-Engine/` (`00_index` … `17_v3_word_list_and_uns_bins`, `1024.md`) | 17 pages, 2026-10-18 → 2026-11-20 | This is the SemPriCon tuning wiki, not Tuning-the-Engine; I have put it **in** the job. If the author means it to be historical chronology as well, it moves to the excluded list. `10_design_notes` (2026-11-20) is the newest. Update `00_index`, `05_the_baseline`, `11_baseline_mapping_zh_en`, `17_v3_word_list_and_uns_bins` against the SemPriCon v3 state (integer versions, `test_{M}_{A}_v{V}.bin`, Chinese baseline, the English-speaking track). `1024.md` (89 KB) is a data page; to read. |

## D. `Broca/` and `Wernicke/` (the two current trees)

| page | job |
|---|---|
| `Broca/README.md` (1.4 KB), `Wernicke/README.md` (1.7 KB) | Rewrite as the entry pages for the scaled boxkite (Broca) and the orbweaver (Wernicke): what is here, which page to read first, which copies are copies. Never call them "the two trees" (standing rule); use the repo names. |
| `Broca/docs/*` and `Wernicke/docs/*` | Copies of pages in `docs/wiki/` and `docs/`; the three Tuning-the-Engine copies are excluded. For every other copy: one home, the other is a pointer. |
| `Wernicke/extractor/CROSSWALK.md`, `CROSSWALK_REPORT.md`, `README.md`; `Wernicke/sanitize/README.md` | To read; written 2026-10-17. |

## E. `SemPriCon/`

| page | job |
|---|---|
| `SemPriCon/README.md` (4.4 KB) and `SemPriCon_requ_conf.md` (16 KB) | Update to the v3 state: fresh start 2026-10-21, v2 archived dirty, `SpecTools`, naming convention. Remove "frozen" (2 hits each) where it refers to the project. To read. |
| `SpecTools/README.md`, `NAMING_CONVENTION.md` | "frozen" 2–3 hits each: check meaning. |
| `EnglishSpeaking/README.md`, `mappings/README.md`, `corpora/README.md`, `orbweaver/PROVENANCE.md` | To read; short. |
| `clean/assessment/*_v3_prose.md` | Current records; check numbers against the latest run before touching. |
| `paper/The_Golden_Ratio_Monad.md` (105 KB, 2026-10-18), `paper/template.md` | The SemPriCon paper; dated before the v3 fresh start. Update the state sections; apply the symbol table; build the PDF into `Desktop/SpaceClaude/SemPriCon/`. |
| `src/PtolC_eb28ce8/`, `src/PtolC_unicode/` READMEs | Two identical copies of `PtolC/README.md`. Replace with pointers. |
| `clean/archive/*`, `dirty/*` | Records; leave. |

## F. Papers

| paper | job |
|---|---|
| `paper/Forward_Propagation_of_Information.md` (101 KB) and `paper/template.md` (59 KB), PDF `paper/Forward_Propagation_of_Information.pdf`, `sec17.md` | Reports the 2026-10-14 measurements (six prompts, twelve voices): leave the measurements. Update: licence sentence (done in the source) → rebuild the PDF; add the symbol table and the d* faces where constants appear; check the claims that cite BAO/mass-gap (the scan found none in this file); apply `cs-paper-code-conventions` §7 (white paper: no narrative). |
| `FourthAgePaper/ScalarContextPropagation/README.md` | 138 KB. Same stacked-eras problem as the root README: a section map, then restructure. Licence done. |
| Seven versions: `19_Dimensional_Scalar_WordNet_Context_Propagation_v2` … `v4.0` (`.md` + `.pdf` each) | One PDF per paper: keep only `v4.0` at the top level (rebuild it, because its licence sentence changed after the last build). The older md/pdf (v2, v3, v3.1–v3.4) go to an `archive/` folder or are removed (Git keeps them). Needs the author's go before anything is moved. The older sources still say GPL (1 hit each). |
| `draft_section_03` … `13`, `NOTEBOOK_PAPER_PLAN.md` | Sources of v4.0; "frozen" hits: check meaning. Decide whether they stay beside the paper or move under `archive/`. |
| `repo_appendix/*` | Copies of VAPMIP documents (`Boxkite-Catalog.txt`, `SYSTEM_SPECS…`, `monad_bin_SPEC.md`, the two skill files, `box_kite_engine/*`, `j2_involution/*`, `reference_docs/*`). Mirror of pages above: after the home pages change, replace each copy with the new text or a pointer; fix `inversion.md` (1 `Ω_ζΣ=W(1)` hit). The two skill copies must match `ContextPlease/claude/skills/`. |
| `bench/*.txt` | Result records; leave. |
| Engineering white paper (the author's friend's request) | Last. CS framing, no narrative, the code's own names (`ScaledMindEye…`, `WordNetBoxkite`, `BoxkiteOrbweaver`, `Monad`). Built from the three working tools' pages after sections A–E are done. |

## G. Order
1. Root `README.md` section map, `docs/wiki/Name-Table.md`, `Operating-the-Monad.md`.
2. Broca and Wernicke entry pages, the scaled-kite page, `semantic_orbweaver_notes.md`.
3. ScalarContextPropagation README and the v4.0 rebuild; `paper/` rebuild.
4. SemPriCon pages and paper; the SemPriCon tuning wiki.
5. Remaining wiki pages, `docs/`, root text files.
6. Copies replaced by pointers; `CHANGELOG.md` entry; `AUDIT_2026-11-21.md` closed.
7. The engineering white paper.

## H. Decisions I need only if the default is wrong
- `notebooks/tuning_the_engine/` is treated as part of the historical record (left alone).
- `Tuning-the-Semantic-Prime-Concept-Engine/` is treated as live SemPriCon documentation (updated).
- Older ScalarContextPropagation versions are archived or removed only on your go.
- Dated records get a header note, not a body edit.
