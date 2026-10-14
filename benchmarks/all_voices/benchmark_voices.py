#!/usr/bin/env python3
"""benchmark_voices.py — benchmark every monad voice the console can select, step by step.

What it does (reproduces VAPMIP docs/wiki/Tuning-the-Engine/42_every_voice_benchmark.md):
  1. discovers the monads exactly as the console does (PtolemyDesktop/ptolemy_console.py discover_monads(): VAPMIP/*monad*.py);
  2. loads each one in a FRESH subprocess exactly as `/monad use <name>` does (load_monad_by_name);
  3. asks the same six prompts twice (round 1 cold, round 2 warm), timing the console import, the module load, the RSS
     before/after, every reply, and the CPU time of the warm round;
  4. if the laptop is on battery (sysfs BAT0 Discharging), samples whole-laptop power every 0.5 s through the warm round
     and reports microwatt-hours per reply (whole laptop, display and OS included).
Modules with no speaking entry point report 'no recognised chat interface' (that is a result, not a failure).

Usage (from VAPMIP/):   python3 benchmarks/all_voices/benchmark_voices.py [--out DIR] [--only NAME ...]
Needs the PtolemyDesktop venv python if the system python3 cannot import nltk (see PtolemyDesktop/.venv).
Side effects: none intended. Nothing that learns or writes is called (no hear/ingest/checkpoint)."""
import argparse, contextlib, glob, io, json, os, subprocess, sys, threading, time, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
VP = os.path.dirname(os.path.dirname(HERE))                      # VAPMIP/
PD = os.path.join(os.path.dirname(VP), "PtolemyDesktop")
PROMPTS = ["finger pointer", "what is a tree", "neutron generation in different reactor types",
           "good morning", "can you play the piano?", "the first reactor was built after neutrons were discovered"]
BAT = "/sys/class/power_supply/BAT0/"

def rss_mb():
    for l in open("/proc/self/status"):
        if l.startswith("VmRSS"): return int(l.split()[1]) / 1024

def child(name):
    sys.path.insert(0, VP); sys.path.insert(0, PD)
    out = {"name": name, "rss_start_mb": round(rss_mb(), 1)}; quiet = io.StringIO()
    def emit(d): print("BENCH_JSON:" + json.dumps(d, default=str)); sys.stdout.flush()
    try:
        t = time.perf_counter()
        with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
            import ptolemy_console as pc
        out["console_import_s"] = round(time.perf_counter() - t, 2); out["rss_console_mb"] = round(rss_mb(), 1)
        class Next:
            kind = "dummy"; enabled = True
            def say(self, t): return ("(next)", {})
            def status(self): return "dummy"
        t = time.perf_counter()
        with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
            m = pc.load_monad_by_name(name, Next())
        out.update(load_s=round(time.perf_counter() - t, 2), rss_loaded_mb=round(rss_mb(), 1),
                   adapter=type(m).__name__, kind=getattr(m, "kind", ""))
    except BaseException as e:
        out["error"] = f"{type(e).__name__}: {str(e)[:300]}"; emit(out); return
    calls = []
    for rnd in (1, 2):
        if rnd == 2: w0, c0 = time.time(), time.process_time()
        for p in PROMPTS:
            t = time.perf_counter()
            try:
                with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                    r = m.say(p)
                reply, err = (r[0] if isinstance(r, tuple) else r), None
            except BaseException as e:
                reply, err = None, f"{type(e).__name__}: {str(e)[:200]}"
            calls.append({"round": rnd, "prompt": p, "ms": round((time.perf_counter() - t) * 1000, 2),
                          "reply": None if reply is None else str(reply)[:300], "error": err})
        if rnd == 2: w1, c1 = time.time(), time.process_time()
    out.update(calls=calls, rss_end_mb=round(rss_mb(), 1), warm_t0=w0, warm_t1=w1, warm_cpu_s=round(c1 - c0, 3))
    emit(out)

def parent(args):
    names = sorted(os.path.splitext(os.path.basename(h))[0] for h in glob.glob(os.path.join(VP, "*monad*.py"))
                   if not os.path.basename(h).startswith("_"))
    if args.only: names = [n for n in names if n in args.only]
    on_battery = False
    try: on_battery = open(BAT + "status").read().strip() == "Discharging"
    except OSError: pass
    results = []
    for n in names:
        buf, stop = [], threading.Event()
        def sampler():
            while not stop.is_set():
                try: buf.append((time.time(), int(open(BAT + "power_now").read()) / 1e6))
                except OSError: pass
                time.sleep(0.5)
        th = threading.Thread(target=sampler) if on_battery else None
        if th: th.start()
        try:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", n], cwd=VP, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=300)
            line = [l for l in p.stdout.splitlines() if l.startswith("BENCH_JSON:")]
            r = json.loads(line[-1][11:]) if line else {"name": n, "error": f"no result (exit {p.returncode}) " + (p.stderr or "")[-200:]}
        except subprocess.TimeoutExpired:
            r = {"name": n, "error": "timeout 300 s"}
        stop.set()
        if th: th.join()
        ok = [c for c in r.get("calls", []) if c["round"] == 2 and not c["error"]]
        if ok:
            r["warm_ms_mean"] = round(st.mean(c["ms"] for c in ok), 2)
            w = [x[1] for x in buf if r["warm_t0"] <= x[0] <= r["warm_t1"]]
            if w:
                r["warm_mean_W"] = round(st.mean(w), 2)
                r["whole_laptop_uWh_per_reply"] = round(r["warm_mean_W"] * r["warm_ms_mean"] / 3.6, 2)
        results.append(r)
        print(f"{n:42s}", r.get("error", "")[:90] or f"load {r['load_s']}s  warm {r.get('warm_ms_mean')} ms  rss +{round(r['rss_loaded_mb'] - r['rss_console_mb'], 1)} MB", flush=True)
    os.makedirs(args.out, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    json.dump({"date": stamp, "on_battery": on_battery, "prompts": PROMPTS, "results": results},
              open(os.path.join(args.out, f"results_{stamp}.json"), "w"), indent=1, default=str)
    speaking = [r for r in results if not r.get("error")]
    print(f"\n{len(results)} monad modules, {len(speaking)} selectable and speaking; results in {args.out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--child"); ap.add_argument("--out", default=os.path.join(HERE, "runs"))
    ap.add_argument("--only", nargs="*"); a = ap.parse_args()
    child(a.child) if a.child else parent(a)
