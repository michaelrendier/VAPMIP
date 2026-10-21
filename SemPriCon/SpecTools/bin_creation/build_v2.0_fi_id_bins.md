# Build recipe — test_finnish_v2.0.bin, test_indonesian_v2.0.bin (Fresh Start v2.0)
Source of record: `clean/archive/../MANIFEST` history and wiki `09_the_test_bins.md`. Run from `SemPriCon/`, HOME at a throwaway directory.
```
python3 tools/gen_alphabet.py                  # alphabet_zh.h, alphabet_fi.h
python3 tools/ingest_corpora.py                # corpora/text/{zh,en,id,fi}_v1.txt + TEXT_V1.sha256
# gcc ... -DALPHABET_TABLE -DALPHABET_HEADER='"alphabet_fi.h"' ... -o build/v2/ptolemy_fi     (id: ASCII-95 build, build/v2/ptolemy_en)
python3 -c "import sys; sys.path.insert(0,'tools'); import ptol_bin; ptol_bin.write_ground('test_finnish_v2.0.bin', version=6)"
build/v2/ptolemy_fi -q -c test_finnish_v2.0.bin -l corpora/text/fi_v1.txt
```
Footgun: `-c <path>` only works if the file exists first; otherwise the engine saves to the protected default and the ingest is lost.
The bins themselves are archived (gitignored) in `dirty/v2.0/`; checksums in `dirty/v2.0/MANIFEST_v2.0.tsv`.
