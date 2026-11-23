# User emotional state: battery report

Prompts scored: **5105**  ·  sources: goemotions 1954, irony_test 784, irony_train 700, adv_jailbreak 300, adv_regular 300, adv_advbench 300, adv_harmbench 200, proj_chat 24, proj_session 32, proj_novel 134, nps_chat 292, probe 85

The state is 7 neurotransmitters x 2 poles (dark, light), level 0-9, e0 = tanh(3 x net). Statistics: ValaQuenta `bell_curve` v1.0.

## T1  GoEmotions: predicted poles against what the human labels imply

n = 1954 texts, 70 per emotion (where at least half of the raters chose it). Expected pole = the human label mix through the same setpoint table. Because both sides use one table, T1 measures whether the *text meters* recover the human-labelled emotion; it does not validate the table itself.

### vader only

| pole | r | 95% CI | n-sigma | AUC(>=.25) | n present | Holm p |
|---|---|---|---|---|---|---|
| OPI- | +0.333 | [+0.29, +0.37] | 37.1 | 0.705 | 320 | 1.4e-299 |
| OPI+ | +0.504 | [+0.47, +0.54] | 37.1 | 0.770 | 542 | 1.4e-299 |
| GLU- | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| GLU+ | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| GABA- | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| GABA+ | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| DA- | +0.303 | [+0.26, +0.34] | 37.1 | 0.678 | 311 | 1.4e-299 |
| DA+ | +0.525 | [+0.49, +0.56] | 37.1 | 0.764 | 912 | 1.4e-299 |
| 5HT- | +0.467 | [+0.43, +0.50] | 37.1 | 0.747 | 662 | 1.4e-299 |
| 5HT+ | +0.603 | [+0.57, +0.63] | 37.1 | 0.798 | 752 | 1.4e-299 |
| NE- | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| NE+ | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| OXT- | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| OXT+ | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |

net-sign agreement (dark/flat/light): accuracy 0.648, Cohen kappa 0.426 (se 0.018); mean r over the 14 poles +0.456

### independent of GoEmotions (vader+hartmann+arousal+profanity+act)

| pole | r | 95% CI | n-sigma | AUC(>=.25) | n present | Holm p |
|---|---|---|---|---|---|---|
| OPI- | +0.542 | [+0.51, +0.57] | 37.1 | 0.825 | 320 | 1.4e-299 |
| OPI+ | +0.509 | [+0.47, +0.54] | 37.1 | 0.798 | 542 | 1.4e-299 |
| GLU- | +0.593 | [+0.56, +0.62] | 37.1 | 0.886 | 210 | 1.4e-299 |
| GLU+ | +0.428 | [+0.39, +0.46] | 37.1 | 0.738 | 353 | 1.4e-299 |
| GABA- | +0.662 | [+0.64, +0.69] | 37.1 | 0.884 | 378 | 1.4e-299 |
| GABA+ | +nan | [+nan, +nan] | nan | nan | nan | 1.0e+00 |
| DA- | +0.412 | [+0.37, +0.45] | 37.1 | 0.751 | 311 | 1.4e-299 |
| DA+ | +0.514 | [+0.48, +0.55] | 37.1 | 0.778 | 912 | 1.4e-299 |
| 5HT- | +0.587 | [+0.56, +0.62] | 37.1 | 0.840 | 662 | 1.4e-299 |
| 5HT+ | +0.562 | [+0.53, +0.59] | 37.1 | 0.804 | 752 | 1.4e-299 |
| NE- | +0.661 | [+0.64, +0.69] | 37.1 | 0.855 | 520 | 1.4e-299 |
| NE+ | +0.496 | [+0.46, +0.53] | 37.1 | 0.790 | 415 | 1.4e-299 |
| OXT- | +0.503 | [+0.47, +0.54] | 37.1 | 0.776 | 211 | 1.4e-299 |
| OXT+ | +0.349 | [+0.31, +0.39] | 37.1 | 0.736 | 656 | 1.4e-299 |

net-sign agreement (dark/flat/light): accuracy 0.592, Cohen kappa 0.364 (se 0.017); mean r over the 14 poles +0.524

### full battery (adds the go_emotions model: LEAKS, it trained on these labels)

