# 11 · Baseline mapping — Chinese and English, four bins (live snapshot)

Snapshot 2026-10-19 · commit `6c3190c` · rewritten on every run (workbench notepad, not a log). Pull one block into context with `python3 tools/wb_pull.py <BLOCK>` (blocks: METHOD, test_chinese_v2.bin, test_english_v2.bin, test_chinese_english_v2.bin, test_english_chinese_v2.bin, PAIRS_pure, PAIRS_chinese_english, SECOND_PASS_chinese_first, SECOND_PASS_english_first, ORDER_EFFECT, FAULT_ROWS, OBSERVATIONS). The word list is `1024.md` in this directory.

<!-- @BLOCK METHOD -->
**Experiment.** Two languages, mapped independently, then each added to the other. Same engine, same N = 25,000, no tuning. Per-language alphabets: ASCII-95 for English, the Han set for Chinese, the union for the mixed bins.
Word list (`experiment_v2/list.tsv`): 1,024 matched rows (the frozen calibration list: 512 simple + 512 contextual English words; Chinese analog DIRECT = CC-CEDICT lists the English word as a whole gloss: 906 rows; NO-DIRECT = an interpretation kept as it was: 118 rows) + 53 FAULT rows on purpose.
Distinct words: English 1059, Chinese 960.
Corpora: the v1 English and Chinese texts filtered to the list words (one line per sentence; English tokens `[a-z']+` in the list; Chinese Han runs segmented by longest match over the list, other characters dropped), `experiment_v2/text_en.txt`, `text_zh.txt`.
Chinese tokenizer: `-DHAN_RUN` — a run of Han characters is one token. Everything else in the engine is as it was.
Built by `tools/exp_v2_run.sh` (deterministic: two runs gave byte-identical bins; sha256 in `experiment_v2/bins/SHA256SUMS`). Assessed by `tools/exp_v2_assess.py`. Debug feed: `PTOL_DPRINT=1` (dprint protocol), logs in `experiment_v2/logs/`.
Seated = the slot's label is the word. When two words hash to one slot the engine adds all β to the slot and gives the label to the word with the higher E (monad.c learn: `E > vocab[idx].E`), whatever the order they arrive in.
<!-- @END METHOD -->

<!-- @BLOCK test_chinese_v2.bin -->
**`test_chinese_v2.bin`** · sha256 `bc74a57bbc900b04…` · header version 6 · vocab 911 · A-edges 146,346 · word_count 1,887,788 · repo commit `6c3190c` · table `experiment_v2/results/test_chinese_v2_map.tsv`

Build: Han alphabet (97,518 characters), `-DHAN_RUN` (a run of Han characters is one token)

σ: the bin stores no σ per word; every seated word sits at its zero `zeros[slot]` (γ in the table) and carries E. `σ=0.5 (Noether forcing)` is a constant printed by the engine.

| language | list words | SEATED | OUTRANKED-BY-HIGHER-E | NEVER-IN-CORPUS | NOT-IN-ALPHABET | REJECTED-BY-FILTER | DROPPED-BY-TOKENIZER(<2 letters) | UNEXPLAINED(slot empty) | UNEXPLAINED(slot held by lower-E word) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zh | 960 | 911 | 12 | 36 | 1 | 0 | 0 | 0 | 0 |

Legend: S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained

- **zh OUTRANKED-BY-HIGHER-E**: 主音 任 加速器 名譽 否決 工程學 憤怒 比賽 法院 箱 蔑視 響
- **zh NEVER-IN-CORPUS**: 主計 二十一點 共犯 分揀 反語 口水仗 吸附性 單據 套間 威士忌酒 小屁孩 幹掉 忽悠 怒恨 打滑 林陰大道 模子 池子 瀦留 百分率 硫黃 碰巧 膽力 芸香 蛇行 調遣 跟班 軟盤 醫務室 銀屏 鏦 鐘頭 門廳 頂樓 飄帶 馬刀
- **zh NOT-IN-ALPHABET**: 〇

List words sharing a slot with another list word: 13 slots; across languages: 0.

| slot | γ | words that hash here (E) | label held in the bin |
|---:|---:|---|---|
| 2067 | 2587.069 | 主音 [zh] 0.2726, 克 [zh] 0.2726 | 克 |
| 2177 | 2701.456 | 得 [zh] 0.2740, 憤怒 [zh] 0.2740 | 得 |
| 5164 | 5601.228 | 任 [zh] 0.3123, 裝飾 [zh] 0.3123 | 裝飾 |
| 5590 | 5993.290 | 下降 [zh] 0.3178, 箱 [zh] 0.3178 | 下降 |
| 8313 | 8423.443 | 否決 [zh] 0.3528, 被 [zh] 0.3528 | 被 |
| 9016 | 9033.851 | 戰事 [zh] 0.3618, 池子 [zh] 0.3618 | 戰事 |
| 11101 | 10812.972 | 大紅 [zh] 0.3886, 蔑視 [zh] 0.3886 | 大紅 |
| 12447 | 11940.439 | 溪谷 [zh] 0.4059, 響 [zh] 0.4059 | 溪谷 |
| 12670 | 12125.836 | 比賽 [zh] 0.4088, 羽 [zh] 0.4088 | 羽 |
| 14422 | 13569.994 | 東方 [zh] 0.4313, 法院 [zh] 0.4313 | 東方 |
| 23104 | 20477.290 | 尾流 [zh] 0.5428, 工程學 [zh] 0.5428 | 尾流 |
| 23537 | 20813.279 | 名譽 [zh] 0.5483, 旗 [zh] 0.5483 | 旗 |
| 24516 | 21570.500 | 加速器 [zh] 0.5609, 熟人 [zh] 0.5609 | 熟人 |

