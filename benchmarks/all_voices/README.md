# All-voices benchmark

`benchmark_voices.py` benchmarks every monad voice the console can select (see the docstring for exactly what is timed).
Reference run: `runs/results_2026-10-14.json` (ThinkPad X1 Carbon 6th, i7-8550U, laptop on battery).
Write-up with transcripts: `docs/wiki/Tuning-the-Engine/42_every_voice_benchmark.md`; paper draft: `docs/paper_drafts/`.

Run from `VAPMIP/`:  `python3 benchmarks/all_voices/benchmark_voices.py`  (use `PtolemyDesktop/.venv/bin/python` if the system python cannot import nltk).
Expect 24 modules, 12 selectable and speaking. Results vary a few percent between runs; the first reply of each voice includes loading WordNet.