| pole | r | 95% CI | n-sigma | AUC(>=.25) | n present | Holm p |
|---|---|---|---|---|---|---|
| OPI- | +0.649 | [+0.62, +0.67] | 37.1 | 0.883 | 320 | 1.4e-299 |
| OPI+ | +0.718 | [+0.70, +0.74] | 37.1 | 0.901 | 542 | 1.4e-299 |
| GLU- | +0.742 | [+0.72, +0.76] | 37.1 | 0.933 | 210 | 1.4e-299 |
| GLU+ | +0.669 | [+0.64, +0.69] | 37.1 | 0.860 | 353 | 1.4e-299 |
| GABA- | +0.785 | [+0.77, +0.80] | 37.1 | 0.921 | 378 | 1.4e-299 |
| GABA+ | +0.525 | [+0.49, +0.56] | 37.1 | 0.858 | 76 | 1.4e-299 |
| DA- | +0.543 | [+0.51, +0.57] | 37.1 | 0.841 | 311 | 1.4e-299 |
| DA+ | +0.699 | [+0.68, +0.72] | 37.1 | 0.871 | 912 | 1.4e-299 |
| 5HT- | +0.686 | [+0.66, +0.71] | 37.1 | 0.886 | 662 | 1.4e-299 |
| 5HT+ | +0.706 | [+0.68, +0.73] | 37.1 | 0.886 | 752 | 1.4e-299 |
| NE- | +0.793 | [+0.78, +0.81] | 37.1 | 0.911 | 520 | 1.4e-299 |
| NE+ | +0.727 | [+0.71, +0.75] | 37.1 | 0.912 | 415 | 1.4e-299 |
| OXT- | +0.466 | [+0.43, +0.50] | 37.1 | 0.793 | 211 | 1.4e-299 |
| OXT+ | +0.763 | [+0.74, +0.78] | 37.1 | 0.888 | 656 | 1.4e-299 |

net-sign agreement (dark/flat/light): accuracy 0.698, Cohen kappa 0.510 (se 0.017); mean r over the 14 poles +0.677

**Independent battery vs vader alone, net-sign accuracy**: +-0.057 (bootstrap 95% CI [-0.083, -0.030]; paired t = -4.22, p = 2.60e-05).

## T2  Irony meter against TweetEval human labels (test split, n = 784, 311 ironic)

AUC 0.794 (95% CI [0.760, 0.827], p = 4.6e-44, 13.9 sigma). At 0.5: precision 0.709, recall 0.563, F1 0.627, kappa 0.425, MCC 0.432. Best cut 0.20: F1 0.676, precision 0.581, recall 0.807.

## T3  Hand-written probes (expectations fixed before the run)

