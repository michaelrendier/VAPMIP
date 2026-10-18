#!/usr/bin/env bash
# Builds The_Golden_Ratio_Monad.pdf (the ONLY PDF kept in the repo; Cody 2026-10-14) from the markdown (pandoc + LuaLaTeX; DejaVu fonts with a Unifont fallback).
# The fallback definition must come BEFORE the font set-up, so the tex is generated, patched, then compiled twice.
set -euo pipefail
T="${TMPDIR:-/tmp}"
cd "$(dirname "$0")"
true  # text is built by make_paper.py; run it first
cat The_Golden_Ratio_Monad.md > $T/goldmonad_clean.md   # timing markers are for --check only
pandoc $T/goldmonad_clean.md -s -o $T/goldmonad.tex -V geometry:margin=1in -V fontsize=10pt -V colorlinks=true \
  -V mainfont="DejaVu Serif" -V mainfontoptions="RawFeature={fallback=fbk}" -V monofont="DejaVu Sans Mono" \
  -V monofontoptions="Scale=0.8,RawFeature={fallback=fbk}" -H header.tex \
  -V title-meta="The Golden-Ratio Monad" -V author-meta="Cody Michael Allison"
python3 - <<'PY'
import os
p = os.environ.get('TMPDIR', '/tmp') + '/goldmonad.tex'; s = open(p).read()
fb = '\\directlua{luaotfload.add_fallback("fbk",{"Unifont:mode=node;"})}\n'
i = s.index('\\usepackage{fontspec}') if '\\usepackage{fontspec}' in s else s.index('\\setmainfont')
open(p, 'w').write(s[:i] + fb + s[i:])
PY
for i in 1 2; do lualatex -interaction=nonstopmode -output-directory=$T $T/goldmonad.tex >$T/goldmonad_$i.log 2>&1; done
cp $T/goldmonad.pdf The_Golden_Ratio_Monad.pdf
echo "pages: $(pdfinfo The_Golden_Ratio_Monad.pdf | awk '/Pages/{print $2}'); missing glyph warnings: $(grep -c 'Missing character' $T/goldmonad_2.log || true)"
