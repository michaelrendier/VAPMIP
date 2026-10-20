#!/usr/bin/env python3
"""exp_v2_assess.py — where did each list word end up, in each of the experiment's bins (read only).

Bins (experiment_v2/bins): test_chinese_v2 (Han alphabet), test_english_v2 (ASCII-95), test_chinese_english_v2 (union alphabet, zh pass then en pass),
test_english_chinese_v2 (union alphabet, en pass then zh pass), plus the saved states between the two passes (bins/stage).
For every list word the address is recomputed here exactly as monad_word_coords does (bijective Horner over the build's alphabet, wrap mod 2^64, golden-ratio
seed), then compared with what the bin holds at that slot.  Nothing is repaired; every disagreement is a row in the output.
Writes experiment_v2/results/*.tsv and results/summary.json."""
import csv, json, math, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); EXP = os.path.join(ROOT, "experiment_v2")
sys.path.insert(0, HERE)
import ptol_bin, gen_alphabet
from dprint import dprint
M64 = (1 << 64) - 1; PHI = 0x9E3779B97F4A7C15; N = 25000; DSTAR = 0.24600; OMEGA = 0.56714

def zeros(n):                     # monad.c generate_zeros, same arithmetic
    ex = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
          52.970321, 56.446248, 59.347044, 60.831779, 65.112544, 67.079811, 69.546402, 72.067158, 75.704691, 77.144840]
    z = ex[:min(n, 20)] + [0.0] * max(0, n - 20); tp = 2.0 * math.pi
    for k in range(21, n + 1):
        t = z[k - 2] + (z[k - 2] - z[k - 3])
        for _ in range(30):
            if t < 2.0: t = k * 3.0
            nt = (t / tp) * (math.log(t / tp) - 1.0) + 0.875; dnt = math.log(t / tp) / tp
            if abs(dnt) < 1e-15: break
            dt = (nt - k) / dnt; t -= dt
            if abs(dt) < 1e-4: break
        z[k - 1] = t
    return z
Z = zeros(N)

def make_addr(kind):
    if kind == "ascii95":
        def rank(c): return ord(c) - 31 if 32 <= ord(c) < 127 else 0
        base = 95
    else:
        alpha = sorted(set({"zh": gen_alphabet.zh(), "un": gen_alphabet.union()}[kind])); r = {c: i + 1 for i, c in enumerate(alpha)}
        def rank(c): return r.get(ord(c), 0)
        base = len(alpha)
    def addr(w):
        v = 0
        for c in w:
            v = (v * base + rank(c)) & M64
        if v > 0: v -= 1
        s = (v * PHI) & M64
        return (s * N) >> 64, DSTAR + (s >> 11) / 9007199254740992.0 * (OMEGA - DSTAR), any(rank(c) == 0 for c in w)
    return addr
ADDR = {"zh": make_addr("zh"), "en": make_addr("ascii95"), "un": make_addr("un")}

L = list(csv.DictReader(open(os.path.join(EXP, "list.tsv"), encoding="utf-8"), delimiter="\t"))
CNT = {(r["lang"], r["word"]): int(r["count"]) for r in csv.DictReader(open(os.path.join(EXP, "corpus_counts.tsv"), encoding="utf-8"), delimiter="\t")}
os.makedirs(os.path.join(EXP, "results"), exist_ok=True)

import re
def feed(log):
    """-> (set of words the engine's filter rejected, {(held, arriving): events}) from a PTOL_DPRINT feed"""
    rej = set(); sh = collections.Counter(); held = arr = None
    for l in open(os.path.join(EXP, "logs", log), encoding="utf-8"):
        m = re.match(r'\[dp\] learn\.rejected = "(.*)"', l)
        if m: rej.add(m.group(1)); continue
        m = re.match(r'\[dp\] learn\.slot_shared\.held = "(.*)"', l)
        if m: held = m.group(1); continue
        m = re.match(r'\[dp\] learn\.slot_shared\.arriving = "(.*)"', l)
        if m: sh[(held, m.group(1))] += 1
    return rej, sh
