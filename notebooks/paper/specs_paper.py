"""specs_paper.py — cell specs for the paper's companion notebooks.

PY[key] / C[key] = {"file": ..., "cells": [("md"|"code", text), ...]}. C cells carry the REAL function text, extracted at build time from the
source file with its path and line range, so a notebook can never drift from the code it shows.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
VAPMIP = os.path.abspath(os.path.join(HERE, "..", ".."))


def cfunc(relpath, name, with_comment=True):
    """Return (text, first_line, last_line) of the C function `name` in VAPMIP/<relpath> (signature line to the matching brace)."""
    lines = open(os.path.join(VAPMIP, relpath), encoding="utf-8").read().split("\n")
    pat = re.compile(r"^(static\s+)?[A-Za-z_][\w\s\*]*?\b" + re.escape(name) + r"\s*\(")
    for i, l in enumerate(lines):
        if pat.match(l) and not l.rstrip().endswith(";"):
            depth, started, j = 0, False, i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                started = started or "{" in lines[j]
                if started and depth == 0: break
                j += 1
            return "\n".join(lines[i:j + 1]), i + 1, j + 1
    raise KeyError(name)


def cblock(relpath, start_pat, end_pat):
    lines = open(os.path.join(VAPMIP, relpath), encoding="utf-8").read().split("\n")
    a = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    b = next(i for i in range(a, len(lines)) if re.search(end_pat, lines[i]))
    return "\n".join(lines[a:b + 1]), a + 1, b + 1


PRE = 'from pn import *\nL = Ledger("%s")\n'
SHOW = "_n = L.show()"
PY, C = {}, {}

# ───────────────────────────── 17 · the Null Operator and the hub ─────────────────────────────
PY["17"] = {"file": "17_null_operator_and_hub.ipynb", "cells": [
("md", """# 17 · The Null Operator and the hub (paper §3)
Code: `ValaQuenta/modules/box_kite/maths.py` (`multiply`, `e0_is_outside`, `fixed_point_gluing`, `fixed_point_weight`, `box_kites`, `chart_spectrum`, `glued_graph`) and `VAPMIP/scaled_mind_eye_boxkite_kernel_monad.py` (`HUB_PSI`, `MindEyeBoxKiteKernel.throw_fiber`).
Every cell runs the real code; each claim is a ledger row (PASS / FAIL, failures kept)."""),
("code", PRE % "17 · the Null Operator and the hub" + """import random
with quiet():
    from ValaQuenta.modules.box_kite import maths as bk
    import scaled_mind_eye_boxkite_kernel_monad as K
rnd = random.Random(2026); rv = lambda: [rnd.uniform(-1, 1) for _ in range(16)]
E0 = [1.0] + [0.0] * 15; nrm = lambda v: math.sqrt(sum(c * c for c in v))
print("HUB_PSI =", K.HUB_PSI)"""),
("md", "## 3.1 e₀ is the identity"),
("code", """w = max(max(abs(a - b) for a, b in zip(bk.multiply(E0, x), x)) for x in (rv() for _ in range(300)))
L.check("e₀ is the left identity of the sedenion product (300 random vectors)", w < 1e-12, f"max |e₀·x − x| = {w:.1e}")
w = max(max(abs(a - b) for a, b in zip(bk.multiply(x, E0), x)) for x in (rv() for _ in range(300)))
L.check("e₀ is the right identity", w < 1e-12, f"max |x·e₀ − x| = {w:.1e}")
dev = max(abs(nrm(bk.multiply(E0, x)) - nrm(x)) for x in (rv() for _ in range(200)))
L.check("multiplying by e₀ preserves the norm: e₀ is not a zero divisor", dev < 1e-12, f"{dev:.1e}")
cm = max(max(abs(c) for c in bk.commutator(0, j)) for j in range(16))
L.check("e₀ commutes with every basis element", cm < 1e-12, f"{cm:.1e}")"""),
("md", "## 3.2 e₀ is outside every chart"),
("code", """o = bk.e0_is_outside(); print(o)
L.check("e₀ is not a point of PG(3,2), is in no assessor, and its associator vanishes against every pair", o["e0_is_outside_the_geometry"], str(o))
kites = bk.box_kites(); allv = [a for v in kites.values() for a in v]
L.check("7 box kites of 6 assessors; 42 assessors in all; none shared", len(kites) == 7 and {len(v) for v in kites.values()} == {6} and len(allv) == len(set(allv)) == 42)
spec = sorted(round(x, 6) for x in bk.chart_spectrum(1)); print("chart 1 Laplacian spectrum:", spec)
L.check("each chart is an octahedron: Laplacian spectrum {0,4,4,4,6,6}", all(sorted(round(x, 6) for x in bk.chart_spectrum(s)) == [0, 4, 4, 4, 6, 6] for s in kites))"""),
("md", "## 3.3 the hub the seven charts share"),
("code", """g = bk.glued_graph(); sp = bk.glued_spectrum(); zero_modes = sum(1 for x in sp if abs(x) < 1e-9)
L.check("adjacency: zero edges between charts", g.get("cross_strut_edges", g.get("cross_edges")) in (0, []), repr(g.get("cross_strut_edges", g.get("cross_edges"))))
L.check("the glued atlas has exactly 7 zero modes (one per chart)", zero_modes == 7, f"{zero_modes} of {len(sp)}")
mem = bk.index_chart_membership(); none = sorted(i for i in range(16) if not mem.get(i))
L.check("skeleton: 14 indices each lie in 6 of the 7 charts; exactly e₀ and e₈ lie in none", sum(1 for v in mem.values() if len(v) == 6) == 14 and none == [0, 8], f"in no chart: {none}")
fg = bk.fixed_point_gluing(); print(fg["reading"])
L.check("fixed_point_weight of the hub is exactly 1", bk.fixed_point_weight(K.HUB_PSI) == 1.0)"""),
("md", "## 3.4 the structural constant at a landing"),
("code", """with quiet(): kern = K.MindEyeBoxKiteKernel()
worst = 0.0
for s in kern.kite.struts:
    for d in (0.0, 0.2, 0.6, 0.9, 1.0):
        with quiet(): t = kern.throw_fiber(s, d, gamma_companion=False)
        worst = max(worst, abs(t.fixed_point_weight - (1 - d * d)))
