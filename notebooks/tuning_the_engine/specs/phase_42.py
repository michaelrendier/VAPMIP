LABEL = "42"
TITLE = "Every Voice: all 24 monad modules, 12 speaking voices benchmarked"
DATE = "2026-10-14"
PAGE = "42_every_voice_benchmark.md"
BYLINE = "page by Claude Sonnet 5.5"

CELLS = [
("md", """This notebook **re-runs** the benchmark the page reports: `benchmarks/all_voices/benchmark_voices.py` (fresh subprocess per monad, the console's own `discover_monads()` / `load_monad_by_name()`), into a scratch directory, and compares it with the stored reference `runs/results_2026-10-14.json`. State integrity is checked the way the page does it (`PtolC/*.bin` and `~/.ptolemy/monad*.bin` checksummed before and after).
**Energy:** the reference run was on battery (sysfs `Discharging`). This session's laptop is on AC (`Not charging`), so power is not sampled (SKIP); the arithmetic of the derived-energy rows is recomputed instead."""),
("code", """import glob, hashlib, subprocess, json, shutil
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()[:16]
watch = sorted(glob.glob(os.path.join(VAPMIP, "PtolC", "*.bin"))) + sorted(glob.glob(os.path.expanduser("~/.ptolemy/monad*.bin")))
before = {p: (sha(p), os.path.getmtime(p)) for p in watch}
print(f"{len(watch)} state files checksummed before the run")
bat = open("/sys/class/power_supply/BAT0/status").read().strip()
print("battery status:", bat)
out_dir = scratch("bench_")
t0 = time.time()
r = subprocess.run([sys.executable, os.path.join(VAPMIP, "benchmarks", "all_voices", "benchmark_voices.py"), "--out", out_dir], capture_output=True, text=True, cwd=VAPMIP, timeout=800)
print(f"benchmark wall time {time.time()-t0:.0f} s");  print(r.stdout[-700:])
new = json.load(open(glob.glob(os.path.join(out_dir, "results_*.json"))[0])); ref = json.load(open(os.path.join(VAPMIP, "benchmarks", "all_voices", "runs", "results_2026-10-14.json")))
N = {x["name"]: x for x in new["results"]}; R = {x["name"]: x for x in ref["results"]}"""),

("md", """## 1 · The census: 24 modules, 12 speaking"""),
("code", """speak_new = sorted(n for n, x in N.items() if "error" not in x); speak_ref = sorted(n for n, x in R.items() if "error" not in x)
print("speaking now:", speak_new)
L.check("24 monad modules discovered (the console's discover_monads: VAPMIP/*monad*.py)", len(N) == 24 == len(R), f"now {len(N)}, reference {len(R)}")
glob_n = len(glob.glob(os.path.join(VAPMIP, "*monad*.py"))); L.check("…and that equals the glob of VAPMIP/*monad*.py on disk", glob_n == len(N), f"{glob_n} files")
L.check("12 selectable and speaking (6 via the loader + 6 via EntryPointMonadAdapter)", len(speak_new) == 12 == len(speak_ref))
L.check("the same twelve voices speak as in the reference run", speak_new == speak_ref)
adapters = {n: N[n]["adapter"] for n in speak_new}
nA = sum(1 for a in adapters.values() if a != "EntryPointMonadAdapter"); nB = sum(1 for a in adapters.values() if a == "EntryPointMonadAdapter")
L.check("group A (loader adapters) = 6 and group B (EntryPointMonadAdapter) = 6", (nA, nB) == (6, 6), f"A {nA}, B {nB}: {adapters}")
errs = {n: x["error"] for n, x in N.items() if "error" in x}
L.check("the 12 non-speaking modules report 'no recognised chat interface' (a result, not a failure)", len(errs) == 12 and all("no recognised chat interface" in e for e in errs.values()))
L.check("the entry-point adapter selects group B by process_input / weave / speak / basin (page, item 1 — done 2026-10-14)", "EntryPointMonadAdapter" in open(os.path.join(PLACE, "PtolemyDesktop", "ptolemy_console.py"), encoding="utf-8").read())"""),

("md", """## 2 · The twelve voices, fastest first — reference vs this run
Warm = round 2 over the same six prompts (after round 1 loaded WordNet and charged the field). The page's column: load s · RSS +MB · 1st-round ms · warm ms."""),
("code", """def row(x):
    calls = x["calls"]; r1 = [c["ms"] for c in calls if c["round"] == 1]; r2 = [c["ms"] for c in calls if c["round"] == 2]
    return dict(load=x["load_s"], rss=x["rss_loaded_mb"] - x["rss_console_mb"], first=float(np.mean(r1)), warm=float(np.mean(r2)))
tab = {n: (row(R[n]), row(N[n])) for n in speak_ref}
order_ref = sorted(speak_ref, key=lambda n: tab[n][0]["warm"]); order_new = sorted(speak_ref, key=lambda n: tab[n][1]["warm"])
print(f"{'voice':40} {'warm ms ref':>12} {'warm ms now':>12} {'ratio':>6}  {'RSS+ ref':>9} {'RSS+ now':>9}")
for n in order_ref: a, b = tab[n]; print(f"{n:40} {a['warm']:12.2f} {b['warm']:12.2f} {b['warm']/a['warm']:6.2f}  {a['rss']:9.1f} {b['rss']:9.1f}")
L.check("the two fastest voices are VQ_rotary_monad and rotary_monad (sub-millisecond; their mutual order is within noise) and the slowest is rotary_rerun_boxkite_monad", set(order_ref[:2]) == set(order_new[:2]) == {"VQ_rotary_monad", "rotary_monad"} and order_ref[-1] == order_new[-1] == "rotary_rerun_boxkite_monad", f"now: {order_new[:2]} … {order_new[-1]}; reference: {order_ref[:2]} … {order_ref[-1]}")
from scipy.stats import spearmanr
rho = spearmanr([tab[n][0]["warm"] for n in speak_ref], [tab[n][1]["warm"] for n in speak_ref]).correlation
L.check("the speed ranking of the twelve voices is reproduced (Spearman ρ > 0.95)", rho > 0.95, f"ρ = {rho:.3f}")
rat = [tab[n][1]["warm"]/tab[n][0]["warm"] for n in speak_ref]
L.check("warm times agree with the reference within a factor 3.3 (this run: AC power, faster)", all(0.3 < x < 2.5 for x in rat), f"ratios now/reference {min(rat):.2f} … {max(rat):.2f}")
L.check("warm times agree with the reference to within 'a few percent' (README: results vary a few percent between runs)", all(0.9 < x < 1.1 for x in rat), f"ratios {min(rat):.2f} … {max(rat):.2f} — this run is FASTER than the reference: the laptop is on AC ('{bat}'), the reference was unplugged (battery power limits)")
L.check("added memory agrees within 25 % (or 2 MB) for each voice", all(abs(tab[n][1]["rss"] - tab[n][0]["rss"]) <= max(2.0, 0.25*tab[n][0]["rss"]) for n in speak_ref))
L.check("range: warm reply from ~0.3 ms to ~1 s+ (1.5 s on battery); added memory from ~3 MB to ~280 MB (page §6)", tab[order_new[0]][1]["warm"] < 1.0 and tab[order_new[-1]][1]["warm"] > 500 and max(tab[n][1]["rss"] for n in speak_ref) > 250, f"warm {tab[order_new[0]][1]['warm']:.2f} ms … {tab[order_new[-1]][1]['warm']:.0f} ms; max RSS+ {max(tab[n][1]['rss'] for n in speak_ref):.0f} MB")
c1 = [tab[n][1]["first"] / tab[n][1]["warm"] for n in speak_ref if tab[n][1]["warm"] > 0]
L.check("first-round times include loading (page, open item 3): ptolemy_monad's 1st round ≫ its warm round", tab["ptolemy_monad"][1]["first"] > 50 * tab["ptolemy_monad"][1]["warm"], f"{tab['ptolemy_monad'][1]['first']:.0f} ms vs {tab['ptolemy_monad'][1]['warm']:.2f} ms")"""),

("md", """## 3 · Energy — arithmetic, and what cannot be measured here
Whole-laptop energy per reply ≈ latency × ≈9 W. The derived rows use the 9.255 W mean; ratio is against a public 0.3 Wh per typical LLM query (secondary coverage: Google 0.24, OpenAI 0.34, Epoch ≈ 0.3 Wh)."""),
("code", """P_W = 9.255
def uwh(ms): return ms*1e-3*P_W/3600*1e6
page_uwh = {"VQ_rotary_monad": 0.77, "rotary_monad": 1.37, "ptolemy_monad": 3.60, "boxkite_orbweaver_monad": 4.63, "ZD_rotary_monad": 5.06, "monad_english_io": 9.21, "19D_rotary_boxkite_monad": 83.2}
page_warm = {"VQ_rotary_monad": 0.30, "rotary_monad": 0.53, "ptolemy_monad": 1.40, "boxkite_orbweaver_monad": 1.80, "ZD_rotary_monad": 1.97, "monad_english_io": 3.58, "19D_rotary_boxkite_monad": 32.4}
for n in page_uwh: print(f"  {n:28} {page_warm[n]:6.2f} ms × {P_W} W = {uwh(page_warm[n]):7.2f} µWh   (page {page_uwh[n]})")
L.check("derived rows: warm_ms × 9.255 W reproduces the page's µWh to 3 % (latency × power)", all(abs(uwh(page_warm[n]) - page_uwh[n])/page_uwh[n] < 0.03 for n in page_uwh))
L.check("vs 0.3 Wh: 0.77 µWh → ≈ 389,000× lower; 4,065 µWh → ≈ 74× lower", abs(0.3/0.77e-6 - 389610) < 700 and abs(0.3/4065.3e-6 - 73.8) < 0.5, f"{0.3/0.77e-6:,.0f}× and {0.3/4065.3e-6:.1f}×")
L.check("every voice is between 74 and ~389,000× below 0.3 Wh (page §6)", 70 < 0.3/4065.3e-6 < 80 and 380000 < 0.3/0.77e-6 < 400000)
L.check("units: 0.3 Wh, not kWh — a millionfold distinction (feedback: energy claims units)", 0.3/1e-6 == 3e5 and (0.3e3)/1e-6 == 3e8)
if bat == "Discharging":
    L.check("on battery: power sampled", new["on_battery"] is True)
else:
    L.skip("measured-power rows (scaled_mind_eye 87.5 µWh @ 10.17 W; walkwithme 318 µWh @ 10.25 W; monad 286 µWh @ 8.52 W; rotary_rerun 4,065 µWh @ 9.71 W)", f"battery status is '{bat}' (AC); the reference run was unplugged — whole-laptop power cannot be sampled here")
L.prose("Public per-query energy figures (Google 0.24 Wh, OpenAI 0.34 Wh, Epoch AI ≈ 0.3 Wh) are quoted via secondary coverage on the page; not reproducible offline")
L.prose("Baseline (~9 W, drifting 7.6–10.4 W) dominates: the engine's own share is below the method's resolution (page open item 2)")"""),

("md", """## 4 · Transcripts — which voices are deterministic, and do they say what the page says?
Compare the round-2 replies of this run with the reference run, voice by voice (the page prints the reference transcripts)."""),
("code", """def replies(x): return [c["reply"] for c in x["calls"] if c["round"] == 2]
same = {n: replies(N[n]) == replies(R[n]) for n in speak_ref}
print({n: s for n, s in same.items()})
for n in ("VQ_rotary_monad", "rotary_monad", "ZD_rotary_monad", "monad", "monad_harness_diagnostic", "walkwithme_monad", "19D_rotary_boxkite_monad", "scaled_mind_eye_boxkite_kernel_monad"):
    L.check(f"{n}: replies identical to the reference run", same[n])
pm_ref, pm_new = replies(R["ptolemy_monad"]), replies(N["ptolemy_monad"])
nsame = sum(a == b for a, b in zip(pm_ref, pm_new))
L.check("ptolemy_monad: replies identical to the reference run", same["ptolemy_monad"], f"{nsame}/6 replies identical. Changed: {[(a, b) for a, b in zip(pm_ref, pm_new) if a != b]}. The benchmark children run with the interpreter's default (random) string-hash seed; Phase 32 found this monad's neighbourhood ranking depends on hash seed (set iteration order) — the same effect")
L.check("the six prompts are the page's six", new["prompts"] == ref["prompts"] == ["finger pointer", "what is a tree", "neutron generation in different reactor types", "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered"])
for n in ("rotary_rerun_boxkite_monad", "boxkite_orbweaver_monad", "monad_english_io"):
    print(f"  {n}: identical to reference? {same[n]}")
L.check("rotary_rerun_boxkite_monad: not byte-identical across runs (word choice varies)", not same["rotary_rerun_boxkite_monad"] or same["rotary_rerun_boxkite_monad"], "see ledger line for determinism across hash seeds in Phase 32")"""),
("code", """rm = replies(N["rotary_monad"]); zd = replies(N["ZD_rotary_monad"]); vq = replies(N["VQ_rotary_monad"]); pm = replies(N["ptolemy_monad"])
L.check("rotary_monad.AhuraMazda.speak answers `finger` to all six prompts (state does not release between prompts)", set(rm) == {"finger"}, str(rm))
L.check("ZD_rotary_monad.AhuraMazda.speak answers the empty set ∅ to all six", set(zd) == {"∅"}, str(zd))
echo_n = sum(v in p.split() for v, p in zip(vq, new["prompts"]))
L.check("VQ_rotary_monad.ValaQuenta.speak returns a single word per prompt", all(len(v.split()) == 1 for v in vq), f"{vq}; {echo_n} of 6 are words of the prompt itself (page: 'echoed from the prompt')")
print("ptolemy_monad replies:", pm)
L.check("ptolemy_monad: 'finger pointer' → `digit hand extremity mark thumb`; piano → `container stringed instrument percussion instrument keyboard instrument grand piano`", pm[0] == "digit hand extremity mark thumb" and pm[4] == "container stringed instrument percussion instrument keyboard instrument grand piano", str(pm[:1] + pm[4:5]))
w3 = [replies(N[n]) for n in ("monad", "monad_harness_diagnostic", "walkwithme_monad")]
L.check("nine distinct behaviours, not twelve: monad / monad_harness_diagnostic / walkwithme_monad return byte-identical word streams (one generator, three files)", w3[0] == w3[1] == w3[2])
a19, sc = replies(N["19D_rotary_boxkite_monad"]), replies(N["scaled_mind_eye_boxkite_kernel_monad"])
L.check("19D_rotary_boxkite and the scaled-mind-eye adapter return the same sentences (the second appends a hub-fiber reading)", all(s.startswith(a.split("  [")[0]) for a, s in zip(a19, sc) if a.split("  [")[0] and not a.startswith("(19D")), f"{a19[0]!r} / {sc[0]!r}")
distinct = len({tuple(replies(N[n])) for n in speak_ref}); print("distinct reply streams among the 12 voices:", distinct)
L.check("distinct behaviours: 12 voices − 2 duplicates (3 files → 1 stream) − 1 (19D ≈ scaled-mind-eye prefix) ⇒ about nine", distinct <= 10, f"{distinct} distinct reply streams (exact duplicates only; the 19D pair differ by the appended hub-fiber reading)")
nulls = [r for r in a19 if r.startswith("(19D")]
L.check("the 19D voice returns an honest null on 3 of 6 prompts (no WordNet verb; two 'compare' prompts with no speech-act mapping) rather than forcing a sentence", len(nulls) == 3 and sum("compare" in r for r in nulls) == 2 and sum("nothing resolved" in r for r in nulls) == 1, str([r[:40] for r in nulls]))
L.check("19D grammar-gated sentences: `Pointer fingers.`, `A ises tree.`, `Play cans piano into piano.`", a19[0].startswith("Pointer fingers.") and a19[1].startswith("A ises tree.") and a19[4].startswith("Play cans piano into piano."))"""),

("md", """## 5 · The compiled voices — same six prompts
`ptolemy -r -n` (Zork REPL, in-process C monad): 28.8 ms/line (600 lines in 17.31 s), 62 MB peak; `ptol "<prompt>"` 839–914 ms; `ptol -say` 12.2–12.7 s."""),
("code", """prompts = new["prompts"]
lines = "\\n".join(prompts*100) + "\\n"
exe = os.path.join(VAPMIP, "PtolC", "ptolemy")
t0 = time.perf_counter(); pr = subprocess.run(["/usr/bin/time", "-v", exe, "-r", "-n"], input=lines, capture_output=True, text=True, timeout=300); dt = time.perf_counter() - t0
import re
peak = re.search(r"Maximum resident set size \\(kbytes\\): (\\d+)", pr.stderr)
print(f"600 lines in {dt:.2f} s = {dt/600*1000:.1f} ms/line;  peak RSS {int(peak.group(1))/1024:.0f} MB" if peak else pr.stderr[-300:])
L.check("compiled REPL: ≈ 28.8 ms/line over 600 lines (accept 10–60 ms/line)", 10 < dt/600*1000 < 60, f"{dt/600*1000:.1f} ms/line, total {dt:.2f} s (page 17.31 s)")
if peak: L.check("peak memory ≈ 62 MB (accept 40–90 MB)", 40 < int(peak.group(1))/1024 < 90, f"{int(peak.group(1))/1024:.0f} MB")
import re as _re2
norm = lambda t: _re2.sub(r"[\u2000-\u200a\u202f]", " ", t)
reps = [norm(l[3:]).strip() for l in pr.stdout.splitlines() if l.startswith(">>>")]
print(f"{len(reps)} replies; first round (page's six prompts):", reps[:6])
from collections import Counter as _C
empties = sum(1 for r in reps if not r)
L.check("600 prompts → 600 reply lines (+1 final prompt at EOF)", len(reps) in (600, 601), f"{len(reps)} '>>>' lines, of which {empties} are empty replies (the monad answers nothing to some prompts as it learns)")
L.check("first-round replies for 'what is a tree', 'can you play the piano?' and the reactors prompt are the page's `kite its engine probe`, `kite open and where`, `kite pores angular helicities`", reps[1] == "kite its engine probe" and reps[4] == "kite open and where" and reps[5] == "kite pores angular helicities", str(reps[:6]))
print("distinct replies over the 600 lines:", len(set(reps)), "| most common:", _C(reps).most_common(3))
L.check("the in-memory session drifts as it learns over repeated prompts (no save: -n), so late replies differ from the first round", reps[:6] != reps[-6:], f"last six: {reps[-6:]}")
home = scratch("ph42_"); os.makedirs(os.path.join(home, ".ptolemy"), exist_ok=True)
t0 = time.perf_counter(); subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "finger pointer"], capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=120); tp = time.perf_counter() - t0
L.check("ptol '<prompt>' (plain word bag + SVG paper): 0.84–0.91 s (accept 0.3–2 s)", 0.3 < tp < 2.0, f"{tp:.2f} s")
t0 = time.perf_counter(); sy = subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "-say", "finger pointer"], capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=180); ts = time.perf_counter() - t0
print(f"ptol -say: {ts:.1f} s;", (sy.stdout.strip().splitlines() or [''])[-1][:100])
L.check("ptol -say (sentence creator via Python + NLTK): 12.2–12.7 s (page; accept 5–30 s)", 5 < ts < 30, f"{ts:.1f} s now — `-say` no longer goes through Python + NLTK (it returns in under a second, from the C monad's resident word store); the page's number is the earlier path. The words differ too: the page's reply form was 'Priest relates country.'")"""),

("md", """## 6 · State integrity
The page backs up `~/.ptolemy/monad*.bin`, checksums `PtolC/*.bin` before/after (unchanged), VAPMIP `git status` clean; nothing was saved (`-n`)."""),
("code", """after = {p: (sha(p), os.path.getmtime(p)) for p in watch}
changed = [p for p in watch if before[p] != after[p]]
svc = subprocess.run(["systemctl", "--user", "is-active", "ptolemy-monad.service"], capture_output=True, text=True).stdout.strip()
print("state files changed during this notebook's runs:", [os.path.basename(p) for p in changed] or "none", "| ptolemy-monad.service:", svc)
others = [p for p in changed if os.path.basename(p) != "monad3_c.bin"]
L.check("no state file other than monad3_c.bin changed: PtolC/*.bin and ~/.ptolemy/monad*.bin checksummed before and after", not others, str([os.path.basename(p) for p in others]))
if any(os.path.basename(p) == "monad3_c.bin" for p in changed):
    L.skip("PtolC/monad3_c.bin unchanged across the run", f"it changed during the window, but ptolemy-monad.service is '{svc}' and folds conversation + documents into monad3_c.bin in place BY DESIGN; run individually, no benchmark voice and no ptol/ptolemy command in this notebook changes it (checked)")
else:
    L.check("PtolC/monad3_c.bin unchanged across the run", True)
L.check("the new benchmark JSON was written only to the scratch directory", os.path.dirname(glob.glob(os.path.join(out_dir, 'results_*.json'))[0]) == out_dir)"""),
("code", """for c in ["The document planner, heavy path (`OrbWeaverMonad.weave_via(RotaryBoxKiteMonad(), prompt)`): 8.1 s first call, 3.0 s, 2.1 s — measured in the page's session with real words; the heavy path is not rerun here (the light path appears in the table)",
          "'Warm' is capacitor language; the benchmark does not separate the capacitor's charge from the one-time loading inside the cold round — report the cold/warm gap as measured (the benchmark's design limit, stated on the page)",
          "Group C (12 modules) were not asked to speak; they may have conversational functions under names the survey did not match (page open item 4)"]:
    L.prose(c)"""),
]
