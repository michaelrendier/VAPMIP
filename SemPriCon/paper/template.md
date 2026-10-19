# The Golden-Ratio Monad

### A complete mechanical account of the engine that answered "what is your name": `ptolemy` v1.215 (`PtolC/monad.c`), its store, its replies, and its measured limits

**Cody Michael Allison** (Michael Rendier), independent researcher · the.wandering.god@gmail.com · ORCID 0009-0007-7239-6760\
**Written by an AI assistant:** Claude Sonnet 5.5 (`claude-sonnet-5-5`), with the author's `cs-paper-code-conventions` skill running (`ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md`)\
**Date:** 2026-10-18 · **Status:** first full draft · **Code:** `VAPMIP/SemPriCon` · **Reference source:** `VAPMIP/PtolC/`, commit `{{commit_short}}` ({{commit_date}}) · **Repository prefix:** every path below, written `REPO/directory/file`, lives under `https://github.com/michaelrendier/`

---

> ## Read this first: who wrote this, and how
>
> **The assistant.** This paper was written by a transformer language model, Claude Sonnet 5.5 (`claude-sonnet-5-5`), working with the author's `cs-paper-code-conventions` skill active; the skill decides how code is shown in a paper. Every number in the text that comes from code was produced by `VAPMIP/SemPriCon/paper/evidence.py` when `VAPMIP/SemPriCon/paper/make_paper.py` last ran; none is typed in by hand. Every C listing is cut from the source file by function name when the paper is built.
>
> **The author.** The author is a software engineer, not a trained mathematician or linguist, and says so. Every statement that is not attributed to a cited source should be read as unverified until an expert has checked it.
>
> **The method.** The author's method is to give the assistant measurements to take ("run it", "chase that to its source") rather than results to reach. In this work he also stated his own expectations of the system; the paper reports the measurements as found, whichever way they fall. This is a safeguard, not a guarantee. The author's standing instruction is that **the code is authoritative to this paper**: where a comment, a wiki page or a recollection disagrees with the source at commit `{{commit_short}}`, the paper describes the source.
>
> **What kind of paper this is.** An engineering white paper about one finished program, shown running. It contains no proofs and makes no prediction beyond §18, which is labelled `THEORETICAL`. It changes nothing in the code it describes: the reference binary is built from the unmodified source, the store it loaded is read-only, and a second implementation (a line-for-line Python port) is checked against the first.

---

## Abstract

