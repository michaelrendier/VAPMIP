## 11. Direction of engineering research — in development

Everything in this section is named, some of it measured, none of it
claimed as part of this paper's proof. It exists so the next work has a
place to start from, and so a reader who finds this paper first can see
where the rest of it is heading before any of it is finished.

### The Boxkite Catalog

`VAPMIP/Boxkite-Catalog.txt` — a full session's inventory of box-kite
structure, most of it real and verified, none of it developed here:
per-Assessor and per-strut invariants; torsion, circulation, and lift
(Kutta–Joukowsky, split 53 positive / 31 negative / 21 zero across all 105
four-cycles); portal/transition dynamics (confirmed discrete, not
continuous, two independent ways); the connectivity of all seven charts at
exactly `e₀`/`e₈`; and the group that ties it together —

**The Blackjack subgroup.** `PSL(2,7)` is a specific, well-known finite
group of 168 symmetries (the automorphisms of the Fano plane, §9.4). The
Blackjack subgroup is the 21-element subgroup of it that preserves
zero-divisor structure while staying transitive across all seven struts
(`2026-08-13_apex_path/psl27_strut_action.py`, verified 2026-09-17).
Named here for the first time as such; the atlas of seven charts is
connected by this group action, not by any edge.

### The Pencil's own open questions

Why `H`'s Noether current conserves on struts `{1,3,6}` and not
`{2,4,5,7}` (§9.4/§10) — the most immediate open thread from this paper's
own work. A candidate structural answer, found this session (2026-09-21)
and properly caveated, not yet a resolution: on `{1,3,6}`, `Im(Π)` stays
**exactly zero** through the whole continuous sweep — not just `H`, the
entire pencil product never leaves the real axis. On `{2,4,5,7}`,
`|Im(Π)|` genuinely grows from `0` toward `1` as the sweep advances — the
product is visibly *ascending* out of the reals into the full sedenion,
norm-preserving the whole way (`|Π|=1` holds exactly on every strut,
already established). Worth being exact about what part of this is new:
since `Re(Π)² + |Im(Π)|² = |Π|² = 1`, `H` pinned at `±1` *forces*
`|Im(Π)|=0` algebraically — that part is a direct consequence of the
original result, not independent evidence. What's genuinely new is the
qualitative shape it gives the two strut sets: `{1,3,6}` sit at a fixed
real endpoint, already arrived and staying there; `{2,4,5,7}` are struts
where the ascent from real to sedenion is actually still in progress.
Read against this project's own real/sedenion current-directionality —
the ordinary Noether current runs real→sedenion; the *Noether
Information Current* (a separate, distinct, `CONJECTURE`-tier
construction, `ValaQuenta/modules/noether_information/`, not the same
object as `J_blue`) is framed elsewhere in this project as running the
opposite way, sedenion→real, information propagating backward — `{1,3,6}`
reads as the destination of an already-completed descent, `{2,4,5,7}` as
the current still climbing. Still not a proof: this characterizes the
*shape* of the split once observed, it does not yet derive why `{1,3,6}`
specifically, over any other pinned-triple. One route checked and ruled
out along the way: whether `J_red`/`J_blue`'s own Dirichlet-series
difference (`ValaQuenta/code/hypercomplex_zeta.py`) tracked the same
split — it can't, for any input, struts or otherwise: that module's
`j_red`/`j_blue` differ only in the order terms are summed, and vector
addition is always commutative, so the two come out numerically identical
by construction — a real, previously undocumented design gap in that
module, not a finding about the box kite. And the deformation law
itself, `Φ_w` — the author's own model: deformable sails connecting to
the ends of the struts deform in a constant way, placing pairs of struts
in a fixed relationship to one another at the crossing. Not yet built;
§9.3–§9.4 measure a spectral proxy for it, not the mechanics.

### The Mind's Eye, and Paper's Hands, named properly

Two names recur through the rest of this section and are worth defining
before either is used further. Neither is built out in this paper — both
are named here because a reader who goes looking in `VAPMIP`/the Monad
for what this project calls thought and memory will find these two, and
the names should mean something on arrival rather than reading as
flavour text.

