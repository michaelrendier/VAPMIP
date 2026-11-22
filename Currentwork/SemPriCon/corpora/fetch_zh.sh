#!/usr/bin/env bash
# fetch_zh.sh — the Chinese-only baseline sources (Mandarin, Traditional where available; NO Cantonese, Hokkien or Min sources).
# Same rules as fetch.sh: Mozilla UA, one connection, public files, rate-limited, resumable, recorded in MANIFEST.tsv.
set -u
cd "$(dirname "$0")"
UA="${CLAUDE_UA:-Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0}"
get() {  # get <dest> <url> <licence>
  local dest="$1" url="$2" lic="$3"; mkdir -p "$(dirname "$dest")"
  local want; want=$(curl -sIL -m 30 -A "$UA" "$url" | tr -d '\r' | awk 'tolower($1)=="content-length:"{v=$2} END{print v}')
  if [ -f "$dest" ] && [ -n "$want" ] && [ "$(stat -c %s "$dest")" = "$want" ]; then echo "have $dest"; else
    echo "get  $dest <- $url ($want bytes)"; curl -fL -C - --retry 3 --retry-delay 5 -A "$UA" --limit-rate 8m -o "$dest" "$url" || { echo "FAILED $url"; return 1; }; fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$dest" "$url" "$(stat -c %s "$dest")" "$(sha256sum "$dest" | cut -d' ' -f1)" "$lic" "$(date +%F)" >> MANIFEST.tsv
}
M=https://raw.githubusercontent.com/g0v/moedict-data/master; L_M="CC BY-ND 3.0 TW (Taiwan Ministry of Education 重編國語辭典修訂本); the ND limit is on the text; format conversion and use permitted per the MOE reading quoted in moedict-data/README"
get zh/moedict/dict-revised.json.xz "$M/dict-revised.json.xz" "$L_M"
get zh/moedict/README.md "$M/README.md" "$L_M"
G=https://raw.githubusercontent.com/gujilab/chinese-classical-corpus/main; L_G="CC0 (gujilab/chinese-classical-corpus; public-domain classical texts)"
for f in LICENSE README.md output/shuowen.json output/shisanjing/erya.json output/sishu/daxue.json output/sishu/lunyu.json output/sishu/mengzi.json output/sishu/zhongyong.json; do get zh/classical/$(basename $f) "$G/$f" "$L_G"; done
get zh/structure/Unihan.zip https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip "Unicode License (Unihan database)"
get zh/structure/makemeahanzi-dictionary.txt https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt "makemeahanzi dictionary.txt (derived from Unihan + CC-CEDICT; see the repo README)"
get zh/structure/cjkvi-ids.txt https://raw.githubusercontent.com/cjkvi/cjkvi-ids/master/ids.txt "cjkvi-ids (CHISE IDS data; licence to be checked before redistribution)"
get zh/structure/cedict_1_0_ts_utf-8_mdbg.zip https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip "CC BY-SA 4.0 (CC-CEDICT, MDBG export)"
echo DONE_ZH
