#!/usr/bin/env python3
"""exp_v2_wiki.py — write the live-snapshot wiki page and 1024.md from experiment_v2/results.  Overwrites (the page is a workbench snapshot, not a log).
Blocks are delimited  <!-- @BLOCK name -->  ...  <!-- @END name -->  so tools/wb_pull.py can print one by name."""
import csv, json, os, sys, hashlib, subprocess, collections, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); EXP = os.path.join(ROOT, "experiment_v2"); RES = os.path.join(EXP, "results")
WIKI = os.path.abspath(os.path.join(ROOT, "..", "docs", "wiki", "Tuning-the-Semantic-Prime-Concept-Engine"))
S = json.load(open(os.path.join(RES, "summary.json")))
L = list(csv.DictReader(open(os.path.join(EXP, "list.tsv"), encoding="utf-8"), delimiter="\t"))
def tsv(n): return list(csv.DictReader(open(os.path.join(RES, n), encoding="utf-8"), delimiter="\t"))
MAP = {n: {(r["lang"], r["word"]): r for r in tsv(f"{n}_map.tsv")} for n in ("test_chinese_v2", "test_english_v2", "test_chinese_english_v2", "test_english_chinese_v2")}
sha = {l.split()[1].split("/")[-1]: l.split()[0] for l in open(os.path.join(EXP, "bins", "SHA256SUMS")) if "/stage/" not in l}
commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
ABBR = {"SEATED": "S", "OUTRANKED-BY-HIGHER-E": "O", "NEVER-IN-CORPUS": "N", "NOT-IN-ALPHABET": "A", "REJECTED-BY-FILTER": "F", "DROPPED-BY-TOKENIZER(<2 letters)": "T",
        "UNEXPLAINED(slot empty)": "?", "UNEXPLAINED(slot held by lower-E word)": "?"}
LEG = "S seated · O outranked (slot label taken by a word with higher E) · N never in the filtered corpus · A character outside the build's alphabet · F rejected by the engine's token filter · T dropped by the tokenizer (< 2 letters) · ? unexplained"
def blk(name, body): return f"<!-- @BLOCK {name} -->\n{body.rstrip()}\n<!-- @END {name} -->\n"
def states_tbl(name, langs):
    out = ["| language | list words | " + " | ".join(ABBR) + " |", "|---|---:|" + "---:|" * len(ABBR)]
    for lg in langs:
        st = S[name][lg]["states"]; out.append(f"| {lg} | {S[name][lg]['words']} | " + " | ".join(str(st.get(k, 0)) for k in ABBR) + " |")
    return "\n".join(out)
def words_in(name, lg, state): return " ".join(w for (l, w), r in MAP[name].items() if l == lg and r["state"] == state)
def shared_tbl(name):
    sl = collections.defaultdict(list)
    for (lg, w), r in MAP[name].items(): sl[int(r["slot"])].append((lg, w, float(r["E_address"])))
    rows = ["| slot | γ | words that hash here (E) | label held in the bin |", "|---:|---:|---|---|"]
    n = 0
    for i in sorted(sl):
        if len(sl[i]) > 1:
            held = next((r["occupant"] for r in MAP[name].values() if int(r["slot"]) == i and r["occupant"]), "")
            g = next(r["gamma"] for r in MAP[name].values() if int(r["slot"]) == i)
            rows.append(f"| {i} | {float(g):.3f} | " + ", ".join(f"{w} [{lg}] {e:.4f}" for lg, w, e in sl[i]) + f" | {held} |"); n += 1
    return "\n".join(rows) if n else "none"
