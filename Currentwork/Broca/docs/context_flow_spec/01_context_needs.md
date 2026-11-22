# 01 — Context Needs

**Establishes:** what context the system must hold, at what granularity, in what
form, and what it must hand over at each seam. This is the first design
document because every later method consumes or produces one of these items.

Needs are numbered **CN-nn**. A later document that depends on a need cites its
number.

---

## 1. Two jobs, two contracts

The Zork Sentence Parser must both **deconstruct** a sentence and **construct**
one (and, later, larger text objects). They need different things from context.

| | Deconstruct (read) | Construct (write) |
|---|---|---|
| Sees | The whole input unit at once | Only what has already been emitted, plus the plan |
| Order | Unordered / simultaneous | Ordered, each step conditioned on previous |
| Output | A structured reading (roles, topic, act, focus) | A word sequence |
| Existing analogue | `MindsEye.snapshot()` — "all at once, none of it ordered" [CODE: `rotary_rerun_monad.py` contract, quoted in `19D_boxkite_context_monad.py`] | `PapersHands.emit_*` — emits in sequence [CODE] |
| Existing C/py entry | `zork_parse()` (`PtolC/zork.h`) and `engine/grammar/shadow.py` `reduce()` | `console_speak()` → `get_monad_sentence()` → `ptolc_bridge.py` [CODE: `ptol.c`] |

**CN-01.** Deconstruction produces a *reading record* (§3). Construction consumes
a *plan record* (§4). The seam between them is the **context state** (§5).

**CN-02.** Neither job may require the other's data structure internally. The
reading record and the plan record are plain data; the context state is the only
shared mutable object.

## 2. Existing interfaces (what is already true) [CODE]

These are facts about the repository on 2026-10-12. They constrain the design.

### 2.1 Zork parser (`PtolC/zork.h`)

`ZorkResult` carries: `op` (sedenion operator 0–15), `op_name`, `verb`, `noun`
(first noun phrase), `noun2` (ditransitive second noun), `prep`, `prompt`, `ok`,
`error`, and slash-command fields. Documented mapping:
VERB → sedenion operator; NOUN → word in monad vocab; PREP → relation label;
**IT → last-mentioned noun (e₁₁ dereference)**. Context is a single remembered
noun (`g_last_noun`, reset by `zork_reset_context()`).

> Consequence: the current parser's whole context memory is **one noun**. Centering
> (`06_centering.md`) is the principled generalisation of that single slot.

### 2.2 Construction call (`ptol.c`: `get_monad_sentence`, `infer_speech_act`)

Three inputs go to the sentence creator, written to a temp file and piped to
`python3 -m engine.grammar.ptolc_bridge`:

```
GAMMA <float>               Γ ∈ (−1, 1), from measure_gamma()
ACT   <speech_act>          one of 7 keys
WORDS <lemma> <lemma> ...   firing word bag, spiral order, deduplicated
```

Speech acts (`engine/grammar/sails.py` `SPEECH_ACTS`): `what_does_X_do`, `who_Xs`,
`how`, `why`, `where`, `define_X`, `yesno`. `infer_speech_act` is a wh-word scan,
explicitly "heuristic, not a parser".

On failure the bridge prints nothing and exits nonzero; `console_speak` keeps the
word bag (**guaranteed fallback**).

### 2.3 Register bands (`sails.py` `REGISTER_BANDS`)

|Γ| → register: narrative [0, 0.33), surface [0.33, 0.55), technical [0.55, 0.78),
thesis [0.78, 1.01). Here Γ is `context_hash_v2`'s dissertational↔narrative scale.

> Note: `ptol.c` uses **two different Γ's** (documented in-source). `measure_gamma()`
> is the J_red/J_blue sedenion-projection amplitude. `monad3_gamma_radial()` is the
> WordNet-relational fold. `get_monad_sentence` is passed the former. The spec
> keeps them distinct: **Γ_proj** (projection) and **Γ_rad** (relational).

### 2.4 The per-word context vector (`monad3_c.bin`, `wordnet_boxkite.py`)

