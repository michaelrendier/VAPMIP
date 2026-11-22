#!/usr/bin/env python3
"""make_paper.py — builds The_Golden_Ratio_Monad.md from template.md.

Every {{key}} is looked up in the dict evidence.collect() returns (fresh runs of the code).  Verbatim source comes from
  {{C:file:function}}                      the whole C function, cut from src/PtolC_eb28ce8/
  {{EXC:file:before:after:start::end}}      the lines from the first line containing `start` to the first later line containing `end`,
                                            plus `before` lines above and `after` lines below (an excerpt; the paper says so)
  {{LINES:file:function}}                   the line range of a function
--check : rebuild and compare with the committed text; nonzero exit if they differ.   --cached : reuse evidence.json (fast; for typography only)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(ROOT, "src", "PtolC_eb28ce8"); OUT = os.path.join(HERE, "The_Golden_Ratio_Monad.md")


def excerpt(fname, before, after, start, end):
    L = open(os.path.join(SRC, fname), encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(L) if start in l)
    j = next(k for k in range(i, len(L)) if end in L[k])
    a, b = i - int(before), j + int(after)
    return f"{chr(10).join(L[a:b + 1])}", (a + 1, b + 1)


def build(cached=False):
    if cached:
        E = json.load(open(os.path.join(HERE, "evidence.json")))
    else:
        sys.path.insert(0, HERE); import evidence
        E = {k: str(v) for k, v in evidence.collect().items()}
        json.dump(E, open(os.path.join(HERE, "evidence.json"), "w"), indent=1, ensure_ascii=False)
    T = open(os.path.join(HERE, "template.md"), encoding="utf-8").read()
    def sub(m):
        k = m.group(1)
        if k.startswith("EXC:"):
            f, b, a, rest = k[4:].split(":", 3); s, e = rest.split("::")
            txt, (x, y) = excerpt(f, b, a, s, e); return txt
        if k.startswith("EXCL:"):
            f, b, a, rest = k[5:].split(":", 3); s, e = rest.split("::")
            txt, (x, y) = excerpt(f, b, a, s, e); return f"{x}–{y}"
        if k.startswith("PYFN:"):
            import ast; rel, name = k[5:].split(":"); src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name); return ast.get_source_segment(src, node)
        if k.startswith("LINES:"):
            return E["L:" + k[6:]]
        if k not in E:
            raise KeyError(f"template key not in evidence: {k}")
        return str(E[k])
    return re.sub(r"\{\{([^{}]+)\}\}", sub, T)


if __name__ == "__main__":
    text = build(cached="--cached" in sys.argv)
    if "--check" in sys.argv:
        old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        norm = lambda t: re.sub(r"took \d+ s", "took N s", t)   # the run time is the one number that is not reproducible
        if norm(old) == norm(text): print("check: paper text matches a fresh run"); sys.exit(0)
        print("check: DIFFERS from a fresh run"); sys.exit(1)
    open(OUT, "w", encoding="utf-8").write(text); print("wrote", OUT, len(text.split("\n")), "lines")
