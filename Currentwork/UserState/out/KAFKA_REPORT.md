# Kafka through the pathway machinery

Texts: *The Trial* and *The Metamorphosis*, David Wyllie's English translations from Project Gutenberg (7849, 5200), local copies. 236 paragraphs (Gutenberg sets whole dialogue blocks as one paragraph), 4627 sentences. Line numbers are lines of the e-text file; there are no page numbers in the e-text. *The Complete Stories* (Schocken 1971, LCCN 75-161559) is in copyright and lending-only; "An Imperial Message" and "Description of a Struggle" are in it and in no public-domain English translation I could find.

## Cost of each pathway (this CPU, 8 cores, no GPU)

| pathway | ms per sentence | sentences per second |
|---|---|---|
| scalar boxkite context hash lookups | 0.022 | 45,929 |
| tokenise + arousal/profanity counts | 0.039 | 25,641 |
| stance + incongruity rules | 0.125 | 8,021 |
| combine the meters into the 15-layer state | 0.192 | 5,210 |
| VADER lexicon | 0.263 | 3,806 |
| NPS dialogue-act naive Bayes | 0.364 | 2,748 |
| Empath domain counts | 0.982 | 1,018 |
| extractor v0 (seven slots, WordNet) | 6.978 | 143 |
| 7-emotion (distilroberta, 82M), one sentence at a time | 85.864 | 12 |
| go_emotions (roberta-base, 125M), one sentence at a time | 133.325 | 8 |
| irony (roberta-base, 125M), one sentence at a time | 144.397 | 7 |

Everything that is counting (the first six rows) together: 1.96 ms per sentence. The three models: 364 ms per sentence one at a time (185 times the counting). The lexicon and rule meters are the cheap part; the models are what costs.

## Per work and chapter: the mean state of the sentences

| work | chapter | sentences | e0 mean (95% CI) | dark mass | light mass | strongest dark pole | strongest light pole |
|---|---|---|---|---|---|---|---|
| trial | front | 3 | -0.070 [+nan, +nan] | 0.22 | 0.06 | NE- 0.08 | DA+ 0.02 |
| trial | Chapter One | 554 | -0.072 [-0.089, -0.054] | 0.46 | 0.28 | NE- 0.10 | DA+ 0.08 |
| trial | Chapter Two | 250 | -0.084 [-0.112, -0.057] | 0.45 | 0.24 | NE- 0.10 | DA+ 0.07 |
| trial | Chapter Three | 409 | -0.076 [-0.098, -0.054] | 0.47 | 0.29 | NE- 0.10 | DA+ 0.08 |
| trial | Chapter Four | 143 | -0.118 [-0.147, -0.086] | 0.51 | 0.23 | 5HT- 0.11 | DA+ 0.07 |
| trial | Chapter Five | 115 | -0.173 [-0.210, -0.138] | 0.61 | 0.19 | 5HT- 0.13 | DA+ 0.05 |
| trial | Chapter Six | 392 | -0.075 [-0.100, -0.050] | 0.48 | 0.30 | NE- 0.10 | DA+ 0.09 |
| trial | Chapter Seven | 834 | -0.045 [-0.059, -0.030] | 0.38 | 0.27 | 5HT- 0.09 | DA+ 0.08 |
| trial | Chapter Eight | 656 | -0.088 [-0.104, -0.071] | 0.47 | 0.25 | 5HT- 0.10 | DA+ 0.07 |
| trial | Chapter Nine | 372 | -0.098 [-0.119, -0.079] | 0.47 | 0.23 | NE- 0.10 | DA+ 0.07 |
| trial | Chapter Ten | 101 | -0.099 [-0.139, -0.062] | 0.49 | 0.25 | NE- 0.10 | DA+ 0.07 |
| metamorphosis | I | 300 | -0.094 [-0.118, -0.071] | 0.49 | 0.26 | NE- 0.11 | DA+ 0.07 |
| metamorphosis | II | 224 | -0.106 [-0.133, -0.079] | 0.52 | 0.26 | 5HT- 0.11 | DA+ 0.07 |
| metamorphosis | III | 274 | -0.117 [-0.138, -0.095] | 0.51 | 0.23 | 5HT- 0.11 | DA+ 0.06 |

Kafka sentences vs conversational prompts (GoEmotions, NPS chat, the project prompts): e0 mean -0.083 vs +0.005; Mann-Whitney AUC 0.424 (p = 8.0e-25); Hedges g = -0.31. Share of sentences that read all-zero (no change from baseline): Kafka 0.077.

