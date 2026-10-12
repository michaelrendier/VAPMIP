#!/usr/bin/env python3
"""verify_spec.py — consistency check for the Context Flow specification.

    python3 verify_spec.py                 check docs, matrix, schemas
    python3 verify_spec.py --render        also regenerate 12_test_matrix.md
    python3 verify_spec.py --calibration D validate calibration items in D (*.jsonl)

Exit code 0 only if every check passes. Standard library only.
"""
import argparse, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ID_RE = re.compile(r"\b([A-Z]{2,5})-(\d{2})(?:\.\.(\d{2}))?\b")
PREFIXES = {"SPL", "SM", "DEC", "TT", "CEN", "RST", "GEN", "ATT", "POS", "BPE", "MASK", "CAL", "PERF"}
RELATIONS = {None, "R-ELAB", "R-EXAM", "R-CAUS", "R-RES", "R-EVID", "R-BACK",
             "R-CONC", "R-COND", "R-CONT", "R-SEQ", "R-LIST", "R-SUM"}


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def ids_in(text):
    out = set()
    for m in ID_RE.finditer(text):
        pre, a, b = m.group(1), int(m.group(2)), m.group(3)
        if pre not in PREFIXES:
            continue
        for n in range(a, (int(b) if b else a) + 1):
            out.add(f"{pre}-{n:02d}")
    return out


def check_matrix(errors):
    m = json.loads(read("test_matrix.json"))
    tests = m["tests"]
    seen = set()
    metrics_doc = read("11_metrics_and_benchmarks.md")
    defined = set(re.findall(r"\*\*(MET-[A-Z0-9]+)", metrics_doc))
    for t in tests:
        tid = t["id"]
        if tid in seen:
            errors.append(f"duplicate test id {tid}")
        seen.add(tid)
        if t["status"] not in m["statuses"]:
            errors.append(f"{tid}: bad status {t['status']}")
        if not os.path.exists(os.path.join(HERE, t["spec"])):
            errors.append(f"{tid}: spec file missing {t['spec']}")
        elif tid not in ids_in(read(t["spec"])):
            errors.append(f"{tid}: not mentioned in its spec {t['spec']}")
        if t["kind"] == "metric" and t["metric"] not in defined:
            errors.append(f"{tid}: metric {t['metric']} not defined in 11_metrics_and_benchmarks.md")
        if t["kind"] == "exact" and t["metric"] != "exact":
            errors.append(f"{tid}: kind exact but metric {t['metric']}")
    # every ID cited in any doc must exist in the matrix (catches typos / orphans)
    for name in sorted(os.listdir(HERE)):
        if name.endswith(".md") and name != "12_test_matrix.md":
            for tid in ids_in(read(name)):
                if tid not in seen:
                    errors.append(f"{name}: cites {tid}, which is not in test_matrix.json")
    return m


def check_docs(errors):
    readme = read("00_README.md")
    for f in re.findall(r"`(\d\d_[a-z_]+\.md)`", readme):
        if not os.path.exists(os.path.join(HERE, f)):
            errors.append(f"00_README.md lists missing file {f}")
    for f in ("test_matrix.json", "verify_spec.py"):
        if not os.path.exists(os.path.join(HERE, f)):
            errors.append(f"missing {f}")
    for s in os.listdir(os.path.join(HERE, "schemas")):
        try:
            json.loads(read(os.path.join("schemas", s)))
        except Exception as e:
            errors.append(f"schema {s} unreadable: {e}")


def render(m):
    lines = ["# 12 — Test Matrix (generated)", "",
             "Generated from `test_matrix.json` by `verify_spec.py --render`. Do not edit by hand.", "",
             f"Matrix version {m['matrix_version']} · spec version {m['spec_version']} · {len(m['tests'])} tests", "",
             "| ID | Area | Title | Metric | Needs set | Threshold | Status | Spec |",
             "|---|---|---|---|---|---|---|---|"]
    for t in m["tests"]:
        lines.append(f"| `{t['id']}` | {t['area']} | {t['title']} | {t['metric']} | "
                     f"{'yes' if t['needs_calibration_set'] else 'no'} | "
                     f"{t['threshold'] if t['threshold'] is not None else '—'} | {t['status']} | {t['spec']} |")
    by = {}
    for t in m["tests"]:
        by[t["status"]] = by.get(t["status"], 0) + 1
    lines += ["", "## Status counts", ""] + [f"- {k}: {v}" for k, v in sorted(by.items())]
    with open(os.path.join(HERE, "12_test_matrix.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def check_calibration(d, errors):
    ids = set()
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                if not line.strip():
                    continue
                where = f"{fn}:{ln}"
                try:
                    it = json.loads(line)
                except Exception as e:
                    errors.append(f"{where}: bad json {e}")
                    continue
                for k in ("id", "tier", "split", "subject_area", "prompt_type", "turns", "response", "expect"):
                    if k not in it:
                        errors.append(f"{where}: missing {k}")
                if "id" not in it:
                    continue
                if it["id"] in ids:
                    errors.append(f"{where}: duplicate id {it['id']}")
                ids.add(it["id"])
                want = "dev" if hashlib.sha256(it["id"].encode()).hexdigest()[0] in "0123456789ab" else "test"
                if it.get("split") != want:
                    errors.append(f"{where}: split {it.get('split')} != hash rule {want}")
                r = it.get("response", {})
                units = r.get("units", [])
                for u in units:
                    if not u.get("text", "").strip():
                        errors.append(f"{where}: empty unit {u.get('unit_id')}")
                    if u.get("relation_to_prev") not in RELATIONS:
                        errors.append(f"{where}: bad relation {u.get('relation_to_prev')}")
                for b in r.get("boundaries", []):
                    if not (1 <= b < len(units)):
                        errors.append(f"{where}: boundary {b} out of range")
    return len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--calibration")
    a = ap.parse_args()
    errors = []
    if a.render:
        render(json.loads(read("test_matrix.json")))
    check_docs(errors)
    m = check_matrix(errors)
    n = None
    if a.calibration:
        n = check_calibration(a.calibration, errors)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(m['tests'])} tests, docs consistent" + (f", {n} calibration items" if n is not None else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