A small language engine is easiest to trust when every step between a prompt and a reply is arithmetic that a reader can follow and re-run. The May-2026 C monad of this project is such an engine: {{nfuncs}} functions in five C files, no trained weights, no gradient descent, no network. It hashes a word's spelling to one of 25 000 positions by multiplying a base-95 number by the golden ratio; it learns by adding weights between positions that occur near each other in text; and it replies by spreading weight from the prompt's positions through those links and reading positions out in golden-angle order. It once answered "what is your name" with `holcus same stuff seemy`. No complete account of how exists: the descriptions on file (comments, wiki pages, session notes) disagree with the code and with each other. This paper is that account. It describes each function in the order the program runs, identifies the store the program loaded ({{hdr.vocab}} occupied positions, {{hdr.A}} weighted links, byte-identical to the screenshot's header), reproduces the reply from source, and checks a line-for-line Python port against the compiled binary ({{equiv.ok}} replies identical; learned state exact). It then measures what the engine's address function, word display rule and constants do, and records ten limits as results. The first word of the reply is explained mechanically: it is the display label of the position that the word *in* addresses to. The store contains no non-ASCII word, and the program's tokenizer cannot admit one. The source is not changed, tuned or improved here; the account is the baseline against which the next version is measured.

![The first attempt (file dated 2026-05-17): `ptolemy -l 'what is your name'` in `Projects/Ptol/Ptolemy3` on the HP EliteBook 820 G3 ends in `Segmentation fault (core dumped)`. File: `VAPMIP/SemPriCon/paper/figures/1-funny-ptolemy.png`. Shoutout to Max Cohen's Computer - Euclid](figures/1-funny-ptolemy.png){width=90%}

---

## 1. Introduction

A program that replies to a question with arithmetic alone has to be accounted for in arithmetic. For the engine described here that has not been done. Its most quoted result is one reply, to the prompt "what is your name", and the explanations on file for that reply were written at different times from memory, from comments in the source, or from the design the program was meant to implement. Those explanations do not agree. One says the first word was forced by a conservation law; the source selects it by a nearest-value rule. One says each word maps to a unique prime; the source sends every word of eight letters or more to the same position. One says the vocabulary is the words the engine has met; the source stores, per position, whichever colliding word has the largest spelling-derived number. Any of these may have been true of a design. None can be used as a baseline for the next version, which will replace the spelling hash with a hash of meaning, unless the present version is described exactly.

The way around the problem is to give up every authority except the source at one commit and to check the description against an independent implementation. The paper therefore does four things, in this order. It fixes the program: the commit, the git blob of each file, the checksum of the store it loaded. It describes every function that runs, in run order, quoting short functions verbatim and giving longer ones as named steps with the exact lines. It reimplements the same functions line for line in Python, bugs included, and requires the reimplementation to reproduce the compiled binary's replies and learned state byte for byte, so that each sentence of the description is a statement about code that has been run twice. And it measures the store and the functions, reporting every limit as a result, without changing anything.

The reader should come away able to say, for any word and any prompt, which position the word addresses, how heavy that position is, which words the engine can emit, why it emits the first word it does, and what the engine cannot do. The paper does not claim the engine understands anything; it states what the engine computes.

---

## 2. Notation, disambiguations, and conventions followed in this paper

### 2.1 Notation

Every component described in this paper carries one label, applied consistently:

- **`ESTABLISHED`**: mathematics or computer science that predates this work, cited to its source.
- **`OURS`**: code or a design choice built for this work and not published elsewhere.
- **`THEORETICAL`**: designed, or partly attempted, but not reduced to running, verified code.
- **`OPEN`**: a question this paper cannot settle.
- The suffix **`:CALCULATED`** marks a result the paper's own code produced. It says a number came out of a run; it does not say a statement was proved.

Maths is written in Unicode, never LaTeX, and code identifiers are given as the code spells them. The symbols and identifiers used:

| symbol | code identifier | meaning |
|---|---|---|
| N | `m->N`, `MONAD_N_DEFAULT` | number of positions ("slots", "zeros"): 25 000 |
| idx | `idx`, `z#idx` in traces | a slot number, 0 … N−1 |
| γ | `m->zeros[idx]` | the number attached to slot idx (§5) |
| E | `E`, `vocab[idx].E` | the word's energy, a function of spelling alone (§6) |
| β | `m->beta[idx]` | the slot's depth: grows each time a word addresses it, capped at `MONAD_BETA_SAT` |
| age | `m->age[idx]` | steps since the slot was last in a prompt |
| A | `m->am` | the link table: weight between two slots (§8) |
| J | `J[idx]` | the weight a prompt puts on a slot while speaking (§12) |
| φ | `MONAD_PHI` | the golden ratio, 1.6180339887498948482 |
| d\*, Ω | `MONAD_D_STAR`, `MONAD_OMEGA_ZS` | the lower and upper bounds of E: 0.24600 and 0.56714 |
| `U+200B … U+2003` | `fermat_space_utf8` | the eight invisible separator characters (§12.10) |

The code attaches physical and number-theoretic names to these quantities ("Riemann zero", "Noether", "Wick rotation", "Fermat", "Lagrangian", "octonion"). This paper uses the code's names where it must refer to the code and states what the computation is, in arithmetic, each time. It does not rely on any of the names for a claim.

### 2.2 Disambiguations

**Slot, zero, word.** A *slot* (the code says *zero*, `z#idx` in traces) is one of 25 000 positions. A *word* is a lower-case ASCII token. Many words address the same slot (§17.1); the engine's weights (β, A) belong to the slot, not to a word.

**Vocabulary.** In this paper the *vocabulary* of a store is the set of *displayed words*: one word per occupied slot, the word the slot displays. It is not the set of words the engine has met.

**"The semantic prime hash."** Three different things on file carry this or a similar name. (H1) A Python-era hash that takes `next_prime` of a base-95 value (`VAPMIP/monad.py`, `_horner_hash`). (H2) The golden-ratio seed hash in this paper, `monad_word_coords`: **there is no prime in it**. (H3) The WordNet relation-count codes, products of primes raised to relation counts (`VAPMIP/wordnet_boxkite.py`). This paper is about H2 only. A prime-concept hash is the next engineering step and is not part of the baseline described here.

**`ptolemy` and `ptol`.** `ptolemy` is the program built from `main.c` and described here. The later compiled monad `ptol` (`PtolC/ptol.c`) is a different program with a different store (`monad3_c.bin`) and is neither described nor touched.

**Reference build.** The *reference binary* is `ptolemy` built from the unmodified source at commit `{{commit_short}}`. The *port* is `SemPriCon/tools/monad_py.py`.

**The store.** The *store* is the PTOL state file `monad_wordnet_v4_20260519.bin` (§4, §16).

### 2.3 Post-Hoc citations

A citation with no tag is a source the code was built directly against: WordNet's data and the tools used to read it. A citation marked `Post-Hoc:` is a correspondence noticed after the code already worked. The golden-ratio multiplication in §6, the Newton iteration on the zero-counting function in §5 and the golden-angle walk in §12.7 were written without citing any source; the literature that describes the same constructions is listed in the References as `Post-Hoc:` and nothing in the paper depends on it.

### 2.4 ContextPlease

ContextPlease is the author's versioned memory for work done with a language model: notes, protocols, skills, primers and scratch directories that let a fresh model session come up to speed with historical access instead of re-deriving what is already known. It is the source of the notes, earlier traces and commit history this paper starts from; the files used are listed in §20. The code, the store and the numbers do not come from it: they come from the repository at the commit above.

### 2.5 Conventions

- One running prompt, `what is your name`, carries every named-step description; eight prompts are used for equivalence.
- A short function (about 40 lines or fewer) is quoted verbatim, cut from the source by name when the paper is built, with its line range. A long function is given as named steps with verbatim excerpts, each marked as an excerpt with its line range; the runnable unit for a long function is its port, executed in `SemPriCon/notebooks/`.
- Every figure comes from a script that can be re-run. A table whose header says "port" is computed by the Python port; a table whose header says "C" is the compiled binary's own output.
- Where the code disagrees with its own comments, the paper reports the disagreement as a result (§17).
- The port is verified, not trusted: replies and learned state are compared with the compiled binary (§14.3, §10.8). Where the port and the binary could disagree (floating-point summation order in §12.3), the check is on the output of the whole function.

### 2.6 The machine measured on

One ThinkPad X1 Carbon (6th generation), Intel Core i7-8550U, no GPU, no network, Linux 6.8. The evidence run that produced this text took {{rt.seconds}} s.

### 2.7 Authentication: what "authoritative" refers to

The paper's authority is the following set of files and the checksum of the store, nothing else. A reader can check each line.

{{tbl.auth}}

The store: `monad_wordnet_v4_20260519.bin`, sha256 `{{store.sha256}}`, {{store.size}} bytes, read in full by the reader of §4 (every byte accounted for: {{hdr.consumed}}). Commit `{{commit}}` ("{{commit_subject}}").

### 2.8 Install and run

    cd VAPMIP/SemPriCon
    cp -r src/PtolC_eb28ce8 build/ && make -C build/PtolC_eb28ce8         # gcc, make, libm, libxml2 headers
    mkdir -p scratch_home/.ptolemy
    HOME=$PWD/scratch_home PTOLEMY_HOME=$PWD/scratch_home/.ptolemy \
      build/PtolC_eb28ce8/ptolemy -c dirty/monad_wordnet_v4_20260519.bin -W "what is your name" -n
    python3 tools/verify_against_c.py            # port vs binary, 8 prompts
    python3 tools/verify_learn_against_c.py      # port vs binary, learned state
    python3 -m nbconvert --to notebook --execute --inplace notebooks/0*.ipynb

`-c` names the store, `-W` is the reply mode of the screenshot, `-n` forbids saving. The store is also `chmod a-w`.

---

# Part I: the machine, in the order the code runs

## 3. Reading order and function index

The program is five C files and four headers (§2.7). `main` loads a store (`state_load`), then handles its arguments left to right: `-i` learns the built-in identity text, `-l`/`-L` learn a text or file, `-W` hears a prompt and speaks, and a final step saves or refuses to save. Learning and speaking use the same four data structures: the slot arrays β and age, the table of displayed words (the vocabulary), the word map, and the link table A. This section lists every function in the five files with its line range; the right-hand column gives the section of this paper that describes it. Functions marked "—" are helpers (colour, I/O, file-type routing) that never touch a reply and are not described. Functions marked "n/a" exist in the file but are not on the path of the replies in this paper.

{{tbl.funcs}}

The reply of §14 is produced by exactly this call chain: `main` → `state_load` → `monad_speak_wick` → `monad_speak` → { `monad_hear_raw` → `monad_wm_get` → `monad_word_coords`; `dirac_*` not used; `near_canonical` → `surface_canonical`; `fermat_space_utf8`; `token_accept` }. The store the reply used was built by earlier `monad_learn_ex` calls (`-l`, `-L`, `-i`).

---

## 4. The store: `state_load` and `state_save`

**Label:** `OURS`. **Source:** `state.c` lines {{LINES:state.c:state_load}} (`state_load`), {{LINES:state.c:state_save}} (`state_save`). Both are long, so they are given as named steps (convention E). The runnable reader is Listing 1.

The store is a binary file with four fields: a header, two arrays indexed by slot, the vocabulary (one entry per occupied slot) and the link table.

| field | size | content |
|---|---|---|
| magic | 4 | `"PTOL"` |
| version, N, vocab_size, A_size, word_count | 5 × u32 | version 4; N = slots; counts |
| threshold | f64 | `emission_threshold` (stored; never read by the speaking path, §17.7) |
| affect | f32 | v4 only: the `affect` variable (§12.6) |
| β | N × f64 | depth per slot |
| age | N × i32 | steps since last prompted |
| vocabulary | per occupied slot | `idx` u32, `wlen` u16, `E` f64, `home_stratum` u8, `gen_stratum` u8, `prose_seen` u8 (v ≥ 3), then `wlen` bytes of the word |
| A | A_size × 16 | `i` u32, `j` u32, `w` f64, always `i < j` |

**`state_load`, named steps.**

1. **S1 [open and magic].** Open the file; the first four bytes must be `PTOL`, else report and return −1.
2. **S2 [header].** Read version, N, vocab_size, A_size, word_count (`read32`) and the threshold (`read64d`).
3. **S3 [resize].** If the file's N differs from the monad's N, call `monad_resize`: the file is authoritative. (N = 25 000 in every store in this paper.)
4. **S4 [affect].** If version ≥ 4, read one f32 into `m->affect`.
5. **S5 [β and age].** Read N doubles and N ints.
6. **S6 [capacity].** Grow the link table to `next_pow2(2 · A_size)` and the word map to `next_pow2(2 · vocab_size)` entries.
7. **S7 [vocabulary].** For each entry: read `idx`, `wlen`, `E`; read the two strata if version ≥ 2 and `prose_seen` if version ≥ 3; clamp `wlen` below `MAX_WORD_LEN` = 256; read the word; if `idx < N`, fill `vocab[idx]` and call `monad_wm_set(word, idx)`. The word map is rebuilt from the displayed words only (§7, §17.8).
8. **S8 [links].** For each A entry with `i, j < N`, call `monad_a_add(i, j, w)`: weights accumulate, so a duplicate pair would add.
9. **S9 [report].** Print `[state] loaded <path>  vocab=<n>  A=<n>  wc=<n>` on standard error. This is the line in the screenshot.

**`state_save`** writes the same layout: vocabulary for every slot with `present`, A for every table entry with weight ≥ `min_weight`. `main` calls it with `min_weight = 0.0`.

**Listing 1 — reader for the store (`SemPriCon/tools/ptol_bin.py`, function `load`, verbatim).** Reads every section and returns the number of bytes consumed, so a short read or a wrong layout is visible.

```python
import struct
import numpy as np

{{PYFN:tools/ptol_bin.py:load}}
```

**Transcript 1 — the store of this paper, read by Listing 1.**

    > d = ptol_bin.load("dirty/monad_wordnet_v4_20260519.bin")
    > d["version"], d["N"], d["vocab_size"], d["A_size"], d["word_count"], d["affect"]
    ({{hdr.version}}, {{hdr.N}}, {{hdr.vocab}}, {{hdr.A}}, {{hdr.wc}}, {{hdr.affect}})
    > d["bytes_consumed"] == d["bytes_total"]
    {{hdr.consumed}}

The numbers are the ones printed by the program in the screenshot (`vocab=24485  A=6825748  wc=121914388`).

---

## 5. Constants and the zeros

### 5.1 Constants (`ptolemy.h`)

**Label:** `OURS`. The constants are defined once; the header says they "mirror `Philadelphos/monad.py` exactly". The right-hand column counts how often each name occurs in the program's other `.c` files.

{{tbl.consts}}

Defined and never used by any `.c` file: {{unused}}. They are documentation, not parameters. The stored `emission_threshold` is set in `monad_create` and written and read by `state.c`, but no speaking function reads it.

### 5.2 `generate_zeros`

**Label:** the formula inside is `ESTABLISHED` (the main terms of the Riemann–von Mangoldt counting function, von Mangoldt 1905; `Post-Hoc:` the code does not cite it); the function is `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:generate_zeros}}.

**Listing 2 — `generate_zeros` (`monad.c`, verbatim).**

```c
{{C:monad.c:generate_zeros}}
```

Named steps: **Z1** copy the first 20 tabulated values (14.134725 … 77.144840) into `z[0..19]`. **Z2** for each later index n = 21 … N, start from the linear extrapolation `t = z[n-2] + (z[n-2] − z[n-3])`. **Z3** solve `nt(t) = n` by Newton's method (at most 30 steps, stop when the step is below 10⁻⁴), where `nt(t) = (t/2π)(ln(t/2π) − 1) + 0.875`. **Z4** store `z[n-1] = t`.

The values after the twentieth are therefore solutions of an approximate counting formula, not tabulated zeros of the zeta function. Checked against `mpmath` {{mpmath}} (`zetazero`):

{{tbl.zeros}}

The sequence is increasing and smooth, and the engine uses it only as a number γ attached to each slot: in `sin(γ)` (§10.2), in `|γᵢ − γⱼ|` (§10.5), in `sin(γ/2)·cos(γ/2)` (§10.3) and in `cos(γ/2 + φ_rot)` (§12.7). No property of the true zeros is used.

---

## 6. The address: `monad_word_coords`

**Label:** `OURS`; `Post-Hoc:` the construction is multiplicative (Fibonacci) hashing (Knuth, 1973) applied to a base-95 number. **Source:** `monad.c` lines {{LINES:monad.c:monad_word_coords}}.

**Listing 3 — `monad_word_coords` (`monad.c`, verbatim).** Maps a word's spelling to a slot `idx` and an energy `E`.

```c
{{C:monad.c:monad_word_coords}}
```

Named steps:

1. **A1 [digits].** Each byte `c` of the word contributes digit `c − 31` if `32 ≤ c < 127`, and digit **0** otherwise (every byte of a non-ASCII character).
2. **A2 [Horner].** `v ← 95·v + digit`, in unsigned 64-bit arithmetic: the value wraps modulo 2⁶⁴.
3. **A3 [shift].** If `v > 0`, `v ← v − 1`.
4. **A4 [golden ratio].** `seed = fmod((double)v · φ, 1.0)`, taken in [0, 1).
5. **A5 [slot].** `idx = floor(seed · N)`, clamped to [0, N−1].
6. **A6 [energy].** `E = d* + seed · (Ω − d*)`, so E ∈ [0.24600, 0.56714).

**Worked example, `holcus` (port; the compiled binary gives the same slot and E, §14.3).**

{{hol.steps}}

`v − 1 = {{hol.vminus}}`; `(double)v · φ = {{hol.prod}}`; `fmod(…, 1) = {{hol.seed}}`; `idx = {{hol.idx}}`, `E = {{hol.E}}`.

**The address is exactly what built the store.** Re-addressing each of the {{addr.checked}} displayed words from its spelling gives the slot and E stored for it in all but {{addr.mismatch}} cases.

### 6.1 Measured: address resolution falls with word length

A double has 53 significant bits. `(double)v · φ` exceeds 2⁵² once `v` exceeds 2⁵²/φ = {{thr52}}; from there the spacing between doubles is at least 1 and `fmod(x, 1.0)` is exactly 0. Below that threshold the spacing is 2⁻ᵏ for some k that shrinks by one for every doubling of `v`, so the seed has only k fractional bits. A word's `v` is bounded by 95 raised to its length: 95⁷ = {{p95_7}}, 95⁸ = {{p95_8}}; the smallest `v` of any eight-letter lower-case word, `aaaaaaaa`, is {{v_aaaaaaaa}}, above the threshold. Every word of eight or more letters therefore has seed 0: slot 0, E = d\* = 0.24600. Seven-letter words keep 6 fractional bits (64 distinct seeds). Six-letter words keep 13 (8 192).

**Table 1 — slots reached, by word length (port; all {{lem.n}} single-token ASCII WordNet lemmas that pass the prose filter).**

{{tbl.reslen}}

{{lem.slot0}} of {{lem.n}} lemmas address to slot 0 ({{lem.ge8}} lemmas have eight or more letters), and the lemmas as a whole reach {{lem.slots}} of 25 000 slots. Slot 0 displays `{{slot0.word}}`. The unsigned wrap in A2 begins at about ten letters (95¹⁰ > 2⁶⁴) but is moot, because the seed is already 0.

**Table 2 — selected words (port).**

{{tbl.words}}

### 6.2 Measured: non-ASCII input

The engine's tokenizer (§9.2) removes non-ASCII bytes before any word reaches `monad_word_coords`. A direct call with a non-ASCII string behaves as follows: every byte is digit 0, so a string made only of non-ASCII characters has `v = 0` and addresses slot 0, E = d\*; in a mixed string each non-ASCII byte counts as a zero digit, which still multiplies the value by 95.

**Table 3 — direct calls and tokenizer output.**

{{tbl.nonascii}}

---

## 7. The word map: `fnv1a`, `monad_wm_get`, `monad_wm_set`

**Label:** `OURS`; FNV-1a is `ESTABLISHED` (Fowler–Noll–Vo; not cited by the code, `Post-Hoc:`). **Source:** `monad.c` lines {{LINES:monad.c:fnv1a}}, {{LINES:monad.c:monad_wm_get}}, {{LINES:monad.c:monad_wm_set}}.

The word map is an open-addressing hash table from a word to its slot, with linear probing and doubling at 65 % load. Its only purposes are to tell the learning and hearing paths whether a word is *known* (it is the displayed word of some slot) and to return the stored E.

**Listing 4 — `fnv1a`, `monad_wm_get`, `monad_wm_set` (`monad.c`, verbatim).**

```c
{{C:monad.c:fnv1a}}

{{C:monad.c:monad_wm_get}}

{{C:monad.c:monad_wm_set}}
```

`monad_wm_get(word)`: look the word up; if present, return its slot, and take E from the slot's displayed entry if that slot is occupied, else recompute E; if absent, compute `(idx, E)` with `monad_word_coords` and return 0 ("new"). So a word that is not the displayed word of any slot is reported `[new]` even if it has been learned, and its E is recomputed from spelling, which gives the same value; the flag therefore says nothing about whether the word was ever met (§17.8).

---

## 8. The link table: `a_key`, `monad_a_add`, `monad_a_get`

**Label:** `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:a_key}}, {{LINES:monad.c:monad_a_add}}, {{LINES:monad.c:monad_a_get}}.

