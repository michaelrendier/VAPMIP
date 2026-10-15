#!/usr/bin/env python3
"""build_notebooks.py — turn specs/phase_*.py into executed .ipynb files.

Run with the PtolemyDesktop venv (it has nbformat/nbclient/ipykernel):
    PtolemyDesktop/.venv/bin/python VAPMIP/notebooks/tuning_the_engine/build_notebooks.py [NN ...]

Each spec defines  TITLE, DATE, PAGE (wiki file name), BYLINE, CELLS = [("md"|"code", text), ...].
Cells are executed with allow_errors=True: an exception is a recorded result, never swallowed.
"""
import os, sys, glob, importlib.util, time
import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))
# the system python3 kernel carries a ~/.local numpy that shadows the apt one (ABI mismatch with nltk/pandas);
# execute in the PtolemyDesktop venv through a kernelspec kept beside this file, but save metadata as plain python3
os.environ["JUPYTER_PATH"] = os.path.join(HERE, ".jupyter_path")
KERNEL = "ptolemy-venv"

def load(path):
    spec = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def build(path, execute=True):
    s = load(path)
    nn = os.path.basename(path)[len("phase_"):-3]
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    head = (f"# Phase {s.LABEL} — {s.TITLE}\n"
            f"**Tuning the Engine, {s.DATE}** · wiki page: "
            f"[`{s.PAGE}`](../../docs/wiki/Tuning-the-Engine/{s.PAGE}) · {s.BYLINE}\n\n"
            "> Companion notebook. It runs the machinery the page refers to and records, "
            "claim by claim, what reproduces (`PASS`), what does not (`FAIL`, kept), and what the "
            "page states with no executable counterpart (`PROSE`). Maths in Unicode; code identifiers as in the repo.")
    cells = [nbformat.v4.new_markdown_cell(head),
             nbformat.v4.new_code_cell("from tte import *\nL = Ledger(%r)" % f"Phase {s.LABEL}")]
    for kind, text in s.CELLS:
        cells.append(nbformat.v4.new_markdown_cell(text) if kind == "md" else nbformat.v4.new_code_cell(text))
    cells.append(nbformat.v4.new_markdown_cell("## Ledger"))
    cells.append(nbformat.v4.new_code_cell("_n = L.show()"))
    nb.cells = cells
    out = os.path.join(HERE, f"phase_{nn}.ipynb")
    t0 = time.time()
    if execute:
        NotebookClient(nb, timeout=900, kernel_name=KERNEL, allow_errors=True,
                       resources={"metadata": {"path": HERE}}).execute()
    nbformat.write(nb, out)
    errs = sum(1 for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.output_type == "error")
    tail = ""
    for o in nb.cells[-1].get("outputs", []):
        if o.output_type == "stream": tail = o.text.strip().splitlines()[-1]
    print(f"phase_{nn}: {len(nb.cells)} cells, {errs} cell errors, {time.time()-t0:.1f}s | {tail}")
    return errs

if __name__ == "__main__":
    want = sys.argv[1:]
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "phase_*.py"))):
        nn = os.path.basename(p)[6:-3]
        if want and nn not in want: continue
        build(p)
