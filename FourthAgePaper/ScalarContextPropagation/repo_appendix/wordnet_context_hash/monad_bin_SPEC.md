# monad.bin — Formal Specification

**Version:** `monad.bin/merged` (format v1) · 2026-08-29
**Producer:** `build_monad_bin.py merge` · **Consumers:** `VAPMIP.monad.Engine.load_bin`,
`VAPMIP/monad_combine.py` (→ packed C form for `ptol.c`)

`monad.bin` is the Monad's whole brain in one file: **both the vocabulary**
(every word → its deterministic address) **and the knowledge store** (the
scalar β-field, the E-field, and the A-matrix co-occurrence topology). It is a
union of *factor bins*, each built by corpus ingestion; the union is
order-independent and byte-reproducible from the same factor set.

---

## 1. Container

A single Python **pickle** (protocol 4) of one `dict`. `Engine.load_bin` also
accepts the legacy PTOL binary (`magic == b"PTOL"`) — see §5 — but `merge`
always emits the pickle.

## 2. Top-level keys

| key | type | meaning |
|---|---|---|
| `version` | `str` | `"monad.bin/merged"` for a merged bin; `"vX.Y"` for a single-corpus session bin |
| `n` | `int` | vocabulary size = `len(words)` |
| `vocab` | `dict[str, int]` | word → row index |
| `words` | `list[str]` | row index → word (cleaned: lowercased, edge punctuation stripped) |
| `beta` | `list[float]` | β-field, one per word. Knowledge depth at that address. Range `(0, MONAD_BETA_SAT]` — `MONAD_BETA_SAT = 7.552` (`PtolC/ptolemy.h`), not `(0, 1]` as this spec previously stated: checked directly against the live cap in `monad_learn_ex` (`PtolC/monad.c`), the formula the daemon actually runs. Seeded at `GAP ≈ 7.07e-4`. The `monad.bin`/`Crank.learn` build path (§4, §9) separately caps at `1.0` on its own accumulation rule; `monad3_c.bin`'s own β field is kept in sync with the live in-memory value via `daemon.c::monad3c_fold_inplace` (periodic in-place mmap write, not a rebuild), so once the daemon has grown a word past `1.0` live, that is `monad3_c.bin`'s real value — the bootstrap-time `≤1.0` figure is only the file's starting point, not its ceiling. |
| `E` | `list[float]` | E-field, one per word. `E = |sin(π·γ / (γ+1))|` where `γ` is the word's Riemann-zero value. Fixed by the address — not learned. |
| `A` | `list[dict[int, float]]` | sparse A-matrix. `A[i][j]` = directed co-occurrence weight i→j, range `(0, 1]`. Row `i` is the out-edges of word `i`. |
| `age` | `list[float]` | temporal decay counter per word; `0.0` = just touched |
| `fire_count` | `list[int]` | emission counter per word |
| `stratum` | `list[int]` | tower stratum: `0` = critical line, `1` = octonion, `2` = sedenion |
| `psi_prev` | `list[float]` (16) | last ψ window state |
| `word_count` | `int` | total words ever learned |
| `correction_mask` | `dict[int, dict[int, float]]` | sparse edge-suppression overlay ∈ `(0, 1]`; absent = 1.0 (unmodified). Applied in `a_propagate`. "The field remembers what it unlearned." |
| `_provenance` | `list[dict]` *(merged bins only)* | per factor: `{bin, weight, sha256, project, vocab, edges}` |
| `_bootstrap` | `dict` *(bootstrap builds only)* | `{kind: "project-fluent", spec_version: int, project_corpus_sha256: str, project_first: true, project_factors: list[str]}` — see §8 |
| `_built` | `str` *(merged bins only)* | ISO timestamp |

A single-corpus bin written by `Engine.save_session` has the same keys minus
`_provenance` / `_built`.

## 3. Word → address (deterministic, corpus-independent)

Every word's row is a *label*; its **address** is derived, not assigned:

```
H(w)   = Σ_{k} ord(w_k) · 95^{|w|-1-k}   (mod 2^16)     Horner, base 95, offset 32
p      = next_prime(H(w))
idx    = π(p)                                            prime-counting index
γ      = the idx-th non-trivial Riemann zero (imag part), found by Z(t) Newton
E(w)   = |sin(π·γ / (γ + 1))|
```

Two runs on the same corpus produce identical `E` for the same word. This is
why the merge (§4) is collision-free and order-independent: a word carries the
same address in every factor bin.

## 4. Merge semantics (`build_monad_bin.py merge`)

Given factor bins `F_1 … F_m` with weights `w_1 … w_m`, folded in order:

- **vocab / words** — set union. First factor to contain a word seeds its row.
- **β** — on first sight: `β ← min(β_F · w, 1)`. On a later sight of the same
  word: `β ← min(β + β_F · w, 1)`. A word attested across many domains gets a
  deeper field.
- **E** — taken from the first factor that has the word (address-fixed, so all
  factors agree anyway).
- **A-matrix** — `A[i][j] ← min(A[i][j] + w_F · A_F[remap(i)][remap(j)], 1)`.
  Self-edges (`i == j`) dropped.
- **age** — first-seen value; `fire_count` / `stratum` reset to 0.
- **`_provenance`** records each factor's sha256 + weight + counts.

Determinism: identical factor set (by sha256) + identical weights + identical
fold order ⇒ identical `monad.bin`.

## 5. Packed C form (`monad3_c.bin`) — what `ptol.c` actually reads

`ptol.c` does **not** read `monad.bin` directly. It `mmap`s a fixed-offset,
zero-copy packed file `monad3_c.bin` (layout in `PtolC/monad3c.h`,
`MONAD3C_MAGIC = "MONAD3C\0"`):