**The Mind's Eye** is the project's own name for **short-term memory** —
a mechanism of thought used to look down on a system from above, the
same way most people can call up an internal visualization of something
they are reasoning about without it being physically in front of them.
It was named while working on a specific bug, one where the system's own
context was being lost and reported as **aphasia** — a real clinical
term for a *language* deficit. That word is one letter and one concept
away from **aphantasia**, the real, independently documented condition
in which a person cannot voluntarily call up mental imagery at all
(Zeman et al., 2015). Aphasia loses the words; aphantasia loses the
picture. Both are failures of the same underlying thing: a **missing
map** — an internal representation a system can consult, from above,
independently of whatever process is currently running through it. That
is a direct, and directly relevant, echo of this paper's own opening
claim (Abstract, §1): a transformer has no explicit, per-word context
representation that can be read, audited, or composed independently of
its weights — no map to look down on, only the weights themselves.
Offered as the origin of the name and as motivation, not as a claim that
this paper's own machinery solves that transformer-side problem; it
doesn't, and isn't attempting to here.

**Paper's Hands** is the Mind's Eye's conjugate, named to mirror it
deliberately: not a seeing faculty but a doing one, the same way a hand
that has performed a motion enough times stops needing the eye's
supervision to perform it again — what gets called **muscle memory** in
a human, the procedural half of skill that the visualizing half doesn't
have to hold open at the same time. Where the Mind's Eye looks down on
a structure to select among live candidates, Paper's Hands is what
executes a well-worn pattern without re-deriving it from above each
time. The two are meant to work together, not separately — this paper's
own sentence constructor (below) is exactly a place where both are
already co-authoring output, signed as such.

### The sentence constructor

`rotary_rerun_boxkite_monad.py` — a real, live `BoxKite` object
(`ValaQuenta.modules.box_kite`, genuinely 7 struts / 42 Assessors, not a
metaphor), built once via `BoxKite.between(eye, hands)` as *"the relational
language spoken by both MindsEye and PapersHands,"* signed so a third party
can verify which two subsystems co-authored it. The real sentence creator
(VerbNet sails + WordNet hypernym-closure fill + a SELRESTR gate,
`engine/grammar/`) is live as of 2026-09-11, confirmed running end to end
this session (`voice:creator` in a real Chat-tab transcript, a genuine
constructed sentence, not one of the eleven canned templates it replaced).
None of this paper's Gamma-Radial Windspeed feeds it yet.

### The A-Matrix Basin Windspeed

The other windspeed tested in this paper's own §9.1 — the **A-Matrix
Basin Windspeed** (A-matrix basin drift) — was deliberately not used
here. It is real, corpus-dependent, and usage-sensitive in exactly the
way this paper's corpus-free Gamma-Radial Windspeed isn't, which is
precisely why it's the right scalar for word *selection* inside live
sentence construction rather than for address-only context propagation.
It is the constructor windspeed for a later, separate engineering pass
on the Mind's Eye (short-term memory, above).

### Mind's Eye as a box kite

A stated direction, not yet built: making the Mind's Eye — short-term
memory — itself a box kite, so that `rehearse` (raising salience on a
candidate) is tracing rings — closed walks — on the kite's own structure,
`archive` is committing whichever ring won, and audience-appropriate word
choice is a genuine geometric constraint (steering the walk within a
listener's own reachable vertices) rather than a filter bolted on
afterward. Sentences as **rings inside one box kite**, not rings of box
kites — a real correction to an earlier framing, kept as a parallel, not
a replacement, to the older per-word box-kite-as-database model this
project also still uses (§6).

The promotion step this implies — a rehearsed ring becoming committed,
long-term-memory output — is governed in the Mind's Eye's own design by
the **Zero Divisor Reframe**: a thought-pathway is promoted only once it
is both mathematically correct *and* contextually sane, two separate
gates, kept separate on purpose. That mechanism lives in `VAPMIP`, is
real, and is named here only as a pointer — it is not developed, and not
in scope, in this paper.

### A methodology note, for whoever picks this up next

Two real mistakes in this paper's own working sessions — analysing a
Native-Space object in Cartesian coordinates, and quantizing a continuous
generator onto a 16-point lattice without noticing — cost real time before
being caught. Both are now a standing skill
(`~/.claude/skills/observer-position/`), built specifically so hyperdimensional
work states its coordinate frame and its aperture before trusting a result,
the same discipline a camera pose or a viewport offset already gets in
lower-dimensional work. Offered here as process, not results, because the
mistakes were real and the fix generalises past this one paper.