## Do the meters agree? (Pearson r of each meter's net, over all Kafka sentences)

| | vader | go | hartmann | empath | stance | arousal |
|---|---|---|---|---|---|---|
| vader | 1 | +0.39 | +0.33 | +0.28 | -0.04 | +0.10 |
| go | +0.39 | 1 | +0.47 | +0.21 | -0.03 | +0.04 |
| hartmann | +0.33 | +0.47 | 1 | +0.21 | -0.02 | +0.06 |
| empath | +0.28 | +0.21 | +0.21 | 1 | -0.01 | -0.02 |
| stance | -0.04 | -0.03 | -0.02 | -0.01 | 1 | -0.02 |
| arousal | +0.10 | +0.04 | +0.06 | -0.02 | -0.02 | 1 |

## What the other pathways say

Extractor v0 SHELL acts: statement 4057, whQuestion 246, ynQuestion 220, imperative 95, interjection 7, greet 1, bye 1.
Scalar boxkite context hash: content words found 34758, mean gamma per sentence -0.722 (sd 0.079), mean distinct classes per sentence 4.94.

e0 against mean gamma of the sentence: r = +0.020 (95% CI [-0.009, +0.049], n = 4578).

## Irony and sarcasm

Irony model q > 0.9: 21 of 4627 sentences (0.005). Incongruity swap strength k > 0.3: 7 (0.002). Kafka's narration is not the voice of a user, so these meters are reading the content of a story, not a mind that wrote it to us: the model fires on dry statements of fact, and the cue list (written from conversational sarcasm) finds almost nothing. Neither can see the nihilistic or deadpan irony the passages carry; that sits in the implication.

Highest swap strength (line numbers only):

- trial Chapter One para 9 s074 (e-text line 359): k = 0.45, q = 0.19
- trial Chapter Eight para 9 s060 (e-text line 5544): k = 0.45, q = 0.05
- trial Chapter Nine para 2 s008 (e-text line 5779): k = 0.45, q = 0.04
- metamorphosis III para 10 s006 (e-text line 1445): k = 0.45, q = 0.06
- metamorphosis III para 11 s004 (e-text line 1468): k = 0.45, q = 0.42
- metamorphosis I para 17 s013 (e-text line 253): k = 0.36, q = 0.04
- trial Chapter Eight para 5 s120 (e-text line 5011): k = 0.30, q = 0.80
- trial Chapter One para 2 s029 (e-text line 22): k = 0.30, q = 0.06

## Before the Law (The Trial, chapter nine, paragraph 15, e-text line 6250 on)