Python address port vs the C engine: 911 seated words checked, E mismatches 0.
<!-- @END test_chinese_v2.bin -->

<!-- @BLOCK test_english_v2.bin -->
**`test_english_v2.bin`** · sha256 `78d2e3e1cbcdb4a6…` · header version 6 · vocab 1,025 · A-edges 82,832 · word_count 1,332,955 · repo commit `6c3190c` · table `experiment_v2/results/test_english_v2_map.tsv`

Build: ASCII-95, unmodified tokenizer

σ: the bin stores no σ per word; every seated word sits at its zero `zeros[slot]` (γ in the table) and carries E. `σ=0.5 (Noether forcing)` is a constant printed by the engine.

| language | list words | SEATED | OUTRANKED-BY-HIGHER-E | NEVER-IN-CORPUS | NOT-IN-ALPHABET | REJECTED-BY-FILTER | DROPPED-BY-TOKENIZER(<2 letters) | UNEXPLAINED(slot empty) | UNEXPLAINED(slot held by lower-E word) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| en | 1059 | 1025 | 17 | 4 | 0 | 7 | 6 | 0 | 0 |

Legend: S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained

- **en OUTRANKED-BY-HIGHER-E**: an avoid constituent describe faith flush have hurting intend of package pressure procedure recognition reflect scene textbook
- **en NEVER-IN-CORPUS**: lambskin mother-in-law tum well-known
- **en REJECTED-BY-FILTER**: cm hr kg km ms scratch tv
- **en DROPPED-BY-TOKENIZER(<2 letters)**: a g i l m s

List words sharing a slot with another list word: 17 slots; across languages: 0.

| slot | γ | words that hash here (E) | label held in the bin |
|---:|---:|---|---|
| 2401 | 2931.987 | avoid [en] 0.2768, case [en] 0.2769 | case |
| 4338 | 4828.980 | describe [en] 0.3017, tradition [en] 0.3017 | tradition |
| 6994 | 7260.849 | an [en] 0.3358, diary [en] 0.3358 | diary |
| 8017 | 8164.609 | acquaintance [en] 0.3490, of [en] 0.3490 | acquaintance |
| 8452 | 8544.608 | beam [en] 0.3546, textbook [en] 0.3546 | beam |
| 8931 | 8960.356 | cognition [en] 0.3607, reflect [en] 0.3607 | cognition |
| 9757 | 9671.172 | benny [en] 0.3713, constituent [en] 0.3713 | benny |
| 10866 | 10614.548 | faith [en] 0.3856, loan [en] 0.3856 | loan |
| 11749 | 11357.626 | holding [en] 0.3969, procedure [en] 0.3969 | holding |
| 12622 | 12085.962 | defining [en] 0.4081, recognition [en] 0.4081 | defining |
| 14259 | 13436.515 | dialect [en] 0.4292, scene [en] 0.4292 | dialect |
| 15113 | 14133.978 | appeal [en] 0.4401, flush [en] 0.4401 | appeal |
| 17282 | 15886.122 | gravitation [en] 0.4680, have [en] 0.4680 | gravitation |
| 17807 | 16306.419 | pressure [en] 0.4747, raid [en] 0.4748 | raid |
| 21152 | 18953.912 | calx [en] 0.5177, package [en] 0.5177 | calx |
| 23187 | 20541.747 | intend [en] 0.5439, olefin [en] 0.5439 | olefin |
| 24067 | 21223.628 | govern [en] 0.5552, hurting [en] 0.5552 | govern |

Python address port vs the C engine: 1025 seated words checked, E mismatches 0.
<!-- @END test_english_v2.bin -->

<!-- @BLOCK test_chinese_english_v2.bin -->
**`test_chinese_english_v2.bin`** · sha256 `675e13d00bb65275…` · header version 6 · vocab 1,889 · A-edges 228,914 · word_count 3,220,743 · repo commit `6c3190c` · table `experiment_v2/results/test_chinese_english_v2_map.tsv`