REJ_EN, SH_EN = feed("test_english_v2.en.dprint.log"); _, SH_ZH = feed("test_chinese_v2.zh.dprint.log")

class Bin:
    def __init__(self, name, path, build):
        self.name, self.build = name, build; d = ptol_bin.load(path); self.d = d
        self.occ = {v[0]: v for v in d["vocab"]}                       # idx -> (idx, word, E, ...)
        e = d["edges"]; self.deg = np.zeros(N, dtype=np.int64); self.wsum = np.zeros(N)
        np.add.at(self.deg, e["i"].astype(np.int64), 1); np.add.at(self.deg, e["j"].astype(np.int64), 1)
        np.add.at(self.wsum, e["i"].astype(np.int64), e["w"]); np.add.at(self.wsum, e["j"].astype(np.int64), e["w"])
        self.beta = d["beta"]
    def locate(self, lang, w):
        """-> dict(idx, gamma, E_addr, state, occupant, beta, deg, count)"""
        idx, E, outside = ADDR[self.build](w); occ = self.occ.get(idx); cnt = CNT.get((lang, w), 0)
        if outside: st = "NOT-IN-ALPHABET"
        elif cnt == 0: st = "NEVER-IN-CORPUS"
        elif lang == "en" and len(w) < 2: st = "DROPPED-BY-TOKENIZER(<2 letters)"
        elif lang == "en" and w in REJ_EN: st = "REJECTED-BY-FILTER"
        elif occ and occ[1] == w: st = "SEATED"
        elif occ: st = "OUTRANKED-BY-HIGHER-E" if occ[2] > E else "UNEXPLAINED(slot held by lower-E word)"
        else: st = "UNEXPLAINED(slot empty)"
        r = dict(idx=idx, gamma=Z[idx], E=E, state=st, occupant=(occ[1] if occ else ""), occE=(occ[2] if occ else ""),
                 beta=float(self.beta[idx]), deg=int(self.deg[idx]), wsum=float(self.wsum[idx]), count=cnt)
        dprint(f"{self.name}.{lang}.{w}", r)
        return r

P = os.path.join(EXP, "bins")
BINS = {n: Bin(n, os.path.join(P, f"{n}.bin"), b) for n, b in [
    ("test_chinese_v2", "zh"), ("test_english_v2", "ascii95" if False else "en"), ("test_chinese_english_v2", "un"), ("test_english_chinese_v2", "un")]}
STAGE = {"test_chinese_english_v2": Bin("after_zh", os.path.join(P, "stage", "test_chinese_english_v2.after_zh.bin"), "un"),
         "test_english_chinese_v2": Bin("after_en", os.path.join(P, "stage", "test_english_chinese_v2.after_en.bin"), "un")}
enw = sorted({r["en"] for r in L if r["en"] != "-"}); zhw = sorted({r["zh"] for r in L if r["zh"] != "-"})
summary = {"engine_rejected_words(english feed)": sorted(REJ_EN), "slot_sharing_events_distinct_pairs": dict(en_pure=len(SH_EN), zh_pure=len(SH_ZH))}; maps = {}
for name, b in BINS.items():
    langs = [("zh", zhw)] if name == "test_chinese_v2" else [("en", enw)] if name == "test_english_v2" else [("zh", zhw), ("en", enw)]
    rows = []
    for lang, ws in langs:
        for w in ws:
            x = b.locate(lang, w); x.update(lang=lang, word=w); rows.append(x)
    maps[name] = {(x["lang"], x["word"]): x for x in rows}
    with open(os.path.join(EXP, "results", f"{name}_map.tsv"), "w", encoding="utf-8") as o:
        o.write("lang\tword\tslot\tgamma\tE_address\tstate\toccupant\toccupant_E\tbeta\tdegree\tedge_weight_sum\tcorpus_count\n")
        for x in rows: o.write("\t".join(str(x[k]) for k in ("lang", "word", "idx", "gamma", "E", "state", "occupant", "occE", "beta", "deg", "wsum", "count")).replace("\t\t", "\t\t") + "\n")
    s = {}
    for lang, _ in langs:
        c = collections.Counter(x["state"] for x in rows if x["lang"] == lang)
        # slots shared among list words of the same language / across
        sl = collections.defaultdict(list)
        for x in rows:
            sl[x["idx"]].append((x["lang"], x["word"]))
        s[lang] = dict(words=sum(1 for x in rows if x["lang"] == lang), states=dict(c))
    s["slots_shared_by_list_words"] = {str(k): v for k, v in sl.items() if len(v) > 1}
    s["cross_language_slot_sharing"] = sum(1 for v in sl.values() if len({a for a, _ in v}) > 1)
    s["header"] = dict(vocab=b.d["vocab_size"], A=b.d["A_size"], word_count=b.d["word_count"], version=b.d["version"])
    # engine address vs stored slot for every seated word (python port must equal the C engine)
    s["address_port_check"] = dict(seated=sum(1 for x in rows if x["state"] == "SEATED"),
        stored_E_mismatch=sum(1 for x in rows if x["state"] == "SEATED" and abs(b.occ[x["idx"]][2] - x["E"]) > 1e-12))
    summary[name] = s