Each WordNet entry is an 82-byte record: `word[32] pos[1] pad[3] offset[4]
vec[19] depth_weight[4]`. `vec[19]` holds one **log-compressed relation count per
relation method**, in the order of `RELATION_METHODS`:

```
0 hypernyms          5 substance_holonyms   10 attributes      15 similar_tos
1 instance_hypernyms 6 part_holonyms        11 entailments     16 topic_domains
2 hyponyms           7 member_meronyms      12 causes          17 region_domains
3 instance_hyponyms  8 substance_meronyms   13 also_sees       18 usage_domains
4 member_holonyms    9 part_meronyms        14 verb_groups
```

`compress_count(n) = round(log2(n+1))` is applied to the count *before* it becomes
an exponent. `monad3_gamma_radial(vec) = tanh(½ · ln(log_code / anchor))` with
`log_code = Σ vec[i]·ln(prime_i)` over `GR_CONTEXT_PRIMES[19]` and an anchor that
excludes the hyponyms slot (`GR_HYPONYMS_IDX = 2`). Returns NaN where
`log_code ≤ 0`.

Lookup is a lower-cased binary search over the sorted `WordRec` table, zero-copy
over an mmap (`monad3_lookup`).

**CN-03.** Any context method that needs a per-word vector must read `vec[19]`
(or its derived scalar Γ_rad) from this store. No other per-word representation
may be introduced without a spec revision.

**CN-04.** Whether the hyponyms slot is included in a similarity must be a
declared parameter of the experiment, since the Γ_rad anchor excludes it.
[PARAM: `include_hyponyms`, default **false** to match the anchor.]

### 2.5 Existing structure analysis (`engine/grammar/shadow.py`)

`reduce(sent) → Shadow` yields `pos`, a `ring` (e0 = finite verb anchor, e1..eK
dependents, edges = Universal-Dependencies deprels), `spoca` slots over
`S P O_d O_i C_s C_o A`, and the clause `pattern` (one of 7). `check(shadow)`
returns `prime` (verb licenses the pattern) or `composite` (residue = the
unlicensed pattern).

## 3. The reading record (output of deconstruction)

**CN-10.** A reading record has these fields. Fields marked ★ already exist in
some form (§2); the rest are new.

| Field | Type | Source |
|---|---|---|
| `text` | string | input |
| `tokens` | list of token records | tokenizer |
| `speech_act` | one of the 7 keys | ★ `infer_speech_act` (heuristic) |
| `verb`, `verb_lemma` | string | ★ `shadow.reduce` |
| `pattern` | one of 7 clause patterns | ★ `shadow.reduce` |
| `spoca` | slot → forms | ★ `shadow.reduce` |
| `entities` | ordered list (ranked by role) | **new** — feeds Centering Cf |
| `topic_vec` | float[19] | **new** — decayed sum of `vec[19]` |
| `gamma_proj`, `gamma_rad_mean` | float | ★ / **new** |
| `ring_point` | (r₁, r₂, Γ) | **new** — Smith-chart locator output |
| `oov` | list of tokens not in store | **new** |
| `refusals` | list of explicit refusals | **new** — see CN-12 |

**CN-11.** A token record has `surface`, `lemma`, `pos`, `in_store` (bool),
`vec19` (or null), `gamma_rad` (or null), `role` (or null).

**CN-12.** Deconstruction must **refuse explicitly** rather than guess when: the
input is empty; no token is in the store; the clause pattern is `composite`; or
the speech act cannot be inferred and the caller required one. A refusal is a
value in `refusals`, never an exception swallowed silently and never a default
that looks like a reading.

## 4. The plan record (input to construction)

**CN-20.** A plan record is an ordered list of **units**. Each unit has:

| Field | Meaning |
|---|---|
| `unit_id` | stable identifier |
| `level` | granularity level L1–L3 (§6) |
| `speech_act` | what kind of sentence |
| `focus_entity` | the intended Cb / topic of the unit |
| `content_words` | selected NOUN/VERB/ADVERB lemmas (from vocabulary mechanism) |
| `relation_to_prev` | RST relation to the previous unit, or null for the first |
| `connective` | pathway word chosen for that relation, or null |
| `register` | band from `REGISTER_BANDS` |

