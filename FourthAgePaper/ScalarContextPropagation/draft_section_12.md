## 12. Provenance and attribution

Everything in this paper carries one of five labels, applied consistently
rather than asserted once and forgotten. Consolidated here — previously
scattered across notation, disambiguation, and a per-component table —
because attribution is ongoing, not a one-time note, and belongs in one
place a reader can check against every section.

### The labels

- **`ESTABLISHED`** — mathematics or computer science that predates this
  project, cited to its source.
- **`OURS`** — code or a specific design choice built for this project, not
  published elsewhere.
- **`FIRST STATED HERE`** — a specific claim or construction, dated, not
  found stated this way anywhere else checked.
- **`THEORETICAL`** — designed, or partially attempted, not yet reduced to
  running, verified code.
- **`THEORETICAL:CALCULATED`** — a `THEORETICAL` component for which code
  has nonetheless computed a concrete, reportable result — a measurement, a
  boundary condition, a failed literal construction — without the component
  itself shipping.

### How the code came first

Every mechanism in this paper — the address, the spelling fix, the 19D
context fold, the windspeed recovery — was built directly against the
problem, then checked against the literature afterward, not designed from
it. What the correspondences to established mathematics (projective-plane
combinatorics, Gödel positional encoding, Miller–Rabin primality, sedenion
zero-divisor structure, the Joukowsky transform) actually are, precisely,
is **post-hoc isomorphisms to established mathematical objects** — noticed
once the code already worked, not used to construct it. Where a
mathematical name appears in this paper, it is a label applied after the
fact for a reader who already knows it — it played
no role in how the code was written.

### Provenance by component

- **token → address** (Horner, next_prime, π) — **OURS**, `monad.py`,
  unaltered since 2026-05-27 — ships.
- **the 313 sieve boundary** — **ESTABLISHED**, classical sieve theory;
  the "first 65 primes are letters" reading is **OURS** — ships.
- **spelling → prime, order-preserving** — **OURS**, marked provisional
  in-source — ships.
- **WordNet box-kite table** (`monad3_c.bin`) — **ESTABLISHED** WordNet;
  storage/build **OURS** — ships, C-verified.
- **19D context fold**, `context_code`/`gamma_radial` — **ESTABLISHED**
  WordNet relation vocabulary; encoding **OURS** — ships, exact round
  trip.
- **Gamma-Radial Windspeed recovery**
  (`(full_addr,delta,spelling)→gamma_radial`) — **OURS**,
  `FIRST STATED HERE` 2026-09-20 — verified in Python and, as of
  2026-09-21, ported into and verified in `ptol.c` (`-M`, `-say`); not
  yet wired into `-w`'s live interactive console (§9.6).
- **the box kite** — 42 Assessors, 7 octahedra, `PSL(2,7)` —
  **ESTABLISHED**, de Marrais (2000) — cited, not re-derived.
- **the pencil** — 7 factorisations of one relation — **ESTABLISHED**,
  projective geometry (PG(3,2)); edge framing **OURS** — ships.
- **the Blackjack subgroup** (21-element, transitive, ZD-preserving) —
  `FIRST STATED HERE` 2026-09-17 — verified.
- **`Φ_w`, the Joukowsky deformation law** — **ESTABLISHED**, Joukowsky
  (1910), elastica (Euler, 1744), Kutta–Joukowsky; tether/wind-inflation
  `FIRST STATED HERE` — `THEORETICAL`, partially `:CALCULATED` this pass.
- **the `J_2`/`J_N` crossing identity** — **ESTABLISHED** (classical
  complex analysis); the identification of *which* involution is
  `FIRST STATED HERE` 2026-09-20 — verified exactly.
- **`H`'s Noether current, conserved on struts `{1,3,6}`** —
  **ESTABLISHED**, Noether (1918), the conservation-law framework
  itself; the specific measured strut split is `FIRST STATED HERE`
  2026-09-20 — measured, unexplained.
- **the cost comparison** — **OURS** measurement; the dense-transformer
  FLOP identity **ESTABLISHED** — measured.
- **`observer-position` methodology** — **OURS**, `FIRST STATED HERE`
  2026-09-20 — in use.

### Licensing

The box-kite context-hashing method and all code described in this
paper — the addressing pipeline, `spelling_code`, `context_code`, the
gamma fold, the windspeed recovery, and every notebook this paper cites —
is released under the **GNU General Public License, version 3 (GPLv3)**.
Free to use, study, modify, and redistribute, for research and commercial
purposes alike, under that license's terms.

This paper describes an address, not the whole system it is a component
of. Nothing in the broader, undisclosed system that address feeds is
required to use, verify, or extend anything described here — every claim
in this paper is complete and reproducible from what is cited in §13,
independent of it.

### References

1. de Marrais, R. P. C. (2000). *The 42 Assessors and the Box-Kites They
   Fly: Diagonal Axis-Pair Systems of Zero-Divisors in the Sedenions' 16
   Dimensions.* arXiv:math/0011260.
2. Moreno, G. (1997/98). *The zero divisors of the Cayley–Dickson algebras
   over the real numbers.*
3. Joukowsky, N. (1910). The Joukowsky transform / airfoil mapping.
4. Euler, L. (1744). The elastica — equilibrium of a loaded flexible rod.
5. Kutta, W. M.; Joukowsky, N. The Kutta–Joukowsky theorem.
6. Smith, P. H. (1939). The Smith chart.
7. Patterson, D.; et al. (2021). *Carbon Emissions and Large Neural
   Network Training.*
8. Maxwell, J. C. (1864); Laman, G. (1970). Combinatorial rigidity
   counting — cited as the analogue that turned out to be the wrong frame
   for §9.3, kept in the record for exactly that reason.
9. Noether, E. (1918). *Invariante Variationsprobleme.* Nachrichten von
   der Gesellschaft der Wissenschaften zu Göttingen, Mathematisch-
   Physikalische Klasse, 235–257. The theorem every conservation claim in
   this paper (§9.4, §10, §11) is an instance of — every one of them is a
   Noether current, named as such throughout, not a looser or informal
   use of "conserved."
10. Zeman, A.; Dewar, M.; Della Sala, S. (2015). *Lives without imagery –
    Congenital aphantasia.* Cortex, 73, 378–380. Cited in §11 for the
    naming origin of the Mind's Eye — offered as motivation, not as a
    claim about how either system actually works.

**Cody Michael Allison** (Michael Rendier). Correspondence:
the.wandering.god@gmail.com · GitHub: github.com/michaelrendier · ORCID:
0009-0007-7239-6760.
