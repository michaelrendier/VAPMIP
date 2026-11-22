#!/bin/bash
# build_v2.0_zh_en_wordlist_bins.sh (copy of tools/exp_v2_run.sh, run from SpecTools/bin_creation; the v2.0 four-bin zh/en word-list experiment) — build the four experiment bins from ground state (experiment_v2/).  PTOL_DPRINT=1 feed is filtered to the engine's learn.* lines.
set -u; cd "$(dirname "$0")/../.."; X=experiment_v2; B=build/exp_v2; export HOME=$PWD/$X/home; mkdir -p $X/bins/stage $X/logs
for n in test_chinese_v2 test_english_v2 test_chinese_english_v2 test_english_chinese_v2; do rm -f $X/bins/$n.bin; python3 -c "import sys; sys.path.insert(0,'tools'); import ptol_bin; ptol_bin.write_ground('$X/bins/$n.bin', version=6)"; done
go(){ PTOL_DPRINT=1 $B/$1 -c $X/bins/$2.bin -l $X/$3 2>&1 | grep -E "^\[(dp\] learn\.|state|monad)|^ +(ground|σ|affect)" > $X/logs/$2.$4.dprint.log; echo "$2 $4: $(grep -c 'learn.rejected' $X/logs/$2.$4.dprint.log) rejected, $(grep -c 'learn.slot_shared =' $X/logs/$2.$4.dprint.log) slot_shared events"; }
go ptolemy_zh test_chinese_v2 text_zh.txt zh
go ptolemy_en test_english_v2 text_en.txt en
go ptolemy_un test_chinese_english_v2 text_zh.txt pass1_zh; cp $X/bins/test_chinese_english_v2.bin $X/bins/stage/test_chinese_english_v2.after_zh.bin
go ptolemy_un test_chinese_english_v2 text_en.txt pass2_en
go ptolemy_un test_english_chinese_v2 text_en.txt pass1_en; cp $X/bins/test_english_chinese_v2.bin $X/bins/stage/test_english_chinese_v2.after_en.bin
go ptolemy_un test_english_chinese_v2 text_zh.txt pass2_zh
sha256sum $X/bins/*.bin $X/bins/stage/*.bin > $X/bins/SHA256SUMS
