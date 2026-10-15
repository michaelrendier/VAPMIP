# Lyndon Factorisation — the word-primes, and the conjugation/tense slot

*Written 2026-10-14 (Claude Sonnet 5.5, for Cody). Stub: `VAPMIP/lyndon_conjugation.py`. Nothing imports it yet.*

Cody, 2026-10-14: the Lyndon factorisation "gets a wiki page... and is to be woven into the equation... this will be the part of the
mechanism that handles conjugations and tenses". This page records what the factorisation is, what the stub does and does not do,
and where it was seen. It does not design the mechanism.

## What it is

A **Lyndon word** is a non-empty word strictly smaller (lexicographically) than every one of its proper rotations. The **Chen–Fox–Lyndon
theorem**: every word factors uniquely as a concatenation of Lyndon words in non-increasing order, `w = l₁ l₂ … l_k`, `l₁ ≥ l₂ ≥ … ≥ l_k`.
That is the word-level fundamental theorem of arithmetic: Lyndon words are the primes, the factor count k plays the part of Ω(n),
and the primitive root `w = uᵏ` plays the part of a prime power. Duval's algorithm finds the factorisation in one linear pass without
backtracking. The GenerationalLineage toolset `engine/toolsets/lyndon.py` is the same object (`descend` free).

| integers | words |
|---|---|
| prime | Lyndon word |
| n = p₁ ≥ p₂ ≥ … ≥ p_k | w = l₁ ≥ l₂ ≥ … ≥ l_k |
| Ω(n) = k | number of Lyndon factors |
| gcd/lcm by exponents | primitive root and exponent |

The number of Lyndon words of length n over k letters is (1/n)Σ μ(d)·k^(n/d); the necklaces (rotation classes) number (1/n)Σ φ(d)·k^(n/d).

## What the stub contains

`verify()` checks the theorem exhaustively on every word of length ≤ 10 over {a, b} (2,046 words): factors concatenate to the word,
each is Lyndon, they are non-increasing, and the Lyndon counts per length (2, 1, 2, 3, 6, 9, 18, 30, 56, 99) equal the formula.
Failures: 0. Examples: `banana → b|an|an|a`; `abracadabra → abracad|abr|a`; over word tokens, `the cat sat on the mat → the | cat sat on the mat`.

`conjugates()` and `inflection_frame()` are **stubs** and raise `NotImplementedError`. They mark where the conjugation and tense mechanism
attaches; they contain no design.

**A naming point to settle in the design.** In combinatorics on words, two words are *conjugate* when one is a rotation of the other
(uv ~ vu): the necklace class. Whether that is the same thing as grammatical conjugation (verb forms) is not assumed here. The
helper `necklace_class()` is the combinatorial sense only.

## Where it was seen

In `FourthAgePapers/CollatzShift` a count of Lyndon factors in Collatz parity streams looked unusual and was traced to the way the
streams begin and end: a leading symbol changes the factor count (for random bits, a stream's first bit being 1 versus 0 shifts
the mean number of factors), which is a sentence-initial boundary effect. Matched controls remove it (z ≈ 0). It is recorded in that paper as a
fault in our control matching, not as a finding. The point for this page: a word's factor count is sensitive to its first and last symbols,
so any use of Lyndon factors on sentences has to say how boundaries are treated.

## Open (not designed)

- how Lyndon factors of a token stream relate to the project's word-primes and sentence constructor;
- the order on tokens that the factorisation uses (it is the order that makes a word "smaller than its rotations");
- what a "tense" is as a transformation of the factor list;
- how this is woven into the equation (the L_(I|O) path, the harness, or neither).
