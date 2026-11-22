#!/usr/bin/env python3
"""verify_against_c.py — run the compiled eb28ce8 binary and monad_py on the same prompts against the same bin; compare byte for byte."""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import monad_py as mp
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BIN = os.path.join(ROOT, "build", "PtolC_eb28ce8", "ptolemy")
STORE = os.path.join(ROOT, "dirty", "monad_wordnet_v4_20260519.bin")

def c_reply(prompt, mode="-W"):
    env = dict(os.environ, PTOLEMY_HOME=os.path.join(ROOT, "scratch_home"), HOME=os.path.join(ROOT, "scratch_home"))
    r = subprocess.run([BIN, "-c", STORE, mode, prompt, "-n"], capture_output=True, text=True, env=env)
    return r.stdout.rstrip("\n")

if __name__ == "__main__":
    t = time.time(); m = mp.Monad.from_bin(STORE); print("loaded", round(time.time() - t, 1), "s")
    prompts = ["what is your name", "can you hear what i am typing", "who are you", "what is a tree", "good morning", "the cat sat on the mat",
               "how do you do", "tell me about water"]
    ok = 0
    for p in prompts:
        c = c_reply(p); m = mp.Monad.from_bin(STORE); tr = {}; py = m.speak_wick(p, 50, tr)
        same = (c == py); ok += same
        print(("MATCH " if same else "DIFF  ") + repr(p), "\n   C :", repr(c), "\n   Py:", repr(py))
    print(f"{ok}/{len(prompts)} identical")
