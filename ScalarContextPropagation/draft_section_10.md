## 10. Conclusion — what the scalar actually does, proven and open

### The claim this paper set out to prove

**Proven, exactly, on live data:** a word's full 19-dimensional WordNet
relational signature is recoverable from one prime address and its literal
spelling, with no separate WordNet lookup. `context_vector`→`context_code`
factors back exact on the full 146,743-word store (§7.2). The combined
`(spelling, context)` address round-trips exact, 286/286, on a live sample
(§7.4). And read the other direction — the one this paper is actually
about — **the Gamma-Radial Windspeed (`gamma_radial`) recovers out of
`(full_addr, delta)` and the word's own text alone**, dividing out the spelling component
computed fresh from the letters, with no context stored anywhere except in
that one scalar (§9.1). That is the proof of concept: the single scalar
number *does* recreate the exact structure that leads to the 19D context
relationships, starting from nothing but the literal spelling of the word.
Nothing about this claim is aspirational — it is measured, exact, and
reproducible from the notebooks cited throughout.

### What is genuinely working

- The address itself (§3–§5): deterministic, four months unmodified,
  measured live at 347,119 words.
- The domain it's built on (§4): 313 as the sieve's own extinction
  boundary — not a round number, a fact about `p²≤N` — grounding "the first
  65 primes are letters."
- The spelling fix (§5): order-sensitive, exact for the ≤20-letter words the
  tier is built for, and the failure past that is the *predicted* arithmetic
  wraparound, not a mystery.
- `monad3_c.bin` (§6): the real WordNet box-kite table, built and
  cross-checked C-vs-Python exact, and confirmed live in `ptol.c` today via
  `-M`'s byte-exact struct read — not a paper design, a running binary.
- The context read and its scalar fold (§7): exact, both directions.
- The windspeed recovery (§9.1): exact, and — corrected twice in the
  process, both corrections kept in the record — genuinely continuous once
  represented in this project's own native coordinates rather than a
  Cartesian or basis-vector-quantized stand-in.
- A real, non-trivial Noether current (§9.4): `H` exactly conserved,
  in Emmy Noether's own precise sense — a continuous symmetry of the
  motion holding the quantity fixed — along one specific, non-arbitrary
  path through the pencil, on 3 of 7 struts.
- The cost claim (§8): measured, `10⁴`–`10⁶`× cheaper per query, structural
  not optimisation.

### What needs work — named honestly, not hidden

- **`Φ_w`, the full deformation law**, is still open. What §9 adds is real
  progress — the object is continuous, not discrete, and a Noether current
  holds on a real subset of struts under a specific ordering — but the
  complete map from `(H, w)` to all six Assessor coordinates, for every
  strut, is not built.
- **Why struts `{1,3,6}` carry that Noether current and `{2,4,5,7}` don't**
  is unresolved. Checked and ruled out the obvious candidate (a Fano-plane
  line); the real
  answer likely lives in the pencil's own `(a,b)` pairing structure, not the
  index set, and needs a properly-targeted test this pass didn't finish.
- **The author's own sail-pressure-to-strut-angle mechanics** — deformable sails
  fixing two struts' relative position at the crossing — remains unbuilt.
  Everything in §9.3–§9.4 is a spectral/algebraic proxy for that geometry,
  not the geometry itself.
- **The C port — done, one piece short.** The Gamma-Radial Windspeed
  recovery is now ported into `ptol.c` (`monad3_gamma_radial()`,
  2026-09-21), checked against this paper's own recorded value first
  (`windspeed("tree") = -0.151155`, both languages, to 6 decimal
  places), and live via `-M`/`-say` — both real, scriptable, offline
  entry points. What's still open is narrower than "the port": wiring
  that same computation into `-w`'s live interactive console
  (`mh_send_chat`'s wire protocol to the curses UI) — computed today,
  not yet transmitted, left for its own tested pass rather than
  extended in the same sitting as the port itself (§9.6).
- **The Scale engine's contextual flow**, and the sentence-construction
  windspeed (the **A-Matrix Basin Windspeed**) this paper deliberately
  excluded, are both real, both wanted, and both separate, later
  engineering — not gaps in this paper's own claim, but named here so the
  boundary is visible. See §11.

### The honest shape of it

This paper proves the *address* half of its own claim completely: context
propagates forward, exactly, from one scalar and a spelling, with nothing
stored in between. It proves a *real, structured* opening piece of the
*geometry* half — continuous where earlier passes found (wrongly) discrete,
carrying a genuine Noether current on a subset of the structure — without
proving the whole geometry. That is a true, checkable, and useful place to
stop a first paper.
