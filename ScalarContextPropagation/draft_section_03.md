## 3. "The primes are the words"

Every mechanism in this paper eventually addresses a word by its
*relational* structure — what it means in context, not how it's spelled.
That wasn't the starting idea. The starting idea, in `VAPMIP/monad.py`
since 2026-05-27, unaltered since, was simpler and more ambitious at
once: that a prime number could stand for a **concept**, the same
irreducible way it stands for a number — and that mapping a word onto one
would be enough, on its own, to place related words near each other,
across languages, because the concept was assumed to be prior to any
particular spelling of it. §3.4 is honest about what running that idea
actually produced: a field of collisions dense enough that the scripting
around it was shelved — not because the idea was "wrong" in some final
sense, its success or failure was never really the point, but because
that density is what pointed toward relational *structure*, not a bare
address, as the place to keep looking. This section is the mechanical
piece underneath that whole arc: a deterministic, collision-mostly-
avoiding map from a word's spelling to an address, read from the code
that has run, unmodified, for four months.

**Two real screenshots, not staged for this paper — the actual first
runs:**

**Figure 3a.** `SpaceClaude/funny-ptolemy.png` — the very first time this
machinery was ever run: `ptolemy -l 'what is your name'` →
`Segmentation fault (core dumped)`. Kept in the record on purpose, not
cropped out: this is what "the first attempt at semantic hash" actually
looked like, the honest starting point before any of the rest of this
paper existed.

*Shoutout to Max Cohen's computer — Euclid.*

**Figure 3b.** `SpaceClaude/TheExtractor.png` — the first real question
put to the running system, asked two ways. `ptolemy -h 'what is your
name'` prints the per-word state table (`z#`, `γ`, `σ=0.5`, `E`,
`β=7.552000` — the same `MONAD_BETA_SAT` cited in §8, visible here from
the very first run); `ptolemy -W 'what is your name` then returns
`holcussamestuffseemy`. This is where the name **Holcus** came from — a
real word (a grass genus, "Yorkshire fog") surfacing out of the very
first multilingual semantic-prime-hash run, not chosen in advance.

### 3.1 The address, in the four lines it actually is

```python
# VAPMIP/monad.py — unaltered since commit 204c75d, 2026-05-27
_PRIME_CAP = 1 << 16                      # 65536 — primes searched in [2, 65537]

def _horner_hash(w: str, base: int = 95, offset: int = 32) -> int:
    v = 0
    for ch in w:
        v = v * base + max(0, ord(ch) - offset)
    return abs(v)

def _word_zero_idx(w: str) -> int:
    v = _horner_hash(w)
    p = _next_prime(v)                    # smallest prime >= v mod _PRIME_CAP
    idx = _prime_pi_table[min(p, _PRIME_CAP + 1)]   # pi(p) -- count of primes <= p
    return max(1, idx)
```
Live, runnable: `notebooks/01_semantic_prime_hashing.ipynb`, cell 3 —
the same function, unmodified, wrapped for tracing.

Per [`cs-paper-code-conventions`](../../.claude/skills/cs-paper-code-conventions/SKILL.md)
§1: this is `OURS`, short, and *is* the paper's contribution at this
step — it gets the real listing, not a Σ standing in for a loop. Three
established pieces do the actual work, cited and not re-derived: a
Horner polynomial evaluation (base 95, the size of printable ASCII) turns
a word's spelling into one integer; a sieve of Eratosthenes, run once at
import, supplies both a fast `next_prime` and a precomputed `π` table
(count of primes ≤ *k*, for every *k* up to 65536); composing them sends
a word to **which of up to 6,543 non-trivial Riemann zeros indexes its
address**. (The non-trivial zeros of the Riemann zeta function are a
fixed, established, precomputable sequence of real numbers, indexed
1, 2, 3, ...; nothing in this paper depends on why they're
mathematically significant, only that they're a real, ordered,
infinite, freely-computable sequence to index into — a fact table, not
a proof step.) That index — call it `γ` from here on, its usual
symbol — is the pencil selector every later section of this paper
reads off of.

