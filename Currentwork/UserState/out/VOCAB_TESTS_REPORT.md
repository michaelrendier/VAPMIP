# Vocabulary store tests (V1-V4)

## V1  additive store, exact round trip

order-independent with gold senses: **True**   ·   disk round trip exact: **True**   ·   11 observations, 9 lemmas

## V2  a synset added on the fly

sense id usr:86:1; 19-vector nonzero at ['hypernyms', 'also_sees']; gamma_radial -0.806
kitchen context chooses: `usr:86:1`   ·   "page 86" in coding context chooses: `eighty-six.s.01`   ·   usage count after 3 kitchen sentences: 3

**PASS**

## V3  disambiguation on SemCor (gold senses)

5099 usable SemCor sentences; train (confirmed senses) 4000, test 800

| method | accuracy | ambiguous tokens |
|---|---|---|
| rank-first baseline | 0.518 | 8119 |
| gloss overlap only | 0.464 | 8119 |
| rank prior + gloss | 0.519 | 8119 |
| rank prior + gloss + this store's usage | 0.564 | 8119 |

usage store minus rank-first baseline: +0.046

## V4  vocabulary depth by register

| register | texts | mean log polysemy [95% CI] | rare-word rate [95% CI] | word length | FK grade |
|---|---|---|---|---|---|
| nps_chat | 41 | 1.424 [1.269, 1.587] | 0.375 [0.299, 0.448] | 6.13 | 1.7 |
| goemotions | 269 | 1.693 [1.645, 1.737] | 0.273 [0.252, 0.294] | 5.51 | 4.2 |
| proj_chat | 3 | 1.641 [1.266, 2.046] | 0.433 [0.400, 0.500] | 6.26 | 1.9 |
| proj_novel | 62 | 1.636 [1.533, 1.744] | 0.291 [0.240, 0.338] | 6.25 | 5.5 |
| ScalarContext paper | 169 | 1.422 [1.383, 1.460] | 0.460 [0.437, 0.482] | 5.98 | 12.4 |

ordering nps_chat < goemotions < proj_chat < paper holds on polysemy: **False**, on rare-word rate: **False**

## V4b  sense-tail depth (retooled)

| register | chunks | non-first-sense share [95% CI] | sense familiarity (log count) [95% CI] | log polysemy of the words used | word length |
|---|---|---|---|---|---|
| nps_chat | 27 | 0.000 [0.000, 0.000] | 2.525 [2.214, 2.823] | 2.82 | 6.39 |
| goemotions | 148 | 0.002 [0.000, 0.005] | 2.286 [2.172, 2.397] | 2.73 | 5.55 |
| Cody (dark-prompt.md) | 58 | 0.000 [0.000, 0.000] | 1.954 [1.790, 2.109] | 2.76 | 6.08 |
| ScalarContext paper | 146 | 0.002 [0.000, 0.005] | 2.249 [2.133, 2.363] | 2.64 | 6.05 |
| Kafka (Wyllie) | 146 | 0.001 [0.000, 0.002] | 2.379 [2.268, 2.495] | 2.74 | 5.79 |

ordering holds on non-first-sense share: **False**; on sense familiarity falling: **False**