A is a symmetric weight between two slots. It is stored once per unordered pair, in an open-addressing hash table whose key packs both slot numbers into 30 bits.

**Listing 5 — `a_key`, `monad_a_add`, `monad_a_get` (`monad.c`, verbatim).**

```c
{{C:monad.c:a_key}}

{{C:monad.c:monad_a_add}}

{{C:monad.c:monad_a_get}}
```

Properties: the pair is ordered so `i < j`; the key is `(i << 15) | j`, which is unambiguous only while both numbers are below 2¹⁵ = 32 768 (N = 25 000 here); key 0 means "empty", and the only pair that would produce it, (0, 0), is excluded by the `i == j` test; the table doubles at 65 % load; the probe start is `key & mask` with no mixing, so keys that agree in their low bits (slots that differ by a multiple of the table size) share a probe chain. Adding to an existing pair adds the weights. The store holds {{hdr.A}} pairs, an edge density of {{density}} % of the N(N−1)/2 possible.

---

## 9. Lifecycle, tokenizer and filter

### 9.1 Lifecycle (`monad_create`, `monad_ground_init`, `monad_resize`, `monad_destroy`)

**Label:** `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:monad_create}}–{{LINES:monad.c:monad_resize}}. `monad_create(N)` allocates the arrays and sets `ground = |L_GROUND|/N` = 7.552·10⁻⁵ and `emission_threshold = 2|L_GROUND|` = 3.776, with an initial word map of 65 536 entries and link table of 131 072 entries. `monad_ground_init` fills `zeros` with `generate_zeros(N)` and sets every β to `ground` and every age to 0. `monad_resize` reallocates all four arrays for a new N. A fresh monad therefore has every slot at the ground depth and no vocabulary.

### 9.2 The tokenizer: `tok_split`

**Label:** `OURS`. **Source:** `tokenizer.c` lines {{LINES:tokenizer.c:tok_split}}.

**Listing 6 — `tok_split` (`tokenizer.c`, verbatim).**

```c
{{C:tokenizer.c:tok_split}}
```

A word character is `isalpha(c)` or an apostrophe, on an `unsigned char` in the C locale (no `setlocale` call occurs in any of the five files): **ASCII letters and the apostrophe only.** Every other byte, including every byte of every non-ASCII character, ends a word. Tokens are lower-cased; a token must have at least two characters and must not start with an apostrophe.

**Table 4 — `tok_split` (port, verified on the compiled binary's learned state in §10.8).**

{{tbl.tok}}

### 9.3 The filter: `token_accept`

**Label:** `OURS`. **Source:** `filter.c` lines {{LINES:filter.c:token_accept}}, with the helpers {{LINES:filter.c:is_pure_numeric}}–{{LINES:filter.c:is_long_allcaps}}.

**Listing 7 — `token_accept` (`filter.c`, verbatim).** Decides whether a token is allowed to take a slot when learning. Hearing does not call it. Speaking calls it on candidate output words (§12.8, §12.9).

```c
{{C:filter.c:token_accept}}
```

The rule table (`FILETYPE_RULES`) has one row per file type: maximum length 24 for prose, markup, document and WordNet text (40 for code); no hex strings, no slashes, no tokens more than half digits and no long all-capital tokens except in code; base-64-looking chunks of at least 16 characters are rejected for the text types; the vowel gate applies to the text types: a token needs at least one of `aeiou`, and a token of six or more letters needs at least 15 % vowels; a token ending in an apostrophe is rejected.

**Table 5 — `token_accept` on prose rules (port).**

{{tbl.accept}}

Of the {{hdr.vocab}} displayed words in the store, {{tok.rejected_now}} would be rejected by this version of the filter ({{tok.rejected_ex}}, …): they entered under an earlier filter or through slot display (§10.4).

---

## 10. Learning: `monad_learn_ex`

**Label:** `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:monad_learn_ex}} (`monad_learn_ex`, 132 lines), {{LINES:monad.c:monad_learn}} (`monad_learn`: calls `monad_learn_ex` with prose rules). Learning is the only way a slot gets a word, a depth or a link. The function is long, so it is given as named steps (convention E) with verbatim excerpts; the runnable unit is `Monad.learn_ex` in `SemPriCon/tools/monad_py.py`, checked against the binary in §10.8.