def bin_block(name, langs):
    h = S[name]["header"]; t = [f"**`{name}.bin`** · sha256 `{sha.get(name + '.bin', '')[:16]}…` · header version {h['version']} · vocab {h['vocab']:,} · A-edges {h['A']:,} · word_count {h['word_count']:,} · repo commit `{commit}` · table `experiment_v2/results/{name}_map.tsv`",
        "", "Build: " + {"test_chinese_v2": "Han alphabet (97,518 characters), `-DHAN_RUN` (a run of Han characters is one token)", "test_english_v2": "ASCII-95, unmodified tokenizer",
                          "test_chinese_english_v2": "union alphabet (' a–z + 97,518 Han = 97,545), `-DHAN_RUN`; Chinese pass, then English pass on top",
                          "test_english_chinese_v2": "union alphabet (' a–z + 97,518 Han = 97,545), `-DHAN_RUN`; English pass, then Chinese pass on top"}[name],
        "", "σ: the bin stores no σ per word; every seated word sits at its zero `zeros[slot]` (γ in the table) and carries E. `σ=0.5 (Noether forcing)` is a constant printed by the engine.", "",
        states_tbl(name, langs), "", "Legend: " + LEG, ""]
    for lg in langs:
        for stt in ("OUTRANKED-BY-HIGHER-E", "NEVER-IN-CORPUS", "NOT-IN-ALPHABET", "REJECTED-BY-FILTER", "DROPPED-BY-TOKENIZER(<2 letters)"):
            ws = words_in(name, lg, stt)
            if ws: t.append(f"- **{lg} {stt}**: {ws}")
    t += ["", f"List words sharing a slot with another list word: {len(S[name]['slots_shared_by_list_words'])} slots; across languages: {S[name]['cross_language_slot_sharing']}.", "", shared_tbl(name)]
    if "edges_joining_an_en_slot_and_a_zh_slot" in S[name]:
        t += ["", f"Edges joining a slot seated by an English list word to a slot seated by a Chinese list word: **{S[name]['edges_joining_an_en_slot_and_a_zh_slot']:,}**."]
    t += ["", f"Python address port vs the C engine: {S[name]['address_port_check']['seated']} seated words checked, E mismatches {S[name]['address_port_check']['stored_E_mismatch']}."]
    return "\n".join(t)
def pair_block(key, title):
    p = S[key]; e = p["expected_uniform"]
    return "\n".join([f"**{title}**  ({p['pairs']} matched pairs: an English word and its Chinese word; table `results/pairs_{ 'pure' if 'pure' in key else key[6:]}.tsv`)", "",
        "| measure | observed | expected if the two placements are unrelated |", "|---|---:|---:|",
        f"| same slot | {p['same_slot']} | {e['same_slot']} |", f"| within 1 slot | {p['within_1']} | {e['within_1']} |", f"| within 3 slots | {p['within_3']} | {e['within_3']} |", f"| within 10 slots | {p['within_10']} | {e['within_10']} |",
        f"| \\|Δslot\\|/N quartiles | {p['abs_dslot_over_N_quartiles']} | {p['expected_if_unrelated_quartiles']} |",
        f"| \\|ΔE\\| quartiles | {p['dE_abs_quartiles']} | {p['expected_dE_abs_quartiles_if_unrelated']} |",
        f"| \\|Δγ\\| in local zero spacings, quartiles | {p['dgamma_spacings_abs_quartiles']} | — |", "",
        f"Histogram of \\|Δslot\\|/N in ten equal bins: {p['dslot_hist_over_N_10bins']}  (unrelated placements give a falling triangle: ≈ 19 %, 17 %, 15 % … 1 % of pairs)."])
def second_block(n):
    k = [x for x in S if x.startswith("second_pass_effect") and x.endswith(n)][0]; v = S[k]
    return "\n".join([f"**{n}** — what the second language's pass did to the first language ({v['first_language']}) · stage file `bins/stage/`", "",
        f"- first-pass vocab {v['first_pass_vocab']:,} → final vocab {v['final_vocab']:,}", f"- slots whose label word changed: **{v['slots_whose_word_changed']}**",
        f"- first-language list words whose β changed: **{v['first_language_words_beta_changed']}** of {v['seated_words']}  (β change min/q1/median/q3/max: {v['beta_change_quartiles']})",
        f"- first-language list words whose edge count changed: {v['degree_change_nonzero']}", "- state transitions (first pass → final):"] + [f"  - {a}: {c}" for a, c in v["state_transitions"].items()])
o = S["order_effect(zh_first_vs_en_first)"]
_dev = max(abs(float(r["E_address"]) - (0.24600 + int(r["slot"]) / 25000 * (0.56714 - 0.24600))) for r in MAP["test_english_v2"].values() if r["state"] == "SEATED")
_devz = max(abs(float(r["E_address"]) - (0.24600 + int(r["slot"]) / 25000 * (0.56714 - 0.24600))) for r in MAP["test_chinese_v2"].values() if r["state"] == "SEATED")
fault = [r for r in L if r["kind"].startswith("FAULT")]
def st(name, lg, w):
    r = MAP[name].get((lg, w)); return "" if not r else f"{ABBR.get(r['state'], r['state'])} {r['slot']}"
