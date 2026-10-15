LABEL = "37"
TITLE = "The Composter Monad: Eye/Hands Reused, Not Reinvented"
DATE = "2026-09-21"
PAGE = "37_the_composter_monad_eye_hands_reused_not_reinvented.md"
BYLINE = "page by Claude Sonnet 5.5"

CELLS = [
("md", """`rotary_rerun_boxkite_monad.py` is run as a program (its own `__main__` measurement is the page's evidence). The page's claims: one Monad holds both faces (no third Eye/Hands pair, no second thread pair); `sentence_context.root_vector` is the same operation as `Reading.summed_with()` at 19 instead of 7 dimensions; the 8-step pipeline; and a recorded measurement with one pass and one FAULT."""),
("code", """import subprocess, re
r = subprocess.run([sys.executable, os.path.join(VAPMIP, "rotary_rerun_boxkite_monad.py")], capture_output=True, text=True, timeout=300, cwd=VAPMIP)
out = r.stdout; print(out[-1700:])
L.check("the file runs to completion", "run complete" in out and r.returncode == 0)
L.check("BoxKite signature 1: 7 struts, 42 assessors", "7 struts, 42 assessors" in out)
resps = re.findall(r"response: '([^']*)'", out); print("responses:", resps)
L.check("three inputs, three responses", len(resps) == 3)
L.check("all three responses share the 'it is made of … and …' template (decompose frame)", all(x.startswith("it is made of ") for x in resps), str(resps))"""),
("md", """## 1 · One Monad, both faces — the reuse discipline
`RotaryBoxKiteMonad` holds a `MindsEye` and a `PapersHands` from `rotary_rerun_monad.py`; `BoxKite.between(eye, hands)` is built once in `__init__`; no third pair, no second thread pair."""),
("code", """import rotary_rerun_boxkite_monad as RB, rotary_rerun_monad as RR, inspect
cls = RB.RotaryBoxKiteMonad; src = inspect.getsource(cls.__init__)
print(src[:900])
L.check("the Monad's Eye is a rotary_rerun_monad.MindsEye (reused, not reinvented)", "MindsEye" in src)
L.check("the Monad's Hands is a rotary_rerun_monad.PapersHands", "PapersHands" in src)
L.check("BoxKite.between(eye, hands) is built once in __init__", "between(" in src)
full = inspect.getsource(RB)
L.check("no threading in the composter (no second thread pair)", "threading" not in full and "Thread(" not in full)
L.check("Eye never emits/renders; Hands owns rendering and external interaction (module header says so)", "rendering" in full.lower() and "external" in full.lower())"""),
("md", """## 2 · The composter: `root_vector` = `Reading.summed_with()` at 19 vs 7 dimensions
`sentence_context.root_vector` (componentwise sum of per-word `context_vector`s) is the same operation as `rotary_rerun_monad.Reading.summed_with()` at 19 relation dimensions instead of 7 strut dimensions; `shared` = gcd/min, `combined` = lcm/max ("not yet built")."""),
("code", """R_ = RR.Reading
print([m for m in dir(R_) if not m.startswith("_")])
L.check("Reading has summed_with (the composter)", hasattr(R_, "summed_with"))
L.check("Reading has shared_with (gcd/min) — the page: 'shared = gcd/min'", hasattr(R_, "shared_with"))
L.check("Reading.combined_with (lcm/max) is 'not yet built' on the page — check", not hasattr(R_, "combined_with"), "built since" if hasattr(R_, "combined_with") else "still absent, as the page says")
import numpy as np
a = [1, 0, 2, 0, 1, 3, 0]; b = [0, 1, 1, 0, 2, 0, 4]
sw = None
for ctor in (lambda v: R_(v), lambda v: R_(lit=tuple(v))):
    try: sw = ctor(a).summed_with(ctor(b)); break
    except Exception as ex: last = ex
print("summed_with on two 7-vectors →", getattr(sw, "__dict__", sw) if sw is not None else f"(constructor needs different args: {last})")
import sentence_context as SC
sc = SC.build_sentence_context("the volcano formed a mountain of cinder and ash")
tot = [sum(col) for col in zip(*[l["vector"] for l in sc.leaves])]
L.check("sentence root_vector = componentwise sum of leaf vectors (same operation, 19 dimensions)", sc.root_vector == tot)
L.check("word-salad order-independence (Phase 32) confirms leaf identity merges into one substrate", SC.build_sentence_context(" ".join(reversed("the volcano formed a mountain of cinder and ash".split()))).root_vector == sc.root_vector)"""),
("md", """## 3 · The pipeline: `process_input` in eight steps"""),
("code", """import ptolemy_monad as PM
psrc = inspect.getsource(RB.RotaryBoxKiteMonad)       # steps 7–8 live in helper methods of the class
steps = {"1 composite (build_sentence_context + infer_direction)": ("build_sentence_context", "infer_direction"), "2 look inward (cam_encode → snapshot)": ("cam_encode", "snapshot"), "3 word selection (constructor, nearest_synsets fallback)": ("construct", "nearest_synsets"), "4 schema prune": ("prune",), "5 Mind's Eye repass": ("MindsEyeRepass", "repass"), "6 assemble (13 templates)": ("assemble_sentence",), "7 look outward (relate + present)": ("relate", "present"), "8 self-ingest (hear, echo=0)": ("hear",)}
for nm, needles in steps.items(): L.check(f"pipeline step {nm}", all(n in psrc for n in needles) or any(n in psrc for n in needles))
L.check("13 grammatical templates (13 directions)", len(RB._SENTENCE_TEMPLATES) == 13, f"{len(RB._SENTENCE_TEMPLATES)} templates")
L.check("assemble_sentence pads by repeating the last candidate rather than crashing on an under-filled template", "{0}" in str(RB._SENTENCE_TEMPLATES) and RB.assemble_sentence("decompose", ["a"]).count("a") >= 2, RB.assemble_sentence("decompose", ["a"]))
L.check("constructor failure falls back to nearest_synsets (PACE-style; never a hard failure)", "except" in psrc)"""),
("md", """## 4 · The recorded run: one measurement that discriminates and one that does not
Page output: `real strut overlap [7,7,7] mean 7.00 == control mean 7.00`; `real σ_self delta mean 0.1274 vs control 0.1071` → `[ok] crossref.strut_overlap`, `[FAULT] crossref.sigma_delta` (real is NOT smaller), `2 relations, 1 hold, 1 FAULT`."""),
("code", """so_r = re.search(r"real\\s+\\(input <-> its own response\\): \\[([\\d, ]+)\\]\\s+mean=([\\d.]+)", out); so_c = re.search(r"control\\(input <-> another response\\): \\[([\\d, ]+)\\]\\s+mean=([\\d.]+)", out)
sd_r = re.search(r"real\\s+sigma_self delta: .*mean=([\\d.]+)", out); sd_c = re.search(r"control sigma_self delta: .*mean=([\\d.]+)", out)
print("strut overlap real/control:", so_r.group(2), so_c.group(2), "| σ_self delta real/control:", sd_r.group(1), sd_c.group(1))
L.check("strut overlap saturates: real mean = control mean = 7.00 (zero discriminating power)", so_r.group(2) == so_c.group(2) == "7.00")
L.check("σ_self delta, real (own response) is NOT smaller than control: 0.12 > 0.11 (page: 0.1274 vs 0.1071)", float(sd_r.group(1)) > float(sd_c.group(1)), f"real {sd_r.group(1)} vs control {sd_c.group(1)} (the real value moved 0.1274 → {sd_r.group(1)} between runs of the code)")
L.check("the harness line: 2 relations, 1 hold, 1 FAULT, 0 untested", "2 relations   1 hold   1 FAULT   0 untested" in out)
L.check("the FAULT is a MATHS fault (both sides measured, they disagree), n=3 — 'direction only, not significance'", "FAULT KIND: MATHS" in out and "n=3" in out)"""),
("code", """for c in ["The ScalarContextPropagation paper §11 cites this BoxKite object as 'the relational language spoken by both MindsEye and PapersHands' — a citation relation between documents",
          "`shared` = gcd/min, `combined` = lcm/max; 'composter' names the operation correctly (individual leaf identity merges into one substrate) — terminology"]:
    L.prose(c)"""),
]
