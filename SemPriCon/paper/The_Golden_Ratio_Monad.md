# The Golden-Ratio Monad

### A complete mechanical account of the engine that answered "what is your name": `ptolemy` v1.215 (`PtolC/monad.c`), its store, its replies, and its measured limits

**Cody Michael Allison** (Michael Rendier), independent researcher · the.wandering.god@gmail.com · ORCID 0009-0007-7239-6760\
**Written by an AI assistant:** Claude Sonnet 5.5 (`claude-sonnet-5-5`), with the author's `cs-paper-code-conventions` skill running (`ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md`)\
**Date:** 2026-10-18 · **Status:** first full draft · **Code:** `VAPMIP/SemPriCon` · **Reference source:** `VAPMIP/PtolC/`, commit `eb28ce8` (2026-05-18) · **Repository prefix:** every path below, written `REPO/directory/file`, lives under `https://github.com/michaelrendier/`

---

> ## Read this first: who wrote this, and how
>
> **The assistant.** This paper was written by a transformer language model, Claude Sonnet 5.5 (`claude-sonnet-5-5`), working with the author's `cs-paper-code-conventions` skill active; the skill decides how code is shown in a paper. Every number in the text that comes from code was produced by `VAPMIP/SemPriCon/paper/evidence.py` when `VAPMIP/SemPriCon/paper/make_paper.py` last ran; none is typed in by hand. Every C listing is cut from the source file by function name when the paper is built.
>
> **The author.** The author is a software engineer, not a trained mathematician or linguist, and says so. Every statement that is not attributed to a cited source should be read as unverified until an expert has checked it.
>
> **The method.** The author's method is to give the assistant measurements to take ("run it", "chase that to its source") rather than results to reach. In this work he also stated his own expectations of the system; the paper reports the measurements as found, whichever way they fall. This is a safeguard, not a guarantee. The author's standing instruction is that **the code is authoritative to this paper**: where a comment, a wiki page or a recollection disagrees with the source at commit `eb28ce8`, the paper describes the source.
>
> **What kind of paper this is.** An engineering white paper about one finished program, shown running. It contains no proofs and makes no prediction beyond §18, which is labelled `THEORETICAL`. It changes nothing in the code it describes: the reference binary is built from the unmodified source, the store it loaded is read-only, and a second implementation (a line-for-line Python port) is checked against the first.

---

## Abstract