ft = ["| kind | English | Chinese | en bin | zh bin | en in union | zh in union |", "|---|---|---|---|---|---|---|"]
for r in fault:
    ft.append(f"| {r['kind'].split(':')[1]} | {r['en']} | {r['zh']} | {st('test_english_v2','en',r['en']) if r['en']!='-' else ''} | {st('test_chinese_v2','zh',r['zh']) if r['zh']!='-' else ''} | "
              f"{st('test_chinese_english_v2','en',r['en']) if r['en']!='-' else ''} | {st('test_chinese_english_v2','zh',r['zh']) if r['zh']!='-' else ''} |")
direct = collections.Counter(r["status"] for r in L if r["kind"] == "MATCHED")
page = [f"# 11 · Baseline mapping — Chinese and English, four bins (live snapshot)", "",
 f"Snapshot {datetime.date.today()} · commit `{commit}` · rewritten on every run (workbench notepad, not a log). Pull one block into context with `python3 tools/wb_pull.py <BLOCK>` "
 f"(blocks: METHOD, test_chinese_v2.bin, test_english_v2.bin, test_chinese_english_v2.bin, test_english_chinese_v2.bin, PAIRS_pure, PAIRS_chinese_english, SECOND_PASS_chinese_first, SECOND_PASS_english_first, ORDER_EFFECT, FAULT_ROWS, OBSERVATIONS). "
 "The word list is `1024.md` in this directory.", ""]
page.append(blk("METHOD", f"""**Experiment.** Two languages, mapped independently, then each added to the other. Same engine, same N = 25,000, no tuning. Per-language alphabets: ASCII-95 for English, the Han set for Chinese, the union for the mixed bins.
Word list (`experiment_v2/list.tsv`): 1,024 matched rows (the frozen calibration list: 512 simple + 512 contextual English words; Chinese analog DIRECT = CC-CEDICT lists the English word as a whole gloss: {direct['DIRECT']} rows; NO-DIRECT = an interpretation kept as it was: {direct['NO-DIRECT']} rows) + {len(fault)} FAULT rows on purpose.
Distinct words: English {len({r['en'] for r in L if r['en']!='-'})}, Chinese {len({r['zh'] for r in L if r['zh']!='-'})}.
Corpora: the v1 English and Chinese texts filtered to the list words (one line per sentence; English tokens `[a-z']+` in the list; Chinese Han runs segmented by longest match over the list, other characters dropped), `experiment_v2/text_en.txt`, `text_zh.txt`.
Chinese tokenizer: `-DHAN_RUN` — a run of Han characters is one token. Everything else in the engine is as it was.
Built by `tools/exp_v2_run.sh` (deterministic: two runs gave byte-identical bins; sha256 in `experiment_v2/bins/SHA256SUMS`). Assessed by `tools/exp_v2_assess.py`. Debug feed: `PTOL_DPRINT=1` (dprint protocol), logs in `experiment_v2/logs/`.
Seated = the slot's label is the word. When two words hash to one slot the engine adds all β to the slot and gives the label to the word with the higher E (monad.c learn: `E > vocab[idx].E`), whatever the order they arrive in."""))
page.append(blk("test_chinese_v2.bin", bin_block("test_chinese_v2", ["zh"])))
page.append(blk("test_english_v2.bin", bin_block("test_english_v2", ["en"])))
page.append(blk("test_chinese_english_v2.bin", bin_block("test_chinese_english_v2", ["zh", "en"])))
page.append(blk("test_english_chinese_v2.bin", bin_block("test_english_chinese_v2", ["zh", "en"])))
page.append(blk("PAIRS_pure", pair_block("pairs_pure(en bin vs zh bin)", "Where the English word and its Chinese word landed — English in test_english_v2.bin, Chinese in test_chinese_v2.bin")))
page.append(blk("PAIRS_chinese_english", pair_block("pairs_test_chinese_english_v2", "The same pairs inside one union-alphabet table (test_chinese_english_v2.bin = test_english_chinese_v2.bin positions)")))
page.append(blk("SECOND_PASS_chinese_first", second_block("test_chinese_english_v2")))
page.append(blk("SECOND_PASS_english_first", second_block("test_english_chinese_v2")))
page.append(blk("ORDER_EFFECT", "\n".join(["**Chinese-first final bin against English-first final bin**", "",
  f"- vocab {o['vocab']}; slots whose label differs: **{o['slots_with_different_word']}**",
  f"- β: max |difference| {o['beta_max_abs_diff']:.3g} over {o['beta_slots_differing']} slots", f"- A-edges: {o['edges']}; only in Chinese-first {o['edges_only_in_zh_first']}; only in English-first {o['edges_only_in_en_first']}",
  f"- edge weights: {o['edge_weights_differing']} of the shared edges differ (max |difference| {o['edge_weight_max_abs_diff']:.3g})", "",
  f"Same slot in the pure build and the union build: English {S['slot_unchanged_pure_vs_union_en']['same_slot']} of {S['slot_unchanged_pure_vs_union_en']['words']}; Chinese {S['slot_unchanged_pure_vs_union_zh']['same_slot']} of {S['slot_unchanged_pure_vs_union_zh']['words']}."])))
