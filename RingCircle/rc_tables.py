#!/usr/bin/env python3
"""rc_tables.py — writes slot_table.md (per-slot table) from results.json, rc10_results.json, rc12_results.json.  No numbers are typed by hand."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json"))); E = json.load(open(os.path.join(HERE, "rc10_results.json"))); U = json.load(open(os.path.join(HERE, "rc12_results.json")))
deform = {tuple(p) for p in R["RC2_deforming_pairs"]}
rows = ["| slot k | prime p_k | engine leaf path (L=0, R=1) | generator slots | products of its generators: bracketing → sign·(−1)^parity | circles that deform with it (anticommutator ‖·‖ = 4√2) | Euler circle of p_k at σ = ½: centre, radius | angular rate ln p (UNS: ln10·log10 p) |", "|---|---|---|---|---|---|---|---|"]
for k in range(16):
    gens = R["RC4_generator_products_per_slot"].get(str(k), {}).get("generators", [])
    cons = R["RC4_generator_products_per_slot"].get(str(k), {}).get("bracketing_constant_c", {})
    cs = "; ".join(f"{b} → {v}" for b, v in cons.items()) if len(gens) >= 2 else ("—" if k else "identity e₀")
    if k and len(gens) == 1: cs = "single generator"
    partners = sorted({b if a == k else a for a, b in deform if k in (a, b)})
    u = U[str(k)]
    rows.append(f"| {k} | {u['prime']} | {E['single_slots'][str(k)]['leaf']} | {', '.join(map(str, gens)) if gens else '—'} | {cs} | {', '.join(map(str, partners)) if partners else '—'} | {u['centre_predicted']:.4f}, {u['radius_predicted']:.4f} | {u['angular_rate_ln_p']:.4f} ({u['UNS_rate_ln10_times_log10_p']:.4f}) |")
open(os.path.join(HERE, "slot_table.md"), "w").write("\n".join(rows) + "\n")
print("\n".join(rows[:8]))
