#!/bin/sh
# Byte-identity check: every file mirrored into mappings/{UNS,Flat}/ must equal its source in ../tools/ (nothing in tools/ was altered).
cd "$(dirname "$0")" || exit 1
rc=0
for d in UNS Flat; do for f in $d/*.py; do
  cmp -s "$f" "../tools/$(basename "$f")" && echo "same  $f" || { echo "DIFF  $f"; rc=1; }
done; done
exit $rc
