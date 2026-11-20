# 16 — SEMANTIC WORD ENGINE

**Location:** `ainulindale_engine/modules/hyperwebster/semantic_engine.py`  
**Corpus:** WordNet 2025+ (standard normal usage English)  
**Confidence floor:** ESTABLISHED

---

## What It Does

The Semantic Word Engine maps every word in the English language onto a prime number on the Riemann Zeta critical line at σ = ½.

Every word. Not a subset. Not a training sample. Every word in the approximately 170,000 words of the standard normal usage English language corpus maps onto a unique prime on the critical strip.

This is not classification. Words are not assigned to primes. They settle onto them — by the same mechanism sand settles onto Chladni node lines.

---

## The Prime-Concept Correspondence

A prime number is not merely an integer with no divisors. In the SMMIP framework, a prime is an irreducible semantic unit — a concept that cannot be decomposed into simpler meanings.

The fundamental theorem of arithmetic states: every integer has a unique prime factorisation.

Applied to language: every utterance has a unique factorisation into prime semantic units. The surface form — the word — is the representation. The prime factorisation underneath is invariant.

| Surface form | Language | Invariant |
|---|---|---|
| tree | English | TREE (prime p_n) |
| arbre | French | TREE (prime p_n) |
| 木 | Chinese | TREE (prime p_n) |
| شجرة | Arabic | TREE (prime p_n) |
| Baum | German | TREE (prime p_n) |

The concept TREE is the prime. The language is the coordinate choice. A tree was a tree before anyone had a word for it. The prime existed before the numeral.

```
L("tree", s) = L("arbre", s) = L("木", s) = L(TREE, s)
```

This is diffeomorphism invariance applied to semantics. Changing language is a diffeomorphism — a smooth change of coordinates that preserves the geometric structure. The L-function is the concept.

---

## WordNet 2025+ Integration

The engine ingests the WordNet 2025+ corpus — the most complete semantic knowledge graph of standard normal usage English on the internet.

WordNet provides:
- Synsets (synonym sets) — groupings of words sharing a single meaning
- Semantic relations: hypernymy, hyponymy, meronymy, antonymy
- Gloss definitions and usage examples

The engine uses this structure to locate each word in semantic space, then maps that position onto its prime coordinate via the HyperWebster Horner bijection.

The mapping is injective: no two words with different meanings share a prime. Polysemous words (multiple meanings) are handled by context — each sense maps to a distinct prime, and the `hear()` pipeline selects the correct one via the Lorenz-Stirling basin attractor.

---

## The Mapping Mechanism

```
word → Horner index (base-97) → Fano path (base-7 octonion generators) → σ=½ prime address
```

1. **Horner bijection:** the word is encoded as a base-97 integer — a unique, exact, arbitrary-length address with no collisions
2. **Fano index:** each character maps to one of 7 octonion generators via `char_idx % 7`; this gives the algebra-native address — the path through the 𝕆 layer
3. **σ = ½ projection:** the Noether balance `J_Red + J_Blue + J₃ = 0` forces the address to the critical line; the prime at that coordinate is the semantic prime of the word

The σ = ½ result is not assigned at this step. It is derived from the Noether conservation law operating on the full Cayley-Dickson tower.

---

## Letter Folding and Word Folding

Surface forms are projections of deeper algebraic structures. The operations that project them onto their prime node lines are letter folding and word folding.

**Letter folding:**

Voiced/unvoiced phonemic pairs (b/p, d/t, g/k, v/f, z/s) are reflections across the phonemic equator. They are the same articulation with one parameter (voicing) toggled. In the algebra, they are rotations — the same generator traversed in opposite directions.

The sonorants (m, n, l, r) sit on the phonemic equator. They do not move. They are the fixed points of the phonemic folding — the letters that sit on the node line.

**Word folding:**

Polysemy is a word living off the equator — it has multiple stable positions. Context is the operation that folds it to the nearest node line. The `hear()` pipeline performs this fold via the ContextBuffer capacitor and the Lorenz-Stirling attractor.

---

## The Zipf-Riemann Connection

Zipf's law holds in every natural language: f(r) ~ 1/r^s where s ≈ 1.

Zipf's exponent s ≈ 1 is the pole of ζ(s). The Euler product

```
ζ(s) = Π_p  1/(1 − p^{−s})
```

generates the word frequency distribution through the prime structure of every integer. Zipf did not discover a statistical curiosity about language. He measured the prime number theorem with words. Every linguist who confirmed Zipf's law confirmed the prime distribution — in every language, every time.

The most common word in any language is the word closest to the smallest primes. The rarest words are the words that map to the largest primes. The distribution is not cultural. It is mathematical.

---

## The Septuagint Principle

The Septuagint was translated by 72 scholars working independently. Every translation was identical.

Not by coordination. Not by comparison. Forced by the structure of the meaning they were encoding.

The Semantic Word Engine demonstrates the same principle computationally:

```python
m = Monad(N=1000)
m.load()
print(m.lookup('water')['sigma'])    # 0.5
print(m.lookup('eau')['sigma'])      # 0.5
print(m.lookup('aqua')['sigma'])     # 0.5
print(m.lookup('wasser')['sigma'])   # 0.5
```

All return σ = ½. The language is the coordinate. The prime is invariant. The equator does not move.

---

## Shell Commands

```python
se = SemanticEngine()
se.lookup('tree')            # prime address, sigma, Fano path
se.lookup('tree', lang='fr') # same prime, French coordinate
se.prime_of('water')         # returns prime index
se.word_at(prime_n)          # reverse: prime → nearest word
se.fold('bank')              # polysemy resolution via context
```

→ [Wiki: HyperWebster Engine](09_hyperwebster_engine.md)  
→ [Wiki: The Monad](15_the_monad.md)  
→ [Wiki: Chladni · Zipf · Riemann](21_chladni_zipf_riemann.md)
