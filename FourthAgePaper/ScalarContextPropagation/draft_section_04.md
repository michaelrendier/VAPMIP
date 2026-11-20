## 4. Why primes at all — how we came to 313

### 4.1 The Two Trees Engine

Two names recur through this section: **Laurelin** and **Telperion**.
They are not this paper's invention — they name a general-purpose
component (`GenerationalLineage`'s Two Trees engine, defined plainly in
§2.5) already used elsewhere in this project to split a domain of primes
into two disjoint sub-domains and track what crosses between them.
Nothing in this section depends on that engine's wider scope; the two
names are used here purely as fixed labels for the two domains §4.4
derives, so that later sections (and this paper's own code) have one
word each instead of a clause.

Live, runnable: this paper's own
`notebooks/02_the_313_sieve_and_49999_unsieve.ipynb` demonstrates the
engine directly, cell by cell (§4.4–§4.5 below). The engine's own home
notebook, built under this project's Full Engine Protocol (one numbered
notebook per engine, `VAPMIP/notebooks/`), is
`VAPMIP/notebooks/16_e10_generational_lineage.ipynb` — it documents the
Two Trees engine at a depth this paper doesn't need and isn't developed
here; named only as a pointer.

Worth stating plainly why Tolkien's vocabulary is used for this at all,
rather than left as unexplained flavour: the author's own reason is that
Tolkien's Ainulindalë — the creation account in his legendarium — reads
as a language-structural-constant calibration check, told the same way
regardless of which of Tolkien's own constructed languages is telling
it. That property — one invariant, checkable for reading the same across
otherwise-independent representations — is the actual design principle
behind a real structural constant the author engineered elsewhere in
this project, out of scope here and not developed further in this
paper. The names are kept because that analogy is load-bearing to that
other design, not for atmosphere.

### 4.2 Laurelin — the factors domain

A prime is, by the classical sieve reading, exactly what survives
elimination: strike every multiple of 2, then of 3, then of 5, and so
on — what remains unstruck at the end is prime, defined entirely by the
factors it does *not* have. That is the extinction reading of
factorisation, older than any of the machinery in this paper. Reported
plainly, without claiming it resolves anything open: **Fermat's
framing defines the primes by the extinction of every possible factor;
the Riemann zeta function, by contrast, only describes the primes'
*order of arrival*** — the density and spacing of a set already fixed by
that extinction test, not what makes any one of its members prime.
Nothing here leans on the truth or falsity of any unproven conjecture
about that order; the distinction is between what *defines* the set and
what *describes* its distribution, and both readings are standard.

**Laurelin** is assigned this section's *factors* domain — see §4.5:
the primes above 313 that this paper's own sieve run shows never once
serve as anything but a factor of something larger. They exist in the
dataset only in that role.

### 4.3 Telperion — the Riemann prime-zeta-zero tree

**Telperion** is assigned this section's other domain — the primes at
or below 313 — for a reason specific to this paper, not a restatement of
how the name is used elsewhere in the project: every one of those primes
is exactly a *letter*, and §3 already showed what a letter is for —
`Horner → next_prime → π(p) → γ`, a walk that ends on one specific
non-trivial Riemann zeta zero. Telperion's domain, in this paper, is the
alphabet whose addresses *are* Riemann zeros. That is what "Riemann
prime-zeta-zero tree" means here, concretely, not evocatively.