**Named steps for a text.**

1. **L1 [refuse keys].** If the text begins with `-----BEGIN `, refuse (PEM key or certificate material) and return.
2. **L2 [sentences].** Cut the text at `.`, `!`, `?` and newline. A piece shorter than two bytes is skipped.
3. **L3 [tokens].** `tok_split` the sentence (§9.2). If it yields nothing, go to the next sentence.
4. **L4 [per token].** For each token accepted by `token_accept` (rejected ones are counted in `rejected_count`): address it (`monad_wm_get`; §6, §7), raise β of its slot, give the slot its displayed word, set `prose_seen`, count the word. Remember the slot and E in order (`sidx`, `sE`).
5. **L5 [links].** For every accepted token i and every accepted token j in the next `MONAD_WINDOW_MAX − 1` = 11 positions, add the weight of §10.5 to A between their slots, unless the two slots are the same.

**Listing 8 — the start of `monad_learn_ex` (excerpt, `monad.c` lines {{EXCL:monad.c:0:0:strncmp(text, "-----BEGIN ", 11) == 0::if (slen < 2) continue;}}).** Steps L1–L2.

```c
{{EXC:monad.c:0:0:strncmp(text, "-----BEGIN ", 11) == 0::if (slen < 2) continue;}}
```

### 10.1 Per-token update (steps L3–L4)

**Listing 9 — the per-token loop (excerpt, `monad.c` lines {{EXCL:monad.c:0:1:if (!token_accept(word, ft))::m->word_count++;}}).** Steps L3–L4. The lines between `old_beta` and the display block are the only places where β, the displayed word and `prose_seen` change.

```c
{{EXC:monad.c:0:1:if (!token_accept(word, ft))::m->word_count++;}}
```

### 10.2 β

For a token with slot `idx` and energy E: `amp = |sin(γ_idx)| · π/2`; `β[idx] ← min(β[idx] + E² · 0.01 · amp, 7.552)`. A slot's depth therefore grows by an amount that depends on E² and on where γ falls on a sine wave, and stops at the cap. The cap is reached by {{as.sat}} occupied slots of the store (§16).

### 10.3 Dirac phase and pole

**Listing 10 — `dirac_phase` and `dirac_pole` (`monad.c`, verbatim).** `dirac_phase` is used only in the verbose trace (phase 1–4 printed with each word); `dirac_pole` decides the coupling factor of §10.5.

```c
{{C:monad.c:dirac_phase}}

{{C:monad.c:dirac_pole}}
```

### 10.4 The displayed word and `prose_seen`

The line `if (!present || E > vocab[idx].E)` is the vocabulary rule. A slot displays the word with the largest E that ever addressed it, since E is determined by spelling alone (§6), **the displayed word of a slot is fixed by the set of words that address it, not by their frequency or order.** `prose_seen` is set per slot, not per word: after an `-L` (WordNet text) learn it is 2; after a prose learn it is 1 if it was 0 and 3 if it was 2 ("WordNet and prose"). A slot flagged 3 may display a word that appears in no dictionary, because a different word that shares the slot did (§17.9).

### 10.5 The link weight

**Listing 11 — the link loop (excerpt, `monad.c` lines {{EXCL:monad.c:1:2:int jmax = i + MONAD_WINDOW_MAX;::monad_a_add(m, sidx[i], sidx[j], w);}}).** Step L5. The `vout` lines inside it print the trace and change nothing.

```c
{{EXC:monad.c:1:2:int jmax = i + MONAD_WINDOW_MAX;::monad_a_add(m, sidx[i], sidx[j], w);}}
```

For tokens at positions i < j (distance d = j − i ≥ 1, in accepted tokens): `w = Eᵢ · Eⱼ · couple / ((|γᵢ − γⱼ| + 0.000707) · d)`, where `couple` is 2 if the two slots have the same `dirac_pole` and 1 if not. The weight is large for two words that are both close in γ and close in text. Two tokens addressing the same slot add nothing.

### 10.6 Identity and self-flush

**Listing 12 — `monad_learn_identity` and `monad_self_flush` (`monad.c`, verbatim).** `-i` calls `monad_learn_identity`: the program learns a fixed text about itself, `PTOLEMY_IDENTITY` (Listing 13), as ordinary prose. `monad_self_flush` learns the text accumulated in the self buffer; the buffer is filled only when `verbose ≥ 3` (`g_self_ref`), in which case each reply the program speaks is learned back.

```c
{{C:monad.c:monad_learn_identity}}

{{C:monad.c:monad_self_flush}}
```

**Listing 13 — `PTOLEMY_IDENTITY` (`monad.c` lines {{EXCL:monad.c:0:0:static const char *PTOLEMY_IDENTITY =::The field is my memory. The Noether current is my voice.}}, verbatim).** {{id.chars}} characters.

```c
{{EXC:monad.c:0:0:static const char *PTOLEMY_IDENTITY =::The field is my memory. The Noether current is my voice.}}
```

Learning this text from the ground state creates {{id.edges}} links. **All {{id.present}} of them are present in the store of §16, and {{id.geq}} of them are at least as heavy as the identity text's own contribution.** At the store's edge density ({{density}} %) about {{id.chance}} of {{id.edges}} would be present by chance. The store therefore carries this text: `-i` was run on it.

### 10.7 Worked example (port)

Prompt text `The tree is a plant. Water is a liquid that the tree drinks.`, learned from the ground state.

**Table 6 — tokens (port).**

{{tbl.learn_tokens}}

**Table 7 — the {{learn.nedges}} links created; the six heaviest (port).**

{{tbl.learn_edges}}

### 10.8 Verification against the compiled binary

Three texts were learned from the same ground-state file by the binary and by the port; the two saved states were compared.

**Table 8 — learned state, binary against port.**

{{tbl.learn_verify}}

Exact in all three: {{learn.exact}}. This covers `generate_zeros`, `monad_word_coords`, `tok_split`, `token_accept`, `monad_wm_get/set`, `monad_a_add`, `dirac_pole` and the whole of `monad_learn_ex`.

