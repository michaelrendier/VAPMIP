# Crosswalk test report

Generated 2026-10-17 by `crosswalk_tests.py` (tests A, A2, C, D, F re-run for this file; B took 6 minutes and its output was saved from the run). Rule base: `silk_map.py` first draft. Interpretation: `CROSSWALK.md`.

```
A. UD English-EWT dev + test: 4078 sentences, 44071 non-punctuation tokens
   tokens given at least one role: 43349 (98.4%); given more than one role: 5596 (12.7%)
   role.field counts: ELABORATE 11204, ANCHOR 10350, SPAN.frame 7264, HOOK 5061, SPAN.claim 4919, SCAFFOLD 3222, WRAP 3102, SPAN.relation 2594, SHELL.polarity 564, SHELL 352, SHELL.gap 330
   left over (deprel, upos) not covered by the seven: ('parataxis', 'VERB') x293, ('list', 'NUM') x147, ('parataxis', 'NOUN') x134, ('list', 'PROPN') x124, ('list', 'NOUN') x123, ('parataxis', 'ADJ') x86, ('parataxis', 'PROPN') x25, ('root:X', 'X') x24, ('root:SYM', 'SYM') x18, ('list', 'SYM') x14, ('parataxis', 'X') x13, ('list', 'ADJ') x9
   sentences with no ANCHOR: 10.1%; no SPAN: 26.4%; neither: 5.6%
   roles occupied per sentence: 0: 1.3%, 1: 5.9%, 2: 16.7%, 3: 13.1%, 4: 17.4%, 5: 21.4%, 6: 18.8%, 7: 5.4%

A2. UD English-EWT train, real text: 22392 event-verb clauses and 4692 copular clauses (17.3% copular)
   SPAN fields claim x frame per event verb: both 4272, claim only 9584, frame only 4747, neither 3789; phi = -0.245 (0 = independent)
   P(claim) = 61.9%, P(frame) = 40.3%, P(both) = 19.1% vs the product 24.9%

B. PropBank on the Penn Treebank sample, Stanza-parsed from gold tokens: 700 sentences sampled, 0 skipped (token mismatch)
   predicate (the verb) gets: SPAN.relation 678, SPAN.claim 421, ELABORATE 380, SPAN.frame 272, UNCOVERED.parataxis 34
   argument label -> role of the argument's head token (top three), and whether the predicted role was among them:
     ARG1      n= 1806  SPAN.claim 60%, ANCHOR 21%, HOOK 9%                            expected SPAN.claim   hit 66.6%
     ARG0      n= 1491  ANCHOR 66%, HOOK 22%, SPAN.claim 5%                            expected ANCHOR       hit 86.5%
     ARGM-TMP  n=  406  SPAN.frame 52%, ELABORATE 25%, HOOK 16%                        expected SPAN.frame   hit 64.6%
     ARGM-ADV  n=  181  SPAN.frame 60%, ELABORATE 32%, HOOK 3%                         expected SPAN.frame   hit 62.5%
     ARG2      n=  173  SPAN.claim 55%, ANCHOR 18%, HOOK 12%                           expected SPAN.claim   hit 63.6%
     ARGM-MOD  n=  162  SCAFFOLD 95%, SPAN.relation 1%, SPAN.claim 1%                  expected SCAFFOLD     hit 95.7%
     ARGM-LOC  n=  149  SPAN.frame 65%, HOOK 22%, ELABORATE 10%                        expected SPAN.frame   hit 86.0%
     ARGM-MNR  n=  128  ELABORATE 48%, SPAN.frame 40%, SPAN.claim 6%                   expected SPAN.frame   hit 42.3%
     ARGM-NEG  n=  120  SHELL.polarity 50%, ELABORATE 49%, WRAP 0%                     expected SHELL        hit 100.0%
     ARG2-EXT  n=   78  SPAN.claim 43%, HOOK 42%, SPAN.frame 10%                       expected -            hit n/a
     ARG4-to   n=   78  SPAN.frame 53%, HOOK 41%, ELABORATE 5%                         expected -            hit n/a
     ARGM-DIS  n=   71  ELABORATE 63%, WRAP 23%, SPAN.frame 12%                        expected WRAP         hit 23.3%
     ARG0-by   n=   57  SPAN.claim 71%, HOOK 24%, SPAN.frame 3%                        expected -            hit n/a
     ARGM-PNC  n=   49  SPAN.frame 95%, HOOK 2%, ELABORATE 2%                          expected SPAN.frame   hit 97.9%
     ARG2-to   n=   33  SPAN.frame 87%, HOOK 9%, ELABORATE 3%                          expected -            hit n/a
     ARG3-from n=   31  SPAN.frame 58%, HOOK 35%, ELABORATE 6%                         expected -            hit n/a
     ARGM-DIR  n=   29  SPAN.frame 51%, ELABORATE 24%, HOOK 17%                        expected SPAN.frame   hit 62.5%
     ARGM-CAU  n=   28  SPAN.frame 82%, ELABORATE 7%, SHELL.gap 7%                     expected SPAN.frame   hit 88.5%
     ARG3      n=   27  SPAN.claim 55%, ANCHOR 22%, HOOK 7%                            expected SPAN.claim   hit 60.0%
     ARG2-with n=   25  SPAN.frame 76%, ELABORATE 12%, HOOK 12%                        expected -            hit n/a

C. WordNet 3.1 verb frames: 35 generic frames; all open with a subject (ANCHOR): 35; others: []
   slot patterns (ANCHOR + SPAN fields) and how many frames have each:
     12  ANCHOR + relation, claim
      8  ANCHOR + relation, claim, (marker)
      7  ANCHOR + relation, (marker), claim
      4  ANCHOR + relation
      2  ANCHOR + relation, frame
      2  ANCHOR + relation, claim, frame
   VerbNet 429 classes, 1310 frames. Syntax elements in all frames: NP 2944, VERB 1310, PREP 697, LEX 88, ADJ 45, ADV 34
   every element is one the roles can hold: NP (ANCHOR or claim), VERB (relation), PREP+NP (frame), ADJ (claim), ADV (frame), LEX (fixed words)
   frames with a pre-verbal NP (ANCHOR): 98.3%; thematic roles of that NP: Agent 861, Theme 99, Experiencer 69, Patient 64, Actor1 38, Actor 36, Cause 31, Location 26
   post-verbal claims per frame (0,1,2,3+): 0: 424, 1: 765, 2: 121; frames (PP or ADV) per frame: 0: 674, 1: 553, 2: 83
   SPAN fields claim x frame across VerbNet frames: both 340, claim only 546, frame only 296, neither 128; phi = -0.294 (0 = independent)

D. nps_chat: 10567 posts in 15 dialogue acts; acts with no SHELL.act mapping: none
   act counts: Statement 3185, System 2632, Greet 1363, Emotion 1106, ynQuestion 550, whQuestion 533, Accept 233, Bye 195, Emphasis 190, Continuer 168, Reject 159, yAnswer 108, nAnswer 72, Clarify 38, Other 35
   SHELL.act values the corpus needs: ['accept', 'answer', 'bye', 'clarify', 'continuer', 'exclaim', 'greet', 'other', 'reject', 'statement', 'system', 'whQuestion', 'ynQuestion']
   values in my hand-made answers but absent from nps_chat: ['imperative', 'thanks']; in nps_chat but absent from my answers: ['accept', 'answer', 'bye', 'clarify', 'continuer', 'exclaim', 'reject', 'system']

F. closed-class test on UD English-EWT (train, dev, test): distinct lemmas per role-class and the share of its tokens the top N lemmas cover
   SCAFFOLD (aux, cop, expl)          tokens  16404, distinct lemmas    16; top 10 cover 97.1%, top 25 100.0%, top 50 100.0%, top 100 100.0%; most common: be, have, will, do, can, would, there, could
   WRAP (mark, cc)                    tokens  17023, distinct lemmas    79; top 10 cover 87.9%, top 25 96.6%, top 50 99.7%, top 100 100.0%; most common: and, to, that, but, if, or, as, because
   SPAN.frame marker (case)           tokens  21434, distinct lemmas   102; top 10 cover 82.8%, top 25 94.1%, top 50 98.6%, top 100 100.0%; most common: of, in, for, to, with, on, at, 's
   ELABORATE (amod, advmod)           tokens  26138, distinct lemmas  2667; top 10 cover 22.8%, top 25 35.7%, top 50 47.6%, top 100 59.4%; most common: not, good, so, just, very, when, also, new
   ANCHOR givenness (det, nmod:poss)  tokens  24063, distinct lemmas   426; top 10 cover 89.4%, top 25 96.8%, top 50 97.6%, top 100 98.4%; most common: the, a, my, this, your, their, his, our

```
