#!/usr/bin/env python3
"""calibration_build.py — the 1 024-concept calibration set: simple concepts and their layered analogues, each with a direct word in every test-bed language.

Candidates: English (word, POS) pairs that appear as an English gloss in the Wiktionary extract of EVERY language (corpora/derived/concept_index_<lang>.json) and have the
same POS in WordNet.  Evidence grade = the worst gloss rank across the five languages:  A primary gloss everywhere,  B within the first two,  C within the first four,
D any rank.  Only grade A meets the data criterion for "direct analogue" on its own; B-D are candidates awaiting review (column `review`).
Tiers: S (simple: concrete lexicographer class, <= 5 senses) and L (layered: abstract class or >= 8 senses; the middle goes by senses).  Pair: an L is paired with the S that
WordNet ties to it (S's word in L's definition, a derivationally related form, or a hypernym link).  Chinese headwords are converted to Traditional (OpenCC s2twp).
Writes calibration/calibration_1024.tsv and calibration/calibration_pool_all.tsv."""
import collections, csv, json, os, re, subprocess, sys
from nltk.corpus import wordnet as wn
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..")); D = os.path.join(ROOT, "corpora", "derived")
LANGS = ["Chinese", "Swahili", "Finnish", "Indonesian", "Quechua"]
CONC = {"noun.animal", "noun.plant", "noun.body", "noun.object", "noun.substance", "noun.food", "noun.artifact", "noun.location", "noun.phenomenon", "noun.person", "verb.motion",
        "verb.body", "verb.consumption", "verb.contact", "verb.weather", "adj.all", "adj.pert", "adv.all"}
CONTACT_BAD = {"English", "Chinese", "Mandarin", "Hokkien", "Min Nan", "Cantonese", "Hakka", "Swahili", "Finnish", "Indonesian", "Quechua"}   # a mention of another test-bed language
GRADE = lambda r: "A" if r == 0 else "B" if r <= 1 else "C" if r <= 3 else "D"


def varcon():
    us2uk = {}
    for line in open(os.path.join(ROOT, "corpora", "lexicon", "varcon.txt"), encoding="latin-1"):
        if line.startswith("#") or ":" not in line: continue
        us, uk = None, None
        for part in line.strip().split(" / "):
            tags, _, w = part.partition(":"); tg = tags.replace("v", "").split(); w = w.strip().lower()
            if "A" in tg and us is None and "v" not in tags.split()[0:1] : us = w
            if "B" in tg and uk is None: uk = w
        if us and uk and us != uk and " " not in us: us2uk[us] = uk
    return us2uk


def lex(lang):
    t = {}
    p = os.path.join(D, f"lex_{lang}.tsv")
    if not os.path.exists(p): return t
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"): t[r["key"]] = r
    return t


def trad(words):
    out = subprocess.run([os.path.join(HERE, "opencc_local.sh"), "s2twp"], input="\n".join(words), capture_output=True, text=True).stdout.split("\n")
    return out[:len(words)]


