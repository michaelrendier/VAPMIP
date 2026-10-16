"""pn.py — shared helper for the paper's companion notebooks (VAPMIP/notebooks/paper/).

Every Python notebook starts with `from pn import *`. It puts the repo on sys.path, exposes the six test prompts, a Ledger
(PASS / FAIL / PROSE / SKIP, failures kept) and the helpers that run the compiled `ptol` safely:
  * plain `ptol`, `-r`, `-s/-b/-H` write files into $HOME/.ptolemy, so they run with a scratch HOME;
  * `ptol -say` writes nothing and its sentence bridge needs the REAL home (user site-packages and ~/nltk_data),
    so it runs with the real HOME; with a scratch HOME ptol silently falls back to the word bag.
"""
import os, sys, math, time, io, json, contextlib, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VAPMIP = os.path.abspath(os.path.join(HERE, "..", ".."))
PLACE = os.path.abspath(os.path.join(VAPMIP, ".."))
for p in (VAPMIP, PLACE, os.path.join(PLACE, "PtolemyDesktop"), os.path.join(VAPMIP, "notebooks", "tuning_the_engine")):
    if p not in sys.path:
        sys.path.insert(0, p)
from tte import Ledger                                   # the same claim ledger the Tuning-the-Engine notebooks use

PTOL = os.path.join(VAPMIP, "PtolC", "ptol")
PTOLEMY = os.path.join(VAPMIP, "PtolC", "ptolemy")
PROMPTS = ["finger pointer", "what is a tree", "neutron generation in different reactor types",
           "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered"]


@contextlib.contextmanager
def quiet():
    """Silence the import-time chatter of the monad modules (they print status lines)."""
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        yield


def scratch_home():
    d = tempfile.mkdtemp(prefix="pn_home_")
    os.makedirs(os.path.join(d, ".ptolemy"), exist_ok=True)
    return d


def ptol(*args, real_home=False, timeout=180):
    """Run the compiled monad. Returns (stdout, stderr, seconds)."""
    env = os.environ.copy() if real_home else dict(os.environ, HOME=scratch_home())
    t = time.perf_counter()
    r = subprocess.run([PTOL, *args], capture_output=True, text=True, cwd=os.path.dirname(PTOL), env=env, timeout=timeout)
    return r.stdout, r.stderr, time.perf_counter() - t


def ptol_say(prompt):
    """`ptol -say` with the real HOME (writes no files). Returns (sentence, status_line, seconds)."""
    out, err, dt = ptol("-say", prompt, real_home=True)
    status = next((l.strip() for l in err.splitlines() if "σ=" in l), "")
    return out.strip(), status, dt
