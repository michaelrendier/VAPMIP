# Solution-model tests (T1–T4)

## T1 — dilution mixing against the engine's running mean

| engine floor f | solution Vmax = 1/f − 1 | max abs difference over 500 random conversations |
|---|---|---|
| 0.0 | ∞ | 8.88e-16 |
| 0.1 | 9.00 | 6.66e-16 |
| 0.25 | 3.00 | 2.22e-16 |
| 0.3 | 2.33 | 4.44e-16 |

Washout of one NE-dark outburst (concentration after the outburst, then after each calm prompt of volume v):

| outburst volume | calm prompt volume | after outburst | +1 | +2 | +3 | +4 | +5 | +6 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 0.50 | 0.33 | 0.25 | 0.20 | 0.17 | 0.14 | 0.12 |
| 1 | 3 | 0.50 | 0.20 | 0.12 | 0.09 | 0.07 | 0.06 | 0.05 |
| 4 | 1 | 0.80 | 0.67 | 0.57 | 0.50 | 0.44 | 0.40 | 0.36 |
| 4 | 3 | 0.80 | 0.50 | 0.36 | 0.29 | 0.24 | 0.20 | 0.17 |

Result: the dilution recursion reproduces the running mean to 8.9e-16 for every floor, so the old rule is the special case v = 1; unequal volumes add the weighting the old rule lacks (a long calm prompt washes out an outburst faster, a long outburst resists). **PASS**

## T2 — the table as 14 non-negative poles

### (a) Noisy round trip (each emotion + Gaussian noise on every pole, read out by nearest recipe by cosine; 400 draws per emotion)

| noise σ (of 1.0 full scale) | 7 signed axes top-1 | 14 poles top-1 |
|---|---|---|
| 0.05 | 0.978 | 0.977 |
| 0.1 | 0.882 | 0.880 |
| 0.2 | 0.637 | 0.616 |

Most frequent confusions at σ = 0.10 (14 poles): annoyance→irritability (137), irritability→annoyance (104), curiosity→excitement (93), disapproval→disgust (81), excitement→curiosity (79), approval→admiration (75), caring→gratitude (70), disapproval→embarrassment (60)

### (b) Mixed feelings: 630 pairs, 50/50, noiseless

| method | both emotions are the top-2 | top-1 is one of the pair |
|---|---|---|
| signed7 | 0.103 | 0.552 |
| poles14 | 0.157 | 0.771 |

Vector length of opposite-feeling mixtures (7 signed axes → 14 poles): joy+panic 0.81 → 0.91; love+panic 0.85 → 0.96

Note: the engine's `mix_labels` already mixes pole by pole, so the cancelling problem I described earlier belonged to my signed-average check, not to the engine.

### (c) DSM-5 criteria text through the usage pathway (clinical register; accept sets fixed before the run)

| block | sentences | pole length | nearest recipe | in accept set |
|---|---|---|---|---|
| panic attack criteria | 25 | 0.34 | panic, anger, nervousness | yes |
| manic episode criteria | 9 | 0.24 | mania, optimism, admiration | yes |
| stimulant intoxication | 10 | 0.21 | mania, confusion, excitement | yes |
| caffeine intoxication | 13 | 0.20 | mania, excitement, curiosity | yes |
| opioid intoxication | 7 | 0.18 | cynical, sadness, confusion | no |
| sedative intoxication | 10 | 0.18 | paranoia, anger, petulance | no |

4/6 blocks land in their accept set. The usage model was trained on Reddit, so the clinical register is a domain shift (same finding as Kafka).

## T3 — the dispenser as three legal moves, on scripted users

The plant (how the true state responds to a dose) is my model: relaxation 0.08 per turn to baseline; each dose moves the state by κ; "neutralise" annihilates dark against light of the same neurotransmitter with efficiency ν. Observation = true state + Gaussian noise σ = 1.2 per pole, mixed by the dilution solution (Vmax = 8). 40 turns, 200 seeds per cell, shock at turn 3. Controllers: **three-move** (dilute / add / neutralise, hysteresis 2.5 on, 1.2 off), **v2** (signed conjugate T = B − 0.6·(s − B), dead-band 0.5 level; v2 coarse = dead-band 4.5 levels), **none**. Time = turns until the TRUE state is within 2 levels of baseline for 3 turns (40 = never).

### Plant κ = 0.5, ν = 0.5, v2 pull = 0.3