```
[ Monad3cHeader ][ word blob ][ WordRec[n_words] sorted by name — bsearch ]
[ eng: beta f64[nE]  E f64[nE]  age i32[nE]  fire i32[nE]  stratum i32[nE] ]
[ eng A-matrix CSR:  rowptr u32[nE+1]  col u32[nnz]  w f32[nnz] ]
[ wn:  BoxKiteEntry[nW]  (WordNet box-kite table) ]
[ phon: ix u64[nP+1]  blob (len-prefixed ARPAbet tokens) ]
```

`monad_combine.py`:
- `CombinedMonad(english=<monad.bin state>, wordnet=read_boxkite_c(), phonetic=read_phonetic())`
- `write(cm, path)` → the intermediate MONAD3 pickle
- `write_c(cm, path)` → `monad3_c.bin` (+ regenerates `monad3c.h`)

The merged `monad.bin` supplies the `eng:` sections (β / E / A CSR / word
table); the WordNet and phonetic sections come from `c_monad_wordnet.bin` and
`monad_phonetic.bin` unchanged.

## 6. Bootstrap marker and build safety

`bootstrap.py` is the canonical build. It ingests the ContextPlease
engineering corpus FIRST (the project factor bins: `monad_engineering.bin`,
`monad_war.bin`, `monad_repos.bin`, folded before all others), then general
language, then any `--add` user trees. The output carries `_bootstrap`
(above). `_provenance[i].project` is `true` for the project + user factors.

**Safety.** Before overwriting `~/.ptolemy/monad.bin`, the build reads any
existing `_bootstrap`:
- missing / `kind != "project-fluent"` / different `spec_version` → **refuse**
  (exit 2); the user must pass `--override`, which copies the old file to
  `monad.bin.bak-<ts>` first.
- same `kind` + `spec_version` → refresh in place.

**C side.** `PtolC/monad_guard.sh <candidate> <installed>` does the
equivalent for `monad3_c.bin`: compares the `MONAD3C` magic + version stamp,
refuses a mismatched overwrite unless `PTOL_MONAD_OVERRIDE=1` (which backs
up first). The ptol.c build calls this before installing the store.

## 7. Size and distribution

The merged pickle is ~66 MB and grows with the corpus. GitHub **release
assets** allow 2 GB, so `monad.bin` ships as a release asset directly. The
**preferred** path (Cody, 2026-08-29): ship the *corpuses* (in ContextPlease)
and the *builder*, and let each user rebuild `monad.bin` on-box from whatever
corpus subset they point it at. Factor bins (`monad_*.bin`, each ≤ 36 MB here)
are the intermediate rebuild artifacts and can also be shipped individually.

## 8. Conversational ingest and paragraph recognition

`service/` is the live-ingest path (Cody, 2026-08): the Monad also learns
passively from conversation. The Claude Code hook `service/hooks/monad_observe.py`
is wired `UserPromptSubmit → external`, `Stop → internal`; it prose-sanitises
the turn (`harness.strip_to_prose`), splits it (`harness._sentences`) and
writes a non-blocking FIFO message to the daemon (`PtolC/daemon.c`), spooling
to `~/.ptolemy/observe.spool` if the daemon is down. The FIFO header is
`<class> [pair_id]` with `class ∈ {external, internal, document}` (exact
`strcmp` in the C daemon — the token set is fixed); `w_sem` weights are
external 1.5, internal 0.9. A prompt and its response share a `pair_id`
(stashed at `~/.ptolemy/.pair-<session>`). The hook must never block the
prompt or fail the turn — every step is best-effort and it always exits 0.

**Paragraph recognition (semantic side).** The semantic section of the Monad
is the *paragraph builder along paragraph grammar* (phonetic ↔ context,
semantic ↔ content/prompt). An `external` prompt of more than one sentence
**is a paragraph, by definition**. When `monad_observe.py` sees that, it
appends a best-effort sidecar record to `~/.ptolemy/paragraphs.spool.jsonl`:

```
{"kind":"paragraph","pair":<pid|null>,"session":<sid>,"ts":<epoch>,
 "n_sentences":<n>,"sentences":[<raw sentence>, …]}
```

This is purely additive — the normal `external <pid>` FIFO message is
unchanged. The **higher-order prime semantic hash** over that structure is
computed *downstream* by the paragraph-builder, never in the hook (it loads
WordNet). `semantic_paragraph.paragraph_hash(sentences)` composes the
original per-word prime semantic hash (`context_hash_v2.code_omega` /
`wordnet_boxkite.context_code` — squarefree product of the primes for the
WordNet relations a synset fires) up one structural level:

- `sentence_omega` = radical of the product of the sentence's content-word
  codes — the squarefree **set** of relations that sentence engages;
- `paragraph_omega` = product of the sentence omegas — its prime
  factorisation gives `(relation, sentence-count)` pairs: `support` is the
  paragraph's semantic footprint, each exponent is how many sentences
  sustain that relation;
- `grammar` = per-sentence dominant relation in reading order (branching
  channel `hyponyms` dropped, as `code_omega` does) — the argument arc.

## 9. Reproduce

```
python3 bootstrap.py            # canonical: project corpus first, then general language
# or, step by step, from corpuses (ContextPlease/claude/monad_bin/ + hist_prime + repo prose):
python3 corpus_strip.py  > corpus_all.txt          # primers + TODOs → prose
python3 corpus_repos.py --ingest                   # all repo wiki/README prose → monad_repos.bin
python3 ingest.py                                  # corpus_all.txt → monad_engineering.bin
python3 ingest_war.py                              # prime-directive primers → monad_war.bin
# then:
python3 build_monad_bin.py merge                   # union → ~/.ptolemy/monad.bin (+ manifest.json)
python3 build_monad_bin.py verify
```