**CN-21.** The plan is built **before** any surface text is produced
(Reiter & Dale document planning; `08_generation_pipeline.md`).

**CN-22.** The sentence creator (`engine/grammar/generate.py`
`build_response`/`ParseSpec`) already accepts a `ParseSpec(speech_act, verb,
topic_lemmas)` and a depth band. A plan unit maps onto one `ParseSpec`;
no change to the creator's interface is required for L1 (sentence) generation.

## 5. The context state (the only shared mutable object)

**CN-30.** Context state is a small fixed-size record, copyable by value:

```
ContextState:
    C[L]        float[19] per level L ∈ {L0..L4}   decayed topic vector
    m[L]        float     per level: decayed mass (normaliser)
    Cf          ordered list of entities of the previous unit   (Centering)
    Cb          entity or null
    last_rel    RST relation of the previous unit or null
    ring_visited   set of ring positions already used          (Smith-chart)
    step        int       unit counter
```

**CN-31.** Context state is **deterministic**: the same input sequence from the
same initial state gives a bit-identical state. (Needed for regression tests.)

**CN-32.** Context state has an explicit **reset** operation and an explicit
**boundary** operation (§6.3). There is no implicit forgetting.

**CN-33.** Context state must be serialisable to a fixed byte layout so a C port
can hold it without allocation. [C-port note; no format is fixed here.]

## 6. Granularity levels

The author's plan includes "different granularity models". The spec fixes the
level names so documents agree:

| Level | Unit | Typical span | Reset by |
|---|---|---|---|
| **L0** | word | 1 token | never (always integrates) |
| **L1** | clause / sentence | ≈ 5–40 tokens | sentence boundary |
| **L2** | paragraph / topic segment | ≈ 3–10 sentences | topic-shift boundary (`05_*`) |
| **L3** | document / response | whole response | start of response |
| **L4** | session / conversation | many turns | explicit reset only |
| (L5) | ingested knowledge | — | reserved; hyperindexer, out of scope |

**CN-40.** Every context method states which level(s) it reads and writes.

**CN-41.** Time constants grow with level (`04_carry_over_decay.md`):
τ(L0) < τ(L1) < τ(L2) < τ(L3) < τ(L4). The ordering is a hard requirement; the
values are [PARAM].

**CN-42.** A *boundary event* at level L (a sentence end, a detected topic shift)
acts on the integrators at levels ≤ L and leaves levels > L untouched.

### 6.3 Boundary operation (definition)

`boundary(L, β)`: for every level `l ≤ L`: `C[l] ← β·C[l]`, `m[l] ← β·m[l]`.
`β = 0` is a hard reset; `β = 1` is a no-op. `β` is a [PARAM] per level.

## 7. Open design questions (to be closed by experiment)

| ID | Question | Closed by |
|---|---|---|
| Q1 | What is the largest unit one pass should hold in view? | `PERF-05`, `DEC-*`, calibration tier 1/2 |
| Q2 | What survives from one sentence to the next, beyond Cb/Cf? | `DEC-04`, `CEN-05` |
| Q3 | Does deconstruction run over the whole text first, or alternate with construction? | `GEN-01` vs an alternating variant (not yet specified; add as `M-PIPE-ALT` if chosen) |
| Q4 | Is `vec[19]` cosine a better topic similarity than Γ_rad difference, a Jaccard of non-zero slots, or a log-transformed cosine? | `SM-04`, `SM-05`, `TT-02` |
| Q5 | Which two relationships make an independent ring pair? | `SM-02` |
| Q6 | Does word sense need disambiguation before the vector is read, or can the topic sum absorb it? | `CAL` ambiguous-word items; `SM-04` |

## 8. Reserved slots (ingested knowledge)

**CN-90.** Level L5 and a `knowledge_ref` field in plan units are reserved for
hyperindexed ingested knowledge. No method in this spec may *depend* on them; a
method may *expose* a hook where they would attach. Nothing is tested.

## 9. Tests that cite this document

Needs are exercised indirectly through the method tests; the direct checks are:
`GEN-02` (fallback honoured), `GEN-03` (all content words in store), `DEC-*`
(CN-31 determinism), `SPL-*` (CN-10..CN-12 record shape).