| scenario | controller | time to band | overshoot (levels) | dispenses | solute dosed | infeasible emissions |
|---|---|---|---|---|---|---|
| panic | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| panic | v2 | 5.2 | 0.00 | 37.1 | 186.7 | 0.33 |
| panic | v2 coarse | 17.0 | 0.00 | 0.5 | 3.6 | 1.00 |
| panic | three-move | 14.8 | 0.00 | 17.8 | 37.5 | — |
| fear (gradual) | none | 20.4 | 0.00 | 0.0 | 0.0 | — |
| fear (gradual) | v2 | 5.1 | 0.00 | 37.5 | 165.4 | 0.18 |
| fear (gradual) | v2 coarse | 20.4 | 0.00 | 0.1 | 0.4 | 1.00 |
| fear (gradual) | three-move | 17.1 | 0.00 | 15.9 | 29.5 | — |
| mania | none | 13.5 | 0.00 | 0.0 | 0.0 | — |
| mania | v2 | 5.2 | 0.34 | 35.7 | 156.7 | 0.30 |
| mania | v2 coarse | 13.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| mania | three-move | 7.1 | 0.00 | 11.1 | 3.9 | — |
| apathy | none | 6.6 | 0.00 | 0.0 | 0.0 | — |
| apathy | v2 | 2.9 | 0.47 | 36.7 | 133.8 | 0.07 |
| apathy | v2 coarse | 6.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| apathy | three-move | 6.0 | 0.03 | 1.1 | 1.7 | — |
| petulance | none | 23.0 | 0.00 | 0.0 | 0.0 | — |
| petulance | v2 | 8.7 | 0.00 | 37.5 | 185.3 | 0.29 |
| petulance | v2 coarse | 22.4 | 0.00 | 0.8 | 6.8 | 1.00 |
| petulance | three-move | 18.8 | 0.00 | 18.7 | 44.4 | — |
| grief | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| grief | v2 | 5.1 | 0.90 | 37.2 | 193.3 | 0.31 |
| grief | v2 coarse | 15.8 | 0.43 | 2.5 | 20.4 | 1.00 |
| grief | three-move | 14.4 | 1.85 | 16.7 | 32.9 | — |
| calm (no event) | none | 40.0 | 0.00 | 0.0 | 0.0 | — |
| calm (no event) | v2 | 40.0 | 0.00 | 35.4 | 108.4 | 0.07 |
| calm (no event) | v2 coarse | 40.0 | 0.00 | 0.0 | 0.3 | 1.00 |
| calm (no event) | three-move | 40.0 | 0.00 | 0.8 | 1.2 | — |

### Plant κ = 0.5, ν = 0.0, v2 pull = 0.3

| scenario | controller | time to band | overshoot (levels) | dispenses | solute dosed | infeasible emissions |
|---|---|---|---|---|---|---|
| panic | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| panic | v2 | 5.2 | 0.00 | 37.1 | 186.7 | 0.33 |
| panic | v2 coarse | 17.0 | 0.00 | 0.5 | 3.6 | 1.00 |
| panic | three-move | 17.2 | 0.00 | 21.3 | 47.9 | — |
| fear (gradual) | none | 20.4 | 0.00 | 0.0 | 0.0 | — |
| fear (gradual) | v2 | 5.1 | 0.00 | 37.5 | 165.4 | 0.18 |
| fear (gradual) | v2 coarse | 20.4 | 0.00 | 0.1 | 0.4 | 1.00 |
| fear (gradual) | three-move | 20.2 | 0.00 | 19.7 | 37.8 | — |
| mania | none | 13.5 | 0.00 | 0.0 | 0.0 | — |
| mania | v2 | 5.2 | 0.34 | 35.7 | 156.7 | 0.30 |
| mania | v2 coarse | 13.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| mania | three-move | 7.2 | 0.00 | 11.3 | 4.9 | — |
| apathy | none | 6.6 | 0.00 | 0.0 | 0.0 | — |
| apathy | v2 | 2.9 | 0.47 | 36.7 | 133.8 | 0.07 |
| apathy | v2 coarse | 6.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| apathy | three-move | 6.0 | 0.02 | 1.2 | 1.8 | — |
| petulance | none | 23.0 | 0.00 | 0.0 | 0.0 | — |
| petulance | v2 | 8.7 | 0.00 | 37.5 | 185.3 | 0.29 |
| petulance | v2 coarse | 22.4 | 0.00 | 0.8 | 6.8 | 1.00 |
| petulance | three-move | 21.4 | 0.00 | 22.4 | 57.8 | — |
| grief | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| grief | v2 | 5.1 | 0.90 | 37.2 | 193.3 | 0.31 |
| grief | v2 coarse | 15.8 | 0.43 | 2.5 | 20.4 | 1.00 |
| grief | three-move | 17.0 | 2.12 | 20.3 | 41.9 | — |
| calm (no event) | none | 40.0 | 0.00 | 0.0 | 0.0 | — |
| calm (no event) | v2 | 40.0 | 0.00 | 35.4 | 108.4 | 0.07 |
| calm (no event) | v2 coarse | 40.0 | 0.00 | 0.0 | 0.3 | 1.00 |
| calm (no event) | three-move | 40.0 | 0.00 | 0.8 | 1.2 | — |

