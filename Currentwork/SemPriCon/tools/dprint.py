"""dprint.py — Cody's dPrint() protocol (original: Ptolemy2/Phaleron/APISniff/APISniff.py:421): after a value changes, print "name = value" to stdout.
Global flag: environment variable PTOL_DPRINT (unset or "0" = off).  Every line starts "[dp] " so the feed can be grepped.  Unlike the original, a falsy value
(0, "", []) is printed as itself, not dropped."""
import os
ON = os.environ.get("PTOL_DPRINT", "0") not in ("", "0")

def dprint(label, value=None, *, always=False):
    if ON or always:
        print(f"[dp] {label}" + ("" if value is None else f" = {value!r}"), flush=True)