def main():
    ix = {l: json.load(open(os.path.join(D, f"concept_index_{l}.json"))) for l in ("Swahili", "Quechua")}
    om = json.load(open(os.path.join(D, "omw_candidates.json"))); freq = json.load(open(os.path.join(D, "word_freq.json")))
    lx = {l: lex(l) for l in LANGS}; v = varcon(); pool = []
    for k, o in om.items():
        w, p = k.split("|"); s = wn.synset(o["synset"]); pick, ranks, flags, fqs = {}, {}, {}, {}
        if not all(any(c[1] <= 9 for c in ix[l][k]) for l in ("Swahili", "Quechua")): continue        # a gloss rank above 9 is not evidence
        for l in ("Swahili", "Quechua"):
            fq = freq[l]
            cands = sorted([c for c in ix[l][k] if c[1] <= 9], key=lambda x: (fq.get(x[0], 0) < 3, x[1], 0 if (lx[l].get(x[0].casefold(), {}).get("etym") != "borrowed") else 1, -fq.get(x[0], 0), len(x[0]), x[0]))
            hw, r, ns = cands[0]; pick[l], ranks[l], fqs[l] = hw, r, fq.get(hw, 0)
        for l, cl in (("Finnish", o["fin"]), ("Indonesian", o["ind"])):
            fq = freq[l]; hw = sorted(cl, key=lambda x: (fq.get(x, 0) < 3, 0 if (lx[l].get(x.casefold(), {}).get("etym") != "borrowed") else 1, -fq.get(x, 0), len(x), x))[0]
            pick[l], ranks[l], fqs[l] = hw, 0, fq.get(hw, 0)
        fq = freq["Chinese"]; zhc = sorted(set(o["cmn_trad"]), key=lambda x: (fq.get(x, 0) < 3, -fq.get(x, 0), len(x), x))[0]
        pick["Chinese"], ranks["Chinese"], fqs["Chinese"] = zhc, 0, fq.get(zhc, 0)
        for l in LANGS:
            row = lx[l].get(pick[l].casefold(), {}); f = []
            if row.get("etym") == "borrowed": f.append("borrowed")
            m = {x for x in row.get("mentions", "").split(",") if x} & CONTACT_BAD
            if m: f.append("contact:" + "+".join(sorted(m)))
            flags[l] = f
        ss = wn.synsets(w, p)
        pool.append(dict(key=k, word=w, pos=p, pick=pick, ranks=ranks, flags=flags, fqs=fqs, worst=max(ranks["Swahili"], ranks["Quechua"]) if min(fqs.values()) >= 3 else 99,
                         lexname=s.lexname(), nsenses=len(ss), gloss=s.definition(), syn=s, synset=o["synset"], zh_trad=zhc, zh_changed=False))
    for x in pool:
        x["grade"] = GRADE(x["worst"]); x["clean"] = not any(x["flags"][l] for l in LANGS)
        x["abstract"] = x["lexname"] not in CONC
        x["layer_score"] = 3 * x["abstract"] + x["nsenses"] / 3       # layeredness: abstract lexicographer class, plus polysemy
    # 1. selection: the 1 024 best-evidenced candidates (grade, then cleanliness of etymology, then word)
    sel = sorted(pool, key=lambda x: (x["grade"], not x["clean"], x["word"]))[:1024]
    # 2. tiers: the lower half by layeredness is the simple set S, the upper half the layered set L
    for i, x in enumerate(sorted(sel, key=lambda x: (x["layer_score"], x["word"]))): x["tier"] = "S" if i < len(sel) // 2 else "L"
    # 3. pairs: an L is paired with the S that WordNet ties to it (derivationally related form, or a hypernym link); one-to-one, best-evidenced first
    S = [x for x in sel if x["tier"] == "S"]; pairs = []
    for Lx_ in [x for x in sel if x["tier"] == "L"]:
        best = None
        for s in S:
            sc = 2 if any(s["word"] == d.name().lower() for lem in Lx_["syn"].lemmas() for d in lem.derivationally_related_forms()) else (1 if (s["syn"] in Lx_["syn"].hypernyms() or Lx_["syn"] in s["syn"].hypernyms()) else 0)
            if sc and (best is None or (sc, -ord(s["grade"])) > best[0]): best = ((sc, -ord(s["grade"])), s)
        if best: pairs.append((best[0][0], Lx_, best[1]))
    used_s, used_l, pid = set(), set(), 0
    for sc, Lx_, s in sorted(pairs, key=lambda t: (-t[0], t[1]["grade"] + t[2]["grade"], t[1]["word"])):
        if Lx_["key"] in used_l or s["key"] in used_s: continue
        pid += 1; used_l.add(Lx_["key"]); used_s.add(s["key"]); Lx_["pair"] = s["pair"] = pid; Lx_["rel"] = s["rel"] = {2: "derivationally related", 1: "hypernym link"}[sc]
    sel = {x["key"]: x for x in sel}
    print("pool", len(pool), "selected", len(sel), "pairs", pid)
    cols = ["id", "tier", "pair", "pair_relation", "pos", "en_us", "en_uk", "zh_trad", "sw", "fi", "id_", "qu", "grade", "ranks_zh_sw_fi_id_qu", "freq_zh_sw_fi_id_qu", "flags", "lexname", "n_senses", "synset", "en_gloss", "review"]
    def row(i, x):
        uk = v.get(x["word"], x["word"]); fl = ";".join(f"{l[:2]}:{','.join(x['flags'][l])}" for l in LANGS if x["flags"][l])
        return [i, x.get("tier", ""), x.get("pair", ""), x.get("rel", ""), x["pos"], x["word"], uk, x["zh_trad"], x["pick"]["Swahili"], x["pick"]["Finnish"], x["pick"]["Indonesian"], x["pick"]["Quechua"], x["grade"],
                ",".join(str(x["ranks"][l]) for l in LANGS), ",".join(str(x["fqs"][l]) for l in LANGS), fl, x["lexname"], x["nsenses"], x["synset"], x["gloss"], "pending" if x["grade"] != "A" or fl else "data-verified"]
    for name, items in (("calibration_1024.tsv", sorted(sel.values(), key=lambda x: (x.get("pair") == "", x.get("pair") or 0, x["tier"] != "S", x["word"]))), ("calibration_pool_all.tsv", sorted(pool, key=lambda x: (x["grade"], x["word"])))):
        with open(os.path.join(ROOT, "calibration", name), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t"); w.writerow(cols)
            for i, x in enumerate(items, 1): w.writerow(row(f"C{i:04d}", x))
    sl = list(sel.values())
    print("selected", len(sl), dict(collections.Counter(x["tier"] for x in sl)), "grades", dict(collections.Counter(x["grade"] for x in sl)), "pairs", pid,
          "| clean+A:", sum(1 for x in sl if x["grade"] == "A" and x["clean"]), "| zh converted to Traditional:", sum(1 for x in sl if x["zh_changed"]))


if __name__ == "__main__":
    main()
