#!/usr/bin/env python3
"""assess_bin.py — measure what a PTOL state file contains.  Read-only.

Same verdict machinery as VAPMIP/tools/eval_checkpoint.py (classify, field_entropy, gini_coefficient are imported, not copied),
plus the 2026-10-17 token sanitiser (Wernicke/sanitize/sanitize_v0.sanitize_token) so the numbers sit beside the POISON notes,
plus a script (Unicode block) census, which the older assessments never had.

    python3 assess_bin.py <file.bin> <out.json>
"""
import collections, hashlib, importlib.util, json, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
VAP = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import ptol_bin

def _imp(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

ev = _imp("eval_checkpoint", os.path.join(VAP, "tools", "eval_checkpoint.py"))
sys.path.insert(0, os.path.join(VAP, "Wernicke", "sanitize"))
import sanitize_v0 as sv


def script_of(ch):
    if ch.isascii():
        return "ASCII"
    try:
        n = unicodedata.name(ch)
    except ValueError:
        return "UNNAMED"
    return n.split(" ")[0]          # LATIN, GREEK, CYRILLIC, ARABIC, CJK, HANGUL, HIRAGANA, DEVANAGARI ...


def main(path, out):
    d = ptol_bin.load(path)
    vocab = d["vocab"]
    words = [v[1] for v in vocab]
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()

    # script census: a word's script = its set of non-ASCII scripts (or ASCII)
    word_scripts = collections.Counter(); script_chars = collections.Counter(); nonascii_words = []
    for w in words:
        sc = {script_of(c) for c in w if not c.isascii()}
        if sc:
            word_scripts["+".join(sorted(sc))] += 1; nonascii_words.append(w)
        else:
            word_scripts["ASCII"] += 1
        for c in w:
            if not c.isascii():
                script_chars[script_of(c)] += 1

    # eval_checkpoint classifier
    poll = collections.Counter(); polluted = 0
    for w in words:
        lab = ev.classify(w)
        if lab: polluted += 1
        for l in lab: poll[l] += 1

    # sanitiser tiers
    tiers = collections.Counter(); samples = collections.defaultdict(list)
    for w in words:
        t, why, _ = sv.sanitize_token(w)
        tiers[f"{t}:{why}"] += 1
        if len(samples[f"{t}:{why}"]) < 12: samples[f"{t}:{why}"].append(w)

    beta = d["beta"]; N = d["N"]
    occ = [float(b) for b in beta if b > 0]
    H = ev.field_entropy(beta, N); Hmax = __import__("math").log2(max(1, len([b for b in beta if b > 0])))
    gini = ev.gini_coefficient(beta)

    byidx = {v[0]: v for v in vocab}
    probe = {}
    for w in ["holcus", "philadelphos", "same", "stuff", "seemy", "what", "is", "your", "name", "tree", "water",
              "setn", "abysmal", "quun", "nanti", "emite", "ptolemy"]:
        hit = [v for v in vocab if v[1] == w]
        probe[w] = [dict(idx=v[0], E=round(v[2], 4), beta=round(float(beta[v[0]]), 3), age=int(d["age"][v[0]]),
                         home=v[3], gen=v[4], prose_seen=v[5]) for v in hit] or None

    ed = d["edges"]; order = ed["w"].argsort()[::-1][:25]
    top_edges = [dict(a=byidx[int(ed["i"][k])][1] if int(ed["i"][k]) in byidx else None,
                      b=byidx[int(ed["j"][k])][1] if int(ed["j"][k]) in byidx else None,
                      w=round(float(ed["w"][k]), 3)) for k in order]
    top_beta = sorted(vocab, key=lambda v: -beta[v[0]])[:25]

    rep = dict(file=os.path.basename(path), sha256=sha, size_bytes=d["bytes_total"], bytes_consumed=d["bytes_consumed"],
               header=dict(version=d["version"], N=N, vocab_size=d["vocab_size"], A_size=d["A_size"], word_count=d["word_count"],
                           threshold=d["threshold"], affect=d["affect"]),
               field=dict(occupied_zeros=len(occ), entropy=round(H, 4), entropy_max=round(Hmax, 4),
                          entropy_pct=round(100 * H / Hmax, 2), gini=round(gini, 4),
                          beta_saturated=int(sum(1 for b in occ if b >= 7.55)), beta_max=max(occ)),
               strata=dict(home=dict(collections.Counter(v[3] for v in vocab)), gen=dict(collections.Counter(v[4] for v in vocab)),
                           prose_seen=dict(collections.Counter(v[5] for v in vocab))),
               scripts=dict(word_scripts=dict(word_scripts.most_common()), nonascii_chars=dict(script_chars.most_common()),
                            nonascii_word_count=len(nonascii_words), nonascii_samples=nonascii_words[:60]),
               eval_checkpoint=dict(polluted=polluted, clean=len(words) - polluted,
                                    pollution_pct=round(100 * polluted / len(words), 2), by_category=dict(poll.most_common())),
               sanitiser=dict(tiers=dict(sorted(tiers.items(), key=lambda kv: -kv[1])), samples=dict(samples),
                              quarantined=sum(n for k, n in tiers.items() if k.startswith("Q:")),
                              quarantined_pct=round(100 * sum(n for k, n in tiers.items() if k.startswith("Q:")) / len(words), 2)),
               probes=probe, top_beta=[dict(word=v[1], idx=v[0], E=round(v[2], 4), beta=round(float(beta[v[0]]), 3)) for v in top_beta],
               top_edges=top_edges)
    json.dump(rep, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: rep[k] for k in ("header", "field", "eval_checkpoint")}, indent=1)[:2500])
    print("scripts:", dict(list(word_scripts.most_common(12))))
    print("sanitiser:", dict(list(rep["sanitiser"]["tiers"].items())[:14]), "Q%", rep["sanitiser"]["quarantined_pct"])
    print("probes:", json.dumps(probe)[:1500])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