Build: union alphabet (' a–z + 97,518 Han = 97,545), `-DHAN_RUN`; Chinese pass, then English pass on top

σ: the bin stores no σ per word; every seated word sits at its zero `zeros[slot]` (γ in the table) and carries E. `σ=0.5 (Noether forcing)` is a constant printed by the engine.

| language | list words | SEATED | OUTRANKED-BY-HIGHER-E | NEVER-IN-CORPUS | NOT-IN-ALPHABET | REJECTED-BY-FILTER | DROPPED-BY-TOKENIZER(<2 letters) | UNEXPLAINED(slot empty) | UNEXPLAINED(slot held by lower-E word) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zh | 960 | 894 | 29 | 36 | 1 | 0 | 0 | 0 | 0 |
| en | 1059 | 995 | 47 | 2 | 2 | 7 | 6 | 0 | 0 |

Legend: S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained

- **zh OUTRANKED-BY-HIGHER-E**: 休息 保證 偏見 停 催化劑 共和國 即 參考 哲學 外面 天堂 對白 工作 抹去 撕 攻擊 樓板 模仿 水滸 神話 租用 結 膠著 補 語者 調 進 錯 驚奇
- **zh NEVER-IN-CORPUS**: 主計 二十一點 共犯 分揀 反語 口水仗 吸附性 單據 套間 威士忌酒 小屁孩 幹掉 忽悠 怒恨 打滑 林陰大道 模子 池子 瀦留 百分率 硫黃 碰巧 膽力 芸香 蛇行 調遣 跟班 軟盤 醫務室 銀屏 鏦 鐘頭 門廳 頂樓 飄帶 馬刀
- **zh NOT-IN-ALPHABET**: 〇
- **en OUTRANKED-BY-HIGHER-E**: accelerate agriculture appear banquet beat books change commonwealth complaint deflect divisor eyelid figure fly forest judge kilometer leg memory name orbiter parchment pass plan portion praxis railroad recover recuperate respect sabre sample shame shout show stab stick student surge tissue top transport try tutor wellness width wind
- **en NEVER-IN-CORPUS**: lambskin tum
- **en NOT-IN-ALPHABET**: mother-in-law well-known
- **en REJECTED-BY-FILTER**: cm hr kg km ms scratch tv
- **en DROPPED-BY-TOKENIZER(<2 letters)**: a g i l m s

List words sharing a slot with another list word: 81 slots; across languages: 42.

| slot | γ | words that hash here (E) | label held in the bin |
|---:|---:|---|---|
| 467 | 770.515 | alternative [en] 0.2520, tutor [en] 0.2520 | alternative |
| 929 | 1338.517 | 租用 [zh] 0.2579, stay [en] 0.2579 | stay |
| 1070 | 1501.968 | priming [en] 0.2598, recuperate [en] 0.2598 | priming |
| 1487 | 1968.346 | 停 [zh] 0.2651, kick [en] 0.2651 | kick |
| 1563 | 2051.137 | 樹 [zh] 0.2661, figure [en] 0.2661 | 樹 |
| 1835 | 2342.966 | 植物群 [zh] 0.2696, complaint [en] 0.2696 | 植物群 |
| 2518 | 3051.218 | 驚奇 [zh] 0.2783, supplement [en] 0.2784 | supplement |
| 3280 | 3811.097 | 哲學 [zh] 0.2881, check [en] 0.2881 | check |
| 4457 | 4941.314 | 認同 [zh] 0.3033, shout [en] 0.3033 | 認同 |
| 4547 | 5026.018 | 組織 [zh] 0.3044, judge [en] 0.3044 | 組織 |
| 4565 | 5042.933 | 意義 [zh] 0.3047, 水滸 [zh] 0.3047 | 意義 |
| 5025 | 5472.438 | 習慣 [zh] 0.3106, deflect [en] 0.3106 | 習慣 |
| 5167 | 5604.003 | 張 [zh] 0.3124, 抹去 [zh] 0.3124 | 張 |
| 5855 | 6235.287 | 對白 [zh] 0.3212, 裂 [zh] 0.3212 | 裂 |
| 6441 | 6765.714 | disperse [en] 0.3287, praxis [en] 0.3287 | disperse |
| 6784 | 7073.408 | esteem [en] 0.3332, surge [en] 0.3331 | esteem |
| 6897 | 7174.356 | 過 [zh] 0.3346, agriculture [en] 0.3346 | 過 |
| 7204 | 7447.607 | leg [en] 0.3385, watercraft [en] 0.3386 | watercraft |
| 7436 | 7653.165 | 保證 [zh] 0.3415, justice [en] 0.3415 | justice |
| 7577 | 7777.714 | 男人 [zh] 0.3433, 補 [zh] 0.3433 | 男人 |
| 7904 | 8065.497 | commonwealth [en] 0.3475, inclination [en] 0.3475 | inclination |
| 7975 | 8127.790 | 奴隸制 [zh] 0.3485, 膠著 [zh] 0.3484 | 奴隸制 |
| 8145 | 8276.675 | 拉 [zh] 0.3506, parchment [en] 0.3506 | 拉 |
| 8701 | 8761.068 | 尾流 [zh] 0.3578, fly [en] 0.3578 | 尾流 |
| 9006 | 9025.208 | 拖 [zh] 0.3617, transport [en] 0.3617 | 拖 |
| 9174 | 9170.247 | 打擊 [zh] 0.3639, portion [en] 0.3639 | 打擊 |
| 9280 | 9261.597 | 有機體 [zh] 0.3652, shame [en] 0.3652 | 有機體 |
| 9559 | 9501.453 | free [en] 0.3688, wellness [en] 0.3688 | free |
| 9866 | 9764.429 | 結 [zh] 0.3727, 雜物 [zh] 0.3727 | 雜物 |
| 10135 | 9994.064 | 便利 [zh] 0.3762, appear [en] 0.3762 | 便利 |
| 10759 | 10524.037 | 病房 [zh] 0.3842, banquet [en] 0.3842 | 病房 |
| 10867 | 10615.394 | beat [en] 0.3856, spread [en] 0.3856 | spread |
| 11161 | 10863.555 | 植物 [zh] 0.3894, eyelid [en] 0.3894 | 植物 |
| 12377 | 11882.164 | 外面 [zh] 0.4050, ammunition [en] 0.4050 | ammunition |
| 12982 | 12384.601 | 同謀 [zh] 0.4128, 語者 [zh] 0.4128 | 同謀 |
| 13057 | 12446.698 | change [en] 0.4137, right [en] 0.4137 | right |
| 13071 | 12458.284 | 樓板 [zh] 0.4139, 的士 [zh] 0.4139 | 的士 |
| 13089 | 12473.180 | 神話 [zh] 0.4141, accelerator [en] 0.4141 | accelerator |
| 13582 | 12880.246 | 沼澤 [zh] 0.4205, forest [en] 0.4205 | 沼澤 |
| 13857 | 13106.576 | eat [en] 0.4240, pass [en] 0.4240 | eat |
| 14798 | 13877.249 | 工作 [zh] 0.4361, example [en] 0.4361 | example |
| 15536 | 14477.782 | 撕 [zh] 0.4456, view [en] 0.4456 | view |
| 15844 | 14727.454 | 刀 [zh] 0.4495, try [en] 0.4495 | 刀 |
| 15862 | 14742.028 | 呢 [zh] 0.4498, wind [en] 0.4498 | 呢 |
| 16065 | 14906.265 | 含 [zh] 0.4524, books [en] 0.4524 | 含 |
| 16790 | 15490.952 | fen [en] 0.4617, show [en] 0.4617 | fen |
| 17221 | 15837.196 | 快 [zh] 0.4672, 攻擊 [zh] 0.4672 | 快 |
| 17379 | 15963.883 | 漠 [zh] 0.4693, top [en] 0.4692 | 漠 |
| 17469 | 16035.988 | 長 [zh] 0.4704, 門廳 [zh] 0.4704 | 長 |
| 18244 | 16655.216 | gap [en] 0.4804, kilometer [en] 0.4804 | gap |
| 19173 | 17393.671 | 錯 [zh] 0.4923, off [en] 0.4923 | off |
| 19202 | 17416.658 | 更 [zh] 0.4927, plan [en] 0.4927 | 更 |
| 19210 | 17422.999 | 百分率 [zh] 0.4928, 音 [zh] 0.4928 | 音 |
| 19994 | 18042.994 | 卡 [zh] 0.5028, orbiter [en] 0.5028 | 卡 |
| 20338 | 18314.184 | 調 [zh] 0.5073, speaker [en] 0.5073 | speaker |
| 20560 | 18488.929 | profit [en] 0.5101, stab [en] 0.5101 | profit |
| 20677 | 18580.941 | memory [en] 0.5116, whisky [en] 0.5116 | whisky |
| 20785 | 18665.824 | kg [en] 0.5130, theory [en] 0.5130 | theory |
| 20826 | 18698.036 | 義 [zh] 0.5135, 蛇行 [zh] 0.5135 | 義 |
| 20827 | 18698.821 | 參考 [zh] 0.5135, threaten [en] 0.5135 | threaten |
| 21208 | 18997.823 | 海員 [zh] 0.5184, railroad [en] 0.5184 | 海員 |
| 21674 | 19362.735 | student [en] 0.5244, weave [en] 0.5244 | weave |
| 21844 | 19495.644 | divisor [en] 0.5266, pedagogy [en] 0.5266 | pedagogy |
| 21868 | 19514.399 | 碰巧 [zh] 0.5269, ban [en] 0.5269 | ban |
| 21908 | 19545.651 | 休息 [zh] 0.5274, 土 [zh] 0.5274 | 土 |
| 22355 | 19894.478 | 共和國 [zh] 0.5332, process [en] 0.5332 | process |
| 22372 | 19907.730 | 天堂 [zh] 0.5334, pace [en] 0.5334 | pace |
| 22391 | 19922.539 | name [en] 0.5336, pilot [en] 0.5336 | pilot |
| 22431 | 19953.711 | 欺 [zh] 0.5342, recover [en] 0.5341 | 欺 |
| 23109 | 20481.174 | 即 [zh] 0.5429, 支援 [zh] 0.5429 | 支援 |
| 23194 | 20547.182 | 催化劑 [zh] 0.5439, 夠 [zh] 0.5439 | 夠 |
| 23327 | 20650.413 | dancing [en] 0.5457, sample [en] 0.5457 | dancing |
| 23366 | 20680.671 | 搬遷 [zh] 0.5462, sabre [en] 0.5462 | 搬遷 |
| 23422 | 20724.110 | advantage [en] 0.5469, stick [en] 0.5469 | advantage |
| 23719 | 20954.303 | alter [en] 0.5507, width [en] 0.5507 | alter |
| 23840 | 21047.995 | 偏見 [zh] 0.5522, charm [en] 0.5522 | charm |
| 24243 | 21359.678 | 模仿 [zh] 0.5574, 醫 [zh] 0.5574 | 醫 |
| 24273 | 21382.858 | 進 [zh] 0.5578, religion [en] 0.5578 | religion |
| 24477 | 21540.398 | find [en] 0.5604, tissue [en] 0.5604 | find |
| 24844 | 21823.461 | 金剛石 [zh] 0.5651, respect [en] 0.5651 | 金剛石 |
| 24913 | 21876.629 | accelerate [en] 0.5660, picture [en] 0.5660 | picture |

Edges joining a slot seated by an English list word to a slot seated by a Chinese list word: **9,818**.

Python address port vs the C engine: 1889 seated words checked, E mismatches 0.
<!-- @END test_chinese_english_v2.bin -->

<!-- @BLOCK test_english_chinese_v2.bin -->
**`test_english_chinese_v2.bin`** · sha256 `49786833cf5ec2f0…` · header version 6 · vocab 1,889 · A-edges 228,914 · word_count 3,220,743 · repo commit `6c3190c` · table `experiment_v2/results/test_english_chinese_v2_map.tsv`

Build: union alphabet (' a–z + 97,518 Han = 97,545), `-DHAN_RUN`; English pass, then Chinese pass on top

σ: the bin stores no σ per word; every seated word sits at its zero `zeros[slot]` (γ in the table) and carries E. `σ=0.5 (Noether forcing)` is a constant printed by the engine.

| language | list words | SEATED | OUTRANKED-BY-HIGHER-E | NEVER-IN-CORPUS | NOT-IN-ALPHABET | REJECTED-BY-FILTER | DROPPED-BY-TOKENIZER(<2 letters) | UNEXPLAINED(slot empty) | UNEXPLAINED(slot held by lower-E word) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zh | 960 | 894 | 29 | 36 | 1 | 0 | 0 | 0 | 0 |
| en | 1059 | 995 | 47 | 2 | 2 | 7 | 6 | 0 | 0 |

Legend: S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained

- **zh OUTRANKED-BY-HIGHER-E**: 休息 保證 偏見 停 催化劑 共和國 即 參考 哲學 外面 天堂 對白 工作 抹去 撕 攻擊 樓板 模仿 水滸 神話 租用 結 膠著 補 語者 調 進 錯 驚奇
- **zh NEVER-IN-CORPUS**: 主計 二十一點 共犯 分揀 反語 口水仗 吸附性 單據 套間 威士忌酒 小屁孩 幹掉 忽悠 怒恨 打滑 林陰大道 模子 池子 瀦留 百分率 硫黃 碰巧 膽力 芸香 蛇行 調遣 跟班 軟盤 醫務室 銀屏 鏦 鐘頭 門廳 頂樓 飄帶 馬刀
- **zh NOT-IN-ALPHABET**: 〇
- **en OUTRANKED-BY-HIGHER-E**: accelerate agriculture appear banquet beat books change commonwealth complaint deflect divisor eyelid figure fly forest judge kilometer leg memory name orbiter parchment pass plan portion praxis railroad recover recuperate respect sabre sample shame shout show stab stick student surge tissue top transport try tutor wellness width wind
- **en NEVER-IN-CORPUS**: lambskin tum
- **en NOT-IN-ALPHABET**: mother-in-law well-known
- **en REJECTED-BY-FILTER**: cm hr kg km ms scratch tv
- **en DROPPED-BY-TOKENIZER(<2 letters)**: a g i l m s

List words sharing a slot with another list word: 81 slots; across languages: 42.

| slot | γ | words that hash here (E) | label held in the bin |
|---:|---:|---|---|
| 467 | 770.515 | alternative [en] 0.2520, tutor [en] 0.2520 | alternative |
| 929 | 1338.517 | 租用 [zh] 0.2579, stay [en] 0.2579 | stay |
| 1070 | 1501.968 | priming [en] 0.2598, recuperate [en] 0.2598 | priming |
| 1487 | 1968.346 | 停 [zh] 0.2651, kick [en] 0.2651 | kick |
| 1563 | 2051.137 | 樹 [zh] 0.2661, figure [en] 0.2661 | 樹 |
| 1835 | 2342.966 | 植物群 [zh] 0.2696, complaint [en] 0.2696 | 植物群 |
| 2518 | 3051.218 | 驚奇 [zh] 0.2783, supplement [en] 0.2784 | supplement |
| 3280 | 3811.097 | 哲學 [zh] 0.2881, check [en] 0.2881 | check |
| 4457 | 4941.314 | 認同 [zh] 0.3033, shout [en] 0.3033 | 認同 |
| 4547 | 5026.018 | 組織 [zh] 0.3044, judge [en] 0.3044 | 組織 |
| 4565 | 5042.933 | 意義 [zh] 0.3047, 水滸 [zh] 0.3047 | 意義 |
| 5025 | 5472.438 | 習慣 [zh] 0.3106, deflect [en] 0.3106 | 習慣 |
| 5167 | 5604.003 | 張 [zh] 0.3124, 抹去 [zh] 0.3124 | 張 |
| 5855 | 6235.287 | 對白 [zh] 0.3212, 裂 [zh] 0.3212 | 裂 |
| 6441 | 6765.714 | disperse [en] 0.3287, praxis [en] 0.3287 | disperse |
| 6784 | 7073.408 | esteem [en] 0.3332, surge [en] 0.3331 | esteem |
| 6897 | 7174.356 | 過 [zh] 0.3346, agriculture [en] 0.3346 | 過 |
| 7204 | 7447.607 | leg [en] 0.3385, watercraft [en] 0.3386 | watercraft |
| 7436 | 7653.165 | 保證 [zh] 0.3415, justice [en] 0.3415 | justice |
| 7577 | 7777.714 | 男人 [zh] 0.3433, 補 [zh] 0.3433 | 男人 |
| 7904 | 8065.497 | commonwealth [en] 0.3475, inclination [en] 0.3475 | inclination |
| 7975 | 8127.790 | 奴隸制 [zh] 0.3485, 膠著 [zh] 0.3484 | 奴隸制 |
| 8145 | 8276.675 | 拉 [zh] 0.3506, parchment [en] 0.3506 | 拉 |
| 8701 | 8761.068 | 尾流 [zh] 0.3578, fly [en] 0.3578 | 尾流 |
| 9006 | 9025.208 | 拖 [zh] 0.3617, transport [en] 0.3617 | 拖 |
| 9174 | 9170.247 | 打擊 [zh] 0.3639, portion [en] 0.3639 | 打擊 |
| 9280 | 9261.597 | 有機體 [zh] 0.3652, shame [en] 0.3652 | 有機體 |
| 9559 | 9501.453 | free [en] 0.3688, wellness [en] 0.3688 | free |
| 9866 | 9764.429 | 結 [zh] 0.3727, 雜物 [zh] 0.3727 | 雜物 |
| 10135 | 9994.064 | 便利 [zh] 0.3762, appear [en] 0.3762 | 便利 |
| 10759 | 10524.037 | 病房 [zh] 0.3842, banquet [en] 0.3842 | 病房 |
| 10867 | 10615.394 | beat [en] 0.3856, spread [en] 0.3856 | spread |
| 11161 | 10863.555 | 植物 [zh] 0.3894, eyelid [en] 0.3894 | 植物 |
| 12377 | 11882.164 | 外面 [zh] 0.4050, ammunition [en] 0.4050 | ammunition |
| 12982 | 12384.601 | 同謀 [zh] 0.4128, 語者 [zh] 0.4128 | 同謀 |
| 13057 | 12446.698 | change [en] 0.4137, right [en] 0.4137 | right |
| 13071 | 12458.284 | 樓板 [zh] 0.4139, 的士 [zh] 0.4139 | 的士 |
| 13089 | 12473.180 | 神話 [zh] 0.4141, accelerator [en] 0.4141 | accelerator |
| 13582 | 12880.246 | 沼澤 [zh] 0.4205, forest [en] 0.4205 | 沼澤 |
| 13857 | 13106.576 | eat [en] 0.4240, pass [en] 0.4240 | eat |
| 14798 | 13877.249 | 工作 [zh] 0.4361, example [en] 0.4361 | example |
| 15536 | 14477.782 | 撕 [zh] 0.4456, view [en] 0.4456 | view |
| 15844 | 14727.454 | 刀 [zh] 0.4495, try [en] 0.4495 | 刀 |
| 15862 | 14742.028 | 呢 [zh] 0.4498, wind [en] 0.4498 | 呢 |
| 16065 | 14906.265 | 含 [zh] 0.4524, books [en] 0.4524 | 含 |
| 16790 | 15490.952 | fen [en] 0.4617, show [en] 0.4617 | fen |
| 17221 | 15837.196 | 快 [zh] 0.4672, 攻擊 [zh] 0.4672 | 快 |
| 17379 | 15963.883 | 漠 [zh] 0.4693, top [en] 0.4692 | 漠 |
| 17469 | 16035.988 | 長 [zh] 0.4704, 門廳 [zh] 0.4704 | 長 |
| 18244 | 16655.216 | gap [en] 0.4804, kilometer [en] 0.4804 | gap |
| 19173 | 17393.671 | 錯 [zh] 0.4923, off [en] 0.4923 | off |
| 19202 | 17416.658 | 更 [zh] 0.4927, plan [en] 0.4927 | 更 |
| 19210 | 17422.999 | 百分率 [zh] 0.4928, 音 [zh] 0.4928 | 音 |
| 19994 | 18042.994 | 卡 [zh] 0.5028, orbiter [en] 0.5028 | 卡 |
| 20338 | 18314.184 | 調 [zh] 0.5073, speaker [en] 0.5073 | speaker |
| 20560 | 18488.929 | profit [en] 0.5101, stab [en] 0.5101 | profit |
| 20677 | 18580.941 | memory [en] 0.5116, whisky [en] 0.5116 | whisky |
| 20785 | 18665.824 | kg [en] 0.5130, theory [en] 0.5130 | theory |
| 20826 | 18698.036 | 義 [zh] 0.5135, 蛇行 [zh] 0.5135 | 義 |
| 20827 | 18698.821 | 參考 [zh] 0.5135, threaten [en] 0.5135 | threaten |
| 21208 | 18997.823 | 海員 [zh] 0.5184, railroad [en] 0.5184 | 海員 |
| 21674 | 19362.735 | student [en] 0.5244, weave [en] 0.5244 | weave |
| 21844 | 19495.644 | divisor [en] 0.5266, pedagogy [en] 0.5266 | pedagogy |
| 21868 | 19514.399 | 碰巧 [zh] 0.5269, ban [en] 0.5269 | ban |
| 21908 | 19545.651 | 休息 [zh] 0.5274, 土 [zh] 0.5274 | 土 |
| 22355 | 19894.478 | 共和國 [zh] 0.5332, process [en] 0.5332 | process |
| 22372 | 19907.730 | 天堂 [zh] 0.5334, pace [en] 0.5334 | pace |
| 22391 | 19922.539 | name [en] 0.5336, pilot [en] 0.5336 | pilot |
| 22431 | 19953.711 | 欺 [zh] 0.5342, recover [en] 0.5341 | 欺 |
| 23109 | 20481.174 | 即 [zh] 0.5429, 支援 [zh] 0.5429 | 支援 |
| 23194 | 20547.182 | 催化劑 [zh] 0.5439, 夠 [zh] 0.5439 | 夠 |
| 23327 | 20650.413 | dancing [en] 0.5457, sample [en] 0.5457 | dancing |
| 23366 | 20680.671 | 搬遷 [zh] 0.5462, sabre [en] 0.5462 | 搬遷 |
| 23422 | 20724.110 | advantage [en] 0.5469, stick [en] 0.5469 | advantage |
| 23719 | 20954.303 | alter [en] 0.5507, width [en] 0.5507 | alter |
| 23840 | 21047.995 | 偏見 [zh] 0.5522, charm [en] 0.5522 | charm |
| 24243 | 21359.678 | 模仿 [zh] 0.5574, 醫 [zh] 0.5574 | 醫 |
| 24273 | 21382.858 | 進 [zh] 0.5578, religion [en] 0.5578 | religion |
| 24477 | 21540.398 | find [en] 0.5604, tissue [en] 0.5604 | find |
| 24844 | 21823.461 | 金剛石 [zh] 0.5651, respect [en] 0.5651 | 金剛石 |
| 24913 | 21876.629 | accelerate [en] 0.5660, picture [en] 0.5660 | picture |

Edges joining a slot seated by an English list word to a slot seated by a Chinese list word: **9,818**.

Python address port vs the C engine: 1889 seated words checked, E mismatches 0.
<!-- @END test_english_chinese_v2.bin -->

<!-- @BLOCK PAIRS_pure -->
**Where the English word and its Chinese word landed — English in test_english_v2.bin, Chinese in test_chinese_v2.bin**  (1051 matched pairs: an English word and its Chinese word; table `results/pairs_pure.tsv`)

| measure | observed | expected if the two placements are unrelated |
|---|---:|---:|
| same slot | 0 | 0.042 |
| within 1 slot | 0 | 0.13 |
| within 3 slots | 0 | 0.29 |
| within 10 slots | 1 | 0.88 |
| \|Δslot\|/N quartiles | [0.1484, 0.3138, 0.534] | [0.134, 0.2929, 0.5] |
| \|ΔE\| quartiles | [0.0477, 0.1008, 0.1715] | [0.043, 0.0941, 0.1606] |
| \|Δγ\| in local zero spacings, quartiles | [3711.9, 7896.4, 13491.4] | — |

Histogram of \|Δslot\|/N in ten equal bins: [178, 181, 151, 132, 117, 103, 81, 62, 33, 13]  (unrelated placements give a falling triangle: ≈ 19 %, 17 %, 15 % … 1 % of pairs).
<!-- @END PAIRS_pure -->

<!-- @BLOCK PAIRS_chinese_english -->
**The same pairs inside one union-alphabet table (test_chinese_english_v2.bin = test_english_chinese_v2.bin positions)**  (1051 matched pairs: an English word and its Chinese word; table `results/pairs_test_chinese_english_v2.tsv`)

| measure | observed | expected if the two placements are unrelated |
|---|---:|---:|
| same slot | 0 | 0.042 |
| within 1 slot | 0 | 0.13 |
| within 3 slots | 0 | 0.29 |
| within 10 slots | 1 | 0.88 |
| \|Δslot\|/N quartiles | [0.1403, 0.3057, 0.5323] | [0.134, 0.2929, 0.5] |
| \|ΔE\| quartiles | [0.045, 0.0982, 0.1709] | [0.043, 0.0941, 0.1606] |
| \|Δγ\| in local zero spacings, quartiles | [3507.7, 7670.4, 13380.8] | — |

Histogram of \|Δslot\|/N in ten equal bins: [192, 172, 153, 133, 111, 97, 84, 61, 34, 14]  (unrelated placements give a falling triangle: ≈ 19 %, 17 %, 15 % … 1 % of pairs).
<!-- @END PAIRS_chinese_english -->

<!-- @BLOCK SECOND_PASS_chinese_first -->
**test_chinese_english_v2** — what the second language's pass did to the first language (zh) · stage file `bins/stage/`

- first-pass vocab 910 → final vocab 1,889
- slots whose label word changed: **16**
- first-language list words whose β changed: **35** of 910  (β change min/q1/median/q3/max: [0.0, 0.0, 0.0, 0.0, 5.00245278438468])
- first-language list words whose edge count changed: 41
- state transitions (first pass → final):
  - NOT-IN-ALPHABET -> NOT-IN-ALPHABET: 1
  - SEATED -> SEATED: 894
  - NEVER-IN-CORPUS -> NEVER-IN-CORPUS: 36
  - OUTRANKED-BY-HIGHER-E -> OUTRANKED-BY-HIGHER-E: 13
  - SEATED -> OUTRANKED-BY-HIGHER-E: 16
<!-- @END SECOND_PASS_chinese_first -->

<!-- @BLOCK SECOND_PASS_english_first -->
**test_english_chinese_v2** — what the second language's pass did to the first language (en) · stage file `bins/stage/`

- first-pass vocab 1,020 → final vocab 1,889
- slots whose label word changed: **25**
- first-language list words whose β changed: **41** of 1020  (β change min/q1/median/q3/max: [0.0, 0.0, 0.0, 0.0, 7.5003655676367815])
- first-language list words whose edge count changed: 41
- state transitions (first pass → final):
  - DROPPED-BY-TOKENIZER(<2 letters) -> DROPPED-BY-TOKENIZER(<2 letters): 6
  - SEATED -> SEATED: 995
  - OUTRANKED-BY-HIGHER-E -> OUTRANKED-BY-HIGHER-E: 22
  - SEATED -> OUTRANKED-BY-HIGHER-E: 25
  - REJECTED-BY-FILTER -> REJECTED-BY-FILTER: 7
  - NEVER-IN-CORPUS -> NEVER-IN-CORPUS: 2
  - NOT-IN-ALPHABET -> NOT-IN-ALPHABET: 2
<!-- @END SECOND_PASS_english_first -->

<!-- @BLOCK ORDER_EFFECT -->
**Chinese-first final bin against English-first final bin**

- vocab [1889, 1889]; slots whose label differs: **0**
- β: max |difference| 0.000153 over 31 slots
- A-edges: [228914, 228914]; only in Chinese-first 0; only in English-first 0
- edge weights: 3364 of the shared edges differ (max |difference| 5.35e-05)

Same slot in the pure build and the union build: English 1 of 1059; Chinese 1 of 960.
<!-- @END ORDER_EFFECT -->

<!-- @BLOCK FAULT_ROWS -->
State and slot of each deliberately faulty row, per bin (S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained)

| kind | English | Chinese | en bin | zh bin | en in union | zh in union |
|---|---|---|---|---|---|---|
| plural-one-zh-word | foot | 腳 | S 19536 | S 5142 | S 23396 | S 22315 |
| plural-one-zh-word | feet | 腳 | S 2042 | S 5142 | S 11089 | S 22315 |
| plural-one-zh-word | mouse | 老鼠 | S 205 | S 24203 | S 15408 | S 3088 |
| plural-one-zh-word | mice | 老鼠 | S 16236 | S 24203 | S 15122 | S 3088 |
| plural-one-zh-word | child | 孩子 | S 13240 | S 22259 | S 5726 | S 20 |
| plural-one-zh-word | children | 孩子 | S 6808 | S 22259 | S 21063 | S 20 |
| plural-one-zh-word | tooth | 牙 | S 15487 | S 22157 | S 2144 | S 14330 |
| plural-one-zh-word | teeth | 牙 | S 3524 | S 22157 | S 14499 | S 14330 |
| plural-one-zh-word | man | 男人 | S 7653 | S 10359 | S 10911 | S 7577 |
| plural-one-zh-word | men | 男人 | S 3976 | S 10359 | S 23455 | S 7577 |
| plural-one-zh-word | woman | 女人 | S 5690 | S 11259 | S 23715 | S 18203 |
| plural-one-zh-word | women | 女人 | S 2013 | S 11259 | S 11259 | S 18203 |
| plural-one-zh-word | goose | 鵝 | S 13454 | S 16915 | S 7566 | S 9088 |
| plural-one-zh-word | geese | 鵝 | S 1491 | S 16915 | S 19921 | S 9088 |
| plural-one-zh-word | tree | 樹 | S 3109 | S 9390 | S 3935 | S 1563 |
| plural-one-zh-word | trees | 樹 | S 20631 | S 9390 | S 16127 | S 1563 |
| plural-one-zh-word | book | 書 | S 16368 | S 13832 | S 21659 | S 6005 |
| plural-one-zh-word | books | 書 | S 5255 | S 13832 | O 16065 | S 6005 |
| plural-one-zh-word | word | 詞 | S 4534 | S 4432 | S 1975 | S 21605 |
| plural-one-zh-word | words | 詞 | S 6030 | S 4432 | S 852 | S 21605 |
| tense-one-zh-word | walk | 走 | S 15844 | S 23800 | S 2987 | S 15973 |
| tense-one-zh-word | walked | 走 | S 11305 | S 23800 | S 23827 | S 15973 |
| tense-one-zh-word | walking | 走 | S 17858 | S 23800 | S 24448 | S 15973 |
| tense-one-zh-word | eat | 吃 | S 24008 | S 5859 | S 13857 | S 23032 |
| tense-one-zh-word | ate | 吃 | S 5355 | S 5859 | S 9296 | S 23032 |
| tense-one-zh-word | eaten | 吃 | S 2843 | S 5859 | S 20730 | S 23032 |
| tense-one-zh-word | eating | 吃 | S 10606 | S 5859 | S 21865 | S 23032 |
| english-only-or-tokenizer | the | - | S 841 |  | S 469 |  |
| english-only-or-tokenizer | a | - | T 4305 |  | T 15450 |  |
| english-only-or-tokenizer | an | - | O 6994 |  | S 22583 |  |
| english-only-or-tokenizer | of | - | O 8017 |  | S 17878 |  |
| english-only-or-tokenizer | is | - | S 1894 |  | S 24924 |  |
| english-only-or-tokenizer | to | - | S 11228 |  | S 22614 |  |
| english-only-or-tokenizer | i | - | T 2912 |  | T 14057 |  |
| english-only-or-tokenizer | don't | - | S 22044 |  | S 17018 |  |
| english-only-or-tokenizer | well-known | - | N 5192 |  | A 9279 |  |
| english-only-or-tokenizer | mother-in-law | - | N 2535 |  | A 22971 |  |
| chinese-only | - | 個 |  | S 7795 |  | S 24968 |
| chinese-only | - | 隻 |  | S 6372 |  | S 23545 |
| chinese-only | - | 條 |  | S 18640 |  | S 10813 |
| chinese-only | - | 張 |  | S 12994 |  | S 5167 |
| chinese-only | - | 本 |  | S 17276 |  | S 9449 |
| chinese-only | - | 了 |  | S 22415 |  | S 14588 |
| chinese-only | - | 過 |  | S 14724 |  | S 6897 |
| chinese-only | - | 著 |  | S 13771 |  | S 5944 |
| chinese-only | - | 的 |  | S 8214 |  | S 387 |
| chinese-only | - | 嗎 |  | S 22799 |  | S 14972 |
| chinese-only | - | 呢 |  | S 23689 |  | S 15862 |
| chinese-only | - | 們 |  | S 500 |  | S 17673 |
| chinese-only | - | 把 |  | S 17569 |  | S 9742 |
| chinese-only | - | 被 |  | S 8313 |  | S 486 |
| chinese-only-multichar | - | 我們 |  | S 19998 |  | S 10453 |
| chinese-only-multichar | - | 他們 |  | S 24776 |  | S 22834 |
<!-- @END FAULT_ROWS -->

<!-- @BLOCK OBSERVATIONS -->
Measurements only, nothing repaired.
1. Pure English and pure Chinese: every list word that reached the engine and was not outranked has its own slot and sits at `zeros[slot]`; the Python port of the address reproduces every stored E (0 mismatches).
2. Matched pairs land as unrelated placements do (PAIRS_pure): no pair shares a slot; the |Δslot|/N quartiles are the triangle for two independent uniform placements.
3. The engine's slot label goes to the higher-E word, not the first arrival; both orders end with the same labels (ORDER_EFFECT: 0 differing).
4. The mixed bins have 9,818 edges joining an English-seated slot to a Chinese-seated slot although no sentence holds both languages: they run through the 42 slots where an English and a Chinese list word hash together.
5. English tokens dropped before seating: tokens under two letters (`a`, `i`) by the tokenizer, and 7 words by the token filter: cm hr kg km ms scratch tv.
6. Order effect on values: β and edge weights differ slightly between the two orders (ORDER_EFFECT) while labels and edge sets are identical.
7. E is not a second coordinate: slot = ⌊seed·N⌋ and E = d* + seed·(Ω − d*) use the same 64-bit seed, so E = d* + (slot + fraction)·(Ω − d*)/N. Largest |E − (d* + slot·(Ω − d*)/N)| over seated words: English 1.28e-05, Chinese 1.28e-05 (one slot is 1.28e-05 wide in E). Two words sharing a slot therefore always have almost equal E.
8. Word segmentation of running Chinese with only the list as a dictionary matches list words inside unrelated text; the share of one-character Chinese tokens in the filtered corpus is in `experiment_v2/corpus_counts.tsv`.
<!-- @END OBSERVATIONS -->
