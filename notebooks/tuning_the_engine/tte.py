"""tte.py — shared helper for the Tuning-the-Engine notebooks (one per wiki phase).

Every notebook starts with `from tte import *`. It does three things only:
  1. puts the VAPMIP repo, VAPMIP/engines and ValaQuenta's parent on sys.path;
  2. exposes the constants every phase uses (same values as engines/_sedenion.py);
  3. gives a Ledger: each claim a notebook tests is recorded with its measured
     value and PASS / FAIL / PROSE. A FAIL stays in the output — failures are
     results, not something to hide (see the wiki's own retractions).
"""
import os, sys, math, json, time, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
VAPMIP = os.path.abspath(os.path.join(HERE, "..", ".."))
PLACE = os.path.abspath(os.path.join(VAPMIP, ".."))
WIKI = os.path.join(VAPMIP, "docs", "wiki", "Tuning-the-Engine")
for p in (VAPMIP, os.path.join(VAPMIP, "engines"), PLACE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np

OMEGA_ZS = 0.56714329040978387299996866221          # W(1), Lambert fixed point
LN10 = math.log(10.0)
D_STAR = OMEGA_ZS / LN10                             # 0.24631 "The Boundary"
GAP = 1.0 / (1000.0 * math.sqrt(2.0))                # 0.000707357
PHI = (1 + math.sqrt(5)) / 2


def page(name):
    """Return the text of a wiki page (by file name prefix, e.g. '01')."""
    for f in sorted(os.listdir(WIKI)):
        if f.startswith(name):
            with open(os.path.join(WIKI, f), encoding="utf-8") as fh:
                return fh.read()
    raise FileNotFoundError(name)


def try_import(modname, *, attr=None):
    """Import a repo module; return (module_or_attr, None) or (None, error_text).
    Used so a notebook reports a missing/broken module as a result instead of dying."""
    try:
        m = importlib.import_module(modname)
        return (getattr(m, attr) if attr else m), None
    except BaseException as ex:                       # noqa: BLE001 — report, don't hide
        return None, f"{type(ex).__name__}: {ex}"


class Ledger:
    """Claim ledger. L.check(claim, ok, detail) -> records PASS/FAIL; L.prose(claim) -> PROSE."""
    def __init__(self, title="claims"):
        self.title, self.rows = title, []

    def check(self, claim, ok, detail=""):
        self.rows.append(("PASS" if ok else "FAIL", claim, str(detail)))
        return bool(ok)

    def prose(self, claim, why="stated on the page; no executable counterpart in the repo"):
        self.rows.append(("PROSE", claim, why))

    def skip(self, claim, why):
        """The claim has an executable counterpart that cannot run in this environment (missing data/hardware)."""
        self.rows.append(("SKIP", claim, str(why)))

    def show(self):
        w = max(len(r[1]) for r in self.rows) if self.rows else 10
        print(f"LEDGER — {self.title}")
        for s, c, d in self.rows:
            print(f"  [{s:5}] {c}" + (f"\n          {d}" if d else ""))
        n = {k: sum(1 for r in self.rows if r[0] == k) for k in ("PASS", "FAIL", "PROSE", "SKIP")}
        print(f"  -> PASS {n['PASS']} · FAIL {n['FAIL']} · PROSE {n['PROSE']}" + (f" · SKIP {n['SKIP']}" if n['SKIP'] else ""))
        return n

def scratch(prefix="tte_"):
    """A fresh temp dir under $CLAUDE_JOB_DIR/tmp when set (background jobs share /tmp), else the system temp."""
    import tempfile
    base = os.path.join(os.environ["CLAUDE_JOB_DIR"], "tmp") if os.environ.get("CLAUDE_JOB_DIR") else None
    if base: os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix=prefix, dir=base)


def ptol_raw(text, eye="H", home=None):
    """Run PtolC/ptol -r on `text` with HOME redirected (ptol writes papers into ~/.ptolemy).
    Returns dict(header=str, sigma_self, gamma, u, scalars[16], primes[...], sigma_rb[16])."""
    import subprocess
    home = home or scratch("ptolhome_")
    os.makedirs(os.path.join(home, ".ptolemy"), exist_ok=True)
    pr = subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "-r", "-eye", eye, text],
                        capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=60)
    out = pr.stdout.splitlines()
    head = [l for l in pr.stderr.splitlines() if l.startswith("eye:")][0]      # the Eye line is on stderr
    def num(tag):
        t = head.split(tag)[1].split()[0]; return float(t)
    parts, cur = [], []
    for l in out:
        if l.strip() == "---": parts.append(cur); cur = []
        else: cur.append(l)
    parts.append(cur)
    return dict(header=head, sigma_self=num("σ_self:"), gamma=num("Γ:"), u=num("u:"),
                scalars=[float(x) for x in parts[0]], primes=[int(x) for x in parts[1] if x.strip().lstrip("-").isdigit()],
                sigma_rb=[float(x) for x in parts[2][:16]] if len(parts) > 2 else [])


def zd_vectors():
    """The 84 sedenion zero-divisor vectors e_a ± e_b (a in 1..7, b in 8..15) that have an annihilating partner.
    Returns (vectors:{key:list16}, ordered_pairs:set) computed from engines/_sedenion.cd_mul."""
    import itertools
    from _sedenion import cd_mul
    vecs = {}
    for a in range(1, 8):
        for b in range(8, 16):
            for sg in (1, -1):
                v = [0.0]*16; v[a] = 1.0; v[b] = float(sg); vecs[(a, b, sg)] = v
    pairs = set()
    for (ka, va), (kb, vb) in itertools.product(vecs.items(), vecs.items()):
        if max(abs(x) for x in cd_mul(va, vb)) < 1e-12: pairs.add((ka, kb))
    return vecs, pairs

__all__ = [n for n in dir() if not n.startswith("_")]
