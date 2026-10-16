#!/usr/bin/env python3
"""build_paper_notebooks.py — build and execute the paper's companion notebooks.

    PtolemyDesktop/.venv/bin/python VAPMIP/notebooks/paper/build_paper_notebooks.py [NN ...]      # Python notebooks 17..22
    /usr/bin/python3               VAPMIP/notebooks/paper/build_paper_notebooks.py --c [07c 08c]  # C notebooks (kernel `c`)

Specs live in specs_paper.py. Python notebooks run in the venv kernel (PYTHONHASHSEED=0, kernelspec kept beside the Tuning-the-Engine
notebooks); C notebooks run on the `c` kernel (jupyter-c-kernel, each cell is a standalone C program compiled with gcc), started with the
notebook's own directory as the working directory. Cells run with errors allowed: an error is a recorded result.
"""
import os, sys, time, queue, importlib.util
import nbformat

HERE = os.path.dirname(os.path.abspath(__file__))
VAPMIP = os.path.abspath(os.path.join(HERE, "..", ".."))
spec = importlib.util.spec_from_file_location("specs_paper", os.path.join(HERE, "specs_paper.py"))
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)


def make(nbspec, kernel_display, kernel_name, lang):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": kernel_display, "language": lang, "name": kernel_name}
    cells = []
    for kind, text in nbspec["cells"]:
        cells.append(nbformat.v4.new_markdown_cell(text) if kind == "md" else nbformat.v4.new_code_cell(text))
    nb.cells = cells
    return nb


def run_python(key):
    from nbclient import NotebookClient
    os.environ["JUPYTER_PATH"] = os.path.join(VAPMIP, "notebooks", "tuning_the_engine", ".jupyter_path")
    nbspec = S.PY[key]
    nb = make(nbspec, "Python 3", "python3", "python")
    t0 = time.time()
    NotebookClient(nb, timeout=1200, kernel_name="ptolemy-venv", allow_errors=True,
                   resources={"metadata": {"path": HERE}}).execute()
    out = os.path.join(HERE, nbspec["file"])
    nbformat.write(nb, out)
    return summarise(nb, out, t0)


def run_c(key):
    from jupyter_client.manager import start_new_kernel
    nbspec = S.C[key]
    nb = make(nbspec, "C", "c", "c")
    cdir = os.path.join(VAPMIP, "notebooks", "c")
    km, kc = start_new_kernel(kernel_name="c", startup_timeout=60, cwd=cdir)
    t0 = time.time(); n = 0
    for c in nb.cells:
        if c.cell_type != "code": continue
        n += 1
        kc.execute(c.source); outs = []
        while True:
            try: m = kc.get_iopub_msg(timeout=120)
            except queue.Empty:
                outs.append(nbformat.v4.new_output("error", ename="Timeout", evalue="no reply in 120 s", traceback=[])); break
            t = m["msg_type"]
            if t == "stream": outs.append(nbformat.v4.new_output("stream", name=m["content"]["name"], text=m["content"]["text"]))
            elif t == "error": outs.append(nbformat.v4.new_output("error", ename=m["content"]["ename"], evalue=m["content"]["evalue"], traceback=m["content"].get("traceback", [])))
            elif t == "status" and m["content"]["execution_state"] == "idle": break
        c.outputs = outs; c.execution_count = n
    kc.stop_channels(); km.shutdown_kernel(now=True)
    out = os.path.join(cdir, nbspec["file"])
    nbformat.write(nb, out)
    return summarise(nb, out, t0)


def summarise(nb, out, t0):
    errs = sum(1 for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.output_type == "error")
    tail = ""
    for c in reversed(nb.cells):
        if c.cell_type != "code": continue
        for o in c.get("outputs", []):
            if o.output_type == "stream":
                lines = [l for l in o.text.strip().splitlines() if "PASS" in l or "FAIL" in l]
                if lines: tail = lines[-1]
        if tail: break
    print(f"{os.path.relpath(out, VAPMIP)}: {len(nb.cells)} cells, {errs} cell errors, {time.time()-t0:.1f}s | {tail}")
    return errs


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--c":
        for k in (args[1:] or sorted(S.C)): run_c(k)
    else:
        for k in (args or sorted(S.PY)): run_python(k)