# ── pair landing: matched rows, English word vs its Chinese word ─────────────────────────────────
def spacing(g): return 2 * math.pi / math.log(g / (2 * math.pi))
def pair_stats(en_map, zh_map, label):
    D = []; rows = []
    for r in L:
        if r["en"] == "-" or r["zh"] == "-": continue
        e = en_map.get(("en", r["en"])); z = zh_map.get(("zh", r["zh"]))
        if not e or not z: continue
        di = z["idx"] - e["idx"]; dg = (z["gamma"] - e["gamma"]) / spacing(0.5 * (z["gamma"] + e["gamma"])); dE = z["E"] - e["E"]
        rows.append(dict(n=r["n"], kind=r["kind"], en=r["en"], zh=r["zh"], status=r["status"], en_slot=e["idx"], zh_slot=z["idx"], d_slot=di, d_gamma_spacings=dg, dE=dE,
                         en_state=e["state"], zh_state=z["state"]))
        D.append((abs(di), dg, dE))
    a = np.array([x[0] for x in D]); g = np.array([x[1] for x in D]); E = np.array([x[2] for x in D]); n = len(D)
    out = dict(pairs=n, same_slot=int((a == 0).sum()), within_1=int((a <= 1).sum()), within_3=int((a <= 3).sum()), within_10=int((a <= 10).sum()),
               expected_uniform=dict(same_slot=round(n / N, 3), within_1=round(n * 3 / N, 2), within_3=round(n * 7 / N, 2), within_10=round(n * 21 / N, 2)),
               abs_dslot_over_N_quartiles=[round(float(q) / N, 4) for q in np.percentile(a, [25, 50, 75])], expected_if_unrelated_quartiles=[0.1340, 0.2929, 0.5],
               dgamma_spacings_abs_quartiles=[round(float(q), 1) for q in np.percentile(np.abs(g), [25, 50, 75])],
               dE_abs_quartiles=[round(float(q), 4) for q in np.percentile(np.abs(E), [25, 50, 75])], expected_dE_abs_quartiles_if_unrelated=[round(0.1340 * (OMEGA - DSTAR), 4), round(0.2929 * (OMEGA - DSTAR), 4), round(0.5 * (OMEGA - DSTAR), 4)],
               dslot_hist_over_N_10bins=np.histogram(a / N, bins=10, range=(0, 1))[0].tolist())
    with open(os.path.join(EXP, "results", f"pairs_{label}.tsv"), "w", encoding="utf-8") as o:
        o.write("\t".join(rows[0].keys()) + "\n"); [o.write("\t".join(str(v) for v in r.values()) + "\n") for r in rows]
    return out
summary["pairs_pure(en bin vs zh bin)"] = pair_stats(maps["test_english_v2"], maps["test_chinese_v2"], "pure")
for n in ("test_chinese_english_v2", "test_english_chinese_v2"):
    summary[f"pairs_{n}"] = pair_stats(maps[n], maps[n], n)