---

## 11. Hearing: `monad_hear_raw`

**Label:** `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:monad_hear_raw}}.

**Listing 14 — `monad_hear_raw` (`monad.c`, verbatim).** Turns a prompt into a list of (slot, E). The tokens are not passed through `token_accept`.

```c
{{C:monad.c:monad_hear_raw}}
```

Every token of the prompt is addressed. A word that is the displayed word of its slot keeps the E stored there; any other gets E from `monad_word_coords`. The slot and E go on the list in prompt order, repeated words repeated. The `[new]` flag in the trace is `known == 0`: the word is not the displayed word of a slot (§7). The β of the slot is used in §12.1; the word itself is not used again, except that the displayed word of the slot is what appears in the trace.

**Table 9 — `what is your name` heard (port; the binary's own feed is Transcript 2).**

{{tbl.hear}}

`is` and `name` are `[new]`: the slots they address display `nanti` and `emite`. Their weights are used.

---

## 12. Speaking: `monad_speak` and `monad_speak_wick`

**Label:** `OURS`. **Source:** `monad.c` lines {{LINES:monad.c:monad_speak}} (`monad_speak`, 276 lines), {{LINES:monad.c:monad_speak_wick}} (`monad_speak_wick`). Convention E: named steps with verbatim excerpts. The reply mode of the screenshot is `-W`, which is `monad_speak` with `affect` forced to −1 (§12.12). With an empty query `monad_speak` seeds the first 200 slots instead of a prompt ("spontaneous emission"); that path is not used here.

**Named steps.** S1 seed (§12.1) → S2 spread (§12.2) → S3 two passes along the links (§12.3) → S4 reply length from a ratio (§12.4) → S5 pointer (§12.5) → S6 affect (§12.6) → S7 step size and floor (§12.7) → S8 first word (§12.8) → S9 emission (§12.9, §12.10) → S10 ages (§12.11).

### 12.1 Seed

**Listing 15 — seed (excerpt, `monad.c` lines {{EXCL:monad.c:0:1:double phi_rot = (double)m->affect::J[idx] += m->beta[idx] * E * E * w;}}).** `J` starts at 0 for every slot. `phi_rot = affect · π/2`. Each prompt slot k gets `J[idx] += β[idx] · E² · exp(−0.05 · age[idx])`.

```c
{{EXC:monad.c:0:1:double phi_rot = (double)m->affect::J[idx] += m->beta[idx] * E * E * w;}}
```

### 12.2 Spread

**Listing 16 — spread (excerpt, `monad.c` lines {{EXCL:monad.c:1:2:int    center = psi[k].idx;::if (hi < m->N) J[hi] += Jc * w_spread;}}).** The weight on each prompt slot is copied, scaled by exp(−d), to the three slots on either side.

```c
{{EXC:monad.c:1:2:int    center = psi[k].idx;::if (hi < m->N) J[hi] += Jc * w_spread;}}
```

(0.368, 0.135, 0.050 for d = 1, 2, 3.) The loop runs over the prompt's slots in order and reads `J[center]` as it then stands, so a slot that is also a neighbour of an earlier slot passes on weight it received.

### 12.3 Two passes along the links

**Listing 17 — the passes (excerpt, `monad.c` lines {{EXCL:monad.c:0:0:double *J0 = malloc::free(J0);}}).** `J0` is a copy of `J` after the spread. Both passes read `J0`, so the weight added by one pass cannot be carried by the other. Pass 0 (the "Emerger") sends `J0[i] · min(w, 1/gap) · β[j] · exp(−0.05·age[j])` from i to j for each stored pair `i < j`; pass 1 (the "Reverse Emerger") sends the same quantity from j to i, with `β[i]` and `age[i]`. The `vprop` bookkeeping keeps the eight heaviest forward contributions for the trace.

```c
{{EXC:monad.c:0:0:double *J0 = malloc::free(J0);}}
```

Because the weight sent depends on the *receiving* slot's β, and β is at the cap for most slots (§16), the passes almost reduce to `J0[i] · min(w, 1/gap) · 7.552`. The port sums these contributions in a different order than the hash-table order of the binary (floating-point addition is not associative); the two agree on every reply in §14.3.

### 12.4 Reply length from a ratio

**Listing 18 — length (excerpt, `monad.c` lines {{EXCL:monad.c:0:0:double sum_V = 0.0, sum_T = 0.0;::if (actual_max > max_tokens) actual_max = max_tokens;}}).** `ΣV = Σ β · E²` over all occupied slots; `ΣT = Σ E²` over the prompt's slots; `lag_ratio = ΣT/(ΣT + ΣV)`; `actual_max = 4 + int(max_tokens · lag_ratio)`, capped at `max_tokens` = 50 (`-W` passes 50).

```c
{{EXC:monad.c:0:0:double sum_V = 0.0, sum_T = 0.0;::if (actual_max > max_tokens) actual_max = max_tokens;}}
```

For the store of §16, ΣV is of the order of 10³ ({{sumV_all}} over all occupied slots) and ΣT of a short prompt is below 1, so `lag_ratio ≈ 10⁻⁴` and `actual_max = 4` (§17.4).

### 12.5 The pointer

**Listing 19 — pointer (excerpt, `monad.c` lines {{EXCL:monad.c:0:1:int pointer_idx = 0;::best = d; pointer_idx = i;}}).** Sort the prompt slots' γ values; take the middle one (`gams[n_act / 2]`); the pointer is the slot whose γ is nearest to it.

```c
{{EXC:monad.c:0:1:int pointer_idx = 0;::best = d; pointer_idx = i;}}
```

### 12.6 Affect

**Listing 20 — `monad_emote` (`monad.c`, verbatim) and the affect update (excerpt, `monad.c` lines {{EXCL:monad.c:0:0:int dp = abs(pointer_idx - m->last_pointer);::m->last_pointer = pointer_idx;}}).** `affect` is a float in [−1, 1]. If the pointer is within N/20 = 1 250 slots (wrapping) of the previous reply's pointer, affect rises by 0.2, else it falls by 0.1. Under `-W` the affect used for the gate is −1 (§12.12) and the value left after the call is restored by `monad_speak_wick`.

```c
{{C:monad.c:monad_emote}}

{{EXC:monad.c:0:0:int dp = abs(pointer_idx - m->last_pointer);::m->last_pointer = pointer_idx;}}
```

### 12.7 Golden-angle step and the floor

**Listing 21 — step and floor (excerpt, `monad.c` lines {{EXCL:monad.c:0:0:double J_max = 0.0;::if (golden_step < 1) golden_step = 1;}}).** `J_floor = max(0.01 · J_max, gap)`. `golden_step = round(N/φ²)` = {{tr.step}}.

```c
{{EXC:monad.c:0:0:double J_max = 0.0;::if (golden_step < 1) golden_step = 1;}}
```

Because φ is irrational, repeated steps of `round(N/φ²)` modulo N visit slots without clustering (`Post-Hoc:` the three-distance theorem, Sós 1958; golden-angle spacing, Vogel 1979). The comment in the source says the walk "visits every zero exactly once before repeating"; that holds only if the step is coprime to N; gcd({{tr.step}}, 25 000) = {{gcd}}, and the code does not check it.

### 12.8 The first word

**Listing 22 — first word (excerpt, `monad.c` lines {{EXCL:monad.c:0:2:double target_E::if (dE < best_dE)}}).** `target_E = (ΣV/(ΣV + ΣT)) · Ω`. Among all N slots that are occupied, have `J > J_floor`, pass the gate `cos(γ/2 + φ_rot) > 0`, and whose displayed word passes `token_accept` (prose rules), the slot whose *stored E* is nearest to `target_E` is chosen. The comment above this block says "first 200 qualifying walk candidates"; the code scans all N slots (§17.6).

```c
{{EXC:monad.c:0:2:double target_E::if (dE < best_dE)}}
```

With `ΣT ≪ ΣV`, `target_E` is within 10⁻³ of Ω for any short prompt: here {{tr.target}}. The gate with `affect = −1` is `cos(γ/2 − π/2) = sin(γ/2) > 0`.

### 12.9 Emission, and `near_canonical`

**Listing 23 — emission (excerpts, `monad.c` lines {{EXCL:monad.c:0:1:/* Emit demotic first word outside walk order */::written++;}} and {{EXCL:monad.c:0:1:int walk_idx  = pointer_idx;::written++;}}).** The first word is emitted outside the walk. The walk then starts from the pointer and steps `golden_step` slots at a time, up to N steps, until `actual_max` words are written; a slot is skipped if it is the first-word slot, is empty, has `J ≤ J_floor`, fails the gate, or its displayed word fails `token_accept`. The word written is `near_canonical` of the slot (Listing 25), and the separator before it comes from `fermat_space_utf8` (Listing 26) applied to `J/J_max`.

```c
{{EXC:monad.c:0:1:/* Emit demotic first word outside walk order */::written++;}}