```python
>>> for w in ["accretion", "pile", "toroidal",
...           "condensate", "narrative", "dissertation"]:
...     trace(w)
   'accretion'  H=    435952031571538408  next_prime=  7933  idx= 1002  /
                gamma=1439.015472
        'pile'  H=              69256114  next_prime= 49043  idx= 5042  /
                gamma=5548.516421
    'toroidal'  H=      5924746544723326  next_prime= 13513  idx= 1601  /
                gamma=2117.754191
  'condensate'  H=  42756310149759033674  next_prime=  3761  idx=  523  /
                gamma=853.143566
   'narrative'  H=    522068046232455314  next_prime=  1847  idx=  283  /
                gamma=522.366924
'dissertation'  H=391207708623858272995283  next_prime= 46919  idx= 4847  /
                gamma=5365.310518
```
(`notebooks/01_semantic_prime_hashing.ipynb`, cell 3, run live against
the unmodified function.) Determinism holds — the same word produces the
same index on every call, checked against three repeated calls each for
ten words, no exceptions.

### 3.2 The domain, measured on the live vocabulary

Run against all 347,119 words in `VAPMIP/PtolC/monad3_c.bin`, at
109,403 words/second:

```
idx range: [1, 6543]  distinct buckets used: 6543/6542
words per bucket: min 1  max 395  mean 53.1
most-populated buckets: [(3386, 395), (3645, 338), (4523, 310), ...]
```
Live, runnable: `notebooks/01_semantic_prime_hashing.ipynb`, cells 7–8
(the collision-rate and bucket-distribution pass over the live
vocabulary).

Read that second number twice: `6543/6542`. Not a typo — the code's own
count of distinct buckets used *exceeds* the paper's previously-stated
bucket count. Chased rather than rounded away
(`notebooks/01_semantic_prime_hashing.ipynb`, cells 11–12):

```python
>>> print("pi(65536) =", monad._prime_pi_table[65536],
...       " pi(65537) =", monad._prime_pi_table[65537])
pi(65536) = 6542   pi(65537) = 6543
```