That is this paper's own, local, narrow reading of the name — worth
distinguishing clearly from the fuller object Telperion names elsewhere
in this project, so a reader who goes looking finds a consistent
picture rather than a collision. Stated once, plainly, without
developing it further here: elsewhere, **Telperion is the Prime Number
Tree** — the Cayley–Dickson tower read top to bottom, with the primes as
the leaves that survive every level intact and the composites as the
ones that fall. Its spectral nodes are **the Riemann zeros**, read as a
**Zeta Zero Lattice** — a genuine lattice (an ordered, countable,
indexable structure) built from a sequence of numbers that are each
individually continuous-valued, not integers; the "lattice" is in how
the sequence is used and indexed, not a claim that the zeros themselves
are discrete. That object is a conjugate pair with Laurelin, the same
partition this paper's own §4.2/§4.5 draws locally, just at the scale of
the whole Cayley–Dickson tower rather than one sieve boundary. It is
built and run as its own engine in `ValaQuenta/zero_lattice.py`
(`ZLNode`; the same file computes both the tree and the 42-class
zero-divisor lattice, §9's box kite among them) and fleshed out far more
fully in a dedicated repository,
[`AbrikosovTree`](https://github.com/michaelrendier/AbrikosovTree) — the
Riemann zeros there are identified with an Abrikosov vortex lattice (the
2003 Nobel-winning superconductor structure), the primes with the
un-extinctable condensate they pin. Worth naming honestly rather than
quietly resolved: testing elsewhere in this project has suggested — not
re-verified in this paper, not developed here — that the zero-divisor
lattice this paper's own §9 later uses may actually *contain* this same
Telperion as a substructure, which would make "different object, no
overlap" too strong a claim; that relationship is a real, open thread
for the Catalog (§11), not settled either way here. This paper's own
Telperion — the ≤313 letter alphabet — is the one narrow, local slice of
all of that this section actually needs.

### 4.4 The boundary itself

The question, asked plainly, before any of the rest of this paper
existed: **what is the last prime number to see any new factors come
down in the sieve?** — equivalently, the highest prime factor ever
required to build any composite in the domain at all. Not offhand maths;
a dataset of two conjugate domains over the composites (the Two Trees
engine — primes, composites), built and checked directly:

```python
# GenerationalLineage/engine/lineage.py::un_sieve, run for N=10^5
import lineage
r = lineage.un_sieve(100_000)
```
Live, runnable: `notebooks/02_the_313_sieve_and_49999_unsieve.ipynb`,
cell 1.

The standard optimised sieve only needs to strike multiples of `p`
starting at `p²` — every smaller multiple of `p` was already struck by a
smaller prime factor. So `p` contributes a **new** strike only while
`p² ≤ N`. Direct code, not looked up:

```python
>>> primes = sieve_primes(100_000)
>>> max(p for p in primes if p * p <= 100_000)
313
```
Live, runnable: `notebooks/02_the_313_sieve_and_49999_unsieve.ipynb`,
cell 3.

313 is the answer: the last prime with anything new to strike at
`N = 10⁵`.

### 4.5 Composite primes — the closed alphabet

What that boundary actually splits the primes into, checked directly
rather than reasoned about in prose (`_spf_gpf_tables(100_000)`, every
composite `≤ 10⁵`, no sampling):

```python
>>> spf, gpf, primes = _spf_gpf_tables(100_000)
>>> comps = [n for n in range(4, 100_001) if spf[n] != n]
>>> max(spf[n] for n in comps)
313
>>> len({spf[n] for n in comps})            # every one of the 65 gets used
65
>>> never_spf = {p for p in {gpf[n] for n in comps} if p not in {spf[n] for n in comps}}
>>> len(never_spf), min(never_spf), max(never_spf), all(p > 313 for p in never_spf)
(5068, 317, 49999, True)
```
Live, runnable: `notebooks/02_the_313_sieve_and_49999_unsieve.ipynb`,
cell 7.

**Composite primes** — Telperion's, ≤313, 65 of them — are the complete,
closed alphabet of every composite's smallest-factor identity: no
composite in the whole domain ever has an `spf` outside this set, and
every one of the 65 gets used. **Factoral primes** — Laurelin's, 317
through 49999, 5,068 of them — are exactly the primes that *never* once
serve as an `spf` for anything: Telperion is permanently blind to them,
zero exceptions, not approximately; they only ever surface as a `gpf`,
which is to say only Laurelin ever accounts for them at all. The split
isn't a rule of thumb, it's exact: `max(spf) == 313`, always, for every
composite ≤ N, because `spf(n) ≤ √n ≤ √N` is arithmetic, not policy.

That single number is what turned an open question — are the primes
*words*, or are they *letters* — into a decision. **The first 65
primes are letters.** With a bounded, principled pool to draw from
(not an arbitrary round number, the sieve's own extinction boundary),
spelling can be hashed into primes in an orderly way, mostly collision-
independent rather than colliding by accident — which is exactly where
§5 picks up.

Reported for completeness, not developed further, but defined properly
rather than waved at: **the sieve run forward, extinction-first, is not
the same process as its construction-side counterpart, recursive
sieving** — not "the sieve undone in reverse order," a real, separate
pathway. Recursive sieving starts from the true ground state, *just the
primes, nothing built yet*, and turns primes on one at a time in
ascending order; a composite is **born** — enters the construction — the
moment its *largest* needed prime factor is switched on, not its
smallest, because every one of its factors has to be available before it
can exist as their product, and the biggest one is necessarily the last
to arrive. That boundary — when the last composite finishes being born —
doesn't resolve until 49999, not 313: a genuinely different, much larger
number, because birth-order and death-order are not mirror images of the
same statistics. Measured directly, not assumed: the birth-order
histogram carries roughly four times the entropy of the death-order one
(`+7.19` bits, engine
`GenerationalLineage/engine/lineage.py::un_sieve`) — extinguishing a
composite is cheap (its smallest factor alone convicts it), constructing
one is expensive (every factor has to show up), and that cost asymmetry
is a real, intrinsic fact about the domain, not an artefact of which
direction the sieve is read in. Left here as one honest, properly
defined line for whichever number theorist or physicist wants to run
with it, not part of this paper's own argument.
