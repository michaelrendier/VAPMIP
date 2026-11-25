# Recipe library v2 (R1-R2)

New rows are PROPOSED (engineering), with the reason:

| row | reason |
|---|---|
| drive | intense pull toward one goal; what the DSM calls a manic layer, without the fault |
| hyperfocus | drive with inhibitory control held: one task, nothing else |
| wrath | protective anger at a violation, care still present (OXT stays up, unlike irritability) |
| indignation | anger at unfairness, aimed outward |
| incredulity | astonished disbelief |
| resolve | settled determination |
| composure | calm competence under load |
| equanimity | emotions put away; steady and low; a person with little affect showing |
| flow | absorbed skilled activity |
| serenity | deep calm |
| weariness | tired, spent |
| loneliness | missing connection |
| boredom | under-stimulated |
| awe | wonder at something large |
| tenderness | gentle care |
| determination_to_teach | the mentor state: wants the other to learn (Cody: a mentor in the kitchen) |

## R1  many-at-once readout (mixtures + noise)

1500 random mixtures of 1-3 recipes, Dirichlet weights, noise sigma = 0.08 on the pole levels (clipped at 0).  top1 = the heaviest component is the top answer; set = all true components appear in the top-k answers (k = number true).

| library | method | top-1 heaviest component | all components found |
|---|---|---|---|
| old library (36 rows) | best cosine | 0.702 | 0.339 |
| old library (36 rows) | NNLS | 0.667 | 0.378 |
| v2 library (52 rows) | best cosine | 0.691 | 0.349 |
| v2 library (52 rows) | NNLS | 0.576 | 0.314 |

## R2  balance of the two libraries (net = sum of light - sum of dark in the signed row)

| library | rows | net-dark | net-light | near zero |
|---|---|---|---|---|
| old (28 GoEmotions + 8 DSM) | 36 | 17 | 18 | 1 |
| v2 | 52 | 20 | 31 | 1 |

NNLS minus best-cosine on v2: top-1 -0.115, all-found -0.035.
