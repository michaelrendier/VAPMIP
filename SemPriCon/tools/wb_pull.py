#!/usr/bin/env python3
"""wb_pull.py — print one named block from the workbench wiki page (blocks are <!-- @BLOCK name --> ... <!-- @END name -->).
    python3 tools/wb_pull.py test_chinese_v2.bin      python3 tools/wb_pull.py --list"""
import os, re, sys
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "wiki", "Tuning-the-Semantic-Prime-Concept-Engine", "11_baseline_mapping_zh_en.md")
t = open(PAGE, encoding="utf-8").read()
if sys.argv[1:] == ["--list"]: print("\n".join(re.findall(r"<!-- @BLOCK (.*?) -->", t))); sys.exit()
m = re.search(r"<!-- @BLOCK " + re.escape(sys.argv[1]) + r" -->\n(.*?)\n<!-- @END ", t, re.S)
print(m.group(1) if m else f"no block {sys.argv[1]!r}; try --list", file=sys.stdout if m else sys.stderr)