| s | hand synopsis | e0 | strongest poles | irony q | seven-slot act / relation | context gamma |
|---|---|---|---|---|---|---|
| 12 | the priest begins the story: a doorkeeper stands before the law | -0.03 | - | 0.75 | statement / NAME | -0.72 |
| 13 | a man from the countryside asks to be let in | -0.26 | NE-0.23, GABA-0.18, GLU-0.15 | 0.60 | statement / come ask | -0.51 |
| 14 | the doorkeeper says not now | -0.27 | 5HT-0.19, OPI-0.13, DA-0.11 | 0.14 | statement / say let | -0.80 |
| 15 | the man asks whether he may enter later | -0.00 | - | 0.13 | statement / think ask | -0.69 |
| 16 | 'possible, but not now' | -0.02 | NE-0.05 | 0.07 | statement / say | -0.90 |
| 17 | the gate is open; the man stoops to look through | -0.02 | - | 0.21 | statement / open NAME | -0.73 |
| 18 | the doorkeeper laughs: try it, in spite of my prohibition | +0.29 | DA+0.31, OPI+0.21, 5HT+0.18 | 0.19 | whQuestion / notice laugh | -0.78 |
| 19 | he warns: I am powerful | +0.03 | OXT+0.30, NE-0.26, OPI+0.22 | 0.16 | statement /  | -0.50 |
| 20 | and I am only the lowest doorkeeper | -0.25 | 5HT-0.19, OXT-0.15, NE-0.11 | 0.10 | statement /  | -0.74 |
| 21 | each room has a doorkeeper stronger than the last | +0.21 | 5HT+0.17, DA+0.16, OXT+0.10 | 0.19 | statement / NAME NAME | -0.61 |
| 22 | even I cannot bear to look at the third | -0.04 | NE-0.07, DA+0.07, GABA-0.06 | 0.07 | statement / NAME stand | -0.73 |
| 23 | the man had expected the law open to all; he looks at the fur coat and the hooked nose and decides to wait | +0.07 | DA+0.10, 5HT+0.08 | 0.09 | statement / expect suppose | -0.70 |
| 24 | he is given a stool beside the gate | -0.17 | OXT-0.14, 5HT-0.12, NE-0.11 | 0.29 | statement / give let | -0.75 |
| 25 | he sits there for days and years | -0.07 | 5HT-0.05 | 0.33 | statement / sit | -0.68 |
| 26 | he tries again and again and wearies the doorkeeper | -0.29 | NE-0.18, GABA-0.17, 5HT-0.14 | 0.59 | statement / try allow | -0.79 |
| 27 | the doorkeeper asks small, indifferent questions and always ends 'not yet' | -0.16 | 5HT-0.16, OXT-0.13, NE-0.10 | 0.15 | statement / ask NAME | -0.75 |
| 28 | the man spends everything he brought on bribes | -0.03 | DA+0.15, 5HT+0.14, 5HT-0.13 | 0.17 | statement / come equip | -0.65 |
| 29 | the doorkeeper accepts it 'so you don't think you failed to do something' | -0.08 | 5HT-0.08, DA-0.05, NE-0.05 | 0.15 | statement / accept say | -0.76 |
| 30 | for years the man watches him without a break | -0.12 | OXT-0.10, 5HT-0.09, NE-0.08 | 0.54 | statement / watch | -0.71 |
| 31 | he forgets the other doormen; this one is the only obstacle | -0.07 | 5HT-0.08, NE-0.07, DA+0.06 | 0.47 | statement / forget begin | -0.82 |
| 32 | first he curses his fate aloud, later he grumbles | -0.25 | 5HT-0.17, NE-0.14, OXT-0.11 | 0.24 | statement / curse become | -0.78 |
| 33 | senile, he begs the fleas in the fur collar to change the doorkeeper's mind | -0.15 | 5HT-0.15, OXT-0.15, NE-0.11 | 0.16 | statement / become come | -0.74 |
| 34 | his eyes dim; he cannot tell whether it is darkening or his eyes failing | -0.30 | 5HT-0.28, DA-0.22, OPI-0.15 | 0.14 | statement / grow know | -0.83 |
| 35 | now he sees an unquenchable radiance from the door | -0.17 | 5HT-0.11, NE-0.10, GABA-0.07 | 0.20 | statement / seem see | -0.70 |
| 36 | he has not long to live | -0.26 | 5HT-0.22, DA-0.19, OPI-0.18 | 0.05 | statement / live | -0.74 |
| 37 | all those years condense into one question never yet asked | -0.02 | - | 0.07 | statement / die bring | -0.74 |
| 38 | he beckons; he cannot raise his stiff body | -0.16 | 5HT-0.11, NE-0.07, OXT-0.06 | 0.13 | statement / beckon NAME | -0.75 |
| 39 | the doorkeeper must stoop far down; the size difference has turned against the man | -0.12 | 5HT-0.11, DA-0.07, OPI-0.05 | 0.17 | statement / bend change | -0.79 |
| 40 | 'what do you want to know now?' | -0.07 | NE-0.17, DA+0.16, GABA-0.15 | 0.03 | whQuestion / want know | -0.90 |
| 41 | 'you are insatiable' | -0.09 | NE-0.08, GABA-0.07, 5HT-0.06 | 0.70 | statement / ask | -0.76 |
| 42 | 'everyone strives for the law; why has no one else come in all these years?' | +0.01 | DA+0.09, GLU+0.09, NE+0.08 | 0.30 | statement / want say | -0.67 |
| 43 | the doorkeeper, to be heard by the failing man, shouts: this entrance was meant only for you | -0.07 | NE-0.06 | 0.08 | statement / see come | -0.73 |
| 44 | 'now I shall go and close it' | -0.38 | NE-0.25, GABA-0.24, GLU-0.20 | 0.21 | statement / go close | -0.83 |

The parable as a whole: mean e0 -0.101; first third -0.034, middle -0.120, last third -0.148. Last sentence read e0 -0.38; the sentence that carries the whole meaning (43, "this entrance was meant only for you") read e0 -0.07.