page.append(blk("FAULT_ROWS", "State and slot of each deliberately faulty row, per bin (" + LEG + ")\n\n" + "\n".join(ft)))
page.append(blk("OBSERVATIONS", f"""Measurements only, nothing repaired.
1. Pure English and pure Chinese: every list word that reached the engine and was not outranked has its own slot and sits at `zeros[slot]`; the Python port of the address reproduces every stored E (0 mismatches).
2. Matched pairs land as unrelated placements do (PAIRS_pure): no pair shares a slot; the |Δslot|/N quartiles are the triangle for two independent uniform placements.
3. The engine's slot label goes to the higher-E word, not the first arrival; both orders end with the same labels (ORDER_EFFECT: {o['slots_with_different_word']} differing).
4. The mixed bins have {S['test_chinese_english_v2']['edges_joining_an_en_slot_and_a_zh_slot']:,} edges joining an English-seated slot to a Chinese-seated slot although no sentence holds both languages: they run through the {S['test_chinese_english_v2']['cross_language_slot_sharing']} slots where an English and a Chinese list word hash together.
5. English tokens dropped before seating: tokens under two letters (`a`, `i`) by the tokenizer, and {len(S['engine_rejected_words(english feed)'])} words by the token filter: {' '.join(S['engine_rejected_words(english feed)'])}.
6. Order effect on values: β and edge weights differ slightly between the two orders (ORDER_EFFECT) while labels and edge sets are identical.
7. E is not a second coordinate: slot = ⌊seed·N⌋ and E = d* + seed·(Ω − d*) use the same 64-bit seed, so E = d* + (slot + fraction)·(Ω − d*)/N. Largest |E − (d* + slot·(Ω − d*)/N)| over seated words: English {_dev:.3g}, Chinese {_devz:.3g} (one slot is {(0.56714-0.24600)/25000:.3g} wide in E). Two words sharing a slot therefore always have almost equal E.
8. Word segmentation of running Chinese with only the list as a dictionary matches list words inside unrelated text; the share of one-character Chinese tokens in the filtered corpus is in `experiment_v2/corpus_counts.tsv`."""))
open(os.path.join(WIKI, "11_baseline_mapping_zh_en.md"), "w", encoding="utf-8").write("\n".join(page))
# ── 1024.md ─────────────────────────────────────────────────────────────────────
def cell(name, lg, w):
    if w == "-": return ""
    r = MAP[name].get((lg, w)); return f"{ABBR.get(r['state'], r['state'])} {r['slot']}" if r else ""
doc = ["# 1024 — the word list (updated in place, not appended)", "",
       f"Each row: the English word (row header), its Chinese word, and what it maps to in each bin: state letter + slot. {LEG}. Rows 1–1024 are the matched list; rows after are deliberate FAULT rows. "
       "Source of truth `experiment_v2/list.tsv` (generated by `tools/exp_v2_list.py`); results `experiment_v2/results/`. Snapshot " + str(datetime.date.today()) + f", commit `{commit}`.", "",
       "| # | kind | English | Chinese | analog | en: test_english_v2 | zh: test_chinese_v2 | en: union | zh: union |", "|---:|---|---|---|---|---|---|---|---|"]
for r in L:
    doc.append(f"| {r['n']} | {r['kind'].replace('MATCHED','') or 'M'}{(' '+r['half']+r['pair']) if r['half'] else ''} | {r['en']} | {r['zh']} | {r['status']} | {cell('test_english_v2','en',r['en'])} | {cell('test_chinese_v2','zh',r['zh'])} | {cell('test_chinese_english_v2','en',r['en'])} | {cell('test_chinese_english_v2','zh',r['zh'])} |")
open(os.path.join(WIKI, "1024.md"), "w", encoding="utf-8").write("\n".join(doc) + "\n")
print("wrote", os.path.join(WIKI, "11_baseline_mapping_zh_en.md"), "and 1024.md")