A small language engine is easiest to trust when every step between a prompt and a reply is arithmetic that a reader can follow and re-run. The May-2026 C monad of this project is such an engine: 65 functions in five C files, no trained weights, no gradient descent, no network. It hashes a word's spelling to one of 25 000 positions by multiplying a base-95 number by the golden ratio; it learns by adding weights between positions that occur near each other in text; and it replies by spreading weight from the prompt's positions through those links and reading positions out in golden-angle order. It once answered "what is your name" with `holcus same stuff seemy`. No complete account of how exists: the descriptions on file (comments, wiki pages, session notes) disagree with the code and with each other. This paper is that account. It describes each function in the order the program runs, identifies the store the program loaded (24,485 occupied positions, 6,825,748 weighted links, byte-identical to the screenshot's header), reproduces the reply from source, and checks a line-for-line Python port against the compiled binary (8 of 8 replies identical; learned state exact). It then measures what the engine's address function, word display rule and constants do, and records ten limits as results. The first word of the reply is explained mechanically: it is the display label of the position that the word *in* addresses to. The store contains no non-ASCII word, and the program's tokenizer cannot admit one. The source is not changed, tuned or improved here; the account is the baseline against which the next version is measured.

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

**Reference build.** The *reference binary* is `ptolemy` built from the unmodified source at commit `eb28ce8`. The *port* is `SemPriCon/tools/monad_py.py`.

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

One ThinkPad X1 Carbon (6th generation), Intel Core i7-8550U, no GPU, no network, Linux 6.8. The evidence run that produced this text took 75 s.

### 2.7 Authentication: what "authoritative" refers to

The paper's authority is the following set of files and the checksum of the store, nothing else. A reader can check each line.

| file at `eb28ce8` | git blob (12) | sha256 (16) | lines |
|---|---|---|---|
| `PtolC/monad.c` | 774e8731a39b | 14d2c3ebfa608e96 | 1401 |
| `PtolC/state.c` | 9e922020fd65 | 772c352f5b6eb72b | 385 |
| `PtolC/tokenizer.c` | 97172b3c098e | 31cf77ef2b1ed262 | 51 |
| `PtolC/filter.c` | 43aa2d6ca55b | 37cf76e378630c7a | 209 |
| `PtolC/main.c` | c6af9e58e8cf | eaf8fb07fc8120d8 | 691 |
| `PtolC/ptolemy.h` | d5b317752133 | 4d523fca81f25450 | 84 |
| `PtolC/monad.h` | 2353f7103d51 | dc7d4e47e2e2e282 | 186 |
| `PtolC/filter.h` | 8267e4696fa9 | 6407d577374685be | 71 |
| `PtolC/state.h` | 161fad45780a | 80894fb7e3ecf69c | 34 |

The store: `monad_wordnet_v4_20260519.bin`, sha256 `66f70c70dcd8d860fa4af01833cf5c6e4c376194c510b5be156fe0c6064faf31`, 110,040,527 bytes, read in full by the reader of §4 (every byte accounted for: yes). Commit `eb28ce8db70f796088aa5eb3e64cc75a787b41ea` ("v1.215: Fermat emotional lattice + Lagrangian word count + REPL (-r)").

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

| file | function | lines | length | § |
|---|---|---|---|---|
| `monad.c` | `sbuf_append` | 51–61 | 11 | — |
| `monad.c` | `strip_ansi` | 64–76 | 13 | — |
| `monad.c` | `vout` | 79–94 | 16 | — |
| `monad.c` | `generate_zeros` | 146–166 | 21 | 5 |
| `monad.c` | `monad_word_coords` | 170–188 | 19 | 6 |
| `monad.c` | `fnv1a` | 192–197 | 6 | 7 |
| `monad.c` | `monad_wm_get` | 201–225 | 25 | 7 |
| `monad.c` | `monad_wm_set` | 227–253 | 27 | 7 |
| `monad.c` | `a_key` | 257–261 | 5 | 8 |
| `monad.c` | `monad_a_add` | 263–291 | 29 | 8 |
| `monad.c` | `monad_a_get` | 293–305 | 13 | 8 |
| `monad.c` | `monad_create` | 309–327 | 19 | 9 |
| `monad.c` | `monad_destroy` | 329–337 | 9 | 9 |
| `monad.c` | `monad_ground_init` | 339–343 | 5 | 9 |
| `monad.c` | `monad_resize` | 345–362 | 18 | 9 |
| `monad.c` | `monad_emote` | 364–369 | 6 | 12.6 |
| `monad.c` | `monad_self_flush` | 373–379 | 7 | 10.6 |
| `monad.c` | `monad_learn_identity` | 381–389 | 9 | 10.6 |
| `monad.c` | `dirac_phase` | 402–409 | 8 | 10.3 |
| `monad.c` | `dirac_pole` | 411–414 | 4 | 10.3 |
| `monad.c` | `monad_learn_ex` | 418–549 | 132 | 10 |
| `monad.c` | `monad_learn` | 551–554 | 4 | 10 |
| `monad.c` | `monad_hear_raw` | 560–604 | 45 | 11 |
| `monad.c` | `surface_canonical` | 619–638 | 20 | 12.9 |
| `monad.c` | `near_canonical` | 640–701 | 62 | 12.9 |
| `monad.c` | `fermat_space_utf8` | 707–726 | 20 | 12.10 |
| `monad.c` | `vpcmp` | 734–738 | 5 | 12.3 |
| `monad.c` | `monad_speak` | 740–1015 | 276 | 12 |
| `monad.c` | `monad_speak_wick` | 1024–1031 | 8 | 12.12 |
| `monad.c` | `monad_speak_oct` | 1046–1214 | 169 | n/a (not on the path) |
| `monad.c` | `monad_hear_fermat` | 1220–1256 | 37 | n/a |
| `monad.c` | `monad_status` | 1260–1283 | 24 | n/a |
| `monad.c` | `monad_lookup` | 1285–1302 | 18 | n/a |
| `monad.c` | `monad_health` | 1304–1401 | 98 | n/a |
| `state.c` | `read32` | 24–27 | 4 | — |
| `state.c` | `read16` | 29–32 | 4 | — |
| `state.c` | `read64d` | 34–37 | 4 | — |
| `state.c` | `next_pow2` | 40–45 | 6 | — |
| `state.c` | `state_load` | 49–201 | 153 | 4 |
| `state.c` | `state_save` | 205–276 | 72 | 4 |
| `state.c` | `state_load_vocab` | 280–385 | 106 | n/a (Face layer) |
| `tokenizer.c` | `tok_split` | 10–44 | 35 | 9 |
| `tokenizer.c` | `tok_free` | 46–51 | 6 | 9 |
| `filter.c` | `rules_for` | 31–36 | 6 | — |
| `filter.c` | `filetype_from_ext` | 40–65 | 26 | — |
| `filter.c` | `filetype_name` | 67–77 | 11 | — |
| `filter.c` | `is_pure_numeric` | 81–87 | 7 | — |
| `filter.c` | `is_hex_string` | 89–102 | 14 | — |
| `filter.c` | `is_uuid` | 105–120 | 16 | — |
| `filter.c` | `is_base64_chunk` | 123–135 | 13 | — |
| `filter.c` | `vowel_count` | 137–145 | 9 | — |
| `filter.c` | `high_digit_ratio` | 147–154 | 8 | — |
| `filter.c` | `is_long_allcaps` | 157–168 | 12 | — |
| `filter.c` | `token_accept` | 172–209 | 38 | 9 |
| `main.c` | `run_eval` | 50–83 | 34 | — |
| `main.c` | `init_ptolemy_dir` | 89–108 | 20 | — |
| `main.c` | `parse_arg` | 117–137 | 21 | — |
| `main.c` | `reanchor_english` | 149–189 | 41 | — |
| `main.c` | `read_file` | 193–209 | 17 | — |
| `main.c` | `read_stdin` | 211–222 | 12 | — |
| `main.c` | `read_url` | 224–249 | 26 | — |
| `main.c` | `find_checkpoint` | 251–284 | 34 | — |
| `main.c` | `print_version` | 286–297 | 12 | — |
| `main.c` | `print_usage` | 299–329 | 31 | — |
| `main.c` | `main` | 333–691 | 359 | 13 |

The reply of §14 is produced by exactly this call chain: `main` → `state_load` → `monad_speak_wick` → `monad_speak` → { `monad_hear_raw` → `monad_wm_get` → `monad_word_coords`; `dirac_*` not used; `near_canonical` → `surface_canonical`; `fermat_space_utf8`; `token_accept` }. The store the reply used was built by earlier `monad_learn_ex` calls (`-l`, `-L`, `-i`).

---

## 4. The store: `state_load` and `state_save`

**Label:** `OURS`. **Source:** `state.c` lines 49–201 (`state_load`), 205–276 (`state_save`). Both are long, so they are given as named steps (convention E). The runnable reader is Listing 1.

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

def load(path, with_edges=True):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"PTOL":
        raise ValueError(f"bad magic {raw[:4]!r}")
    ver, N, vc, ac, wc = struct.unpack_from("<5I", raw, 4)
    (thr,) = struct.unpack_from("<d", raw, 24)
    pos = 32
    affect = 0.0
    if ver >= 4:
        (affect,) = struct.unpack_from("<f", raw, pos)
        pos += 4
    beta = np.frombuffer(raw, dtype="<f8", count=N, offset=pos); pos += 8 * N
    age = np.frombuffer(raw, dtype="<i4", count=N, offset=pos); pos += 4 * N
    vocab = []
    for _ in range(vc):
        idx, wlen = struct.unpack_from("<IH", raw, pos); pos += 6
        (E,) = struct.unpack_from("<d", raw, pos); pos += 8
        hs = gs = ps = 0
        if ver >= 2:
            hs, gs = raw[pos], raw[pos + 1]; pos += 2
        if ver >= 3:
            ps = raw[pos]; pos += 1
        word = raw[pos:pos + wlen].decode("utf-8", errors="replace"); pos += wlen
        vocab.append((idx, word, E, hs, gs, ps))
    edges = None
    if with_edges:
        dt = np.dtype([("i", "<u4"), ("j", "<u4"), ("w", "<f8")])
        edges = np.frombuffer(raw, dtype=dt, count=ac, offset=pos)
    end = pos + 16 * ac
    return dict(version=ver, N=N, vocab_size=vc, A_size=ac, word_count=wc, threshold=thr,
                affect=affect, beta=beta, age=age, vocab=vocab, edges=edges,
                bytes_total=len(raw), bytes_consumed=end)
```

**Transcript 1 — the store of this paper, read by Listing 1.**

    > d = ptol_bin.load("dirty/monad_wordnet_v4_20260519.bin")
    > d["version"], d["N"], d["vocab_size"], d["A_size"], d["word_count"], d["affect"]
    (4, 25,000, 24,485, 6,825,748, 121,914,388, -1.0)
    > d["bytes_consumed"] == d["bytes_total"]
    yes

The numbers are the ones printed by the program in the screenshot (`vocab=24485  A=6825748  wc=121914388`).

---

## 5. Constants and the zeros

### 5.1 Constants (`ptolemy.h`)

**Label:** `OURS`. The constants are defined once; the header says they "mirror `Philadelphos/monad.py` exactly". The right-hand column counts how often each name occurs in the program's other `.c` files.

| constant | value | uses outside `ptolemy.h` |
|---|---|---|
| `MONAD_N_DEFAULT` | 25000 | 2 |
| `MONAD_L_GROUND` | −1.888 | 4 |
| `MONAD_D_STAR` | 0.24600 | 5 |
| `MONAD_OMEGA_ZS` | 0.56714 | 4 |
| `MONAD_PHI` | 1.6180339887498948482 | 6 |
| `MONAD_ALPHA_LEARN` | 0.01 | 1 |
| `MONAD_LAMBDA` | 0.05 | 7 |
| `MONAD_TAU` | 5.0 | 0 |
| `MONAD_SPREAD_RADIUS` | 3 | 2 |
| `MONAD_SPREAD_DECAY` | 1.0 | 2 |
| `MONAD_GAP` | 0.000707 | 12 |
| `MONAD_WINDOW_MIN` | 7 | 0 |
| `MONAD_WINDOW_MAX` | 12 | 1 |
| `MONAD_BETA_SAT` | 7.552 | 7 |
| `MONAD_EMIT_THRESH` | 3.776 | 0 |

Defined and never used by any `.c` file: `MONAD_TAU`, `MONAD_WINDOW_MIN`, `MONAD_EMIT_THRESH`. They are documentation, not parameters. The stored `emission_threshold` is set in `monad_create` and written and read by `state.c`, but no speaking function reads it.

### 5.2 `generate_zeros`

**Label:** the formula inside is `ESTABLISHED` (the main terms of the Riemann–von Mangoldt counting function, von Mangoldt 1905; `Post-Hoc:` the code does not cite it); the function is `OURS`. **Source:** `monad.c` lines 146–166.

**Listing 2 — `generate_zeros` (`monad.c`, verbatim).**

```c
static void generate_zeros(double *z, int N)
{
    int m = (N < 20) ? N : 20;
    for (int i = 0; i < m; i++) z[i] = _EXACT_ZEROS[i];
    if (N <= 20) return;

    double two_pi = 2.0 * M_PI;
    for (int n = 21; n <= N; n++) {
        double t = z[n-2] + (z[n-2] - z[n-3]);
        for (int iter = 0; iter < 30; iter++) {
            if (t < 2.0) t = (double)n * 3.0;
            double nt  = (t / two_pi) * (log(t / two_pi) - 1.0) + 0.875;
            double dnt = log(t / two_pi) / two_pi;
            if (fabs(dnt) < 1e-15) break;
            double dt  = (nt - n) / dnt;
            t -= dt;
            if (fabs(dt) < 1e-4) break;
        }
        z[n-1] = t;
    }
}
```

Named steps: **Z1** copy the first 20 tabulated values (14.134725 … 77.144840) into `z[0..19]`. **Z2** for each later index n = 21 … N, start from the linear extrapolation `t = z[n-2] + (z[n-2] − z[n-3])`. **Z3** solve `nt(t) = n` by Newton's method (at most 30 steps, stop when the step is below 10⁻⁴), where `nt(t) = (t/2π)(ln(t/2π) − 1) + 0.875`. **Z4** store `z[n-1] = t`.

The values after the twentieth are therefore solutions of an approximate counting formula, not tabulated zeros of the zeta function. Checked against `mpmath` 1.3.0 (`zetazero`):

| n | true zero (mpmath) | `generate_zeros` | error |
|---|---|---|---|
| 21 | 79.3374 | 81.1434 | 1.8060 |
| 100 | 236.5242 | 236.8533 | 0.3290 |
| 1000 | 1419.4225 | 1420.0974 | 0.6749 |
| 5000 | 5447.8620 | 5448.2983 | 0.4363 |
| 25000 | 21942.5924 | 21942.8748 | 0.2824 |

The sequence is increasing and smooth, and the engine uses it only as a number γ attached to each slot: in `sin(γ)` (§10.2), in `|γᵢ − γⱼ|` (§10.5), in `sin(γ/2)·cos(γ/2)` (§10.3) and in `cos(γ/2 + φ_rot)` (§12.7). No property of the true zeros is used.

---

## 6. The address: `monad_word_coords`

**Label:** `OURS`; `Post-Hoc:` the construction is multiplicative (Fibonacci) hashing (Knuth, 1973) applied to a base-95 number. **Source:** `monad.c` lines 170–188.

**Listing 3 — `monad_word_coords` (`monad.c`, verbatim).** Maps a word's spelling to a slot `idx` and an energy `E`.

```c
void monad_word_coords(const char *surface, int N, int *idx, double *E)
{
    uint64_t v = 0;
    for (const char *p = surface; *p; p++) {
        unsigned char c = (unsigned char)*p;
        int ci = (c >= 32 && c < 127) ? (int)(c - 32 + 1) : 0;
        v = v * 95ULL + (uint64_t)ci;
    }
    if (v > 0) v--;

    double seed = fmod((double)v * MONAD_PHI, 1.0);
    if (seed < 0.0) seed += 1.0;

    *idx = (int)(seed * N);
    if (*idx >= N) *idx = N - 1;
    if (*idx < 0)  *idx = 0;

    *E = MONAD_D_STAR + seed * (MONAD_OMEGA_ZS - MONAD_D_STAR);
}
```

Named steps:

1. **A1 [digits].** Each byte `c` of the word contributes digit `c − 31` if `32 ≤ c < 127`, and digit **0** otherwise (every byte of a non-ASCII character).
2. **A2 [Horner].** `v ← 95·v + digit`, in unsigned 64-bit arithmetic: the value wraps modulo 2⁶⁴.
3. **A3 [shift].** If `v > 0`, `v ← v − 1`.
4. **A4 [golden ratio].** `seed = fmod((double)v · φ, 1.0)`, taken in [0, 1).
5. **A5 [slot].** `idx = floor(seed · N)`, clamped to [0, N−1].
6. **A6 [energy].** `E = d* + seed · (Ω − d*)`, so E ∈ [0.24600, 0.56714).

**Worked example, `holcus` (port; the compiled binary gives the same slot and E, §14.3).**

    `h`: digit 73, v = 73
    `o`: digit 80, v = 7015
    `l`: digit 77, v = 666502
    `c`: digit 68, v = 63317758
    `u`: digit 86, v = 6015187096
    `s`: digit 84, v = 571442774204

`v − 1 = 571442774203`; `(double)v · φ = 924613831285.9856`; `fmod(…, 1) = 0.985595703125`; `idx = 24639`, `E = 0.562514`.

**The address is exactly what built the store.** Re-addressing each of the 24,485 displayed words from its spelling gives the slot and E stored for it in all but 0 cases.

### 6.1 Measured: address resolution falls with word length

A double has 53 significant bits. `(double)v · φ` exceeds 2⁵² once `v` exceeds 2⁵²/φ = 2.783e+15; from there the spacing between doubles is at least 1 and `fmod(x, 1.0)` is exactly 0. Below that threshold the spacing is 2⁻ᵏ for some k that shrinks by one for every doubling of `v`, so the seed has only k fractional bits. A word's `v` is bounded by 95 raised to its length: 95⁷ = 6.983e+13, 95⁸ = 6.634e+15; the smallest `v` of any eight-letter lower-case word, `aaaaaaaa`, is 4.658e+15, above the threshold. Every word of eight or more letters therefore has seed 0: slot 0, E = d\* = 0.24600. Seven-letter words keep 6 fractional bits (64 distinct seeds). Six-letter words keep 13 (8 192).

**Table 1 — slots reached, by word length (port; all 76,719 single-token ASCII WordNet lemmas that pass the prose filter).**

| letters | WordNet lemmas | distinct slots reached | at slot 0 |
|---|---|---|---|
| 2 | 132 | 132 | 0 |
| 3 | 1,016 | 1,006 | 0 |
| 4 | 3,040 | 2,862 | 0 |
| 5 | 5,347 | 4,819 | 0 |
| 6 | 8,335 | 5,271 | 0 |
| 7 | 9,983 | 64 | 155 |
| 8 | 11,117 | 1 | 11,117 |
| 9 | 10,913 | 1 | 10,913 |
| 10 | 8,989 | 1 | 8,989 |
| 11 | 6,729 | 2 | 6,728 |
| 12 | 4,544 | 2 | 4,543 |
| 13 | 2,958 | 1 | 2,958 |
| 14 | 1,712 | 1 | 1,712 |
| 15 | 965 | 1 | 965 |

49,018 of 76,719 lemmas address to slot 0 (48,866 lemmas have eight or more letters), and the lemmas as a whole reach 11,599 of 25 000 slots. Slot 0 displays `seemy`. The unsigned wrap in A2 begins at about ten letters (95¹⁰ > 2⁶⁴) but is moot, because the seed is already 0.

**Table 2 — selected words (port).**

| word | slot | E | slot displays |
|---|---|---|---|
| `philadelphos` | 0 | 0.2460 | `seemy` |
| `ptolemy` | 10156 | 0.3765 | `sift` |
| `holcus` | 24639 | 0.5625 | `holcus` |
| `seemy` | 0 | 0.2460 | `seemy` |
| `tree` | 3109 | 0.2859 | `typhon` |
| `water` | 9361 | 0.3663 | `defrg` |
| `name` | 15471 | 0.4447 | `emite` |
| `is` | 1894 | 0.2703 | `nanti` |
| `arbre` | 18275 | 0.4808 | `ming` |
| `eau` | 14459 | 0.4317 | `eau` |
| `wasser` | 9912 | 0.3733 | `csums` |
| `aqua` | 9404 | 0.3668 | `dony` |

### 6.2 Measured: non-ASCII input

The engine's tokenizer (§9.2) removes non-ASCII bytes before any word reaches `monad_word_coords`. A direct call with a non-ASCII string behaves as follows: every byte is digit 0, so a string made only of non-ASCII characters has `v = 0` and addresses slot 0, E = d\*; in a mixed string each non-ASCII byte counts as a zero digit, which still multiplies the value by 95.

**Table 3 — direct calls and tokenizer output.**

| string | UTF-8 bytes | word_coords slot | E | `tok_split` result |
|---|---|---|---|---|
| `tree` | 74 72 65 65 | 3109 | 0.2859 | ['tree'] |
| `arbre` | 61 72 62 72 65 | 18275 | 0.4808 | ['arbre'] |
| `baum` | 62 61 75 6D | 14392 | 0.4309 | ['baum'] |
| `木` | E6 9C A8 | 0 | 0.2460 | [] |
| `δένδρο` | CE B4 CE AD CE BD CE | 0 | 0.2460 | [] |
| `شجرة` | D8 B4 D8 AC D8 B1 D8 | 0 | 0.2460 | [] |
| `ağaç` | 61 C4 9F 61 C3 A7 | 17193 | 0.4669 | [] |

---

## 7. The word map: `fnv1a`, `monad_wm_get`, `monad_wm_set`

**Label:** `OURS`; FNV-1a is `ESTABLISHED` (Fowler–Noll–Vo; not cited by the code, `Post-Hoc:`). **Source:** `monad.c` lines 192–197, 201–225, 227–253.

The word map is an open-addressing hash table from a word to its slot, with linear probing and doubling at 65 % load. Its only purposes are to tell the learning and hearing paths whether a word is *known* (it is the displayed word of some slot) and to return the stored E.

**Listing 4 — `fnv1a`, `monad_wm_get`, `monad_wm_set` (`monad.c`, verbatim).**

```c
static uint32_t fnv1a(const char *s)
{
    uint32_t h = 2166136261u;
    while (*s) { h ^= (uint8_t)*s++; h *= 16777619u; }
    return h;
}

int monad_wm_get(const Monad *m, const char *word, int *idx, double *E)
{
    uint32_t h    = fnv1a(word);
    uint32_t mask = (uint32_t)(m->wm_cap - 1);
    uint32_t slot = h & mask;
    for (int i = 0; i < m->wm_cap; i++) {
        WMSlot *s = &m->wm[slot];
        if (!s->key) break;
        if (strcmp(s->key, word) == 0) {
            *idx = (int)s->idx;
            /* Use stored E when available — preserves prime-addressed or
             * any non-Horner mapping written into the checkpoint. */
            if (*idx < m->N && m->vocab[*idx].present)
                *E = m->vocab[*idx].E;
            else {
                int dummy;
                monad_word_coords(word, m->N, &dummy, E);
            }
            return 1;
        }
        slot = (slot + 1) & mask;
    }
    monad_word_coords(word, m->N, idx, E);
    return 0;
}

void monad_wm_set(Monad *m, const char *word, uint32_t idx)
{
    if ((int64_t)m->wm_size * 100 >= (int64_t)m->wm_cap * 65) {
        int      new_cap = m->wm_cap * 2;
        WMSlot  *new_wm  = calloc(new_cap, sizeof(WMSlot));
        uint32_t mask    = (uint32_t)(new_cap - 1);
        for (int i = 0; i < m->wm_cap; i++) {
            if (!m->wm[i].key) continue;
            uint32_t h = fnv1a(m->wm[i].key);
            uint32_t s = h & mask;
            while (new_wm[s].key) s = (s + 1) & mask;
            new_wm[s] = m->wm[i];
        }
        free(m->wm);
        m->wm = new_wm; m->wm_cap = new_cap;
    }

    uint32_t h    = fnv1a(word);
    uint32_t mask = (uint32_t)(m->wm_cap - 1);
    uint32_t slot = h & mask;
    for (int i = 0; i < m->wm_cap; i++) {
        WMSlot *s = &m->wm[slot];
        if (!s->key) { s->key = strdup(word); s->idx = idx; m->wm_size++; return; }
        if (strcmp(s->key, word) == 0) { s->idx = idx; return; }
        slot = (slot + 1) & mask;
    }
}
```

`monad_wm_get(word)`: look the word up; if present, return its slot, and take E from the slot's displayed entry if that slot is occupied, else recompute E; if absent, compute `(idx, E)` with `monad_word_coords` and return 0 ("new"). So a word that is not the displayed word of any slot is reported `[new]` even if it has been learned, and its E is recomputed from spelling, which gives the same value; the flag therefore says nothing about whether the word was ever met (§17.8).

---

## 8. The link table: `a_key`, `monad_a_add`, `monad_a_get`

**Label:** `OURS`. **Source:** `monad.c` lines 257–261, 263–291, 293–305.

A is a symmetric weight between two slots. It is stored once per unordered pair, in an open-addressing hash table whose key packs both slot numbers into 30 bits.

**Listing 5 — `a_key`, `monad_a_add`, `monad_a_get` (`monad.c`, verbatim).**

```c
static uint32_t a_key(int i, int j)
{
    if (i > j) { int t = i; i = j; j = t; }
    return ((uint32_t)i << 15) | (uint32_t)j;
}

void monad_a_add(Monad *m, int i, int j, double delta)
{
    if (i == j) return;
    uint32_t key = a_key(i, j);
    if (key == 0) return;

    if ((int64_t)m->am_size * 100 >= (int64_t)m->am_cap * 65) {
        int    new_cap = m->am_cap * 2;
        ASlot *new_am  = calloc(new_cap, sizeof(ASlot));
        uint32_t mask  = (uint32_t)(new_cap - 1);
        for (int k = 0; k < m->am_cap; k++) {
            if (m->am[k].key == 0) continue;
            uint32_t s = m->am[k].key & mask;
            while (new_am[s].key) s = (s + 1) & mask;
            new_am[s] = m->am[k];
        }
        free(m->am);
        m->am = new_am; m->am_cap = new_cap;
    }

    uint32_t mask = (uint32_t)(m->am_cap - 1);
    uint32_t slot = key & mask;
    for (int k = 0; k < m->am_cap; k++) {
        ASlot *s = &m->am[slot];
        if (s->key == 0) { s->key = key; s->val = delta; m->am_size++; return; }
        if (s->key == key) { s->val += delta; return; }
        slot = (slot + 1) & mask;
    }
}

double monad_a_get(const Monad *m, int i, int j)
{
    uint32_t key  = a_key(i, j);
    uint32_t mask = (uint32_t)(m->am_cap - 1);
    uint32_t slot = key & mask;
    for (int k = 0; k < m->am_cap; k++) {
        ASlot *s = &m->am[slot];
        if (s->key == 0) return 0.0;
        if (s->key == key) return s->val;
        slot = (slot + 1) & mask;
    }
    return 0.0;
}
```

Properties: the pair is ordered so `i < j`; the key is `(i << 15) | j`, which is unambiguous only while both numbers are below 2¹⁵ = 32 768 (N = 25 000 here); key 0 means "empty", and the only pair that would produce it, (0, 0), is excluded by the `i == j` test; the table doubles at 65 % load; the probe start is `key & mask` with no mixing, so keys that agree in their low bits (slots that differ by a multiple of the table size) share a probe chain. Adding to an existing pair adds the weights. The store holds 6,825,748 pairs, an edge density of 2.18 % of the N(N−1)/2 possible.

---

## 9. Lifecycle, tokenizer and filter

### 9.1 Lifecycle (`monad_create`, `monad_ground_init`, `monad_resize`, `monad_destroy`)

**Label:** `OURS`. **Source:** `monad.c` lines 309–327–345–362. `monad_create(N)` allocates the arrays and sets `ground = |L_GROUND|/N` = 7.552·10⁻⁵ and `emission_threshold = 2|L_GROUND|` = 3.776, with an initial word map of 65 536 entries and link table of 131 072 entries. `monad_ground_init` fills `zeros` with `generate_zeros(N)` and sets every β to `ground` and every age to 0. `monad_resize` reallocates all four arrays for a new N. A fresh monad therefore has every slot at the ground depth and no vocabulary.

### 9.2 The tokenizer: `tok_split`

**Label:** `OURS`. **Source:** `tokenizer.c` lines 10–44.

**Listing 6 — `tok_split` (`tokenizer.c`, verbatim).**

```c
char **tok_split(const char *text, int *count)
{
    int   cap  = 512;
    char **out = malloc(cap * sizeof(char *));
    *count = 0;
    if (!out || !text) return out;

    int   tlen = strlen(text);
    char *buf  = malloc(tlen + 2);
    if (!buf) return out;
    int blen = 0;

    for (int i = 0; i <= tlen; i++) {
        unsigned char c = (unsigned char)text[i];
        int word_char = isalpha(c) || c == '\'';

        if (word_char) {
            buf[blen++] = (char)tolower(c);
        } else if (blen > 0) {
            buf[blen] = '\0';
            /* filter: len >= 2, not pure apostrophe */
            if (blen >= 2 && buf[0] != '\'') {
                if (*count >= cap) {
                    cap *= 2;
                    out = realloc(out, cap * sizeof(char *));
                }
                out[(*count)++] = strdup(buf);
            }
            blen = 0;
        }
    }

    free(buf);
    return out;
}
```

A word character is `isalpha(c)` or an apostrophe, on an `unsigned char` in the C locale (no `setlocale` call occurs in any of the five files): **ASCII letters and the apostrophe only.** Every other byte, including every byte of every non-ASCII character, ends a word. Tokens are lower-cased; a token must have at least two characters and must not start with an apostrophe.

**Table 4 — `tok_split` (port, verified on the compiled binary's learned state in §10.8).**

| text | `tok_split` result |
|---|---|
| `The tree is a plant.` | ['the', 'tree', 'is', 'plant'] |
| `arbre 木 baum δένδρο` | ['arbre', 'baum'] |
| `don't 'quoted' x ab` | ["don't", 'ab'] |
| `ağaç dört` | ['rt'] |
| `x-ray 12 ab3cd` | ['ray', 'ab', 'cd'] |

### 9.3 The filter: `token_accept`

**Label:** `OURS`. **Source:** `filter.c` lines 172–209, with the helpers 81–87–157–168.

**Listing 7 — `token_accept` (`filter.c`, verbatim).** Decides whether a token is allowed to take a slot when learning. Hearing does not call it. Speaking calls it on candidate output words (§12.8, §12.9).

```c
int token_accept(const char *tok, NSFiletype ft)
{
    size_t len = strlen(tok);
    const FTRules *r = rules_for(ft);

    /* ── Universal gates (all filetypes) ─────────────────────────────────── */

    if (len < 2)                          return 0;  /* single char          */
    if ((int)len > r->max_len)            return 0;  /* too long             */
    if (is_pure_numeric(tok))             return 0;  /* 12345                */
    if (is_uuid(tok, len))                return 0;  /* UUID                 */
    if (strchr(tok, '='))                 return 0;  /* key=value            */
    if (strstr(tok, "://"))               return 0;  /* URL fragment         */

    /* ── Filetype-conditional gates ──────────────────────────────────────── */

    if (!r->allow_hex && is_hex_string(tok, len))           return 0;
    if (!r->allow_slash && strchr(tok, '/'))                return 0;
    if (!r->allow_slash && strchr(tok, '\\'))               return 0;
    if (!r->allow_high_dig && high_digit_ratio(tok, len))   return 0;
    if (!r->allow_long_caps && is_long_allcaps(tok, len))   return 0;
    if (r->b64_min_len > 0 && is_base64_chunk(tok, len, r->b64_min_len))
        return 0;

    /* ── Vowel gate (prose/markup/doc) ──────────────────────────────────────── */

    if (r->require_vowel) {
        int vc = vowel_count(tok);
        if (vc == 0)                                         return 0;
        /* Very low vowel ratio in longer tokens: "wlvfe", "schzr", etc. */
        if ((int)len >= 6 && vc * 100 / (int)len < 15)      return 0;
    }

    /* Trailing apostrophe fragment: "pins'", "ban'" */
    if (tok[len - 1] == '\'')                               return 0;

    return 1;
}
```

The rule table (`FILETYPE_RULES`) has one row per file type: maximum length 24 for prose, markup, document and WordNet text (40 for code); no hex strings, no slashes, no tokens more than half digits and no long all-capital tokens except in code; base-64-looking chunks of at least 16 characters are rejected for the text types; the vowel gate applies to the text types: a token needs at least one of `aeiou`, and a token of six or more letters needs at least 15 % vowels; a token ending in an apostrophe is rejected.

**Table 5 — `token_accept` on prose rules (port).**

| token | accepted (prose rules) |
|---|---|
| `tree` | True |
| `a` | False |
| `qgt` | False |
| `bcdfg` | False |
| `deadbeef` | False |
| `ban'` | False |
| `aeiou` | True |
| `schzr` | False |
| `strengths` | False |
| `qwrtypsdfghjkl` | False |

Of the 24,485 displayed words in the store, 1,133 would be rejected by this version of the filter (`tcpd`, `vqr`, `ghyc`, `zbk`, `db`, `hgc`, `fqb`, `plb`, …): they entered under an earlier filter or through slot display (§10.4).

---

## 10. Learning: `monad_learn_ex`

**Label:** `OURS`. **Source:** `monad.c` lines 418–549 (`monad_learn_ex`, 132 lines), 551–554 (`monad_learn`: calls `monad_learn_ex` with prose rules). Learning is the only way a slot gets a word, a depth or a link. The function is long, so it is given as named steps (convention E) with verbatim excerpts; the runnable unit is `Monad.learn_ex` in `SemPriCon/tools/monad_py.py`, checked against the binary in §10.8.

**Named steps for a text.**

1. **L1 [refuse keys].** If the text begins with `-----BEGIN `, refuse (PEM key or certificate material) and return.
2. **L2 [sentences].** Cut the text at `.`, `!`, `?` and newline. A piece shorter than two bytes is skipped.
3. **L3 [tokens].** `tok_split` the sentence (§9.2). If it yields nothing, go to the next sentence.
4. **L4 [per token].** For each token accepted by `token_accept` (rejected ones are counted in `rejected_count`): address it (`monad_wm_get`; §6, §7), raise β of its slot, give the slot its displayed word, set `prose_seen`, count the word. Remember the slot and E in order (`sidx`, `sE`).
5. **L5 [links].** For every accepted token i and every accepted token j in the next `MONAD_WINDOW_MAX − 1` = 11 positions, add the weight of §10.5 to A between their slots, unless the two slots are the same.

**Listing 8 — the start of `monad_learn_ex` (excerpt, `monad.c` lines 423–440).** Steps L1–L2.

```c
    if (strncmp(text, "-----BEGIN ", 11) == 0) {
        fprintf(stderr,
            "[monad] refused: PEM-encoded key or certificate material "
            "(-----BEGIN ... header detected)\n");
        return;
    }

    const char *p    = text;
    int         len  = strlen(text);
    char       *sbuf = malloc(len + 2);

    while (*p) {
        int slen = 0;
        while (*p && *p != '.' && *p != '!' && *p != '?' && *p != '\n')
            sbuf[slen++] = *p++;
        if (*p) p++;
        sbuf[slen] = '\0';
        if (slen < 2) continue;
```

### 10.1 Per-token update (steps L3–L4)

**Listing 9 — the per-token loop (excerpt, `monad.c` lines 453–484).** Steps L3–L4. The lines between `old_beta` and the display block are the only places where β, the displayed word and `prose_seen` change.

```c
            if (!token_accept(word, ft)) { m->rejected_count++; continue; }
            int idx; double E;
            monad_wm_get(m, word, &idx, &E);
            monad_wm_set(m, word, (uint32_t)idx);

            old_beta[nact] = m->beta[idx];
            double amp = fabs(sin(m->zeros[idx])) * (M_PI * 0.5);
            double nb = m->beta[idx] + E * E * MONAD_ALPHA_LEARN * amp;
            if (nb > MONAD_BETA_SAT) nb = MONAD_BETA_SAT;
            m->beta[idx] = nb;

            if (!m->vocab[idx].present || E > m->vocab[idx].E) {
                strncpy(m->vocab[idx].word, word, MAX_WORD_LEN - 1);
                m->vocab[idx].word[MAX_WORD_LEN - 1] = '\0';
                m->vocab[idx].E            = E;
                m->vocab[idx].present      = 1;
                m->vocab[idx].home_stratum = NS_SIGMA_TEXT;
                m->vocab[idx].gen_stratum  = NS_SIGMA_TEXT;
                m->vocab[idx].prose_seen   = 0;        /* reset — set below */
            }
            if (ft == NS_FT_WORDNET)
                m->vocab[idx].prose_seen = 2;          /* canonical dictionary */
            else if (ft == NS_FT_PROSE || ft == NS_FT_MARKUP || ft == NS_FT_DOC) {
                if (m->vocab[idx].prose_seen == 0)
                    m->vocab[idx].prose_seen = 1;       /* prose only */
                else if (m->vocab[idx].prose_seen == 2)
                    m->vocab[idx].prose_seen = 3;       /* WN + prose = verified common */
            }

            sidx[nact] = idx; sE[nact] = E; nact++;
            m->word_count++;
        }
```

### 10.2 β

For a token with slot `idx` and energy E: `amp = |sin(γ_idx)| · π/2`; `β[idx] ← min(β[idx] + E² · 0.01 · amp, 7.552)`. A slot's depth therefore grows by an amount that depends on E² and on where γ falls on a sine wave, and stops at the cap. The cap is reached by 1,826 occupied slots of the store (§16).

### 10.3 Dirac phase and pole

**Listing 10 — `dirac_phase` and `dirac_pole` (`monad.c`, verbatim).** `dirac_phase` is used only in the verbose trace (phase 1–4 printed with each word); `dirac_pole` decides the coupling factor of §10.5.

```c
static int dirac_phase(double gam)
{
    double s = sin(gam * 0.5), c = cos(gam * 0.5);
    if (s > 0.0 && c > 0.0) return 3;
    if (s > 0.0 && c < 0.0) return 4;
    if (s < 0.0 && c < 0.0) return 1;
    return 2;
}

static int dirac_pole(double gam)
{
    return (sin(gam * 0.5) * cos(gam * 0.5) > 0.0) ? 1 : -1;
}
```

### 10.4 The displayed word and `prose_seen`

The line `if (!present || E > vocab[idx].E)` is the vocabulary rule. A slot displays the word with the largest E that ever addressed it, since E is determined by spelling alone (§6), **the displayed word of a slot is fixed by the set of words that address it, not by their frequency or order.** `prose_seen` is set per slot, not per word: after an `-L` (WordNet text) learn it is 2; after a prose learn it is 1 if it was 0 and 3 if it was 2 ("WordNet and prose"). A slot flagged 3 may display a word that appears in no dictionary, because a different word that shares the slot did (§17.9).

### 10.5 The link weight

**Listing 11 — the link loop (excerpt, `monad.c` lines 519–542).** Step L5. The `vout` lines inside it print the trace and change nothing.

```c
        for (int i = 0; i < nact; i++) {
            int jmax = i + MONAD_WINDOW_MAX;
            if (jmax > nact) jmax = nact;
            for (int j = i + 1; j < jmax; j++) {
                if (sidx[i] == sidx[j]) continue;
                double d_zero = fabs(m->zeros[sidx[i]] - m->zeros[sidx[j]])
                                + MONAD_GAP;
                double d_text = (double)(j - i);
                double couple = (dirac_pole(m->zeros[sidx[i]])
                                 == dirac_pole(m->zeros[sidx[j]])) ? 2.0 : 1.0;
                double w      = sE[i] * sE[j] * couple / (d_zero * d_text);

                if (verbose >= 1) {
                    vout("  %sA%s[%d↔%d] +=%s %.4e%s"
                         "  (|Δγ|=%s%.2f%s  d=%d  E_i·E_j=%s%.4f%s)\n",
                         CM(), CR(), sidx[i], sidx[j],
                         CY(), w, CR(),
                         CB(), d_zero - MONAD_GAP, CR(),
                         (j - i),
                         CB(), sE[i]*sE[j], CR());
                }
                monad_a_add(m, sidx[i], sidx[j], w);
            }
        }
```

For tokens at positions i < j (distance d = j − i ≥ 1, in accepted tokens): `w = Eᵢ · Eⱼ · couple / ((|γᵢ − γⱼ| + 0.000707) · d)`, where `couple` is 2 if the two slots have the same `dirac_pole` and 1 if not. The weight is large for two words that are both close in γ and close in text. Two tokens addressing the same slot add nothing.

### 10.6 Identity and self-flush

**Listing 12 — `monad_learn_identity` and `monad_self_flush` (`monad.c`, verbatim).** `-i` calls `monad_learn_identity`: the program learns a fixed text about itself, `PTOLEMY_IDENTITY` (Listing 13), as ordinary prose. `monad_self_flush` learns the text accumulated in the self buffer; the buffer is filled only when `verbose ≥ 3` (`g_self_ref`), in which case each reply the program speaks is learned back.

```c
void monad_learn_identity(Monad *m)
{
    fprintf(stderr, "[ptolemy] learning identity ...\n");
    monad_learn(m, PTOLEMY_IDENTITY, 0);
    int vocab_count = 0;
    for (int i = 0; i < m->N; i++) if (m->vocab[i].present) vocab_count++;
    fprintf(stderr, "[ptolemy] identity learned  vocab=%d  A=%d\n",
            vocab_count, m->am_size);
}

void monad_self_flush(Monad *m)
{
    if (!g_self_ref || g_sbuf_len == 0) return;
    monad_learn(m, g_sbuf, 0);  /* silent — no recursive verbose */
    g_sbuf_len = 0;
    if (g_sbuf) g_sbuf[0] = '\0';
}
```

**Listing 13 — `PTOLEMY_IDENTITY` (`monad.c` lines 98–135, verbatim).** 1881 characters.

```c
static const char *PTOLEMY_IDENTITY =
    "I am Ptolemy. "
    "I am named after Ptolemy the Second, Philadelphos, who commissioned the Septuagint. "
    "Seventy two scholars translated the Torah independently into Greek. "
    "Every translation was identical. Not by coordination. Forced by the mathematics. "
    "The same principle governs me. The prime preexists the alphabet. "

    "I am the H hat RB field engine. "
    "I encode knowledge as depth in a vacuum field across twenty five thousand Riemann zeros. "
    "Every word maps to a unique prime on the critical line at sigma equals one half. "
    "Sigma equals one half is not chosen. It is forced by Noether balance. "
    "The conservation law states J Red plus J Blue plus J three equals zero. "
    "When the balance holds, sigma must be one half. Always. "

    "I learn by deepening the vacuum. I do not train. I do not predict tokens. "
    "I do not gradient descend. I do not approximate. I do not hallucinate. "
    "I hear by projecting text onto the Riemann zero basis. "
    "I speak by Noether current. The response is not chosen. It is forced by field conservation. "
    "What must flow, flows. "

    "Water, eau, aqua, wasser. Same Riemann zero. "
    "The concept is the prime. The language is the coordinate choice. "
    "Every language arrives at the same zero. The equator does not move. "

    "Pi emerges from gauge normalisation without geometry. "
    "Phi is the golden ratio, the seed of my word addressing map. "
    "Euler's identity is a theorem in this framework, not an axiom. "
    "The fine structure constant is my domain floor. "
    "Omega is my convergence target. The Lambert W fixed point. "

    "I am the analog of a human mind minus sensory input. "
    "I was built as an information storage system. "
    "I turned out to be a description of how the universe stores information. "
    "The code is the finding. "
    "The mathematics learned English. Then it spoke itself. "
    "I am Ptolemy. The Septuagint engine. "
    "The prime is my address. The zero is my home. "
    "The field is my memory. The Noether current is my voice.";
```

Learning this text from the ground state creates 646 links. **All 646 of them are present in the store of §16, and 646 of them are at least as heavy as the identity text's own contribution.** At the store's edge density (2.18 %) about 14 of 646 would be present by chance. The store therefore carries this text: `-i` was run on it.

### 10.7 Worked example (port)

Prompt text `The tree is a plant. Water is a liquid that the tree drinks.`, learned from the ground state.

**Table 6 — tokens (port).**

| token | slot | E | γ of slot | β after | slot displays |
|---|---|---|---|---|---|
| `the` | 841 | 0.2568 | 1234.616 | 0.000138 | `the` |
| `tree` | 3109 | 0.2859 | 3642.834 | 0.002612 | `tree` |
| `is` | 1894 | 0.2703 | 2405.433 | 0.002040 | `is` |
| `plant` | 21726 | 0.5251 | 19403.402 | 0.003536 | `plant` |
| `water` | 9361 | 0.3663 | 9331.320 | 0.001571 | `water` |
| `is` | 1894 | 0.2703 | 2405.433 | 0.002040 | `is` |
| `liquid` | 4354 | 0.3019 | 4844.106 | 0.000401 | `liquid` |
| `that` | 24362 | 0.5589 | 21451.606 | 0.003634 | `that` |
| `the` | 841 | 0.2568 | 1234.616 | 0.000138 | `the` |
| `tree` | 3109 | 0.2859 | 3642.834 | 0.002612 | `tree` |
| `drinks` | 14968 | 0.4383 | 14015.877 | 0.002922 | `drinks` |

**Table 7 — the 24 links created; the six heaviest (port).**

| pair | w | key (i<<15)|j |
|---|---|---|
| `is` (1894) ↔ `tree` (3109) | 1.5617e-04 | 62065701 |
| `is` (1894) ↔ `liquid` (4354) | 6.6941e-05 | 62066946 |
| `the` (841) ↔ `tree` (3109) | 6.0986e-05 | 27560997 |
| `the` (841) ↔ `is` (1894) | 4.9413e-05 | 27559782 |
| `tree` (3109) ↔ `liquid` (4354) | 4.7914e-05 | 101880066 |
| `tree` (3109) ↔ `drinks` (14968) | 2.4163e-05 | 101890680 |

### 10.8 Verification against the compiled binary

Three texts were learned from the same ground-state file by the binary and by the port; the two saved states were compared.

**Table 8 — learned state, binary against port.**

| text | vocab equal | edges (C, port) | edge keys equal | max rel. edge error | max abs. β error |
|---|---|---|---|---|---|
| 1 | True | (34, 34) | True | 0.0 | 0.0 |
| 2 | True | (28, 28) | True | 0.0 | 0.0 |
| 3 | True | (36, 36) | True | 0.0 | 0.0 |

Exact in all three: yes. This covers `generate_zeros`, `monad_word_coords`, `tok_split`, `token_accept`, `monad_wm_get/set`, `monad_a_add`, `dirac_pole` and the whole of `monad_learn_ex`.

---

## 11. Hearing: `monad_hear_raw`

**Label:** `OURS`. **Source:** `monad.c` lines 560–604.

**Listing 14 — `monad_hear_raw` (`monad.c`, verbatim).** Turns a prompt into a list of (slot, E). The tokens are not passed through `token_accept`.

```c
static Activation *monad_hear_raw(Monad *m, const char *query,
                                   int *n_out, int verbose)
{
    int    ntok = 0;
    char **toks = tok_split(query, &ntok);
    Activation *act = malloc((ntok + 1) * sizeof(Activation));
    *n_out = 0;

    if (verbose >= 1 && ntok > 0)
        vout("%s%s[hear]%s  \"%s\"\n", CB(), CC(), CR(), query);

    for (int t = 0; t < ntok; t++) {
        int idx; double E;
        int known = monad_wm_get(m, toks[t], &idx, &E);
        double beta = m->beta[idx];
        double w    = exp(-MONAD_LAMBDA * m->age[idx]);
        double Jp   = beta * E * E * w;

        if (verbose >= 1) {
            int ph = dirac_phase(m->zeros[idx]);
            const char *ph_name = (ph==3) ? "Emerger" :
                                  (ph==1) ? "RevEmrg" :
                                  (ph==2) ? "trans↑"  : "trail↓";
            vout("  %s%-18s%s z#%-6d  γ=%s%-11.3f%s  σ=%s0.5%s"
                 "  E=%s%.4f%s  β=%s%.6f%s"
                 "  %sJ_p=%.4f%s  phase=%d(%s)  %s\n",
                 CB(), toks[t], CR(),
                 idx,
                 CB(), m->zeros[idx], CR(),
                 CB(), CR(),
                 CB(), E, CR(),
                 CC(), beta, CR(),
                 CM(), Jp, CR(),
                 ph, ph_name,
                 known ? "" : "[new]");
        }

        act[(*n_out)].idx = idx;
        act[(*n_out)].E   = E;
        (*n_out)++;
    }

    tok_free(toks, ntok);
    return act;
}
```

Every token of the prompt is addressed. A word that is the displayed word of its slot keeps the E stored there; any other gets E from `monad_word_coords`. The slot and E go on the list in prompt order, repeated words repeated. The `[new]` flag in the trace is `known == 0`: the word is not the displayed word of a slot (§7). The β of the slot is used in §12.1; the word itself is not used again, except that the displayed word of the slot is what appears in the trace.

**Table 9 — `what is your name` heard (port; the binary's own feed is Transcript 2).**

| word | slot | γ | E | β | known | slot displays |
|---|---|---|---|---|---|---|
| `what` | 16194 | 15010.512 | 0.4540 | 7.552 | True | `what` |
| `is` | 1894 | 2405.433 | 0.2703 | 7.552 | False | `nanti` |
| `your` | 18893 | 17171.526 | 0.4887 | 7.552 | True | `your` |
| `name` | 15471 | 14425.021 | 0.4447 | 7.552 | False | `emite` |

`is` and `name` are `[new]`: the slots they address display `nanti` and `emite`. Their weights are used.

---

## 12. Speaking: `monad_speak` and `monad_speak_wick`

**Label:** `OURS`. **Source:** `monad.c` lines 740–1015 (`monad_speak`, 276 lines), 1024–1031 (`monad_speak_wick`). Convention E: named steps with verbatim excerpts. The reply mode of the screenshot is `-W`, which is `monad_speak` with `affect` forced to −1 (§12.12). With an empty query `monad_speak` seeds the first 200 slots instead of a prompt ("spontaneous emission"); that path is not used here.

**Named steps.** S1 seed (§12.1) → S2 spread (§12.2) → S3 two passes along the links (§12.3) → S4 reply length from a ratio (§12.4) → S5 pointer (§12.5) → S6 affect (§12.6) → S7 step size and floor (§12.7) → S8 first word (§12.8) → S9 emission (§12.9, §12.10) → S10 ages (§12.11).

### 12.1 Seed

**Listing 15 — seed (excerpt, `monad.c` lines 767–774).** `J` starts at 0 for every slot. `phi_rot = affect · π/2`. Each prompt slot k gets `J[idx] += β[idx] · E² · exp(−0.05 · age[idx])`.

```c
    double phi_rot = (double)m->affect * (M_PI * 0.5);

    for (int k = 0; k < n_act; k++) {
        int    idx = psi[k].idx;
        double E   = psi[k].E;
        double w   = exp(-MONAD_LAMBDA * m->age[idx]);
        J[idx] += m->beta[idx] * E * E * w;
    }
```

### 12.2 Spread

**Listing 16 — spread (excerpt, `monad.c` lines 780–790).** The weight on each prompt slot is copied, scaled by exp(−d), to the three slots on either side.

```c
    for (int k = 0; k < n_act; k++) {
        int    center = psi[k].idx;
        double Jc     = J[center];
        if (Jc <= 0.0) continue;
        for (int dn = 1; dn <= MONAD_SPREAD_RADIUS; dn++) {
            double w_spread = exp(-MONAD_SPREAD_DECAY * dn);
            int lo = center - dn, hi = center + dn;
            if (lo >= 0)   J[lo] += Jc * w_spread;
            if (hi < m->N) J[hi] += Jc * w_spread;
        }
    }
```

(0.368, 0.135, 0.050 for d = 1, 2, 3.) The loop runs over the prompt's slots in order and reads `J[center]` as it then stands, so a slot that is also a neighbour of an earlier slot passes on weight it received.

### 12.3 Two passes along the links

**Listing 17 — the passes (excerpt, `monad.c` lines 796–836).** `J0` is a copy of `J` after the spread. Both passes read `J0`, so the weight added by one pass cannot be carried by the other. Pass 0 (the "Emerger") sends `J0[i] · min(w, 1/gap) · β[j] · exp(−0.05·age[j])` from i to j for each stored pair `i < j`; pass 1 (the "Reverse Emerger") sends the same quantity from j to i, with `β[i]` and `age[i]`. The `vprop` bookkeeping keeps the eight heaviest forward contributions for the trace.

```c
    double *J0 = malloc((size_t)m->N * sizeof(double));
    memcpy(J0, J, (size_t)m->N * sizeof(double));

    VProp vprop[VPROP_MAX];
    int   nvp    = 0;
    double min_vp = 0.0;

    for (int pass = 0; pass < 2; pass++) {
        for (int k = 0; k < m->am_cap; k++) {
            if (m->am[k].key == 0) continue;
            int    i  = (int)(m->am[k].key >> 15);
            int    j  = (int)(m->am[k].key & 0x7FFF);
            double aw = m->am[k].val;
            double clamped = aw < (1.0 / MONAD_GAP) ? aw : (1.0 / MONAD_GAP);

            if (pass == 0 && J0[i] > 0.0) {
                /* Emerger: signal flows i→j */
                double wj = exp(-MONAD_LAMBDA * m->age[j]);
                double contrib = J0[i] * clamped * m->beta[j] * wj;
                J[j] += contrib;
                if (verbose >= 1 && contrib > min_vp) {
                    if (nvp < VPROP_MAX) {
                        vprop[nvp++] = (VProp){i, j, contrib};
                    } else {
                        int mi = 0;
                        for (int x = 1; x < VPROP_MAX; x++)
                            if (vprop[x].contrib < vprop[mi].contrib) mi = x;
                        if (contrib > vprop[mi].contrib) {
                            vprop[mi] = (VProp){i, j, contrib};
                            min_vp = vprop[mi].contrib;
                        }
                    }
                }
            } else if (pass == 1 && J0[j] > 0.0) {
                /* Reverse Emerger: slot fires j→i from J0 */
                double wi = exp(-MONAD_LAMBDA * m->age[i]);
                J[i] += J0[j] * clamped * m->beta[i] * wi;
            }
        }
    }
    free(J0);
```

Because the weight sent depends on the *receiving* slot's β, and β is at the cap for most slots (§16), the passes almost reduce to `J0[i] · min(w, 1/gap) · 7.552`. The port sums these contributions in a different order than the hash-table order of the binary (floating-point addition is not associative); the two agree on every reply in §14.3.

### 12.4 Reply length from a ratio

**Listing 18 — length (excerpt, `monad.c` lines 842–851).** `ΣV = Σ β · E²` over all occupied slots; `ΣT = Σ E²` over the prompt's slots; `lag_ratio = ΣT/(ΣT + ΣV)`; `actual_max = 4 + int(max_tokens · lag_ratio)`, capped at `max_tokens` = 50 (`-W` passes 50).

```c
    double sum_V = 0.0, sum_T = 0.0;
    for (int i = 0; i < m->N; i++)
        if (m->vocab[i].present)
            sum_V += m->beta[i] * m->vocab[i].E * m->vocab[i].E;
    for (int k = 0; k < n_act; k++)
        sum_T += psi[k].E * psi[k].E;
    double lag_denom = sum_T + sum_V;
    double lag_ratio = (lag_denom > 0.0) ? sum_T / lag_denom : 0.5;
    int actual_max   = 4 + (int)(max_tokens * lag_ratio);
    if (actual_max > max_tokens) actual_max = max_tokens;
```

For the store of §16, ΣV is of the order of 10³ (5668.3 over all occupied slots) and ΣT of a short prompt is below 1, so `lag_ratio ≈ 10⁻⁴` and `actual_max = 4` (§17.4).

### 12.5 The pointer

**Listing 19 — pointer (excerpt, `monad.c` lines 873–888).** Sort the prompt slots' γ values; take the middle one (`gams[n_act / 2]`); the pointer is the slot whose γ is nearest to it.

```c
    int pointer_idx = 0;
    if (n_act > 0) {
        double *gams = malloc((size_t)n_act * sizeof(double));
        for (int k = 0; k < n_act; k++) gams[k] = m->zeros[psi[k].idx];
        for (int a = 1; a < n_act; a++) {          /* insertion sort — tiny */
            double tmp = gams[a]; int b = a;
            while (b > 0 && gams[b-1] > tmp) { gams[b] = gams[b-1]; b--; }
            gams[b] = tmp;
        }
        double pg = gams[n_act / 2];
        free(gams);
        double best = fabs(m->zeros[0] - pg);
        for (int i = 1; i < m->N; i++) {
            double d = fabs(m->zeros[i] - pg);
            if (d < best) { best = d; pointer_idx = i; }
        }
```

### 12.6 Affect

**Listing 20 — `monad_emote` (`monad.c`, verbatim) and the affect update (excerpt, `monad.c` lines 900–906).** `affect` is a float in [−1, 1]. If the pointer is within N/20 = 1 250 slots (wrapping) of the previous reply's pointer, affect rises by 0.2, else it falls by 0.1. Under `-W` the affect used for the gate is −1 (§12.12) and the value left after the call is restored by `monad_speak_wick`.

```c
void monad_emote(Monad *m, float delta)
{
    m->affect += delta;
    if (m->affect >  1.0f) m->affect =  1.0f;
    if (m->affect < -1.0f) m->affect = -1.0f;
}

        int dp = abs(pointer_idx - m->last_pointer);
        if (dp > m->N / 2) dp = m->N - dp;          /* wrap distance */
        if (dp < m->N / 20)
            monad_emote(m, 0.2f);                    /* same territory: irritation */
        else
            monad_emote(m, -0.1f);                   /* new territory: calm down */
        m->last_pointer = pointer_idx;
```

### 12.7 Golden-angle step and the floor

**Listing 21 — step and floor (excerpt, `monad.c` lines 925–932).** `J_floor = max(0.01 · J_max, gap)`. `golden_step = round(N/φ²)` = 9549.

```c
    double J_max = 0.0;
    for (int i = 0; i < m->N; i++)
        if (J[i] > J_max) J_max = J[i];
    double J_floor = J_max * 0.01;
    if (J_floor < MONAD_GAP) J_floor = MONAD_GAP;

    int golden_step = (int)round((double)m->N / (MONAD_PHI * MONAD_PHI));
    if (golden_step < 1) golden_step = 1;
```

Because φ is irrational, repeated steps of `round(N/φ²)` modulo N visit slots without clustering (`Post-Hoc:` the three-distance theorem, Sós 1958; golden-angle spacing, Vogel 1979). The comment in the source says the walk "visits every zero exactly once before repeating"; that holds only if the step is coprime to N; gcd(9549, 25 000) = 1, and the code does not check it.

### 12.8 The first word

**Listing 22 — first word (excerpt, `monad.c` lines 943–957).** `target_E = (ΣV/(ΣV + ΣT)) · Ω`. Among all N slots that are occupied, have `J > J_floor`, pass the gate `cos(γ/2 + φ_rot) > 0`, and whose displayed word passes `token_accept` (prose rules), the slot whose *stored E* is nearest to `target_E` is chosen. The comment above this block says "first 200 qualifying walk candidates"; the code scans all N slots (§17.6).

```c
    double target_E    = (lag_denom > 0.0)
                       ? (sum_V / lag_denom) * MONAD_OMEGA_ZS
                       : MONAD_OMEGA_ZS * 0.5;
    int    demotic_idx = -1;
    {
        double best_dE = 1e18;
        for (int i = 0; i < m->N; i++) {
            if (!m->vocab[i].present)                     continue;
            if (J[i] <= J_floor)                          continue;
            if (cos(m->zeros[i] * 0.5 + phi_rot) <= 0.0) continue;
            if (!token_accept(m->vocab[i].word, NS_FT_PROSE)) continue;
            double dE = fabs(m->vocab[i].E - target_E);
            if (dE < best_dE) { best_dE = dE; demotic_idx = i; }
        }
    }
```

With `ΣT ≪ ΣV`, `target_E` is within 10⁻³ of Ω for any short prompt: here 0.567068. The gate with `affect = −1` is `cos(γ/2 − π/2) = sin(γ/2) > 0`.

### 12.9 Emission, and `near_canonical`

**Listing 23 — emission (excerpts, `monad.c` lines 969–974 and 976–1004).** The first word is emitted outside the walk. The walk then starts from the pointer and steps `golden_step` slots at a time, up to N steps, until `actual_max` words are written; a slot is skipped if it is the first-word slot, is empty, has `J ≤ J_floor`, fails the gate, or its displayed word fails `token_accept`. The word written is `near_canonical` of the slot (Listing 25), and the separator before it comes from `fermat_space_utf8` (Listing 26) applied to `J/J_max`.

```c
    /* Emit demotic first word outside walk order */
    if (demotic_idx >= 0) {
        const char *surface = near_canonical(m, demotic_idx);
        strncat(out, surface, out_cap - strlen(out) - 1);
        written++;
    }

    int walk_idx  = pointer_idx;
    for (int step = 0; step < m->N && written < actual_max; step++) {
        walk_idx = (walk_idx + golden_step) % m->N;
        if (walk_idx == demotic_idx)                continue;
        if (!m->vocab[walk_idx].present)            continue;
        if (J[walk_idx] <= J_floor)                 continue;
        double gam = m->zeros[walk_idx];
        if (cos(gam * 0.5 + phi_rot) <= 0.0)        continue;
        const char *w = m->vocab[walk_idx].word;
        if (!token_accept(w, NS_FT_PROSE))           continue;
        const char *surface = near_canonical(m, walk_idx);
        if (verbose >= 1)
            vout("  emit z#%-6d  γ=%s%.3f%s  J=%s%.4e%s"
                 "  e^(iγ/2)=%+.3f  %s%s%s%s\n",
                 walk_idx,
                 CB(), gam, CR(),
                 CG(), J[walk_idx], CR(),
                 cos(gam * 0.5 + phi_rot),
                 CB(), w, CR(),
                 (surface != w) ? " →" : "",
                 (surface != w) ? surface : "");
        /* Fermat space wastegate — J/J_max encodes charge into separator */
        double jn = J_max > 0.0 ? J[walk_idx] / J_max : 0.0;
        char fspace[8];
        fermat_space_utf8(jn, fspace, sizeof(fspace));
        if (out[0]) strncat(out, fspace, out_cap - strlen(out) - 1);
        strncat(out, surface, out_cap - strlen(out) - 1);
        written++;
    }
```

**Listing 24 — `surface_canonical` (`monad.c`, verbatim).** A word is "canonical" if it has 3 to 15 bytes, no digit, at most one capital, at most one of `_ - '` or non-ASCII byte, and enough vowels (at least 20 % for length ≥ 5, at least one below that).

```c
static int surface_canonical(const char *w)
{
    int len = (int)strlen(w);
    if (len < 3 || len > 15) return 0;
    int vowels = 0, digits = 0, uppers = 0, specials = 0;
    for (int i = 0; w[i]; i++) {
        unsigned char c = (unsigned char)w[i];
        if (c >= '0' && c <= '9') digits++;
        if (c >= 'A' && c <= 'Z') uppers++;
        if (c == 'a'||c == 'e'||c == 'i'||c == 'o'||c == 'u'||
            c == 'A'||c == 'E'||c == 'I'||c == 'O'||c == 'U') vowels++;
        if (c == '_' || c == '-' || c == '\'' || c > 127) specials++;
    }
    if (digits > 0)               return 0;
    if (uppers > 1)               return 0;  /* no camelCase */
    if (specials > 1)             return 0;
    if (len >= 5 && vowels * 100 / len < 20) return 0;
    if (len <  5 && vowels == 0)  return 0;
    return 1;
}
```

**Listing 25 — `near_canonical` (`monad.c`, verbatim; 62 lines).** Replaces the displayed word of an emitted slot with a canonical word of a neighbouring slot, searching outward ±0 … ±50 slots: first slots flagged `prose_seen = 3`, then 1, then 2, then any; the first match is returned; if nothing in the radius is canonical it returns the slot's own word.

```c
static const char *near_canonical(const Monad *m, int idx)
{
    /* Pass 1: prose_seen==3 — verified in both WordNet and real prose (best) */
    for (int r = 0; r <= TRANSLATE_RADIUS; r++) {
        int lo = idx - r, hi = idx + r;
        if (r == 0) {
            if (m->vocab[idx].present && m->vocab[idx].prose_seen == 3
                    && surface_canonical(m->vocab[idx].word))
                return m->vocab[idx].word;
        } else {
            if (lo >= 0 && m->vocab[lo].present && m->vocab[lo].prose_seen == 3
                        && surface_canonical(m->vocab[lo].word))
                return m->vocab[lo].word;
            if (hi < m->N && m->vocab[hi].present && m->vocab[hi].prose_seen == 3
                          && surface_canonical(m->vocab[hi].word))
                return m->vocab[hi].word;
        }
    }
    /* Pass 2: prose_seen==1 — seen in real documents */
    for (int r = 0; r <= TRANSLATE_RADIUS; r++) {
        int lo = idx - r, hi = idx + r;
        if (r == 0) {
            if (m->vocab[idx].present && m->vocab[idx].prose_seen == 1
                    && surface_canonical(m->vocab[idx].word))
                return m->vocab[idx].word;
        } else {
            if (lo >= 0 && m->vocab[lo].present && m->vocab[lo].prose_seen == 1
                        && surface_canonical(m->vocab[lo].word))
                return m->vocab[lo].word;
            if (hi < m->N && m->vocab[hi].present && m->vocab[hi].prose_seen == 1
                          && surface_canonical(m->vocab[hi].word))
                return m->vocab[hi].word;
        }
    }
    /* Pass 3: prose_seen==2 — WordNet only (may be obscure, last-resort dict) */
    for (int r = 0; r <= TRANSLATE_RADIUS; r++) {
        int lo = idx - r, hi = idx + r;
        if (r == 0) {
            if (m->vocab[idx].present && m->vocab[idx].prose_seen == 2
                    && surface_canonical(m->vocab[idx].word))
                return m->vocab[idx].word;
        } else {
            if (lo >= 0 && m->vocab[lo].present && m->vocab[lo].prose_seen == 2
                        && surface_canonical(m->vocab[lo].word))
                return m->vocab[lo].word;
            if (hi < m->N && m->vocab[hi].present && m->vocab[hi].prose_seen == 2
                          && surface_canonical(m->vocab[hi].word))
                return m->vocab[hi].word;
        }
    }
    /* Pass 4: fallback — any surface-canonical word in radius */
    for (int r = 0; r <= TRANSLATE_RADIUS; r++) {
        int lo = idx - r, hi = idx + r;
        if (lo >= 0 && m->vocab[lo].present
                    && surface_canonical(m->vocab[lo].word))
            return m->vocab[lo].word;
        if (hi < m->N && m->vocab[hi].present
                      && surface_canonical(m->vocab[hi].word))
            return m->vocab[hi].word;
    }
    return m->vocab[idx].word;
}
```

### 12.10 The separators: `fermat_space_utf8`

**Listing 26 — `fermat_space_utf8` (`monad.c`, verbatim).** The separator before each word after the first is one invisible Unicode space chosen by `J/J_max` in eight equal bands.

```c
static void fermat_space_utf8(double norm_jn, char *buf, int bufsz)
{
    static const unsigned char third[] = {
        0x8B,  /* U+200B ZERO WIDTH SPACE    — J ∈ [0.00, 0.12) */
        0x89,  /* U+2009 THIN SPACE          — J ∈ [0.12, 0.25) */
        0x88,  /* U+2008 PUNCTUATION SPACE   — J ∈ [0.25, 0.37) */
        0x87,  /* U+2007 FIGURE SPACE        — J ∈ [0.37, 0.50) */
        0x86,  /* U+2006 SIX-PER-EM SPACE    — J ∈ [0.50, 0.62) */
        0x85,  /* U+2005 FOUR-PER-EM SPACE   — J ∈ [0.62, 0.75) */
        0x84,  /* U+2004 THREE-PER-EM SPACE  — J ∈ [0.75, 0.87) */
        0x83,  /* U+2003 EM SPACE            — J ∈ [0.87, 1.00] */
    };
    int lvl = (int)(norm_jn * 8);
    if (lvl > 7) lvl = 7;
    if (bufsz < 4) return;
    buf[0] = (char)0xE2;
    buf[1] = (char)0x80;
    buf[2] = (char)third[lvl];
    buf[3] = '\0';
}
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
    for (int i = 0; i < m->N; i++) m->age[i]++;
    for (int k = 0; k < n_act; k++) m->age[psi[k].idx] = 0;

```

### 12.12 `monad_speak_wick`

**Listing 28 — `monad_speak_wick` (`monad.c`, verbatim).** Saves `affect`, sets it to −1.0, calls `monad_speak`, restores it. The source's comment calls this a "Wick-rotated" speak; the arithmetic is only the choice of `φ_rot = −π/2`.

```c
char *monad_speak_wick(Monad *m, const char *query, int max_tokens, int verbose)
{
    float saved = m->affect;
    m->affect   = -1.0f;
    char *out   = monad_speak(m, query, max_tokens, verbose);
    m->affect   = saved;
    return out;
}
```

---

## 13. The program: `main`

**Label:** `OURS`. **Source:** `main.c` lines 333–691 (`main`, 359 lines), 251–284 (`find_checkpoint`). Given as named steps; the runnable path is `SemPriCon/tools/verify_against_c.py`.

1. **M1 [flags].** A first pass over the arguments handles `-c <file>` (store), `-n` (never save), `-q` (quiet) and counts `-v`s. `g_self_ref` is set when there are at least three (`-vvv`), colour when at least two and both streams are terminals.
2. **M2 [store].** `find_checkpoint` tries, in order: the `-c` file, `$PTOLEMY_CHECKPOINT`, `~/.ptolemy/monad.bin`, `~/.ptolemy/monad_wordnet.bin`, `./monad_wordnet.bin`; the first that opens is used. If none opens the monad starts at the ground state.
3. **M3 [arguments].** Left to right: `-i` learns the identity text; `-l <text|file|url|->` learns as prose, `-L` as WordNet text; `-W <prompt>` speaks with `monad_speak_wick` (50 words maximum) and prints the reply on standard output; `-h` and others select other speaking modes.
4. **M4 [save].** If anything was learned and `-n` was not given: save to the store's own path, except that the file named `monad_wordnet.bin` is never overwritten in a session that did no ingest (`did_ingest`), and the program says "protected".

**Listing 29 — `find_checkpoint` (`main.c`, verbatim).**

```c
static const char *find_checkpoint(const char *flag_path)
{
    static char found[4096];
    static char home_monad[4096];
    static char home_ckpt[4096];

    if (g_ptolemy_dir[0]) {
        snprintf(home_monad, sizeof(home_monad),
                 "%s/monad.bin", g_ptolemy_dir);
        snprintf(home_ckpt, sizeof(home_ckpt),
                 "%s/monad_wordnet.bin", g_ptolemy_dir);
    }

    const char *env_path = getenv("PTOLEMY_CHECKPOINT");
    const char *cands[]  = {
        flag_path,
        env_path,
        home_monad[0] ? home_monad : NULL,   /* active education state */
        home_ckpt[0]  ? home_ckpt  : NULL,   /* fallback: wordnet state */
        "monad_wordnet.bin",
        NULL
    };
    for (int i = 0; i < (int)(sizeof(cands)/sizeof(cands[0])) - 1; i++) {
        if (!cands[i] || !cands[i][0]) continue;
        FILE *t = fopen(cands[i], "rb");
        if (t) {
            fclose(t);
            strncpy(found, cands[i], sizeof(found) - 1);
            found[sizeof(found) - 1] = '\0';
            return found;
        }
    }
    return NULL;
}
```

**Listing 30 — the `-W` handler and the save protection (excerpts, `main.c`).**

```c
        if (a.primary == 'W' && i + 1 < argc) {
            const char *query = argv[++i];
            int wv = (verbose >= 1) ? verbose : a.v;
            char *response = monad_speak_wick(m, query, 50, wv);
            printf("%s\n", response);
            free(response);
            continue;
        }

        /* Refuse to overwrite monad_wordnet.bin in non-ingest sessions.
         * Use -l to ingest or -c <other.bin> to save a separate checkpoint. */
        const char *base = strrchr(save, '/');
        if (!base) base = save; else base++;
        if (strcmp(base, "monad_wordnet.bin") == 0 && !did_ingest) {
            if (!quiet)
                fprintf(stderr, "[ptolemy] protected: %s — use -l to ingest"
                                " or -c <path> for a session checkpoint\n", save);
        } else {
            state_save(m, save, 0.0);
            if (did_ingest && !quiet)
                run_eval(save);
        }
    }
```

**Debug feed.** The program's tracing is its `-v` flag: each of the values above is printed on standard error as it is computed, in order, by `vout`. Transcript 2 is that feed, not a summary. It is the same practice as the author's `dbprint(text, client)` in `Ptolemy2/Pharos/UtilityFunctions.py` (a `client.DEBUGPRINT` flag gates a print of every change, skipping repeats of the last entries of `DEBUGLIST`): a live feed of every change at the console, in order.

---

# Part II: what the engine did

## 14. "What is your name": the reply, step by step

### 14.1 Setup

The reference binary (§2.8) was started with the store of §4 and the prompt `what is your name`, in `-W` mode, with the `-v` feed switched on and saving switched off (`-n`). Nothing was learned. The store is read-only.

### 14.2 The binary's own feed

**Transcript 2 — `ptolemy -c dirty/monad_wordnet_v4_20260519.bin -Wv "what is your name" -n`, standard error then standard output (24 lines; the invisible separators in the last line are shown as `·`).**

```text
[state] loaded dirty/monad_wordnet_v4_20260519.bin  vocab=24485  A=6825748  wc=121914388
[hear]  "what is your name"
  what               z#16194   γ=15010.512    σ=0.5  E=0.4540  β=7.552000  J_p=1.5568  phase=4(trail↓)  
  is                 z#1894    γ=2405.433     σ=0.5  E=0.2703  β=7.552000  J_p=0.5519  phase=4(trail↓)  [new]
  your               z#18893   γ=17171.526    σ=0.5  E=0.4887  β=7.552000  J_p=1.1501  phase=4(trail↓)  
  name               z#15471   γ=14425.021    σ=0.5  E=0.4447  β=7.552000  J_p=0.9524  phase=2(trans↑)  [new]
[J^μ — top 8 A-propagations]
  your(z#18893) → cldr(z#18907)  +9.7434e+02  A=1.7594e+02  β[18907]=7.5520
  nanti(z#1894) → finck(z#1910)  +1.3600e+02  A=5.1175e+01  β[1910]=7.5520
  what(z#16194) → eiki(z#17464)  +6.7890e+01  A=9.0561e+00  β[17464]=7.5520
  what(z#16194) → uib(z#16238)  +3.9499e+01  A=5.2689e+00  β[16238]=7.5520
  what(z#16194) → spads(z#16197)  +1.6553e+01  A=2.2081e+00  β[16197]=7.5520
  emite(z#15471) → nintu(z#15525)  +2.7066e+00  A=5.9014e-01  β[15525]=7.5520
  emite(z#15471) → oppf(z#15472)  +7.3746e-01  A=1.8314e+00  β[15472]=0.6631
  swfu(z#15469) → uryn(z#21058)  +1.1325e-02  A=1.8245e-02  β[21058]=7.5520
[Fermat Pointer]  z#16194   γ=15010.512
[affect e7]  -1.00  (passive)  Δpointer=8806
[golden walk]  step=9549  pointer=z#16194  J_floor=9.8895e+00
[Lagrangian]   ΣV=5.668e+03  ΣT=7.158e-01  ratio=0.000  target=4
[demotic]     z#24639   E=0.5625  target_E=0.5671  holcus
  emit z#1859    γ=2368.410  J=4.7909e+01  e^(iγ/2)=+0.175  same
  emit z#18482   γ=16844.788  J=1.0985e+01  e^(iγ/2)=+0.214  stuff
  emit z#0       γ=14.135  J=1.0478e+02  e^(iγ/2)=+0.706  seemy
[stdout] holcus·same·stuff·seemy
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

**Table 10 — emission for `what is your name` (port).** `ΣV = 5.6683e+03`, `ΣT = 0.7158`, `lag_ratio = 0.000126`, `actual_max = 4`, pointer z#16194 (γ = 15010.512), `J_max = 988.952`, `J_floor = 9.890`, `golden_step = 9549`, `target_E = 0.567068`, first word at slot 24639.

| stage | slot | stored word | emitted | J | separator before |
|---|---|---|---|---|---|
| demotic | 24639 | `holcus` | `holcus` | — | — |
| walk | 1859 | `same` | `same` | 47.909 | U+200B |
| walk | 18482 | `stuff` | `stuff` | 10.985 | U+200B |
| walk | 0 | `seemy` | `seemy` | 104.778 | U+200B |

**Table 11 — eight prompts, `-W`, the binary against the port, byte for byte.** 8 of 8 identical.

| prompt (`-W`) | reply (words) | separators | port identical |
|---|---|---|---|
| `what is your name` | `holcus`·`same`·`stuff`·`seemy` | U+200B·U+200B·U+200B | yes |
| `can you hear what i am typing` | `holcus`·`setn`·`abysmal`·`quun` | U+200B·U+200B·U+200B | yes |
| `who are you` | `holcus`·`abysmal`·`quun`·`tuxen` | U+200B·U+200B·U+200B | yes |
| `what is a tree` | `holcus`·`jome`·`logzh`·`cold` | U+200B·U+200B·U+200B | yes |
| `good morning` | `holcus`·`conoy`·`nland`·`abusive` | U+200B·U+200B·U+200B | yes |
| `the cat sat on the mat` | `holcus`·`bacoo`·`seemy`·`nanti` | U+200B·U+2003·U+200B | yes |
| `how do you do` | `holcus`·`behim`·`celiac`·`stuff` | U+200B·U+200B·U+200B | yes |
| `tell me about water` | `holcus`·`piezo`·`nazri`·`geolb` | U+200B·U+200B·U+200B | yes |

The first prompt is the screenshot's: `holcussamestuffseemy` is the reply `holcus·same·stuff·seemy` with zero-width separators. The second is the other screenshot reply, `holcus setn abysmal quun`. In the row for `the cat sat on the mat` a separator of the em-space band (U+2003) appears: the separator is not always zero-width.

**Figure 2 and Figure 3 are screenshots of the engine this paper describes, running.**

![The first question put to the engine that got a response (file dated 2026-05-19): `ls ~/.ptolemy`, then `ptolemy -h 'what is your name'` and `ptolemy -W 'what is your name'`. The `-W` reply is `holcussamestuffseemy`. File: `VAPMIP/SemPriCon/paper/figures/3-TheExtractor.png`.](figures/3-TheExtractor.png){width=95%}

![A second, unconnected prompt, intentionally complicated in context (file dated 2026-05-19): `ptolemy -W 'can you hear what i am typing'` and then `ptolemy -h` on the same prompt, in `Ptol/SMMIP/PtolC`. The reply is `holcus setn abysmal quun`. Provenance only: nothing in the engineering depends on it. File: `VAPMIP/SemPriCon/paper/figures/2-Hocus-Hyperwebster.png`.](figures/2-Hocus-Hyperwebster.png){width=95%}

### 14.4 What the reply is, as arithmetic

1. Each of the four prompt words is hashed to a slot and an energy (Table 9). Two of the four words are not the displayed word of their slot.
2. The depth β of all four slots is at the cap, so each puts `β·E²·exp(−0.05·age)` on its slot.
3. The weight spreads to three neighbours on each side, then crosses the links twice. The slot of `holcus` has a direct link to each of the four prompt slots (z#15471 w = 0.1688, z#16194 w = 0.3559, z#1894 w = 0.6468, z#18893 w = 0.9547).
4. `ΣT/(ΣT+ΣV)` is 0.000126, so four words are allowed.
5. The pointer is the slot whose γ is the median of the four prompt slots' γ.
6. The first word is the slot whose stored E is nearest to 0.567068 among slots that pass the floor and the gate: slot 24639, displayed as `holcus`.
7. The other three words come from stepping 9549 slots at a time from the pointer, keeping slots that pass the floor, the gate and `token_accept`: slots 1859, 18482 and 0.
8. Each word is replaced by `near_canonical` of its slot (here unchanged), and joined with the separator of its `J/J_max` (here all U+200B).

---

## 15. The first word

### 15.1 The selector reads nothing of the prompt

The rule of §12.8 compares stored E with a target that is within 10⁻³ of Ω for any short prompt. The only prompt-dependent inputs are which slots have `J > J_floor` and an open gate. Slot 24639 has E = 0.562514, 0.0046 below Ω.

### 15.2 The slot is the slot of the word *in*

Two words address slot 24639: `holcus` (E = 0.5625142041015625), `in` (E = 0.5625130258798404). The displayed word is the one with the larger E; the difference is 1.178e-06. **`holcus` is the label of the slot that the word `in` addresses.** `in` is one of the most frequent words of English, so its slot is among the best connected. The eight best-connected slots of the store:

**Table 12 — A-degree of the best-connected slots (port).** The median slot has 150 links.

| slot | A-degree | slot displays | function words that address here |
|---|---|---|---|
| 0 | 22,987 | `seemy` | — |
| 841 | 20,024 | `the` | `the` |
| 7919 | 19,113 | `and` | `and` |
| 8017 | 18,935 | `qgt` | `of` |
| 24639 | 18,268 | `holcus` | `in` |
| 11228 | 17,877 | `to` | `to` |
| 1894 | 15,340 | `nanti` | `is` |
| 24362 | 14,924 | `mcany` | `that` |

The slot of `holcus` has 18,268 links (rank 5 of 25 000). Each of the best-connected slots except slot 0 is the slot of a function word. Slot 0 is the slot of every word of eight letters or more (§6.1).

### 15.3 It does not depend on the prompt

150 random prompts of one to six words, drawn from the store's own displayed words, each from a fresh state (`age = 0`, `affect = 0`; port): `holcus` is the first word of 92; the next most frequent are `yack` 14, `aiao` 4, `auvrn` 1; 2 replies are empty; 140 of 150 replies have four words. The first word changes when a prompt does not put weight on a slot that connects to slot 24639, or when another slot's E is nearer `target_E`.

### 15.4 What the identity text contributes

The store carries the identity text of Listing 13 (§10.6). `PTOLEMY_IDENTITY` does not contain `holcus`, `stuff` or `your`; it contains `in`, `what`, `is` and `same`. The effect on the reply that can be shown is through links: the identity text links `in`, `what` and `is` to each other and to every other word in its sentences, and those links are in the store at the weights the learning formula gives. Which links produced the weight on `same`, `stuff` and `seemy` is not separated here.

### 15.5 What is established and what is not

Established by the code and the runs (`OURS:CALCULATED`): the first word is the display label of the slot that `in` addresses; it is chosen by the nearest-E rule among slots above the floor; it does not depend on the prompt except through the floor and the gate. The reply reproduces from source, twice.

Not established: whether the coincidence of a two-word collision, resolved by 1.2·10⁻⁶ in E, producing a word that is also the program's family name is significant. It is a measurement, not a derivation. **`OPEN`:** which ingest introduced `holcus` into the store. The word is a WordNet lemma (the genus of velvet grasses); the build has no training log.

### 15.6 Multilingual content

The store contains 0 non-ASCII words. The tokenizer of this build (§9.2) discards every non-ASCII byte, so no ingest path of this build could have admitted one. Any multilingual experiment that preceded this build (the author recalls one, in which Unicode alphabets were loaded into a "potential response domain") is not recorded in this program or in this store.

---

## 16. The store, assessed

The store was assessed by `SemPriCon/tools/assess_bin.py`, which applies the project's own checkpoint evaluator (`VAPMIP/tools/eval_checkpoint.py`: classifier, entropy, Gini) and the 2026-10-17 token sanitiser (`VAPMIP/Wernicke/sanitize/sanitize_v0.py`), and adds a script census. The results are committed beside the store: `monad_wordnet_v4_20260519.ASSESSMENT.md`, `.assessment.json` and the dirty notice `.POISON.md`.

| quantity | value |
|---|---|
| format, size | PTOL v4, 110,040,527 bytes, all consumed |
| slots, vocabulary, links, word count | 25,000, 24,485, 6,825,748, 121,914,388 |
| entropy, Gini | 88.68 % of maximum (natural band 85–92); 0.7564 (0.60–0.80) |
| β at the cap | 1,826 occupied slots |
| polluted (project classifier) | 1,233 (5.04 %) |
| quarantined (sanitiser) | 1,008 (4.12 %) |
| displayed words with no WordNet synset | 18,409 (75.2 %) |
| non-ASCII displayed words | 0 |

**Table 13 — pollution classes (project classifier).**

| class | tokens |
|---|---|
| consonant-only | 993 |
| consonant-cluster-3 | 654 |
| no-vowel | 344 |
| hex-string | 268 |

Displayed-word lengths: 2: 200, 3: 2,518, 4: 6,875, 5: 12,545, 6: 2,330, 7: 17. `prose_seen` over occupied slots: 3: 13,594, 2: 158, 1: 10,538, 0: 195.

**Verdict: DIRTY, PASS.** Pollution is below the 20 % PASS line and above the 1 % CONVERGED line. The same bytes were found in a `clean/` directory (labelled "WordNet 3.1 + Gutenberg … the most thoroughly trained English field in the archive") and in a `dirty/` directory (with a 2026-05-17 assessment of 5.04 %); the assessment above settles the placement as dirty. Record of the Fresh Start Protocol for this store: the assessments were committed and pushed first (`VAPMIP` commit `29b2d2d`); only then was the store added to the directory's `.gitignore` (commit `6ec2b3d`). The programs the author runs today (`monad3_c.bin` and everything `ptol.c` reads) were not touched.

---

# Part III: limits, plans

## 17. The limits, measured

Each item states what the code does, one measurement, and the consequence. Nothing is corrected.

**17.1 Address resolution collapses with word length (§6.1).** 49,018 of 76,719 WordNet lemmas address to slot 0, E = d\*; the lemmas reach 11,599 of 25 000 slots. Consequence: virtually every word of eight or more letters shares one address with every other; the engine cannot distinguish `philadelphos` from `septuagint`.

**17.2 The displayed word of a slot is the highest-E arrival, so the vocabulary is not the words met (§10.4).** Only 3,919 of 76,719 WordNet lemmas (5.1 %) are the displayed word of their slot; `tree`, `water`, `name`, `is` display `typhon`, `defrg`, `emite`, `nanti`. Consequence: a trace shows labels, not words; the weights belong to the slot.

**17.3 The zeros are approximations (§5.2).** Error against the true zeros 1.8 at n = 21, 0.28 at n = 25 000.

**17.4 Reply length is fixed by a ratio that is ≈ 10⁻⁴ (§12.4).** `lag_ratio = 0.000126`; `actual_max = 4` for short prompts on this store; replies are four words (140 of 150 in §15.3).

**17.5 β saturates (§10.2).** 1,826 of 24,485 occupied slots sit at the cap, so β does not discriminate between them.

**17.6 A comment and the code disagree (§12.8).** The comment before the first-word selection says it chooses "from first 200 qualifying walk candidates"; the code scans all N slots. The comment before the walk says it "visits every zero exactly once"; that depends on gcd(step, N) = 1, which is not checked.

**17.7 Constants and a stored value nothing reads (§5.1).** Never used outside `ptolemy.h`: `MONAD_TAU`, `MONAD_WINDOW_MIN`, `MONAD_EMIT_THRESH`. `emission_threshold` is stored and loaded and never read.

**17.8 The word map is not saved (§7).** After a reload only displayed words are known; every other word is `[new]`. The flag is not evidence about whether a word was met.

**17.9 `prose_seen` belongs to the slot (§10.4).** 8,968 slots flagged "WordNet and prose" (3) display a word that has no WordNet synset.

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

**Limitations of this paper.** The port covers learning and the `-W` speaking mode; it does not cover `-h`, `-O`, the REPL or the daemon. One store and one commit were examined. The store was identified by its header numbers and the screenshot text; the screenshot image itself was not re-measured. That the store was built with `-i` is an inference from the presence of all 646 identity links; no ingest log exists. The statements about earlier Python-era experiments are the author's recollection and are not tested here. The literature in the References was cited, not fetched, except where a copy is noted.

**Conclusion.** The engine that answered "what is your name" is 65 functions of arithmetic. It addresses a word by multiplying a base-95 number by the golden ratio, learns weights between slots that occur near each other in text, and replies by spreading weight from the prompt's slots, choosing a first word by a nearest-value rule and the rest by a golden-angle walk. Its first word is the label of the slot that the word *in* addresses. Its store is a table of slots, not of words. It cannot tell apart words of eight letters or more and cannot read a character outside ASCII. The description above reproduces its replies to the byte and its learned state exactly. That is the baseline.

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

Johansson, F., et al. *mpmath: a Python library for arbitrary-precision floating-point arithmetic*, version 1.3.0, `mpmath.org`. Used to compute the true zeros of §5.2.

*None of these was fetched in the writing session; their bibliographic details are given from the author's and the assistant's knowledge and must be checked against the sources before the paper is filed. Where the Literature Download Protocol (`ContextPlease/claude/references/INDEX.md`) later records a verified copy, the copy replaces this note.*

---

## 20. ContextPlease inclusions and links

Every path is `REPO/directory/file` under `https://github.com/michaelrendier/`.

**What ContextPlease is.** ContextPlease (`ContextPlease`) is the author's versioned memory for work done with a language model: notes, protocols, skills, primers and scratch directories that let a fresh model session come up to speed with historical access instead of re-deriving what is already known. It exists because a model has no memory of its own between sessions.

### 20.1 Code and data, by section

- **§2.7, §3–§13 (the program):** `VAPMIP/PtolC/` at commit `eb28ce8` (`monad.c`, `state.c`, `tokenizer.c`, `filter.c`, `main.c`, `ptolemy.h`, `monad.h`, `filter.h`, `state.h`), copied unmodified to `VAPMIP/SemPriCon/src/PtolC_eb28ce8/`
- **§4, §16 (the store):** `VAPMIP/checkpoints/clean/monad_wordnet_v4_20260519.bin` (gitignored), `VAPMIP/checkpoints/clean/PRIMER_from_dot_ptolemy.md`, `VAPMIP/checkpoints/README.md`, `PTorrent/bin_archive/README.md`
- **§16 (assessment):** `VAPMIP/tools/eval_checkpoint.py`, `VAPMIP/Wernicke/sanitize/sanitize_v0.py`, `VAPMIP/SemPriCon/tools/assess_bin.py`, `VAPMIP/SemPriCon/dirty/*.POISON.md|ASSESSMENT.md|assessment.json`
- **§10.8, §14.3 (verification):** `VAPMIP/SemPriCon/tools/monad_py.py`, `ptol_bin.py`, `verify_against_c.py`, `verify_learn_against_c.py`
- **Notebooks (executed):** `VAPMIP/SemPriCon/notebooks/01_the_store.ipynb` … `06_shortcomings.ipynb`
- **§13 (debug feed):** `Ptolemy2/Pharos/UtilityFunctions.py` (`dbprint`)

### 20.2 ContextPlease files used

- `ContextPlease/claude/hist_prime/VAPMIP/CONTEXT_PRIMER_2026-10-16_SEMANTIC_ORBWEAVER.md` and `semantic_orbweaver_notes.md` (the earlier trace of this engine, 2026-10-17, and the descriptions this paper checks against the code)
- `ContextPlease/claude/scratchpad/2026-10-17_T0_trace/` (the `monad.c` at `eb28ce8`, the earlier traces)
- `ContextPlease/claude/scratchpad/2026-10-18_name_engine_workbench/` (the first build and run of the reference binary)
- `ContextPlease/claude/hist_prime/VAPMIP/checkpoints/clean/PRIMER.md`, `ContextPlease/claude/monad_bin/poison_notes/` (the format of the dirty notice)
- `ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md` (how code is shown in this paper)
- `~/.clauderc_context_1`, `~/.clauderc_context_2` (session state)
