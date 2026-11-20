## 7. Reading `monad3_c.bin`'s WordNet relationships

§6 built the store; this section is only the **reading** mechanism —
how a synset's 19 stored relation counts become one address. Nothing
here touches the box kite yet; it's the input the pencil/box-kite
section consumes directly, not developed further here on purpose.

### 7.1 Nineteen relations, one prime each

`VAPMIP/wordnet_boxkite.py`: the 19 relation types this store carries
(`RELATION_METHODS`) each get their own fixed prime line
(`CONTEXT_PRIMES`), starting just above the spelling tier's ceiling:

```python
RELATION_METHODS = ['hypernyms', 'instance_hypernyms', 'hyponyms',
    'instance_hyponyms', 'member_holonyms', 'substance_holonyms',
    'part_holonyms', 'member_meronyms', 'substance_meronyms',
    'part_meronyms', 'attributes', 'entailments', 'causes', 'also_sees',
    'verb_groups', 'similar_tos', 'topic_domains', 'region_domains',
    'usage_domains']                                            # 19
CONTEXT_PRIMES[:19] = [73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
                        127, 131, 137, 139, 149, 151, 157, 163, 167]
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 1.

### 7.2 Nineteen counts → one integer, exact

`context_code(v) = ∏ᵢ CONTEXT_PRIMES[i]^v[i]` — unique factorisation
makes it recoverable exactly, by construction, checked against the live
store rather than trusted on the math alone. Loaded **146,743 words**
carrying a stored 19-vector directly from `monad3_c.bin`:

```
loaded 146,743 words carrying a stored 19-vector, in 0.44s
example: "'hood"  vector=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
         context_code=12191  recovered=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
         match=True
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 3.

`'hood`'s vector has exactly two nonzero slots — `hypernyms` (position 0)
and `usage_domains` (position 18) — and `12191 = 73¹ × 167¹`, the product
of exactly those two primes. Factoring back recovers the same vector,
exactly, on this and (per the paper's own G1 gate) the full store.

### 7.3 One integer → one real — the gamma fold

`context_code` is still a large integer, one per distinct relational
*shape*, not yet the single continuous scalar the rest of this series
carries context as:

```python
log_code     = Σᵢ v[i] · ln(CONTEXT_PRIMES[i])
gamma_radial = tanh(0.5 · ln(log_code / LOG_ANCHOR))
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 5.

`tanh`/`atanh` round-trip `log_code` to machine precision; `log_code`
itself is injective on real vocabulary by the same unique-factorisation
argument as §7.2, one level up. Measured on a 20,000-word sample:

```
sample: 20,000 words
gamma_radial round trip (tanh -> atanh) max rel err: 8.00e-16
distinct log_code values seen: 559
19-vector collisions on a repeated log_code: 0
```

559 distinct values over 20,000 words is expected, not a defect — many
words share an exact relational shape (§7.1's earlier finding, `hilbert`/
`irrawaddy`/`new_york` among them); the fold is checked *within* each
shape, not claimed to separate words that were never distinct in the
first place.

### 7.4 Combined with spelling — one prime per word, both halves recoverable

§5's `spelling_code` uses `LETTER_PRIMES` (`≤ 71`); `context_code` uses
`CONTEXT_PRIMES` (`≥ 73`) — disjoint by construction, checked directly:

```
LETTER_PRIMES max: 71   CONTEXT_PRIMES min: 73
disjoint by construction: True
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 7.

so `full_code = spelling_code(word) × context_code(v)`,
`full_addr = next_prime(full_code)`, `delta = full_addr − full_code`
never has an prime that's ambiguous about which half it came from.
Measured:

```
286/286 exact full round trip (spelling + full 19D context, from ONE prime)
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 9.

One full worked example, end to end:

```
word:            'ubermensch'
context vector:  {'hypernyms': 1}
spelling_code:   249620148694053351635350542193367877/
                 351733454685659309076456677307616437/
                 3387794042547528892750233600000
context_code:    73
full_addr:       182222708546658946693805895801158550/
                 466765421920531295625813374434559999/
                 257308965105969609170767052800179
delta:           179
```
Live, runnable: `notebooks/05_wordnet_19d_contextual_hash.ipynb`, cell 11.

One prime. Both the exact spelling and the full 19-dimensional WordNet
relational signature of the word, recoverable from `(full_addr, delta)`
alone.

### What this section is not

Not the box kite, not the pencil. `gamma_radial`, exactly as folded
here, **is §9's windspeed** — not an input analogous to it, the same
number. §9.1 shows the recovery running the other direction: given only
`(full_addr, delta)` and the word's own spelling, `gamma_radial` comes
back out with no separate WordNet read at all. How that scalar selects
a chart or drives a deformation is §9's job, not this one's — this
section only has to show the fold is exact and reversible, which it is.