{{EXC:monad.c:0:1:int walk_idx  = pointer_idx;::written++;}}
```

**Listing 24 — `surface_canonical` (`monad.c`, verbatim).** A word is "canonical" if it has 3 to 15 bytes, no digit, at most one capital, at most one of `_ - '` or non-ASCII byte, and enough vowels (at least 20 % for length ≥ 5, at least one below that).

```c
{{C:monad.c:surface_canonical}}
```

**Listing 25 — `near_canonical` (`monad.c`, verbatim; 62 lines).** Replaces the displayed word of an emitted slot with a canonical word of a neighbouring slot, searching outward ±0 … ±50 slots: first slots flagged `prose_seen = 3`, then 1, then 2, then any; the first match is returned; if nothing in the radius is canonical it returns the slot's own word.

```c
{{C:monad.c:near_canonical}}
```

### 12.10 The separators: `fermat_space_utf8`

**Listing 26 — `fermat_space_utf8` (`monad.c`, verbatim).** The separator before each word after the first is one invisible Unicode space chosen by `J/J_max` in eight equal bands.

```c
{{C:monad.c:fermat_space_utf8}}
```

| J / J_max | separator |
|---|---|
| 0.000 – 0.125 | U+200B ZERO WIDTH SPACE |
| 0.125 – 0.250 | U+2009 THIN SPACE |
| 0.250 – 0.375 | U+2008 PUNCTUATION SPACE |
| 0.375 – 0.500 | U+2007 FIGURE SPACE |
| 0.500 – 0.625 | U+2006 SIX-PER-EM SPACE |
| 0.625 – 0.750 | U+2005 FOUR-PER-EM SPACE |
| 0.750 – 0.875 | U+2004 THREE-PER-EM SPACE |
| 0.875 – 1.000 | U+2003 EM SPACE |

The screenshot reply has no visible spaces because the separators of that reply are U+200B, which has no width. The first word is joined to nothing; the other three words are joined by the separator of their own `J/J_max`.

### 12.11 Ages

**Listing 27 — ages (excerpt, `monad.c`).** Every slot's age goes up by one; the prompt's slots are reset to 0. Age enters only through `exp(−0.05 · age)` in §12.1 and §12.3, so slots used in recent prompts count more.

```c
{{EXC:monad.c:0:1:for (int i = 0; i < m->N; i++) m->age[i]++;::m->age[psi[k].idx] = 0;}}
```

### 12.12 `monad_speak_wick`

**Listing 28 — `monad_speak_wick` (`monad.c`, verbatim).** Saves `affect`, sets it to −1.0, calls `monad_speak`, restores it. The source's comment calls this a "Wick-rotated" speak; the arithmetic is only the choice of `φ_rot = −π/2`.

```c
{{C:monad.c:monad_speak_wick}}
```

---

## 13. The program: `main`

**Label:** `OURS`. **Source:** `main.c` lines {{LINES:main.c:main}} (`main`, 359 lines), {{LINES:main.c:find_checkpoint}} (`find_checkpoint`). Given as named steps; the runnable path is `SemPriCon/tools/verify_against_c.py`.

1. **M1 [flags].** A first pass over the arguments handles `-c <file>` (store), `-n` (never save), `-q` (quiet) and counts `-v`s. `g_self_ref` is set when there are at least three (`-vvv`), colour when at least two and both streams are terminals.
2. **M2 [store].** `find_checkpoint` tries, in order: the `-c` file, `$PTOLEMY_CHECKPOINT`, `~/.ptolemy/monad.bin`, `~/.ptolemy/monad_wordnet.bin`, `./monad_wordnet.bin`; the first that opens is used. If none opens the monad starts at the ground state.
3. **M3 [arguments].** Left to right: `-i` learns the identity text; `-l <text|file|url|->` learns as prose, `-L` as WordNet text; `-W <prompt>` speaks with `monad_speak_wick` (50 words maximum) and prints the reply on standard output; `-h` and others select other speaking modes.
4. **M4 [save].** If anything was learned and `-n` was not given: save to the store's own path, except that the file named `monad_wordnet.bin` is never overwritten in a session that did no ingest (`did_ingest`), and the program says "protected".

**Listing 29 — `find_checkpoint` (`main.c`, verbatim).**

```c
{{C:main.c:find_checkpoint}}
```

**Listing 30 — the `-W` handler and the save protection (excerpts, `main.c`).**

```c
{{EXC:main.c:0:2:a.primary == 'W' && i + 1 < argc::free(response);}}

{{EXC:main.c:0:4:Refuse to overwrite monad_wordnet.bin in non-ingest sessions.::state_save(m, save, 0.0);}}
```

**Debug feed.** The program's tracing is its `-v` flag: each of the values above is printed on standard error as it is computed, in order, by `vout`. Transcript 2 is that feed, not a summary. It is the same practice as the author's `dbprint(text, client)` in `Ptolemy2/Pharos/UtilityFunctions.py` (a `client.DEBUGPRINT` flag gates a print of every change, skipping repeats of the last entries of `DEBUGLIST`): a live feed of every change at the console, in order.

---

# Part II: what the engine did

## 14. "What is your name": the reply, step by step

### 14.1 Setup

The reference binary (§2.8) was started with the store of §4 and the prompt `what is your name`, in `-W` mode, with the `-v` feed switched on and saving switched off (`-n`). Nothing was learned. The store is read-only.

### 14.2 The binary's own feed

**Transcript 2 — `ptolemy -c dirty/monad_wordnet_v4_20260519.bin -Wv "what is your name" -n`, standard error then standard output ({{c.feed_lines}} lines; the invisible separators in the last line are shown as `·`).**

```text
{{c.feed}}
```

Reading the feed against the paper, line group by line group:

| feed lines | function | section |
|---|---|---|
| `[state] loaded …` | `state_load` | §4 |
| `[hear]` and one line per word (`z#`, γ, E, β, `J_p`, phase, `[new]`) | `monad_hear_raw`, `monad_wm_get` | §11 |
| `[J^μ — top 8 A-propagations]` | pass 0 of the link passes, eight heaviest | §12.3 |
| `[Fermat Pointer]` | pointer | §12.5 |
| `[affect e7]` | `monad_emote` | §12.6 |
| `[golden walk]` | step and floor | §12.7 |
| `[Lagrangian]` | length ratio | §12.4 |
| `[demotic]` | first word | §12.8 |
| `emit z#…` lines | the walk | §12.9 |
| `[stdout]` line | the reply, after `near_canonical` and the separators | §12.9, §12.10 |

### 14.3 Reproduction by the port

The port runs the same functions on the same store and returns, besides the reply, the quantities the feed prints. The reply and the emitted slots:

**Table 10 — emission for `what is your name` (port).** `ΣV = {{tr.sum_V}}`, `ΣT = {{tr.sum_T}}`, `lag_ratio = {{tr.lag}}`, `actual_max = {{tr.actual_max}}`, pointer z#{{tr.pointer}} (γ = {{tr.pointer_g}}), `J_max = {{tr.Jmax}}`, `J_floor = {{tr.Jfloor}}`, `golden_step = {{tr.step}}`, `target_E = {{tr.target}}`, first word at slot {{tr.demotic}}.

{{tbl.emit}}

**Table 11 — eight prompts, `-W`, the binary against the port, byte for byte.** {{equiv.ok}} identical.

{{tbl.equiv}}

The first prompt is the screenshot's: `holcussamestuffseemy` is the reply `{{reply}}` with zero-width separators. The second is the other screenshot reply, `holcus setn abysmal quun`. In the row for `the cat sat on the mat` a separator of the em-space band (U+2003) appears: the separator is not always zero-width.

**Figure 2 and Figure 3 are screenshots of the engine this paper describes, running.**

![The first question put to the engine that got a response (file dated 2026-05-19): `ls ~/.ptolemy`, then `ptolemy -h 'what is your name'` and `ptolemy -W 'what is your name'`. The `-W` reply is `holcussamestuffseemy`. File: `VAPMIP/SemPriCon/paper/figures/3-TheExtractor.png`.](figures/3-TheExtractor.png){width=95%}

