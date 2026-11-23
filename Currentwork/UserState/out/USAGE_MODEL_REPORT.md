# The usage-statistics pathway (word + bigram counts) against the meter battery

Trained on 56,030 human-labelled GoEmotions texts (the 1,954 test texts of the battery excluded); 45,448 word and bigram features; fit 7.9 s. Target: the 14 pole levels implied by the human labels through the setpoint table. Test: the same 1,954 held-out texts as T1.

| pathway | mean r over 14 poles | net-sign accuracy | kappa | cost per text |
|---|---|---|---|---|
| usage model (word+bigram counts, ridge) | +0.677 (14 poles) | 0.718 | 0.522 | 0.041 ms (batch of 300) |
| VADER only | +0.456 (6 poles) | 0.648 | 0.426 | 0.26 ms |
| battery without GoEmotions-trained meter (independent) | +0.585 (13 poles) | 0.670 | 0.465 | ~1.0 ms counting + 86 ms (7-emotion model) |
| full battery (leaks) | +0.742 (14 poles) | 0.781 | 0.632 | ~1.96 ms counting + 364 ms (three models) |

Usage model minus independent battery, net-sign accuracy: +0.048 (bootstrap 95% CI [+0.025, +0.072], paired t = 3.81, p = 1.4e-04).

Usage model minus VADER, net-sign accuracy: +0.069 (bootstrap 95% CI [+0.047, +0.092], paired t = 5.84, p = 6.0e-09).

## On Kafka (4,627 sentences)

Per-sentence e0, usage model against the full battery: r = +0.517 (95% CI [+0.495, +0.537]). Mean e0: usage model +0.102, battery -0.083.

Before the Law: mean e0 +0.096; thirds +0.089, +0.091, +0.107; last sentence ("now I'll go and close it") +0.06; sentence 43 ("this entrance was meant only for you") +0.29.

## What the usage model learned (largest weights)

- NE-: scared, afraid, scary, terrifying, horrible, fuck, terrible, fucking, stupid, hate
- OXT+: thanks, love, loved, thank, i like, loving, lovely, loves, great, glad
- DA+: lol, excited, hope, happy, fun, haha, love, funny, wish, enjoy
- 5HT-: sad, sadly, sorry, embarrassing, hurts, worse, painful, worst, disgusting, bad
- GABA-: scared, fuck, scary, afraid, terrifying, fucking, stupid, horrible, angry, hate
- OPI+: love, thanks, glad, loved, lol, happy, enjoy, loving, haha, fun