# ── what the second pass did to the first language (stage state -> final) ───────────────────────
for n, st in STAGE.items():
    fin = BINS[n]; first = "zh" if n.startswith("test_chinese") else "en"; ws = zhw if first == "zh" else enw
    ch = collections.Counter(); db = []
    for w in ws:
        a = st.locate(first, w); b = fin.locate(first, w)
        ch[(a["state"], b["state"])] += 1
        if a["state"] == "SEATED": db.append((fin.beta[b["idx"]] - st.beta[a["idx"]], fin.deg[b["idx"]] - st.deg[a["idx"]]))
    occ_changed = sum(1 for i, v in st.occ.items() if (fin.occ.get(i) or (0, ""))[1] != v[1])
    dbeta = np.array([x[0] for x in db])
    summary[f"second_pass_effect_on_{first}_{n}"] = dict(
        first_language=first, state_transitions={f"{a} -> {b}": c for (a, b), c in ch.items()},
        slots_whose_word_changed=occ_changed, first_pass_vocab=st.d["vocab_size"], final_vocab=fin.d["vocab_size"],
        first_language_words_beta_changed=int((np.abs(dbeta) > 1e-12).sum()), seated_words=len(db),
        beta_change_quartiles=[float(q) for q in np.percentile(dbeta, [0, 25, 50, 75, 100])] if len(dbeta) else None,
        degree_change_nonzero=int(sum(1 for x in db if x[1] != 0)))

# ── the two final bins against each other (does order matter?) ───────────────────────────────────
a, b = BINS["test_chinese_english_v2"], BINS["test_english_chinese_v2"]
wa = {i: v[1] for i, v in a.occ.items()}; wb = {i: v[1] for i, v in b.occ.items()}
ea, eb = a.d["edges"], b.d["edges"]
ka = {(int(i), int(j)): float(w) for i, j, w in zip(ea["i"], ea["j"], ea["w"])}; kb = {(int(i), int(j)): float(w) for i, j, w in zip(eb["i"], eb["j"], eb["w"])}
both = set(ka) & set(kb)
summary["order_effect(zh_first_vs_en_first)"] = dict(
    slots_with_different_word=sum(1 for i in set(wa) | set(wb) if wa.get(i) != wb.get(i)), vocab=(len(wa), len(wb)),
    beta_max_abs_diff=float(np.abs(a.beta - b.beta).max()), beta_slots_differing=int((np.abs(a.beta - b.beta) > 1e-12).sum()),
    edges=(len(ka), len(kb)), edges_only_in_zh_first=len(set(ka) - set(kb)), edges_only_in_en_first=len(set(kb) - set(ka)),
    edge_weight_max_abs_diff=max((abs(ka[k] - kb[k]) for k in both), default=0.0), edge_weights_differing=sum(1 for k in both if abs(ka[k] - kb[k]) > 1e-9))
# cross-language edges in the union bins: an edge joining a slot seated by an en list word to a slot seated by a zh list word
for n in ("test_chinese_english_v2", "test_english_chinese_v2"):
    bn = BINS[n]; lang_of = {}
    for (lg, w), x in maps[n].items():
        if x["state"] == "SEATED": lang_of[x["idx"]] = lg
    e = bn.d["edges"]; cross = sum(1 for i, j in zip(e["i"], e["j"]) if lang_of.get(int(i)) and lang_of.get(int(j)) and lang_of[int(i)] != lang_of[int(j)])
    summary[n]["edges_joining_an_en_slot_and_a_zh_slot"] = cross
# pure English / Chinese words: same slot in union build as in pure build?
for lang, pure, ws in (("en", "test_english_v2", enw), ("zh", "test_chinese_v2", zhw)):
    summary[f"slot_unchanged_pure_vs_union_{lang}"] = dict(words=len(ws), same_slot=sum(1 for w in ws if maps[pure][(lang, w)]["idx"] == maps["test_chinese_english_v2"][(lang, w)]["idx"]))
json.dump(summary, open(os.path.join(EXP, "results", "summary.json"), "w"), indent=1, ensure_ascii=False, default=str)
print(json.dumps({k: v for k, v in summary.items() if not k.startswith("pairs_test")}, indent=1, ensure_ascii=False, default=str)[:6000])