![A second, unconnected prompt, intentionally complicated in context (file dated 2026-05-19): `ptolemy -W 'can you hear what i am typing'` and then `ptolemy -h` on the same prompt, in `Ptol/SMMIP/PtolC`. The reply is `holcus setn abysmal quun`. Provenance only: nothing in the engineering depends on it. File: `VAPMIP/SemPriCon/paper/figures/2-Hocus-Hyperwebster.png`.](figures/2-Hocus-Hyperwebster.png){width=95%}

### 14.4 What the reply is, as arithmetic

1. Each of the four prompt words is hashed to a slot and an energy (Table 9). Two of the four words are not the displayed word of their slot.
2. The depth β of all four slots is at the cap, so each puts `β·E²·exp(−0.05·age)` on its slot.
3. The weight spreads to three neighbours on each side, then crosses the links twice. The slot of `holcus` has a direct link to each of the four prompt slots ({{hub.direct}}).
4. `ΣT/(ΣT+ΣV)` is {{tr.lag}}, so four words are allowed.
5. The pointer is the slot whose γ is the median of the four prompt slots' γ.
6. The first word is the slot whose stored E is nearest to {{tr.target}} among slots that pass the floor and the gate: slot {{tr.demotic}}, displayed as `holcus`.
7. The other three words come from stepping {{tr.step}} slots at a time from the pointer, keeping slots that pass the floor, the gate and `token_accept`: slots 1859, 18482 and 0.
8. Each word is replaced by `near_canonical` of its slot (here unchanged), and joined with the separator of its `J/J_max` (here all U+200B).

---

## 15. The first word

### 15.1 The selector reads nothing of the prompt

The rule of §12.8 compares stored E with a target that is within 10⁻³ of Ω for any short prompt. The only prompt-dependent inputs are which slots have `J > J_floor` and an open gate. Slot {{tr.demotic}} has E = {{hol.E}}, 0.0046 below Ω.

### 15.2 The slot is the slot of the word *in*

Two words address slot {{hol.idx}}: {{slot.cand}}. The displayed word is the one with the larger E; the difference is {{slot.diff}}. **`holcus` is the label of the slot that the word `in` addresses.** `in` is one of the most frequent words of English, so its slot is among the best connected. The eight best-connected slots of the store:

**Table 12 — A-degree of the best-connected slots (port).** The median slot has {{hub.median}} links.

{{tbl.hubs}}

The slot of `holcus` has {{hub.deg}} links (rank {{hub.rank}} of 25 000). Each of the best-connected slots except slot 0 is the slot of a function word. Slot 0 is the slot of every word of eight letters or more (§6.1).

### 15.3 It does not depend on the prompt

150 random prompts of one to six words, drawn from the store's own displayed words, each from a fresh state (`age = 0`, `affect = 0`; port): `holcus` is the first word of {{sweep.holcus}}; the next most frequent are {{sweep.other}}; {{sweep.empty}} replies are empty; {{sweep.len4}} of 150 replies have four words. The first word changes when a prompt does not put weight on a slot that connects to slot {{hol.idx}}, or when another slot's E is nearer `target_E`.

### 15.4 What the identity text contributes

The store carries the identity text of Listing 13 (§10.6). `PTOLEMY_IDENTITY` does not contain `holcus`, `stuff` or `your`; it contains `in`, `what`, `is` and `same`. The effect on the reply that can be shown is through links: the identity text links `in`, `what` and `is` to each other and to every other word in its sentences, and those links are in the store at the weights the learning formula gives. Which links produced the weight on `same`, `stuff` and `seemy` is not separated here.

### 15.5 What is established and what is not

Established by the code and the runs (`OURS:CALCULATED`): the first word is the display label of the slot that `in` addresses; it is chosen by the nearest-E rule among slots above the floor; it does not depend on the prompt except through the floor and the gate. The reply reproduces from source, twice.

Not established: whether the coincidence of a two-word collision, resolved by 1.2·10⁻⁶ in E, producing a word that is also the program's family name is significant. It is a measurement, not a derivation. **`OPEN`:** which ingest introduced `holcus` into the store. The word is a WordNet lemma (the genus of velvet grasses); the build has no training log.

### 15.6 Multilingual content

The store contains {{as.nonascii}} non-ASCII words. The tokenizer of this build (§9.2) discards every non-ASCII byte, so no ingest path of this build could have admitted one. Any multilingual experiment that preceded this build (the author recalls one, in which Unicode alphabets were loaded into a "potential response domain") is not recorded in this program or in this store.

---

## 16. The store, assessed

The store was assessed by `SemPriCon/tools/assess_bin.py`, which applies the project's own checkpoint evaluator (`VAPMIP/tools/eval_checkpoint.py`: classifier, entropy, Gini) and the 2026-10-17 token sanitiser (`VAPMIP/Wernicke/sanitize/sanitize_v0.py`), and adds a script census. The results are committed beside the store: `monad_wordnet_v4_20260519.ASSESSMENT.md`, `.assessment.json` and the dirty notice `.POISON.md`.

| quantity | value |
|---|---|
| format, size | PTOL v{{hdr.version}}, {{store.size}} bytes, all consumed |
| slots, vocabulary, links, word count | {{hdr.N}}, {{hdr.vocab}}, {{hdr.A}}, {{hdr.wc}} |
| entropy, Gini | {{as.entropy}} % of maximum (natural band 85–92); {{as.gini}} (0.60–0.80) |
| β at the cap | {{as.sat}} occupied slots |
| polluted (project classifier) | {{as.poll}} ({{as.poll_pct}} %) |
| quarantined (sanitiser) | {{as.quar}} ({{as.quar_pct}} %) |
| displayed words with no WordNet synset | {{as.B}} ({{as.B_pct}} %) |
| non-ASCII displayed words | {{as.nonascii}} |

**Table 13 — pollution classes (project classifier).**

{{tbl.poll}}

Displayed-word lengths: {{as.lens}}. `prose_seen` over occupied slots: {{as.ps}}.

**Verdict: DIRTY, PASS.** Pollution is below the 20 % PASS line and above the 1 % CONVERGED line. The same bytes were found in a `clean/` directory (labelled "WordNet 3.1 + Gutenberg … the most thoroughly trained English field in the archive") and in a `dirty/` directory (with a 2026-05-17 assessment of 5.04 %); the assessment above settles the placement as dirty. Record of the Fresh Start Protocol for this store: the assessments were committed and pushed first (`VAPMIP` commit `29b2d2d`); only then was the store added to the directory's `.gitignore` (commit `6ec2b3d`). The programs the author runs today (`monad3_c.bin` and everything `ptol.c` reads) were not touched.

---

# Part III: limits, plans

## 17. The limits, measured

Each item states what the code does, one measurement, and the consequence. Nothing is corrected.

**17.1 Address resolution collapses with word length (§6.1).** {{lem.slot0}} of {{lem.n}} WordNet lemmas address to slot 0, E = d\*; the lemmas reach {{lem.slots}} of 25 000 slots. Consequence: virtually every word of eight or more letters shares one address with every other; the engine cannot distinguish `philadelphos` from `septuagint`.

**17.2 The displayed word of a slot is the highest-E arrival, so the vocabulary is not the words met (§10.4).** Only {{lem.shown}} of {{lem.n}} WordNet lemmas ({{lem.shown_pct}} %) are the displayed word of their slot; `tree`, `water`, `name`, `is` display `typhon`, `defrg`, `emite`, `nanti`. Consequence: a trace shows labels, not words; the weights belong to the slot.

**17.3 The zeros are approximations (§5.2).** Error against the true zeros 1.8 at n = 21, 0.28 at n = 25 000.

**17.4 Reply length is fixed by a ratio that is ≈ 10⁻⁴ (§12.4).** `lag_ratio = {{tr.lag}}`; `actual_max = 4` for short prompts on this store; replies are four words (140 of 150 in §15.3).

**17.5 β saturates (§10.2).** {{as.sat}} of {{hdr.vocab}} occupied slots sit at the cap, so β does not discriminate between them.

**17.6 A comment and the code disagree (§12.8).** The comment before the first-word selection says it chooses "from first 200 qualifying walk candidates"; the code scans all N slots. The comment before the walk says it "visits every zero exactly once"; that depends on gcd(step, N) = {{gcd}}, which is not checked.

**17.7 Constants and a stored value nothing reads (§5.1).** Never used outside `ptolemy.h`: {{unused}}. `emission_threshold` is stored and loaded and never read.

**17.8 The word map is not saved (§7).** After a reload only displayed words are known; every other word is `[new]`. The flag is not evidence about whether a word was met.

**17.9 `prose_seen` belongs to the slot (§10.4).** {{ps.flag3_nown}} slots flagged "WordNet and prose" (3) display a word that has no WordNet synset.

