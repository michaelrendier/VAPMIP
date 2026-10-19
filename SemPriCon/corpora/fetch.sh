#!/usr/bin/env bash
# fetch.sh — the downloads for the Unicode test bed (English US/UK + Mandarin, Swahili, Finnish, Indonesian, Quechua).
# Rules: Mozilla UA on every request; one connection at a time; public files only; rate-limited; resumable (-C -).
# Every file lands with its source URL, size and sha256 in MANIFEST.tsv.  Skips a file that is already complete.
set -u
cd "$(dirname "$0")"
UA="${CLAUDE_UA:-Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0}"
RATE="${FETCH_RATE:-8m}"
get() {  # get <dest> <url> <licence>
  local dest="$1" url="$2" lic="$3"
  mkdir -p "$(dirname "$dest")"
  local want; want=$(curl -sIL -m 30 -A "$UA" "$url" | tr -d '\r' | awk 'tolower($1)=="content-length:"{v=$2} END{print v}')
  if [ -f "$dest" ] && [ -n "$want" ] && [ "$(stat -c %s "$dest")" = "$want" ]; then echo "have $dest"; else
    echo "get  $dest <- $url ($want bytes)"
    curl -fL -C - --retry 3 --retry-delay 5 -A "$UA" --limit-rate "$RATE" -o "$dest" "$url" || { echo "FAILED $url"; return 1; }
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$dest" "$url" "$(stat -c %s "$dest")" "$(sha256sum "$dest" | cut -d' ' -f1)" "$lic" "$(date +%F)" >> MANIFEST.tsv
}
K=https://kaikki.org/dictionary; LIC_K="CC BY-SA 4.0 + GFDL (Wiktionary via wiktextract, Ylonen 2022; cite and link kaikki.org)"
for L in Quechua Swahili Indonesian Chinese English Finnish; do get lexicon/kaikki-$L.jsonl "$K/$L/kaikki.org-dictionary-$L.jsonl" "$LIC_K"; done
T=https://downloads.tatoeba.org/exports; LIC_T="CC BY 2.0 FR (Tatoeba)"
for L in que swh fin ind cmn eng; do get tatoeba/${L}_sentences.tsv.bz2 "$T/per_language/$L/${L}_sentences.tsv.bz2" "$LIC_T"; done
get tatoeba/links.tar.bz2 "$T/links.tar.bz2" "$LIC_T"
H=https://huggingface.co/datasets/wikimedia/wikipedia/resolve/main; LIC_W="CC BY-SA 4.0 + GFDL (Wikimedia, dump 20231101, via Hugging Face wikimedia/wikipedia)"
get wikipedia/qu.parquet "$H/20231101.qu/train-00000-of-00001.parquet" "$LIC_W"
get wikipedia/sw.parquet "$H/20231101.sw/train-00000-of-00001.parquet" "$LIC_W"
get wikipedia/fi-00.parquet "$H/20231101.fi/train-00000-of-00003.parquet" "$LIC_W"
get wikipedia/id-00.parquet "$H/20231101.id/train-00000-of-00003.parquet" "$LIC_W"
get wikipedia/zh-00.parquet "$H/20231101.zh/train-00000-of-00006.parquet" "$LIC_W"
get wikipedia/en-00.parquet "$H/20231101.en/train-00000-of-00041.parquet" "$LIC_W"
echo DONE