L.check("fixed_point_weight at a fiber landing equals 1 − depth² for all 7 struts × 5 depths", worst < 1e-12, f"max deviation {worst:.1e}")
with quiet(): t = kern.throw_fiber(1, 0.6, gamma_companion=False)
print("psi after one throw (strut 1, depth 0.6):", [round(c, 4) for c in t.psi])
L.check("a throw leaves energy only on e₀ and the chosen assessor's two indices", sum(1 for c in t.psi if abs(c) > 1e-15) == 3, str([i for i, c in enumerate(t.psi) if abs(c) > 1e-15]))"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── 18 · the sentence bridge ─────────────────────────────
PY["18"] = {"file": "18_ptol_sentence_bridge.ipynb", "cells": [
("md", """# 18 · The sentence path of the compiled monad (paper §8)
Code: `VAPMIP/PtolC/ptol.c` (`console_speak`, `infer_speech_act`, `get_monad_sentence`), `VAPMIP/engine/grammar/ptolc_bridge.py`.
`ptol -say` runs with the **real** HOME (it writes no files; the bridge needs the user's site-packages and `~/nltk_data`)."""),
("code", PRE % "18 · the sentence path of the compiled monad" + """rows = []
for p in ["what is a tree", "finger pointer", "can you play the piano?"]:
    s, status, dt = ptol_say(p); rows.append((p, s, status, dt)); print(f"{p!r:30} -> {s!r}   {status}   {dt:.1f} s")
L.check("ptol -say returns one non-empty line for each prompt", all(r[1] for r in rows))
L.check("the status line reports σ_self, Γ and the firing primes", all("σ=" in r[2] and "Γ=" in r[2] for r in rows))"""),
("md", "## The bridge on its own: three lines in, one line out"),
("code", """def bridge(text):
    r = subprocess.run(["python3", "-m", "engine.grammar.ptolc_bridge"], input=text, capture_output=True, text=True, cwd=VAPMIP, timeout=120)
    return r.returncode, r.stdout.strip()
for txt in ("GAMMA -0.58\\nACT define_X\\nWORDS tree\\n", "GAMMA 0.30\\nACT how\\nWORDS tree plant grow\\n", "GAMMA -0.58\\nACT define_X\\nWORDS\\n"):
    print(repr(txt), "->", bridge(txt))
rc, out = bridge("GAMMA -0.58\\nACT define_X\\nWORDS tree\\n")
L.check("a valid word bag gives exit 0 and one sentence", rc == 0 and out != "", out)
rc, out = bridge("GAMMA -0.58\\nACT define_X\\nWORDS\\n")
L.check("ptolc_bridge docstring: on a bad word list it prints nothing and exits non-zero; with an EMPTY list it does so (so the C side keeps the word bag)", rc != 0 and out == "", f"rc={rc} out={out!r}: with no words it returns a sentence anyway")"""),
("md", "## The guaranteed fallback is real: with no usable HOME, ptol keeps the word bag"),
("code", """so, se, dt = ptol("-say", "what is a tree", real_home=False)
print("scratch HOME:", repr(so.strip()), f"{dt:.1f} s")
s_real, _, dt_real = ptol_say("what is a tree"); print("real HOME   :", repr(s_real), f"{dt_real:.1f} s")
L.check("with a scratch HOME the bridge cannot run and ptol keeps the word bag (fast), not a sentence", so.strip() != s_real and dt < dt_real, f"{dt:.1f} s vs {dt_real:.1f} s")"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── 19 · parser tables ─────────────────────────────
PY["19"] = {"file": "19_parser_tables.ipynb", "cells": [
("md", """# 19 · The parser: C table against Python table (paper §9)
Code: `VAPMIP/PtolC/zork.c` (`VERBS[]`, `zork_parse`), `VAPMIP/zork_parser.py` (`OPERATOR_VERBS`, `VERB_TO_OP`, `OP_NAMES`). Exhaustive comparison."""),
("code", PRE % "19 · parser tables" + """import re
with quiet(): import zork_parser as zp
c = open(os.path.join(VAPMIP, "PtolC", "zork.c")).read(); tbl = c[c.index("VerbEntry VERBS[]"):]; tbl = tbl[:tbl.index("};")]
cv = {m.group(1): int(m.group(2)) for m in re.finditer(r'\\{\\s*"([^"]+)"\\s*,\\s*(\\d+)\\s*\\}', tbl)}
pv = dict(zp.VERB_TO_OP)
print(len(cv), "verbs in the C table;", len(pv), "in the Python table")
print("operators:", {k: v for k, v in zp.OP_NAMES.items()})"""),
("code", """only_py = sorted(set(pv) - set(cv)); only_c = sorted(set(cv) - set(pv)); diff = sorted(v for v in set(cv) & set(pv) if cv[v] != pv[v])
print("only in Python:", only_py); print("only in C:", only_c); print("same verb, different operator:", [(v, cv[v], pv[v]) for v in diff])
L.check("both tables cover all 16 operators", len(set(cv.values())) == 16 and len(set(pv.values())) == 16)
L.check("every compiled verb is in the Python table", not only_c, str(only_c))
L.check("zork.h: the C table 'mirrors zork_parser.py exactly' (no verb maps to a different operator)", not diff, str([(v, cv[v], pv[v]) for v in diff]))
L.check("zork.h: same verb table (the Python table has no extra verbs)", not only_py, str(only_py))
multi = {}
for op, vs in zp.OPERATOR_VERBS.items():
    for v in vs: multi.setdefault(v, []).append(op)
multi = {v: o for v, o in multi.items() if len(set(o)) > 1}
print("verbs listed under more than one operator in Python:", multi)
agree = sorted(v for v in multi if cv.get(v) == pv[v])
L.check("cause: Python lists 6 verbs under two operators and keeps the last; the C table lists each once; 5 of the 6 then differ", len(multi) == 6 and sorted(set(multi) - set(agree)) == sorted(diff), f"doubly listed: {sorted(multi)}; agree: {agree}; differ: {diff}")"""),
("md", "## One line through the compiled REPL"),
("code", """r = subprocess.run([PTOLEMY, "-r", "-n"], input="what is a tree\\n\\n", capture_output=True, text=True, timeout=60, cwd=os.path.dirname(PTOLEMY))
z = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("[zork]")]
print(z)
L.check("`what is a tree` parses to operator e0/identity with prompt `identity is tree`", any("e0/identity" in l and "identity is tree" in l for l in z))"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── 20 · the kernel ─────────────────────────────
PY["20"] = {"file": "20_scaled_kernel_fibers.ipynb", "cells": [
("md", """# 20 · The kernel: hub, fiber, run (paper §12)
Code: `VAPMIP/scaled_mind_eye_boxkite_kernel_monad.py` (`MindEyeBoxKiteKernel`, `hub_report`, `throw_fiber`, `run_boxkite`, `FiberThrow`), `VAPMIP/19D_boxkite_context_monad.py` (`GaugeEye.continuous_snapshot`, `GaugeHands.emit_steered`)."""),
("code", PRE % "20 · the kernel" + """with quiet():
    import scaled_mind_eye_boxkite_kernel_monad as K
    kern = K.MindEyeBoxKiteKernel()
    hub = kern.hub_report()
print({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in list(v.items())[:3]}) for k, v in hub.items()})
L.check("the hub is confirmed before it is used (e₀ outside the geometry)", hub["e0_is_outside"]["e0_is_outside_the_geometry"])
L.check("hub fixed_point_weight is 1", abs(hub["hub_fixed_point_weight"] - 1.0) < 1e-12)"""),
("md", "## Run a boxkite: one hub-anchored fiber per strut"),
("code", """with quiet(): throws = kern.run_boxkite([(s, 0.6) for s in kern.kite.struts])
for t in throws: print(" ", t)
L.check("seven fibers, one per strut", [t.strut for t in throws] == list(range(1, 8)))
L.check("fixed_point_weight at every landing is 1 − 0.6² = 0.64", all(abs(t.fixed_point_weight - 0.64) < 1e-12 for t in throws))
print("is_zero_divisor by strut:", {t.strut: t.is_zero_divisor for t in throws})
print("windspeed by strut:", {t.strut: round(t.a_matrix_basin_windspeed, 6) for t in throws})
print("sigma_self by strut:", {t.strut: round(t.sigma_self, 6) for t in throws}, "(the kernel's own red/blue split: red = k ≥ 8)")"""),
("md", "## Each throw starts from the hub, never from the previous landing"),
("code", """with quiet():
    a = kern.throw_fiber(3, 0.6, gamma_companion=False); kern.throw_fiber(5, 0.9, gamma_companion=False); b = kern.throw_fiber(3, 0.6, gamma_companion=False)
L.check("throwing strut 3 again after other throws gives the identical landing (no residue between fibers)", a.psi == b.psi and a.fixed_point_weight == b.fixed_point_weight)
try: kern.throw_fiber(1, 1.5)
except ValueError as e: print("depth 1.5 refused:", e); L.check("a depth outside [0,1] is refused", True, str(e))
else: L.check("a depth outside [0,1] is refused", False, "no error")"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── 21 · the encounter ─────────────────────────────
PY["21"] = {"file": "21_scaled_adapter_encounter.ipynb", "cells": [
("md", """# 21 · The encounter: from a prompt to a sentence in the Python monad (paper §13)
Code: `PtolemyDesktop/ptolemy_console.py` (`build_encounter_19d`, `ScaledMindEyeMonadAdapter.say`), `VAPMIP/19D_rotary_boxkite_monad.py` (`NineteenDMindsEye.create_context`, `RotaryBoxKite19D.process_input`), `VAPMIP/ptolemy_monad.py` (`infer_direction`).
This kernel runs with `PYTHONHASHSEED=0`; the last cells vary the seed."""),
("code", PRE % "21 · the encounter" + """with quiet():
    import ptolemy_console as pc
    ad = pc.ScaledMindEyeMonadAdapter()
print(ad.kind)
rounds = []
for rnd_i in (1, 2):
    rows = []
    for p in PROMPTS:
        t = time.perf_counter()
        with quiet(): reply, meta = ad.say(p)
        rows.append((p, reply, meta, time.perf_counter() - t))
    rounds.append(rows)
for (p, r1, m1, t1), (_, r2, m2, t2) in zip(*rounds):
    print(f"> {p}\\n    {r1}\\n    meta: { {k: m1[k] for k in m1 if k in ('via','direction','strut','verdict')} }   cold {t1*1000:.0f} ms, warm {t2*1000:.1f} ms")
L.check("within a process the second round returns the same replies as the first", all(a[1] == b[1] for a, b in zip(*rounds)))"""),
("md", "## NULL first: nothing is fabricated when nothing resolves"),
("code", """nulls = [(p, r) for p, r, m, t in rounds[1] if r.startswith("(19D:")]
for p, r in nulls: print(f"> {p}\\n    {r}")
kinds = {m.get("via") for p, r, m, t in rounds[1] if r.startswith("(19D:")}; print("non-sentence replies by kind:", sorted(kinds))
L.check("some test prompts end in an explicit non-sentence reply (no verb: NULL; no dominant signal: observe; direction without a speech act: unmapped), none fabricated", len(nulls) >= 1, f"{len(nulls)} of {len(PROMPTS)}: {sorted(kinds)}")
L.check("each such reply says why and carries no generated sentence (no hub-fiber line)", all("hub fiber" not in r for p, r in nulls))
answered = [(p, r, m) for p, r, m, t in rounds[1] if m.get("via") == "scaled_mind_eye"]
L.check("a resolved prompt reports its direction, its strut and the fixed-point weight of the throw", all("hub fiber" in r and "fixed_point_weight" in r for p, r, m in answered), f"{len(answered)} resolved")"""),
("md", "## Across hash seeds (five fresh processes)"),
("code", """CHILD = r'''
import sys, json, io, contextlib
sys.path.insert(0, %r); sys.path.insert(0, %r)
q = io.StringIO()
with contextlib.redirect_stdout(q), contextlib.redirect_stderr(q):
    import ptolemy_console as pc
    ad = pc.ScaledMindEyeMonadAdapter()
    out = [ad.say(p)[0] for p in %r]
print(json.dumps(out))
''' % (VAPMIP, os.path.join(PLACE, "PtolemyDesktop"), PROMPTS)
seeds, per = [0, 1, 2, 3, 4], {p: [] for p in PROMPTS}
for sd in seeds:
    r = subprocess.run([sys.executable, "-c", CHILD], capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED=str(sd)), timeout=600)
    for p, rep in zip(PROMPTS, json.loads(r.stdout.strip().splitlines()[-1])): per[p].append(rep)
for p in PROMPTS: print(f"{len(set(per[p]))} distinct | {p}")
nvar = sum(1 for p in PROMPTS if len(set(per[p])) > 1)
L.check("replies are fixed for a given seed (seed 0 here equals seed 0 in a fresh process)", all(per[p][0] == rounds[1][i][1] for i, p in enumerate(PROMPTS)))
L.check("replies do not depend on the hash seed (a measured disagreement is kept if it does)", nvar == 0, f"{nvar} of {len(PROMPTS)} prompts give more than one reply across seeds 0–4")"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── 22 · fault ledger and NULL behaviour ─────────────────────────────
PY["22"] = {"file": "22_fault_ledger_and_null.ipynb", "cells": [
("md", """# 22 · Fault handling and NULL behaviour (paper §14)
Code: `VAPMIP/rotary_rerun_monad.py` (`Fault`, `Status`, `Relation`, `Ledger`, `Harness`, `MindsEye`), `ValaQuenta/modules/box_kite/maths.py` (`fixed_point_weight`), `VAPMIP/PtolC/ptol.c` (`measure_sigma`).
Part 1: every fault is a record. Part 2: what each program returns for an all-zero input (a census; each entry is a data point)."""),
("code", PRE % "22 · fault handling and NULL behaviour" + """with quiet():
    import rotary_rerun_monad as rr
    h = rr.Harness(); h.run(psi=rr._demo_psi(), currents=(0.412, -0.187, -0.201))
led = h.ledger
counts = {s.name: led.count(s) for s in rr.Status}
print("records:", len(led), counts)
print("faults by kind:", {k.name: len(led.faults_of(k)) for k in rr.Fault})
for r in led.faults()[:3]: print(f"  [{r.fault.name}] {r.name}: expected {r.expected!r}, observed {r.observed!r}")
L.check("every check is a record (none is a bare count)", len(led) == sum(counts.values()) and len(led) > 50, f"{len(led)} records")
L.check("a violated record is classified MATHS or CODE, never left unclassified", all(r.fault is not rr.Fault.NONE for r in led.faults()))
L.check("the deliberately unbalanced currents produce at least one fault for the harness to find", len(led.faults()) >= 1, f"{len(led.faults())} faults")
print("maths_works:", led.maths_works)"""),
("md", "## NULL census: an all-zero input"),
("code", """with quiet():
    from ValaQuenta.modules.box_kite import maths as bk
rows = []
def row(name, ret, keeps): rows.append((name, ret, keeps)); print(f"  {'KEEPS NULL ' if keeps else 'SUPPLIES   '} {name:62s} -> {ret}")
snap = rr.MindsEye().snapshot([0.0] * 16)["sigma_self"]
row("rotary_rerun_monad.MindsEye.snapshot(zeros)['sigma_self']", repr(snap), isinstance(snap, float) and math.isnan(snap))
row("box_kite.fixed_point_weight(zeros)", repr(bk.fixed_point_weight([0.0] * 16)), False)
out, err, _ = ptol("-r", "")
sig = next((l.split("σ_self:")[1].split()[0] for l in err.splitlines() if "σ_self" in l), "?")
row('ptol -r ""  (σ_self printed)', sig, sig.lower() == "nan")
src = open(os.path.join(VAPMIP, "PtolC", "ptol.c")).read()
row("ptol.c measure_sigma: `if (total < 1e-15) return 0.5;`", "returns 0.5 for a zero vector" if "if (total < 1e-15) return 0.5;" in src else "(line not found)", False)
with quiet(): import ptolemy_console as pc; ad = pc.ScaledMindEyeMonadAdapter()
with quiet(): rep, meta = ad.say("good morning")
row("ScaledMindEyeMonadAdapter.say('good morning') (no verb resolves)", rep[:70], rep.startswith("(19D"))
L.check("census recorded (not a verdict on the engines)", True, f"{sum(1 for r in rows if r[2])} of {len(rows)} paths keep NULL; {sum(1 for r in rows if not r[2])} supply a value")"""),
("md", "## Ledger"), ("code", SHOW)]}

# ───────────────────────────── C notebooks ─────────────────────────────
_proj, p1, p2 = cfunc("PtolC/ptol.c", "project")
_sig, s1, s2 = cfunc("PtolC/ptol.c", "measure_sigma")
_gam, g1, g2 = cfunc("PtolC/ptol.c", "measure_gamma")
_P, pa, pb = cblock("PtolC/ptol.c", r"^static const int P\[16\]", r"^\};")
C["07c"] = {"file": "07c_ptol_projection_and_balance.ipynb", "cells": [
("md", f"""# 07c · The question: a prompt becomes ψ, in C (paper §5)
**Requires the C kernel** (`jupyter-c-kernel`; each cell is a standalone C program compiled with gcc). The functions below are extracted **verbatim** from `VAPMIP/PtolC/ptol.c` at build time:
`P[16]` (lines {pa}–{pb}), `project` ({p1}–{p2}), `measure_sigma` ({s1}–{s2}), `measure_gamma` ({g1}–{g2}). The last cell runs the real `ptol -r` and compares."""),
("code", f"""//%cflags:-D_DEFAULT_SOURCE
//%ldflags:-lm
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

/* ptol.c:{pa}-{pb} */
{_P}

/* ptol.c:{p1}-{p2} */
{_proj}

/* ptol.c:{s1}-{s2} */
{_sig}

/* ptol.c:{g1}-{g2} */
{_gam}

int main(void) {{
    const char *prompts[] = {{"finger pointer", "what is a tree", "neutron generation in different reactor types",
                              "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered"}};
    for (int q = 0; q < 6; q++) {{
        const unsigned char *s = (const unsigned char *)prompts[q]; int n = (int)strlen(prompts[q]);
        double x[16], v[16], norm = 0.0;
        for (int k = 0; k < 16; k++) {{ x[k] = project(s, n, k, 0.5); norm += x[k] * x[k]; }}
        norm = sqrt(norm);
        for (int k = 0; k < 16; k++) v[k] = (norm > 0.0) ? x[k] / norm : 0.0;
        double gam, u; measure_gamma(v, &gam, &u);
        printf("%-58s sigma_self=%.10f  Gamma=%+.10f  u=%+.6f\\n", prompts[q], measure_sigma(v), gam, u);
    }}
    return 0;
}}
"""),
("md", "## The real binary against the extracted functions (Eye H, σ = ½)"),
("code", f"""//%cflags:-D_DEFAULT_SOURCE
//%ldflags:-lm
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

{_P}

{_proj}

int main(void) {{
    const char *prompt = "what is a tree";
    system("mkdir -p /tmp/ptol_nb_home/.ptolemy");
    FILE *p = popen("HOME=/tmp/ptol_nb_home ../../PtolC/ptol -r \\"what is a tree\\" 2>/dev/null", "r");
    if (!p) {{ printf("FAIL: could not run ../../PtolC/ptol (build it: cd PtolC && make)\\n"); return 1; }}
    double real[16]; int got = 0; char line[256];
    while (got < 16 && fgets(line, sizeof line, p)) real[got++] = atof(line);
    pclose(p);
    const unsigned char *s = (const unsigned char *)prompt; int n = (int)strlen(prompt);
    double x[16], norm = 0.0, worst = 0.0;
    for (int k = 0; k < 16; k++) {{ x[k] = project(s, n, k, 0.5); norm += x[k] * x[k]; }}
    norm = sqrt(norm);
    for (int k = 0; k < 16; k++) {{ double d = fabs(x[k] / norm - real[k]); if (d > worst) worst = d; }}
    printf("read %d numbers from ptol -r; max |extracted - real| = %.2e\\n", got, worst);
    printf("%s: the extracted project() reproduces ptol -r to the printed precision (1e-10)\\n", (got == 16 && worst < 1e-9) ? "PASS" : "FAIL");
    return 0;
}}
""")]}

_wc, w1, w2 = cfunc("PtolC/monad.c", "monad_word_coords")
_lk, l1, l2 = cfunc("PtolC/ptol.c", "monad3_lookup")
_gr, r1, r2 = cfunc("PtolC/ptol.c", "monad3_gamma_radial")
_ga, a1, a2 = cfunc("PtolC/ptol.c", "gr_log_anchor")
C["08c"] = {"file": "08c_ptol_store.ipynb", "cells": [
("md", f"""# 08c · The store: one mmap'd file, one binary search, in C (paper §4)
**Requires the C kernel.** Extracted verbatim at build time: `monad3_lookup` (`ptol.c` {l1}–{l2}), `gr_log_anchor` ({a1}–{a2}), `monad3_gamma_radial` ({r1}–{r2}), and `monad_word_coords` (`monad.c` {w1}–{w2}). The header layout is `PtolC/monad3c.h`, included directly."""),
("code", """//%cflags:-I../../PtolC
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include "monad3c.h"

int main(void) {
    int fd = open("../../PtolC/monad3_c.bin", O_RDONLY); struct stat st; fstat(fd, &st);
    const Monad3cHeader *h = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    printf("file size      %lld bytes\\n", (long long)st.st_size);
    printf("magic          %.7s   version %u\\n", h->magic, h->version);
    printf("words          %u   (one WordRec per word: 16 bytes)\\n", h->n_words);
    printf("english store  %u entries   wordnet store  %u entries   phonetic store  %u entries\\n", h->n_eng, h->n_wn, h->n_phon);
    printf("co-occurrence  %u edges\\n", h->nnz);
    printf("%s: header magic is MONAD3C and sizeof(WordRec) == 16\\n", (memcmp(h->magic, MONAD3C_MAGIC, 8) == 0 && sizeof(WordRec) == 16) ? "PASS" : "FAIL");
    return 0;
}
"""),
("md", "## One binary search gives the indices into all three stores"),
("code", f"""//%cflags:-I../../PtolC
//%ldflags:-lm
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include "monad3c.h"

static const unsigned char *g_m3 = NULL; static const Monad3cHeader *g_m3h = NULL;

/* ptol.c:{l1}-{l2} */
{_lk}

/* ptol.c:{a1}-{a2} (constants copied with it) */
static const int GR_CONTEXT_PRIMES[19] = {{73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167}};
#define GR_HYPONYMS_IDX 2
{_ga}

/* ptol.c:{r1}-{r2} */
{_gr}

int main(void) {{
    int fd = open("../../PtolC/monad3_c.bin", O_RDONLY); struct stat st; fstat(fd, &st);
    g_m3 = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0); g_m3h = (const Monad3cHeader *)g_m3;
    const char *words[] = {{"tree", "what", "piano", "xyzzyq"}};
    int hits = 0;
    for (int i = 0; i < 4; i++) {{
        int32_t ix[3]; uint32_t deg; int hit = monad3_lookup(words[i], ix, &deg);
        printf("%-8s hit=%d  eng=%d wn=%d phon=%d  degree=%u", words[i], hit, ix[0], ix[1], ix[2], deg);
        if (hit && ix[1] >= 0) {{
            const int16_t *vec = (const int16_t *)(g_m3 + g_m3h->off_wn + (size_t)ix[1] * 82u + 40);
            printf("   gamma_radial=%+.6f", monad3_gamma_radial(vec));
        }}
        printf("\\n"); if (hit) hits++;
    }}
    printf("%s: three of the four words are in the store and the unknown word is not (hits = %d)\\n", hits == 3 ? "PASS" : "FAIL", hits);
    return 0;
}}
"""),
("md", "## Every word gets a slot and an energy between the two constants"),
("code", f"""//%cflags:-I../../PtolC
//%ldflags:-lm
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "ptolemy.h"

/* monad.c:{w1}-{w2} */
{_wc}

int main(void) {{
    const char *words[] = {{"tree", "what", "piano", "neutron", "good", "morning", "reactor", "discovered"}};
    double lo = 1e9, hi = -1e9; int N = 25000;
    for (int i = 0; i < 8; i++) {{
        int idx; double E; monad_word_coords(words[i], N, &idx, &E);
        printf("%-12s slot %5d  E = %.6f\\n", words[i], idx, E);
        if (E < lo) lo = E; if (E > hi) hi = E;
    }}
    printf("MONAD_D_STAR = %.5f, MONAD_OMEGA_ZS = %.5f; observed E in [%.6f, %.6f]\\n", MONAD_D_STAR, MONAD_OMEGA_ZS, lo, hi);
    printf("%s: every energy lies between MONAD_D_STAR and MONAD_OMEGA_ZS\\n", (lo >= MONAD_D_STAR - 1e-12 && hi <= MONAD_OMEGA_ZS + 1e-12) ? "PASS" : "FAIL");
    return 0;
}}
"""),
("md", "## The slots printed in two screenshots of May 2026 (paper §7.3, screenshots 2 and 3)\nThe ten (word, slot, energy) triples below are transcribed from the screenshots `2-Hocus-Hyperwebster.png` and `3-TheExtractor.png`, taken on the earlier store (`monad_wordnet.bin`, vocab 24,485); the function is today's `monad_word_coords`."),
("code", f"""//%cflags:-I../../PtolC
//%ldflags:-lm
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "ptolemy.h"

{_wc}

int main(void) {{
    const char *w[] = {{"can","you","hear","what","i","am","typing","is","your","name"}};
    int z[] = {{18466,17464,19372,16194,2912,16543,21041,1894,18893,15471}};
    double E[] = {{0.4832,0.4703,0.4949,0.4540,0.2834,0.4585,0.5163,0.2703,0.4887,0.4447}};
    int old_ok = 1, new_same = 0;
    for (int i = 0; i < 10; i++) {{
        int idx; double e; monad_word_coords(w[i], 25000, &idx, &e);
        /* the formula the comment in monad_word_coords says it replaced: fmod((double)v*MONAD_PHI, 1.0) */
        uint64_t v = 0; for (const char *p = w[i]; *p; p++) v = v * 95ULL + (uint64_t)((unsigned char)*p - 32 + 1);
        if (v > 0) v--;
        int old_idx = (int)(fmod((double)v * MONAD_PHI, 1.0) * 25000);
        int match_new = (idx == z[i]) && (fabs(e - E[i]) < 5e-5), match_old = (old_idx == z[i]);
        if (!match_old) old_ok = 0;
        if (match_new) new_same++;
        printf("shot %-7s screen slot %5d | today %5d | old formula %5d | E %.4f (screen %.4f) %s\\n", w[i], z[i], idx, old_idx, e, E[i], match_new ? "match" : "DIFFERS (today)");
    }}
    printf("%s: the replaced formula (fmod of v*MONAD_PHI) reproduces all ten screenshot slots; today's exact-integer monad_word_coords reproduces %d of 10 (the others differ by one slot, six-character word, as monad.c's own comment says)\\n", (old_ok && new_same >= 9) ? "PASS" : "FAIL", new_same);
    return 0;
}}
""")]}


# ───────────────────── 09c · the learning step of monad.c, in C (paper §7) ─────────────────────
def cspan(relpath, start_pat, end_pat, extra=0):
    lines = open(os.path.join(VAPMIP, relpath), encoding="utf-8").read().split("\n")
    a = next(i for i, l in enumerate(lines) if re.search(start_pat, l))
    b = next(i for i in range(a, len(lines)) if re.search(end_pat, lines[i])) + extra
    return "\n".join(lines[a:b + 1]), a + 1, b + 1


_dp, d1, d2 = cfunc("PtolC/monad.c", "dirac_pole")
_beta, b1, b2 = cspan("PtolC/monad.c", r"double amp = fabs\(sin\(m->zeros\[idx\]\)\)", r"m->beta\[idx\] = nb;")
_lad, l1_, l2_ = cspan("PtolC/monad.c", r"if \(ft == NS_FT_WORDNET\)", r"prose_seen = 3", extra=1)
_cpl, c1_, c2_ = cspan("PtolC/monad.c", r"double d_zero = fabs\(m->zeros\[sidx\[i\]\]", r"double w\s+= sE\[i\] \* sE\[j\] \* couple")
C["09c"] = {"file": "09c_ptol_learning_step.ipynb", "cells": [
("md", f"""# 09c · Learning in the C monad: the update arithmetic, in C (paper §7)
**Requires the C kernel.** The lines below are extracted **verbatim** from `VAPMIP/PtolC/monad.c` at build time and run on a minimal stand-in for the `Monad` struct (only the fields those lines touch); constants come from the real `ptolemy.h` and `filter.h`:
`dirac_pole` (lines {d1}–{d2}), the β update ({b1}–{b2}), the `prose_seen` ladder ({l1_}–{l2_}), the co-occurrence coupling ({c1_}–{c2_}) of `monad_learn_ex`."""),
("code", f"""//%cflags:-I../../PtolC -D_DEFAULT_SOURCE
//%ldflags:-lm
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "ptolemy.h"
#include "filter.h"

/* monad.c:{d1}-{d2} */
{_dp}

typedef struct {{ double zeros[4]; double beta[4]; struct {{ int prose_seen; }} vocab[4]; }} MiniMonad;

/* monad.c:{b1}-{b2}, verbatim, on slot idx of a MiniMonad */
static void beta_update(MiniMonad *m, int idx, double E) {{
{_beta}
}}

int main(void) {{
    MiniMonad m = {{ .zeros = {{14.134725, 21.022040, 25.010858, 30.424876}}, .beta = {{0, 0, 0, 0}} }};
    double E = 0.40;
    printf("MONAD_ALPHA_LEARN = %g, MONAD_BETA_SAT = %g\\n", MONAD_ALPHA_LEARN, MONAD_BETA_SAT);
    int monotone = 1, capped = 1; double prev = 0;
    for (int step = 1; step <= 4000; step++) {{
        beta_update(&m, 0, E);
        if (m.beta[0] + 1e-15 < prev) monotone = 0;
        if (m.beta[0] > MONAD_BETA_SAT + 1e-12) capped = 0;
        prev = m.beta[0];
        if (step == 1 || step == 10 || step == 100 || step == 1000 || step == 4000) printf("step %4d: beta = %.6f\\n", step, m.beta[0]);
    }}
    printf("%s: beta only rises with repeated exposure and never exceeds MONAD_BETA_SAT\\n", (monotone && capped) ? "PASS" : "FAIL");
    return 0;
}}
"""),
("md", "## The `prose_seen` ladder is order-dependent"),
("code", f"""//%cflags:-I../../PtolC -D_DEFAULT_SOURCE
//%ldflags:-lm
#include <stdio.h>
#include "filter.h"

typedef struct {{ struct {{ int prose_seen; }} vocab[1]; }} MiniMonad;

/* monad.c:{l1_}-{l2_}, verbatim, on slot idx of a MiniMonad */
static void ladder(MiniMonad *m, int idx, NSFiletype ft) {{
{_lad}
}}

int main(void) {{
    MiniMonad a = {{ .vocab = {{ {{0}} }} }}, b = {{ .vocab = {{ {{0}} }} }};
    ladder(&a, 0, NS_FT_WORDNET); ladder(&a, 0, NS_FT_PROSE);      /* dictionary first, then prose */
    ladder(&b, 0, NS_FT_PROSE);   ladder(&b, 0, NS_FT_WORDNET);    /* prose first, then dictionary */
    printf("WordNet then prose: prose_seen = %d\\nprose then WordNet: prose_seen = %d\\n", a.vocab[0].prose_seen, b.vocab[0].prose_seen);
    printf("%s: the ladder reaches 3 (verified common) in one order and not the other (%d vs %d)\\n", (a.vocab[0].prose_seen != b.vocab[0].prose_seen) ? "PASS" : "FAIL", a.vocab[0].prose_seen, b.vocab[0].prose_seen);
    return 0;
}}
"""),
("md", "## The co-occurrence coupling"),
("code", f"""//%cflags:-I../../PtolC -D_DEFAULT_SOURCE
//%ldflags:-lm
#include <stdio.h>
#include <math.h>
#include "ptolemy.h"

/* monad.c:{d1}-{d2} */
{_dp}

typedef struct {{ double zeros[4]; }} MiniMonad;

/* monad.c:{c1_}-{c2_}, verbatim, for tokens i and j of one sentence */
static double coupling(MiniMonad *m, int *sidx, double *sE, int i, int j) {{
{_cpl}
    return w;
}}

int main(void) {{
    MiniMonad m = {{ .zeros = {{14.134725, 21.022040, 25.010858, 30.424876}} }};
    int sidx[4] = {{0, 1, 2, 3}}; double sE[4] = {{0.40, 0.41, 0.42, 0.43}};
    int ok = 1;
    for (int j = 1; j < 4; j++) {{ double w = coupling(&m, sidx, sE, 0, j); printf("token 0 -- token %d: w = %.6e\\n", j, w); if (!(w > 0)) ok = 0; }}
    double near = coupling(&m, sidx, sE, 0, 1), far = coupling(&m, sidx, sE, 0, 3);
    printf("%s: couplings are positive and the nearer token (distance 1) couples more strongly than the farther (distance 3)\\n", (ok && near > far) ? "PASS" : "FAIL");
    return 0;
}}
""")]}
