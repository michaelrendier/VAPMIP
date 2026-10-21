# Build recipe — test_chinese_v1.0.bin, test_english_v1.0.bin (Fresh Start v1.0)
Archived with their commands in `clean/archive/v1.0/MANIFEST_v1.0.tsv`. Run from `SemPriCon/`, HOME at a throwaway directory.
```
python3 -c "import sys; sys.path.insert(0,'tools'); import ptol_bin; ptol_bin.write_ground('test_chinese_v1.0.bin', version=5)"   # same for english
build/zh/ptolemy_zh -q -c test_chinese_v1.0.bin -l corpora/text/zh_v1.txt   # Unicode code-point alphabet (Horner base 0x110001 mod 2^61-1)
build/en/ptolemy_en -q -c test_english_v1.0.bin -l corpora/text/en_v1.txt   # ASCII-95 alphabet (Horner base 95), -DALPHABET_ASCII95
```
Reference bin (the May-2026 engine at eb28ce8, `holcus same stuff seemy`): see `../README.md`, `src/PtolC_eb28ce8/`.