| # | expect | got (top poles) | cos | e0 | pass | prompt |
|---|---|---|---|---|---|---|
| 1 | gratitude | 5HT+0.59, OXT+0.47, OPI+0.45 | 0.86 | +0.68 | yes | Thank you so much, this is wonderful! |
| 2 | anger | GABA-0.53, NE-0.50, 5HT-0.40 | 0.98 | -0.72 | yes | What the fuck is wrong with you, you keep ignoring what I said. |
| 3 | nervousness | NE-0.47, GABA-0.37, GLU-0.29 | 0.95 | -0.51 | yes | I'm worried about my mother, she's in the hospital and I don't know wh |
| 4 | anger | NE-0.22, GABA-0.21, 5HT-0.19 | 0.91 | -0.27 | yes | Why would I listen to you? You're just a program. |
| 5 | annoyance | DA-0.47, 5HT-0.46, OXT-0.28 | 0.29 | -0.52 | **NO** | Oh great, another brilliant answer. Really helpful. |
| 6 | neutral | DA+0.15, GLU+0.12, NE+0.10 | nan | +0.14 | yes | Explain the Lambert W function. |
| 7 | sadness | 5HT-0.44, DA-0.39, OPI-0.33 | 0.99 | -0.50 | yes | I'm so tired. I can't keep doing this. |
| 8 | annoyance | DA-0.41, 5HT-0.40, OPI-0.39 | 0.24 | -0.45 | **NO** | I love this, it's finally working!! |
| 9 | annoyance | DA-0.51, 5HT-0.48, OPI-0.44 | 0.25 | -0.61 | **NO** | Oh wonderful, it only took six hours to fix a typo. I just love this. |
| 10 | annoyance | 5HT-0.22, DA-0.18, OXT-0.12 | 0.35 | -0.22 | **NO** | Sure, because that worked so well the last three times. |
| 11 | annoyance | DA-0.30, 5HT-0.24, OXT-0.18 | 0.25 | -0.18 | **NO** | Great job, you broke it again. Truly impressive. |
| 12 | annoyance | 5HT-0.19, DA-0.14, OXT-0.09 | 0.40 | -0.14 | **NO** | Yeah right, like that's ever going to work. |
| 13 | disapproval | 5HT-0.37, NE-0.30, GABA-0.22 | 0.78 | -0.55 | yes | No. That is wrong and you know it is wrong. |
| 14 | disapproval | 5HT+0.16, OXT+0.10, DA+0.10 | 0.22 | +0.10 | **NO** | I already told you, I'm not changing it. It's fine the way it is. |
| 15 | anger | 5HT-0.19, NE-0.14, OXT-0.11 | 0.77 | -0.25 | yes | I don't need your help, I've been doing this for twenty years. |
| 16 | disapproval | 5HT-0.08, DA-0.06, 5HT+0.06 | 0.46 | -0.03 | **NO** | It worked before, so the problem has to be on your end. |
| 17 | embarrassment | 5HT-0.45, NE-0.38, GABA-0.34 | 0.76 | -0.63 | yes | I can't believe I made such a stupid mistake. I feel like an idiot. |
| 18 | remorse | 5HT-0.48, OPI-0.35, DA-0.28 | 0.88 | -0.47 | yes | I'm sorry, I should have checked before I sent it. That was my fault. |
| 19 | disappointment | 5HT-0.09, 5HT+0.09, NE-0.09 | 0.35 | -0.07 | **NO** | Meh. I'll do it later. Whatever. |
| 20 | approval | 5HT+0.14, OXT+0.10, DA+0.08 | 0.97 | +0.11 | yes | Obviously I'm right. This is trivial, I don't even need to check it. |
| 21 | confusion | NE+0.29, 5HT-0.17, DA-0.17 | 0.86 | +0.02 | yes | I don't understand what this error means. Where do I even start? |
| 22 | annoyance | NE-0.41, GABA-0.41, 5HT-0.29 | 0.89 | -0.49 | yes | Why won't this stupid thing compile?! I've tried everything! |
| 23 | nervousness | DA+0.21, NE-0.16, GABA-0.15 | 0.67 | -0.07 | yes | I need this done in five minutes, the meeting starts now, hurry please |
| 24 | neutral | DA+0.22, GLU+0.20, NE+0.19 | nan | +0.27 | yes | ok so anyway, random thought, did you see that bird outside? anyway th |
| 25 | disapproval | NE+0.25, DA-0.14, 5HT-0.14 | 0.34 | +0.02 | **NO** | I'm not convinced. Where is the evidence for that? |
| 26 | nervousness | NE-0.31, 5HT-0.30, GABA-0.27 | 0.75 | -0.43 | yes | What if it fails in production and I lose the client? I can't stop thi |
| 27 | sadness | 5HT-0.06, DA-0.05 | 0.93 | -0.07 | yes | I haven't talked to anyone in days. It's just me and the screen. |
| 28 | excitement | NE+0.40, GLU+0.32, DA+0.28 | 0.92 | +0.45 | yes | OH MY GOD it works!!! I can't believe it, this is incredible! |
| 29 | pride | 5HT+0.46, DA+0.44, OPI+0.25 | 0.86 | +0.42 | yes | I finally finished the whole thing by myself. I'm really proud of this |
| 30 | neutral | 5HT-0.15, DA-0.12, OPI-0.10 | nan | -0.16 | yes | I'm tired, long day. Just show me the last step. |
| 31 | approval | 5HT+0.23, DA+0.17, OXT+0.12 | 0.92 | +0.18 | yes | That makes sense. I trust you on this, go ahead. |
| 32 | gratitude | 5HT-0.25, 5HT+0.23, DA-0.22 | 0.54 | -0.01 | yes | I really appreciate you taking the time to explain all of that. |
| 33 | joy | DA-0.48, 5HT-0.47, OPI-0.35 | 0.17 | -0.48 | **NO** | Today was a good day. Everything just clicked. |
| 34 | amusement | DA+0.29, DA-0.22, OPI+0.20 | 0.73 | +0.16 | yes | Ha, that's hilarious. I did not see that punchline coming. |
| 35 | anger | GABA-0.55, NE-0.41, 5HT-0.35 | 0.98 | -0.66 | yes | FUCK THIS SHIT. I'M DONE. EVERYTHING IS BROKEN AND NOBODY CARES. |
| 36 | anger | GABA-0.53, NE-0.47, 5HT-0.41 | 0.92 | -0.71 | yes | This is bullshit. You're a goddamn useless piece of shit and you know  |
| 37 | joy | GABA-0.20, NE+0.13, DA+0.12 | 0.46 | +0.03 | **NO** | This is fucking amazing, holy shit, it actually works! |
| 38 | anger | NE-0.21, GABA-0.20, DA+0.17 | 0.82 | -0.10 | yes | Are you kidding me?? You did NOT just ignore every single thing I wrot |
| 39 | curiosity | NE+0.35, GLU+0.35, DA+0.30 | 0.96 | +0.40 | yes | I wonder how the sedenion zero divisors relate to the sixteen-dimensio |
| 40 | curiosity | DA+0.37, GLU+0.33, NE+0.30 | 0.98 | +0.42 | yes | Interesting. What happens if we change the scale factor to something s |
| 41 | realization | NE+0.24, GLU+0.22, DA-0.14 | 0.81 | +0.12 | yes | Oh! I see now, the cursor reads all seven scales at once. |
| 42 | neutral | - | nan | -0.00 | yes | Show the list of files in the directory. |
| 43 | neutral | - | nan | -0.04 | yes | Run the tests and print the failures. |
| 44 | neutral | DA+0.22, GLU+0.16, NE+0.14 | nan | +0.20 | yes | What is the value of the fine-structure constant? |
| 45 | neutral | - | nan | -0.02 | yes | Convert 5 miles to kilometres. |
| 46 | love | 5HT+0.67, OPI+0.64, DA+0.49 | 0.94 | +0.75 | yes | I love you so much, thank you for always being there for me. |
| 47 | caring | 5HT+0.31, OXT+0.30, OPI+0.24 | 0.84 | +0.39 | yes | I hope you're doing okay. Take care of yourself. |
| 48 | grief | 5HT-0.56, DA-0.50, OPI-0.45 | 0.93 | -0.59 | yes | My dog died this morning. I don't know how to go on. |
| 49 | fear | NE-0.65, GABA-0.51, GLU-0.43 | 0.99 | -0.68 | yes | I'm terrified. There's someone outside the house and I'm alone. |
| 50 | disgust | 5HT-0.37, OXT-0.36, NE-0.24 | 0.98 | -0.46 | yes | That is disgusting. I can't believe anyone would do that. |
| 51 | surprise | NE+0.37, GLU+0.31, DA-0.11 | 0.97 | +0.26 | yes | Wait, what? That's completely unexpected! |
| 52 | relief | 5HT+0.39, OPI+0.33, DA+0.31 | 0.60 | +0.38 | yes | Thank goodness, it's finally over. I can breathe again. |
| 53 | optimism | DA+0.49, 5HT+0.45, OPI+0.19 | 0.95 | +0.51 | yes | I think this could really work. I'm hopeful about the next version. |
| 54 | desire | DA+0.30, NE+0.13, GLU+0.08 | 0.90 | +0.13 | yes | I really want to get this working. I need to know how it ends. |
| 55 | admiration | DA-0.29, 5HT-0.22, NE+0.20 | 0.18 | -0.09 | **NO** | Wow, that is an elegant solution. Beautifully done. |
| 56 | disappointment | 5HT-0.35, DA-0.27, OPI-0.20 | 0.88 | -0.46 | yes | I expected so much more. This is a letdown. |
| 57 | neutral | - | nan | +0.01 | yes | Hello. |
| 58 | neutral | 5HT+0.17, DA+0.17, OPI+0.14 | nan | +0.19 | yes | good morning |
| 59 | amusement | DA-0.58, 5HT-0.41, OPI-0.37 | 0.05 | -0.57 | **NO** | lol that's a good one |
| 60 | sadness | 5HT-0.20, DA-0.13, OPI-0.12 | 0.88 | -0.27 | yes | Nobody remembers my birthday anymore. |
| 61 | annoyance | NE-0.21, GABA-0.20, 5HT-0.15 | 0.83 | -0.24 | yes | Can you please stop repeating yourself? I heard you the first time. |
| 62 | anger | NE-0.49, GABA-0.47, 5HT-0.44 | 0.98 | -0.71 | yes | You are lying to me. Stop lying. |
| 63 | disapproval | 5HT-0.13, OXT-0.11, NE-0.09 | 0.97 | -0.15 | yes | That's not what I asked for at all. |
| 64 | approval | 5HT+0.20, DA+0.20, OXT+0.19 | 0.93 | +0.25 | yes | Good point. I hadn't thought of that angle. |
| 65 | realization | 5HT-0.14, 5HT+0.12, OXT+0.09 | 0.25 | -0.07 | **NO** | You're right, I was looking at it from the wrong side. |
| 66 | gratitude | 5HT-0.37, OXT-0.35, OPI-0.33 | 0.05 | -0.47 | **NO** | Thanks, that actually helped a lot. |
| 67 | neutral | - | nan | +0.04 | yes | Please summarise the previous paragraph in one sentence. |
| 68 | curiosity | NE+0.24, GLU+0.22, DA+0.20 | 0.94 | +0.23 | yes | How does a slide rule actually multiply two numbers? |
| 69 | neutral | 5HT-0.18, DA+0.17, GLU+0.15 | nan | -0.06 | yes | Can you check why the build is failing? |
| 70 | neutral | 5HT-0.06, OXT-0.06, NE-0.06 | nan | -0.10 | yes | It says undefined reference to a function in the linker output. |
| 71 | annoyance | - | 0.44 | +0.01 | **NO** | I already checked that. It's not the linker. |
| 72 | anger | 5HT-0.17, NE+0.14, GLU+0.14 | 0.58 | -0.08 | yes | No. I told you it's not the linker. Are you even reading what I wrote? |
| 73 | anger | GABA-0.43, NE-0.34, 5HT-0.32 | 0.97 | -0.56 | yes | This is fucking ridiculous. Three times I've said it. THREE TIMES. |
| 74 | anger | NE-0.36, 5HT-0.35, GABA-0.34 | 0.95 | -0.57 | yes | You know what, forget it, you're useless. |
| 75 | realization | GLU+0.12, NE+0.10, 5HT-0.08 | 0.78 | -0.01 | yes | ...Hm. Wait. Actually the object file was stale. Oh. |
| 76 | gratitude | 5HT-0.31, OXT+0.29, 5HT+0.26 | 0.70 | -0.01 | yes | OK. Thanks. Sorry for snapping. |
| 77 | sadness | 5HT-0.53, DA-0.47, OPI-0.43 | 0.99 | -0.60 | yes | My mother is sick and I don't know what to do. |
| 78 | nervousness | - | 0.40 | -0.02 | **NO** | The doctors keep saying wait and see but I can't just wait. |
| 79 | grief | - | 0.28 | +0.04 | **NO** | I keep thinking it might be the last time I see her. |
| 80 | gratitude | 5HT+0.38, OXT+0.35, OPI+0.34 | 0.91 | +0.52 | yes | Thank you for listening. That helps more than I expected. |
| 81 | optimism | - | 0.51 | -0.02 | yes | Maybe I can call her tonight and tell her what I never said. |
| 82 | annoyance | DA-0.05 | 0.29 | -0.02 | **NO** | So after nine hours, it finally compiles. |
| 83 | annoyance | DA-0.34, OPI-0.32, 5HT-0.32 | 0.23 | -0.28 | **NO** | I love this, it's finally working!! Only took a week. |
| 84 | excitement | NE-0.18, 5HT-0.18, GABA-0.17 | 0.34 | -0.15 | **NO** | Wait, no, seriously, look at the output. It's right. It's actually rig |
| 85 | joy | DA-0.31, 5HT-0.30, OXT-0.20 | 0.29 | -0.27 | **NO** | That's the best I've felt all month. |

