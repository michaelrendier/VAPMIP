# The seven roles against the operator inventories we already have (2026-10-17)

Deconstruction uses **only the seven silk types** (`ANCHOR SPAN SCAFFOLD ELABORATE HOOK WRAP SHELL`; SPAN has `relation`, `claim`,
`frame`). The orbweaver web does not take part. The rule base is `silk_map.py`; the measurements come from
`crosswalk_tests.py` (run it: `python3 crosswalk_tests.py A|A2|B|C|D|F`). Test results are in `CROSSWALK_REPORT.md`.
Everything marked *measured* was run on this machine against annotation that was already on disk; everything marked *crosswalk* is a
proposed correspondence with nothing run behind it.

## 1. The Zork parser's categories (the ones the roles replace)

| Zork | role | status |
|---|---|---|
| VERB (selects one of 16 operators) | SPAN.relation (the 16 operators stay as an attribute of it) | crosswalk; the verb still governs |
| NOUN | ANCHOR (given or topic), HOOK (specific), or SPAN.claim (complement) by position | crosswalk; the split is by dependency, not by word |
| PREP | SPAN.frame (the marker; the NP after it is the frame's content) | measured: 102 lemmas cover 100% of UD case-marking tokens |
| IT / THEM (anaphor) | ANCHOR | crosswalk |
| ARTICLES (skipped by Zork) | ANCHOR, as givenness markers | measured: 426 lemmas, top 25 cover 96.8% |
| AND chains | WRAP | measured: 79 lemmas cover 100% of mark and cc tokens |
| directions (N, S, E, W) | SPAN.relation (branch operator) plus SPAN.frame | crosswalk |
| nothing | SCAFFOLD, ELABORATE, SHELL | the roles Zork never had |

## 2. WordNet and its relatives (the "operators" of the lexicons)

| inventory | maps to | status |
|---|---|---|
| WordNet part of speech n, v, a, r | n: ANCHOR, HOOK or claim; v: relation; a, r: ELABORATE | crosswalk |
| WordNet's 35 generic verb frames | all 35 open with a subject (ANCHOR) and decompose into relation + claim + frame | **measured 35 of 35** |
| the 19 relation pointers, 45 lexicographer files | NOT part of deconstruction: these are what the web spreads over | by rule |
| VerbNet syntax elements (NP, VERB, PREP, ADJ, ADV, LEX) | NP before the verb: ANCHOR; NP after: claim; PREP+NP: frame; VERB: relation | **measured: all 1,310 frames; 98.3% have a pre-verbal NP, it is an Agent in 861** |
| VerbNet thematic roles | Agent: ANCHOR; Theme, Patient, Topic: claim; Location, Destination, Source, Instrument, Beneficiary: frame | crosswalk |
| PropBank ARG0 to ARG5, ARGM-* | see `CROSSWALK_REPORT.md` section B | measured on the Penn Treebank sample |
| FrameNet frame elements (Core, Peripheral, Extra-Thematic) | Core: claim; Peripheral: frame; Extra-Thematic: ELABORATE or WRAP | crosswalk |
| Universal Dependencies relations | `UD_ROLE` in `silk_map.py` | **measured: 98.4% of 44,071 tokens** |

## 3. The English-grammar and literary inventories

| inventory | maps to |
|---|---|
| the eight traditional parts of speech | noun: ANCHOR, HOOK, claim; pronoun: ANCHOR; verb: relation or SCAFFOLD; adjective, adverb: ELABORATE or claim; preposition: frame marker; conjunction: WRAP; interjection: SHELL; article: ANCHOR |
| Quirk et al. clause elements S V O C A | S: ANCHOR; V: relation (with SCAFFOLD for auxiliaries); O: claim; C: claim (the copular case); A: frame |
| Halliday's transitivity | Process: relation; Participants: ANCHOR and claim; Circumstances: frame |
| Halliday's Theme and Rheme | Theme: ANCHOR; Rheme: SPAN |
| Halliday's textual metafunction | WRAP (cohesion) |
| Halliday's Mood and Polarity | SHELL (and SCAFFOLD for the finite carrier) |
| Austin and Searle speech acts (assertive, directive, commissive, expressive, declaration) | SHELL.act |
| Burke's dramatistic pentad (Agent, Act, Scene, Agency, Purpose) | Agent: ANCHOR; Act: relation; Scene, Agency, Purpose: frame |
| Toulmin's argument (Claim, Grounds, Qualifier, Rebuttal) | Claim: SPAN.claim; Grounds: HOOK (specifics); Qualifier: SCAFFOLD (modal) or ELABORATE; Rebuttal: WRAP (contrast) |
| PDTB and RST relations (Temporal, Contingency, Comparison, Expansion) | WRAP; each connective class carries a radial move on the web |

## 4. What the tests say (details and numbers in `CROSSWALK_REPORT.md`)

1. **The seven nearly suffice.** On gold UD English-EWT, 98.4% of tokens get a role. What is left is `parataxis` (a second clause) and `list`
   items: both are fixable inside the seven (a second SPAN; list items as HOOK).
2. **Four of the roles are closed classes and can be hardcoded**: SCAFFOLD (16 lemmas, 100%), WRAP (79 lemmas, 100%), the frame
   marker (102 lemmas, 100%), and ANCHOR's givenness markers (top 25 cover 97%). ELABORATE is open (2,667 lemmas): it needs WordNet.
   One call to make: the infinitive "to" is the third most common WRAP token (a `mark`) but behaves like a SCAFFOLD.
3. **SPAN's claim and frame are not independent, only free.** Phi is -0.245 in real text and -0.294 across VerbNet's frames: a verb with a
   direct object tends to carry fewer prepositional frames. All four combinations occur, and 17.3% of clauses are copular
   (the relation is NAME and the load is in the claim). So the three fields stay separate slots, but a parser may not assume independence.
4. **SHELL needs a bigger act inventory than my answers used.** The 15 dialogue acts of NLTK's nps_chat all map; they add accept, answer,
   bye, clarify, continuer, exclaim, reject and system. `imperative` and `thanks` (mine) are not in that corpus.

## 5. What the PropBank test adds (section B of the report: 700 sentences, Stanza-parsed from gold tokens)

* **ARG0 lands on ANCHOR 66%** (86.5% counting a name that is both), **ARGM-MOD on SCAFFOLD 95.7%**, **ARGM-LOC 86%**, **ARGM-PNC 98%**,
  **ARGM-CAU 89%**. The roles hold where the syntax is regular.
* **ARG1 is ANCHOR 21% of the time and claim 60%:** a passive or unaccusative subject is the ARG1, so the role depends on voice. Both are right.
* **Only 38% of PropBank's predicates land on SPAN.relation.** The rest sit in non-root positions: 421 are copular predicates (claim),
  380 are participles or adjectives modifying a noun (ELABORATE), 272 are verbs inside adverbial clauses (frame). A verb in a
  subordinate clause is the relation of **its own SPAN**: deconstruction must recurse into `advcl`, `ccomp`, `xcomp`, `acl`, `conj`,
  `parataxis` (the notes already write these as `<clause: ...>`; this is the evidence it is not optional).
* **Scope is not syntactic.** ARGM-TMP and ARGM-LOC are `advmod` as often as they are `obl` ("yesterday", "there"): 25% and 10% land on ELABORATE
  while meaning a frame. ARGM-MNR splits 48% ELABORATE ("quickly") and 40% frame ("in a hurry"), which is right.
  Fix: a small closed list of temporal and locative adverbs routes `advmod` to SPAN.frame (it can be mined from this very data).
* **Negation is double-counted:** "not" is SHELL.polarity 50% and ELABORATE 49%. Polarity must override.
* **Discourse adverbs are mislabelled:** ARGM-DIS is ELABORATE 63% and WRAP only 23% ("however", "also", "thus"). A closed list of discourse
  adverbs routes them to WRAP.

## 6. Rule-base changes the tests call for (v2 of `silk_map.py`, not yet made)

1. Clause recursion: a verb under advcl, ccomp, xcomp, acl, acl:relcl, conj, parataxis opens its own SPAN (relation), and the whole clause takes the role it has in the parent.
2. A closed list of temporal and locative adverbs: `advmod` to SPAN.frame.
3. Polarity overrides ELABORATE.
4. A closed list of discourse adverbs: to WRAP.
5. `parataxis` and `list` handled (second SPAN; list items as HOOK).
6. The infinitive "to" (a `mark`) to SCAFFOLD.
7. Voice recorded: a passive subject is ANCHOR and also the claim of the verb.
8. SHELL.act inventory widened to the dialogue acts (accept, answer, bye, clarify, continuer, exclaim, reject, system) plus my `imperative` and `thanks`.