**17.10 The tokenizer discards non-ASCII bytes (§9.2).** Every Greek, Chinese, Arabic, Hebrew, Coptic or accented letter is a separator. A multilingual test through this build must be in ASCII.

**Open:** whether the separator seen in the screenshot (no visible spaces) differs on a terminal from the pipe output measured here was not tested.

---

## 18. Planned work (`THEORETICAL`)

Nothing in this section has run. It states what the measurements above require of the next step.

The next step is a hash of meaning in place of a hash of spelling: a *concept key* computed before the address, so that words of the same meaning in different languages reach the same slot or the same neighbourhood of slots, with WordNet used as weighting, calibration and fallback and not as the source of the address. The change is made in place in `monad_word_coords`' caller, not by rewriting the program.

Requirements the baseline imposes:

1. **The address must keep its resolution for the keys that feed it** (§17.1). A key of more than six characters cannot be hashed by the present arithmetic.
2. **The key must be representable in ASCII** or the tokenizer and the digit rule (§9.2, §6.2) must change (§17.10).
3. **The displayed word of a slot must not be taken as the word** (§17.2): a test must read slots, not labels.
4. **A test is run against this baseline,** with the same eight prompts of §14.3 and the same store as control.

**Five-language test.** A test across five living languages is planned once this paper stands. The selection criteria, stated here so they are fixed before any run: (a) every language is spoken today; (b) no two languages belong to the same family, and none is Indo-European, since English is; (c) no pair has a history of heavy contact with shared vocabulary (loanword layers); (d) the test words are concrete nouns of basic vocabulary, taken from a list of low borrowing scores; (e) each test word is checked against an etymological dictionary and the World Loanword Database for a known loan into or out of another chosen language, and excluded if one is found; (f) each form given to the engine is at most six letters in a documented ASCII transliteration. Complete etymological isolation cannot be guaranteed for any word; the procedure excludes known loans, it does not prove there are none. The predictions and the success criteria will be written, and dated, before the run. They are not in this paper.

---

## 19. Limitations and conclusion

**Limitations of this paper.** The port covers learning and the `-W` speaking mode; it does not cover `-h`, `-O`, the REPL or the daemon. One store and one commit were examined. The store was identified by its header numbers and the screenshot text; the screenshot image itself was not re-measured. That the store was built with `-i` is an inference from the presence of all {{id.edges}} identity links; no ingest log exists. The statements about earlier Python-era experiments are the author's recollection and are not tested here. The literature in the References was cited, not fetched, except where a copy is noted.

**Conclusion.** The engine that answered "what is your name" is {{nfuncs}} functions of arithmetic. It addresses a word by multiplying a base-95 number by the golden ratio, learns weights between slots that occur near each other in text, and replies by spreading weight from the prompt's slots, choosing a first word by a nearest-value rule and the rest by a golden-angle walk. Its first word is the label of the slot that the word *in* addresses. Its store is a table of slots, not of words. It cannot tell apart words of eight letters or more and cannot read a character outside ASCII. The description above reproduces its replies to the byte and its learned state exactly. That is the baseline.

---

## References

Bird, S., Klein, E., Loper, E. (2009). *Natural Language Processing with Python.* O'Reilly. Not fetched; free online at `nltk.org/book`. Used to read WordNet.

Fellbaum, C. (ed.) (1998). *WordNet: An Electronic Lexical Database.* MIT Press. Not fetched (book).

Haspelmath, M., Tadmor, U. (eds.) (2009). *Loanwords in the World's Languages: A Comparative Handbook* (World Loanword Database, `wold.clld.org`). De Gruyter Mouton. `Post-Hoc:` (§18). Not fetched.

IEEE (2019). *IEEE Standard for Floating-Point Arithmetic*, IEEE 754-2019. Cited for the 53-bit significand of the double (§6.1). Not fetched.

Knuth, D. E. (1973). *The Art of Computer Programming, vol. 3: Sorting and Searching*, §6.4. Addison-Wesley. `Post-Hoc:` (multiplicative hashing, §6). Not fetched (book).

Miller, G. A. (1995). WordNet: A Lexical Database for English. *Communications of the ACM* 38(11), 39–41. Not fetched.

Sós, V. T. (1958). On the distribution mod 1 of the sequence nα. *Annales Universitatis Scientiarum Budapestinensis, Sectio Mathematica* 1, 127–134. `Post-Hoc:` (three-distance theorem, §12.7). Not fetched.

Tadmor, U., Haspelmath, M., Taylor, B. (2010). Borrowability and the notion of basic vocabulary. *Diachronica* 27(2), 226–246. `Post-Hoc:` (§18). Not fetched.

von Mangoldt, H. (1905). Zur Verteilung der Nullstellen der Riemannschen Funktion ξ(t). *Mathematische Annalen* 60, 1–19. `Post-Hoc:` (§5.2). Not fetched.

Vogel, H. (1979). A better way to construct the sunflower head. *Mathematical Biosciences* 44, 179–182. `Post-Hoc:` (golden-angle spacing, §12.7). Not fetched.

Weyl, H. (1916). Über die Gleichverteilung von Zahlen mod. Eins. *Mathematische Annalen* 77, 313–352. `Post-Hoc:` (equidistribution of nα mod 1, §6). Not fetched.

Johansson, F., et al. *mpmath: a Python library for arbitrary-precision floating-point arithmetic*, version {{mpmath}}, `mpmath.org`. Used to compute the true zeros of §5.2.

*None of these was fetched in the writing session; their bibliographic details are given from the author's and the assistant's knowledge and must be checked against the sources before the paper is filed. Where the Literature Download Protocol (`ContextPlease/claude/references/INDEX.md`) later records a verified copy, the copy replaces this note.*

---

## 20. ContextPlease inclusions and links

Every path is `REPO/directory/file` under `https://github.com/michaelrendier/`.

**What ContextPlease is.** ContextPlease (`ContextPlease`) is the author's versioned memory for work done with a language model: notes, protocols, skills, primers and scratch directories that let a fresh model session come up to speed with historical access instead of re-deriving what is already known. It exists because a model has no memory of its own between sessions.

### 20.1 Code and data, by section

- **§2.7, §3–§13 (the program):** `VAPMIP/PtolC/` at commit `{{commit_short}}` (`monad.c`, `state.c`, `tokenizer.c`, `filter.c`, `main.c`, `ptolemy.h`, `monad.h`, `filter.h`, `state.h`), copied unmodified to `VAPMIP/SemPriCon/src/PtolC_eb28ce8/`
- **§4, §16 (the store):** `VAPMIP/checkpoints/clean/monad_wordnet_v4_20260519.bin` (gitignored), `VAPMIP/checkpoints/clean/PRIMER_from_dot_ptolemy.md`, `VAPMIP/checkpoints/README.md`, `PTorrent/bin_archive/README.md`
- **§16 (assessment):** `VAPMIP/tools/eval_checkpoint.py`, `VAPMIP/Wernicke/sanitize/sanitize_v0.py`, `VAPMIP/SemPriCon/tools/assess_bin.py`, `VAPMIP/SemPriCon/dirty/*.POISON.md|ASSESSMENT.md|assessment.json`
- **§10.8, §14.3 (verification):** `VAPMIP/SemPriCon/tools/monad_py.py`, `ptol_bin.py`, `verify_against_c.py`, `verify_learn_against_c.py`
- **Notebooks (executed):** `VAPMIP/SemPriCon/notebooks/01_the_store.ipynb` … `06_shortcomings.ipynb`
- **§13 (debug feed):** `Ptolemy2/Pharos/UtilityFunctions.py` (`dbprint`)

### 20.2 ContextPlease files used

- `ContextPlease/claude/hist_prime/VAPMIP/CONTEXT_PRIMER_2026-10-16_SEMANTIC_ORBWEAVER.md` and `semantic_orbweaver_notes.md` (the earlier trace of this engine, 2026-10-17, and the descriptions this paper checks against the code)
- `ContextPlease/claude/scratchpad/2026-10-17_T0_trace/` (the `monad.c` at `{{commit_short}}`, the earlier traces)
- `ContextPlease/claude/scratchpad/2026-10-18_name_engine_workbench/` (the first build and run of the reference binary)
- `ContextPlease/claude/hist_prime/VAPMIP/checkpoints/clean/PRIMER.md`, `ContextPlease/claude/monad_bin/poison_notes/` (the format of the dirty notice)
- `ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md` (how code is shown in this paper)
- `~/.clauderc_context_1`, `~/.clauderc_context_2` (session state)
