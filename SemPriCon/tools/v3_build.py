#!/usr/bin/env python3
"""v3_build.py — Fresh Start v3.0: the two UNS bins built from the v3.0 word list (calibration/calibration_v3_en_zh.tsv).

  test_english_v3.0.bin   the 1 024 English words addressed by M3 (English in Universal Native Space: golden-angle turns on the π/2 equator; tools/uns_mech.en_uns, the eb28ce8 float seed)
  test_chinese_v3.0.bin   the 1 024 Chinese characters addressed by M4 (Chinese in UNS: dictionary-order turn, key-component radius; tools/uns_mech.zh_uns)

Each single-language bin is: ground state → one learning pass over its half of the list (one word per line) → frozen, state version 6.  The learning step is the monad's own (monad_py.Monad.learn_ex):
β[slot] += E²·ALPHA_LEARN·|sin γ|·π/2 (capped at BETA_SAT), the slot's label is the highest-E arrival, word_count += 1.  Differences from the engine's ingest, all deliberate:
  * the address is the UNS mechanism, not monad_word_coords;
  * γ in the β update is the EXACT zero of the slot (SpecTools/zeros), for both languages (UNS: the 25 000 exact zeros are the marks on the equator);
  * the engine's token filter (hex strings, vowel ratio, length ...) is NOT applied: every word of the list is addressed.  What the filter would have rejected is counted and reported;
  * a list of single words has no sentences, so there are no A edges.
Also builds test_chinese_english_v3.0.bin (build_assigned).  Also writes data/v3_map.tsv (one row per list row, both languages) and data/v3_build_summary.json.

    .venv/bin/python tools/v3_build.py
"""
import csv, hashlib, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from dprint import dprint
import monad_py as mp, ptol_bin
from uns_mech import en_uns, zh_uns
from zh_half_line import Table, zeros
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LIST = os.path.join(ROOT, "calibration", "calibration_v3_en_zh.tsv")
N = mp.N_DEFAULT


def circ(a, b):
    d = abs(a - b) % 1.0
    return min(d, 1.0 - d)


def build_events(events, gamma, path):
    """ground state -> one learning pass over `events` = [(word, slot, E)] in order -> frozen state v6 at `path`.
    Learning step as monad_py.Monad.learn_ex: beta[slot] += E^2 * ALPHA_LEARN * |sin gamma| * pi/2 (capped), the label is the highest-E arrival (strict >: the first of equal E keeps it), word_count += 1."""
    beta = [abs(mp.L_GROUND) / N] * N
    vocab, count, per_slot, status = {}, 0, {}, {}
    for w, idx, E in events:
        amp = abs(math.sin(gamma[idx])) * (math.pi * 0.5)
        nb = beta[idx] + E * E * mp.ALPHA_LEARN * amp; beta[idx] = mp.BETA_SAT if nb > mp.BETA_SAT else nb
        v = vocab.get(idx)
        if v is None or E > v[2]: vocab[idx] = (idx, w, E, 1, 1, 1)
        count += 1; per_slot.setdefault(idx, []).append(w)
    for idx, ws in per_slot.items():
        for w in ws: status[w] = "S" if vocab[idx][1] == w else "O"            # seated / outranked by a higher E in the same slot
    ptol_bin.write_state(path, N, beta, [0] * N, vocab.values(), (), count, mp.EMIT_THRESH, 0.0, 6)
    os.chmod(path, 0o444)
    return per_slot, status


def build(rows, key, addr, gamma, path):
    return build_events([(r[key], addr(r[key])["slot"], addr(r[key])["E"]) for r in rows], gamma, path)


def build_assigned(rows, en, zh, gamma, path):
    """test_chinese_english_v3.0.bin: pass 1 the Chinese characters at their M4 addresses; pass 2 each English word ASSIGNED to the slot of its Chinese partner (same row of the list).
    The English word keeps its own M3 energy E (its own radius on the equator); only the slot (the azimuth, the idea) is taken from the Chinese."""
    ev = [(r["zh_trad"], zh[r["id"]]["slot"], zh[r["id"]]["E"]) for r in rows] + [(r["en_us"], zh[r["id"]]["slot"], en[r["id"]]["E"]) for r in rows]
    return build_events(ev, gamma, path)


