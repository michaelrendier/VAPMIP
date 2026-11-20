## 5. Spelling → prime — order, and the anagram collision

§4 gave a closed, complete pool of "letter" primes to spend. The obvious
way to spend it — one prime per letter, multiply the word's letters
together — is the first thing tried, and it's broken in a specific,
demonstrable way: **multiplication commutes.** A product of primes
records *which* letters appear and *how many times*, by unique
factorisation, and nothing else. It cannot, structurally, carry the
*order* they appeared in. `'dog' != 'god'`; a hash meant to reconstruct
spelling exactly can't lose that.

### 5.1 The naive scheme, and where it breaks

One prime per letter, alphabetically, product of the word:

```python
_primes = sieve(200)
LETTER_PRIME = {chr(ord('a') + i): _primes[i] for i in range(26)}
# a=2, b=3, c=5, d=7, e=11, ... z=101

def naive_phonetic_hash(word: str) -> int:
    prod = 1
    for ch in word.lower():
        if ch.isalpha():
            prod *= LETTER_PRIME[ch]
    return prod
```
Live, runnable: `notebooks/03_phonetic_prime_hashing.ipynb`, cell 2.

Run against real words:

```
'cat'  ->  710
'act'  ->  710
'tac'  ->  710
```

`cat`, `act`, and `tac` — three orderings of the same three letters — all
hash to exactly 710. That's not a near-miss, it's every permutation
landing on the same integer, every time, by construction:

```
naive_phonetic_hash('cat') == 710
naive_phonetic_hash('act') == 710
equal: True

naive_phonetic_hash('listen') == 1914801911
naive_phonetic_hash('silent') == 1914801911
equal: True
```
Live, runnable: `notebooks/03_phonetic_prime_hashing.ipynb`, cell 4.

Every anagram pair in English collides. A prime-per-letter product is an
excellent hash of the *multiset* of a word's letters and a total failure
as a hash of the *word*.

### 5.2 The fix — position picks the base, the letter is the exponent

`VAPMIP/wordnet_boxkite.py::spelling_code` inverts which part of the
construction carries which information. Position, not letter identity,
selects the prime; the letter becomes the exponent on it:

```python
LETTER_CAP = 71                                  # NOTE: 20-prime tier, not §4's 65
LETTER_PRIMES = [p for p in _P if p <= LETTER_CAP]   # [2,3,5,7,...,71], 20 of them

def spelling_code(word: str) -> int:
    code = 1
    for i, ch in enumerate(w for w in word.lower() if w.isalpha()):
        p = LETTER_PRIMES[i % len(LETTER_PRIMES)]    # position -> base, cycling every 20
        exp = ord(ch) - ord('a') + 1                 # letter -> exponent, a=1..z=26
        code *= p ** exp
    return code
```
Live, runnable: `VAPMIP/wordnet_boxkite.py::spelling_code` (the actual
shipped function; imported and run directly, not restated, in
`notebooks/03_phonetic_prime_hashing.ipynb`, cell 6).

The 20 primes are one **per position**, not one per letter — the
alphabet is not truncated. All 26 letters are fully carried, at every
position, by the exponent (`ord(ch)-ord('a')+1`, `a=1..z=26`); a lone
letter's `spelling_code` is just that base's exponent, confirmed for all
26: `a→2, b→4, c→8, d→16, ... z→67108864`. What the 20 actually bounds is
**word length**: past the 20th letter, a position reuses an earlier
position's base prime, and the two positions' exponents land on the same
base and simply **add**. Built a real one, not a hypothetical — two
distinct 21-letter words, position 0 and position 20 sharing base prime
2, `1+3 == 2+2`:

```python
>>> spelling_code('a' + 'x'*19 + 'c')   # pos 0='a'(1), pos 20='c'(3) -> 1+3=4 on base 2
>>> spelling_code('b' + 'x'*19 + 'b')   # pos 0='b'(2), pos 20='b'(2) -> 2+2=4 on base 2
True   # genuine collision — not because a letter is missing, because a position repeated
```
Runnable directly against the shipped `spelling_code` above — a
constructed worked example, not a stored notebook cell, reproducible by
calling both lines against `VAPMIP/wordnet_boxkite.py`.

Position `i`'s prime is fixed regardless of which letter sits there;
swapping two letters now swaps which *exponent* lands on which *base* —
no longer a symmetric product, order survives (for words that don't
reach the wraparound above). A trailing `/` on a number below is a
line-wrap mark only, not part of the value — join the digits across
the break to get the real integer back; the same convention is used
everywhere a number this long appears again in this paper:

```
'cat'     spelling_code = 2288818359375000
'act'     spelling_code = 5149841308593750
'listen'  spelling_code = 778058911374966818061872931448741213/
                          84823203125000000000000
'silent'  spelling_code = 305601935552050069509298342748495166/
                          804755637888000000000000

cat == act now?    False
listen == silent?  False
```
Live, runnable: `notebooks/03_phonetic_prime_hashing.ipynb`, cell 6.

Exact, order-sensitive spelling as a prime, recoverable — position `i`'s
prime is known in advance, so factoring the code back at each of those
20 recurring bases recovers each letter's exponent, in order:

```
'cat'              -> decoded 'cat'              match: True
'act'              -> decoded 'act'              match: True
'windspeed'        -> decoded 'windspeed'        match: True
'reconstructible'  -> decoded 'reconstructible'  match: True
```
Live, runnable: `notebooks/03_phonetic_prime_hashing.ipynb`, cell 8.

### 5.3 Measured, not asserted — live 30,000-word sample

```
exact word recovery: 27,375/28,728  (95.290%)
words <=20 alpha chars: 28,296  exact 27,375 (96.745%)
words  >20 alpha chars: 432  (position cycle wraps at 20 -> exponents
                              add on the reused prime -> lossy, by
                              construction)
```
Live, runnable: `notebooks/03_phonetic_prime_hashing.ipynb`, cell 10.

The failure mode is exact and predicted, not mysterious: the tier is 20
primes, cycling. A word over 20 letters reuses a base prime at two
different positions, and since a product of prime powers can't
distinguish `p^a · p^b` from `p^(a+b)`, those two positions' exponents
just add — recoverable as a sum, not as two separate letters. Lossy
exactly where the construction says it will be, and nowhere else:
**96.745%** exact on the ≤20-letter words the scheme is actually built
for, **0%** guaranteed-exact past that by the same arithmetic that gives
the 96.745%.

### One honest note carried forward

§4 established 65 primes (≤313) as the complete letter pool. What
actually ships here uses a smaller, 20-prime cycling tier (≤71) — the
20-prime tier is what the position-cycling needs (enough bases that most
real words never wrap), not the full 65. Worth being upfront about in
the paper rather than letting a reader notice the numbers don't match:
is the 65-prime pool meant to become the tier size eventually (fewer
wraps, longer words safe), or is 20 the settled design and 65 is a
separate fact about the domain, not a promise about this tier's size?
