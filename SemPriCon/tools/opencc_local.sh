#!/usr/bin/env bash
# opencc_local.sh — run OpenCC (Debian/Ubuntu 1.1.7 packages unpacked under corpora/zh/src/opencc-root, no root needed).
#   tools/opencc_local.sh s2twp  < in.txt > out.txt      (Simplified -> Traditional, Taiwan standard, with phrase conversion)
#   configs: s2t s2tw s2twp t2s tw2s ...
R="$(cd "$(dirname "$0")/../corpora/zh/src/opencc-root" && pwd)"
CFG="$1"; shift
LD_LIBRARY_PATH="$(find "$R" -name '*.so*' -printf '%h\n' | sort -u | tr '\n' ':')" "$R/usr/bin/opencc" -c "$R/usr/share/opencc/$CFG.json" "$@"