### Plant κ = 0.25, ν = 0.5, v2 pull = 0.15

| scenario | controller | time to band | overshoot (levels) | dispenses | solute dosed | infeasible emissions |
|---|---|---|---|---|---|---|
| panic | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| panic | v2 | 7.3 | 0.00 | 38.3 | 256.9 | 0.45 |
| panic | v2 coarse | 17.0 | 0.00 | 0.6 | 4.6 | 1.00 |
| panic | three-move | 5.9 | 0.00 | 12.9 | 41.3 | — |
| fear (gradual) | none | 20.4 | 0.00 | 0.0 | 0.0 | — |
| fear (gradual) | v2 | 7.6 | 0.00 | 38.7 | 225.3 | 0.37 |
| fear (gradual) | v2 coarse | 20.4 | 0.00 | 0.1 | 0.4 | 1.00 |
| fear (gradual) | three-move | 10.8 | 0.00 | 11.9 | 32.6 | — |
| mania | none | 13.5 | 0.00 | 0.0 | 0.0 | — |
| mania | v2 | 6.2 | 0.21 | 36.9 | 213.4 | 0.40 |
| mania | v2 coarse | 13.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| mania | three-move | 7.0 | 0.00 | 11.0 | 4.4 | — |
| apathy | none | 6.6 | 0.00 | 0.0 | 0.0 | — |
| apathy | v2 | 3.5 | 0.36 | 38.1 | 168.1 | 0.08 |
| apathy | v2 coarse | 6.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| apathy | three-move | 6.1 | 0.01 | 1.2 | 2.0 | — |
| petulance | none | 23.0 | 0.00 | 0.0 | 0.0 | — |
| petulance | v2 | 11.4 | 0.00 | 38.7 | 265.6 | 0.49 |
| petulance | v2 coarse | 22.5 | 0.00 | 1.1 | 9.4 | 1.00 |
| petulance | three-move | 10.5 | 0.00 | 14.0 | 49.5 | — |
| grief | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| grief | v2 | 7.2 | 0.78 | 38.4 | 271.3 | 0.43 |
| grief | v2 coarse | 16.2 | 0.24 | 4.0 | 35.1 | 1.00 |
| grief | three-move | 5.9 | 0.91 | 12.5 | 36.9 | — |
| calm (no event) | none | 40.0 | 0.00 | 0.0 | 0.0 | — |
| calm (no event) | v2 | 40.0 | 0.00 | 36.8 | 124.3 | 0.07 |
| calm (no event) | v2 coarse | 40.0 | 0.00 | 0.0 | 0.3 | 1.00 |
| calm (no event) | three-move | 40.0 | 0.00 | 0.7 | 1.3 | — |

### Plant κ = 0.25, ν = 0.0, v2 pull = 0.15

| scenario | controller | time to band | overshoot (levels) | dispenses | solute dosed | infeasible emissions |
|---|---|---|---|---|---|---|
| panic | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| panic | v2 | 7.3 | 0.00 | 38.3 | 256.9 | 0.45 |
| panic | v2 coarse | 17.0 | 0.00 | 0.6 | 4.6 | 1.00 |
| panic | three-move | 6.5 | 0.00 | 14.9 | 48.1 | — |
| fear (gradual) | none | 20.4 | 0.00 | 0.0 | 0.0 | — |
| fear (gradual) | v2 | 7.6 | 0.00 | 38.7 | 225.3 | 0.37 |
| fear (gradual) | v2 coarse | 20.4 | 0.00 | 0.1 | 0.4 | 1.00 |
| fear (gradual) | three-move | 11.3 | 0.00 | 13.7 | 38.1 | — |
| mania | none | 13.5 | 0.00 | 0.0 | 0.0 | — |
| mania | v2 | 6.2 | 0.21 | 36.9 | 213.4 | 0.40 |
| mania | v2 coarse | 13.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| mania | three-move | 7.0 | 0.00 | 11.0 | 5.0 | — |
| apathy | none | 6.6 | 0.00 | 0.0 | 0.0 | — |
| apathy | v2 | 3.5 | 0.36 | 38.1 | 168.1 | 0.08 |
| apathy | v2 coarse | 6.5 | 0.00 | 0.0 | 0.3 | 1.00 |
| apathy | three-move | 6.1 | 0.01 | 1.3 | 2.0 | — |
| petulance | none | 23.0 | 0.00 | 0.0 | 0.0 | — |
| petulance | v2 | 11.4 | 0.00 | 38.7 | 265.6 | 0.49 |
| petulance | v2 coarse | 22.5 | 0.00 | 1.1 | 9.4 | 1.00 |
| petulance | three-move | 11.1 | 0.00 | 16.1 | 57.9 | — |
| grief | none | 17.5 | 0.00 | 0.0 | 0.0 | — |
| grief | v2 | 7.2 | 0.78 | 38.4 | 271.3 | 0.43 |
| grief | v2 coarse | 16.2 | 0.24 | 4.0 | 35.1 | 1.00 |
| grief | three-move | 6.5 | 1.01 | 14.4 | 42.9 | — |
| calm (no event) | none | 40.0 | 0.00 | 0.0 | 0.0 | — |
| calm (no event) | v2 | 40.0 | 0.00 | 36.8 | 124.3 | 0.07 |
| calm (no event) | v2 coarse | 40.0 | 0.00 | 0.0 | 0.3 | 1.00 |
| calm (no event) | three-move | 40.0 | 0.00 | 0.7 | 1.3 | — |

