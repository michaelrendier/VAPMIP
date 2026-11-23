# UserState: the user's emotional state from the text of a prompt

The input side of the machine (nothing here reads the recipes yet). Code: `../../user_state.py` (meters, the 15-layer object, the scalar, the code, the warming conversation), `../../user_state_console.py` (the slide-rule console), `../../ans_to_png.py` (truecolor `.ans` to PNG). Statistics: ValaQuenta `bell_curve` v1.1.

| file | what |
|---|---|
| `build_corpus.py` | builds `corpus.jsonl` (5,105 prompts, seed 20261122) from GoEmotions, TweetEval irony, AdvBench, HarmBench, jailbreak_llms, NPS Chat, the Wernicke standard prompts and `probes.jsonl` |
| `probes.jsonl` | 85 hand-written probes with the expected emotion written before any run, including three multi-turn conversations |
| `run_raw.py` | stage 1: runs VADER, three models, arousal features, dialogue act once per prompt, caches to `raw_cache.jsonl` |
| `augment_cache.py` | adds the Empath domain counts to the cache |
| `run_battery.py` | stage 2: scores, validates (T1 to T4), writes `out/REPORT.md`, `out/*.ans`, `out/results.jsonl` |
| `out/REPORT_v1.md` | the first run, kept (62/85 probes; the irony swap flipped sincere prompts) |
| `out/REPORT.md` | the current run |
| `out/user_state_probes.ans`, `out/user_state_corpus.ans` | each prompt with its 15-cell state, truecolor; `cat` them in a terminal |

Not committed (`.gitignore`): `corpus.jsonl`, `raw_cache.jsonl`, `out/results.jsonl`, `out_local/` (tweets, adversarial strings). Raw downloads: `~/Desktop/SpaceClaude/local_only_references/UserStateCorpora/`.

Run: `cd VAPMIP && .venv/bin/python Currentwork/UserState/build_corpus.py && .venv/bin/python Currentwork/UserState/run_raw.py && .venv/bin/python Currentwork/UserState/run_battery.py`