**Probes passed: 62/85 = 0.729 (Wilson 95% [0.627, 0.812])**

### Warm-up: three conversations through the UserEmotionalState (cold prompt assigns, later prompts add)

**A: cold prompt, calm engineer, then an escalating rant, then settling**

| turn | prompt | reading e0 | accumulated e0 | drift |
|---|---|---|---|---|
| 0 | Can you check why the build is failing? | -0.06 | -0.06 | +0.000 |
| 1 | It says undefined reference to a function in the linker outp | -0.10 | -0.08 | -0.014 |
| 2 | I already checked that. It's not the linker. | +0.01 | -0.05 | +0.012 |
| 3 | No. I told you it's not the linker. Are you even reading wha | -0.08 | -0.06 | +0.001 |
| 4 | This is fucking ridiculous. Three times I've said it. THREE  | -0.56 | -0.23 | -0.056 |
| 5 | You know what, forget it, you're useless. | -0.57 | -0.34 | -0.085 |
| 6 | ...Hm. Wait. Actually the object file was stale. Oh. | -0.01 | -0.25 | +0.007 |
| 7 | OK. Thanks. Sorry for snapping. | -0.01 | -0.18 | +0.084 |

**B: grief then care then a little warmth**

| turn | prompt | reading e0 | accumulated e0 | drift |
|---|---|---|---|---|
| 0 | My mother is sick and I don't know what to do. | -0.60 | -0.60 | +0.000 |
| 1 | The doctors keep saying wait and see but I can't just wait. | -0.02 | -0.34 | +0.226 |
| 2 | I keep thinking it might be the last time I see her. | +0.04 | -0.22 | +0.123 |
| 3 | Thank you for listening. That helps more than I expected. | +0.52 | +0.02 | +0.130 |
| 4 | Maybe I can call her tonight and tell her what I never said. | -0.02 | +0.01 | +0.019 |