def main():
    rows = list(csv.DictReader(open(LIST, encoding="utf-8"), delimiter="\t"))
    assert len(rows) == 1024 and all(len(r["zh_trad"]) == 1 for r in rows)
    Z = zeros(); gamma = [Z[k + 1] for k in range(N)]
    T = Table()
    en = {r["id"]: en_uns(r["en_us"]) for r in rows}; zh = {r["id"]: zh_uns(T, r["zh_trad"]) for r in rows}
    out = os.path.join(ROOT, "clean"); os.makedirs(out, exist_ok=True)
    pe = os.path.join(out, "test_english_v3.0.bin"); pz = os.path.join(out, "test_chinese_v3.0.bin")
    for p in (pe, pz):
        if os.path.exists(p): os.chmod(p, 0o644)
    ps_en, st_en = build(rows, "en_us", en_uns, gamma, pe)
    ps_zh, st_zh = build(rows, "zh_trad", lambda c: zh_uns(T, c), gamma, pz)
    pce = os.path.join(out, "test_chinese_english_v3.0.bin")
    if os.path.exists(pce): os.chmod(pce, 0o644)
    ps_ce, st_ce = build_assigned(rows, en, zh, gamma, pce)
    reject = {r["en_us"] for r in rows if not mp.token_accept(r["en_us"], mp.NS_FT_PROSE)}
    # the map, one row per list row
    cols = ["id", "half", "pair", "pos", "en", "zh", "en_slot", "en_gamma", "en_E", "en_turn", "en_r", "en_state", "en_filter_rejects", "zh_slot", "zh_gamma", "zh_E", "zh_turn", "zh_r", "zh_state", "turn_distance", "ce_zh_state", "ce_en_state"]
    with open(os.path.join(ROOT, "data", "v3_map.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t"); w.writerow(cols)
        for r in rows:
            a, b = en[r["id"]], zh[r["id"]]
            w.writerow([r["id"], r["half"], r["pair"], r["pos"], r["en_us"], r["zh_trad"], a["slot"], f"{gamma[a['slot']]:.9f}", f"{a['E']:.9f}", f"{a['turn']:.9f}", f"{a['r']:.6f}", st_en[r["en_us"]],
                        int(r["en_us"] in reject), b["slot"], f"{gamma[b['slot']]:.9f}", f"{b['E']:.9f}", f"{b['turn']:.9f}", f"{b['r']:.6f}", st_zh[r["zh_trad"]], f"{circ(a['turn'], b['turn']):.9f}", st_ce[r["zh_trad"]], st_ce[r["en_us"]]])
    # divergence survey
    pairs = {}
    for r in rows: pairs.setdefault(r["pair"], {})[r["half"]] = r
    def partner(d, lang):
        return [circ(d[p["S"]["id"]]["turn"], d[p["L"]["id"]]["turn"]) for p in pairs.values()]
    def med(x): x = sorted(x); return x[len(x) // 2]
    tdist = [circ(en[r["id"]]["turn"], zh[r["id"]]["turn"]) for r in rows]
    # baseline: the same statistic with the Chinese column shuffled (a fixed rotation by 509 rows), i.e. unrelated rows
    ids = [r["id"] for r in rows]
    shuf = [circ(en[ids[i]]["turn"], zh[ids[(i + 509) % 1024]]["turn"]) for i in range(1024)]
    shuf_en = [circ(en[p["S"]["id"]]["turn"], en[pairs[str((int(k) + 211) % 512 or 512)]["L"]["id"]]["turn"]) for k, p in pairs.items()]
    shuf_zh = [circ(zh[p["S"]["id"]]["turn"], zh[pairs[str((int(k) + 211) % 512 or 512)]["L"]["id"]]["turn"]) for k, p in pairs.items()]
    def stats(ps, words):
        sizes = sorted((len(v) for v in ps.values()), reverse=True)
        return dict(occupied_slots=len(ps), max_words_in_a_slot=sizes[0], slots_with_more_than_one=sum(1 for s in sizes if s > 1),
                    outranked_words=sum(1 for v in ps.values() for _ in v) - len(ps), slot_0_words=len(ps.get(0, [])))
    summ = dict(list_sha256=hashlib.sha256(open(LIST, "rb").read()).hexdigest(),
                english=dict(stats(ps_en, None), words_of_8_or_more_letters=sum(len(r["en_us"]) >= 8 for r in rows), filter_would_reject=len(reject), rejected_words=sorted(reject)),
                chinese=stats(ps_zh, None),
                bins={os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (pe, pz, pce)},
                chinese_english=dict(stats(ps_ce, None), english_labels=sum(1 for r in rows if st_ce[r["en_us"]] == "S"), chinese_labels=sum(1 for r in rows if st_ce[r["zh_trad"]] == "S"),
                                     slots_where_english_outranks=sum(1 for r in rows if st_ce[r["zh_trad"]] == "O"), vocab_size=len(ps_ce)),
                english_vs_chinese_same_row_turn_distance=dict(median=med(tdist), mean=sum(tdist) / 1024, shuffled_median=med(shuf), uniform_expected_mean=0.25, within_0_01=sum(d < .01 for d in tdist), shuffled_within_0_01=sum(d < .01 for d in shuf)),
                same_slot=sum(en[i]["slot"] == zh[i]["slot"] for i in ids),
                SL_partner_turn_distance=dict(english_median=med(partner(en, "en")), english_shuffled_median=med(shuf_en), chinese_median=med(partner(zh, "zh")), chinese_shuffled_median=med(shuf_zh),
                                              english_within_0_01=sum(d < .01 for d in partner(en, "en")), chinese_within_0_01=sum(d < .01 for d in partner(zh, "zh")),
                                              english_shuffled_within_0_01=sum(d < .01 for d in shuf_en), chinese_shuffled_within_0_01=sum(d < .01 for d in shuf_zh)),
                r_range=dict(english=[min(a["r"] for a in en.values()), max(a["r"] for a in en.values())], chinese=[min(a["r"] for a in zh.values()), max(a["r"] for a in zh.values())]))
    json.dump(summ, open(os.path.join(ROOT, "data", "v3_build_summary.json"), "w"), ensure_ascii=False, indent=1)
    # manifest
    with open(os.path.join(out, "MANIFEST.tsv"), "w") as f:
        f.write("# clean/ — Fresh Start v3.0 (2026-10-21)\n# Two single-language Universal Native Space bins, read-only, built by tools/v3_build.py from calibration/calibration_v3_en_zh.tsv (sha256 below).\n"
                "# Each is: ground state -> one learning pass over its half of the 1 024-row list -> frozen.  State format v6.  v2.0 is archived in dirty/v2.0/ (bins) and clean/archive/v2.0/.\n"
                "file\tsha256\taddress\tword list\n")
        f.write(f"test_english_v3.0.bin\t{summ['bins']['test_english_v3.0.bin']}\tM3: English in UNS (tools/uns_mech.en_uns; eb28ce8 float seed, golden-angle turns on the pi/2 equator)\tcalibration_v3_en_zh.tsv {summ['list_sha256'][:16]} (en_us column)\n")
        f.write(f"test_chinese_english_v3.0.bin\t{summ['bins']['test_chinese_english_v3.0.bin']}\tpass 1: M4 Chinese characters; pass 2: each English word ASSIGNED to the slot of its Chinese partner (the English word keeps its own M3 energy)\tcalibration_v3_en_zh.tsv {summ['list_sha256'][:16]} (zh_trad then en_us)\n")
        f.write(f"test_chinese_v3.0.bin\t{summ['bins']['test_chinese_v3.0.bin']}\tM4: Chinese in UNS (tools/uns_mech.zh_uns; dictionary-order turn, key-component radius, exact zeros)\tcalibration_v3_en_zh.tsv {summ['list_sha256'][:16]} (zh_trad column)\n")
    print(json.dumps({k: summ[k] for k in summ if k != "english"}, ensure_ascii=False, indent=1)); print(json.dumps({k: v for k, v in summ["english"].items() if k != "rejected_words"}, indent=1))


if __name__ == "__main__":
    main()