`next_prime` is documented, and coded, to reach **65537** inclusive.
65537 is itself prime (it's a Fermat prime, `2^16 + 1`) — so
`π(65537) = π(65536) + 1 = 6543`, one past where the code's own stated
range said it could go. **Verdict: MATHS/METHOD, not CODE.** The function
is internally consistent; it is two *stated* boundaries (`p ∈ [2,65537]`
and `idx ∈ [1,6542]`) disagreeing with each other. This is not a corner
case nobody hits — 91 real words in the live vocabulary land in bucket
6543, most of them ordinary English (`apocope`, `contemplating`,
`discipline`), a few tokenizer noise from the live corpus
(`'kay`, `1387–1422`, raw LaTeX fragments) worth naming honestly rather
than pretending the vocabulary is cleaner than it is. The corrected range
carried forward from here on: **`idx ∈ [1, 6543]`**, not 6542.

### 3.3 A live bug, reproduced, not fixed

`_horner_hash` clamps digits from *below* only (`max(0, ord(ch) - 32)`).
An invisible Unicode character and a printable two-character sequence can
therefore land on the same clamped digit:

```python
>>> zwsp = "​"     # U+200B, ZERO WIDTH SPACE
>>> print(f"horner(U+200B) = {monad._horner_hash(zwsp)}"
...       f"   horner('v!') = {monad._horner_hash('v!')}")
horner(U+200B) = 8171   horner('v!') = 8171
>>> print(f"idx(U+200B) = {monad._word_zero_idx(zwsp)}"
...       f"   idx('v!') = {monad._word_zero_idx('v!')}")
idx(U+200B) = 1026   idx('v!') = 1026
```
Live, runnable: `notebooks/01_semantic_prime_hashing.ipynb`, cell 10.

`VAPMIP/prime_hash.py` (2026-08-18) names what's actually wrong here — a
category error, not an off-by-one: whitespace and invisible control
characters are **aperture** (they set which domain of words is being
drawn from) and were never supposed to reach the letter polynomial as a
digit at all. Its proposed fix, `split_tiers()`, strips anything outside
printable ASCII before hashing, so an invisible character can never forge
a collision. That fix has been designed and is not, as of this writing,
wired into `monad.py` — the bug above is live in the function every later
section of this paper still calls.

### 3.4 The historic foothold — the entrance to the freeway, not a verdict

The idea that a prime could stand for an **irreducible concept** — not
per-language, but underneath every language — predates all of the above.
The clearest statement of it is `Ainulindale/wiki/16_semantic_word_engine.md`:
tree/arbre/木/شجرة/Baum, water/eau/aqua/wasser, all claimed to land on
the same invariant, "the concept is the prime, the language is the
coordinate choice." What's recorded below is not a verdict on that idea —
whether it succeeds or fails was never the point. It's engineering
history: this mechanism, run for real, produced a field of collisions
dense enough that the scripting around it was shelved for months, and
picked back up only after a different object — the box kite, §10's
hyper-relationship snapshot — made it clear *why* the collisions were so
dense. That pivot, not a pass/fail on wiki-16's claim, is what this
section is actually recording.

Run blind, today, against the unmodified mechanism above
(`repo_appendix/semantic_prime_hash/001_original_2026-05-27_word_zero_idx.py`):

```python
=== tree ===
  en  'tree'      idx=2273
  es  'árbol'     idx=111
  zh  '树'        idx=2919
=== water ===
  en  'water'     idx=2009
  fr  'eau'       idx=4122
  ja  '水'        idx=3018
=== water/eau/aqua/wasser (wiki-16's own cited example) ===
  'water'     idx=2009
  'eau'       idx=4122
  'aqua'      idx=4310
  'wasser'    idx=1204
```
(re-run live, this session, against the unmodified function.)

None of the tested groups share an `idx` — including wiki-16's own cited
water/eau/aqua/wasser example. `_word_zero_idx` places every word
*somewhere* (mechanically true by construction — it's a total function),
but a base-95 Horner hash over UTF-8 code points has no reason to be
language-invariant, and isn't. That's not the interesting part, though —
the interesting part, engineering-wise, is the *density* of collision
this style of address produces once you're not just checking a handful
of hand-picked pairs but running it across a real vocabulary: enough
collisions, close enough together, that continuing to script against a
bare address stopped being productive.

The same signal shows up a second time, independently, three months
later, in `wordnet_boxkite.py`'s own in-source history comment: an
earlier version of that file's collision test checked whether a synset
and its hypernym produced *small prime gaps* — which, read back later,
was quietly testing semantic relatedness rather than what was actually
wanted. The author's own note, kept in the file rather than edited away: *"twin
primes were to illustrate the idea of contextual neighborhood... not
semantic neighborhood."* What the retest actually turned up: synsets with
an **exactly identical 19-relation shape** collide on address every
time, regardless of what they mean — `hilbert.n.01` (a mathematician),
`irrawaddy.n.01` (a river), and `new_york.n.03` (a city) share one
address purely because all three have the same named-instance relational
shape.

Both times, the collision density is what mattered, not a verdict on the
mechanism that produced it — it's what shelved the scripting the first
time, and it's what pointed at *relational structure* as the place worth
building on the second. Everything from §9 onward (the pencil, the box
kite, the WordNet relational vector) exists because that density was
followed rather than argued with. That's the sense in which this section
is a foothold, not a result: it's the on-ramp, not the destination — "the
entrance to the freeway" of Teaching the Maths how to speak English.