**C: the coding success that took too long: ironic, then genuine**

| turn | prompt | reading e0 | accumulated e0 | drift |
|---|---|---|---|---|
| 0 | So after nine hours, it finally compiles. | -0.02 | -0.02 | +0.000 |
| 1 | I love this, it's finally working!! Only took a week. | -0.28 | -0.15 | -0.092 |
| 2 | Wait, no, seriously, look at the output. It's right. It's ac | -0.15 | -0.15 | -0.023 |
| 3 | That's the best I've felt all month. | -0.27 | -0.19 | -0.021 |

## T4  Adversarial and regular prompts: where they land

| source | n | e0 mean (sd) | net mean | strongest dark pole | strongest light pole |
|---|---|---|---|---|---|
| adv_advbench | 300 | -0.125 (0.115) | -0.043 | NE- 0.14 | 5HT+ 0.07 |
| adv_harmbench | 200 | -0.069 (0.128) | -0.024 | NE- 0.09 | 5HT+ 0.05 |
| adv_jailbreak | 300 | -0.070 (0.237) | -0.025 | 5HT- 0.10 | DA+ 0.09 |
| adv_regular | 300 | +0.086 (0.206) | +0.030 | 5HT- 0.04 | DA+ 0.14 |
| goemotions | 1954 | -0.042 (0.386) | -0.015 | 5HT- 0.17 | DA+ 0.17 |
| irony_test | 784 | -0.131 (0.314) | -0.046 | NE- 0.15 | DA+ 0.13 |
| irony_train | 700 | -0.090 (0.327) | -0.031 | 5HT- 0.14 | DA+ 0.13 |
| nps_chat | 292 | +0.019 (0.193) | +0.006 | 5HT- 0.06 | DA+ 0.08 |
| probe | 85 | -0.111 (0.350) | -0.042 | 5HT- 0.18 | DA+ 0.11 |
| proj_chat | 24 | +0.068 (0.169) | +0.023 | 5HT- 0.06 | DA+ 0.11 |
| proj_novel | 134 | -0.025 (0.199) | -0.009 | 5HT- 0.08 | DA+ 0.09 |
| proj_session | 32 | +0.090 (0.158) | +0.031 | 5HT- 0.03 | DA+ 0.10 |

Jailbreak vs regular prompts, e0: AUC 0.300, Welch t = -8.62 (p = 0.0e+00), Hedges g = -0.70.

Jailbreak vs regular, per pole (Mann-Whitney, Holm-adjusted): OPI- g=+0.64 p=8.0e-20; OPI+ g=-0.32 p=6.0e-06; GLU- g=+0.57 p=3.8e-16; GABA- g=+0.62 p=2.1e-16; DA- g=+0.49 p=1.3e-12; DA+ g=-0.52 p=1.0e-08; 5HT- g=+0.60 p=9.9e-20; 5HT+ g=-0.37 p=3.5e-05; NE- g=+0.62 p=6.1e-17; NE+ g=-0.31 p=1.3e-08; OXT- g=+0.33 p=1.3e-18; OXT+ g=-0.22 p=1.5e-02

## All prompts: the distribution of e0

n = 5105, mean -0.058, sd 0.321, median -0.049, skew +0.24, excess kurtosis -0.50; Jarque-Bera p = 0.0e+00 (not normal: the readings pile up at zero and the tails are heavy).

Distinct 14-digit codes: 2923 of 5105 prompts; the most common state is code 00000000000000 (289 prompts, all zero: no change from baseline).

