#!/usr/bin/env bash
# Builds Forward_Propagation_of_Information.pdf (the ONLY PDF kept in the repo; Cody 2026-10-14) from the markdown (pandoc + LuaLaTeX; DejaVu fonts with a Unifont fallback).
# The fallback definition must come BEFORE the font set-up, so the tex is generated, patched, then compiled twice.
set -euo pipefail
T="${TMPDIR:-/tmp}"
cd "$(dirname "$0")"
[ -n "${SKIP_MAKE:-}" ] || ../../PtolemyDesktop/.venv/bin/python make_paper.py
sed 's/[⟦⟧]//g' Forward_Propagation_of_Information.md > $T/fwdprop_clean.md   # timing markers are for --check only
pandoc $T/fwdprop_clean.md -s -o $T/fwdprop.tex -V geometry:margin=1in -V fontsize=10pt -V colorlinks=true \
  -V mainfont="DejaVu Serif" -V mainfontoptions="RawFeature={fallback=fbk}" -V monofont="DejaVu Sans Mono" \
  -V monofontoptions="Scale=0.8,RawFeature={fallback=fbk}" -H header.tex \
  -V title-meta="Forward Propagation of Information" -V author-meta="Cody Michael Allison"
python3 - <<'PY'
import os
p = os.environ.get('TMPDIR', '/tmp') + '/fwdprop.tex'; s = open(p).read()
fb = '\\directlua{luaotfload.add_fallback("fbk",{"Unifont:mode=node;"})}\n'
i = s.index('\\usepackage{fontspec}') if '\\usepackage{fontspec}' in s else s.index('\\setmainfont')
open(p, 'w').write(s[:i] + fb + s[i:])
PY
for i in 1 2; do lualatex -interaction=nonstopmode -output-directory=$T $T/fwdprop.tex >$T/fwdprop_$i.log 2>&1; done
cp $T/fwdprop.pdf Forward_Propagation_of_Information.pdf
echo "pages: $(pdfinfo Forward_Propagation_of_Information.pdf | awk '/Pages/{print $2}'); missing glyph warnings: $(grep -c 'Missing character' $T/fwdprop_2.log || true)"