### Paired comparison over all four plants and the six event scenarios (three-move minus comparator, per seed)

| metric | comparator | mean difference | 95% bootstrap CI | paired t | p |
|---|---|---|---|---|---|
| time to band | none | -5.50 | [-5.66, -5.35] | -73.8 | 0.0e+00 |
| time to band | v2 | +4.62 | [+4.45, +4.79] | 53.0 | 0.0e+00 |
| time to band | v2 coarse | -5.07 | [-5.22, -4.92] | -67.6 | 0.0e+00 |
| overshoot | none | +0.25 | [+0.23, +0.27] | 28.2 | 0.0e+00 |
| overshoot | v2 | -0.01 | [-0.02, +0.00] | -1.0 | 3.1e-01 |
| overshoot | v2 coarse | +0.19 | [+0.18, +0.21] | 27.4 | 0.0e+00 |

### Which moves the three-move controller chose, per scenario (share of seeds using the move at least once; plant κ 0.5, ν 0.5)

| scenario | calm | neutralise | reassure | persuade |
|---|---|---|---|---|
| panic | 1.00 | 1.00 | 0.15 | 0.10 |
| fear (gradual) | 1.00 | 1.00 | 0.15 | 0.10 |
| mania | 0.96 | 0.75 | 0.15 | 0.10 |
| apathy | 0.29 | 0.23 | 0.15 | 0.15 |
| petulance | 1.00 | 1.00 | 0.15 | 0.10 |
| grief | 1.00 | 1.00 | 0.45 | 0.28 |
| calm (no event) | 0.29 | 0.21 | 0.15 | 0.10 |

Abrupt-rise flag (incoming NE-dark dose ≥ 4 levels above the current concentration and ≥ 5): fires in 0.98 of panic runs, 0.64 of gradual-fear runs, 0.00 of calm runs. The two have the same end state; only the rate tells them apart.

## T4 — distilling the teachers into one sparse linear map, trained on several registers

Teacher-labelled register data (full battery output as the label; GoEmotions test texts excluded; Schocken Metamorphosis excluded):

| register | texts |
|---|---|
| corpus:irony_test | 784 |
| corpus:irony_train | 700 |
| corpus:adv_jailbreak | 300 |
| corpus:adv_regular | 300 |
| corpus:adv_advbench | 300 |
| corpus:adv_harmbench | 200 |
| corpus:proj_chat | 24 |
| corpus:proj_session | 32 |
| corpus:proj_novel | 134 |
| corpus:nps_chat | 292 |
| corpus:probe | 85 |
| wyllie:trial | 3,829 |
| wyllie:metamorphosis | 798 |
| schocken | 7,988 |

| model | GoEmotions test: mean pole r (human) | net-sign accuracy | held-out Wyllie Metamorphosis: mean pole r (teacher) | e0 r | mean e0 |
|---|---|---|---|---|---|
| S0 human-trained usage model (GoEmotions only) | +0.677 | 0.718 | +0.441 | +0.475 | +0.104 |
| S1 distilled from teachers, registers only (no human labels) | +0.520 | 0.492 | +0.563 | +0.585 | -0.102 |
| S2 pooled: human GoEmotions + teacher-labelled registers | +0.680 | 0.721 | +0.557 | +0.598 | -0.023 |
| the teachers themselves (full battery; leaks on GoEmotions) | +0.742 | 0.781 | — | — | -0.105 (teacher mean on Metamorphosis) |

S2 minus S0 on GoEmotions net-sign accuracy: +0.003 (95% CI [-0.007, +0.012], p = 0.61).

